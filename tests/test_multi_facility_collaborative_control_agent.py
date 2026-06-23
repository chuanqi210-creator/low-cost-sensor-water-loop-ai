from water_ai.agents.multi_facility_collaborative_control_agent import (
    CONTROL_STATE_AXES,
    MultiFacilityCollaborativeControlAgent,
)
from water_ai.agents.sensor_network_sparse_placement_agent import SensorNetworkSparsePlacementAgent


def test_multi_facility_agent_turns_sparse_placement_into_state_action_matrices() -> None:
    sparse = _sparse_metrics()
    report = MultiFacilityCollaborativeControlAgent(sparse_placement_metrics=sparse).run([])

    facility_matrix = report.metrics["facility_state_matrix"]
    joint_actions = report.metrics["joint_action_matrix"]
    readiness = report.metrics["readiness"]

    assert len(facility_matrix) == 5
    assert set(facility_matrix[0]["state_vector"]) == set(CONTROL_STATE_AXES)
    assert len(joint_actions) >= 5
    assert joint_actions[0]["joint_policy_score"] >= joint_actions[-1]["joint_policy_score"]
    assert readiness["coordination_status"] == "synthetic_collaborative_policy_needs_field_replay"
    assert readiness["can_write_to_actuator"] is False


def test_multi_facility_agent_keeps_decision_tree_as_explanation_until_field_validated() -> None:
    sparse = _sparse_metrics()
    report = MultiFacilityCollaborativeControlAgent(sparse_placement_metrics=sparse).run([])

    distilled = report.metrics["decision_tree_distillation"]

    assert distilled["distillation_method"] == "ID3_style_decision_tree_surrogate"
    assert distilled["distilled_policy_accuracy_proxy"] < distilled["minimum_required_accuracy"]
    assert distilled["can_replace_black_box_policy"] is False
    assert any(rule["rule_id"] == "R3_catalyst_uncertainty_block" for rule in distilled["tree_rules"])
    assert any(issue.issue_type == "catalyst_state_too_weak_for_autonomous_policy" for issue in report.issues)


def test_multi_facility_agent_can_become_candidate_with_field_replay_and_stronger_catalyst_observability() -> None:
    sparse = _sparse_metrics()
    sparse["coverage"]["catalyst_activity_observability"] = 0.72
    sparse["coverage"]["weak_state_coverage"] = 0.72
    sparse["readiness"]["sparse_placement_status"] = "field_sparse_sensor_layout_candidate_ready"

    report = MultiFacilityCollaborativeControlAgent(
        sparse_placement_metrics=sparse,
        data_origin="field_coordination_replay",
        field_validation={
            "joint_action_accuracy": 0.93,
            "reward_regret": 0.05,
            "field_replay_coverage": 0.90,
            "distilled_policy_accuracy": 0.92,
        },
    ).run([])

    readiness = report.metrics["readiness"]
    distilled = report.metrics["decision_tree_distillation"]

    assert readiness["coordination_status"] == "field_collaborative_policy_candidate_ready"
    assert readiness["can_write_to_actuator"] is True
    assert readiness["can_write_to_release_gate"] is False
    assert distilled["can_replace_black_box_policy"] is True


