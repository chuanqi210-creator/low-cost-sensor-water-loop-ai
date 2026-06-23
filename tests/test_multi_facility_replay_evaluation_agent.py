from experiments.run_agent52_multi_facility_replay_evaluation import (
    AGENT52_REPLAY_EXPORT_FIELDS,
    _agent52_replay_export_payload,
)
from water_ai.agents.multi_facility_collaborative_control_agent import MultiFacilityCollaborativeControlAgent
from water_ai.agents.multi_facility_replay_evaluation_agent import (
    REPLAY_REQUIRED_FIELDS,
    MultiFacilityReplayEvaluationAgent,
)
from water_ai.agents.sensor_network_sparse_placement_agent import SensorNetworkSparsePlacementAgent


def test_multi_facility_replay_agent_builds_replay_schema_and_metrics() -> None:
    report = MultiFacilityReplayEvaluationAgent(
        collaborative_control_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
    ).run([])

    schema = report.metrics["replay_schema"]
    metrics = report.metrics["offline_evaluation_metrics"]
    table = report.metrics["replay_table"]
    comparison = report.metrics["control_policy_comparison"]
    contract = report.metrics["control_baseline_contract"]

    assert schema["schema_id"] == "multi_facility_state_action_reward_replay_v1"
    assert set(REPLAY_REQUIRED_FIELDS).issubset(set(schema["required_fields"]))
    assert metrics["replay_case_count"] >= 5
    assert metrics["candidate_action_count"] >= 5
    assert metrics["control_policy_baseline_strategy_count"] == 6
    assert contract["baseline_strategy_count"] == 6
    assert contract["comparison_status"] == "synthetic_control_policy_baseline_comparison_ready_needs_field_replay"
    assert "release_first_rule" in comparison["metrics_by_strategy"]
    assert "expert_upper_bound" in comparison["metrics_by_strategy"]
    assert table[0]["reward_by_action"]
    assert "catalyst_proxy_summary_status" in table[0]
    assert "joint_action_accuracy" in metrics
    assert "mean_reward_regret" in metrics
    assert metrics["catalyst_proxy_field_validation_pass"] is False


def test_multi_facility_replay_agent_keeps_synthetic_replay_blocked_from_actuator() -> None:
    report = MultiFacilityReplayEvaluationAgent(
        collaborative_control_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
    ).run([])

    readiness = report.metrics["readiness"]
    writeback = report.metrics["agent49_writeback"]

    assert readiness["replay_evaluation_status"] == "synthetic_replay_evaluation_ready_needs_field_replay"
    assert readiness["can_update_agent49_reward_prior"] is True
    assert readiness["can_write_to_actuator"] is False
    assert "actuator_policy" in writeback["blocked_writeback"]
    assert any(issue.issue_type == "field_replay_required_before_agent49_promotion" for issue in report.issues)


def test_multi_facility_replay_agent_surfaces_regret_and_false_positive_costs() -> None:
    report = MultiFacilityReplayEvaluationAgent(
        collaborative_control_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
    ).run([])

    metrics = report.metrics["offline_evaluation_metrics"]
    diagnostics = report.metrics["reward_diagnostics"]

    assert metrics["mean_reward_regret"] > 0
    assert metrics["protective_false_positive_rate"] > 0
    assert diagnostics["highest_regret_cases"]
    assert diagnostics["false_positive_cases"]


def test_multi_facility_replay_agent_refreshes_guardrail_aware_replay_metrics() -> None:
    report = MultiFacilityReplayEvaluationAgent(
        collaborative_control_metrics=_agent49_guardrail_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
    ).run([])

    metrics = report.metrics["offline_evaluation_metrics"]
    diagnostics = report.metrics["reward_diagnostics"]
    readiness = report.metrics["readiness"]

    assert readiness["guardrail_aware_replay_ready"] is True
    assert metrics["control_replay_guardrails_integrated"] is True
    assert metrics["guardrail_aware_joint_action_accuracy"] > metrics["joint_action_accuracy"]
    assert metrics["guardrail_aware_p95_reward_regret"] < metrics["p95_reward_regret"]
    assert metrics["guardrail_aware_false_positive_action_cost"] < metrics["false_positive_action_cost"]
    assert diagnostics["guardrail_resolved_cases"]
    assert readiness["can_write_to_actuator"] is False


