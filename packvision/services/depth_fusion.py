from __future__ import annotations

from typing import Any


DIMENSION_KEYS = ("length_mm", "width_mm", "height_mm")
SIDE_VIEW_ROLES = {"side", "left", "right"}


class DepthFusionError(RuntimeError):
    pass


def fuse_depth_measurements(
    view_measurements: list[dict[str, Any]],
    *,
    strategy: str = "conservative_max",
    disagreement_ratio: float = 0.12,
) -> dict[str, Any]:
    normalized_strategy = str(strategy or "conservative_max").strip().lower()
    if normalized_strategy not in {"conservative_max", "confidence_weighted"}:
        raise DepthFusionError("strategy must be conservative_max or confidence_weighted.")
    if not view_measurements:
        raise DepthFusionError("view_measurements must include at least one view result.")
    if disagreement_ratio <= 0:
        raise DepthFusionError("disagreement_ratio must be positive.")

    views = [_normalize_view(item, index) for index, item in enumerate(view_measurements)]
    usable_views = [view for view in views if view["usable"]]
    if not usable_views:
        raise DepthFusionError("No usable measured views were provided.")

    dimension_values = {
        key: [view["dimensions"][key] for view in usable_views if view["dimensions"].get(key) is not None]
        for key in DIMENSION_KEYS
    }
    fused_dimensions: dict[str, float | None] = {}
    disagreements: dict[str, dict[str, float]] = {}
    for key, values in dimension_values.items():
        if not values:
            fused_dimensions[key] = None
            continue
        if normalized_strategy == "confidence_weighted":
            fused_dimensions[key] = _weighted_dimension(key, usable_views)
        else:
            fused_dimensions[key] = max(values)
        spread = max(values) - min(values)
        baseline = max(max(values), 1.0)
        ratio = spread / baseline
        if len(values) >= 2 and ratio > disagreement_ratio:
            disagreements[key] = {
                "min_mm": round(min(values), 1),
                "max_mm": round(max(values), 1),
                "spread_ratio": round(ratio, 3),
            }

    length = fused_dimensions.get("length_mm")
    width = fused_dimensions.get("width_mm")
    height = fused_dimensions.get("height_mm")
    volume_l = None
    if length is not None and width is not None and height is not None:
        volume_l = length * width * height / 1_000_000

    roles = [view["role"] for view in usable_views]
    flags = _unique_flags(usable_views)
    flags.append("multi_view_fusion" if len(usable_views) >= 2 else "single_view_fallback")
    if _has_three_view_roles(roles):
        flags.append("three_view_ready")
    if disagreements:
        flags.append("view_disagreement_risk")
    if normalized_strategy == "conservative_max":
        flags.append("conservative_dimension_max_used")

    confidence = _fused_confidence(usable_views, disagreements)
    status = "measured" if not disagreements and all(fused_dimensions.get(key) is not None for key in DIMENSION_KEYS) else "review"
    recommendation_codes = _recommendations(usable_views, disagreements, roles)

    return {
        "status": status,
        "confidence": confidence,
        "dimensions": {
            "length_mm": _round_optional(length),
            "width_mm": _round_optional(width),
            "height_mm": _round_optional(height),
            "volume_l": round(float(volume_l), 3) if volume_l is not None else None,
        },
        "views": usable_views,
        "ignored_views": [view for view in views if not view["usable"]],
        "fusion": {
            "strategy": normalized_strategy,
            "view_count": len(usable_views),
            "roles": roles,
            "disagreement_ratio": float(disagreement_ratio),
            "disagreements": disagreements,
            "dimension_sources": _dimension_sources(usable_views),
        },
        "quality_flags": sorted(set(flags)),
        "recommendation_codes": recommendation_codes,
        "method": {
            "name": "multi_view_depth_measurement_fusion",
            "notes": [
                "The same contract works for one Astra Pro, two cross-check cameras, or a future three-view rig.",
                "Conservative max fusion avoids under-reporting shipping size for irregular automotive parts.",
                "When views disagree beyond tolerance, keep the result reviewable instead of auto-accepting it.",
            ],
        },
    }


