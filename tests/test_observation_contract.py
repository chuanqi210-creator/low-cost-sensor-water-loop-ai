from water_ai.agents.sensor_network_sparse_placement_agent import SensorNetworkSparsePlacementAgent
from water_ai.observation_contract import ObservationContractMerge


def test_observation_contract_merges_agent48_51_54_into_budget_balanced_contract() -> None:
    result = _contract().build()
    readiness = result["readiness"]
    recommended = result["recommended_observation_contract"]

    assert readiness["observation_contract_status"] == (
        "synthetic_observation_contract_ready_needs_field_topology_proxy_labels_and_missingness"
    )
    assert recommended["candidate_id"] == "budget_rebalanced_proxy_contract"
    assert recommended["budget_pass"] is True
    assert readiness["proxy_enhanced_weak_state_coverage"] >= 0.55
    assert readiness["base_weak_state_coverage"] == 0.3
    assert readiness["catalyst_observability_gain"] > 0.0
    assert readiness["weak_axis_repair_status"] == "agent48_catalyst_axis_requires_proxy_patch_and_field_label"
    assert readiness["weak_axis_repair_score"] > 0.0


def test_observation_contract_preserves_no_release_and_no_actuator_boundary() -> None:
    result = _contract().build()
    readiness = result["readiness"]
    policy = result["writeback_policy"]

    assert readiness["can_write_to_actuator"] is False
    assert readiness["can_write_to_release_gate"] is False
    assert readiness["can_relax_agent49_catalyst_uncertainty_block"] is False
    assert "release_gate_policy" in policy["blocked_writeback"]
    assert "agent49_catalyst_uncertainty_relaxation" in policy["blocked_writeback"]


def test_observation_contract_exposes_soft_sensor_schema_patch_and_field_requirements() -> None:
    result = _contract().build()
    schema_patch = result["soft_sensor_schema_patch"]
    requirements = result["field_validation_requirements"]

    assert "layout_id" in schema_patch["missing_layout_terms"]
    assert "availability_mask" in schema_patch["missing_layout_terms"]
    assert len(requirements) == 3
    assert requirements[0]["needed_for"] == "final field sensor placement"
    assert requirements[1]["needed_for"] == "relaxing catalyst uncertainty block"


def test_observation_contract_keeps_full_patch_as_over_budget_design_option() -> None:
    result = _contract().build()
    candidates = {item["candidate_id"]: item for item in result["contract_candidates"]}

    assert candidates["full_proxy_patch_contract"]["proxy_enhanced_weak_state_coverage"] == 0.72
    assert candidates["full_proxy_patch_contract"]["budget_pass"] is False
    assert candidates["budget_rebalanced_proxy_contract"]["budget_pass"] is True
    assert candidates["budget_rebalanced_proxy_contract"]["removed_base_pairs"]


def test_observation_contract_consumes_agent51_weak_axis_repair_priorities() -> None:
    result = _contract().build()
    records = result["proxy_patch_records"]
    recommended = result["recommended_observation_contract"]
    policy = result["writeback_policy"]

    assert records[0]["candidate_id"] == "N3_catalyst_bed_outlet:UV254_abs"
    assert records[0]["repair_priority_score"] > records[-1]["repair_priority_score"]
    assert records[0]["weak_axis_repair_status"] == "agent48_catalyst_axis_requires_proxy_patch_and_field_label"
    assert recommended["field_repair_evidence_requirement_count"] >= 1
    assert "agent51_weak_axis_repair_plan" in policy["allowed_writeback"]