def test_multi_facility_replay_agent_outputs_control_policy_baseline_contract() -> None:
    report = MultiFacilityReplayEvaluationAgent(
        collaborative_control_metrics=_agent49_guardrail_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
    ).run([])

    comparison = report.metrics["control_policy_comparison"]
    contract = report.metrics["control_baseline_contract"]
    strategies = comparison["metrics_by_strategy"]

    assert contract["contract_id"] == "agent52_control_policy_baseline_comparison_v1"
    assert contract["missing_baseline_policy_ids"] == []
    assert contract["field_benchmark_required"] is True
    assert contract["can_select_deployed_policy"] is False
    assert contract["can_write_to_actuator"] is False
    assert contract["can_write_to_release_gate"] is False
    assert "cannot prove deployed control performance from synthetic replay" in contract["cannot_do"]
    assert strategies["expert_upper_bound"]["joint_action_accuracy"] == 1.0
    assert strategies["guardrail_aware_policy"]["joint_action_accuracy"] > strategies["agent49_policy"][
        "joint_action_accuracy"
    ]
    assert strategies["guardrail_aware_policy"]["mean_reward_regret"] < strategies["agent49_policy"][
        "mean_reward_regret"
    ]
    assert strategies["release_first_rule"]["release_gate_mismatch_rate"] > strategies["guardrail_aware_policy"][
        "release_gate_mismatch_rate"
    ]
    assert comparison["delta_summary"]["guardrail_vs_agent49_accuracy_gain"] > 0
    assert comparison["delta_summary"]["guardrail_vs_release_first_mismatch_delta"] > 0


def test_agent52_replay_export_payload_matches_r8p_work_package_contract() -> None:
    report = MultiFacilityReplayEvaluationAgent(
        collaborative_control_metrics=_agent49_guardrail_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
    ).run([])

    export = _agent52_replay_export_payload(report)
    manifest = export["manifest"]
    rows = export["rows"]

    assert manifest["work_package_id"] == "R8U25_AGENT52_REPLAY_EXPORT_WORK_PACKAGE"
    assert manifest["export_status"] == "agent52_replay_export_ready_synthetic_only"
    assert manifest["row_count"] == len(report.metrics["replay_table"])
    assert manifest["all_rows_field_origin"] is False
    assert manifest["can_route_to_r8p_candidate_rows"] is False
    assert manifest["can_create_field_evidence_by_export_only"] is False
    assert manifest["can_write_to_actuator"] is False
    assert manifest["can_write_to_release_gate"] is False
    assert set(manifest["required_fields"]).issubset(set(AGENT52_REPLAY_EXPORT_FIELDS))
    assert set(manifest["required_fields"]).issubset(set(rows[0]))
    assert all(row["data_origin"] == "synthetic_replay_design" for row in rows)
    assert all(row["evidence_status"] == "synthetic_replay_candidate_not_field_evidence" for row in rows)
    assert all(row["can_write_to_actuator"] is False for row in rows)
    assert all(row["can_write_to_release_gate"] is False for row in rows)


def test_multi_facility_replay_agent_consumes_pressure_headloss_guardrail_boundary() -> None:
    report = MultiFacilityReplayEvaluationAgent(
        collaborative_control_metrics=_agent49_guardrail_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
    ).run([])

    schema = report.metrics["replay_schema"]
    table = report.metrics["replay_table"]
    metrics = report.metrics["offline_evaluation_metrics"]
    context = report.metrics["pressure_headloss_context"]
    readiness = report.metrics["readiness"]
    writeback = report.metrics["agent49_writeback"]

    assert "pressure_headloss_candidate_pool_status" in schema["required_fields"]
    assert table[0]["pressure_headloss_boundary_consumed"] is True
    assert context["consumed_by_agent52"] is True
    assert metrics["pressure_headloss_boundary_consumed"] is True
    assert metrics["pressure_headloss_candidate_count"] == 3
    assert metrics["pressure_headloss_blocked_guardrail_case_count"] >= 2
    assert metrics["pressure_headloss_can_relax_control_guardrail"] is False
    assert readiness["pressure_headloss_boundary_consumed"] is True
    assert readiness["pressure_headloss_guardrail_field_ready"] is False
    assert readiness["can_write_to_actuator"] is False
    assert writeback["metric_patch"]["pressure_headloss_boundary_consumed"] is True
    assert any(
        issue.issue_type == "pressure_headloss_guardrail_boundary_requires_field_replay"
        for issue in report.issues
    )


