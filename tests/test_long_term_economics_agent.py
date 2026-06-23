from water_ai.agents.long_term_economics_agent import LongTermEconomicsAgent


def test_long_term_agent_pairs_inventory_and_validation_under_lead_time_risk() -> None:
    report = LongTermEconomicsAgent(
        batch_records=[
            _record(validation_minutes=260, elapsed_min=420, catalyst_lifetime=0.35),
            _record(validation_minutes=240, elapsed_min=380, catalyst_lifetime=0.28),
        ],
        catalyst_spares_remaining=0,
        oxidant_stock_units_remaining=0.3,
        validation_staff_hours_capacity=3.0,
        campaign_time_budget_min=720,
        budget_index_limit=5.5,
        catalyst_lead_time_campaigns=2,
        oxidant_lead_time_campaigns=1,
        validation_staff_ramp_campaigns=1,
    ).run([])

    selected = report.metrics["selected_program"]

    assert selected["program_id"] in {"balanced_recovery_program", "full_recovery_program"}
    assert selected["actions"]["validation_hours_delta"] > 0
    assert selected["actions"]["catalyst_spares_delta"] > 0
    assert selected["lead_time_risk"] >= 0.30
    assert any("提前期" in recommendation for recommendation in report.recommendations)


def test_long_term_agent_penalizes_full_program_when_budget_is_tight() -> None:
    report = LongTermEconomicsAgent(
        batch_records=[
            _record(validation_minutes=230, elapsed_min=360, catalyst_lifetime=0.31),
            _record(validation_minutes=220, elapsed_min=350, catalyst_lifetime=0.27),
        ],
        catalyst_spares_remaining=0,
        oxidant_stock_units_remaining=0.4,
        validation_staff_hours_capacity=3.5,
        campaign_time_budget_min=760,
        planning_horizon_campaigns=4,
        budget_index_limit=2.4,
        candidate_programs=[
            {
                "program_id": "balanced_budget_program",
                "description": "分阶段补齐验证、催化剂和氧化剂。",
                "validation_hours_delta": 5.0,
                "catalyst_spares_delta": 2,
                "oxidant_stock_delta": 1.5,
                "campaign_time_delta_min": 240,
                "one_time_cost_index": 0.45,
                "recurring_cost_index": 0.18,
                "implementation_risk": 0.10,
            },
            {
                "program_id": "overbuilt_full_program",
                "description": "一次性满配所有资源。",
                "validation_hours_delta": 7.0,
                "catalyst_spares_delta": 3,
                "oxidant_stock_delta": 2.5,
                "campaign_time_delta_min": 420,
                "validation_minutes_multiplier": 0.74,
                "one_time_cost_index": 2.60,
                "recurring_cost_index": 0.70,
                "implementation_risk": 0.22,
            },
        ],
    ).run([])

    selected = report.metrics["selected_program"]
    ranked = report.metrics["ranked_programs"]

    assert selected["program_id"] == "balanced_budget_program"
    assert ranked[0]["program_score"] > ranked[1]["program_score"]
    assert ranked[1]["budget_pressure"] > 1.0


def test_long_term_agent_keeps_monitoring_when_campaign_has_no_bottlenecks() -> None:
    report = LongTermEconomicsAgent(
        batch_records=[
            _record(validation_minutes=45, elapsed_min=120, catalyst_lifetime=0.84),
            _record(validation_minutes=50, elapsed_min=130, catalyst_lifetime=0.82),
        ],
        catalyst_spares_remaining=3,
        oxidant_stock_units_remaining=2.6,
        validation_staff_hours_capacity=6.0,
        campaign_time_budget_min=720,
        budget_index_limit=3.0,
    ).run([])

    selected = report.metrics["selected_program"]

    assert selected["program_id"] == "minimum_response"
    assert selected["residual_bottleneck_ids"] == []
    assert not report.issues


def _record(*, validation_minutes: int, elapsed_min: int, catalyst_lifetime: float) -> dict[str, object]:
    return {
        "success": True,
        "elapsed_min": elapsed_min,
        "cumulative_cost": 1.0,
        "cumulative_energy": 0.4,
        "validation_minutes": validation_minutes,
        "regeneration_count": 1,
        "replacement_count": 0,
        "oxidant_dose_count": 1,
        "catalyst_lifetime_fraction_end": catalyst_lifetime,
        "catalyst_activity_end": 0.68,
    }
