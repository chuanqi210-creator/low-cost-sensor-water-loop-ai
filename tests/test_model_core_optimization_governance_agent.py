from water_ai.agents.model_core_optimization_governance_agent import (
    CORE_ABILITY_WEIGHTS,
    MODULE_TERMINATION_THRESHOLDS,
    ModelCoreOptimizationGovernanceAgent,
    REQUIRED_EVIDENCE_FIELDS,
)


def test_governance_agent_ranks_model_core_ahead_of_presentation_work() -> None:
    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=_agent48_metrics(),
        agent49_metrics=_agent49_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])

    ranking = report.metrics["priority_ranking"]
    top_ids = [item["task_id"] for item in ranking[:3]]
    low_ids = [item["task_id"] for item in report.metrics["low_priority_backlog"]]

    assert "P1_agent48_comparable_sparse_sensor_placement" in top_ids
    assert "P3_agent49_replay_ready_offline_evaluation" in [item["task_id"] for item in ranking[:4]]
    assert "L1_ppt_word_showcase_polish" in low_ids
    assert ranking[0]["marginal_value_score"] > ranking[-1]["marginal_value_score"]


def test_governance_agent_elevates_catalyst_activity_when_weak_state_coverage_is_low() -> None:
    metrics = _agent48_metrics()
    metrics["coverage"]["weak_state_coverage"] = 0.300
    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=metrics,
        agent49_metrics=_agent49_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])

    ranking = report.metrics["priority_ranking"]
    top_two = [item["task_id"] for item in ranking[:2]]

    assert "P2_catalyst_activity_weak_observability_proxy" in top_two
    assert any("catalyst_activity" in reason for reason in report.metrics["blocked_reasons"])
    assert any(issue.issue_type == "catalyst_activity_weak_observability" for issue in report.issues)


def test_governance_agent_interrupts_presentation_only_work() -> None:
    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=_agent48_metrics(),
        agent49_metrics=_agent49_metrics(),
        external_evidence_matrix=_evidence_matrix(),
        current_work_item={
            "task_id": "deck_polish",
            "title": "继续美化 PPT 和 Word 展示材料",
            "category": "presentation",
            "touches_model_metrics": False,
        },
    ).run([])

    assert report.metrics["self_interrupt_verdict"] == "interrupt_and_refocus"
    assert any(issue.issue_type == "presentation_bias_detected" for issue in report.issues)


def test_governance_agent_validates_evidence_matrix_required_fields() -> None:
    incomplete = [{field: "filled" for field in REQUIRED_EVIDENCE_FIELDS[:-1]}]

    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=_agent48_metrics(),
        agent49_metrics=_agent49_metrics(),
        external_evidence_matrix=incomplete,
    ).run([])

    status = report.metrics["evidence_matrix_status"]

    assert status["status"] == "evidence_matrix_needs_patch"
    assert status["incomplete_records"][0]["missing"] == ["failure_boundary"]
    assert any(issue.issue_type == "evidence_matrix_schema_incomplete" for issue in report.issues)


def test_governance_agent_continues_model_core_work_when_current_task_touches_metrics() -> None:
    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=_agent48_metrics(),
        agent49_metrics=_agent49_metrics(),
        external_evidence_matrix=_evidence_matrix(),
        current_work_item={
            "task_id": "agent48_upgrade",
            "title": "升级 Agent48 稀疏布点优化",
            "category": "sparse_sensing",
            "touches_model_metrics": True,
        },
    ).run([])

    assert report.metrics["self_interrupt_verdict"] == "continue_core_work"
    assert report.metrics["recommended_next_core_action"]["task_id"].startswith("P1_")


def test_governance_agent_queues_non_metric_refocus_without_interrupting_current_loop() -> None:
    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=_agent48_metrics(),
        agent49_metrics=_agent49_metrics(),
        external_evidence_matrix=_evidence_matrix(),
        current_work_item={
            "task_id": "new_possible_core_gap",
            "title": "发现一个可能更高边际价值的模型缺口",
            "category": "model_core",
            "touches_model_metrics": False,
            "stage_boundary": False,
            "current_step_complete": False,
        },
    ).run([])

    assert report.metrics["self_interrupt_verdict"] == "continue_core_work"
    assert report.metrics["self_interrupt_mode"] == "stage_gate_throttled_hard_gate_with_deferred_backlog"
    gate = report.metrics["governance_review_gate"]
    assert gate["decision"] == "continue_current_micro_loop"
    assert gate["deep_review_allowed"] is False
    assert gate["governance_rerun_recommended"] is False
    assert report.metrics["stage_boundary_deferred_count"] == 1
    assert report.metrics["stage_boundary_deferred_backlog"][0]["task_id"] == "new_possible_core_gap"
    assert not any(
        issue.issue_type == "self_interrupt_deferred_until_stage_boundary"
        for issue in report.issues
    )
    assert not any(issue.issue_type == "presentation_bias_detected" for issue in report.issues)


def test_governance_agent_allows_deep_review_only_at_stage_boundary() -> None:
    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=_agent48_metrics(),
        agent49_metrics=_agent49_metrics(),
        external_evidence_matrix=_evidence_matrix(),
        current_work_item={
            "task_id": "bounded_agent48_loop_done",
            "title": "Agent48 一轮可验证小闭环已经完成，需要统一复盘 backlog",
            "category": "model_core",
            "touches_model_metrics": False,
            "current_step_complete": True,
        },
    ).run([])

    gate = report.metrics["governance_review_gate"]

    assert report.metrics["self_interrupt_verdict"] == "continue_core_work"
    assert gate["decision"] == "run_stage_review"
    assert gate["deep_review_allowed"] is True
    assert gate["governance_rerun_recommended"] is True
    assert report.metrics["stage_boundary_deferred_count"] == 0


def test_governance_agent_can_throttle_stage_review_when_budget_is_exhausted() -> None:
    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=_agent48_metrics(),
        agent49_metrics=_agent49_metrics(),
        external_evidence_matrix=_evidence_matrix(),
        current_work_item={
            "task_id": "bounded_agent48_loop_done",
            "title": "Agent48 一轮可验证小闭环已经完成，但本轮治理预算用尽",
            "category": "model_core",
            "touches_model_metrics": False,
            "current_step_complete": True,
            "governance_review_budget_remaining": 0,
        },
    ).run([])

    gate = report.metrics["governance_review_gate"]

    assert report.metrics["self_interrupt_verdict"] == "continue_core_work"
    assert gate["decision"] == "defer_review_due_to_budget"
    assert gate["deep_review_allowed"] is False
    assert gate["governance_rerun_recommended"] is False


def test_governance_agent_hard_risk_bypasses_review_throttle() -> None:
    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=_agent48_metrics(),
        agent49_metrics=_agent49_metrics(),
        external_evidence_matrix=_evidence_matrix(),
        current_work_item={
            "task_id": "unsafe_claim_upgrade",
            "title": "把 template 数据写成现场支持结论",
            "category": "model_core",
            "touches_model_metrics": True,
            "writes_synthetic_as_field_claim": True,
            "governance_review_budget_remaining": 0,
        },
    ).run([])

    gate = report.metrics["governance_review_gate"]

    assert report.metrics["self_interrupt_verdict"] == "interrupt_and_refocus"
    assert gate["decision"] == "interrupt_and_refocus_now"
    assert gate["deep_review_allowed"] is True
    assert gate["hard_risk_detected"] is True


def test_governance_agent_outputs_quantified_core_score_and_module_gate() -> None:
    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=_agent48_ready_metrics(),
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        grey_box_physics_metrics=_grey_box_physics_metrics(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
        engineering_constraints_metrics=_engineering_constraints_metrics(),
        knowledge_graph_reasoning_metrics=_kg_reasoning_metrics(),
        main_chain_reconnection_metrics=_main_chain_reconnection_metrics(),
        field_validation_queue_alignment_metrics=_field_validation_alignment_metrics(),
        claim_specific_field_package_metrics=_claim_specific_field_package_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])

    gate = report.metrics["quantified_core_score_gate"]

    assert gate["gate_id"] == "R8u68_quantified_core_score_and_hidden_state_termination_gate"
    assert gate["ability_weights"] == CORE_ABILITY_WEIGHTS
    assert set(gate["ability_scores"]) == set(CORE_ABILITY_WEIGHTS)
    assert 0.0 <= gate["core_score"] <= 1.0
    assert gate["iteration_validity_status"] == "baseline_recorded_needs_next_delta"
    assert gate["stage_decision"] == "continue_core_work_with_quantified_baseline"
    assert gate["effective_iteration_gate"]["validity_basis"] == "baseline_recorded_needs_next_delta"
    assert gate["effective_iteration_gate"]["score_delta_pass"] is False
    assert gate["effective_iteration_gate"]["effective_iteration_pass"] is False
    assert gate["module_stage_termination_gate"]["thresholds"]["evidence_boundary_completeness"] == 1.0
    assert gate["no_write_boundaries"]["can_write_to_actuator"] is False
    assert gate["no_write_boundaries"]["can_write_to_release_gate"] is False


def test_governance_agent_separates_hidden_state_contract_from_field_control_readiness() -> None:
    report = ModelCoreOptimizationGovernanceAgent(
        manifest={
            "latest_agent50_core_score": 1.0,
            "latest_agent50_module_stage_status": "module_stage_needs_more_core_work",
        },
        agent48_metrics=_agent48_ready_metrics_with_hidden_state_ledger(),
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        grey_box_physics_metrics=_grey_box_physics_metrics(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
        engineering_constraints_metrics=_engineering_constraints_metrics(),
        knowledge_graph_reasoning_metrics=_kg_reasoning_metrics(),
        main_chain_reconnection_metrics=_main_chain_reconnection_metrics(),
        field_validation_queue_alignment_metrics=_field_validation_alignment_metrics(),
        claim_specific_field_package_metrics=_claim_specific_field_package_metrics(),
        external_evidence_matrix=_evidence_matrix(),
        current_work_item={
            "task_id": "r8u68_hidden_state_coverage_ledger",
            "title": "把隐藏状态覆盖拆成架构契约、补丁设计、现场验证和控制可用性",
            "category": "verification_governance",
            "touches_model_metrics": True,
            "changed_contract_or_gate": True,
            "targeted_tests_passed": True,
        },
    ).run([])

    gate = report.metrics["quantified_core_score_gate"]
    ledger = gate["hidden_state_coverage_ledger"]
    module_gate = gate["module_stage_termination_gate"]
    catalyst_row = next(row for row in ledger["state_rows"] if row["hidden_state"] == "catalyst_activity")

    assert ledger["state_variable_contract_coverage"] == 1.0
    assert ledger["sparse_estimation_ready_coverage"] == 0.667
    assert ledger["design_or_patch_ready_coverage"] == 1.0
    assert ledger["field_validated_state_coverage"] == 0.0
    assert ledger["control_ready_state_coverage"] == 0.0
    assert catalyst_row["coverage_stage"] == "synthetic_proxy_design_ready_needs_field_labels"
    assert "cannot support field claim" in catalyst_row["evidence_boundary"]
    assert module_gate["module_stage_status"] == "module_stage_complete"
    assert module_gate["metrics"]["state_variable_coverage"] == 1.0
    assert module_gate["supporting_state_metrics"]["field_validated_state_coverage"] == 0.0
    assert gate["previous_module_stage_status"] == "module_stage_needs_more_core_work"
    assert gate["module_stage_blocker_resolved"] is True
    assert gate["hard_blocker_resolved"] is True
    assert gate["iteration_validity_status"] == "valid_iteration"
    assert gate["effective_iteration_gate"]["hard_blocker_resolution_pass"] is True
    assert gate["effective_iteration_gate"]["validity_basis"] == "hard_blocker_resolved"
    assert gate["effective_iteration_gate"]["effective_iteration_pass"] is True
    assert gate["no_write_boundaries"]["can_write_to_actuator"] is False
    assert gate["no_write_boundaries"]["can_write_to_release_gate"] is False


def test_governance_agent_outputs_module_stage_termination_proof_rows() -> None:
    report = ModelCoreOptimizationGovernanceAgent(
        manifest={
            "latest_agent50_core_score": 1.0,
            "latest_agent50_module_stage_status": "module_stage_needs_more_core_work",
        },
        agent48_metrics=_agent48_ready_metrics_with_hidden_state_ledger(),
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        grey_box_physics_metrics=_grey_box_physics_metrics(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
        engineering_constraints_metrics=_engineering_constraints_metrics(),
        knowledge_graph_reasoning_metrics=_kg_reasoning_metrics(),
        main_chain_reconnection_metrics=_main_chain_reconnection_metrics(),
        field_validation_queue_alignment_metrics=_field_validation_alignment_metrics(),
        claim_specific_field_package_metrics=_claim_specific_field_package_metrics(),
        external_evidence_matrix=_evidence_matrix(),
        current_work_item={
            "task_id": "r8u180_module_stage_termination_proof",
            "title": "Expose per-criterion module termination proof rows",
            "category": "verification_governance",
            "touches_model_metrics": True,
            "changed_contract_or_gate": True,
            "targeted_tests_passed": True,
        },
    ).run([])

    module_gate = report.metrics["quantified_core_score_gate"]["module_stage_termination_gate"]
    proof = module_gate["termination_proof_rows"]

    assert module_gate["termination_proof_status"] == "module_stage_termination_proof_complete"
    assert module_gate["termination_pass_rate"] == 1.0
    assert [row["metric"] for row in proof] == list(MODULE_TERMINATION_THRESHOLDS)
    assert all(row["passed"] is True for row in proof)
    assert all(row["system_layer"] for row in proof)
    assert all(row["core_capability"] for row in proof)
    assert all(row["evidence_source"] for row in proof)
    assert all(row["failure_boundary"] for row in proof)
    no_write_row = next(row for row in proof if row["metric"] == "no_write_boundary_clarity")
    assert no_write_row["can_write_to_actuator"] is False
    assert no_write_row["can_write_to_release_gate"] is False


def test_governance_agent_stops_expansion_when_delta_is_low_without_hard_blocker() -> None:
    baseline = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=_agent48_ready_metrics(),
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        grey_box_physics_metrics=_grey_box_physics_metrics(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
        engineering_constraints_metrics=_engineering_constraints_metrics(),
        knowledge_graph_reasoning_metrics=_kg_reasoning_metrics(),
        main_chain_reconnection_metrics=_main_chain_reconnection_metrics(),
        field_validation_queue_alignment_metrics=_field_validation_alignment_metrics(),
        claim_specific_field_package_metrics=_claim_specific_field_package_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])
    previous = baseline.metrics["quantified_core_score_gate"]["core_score"]

    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=_agent48_ready_metrics(),
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        grey_box_physics_metrics=_grey_box_physics_metrics(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
        engineering_constraints_metrics=_engineering_constraints_metrics(),
        knowledge_graph_reasoning_metrics=_kg_reasoning_metrics(),
        main_chain_reconnection_metrics=_main_chain_reconnection_metrics(),
        field_validation_queue_alignment_metrics=_field_validation_alignment_metrics(),
        claim_specific_field_package_metrics=_claim_specific_field_package_metrics(),
        external_evidence_matrix=_evidence_matrix(),
        current_work_item={
            "task_id": "low_gain_extra_detail",
            "title": "继续补同一模块的低增益细节",
            "category": "model_core",
            "touches_model_metrics": True,
            "previous_core_score": previous,
            "changed_contract_or_gate": True,
            "targeted_tests_passed": True,
        },
    ).run([])

    gate = report.metrics["quantified_core_score_gate"]

    assert gate["iteration_delta"] == 0.0
    assert gate["iteration_validity_status"] == "low_marginal_gain_without_hard_blocker"
    assert gate["stage_decision"] == "stop_expansion_enter_review_or_backlog"
    assert gate["continue_expansion_allowed"] is False
    assert gate["effective_iteration_gate"]["low_gain_without_hard_blocker"] is True
    assert gate["effective_iteration_gate"]["validity_basis"] == "low_gain_without_hard_blocker"
    assert gate["effective_iteration_gate"]["effective_iteration_pass"] is False
    assert gate["effective_iteration_gate"]["expansion_stop_required"] is True


def test_governance_agent_accepts_low_delta_when_hard_blocker_is_resolved() -> None:
    baseline = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=_agent48_ready_metrics(),
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        grey_box_physics_metrics=_grey_box_physics_metrics(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
        engineering_constraints_metrics=_engineering_constraints_metrics(),
        knowledge_graph_reasoning_metrics=_kg_reasoning_metrics(),
        main_chain_reconnection_metrics=_main_chain_reconnection_metrics(),
        field_validation_queue_alignment_metrics=_field_validation_alignment_metrics(),
        claim_specific_field_package_metrics=_claim_specific_field_package_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])
    previous = baseline.metrics["quantified_core_score_gate"]["core_score"]

    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=_agent48_ready_metrics(),
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        grey_box_physics_metrics=_grey_box_physics_metrics(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
        engineering_constraints_metrics=_engineering_constraints_metrics(),
        knowledge_graph_reasoning_metrics=_kg_reasoning_metrics(),
        main_chain_reconnection_metrics=_main_chain_reconnection_metrics(),
        field_validation_queue_alignment_metrics=_field_validation_alignment_metrics(),
        claim_specific_field_package_metrics=_claim_specific_field_package_metrics(),
        external_evidence_matrix=_evidence_matrix(),
        current_work_item={
            "task_id": "r8u67_quantified_termination_gate",
            "title": "补可量化终止条件 gate",
            "category": "verification_governance",
            "touches_model_metrics": True,
            "previous_core_score": previous,
            "resolved_hard_blocker": True,
            "changed_contract_or_gate": True,
            "targeted_tests_passed": True,
        },
    ).run([])

    gate = report.metrics["quantified_core_score_gate"]

    assert gate["iteration_delta"] == 0.0
    assert gate["hard_blocker_resolved"] is True
    assert gate["iteration_validity_status"] == "valid_iteration"
    assert gate["stage_decision"] == "continue_to_next_highest_value_core_action"
    assert gate["continue_expansion_allowed"] is True
    assert gate["effective_iteration_gate"]["score_delta_pass"] is False
    assert gate["effective_iteration_gate"]["hard_blocker_resolution_pass"] is True
    assert gate["effective_iteration_gate"]["validity_basis"] == "hard_blocker_resolved"
    assert gate["effective_iteration_gate"]["effective_iteration_pass"] is True


def test_governance_agent_moves_to_catalyst_proxy_after_agent48_comparison_baseline_exists() -> None:
    metrics = _agent48_metrics()
    metrics["algorithm_comparison"] = [
        {"strategy_id": "greedy_marginal"},
        {"strategy_id": "reconstruction_qr_proxy"},
        {"strategy_id": "classification_sspoc_proxy"},
        {"strategy_id": "topology_robust_cost_proxy"},
    ]
    metrics["selected_strategy"] = {"strategy_id": "greedy_marginal"}

    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=metrics,
        agent49_metrics=_agent49_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])

    assert report.metrics["recommended_next_core_action"]["task_id"] == "P2_catalyst_activity_weak_observability_proxy"
    assert report.metrics["priority_ranking"][0]["task_id"] == "P2_catalyst_activity_weak_observability_proxy"
    assert any(item.get("implementation_status") == "synthetic_comparison_baseline_ready" for item in report.metrics["priority_ranking"])


