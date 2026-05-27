from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageSequence

from packvision.services.depth_devices import astra_depth_intrinsics_from_fov
from packvision.services.depth_geometry import (
    DepthIntrinsics,
    DepthMeasurementError,
    DepthObjectConfig,
    measure_depth_object_mask,
)


class DepthSimulationError(RuntimeError):
    pass


@dataclass(frozen=True)
class SimulatedDepthArtifacts:
    source_png: bytes
    overlay_png: bytes
    depth_preview_png: bytes


@dataclass(frozen=True)
class SimulatedDepthMeasurement:
    result: dict[str, Any]
    artifacts: SimulatedDepthArtifacts


def simulate_astra_depth_measurement_from_image(
    image_bytes: bytes,
    *,
    filename: str | None = None,
    source_url: str | None = None,
    roi: list[int] | None = None,
    table_depth_mm: float = 1200.0,
    object_depth_mm: float = 850.0,
    frame_index: int = 0,
    max_width: int = 640,
) -> SimulatedDepthMeasurement:
    if not image_bytes:
        raise DepthSimulationError("image_bytes is required.")
    if table_depth_mm <= object_depth_mm:
        raise DepthSimulationError("table_depth_mm must be greater than object_depth_mm.")
    if max_width < 160:
        raise DepthSimulationError("max_width must be at least 160 pixels.")

    rgb = _decode_rgb(image_bytes, frame_index=frame_index)
    rgb = _resize_to_width(rgb, max_width=max_width)
    height, width = rgb.shape[:2]
    clipped_roi = _clip_roi(roi or _default_roi(width, height), width, height)
    mask, mask_method = _foreground_mask(rgb, clipped_roi)
    depth_frame = _synthetic_depth_frame(
        rgb,
        mask,
        table_depth_mm=table_depth_mm,
        object_depth_mm=object_depth_mm,
    )

    intrinsics_dict = astra_depth_intrinsics_from_fov(width, height)
    intrinsics = DepthIntrinsics(
        fx=float(intrinsics_dict["fx"]),
        fy=float(intrinsics_dict["fy"]),
        cx=float(intrinsics_dict["cx"]),
        cy=float(intrinsics_dict["cy"]),
        width=width,
        height=height,
        depth_scale=1.0,
    )
    background_roi = _background_roi(width, height)
    try:
        result = measure_depth_object_mask(
            depth_frame,
            intrinsics,
            DepthObjectConfig(
                roi=clipped_roi,
                background_roi=background_roi,
                table_depth_mm=table_depth_mm,
                object_min_height_mm=max(30.0, (table_depth_mm - object_depth_mm) * 0.35),
                trim_quantile=0.02,
                footprint_method="principal_axes",
            ),
        )
    except DepthMeasurementError as exc:
        raise DepthSimulationError(str(exc)) from exc

    result["simulation"] = {
        "mode": "real_image_plus_synthetic_astra_depth",
        "filename": filename,
        "source_url": source_url,
        "source_kind": "uploaded_or_downloaded_real_rgb_image",
        "frame_index": int(frame_index),
        "image_shape": {"width": width, "height": height},
        "roi": clipped_roi,
        "background_roi": background_roi,
        "mask_method": mask_method,
        "mask_pixel_count": int(mask.sum()),
        "mask_coverage_ratio": round(float(mask.sum()) / float(width * height), 4),
        "table_depth_mm": round(float(table_depth_mm), 1),
        "object_depth_mm": round(float(object_depth_mm), 1),
        "simulated_height_mm": round(float(table_depth_mm - object_depth_mm), 1),
        "intrinsics_source": intrinsics_dict["source"],
        "quality_flags": [
            "hardware_not_connected",
            "real_rgb_image_used",
            "synthetic_depth_frame_used",
            "astra_intrinsics_simulated_from_datasheet_fov",
        ],
        "operator_note": "This is a hardware dry-run, not a certified dimension measurement.",
    }
    result.setdefault("quality_flags", [])
    for flag in result["simulation"]["quality_flags"]:
        if flag not in result["quality_flags"]:
            result["quality_flags"].append(flag)
    result.setdefault("recommendation_codes", [])
    if "validate_with_real_astra_depth_frame" not in result["recommendation_codes"]:
        result["recommendation_codes"].append("validate_with_real_astra_depth_frame")
    result["method"]["notes"].append(
        "RGB pixels are real, but depth is simulated with Astra Pro FOV intrinsics for pre-hardware workflow testing."
    )

    artifacts = SimulatedDepthArtifacts(
        source_png=_encode_png(rgb),
        overlay_png=_render_overlay(rgb, clipped_roi, mask, result),
        depth_preview_png=_render_depth_preview(depth_frame, mask),
    )
    return SimulatedDepthMeasurement(result=result, artifacts=artifacts)


