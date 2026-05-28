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
from packvision.services.ai_plugins import build_ai_plugin_inventory
from packvision.services.barcode import detect_codes
from packvision.services.astra_vendor import AstraVendorError, astra_vendor_profile, normalize_camera_info, resolve_astra_root
from packvision.services.capture_quality import CaptureQualityError, analyze_capture_quality
from packvision.services.depth_camera import depth_camera_status
from packvision.services.depth_capture import (
    capture_depth_once,
    DepthCaptureConfig,
    DepthCaptureError,
    depth_capture_capabilities,
    probe_depth_capture,
)
from packvision.services.depth_devices import build_depth_camera_inventory
from packvision.services.depth_extrinsics import validate_multiview_extrinsics
from packvision.services.depth_fusion import DepthFusionError, fuse_depth_measurements
from packvision.services.depth_geometry import (
    build_depth_evidence_bundle,
    detect_depth_object_region,
    DepthObjectConfig,
    DepthIntrinsics,
    DepthMeasurementConfig,
    DepthMeasurementError,
    measure_depth_object_mask,
    measure_depth_roi,
)
from packvision.services.depth_live import DepthLiveConfig, DepthLiveError, DepthLiveManager
from packvision.services.depth_quality import DepthQualityError, analyze_depth_quality
from packvision.services.astra_tutorials import build_astra_tutorial_playbook
from packvision.services.depth_simulation import (
    DepthSimulationError,
    simulate_astra_depth_measurement_from_image,
)
from packvision.services.depth_workflow import build_depth_workflow_guide, recommend_capture_workflow
from packvision.services.deployment import build_deployment_readiness, build_deployment_readiness_summary
from packvision.services.history import (
    export_measurements_csv,
    get_measurement,
    init_db,
    list_measurements,
    save_measurement,
)
from packvision.services.industry import (
    DEFAULT_VOLUMETRIC_RULE_ID,
    build_packaging_profile,
    infer_material_hint_from_capture_quality,
    list_volumetric_rules,
)
from packvision.services.measurement import (
    MeasurementConfig,
    MeasurementError,
    generate_calibration_svg,
    generate_demo_image,
    measure_images,
    opencv_ready,
)
from packvision.services.review_pool import (
    export_review_samples_csv,
    export_review_truth_template_csv,
    list_review_samples,
)
from packvision.services.scale import build_scale_status, read_scale_weight
from packvision.services.storage import ensure_data_dirs, resource_path, write_bytes
from packvision.services.station import build_station_snapshot
from packvision.services.support_bundle import build_support_bundle
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
    volumetric_rule_id: str | None = None
    volumetric_divisor_l_per_kg: float | None = None
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
    camera_id: str | None = None
    role: str | None = None


class DepthCaptureFramePayload(BaseModel):
    backend: str = "auto"
    timeout_ms: int = 1500
    camera_id: str | None = None
    role: str | None = None
    include_frame: bool = True


class CameraInfoNormalizePayload(BaseModel):
    camera_info: dict[str, Any]
    stream: str = "depth"
    depth_scale: float = 1.0


class DepthMeasureCapturePayload(DepthTraceabilityPayload):
    backend: str = "auto"
    timeout_ms: int = 1500
    camera_id: str | None = None
    role: str | None = None
    measurement_mode: str = "object_mask"
    roi: list[int] | None = None
    background_roi: list[int] | None = None
    table_depth_mm: float | None = None
    min_valid_depth_mm: float = 50.0
    max_valid_depth_mm: float = 6000.0
    object_min_height_mm: float = 30.0
    trim_quantile: float = 0.02
    footprint_method: str = "principal_axes"
    trim_ratio: float = 0.08
    save_depth_evidence: bool = True


class DepthLiveStartPayload(BaseModel):
    backend: str = "auto"
    timeout_ms: int = 1500
    camera_id: str | None = None
    role: str | None = None
    interval_ms: int = 700
    allow_simulation: bool = True
    measurement_mode: str = "auto"
    min_valid_depth_mm: float = 50.0
    max_valid_depth_mm: float = 6000.0
    object_min_height_mm: float = 30.0
    footprint_method: str = "principal_axes"
    stable_required_frames: int = 3


class DepthLiveConfirmPayload(DepthTraceabilityPayload):
    require_stable: bool = True


class DepthFusionPayload(DepthTraceabilityPayload):
    view_measurements: list[dict[str, Any]]
    strategy: str = "conservative_max"
    disagreement_ratio: float = 0.12


