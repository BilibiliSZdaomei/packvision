from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


DWS_CAPABILITIES = (
    "dimensioning",
    "weighing",
    "scanning",
    "evidence",
    "integration",
    "device_health",
)


def build_station_snapshot(
    *,
    live_state: dict[str, Any] | None = None,
    latest_measurements: list[dict[str, Any]] | None = None,
    usage: dict[str, Any] | None = None,
    scale_status: dict[str, Any] | None = None,
    integration_outbox: dict[str, Any] | None = None,
    device_watchdog: dict[str, Any] | None = None,
) -> dict[str, Any]:
    live = live_state or {}
    latest = (latest_measurements or [{}])[0] if latest_measurements else {}
    usage_summary = usage or {}
    scale = scale_status or {}
    outbox = integration_outbox or {}
    watchdog = device_watchdog or {}
    capabilities = _capability_statuses(live, latest, usage_summary, scale, outbox, watchdog)
    score = _professional_score(capabilities)

    return {
        "snapshot_at": datetime.now(timezone.utc).isoformat(),
        "station_status": _station_status(live),
        "operator_mode": "auto_live_capture",
        "camera_monitor_layout": [
            {"role": "top", "label": "Top camera", "purpose": "primary_dimensioning"},
            {"role": "front", "label": "Front camera", "purpose": "height_and_front_contour"},
            {"role": "side", "label": "Side camera", "purpose": "side_contour_and_occlusion_check"},
        ],
        "architecture_decision": {
            "mode": "medium_upgrade_modular_monolith",
            "reason": (
                "Local-first FastAPI services are suitable for overseas warehouse deployment; "
                "industrial maturity needs a station orchestration layer, device adapters, and WMS integration."
            ),
        },
        "dws_capabilities": capabilities,
        "professional_score": score,
        "current_candidate": _current_candidate(live),
        "latest_record": _latest_record(latest),
        "scale_status": _scale_summary(scale),
        "integration_outbox": _outbox_summary(outbox),
        "device_watchdog": _watchdog_summary(watchdog),
        "production_gaps": _production_gaps(live, latest, capabilities, scale, outbox, watchdog),
        "next_upgrade_tracks": [
            "scale_adapter_usb_rs232_hid",
            "wms_tms_push_and_retry_queue",
            "hardware_watchdog_field_validation",
            "operator_permission_and_audit_trail",
            "camera_calibration_profile_registry",
        ],
    }


def _station_status(live: dict[str, Any]) -> str:
    status = str(live.get("status") or "stopped")
    if status == "stable_ready" and live.get("can_confirm"):
        return "ready_to_record"
    if status in {"measuring", "starting", "waiting_for_object", "needs_review", "error"}:
        return status
    if live.get("running"):
        return "measuring"
    return "paused"


def _capability_statuses(
    live: dict[str, Any],
    latest: dict[str, Any],
    usage: dict[str, Any],
    scale: dict[str, Any],
    outbox: dict[str, Any],
    watchdog: dict[str, Any],
) -> list[dict[str, Any]]:
    live_dims = ((live.get("stable_result") or live.get("latest_result") or {}).get("dimensions") or {})
    latest_has_dims = any(_positive(latest.get(key)) for key in ("length_mm", "width_mm", "height_mm", "volume_l"))
    latest_has_order = bool(latest.get("order_id") or latest.get("barcode_text"))
    latest_has_weight = _positive(latest.get("chargeable_weight_kg")) or _positive(latest.get("volumetric_weight_kg"))
    scale_has_auto_weight = _positive(scale.get("weight_kg")) and scale.get("status") == "auto_weight_ready"
    latest_has_evidence = bool(latest.get("top_result_url") or latest.get("side_result_url") or live.get("can_confirm"))

    return [
        {
            "id": "dimensioning",
            "label": "Dimensioning",
            "status": "ready" if live.get("can_confirm") or live_dims or latest_has_dims else "waiting",
            "source": "depth_live_or_history",
        },
        {
            "id": "weighing",
            "label": "Weighing",
            "status": "auto_ready" if scale_has_auto_weight else "manual_ready" if latest_has_weight else "manual_input_pending",
            "source": scale.get("source") or "manual_weight_and_dim_rule",
        },
        {
            "id": "scanning",
            "label": "Scanning",
            "status": "ready" if latest_has_order else "manual_or_image_ready",
            "source": "scanner_text_or_barcode_image",
        },
        {
            "id": "evidence",
            "label": "Evidence",
            "status": "ready" if latest_has_evidence else "pending_capture",
            "source": "annotated_image_or_depth_point_cloud",
        },
        {
            "id": "integration",
            "label": "Integration",
            "status": _integration_status(outbox),
            "source": "local_api_sqlite_csv_outbox_http_dispatch",
        },
        {
            "id": "device_health",
            "label": "Device watchdog",
            "status": _device_health_status(watchdog),
            "source": watchdog.get("operator_mode") or "hardware_watchdog",
        },
    ]


def _professional_score(capabilities: list[dict[str, Any]]) -> dict[str, Any]:
    strong_statuses = {
        "ready",
        "auto_ready",
        "manual_ready",
        "manual_or_image_ready",
        "local_ready",
        "outbox_ready",
        "http_push_ready",
        "retry_attention",
        "watchdog_ready",
        "watchdog_warning",
    }
    ready_count = sum(1 for item in capabilities if item["status"] in strong_statuses)
    total = max(1, len(capabilities))
    percent = round(ready_count / total * 100)
    level = "industrial_pilot_ready" if percent >= 80 else "prototype_to_pilot"
    return {
        "ready_count": ready_count,
        "total": total,
        "percent": percent,
        "level": level,
    }


