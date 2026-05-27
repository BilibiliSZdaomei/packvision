import json
import zipfile

from packvision.services.support_bundle import build_support_bundle


def test_support_bundle_collects_field_diagnostics_without_images():
    bundle_path = build_support_bundle()

    assert bundle_path.exists()
    assert bundle_path.suffix == ".zip"
    assert bundle_path.stat().st_size < 10 * 1024 * 1024

    with zipfile.ZipFile(bundle_path) as archive:
        names = set(archive.namelist())
        assert "manifest.json" in names
        assert "deployment_readiness.json" in names
        assert "depth_status.json" in names
        assert "usage_summary.json" in names
        assert "history_latest.csv" in names
        assert "usage_events.csv" in names
        assert "review_truth_template.csv" in names
        assert any(name.startswith("logs/PackVision.log") for name in names)

        manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
        assert manifest["app"] == "PackVision"
        assert manifest["privacy"]["include_upload_images_by_default"] is False
        assert manifest["privacy"]["include_result_images_by_default"] is False
