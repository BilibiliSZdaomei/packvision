from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from packvision.services.depth_camera import depth_camera_status
from packvision.services.depth_devices import (
    DepthDeviceError,
    build_depth_camera_inventory,
    camera_config_by_id_or_role,
    enumerate_openni_devices,
)
from packvision.services.depth_geometry import DepthIntrinsics


@dataclass(frozen=True)
class DepthCaptureConfig:
    backend: str = "auto"
    timeout_ms: int = 1500
    camera_id: str | None = None
    role: str | None = None


@dataclass(frozen=True)
class DepthFrameBundle:
    depth_frame: list[list[float]]
    intrinsics: DepthIntrinsics
    backend: str
    camera_id: str | None = None
    role: str | None = None
    serial_number: str | None = None
    color_frame_shape: tuple[int, int] | None = None
    frame_index: int | None = None
    timestamp_us: int | None = None


class DepthCaptureError(RuntimeError):
    pass


def depth_capture_capabilities(vendor_root: str | Path | None = None) -> dict[str, Any]:
    status = depth_camera_status(vendor_root)
    pyorbbecsdk_available = importlib.util.find_spec("pyorbbecsdk") is not None
    primesense_available = importlib.util.find_spec("primesense") is not None
    opencv_openni2_available = _opencv_openni2_available()
    openni_runtime_ready = bool(
        status["openni2"]["openni_dll_found"] and status["openni2"]["orbbec_driver_found"]
    )
    openni_primesense_ready = openni_runtime_ready and primesense_available
    camera_inventory = build_depth_camera_inventory()

    if pyorbbecsdk_available:
        recommended = "pyorbbecsdk"
    elif openni_primesense_ready:
        recommended = "openni2_primesense"
    elif openni_runtime_ready and opencv_openni2_available:
        recommended = "openni2_runtime_probe"
    else:
        recommended = "not_ready"

    return {
        "recommended_capture_backend": recommended,
        "capture_backends": {
            "pyorbbecsdk": {
                "available": pyorbbecsdk_available,
                "role": "Optional OrbbecSDK path for future hardware families.",
            },
            "openni2_primesense": {
                "available": openni_primesense_ready,
                "openni_runtime_ready": openni_runtime_ready,
                "primesense_available": primesense_available,
                "role": "Primary Astra Pro OpenNI frame capture path on Windows.",
            },
            "openni2_runtime_probe": {
                "available": openni_runtime_ready and opencv_openni2_available,
                "openni_runtime_ready": openni_runtime_ready,
                "opencv_openni2_available": opencv_openni2_available,
                "role": "Vendor runtime and OpenCV probe path for first hardware validation.",
            },
        },
        "camera_inventory": camera_inventory,
        "hardware_status": status,
        "notes": [
            "Frame capture is isolated behind a backend adapter so the main workflow can survive hardware changes.",
            "Run the vendor viewer first when the camera arrives, then use the PackVision probe endpoint.",
            "Measurement APIs already accept depth_frame payloads, so captured frames enter the existing history flow.",
            "Multi-camera upgrades should add camera_id and role entries instead of changing warehouse workflows.",
        ],
    }


