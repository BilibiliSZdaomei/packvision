from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


DWS_CAPABILITIES = (
    "dimensioning",
    "weighing",
    "scanning",
    "evidence",
    "integration",
)


def build_station_snapshot(
    *,
    live_state: dict[str, Any] | None = None,
    latest_measurements: list[dict[str, Any]] | None = None,
    usage: dict[str, Any] | None = None,
) -> dict[str, Any]:
    live = live_state or {}
    latest = (latest_measurements or [{}])[0] if latest_measurements else {}
    usage_summary = usage or {}
    capabilities = _capability_statuses(live, latest, usage_summary)
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
        "production_gaps": _production_gaps(live, latest, capabilities),
        "next_upgrade_tracks": [
            "scale_adapter_usb_rs232_hid",
            "wms_tms_push_and_retry_queue",
            "hardware_watchdog_and_recovery",
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
) -> list[dict[str, Any]]:
    live_dims = ((live.get("stable_result") or live.get("latest_result") or {}).get("dimensions") or {})
    latest_has_dims = any(_positive(latest.get(key)) for key in ("length_mm", "width_mm", "height_mm", "volume_l"))
    latest_has_order = bool(latest.get("order_id") or latest.get("barcode_text"))
    latest_has_weight = _positive(latest.get("chargeable_weight_kg")) or _positive(latest.get("volumetric_weight_kg"))
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
            "status": "manual_ready" if latest_has_weight else "manual_input_pending",
            "source": "manual_weight_and_dim_rule",
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
            "status": "local_ready" if usage.get("total_calls", 0) >= 0 else "unknown",
            "source": "local_api_sqlite_csv",
        },
    ]


def _professional_score(capabilities: list[dict[str, Any]]) -> dict[str, Any]:
    strong_statuses = {"ready", "manual_ready", "manual_or_image_ready", "local_ready"}
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


def _production_gaps(
    live: dict[str, Any],
    latest: dict[str, Any],
    capabilities: list[dict[str, Any]],
) -> list[dict[str, str]]:
    gaps: list[dict[str, str]] = []
    if live.get("simulation_active"):
        gaps.append(_gap("hardware_validation_pending", "Astra Pro real hardware validation is still required."))
    if not _positive(latest.get("actual_weight_kg")):
        gaps.append(_gap("scale_adapter_pending", "Actual weight is still manual; add USB/RS232/HID scale adapter."))
    if not (latest.get("order_id") or latest.get("barcode_text")):
        gaps.append(_gap("wms_order_binding_pending", "Order binding should be driven by scanner or WMS lookup."))
    if any(item["status"].endswith("pending") for item in capabilities):
        gaps.append(_gap("operator_exception_flow_pending", "Pending states need clear operator recovery prompts."))
    gaps.append(_gap("wms_push_retry_pending", "Industrial deployment needs WMS/TMS push with retry queue."))
    return gaps


def _gap(code: str, message: str) -> dict[str, str]:
    return {"code": code, "message": message}


def _positive(value: Any) -> bool:
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False
