from __future__ import annotations

import base64
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Any
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from packvision import __version__
from packvision.services.barcode import detect_codes
from packvision.services.history import get_measurement, init_db, list_measurements, save_measurement
from packvision.services.measurement import (
    MeasurementConfig,
    MeasurementError,
    generate_calibration_svg,
    generate_demo_image,
    measure_images,
    opencv_ready,
)
from packvision.services.storage import ensure_data_dirs, resource_path, write_bytes


STATIC_DIR = resource_path("static")
MAX_UPLOAD_BYTES = 15 * 1024 * 1024


class ScanPayload(BaseModel):
    order_id: str | None = None
    barcode_text: str | None = None


def create_app() -> FastAPI:
    app = FastAPI(title="PackVision Local", version=__version__)
    dirs = ensure_data_dirs()
    init_db()
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    app.mount("/results", StaticFiles(directory=dirs["results"]), name="results")

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/api/health")
    def health() -> dict[str, object]:
        return {
            "ok": True,
            "version": __version__,
            "opencv_aruco": opencv_ready(),
            "history_db": True,
        }

    @app.get("/api/calibration-card.svg", response_class=HTMLResponse)
    def calibration_card(marker_size_mm: float = 50.0) -> Response:
        try:
            svg = generate_calibration_svg(marker_size_mm=marker_size_mm)
        except MeasurementError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        return Response(content=svg, media_type="image/svg+xml")

    @app.get("/api/demo-image.jpg")
    def demo_image() -> Response:
        try:
            image = generate_demo_image()
        except MeasurementError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        return Response(content=image, media_type="image/jpeg")

    @app.post("/api/measure")
    async def measure(
        top_image: Annotated[UploadFile, File()],
        side_image: Annotated[UploadFile | None, File()] = None,
        marker_size_mm: Annotated[float, Form()] = 50.0,
        manual_height_mm: Annotated[float | None, Form()] = None,
        camera_distance_mm: Annotated[float | None, Form()] = None,
        focal_length_35mm: Annotated[float | None, Form()] = None,
        top_box_json: Annotated[str | None, Form()] = None,
        side_box_json: Annotated[str | None, Form()] = None,
        order_id: Annotated[str | None, Form()] = None,
        barcode_text: Annotated[str | None, Form()] = None,
    ) -> dict[str, object]:
        if marker_size_mm <= 0:
            raise HTTPException(status_code=422, detail="marker_size_mm must be positive.")

        top_bytes = await top_image.read()
        side_bytes = await side_image.read() if side_image else None
        if not top_bytes:
            raise HTTPException(status_code=422, detail="top_image is required.")
        if len(top_bytes) > MAX_UPLOAD_BYTES or (side_bytes and len(side_bytes) > MAX_UPLOAD_BYTES):
            raise HTTPException(status_code=413, detail="Each image must be 15 MB or smaller.")

        top_path = write_bytes(dirs["uploads"], _suffix(top_image.filename), top_bytes)
        side_path = None
        if side_bytes and side_image:
            side_path = write_bytes(dirs["uploads"], _suffix(side_image.filename), side_bytes)

        try:
            result = measure_images(
                top_bytes,
                side_image_bytes=side_bytes,
                config=MeasurementConfig(
                    marker_size_mm=marker_size_mm,
                    manual_height_mm=manual_height_mm,
                    camera_distance_mm=camera_distance_mm,
                    focal_length_35mm=focal_length_35mm,
                    top_box_points=_parse_points(top_box_json, "top_box_json"),
                    side_box_points=_parse_points(side_box_json, "side_box_json"),
                ),
            )
        except MeasurementError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        top_annotated = result["top_view"].pop("annotated_image_base64")
        top_annotated_path = write_bytes(
            dirs["results"],
            ".jpg",
            base64.b64decode(top_annotated),
        )
        result["top_view"]["annotated_image_url"] = f"/results/{top_annotated_path.name}"

        if result.get("side_view"):
            side_annotated = result["side_view"].pop("annotated_image_base64")
            side_annotated_path = write_bytes(
                dirs["results"],
                ".jpg",
                base64.b64decode(side_annotated),
            )
            result["side_view"]["annotated_image_url"] = f"/results/{side_annotated_path.name}"

        result["measurement_id"] = uuid4().hex[:12]
        result["created_at"] = datetime.now(timezone.utc).isoformat()
        result["order_id"] = _clean_text(order_id)
        result["barcode_text"] = _clean_text(barcode_text)
        result["artifacts"] = {
            "top_upload": str(top_path),
            "side_upload": str(side_path) if side_path else None,
        }
        save_measurement(result)
        return result

    @app.get("/api/history")
    def history(limit: int = 50, order_id: str | None = None) -> dict[str, object]:
        return {"items": list_measurements(limit=limit, order_id=_clean_text(order_id))}

    @app.get("/api/history/{measurement_id}")
    def history_detail(measurement_id: str) -> dict[str, object]:
        result = get_measurement(measurement_id)
        if not result:
            raise HTTPException(status_code=404, detail="Measurement not found.")
        return result

    @app.post("/api/orders/scan")
    def scan_order(payload: ScanPayload) -> dict[str, object]:
        barcode = _clean_text(payload.barcode_text) or _clean_text(payload.order_id)
        order = _clean_text(payload.order_id) or barcode
        if not order:
            raise HTTPException(status_code=422, detail="order_id or barcode_text is required.")
        return {
            "order_id": order,
            "barcode_text": barcode,
            "source": "scanner_or_manual",
        }

    @app.post("/api/orders/decode-image")
    async def decode_order_image(order_image: Annotated[UploadFile, File()]) -> dict[str, object]:
        content = await order_image.read()
        if not content:
            raise HTTPException(status_code=422, detail="order_image is required.")
        if len(content) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="Image must be 15 MB or smaller.")
        return detect_codes(content)

    return app


def _parse_points(raw: str | None, field_name: str) -> list[list[float]] | None:
    if not raw:
        return None
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=422, detail=f"{field_name} must be valid JSON.") from exc
    if not isinstance(value, list):
        raise HTTPException(status_code=422, detail=f"{field_name} must be a JSON array.")

    points: list[list[float]] = []
    for item in value:
        if not isinstance(item, list | tuple) or len(item) != 2:
            raise HTTPException(status_code=422, detail=f"{field_name} points must be [x, y].")
        try:
            points.append([float(item[0]), float(item[1])])
        except (TypeError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=f"{field_name} coordinates must be numbers.") from exc
    if len(points) not in {2, 4}:
        raise HTTPException(status_code=422, detail=f"{field_name} must contain 2 or 4 points.")
    return points


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _suffix(filename: str | None) -> str:
    if not filename:
        return ".jpg"
    suffix = Path(filename).suffix.lower()
    return suffix if suffix in {".jpg", ".jpeg", ".png", ".webp", ".bmp"} else ".jpg"
