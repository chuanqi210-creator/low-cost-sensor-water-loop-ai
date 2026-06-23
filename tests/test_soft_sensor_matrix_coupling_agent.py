from water_ai.agents.data_quality_agent import DataQualityAgent
from water_ai.agents.sensor_network_sparse_placement_agent import SensorNetworkSparsePlacementAgent
from water_ai.agents.soft_sensor_agent import SoftSensorAgent
from water_ai.agents.soft_sensor_matrix_coupling_agent import SoftSensorMatrixCouplingAgent
from water_ai.process_dynamics import generate_sensor_stream_from_process_state, initial_process_state
from water_ai.soft_sensor_model import FEATURE_COLUMNS


def test_soft_sensor_matrix_coupling_agent_builds_layout_aware_contract() -> None:
    sparse_report = SensorNetworkSparsePlacementAgent(max_sensors=6, budget_limit=5.8).run([])
    readings = generate_sensor_stream_from_process_state(initial_process_state("matrix_shock"), n=48, seed=54)
    dq_report = DataQualityAgent().run(readings)
    soft_report = SoftSensorAgent(
        data_quality_report=dq_report,
        sensor_layout_interface=sparse_report.metrics["soft_sensor_interface"],
    ).run(readings)

    report = SoftSensorMatrixCouplingAgent(
        sensor_layout_interface=sparse_report.metrics["soft_sensor_interface"],
        sparse_placement_metrics=sparse_report.metrics,
        soft_sensor_layout_context=soft_report.metrics["layout_context"],
        grey_box_physics_metrics=_grey_box_metrics(),
    ).run(readings)

    contract = report.metrics["feature_contract"]
    readiness = report.metrics["readiness"]

    assert contract["tensor_axes"] == ["time", "node", "modality", "feature_channel"]
    assert contract["mask_shape"] == [6, 5]
    assert "availability_mask" in contract["feature_channels"]
    assert "time_since_last_observed_min" in contract["field_schema_patch"]
    assert readiness["soft_sensor_matrix_status"] == "synthetic_layout_aware_soft_sensor_contract_ready_needs_field_missingness"
    assert readiness["can_update_soft_sensor_training_schema"] is True
    assert readiness["can_write_to_release_gate"] is False


def test_soft_sensor_matrix_coupling_agent_exposes_training_schema_gap_and_stress_tests() -> None:
    sparse_report = SensorNetworkSparsePlacementAgent(max_sensors=6, budget_limit=5.8).run([])
    report = SoftSensorMatrixCouplingAgent(
        sensor_layout_interface=sparse_report.metrics["soft_sensor_interface"],
        sparse_placement_metrics=sparse_report.metrics,
        soft_sensor_layout_context={"layout_status": "global_modality_fallback_used_for_layout"},
        soft_sensor_training_metrics={"features": ["timestamp_min", "cycle_id", "UV254_abs"]},
    ).run([])

    gap = report.metrics["training_schema_gap"]
    stress = report.metrics["missingness_stress_tests"]

    assert "layout_id" in gap["missing_layout_terms"]
    assert "node_id" in gap["missing_layout_terms"]
    assert any(row["scenario_id"] == "catalyst_bed_uv254_orp_missing" for row in stress)
    assert any(issue.issue_type == "soft_sensor_layout_features_missing" for issue in report.issues)
    assert report.metrics["agent50_writeback"]["can_advance_governance_priority"] is True


