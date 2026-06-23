from water_ai.agents.recovery_execution_replay_agent import RecoveryExecutionReplayAgent


def test_recovery_execution_replay_agent_validates_written_strategy() -> None:
    records = [
        _record("matrix_shock", validation_minutes=53, elapsed_min=126),
        _record("catalyst_deactivation", validation_minutes=0, elapsed_min=88),
        _record("matrix_shock", validation_minutes=73, elapsed_min=146),
        _record("catalyst_deactivation", validation_minutes=146, elapsed_min=365),
        _record("oxidant_limitation", validation_minutes=0, elapsed_min=42),
        _record("oxidant_limitation", validation_minutes=46, elapsed_min=172),
        _record("sensor_faults", validation_minutes=73, elapsed_min=99),
        _record("reaction_time_insufficient", validation_minutes=73, elapsed_min=102),
    ]

    report = RecoveryExecutionReplayAgent(
        source_records=records,
        recovery_baseline=_baseline(),
        catalyst_spares_remaining=0,
        oxidant_stock_units_remaining=1.5,
        validation_staff_hours_capacity=5.5,
        campaign_time_budget_min=960,
    ).run([])

    comparison = report.metrics["comparison"]

    assert comparison["replay_verdict"] == "recovery_execution_validated"
    assert comparison["time_usage_without_strategy"] >= 0.90
    assert comparison["time_usage_with_strategy"] == 0.884
    assert comparison["recommended_next_intake_fraction"] == 0.75
    assert comparison["strategy_bottleneck_ids"] == []
    assert not report.issues


def test_recovery_execution_replay_agent_triggers_fallback_when_time_still_high() -> None:
    records = [
        _record("matrix_shock", validation_minutes=53, elapsed_min=180),
        _record("catalyst_deactivation", validation_minutes=0, elapsed_min=160),
        _record("matrix_shock", validation_minutes=73, elapsed_min=200),
        _record("catalyst_deactivation", validation_minutes=146, elapsed_min=420),
        _record("oxidant_limitation", validation_minutes=0, elapsed_min=80),
        _record("oxidant_limitation", validation_minutes=46, elapsed_min=220),
        _record("sensor_faults", validation_minutes=73, elapsed_min=99),
        _record("reaction_time_insufficient", validation_minutes=73, elapsed_min=102),
    ]

    report = RecoveryExecutionReplayAgent(
        source_records=records,
        recovery_baseline=_baseline(),
        catalyst_spares_remaining=0,
        oxidant_stock_units_remaining=1.5,
        validation_staff_hours_capacity=5.5,
        campaign_time_budget_min=960,
    ).run([])

    comparison = report.metrics["comparison"]

    assert comparison["replay_verdict"] == "fallback_required"
    assert comparison["fallback_required"] is True
    assert comparison["recommended_next_intake_fraction"] == 0.6
    assert "campaign_time_budget" in comparison["strategy_bottleneck_ids"]
    assert report.issues[0].issue_type == "recovery_fallback_triggered"


def test_recovery_execution_replay_agent_uses_fallback_when_policy_disabled() -> None:
    baseline = _baseline()
    policy = baseline["online_control_config"]["recovery_control_policy"]
    policy["enabled"] = False
    policy["target_intake_fraction"] = 0.6
    baseline["online_control_config"]["load_control_policy"]["protected_intake_fraction"] = 0.6

    report = RecoveryExecutionReplayAgent(
        source_records=[_record("matrix_shock", validation_minutes=40, elapsed_min=120) for _ in range(8)],
        recovery_baseline=baseline,
        catalyst_spares_remaining=0,
        oxidant_stock_units_remaining=1.5,
        validation_staff_hours_capacity=5.5,
        campaign_time_budget_min=960,
    ).run([])

    with_strategy = report.metrics["with_recovery_strategy"]

    assert with_strategy["target_intake_fraction"] == 0.6
    assert with_strategy["actual_throughput_fraction"] == 0.625


def _baseline() -> dict[str, object]:
    return {
        "baseline_version": "baseline_v1_replan_recovery",
        "online_control_config": {
            "budget_sequence": [
                {"order": 1, "budget_item": "外包低价值验证"},
                {"order": 2, "budget_item": "催化剂备用供应商"},
                {"order": 3, "budget_item": "验证能力批复"},
                {"order": 4, "budget_item": "催化剂库存批复"},
                {"order": 5, "budget_item": "氧化剂库存批复"},
            ],
            "load_control_policy": {
                "protected_intake_fraction": 0.75,
                "fallback_intake_fraction": 0.6,
            },
            "recovery_control_policy": {
                "enabled": True,
                "selected_candidate_id": "stagger_validation_overlap",
                "target_intake_fraction": 0.75,
                "fallback_intake_fraction": 0.6,
                "expected_time_budget_usage": 0.884,
                "queue_policy": "source_order",
                "validation_overlap_rule": {
                    "overlap_fraction_of_validation_minutes": 0.35,
                    "max_overlap_min_per_batch": 30,
                },
            },
        },
    }


def _record(scenario: str, *, validation_minutes: int, elapsed_min: int) -> dict[str, object]:
    return {
        "scenario": scenario,
        "success": True,
        "elapsed_min": elapsed_min,
        "cumulative_cost": 1.0,
        "cumulative_energy": 0.4,
        "validation_minutes": validation_minutes,
        "regeneration_count": 1,
        "replacement_count": 0,
        "oxidant_dose_count": 1,
        "catalyst_lifetime_fraction_end": 0.70,
        "catalyst_activity_end": 0.74,
    }
