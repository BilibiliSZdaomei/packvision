from __future__ import annotations

import time

from packvision.services.depth_capture import DepthCaptureConfig, DepthFrameBundle
from packvision.services.depth_geometry import DepthIntrinsics
from packvision.services import depth_live
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


def test_live_default_config_samples_secondary_camera_results(monkeypatch):
    monkeypatch.setattr(
        depth_live,
        "load_depth_camera_config",
        lambda: {
            "cameras": [
                {"camera_id": "astra-pro-top-01", "role": "top", "enabled": True},
                {"camera_id": "astra-pro-front-01", "role": "front", "enabled": True},
            ]
        },
    )

    def rig_capture(config: DepthCaptureConfig) -> DepthFrameBundle:
        role = config.role or "top"
        depth = [[1000.0 for _ in range(12)] for _ in range(10)]
        if role == "top":
            for y in range(3, 8):
                for x in range(3, 9):
                    depth[y][x] = 760.0
        return DepthFrameBundle(
            depth_frame=depth,
            intrinsics=DepthIntrinsics(fx=100, fy=100, cx=6, cy=5, width=12, height=10),
            backend="openni2_primesense",
            camera_id=f"astra-pro-{role}-01",
            role=role,
            serial_number=f"{role}-serial",
            frame_index=1,
            timestamp_us=123456,
        )

    manager = DepthLiveManager(rig_capture)
    try:
        manager.start(
            DepthLiveConfig(
                backend="auto",
                timeout_ms=500,
                interval_ms=50,
                allow_simulation=False,
                stable_required_frames=1,
            )
        )

        state = {}
        for _ in range(20):
            state = manager.state()
            if len(state.get("camera_results") or []) == 2:
                break
            time.sleep(0.06)

        roles = {item["camera_capture"]["role"] for item in state["camera_results"]}
        assert roles == {"top", "front"}
        front = next(item for item in state["camera_results"] if item["camera_capture"]["role"] == "front")
        assert front["status"] == "waiting_for_object"
        assert front["camera_capture"]["camera_id"] == "astra-pro-front-01"
    finally:
        manager.stop()


def test_live_waiting_state_keeps_camera_capture_evidence():
    def flat_capture(config: DepthCaptureConfig) -> DepthFrameBundle:
        return DepthFrameBundle(
            depth_frame=[[1000.0 for _ in range(10)] for _ in range(8)],
            intrinsics=DepthIntrinsics(fx=100, fy=100, cx=5, cy=4, width=10, height=8),
            backend="openni2_primesense",
            camera_id="astra-pro-front-01",
            role=config.role,
            serial_number="front-serial",
            frame_index=7,
            timestamp_us=123456,
        )

    manager = DepthLiveManager(flat_capture)
    try:
        manager.start(
            DepthLiveConfig(
                backend="auto",
                role="front",
                timeout_ms=500,
                interval_ms=50,
                allow_simulation=False,
            )
        )

        state = {}
        for _ in range(20):
            state = manager.state()
            if state.get("latest_result"):
                break
            time.sleep(0.06)

        assert state["status"] == "waiting_for_object"
        assert state["simulation_active"] is False
        assert state["latest_result"]["camera_capture"]["camera_id"] == "astra-pro-front-01"
        assert state["latest_result"]["camera_capture"]["role"] == "front"
        assert state["latest_result"]["camera_capture"]["frame_shape"] == {"height": 8, "width": 10}
        assert state["latest_result"]["live_capture"]["status"] == "waiting_for_object"
    finally:
        manager.stop()
