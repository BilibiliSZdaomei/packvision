from fastapi.testclient import TestClient
import pytest

from packvision.app import create_app
from packvision.services.measurement import opencv_ready


def test_health_endpoint_reports_runtime():
    client = TestClient(create_app())
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["ok"] is True


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
