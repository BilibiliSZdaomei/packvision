import pytest

from packvision.services.measurement import MeasurementConfig, measure_images, opencv_ready


pytestmark = pytest.mark.skipif(not opencv_ready(), reason="OpenCV ArUco is unavailable")


def test_measure_top_image_with_aruco_marker():
    import cv2
    import numpy as np

    canvas = np.full((700, 1000, 3), 255, dtype=np.uint8)
    cv2.rectangle(canvas, (250, 150), (850, 550), (214, 211, 199), -1)
    cv2.rectangle(canvas, (250, 150), (850, 550), (45, 55, 49), 5)

    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    marker = cv2.aruco.generateImageMarker(dictionary, 0, 100)
    canvas[64:164, 72:172] = cv2.cvtColor(marker, cv2.COLOR_GRAY2BGR)

    ok, encoded = cv2.imencode(".jpg", canvas)
    assert ok

    result = measure_images(encoded.tobytes(), config=MeasurementConfig(marker_size_mm=50))

    assert result["status"] == "measured"
    assert result["dimensions"]["length_mm"] == pytest.approx(300, abs=12)
    assert result["dimensions"]["width_mm"] == pytest.approx(200, abs=12)
    assert "aruco_reference_detected" in result["quality_flags"]


def test_no_marker_manual_box_uses_camera_distance_estimate():
    import cv2
    import numpy as np

    canvas = np.full((700, 1000, 3), 245, dtype=np.uint8)
    cv2.rectangle(canvas, (250, 170), (550, 370), (188, 190, 181), -1)
    cv2.rectangle(canvas, (250, 170), (550, 370), (45, 55, 49), 4)

    ok, encoded = cv2.imencode(".jpg", canvas)
    assert ok

    result = measure_images(
        encoded.tobytes(),
        config=MeasurementConfig(
            camera_distance_mm=1000,
            focal_length_35mm=45,
            top_box_points=[[250, 170], [550, 370]],
            manual_height_mm=90,
        ),
    )

    assert result["status"] == "measured"
    assert result["confidence"] == pytest.approx(0.78, abs=0.01)
    assert result["dimensions"]["length_mm"] == pytest.approx(240, abs=8)
    assert result["dimensions"]["width_mm"] == pytest.approx(160, abs=8)
    assert "camera_distance_manual_focal_scale_used" in result["quality_flags"]
    assert "manual_top_box_used" in result["quality_flags"]


def test_side_photo_can_estimate_height():
    import cv2
    import numpy as np

    top = np.full((700, 1000, 3), 255, dtype=np.uint8)
    side = np.full((520, 900, 3), 255, dtype=np.uint8)
    cv2.rectangle(top, (250, 150), (850, 550), (214, 211, 199), -1)
    cv2.rectangle(top, (250, 150), (850, 550), (45, 55, 49), 5)
    cv2.rectangle(side, (260, 180), (760, 340), (214, 211, 199), -1)
    cv2.rectangle(side, (260, 180), (760, 340), (45, 55, 49), 5)

    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    marker = cv2.aruco.generateImageMarker(dictionary, 0, 100)
    marker_bgr = cv2.cvtColor(marker, cv2.COLOR_GRAY2BGR)
    top[64:164, 72:172] = marker_bgr
    side[46:146, 70:170] = marker_bgr

    ok_top, top_encoded = cv2.imencode(".jpg", top)
    ok_side, side_encoded = cv2.imencode(".jpg", side)
    assert ok_top and ok_side

    result = measure_images(
        top_encoded.tobytes(),
        side_image_bytes=side_encoded.tobytes(),
        config=MeasurementConfig(
            marker_size_mm=50,
            side_box_points=[[260, 180], [760, 340]],
        ),
    )

    assert result["status"] == "measured"
    assert result["dimensions"]["height_mm"] == pytest.approx(80, abs=6)
    assert result["side_measurement"]["height_candidate_mm"] == pytest.approx(80, abs=6)
    assert "side_view_height_estimated" in result["quality_flags"]


def test_center_cardboard_box_wins_over_lower_clutter_without_marker():
    import cv2
    import numpy as np

    top = np.full((900, 700, 3), (214, 214, 198), dtype=np.uint8)
    cv2.rectangle(top, (180, 230), (545, 690), (92, 112, 160), -1)
    cv2.rectangle(top, (180, 230), (545, 690), (70, 62, 54), 3)
    cv2.rectangle(top, (250, 760), (680, 890), (38, 38, 42), -1)
    cv2.line(top, (260, 820), (690, 830), (15, 15, 15), 18)

    side = np.full((520, 900, 3), (212, 212, 198), dtype=np.uint8)
    cv2.rectangle(side, (110, 170), (790, 390), (92, 112, 160), -1)
    cv2.rectangle(side, (110, 170), (790, 390), (70, 62, 54), 3)

    ok_top, top_encoded = cv2.imencode(".jpg", top)
    ok_side, side_encoded = cv2.imencode(".jpg", side)
    assert ok_top and ok_side

    result = measure_images(
        top_encoded.tobytes(),
        side_image_bytes=side_encoded.tobytes(),
        config=MeasurementConfig(manual_height_mm=120),
    )

    assert result["status"] == "needs_reference"
    assert result["dimensions"]["length_mm"] == pytest.approx(370, abs=30)
    assert result["dimensions"]["width_mm"] == pytest.approx(295, abs=35)
    assert result["dimensions"]["height_mm"] == pytest.approx(120, abs=0.1)
    assert "cross_view_scale_estimate" in result["quality_flags"]
    assert result["top_view"]["box"]["candidate_kind"] == "cardboard_color"
    center_y = sum(point[1] for point in result["top_view"]["box"]["corners"]) / 4
    assert 350 < center_y < 560
