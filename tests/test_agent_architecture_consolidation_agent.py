import json

from water_ai.agents.agent_architecture_consolidation_agent import (
    AGENT_MODULE_MAP,
    CORE_ANCHOR_AGENTS,
    AgentArchitectureConsolidationAgent,
    REQUIRED_ARCHITECTURE_EVIDENCE_FIELDS,
    REQUIRED_PATENT_TECHNICAL_FEATURE_FIELDS,
    REQUIRED_TECHNICAL_CLAIM_SCAFFOLD_FIELDS,
    REQUIRED_TECHNICAL_EMBODIMENT_FIELDS,
    REQUIRED_TECHNICAL_EFFECT_MEASUREMENT_FIELDS,
    REQUIRED_PRIOR_ART_DISTINCTION_FIELDS,
    REQUIRED_FORMAL_SEARCH_WORK_PACKAGE_FIELDS,
    REQUIRED_FORMAL_SEARCH_RESULT_INTAKE_FIELDS,
    REQUIRED_FORMAL_SEARCH_RESULT_VALIDATION_GATE_FIELDS,
    REQUIRED_FORMAL_SEARCH_RESULT_PACKAGE_TEMPLATE_FIELDS,
    REQUIRED_FORMAL_SEARCH_RESULT_SUBMISSION_TEMPLATE_FIELDS,
    PRIOR_ART_HIT_TABLE_FIELDS,
    CLAIM_ELEMENT_COMPARISON_FIELDS,
)


def test_architecture_consolidation_maps_all_known_agents_to_modules() -> None:
    report = AgentArchitectureConsolidationAgent(agent_names=list(AGENT_MODULE_MAP)).run([])

    assert report.metrics["agent_count"] == len(AGENT_MODULE_MAP)
    assert report.metrics["unmapped_agent_count"] == 0
    assert report.metrics["mapped_agent_count"] == len(AGENT_MODULE_MAP)
    assert report.metrics["module_count"] == 9
    assert report.metrics["core_anchor_coverage"]["coverage_rate"] == 1.0


def test_architecture_consolidation_maps_modules_to_global_seven_layer_spine() -> None:
    report = AgentArchitectureConsolidationAgent(agent_names=list(AGENT_MODULE_MAP)).run([])

    spine = report.metrics["system_spine_coverage"]
    layer_board = report.metrics["system_layer_board"]
    spine_map = {row["module_id"]: row for row in report.metrics["system_spine_map"]}

    assert spine["system_spine_status"] == "global_system_spine_mapped_with_frozen_expression_layer"
    assert spine["layer_coverage_rate"] == 1.0
    assert spine["ability_coverage_rate"] == 1.0
    assert spine["missing_layers"] == []
    assert spine["missing_abilities"] == []
    assert len(layer_board) == 7
    assert all(row["coverage_status"] == "covered" for row in layer_board)
    assert spine_map["M1_sparse_observation_layout"]["primary_layer"] == "L2_observation_layer"
    assert spine_map["M4_collaborative_control"]["primary_layer"] == "L5_diagnostic_decision_layer"
    assert spine_map["M8_model_governance"]["core_abilities"] == ["evolvability", "verifiability"]


def test_architecture_consolidation_exposes_complete_module_interface_contracts() -> None:
    report = AgentArchitectureConsolidationAgent(agent_names=list(AGENT_MODULE_MAP)).run([])

    coverage = report.metrics["interface_contract_coverage"]
    contracts = {row["module_id"]: row for row in report.metrics["module_interface_contracts"]}

    assert coverage["interface_contract_status"] == "all_module_interface_contracts_complete"
    assert coverage["interface_contract_coverage_rate"] == 1.0
    assert coverage["incomplete_module_contracts"] == []
    assert coverage["module_contract_count"] == report.metrics["module_count"]
    assert coverage["complete_module_contract_count"] == report.metrics["module_count"]
    assert all(
        contract["contract_status"] == "interface_contract_complete"
        for contract in contracts.values()
    )
    assert "joint_action" in contracts["M4_collaborative_control"]["state_variables"]
    assert "不能改变模型结论" in contracts["M9_presentation_delivery"]["cannot_do"]
    assert "field evidence" in contracts["M6_field_evidence_chain"]["cannot_do"]


def test_architecture_consolidation_exposes_patent_grade_technical_feature_ledger() -> None:
    report = AgentArchitectureConsolidationAgent(agent_names=list(AGENT_MODULE_MAP)).run([])

    coverage = report.metrics["patent_technical_feature_coverage"]
    ledger = {row["feature_id"]: row for row in report.metrics["patent_technical_feature_ledger"]}

    assert coverage["patent_technical_feature_status"] == (
        "technical_feature_ledger_ready_as_disclosure_scaffold_not_field_claim"
    )
    assert coverage["technical_feature_coverage_rate"] == 1.0
    assert coverage["field_claim_upgrade_allowed"] is False
    assert coverage["abstract_only_feature_ids"] == []
    assert coverage["excluded_modules"] == ["M9_presentation_delivery"]
    assert len(ledger) == 8
    assert "M9_presentation_delivery" not in {row["module_id"] for row in ledger.values()}
    for row in ledger.values():
        missing = [field for field in REQUIRED_PATENT_TECHNICAL_FEATURE_FIELDS if not row.get(field)]
        assert missing == []
        assert row["feature_status"] == "technical_feature_candidate_complete_not_field_claim"
        assert row["abstract_only_risk"] is False
        assert row["field_claim_status"] == (
            "not_field_supported_until_replay_holdout_operator_review_and_release_gate_pass"
        )
        assert row["evidence_boundary"]
        assert row["field_validation_gate"]
        assert row["legal_status"] == "technical_disclosure_candidate_not_legal_advice"

    cyclic_control = ledger["PTF4_cyclic_low_frequency_control"]
    assert "回流" in cyclic_control["control_actions"]
    assert "release gate" in cyclic_control["evidence_boundary"]
    assert "低频" in cyclic_control["prior_art_distinction"]


def test_architecture_consolidation_exposes_technical_claim_skeleton_scaffold() -> None:
    report = AgentArchitectureConsolidationAgent(agent_names=list(AGENT_MODULE_MAP)).run([])

    coverage = report.metrics["technical_claim_skeleton_coverage"]
    scaffolds = {row["claim_id"]: row for row in report.metrics["technical_claim_skeleton_scaffold"]}

    assert coverage["technical_claim_skeleton_status"] == (
        "technical_claim_skeleton_ready_as_scaffold_not_legal_claim_not_field_claim"
    )
    assert coverage["technical_claim_skeleton_coverage_rate"] == 1.0
    assert coverage["claim_scaffold_count"] == 7
    assert len(coverage["independent_claim_scaffold_ids"]) == 2
    assert len(coverage["dependent_or_divisional_scaffold_ids"]) == 5
    assert coverage["missing_feature_coverage"] == []
    assert coverage["field_claim_upgrade_allowed"] is False
    assert coverage["legal_status"] == "technical_claim_scaffold_not_legal_advice"

    main_method = scaffolds["TCS1_independent_method_low_cost_sparse_cyclic_greybox_control"]
    assert set(main_method["required_layers"]) == {
        "L1_field_object_layer",
        "L2_observation_layer",
        "L3_state_estimation_layer",
        "L4_mechanism_evidence_layer",
        "L5_diagnostic_decision_layer",
        "L6_closed_loop_execution_layer",
        "L7_validation_governance_layer",
    }
    assert "PTF4_cyclic_low_frequency_control" in main_method["mapped_feature_ids"]
    assert "release gate" in main_method["verification_gates"]
    assert main_method["claim_upgrade_allowed"] is False

    dependent_ids = set(coverage["dependent_or_divisional_scaffold_ids"])
    assert {
        "TCS3_dependent_catalyst_activity_regeneration_control",
        "TCS4_dependent_node_modality_sparse_hidden_state_estimation",
        "TCS5_dependent_field_replay_protective_writeback",
        "TCS6_dependent_low_frequency_cycle_window_control",
        "TCS7_dependent_greybox_multi_agent_safety_arbitration",
    } == dependent_ids
    for row in scaffolds.values():
        missing = [field for field in REQUIRED_TECHNICAL_CLAIM_SCAFFOLD_FIELDS if not row.get(field)]
        assert missing == []
        assert row["claim_scaffold_status"] == (
            "technical_claim_scaffold_complete_not_legal_claim_not_field_claim"
        )
        assert row["missing_feature_ids"] == []
        assert row["abstract_only_risk"] is False
        assert row["field_claim_status"] == "not_field_supported_until_required_gates_pass"
        assert row["legal_status"] == "technical_claim_scaffold_not_legal_advice"


def test_architecture_consolidation_exposes_technical_embodiment_validation_matrix() -> None:
    report = AgentArchitectureConsolidationAgent(agent_names=list(AGENT_MODULE_MAP)).run([])

    coverage = report.metrics["technical_embodiment_validation_coverage"]
    embodiments = {
        row["embodiment_id"]: row
        for row in report.metrics["technical_embodiment_validation_matrix"]
    }

    assert coverage["technical_embodiment_validation_status"] == (
        "technical_embodiment_matrix_ready_not_field_evidence"
    )
    assert coverage["technical_embodiment_validation_coverage_rate"] == 1.0
    assert coverage["embodiment_count"] == 6
    assert coverage["complete_embodiment_count"] == 6
    assert coverage["missing_claim_coverage"] == []
    assert coverage["missing_feature_coverage"] == []
    assert coverage["field_claim_upgrade_allowed"] is False
    assert coverage["can_generate_field_evidence"] is False
    assert coverage["can_write_to_actuator"] is False
    assert coverage["can_write_to_release_gate"] is False

    pressure_package = embodiments["TE2_pressure_resolution_route_package_validation"]
    assert "R7_TO_R8P_WORK_PACKAGE_DIR" in pressure_package["source_package_requirements"]
    assert "R8u-28 assembly gate" in pressure_package["validation_gates"]
    assert pressure_package["current_evidence_status"] == "blocked_waiting_for_R7_TO_R8P_WORK_PACKAGE_DIR"
    assert pressure_package["field_claim_upgrade_allowed"] is False

    catalyst = embodiments["TE3_catalyst_activity_proxy_regeneration"]
    assert "催化剂再生" in catalyst["step_sequence"][-1]
    assert "Agent51 field proxy holdout" in catalyst["validation_gates"]
    assert "holdout_mae" in catalyst["acceptance_metrics"]

    for row in embodiments.values():
        missing = [
            field
            for field in REQUIRED_TECHNICAL_EMBODIMENT_FIELDS
            if row.get(field) in (None, "", [])
        ]
        assert missing == []
        assert row["validation_ready_status"] == (
            "embodiment_validation_scaffold_complete_waiting_for_field_evidence"
        )
        assert row["missing_claim_ids"] == []
        assert row["missing_feature_ids"] == []
        assert row["can_generate_field_evidence"] is False
        assert row["can_write_to_actuator"] is False
        assert row["can_write_to_release_gate"] is False


def test_architecture_consolidation_exposes_technical_effect_measurement_matrix() -> None:
    report = AgentArchitectureConsolidationAgent(agent_names=list(AGENT_MODULE_MAP)).run([])

    coverage = report.metrics["technical_effect_measurement_coverage"]
    effects = {
        row["effect_id"]: row
        for row in report.metrics["technical_effect_measurement_matrix"]
    }

    assert coverage["technical_effect_measurement_status"] == (
        "technical_effect_measurement_matrix_ready_not_field_evidence"
    )
    assert coverage["technical_effect_measurement_coverage_rate"] == 1.0
    assert coverage["effect_count"] == 7
    assert coverage["complete_effect_count"] == 7
    assert coverage["missing_embodiment_coverage"] == []
    assert coverage["field_claim_upgrade_allowed"] is False
    assert coverage["can_generate_field_evidence"] is False
    assert coverage["can_write_to_actuator"] is False
    assert coverage["can_write_to_release_gate"] is False

    low_frequency = effects["TEM3_low_frequency_cycle_window_reduces_fast_sensor_need"]
    assert low_frequency["linked_embodiment_ids"] == ["TE5_low_frequency_cycle_window_control"]
    assert "latency_violation_rate" in low_frequency["measurement_metrics"]
    assert "timestamped field replay" in " ".join(low_frequency["acceptance_thresholds"])
    assert "actuator feedback" in low_frequency["validation_gate"]

    catalyst = effects["TEM4_catalyst_proxy_guardrail_effect"]
    assert catalyst["linked_embodiment_ids"] == ["TE3_catalyst_activity_proxy_regeneration"]
    assert "holdout_mae" in catalyst["measurement_metrics"]
    assert "Agent51 field proxy holdout" in catalyst["validation_gate"]
    assert catalyst["can_write_to_actuator"] is False

    release_gate = effects["TEM5_field_replay_protective_writeback_reduces_false_release"]
    assert "pressure_source_conflict_requires_operator_review" in release_gate["measurement_metrics"]
    assert "can_write_to_release_gate must remain false" in " ".join(release_gate["acceptance_thresholds"])
    assert release_gate["can_write_to_release_gate"] is False

    for row in effects.values():
        missing = [
            field
            for field in REQUIRED_TECHNICAL_EFFECT_MEASUREMENT_FIELDS
            if row.get(field) in (None, "", [])
        ]
        assert missing == []
        assert row["measurement_ready_status"] == (
            "technical_effect_measurement_complete_waiting_for_field_evidence"
        )
        assert row["missing_embodiment_ids"] == []
        assert row["missing_claim_ids"] == []
        assert row["missing_feature_ids"] == []
        assert row["field_claim_upgrade_allowed"] is False
        assert row["can_generate_field_evidence"] is False
        assert row["can_write_to_actuator"] is False
        assert row["can_write_to_release_gate"] is False


def test_architecture_consolidation_exposes_prior_art_distinction_matrix() -> None:
    report = AgentArchitectureConsolidationAgent(agent_names=list(AGENT_MODULE_MAP)).run([])

    coverage = report.metrics["prior_art_distinction_coverage"]
    distinctions = {
        row["distinction_id"]: row
        for row in report.metrics["prior_art_distinction_matrix"]
    }

    assert coverage["prior_art_distinction_status"] == (
        "prior_art_distinction_matrix_ready_as_hypothesis_not_search_or_legal_opinion"
    )
    assert coverage["prior_art_distinction_coverage_rate"] == 1.0
    assert coverage["distinction_count"] == 7
    assert coverage["complete_distinction_count"] == 7
    assert coverage["missing_claim_coverage"] == []
    assert coverage["missing_feature_coverage"] == []
    assert coverage["missing_effect_coverage"] == []
    assert coverage["formal_search_required"] is True
    assert coverage["field_claim_upgrade_allowed"] is False
    assert coverage["novelty_or_inventiveness_opinion_allowed"] is False
    assert coverage["legal_status"] == "prior_art_distinction_hypothesis_not_legal_opinion"

    sparse = distinctions["PAD2_sparse_sensor_placement_vs_node_modality_hidden_state_layout"]
    assert "PySensors official repository" in sparse["representative_sources"]
    assert "node-modality" in sparse["distinguishing_combination"]
    assert "catalyst_activity" in sparse["dependent_fallback_path"]
    assert sparse["formal_search_required"] is True

    multi_agent = distinctions["PAD3_marl_pump_coordination_vs_greybox_multi_agent_safety_arbitration"]
    assert "black box" not in multi_agent["distinguishing_combination"].lower()
    assert "灰箱" in multi_agent["distinguishing_combination"]
    assert "not_legal_opinion" in multi_agent["legal_status"]
    assert "field state-action-reward replay" in multi_agent["verification_needed"]

    catalyst = distinctions["PAD6_ai_catalyst_discovery_vs_operational_catalyst_activity_guardrail"]
    assert "Multi-agent AI catalyst discovery reference" in catalyst["representative_sources"][0]
    assert "不是用 AI 发现新催化剂" in catalyst["why_not_generic_ai_or_control"]
    assert "Agent51 field proxy holdout" in catalyst["verification_needed"]

    for row in distinctions.values():
        missing = [
            field
            for field in REQUIRED_PRIOR_ART_DISTINCTION_FIELDS
            if row.get(field) in (None, "", [])
        ]
        assert missing == []
        assert row["distinction_ready_status"] == (
            "prior_art_distinction_complete_waiting_for_formal_search_and_field_evidence"
        )
        assert row["missing_claim_ids"] == []
        assert row["missing_feature_ids"] == []
        assert row["missing_effect_ids"] == []
        assert row["formal_search_required"] is True
        assert row["field_claim_upgrade_allowed"] is False
        assert row["novelty_or_inventiveness_opinion_allowed"] is False
        assert row["can_generate_field_evidence"] is False
        assert row["can_write_to_actuator"] is False
        assert row["can_write_to_release_gate"] is False


def test_architecture_consolidation_exposes_formal_search_work_packages() -> None:
    report = AgentArchitectureConsolidationAgent(agent_names=list(AGENT_MODULE_MAP)).run([])

    coverage = report.metrics["formal_search_work_package_coverage"]
    work_packages = {
        row["work_package_id"]: row
        for row in report.metrics["formal_search_work_package_matrix"]
    }

    assert coverage["formal_search_work_package_status"] == (
        "formal_search_work_packages_ready_not_search_results"
    )
    assert coverage["formal_search_work_package_coverage_rate"] == 1.0
    assert coverage["work_package_count"] == 7
    assert coverage["complete_work_package_count"] == 7
    assert coverage["missing_distinction_coverage"] == []
    assert coverage["formal_search_required"] is True
    assert coverage["formal_search_completed"] is False
    assert coverage["legal_opinion_allowed"] is False
    assert coverage["field_claim_upgrade_allowed"] is False
    assert coverage["can_generate_prior_art_result"] is False
    assert coverage["can_generate_field_evidence"] is False

    sparse = work_packages["FSWP2_node_modality_sparse_hidden_state_search"]
    assert sparse["linked_distinction_ids"] == [
        "PAD2_sparse_sensor_placement_vs_node_modality_hidden_state_layout"
    ]
    assert any("node modality" in query.lower() for query in sparse["english_search_queries"])
    assert any("节点" in query for query in sparse["chinese_search_queries"])
    assert "catalyst_activity" in sparse["claim_fallback_if_prior_art_found"]

    catalyst = work_packages["FSWP6_operational_catalyst_activity_guardrail_search"]
    assert any("catalyst activity" in query.lower() for query in catalyst["english_search_queries"])
    assert "Agent51 field proxy holdout" in catalyst["field_validation_gate_to_preserve"]
    assert catalyst["formal_search_completed"] is False

    release_gate = work_packages["FSWP7_pressure_resolution_protective_release_gate_search"]
    assert "R7_TO_R8P_WORK_PACKAGE_DIR" in release_gate["field_validation_gate_to_preserve"]
    assert any("pressure source conflict" in query.lower() for query in release_gate["english_search_queries"])
    assert "release-block correctness" in release_gate["claim_fallback_if_prior_art_found"]

    for row in work_packages.values():
        missing = [
            field
            for field in REQUIRED_FORMAL_SEARCH_WORK_PACKAGE_FIELDS
            if row.get(field) in (None, "", [])
        ]
        assert missing == []
        assert row["work_package_ready_status"] == (
            "formal_search_work_package_complete_waiting_for_human_or_external_search"
        )
        assert row["missing_distinction_ids"] == []
        assert row["formal_search_required"] is True
        assert row["formal_search_completed"] is False
        assert row["legal_opinion_allowed"] is False
        assert row["field_claim_upgrade_allowed"] is False
        assert row["can_generate_prior_art_result"] is False
        assert row["can_generate_legal_opinion"] is False
        assert row["can_generate_field_evidence"] is False
        assert row["english_search_queries"]
        assert row["chinese_search_queries"]
        assert row["claim_fallback_if_prior_art_found"]


def test_architecture_consolidation_exposes_formal_search_result_intake_schema() -> None:
    report = AgentArchitectureConsolidationAgent(agent_names=list(AGENT_MODULE_MAP)).run([])

    coverage = report.metrics["formal_search_result_intake_coverage"]
    intakes = {
        row["linked_work_package_id"]: row
        for row in report.metrics["formal_search_result_intake_schema"]
    }

    assert coverage["formal_search_result_intake_status"] == (
        "formal_search_result_intake_schema_ready_waiting_for_external_results"
    )
    assert coverage["formal_search_result_intake_coverage_rate"] == 1.0
    assert coverage["intake_count"] == 7
    assert coverage["complete_intake_count"] == 7
    assert coverage["missing_work_package_coverage"] == []
    assert coverage["formal_search_result_supplied"] is False
    assert coverage["accepted_hit_count"] == 0
    assert coverage["can_generate_prior_art_result"] is False
    assert coverage["legal_opinion_allowed"] is False
    assert coverage["field_claim_upgrade_allowed"] is False
    assert coverage["required_hit_table_fields"] == list(PRIOR_ART_HIT_TABLE_FIELDS)
    assert coverage["required_claim_element_comparison_fields"] == list(CLAIM_ELEMENT_COMPARISON_FIELDS)

    catalyst = intakes["FSWP6_operational_catalyst_activity_guardrail_search"]
    assert "FSWP6_operational_catalyst_activity_guardrail_search_prior_art_hit_table.csv_or_json" in catalyst[
        "input_artifacts"
    ]
    assert "matched_query must be one of the english/chinese search queries or a reviewer-approved expansion" in catalyst[
        "acceptance_checks"
    ]
    assert "attempt to set field_claim_upgrade_allowed=true before field validation gates" in catalyst[
        "blocking_conditions"
    ]

    release_gate = intakes["FSWP7_pressure_resolution_protective_release_gate_search"]
    assert "publication_or_patent_id" in release_gate["minimum_evidence_to_accept_hit"]
    assert "discard_claim_route" in release_gate["claim_scope_decision_options"]
    assert "release gate" in release_gate["field_validation_gate_to_preserve"]

    for row in intakes.values():
        missing = [
            field
            for field in REQUIRED_FORMAL_SEARCH_RESULT_INTAKE_FIELDS
            if row.get(field) in (None, "", [])
        ]
        assert missing == []
        assert row["intake_ready_status"] == (
            "formal_search_result_intake_complete_waiting_for_external_search_results"
        )
        assert row["required_hit_table_fields"] == list(PRIOR_ART_HIT_TABLE_FIELDS)
        assert row["required_claim_element_comparison_fields"] == list(CLAIM_ELEMENT_COMPARISON_FIELDS)
        assert row["formal_search_result_supplied"] is False
        assert row["accepted_hit_count"] == 0
        assert row["can_generate_prior_art_result"] is False
        assert row["legal_opinion_allowed"] is False
        assert row["field_claim_upgrade_allowed"] is False
        assert row["mapped_claim_ids"]
        assert row["mapped_feature_ids"]
        assert row["mapped_effect_ids"]