def test_governance_agent_moves_to_agent49_after_catalyst_proxy_baseline_exists() -> None:
    metrics = _agent48_metrics()
    metrics["algorithm_comparison"] = [
        {"strategy_id": "greedy_marginal"},
        {"strategy_id": "reconstruction_qr_proxy"},
        {"strategy_id": "classification_sspoc_proxy"},
        {"strategy_id": "topology_robust_cost_proxy"},
    ]
    metrics["selected_strategy"] = {"strategy_id": "greedy_marginal"}

    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=metrics,
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])

    ranking = report.metrics["priority_ranking"]

    assert report.metrics["recommended_next_core_action"]["task_id"] == "P3_agent49_replay_ready_offline_evaluation"
    assert ranking[0]["task_id"] == "P3_agent49_replay_ready_offline_evaluation"
    assert any(
        item.get("implementation_status") == "synthetic_proxy_design_ready_needs_field_labels"
        for item in ranking
    )
    assert any("field_proxy_holdout" in reason for reason in report.metrics["blocked_reasons"])


def test_governance_agent_moves_to_grey_box_after_agent49_replay_baseline_exists() -> None:
    metrics = _agent48_metrics()
    metrics["algorithm_comparison"] = [
        {"strategy_id": "greedy_marginal"},
        {"strategy_id": "reconstruction_qr_proxy"},
        {"strategy_id": "classification_sspoc_proxy"},
        {"strategy_id": "topology_robust_cost_proxy"},
    ]
    metrics["selected_strategy"] = {"strategy_id": "greedy_marginal"}

    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=metrics,
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])

    ranking = report.metrics["priority_ranking"]

    assert report.metrics["recommended_next_core_action"]["task_id"] == "P4_minimal_grey_box_physics"
    assert ranking[0]["task_id"] == "P4_minimal_grey_box_physics"
    assert any(
        item.get("implementation_status") == "synthetic_replay_evaluation_ready_needs_field_replay"
        for item in ranking
    )
    assert any("field multi-node" in reason for reason in report.metrics["blocked_reasons"])


def test_governance_agent_moves_to_soft_sensor_matrix_after_grey_box_baseline_exists() -> None:
    metrics = _agent48_metrics()
    metrics["algorithm_comparison"] = [
        {"strategy_id": "greedy_marginal"},
        {"strategy_id": "reconstruction_qr_proxy"},
        {"strategy_id": "classification_sspoc_proxy"},
        {"strategy_id": "topology_robust_cost_proxy"},
    ]
    metrics["selected_strategy"] = {"strategy_id": "greedy_marginal"}

    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=metrics,
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        grey_box_physics_metrics=_grey_box_physics_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])

    ranking = report.metrics["priority_ranking"]

    assert report.metrics["recommended_next_core_action"]["task_id"] == "P5_soft_sensor_node_modality_missingness"
    assert ranking[0]["task_id"] == "P5_soft_sensor_node_modality_missingness"
    assert any(
        item.get("implementation_status") == "synthetic_grey_box_physics_prior_ready_needs_field_calibration"
        for item in ranking
    )
    assert any("field RTD" in reason for reason in report.metrics["blocked_reasons"])


def test_governance_agent_moves_to_engineering_constraints_after_soft_sensor_matrix_baseline_exists() -> None:
    metrics = _agent48_metrics()
    metrics["algorithm_comparison"] = [
        {"strategy_id": "greedy_marginal"},
        {"strategy_id": "reconstruction_qr_proxy"},
        {"strategy_id": "classification_sspoc_proxy"},
        {"strategy_id": "topology_robust_cost_proxy"},
    ]
    metrics["selected_strategy"] = {"strategy_id": "greedy_marginal"}

    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=metrics,
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        grey_box_physics_metrics=_grey_box_physics_metrics(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])

    ranking = report.metrics["priority_ranking"]

    assert report.metrics["recommended_next_core_action"]["task_id"] == "P7_engineering_constraints_in_reward_and_arbitration"
    assert ranking[0]["task_id"] == "P7_engineering_constraints_in_reward_and_arbitration"
    assert any(
        item.get("implementation_status") == "synthetic_layout_aware_soft_sensor_contract_ready_needs_field_missingness"
        for item in ranking
    )
    assert any("field node-specific values" in reason for reason in report.metrics["blocked_reasons"])
    assert any(issue.issue_type == "field_missingness_replay_required" for issue in report.issues)


def test_governance_agent_moves_to_kg_after_engineering_constraints_baseline_exists() -> None:
    metrics = _agent48_metrics()
    metrics["algorithm_comparison"] = [
        {"strategy_id": "greedy_marginal"},
        {"strategy_id": "reconstruction_qr_proxy"},
        {"strategy_id": "classification_sspoc_proxy"},
        {"strategy_id": "topology_robust_cost_proxy"},
    ]
    metrics["selected_strategy"] = {"strategy_id": "greedy_marginal"}

    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=metrics,
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        grey_box_physics_metrics=_grey_box_physics_metrics(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
        engineering_constraints_metrics=_engineering_constraints_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])

    ranking = report.metrics["priority_ranking"]

    assert report.metrics["recommended_next_core_action"]["task_id"] == "P6_reasonable_knowledge_graph_upgrade"
    assert ranking[0]["task_id"] == "P6_reasonable_knowledge_graph_upgrade"
    assert any(
        item.get("implementation_status") == "synthetic_engineering_constraints_reward_patch_ready_needs_plc_scada_and_field_replay"
        for item in ranking
    )
    assert any("PLC/SCADA" in reason for reason in report.metrics["blocked_reasons"])
    assert any(issue.issue_type == "field_execution_replay_required" for issue in report.issues)


def test_governance_agent_moves_to_cross_agent_reconnection_after_kg_baseline_exists() -> None:
    metrics = _agent48_metrics()
    metrics["algorithm_comparison"] = [
        {"strategy_id": "greedy_marginal"},
        {"strategy_id": "reconstruction_qr_proxy"},
        {"strategy_id": "classification_sspoc_proxy"},
        {"strategy_id": "topology_robust_cost_proxy"},
    ]
    metrics["selected_strategy"] = {"strategy_id": "greedy_marginal"}

    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=metrics,
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        grey_box_physics_metrics=_grey_box_physics_metrics(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
        engineering_constraints_metrics=_engineering_constraints_metrics(),
        knowledge_graph_reasoning_metrics=_kg_reasoning_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])

    assert report.metrics["recommended_next_core_action"]["task_id"] == "P8_cross_agent_core_reconnection"
    assert report.metrics["priority_ranking"][0]["task_id"] == "P8_cross_agent_core_reconnection"
    assert any(item.get("implementation_status") == "kg_reasoning_patch_ready_needs_field_supported_edges" for item in report.metrics["priority_ranking"])


def test_governance_agent_moves_to_field_validation_alignment_after_main_chain_reconnects() -> None:
    metrics = _agent48_metrics()
    metrics["algorithm_comparison"] = [
        {"strategy_id": "greedy_marginal"},
        {"strategy_id": "reconstruction_qr_proxy"},
        {"strategy_id": "classification_sspoc_proxy"},
        {"strategy_id": "topology_robust_cost_proxy"},
    ]
    metrics["selected_strategy"] = {"strategy_id": "greedy_marginal"}

    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=metrics,
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        grey_box_physics_metrics=_grey_box_physics_metrics(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
        engineering_constraints_metrics=_engineering_constraints_metrics(),
        knowledge_graph_reasoning_metrics=_kg_reasoning_metrics(),
        main_chain_reconnection_metrics=_main_chain_reconnection_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])

    assert report.metrics["recommended_next_core_action"]["task_id"] == "P9_field_validation_queue_alignment"
    assert report.metrics["priority_ranking"][0]["task_id"] == "P9_field_validation_queue_alignment"
    assert any(
        item.get("implementation_status") == "synthetic_main_chain_reconnection_ready_needs_field_replay"
        for item in report.metrics["priority_ranking"]
    )


def test_governance_agent_moves_to_claim_specific_field_package_after_alignment_exists() -> None:
    metrics = _agent48_metrics()
    metrics["algorithm_comparison"] = [
        {"strategy_id": "greedy_marginal"},
        {"strategy_id": "reconstruction_qr_proxy"},
        {"strategy_id": "classification_sspoc_proxy"},
        {"strategy_id": "topology_robust_cost_proxy"},
    ]
    metrics["selected_strategy"] = {"strategy_id": "greedy_marginal"}

    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=metrics,
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        grey_box_physics_metrics=_grey_box_physics_metrics(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
        engineering_constraints_metrics=_engineering_constraints_metrics(),
        knowledge_graph_reasoning_metrics=_kg_reasoning_metrics(),
        main_chain_reconnection_metrics=_main_chain_reconnection_metrics(),
        field_validation_queue_alignment_metrics=_field_validation_alignment_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])

    assert report.metrics["recommended_next_core_action"]["task_id"] == "P10_claim_specific_field_package_and_source_basis"
    assert report.metrics["priority_ranking"][0]["task_id"] == "P10_claim_specific_field_package_and_source_basis"
    assert any(
        item.get("implementation_status") == "field_validation_alignment_ready_needs_real_field_package"
        for item in report.metrics["priority_ranking"]
    )
    assert any(issue.issue_type == "claim_specific_field_package_required" for issue in report.issues)


def test_governance_agent_moves_to_source_basis_or_field_import_after_claim_package_exists() -> None:
    metrics = _agent48_metrics()
    metrics["algorithm_comparison"] = [
        {"strategy_id": "greedy_marginal"},
        {"strategy_id": "reconstruction_qr_proxy"},
        {"strategy_id": "classification_sspoc_proxy"},
        {"strategy_id": "topology_robust_cost_proxy"},
    ]
    metrics["selected_strategy"] = {"strategy_id": "greedy_marginal"}

    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=metrics,
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        grey_box_physics_metrics=_grey_box_physics_metrics(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
        engineering_constraints_metrics=_engineering_constraints_metrics(),
        knowledge_graph_reasoning_metrics=_kg_reasoning_metrics(),
        main_chain_reconnection_metrics=_main_chain_reconnection_metrics(),
        field_validation_queue_alignment_metrics=_field_validation_alignment_metrics(),
        claim_specific_field_package_metrics=_claim_specific_field_package_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])

    assert report.metrics["recommended_next_core_action"]["task_id"] == "P11_source_basis_detail_or_real_field_package_import"
    assert report.metrics["priority_ranking"][0]["task_id"] == "P11_source_basis_detail_or_real_field_package_import"
    assert any(
        item.get("implementation_status") == "claim_specific_package_ready_needs_real_data_and_source_basis_detail"
        for item in report.metrics["priority_ranking"]
    )
    assert any(issue.issue_type == "source_basis_detail_or_field_package_import_required" for issue in report.issues)


def test_governance_agent_does_not_keep_recommending_citation_patch_after_source_basis_is_complete() -> None:
    metrics = _agent48_metrics()
    metrics["algorithm_comparison"] = [
        {"strategy_id": "greedy_marginal"},
        {"strategy_id": "reconstruction_qr_proxy"},
        {"strategy_id": "classification_sspoc_proxy"},
        {"strategy_id": "topology_robust_cost_proxy"},
    ]
    metrics["selected_strategy"] = {"strategy_id": "greedy_marginal"}
    claim_metrics = _claim_specific_field_package_metrics()
    claim_metrics["readiness"]["source_basis_completion_rate"] = 1.0

    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=metrics,
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        grey_box_physics_metrics=_grey_box_physics_metrics(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
        engineering_constraints_metrics=_engineering_constraints_metrics(),
        knowledge_graph_reasoning_metrics=_kg_reasoning_metrics(),
        main_chain_reconnection_metrics=_main_chain_reconnection_metrics(),
        field_validation_queue_alignment_metrics=_field_validation_alignment_metrics(),
        claim_specific_field_package_metrics=claim_metrics,
        unified_field_evidence_gate_metrics=_unified_field_evidence_gate_metrics(),
        real_field_package_acceptance_metrics=_real_field_package_acceptance_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])

    p11 = next(
        item
        for item in report.metrics["priority_ranking"]
        if item["task_id"] == "P11_source_basis_detail_or_real_field_package_import"
    )

    assert p11["implementation_status"] == "waiting_on_real_field_package_external_blocker"
    assert p11["external_blocker"] is True
    assert "停止内部补 source_basis/citation" in p11["next_experiment"]
    assert "真实包" in p11["next_experiment"]
    assert "不能写 actuator" in p11["failure_boundary"]
    assert report.metrics["recommended_next_core_action"]["task_id"] != "P11_source_basis_detail_or_real_field_package_import"
    assert report.metrics["external_blocker_backlog"][0]["task_id"] == "P11_source_basis_detail_or_real_field_package_import"
    assert any(
        "external real-field-package blocker" in reason
        for reason in report.metrics["blocked_reasons"]
    )
    assert not any(
        "仍需具体 citation" in issue.message
        for issue in report.issues
        if issue.issue_type == "source_basis_detail_or_field_package_import_required"
    )


def test_governance_agent_consumes_r2_r3_outputs_and_demotes_repeated_baselines() -> None:
    metrics = _agent48_ready_metrics()
    claim_metrics = _claim_specific_field_package_metrics()
    claim_metrics["readiness"]["source_basis_completion_rate"] = 1.0

    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=metrics,
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        grey_box_physics_metrics=_grey_box_physics_metrics(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
        engineering_constraints_metrics=_engineering_constraints_metrics(),
        knowledge_graph_reasoning_metrics=_kg_reasoning_metrics(),
        main_chain_reconnection_metrics=_main_chain_reconnection_metrics(),
        field_validation_queue_alignment_metrics=_field_validation_alignment_metrics(),
        claim_specific_field_package_metrics=claim_metrics,
        unified_field_evidence_gate_metrics=_unified_field_evidence_gate_metrics(),
        real_field_package_acceptance_metrics=_real_field_package_acceptance_metrics(),
        r7_pipeline_metrics=_r7_pipeline_metrics(),
        observation_contract_metrics=_observation_contract_metrics(),
        observation_response_bridge_metrics=_observation_response_bridge_metrics(),
        control_replay_stress_metrics=_control_replay_stress_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])

    ranking_by_id = {item["task_id"]: item for item in report.metrics["priority_ranking"]}

    assert ranking_by_id["P1_agent48_comparable_sparse_sensor_placement"]["implementation_status"].startswith(
        "consumed_by_R2_observation_contract"
    )
    assert ranking_by_id["P2_catalyst_activity_weak_observability_proxy"]["implementation_status"].startswith(
        "consumed_by_R2_observation_contract"
    )
    assert ranking_by_id["P5_soft_sensor_node_modality_missingness"]["implementation_status"].startswith(
        "consumed_by_R2_observation_contract"
    )
    assert ranking_by_id["P3_agent49_replay_ready_offline_evaluation"]["implementation_status"].startswith(
        "consumed_by_R3_counterfactual_stress"
    )
    assert ranking_by_id["P11_source_basis_detail_or_real_field_package_import"]["external_blocker"] is True
    assert report.metrics["governance_scorecard"]["external_field_blocker_active"] is True
    assert report.metrics["governance_scorecard"]["claim_basis_promotion_gate_status"] == (
        "claim_basis_promotion_blocked_until_field_validation"
    )
    assert report.metrics["governance_scorecard"]["claim_basis_promotion_ready_count"] == 0
    assert report.metrics["governance_scorecard"]["claim_basis_promotion_blocked_count"] == 5
    assert report.metrics["governance_scorecard"]["claim_basis_promotion_can_emit_field_claim_upgrade"] is False
    assert report.metrics["governance_scorecard"]["claim_basis_promotion_can_write_to_actuator"] is False
    assert report.metrics["governance_scorecard"]["claim_basis_promotion_can_write_to_release_gate"] is False
    assert report.metrics["governance_scorecard"]["field_evidence_wait_status"]["field_import_ready"] is False
    assert report.metrics["governance_scorecard"]["r7_field_evidence_sufficiency_status"] == (
        "field_evidence_sufficiency_blocked_before_import"
    )
    assert report.metrics["governance_scorecard"]["r7_submission_readiness_status"] == (
        "field_package_submission_blocked_at_import_preflight"
    )
    assert report.metrics["governance_scorecard"]["r7_submission_repair_work_order_status"] == (
        "field_package_submission_repair_work_order_blocked_at_import_preflight"
    )
    assert report.metrics["governance_scorecard"]["r7_submission_repair_item_count"] == 13
    assert report.metrics["governance_scorecard"]["r7_submission_repair_response_preflight_status"] == (
        "repair_response_preflight_blocked_at_template_markers"
    )
    assert report.metrics["governance_scorecard"][
        "r7_submission_repair_response_can_route_to_r7_preflight"
    ] is False
    assert report.metrics["governance_scorecard"]["field_evidence_wait_status"][
        "r7_submission_highest_priority_blocker"
    ] == "R7A_IMPORT_PREFLIGHT"
    assert report.metrics["governance_scorecard"]["field_evidence_wait_status"][
        "r7_submission_repair_work_order_status"
    ] == "field_package_submission_repair_work_order_blocked_at_import_preflight"
    assert report.metrics["governance_scorecard"]["field_evidence_wait_status"][
        "r7_submission_repair_item_count"
    ] == 13
    assert report.metrics["governance_scorecard"]["field_evidence_wait_status"][
        "r7_submission_repair_response_preflight_status"
    ] == "repair_response_preflight_blocked_at_template_markers"
    assert report.metrics["governance_scorecard"]["field_evidence_wait_status"][
        "r7_submission_repair_response_can_route_to_r7_preflight"
    ] is False
    assert report.metrics["governance_scorecard"]["field_evidence_wait_status"][
        "r7_field_evidence_sufficiency_status"
    ] == "field_evidence_sufficiency_blocked_before_import"
    assert report.metrics["governance_scorecard"]["field_evidence_wait_status"][
        "r7_can_route_to_human_review_candidate"
    ] is False
    field_channel = report.metrics["external_activation_contract"]["channels"][0]
    assert field_channel["channel_id"] == "R7_REAL_FIELD_PACKAGE"
    assert field_channel["repair_work_order_status"] == (
        "field_package_submission_repair_work_order_blocked_at_import_preflight"
    )
    assert field_channel["repair_item_count"] == 13
    assert field_channel["repair_response_preflight_status"] == (
        "repair_response_preflight_blocked_at_template_markers"
    )
    assert field_channel["repair_response_can_route_to_r7_preflight"] is False
    assert report.metrics["recommended_next_core_action"]["task_id"] == "WAIT_real_field_package_or_new_core_interface"
    assert report.metrics["self_interrupt_verdict"] == "stage_boundary_wait_for_external_activation"
    assert "外部激活等待" in report.metrics["self_interrupt_reason"]
    assert any(
        issue.issue_type == "stage_boundary_wait_for_external_activation"
        for issue in report.issues
    )
    assert any("外部证据包" in recommendation for recommendation in report.recommendations)
    core_gate = report.metrics["quantified_core_score_gate"]
    assert core_gate["stage_decision"] == (
        "stop_expansion_wait_for_real_field_package_or_new_core_interface"
    )
    assert core_gate["effective_iteration_gate"]["score_delta_pass"] is False
    assert core_gate["effective_iteration_gate"]["stage_boundary_termination_pass"] is True
    assert core_gate["effective_iteration_gate"]["validity_basis"] == (
        "stage_boundary_external_wait_not_score_gain"
    )
    assert core_gate["effective_iteration_gate"]["effective_iteration_pass"] is True
    assert core_gate["effective_iteration_gate"]["expansion_stop_required"] is True
    assert "not a score-gain claim" in core_gate["effective_iteration_gate"]["interpretation"]
    assert core_gate["self_interrupt_verdict"] == "stage_boundary_wait_for_external_activation"
    assert "外部激活等待" in core_gate["self_interrupt_reason"]
    assert core_gate["self_interrupt_mode"] == "stage_gate_throttled_hard_gate_with_deferred_backlog"
    allowed_actions = core_gate["next_allowed_actions"]
    action_channels = {action["channel_id"] for action in allowed_actions}
    assert "R7_REAL_FIELD_PACKAGE" in action_channels
    assert "R8U66_PATH_ENDPOINT_LABEL_PACKAGE" in action_channels
    assert "R8U79_FORMAL_SEARCH_RESULT_PACKAGE" in action_channels
    assert "NEW_CORE_INTERFACE" in action_channels
    assert all("actuator policy" in action["boundary"] or action["channel_id"] == "NEW_CORE_INTERFACE" for action in allowed_actions)
    actions_by_channel = {action["channel_id"]: action for action in allowed_actions}
    assert actions_by_channel["R7_REAL_FIELD_PACKAGE"]["activation_route_class"] == (
        "model_chain_external_package"
    )
    assert actions_by_channel["R7_REAL_FIELD_PACKAGE"]["model_chain_resume_candidate"] is True
    assert actions_by_channel["R7_REAL_FIELD_PACKAGE"]["handoff_only"] is False
    assert actions_by_channel["R7_REAL_FIELD_PACKAGE"]["requires_tested_interface"] is False
    assert actions_by_channel["R7_REAL_FIELD_PACKAGE"]["current_route_ready"] is False
    assert actions_by_channel["R7_REAL_FIELD_PACKAGE"]["current_model_chain_resume_ready"] is False
    assert actions_by_channel["R7_REAL_FIELD_PACKAGE"]["current_handoff_ready"] is False
    assert actions_by_channel["R7_REAL_FIELD_PACKAGE"]["action_resume_state"] == (
        "model_chain_blocked_waiting_for_package"
    )
    assert "Agent44/42/43/45" in actions_by_channel["R7_REAL_FIELD_PACKAGE"]["boundary"]
    assert actions_by_channel["R8U66_PATH_ENDPOINT_LABEL_PACKAGE"]["activation_route_class"] == (
        "model_chain_external_package"
    )
    assert actions_by_channel["R8U66_PATH_ENDPOINT_LABEL_PACKAGE"]["model_chain_resume_candidate"] is True
    assert actions_by_channel["R8U66_PATH_ENDPOINT_LABEL_PACKAGE"]["current_route_ready"] is False
    assert actions_by_channel["R8U66_PATH_ENDPOINT_LABEL_PACKAGE"]["current_model_chain_resume_ready"] is False
    assert actions_by_channel["R8U66_PATH_ENDPOINT_LABEL_PACKAGE"]["action_resume_state"] == (
        "model_chain_blocked_waiting_for_package"
    )
    assert actions_by_channel["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"]["activation_route_class"] == (
        "formal_search_handoff_only"
    )
    assert actions_by_channel["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"]["model_chain_resume_candidate"] is False
    assert actions_by_channel["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"]["handoff_only"] is True
    assert actions_by_channel["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"]["can_resume_model_chain"] is False
    assert actions_by_channel["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"]["current_route_ready"] is False
    assert actions_by_channel["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"]["current_model_chain_resume_ready"] is False
    assert actions_by_channel["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"]["current_handoff_ready"] is False
    assert actions_by_channel["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"]["action_resume_state"] == (
        "handoff_blocked_waiting_for_package"
    )
    assert "formal-search handoff only" in actions_by_channel["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"]["boundary"]
    assert "cannot resume field replay or control" in actions_by_channel["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"]["boundary"]
    assert actions_by_channel["NEW_CORE_INTERFACE"]["activation_route_class"] == "new_testable_core_interface"
    assert actions_by_channel["NEW_CORE_INTERFACE"]["requires_tested_interface"] is True
    assert actions_by_channel["NEW_CORE_INTERFACE"]["can_resume_model_chain"] is False
    assert actions_by_channel["NEW_CORE_INTERFACE"]["current_route_ready"] is False
    assert actions_by_channel["NEW_CORE_INTERFACE"]["current_model_chain_resume_ready"] is False
    assert actions_by_channel["NEW_CORE_INTERFACE"]["current_handoff_ready"] is False
    assert actions_by_channel["NEW_CORE_INTERFACE"]["action_resume_state"] == (
        "new_interface_required_before_any_resume"
    )
    assert actions_by_channel["NEW_CORE_INTERFACE"]["router_status"] == (
        "not_applicable_for_new_core_interface"
    )
    assert actions_by_channel["NEW_CORE_INTERFACE"]["router_preflight_status"] == (
        "new_interface_needs_tests_or_verification_gate"
    )
    assert actions_by_channel["NEW_CORE_INTERFACE"]["router_validation_command"] == (
        "not_applicable_for_new_core_interface"
    )
    resume_conditions = core_gate["external_resume_conditions"]
    assert resume_conditions["resume_policy"].startswith("Resume internal model-chain execution only after")
    resume_channels = {channel["channel_id"]: channel for channel in resume_conditions["channels"]}
    assert resume_channels["R7_REAL_FIELD_PACKAGE"]["can_resume_model_chain"] is False
    assert "metadata.json with data_origin=field" in resume_channels["R7_REAL_FIELD_PACKAGE"]["required_evidence"][0]
    assert "No channel may write actuator policy" in resume_conditions["global_no_write_boundary"]


