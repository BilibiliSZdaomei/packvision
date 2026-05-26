from __future__ import annotations

from typing import Any


LONG_PART_THRESHOLD_MM = 1200.0
STANDARD_RATIO_LIMIT = 4.0
VOLUMETRIC_DIVISOR_L_PER_KG = 6.0


def build_packaging_profile(
    dimensions: dict[str, Any],
    *,
    part_category: str | None = None,
    package_hint: str | None = None,
    actual_weight_kg: float | None = None,
) -> dict[str, Any]:
    length = _number(dimensions.get("length_mm"))
    width = _number(dimensions.get("width_mm"))
    height = _number(dimensions.get("height_mm"))
    volume_l = _number(dimensions.get("volume_l"))
    hint = (package_hint or "").strip().lower()
    category = (part_category or "").strip().lower() or None

    sides = [value for value in [length, width, height] if value and value > 0]
    longest = max(sides) if sides else None
    shortest = min(sides) if sides else None
    side_ratio = (longest / shortest) if longest and shortest else None

    handling_flags: list[str] = []
    if not height:
        handling_flags.append("needs_depth_or_manual_height")
    if longest and longest >= LONG_PART_THRESHOLD_MM:
        handling_flags.append("oversize_length")
    if category in {"bumper", "bumper_trim", "fender", "grille", "exhaust", "molding"}:
        handling_flags.append("fragile_or_shape_sensitive")

    package_class = _classify_package(hint, length, width, height, side_ratio)
    capture_mode = _recommended_capture_mode(package_class)

    if package_class == "standard_carton" and not handling_flags:
        handling_flags.append("warehouse_ready")
    if package_class in {"bulky_irregular", "irregular_or_soft_pack"}:
        handling_flags.append("manual_review_recommended")

    volumetric_weight_kg = _volumetric_weight(volume_l, length, width, height)
    chargeable_weight = _chargeable_weight(actual_weight_kg, volumetric_weight_kg)

    return {
        "package_class": package_class,
        "recommended_capture_mode": capture_mode,
        "part_category": category,
        "package_hint": hint or None,
        "dimensions": {
            "length_mm": length,
            "width_mm": width,
            "height_mm": height,
            "volume_l": volume_l,
            "side_ratio": round(side_ratio, 3) if side_ratio else None,
        },
        "actual_weight_kg": _round(actual_weight_kg, 3),
        "volumetric_weight_kg": _round(volumetric_weight_kg, 3),
        "chargeable_weight_kg": _round(chargeable_weight, 3),
        "handling_flags": sorted(set(handling_flags)),
        "workflow": _workflow_for(package_class),
    }


def _classify_package(
    hint: str,
    length: float | None,
    width: float | None,
    height: float | None,
    side_ratio: float | None,
) -> str:
    if hint in {"long", "long_part", "tube", "shock_absorber"}:
        return "long_part"
    if hint in {"irregular", "soft", "soft_pack", "bag", "wrapped"} and not height:
        return "irregular_or_soft_pack"
    if length and length >= LONG_PART_THRESHOLD_MM:
        return "long_part"
    if not height:
        return "irregular_or_soft_pack"
    if hint in {"irregular", "soft", "soft_pack", "bag"}:
        return "irregular_or_soft_pack"
    if side_ratio and side_ratio > STANDARD_RATIO_LIMIT:
        return "bulky_irregular"
    return "standard_carton"


def _recommended_capture_mode(package_class: str) -> str:
    return {
        "standard_carton": "top_plus_side_or_depth_roi",
        "long_part": "depth_roi_long_item",
        "irregular_or_soft_pack": "depth_object_mask",
        "bulky_irregular": "depth_object_mask",
    }.get(package_class, "manual_review")


def _workflow_for(package_class: str) -> list[str]:
    if package_class == "standard_carton":
        return ["scan_order", "capture_top_or_depth", "confirm_box_edges", "save_history"]
    if package_class == "long_part":
        return ["scan_order", "place_diagonal_or_long_axis_visible", "depth_roi", "check_oversize_rule", "save_history"]
    if package_class == "irregular_or_soft_pack":
        return ["scan_order", "depth_object_mask", "manual_adjust_if_needed", "save_history"]
    return ["scan_order", "depth_object_mask", "manual_review", "save_history"]


def _volumetric_weight(
    volume_l: float | None,
    length: float | None,
    width: float | None,
    height: float | None,
) -> float | None:
    if volume_l is None and length and width and height:
        volume_l = length * width * height / 1_000_000
    if volume_l is None:
        return None
    return volume_l / VOLUMETRIC_DIVISOR_L_PER_KG


def _chargeable_weight(actual_weight_kg: float | None, volumetric_weight_kg: float | None) -> float | None:
    values = [value for value in [_number(actual_weight_kg), volumetric_weight_kg] if value is not None]
    return max(values) if values else None


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
