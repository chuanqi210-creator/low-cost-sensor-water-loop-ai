from water_ai.agents.field_replay_evidence_chain_agent import FieldReplayEvidenceChainAgent
from water_ai.agents.field_replay_import_agent import FieldReplayImportAgent


def test_evidence_chain_blocks_synthetic_import_before_replay() -> None:
    import_report = FieldReplayImportAgent(
        metadata=_metadata("synthetic"),
        raw_tables=_raw_package(),
    ).run([])

    report = FieldReplayEvidenceChainAgent(
        import_report=import_report,
        matrix_fast_proxy_metrics=_matrix_fast_proxy_metrics(),
        minimum_proxy_events=3,
    ).run([])

    readiness = report.metrics["readiness"]
    writeback = report.metrics["writeback_candidate"]

    assert readiness["field_replay_evidence_chain_status"] == "field_replay_evidence_chain_blocked_at_import"
    assert report.metrics["timestamped_replay_stage"]["stage_status"] == "not_run"
    assert report.metrics["g6_stage"]["stage_status"] == "not_run"
    assert writeback["can_emit_protective_writeback_candidate"] is False
    assert any(issue.issue_type == "import_gate_not_passed" for issue in report.issues)


def test_evidence_chain_requires_agent44_import_gate() -> None:
    report = FieldReplayEvidenceChainAgent(
        matrix_fast_proxy_metrics=_matrix_fast_proxy_metrics(),
        minimum_proxy_events=3,
    ).run([])

    readiness = report.metrics["readiness"]

    assert readiness["field_replay_evidence_chain_status"] == "field_replay_evidence_chain_blocked_at_import"
    assert "missing_import_report" in report.metrics["import_stage"]["blocking_reasons"]
    assert readiness["can_emit_protective_writeback_candidate"] is False


def test_evidence_chain_emits_only_protective_candidate_when_all_gates_pass() -> None:
    import_report = FieldReplayImportAgent(
        metadata=_metadata("field"),
        raw_tables=_raw_package(),
    ).run([])

    report = FieldReplayEvidenceChainAgent(
        import_report=import_report,
        matrix_fast_proxy_metrics=_matrix_fast_proxy_metrics(),
        minimum_proxy_events=3,
    ).run([])

    readiness = report.metrics["readiness"]
    writeback = report.metrics["writeback_candidate"]

    assert readiness["field_replay_evidence_chain_status"] == "field_replay_protective_writeback_candidate_ready"
    assert readiness["import_ready"] is True
    assert readiness["timestamped_replay_ready"] is True
    assert readiness["g6_ready"] is True
    assert writeback["can_emit_protective_writeback_candidate"] is True
    assert writeback["can_write_to_release_gate"] is False
    assert writeback["requires_human_review_before_application"] is True
    assert report.issues == []


def test_evidence_chain_blocks_at_g6_when_fast_proxy_validation_fails() -> None:
    raw_tables = _raw_package()
    raw_tables["fast_proxy_event_log"].append(
        _proxy_event("B004", "10", "95", "true", "false", "0.4")
    )
    raw_tables["sensor_timeseries"].append(_sensor("B004", "0"))
    raw_tables["offline_lab_results"].append(_lab("B004", "15", "95", "0.0"))
    raw_tables["campaign_operation_log"].append(_operation("B004", "switch_or_pretreat", "10", "16", "20", "40"))
    raw_tables["pressure_headloss_event_log"].append(_pressure_event("B004", "18", "15", "true"))
    import_report = FieldReplayImportAgent(
        metadata=_metadata("field"),
        raw_tables=raw_tables,
    ).run([])

    report = FieldReplayEvidenceChainAgent(
        import_report=import_report,
        matrix_fast_proxy_metrics=_matrix_fast_proxy_metrics(),
        minimum_proxy_events=3,
    ).run([])

    readiness = report.metrics["readiness"]
    g6_readiness = report.metrics["g6_stage"]["readiness"]

    assert readiness["field_replay_evidence_chain_status"] == "field_replay_evidence_chain_blocked_at_timestamped_replay"
    assert readiness["can_emit_protective_writeback_candidate"] is False
    assert g6_readiness["can_write_to_protective_control"] is False
    assert "G6_5_proxy_precision_recall" in report.metrics["g6_stage"]["issue_types"]