def test_architecture_consolidation_exposes_formal_search_result_validation_gate() -> None:
    report = AgentArchitectureConsolidationAgent(agent_names=list(AGENT_MODULE_MAP)).run([])

    coverage = report.metrics["formal_search_result_validation_gate_coverage"]
    gates = {
        row["linked_work_package_id"]: row
        for row in report.metrics["formal_search_result_validation_gate"]
    }

    assert coverage["formal_search_result_validation_gate_status"] == (
        "formal_search_result_validation_gate_ready_waiting_for_external_result_package"
    )
    assert coverage["formal_search_result_validation_gate_coverage_rate"] == 1.0
    assert coverage["validation_gate_count"] == 7
    assert coverage["complete_validation_gate_count"] == 7
    assert coverage["missing_intake_coverage"] == []
    assert coverage["formal_search_result_package_supplied"] is False
    assert coverage["validated_hit_count"] == 0
    assert coverage["rejected_hit_count"] == 0
    assert coverage["can_generate_prior_art_result"] is False
    assert coverage["legal_opinion_allowed"] is False
    assert coverage["field_claim_upgrade_allowed"] is False
    assert coverage["required_validation_gate_fields"] == list(
        REQUIRED_FORMAL_SEARCH_RESULT_VALIDATION_GATE_FIELDS
    )

    catalyst = gates["FSWP6_operational_catalyst_activity_guardrail_search"]
    assert "Google Patents" in catalyst["allowed_source_databases"]
    assert "reviewer_approved_query_expansion_with_rationale" in catalyst["allowed_query_sources"]
    assert "source_database not in allowed_source_databases" in catalyst["blocking_conditions"]
    assert any(
        "reviewer_boundary" in patch_output
        for patch_output in catalyst["patch_plan_outputs"]
    )

    release_gate = gates["FSWP7_pressure_resolution_protective_release_gate_search"]
    assert "reject reviewer text that asserts legal conclusion, authorization likelihood or field-supported claim" in release_gate[
        "runtime_validation_steps"
    ]
    assert "can_generate_prior_art_result set without accepted hits and human/external review" in release_gate[
        "blocking_conditions"
    ]

    for row in gates.values():
        missing = [
            field
            for field in REQUIRED_FORMAL_SEARCH_RESULT_VALIDATION_GATE_FIELDS
            if row.get(field) in (None, "", [])
        ]
        assert missing == []
        assert row["validation_ready_status"] == (
            "formal_search_result_validation_gate_complete_waiting_for_external_result_package"
        )
        assert row["hit_table_required_fields"] == list(PRIOR_ART_HIT_TABLE_FIELDS)
        assert row["comparison_chart_required_fields"] == list(CLAIM_ELEMENT_COMPARISON_FIELDS)
        assert row["formal_search_result_package_supplied"] is False
        assert row["validated_hit_count"] == 0
        assert row["rejected_hit_count"] == 0
        assert row["can_generate_prior_art_result"] is False
        assert row["legal_opinion_allowed"] is False
        assert row["field_claim_upgrade_allowed"] is False
        assert row["mapped_claim_ids"]
        assert row["mapped_feature_ids"]
        assert row["mapped_effect_ids"]


def test_architecture_consolidation_exposes_formal_search_result_package_template_and_preflight() -> None:
    report = AgentArchitectureConsolidationAgent(agent_names=list(AGENT_MODULE_MAP)).run([])

    coverage = report.metrics["formal_search_result_package_template_coverage"]
    submission_template = report.metrics["formal_search_result_package_submission_template"]
    templates = {
        row["linked_work_package_id"]: row
        for row in report.metrics["formal_search_result_package_template"]
    }
    preflight = report.metrics["formal_search_result_package_source_preflight"]
    row_preflight = report.metrics["formal_search_result_package_row_preflight"]
    validation_execution = report.metrics["formal_search_result_validation_execution"]
    nonlegal_review_packet = report.metrics["formal_search_nonlegal_comparison_review_packet"]
    nonlegal_response_template = report.metrics["formal_search_nonlegal_review_response_template"]
    nonlegal_response_preflight = report.metrics[
        "formal_search_nonlegal_review_response_source_preflight"
    ]
    claim_scope_patch_draft = report.metrics["formal_search_claim_scope_patch_draft"]
    formal_counsel_template = report.metrics["formal_counsel_review_response_template"]
    formal_counsel_preflight = report.metrics[
        "formal_counsel_review_response_source_preflight"
    ]
    disclosure_revision_queue = report.metrics["formal_disclosure_revision_queue"]
    disclosure_revision_impact_plan = report.metrics[
        "formal_disclosure_revision_impact_plan"
    ]
    formal_search_review_readiness = report.metrics["formal_search_review_readiness"]
    formal_search_execution_route_plan = report.metrics[
        "formal_search_execution_route_plan"
    ]

    assert coverage["formal_search_result_package_template_status"] == (
        "formal_search_result_package_templates_ready_waiting_for_submission"
    )
    assert coverage["formal_search_result_package_template_coverage_rate"] == 1.0
    assert coverage["package_template_count"] == 7
    assert coverage["complete_package_template_count"] == 7
    assert coverage["missing_validation_gate_coverage"] == []
    assert coverage["formal_search_result_package_supplied"] is False
    assert coverage["can_route_to_validation_gate"] is False
    assert coverage["can_generate_prior_art_result"] is False
    assert coverage["legal_opinion_allowed"] is False
    assert coverage["field_claim_upgrade_allowed"] is False
    assert coverage["required_package_template_fields"] == list(
        REQUIRED_FORMAL_SEARCH_RESULT_PACKAGE_TEMPLATE_FIELDS
    )
    assert submission_template["submission_template_status"] == (
        "formal_search_result_package_submission_template_ready"
    )
    assert submission_template["submission_template_ready_status"] == (
        "formal_search_result_package_submission_template_complete"
    )
    assert submission_template["expected_env_var"] == "FORMAL_SEARCH_RESULT_PACKAGE_PATH"
    assert submission_template["expected_work_package_ids"] == sorted(templates)
    assert submission_template["required_result_tables"] == [
        "prior_art_hit_table",
        "claim_element_comparison_chart",
        "fallback_claim_scope_recommendation",
    ]
    assert submission_template["can_route_to_validation_gate"] is False
    assert submission_template["can_generate_prior_art_result"] is False
    assert submission_template["legal_opinion_allowed"] is False
    assert submission_template["field_claim_upgrade_allowed"] is False
    assert submission_template["missing_submission_template_fields"] == []
    assert [
        field
        for field in REQUIRED_FORMAL_SEARCH_RESULT_SUBMISSION_TEMPLATE_FIELDS
        if submission_template.get(field) in (None, "", [])
    ] == []

    catalyst = templates["FSWP6_operational_catalyst_activity_guardrail_search"]
    assert catalyst["required_result_tables"] == [
        "prior_art_hit_table",
        "claim_element_comparison_chart",
        "fallback_claim_scope_recommendation",
    ]
    assert "Google Patents" in catalyst["allowed_source_databases"]
    assert "reject TODO/template/sample rows" in catalyst["row_level_rejection_rules"]
    assert "review_boundary_statement" in catalyst["package_manifest_required_fields"]
    assert catalyst["prior_art_hit_table_template_fields"] == list(PRIOR_ART_HIT_TABLE_FIELDS)
    assert catalyst["claim_element_comparison_template_fields"] == list(
        CLAIM_ELEMENT_COMPARISON_FIELDS
    )

    for row in templates.values():
        missing = [
            field
            for field in REQUIRED_FORMAL_SEARCH_RESULT_PACKAGE_TEMPLATE_FIELDS
            if row.get(field) in (None, "", [])
        ]
        assert missing == []
        assert row["package_template_ready_status"] == (
            "formal_search_result_package_template_complete_waiting_for_submission"
        )
        assert row["formal_search_result_package_supplied"] is False
        assert row["can_route_to_validation_gate"] is False
        assert row["can_generate_prior_art_result"] is False
        assert row["legal_opinion_allowed"] is False
        assert row["field_claim_upgrade_allowed"] is False

    assert preflight["formal_search_result_package_source_status"] == (
        "formal_search_result_package_preflight_waiting_for_submission_path"
    )
    assert preflight["expected_env_var"] == "FORMAL_SEARCH_RESULT_PACKAGE_PATH"
    assert preflight["required_root_keys"] == ["package_metadata", "work_package_results"]
    assert preflight["formal_search_result_package_supplied"] is False
    assert preflight["can_route_to_validation_gate"] is False
    assert preflight["can_generate_prior_art_result"] is False
    assert preflight["legal_opinion_allowed"] is False
    assert preflight["field_claim_upgrade_allowed"] is False
    assert preflight["template_marker_gap_count"] == 0
    assert preflight["preflight_blockers"] == ["FORMAL_SEARCH_RESULT_PACKAGE_PATH:not_set"]
    assert row_preflight["formal_search_result_package_row_preflight_status"] == (
        "formal_search_result_package_row_preflight_blocked_at_source_preflight"
    )
    assert row_preflight["source_preflight_status"] == (
        "formal_search_result_package_preflight_waiting_for_submission_path"
    )
    assert row_preflight["can_route_to_validation_gate"] is False
    assert row_preflight["can_generate_prior_art_result"] is False
    assert validation_execution["formal_search_result_validation_execution_status"] == (
        "formal_search_result_validation_execution_blocked_at_row_preflight"
    )
    assert validation_execution["row_preflight_status"] == (
        "formal_search_result_package_row_preflight_blocked_at_source_preflight"
    )
    assert validation_execution["validated_hit_count"] == 0
    assert validation_execution["rejected_hit_count"] == 0
    assert validation_execution["can_enter_human_nonlegal_comparison_review"] is False
    assert validation_execution["can_generate_prior_art_result"] is False
    assert validation_execution["legal_opinion_allowed"] is False
    assert validation_execution["field_claim_upgrade_allowed"] is False
    assert nonlegal_review_packet["formal_search_nonlegal_comparison_review_packet_status"] == (
        "formal_search_nonlegal_review_packet_blocked_at_validation_execution"
    )
    assert nonlegal_review_packet["validation_execution_status"] == (
        "formal_search_result_validation_execution_blocked_at_row_preflight"
    )
    assert nonlegal_review_packet["review_packet_row_count"] == 0
    assert nonlegal_review_packet["human_review_completed"] is False
    assert nonlegal_review_packet["can_enter_human_nonlegal_comparison_review"] is False
    assert nonlegal_review_packet["can_generate_prior_art_result"] is False
    assert nonlegal_review_packet["legal_opinion_allowed"] is False
    assert nonlegal_review_packet["field_claim_upgrade_allowed"] is False
    assert nonlegal_response_template[
        "formal_search_nonlegal_review_response_template_status"
    ] == "formal_search_nonlegal_review_response_template_blocked_at_review_packet"
    assert nonlegal_response_template["expected_env_var"] == (
        "FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH"
    )
    assert nonlegal_response_template["response_template_rows"] == []
    assert nonlegal_response_template["can_route_to_claim_scope_patch_draft"] is False
    assert nonlegal_response_preflight[
        "formal_search_nonlegal_review_response_source_status"
    ] == "formal_search_nonlegal_review_response_preflight_blocked_at_template"
    assert nonlegal_response_preflight["accepted_review_row_count"] == 0
    assert nonlegal_response_preflight["rejected_review_row_count"] == 0
    assert nonlegal_response_preflight["human_review_completed"] is False
    assert nonlegal_response_preflight["can_route_to_claim_scope_patch_draft"] is False
    assert nonlegal_response_preflight["can_generate_prior_art_result"] is False
    assert nonlegal_response_preflight["legal_opinion_allowed"] is False
    assert nonlegal_response_preflight["field_claim_upgrade_allowed"] is False
    assert claim_scope_patch_draft["formal_search_claim_scope_patch_draft_status"] == (
        "formal_search_claim_scope_patch_draft_blocked_at_nonlegal_review_response"
    )
    assert claim_scope_patch_draft["draft_patch_count"] == 0
    assert claim_scope_patch_draft["claim_scope_patch_rows"] == []
    assert claim_scope_patch_draft["can_route_to_formal_counsel_review"] is False
    assert claim_scope_patch_draft["can_emit_claim_text"] is False
    assert claim_scope_patch_draft["can_generate_prior_art_result"] is False
    assert claim_scope_patch_draft["legal_opinion_allowed"] is False
    assert claim_scope_patch_draft["field_claim_upgrade_allowed"] is False
    assert formal_counsel_template["formal_counsel_review_response_template_status"] == (
        "formal_counsel_review_response_template_blocked_at_claim_scope_patch_draft"
    )
    assert formal_counsel_template["response_template_rows"] == []
    assert formal_counsel_template["can_route_to_disclosure_revision_queue"] is False
    assert formal_counsel_template["can_emit_claim_text"] is False
    assert formal_counsel_preflight["formal_counsel_review_response_source_status"] == (
        "formal_counsel_review_response_preflight_blocked_at_template"
    )
    assert formal_counsel_preflight["accepted_formal_review_row_count"] == 0
    assert formal_counsel_preflight["rejected_formal_review_row_count"] == 0
    assert formal_counsel_preflight["external_formal_review_completed"] is False
    assert formal_counsel_preflight["can_route_to_disclosure_revision_queue"] is False
    assert formal_counsel_preflight["can_emit_claim_text"] is False
    assert formal_counsel_preflight["can_generate_prior_art_result"] is False
    assert formal_counsel_preflight["legal_opinion_allowed"] is False
    assert formal_counsel_preflight["field_claim_upgrade_allowed"] is False
    assert disclosure_revision_queue["formal_disclosure_revision_queue_status"] == (
        "formal_disclosure_revision_queue_blocked_at_formal_counsel_review_response"
    )
    assert disclosure_revision_queue["revision_item_count"] == 0
    assert disclosure_revision_queue["disclosure_revision_items"] == []
    assert disclosure_revision_queue["can_route_to_disclosure_editor"] is False
    assert disclosure_revision_queue["can_apply_disclosure_revision_automatically"] is False
    assert disclosure_revision_queue["can_emit_claim_text"] is False
    assert disclosure_revision_queue["can_generate_prior_art_result"] is False
    assert disclosure_revision_queue["legal_opinion_allowed"] is False
    assert disclosure_revision_queue["field_claim_upgrade_allowed"] is False
    assert disclosure_revision_impact_plan[
        "formal_disclosure_revision_impact_plan_status"
    ] == "formal_disclosure_revision_impact_plan_blocked_at_revision_queue"
    assert disclosure_revision_impact_plan["revision_impact_item_count"] == 0
    assert disclosure_revision_impact_plan["revision_impact_items"] == []
    assert disclosure_revision_impact_plan["can_route_to_human_artifact_revision"] is False
    assert disclosure_revision_impact_plan["can_apply_artifact_patch_automatically"] is False
    assert disclosure_revision_impact_plan["can_emit_claim_text"] is False
    assert disclosure_revision_impact_plan["can_generate_prior_art_result"] is False
    assert disclosure_revision_impact_plan["legal_opinion_allowed"] is False
    assert disclosure_revision_impact_plan["field_claim_upgrade_allowed"] is False
    assert formal_search_review_readiness["formal_search_review_readiness_status"] == (
        "formal_search_review_blocked_at_result_package_source_preflight"
    )
    assert formal_search_review_readiness["highest_priority_blocker"] == (
        "FSR_SOURCE_PREFLIGHT"
    )
    assert formal_search_review_readiness["next_operator_action"] == (
        "submit_formal_search_result_package"
    )
    assert formal_search_review_readiness["boundary_violation_count"] == 0
    assert formal_search_review_readiness["can_route_to_validation_gate"] is False
    assert formal_search_review_readiness["can_enter_human_nonlegal_comparison_review"] is False
    assert formal_search_review_readiness["human_nonlegal_review_completed"] is False
    assert formal_search_review_readiness["can_generate_prior_art_result"] is False
    assert formal_search_review_readiness["legal_opinion_allowed"] is False
    assert formal_search_review_readiness["can_emit_claim_text"] is False
    assert formal_search_review_readiness["field_claim_upgrade_allowed"] is False
    assert formal_search_review_readiness["stage_checks"][0]["stage_id"] == (
        "NO_LEGAL_OR_FIELD_CLAIM_BOUNDARY"
    )
    assert formal_search_review_readiness["stage_checks"][0]["passed"] is True
    assert formal_search_execution_route_plan["route_plan_status"] == (
        "formal_search_execution_route_plan_ready_waiting_for_external_search_execution"
    )
    assert formal_search_execution_route_plan["linked_review_highest_priority_blocker"] == (
        "FSR_SOURCE_PREFLIGHT"
    )
    assert formal_search_execution_route_plan["operator_first_action"] == (
        "execute_external_or_human_search_and_submit_FORMAL_SEARCH_RESULT_PACKAGE_PATH"
    )
    assert formal_search_execution_route_plan["route_row_count"] == 7
    assert formal_search_execution_route_plan["complete_route_row_count"] == 7
    assert formal_search_execution_route_plan["can_submit_synthetic_or_template_result_package"] is False
    assert formal_search_execution_route_plan["can_generate_prior_art_result"] is False
    assert formal_search_execution_route_plan["legal_opinion_allowed"] is False
    assert formal_search_execution_route_plan["can_emit_claim_text"] is False
    assert formal_search_execution_route_plan["field_claim_upgrade_allowed"] is False
    for route in formal_search_execution_route_plan["route_rows"]:
        assert route["search_databases"]
        assert route["english_search_queries"] or route["chinese_search_queries"]
        assert route["required_result_tables"] == [
            "prior_art_hit_table",
            "claim_element_comparison_chart",
            "fallback_claim_scope_recommendation",
        ]
        assert route["route_ready_status"] == (
            "formal_search_execution_route_ready_waiting_for_external_search"
        )
        assert route["can_generate_prior_art_result"] is False
        assert "reject TODO/template/sample rows" in route["rejection_boundaries"]


def test_architecture_consolidation_maps_nonlegal_prior_art_seeds_only_as_route_references() -> None:
    seed_matrix = {
        "status": "nonlegal_prior_art_seed_matrix_ready_not_formal_search_result",
        "prior_art_seed_rows": [
            {
                "seed_id": "PA_TEST_SOFT_SENSOR",
                "url": "https://example.test/nonlegal-seed",
                "mapped_project_features": ["PTF2_soft_sensor_grey_state_estimation"],
            }
        ],
    }

    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        nonlegal_prior_art_seed_matrix=seed_matrix,
    ).run([])
    route_plan = report.metrics["formal_search_execution_route_plan"]

    assert route_plan["nonlegal_prior_art_seed_matrix_status"] == (
        "nonlegal_prior_art_seed_matrix_ready_not_formal_search_result"
    )
    assert route_plan["mapped_seed_route_count"] >= 1
    matched_routes = [
        route
        for route in route_plan["route_rows"]
        if "PA_TEST_SOFT_SENSOR" in route["mapped_nonlegal_seed_ids"]
    ]
    assert matched_routes
    for route in matched_routes:
        assert route["seed_mapping_status"] == "nonlegal_prior_art_seed_references_available"
        assert route["can_generate_prior_art_result"] is False
        assert route["legal_opinion_allowed"] is False
        assert route["field_claim_upgrade_allowed"] is False


def test_architecture_consolidation_rejects_submission_template_as_prior_art_package(tmp_path) -> None:
    report = AgentArchitectureConsolidationAgent(agent_names=list(AGENT_MODULE_MAP)).run([])
    template_path = tmp_path / "formal_search_submission_template.json"
    template_path.write_text(
        json.dumps(report.metrics["formal_search_result_package_submission_template"], ensure_ascii=False),
        encoding="utf-8",
    )

    replay = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        formal_search_result_package_path=str(template_path),
    ).run([])
    preflight = replay.metrics["formal_search_result_package_source_preflight"]

    assert preflight["formal_search_result_package_source_status"] == (
        "formal_search_result_package_failed_template_marker_preflight"
    )
    assert preflight["formal_search_result_package_supplied"] is True
    assert preflight["can_route_to_validation_gate"] is False
    assert preflight["can_generate_prior_art_result"] is False
    assert preflight["legal_opinion_allowed"] is False
    assert preflight["field_claim_upgrade_allowed"] is False
    assert preflight["template_marker_gap_count"] > 0
    assert "template_marker_preflight:template_or_todo_values_present" in preflight[
        "preflight_blockers"
    ]


