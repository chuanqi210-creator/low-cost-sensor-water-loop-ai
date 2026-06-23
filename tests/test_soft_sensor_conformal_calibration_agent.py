from water_ai.agents.soft_sensor_conformal_calibration_agent import SoftSensorConformalCalibrationAgent
from water_ai.soft_sensor_model import TARGET_COLUMNS


def test_conformal_calibration_agent_requires_field_holdout_for_writeback() -> None:
    report = SoftSensorConformalCalibrationAgent(
        validation_records=_records(),
        evidence_stage="synthetic_holdout",
        alpha=0.10,
    ).run([])

    readiness = report.metrics["readiness"]
    conformal = report.metrics["conformal"]

    assert readiness["conformal_status"] == "synthetic_conformal_interface_ready_needs_field_holdout"
    assert readiness["field_holdout_required"] is True
    assert readiness["can_write_to_release_gate"] is False
    assert conformal["target_coverage_level"] == 0.9
    assert conformal["overall_conformal_coverage"] >= 0.8
    assert any(issue.issue_type == "field_holdout_required_for_conformal_calibration" for issue in report.issues)


def test_conformal_calibration_agent_accepts_field_holdout_when_coverage_is_good() -> None:
    report = SoftSensorConformalCalibrationAgent(
        validation_records=_records(),
        evidence_stage="field_holdout",
        alpha=0.10,
    ).run([])

    readiness = report.metrics["readiness"]

    assert readiness["conformal_status"] == "field_conformal_calibration_ready"
    assert readiness["field_holdout_required"] is False
    assert readiness["can_write_to_release_gate"] is True


def _records() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    scenarios = ["clean_release", "matrix_shock", "sensor_faults", "catalyst_deactivation"]
    for index in range(40):
        base_error = 0.015 + 0.002 * (index % 5)
        errors = {
            target: round(base_error + 0.003 * target_index, 4)
            for target_index, target in enumerate(TARGET_COLUMNS)
        }
        records.append(
            {
                "scenario": scenarios[index % len(scenarios)],
                "seed": index,
                "uncertainty_score": round(0.08 + 0.01 * (index % 4), 3),
                "ood_risk": 0.02 if index % 7 else 0.14,
                "target_abs_errors": errors,
            }
        )
    return records
