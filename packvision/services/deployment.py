from __future__ import annotations

import os
import platform
import shutil
import sys
from pathlib import Path
from typing import Any

from packvision import __version__
from packvision.services.ai_plugins import build_ai_plugin_inventory
from packvision.services.depth_camera import depth_camera_status
from packvision.services.depth_capture import depth_capture_capabilities
from packvision.services.measurement import opencv_ready
from packvision.services.storage import app_data_dir, ensure_data_dirs, resource_path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MAX_HANDOFF_MB = 100


def build_deployment_readiness(
    vendor_root: str | Path | None = None,
    *,
    package_root: str | Path | None = None,
    max_handoff_mb: int = DEFAULT_MAX_HANDOFF_MB,
) -> dict[str, Any]:
    root = Path(package_root) if package_root else _default_package_root()
    data_dirs = _data_dir_status()
    app_status = _app_status(root, max_handoff_mb=max_handoff_mb)
    depth_status = depth_camera_status(vendor_root)
    capture_status = depth_capture_capabilities(vendor_root)
    ai_plugin_status = build_ai_plugin_inventory()
    checklist = _checklist(app_status, data_dirs, depth_status, capture_status)
    blockers = [item for item in checklist if item["status"] == "blocker"]
    warnings = [item for item in checklist if item["status"] == "warning"]
    manual = [item for item in checklist if item["status"] == "manual_required"]

    modes = _readiness_modes(root, app_status, data_dirs, depth_status, capture_status, checklist)
    return {
        "status": "ready" if modes["overseas_handoff_package"]["ready"] and not blockers else "needs_attention",
        "version": __version__,
        "max_handoff_mb": max_handoff_mb,
        "readiness_modes": modes,
        "summary": {
            "blocker_count": len(blockers),
            "warning_count": len(warnings),
            "manual_required_count": len(manual),
            "image_only_ready": modes["image_only"]["ready"],
            "depth_preinstall_ready": modes["depth_preinstall"]["ready"],
            "camera_trial_ready": modes["camera_trial"]["ready"],
            "overseas_handoff_ready": modes["overseas_handoff_package"]["ready"],
        },
        "checks": checklist,
        "blockers": blockers,
        "warnings": warnings,
        "manual_required": manual,
        "target_warehouse_prepare_before_arrival": _target_warehouse_prepare_before_arrival(),
        "arrival_handoff_sequence": _arrival_handoff_sequence(),
        "transfer_package": _transfer_package(root, app_status, max_handoff_mb=max_handoff_mb),
        "local_paths": {
            "project_root": str(root),
            "app_data_dir": str(app_data_dir()),
            "docs_cn": str(root / "docs_cn"),
            "obsidian_notes": str(root / "docs_obsidian" / "PackVision"),
            "readiness_script": str(_readiness_script_path(root)),
            "handoff_package_script": str(root / "scripts" / "build_handoff_package.ps1"),
        },
        "hardware_status": depth_status,
        "capture_status": capture_status,
        "ai_plugins": ai_plugin_status,
    }


def build_deployment_readiness_summary(
    vendor_root: str | Path | None = None,
    *,
    package_root: str | Path | None = None,
    max_handoff_mb: int = DEFAULT_MAX_HANDOFF_MB,
) -> dict[str, Any]:
    readiness = build_deployment_readiness(
        vendor_root,
        package_root=package_root,
        max_handoff_mb=max_handoff_mb,
    )
    return {
        "status": readiness["status"],
        "version": readiness["version"],
        "max_handoff_mb": readiness["max_handoff_mb"],
        "summary": readiness["summary"],
        "readiness_modes": readiness["readiness_modes"],
        "blockers": _compact_checks(readiness.get("blockers") or []),
        "warnings": _compact_checks(readiness.get("warnings") or []),
        "manual_required": _compact_checks(readiness.get("manual_required") or []),
        "transfer_package": readiness["transfer_package"],
        "local_paths": readiness["local_paths"],
    }


