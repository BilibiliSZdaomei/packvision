from packvision.services.depth_extrinsics import validate_multiview_extrinsics


def test_validate_multiview_extrinsics_accepts_three_view_rig_with_side_alias():
    result = validate_multiview_extrinsics(
        [
            {"camera_id": "top-01", "role": "top", "serial_hint": "TOP"},
            {
                "camera_id": "front-01",
                "role": "front",
                "serial_hint": "FRONT",
                "extrinsics": {"translation_mm": [0, -650, 420], "rotation_deg": [65, 0, 0]},
            },
            {
                "camera_id": "left-01",
                "role": "left",
                "serial_hint": "LEFT",
                "extrinsics": {"translation_mm": [-520, 0, 430], "rotation_deg": [65, 0, -90]},
            },
        ],
        validation_measurements=[
            {"role": "top", "status": "measured", "confidence": 0.82, "dimensions": {"length_mm": 820, "width_mm": 320, "height_mm": 180}},
            {"role": "front", "status": "measured", "confidence": 0.8, "dimensions": {"length_mm": 825, "width_mm": 318, "height_mm": 182}},
            {"role": "left", "status": "measured", "confidence": 0.78, "dimensions": {"length_mm": 823, "width_mm": 322, "height_mm": 181}},
        ],
    )

    assert result["status"] == "ready"
    assert result["rig"]["ready_for_three_view_validation"] is True
    assert result["rig"]["role_families"] == ["front", "side", "top"]
    assert result["fusion_validation"]["status"] == "measured"
    assert result["summary"]["blocker_count"] == 0


def test_validate_multiview_extrinsics_blocks_missing_transform_and_serial_binding():
    result = validate_multiview_extrinsics(
        [
            {"camera_id": "top-01", "role": "top", "serial_hint": "TOP"},
            {"camera_id": "front-01", "role": "front"},
        ],
        required_roles=["top", "front"],
    )

    assert result["status"] == "blocked"
    issue_codes = {issue["code"] for issue in result["issues"]}
    assert "extrinsics_missing" in issue_codes
    assert "serial_binding_missing" in issue_codes
    assert "overlap_validation_missing" in issue_codes
    assert result["rig"]["ready_for_two_camera_validation"] is True


def test_validate_multiview_extrinsics_marks_conflicting_views_for_review():
    result = validate_multiview_extrinsics(
        [
            {"camera_id": "top-01", "role": "top", "serial_hint": "TOP"},
            {
                "camera_id": "front-01",
                "role": "front",
                "serial_hint": "FRONT",
                "extrinsics": {"translation_mm": [0, -650, 420], "rotation_deg": [65, 0, 0]},
            },
        ],
        required_roles=["top", "front"],
        validation_measurements=[
            {"role": "top", "status": "measured", "confidence": 0.8, "dimensions": {"length_mm": 1000, "width_mm": 300, "height_mm": 200}},
            {"role": "front", "status": "measured", "confidence": 0.78, "dimensions": {"length_mm": 700, "width_mm": 310, "height_mm": 205}},
        ],
        disagreement_ratio=0.1,
    )

    assert result["status"] == "review"
    assert any(issue["code"] == "view_dimension_disagreement" for issue in result["issues"])
    assert "length_mm" in result["fusion_validation"]["fusion"]["disagreements"]
