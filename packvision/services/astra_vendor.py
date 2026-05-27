from __future__ import annotations

import os
from pathlib import Path
from typing import Any


BAIDU_VENDOR_ROOT = Path(r"D:\BaiduNetdiskDownload\奥比中光Astra Pro")
PROJECT_VENDOR_ROOT = Path(__file__).resolve().parents[2] / "奥比中光Astra Pro"

ASTRA_PRO_SPECS: dict[str, Any] = {
    "model": "Orbbec Astra Pro",
    "depth_technology": "single_camera_structured_light",
    "usb_interface": "USB2.0",
    "recommended_pc_usb": "stable USB data port, preferably USB3.x or powered hub for field reliability",
    "depth_range_mm": [600, 8000],
    "depth_resolutions": ["1280x1024@7FPS", "640x480@30FPS", "320x240@30FPS", "160x120@30FPS"],
    "color_resolutions": ["1280x720@30FPS", "640x480@30FPS", "320x240@30FPS"],
    "depth_accuracy": "1m:+/-3mm",
    "depth_fov": {"horizontal_deg": 58.4, "vertical_deg": 45.5},
    "color_fov": {"horizontal_deg": 66.1, "vertical_deg": 40.2},
    "power": "2.5W MAX, peak current 500mA MAX",
}


class AstraVendorError(RuntimeError):
    pass


def resolve_astra_root(vendor_root: str | Path | None = None) -> Path:
    if vendor_root:
        return Path(vendor_root)
    env_root = os.environ.get("PACKVISION_ASTRA_ROOT")
    if env_root:
        return Path(env_root)
    if PROJECT_VENDOR_ROOT.exists():
        return PROJECT_VENDOR_ROOT
    return BAIDU_VENDOR_ROOT


def astra_vendor_profile(vendor_root: str | Path | None = None) -> dict[str, Any]:
    root = resolve_astra_root(vendor_root)
    openni_dir = root / "上位机软件" / "上位机软件"
    windows_driver = root / "上位机软件" / "Window 驱动" / "SensorDriver_V4.3.0.17.exe"
    viewer = openni_dir / "OrbbecViewer.exe"
    openni_dll = openni_dir / "OpenNI2.dll"
    orbbec_driver = openni_dir / "OpenNI2" / "Drivers" / "orbbec.dll"
    ros2_tar = root / "ROS2系列教程" / "OpenNI_ROS2_SDK_v1.1.0_20230131_d6d939.tar"
    calibration_doc = root / "ROS1系列教程" / "1、Astra相机标定" / "1、Astra相机标定.md"
    calibration_board = root / "棋盘格标定200x160_7x10.pdf"

    return {
        "vendor_root": str(root),
        "vendor_root_exists": root.exists(),
        "hardware_profile": ASTRA_PRO_SPECS,
        "vendor_files": {
            "windows_driver": _file_entry(windows_driver),
            "orbbec_viewer": _file_entry(viewer),
            "openni2_runtime": _file_entry(openni_dll),
            "orbbec_openni_driver": _file_entry(orbbec_driver),
            "ros2_openni_sdk": _file_entry(ros2_tar),
            "calibration_tutorial": _file_entry(calibration_doc),
            "calibration_board": _file_entry(calibration_board),
        },
        "acceptance_workflow": [
            "install_windows_sensor_driver",
            "confirm_orbbec_device_in_device_manager",
            "open_orbbec_viewer",
            "verify_depth_color_ir_point_cloud",
            "only_then_open_packvision_hardware_capture",
        ],
        "vendor_first_calibration_strategy": {
            "default": "Use device/OpenNI/ROS camera parameters before PackVision fallback calibration.",
            "warehouse_worker": "No manual focal length, aperture, or intrinsic entry.",
            "engineer_only": [
                "Run OrbbecViewer for hardware validation.",
                "Use ROS camera_calibration only when device accuracy is suspect.",
                "Import rgb_camera / ir_camera calibration YAML when available.",
            ],
        },
        "ros_interfaces": {
            "camera_info_topics": ["/camera/depth/camera_info", "/camera/color/camera_info"],
            "services": [
                "/camera/get_camera_info",
                "/camera/get_camera_params",
                "/camera/get_device_info",
                "/camera/get_sdk_version",
            ],
            "measurement_input_priority": [
                "depth_frame_plus_ros_camera_info",
                "depth_frame_plus_imported_calibration_yaml",
                "depth_frame_plus_engineer_verified_intrinsics",
            ],
        },
        "material_depth_risks": [
            "black_or_dark_surface_absorbs_infrared",
            "mirror_or_glossy_surface_reflects_infrared",
            "transparent_material_depth_dropout",
            "too_close_under_600mm",
        ],
    }


