from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Any

import numpy as np

from packvision.services.depth_quality import DepthQualityError, analyze_depth_quality


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


@dataclass(frozen=True)
class DepthObjectConfig:
    roi: list[int]
    background_roi: list[int] | None = None
    table_depth_mm: float | None = None
    min_valid_depth_mm: float = 50.0
    max_valid_depth_mm: float = 6000.0
    object_min_height_mm: float = 30.0
    trim_quantile: float = 0.02
    footprint_method: str = "axis_aligned"


@dataclass(frozen=True)
class DepthEvidenceBundle:
    metadata: dict[str, Any]
    point_cloud_npz: bytes
    depth_preview_png: bytes


class DepthMeasurementError(RuntimeError):
    pass


def measure_depth_roi(
    depth_frame: Any,
    intrinsics: DepthIntrinsics,
    config: DepthMeasurementConfig,
) -> dict[str, Any]:
    depth_mm = _normalize_depth_frame(depth_frame, intrinsics.depth_scale)
    roi = _clip_roi(config.roi, intrinsics.width, intrinsics.height, "roi")
    quality = _analyze_depth_quality(
        depth_mm,
        roi=roi,
        background_roi=config.background_roi,
        min_valid_depth_mm=config.min_valid_depth_mm,
        max_valid_depth_mm=config.max_valid_depth_mm,
    )
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
    flags.extend(quality["quality_flags"])

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
        "depth_quality": quality,
        "quality_flags": sorted(set(flags)),
        "recommendation_codes": _depth_recommendations(
            quality["recommendation_codes"],
            flags,
        ),
        "method": {
            "name": "depth_camera_roi_projection",
            "notes": [
                "ROI pixels are projected with camera intrinsics and median depth.",
                "Height is table/background depth minus object top depth.",
                "This path is hardware-ready and can run with synthetic depth frames before the camera arrives.",
            ],
        },
    }


