from water_ai.agents.implementation_stress_test_agent import ImplementationStressTestAgent


def test_implementation_stress_test_agent_flags_catalyst_delay_contingency() -> None:
    report = ImplementationStressTestAgent(
        selected_program=_selected_program(),
        phase_plan=_phase_plan(),
        intake_policy=_intake_policy(),
        inventory_policy=_inventory_policy(),
        validation_staffing_plan=_validation_plan(),
        stress_scenarios=[
            {"scenario_id": "on_schedule"},
            {"scenario_id": "catalyst_delay", "catalyst_delay_campaigns": 2},
        ],
    ).run([])

    worst = report.metrics["worst_case"]

    assert worst["scenario_id"] == "catalyst_delay"
    assert worst["catalyst_stockout_risk"] > 0
    assert any("催化剂" in action for action in worst["contingency_actions"])
    assert report.metrics["guardrails"]["latest_safe_ready_campaign"] > _intake_policy()["estimated_ready_campaign"]


def test_implementation_stress_test_agent_lowers_intake_under_combined_pressure() -> None:
    report = ImplementationStressTestAgent(
        selected_program=_selected_program(),
        phase_plan=_phase_plan(),
        intake_policy=_intake_policy(),
        inventory_policy=_inventory_policy(),
        validation_staffing_plan=_validation_plan(),
        stress_scenarios=[
            {
                "scenario_id": "combined_delay_high_intake",
                "catalyst_delay_campaigns": 1,
                "validation_ramp_delay_campaigns": 1,
                "budget_release_fraction": 0.7,
                "intake_pressure_multiplier": 1.3,
            }
        ],
    ).run([])

    scenario = report.metrics["ranked_stress_scenarios"][0]

    assert scenario["protected_intake_fraction"] <= 0.5
    assert scenario["scenario_risk"] >= 0.35
    assert report.issues


def test_implementation_stress_test_agent_keeps_on_schedule_risk_low() -> None:
    report = ImplementationStressTestAgent(
        selected_program=_selected_program(),
        phase_plan=_phase_plan(),
        intake_policy=_intake_policy(),
        inventory_policy=_inventory_policy(),
        validation_staffing_plan=_validation_plan(),
        stress_scenarios=[{"scenario_id": "on_schedule"}],
    ).run([])

    scenario = report.metrics["ranked_stress_scenarios"][0]

    assert scenario["scenario_risk"] < 0.15
    assert report.metrics["robustness_score"] > 0.85
    assert not report.issues


def _selected_program() -> dict[str, object]:
    return {
        "program_id": "full_recovery_program",
        "program_score": 0.651,
        "service_level": 0.723,
        "budget_pressure": 1.39,
        "lead_time_risk": 0.53,
        "residual_operational_risk": 0.299,
        "actions": {
            "validation_hours_delta": 5.0,
            "catalyst_spares_delta": 2,
            "oxidant_stock_delta": 2.0,
            "campaign_time_delta_min": 360,
            "validation_minutes_multiplier": 0.78,
        },
    }


def _phase_plan() -> list[dict[str, object]]:
    return [
        {"phase_id": "phase_0_transition_control", "campaign_start": 0, "campaign_end": 0},
        {"phase_id": "phase_1_validation_and_oxidant_ramp", "campaign_start": 1, "campaign_end": 1},
        {"phase_id": "phase_2_catalyst_procurement_lock", "campaign_start": 1, "campaign_end": 2},
        {"phase_id": "phase_3_integrated_ramp_up", "campaign_start": 2, "campaign_end": 3},
    ]


def _intake_policy() -> dict[str, object]:
    return {
        "campaign_0_max_intake_fraction": 0.5,
        "pre_ready_max_intake_fraction": 0.65,
        "post_ready_max_intake_fraction": 1.0,
        "estimated_ready_campaign": 2,
    }


def _inventory_policy() -> dict[str, object]:
    return {
        "catalyst_safety_stock": 2,
        "catalyst_reorder_point": 2,
        "oxidant_safety_stock_units": 1.2,
        "oxidant_reorder_point_campaigns": 1,
    }


def _validation_plan() -> dict[str, object]:
    return {
        "base_capacity_h_per_campaign": 5.5,
        "target_capacity_h_per_campaign": 10.5,
        "ramp_campaigns": 1,
    }
