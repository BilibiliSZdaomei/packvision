from __future__ import annotations

import base64
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Any
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from packvision import __version__
from packvision.services.barcode import detect_codes
from packvision.services.capture_quality import CaptureQualityError, analyze_capture_quality
from packvision.services.depth_camera import depth_camera_status
from packvision.services.depth_capture import (
    DepthCaptureConfig,
    DepthCaptureError,
    depth_capture_capabilities,
    probe_depth_capture,
)
from packvision.services.depth_geometry import (
    DepthObjectConfig,
    DepthIntrinsics,
    DepthMeasurementConfig,
    DepthMeasurementError,
    measure_depth_object_mask,
    measure_depth_roi,
)
from packvision.services.depth_quality import DepthQualityError, analyze_depth_quality
from packvision.services.depth_workflow import build_depth_workflow_guide, recommend_capture_workflow
from packvision.services.history import (
    export_measurements_csv,
    get_measurement,
    init_db,
    list_measurements,
    save_measurement,
)
from packvision.services.industry import build_packaging_profile
from packvision.services.measurement import (
    MeasurementConfig,
    MeasurementError,
    generate_calibration_svg,
    generate_demo_image,
    measure_images,
    opencv_ready,
)
from packvision.services.storage import ensure_data_dirs, resource_path, write_bytes
from packvision.services.usage import (
    export_usage_csv,
    init_usage_db,
    list_usage_events,
    record_usage_event,
    should_record_usage,
    usage_summary,
)
from packvision.services.validation import (
    build_trial_plan,
    build_trial_template_csv,
    evaluate_trial_csv,
    evaluate_trial_run,
)


STATIC_DIR = resource_path("static")
MAX_UPLOAD_BYTES = 15 * 1024 * 1024


class ScanPayload(BaseModel):
    order_id: str | None = None
    barcode_text: str | None = None


class DepthIntrinsicsPayload(BaseModel):
    fx: float
    fy: float
    cx: float
    cy: float
    width: int
    height: int
    depth_scale: float = 1.0


class DepthTraceabilityPayload(BaseModel):
    order_id: str | None = None
    barcode_text: str | None = None
    part_category: str | None = None
    package_hint: str | None = None
    material_hint: str | None = None
    actual_weight_kg: float | None = None
    save_to_history: bool = False


class DepthMeasurePayload(DepthTraceabilityPayload):
    depth_frame: list[list[float]]
    intrinsics: DepthIntrinsicsPayload
    roi: list[int]
    background_roi: list[int] | None = None
    table_depth_mm: float | None = None
    min_valid_depth_mm: float = 50.0
    max_valid_depth_mm: float = 6000.0
    trim_ratio: float = 0.08


class DepthObjectMeasurePayload(DepthTraceabilityPayload):
    depth_frame: list[list[float]]
    intrinsics: DepthIntrinsicsPayload
    roi: list[int]
    background_roi: list[int] | None = None
    table_depth_mm: float | None = None
    min_valid_depth_mm: float = 50.0
    max_valid_depth_mm: float = 6000.0
    object_min_height_mm: float = 30.0
    trim_quantile: float = 0.02
    footprint_method: str = "axis_aligned"


class DepthCaptureProbePayload(BaseModel):
    backend: str = "auto"
    timeout_ms: int = 1500


class DepthQualityPayload(BaseModel):
    depth_frame: list[list[float]]
    roi: list[int] | None = None
    background_roi: list[int] | None = None
    min_valid_depth_mm: float = 50.0
    max_valid_depth_mm: float = 6000.0
    depth_scale: float = 1.0
    noise_check: bool = True


class IndustryProfilePayload(BaseModel):
    dimensions: dict[str, Any]
    part_category: str | None = None
    package_hint: str | None = None
    material_hint: str | None = None
    actual_weight_kg: float | None = None


class TrialRunEvaluationPayload(BaseModel):
    samples: list[dict[str, Any]]