def test_architecture_consolidation_routes_valid_search_result_package_to_validation_gate(tmp_path) -> None:
    report = AgentArchitectureConsolidationAgent(agent_names=list(AGENT_MODULE_MAP)).run([])
    package_templates = report.metrics["formal_search_result_package_template"]
    work_package_results = {}
    for index, template in enumerate(package_templates, start=1):
        work_package_id = template["linked_work_package_id"]
        hit_id = f"HIT_{index}"
        mapped_element = (
            template["mapped_claim_ids"][0]
            if template["mapped_claim_ids"]
            else template["mapped_feature_ids"][0]
        )
        work_package_results[work_package_id] = {
            "package_manifest": {
                "package_id": f"PKG_{index}",
                "linked_work_package_id": work_package_id,
                "search_executor": "external_searcher",
                "search_date": "2026-06-04",
                "databases_searched": [template["allowed_source_databases"][0]],
                "query_log": [template["allowed_query_sources"][0]],
                "reviewer_id": "reviewer_A",
                "review_time": "2026-06-04T00:00:00Z",
                "review_boundary_statement": "Comparison record only; no authorization or field claim asserted.",
                "legal_status": "not_legal_opinion",
            },
            "prior_art_hit_table": [
                {
                    "hit_id": hit_id,
                    "linked_work_package_id": work_package_id,
                    "source_database": template["allowed_source_databases"][0],
                    "publication_or_patent_id": f"PUB_{index}",
                    "title": f"External comparison record {index}",
                    "assignee_or_authors": "external authors",
                    "publication_date": "2024-01-01",
                    "url_or_reference": f"https://example.org/prior-art/{index}",
                    "matched_query": template["allowed_query_sources"][0],
                    "matched_claim_elements": [mapped_element],
                    "disclosed_capabilities": "partial wastewater monitoring or control capability",
                    "missing_project_elements": "does not disclose the full cyclic greybox evidence-gated chain",
                    "overlap_level": "partial",
                    "novelty_risk_signal": "risk_signal_only",
                    "combination_risk_signal": "combination_review_needed",
                    "reviewer_id": "reviewer_A",
                    "review_status": "reviewed_for_structural_comparison_only",
                    "legal_status": "not_legal_opinion",
                }
            ],
            "claim_element_comparison_chart": [
                {
                    "comparison_id": f"CMP_{index}",
                    "linked_hit_id": hit_id,
                    "linked_work_package_id": work_package_id,
                    "claim_or_feature_element": mapped_element,
                    "project_element_text": "project element under comparison",
                    "prior_art_disclosure_text": "prior art describes a partial related capability",
                    "match_level": "partial",
                    "missing_or_distinguishing_detail": "missing full low-cost cyclic greybox validation gate linkage",
                    "fallback_claim_scope_impact": "retain dependent fallback pending formal review",
                    "field_validation_gate_to_preserve": "field replay and operator review gate",
                    "reviewer_decision": "comparison_record_only",
                    "legal_status": "not_legal_opinion",
                }
            ],
            "fallback_claim_scope_recommendation": [
                {
                    "linked_work_package_id": work_package_id,
                    "claim_scope_decision_option": "retain_candidate_scope_pending_formal_review",
                    "decision_rationale": "comparison-only record keeps validation gates intact",
                    "triggering_hit_ids": [hit_id],
                    "preserved_field_validation_gate": "field replay and operator review gate",
                    "reviewer_id": "reviewer_A",
                    "legal_status": "not_legal_opinion",
                }
            ],
        }
    package_path = tmp_path / "formal_search_result_package.json"
    package_path.write_text(
        json.dumps(
            {
                "package_metadata": {
                    "package_id": "PKG_FORMAL_SEARCH_TEST",
                    "package_type": "formal_search_result_package",
                    "search_executor": "external_searcher",
                    "search_date": "2026-06-04",
                    "reviewer_id": "reviewer_A",
                    "review_time": "2026-06-04T00:00:00Z",
                    "review_boundary_statement": "Comparison record only; no authorization or field claim asserted.",
                    "legal_status": "not_legal_opinion",
                },
                "work_package_results": work_package_results,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    replay = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        formal_search_result_package_path=str(package_path),
    ).run([])
    source_preflight = replay.metrics["formal_search_result_package_source_preflight"]
    row_preflight = replay.metrics["formal_search_result_package_row_preflight"]
    validation_execution = replay.metrics["formal_search_result_validation_execution"]
    nonlegal_review_packet = replay.metrics["formal_search_nonlegal_comparison_review_packet"]
    nonlegal_response_template = replay.metrics["formal_search_nonlegal_review_response_template"]
    nonlegal_response_preflight = replay.metrics[
        "formal_search_nonlegal_review_response_source_preflight"
    ]
    claim_scope_patch_draft = replay.metrics["formal_search_claim_scope_patch_draft"]
    formal_counsel_template = replay.metrics["formal_counsel_review_response_template"]
    formal_counsel_preflight = replay.metrics[
        "formal_counsel_review_response_source_preflight"
    ]
    disclosure_revision_queue = replay.metrics["formal_disclosure_revision_queue"]
    disclosure_revision_impact_plan = replay.metrics[
        "formal_disclosure_revision_impact_plan"
    ]
    formal_search_review_readiness = replay.metrics["formal_search_review_readiness"]

    assert source_preflight["formal_search_result_package_source_status"] == (
        "formal_search_result_package_source_ready_for_validation_gate"
    )
    assert source_preflight["can_route_to_validation_gate"] is True
    assert source_preflight["template_marker_gap_count"] == 0
    assert row_preflight["formal_search_result_package_row_preflight_status"] == (
        "formal_search_result_package_row_preflight_ready_for_validation_gate"
    )
    assert row_preflight["checked_work_package_count"] == 7
    assert row_preflight["checked_hit_row_count"] == 7
    assert row_preflight["checked_comparison_row_count"] == 7
    assert row_preflight["checked_fallback_row_count"] == 7
    assert row_preflight["structurally_valid_hit_row_count"] == 7
    assert row_preflight["row_gap_count"] == 0
    assert row_preflight["comparison_coverage_gap_count"] == 0
    assert row_preflight["forbidden_review_boundary_count"] == 0
    assert row_preflight["can_route_to_validation_gate"] is True
    assert row_preflight["can_generate_prior_art_result"] is False
    assert row_preflight["legal_opinion_allowed"] is False
    assert row_preflight["field_claim_upgrade_allowed"] is False
    assert validation_execution["formal_search_result_validation_execution_status"] == (
        "formal_search_result_validation_execution_ready_for_human_nonlegal_comparison_review"
    )
    assert validation_execution["formal_search_result_package_supplied"] is True
    assert validation_execution["work_package_execution_count"] == 7
    assert validation_execution["execution_row_count"] == 7
    assert validation_execution["validated_hit_count"] == 7
    assert validation_execution["rejected_hit_count"] == 0
    assert validation_execution["comparison_row_count"] == 7
    assert validation_execution["fallback_row_count"] == 7
    assert validation_execution["execution_patch_plan"] == []
    assert validation_execution["can_enter_human_nonlegal_comparison_review"] is True
    assert validation_execution["can_generate_prior_art_result"] is False
    assert validation_execution["legal_opinion_allowed"] is False
    assert validation_execution["field_claim_upgrade_allowed"] is False
    assert nonlegal_review_packet["formal_search_nonlegal_comparison_review_packet_status"] == (
        "formal_search_nonlegal_review_packet_ready_waiting_for_human_review"
    )
    assert nonlegal_review_packet["review_packet_row_count"] == 7
    assert len(nonlegal_review_packet["review_packet_rows"]) == 7
    assert nonlegal_review_packet["review_packet_patch_plan"] == []
    assert nonlegal_review_packet["human_review_completed"] is False
    assert nonlegal_review_packet["can_enter_human_nonlegal_comparison_review"] is True
    assert nonlegal_review_packet["can_generate_prior_art_result"] is False
    assert nonlegal_review_packet["legal_opinion_allowed"] is False
    assert nonlegal_review_packet["field_claim_upgrade_allowed"] is False
    for review_row in nonlegal_review_packet["review_packet_rows"]:
        assert review_row["review_packet_row_status"] == (
            "ready_for_human_nonlegal_technical_comparison"
        )
        assert review_row["hit_id"]
        assert review_row["covered_project_element_ids"]
        assert "distinguishing_technical_detail" in review_row["required_reviewer_fields"]
        assert "cannot assert novelty or inventiveness" in review_row["cannot_do"]
    assert nonlegal_response_template[
        "formal_search_nonlegal_review_response_template_status"
    ] == "formal_search_nonlegal_review_response_template_ready_waiting_for_human_submission"
    assert len(nonlegal_response_template["expected_review_packet_row_ids"]) == 7
    assert len(nonlegal_response_template["response_template_rows"]) == 7
    assert nonlegal_response_template["human_review_completed"] is False
    assert nonlegal_response_preflight[
        "formal_search_nonlegal_review_response_source_status"
    ] == "formal_search_nonlegal_review_response_preflight_waiting_for_submission_path"
    assert nonlegal_response_preflight["accepted_review_row_count"] == 0
    assert nonlegal_response_preflight["human_review_completed"] is False
    assert nonlegal_response_preflight["can_route_to_claim_scope_patch_draft"] is False
    assert claim_scope_patch_draft["formal_search_claim_scope_patch_draft_status"] == (
        "formal_search_claim_scope_patch_draft_blocked_at_nonlegal_review_response"
    )
    assert claim_scope_patch_draft["draft_patch_count"] == 0
    assert claim_scope_patch_draft["can_route_to_formal_counsel_review"] is False
    assert claim_scope_patch_draft["can_emit_claim_text"] is False
    assert formal_counsel_template["formal_counsel_review_response_template_status"] == (
        "formal_counsel_review_response_template_blocked_at_claim_scope_patch_draft"
    )
    assert formal_counsel_preflight["formal_counsel_review_response_source_status"] == (
        "formal_counsel_review_response_preflight_blocked_at_template"
    )
    assert formal_counsel_preflight["can_route_to_disclosure_revision_queue"] is False
    assert disclosure_revision_queue["formal_disclosure_revision_queue_status"] == (
        "formal_disclosure_revision_queue_blocked_at_formal_counsel_review_response"
    )
    assert disclosure_revision_queue["revision_item_count"] == 0
    assert disclosure_revision_impact_plan[
        "formal_disclosure_revision_impact_plan_status"
    ] == "formal_disclosure_revision_impact_plan_blocked_at_revision_queue"
    assert disclosure_revision_impact_plan["revision_impact_item_count"] == 0
    assert disclosure_revision_impact_plan["can_route_to_human_artifact_revision"] is False
    assert formal_search_review_readiness["formal_search_review_readiness_status"] == (
        "formal_search_review_ready_for_human_nonlegal_comparison"
    )
    assert formal_search_review_readiness["highest_priority_blocker"] == (
        "FSR_NONLEGAL_REVIEW_RESPONSE"
    )
    assert formal_search_review_readiness["next_operator_action"] == (
        "complete_human_nonlegal_comparison_review_response"
    )
    assert formal_search_review_readiness["blocking_stage_count"] == 5
    assert formal_search_review_readiness["boundary_violation_count"] == 0
    assert formal_search_review_readiness["can_route_to_validation_gate"] is True
    assert formal_search_review_readiness["can_enter_human_nonlegal_comparison_review"] is True
    assert formal_search_review_readiness["human_nonlegal_review_completed"] is False
    assert formal_search_review_readiness["can_route_to_claim_scope_patch_draft"] is False
    assert formal_search_review_readiness["can_generate_prior_art_result"] is False
    assert formal_search_review_readiness["legal_opinion_allowed"] is False
    assert formal_search_review_readiness["can_emit_claim_text"] is False
    assert formal_search_review_readiness["field_claim_upgrade_allowed"] is False

    ai_draft_response_path = tmp_path / "formal_search_nonlegal_review_ai_draft.json"
    ai_draft_response_path.write_text(
        json.dumps(
            {
                "review_metadata": {
                    "response_package_id": "NONLEGAL_REVIEW_AI_DRAFT_TEST",
                    "reviewer_id": "ai_assistant",
                    "reviewer_role": "ai_assisted_nonlegal_draft",
                    "review_time": "2026-06-04T00:30:00Z",
                    "evidence_boundary_acknowledgement": (
                        "AI draft only; human nonlegal review has not completed."
                    ),
                    "legal_status": "ai_draft_not_legal_opinion",
                },
                "review_rows": [
                    {
                        "review_packet_row_id": row["review_packet_row_id"],
                        "linked_work_package_id": row["linked_work_package_id"],
                        "hit_id": row["hit_id"],
                        "reviewer_id": "ai_assistant",
                        "reviewer_role": "ai_assisted_nonlegal_draft",
                        "review_time": "2026-06-04T00:30:00Z",
                        "nonlegal_overlap_assessment": "AI draft: partial technical overlap",
                        "distinguishing_technical_detail": (
                            "AI draft: missing cyclic greybox evidence-gated control chain"
                        ),
                        "fallback_scope_recommendation": (
                            "AI draft: retain candidate scope pending human review"
                        ),
                        "preserved_field_validation_gate": "field replay, holdout and operator review",
                        "evidence_boundary_acknowledgement": (
                            "AI-generated draft only; not a completed human review"
                        ),
                        "reviewer_signature_or_trace_id": f"AI_DRAFT_TRACE_{index}",
                        "legal_status": "ai_draft_not_legal_opinion",
                    }
                    for index, row in enumerate(
                        nonlegal_review_packet["review_packet_rows"], start=1
                    )
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    ai_draft_replay = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        formal_search_result_package_path=str(package_path),
        formal_search_nonlegal_review_response_path=str(ai_draft_response_path),
    ).run([])
    ai_draft_preflight = ai_draft_replay.metrics[
        "formal_search_nonlegal_review_response_source_preflight"
    ]
    ai_draft_claim_scope_patch = ai_draft_replay.metrics[
        "formal_search_claim_scope_patch_draft"
    ]
    assert ai_draft_preflight["formal_search_nonlegal_review_response_source_status"] == (
        "formal_search_nonlegal_review_response_failed_preflight"
    )
    assert ai_draft_preflight["human_review_completed"] is False
    assert ai_draft_preflight["can_route_to_claim_scope_patch_draft"] is False
    assert ai_draft_preflight["ai_draft_boundary_gap_count"] == 8
    assert "ai_draft_boundary_count=8" in ai_draft_preflight["preflight_blockers"]
    assert {
        "scope": "review_metadata",
        "issue": "ai_draft_cannot_satisfy_human_nonlegal_review",
        "fields": ["reviewer_role", "legal_status"],
    } in ai_draft_preflight["ai_draft_boundary_gaps"]
    assert ai_draft_claim_scope_patch["formal_search_claim_scope_patch_draft_status"] == (
        "formal_search_claim_scope_patch_draft_blocked_at_nonlegal_review_response"
    )

    review_response_path = tmp_path / "formal_search_nonlegal_review_response.json"
    review_response_path.write_text(
        json.dumps(
            {
                "review_metadata": {
                    "response_package_id": "NONLEGAL_REVIEW_RESPONSE_TEST",
                    "reviewer_id": "reviewer_A",
                    "review_time": "2026-06-04T01:00:00Z",
                    "evidence_boundary_acknowledgement": (
                        "Nonlegal technical comparison only; field and formal counsel gates preserved."
                    ),
                    "legal_status": "not_legal_opinion",
                },
                "review_rows": [
                    {
                        "review_packet_row_id": row["review_packet_row_id"],
                        "linked_work_package_id": row["linked_work_package_id"],
                        "hit_id": row["hit_id"],
                        "reviewer_id": "reviewer_A",
                        "review_time": "2026-06-04T01:00:00Z",
                        "nonlegal_overlap_assessment": "partial technical overlap",
                        "distinguishing_technical_detail": (
                            "missing cyclic greybox low-cost sensing validation and gate chain"
                        ),
                        "fallback_scope_recommendation": (
                            "retain candidate scope pending formal counsel and field validation"
                        ),
                        "preserved_field_validation_gate": "field replay, holdout and operator review",
                        "evidence_boundary_acknowledgement": (
                            "nonlegal technical review only; not field evidence"
                        ),
                        "reviewer_signature_or_trace_id": f"TRACE_{index}",
                        "legal_status": "not_legal_opinion",
                    }
                    for index, row in enumerate(
                        nonlegal_review_packet["review_packet_rows"], start=1
                    )
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    reviewed = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        formal_search_result_package_path=str(package_path),
        formal_search_nonlegal_review_response_path=str(review_response_path),
    ).run([])
    reviewed_preflight = reviewed.metrics[
        "formal_search_nonlegal_review_response_source_preflight"
    ]
    reviewed_claim_scope_patch = reviewed.metrics["formal_search_claim_scope_patch_draft"]
    reviewed_formal_counsel_template = reviewed.metrics[
        "formal_counsel_review_response_template"
    ]
    reviewed_formal_counsel_preflight = reviewed.metrics[
        "formal_counsel_review_response_source_preflight"
    ]
    reviewed_formal_search_readiness = reviewed.metrics["formal_search_review_readiness"]
    assert reviewed_preflight["formal_search_nonlegal_review_response_source_status"] == (
        "formal_search_nonlegal_review_response_ready_for_claim_scope_patch_draft"
    )
    assert reviewed_preflight["accepted_review_row_count"] == 7
    assert reviewed_preflight["rejected_review_row_count"] == 0
    assert reviewed_preflight["review_response_gap_count"] == 0
    assert reviewed_preflight["forbidden_review_boundary_count"] == 0
    assert reviewed_preflight["template_marker_gap_count"] == 0
    assert reviewed_preflight["human_review_completed"] is True
    assert reviewed_preflight["can_route_to_claim_scope_patch_draft"] is True
    assert reviewed_preflight["can_generate_prior_art_result"] is False
    assert reviewed_preflight["legal_opinion_allowed"] is False
    assert reviewed_preflight["field_claim_upgrade_allowed"] is False
    assert len(reviewed_preflight["accepted_review_rows"]) == 7
    assert reviewed_claim_scope_patch["formal_search_claim_scope_patch_draft_status"] == (
        "formal_search_claim_scope_patch_draft_ready_for_formal_counsel_review"
    )
    assert reviewed_claim_scope_patch["draft_patch_count"] == 7
    assert len(reviewed_claim_scope_patch["claim_scope_patch_rows"]) == 7
    assert reviewed_claim_scope_patch["can_route_to_formal_counsel_review"] is True
    assert reviewed_claim_scope_patch["can_emit_claim_text"] is False
    assert reviewed_claim_scope_patch["can_generate_prior_art_result"] is False
    assert reviewed_claim_scope_patch["legal_opinion_allowed"] is False
    assert reviewed_claim_scope_patch["field_claim_upgrade_allowed"] is False
    for patch_row in reviewed_claim_scope_patch["claim_scope_patch_rows"]:
        assert patch_row["patch_status"] == "draft_only_waiting_for_formal_counsel_review"
        assert patch_row["required_next_review"] == "formal_patent_counsel_review_required"
        assert patch_row["distinguishing_technical_detail"]
        assert patch_row["preserved_field_validation_gate"]
        assert "cannot_emit_claim_text" in patch_row["cannot_do"]
        assert "cannot_assert_novelty_or_inventiveness" in patch_row["cannot_do"]
    assert reviewed_formal_counsel_template["formal_counsel_review_response_template_status"] == (
        "formal_counsel_review_response_template_ready_waiting_for_external_formal_review"
    )
    assert len(reviewed_formal_counsel_template["expected_claim_scope_patch_ids"]) == 7
    assert len(reviewed_formal_counsel_template["response_template_rows"]) == 7
    assert reviewed_formal_counsel_preflight[
        "formal_counsel_review_response_source_status"
    ] == "formal_counsel_review_response_preflight_waiting_for_submission_path"
    assert reviewed_formal_counsel_preflight["accepted_formal_review_row_count"] == 0
    assert reviewed_formal_counsel_preflight["external_formal_review_completed"] is False
    assert reviewed_formal_counsel_preflight[
        "can_route_to_disclosure_revision_queue"
    ] is False
    assert reviewed_formal_search_readiness["formal_search_review_readiness_status"] == (
        "formal_search_review_ready_for_external_formal_counsel_review"
    )
    assert reviewed_formal_search_readiness["highest_priority_blocker"] == (
        "FSR_FORMAL_COUNSEL_RESPONSE"
    )
    assert reviewed_formal_search_readiness["next_operator_action"] == (
        "complete_external_formal_counsel_review_response"
    )
    assert reviewed_formal_search_readiness["can_route_to_claim_scope_patch_draft"] is True
    assert reviewed_formal_search_readiness["can_route_to_formal_counsel_review"] is True
    assert reviewed_formal_search_readiness["external_formal_review_completed"] is False
    assert reviewed_formal_search_readiness["can_emit_claim_text"] is False

    formal_response_path = tmp_path / "formal_counsel_review_response.json"
    formal_response_path.write_text(
        json.dumps(
            {
                "review_metadata": {
                    "response_package_id": "FORMAL_COUNSEL_RESPONSE_TEST",
                    "formal_reviewer_id": "formal_reviewer_A",
                    "review_time": "2026-06-04T02:00:00Z",
                    "boundary_acknowledgement": (
                        "External formal review routing record only; system must preserve field gates."
                    ),
                    "legal_status": "external_review_record_not_system_opinion",
                },
                "review_rows": [
                    {
                        "claim_scope_patch_id": row["claim_scope_patch_id"],
                        "review_packet_row_id": row["review_packet_row_id"],
                        "linked_work_package_id": row["linked_work_package_id"],
                        "hit_id": row["hit_id"],
                        "formal_reviewer_id": "formal_reviewer_A",
                        "review_time": "2026-06-04T02:00:00Z",
                        "scope_review_disposition": "retain pending disclosure revision",
                        "approved_technical_revision_summary": (
                            "keep technical distinction around cyclic greybox gate chain"
                        ),
                        "required_disclosure_revision": (
                            "add implementation detail and validation boundary notes"
                        ),
                        "preserved_field_validation_gate": row["preserved_field_validation_gate"],
                        "required_followup_search_or_evidence": "no additional source in this test fixture",
                        "boundary_acknowledgement": (
                            "routing record only; no system-generated claim text or field conclusion"
                        ),
                        "formal_review_trace_id": f"FORMAL_TRACE_{index}",
                        "legal_status": "external_review_record_not_system_opinion",
                    }
                    for index, row in enumerate(
                        reviewed_claim_scope_patch["claim_scope_patch_rows"],
                        start=1,
                    )
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    formal_reviewed = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        formal_search_result_package_path=str(package_path),
        formal_search_nonlegal_review_response_path=str(review_response_path),
        formal_counsel_review_response_path=str(formal_response_path),
    ).run([])
    formal_preflight = formal_reviewed.metrics[
        "formal_counsel_review_response_source_preflight"
    ]
    formal_revision_queue = formal_reviewed.metrics["formal_disclosure_revision_queue"]
    formal_revision_impact_plan = formal_reviewed.metrics[
        "formal_disclosure_revision_impact_plan"
    ]
    formal_reviewed_readiness = formal_reviewed.metrics["formal_search_review_readiness"]
    assert formal_preflight["formal_counsel_review_response_source_status"] == (
        "formal_counsel_review_response_ready_for_disclosure_revision_queue"
    )
    assert formal_preflight["accepted_formal_review_row_count"] == 7
    assert formal_preflight["rejected_formal_review_row_count"] == 0
    assert formal_preflight["formal_review_gap_count"] == 0
    assert formal_preflight["forbidden_formal_review_boundary_count"] == 0
    assert formal_preflight["template_marker_gap_count"] == 0
    assert formal_preflight["external_formal_review_completed"] is True
    assert formal_preflight["can_route_to_disclosure_revision_queue"] is True
    assert formal_preflight["can_emit_claim_text"] is False
    assert formal_preflight["can_generate_prior_art_result"] is False
    assert formal_preflight["legal_opinion_allowed"] is False
    assert formal_preflight["field_claim_upgrade_allowed"] is False
    assert len(formal_preflight["accepted_formal_review_rows"]) == 7
    assert formal_revision_queue["formal_disclosure_revision_queue_status"] == (
        "formal_disclosure_revision_queue_ready_for_human_disclosure_editor"
    )
    assert formal_revision_queue["revision_item_count"] == 7
    assert len(formal_revision_queue["disclosure_revision_items"]) == 7
    assert formal_revision_queue["can_route_to_disclosure_editor"] is True
    assert formal_revision_queue["can_apply_disclosure_revision_automatically"] is False
    assert formal_revision_queue["can_emit_claim_text"] is False
    assert formal_revision_queue["can_generate_prior_art_result"] is False
    assert formal_revision_queue["legal_opinion_allowed"] is False
    assert formal_revision_queue["field_claim_upgrade_allowed"] is False
    for revision_item in formal_revision_queue["disclosure_revision_items"]:
        assert revision_item["revision_status"] == "queued_for_human_disclosure_editor"
        assert revision_item["required_disclosure_revision"]
        assert revision_item["preserved_field_validation_gate"]
        assert "cannot_apply_revision_automatically" in revision_item["cannot_do"]
        assert "cannot_emit_claim_text" in revision_item["cannot_do"]
    assert formal_revision_impact_plan[
        "formal_disclosure_revision_impact_plan_status"
    ] == "formal_disclosure_revision_impact_plan_ready_for_human_artifact_revision"
    assert formal_reviewed_readiness["formal_search_review_readiness_status"] == (
        "formal_search_review_ready_for_human_disclosure_revision"
    )
    assert formal_reviewed_readiness["highest_priority_blocker"] == "NONE"
    assert formal_reviewed_readiness["blocking_stage_count"] == 0
    assert formal_reviewed_readiness["next_operator_action"] == (
        "perform_human_disclosure_revision_against_impact_plan"
    )
    assert formal_reviewed_readiness["external_formal_review_completed"] is True
    assert formal_reviewed_readiness["can_route_to_disclosure_editor"] is True
    assert formal_reviewed_readiness["can_route_to_human_artifact_revision"] is True
    assert formal_reviewed_readiness["can_generate_prior_art_result"] is False
    assert formal_reviewed_readiness["legal_opinion_allowed"] is False
    assert formal_reviewed_readiness["can_emit_claim_text"] is False
    assert formal_reviewed_readiness["field_claim_upgrade_allowed"] is False
    assert formal_revision_impact_plan["revision_impact_item_count"] == 7
    assert len(formal_revision_impact_plan["revision_impact_items"]) == 7
    assert formal_revision_impact_plan["can_route_to_human_artifact_revision"] is True
    assert formal_revision_impact_plan["can_apply_artifact_patch_automatically"] is False
    assert formal_revision_impact_plan["can_emit_claim_text"] is False
    assert formal_revision_impact_plan["can_generate_prior_art_result"] is False
    assert formal_revision_impact_plan["legal_opinion_allowed"] is False
    assert formal_revision_impact_plan["field_claim_upgrade_allowed"] is False
    for impact_item in formal_revision_impact_plan["revision_impact_items"]:
        assert impact_item["impact_status"] == (
            "impact_plan_waiting_for_human_artifact_revision"
        )
        assert "technical_claim_skeleton_scaffold" in impact_item["target_artifacts"]
        assert "patent_technical_feature_ledger" in impact_item["target_artifacts"]
        assert impact_item["human_revision_steps"]
        assert impact_item["verification_before_acceptance"]
        assert "cannot_apply_artifact_patch_automatically" in impact_item["cannot_do"]
        assert "cannot_emit_claim_text" in impact_item["cannot_do"]
        assert "cannot_generate_prior_art_result" in impact_item["cannot_do"]


def test_architecture_consolidation_freezes_presentation_agents() -> None:
    report = AgentArchitectureConsolidationAgent(agent_names=list(AGENT_MODULE_MAP)).run([])

    presentation_rows = [
        row for row in report.metrics["agent_audit_table"] if row["module_id"] == "M9_presentation_delivery"
    ]
    presentation_spine = [
        row for row in report.metrics["system_spine_map"] if row["module_id"] == "M9_presentation_delivery"
    ][0]

    assert {row["agent_name"] for row in presentation_rows} == {
        "deliverable_organization_agent",
        "presentation_asset_agent",
        "presentation_deck_agent",
    }
    assert all(row["retention_decision"] == "freeze_low_priority" for row in presentation_rows)
    assert report.metrics["presentation_freeze_agent_count"] == 3
    assert presentation_spine["primary_layer"] == "OUTSIDE_MODEL_SPINE"
    assert presentation_spine["spine_policy"] == "freeze_outside_model_spine"
    assert presentation_spine["is_inside_model_spine"] is False
    assert any(issue.issue_type == "presentation_agents_frozen" for issue in report.issues)


def test_architecture_consolidation_keeps_current_core_anchor_agents() -> None:
    report = AgentArchitectureConsolidationAgent(agent_names=list(AGENT_MODULE_MAP)).run([])
    rows_by_name = {row["agent_name"]: row for row in report.metrics["agent_audit_table"]}

    for agent_name in CORE_ANCHOR_AGENTS:
        assert rows_by_name[agent_name]["is_core_anchor"] is True
        assert rows_by_name[agent_name]["module_id"] != "M9_presentation_delivery"
        assert "核心" in rows_by_name[agent_name]["model_core_contribution"]


def test_architecture_consolidation_identifies_evidence_and_project_ops_redundancy_clusters() -> None:
    report = AgentArchitectureConsolidationAgent(agent_names=list(AGENT_MODULE_MAP)).run([])
    clusters = {cluster["cluster_id"]: cluster for cluster in report.metrics["redundancy_clusters"]}

    assert "C2_field_evidence_claim_gate_cluster" in clusters
    assert "claim_specific_field_package_agent" in clusters["C2_field_evidence_claim_gate_cluster"]["agents"]
    assert "field_validation_queue_alignment_agent" in clusters["C2_field_evidence_claim_gate_cluster"]["agents"]
    assert "C3_project_operations_cluster" in clusters
    assert "replanning_orchestrator_agent" in clusters["C3_project_operations_cluster"]["agents"]
    assert report.metrics["redundancy_cluster_count"] >= 5


def test_architecture_consolidation_ranks_field_evidence_merge_ahead_of_presentation_freeze() -> None:
    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        core_metrics={
            "claim_specific_field_package_metrics": {
                "readiness": {
                    "source_basis_completion_rate": 0.45,
                }
            }
        },
    ).run([])
    actions = report.metrics["ranked_refactor_actions"]

    assert actions[0]["action_id"] == "R1_unify_field_evidence_and_source_basis_gate"
    assert actions[0]["marginal_value_score"] > actions[-1]["marginal_value_score"]
    assert actions[-1]["action_id"] == "R4_freeze_presentation_and_compress_project_ops"
    assert report.metrics["self_interrupt_verdict"] == "continue_core_architecture_consolidation"


def test_architecture_consolidation_moves_to_source_basis_detail_after_unified_gate_exists() -> None:
    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        core_metrics={
            "unified_field_evidence_gate_metrics": {
                "readiness": {
                    "unified_field_evidence_gate_status": "unified_gate_ready_blocking_field_claim_upgrade",
                    "gate_source_consolidation_coverage": 1.0,
                    "source_basis_completion_rate": 0.45,
                }
            }
        },
    ).run([])

    assert report.metrics["ranked_refactor_actions"][0]["action_id"] == (
        "R1b_source_basis_detail_completion_inside_unified_gate"
    )
    assert "source_basis" in report.metrics["ranked_refactor_actions"][0]["title"]


def test_architecture_consolidation_moves_to_observation_contract_when_source_basis_detail_ready() -> None:
    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        core_metrics={
            "unified_field_evidence_gate_metrics": {
                "readiness": {
                    "unified_field_evidence_gate_status": "unified_gate_ready_blocking_field_claim_upgrade",
                    "gate_source_consolidation_coverage": 1.0,
                    "source_basis_completion_rate": 0.45,
                    "citation_detail_completion_rate": 1.0,
                    "source_basis_parameter_boundary_coverage": 1.0,
                }
            }
        },
    ).run([])

    assert report.metrics["ranked_refactor_actions"][0]["action_id"] == (
        "R2_agent48_51_54_observation_contract_merge"
    )
    assert "观测" in report.metrics["ranked_refactor_actions"][0]["title"]


def test_architecture_consolidation_moves_to_replay_after_observation_contract_ready() -> None:
    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        core_metrics={
            "unified_field_evidence_gate_metrics": {
                "readiness": {
                    "unified_field_evidence_gate_status": "unified_gate_ready_blocking_field_claim_upgrade",
                    "gate_source_consolidation_coverage": 1.0,
                    "source_basis_completion_rate": 0.45,
                    "citation_detail_completion_rate": 1.0,
                }
            },
            "observation_contract_metrics": {
                "readiness": {
                    "observation_contract_status": (
                        "synthetic_observation_contract_ready_needs_field_topology_proxy_labels_and_missingness"
                    ),
                    "budget_pass": True,
                    "proxy_enhanced_weak_state_coverage": 0.58,
                }
            },
        },
    ).run([])

    assert report.metrics["ranked_refactor_actions"][0]["action_id"] == (
        "R3_agent49_replay_counterfactual_stress"
    )
    assert report.metrics["ranked_refactor_actions"][1]["action_id"] == (
        "R2_observation_contract_baseline_completed"
    )


def test_architecture_consolidation_moves_to_reward_prior_after_control_stress_ready() -> None:
    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        core_metrics={
            "unified_field_evidence_gate_metrics": {
                "readiness": {
                    "unified_field_evidence_gate_status": "unified_gate_ready_blocking_field_claim_upgrade",
                    "gate_source_consolidation_coverage": 1.0,
                    "citation_detail_completion_rate": 1.0,
                }
            },
            "observation_contract_metrics": {
                "readiness": {
                    "observation_contract_status": (
                        "synthetic_observation_contract_ready_needs_field_topology_proxy_labels_and_missingness"
                    ),
                    "budget_pass": True,
                    "proxy_enhanced_weak_state_coverage": 0.58,
                }
            },
            "control_replay_stress_metrics": {
                "readiness": {
                    "control_replay_stress_status": "synthetic_counterfactual_stress_ready_needs_field_replay",
                    "can_update_agent49_reward_prior": True,
                },
                "counterfactual_metrics": {
                    "guardrail_candidate": {"joint_action_accuracy": 1.0},
                },
            },
        },
    ).run([])

    assert report.metrics["ranked_refactor_actions"][0]["action_id"] == (
        "R3b_agent49_reward_prior_patch_from_counterfactual_stress"
    )
    assert "reward prior" in report.metrics["ranked_refactor_actions"][0]["title"]


def test_architecture_consolidation_moves_to_guardrail_aware_replay_after_r3b_integrated() -> None:
    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        core_metrics={
            "unified_field_evidence_gate_metrics": {
                "readiness": {
                    "unified_field_evidence_gate_status": "unified_gate_ready_blocking_field_claim_upgrade",
                    "gate_source_consolidation_coverage": 1.0,
                    "citation_detail_completion_rate": 1.0,
                }
            },
            "observation_contract_metrics": {
                "readiness": {
                    "observation_contract_status": (
                        "synthetic_observation_contract_ready_needs_field_topology_proxy_labels_and_missingness"
                    ),
                    "budget_pass": True,
                    "proxy_enhanced_weak_state_coverage": 0.58,
                }
            },
            "control_replay_stress_metrics": {
                "readiness": {
                    "control_replay_stress_status": "synthetic_counterfactual_stress_ready_needs_field_replay",
                    "can_update_agent49_reward_prior": True,
                },
                "counterfactual_metrics": {
                    "guardrail_candidate": {"joint_action_accuracy": 1.0},
                },
            },
            "collaborative_control_metrics": {
                "readiness": {
                    "control_replay_guardrails_integrated": True,
                },
                "control_replay_guardrail_context": {
                    "reward_prior_guardrail_available": True,
                },
            },
        },
    ).run([])

    assert report.metrics["ranked_refactor_actions"][0]["action_id"] == (
        "R3c_agent52_guardrail_aware_replay_refresh"
    )
    assert "Agent52" in report.metrics["ranked_refactor_actions"][0]["title"]


def test_architecture_consolidation_moves_to_grey_box_backprop_after_r3c_ready() -> None:
    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        core_metrics={
            "unified_field_evidence_gate_metrics": {
                "readiness": {
                    "unified_field_evidence_gate_status": "unified_gate_ready_blocking_field_claim_upgrade",
                    "gate_source_consolidation_coverage": 1.0,
                    "citation_detail_completion_rate": 1.0,
                }
            },
            "observation_contract_metrics": {
                "readiness": {
                    "observation_contract_status": (
                        "synthetic_observation_contract_ready_needs_field_topology_proxy_labels_and_missingness"
                    ),
                    "budget_pass": True,
                    "proxy_enhanced_weak_state_coverage": 0.58,
                }
            },
            "control_replay_stress_metrics": {
                "readiness": {
                    "control_replay_stress_status": "synthetic_counterfactual_stress_ready_needs_field_replay",
                    "can_update_agent49_reward_prior": True,
                },
                "counterfactual_metrics": {
                    "guardrail_candidate": {"joint_action_accuracy": 1.0},
                },
            },
            "collaborative_control_metrics": {
                "readiness": {
                    "control_replay_guardrails_integrated": True,
                },
                "control_replay_guardrail_context": {
                    "reward_prior_guardrail_available": True,
                },
            },
            "replay_evaluation_metrics": {
                "readiness": {
                    "guardrail_aware_replay_ready": True,
                },
                "offline_evaluation_metrics": {
                    "control_replay_guardrails_integrated": True,
                    "guardrail_aware_regret_delta": 0.055,
                },
            },
        },
    ).run([])

    assert report.metrics["ranked_refactor_actions"][0]["action_id"] == (
        "R4_backpropagate_guardrail_failures_to_grey_box_and_field_requirements"
    )
    assert "灰箱" in report.metrics["ranked_refactor_actions"][0]["title"]


def test_architecture_consolidation_moves_to_patch_consumption_after_r4_ready() -> None:
    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        core_metrics={
            "unified_field_evidence_gate_metrics": {
                "readiness": {
                    "unified_field_evidence_gate_status": "unified_gate_ready_blocking_field_claim_upgrade",
                    "gate_source_consolidation_coverage": 1.0,
                    "citation_detail_completion_rate": 1.0,
                }
            },
            "observation_contract_metrics": {
                "readiness": {
                    "observation_contract_status": (
                        "synthetic_observation_contract_ready_needs_field_topology_proxy_labels_and_missingness"
                    ),
                    "budget_pass": True,
                    "proxy_enhanced_weak_state_coverage": 0.58,
                }
            },
            "control_replay_stress_metrics": {
                "readiness": {
                    "control_replay_stress_status": "synthetic_counterfactual_stress_ready_needs_field_replay",
                    "can_update_agent49_reward_prior": True,
                },
                "counterfactual_metrics": {
                    "guardrail_candidate": {"joint_action_accuracy": 1.0},
                },
            },
            "collaborative_control_metrics": {
                "readiness": {
                    "control_replay_guardrails_integrated": True,
                },
                "control_replay_guardrail_context": {
                    "reward_prior_guardrail_available": True,
                },
            },
            "replay_evaluation_metrics": {
                "readiness": {
                    "guardrail_aware_replay_ready": True,
                },
                "offline_evaluation_metrics": {
                    "control_replay_guardrails_integrated": True,
                    "guardrail_aware_regret_delta": 0.055,
                },
            },
            "control_guardrail_backpropagation_metrics": {
                "readiness": {
                    "backpropagation_ready": True,
                },
                "coverage_metrics": {
                    "resolved_case_to_mechanism_coverage": 1.0,
                },
            },
        },
    ).run([])

    assert report.metrics["ranked_refactor_actions"][0]["action_id"] == (
        "R4b_patch_agent53_and_field_requirement_interfaces"
    )
    assert "Agent53" in report.metrics["ranked_refactor_actions"][0]["title"]


def test_architecture_consolidation_moves_to_schema_extension_after_r4b_ready() -> None:
    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        core_metrics={
            "unified_field_evidence_gate_metrics": {
                "readiness": {
                    "unified_field_evidence_gate_status": "unified_gate_ready_blocking_field_claim_upgrade",
                    "gate_source_consolidation_coverage": 1.0,
                    "citation_detail_completion_rate": 1.0,
                }
            },
            "observation_contract_metrics": {
                "readiness": {
                    "observation_contract_status": (
                        "synthetic_observation_contract_ready_needs_field_topology_proxy_labels_and_missingness"
                    ),
                    "budget_pass": True,
                    "proxy_enhanced_weak_state_coverage": 0.58,
                }
            },
            "control_replay_stress_metrics": {
                "readiness": {
                    "control_replay_stress_status": "synthetic_counterfactual_stress_ready_needs_field_replay",
                    "can_update_agent49_reward_prior": True,
                },
                "counterfactual_metrics": {
                    "guardrail_candidate": {"joint_action_accuracy": 1.0},
                },
            },
            "collaborative_control_metrics": {
                "readiness": {
                    "control_replay_guardrails_integrated": True,
                },
                "control_replay_guardrail_context": {
                    "reward_prior_guardrail_available": True,
                },
            },
            "replay_evaluation_metrics": {
                "readiness": {
                    "guardrail_aware_replay_ready": True,
                },
                "offline_evaluation_metrics": {
                    "control_replay_guardrails_integrated": True,
                    "guardrail_aware_regret_delta": 0.055,
                },
            },
            "control_guardrail_backpropagation_metrics": {
                "readiness": {
                    "backpropagation_ready": True,
                },
                "coverage_metrics": {
                    "resolved_case_to_mechanism_coverage": 1.0,
                },
            },
            "minimal_grey_box_physics_metrics": {
                "readiness": {
                    "agent53_guardrail_boundary_consumption_rate": 1.0,
                }
            },
            "field_validation_queue_alignment_metrics": {
                "readiness": {
                    "field_requirement_patch_consumption_rate": 1.0,
                }
            },
            "claim_specific_field_package_metrics": {
                "readiness": {
                    "field_requirement_patch_consumption_rate": 1.0,
                    "unmet_guardrail_field_count": 6,
                    "unmet_guardrail_fields": [
                        "actuator_latency_p90",
                        "hold_time_min",
                        "proxy_holdout_label",
                        "pump_valve_result",
                        "regeneration_event",
                        "tank_storage_margin",
                    ],
                    "source_basis_completion_rate": 0.45,
                }
            },
        },
    ).run([])

    top = report.metrics["ranked_refactor_actions"][0]

    assert top["action_id"] == "R5_extend_guardrail_field_and_replay_schema"
    assert "Agent30/42" in top["implementation_path"]
    assert "unmet_guardrail_field_count=6" in top["trigger_metric"]


def test_architecture_consolidation_moves_to_source_basis_after_r5_schema_ready() -> None:
    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        core_metrics=_r4b_ready_core_metrics(unmet_count=0, unmet_fields=[]),
    ).run([])

    top = report.metrics["ranked_refactor_actions"][0]

    assert top["action_id"] == "R6_complete_guardrail_source_basis_and_field_package_acceptance"
    assert "source_basis_completion_rate=0.225" in top["trigger_metric"]
    assert "真实 field package" in top["why_now"]


def test_architecture_consolidation_moves_to_real_field_import_after_source_basis_ready() -> None:
    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        core_metrics=_r4b_ready_core_metrics(unmet_count=0, unmet_fields=[], source_basis_rate=1.0),
    ).run([])

    top = report.metrics["ranked_refactor_actions"][0]

    assert top["action_id"] == "R7_real_field_package_import_acceptance_gate"
    assert "field package" in top["title"]
    assert "synthetic template" in top["must_not_do"]