def _compact_checks(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": item.get("id"),
            "label": item.get("label"),
            "status": item.get("status"),
            "next_action": item.get("next_action"),
        }
        for item in items
    ]


def _data_dir_status() -> dict[str, Any]:
    dirs = ensure_data_dirs()
    entries = {}
    for name, path in dirs.items():
        entries[name] = {
            "path": str(path),
            "exists": path.exists(),
            "writable": _is_writable(path),
        }
    return {
        "root": str(dirs["root"]),
        "entries": entries,
        "all_writable": all(item["writable"] for item in entries.values()),
    }


def _app_status(root: Path, *, max_handoff_mb: int) -> dict[str, Any]:
    exe_path = Path(sys.executable) if getattr(sys, "frozen", False) else root / "dist" / "PackVision.exe"
    exe_size = exe_path.stat().st_size if exe_path.exists() else None
    max_bytes = max_handoff_mb * 1024 * 1024
    static_index = resource_path("static", "index.html")
    return {
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "is_windows": platform.system().lower() == "windows",
            "is_64bit": sys.maxsize > 2**32,
            "python": sys.version.split()[0],
            "frozen_exe": bool(getattr(sys, "frozen", False)),
        },
        "commands": {
            "powershell_available": shutil.which("powershell") is not None or shutil.which("pwsh") is not None,
        },
        "runtime": {
            "opencv_aruco_ready": opencv_ready(),
            "static_index": str(static_index),
            "static_index_found": static_index.exists(),
        },
        "package": {
            "exe_path": str(exe_path),
            "exe_found": exe_path.exists(),
            "exe_size_bytes": exe_size,
            "exe_size_mb": round(exe_size / (1024 * 1024), 2) if exe_size is not None else None,
            "within_handoff_limit": bool(exe_size is not None and exe_size <= max_bytes),
        },
        "environment": {
            "PACKVISION_ASTRA_ROOT": os.environ.get("PACKVISION_ASTRA_ROOT"),
            "PACKVISION_DEPTH_CAMERA_CONFIG": os.environ.get("PACKVISION_DEPTH_CAMERA_CONFIG"),
        },
    }


