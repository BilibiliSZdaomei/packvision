import pytest

from packvision.services.depth_quality import analyze_depth_quality


def test_depth_quality_flags_sparse_depth_holes():
    import numpy as np

    depth = np.zeros((20, 20), dtype=np.float32)
    depth[5:15, 5:9] = 850.0

    result = analyze_depth_quality(
        depth,
        roi=[5, 5, 15, 15],
        min_valid_depth_mm=50,
        max_valid_depth_mm=6000,
    )

    assert result["status"] == "review"
    assert result["roi"]["valid_pixel_ratio"] == pytest.approx(0.4)
    assert "sparse_depth_frame" in result["quality_flags"]
    assert "depth_hole_risk" in result["quality_flags"]
    assert "retake_depth_with_less_reflection" in result["recommendation_codes"]


def test_depth_quality_flags_noisy_depth_roi():
    import numpy as np

    depth = np.full((20, 20), 900.0, dtype=np.float32)
    depth[5:15, 5:15] = np.tile([760.0, 1040.0], (10, 5))

    result = analyze_depth_quality(
        depth,
        roi=[5, 5, 15, 15],
        background_roi=[0, 0, 4, 4],
        min_valid_depth_mm=50,
        max_valid_depth_mm=6000,
    )

    assert result["status"] == "review"
    assert result["roi"]["depth_std_mm"] > 100
    assert "noisy_depth_roi" in result["quality_flags"]
    assert "stabilize_depth_camera_and_retake" in result["recommendation_codes"]
