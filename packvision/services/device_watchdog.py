from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from packvision.services.depth_capture import depth_capture_capabilities


STALE_MULTIPLIER = 4
MIN_STALE_SECONDS = 8


def build_device_watchdog(
    *,
    live_state: dict[str, Any] | None = None,
    capture_status: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    live = live_state or {}
    capture = capture_status or depth_capture_capabilities()
    inventory = capture.get("camera_inventory") or {}
    openni_probe = inventory.get("openni_probe") or {}
    backends = capture.get("capture_backends") or {}
    openni_backend = backends.get("openni2_primesense") or {}
    runtime_probe = backends.get("openni2_runtime_probe") or {}

    runtime_ready = bool(openni_backend.get("openni_runtime_ready") or runtime_probe.get("openni_runtime_ready"))
    capture_backend_ready = bool(
        openni_backend.get("available")
        or runtime_probe.get("available")
        or (backends.get("pyorbbecsdk") or {}).get("available")
    )
    device_count = _as_int(openni_probe.get("device_count"))
    configured_count = _as_int(inventory.get("configured_camera_count"))
    target_count = _as_int(inventory.get("target_camera_count"), default=max(1, configured_count))
    missing_roles = list(inventory.get("missing_three_view_roles") or [])
    live_running = bool(live.get("running"))
    live_status = str(live.get("status") or "stopped")
    simulation_active = bool(live.get("simulation_active"))
    stale = _live_is_stale(live, now=now)
    last_error = str(live.get("last_error") or "").strip()
    live_real_capture_active = (
        live_running
        and not simulation_active
        and not stale
        and not last_error
        and _as_int(live.get("frame_count")) > 0
        and live_status in {"measuring", "stable_ready", "needs_review", "waiting_for_object"}
    )
    live_camera_count = _live_camera_count(live)
    effective_device_count = max(device_count, live_camera_count if live_real_capture_active else 0)

    issues: list[dict[str, Any]] = []
    if not runtime_ready:
        issues.append(
            _issue(
                "openni_runtime_not_ready",
                "critical",
                "OpenNI runtime is not ready.",
                "Install or repair the Astra Pro vendor runtime under D:\\app\\orbbec-astra-pro.",
            )
        )
    if not capture_backend_ready:
        issues.append(
            _issue(
                "capture_backend_not_ready",
                "critical",
                "No depth capture backend is ready.",
                "Install the lightweight capture dependency or use photo fallback until engineering fixes the runtime.",
            )
        )
    if runtime_ready and effective_device_count == 0:
        issues.append(
            _issue(
                "no_depth_camera_detected",
                "warning",
                "Astra/Orbbec runtime is ready, but no depth camera is detected.",
                "Check USB data cable, powered hub, Device Manager, then confirm streams in OrbbecViewer.",
            )
        )
    if live_running and stale:
        issues.append(
            _issue(
                "live_stream_stale",
                "critical",
                "The live stream has not updated within the expected watchdog window.",
                "Pause and resume live capture; if it repeats, reconnect USB and export a support bundle.",
            )
        )
    if live_status == "error" or last_error:
        issues.append(
            _issue(
                "live_stream_error",
                "warning" if simulation_active else "critical",
                "The live capture loop reported an error.",
                "Use OrbbecViewer to validate the camera, then rerun PackVision capture probe.",
                detail=last_error or live_status,
            )
        )
    if simulation_active:
        issues.append(
            _issue(
                "simulation_fallback_active",
                "warning",
                "Live measurement is using simulation fallback.",
                "This is acceptable before the camera arrives, but shipping measurements need real camera capture.",
            )
        )
    if target_count >= 3 and effective_device_count < target_count:
        issues.append(
            _issue(
                "multiview_camera_count_incomplete",
                "warning",
                "Configured multi-view station has fewer detected cameras than target roles.",
                "Bind top/front/side camera serial numbers and rerun multi-camera validation.",
                detail=f"detected={effective_device_count}, target={target_count}, missing={','.join(missing_roles)}",
            )
        )

    severity = _overall_severity(issues)
    status = _watchdog_status(severity, runtime_ready, effective_device_count, simulation_active, live_status, stale)
    recovery_steps = _recovery_steps(status, issues)
    return {
        "status": status,
        "severity": severity,
        "checked_at": (now or datetime.now(timezone.utc)).isoformat(),
        "safe_to_record_live": bool(
            live.get("can_confirm") and not simulation_active and effective_device_count > 0 and severity != "critical"
        ),
        "dry_run_record_available": bool(live.get("can_confirm")),
        "photo_fallback_available": True,
        "operator_mode": _operator_mode(status),
        "signals": {
            "recommended_capture_backend": capture.get("recommended_capture_backend"),
            "runtime_ready": runtime_ready,
            "capture_backend_ready": capture_backend_ready,
            "device_count": device_count,
            "effective_device_count": effective_device_count,
            "live_camera_count": live_camera_count,
            "configured_camera_count": configured_count,
            "target_camera_count": target_count,
            "missing_three_view_roles": missing_roles,
            "live_running": live_running,
            "live_status": live_status,
            "simulation_active": simulation_active,
            "live_stale": stale,
            "fps": live.get("fps"),
            "frame_count": live.get("frame_count"),
            "updated_at": live.get("updated_at"),
            "last_error": last_error or None,
        },
        "issues": issues,
        "recovery_steps": recovery_steps,
    }


def _issue(code: str, severity: str, message: str, recovery: str, *, detail: str | None = None) -> dict[str, Any]:
    item = {
        "code": code,
        "severity": severity,
        "message": message,
        "recovery": recovery,
    }
    if detail:
        item["detail"] = detail
    return item


def _overall_severity(issues: list[dict[str, Any]]) -> str:
    severities = {str(issue.get("severity")) for issue in issues}
    if "critical" in severities:
        return "critical"
    if "warning" in severities:
        return "warning"
    return "ok"


def _watchdog_status(
    severity: str,
    runtime_ready: bool,
    device_count: int,
    simulation_active: bool,
    live_status: str,
    stale: bool,
) -> str:
    if severity == "critical":
        if stale:
            return "live_stale"
        if not runtime_ready:
            return "runtime_not_ready"
        return "needs_recovery"
    if simulation_active:
        return "simulation_fallback"
    if device_count > 0 and live_status in {"measuring", "stable_ready", "needs_review", "waiting_for_object"}:
        return "live_camera_active"
    if device_count > 0:
        return "camera_detected_idle"
    if severity == "warning":
        return "no_camera_detected"
    return "ready"


def _operator_mode(status: str) -> str:
    if status in {"live_camera_active", "camera_detected_idle", "ready"}:
        return "live_camera_measurement"
    if status == "simulation_fallback":
        return "dry_run_or_photo_fallback"
    if status == "no_camera_detected":
        return "photo_fallback_until_camera_connected"
    return "engineering_recovery_required"


def _recovery_steps(status: str, issues: list[dict[str, Any]]) -> list[dict[str, str]]:
    if status in {"live_camera_active", "camera_detected_idle", "ready"} and not issues:
        return [
            {
                "id": "continue_live_measurement",
                "label": "Continue live measurement and record only stable results.",
            }
        ]

    issue_codes = {str(issue.get("code")) for issue in issues}
    steps: list[dict[str, str]] = []
    if "openni_runtime_not_ready" in issue_codes or "capture_backend_not_ready" in issue_codes:
        steps.extend(
            [
                {"id": "check_driver_install", "label": "Run D:\\app\\orbbec-astra-pro\\检查Astra安装.ps1."},
                {"id": "repair_vendor_runtime", "label": "Reinstall SensorDriver and keep OpenNI2.dll beside OrbbecViewer."},
            ]
        )
    if "no_depth_camera_detected" in issue_codes:
        steps.extend(
            [
                {"id": "check_usb_data_path", "label": "Use a data-rated USB cable and avoid passive long cables."},
                {"id": "open_orbbec_viewer", "label": "Open OrbbecViewer and confirm Color/Depth/IR streams."},
                {"id": "rerun_capture_probe", "label": "Return to PackVision and run capture probe again."},
            ]
        )
    if "live_stream_stale" in issue_codes or "live_stream_error" in issue_codes:
        steps.extend(
            [
                {"id": "restart_live_stream", "label": "Pause live capture, then resume live capture."},
                {"id": "export_support_bundle", "label": "Export the field support bundle if the error repeats."},
            ]
        )
    if "simulation_fallback_active" in issue_codes:
        steps.append(
            {
                "id": "validate_real_camera_before_shipping",
                "label": "Do not use simulation for shipping dimensions; connect Astra Pro first.",
            }
        )
    if "multiview_camera_count_incomplete" in issue_codes:
        steps.append(
            {
                "id": "bind_multiview_serials",
                "label": "Bind top/front/side camera serial hints before three-view production use.",
            }
        )
    return _unique_steps(steps)


def _unique_steps(steps: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[str] = set()
    unique: list[dict[str, str]] = []
    for step in steps:
        step_id = step["id"]
        if step_id in seen:
            continue
        seen.add(step_id)
        unique.append(step)
    return unique


def _live_is_stale(live: dict[str, Any], *, now: datetime | None = None) -> bool:
    if not live.get("running"):
        return False
    updated_raw = live.get("updated_at")
    if not updated_raw:
        return False
    try:
        updated = datetime.fromisoformat(str(updated_raw).replace("Z", "+00:00"))
    except ValueError:
        return False
    if updated.tzinfo is None:
        updated = updated.replace(tzinfo=timezone.utc)
    config = live.get("config") if isinstance(live.get("config"), dict) else {}
    interval_seconds = max(0.25, min(5.0, _as_int(config.get("interval_ms"), default=700) / 1000.0))
    threshold = max(MIN_STALE_SECONDS, interval_seconds * STALE_MULTIPLIER)
    return ((now or datetime.now(timezone.utc)) - updated).total_seconds() > threshold


def _live_camera_count(live: dict[str, Any]) -> int:
    results = live.get("camera_results")
    if not isinstance(results, list):
        results = []
    camera_ids: set[str] = set()
    for result in results:
        if not isinstance(result, dict):
            continue
        capture = result.get("camera_capture") if isinstance(result.get("camera_capture"), dict) else {}
        if capture.get("status") != "captured":
            continue
        camera_id = str(capture.get("camera_id") or capture.get("role") or "").strip()
        if camera_id:
            camera_ids.add(camera_id)
    if camera_ids:
        return len(camera_ids)
    latest = live.get("latest_result") if isinstance(live.get("latest_result"), dict) else {}
    capture = latest.get("camera_capture") if isinstance(latest.get("camera_capture"), dict) else {}
    return 1 if capture.get("status") == "captured" else 0


def _as_int(value: Any, *, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
