from __future__ import annotations

import csv
import io
import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib import error, request
from urllib.parse import urlparse

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
DEFAULT_DISPATCH_LIMIT = 20
MAX_DISPATCH_LIMIT = 100
DEFAULT_HTTP_TIMEOUT_MS = 3000


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
    dispatch = integration_dispatch_status()
    return {
        "total": sum(by_status.values()),
        "pending": by_status.get("pending", 0),
        "sent": by_status.get("sent", 0),
        "failed": by_status.get("failed", 0),
        "due_for_retry": int(due["count"] if due else 0),
        "latest_event": dict(latest) if latest else None,
        "delivery_mode": dispatch["delivery_mode"],
        "dispatch": dispatch,
    }


def integration_dispatch_status(env: dict[str, str] | None = None) -> dict[str, Any]:
    values = env or os.environ
    endpoint = _integration_endpoint(values)
    dry_run = _bool_env(values, "PACKVISION_INTEGRATION_DRY_RUN")
    configured = bool(endpoint) or dry_run
    return {
        "status": "ready" if configured else "not_configured",
        "delivery_mode": "http_push" if endpoint else "local_outbox",
        "target": _integration_target(values),
        "endpoint_configured": bool(endpoint),
        "endpoint_host": _endpoint_host(endpoint),
        "token_configured": bool(values.get("PACKVISION_INTEGRATION_HTTP_TOKEN") or values.get("PACKVISION_WMS_TMS_TOKEN")),
        "dry_run": dry_run,
        "timeout_ms": _int_env(values, "PACKVISION_INTEGRATION_TIMEOUT_MS", DEFAULT_HTTP_TIMEOUT_MS),
        "batch_limit_default": DEFAULT_DISPATCH_LIMIT,
        "failure_behavior": "keep_event_in_outbox_and_retry_later",
        "required_env": [
            "PACKVISION_INTEGRATION_HTTP_URL",
            "PACKVISION_INTEGRATION_HTTP_TOKEN optional",
            "PACKVISION_INTEGRATION_TARGET optional",
        ],
        "next_actions": []
        if configured
        else [
            "set_packvision_integration_http_url_when_wms_tms_is_ready",
            "keep_using_local_outbox_and_csv_export_until_then",
        ],
    }


