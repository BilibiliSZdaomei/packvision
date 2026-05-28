from fastapi.testclient import TestClient
from io import BytesIO
from PIL import Image, ImageDraw
import pytest
import time
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


def test_deployment_support_bundle_endpoint_returns_zip():
    client = TestClient(create_app())
    response = client.get("/api/deployment/support-bundle.zip")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    assert response.content.startswith(b"PK")


def test_field_trial_report_endpoints_return_evidence_summary():
    client = TestClient(create_app())
    response = client.get("/api/deployment/field-trial-report")

    assert response.status_code == 200
    body = response.json()
    assert body["report_type"] == "packvision_field_trial_report"
    assert "verdict" in body
    assert any(item["id"] == "local_app" for item in body["scorecard"])

    markdown = client.get("/api/deployment/field-trial-report.md")
    assert markdown.status_code == 200
    assert "PackVision 现场试运行报告" in markdown.text


def test_vendor_calibration_board_endpoint_uses_astra_reference_file():
    client = TestClient(create_app())
    response = client.get("/api/depth/vendor-calibration-board.pdf")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")


def test_vendor_viewer_open_endpoint_launches(monkeypatch):
    import packvision.app as app_module

    monkeypatch.setattr(
        app_module,
        "launch_vendor_viewer",
        lambda: {"status": "started", "tool": "OrbbecViewer", "pid": 1234, "path": r"D:\app\viewer.exe"},
    )

    client = TestClient(create_app())
    response = client.post("/api/depth/vendor-viewer/open")

    assert response.status_code == 200
    assert response.json()["status"] == "started"
    assert response.json()["tool"] == "OrbbecViewer"


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
    assert saved["actual_weight_kg"] == 3.2
    assert saved["volumetric_rule_id"] == "standard_6000"
    assert saved["volumetric_weight_kg"] is not None
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
    assert body["field_diagnosis"]["severity"] in {
        "ready",
        "waiting_for_camera",
        "validation_required",
        "action_required",
        "blocked",
    }
    assert body["field_diagnosis"]["primary_actions"]


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


