from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any


SCALE_SOURCES = ("manual_entry", "mock", "usb_hid", "rs232_serial")


def build_scale_status(env: dict[str, str] | None = None) -> dict[str, Any]:
    values = env or os.environ
    source = _scale_source(values)
    reading = _mock_reading(values) if source == "mock" else None
    configured = source != "manual_entry"
    return {
        "status": _status(source, reading),
        "source": source,
        "configured": configured,
        "stable": bool(reading and reading["stable"]),
        "weight_kg": reading["weight_kg"] if reading else None,
        "read_at": reading["read_at"] if reading else None,
        "adapters": _adapters(values, source),
        "setup_requirements": [
            "manual_entry_kept_as_fallback",
            "usb_hid_or_rs232_adapter_optional",
            "no_heavy_driver_bundled_in_base_package",
        ],
        "integration_policy": {
            "base_package": "manual_or_mock_only",
            "hardware_adapter": "enabled_by_environment_or_future_plugin",
            "failure_behavior": "keep_manual_weight_input_available",
        },
    }


def read_scale_weight(env: dict[str, str] | None = None) -> dict[str, Any]:
    status = build_scale_status(env)
    if status["weight_kg"]:
        return {
            "status": "measured",
            "source": status["source"],
            "weight_kg": status["weight_kg"],
            "stable": status["stable"],
            "read_at": status["read_at"],
        }
    return {
        "status": "manual_required",
        "source": status["source"],
        "weight_kg": None,
        "stable": False,
        "read_at": None,
        "next_actions": [
            "type_actual_weight_manually",
            "configure_packvision_scale_source_when_hardware_arrives",
        ],
    }


def _scale_source(env: dict[str, str]) -> str:
    source = (env.get("PACKVISION_SCALE_SOURCE") or "manual_entry").strip().lower()
    return source if source in SCALE_SOURCES else "manual_entry"


def _mock_reading(env: dict[str, str]) -> dict[str, Any] | None:
    try:
        weight = float(env.get("PACKVISION_MOCK_SCALE_KG") or "")
    except ValueError:
        return None
    if weight <= 0:
        return None
    return {
        "weight_kg": round(weight, 3),
        "stable": True,
        "read_at": datetime.now(timezone.utc).isoformat(),
    }


def _status(source: str, reading: dict[str, Any] | None) -> str:
    if reading:
        return "auto_weight_ready"
    if source == "manual_entry":
        return "manual_ready"
    return "adapter_configured_waiting"


def _adapters(env: dict[str, str], active_source: str) -> list[dict[str, Any]]:
    return [
        {
            "id": "manual_entry",
            "label": "Manual weight input",
            "available": True,
            "active": active_source == "manual_entry",
            "requires": [],
        },
        {
            "id": "mock",
            "label": "Mock scale for dry runs",
            "available": bool(env.get("PACKVISION_MOCK_SCALE_KG")),
            "active": active_source == "mock",
            "requires": ["PACKVISION_SCALE_SOURCE=mock", "PACKVISION_MOCK_SCALE_KG"],
        },
        {
            "id": "usb_hid",
            "label": "USB HID scale adapter",
            "available": env.get("PACKVISION_SCALE_HID_ENABLED") == "1",
            "active": active_source == "usb_hid",
            "requires": ["PACKVISION_SCALE_SOURCE=usb_hid", "future_hid_plugin"],
        },
        {
            "id": "rs232_serial",
            "label": "RS232 serial scale adapter",
            "available": bool(env.get("PACKVISION_SCALE_SERIAL_PORT")),
            "active": active_source == "rs232_serial",
            "requires": ["PACKVISION_SCALE_SOURCE=rs232_serial", "PACKVISION_SCALE_SERIAL_PORT"],
        },
    ]
