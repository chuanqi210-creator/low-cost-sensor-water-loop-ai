from water_ai.new_core_interface_candidate_gate import (
    GATE_ID,
    build_new_core_interface_candidate_gate,
    new_core_interface_candidate_gate_report_md,
)


def test_new_core_interface_candidate_gate_ranks_stage_boundary_contracts() -> None:
    gate = build_new_core_interface_candidate_gate(
        core_gate=_core_gate(),
        priority_ranking=_priority_ranking(),
    )

    metadata = gate["gate_metadata"]
    summary = gate["candidate_summary"]
    rows = gate["candidate_rows"]

    assert metadata["gate_id"] == GATE_ID
    assert metadata["gate_status"] == "new_core_interface_candidate_gate_ready_with_ranked_contracts"
    assert summary["candidate_count"] == 5
    assert summary["admissible_candidate_count"] == 5
    assert summary["highest_priority_candidate_id"] == "NCI1_GREY_BOX_CALIBRATION_PACKAGE"
    assert summary["highest_priority_source_env_var"] == "GREY_BOX_CALIBRATION_PACKAGE_DIR"
    assert summary["highest_priority_validation_command"] == (
        ".venv/bin/python experiments/run_grey_box_calibration_package_preflight.py"
    )
    assert summary["highest_priority_preflight_status"] == (
        "grey_box_calibration_package_preflight_not_available"
    )
    assert summary["highest_priority_preflight_pass"] is False
    assert summary["highest_priority_can_route_to_downstream_calibration"] is False
    assert summary["highest_priority_can_route_to_downstream_interface"] is False
    assert summary["highest_priority_downstream_calibration_status"] == (
        "grey_box_field_calibration_summary_not_available"
    )
    assert summary["highest_priority_downstream_interface_status"] == (
        "grey_box_field_calibration_summary_not_available"
    )
    assert summary["highest_priority_can_run_agent53_field_calibration"] is False
    assert summary["highest_priority_agent53_field_candidate_ready"] is False
    assert summary["can_generate_field_evidence"] is False
    assert summary["can_write_to_actuator"] is False
    assert summary["can_write_to_release_gate"] is False
    assert rows[0]["system_layer"] == "state_estimation_and_grey_box_physics"
    assert "influent_effluent_lab_pairs" in rows[0]["input_contract"]
    assert "mass_balance_residual_summary" in rows[0]["output_contract"]
    assert "cannot create field evidence" in rows[0]["failure_boundary"]


def test_new_core_interface_candidate_gate_consumes_grey_box_calibration_preflight() -> None:
    gate = build_new_core_interface_candidate_gate(
        core_gate=_core_gate(),
        priority_ranking=_priority_ranking(),
        grey_box_calibration_preflight={
            "package_status": "grey_box_calibration_package_ready_for_agent53_field_calibration",
            "package_preflight_pass": True,
            "matched_batch_count": 3,
            "can_route_to_agent53_field_calibration": True,
            "next_operator_action": (
                "route_GREY_BOX_CALIBRATION_PACKAGE_DIR_to_Agent53_field_calibration_preflight_consumer"
            ),
        },
        grey_box_field_calibration_summary={
            "summary_status": "grey_box_field_calibration_summary_ready_for_agent53_field_candidate",
            "can_run_agent53_field_calibration": True,
            "agent53_field_candidate_ready": True,
            "next_operator_action": (
                "run_Agent53_with_evidence_stage_field_physics_calibration_and_keep_release_gate_closed"
            ),
        },
    )

    summary = gate["candidate_summary"]
    row = gate["candidate_rows"][0]

    assert summary["highest_priority_preflight_status"] == (
        "grey_box_calibration_package_ready_for_agent53_field_calibration"
    )
    assert summary["highest_priority_preflight_pass"] is True
    assert summary["highest_priority_can_route_to_downstream_calibration"] is True
    assert summary["highest_priority_can_route_to_downstream_interface"] is True
    assert summary["highest_priority_downstream_calibration_status"] == (
        "grey_box_field_calibration_summary_ready_for_agent53_field_candidate"
    )
    assert summary["highest_priority_downstream_interface_status"] == (
        "grey_box_field_calibration_summary_ready_for_agent53_field_candidate"
    )
    assert summary["highest_priority_can_run_agent53_field_calibration"] is True
    assert summary["highest_priority_agent53_field_candidate_ready"] is True
    assert row["interface_candidate_status"] == (
        "interface_preflight_ready_for_agent53_field_calibration"
    )
    assert row["candidate_preflight_pass"] is True
    assert row["candidate_matched_batch_count"] == 3
    assert row["next_interface_action"] == (
        "run_Agent53_with_evidence_stage_field_physics_calibration_and_keep_release_gate_closed"
    )
    assert row["downstream_calibration_status"] == (
        "grey_box_field_calibration_summary_ready_for_agent53_field_candidate"
    )
    assert row["can_run_agent53_field_calibration"] is True
    assert row["agent53_field_candidate_ready"] is True
    assert row["can_write_to_actuator"] is False
    assert row["can_write_to_release_gate"] is False


