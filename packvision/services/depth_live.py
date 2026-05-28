from __future__ import annotations

import copy
import queue
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

import numpy as np

from packvision.services.depth_capture import DepthCaptureConfig, DepthCaptureError, DepthFrameBundle
from packvision.services.depth_geometry import (
    DepthIntrinsics,
    DepthMeasurementConfig,
    DepthMeasurementError,
    DepthObjectConfig,
    detect_depth_object_region,
    measure_depth_object_mask,
    measure_depth_roi,
)


CaptureFn = Callable[[DepthCaptureConfig], DepthFrameBundle]


@dataclass(frozen=True)
class DepthLiveConfig:
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
    trim_ratio: float = 0.08
    trim_quantile: float = 0.02
    stable_required_frames: int = 3


class DepthLiveError(RuntimeError):
    pass


class DepthLiveManager:
    def __init__(self, capture_fn: CaptureFn):
        self._capture_fn = capture_fn
        self._lock = threading.RLock()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._config = DepthLiveConfig()
        self._frame_count = 0
        self._measurement_count = 0
        self._stable_frame_count = 0
        self._last_dimensions: dict[str, float] | None = None
        self._latest_bundle: DepthFrameBundle | None = None
        self._stable_bundle: DepthFrameBundle | None = None
        self._latest_result: dict[str, Any] | None = None
        self._stable_result: dict[str, Any] | None = None
        self._last_error: str | None = None
        self._simulation_active = False
        self._simulation_fallback_reason: str | None = None
        self._status = "stopped"
        self._started_at: str | None = None
        self._updated_at: str | None = None
        self._started_monotonic: float | None = None

    def start(self, config: DepthLiveConfig | None = None) -> dict[str, Any]:
        config = config or DepthLiveConfig()
        self.stop()
        with self._lock:
            self._config = _normalized_config(config)
            self._stop_event = threading.Event()
            self._frame_count = 0
            self._measurement_count = 0
            self._stable_frame_count = 0
            self._last_dimensions = None
            self._latest_bundle = None
            self._stable_bundle = None
            self._latest_result = None
            self._stable_result = None
            self._last_error = None
            self._simulation_active = False
            self._simulation_fallback_reason = None
            self._status = "starting"
            self._started_at = _now()
            self._started_monotonic = time.monotonic()
            self._updated_at = self._started_at
            self._thread = threading.Thread(target=self._run, name="packvision-depth-live", daemon=True)
            self._thread.start()
        return self.state()

    def stop(self) -> dict[str, Any]:
        thread: threading.Thread | None
        with self._lock:
            thread = self._thread
            if thread and thread.is_alive():
                self._stop_event.set()
        if thread and thread.is_alive():
            thread.join(timeout=1.5)
        with self._lock:
            self._thread = None
            self._status = "stopped"
            self._updated_at = _now()
        return self.state()

    def state(self) -> dict[str, Any]:
        with self._lock:
            uptime_seconds = _uptime_seconds(self._started_monotonic)
            fps = _average_fps(self._frame_count, uptime_seconds)
            return {
                "running": bool(self._thread and self._thread.is_alive() and not self._stop_event.is_set()),
                "status": self._status,
                "frame_count": self._frame_count,
                "measurement_count": self._measurement_count,
                "uptime_seconds": uptime_seconds,
                "fps": fps,
                "stable_frame_count": self._stable_frame_count,
                "stable_required_frames": self._config.stable_required_frames,
                "simulation_active": self._simulation_active,
                "last_error": self._last_error,
                "started_at": self._started_at,
                "updated_at": self._updated_at,
                "config": _config_summary(self._config),
                "latest_result": _result_summary(self._latest_result),
                "stable_result": _result_summary(self._stable_result),
                "can_confirm": self._stable_result is not None,
            }

    def confirm_candidate(self, *, require_stable: bool = True) -> dict[str, Any]:
        with self._lock:
            result = self._stable_result if require_stable else self._stable_result or self._latest_result
            bundle = self._stable_bundle if require_stable else self._stable_bundle or self._latest_bundle
            if result is None or bundle is None:
                status = "stable result" if require_stable else "live candidate"
                raise DepthLiveError(f"No {status} is available to confirm.")
            return {
                "result": copy.deepcopy(result),
                "bundle": copy.deepcopy(bundle),
                "state": self.state(),
            }

    def _run(self) -> None:
        while not self._stop_event.is_set():
            self._tick()
            interval = max(0.25, min(5.0, self._config.interval_ms / 1000.0))
            self._stop_event.wait(interval)

    def _tick(self) -> None:
        config = self._config
        try:
            bundle, simulation_active, capture_error = self._capture_bundle(config)
            region = detect_depth_object_region(
                bundle.depth_frame,
                bundle.intrinsics,
                min_valid_depth_mm=config.min_valid_depth_mm,
                max_valid_depth_mm=config.max_valid_depth_mm,
                object_min_height_mm=config.object_min_height_mm,
            )
            with self._lock:
                self._frame_count += 1
                self._latest_bundle = copy.deepcopy(bundle)
                self._simulation_active = simulation_active
                self._last_error = capture_error
                self._updated_at = _now()

            if region.get("source") != "auto_depth_foreground":
                self._set_waiting(region)
                return

            result = self._measure_bundle(bundle, region, config)
            stable = self._update_stability(result)
            result["live_capture"] = {
                "status": "stable_ready" if stable else "measuring",
                "stable_frame_count": self._stable_frame_count,
                "stable_required_frames": config.stable_required_frames,
                "simulation_active": simulation_active,
            }
            with self._lock:
                self._measurement_count += 1
                self._latest_result = result
                self._latest_bundle = copy.deepcopy(bundle)
                if stable:
                    self._stable_result = copy.deepcopy(result)
                    self._stable_bundle = copy.deepcopy(bundle)
                self._status = "stable_ready" if stable else "measuring"
                if result.get("confidence", 0) < 0.5 and stable:
                    self._status = "needs_review"
                self._updated_at = _now()
        except (DepthCaptureError, DepthMeasurementError, ValueError) as exc:
            with self._lock:
                self._status = "error"
                self._last_error = str(exc)
                self._updated_at = _now()

    def _capture_bundle(self, config: DepthLiveConfig) -> tuple[DepthFrameBundle, bool, str | None]:
        backend = str(config.backend or "auto").strip().lower()
        if backend in {"simulated", "simulation", "dry_run"}:
            return _synthetic_live_bundle(self._frame_count + 1), True, None
        with self._lock:
            fallback_reason = self._simulation_fallback_reason
        if config.allow_simulation and fallback_reason:
            return _synthetic_live_bundle(self._frame_count + 1), True, fallback_reason
        try:
            bundle = (
                self._capture_with_timeout(config)
                if config.allow_simulation
                else self._capture_fn(_capture_config(config))
            )
            return bundle, False, None
        except DepthCaptureError as exc:
            if not config.allow_simulation:
                raise
            message = str(exc)
            with self._lock:
                self._simulation_fallback_reason = message
            return _synthetic_live_bundle(self._frame_count + 1), True, message

    def _capture_with_timeout(self, config: DepthLiveConfig) -> DepthFrameBundle:
        results: queue.Queue[tuple[DepthFrameBundle | None, BaseException | None]] = queue.Queue(maxsize=1)

        def worker() -> None:
            try:
                results.put((self._capture_fn(_capture_config(config)), None))
            except BaseException as exc:  # pragma: no cover - defensive around optional hardware SDKs
                results.put((None, exc))

        thread = threading.Thread(target=worker, name="packvision-depth-capture-probe", daemon=True)
        thread.start()
        try:
            bundle, error = results.get(timeout=max(0.1, config.timeout_ms / 1000.0))
        except queue.Empty as exc:
            raise DepthCaptureError(
                f"Depth capture timed out after {config.timeout_ms} ms; live view is using simulation fallback."
            ) from exc
        if error is not None:
            if isinstance(error, DepthCaptureError):
                raise error
            raise DepthCaptureError(str(error)) from error
        if bundle is None:
            raise DepthCaptureError("Depth capture returned no frame.")
        return bundle

    def _measure_bundle(
        self,
        bundle: DepthFrameBundle,
        region: dict[str, Any],
        config: DepthLiveConfig,
    ) -> dict[str, Any]:
        roi = region["roi"]
        background_roi = region.get("background_roi")
        table_depth_mm = region.get("table_depth_mm")
        mode = str(config.measurement_mode or "auto").strip().lower()
        if mode == "roi":
            result = measure_depth_roi(
                bundle.depth_frame,
                bundle.intrinsics,
                DepthMeasurementConfig(
                    roi=roi,
                    background_roi=background_roi,
                    table_depth_mm=table_depth_mm,
                    min_valid_depth_mm=config.min_valid_depth_mm,
                    max_valid_depth_mm=config.max_valid_depth_mm,
                    trim_ratio=config.trim_ratio,
                ),
            )
        else:
            result = measure_depth_object_mask(
                bundle.depth_frame,
                bundle.intrinsics,
                DepthObjectConfig(
                    roi=roi,
                    background_roi=background_roi,
                    table_depth_mm=table_depth_mm,
                    min_valid_depth_mm=config.min_valid_depth_mm,
                    max_valid_depth_mm=config.max_valid_depth_mm,
                    object_min_height_mm=config.object_min_height_mm,
                    trim_quantile=config.trim_quantile,
                    footprint_method=config.footprint_method,
                ),
            )
        result["camera_capture"] = _bundle_summary(bundle)
        result["capture_regions"] = region
        return result

    def _set_waiting(self, region: dict[str, Any]) -> None:
        with self._lock:
            self._status = "waiting_for_object"
            self._stable_frame_count = 0
            self._last_dimensions = None
            self._latest_result = {
                "status": "waiting_for_object",
                "confidence": 0.0,
                "capture_regions": region,
                "dimensions": {},
                "quality_flags": ["waiting_for_depth_foreground"],
                "recommendation_codes": ["place_package_under_depth_camera"],
            }
            self._updated_at = _now()

    def _update_stability(self, result: dict[str, Any]) -> bool:
        dimensions = _dimension_fingerprint(result)
        with self._lock:
            if self._last_dimensions and _dimensions_close(self._last_dimensions, dimensions):
                self._stable_frame_count += 1
            else:
                self._stable_frame_count = 1
            self._last_dimensions = dimensions
            return self._stable_frame_count >= self._config.stable_required_frames


