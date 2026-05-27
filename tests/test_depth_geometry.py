import pytest

from packvision.services.depth_geometry import (
    DepthObjectConfig,
    DepthIntrinsics,
    DepthMeasurementConfig,
    DepthMeasurementError,
    measure_depth_object_mask,
    measure_depth_roi,
)


def test_measure_depth_roi_estimates_physical_dimensions():
    import numpy as np

    depth = np.full((480, 640), 1000, dtype=np.float32)
    depth[180:300, 220:420] = 800
    depth[190, 230] = 0
    depth[210, 260] = 4500

    result = measure_depth_roi(
        depth,
        DepthIntrinsics(fx=580, fy=580, cx=320, cy=240, width=640, height=480),
        DepthMeasurementConfig(
            roi=[220, 180, 420, 300],
            background_roi=[20, 20, 120, 120],
        ),
    )

    assert result["status"] == "measured"
    assert result["dimensions"]["length_mm"] == pytest.approx(275.9, abs=0.3)
    assert result["dimensions"]["width_mm"] == pytest.approx(165.5, abs=0.3)
    assert result["dimensions"]["height_mm"] == pytest.approx(200, abs=0.1)
    assert result["dimensions"]["volume_l"] == pytest.approx(9.129, abs=0.01)
    assert "background_depth_used" in result["quality_flags"]
    assert "depth_camera_measurement" in result["quality_flags"]


def test_measure_depth_roi_requires_valid_depth_pixels():
    import numpy as np

    depth = np.zeros((12, 12), dtype=np.float32)

    with pytest.raises(DepthMeasurementError, match="No valid depth pixels"):
        measure_depth_roi(
            depth,
            DepthIntrinsics(fx=100, fy=100, cx=6, cy=6, width=12, height=12),
            DepthMeasurementConfig(roi=[2, 2, 8, 8]),
        )


def test_measure_depth_object_mask_uses_object_extent_not_full_roi():
    import numpy as np

    depth = np.full((100, 120), 1000, dtype=np.float32)
    depth[30:52, 20:70] = 760
    depth[52:75, 20:38] = 760

    result = measure_depth_object_mask(
        depth,
        DepthIntrinsics(fx=200, fy=200, cx=60, cy=50, width=120, height=100),
        DepthObjectConfig(
            roi=[10, 20, 90, 90],
            background_roi=[0, 0, 20, 20],
            object_min_height_mm=40,
            trim_quantile=0.0,
        ),
    )

    assert result["status"] == "measured"
    assert result["dimensions"]["length_mm"] == pytest.approx(186.2, abs=1.0)
    assert result["dimensions"]["width_mm"] == pytest.approx(167.2, abs=1.0)
    assert result["dimensions"]["height_mm"] == pytest.approx(240.0, abs=0.1)
    assert result["depth"]["object_pixel_count"] == 1514
    assert "depth_object_mask_used" in result["quality_flags"]


def test_measure_depth_roi_merges_depth_quality_recommendations():
    import numpy as np

    depth = np.full((20, 20), 1000.0, dtype=np.float32)
    depth[5:15, 5:15] = 0.0
    depth[5:15, 5:9] = 800.0

    result = measure_depth_roi(
        depth,
        DepthIntrinsics(fx=100, fy=100, cx=10, cy=10, width=20, height=20),
        DepthMeasurementConfig(
            roi=[5, 5, 15, 15],
            background_roi=[0, 0, 4, 4],
        ),
    )

    assert result["status"] == "measured"
    assert result["depth_quality"]["roi"]["valid_pixel_ratio"] == pytest.approx(0.4)
    assert "sparse_depth_frame" in result["quality_flags"]
    assert "depth_hole_risk" in result["quality_flags"]
    assert "retake_depth_with_less_reflection" in result["recommendation_codes"]


def test_measure_depth_object_mask_principal_axes_handles_diagonal_long_part():
    import numpy as np

    depth = np.full((24, 24), 1000.0, dtype=np.float32)
    for y in range(4, 20):
        for x in range(4, 20):
            if abs(x - y) <= 1:
                depth[y, x] = 760.0

    result = measure_depth_object_mask(
        depth,
        DepthIntrinsics(fx=100, fy=100, cx=12, cy=12, width=24, height=24),
        DepthObjectConfig(
            roi=[3, 3, 21, 21],
            background_roi=[0, 0, 3, 3],
            object_min_height_mm=80,
            trim_quantile=0.0,
            footprint_method="principal_axes",
        ),
    )

    assert result["status"] == "measured"
    assert result["dimensions"]["length_mm"] == pytest.approx(161.2, abs=1.5)
    assert result["dimensions"]["width_mm"] == pytest.approx(10.7, abs=1.5)
    assert result["depth"]["footprint_method"] == "principal_axes"
    assert result["depth"]["orientation_deg"] == pytest.approx(45.0, abs=1.0)
    assert "principal_axis_extent_used" in result["quality_flags"]
