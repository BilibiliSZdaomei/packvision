from __future__ import annotations

import csv
import io
import json
import sqlite3
from pathlib import Path
from typing import Any

from packvision.services.storage import app_data_dir


EXTRA_COLUMNS = {
    "part_category": "TEXT",
    "package_hint": "TEXT",
    "material_hint": "TEXT",
    "package_class": "TEXT",
    "recommended_capture_mode": "TEXT",
    "chargeable_weight_kg": "REAL",
    "measurement_method": "TEXT",
}

HISTORY_COLUMNS = (
    "measurement_id",
    "created_at",
    "order_id",
    "barcode_text",
    "part_category",
    "package_hint",
    "material_hint",
    "package_class",
    "recommended_capture_mode",
    "status",
    "confidence",
    "measurement_method",
    "length_mm",
    "width_mm",
    "height_mm",
    "volume_l",
    "chargeable_weight_kg",
    "top_result_url",
    "side_result_url",
)


def db_path() -> Path:
    path = app_data_dir() / "packvision.sqlite3"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS measurements (
                measurement_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                order_id TEXT,
                barcode_text TEXT,
                status TEXT NOT NULL,
                confidence REAL NOT NULL,
                length_mm REAL,
                width_mm REAL,
                height_mm REAL,
                volume_l REAL,
                top_upload TEXT,
                side_upload TEXT,
                top_result_url TEXT,
                side_result_url TEXT,
                result_json TEXT NOT NULL
            )
            """
        )
        _ensure_columns(conn)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_measurements_created_at ON measurements(created_at DESC)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_measurements_order_id ON measurements(order_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_measurements_package_class ON measurements(package_class)")


def save_measurement(result: dict[str, Any]) -> None:
    init_db()
    dims = result.get("dimensions") or {}
    artifacts = result.get("artifacts") or {}
    top_view = result.get("top_view") or {}
    side_view = result.get("side_view") or {}
    industry_profile = result.get("industry_profile") or {}
    method = result.get("method") or {}
    with _connect() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO measurements (
                measurement_id, created_at, order_id, barcode_text, status, confidence,
                length_mm, width_mm, height_mm, volume_l, top_upload, side_upload,
                top_result_url, side_result_url, result_json, part_category, package_hint,
                material_hint, package_class, recommended_capture_mode, chargeable_weight_kg, measurement_method
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result["measurement_id"],
                result["created_at"],
                result.get("order_id"),
                result.get("barcode_text"),
                result["status"],
                result["confidence"],
                dims.get("length_mm"),
                dims.get("width_mm"),
                dims.get("height_mm"),
                dims.get("volume_l"),
                artifacts.get("top_upload"),
                artifacts.get("side_upload"),
                top_view.get("annotated_image_url"),
                side_view.get("annotated_image_url"),
                json.dumps(result, ensure_ascii=False),
                result.get("part_category"),
                result.get("package_hint"),
                result.get("material_hint"),
                industry_profile.get("package_class"),
                industry_profile.get("recommended_capture_mode"),
                industry_profile.get("chargeable_weight_kg"),
                method.get("name") or result.get("measurement_method"),
            ),
        )


def list_measurements(limit: int = 50, order_id: str | None = None) -> list[dict[str, Any]]:
    init_db()
    limit = max(1, min(limit, 500))
    query = """
        SELECT measurement_id, created_at, order_id, barcode_text, status, confidence,
               part_category, package_hint, material_hint, package_class, recommended_capture_mode,
               length_mm, width_mm, height_mm, volume_l, chargeable_weight_kg,
               measurement_method,
               top_result_url, side_result_url
        FROM measurements
    """
    params: list[Any] = []
    if order_id:
        query += " WHERE order_id LIKE ?"
        params.append(f"%{order_id}%")
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    with _connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def export_measurements_csv(limit: int = 500, order_id: str | None = None) -> str:
    rows = list_measurements(limit=limit, order_id=order_id)
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=HISTORY_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({column: row.get(column) for column in HISTORY_COLUMNS})
    return buffer.getvalue()


def get_measurement(measurement_id: str) -> dict[str, Any] | None:
    init_db()
    with _connect() as conn:
        row = conn.execute(
            "SELECT result_json FROM measurements WHERE measurement_id = ?",
            (measurement_id,),
        ).fetchone()
    if not row:
        return None
    return json.loads(row["result_json"])


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_columns(conn: sqlite3.Connection) -> None:
    existing = {row["name"] for row in conn.execute("PRAGMA table_info(measurements)").fetchall()}
    for name, column_type in EXTRA_COLUMNS.items():
        if name not in existing:
            conn.execute(f"ALTER TABLE measurements ADD COLUMN {name} {column_type}")
