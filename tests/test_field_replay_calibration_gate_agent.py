from water_ai.agents.field_replay_calibration_gate_agent import FieldReplayCalibrationGateAgent
from water_ai.agents.timestamped_campaign_replay_agent import TimestampedCampaignReplayAgent


def test_field_replay_calibration_gate_blocks_synthetic_replay() -> None:
    replay_report = TimestampedCampaignReplayAgent(
        datasets=_timestamped_package(),
        data_origin="synthetic",
        minimum_proxy_events=3,
    ).run([])

    report = FieldReplayCalibrationGateAgent(
        timestamped_replay_report=replay_report,
        matrix_fast_proxy_metrics=_matrix_fast_proxy_metrics(),
        minimum_proxy_events=3,
    ).run([])

    readiness = report.metrics["readiness"]

    assert readiness["field_replay_gate_status"] == "synthetic_replay_gate_blocked"
    assert readiness["can_write_to_protective_control"] is False
    assert readiness["can_write_to_release_gate"] is False
    assert "G6_1_field_origin" in readiness["failed_gate_ids"]
    assert any(issue.issue_type == "G6_1_field_origin" for issue in report.issues)


def test_field_replay_calibration_gate_allows_only_protective_writeback_when_field_replay_passes() -> None:
    replay_report = TimestampedCampaignReplayAgent(
        datasets=_timestamped_package(),
        data_origin="field",
        minimum_proxy_events=3,
    ).run([])

    report = FieldReplayCalibrationGateAgent(
        timestamped_replay_report=replay_report,
        matrix_fast_proxy_metrics=_matrix_fast_proxy_metrics(),
        minimum_proxy_events=3,
    ).run([])

    readiness = report.metrics["readiness"]
    writeback = report.metrics["writeback_policy"]

    assert readiness["field_replay_gate_status"] == "field_fast_proxy_protective_control_gate_ready"
    assert readiness["failed_gate_ids"] == []
    assert writeback["can_write_to_protective_control"] is True
    assert writeback["can_write_to_release_gate"] is False
    assert writeback["release_policy"] == "block_release_until_lab_and_field_conformal_calibration"
    assert report.issues == []


def test_field_replay_calibration_gate_fails_low_precision_and_false_positive_cost() -> None:
    package = _timestamped_package()
    package["fast_proxy_event_log"].append(
        _proxy_event("B004", event_time=10, label_time=95, triggered=True, label=False, cost=0.4)
    )
    package["sensor_timeseries"].append(_sensor("B004", 0))
    package["offline_lab_results"].append(_lab("B004", 15, 95))
    package["campaign_operation_log"].append(_operation("B004", "switch_or_pretreat", 10, 16, 20, 40))
    package["pressure_headloss_event_log"].append(_pressure_event("B004", event_time=18, sample_time=15, anomaly=True))
    replay_report = TimestampedCampaignReplayAgent(
        datasets=package,
        data_origin="field",
        minimum_proxy_events=3,
    ).run([])

    report = FieldReplayCalibrationGateAgent(
        timestamped_replay_report=replay_report,
        matrix_fast_proxy_metrics=_matrix_fast_proxy_metrics(),
        minimum_proxy_events=3,
    ).run([])

    readiness = report.metrics["readiness"]

    assert readiness["field_replay_gate_status"] == "field_fast_proxy_calibration_gate_failed"
    assert "G6_5_proxy_precision_recall" in readiness["failed_gate_ids"]
    assert "G6_7_false_positive_cost" in readiness["failed_gate_ids"]
    assert readiness["can_write_to_protective_control"] is False