def test_new_core_interface_candidate_gate_consumes_field_supported_kg_edge_preflight() -> None:
    gate = build_new_core_interface_candidate_gate(
        core_gate=_core_gate(),
        priority_ranking=[
            {
                "task_id": "P6_reasonable_knowledge_graph_upgrade",
                "title": "知识库升级为可推理 KG",
                "marginal_value_score": 0.81,
                "implementation_status": "kg_reasoning_patch_ready_needs_field_supported_edges",
                "next_experiment": "waiting for field-supported KG edges",
                "failure_boundary": "needs field-supported evidence paths",
            }
        ],
        field_supported_kg_edge_preflight={
            "package_status": "field_supported_kg_edge_package_ready_for_kg_reasoning",
            "package_preflight_pass": True,
            "matched_edge_count": 3,
            "can_route_to_kg_reasoning_field_edge_update": True,
            "next_operator_action": (
                "route_FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR_to_KG_reasoning_field_edge_preflight_consumer"
            ),
        },
    )

    summary = gate["candidate_summary"]
    row = gate["candidate_rows"][0]

    assert summary["highest_priority_candidate_id"] == "NCI5_FIELD_SUPPORTED_KG_EDGE_PACKAGE"
    assert summary["highest_priority_preflight_status"] == (
        "field_supported_kg_edge_package_ready_for_kg_reasoning"
    )
    assert summary["highest_priority_preflight_pass"] is True
    assert summary["highest_priority_can_route_to_downstream_calibration"] is False
    assert summary["highest_priority_can_route_to_downstream_interface"] is True
    assert summary["highest_priority_downstream_interface_status"] == (
        "field_supported_kg_edge_package_ready_for_kg_reasoning"
    )
    assert row["interface_candidate_status"] == (
        "interface_preflight_ready_for_kg_reasoning_field_edge_update"
    )
    assert row["candidate_matched_edge_count"] == 3
    assert row["can_route_to_downstream_interface"] is True
    assert row["downstream_calibration_status"] == (
        "not_applicable_for_field_supported_kg_edge_package"
    )
    assert row["can_write_to_actuator"] is False
    assert row["can_write_to_release_gate"] is False


def test_new_core_interface_candidate_gate_consumes_sparse_topology_installability_preflight() -> None:
    gate = build_new_core_interface_candidate_gate(
        core_gate=_core_gate(),
        priority_ranking=[
            {
                "task_id": "P1_agent48_comparable_sparse_sensor_placement",
                "title": "Agent48 可比较布点优化",
                "marginal_value_score": 0.84,
                "implementation_status": "layout_prior_ready_needs_field_topology",
                "next_experiment": "waiting for topology/installability package",
                "failure_boundary": "needs field topology, installability and node labels",
            }
        ],
        sparse_topology_installability_preflight={
            "package_status": (
                "sparse_topology_installability_package_ready_for_agent48_layout_holdout"
            ),
            "package_preflight_pass": True,
            "matched_node_count": 3,
            "can_route_to_agent48_sparse_layout_holdout": True,
            "next_operator_action": (
                "route_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR_to_Agent48_sparse_layout_holdout_consumer"
            ),
        },
    )

    summary = gate["candidate_summary"]
    row = gate["candidate_rows"][0]

    assert summary["highest_priority_candidate_id"] == (
        "NCI4_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE"
    )
    assert summary["highest_priority_preflight_status"] == (
        "sparse_topology_installability_package_ready_for_agent48_layout_holdout"
    )
    assert summary["highest_priority_preflight_pass"] is True
    assert summary["highest_priority_can_route_to_downstream_calibration"] is False
    assert summary["highest_priority_can_route_to_downstream_interface"] is True
    assert summary["highest_priority_downstream_interface_status"] == (
        "sparse_topology_installability_package_ready_for_agent48_layout_holdout"
    )
    assert row["interface_candidate_status"] == (
        "interface_preflight_ready_for_agent48_sparse_layout_holdout"
    )
    assert row["candidate_matched_node_count"] == 3
    assert row["can_route_to_downstream_interface"] is True
    assert row["downstream_calibration_status"] == (
        "not_applicable_for_sparse_topology_installability_package"
    )
    assert row["can_write_to_actuator"] is False
    assert row["can_write_to_release_gate"] is False


