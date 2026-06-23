from water_ai.agents.recovery_ramp_agent import RecoveryRampAgent


def test_recovery_ramp_agent_validates_two_stable_ramps() -> None:
    report = RecoveryRampAgent(
        source_records=[_record(validation_minutes=60, elapsed_min=120) for _ in range(4)],
        online_control_config=_baseline(intake=0.30),
        catalyst_spares_remaining=0,
        oxidant_stock_units_remaining=0.8,
        validation_staff_hours_capacity=3.0,
        campaign_time_budget_min=720,
        ramp_step=0.25,
        target_stable_campaigns=2,
    ).run([])

    assert report.metrics["ramp_verdict"] == "two_step_ramp_validated"
    assert report.metrics["target_met"] is True
    assert report.metrics["final_safe_intake_fraction"] == 0.8
    assert report.metrics["final_safe_throughput_fraction"] == 1.0
    assert not report.issues


def test_recovery_ramp_agent_holds_when_second_step_returns_time_bottleneck() -> None:
    records = [
        _record(validation_minutes=80, elapsed_min=145),
        _record(validation_minutes=80, elapsed_min=145),
        _record(validation_minutes=80, elapsed_min=145),
        _record(validation_minutes=80, elapsed_min=145),
        _record(validation_minutes=80, elapsed_min=145),
        _record(validation_minutes=80, elapsed_min=170),
        _record(validation_minutes=80, elapsed_min=100),
        _record(validation_minutes=80, elapsed_min=100),
    ]

    report = RecoveryRampAgent(
        source_records=records,
        online_control_config=_baseline(intake=0.45),
        catalyst_spares_remaining=0,
        oxidant_stock_units_remaining=1.0,
        validation_staff_hours_capacity=5.5,
        campaign_time_budget_min=960,
        ramp_step=0.15,
        target_stable_campaigns=2,
    ).run([])

    assert report.metrics["ramp_verdict"] == "partial_ramp_hold"
    assert report.metrics["stable_campaigns_completed"] == 1
    assert report.metrics["final_safe_intake_fraction"] == 0.6
    assert report.metrics["final_safe_throughput_fraction"] == 0.625
    assert report.metrics["limiting_attempted_fraction"] == 0.75
    assert report.metrics["limiting_bottlenecks"] == ["campaign_time_budget"]


def test_recovery_ramp_agent_blocks_immediate_unsafe_recovery() -> None:
    report = RecoveryRampAgent(
        source_records=[_record(validation_minutes=60, elapsed_min=250) for _ in range(4)],
        online_control_config=_baseline(intake=0.50),
        catalyst_spares_remaining=0,
        oxidant_stock_units_remaining=1.0,
        validation_staff_hours_capacity=4.0,
        campaign_time_budget_min=720,
        ramp_step=0.15,
        target_stable_campaigns=2,
    ).run([])

    assert report.metrics["ramp_verdict"] == "hold_protected_intake"
    assert report.metrics["stable_campaigns_completed"] == 0
    assert report.metrics["final_safe_intake_fraction"] == 0.5
    assert "campaign_time_budget" in report.metrics["limiting_bottlenecks"]
    assert report.issues[0].evidence["attempted_intake_fraction"] == 0.65


def _baseline(*, intake: float) -> dict[str, object]:
    return {
        "baseline_version": "baseline_v1_replan",
        "load_control_policy": {"protected_intake_fraction": intake},
        "writeback_rules": {"stable_campaigns_required_for_ramp": 2, "ramp_step": 0.15},
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
        "catalyst_lifetime_fraction_end": 0.62,
        "catalyst_activity_end": 0.72,
    }
