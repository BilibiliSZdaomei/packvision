from fastapi.testclient import TestClient
from io import BytesIO
from PIL import Image, ImageDraw
import pytest
from uuid import uuid4

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
def test_measure_endpoint_auto_material_signal_when_worker_does_not_choose_material():
    import cv2
    import numpy as np

    image = np.full((360, 480, 3), 255, dtype=np.uint8)
    ok, encoded = cv2.imencode(".jpg", image)
    assert ok

    client = TestClient(create_app())
    response = client.post(
        "/api/measure",
        files={"top_image": ("glare.jpg", encoded.tobytes(), "image/jpeg")},
        data={
            "manual_height_mm": "120",
            "camera_distance_mm": "1000",
            "focal_length_35mm": "35",
            "top_box_json": "[[80, 80], [360, 260]]",
            "order_id": "AUTO-MAT-001",
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["material_hint"] == "reflective"
    assert body["material_hint_source"] == "capture_quality"
    assert body["industry_profile"]["material_class"] == "reflective"
    assert body["industry_profile"]["material_hint_source"] == "capture_quality"
    assert "reflective_depth_noise_risk" in body["industry_profile"]["handling_flags"]


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
    assert "vendor_profile" in body
    assert body["calibration_strategy"]["warehouse_worker"] == "No manual focal length, aperture, or intrinsic entry."


def test_depth_vendor_profile_endpoint_prefers_vendor_camera_info():
    client = TestClient(create_app())
    response = client.get("/api/depth/vendor-profile")

    body = response.json()
    assert response.status_code == 200
    assert body["hardware_profile"]["model"] == "Orbbec Astra Pro"
    assert "/camera/depth/camera_info" in body["ros_interfaces"]["camera_info_topics"]
    assert body["vendor_first_calibration_strategy"]["warehouse_worker"]
    assert body["tutorial_playbook"]["multi_camera_playbook"]["vendor_commands"]["cleanup_shared_memory"]


def test_depth_astra_tutorial_playbook_endpoint_maps_missed_vendor_controls():
    client = TestClient(create_app())
    response = client.get("/api/depth/astra/tutorial-playbook")

    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "reviewed_and_project_mapped"
    services = [
        control["service"]
        for group in body["control_catalog"]
        for control in group["controls"]
    ]
    launch_params = [item["name"] for item in body["launch_parameter_catalog"]]
    assert "/camera/set_ir_exposure" in services
    assert "/camera/set_depth_mirror" in services
    assert "device_num" in launch_params
    assert "depth_registration" in launch_params
    assert body["multi_camera_playbook"]["vendor_commands"]["cleanup_shared_memory"].endswith("cleanup_shm_node")
    assert body["calibration_contract"]["warehouse_worker_policy"].startswith("Workers never")


def test_depth_camera_info_normalize_accepts_ros_camera_info():
    client = TestClient(create_app())
    response = client.post(
        "/api/depth/camera-info/normalize",
        json={
            "stream": "depth",
            "depth_scale": 1.0,
            "camera_info": {
                "width": 640,
                "height": 480,
                "camera_name": "ir_camera",
                "k": [517.3, 0, 326.8, 0, 519.2, 244.6, 0, 0, 1],
                "d": [-0.4, 0.3, 0.0, 0.0, 0.0],
                "distortion_model": "plumb_bob",
            },
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["source"] == "ros_camera_info_topic"
    assert body["intrinsics"]["fx"] == 517.3
    assert body["intrinsics"]["width"] == 640
    assert "manual_intrinsics_not_required" in body["quality_flags"]


def test_depth_camera_info_normalize_accepts_get_camera_info_service_shape():
    client = TestClient(create_app())
    response = client.post(
        "/api/depth/camera-info/normalize",
        json={
            "stream": "depth",
            "camera_info": {
                "success": True,
                "message": "",
                "info": {
                    "width": 640,
                    "height": 480,
                    "camera_name": "ir_camera",
                    "k": [517.3, 0, 326.8, 0, 519.2, 244.6, 0, 0, 1],
                },
            },
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["intrinsics"]["cy"] == 244.6


def test_depth_camera_info_normalize_accepts_calibration_yaml_shape():
    client = TestClient(create_app())
    response = client.post(
        "/api/depth/camera-info/normalize",
        json={
            "stream": "color",
            "camera_info": {
                "image_width": 1280,
                "image_height": 720,
                "camera_name": "rgb_camera",
                "camera_matrix": {
                    "rows": 3,
                    "cols": 3,
                    "data": [900.0, 0, 640.0, 0, 902.0, 360.0, 0, 0, 1],
                },
            },
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["source"] == "ros_calibration_yaml"
    assert body["intrinsics"]["fy"] == 902.0
    assert body["intrinsics"]["height"] == 720


def test_depth_capture_capabilities_endpoint_reports_optional_backends():
    client = TestClient(create_app())
    response = client.get("/api/depth/capture/capabilities")

    body = response.json()
    assert response.status_code == 200
    assert "capture_backends" in body
    assert "pyorbbecsdk" in body["capture_backends"]
    assert "openni2_primesense" in body["capture_backends"]
    assert "openni2_runtime_probe" in body["capture_backends"]
    assert body["recommended_capture_backend"] in {
        "pyorbbecsdk",
        "openni2_primesense",
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
        "openni_runtime_ready_no_device",
    }
    assert isinstance(body["ready"], bool)
    assert body["next_actions"]
    assert body["next_action_keys"]


def test_depth_cameras_endpoint_returns_configured_rig():
    client = TestClient(create_app())
    response = client.get("/api/depth/cameras")

    body = response.json()
    assert response.status_code == 200
    assert body["configured_camera_count"] >= 1
    assert "required_three_view_roles" in body
    assert body["upgrade_path"]["three_camera_target"]
    assert body["ros2_multi_camera"]["cleanup_command"] == "ros2 run astra_camera cleanup_shm_node"
    assert body["cameras"][0]["ros2_profile"]["operator_policy"]["measurement_mode"] == "auto"


def test_depth_capture_frame_endpoint_returns_captured_frame_without_hardware(monkeypatch):
    from packvision.services.depth_capture import DepthFrameBundle
    from packvision.services.depth_geometry import DepthIntrinsics

    def fake_capture(config):
        return DepthFrameBundle(
            depth_frame=[[1000.0, 1001.0], [999.0, 1002.0]],
            intrinsics=DepthIntrinsics(fx=100, fy=100, cx=1, cy=1, width=2, height=2),
            backend="openni2_primesense",
            camera_id=config.camera_id or "astra-pro-top-01",
            role=config.role or "top",
            serial_number="fake-uri",
            frame_index=7,
        )

    monkeypatch.setattr("packvision.app.capture_depth_once", fake_capture)
    client = TestClient(create_app())
    response = client.post("/api/depth/capture/frame", json={"include_frame": False})

    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "captured"
    assert body["frame_shape"] == {"height": 2, "width": 2}
    assert "depth_frame" not in body
    assert body["camera_id"] == "astra-pro-top-01"


def test_depth_fuse_measurements_endpoint_saves_traceable_result():
    client = TestClient(create_app())
    response = client.post(
        "/api/depth/fuse-measurements",
        json={
            "order_id": "MV-001",
            "part_category": "bumper",
            "package_hint": "irregular",
            "view_measurements": [
                {
                    "view_id": "top",
                    "role": "top",
                    "status": "measured",
                    "confidence": 0.82,
                    "dimensions": {"length_mm": 900, "width_mm": 240, "height_mm": 160},
                },
                {
                    "view_id": "front",
                    "role": "front",
                    "status": "measured",
                    "confidence": 0.78,
                    "dimensions": {"length_mm": 910, "width_mm": 250, "height_mm": 170},
                },
            ],
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["measurement_source"] == "depth_multi_view_fusion"
    assert body["order_id"] == "MV-001"
    assert body["dimensions"]["length_mm"] == 910.0
    assert "multi_view_fusion" in body["quality_flags"]


def test_review_samples_collects_low_confidence_and_view_conflicts():
    client = TestClient(create_app())
    order_id = f"RV-{uuid4().hex[:8]}"
    response = client.post(
        "/api/depth/fuse-measurements",
        json={
            "order_id": order_id,
            "part_category": "bumper",
            "package_hint": "irregular",
            "save_to_history": True,
            "view_measurements": [
                {
                    "view_id": "top",
                    "role": "top",
                    "status": "measured",
                    "confidence": 0.54,
                    "dimensions": {"length_mm": 980, "width_mm": 260, "height_mm": 155},
                    "quality_flags": ["depth_hole_risk"],
                    "recommendation_codes": ["retake_depth_with_less_reflection"],
                },
                {
                    "view_id": "front",
                    "role": "front",
                    "status": "measured",
                    "confidence": 0.49,
                    "dimensions": {"length_mm": 710, "width_mm": 255, "height_mm": 150},
                },
            ],
        },
    )

    measured = response.json()
    assert response.status_code == 200
    assert measured["history_saved"] is True
    assert measured["status"] == "review"

    review = client.get("/api/review/samples", params={"order_id": order_id})
    body = review.json()
    assert review.status_code == 200
    assert body["summary"]["total_review_samples"] == 1
    assert body["items"][0]["measurement_id"] == measured["measurement_id"]
    assert body["items"][0]["priority"] in {"critical", "high"}
    assert "view_disagreement_risk" in body["items"][0]["review_reasons"]
    assert "low_confidence" in body["items"][0]["review_reasons"]

    export = client.get("/api/review/export.csv", params={"order_id": order_id})
    assert export.status_code == 200
    assert "measurement_id,created_at,order_id,status,priority" in export.text
    assert order_id in export.text


def test_depth_quality_endpoint_flags_sparse_synthetic_frame():
    client = TestClient(create_app())
    depth = [[0.0 for _ in range(8)] for _ in range(8)]
    for y in range(2, 6):
        for x in range(2, 4):
            depth[y][x] = 800.0

    response = client.post(
        "/api/depth/quality",
        json={
            "depth_frame": depth,
            "roi": [2, 2, 6, 6],
            "min_valid_depth_mm": 50,
            "max_valid_depth_mm": 6000,
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "review"
    assert "depth_hole_risk" in body["quality_flags"]


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


def test_depth_simulate_from_image_endpoint_runs_astra_dry_run():
    client = TestClient(create_app())
    image = Image.new("RGB", (320, 220), (176, 170, 155))
    draw = ImageDraw.Draw(image)
    draw.rectangle([55, 45, 265, 175], fill=(205, 198, 170), outline=(90, 78, 55), width=4)
    draw.ellipse([90, 70, 230, 160], fill=(35, 95, 170), outline=(20, 50, 90), width=3)
    buffer = BytesIO()
    image.save(buffer, format="PNG")

    response = client.post(
        "/api/depth/simulate-from-image",
        files={"image": ("sample.png", buffer.getvalue(), "image/png")},
        data={
            "table_depth_mm": "1200",
            "object_depth_mm": "850",
            "part_category": "simulation_fixture",
            "source_url": "https://clubs.github.io/gif/box_000.gif",
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["measurement_source"] == "depth_simulated_real_image"
    assert body["dimensions"]["height_mm"] == pytest.approx(350.0, abs=8.0)
    assert body["simulation"]["mode"] == "real_image_plus_synthetic_astra_depth"
    assert "real_rgb_image_used" in body["quality_flags"]
    assert body["artifacts"]["simulation_overlay_url"].startswith("/results/")


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


def test_depth_measure_object_endpoint_accepts_principal_axis_footprint():
    client = TestClient(create_app())
    depth = [[1000.0 for _ in range(12)] for _ in range(12)]
    for y in range(2, 10):
        for x in range(2, 10):
            if abs(x - y) <= 1:
                depth[y][x] = 760.0

    response = client.post(
        "/api/depth/measure-object",
        json={
            "depth_frame": depth,
            "intrinsics": {
                "fx": 100.0,
                "fy": 100.0,
                "cx": 6.0,
                "cy": 6.0,
                "width": 12,
                "height": 12,
            },
            "roi": [1, 1, 11, 11],
            "background_roi": [0, 0, 1, 1],
            "object_min_height_mm": 80,
            "trim_quantile": 0.0,
            "footprint_method": "principal_axes",
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["depth"]["footprint_method"] == "principal_axes"
    assert body["depth"]["orientation_deg"] == pytest.approx(45.0, abs=1.0)
    assert "principal_axis_extent_used" in body["quality_flags"]


def test_usage_summary_counts_depth_measurement_calls():
    client = TestClient(create_app())
    before = client.get("/api/usage/summary").json()
    before_measurements = before["measurement_calls"]
    before_endpoint_calls = _endpoint_call_count(before, "/api/depth/measure-roi")

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
    assert response.status_code == 200

    after = client.get("/api/usage/summary").json()
    assert after["measurement_calls"] == before_measurements + 1
    assert _endpoint_call_count(after, "/api/depth/measure-roi") == before_endpoint_calls + 1


def test_usage_events_and_export_include_api_call_logs():
    client = TestClient(create_app())
    depth = [[0.0 for _ in range(8)] for _ in range(8)]
    for y in range(2, 6):
        for x in range(2, 4):
            depth[y][x] = 800.0

    response = client.post(
        "/api/depth/quality",
        json={
            "depth_frame": depth,
            "roi": [2, 2, 6, 6],
            "min_valid_depth_mm": 50,
            "max_valid_depth_mm": 6000,
        },
    )
    assert response.status_code == 200

    events = client.get("/api/usage/events", params={"limit": 5, "endpoint": "/api/depth/quality"})
    assert events.status_code == 200
    items = events.json()["items"]
    assert items
    assert items[0]["endpoint"] == "/api/depth/quality"
    assert items[0]["success"] is True

    export = client.get("/api/usage/export.csv", params={"endpoint": "/api/depth/quality"})
    assert export.status_code == 200
    assert "endpoint" in export.text
    assert "/api/depth/quality" in export.text


def test_usage_events_link_successful_measurements_to_order_and_measurement_id():
    client = TestClient(create_app())
    order_id = f"USAGE-TRACE-{uuid4().hex[:8]}"
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
            "order_id": order_id,
            "package_hint": "carton",
        },
    )

    body = response.json()
    assert response.status_code == 200
    events = client.get("/api/usage/events", params={"limit": 50, "endpoint": "/api/depth/measure-roi"})
    matching = [
        item
        for item in events.json()["items"]
        if item["measurement_id"] == body["measurement_id"]
    ]
    assert matching
    assert matching[0]["order_id"] == order_id
    assert matching[0]["measurement_source"] == "depth_roi_api"


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


def _endpoint_call_count(summary: dict[str, object], endpoint: str) -> int:
    by_endpoint = summary.get("by_endpoint") or []
    for item in by_endpoint:
        if item["endpoint"] == endpoint:
            return int(item["call_count"])
    return 0
