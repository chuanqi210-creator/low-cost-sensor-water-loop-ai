from water_ai.agents.resource_expansion_agent import ResourceExpansionAgent


def test_resource_expansion_agent_prefers_combined_intervention_for_dual_bottleneck() -> None:
    report = ResourceExpansionAgent(
        batch_records=[
            _record(validation_minutes=220, elapsed_min=360, catalyst_lifetime=0.42),
            _record(validation_minutes=230, elapsed_min=390, catalyst_lifetime=0.38),
        ],
        catalyst_spares_remaining=0,
        oxidant_stock_units_remaining=1.4,
        validation_staff_hours_capacity=4.0,
        campaign_time_budget_min=900,
        candidate_interventions=[
            {
                "intervention_id": "add_validation_shift",
                "validation_hours_delta": 5.0,
                "implementation_cost_index": 0.42,
                "implementation_risk": 0.08,
            },
            {
                "intervention_id": "add_catalyst_spare",
                "catalyst_spares_delta": 1,
                "implementation_cost_index": 0.62,
                "implementation_risk": 0.06,
            },
            {
                "intervention_id": "validation_shift_plus_spare",
                "validation_hours_delta": 5.0,
                "catalyst_spares_delta": 2,
                "implementation_cost_index": 0.86,
                "implementation_risk": 0.10,
            },
        ],
    ).run([])

    assert report.metrics["selected_intervention"]["intervention_id"] == "validation_shift_plus_spare"
    assert "validation_capacity" not in report.metrics["selected_intervention"]["residual_bottleneck_ids"]
    assert "catalyst_inventory" not in report.metrics["selected_intervention"]["residual_bottleneck_ids"]


def test_resource_expansion_agent_evaluates_validation_compression() -> None:
    report = ResourceExpansionAgent(
        batch_records=[
            _record(validation_minutes=180, elapsed_min=240, catalyst_lifetime=0.82),
            _record(validation_minutes=160, elapsed_min=220, catalyst_lifetime=0.78),
        ],
        catalyst_spares_remaining=2,
        oxidant_stock_units_remaining=1.6,
        validation_staff_hours_capacity=4.5,
        campaign_time_budget_min=720,
        candidate_interventions=[
            {
                "intervention_id": "compress_low_value_validation",
                "validation_minutes_multiplier": 0.55,
                "implementation_cost_index": 0.18,
                "implementation_risk": 0.16,
            }
        ],
    ).run([])

    selected = report.metrics["selected_intervention"]
    assert selected["intervention_id"] == "compress_low_value_validation"
    assert selected["adjusted_validation_staff_usage"] < report.metrics["baseline"]["campaign_metrics"]["validation_staff_usage"]


def test_resource_expansion_agent_flags_residual_bottlenecks_when_single_action_is_insufficient() -> None:
    report = ResourceExpansionAgent(
        batch_records=[_record(validation_minutes=300, elapsed_min=500, catalyst_lifetime=0.22)],
        catalyst_spares_remaining=0,
        oxidant_stock_units_remaining=0.2,
        validation_staff_hours_capacity=2.0,
        campaign_time_budget_min=360,
        candidate_interventions=[
            {
                "intervention_id": "replenish_oxidant_stock",
                "oxidant_stock_delta": 1.5,
                "implementation_cost_index": 0.22,
                "implementation_risk": 0.04,
            }
        ],
    ).run([])

    selected = report.metrics["selected_intervention"]
    assert selected["intervention_id"] == "replenish_oxidant_stock"
    assert "validation_capacity" in selected["residual_bottleneck_ids"]
    assert report.issues


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
