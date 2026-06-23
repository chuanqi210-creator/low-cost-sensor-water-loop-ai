from water_ai.agents.post_replan_replay_agent import PostReplanReplayAgent


def test_post_replan_replay_agent_validates_bottleneck_reduction() -> None:
    report = PostReplanReplayAgent(
        pre_replan_records=[
            _record(validation_minutes=220, elapsed_min=300),
            _record(validation_minutes=230, elapsed_min=300),
            _record(validation_minutes=180, elapsed_min=260),
            _record(validation_minutes=160, elapsed_min=240),
        ],
        online_control_config=_baseline(intake=0.5),
        catalyst_spares_remaining=0,
        oxidant_stock_units_remaining=0.8,
        validation_staff_hours_capacity=3.0,
        campaign_time_budget_min=720,
    ).run([])

    comparison = report.metrics["comparison"]

    assert comparison["verdict"] == "validated"
    assert comparison["after_validation_staff_usage"] < comparison["before_validation_staff_usage"]
    assert "validation_capacity" in comparison["removed_bottleneck_ids"]
    assert "catalyst_inventory" in comparison["removed_bottleneck_ids"]


def test_post_replan_replay_agent_flags_remaining_bottlenecks_without_budget_actions() -> None:
    report = PostReplanReplayAgent(
        pre_replan_records=[
            _record(validation_minutes=240, elapsed_min=360),
            _record(validation_minutes=230, elapsed_min=350),
        ],
        online_control_config={
            "load_control_policy": {"protected_intake_fraction": 1.0},
            "budget_sequence": [],
        },
        catalyst_spares_remaining=0,
        oxidant_stock_units_remaining=0.5,
        validation_staff_hours_capacity=3.0,
        campaign_time_budget_min=600,
    ).run([])

    comparison = report.metrics["comparison"]

    assert comparison["verdict"] == "partial"
    assert comparison["remaining_bottleneck_ids"]
    assert report.issues


def test_post_replan_replay_agent_records_throughput_tradeoff() -> None:
    report = PostReplanReplayAgent(
        pre_replan_records=[
            _record(validation_minutes=120, elapsed_min=180),
            _record(validation_minutes=120, elapsed_min=180),
            _record(validation_minutes=120, elapsed_min=180),
            _record(validation_minutes=120, elapsed_min=180),
        ],
        online_control_config=_baseline(intake=0.25),
        catalyst_spares_remaining=0,
        oxidant_stock_units_remaining=1.0,
        validation_staff_hours_capacity=4.0,
        campaign_time_budget_min=720,
    ).run([])

    comparison = report.metrics["comparison"]
    issue_types = {issue.issue_type for issue in report.issues}

    assert comparison["throughput_fraction"] == 0.25
    assert "throughput_tradeoff" in issue_types


def _baseline(*, intake: float) -> dict[str, object]:
    return {
        "baseline_version": "baseline_v1_replan",
        "load_control_policy": {"protected_intake_fraction": intake},
        "budget_sequence": [
            {"order": 1, "budget_item": "外包低价值验证"},
            {"order": 2, "budget_item": "催化剂备用供应商"},
            {"order": 3, "budget_item": "验证能力批复"},
            {"order": 4, "budget_item": "催化剂库存批复"},
            {"order": 5, "budget_item": "氧化剂库存批复"},
        ],
        "selected_queue_policy": {"policy_id": "high_risk_first"},
        "selected_portfolio": {"package_id": "resilience_bridge_portfolio"},
    }


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
