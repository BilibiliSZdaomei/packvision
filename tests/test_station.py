from packvision.services.station import build_station_snapshot


def test_station_snapshot_scores_professional_dws_capabilities():
    snapshot = build_station_snapshot(
        live_state={
            "status": "stable_ready",
            "can_confirm": True,
            "simulation_active": True,
            "fps": 12.5,
            "stable_result": {
                "dimensions": {"length_mm": 500, "width_mm": 320, "height_mm": 210},
                "quality_flags": [],
            },
        },
        latest_measurements=[
            {
                "measurement_id": "m1",
                "order_id": "SO-1",
                "length_mm": 500,
                "chargeable_weight_kg": 8.2,
                "actual_weight_kg": 6.4,
                "top_result_url": "/results/a.jpg",
            }
        ],
        usage={"total_calls": 10},
        scale_status={"status": "auto_weight_ready", "source": "mock", "weight_kg": 6.4, "stable": True},
        integration_outbox={"delivery_mode": "local_outbox", "pending": 1, "failed": 0, "due_for_retry": 1, "total": 1},
        device_watchdog={
            "status": "live_camera_active",
            "severity": "ok",
            "operator_mode": "live_camera_measurement",
            "safe_to_record_live": True,
            "signals": {"device_count": 1, "simulation_active": False, "live_stale": False},
            "issues": [],
        },
    )

    assert snapshot["station_status"] == "ready_to_record"
    assert snapshot["architecture_decision"]["mode"] == "medium_upgrade_modular_monolith"
    assert [camera["role"] for camera in snapshot["camera_monitor_layout"]] == ["top", "front", "side"]
    assert snapshot["professional_score"]["percent"] == 100
    assert snapshot["current_candidate"]["can_confirm"] is True
    assert snapshot["latest_record"]["order_id"] == "SO-1"
    assert snapshot["scale_status"]["source"] == "mock"
    assert snapshot["integration_outbox"]["pending"] == 1
    assert next(item for item in snapshot["dws_capabilities"] if item["id"] == "weighing")["status"] == "auto_ready"
    assert next(item for item in snapshot["dws_capabilities"] if item["id"] == "integration")["status"] == "outbox_ready"
    assert next(item for item in snapshot["dws_capabilities"] if item["id"] == "device_health")["status"] == "watchdog_ready"
    assert {item["id"] for item in snapshot["dws_capabilities"]} == {
        "dimensioning",
        "weighing",
        "scanning",
        "evidence",
        "integration",
        "device_health",
    }
    assert any(gap["code"] == "hardware_validation_pending" for gap in snapshot["production_gaps"])
    assert any(gap["code"] == "wms_connector_pending" for gap in snapshot["production_gaps"])


def test_station_snapshot_reports_pilot_gaps_when_no_record_exists():
    snapshot = build_station_snapshot(
        live_state={"status": "waiting_for_object", "can_confirm": False},
        latest_measurements=[],
        usage={"total_calls": 0},
    )

    assert snapshot["station_status"] == "waiting_for_object"
    assert snapshot["professional_score"]["level"] == "prototype_to_pilot"
    assert any(gap["code"] == "scale_adapter_pending" for gap in snapshot["production_gaps"])
    assert "wms_tms_push_and_retry_queue" in snapshot["next_upgrade_tracks"]