class DepthExtrinsicsValidationPayload(BaseModel):
    cameras: list[dict[str, Any]]
    validation_measurements: list[dict[str, Any]] = []
    required_roles: list[str] = ["top", "front", "side"]
    reference_role: str = "top"
    disagreement_ratio: float = 0.12


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
    volumetric_rule_id: str | None = None
    volumetric_divisor_l_per_kg: float | None = None


class TrialRunEvaluationPayload(BaseModel):
    samples: list[dict[str, Any]]


def create_app() -> FastAPI:
    app = FastAPI(title="PackVision Local", version=__version__)
    dirs = ensure_data_dirs()
    init_db()
    init_usage_db()
    depth_live_manager = DepthLiveManager(capture_depth_once)
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

    @app.get("/api/deployment/readiness")
    def deployment_readiness() -> dict[str, object]:
        return build_deployment_readiness()

    @app.get("/api/deployment/readiness-summary")
    def deployment_readiness_summary() -> dict[str, object]:
        return build_deployment_readiness_summary()

    @app.get("/api/deployment/support-bundle.zip")
    def deployment_support_bundle() -> FileResponse:
        bundle_path = build_support_bundle()
        return FileResponse(
            bundle_path,
            media_type="application/zip",
            filename=bundle_path.name,
        )

    @app.get("/api/station/snapshot")
    def station_snapshot() -> dict[str, object]:
        return build_station_snapshot(
            live_state=depth_live_manager.state(),
            latest_measurements=list_measurements(limit=1),
            usage=usage_summary(),
            scale_status=build_scale_status(),
        )

    @app.get("/api/ai/plugins")
    def ai_plugins() -> dict[str, object]:
        return build_ai_plugin_inventory()

    @app.get("/api/calibration-card.svg", response_class=HTMLResponse)
    def calibration_card(marker_size_mm: float = 50.0) -> Response:
        try:
            svg = generate_calibration_svg(marker_size_mm=marker_size_mm)
        except MeasurementError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        return Response(content=svg, media_type="image/svg+xml")

    @app.get("/api/depth/vendor-calibration-board.pdf")
    def vendor_calibration_board() -> FileResponse:
        board_path = resolve_astra_root() / "棋盘格标定200x160_7x10.pdf"
        if not board_path.exists():
            raise HTTPException(status_code=404, detail="Astra Pro vendor calibration board not found.")
        return FileResponse(
            board_path,
            media_type="application/pdf",
            filename="Astra-Pro-checkerboard-200x160-7x10.pdf",
        )

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
        volumetric_rule_id: Annotated[str | None, Form()] = None,
        volumetric_divisor_l_per_kg: Annotated[float | None, Form()] = None,
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
        explicit_material_hint = _clean_text(material_hint)
        auto_material_signal = infer_material_hint_from_capture_quality(
            result.get("capture_quality") if isinstance(result.get("capture_quality"), dict) else None,
            result.get("quality_flags") if isinstance(result.get("quality_flags"), list) else None,
        )
        result["material_hint"] = explicit_material_hint or auto_material_signal.get("material_hint")
        result["material_hint_source"] = "manual" if explicit_material_hint else auto_material_signal.get("source")
        result["auto_material_signal"] = auto_material_signal
        result["actual_weight_kg"] = actual_weight_kg if actual_weight_kg and actual_weight_kg > 0 else None
        result["industry_profile"] = build_packaging_profile(
            result["dimensions"],
            part_category=result["part_category"],
            package_hint=result["package_hint"],
            material_hint=result["material_hint"],
            actual_weight_kg=result["actual_weight_kg"],
            volumetric_rule_id=volumetric_rule_id,
            volumetric_divisor_l_per_kg=volumetric_divisor_l_per_kg,
        )
        result["volumetric_rule_id"] = result["industry_profile"].get("volumetric_rule_id")
        result["volumetric_weight_kg"] = result["industry_profile"].get("volumetric_weight_kg")
        result["chargeable_weight_kg"] = result["industry_profile"].get("chargeable_weight_kg")
        result["billing_weight_source"] = result["industry_profile"].get("billing_weight_source")
        result["industry_profile"]["material_hint_source"] = result["material_hint_source"]
        result["industry_profile"]["auto_material_signal"] = auto_material_signal
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

    @app.get("/api/review/samples")
    def review_samples(limit: int = 50, order_id: str | None = None) -> dict[str, object]:
        return list_review_samples(limit=limit, order_id=_clean_text(order_id))

    @app.get("/api/review/export.csv")
    def review_export(limit: int = 500, order_id: str | None = None) -> Response:
        csv_text = export_review_samples_csv(limit=limit, order_id=_clean_text(order_id))
        return Response(
            content=csv_text,
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": 'attachment; filename="packvision-review-samples.csv"'},
        )

    @app.get("/api/review/truth-template.csv")
    def review_truth_template(limit: int = 500, order_id: str | None = None) -> Response:
        csv_text = export_review_truth_template_csv(limit=limit, order_id=_clean_text(order_id))
        return Response(
            content=csv_text,
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": 'attachment; filename="packvision-review-truth-template.csv"'},
        )

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

    @app.get("/api/depth/vendor-profile")
    def depth_vendor_profile() -> dict[str, object]:
        return astra_vendor_profile()

    @app.get("/api/depth/astra/tutorial-playbook")
    def depth_astra_tutorial_playbook() -> dict[str, object]:
        return build_astra_tutorial_playbook()

    @app.post("/api/depth/camera-info/normalize")
    def depth_camera_info_normalize(payload: CameraInfoNormalizePayload) -> dict[str, object]:
        try:
            return normalize_camera_info(
                payload.camera_info,
                stream=payload.stream,
                depth_scale=payload.depth_scale,
            )
        except AstraVendorError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

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

    @app.get("/api/depth/cameras")
    def depth_cameras() -> dict[str, object]:
        return build_depth_camera_inventory()

    @app.post("/api/depth/capture/probe")
    def depth_capture_probe(payload: DepthCaptureProbePayload) -> dict[str, object]:
        try:
            return probe_depth_capture(
                DepthCaptureConfig(
                    backend=payload.backend,
                    timeout_ms=payload.timeout_ms,
                    camera_id=payload.camera_id,
                    role=payload.role,
                )
            )
        except DepthCaptureError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post("/api/depth/capture/frame")
    def depth_capture_frame(payload: DepthCaptureFramePayload) -> dict[str, object]:
        try:
            bundle = capture_depth_once(
                DepthCaptureConfig(
                    backend=payload.backend,
                    timeout_ms=payload.timeout_ms,
                    camera_id=payload.camera_id,
                    role=payload.role,
                )
            )
            return _depth_frame_response(bundle, include_frame=payload.include_frame)
        except DepthCaptureError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post("/api/depth/measure-capture")
    def depth_measure_capture(request: Request, payload: DepthMeasureCapturePayload) -> dict[str, object]:
        try:
            bundle = capture_depth_once(
                DepthCaptureConfig(
                    backend=payload.backend,
                    timeout_ms=payload.timeout_ms,
                    camera_id=payload.camera_id,
                    role=payload.role,
                )
            )
            capture_regions = _depth_capture_regions(
                bundle.depth_frame,
                intrinsics=bundle.intrinsics,
                roi=payload.roi,
                background_roi=payload.background_roi,
                min_valid_depth_mm=payload.min_valid_depth_mm,
                max_valid_depth_mm=payload.max_valid_depth_mm,
                object_min_height_mm=payload.object_min_height_mm,
            )
            roi = capture_regions["roi"]
            background_roi = capture_regions.get("background_roi")
            table_depth_mm = payload.table_depth_mm
            if table_depth_mm is None:
                table_depth_mm = capture_regions.get("table_depth_mm")
            measurement_mode = str(payload.measurement_mode or "object_mask").strip().lower()
            if measurement_mode == "roi":
                result = measure_depth_roi(
                    bundle.depth_frame,
                    bundle.intrinsics,
                    DepthMeasurementConfig(
                        roi=roi,
                        background_roi=background_roi,
                        table_depth_mm=table_depth_mm,
                        min_valid_depth_mm=payload.min_valid_depth_mm,
                        max_valid_depth_mm=payload.max_valid_depth_mm,
                        trim_ratio=payload.trim_ratio,
                    ),
                )
            elif measurement_mode in {"object_mask", "auto"}:
                result = measure_depth_object_mask(
                    bundle.depth_frame,
                    bundle.intrinsics,
                    DepthObjectConfig(
                        roi=roi,
                        background_roi=background_roi,
                        table_depth_mm=table_depth_mm,
                        min_valid_depth_mm=payload.min_valid_depth_mm,
                        max_valid_depth_mm=payload.max_valid_depth_mm,
                        object_min_height_mm=payload.object_min_height_mm,
                        trim_quantile=payload.trim_quantile,
                        footprint_method=payload.footprint_method,
                    ),
                )
            else:
                raise DepthCaptureError("measurement_mode must be auto, object_mask, or roi.")
            result["camera_capture"] = _depth_frame_response(bundle, include_frame=False)
            result["capture_regions"] = capture_regions
            if payload.save_depth_evidence:
                _attach_depth_evidence_artifacts(
                    result,
                    bundle,
                    roi=roi,
                    table_depth_mm=table_depth_mm,
                    min_valid_depth_mm=payload.min_valid_depth_mm,
                    max_valid_depth_mm=payload.max_valid_depth_mm,
                    object_min_height_mm=payload.object_min_height_mm,
                    results_dir=dirs["results"],
                )
            finalized = _finalize_depth_result(result, payload, measurement_source="depth_camera_capture")
            _set_usage_trace(request, finalized)
            return finalized
        except (DepthCaptureError, DepthMeasurementError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post("/api/depth/live/start")
    def depth_live_start(payload: DepthLiveStartPayload) -> dict[str, object]:
        return depth_live_manager.start(
            DepthLiveConfig(
                backend=payload.backend,
                timeout_ms=payload.timeout_ms,
                camera_id=payload.camera_id,
                role=payload.role,
                interval_ms=payload.interval_ms,
                allow_simulation=payload.allow_simulation,
                measurement_mode=payload.measurement_mode,
                min_valid_depth_mm=payload.min_valid_depth_mm,
                max_valid_depth_mm=payload.max_valid_depth_mm,
                object_min_height_mm=payload.object_min_height_mm,
                footprint_method=payload.footprint_method,
                stable_required_frames=payload.stable_required_frames,
            )
        )

    @app.get("/api/depth/live/state")
    def depth_live_state() -> dict[str, object]:
        return depth_live_manager.state()

    @app.post("/api/depth/live/stop")
    def depth_live_stop() -> dict[str, object]:
        return depth_live_manager.stop()

    @app.post("/api/depth/live/confirm")
    def depth_live_confirm(request: Request, payload: DepthLiveConfirmPayload) -> dict[str, object]:
        try:
            candidate = depth_live_manager.confirm_candidate(require_stable=payload.require_stable)
            result = candidate["result"]
            bundle = candidate["bundle"]
            capture_regions = result.get("capture_regions") if isinstance(result.get("capture_regions"), dict) else {}
            roi = capture_regions.get("roi")
            if not isinstance(roi, list):
                raise DepthLiveError("Live candidate does not include a valid ROI.")
            _attach_depth_evidence_artifacts(
                result,
                bundle,
                roi=roi,
                table_depth_mm=capture_regions.get("table_depth_mm"),
                min_valid_depth_mm=50.0,
                max_valid_depth_mm=6000.0,
                object_min_height_mm=30.0,
                results_dir=dirs["results"],
            )
            result["live_confirmation"] = {
                "confirmed_from": "depth_live_stream",
                "live_state": candidate["state"],
            }
            finalized = _finalize_depth_result(
                result,
                payload,
                measurement_source="depth_live_confirm",
                save_to_history=True,
            )
            _set_usage_trace(request, finalized)
            return finalized
        except (DepthLiveError, DepthMeasurementError) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.post("/api/depth/fuse-measurements")
    def depth_fuse_measurements(request: Request, payload: DepthFusionPayload) -> dict[str, object]:
        try:
            result = fuse_depth_measurements(
                payload.view_measurements,
                strategy=payload.strategy,
                disagreement_ratio=payload.disagreement_ratio,
            )
            finalized = _finalize_depth_result(result, payload, measurement_source="depth_multi_view_fusion")
            _set_usage_trace(request, finalized)
            return finalized
        except DepthFusionError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post("/api/depth/extrinsics/validate")
    def depth_extrinsics_validate(payload: DepthExtrinsicsValidationPayload) -> dict[str, object]:
        return validate_multiview_extrinsics(
            payload.cameras,
            validation_measurements=payload.validation_measurements,
            required_roles=payload.required_roles,
            reference_role=payload.reference_role,
            disagreement_ratio=payload.disagreement_ratio,
        )

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
                volumetric_rule_id=payload.volumetric_rule_id,
                volumetric_divisor_l_per_kg=payload.volumetric_divisor_l_per_kg,
                save_to_history=True,
            ),
            measurement_source="depth_demo_object",
            save_to_history=True,
        )
        _set_usage_trace(request, result)
        return result

    @app.post("/api/depth/simulate-from-image")
    async def depth_simulate_from_image(
        request: Request,
        image: Annotated[UploadFile, File()],
        order_id: Annotated[str | None, Form()] = None,
        barcode_text: Annotated[str | None, Form()] = None,
        part_category: Annotated[str | None, Form()] = None,
        package_hint: Annotated[str | None, Form()] = None,
        material_hint: Annotated[str | None, Form()] = None,
        actual_weight_kg: Annotated[float | None, Form()] = None,
        volumetric_rule_id: Annotated[str | None, Form()] = None,
        volumetric_divisor_l_per_kg: Annotated[float | None, Form()] = None,
        roi_json: Annotated[str | None, Form()] = None,
        table_depth_mm: Annotated[float, Form()] = 1200.0,
        object_depth_mm: Annotated[float, Form()] = 850.0,
        frame_index: Annotated[int, Form()] = 0,
        save_to_history: Annotated[bool, Form()] = False,
        source_url: Annotated[str | None, Form()] = None,
    ) -> dict[str, object]:
        content = await image.read()
        if not content:
            raise HTTPException(status_code=422, detail="image is required.")
        if len(content) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="Image must be 15 MB or smaller.")
        try:
            simulated = simulate_astra_depth_measurement_from_image(
                content,
                filename=image.filename,
                source_url=source_url,
                roi=_parse_roi_json(roi_json),
                table_depth_mm=table_depth_mm,
                object_depth_mm=object_depth_mm,
                frame_index=frame_index,
            )
        except DepthSimulationError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        source_path = write_bytes(dirs["results"], ".png", simulated.artifacts.source_png)
        overlay_path = write_bytes(dirs["results"], ".png", simulated.artifacts.overlay_png)
        depth_preview_path = write_bytes(dirs["results"], ".png", simulated.artifacts.depth_preview_png)
        payload = DepthTraceabilityPayload(
            order_id=order_id,
            barcode_text=barcode_text,
            part_category=part_category,
            package_hint=package_hint,
            material_hint=material_hint,
            actual_weight_kg=actual_weight_kg,
            volumetric_rule_id=volumetric_rule_id,
            volumetric_divisor_l_per_kg=volumetric_divisor_l_per_kg,
            save_to_history=False,
        )
        result = _finalize_depth_result(
            simulated.result,
            payload,
            measurement_source="depth_simulated_real_image",
            save_to_history=False,
        )
        result["artifacts"].update(
            {
                "source_image_url": f"/results/{source_path.name}",
                "simulation_overlay_url": f"/results/{overlay_path.name}",
                "depth_preview_url": f"/results/{depth_preview_path.name}",
            }
        )
        if save_to_history:
            result["history_saved"] = True
            save_measurement(result)
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
            volumetric_rule_id=payload.volumetric_rule_id,
            volumetric_divisor_l_per_kg=payload.volumetric_divisor_l_per_kg,
        )

    @app.get("/api/weight/volumetric-rules")
    def volumetric_rules() -> dict[str, object]:
        return {
            "default_rule_id": DEFAULT_VOLUMETRIC_RULE_ID,
            "rules": list_volumetric_rules(),
        }

    @app.get("/api/scale/status")
    def scale_status() -> dict[str, object]:
        return build_scale_status()

    @app.post("/api/scale/read")
    def scale_read() -> dict[str, object]:
        return read_scale_weight()

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