def test_soft_sensor_matrix_coupling_agent_consumes_pressure_headloss_candidate_pool() -> None:
    sparse_report = SensorNetworkSparsePlacementAgent(max_sensors=6, budget_limit=5.8).run([])
    report = SoftSensorMatrixCouplingAgent(
        sensor_layout_interface=sparse_report.metrics["soft_sensor_interface"],
        sparse_placement_metrics=sparse_report.metrics,
        soft_sensor_layout_context={"layout_status": "global_modality_fallback_used_for_layout"},
    ).run([])

    contract = report.metrics["feature_contract"]["pressure_headloss_candidate_contract"]
    readiness = report.metrics["readiness"]
    gap = report.metrics["training_schema_gap"]

    assert contract["pool_status"] == "pressure_headloss_candidate_pool_ready_needs_field_topology_and_labels"
    assert contract["source"] == "Agent48.hidden_state_requirement_ledger"
    assert "N3_catalyst_bed:pressure_drop_kPa" in contract["candidate_ids"]
    assert "headloss_kPa_per_m" in contract["candidate_feature_terms"]
    assert contract["can_use_as_installed_sensor"] is False
    assert readiness["pressure_headloss_candidate_count"] == contract["candidate_count"]
    assert readiness["can_update_pressure_headloss_candidate_schema"] is True
    assert readiness["can_use_pressure_headloss_for_field_claim"] is False
    assert "pressure_drop_kPa" in gap["missing_pressure_headloss_terms"]
    assert any(
        issue.issue_type == "pressure_headloss_candidate_schema_not_trained"
        for issue in report.issues
    )


def test_soft_sensor_matrix_coupling_agent_consumes_hydraulic_path_contract() -> None:
    sparse_report = SensorNetworkSparsePlacementAgent(max_sensors=6, budget_limit=5.8).run([])
    report = SoftSensorMatrixCouplingAgent(
        sensor_layout_interface=sparse_report.metrics["soft_sensor_interface"],
        sparse_placement_metrics=sparse_report.metrics,
        soft_sensor_layout_context={"layout_status": "global_modality_fallback_used_for_layout"},
    ).run([])

    contract = report.metrics["feature_contract"]["hydraulic_path_feature_contract"]
    readiness = report.metrics["readiness"]
    gap = report.metrics["training_schema_gap"]

    assert contract["source"] == "Agent48.hydraulic_path_coverage_contract"
    assert contract["contract_status"] == "hydraulic_path_contract_ready_needs_field_topology_and_release_endpoint"
    assert contract["covered_stage_count"] == 6
    assert contract["path_stage_count"] == 6
    assert contract["recirculation_loop_observed"] is True
    assert contract["final_release_gate_needs_effluent_label"] is True
    assert contract["can_support_soft_sensor_path_prior"] is True
    assert contract["can_use_for_release_gate"] is False
    assert "hydraulic_path_coverage_rate" in contract["feature_terms"]
    assert "release_endpoint_label_missing_flag" in contract["feature_terms"]
    assert "path_stage_id" in contract["field_schema_terms"]
    assert "release_boundary_flag" in contract["field_schema_terms"]
    assert readiness["can_update_hydraulic_path_feature_schema"] is True
    assert readiness["hydraulic_path_schema_ready"] is True
    assert readiness["layout_holdout_ready"] is False
    assert readiness["can_use_hydraulic_path_for_release_gate"] is False
    assert readiness["next_recommended_core_action"] == "R8u65_add_synthetic_layout_holdout_for_path_features"
    assert gap["missing_hydraulic_path_terms"] == []
    assert "final_effluent_release_endpoint_labels_missing" in gap["field_blockers"]
    assert not any(issue.issue_type == "hydraulic_path_feature_schema_not_trained" for issue in report.issues)
    assert any(
        issue.issue_type == "hydraulic_path_release_endpoint_blocks_release_use"
        for issue in report.issues
    )