def test_architecture_consolidation_uses_r7_acceptance_gate_next_action() -> None:
    core_metrics = _r4b_ready_core_metrics(unmet_count=0, unmet_fields=[], source_basis_rate=1.0)
    core_metrics["real_field_package_acceptance_gate_metrics"] = {
        "readiness": {
            "real_field_package_acceptance_status": "real_field_package_acceptance_blocked_at_import",
            "passed_stage_count": 0,
            "total_stage_count": 7,
            "blocking_reasons": ["field_package_not_imported_or_data_origin_not_field"],
            "next_recommended_core_action": "R7a_import_real_field_package_with_metadata_and_csv",
        }
    }

    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        core_metrics=core_metrics,
    ).run([])

    top = report.metrics["ranked_refactor_actions"][0]

    assert top["action_id"] == "R7a_import_real_field_package_with_metadata_and_csv"
    assert "0/7" in top["trigger_metric"]
    assert "field_package_not_imported_or_data_origin_not_field" in top["current_blockers"]


def test_architecture_consolidation_provides_offline_core_fallback_when_r7a_waits_for_field_package() -> None:
    core_metrics = _r4b_ready_core_metrics(unmet_count=0, unmet_fields=[], source_basis_rate=1.0)
    core_metrics["real_field_package_acceptance_gate_metrics"] = {
        "readiness": {
            "real_field_package_acceptance_status": "real_field_package_acceptance_blocked_at_import",
            "passed_stage_count": 0,
            "total_stage_count": 8,
            "blocking_reasons": ["field_package_not_imported_or_data_origin_not_field"],
            "next_recommended_core_action": "R7a_import_real_field_package_with_metadata_and_csv",
        }
    }
    core_metrics["agent48_metrics"] = _agent48_hidden_state_ledger_metrics()

    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        core_metrics=core_metrics,
    ).run([])

    fallback = report.metrics["offline_core_fallback_action"]

    assert report.metrics["ranked_refactor_actions"][0]["action_id"] == "R7a_import_real_field_package_with_metadata_and_csv"
    assert fallback["fallback_enabled"] is True
    assert fallback["action_id"] == "R8b_agent48_pressure_headloss_candidate_pool_design"
    assert "catalyst_activity" in fallback["trigger_metric"]
    assert any("离线核心 fallback" in recommendation for recommendation in report.recommendations)


def test_architecture_consolidation_advances_fallback_after_pressure_headloss_pool_reaches_r2() -> None:
    core_metrics = _r4b_ready_core_metrics(unmet_count=0, unmet_fields=[], source_basis_rate=1.0)
    core_metrics["real_field_package_acceptance_gate_metrics"] = {
        "readiness": {
            "real_field_package_acceptance_status": "real_field_package_acceptance_blocked_at_import",
            "passed_stage_count": 0,
            "total_stage_count": 8,
            "blocking_reasons": ["field_package_not_imported_or_data_origin_not_field"],
            "next_recommended_core_action": "R7a_import_real_field_package_with_metadata_and_csv",
        }
    }
    core_metrics["agent48_metrics"] = _agent48_hidden_state_ledger_metrics(with_pressure_pool=True)
    core_metrics["observation_contract_metrics"] = {
        "readiness": {
            "observation_contract_status": (
                "synthetic_observation_contract_ready_needs_field_topology_proxy_labels_and_missingness"
            ),
            "budget_pass": True,
            "proxy_enhanced_weak_state_coverage": 0.58,
            "agent48_pressure_headloss_candidate_pool_status": (
                "pressure_headloss_candidate_pool_ready_needs_field_topology_and_labels"
            ),
            "agent48_pressure_headloss_candidate_count": 3,
        },
        "field_validation_requirements": [
            {
                "requirement_id": "R2_FV4_agent48_hidden_state_requirement_patch",
                "pressure_headloss_candidate_ids": ["N3_catalyst_bed:pressure_drop_kPa"],
            }
        ],
    }

    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        core_metrics=core_metrics,
    ).run([])

    fallback = report.metrics["offline_core_fallback_action"]

    assert fallback["fallback_enabled"] is True
    assert fallback["action_id"] == "R8c_agent54_49_consume_pressure_headloss_contract"
    assert "R2_FV4_pressure_pool_consumed=True" in fallback["trigger_metric"]