def _parse_roi_json(raw: str | None) -> list[int] | None:
    if not raw:
        return None
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=422, detail="roi_json must be valid JSON.") from exc
    if not isinstance(value, list) or len(value) != 4:
        raise HTTPException(status_code=422, detail="roi_json must be [x1, y1, x2, y2].")
    try:
        return [int(round(float(item))) for item in value]
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail="roi_json values must be numbers.") from exc


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


def _depth_frame_response(bundle: Any, *, include_frame: bool) -> dict[str, object]:
    frame_height = len(bundle.depth_frame)
    frame_width = len(bundle.depth_frame[0]) if frame_height else 0
    response: dict[str, object] = {
        "status": "captured",
        "backend": bundle.backend,
        "camera_id": bundle.camera_id,
        "role": bundle.role,
        "serial_number": bundle.serial_number,
        "frame_index": bundle.frame_index,
        "timestamp_us": bundle.timestamp_us,
        "frame_shape": {"height": frame_height, "width": frame_width},
        "intrinsics": {
            "fx": bundle.intrinsics.fx,
            "fy": bundle.intrinsics.fy,
            "cx": bundle.intrinsics.cx,
            "cy": bundle.intrinsics.cy,
            "width": bundle.intrinsics.width,
            "height": bundle.intrinsics.height,
            "depth_scale": bundle.intrinsics.depth_scale,
        },
    }
    if include_frame:
        response["depth_frame"] = bundle.depth_frame
    return response


