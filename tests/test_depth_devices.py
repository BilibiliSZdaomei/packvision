from packvision.services import depth_devices
from packvision.services.depth_devices import (
    astra_depth_intrinsics_from_fov,
    build_depth_camera_inventory,
    load_depth_camera_config,
)


def test_default_depth_camera_config_is_single_astra_top_camera(tmp_path, monkeypatch):
    monkeypatch.setenv("PACKVISION_DEPTH_CAMERA_CONFIG", str(tmp_path / "missing.json"))
    monkeypatch.setenv("PACKVISION_ASTRA_ROOT", str(tmp_path / "vendor"))

    config = load_depth_camera_config()

    assert config["config_source"] == "generated_default"
    assert config["default_camera_id"] == "astra-pro-top-01"
    assert config["cameras"][0]["role"] == "top"
    assert config["cameras"][0]["backend"] == "openni2_primesense"
    assert config["target_camera_count"] == 1


def test_astra_depth_intrinsics_are_derived_from_datasheet_fov():
    intrinsics = astra_depth_intrinsics_from_fov(640, 480)

    assert intrinsics["fx"] > 550
    assert intrinsics["fy"] > 550
    assert intrinsics["cx"] == 320.0
    assert "factory_camera_info_preferred" in intrinsics["quality_flags"]


def test_depth_camera_inventory_marks_future_three_view_roles(tmp_path, monkeypatch):
    config_path = tmp_path / "depth-cameras.json"
    config_path.write_text(
        """
        {
          "version": 1,
          "target_camera_count": 3,
          "default_camera_id": "top",
          "cameras": [
            {"camera_id": "top", "role": "top", "enabled": true, "runtime_dir": "D:/runtime"},
            {"camera_id": "front", "role": "front", "enabled": true, "runtime_dir": "D:/runtime"},
            {"camera_id": "left", "role": "left", "enabled": true, "runtime_dir": "D:/runtime"}
          ]
        }
        """,
        encoding="utf-8",
    )
    monkeypatch.setenv("PACKVISION_DEPTH_CAMERA_CONFIG", str(config_path))
    monkeypatch.setattr(
        depth_devices,
        "enumerate_openni_devices",
        lambda runtime_dir=None: {
            "backend": "openni2_primesense",
            "python_package_available": True,
            "runtime_dir": str(runtime_dir),
            "runtime_dir_exists": True,
            "runtime_initialized": True,
            "device_count": 3,
            "devices": [{"index": 0, "uri": "uri0"}, {"index": 1, "uri": "uri1"}, {"index": 2, "uri": "uri2"}],
            "error": None,
        },
    )

    inventory = build_depth_camera_inventory()

    assert inventory["configured_camera_count"] == 3
    assert inventory["ready_for_three_view_fusion"] is True
    assert inventory["missing_three_view_roles"] == []