def test_architecture_consolidation_advances_fallback_after_agent54_49_consume_pressure_headloss_contract() -> None:
    core_metrics = _r4b_ready_core_metrics(unmet_count=0, unmet_fields=[], source_basis_rate=1.0)
    core_metrics["real_field_package_acceptance_gate_metrics"] = {
        "readiness": {
            "real_field_package_acceptance_status": "real_field_package_acceptance_blocked_at_import",
            "passed_stage_count": 0,
            "total_stage_count": 8,
            "blocking_reasons": ["field_package_not_imported_or_data_origin_not_field"],
            "next_recommended_core_action": "R7a_import_real_field_package_with_metadata_and_csv",
        }
    }
    core_metrics["agent48_metrics"] = _agent48_hidden_state_ledger_metrics(with_pressure_pool=True)
    core_metrics["observation_contract_metrics"] = {
        "readiness": {
            "observation_contract_status": (
                "synthetic_observation_contract_ready_needs_field_topology_proxy_labels_and_missingness"
            ),
            "budget_pass": True,
            "proxy_enhanced_weak_state_coverage": 0.58,
            "agent48_pressure_headloss_candidate_pool_status": (
                "pressure_headloss_candidate_pool_ready_needs_field_topology_and_labels"
            ),
            "agent48_pressure_headloss_candidate_count": 3,
        },
        "field_validation_requirements": [
            {
                "requirement_id": "R2_FV4_agent48_hidden_state_requirement_patch",
                "pressure_headloss_candidate_ids": ["N3_catalyst_bed:pressure_drop_kPa"],
            }
        ],
    }
    core_metrics["soft_sensor_matrix_metrics"] = {
        "readiness": {
            "pressure_headloss_candidate_pool_status": (
                "pressure_headloss_candidate_pool_ready_needs_field_topology_and_labels"
            ),
            "pressure_headloss_candidate_count": 3,
        },
        "feature_contract": {
            "pressure_headloss_candidate_contract": {
                "pool_status": "pressure_headloss_candidate_pool_ready_needs_field_topology_and_labels",
                "candidate_count": 3,
            }
        },
    }
    core_metrics["collaborative_control_metrics"] = {
        "sparse_context": {
            "observation_contract_context": {
                "pressure_headloss_consumed_by_agent49": True,
                "pressure_headloss_candidate_count": 3,
            }
        },
        "control_replay_guardrail_context": {
            "pressure_headloss_consumed_by_agent49": True,
            "pressure_headloss_candidate_count": 3,
        },
    }

    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        core_metrics=core_metrics,
    ).run([])

    fallback = report.metrics["offline_core_fallback_action"]

    assert fallback["fallback_enabled"] is True
    assert fallback["action_id"] == "R8d_agent52_pressure_headloss_guardrail_replay_refresh"
    assert "Agent54_49_pressure_contract_consumed=True" in fallback["trigger_metric"]


def test_architecture_consolidation_advances_fallback_after_agent52_consumes_pressure_headloss_boundary() -> None:
    core_metrics = _r4b_ready_core_metrics(unmet_count=0, unmet_fields=[], source_basis_rate=1.0)
    core_metrics["real_field_package_acceptance_gate_metrics"] = {
        "readiness": {
            "real_field_package_acceptance_status": "real_field_package_acceptance_blocked_at_import",
            "passed_stage_count": 0,
            "total_stage_count": 8,
            "blocking_reasons": ["field_package_not_imported_or_data_origin_not_field"],
            "next_recommended_core_action": "R7a_import_real_field_package_with_metadata_and_csv",
        }
    }
    core_metrics["agent48_metrics"] = _agent48_hidden_state_ledger_metrics(with_pressure_pool=True)
    core_metrics["observation_contract_metrics"] = {
        "readiness": {
            "observation_contract_status": (
                "synthetic_observation_contract_ready_needs_field_topology_proxy_labels_and_missingness"
            ),
            "budget_pass": True,
            "proxy_enhanced_weak_state_coverage": 0.58,
            "agent48_pressure_headloss_candidate_pool_status": (
                "pressure_headloss_candidate_pool_ready_needs_field_topology_and_labels"
            ),
            "agent48_pressure_headloss_candidate_count": 3,
        },
        "field_validation_requirements": [
            {
                "requirement_id": "R2_FV4_agent48_hidden_state_requirement_patch",
                "pressure_headloss_candidate_ids": ["N3_catalyst_bed:pressure_drop_kPa"],
            }
        ],
    }
    core_metrics["soft_sensor_matrix_metrics"] = {
        "readiness": {
            "pressure_headloss_candidate_pool_status": (
                "pressure_headloss_candidate_pool_ready_needs_field_topology_and_labels"
            ),
            "pressure_headloss_candidate_count": 3,
        }
    }
    core_metrics["collaborative_control_metrics"] = {
        "control_replay_guardrail_context": {
            "pressure_headloss_consumed_by_agent49": True,
            "pressure_headloss_candidate_count": 3,
        }
    }
    core_metrics["replay_evaluation_metrics"] = {
        "offline_evaluation_metrics": {
            "pressure_headloss_boundary_consumed": True,
            "pressure_headloss_candidate_count": 3,
            "pressure_headloss_blocked_guardrail_case_count": 2,
        }
    }

    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        core_metrics=core_metrics,
    ).run([])

    fallback = report.metrics["offline_core_fallback_action"]

    assert fallback["fallback_enabled"] is True
    assert fallback["action_id"] == "R8e_agent30_42_pressure_headloss_field_schema_patch"
    assert "Agent52_pressure_headloss_boundary_consumed=True" in fallback["trigger_metric"]


def test_architecture_consolidation_advances_fallback_after_agent30_42_pressure_headloss_schema_ready() -> None:
    core_metrics = _pressure_headloss_chain_core_metrics(include_r8e=True)

    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        core_metrics=core_metrics,
    ).run([])

    fallback = report.metrics["offline_core_fallback_action"]

    assert fallback["fallback_enabled"] is True
    assert fallback["action_id"] == "R8f_agent44_pressure_headloss_import_gate_patch"
    assert "R8e_field_schema_ready=True" in fallback["trigger_metric"]


def test_architecture_consolidation_advances_fallback_after_agent44_pressure_headloss_import_gate_ready() -> None:
    core_metrics = _pressure_headloss_chain_core_metrics(include_r8e=True, include_r8f=True)

    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        core_metrics=core_metrics,
    ).run([])

    fallback = report.metrics["offline_core_fallback_action"]

    assert fallback["fallback_enabled"] is True
    assert fallback["action_id"] == "R8g_r7_pressure_headloss_minimum_replay_contract"
    assert "R8f_import_gate_pressure_ready=True" in fallback["trigger_metric"]


def test_architecture_consolidation_advances_fallback_after_r7_pressure_headloss_contract_ready() -> None:
    core_metrics = _pressure_headloss_chain_core_metrics(include_r8e=True, include_r8f=True, include_r8g=True)

    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        core_metrics=core_metrics,
    ).run([])

    fallback = report.metrics["offline_core_fallback_action"]

    assert fallback["fallback_enabled"] is True
    assert fallback["action_id"] == "R8h_agent44_pressure_headloss_preflight_diagnostics"
    assert "R8g_r7_pressure_headloss_contract_ready=True" in fallback["trigger_metric"]


def test_architecture_consolidation_advances_fallback_after_agent44_preflight_diagnostics_ready() -> None:
    core_metrics = _pressure_headloss_chain_core_metrics(
        include_r8e=True,
        include_r8f=True,
        include_r8g=True,
        include_r8h=True,
    )

    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        core_metrics=core_metrics,
    ).run([])

    fallback = report.metrics["offline_core_fallback_action"]

    assert fallback["fallback_enabled"] is True
    assert fallback["action_id"] == "R8i_agent51_consume_pressure_headloss_event_log"
    assert "R8h_agent44_preflight_diagnostics_ready=True" in fallback["trigger_metric"]


def test_architecture_consolidation_advances_fallback_after_agent51_pressure_event_source_ready() -> None:
    core_metrics = _pressure_headloss_chain_core_metrics(
        include_r8e=True,
        include_r8f=True,
        include_r8g=True,
        include_r8h=True,
        include_r8i=True,
    )

    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        core_metrics=core_metrics,
    ).run([])

    fallback = report.metrics["offline_core_fallback_action"]

    assert fallback["fallback_enabled"] is True
    assert fallback["action_id"] == "R8j_propagate_agent51_pressure_source_to_agent49_52"
    assert "R8i_agent51_pressure_event_source_ready=True" in fallback["trigger_metric"]


def test_architecture_consolidation_advances_fallback_after_pressure_source_context_propagates() -> None:
    core_metrics = _pressure_headloss_chain_core_metrics(
        include_r8e=True,
        include_r8f=True,
        include_r8g=True,
        include_r8h=True,
        include_r8i=True,
        include_r8j=True,
    )

    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        core_metrics=core_metrics,
    ).run([])

    fallback = report.metrics["offline_core_fallback_action"]

    assert fallback["fallback_enabled"] is True
    assert fallback["action_id"] == "R8k_pressure_headloss_source_conflict_calibration_boundary"
    assert "R8j_pressure_source_context_propagated=True" in fallback["trigger_metric"]


def test_architecture_consolidation_advances_fallback_after_pressure_conflict_boundary_ready() -> None:
    core_metrics = _pressure_headloss_chain_core_metrics(
        include_r8e=True,
        include_r8f=True,
        include_r8g=True,
        include_r8h=True,
        include_r8i=True,
        include_r8j=True,
        include_r8k=True,
    )

    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        core_metrics=core_metrics,
    ).run([])

    fallback = report.metrics["offline_core_fallback_action"]

    assert fallback["fallback_enabled"] is True
    assert fallback["action_id"] == "R8l_pressure_source_conflict_control_replay_impact"
    assert "R8k_pressure_conflict_boundary_ready=True" in fallback["trigger_metric"]


def test_architecture_consolidation_advances_fallback_after_pressure_conflict_reaches_control_replay() -> None:
    core_metrics = _pressure_headloss_chain_core_metrics(
        include_r8e=True,
        include_r8f=True,
        include_r8g=True,
        include_r8h=True,
        include_r8i=True,
        include_r8j=True,
        include_r8k=True,
        include_r8l=True,
    )

    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        core_metrics=core_metrics,
    ).run([])

    fallback = report.metrics["offline_core_fallback_action"]

    assert fallback["fallback_enabled"] is True
    assert fallback["action_id"] == "R8m_pressure_source_conflict_field_patch_requirements"
    assert "R8l_conflict_control_replay_ready=True" in fallback["trigger_metric"]


def test_architecture_consolidation_promotes_pressure_conflict_patch_requirements_as_main_r7_action() -> None:
    core_metrics = _pressure_headloss_chain_core_metrics(
        include_r8e=True,
        include_r8f=True,
        include_r8g=True,
        include_r8h=True,
        include_r8i=True,
        include_r8j=True,
        include_r8k=True,
        include_r8l=True,
        include_r8m=True,
    )

    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        core_metrics=core_metrics,
    ).run([])

    top_action = report.metrics["ranked_refactor_actions"][0]
    fallback = report.metrics["offline_core_fallback_action"]

    assert top_action["action_id"] == "R8m_pressure_source_conflict_field_patch_requirements"
    assert "pressure_source_conflict_count=1" in top_action["trigger_metric"]
    assert fallback["fallback_enabled"] is False


def test_architecture_consolidation_advances_fallback_after_pressure_resolution_clearance_gate_ready() -> None:
    core_metrics = _pressure_headloss_chain_core_metrics(
        include_r8e=True,
        include_r8f=True,
        include_r8g=True,
        include_r8h=True,
        include_r8i=True,
        include_r8j=True,
        include_r8k=True,
        include_r8l=True,
        include_r8n=True,
    )

    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        core_metrics=core_metrics,
    ).run([])

    fallback = report.metrics["offline_core_fallback_action"]

    assert fallback["fallback_enabled"] is True
    assert fallback["action_id"] == "R8o_pressure_resolution_field_replay_scenario_pack"
    assert "R8n_pressure_resolution_replay_clearance_ready=True" in fallback["trigger_metric"]
    assert "resolved_pressure_source_conflict_replay_case_count" in fallback["expected_metrics"]


def test_architecture_consolidation_advances_fallback_after_pressure_resolution_scenario_pack_ready() -> None:
    core_metrics = _pressure_headloss_chain_core_metrics(
        include_r8e=True,
        include_r8f=True,
        include_r8g=True,
        include_r8h=True,
        include_r8i=True,
        include_r8j=True,
        include_r8k=True,
        include_r8l=True,
        include_r8n=True,
        include_r8o=True,
    )

    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        core_metrics=core_metrics,
    ).run([])

    fallback = report.metrics["offline_core_fallback_action"]

    assert fallback["fallback_enabled"] is True
    assert fallback["action_id"] == "R8p_collect_pressure_resolution_replay_rows"
    assert "R8o_pressure_resolution_scenario_pack_ready=True" in fallback["trigger_metric"]
    assert "field_scenario_coverage" in fallback["expected_metrics"]