def test_multi_facility_replay_agent_blocks_promotion_when_agent51_holdout_summary_has_gaps() -> None:
    report = MultiFacilityReplayEvaluationAgent(
        collaborative_control_metrics=_agent49_guardrail_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics_with_summary(
            summary_status="field_proxy_holdout_coverage_gaps",
            ready_for_validation=False,
            field_validation_pass=False,
            scoreable_batch_count=0,
        ),
        data_origin="field_coordination_replay",
        field_validation={
            "field_replay_coverage": 0.90,
            "joint_action_accuracy": 0.93,
            "reward_regret": 0.05,
            "false_positive_action_cost": 0.08,
            "distilled_policy_accuracy": 0.92,
        },
    ).run([])

    metrics = report.metrics["offline_evaluation_metrics"]
    context = report.metrics["catalyst_proxy_context"]
    readiness = report.metrics["readiness"]
    writeback = report.metrics["agent49_writeback"]

    assert context["summary_status"] == "field_proxy_holdout_coverage_gaps"
    assert metrics["catalyst_proxy_scoreable_batch_count"] == 0
    assert readiness["field_ready"] is False
    assert readiness["can_write_to_actuator"] is False
    assert writeback["policy_effect"] == "keep_agent49_synthetic_policy_block"
    assert any(
        issue.issue_type == "catalyst_proxy_field_validation_blocks_agent49_promotion"
        for issue in report.issues
    )


def test_multi_facility_replay_agent_can_become_field_candidate_with_validated_replay() -> None:
    report = MultiFacilityReplayEvaluationAgent(
        collaborative_control_metrics=_agent49_metrics(),
        catalyst_proxy_metrics={"readiness": {"field_validated": True}},
        data_origin="field_coordination_replay",
        field_validation={
            "field_replay_coverage": 0.90,
            "joint_action_accuracy": 0.93,
            "reward_regret": 0.05,
            "false_positive_action_cost": 0.08,
            "distilled_policy_accuracy": 0.92,
        },
    ).run([])

    readiness = report.metrics["readiness"]
    distillation = report.metrics["distillation_evaluation"]

    assert readiness["replay_evaluation_status"] == "field_replay_evaluation_candidate_ready"
    assert readiness["can_train_offline_rl"] is True
    assert readiness["can_write_to_actuator"] is True
    assert readiness["can_write_to_release_gate"] is False
    assert distillation["can_promote_distilled_policy"] is True


def test_multi_facility_replay_agent_accepts_agent51_field_validated_summary_as_control_gate_input() -> None:
    report = MultiFacilityReplayEvaluationAgent(
        collaborative_control_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics_with_summary(
            summary_status="field_proxy_holdout_validation_passed",
            ready_for_validation=True,
            field_validation_pass=True,
            scoreable_batch_count=4,
        ),
        data_origin="field_coordination_replay",
        field_validation={
            "field_replay_coverage": 0.90,
            "joint_action_accuracy": 0.93,
            "reward_regret": 0.05,
            "false_positive_action_cost": 0.08,
            "distilled_policy_accuracy": 0.92,
        },
    ).run([])

    readiness = report.metrics["readiness"]
    metrics = report.metrics["offline_evaluation_metrics"]
    context = report.metrics["catalyst_proxy_context"]

    assert context["guardrail_mode"] == "agent51_field_validated_human_reviewed_relaxation_candidate"
    assert context["accepted_pressure_evidence_sources"] == ["pressure_headloss_event_log"]
    assert context["pressure_headloss_event_source_batch_count"] == 4
    assert metrics["catalyst_proxy_field_validation_pass"] is True
    assert readiness["replay_evaluation_status"] == "field_replay_evaluation_candidate_ready"
    assert readiness["can_write_to_actuator"] is True
    assert readiness["can_write_to_release_gate"] is False


