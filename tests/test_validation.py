import pytest

from packvision.services.validation import build_trial_plan, evaluate_trial_run


def test_trial_plan_covers_auto_parts_package_scenarios():
    plan = build_trial_plan()
    scenario_ids = {scenario["id"] for scenario in plan["scenarios"]}

    assert {"standard_carton", "long_part", "irregular_or_soft_pack"}.issubset(scenario_ids)
    assert {"reflective", "transparent", "dark_absorbing", "deformable"}.issubset(
        set(plan["abnormal_materials"])
    )
    assert plan["minimum_total_samples"] >= 28


def test_evaluate_trial_run_accepts_within_tolerance_standard_carton():
    result = evaluate_trial_run(
        [
            {
                "sample_id": "STD-001",
                "package_class": "standard_carton",
                "measured": {"length_mm": 402, "width_mm": 299, "height_mm": 201},
                "truth": {"length_mm": 400, "width_mm": 300, "height_mm": 200},
            }
        ]
    )

    assert result["samples"][0]["status"] == "pass"
    assert result["samples"][0]["max_abs_error_mm"] == pytest.approx(2.0)
    assert result["summary"]["failed_samples"] == 0


def test_evaluate_trial_run_rejects_transparent_material_large_error():
    result = evaluate_trial_run(
        [
            {
                "sample_id": "MAT-001",
                "package_class": "standard_carton",
                "material_class": "transparent",
                "measured": {"length_mm": 450, "width_mm": 300, "height_mm": 170},
                "truth": {"length_mm": 400, "width_mm": 300, "height_mm": 200},
            }
        ]
    )

    sample = result["samples"][0]
    assert sample["status"] == "fail"
    assert "manual_review_required" in sample["flags"]
    assert result["summary"]["ready_for_site_rollout"] is False
