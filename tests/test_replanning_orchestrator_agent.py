from water_ai.agents.replanning_orchestrator_agent import ReplanningOrchestratorAgent


def test_replanning_orchestrator_skips_when_not_required() -> None:
    report = ReplanningOrchestratorAgent(
        current_control_state={"replan_required": False, "project_mode": "steady_monitoring"},
        batch_records=[_record(validation_minutes=40, elapsed_min=120)],
    ).run([])

    assert report.metrics["replan_executed"] is False
    assert not report.issues
    assert "未触发" in report.summary


def test_replanning_orchestrator_runs_downstream_chain_when_required() -> None:
    report = ReplanningOrchestratorAgent(
        current_control_state={"replan_required": True, "project_mode": "replan_and_protect", "rolling_risk": 0.69},
        batch_records=[
            _record(validation_minutes=240, elapsed_min=380),
            _record(validation_minutes=230, elapsed_min=370),
        ],
        queue_candidate_plans=[
            {
                "policy_id": "arrival_order",
                "description": "arrival order",
                "scenarios": ["matrix_shock", "catalyst_deactivation"],
                "campaign_metrics": {
                    "success_rate": 1.0,
                    "validation_staff_usage": 1.2,
                    "time_budget_usage": 1.0,
                    "catalyst_spares_remaining": 0,
                    "oxidant_stock_units_remaining": 1.2,
                },
                "bottlenecks": [{"bottleneck_id": "validation_capacity", "severity": "critical"}],
                "schedule": {"operating_mode": "pause_or_limit_intake"},
            },
            {
                "policy_id": "validation_smoothed",
                "description": "validation smoothed",
                "scenarios": ["catalyst_deactivation", "matrix_shock"],
                "campaign_metrics": {
                    "success_rate": 1.0,
                    "validation_staff_usage": 0.82,
                    "time_budget_usage": 0.86,
                    "catalyst_spares_remaining": 1,
                    "oxidant_stock_units_remaining": 1.5,
                },
                "bottlenecks": [],
                "schedule": {"operating_mode": "normal_intake"},
            },
        ],
        catalyst_spares_remaining=0,
        oxidant_stock_units_remaining=0.8,
        validation_staff_hours_capacity=4.0,
        campaign_time_budget_min=720,
    ).run([])

    trace = report.metrics["replan_trace"]

    assert report.metrics["replan_executed"] is True
    assert trace["queue_planning"]["selected_policy"]["policy_id"] == "validation_smoothed"
    assert trace["resource_expansion"]["selected_intervention"]
    assert trace["adaptive_portfolio"]["selected_portfolio"]
    assert report.recommendations


def test_replanning_orchestrator_can_run_without_queue_candidates() -> None:
    report = ReplanningOrchestratorAgent(
        current_control_state={"replan_required": True, "project_mode": "replan_and_protect"},
        batch_records=[_record(validation_minutes=180, elapsed_min=260)],
        catalyst_spares_remaining=0,
        oxidant_stock_units_remaining=0.6,
        validation_staff_hours_capacity=3.0,
        campaign_time_budget_min=480,
    ).run([])

    trace = report.metrics["replan_trace"]

    assert report.metrics["replan_executed"] is True
    assert trace["queue_planning"]["selected_policy"] == {}
    assert "跳过队列排序" in trace["queue_planning"]["summary"]


def _record(*, validation_minutes: int, elapsed_min: int) -> dict[str, object]:
    return {
        "success": True,
        "elapsed_min": elapsed_min,
        "cumulative_cost": 1.0,
        "cumulative_energy": 0.4,
        "validation_minutes": validation_minutes,
        "regeneration_count": 1,
        "replacement_count": 0,
        "oxidant_dose_count": 1,
        "catalyst_lifetime_fraction_end": 0.36,
        "catalyst_activity_end": 0.62,
    }
