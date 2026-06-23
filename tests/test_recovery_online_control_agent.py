from water_ai.agents.recovery_online_control_agent import RecoveryOnlineControlAgent


def test_recovery_online_control_agent_maintains_validated_recovery() -> None:
    report = RecoveryOnlineControlAgent(
        recovery_execution_metrics=_execution_metrics(stable=True),
        recovery_baseline=_baseline(),
    ).run([])

    adjusted = report.metrics["adjusted_control_state"]
    update = report.metrics["recovery_campaign_update"]

    assert adjusted["recovery_control_mode"] == "maintain_conditional_recovery"
    assert adjusted["next_intake_fraction"] == 0.75
    assert adjusted["replan_required"] is False
    assert update["acceptance_passed"] is True
    assert update["recovery_policy_applied"] is True
    assert not report.issues


def test_recovery_online_control_agent_falls_back_on_replay_failure() -> None:
    report = RecoveryOnlineControlAgent(
        recovery_execution_metrics=_execution_metrics(stable=False),
        recovery_baseline=_baseline(),
    ).run([])

    adjusted = report.metrics["adjusted_control_state"]
    update = report.metrics["recovery_campaign_update"]

    assert adjusted["recovery_control_mode"] == "fallback_to_safe_fraction"
    assert adjusted["next_intake_fraction"] == 0.6
    assert adjusted["replan_required"] is True
    assert "恢复执行回放触发 fallback trigger" in adjusted["replan_reasons"]
    assert update["acceptance_passed"] is False
    assert report.issues[0].issue_type == "recovery_online_replan_required"


def test_recovery_online_control_agent_preserves_base_online_state() -> None:
    report = RecoveryOnlineControlAgent(
        recovery_execution_metrics=_execution_metrics(stable=True),
        recovery_baseline=_baseline(),
    ).run([])

    adjusted = report.metrics["adjusted_control_state"]

    assert adjusted["base_online_state"]["project_mode"] == "steady_monitoring"
    assert adjusted["target_intake_fraction"] == 0.75
    assert adjusted["fallback_intake_fraction"] == 0.6


def _execution_metrics(*, stable: bool) -> dict[str, object]:
    bottlenecks = [] if stable else ["campaign_time_budget"]
    time_usage = 0.884 if stable else 0.94
    return {
        "with_recovery_strategy": {
            "apply_recovery_policy": True,
            "admitted_batch_count": 6,
            "scenario_sequence": ["matrix_shock", "catalyst_deactivation"],
            "bottleneck_ids": bottlenecks,
            "schedule": {"operating_mode": "normal_intake" if stable else "staggered_intake"},
            "campaign_metrics": {
                "success_rate": 1.0,
                "validation_staff_usage": 0.394,
                "time_budget_usage": time_usage,
                "catalyst_spares_remaining": 3,
                "oxidant_stock_units_remaining": 3.5,
            },
        },
        "comparison": {
            "replay_verdict": "recovery_execution_validated" if stable else "fallback_required",
            "strategy_stable": stable,
            "fallback_required": not stable,
            "target_intake_fraction": 0.75,
            "fallback_intake_fraction": 0.6,
            "strategy_bottleneck_ids": bottlenecks,
            "validation_usage_with_strategy": 0.394,
            "time_usage_with_strategy": time_usage,
            "admitted_batch_count": 6,
        },
    }


def _baseline() -> dict[str, object]:
    return {
        "online_control_config": {
            "selected_portfolio": {"package_id": "resilience_bridge_portfolio"},
            "budget_sequence": [
                {"order": 1, "budget_item": "外包低价值验证"},
                {"order": 2, "budget_item": "验证能力批复"},
            ],
            "load_control_policy": {
                "protected_intake_fraction": 0.75,
                "fallback_intake_fraction": 0.6,
            },
            "recovery_control_policy": {
                "policy_id": "recovery_strategy_v1",
                "target_intake_fraction": 0.75,
                "fallback_intake_fraction": 0.6,
            },
        }
    }
