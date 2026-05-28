from packvision.services import depth_capture
from packvision.services.depth_capture import DepthCaptureConfig, probe_depth_capture


def _capabilities(*, openni_available=True, runtime_ready=True):
    return {
        "recommended_capture_backend": "openni2_primesense" if openni_available else "not_ready",
        "capture_backends": {
            "pyorbbecsdk": {"available": False},
            "openni2_primesense": {
                "available": openni_available,
                "openni_runtime_ready": runtime_ready,
                "primesense_available": openni_available,
            },
            "openni2_runtime_probe": {
                "available": runtime_ready,
                "openni_runtime_ready": runtime_ready,
                "opencv_openni2_available": runtime_ready,
            },
        },
        "camera_inventory": {"openni_probe": {"device_count": 0}},
        "hardware_status": {},
    }


def test_depth_capture_probe_adds_field_diagnosis_for_missing_camera(monkeypatch):
    monkeypatch.setattr(depth_capture, "depth_capture_capabilities", lambda: _capabilities())
    monkeypatch.setattr(
        depth_capture,
        "_camera_for_probe",
        lambda config: {"runtime_dir": "D:/app/orbbec-astra-pro/viewer"},
    )
    monkeypatch.setattr(
        depth_capture,
        "enumerate_openni_devices",
        lambda runtime_dir=None: {
            "runtime_initialized": True,
            "device_count": 0,
            "devices": [],
            "error": None,
        },
    )

    result = probe_depth_capture(DepthCaptureConfig(backend="auto"))

    diagnosis = result["field_diagnosis"]
    assert result["status"] == "openni_runtime_ready_no_device"
    assert diagnosis["severity"] == "waiting_for_camera"
    assert diagnosis["operator_summary_key"] == "probe_no_camera"
    assert diagnosis["can_continue_photo_fallback"] is True
    assert diagnosis["primary_actions"][0]["key"] == "connect_astra_usb"
    assert diagnosis["evidence"]["device_count"] == 0


def test_depth_capture_probe_field_diagnosis_is_ready_when_device_visible(monkeypatch):
    monkeypatch.setattr(depth_capture, "depth_capture_capabilities", lambda: _capabilities())
    monkeypatch.setattr(
        depth_capture,
        "_camera_for_probe",
        lambda config: {"runtime_dir": "D:/app/orbbec-astra-pro/viewer"},
    )
    monkeypatch.setattr(
        depth_capture,
        "enumerate_openni_devices",
        lambda runtime_dir=None: {
            "runtime_initialized": True,
            "device_count": 1,
            "devices": [{"index": 0, "uri": "astra://top"}],
            "error": None,
        },
    )

    result = probe_depth_capture(DepthCaptureConfig(backend="auto", role="top"))

    diagnosis = result["field_diagnosis"]
    assert result["ready"] is True
    assert diagnosis["severity"] == "ready"
    assert diagnosis["operator_summary_key"] == "probe_ready"
    assert diagnosis["primary_actions"][0]["key"] == "capture_depth_frame"
    assert diagnosis["evidence"]["role"] == "top"


def test_depth_capture_probe_field_diagnosis_blocks_when_backend_missing(monkeypatch):
    monkeypatch.setattr(
        depth_capture,
        "depth_capture_capabilities",
        lambda: _capabilities(openni_available=False, runtime_ready=False),
    )

    result = probe_depth_capture(DepthCaptureConfig(backend="auto"))

    diagnosis = result["field_diagnosis"]
    assert result["status"] == "capture_backend_missing"
    assert diagnosis["severity"] == "blocked"
    assert diagnosis["operator_summary_key"] == "probe_backend_missing"
    assert diagnosis["primary_actions"][0]["key"] == "install_windows_driver"
    assert diagnosis["can_continue_photo_fallback"] is True
