from water_ai.agents.sensor_network_sparse_placement_agent import (
    OBSERVATION_AXES,
    SensorNetworkSparsePlacementAgent,
)


def test_sparse_placement_agent_builds_multidimensional_observation_matrix() -> None:
    report = SensorNetworkSparsePlacementAgent(max_sensors=5).run([])

    matrix = report.metrics["observation_matrix"]
    interface = report.metrics["soft_sensor_interface"]
    diagnostics = report.metrics["placement_diagnostics"]
    readiness = report.metrics["readiness"]

    assert matrix
    assert set(matrix[0]["vector"]) == set(OBSERVATION_AXES)
    assert interface["matrix_shape"] == [5, len(OBSERVATION_AXES)]
    assert interface["selected_strategy_id"] == report.metrics["selected_strategy"]["strategy_id"]
    assert interface["placement_diagnostics"]["axis_span_rank_ratio"] == diagnostics["axis_span_rank_ratio"]
    assert diagnostics["candidate_matrix_summary"]["axis_count"] == len(OBSERVATION_AXES) - 1
    assert diagnostics["selected_matrix_shape"] == [5, len(OBSERVATION_AXES) - 1]
    assert interface["missingness_mask_contract"]["requires_layout_id"] is True
    assert readiness["sparse_placement_status"] == "sparse_sensor_layout_ready_needs_field_topology"
    assert readiness["can_update_soft_sensor_design_prior"] is True


def test_sparse_placement_agent_selects_complementary_nodes_and_modalities() -> None:
    report = SensorNetworkSparsePlacementAgent(max_sensors=6).run([])

    selected = report.metrics["selected_sensor_plan"]
    coverage = report.metrics["coverage"]
    modalities = {item["modality"] for item in selected}
    nodes = {item["node_id"] for item in selected}

    assert len(selected) == 6
    assert len(modalities) >= 4
    assert len(nodes) >= 4
    assert coverage["matrix_interference_observability"] >= 0.62
    assert coverage["soft_sensor_reconstruction_gain"] >= 0.62


def test_sparse_placement_agent_respects_budget_limit() -> None:
    report = SensorNetworkSparsePlacementAgent(max_sensors=8, budget_limit=2.0).run([])

    selected = report.metrics["selected_sensor_plan"]
    coverage = report.metrics["coverage"]
    readiness = report.metrics["readiness"]

    assert coverage["total_cost_index"] <= 2.0
    assert len(selected) < 8
    assert readiness["can_finalize_field_deployment"] is False


def test_sparse_placement_agent_still_blocks_field_topology_when_weak_state_is_low() -> None:
    report = SensorNetworkSparsePlacementAgent(
        candidate_nodes=_field_nodes(),
        max_sensors=4,
        budget_limit=5.0,
        data_origin="field_topology",
    ).run([])

    readiness = report.metrics["readiness"]

    assert readiness["sparse_placement_status"] == "field_sparse_sensor_layout_needs_redesign"
    assert readiness["field_topology_required"] is False
    assert readiness["can_finalize_field_deployment"] is False
    assert report.metrics["coverage"]["catalyst_activity_observability"] < 0.55


def test_sparse_placement_agent_compares_reconstruction_classification_and_topology_strategies() -> None:
    report = SensorNetworkSparsePlacementAgent(max_sensors=6, budget_limit=5.8).run([])

    comparison = report.metrics["algorithm_comparison"]
    selected = report.metrics["selected_strategy"]
    strategies = {item["strategy_id"] for item in comparison}

    assert {
        "greedy_marginal",
        "cost_only_baseline",
        "deterministic_random_baseline",
        "reconstruction_qr_proxy",
        "classification_sspoc_proxy",
        "topology_robust_cost_proxy",
    }.issubset(strategies)
    assert comparison[0]["comparable_score"] >= comparison[-1]["comparable_score"]
    assert selected["strategy_id"] == comparison[0]["strategy_id"]
    assert selected["selected_sensor_plan"]
    assert selected["field_validation_boundary"].startswith("algorithm comparison")
    assert all("axis_span_rank_ratio" in item for item in comparison)
    assert all("condition_number_proxy" in item for item in comparison)
    assert all("weak_axis_gap_count" in item for item in comparison)
    assert all("benchmark_role" in item for item in comparison)
    assert all("prior_art_family" in item for item in comparison)


def test_sparse_placement_agent_outputs_prior_art_baseline_contract() -> None:
    report = SensorNetworkSparsePlacementAgent(max_sensors=6, budget_limit=5.8).run([])

    contract = report.metrics["baseline_comparison_contract"]

    assert contract["comparison_status"] == "sparse_baseline_comparison_ready_needs_field_topology_and_labels"
    assert contract["missing_baseline_strategy_ids"] == []
    assert "deterministic_random_baseline" in contract["observed_strategy_ids"]
    assert "cost_only_baseline" in contract["observed_strategy_ids"]
    assert isinstance(contract["best_vs_random_delta"], float)
    assert isinstance(contract["best_vs_cost_only_delta"], float)
    assert contract["field_benchmark_required"] is True
    assert "cannot prove patentability" in contract["cannot_do"]
    assert "node-modality hidden-state placement" in contract["claim_scope_use"]


