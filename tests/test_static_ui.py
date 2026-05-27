from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_static_ui_exposes_usage_statistics_workspace():
    html = (ROOT / "packvision" / "static" / "index.html").read_text(encoding="utf-8")

    assert 'href="#usage"' in html
    assert 'id="usage"' in html
    assert 'id="usageSummaryGrid"' in html
    assert 'id="refreshUsageButton"' in html
    assert 'id="exportUsageLink"' in html


def test_static_ui_has_mobile_navigation_and_focus_states():
    css = (ROOT / "packvision" / "static" / "styles.css").read_text(encoding="utf-8")

    assert "@media (max-width: 720px)" in css
    assert "overflow-x: auto" in css
    assert ":focus-visible" in css
    assert "scrollbar-width: none" in css


def test_depth_workflow_ui_is_scenario_driven():
    html = (ROOT / "packvision" / "static" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "packvision" / "static" / "app.js").read_text(encoding="utf-8")
    css = (ROOT / "packvision" / "static" / "styles.css").read_text(encoding="utf-8")

    assert 'id="workflowPackageSelect"' in html
    assert 'id="workflowMaterialSelect"' in html
    assert 'id="workflowCameraCountSelect"' in html
    assert "workflowPackageSelect?.value" in js
    assert "workflowMaterialSelect?.value" in js
    assert "workflowCameraCountSelect?.value" in js
    assert "cameraPoseLabels" in js
    assert "wide_roi_depth_capture" in js
    assert "package_class=long_part&material_class=reflective&camera_count=2" not in js
    assert ".workflow-controls" in css
