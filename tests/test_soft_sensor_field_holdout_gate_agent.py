from water_ai.agents.soft_sensor_field_holdout_gate_agent import SoftSensorFieldHoldoutGateAgent


def test_field_holdout_gate_blocks_synthetic_metrics_even_when_accuracy_is_high() -> None:
    report = SoftSensorFieldHoldoutGateAgent(
        uncertainty_metrics=_uncertainty_metrics("synthetic_holdout"),
        conformal_metrics=_conformal_metrics("synthetic_holdout"),
    ).run([])

    readiness = report.metrics["readiness"]
    release_policy = report.metrics["release_policy"]

    assert readiness["soft_sensor_field_holdout_gate_status"] == "soft_sensor_release_gate_blocked_non_field_holdout"
    assert "SFG0_field_holdout_origin" in readiness["failed_check_ids"]
    assert release_policy["can_write_to_release_gate"] is False
    assert release_policy["can_auto_release_treated_water"] is False
    assert any(issue.issue_type == "SFG0_field_holdout_origin_failed" for issue in report.issues)


def test_field_holdout_gate_allows_only_calibration_candidate_when_field_metrics_pass() -> None:
    report = SoftSensorFieldHoldoutGateAgent(
        uncertainty_metrics=_uncertainty_metrics("field_holdout"),
        conformal_metrics=_conformal_metrics("field_holdout"),
    ).run([])

    readiness = report.metrics["readiness"]
    release_policy = report.metrics["release_policy"]

    assert readiness["soft_sensor_field_holdout_gate_status"] == "soft_sensor_field_holdout_release_candidate_ready"
    assert readiness["can_write_to_release_gate"] is True
    assert release_policy["write_scope"] == "field_holdout_calibrated_interval_threshold_candidate"
    assert release_policy["can_auto_release_treated_water"] is False
    assert release_policy["requires_offline_lab_confirmation_for_compliance"] is True
    assert report.issues == []


def test_field_holdout_gate_blocks_weak_target_and_ood_failures() -> None:
    conformal = _conformal_metrics("field_holdout")
    conformal["conformal"]["coverage_by_target"]["catalyst_activity"] = 0.70
    conformal["conformal"]["coverage_by_target"]["matrix_interference"] = 0.84
    conformal["conformal"]["ood_alert_rate"] = 0.18

    report = SoftSensorFieldHoldoutGateAgent(
        uncertainty_metrics=_uncertainty_metrics("field_holdout"),
        conformal_metrics=conformal,
    ).run([])

    readiness = report.metrics["readiness"]

    assert readiness["soft_sensor_field_holdout_gate_status"] == "soft_sensor_release_gate_blocked_calibration_gaps"
    assert "SFG4_abstention_and_ood" in readiness["failed_check_ids"]
    assert "SFG5_weak_target_coverage" in readiness["failed_check_ids"]
    assert readiness["can_write_to_release_gate"] is False


def test_field_holdout_gate_requires_scenario_diversity() -> None:
    conformal = _conformal_metrics("field_holdout")
    conformal["conformal"]["scenario_full_coverage"] = {"clean_release": 1.0}
    uncertainty = _uncertainty_metrics("field_holdout")
    uncertainty["uncertainty_metrics"]["scenario_counts"] = {"clean_release": 40}

    report = SoftSensorFieldHoldoutGateAgent(
        uncertainty_metrics=uncertainty,
        conformal_metrics=conformal,
    ).run([])

    readiness = report.metrics["readiness"]

    assert readiness["soft_sensor_field_holdout_gate_status"] == "soft_sensor_release_gate_blocked_calibration_gaps"
    assert "SFG6_scenario_diversity" in readiness["failed_check_ids"]


def _uncertainty_metrics(evidence_stage: str) -> dict[str, object]:
    return {
        "evidence_stage": evidence_stage,
        "uncertainty_metrics": {
            "record_count": 48,
            "scenario_counts": {
                "clean_release": 16,
                "matrix_shock": 16,
                "catalyst_deactivation": 16,
            },
            "coverage_by_target": {
                "pollutant_residual_risk": 0.96,
                "reaction_completion": 0.94,
                "oxidant_remaining": 0.95,
                "catalyst_activity": 0.92,
                "matrix_interference": 0.90,
            },
            "overall_interval_coverage": 0.94,
            "mean_interval_width": 0.18,
            "ood_alert_count": 2,
        },
        "readiness": {
            "uncertainty_validation_status": (
                "field_uncertainty_validation_ready"
                if evidence_stage == "field_holdout"
                else "synthetic_uncertainty_layer_ready_needs_field_holdout"
            ),
            "field_holdout_required": evidence_stage != "field_holdout",
        },
    }


def _conformal_metrics(evidence_stage: str) -> dict[str, object]:
    return {
        "evidence_stage": evidence_stage,
        "split": {
            "record_count": 48,
            "evaluation_count": 16,
        },
        "conformal": {
            "coverage_by_target": {
                "pollutant_residual_risk": 0.95,
                "reaction_completion": 0.93,
                "oxidant_remaining": 0.96,
                "catalyst_activity": 0.90,
                "matrix_interference": 0.91,
            },
            "scenario_full_coverage": {
                "clean_release": 1.0,
                "matrix_shock": 0.88,
                "catalyst_deactivation": 0.80,
            },
            "overall_conformal_coverage": 0.93,
            "mean_conformal_interval_width": 0.24,
            "evaluation_pair_count": 80,
            "release_abstention_rate": 0.12,
            "ood_alert_rate": 0.04,
        },
        "readiness": {
            "conformal_status": (
                "field_conformal_calibration_ready"
                if evidence_stage == "field_holdout"
                else "synthetic_conformal_interface_ready_needs_field_holdout"
            ),
            "can_write_to_release_gate": evidence_stage == "field_holdout",
        },
    }