def test_new_core_interface_candidate_gate_consumes_field_control_replay_preflight() -> None:
    gate = build_new_core_interface_candidate_gate(
        core_gate=_core_gate(),
        priority_ranking=[
            {
                "task_id": "P3_agent49_replay_ready_offline_evaluation",
                "title": "Agent49 replay-ready 离线评估",
                "marginal_value_score": 0.85,
                "implementation_status": "control_prior_ready_needs_field_replay",
                "next_experiment": "waiting for field control replay package",
                "failure_boundary": "needs field state-action-reward replay",
            }
        ],
        field_control_replay_preflight={
            "package_status": "field_control_replay_package_ready_for_agent49_offline_replay",
            "package_preflight_pass": True,
            "matched_transition_count": 3,
            "can_route_to_agent49_field_control_replay": True,
            "next_operator_action": (
                "route_FIELD_CONTROL_REPLAY_PACKAGE_DIR_to_Agent49_Agent52_offline_control_replay_consumer"
            ),
        },
    )

    summary = gate["candidate_summary"]
    row = gate["candidate_rows"][0]

    assert summary["highest_priority_candidate_id"] == "NCI3_FIELD_CONTROL_REPLAY_PACKAGE"
    assert summary["highest_priority_preflight_status"] == (
        "field_control_replay_package_ready_for_agent49_offline_replay"
    )
    assert summary["highest_priority_preflight_pass"] is True
    assert summary["highest_priority_can_route_to_downstream_calibration"] is False
    assert summary["highest_priority_can_route_to_downstream_interface"] is True
    assert summary["highest_priority_downstream_interface_status"] == (
        "field_control_replay_package_ready_for_agent49_offline_replay"
    )
    assert row["interface_candidate_status"] == (
        "interface_preflight_ready_for_agent49_field_control_replay"
    )
    assert row["candidate_matched_transition_count"] == 3
    assert row["can_route_to_downstream_interface"] is True
    assert row["downstream_calibration_status"] == (
        "not_applicable_for_field_control_replay_package"
    )
    assert row["can_write_to_actuator"] is False
    assert row["can_write_to_release_gate"] is False


def test_new_core_interface_candidate_gate_consumes_field_missingness_replay_preflight() -> None:
    gate = build_new_core_interface_candidate_gate(
        core_gate=_core_gate(),
        priority_ranking=[
            {
                "task_id": "P5_soft_sensor_node_modality_missingness",
                "title": "软传感与缺测矩阵耦合",
                "marginal_value_score": 0.83,
                "implementation_status": "soft_sensor_contract_ready_needs_field_missingness",
                "next_experiment": "waiting for field missingness replay package",
                "failure_boundary": "needs field missingness replay",
            }
        ],
        field_missingness_replay_preflight={
            "package_status": (
                "field_missingness_replay_package_ready_for_agent54_missingness_holdout"
            ),
            "package_preflight_pass": True,
            "matched_sample_count": 3,
            "can_route_to_agent54_field_missingness_replay": True,
            "next_operator_action": (
                "route_FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR_to_Agent54_field_missingness_holdout_consumer"
            ),
        },
    )

    summary = gate["candidate_summary"]
    row = gate["candidate_rows"][0]

    assert summary["highest_priority_candidate_id"] == "NCI2_FIELD_MISSINGNESS_REPLAY_PACKAGE"
    assert summary["highest_priority_preflight_status"] == (
        "field_missingness_replay_package_ready_for_agent54_missingness_holdout"
    )
    assert summary["highest_priority_preflight_pass"] is True
    assert summary["highest_priority_can_route_to_downstream_calibration"] is False
    assert summary["highest_priority_can_route_to_downstream_interface"] is True
    assert summary["highest_priority_downstream_interface_status"] == (
        "field_missingness_replay_package_ready_for_agent54_missingness_holdout"
    )
    assert row["interface_candidate_status"] == (
        "interface_preflight_ready_for_agent54_field_missingness_replay"
    )
    assert row["candidate_matched_sample_count"] == 3
    assert row["can_route_to_downstream_interface"] is True
    assert row["downstream_calibration_status"] == (
        "not_applicable_for_field_missingness_replay_package"
    )
    assert row["can_write_to_actuator"] is False
    assert row["can_write_to_release_gate"] is False


