from water_ai.agents.soft_sensor_uncertainty_validation_agent import SoftSensorUncertaintyValidationAgent


def test_uncertainty_validation_agent_requires_field_holdout() -> None:
    report = SoftSensorUncertaintyValidationAgent(
        validation_records=_records(),
        evidence_stage="synthetic_holdout",
    ).run([])

    readiness = report.metrics["readiness"]
    aggregate = report.metrics["aggregate"]

    assert readiness["uncertainty_validation_status"] == "synthetic_uncertainty_layer_ready_needs_field_holdout"
    assert readiness["field_holdout_required"] is True
    assert aggregate["overall_interval_coverage"] > 0.7
    assert any(issue.issue_type == "field_holdout_required_for_uncertainty" for issue in report.issues)


def test_uncertainty_validation_agent_accepts_field_holdout_when_coverage_is_good() -> None:
    report = SoftSensorUncertaintyValidationAgent(
        validation_records=_records(),
        evidence_stage="field_holdout",
    ).run([])

    readiness = report.metrics["readiness"]

    assert readiness["uncertainty_validation_status"] == "field_uncertainty_validation_ready"
    assert readiness["field_holdout_required"] is False


def _records() -> list[dict[str, object]]:
    return [
        {
            "scenario": "clean_release",
            "uncertainty_score": 0.12,
            "ood_risk": 0.0,
            "release_blocked_by_uncertainty": False,
            "target_abs_errors": {
                "pollutant_residual_risk": 0.03,
                "reaction_completion": 0.02,
                "oxidant_remaining": 0.02,
                "catalyst_activity": 0.04,
                "matrix_interference": 0.03,
            },
            "target_interval_coverage": {
                "pollutant_residual_risk": True,
                "reaction_completion": True,
                "oxidant_remaining": True,
                "catalyst_activity": True,
                "matrix_interference": True,
            },
            "target_interval_widths": {
                "pollutant_residual_risk": 0.12,
                "reaction_completion": 0.10,
                "oxidant_remaining": 0.08,
                "catalyst_activity": 0.18,
                "matrix_interference": 0.16,
            },
        },
        {
            "scenario": "matrix_shock",
            "uncertainty_score": 0.31,
            "ood_risk": 0.14,
            "release_blocked_by_uncertainty": True,
            "target_abs_errors": {
                "pollutant_residual_risk": 0.08,
                "reaction_completion": 0.06,
                "oxidant_remaining": 0.05,
                "catalyst_activity": 0.11,
                "matrix_interference": 0.10,
            },
            "target_interval_coverage": {
                "pollutant_residual_risk": True,
                "reaction_completion": True,
                "oxidant_remaining": True,
                "catalyst_activity": False,
                "matrix_interference": True,
            },
            "target_interval_widths": {
                "pollutant_residual_risk": 0.20,
                "reaction_completion": 0.18,
                "oxidant_remaining": 0.16,
                "catalyst_activity": 0.22,
                "matrix_interference": 0.24,
            },
        },
    ]