def test_sparse_placement_agent_outputs_topology_graph_and_comparable_objectives() -> None:
    report = SensorNetworkSparsePlacementAgent(max_sensors=6, budget_limit=5.8).run([])

    graph = report.metrics["topology_graph"]
    comparison = report.metrics["algorithm_comparison"]

    assert graph["topology_type"] == "process_unit_graph_with_recirculation_loop"
    assert any(edge["from"] == "N4_recirculation_loop" for edge in graph["edges"])
    assert all("reconstruction_objective" in item for item in comparison)
    assert all("classification_objective" in item for item in comparison)
    assert all("topology_coverage_score" in item for item in comparison)


def test_sparse_placement_agent_outputs_hydraulic_path_coverage_contract() -> None:
    report = SensorNetworkSparsePlacementAgent(max_sensors=6, budget_limit=5.8).run([])

    contract = report.metrics["hydraulic_path_coverage_contract"]
    interface_contract = report.metrics["soft_sensor_interface"]["hydraulic_path_contract"]

    assert contract["path_id"] == "low_cost_circular_treatment_path_v1"
    assert contract["contract_status"] == "hydraulic_path_contract_ready_needs_field_topology_and_release_endpoint"
    assert contract["path_stage_count"] == 6
    assert contract["covered_stage_count"] == 6
    assert contract["recirculation_loop_observed"] is True
    assert contract["low_frequency_time_buffer_observed"] is True
    assert contract["final_effluent_directly_observed"] is False
    assert contract["final_release_gate_needs_effluent_label"] is True
    assert contract["can_support_soft_sensor_path_prior"] is True
    assert contract["can_support_control_replay_design_prior"] is True
    assert contract["can_finalize_field_deployment"] is False
    assert "field_topology_and_hydraulic_path_labels_required" in contract["unresolved_requirements"]
    assert "final_effluent_release_endpoint_not_directly_observed" in contract["unresolved_requirements"]
    assert "pressure_drop_or_headloss_proxy_not_installed_in_selected_layout" in contract["unresolved_requirements"]
    assert "agent52_replay_table" in contract["field_package_contract"]["required_tables"]
    assert "cannot write release gate when final effluent endpoint is not directly field-labeled" in contract["cannot_do"]
    assert interface_contract["contract_status"] == contract["contract_status"]
    assert interface_contract["covered_stage_count"] == contract["covered_stage_count"]
    assert any(
        issue.issue_type == "hydraulic_path_release_endpoint_needs_effluent_label"
        for issue in report.issues
    )


def test_sparse_placement_agent_diagnoses_matrix_stability_and_weak_axis_gaps() -> None:
    report = SensorNetworkSparsePlacementAgent(max_sensors=6, budget_limit=5.8).run([])

    diagnostics = report.metrics["placement_diagnostics"]
    gaps = diagnostics["weak_axis_gaps"]

    assert diagnostics["diagnostic_status"] == "placement_diagnostics_need_axis_patch_or_field_benchmark"
    assert diagnostics["selected_matrix_rank"] >= 4
    assert diagnostics["axis_span_rank_ratio"] > 0.0
    assert diagnostics["condition_number_proxy"] > 1.0
    assert diagnostics["reconstruction_stability_score"] < 1.0
    assert diagnostics["single_point_dependency_count"] >= 1
    assert any(gap["axis"] == "catalyst_activity_observability" for gap in gaps)
    assert all("best_available_candidate" in gap for gap in gaps)


def test_sparse_placement_agent_outputs_hidden_state_requirement_ledger() -> None:
    report = SensorNetworkSparsePlacementAgent(max_sensors=6, budget_limit=5.8).run([])

    ledger = report.metrics["hidden_state_requirement_ledger"]
    rows = {row["hidden_state"]: row for row in ledger["state_rows"]}
    interface_contract = report.metrics["soft_sensor_interface"]["hidden_state_requirement_contract"]

    assert ledger["ledger_status"] == "hidden_state_requirement_ledger_ready_with_gaps"
    assert ledger["hidden_state_count"] == 6
    assert ledger["ready_hidden_state_count"] >= 4
    assert interface_contract["ledger_status"] == ledger["ledger_status"]
    assert interface_contract["state_readiness"]["catalyst_activity"]["ready_for_soft_sensor_estimation"] is False
    assert interface_contract["state_readiness"]["hydraulic_delay"]["ready_for_soft_sensor_estimation"] is True

    catalyst = rows["catalyst_activity"]
    assert catalyst["min_primary_axis_score"] < catalyst["target"]
    assert catalyst["candidate_patch"]["patch_status"] == "candidate_pool_patch_incomplete"
    assert catalyst["candidate_patch"]["candidate_pool_recoverable"] is False
    assert "pressure_drop_kPa" in catalyst["missing_required_modalities"]
    assert "pressure_drop_or_headloss_proxy_not_in_selected_layout" in catalyst["unresolved_requirements"]
    assert "offline_lab_results.catalyst_activity" in catalyst["field_evidence_needed"]


