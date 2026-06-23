from water_ai.agents.timestamped_campaign_replay_agent import TimestampedCampaignReplayAgent


def test_timestamped_campaign_replay_requires_field_data_before_calibration() -> None:
    report = TimestampedCampaignReplayAgent(
        datasets=_timestamped_package(),
        data_origin="synthetic",
        minimum_proxy_events=3,
    ).run([])

    readiness = report.metrics["readiness"]
    metrics = report.metrics["replay_metrics"]

    assert readiness["timestamped_replay_status"] == "synthetic_timestamp_schema_ready_needs_field_replay"
    assert readiness["can_calibrate_fast_proxy"] is False
    assert metrics["proxy_precision"] == 1.0
    assert metrics["proxy_recall"] == 1.0
    assert metrics["pressure_headloss_event_count"] == 3
    assert report.metrics["linkage"]["pressure_headloss_batch_count"] == 3
    assert any(issue.issue_type == "field_timestamped_replay_required" for issue in report.issues)


def test_timestamped_campaign_replay_accepts_field_replay_when_proxy_labels_are_sufficient() -> None:
    report = TimestampedCampaignReplayAgent(
        datasets=_timestamped_package(),
        data_origin="field",
        minimum_proxy_events=3,
    ).run([])

    readiness = report.metrics["readiness"]

    assert readiness["timestamped_replay_status"] == "field_timestamped_replay_ready_for_fast_proxy_calibration"
    assert readiness["can_calibrate_fast_proxy"] is True
    assert readiness["can_write_to_protective_control"] is True
    assert report.issues == []


def test_timestamped_campaign_replay_blocks_missing_result_times() -> None:
    package = _timestamped_package()
    package["offline_lab_results"][0].pop("result_time_min")

    report = TimestampedCampaignReplayAgent(
        datasets=package,
        data_origin="field",
        minimum_proxy_events=3,
    ).run([])

    readiness = report.metrics["readiness"]

    assert readiness["timestamped_replay_status"] == "field_timestamped_replay_schema_blocked"
    assert readiness["can_calibrate_fast_proxy"] is False
    assert report.metrics["table_audit"]["offline_lab_results"]["status"] == "schema_incomplete"


def test_timestamped_campaign_replay_detects_failed_proxy_validation() -> None:
    package = _timestamped_package()
    package["fast_proxy_event_log"].append(
        _proxy_event("B004", event_time=10, label_time=95, triggered=True, label=False, cost=0.3)
    )
    package["sensor_timeseries"].append(_sensor("B004", 0))
    package["offline_lab_results"].append(_lab("B004", 15, 95))
    package["campaign_operation_log"].append(_operation("B004", "switch_or_pretreat", 10, 16, 20, 40))

    report = TimestampedCampaignReplayAgent(
        datasets=package,
        data_origin="field",
        minimum_proxy_events=3,
    ).run([])

    readiness = report.metrics["readiness"]
    metrics = report.metrics["replay_metrics"]

    assert readiness["timestamped_replay_status"] == "field_fast_proxy_validation_failed"
    assert metrics["proxy_precision"] < 0.82


def test_timestamped_campaign_replay_schema_covers_r4b_guardrail_fields() -> None:
    contract = TimestampedCampaignReplayAgent.replay_schema_contract()
    schema_fields = {
        field
        for spec in contract.values()
        for field in list(spec["required_fields"]) + list(spec.get("optional_fields", []))
    }
    headers = TimestampedCampaignReplayAgent.template_headers()

    assert {
        "proxy_holdout_label",
        "regeneration_event",
        "tank_storage_margin",
        "actuator_latency_p90",
        "pump_valve_result",
        "hold_time_min",
    }.issubset(schema_fields)
    assert "flow_Lmin" in headers["sensor_timeseries"]


def test_timestamped_campaign_replay_schema_covers_r8e_pressure_headloss_replay_fields() -> None:
    contract = TimestampedCampaignReplayAgent.replay_schema_contract()
    schema_fields = {
        field
        for spec in contract.values()
        for field in list(spec["required_fields"]) + list(spec.get("optional_fields", []))
    }

    assert "pressure_headloss_event_log" in contract
    assert {
        "pressure_drop_kPa",
        "headloss_kPa_per_m",
        "flow_normalized_pressure_residual",
        "matched_lab_sample_time_min",
        "hydraulic_anomaly_label",
        "pressure_headloss_proxy_label",
    }.issubset(schema_fields)


