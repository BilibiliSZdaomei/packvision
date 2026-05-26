from packvision.services.industry import build_packaging_profile


def test_standard_carton_profile():
    profile = build_packaging_profile(
        {"length_mm": 420, "width_mm": 280, "height_mm": 160, "volume_l": 18.816},
        part_category="filter",
        package_hint="carton",
        actual_weight_kg=3.2,
    )

    assert profile["package_class"] == "standard_carton"
    assert profile["recommended_capture_mode"] == "top_plus_side_or_depth_roi"
    assert profile["chargeable_weight_kg"] == 3.2
    assert "warehouse_ready" in profile["handling_flags"]


def test_long_part_profile():
    profile = build_packaging_profile(
        {"length_mm": 1300, "width_mm": 180, "height_mm": 120, "volume_l": 28.08},
        part_category="shock_absorber",
        package_hint="long_part",
    )

    assert profile["package_class"] == "long_part"
    assert "oversize_length" in profile["handling_flags"]
    assert profile["recommended_capture_mode"] == "depth_roi_long_item"


def test_irregular_soft_package_profile():
    profile = build_packaging_profile(
        {"length_mm": 620, "width_mm": 430, "height_mm": None, "volume_l": None},
        part_category="bumper_trim",
        package_hint="irregular",
    )

    assert profile["package_class"] == "irregular_or_soft_pack"
    assert "needs_depth_or_manual_height" in profile["handling_flags"]
    assert profile["recommended_capture_mode"] == "depth_object_mask"


def test_bulky_irregular_profile_when_sides_are_unbalanced():
    profile = build_packaging_profile(
        {"length_mm": 760, "width_mm": 90, "height_mm": 460, "volume_l": 31.464},
        part_category="control_arm",
        package_hint="wrapped",
        actual_weight_kg=2.5,
    )

    assert profile["package_class"] == "bulky_irregular"
    assert profile["chargeable_weight_kg"] > 2.5
    assert "manual_review_recommended" in profile["handling_flags"]


def test_reflective_material_profile_adds_surface_check_flow():
    profile = build_packaging_profile(
        {"length_mm": 420, "width_mm": 280, "height_mm": 160, "volume_l": 18.816},
        part_category="trim",
        package_hint="carton",
        material_hint="reflective",
    )

    assert profile["package_class"] == "standard_carton"
    assert profile["material_class"] == "reflective"
    assert profile["material_risk_level"] == "high"
    assert "reflective_depth_noise_risk" in profile["handling_flags"]
    assert "material_surface_check" in profile["workflow"]
    assert "retake_or_manual_verify" in profile["workflow"]