def normalize_camera_info(
    camera_info: dict[str, Any],
    *,
    stream: str = "depth",
    depth_scale: float = 1.0,
) -> dict[str, Any]:
    if depth_scale <= 0:
        raise AstraVendorError("depth_scale must be positive.")
    if not isinstance(camera_info, dict):
        raise AstraVendorError("camera_info must be an object.")
    if isinstance(camera_info.get("info"), dict):
        camera_info = camera_info["info"]

    matrix, source = _extract_camera_matrix(camera_info)
    width = _extract_int(camera_info, "width", "image_width")
    height = _extract_int(camera_info, "height", "image_height")
    if width <= 0 or height <= 0:
        raise AstraVendorError("camera_info must include positive width/height or image_width/image_height.")

    fx = _positive_float(matrix[0], "fx")
    fy = _positive_float(matrix[4], "fy")
    cx = float(matrix[2])
    cy = float(matrix[5])
    stream_name = (stream or "depth").strip().lower()
    camera_name = camera_info.get("camera_name") or camera_info.get("name")
    flags = ["vendor_camera_info_used", "manual_intrinsics_not_required"]
    notes = [
        "Use this intrinsics payload directly with /api/depth/measure-roi or /api/depth/measure-object.",
        "For Astra Pro hardware, prefer /camera/depth/camera_info or imported ROS calibration YAML.",
    ]

    if not camera_name:
        flags.append("camera_name_missing")
    elif stream_name in {"depth", "ir", "infrared"} and camera_name != "ir_camera":
        flags.append("nonstandard_depth_camera_name")
        notes.append("ROS2 Astra README expects depth/IR calibration camera_name to be ir_camera.")
    elif stream_name in {"color", "rgb"} and camera_name != "rgb_camera":
        flags.append("nonstandard_color_camera_name")
        notes.append("ROS2 Astra README expects color calibration camera_name to be rgb_camera.")

    distortion = camera_info.get("distortion_coefficients") or camera_info.get("d") or camera_info.get("D")
    if isinstance(distortion, dict):
        distortion_data = distortion.get("data")
    else:
        distortion_data = distortion

    return {
        "status": "normalized",
        "source": source,
        "stream": stream_name,
        "camera_name": camera_name,
        "intrinsics": {
            "fx": fx,
            "fy": fy,
            "cx": cx,
            "cy": cy,
            "width": width,
            "height": height,
            "depth_scale": float(depth_scale),
        },
        "distortion_model": camera_info.get("distortion_model"),
        "distortion_coefficients": distortion_data if isinstance(distortion_data, list) else None,
        "quality_flags": flags,
        "notes": notes,
    }


def _file_entry(path: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "found": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() and path.is_file() else None,
    }


def _extract_camera_matrix(camera_info: dict[str, Any]) -> tuple[list[float], str]:
    for key in ("k", "K"):
        value = camera_info.get(key)
        if isinstance(value, list) and len(value) == 9:
            return [float(item) for item in value], "ros_camera_info_topic"

    camera_matrix = camera_info.get("camera_matrix")
    if isinstance(camera_matrix, dict):
        data = camera_matrix.get("data")
        if isinstance(data, list) and len(data) == 9:
            return [float(item) for item in data], "ros_calibration_yaml"

    raise AstraVendorError("camera_info must include k/K[9] or camera_matrix.data[9].")


def _extract_int(camera_info: dict[str, Any], *keys: str) -> int:
    for key in keys:
        value = camera_info.get(key)
        if value is not None:
            try:
                return int(value)
            except (TypeError, ValueError) as exc:
                raise AstraVendorError(f"{key} must be an integer.") from exc
    return 0


def _positive_float(value: Any, field_name: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise AstraVendorError(f"{field_name} must be numeric.") from exc
    if number <= 0:
        raise AstraVendorError(f"{field_name} must be positive.")
    return number