def test_multi_facility_agent_consumes_observation_contract_as_design_prior() -> None:
    sparse = _sparse_metrics()
    report = MultiFacilityCollaborativeControlAgent(
        sparse_placement_metrics=sparse,
        observation_contract_metrics={
            "readiness": {
                "observation_contract_status": (
                    "synthetic_observation_contract_ready_needs_field_topology_proxy_labels_and_missingness"
                ),
                "budget_pass": True,
                "recommended_sensor_count": 7,
                "proxy_enhanced_weak_state_coverage": 0.58,
                "field_proxy_labels_ready": False,
                "weak_axis_repair_status": "agent48_catalyst_axis_requires_proxy_patch_and_field_label",
                "weak_axis_repair_score": 0.983,
                "field_repair_evidence_requirement_count": 4,
            },
            "recommended_observation_contract": {
                "candidate_id": "budget_rebalanced_proxy_contract",
                "contract_id": "greedy_marginal:6x10::budget_rebalanced_proxy_contract",
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
                "weak_axis_repair_status": "agent48_catalyst_axis_requires_proxy_patch_and_field_label",
                "weak_axis_repair_score": 0.983,
                "field_repair_evidence_requirement_count": 4,
            },
        },
    ).run([])

    sparse_context = report.metrics["sparse_context"]
    readiness = report.metrics["readiness"]

    assert sparse_context["observation_contract_context"]["contract_ready"] is True
    assert sparse_context["coverage"]["weak_state_coverage"] == 0.58
    assert sparse_context["coverage"]["catalyst_activity_observability"] == 0.58
    assert sparse_context["selected_sensor_count"] == 7
    assert (
        sparse_context["observation_contract_context"]["weak_axis_repair_status"]
        == "agent48_catalyst_axis_requires_proxy_patch_and_field_label"
    )
    assert any(issue.issue_type == "catalyst_axis_repair_prior_not_field_validated" for issue in report.issues)
    assert readiness["weak_state_ready"] is True
    assert readiness["can_write_to_actuator"] is False


def test_multi_facility_agent_consumes_control_replay_stress_as_reward_prior() -> None:
    sparse = _sparse_metrics()
    report = MultiFacilityCollaborativeControlAgent(
        sparse_placement_metrics=sparse,
        observation_contract_metrics=_observation_contract_metrics(),
        control_replay_stress_metrics=_control_replay_stress_metrics(),
    ).run([])

    context = report.metrics["control_replay_guardrail_context"]
    actions = {item["joint_action_id"]: item for item in report.metrics["joint_action_matrix"]}
    readiness = report.metrics["readiness"]
    rule_ids = {rule["rule_id"] for rule in report.metrics["decision_tree_distillation"]["tree_rules"]}

    assert context["reward_prior_guardrail_available"] is True
    assert context["can_write_to_actuator"] is False
    assert readiness["control_replay_guardrails_integrated"] is True
    assert actions["J2_catalyst_protection_before_regeneration"]["reward_components"][
        "control_replay_guardrail_penalty"
    ] == 0.16
    assert actions["J0_matrix_shock_equalize_and_recycle"]["reward_components"][
        "control_replay_guardrail_penalty"
    ] == 0.14
    assert actions["J4_safe_low_cost_standby"]["reward_components"]["control_replay_guardrail_bonus"] == 0.045
    assert "R3G1_catalyst_uncertain_requires_standby_or_human_review" in rule_ids
    assert "R3G2_hydraulic_delay_unknown_blocks_recycle" in rule_ids
    assert report.metrics["shared_experience_pool"]["priority_replay_keys"][-1] == "R3_counterfactual_guardrail_case"


def test_multi_facility_agent_consumes_agent51_holdout_summary_for_catalyst_guardrail() -> None:
    sparse = _sparse_metrics()
    report = MultiFacilityCollaborativeControlAgent(
        sparse_placement_metrics=sparse,
        observation_contract_metrics=_observation_contract_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(summary_status="field_proxy_holdout_coverage_gaps"),
        control_replay_stress_metrics=_control_replay_stress_metrics(),
    ).run([])

    context = report.metrics["control_replay_guardrail_context"]
    actions = {item["joint_action_id"]: item for item in report.metrics["joint_action_matrix"]}

    assert context["catalyst_proxy_summary_status"] == "field_proxy_holdout_coverage_gaps"
    assert context["catalyst_proxy_scoreable_batch_count"] == 0
    assert context["field_proxy_labels_ready"] is False
    assert context["catalyst_guardrail_mode"] == "agent51_holdout_coverage_gaps_keep_catalyst_guardrail"
    assert actions["J2_catalyst_protection_before_regeneration"]["reward_components"][
        "control_replay_guardrail_penalty"
    ] == 0.16
    assert any(
        issue.issue_type == "agent51_catalyst_proxy_not_ready_for_control_relaxation"
        for issue in report.issues
    )