def test_governance_agent_consumes_field_activation_matrix_without_resuming_model_chain() -> None:
    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=_agent48_ready_metrics(),
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        grey_box_physics_metrics=_grey_box_physics_metrics(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
        engineering_constraints_metrics=_engineering_constraints_metrics(),
        knowledge_graph_reasoning_metrics=_kg_reasoning_metrics(),
        main_chain_reconnection_metrics=_main_chain_reconnection_metrics(),
        field_validation_queue_alignment_metrics=_field_validation_alignment_metrics(),
        claim_specific_field_package_metrics=_claim_specific_field_package_metrics(),
        unified_field_evidence_gate_metrics=_unified_field_evidence_gate_metrics(),
        real_field_package_acceptance_metrics=_real_field_package_acceptance_metrics(),
        r7_pipeline_metrics=_r7_pipeline_metrics(),
        observation_contract_metrics=_observation_contract_metrics(),
        control_replay_stress_metrics=_control_replay_stress_metrics(),
        field_activation_matrix_metrics=_field_activation_matrix_metrics(),
        observation_response_bridge_metrics=_observation_response_bridge_metrics(),
        catalyst_evidence_response_gate_metrics=_catalyst_evidence_response_gate_metrics(),
        catalyst_response_submission_kit_metrics=_catalyst_response_submission_kit_metrics(),
        focused_catalyst_response_merge_metrics=_focused_catalyst_response_merge_metrics(),
        external_activation_operator_action_packet=_external_activation_operator_action_packet(),
        catalyst_field_package_slice_metrics=_catalyst_field_package_slice_metrics(),
        catalyst_slice_r7_patch_candidate_metrics=_catalyst_slice_r7_patch_candidate_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])

    core_gate = report.metrics["quantified_core_score_gate"]
    actions_by_channel = {
        action["channel_id"]: action for action in core_gate["next_allowed_actions"]
    }
    r7_action = actions_by_channel["R7_REAL_FIELD_PACKAGE"]
    new_interface = actions_by_channel["NEW_CORE_INTERFACE"]
    resume_conditions = core_gate["external_resume_conditions"]
    recommended = report.metrics["recommended_next_core_action"]

    assert recommended["task_id"] == "FIELD_ACTIVATION_RESPONSE_FOCUS_HANDOFF_NEXT_ACTION"
    assert recommended["first_blocked_step"] == "response_source"
    assert recommended["blocked_by"] == "R8U106_SUBMIT_FIELD_ACTIVATION_RESPONSE"
    assert recommended["next_operator_action"] == (
        "fill_focused_catalyst_response_template_then_set_FOCUSED_CATALYST_RESPONSE_PATH_"
        "and_merge_to_FIELD_ACTIVATION_RESPONSE_PATH"
    )
    assert recommended["external_blocker"] is True
    assert "focused handoff 已就绪" in recommended["next_experiment"]
    assert "FOCUSED_CATALYST_RESPONSE_PATH" in recommended["next_experiment"]
    assert (
        ".venv/bin/python experiments/run_focused_catalyst_response_merge.py"
        in recommended["next_experiment"]
    )
    assert "不能替代完整 field activation response" in recommended["failure_boundary"]
    assert r7_action["external_activation_operator_action_packet_status"] == (
        "operator_packet_waiting_for_focused_catalyst_response"
    )
    assert r7_action["external_activation_operator_action_packet_focused_candidate_availability_status"] == (
        "candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH"
    )
    assert (
        r7_action[
            "external_activation_operator_action_packet_focused_candidate_operator_packet_submit_ready"
        ]
        is False
    )
    assert r7_action["external_activation_operator_action_packet_can_resume_model_chain"] is False
    assert r7_action["external_activation_operator_action_packet_can_write_to_actuator"] is False
    assert r7_action["external_activation_operator_action_packet_can_write_to_release_gate"] is False
    assert new_interface["new_core_interface_id"] == "R8u97_field_activation_matrix_interface"
    assert new_interface["new_core_interface_status"] == (
        "field_activation_matrix_ready_for_state_level_external_collection"
    )
    assert new_interface["new_core_interface_hidden_state_row_count"] == 6
    assert new_interface["new_core_interface_no_write_boundary_complete"] is True
    assert new_interface["new_core_interface_response_source_preflight_status"] == (
        "field_activation_response_source_using_default_template"
    )
    assert new_interface["new_core_interface_response_source_external_response_supplied"] is False
    assert new_interface["new_core_interface_response_source_can_run_response_preflight"] is True
    assert new_interface["new_core_interface_response_repair_work_order_status"] == (
        "field_activation_response_repair_work_order_waiting_for_external_response"
    )
    assert new_interface["new_core_interface_response_repair_item_count"] == 7
    assert new_interface["new_core_interface_response_repair_highest_priority_repair_id"] == (
        "R8U102_SUBMIT_FIELD_ACTIVATION_RESPONSE"
    )
    assert new_interface["new_core_interface_response_preflight_status"] == (
        "field_activation_response_blocked_before_external_package_preflight"
    )
    assert new_interface["new_core_interface_response_missing_value_payload_row_count"] == 0
    assert new_interface["new_core_interface_response_template_value_payload_row_count"] == 33
    assert new_interface["new_core_interface_response_can_route"] is False
    assert new_interface["new_core_interface_response_focus_handoff_repair_work_order_status"] == (
        "focused_catalyst_response_repair_work_order_waiting_for_external_response"
    )
    assert new_interface["new_core_interface_response_focus_handoff_repair_item_count"] == 1
    assert new_interface["new_core_interface_response_focus_handoff_repair_next_operator_action"] == (
        "fill_outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json_"
        "with_real_field_values_then_set_FOCUSED_CATALYST_RESPONSE_PATH"
    )
    assert new_interface["new_core_interface_external_activation_operator_action_packet_status"] == (
        "operator_packet_waiting_for_focused_catalyst_response"
    )
    assert (
        new_interface[
            "new_core_interface_external_activation_operator_action_packet_target_hidden_state"
        ]
        == "catalyst_activity"
    )
    assert new_interface["new_core_interface_external_activation_operator_action_packet_source_env_var"] == (
        "FOCUSED_CATALYST_RESPONSE_PATH"
    )
    assert (
        new_interface[
            "new_core_interface_external_activation_operator_action_packet_expected_focused_response_row_count"
        ]
        == 6
    )
    assert new_interface[
        "new_core_interface_external_activation_operator_action_packet_focused_candidate_availability_status"
    ] == "candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH"
    assert (
        new_interface[
            "new_core_interface_external_activation_operator_action_packet_focused_candidate_operator_packet_submit_ready"
        ]
        is False
    )
    assert new_interface[
        "new_core_interface_external_activation_operator_action_packet_next_operator_action"
    ] == (
        "fill_outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json_"
        "with_real_field_values_then_set_FOCUSED_CATALYST_RESPONSE_PATH"
    )
    assert new_interface["new_core_interface_external_activation_operator_action_packet_boundary_pass"] is True
    assert (
        new_interface[
            "new_core_interface_external_activation_operator_action_packet_can_resume_model_chain"
        ]
        is False
    )
    assert (
        new_interface[
            "new_core_interface_external_activation_operator_action_packet_can_write_to_actuator"
        ]
        is False
    )
    assert (
        new_interface[
            "new_core_interface_external_activation_operator_action_packet_can_write_to_release_gate"
        ]
        is False
    )
    assert new_interface["new_core_interface_package_assembly_status"] == (
        "field_activation_package_assembly_plan_blocked_by_response_preflight"
    )
    assert new_interface["new_core_interface_package_assembly_can_stage"] is False
    assert new_interface["new_core_interface_package_staging_status"] == (
        "field_activation_package_staging_manifest_blocked_by_response_preflight"
    )
    assert new_interface["new_core_interface_package_staging_can_materialize"] is False
    assert new_interface["new_core_interface_package_staging_next_operator_action"] == (
        "complete_response_preflight_and_package_assembly_before_staging"
    )
    assert new_interface["new_core_interface_materialized_package_preflight_status"] == (
        "field_activation_materialized_package_preflight_blocked_by_staging_manifest"
    )
    assert new_interface["new_core_interface_materialized_package_can_route"] is False
    assert new_interface["new_core_interface_external_readiness_gate_status"] == (
        "field_activation_external_readiness_waiting_for_external_response"
    )
    assert new_interface["new_core_interface_external_readiness_next_operator_action"] == (
        "set_FIELD_ACTIVATION_RESPONSE_PATH_to_filled_external_response_json"
    )
    assert new_interface["new_core_interface_external_readiness_can_submit"] is False
    assert new_interface["new_core_interface_response_submission_packet_status"] == (
        "field_activation_response_submission_packet_waiting_for_external_response"
    )
    assert new_interface["new_core_interface_response_submission_next_operator_action"] == (
        "fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH"
    )
    assert new_interface["new_core_interface_response_submission_can_route"] is False
    assert new_interface["new_core_interface_schema_preflight_status"] == (
        "field_activation_schema_preflight_passed"
    )
    assert new_interface["new_core_interface_schema_can_validate_response_structure"] is True
    assert new_interface["new_core_interface_schema_can_resume_model_chain"] is False
    assert new_interface["new_core_interface_schema_can_write_to_actuator"] is False
    assert new_interface["new_core_interface_schema_can_write_to_release_gate"] is False
    assert new_interface["action_resume_state"] == (
        "new_core_interface_defined_waiting_for_external_evidence"
    )
    assert new_interface["can_resume_model_chain"] is False
    assert new_interface["router_preflight_status"] == (
        "new_interface_defined_no_model_chain_resume_without_external_evidence"
    )
    assert resume_conditions["new_core_interface"]["interface_status"] == (
        "field_activation_matrix_ready_for_state_level_external_collection"
    )
    assert resume_conditions["new_core_interface"]["can_resume_model_chain"] is False
    assert resume_conditions["new_core_interface"]["can_write_to_actuator"] is False
    assert resume_conditions["new_core_interface"]["can_write_to_release_gate"] is False
    assert resume_conditions["new_core_interface"]["response_source_preflight_status"] == (
        "field_activation_response_source_using_default_template"
    )
    assert resume_conditions["new_core_interface"]["response_source_external_response_supplied"] is False
    assert resume_conditions["new_core_interface"]["response_source_can_run_response_preflight"] is True
    assert resume_conditions["new_core_interface"]["response_repair_work_order_status"] == (
        "field_activation_response_repair_work_order_waiting_for_external_response"
    )
    assert resume_conditions["new_core_interface"]["response_repair_item_count"] == 7
    assert resume_conditions["new_core_interface"]["response_repair_highest_priority_repair_id"] == (
        "R8U102_SUBMIT_FIELD_ACTIVATION_RESPONSE"
    )
    assert resume_conditions["new_core_interface"]["response_preflight_status"] == (
        "field_activation_response_blocked_before_external_package_preflight"
    )
    assert resume_conditions["new_core_interface"]["response_template_marker_row_count"] == 33
    assert resume_conditions["new_core_interface"]["response_missing_value_payload_row_count"] == 0
    assert resume_conditions["new_core_interface"]["response_template_value_payload_row_count"] == 33
    assert resume_conditions["new_core_interface"]["response_can_route_to_external_activation_router"] is False
    assert resume_conditions["new_core_interface"]["package_assembly_status"] == (
        "field_activation_package_assembly_plan_blocked_by_response_preflight"
    )
    assert resume_conditions["new_core_interface"]["package_assembly_candidate_channel_plan_count"] == 2
    assert resume_conditions["new_core_interface"]["package_assembly_can_stage_external_package_candidates"] is False
    assert resume_conditions["new_core_interface"]["package_staging_status"] == (
        "field_activation_package_staging_manifest_blocked_by_response_preflight"
    )
    assert resume_conditions["new_core_interface"]["package_staging_selected_channel_manifest_count"] == 1
    assert resume_conditions["new_core_interface"]["package_staging_candidate_channel_requirement_count"] == 2
    assert (
        resume_conditions["new_core_interface"][
            "package_staging_can_materialize_no_write_package_candidates"
        ]
        is False
    )
    assert resume_conditions["new_core_interface"]["package_staging_next_operator_action"] == (
        "complete_response_preflight_and_package_assembly_before_staging"
    )
    assert resume_conditions["new_core_interface"]["materialized_package_preflight_status"] == (
        "field_activation_materialized_package_preflight_blocked_by_staging_manifest"
    )
    assert resume_conditions["new_core_interface"]["materialized_package_blocker_count"] == 1
    assert resume_conditions["new_core_interface"]["materialized_package_highest_priority_blocker"] == (
        "R8U105_STAGING_MANIFEST_NOT_READY"
    )
    assert (
        resume_conditions["new_core_interface"][
            "materialized_package_can_route_to_external_activation_router"
        ]
        is False
    )
    assert resume_conditions["new_core_interface"]["materialized_package_next_operator_action"] == (
        "complete_field_activation_staging_manifest_before_materializing_package"
    )
    assert resume_conditions["new_core_interface"]["external_readiness_gate_status"] == (
        "field_activation_external_readiness_waiting_for_external_response"
    )
    assert resume_conditions["new_core_interface"]["external_readiness_first_blocked_step"] == (
        "response_source"
    )
    assert resume_conditions["new_core_interface"]["external_readiness_highest_priority_blocker"] == (
        "R8U106_SUBMIT_FIELD_ACTIVATION_RESPONSE"
    )
    assert resume_conditions["new_core_interface"]["external_readiness_next_operator_action"] == (
        "set_FIELD_ACTIVATION_RESPONSE_PATH_to_filled_external_response_json"
    )
    assert (
        resume_conditions["new_core_interface"][
            "external_readiness_can_submit_to_external_activation_router"
        ]
        is False
    )
    assert resume_conditions["new_core_interface"]["response_submission_packet_status"] == (
        "field_activation_response_submission_packet_waiting_for_external_response"
    )
    assert resume_conditions["new_core_interface"]["response_submission_highest_priority_blocker"] == (
        "R8U106_SUBMIT_FIELD_ACTIVATION_RESPONSE"
    )
    assert resume_conditions["new_core_interface"]["response_submission_next_operator_action"] == (
        "fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH"
    )
    assert (
        resume_conditions["new_core_interface"][
            "response_submission_can_route_to_external_activation_router"
        ]
        is False
    )
    assert resume_conditions["new_core_interface"]["response_focus_handoff_repair_work_order_status"] == (
        "focused_catalyst_response_repair_work_order_waiting_for_external_response"
    )
    assert resume_conditions["new_core_interface"]["response_focus_handoff_repair_item_count"] == 1
    assert resume_conditions["new_core_interface"]["response_focus_handoff_repair_next_operator_action"] == (
        "fill_outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json_"
        "with_real_field_values_then_set_FOCUSED_CATALYST_RESPONSE_PATH"
    )
    assert resume_conditions["new_core_interface"]["external_activation_operator_action_packet_status"] == (
        "operator_packet_waiting_for_focused_catalyst_response"
    )
    assert (
        resume_conditions["new_core_interface"][
            "external_activation_operator_action_packet_target_hidden_state"
        ]
        == "catalyst_activity"
    )
    assert resume_conditions["new_core_interface"]["external_activation_operator_action_packet_source_env_var"] == (
        "FOCUSED_CATALYST_RESPONSE_PATH"
    )
    assert (
        resume_conditions["new_core_interface"][
            "external_activation_operator_action_packet_expected_focused_response_row_count"
        ]
        == 6
    )
    assert resume_conditions["new_core_interface"][
        "external_activation_operator_action_packet_focused_candidate_availability_status"
    ] == "candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH"
    assert (
        resume_conditions["new_core_interface"][
            "external_activation_operator_action_packet_focused_candidate_operator_packet_submit_ready"
        ]
        is False
    )
    assert resume_conditions["new_core_interface"][
        "external_activation_operator_action_packet_next_operator_action"
    ] == (
        "fill_outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json_"
        "with_real_field_values_then_set_FOCUSED_CATALYST_RESPONSE_PATH"
    )
    assert (
        resume_conditions["new_core_interface"]["external_activation_operator_action_packet_boundary_pass"]
        is True
    )
    assert (
        resume_conditions["new_core_interface"][
            "external_activation_operator_action_packet_can_resume_model_chain"
        ]
        is False
    )
    assert (
        resume_conditions["new_core_interface"][
            "external_activation_operator_action_packet_can_write_to_actuator"
        ]
        is False
    )
    assert (
        resume_conditions["new_core_interface"][
            "external_activation_operator_action_packet_can_write_to_release_gate"
        ]
        is False
    )
    assert resume_conditions["new_core_interface"]["schema_preflight_status"] == (
        "field_activation_schema_preflight_passed"
    )
    assert resume_conditions["new_core_interface"]["schema_can_validate_response_structure"] is True
    assert resume_conditions["new_core_interface"]["schema_can_resume_model_chain"] is False
    assert resume_conditions["new_core_interface"]["schema_can_write_to_actuator"] is False
    assert resume_conditions["new_core_interface"]["schema_can_write_to_release_gate"] is False
    assert report.metrics["governance_scorecard"]["field_activation_matrix_hidden_state_row_count"] == 6
    assert report.metrics["governance_scorecard"]["field_activation_matrix_can_resume_model_chain"] is False
    assert report.metrics["governance_scorecard"]["field_activation_response_source_preflight_status"] == (
        "field_activation_response_source_using_default_template"
    )
    assert (
        report.metrics["governance_scorecard"][
            "field_activation_response_source_external_response_supplied"
        ]
        is False
    )
    assert (
        report.metrics["governance_scorecard"][
            "field_activation_response_source_can_run_response_preflight"
        ]
        is True
    )
    assert report.metrics["governance_scorecard"]["field_activation_response_repair_work_order_status"] == (
        "field_activation_response_repair_work_order_waiting_for_external_response"
    )
    assert report.metrics["governance_scorecard"]["field_activation_response_repair_item_count"] == 7
    assert report.metrics["governance_scorecard"]["field_activation_response_repair_highest_priority_repair_id"] == (
        "R8U102_SUBMIT_FIELD_ACTIVATION_RESPONSE"
    )
    assert report.metrics["governance_scorecard"]["field_activation_response_preflight_status"] == (
        "field_activation_response_blocked_before_external_package_preflight"
    )
    assert (
        report.metrics["governance_scorecard"]["field_activation_response_missing_value_payload_row_count"]
        == 0
    )
    assert (
        report.metrics["governance_scorecard"]["field_activation_response_template_value_payload_row_count"]
        == 33
    )
    assert report.metrics["governance_scorecard"]["field_activation_response_coherence_audit_status"] == (
        "field_activation_response_coherence_audit_waiting_for_response_preflight"
    )
    assert report.metrics["governance_scorecard"]["field_activation_response_coherence_hard_blocker_count"] == 0
    assert (
        report.metrics["governance_scorecard"][
            "field_activation_response_coherence_can_route_to_package_assembly"
        ]
        is False
    )
    assert report.metrics["governance_scorecard"]["field_activation_package_assembly_status"] == (
        "field_activation_package_assembly_plan_blocked_by_response_preflight"
    )
    assert report.metrics["governance_scorecard"]["field_activation_package_staging_status"] == (
        "field_activation_package_staging_manifest_blocked_by_response_preflight"
    )
    assert (
        report.metrics["governance_scorecard"][
            "field_activation_package_staging_can_materialize_no_write_package_candidates"
        ]
        is False
    )
    assert report.metrics["governance_scorecard"]["field_activation_materialized_package_preflight_status"] == (
        "field_activation_materialized_package_preflight_blocked_by_staging_manifest"
    )
    assert report.metrics["governance_scorecard"]["field_activation_materialized_package_preflight_blocker_count"] == 1
    assert (
        report.metrics["governance_scorecard"][
            "field_activation_materialized_package_preflight_highest_priority_blocker"
        ]
        == "R8U105_STAGING_MANIFEST_NOT_READY"
    )
    assert (
        report.metrics["governance_scorecard"][
            "field_activation_materialized_package_preflight_can_route_to_external_activation_router"
        ]
        is False
    )
    assert report.metrics["governance_scorecard"]["field_activation_external_readiness_gate_status"] == (
        "field_activation_external_readiness_waiting_for_external_response"
    )
    assert report.metrics["governance_scorecard"]["field_activation_external_readiness_first_blocked_step"] == (
        "response_source"
    )
    assert report.metrics["governance_scorecard"]["field_activation_external_readiness_highest_priority_blocker"] == (
        "R8U106_SUBMIT_FIELD_ACTIVATION_RESPONSE"
    )
    assert report.metrics["governance_scorecard"]["field_activation_external_readiness_next_operator_action"] == (
        "set_FIELD_ACTIVATION_RESPONSE_PATH_to_filled_external_response_json"
    )
    assert (
        report.metrics["governance_scorecard"][
            "field_activation_external_readiness_can_submit_to_external_activation_router"
        ]
        is False
    )
    assert report.metrics["governance_scorecard"]["field_activation_response_submission_packet_status"] == (
        "field_activation_response_submission_packet_waiting_for_external_response"
    )
    assert report.metrics["governance_scorecard"][
        "field_activation_response_submission_packet_next_operator_action"
    ] == "fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH"
    assert report.metrics["governance_scorecard"][
        "field_activation_response_submission_packet_highest_priority_blocker"
    ] == "R8U106_SUBMIT_FIELD_ACTIVATION_RESPONSE"
    assert (
        report.metrics["governance_scorecard"][
            "field_activation_response_submission_packet_can_route_to_external_activation_router"
        ]
        is False
    )
    assert report.metrics["governance_scorecard"]["field_activation_response_completion_ledger_status"] == (
        "field_activation_response_completion_waiting_for_external_response"
    )
    assert report.metrics["governance_scorecard"]["field_activation_response_next_hidden_state_focus"] == (
        "catalyst_activity"
    )
    assert report.metrics["governance_scorecard"]["field_activation_response_focus_handoff_status"] == (
        "field_activation_response_focus_handoff_ready_for_catalyst_activity"
    )
    assert report.metrics["governance_scorecard"]["field_activation_response_focus_handoff_target_hidden_state"] == (
        "catalyst_activity"
    )
    assert report.metrics["governance_scorecard"][
        "field_activation_response_focus_handoff_row_scan_reduction_ratio"
    ] == 0.818
    assert report.metrics["governance_scorecard"]["field_activation_response_focus_handoff_source_env_var"] == (
        "FOCUSED_CATALYST_RESPONSE_PATH"
    )
    assert (
        report.metrics["governance_scorecard"][
            "field_activation_response_focus_handoff_can_submit_to_external_activation_router"
        ]
        is False
    )
    assert report.metrics["governance_scorecard"][
        "field_activation_response_focus_handoff_repair_work_order_status"
    ] == "focused_catalyst_response_repair_work_order_waiting_for_external_response"
    assert (
        report.metrics["governance_scorecard"][
            "field_activation_response_focus_handoff_repair_item_count"
        ]
        == 1
    )
    assert report.metrics["governance_scorecard"][
        "field_activation_response_focus_handoff_repair_next_operator_action"
    ] == (
        "fill_outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json_"
        "with_real_field_values_then_set_FOCUSED_CATALYST_RESPONSE_PATH"
    )
    assert report.metrics["governance_scorecard"][
        "external_activation_operator_action_packet_status"
    ] == "operator_packet_waiting_for_focused_catalyst_response"
    assert report.metrics["governance_scorecard"][
        "external_activation_operator_action_packet_target_hidden_state"
    ] == "catalyst_activity"
    assert report.metrics["governance_scorecard"][
        "external_activation_operator_action_packet_source_env_var"
    ] == "FOCUSED_CATALYST_RESPONSE_PATH"
    assert report.metrics["governance_scorecard"][
        "external_activation_operator_action_packet_expected_focused_response_row_count"
    ] == 6
    assert report.metrics["governance_scorecard"][
        "external_activation_operator_action_packet_focused_candidate_availability_status"
    ] == "candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH"
    assert (
        report.metrics["governance_scorecard"][
            "external_activation_operator_action_packet_focused_candidate_operator_packet_submit_ready"
        ]
        is False
    )
    assert report.metrics["governance_scorecard"][
        "external_activation_operator_action_packet_next_operator_action"
    ] == (
        "fill_outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json_"
        "with_real_field_values_then_set_FOCUSED_CATALYST_RESPONSE_PATH"
    )
    assert report.metrics["governance_scorecard"][
        "external_activation_operator_action_packet_boundary_pass"
    ] is True
    assert report.metrics["governance_scorecard"][
        "external_activation_operator_action_packet_can_resume_model_chain"
    ] is False
    assert report.metrics["governance_scorecard"][
        "external_activation_operator_action_packet_can_write_to_actuator"
    ] is False
    assert report.metrics["governance_scorecard"][
        "external_activation_operator_action_packet_can_write_to_release_gate"
    ] is False
    assert report.metrics["governance_scorecard"]["field_evidence_wait_status"][
        "external_activation_operator_action_packet_status"
    ] == "operator_packet_waiting_for_focused_catalyst_response"
    assert report.metrics["governance_scorecard"]["field_evidence_wait_status"][
        "external_activation_operator_action_packet_boundary_pass"
    ] is True
    assert report.metrics["governance_scorecard"]["field_evidence_wait_status"][
        "external_activation_operator_action_packet_focused_candidate_availability_status"
    ] == "candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH"
    assert report.metrics["governance_scorecard"]["observation_response_bridge_status"] == (
        "observation_response_bridge_ready_for_priority_field_response_fill"
    )
    assert report.metrics["governance_scorecard"]["observation_response_bridge_target_hidden_state"] == (
        "catalyst_activity"
    )
    assert report.metrics["governance_scorecard"]["observation_response_bridge_response_row_count"] == 6
    assert report.metrics["governance_scorecard"]["observation_response_bridge_required_role_coverage_rate"] == 1.0
    assert (
        report.metrics["governance_scorecard"][
            "observation_response_bridge_can_route_to_agent51_field_proxy_holdout"
        ]
        is False
    )
    assert (
        report.metrics["governance_scorecard"][
            "observation_response_bridge_can_relax_agent49_catalyst_uncertainty_block"
        ]
        is False
    )
    assert report.metrics["governance_scorecard"]["catalyst_evidence_response_gate_status"] == (
        "catalyst_evidence_response_gate_waiting_for_FIELD_ACTIVATION_RESPONSE_PATH"
    )
    assert report.metrics["governance_scorecard"]["catalyst_evidence_response_gate_target_response_row_count"] == 6
    assert report.metrics["governance_scorecard"]["catalyst_evidence_response_gate_row_level_preflight_pass"] is False
    assert report.metrics["governance_scorecard"]["catalyst_evidence_response_gate_matched_batch_count"] == 0
    assert (
        report.metrics["governance_scorecard"][
            "catalyst_evidence_response_gate_matched_batch_requirement_pass"
        ]
        is False
    )
    assert (
        report.metrics["governance_scorecard"][
            "catalyst_evidence_response_gate_can_route_to_focused_materialized_package_preflight"
        ]
        is False
    )
    assert (
        report.metrics["governance_scorecard"][
            "catalyst_evidence_response_gate_can_route_to_agent51_field_proxy_holdout"
        ]
        is False
    )
    assert report.metrics["governance_scorecard"]["catalyst_response_submission_kit_status"] == (
        "catalyst_response_submission_kit_ready_for_operator_fill"
    )
    assert report.metrics["governance_scorecard"]["catalyst_response_submission_kit_target_response_row_count"] == 6
    assert report.metrics["governance_scorecard"]["catalyst_response_submission_kit_focused_template_path"] == (
        "outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json"
    )
    assert (
        report.metrics["governance_scorecard"][
            "catalyst_response_submission_kit_can_route_to_agent51_field_proxy_holdout"
        ]
        is False
    )
    assert report.metrics["governance_scorecard"]["focused_catalyst_response_merge_status"] == (
        "focused_catalyst_response_merge_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH"
    )
    assert report.metrics["governance_scorecard"]["focused_catalyst_response_source_preflight_status"] == (
        "focused_catalyst_response_source_using_default_template"
    )
    assert (
        report.metrics["governance_scorecard"][
            "focused_catalyst_response_source_can_run_merge_preflight"
        ]
        is True
    )
    assert report.metrics["governance_scorecard"]["focused_catalyst_response_merge_row_preflight_pass"] is False
    assert report.metrics["governance_scorecard"]["focused_catalyst_response_repair_work_order_status"] == (
        "focused_catalyst_response_repair_work_order_waiting_for_external_response"
    )
    assert report.metrics["governance_scorecard"]["focused_catalyst_response_repair_item_count"] == 1
    assert report.metrics["governance_scorecard"]["focused_catalyst_response_repair_highest_priority_repair_id"] == (
        "FOCUSED_SOURCE_SUBMIT_RESPONSE"
    )
    assert report.metrics["governance_scorecard"]["focused_catalyst_response_merge_can_emit_candidate"] is False
    assert (
        report.metrics["governance_scorecard"][
            "focused_catalyst_response_merge_can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH"
        ]
        is False
    )
    assert report.metrics["governance_scorecard"][
        "focused_catalyst_response_merge_candidate_availability_status"
    ] == "candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH"
    assert (
        report.metrics["governance_scorecard"][
            "focused_catalyst_response_merge_candidate_preflight_submit_ready"
        ]
        is False
    )
    assert (
        report.metrics["governance_scorecard"][
            "focused_catalyst_response_merge_candidate_self_declared_submit_ready"
        ]
        is False
    )
    assert (
        "not field validation"
        in report.metrics["governance_scorecard"][
            "focused_catalyst_response_merge_candidate_submit_ready_semantics"
        ]
    )
    assert (
        report.metrics["governance_scorecard"][
            "focused_catalyst_response_merge_can_route_to_agent51_field_proxy_holdout"
        ]
        is False
    )
    assert report.metrics["governance_scorecard"]["catalyst_field_package_slice_status"] == (
        "catalyst_field_package_slice_waiting_for_CATALYST_FIELD_PACKAGE_SLICE_DIR"
    )
    assert report.metrics["governance_scorecard"]["catalyst_field_package_slice_preflight_pass"] is False
    assert report.metrics["governance_scorecard"]["catalyst_field_package_slice_matched_batch_count"] == 0
    assert report.metrics["governance_scorecard"]["catalyst_field_package_slice_template_dir"] == (
        "outputs/catalyst_field_package_slice/focused_field_package_slice_template"
    )
    assert (
        report.metrics["governance_scorecard"][
            "catalyst_field_package_slice_can_route_to_r7_field_package_patch_candidate"
        ]
        is False
    )
    assert (
        report.metrics["governance_scorecard"][
            "catalyst_field_package_slice_can_route_to_agent51_field_proxy_holdout"
        ]
        is False
    )
    assert report.metrics["governance_scorecard"]["catalyst_slice_r7_patch_candidate_status"] == (
        "catalyst_slice_r7_patch_waiting_for_valid_catalyst_slice"
    )
    assert report.metrics["governance_scorecard"]["catalyst_slice_r7_patch_candidate_materialized"] is False
    assert report.metrics["governance_scorecard"]["catalyst_slice_r7_patch_candidate_preflight_status"] == "not_run"
    assert report.metrics["governance_scorecard"]["catalyst_slice_r7_patch_candidate_remaining_gap_count"] == 0
    assert (
        report.metrics["governance_scorecard"][
            "catalyst_slice_r7_patch_candidate_can_submit_as_REAL_FIELD_REPLAY_PACKAGE_DIR"
        ]
        is False
    )
    assert report.metrics["governance_scorecard"]["field_activation_schema_preflight_status"] == (
        "field_activation_schema_preflight_passed"
    )
    assert (
        report.metrics["governance_scorecard"][
            "field_activation_schema_can_validate_response_structure"
        ]
        is True
    )