def test_timestamped_campaign_replay_blocks_pressure_headloss_events_without_lab_anchor() -> None:
    package = _timestamped_package()
    package["pressure_headloss_event_log"].append(_pressure_event("B999", event_time=18, matched_sample=15, anomaly=True))

    report = TimestampedCampaignReplayAgent(
        datasets=package,
        data_origin="field",
        minimum_proxy_events=3,
    ).run([])

    readiness = report.metrics["readiness"]
    linkage = report.metrics["linkage"]

    assert readiness["timestamped_replay_status"] == "field_timestamped_replay_schema_blocked"
    assert "B999" in linkage["pressure_headloss_without_lab_batches"]
    assert any(issue.issue_type == "pressure_headloss_event_without_lab_anchor" for issue in report.issues)


def _timestamped_package() -> dict[str, list[dict[str, object]]]:
    return {
        "sensor_timeseries": [_sensor("B001", 0), _sensor("B002", 0), _sensor("B003", 0)],
        "offline_lab_results": [_lab("B001", 15, 95), _lab("B002", 15, 90), _lab("B003", 15, 100)],
        "campaign_operation_log": [
            _operation("B001", "switch_or_pretreat", 10, 16, 20, 42),
            _operation("B002", "switch_or_pretreat", 12, 18, 22, 44),
            _operation("B003", "hold_for_validation", 12, 15, 15, 90),
        ],
        "pressure_headloss_event_log": [
            _pressure_event("B001", event_time=18, matched_sample=15, anomaly=False),
            _pressure_event("B002", event_time=20, matched_sample=15, anomaly=True),
            _pressure_event("B003", event_time=30, matched_sample=15, anomaly=False),
        ],
        "fast_proxy_event_log": [
            _proxy_event("B001", event_time=10, label_time=95, triggered=True, label=True, cost=0.0),
            _proxy_event("B002", event_time=12, label_time=90, triggered=True, label=True, cost=0.0),
            _proxy_event("B003", event_time=12, label_time=100, triggered=False, label=False, cost=0.0),
        ],
    }


def _sensor(batch_id: str, timestamp: int) -> dict[str, object]:
    return {
        "batch_id": batch_id,
        "timestamp_min": timestamp,
        "EC_uScm": 3000.0,
        "turbidity_NTU": 40.0,
        "UV254_abs": 0.86,
        "pH": 7.8,
        "ORP_mV": 510.0,
        "pressure_drop_kPa": 4.1,
        "headloss_kPa_per_m": 5.2,
    }


def _lab(batch_id: str, sample_time: int, result_time: int) -> dict[str, object]:
    return {
        "batch_id": batch_id,
        "sample_time_min": sample_time,
        "result_time_min": result_time,
        "analyte": "matrix_shock_label",
        "value": 1.0,
        "qa_flag": "pass",
    }


def _operation(batch_id: str, action_id: str, command: int, effect: int, start: int, end: int) -> dict[str, object]:
    return {
        "campaign_id": "C001",
        "batch_id": batch_id,
        "action_id": action_id,
        "command_time_min": command,
        "effect_time_min": effect,
        "start_min": start,
        "end_min": end,
        "release_policy": "block_release_until_lab_and_field_conformal_calibration",
    }


def _proxy_event(batch_id: str, *, event_time: int, label_time: int, triggered: bool, label: bool, cost: float) -> dict[str, object]:
    return {
        "campaign_id": "C001",
        "batch_id": batch_id,
        "event_time_min": event_time,
        "proxy_score": 0.7 if triggered else 0.1,
        "specificity_guard_score": 0.65 if triggered else 0.1,
        "protective_triggered": triggered,
        "triggered_action_id": "switch_or_pretreat" if triggered else "none",
        "field_label_matrix_shock": label,
        "lab_label_time_min": label_time,
        "false_positive_cost_index": cost,
    }


def _pressure_event(batch_id: str, *, event_time: int, matched_sample: int, anomaly: bool) -> dict[str, object]:
    return {
        "campaign_id": "C001",
        "batch_id": batch_id,
        "event_time_min": event_time,
        "bed_id": "BED_A",
        "pressure_drop_kPa": 6.8 if anomaly else 4.2,
        "headloss_kPa_per_m": 8.5 if anomaly else 5.1,
        "flow_Lmin": 1.2,
        "matched_lab_sample_time_min": matched_sample,
        "regeneration_event": anomaly,
        "hydraulic_anomaly_label": anomaly,
        "flow_normalized_pressure_residual": 0.42 if anomaly else 0.08,
    }
