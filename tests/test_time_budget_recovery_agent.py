from water_ai.agents.time_budget_recovery_agent import TimeBudgetRecoveryAgent


def test_time_budget_recovery_agent_selects_validation_overlap_for_target_recovery() -> None:
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

    report = TimeBudgetRecoveryAgent(
        source_records=records,
        recovery_ramp_metrics=_ramp_metrics(safe=0.60, limiting=0.75),
        online_control_config=_baseline(),
        catalyst_spares_remaining=0,
        oxidant_stock_units_remaining=1.5,
        validation_staff_hours_capacity=5.5,
        campaign_time_budget_min=960,
    ).run([])

    selected = report.metrics["selected_candidate"]

    assert report.metrics["strategy_verdict"] == "target_recovery_feasible"
    assert selected["candidate_id"] == "stagger_validation_overlap"
    assert selected["stable"] is True
    assert selected["target_intake_fraction"] == 0.75
    assert selected["time_budget_usage"] < 0.9


def test_time_budget_recovery_agent_uses_extended_window_when_overlap_cannot_help() -> None:
    records = [
        _record("matrix_shock", validation_minutes=0, elapsed_min=155),
        _record("catalyst_deactivation", validation_minutes=0, elapsed_min=155),
        _record("matrix_shock", validation_minutes=0, elapsed_min=155),
        _record("catalyst_deactivation", validation_minutes=0, elapsed_min=155),
        _record("oxidant_limitation", validation_minutes=0, elapsed_min=155),
        _record("oxidant_limitation", validation_minutes=0, elapsed_min=155),
        _record("sensor_faults", validation_minutes=0, elapsed_min=120),
        _record("reaction_time_insufficient", validation_minutes=0, elapsed_min=120),
    ]

    report = TimeBudgetRecoveryAgent(
        source_records=records,
        recovery_ramp_metrics=_ramp_metrics(safe=0.60, limiting=0.75),
        online_control_config=_baseline(),
        catalyst_spares_remaining=0,
        oxidant_stock_units_remaining=1.5,
        validation_staff_hours_capacity=5.5,
        campaign_time_budget_min=960,
    ).run([])

    selected = report.metrics["selected_candidate"]

    assert report.metrics["strategy_verdict"] == "target_recovery_feasible"
    assert selected["candidate_id"] == "extend_campaign_window_120min"
    assert selected["added_campaign_window_min"] == 120
    assert selected["stable"] is True


def test_time_budget_recovery_agent_holds_safe_fraction_when_target_unresolved() -> None:
    records = [
        _record("matrix_shock", validation_minutes=0, elapsed_min=300),
        _record("catalyst_deactivation", validation_minutes=0, elapsed_min=300),
        _record("matrix_shock", validation_minutes=0, elapsed_min=800),
        _record("catalyst_deactivation", validation_minutes=0, elapsed_min=800),
    ]

    report = TimeBudgetRecoveryAgent(
        source_records=records,
        recovery_ramp_metrics=_ramp_metrics(safe=0.50, limiting=0.75),
        online_control_config=_baseline(),
        catalyst_spares_remaining=0,
        oxidant_stock_units_remaining=1.5,
        validation_staff_hours_capacity=5.5,
        campaign_time_budget_min=960,
    ).run([])

    selected = report.metrics["selected_candidate"]

    assert report.metrics["strategy_verdict"] == "hold_safe_fraction"
    assert selected["candidate_id"] == "hold_safe_fraction"
    assert selected["stable"] is True
    assert selected["target_recovery"] is False
    assert report.issues[0].issue_type == "target_recovery_not_feasible"


def _ramp_metrics(*, safe: float, limiting: float) -> dict[str, object]:
    return {
        "final_safe_intake_fraction": safe,
        "limiting_attempted_fraction": limiting,
        "limiting_bottlenecks": ["campaign_time_budget"],
        "ramp_step": 0.15,
    }


def _baseline() -> dict[str, object]:
    return {
        "baseline_version": "baseline_v1_replan",
        "budget_sequence": [
            {"order": 1, "budget_item": "外包低价值验证"},
            {"order": 2, "budget_item": "催化剂备用供应商"},
            {"order": 3, "budget_item": "验证能力批复"},
            {"order": 4, "budget_item": "催化剂库存批复"},
            {"order": 5, "budget_item": "氧化剂库存批复"},
        ],
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