def test_multi_facility_agent_consumes_pressure_headloss_contract_as_control_boundary() -> None:
    sparse = _sparse_metrics()
    report = MultiFacilityCollaborativeControlAgent(
        sparse_placement_metrics=sparse,
        observation_contract_metrics=_observation_contract_metrics(),
    ).run([])

    observation_context = report.metrics["sparse_context"]["observation_contract_context"]
    guardrail_context = report.metrics["control_replay_guardrail_context"]
    rule_ids = {rule["rule_id"] for rule in report.metrics["decision_tree_distillation"]["tree_rules"]}

    assert observation_context["pressure_headloss_consumed_by_agent49"] is True
    assert observation_context["pressure_headloss_candidate_pool_status"] == (
        "pressure_headloss_candidate_pool_ready_needs_field_topology_and_labels"
    )
    assert "N3_catalyst_bed:pressure_drop_kPa" in observation_context["pressure_headloss_candidate_ids"]
    assert observation_context["pressure_headloss_can_relax_control_guardrail"] is False
    assert guardrail_context["pressure_headloss_consumed_by_agent49"] is True
    assert guardrail_context["pressure_headloss_can_relax_control_guardrail"] is False
    assert guardrail_context["can_write_to_actuator"] is False
    assert report.metrics["readiness"]["can_write_to_actuator"] is False
    assert "R8C_pressure_headloss_candidate_boundary" in rule_ids
    assert any(
        issue.issue_type == "pressure_headloss_candidate_not_field_validated_for_control"
        for issue in report.issues
    )


def test_multi_facility_agent_relaxes_r3g1_reward_penalty_only_after_agent51_field_validation() -> None:
    sparse = _sparse_metrics()
    report = MultiFacilityCollaborativeControlAgent(
        sparse_placement_metrics=sparse,
        observation_contract_metrics=_observation_contract_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(
            summary_status="field_proxy_holdout_validation_passed",
            ready_for_validation=True,
            field_validation_pass=True,
            scoreable_batch_count=4,
        ),
        control_replay_stress_metrics=_control_replay_stress_metrics(),
    ).run([])

    context = report.metrics["control_replay_guardrail_context"]
    actions = {item["joint_action_id"]: item for item in report.metrics["joint_action_matrix"]}

    assert context["field_proxy_labels_ready"] is True
    assert context["catalyst_proxy_field_validation_pass"] is True
    assert context["accepted_pressure_evidence_sources"] == ["pressure_headloss_event_log"]
    assert context["pressure_headloss_event_source_batch_count"] == 4
    assert context["catalyst_guardrail_mode"] == "agent51_field_validated_human_reviewed_relaxation_candidate"
    assert actions["J2_catalyst_protection_before_regeneration"]["reward_components"][
        "control_replay_guardrail_penalty"
    ] == 0.0
    assert report.metrics["readiness"]["can_write_to_actuator"] is False


def test_multi_facility_agent_keeps_guardrail_when_pressure_sources_conflict_after_field_validation() -> None:
    sparse = _sparse_metrics()
    report = MultiFacilityCollaborativeControlAgent(
        sparse_placement_metrics=sparse,
        observation_contract_metrics=_observation_contract_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(
            summary_status="field_proxy_holdout_validation_passed",
            ready_for_validation=True,
            field_validation_pass=True,
            scoreable_batch_count=4,
            pressure_source_conflict_count=1,
        ),
        control_replay_stress_metrics=_control_replay_stress_metrics(),
    ).run([])

    context = report.metrics["control_replay_guardrail_context"]
    actions = {item["joint_action_id"]: item for item in report.metrics["joint_action_matrix"]}
    rule_ids = {rule["rule_id"] for rule in report.metrics["decision_tree_distillation"]["tree_rules"]}

    assert context["catalyst_proxy_field_validation_pass"] is True
    assert context["field_proxy_labels_ready"] is False
    assert context["pressure_source_conflict_count"] == 1
    assert context["resolved_pressure_source_conflict_count"] == 0
    assert context["unresolved_pressure_source_conflict_count"] == 1
    assert context["pressure_source_resolution_record_count"] == 0
    assert len(context["unresolved_pressure_source_conflicts"]) == 1
    assert context["conflict_requires_operator_review"] is True
    assert context["pressure_source_conflict_control_block"] is True
    assert context["catalyst_guardrail_mode"] == "agent51_pressure_source_conflict_keep_catalyst_guardrail"
    assert actions["J2_catalyst_protection_before_regeneration"]["reward_components"][
        "control_replay_guardrail_penalty"
    ] == 0.16
    assert "R8K_pressure_source_conflict_requires_operator_review" in rule_ids
    assert any(
        issue.issue_type == "pressure_source_conflict_blocks_control_relaxation"
        for issue in report.issues
    )


