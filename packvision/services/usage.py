from __future__ import annotations

import csv
import io
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from packvision.services.storage import app_data_dir


MEASUREMENT_ENDPOINTS = {
    "/api/measure",
    "/api/depth/demo-object",
    "/api/depth/demo-object/save",
    "/api/depth/measure-roi",
    "/api/depth/measure-object",
}

USAGE_COLUMNS = (
    "event_id",
    "created_at",
    "endpoint",
    "method",
    "status_code",
    "success",
    "duration_ms",
    "is_measurement",
    "order_id",
    "measurement_id",
    "measurement_source",
    "error_message",
)


def usage_db_path() -> Path:
    path = app_data_dir() / "packvision.sqlite3"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def init_usage_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS usage_events (
                event_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                method TEXT NOT NULL,
                status_code INTEGER NOT NULL,
                success INTEGER NOT NULL,
                duration_ms REAL,
                is_measurement INTEGER NOT NULL,
                order_id TEXT,
                measurement_id TEXT,
                measurement_source TEXT,
                error_message TEXT,
                extra_json TEXT NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_usage_events_created_at ON usage_events(created_at DESC)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_usage_events_endpoint ON usage_events(endpoint)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_usage_events_is_measurement ON usage_events(is_measurement)")


def should_record_usage(endpoint: str) -> bool:
    return endpoint.startswith("/api/") and not endpoint.startswith("/api/usage")


def record_usage_event(
    *,
    endpoint: str,
    method: str,
    status_code: int,
    success: bool | None = None,
    duration_ms: float | None = None,
    order_id: str | None = None,
    measurement_id: str | None = None,
    measurement_source: str | None = None,
    error_message: str | None = None,
    extra: dict[str, Any] | None = None,
    created_at: str | None = None,
) -> str:
    init_usage_db()
    event_id = uuid4().hex
    clean_endpoint = _clean_text(endpoint) or "/api/unknown"
    status = int(status_code)
    is_success = (status < 400) if success is None else bool(success)
    event_time = created_at or datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO usage_events (
                event_id, created_at, endpoint, method, status_code, success, duration_ms,
                is_measurement, order_id, measurement_id, measurement_source, error_message, extra_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                event_time,
                clean_endpoint,
                method.upper(),
                status,
                1 if is_success else 0,
                round(float(duration_ms), 3) if duration_ms is not None else None,
                1 if clean_endpoint in MEASUREMENT_ENDPOINTS else 0,
                _clean_text(order_id),
                _clean_text(measurement_id),
                _clean_text(measurement_source),
                _clean_text(error_message),
                json.dumps(extra or {}, ensure_ascii=False),
            ),
        )
    return event_id


def list_usage_events(
    *,
    limit: int = 100,
    endpoint: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> list[dict[str, Any]]:
    init_usage_db()
    limit = max(1, min(limit, 1000))
    where, params = _filters(endpoint=endpoint, date_from=date_from, date_to=date_to)
    query = f"""
        SELECT event_id, created_at, endpoint, method, status_code, success, duration_ms,
               is_measurement, order_id, measurement_id, measurement_source, error_message, extra_json
        FROM usage_events
        {where}
        ORDER BY created_at DESC
        LIMIT ?
    """
    params.append(limit)
    with _connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return [_row_to_event(row) for row in rows]


def usage_summary(
    *,
    endpoint: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> dict[str, Any]:
    init_usage_db()
    where, params = _filters(endpoint=endpoint, date_from=date_from, date_to=date_to)
    with _connect() as conn:
        totals = conn.execute(
            f"""
            SELECT COUNT(*) AS total_calls,
                   COALESCE(SUM(success), 0) AS successful_calls,
                   COALESCE(SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END), 0) AS failed_calls,
                   COALESCE(SUM(is_measurement), 0) AS measurement_calls,
                   MIN(created_at) AS first_event_at,
                   MAX(created_at) AS last_event_at
            FROM usage_events
            {where}
            """,
            params,
        ).fetchone()
        by_endpoint = conn.execute(
            f"""
            SELECT endpoint, method, COUNT(*) AS call_count,
                   COALESCE(SUM(success), 0) AS successful_calls,
                   COALESCE(SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END), 0) AS failed_calls,
                   COALESCE(SUM(is_measurement), 0) AS measurement_calls,
                   ROUND(AVG(duration_ms), 3) AS avg_duration_ms
            FROM usage_events
            {where}
            GROUP BY endpoint, method
            ORDER BY call_count DESC, endpoint ASC
            """,
            params,
        ).fetchall()
        by_day = conn.execute(
            f"""
            SELECT SUBSTR(created_at, 1, 10) AS day, COUNT(*) AS call_count,
                   COALESCE(SUM(is_measurement), 0) AS measurement_calls
            FROM usage_events
            {where}
            GROUP BY day
            ORDER BY day DESC
            """,
            params,
        ).fetchall()

    return {
        "total_calls": int(totals["total_calls"] or 0),
        "successful_calls": int(totals["successful_calls"] or 0),
        "failed_calls": int(totals["failed_calls"] or 0),
        "measurement_calls": int(totals["measurement_calls"] or 0),
        "first_event_at": totals["first_event_at"],
        "last_event_at": totals["last_event_at"],
        "by_endpoint": [_summary_row(row) for row in by_endpoint],
        "by_day": [dict(row) for row in by_day],
    }


def export_usage_csv(
    *,
    limit: int = 1000,
    endpoint: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> str:
    rows = list_usage_events(limit=limit, endpoint=endpoint, date_from=date_from, date_to=date_to)
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=USAGE_COLUMNS, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({column: row.get(column) for column in USAGE_COLUMNS})
    return buffer.getvalue()


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(usage_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def _filters(
    *,
    endpoint: str | None,
    date_from: str | None,
    date_to: str | None,
) -> tuple[str, list[Any]]:
    clauses: list[str] = []
    params: list[Any] = []
    if _clean_text(endpoint):
        clauses.append("endpoint = ?")
        params.append(_clean_text(endpoint))
    if _clean_text(date_from):
        clauses.append("created_at >= ?")
        params.append(_normalize_date_bound(_clean_text(date_from), is_end=False))
    if _clean_text(date_to):
        clauses.append("created_at <= ?")
        params.append(_normalize_date_bound(_clean_text(date_to), is_end=True))
    return (f"WHERE {' AND '.join(clauses)}" if clauses else "", params)


def _row_to_event(row: sqlite3.Row) -> dict[str, Any]:
    event = dict(row)
    event["success"] = bool(event["success"])
    event["is_measurement"] = bool(event["is_measurement"])
    event["extra"] = json.loads(event.pop("extra_json") or "{}")
    return event


def _summary_row(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "endpoint": row["endpoint"],
        "method": row["method"],
        "call_count": int(row["call_count"] or 0),
        "successful_calls": int(row["successful_calls"] or 0),
        "failed_calls": int(row["failed_calls"] or 0),
        "measurement_calls": int(row["measurement_calls"] or 0),
        "avg_duration_ms": row["avg_duration_ms"],
    }


def _clean_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _normalize_date_bound(value: str | None, *, is_end: bool) -> str | None:
    if value and len(value) == 10 and value[4] == "-" and value[7] == "-":
        suffix = "T23:59:59.999999+00:00" if is_end else "T00:00:00+00:00"
        return f"{value}{suffix}"
    return value