def _checklist(
    app_status: dict[str, Any],
    data_dirs: dict[str, Any],
    depth_status: dict[str, Any],
    capture_status: dict[str, Any],
) -> list[dict[str, Any]]:
    vendor_files = depth_status.get("vendor_profile", {}).get("vendor_files", {})
    openni = depth_status.get("openni2", {})
    inventory = depth_status.get("camera_inventory", {})
    windows_driver = depth_status.get("windows_driver", {})
    windows_driver_installation = windows_driver.get("installation", {})
    package_status = app_status["package"]
    runtime_status = app_status["runtime"]
    platform_status = app_status["platform"]
    backends = capture_status.get("capture_backends", {})

    checks = [
        _check(
            "windows_pc",
            "Windows PC",
            "pass" if platform_status["is_windows"] else "warning",
            "PackVision is packaged for Windows warehouse PCs.",
            "Use a Windows 10/11 64-bit PC for the field handoff.",
        ),
        _check(
            "x64_runtime",
            "64-bit runtime",
            "pass" if platform_status["is_64bit"] else "blocker",
            "Depth SDKs and the PyInstaller build expect a 64-bit runtime.",
            "Use a 64-bit Windows installation.",
        ),
        _check(
            "opencv_aruco",
            "OpenCV ArUco runtime",
            "pass" if runtime_status["opencv_aruco_ready"] else "blocker",
            "Image-only fallback and calibration cards require OpenCV ArUco.",
            "Install requirements or use the packaged EXE.",
        ),
        _check(
            "static_ui",
            "PackVision UI files",
            "pass" if runtime_status["static_index_found"] else "blocker",
            "The local Web UI must be bundled with the app.",
            "Rebuild the EXE or run from the project root.",
        ),
        _check(
            "data_dirs_writable",
            "Writable history and artifact folders",
            "pass" if data_dirs["all_writable"] else "blocker",
            "Measurements, uploads, logs, and history exports need a writable local data folder.",
            "Run PackVision from a user-writable Windows profile.",
        ),
        _check(
            "packvision_exe",
            "PackVision.exe handoff file",
            "pass" if package_status["exe_found"] and package_status["within_handoff_limit"] else "warning",
            f"The handoff EXE should exist and stay below {DEFAULT_MAX_HANDOFF_MB} MB when possible.",
            "Run scripts/build_exe.ps1, then scripts/build_handoff_package.ps1.",
            details=package_status,
        ),
        _check(
            "vendor_tutorial_folder",
            "Astra Pro vendor tutorial folder",
            "pass" if depth_status.get("vendor_root_exists") else "warning",
            "The seller tutorial folder provides driver, viewer, OpenNI runtime, and calibration references.",
            "Copy the Astra Pro tutorial folder or set PACKVISION_ASTRA_ROOT.",
        ),
        _check(
            "windows_driver_installer",
            "Astra Windows driver installer",
            "pass" if windows_driver.get("found") else "warning",
            "Other warehouses should install the vendor driver before you arrive.",
            "Install SensorDriver on the target PC, then confirm Device Manager shows Orbbec.",
            details=windows_driver,
        ),
        _check(
            "windows_driver_installed",
            "Astra Windows driver installed",
            "pass" if windows_driver_installation.get("installed") else "manual_required",
            "The installer file only proves we have the package; Windows must also have the Orbbec driver registered.",
            "Run SensorDriver_V4.3.0.17.exe, then rerun the readiness check and OrbbecViewer.",
            details=windows_driver_installation,
        ),
        _check(
            "vendor_viewer",
            "OrbbecViewer validation tool",
            "pass" if depth_status.get("vendor_viewer", {}).get("found") else "warning",
            "The vendor viewer is the first proof that color/depth/IR/point-cloud streams work.",
            "Open OrbbecViewer once before using PackVision hardware capture.",
            details=depth_status.get("vendor_viewer", {}),
        ),
        _check(
            "openni_runtime",
            "OpenNI runtime files",
            "pass" if openni.get("openni_dll_found") and openni.get("orbbec_driver_found") else "warning",
            "PackVision's first Astra Pro capture backend uses the vendor OpenNI runtime.",
            "Keep OpenNI2.dll and the Orbbec OpenNI driver beside the viewer.",
            details=openni,
        ),
        _check(
            "python_capture_backend",
            "Python capture backend",
            "pass"
            if backends.get("openni2_primesense", {}).get("available") or backends.get("pyorbbecsdk", {}).get("available")
            else "warning",
            "A capture backend is needed only for direct camera capture, not for image-only mode.",
            "Use the packaged runtime or install primesense/pyorbbecsdk in the hardware environment.",
            details=backends,
        ),
        _check(
            "calibration_board_reference",
            "Vendor calibration board reference",
            "pass" if vendor_files.get("calibration_board", {}).get("found") else "manual_required",
            "Depth camera work should prefer factory/ROS camera_info; printed boards are fallback and validation aids.",
            "Print the vendor checkerboard PDF for engineering validation; keep PackVision ArUco only for image fallback.",
            details=vendor_files.get("calibration_board", {}),
        ),
        _check(
            "camera_connected",
            "Astra Pro connected now",
            "pass" if inventory.get("ready_for_single_camera_capture") else "manual_required",
            "This can only pass when a camera is plugged into the current PC.",
            "At the warehouse, connect one Astra Pro first and rerun the readiness check.",
            details=inventory.get("openni_probe", {}),
        ),
        _check(
            "field_accessories",
            "Field accessories prepared",
            "manual_required",
            "USB data cable, stable mount, matte table surface, lighting, tape/caliper, and printed cards are physical items.",
            "Ask the warehouse to prepare the arrival checklist before you travel.",
        ),
    ]
    return checks


