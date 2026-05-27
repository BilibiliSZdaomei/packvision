from __future__ import annotations

import csv
import io
import json
import sqlite3
from typing import Any

from packvision.services.history import db_path, init_db


DIMENSION_KEYS = ("length_mm", "width_mm", "height_mm")
LOW_CONFIDENCE_THRESHOLD = 0.65

REVIEW_FLAG_KEYWORDS = (
    "review",
    "risk",
    "hole",
    "sparse",
    "noisy",
    "unstable",
    "missing",
    "manual",
    "overexposed",
    "underexposed",
    "low_contrast",
    "blurry",
    "disagreement",
)

REVIEW_RECOMMENDATION_KEYWORDS = (
    "review",
    "retake",
    "manual",
    "validate",
    "stabilize",
    "reflection",
    "background",
    "reposition",
)

CSV_COLUMNS = (
    "measurement_id",
    "created_at",
    "order_id",
    "status",
    "priority",
    "confidence",
    "package_class",
    "material_class",
    "material_risk_level",
    "length_mm",
    "width_mm",
    "height_mm",
    "review_reasons",
    "suggested_action",
)


def list_review_samples(limit: int = 50, order_id: str | None = None) -> dict[str, Any]:
    limit = max(1, min(int(limit or 50), 500))
    candidates = _load_recent_measurement_results(scan_limit=max(limit * 8, 200), order_id=order_id)
    items: list[dict[str, Any]] = []
    for result in candidates:
        sample = build_review_sample(result)
        if sample:
            items.append(sample)
        if len(items) >= limit:
            break
    return {"items": items, "summary": _summary(items)}


