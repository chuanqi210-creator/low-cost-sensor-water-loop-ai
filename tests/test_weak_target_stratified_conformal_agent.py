from water_ai.agents.weak_target_stratified_conformal_agent import WeakTargetStratifiedConformalAgent


def test_weak_target_stratified_agent_blocks_synthetic_candidate() -> None:
    report = WeakTargetStratifiedConformalAgent(
        conformal_metrics=_conformal_metrics("synthetic_holdout", matrix_coverage=0.875),
        validation_records=_records(matrix_misses=True),
    ).run([])

    readiness = report.metrics["readiness"]
    handoff = report.metrics["handoff_policy"]
    profiles = {item["target"]: item for item in report.metrics["weak_target_profiles"]}

    assert readiness["weak_target_stratified_status"] == "weak_target_stratified_synthetic_candidate_needs_field_holdout"
    assert "WTC0_field_holdout_origin" in readiness["failed_check_ids"]
    assert "WTC2_weak_target_coverage" in readiness["failed_check_ids"]
    assert handoff["can_pass_candidate_to_agent46"] is False
    assert handoff["can_write_to_release_gate"] is False
    assert profiles["matrix_interference"]["candidate_threshold"] > profiles["matrix_interference"]["base_threshold"]


def test_weak_target_stratified_agent_allows_field_candidate_for_agent46_only() -> None:
    report = WeakTargetStratifiedConformalAgent(
        conformal_metrics=_conformal_metrics("field_holdout", matrix_coverage=0.92),
        validation_records=_records(matrix_misses=False),
    ).run([])

    readiness = report.metrics["readiness"]
    handoff = report.metrics["handoff_policy"]

    assert readiness["weak_target_stratified_status"] == "field_weak_target_stratified_candidate_ready_for_agent46"
    assert readiness["can_pass_candidate_to_agent46"] is True
    assert readiness["can_write_to_release_gate"] is False
    assert handoff["candidate_type"] == "weak_target_stratified_threshold_candidate"
    assert handoff["can_write_to_release_gate"] is False
    assert report.issues == []


def test_weak_target_stratified_agent_flags_field_weak_target_failure() -> None:
    report = WeakTargetStratifiedConformalAgent(
        conformal_metrics=_conformal_metrics("field_holdout", matrix_coverage=0.72),
        validation_records=_records(matrix_misses=True),
    ).run([])

    readiness = report.metrics["readiness"]
    profiles = {item["target"]: item for item in report.metrics["weak_target_profiles"]}

    assert readiness["weak_target_stratified_status"] == "field_weak_target_stratification_needs_recalibration"
    assert "WTC2_weak_target_coverage" in readiness["failed_check_ids"]
    assert profiles["matrix_interference"]["recommended_mode"] == "target_and_scenario_stratified_conformal"
    assert any(issue.issue_type == "WTC2_weak_target_coverage_failed" for issue in report.issues)


def test_weak_target_stratified_agent_preserves_release_gate_boundary() -> None:
    report = WeakTargetStratifiedConformalAgent(
        conformal_metrics=_conformal_metrics("field_holdout", matrix_coverage=0.92),
        validation_records=_records(matrix_misses=False),
    ).run([])

    assert report.metrics["readiness"]["can_write_to_release_gate"] is False
    assert report.metrics["handoff_policy"]["can_auto_release_treated_water"] is False


def _conformal_metrics(evidence_stage: str, *, matrix_coverage: float) -> dict[str, object]:
    return {
        "evidence_stage": evidence_stage,
        "alpha": 0.1,
        "split": {
            "record_count": 40,
            "calibration_indices": list(range(24)),
            "evaluation_indices": list(range(24, 40)),
        },
        "conformal": {
            "target_coverage_level": 0.9,
            "target_nonconformity_thresholds": {
                "catalyst_activity": 0.14,
                "matrix_interference": 0.10,
            },
            "coverage_by_target": {
                "catalyst_activity": 0.94,
                "matrix_interference": matrix_coverage,
            },
            "width_by_target": {
                "catalyst_activity": 0.28,
                "matrix_interference": 0.20,
            },
            "misses_by_target": {
                "catalyst_activity": 0,
                "matrix_interference": 2 if matrix_coverage < 0.88 else 0,
            },
        },
        "readiness": {
            "conformal_status": "field_conformal_calibration_ready" if evidence_stage == "field_holdout" else "synthetic_conformal_interface_ready_needs_field_holdout",
            "can_write_to_release_gate": False,
        },
    }


def _records(*, matrix_misses: bool) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    scenarios = ["clean_release", "matrix_shock", "catalyst_deactivation", "matrix_shock"]
    for index in range(40):
        scenario = scenarios[index % len(scenarios)]
        matrix_error = 0.08
        if matrix_misses and index in (29, 33, 37):
            matrix_error = 0.16
        records.append(
            {
                "scenario": scenario,
                "target_abs_errors": {
                    "catalyst_activity": 0.10 if index % 6 else 0.12,
                    "matrix_interference": matrix_error,
                },
            }
        )
    return records