def test_observation_contract_consumes_agent48_hidden_state_requirement_ledger() -> None:
    result = _contract_with_real_agent48_ledger().build()
    readiness = result["readiness"]
    base = result["base_layout_contract"]
    requirements = {item["requirement_id"]: item for item in result["field_validation_requirements"]}

    assert readiness["agent48_hidden_state_ledger_status"] == "hidden_state_requirement_ledger_ready_with_gaps"
    assert readiness["agent48_hidden_state_ready_count"] >= 4
    assert "catalyst_activity" in readiness["agent48_hidden_state_hard_unresolved"]
    assert base["hidden_state_minimum_patch_status"] == "minimum_cost_patch_requires_new_modality_or_field_label"
    assert readiness["agent48_pressure_headloss_candidate_pool_status"] == (
        "pressure_headloss_candidate_pool_ready_needs_field_topology_and_labels"
    )
    assert "N3_catalyst_bed:pressure_drop_kPa" in readiness["agent48_pressure_headloss_candidate_ids"]
    assert "R2_FV4_agent48_hidden_state_requirement_patch" in requirements
    assert requirements["R2_FV4_agent48_hidden_state_requirement_patch"]["hard_unresolved_hidden_states"] == [
        "catalyst_activity"
    ]
    assert requirements["R2_FV4_agent48_hidden_state_requirement_patch"]["minimum_matched_batch_count"] == 3
    assert "N3_catalyst_bed:headloss_kPa_per_m" in requirements["R2_FV4_agent48_hidden_state_requirement_patch"][
        "pressure_headloss_candidate_ids"
    ]
    assert "pressure_drop_kPa_or_headloss_proxy" in requirements["R2_FV4_agent48_hidden_state_requirement_patch"][
        "required_signals_or_fields"
    ]