def measure_depth_object_mask(
    depth_frame: Any,
    intrinsics: DepthIntrinsics,
    config: DepthObjectConfig,
) -> dict[str, Any]:
    depth_mm = _normalize_depth_frame(depth_frame, intrinsics.depth_scale)
    roi = _clip_roi(config.roi, intrinsics.width, intrinsics.height, "roi")
    footprint_method = _normalize_footprint_method(config.footprint_method)
    quality = _analyze_depth_quality(
        depth_mm,
        roi=roi,
        background_roi=config.background_roi,
        min_valid_depth_mm=config.min_valid_depth_mm,
        max_valid_depth_mm=config.max_valid_depth_mm,
        noise_check=False,
    )
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
            table_depth_mm = _robust_depth(background_values, 0.08)

    if table_depth_mm is None:
        raise DepthMeasurementError("table_depth_mm or background_roi is required for object mask measurement.")

    x1, y1, x2, y2 = roi
    roi_depth = depth_mm[y1:y2, x1:x2]
    valid_mask = (
        np.isfinite(roi_depth)
        & (roi_depth >= config.min_valid_depth_mm)
        & (roi_depth <= config.max_valid_depth_mm)
    )
    object_mask = valid_mask & (roi_depth <= (table_depth_mm - config.object_min_height_mm))
    ys, xs = np.nonzero(object_mask)
    if xs.size == 0:
        raise DepthMeasurementError("No object pixels found above the table depth.")

    image_x = xs.astype(np.float32) + x1
    image_y = ys.astype(np.float32) + y1
    z = roi_depth[ys, xs].astype(np.float32)
    world_x = (image_x - float(intrinsics.cx)) * z / float(intrinsics.fx)
    world_y = (image_y - float(intrinsics.cy)) * z / float(intrinsics.fy)

    x_extent, y_extent, orientation_deg = _footprint_extents(
        world_x,
        world_y,
        footprint_method,
        config.trim_quantile,
    )
    height_mm = max(0.0, float(table_depth_mm) - _robust_depth(z, 0.08))
    length_mm = max(x_extent, y_extent)
    width_mm = min(x_extent, y_extent)
    volume_l = length_mm * width_mm * height_mm / 1_000_000

    object_pixel_count = int(xs.size)
    roi_pixel_count = max(1, (x2 - x1) * (y2 - y1))
    object_ratio = object_pixel_count / roi_pixel_count
    flags = ["depth_camera_measurement", "depth_object_mask_used", "background_depth_used"]
    if footprint_method == "principal_axes":
        flags.append("principal_axis_extent_used")
    else:
        flags.append("axis_aligned_extent_used")
    if object_ratio < 0.08:
        flags.append("small_object_mask")
    if config.trim_quantile:
        flags.append("point_cloud_extent_trimmed")
    flags.extend(quality["quality_flags"])

    confidence = 0.82 * min(1.0, max(0.35, object_ratio * 4.0))

    return {
        "status": "measured",
        "confidence": round(float(confidence), 2),
        "dimensions": {
            "length_mm": round(float(length_mm), 1),
            "width_mm": round(float(width_mm), 1),
            "height_mm": round(float(height_mm), 1),
            "volume_l": round(float(volume_l), 3),
        },
        "depth": {
            "table_depth_mm": round(float(table_depth_mm), 1),
            "object_depth_mm": round(float(np.median(z)), 1),
            "object_pixel_count": object_pixel_count,
            "object_pixel_ratio": round(float(object_ratio), 3),
            "roi": roi,
            "background_roi": config.background_roi,
            "footprint_method": footprint_method,
            "orientation_deg": round(float(orientation_deg), 1) if orientation_deg is not None else None,
            "x_extent_mm": round(float(x_extent), 1),
            "y_extent_mm": round(float(y_extent), 1),
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
        "depth_quality": quality,
        "quality_flags": sorted(set(flags)),
        "recommendation_codes": _depth_recommendations(
            quality["recommendation_codes"],
            flags,
        ),
        "method": {
            "name": "depth_object_mask_projection",
            "notes": [
                "Object pixels are separated by table depth and projected with camera intrinsics.",
                "Footprint uses the point-cloud extent instead of the full rectangular ROI.",
                "This is the preferred path for soft, wrapped, or irregular automotive spare parts.",
            ],
        },
    }


def detect_depth_object_region(
    depth_frame: Any,
    intrinsics: DepthIntrinsics,
    *,
    min_valid_depth_mm: float = 50.0,
    max_valid_depth_mm: float = 6000.0,
    object_min_height_mm: float = 30.0,
    padding_px: int | None = None,
) -> dict[str, Any]:
    depth_mm = _normalize_depth_frame(depth_frame, intrinsics.depth_scale)
    height, width = depth_mm.shape
    valid_mask = (
        np.isfinite(depth_mm)
        & (depth_mm >= min_valid_depth_mm)
        & (depth_mm <= max_valid_depth_mm)
    )
    valid_values = depth_mm[valid_mask]
    if valid_values.size < max(8, int(width * height * 0.03)):
        return _center_region(width, height, "auto_center_default", reason="too_few_valid_depth_pixels")

    border_values = depth_mm[_border_mask(width, height) & valid_mask]
    background_values = border_values if border_values.size >= max(8, int(valid_values.size * 0.05)) else valid_values
    table_depth_mm = float(np.quantile(background_values, 0.82))
    threshold = table_depth_mm - max(1.0, float(object_min_height_mm))
    object_mask = valid_mask & (depth_mm <= threshold)
    component = _largest_component(object_mask)
    if component is None:
        region = _center_region(width, height, "auto_center_default", reason="no_depth_foreground_component")
        region["table_depth_mm"] = round(float(table_depth_mm), 1)
        return region

    component_mask, component_area = component
    if component_area < max(6, int(width * height * 0.01)):
        region = _center_region(width, height, "auto_center_default", reason="depth_foreground_too_small")
        region["table_depth_mm"] = round(float(table_depth_mm), 1)
        region["foreground_pixel_count"] = int(component_area)
        return region

    ys, xs = np.nonzero(component_mask)
    pad = padding_px if padding_px is not None else max(1, int(round(min(width, height) * 0.035)))
    roi = [
        max(0, int(xs.min()) - pad),
        max(0, int(ys.min()) - pad),
        min(width, int(xs.max()) + pad + 1),
        min(height, int(ys.max()) + pad + 1),
    ]
    return {
        "roi": roi,
        "background_roi": _background_corner_roi(depth_mm, valid_mask, table_depth_mm),
        "source": "auto_depth_foreground",
        "reason": "largest_depth_foreground_component",
        "table_depth_mm": round(float(table_depth_mm), 1),
        "foreground_pixel_count": int(component_area),
        "foreground_pixel_ratio": round(float(component_area / max(1, width * height)), 4),
        "foreground_threshold_mm": round(float(threshold), 1),
    }


def build_depth_evidence_bundle(
    depth_frame: Any,
    intrinsics: DepthIntrinsics,
    *,
    roi: list[int],
    table_depth_mm: float | None = None,
    min_valid_depth_mm: float = 50.0,
    max_valid_depth_mm: float = 6000.0,
    object_min_height_mm: float = 30.0,
    max_points: int = 2500,
) -> DepthEvidenceBundle:
    depth_mm = _normalize_depth_frame(depth_frame, intrinsics.depth_scale)
    clipped_roi = _clip_roi(roi, intrinsics.width, intrinsics.height, "roi")
    selection_mask = _evidence_selection_mask(
        depth_mm,
        clipped_roi,
        table_depth_mm=table_depth_mm,
        min_valid_depth_mm=min_valid_depth_mm,
        max_valid_depth_mm=max_valid_depth_mm,
        object_min_height_mm=object_min_height_mm,
    )
    ys, xs = np.nonzero(selection_mask)
    if xs.size == 0:
        raise DepthMeasurementError("No valid points available for depth evidence.")

    z = depth_mm[ys, xs].astype(np.float32)
    world_x = (xs.astype(np.float32) - float(intrinsics.cx)) * z / float(intrinsics.fx)
    world_y = (ys.astype(np.float32) - float(intrinsics.cy)) * z / float(intrinsics.fy)
    points = np.column_stack((world_x, world_y, z)).astype(np.float32)
    sampled_points = _deterministic_point_sample(points, max_points=max_points)

    buffer = io.BytesIO()
    np.savez_compressed(
        buffer,
        points_mm=sampled_points,
        roi=np.asarray(clipped_roi, dtype=np.int32),
        intrinsics=np.asarray(
            [intrinsics.fx, intrinsics.fy, intrinsics.cx, intrinsics.cy, intrinsics.depth_scale],
            dtype=np.float32,
        ),
        table_depth_mm=np.asarray([table_depth_mm if table_depth_mm is not None else np.nan], dtype=np.float32),
    )
    metadata = {
        "format": "npz",
        "coordinate_system": "camera_mm",
        "roi": clipped_roi,
        "point_count": int(points.shape[0]),
        "sampled_point_count": int(sampled_points.shape[0]),
        "max_points": int(max_points),
        "table_depth_mm": round(float(table_depth_mm), 1) if table_depth_mm is not None else None,
        "contains_object_mask": table_depth_mm is not None,
    }
    return DepthEvidenceBundle(
        metadata=metadata,
        point_cloud_npz=buffer.getvalue(),
        depth_preview_png=_render_depth_preview_png(depth_mm, clipped_roi, selection_mask),
    )


def _normalize_depth_frame(depth_frame: Any, depth_scale: float) -> np.ndarray:
    depth = np.asarray(depth_frame, dtype=np.float32)
    if depth.ndim != 2:
        raise DepthMeasurementError("depth_frame must be a 2D array.")
    if depth_scale <= 0:
        raise DepthMeasurementError("depth_scale must be positive.")
    return depth * float(depth_scale)


def _analyze_depth_quality(
    depth_mm: np.ndarray,
    *,
    roi: list[int],
    background_roi: list[int] | None,
    min_valid_depth_mm: float,
    max_valid_depth_mm: float,
    noise_check: bool = True,
) -> dict[str, Any]:
    try:
        return analyze_depth_quality(
            depth_mm,
            roi=roi,
            background_roi=background_roi,
            min_valid_depth_mm=min_valid_depth_mm,
            max_valid_depth_mm=max_valid_depth_mm,
            noise_check=noise_check,
        )
    except DepthQualityError as exc:
        raise DepthMeasurementError(str(exc)) from exc


def _depth_recommendations(base_recommendations: list[str], flags: list[str]) -> list[str]:
    recommendations = list(base_recommendations)
    if "small_object_mask" in flags:
        recommendations.append("expand_object_roi_or_reposition")
    return sorted(set(recommendations))


def _center_region(width: int, height: int, source: str, *, reason: str) -> dict[str, Any]:
    margin_x = max(1, int(width * 0.18))
    margin_y = max(1, int(height * 0.18))
    return {
        "roi": [
            margin_x,
            margin_y,
            max(margin_x + 1, width - margin_x),
            max(margin_y + 1, height - margin_y),
        ],
        "background_roi": [
            0,
            0,
            max(1, min(margin_x, width)),
            max(1, min(margin_y, height)),
        ],
        "source": source,
        "reason": reason,
    }


def _border_mask(width: int, height: int) -> np.ndarray:
    border = max(1, int(round(min(width, height) * 0.1)))
    mask = np.zeros((height, width), dtype=bool)
    mask[:border, :] = True
    mask[-border:, :] = True
    mask[:, :border] = True
    mask[:, -border:] = True
    return mask


def _largest_component(mask: np.ndarray) -> tuple[np.ndarray, int] | None:
    if not np.any(mask):
        return None
    try:
        import cv2

        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), connectivity=8)
        if num_labels <= 1:
            return None
        areas = stats[1:, cv2.CC_STAT_AREA]
        label = int(np.argmax(areas)) + 1
        area = int(stats[label, cv2.CC_STAT_AREA])
        return labels == label, area
    except Exception:
        ys, xs = np.nonzero(mask)
        component = np.zeros_like(mask, dtype=bool)
        component[ys, xs] = True
        return component, int(xs.size)


