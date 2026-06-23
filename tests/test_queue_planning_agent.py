from water_ai.agents.operations_scheduling_agent import OperationsSchedulingAgent
from water_ai.agents.queue_planning_agent import QueuePlanningAgent
from water_ai.operations import run_multibatch_campaign


def test_queue_planning_agent_selects_lower_bottleneck_policy() -> None:
    report = QueuePlanningAgent(
        candidate_plans=[
            {
                "policy_id": "arrival_order",
                "description": "arrival order",
                "scenarios": ["matrix_shock", "catalyst_deactivation"],
                "campaign_metrics": {
                    "success_rate": 1.0,
                    "validation_staff_usage": 1.25,
                    "time_budget_usage": 1.1,
                    "catalyst_spares_remaining": 0,
                    "oxidant_stock_units_remaining": 0.8,
                },
                "bottlenecks": [{"bottleneck_id": "catalyst_inventory", "severity": "critical"}],
                "schedule": {"operating_mode": "pause_or_limit_intake"},
            },
            {
                "policy_id": "validation_smoothed",
                "description": "interleaved validation-heavy batches",
                "scenarios": ["reaction_time_insufficient", "matrix_shock"],
                "campaign_metrics": {
                    "success_rate": 1.0,
                    "validation_staff_usage": 0.62,
                    "time_budget_usage": 0.74,
                    "catalyst_spares_remaining": 1,
                    "oxidant_stock_units_remaining": 1.4,
                },
                "bottlenecks": [],
                "schedule": {"operating_mode": "normal_intake"},
            },
        ]
    ).run([])

    assert report.metrics["selected_policy"]["policy_id"] == "validation_smoothed"
    assert report.metrics["ranked_policies"][0]["queue_score"] > report.metrics["ranked_policies"][1]["queue_score"]


def test_queue_planning_agent_can_rank_real_campaign_candidates() -> None:
    scenarios = [
        "sensor_faults",
        "oxidant_limitation",
        "reaction_time_insufficient",
        "matrix_shock",
        "catalyst_deactivation",
    ]
    candidate_plans = []
    for policy_id, ordered in {
        "arrival_order": scenarios,
        "validation_smoothed": ["reaction_time_insufficient", "sensor_faults", "oxidant_limitation", "matrix_shock", "catalyst_deactivation"],
    }.items():
        campaign = run_multibatch_campaign(
            ordered,
            max_steps_per_batch=5,
            initial_catalyst_spares=1,
            initial_oxidant_stock_units=2.2,
            seed=7,
        )
        ops = OperationsSchedulingAgent(
            batch_records=[record.as_dict() for record in campaign.records],
            catalyst_spares_remaining=campaign.catalyst_spares_remaining,
            oxidant_stock_units_remaining=campaign.oxidant_stock_units_remaining,
            validation_staff_hours_capacity=5.5,
            campaign_time_budget_min=960,
        ).run([])
        candidate_plans.append(
            {
                "policy_id": policy_id,
                "description": policy_id,
                "scenarios": ordered,
                "campaign_metrics": ops.metrics["campaign_metrics"],
                "bottlenecks": ops.metrics["bottlenecks"],
                "schedule": ops.metrics["schedule"],
            }
        )

    report = QueuePlanningAgent(candidate_plans=candidate_plans).run([])

    assert len(report.metrics["ranked_policies"]) == 2
    assert report.metrics["selected_policy"]["success_rate"] == 1.0
    assert report.metrics["selected_policy"]["queue_score"] >= 0.0
