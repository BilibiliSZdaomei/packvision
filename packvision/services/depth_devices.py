from __future__ import annotations

import importlib.util
import json
import math
import os
from pathlib import Path
from typing import Any

from packvision.services.astra_vendor import ASTRA_PRO_SPECS, resolve_astra_root


DEFAULT_INSTALL_ROOT = Path(r"D:\app\orbbec-astra-pro")
DEFAULT_CAMERA_CONFIG_PATH = DEFAULT_INSTALL_ROOT / "packvision-depth-cameras.json"
CAMERA_ROLES = ("top", "front", "left", "right", "back", "aux")
THREE_VIEW_ROLES = ("top", "front", "left")


class DepthDeviceError(RuntimeError):
    pass


def default_openni_runtime_dir(vendor_root: str | Path | None = None) -> Path:
    root = resolve_astra_root(vendor_root)
    return root / "上位机软件" / "上位机软件"


def default_depth_camera_config_path() -> Path:
    configured = os.environ.get("PACKVISION_DEPTH_CAMERA_CONFIG")
    return Path(configured) if configured else DEFAULT_CAMERA_CONFIG_PATH


def astra_depth_intrinsics_from_fov(
    width: int = 640,
    height: int = 480,
    *,
    depth_scale: float = 1.0,
) -> dict[str, Any]:
    depth_fov = ASTRA_PRO_SPECS["depth_fov"]
    fx = width / (2.0 * math.tan(math.radians(float(depth_fov["horizontal_deg"])) / 2.0))
    fy = height / (2.0 * math.tan(math.radians(float(depth_fov["vertical_deg"])) / 2.0))
    return {
        "fx": round(fx, 3),
        "fy": round(fy, 3),
        "cx": round(width / 2.0, 3),
        "cy": round(height / 2.0, 3),
        "width": int(width),
        "height": int(height),
        "depth_scale": float(depth_scale),
        "source": "astra_pro_datasheet_depth_fov_estimate",
        "quality_flags": ["factory_camera_info_preferred", "field_validation_required"],
    }


def build_default_depth_camera_config(vendor_root: str | Path | None = None) -> dict[str, Any]:
    root = resolve_astra_root(vendor_root)
    runtime_dir = default_openni_runtime_dir(root)
    return {
        "version": 1,
        "rig_id": "packvision-astra-pro-rig",
        "target_camera_count": 1,
        "default_camera_id": "astra-pro-top-01",
        "cameras": [
            {
                "camera_id": "astra-pro-top-01",
                "role": "top",
                "enabled": True,
                "backend": "openni2_primesense",
                "model": "Orbbec Astra Pro",
                "serial_hint": None,
                "vendor_root": str(root),
                "runtime_dir": str(runtime_dir),
                "mount": {
                    "pose": "top_down",
                    "purpose": "single-camera warehouse measurement and first hardware validation",
                },
                "intrinsics": astra_depth_intrinsics_from_fov(640, 480),
            }
        ],
        "future_ready_roles": list(THREE_VIEW_ROLES),
        "fusion_policy": {
            "strategy": "conservative_max",
            "minimum_views_for_auto_accept": 1,
            "target_views_for_three_view": 3,
            "disagreement_ratio": 0.12,
            "notes": [
                "Astra Pro starts as a single top camera.",
                "Add front and left/right cameras later without changing measurement APIs.",
                "Conservative max fusion avoids under-reporting shipping dimensions.",
            ],
        },
    }


def load_depth_camera_config(config_path: str | Path | None = None) -> dict[str, Any]:
    path = Path(config_path) if config_path else default_depth_camera_config_path()
    if path.exists():
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise DepthDeviceError(f"Unable to read depth camera config: {path}") from exc
        source = "file"
    else:
        raw = build_default_depth_camera_config()
        source = "generated_default"

    return _normalize_depth_camera_config(raw, path, source)


