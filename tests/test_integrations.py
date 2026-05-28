from uuid import uuid4

from packvision.services.integrations import (
    dispatch_outbox_events,
    enqueue_measurement_event,
    integration_dispatch_status,
    list_outbox_events,
)


def _measurement(order_id: str) -> dict:
    return {
        "measurement_id": f"MEAS-{uuid4().hex}",
        "created_at": "2026-05-28T00:00:00+00:00",
        "order_id": order_id,
        "barcode_text": order_id,
        "status": "measured",
        "confidence": 0.92,
        "measurement_source": "test",
        "dimensions": {"length_mm": 500, "width_mm": 300, "height_mm": 200, "volume_l": 30},
        "industry_profile": {"chargeable_weight_kg": 6.0, "billing_weight_source": "volumetric_weight"},
    }


def test_integration_dispatch_status_is_safe_without_endpoint():
    status = integration_dispatch_status({})

    assert status["status"] == "not_configured"
    assert status["delivery_mode"] == "local_outbox"
    assert status["token_configured"] is False
    assert "set_packvision_integration_http_url_when_wms_tms_is_ready" in status["next_actions"]


def test_dispatch_outbox_events_marks_dry_run_as_sent():
    target = f"test_{uuid4().hex}"
    order_id = f"DRY-{uuid4().hex[:8]}"
    event = enqueue_measurement_event(_measurement(order_id), target=target)

    result = dispatch_outbox_events(
        env={"PACKVISION_INTEGRATION_DRY_RUN": "1", "PACKVISION_INTEGRATION_TARGET": target},
        limit=10,
    )

    assert result["status"] == "dispatched"
    assert result["sent"] == 1
    assert result["events"][0]["event_id"] == event["event_id"]
    saved = list_outbox_events(order_id=order_id)["items"][0]
    assert saved["status"] == "sent"
    assert "dry_run_sent" in saved["last_response"]


def test_dispatch_outbox_events_posts_payload_and_auth_header():
    target = f"test_{uuid4().hex}"
    order_id = f"HTTP-{uuid4().hex[:8]}"
    event = enqueue_measurement_event(_measurement(order_id), target=target)
    captured = {}

    def fake_post(url, payload, headers, timeout_ms):
        captured.update({"url": url, "payload": payload, "headers": headers, "timeout_ms": timeout_ms})
        return {"status_code": 202, "body": "accepted"}

    result = dispatch_outbox_events(
        env={
            "PACKVISION_INTEGRATION_HTTP_URL": "https://wms.example.test/events",
            "PACKVISION_INTEGRATION_HTTP_TOKEN": "secret-token",
            "PACKVISION_INTEGRATION_TARGET": target,
            "PACKVISION_INTEGRATION_TIMEOUT_MS": "1200",
        },
        limit=10,
        post_json=fake_post,
    )

    assert result["status"] == "dispatched"
    assert captured["url"] == "https://wms.example.test/events"
    assert captured["headers"]["Authorization"] == "Bearer secret-token"
    assert captured["headers"]["X-PackVision-Event-Id"] == event["event_id"]
    assert captured["timeout_ms"] == 1200
    assert captured["payload"]["schema"] == "packvision.integration_event.v1"
    assert captured["payload"]["payload"]["order_id"] == order_id


def test_dispatch_outbox_events_keeps_failed_event_for_retry():
    target = f"test_{uuid4().hex}"
    order_id = f"FAIL-{uuid4().hex[:8]}"
    event = enqueue_measurement_event(_measurement(order_id), target=target)

    result = dispatch_outbox_events(
        env={"PACKVISION_INTEGRATION_HTTP_URL": "https://wms.example.test/events", "PACKVISION_INTEGRATION_TARGET": target},
        limit=10,
        post_json=lambda *args: {"status_code": 503, "body": "down"},
    )

    assert result["status"] == "partial_failure"
    assert result["failed"] == 1
    saved = list_outbox_events(order_id=order_id)["items"][0]
    assert saved["event_id"] == event["event_id"]
    assert saved["status"] == "failed"
    assert saved["retry_count"] == 1
    assert "HTTP 503" in saved["last_error"]