def test_governance_agent_treats_r7_sufficiency_smoke_pass_as_import_progress() -> None:
    metrics = _agent48_ready_metrics()
    claim_metrics = _claim_specific_field_package_metrics()
    claim_metrics["readiness"]["source_basis_completion_rate"] = 1.0
    r7_pipeline = _r7_pipeline_metrics(
        status="field_evidence_sufficiency_smoke_ready_needs_calibration_event_volume",
        smoke_pass=True,
        human_review_candidate=False,
    )

    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=metrics,
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        grey_box_physics_metrics=_grey_box_physics_metrics(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
        engineering_constraints_metrics=_engineering_constraints_metrics(),
        knowledge_graph_reasoning_metrics=_kg_reasoning_metrics(),
        main_chain_reconnection_metrics=_main_chain_reconnection_metrics(),
        field_validation_queue_alignment_metrics=_field_validation_alignment_metrics(),
        claim_specific_field_package_metrics=claim_metrics,
        unified_field_evidence_gate_metrics=_unified_field_evidence_gate_metrics(),
        real_field_package_acceptance_metrics=_real_field_package_acceptance_metrics(),
        r7_pipeline_metrics=r7_pipeline,
        observation_contract_metrics=_observation_contract_metrics(),
        control_replay_stress_metrics=_control_replay_stress_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])

    wait_status = report.metrics["governance_scorecard"]["field_evidence_wait_status"]

    assert wait_status["field_import_ready"] is True
    assert wait_status["external_field_blocker_active"] is False
    assert wait_status["r7_field_evidence_smoke_pass"] is True
    assert wait_status["r7_can_route_to_agent42_smoke_replay"] is True
    assert wait_status["r7_can_route_to_human_review_candidate"] is False
    assert report.metrics["recommended_next_core_action"]["task_id"] != "WAIT_real_field_package_or_new_core_interface"


