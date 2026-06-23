from water_ai.agents.grey_box_dynamic_latency_agent import GreyBoxDynamicLatencyAgent


def test_grey_box_latency_agent_keeps_synthetic_boundary_and_finds_slow_evidence() -> None:
    report = GreyBoxDynamicLatencyAgent(
        evidence_stage="synthetic_replay",
        field_timestamp_coverage=0.0,
        conformal_readiness={"can_write_to_release_gate": False},
    ).run([])

    readiness = report.metrics["readiness"]
    budget = report.metrics["latency_budget"]
    method_contract = report.metrics["method_contract"]

    assert readiness["latency_status"] == "synthetic_latency_budget_ready_needs_field_timestamps"
    assert readiness["field_timestamps_required"] is True
    assert readiness["release_gate_can_use_latency_budget"] is False
    assert readiness["latency_budget_violation_rate"] > 0
    assert method_contract["upgrade_id"] == "grey_box_dynamic_control_latency"
    assert method_contract["borrowed_from"] == ["parsa_2024_dynamic_control_review"]
    assert any(item["scenario"] == "matrix_shock" and item["latency_status"] == "needs_longer_buffer_or_fast_proxy" for item in budget)
    assert any(issue.issue_type == "field_timestamps_required_for_latency_budget" for issue in report.issues)


def test_grey_box_latency_agent_accepts_field_timestamped_ready_profiles() -> None:
    report = GreyBoxDynamicLatencyAgent(
        scenario_profiles=[_safe_profile("matrix_shock"), _safe_profile("catalyst_deactivation")],
        evidence_stage="field_timestamped",
        field_timestamp_coverage=0.94,
        conformal_readiness={"can_write_to_release_gate": True},
    ).run([])

    readiness = report.metrics["readiness"]

    assert readiness["latency_status"] == "field_latency_budget_ready"
    assert readiness["field_replay_ready"] is True
    assert readiness["release_gate_can_use_latency_budget"] is True
    assert readiness["latency_budget_violation_rate"] == 0.0
    assert report.issues == []


def test_grey_box_latency_agent_blocks_field_replay_when_action_is_too_slow() -> None:
    profile = _safe_profile("oxidant_limitation")
    profile["human_review_min"] = 40.0
    profile["actuator_delay_min"] = 45.0
    profile["action_deadline_min"] = 50.0

    report = GreyBoxDynamicLatencyAgent(
        scenario_profiles=[profile],
        evidence_stage="field_timestamped",
        field_timestamp_coverage=0.9,
        conformal_readiness={"can_write_to_release_gate": True},
    ).run([])

    readiness = report.metrics["readiness"]
    budget = report.metrics["latency_budget"][0]

    assert readiness["latency_status"] == "field_latency_constraints_need_control_redesign"
    assert readiness["field_replay_ready"] is False
    assert budget["latency_status"] == "control_action_too_slow"
    assert report.issues[0].issue_type == "control_action_latency_exceeds_deadline"


def _safe_profile(scenario: str) -> dict[str, object]:
    return {
        "scenario": scenario,
        "risk_mode": "field_safe_test",
        "borrowed_from": "parsa_2024_dynamic_control_review",
        "reality_mapping": "field timestamp replay has enough hold and recycle time for delayed evidence.",
        "data_needs": ["sampling_timestamp", "actuator_command_timestamp", "offline_result_timestamp"],
        "evaluation_metrics": ["latency_budget_violation_rate", "field_replay_success_rate"],
        "failure_boundary": "only valid for this field holdout replay.",
        "sampling_interval_min": 3.0,
        "qc_window_min": 5.0,
        "soft_sensor_compute_min": 1.0,
        "human_review_min": 3.0,
        "lab_turnaround_min": 20.0,
        "actuator_delay_min": 4.0,
        "mixing_delay_min": 5.0,
        "hold_buffer_min": 90.0,
        "recycle_retention_min": 60.0,
        "validation_overlap_credit_min": 10.0,
        "action_deadline_min": 120.0,
    }