def test_multi_facility_replay_agent_blocks_promotion_when_pressure_sources_conflict() -> None:
    catalyst_metrics = _catalyst_proxy_metrics_with_summary(
        summary_status="field_proxy_holdout_validation_passed",
        ready_for_validation=True,
        field_validation_pass=True,
        scoreable_batch_count=4,
        pressure_source_conflict_count=1,
    )
    report = MultiFacilityReplayEvaluationAgent(
        collaborative_control_metrics=_agent49_guardrail_metrics(catalyst_proxy_metrics=catalyst_metrics),
        catalyst_proxy_metrics=catalyst_metrics,
        data_origin="field_coordination_replay",
        field_validation={
            "field_replay_coverage": 0.90,
            "joint_action_accuracy": 0.93,
            "reward_regret": 0.05,
            "false_positive_action_cost": 0.08,
            "distilled_policy_accuracy": 0.92,
        },
    ).run([])

    table = report.metrics["replay_table"]
    metrics = report.metrics["offline_evaluation_metrics"]
    context = report.metrics["pressure_headloss_context"]
    readiness = report.metrics["readiness"]
    writeback = report.metrics["agent49_writeback"]

    assert table[0]["pressure_source_conflict_requires_operator_review"] is True
    assert context["pressure_source_conflict_count"] == 1
    assert context["unresolved_pressure_source_conflict_count"] == 1
    assert context["resolved_pressure_source_conflict_count"] == 0
    assert context["pressure_source_resolution_record_count"] == 0
    assert metrics["pressure_source_conflict_count"] == 1
    assert metrics["unresolved_pressure_source_conflict_count"] == 1
    assert metrics["resolved_pressure_source_conflict_count"] == 0
    assert metrics["pressure_source_resolution_record_count"] == 0
    assert metrics["pressure_source_conflict_requires_operator_review"] is True
    assert metrics["pressure_source_conflict_replay_blocked_case_count"] >= 2
    assert readiness["field_ready"] is False
    assert readiness["pressure_source_conflict_clear"] is False
    assert readiness["unresolved_pressure_source_conflict_count"] == 1
    assert readiness["can_write_to_actuator"] is False
    assert writeback["metric_patch"]["pressure_source_conflict_requires_operator_review"] is True
    assert writeback["metric_patch"]["unresolved_pressure_source_conflict_count"] == 1
    assert writeback["policy_effect"] == "keep_agent49_synthetic_policy_block"
    assert any(
        issue.issue_type == "pressure_source_conflict_blocks_agent49_promotion"
        for issue in report.issues
    )


def test_multi_facility_replay_agent_clears_resolved_pressure_source_conflict_gate() -> None:
    catalyst_metrics = _catalyst_proxy_metrics_with_summary(
        summary_status="field_proxy_holdout_validation_passed",
        ready_for_validation=True,
        field_validation_pass=True,
        scoreable_batch_count=4,
        pressure_source_conflict_count=1,
        resolved_pressure_source_conflict_count=1,
    )
    report = MultiFacilityReplayEvaluationAgent(
        collaborative_control_metrics=_agent49_guardrail_metrics(catalyst_proxy_metrics=catalyst_metrics),
        catalyst_proxy_metrics=catalyst_metrics,
        data_origin="field_coordination_replay",
        field_validation={
            "field_replay_coverage": 0.90,
            "joint_action_accuracy": 0.93,
            "reward_regret": 0.05,
            "false_positive_action_cost": 0.08,
            "distilled_policy_accuracy": 0.92,
        },
    ).run([])

    table = report.metrics["replay_table"]
    metrics = report.metrics["offline_evaluation_metrics"]
    context = report.metrics["pressure_headloss_context"]
    readiness = report.metrics["readiness"]
    writeback = report.metrics["agent49_writeback"]

    assert table[0]["pressure_source_conflict_count"] == 1
    assert table[0]["resolved_pressure_source_conflict_count"] == 1
    assert table[0]["unresolved_pressure_source_conflict_count"] == 0
    assert table[0]["pressure_source_conflict_requires_operator_review"] is False
    assert context["pressure_source_conflict_count"] == 1
    assert context["resolved_pressure_source_conflict_count"] == 1
    assert context["unresolved_pressure_source_conflict_count"] == 0
    assert context["pressure_source_resolution_record_count"] == 1
    assert metrics["pressure_source_conflict_count"] == 1
    assert metrics["resolved_pressure_source_conflict_count"] == 1
    assert metrics["unresolved_pressure_source_conflict_count"] == 0
    assert metrics["pressure_source_resolution_record_count"] == 1
    assert metrics["pressure_source_conflict_requires_operator_review"] is False
    assert metrics["pressure_source_conflict_replay_blocked_case_count"] == 0
    assert readiness["pressure_source_conflict_clear"] is True
    assert readiness["unresolved_pressure_source_conflict_count"] == 0
    assert writeback["metric_patch"]["resolved_pressure_source_conflict_count"] == 1
    assert writeback["metric_patch"]["unresolved_pressure_source_conflict_count"] == 0
    assert not any(
        issue.issue_type == "pressure_source_conflict_blocks_agent49_promotion"
        for issue in report.issues
    )