def export_review_samples_csv(limit: int = 500, order_id: str | None = None) -> str:
    rows = list_review_samples(limit=limit, order_id=order_id)["items"]
    output = io.StringIO()
    output.write("\ufeff")
    writer = csv.DictWriter(output, fieldnames=CSV_COLUMNS, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    for row in rows:
        flattened = dict(row)
        dimensions = row.get("dimensions") or {}
        flattened.update({key: dimensions.get(key) for key in DIMENSION_KEYS})
        flattened["review_reasons"] = "|".join(row.get("review_reasons") or [])
        writer.writerow({column: flattened.get(column) for column in CSV_COLUMNS})
    return output.getvalue()


def build_review_sample(result: dict[str, Any]) -> dict[str, Any] | None:
    status = str(result.get("status") or "").strip().lower()
    confidence = _number(result.get("confidence")) or 0.0
    industry = result.get("industry_profile") if isinstance(result.get("industry_profile"), dict) else {}
    reasons = _review_reasons(result, industry, status, confidence)
    if not reasons:
        return None

    dimensions = result.get("dimensions") if isinstance(result.get("dimensions"), dict) else {}
    artifacts = result.get("artifacts") if isinstance(result.get("artifacts"), dict) else {}
    top_view = result.get("top_view") if isinstance(result.get("top_view"), dict) else {}
    side_view = result.get("side_view") if isinstance(result.get("side_view"), dict) else {}
    package_class = industry.get("package_class")
    material_class = industry.get("material_class")
    material_risk_level = industry.get("material_risk_level")
    return {
        "measurement_id": result.get("measurement_id"),
        "created_at": result.get("created_at"),
        "order_id": result.get("order_id"),
        "barcode_text": result.get("barcode_text"),
        "status": status or None,
        "priority": _priority(reasons, status, material_risk_level),
        "confidence": round(confidence, 3),
        "measurement_source": result.get("measurement_source"),
        "package_class": package_class,
        "material_class": material_class,
        "material_risk_level": material_risk_level,
        "dimensions": {key: dimensions.get(key) for key in DIMENSION_KEYS},
        "review_reasons": reasons,
        "quality_flags": _string_list(result.get("quality_flags")),
        "recommendation_codes": _string_list(result.get("recommendation_codes")),
        "handling_flags": _string_list(industry.get("handling_flags")),
        "artifact_urls": {
            key: value
            for key, value in {
                "top": top_view.get("annotated_image_url")
                or artifacts.get("top_result_url")
                or artifacts.get("top_upload"),
                "side": side_view.get("annotated_image_url")
                or artifacts.get("side_result_url")
                or artifacts.get("side_upload"),
                "depth_overlay": artifacts.get("simulation_overlay_url"),
                "depth_preview": artifacts.get("depth_preview_url"),
            }.items()
            if value
        },
        "suggested_action": _suggested_action(reasons, material_risk_level),
    }


def _review_reasons(
    result: dict[str, Any],
    industry: dict[str, Any],
    status: str,
    confidence: float,
) -> list[str]:
    reasons: list[str] = []
    if status and status != "measured":
        reasons.append(f"status_{status}")
    if confidence < LOW_CONFIDENCE_THRESHOLD:
        reasons.append("low_confidence")

    for flag in _string_list(result.get("quality_flags")) + _string_list(industry.get("handling_flags")):
        if _matches_any(flag, REVIEW_FLAG_KEYWORDS):
            reasons.append(flag)

    for code in _string_list(result.get("recommendation_codes")):
        if _matches_any(code, REVIEW_RECOMMENDATION_KEYWORDS):
            reasons.append(code)

    material_risk_level = str(industry.get("material_risk_level") or "").strip().lower()
    if material_risk_level in {"medium", "high"}:
        reasons.append(f"material_{material_risk_level}_risk")

    return sorted(set(reasons))


def _priority(reasons: list[str], status: str, material_risk_level: Any) -> str:
    reason_text = " ".join(reasons)
    if status in {"fail", "failed", "error"} or "disagreement" in reason_text:
        return "critical"
    if str(material_risk_level or "").lower() == "high" or "depth_hole_risk" in reasons:
        return "high"
    if "low_confidence" in reasons or any("retake" in reason for reason in reasons):
        return "high"
    return "medium"


def _suggested_action(reasons: list[str], material_risk_level: Any) -> str:
    reason_set = set(reasons)
    if any("disagreement" in reason for reason in reason_set):
        return "compare_views_and_measure_truth"
    if "depth_hole_risk" in reason_set or str(material_risk_level or "").lower() == "high":
        return "retake_with_angle_lighting_change_and_manual_truth"
    if any("manual" in reason for reason in reason_set):
        return "check_annotation_boundary_and_save_truth"
    if "low_confidence" in reason_set:
        return "spot_check_with_tape_or_depth_camera"
    return "review_before_accepting_measurement"


def _summary(items: list[dict[str, Any]]) -> dict[str, Any]:
    by_priority: dict[str, int] = {}
    by_reason: dict[str, int] = {}
    for item in items:
        priority = str(item.get("priority") or "medium")
        by_priority[priority] = by_priority.get(priority, 0) + 1
        for reason in item.get("review_reasons") or []:
            by_reason[reason] = by_reason.get(reason, 0) + 1
    return {
        "total_review_samples": len(items),
        "by_priority": by_priority,
        "top_reasons": [
            {"reason": reason, "count": count}
            for reason, count in sorted(by_reason.items(), key=lambda item: (-item[1], item[0]))[:10]
        ],
    }


def _load_recent_measurement_results(scan_limit: int, order_id: str | None) -> list[dict[str, Any]]:
    init_db()
    query = "SELECT result_json FROM measurements"
    params: list[Any] = []
    if order_id:
        query += " WHERE order_id LIKE ?"
        params.append(f"%{order_id}%")
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(max(1, min(scan_limit, 2000)))
    with sqlite3.connect(db_path()) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(query, params).fetchall()
    results: list[dict[str, Any]] = []
    for row in rows:
        try:
            parsed = json.loads(row["result_json"])
        except (TypeError, json.JSONDecodeError):
            continue
        if isinstance(parsed, dict):
            results.append(parsed)
    return results


def _matches_any(value: str, keywords: tuple[str, ...]) -> bool:
    normalized = value.lower()
    return any(keyword in normalized for keyword in keywords)


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _number(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number >= 0 else None