def _background_corner_roi(depth_mm: np.ndarray, valid_mask: np.ndarray, table_depth_mm: float) -> list[int] | None:
    height, width = depth_mm.shape
    corner_w = max(1, int(round(width * 0.14)))
    corner_h = max(1, int(round(height * 0.14)))
    candidates = [
        [0, 0, corner_w, corner_h],
        [max(0, width - corner_w), 0, width, corner_h],
        [0, max(0, height - corner_h), corner_w, height],
        [max(0, width - corner_w), max(0, height - corner_h), width, height],
    ]
    best_roi: list[int] | None = None
    best_score = -1.0
    for roi in candidates:
        x1, y1, x2, y2 = roi
        roi_valid = valid_mask[y1:y2, x1:x2]
        if not np.any(roi_valid):
            continue
        values = depth_mm[y1:y2, x1:x2][roi_valid]
        closeness = 1.0 / (1.0 + abs(float(np.median(values)) - float(table_depth_mm)))
        score = float(roi_valid.mean()) + closeness
        if score > best_score:
            best_score = score
            best_roi = roi
    return best_roi


def _evidence_selection_mask(
    depth_mm: np.ndarray,
    roi: list[int],
    *,
    table_depth_mm: float | None,
    min_valid_depth_mm: float,
    max_valid_depth_mm: float,
    object_min_height_mm: float,
) -> np.ndarray:
    x1, y1, x2, y2 = roi
    mask = np.zeros_like(depth_mm, dtype=bool)
    roi_depth = depth_mm[y1:y2, x1:x2]
    valid = (
        np.isfinite(roi_depth)
        & (roi_depth >= min_valid_depth_mm)
        & (roi_depth <= max_valid_depth_mm)
    )
    if table_depth_mm is not None:
        valid &= roi_depth <= (float(table_depth_mm) - float(object_min_height_mm))
    mask[y1:y2, x1:x2] = valid
    return mask