def create_app() -> FastAPI:
    app = FastAPI(title="PackVision Local", version=__version__)
    dirs = ensure_data_dirs()
    init_db()
    init_usage_db()
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    app.mount("/results", StaticFiles(directory=dirs["results"]), name="results")

    @app.middleware("http")
    async def usage_logging_middleware(request: Request, call_next):
        endpoint = request.url.path
        should_log = should_record_usage(endpoint)
        started_at = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception as exc:
            if should_log:
                record_usage_event(
                    endpoint=endpoint,
                    method=request.method,
                    status_code=500,
                    success=False,
                    duration_ms=(time.perf_counter() - started_at) * 1000,
                    error_message=str(exc),
                )
            raise
        if should_log:
            trace = _usage_trace(request)
            record_usage_event(
                endpoint=endpoint,
                method=request.method,
                status_code=response.status_code,
                duration_ms=(time.perf_counter() - started_at) * 1000,
                order_id=trace.get("order_id"),
                measurement_id=trace.get("measurement_id"),
                measurement_source=trace.get("measurement_source"),
                extra=trace.get("extra"),
            )
        return response

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon() -> Response:
        return Response(status_code=204)

    @app.get("/api/health")
    def health() -> dict[str, object]:
        return {
            "ok": True,
            "version": __version__,
            "opencv_aruco": opencv_ready(),
            "history_db": True,
            "depth_camera": depth_camera_status(),
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
        request: Request,
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
        part_category: Annotated[str | None, Form()] = None,
        package_hint: Annotated[str | None, Form()] = None,
        material_hint: Annotated[str | None, Form()] = None,
        actual_weight_kg: Annotated[float | None, Form()] = None,
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
        result["part_category"] = _clean_text(part_category)
        result["package_hint"] = _clean_text(package_hint)
        result["material_hint"] = _clean_text(material_hint)
        result["actual_weight_kg"] = actual_weight_kg if actual_weight_kg and actual_weight_kg > 0 else None
        result["industry_profile"] = build_packaging_profile(
            result["dimensions"],
            part_category=result["part_category"],
            package_hint=result["package_hint"],
            material_hint=result["material_hint"],
            actual_weight_kg=result["actual_weight_kg"],
        )
        result["artifacts"] = {
            "top_upload": str(top_path),
            "side_upload": str(side_path) if side_path else None,
        }
        _set_usage_trace(request, result, measurement_source="image_measure_api")
        save_measurement(result)
        return result

    @app.get("/api/history")
    def history(limit: int = 50, order_id: str | None = None) -> dict[str, object]:
        return {"items": list_measurements(limit=limit, order_id=_clean_text(order_id))}

    @app.get("/api/history/export.csv")
    def history_export(limit: int = 500, order_id: str | None = None) -> Response:
        csv_text = export_measurements_csv(limit=limit, order_id=_clean_text(order_id))
        return Response(
            content=csv_text,
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": 'attachment; filename="packvision-history.csv"'},
        )

    @app.get("/api/history/{measurement_id}")
    def history_detail(measurement_id: str) -> dict[str, object]:
        result = get_measurement(measurement_id)
        if not result:
            raise HTTPException(status_code=404, detail="Measurement not found.")
        return result

    @app.get("/api/usage/summary")
    def usage_report(
        endpoint: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> dict[str, object]:
        return usage_summary(
            endpoint=_clean_text(endpoint),
            date_from=_clean_text(date_from),
            date_to=_clean_text(date_to),
        )

    @app.get("/api/usage/events")
    def usage_events(
        limit: int = 100,
        endpoint: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> dict[str, object]:
        return {
            "items": list_usage_events(
                limit=limit,
                endpoint=_clean_text(endpoint),
                date_from=_clean_text(date_from),
                date_to=_clean_text(date_to),
            )
        }

    @app.get("/api/usage/export.csv")
    def usage_export(
        limit: int = 1000,
        endpoint: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> Response:
        csv_text = export_usage_csv(
            limit=limit,
            endpoint=_clean_text(endpoint),
            date_from=_clean_text(date_from),
            date_to=_clean_text(date_to),
        )
        return Response(
            content=csv_text,
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": 'attachment; filename="packvision-usage.csv"'},
        )

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

    @app.post("/api/capture/quality")
    async def capture_quality(image: Annotated[UploadFile, File()]) -> dict[str, object]:
        content = await image.read()
        if not content:
            raise HTTPException(status_code=422, detail="image is required.")
        if len(content) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="Image must be 15 MB or smaller.")
        try:
            return analyze_capture_quality(content)
        except CaptureQualityError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.get("/api/depth/status")
    def depth_status() -> dict[str, object]:
        return depth_camera_status()

    @app.get("/api/depth/workflow-guide")
    def depth_workflow_guide(
        package_class: str = "standard_carton",
        material_class: str | None = None,
        camera_count: int = 1,
    ) -> dict[str, object]:
        return {
            "guide": build_depth_workflow_guide(),
            "recommended_workflow": recommend_capture_workflow(
                package_class=package_class,
                material_class=material_class,
                camera_count=camera_count,
            ),
        }

    @app.get("/api/depth/capture/capabilities")
    def depth_capture_capability_report() -> dict[str, object]:
        return depth_capture_capabilities()

    @app.post("/api/depth/capture/probe")
    def depth_capture_probe(payload: DepthCaptureProbePayload) -> dict[str, object]:
        try:
            return probe_depth_capture(
                DepthCaptureConfig(
                    backend=payload.backend,
                    timeout_ms=payload.timeout_ms,
                )
            )
        except DepthCaptureError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post("/api/depth/quality")
    def depth_quality(payload: DepthQualityPayload) -> dict[str, object]:
        try:
            return analyze_depth_quality(
                payload.depth_frame,
                roi=payload.roi,
                background_roi=payload.background_roi,
                min_valid_depth_mm=payload.min_valid_depth_mm,
                max_valid_depth_mm=payload.max_valid_depth_mm,
                depth_scale=payload.depth_scale,
                noise_check=payload.noise_check,
            )
        except DepthQualityError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.get("/api/depth/demo-object")
    def depth_demo_object(request: Request) -> dict[str, object]:
        result = _finalize_depth_result(
            _depth_demo_object_result(),
            DepthTraceabilityPayload(
                part_category="bumper_trim",
                package_hint="irregular",
                actual_weight_kg=4.6,
            ),
            measurement_source="depth_demo_object",
        )
        _set_usage_trace(request, result)
        return result

    @app.post("/api/depth/demo-object/save")
    def save_depth_demo_object(request: Request, payload: DepthTraceabilityPayload) -> dict[str, object]:
        result = _finalize_depth_result(
            _depth_demo_object_result(),
            DepthTraceabilityPayload(
                order_id=payload.order_id,
                barcode_text=payload.barcode_text,
                part_category=payload.part_category or "bumper_trim",
                package_hint=payload.package_hint or "irregular",
                material_hint=payload.material_hint,
                actual_weight_kg=payload.actual_weight_kg or 4.6,
                save_to_history=True,
            ),
            measurement_source="depth_demo_object",
            save_to_history=True,
        )
        _set_usage_trace(request, result)
        return result

    @app.post("/api/depth/measure-roi")
    def depth_measure_roi(request: Request, payload: DepthMeasurePayload) -> dict[str, object]:
        try:
            result = measure_depth_roi(
                payload.depth_frame,
                DepthIntrinsics(**payload.intrinsics.model_dump()),
                DepthMeasurementConfig(
                    roi=payload.roi,
                    background_roi=payload.background_roi,
                    table_depth_mm=payload.table_depth_mm,
                    min_valid_depth_mm=payload.min_valid_depth_mm,
                    max_valid_depth_mm=payload.max_valid_depth_mm,
                    trim_ratio=payload.trim_ratio,
                ),
            )
            finalized = _finalize_depth_result(result, payload, measurement_source="depth_roi_api")
            _set_usage_trace(request, finalized)
            return finalized
        except DepthMeasurementError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post("/api/depth/measure-object")
    def depth_measure_object(request: Request, payload: DepthObjectMeasurePayload) -> dict[str, object]:
        try:
            result = measure_depth_object_mask(
                payload.depth_frame,
                DepthIntrinsics(**payload.intrinsics.model_dump()),
                DepthObjectConfig(
                    roi=payload.roi,
                    background_roi=payload.background_roi,
                    table_depth_mm=payload.table_depth_mm,
                    min_valid_depth_mm=payload.min_valid_depth_mm,
                    max_valid_depth_mm=payload.max_valid_depth_mm,
                    object_min_height_mm=payload.object_min_height_mm,
                    trim_quantile=payload.trim_quantile,
                    footprint_method=payload.footprint_method,
                ),
            )
            finalized = _finalize_depth_result(result, payload, measurement_source="depth_object_api")
            _set_usage_trace(request, finalized)
            return finalized
        except DepthMeasurementError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post("/api/industry/profile")
    def industry_profile(payload: IndustryProfilePayload) -> dict[str, object]:
        return build_packaging_profile(
            payload.dimensions,
            part_category=payload.part_category,
            package_hint=payload.package_hint,
            material_hint=payload.material_hint,
            actual_weight_kg=payload.actual_weight_kg,
        )

    @app.get("/api/validation/trial-plan")
    def validation_trial_plan() -> dict[str, object]:
        return build_trial_plan()

    @app.get("/api/validation/trial-template.csv")
    def validation_trial_template_csv() -> Response:
        return Response(
            content=build_trial_template_csv(),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": 'attachment; filename="packvision-trial-template.csv"'},
        )

    @app.post("/api/validation/evaluate")
    def validation_evaluate(payload: TrialRunEvaluationPayload) -> dict[str, object]:
        return evaluate_trial_run(payload.samples)

    @app.post("/api/validation/evaluate-csv")
    async def validation_evaluate_csv(trial_csv: Annotated[UploadFile, File()]) -> dict[str, object]:
        data = await trial_csv.read()
        if not data:
            raise HTTPException(status_code=400, detail="trial_csv is empty.")
        if len(data) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="trial_csv is too large.")
        try:
            csv_text = data.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise HTTPException(status_code=400, detail="trial_csv must be UTF-8 CSV.") from exc
        return evaluate_trial_csv(csv_text)

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


def _depth_demo_object_result() -> dict[str, object]:
    depth_frame = [[1200.0 for _ in range(24)] for _ in range(18)]
    for y in range(4, 15):
        for x in range(4, 21):
            core = abs(x - 12) * 0.75 + abs(y - 9) * 1.35
            if core < 8.2 and not (x < 8 and y < 7):
                depth_frame[y][x] = 820.0 + ((x + y) % 3) * 5.0

    result = measure_depth_object_mask(
        depth_frame,
        DepthIntrinsics(fx=60.0, fy=60.0, cx=12.0, cy=9.0, width=24, height=18),
        DepthObjectConfig(
            roi=[3, 3, 22, 16],
            background_roi=[0, 0, 3, 3],
            object_min_height_mm=80.0,
            trim_quantile=0.01,
        ),
    )
    result["sample"] = {
        "name": "synthetic_irregular_auto_part",
        "purpose": "Validate object-mask depth measurement before Astra Pro hardware arrives.",
    }
    return result


def _finalize_depth_result(
    result: dict[str, object],
    payload: DepthTraceabilityPayload,
    *,
    measurement_source: str,
    save_to_history: bool | None = None,
) -> dict[str, object]:
    actual_weight = payload.actual_weight_kg if payload.actual_weight_kg and payload.actual_weight_kg > 0 else None
    result["measurement_id"] = uuid4().hex[:12]
    result["created_at"] = datetime.now(timezone.utc).isoformat()
    result["order_id"] = _clean_text(payload.order_id)
    result["barcode_text"] = _clean_text(payload.barcode_text)
    result["part_category"] = _clean_text(payload.part_category)
    result["package_hint"] = _clean_text(payload.package_hint)
    result["material_hint"] = _clean_text(payload.material_hint)
    result["actual_weight_kg"] = actual_weight
    result["measurement_source"] = measurement_source
    result["artifacts"] = {"depth_source": measurement_source}
    result["industry_profile"] = build_packaging_profile(
        result.get("dimensions") or {},
        part_category=result["part_category"],
        package_hint=result["package_hint"],
        material_hint=result["material_hint"],
        actual_weight_kg=actual_weight,
    )
    should_save = payload.save_to_history if save_to_history is None else save_to_history
    result["history_saved"] = bool(should_save)
    if should_save:
        save_measurement(result)
    return result


def _set_usage_trace(
    request: Request,
    result: dict[str, object],
    *,
    measurement_source: str | None = None,
) -> None:
    industry_profile = result.get("industry_profile") or {}
    request.state.usage_trace = {
        "order_id": result.get("order_id"),
        "measurement_id": result.get("measurement_id"),
        "measurement_source": measurement_source or result.get("measurement_source"),
        "extra": {
            "history_saved": result.get("history_saved"),
            "package_class": industry_profile.get("package_class"),
            "part_category": result.get("part_category"),
        },
    }


def _usage_trace(request: Request) -> dict[str, object]:
    trace = getattr(request.state, "usage_trace", None)
    return trace if isinstance(trace, dict) else {}