def _readiness_modes(
    root: Path,
    app_status: dict[str, Any],
    data_dirs: dict[str, Any],
    depth_status: dict[str, Any],
    capture_status: dict[str, Any],
    checks: list[dict[str, Any]],
) -> dict[str, Any]:
    check_by_id = {item["id"]: item for item in checks}
    image_only_required = ["x64_runtime", "opencv_aruco", "static_ui", "data_dirs_writable"]
    image_only_ready = all(check_by_id[item]["status"] == "pass" for item in image_only_required)

    openni = depth_status.get("openni2", {})
    windows_driver_installation = depth_status.get("windows_driver", {}).get("installation", {})
    depth_preinstall_ready = bool(
        image_only_ready
        and depth_status.get("vendor_root_exists")
        and depth_status.get("windows_driver", {}).get("found")
        and windows_driver_installation.get("installed")
        and depth_status.get("vendor_viewer", {}).get("found")
        and openni.get("openni_dll_found")
        and openni.get("orbbec_driver_found")
    )
    capture_backend_ready = capture_status.get("recommended_capture_backend") in {
        "pyorbbecsdk",
        "openni2_primesense",
        "openni2_runtime_probe",
    }
    inventory = depth_status.get("camera_inventory", {})
    camera_trial_ready = bool(depth_preinstall_ready and capture_backend_ready and inventory.get("ready_for_single_camera_capture"))
    package_status = app_status["package"]
    handoff_ready = bool(
        image_only_ready
        and package_status["exe_found"]
        and package_status["within_handoff_limit"]
        and _readiness_script_path(root).exists()
    )

    return {
        "image_only": {
            "ready": image_only_ready,
            "purpose": "Phone-photo upload, barcode/order traceability, history, CSV export, and demo mode.",
            "missing_check_ids": _missing_required(check_by_id, image_only_required),
        },
        "depth_preinstall": {
            "ready": depth_preinstall_ready,
            "purpose": "Target warehouse has installed the Astra Pro driver/viewer/runtime before arrival.",
            "requires_camera_connected": False,
            "windows_driver_installed": bool(windows_driver_installation.get("installed")),
            "recommended_backend": capture_status.get("recommended_capture_backend"),
        },
        "camera_trial": {
            "ready": camera_trial_ready,
            "purpose": "Current PC can see at least one Astra/Orbbec depth camera and can begin known-carton validation.",
            "requires_camera_connected": True,
            "openni_device_count": inventory.get("openni_probe", {}).get("device_count"),
        },
        "overseas_handoff_package": {
            "ready": handoff_ready,
            "purpose": "The local files are ready to copy to another warehouse PC; target-side driver and camera checks still run on arrival.",
            "max_handoff_mb": DEFAULT_MAX_HANDOFF_MB,
            "exe_size_mb": package_status.get("exe_size_mb"),
        },
    }


