from __future__ import annotations

from typing import Any

from packvision.services.depth_fusion import DepthFusionError, fuse_depth_measurements


DEFAULT_REQUIRED_ROLES = ("top", "front", "side")
SIDE_ROLES = {"side", "left", "right"}
ROLE_ALIASES = {
    "side": "side",
    "left": "side",
    "right": "side",
    "top": "top",
    "front": "front",
}


def validate_multiview_extrinsics(
    cameras: list[dict[str, Any]],
    *,
    validation_measurements: list[dict[str, Any]] | None = None,
    required_roles: list[str] | None = None,
    reference_role: str = "top",
    disagreement_ratio: float = 0.12,
) -> dict[str, Any]:
    enabled = [_normalize_camera(camera, index) for index, camera in enumerate(cameras) if camera.get("enabled", True)]
    required = [_role_family(role) for role in (required_roles or list(DEFAULT_REQUIRED_ROLES))]
    reference_family = _role_family(reference_role)
    issues: list[dict[str, Any]] = []
    issues.extend(_camera_role_issues(enabled, required))
    issues.extend(_extrinsic_issues(enabled, reference_family))

    fusion_validation = None
    validation_measurements = validation_measurements or []
    if validation_measurements:
        try:
            fusion_validation = fuse_depth_measurements(
                validation_measurements,
                strategy="conservative_max",
                disagreement_ratio=disagreement_ratio,
            )
        except DepthFusionError as exc:
            issues.append({"code": "validation_measurements_invalid", "severity": "blocker", "message": str(exc)})
        else:
            disagreements = fusion_validation.get("fusion", {}).get("disagreements") or {}
            if disagreements:
                issues.append(
                    {
                        "code": "view_dimension_disagreement",
                        "severity": "review",
                        "message": "Validation measurements disagree beyond tolerance.",
                        "details": disagreements,
                    }
                )
    else:
        issues.append(
            {
                "code": "overlap_validation_missing",
                "severity": "warning",
                "message": "Capture the same known carton from each camera before accepting extrinsics.",
            }
        )

    status = _status(issues)
    role_families = {camera["role_family"] for camera in enabled}
    return {
        "status": status,
        "rig": {
            "camera_count": len(enabled),
            "roles": [camera["role"] for camera in enabled],
            "role_families": sorted(role_families),
            "required_roles": required,
            "reference_role": reference_family,
            "ready_for_two_camera_validation": {"top", "front"}.issubset(role_families),
            "ready_for_three_view_validation": all(role in role_families for role in required),
        },
        "cameras": enabled,
        "issues": issues,
        "summary": {
            "blocker_count": len([issue for issue in issues if issue["severity"] == "blocker"]),
            "review_count": len([issue for issue in issues if issue["severity"] == "review"]),
            "warning_count": len([issue for issue in issues if issue["severity"] == "warning"]),
        },
        "fusion_validation": fusion_validation,
        "conservative_policy": {
            "strategy": "conservative_max",
            "disagreement_ratio": float(disagreement_ratio),
            "why": "Never under-report shipping dimensions when camera views conflict.",
        },
        "operator_policy": {
            "warehouse_worker_edits_extrinsics": False,
            "engineer_validates_with_known_carton": True,
            "failed_validation_goes_to_review_pool": True,
        },
    }


def _normalize_camera(camera: dict[str, Any], index: int) -> dict[str, Any]:
    role = _clean(camera.get("role")) or _role_from_index(index)
    role_family = _role_family(role)
    extrinsics = camera.get("extrinsics") or camera.get("extrinsic") or {}
    if isinstance(camera.get("mount"), dict) and not extrinsics:
        extrinsics = camera["mount"].get("extrinsics") or {}
    return {
        "camera_id": _clean(camera.get("camera_id")) or f"camera-{index + 1}",
        "role": role,
        "role_family": role_family,
        "serial_hint": _clean(camera.get("serial_hint") or camera.get("serial_number")),
        "model": _clean(camera.get("model")),
        "enabled": bool(camera.get("enabled", True)),
        "extrinsics": _normalize_extrinsics(extrinsics),
    }


def _normalize_extrinsics(extrinsics: Any) -> dict[str, Any]:
    if not isinstance(extrinsics, dict):
        return {"provided": False, "translation_mm": None, "rotation_deg": None, "source": None}
    translation = _number_list(extrinsics.get("translation_mm") or extrinsics.get("translation"), 3)
    rotation = _number_list(
        extrinsics.get("rotation_deg") or extrinsics.get("rotation_rpy_deg") or extrinsics.get("rotation"),
        3,
    )
    matrix = extrinsics.get("transform_matrix_4x4")
    matrix_valid = isinstance(matrix, list) and len(matrix) == 4 and all(isinstance(row, list) and len(row) == 4 for row in matrix)
    return {
        "provided": bool(translation and rotation) or matrix_valid,
        "translation_mm": translation,
        "rotation_deg": rotation,
        "transform_matrix_4x4_provided": matrix_valid,
        "source": _clean(extrinsics.get("source")),
        "validated_at": _clean(extrinsics.get("validated_at")),
    }


def _camera_role_issues(cameras: list[dict[str, Any]], required: list[str]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    if not cameras:
        return [{"code": "no_enabled_cameras", "severity": "blocker", "message": "At least one enabled camera is required."}]

    role_families = [camera["role_family"] for camera in cameras]
    for role in required:
        if role not in role_families:
            severity = "blocker" if role in {"top", "front"} else "warning"
            issues.append({"code": "missing_required_role", "severity": severity, "message": role})

    serials = [camera["serial_hint"] for camera in cameras if camera.get("serial_hint")]
    if len(cameras) >= 2 and len(serials) < len(cameras):
        issues.append(
            {
                "code": "serial_binding_missing",
                "severity": "warning",
                "message": "Bind serial_hint for every camera before multi-camera production use.",
            }
        )
    if len(serials) != len(set(serials)):
        issues.append({"code": "duplicate_serial_hint", "severity": "blocker", "message": "Camera serial hints must be unique."})
    return issues


def _extrinsic_issues(cameras: list[dict[str, Any]], reference_family: str) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for camera in cameras:
        if camera["role_family"] == reference_family:
            continue
        extrinsics = camera["extrinsics"]
        if not extrinsics["provided"]:
            issues.append(
                {
                    "code": "extrinsics_missing",
                    "severity": "blocker",
                    "message": f"{camera['camera_id']} ({camera['role']}) needs translation/rotation or a 4x4 transform.",
                }
            )
    return issues


def _status(issues: list[dict[str, Any]]) -> str:
    if any(issue["severity"] == "blocker" for issue in issues):
        return "blocked"
    if any(issue["severity"] == "review" for issue in issues):
        return "review"
    if any(issue["severity"] == "warning" for issue in issues):
        return "needs_attention"
    return "ready"


def _role_family(role: Any) -> str:
    normalized = _clean(role) or "aux"
    return ROLE_ALIASES.get(normalized, normalized)


def _role_from_index(index: int) -> str:
    return ("top", "front", "side", "aux")[index] if index < 4 else "aux"


def _number_list(value: Any, expected_len: int) -> list[float] | None:
    if not isinstance(value, list | tuple) or len(value) != expected_len:
        return None
    numbers: list[float] = []
    for item in value:
        try:
            numbers.append(round(float(item), 4))
        except (TypeError, ValueError):
            return None
    return numbers


def _clean(value: Any) -> str | None:
    text = str(value or "").strip().lower()
    return text or None
