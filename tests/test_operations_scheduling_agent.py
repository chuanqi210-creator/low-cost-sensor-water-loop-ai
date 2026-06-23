from water_ai.agents.operations_scheduling_agent import OperationsSchedulingAgent
from water_ai.operations import run_multibatch_campaign


def test_multibatch_campaign_builds_operation_records() -> None:
    campaign = run_multibatch_campaign(
        ["sensor_faults", "matrix_shock", "catalyst_deactivation"],
        max_steps_per_batch=5,
        initial_catalyst_spares=1,
        initial_oxidant_stock_units=2.0,
        seed=7,
    )

    assert len(campaign.records) == 3
    assert all(record.success for record in campaign.records)
    assert campaign.total_elapsed_min > 0
    assert campaign.records[-1].catalyst_age_cycles_end >= campaign.records[0].catalyst_age_cycles_end


def test_operations_scheduling_agent_flags_validation_capacity() -> None:
    records = [
        {
            "success": True,
            "elapsed_min": 180,
            "cumulative_cost": 0.8,
            "cumulative_energy": 0.3,
            "validation_minutes": 130,
            "regeneration_count": 0,
            "replacement_count": 0,
            "oxidant_dose_count": 0,
            "catalyst_lifetime_fraction_end": 0.72,
            "catalyst_activity_end": 0.81,
        },
        {
            "success": True,
            "elapsed_min": 210,
            "cumulative_cost": 0.9,
            "cumulative_energy": 0.4,
            "validation_minutes": 120,
            "regeneration_count": 0,
            "replacement_count": 0,
            "oxidant_dose_count": 1,
            "catalyst_lifetime_fraction_end": 0.68,
            "catalyst_activity_end": 0.78,
        },
    ]

    report = OperationsSchedulingAgent(
        batch_records=records,
        validation_staff_hours_capacity=3.5,
        catalyst_spares_remaining=2,
        oxidant_stock_units_remaining=1.4,
        campaign_time_budget_min=600,
    ).run([])

    bottleneck_ids = [item["bottleneck_id"] for item in report.metrics["bottlenecks"]]
    assert "validation_capacity" in bottleneck_ids
    assert report.metrics["schedule"]["operating_mode"] == "staggered_intake"


def test_operations_scheduling_agent_flags_inventory_and_limits_intake() -> None:
    records = [
        {
            "success": True,
            "elapsed_min": 260,
            "cumulative_cost": 1.9,
            "cumulative_energy": 0.8,
            "validation_minutes": 30,
            "regeneration_count": 1,
            "replacement_count": 1,
            "oxidant_dose_count": 2,
            "catalyst_lifetime_fraction_end": 0.31,
            "catalyst_activity_end": 0.58,
        }
    ]

    report = OperationsSchedulingAgent(
        batch_records=records,
        catalyst_spares_remaining=0,
        oxidant_stock_units_remaining=0.4,
        validation_staff_hours_capacity=4.0,
        campaign_time_budget_min=480,
    ).run([])

    action_ids = [item["action_id"] for item in report.metrics["schedule"]["action_queue"]]
    assert "reorder_catalyst_modules" in action_ids
    assert "limit_intake" in action_ids
    assert "replenish_oxidant" in action_ids
