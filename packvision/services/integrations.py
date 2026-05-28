from __future__ import annotations

import csv
import io
import json
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any

from packvision.services.history import db_path


OUTBOX_COLUMNS = (
    "event_id",
    "created_at",
    "updated_at",
    "next_attempt_at",
    "target",
    "event_type",
    "status",
    "retry_count",
    "measurement_id",
    "order_id",
    "barcode_text",
    "last_error",
    "last_response",
)


def init_integration_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS integration_outbox (
                event_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                next_attempt_at TEXT NOT NULL,
                target TEXT NOT NULL,
                event_type TEXT NOT NULL,
                status TEXT NOT NULL,
                retry_count INTEGER NOT NULL DEFAULT 0,
                measurement_id TEXT NOT NULL,
                order_id TEXT,
                barcode_text TEXT,
                payload_json TEXT NOT NULL,
                last_error TEXT,
                last_response TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_outbox_measurement_target_type
            ON integration_outbox(measurement_id, target, event_type)
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_outbox_status_next ON integration_outbox(status, next_attempt_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_outbox_created ON integration_outbox(created_at DESC)")


def enqueue_measurement_event(result: dict[str, Any], *, target: str = "wms_tms") -> dict[str, Any]:
    init_integration_db()
    now = _now()
    payload = _measurement_payload(result)
    event_id = f"{target}-{payload['measurement_id']}"
    with _connect() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO integration_outbox (
                event_id, created_at, updated_at, next_attempt_at, target, event_type,
                status, retry_count, measurement_id, order_id, barcode_text, payload_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                now,
                now,
                now,
                target,
                "measurement.created",
                "pending",
                0,
                payload["measurement_id"],
                payload.get("order_id"),
                payload.get("barcode_text"),
                json.dumps(payload, ensure_ascii=False, sort_keys=True),
            ),
        )
        row = conn.execute("SELECT * FROM integration_outbox WHERE event_id = ?", (event_id,)).fetchone()
    return _row_to_event(row)


def list_outbox_events(
    *,
    status: str | None = None,
    order_id: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    init_integration_db()
    limit = max(1, min(int(limit), 500))
    query = "SELECT * FROM integration_outbox"
    params: list[Any] = []
    filters: list[str] = []
    if status:
        filters.append("status = ?")
        params.append(_normalize_status(status))
    if order_id:
        filters.append("(order_id LIKE ? OR barcode_text LIKE ?)")
        params.extend([f"%{order_id}%", f"%{order_id}%"])
    if filters:
        query += " WHERE " + " AND ".join(filters)
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    with _connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return {"summary": outbox_summary(), "items": [_row_to_event(row) for row in rows]}


def outbox_summary() -> dict[str, Any]:
    init_integration_db()
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT status, COUNT(*) AS count
            FROM integration_outbox
            GROUP BY status
            """
        ).fetchall()
        due = conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM integration_outbox
            WHERE status IN ('pending', 'failed') AND next_attempt_at <= ?
            """,
            (_now(),),
        ).fetchone()
        latest = conn.execute(
            """
            SELECT event_id, status, updated_at
            FROM integration_outbox
            ORDER BY updated_at DESC
            LIMIT 1
            """
        ).fetchone()
    by_status = {row["status"]: int(row["count"]) for row in rows}
    return {
        "total": sum(by_status.values()),
        "pending": by_status.get("pending", 0),
        "sent": by_status.get("sent", 0),
        "failed": by_status.get("failed", 0),
        "due_for_retry": int(due["count"] if due else 0),
        "latest_event": dict(latest) if latest else None,
        "delivery_mode": "local_outbox",
    }


def update_outbox_event(
    event_id: str,
    *,
    status: str,
    response: str | None = None,
    error: str | None = None,
    retry_after_seconds: int | None = None,
) -> dict[str, Any]:
    init_integration_db()
    normalized = _normalize_status(status)
    if normalized not in {"pending", "sent", "failed"}:
        raise ValueError("status must be pending, sent, or failed.")
    now = _now()
    next_attempt = _next_attempt(now, retry_after_seconds) if normalized != "sent" else now
    retry_delta = 1 if normalized == "failed" else 0
    with _connect() as conn:
        existing = conn.execute("SELECT event_id FROM integration_outbox WHERE event_id = ?", (event_id,)).fetchone()
        if not existing:
            raise KeyError(event_id)
        conn.execute(
            """
            UPDATE integration_outbox
            SET status = ?, updated_at = ?, next_attempt_at = ?,
                retry_count = retry_count + ?, last_error = ?, last_response = ?
            WHERE event_id = ?
            """,
            (normalized, now, next_attempt, retry_delta, error, response, event_id),
        )
        row = conn.execute("SELECT * FROM integration_outbox WHERE event_id = ?", (event_id,)).fetchone()
    return _row_to_event(row)


def export_outbox_csv(limit: int = 500, status: str | None = None) -> str:
    data = list_outbox_events(status=status, limit=limit)
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=OUTBOX_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    for item in data["items"]:
        writer.writerow({column: item.get(column) for column in OUTBOX_COLUMNS})
    return buffer.getvalue()


def _measurement_payload(result: dict[str, Any]) -> dict[str, Any]:
    industry = result.get("industry_profile") if isinstance(result.get("industry_profile"), dict) else {}
    dims = result.get("dimensions") if isinstance(result.get("dimensions"), dict) else {}
    method = result.get("method") if isinstance(result.get("method"), dict) else {}
    return {
        "schema": "packvision.measurement.v1",
        "measurement_id": str(result.get("measurement_id") or ""),
        "created_at": result.get("created_at"),
        "order_id": result.get("order_id"),
        "barcode_text": result.get("barcode_text"),
        "status": result.get("status"),
        "confidence": result.get("confidence"),
        "measurement_source": result.get("measurement_source"),
        "measurement_method": method.get("name") or result.get("measurement_method"),
        "dimensions": {
            "length_mm": dims.get("length_mm"),
            "width_mm": dims.get("width_mm"),
            "height_mm": dims.get("height_mm"),
            "volume_l": dims.get("volume_l"),
        },
        "package": {
            "part_category": result.get("part_category"),
            "package_hint": result.get("package_hint"),
            "material_hint": result.get("material_hint"),
            "package_class": industry.get("package_class"),
            "recommended_capture_mode": industry.get("recommended_capture_mode"),
        },
        "billing": {
            "actual_weight_kg": result.get("actual_weight_kg") or industry.get("actual_weight_kg"),
            "volumetric_weight_kg": industry.get("volumetric_weight_kg") or result.get("volumetric_weight_kg"),
            "volumetric_rule_id": industry.get("volumetric_rule_id") or result.get("volumetric_rule_id"),
            "billing_weight_source": industry.get("billing_weight_source") or result.get("billing_weight_source"),
            "chargeable_weight_kg": industry.get("chargeable_weight_kg") or result.get("chargeable_weight_kg"),
        },
        "artifacts": result.get("artifacts") if isinstance(result.get("artifacts"), dict) else {},
    }


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    return conn


def _row_to_event(row: sqlite3.Row | None) -> dict[str, Any]:
    if row is None:
        return {}
    item = dict(row)
    payload = item.pop("payload_json", "{}")
    try:
        item["payload"] = json.loads(payload)
    except json.JSONDecodeError:
        item["payload"] = {}
    return item


def _normalize_status(value: str) -> str:
    return str(value or "pending").strip().lower()


def _next_attempt(now: str, retry_after_seconds: int | None) -> str:
    seconds = max(0, min(int(retry_after_seconds or 0), 7 * 24 * 60 * 60))
    base = datetime.fromisoformat(now)
    return (base + timedelta(seconds=seconds)).isoformat()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