def build_depth_camera_inventory(config_path: str | Path | None = None) -> dict[str, Any]:
    config = load_depth_camera_config(config_path)
    enabled_cameras = [camera for camera in config["cameras"] if camera["enabled"]]
    runtime_dir = _first_runtime_dir(enabled_cameras)
    openni_probe = enumerate_openni_devices(runtime_dir)
    detected_count = int(openni_probe.get("device_count") or 0)

    configured = []
    for index, camera in enumerate(enabled_cameras):
        connected = False
        serial_hint = camera.get("serial_hint")
        if serial_hint:
            connected = any(serial_hint in str(device.get("uri") or "") for device in openni_probe["devices"])
        elif detected_count == 1 and len(enabled_cameras) == 1:
            connected = True
        elif detected_count > index:
            connected = True
        configured.append(
            {
                **camera,
                "connected_candidate": connected,
                "connection_note": _connection_note(camera, connected, detected_count),
            }
        )

    roles = [camera["role"] for camera in enabled_cameras]
    missing_three_view_roles = [role for role in THREE_VIEW_ROLES if role not in roles]
    return {
        "config": config,
        "configured_camera_count": len(enabled_cameras),
        "target_camera_count": config["target_camera_count"],
        "configured_roles": roles,
        "required_three_view_roles": list(THREE_VIEW_ROLES),
        "missing_three_view_roles": missing_three_view_roles,
        "ready_for_single_camera_capture": detected_count >= 1 and bool(enabled_cameras),
        "ready_for_three_view_fusion": len(missing_three_view_roles) == 0 and detected_count >= 3,
        "openni_probe": openni_probe,
        "cameras": configured,
        "upgrade_path": {
            "single_camera_now": "Use top Astra Pro capture for cartons, long parts, and irregular masks.",
            "two_camera_next": "Add a front or side camera for height/silhouette cross-checks.",
            "three_camera_target": "Top + front + left/right views enable conservative fusion for bulky irregular parts.",
            "better_camera_later": "Keep the same camera_id/role contract and swap backend/model per device.",
        },
    }


def enumerate_openni_devices(runtime_dir: str | Path | None = None) -> dict[str, Any]:
    runtime = Path(runtime_dir) if runtime_dir else default_openni_runtime_dir()
    result: dict[str, Any] = {
        "backend": "openni2_primesense",
        "python_package_available": importlib.util.find_spec("primesense") is not None,
        "runtime_dir": str(runtime),
        "runtime_dir_exists": runtime.exists(),
        "runtime_initialized": False,
        "device_count": 0,
        "devices": [],
        "error": None,
    }
    if not result["python_package_available"]:
        result["error"] = "Python package primesense is not installed."
        return result
    if not runtime.exists():
        result["error"] = f"OpenNI runtime directory does not exist: {runtime}"
        return result

    try:
        from primesense import openni2  # type: ignore[import-not-found]

        openni2.initialize(str(runtime))
        result["runtime_initialized"] = True
        uris = openni2.Device.enumerate_uris()
        result["devices"] = [
            {
                "index": index,
                "uri": _stringify_uri(uri),
                "role_match": _role_hint_from_index(index),
            }
            for index, uri in enumerate(uris)
        ]
        result["device_count"] = len(result["devices"])
    except Exception as exc:  # pragma: no cover - depends on vendor runtime and hardware
        result["error"] = str(exc)
    finally:
        try:
            from primesense import openni2  # type: ignore[import-not-found]

            if result["runtime_initialized"]:
                openni2.unload()
        except Exception:
            pass
    return result


def camera_config_by_id_or_role(
    camera_id: str | None = None,
    role: str | None = None,
    *,
    config_path: str | Path | None = None,
) -> dict[str, Any]:
    config = load_depth_camera_config(config_path)
    cameras = [camera for camera in config["cameras"] if camera["enabled"]]
    if camera_id:
        for camera in cameras:
            if camera["camera_id"] == camera_id:
                return camera
        raise DepthDeviceError(f"Unknown depth camera_id: {camera_id}")
    if role:
        normalized_role = _normalize_role(role, "top")
        for camera in cameras:
            if camera["role"] == normalized_role:
                return camera
        raise DepthDeviceError(f"No enabled depth camera configured for role: {normalized_role}")
    if not cameras:
        raise DepthDeviceError("No enabled depth camera is configured.")
    default_id = config.get("default_camera_id")
    for camera in cameras:
        if camera["camera_id"] == default_id:
            return camera
    return cameras[0]