def _deterministic_point_sample(points: np.ndarray, *, max_points: int) -> np.ndarray:
    if points.shape[0] <= max_points:
        return points
    indexes = np.linspace(0, points.shape[0] - 1, max_points, dtype=np.int32)
    return points[indexes]


def _render_depth_preview_png(depth_mm: np.ndarray, roi: list[int], selection_mask: np.ndarray) -> bytes:
    try:
        import cv2
    except Exception as exc:
        raise DepthMeasurementError("OpenCV is required to render depth evidence previews.") from exc

    valid = np.isfinite(depth_mm) & (depth_mm > 0)
    if np.any(valid):
        low = float(np.percentile(depth_mm[valid], 2))
        high = float(np.percentile(depth_mm[valid], 98))
    else:
        low, high = 0.0, 1.0
    normalized = np.clip((depth_mm - low) / max(1.0, high - low), 0.0, 1.0)
    gray = (255 - normalized * 255).astype(np.uint8)
    preview = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    preview[selection_mask] = (40, 210, 80)
    x1, y1, x2, y2 = roi
    cv2.rectangle(preview, (x1, y1), (max(x1, x2 - 1), max(y1, y2 - 1)), (0, 180, 255), 1)
    ok, encoded = cv2.imencode(".png", preview)
    if not ok:
        raise DepthMeasurementError("Failed to encode depth evidence preview.")
    return encoded.tobytes()