def test_soft_sensor_matrix_coupling_agent_consumes_layout_holdout_metrics() -> None:
    sparse_report = SensorNetworkSparsePlacementAgent(max_sensors=6, budget_limit=5.8).run([])
    training_metrics = {
        "features": FEATURE_COLUMNS,
        "hydraulic_path_feature_variation_status": "synthetic_path_feature_variation_ready_for_layout_holdout",
        "layout_holdout": {
            "status": "synthetic_layout_holdout_ready_needs_field_path_labels",
            "mean_mae": 0.01524,
            "train_layout_ids": ["greedy_marginal:4x10", "greedy_marginal:6x10"],
            "holdout_layout_ids": ["classification_sspoc_proxy:5x10"],
            "field_boundary": "synthetic layout holdout checks path-feature schema generalization only",
        },
    }
    report = SoftSensorMatrixCouplingAgent(
        sensor_layout_interface=sparse_report.metrics["soft_sensor_interface"],
        sparse_placement_metrics=sparse_report.metrics,
        soft_sensor_layout_context={"layout_status": "global_modality_fallback_used_for_layout"},
        soft_sensor_training_metrics=training_metrics,
    ).run([])

    readiness = report.metrics["readiness"]

    assert readiness["hydraulic_path_feature_variation_ready"] is True
    assert readiness["layout_holdout_ready"] is True
    assert readiness["layout_holdout_mean_mae"] == 0.01524
    assert readiness["layout_holdout_heldout_layout_count"] == 1
    assert readiness["field_path_endpoint_label_package_ready"] is False
    assert readiness["field_path_endpoint_label_matched_batch_count"] == 0
    assert readiness["next_recommended_core_action"] == "R8u66_collect_field_path_endpoint_labels_for_layout_holdout"
    assert any(
        issue.issue_type == "field_path_endpoint_label_package_required_for_field_holdout"
        for issue in report.issues
    )


def test_soft_sensor_matrix_coupling_agent_rejects_template_path_endpoint_package() -> None:
    sparse_report = SensorNetworkSparsePlacementAgent(max_sensors=6, budget_limit=5.8).run([])
    package = _accepted_field_path_package()
    package["node_modality_sensor_timeseries"][0]["template_only"] = True
    report = SoftSensorMatrixCouplingAgent(
        sensor_layout_interface=sparse_report.metrics["soft_sensor_interface"],
        sparse_placement_metrics=sparse_report.metrics,
        soft_sensor_layout_context={"layout_status": "global_modality_fallback_used_for_layout"},
        soft_sensor_training_metrics=_layout_holdout_training_metrics(),
        field_path_label_package=package,
    ).run([])

    preflight = report.metrics["field_path_endpoint_label_package_preflight"]
    readiness = report.metrics["readiness"]

    assert preflight["preflight_status"] == "field_path_endpoint_label_package_blocked_by_preflight"
    assert preflight["template_marker_count"] == 1
    assert "template_or_todo_markers_present" in preflight["blockers"]
    assert readiness["field_path_endpoint_label_package_ready"] is False
    assert readiness["next_recommended_core_action"] == "R8u66_collect_field_path_endpoint_labels_for_layout_holdout"


def test_soft_sensor_matrix_coupling_agent_accepts_field_path_endpoint_package_preflight() -> None:
    sparse_report = SensorNetworkSparsePlacementAgent(max_sensors=6, budget_limit=5.8).run([])
    report = SoftSensorMatrixCouplingAgent(
        sensor_layout_interface=sparse_report.metrics["soft_sensor_interface"],
        sparse_placement_metrics=sparse_report.metrics,
        soft_sensor_layout_context={"layout_status": "global_modality_fallback_used_for_layout"},
        soft_sensor_training_metrics=_layout_holdout_training_metrics(),
        field_path_label_package=_accepted_field_path_package(),
        data_origin="field_layout_missingness",
    ).run([])

    preflight = report.metrics["field_path_endpoint_label_package_preflight"]
    readiness = report.metrics["readiness"]

    assert preflight["preflight_status"] == "field_path_endpoint_label_package_ready_for_field_layout_holdout"
    assert preflight["matched_batch_count"] == 5
    assert preflight["accepted_batch_ids"] == ["B0", "B1", "B2", "B3", "B4"]
    assert readiness["field_path_endpoint_label_package_ready"] is True
    assert readiness["can_route_to_field_layout_holdout"] is True
    assert readiness["field_ready"] is True
    assert readiness["next_recommended_core_action"] == "R8u67_run_field_layout_holdout_with_accepted_path_endpoint_labels"