def test_governance_agent_records_path_endpoint_label_preflight_blocker() -> None:
    metrics = _agent48_ready_metrics()
    claim_metrics = _claim_specific_field_package_metrics()
    claim_metrics["readiness"]["source_basis_completion_rate"] = 1.0

    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=metrics,
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        grey_box_physics_metrics=_grey_box_physics_metrics(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
        engineering_constraints_metrics=_engineering_constraints_metrics(),
        knowledge_graph_reasoning_metrics=_kg_reasoning_metrics(),
        main_chain_reconnection_metrics=_main_chain_reconnection_metrics(),
        field_validation_queue_alignment_metrics=_field_validation_alignment_metrics(),
        claim_specific_field_package_metrics=claim_metrics,
        unified_field_evidence_gate_metrics=_unified_field_evidence_gate_metrics(),
        real_field_package_acceptance_metrics=_real_field_package_acceptance_metrics(),
        r7_pipeline_metrics=_r7_pipeline_metrics(),
        field_path_endpoint_label_preflight=_field_path_endpoint_label_preflight_blocked(),
        observation_contract_metrics=_observation_contract_metrics(),
        control_replay_stress_metrics=_control_replay_stress_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])

    scorecard = report.metrics["governance_scorecard"]
    wait_status = scorecard["field_evidence_wait_status"]

    assert scorecard["field_path_endpoint_label_preflight_status"] == "no_field_path_endpoint_label_package_supplied"
    assert scorecard["field_path_endpoint_label_package_ready"] is False
    assert scorecard["field_path_endpoint_required_matched_batch_deficit"] == 5
    assert scorecard["field_path_endpoint_alignment_patch_plan_status"] == (
        "field_path_endpoint_alignment_blocked_by_preflight"
    )
    assert wait_status["field_path_endpoint_missing_tables"] == [
        "site_topology_or_bed_geometry",
        "node_modality_sensor_timeseries",
        "hydraulic_path_stage_labels",
        "final_effluent_endpoint_labels",
        "campaign_operation_log",
        "offline_lab_results",
    ]
    assert wait_status["can_route_to_field_layout_holdout_with_path_labels"] is False
    assert wait_status["release_gate_endpoint_label_blocked"] is True
    assert any(
        issue.issue_type == "field_path_endpoint_label_package_required"
        for issue in report.issues
    )


def test_governance_agent_allows_layout_holdout_route_only_with_path_endpoint_labels() -> None:
    metrics = _agent48_ready_metrics()
    claim_metrics = _claim_specific_field_package_metrics()
    claim_metrics["readiness"]["source_basis_completion_rate"] = 1.0
    r7_pipeline = _r7_pipeline_metrics(
        status="field_evidence_sufficiency_smoke_ready_needs_calibration_event_volume",
        smoke_pass=True,
        human_review_candidate=False,
    )

    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=metrics,
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        grey_box_physics_metrics=_grey_box_physics_metrics(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
        engineering_constraints_metrics=_engineering_constraints_metrics(),
        knowledge_graph_reasoning_metrics=_kg_reasoning_metrics(),
        main_chain_reconnection_metrics=_main_chain_reconnection_metrics(),
        field_validation_queue_alignment_metrics=_field_validation_alignment_metrics(),
        claim_specific_field_package_metrics=claim_metrics,
        unified_field_evidence_gate_metrics=_unified_field_evidence_gate_metrics(),
        real_field_package_acceptance_metrics=_real_field_package_acceptance_metrics(),
        r7_pipeline_metrics=r7_pipeline,
        field_path_endpoint_label_preflight=_field_path_endpoint_label_preflight_ready(),
        observation_contract_metrics=_observation_contract_metrics(),
        control_replay_stress_metrics=_control_replay_stress_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])

    wait_status = report.metrics["governance_scorecard"]["field_evidence_wait_status"]
    no_write = report.metrics["quantified_core_score_gate"]["no_write_boundaries"]

    assert wait_status["field_import_ready"] is True
    assert wait_status["field_path_endpoint_label_package_ready"] is True
    assert wait_status["field_path_endpoint_final_effluent_label_ready"] is True
    assert wait_status["field_path_endpoint_required_matched_batch_deficit"] == 0
    assert wait_status["field_path_endpoint_alignment_patch_plan_status"] == "field_path_endpoint_alignment_ready"
    assert wait_status["can_route_to_field_layout_holdout_with_path_labels"] is True
    assert wait_status["release_gate_endpoint_label_blocked"] is False
    assert no_write["can_write_to_release_gate"] is False
    assert report.metrics["recommended_next_core_action"]["task_id"] != "WAIT_real_field_package_or_new_core_interface"


def test_governance_agent_consumes_formal_search_execution_route_plan() -> None:
    baseline = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=_agent48_ready_metrics(),
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        grey_box_physics_metrics=_grey_box_physics_metrics(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
        engineering_constraints_metrics=_engineering_constraints_metrics(),
        knowledge_graph_reasoning_metrics=_kg_reasoning_metrics(),
        main_chain_reconnection_metrics=_main_chain_reconnection_metrics(),
        field_validation_queue_alignment_metrics=_field_validation_alignment_metrics(),
        claim_specific_field_package_metrics=_claim_specific_field_package_metrics(),
        unified_field_evidence_gate_metrics=_unified_field_evidence_gate_metrics(),
        real_field_package_acceptance_metrics=_real_field_package_acceptance_metrics(),
        r7_pipeline_metrics=_r7_pipeline_metrics(),
        field_path_endpoint_label_preflight=_field_path_endpoint_label_preflight_blocked(),
        observation_contract_metrics=_observation_contract_metrics(),
        control_replay_stress_metrics=_control_replay_stress_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])
    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=_agent48_ready_metrics(),
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        grey_box_physics_metrics=_grey_box_physics_metrics(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
        engineering_constraints_metrics=_engineering_constraints_metrics(),
        knowledge_graph_reasoning_metrics=_kg_reasoning_metrics(),
        main_chain_reconnection_metrics=_main_chain_reconnection_metrics(),
        field_validation_queue_alignment_metrics=_field_validation_alignment_metrics(),
        claim_specific_field_package_metrics=_claim_specific_field_package_metrics(),
        unified_field_evidence_gate_metrics=_unified_field_evidence_gate_metrics(),
        real_field_package_acceptance_metrics=_real_field_package_acceptance_metrics(),
        r7_pipeline_metrics=_r7_pipeline_metrics(),
        field_path_endpoint_label_preflight=_field_path_endpoint_label_preflight_blocked(),
        formal_search_execution_route_plan=_formal_search_execution_route_plan_ready(),
        observation_contract_metrics=_observation_contract_metrics(),
        control_replay_stress_metrics=_control_replay_stress_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])

    scorecard = report.metrics["governance_scorecard"]
    baseline_protectability = baseline.metrics["quantified_core_score_gate"]["ability_scores"][
        "protectability"
    ]
    route_plan_protectability = report.metrics["quantified_core_score_gate"]["ability_scores"][
        "protectability"
    ]

    assert scorecard["formal_search_execution_route_plan_status"] == (
        "formal_search_execution_route_plan_ready_waiting_for_external_search_execution"
    )
    assert scorecard["formal_search_execution_complete_route_row_count"] == 7
    assert scorecard["formal_search_execution_route_row_count"] == 7
    assert scorecard["formal_search_execution_mapped_seed_route_count"] == 7
    assert scorecard["formal_search_execution_operator_first_action"] == (
        "execute_external_or_human_search_and_submit_FORMAL_SEARCH_RESULT_PACKAGE_PATH"
    )
    assert scorecard["formal_search_execution_boundary_preserved"] is True
    assert any("R8u79 formal search execution route plan is ready" in reason for reason in report.metrics["blocked_reasons"])
    assert route_plan_protectability > baseline_protectability


def test_governance_agent_rejects_formal_search_route_plan_when_boundary_is_not_preserved() -> None:
    route_plan = _formal_search_execution_route_plan_ready()
    route_plan["can_emit_claim_text"] = True

    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=_agent48_ready_metrics(),
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        grey_box_physics_metrics=_grey_box_physics_metrics(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
        engineering_constraints_metrics=_engineering_constraints_metrics(),
        knowledge_graph_reasoning_metrics=_kg_reasoning_metrics(),
        main_chain_reconnection_metrics=_main_chain_reconnection_metrics(),
        field_validation_queue_alignment_metrics=_field_validation_alignment_metrics(),
        claim_specific_field_package_metrics=_claim_specific_field_package_metrics(),
        unified_field_evidence_gate_metrics=_unified_field_evidence_gate_metrics(),
        real_field_package_acceptance_metrics=_real_field_package_acceptance_metrics(),
        r7_pipeline_metrics=_r7_pipeline_metrics(),
        formal_search_execution_route_plan=route_plan,
        observation_contract_metrics=_observation_contract_metrics(),
        control_replay_stress_metrics=_control_replay_stress_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])

    scorecard = report.metrics["governance_scorecard"]

    assert scorecard["formal_search_execution_route_plan_status"] == (
        "formal_search_execution_route_plan_ready_waiting_for_external_search_execution"
    )
    assert scorecard["formal_search_execution_boundary_preserved"] is False
    assert not any("R8u79 formal search execution route plan is ready" in reason for reason in report.metrics["blocked_reasons"])


def test_governance_agent_outputs_external_activation_contract_for_wait_state() -> None:
    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=_agent48_ready_metrics(),
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        grey_box_physics_metrics=_grey_box_physics_metrics(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
        engineering_constraints_metrics=_engineering_constraints_metrics(),
        knowledge_graph_reasoning_metrics=_kg_reasoning_metrics(),
        main_chain_reconnection_metrics=_main_chain_reconnection_metrics(),
        field_validation_queue_alignment_metrics=_field_validation_alignment_metrics(),
        claim_specific_field_package_metrics=_claim_specific_field_package_metrics(),
        unified_field_evidence_gate_metrics=_unified_field_evidence_gate_metrics(),
        real_field_package_acceptance_metrics=_real_field_package_acceptance_metrics(),
        r7_pipeline_metrics=_r7_pipeline_metrics(),
        field_path_endpoint_label_preflight=_field_path_endpoint_label_preflight_blocked(),
        formal_search_execution_route_plan=_formal_search_execution_route_plan_ready(),
        observation_contract_metrics=_observation_contract_metrics(),
        control_replay_stress_metrics=_control_replay_stress_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])

    contract = report.metrics["external_activation_contract"]
    channels = {channel["channel_id"]: channel for channel in contract["channels"]}
    scorecard = report.metrics["governance_scorecard"]

    assert contract["contract_id"] == "R8u81_external_evidence_activation_contract"
    assert contract["contract_status"] == "waiting_for_external_evidence_packages"
    assert contract["activation_ready"] is False
    assert contract["ready_channel_count"] == 0
    assert contract["blocked_channel_count"] == 3
    assert contract["boundary_preserved"] is True
    assert scorecard["external_activation_contract_status"] == "waiting_for_external_evidence_packages"
    assert scorecard["external_activation_ready"] is False
    assert channels["R7_REAL_FIELD_PACKAGE"]["can_resume_model_chain"] is False
    assert channels["R8U66_PATH_ENDPOINT_LABEL_PACKAGE"]["can_resume_model_chain"] is False
    assert channels["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"]["ready_for_external_submission"] is True
    assert channels["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"]["can_resume_model_chain"] is False
    assert any(
        "seed matrix is submitted as accepted prior art" in rule
        for rule in channels["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"]["reject_if"]
    )
    core_gate = report.metrics["quantified_core_score_gate"]
    assert core_gate["next_allowed_actions"][0]["action_type"] == "submit_external_evidence_package"
    assert {
        action["package_pointer"]
        for action in core_gate["next_allowed_actions"]
        if action["action_type"] == "submit_external_evidence_package"
    } == {
        "REAL_FIELD_REPLAY_PACKAGE_DIR",
        "FIELD_PATH_ENDPOINT_LABEL_PACKAGE_DIR",
        "FORMAL_SEARCH_RESULT_PACKAGE_PATH",
    }
    assert core_gate["external_resume_conditions"]["contract_status"] == (
        "waiting_for_external_evidence_packages"
    )
    assert core_gate["external_resume_conditions"]["activation_ready"] is False
    assert core_gate["external_resume_conditions"]["router_status"] == (
        "external_activation_router_not_consumed_by_agent50"
    )
    assert core_gate["external_resume_conditions"]["router_consumed"] is False
    assert core_gate["external_resume_conditions"]["router_validation_command"] == (
        ".venv/bin/python experiments/run_external_activation_router.py"
    )
    assert "No channel may write actuator policy" in contract["global_no_write_boundary"]
    assert scorecard["external_activation_router_status"] == "external_activation_router_not_consumed_by_agent50"
    assert scorecard["external_activation_router_consumed"] is False
    assert scorecard["external_activation_router_route_ready_count"] == 0
    assert scorecard["external_activation_router_model_chain_ready_route_count"] == 0
    assert scorecard["external_activation_router_handoff_ready_route_count"] == 0
    assert scorecard["external_activation_router_boundary_preserved"] is False


def test_governance_agent_consumes_external_activation_router_status() -> None:
    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=_agent48_ready_metrics(),
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        grey_box_physics_metrics=_grey_box_physics_metrics(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
        engineering_constraints_metrics=_engineering_constraints_metrics(),
        knowledge_graph_reasoning_metrics=_kg_reasoning_metrics(),
        main_chain_reconnection_metrics=_main_chain_reconnection_metrics(),
        field_validation_queue_alignment_metrics=_field_validation_alignment_metrics(),
        claim_specific_field_package_metrics=_claim_specific_field_package_metrics(),
        unified_field_evidence_gate_metrics=_unified_field_evidence_gate_metrics(),
        real_field_package_acceptance_metrics=_real_field_package_acceptance_metrics(),
        r7_pipeline_metrics=_r7_pipeline_metrics(),
        field_path_endpoint_label_preflight=_field_path_endpoint_label_preflight_blocked(),
        formal_search_execution_route_plan=_formal_search_execution_route_plan_ready(),
        external_activation_router=_external_activation_router_waiting(),
        observation_contract_metrics=_observation_contract_metrics(),
        control_replay_stress_metrics=_control_replay_stress_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])

    scorecard = report.metrics["governance_scorecard"]

    assert scorecard["external_activation_router_status"] == (
        "external_activation_router_waiting_for_external_paths"
    )
    assert scorecard["external_activation_router_consumed"] is True
    assert scorecard["external_activation_router_path_supplied_count"] == 0
    assert scorecard["external_activation_router_route_ready_count"] == 0
    assert scorecard["external_activation_router_model_chain_ready_route_count"] == 0
    assert scorecard["external_activation_router_handoff_ready_route_count"] == 0
    assert scorecard["external_activation_router_blocked_route_count"] == 3
    assert scorecard["external_activation_router_boundary_preserved"] is True
    assert "never writes actuator policy" in scorecard["external_activation_router_no_write_boundary"]
    assert scorecard["external_activation_router_ready_channel_ids"] == []
    assert scorecard["external_activation_router_model_chain_ready_channel_ids"] == []
    assert scorecard["external_activation_router_handoff_ready_channel_ids"] == []
    assert scorecard["external_activation_router_blocked_channel_ids"] == [
        "R7_REAL_FIELD_PACKAGE",
        "R8U66_PATH_ENDPOINT_LABEL_PACKAGE",
        "R8U79_FORMAL_SEARCH_RESULT_PACKAGE",
    ]
    assert scorecard["external_activation_router_highest_priority_blocker"] == (
        "R7_REAL_FIELD_PACKAGE:REAL_FIELD_REPLAY_PACKAGE_DIR:not_set"
    )
    assert scorecard["external_activation_router_next_operator_action"] == "set_REAL_FIELD_REPLAY_PACKAGE_DIR"
    core_gate = report.metrics["quantified_core_score_gate"]
    resume_conditions = core_gate["external_resume_conditions"]
    assert resume_conditions["router_status"] == "external_activation_router_waiting_for_external_paths"
    assert resume_conditions["router_consumed"] is True
    assert resume_conditions["router_model_chain_ready_route_count"] == 0
    assert resume_conditions["router_handoff_ready_route_count"] == 0
    assert resume_conditions["router_blocked_route_count"] == 3
    assert resume_conditions["router_model_chain_ready_channel_ids"] == []
    assert resume_conditions["router_handoff_ready_channel_ids"] == []
    assert resume_conditions["router_highest_priority_blocker"] == (
        "R7_REAL_FIELD_PACKAGE:REAL_FIELD_REPLAY_PACKAGE_DIR:not_set"
    )
    assert resume_conditions["router_next_operator_action"] == "set_REAL_FIELD_REPLAY_PACKAGE_DIR"
    assert resume_conditions["router_route_summary"][0]["channel_id"] == "R7_REAL_FIELD_PACKAGE"
    allowed_actions = {
        action["channel_id"]: action
        for action in core_gate["next_allowed_actions"]
        if action["action_type"] == "submit_external_evidence_package"
    }
    assert allowed_actions["R7_REAL_FIELD_PACKAGE"]["router_route_status"] == (
        "activation_route_waiting_for_env_var"
    )
    assert allowed_actions["R7_REAL_FIELD_PACKAGE"]["router_operator_action"] == (
        "set_REAL_FIELD_REPLAY_PACKAGE_DIR"
    )
    assert allowed_actions["R7_REAL_FIELD_PACKAGE"]["router_validation_command"] == (
        ".venv/bin/python experiments/run_external_activation_router.py"
    )


def test_governance_agent_updates_formal_search_blocked_reason_after_handoff_ready() -> None:
    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=_agent48_ready_metrics(),
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        grey_box_physics_metrics=_grey_box_physics_metrics(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
        engineering_constraints_metrics=_engineering_constraints_metrics(),
        knowledge_graph_reasoning_metrics=_kg_reasoning_metrics(),
        main_chain_reconnection_metrics=_main_chain_reconnection_metrics(),
        field_validation_queue_alignment_metrics=_field_validation_alignment_metrics(),
        claim_specific_field_package_metrics=_claim_specific_field_package_metrics(),
        unified_field_evidence_gate_metrics=_unified_field_evidence_gate_metrics(),
        real_field_package_acceptance_metrics=_real_field_package_acceptance_metrics(),
        r7_pipeline_metrics=_r7_pipeline_metrics(),
        field_path_endpoint_label_preflight=_field_path_endpoint_label_preflight_blocked(),
        formal_search_execution_route_plan=_formal_search_execution_route_plan_ready(),
        external_activation_router=_external_activation_router_with_formal_handoff_ready(),
        observation_contract_metrics=_observation_contract_metrics(),
        control_replay_stress_metrics=_control_replay_stress_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])

    scorecard = report.metrics["governance_scorecard"]
    blocked_reasons = report.metrics["blocked_reasons"]

    assert scorecard["external_activation_router_handoff_ready_route_count"] == 1
    assert scorecard["external_activation_router_model_chain_ready_route_count"] == 0
    assert scorecard["external_activation_router_handoff_ready_channel_ids"] == [
        "R8U79_FORMAL_SEARCH_RESULT_PACKAGE"
    ]
    assert any(
        "FORMAL_SEARCH_RESULT_PACKAGE_PATH has passed source/row preflight" in reason
        for reason in blocked_reasons
    )
    assert not any(
        "FORMAL_SEARCH_RESULT_PACKAGE_PATH is still required before nonlegal comparison review" in reason
        for reason in blocked_reasons
    )
    core_gate = report.metrics["quantified_core_score_gate"]
    formal_action = {
        action["channel_id"]: action
        for action in core_gate["next_allowed_actions"]
        if action["action_type"] == "submit_external_evidence_package"
    }["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"]
    assert formal_action["current_handoff_ready"] is True
    assert formal_action["can_resume_model_chain"] is False