def test_architecture_consolidation_consumes_r8p_field_rows_patch_plan() -> None:
    core_metrics = _pressure_headloss_chain_core_metrics(
        include_r8e=True,
        include_r8f=True,
        include_r8g=True,
        include_r8h=True,
        include_r8i=True,
        include_r8j=True,
        include_r8k=True,
        include_r8l=True,
        include_r8n=True,
        include_r8o=True,
    )
    core_metrics["pressure_resolution_replay_scenario_pack_metrics"]["field_rows_patch_plan"] = {
        "field_rows_patch_plan_status": "field_rows_patch_plan_blocked_at_source_preflight",
        "next_operator_action": "R8p_fix_field_rows_source_preflight",
        "patch_item_count": 12,
        "highest_priority_patch_id": "R8P_SOURCE_MISSING_FIELD_ROWS_FILE",
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }
    core_metrics["pressure_resolution_replay_scenario_pack_metrics"]["field_rows_operator_handoff"] = {
        "field_rows_operator_handoff_status": "field_rows_operator_handoff_ready_needs_source_package",
        "field_rows_package_schema_status": "field_rows_package_schema_ready",
    "field_rows_schema_validation_status": "schema_validation_blocked_at_source_preflight",
    "field_rows_collection_checklist_status": "field_rows_collection_checklist_ready_needs_source_package",
    "field_rows_batch_bundle_preflight_status": "batch_bundle_preflight_blocked_at_source_preflight",
    "field_rows_temporal_window_preflight_status": "temporal_window_preflight_blocked_at_source_preflight",
    "field_rows_scenario_semantic_preflight_status": (
        "scenario_semantic_preflight_blocked_at_source_preflight"
    ),
    "field_rows_downstream_routing_preflight_status": (
        "downstream_routing_preflight_blocked_at_source_preflight"
    ),
    "field_rows_provenance_gate_status": "all_required_tables_require_field_origin",
    "field_rows_all_tables_require_data_origin": True,
    "field_rows_provenance_required_table_count": 6,
    "schema_validation_summary": {
        "required_field_gap_count": 0,
        "invalid_type_count": 0,
        "missing_table_count": 6,
        "empty_table_count": 0,
        "unknown_table_count": 0,
    },
    "batch_bundle_preflight_summary": {
        "candidate_batch_count": 0,
        "complete_bundle_count": 0,
        "partial_bundle_count": 0,
        "missing_bundle_table_count": 0,
        "scenario_bundle_ready_count": 0,
    },
    "temporal_window_preflight_summary": {
        "checked_batch_count": 0,
        "temporal_valid_batch_count": 0,
        "temporal_violation_count": 0,
        "hold_time_violation_count": 0,
        "scenario_temporal_ready_count": 0,
    },
    "scenario_semantic_preflight_summary": {
        "checked_batch_count": 0,
        "semantic_valid_batch_count": 0,
        "semantic_violation_count": 0,
        "scenario_semantic_ready_count": 0,
    },
    "downstream_routing_preflight_summary": {
        "accepted_scenario_count": 0,
        "accepted_batch_count": 0,
        "routing_target_count": 4,
        "routing_ready_target_count": 0,
        "can_route_to_r8v": False,
    },
    "validation_command_default": (
        ".venv/bin/python experiments/run_agent61_pressure_resolution_replay_scenario_pack.py"
    ),
    "env_override_name": "PRESSURE_RESOLUTION_REPLAY_ROWS_PATH",
    "default_field_rows_path": "outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows.json",
    "template_rows_path": (
        "outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_template.json"
    ),
    "rows_schema_path": (
        "outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_schema.json"
    ),
    "collection_checklist_path": (
        "outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_collection_checklist.json"
    ),
    "field_rows_batch_bundle_preflight_path": (
        "outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_batch_bundle_preflight.json"
    ),
    "field_rows_temporal_window_preflight_path": (
        "outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_temporal_window_preflight.json"
    ),
    "field_rows_scenario_semantic_preflight_path": (
        "outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_scenario_semantic_preflight.json"
    ),
        "field_rows_downstream_routing_preflight_path": (
            "outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_downstream_routing_preflight.json"
        ),
    }
    core_metrics["pressure_resolution_replay_scenario_pack_metrics"]["field_rows_r7_completion_plan"] = {
        "completion_plan_status": "r7_to_r8p_completion_plan_waiting_for_r7_package",
    "item_count": 6,
    "item_class_counts": {
        "r7_source_package": 1,
        "operator_supplement": 4,
        "agent52_replay_export": 1,
    },
    "field_gap_count_by_class": {
        "r7_source_package": 0,
        "operator_supplement": 10,
        "agent52_replay_export": 11,
    },
    "completion_plan_path": (
        "outputs/pressure_resolution_replay_scenario_pack/"
        "pressure_resolution_replay_rows_r7_completion_plan.json"
    ),
    "required_execution_order": [
        "R8U22_R7_SOURCE_PACKAGE_R7_TO_R8P_STAGING_PREFLIGHT_NO_R7_PACKAGE_SUPPLIED",
        "R8U22_OPERATOR_SUPPLEMENT_CAMPAIGN_OPERATION_LOG",
        "R8U22_OPERATOR_SUPPLEMENT_FAST_PROXY_EVENT_LOG",
        "R8U22_OPERATOR_SUPPLEMENT_NODE_MODALITY_SENSOR_TIMESERIES",
        "R8U22_OPERATOR_SUPPLEMENT_PRESSURE_HEADLOSS_EVENT_LOG",
        "R8U22_AGENT52_REPLAY_EXPORT_AGENT52_REPLAY_TABLE",
        ],
    }
    core_metrics["pressure_resolution_replay_scenario_pack_metrics"]["field_rows_r7_completion_route_contracts"] = {
        "completion_route_contracts_status": "completion_route_contracts_ready_waiting_for_r7_package",
        "route_contract_count": 4,
        "open_route_count": 4,
        "open_route_ids": [
            "r7_source_package",
            "operator_supplement",
            "agent52_replay_export",
            "r8p_validation_gates",
        ],
        "completion_route_contracts_path": (
            "outputs/pressure_resolution_replay_scenario_pack/"
            "pressure_resolution_replay_rows_r7_completion_route_contracts.json"
        ),
    }
    core_metrics["pressure_resolution_replay_scenario_pack_metrics"]["field_rows_r7_completion_route_work_packages"] = {
        "route_work_packages_status": "route_work_packages_ready_waiting_for_r7_package",
        "work_package_count": 4,
        "open_work_package_count": 4,
        "open_work_package_ids": [
            "R8U25_R7_SOURCE_PACKAGE_WORK_PACKAGE",
            "R8U25_OPERATOR_SUPPLEMENT_WORK_PACKAGE",
            "R8U25_AGENT52_REPLAY_EXPORT_WORK_PACKAGE",
            "R8U25_R8P_VALIDATION_GATES_WORK_PACKAGE",
        ],
        "route_work_packages_path": (
            "outputs/pressure_resolution_replay_scenario_pack/"
            "pressure_resolution_replay_rows_r7_completion_route_work_packages.json"
        ),
    }
    core_metrics["pressure_resolution_replay_scenario_pack_metrics"][
        "field_rows_r7_completion_route_work_package_templates"
    ] = {
        "route_work_package_templates_status": "route_work_package_templates_ready_not_evidence",
        "work_package_template_count": 4,
        "template_dir": (
            "outputs/pressure_resolution_replay_scenario_pack/"
            "pressure_resolution_replay_rows_r7_completion_route_work_package_templates"
        ),
    }
    core_metrics["pressure_resolution_replay_scenario_pack_metrics"][
        "field_rows_r7_completion_route_work_package_preflight"
    ] = {
        "route_work_package_preflight_status": "route_work_package_preflight_waiting_for_submission_dir",
        "submitted_work_package_count": 0,
        "passed_work_package_count": 0,
        "blocked_work_package_count": 4,
        "route_work_package_preflight_path": (
            "outputs/pressure_resolution_replay_scenario_pack/"
            "pressure_resolution_replay_rows_r7_completion_route_work_package_preflight.json"
        ),
    }
    core_metrics["pressure_resolution_replay_scenario_pack_metrics"][
        "field_rows_r7_completion_route_work_package_patch_plan"
    ] = {
        "route_work_package_patch_plan_status": "route_work_package_patch_plan_waiting_for_submission_dir",
        "patch_item_count": 1,
        "highest_priority_patch_id": "R8U27_SET_R7_TO_R8P_WORK_PACKAGE_DIR",
        "route_work_package_patch_plan_path": (
            "outputs/pressure_resolution_replay_scenario_pack/"
            "pressure_resolution_replay_rows_r7_completion_route_work_package_patch_plan.json"
        ),
    }
    core_metrics["pressure_resolution_replay_scenario_pack_metrics"][
        "field_rows_r7_completion_route_work_package_assembly_gate"
    ] = {
        "route_work_package_assembly_gate_status": "route_work_package_assembly_gate_blocked_waiting_for_submission_dir",
        "assembly_step_count": 6,
        "ready_assembly_step_count": 0,
        "blocked_assembly_step_count": 6,
        "route_work_package_assembly_gate_path": (
            "outputs/pressure_resolution_replay_scenario_pack/"
            "pressure_resolution_replay_rows_r7_completion_route_work_package_assembly_gate.json"
        ),
    }
    core_metrics["pressure_resolution_replay_scenario_pack_metrics"][
        "field_rows_submission_readiness_review"
    ] = {
        "submission_readiness_review_status": "submission_readiness_review_blocked_at_source_package",
        "next_operator_action": "R8p_fix_field_rows_source_preflight",
        "can_route_to_r8v": False,
        "direct_r8p_highest_priority_patch_id": "R8P_SOURCE_MISSING_FIELD_ROWS_FILE",
        "r7_to_r8p_highest_priority_patch_id": "R8U27_SET_R7_TO_R8P_WORK_PACKAGE_DIR",
        "review_path": (
            "outputs/pressure_resolution_replay_scenario_pack/"
            "pressure_resolution_replay_rows_submission_readiness_review.json"
        ),
    }
    core_metrics["pressure_resolution_replay_scenario_pack_metrics"][
        "field_rows_source_package_submission_route_guide"
    ] = {
        "source_package_submission_route_guide_status": (
            "source_package_submission_route_guide_ready_for_source_package_submission"
        ),
        "recommended_route_id": "direct_r8p_json_or_csv_source_package",
        "next_operator_action": "R8p_submit_direct_json_or_csv_source_package",
        "route_option_count": 3,
        "can_route_to_r8v": False,
        "guide_path": (
            "outputs/pressure_resolution_replay_scenario_pack/"
            "pressure_resolution_replay_rows_source_package_submission_route_guide.json"
        ),
    }
    core_metrics["pressure_resolution_replay_scenario_pack_metrics"][
        "field_rows_source_package_route_preflight"
    ] = {
        "source_package_route_preflight_status": (
            "source_package_route_preflight_waiting_for_source_package_submission"
        ),
        "recommended_route_id": "direct_r8p_json_or_csv_source_package",
        "recommended_route_preflight_status": (
            "recommended_route_preflight_waiting_for_direct_source_package"
        ),
        "next_operator_action": "R8p_submit_direct_json_or_csv_source_package",
        "ready_route_count": 0,
        "waiting_route_count": 3,
        "blocked_route_count": 0,
        "route_preflight_path": (
            "outputs/pressure_resolution_replay_scenario_pack/"
            "pressure_resolution_replay_rows_source_package_route_preflight.json"
        ),
    }
    core_metrics["pressure_resolution_replay_scenario_pack_metrics"]["field_rows_downstream_route_handoff"] = {
        "downstream_route_handoff_status": "downstream_route_handoff_blocked_by_upstream_r8p_preflight",
        "handoff_target_count": 4,
        "ready_handoff_target_count": 0,
        "blocked_handoff_target_count": 4,
        "next_operator_action": "R8p_fix_field_rows_source_preflight",
        "handoff_path": (
            "outputs/pressure_resolution_replay_scenario_pack/"
            "pressure_resolution_replay_rows_downstream_route_handoff.json"
        ),
        "can_route_to_r8v": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "field_claim_upgrade_allowed": False,
    }
    core_metrics["pressure_resolution_replay_scenario_pack_metrics"][
        "field_rows_downstream_target_gate_preflight"
    ] = {
        "downstream_target_gate_preflight_status": (
            "downstream_target_gate_preflight_blocked_by_downstream_route_handoff"
        ),
        "target_gate_count": 4,
        "ready_target_gate_count": 0,
        "blocked_target_gate_count": 4,
        "next_operator_action": "R8p_fix_field_rows_source_preflight",
        "target_gate_preflight_path": (
            "outputs/pressure_resolution_replay_scenario_pack/"
            "pressure_resolution_replay_rows_downstream_target_gate_preflight.json"
        ),
        "can_execute_all_target_gates": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "field_claim_upgrade_allowed": False,
    }
    core_metrics["pressure_resolution_replay_scenario_pack_metrics"][
        "field_rows_downstream_target_gate_result_preflight"
    ] = {
        "downstream_target_gate_result_preflight_status": (
            "downstream_target_gate_result_preflight_blocked_by_target_gate_preflight"
        ),
        "submitted_target_result_count": 0,
        "accepted_target_result_count": 0,
        "rejected_target_result_count": 0,
        "missing_target_ids": [
            "agent51_catalyst_proxy_holdout",
            "agent49_guardrail_context",
            "agent52_replay_clearance",
            "r7_evidence_chain",
        ],
        "next_operator_action": "R8p_fix_field_rows_source_preflight",
        "preflight_path": (
            "outputs/pressure_resolution_replay_scenario_pack/"
            "pressure_resolution_replay_rows_downstream_target_gate_result_preflight.json"
        ),
        "can_route_to_result_arbitration": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "field_claim_upgrade_allowed": False,
    }
    core_metrics["pressure_resolution_replay_scenario_pack_metrics"][
        "field_rows_downstream_target_gate_result_arbitration"
    ] = {
        "downstream_target_gate_result_arbitration_status": (
            "downstream_target_gate_result_arbitration_blocked_by_result_preflight"
        ),
        "accepted_target_result_count": 0,
        "target_gate_status_counts": {
            "target_gate_result_passed": 0,
            "target_gate_result_failed": 0,
            "target_gate_result_blocked": 0,
            "target_gate_result_waiting_for_operator_review": 0,
            "target_gate_result_invalid_or_missing": 0,
        },
        "next_operator_action": "R8p_fix_field_rows_source_preflight",
        "can_route_to_operator_review": False,
        "can_emit_protective_control_candidate": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "field_claim_upgrade_allowed": False,
    }
    core_metrics["pressure_resolution_replay_scenario_pack_metrics"][
        "field_rows_downstream_target_gate_operator_review_preflight"
    ] = {
        "downstream_target_gate_operator_review_preflight_status": (
            "downstream_target_gate_operator_review_preflight_blocked_by_result_arbitration"
        ),
        "approved_operator_review_count": 0,
        "rejected_operator_review_count": 0,
        "hold_operator_review_count": 0,
        "next_operator_action": "R8p_fix_field_rows_source_preflight",
        "can_route_to_post_review_gate": False,
        "can_emit_protective_control_candidate": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "field_claim_upgrade_allowed": False,
    }
    core_metrics["pressure_resolution_replay_scenario_pack_metrics"][
        "field_rows_downstream_target_gate_post_review_gate"
    ] = {
        "downstream_target_gate_post_review_gate_status": (
            "downstream_target_gate_post_review_gate_blocked_by_operator_review_preflight"
        ),
        "candidate_target_count": 0,
        "next_operator_action": "R8p_fix_field_rows_source_preflight",
        "can_route_to_protective_candidate_evaluation": False,
        "can_emit_protective_control_candidate": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "field_claim_upgrade_allowed": False,
    }
    core_metrics["pressure_resolution_replay_scenario_pack_metrics"][
        "field_rows_downstream_target_gate_protective_candidate_evaluation"
    ] = {
        "downstream_target_gate_protective_candidate_evaluation_status": (
            "protective_candidate_evaluation_blocked_by_post_review_gate"
        ),
        "candidate_target_count": 0,
        "next_operator_action": "R8p_fix_field_rows_source_preflight",
        "can_emit_protective_control_candidate": False,
        "can_route_to_final_execution_review": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "field_claim_upgrade_allowed": False,
    }

    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        core_metrics=core_metrics,
    ).run([])

    fallback = report.metrics["offline_core_fallback_action"]

    assert fallback["fallback_enabled"] is True
    assert fallback["action_id"] == "R8p_fix_field_rows_source_preflight"
    assert fallback["patch_plan_status"] == "field_rows_patch_plan_blocked_at_source_preflight"
    assert fallback["highest_priority_patch_id"] == "R8P_SOURCE_MISSING_FIELD_ROWS_FILE"
    assert "patch_item_count=12" in fallback["trigger_metric"]
    assert "operator_handoff_status=field_rows_operator_handoff_ready_needs_source_package" in fallback["trigger_metric"]
    assert "schema_status=field_rows_package_schema_ready" in fallback["trigger_metric"]
    assert "schema_validation_status=schema_validation_blocked_at_source_preflight" in fallback["trigger_metric"]
    assert "collection_checklist_status=field_rows_collection_checklist_ready_needs_source_package" in fallback["trigger_metric"]
    assert "batch_bundle_preflight_status=batch_bundle_preflight_blocked_at_source_preflight" in fallback["trigger_metric"]
    assert "temporal_window_preflight_status=temporal_window_preflight_blocked_at_source_preflight" in fallback["trigger_metric"]
    assert (
        "scenario_semantic_preflight_status=scenario_semantic_preflight_blocked_at_source_preflight"
        in fallback["trigger_metric"]
    )
    assert (
        "downstream_routing_preflight_status=downstream_routing_preflight_blocked_at_source_preflight"
        in fallback["trigger_metric"]
    )
    assert "provenance_gate_status=all_required_tables_require_field_origin" in fallback["trigger_metric"]
    assert "all_tables_require_data_origin=True" in fallback["trigger_metric"]
    assert "r7_completion_plan_status=r7_to_r8p_completion_plan_waiting_for_r7_package" in fallback[
        "trigger_metric"
    ]
    assert "r7_completion_item_count=6" in fallback["trigger_metric"]
    assert "operator_supplement:4" in fallback["trigger_metric"]
    assert "agent52_replay_export:11" in fallback["trigger_metric"]
    assert "r7_route_contract_status=completion_route_contracts_ready_waiting_for_r7_package" in fallback[
        "trigger_metric"
    ]
    assert "r7_open_route_count=4" in fallback["trigger_metric"]
    assert "r7_source_package,operator_supplement,agent52_replay_export,r8p_validation_gates" in fallback[
        "trigger_metric"
    ]
    assert "r7_work_package_status=route_work_packages_ready_waiting_for_r7_package" in fallback[
        "trigger_metric"
    ]
    assert "r7_open_work_package_count=4" in fallback["trigger_metric"]
    assert (
        "R8U25_R7_SOURCE_PACKAGE_WORK_PACKAGE,R8U25_OPERATOR_SUPPLEMENT_WORK_PACKAGE,"
        "R8U25_AGENT52_REPLAY_EXPORT_WORK_PACKAGE,R8U25_R8P_VALIDATION_GATES_WORK_PACKAGE"
    ) in fallback["trigger_metric"]
    assert "r7_work_package_template_status=route_work_package_templates_ready_not_evidence" in fallback[
        "trigger_metric"
    ]
    assert "r7_work_package_preflight_status=route_work_package_preflight_waiting_for_submission_dir" in fallback[
        "trigger_metric"
    ]
    assert "r7_submitted_work_package_count=0" in fallback["trigger_metric"]
    assert "r7_passed_work_package_count=0" in fallback["trigger_metric"]
    assert "r7_blocked_work_package_count=4" in fallback["trigger_metric"]
    assert (
        "r7_work_package_patch_plan_status=route_work_package_patch_plan_waiting_for_submission_dir"
        in fallback["trigger_metric"]
    )
    assert "r7_work_package_patch_item_count=1" in fallback["trigger_metric"]
    assert "r7_work_package_highest_priority_patch_id=R8U27_SET_R7_TO_R8P_WORK_PACKAGE_DIR" in fallback[
        "trigger_metric"
    ]
    assert (
        "r7_work_package_assembly_gate_status=route_work_package_assembly_gate_blocked_waiting_for_submission_dir"
        in fallback["trigger_metric"]
    )
    assert "r7_work_package_assembly_step_count=6" in fallback["trigger_metric"]
    assert "r7_work_package_blocked_assembly_step_count=6" in fallback["trigger_metric"]
    assert (
        "submission_readiness_review_status=submission_readiness_review_blocked_at_source_package"
        in fallback["trigger_metric"]
    )
    assert "submission_readiness_next_operator_action=R8p_fix_field_rows_source_preflight" in fallback[
        "trigger_metric"
    ]
    assert "submission_readiness_can_route_to_r8v=False" in fallback["trigger_metric"]
    assert (
        "source_package_route_guide_status=source_package_submission_route_guide_ready_for_source_package_submission"
        in fallback["trigger_metric"]
    )
    assert "source_package_recommended_route_id=direct_r8p_json_or_csv_source_package" in fallback[
        "trigger_metric"
    ]
    assert "source_package_next_operator_action=R8p_submit_direct_json_or_csv_source_package" in fallback[
        "trigger_metric"
    ]
    assert "source_package_route_option_count=3" in fallback["trigger_metric"]
    assert (
        "source_package_route_preflight_status=source_package_route_preflight_waiting_for_source_package_submission"
        in fallback["trigger_metric"]
    )
    assert (
        "source_package_recommended_route_preflight_status=recommended_route_preflight_waiting_for_direct_source_package"
        in fallback["trigger_metric"]
    )
    assert "source_package_ready_route_count=0" in fallback["trigger_metric"]
    assert "source_package_waiting_route_count=3" in fallback["trigger_metric"]
    assert "source_package_blocked_route_count=0" in fallback["trigger_metric"]
    assert (
        "downstream_route_handoff_status=downstream_route_handoff_blocked_by_upstream_r8p_preflight"
        in fallback["trigger_metric"]
    )
    assert "downstream_ready_handoff_target_count=0" in fallback["trigger_metric"]
    assert "downstream_blocked_handoff_target_count=4" in fallback["trigger_metric"]
    assert (
        "downstream_route_handoff_next_operator_action=R8p_fix_field_rows_source_preflight"
        in fallback["trigger_metric"]
    )
    assert (
        "downstream_target_gate_result_preflight_status="
        "downstream_target_gate_result_preflight_blocked_by_target_gate_preflight"
        in fallback["trigger_metric"]
    )
    assert "downstream_target_gate_result_submitted_count=0" in fallback["trigger_metric"]
    assert "downstream_target_gate_result_accepted_count=0" in fallback["trigger_metric"]
    assert "downstream_target_gate_result_rejected_count=0" in fallback["trigger_metric"]
    assert (
        "downstream_target_gate_result_next_operator_action=R8p_fix_field_rows_source_preflight"
        in fallback["trigger_metric"]
    )
    assert (
        "downstream_target_gate_result_arbitration_status="
        "downstream_target_gate_result_arbitration_blocked_by_result_preflight"
        in fallback["trigger_metric"]
    )
    assert (
        "downstream_target_gate_result_arbitration_next_operator_action=R8p_fix_field_rows_source_preflight"
        in fallback["trigger_metric"]
    )
    assert "downstream_target_gate_result_can_route_to_operator_review=False" in fallback["trigger_metric"]
    assert (
        "downstream_target_gate_result_can_emit_protective_control_candidate=False"
        in fallback["trigger_metric"]
    )
    assert fallback["operator_handoff_status"] == "field_rows_operator_handoff_ready_needs_source_package"
    assert fallback["field_rows_package_schema_status"] == "field_rows_package_schema_ready"
    assert fallback["field_rows_schema_validation_status"] == "schema_validation_blocked_at_source_preflight"
    assert fallback["field_rows_collection_checklist_status"] == (
        "field_rows_collection_checklist_ready_needs_source_package"
    )
    assert fallback["field_rows_batch_bundle_preflight_status"] == (
        "batch_bundle_preflight_blocked_at_source_preflight"
    )
    assert fallback["batch_bundle_preflight_summary"]["complete_bundle_count"] == 0
    assert fallback["batch_bundle_preflight_path"].endswith(
        "pressure_resolution_replay_rows_batch_bundle_preflight.json"
    )
    assert fallback["field_rows_temporal_window_preflight_status"] == (
        "temporal_window_preflight_blocked_at_source_preflight"
    )
    assert fallback["temporal_window_preflight_summary"]["temporal_violation_count"] == 0
    assert fallback["temporal_window_preflight_path"].endswith(
        "pressure_resolution_replay_rows_temporal_window_preflight.json"
    )
    assert fallback["field_rows_scenario_semantic_preflight_status"] == (
        "scenario_semantic_preflight_blocked_at_source_preflight"
    )
    assert fallback["scenario_semantic_preflight_summary"]["semantic_violation_count"] == 0
    assert fallback["scenario_semantic_preflight_path"].endswith(
        "pressure_resolution_replay_rows_scenario_semantic_preflight.json"
    )
    assert fallback["field_rows_downstream_routing_preflight_status"] == (
        "downstream_routing_preflight_blocked_at_source_preflight"
    )
    assert fallback["downstream_routing_preflight_summary"]["routing_target_count"] == 4
    assert fallback["downstream_routing_preflight_path"].endswith(
        "pressure_resolution_replay_rows_downstream_routing_preflight.json"
    )
    assert fallback["field_rows_downstream_route_handoff_status"] == (
        "downstream_route_handoff_blocked_by_upstream_r8p_preflight"
    )
    assert fallback["downstream_handoff_target_count"] == 4
    assert fallback["downstream_ready_handoff_target_count"] == 0
    assert fallback["downstream_blocked_handoff_target_count"] == 4
    assert fallback["downstream_route_handoff_next_operator_action"] == "R8p_fix_field_rows_source_preflight"
    assert fallback["downstream_route_handoff_path"].endswith(
        "pressure_resolution_replay_rows_downstream_route_handoff.json"
    )
    assert fallback["field_rows_downstream_target_gate_preflight_status"] == (
        "downstream_target_gate_preflight_blocked_by_downstream_route_handoff"
    )
    assert fallback["downstream_target_gate_count"] == 4
    assert fallback["downstream_ready_target_gate_count"] == 0
    assert fallback["downstream_blocked_target_gate_count"] == 4
    assert fallback["downstream_target_gate_preflight_next_operator_action"] == (
        "R8p_fix_field_rows_source_preflight"
    )
    assert fallback["downstream_target_gate_preflight_path"].endswith(
        "pressure_resolution_replay_rows_downstream_target_gate_preflight.json"
    )
    assert fallback["field_rows_downstream_target_gate_result_preflight_status"] == (
        "downstream_target_gate_result_preflight_blocked_by_target_gate_preflight"
    )
    assert fallback["downstream_target_gate_result_submitted_count"] == 0
    assert fallback["downstream_target_gate_result_accepted_count"] == 0
    assert fallback["downstream_target_gate_result_rejected_count"] == 0
    assert fallback["downstream_target_gate_result_next_operator_action"] == (
        "R8p_fix_field_rows_source_preflight"
    )
    assert fallback["downstream_target_gate_result_preflight_path"].endswith(
        "pressure_resolution_replay_rows_downstream_target_gate_result_preflight.json"
    )
    assert fallback["field_rows_downstream_target_gate_result_arbitration_status"] == (
        "downstream_target_gate_result_arbitration_blocked_by_result_preflight"
    )
    assert fallback["downstream_target_gate_result_arbitration_next_operator_action"] == (
        "R8p_fix_field_rows_source_preflight"
    )
    assert fallback["downstream_target_gate_result_can_route_to_operator_review"] is False
    assert fallback["downstream_target_gate_result_can_emit_protective_control_candidate"] is False
    assert fallback["field_rows_downstream_target_gate_post_review_gate_status"] == (
        "downstream_target_gate_post_review_gate_blocked_by_operator_review_preflight"
    )
    assert fallback["downstream_target_gate_post_review_can_route_to_protective_candidate"] is False
    assert fallback["downstream_target_gate_post_review_can_emit_protective_control_candidate"] is False
    assert fallback["field_rows_downstream_target_gate_protective_candidate_evaluation_status"] == (
        "protective_candidate_evaluation_blocked_by_post_review_gate"
    )
    assert fallback["downstream_target_gate_protective_candidate_can_emit"] is False
    assert fallback["downstream_target_gate_protective_candidate_can_route_to_final_execution_review"] is False
    assert fallback["field_rows_provenance_gate_status"] == "all_required_tables_require_field_origin"
    assert fallback["field_rows_all_tables_require_data_origin"] is True
    assert fallback["field_rows_provenance_required_table_count"] == 6
    assert fallback["r7_completion_plan_status"] == "r7_to_r8p_completion_plan_waiting_for_r7_package"
    assert fallback["r7_completion_item_count"] == 6
    assert fallback["r7_completion_item_class_counts"]["operator_supplement"] == 4
    assert fallback["r7_completion_field_gap_count_by_class"]["agent52_replay_export"] == 11
    assert fallback["r7_completion_plan_path"].endswith(
        "pressure_resolution_replay_rows_r7_completion_plan.json"
    )
    assert fallback["r7_completion_required_execution_order"][-1] == (
        "R8U22_AGENT52_REPLAY_EXPORT_AGENT52_REPLAY_TABLE"
    )
    assert fallback["r7_completion_route_contracts_status"] == (
        "completion_route_contracts_ready_waiting_for_r7_package"
    )
    assert fallback["r7_completion_route_contract_count"] == 4
    assert fallback["r7_completion_open_route_count"] == 4
    assert fallback["r7_completion_open_route_ids"][0] == "r7_source_package"
    assert fallback["r7_completion_route_contracts_path"].endswith(
        "pressure_resolution_replay_rows_r7_completion_route_contracts.json"
    )
    assert fallback["r7_completion_route_work_packages_status"] == (
        "route_work_packages_ready_waiting_for_r7_package"
    )
    assert fallback["r7_completion_route_work_package_count"] == 4
    assert fallback["r7_completion_open_work_package_count"] == 4
    assert fallback["r7_completion_open_work_package_ids"][0] == "R8U25_R7_SOURCE_PACKAGE_WORK_PACKAGE"
    assert fallback["r7_completion_route_work_packages_path"].endswith(
        "pressure_resolution_replay_rows_r7_completion_route_work_packages.json"
    )
    assert fallback["r7_completion_route_work_package_templates_status"] == (
        "route_work_package_templates_ready_not_evidence"
    )
    assert fallback["r7_completion_route_work_package_preflight_status"] == (
        "route_work_package_preflight_waiting_for_submission_dir"
    )
    assert fallback["r7_completion_submitted_work_package_count"] == 0
    assert fallback["r7_completion_passed_work_package_count"] == 0
    assert fallback["r7_completion_blocked_work_package_count"] == 4
    assert fallback["r7_completion_route_work_package_preflight_path"].endswith(
        "pressure_resolution_replay_rows_r7_completion_route_work_package_preflight.json"
    )
    assert fallback["r7_completion_route_work_package_patch_plan_status"] == (
        "route_work_package_patch_plan_waiting_for_submission_dir"
    )
    assert fallback["r7_completion_route_work_package_patch_item_count"] == 1
    assert fallback["r7_completion_route_work_package_highest_priority_patch_id"] == (
        "R8U27_SET_R7_TO_R8P_WORK_PACKAGE_DIR"
    )
    assert fallback["r7_completion_route_work_package_patch_plan_path"].endswith(
        "pressure_resolution_replay_rows_r7_completion_route_work_package_patch_plan.json"
    )
    assert fallback["r7_completion_route_work_package_assembly_gate_status"] == (
        "route_work_package_assembly_gate_blocked_waiting_for_submission_dir"
    )
    assert fallback["r7_completion_route_work_package_assembly_step_count"] == 6
    assert fallback["r7_completion_route_work_package_ready_assembly_step_count"] == 0
    assert fallback["r7_completion_route_work_package_blocked_assembly_step_count"] == 6
    assert fallback["r7_completion_route_work_package_assembly_gate_path"].endswith(
        "pressure_resolution_replay_rows_r7_completion_route_work_package_assembly_gate.json"
    )
    assert fallback["submission_readiness_review_status"] == (
        "submission_readiness_review_blocked_at_source_package"
    )
    assert fallback["submission_readiness_next_operator_action"] == "R8p_fix_field_rows_source_preflight"
    assert fallback["submission_readiness_can_route_to_r8v"] is False
    assert fallback["submission_readiness_direct_highest_priority_patch_id"] == (
        "R8P_SOURCE_MISSING_FIELD_ROWS_FILE"
    )
    assert fallback["submission_readiness_r7_highest_priority_patch_id"] == (
        "R8U27_SET_R7_TO_R8P_WORK_PACKAGE_DIR"
    )
    assert fallback["submission_readiness_review_path"].endswith(
        "pressure_resolution_replay_rows_submission_readiness_review.json"
    )
    assert fallback["source_package_route_guide_status"] == (
        "source_package_submission_route_guide_ready_for_source_package_submission"
    )
    assert fallback["source_package_recommended_route_id"] == "direct_r8p_json_or_csv_source_package"
    assert fallback["source_package_next_operator_action"] == "R8p_submit_direct_json_or_csv_source_package"
    assert fallback["source_package_route_option_count"] == 3
    assert fallback["source_package_route_guide_path"].endswith(
        "pressure_resolution_replay_rows_source_package_submission_route_guide.json"
    )
    assert fallback["source_package_route_preflight_status"] == (
        "source_package_route_preflight_waiting_for_source_package_submission"
    )
    assert fallback["source_package_recommended_route_preflight_status"] == (
        "recommended_route_preflight_waiting_for_direct_source_package"
    )
    assert fallback["source_package_route_preflight_next_operator_action"] == (
        "R8p_submit_direct_json_or_csv_source_package"
    )
    assert fallback["source_package_ready_route_count"] == 0
    assert fallback["source_package_waiting_route_count"] == 3
    assert fallback["source_package_blocked_route_count"] == 0
    assert fallback["source_package_route_preflight_path"].endswith(
        "pressure_resolution_replay_rows_source_package_route_preflight.json"
    )
    assert fallback["schema_validation_summary"]["missing_table_count"] == 6
    assert fallback["validation_command"] == (
        ".venv/bin/python experiments/run_agent61_pressure_resolution_replay_scenario_pack.py"
    )
    assert fallback["env_override_name"] == "PRESSURE_RESOLUTION_REPLAY_ROWS_PATH"
    assert fallback["default_field_rows_path"].endswith("pressure_resolution_replay_rows.json")
    assert fallback["template_rows_path"].endswith("pressure_resolution_replay_rows_template.json")
    assert fallback["rows_schema_path"].endswith("pressure_resolution_replay_rows_schema.json")
    assert fallback["collection_checklist_path"].endswith(
        "pressure_resolution_replay_rows_collection_checklist.json"
    )
    assert "补包计划" in fallback["reason"]
    assert "can_write_to_actuator" in fallback["expected_metrics"]
    assert "field_rows_operator_handoff_status" in fallback["expected_metrics"]
    assert "field_rows_package_schema_status" in fallback["expected_metrics"]
    assert "field_rows_schema_validation_status" in fallback["expected_metrics"]
    assert "field_rows_schema_template_marker_gap_count" in fallback["expected_metrics"]
    assert "field_rows_schema_field_origin_gap_count" in fallback["expected_metrics"]
    assert "field_rows_collection_checklist_status" in fallback["expected_metrics"]
    assert "field_rows_batch_bundle_preflight_status" in fallback["expected_metrics"]
    assert "field_rows_complete_batch_bundle_count" in fallback["expected_metrics"]
    assert "field_rows_partial_batch_bundle_count" in fallback["expected_metrics"]
    assert "field_rows_missing_bundle_table_count" in fallback["expected_metrics"]
    assert "field_rows_temporal_window_preflight_status" in fallback["expected_metrics"]
    assert "field_rows_temporal_valid_batch_count" in fallback["expected_metrics"]
    assert "field_rows_temporal_violation_count" in fallback["expected_metrics"]
    assert "field_rows_hold_time_violation_count" in fallback["expected_metrics"]
    assert "field_rows_scenario_semantic_preflight_status" in fallback["expected_metrics"]
    assert "field_rows_semantic_valid_batch_count" in fallback["expected_metrics"]
    assert "field_rows_semantic_violation_count" in fallback["expected_metrics"]
    assert "field_rows_downstream_routing_preflight_status" in fallback["expected_metrics"]
    assert "field_rows_routing_ready_target_count" in fallback["expected_metrics"]
    assert "field_rows_downstream_routing_target_count" in fallback["expected_metrics"]
    assert "field_rows_provenance_gate_status" in fallback["expected_metrics"]
    assert "field_rows_all_tables_require_data_origin" in fallback["expected_metrics"]
    assert "r7_completion_plan_status" in fallback["expected_metrics"]
    assert "r7_completion_item_class_counts" in fallback["expected_metrics"]
    assert "r7_completion_field_gap_count_by_class" in fallback["expected_metrics"]
    assert "r7_completion_required_execution_order" in fallback["expected_metrics"]
    assert "r7_completion_route_contracts_status" in fallback["expected_metrics"]
    assert "r7_completion_open_route_count" in fallback["expected_metrics"]
    assert "r7_completion_open_route_ids" in fallback["expected_metrics"]
    assert "r7_completion_route_work_packages_status" in fallback["expected_metrics"]
    assert "r7_completion_open_work_package_count" in fallback["expected_metrics"]
    assert "r7_completion_open_work_package_ids" in fallback["expected_metrics"]
    assert "r7_completion_route_work_package_preflight_status" in fallback["expected_metrics"]
    assert "r7_completion_submitted_work_package_count" in fallback["expected_metrics"]
    assert "r7_completion_passed_work_package_count" in fallback["expected_metrics"]
    assert "r7_completion_blocked_work_package_count" in fallback["expected_metrics"]
    assert "r7_completion_route_work_package_patch_plan_status" in fallback["expected_metrics"]
    assert "r7_completion_route_work_package_patch_item_count" in fallback["expected_metrics"]
    assert "r7_completion_route_work_package_highest_priority_patch_id" in fallback["expected_metrics"]
    assert "r7_completion_route_work_package_assembly_gate_status" in fallback["expected_metrics"]
    assert "r7_completion_route_work_package_assembly_step_count" in fallback["expected_metrics"]
    assert "r7_completion_route_work_package_ready_assembly_step_count" in fallback["expected_metrics"]
    assert "r7_completion_route_work_package_blocked_assembly_step_count" in fallback["expected_metrics"]
    assert "submission_readiness_review_status" in fallback["expected_metrics"]
    assert "submission_readiness_next_operator_action" in fallback["expected_metrics"]
    assert "submission_readiness_can_route_to_r8v" in fallback["expected_metrics"]
    assert "submission_readiness_direct_highest_priority_patch_id" in fallback["expected_metrics"]
    assert "submission_readiness_r7_highest_priority_patch_id" in fallback["expected_metrics"]
    assert "source_package_route_guide_status" in fallback["expected_metrics"]
    assert "source_package_recommended_route_id" in fallback["expected_metrics"]
    assert "source_package_next_operator_action" in fallback["expected_metrics"]
    assert "source_package_route_option_count" in fallback["expected_metrics"]
    assert "source_package_route_preflight_status" in fallback["expected_metrics"]
    assert "source_package_recommended_route_preflight_status" in fallback["expected_metrics"]
    assert "source_package_route_preflight_next_operator_action" in fallback["expected_metrics"]
    assert "source_package_ready_route_count" in fallback["expected_metrics"]
    assert "source_package_waiting_route_count" in fallback["expected_metrics"]
    assert "source_package_blocked_route_count" in fallback["expected_metrics"]
    assert "field_rows_downstream_route_handoff_status" in fallback["expected_metrics"]
    assert "field_rows_downstream_ready_handoff_target_count" in fallback["expected_metrics"]
    assert "field_rows_downstream_blocked_handoff_target_count" in fallback["expected_metrics"]
    assert "field_rows_downstream_route_handoff_next_operator_action" in fallback["expected_metrics"]
    assert "field_rows_downstream_target_gate_preflight_status" in fallback["expected_metrics"]
    assert "field_rows_downstream_ready_target_gate_count" in fallback["expected_metrics"]
    assert "field_rows_downstream_blocked_target_gate_count" in fallback["expected_metrics"]
    assert "field_rows_downstream_target_gate_preflight_next_operator_action" in fallback["expected_metrics"]
    assert "field_rows_downstream_target_gate_result_preflight_status" in fallback["expected_metrics"]
    assert "field_rows_downstream_target_gate_result_submitted_count" in fallback["expected_metrics"]
    assert "field_rows_downstream_target_gate_result_accepted_count" in fallback["expected_metrics"]
    assert "field_rows_downstream_target_gate_result_rejected_count" in fallback["expected_metrics"]
    assert "field_rows_downstream_target_gate_result_next_operator_action" in fallback["expected_metrics"]
    assert "field_rows_downstream_target_gate_result_arbitration_status" in fallback["expected_metrics"]
    assert "field_rows_downstream_target_gate_result_arbitration_next_operator_action" in fallback["expected_metrics"]
    assert "field_rows_downstream_target_gate_result_can_route_to_operator_review" in fallback["expected_metrics"]
    assert (
        "field_rows_downstream_target_gate_result_can_emit_protective_control_candidate"
        in fallback["expected_metrics"]
    )


