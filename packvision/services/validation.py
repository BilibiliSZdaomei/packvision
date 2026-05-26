from __future__ import annotations

import csv
import io
from typing import Any


DIMENSION_KEYS = ("length_mm", "width_mm", "height_mm")

SCENARIO_RULES = {
    "standard_carton": {
        "label": "Standard carton",
        "minimum_samples": 5,
        "abs_tolerance_mm": 8.0,
        "relative_tolerance_pct": 3.0,
        "required_capture_mode": "top_plus_side_or_depth_roi",
    },
    "long_part": {
        "label": "Long part",
        "minimum_samples": 5,
        "abs_tolerance_mm": 12.0,
        "relative_tolerance_pct": 2.5,
        "required_capture_mode": "depth_roi_long_item",
    },
    "irregular_or_soft_pack": {
        "label": "Irregular or soft pack",
        "minimum_samples": 10,
        "abs_tolerance_mm": 18.0,
        "relative_tolerance_pct": 6.0,
        "required_capture_mode": "depth_object_mask",
    },
    "bulky_irregular": {
        "label": "Bulky irregular",
        "minimum_samples": 4,
        "abs_tolerance_mm": 20.0,
        "relative_tolerance_pct": 6.0,
        "required_capture_mode": "depth_object_mask",
    },
}

ABNORMAL_MATERIAL_RULES = {
    "reflective": {
        "minimum_samples": 2,
        "risk_level": "high",
        "flags": ["reflective_depth_noise_risk", "manual_review_required"],
    },
    "transparent": {
        "minimum_samples": 2,
        "risk_level": "high",
        "flags": ["transparent_depth_dropout_risk", "manual_review_required"],
    },
    "dark_absorbing": {
        "minimum_samples": 2,
        "risk_level": "medium",
        "flags": ["dark_surface_depth_dropout_risk", "manual_review_required"],
    },
    "deformable": {
        "minimum_samples": 2,
        "risk_level": "medium",
        "flags": ["deformable_shape_drift_risk", "manual_review_required"],
    },
}

TRIAL_TEMPLATE_COLUMNS = (
    "sample_id",
    "order_id",
    "package_class",
    "material_class",
    "measured_length_mm",
    "measured_width_mm",
    "measured_height_mm",
    "truth_length_mm",
    "truth_width_mm",
    "truth_height_mm",
    "actual_weight_kg",
    "notes",
)

_SCENARIO_SAMPLE_PREFIXES = {
    "standard_carton": "STD",
    "long_part": "LONG",
    "irregular_or_soft_pack": "IRR",
    "bulky_irregular": "BULK",
}

_MATERIAL_SAMPLE_PREFIXES = {
    "reflective": "REF",
    "transparent": "TRA",
    "dark_absorbing": "DARK",
    "deformable": "DEF",
}


def build_trial_plan() -> dict[str, Any]:
    scenarios = [
        {
            "id": scenario_id,
            **rule,
            "acceptance": _acceptance_text(rule),
        }
        for scenario_id, rule in SCENARIO_RULES.items()
    ]
    material_total = sum(rule["minimum_samples"] for rule in ABNORMAL_MATERIAL_RULES.values())
    return {
        "minimum_total_samples": sum(rule["minimum_samples"] for rule in SCENARIO_RULES.values()) + material_total,
        "scenarios": scenarios,
        "abnormal_materials": list(ABNORMAL_MATERIAL_RULES.keys()),
        "material_scenarios": [
            {"id": material, **rule}
            for material, rule in ABNORMAL_MATERIAL_RULES.items()
        ],
        "site_steps": [
            "install_driver_and_confirm_vendor_viewer",
            "run_capture_probe",
            "measure_truth_with_tape_or_caliper",
            "capture_packvision_measurement",
            "evaluate_trial_run",
            "export_history_csv",
        ],
    }


def evaluate_trial_run(samples: list[dict[str, Any]]) -> dict[str, Any]:
    evaluated = [_evaluate_sample(sample) for sample in samples]
    failed = [sample for sample in evaluated if sample["status"] == "fail"]
    review = [sample for sample in evaluated if "manual_review_required" in sample["flags"]]
    scenario_counts = _count_by(evaluated, "package_class")
    material_counts = _count_by(evaluated, "material_class")
    sample_count_gaps = _sample_count_gaps(scenario_counts, material_counts)
    return {
        "samples": evaluated,
        "summary": {
            "total_samples": len(evaluated),
            "passed_samples": len(evaluated) - len(failed),
            "failed_samples": len(failed),
            "manual_review_samples": len(review),
            "sample_count_gaps": sample_count_gaps,
            "ready_for_site_rollout": not failed and not sample_count_gaps,
        },
    }


def build_trial_template_csv() -> str:
    output = io.StringIO()
    output.write("\ufeff")
    writer = csv.DictWriter(output, fieldnames=TRIAL_TEMPLATE_COLUMNS, lineterminator="\n")
    writer.writeheader()

    for scenario_id, rule in SCENARIO_RULES.items():
        prefix = _SCENARIO_SAMPLE_PREFIXES.get(scenario_id, scenario_id.upper())
        for index in range(1, int(rule["minimum_samples"]) + 1):
            writer.writerow(
                {
                    "sample_id": f"{prefix}-{index:03d}",
                    "package_class": scenario_id,
                }
            )

    for material_id, rule in ABNORMAL_MATERIAL_RULES.items():
        prefix = _MATERIAL_SAMPLE_PREFIXES.get(material_id, material_id.upper())
        for index in range(1, int(rule["minimum_samples"]) + 1):
            writer.writerow(
                {
                    "sample_id": f"MAT-{prefix}-{index:03d}",
                    "package_class": "standard_carton",
                    "material_class": material_id,
                }
            )

    return output.getvalue()