def test_governance_agent_consumes_formal_search_ai_nonlegal_review_brief() -> None:
    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=_agent48_ready_metrics(),
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        grey_box_physics_metrics=_grey_box_physics_metrics(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
        engineering_constraints_metrics=_engineering_constraints_metrics(),
        knowledge_graph_reasoning_metrics=_kg_reasoning_metrics(),
        main_chain_reconnection_metrics=_main_chain_reconnection_metrics(),
        field_validation_queue_alignment_metrics=_field_validation_alignment_metrics(),
        claim_specific_field_package_metrics=_claim_specific_field_package_metrics(),
        unified_field_evidence_gate_metrics=_unified_field_evidence_gate_metrics(),
        real_field_package_acceptance_metrics=_real_field_package_acceptance_metrics(),
        r7_pipeline_metrics=_r7_pipeline_metrics(),
        field_path_endpoint_label_preflight=_field_path_endpoint_label_preflight_blocked(),
        formal_search_execution_route_plan=_formal_search_execution_route_plan_ready(),
        formal_search_ai_nonlegal_review_brief=_formal_search_ai_nonlegal_review_brief_ready(),
        external_activation_router=_external_activation_router_with_formal_handoff_ready(),
        observation_contract_metrics=_observation_contract_metrics(),
        control_replay_stress_metrics=_control_replay_stress_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])

    scorecard = report.metrics["governance_scorecard"]
    blocked_reasons = report.metrics["blocked_reasons"]

    assert scorecard["formal_search_ai_nonlegal_review_brief_status"] == (
        "formal_search_ai_nonlegal_review_brief_ready_for_human_review"
    )
    assert scorecard["formal_search_ai_nonlegal_review_brief_row_count"] == 7
    assert scorecard["formal_search_ai_nonlegal_review_brief_missing_source_row_count"] == 0
    assert scorecard["formal_search_ai_nonlegal_review_brief_missing_claim_mapping_row_count"] == 0
    assert scorecard["formal_search_ai_nonlegal_review_brief_can_help_human_review"] is True
    assert scorecard["formal_search_ai_nonlegal_review_brief_can_route_to_claim_scope_patch_draft"] is False
    assert scorecard["formal_search_ai_nonlegal_review_brief_boundary_preserved"] is True
    assert "FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH" in scorecard[
        "formal_search_ai_nonlegal_review_brief_next_operator_action"
    ]
    assert any(
        "R8u134 formal search AI nonlegal review brief is ready" in reason
        and "FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH is required" in reason
        for reason in blocked_reasons
    )
    assert not any(
        "FORMAL_SEARCH_RESULT_PACKAGE_PATH has passed source/row preflight" in reason
        for reason in blocked_reasons
    )


def test_governance_agent_consumes_formal_search_nonlegal_review_operator_packet() -> None:
    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=_agent48_ready_metrics(),
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        grey_box_physics_metrics=_grey_box_physics_metrics(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
        engineering_constraints_metrics=_engineering_constraints_metrics(),
        knowledge_graph_reasoning_metrics=_kg_reasoning_metrics(),
        main_chain_reconnection_metrics=_main_chain_reconnection_metrics(),
        field_validation_queue_alignment_metrics=_field_validation_alignment_metrics(),
        claim_specific_field_package_metrics=_claim_specific_field_package_metrics(),
        unified_field_evidence_gate_metrics=_unified_field_evidence_gate_metrics(),
        real_field_package_acceptance_metrics=_real_field_package_acceptance_metrics(),
        r7_pipeline_metrics=_r7_pipeline_metrics(),
        field_path_endpoint_label_preflight=_field_path_endpoint_label_preflight_blocked(),
        formal_search_execution_route_plan=_formal_search_execution_route_plan_ready(),
        formal_search_ai_nonlegal_review_brief=_formal_search_ai_nonlegal_review_brief_ready(),
        formal_search_nonlegal_review_operator_packet=(
            _formal_search_nonlegal_review_operator_packet_ready()
        ),
        external_activation_router=_external_activation_router_with_formal_handoff_ready(),
        observation_contract_metrics=_observation_contract_metrics(),
        control_replay_stress_metrics=_control_replay_stress_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])

    scorecard = report.metrics["governance_scorecard"]
    blocked_reasons = report.metrics["blocked_reasons"]

    assert scorecard["formal_search_nonlegal_review_operator_packet_status"] == (
        "formal_search_nonlegal_review_operator_packet_ready_waiting_for_human_response"
    )
    assert (
        scorecard[
            "formal_search_nonlegal_review_operator_packet_expected_review_packet_row_count"
        ]
        == 7
    )
    assert (
        scorecard[
            "formal_search_nonlegal_review_operator_packet_high_priority_review_row_count"
        ]
        == 1
    )
    assert (
        scorecard[
            "formal_search_nonlegal_review_operator_packet_accepted_review_row_count"
        ]
        == 0
    )
    assert scorecard["formal_search_nonlegal_review_operator_packet_source_env_var"] == (
        "FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH"
    )
    assert (
        scorecard[
            "formal_search_nonlegal_review_operator_packet_can_route_to_claim_scope_patch_draft"
        ]
        is False
    )
    assert scorecard["formal_search_nonlegal_review_operator_packet_boundary_preserved"] is True
    assert "Agent60 source preflight" in scorecard[
        "formal_search_nonlegal_review_operator_packet_next_operator_action"
    ]
    assert any(
        "R8u136 formal search nonlegal review operator packet is ready" in reason
        and "7 human nonlegal review rows" in reason
        for reason in blocked_reasons
    )
    assert not any(
        "R8u134 formal search AI nonlegal review brief is ready" in reason
        for reason in blocked_reasons
    )
    core_gate = report.metrics["quantified_core_score_gate"]
    formal_action = {
        action["channel_id"]: action for action in core_gate["next_allowed_actions"]
    }["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"]
    resume_packet = core_gate["external_resume_conditions"][
        "formal_search_nonlegal_review_operator_packet"
    ]
    assert formal_action["formal_nonlegal_review_operator_packet_status"] == (
        "formal_search_nonlegal_review_operator_packet_ready_waiting_for_human_response"
    )
    assert formal_action["formal_nonlegal_review_operator_packet_ready"] is True
    assert (
        formal_action[
            "formal_nonlegal_review_operator_packet_expected_review_packet_row_count"
        ]
        == 7
    )
    assert formal_action["formal_nonlegal_review_operator_packet_source_env_var"] == (
        "FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH"
    )
    assert (
        formal_action[
            "formal_nonlegal_review_operator_packet_can_route_to_claim_scope_patch_draft"
        ]
        is False
    )
    assert formal_action["formal_nonlegal_review_operator_packet_can_resume_model_chain"] is False
    assert formal_action["formal_nonlegal_review_operator_packet_can_emit_claim_text"] is False
    assert formal_action["formal_nonlegal_review_operator_packet_can_write_to_actuator"] is False
    assert formal_action["formal_nonlegal_review_operator_packet_can_write_to_release_gate"] is False
    assert formal_action["current_handoff_ready"] is True
    assert formal_action["current_model_chain_resume_ready"] is False
    assert resume_packet["formal_nonlegal_review_operator_packet_ready"] is True
    assert resume_packet["formal_nonlegal_review_operator_packet_expected_review_packet_row_count"] == 7
    assert resume_packet["formal_nonlegal_review_operator_packet_can_write_to_release_gate"] is False


def test_governance_agent_surfaces_router_catalyst_patch_candidate_status() -> None:
    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=_agent48_ready_metrics(),
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        grey_box_physics_metrics=_grey_box_physics_metrics(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
        engineering_constraints_metrics=_engineering_constraints_metrics(),
        knowledge_graph_reasoning_metrics=_kg_reasoning_metrics(),
        main_chain_reconnection_metrics=_main_chain_reconnection_metrics(),
        field_validation_queue_alignment_metrics=_field_validation_alignment_metrics(),
        claim_specific_field_package_metrics=_claim_specific_field_package_metrics(),
        unified_field_evidence_gate_metrics=_unified_field_evidence_gate_metrics(),
        real_field_package_acceptance_metrics=_real_field_package_acceptance_metrics(),
        r7_pipeline_metrics=_r7_pipeline_metrics(),
        field_path_endpoint_label_preflight=_field_path_endpoint_label_preflight_blocked(),
        formal_search_execution_route_plan=_formal_search_execution_route_plan_ready(),
        external_activation_router=_external_activation_router_with_catalyst_patch_candidate(),
        observation_contract_metrics=_observation_contract_metrics(),
        control_replay_stress_metrics=_control_replay_stress_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])

    scorecard = report.metrics["governance_scorecard"]
    route_summary = {
        row["channel_id"]: row
        for row in scorecard["external_activation_router_route_summary"]
    }

    assert scorecard["external_activation_router_catalyst_patch_candidate_consumed"] is True
    assert scorecard["external_activation_router_catalyst_patch_candidate_status"] == (
        "catalyst_slice_r7_patch_candidate_ready_for_operator_submission"
    )
    assert scorecard["external_activation_router_catalyst_patch_candidate_materialized"] is True
    assert scorecard["external_activation_router_catalyst_patch_candidate_preflight_status"] == (
        "field_package_preflight_ready_for_agent42"
    )
    assert scorecard["external_activation_router_catalyst_patch_candidate_remaining_gap_count"] == 0
    assert (
        scorecard[
            "external_activation_router_catalyst_patch_candidate_can_submit_as_REAL_FIELD_REPLAY_PACKAGE_DIR"
        ]
        is True
    )
    assert scorecard["external_activation_router_next_operator_action"] == (
        "set_REAL_FIELD_REPLAY_PACKAGE_DIR_to_catalyst_patch_candidate"
    )
    assert route_summary["R7_REAL_FIELD_PACKAGE"]["route_ready"] is False
    assert route_summary["R7_REAL_FIELD_PACKAGE"]["catalyst_patch_candidate_status"] == (
        "catalyst_slice_r7_patch_candidate_ready_for_operator_submission"
    )
    assert (
        route_summary["R7_REAL_FIELD_PACKAGE"][
            "catalyst_patch_candidate_can_submit_as_REAL_FIELD_REPLAY_PACKAGE_DIR"
        ]
        is True
    )
    core_gate = report.metrics["quantified_core_score_gate"]
    assert (
        core_gate["external_resume_conditions"][
            "router_catalyst_patch_candidate_can_submit_as_REAL_FIELD_REPLAY_PACKAGE_DIR"
        ]
        is True
    )
    assert core_gate["external_resume_conditions"]["router_model_chain_ready_route_count"] == 0
    allowed_actions = {
        action["channel_id"]: action
        for action in core_gate["next_allowed_actions"]
        if action["action_type"] == "submit_external_evidence_package"
    }
    assert (
        allowed_actions["R7_REAL_FIELD_PACKAGE"][
            "router_catalyst_patch_candidate_can_submit_as_REAL_FIELD_REPLAY_PACKAGE_DIR"
        ]
        is True
    )
    assert allowed_actions["R7_REAL_FIELD_PACKAGE"]["current_model_chain_resume_ready"] is False


def test_governance_agent_surfaces_router_field_activation_upstream_gate() -> None:
    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=_agent48_ready_metrics(),
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        grey_box_physics_metrics=_grey_box_physics_metrics(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
        engineering_constraints_metrics=_engineering_constraints_metrics(),
        knowledge_graph_reasoning_metrics=_kg_reasoning_metrics(),
        main_chain_reconnection_metrics=_main_chain_reconnection_metrics(),
        field_validation_queue_alignment_metrics=_field_validation_alignment_metrics(),
        claim_specific_field_package_metrics=_claim_specific_field_package_metrics(),
        unified_field_evidence_gate_metrics=_unified_field_evidence_gate_metrics(),
        real_field_package_acceptance_metrics=_real_field_package_acceptance_metrics(),
        r7_pipeline_metrics=_r7_pipeline_metrics(),
        field_path_endpoint_label_preflight=_field_path_endpoint_label_preflight_blocked(),
        formal_search_execution_route_plan=_formal_search_execution_route_plan_ready(),
        external_activation_router=_external_activation_router_with_field_activation_upstream_gate(),
        observation_contract_metrics=_observation_contract_metrics(),
        control_replay_stress_metrics=_control_replay_stress_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])

    scorecard = report.metrics["governance_scorecard"]
    route_summary = {
        row["channel_id"]: row
        for row in scorecard["external_activation_router_route_summary"]
    }

    assert scorecard["external_activation_router_next_operator_action"] == (
        "fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH"
    )
    assert scorecard["external_activation_router_field_activation_upstream_consumed"] is True
    assert scorecard["external_activation_router_field_activation_upstream_status"] == (
        "field_activation_external_readiness_waiting_for_external_response"
    )
    assert scorecard["external_activation_router_field_activation_upstream_first_blocked_step"] == (
        "response_source"
    )
    assert scorecard["external_activation_router_field_activation_upstream_highest_priority_blocker"] == (
        "R8U106_SUBMIT_FIELD_ACTIVATION_RESPONSE"
    )
    assert (
        scorecard[
            "external_activation_router_field_activation_upstream_can_submit_to_external_activation_router"
        ]
        is False
    )
    assert route_summary["R7_REAL_FIELD_PACKAGE"]["route_status"] == (
        "activation_route_blocked_by_field_activation_upstream_gate"
    )
    assert route_summary["R7_REAL_FIELD_PACKAGE"]["preflight_status"] == (
        "field_activation_external_readiness_waiting_for_external_response"
    )
    assert route_summary["R7_REAL_FIELD_PACKAGE"]["field_activation_upstream_next_operator_action"] == (
        "fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH"
    )
    core_gate = report.metrics["quantified_core_score_gate"]
    assert core_gate["external_resume_conditions"]["router_next_operator_action"] == (
        "fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH"
    )
    assert core_gate["external_resume_conditions"]["router_field_activation_upstream_status"] == (
        "field_activation_external_readiness_waiting_for_external_response"
    )
    allowed_actions = {
        action["channel_id"]: action
        for action in core_gate["next_allowed_actions"]
        if action["action_type"] == "submit_external_evidence_package"
    }
    assert allowed_actions["R7_REAL_FIELD_PACKAGE"]["router_operator_action"] == (
        "fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH"
    )
    assert allowed_actions["R7_REAL_FIELD_PACKAGE"]["router_field_activation_upstream_status"] == (
        "field_activation_external_readiness_waiting_for_external_response"
    )
    assert allowed_actions["R7_REAL_FIELD_PACKAGE"]["current_model_chain_resume_ready"] is False


def test_governance_agent_prioritizes_submitted_field_route_preflight_blocker() -> None:
    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=_agent48_ready_metrics(),
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        grey_box_physics_metrics=_grey_box_physics_metrics(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
        engineering_constraints_metrics=_engineering_constraints_metrics(),
        knowledge_graph_reasoning_metrics=_kg_reasoning_metrics(),
        main_chain_reconnection_metrics=_main_chain_reconnection_metrics(),
        field_validation_queue_alignment_metrics=_field_validation_alignment_metrics(),
        claim_specific_field_package_metrics=_claim_specific_field_package_metrics(),
        unified_field_evidence_gate_metrics=_unified_field_evidence_gate_metrics(),
        real_field_package_acceptance_metrics=_real_field_package_acceptance_metrics(),
        r7_pipeline_metrics=_r7_pipeline_metrics(),
        field_path_endpoint_label_preflight=_field_path_endpoint_label_preflight_blocked(),
        formal_search_execution_route_plan=_formal_search_execution_route_plan_ready(),
        external_activation_router=_external_activation_router_field_preflight_blocked(),
        observation_contract_metrics=_observation_contract_metrics(),
        control_replay_stress_metrics=_control_replay_stress_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])

    scorecard = report.metrics["governance_scorecard"]
    route_summary = {
        row["channel_id"]: row
        for row in scorecard["external_activation_router_route_summary"]
    }

    assert scorecard["external_activation_router_path_supplied_count"] == 1
    assert scorecard["external_activation_router_highest_priority_blocker"] == (
        "R7_REAL_FIELD_PACKAGE:field_package_preflight_not_ready:"
        "field_package_template_ready_needs_real_values_and_rows"
    )
    assert scorecard["external_activation_router_next_operator_action"] == (
        "Replace placeholder metadata fields: site_id, campaign_id."
    )
    assert route_summary["R7_REAL_FIELD_PACKAGE"]["preflight_status"] == (
        "field_package_template_ready_needs_real_values_and_rows"
    )
    core_gate = report.metrics["quantified_core_score_gate"]
    assert core_gate["external_resume_conditions"]["router_highest_priority_blocker"] == (
        "R7_REAL_FIELD_PACKAGE:field_package_preflight_not_ready:"
        "field_package_template_ready_needs_real_values_and_rows"
    )
    allowed_actions = {
        action["channel_id"]: action
        for action in core_gate["next_allowed_actions"]
        if action["action_type"] == "submit_external_evidence_package"
    }
    assert allowed_actions["R7_REAL_FIELD_PACKAGE"]["router_preflight_status"] == (
        "field_package_template_ready_needs_real_values_and_rows"
    )
    assert route_summary["R7_REAL_FIELD_PACKAGE"]["path_supplied"] is True


