from water_ai.agents.model_realism_audit_agent import ModelRealismAuditAgent


def test_model_realism_audit_agent_flags_synthetic_only_validation() -> None:
    report = ModelRealismAuditAgent(
        training_metrics=_training_metrics(field_rows=0, uncertainty=False),
        field_gate_metrics=_field_gate_metrics(field_required=True),
        latest_regression="145 passed",
    ).run([])

    readiness = report.metrics["readiness"]
    validation = report.metrics["validation_audit"]
    backlog = report.metrics["model_upgrade_backlog"]

    assert readiness["realism_status"] == "simulation_baseline_needs_field_grounding"
    assert validation["validation_status"] == "synthetic_only_uncertainty_missing"
    assert any(issue.issue_type == "field_validation_missing" for issue in report.issues)
    assert backlog[0]["work_id"] == "field_data_acceptance_before_retraining"
    assert any(item["work_id"] == "soft_sensor_uncertainty_layer" for item in backlog)


def test_model_realism_audit_agent_recognizes_knowledge_expansion_axes() -> None:
    report = ModelRealismAuditAgent(
        training_metrics=_training_metrics(field_rows=120, uncertainty=True),
        field_gate_metrics=_field_gate_metrics(field_required=False),
        latest_regression="145 passed",
    ).run([])

    knowledge = report.metrics["knowledge_audit"]
    field = report.metrics["field_audit"]
    process = report.metrics["process_audit"]
    backlog = report.metrics["model_upgrade_backlog"]

    assert knowledge["entry_count"] >= 9
    assert knowledge["expected_axes"]["persistent_micropollutant"] is True
    assert knowledge["expected_axes"]["heavy_metal_or_speciation"] is True
    assert knowledge["expected_axes"]["biological_or_nutrient_effluent"] is True
    assert field["field_status"] == "field_validation_can_start"
    assert any(item["work_id"] == "soft_sensor_uncertainty_field_calibration" for item in backlog)
    uncertainty_gap = next(gap for gap in process["gaps"] if gap["gap_id"] == "uncertainty_and_extrapolation")
    assert "已有 synthetic 不确定性" in uncertainty_gap["current_state"]


def _training_metrics(*, field_rows: int, uncertainty: bool) -> dict[str, object]:
    rows_by_source = {"process_dynamics": 34560, "legacy_scenario": 17280}
    if field_rows:
        rows_by_source["field"] = field_rows
    metrics = {
        "model_version": "rf_multioutput_v3_catalyst",
        "rows": 51840 + field_rows,
        "rows_by_source": rows_by_source,
        "mean_mae": 0.01383,
        "mae_by_target": {
            "pollutant_residual_risk": 0.00767,
            "reaction_completion": 0.01084,
            "oxidant_remaining": 0.00553,
            "catalyst_activity": 0.02424,
            "matrix_interference": 0.02087,
        },
        "r2_by_target": {
            "pollutant_residual_risk": 0.99482,
            "reaction_completion": 0.98567,
            "oxidant_remaining": 0.99862,
            "catalyst_activity": 0.91363,
            "matrix_interference": 0.8951,
        },
    }
    if uncertainty:
        metrics["uncertainty_metrics"] = {"prediction_interval_coverage": 0.91}
    return metrics


def _field_gate_metrics(*, field_required: bool) -> dict[str, object]:
    return {
        "readiness": {
            "calibration_gate_status": "calibration_protocol_ready_waiting_for_field_data"
            if field_required
            else "field_calibration_can_start",
            "accepted_gate_count": 5 if field_required else 6,
            "total_gate_count": 6,
            "blocking_gates": ["G0_data_origin"] if field_required else [],
            "data_origin": "synthetic" if field_required else "field",
            "field_data_required": field_required,
        }
    }