def evaluate_trial_csv(csv_text: str) -> dict[str, Any]:
    reader = csv.DictReader(io.StringIO(csv_text.lstrip("\ufeff")))
    samples = [_sample_from_csv_row(row) for row in reader if _row_has_content(row)]
    result = evaluate_trial_run(samples)
    result["source"] = "csv"
    result["parsed_rows"] = len(samples)
    return result


def _evaluate_sample(sample: dict[str, Any]) -> dict[str, Any]:
    package_class = str(sample.get("package_class") or "standard_carton")
    material_class = _clean_optional(sample.get("material_class"))
    rule = SCENARIO_RULES.get(package_class, SCENARIO_RULES["irregular_or_soft_pack"])
    material_rule = ABNORMAL_MATERIAL_RULES.get(material_class or "")
    measured = sample.get("measured") or {}
    truth = sample.get("truth") or {}
    dimension_errors = _dimension_errors(measured, truth)
    max_abs_error = max((item["abs_error_mm"] for item in dimension_errors.values()), default=None)
    max_relative_error = max((item["relative_error_pct"] for item in dimension_errors.values()), default=None)
    flags: list[str] = []
    if material_rule:
        flags.extend(material_rule["flags"])
    if not dimension_errors:
        flags.append("truth_dimensions_missing")

    within_abs = max_abs_error is not None and max_abs_error <= rule["abs_tolerance_mm"]
    within_relative = max_relative_error is not None and max_relative_error <= rule["relative_tolerance_pct"]
    passed = within_abs or within_relative
    if not passed:
        flags.append("dimension_error_exceeds_tolerance")

    return {
        "sample_id": sample.get("sample_id"),
        "order_id": sample.get("order_id"),
        "package_class": package_class,
        "material_class": material_class,
        "actual_weight_kg": _round(_number(sample.get("actual_weight_kg")), 3),
        "status": "pass" if passed else "fail",
        "max_abs_error_mm": _round(max_abs_error, 3),
        "max_relative_error_pct": _round(max_relative_error, 3),
        "dimension_errors": dimension_errors,
        "tolerance": {
            "abs_tolerance_mm": rule["abs_tolerance_mm"],
            "relative_tolerance_pct": rule["relative_tolerance_pct"],
        },
        "flags": sorted(set(flags)),
        "notes": sample.get("notes"),
    }


def _sample_from_csv_row(row: dict[str | None, Any]) -> dict[str, Any]:
    return {
        "sample_id": _row_text(row, "sample_id"),
        "order_id": _row_text(row, "order_id"),
        "package_class": _row_text(row, "package_class") or "standard_carton",
        "material_class": _row_text(row, "material_class"),
        "actual_weight_kg": _number(_row_text(row, "actual_weight_kg")),
        "measured": _dimension_map_from_row(row, "measured"),
        "truth": _dimension_map_from_row(row, "truth"),
        "notes": _row_text(row, "notes"),
    }


def _dimension_map_from_row(row: dict[str | None, Any], prefix: str) -> dict[str, float]:
    dimensions: dict[str, float] = {}
    for key in DIMENSION_KEYS:
        value = _number(_row_text(row, f"{prefix}_{key}"))
        if value is not None:
            dimensions[key] = value
    return dimensions


def _row_has_content(row: dict[str | None, Any]) -> bool:
    return any(str(value).strip() for key, value in row.items() if key is not None and value is not None)


def _row_text(row: dict[str | None, Any], key: str) -> str | None:
    value = row.get(key)
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _dimension_errors(measured: dict[str, Any], truth: dict[str, Any]) -> dict[str, dict[str, float]]:
    errors: dict[str, dict[str, float]] = {}
    for key in DIMENSION_KEYS:
        measured_value = _number(measured.get(key))
        truth_value = _number(truth.get(key))
        if measured_value is None or truth_value is None:
            continue
        abs_error = abs(measured_value - truth_value)
        errors[key] = {
            "measured_mm": measured_value,
            "truth_mm": truth_value,
            "abs_error_mm": _round(abs_error, 3),
            "relative_error_pct": _round(abs_error / truth_value * 100, 3),
        }
    return errors


def _sample_count_gaps(scenario_counts: dict[str, int], material_counts: dict[str, int]) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    for scenario_id, rule in SCENARIO_RULES.items():
        current = scenario_counts.get(scenario_id, 0)
        if current < rule["minimum_samples"]:
            gaps.append({"id": scenario_id, "current": current, "required": rule["minimum_samples"]})
    for material_id, rule in ABNORMAL_MATERIAL_RULES.items():
        current = material_counts.get(material_id, 0)
        if current < rule["minimum_samples"]:
            gaps.append({"id": material_id, "current": current, "required": rule["minimum_samples"]})
    return gaps


def _count_by(samples: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for sample in samples:
        value = sample.get(key)
        if not value:
            continue
        counts[str(value)] = counts.get(str(value), 0) + 1
    return counts


def _acceptance_text(rule: dict[str, Any]) -> str:
    return f"<= {rule['abs_tolerance_mm']} mm or <= {rule['relative_tolerance_pct']}% max dimension error"


def _clean_optional(value: Any) -> str | None:
    text = str(value or "").strip().lower()
    return text or None


def _number(value: Any) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def _round(value: float | None, digits: int) -> float | None:
    return round(float(value), digits) if value is not None else None