def test_depth_measure_capture_auto_finds_foreground_without_worker_selection(monkeypatch):
    from packvision.services.depth_capture import DepthFrameBundle
    from packvision.services.depth_geometry import DepthIntrinsics

    def fake_capture(config):
        depth_frame = [[1000.0 for _ in range(10)] for _ in range(10)]
        for y in range(3, 7):
            for x in range(3, 8):
                depth_frame[y][x] = 760.0
        return DepthFrameBundle(
            depth_frame=depth_frame,
            intrinsics=DepthIntrinsics(fx=100, fy=100, cx=5, cy=5, width=10, height=10),
            backend="openni2_primesense",
            camera_id=config.camera_id or "astra-pro-top-01",
            role=config.role or "top",
            serial_number="fake-uri",
            frame_index=8,
        )

    monkeypatch.setattr("packvision.app.capture_depth_once", fake_capture)
    client = TestClient(create_app())
    order_id = f"DEPTH-AUTO-{uuid4().hex[:8]}"
    response = client.post(
        "/api/depth/measure-capture",
        json={"order_id": order_id, "save_to_history": True, "measurement_mode": "auto"},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["measurement_source"] == "depth_camera_capture"
    assert body["history_saved"] is True
    assert body["capture_regions"]["source"] == "auto_depth_foreground"
    assert body["capture_regions"]["roi"] == [2, 2, 9, 8]
    assert body["capture_regions"]["table_depth_mm"] == 1000.0
    assert body["dimensions"]["height_mm"] > 0
    assert body["camera_capture"]["frame_shape"] == {"height": 10, "width": 10}
    assert body["depth_evidence"]["saved"] is True
    assert body["depth_evidence"]["point_count"] == 20
    assert body["artifacts"]["depth_point_cloud_url"].endswith(".npz")
    assert body["artifacts"]["depth_preview_url"].endswith(".png")

    history = client.get("/api/history", params={"order_id": order_id})
    assert any(item["measurement_id"] == body["measurement_id"] for item in history.json()["items"])


def test_depth_live_stream_can_confirm_stable_candidate_without_hardware():
    client = TestClient(create_app())
    order_id = f"LIVE-{uuid4().hex[:8]}"
    try:
        start = client.post(
            "/api/depth/live/start",
            json={
                "backend": "simulated",
                "interval_ms": 50,
                "stable_required_frames": 2,
            },
        )
        assert start.status_code == 200

        state = {}
        for _ in range(30):
            state = client.get("/api/depth/live/state").json()
            if state.get("can_confirm"):
                break
            time.sleep(0.06)

        assert state["running"] is True
        assert state["status"] in {"stable_ready", "needs_review"}
        assert state["can_confirm"] is True
        assert state["stable_result"]["dimensions"]["length_mm"] > 0
        assert state["simulation_active"] is True
        assert state["uptime_seconds"] >= 0
        assert state["fps"] >= 0

        confirm = client.post(
            "/api/depth/live/confirm",
            json={"order_id": order_id, "barcode_text": order_id, "require_stable": True},
        )
        body = confirm.json()
        assert confirm.status_code == 200
        assert body["measurement_source"] == "depth_live_confirm"
        assert body["history_saved"] is True
        assert body["live_confirmation"]["confirmed_from"] == "depth_live_stream"
        assert body["artifacts"]["depth_point_cloud_url"].endswith(".npz")

        history = client.get("/api/history", params={"order_id": order_id})
        assert any(item["measurement_id"] == body["measurement_id"] for item in history.json()["items"])

        outbox = client.get("/api/integrations/outbox", params={"order_id": order_id})
        assert outbox.status_code == 200
        event = next(item for item in outbox.json()["items"] if item["measurement_id"] == body["measurement_id"])
        assert event["status"] == "pending"
        assert event["target"] == "wms_tms"
        assert event["payload"]["billing"]["chargeable_weight_kg"] == body["chargeable_weight_kg"]

        marked = client.post(
            f"/api/integrations/outbox/{event['event_id']}",
            json={"status": "failed", "error": "WMS test endpoint unavailable", "retry_after_seconds": 60},
        )
        assert marked.status_code == 200
        assert marked.json()["retry_count"] == 1

        exported = client.get("/api/integrations/outbox/export.csv")
        assert exported.status_code == 200
        assert "event_id,created_at,updated_at,next_attempt_at" in exported.text

        dispatch_status = client.get("/api/integrations/dispatch/status")
        assert dispatch_status.status_code == 200
        assert dispatch_status.json()["failure_behavior"] == "keep_event_in_outbox_and_retry_later"

        dispatch = client.post("/api/integrations/outbox/dispatch", json={"limit": 5})
        assert dispatch.status_code == 200
        assert dispatch.json()["status"] in {"not_configured", "no_due_events", "dispatched", "partial_failure"}
    finally:
        client.post("/api/depth/live/stop")


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


def test_depth_extrinsics_validate_endpoint_checks_three_view_rig():
    client = TestClient(create_app())
    response = client.post(
        "/api/depth/extrinsics/validate",
        json={
            "cameras": [
                {"camera_id": "top-01", "role": "top", "serial_hint": "TOP"},
                {
                    "camera_id": "front-01",
                    "role": "front",
                    "serial_hint": "FRONT",
                    "extrinsics": {"translation_mm": [0, -650, 420], "rotation_deg": [65, 0, 0]},
                },
                {
                    "camera_id": "side-01",
                    "role": "side",
                    "serial_hint": "SIDE",
                    "extrinsics": {"translation_mm": [-520, 0, 430], "rotation_deg": [65, 0, -90]},
                },
            ],
            "validation_measurements": [
                {"role": "top", "status": "measured", "confidence": 0.82, "dimensions": {"length_mm": 820, "width_mm": 320, "height_mm": 180}},
                {"role": "front", "status": "measured", "confidence": 0.8, "dimensions": {"length_mm": 825, "width_mm": 318, "height_mm": 182}},
                {"role": "side", "status": "measured", "confidence": 0.78, "dimensions": {"length_mm": 823, "width_mm": 322, "height_mm": 181}},
            ],
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "ready"
    assert body["rig"]["ready_for_three_view_validation"] is True
    assert body["conservative_policy"]["strategy"] == "conservative_max"


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

    truth_template = client.get("/api/review/truth-template.csv", params={"order_id": order_id})
    assert truth_template.status_code == 200
    assert "sample_id,order_id,package_class,material_class,measured_length_mm" in truth_template.text
    assert measured["measurement_id"] in truth_template.text
    assert "truth_length_mm" in truth_template.text


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
            "volumetric_rule_id": "express_5000",
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["package_class"] == "long_part"
    assert body["recommended_capture_mode"] == "depth_roi_long_item"
    assert body["volumetric_rule_id"] == "express_5000"
    assert body["billing_weight_source"] == "volumetric_weight"
    assert "oversize_length" in body["handling_flags"]


def test_volumetric_rule_endpoint_returns_default_rule_table():
    client = TestClient(create_app())
    response = client.get("/api/weight/volumetric-rules")

    body = response.json()
    assert response.status_code == 200
    assert body["default_rule_id"] == "standard_6000"
    assert {rule["rule_id"] for rule in body["rules"]} >= {"standard_6000", "express_5000", "economy_8000"}


def test_scale_status_endpoint_keeps_manual_fallback_available():
    client = TestClient(create_app())
    response = client.get("/api/scale/status")

    body = response.json()
    assert response.status_code == 200
    assert body["source"] == "manual_entry"
    assert body["status"] == "manual_ready"
    assert any(adapter["id"] == "manual_entry" and adapter["available"] for adapter in body["adapters"])


def test_device_watchdog_endpoint_reports_recovery_guidance():
    client = TestClient(create_app())
    response = client.get("/api/device/watchdog")

    body = response.json()
    assert response.status_code == 200
    assert body["status"]
    assert body["severity"] in {"ok", "warning", "critical"}
    assert "device_count" in body["signals"]
    assert body["photo_fallback_available"] is True
    assert isinstance(body["recovery_steps"], list)


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


def test_ai_plugin_endpoint_reports_lightweight_base_without_plugins(monkeypatch, tmp_path):
    monkeypatch.setenv("PACKVISION_AI_MODEL_ROOT", str(tmp_path))
    client = TestClient(create_app())
    response = client.get("/api/ai/plugins")

    body = response.json()
    assert response.status_code == 200
    assert body["base_package_policy"]["heavy_models_bundled"] is False
    assert body["summary"]["installed_count"] == 0
    assert body["plugins"] == []
    assert "manual_annotation_review" in body["fallback_chain"]


def test_station_snapshot_endpoint_reports_dws_orchestration_status():
    client = TestClient(create_app())
    response = client.get("/api/station/snapshot")

    body = response.json()
    assert response.status_code == 200
    assert body["architecture_decision"]["mode"] == "medium_upgrade_modular_monolith"
    assert [camera["role"] for camera in body["camera_monitor_layout"]] == ["top", "front", "side"]
    assert {item["id"] for item in body["dws_capabilities"]} >= {
        "dimensioning",
        "weighing",
        "scanning",
        "evidence",
        "integration",
        "device_health",
    }
    assert "wms_tms_push_and_retry_queue" in body["next_upgrade_tracks"]
    assert "device_watchdog" in body


def test_ai_plugin_endpoint_validates_optional_model_manifest(monkeypatch, tmp_path):
    plugin_dir = tmp_path / "packvision-yolo"
    plugin_dir.mkdir()
    (plugin_dir / "plugin.json").write_text(
        """
        {
          "id": "packvision-yolo-carton",
          "name": "PackVision carton detector",
          "version": "0.1.0",
          "enabled": true,
          "engine": "onnxruntime_cpu",
          "capabilities": ["box_detection", "oriented_box_detection"],
          "model_files": [{"path": "weights/model.onnx", "required": true}]
        }
        """,
        encoding="utf-8",
    )
    monkeypatch.setenv("PACKVISION_AI_MODEL_ROOT", str(tmp_path))
    client = TestClient(create_app())
    response = client.get("/api/ai/plugins")

    body = response.json()
    assert response.status_code == 200
    assert body["summary"]["installed_count"] == 1
    assert body["summary"]["attention_count"] == 1
    assert body["plugins"][0]["id"] == "packvision-yolo-carton"
    assert body["plugins"][0]["status"] == "needs_attention"
    assert body["plugins"][0]["issues"][0]["code"] == "missing_model_file"


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
