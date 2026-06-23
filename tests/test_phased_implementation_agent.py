from water_ai.agents.phased_implementation_agent import PhasedImplementationAgent


def test_phased_implementation_agent_builds_transition_and_procurement_plan() -> None:
    report = PhasedImplementationAgent(
        selected_program=_full_program(),
        planning_assumptions={
            "planning_horizon_campaigns": 4,
            "budget_index_limit": 4.2,
            "catalyst_lead_time_campaigns": 2,
            "oxidant_lead_time_campaigns": 1,
            "validation_staff_ramp_campaigns": 1,
        },
        validation_staff_hours_capacity=5.5,
    ).run([])

    phase_ids = [phase["phase_id"] for phase in report.metrics["phase_plan"]]
    intake_policy = report.metrics["intake_policy"]

    assert phase_ids[0] == "phase_0_transition_control"
    assert "phase_2_catalyst_procurement_lock" in phase_ids
    assert "phase_3_integrated_ramp_up" in phase_ids
    assert intake_policy["campaign_0_max_intake_fraction"] < 1.0
    assert report.metrics["readiness"]["estimated_ready_campaign"] >= 2
    assert any(issue.issue_type == "transition_gap" for issue in report.issues)


def test_phased_implementation_agent_keeps_monitoring_plan_for_minimum_response() -> None:
    report = PhasedImplementationAgent(
        selected_program={
            "program_id": "minimum_response",
            "program_score": 0.74,
            "service_level": 0.82,
            "lead_time_risk": 0.02,
            "budget_pressure": 0.05,
            "residual_operational_risk": 0.03,
            "residual_bottleneck_ids": [],
            "actions": {
                "validation_hours_delta": 0.0,
                "catalyst_spares_delta": 0,
                "oxidant_stock_delta": 0.0,
                "campaign_time_delta_min": 0,
                "validation_minutes_multiplier": 1.0,
            },
        },
        planning_horizon_campaigns=4,
    ).run([])

    phases = report.metrics["phase_plan"]

    assert len(phases) == 1
    assert phases[0]["phase_id"] == "phase_0_monitoring"
    assert report.metrics["schedule_risk"] < 0.2
    assert not report.issues


def test_phased_implementation_agent_flags_staged_budget_need() -> None:
    program = _full_program()
    program["budget_pressure"] = 1.45

    report = PhasedImplementationAgent(
        selected_program=program,
        planning_assumptions={"catalyst_lead_time_campaigns": 2, "oxidant_lead_time_campaigns": 1, "validation_staff_ramp_campaigns": 1},
    ).run([])

    issue_types = {issue.issue_type for issue in report.issues}

    assert "staged_budget_required" in issue_types
    assert report.metrics["schedule_risk"] > 0.30
    assert any("阶段" in recommendation for recommendation in report.recommendations)


def _full_program() -> dict[str, object]:
    return {
        "program_id": "full_recovery_program",
        "program_score": 0.651,
        "service_level": 0.723,
        "resource_resilience": 0.805,
        "multi_campaign_cost_index": 5.836,
        "budget_pressure": 1.39,
        "lead_time_risk": 0.53,
        "compression_risk": 0.196,
        "residual_operational_risk": 0.299,
        "residual_bottleneck_ids": [],
        "actions": {
            "validation_hours_delta": 5.0,
            "catalyst_spares_delta": 2,
            "oxidant_stock_delta": 2.0,
            "campaign_time_delta_min": 360,
            "validation_minutes_multiplier": 0.78,
        },
    }