def probe_depth_capture(config: DepthCaptureConfig | None = None) -> dict[str, Any]:
    config = config or DepthCaptureConfig()
    backend_requested = (config.backend or "auto").strip().lower()
    if backend_requested == "openni2":
        backend_requested = "openni2_primesense"
    if backend_requested not in {"auto", "pyorbbecsdk", "openni2_primesense", "openni2_runtime_probe"}:
        raise DepthCaptureError("backend must be auto, pyorbbecsdk, openni2_primesense, or openni2_runtime_probe.")

    capabilities = depth_capture_capabilities()
    selected = _select_backend(backend_requested, capabilities)
    backends = capabilities["capture_backends"]
    pyorbbec_ready = bool(backends["pyorbbecsdk"]["available"])
    openni_primesense_ready = bool(backends["openni2_primesense"]["available"])
    openni_ready = bool(backends["openni2_runtime_probe"]["available"])
    openni_runtime_ready = bool(backends["openni2_runtime_probe"]["openni_runtime_ready"])
    openni_probe: dict[str, Any] | None = None

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
    elif selected == "openni2_primesense" and openni_primesense_ready:
        camera = _camera_for_probe(config)
        openni_probe = enumerate_openni_devices(camera.get("runtime_dir"))
        device_count = int(openni_probe.get("device_count") or 0)
        ready = device_count > 0
        status = "ready_for_capture" if ready else "openni_runtime_ready_no_device"
        message_key = "openni_device_ready" if ready else "openni_runtime_ready_no_device"
        message = (
            "OpenNI runtime is initialized and at least one Astra/Orbbec depth camera is visible."
            if ready
            else "OpenNI runtime is initialized, but no Astra/Orbbec camera is connected right now."
        )
        next_action_keys = (
            ["capture_depth_frame", "measure_known_carton", "save_validation_history"]
            if ready
            else ["connect_astra_usb", "open_vendor_viewer", "rerun_probe_connected"]
        )
        next_actions = (
            [
                "Capture a depth frame through PackVision and check image stability.",
                "Measure a known carton or auto part and compare against tape-measure truth.",
                "Save the trial result to history with the order ID or validation sample ID.",
            ]
            if ready
            else [
                "Connect Astra Pro with a data-rated USB cable.",
                "Open OrbbecViewer and confirm the depth stream works.",
                "Run this probe again; device_count should become 1 or more.",
            ]
        )
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
            "install_primesense",
            "run_status_script",
        ]
        next_actions = [
            "Keep using the current depth_frame measurement APIs for imported frames.",
            "Install primesense in the hardware runtime environment to enable OpenNI frame capture.",
            "Use D:\\app\\orbbec-astra-pro\\检查Astra安装.ps1 to confirm the driver and OpenNI runtime.",
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

    field_diagnosis = _field_probe_diagnosis(
        status=status,
        ready=ready,
        message=message,
        message_key=message_key,
        backend_selected=selected,
        config=config,
        next_action_keys=next_action_keys,
        next_actions=next_actions,
        capabilities=capabilities,
        openni_probe=openni_probe,
    )
    return {
        "backend_requested": backend_requested,
        "backend_selected": selected,
        "timeout_ms": config.timeout_ms,
        "camera_id": config.camera_id,
        "role": config.role,
        "ready": ready,
        "status": status,
        "message_key": message_key,
        "message": message,
        "next_action_keys": next_action_keys,
        "next_actions": next_actions,
        "field_diagnosis": field_diagnosis,
        "capabilities": capabilities,
    }


def _field_probe_diagnosis(
    *,
    status: str,
    ready: bool,
    message: str,
    message_key: str,
    backend_selected: str,
    config: DepthCaptureConfig,
    next_action_keys: list[str],
    next_actions: list[str],
    capabilities: dict[str, Any],
    openni_probe: dict[str, Any] | None,
) -> dict[str, Any]:
    summary_key_by_status = {
        "ready_for_capture": "probe_ready",
        "openni_runtime_ready_no_device": "probe_no_camera",
        "hardware_validation_required": "probe_validate_hardware",
        "driver_ready_capture_backend_missing": "probe_backend_missing",
        "capture_backend_missing": "probe_backend_missing",
    }
    severity_by_status = {
        "ready_for_capture": "ready",
        "openni_runtime_ready_no_device": "waiting_for_camera",
        "hardware_validation_required": "validation_required",
        "driver_ready_capture_backend_missing": "action_required",
        "capture_backend_missing": "blocked",
    }
    summary_key = summary_key_by_status.get(status, message_key)
    severity = severity_by_status.get(status, "attention" if not ready else "ready")
    probe = openni_probe or (capabilities.get("camera_inventory") or {}).get("openni_probe") or {}
    device_count = int(probe.get("device_count") or 0)
    runtime_initialized = bool(probe.get("runtime_initialized"))
    action_items = [
        {
            "key": key,
            "label": key,
            "detail": next_actions[index] if index < len(next_actions) else key,
        }
        for index, key in enumerate(next_action_keys)
    ]
    return {
        "severity": severity,
        "operator_summary_key": summary_key,
        "operator_summary": _operator_summary_text(summary_key),
        "operator_detail": message,
        "can_continue_photo_fallback": not ready,
        "primary_actions": action_items,
        "evidence": {
            "status": status,
            "backend_selected": backend_selected,
            "camera_id": config.camera_id,
            "role": config.role,
            "runtime_initialized": runtime_initialized,
            "device_count": device_count,
            "openni_error": probe.get("error"),
        },
    }


def _operator_summary_text(summary_key: str) -> str:
    summaries = {
        "probe_ready": "Depth camera is visible; capture a frame, then validate a known carton.",
        "probe_no_camera": "Driver and runtime are ready, but no Astra Pro is connected.",
        "probe_validate_hardware": "Runtime is present; connect the camera and validate it with OrbbecViewer.",
        "probe_backend_missing": "Capture backend is not ready; fix the driver/runtime or Python adapter first.",
    }
    return summaries.get(summary_key, "Review the capture probe status and follow the listed actions.")


def capture_depth_once(config: DepthCaptureConfig | None = None) -> DepthFrameBundle:
    config = config or DepthCaptureConfig()
    probe = probe_depth_capture(config)
    if probe["backend_selected"] != "openni2_primesense":
        raise DepthCaptureError(
            "Direct frame capture currently uses the OpenNI2/PrimeSense backend. "
            f"Current selected backend: {probe['backend_selected']}."
        )
    if probe["status"] != "ready_for_capture":
        raise DepthCaptureError(
            "Astra Pro frame capture is not ready yet. "
            f"Current probe status: {probe['status']}."
        )
    camera = _camera_for_probe(config)
    return _capture_openni2_frame(camera)


def _select_backend(backend_requested: str, capabilities: dict[str, Any]) -> str:
    if backend_requested != "auto":
        return backend_requested
    recommended = capabilities.get("recommended_capture_backend")
    if recommended in {"pyorbbecsdk", "openni2_primesense", "openni2_runtime_probe"}:
        return str(recommended)
    return "openni2_primesense"


def _opencv_openni2_available() -> bool:
    try:
        import cv2  # type: ignore[import-not-found]
    except Exception:
        return False
    return bool(hasattr(cv2, "CAP_OPENNI2"))


def _camera_for_probe(config: DepthCaptureConfig) -> dict[str, Any]:
    try:
        return camera_config_by_id_or_role(config.camera_id, config.role)
    except DepthDeviceError as exc:
        raise DepthCaptureError(str(exc)) from exc


def _capture_openni2_frame(camera: dict[str, Any]) -> DepthFrameBundle:
    try:
        import numpy as np
        from primesense import openni2  # type: ignore[import-not-found]
    except Exception as exc:  # pragma: no cover - depends on optional hardware package
        raise DepthCaptureError("OpenNI2 capture requires numpy and primesense to be installed.") from exc

    runtime_dir = Path(camera.get("runtime_dir") or "")
    if not runtime_dir.exists():
        raise DepthCaptureError(f"OpenNI runtime directory does not exist: {runtime_dir}")

    stream = None
    device = None
    initialized = False
    try:
        openni2.initialize(str(runtime_dir))
        initialized = True
        devices = openni2.Device.open_all()
        if not devices:
            raise DepthCaptureError("No OpenNI depth camera is connected.")
        device = _select_openni_device(devices, camera)
        stream = device.create_depth_stream()
        stream.start()
        frame = stream.read_frame()
        width = int(frame.width)
        height = int(frame.height)
        depth = np.frombuffer(frame.get_buffer_as_uint16(), dtype=np.uint16).reshape((height, width))
        intrinsics = _intrinsics_from_camera_config(camera, width, height)
        return DepthFrameBundle(
            depth_frame=depth.astype(float).tolist(),
            intrinsics=intrinsics,
            backend="openni2_primesense",
            camera_id=camera.get("camera_id"),
            role=camera.get("role"),
            serial_number=_device_uri(device),
            frame_index=int(getattr(frame, "frameIndex", 0) or 0),
            timestamp_us=int(getattr(frame, "timestamp", 0) or 0),
        )
    except DepthCaptureError:
        raise
    except Exception as exc:  # pragma: no cover - depends on actual hardware
        raise DepthCaptureError(f"OpenNI2 frame capture failed: {exc}") from exc
    finally:
        try:
            if stream is not None:
                stream.stop()
                stream.close()
        except Exception:
            pass
        try:
            if device is not None:
                device.close()
        except Exception:
            pass
        try:
            if initialized:
                openni2.unload()
        except Exception:
            pass


def _select_openni_device(devices: list[Any], camera: dict[str, Any]) -> Any:
    serial_hint = camera.get("serial_hint")
    if serial_hint:
        for device in devices:
            if serial_hint in _device_uri(device):
                return device
    return devices[0]


def _device_uri(device: Any) -> str:
    uri = getattr(device, "uri", None)
    if isinstance(uri, bytes):
        return uri.decode("utf-8", errors="replace")
    return str(uri or "")


def _intrinsics_from_camera_config(camera: dict[str, Any], width: int, height: int) -> DepthIntrinsics:
    data = camera.get("intrinsics") if isinstance(camera.get("intrinsics"), dict) else {}
    fx = float(data.get("fx") or max(width, 1))
    fy = float(data.get("fy") or max(height, 1))
    cx = float(data.get("cx") if data.get("cx") is not None else width / 2.0)
    cy = float(data.get("cy") if data.get("cy") is not None else height / 2.0)
    depth_scale = float(data.get("depth_scale") or 1.0)
    return DepthIntrinsics(
        fx=fx,
        fy=fy,
        cx=cx,
        cy=cy,
        width=int(width),
        height=int(height),
        depth_scale=depth_scale,
    )
