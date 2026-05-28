from datetime import datetime, timedelta, timezone

from packvision.services.device_watchdog import build_device_watchdog


def _capture_status(device_count: int = 0) -> dict:
    return {
        "recommended_capture_backend": "openni2_primesense",
        "capture_backends": {
            "pyorbbecsdk": {"available": False},
            "openni2_primesense": {"available": True, "openni_runtime_ready": True},
            "openni2_runtime_probe": {"available": True, "openni_runtime_ready": True},
        },
        "camera_inventory": {
            "configured_camera_count": 1,
            "target_camera_count": 1,
            "missing_three_view_roles": ["front", "left"],
            "openni_probe": {"device_count": device_count},
        },
    }


def test_device_watchdog_reports_no_camera_without_blocking_photo_fallback():
    result = build_device_watchdog(capture_status=_capture_status(device_count=0))

    assert result["status"] == "no_camera_detected"
    assert result["severity"] == "warning"
    assert result["photo_fallback_available"] is True
    assert result["safe_to_record_live"] is False
    assert result["signals"]["device_count"] == 0
    assert "no_depth_camera_detected" in {issue["code"] for issue in result["issues"]}
    assert "open_orbbec_viewer" in {step["id"] for step in result["recovery_steps"]}


def test_device_watchdog_marks_stale_live_stream_as_recovery_required():
    now = datetime(2026, 5, 28, 8, 0, 0, tzinfo=timezone.utc)
    live_state = {
        "running": True,
        "status": "measuring",
        "updated_at": (now - timedelta(seconds=30)).isoformat(),
        "config": {"interval_ms": 700},
        "can_confirm": False,
    }
    result = build_device_watchdog(
        live_state=live_state,
        capture_status=_capture_status(device_count=1),
        now=now,
    )

    assert result["status"] == "live_stale"
    assert result["severity"] == "critical"
    assert result["signals"]["live_stale"] is True
    assert "restart_live_stream" in {step["id"] for step in result["recovery_steps"]}


def test_device_watchdog_allows_real_live_recording_only_with_camera_and_stable_candidate():
    live_state = {
        "running": True,
        "status": "stable_ready",
        "updated_at": datetime(2026, 5, 28, 8, 0, 0, tzinfo=timezone.utc).isoformat(),
        "config": {"interval_ms": 700},
        "can_confirm": True,
        "simulation_active": False,
    }
    result = build_device_watchdog(
        live_state=live_state,
        capture_status=_capture_status(device_count=1),
        now=datetime(2026, 5, 28, 8, 0, 1, tzinfo=timezone.utc),
    )

    assert result["status"] == "live_camera_active"
    assert result["severity"] == "ok"
    assert result["safe_to_record_live"] is True
    assert result["operator_mode"] == "live_camera_measurement"


def test_device_watchdog_trusts_active_real_live_camera_when_probe_is_transiently_empty():
    live_state = {
        "running": True,
        "status": "stable_ready",
        "updated_at": datetime(2026, 5, 28, 8, 0, 0, tzinfo=timezone.utc).isoformat(),
        "config": {"interval_ms": 700},
        "frame_count": 4,
        "can_confirm": True,
        "simulation_active": False,
        "camera_results": [
            {
                "camera_capture": {
                    "status": "captured",
                    "camera_id": "astra-pro-top-01",
                    "role": "top",
                }
            },
            {
                "camera_capture": {
                    "status": "captured",
                    "camera_id": "astra-pro-front-01",
                    "role": "front",
                }
            },
        ],
    }
    result = build_device_watchdog(
        live_state=live_state,
        capture_status=_capture_status(device_count=0),
        now=datetime(2026, 5, 28, 8, 0, 1, tzinfo=timezone.utc),
    )

    assert result["status"] == "live_camera_active"
    assert result["severity"] == "ok"
    assert result["safe_to_record_live"] is True
    assert result["signals"]["device_count"] == 0
    assert result["signals"]["effective_device_count"] == 2
    assert "no_depth_camera_detected" not in {issue["code"] for issue in result["issues"]}
