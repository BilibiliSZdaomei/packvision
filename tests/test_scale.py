from packvision.services.scale import build_scale_status, read_scale_weight


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
