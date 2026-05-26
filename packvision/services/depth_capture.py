from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from packvision.services.depth_camera import depth_camera_status
from packvision.services.depth_geometry import DepthIntrinsics


@dataclass(frozen=True)
class DepthCaptureConfig:
    backend: str = "auto"
    timeout_ms: int = 1500


@dataclass(frozen=True)
class DepthFrameBundle:
    depth_frame: list[list[float]]
    intrinsics: DepthIntrinsics
    backend: str
    serial_number: str | None = None
    color_frame_shape: tuple[int, int] | None = None


class DepthCaptureError(RuntimeError):
    pass


def depth_capture_capabilities(vendor_root: str | Path | None = None) -> dict[str, Any]:
    status = depth_camera_status(vendor_root)
    pyorbbecsdk_available = importlib.util.find_spec("pyorbbecsdk") is not None
    opencv_openni2_available = _opencv_openni2_available()
    openni_runtime_ready = bool(
        status["openni2"]["openni_dll_found"] and status["openni2"]["orbbec_driver_found"]
    )

    if pyorbbecsdk_available:
        recommended = "pyorbbecsdk"
    elif openni_runtime_ready and opencv_openni2_available:
        recommended = "openni2_runtime_probe"
    else:
        recommended = "not_ready"

    return {
        "recommended_capture_backend": recommended,
        "capture_backends": {
            "pyorbbecsdk": {
                "available": pyorbbecsdk_available,
                "role": "Preferred optional Python SDK path for real Astra Pro frame capture.",
            },
            "openni2_runtime_probe": {
                "available": openni_runtime_ready and opencv_openni2_available,
                "openni_runtime_ready": openni_runtime_ready,
                "opencv_openni2_available": opencv_openni2_available,
                "role": "Vendor runtime and OpenCV probe path for first hardware validation.",
            },
        },
        "hardware_status": status,
        "notes": [
            "Frame capture stays optional so PackVision.exe remains lightweight.",
            "Run the vendor viewer first when the camera arrives, then use the probe endpoint.",
            "Measurement APIs already accept depth_frame payloads, so captured frames can enter the existing history flow.",
        ],
    }


def probe_depth_capture(config: DepthCaptureConfig | None = None) -> dict[str, Any]:
    config = config or DepthCaptureConfig()
    backend_requested = (config.backend or "auto").strip().lower()
    if backend_requested not in {"auto", "pyorbbecsdk", "openni2_runtime_probe"}:
        raise DepthCaptureError("backend must be auto, pyorbbecsdk, or openni2_runtime_probe.")

    capabilities = depth_capture_capabilities()
    selected = _select_backend(backend_requested, capabilities)
    backends = capabilities["capture_backends"]
    pyorbbec_ready = bool(backends["pyorbbecsdk"]["available"])
    openni_ready = bool(backends["openni2_runtime_probe"]["available"])
    openni_runtime_ready = bool(backends["openni2_runtime_probe"]["openni_runtime_ready"])

    if selected == "pyorbbecsdk" and pyorbbec_ready:
        status = "hardware_validation_required"
        ready = False
        message = "pyorbbecsdk is installed; plug in Astra Pro and validate first capture on site."
        message_key = "pyorbbec_ready_validate"
        next_action_keys = [
            "connect_camera_driver",
            "confirm_vendor_viewer_streams",
            "validate_known_carton_history",
        ]
        next_actions = [
            "Connect Astra Pro over USB and confirm the Windows driver is installed.",
            "Open the vendor viewer once to confirm RGB and Depth streams.",
            "Run PackVision capture validation with a known carton and save the result to history.",
        ]
    elif selected == "openni2_runtime_probe" and openni_ready:
        status = "hardware_validation_required"
        ready = False
        message = "OpenNI2 runtime and OpenCV probe support are present; hardware validation is still required."
        message_key = "openni_ready_validate"
        next_action_keys = [
            "confirm_vendor_viewer_depth",
            "rerun_probe_connected",
            "install_pyorbbec_if_unstable",
        ]
        next_actions = [
            "Connect Astra Pro and confirm the vendor viewer can see depth frames.",
            "Use the probe endpoint again with the camera connected.",
            "Install pyorbbecsdk later if OpenNI2 capture is unstable on this Windows build.",
        ]
    elif openni_runtime_ready:
        status = "driver_ready_capture_backend_missing"
        ready = False
        message = "Vendor runtime files are present, but no Python capture backend is ready in the lightweight EXE."
        message_key = "driver_ready_backend_missing"
        next_action_keys = [
            "use_depth_frame_apis",
            "install_pyorbbec_hardware_build",
            "run_status_script",
        ]
        next_actions = [
            "Keep using the current depth_frame measurement APIs for imported frames.",
            "After the camera arrives, install or bundle pyorbbecsdk in a hardware-specific build.",
            "Use scripts\\check_astra_depth_status.ps1 to confirm the tutorial folder and driver files.",
        ]
    else:
        status = "capture_backend_missing"
        ready = False
        message = "No local capture backend is ready yet."
        message_key = "capture_backend_missing"
        next_action_keys = [
            "install_windows_driver",
            "set_astra_root",
            "confirm_vendor_viewer",
        ]
        next_actions = [
            "Install the Astra Pro Windows driver from the seller tutorial folder.",
            "Set PACKVISION_ASTRA_ROOT if the tutorial files are stored elsewhere.",
            "Use the vendor viewer to confirm the camera before enabling real-time capture.",
        ]

    return {
        "backend_requested": backend_requested,
        "backend_selected": selected,
        "timeout_ms": config.timeout_ms,
        "ready": ready,
        "status": status,
        "message_key": message_key,
        "message": message,
        "next_action_keys": next_action_keys,
        "next_actions": next_actions,
        "capabilities": capabilities,
    }


def capture_depth_once(config: DepthCaptureConfig | None = None) -> DepthFrameBundle:
    probe = probe_depth_capture(config)
    raise DepthCaptureError(
        "Direct Astra Pro frame capture requires hardware validation first. "
        f"Current probe status: {probe['status']}."
    )


def _select_backend(backend_requested: str, capabilities: dict[str, Any]) -> str:
    if backend_requested != "auto":
        return backend_requested
    recommended = capabilities.get("recommended_capture_backend")
    if recommended in {"pyorbbecsdk", "openni2_runtime_probe"}:
        return str(recommended)
    return "pyorbbecsdk"


def _opencv_openni2_available() -> bool:
    try:
        import cv2  # type: ignore[import-not-found]
    except Exception:
        return False
    return bool(hasattr(cv2, "CAP_OPENNI2"))
