from fastapi.testclient import TestClient
import pytest

from packvision.app import create_app
from packvision.services.measurement import opencv_ready


def test_health_endpoint_reports_runtime():
    client = TestClient(create_app())
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert "depth_camera" in response.json()


@pytest.mark.skipif(not opencv_ready(), reason="OpenCV ArUco is unavailable")
def test_demo_image_endpoint_returns_jpeg():
    client = TestClient(create_app())
    response = client.get("/api/demo-image.jpg")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"
    assert response.content.startswith(b"\xff\xd8")


@pytest.mark.skipif(not opencv_ready(), reason="OpenCV ArUco is unavailable")
def test_measure_endpoint_accepts_demo_image():
    client = TestClient(create_app())
    demo = client.get("/api/demo-image.jpg")

    response = client.post(
        "/api/measure",
        files={"top_image": ("demo.jpg", demo.content, "image/jpeg")},
        data={
            "marker_size_mm": "50",
            "manual_height_mm": "120",
            "order_id": "SO-20260526-001",
            "barcode_text": "SO-20260526-001",
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "measured"
    assert body["measurement_id"]
    assert body["order_id"] == "SO-20260526-001"
    assert body["created_at"]
    assert body["top_view"]["annotated_image_url"].startswith("/results/")
    assert "manual_height_used" in body["quality_flags"]

    history = client.get("/api/history", params={"order_id": "SO-20260526"})
    assert history.status_code == 200
    assert any(item["measurement_id"] == body["measurement_id"] for item in history.json()["items"])

    detail = client.get(f"/api/history/{body['measurement_id']}")
    assert detail.status_code == 200
    assert detail.json()["measurement_id"] == body["measurement_id"]


def test_order_scan_endpoint_normalizes_payload():
    client = TestClient(create_app())
    response = client.post("/api/orders/scan", json={"barcode_text": "  PKG-7788  "})

    assert response.status_code == 200
    assert response.json()["order_id"] == "PKG-7788"
    assert response.json()["barcode_text"] == "PKG-7788"


@pytest.mark.skipif(not opencv_ready(), reason="OpenCV is unavailable")
def test_decode_order_image_endpoint_accepts_image():
    client = TestClient(create_app())
    demo = client.get("/api/demo-image.jpg")

    response = client.post(
        "/api/orders/decode-image",
        files={"order_image": ("demo.jpg", demo.content, "image/jpeg")},
    )

    assert response.status_code == 200
    assert "codes" in response.json()


def test_depth_status_endpoint_reports_vendor_assets():
    client = TestClient(create_app())
    response = client.get("/api/depth/status")

    body = response.json()
    assert response.status_code == 200
    assert "recommended_backend" in body
    assert "openni2" in body


def test_depth_measure_roi_endpoint_accepts_synthetic_frame():
    client = TestClient(create_app())
    depth = [[1000.0 for _ in range(8)] for _ in range(8)]
    for y in range(2, 6):
        for x in range(2, 6):
            depth[y][x] = 800.0

    response = client.post(
        "/api/depth/measure-roi",
        json={
            "depth_frame": depth,
            "intrinsics": {
                "fx": 100.0,
                "fy": 100.0,
                "cx": 4.0,
                "cy": 4.0,
                "width": 8,
                "height": 8,
            },
            "roi": [2, 2, 6, 6],
            "background_roi": [0, 0, 2, 2],
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["dimensions"]["length_mm"] == pytest.approx(32.0)
    assert body["dimensions"]["height_mm"] == pytest.approx(200.0)


def test_depth_measure_object_endpoint_accepts_synthetic_frame():
    client = TestClient(create_app())
    depth = [[1000.0 for _ in range(10)] for _ in range(10)]
    for y in range(3, 7):
        for x in range(2, 8):
            depth[y][x] = 760.0

    response = client.post(
        "/api/depth/measure-object",
        json={
            "depth_frame": depth,
            "intrinsics": {
                "fx": 100.0,
                "fy": 100.0,
                "cx": 5.0,
                "cy": 5.0,
                "width": 10,
                "height": 10,
            },
            "roi": [1, 2, 9, 8],
            "background_roi": [0, 0, 2, 2],
            "object_min_height_mm": 50,
            "trim_quantile": 0,
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["dimensions"]["height_mm"] == pytest.approx(240.0)
    assert body["depth"]["object_pixel_count"] == 24
    assert "depth_object_mask_used" in body["quality_flags"]


def test_industry_profile_endpoint_classifies_auto_parts_package():
    client = TestClient(create_app())
    response = client.post(
        "/api/industry/profile",
        json={
            "dimensions": {
                "length_mm": 1300,
                "width_mm": 180,
                "height_mm": 120,
                "volume_l": 28.08,
            },
            "part_category": "shock_absorber",
            "package_hint": "long_part",
            "actual_weight_kg": 4.1,
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["package_class"] == "long_part"
    assert body["recommended_capture_mode"] == "depth_roi_long_item"
    assert "oversize_length" in body["handling_flags"]
