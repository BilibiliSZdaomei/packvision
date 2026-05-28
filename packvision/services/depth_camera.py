from __future__ import annotations

import importlib.util
import os
import platform
import subprocess
import time
from pathlib import Path
from typing import Any

from packvision.services.astra_vendor import astra_vendor_profile, resolve_astra_root
from packvision.services.depth_devices import build_depth_camera_inventory


DEFAULT_ASTRA_ROOT = Path(r"D:\BaiduNetdiskDownload\奥比中光Astra Pro")
DEFAULT_STATUS_CACHE_SECONDS = 5.0
_STATUS_CACHE: dict[str, tuple[float, dict[str, Any]]] = {}
_DRIVER_INSTALLATION_CACHE: dict[str, Any] | None = None


def depth_camera_status(vendor_root: str | Path | None = None) -> dict[str, Any]:
    root = resolve_astra_root(vendor_root)
    cache_key = str(root)
    cache_seconds = _status_cache_seconds()
    now = time.monotonic()
    cached = _STATUS_CACHE.get(cache_key)
    if cached and cache_seconds > 0 and now - cached[0] < cache_seconds:
        return cached[1]

    status = _build_depth_camera_status(root)
    if cache_seconds > 0:
        _STATUS_CACHE[cache_key] = (now, status)
    return status


def _build_depth_camera_status(root: Path) -> dict[str, Any]:
    openni_dir = root / "上位机软件" / "上位机软件"
    openni_dll = openni_dir / "OpenNI2.dll"
    orbbec_driver = openni_dir / "OpenNI2" / "Drivers" / "orbbec.dll"
    windows_driver = root / "上位机软件" / "Window 驱动" / "SensorDriver_V4.3.0.17.exe"
    windows_driver_installation = windows_driver_installation_status()
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
            "installed": windows_driver_installation["installed"],
            "installation": windows_driver_installation,
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
        "camera_inventory": build_depth_camera_inventory(),
        "calibration_strategy": vendor_profile["vendor_first_calibration_strategy"],
        "notes": [
            "Install the Windows sensor driver before first USB validation.",
            "Validate depth, color, IR, and point cloud in OrbbecViewer before PackVision capture debugging.",
            "For Astra Pro measurement, prefer ROS/OpenNI camera_info and get_camera_params over manual intrinsics.",
            "Use PACKVISION_ASTRA_ROOT to point PackVision at another vendor tutorial folder.",
            "The branch keeps hardware SDK imports optional so the main EXE remains lightweight.",
        ],
    }


def windows_driver_installation_status(
    *,
    registry_entries: list[dict[str, Any]] | None = None,
    pnputil_output: str | None = None,
) -> dict[str, Any]:
    global _DRIVER_INSTALLATION_CACHE
    if registry_entries is None and pnputil_output is None and _DRIVER_INSTALLATION_CACHE is not None:
        return _DRIVER_INSTALLATION_CACHE
    programs = registry_entries if registry_entries is not None else _read_orbbec_uninstall_entries()
    driver_store_entries = _parse_orbbec_pnputil_entries(
        pnputil_output if pnputil_output is not None else _read_pnputil_driver_output()
    )
    installed = bool(programs or driver_store_entries)
    status = {
        "platform": platform.system(),
        "installed": installed,
        "status": "installed" if installed else "not_found",
        "program_entries": programs,
        "driver_store_entries": driver_store_entries,
        "evidence": _driver_evidence(programs, driver_store_entries),
    }
    if registry_entries is None and pnputil_output is None:
        _DRIVER_INSTALLATION_CACHE = status
    return status


def _read_orbbec_uninstall_entries() -> list[dict[str, Any]]:
    if platform.system().lower() != "windows":
        return []
    try:
        import winreg
    except ImportError:
        return []

    entries: list[dict[str, Any]] = []
    uninstall_roots = [
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]
    for hive, subkey in uninstall_roots:
        try:
            with winreg.OpenKey(hive, subkey) as root:
                for index in range(winreg.QueryInfoKey(root)[0]):
                    try:
                        child_name = winreg.EnumKey(root, index)
                        with winreg.OpenKey(root, child_name) as child:
                            item = _read_uninstall_entry(winreg, child)
                    except OSError:
                        continue
                    if _looks_like_orbbec_driver(item):
                        entries.append(item)
        except OSError:
            continue
    return entries


def _read_uninstall_entry(winreg: Any, key: Any) -> dict[str, Any]:
    fields = ["DisplayName", "DisplayVersion", "Publisher", "InstallLocation", "InstallDate"]
    item: dict[str, Any] = {}
    for field in fields:
        try:
            value, _ = winreg.QueryValueEx(key, field)
        except OSError:
            value = None
        item[field] = value
    return item


def _read_pnputil_driver_output() -> str:
    if platform.system().lower() != "windows":
        return ""
    try:
        result = subprocess.run(
            ["pnputil", "/enum-drivers"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=8,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return (result.stdout or "") + "\n" + (result.stderr or "")


def _parse_orbbec_pnputil_entries(output: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            if _looks_like_orbbec_driver(current):
                entries.append(current)
            current = {}
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        current[key.strip()] = value.strip()
    if _looks_like_orbbec_driver(current):
        entries.append(current)
    return entries


def _looks_like_orbbec_driver(item: dict[str, Any]) -> bool:
    haystack = " ".join(str(value or "") for value in item.values()).lower()
    return any(keyword in haystack for keyword in ("orbbec", "astra", "obdrv", "sensordriver", "primesense"))


def _driver_evidence(programs: list[dict[str, Any]], driver_store_entries: list[dict[str, str]]) -> list[str]:
    evidence: list[str] = []
    for item in programs[:3]:
        name = item.get("DisplayName") or "Orbbec driver"
        version = item.get("DisplayVersion")
        evidence.append(f"{name} {version}".strip())
    for item in driver_store_entries[:3]:
        published = item.get("Published Name") or item.get("Original Name") or "driver store"
        provider = item.get("Provider Name") or "Orbbec"
        version = item.get("Driver Version")
        evidence.append(f"{provider} {published} {version}".strip())
    return evidence


def _status_cache_seconds() -> float:
    try:
        return max(0.0, float(os.environ.get("PACKVISION_DEPTH_STATUS_CACHE_SECONDS", DEFAULT_STATUS_CACHE_SECONDS)))
    except (TypeError, ValueError):
        return DEFAULT_STATUS_CACHE_SECONDS