def _agent49_metrics() -> dict[str, object]:
    sparse = _sparse_metrics()
    report = MultiFacilityCollaborativeControlAgent(sparse_placement_metrics=sparse).run([])
    return dict(report.metrics)


def _agent49_guardrail_metrics(catalyst_proxy_metrics: dict[str, object] | None = None) -> dict[str, object]:
    sparse = _sparse_metrics()
    report = MultiFacilityCollaborativeControlAgent(
        sparse_placement_metrics=sparse,
        observation_contract_metrics=_observation_contract_metrics(),
        catalyst_proxy_metrics=catalyst_proxy_metrics,
        control_replay_stress_metrics=_control_replay_stress_metrics(),
    ).run([])
    return dict(report.metrics)


def _sparse_metrics() -> dict[str, object]:
    report = SensorNetworkSparsePlacementAgent(max_sensors=6, budget_limit=5.8).run([])
    return {
        "selected_sensor_plan": report.metrics["selected_sensor_plan"],
        "coverage": dict(report.metrics["coverage"]),
        "readiness": dict(report.metrics["readiness"]),
        "soft_sensor_interface": report.metrics["soft_sensor_interface"],
    }


def _catalyst_proxy_metrics() -> dict[str, object]:
    return {
        "proxy_metrics": {
            "proxy_observability_after_recommended_patch": 0.72,
            "weak_state_coverage_after_proxy_design": 0.72,
        },
        "readiness": {
            "catalyst_proxy_status": "synthetic_catalyst_proxy_design_ready_needs_field_labels",
            "proxy_ready": True,
            "field_validated": False,
        },
    }


def _catalyst_proxy_metrics_with_summary(
    *,
    summary_status: str,
    ready_for_validation: bool,
    field_validation_pass: bool,
    scoreable_batch_count: int,
    pressure_source_conflict_count: int = 0,
    resolved_pressure_source_conflict_count: int = 0,
) -> dict[str, object]:
    unresolved_pressure_source_conflict_count = max(
        0,
        pressure_source_conflict_count - resolved_pressure_source_conflict_count,
    )
    conflict_requires_operator_review = unresolved_pressure_source_conflict_count > 0
    metrics = _catalyst_proxy_metrics()
    metrics["readiness"] = {
        "catalyst_proxy_status": summary_status,
        "field_validated": field_validation_pass,
        "field_proxy_holdout_summary_status": summary_status,
        "field_holdout_scoreable_batch_count": scoreable_batch_count,
        "field_holdout_matched_batch_count": scoreable_batch_count,
        "accepted_pressure_evidence_sources": ["pressure_headloss_event_log"] if scoreable_batch_count else [],
        "pressure_headloss_event_source_batch_count": scoreable_batch_count,
        "pressure_source_conflict_count": pressure_source_conflict_count,
        "resolved_pressure_source_conflict_count": resolved_pressure_source_conflict_count,
        "unresolved_pressure_source_conflict_count": unresolved_pressure_source_conflict_count,
        "pressure_source_resolution_record_count": resolved_pressure_source_conflict_count,
        "conflict_requires_operator_review": conflict_requires_operator_review,
    }
    metrics["field_proxy_holdout_summary"] = {
        "field_proxy_holdout_summary_status": summary_status,
        "ready_for_agent51_validation": ready_for_validation,
        "field_validation_pass": field_validation_pass,
        "scoreable_batch_count": scoreable_batch_count,
        "matched_batch_count": scoreable_batch_count,
        "accepted_pressure_evidence_sources": ["pressure_headloss_event_log"] if scoreable_batch_count else [],
        "pressure_headloss_event_source_batch_count": scoreable_batch_count,
        "pressure_evidence_source_batch_counts": {
            "node_modality_sensor_timeseries": 0,
            "pressure_headloss_event_log": scoreable_batch_count,
            "source_conflict_requires_operator_review": unresolved_pressure_source_conflict_count,
        },
        "pressure_source_conflict_count": pressure_source_conflict_count,
        "resolved_pressure_source_conflict_count": resolved_pressure_source_conflict_count,
        "unresolved_pressure_source_conflict_count": unresolved_pressure_source_conflict_count,
        "pressure_source_resolution_record_count": resolved_pressure_source_conflict_count,
        "pressure_source_conflicts": [
            {
                "batch_id": "B002",
                "action": "operator_review_required_before_agent51_scoring",
            }
        ]
        if pressure_source_conflict_count
        else [],
        "unresolved_pressure_source_conflicts": [
            {
                "batch_id": "B002",
                "action": "operator_review_required_before_agent51_scoring",
            }
        ]
        if unresolved_pressure_source_conflict_count
        else [],
        "pressure_source_resolutions": [
            {
                "batch_id": "B002",
                "authoritative_pressure_source": "pressure_headloss_event_log",
                "calibration_action_id": "CAL-002",
            }
        ]
        if resolved_pressure_source_conflict_count
        else [],
        "conflict_requires_operator_review": conflict_requires_operator_review,
        "field_validation_metrics": {
            "holdout_mae": 0.08 if field_validation_pass else 1.0,
            "proxy_label_correlation": 0.82 if field_validation_pass else 0.0,
        },
    }
    return metrics