def _normalize_depth_camera_config(raw: dict[str, Any], path: Path, source: str) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise DepthDeviceError("Depth camera config must be a JSON object.")
    cameras_raw = raw.get("cameras")
    if not isinstance(cameras_raw, list) or not cameras_raw:
        cameras_raw = build_default_depth_camera_config().get("cameras", [])

    cameras = []
    for index, item in enumerate(cameras_raw):
        if not isinstance(item, dict):
            continue
        role = _normalize_role(item.get("role"), _role_hint_from_index(index))
        vendor_root = Path(item.get("vendor_root") or resolve_astra_root())
        runtime_dir = Path(item.get("runtime_dir") or default_openni_runtime_dir(vendor_root))
        intrinsics = item.get("intrinsics") if isinstance(item.get("intrinsics"), dict) else {}
        width = int(intrinsics.get("width") or 640)
        height = int(intrinsics.get("height") or 480)
        default_intrinsics = astra_depth_intrinsics_from_fov(width, height)
        default_intrinsics.update({key: value for key, value in intrinsics.items() if value is not None})
        cameras.append(
            {
                "camera_id": str(item.get("camera_id") or f"depth-camera-{index + 1:02d}"),
                "role": role,
                "enabled": bool(item.get("enabled", True)),
                "backend": str(item.get("backend") or "openni2_primesense"),
                "model": str(item.get("model") or "Orbbec Astra Pro"),
                "serial_hint": item.get("serial_hint"),
                "vendor_root": str(vendor_root),
                "runtime_dir": str(runtime_dir),
                "mount": item.get("mount") if isinstance(item.get("mount"), dict) else {},
                "intrinsics": default_intrinsics,
            }
        )

    target_camera_count = int(raw.get("target_camera_count") or len(cameras) or 1)
    return {
        "version": int(raw.get("version") or 1),
        "rig_id": str(raw.get("rig_id") or "packvision-depth-rig"),
        "config_path": str(path),
        "config_source": source,
        "config_path_exists": path.exists(),
        "target_camera_count": max(1, target_camera_count),
        "default_camera_id": str(raw.get("default_camera_id") or cameras[0]["camera_id"]),
        "cameras": cameras,
        "future_ready_roles": list(raw.get("future_ready_roles") or THREE_VIEW_ROLES),
        "fusion_policy": raw.get("fusion_policy") if isinstance(raw.get("fusion_policy"), dict) else {},
    }


def _first_runtime_dir(cameras: list[dict[str, Any]]) -> str | None:
    for camera in cameras:
        runtime_dir = camera.get("runtime_dir")
        if runtime_dir:
            return str(runtime_dir)
    return None


def _connection_note(camera: dict[str, Any], connected: bool, detected_count: int) -> str:
    if connected:
        return "A detected OpenNI device can be assigned to this configured camera."
    if detected_count == 0:
        return "No OpenNI depth camera is connected right now."
    if camera.get("serial_hint"):
        return "Detected devices exist, but none matched this camera serial_hint."
    return "Detected devices exist; add serial_hint after the first multi-camera validation."


def _normalize_role(value: Any, fallback: str) -> str:
    role = str(value or fallback).strip().lower()
    return role if role in CAMERA_ROLES else fallback


def _role_hint_from_index(index: int) -> str:
    if index < len(CAMERA_ROLES):
        return CAMERA_ROLES[index]
    return "aux"


def _stringify_uri(uri: Any) -> str:
    if isinstance(uri, bytes):
        return uri.decode("utf-8", errors="replace")
    return str(uri)