def test_architecture_consolidation_advances_fallback_after_pressure_resolution_rows_accepted() -> None:
    core_metrics = _pressure_headloss_chain_core_metrics(
        include_r8e=True,
        include_r8f=True,
        include_r8g=True,
        include_r8h=True,
        include_r8i=True,
        include_r8j=True,
        include_r8k=True,
        include_r8l=True,
        include_r8n=True,
        include_r8o=True,
        include_r8p=True,
    )

    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        core_metrics=core_metrics,
    ).run([])

    fallback = report.metrics["offline_core_fallback_action"]

    assert fallback["fallback_enabled"] is True
    assert fallback["action_id"] == "R8v_route_pressure_resolution_rows_to_field_replay_and_holdout_gates"
    assert "field_scenario_coverage=1.000" in fallback["trigger_metric"]
    assert (
        "downstream_routing_preflight_status=downstream_routing_preflight_passed_ready_for_r8v_field_replay_and_holdout_gates"
        in fallback["trigger_metric"]
    )
    assert "downstream_route_handoff_status=downstream_route_handoff_ready_for_r8v_target_gates" in fallback[
        "trigger_metric"
    ]
    assert "downstream_ready_handoff_target_count=4" in fallback["trigger_metric"]
    assert "downstream_blocked_handoff_target_count=0" in fallback["trigger_metric"]
    assert "downstream_target_gate_preflight_status=downstream_target_gate_preflight_ready_for_r8v_execution" in fallback[
        "trigger_metric"
    ]
    assert "downstream_ready_target_gate_count=4" in fallback["trigger_metric"]
    assert "downstream_blocked_target_gate_count=0" in fallback["trigger_metric"]
    assert (
        "downstream_target_gate_result_preflight_status="
        "downstream_target_gate_result_preflight_waiting_for_result_package"
        in fallback["trigger_metric"]
    )
    assert "downstream_target_gate_result_submitted_count=0" in fallback["trigger_metric"]
    assert "downstream_target_gate_result_accepted_count=0" in fallback["trigger_metric"]
    assert "downstream_target_gate_result_rejected_count=0" in fallback["trigger_metric"]
    assert (
        "downstream_target_gate_result_next_operator_action=R8v_submit_target_gate_result_package"
        in fallback["trigger_metric"]
    )
    assert (
        "downstream_target_gate_result_arbitration_status="
        "downstream_target_gate_result_arbitration_blocked_by_result_preflight"
        in fallback["trigger_metric"]
    )
    assert (
        "downstream_target_gate_result_arbitration_next_operator_action=R8v_submit_target_gate_result_package"
        in fallback["trigger_metric"]
    )
    assert "downstream_target_gate_result_can_route_to_operator_review=False" in fallback["trigger_metric"]
    assert (
        "downstream_target_gate_result_can_emit_protective_control_candidate=False"
        in fallback["trigger_metric"]
    )
    assert "field_rows_downstream_routing_preflight_status" in fallback["expected_metrics"]
    assert "field_rows_routing_ready_target_count" in fallback["expected_metrics"]
    assert "field_rows_downstream_route_handoff_status" in fallback["expected_metrics"]
    assert "field_rows_downstream_ready_handoff_target_count" in fallback["expected_metrics"]
    assert "field_rows_downstream_target_gate_preflight_status" in fallback["expected_metrics"]
    assert "field_rows_downstream_ready_target_gate_count" in fallback["expected_metrics"]
    assert "field_rows_downstream_blocked_target_gate_count" in fallback["expected_metrics"]
    assert "field_rows_downstream_target_gate_result_preflight_status" in fallback["expected_metrics"]
    assert "field_rows_downstream_target_gate_result_submitted_count" in fallback["expected_metrics"]
    assert "field_rows_downstream_target_gate_result_accepted_count" in fallback["expected_metrics"]
    assert "field_rows_downstream_target_gate_result_rejected_count" in fallback["expected_metrics"]
    assert "field_rows_downstream_target_gate_result_next_operator_action" in fallback["expected_metrics"]
    assert "field_rows_downstream_target_gate_result_arbitration_status" in fallback["expected_metrics"]
    assert "field_rows_downstream_target_gate_result_arbitration_next_operator_action" in fallback["expected_metrics"]
    assert "field_rows_downstream_target_gate_result_can_route_to_operator_review" in fallback["expected_metrics"]
    assert (
        "field_rows_downstream_target_gate_result_can_emit_protective_control_candidate"
        in fallback["expected_metrics"]
    )
    assert fallback["field_rows_downstream_route_handoff_status"] == (
        "downstream_route_handoff_ready_for_r8v_target_gates"
    )
    assert fallback["downstream_handoff_target_count"] == 4
    assert fallback["downstream_ready_handoff_target_count"] == 4
    assert fallback["downstream_blocked_handoff_target_count"] == 0
    assert fallback["downstream_route_handoff_summary"]["can_write_to_actuator"] is False
    assert fallback["downstream_route_handoff_summary"]["can_write_to_release_gate"] is False
    assert fallback["field_rows_downstream_target_gate_preflight_status"] == (
        "downstream_target_gate_preflight_ready_for_r8v_execution"
    )
    assert fallback["downstream_target_gate_count"] == 4
    assert fallback["downstream_ready_target_gate_count"] == 4
    assert fallback["downstream_blocked_target_gate_count"] == 0
    assert fallback["downstream_target_gate_preflight_summary"]["can_write_to_actuator"] is False
    assert fallback["downstream_target_gate_preflight_summary"]["can_write_to_release_gate"] is False
    assert fallback["field_rows_downstream_target_gate_result_preflight_status"] == (
        "downstream_target_gate_result_preflight_waiting_for_result_package"
    )
    assert fallback["downstream_target_gate_result_submitted_count"] == 0
    assert fallback["downstream_target_gate_result_accepted_count"] == 0
    assert fallback["downstream_target_gate_result_rejected_count"] == 0
    assert fallback["downstream_target_gate_result_next_operator_action"] == (
        "R8v_submit_target_gate_result_package"
    )
    assert fallback["downstream_target_gate_result_preflight_summary"]["can_write_to_actuator"] is False
    assert fallback["downstream_target_gate_result_preflight_summary"]["can_write_to_release_gate"] is False
    assert fallback["field_rows_downstream_target_gate_result_arbitration_status"] == (
        "downstream_target_gate_result_arbitration_blocked_by_result_preflight"
    )
    assert fallback["downstream_target_gate_result_arbitration_next_operator_action"] == (
        "R8v_submit_target_gate_result_package"
    )
    assert fallback["downstream_target_gate_result_can_route_to_operator_review"] is False
    assert fallback["downstream_target_gate_result_can_emit_protective_control_candidate"] is False
    assert fallback["downstream_target_gate_result_arbitration_summary"]["can_write_to_actuator"] is False
    assert fallback["downstream_target_gate_result_arbitration_summary"]["can_write_to_release_gate"] is False
    assert fallback["field_rows_downstream_target_gate_post_review_gate_status"] == (
        "downstream_target_gate_post_review_gate_blocked_by_operator_review_preflight"
    )
    assert fallback["downstream_target_gate_post_review_can_route_to_protective_candidate"] is False
    assert fallback["downstream_target_gate_post_review_can_emit_protective_control_candidate"] is False
    assert fallback["field_rows_downstream_target_gate_protective_candidate_evaluation_status"] == (
        "protective_candidate_evaluation_blocked_by_post_review_gate"
    )
    assert fallback["downstream_target_gate_protective_candidate_can_emit"] is False
    assert fallback["downstream_target_gate_protective_candidate_can_route_to_final_execution_review"] is False
    assert "Agent51" in fallback["reason"]
    assert "can_write_to_actuator" in fallback["expected_metrics"]


def test_architecture_consolidation_promotes_r7_claim_specific_coverage_gap() -> None:
    core_metrics = _r4b_ready_core_metrics(unmet_count=0, unmet_fields=[], source_basis_rate=1.0)
    core_metrics["real_field_package_acceptance_gate_metrics"] = {
        "readiness": {
            "real_field_package_acceptance_status": "real_field_package_acceptance_blocked_at_claim_specific_package",
            "passed_stage_count": 5,
            "total_stage_count": 7,
            "blocking_reasons": ["claim_specific_real_field_rows_not_passed"],
            "next_recommended_core_action": "R7d_link_claim_specific_field_rows",
        }
    }
    core_metrics["r7_real_field_replay_pipeline_metrics"] = {
        "pipeline_readiness": {
            "field_package_coverage_status": "field_package_claim_specific_coverage_gaps",
            "claim_specific_coverage_rate": 0.6,
            "soft_holdout_coverage_pass": True,
            "r7_next_action": "R7d_link_claim_specific_field_rows",
        },
        "field_package_coverage": {
            "next_actions": [
                "Patch claim need FVQ01: claim_required_fields_empty.",
                "Coverage readiness is not deployment permission; actuator and release-gate writeback remain forbidden.",
            ]
        },
    }

    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        core_metrics=core_metrics,
    ).run([])

    top = report.metrics["ranked_refactor_actions"][0]

    assert top["action_id"] == "R7g_patch_field_package_claim_specific_coverage"
    assert "claim_specific_coverage_rate=0.600" in top["trigger_metric"]
    assert "Patch claim need FVQ01" in top["current_blockers"]


def test_architecture_consolidation_promotes_r7_soft_holdout_weak_target_gap() -> None:
    core_metrics = _r4b_ready_core_metrics(unmet_count=0, unmet_fields=[], source_basis_rate=1.0)
    core_metrics["real_field_package_acceptance_gate_metrics"] = {
        "readiness": {
            "real_field_package_acceptance_status": "real_field_package_acceptance_blocked_at_soft_holdout",
            "passed_stage_count": 4,
            "total_stage_count": 7,
            "blocking_reasons": ["soft_sensor_field_holdout_gate_not_passed"],
            "next_recommended_core_action": "R7c_collect_soft_sensor_field_holdout_labels",
        }
    }
    core_metrics["r7_real_field_replay_pipeline_metrics"] = {
        "pipeline_readiness": {
            "field_package_coverage_status": "field_package_soft_holdout_coverage_gaps",
            "claim_specific_coverage_rate": 1.0,
            "soft_holdout_coverage_pass": False,
            "r7_next_action": "R7c_collect_soft_sensor_field_holdout_labels",
        },
        "field_package_coverage": {
            "next_actions": [
                "Add offline_lab_results analytes for weak targets: catalyst_activity, matrix_interference."
            ]
        },
    }

    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        core_metrics=core_metrics,
    ).run([])

    top = report.metrics["ranked_refactor_actions"][0]

    assert top["action_id"] == "R7h_patch_soft_holdout_weak_target_labels"
    assert "soft_holdout_coverage_pass=False" in top["trigger_metric"]
    assert "catalyst_activity" in top["implementation_path"]


def test_architecture_consolidation_promotes_r7_minimum_replay_contract_gap() -> None:
    core_metrics = _r4b_ready_core_metrics(unmet_count=0, unmet_fields=[], source_basis_rate=1.0)
    core_metrics["real_field_package_acceptance_gate_metrics"] = {
        "readiness": {
            "real_field_package_acceptance_status": "real_field_package_acceptance_blocked_at_timestamped_replay",
            "passed_stage_count": 1,
            "total_stage_count": 7,
            "blocking_reasons": ["timestamped_replay_not_field_ready"],
            "next_recommended_core_action": "R7b_run_timestamped_replay_g6_and_evidence_chain",
        }
    }
    core_metrics["r7_real_field_replay_pipeline_metrics"] = {
        "pipeline_readiness": {
            "field_package_coverage_status": "field_package_coverage_ready_for_replay_and_holdout",
            "claim_specific_coverage_rate": 1.0,
            "soft_holdout_coverage_pass": True,
            "minimum_replay_contract_status": "minimum_replay_contract_batch_linkage_gaps",
            "minimum_common_batch_count": 1,
            "minimum_valid_matched_batch_count": 1,
            "minimum_valid_operation_action_count": 2,
            "minimum_invalid_operation_action_count": 1,
            "minimum_valid_lab_result_count": 2,
            "minimum_invalid_lab_result_count": 1,
            "minimum_valid_proxy_label_count": 2,
            "minimum_invalid_proxy_label_count": 1,
            "coverage_patch_plan_status": "patch_plan_requires_minimum_replay_contract",
            "coverage_patch_plan_item_count": 1,
            "r7_next_action": "R7b_run_timestamped_replay_g6_and_evidence_chain",
        },
        "field_package_coverage": {
            "patch_plan": {
                "patch_plan_status": "patch_plan_requires_minimum_replay_contract",
                "item_count": 1,
            }
        },
    }

    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        core_metrics=core_metrics,
    ).run([])

    top = report.metrics["ranked_refactor_actions"][0]

    assert top["action_id"] == "R7i_patch_minimum_replay_batch_linkage"
    assert "minimum_common_batch_count=1" in top["trigger_metric"]
    assert "minimum_valid_matched_batch_count=1" in top["trigger_metric"]
    assert "minimum_valid_operation_action_count=2" in top["trigger_metric"]
    assert "minimum_valid_lab_result_count=2" in top["trigger_metric"]
    assert "minimum_valid_proxy_label_count=2" in top["trigger_metric"]
    assert "共同 batch_id" in top["implementation_path"]