def test_governance_agent_external_activation_contract_routes_field_and_path_when_ready() -> None:
    report = ModelCoreOptimizationGovernanceAgent(
        agent48_metrics=_agent48_ready_metrics(),
        agent49_metrics=_agent49_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        grey_box_physics_metrics=_grey_box_physics_metrics(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
        engineering_constraints_metrics=_engineering_constraints_metrics(),
        knowledge_graph_reasoning_metrics=_kg_reasoning_metrics(),
        main_chain_reconnection_metrics=_main_chain_reconnection_metrics(),
        field_validation_queue_alignment_metrics=_field_validation_alignment_metrics(),
        claim_specific_field_package_metrics=_claim_specific_field_package_metrics(),
        unified_field_evidence_gate_metrics=_unified_field_evidence_gate_metrics(),
        real_field_package_acceptance_metrics=_real_field_package_acceptance_metrics(),
        r7_pipeline_metrics=_r7_pipeline_metrics(smoke_pass=True, human_review_candidate=True),
        field_path_endpoint_label_preflight=_field_path_endpoint_label_preflight_ready(),
        formal_search_execution_route_plan=_formal_search_execution_route_plan_ready(),
        observation_contract_metrics=_observation_contract_metrics(),
        control_replay_stress_metrics=_control_replay_stress_metrics(),
        external_evidence_matrix=_evidence_matrix(),
    ).run([])

    contract = report.metrics["external_activation_contract"]
    channels = {channel["channel_id"]: channel for channel in contract["channels"]}
    no_write = report.metrics["quantified_core_score_gate"]["no_write_boundaries"]

    assert contract["contract_status"] == "external_evidence_activation_ready"
    assert contract["activation_ready"] is True
    assert contract["ready_channel_count"] == 2
    assert contract["blocked_channel_count"] == 1
    assert channels["R7_REAL_FIELD_PACKAGE"]["can_resume_model_chain"] is True
    assert channels["R8U66_PATH_ENDPOINT_LABEL_PACKAGE"]["can_resume_model_chain"] is True
    assert channels["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"]["can_resume_model_chain"] is False
    assert channels["R7_REAL_FIELD_PACKAGE"]["resumes_to"][0] == "Agent44 field import preflight"
    assert no_write["can_write_to_actuator"] is False
    assert no_write["can_write_to_release_gate"] is False


def _agent48_metrics() -> dict[str, object]:
    return {
        "coverage": {
            "weak_state_coverage": 0.300,
            "catalyst_activity_observability": 0.300,
            "soft_sensor_reconstruction_gain": 0.827,
            "matrix_interference_observability": 0.851,
            "total_cost_index": 4.176,
        },
        "readiness": {
            "sparse_placement_status": "sparse_sensor_layout_ready_needs_field_topology",
            "can_update_soft_sensor_design_prior": True,
            "can_finalize_field_deployment": False,
        },
    }


def _agent48_ready_metrics() -> dict[str, object]:
    metrics = _agent48_metrics()
    metrics["algorithm_comparison"] = [
        {"strategy_id": "greedy_marginal"},
        {"strategy_id": "reconstruction_qr_proxy"},
        {"strategy_id": "classification_sspoc_proxy"},
        {"strategy_id": "topology_robust_cost_proxy"},
    ]
    metrics["selected_strategy"] = {"strategy_id": "greedy_marginal"}
    return metrics


def _agent48_ready_metrics_with_hidden_state_ledger() -> dict[str, object]:
    metrics = _agent48_ready_metrics()
    metrics["hidden_state_requirement_ledger"] = {
        "ledger_status": "hidden_state_requirement_ledger_ready_with_gaps",
        "state_rows": [
            {
                "hidden_state": "pollutant_residual",
                "min_primary_axis_score": 0.814,
                "ready_for_soft_sensor_estimation": True,
                "ready_for_control_use": False,
                "missing_required_zones": ["effluent"],
                "missing_required_modalities": [],
                "field_evidence_needed": ["influent_effluent_lab_pollutant_residual"],
                "candidate_patch": {"patch_status": "state_target_already_met"},
            },
            {
                "hidden_state": "reaction_completion",
                "min_primary_axis_score": 0.712,
                "ready_for_soft_sensor_estimation": True,
                "ready_for_control_use": False,
                "missing_required_zones": [],
                "missing_required_modalities": ["pH"],
                "field_evidence_needed": ["reaction_completion_lab_or_kinetic_label"],
                "candidate_patch": {"patch_status": "state_target_already_met"},
            },
            {
                "hidden_state": "catalyst_activity",
                "min_primary_axis_score": 0.300,
                "ready_for_soft_sensor_estimation": False,
                "ready_for_control_use": False,
                "missing_required_zones": [],
                "missing_required_modalities": ["pressure_drop_kPa"],
                "field_evidence_needed": ["catalyst_activity_label", "regeneration_history"],
                "candidate_patch": {"patch_status": "candidate_pool_patch_incomplete"},
            },
            {
                "hidden_state": "matrix_interference",
                "min_primary_axis_score": 0.587,
                "ready_for_soft_sensor_estimation": False,
                "ready_for_control_use": False,
                "missing_required_zones": [],
                "missing_required_modalities": ["temperature_C", "EC_uScm"],
                "field_evidence_needed": ["matrix_spike_or_inhibition_label"],
                "candidate_patch": {"patch_status": "candidate_pool_patch_available"},
            },
            {
                "hidden_state": "hydraulic_delay",
                "min_primary_axis_score": 0.760,
                "ready_for_soft_sensor_estimation": True,
                "ready_for_control_use": False,
                "missing_required_zones": [],
                "missing_required_modalities": ["pressure_drop_kPa"],
                "field_evidence_needed": ["tracer_or_residence_time_distribution"],
                "candidate_patch": {"patch_status": "state_target_already_met"},
            },
            {
                "hidden_state": "release_or_byproduct_risk",
                "min_primary_axis_score": 0.712,
                "ready_for_soft_sensor_estimation": True,
                "ready_for_control_use": False,
                "missing_required_zones": ["effluent"],
                "missing_required_modalities": ["pH"],
                "field_evidence_needed": ["byproduct_or_release_lab_label"],
                "candidate_patch": {"patch_status": "state_target_already_met"},
            },
        ],
    }
    return metrics


def _agent49_metrics() -> dict[str, object]:
    return {
        "readiness": {
            "coordination_status": "synthetic_collaborative_policy_needs_field_replay",
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        },
        "decision_tree_distillation": {
            "distilled_policy_accuracy_proxy": 0.794,
            "minimum_required_accuracy": 0.9,
        },
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
            "can_relax_agent49_catalyst_uncertainty_block": False,
        },
    }


def _replay_evaluation_metrics() -> dict[str, object]:
    return {
        "offline_evaluation_metrics": {
            "replay_case_count": 6,
            "joint_action_accuracy": 0.667,
            "mean_reward_regret": 0.052,
            "field_replay_coverage": 0.0,
        },
        "readiness": {
            "replay_evaluation_status": "synthetic_replay_evaluation_ready_needs_field_replay",
            "synthetic_replay_ready": True,
            "field_ready": False,
            "can_write_to_actuator": False,
        },
    }


def _grey_box_physics_metrics() -> dict[str, object]:
    return {
        "readiness": {
            "grey_box_physics_status": "synthetic_grey_box_physics_prior_ready_needs_field_calibration",
            "synthetic_prior_ready": True,
            "field_ready": False,
            "mean_grey_box_residual": 0.092,
            "max_mass_balance_residual": 0.041,
        }
    }


def _soft_sensor_matrix_metrics() -> dict[str, object]:
    return {
        "readiness": {
            "soft_sensor_matrix_status": "synthetic_layout_aware_soft_sensor_contract_ready_needs_field_missingness",
            "can_update_soft_sensor_training_schema": True,
            "field_ready": False,
            "missingness_robustness_score": 0.536,
        }
    }


def _engineering_constraints_metrics() -> dict[str, object]:
    return {
        "readiness": {
            "engineering_constraints_status": "synthetic_engineering_constraints_reward_patch_ready_needs_plc_scada_and_field_replay",
            "can_update_agent49_reward_contract": True,
            "field_ready": False,
            "mean_execution_feasibility": 0.812,
            "can_write_to_actuator": False,
        }
    }


def _kg_reasoning_metrics() -> dict[str, object]:
    return {
        "readiness": {
            "kg_reasoning_status": "kg_reasoning_patch_ready_needs_field_supported_edges",
            "can_update_mechanism_evidence": True,
            "can_update_action_bias_prior": True,
            "field_supported_edge_ratio": 0.0,
            "evidence_traceability": 1.0,
            "constraint_hit_rate": 1.0,
        }
    }


def _main_chain_reconnection_metrics() -> dict[str, object]:
    return {
        "readiness": {
            "main_chain_reconnection_status": "synthetic_main_chain_reconnection_ready_needs_field_replay",
            "can_update_agent50_priority": True,
            "main_chain_prior_consumption_rate": 1.0,
        }
    }


def _field_validation_alignment_metrics() -> dict[str, object]:
    return {
        "readiness": {
            "field_validation_alignment_status": "field_validation_alignment_ready_needs_real_field_package",
            "field_need_to_table_coverage": 1.0,
            "field_need_to_gate_coverage": 1.0,
            "can_update_agent50_priority": True,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        }
    }


def _claim_specific_field_package_metrics() -> dict[str, object]:
    return {
        "readiness": {
            "claim_specific_package_status": "claim_specific_package_ready_needs_real_data_and_source_basis_detail",
            "claim_specific_required_field_coverage": 1.0,
            "source_basis_completion_rate": 0.45,
            "can_update_agent50_priority": True,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        }
    }


def _unified_field_evidence_gate_metrics() -> dict[str, object]:
    return {
        "readiness": {
            "unified_field_evidence_gate_status": "unified_gate_ready_blocking_field_claim_upgrade",
            "source_basis_completion_rate": 1.0,
            "citation_detail_completion_rate": 1.0,
            "source_basis_parameter_boundary_coverage": 1.0,
            "field_import_pass": False,
            "field_replay_evidence_chain_pass": False,
            "soft_sensor_field_holdout_gate_pass": False,
            "can_emit_field_claim_upgrade": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        },
        "claim_basis_promotion_gate": {
            "gate_status": "claim_basis_promotion_blocked_until_field_validation",
            "promotion_decision_count": 5,
            "ready_promotion_count": 0,
            "blocked_promotion_count": 5,
            "can_emit_field_claim_upgrade": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        },
        "next_refactor_action": {
            "action_id": "R2_agent48_51_54_observation_contract_merge",
            "title": "合并稀疏布点、催化剂代理与软传感观测矩阵合同",
            "reason": "field evidence gate 已统一且 source_basis 细节已补齐",
            "must_not_do": "不能把 literature traceability 当作 field validation",
        },
    }


def _real_field_package_acceptance_metrics() -> dict[str, object]:
    return {
        "readiness": {
            "real_field_package_acceptance_status": "real_field_package_acceptance_blocked_at_import",
            "field_package_import_pass": False,
            "field_replay_evidence_chain_pass": False,
            "soft_sensor_field_holdout_gate_pass": False,
            "can_emit_field_supported_claim_candidate": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        }
    }


def _r7_pipeline_metrics(
    *,
    status: str = "field_evidence_sufficiency_blocked_before_import",
    smoke_pass: bool = False,
    human_review_candidate: bool = False,
) -> dict[str, object]:
    return {
        "pipeline_readiness": {
            "r7_status": "real_field_package_acceptance_blocked_at_import",
            "field_evidence_sufficiency_status": status,
            "field_evidence_sufficiency_score": 0.26 if not smoke_pass else 0.9,
            "field_evidence_smoke_pass": smoke_pass,
            "field_evidence_calibration_volume_pass": human_review_candidate,
            "can_route_to_agent42_smoke_replay": smoke_pass,
            "can_route_to_field_holdout": smoke_pass,
            "can_route_to_human_review_candidate": human_review_candidate,
            "field_package_submission_readiness_status": (
                "field_package_submission_smoke_ready_needs_path_endpoint_alignment_for_layout_holdout"
                if smoke_pass
                else "field_package_submission_blocked_at_import_preflight"
            ),
            "field_package_submission_highest_priority_blocker": (
                "R8U66_PATH_ENDPOINT_ALIGNMENT" if smoke_pass else "R7A_IMPORT_PREFLIGHT"
            ),
            "field_package_submission_next_operator_action": (
                "collect_path_endpoint_same_batch_rows_for_layout_holdout"
                if smoke_pass
                else "repair_metadata_headers_and_real_rows_before_agent42"
            ),
            "field_package_submission_blocking_stage_count": 2 if smoke_pass else 5,
            "field_package_submission_repair_work_order_status": (
                "field_package_submission_repair_work_order_requires_path_endpoint_alignment"
                if smoke_pass
                else "field_package_submission_repair_work_order_blocked_at_import_preflight"
            ),
            "field_package_submission_repair_item_count": 2 if smoke_pass else 13,
            "field_package_submission_repair_response_preflight_status": (
                "repair_response_preflight_ready_for_r7_preflight"
                if smoke_pass
                else "repair_response_preflight_blocked_at_template_markers"
            ),
            "field_package_submission_repair_response_can_route_to_r7_preflight": smoke_pass,
            "field_supported_claim_upgrade_ready": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        }
    }


def _field_path_endpoint_label_preflight_blocked() -> dict[str, object]:
    required_tables = [
        "site_topology_or_bed_geometry",
        "node_modality_sensor_timeseries",
        "hydraulic_path_stage_labels",
        "final_effluent_endpoint_labels",
        "campaign_operation_log",
        "offline_lab_results",
    ]
    return {
        "preflight_status": "no_field_path_endpoint_label_package_supplied",
        "required_tables": required_tables,
        "missing_tables": list(required_tables),
        "matched_batch_count": 0,
        "required_matched_batch_deficit": 5,
        "batch_alignment_gap_count": 0,
        "alignment_patch_plan": {
            "patch_plan_status": "field_path_endpoint_alignment_blocked_by_preflight",
            "item_count": 7,
        },
        "can_route_to_field_layout_holdout": False,
        "next_operator_action": "submit_field_path_endpoint_label_package_rows",
        "field_boundary": "contract only; no real path/endpoint package rows have been supplied",
    }


def _field_path_endpoint_label_preflight_ready() -> dict[str, object]:
    return {
        "preflight_status": "field_path_endpoint_label_package_ready_for_layout_holdout",
        "required_tables": [
            "site_topology_or_bed_geometry",
            "node_modality_sensor_timeseries",
            "hydraulic_path_stage_labels",
            "final_effluent_endpoint_labels",
            "campaign_operation_log",
            "offline_lab_results",
        ],
        "missing_tables": [],
        "empty_tables": [],
        "invalid_table_shapes": [],
        "template_marker_count": 0,
        "required_field_gap_count": 0,
        "matched_batch_count": 5,
        "required_matched_batch_deficit": 0,
        "batch_alignment_gap_count": 0,
        "alignment_patch_plan": {
            "patch_plan_status": "field_path_endpoint_alignment_ready",
            "item_count": 0,
        },
        "accepted_batch_ids": ["B001", "B002", "B003", "B004", "B005"],
        "can_route_to_field_layout_holdout": True,
        "next_operator_action": "route_to_field_layout_holdout_review",
        "field_boundary": "field path/endpoint rows are accepted for layout holdout; release write remains blocked",
    }


def _external_activation_router_waiting() -> dict[str, object]:
    return {
        "router_id": "R8u82_external_activation_router",
        "source_contract_id": "R8u81_external_evidence_activation_contract",
        "router_status": "external_activation_router_waiting_for_external_paths",
        "path_supplied_count": 0,
        "route_ready_count": 0,
        "model_chain_ready_route_count": 0,
        "handoff_ready_route_count": 0,
        "blocked_route_count": 3,
        "ready_channel_ids": [],
        "model_chain_ready_channel_ids": [],
        "handoff_ready_channel_ids": [],
        "blocked_channel_ids": [
            "R7_REAL_FIELD_PACKAGE",
            "R8U66_PATH_ENDPOINT_LABEL_PACKAGE",
            "R8U79_FORMAL_SEARCH_RESULT_PACKAGE",
        ],
        "priority_route_channel_id": "R7_REAL_FIELD_PACKAGE",
        "priority_route_status": "activation_route_waiting_for_env_var",
        "priority_route_ready": False,
        "priority_route_can_resume_model_chain": False,
        "priority_route_preflight_status": "-",
        "highest_priority_blocker": "R7_REAL_FIELD_PACKAGE:REAL_FIELD_REPLAY_PACKAGE_DIR:not_set",
        "next_operator_action": "set_REAL_FIELD_REPLAY_PACKAGE_DIR",
        "router_validation_command": ".venv/bin/python experiments/run_external_activation_router.py",
        "priority_route_command": "",
        "boundary_preserved": True,
        "global_no_write_boundary": (
            "This router only prepares preflight/execution routes. It never writes actuator policy, "
            "release-gate clearance, patent/legal conclusions or field-supported claims."
        ),
        "route_rows": [
            {
                "channel_id": "R7_REAL_FIELD_PACKAGE",
                "route_status": "activation_route_waiting_for_env_var",
                "path_supplied": False,
                "route_ready": False,
                "blocked_reason": "REAL_FIELD_REPLAY_PACKAGE_DIR:not_set",
                "operator_action": "set_REAL_FIELD_REPLAY_PACKAGE_DIR",
            },
            {
                "channel_id": "R8U66_PATH_ENDPOINT_LABEL_PACKAGE",
                "route_status": "activation_route_waiting_for_env_var",
                "path_supplied": False,
                "route_ready": False,
                "blocked_reason": "FIELD_PATH_ENDPOINT_LABEL_PACKAGE_DIR:not_set",
                "operator_action": "set_FIELD_PATH_ENDPOINT_LABEL_PACKAGE_DIR",
            },
            {
                "channel_id": "R8U79_FORMAL_SEARCH_RESULT_PACKAGE",
                "route_status": "activation_route_waiting_for_env_var",
                "path_supplied": False,
                "route_ready": False,
                "blocked_reason": "FORMAL_SEARCH_RESULT_PACKAGE_PATH:not_set",
                "operator_action": "set_FORMAL_SEARCH_RESULT_PACKAGE_PATH",
            },
        ],
    }


def _external_activation_router_with_formal_handoff_ready() -> dict[str, object]:
    router = _external_activation_router_waiting()
    router.update(
        {
            "router_status": "external_activation_router_has_handoff_ready_routes",
            "path_supplied_count": 1,
            "route_ready_count": 1,
            "model_chain_ready_route_count": 0,
            "handoff_ready_route_count": 1,
            "blocked_route_count": 2,
            "ready_channel_ids": ["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"],
            "model_chain_ready_channel_ids": [],
            "handoff_ready_channel_ids": ["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"],
            "blocked_channel_ids": [
                "R7_REAL_FIELD_PACKAGE",
                "R8U66_PATH_ENDPOINT_LABEL_PACKAGE",
            ],
            "priority_route_channel_id": "R8U79_FORMAL_SEARCH_RESULT_PACKAGE",
            "priority_route_status": "activation_route_ready_for_agent60_formal_search_preflight",
            "priority_route_ready": True,
            "priority_route_can_resume_model_chain": False,
            "priority_route_preflight_status": (
                "formal_search_result_package_row_preflight_ready_for_validation_gate"
            ),
            "highest_priority_blocker": "",
            "next_operator_action": "run_preflight_or_pipeline_command",
        }
    )
    router["route_rows"][2].update(
        {
            "route_status": "activation_route_ready_for_agent60_formal_search_preflight",
            "path_supplied": True,
            "route_ready": True,
            "can_resume_model_chain": False,
            "blocked_reason": "",
            "operator_action": "run_preflight_or_pipeline_command",
            "formal_search_result_package_row_preflight": {
                "formal_search_result_package_row_preflight_status": (
                    "formal_search_result_package_row_preflight_ready_for_validation_gate"
                )
            },
            "formal_search_result_validation_execution": {
                "formal_search_result_validation_execution_status": (
                    "formal_search_result_validation_execution_ready_for_human_nonlegal_comparison_review"
                ),
                "can_enter_human_nonlegal_comparison_review": True,
                "can_generate_prior_art_result": False,
                "legal_opinion_allowed": False,
                "field_claim_upgrade_allowed": False,
            },
        }
    )
    return router


def _external_activation_router_with_catalyst_patch_candidate() -> dict[str, object]:
    router = _external_activation_router_waiting()
    candidate = {
        "consumed": True,
        "patch_status": "catalyst_slice_r7_patch_candidate_ready_for_operator_submission",
        "candidate_materialized": True,
        "candidate_preflight_status": "field_package_preflight_ready_for_agent42",
        "remaining_gap_count": 0,
        "can_submit_candidate_as_REAL_FIELD_REPLAY_PACKAGE_DIR": True,
        "can_route_to_agent51_field_proxy_holdout": True,
        "candidate_package_dir": "/tmp/r7_patch_candidate_package",
        "source_slice_path": "/tmp/catalyst_slice",
        "next_operator_action": "set_REAL_FIELD_REPLAY_PACKAGE_DIR_to_candidate_package",
        "candidate_submission_boundary": (
            "Candidate remains blocked until REAL_FIELD_REPLAY_PACKAGE_DIR is set "
            "and full R7 field preflight passes."
        ),
    }
    router.update(
        {
            "catalyst_patch_candidate_consumed": True,
            "catalyst_patch_candidate_status": candidate["patch_status"],
            "catalyst_patch_candidate_materialized": True,
            "catalyst_patch_candidate_preflight_status": candidate["candidate_preflight_status"],
            "catalyst_patch_candidate_remaining_gap_count": 0,
            "catalyst_patch_candidate_can_submit_as_REAL_FIELD_REPLAY_PACKAGE_DIR": True,
            "catalyst_patch_candidate_package_dir": candidate["candidate_package_dir"],
            "next_operator_action": "set_REAL_FIELD_REPLAY_PACKAGE_DIR_to_catalyst_patch_candidate",
        }
    )
    router["route_rows"][0]["operator_action"] = (
        "set_REAL_FIELD_REPLAY_PACKAGE_DIR_to_catalyst_patch_candidate"
    )
    router["route_rows"][0]["catalyst_slice_r7_patch_candidate"] = candidate
    return router


