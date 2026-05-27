from __future__ import annotations

from typing import Any


READINESS_ITEMS = [
    {
        "id": "administrator_rights",
        "priority": "required",
        "label": "Windows administrator rights",
        "why": "Needed to install Orbbec drivers, OpenNI runtime, and viewer tools.",
    },
    {
        "id": "orbbec_viewer_driver",
        "priority": "required",
        "label": "Orbbec driver and viewer",
        "why": "Validate depth frames in the vendor viewer before debugging PackVision.",
    },
    {
        "id": "usb_data_extension_cable",
        "priority": "required",
        "label": "USB data extension cables",
        "spec": "1 m and 2 m USB 3.0 data-rated cables; avoid charge-only or very long passive cables.",
        "why": "The camera needs a stable fixed position and cannot always sit next to the PC.",
    },
    {
        "id": "powered_usb_hub",
        "priority": "recommended",
        "label": "Powered USB 3.0 hub",
        "spec": "4 or 7 data ports with an external power adapter.",
        "why": "Two cameras share bandwidth and power; a self-powered hub reduces dropouts during trials.",
    },
    {
        "id": "stable_mount_or_tripod",
        "priority": "required",
        "label": "Tripod, arm, or fixed mount",
        "why": "Handheld depth capture makes package dimensions drift.",
    },
    {
        "id": "truth_measurement_tools",
        "priority": "required",
        "label": "Tape measure and caliper",
        "why": "Site acceptance needs human truth values for the validation CSV.",
    },
    {
        "id": "matte_work_surface",
        "priority": "recommended",
        "label": "Flat matte work surface",
        "why": "A stable non-reflective table improves background depth estimates.",
    },
    {
        "id": "lighting_control",
        "priority": "recommended",
        "label": "Stable indoor lighting",
        "why": "Avoid direct sunlight and harsh reflections that can disturb depth frames.",
    },
    {
        "id": "barcode_input_ready",
        "priority": "recommended",
        "label": "Barcode scanner or barcode image upload path",
        "why": "Keeps the measurement tied to the warehouse order ID.",
    },
]

PACKAGE_WORKFLOWS = {
    "standard_carton": {
        "label": "Standard carton",
        "camera_pose": "top-down depth ROI with optional side photo cross-check",
        "capture_step_ids": ["vendor_viewer_depth_check", "top_depth_roi", "side_height_cross_check"],
        "readiness_item_ids": ["stable_mount_or_tripod", "truth_measurement_tools", "matte_work_surface"],
    },
    "long_part": {
        "label": "Long part",
        "camera_pose": "raised top-down or oblique view covering the full length",
        "capture_step_ids": ["vendor_viewer_depth_check", "long_item_depth_roi", "end_to_end_truth_check"],
        "readiness_item_ids": [
            "usb_data_extension_cable",
            "stable_mount_or_tripod",
            "truth_measurement_tools",
            "matte_work_surface",
        ],
    },
    "irregular_or_soft_pack": {
        "label": "Irregular or soft pack",
        "camera_pose": "object-mask depth capture with manual mask review",
        "capture_step_ids": ["vendor_viewer_depth_check", "object_mask_depth_capture", "manual_mask_review"],
        "readiness_item_ids": ["stable_mount_or_tripod", "truth_measurement_tools", "lighting_control"],
    },
    "bulky_irregular": {
        "label": "Bulky irregular",
        "camera_pose": "wide ROI with second angle cross-check when the silhouette is incomplete",
        "capture_step_ids": ["vendor_viewer_depth_check", "wide_roi_depth_capture", "second_angle_cross_check"],
        "readiness_item_ids": [
            "usb_data_extension_cable",
            "stable_mount_or_tripod",
            "truth_measurement_tools",
            "lighting_control",
        ],
    },
}

MATERIAL_WORKFLOWS = {
    "reflective": {
        "label": "Reflective or metal surface",
        "capture_step_ids": ["reflective_surface_cross_check", "manual_review_required"],
        "readiness_item_ids": ["lighting_control", "truth_measurement_tools"],
    },
    "transparent": {
        "label": "Transparent or lens-like surface",
        "capture_step_ids": ["transparent_depth_dropout_review", "manual_review_required"],
        "readiness_item_ids": ["lighting_control", "truth_measurement_tools"],
    },
    "dark_absorbing": {
        "label": "Dark absorbing surface",
        "capture_step_ids": ["dark_surface_depth_dropout_review", "manual_review_required"],
        "readiness_item_ids": ["lighting_control", "truth_measurement_tools"],
    },
    "deformable": {
        "label": "Deformable soft package",
        "capture_step_ids": ["deformable_shape_repeat_capture", "manual_review_required"],
        "readiness_item_ids": ["stable_mount_or_tripod", "truth_measurement_tools"],
    },
}


def build_depth_workflow_guide() -> dict[str, Any]:
    return {
        "readiness_items": READINESS_ITEMS,
        "package_workflows": [{"id": key, **value} for key, value in PACKAGE_WORKFLOWS.items()],
        "material_workflows": [{"id": key, **value} for key, value in MATERIAL_WORKFLOWS.items()],
        "motherboard_required_now": False,
        "first_hour_steps": [
            "install_orbbec_driver",
            "open_vendor_viewer",
            "confirm_depth_frame",
            "run_packvision_depth_status",
            "probe_capture_backend",
            "measure_validation_csv_samples",
        ],
        "upgrade_triggers": [
            "two_cameras_drop_frames_after_direct_usb_and_powered_hub_tests",
            "company_pc_cannot_install_vendor_driver",
            "yolo_or_multi_camera_realtime_pipeline_needs_gpu",
        ],
    }


def recommend_capture_workflow(
    package_class: str = "standard_carton",
    material_class: str | None = None,
    camera_count: int = 1,
) -> dict[str, Any]:
    normalized_package = package_class if package_class in PACKAGE_WORKFLOWS else "irregular_or_soft_pack"
    normalized_material = _clean_optional(material_class)
    package_workflow = PACKAGE_WORKFLOWS[normalized_package]
    material_workflow = MATERIAL_WORKFLOWS.get(normalized_material or "")

    readiness_item_ids = [
        "administrator_rights",
        "orbbec_viewer_driver",
        *package_workflow["readiness_item_ids"],
    ]
    capture_step_ids = list(package_workflow["capture_step_ids"])

    if camera_count >= 2:
        readiness_item_ids.extend(["powered_usb_hub", "usb_data_extension_cable"])
        capture_step_ids.append("separate_usb_controller_or_powered_hub_check")

    if material_workflow:
        readiness_item_ids.extend(material_workflow["readiness_item_ids"])
        capture_step_ids.extend(material_workflow["capture_step_ids"])

    return {
        "package_class": normalized_package,
        "material_class": normalized_material,
        "camera_count": max(1, int(camera_count or 1)),
        "camera_pose": package_workflow["camera_pose"],
        "readiness_item_ids": _unique(readiness_item_ids),
        "capture_step_ids": _unique(capture_step_ids),
        "upgrade_advice": {
            "motherboard_required_now": False,
            "try_before_upgrade": [
                "direct_usb_port",
                "short_data_cable",
                "powered_usb_hub",
                "separate_pc_usb_ports",
            ],
            "consider_hardware_upgrade_when": [
                "depth_viewer_still_drops_frames",
                "two_camera_trial_needs_realtime_high_fps",
                "company_pc_policy_blocks_driver_installation",
            ],
        },
    }


def _clean_optional(value: str | None) -> str | None:
    text = str(value or "").strip().lower()
    return text or None


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique_values: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        unique_values.append(value)
    return unique_values