def _decode_rgb(image_bytes: bytes, *, frame_index: int) -> np.ndarray:
    try:
        with Image.open(io.BytesIO(image_bytes)) as image:
            frames = ImageSequence.Iterator(image)
            selected = None
            for index, frame in enumerate(frames):
                selected = frame.convert("RGB")
                if index >= max(0, int(frame_index)):
                    break
            if selected is None:
                selected = image.convert("RGB")
            return np.asarray(selected, dtype=np.uint8)
    except Exception as exc:
        raise DepthSimulationError("Unable to decode the image.") from exc


def _resize_to_width(rgb: np.ndarray, *, max_width: int) -> np.ndarray:
    height, width = rgb.shape[:2]
    if width <= max_width:
        return rgb
    scale = max_width / float(width)
    resized = cv2.resize(rgb, (max_width, max(1, int(round(height * scale)))), interpolation=cv2.INTER_AREA)
    return resized.astype(np.uint8)


def _default_roi(width: int, height: int) -> list[int]:
    margin_x = int(width * 0.08)
    margin_y = int(height * 0.08)
    return [margin_x, margin_y, width - margin_x, height - margin_y]


def _clip_roi(roi: list[int], width: int, height: int) -> list[int]:
    if len(roi) != 4:
        raise DepthSimulationError("roi must be [x1, y1, x2, y2].")
    x1, y1, x2, y2 = [int(round(float(value))) for value in roi]
    x1 = max(0, min(width - 1, x1))
    y1 = max(0, min(height - 1, y1))
    x2 = max(x1 + 1, min(width, x2))
    y2 = max(y1 + 1, min(height, y2))
    return [x1, y1, x2, y2]


def _foreground_mask(rgb: np.ndarray, roi: list[int]) -> tuple[np.ndarray, str]:
    height, width = rgb.shape[:2]
    x1, y1, x2, y2 = roi
    crop = rgb[y1:y2, x1:x2]
    hsv = cv2.cvtColor(crop, cv2.COLOR_RGB2HSV)
    gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)
    sat = hsv[:, :, 1]
    saturation_cutoff = max(30, int(np.percentile(sat, 62)))
    colorful = sat >= saturation_cutoff
    edges = cv2.Canny(gray, 40, 120)
    edges = cv2.dilate(edges, np.ones((5, 5), np.uint8), iterations=1) > 0
    local_contrast = np.abs(gray.astype(np.int16) - int(np.median(gray))) > 22
    mask_crop = colorful | edges | local_contrast
    mask_crop = cv2.morphologyEx(mask_crop.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)) > 0
    mask_crop = _keep_central_components(mask_crop)
    coverage = float(mask_crop.sum()) / float(mask_crop.size)
    method = "color_edge_contrast_mask"
    if coverage < 0.02 or coverage > 0.85:
        mask_crop = _fallback_ellipse_mask(crop.shape[1], crop.shape[0])
        method = "fallback_center_ellipse_mask"

    mask = np.zeros((height, width), dtype=bool)
    mask[y1:y2, x1:x2] = mask_crop
    return mask, method


