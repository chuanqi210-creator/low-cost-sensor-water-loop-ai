from water_ai.agents.recovery_strategy_writeback_agent import RecoveryStrategyWritebackAgent


def test_recovery_strategy_writeback_agent_writes_conditional_target_recovery() -> None:
    report = RecoveryStrategyWritebackAgent(
        time_budget_recovery_metrics=_metrics(
            selected={
                "candidate_id": "stagger_validation_overlap",
                "stable": True,
                "target_recovery": True,
                "target_intake_fraction": 0.75,
                "actual_throughput_fraction": 0.75,
                "admitted_batch_count": 6,
                "time_budget_usage": 0.884,
                "validation_staff_usage": 0.394,
                "elapsed_reduction_min": 90.2,
                "queue_policy": "source_order",
                "scenario_sequence": ["matrix_shock", "catalyst_deactivation"],
            }
        ),
        previous_baseline=_baseline(),
        baseline_version="baseline_v1_replan",
    ).run([])

    updated = report.metrics["recovery_strategy_baseline"]
    config = updated["online_control_config"]
    recovery = config["recovery_control_policy"]

    assert updated["baseline_version"] == "baseline_v1_replan_recovery"
    assert updated["writeback_decision"]["writeback_mode"] == "conditional_target_recovery"
    assert config["load_control_policy"]["protected_intake_fraction"] == 0.75
    assert config["load_control_policy"]["fallback_intake_fraction"] == 0.6
    assert recovery["enabled"] is True
    assert recovery["selected_candidate_id"] == "stagger_validation_overlap"
    assert recovery["validation_overlap_rule"]["max_overlap_min_per_batch"] == 30
    assert config["writeback_rules"]["post_recovery_replay_required"] is True
    assert config["selected_queue_policy"]["runtime_recovery_override"]["preserve_replanned_order"] is True
    assert not report.issues


def test_recovery_strategy_writeback_agent_holds_safe_fraction_when_target_not_feasible() -> None:
    report = RecoveryStrategyWritebackAgent(
        time_budget_recovery_metrics=_metrics(
            selected={
                "candidate_id": "hold_safe_fraction",
                "stable": True,
                "target_recovery": False,
                "target_intake_fraction": 0.6,
                "actual_throughput_fraction": 0.625,
                "time_budget_usage": 0.799,
                "validation_staff_usage": 0.337,
                "queue_policy": "source_order",
            }
        ),
        previous_baseline=_baseline(),
        baseline_version="baseline_v1_replan",
    ).run([])

    updated = report.metrics["recovery_strategy_baseline"]
    config = updated["online_control_config"]

    assert updated["writeback_decision"]["writeback_mode"] == "hold_safe_recovery_fraction"
    assert config["load_control_policy"]["protected_intake_fraction"] == 0.6
    assert config["recovery_control_policy"]["enabled"] is False
    assert report.issues[0].issue_type == "target_recovery_not_written"


def test_recovery_strategy_writeback_agent_flags_queue_reordering_strategy() -> None:
    report = RecoveryStrategyWritebackAgent(
        time_budget_recovery_metrics=_metrics(
            selected={
                "candidate_id": "time_smoothed_queue",
                "stable": True,
                "target_recovery": True,
                "target_intake_fraction": 0.75,
                "actual_throughput_fraction": 0.75,
                "time_budget_usage": 0.628,
                "validation_staff_usage": 0.337,
                "queue_policy": "short_elapsed_first",
            }
        ),
        previous_baseline=_baseline(),
        baseline_version="baseline_v1_replan",
    ).run([])

    issue_types = {issue.issue_type for issue in report.issues}
    override = report.metrics["recovery_strategy_baseline"]["online_control_config"]["selected_queue_policy"][
        "runtime_recovery_override"
    ]

    assert "queue_reordering_requires_wait_limit" in issue_types
    assert override["preserve_replanned_order"] is False


def _metrics(*, selected: dict[str, object]) -> dict[str, object]:
    return {
        "strategy_verdict": "target_recovery_feasible",
        "target_intake_fraction": 0.75,
        "safe_intake_fraction": 0.6,
        "selected_candidate": selected,
    }


def _baseline() -> dict[str, object]:
    return {
        "selected_queue_policy": {"policy_id": "high_risk_first"},
        "selected_portfolio": {"package_id": "resilience_bridge_portfolio"},
        "budget_sequence": [{"order": 1, "budget_item": "外包低价值验证"}],
        "load_control_policy": {
            "protected_intake_fraction": 0.45,
            "normalization_rule": "连续两个 campaign 稳定后恢复。",
        },
        "guardrails": {"mandatory_replan_thresholds": ["阶段验收失败"]},
        "writeback_rules": {
            "stable_campaigns_required_for_ramp": 2,
            "ramp_step": 0.15,
        },
    }