def test_sparse_placement_agent_translates_requirement_gaps_into_minimum_cost_patch() -> None:
    report = SensorNetworkSparsePlacementAgent(max_sensors=6, budget_limit=5.8).run([])

    ledger = report.metrics["hidden_state_requirement_ledger"]
    patch = ledger["minimum_cost_requirement_patch"]
    rows = {row["hidden_state"]: row for row in ledger["state_rows"]}

    assert patch["patch_status"] == "minimum_cost_patch_requires_new_modality_or_field_label"
    assert "catalyst_activity" in patch["hard_unresolved_hidden_states"]
    assert "matrix_interference" in patch["unresolved_hidden_states"]
    assert patch["recommended_candidate_ids"]
    assert rows["pollutant_residual"]["candidate_patch"]["patch_status"] == "state_target_already_met"
    assert any(
        issue.issue_type == "hidden_state_requirement_requires_new_modality_or_field_label"
        for issue in report.issues
    )


def test_sparse_placement_agent_designs_pressure_headloss_candidate_pool_for_hard_unresolved_states() -> None:
    report = SensorNetworkSparsePlacementAgent(max_sensors=6, budget_limit=5.8).run([])

    ledger = report.metrics["hidden_state_requirement_ledger"]
    pool = ledger["pressure_headloss_candidate_pool"]
    patch = ledger["minimum_cost_requirement_patch"]

    assert pool["pool_status"] == "pressure_headloss_candidate_pool_ready_needs_field_topology_and_labels"
    assert pool["target_hidden_states"] == ["catalyst_activity", "hydraulic_delay"]
    assert pool["candidate_count"] >= 3
    assert "N3_catalyst_bed:pressure_drop_kPa" in pool["candidate_ids"]
    assert "N3_catalyst_bed:headloss_kPa_per_m" in pool["candidate_ids"]
    assert "node_modality_sensor_timeseries" in pool["field_package_contract"]["required_tables"]
    assert pool["field_package_contract"]["minimum_matched_batch_count"] == 3
    assert "cannot write actuator policy" in pool["field_package_contract"]["cannot_do"]
    assert patch["pressure_headloss_candidate_count"] == pool["candidate_count"]
    assert patch["pressure_headloss_candidate_pool_status"] == pool["pool_status"]


def _field_nodes() -> list[dict[str, object]]:
    return [
        {
            "node_id": "F1_matrix_inlet",
            "zone": "influent",
            "hydraulic_position": 0.08,
            "process_representativeness": 0.60,
            "matrix_shock_exposure": 1.0,
            "catalyst_access": 0.25,
            "hydraulic_leverage": 0.55,
            "control_latency_value": 0.95,
            "maintenance_access": 0.92,
            "install_cost_index": 0.65,
        },
        {
            "node_id": "F2_reactor_core",
            "zone": "reaction_core",
            "hydraulic_position": 0.50,
            "process_representativeness": 0.95,
            "matrix_shock_exposure": 0.72,
            "catalyst_access": 0.72,
            "hydraulic_leverage": 0.65,
            "control_latency_value": 0.66,
            "maintenance_access": 0.70,
            "install_cost_index": 0.90,
        },
        {
            "node_id": "F3_catalyst_outlet",
            "zone": "catalyst_bed",
            "hydraulic_position": 0.68,
            "process_representativeness": 0.92,
            "matrix_shock_exposure": 0.68,
            "catalyst_access": 1.0,
            "hydraulic_leverage": 0.58,
            "control_latency_value": 0.62,
            "maintenance_access": 0.72,
            "install_cost_index": 0.86,
        },
        {
            "node_id": "F4_recycle_loop",
            "zone": "loop",
            "hydraulic_position": 0.58,
            "process_representativeness": 0.88,
            "matrix_shock_exposure": 0.92,
            "catalyst_access": 0.70,
            "hydraulic_leverage": 1.0,
            "control_latency_value": 0.92,
            "maintenance_access": 0.78,
            "install_cost_index": 0.72,
        },
        {
            "node_id": "F5_effluent",
            "zone": "effluent",
            "hydraulic_position": 0.96,
            "process_representativeness": 0.95,
            "matrix_shock_exposure": 0.42,
            "catalyst_access": 0.40,
            "hydraulic_leverage": 0.50,
            "control_latency_value": 0.40,
            "maintenance_access": 0.90,
            "install_cost_index": 0.64,
        },
    ]