def _normalized_config(config: DepthLiveConfig) -> DepthLiveConfig:
    return DepthLiveConfig(
        backend=str(config.backend or "auto").strip().lower(),
        timeout_ms=max(250, min(8000, int(config.timeout_ms))),
        camera_id=config.camera_id,
        role=config.role,
        interval_ms=max(250, min(5000, int(config.interval_ms))),
        allow_simulation=bool(config.allow_simulation),
        measurement_mode=str(config.measurement_mode or "auto").strip().lower(),
        min_valid_depth_mm=float(config.min_valid_depth_mm),
        max_valid_depth_mm=float(config.max_valid_depth_mm),
        object_min_height_mm=float(config.object_min_height_mm),
        footprint_method=str(config.footprint_method or "principal_axes").strip().lower(),
        trim_ratio=float(config.trim_ratio),
        trim_quantile=float(config.trim_quantile),
        stable_required_frames=max(1, min(12, int(config.stable_required_frames))),
    )


def _capture_config(config: DepthLiveConfig) -> DepthCaptureConfig:
    return DepthCaptureConfig(
        backend=config.backend,
        timeout_ms=config.timeout_ms,
        camera_id=config.camera_id,
        role=config.role,
    )


def _synthetic_live_bundle(frame_index: int) -> DepthFrameBundle:
    width, height = 64, 48
    depth = np.full((height, width), 1200.0, dtype=np.float32)
    depth += np.linspace(-4.0, 4.0, width, dtype=np.float32)[None, :]
    depth += np.linspace(-3.0, 3.0, height, dtype=np.float32)[:, None]
    x_shift = 1 if frame_index % 7 == 0 else 0
    y_shift = 1 if frame_index % 11 == 0 else 0
    depth[16 + y_shift : 33 + y_shift, 20 + x_shift : 45 + x_shift] = 860.0 + (frame_index % 3)
    return DepthFrameBundle(
        depth_frame=np.round(depth, 2).astype(float).tolist(),
        intrinsics=DepthIntrinsics(fx=58.0, fy=58.0, cx=32.0, cy=24.0, width=width, height=height),
        backend="simulated_live_astra",
        camera_id="simulated-astra-pro-top",
        role="top",
        serial_number="SIM-LIVE-ASTRA",
        frame_index=frame_index,
        timestamp_us=int(time.time() * 1_000_000),
    )