def test_field_replay_calibration_gate_fails_missing_result_time_as_schema_gate() -> None:
    package = _timestamped_package()
    package["offline_lab_results"][0].pop("result_time_min")
    replay_report = TimestampedCampaignReplayAgent(
        datasets=package,
        data_origin="field",
        minimum_proxy_events=3,
    ).run([])

    report = FieldReplayCalibrationGateAgent(
        timestamped_replay_report=replay_report,
        matrix_fast_proxy_metrics=_matrix_fast_proxy_metrics(),
        minimum_proxy_events=3,
    ).run([])

    readiness = report.metrics["readiness"]

    assert readiness["field_replay_gate_status"] == "field_replay_schema_gate_failed"
    assert "G6_2_timestamp_schema_ready" in readiness["failed_gate_ids"]
    assert "G6_2_timestamp_schema_ready" in report.metrics["gate_results"]["blocking_gate_ids"]


def test_field_replay_calibration_gate_fails_when_protective_action_is_too_slow() -> None:
    package = _timestamped_package()
    for row in package["campaign_operation_log"]:
        row["effect_time_min"] = row["command_time_min"] + 28
    replay_report = TimestampedCampaignReplayAgent(
        datasets=package,
        data_origin="field",
        minimum_proxy_events=3,
    ).run([])

    report = FieldReplayCalibrationGateAgent(
        timestamped_replay_report=replay_report,
        matrix_fast_proxy_metrics=_matrix_fast_proxy_metrics(),
        minimum_proxy_events=3,
    ).run([])

    readiness = report.metrics["readiness"]

    assert readiness["field_replay_gate_status"] == "field_fast_proxy_calibration_gate_failed"
    assert "G6_6_latency_action_margin" in readiness["failed_gate_ids"]
    assert readiness["can_write_to_protective_control"] is False


def _timestamped_package() -> dict[str, list[dict[str, object]]]:
    return {
        "sensor_timeseries": [_sensor("B001", 0), _sensor("B002", 0), _sensor("B003", 0)],
        "offline_lab_results": [_lab("B001", 15, 95), _lab("B002", 15, 90), _lab("B003", 15, 100)],
        "campaign_operation_log": [
            _operation("B001", "switch_or_pretreat", 10, 16, 20, 42),
            _operation("B002", "switch_or_pretreat", 12, 18, 22, 44),
            _operation("B003", "hold_for_validation", 12, 15, 15, 90),
        ],
        "fast_proxy_event_log": [
            _proxy_event("B001", event_time=10, label_time=95, triggered=True, label=True, cost=0.0),
            _proxy_event("B002", event_time=12, label_time=90, triggered=True, label=True, cost=0.0),
            _proxy_event("B003", event_time=12, label_time=100, triggered=False, label=False, cost=0.0),
        ],
        "pressure_headloss_event_log": [
            _pressure_event("B001", event_time=18, sample_time=15, anomaly=True),
            _pressure_event("B002", event_time=20, sample_time=15, anomaly=False),
            _pressure_event("B003", event_time=22, sample_time=15, anomaly=False),
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


def _pressure_event(batch_id: str, *, event_time: int, sample_time: int, anomaly: bool) -> dict[str, object]:
    return {
        "campaign_id": "C001",
        "batch_id": batch_id,
        "event_time_min": event_time,
        "bed_id": "N3_catalyst_bed",
        "pressure_drop_kPa": 6.8 if anomaly else 4.1,
        "headloss_kPa_per_m": 0.34 if anomaly else 0.22,
        "flow_Lmin": 1.2,
        "matched_lab_sample_time_min": sample_time,
        "regeneration_event": False,
        "hydraulic_anomaly_label": anomaly,
        "flow_normalized_pressure_residual": 0.18 if anomaly else 0.02,
        "expected_clean_bed_pressure_drop_kPa": 3.2,
        "operator_review_required": anomaly,
    }


def _matrix_fast_proxy_metrics() -> dict[str, object]:
    return {
        "readiness": {
            "can_write_to_protective_control": False,
            "can_write_to_release_gate": False,
            "release_gate_block_reason": "fast proxy can trigger protection, but release still requires lab evidence",
        }
    }
