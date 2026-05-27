import pytest

from packvision.services.capture_quality import analyze_capture_quality
from packvision.services.measurement import MeasurementConfig, measure_images, opencv_ready


pytestmark = pytest.mark.skipif(not opencv_ready(), reason="OpenCV is unavailable")


def _jpeg_from_gray(value: int) -> bytes:
    import cv2
    import numpy as np

    image = np.full((360, 480, 3), value, dtype=np.uint8)
    ok, encoded = cv2.imencode(".jpg", image)
    assert ok
    return encoded.tobytes()


def test_capture_quality_flags_overexposed_phone_photo():
    result = analyze_capture_quality(_jpeg_from_gray(255))

    assert result["status"] == "review"
    assert "lighting_overexposed" in result["quality_flags"]
    assert "retake_away_from_direct_light" in result["recommendation_codes"]


def test_capture_quality_flags_underexposed_phone_photo():
    result = analyze_capture_quality(_jpeg_from_gray(5))

    assert result["status"] == "review"
    assert "lighting_underexposed" in result["quality_flags"]
    assert "add_stable_indoor_light" in result["recommendation_codes"]


def test_measurement_merges_capture_quality_flags_for_worker_mode():
    image_bytes = _jpeg_from_gray(255)

    result = measure_images(
        image_bytes,
        config=MeasurementConfig(
            camera_distance_mm=1000,
            focal_length_35mm=35,
            top_box_points=[[80, 80], [360, 260]],
            manual_height_mm=120,
        ),
    )

    assert result["status"] == "measured"
    assert "lighting_overexposed" in result["quality_flags"]
    assert "retake_away_from_direct_light" in result["recommendation_codes"]
