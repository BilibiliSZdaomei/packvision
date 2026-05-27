from __future__ import annotations

from typing import Any


LONG_PART_THRESHOLD_MM = 1200.0
STANDARD_RATIO_LIMIT = 4.0
VOLUMETRIC_DIVISOR_L_PER_KG = 6.0


def infer_material_hint_from_capture_quality(
    capture_quality: dict[str, Any] | None,
    quality_flags: list[str] | None = None,
) -> dict[str, Any]:
    flags = set(quality_flags or [])
    metrics: list[dict[str, Any]] = []
    for quality in _capture_quality_views(capture_quality):
        flags.update(quality.get("quality_flags") or [])
        if isinstance(quality.get("metrics"), dict):
            metrics.append(quality["metrics"])

    max_overexposed = max((_number(item.get("overexposed_ratio")) or 0 for item in metrics), default=0)
    max_underexposed = max((_number(item.get("underexposed_ratio")) or 0 for item in metrics), default=0)
    min_contrast = min((_number(item.get("contrast_std")) or 999 for item in metrics), default=999)

    if "low_contrast_capture" in flags and (
        "package_contour_not_found" in flags or (min_contrast <= 6 and max_overexposed < 0.25 and max_underexposed < 0.25)
    ):
        return _material_signal(
            "transparent",
            0.56,
            ["low_contrast_capture", "possible_clear_or_lens_surface"],
        )
    if "lighting_overexposed" in flags or max_overexposed >= 0.12:
        return _material_signal(
            "reflective",
            0.58,
            ["lighting_overexposed", "possible_glare_or_metal_surface"],
        )
    if "lighting_underexposed" in flags or max_underexposed >= 0.35:
        return _material_signal(
            "dark_absorbing",
            0.54,
            ["lighting_underexposed", "possible_dark_absorbing_surface"],
        )

    return {
        "material_hint": None,
        "source": None,
        "confidence": 0.0,
        "reason_codes": [],
    }


def build_packaging_profile(
    dimensions: dict[str, Any],
    *,
    part_category: str | None = None,
    package_hint: str | None = None,
    material_hint: str | None = None,
    actual_weight_kg: float | None = None,
) -> dict[str, Any]:
    length = _number(dimensions.get("length_mm"))
    width = _number(dimensions.get("width_mm"))
    height = _number(dimensions.get("height_mm"))
    volume_l = _number(dimensions.get("volume_l"))
    hint = (package_hint or "").strip().lower()
    category = (part_category or "").strip().lower() or None
    material = _material_class(material_hint)
    material_risk = _material_risk(material)

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
    handling_flags.extend(material_risk["flags"])

    package_class = _classify_package(hint, length, width, height, side_ratio)
    capture_mode = _recommended_capture_mode(package_class)

    if package_class == "standard_carton" and not handling_flags:
        handling_flags.append("warehouse_ready")
    if package_class in {"bulky_irregular", "irregular_or_soft_pack"}:
        handling_flags.append("manual_review_recommended")
    if material_risk["risk_level"] in {"medium", "high"}:
        handling_flags.append("manual_review_recommended")

    volumetric_weight_kg = _volumetric_weight(volume_l, length, width, height)
    chargeable_weight = _chargeable_weight(actual_weight_kg, volumetric_weight_kg)

    return {
        "package_class": package_class,
        "recommended_capture_mode": capture_mode,
        "part_category": category,
        "package_hint": hint or None,
        "material_hint": (material_hint or "").strip().lower() or None,
        "material_class": material,
        "material_risk_level": material_risk["risk_level"],
        "material_capture_adjustments": material_risk["capture_adjustments"],
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
        "workflow": _workflow_for(package_class, material),
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


def _workflow_for(package_class: str, material_class: str | None = None) -> list[str]:
    if package_class == "standard_carton":
        workflow = ["scan_order", "capture_top_or_depth", "confirm_box_edges", "save_history"]
    elif package_class == "long_part":
        workflow = ["scan_order", "place_diagonal_or_long_axis_visible", "depth_roi", "check_oversize_rule", "save_history"]
    elif package_class == "irregular_or_soft_pack":
        workflow = ["scan_order", "depth_object_mask", "manual_adjust_if_needed", "save_history"]
    else:
        workflow = ["scan_order", "depth_object_mask", "manual_review", "save_history"]

    if material_class in {"reflective", "transparent", "dark_absorbing", "deformable"}:
        insert_at = max(1, len(workflow) - 1)
        workflow[insert_at:insert_at] = ["material_surface_check", "retake_or_manual_verify"]
    return workflow


def _material_class(material_hint: str | None) -> str | None:
    material = (material_hint or "").strip().lower()
    if not material:
        return None
    if material in {"normal", "matte", "cardboard", "paper", "carton"}:
        return "normal"
    if material in {"reflective", "glossy", "metal", "metallic", "chrome", "mirror", "foil"}:
        return "reflective"
    if material in {"transparent", "clear", "glass", "acrylic", "lens"}:
        return "transparent"
    if material in {"black", "dark", "matte_black", "rubber", "absorbing", "dark_absorbing"}:
        return "dark_absorbing"
    if material in {"deformable", "soft", "foam", "fabric", "bag", "film"}:
        return "deformable"
    return material


def _material_risk(material_class: str | None) -> dict[str, Any]:
    risks = {
        "reflective": {
            "risk_level": "high",
            "flags": ["reflective_depth_noise_risk"],
            "capture_adjustments": ["change_angle", "reduce_glare", "manual_spot_check"],
        },
        "transparent": {
            "risk_level": "high",
            "flags": ["transparent_depth_dropout_risk"],
            "capture_adjustments": ["use_matte_background", "add_visible_outer_bag", "manual_spot_check"],
        },
        "dark_absorbing": {
            "risk_level": "medium",
            "flags": ["dark_surface_depth_dropout_risk"],
            "capture_adjustments": ["increase_lighting", "shorten_distance", "manual_spot_check"],
        },
        "deformable": {
            "risk_level": "medium",
            "flags": ["deformable_shape_drift_risk"],
            "capture_adjustments": ["avoid_compression", "capture_largest_outline", "manual_spot_check"],
        },
    }
    return risks.get(
        material_class or "",
        {
            "risk_level": "low" if material_class else None,
            "flags": [],
            "capture_adjustments": [],
        },
    )


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


def _capture_quality_views(capture_quality: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(capture_quality, dict):
        return []
    if "metrics" in capture_quality or "quality_flags" in capture_quality:
        return [capture_quality]
    return [
        view
        for key in ("top", "side")
        if isinstance((view := capture_quality.get(key)), dict)
    ]


def _material_signal(material_hint: str, confidence: float, reason_codes: list[str]) -> dict[str, Any]:
    return {
        "material_hint": material_hint,
        "source": "capture_quality",
        "confidence": round(confidence, 2),
        "reason_codes": reason_codes,
    }


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