def dispatch_outbox_events(
    *,
    limit: int = DEFAULT_DISPATCH_LIMIT,
    env: dict[str, str] | None = None,
    post_json: Any | None = None,
) -> dict[str, Any]:
    init_integration_db()
    values = env or os.environ
    config = integration_dispatch_status(values)
    target = config["target"]
    limit = max(1, min(int(limit or DEFAULT_DISPATCH_LIMIT), MAX_DISPATCH_LIMIT))
    if config["status"] != "ready":
        return {
            "status": "not_configured",
            "dispatch": config,
            "attempted": 0,
            "sent": 0,
            "failed": 0,
            "events": [],
            "summary": outbox_summary(),
        }

    due_events = _due_outbox_events(target=target, limit=limit)
    if not due_events:
        return {
            "status": "no_due_events",
            "dispatch": config,
            "attempted": 0,
            "sent": 0,
            "failed": 0,
            "events": [],
            "summary": outbox_summary(),
        }

    poster = post_json or _post_json
    results: list[dict[str, Any]] = []
    sent = 0
    failed = 0
    for event in due_events:
        try:
            response = _dry_run_response(event) if config["dry_run"] else poster(
                _integration_endpoint(values),
                _dispatch_payload(event),
                _dispatch_headers(values, event),
                config["timeout_ms"],
            )
            if 200 <= int(response.get("status_code") or 0) < 300:
                updated = update_outbox_event(event["event_id"], status="sent", response=_response_excerpt(response))
                sent += 1
                results.append({"event_id": event["event_id"], "status": "sent", "updated": updated})
            else:
                retry_after = _retry_after_seconds(event)
                updated = update_outbox_event(
                    event["event_id"],
                    status="failed",
                    response=_response_excerpt(response),
                    error=f"HTTP {response.get('status_code')}",
                    retry_after_seconds=retry_after,
                )
                failed += 1
                results.append({"event_id": event["event_id"], "status": "failed", "retry_after_seconds": retry_after, "updated": updated})
        except Exception as exc:
            retry_after = _retry_after_seconds(event)
            updated = update_outbox_event(
                event["event_id"],
                status="failed",
                error=f"{type(exc).__name__}: {exc}",
                retry_after_seconds=retry_after,
            )
            failed += 1
            results.append({"event_id": event["event_id"], "status": "failed", "retry_after_seconds": retry_after, "updated": updated})

    return {
        "status": "dispatched" if failed == 0 else "partial_failure",
        "dispatch": config,
        "attempted": len(due_events),
        "sent": sent,
        "failed": failed,
        "events": results,
        "summary": outbox_summary(),
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


def _due_outbox_events(*, target: str, limit: int) -> list[dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM integration_outbox
            WHERE target = ? AND status IN ('pending', 'failed') AND next_attempt_at <= ?
            ORDER BY next_attempt_at ASC, created_at ASC
            LIMIT ?
            """,
            (target, _now(), limit),
        ).fetchall()
    return [_row_to_event(row) for row in rows]


def _dispatch_payload(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "packvision.integration_event.v1",
        "event_id": event.get("event_id"),
        "event_type": event.get("event_type"),
        "target": event.get("target"),
        "created_at": event.get("created_at"),
        "updated_at": event.get("updated_at"),
        "retry_count": event.get("retry_count"),
        "payload": event.get("payload") or {},
    }


def _dispatch_headers(env: dict[str, str], event: dict[str, Any]) -> dict[str, str]:
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json",
        "X-PackVision-Event-Id": str(event.get("event_id") or ""),
        "X-PackVision-Event-Type": str(event.get("event_type") or ""),
    }
    token = env.get("PACKVISION_INTEGRATION_HTTP_TOKEN") or env.get("PACKVISION_WMS_TMS_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _post_json(url: str, payload: dict[str, Any], headers: dict[str, str], timeout_ms: int) -> dict[str, Any]:
    data = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    req = request.Request(url, data=data, headers=headers, method="POST")
    try:
        with request.urlopen(req, timeout=max(0.1, timeout_ms / 1000.0)) as response:
            body = response.read(8192).decode("utf-8", errors="replace")
            return {"status_code": response.status, "body": body}
    except error.HTTPError as exc:
        body = exc.read(8192).decode("utf-8", errors="replace")
        return {"status_code": exc.code, "body": body}


def _dry_run_response(event: dict[str, Any]) -> dict[str, Any]:
    return {"status_code": 200, "body": f"dry_run_sent:{event.get('event_id')}"}


def _response_excerpt(response: dict[str, Any]) -> str:
    body = str(response.get("body") or "")
    return json.dumps(
        {
            "status_code": response.get("status_code"),
            "body": body[:1000],
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def _retry_after_seconds(event: dict[str, Any]) -> int:
    retry_count = int(event.get("retry_count") or 0)
    return min(3600, 60 * (2 ** min(retry_count, 5)))


def _integration_endpoint(env: dict[str, str]) -> str:
    return str(env.get("PACKVISION_INTEGRATION_HTTP_URL") or env.get("PACKVISION_WMS_TMS_URL") or "").strip()


def _integration_target(env: dict[str, str]) -> str:
    return str(env.get("PACKVISION_INTEGRATION_TARGET") or "wms_tms").strip() or "wms_tms"


def _endpoint_host(endpoint: str) -> str | None:
    if not endpoint:
        return None
    parsed = urlparse(endpoint)
    return parsed.netloc or parsed.path or None


def _bool_env(env: dict[str, str], key: str) -> bool:
    return str(env.get(key) or "").strip().lower() in {"1", "true", "yes", "on"}


def _int_env(env: dict[str, str], key: str, default: int) -> int:
    try:
        return int(env.get(key) or default)
    except (TypeError, ValueError):
        return default


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
