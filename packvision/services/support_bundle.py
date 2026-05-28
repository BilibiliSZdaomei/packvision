from __future__ import annotations

import json
import platform
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from packvision import __version__
from packvision.services.ai_plugins import build_ai_plugin_inventory
from packvision.services.depth_camera import depth_camera_status
from packvision.services.depth_capture import depth_capture_capabilities
from packvision.services.depth_devices import build_depth_camera_inventory
from packvision.services.device_watchdog import build_device_watchdog
from packvision.services.deployment import build_deployment_readiness
from packvision.services.history import export_measurements_csv
from packvision.services.review_pool import export_review_samples_csv, export_review_truth_template_csv
from packvision.services.storage import app_data_dir, ensure_data_dirs
from packvision.services.usage import export_usage_csv, usage_summary


SUPPORT_BUNDLE_HISTORY_LIMIT = 200
SUPPORT_BUNDLE_USAGE_LIMIT = 500
SUPPORT_BUNDLE_REVIEW_LIMIT = 200
SUPPORT_BUNDLE_LOG_TAIL_BYTES = 512 * 1024


def build_support_bundle() -> Path:
    """Build a small field-support zip without bundling private upload images."""

    dirs = ensure_data_dirs()
    support_dir = dirs["results"] / "support"
    support_dir.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc)
    bundle_path = support_dir / f"packvision-support-{generated_at.strftime('%Y%m%d-%H%M%S')}.zip"

    with zipfile.ZipFile(bundle_path, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        _write_json(archive, "manifest.json", _manifest(generated_at, bundle_path))
        _write_json(archive, "deployment_readiness.json", _safe_call(build_deployment_readiness))
        _write_json(archive, "depth_status.json", _safe_call(depth_camera_status))
        _write_json(archive, "depth_capture_capabilities.json", _safe_call(depth_capture_capabilities))
        _write_json(archive, "depth_cameras.json", _safe_call(build_depth_camera_inventory))
        _write_json(archive, "device_watchdog.json", _safe_call(build_device_watchdog))
        _write_json(archive, "ai_plugins.json", _safe_call(build_ai_plugin_inventory))
        _write_json(archive, "usage_summary.json", _safe_call(usage_summary))
        _write_text(
            archive,
            "history_latest.csv",
            _safe_call(export_measurements_csv, limit=SUPPORT_BUNDLE_HISTORY_LIMIT),
        )
        _write_text(archive, "usage_events.csv", _safe_call(export_usage_csv, limit=SUPPORT_BUNDLE_USAGE_LIMIT))
        _write_text(
            archive,
            "review_samples.csv",
            _safe_call(export_review_samples_csv, limit=SUPPORT_BUNDLE_REVIEW_LIMIT),
        )
        _write_text(
            archive,
            "review_truth_template.csv",
            _safe_call(export_review_truth_template_csv, limit=SUPPORT_BUNDLE_REVIEW_LIMIT),
        )
        _write_log(archive)

    return bundle_path


def _manifest(generated_at: datetime, bundle_path: Path) -> dict[str, Any]:
    data_root = app_data_dir()
    return {
        "app": "PackVision",
        "version": __version__,
        "generated_at": generated_at.isoformat(),
        "bundle_path": str(bundle_path),
        "app_data_dir": str(data_root),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "limits": {
            "history_rows": SUPPORT_BUNDLE_HISTORY_LIMIT,
            "usage_rows": SUPPORT_BUNDLE_USAGE_LIMIT,
            "review_rows": SUPPORT_BUNDLE_REVIEW_LIMIT,
        },
        "privacy": {
            "include_upload_images_by_default": False,
            "include_result_images_by_default": False,
            "reason": "Support bundles are intended for remote diagnosis and should stay small enough for file transfer.",
        },
        "contents": [
            "deployment_readiness.json",
            "depth_status.json",
            "depth_capture_capabilities.json",
            "depth_cameras.json",
            "device_watchdog.json",
            "ai_plugins.json",
            "usage_summary.json",
            "history_latest.csv",
            "usage_events.csv",
            "review_samples.csv",
            "review_truth_template.csv",
            "logs/PackVision.log",
        ],
    }


def _safe_call(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    try:
        return func(*args, **kwargs)
    except Exception as exc:  # pragma: no cover - this keeps field diagnostics alive.
        return {
            "status": "error",
            "error_type": type(exc).__name__,
            "message": str(exc),
        }


def _write_json(archive: zipfile.ZipFile, name: str, payload: Any) -> None:
    archive.writestr(name, json.dumps(payload, ensure_ascii=False, indent=2, default=str))


def _write_text(archive: zipfile.ZipFile, name: str, payload: Any) -> None:
    archive.writestr(name, payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False, indent=2))


def _write_log(archive: zipfile.ZipFile) -> None:
    log_path = app_data_dir() / "PackVision.log"
    if log_path.exists():
        content = _read_log_tail(log_path)
        archive.writestr("logs/PackVision.log", content)
        return
    archive.writestr("logs/PackVision.log.missing.txt", f"No PackVision.log found at {log_path}")


def _read_log_tail(log_path: Path) -> bytes:
    size = log_path.stat().st_size
    if size <= SUPPORT_BUNDLE_LOG_TAIL_BYTES:
        return log_path.read_bytes()
    with log_path.open("rb") as handle:
        handle.seek(-SUPPORT_BUNDLE_LOG_TAIL_BYTES, 2)
        tail = handle.read()
    header = (
        f"PackVision.log was {size} bytes; only the last "
        f"{SUPPORT_BUNDLE_LOG_TAIL_BYTES} bytes are included.\n"
    ).encode("utf-8")
    return header + tail
