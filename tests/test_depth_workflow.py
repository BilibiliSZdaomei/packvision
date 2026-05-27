from packvision.services.depth_workflow import build_depth_workflow_guide, recommend_capture_workflow


def test_depth_workflow_guide_includes_field_hardware_kit_without_motherboard():
    guide = build_depth_workflow_guide()
    item_ids = {item["id"] for item in guide["readiness_items"]}

    assert "powered_usb_hub" in item_ids
    assert "usb_data_extension_cable" in item_ids
    assert "stable_mount_or_tripod" in item_ids
    assert guide["motherboard_required_now"] is False


def test_recommend_capture_workflow_handles_two_camera_reflective_long_parts():
    workflow = recommend_capture_workflow(
        package_class="long_part",
        material_class="reflective",
        camera_count=2,
    )

    assert workflow["package_class"] == "long_part"
    assert workflow["material_class"] == "reflective"
    assert "powered_usb_hub" in workflow["readiness_item_ids"]
    assert "long_item_depth_roi" in workflow["capture_step_ids"]
    assert "reflective_surface_cross_check" in workflow["capture_step_ids"]
    assert workflow["upgrade_advice"]["motherboard_required_now"] is False
