from __future__ import annotations

import time

from packvision.services.depth_capture import DepthCaptureConfig, DepthFrameBundle
from packvision.services.depth_live import DepthLiveConfig, DepthLiveManager


def test_live_manager_falls_back_to_simulation_when_hardware_capture_hangs():
    def hanging_capture(_config: DepthCaptureConfig) -> DepthFrameBundle:
        time.sleep(2)
        raise AssertionError("hardware capture should have timed out before returning")

    manager = DepthLiveManager(hanging_capture)
    try:
        manager.start(
            DepthLiveConfig(
                backend="auto",
                timeout_ms=250,
                interval_ms=50,
                allow_simulation=True,
                stable_required_frames=1,
            )
        )

        state = {}
        for _ in range(20):
            state = manager.state()
            if state.get("simulation_active") and state.get("frame_count", 0) > 0:
                break
            time.sleep(0.08)

        assert state["running"] is True
        assert state["simulation_active"] is True
        assert state["frame_count"] > 0
        assert state["can_confirm"] is True
        assert state["latest_result"]["dimensions"]["length_mm"] > 0
        assert "timed out" in state["last_error"]
    finally:
        manager.stop()
