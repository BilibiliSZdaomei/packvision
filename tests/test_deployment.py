from fastapi.testclient import TestClient
from pathlib import Path

from packvision.app import create_app
from packvision.services.deployment import build_deployment_readiness


def test_deployment_readiness_reports_handoff_modes(tmp_path):
    readiness = build_deployment_readiness(vendor_root=tmp_path, package_root=tmp_path)

    assert readiness["max_handoff_mb"] == 100
    assert "image_only" in readiness["readiness_modes"]
    assert "depth_preinstall" in readiness["readiness_modes"]
    assert "camera_trial" in readiness["readiness_modes"]
    assert "overseas_handoff_package" in readiness["readiness_modes"]
    assert readiness["ai_plugins"]["base_package_policy"]["heavy_models_bundled"] is False
    assert readiness["target_warehouse_prepare_before_arrival"]
    repo_readiness = build_deployment_readiness(vendor_root=tmp_path)
    assert Path(repo_readiness["local_paths"]["readiness_script"]).exists()
    assert Path(repo_readiness["local_paths"]["handoff_package_script"]).exists()
    item_ids = {item["id"] for item in readiness["target_warehouse_prepare_before_arrival"]}
    assert "usb_data_cable" in item_ids
    assert "vendor_checkerboard_available" in item_ids
    assert readiness["arrival_handoff_sequence"][0]["step"] == 1


def test_deployment_readiness_endpoint_is_actionable():
    client = TestClient(create_app())
    response = client.get("/api/deployment/readiness")

    body = response.json()
    assert response.status_code == 200
    assert body["status"] in {"ready", "needs_attention"}
    assert body["summary"]["manual_required_count"] >= 1
    assert body["transfer_package"]["max_zip_mb"] == 100
    assert body["transfer_package"]["include_driver_installer_by_default"] is False
    assert any(check["id"] == "field_accessories" for check in body["checks"])


def test_deployment_readiness_summary_endpoint_keeps_workbench_payload_light():
    client = TestClient(create_app())
    response = client.get("/api/deployment/readiness-summary")

    body = response.json()
    assert response.status_code == 200
    assert body["status"] in {"ready", "needs_attention"}
    assert "summary" in body
    assert "readiness_modes" in body
    assert "hardware_status" not in body
    assert "capture_status" not in body
    assert "ai_plugins" not in body


def test_development_cycle_script_exists():
    assert Path("scripts/dev_cycle.ps1").exists()
