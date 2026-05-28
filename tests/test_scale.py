import sys
import types

from packvision.services.scale import build_scale_status, parse_scale_weight_line, read_scale_weight


def test_scale_status_keeps_manual_fallback_lightweight():
    status = build_scale_status({})

    assert status["status"] == "manual_ready"
    assert status["source"] == "manual_entry"
    assert status["weight_kg"] is None
    assert status["integration_policy"]["failure_behavior"] == "keep_manual_weight_input_available"
    assert any(adapter["id"] == "manual_entry" and adapter["available"] for adapter in status["adapters"])


def test_mock_scale_weight_supports_dry_run_without_hardware():
    env = {"PACKVISION_SCALE_SOURCE": "mock", "PACKVISION_MOCK_SCALE_KG": "7.35"}

    status = build_scale_status(env)
    reading = read_scale_weight(env)

    assert status["status"] == "auto_weight_ready"
    assert status["weight_kg"] == 7.35
    assert reading["status"] == "measured"
    assert reading["stable"] is True


def test_parse_scale_weight_line_supports_common_rs232_formats():
    assert parse_scale_weight_line("ST,GS,+   7.350kg")["weight_kg"] == 7.35
    assert parse_scale_weight_line("US,GS,+001250 g")["stable"] is False
    assert parse_scale_weight_line("ST,+ 10.0 lb")["weight_kg"] == 4.536


def test_rs232_scale_adapter_reads_serial_line(monkeypatch):
    class FakeSerial:
        def __init__(self, *args, **kwargs):
            self.lines = [b"ST,GS,+  6.420kg\r\n"]

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def readline(self):
            return self.lines.pop(0)

    fake_serial = types.SimpleNamespace(Serial=FakeSerial)
    monkeypatch.setitem(sys.modules, "serial", fake_serial)
    env = {
        "PACKVISION_SCALE_SOURCE": "rs232_serial",
        "PACKVISION_SCALE_SERIAL_PORT": "COM7",
        "PACKVISION_SCALE_SERIAL_BAUDRATE": "9600",
    }

    status = build_scale_status(env)
    reading = read_scale_weight(env)

    assert status["status"] == "auto_weight_ready"
    assert status["source"] == "rs232_serial"
    assert status["weight_kg"] == 6.42
    assert status["raw_reading"] == "ST,GS,+  6.420kg"
    assert reading["status"] == "measured"


def test_rs232_scale_adapter_keeps_manual_fallback_when_port_missing():
    env = {"PACKVISION_SCALE_SOURCE": "rs232_serial"}

    status = build_scale_status(env)
    reading = read_scale_weight(env)

    assert status["status"] == "adapter_error"
    assert status["adapter_error"] == "serial_port_missing"
    assert reading["status"] == "adapter_error"
    assert "type_actual_weight_manually" in reading["next_actions"]