def _bundle_summary(bundle: DepthFrameBundle) -> dict[str, Any]:
    frame_height = len(bundle.depth_frame)
    frame_width = len(bundle.depth_frame[0]) if frame_height else 0
    return {
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


def _dimension_fingerprint(result: dict[str, Any]) -> dict[str, float]:
    dims = result.get("dimensions") if isinstance(result.get("dimensions"), dict) else {}
    return {
        key: float(dims.get(key) or 0.0)
        for key in ("length_mm", "width_mm", "height_mm")
    }


def _dimensions_close(previous: dict[str, float], current: dict[str, float]) -> bool:
    for key, value in current.items():
        tolerance = max(8.0, abs(value) * 0.03)
        if abs(value - previous.get(key, 0.0)) > tolerance:
            return False
    return True


def _result_summary(result: dict[str, Any] | None) -> dict[str, Any] | None:
    if result is None:
        return None
    return {
        "status": result.get("status"),
        "confidence": result.get("confidence"),
        "dimensions": result.get("dimensions") or {},
        "quality_flags": result.get("quality_flags") or [],
        "recommendation_codes": result.get("recommendation_codes") or [],
        "capture_regions": result.get("capture_regions") or {},
        "camera_capture": result.get("camera_capture") or {},
        "live_capture": result.get("live_capture") or {},
    }


def _config_summary(config: DepthLiveConfig) -> dict[str, Any]:
    return {
        "backend": config.backend,
        "camera_id": config.camera_id,
        "role": config.role,
        "interval_ms": config.interval_ms,
        "allow_simulation": config.allow_simulation,
        "measurement_mode": config.measurement_mode,
        "stable_required_frames": config.stable_required_frames,
    }


def _uptime_seconds(started_monotonic: float | None) -> float:
    if started_monotonic is None:
        return 0.0
    return round(max(0.0, time.monotonic() - started_monotonic), 1)


def _average_fps(frame_count: int, uptime_seconds: float) -> float:
    if not frame_count or uptime_seconds <= 0:
        return 0.0
    return round(frame_count / uptime_seconds, 2)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