def _keep_central_components(mask: np.ndarray) -> np.ndarray:
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask.astype(np.uint8), connectivity=8)
    if num_labels <= 1:
        return mask
    height, width = mask.shape
    center = np.array([width / 2.0, height / 2.0], dtype=np.float32)
    keep = np.zeros_like(mask, dtype=bool)
    min_area = max(20, int(width * height * 0.004))
    for label in range(1, num_labels):
        area = int(stats[label, cv2.CC_STAT_AREA])
        if area < min_area:
            continue
        centroid = centroids[label]
        distance = float(np.linalg.norm(centroid - center))
        if distance <= max(width, height) * 0.55 or area >= width * height * 0.08:
            keep |= labels == label
    return keep if keep.any() else mask


def _fallback_ellipse_mask(width: int, height: int) -> np.ndarray:
    mask = np.zeros((height, width), dtype=np.uint8)
    center = (width // 2, height // 2)
    axes = (max(8, int(width * 0.33)), max(8, int(height * 0.28)))
    cv2.ellipse(mask, center, axes, angle=-8, startAngle=0, endAngle=360, color=1, thickness=-1)
    return mask.astype(bool)


def _synthetic_depth_frame(
    rgb: np.ndarray,
    mask: np.ndarray,
    *,
    table_depth_mm: float,
    object_depth_mm: float,
) -> list[list[float]]:
    height, width = rgb.shape[:2]
    xs = np.linspace(-1.0, 1.0, width, dtype=np.float32)
    ys = np.linspace(-1.0, 1.0, height, dtype=np.float32)[:, None]
    depth = np.full((height, width), float(table_depth_mm), dtype=np.float32)
    depth += xs * 3.5 + ys * 2.5
    texture = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
    texture = (texture - float(np.mean(texture))) / max(1.0, float(np.std(texture)))
    depth[mask] = float(object_depth_mm) + texture[mask] * 3.0
    return np.round(depth, 2).astype(float).tolist()


def _background_roi(width: int, height: int) -> list[int]:
    return [0, 0, max(2, int(width * 0.12)), max(2, int(height * 0.12))]


def _encode_png(rgb: np.ndarray) -> bytes:
    image = Image.fromarray(rgb)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _render_overlay(rgb: np.ndarray, roi: list[int], mask: np.ndarray, result: dict[str, Any]) -> bytes:
    overlay = Image.fromarray(rgb).convert("RGBA")
    mask_layer = Image.new("RGBA", overlay.size, (0, 0, 0, 0))
    mask_image = Image.fromarray(mask.astype(np.uint8) * 115)
    color = Image.new("RGBA", overlay.size, (28, 123, 255, 95))
    mask_layer.paste(color, (0, 0), mask_image)
    overlay = Image.alpha_composite(overlay, mask_layer)
    draw = ImageDraw.Draw(overlay)
    x1, y1, x2, y2 = roi
    draw.rectangle([x1, y1, x2, y2], outline=(255, 214, 10, 255), width=3)
    dims = result.get("dimensions") or {}
    label = (
        f"L {dims.get('length_mm')} mm  W {dims.get('width_mm')} mm  "
        f"H {dims.get('height_mm')} mm"
    )
    draw.rectangle([8, 8, min(overlay.width - 8, 410), 38], fill=(0, 0, 0, 180))
    draw.text((16, 15), label, fill=(255, 255, 255, 255))
    buffer = io.BytesIO()
    overlay.convert("RGB").save(buffer, format="PNG")
    return buffer.getvalue()


def _render_depth_preview(depth_frame: list[list[float]], mask: np.ndarray) -> bytes:
    depth = np.asarray(depth_frame, dtype=np.float32)
    valid = np.isfinite(depth)
    low = float(np.percentile(depth[valid], 2)) if valid.any() else 0.0
    high = float(np.percentile(depth[valid], 98)) if valid.any() else 1.0
    normalized = np.clip((depth - low) / max(1.0, high - low), 0, 1)
    preview = (255 - normalized * 220).astype(np.uint8)
    rgb = cv2.cvtColor(preview, cv2.COLOR_GRAY2RGB)
    rgb[mask] = np.maximum(rgb[mask], np.array([255, 90, 60], dtype=np.uint8))
    return _encode_png(rgb)
