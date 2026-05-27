import pytest

from packvision.services.depth_fusion import DepthFusionError, fuse_depth_measurements


def test_fuse_depth_measurements_uses_conservative_max_for_shipping_size():
    result = fuse_depth_measurements(
        [
            {
                "view_id": "top",
                "role": "top",
                "status": "measured",
                "confidence": 0.8,
                "dimensions": {"length_mm": 820, "width_mm": 360, "height_mm": 180},
                "quality_flags": ["depth_camera_measurement"],
            },
            {
                "view_id": "front",
                "role": "front",
                "status": "measured",
                "confidence": 0.74,
                "dimensions": {"length_mm": 835, "width_mm": 350, "height_mm": 210},
            },
        ],
        disagreement_ratio=0.2,
    )

    assert result["status"] == "measured"
    assert result["dimensions"]["length_mm"] == 835.0
    assert result["dimensions"]["width_mm"] == 360.0
    assert result["dimensions"]["height_mm"] == 210.0
    assert "multi_view_fusion" in result["quality_flags"]
    assert "conservative_dimension_max_used" in result["quality_flags"]


def test_fuse_depth_measurements_flags_large_view_disagreement():
    result = fuse_depth_measurements(
        [
            {"role": "top", "status": "measured", "dimensions": {"length_mm": 1000, "width_mm": 300, "height_mm": 120}},
            {"role": "front", "status": "measured", "dimensions": {"length_mm": 700, "width_mm": 310, "height_mm": 125}},
        ],
        disagreement_ratio=0.1,
    )

    assert result["status"] == "review"
    assert "length_mm" in result["fusion"]["disagreements"]
    assert "view_disagreement_risk" in result["quality_flags"]
    assert "review_multi_view_disagreement" in result["recommendation_codes"]


def test_fuse_depth_measurements_treats_side_as_three_view_role():
    result = fuse_depth_measurements(
        [
            {"role": "top", "status": "measured", "dimensions": {"length_mm": 800, "width_mm": 300, "height_mm": 180}},
            {"role": "front", "status": "measured", "dimensions": {"length_mm": 805, "width_mm": 300, "height_mm": 181}},
            {"role": "side", "status": "measured", "dimensions": {"length_mm": 802, "width_mm": 302, "height_mm": 180}},
        ],
        disagreement_ratio=0.2,
    )

    assert "three_view_ready" in result["quality_flags"]
    assert "complete_three_view_camera_layout" not in result["recommendation_codes"]


def test_fuse_depth_measurements_requires_usable_views():
    with pytest.raises(DepthFusionError):
        fuse_depth_measurements([])
