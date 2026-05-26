from __future__ import annotations

import base64
import io
from dataclasses import dataclass
from typing import Any

try:
    import cv2
    import numpy as np
    from PIL import ExifTags, Image
except Exception:  # pragma: no cover - exercised on machines without OpenCV.
    cv2 = None  # type: ignore[assignment]
    np = None  # type: ignore[assignment]
    Image = None  # type: ignore[assignment]
    ExifTags = None  # type: ignore[assignment]


@dataclass(frozen=True)
class MeasurementConfig:
    marker_size_mm: float = 50.0
    manual_height_mm: float | None = None
    camera_distance_mm: float | None = None
    focal_length_35mm: float | None = None
    top_box_points: list[list[float]] | None = None
    side_box_points: list[list[float]] | None = None


class MeasurementError(RuntimeError):
    pass


def opencv_ready() -> bool:
    return cv2 is not None and np is not None and hasattr(cv2, "aruco")


def measure_images(
    top_image_bytes: bytes,
    *,
    side_image_bytes: bytes | None = None,
    config: MeasurementConfig | None = None,
) -> dict[str, Any]:
    if not opencv_ready():
        raise MeasurementError("OpenCV ArUco support is not available.")

    cfg = config or MeasurementConfig()
    top_image = _decode_image(top_image_bytes)
    top = _measure_single_view(
        top_image,
        top_image_bytes,
        cfg.marker_size_mm,
        "top",
        cfg.top_box_points,
        cfg.camera_distance_mm,
        cfg.focal_length_35mm,
    )

    side = None
    if side_image_bytes:
        side = _measure_single_view(
            _decode_image(side_image_bytes),
            side_image_bytes,
            cfg.marker_size_mm,
            "side",
            cfg.side_box_points,
            cfg.camera_distance_mm,
            cfg.focal_length_35mm,
        )

    dimensions: dict[str, float | None] = {"length_mm": None, "width_mm": None, "height_mm": None}
    flags: list[str] = ["single_camera_perspective_limited"]
    status = "needs_reference"
    confidence = 0.2

    if top["pixel_per_mm"] and top["box"]:
        width_px, height_px = top["box"]["size_px"]
        length_mm = max(width_px, height_px) / top["pixel_per_mm"]
        width_mm = min(width_px, height_px) / top["pixel_per_mm"]
        dimensions["length_mm"] = round(length_mm, 1)
        dimensions["width_mm"] = round(width_mm, 1)
        status = "measured"
        confidence = 0.72 if top["scale_source"] == "aruco_marker" else 0.48
        flags.append(f"{top['scale_source']}_scale_used")
        if top["box"].get("source") == "manual":
            flags.append("manual_top_box_used")
    else:
        if not top["markers"]:
            flags.append("missing_aruco_reference")
        if not top["box"]:
            flags.append("package_contour_not_found")

    side_measurement = None
    if side and side["pixel_per_mm"] and side["box"]:
        side_width_px, side_height_px = side["box"]["size_px"]
        side_major_mm = max(side_width_px, side_height_px) / side["pixel_per_mm"]
        side_minor_mm = min(side_width_px, side_height_px) / side["pixel_per_mm"]
        side_measurement = {
            "major_mm": round(side_major_mm, 1),
            "minor_mm": round(side_minor_mm, 1),
            "height_candidate_mm": round(side_minor_mm, 1),
            "scale_source": side["scale_source"],
        }
        flags.append(f"side_{side['scale_source']}_scale_used")
        if side["box"].get("source") == "manual":
            flags.append("manual_side_box_used")

    if cfg.manual_height_mm and cfg.manual_height_mm > 0:
        dimensions["height_mm"] = round(cfg.manual_height_mm, 1)
        flags.append("manual_height_used")
        if status == "measured":
            confidence = max(confidence, 0.78)
    elif side_measurement:
        dimensions["height_mm"] = side_measurement["height_candidate_mm"]
        flags.append("side_view_height_estimated")
        if status == "measured":
            confidence = max(confidence, 0.82 if side["scale_source"] == "aruco_marker" else 0.58)
    else:
        flags.append("height_missing")

    if top["markers"]:
        flags.append("aruco_reference_detected")
    if side and side["markers"]:
        flags.append("side_aruco_reference_detected")
    if top["box"] and top["box"].get("source") == "manual":
        flags.append("manual_annotation_used")
    if top["box"] and top["box"]["area_ratio"] < 0.025:
        flags.append("package_small_in_frame")

    if dimensions["length_mm"] and dimensions["width_mm"] and dimensions["height_mm"]:
        volume_l = (
            dimensions["length_mm"]
            * dimensions["width_mm"]
            * dimensions["height_mm"]
            / 1_000_000
        )
        dimensions["volume_l"] = round(volume_l, 3)
    else:
        dimensions["volume_l"] = None

    return {
        "status": status,
        "confidence": round(confidence, 2),
        "dimensions": dimensions,
        "quality_flags": sorted(set(flags)),
        "recommendation_codes": _recommendations(flags),
        "side_measurement": side_measurement,
        "top_view": _public_view(top),
        "side_view": _public_view(side) if side else None,
        "method": {
            "name": "aruco_single_camera_reference",
            "marker_size_mm": cfg.marker_size_mm,
            "notes": [
                "Top-down phone photos can estimate length and width when the marker is on the same plane.",
                "Height needs a side image, manual input, or future depth/structured-light hardware.",
                "No-marker mode can only estimate scale when camera distance and focal length metadata are available.",
            ],
        },
    }