def test_multi_facility_agent_accepts_resolved_pressure_source_conflict_context() -> None:
    sparse = _sparse_metrics()
    report = MultiFacilityCollaborativeControlAgent(
        sparse_placement_metrics=sparse,
        observation_contract_metrics=_observation_contract_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(
            summary_status="field_proxy_holdout_validation_passed",
            ready_for_validation=True,
            field_validation_pass=True,
            scoreable_batch_count=4,
            pressure_source_conflict_count=1,
            resolved_pressure_source_conflict_count=1,
        ),
        control_replay_stress_metrics=_control_replay_stress_metrics(),
    ).run([])

    context = report.metrics["control_replay_guardrail_context"]

    assert context["catalyst_proxy_field_validation_pass"] is True
    assert context["field_proxy_labels_ready"] is True
    assert context["pressure_source_conflict_count"] == 1
    assert context["resolved_pressure_source_conflict_count"] == 1
    assert context["unresolved_pressure_source_conflict_count"] == 0
    assert context["pressure_source_resolution_record_count"] == 1
    assert len(context["pressure_source_resolutions"]) == 1
    assert context["conflict_requires_operator_review"] is False
    assert context["pressure_source_conflict_control_block"] is False
    assert context["catalyst_guardrail_mode"] == "agent51_field_validated_human_reviewed_relaxation_candidate"
    assert not any(
        issue.issue_type == "pressure_source_conflict_blocks_control_relaxation"
        for issue in report.issues
    )


def _sparse_metrics() -> dict[str, object]:
    report = SensorNetworkSparsePlacementAgent(max_sensors=6, budget_limit=5.8).run([])
    return {
        "selected_sensor_plan": report.metrics["selected_sensor_plan"],
        "coverage": dict(report.metrics["coverage"]),
        "readiness": dict(report.metrics["readiness"]),
        "soft_sensor_interface": report.metrics["soft_sensor_interface"],
    }


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
            "pressure_headloss_field_package_contract": {
                "required_tables": [
                    "node_modality_sensor_timeseries",
                    "offline_lab_results",
                    "campaign_operation_log",
                    "site_topology_or_bed_geometry",
                ],
                "minimum_matched_batch_count": 3,
            },
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
            "weak_axis_repair_status": "agent48_catalyst_axis_requires_proxy_patch_and_field_label",
            "weak_axis_repair_score": 0.983,
            "field_repair_evidence_requirement_count": 4,
        },
        "recommended_observation_contract": {
            "candidate_id": "budget_rebalanced_proxy_contract",
            "contract_id": "greedy_marginal:6x10::budget_rebalanced_proxy_contract",
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
            "weak_axis_repair_status": "agent48_catalyst_axis_requires_proxy_patch_and_field_label",
            "weak_axis_repair_score": 0.983,
            "field_repair_evidence_requirement_count": 4,
        },
        "field_validation_requirements": [
            {
                "requirement_id": "R2_FV4_agent48_hidden_state_requirement_patch",
                "pressure_headloss_candidate_pool_status": (
                    "pressure_headloss_candidate_pool_ready_needs_field_topology_and_labels"
                ),
                "pressure_headloss_candidate_ids": [
                    "N3_catalyst_bed:pressure_drop_kPa",
                    "N3_catalyst_bed:headloss_kPa_per_m",
                    "N3_catalyst_bed:flow_normalized_pressure_residual",
                ],
                "minimum_matched_batch_count": 3,
                "required_tables": [
                    "node_modality_sensor_timeseries",
                    "offline_lab_results",
                    "campaign_operation_log",
                    "site_topology_or_bed_geometry",
                ],
            }
        ],
    }