def _contract() -> ObservationContractMerge:
    return ObservationContractMerge(
        sparse_placement_metrics={
            "selected_sensor_plan": [
                _sensor("N4_recirculation_loop:UV254_abs", "N4_recirculation_loop", "UV254_abs", 1.012, 0.590),
                _sensor("N3_catalyst_bed_outlet:turbidity_NTU", "N3_catalyst_bed_outlet", "turbidity_NTU", 0.826, 0.348),
                _sensor("N2_reactor_mid:ORP_mV", "N2_reactor_mid", "ORP_mV", 0.756, 0.321),
                _sensor("N0_influent:EC_uScm", "N0_influent", "EC_uScm", 0.434, 0.307),
                _sensor("N1_equalization_tank:flow_Lmin", "N1_equalization_tank", "flow_Lmin", 0.476, 0.245),
                _sensor("N5_polishing_inlet:turbidity_NTU", "N5_polishing_inlet", "turbidity_NTU", 0.672, 0.214),
            ],
            "coverage": {
                "catalyst_activity_observability": 0.3,
                "matrix_interference_observability": 0.851,
                "weak_state_coverage": 0.3,
                "soft_sensor_reconstruction_gain": 0.827,
                "total_cost_index": 4.176,
            },
            "readiness": {"budget_limit": 5.8, "data_origin": "synthetic_topology_prior"},
            "placement_diagnostics": {
                "diagnostic_status": "placement_diagnostics_need_axis_patch_or_field_benchmark",
                "axis_span_rank_ratio": 0.667,
                "condition_number_proxy": 61.726,
                "reconstruction_stability_score": 0.401,
                "weak_axis_gap_count": 2,
                "weak_axis_gaps": [
                    {
                        "axis": "catalyst_activity_observability",
                        "current_coverage": 0.3,
                        "target": 0.55,
                        "gap": 0.25,
                        "best_available_candidate": "N3_catalyst_bed_outlet:UV254_abs",
                        "best_available_value": 0.404,
                        "recoverable_by_current_candidate_pool": False,
                    }
                ],
            },
            "soft_sensor_interface": {
                "layout_id": "greedy_marginal:6x10",
                "selected_nodes": [
                    "N0_influent",
                    "N1_equalization_tank",
                    "N2_reactor_mid",
                    "N3_catalyst_bed_outlet",
                    "N4_recirculation_loop",
                    "N5_polishing_inlet",
                ],
                "selected_modalities": ["EC_uScm", "ORP_mV", "UV254_abs", "flow_Lmin", "turbidity_NTU"],
            },
        },
        catalyst_proxy_metrics={
            "proxy_catalog": [
                {"proxy_id": "bed_uv254_removal_delta", "recommended_patch": ["N3_catalyst_bed_outlet:UV254_abs"]},
                {"proxy_id": "orp_decay_across_bed", "recommended_patch": ["N3_catalyst_bed_outlet:ORP_mV"]},
                {"proxy_id": "turbidity_pressure_fouling", "recommended_patch": ["N3_catalyst_bed:pressure_drop_kPa"]},
            ],
            "proxy_metrics": {
                "recommended_sensor_patches": [
                    "N3_catalyst_bed_outlet:UV254_abs",
                    "N3_catalyst_bed_outlet:ORP_mV",
                    "N3_catalyst_bed:pressure_drop_kPa",
                ],
                "proxy_observability_after_recommended_patch": 0.72,
            },
            "weak_axis_repair_plan": {
                "repair_status": "agent48_catalyst_axis_requires_proxy_patch_and_field_label",
                "repair_score": 0.934,
                "prioritized_proxy_patches": [
                    {
                        "patch_signal": "N3_catalyst_bed_outlet:UV254_abs",
                        "patch_class": "low_cost_sensor",
                        "repair_priority_score": 0.66,
                        "supports_proxy_ids": ["bed_uv254_removal_delta", "residence_time_normalized_rate_residual"],
                        "why_needed": "床出口 UV254 与回流/床入口 UV254 组成差分，支撑活性和停留时间归一化速率残差。",
                    },
                    {
                        "patch_signal": "N3_catalyst_bed_outlet:ORP_mV",
                        "patch_class": "low_cost_sensor",
                        "repair_priority_score": 0.36,
                        "supports_proxy_ids": ["orp_decay_across_bed"],
                        "why_needed": "床出口 ORP 与反应核心 ORP 组成氧化剂利用/衰减代理。",
                    },
                    {
                        "patch_signal": "N3_catalyst_bed:pressure_drop_kPa",
                        "patch_class": "low_cost_sensor",
                        "repair_priority_score": 0.35,
                        "supports_proxy_ids": ["turbidity_pressure_fouling"],
                        "why_needed": "压降用于区分催化剂活性衰减与床层堵塞/污堵。",
                    },
                ],
                "field_repair_evidence_requirements": [
                    {
                        "requirement_id": "CAX_1_low_cost_sensor",
                        "required_table": "sensor_timeseries",
                    }
                ],
            },
            "readiness": {"field_validated": False},
        },
        soft_sensor_matrix_metrics={
            "feature_contract": {
                "layout_id": "greedy_marginal:6x10",
                "selected_nodes": [
                    "N0_influent",
                    "N1_equalization_tank",
                    "N2_reactor_mid",
                    "N3_catalyst_bed_outlet",
                    "N4_recirculation_loop",
                    "N5_polishing_inlet",
                ],
                "selected_modalities": ["EC_uScm", "ORP_mV", "UV254_abs", "flow_Lmin", "turbidity_NTU"],
            },
            "training_schema_gap": {
                "missing_layout_terms": [
                    "layout_id",
                    "node_id",
                    "zone",
                    "modality",
                    "availability_mask",
                    "time_since_last_observed_min",
                ]
            },
            "readiness": {"missingness_robustness_score": 0.684, "field_ready": False},
        },
    )


def _contract_with_real_agent48_ledger() -> ObservationContractMerge:
    sparse_report = SensorNetworkSparsePlacementAgent(max_sensors=6, budget_limit=5.8).run([])
    base = _contract()
    interface = sparse_report.metrics["soft_sensor_interface"]
    return ObservationContractMerge(
        sparse_placement_metrics=sparse_report.metrics,
        catalyst_proxy_metrics=base.catalyst_proxy_metrics,
        soft_sensor_matrix_metrics={
            "feature_contract": {
                "layout_id": interface["layout_id"],
                "selected_nodes": interface["selected_nodes"],
                "selected_modalities": interface["selected_modalities"],
            },
            "training_schema_gap": {
                "missing_layout_terms": [
                    "layout_id",
                    "node_id",
                    "zone",
                    "modality",
                    "availability_mask",
                    "time_since_last_observed_min",
                ]
            },
            "readiness": {"missingness_robustness_score": 0.684, "field_ready": False},
        },
    )


def _sensor(candidate_id: str, node: str, modality: str, cost: float, marginal: float) -> dict[str, object]:
    return {
        "candidate_id": candidate_id,
        "node_id": node,
        "modality": modality,
        "cost_index": cost,
        "marginal_score": marginal,
    }
