from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_static_ui_exposes_usage_statistics_workspace():
    html = (ROOT / "packvision" / "static" / "index.html").read_text(encoding="utf-8")

    assert 'href="#dataCenter"' in html
    assert 'id="dataCenter"' in html
    assert 'id="usage"' in html
    assert 'id="usageSummaryGrid"' in html
    assert 'id="refreshUsageButton"' in html
    assert 'id="exportUsageLink"' in html


def test_static_ui_exposes_review_sample_pool_workspace():
    html = (ROOT / "packvision" / "static" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "packvision" / "static" / "app.js").read_text(encoding="utf-8")
    css = (ROOT / "packvision" / "static" / "styles.css").read_text(encoding="utf-8")

    assert 'href="#dataCenter"' in html
    assert 'id="review"' in html
    assert 'id="reviewSummaryGrid"' in html
    assert 'id="reviewList"' in html
    assert 'id="refreshReviewButton"' in html
    assert 'id="exportReviewLink"' in html
    assert 'id="exportReviewTruthLink"' in html
    assert "/api/review/samples" in js
    assert "/api/review/truth-template.csv" in js
    assert "loadReviewSamples()" in js
    assert ".review-priority-high" in css


def test_static_ui_exposes_lightweight_ai_plugin_status():
    html = (ROOT / "packvision" / "static" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "packvision" / "static" / "app.js").read_text(encoding="utf-8")

    assert 'id="loadAiPluginsButton"' in html
    assert 'id="downloadSupportBundleLink"' in html
    assert "/api/deployment/support-bundle.zip" in html
    assert "/api/depth/vendor-calibration-board.pdf" in html
    assert 'id="aiPluginSummary"' in html
    assert "/api/ai/plugins" in js
    assert "supportBundle" in js
    assert "heavy_models_bundled" in js
    assert "aiPluginNoPlugins" in js


def test_static_ui_has_mobile_navigation_and_focus_states():
    css = (ROOT / "packvision" / "static" / "styles.css").read_text(encoding="utf-8")

    assert "@media (max-width: 720px)" in css
    assert "overflow-x: auto" in css
    assert ":focus-visible" in css
    assert "scrollbar-width: none" in css


def test_depth_workflow_ui_defaults_to_automatic_detection():
    html = (ROOT / "packvision" / "static" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "packvision" / "static" / "app.js").read_text(encoding="utf-8")
    css = (ROOT / "packvision" / "static" / "styles.css").read_text(encoding="utf-8")

    assert '<input id="topImage" name="top_image" type="file" accept="image/*" />' in html
    assert 'id="engineering"' in html
    assert 'id="depthStatusGrid"' in html
    assert 'id="depthProbeSummary"' in html
    assert 'id="liveWorkstation"' in html
    assert 'id="liveStatusGrid"' in html
    assert 'id="liveMonitorGrid"' in html
    assert 'id="cameraMonitor"' in html
    assert 'id="cameraMonitorGrid"' in html
    assert 'data-camera-feed="top"' in html
    assert 'data-camera-feed="front"' in html
    assert 'data-camera-feed="side"' in html
    assert 'id="cameraMonitorCanvasTop"' in html
    assert 'id="cameraMonitorCanvasFront"' in html
    assert 'id="cameraMonitorCanvasSide"' in html
    assert 'id="confirmLiveButton"' in html
    assert 'class="station-strip"' in html
    assert 'id="stationLiveStatus"' in html
    assert 'id="stationChargeableValue"' in html
    assert 'id="stationOrchestrationValue"' in html
    assert 'id="stationReadinessValue"' in html
    assert 'id="actualWeightInput"' in html
    assert 'id="volumetricRuleSelect"' in html
    assert 'id="weightMonitorPanel"' in html
    assert '<details class="workflow-controls" id="workflowControls">' in html
    assert 'id="workflowAutoSummary"' in html
    assert 'id="workflowPackageSelect"' in html
    assert 'id="workflowMaterialSelect"' in html
    assert 'id="workflowCameraCountSelect"' in html
    assert "autoCameraCountForProfile" in js
    assert "loadDepthWorkflow({ auto: true })" in js
    assert "/api/depth/measure-capture" in js
    assert "/api/depth/live/start" in js
    assert "/api/depth/live/state" in js
    assert "/api/depth/live/confirm" in js
    assert "/api/weight/volumetric-rules" in js
    assert "/api/station/snapshot" in js
    assert "/api/deployment/readiness" in js
    assert "renderLiveMonitor" in js
    assert "renderCameraMonitor" in js
    assert "collectCameraMonitorResults" in js
    assert "normalizeCameraRole" in js
    assert "loadStationSnapshot" in js
    assert "loadDeploymentReadiness" in js
    assert "refreshStationHealth" in js
    assert "renderWeightMonitorFromDimensions" in js
    assert "renderStationStrip" in js
    assert "renderDepthEvidenceStage" in js
    assert "startDepthLive({ silent: true })" in js
    assert "buildDepthCapturePayload" in js
    assert "cameraPoseLabels" in js
    assert "wide_roi_depth_capture" in js
    assert "depthCameraPrimary" in js
    assert "package_class=long_part&material_class=reflective&camera_count=2" not in js
    assert ".depth-inline-card" in css
    assert ".live-workstation" in css
    assert ".live-monitor-grid" in css
    assert ".camera-monitor-grid" in css
    assert ".camera-feed.is-primary" in css
    assert ".station-strip" in css
    assert ".depth-evidence" in css
    assert ".weight-monitor-panel" in css
    assert ".workflow-fields" in css
    assert ".workflow-controls" in css


def test_measurement_form_keeps_package_material_optional():
    html = (ROOT / "packvision" / "static" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "packvision" / "static" / "app.js").read_text(encoding="utf-8")
    css = (ROOT / "packvision" / "static" / "styles.css").read_text(encoding="utf-8")

    assert '<details class="parts-card optional-details" id="optionalPartDetails">' in html
    assert 'data-i18n="autoMeasureNoSelection"' in html
    assert 'name="package_hint"' in html
    assert 'name="material_hint"' in html
    assert "autoMeasureNoSelection" in js
    assert ".parts-fields" in css
    assert ".optional-details summary" in css
