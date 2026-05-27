from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any

from packvision import __version__
from packvision.services.storage import app_data_dir


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_NAMES = ("plugin.json", "packvision-plugin.json")
SUPPORTED_ENGINES = {
    "onnxruntime_cpu",
    "external_http",
    "python_stub",
}
KNOWN_CAPABILITIES = {
    "box_detection",
    "oriented_box_detection",
    "segmentation",
    "manual_review_assist",
    "phone_depth_prior",
    "capture_quality_assist",
}


def build_ai_plugin_inventory(model_roots: list[str | Path] | None = None) -> dict[str, Any]:
    roots = _plugin_roots(model_roots)
    plugins: list[dict[str, Any]] = []
    for root in roots:
        plugins.extend(_plugins_from_root(root))

    enabled = [plugin for plugin in plugins if plugin["enabled"]]
    ready = [plugin for plugin in enabled if plugin["status"] == "ready"]
    return {
        "status": "ready" if ready else "not_configured",
        "version": __version__,
        "base_package_policy": {
            "heavy_models_bundled": False,
            "default_runtime": "opencv_depth_manual_fallback",
            "warehouse_worker_visible": False,
            "explain": "The base EXE stays lightweight; YOLO/SAM/Depth-prior models are optional plugins.",
        },
        "plugin_roots": [
            {
                "path": str(root),
                "exists": root.exists(),
            }
            for root in roots
        ],
        "supported_engines": sorted(SUPPORTED_ENGINES),
        "known_capabilities": sorted(KNOWN_CAPABILITIES),
        "summary": {
            "installed_count": len(plugins),
            "enabled_count": len(enabled),
            "ready_count": len(ready),
            "attention_count": len([plugin for plugin in enabled if plugin["status"] != "ready"]),
        },
        "plugins": plugins,
        "fallback_chain": [
            "depth_camera_measurement",
            "opencv_aruco_and_contour",
            "manual_annotation_review",
            "review_sample_pool",
        ],
    }


def _plugin_roots(model_roots: list[str | Path] | None) -> list[Path]:
    if model_roots:
        candidates = [Path(root) for root in model_roots]
    else:
        candidates = []
        env_root = os.environ.get("PACKVISION_AI_MODEL_ROOT")
        if env_root:
            candidates.append(Path(env_root))
        else:
            candidates.extend([PROJECT_ROOT / "models", app_data_dir() / "models"])
            if getattr(sys, "frozen", False):
                candidates.append(Path(sys.executable).resolve().parent / "models")

    roots: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        resolved = candidate.expanduser().resolve()
        key = str(resolved).lower()
        if key not in seen:
            roots.append(resolved)
            seen.add(key)
    return roots


def _plugins_from_root(root: Path) -> list[dict[str, Any]]:
    if not root.exists():
        return []
    plugins: list[dict[str, Any]] = []
    for manifest in sorted(_manifest_paths(root)):
        plugins.append(_plugin_from_manifest(manifest, root))
    return plugins


def _manifest_paths(root: Path) -> list[Path]:
    direct = [root / name for name in MANIFEST_NAMES if (root / name).is_file()]
    nested = [
        path
        for name in MANIFEST_NAMES
        for path in root.glob(f"*/{name}")
        if path.is_file()
    ]
    return direct + nested