def _observation_contract_metrics() -> dict[str, object]:
    return {
        "base_layout_contract": {
            "pressure_headloss_candidate_pool_status": (
                "pressure_headloss_candidate_pool_ready_needs_field_topology_and_labels"
            ),
            "pressure_headloss_candidate_count": 3,
            "pressure_headloss_candidate_ids": [
                "N3_catalyst_bed:pressure_drop_kPa",
                "N3_catalyst_bed:headloss_kPa_per_m",
                "N3_catalyst_bed:flow_normalized_pressure_residual",
            ],
        },
        "readiness": {
            "observation_contract_status": (
                "synthetic_observation_contract_ready_needs_field_topology_proxy_labels_and_missingness"
            ),
            "budget_pass": True,
            "recommended_sensor_count": 7,
            "proxy_enhanced_weak_state_coverage": 0.58,
            "field_proxy_labels_ready": False,
            "agent48_pressure_headloss_candidate_pool_status": (
                "pressure_headloss_candidate_pool_ready_needs_field_topology_and_labels"
            ),
            "agent48_pressure_headloss_candidate_count": 3,
            "agent48_pressure_headloss_candidate_ids": [
                "N3_catalyst_bed:pressure_drop_kPa",
                "N3_catalyst_bed:headloss_kPa_per_m",
                "N3_catalyst_bed:flow_normalized_pressure_residual",
            ],
        },
        "recommended_observation_contract": {
            "candidate_id": "budget_rebalanced_proxy_contract",
            "proxy_enhanced_catalyst_activity_observability": 0.58,
            "contract_pairs": [
                "N0_influent:EC_uScm",
                "N1_equalization_tank:flow_Lmin",
                "N2_reactor_mid:ORP_mV",
                "N3_catalyst_bed_outlet:ORP_mV",
                "N3_catalyst_bed_outlet:UV254_abs",
                "N3_catalyst_bed_outlet:turbidity_NTU",
                "N4_recirculation_loop:UV254_abs",
            ],
        },
    }


def _control_replay_stress_metrics() -> dict[str, object]:
    return {
        "readiness": {
            "control_replay_stress_status": "synthetic_counterfactual_stress_ready_needs_field_replay",
            "field_ready": False,
            "can_update_agent49_reward_prior": True,
        },
        "counterfactual_metrics": {
            "guardrail_candidate": {"joint_action_accuracy": 1.0},
            "p95_reward_regret_delta_guardrail": 0.177,
            "protective_false_positive_cost_delta_guardrail": 0.18,
            "field_replay_coverage": 0.0,
        },
        "reward_prior_patch": {
            "patch_id": "R3_counterfactual_guardrail_reward_prior",
            "triggered_by_cases": [
                {"case_id": "R2", "scenario": "catalyst_uncertain_low_proxy"},
                {"case_id": "R5", "scenario": "hydraulic_delay_violation"},
            ],
            "candidate_rules": [
                {"rule_id": "R3G1_catalyst_uncertain_requires_standby_or_human_review"},
                {"rule_id": "R3G2_hydraulic_delay_unknown_blocks_recycle"},
            ],
        },
    }