def _control_replay_stress_metrics() -> dict[str, object]:
    return {
        "readiness": {
            "control_replay_stress_status": "synthetic_counterfactual_stress_ready_needs_field_replay",
            "field_ready": False,
            "can_update_agent49_reward_prior": True,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
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
                {
                    "rule_id": "R3G1_catalyst_uncertain_requires_standby_or_human_review",
                    "if": "catalyst proxy is not field validated",
                    "then": "prefer J4_safe_low_cost_standby",
                },
                {
                    "rule_id": "R3G2_hydraulic_delay_unknown_blocks_recycle",
                    "if": "tank storage margin or actuator latency evidence is missing",
                    "then": "prefer J3_polishing_and_release_gate",
                },
            ],
        },
    }


def _catalyst_proxy_metrics(
    *,
    summary_status: str,
    ready_for_validation: bool = False,
    field_validation_pass: bool = False,
    scoreable_batch_count: int = 0,
    pressure_source_conflict_count: int = 0,
    resolved_pressure_source_conflict_count: int = 0,
) -> dict[str, object]:
    unresolved_pressure_source_conflict_count = max(
        0,
        pressure_source_conflict_count - resolved_pressure_source_conflict_count,
    )
    conflict_requires_operator_review = unresolved_pressure_source_conflict_count > 0
    unresolved_conflicts = [
        {
            "batch_id": "B002",
            "action": "operator_review_required_before_agent51_scoring",
        }
    ] if unresolved_pressure_source_conflict_count else []
    resolutions = [
        {
            "batch_id": "B002",
            "authoritative_pressure_source": "pressure_headloss_event_log",
            "calibration_action_id": "CAL-002",
        }
    ] if resolved_pressure_source_conflict_count else []
    return {
        "readiness": {
            "field_validated": field_validation_pass,
            "field_proxy_holdout_summary_status": summary_status,
            "field_holdout_scoreable_batch_count": scoreable_batch_count,
            "accepted_pressure_evidence_sources": ["pressure_headloss_event_log"] if scoreable_batch_count else [],
            "pressure_headloss_event_source_batch_count": scoreable_batch_count,
            "pressure_source_conflict_count": pressure_source_conflict_count,
            "resolved_pressure_source_conflict_count": resolved_pressure_source_conflict_count,
            "unresolved_pressure_source_conflict_count": unresolved_pressure_source_conflict_count,
            "pressure_source_resolution_record_count": resolved_pressure_source_conflict_count,
            "unresolved_pressure_source_conflicts": unresolved_conflicts,
            "pressure_source_resolutions": resolutions,
            "conflict_requires_operator_review": conflict_requires_operator_review,
        },
        "field_proxy_holdout_summary": {
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
            "unresolved_pressure_source_conflicts": unresolved_conflicts,
            "pressure_source_resolutions": resolutions,
            "conflict_requires_operator_review": conflict_requires_operator_review,
            "missing_required_signals": []
            if field_validation_pass
            else [
                "N3_catalyst_bed_outlet:UV254_abs",
                "N3_catalyst_bed_outlet:ORP_mV",
                "N3_catalyst_bed:pressure_drop_kPa",
            ],
            "field_validation_metrics": {
                "holdout_mae": 0.08 if field_validation_pass else 1.0,
                "proxy_label_correlation": 0.82 if field_validation_pass else 0.0,
            },
        },
    }