def _current_candidate(live: dict[str, Any]) -> dict[str, Any]:
    result = live.get("stable_result") or live.get("latest_result") or {}
    return {
        "status": live.get("status") or "stopped",
        "can_confirm": bool(live.get("can_confirm")),
        "fps": live.get("fps"),
        "uptime_seconds": live.get("uptime_seconds"),
        "dimensions": result.get("dimensions") or {},
        "quality_flags": result.get("quality_flags") or [],
    }


def _latest_record(latest: dict[str, Any]) -> dict[str, Any]:
    return {
        "measurement_id": latest.get("measurement_id"),
        "created_at": latest.get("created_at"),
        "order_id": latest.get("order_id"),
        "barcode_text": latest.get("barcode_text"),
        "package_class": latest.get("package_class"),
        "measurement_method": latest.get("measurement_method"),
        "chargeable_weight_kg": latest.get("chargeable_weight_kg"),
        "volumetric_weight_kg": latest.get("volumetric_weight_kg"),
        "billing_weight_source": latest.get("billing_weight_source"),
    }


def _scale_summary(scale: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": scale.get("status") or "unknown",
        "source": scale.get("source"),
        "configured": bool(scale.get("configured")),
        "weight_kg": scale.get("weight_kg"),
        "stable": bool(scale.get("stable")),
    }


def _outbox_summary(outbox: dict[str, Any]) -> dict[str, Any]:
    dispatch = outbox.get("dispatch") if isinstance(outbox.get("dispatch"), dict) else {}
    return {
        "delivery_mode": outbox.get("delivery_mode") or "local_outbox",
        "dispatch_status": dispatch.get("status") or "not_configured",
        "endpoint_configured": bool(dispatch.get("endpoint_configured")),
        "total": int(outbox.get("total") or 0),
        "pending": int(outbox.get("pending") or 0),
        "failed": int(outbox.get("failed") or 0),
        "due_for_retry": int(outbox.get("due_for_retry") or 0),
    }


def _watchdog_summary(watchdog: dict[str, Any]) -> dict[str, Any]:
    signals = watchdog.get("signals") if isinstance(watchdog.get("signals"), dict) else {}
    return {
        "status": watchdog.get("status") or "unknown",
        "severity": watchdog.get("severity") or "unknown",
        "operator_mode": watchdog.get("operator_mode"),
        "safe_to_record_live": bool(watchdog.get("safe_to_record_live")),
        "dry_run_record_available": bool(watchdog.get("dry_run_record_available")),
        "device_count": int(signals.get("device_count") or 0),
        "simulation_active": bool(signals.get("simulation_active")),
        "live_stale": bool(signals.get("live_stale")),
        "issues": [
            {"code": item.get("code"), "severity": item.get("severity")}
            for item in (watchdog.get("issues") or [])[:5]
            if isinstance(item, dict)
        ],
        "recovery_steps": [
            {"id": item.get("id"), "label": item.get("label")}
            for item in (watchdog.get("recovery_steps") or [])[:3]
            if isinstance(item, dict)
        ],
    }


def _production_gaps(
    live: dict[str, Any],
    latest: dict[str, Any],
    capabilities: list[dict[str, Any]],
    scale: dict[str, Any],
    outbox: dict[str, Any],
    watchdog: dict[str, Any],
) -> list[dict[str, str]]:
    gaps: list[dict[str, str]] = []
    if live.get("simulation_active"):
        gaps.append(_gap("hardware_validation_pending", "Astra Pro real hardware validation is still required."))
    if not _positive(latest.get("actual_weight_kg")) and scale.get("status") != "auto_weight_ready":
        gaps.append(_gap("scale_adapter_pending", "Actual weight is still manual; add USB/RS232/HID scale adapter."))
    if not (latest.get("order_id") or latest.get("barcode_text")):
        gaps.append(_gap("wms_order_binding_pending", "Order binding should be driven by scanner or WMS lookup."))
    if any(item["status"].endswith("pending") for item in capabilities):
        gaps.append(_gap("operator_exception_flow_pending", "Pending states need clear operator recovery prompts."))
    dispatch = outbox.get("dispatch") if isinstance(outbox.get("dispatch"), dict) else {}
    if dispatch.get("status") != "ready":
        gaps.append(_gap("wms_connector_pending", "Local WMS/TMS outbox is ready; add the target warehouse connector URL and credentials."))
    elif int(outbox.get("failed") or 0) > 0 or int(outbox.get("due_for_retry") or 0) > 0:
        gaps.append(_gap("wms_push_retry_attention", "WMS/TMS push is configured, but failed or retry-due events need attention."))
    if watchdog.get("severity") in {"warning", "critical"}:
        gaps.append(_gap("hardware_watchdog_attention", "Device watchdog found camera/runtime conditions that need field recovery."))
    return gaps


def _gap(code: str, message: str) -> dict[str, str]:
    return {"code": code, "message": message}


def _integration_status(outbox: dict[str, Any]) -> str:
    dispatch = outbox.get("dispatch") if isinstance(outbox.get("dispatch"), dict) else {}
    if dispatch.get("status") == "ready" and int(outbox.get("failed") or 0) == 0:
        return "http_push_ready"
    if int(outbox.get("failed") or 0) > 0 or int(outbox.get("due_for_retry") or 0) > 0:
        return "retry_attention"
    return "outbox_ready"


def _device_health_status(watchdog: dict[str, Any]) -> str:
    severity = watchdog.get("severity")
    if severity == "ok":
        return "watchdog_ready"
    if severity == "warning":
        return "watchdog_warning"
    if severity == "critical":
        return "watchdog_blocker"
    return "watchdog_unknown"


def _positive(value: Any) -> bool:
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False
