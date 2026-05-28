from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from typing import Any


SCALE_SOURCES = ("manual_entry", "mock", "usb_hid", "rs232_serial")
DEFAULT_SERIAL_BAUDRATE = 9600
DEFAULT_SERIAL_TIMEOUT_MS = 500
DEFAULT_SERIAL_READ_LINES = 3


def build_scale_status(env: dict[str, str] | None = None) -> dict[str, Any]:
    values = env or os.environ
    source = _scale_source(values)
    reading = _read_adapter(values, source)
    configured = source != "manual_entry"
    return {
        "status": _status(source, reading),
        "source": source,
        "configured": configured,
        "stable": bool(reading and reading.get("stable")),
        "weight_kg": reading.get("weight_kg") if reading else None,
        "read_at": reading.get("read_at") if reading else None,
        "raw_reading": reading.get("raw") if reading else None,
        "adapter_error": reading.get("error") if reading else None,
        "adapter_config": _adapter_config(values, source),
        "adapters": _adapters(values, source),
        "setup_requirements": [
            "manual_entry_kept_as_fallback",
            "rs232_serial_supported_with_pyserial",
            "usb_hid_kept_as_future_plugin",
            "no_heavy_driver_bundled_in_base_package",
        ],
        "integration_policy": {
            "base_package": "manual_mock_or_rs232_serial",
            "hardware_adapter": "enabled_by_environment",
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
            "raw_reading": status["raw_reading"],
        }
    if status["adapter_error"]:
        return {
            "status": "adapter_error",
            "source": status["source"],
            "weight_kg": None,
            "stable": False,
            "read_at": status["read_at"],
            "adapter_error": status["adapter_error"],
            "next_actions": _error_actions(status["adapter_error"]),
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


def parse_scale_weight_line(raw: str) -> dict[str, Any] | None:
    text = str(raw or "").strip()
    if not text:
        return None
    match = re.search(r"([+-]?\s*\d+(?:[\.,]\d+)?)\s*(kg|kgs|g|lb|lbs)?", text, flags=re.IGNORECASE)
    if not match:
        return None
    numeric = match.group(1).replace(" ", "").replace(",", ".")
    try:
        value = float(numeric)
    except ValueError:
        return None
    unit = (match.group(2) or "kg").lower()
    if unit in {"g"}:
        weight_kg = value / 1000.0
    elif unit in {"lb", "lbs"}:
        weight_kg = value * 0.45359237
    else:
        weight_kg = value
    if weight_kg <= 0:
        return None
    stable = _stable_from_text(text)
    return {
        "weight_kg": round(weight_kg, 3),
        "stable": stable,
        "raw": text,
        "unit": unit,
        "read_at": _now(),
    }


def _read_adapter(env: dict[str, str], source: str) -> dict[str, Any] | None:
    if source == "mock":
        return _mock_reading(env)
    if source == "rs232_serial":
        return _rs232_reading(env)
    if source == "usb_hid":
        return {"error": "usb_hid_plugin_not_enabled", "read_at": _now()}
    return None


def _scale_source(env: dict[str, str]) -> str:
    source = (env.get("PACKVISION_SCALE_SOURCE") or "manual_entry").strip().lower()
    return source if source in SCALE_SOURCES else "manual_entry"


def _mock_reading(env: dict[str, str]) -> dict[str, Any] | None:
    try:
        weight = float(env.get("PACKVISION_MOCK_SCALE_KG") or "")
    except ValueError:
        return {"error": "mock_weight_invalid", "read_at": _now()}
    if weight <= 0:
        return None
    return {
        "weight_kg": round(weight, 3),
        "stable": True,
        "raw": f"{weight:.3f} kg",
        "unit": "kg",
        "read_at": _now(),
    }


def _rs232_reading(env: dict[str, str]) -> dict[str, Any]:
    port = (env.get("PACKVISION_SCALE_SERIAL_PORT") or "").strip()
    if not port:
        return {"error": "serial_port_missing", "read_at": _now()}
    serial_module = _serial_module()
    if serial_module is None:
        return {"error": "pyserial_missing", "read_at": _now()}

    baudrate = _int_env(env, "PACKVISION_SCALE_SERIAL_BAUDRATE", DEFAULT_SERIAL_BAUDRATE)
    timeout_ms = _int_env(env, "PACKVISION_SCALE_SERIAL_TIMEOUT_MS", DEFAULT_SERIAL_TIMEOUT_MS)
    lines_to_read = _int_env(env, "PACKVISION_SCALE_SERIAL_READ_LINES", DEFAULT_SERIAL_READ_LINES)
    encoding = (env.get("PACKVISION_SCALE_SERIAL_ENCODING") or "ascii").strip() or "ascii"
    try:
        with serial_module.Serial(port=port, baudrate=baudrate, timeout=max(0.05, timeout_ms / 1000.0)) as handle:
            for _ in range(max(1, min(lines_to_read, 10))):
                line = handle.readline()
                text = _decode_serial_line(line, encoding)
                parsed = parse_scale_weight_line(text)
                if parsed:
                    parsed.update({"port": port, "baudrate": baudrate})
                    return parsed
    except Exception as exc:  # pragma: no cover - depends on Windows hardware and drivers.
        return {"error": f"serial_read_failed:{type(exc).__name__}", "detail": str(exc), "read_at": _now()}
    return {"error": "serial_no_parseable_weight", "read_at": _now()}


def _serial_module() -> Any | None:
    try:
        import serial  # type: ignore[import-not-found]

        return serial
    except Exception:
        return None


def _decode_serial_line(line: Any, encoding: str) -> str:
    if isinstance(line, bytes):
        return line.decode(encoding, errors="ignore").strip()
    return str(line or "").strip()


def _stable_from_text(text: str) -> bool:
    lowered = text.lower()
    if "unstable" in lowered or re.search(r"\bus\b", lowered):
        return False
    if "stable" in lowered or re.search(r"\bst\b", lowered):
        return True
    return True


def _status(source: str, reading: dict[str, Any] | None) -> str:
    if reading and reading.get("weight_kg"):
        return "auto_weight_ready" if reading.get("stable") else "auto_weight_unstable"
    if reading and reading.get("error"):
        if reading["error"] in {"pyserial_missing", "usb_hid_plugin_not_enabled"}:
            return "adapter_dependency_missing"
        return "adapter_error"
    if source == "manual_entry":
        return "manual_ready"
    return "adapter_configured_waiting"


def _adapter_config(env: dict[str, str], source: str) -> dict[str, Any]:
    if source == "rs232_serial":
        return {
            "port": env.get("PACKVISION_SCALE_SERIAL_PORT"),
            "baudrate": _int_env(env, "PACKVISION_SCALE_SERIAL_BAUDRATE", DEFAULT_SERIAL_BAUDRATE),
            "timeout_ms": _int_env(env, "PACKVISION_SCALE_SERIAL_TIMEOUT_MS", DEFAULT_SERIAL_TIMEOUT_MS),
            "read_lines": _int_env(env, "PACKVISION_SCALE_SERIAL_READ_LINES", DEFAULT_SERIAL_READ_LINES),
        }
    if source == "mock":
        return {"mock_weight_kg": env.get("PACKVISION_MOCK_SCALE_KG")}
    return {}


def _adapters(env: dict[str, str], active_source: str) -> list[dict[str, Any]]:
    serial_available = _serial_module() is not None
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
            "id": "rs232_serial",
            "label": "RS232 serial scale adapter",
            "available": serial_available and bool(env.get("PACKVISION_SCALE_SERIAL_PORT")),
            "active": active_source == "rs232_serial",
            "requires": [
                "PACKVISION_SCALE_SOURCE=rs232_serial",
                "PACKVISION_SCALE_SERIAL_PORT=COMx",
                "PACKVISION_SCALE_SERIAL_BAUDRATE=9600",
            ],
        },
        {
            "id": "usb_hid",
            "label": "USB HID scale adapter",
            "available": env.get("PACKVISION_SCALE_HID_ENABLED") == "1",
            "active": active_source == "usb_hid",
            "requires": ["PACKVISION_SCALE_SOURCE=usb_hid", "future_hid_plugin"],
        },
    ]


def _error_actions(error: str) -> list[str]:
    if error == "serial_port_missing":
        return ["set_packvision_scale_serial_port", "type_actual_weight_manually"]
    if error == "pyserial_missing":
        return ["install_pyserial_or_use_packaged_exe", "type_actual_weight_manually"]
    if error.startswith("serial_read_failed"):
        return ["check_scale_power_and_com_port", "check_usb_rs232_adapter_driver", "type_actual_weight_manually"]
    if error == "serial_no_parseable_weight":
        return ["check_scale_print_protocol", "adjust_scale_serial_baudrate", "type_actual_weight_manually"]
    return ["type_actual_weight_manually", "configure_packvision_scale_source_when_hardware_arrives"]


def _int_env(env: dict[str, str], key: str, default: int) -> int:
    try:
        return int(env.get(key) or default)
    except (TypeError, ValueError):
        return default


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
