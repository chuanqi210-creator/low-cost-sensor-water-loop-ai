from water_ai.agents.campaign_telemetry_agent import CampaignTelemetryAgent


def test_campaign_telemetry_agent_builds_rolling_updates_from_records() -> None:
    report = CampaignTelemetryAgent(
        batch_records=[
            _record(0, "matrix_shock", validation_minutes=140, elapsed_min=220),
            _record(1, "catalyst_deactivation", validation_minutes=150, elapsed_min=240),
            _record(2, "oxidant_limitation", validation_minutes=90, elapsed_min=180),
        ],
        update_cut_points=[1, 3],
        initial_catalyst_spares=1,
        initial_oxidant_stock_units=2.2,
        validation_staff_hours_capacity=4.0,
        campaign_time_budget_min=720,
    ).run([])

    updates = report.metrics["rolling_campaign_updates"]

    assert len(updates) == 2
    assert updates[-1]["success_rate"] == 1.0
    assert updates[-1]["validation_staff_usage"] > updates[0]["validation_staff_usage"]
    assert "validation_capacity" in updates[-1]["bottleneck_ids"]
    assert updates[-1]["intake_pressure_multiplier"] > 1.0


def test_campaign_telemetry_agent_applies_budget_release_plan() -> None:
    report = CampaignTelemetryAgent(
        batch_records=[_record(0, "sensor_faults", validation_minutes=30, elapsed_min=90)],
        budget_release_plan={
            0: {
                "budget_release_fraction": 0.65,
                "budget_released_items": ["外包低价值验证"],
            }
        },
    ).run([])

    update = report.metrics["rolling_campaign_updates"][0]

    assert update["budget_release_fraction"] == 0.65
    assert update["budget_released_items"] == ["外包低价值验证"]


def test_campaign_telemetry_agent_marks_acceptance_failed_on_low_success_rate() -> None:
    report = CampaignTelemetryAgent(
        batch_records=[
            {
                **_record(0, "matrix_shock", validation_minutes=50, elapsed_min=120),
                "success": False,
            }
        ],
    ).run([])

    update = report.metrics["latest_update"]

    assert update["acceptance_passed"] is False
    assert report.issues


def _record(batch_id: int, scenario: str, *, validation_minutes: int, elapsed_min: int) -> dict[str, object]:
    return {
        "batch_id": batch_id,
        "scenario": scenario,
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