def _depth_capture_regions(
    depth_frame: list[list[float]],
    *,
    intrinsics: DepthIntrinsics,
    roi: list[int] | None,
    background_roi: list[int] | None,
    min_valid_depth_mm: float,
    max_valid_depth_mm: float,
    object_min_height_mm: float,
) -> dict[str, Any]:
    frame_height = len(depth_frame)
    frame_width = len(depth_frame[0]) if frame_height else 0
    if frame_width <= 0 or frame_height <= 0:
        raise DepthCaptureError("Captured depth frame is empty.")
    if roi:
        return {"roi": roi, "background_roi": background_roi, "source": "manual"}

    regions = detect_depth_object_region(
        depth_frame,
        intrinsics,
        min_valid_depth_mm=min_valid_depth_mm,
        max_valid_depth_mm=max_valid_depth_mm,
        object_min_height_mm=object_min_height_mm,
    )
    if background_roi:
        regions["background_roi"] = background_roi
        regions["background_roi_source"] = "manual"
    else:
        regions["background_roi_source"] = "auto"
    return regions


def _attach_depth_evidence_artifacts(
    result: dict[str, object],
    bundle: Any,
    *,
    roi: list[int],
    table_depth_mm: float | None,
    min_valid_depth_mm: float,
    max_valid_depth_mm: float,
    object_min_height_mm: float,
    results_dir: Path,
) -> None:
    evidence = build_depth_evidence_bundle(
        bundle.depth_frame,
        bundle.intrinsics,
        roi=roi,
        table_depth_mm=table_depth_mm,
        min_valid_depth_mm=min_valid_depth_mm,
        max_valid_depth_mm=max_valid_depth_mm,
        object_min_height_mm=object_min_height_mm,
    )
    point_cloud_path = write_bytes(results_dir, ".npz", evidence.point_cloud_npz)
    preview_path = write_bytes(results_dir, ".png", evidence.depth_preview_png)
    artifact_updates = {
        "depth_point_cloud_url": f"/results/{point_cloud_path.name}",
        "depth_preview_url": f"/results/{preview_path.name}",
    }
    artifacts = result.get("artifacts") if isinstance(result.get("artifacts"), dict) else {}
    artifacts.update(artifact_updates)
    result["artifacts"] = artifacts
    result["depth_evidence"] = {
        **evidence.metadata,
        **artifact_updates,
        "saved": True,
    }


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
    result["material_hint_source"] = "manual" if result["material_hint"] else None
    result["auto_material_signal"] = {
        "material_hint": None,
        "source": None,
        "confidence": 0.0,
        "reason_codes": [],
    }
    result["actual_weight_kg"] = actual_weight
    result["measurement_source"] = measurement_source
    existing_artifacts = result.get("artifacts") if isinstance(result.get("artifacts"), dict) else {}
    result["artifacts"] = {"depth_source": measurement_source, **existing_artifacts}
    result["industry_profile"] = build_packaging_profile(
        result.get("dimensions") or {},
        part_category=result["part_category"],
        package_hint=result["package_hint"],
        material_hint=result["material_hint"],
        actual_weight_kg=actual_weight,
        volumetric_rule_id=payload.volumetric_rule_id,
        volumetric_divisor_l_per_kg=payload.volumetric_divisor_l_per_kg,
    )
    result["volumetric_rule_id"] = result["industry_profile"].get("volumetric_rule_id")
    result["volumetric_weight_kg"] = result["industry_profile"].get("volumetric_weight_kg")
    result["chargeable_weight_kg"] = result["industry_profile"].get("chargeable_weight_kg")
    result["billing_weight_source"] = result["industry_profile"].get("billing_weight_source")
    result["industry_profile"]["material_hint_source"] = result["material_hint_source"]
    result["industry_profile"]["auto_material_signal"] = result["auto_material_signal"]
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
            "volumetric_rule_id": industry_profile.get("volumetric_rule_id"),
            "chargeable_weight_kg": industry_profile.get("chargeable_weight_kg"),
        },
    }


def _usage_trace(request: Request) -> dict[str, object]:
    trace = getattr(request.state, "usage_trace", None)
    return trace if isinstance(trace, dict) else {}