def _target_warehouse_prepare_before_arrival() -> list[dict[str, Any]]:
    return [
        {
            "id": "driver_and_viewer_installed",
            "owner": "target_warehouse_it",
            "required": True,
            "item": "Install Astra Pro Windows sensor driver and keep OrbbecViewer on the desktop.",
            "verify": "Open OrbbecViewer and confirm color, depth, IR, and point cloud streams.",
        },
        {
            "id": "vendor_checkerboard_available",
            "owner": "target_warehouse",
            "required": True,
            "item": "Print or keep ready the Astra Pro vendor checkerboard calibration PDF.",
            "verify": "Open /api/depth/vendor-calibration-board.pdf; use it for engineering validation, not daily measurement.",
        },
        {
            "id": "printed_aruco_card",
            "owner": "target_warehouse",
            "required": False,
            "item": "Print the PackVision A4 ArUco calibration card only if phone-photo fallback is needed.",
            "verify": "Measure the printed marker with a ruler; do not stretch or fit-to-page.",
        },
        {
            "id": "usb_data_cable",
            "owner": "target_warehouse",
            "required": True,
            "item": "Prepare the original Astra Pro USB cable. If the camera has a fixed USB-A cable, prepare an active USB-A male to USB-A female extension only when extra length is needed; avoid charge-only cables.",
            "verify": "Windows detects a new Orbbec/Astra device after plugging in the camera.",
        },
        {
            "id": "powered_usb_hub",
            "owner": "target_warehouse",
            "required": False,
            "item": "Prepare a powered USB 3.x hub with data-capable USB-A ports for two-camera or three-camera validation.",
            "verify": "Use direct PC USB first; use powered hub if ports are unstable or insufficient.",
        },
        {
            "id": "stable_mount",
            "owner": "target_warehouse",
            "required": True,
            "item": "Prepare a tripod, copy stand, or fixed bracket so the camera angle does not move during measurement.",
            "verify": "The camera keeps the same view when the table is bumped lightly.",
        },
        {
            "id": "matte_surface_and_lighting",
            "owner": "target_warehouse",
            "required": True,
            "item": "Prepare a matte, non-reflective work surface and stable lighting.",
            "verify": "Avoid direct glare, transparent table covers, and deep-black glossy backgrounds.",
        },
        {
            "id": "truth_tools_and_samples",
            "owner": "target_warehouse",
            "required": True,
            "item": "Prepare tape measure/caliper plus known cartons, long parts, irregular parts, and reflective/dark samples.",
            "verify": "Use the PackVision trial CSV to record manual truth dimensions.",
        },
    ]


def _arrival_handoff_sequence() -> list[dict[str, Any]]:
    return [
        {"step": 1, "action": "Copy the handoff package to the target PC and unzip it locally."},
        {"step": 2, "action": "Install or confirm Astra Pro driver and OrbbecViewer from the vendor package."},
        {"step": 3, "action": "Plug in one Astra Pro with a data USB cable; avoid hubs for the first validation."},
        {"step": 4, "action": "Open OrbbecViewer and confirm color, depth, IR, and point cloud streams."},
        {"step": 5, "action": "Run scripts/check_astra_depth_status.ps1 and resolve blockers first."},
        {"step": 6, "action": "Start PackVision.exe and open http://127.0.0.1:8765."},
        {"step": 7, "action": "Run /api/depth/capture/probe, then capture one frame if the probe is ready."},
        {"step": 8, "action": "Measure known cartons and auto-parts samples, save to history, and export validation CSV."},
    ]


def _transfer_package(root: Path, app_status: dict[str, Any], *, max_handoff_mb: int) -> dict[str, Any]:
    return {
        "builder_script": str(root / "scripts" / "build_handoff_package.ps1"),
        "readiness_script": str(_readiness_script_path(root)),
        "recommended_zip_dir": str(root / "release"),
        "max_zip_mb": max_handoff_mb,
        "include_driver_installer_by_default": False,
        "why_driver_not_bundled": "Driver packages may be vendor-specific and should be installed from the official/seller tutorial files on the target PC.",
        "exe": app_status["package"],
        "commands": [
            r"PowerShell -ExecutionPolicy Bypass -File .\scripts\build_exe.ps1",
            r"PowerShell -ExecutionPolicy Bypass -File .\scripts\build_handoff_package.ps1",
            r"PowerShell -ExecutionPolicy Bypass -File .\scripts\check_astra_depth_status.ps1",
        ],
    }


def _default_package_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return PROJECT_ROOT


def _readiness_script_path(root: Path) -> Path:
    source_script = root / "scripts" / "check_astra_depth_status.ps1"
    if source_script.exists():
        return source_script
    return root / "check_astra_depth_status.ps1"


def _check(
    check_id: str,
    label: str,
    status: str,
    why: str,
    next_action: str,
    *,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "id": check_id,
        "label": label,
        "status": status,
        "why": why,
        "next_action": next_action,
        "details": details or {},
    }


def _missing_required(check_by_id: dict[str, dict[str, Any]], required: list[str]) -> list[str]:
    return [item for item in required if check_by_id[item]["status"] != "pass"]


def _is_writable(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".packvision-write-test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return True
    except OSError:
        return False
