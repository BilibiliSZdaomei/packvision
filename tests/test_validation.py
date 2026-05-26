import csv
import io

import pytest

from packvision.services.validation import (
    build_trial_plan,
    build_trial_template_csv,
    evaluate_trial_csv,
    evaluate_trial_run,
)


def test_trial_plan_covers_auto_parts_package_scenarios():
    plan = build_trial_plan()
    scenario_ids = {scenario["id"] for scenario in plan["scenarios"]}

    assert {"standard_carton", "long_part", "irregular_or_soft_pack"}.issubset(scenario_ids)
    assert {"reflective", "transparent", "dark_absorbing", "deformable"}.issubset(
        set(plan["abnormal_materials"])
    )
    assert plan["minimum_total_samples"] >= 28


def test_evaluate_trial_run_accepts_within_tolerance_standard_carton():
    result = evaluate_trial_run(
        [
            {
                "sample_id": "STD-001",
                "package_class": "standard_carton",
                "measured": {"length_mm": 402, "width_mm": 299, "height_mm": 201},
                "truth": {"length_mm": 400, "width_mm": 300, "height_mm": 200},
            }
        ]
    )

    assert result["samples"][0]["status"] == "pass"
    assert result["samples"][0]["max_abs_error_mm"] == pytest.approx(2.0)
    assert result["summary"]["failed_samples"] == 0


def test_evaluate_trial_run_rejects_transparent_material_large_error():
    result = evaluate_trial_run(
        [
            {
                "sample_id": "MAT-001",
                "package_class": "standard_carton",
                "material_class": "transparent",
                "measured": {"length_mm": 450, "width_mm": 300, "height_mm": 170},
                "truth": {"length_mm": 400, "width_mm": 300, "height_mm": 200},
            }
        ]
    )

    sample = result["samples"][0]
    assert sample["status"] == "fail"
    assert "manual_review_required" in sample["flags"]
    assert result["summary"]["ready_for_site_rollout"] is False


def test_trial_template_csv_contains_truth_and_measured_columns():
    csv_text = build_trial_template_csv()
    rows = list(csv.DictReader(io.StringIO(csv_text.lstrip("\ufeff"))))

    assert csv_text.startswith("\ufeff")
    assert rows
    assert "measured_length_mm" in rows[0]
    assert "truth_length_mm" in rows[0]
    assert any(row["package_class"] == "long_part" for row in rows)
    assert any(row["material_class"] == "reflective" for row in rows)


def test_evaluate_trial_csv_parses_wps_ready_rows_with_order_traceability():
    csv_text = """sample_id,order_id,package_class,material_class,measured_length_mm,measured_width_mm,measured_height_mm,truth_length_mm,truth_width_mm,truth_height_mm
STD-CSV-001,SO-20260527-001,standard_carton,,402,299,201,400,300,200
"""

    result = evaluate_trial_csv(csv_text)

    assert result["samples"][0]["sample_id"] == "STD-CSV-001"
    assert result["samples"][0]["order_id"] == "SO-20260527-001"
    assert result["samples"][0]["status"] == "pass"