def test_new_core_interface_candidate_gate_report_surfaces_boundaries() -> None:
    gate = build_new_core_interface_candidate_gate(
        core_gate=_core_gate(),
        priority_ranking=_priority_ranking(),
    )

    report_md = new_core_interface_candidate_gate_report_md(gate)

    assert "NCI1_GREY_BOX_CALIBRATION_PACKAGE" in report_md
    assert "GREY_BOX_CALIBRATION_PACKAGE_DIR" in report_md
    assert "can_generate_field_evidence: `False`" in report_md
    assert "can_write_to_actuator: `False`" in report_md
    assert "This gate ranks possible new core interfaces" in report_md


def test_new_core_interface_candidate_gate_inactive_before_stage_boundary() -> None:
    core_gate = _core_gate()
    core_gate["stage_decision"] = "continue_to_next_highest_value_core_action"
    core_gate["continue_expansion_allowed"] = True

    gate = build_new_core_interface_candidate_gate(
        core_gate=core_gate,
        priority_ranking=_priority_ranking(),
    )

    assert gate["gate_metadata"]["gate_status"] == (
        "new_core_interface_candidate_gate_not_at_stage_boundary"
    )
    assert gate["candidate_summary"]["highest_priority_candidate_id"] == (
        "NCI1_GREY_BOX_CALIBRATION_PACKAGE"
    )
    assert gate["boundary"]["can_resume_model_chain"] is False


def _core_gate() -> dict[str, object]:
    return {
        "stage_decision": "stop_expansion_wait_for_real_field_package_or_new_core_interface",
        "continue_expansion_allowed": False,
    }


def _priority_ranking() -> list[dict[str, object]]:
    return [
        {
            "task_id": "P4_minimal_grey_box_physics",
            "title": "灰箱物理机制最小增强",
            "marginal_value_score": 0.78,
            "implementation_status": "synthetic_grey_box_physics_prior_ready_needs_field_calibration",
            "next_experiment": "waiting for field RTD/lab/catalyst calibration",
            "failure_boundary": "needs field calibration before evidence claims",
        },
        {
            "task_id": "P5_soft_sensor_node_modality_missingness",
            "title": "软传感与缺测矩阵耦合",
            "marginal_value_score": 0.74,
            "implementation_status": "ready_needs_field_missingness",
            "next_experiment": "waiting for field missingness replay",
            "failure_boundary": "needs field holdout",
        },
        {
            "task_id": "P3_agent49_replay_ready_offline_evaluation",
            "title": "Agent49 replay-ready 离线评估",
            "marginal_value_score": 0.7,
            "implementation_status": "ready_needs_field_replay",
            "next_experiment": "waiting for field state-action-reward replay",
            "failure_boundary": "needs field replay",
        },
        {
            "task_id": "P1_agent48_comparable_sparse_sensor_placement",
            "title": "Agent48 可比较布点优化",
            "marginal_value_score": 0.66,
            "implementation_status": "ready_needs_field_topology",
            "next_experiment": "waiting for field topology and labels",
            "failure_boundary": "needs field topology",
        },
        {
            "task_id": "P6_reasonable_knowledge_graph_upgrade",
            "title": "知识库升级为可推理 KG",
            "marginal_value_score": 0.62,
            "implementation_status": "ready_needs_field_supported_edges",
            "next_experiment": "waiting for field-supported KG edges",
            "failure_boundary": "needs field-supported evidence paths",
        },
    ]