def _normalize_footprint_method(method: str) -> str:
    normalized = str(method or "axis_aligned").strip().lower()
    if normalized not in {"axis_aligned", "principal_axes"}:
        raise DepthMeasurementError("footprint_method must be axis_aligned or principal_axes.")
    return normalized


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


def _trimmed_extent(values: np.ndarray, trim_quantile: float) -> float:
    if values.size == 0:
        raise DepthMeasurementError("No points available for extent measurement.")
    if trim_quantile <= 0:
        return float(values.max() - values.min())
    lower_q = min(0.45, trim_quantile)
    upper_q = max(0.55, 1.0 - trim_quantile)
    lower = float(np.quantile(values, lower_q))
    upper = float(np.quantile(values, upper_q))
    return max(0.0, upper - lower)


def _footprint_extents(
    world_x: np.ndarray,
    world_y: np.ndarray,
    footprint_method: str,
    trim_quantile: float,
) -> tuple[float, float, float | None]:
    if footprint_method == "axis_aligned" or world_x.size < 2:
        return (
            _trimmed_extent(world_x, trim_quantile),
            _trimmed_extent(world_y, trim_quantile),
            None,
        )

    points = np.column_stack((world_x, world_y)).astype(np.float32)
    centered = points - points.mean(axis=0)
    if not np.any(centered):
        return 0.0, 0.0, 0.0

    covariance = np.cov(centered, rowvar=False)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    order = np.argsort(eigenvalues)[::-1]
    axes = eigenvectors[:, order]
    projections = centered @ axes
    major_extent = _trimmed_extent(projections[:, 0], trim_quantile)
    minor_extent = _trimmed_extent(projections[:, 1], trim_quantile)
    major_axis = axes[:, 0]
    orientation_deg = float(np.degrees(np.arctan2(major_axis[1], major_axis[0])))
    if orientation_deg <= -90.0:
        orientation_deg += 180.0
    elif orientation_deg > 90.0:
        orientation_deg -= 180.0
    return major_extent, minor_extent, orientation_deg