def generate_demo_image() -> bytes:
    if not opencv_ready():
        raise MeasurementError("OpenCV ArUco support is not available.")
    canvas = np.full((780, 1120, 3), (242, 240, 232), dtype=np.uint8)
    cv2.rectangle(canvas, (0, 0), (1119, 779), (246, 244, 238), -1)
    cv2.rectangle(canvas, (282, 162), (912, 572), (206, 199, 184), -1)
    cv2.rectangle(canvas, (282, 162), (912, 572), (46, 56, 50), 5)
    cv2.line(canvas, (300, 365), (895, 365), (180, 160, 125), 3)
    cv2.putText(
        canvas,
        "PackVision demo parcel",
        (330, 145),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.78,
        (48, 57, 52),
        2,
        cv2.LINE_AA,
    )

    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    marker = cv2.aruco.generateImageMarker(dictionary, 0, 110)
    marker_bgr = cv2.cvtColor(marker, cv2.COLOR_GRAY2BGR)
    canvas[66:176, 76:186] = marker_bgr
    cv2.putText(
        canvas,
        "50 mm marker",
        (76, 206),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (48, 57, 52),
        1,
        cv2.LINE_AA,
    )

    ok, encoded = cv2.imencode(".jpg", canvas, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
    if not ok:
        raise MeasurementError("Unable to encode demo image.")
    return encoded.tobytes()


def generate_marker_png(marker_id: int = 0, pixels: int = 800) -> bytes:
    if not opencv_ready():
        raise MeasurementError("OpenCV ArUco support is not available.")
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    if hasattr(cv2.aruco, "generateImageMarker"):
        marker = cv2.aruco.generateImageMarker(dictionary, marker_id, pixels)
    else:  # pragma: no cover - legacy OpenCV fallback.
        marker = np.zeros((pixels, pixels), dtype=np.uint8)
        cv2.aruco.drawMarker(dictionary, marker_id, pixels, marker, 1)
    ok, encoded = cv2.imencode(".png", marker)
    if not ok:
        raise MeasurementError("Unable to encode marker image.")
    return encoded.tobytes()


def generate_calibration_svg(marker_size_mm: float = 50.0) -> str:
    marker_png = generate_marker_png()
    marker_b64 = base64.b64encode(marker_png).decode("ascii")
    x_mm = 20
    y_mm = 24
    guide_w = marker_size_mm + 24
    guide_h = marker_size_mm + 44
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">
  <rect width="210" height="297" fill="#ffffff"/>
  <rect x="{x_mm - 6}" y="{y_mm - 10}" width="{guide_w}" height="{guide_h}" rx="2" fill="none" stroke="#111827" stroke-width="0.4"/>
  <image href="data:image/png;base64,{marker_b64}" x="{x_mm}" y="{y_mm}" width="{marker_size_mm}" height="{marker_size_mm}"/>
  <text x="{x_mm}" y="{y_mm + marker_size_mm + 10}" font-family="Arial, sans-serif" font-size="5" fill="#111827">PackVision ArUco ID 0</text>
  <text x="{x_mm}" y="{y_mm + marker_size_mm + 17}" font-family="Arial, sans-serif" font-size="4" fill="#374151">Marker size: {marker_size_mm:g} mm. Print at 100% scale.</text>
  <line x1="20" y1="270" x2="120" y2="270" stroke="#111827" stroke-width="0.5"/>
  <text x="20" y="267" font-family="Arial, sans-serif" font-size="4" fill="#111827">100 mm check ruler</text>
  <path d="M20 267 L20 273 M120 267 L120 273" stroke="#111827" stroke-width="0.5"/>
</svg>"""


def _decode_image(content: bytes) -> Any:
    arr = np.frombuffer(content, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise MeasurementError("Unable to decode image.")
    return image


def _measure_single_view(
    image: Any,
    image_bytes: bytes,
    marker_size_mm: float,
    view_name: str,
    manual_box_points: list[list[float]] | None,
    camera_distance_mm: float | None,
    focal_length_35mm: float | None,
) -> dict[str, Any]:
    markers = _detect_markers(image, marker_size_mm)
    marker_scale = _scale_from_markers(markers)
    camera_scale = _scale_from_camera(image, image_bytes, camera_distance_mm, focal_length_35mm)
    pixel_per_mm = marker_scale or camera_scale["pixel_per_mm"]
    scale_source = "aruco_marker" if marker_scale else camera_scale["source"]
    box = _box_from_points(image, manual_box_points) if manual_box_points else _find_package_box(image, markers)
    annotated = _annotate(image, markers, box, pixel_per_mm, view_name)
    return {
        "view": view_name,
        "image_size": {"width": int(image.shape[1]), "height": int(image.shape[0])},
        "markers": markers,
        "pixel_per_mm": pixel_per_mm,
        "scale_source": scale_source,
        "camera_scale": camera_scale,
        "box": box,
        "annotated_jpeg": annotated,
    }


def _detect_markers(image: Any, marker_size_mm: float) -> list[dict[str, Any]]:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    if hasattr(cv2.aruco, "ArucoDetector"):
        detector = cv2.aruco.ArucoDetector(dictionary, cv2.aruco.DetectorParameters())
        corners, ids, _ = detector.detectMarkers(gray)
    else:  # pragma: no cover - legacy OpenCV fallback.
        corners, ids, _ = cv2.aruco.detectMarkers(gray, dictionary)
    if ids is None:
        return []

    markers: list[dict[str, Any]] = []
    for marker_corners, marker_id in zip(corners, ids.flatten()):
        pts = marker_corners.reshape((4, 2)).astype(float)
        sides = [
            float(np.linalg.norm(pts[i] - pts[(i + 1) % 4]))
            for i in range(4)
        ]
        side_px = sum(sides) / len(sides)
        markers.append(
            {
                "id": int(marker_id),
                "corners": pts.round(2).tolist(),
                "side_px": round(side_px, 2),
                "pixel_per_mm": round(side_px / marker_size_mm, 4),
                "center": pts.mean(axis=0).round(2).tolist(),
            }
        )
    return markers


def _scale_from_markers(markers: list[dict[str, Any]]) -> float | None:
    if not markers:
        return None
    values = [marker["pixel_per_mm"] for marker in markers if marker["pixel_per_mm"] > 0]
    if not values:
        return None
    return float(np.median(values))


def _find_package_box(image: Any, markers: list[dict[str, Any]]) -> dict[str, Any] | None:
    working = image.copy()
    for marker in markers:
        pts = np.array(marker["corners"], dtype=np.int32)
        cv2.fillConvexPoly(working, pts, (255, 255, 255))

    gray = cv2.cvtColor(working, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7, 7), 0)
    median = float(np.median(gray))
    lower = int(max(0, 0.66 * median))
    upper = int(min(255, 1.33 * median))
    edges = cv2.Canny(gray, lower, upper)
    kernel = np.ones((5, 5), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    image_area = image.shape[0] * image.shape[1]
    candidates = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < image_area * 0.01 or area > image_area * 0.9:
            continue
        rect = cv2.minAreaRect(contour)
        (width_px, height_px) = rect[1]
        if width_px < 20 or height_px < 20:
            continue
        candidates.append((area, contour, rect))

    if not candidates:
        return None

    area, contour, rect = max(candidates, key=lambda item: item[0])
    box_points = cv2.boxPoints(rect).astype(int)
    width_px, height_px = rect[1]
    return {
        "corners": box_points.tolist(),
        "size_px": [round(float(width_px), 2), round(float(height_px), 2)],
        "angle_deg": round(float(rect[2]), 2),
        "area_ratio": round(float(area / image_area), 4),
        "contour_points": int(len(contour)),
        "source": "auto",
    }


def _box_from_points(image: Any, points: list[list[float]] | None) -> dict[str, Any] | None:
    if not points or len(points) < 2:
        return None
    arr = np.array(points, dtype=np.float32).reshape(-1, 2)
    if len(arr) == 2:
        (x1, y1), (x2, y2) = arr
        arr = np.array([[x1, y1], [x2, y1], [x2, y2], [x1, y2]], dtype=np.float32)
    rect = cv2.minAreaRect(arr)
    box_points = cv2.boxPoints(rect).astype(int)
    width_px, height_px = rect[1]
    image_area = image.shape[0] * image.shape[1]
    return {
        "corners": box_points.tolist(),
        "size_px": [round(float(width_px), 2), round(float(height_px), 2)],
        "angle_deg": round(float(rect[2]), 2),
        "area_ratio": round(float((width_px * height_px) / image_area), 4),
        "contour_points": int(len(arr)),
        "source": "manual",
    }


def _scale_from_camera(
    image: Any,
    image_bytes: bytes,
    camera_distance_mm: float | None,
    focal_length_35mm: float | None,
) -> dict[str, Any]:
    exif = _extract_exif(image_bytes)
    focal_35mm = focal_length_35mm or exif.get("focal_length_35mm")
    if not camera_distance_mm or not focal_35mm or camera_distance_mm <= 0 or focal_35mm <= 0:
        return {
            "pixel_per_mm": None,
            "source": "none",
            "exif": exif,
            "requires": ["camera_distance_mm", "focal_length_35mm_or_exif"],
        }
    image_width_px = image.shape[1]
    focal_px = image_width_px * float(focal_35mm) / 36.0
    return {
        "pixel_per_mm": round(float(focal_px / camera_distance_mm), 6),
        "source": "camera_distance_exif" if exif.get("focal_length_35mm") and not focal_length_35mm else "camera_distance_manual_focal",
        "focal_px": round(float(focal_px), 3),
        "camera_distance_mm": camera_distance_mm,
        "focal_length_35mm": focal_35mm,
        "exif": exif,
    }


def _extract_exif(image_bytes: bytes) -> dict[str, Any]:
    if Image is None or ExifTags is None:
        return {}
    try:
        image = Image.open(io.BytesIO(image_bytes))
        raw = image.getexif()
    except Exception:
        return {}
    if not raw:
        return {}
    tags = {ExifTags.TAGS.get(key, key): raw.get(key) for key in raw.keys()}
    return {
        "focal_length_35mm": _number(tags.get("FocalLengthIn35mmFilm")),
        "focal_length": _number(tags.get("FocalLength")),
        "f_number": _number(tags.get("FNumber")),
        "make": tags.get("Make"),
        "model": tags.get("Model"),
    }


def _number(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if hasattr(value, "numerator") and hasattr(value, "denominator") and value.denominator:
        return float(value.numerator / value.denominator)
    if isinstance(value, tuple) and len(value) == 2 and value[1]:
        return float(value[0] / value[1])
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _annotate(
    image: Any,
    markers: list[dict[str, Any]],
    box: dict[str, Any] | None,
    pixel_per_mm: float | None,
    view_name: str,
) -> bytes:
    annotated = image.copy()
    if markers:
        corners = [np.array(marker["corners"], dtype=np.float32).reshape(1, 4, 2) for marker in markers]
        ids = np.array([[marker["id"]] for marker in markers], dtype=np.int32)
        cv2.aruco.drawDetectedMarkers(annotated, corners, ids)

    if box:
        pts = np.array(box["corners"], dtype=np.int32)
        cv2.polylines(annotated, [pts], True, (31, 122, 117), 4)
        label = _box_label(box, pixel_per_mm)
        anchor = tuple(pts[np.argmin(pts[:, 1])])
        cv2.putText(
            annotated,
            f"{view_name}: {label}",
            (int(anchor[0]), max(28, int(anchor[1]) - 12)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (31, 122, 117),
            2,
            cv2.LINE_AA,
        )

    ok, encoded = cv2.imencode(".jpg", annotated, [int(cv2.IMWRITE_JPEG_QUALITY), 88])
    if not ok:
        raise MeasurementError("Unable to encode annotated image.")
    return encoded.tobytes()


def _box_label(box: dict[str, Any], pixel_per_mm: float | None) -> str:
    width_px, height_px = box["size_px"]
    if not pixel_per_mm:
        return f"{max(width_px, height_px):.0f}px x {min(width_px, height_px):.0f}px"
    return (
        f"{max(width_px, height_px) / pixel_per_mm:.1f}mm x "
        f"{min(width_px, height_px) / pixel_per_mm:.1f}mm"
    )


def _public_view(view: dict[str, Any] | None) -> dict[str, Any] | None:
    if not view:
        return None
    cleaned = dict(view)
    annotated = cleaned.pop("annotated_jpeg", b"")
    cleaned["annotated_image_base64"] = base64.b64encode(annotated).decode("ascii")
    return cleaned


def _recommendations(flags: list[str]) -> list[str]:
    flag_set = set(flags)
    recommendations: list[str] = []
    if "missing_aruco_reference" in flag_set:
        recommendations.append("place_or_print_marker")
        recommendations.append("use_distance_mode_or_marker")
    if "package_contour_not_found" in flag_set:
        recommendations.append("retake_on_plain_background")
    if "height_missing" in flag_set:
        recommendations.append("add_height_or_side_photo")
    if "package_small_in_frame" in flag_set:
        recommendations.append("move_camera_closer")
    if "single_camera_perspective_limited" in flag_set:
        recommendations.append("keep_camera_top_down")
    if "camera_distance_exif_scale_used" in flag_set or "camera_distance_manual_focal_scale_used" in flag_set:
        recommendations.append("distance_mode_is_estimate")
    return recommendations
