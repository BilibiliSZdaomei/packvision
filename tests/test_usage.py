from packvision.services.usage import record_usage_event, usage_summary


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
