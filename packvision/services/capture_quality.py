from __future__ import annotations

from typing import Any

try:
    import cv2
    import numpy as np
except Exception:  # pragma: no cover - exercised on machines without OpenCV.
    cv2 = None  # type: ignore[assignment]
    np = None  # type: ignore[assignment]


class CaptureQualityError(RuntimeError):
    pass


def analyze_capture_quality(image_bytes: bytes) -> dict[str, Any]:
    if cv2 is None or np is None:
        raise CaptureQualityError("OpenCV is not available.")
    image = _decode_image(image_bytes)
    return analyze_decoded_capture_quality(image)


def analyze_decoded_capture_quality(image: Any) -> dict[str, Any]:
    if cv2 is None or np is None:
        raise CaptureQualityError("OpenCV is not available.")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mean_luma = float(np.mean(gray))
    contrast_std = float(np.std(gray))
    overexposed_ratio = float(np.mean(gray >= 250))
    underexposed_ratio = float(np.mean(gray <= 8))
    blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())

    flags: list[str] = []
    if mean_luma >= 245 or overexposed_ratio >= 0.88:
        flags.append("lighting_overexposed")
    if mean_luma <= 25 or underexposed_ratio >= 0.70:
        flags.append("lighting_underexposed")
    if contrast_std <= 8:
        flags.append("low_contrast_capture")
    if blur_score <= 10:
        flags.append("blurry_capture")

    return {
        "status": "review" if flags else "ok",
        "metrics": {
            "mean_luma": round(mean_luma, 3),
            "contrast_std": round(contrast_std, 3),
            "overexposed_ratio": round(overexposed_ratio, 4),
            "underexposed_ratio": round(underexposed_ratio, 4),
            "blur_score": round(blur_score, 3),
        },
        "quality_flags": sorted(set(flags)),
        "recommendation_codes": _recommendations(flags),
    }


def _decode_image(content: bytes) -> Any:
    arr = np.frombuffer(content, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise CaptureQualityError("Unable to decode image.")
    return image


def _recommendations(flags: list[str]) -> list[str]:
    flag_set = set(flags)
    recommendations: list[str] = []
    if "lighting_overexposed" in flag_set:
        recommendations.append("retake_away_from_direct_light")
    if "lighting_underexposed" in flag_set:
        recommendations.append("add_stable_indoor_light")
    if "low_contrast_capture" in flag_set:
        recommendations.append("retake_on_plain_background")
    if "blurry_capture" in flag_set:
        recommendations.append("stabilize_camera_or_tripod")
    return recommendations
