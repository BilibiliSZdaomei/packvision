from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from packvision.services.astra_vendor import astra_vendor_profile, resolve_astra_root


DEFAULT_ASTRA_ROOT = Path(r"D:\BaiduNetdiskDownload\奥比中光Astra Pro")


def depth_camera_status(vendor_root: str | Path | None = None) -> dict[str, Any]:
    root = resolve_astra_root(vendor_root)
    openni_dir = root / "上位机软件" / "上位机软件"
    openni_dll = openni_dir / "OpenNI2.dll"
    orbbec_driver = openni_dir / "OpenNI2" / "Drivers" / "orbbec.dll"
    windows_driver = root / "上位机软件" / "Window 驱动" / "SensorDriver_V4.3.0.17.exe"
    orbbec_viewer = openni_dir / "OrbbecViewer.exe"
    datasheet = root / "产品规格书-Astra Pro_Datasheet _v2.0.pdf"
    calibration_board = root / "棋盘格标定200x160_7x10.pdf"
    calibration_tutorial = root / "ROS1系列教程" / "1、Astra相机标定" / "1、Astra相机标定.md"
    ros2_sdk = root / "ROS2系列教程" / "OpenNI_ROS2_SDK_v1.1.0_20230131_d6d939.tar"
    pyorbbecsdk_available = importlib.util.find_spec("pyorbbecsdk") is not None
    vendor_profile = astra_vendor_profile(root)

    if pyorbbecsdk_available:
        recommended_backend = "pyorbbecsdk"
    elif openni_dll.exists() and orbbec_driver.exists():
        recommended_backend = "openni2_vendor_runtime"
    else:
        recommended_backend = "not_ready"

    return {
        "ready_for_hardware_trial": pyorbbecsdk_available or (openni_dll.exists() and orbbec_driver.exists()),
        "recommended_backend": recommended_backend,
        "pyorbbecsdk_available": pyorbbecsdk_available,
        "vendor_root": str(root),
        "vendor_root_exists": root.exists(),
        "openni2": {
            "runtime_dir": str(openni_dir),
            "openni_dll_found": openni_dll.exists(),
            "orbbec_driver_found": orbbec_driver.exists(),
        },
        "windows_driver": {
            "path": str(windows_driver),
            "found": windows_driver.exists(),
        },
        "vendor_viewer": {
            "path": str(orbbec_viewer),
            "found": orbbec_viewer.exists(),
        },
        "reference_files": {
            "datasheet": str(datasheet) if datasheet.exists() else None,
            "calibration_board": str(calibration_board) if calibration_board.exists() else None,
            "calibration_tutorial": str(calibration_tutorial) if calibration_tutorial.exists() else None,
            "ros2_openni_sdk": str(ros2_sdk) if ros2_sdk.exists() else None,
        },
        "vendor_profile": vendor_profile,
        "calibration_strategy": vendor_profile["vendor_first_calibration_strategy"],
        "notes": [
            "Install the Windows sensor driver before first USB validation.",
            "Validate depth, color, IR, and point cloud in OrbbecViewer before PackVision capture debugging.",
            "For Astra Pro measurement, prefer ROS/OpenNI camera_info and get_camera_params over manual intrinsics.",
            "Use PACKVISION_ASTRA_ROOT to point PackVision at another vendor tutorial folder.",
            "The branch keeps hardware SDK imports optional so the main EXE remains lightweight.",
        ],
    }
