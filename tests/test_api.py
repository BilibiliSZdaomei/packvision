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


def test_favicon_endpoint_does_not_404():
    client = TestClient(create_app())
    response = client.get("/favicon.ico")

    assert response.status_code == 204


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
            "part_category": "filter",
            "package_hint": "carton",
            "actual_weight_kg": "3.2",
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "measured"
    assert body["measurement_id"]
    assert body["order_id"] == "SO-20260526-001"
    assert body["industry_profile"]["package_class"] == "standard_carton"
    assert body["industry_profile"]["chargeable_weight_kg"] >= 3.2
    assert body["created_at"]
    assert body["top_view"]["annotated_image_url"].startswith("/results/")
    assert "manual_height_used" in body["quality_flags"]

    history = client.get("/api/history", params={"order_id": "SO-20260526"})
    assert history.status_code == 200
    assert any(item["measurement_id"] == body["measurement_id"] for item in history.json()["items"])
    saved = next(item for item in history.json()["items"] if item["measurement_id"] == body["measurement_id"])
    assert saved["package_class"] == "standard_carton"
    assert saved["chargeable_weight_kg"] >= 3.2

    export = client.get("/api/history/export.csv", params={"order_id": "SO-20260526-001"})
    assert export.status_code == 200
    assert "package_class" in export.text
    assert "standard_carton" in export.text

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
def test_capture_quality_endpoint_flags_overexposed_upload():
    import cv2
    import numpy as np

    image = np.full((320, 420, 3), 255, dtype=np.uint8)
    ok, encoded = cv2.imencode(".jpg", image)
    assert ok

    client = TestClient(create_app())
    response = client.post(
        "/api/capture/quality",
        files={"image": ("bright.jpg", encoded.tobytes(), "image/jpeg")},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "review"
    assert "lighting_overexposed" in body["quality_flags"]


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


def test_depth_capture_capabilities_endpoint_reports_optional_backends():
    client = TestClient(create_app())
    response = client.get("/api/depth/capture/capabilities")

    body = response.json()
    assert response.status_code == 200
    assert "capture_backends" in body
    assert "pyorbbecsdk" in body["capture_backends"]
    assert "openni2_runtime_probe" in body["capture_backends"]
    assert body["recommended_capture_backend"] in {
        "pyorbbecsdk",
        "openni2_runtime_probe",
        "not_ready",
    }


def test_depth_capture_probe_endpoint_is_actionable_without_required_hardware():
    client = TestClient(create_app())
    response = client.post("/api/depth/capture/probe", json={"backend": "auto"})

    body = response.json()
    assert response.status_code == 200
    assert body["backend_requested"] == "auto"
    assert body["status"] in {
        "ready_for_capture",
        "driver_ready_capture_backend_missing",
        "capture_backend_missing",
        "hardware_validation_required",
    }
    assert isinstance(body["ready"], bool)
    assert body["next_actions"]
    assert body["next_action_keys"]


def test_depth_demo_object_endpoint_returns_measurement():
    client = TestClient(create_app())
    response = client.get("/api/depth/demo-object")

    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "measured"
    assert body["industry_profile"]["package_class"] == "irregular_or_soft_pack"
    assert body["history_saved"] is False
    assert body["measurement_id"]
    assert "depth_object_mask_used" in body["quality_flags"]


def test_depth_demo_object_save_persists_to_history():
    client = TestClient(create_app())
    response = client.post(
        "/api/depth/demo-object/save",
        json={
            "order_id": "DEPTH-DEMO-001",
            "barcode_text": "DEPTH-DEMO-001",
            "part_category": "bumper",
            "package_hint": "irregular",
            "actual_weight_kg": 5.2,
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["history_saved"] is True
    assert body["order_id"] == "DEPTH-DEMO-001"
    assert body["industry_profile"]["recommended_capture_mode"] == "depth_object_mask"

    history = client.get("/api/history", params={"order_id": "DEPTH-DEMO-001"})
    assert history.status_code == 200
    saved = next(item for item in history.json()["items"] if item["measurement_id"] == body["measurement_id"])
    assert saved["measurement_method"] == "depth_object_mask_projection"
    assert saved["package_class"] == "irregular_or_soft_pack"


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
            "save_to_history": True,
            "order_id": "DEPTH-ROI-001",
            "package_hint": "carton",
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["history_saved"] is True
    assert body["order_id"] == "DEPTH-ROI-001"
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


def test_industry_profile_endpoint_reports_abnormal_material_flow():
    client = TestClient(create_app())
    response = client.post(
        "/api/industry/profile",
        json={
            "dimensions": {
                "length_mm": 460,
                "width_mm": 300,
                "height_mm": 180,
                "volume_l": 24.84,
            },
            "part_category": "lamp",
            "package_hint": "carton",
            "material_hint": "transparent",
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["material_class"] == "transparent"
    assert body["material_risk_level"] == "high"
    assert "transparent_depth_dropout_risk" in body["handling_flags"]
    assert "material_surface_check" in body["workflow"]


def test_validation_trial_plan_endpoint_returns_site_plan():
    client = TestClient(create_app())
    response = client.get("/api/validation/trial-plan")

    body = response.json()
    assert response.status_code == 200
    assert body["minimum_total_samples"] >= 28
    assert any(item["id"] == "long_part" for item in body["scenarios"])


def test_validation_evaluate_endpoint_flags_failed_material_sample():
    client = TestClient(create_app())
    response = client.post(
        "/api/validation/evaluate",
        json={
            "samples": [
                {
                    "sample_id": "MAT-API-001",
                    "package_class": "standard_carton",
                    "material_class": "reflective",
                    "measured": {"length_mm": 450, "width_mm": 280, "height_mm": 160},
                    "truth": {"length_mm": 400, "width_mm": 280, "height_mm": 160},
                }
            ]
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["summary"]["failed_samples"] == 1
    assert "manual_review_required" in body["samples"][0]["flags"]


def test_validation_trial_template_csv_endpoint_is_excel_ready():
    client = TestClient(create_app())
    response = client.get("/api/validation/trial-template.csv")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "sample_id" in response.text
    assert "truth_length_mm" in response.text


def test_validation_evaluate_csv_endpoint_accepts_uploaded_csv():
    client = TestClient(create_app())
    csv_text = (
        "sample_id,order_id,package_class,material_class,measured_length_mm,measured_width_mm,"
        "measured_height_mm,truth_length_mm,truth_width_mm,truth_height_mm\n"
        "MAT-CSV-001,SO-CSV-001,standard_carton,transparent,450,300,170,400,300,200\n"
    )
    response = client.post(
        "/api/validation/evaluate-csv",
        files={"trial_csv": ("trial.csv", csv_text.encode("utf-8"), "text/csv")},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["summary"]["failed_samples"] == 1
    assert body["samples"][0]["sample_id"] == "MAT-CSV-001"
    assert body["samples"][0]["order_id"] == "SO-CSV-001"


def test_depth_workflow_guide_endpoint_returns_camera_arrival_plan():
    client = TestClient(create_app())
    response = client.get(
        "/api/depth/workflow-guide",
        params={"package_class": "long_part", "material_class": "reflective", "camera_count": 2},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["recommended_workflow"]["package_class"] == "long_part"
    assert "powered_usb_hub" in body["recommended_workflow"]["readiness_item_ids"]
    assert "reflective_surface_cross_check" in body["recommended_workflow"]["capture_step_ids"]
    assert body["guide"]["motherboard_required_now"] is False