def _plugin_from_manifest(manifest_path: Path, root: Path) -> dict[str, Any]:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return _invalid_plugin(manifest_path, root, str(exc))

    if not isinstance(manifest, dict):
        return _invalid_plugin(manifest_path, root, "Manifest must be a JSON object.")

    plugin_dir = manifest_path.parent
    plugin_id = _text(manifest.get("id")) or plugin_dir.name
    engine = _text(manifest.get("engine")) or "python_stub"
    capabilities = _normalized_list(manifest.get("capabilities"))
    enabled = bool(manifest.get("enabled", True))
    file_checks = _model_file_checks(plugin_dir, manifest.get("model_files"))
    dependency_checks = _dependency_checks(manifest.get("runtime_dependencies"))
    issues = _issues(engine, capabilities, file_checks, dependency_checks)
    status = _status(enabled, issues)

    return {
        "id": plugin_id,
        "name": _text(manifest.get("name")) or plugin_id,
        "version": _text(manifest.get("version")) or "0.0.0",
        "enabled": enabled,
        "status": status,
        "engine": engine,
        "capabilities": capabilities,
        "priority": _text(manifest.get("priority")) or "assist",
        "description": _text(manifest.get("description")),
        "manifest_path": str(manifest_path),
        "plugin_dir": str(plugin_dir),
        "model_files": file_checks,
        "runtime_dependencies": dependency_checks,
        "issues": issues,
        "operator_policy": {
            "worker_selects_model": False,
            "ai_is_assistive": True,
            "fallback_required": True,
        },
    }


def _invalid_plugin(manifest_path: Path, root: Path, error: str) -> dict[str, Any]:
    return {
        "id": manifest_path.parent.name,
        "name": manifest_path.parent.name,
        "version": "0.0.0",
        "enabled": False,
        "status": "invalid_manifest",
        "engine": None,
        "capabilities": [],
        "priority": "assist",
        "description": None,
        "manifest_path": str(manifest_path),
        "plugin_dir": str(manifest_path.parent),
        "model_files": [],
        "runtime_dependencies": [],
        "issues": [{"code": "invalid_manifest", "message": error, "severity": "blocker"}],
        "operator_policy": {
            "worker_selects_model": False,
            "ai_is_assistive": True,
            "fallback_required": True,
        },
        "root": str(root),
    }


def _model_file_checks(plugin_dir: Path, raw_files: Any) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    if not isinstance(raw_files, list):
        return checks
    for item in raw_files:
        if isinstance(item, str):
            rel_path = item
            required = True
        elif isinstance(item, dict):
            rel_path = _text(item.get("path"))
            required = bool(item.get("required", True))
        else:
            continue
        if not rel_path:
            continue
        path = (plugin_dir / rel_path).resolve()
        exists = path.is_file()
        checks.append(
            {
                "path": rel_path,
                "absolute_path": str(path),
                "required": required,
                "exists": exists,
                "size_mb": round(path.stat().st_size / 1024 / 1024, 2) if exists else None,
            }
        )
    return checks


def _dependency_checks(raw_dependencies: Any) -> list[dict[str, Any]]:
    dependencies = _normalized_list(raw_dependencies)
    return [{"package": dependency, "available": _dependency_available(dependency)} for dependency in dependencies]


def _dependency_available(dependency: str) -> bool:
    try:
        return importlib.util.find_spec(dependency) is not None
    except (ImportError, AttributeError, ValueError):
        return False


def _issues(
    engine: str,
    capabilities: list[str],
    file_checks: list[dict[str, Any]],
    dependency_checks: list[dict[str, Any]],
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if engine not in SUPPORTED_ENGINES:
        issues.append({"code": "unsupported_engine", "message": engine, "severity": "blocker"})
    unknown_capabilities = [item for item in capabilities if item not in KNOWN_CAPABILITIES]
    if unknown_capabilities:
        issues.append(
            {
                "code": "unknown_capability",
                "message": ",".join(unknown_capabilities),
                "severity": "warning",
            }
        )
    for check in file_checks:
        if check["required"] and not check["exists"]:
            issues.append({"code": "missing_model_file", "message": check["path"], "severity": "blocker"})
    for check in dependency_checks:
        if not check["available"]:
            issues.append({"code": "missing_runtime_dependency", "message": check["package"], "severity": "blocker"})
    return issues


def _status(enabled: bool, issues: list[dict[str, str]]) -> str:
    if not enabled:
        return "disabled"
    if any(issue["severity"] == "blocker" for issue in issues):
        return "needs_attention"
    return "ready"


def _text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _normalized_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]
