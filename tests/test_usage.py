from uuid import uuid4

from packvision.services.usage import export_usage_csv, record_usage_event, usage_summary


def test_usage_summary_date_to_includes_the_whole_day():
    endpoint = "/api/test-usage-date-filter"
    before = usage_summary(
        endpoint=endpoint,
        date_from="2026-05-31",
        date_to="2026-05-31",
    )["total_calls"]

    record_usage_event(
        endpoint=endpoint,
        method="POST",
        status_code=200,
        created_at="2026-05-31T23:59:00+00:00",
    )

    after = usage_summary(
        endpoint=endpoint,
        date_from="2026-05-31",
        date_to="2026-05-31",
    )["total_calls"]
    assert after == before + 1


def test_usage_export_includes_measurement_traceability_fields():
    endpoint = f"/api/test-usage-export-{uuid4().hex[:8]}"
    measurement_id = uuid4().hex[:12]
    order_id = f"ORDER-{uuid4().hex[:6]}"
    record_usage_event(
        endpoint=endpoint,
        method="POST",
        status_code=200,
        order_id=order_id,
        measurement_id=measurement_id,
        measurement_source="depth_roi_api",
    )

    csv_text = export_usage_csv(endpoint=endpoint)

    assert "order_id" in csv_text
    assert "measurement_id" in csv_text
    assert order_id in csv_text
    assert measurement_id in csv_text
    assert "depth_roi_api" in csv_text


def test_usage_counts_depth_measure_capture_as_measurement_call():
    endpoint = "/api/depth/measure-capture"
    before = usage_summary(endpoint=endpoint)["measurement_calls"]

    record_usage_event(endpoint=endpoint, method="POST", status_code=200)

    after = usage_summary(endpoint=endpoint)["measurement_calls"]
    assert after == before + 1


def test_usage_counts_depth_live_confirm_as_measurement_call():
    endpoint = "/api/depth/live/confirm"
    before = usage_summary(endpoint=endpoint)["measurement_calls"]

    record_usage_event(endpoint=endpoint, method="POST", status_code=200)

    after = usage_summary(endpoint=endpoint)["measurement_calls"]
    assert after == before + 1
