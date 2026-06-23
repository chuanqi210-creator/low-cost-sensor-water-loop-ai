from water_ai.agents.field_calibration_gate_agent import FieldCalibrationGateAgent


def test_field_calibration_gate_agent_waits_for_real_field_data() -> None:
    report = FieldCalibrationGateAgent(
        field_data_metrics=_field_metrics(data_origin="synthetic"),
        latest_regression="141 passed",
    ).run([])

    readiness = report.metrics["readiness"]

    assert readiness["calibration_gate_status"] == "calibration_protocol_ready_waiting_for_field_data"
    assert readiness["accepted_gate_count"] == 5
    assert readiness["total_gate_count"] == 6
    assert readiness["blocking_gates"] == ["G0_data_origin"]
    assert any(issue.issue_type == "field_data_required_before_calibration" for issue in report.issues)


def test_field_calibration_gate_agent_allows_field_calibration_when_gates_pass() -> None:
    report = FieldCalibrationGateAgent(
        field_data_metrics=_field_metrics(data_origin="field"),
        latest_regression="141 passed",
    ).run([])

    readiness = report.metrics["readiness"]
    gates = {gate["gate_id"]: gate for gate in report.metrics["acceptance_gates"]}

    assert readiness["calibration_gate_status"] == "field_calibration_can_start"
    assert readiness["accepted_gate_count"] == 6
    assert gates["G2_lab_label_alignment"]["gate_ready"] is True
    assert report.issues == []


def test_field_calibration_gate_agent_blocks_on_incomplete_tables() -> None:
    metrics = _field_metrics(data_origin="field")
    metrics["table_statuses"]["offline_lab_results"]["status"] = "schema_incomplete"

    report = FieldCalibrationGateAgent(
        field_data_metrics=metrics,
        latest_regression="141 passed",
    ).run([])

    readiness = report.metrics["readiness"]
    gates = {gate["gate_id"]: gate for gate in report.metrics["acceptance_gates"]}

    assert readiness["calibration_gate_status"] == "field_package_needs_gate_fixes"
    assert "G2_lab_label_alignment" in readiness["blocking_gates"]
    assert gates["G2_lab_label_alignment"]["blockers"] == ["offline_lab_results:schema_incomplete"]
    assert any(issue.issue_type == "field_package_needs_gate_fixes" for issue in report.issues)


def _field_metrics(*, data_origin: str) -> dict[str, object]:
    return {
        "data_origin": data_origin,
        "readiness": {
            "interface_status": "field_calibration_ready" if data_origin == "field" else "template_ready_not_field_validated",
            "field_coverage": 1.0,
            "volume_coverage": 1.0,
            "linkage_score": 1.0,
            "calibration_readiness_score": 1.0,
            "data_origin": data_origin,
        },
        "linkage_checks": {"linkage_score": 1.0},
        "table_statuses": {
            "sensor_timeseries": _table_status(288),
            "offline_lab_results": _table_status(24),
            "catalyst_lifecycle": _table_status(8),
            "campaign_operation_log": _table_status(12),
            "cost_deployment": _table_status(5),
        },
        "calibration_tasks": [
            {"task_id": "P1_sensor_noise_drift", "task_ready": True, "blockers": []},
            {"task_id": "P2_soft_sensor_retraining", "task_ready": True, "blockers": []},
            {"task_id": "P3_catalyst_lifecycle", "task_ready": True, "blockers": []},
            {"task_id": "P4_loop_time_budget", "task_ready": True, "blockers": []},
            {"task_id": "P5_cost_deployment", "task_ready": True, "blockers": []},
        ],
    }


def _table_status(record_count: int) -> dict[str, object]:
    return {
        "status": "import_ready",
        "record_count": record_count,
        "field_coverage": 1.0,
        "volume_coverage": 1.0,
        "table_score": 1.0,
    }