def _normalize_view(item: dict[str, Any], index: int) -> dict[str, Any]:
    if not isinstance(item, dict):
        return {"view_id": f"view-{index + 1}", "role": "unknown", "usable": False, "reason": "not_an_object"}
    dimensions = item.get("dimensions") if isinstance(item.get("dimensions"), dict) else {}
    normalized_dimensions = {
        key: _optional_float(dimensions.get(key))
        for key in DIMENSION_KEYS
    }
    usable = item.get("status", "measured") in {"measured", "review"} and any(
        value is not None for value in normalized_dimensions.values()
    )
    return {
        "view_id": str(item.get("view_id") or item.get("camera_id") or f"view-{index + 1}"),
        "camera_id": item.get("camera_id"),
        "role": str(item.get("role") or item.get("camera_role") or _role_from_index(index)).strip().lower(),
        "status": item.get("status"),
        "usable": usable,
        "confidence": _bounded_confidence(item.get("confidence")),
        "dimensions": normalized_dimensions,
        "quality_flags": list(item.get("quality_flags") or []),
        "recommendation_codes": list(item.get("recommendation_codes") or []),
        "measurement_id": item.get("measurement_id"),
    }


def _weighted_dimension(key: str, views: list[dict[str, Any]]) -> float | None:
    weighted_sum = 0.0
    weight_sum = 0.0
    for view in views:
        value = view["dimensions"].get(key)
        if value is None:
            continue
        weight = max(0.05, float(view["confidence"]))
        weighted_sum += value * weight
        weight_sum += weight
    return weighted_sum / weight_sum if weight_sum else None


def _fused_confidence(views: list[dict[str, Any]], disagreements: dict[str, Any]) -> float:
    base = sum(float(view["confidence"]) for view in views) / len(views)
    view_bonus = min(0.12, 0.04 * max(0, len(views) - 1))
    disagreement_penalty = min(0.3, 0.08 * len(disagreements))
    return round(max(0.2, min(0.96, base + view_bonus - disagreement_penalty)), 2)


def _dimension_sources(views: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    sources: dict[str, list[dict[str, Any]]] = {}
    for key in DIMENSION_KEYS:
        sources[key] = [
            {
                "view_id": view["view_id"],
                "role": view["role"],
                "value_mm": _round_optional(view["dimensions"].get(key)),
                "confidence": view["confidence"],
            }
            for view in views
            if view["dimensions"].get(key) is not None
        ]
    return sources


def _unique_flags(views: list[dict[str, Any]]) -> list[str]:
    flags: list[str] = []
    for view in views:
        flags.extend(str(flag) for flag in view.get("quality_flags") or [])
    return flags


def _recommendations(views: list[dict[str, Any]], disagreements: dict[str, Any], roles: list[str]) -> list[str]:
    recommendations: list[str] = []
    for view in views:
        recommendations.extend(str(code) for code in view.get("recommendation_codes") or [])
    if disagreements:
        recommendations.append("review_multi_view_disagreement")
    if len(views) == 1:
        recommendations.append("add_side_or_front_camera_for_cross_check")
    elif not _has_three_view_roles(roles):
        recommendations.append("complete_three_view_camera_layout")
    return sorted(set(recommendations))


def _has_three_view_roles(roles: list[str]) -> bool:
    role_set = set(roles)
    return {"top", "front"}.issubset(role_set) and bool(role_set & SIDE_VIEW_ROLES)


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number < 0:
        return None
    return number


def _bounded_confidence(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0.6
    return max(0.05, min(0.99, number))


def _round_optional(value: float | None) -> float | None:
    return round(float(value), 1) if value is not None else None


def _role_from_index(index: int) -> str:
    roles = ("top", "front", "left", "right", "aux")
    return roles[index] if index < len(roles) else "aux"