def test_evidence_chain_preserves_release_gate_boundary_even_with_g6_pass() -> None:
    import_report = FieldReplayImportAgent(
        metadata=_metadata("field"),
        raw_tables=_raw_package(),
    ).run([])

    report = FieldReplayEvidenceChainAgent(
        import_report=import_report,
        matrix_fast_proxy_metrics=_matrix_fast_proxy_metrics(),
        minimum_proxy_events=3,
    ).run([])

    assert report.metrics["readiness"]["can_write_to_release_gate"] is False
    assert report.metrics["writeback_candidate"]["g6_writeback_policy"]["can_write_to_release_gate"] is False


def _metadata(origin: str) -> dict[str, object]:
    return {
        "data_origin": origin,
        "site_id": "field_site_A",
        "campaign_id": "C001",
        "sampling_start": "2026-06-01T08:00:00+08:00",
        "sampling_end": "2026-06-01T12:00:00+08:00",
        "operator_id": "operator_01",
        "instrument_snapshot_id": "low_cost_sensor_bank_v2",
        "chain_of_custody_id": "custody_C001_signed",
    }


def _raw_package() -> dict[str, list[dict[str, object]]]:
    return {
        "sensor_timeseries": [
            _sensor("B001", "0"),
            _sensor("B002", "0"),
            _sensor("B003", "0"),
        ],
        "offline_lab_results": [
            _lab("B001", "15", "95", "1.0"),
            _lab("B002", "15", "90", "1.0"),
            _lab("B003", "15", "100", "0.0"),
        ],
        "campaign_operation_log": [
            _operation("B001", "switch_or_pretreat", "10", "16", "20", "42"),
            _operation("B002", "switch_or_pretreat", "12", "18", "22", "44"),
            _operation("B003", "hold_for_validation", "12", "15", "15", "90"),
        ],
        "fast_proxy_event_log": [
            _proxy_event("B001", "10", "95", "true", "true", "0.0"),
            _proxy_event("B002", "12", "90", "true", "true", "0.0"),
            _proxy_event("B003", "12", "100", "false", "false", "0.0"),
        ],
        "pressure_headloss_event_log": [
            _pressure_event("B001", "18", "15", "true"),
            _pressure_event("B002", "20", "15", "false"),
            _pressure_event("B003", "22", "15", "false"),
        ],
    }


def _sensor(batch_id: str, timestamp: str) -> dict[str, object]:
    return {
        "batch_id": batch_id,
        "timestamp_min": timestamp,
        "EC_uScm": "3000.0",
        "turbidity_NTU": "40.0",
        "UV254_abs": "0.86",
        "pH": "7.8",
        "ORP_mV": "510.0",
    }


def _lab(batch_id: str, sample_time: str, result_time: str, value: str) -> dict[str, object]:
    return {
        "batch_id": batch_id,
        "sample_time_min": sample_time,
        "result_time_min": result_time,
        "analyte": "matrix_shock_label",
        "value": value,
        "qa_flag": "pass",
    }


def _operation(batch_id: str, action_id: str, command: str, effect: str, start: str, end: str) -> dict[str, object]:
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


def _proxy_event(batch_id: str, event_time: str, label_time: str, triggered: str, label: str, cost: str) -> dict[str, object]:
    return {
        "campaign_id": "C001",
        "batch_id": batch_id,
        "event_time_min": event_time,
        "proxy_score": "0.88",
        "specificity_guard_score": "0.83",
        "protective_triggered": triggered,
        "triggered_action_id": "switch_or_pretreat" if triggered == "true" else "none",
        "field_label_matrix_shock": label,
        "lab_label_time_min": label_time,
        "false_positive_cost_index": cost,
    }


def _pressure_event(batch_id: str, event_time: str, sample_time: str, anomaly: str) -> dict[str, object]:
    return {
        "campaign_id": "C001",
        "batch_id": batch_id,
        "event_time_min": event_time,
        "bed_id": "N3_catalyst_bed",
        "pressure_drop_kPa": "6.8" if anomaly == "true" else "4.1",
        "headloss_kPa_per_m": "0.34" if anomaly == "true" else "0.22",
        "flow_Lmin": "1.2",
        "matched_lab_sample_time_min": sample_time,
        "regeneration_event": "false",
        "hydraulic_anomaly_label": anomaly,
        "flow_normalized_pressure_residual": "0.18" if anomaly == "true" else "0.02",
        "expected_clean_bed_pressure_drop_kPa": "3.2",
        "operator_review_required": anomaly,
    }


def _matrix_fast_proxy_metrics() -> dict[str, object]:
    return {
        "readiness": {
            "can_write_to_release_gate": False,
        }
    }
