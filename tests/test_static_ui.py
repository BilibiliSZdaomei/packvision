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
