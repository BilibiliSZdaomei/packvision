from packvision.services.depth_camera import windows_driver_installation_status


def test_windows_driver_installation_status_detects_installed_sensor_driver():
    status = windows_driver_installation_status(
        registry_entries=[
            {
                "DisplayName": "SensorDriver V4.3.0.17",
                "DisplayVersion": "V4.3.0.17",
                "Publisher": "SHENZHEN ORBBEC CO., LTD.",
            }
        ],
        pnputil_output="",
    )

    assert status["installed"] is True
    assert status["status"] == "installed"
    assert any("SensorDriver" in item for item in status["evidence"])


def test_windows_driver_installation_status_detects_orbbec_driver_store_entry():
    status = windows_driver_installation_status(
        registry_entries=[],
        pnputil_output="""
Published Name:     oem221.inf
Original Name:      obdrv4.inf
Provider Name:      Orbbec
Class Name:         Orbbec
Driver Version:     10/20/2020 4.3.0.17

""",
    )

    assert status["installed"] is True
    assert status["driver_store_entries"][0]["Original Name"] == "obdrv4.inf"


def test_windows_driver_installation_status_reports_not_found_without_evidence():
    status = windows_driver_installation_status(registry_entries=[], pnputil_output="")

    assert status["installed"] is False
    assert status["status"] == "not_found"
    assert status["evidence"] == []
