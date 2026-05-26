import pytest

from packvision.services.depth_geometry import (
    DepthIntrinsics,
    DepthMeasurementConfig,
    DepthMeasurementError,
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