def _grey_box_metrics() -> dict[str, object]:
    return {
        "readiness": {
            "grey_box_physics_status": "synthetic_grey_box_physics_prior_ready_needs_field_calibration",
            "synthetic_prior_ready": True,
        }
    }


def _layout_holdout_training_metrics() -> dict[str, object]:
    return {
        "features": FEATURE_COLUMNS,
        "hydraulic_path_feature_variation_status": "synthetic_path_feature_variation_ready_for_layout_holdout",
        "layout_holdout": {
            "status": "synthetic_layout_holdout_ready_needs_field_path_labels",
            "mean_mae": 0.01524,
            "train_layout_ids": ["greedy_marginal:4x10", "greedy_marginal:6x10"],
            "holdout_layout_ids": ["classification_sspoc_proxy:5x10"],
            "field_boundary": "synthetic layout holdout checks path-feature schema generalization only",
        },
    }


def _accepted_field_path_package() -> dict[str, list[dict[str, object]]]:
    batches = [f"B{idx}" for idx in range(5)]
    return {
        "site_topology_or_bed_geometry": [
            {
                "site_id": "S1",
                "node_id": "N5_effluent",
                "zone": "effluent",
                "upstream_node_id": "N4_loop",
                "downstream_node_id": "OUT",
                "path_stage_id": "S5_release_boundary",
                "hydraulic_path_role": "final_effluent_endpoint",
                "nominal_flow_Lmin": 1.1,
                "nominal_HRT_min": 20,
                "recycle_ratio": 0.25,
                "release_boundary_flag": True,
                "recirculation_loop_flag": False,
            }
        ],
        "node_modality_sensor_timeseries": [
            {
                "batch_id": batch_id,
                "timestamp_min": 12,
                "layout_id": "field_layout_v1",
                "node_id": "N5_effluent",
                "zone": "effluent",
                "modality": "UV254_abs",
                "sensor_value": 0.18,
                "availability_mask": 1,
                "time_since_last_observed_min": 0,
                "data_origin": "field",
            }
            for batch_id in batches
        ],
        "hydraulic_path_stage_labels": [
            {
                "batch_id": batch_id,
                "layout_id": "field_layout_v1",
                "node_id": "N5_effluent",
                "zone": "effluent",
                "path_stage_id": "S5_release_boundary",
                "hydraulic_path_role": "final_effluent_endpoint",
                "stage_coverage_label": 1,
                "direct_path_stage_coverage_label": 1,
                "proxy_path_stage_coverage_label": 0,
                "label_source": "operator_topology_review",
                "reviewer_id": "reviewer_a",
                "review_time_min": 30,
            }
            for batch_id in batches
        ],
        "final_effluent_endpoint_labels": [
            {
                "batch_id": batch_id,
                "endpoint_node_id": "N5_effluent",
                "sample_time_min": 24,
                "final_effluent_direct_observed": 1,
                "release_gate_label": "hold",
                "release_risk_label": 0.2,
                "analyte": "target_pollutant",
                "value": 0.08,
                "unit": "mg/L",
                "qa_flag": "pass",
                "reviewer_id": "reviewer_a",
            }
            for batch_id in batches
        ],
        "campaign_operation_log": [
            {
                "campaign_id": "C1",
                "batch_id": batch_id,
                "action_id": "hold_for_validation",
                "start_min": 0,
                "end_min": 30,
                "recycle_ratio": 0.25,
                "hold_time_min": 30,
                "release_policy": "operator_reviewed",
                "operator_override": False,
            }
            for batch_id in batches
        ],
        "offline_lab_results": [
            {
                "batch_id": batch_id,
                "sample_time_min": 24,
                "sample_source": "final_effluent",
                "analyte": "target_pollutant",
                "value": 0.08,
                "unit": "mg/L",
                "method": "LCMS",
                "qa_flag": "pass",
            }
            for batch_id in batches
        ],
    }