def test_architecture_consolidation_flags_unmapped_agent_before_refactor() -> None:
    report = AgentArchitectureConsolidationAgent(agent_names=["new_unknown_agent"]).run([])

    assert report.metrics["unmapped_agent_count"] == 1
    assert report.metrics["module_board"][-1]["module_id"] == "UNMAPPED"
    assert any(issue.issue_type == "unmapped_agent_detected" for issue in report.issues)


def test_architecture_consolidation_validates_external_evidence_schema() -> None:
    incomplete = [{field: "filled" for field in REQUIRED_ARCHITECTURE_EVIDENCE_FIELDS[:-1]}]

    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        external_architecture_evidence=incomplete,
    ).run([])

    status = report.metrics["external_architecture_evidence_status"]
    assert status["status"] == "architecture_evidence_needs_patch"
    assert status["incomplete_records"][0]["missing"] == ["failure_boundary"]
    assert any(issue.issue_type == "architecture_evidence_incomplete" for issue in report.issues)


def _r4b_ready_core_metrics(
    *,
    unmet_count: int,
    unmet_fields: list[str],
    source_basis_rate: float = 0.225,
) -> dict[str, object]:
    return {
        "unified_field_evidence_gate_metrics": {
            "readiness": {
                "unified_field_evidence_gate_status": "unified_gate_ready_blocking_field_claim_upgrade",
                "gate_source_consolidation_coverage": 1.0,
                "citation_detail_completion_rate": 1.0,
            }
        },
        "observation_contract_metrics": {
            "readiness": {
                "observation_contract_status": (
                    "synthetic_observation_contract_ready_needs_field_topology_proxy_labels_and_missingness"
                ),
                "budget_pass": True,
                "proxy_enhanced_weak_state_coverage": 0.58,
            }
        },
        "control_replay_stress_metrics": {
            "readiness": {
                "control_replay_stress_status": "synthetic_counterfactual_stress_ready_needs_field_replay",
                "can_update_agent49_reward_prior": True,
            },
            "counterfactual_metrics": {
                "guardrail_candidate": {"joint_action_accuracy": 1.0},
            },
        },
        "collaborative_control_metrics": {
            "readiness": {
                "control_replay_guardrails_integrated": True,
            },
            "control_replay_guardrail_context": {
                "reward_prior_guardrail_available": True,
            },
        },
        "replay_evaluation_metrics": {
            "readiness": {
                "guardrail_aware_replay_ready": True,
            },
            "offline_evaluation_metrics": {
                "control_replay_guardrails_integrated": True,
                "guardrail_aware_regret_delta": 0.055,
            },
        },
        "control_guardrail_backpropagation_metrics": {
            "readiness": {
                "backpropagation_ready": True,
            },
            "coverage_metrics": {
                "resolved_case_to_mechanism_coverage": 1.0,
            },
        },
        "minimal_grey_box_physics_metrics": {
            "readiness": {
                "agent53_guardrail_boundary_consumption_rate": 1.0,
            }
        },
        "field_validation_queue_alignment_metrics": {
            "readiness": {
                "field_requirement_patch_consumption_rate": 1.0,
            }
        },
        "claim_specific_field_package_metrics": {
            "readiness": {
                "field_requirement_patch_consumption_rate": 1.0,
                "unmet_guardrail_field_count": unmet_count,
                "unmet_guardrail_fields": unmet_fields,
                "source_basis_completion_rate": source_basis_rate,
                "minimal_field_package_field_pass_rate": 0.0,
            }
        },
    }


def _agent48_hidden_state_ledger_metrics(*, with_pressure_pool: bool = False) -> dict[str, object]:
    ledger = {
        "coverage": {"weak_state_coverage": 0.3},
        "hidden_state_requirement_ledger": {
            "ledger_status": "hidden_state_requirement_ledger_ready_with_gaps",
            "ready_hidden_state_count": 4,
            "hidden_state_count": 6,
            "minimum_cost_requirement_patch": {
                "patch_status": "minimum_cost_patch_requires_new_modality_or_field_label",
                "hard_unresolved_hidden_states": ["catalyst_activity"],
            },
        },
    }
    if with_pressure_pool:
        ledger["hidden_state_requirement_ledger"]["pressure_headloss_candidate_pool"] = {
            "pool_status": "pressure_headloss_candidate_pool_ready_needs_field_topology_and_labels",
            "candidate_count": 3,
            "candidate_ids": [
                "N3_catalyst_bed:pressure_drop_kPa",
                "N3_catalyst_bed:headloss_kPa_per_m",
                "N3_catalyst_bed:flow_normalized_pressure_residual",
            ],
        }
        ledger["hidden_state_requirement_ledger"]["minimum_cost_requirement_patch"][
            "pressure_headloss_candidate_pool_status"
        ] = "pressure_headloss_candidate_pool_ready_needs_field_topology_and_labels"
    return ledger


def _pressure_headloss_chain_core_metrics(
    *,
    include_r8e: bool = False,
    include_r8f: bool = False,
    include_r8g: bool = False,
    include_r8h: bool = False,
    include_r8i: bool = False,
    include_r8j: bool = False,
    include_r8k: bool = False,
    include_r8l: bool = False,
    include_r8m: bool = False,
    include_r8n: bool = False,
    include_r8o: bool = False,
    include_r8p: bool = False,
) -> dict[str, object]:
    core_metrics = _r4b_ready_core_metrics(unmet_count=0, unmet_fields=[], source_basis_rate=1.0)
    core_metrics["real_field_package_acceptance_gate_metrics"] = {
        "readiness": {
            "real_field_package_acceptance_status": "real_field_package_acceptance_blocked_at_import",
            "passed_stage_count": 0,
            "total_stage_count": 8,
            "blocking_reasons": ["field_package_not_imported_or_data_origin_not_field"],
            "next_recommended_core_action": "R7a_import_real_field_package_with_metadata_and_csv",
        }
    }
    core_metrics["agent48_metrics"] = _agent48_hidden_state_ledger_metrics(with_pressure_pool=True)
    core_metrics["observation_contract_metrics"] = {
        "readiness": {
            "observation_contract_status": (
                "synthetic_observation_contract_ready_needs_field_topology_proxy_labels_and_missingness"
            ),
            "budget_pass": True,
            "proxy_enhanced_weak_state_coverage": 0.58,
            "agent48_pressure_headloss_candidate_pool_status": (
                "pressure_headloss_candidate_pool_ready_needs_field_topology_and_labels"
            ),
            "agent48_pressure_headloss_candidate_count": 3,
        },
        "field_validation_requirements": [
            {
                "requirement_id": "R2_FV4_agent48_hidden_state_requirement_patch",
                "pressure_headloss_candidate_ids": ["N3_catalyst_bed:pressure_drop_kPa"],
            }
        ],
    }
    core_metrics["soft_sensor_matrix_metrics"] = {
        "readiness": {
            "pressure_headloss_candidate_pool_status": (
                "pressure_headloss_candidate_pool_ready_needs_field_topology_and_labels"
            ),
            "pressure_headloss_candidate_count": 3,
        }
    }
    core_metrics["collaborative_control_metrics"]["control_replay_guardrail_context"].update(
        {
            "pressure_headloss_consumed_by_agent49": True,
            "pressure_headloss_candidate_count": 3,
        }
    )
    core_metrics["replay_evaluation_metrics"]["offline_evaluation_metrics"].update(
        {
            "pressure_headloss_boundary_consumed": True,
            "pressure_headloss_candidate_count": 3,
            "pressure_headloss_blocked_guardrail_case_count": 2,
        }
    )
    if include_r8e:
        core_metrics["field_data_interface_metrics"] = {
            "field_data_interface": {
                "metrics": {
                    "schema_contract": {"site_topology_or_bed_geometry": {}},
                    "template_headers": {
                        "sensor_timeseries": ["pressure_drop_kPa", "headloss_kPa_per_m"],
                        "campaign_operation_log": ["pressure_headloss_review_required"],
                    },
                }
            }
        }
        core_metrics["timestamped_campaign_replay_metrics"] = {
            "timestamped_campaign_replay": {
                "metrics": {
                    "replay_schema_contract": {"pressure_headloss_event_log": {}},
                    "template_headers": {"sensor_timeseries": ["pressure_drop_kPa"]},
                    "replay_metrics": {
                        "pressure_headloss_event_count": 3,
                        "pressure_headloss_matched_batch_count": 3,
                    },
                    "linkage": {"pressure_headloss_without_lab_batches": []},
                }
            }
        }
    if include_r8f:
        core_metrics["field_replay_import_metrics"] = {
            "table_import_audit": {"pressure_headloss_event_log": {"status": "import_ready"}},
            "linkage_audit": {
                "pressure_headloss_batch_count": 3,
                "pressure_headloss_without_lab_batches": [],
            },
            "readiness": {"accepted_table_count": 5, "total_table_count": 5},
        }
    if include_r8g:
        core_metrics["r7_real_field_replay_pipeline_metrics"] = {
            "field_package_coverage": {
                "minimum_replay_contract_audit": {
                    "required_tables": [
                        "sensor_timeseries",
                        "offline_lab_results",
                        "campaign_operation_log",
                        "fast_proxy_event_log",
                        "pressure_headloss_event_log",
                    ],
                    "table_row_counts": {
                        "sensor_timeseries": 0,
                        "offline_lab_results": 0,
                        "campaign_operation_log": 0,
                        "fast_proxy_event_log": 0,
                        "pressure_headloss_event_log": 0,
                    },
                    "pressure_headloss_event_count": 0,
                    "valid_pressure_headloss_event_count": 0,
                    "valid_pressure_headloss_batch_count": 0,
                }
            },
            "pipeline_readiness": {
                "minimum_pressure_headloss_event_count": 0,
                "minimum_valid_pressure_headloss_event_count": 0,
                "minimum_valid_pressure_headloss_batch_count": 0,
            },
        }
    if include_r8h:
        r7_metrics = core_metrics.setdefault("r7_real_field_replay_pipeline_metrics", {})
        r7_metrics["preflight"] = {
            "agent44_blocking_table_statuses": {},
            "agent44_type_error_count": 0,
            "agent44_type_error_tables": {},
            "agent44_required_field_blockers": {},
            "agent44_linkage_blockers": {},
        }
        r7_metrics.setdefault("field_package_coverage", {}).setdefault(
            "patch_plan",
            {"patch_plan_status": "patch_plan_blocked_at_import_preflight"},
        )
    if include_r8i:
        core_metrics["catalyst_proxy_metrics"] = {
            "method_contract": {
                "data_needs": [
                    "pressure_headloss_event_log.pressure_drop_kPa",
                    "pressure_headloss_event_log.headloss_kPa_per_m",
                ]
            },
            "readiness": {
                "pressure_evidence_source_contract": [
                    "node_modality_sensor_timeseries",
                    "pressure_headloss_event_log",
                ],
                "pressure_headloss_event_source_batch_count": 0,
            },
            "field_proxy_holdout_summary": {
                "accepted_pressure_evidence_sources": [],
                "pressure_headloss_event_source_batch_count": 0,
            },
        }
    if include_r8j:
        core_metrics["collaborative_control_metrics"]["control_replay_guardrail_context"].update(
            {
                "accepted_pressure_evidence_sources": ["pressure_headloss_event_log"],
                "pressure_headloss_event_source_batch_count": 3,
            }
        )
        core_metrics["replay_evaluation_metrics"]["catalyst_proxy_context"] = {
            "accepted_pressure_evidence_sources": ["pressure_headloss_event_log"],
            "pressure_headloss_event_source_batch_count": 3,
        }
    if include_r8k:
        summary = core_metrics["catalyst_proxy_metrics"]["field_proxy_holdout_summary"]
        summary.update(
            {
                "pressure_source_priority_policy": "node_modality_first_fill_missing_from_pressure_headloss_event_log",
                "pressure_source_conflict_count": 0,
                "pressure_source_conflicts": [],
                "conflict_requires_operator_review": False,
            }
        )
    if include_r8l:
        core_metrics["collaborative_control_metrics"]["control_replay_guardrail_context"].update(
            {
                "pressure_source_conflict_count": 0,
                "pressure_source_conflict_control_block": False,
                "conflict_requires_operator_review": False,
            }
        )
        core_metrics["replay_evaluation_metrics"].setdefault("offline_evaluation_metrics", {}).update(
            {
                "pressure_source_conflict_count": 0,
                "pressure_source_conflict_replay_blocked_case_count": 0,
            }
        )
        core_metrics["replay_evaluation_metrics"].setdefault("readiness", {}).update(
            {
                "pressure_source_conflict_requires_operator_review": False,
            }
        )
        core_metrics["replay_evaluation_metrics"].setdefault("agent49_writeback", {})["metric_patch"] = {
            "pressure_source_conflict_requires_operator_review": False,
        }
    if include_r8n:
        r7_metrics = core_metrics.setdefault("r7_real_field_replay_pipeline_metrics", {})
        r7_metrics.setdefault("pipeline_readiness", {}).update(
            {
                "pressure_source_conflict_count": 0,
                "pressure_source_conflict_requires_operator_review": False,
                "resolved_pressure_source_conflict_count": 0,
                "unresolved_pressure_source_conflict_count": 0,
                "pressure_source_resolution_record_count": 0,
                "field_package_pressure_conflict_resolution_status": "pressure_source_conflict_resolution_clear",
                "field_package_pressure_conflict_resolution_ready": True,
            }
        )
        coverage = r7_metrics.setdefault("field_package_coverage", {})
        coverage.setdefault("readiness", {}).update(
            {
                "pressure_source_conflict_count": 0,
                "pressure_source_conflict_requires_operator_review": False,
                "resolved_pressure_source_conflict_count": 0,
                "unresolved_pressure_source_conflict_count": 0,
                "pressure_source_resolution_record_count": 0,
                "field_package_pressure_conflict_resolution_status": "pressure_source_conflict_resolution_clear",
                "field_package_pressure_conflict_resolution_ready": True,
            }
        )
        core_metrics["collaborative_control_metrics"]["control_replay_guardrail_context"].update(
            {
                "resolved_pressure_source_conflict_count": 0,
                "unresolved_pressure_source_conflict_count": 0,
                "pressure_source_resolution_record_count": 0,
                "unresolved_pressure_source_conflicts": [],
                "pressure_source_resolutions": [],
            }
        )
        replay_metrics = core_metrics["replay_evaluation_metrics"]
        replay_metrics.setdefault("offline_evaluation_metrics", {}).update(
            {
                "resolved_pressure_source_conflict_count": 0,
                "unresolved_pressure_source_conflict_count": 0,
                "pressure_source_resolution_record_count": 0,
            }
        )
        replay_metrics.setdefault("readiness", {}).update(
            {
                "resolved_pressure_source_conflict_count": 0,
                "unresolved_pressure_source_conflict_count": 0,
                "pressure_source_resolution_record_count": 0,
                "pressure_source_conflict_clear": True,
            }
        )
        replay_metrics.setdefault("agent49_writeback", {}).setdefault("metric_patch", {}).update(
            {
                "resolved_pressure_source_conflict_count": 0,
                "unresolved_pressure_source_conflict_count": 0,
                "pressure_source_resolution_record_count": 0,
            }
        )
        replay_metrics["pressure_headloss_context"] = {
            "resolved_pressure_source_conflict_count": 0,
            "unresolved_pressure_source_conflict_count": 0,
            "pressure_source_resolution_record_count": 0,
        }
    if include_r8o:
        core_metrics["pressure_resolution_replay_scenario_pack_metrics"] = {
            "readiness": {
                "scenario_pack_status": "pressure_resolution_scenario_pack_ready_needs_real_replay_rows",
                "scenario_schema_coverage": 1.0,
                "field_scenario_coverage": 0.0,
                "source_chain_resolution_fields_ready": True,
                "can_update_agent60_fallback": True,
                "next_recommended_core_action": "R8p_collect_pressure_resolution_replay_rows",
            }
        }
    if include_r8p:
        core_metrics["pressure_resolution_replay_scenario_pack_metrics"] = {
            "readiness": {
                "scenario_pack_status": "pressure_resolution_scenario_pack_field_replay_ready_for_human_review",
                "scenario_schema_coverage": 1.0,
                "field_scenario_coverage": 1.0,
                "source_chain_resolution_fields_ready": True,
                "can_update_agent60_fallback": True,
                "can_upgrade_field_supported_claim": True,
                "next_recommended_core_action": (
                    "R8v_route_pressure_resolution_rows_to_field_replay_and_holdout_gates"
                ),
            },
            "field_row_acceptance": {
                "field_row_acceptance_status": "field_replay_rows_accepted_for_all_scenarios",
                "accepted_scenario_count": 5,
                "accepted_batch_count": 5,
            },
            "field_rows_downstream_routing_preflight": {
                "field_rows_downstream_routing_preflight_status": (
                    "downstream_routing_preflight_passed_ready_for_r8v_field_replay_and_holdout_gates"
                ),
                "can_route_to_r8v": True,
                "routing_target_count": 4,
                "routing_ready_target_count": 4,
                "accepted_batch_count": 5,
            },
            "field_rows_downstream_route_handoff": {
                "downstream_route_handoff_status": "downstream_route_handoff_ready_for_r8v_target_gates",
                "can_route_to_r8v": True,
                "handoff_target_count": 4,
                "ready_handoff_target_count": 4,
                "blocked_handoff_target_count": 0,
                "can_write_to_actuator": False,
                "can_write_to_release_gate": False,
                "field_claim_upgrade_allowed": False,
            },
            "field_rows_downstream_target_gate_preflight": {
                "downstream_target_gate_preflight_status": (
                    "downstream_target_gate_preflight_ready_for_r8v_execution"
                ),
                "target_gate_count": 4,
                "ready_target_gate_count": 4,
                "blocked_target_gate_count": 0,
                "next_operator_action": "R8v_execute_target_gates_in_order_and_collect_gate_metrics",
                "can_execute_all_target_gates": True,
                "can_write_to_actuator": False,
                "can_write_to_release_gate": False,
                "field_claim_upgrade_allowed": False,
            },
            "field_rows_downstream_target_gate_result_preflight": {
                "downstream_target_gate_result_preflight_status": (
                    "downstream_target_gate_result_preflight_waiting_for_result_package"
                ),
                "submitted_target_result_count": 0,
                "accepted_target_result_count": 0,
                "rejected_target_result_count": 0,
                "missing_target_ids": [
                    "agent51_catalyst_proxy_holdout",
                    "agent49_guardrail_context",
                    "agent52_replay_clearance",
                    "r7_evidence_chain",
                ],
                "next_operator_action": "R8v_submit_target_gate_result_package",
                "can_route_to_result_arbitration": False,
                "can_write_to_actuator": False,
                "can_write_to_release_gate": False,
                "field_claim_upgrade_allowed": False,
            },
            "field_rows_downstream_target_gate_result_arbitration": {
                "downstream_target_gate_result_arbitration_status": (
                    "downstream_target_gate_result_arbitration_blocked_by_result_preflight"
                ),
                "accepted_target_result_count": 0,
                "target_gate_status_counts": {
                    "target_gate_result_passed": 0,
                    "target_gate_result_failed": 0,
                    "target_gate_result_blocked": 0,
                    "target_gate_result_waiting_for_operator_review": 0,
                    "target_gate_result_invalid_or_missing": 0,
                },
                "next_operator_action": "R8v_submit_target_gate_result_package",
                "can_route_to_operator_review": False,
                "can_emit_protective_control_candidate": False,
                "can_write_to_actuator": False,
                "can_write_to_release_gate": False,
                "field_claim_upgrade_allowed": False,
            },
            "field_rows_downstream_target_gate_operator_review_preflight": {
                "downstream_target_gate_operator_review_preflight_status": (
                    "downstream_target_gate_operator_review_preflight_blocked_by_result_arbitration"
                ),
                "approved_operator_review_count": 0,
                "rejected_operator_review_count": 0,
                "hold_operator_review_count": 0,
                "next_operator_action": "R8v_submit_target_gate_result_package",
                "can_route_to_post_review_gate": False,
                "can_emit_protective_control_candidate": False,
                "can_write_to_actuator": False,
                "can_write_to_release_gate": False,
                "field_claim_upgrade_allowed": False,
            },
            "field_rows_downstream_target_gate_post_review_gate": {
                "downstream_target_gate_post_review_gate_status": (
                    "downstream_target_gate_post_review_gate_blocked_by_operator_review_preflight"
                ),
                "candidate_target_count": 0,
                "next_operator_action": "R8v_submit_target_gate_result_package",
                "can_route_to_protective_candidate_evaluation": False,
                "can_emit_protective_control_candidate": False,
                "can_write_to_actuator": False,
                "can_write_to_release_gate": False,
                "field_claim_upgrade_allowed": False,
            },
            "field_rows_downstream_target_gate_protective_candidate_evaluation": {
                "downstream_target_gate_protective_candidate_evaluation_status": (
                    "protective_candidate_evaluation_blocked_by_post_review_gate"
                ),
                "candidate_target_count": 0,
                "next_operator_action": "R8v_submit_target_gate_result_package",
                "can_emit_protective_control_candidate": False,
                "can_route_to_final_execution_review": False,
                "can_write_to_actuator": False,
                "can_write_to_release_gate": False,
                "field_claim_upgrade_allowed": False,
            },
        }
    if include_r8m:
        r7_metrics = core_metrics.setdefault("r7_real_field_replay_pipeline_metrics", {})
        r7_metrics.setdefault("pipeline_readiness", {}).update(
            {
                "pressure_source_conflict_count": 1,
                "pressure_source_conflict_requires_operator_review": True,
                "resolved_pressure_source_conflict_count": 0,
                "unresolved_pressure_source_conflict_count": 1,
                "pressure_source_resolution_record_count": 0,
                "field_package_pressure_conflict_resolution_status": (
                    "pressure_source_conflicts_require_field_patch"
                ),
                "field_package_pressure_conflict_resolution_ready": False,
            }
        )
        coverage = r7_metrics.setdefault("field_package_coverage", {})
        coverage.setdefault("readiness", {}).update(
            {
                "pressure_source_conflict_count": 1,
                "pressure_source_conflict_requires_operator_review": True,
                "resolved_pressure_source_conflict_count": 0,
                "unresolved_pressure_source_conflict_count": 1,
                "pressure_source_resolution_record_count": 0,
                "field_package_pressure_conflict_resolution_status": (
                    "pressure_source_conflicts_require_field_patch"
                ),
                "field_package_pressure_conflict_resolution_ready": False,
            }
        )
        coverage["patch_plan"] = {
            "patch_plan_status": "patch_plan_requires_pressure_source_conflict_resolution",
            "items": [
                {
                    "item_id": "R8M_PRESSURE_SOURCE_CONFLICT_FIELD_PATCH",
                    "pressure_source_conflict_count": 1,
                }
            ],
        }
    return core_metrics