def _external_activation_router_with_field_activation_upstream_gate() -> dict[str, object]:
    router = _external_activation_router_waiting()
    upstream = {
        "consumed": True,
        "status": "field_activation_external_readiness_waiting_for_external_response",
        "submission_packet_status": "field_activation_response_submission_packet_waiting_for_external_response",
        "can_submit_to_external_activation_router": False,
        "first_blocked_step": "response_source",
        "highest_priority_blocker": "R8U106_SUBMIT_FIELD_ACTIVATION_RESPONSE",
        "next_operator_action": "fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH",
        "no_write_boundary": "Field activation upstream gate does not create field evidence.",
        "upstream_gate_boundary": (
            "This upstream gate orders field-activation preflights and cannot write actuator or release outputs."
        ),
    }
    router.update(
        {
            "priority_route_status": "activation_route_blocked_by_field_activation_upstream_gate",
            "priority_route_preflight_status": upstream["status"],
            "highest_priority_blocker": (
                "R7_REAL_FIELD_PACKAGE:field_activation_upstream_not_ready:"
                "R8U106_SUBMIT_FIELD_ACTIVATION_RESPONSE:"
                "field_activation_external_readiness_waiting_for_external_response"
            ),
            "next_operator_action": "fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH",
            "field_activation_upstream_consumed": True,
            "field_activation_upstream_status": upstream["status"],
            "field_activation_upstream_first_blocked_step": "response_source",
            "field_activation_upstream_highest_priority_blocker": (
                "R8U106_SUBMIT_FIELD_ACTIVATION_RESPONSE"
            ),
            "field_activation_upstream_next_operator_action": (
                "fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH"
            ),
            "field_activation_upstream_can_submit_to_external_activation_router": False,
            "field_activation_upstream_submission_packet_status": upstream[
                "submission_packet_status"
            ],
        }
    )
    router["route_rows"][0].update(
        {
            "route_status": "activation_route_blocked_by_field_activation_upstream_gate",
            "blocked_reason": (
                "field_activation_upstream_not_ready:"
                "R8U106_SUBMIT_FIELD_ACTIVATION_RESPONSE"
            ),
            "operator_action": "fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH",
            "field_activation_upstream_gate": upstream,
        }
    )
    return router


def _external_activation_router_field_preflight_blocked() -> dict[str, object]:
    router = _external_activation_router_waiting()
    router["router_status"] = "external_activation_router_waiting_for_external_paths"
    router["path_supplied_count"] = 1
    router["priority_route_status"] = "activation_route_blocked_by_field_package_preflight"
    router["priority_route_preflight_status"] = "field_package_template_ready_needs_real_values_and_rows"
    router["highest_priority_blocker"] = (
        "R7_REAL_FIELD_PACKAGE:field_package_preflight_not_ready:"
        "field_package_template_ready_needs_real_values_and_rows"
    )
    router["next_operator_action"] = "Replace placeholder metadata fields: site_id, campaign_id."
    router["route_rows"][0] = {
        "channel_id": "R7_REAL_FIELD_PACKAGE",
        "route_status": "activation_route_blocked_by_field_package_preflight",
        "package_pointer": "REAL_FIELD_REPLAY_PACKAGE_DIR",
        "path_supplied": True,
        "submitted_path": "/tmp/bad_field_package",
        "route_ready": False,
        "can_resume_model_chain": False,
        "blocked_reason": "field_package_preflight_not_ready",
        "operator_action": "Replace placeholder metadata fields: site_id, campaign_id.",
        "field_package_preflight": {
            "status": "field_package_template_ready_needs_real_values_and_rows",
            "placeholder_metadata_fields": ["site_id", "campaign_id"],
            "real_rows_ready": False,
            "can_pass_to_timestamped_replay": False,
        },
    }
    return router


def _formal_search_execution_route_plan_ready() -> dict[str, object]:
    return {
        "route_plan_status": (
            "formal_search_execution_route_plan_ready_waiting_for_external_search_execution"
        ),
        "route_row_count": 7,
        "complete_route_row_count": 7,
        "mapped_seed_route_count": 7,
        "operator_first_action": (
            "execute_external_or_human_search_and_submit_FORMAL_SEARCH_RESULT_PACKAGE_PATH"
        ),
        "can_submit_synthetic_or_template_result_package": False,
        "can_generate_prior_art_result": False,
        "legal_opinion_allowed": False,
        "can_emit_claim_text": False,
        "field_claim_upgrade_allowed": False,
    }


def _formal_search_ai_nonlegal_review_brief_ready() -> dict[str, object]:
    return {
        "brief_metadata": {
            "brief_id": "R8u134_formal_search_ai_nonlegal_review_brief",
            "brief_status": "formal_search_ai_nonlegal_review_brief_ready_for_human_review",
            "brief_role": "ai_assisted_pre_review_not_human_review",
        },
        "review_readiness": {
            "review_packet_row_count": 7,
            "brief_row_count": 7,
            "missing_source_row_count": 0,
            "missing_claim_mapping_row_count": 0,
            "can_help_human_nonlegal_review": True,
            "can_route_to_claim_scope_patch_draft": False,
            "human_review_completed": False,
            "can_generate_prior_art_result": False,
            "legal_opinion_allowed": False,
            "field_claim_upgrade_allowed": False,
        },
        "operator_next_action": {
            "expected_env_var": "FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH",
            "next_operator_action": (
                "complete human nonlegal review response and submit "
                "FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH"
            ),
        },
        "boundary": {
            "can_emit_claim_text": False,
            "can_resume_model_chain": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        },
    }


def _formal_search_nonlegal_review_operator_packet_ready() -> dict[str, object]:
    return {
        "operator_packet_metadata": {
            "packet_id": "R8u136_formal_search_nonlegal_review_operator_packet",
            "packet_status": (
                "formal_search_nonlegal_review_operator_packet_ready_waiting_for_human_response"
            ),
            "linked_ai_brief_status": (
                "formal_search_ai_nonlegal_review_brief_ready_for_human_review"
            ),
        },
        "operator_action": {
            "source_env_var": "FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH",
            "expected_review_packet_row_count": 7,
            "accepted_review_row_count": 0,
            "rejected_review_row_count": 0,
            "high_priority_review_row_count": 1,
            "next_operator_action": (
                "complete a human nonlegal review response at "
                "outputs/agent_architecture_consolidation/"
                "formal_search_nonlegal_review_response.json, set "
                "FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH, then run Agent60 source preflight"
            ),
        },
        "downstream_state": {
            "review_response_supplied": False,
            "human_review_completed": False,
            "can_route_to_claim_scope_patch_draft": False,
            "claim_scope_patch_draft_status": (
                "formal_search_claim_scope_patch_draft_blocked_at_nonlegal_review_response"
            ),
        },
        "boundary": {
            "can_generate_prior_art_result": False,
            "legal_opinion_allowed": False,
            "field_claim_upgrade_allowed": False,
            "can_emit_claim_text": False,
            "can_resume_model_chain": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "can_route_to_claim_scope_patch_draft_without_human_response": False,
        },
    }


def _observation_contract_metrics() -> dict[str, object]:
    return {
        "readiness": {
            "observation_contract_status": "synthetic_observation_contract_ready_needs_field_topology_proxy_labels_and_missingness",
            "proxy_enhanced_weak_state_coverage": 0.58,
            "missingness_robustness_after_patch": 0.727,
            "can_update_agent48_design_prior": True,
            "can_update_agent54_observation_contract": True,
            "can_relax_agent49_catalyst_uncertainty_block": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        },
        "next_refactor_action": {
            "action_id": "R3_agent49_replay_counterfactual_stress",
            "title": "对 Agent49/52 做协同控制 replay 反事实压力测试",
            "reason": "观测契约已把 weak_state_coverage 推过 0.55 的设计门槛",
            "must_not_do": "不能训练黑箱 MARL 或写执行器",
        },
    }


def _control_replay_stress_metrics() -> dict[str, object]:
    return {
        "readiness": {
            "control_replay_stress_status": "synthetic_counterfactual_stress_ready_needs_field_replay",
            "stress_ready": True,
            "field_ready": False,
            "can_update_agent49_reward_prior": True,
            "can_update_agent52_stress_suite": True,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        },
        "next_refactor_action": {
            "action_id": "R3b_agent49_reward_prior_patch_from_counterfactual_stress",
            "title": "把 R3 反事实压力结果写成 Agent49 reward prior guardrails",
            "reason": "R3 stress 已暴露并修复 synthetic 高 regret/误保护场景",
            "must_not_do": "不能把 synthetic stress improvement 当作现场控制有效性",
        },
    }


def _field_activation_matrix_metrics() -> dict[str, object]:
    return {
        "interface_id": "R8u97_field_activation_matrix_interface",
        "readiness": {
            "interface_status": "field_activation_matrix_ready_for_state_level_external_collection",
            "hidden_state_row_count": 6,
            "can_resume_model_chain": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "no_write_boundary_completeness": 1.0,
            "next_gate": "submit_external_evidence_packages_or_run_router_preflight",
        },
        "field_activation_response_preflight": {
            "preflight_status": "field_activation_response_blocked_before_external_package_preflight",
            "expected_response_row_count": 33,
            "template_marker_row_count": 33,
            "missing_value_payload_row_count": 0,
            "template_value_payload_row_count": 33,
            "can_route_to_external_activation_router": False,
        },
        "field_activation_response_completion_ledger": {
            "ledger_status": "field_activation_response_completion_waiting_for_external_response",
            "expected_response_row_count": 33,
            "completed_response_row_count": 0,
            "incomplete_response_row_count": 33,
            "completion_ratio": 0.0,
            "next_hidden_state_focus": "catalyst_activity",
            "next_operator_action": "copy_template_fill_real_field_values_and_set_FIELD_ACTIVATION_RESPONSE_PATH",
            "can_route_to_package_assembly": False,
            "can_resume_model_chain": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        },
        "field_activation_response_focus_handoff": {
            "handoff_status": "field_activation_response_focus_handoff_ready_for_catalyst_activity",
            "target_hidden_state": "catalyst_activity",
            "focused_response_row_count": 6,
            "full_response_expected_row_count": 33,
            "row_scan_reduction_ratio": 0.818,
            "focused_merge_source_env_var": "FOCUSED_CATALYST_RESPONSE_PATH",
            "next_operator_action": (
                "fill_focused_catalyst_response_template_then_set_FOCUSED_CATALYST_RESPONSE_PATH_"
                "and_merge_to_FIELD_ACTIVATION_RESPONSE_PATH"
            ),
            "focused_repair_work_order_status": (
                "focused_catalyst_response_repair_work_order_waiting_for_external_response"
            ),
            "focused_repair_item_count": 1,
            "focused_repair_next_operator_action": (
                "fill_outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json_"
                "with_real_field_values_then_set_FOCUSED_CATALYST_RESPONSE_PATH"
            ),
            "can_submit_to_external_activation_router": False,
            "can_resume_model_chain": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        },
        "field_activation_response_coherence_audit": {
            "audit_status": "field_activation_response_coherence_audit_waiting_for_response_preflight",
            "hard_blocker_count": 0,
            "warning_count": 0,
            "highest_priority_blocker": "",
            "can_route_to_package_assembly": False,
            "can_resume_model_chain": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        },
        "field_activation_response_source_preflight": {
            "source_preflight_status": "field_activation_response_source_using_default_template",
            "external_response_supplied": False,
            "using_default_template": True,
            "can_run_response_preflight": True,
            "can_resume_model_chain": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        },
        "field_activation_response_repair_work_order": {
            "work_order_status": "field_activation_response_repair_work_order_waiting_for_external_response",
            "repair_item_count": 7,
            "highest_priority_repair_id": "R8U102_SUBMIT_FIELD_ACTIVATION_RESPONSE",
            "can_resume_model_chain": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        },
        "field_activation_package_assembly_plan": {
            "assembly_status": "field_activation_package_assembly_plan_blocked_by_response_preflight",
            "channel_plan_count": 1,
            "candidate_channel_plan_count": 2,
            "table_plan_count": 9,
            "can_stage_external_package_candidates": False,
        },
        "field_activation_package_staging_manifest": {
            "staging_status": "field_activation_package_staging_manifest_blocked_by_response_preflight",
            "selected_channel_manifest_count": 1,
            "candidate_channel_requirement_count": 2,
            "can_materialize_no_write_package_candidates": False,
            "next_operator_action": "complete_response_preflight_and_package_assembly_before_staging",
            "can_resume_model_chain": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        },
        "field_activation_materialized_package_preflight": {
            "preflight_status": "field_activation_materialized_package_preflight_blocked_by_staging_manifest",
            "blocker_count": 1,
            "highest_priority_blocker": "R8U105_STAGING_MANIFEST_NOT_READY",
            "can_route_to_external_activation_router": False,
            "next_operator_action": "complete_field_activation_staging_manifest_before_materializing_package",
            "can_resume_model_chain": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        },
        "field_activation_external_readiness_gate": {
            "gate_status": "field_activation_external_readiness_waiting_for_external_response",
            "ready_step_count": 1,
            "blocked_step_count": 6,
            "total_step_count": 7,
            "first_blocked_step": "response_source",
            "highest_priority_blocker": "R8U106_SUBMIT_FIELD_ACTIVATION_RESPONSE",
            "next_operator_action": "set_FIELD_ACTIVATION_RESPONSE_PATH_to_filled_external_response_json",
            "can_submit_to_external_activation_router": False,
            "can_resume_model_chain": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        },
        "field_activation_response_submission_packet": {
            "packet_status": "field_activation_response_submission_packet_waiting_for_external_response",
            "next_operator_action": "fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH",
            "highest_priority_blocker": "R8U106_SUBMIT_FIELD_ACTIVATION_RESPONSE",
            "can_submit_to_response_preflight": True,
            "can_route_to_external_activation_router": False,
            "can_resume_model_chain": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        },
        "field_activation_schema_preflight": {
            "schema_preflight_status": "field_activation_schema_preflight_passed",
            "can_validate_field_activation_response_structure": True,
            "can_resume_model_chain": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        },
    }


def _observation_response_bridge_metrics() -> dict[str, object]:
    return {
        "bridge_status": "observation_response_bridge_ready_for_priority_field_response_fill",
        "primary_target_hidden_state": "catalyst_activity",
        "response_row_count": 6,
        "required_role_coverage_rate": 1.0,
        "can_route_to_agent51_field_proxy_holdout": False,
        "can_relax_agent49_catalyst_uncertainty_block": False,
    }


def _catalyst_evidence_response_gate_metrics() -> dict[str, object]:
    return {
        "gate_status": "catalyst_evidence_response_gate_waiting_for_FIELD_ACTIVATION_RESPONSE_PATH",
        "target_response_row_count": 6,
        "row_level_preflight_pass": False,
        "batch_alignment": {
            "matched_batch_count": 0,
            "matched_batch_requirement_pass": False,
        },
        "can_route_to_focused_materialized_package_preflight": False,
        "can_route_to_agent51_field_proxy_holdout": False,
    }


def _catalyst_response_submission_kit_metrics() -> dict[str, object]:
    return {
        "kit_status": "catalyst_response_submission_kit_ready_for_operator_fill",
        "target_response_row_count": 6,
        "focused_response_template_path": "outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json",
        "can_route_to_agent51_field_proxy_holdout": False,
    }


def _focused_catalyst_response_merge_metrics() -> dict[str, object]:
    return {
        "preflight_status": "focused_catalyst_response_merge_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH",
        "source_preflight_status": "focused_catalyst_response_source_using_default_template",
        "source_can_run_merge_preflight": True,
        "row_preflight_pass": False,
        "can_emit_merged_full_response_candidate": False,
        "can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH": False,
        "merged_full_response_candidate_availability_status": (
            "candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH"
        ),
        "merged_full_response_candidate_self_declared_submit_ready": False,
        "merged_full_response_candidate_preflight_submit_ready": False,
        "merged_full_response_candidate_submit_ready_semantics": (
            "candidate_preflight_submit_ready means the focused six-row merge gate passed. "
            "It is not field validation, model-chain resume readiness, actuator readiness or release readiness."
        ),
        "can_route_to_agent51_field_proxy_holdout": False,
        "focused_catalyst_response_repair_work_order": {
            "work_order_status": "focused_catalyst_response_repair_work_order_waiting_for_external_response",
            "repair_item_count": 1,
            "highest_priority_repair_id": "FOCUSED_SOURCE_SUBMIT_RESPONSE",
            "next_operator_action": (
                "fill_outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json_"
                "with_real_field_values_then_set_FOCUSED_CATALYST_RESPONSE_PATH"
            ),
        },
    }


def _external_activation_operator_action_packet() -> dict[str, object]:
    return {
        "packet_status": "operator_packet_waiting_for_focused_catalyst_response",
        "target_hidden_state": "catalyst_activity",
        "source_env_var": "FOCUSED_CATALYST_RESPONSE_PATH",
        "expected_focused_response_row_count": 6,
        "focused_candidate_availability_status": (
            "candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH"
        ),
        "focused_candidate_operator_packet_submit_ready": False,
        "packet_next_operator_action": (
            "fill_outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json_"
            "with_real_field_values_then_set_FOCUSED_CATALYST_RESPONSE_PATH"
        ),
        "operator_packet_boundary_pass": True,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }


def _catalyst_field_package_slice_metrics() -> dict[str, object]:
    return {
        "slice_status": "catalyst_field_package_slice_waiting_for_CATALYST_FIELD_PACKAGE_SLICE_DIR",
        "slice_preflight_pass": False,
        "matched_batch_count": 0,
        "focused_field_package_slice_template_dir": (
            "outputs/catalyst_field_package_slice/focused_field_package_slice_template"
        ),
        "can_route_to_r7_field_package_patch_candidate": False,
        "can_route_to_agent51_field_proxy_holdout": False,
    }


def _catalyst_slice_r7_patch_candidate_metrics() -> dict[str, object]:
    return {
        "patch_status": "catalyst_slice_r7_patch_waiting_for_valid_catalyst_slice",
        "candidate_materialized": False,
        "candidate_preflight_status": "not_run",
        "full_package_gap_summary": {"remaining_gap_count": 0},
        "can_submit_candidate_as_REAL_FIELD_REPLAY_PACKAGE_DIR": False,
    }


def _evidence_matrix() -> list[dict[str, object]]:
    return [
        {
            "source": "PySensors official repository",
            "method_family": "sparse sensor placement",
            "model_mapping": "Agent48 candidate node-modality matrix",
            "data_needs": "candidate nodes, modalities, topology prior, costs, labels",
            "implementation_path": "compare greedy placement against SSPOR/SSPOC-style objectives",
            "evaluation_metrics": ["reconstruction_gain", "weak_state_coverage", "cost_index"],
            "failure_boundary": "method source only; field topology is still required",
        }
    ]
