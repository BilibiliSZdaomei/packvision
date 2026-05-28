from packvision.services.field_report import build_field_trial_report, field_trial_report_markdown


def test_field_trial_report_marks_pre_hardware_ready_when_camera_missing():
    report = build_field_trial_report(
        readiness={
            "status": "needs_attention",
            "summary": {"blocker_count": 0},
            "readiness_modes": {
                "image_only": {"ready": True},
                "depth_preinstall": {"ready": True},
                "camera_trial": {"ready": False, "openni_device_count": 0},
            },
        },
        station={
            "station_status": "measuring",
            "professional_score": {"percent": 83},
            "device_watchdog": {"status": "simulation_fallback"},
            "production_gaps": [{"code": "hardware_validation_pending", "message": "Connect camera."}],
        },
        history_items=[
            {
                "measurement_id": "m-1",
                "created_at": "2026-05-28T09:00:00+00:00",
                "order_id": "PKG-1",
                "status": "measured",
                "confidence": 0.9,
            }
        ],
        review={"summary": {"total_review_samples": 1}},
        usage={"total_calls": 8, "measurement_calls": 2, "failed_calls": 0},
        scale={"status": "manual_weight_ready", "configured": False},
        integration={"dispatch": {"status": "not_configured"}, "pending": 1, "failed": 0},
    )

    assert report["verdict"]["status"] == "pre_hardware_ready"
    assert report["summary"]["history_records"] == 1
    assert report["summary"]["review_samples"] == 1
    assert any(item["id"] == "camera_hardware" and item["status"] == "pending_hardware" for item in report["scorecard"])
    assert any(action["id"] == "connect_astra_pro" for action in report["next_actions"])


def test_field_trial_report_markdown_contains_scorecard():
    report = build_field_trial_report(
        readiness={
            "summary": {"blocker_count": 0},
            "readiness_modes": {
                "image_only": {"ready": True},
                "depth_preinstall": {"ready": True},
                "camera_trial": {"ready": True, "openni_device_count": 1},
            },
        },
        station={"station_status": "ready_to_record", "professional_score": {"percent": 100}},
        history_items=[{"measurement_id": "m-2", "order_id": "PKG-2"}],
        usage={"total_calls": 10, "measurement_calls": 4},
        review={"summary": {"total_review_samples": 0}},
        scale={"status": "auto_weight_ready", "configured": True},
        integration={"dispatch": {"status": "ready"}, "pending": 0, "failed": 0},
    )

    markdown = field_trial_report_markdown(report)

    assert "# PackVision 现场试运行报告" in markdown
    assert "| 本地程序和 UI | pass |" in markdown
    assert "可进入现场试运行" in markdown
