from __future__ import annotations

from typing import Any

import numpy as np


class DepthQualityError(RuntimeError):
    pass


def analyze_depth_quality(
    depth_frame: Any,
    *,
    roi: list[int] | None = None,
    background_roi: list[int] | None = None,
    min_valid_depth_mm: float = 50.0,
    max_valid_depth_mm: float = 6000.0,
    depth_scale: float = 1.0,
    noise_check: bool = True,
) -> dict[str, Any]:
    depth_mm = _normalize_depth_frame(depth_frame, depth_scale)
    height, width = depth_mm.shape
    target_roi = _clip_roi(roi or [0, 0, width, height], width, height, "roi")
    roi_stats = _region_stats(
        depth_mm,
        target_roi,
        min_valid_depth_mm,
        max_valid_depth_mm,
    )

    background_stats = None
    if background_roi:
        background_stats = _region_stats(
            depth_mm,
            _clip_roi(background_roi, width, height, "background_roi"),
            min_valid_depth_mm,
            max_valid_depth_mm,
        )

    flags = _quality_flags(roi_stats, background_stats, noise_check=noise_check)
    return {
        "status": "review" if flags else "ok",
        "roi": roi_stats,
        "background": background_stats,
        "quality_flags": flags,
        "recommendation_codes": _recommendation_codes(flags),
    }


def _normalize_depth_frame(depth_frame: Any, depth_scale: float) -> np.ndarray:
    if depth_scale <= 0:
        raise DepthQualityError("depth_scale must be positive.")
    depth = np.asarray(depth_frame, dtype=np.float32)
    if depth.ndim != 2:
        raise DepthQualityError("depth_frame must be a 2D array.")
    return depth * float(depth_scale)


def _clip_roi(roi: list[int], width: int, height: int, field_name: str) -> list[int]:
    if len(roi) != 4:
        raise DepthQualityError(f"{field_name} must contain [x1, y1, x2, y2].")
    x1, y1, x2, y2 = [int(round(value)) for value in roi]
    x1 = max(0, min(width, x1))
    x2 = max(0, min(width, x2))
    y1 = max(0, min(height, y1))
    y2 = max(0, min(height, y2))
    if x2 <= x1 or y2 <= y1:
        raise DepthQualityError(f"{field_name} must have positive width and height.")
    return [x1, y1, x2, y2]


def _region_stats(
    depth_mm: np.ndarray,
    roi: list[int],
    min_valid_depth_mm: float,
    max_valid_depth_mm: float,
) -> dict[str, Any]:
    x1, y1, x2, y2 = roi
    values = depth_mm[y1:y2, x1:x2].reshape(-1)
    pixel_count = int(values.size)
    valid = values[
        np.isfinite(values)
        & (values >= min_valid_depth_mm)
        & (values <= max_valid_depth_mm)
    ]
    valid_count = int(valid.size)
    valid_ratio = valid_count / max(1, pixel_count)
    stats: dict[str, Any] = {
        "roi": roi,
        "pixel_count": pixel_count,
        "valid_pixel_count": valid_count,
        "valid_pixel_ratio": round(float(valid_ratio), 3),
        "missing_pixel_ratio": round(float(1.0 - valid_ratio), 3),
        "median_depth_mm": None,
        "depth_std_mm": None,
        "iqr_mm": None,
    }
    if valid_count == 0:
        return stats

    q1 = float(np.quantile(valid, 0.25))
    q3 = float(np.quantile(valid, 0.75))
    stats.update(
        {
            "median_depth_mm": round(float(np.median(valid)), 1),
            "depth_std_mm": round(float(np.std(valid)), 1),
            "iqr_mm": round(q3 - q1, 1),
        }
    )
    return stats


def _quality_flags(
    roi_stats: dict[str, Any],
    background_stats: dict[str, Any] | None,
    *,
    noise_check: bool,
) -> list[str]:
    flags: list[str] = []
    valid_ratio = float(roi_stats["valid_pixel_ratio"])
    missing_ratio = float(roi_stats["missing_pixel_ratio"])
    if valid_ratio <= 0:
        flags.append("no_valid_depth_roi")
    elif valid_ratio < 0.55:
        flags.append("sparse_depth_frame")
    if missing_ratio > 0.2:
        flags.append("depth_hole_risk")

    depth_std = roi_stats["depth_std_mm"]
    iqr = roi_stats["iqr_mm"]
    if noise_check and depth_std is not None and iqr is not None:
        if float(depth_std) > 80.0 or float(iqr) > 120.0:
            flags.append("noisy_depth_roi")

    if background_stats:
        background_std = background_stats["depth_std_mm"]
        if background_std is not None and float(background_std) > 35.0:
            flags.append("unstable_table_depth")

    return sorted(set(flags))


def _recommendation_codes(flags: list[str]) -> list[str]:
    recommendations: list[str] = []
    if any(flag in flags for flag in ["sparse_depth_frame", "depth_hole_risk", "no_valid_depth_roi"]):
        recommendations.append("retake_depth_with_less_reflection")
    if "noisy_depth_roi" in flags:
        recommendations.append("stabilize_depth_camera_and_retake")
    if "unstable_table_depth" in flags:
        recommendations.append("select_clean_background_roi")
    return sorted(set(recommendations))
