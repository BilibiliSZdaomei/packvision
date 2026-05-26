from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class DepthIntrinsics:
    fx: float
    fy: float
    cx: float
    cy: float
    width: int
    height: int
    depth_scale: float = 1.0


@dataclass(frozen=True)
class DepthMeasurementConfig:
    roi: list[int]
    background_roi: list[int] | None = None
    table_depth_mm: float | None = None
    min_valid_depth_mm: float = 50.0
    max_valid_depth_mm: float = 6000.0
    trim_ratio: float = 0.08


class DepthMeasurementError(RuntimeError):
    pass


def measure_depth_roi(
    depth_frame: Any,
    intrinsics: DepthIntrinsics,
    config: DepthMeasurementConfig,
) -> dict[str, Any]:
    depth_mm = _normalize_depth_frame(depth_frame, intrinsics.depth_scale)
    roi = _clip_roi(config.roi, intrinsics.width, intrinsics.height, "roi")
    object_values = _valid_depth_values(
        depth_mm,
        roi,
        config.min_valid_depth_mm,
        config.max_valid_depth_mm,
    )
    if object_values.size == 0:
        raise DepthMeasurementError("No valid depth pixels inside ROI.")

    object_depth_mm = _robust_depth(object_values, config.trim_ratio)
    x1, y1, x2, y2 = roi
    object_width_mm = (x2 - x1) * object_depth_mm / intrinsics.fx
    object_length_mm = (y2 - y1) * object_depth_mm / intrinsics.fy

    table_depth_mm = config.table_depth_mm
    if table_depth_mm is None and config.background_roi:
        background_roi = _clip_roi(
            config.background_roi,
            intrinsics.width,
            intrinsics.height,
            "background_roi",
        )
        background_values = _valid_depth_values(
            depth_mm,
            background_roi,
            config.min_valid_depth_mm,
            config.max_valid_depth_mm,
        )
        if background_values.size:
            table_depth_mm = _robust_depth(background_values, config.trim_ratio)

    height_mm = None
    flags = ["depth_camera_measurement", "depth_roi_used"]
    if table_depth_mm is None:
        flags.append("background_depth_missing")
    else:
        height_mm = max(0.0, table_depth_mm - object_depth_mm)
        flags.append("background_depth_used")

    valid_ratio = object_values.size / max(1, (x2 - x1) * (y2 - y1))
    if valid_ratio < 0.55:
        flags.append("sparse_depth_roi")
    if config.trim_ratio:
        flags.append("depth_outliers_trimmed")

    length_mm = max(object_width_mm, object_length_mm)
    width_mm = min(object_width_mm, object_length_mm)
    volume_l = None
    if height_mm is not None:
        volume_l = length_mm * width_mm * height_mm / 1_000_000

    confidence = 0.76 if height_mm is not None else 0.58
    confidence *= min(1.0, max(0.35, valid_ratio))

    return {
        "status": "measured",
        "confidence": round(float(confidence), 2),
        "dimensions": {
            "length_mm": round(float(length_mm), 1),
            "width_mm": round(float(width_mm), 1),
            "height_mm": round(float(height_mm), 1) if height_mm is not None else None,
            "volume_l": round(float(volume_l), 3) if volume_l is not None else None,
        },
        "depth": {
            "object_depth_mm": round(float(object_depth_mm), 1),
            "table_depth_mm": round(float(table_depth_mm), 1) if table_depth_mm is not None else None,
            "valid_pixel_ratio": round(float(valid_ratio), 3),
            "roi": roi,
            "background_roi": config.background_roi,
            "intrinsics": {
                "fx": intrinsics.fx,
                "fy": intrinsics.fy,
                "cx": intrinsics.cx,
                "cy": intrinsics.cy,
                "width": intrinsics.width,
                "height": intrinsics.height,
                "depth_scale": intrinsics.depth_scale,
            },
        },
        "quality_flags": sorted(set(flags)),
        "method": {
            "name": "depth_camera_roi_projection",
            "notes": [
                "ROI pixels are projected with camera intrinsics and median depth.",
                "Height is table/background depth minus object top depth.",
                "This path is hardware-ready and can run with synthetic depth frames before the camera arrives.",
            ],
        },
    }


def _normalize_depth_frame(depth_frame: Any, depth_scale: float) -> np.ndarray:
    depth = np.asarray(depth_frame, dtype=np.float32)
    if depth.ndim != 2:
        raise DepthMeasurementError("depth_frame must be a 2D array.")
    if depth_scale <= 0:
        raise DepthMeasurementError("depth_scale must be positive.")
    return depth * float(depth_scale)


def _clip_roi(roi: list[int], width: int, height: int, field_name: str) -> list[int]:
    if len(roi) != 4:
        raise DepthMeasurementError(f"{field_name} must contain [x1, y1, x2, y2].")
    x1, y1, x2, y2 = [int(round(value)) for value in roi]
    x1 = max(0, min(width, x1))
    x2 = max(0, min(width, x2))
    y1 = max(0, min(height, y1))
    y2 = max(0, min(height, y2))
    if x2 <= x1 or y2 <= y1:
        raise DepthMeasurementError(f"{field_name} must have positive width and height.")
    return [x1, y1, x2, y2]


def _valid_depth_values(
    depth_mm: np.ndarray,
    roi: list[int],
    min_valid_depth_mm: float,
    max_valid_depth_mm: float,
) -> np.ndarray:
    x1, y1, x2, y2 = roi
    values = depth_mm[y1:y2, x1:x2].reshape(-1)
    return values[
        np.isfinite(values)
        & (values >= min_valid_depth_mm)
        & (values <= max_valid_depth_mm)
    ]


def _robust_depth(values: np.ndarray, trim_ratio: float) -> float:
    if values.size == 0:
        raise DepthMeasurementError("No valid depth values.")
    if trim_ratio <= 0:
        return float(np.median(values))
    lower = float(np.quantile(values, min(0.45, trim_ratio)))
    upper = float(np.quantile(values, max(0.55, 1.0 - trim_ratio)))
    trimmed = values[(values >= lower) & (values <= upper)]
    if trimmed.size == 0:
        trimmed = values
    return float(np.median(trimmed))
