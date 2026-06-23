from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


GATE_ID = "R8u147_new_core_interface_candidate_gate"


INTERFACE_SPECS: dict[str, dict[str, Any]] = {
    "P4_minimal_grey_box_physics": {
        "candidate_id": "NCI1_GREY_BOX_CALIBRATION_PACKAGE",
        "source_env_var": "GREY_BOX_CALIBRATION_PACKAGE_DIR",
        "system_layer": "state_estimation_and_grey_box_physics",
        "core_ability": "verifiability_and_explainability",
        "input_contract": [
            "influent_effluent_lab_pairs",
            "unit_hydraulic_retention_or_rtd_rows",
            "oxidant_or_energy_dose_rows",
            "catalyst_age_or_activity_labels",
            "matrix_inhibition_indicators",
        ],
        "output_contract": [
            "calibrated_grey_box_parameter_ranges",
            "mass_balance_residual_summary",
            "residence_time_error_summary",
            "parameter_validity_boundary",
        ],
        "validation_command": (
            ".venv/bin/python experiments/run_grey_box_calibration_package_preflight.py"
        ),
        "next_interface_action": (
            "define_GREY_BOX_CALIBRATION_PACKAGE_DIR_preflight_before_adding_more_grey_box_logic"
        ),
        "minimum_row_count": 3,
        "failure_boundary": (
            "This interface can calibrate or reject grey-box priors only after real or "
            "literature-bounded calibration rows pass preflight; it cannot create field evidence, "
            "actuator readiness or release readiness."
        ),
        "method_basis": [
            "WaterTAP-style unit model contracts",
            "QSDsan-style process/system simulation boundaries",
            "minimal degradation kinetics and HRT/RTD calibration",
        ],
    },
    "P5_soft_sensor_node_modality_missingness": {
        "candidate_id": "NCI2_FIELD_MISSINGNESS_REPLAY_PACKAGE",
        "source_env_var": "FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR",
        "system_layer": "observation_and_soft_sensor_state_estimation",
        "core_ability": "observability_and_verifiability",
        "input_contract": [
            "node_modality_time_series",
            "availability_mask",
            "time_since_last_observed_min",
            "sensor_quality_status",
            "offline_hidden_state_labels",
        ],
        "output_contract": [
            "missingness_replay_coverage",
            "masked_mae_by_hidden_state",
            "interval_coverage_under_missingness",
            "field_missingness_boundary",
        ],
        "validation_command": (
            ".venv/bin/python experiments/run_field_missingness_replay_preflight.py"
        ),
        "next_interface_action": (
            "define_FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR_preflight_before_training_new_soft_sensor_models"
        ),
        "minimum_row_count": 3,
        "failure_boundary": (
            "Synthetic dropout cannot represent real sensor fouling, low-frequency sampling or "
            "communication loss; this interface only becomes evidence after field missingness rows pass."
        ),
        "method_basis": [
            "GRU-D missingness-aware time-series modeling",
            "BRITS bidirectional imputation consistency",
            "PyPOTS-style missing-data benchmark schema",
        ],
    },
    "P3_agent49_replay_ready_offline_evaluation": {
        "candidate_id": "NCI3_FIELD_CONTROL_REPLAY_PACKAGE",
        "source_env_var": "FIELD_CONTROL_REPLAY_PACKAGE_DIR",
        "system_layer": "diagnosis_decision_and_closed_loop_execution",
        "core_ability": "controllability_and_engineering_feasibility",
        "input_contract": [
            "state_action_next_state_rows",
            "reward_component_rows",
            "operator_or_expert_action_labels",
            "actuator_latency_and_result_rows",
            "unsafe_action_or_override_events",
        ],
        "output_contract": [
            "joint_action_accuracy",
            "reward_regret",
            "unsafe_action_block_rate",
            "field_replay_boundary",
        ],
        "validation_command": ".venv/bin/python experiments/run_field_control_replay_preflight.py",
        "next_interface_action": (
            "define_FIELD_CONTROL_REPLAY_PACKAGE_DIR_preflight_before_considering_offline_RL_or_policy_relaxation"
        ),
        "minimum_row_count": 3,
        "failure_boundary": (
            "Offline replay can only evaluate candidate policies; it cannot authorize actuator writes "
            "without operator review, execution constraints and release gates."
        ),
        "method_basis": [
            "offline RL fixed-dataset evaluation",
            "conservative policy evaluation",
            "decision-tree policy distillation and rule audit",
        ],
    },
    "P1_agent48_comparable_sparse_sensor_placement": {
        "candidate_id": "NCI4_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE",
        "source_env_var": "SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR",
        "system_layer": "observation_sparse_sensing_and_topology",
        "core_ability": "observability_and_engineering_feasibility",
        "input_contract": [
            "site_topology_graph",
            "candidate_node_modality_costs",
            "installability_and_maintenance_constraints",
            "node_specific_hydraulic_delay",
            "historical_or_labeled_state_matrix",
        ],
        "output_contract": [
            "sparse_layout_feasibility_score",
            "reconstruction_gain_by_strategy",
            "weak_state_coverage_delta",
            "installability_boundary",
        ],
        "validation_command": (
            ".venv/bin/python experiments/run_sparse_topology_installability_preflight.py"
        ),
        "next_interface_action": (
            "define_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR_preflight_before_reopening_Agent48_layout_logic"
        ),
        "minimum_row_count": 3,
        "failure_boundary": (
            "Without real topology, installability and node-specific labels, sparse placement remains "
            "a design prior and cannot be presented as a deployable sensor layout."
        ),
        "method_basis": [
            "PySensors sparse placement baselines",
            "WNTR/EPANET-style graph topology and hydraulic constraints",
            "budget-aware node-modality matrix design",
        ],
    },
    "P6_reasonable_knowledge_graph_upgrade": {
        "candidate_id": "NCI5_FIELD_SUPPORTED_KG_EDGE_PACKAGE",
        "source_env_var": "FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR",
        "system_layer": "mechanism_evidence_and_knowledge_graph",
        "core_ability": "explainability_and_verifiability",
        "input_contract": [
            "pollutant_material_condition_edges",
            "source_basis_rows",
            "field_supported_edge_rows",
            "failure_boundary_annotations",
            "claim_or_action_constraint_links",
        ],
        "output_contract": [
            "field_supported_edge_ratio",
            "evidence_path_traceability",
            "constraint_hit_rate",
            "unsupported_edge_boundary",
        ],
        "validation_command": ".venv/bin/python experiments/run_field_supported_kg_edge_preflight.py",
        "next_interface_action": (
            "define_FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR_preflight_before_expanding_KG_claims"
        ),
        "minimum_row_count": 3,
        "failure_boundary": (
            "Literature KG edges can guide priors and explanations; only field-supported edges can "
            "upgrade site-specific claims or control boundaries."
        ),
        "method_basis": [
            "Scientific Knowledge Graph evidence paths",
            "claim verification workflow",
            "source_basis and failure-boundary governance",
        ],
    },
}


def build_new_core_interface_candidate_gate(
    *,
    core_gate: dict[str, Any],
    priority_ranking: list[dict[str, Any]],
    grey_box_calibration_preflight: dict[str, Any] | None = None,
    grey_box_field_calibration_summary: dict[str, Any] | None = None,
    field_supported_kg_edge_preflight: dict[str, Any] | None = None,
    sparse_topology_installability_preflight: dict[str, Any] | None = None,
    field_control_replay_preflight: dict[str, Any] | None = None,
    field_missingness_replay_preflight: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Convert the generic NEW_CORE_INTERFACE escape hatch into ranked contracts."""

    candidate_rows = _candidate_rows(
        priority_ranking,
        grey_box_calibration_preflight=grey_box_calibration_preflight or {},
        grey_box_field_calibration_summary=grey_box_field_calibration_summary or {},
        field_supported_kg_edge_preflight=field_supported_kg_edge_preflight or {},
        sparse_topology_installability_preflight=sparse_topology_installability_preflight or {},
        field_control_replay_preflight=field_control_replay_preflight or {},
        field_missingness_replay_preflight=field_missingness_replay_preflight or {},
    )
    admissible_rows = [
        row
        for row in candidate_rows
        if _is_admissible_or_ready_status(str(row["interface_candidate_status"]))
    ]
    highest = admissible_rows[0] if admissible_rows else {}
    stage_decision = str(core_gate.get("stage_decision", ""))
    internal_expansion_allowed = bool(core_gate.get("continue_expansion_allowed", False))
    gate_status = _gate_status(
        stage_decision=stage_decision,
        internal_expansion_allowed=internal_expansion_allowed,
        admissible_count=len(admissible_rows),
    )
    return {
        "gate_metadata": {
            "gate_id": GATE_ID,
            "gate_status": gate_status,
            "gate_role": "new_core_interface_candidate_queue",
            "created_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "source_core_gate_stage_decision": stage_decision,
            "source_core_gate_continue_expansion_allowed": internal_expansion_allowed,
        },
        "candidate_summary": {
            "candidate_count": len(candidate_rows),
            "admissible_candidate_count": len(admissible_rows),
            "highest_priority_candidate_id": str(highest.get("candidate_id", "")),
            "highest_priority_task_id": str(highest.get("task_id", "")),
            "highest_priority_source_env_var": str(highest.get("source_env_var", "")),
            "highest_priority_system_layer": str(highest.get("system_layer", "")),
            "highest_priority_core_ability": str(highest.get("core_ability", "")),
            "highest_priority_validation_command": str(highest.get("validation_command", "")),
            "highest_priority_next_interface_action": str(
                highest.get("next_interface_action", "")
            ),
            "highest_priority_preflight_status": str(
                highest.get("candidate_preflight_status", "")
            ),
            "highest_priority_preflight_pass": bool(
                highest.get("candidate_preflight_pass", False)
            ),
            "highest_priority_can_route_to_downstream_calibration": bool(
                highest.get("can_route_to_downstream_calibration", False)
            ),
            "highest_priority_can_route_to_downstream_interface": bool(
                highest.get("can_route_to_downstream_interface", False)
            ),
            "highest_priority_downstream_calibration_status": str(
                highest.get("downstream_calibration_status", "")
            ),
            "highest_priority_downstream_interface_status": str(
                highest.get("downstream_interface_status", "")
            ),
            "highest_priority_can_run_agent53_field_calibration": bool(
                highest.get("can_run_agent53_field_calibration", False)
            ),
            "highest_priority_agent53_field_candidate_ready": bool(
                highest.get("agent53_field_candidate_ready", False)
            ),
            "can_resume_model_chain": False,
            "can_generate_field_evidence": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        },
        "candidate_rows": candidate_rows,
        "selection_rules": {
            "rank_source": "Agent50 priority_ranking filtered through INTERFACE_SPECS",
            "admissible_requires": [
                "current core gate is at stop_expansion_wait_for_real_field_package_or_new_core_interface",
                "candidate maps to a seven-layer system interface",
                "candidate defines source env var, input contract, output contract, validation command and failure boundary",
                "candidate does not fabricate field evidence, actuator readiness or release readiness",
            ],
            "do_not_expand_when": [
                "the candidate only adds synthetic detail without a new contract",
                "the candidate bypasses field replay, holdout, source_basis or operator review",
                "the candidate can be satisfied by an existing external package channel",
            ],
        },
        "boundary": {
            "candidate_gate_only": True,
            "can_generate_field_evidence": False,
            "can_resume_model_chain": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "boundary_statement": (
                "This gate ranks possible new core interfaces. It does not implement the interface, "
                "does not validate field data and does not authorize any control or release action."
            ),
        },
    }


def new_core_interface_candidate_gate_report_md(gate: dict[str, Any]) -> str:
    metadata = gate["gate_metadata"]
    summary = gate["candidate_summary"]
    lines = [
        "# New Core Interface Candidate Gate",
        "",
        "## Role",
        "",
        (
            "This gate turns the generic `NEW_CORE_INTERFACE` stage-boundary option into a "
            "ranked list of concrete, testable interface contracts. It is a routing and "
            "architecture gate, not a field-validation result."
        ),
        "",
        "## Gate State",
        "",
        f"- gate_id: `{metadata['gate_id']}`",
        f"- gate_status: `{metadata['gate_status']}`",
        f"- stage_decision: `{metadata['source_core_gate_stage_decision']}`",
        f"- candidate_count: `{summary['candidate_count']}`",
        f"- admissible_candidate_count: `{summary['admissible_candidate_count']}`",
        f"- highest_priority_candidate_id: `{summary['highest_priority_candidate_id']}`",
        f"- highest_priority_source_env_var: `{summary['highest_priority_source_env_var']}`",
        f"- highest_priority_validation_command: `{summary['highest_priority_validation_command']}`",
        f"- highest_priority_preflight_status: `{summary['highest_priority_preflight_status']}`",
        f"- highest_priority_preflight_pass: `{summary['highest_priority_preflight_pass']}`",
        (
            "- highest_priority_can_route_to_downstream_calibration: "
            f"`{summary['highest_priority_can_route_to_downstream_calibration']}`"
        ),
        (
            "- highest_priority_can_route_to_downstream_interface: "
            f"`{summary['highest_priority_can_route_to_downstream_interface']}`"
        ),
        (
            "- highest_priority_downstream_calibration_status: "
            f"`{summary['highest_priority_downstream_calibration_status']}`"
        ),
        (
            "- highest_priority_downstream_interface_status: "
            f"`{summary['highest_priority_downstream_interface_status']}`"
        ),
        (
            "- highest_priority_can_run_agent53_field_calibration: "
            f"`{summary['highest_priority_can_run_agent53_field_calibration']}`"
        ),
        (
            "- highest_priority_agent53_field_candidate_ready: "
            f"`{summary['highest_priority_agent53_field_candidate_ready']}`"
        ),
        f"- can_generate_field_evidence: `{summary['can_generate_field_evidence']}`",
        f"- can_write_to_actuator: `{summary['can_write_to_actuator']}`",
        f"- can_write_to_release_gate: `{summary['can_write_to_release_gate']}`",
        "",
        "## Candidate Rows",
        "",
        (
            "| order | candidate | task | status | preflight | env var | layer | ability | "
            "minimum rows | next interface action |"
        ),
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in gate["candidate_rows"]:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                row["priority_order"],
                row["candidate_id"],
                row["task_id"],
                row["interface_candidate_status"],
                row["candidate_preflight_status"],
                row["source_env_var"],
                row["system_layer"],
                row["core_ability"],
                row["minimum_row_count"],
                row["next_interface_action"],
            )
        )
    lines.extend(["", "## Boundary", "", gate["boundary"]["boundary_statement"], ""])
    return "\n".join(lines)


def _candidate_rows(
    priority_ranking: list[dict[str, Any]],
    *,
    grey_box_calibration_preflight: dict[str, Any],
    grey_box_field_calibration_summary: dict[str, Any],
    field_supported_kg_edge_preflight: dict[str, Any],
    sparse_topology_installability_preflight: dict[str, Any],
    field_control_replay_preflight: dict[str, Any],
    field_missingness_replay_preflight: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(priority_ranking, start=1):
        if not isinstance(item, dict):
            continue
        task_id = str(item.get("task_id", ""))
        spec = INTERFACE_SPECS.get(task_id)
        if not spec:
            continue
        preflight = _candidate_preflight_context(
            spec["candidate_id"],
            grey_box_calibration_preflight=grey_box_calibration_preflight,
            grey_box_field_calibration_summary=grey_box_field_calibration_summary,
            field_supported_kg_edge_preflight=field_supported_kg_edge_preflight,
            sparse_topology_installability_preflight=sparse_topology_installability_preflight,
            field_control_replay_preflight=field_control_replay_preflight,
            field_missingness_replay_preflight=field_missingness_replay_preflight,
        )
        rows.append(
            {
                "priority_order": index,
                "task_id": task_id,
                "title": str(item.get("title", "")),
                "marginal_value_score": float(item.get("marginal_value_score", 0.0) or 0.0),
                "implementation_status": str(item.get("implementation_status", "")),
                "next_experiment": str(item.get("next_experiment", "")),
                "interface_candidate_status": _candidate_status(item, preflight),
                "candidate_id": spec["candidate_id"],
                "source_env_var": spec["source_env_var"],
                "system_layer": spec["system_layer"],
                "core_ability": spec["core_ability"],
                "input_contract": list(spec["input_contract"]),
                "output_contract": list(spec["output_contract"]),
                "validation_command": spec["validation_command"],
                "next_interface_action": (
                    preflight["candidate_next_operator_action"]
                    or spec["next_interface_action"]
                ),
                "minimum_row_count": int(spec["minimum_row_count"]),
                "failure_boundary": spec["failure_boundary"],
                "method_basis": list(spec["method_basis"]),
                **preflight,
                "can_generate_field_evidence": False,
                "can_resume_model_chain": False,
                "can_write_to_actuator": False,
                "can_write_to_release_gate": False,
            }
        )
    return rows


def _candidate_preflight_context(
    candidate_id: str,
    *,
    grey_box_calibration_preflight: dict[str, Any],
    grey_box_field_calibration_summary: dict[str, Any],
    field_supported_kg_edge_preflight: dict[str, Any],
    sparse_topology_installability_preflight: dict[str, Any],
    field_control_replay_preflight: dict[str, Any],
    field_missingness_replay_preflight: dict[str, Any],
) -> dict[str, Any]:
    if candidate_id == "NCI5_FIELD_SUPPORTED_KG_EDGE_PACKAGE":
        return _field_supported_kg_edge_preflight_context(field_supported_kg_edge_preflight)
    if candidate_id == "NCI4_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE":
        return _sparse_topology_installability_preflight_context(
            sparse_topology_installability_preflight
        )
    if candidate_id == "NCI3_FIELD_CONTROL_REPLAY_PACKAGE":
        return _field_control_replay_preflight_context(field_control_replay_preflight)
    if candidate_id == "NCI2_FIELD_MISSINGNESS_REPLAY_PACKAGE":
        return _field_missingness_replay_preflight_context(field_missingness_replay_preflight)
    if candidate_id != "NCI1_GREY_BOX_CALIBRATION_PACKAGE":
        return {
            "candidate_preflight_status": "interface_preflight_not_implemented_yet",
            "candidate_preflight_pass": False,
            "candidate_matched_batch_count": 0,
            "candidate_matched_node_count": 0,
            "candidate_matched_edge_count": 0,
            "candidate_matched_transition_count": 0,
            "candidate_matched_sample_count": 0,
            "can_route_to_downstream_calibration": False,
            "can_route_to_downstream_interface": False,
            "downstream_calibration_status": "downstream_calibration_not_implemented_yet",
            "downstream_interface_status": "downstream_interface_not_implemented_yet",
            "can_run_agent53_field_calibration": False,
            "agent53_field_candidate_ready": False,
            "candidate_ready_status": "interface_preflight_ready_for_downstream_interface",
            "candidate_next_operator_action": "",
        }
    if not grey_box_calibration_preflight:
        return {
            "candidate_preflight_status": "grey_box_calibration_package_preflight_not_available",
            "candidate_preflight_pass": False,
            "candidate_matched_batch_count": 0,
            "candidate_matched_node_count": 0,
            "candidate_matched_edge_count": 0,
            "candidate_matched_transition_count": 0,
            "candidate_matched_sample_count": 0,
            "can_route_to_downstream_calibration": False,
            "can_route_to_downstream_interface": False,
            "downstream_calibration_status": "grey_box_field_calibration_summary_not_available",
            "downstream_interface_status": "grey_box_field_calibration_summary_not_available",
            "can_run_agent53_field_calibration": False,
            "agent53_field_candidate_ready": False,
            "candidate_ready_status": "interface_preflight_ready_for_agent53_field_calibration",
            "candidate_next_operator_action": "",
        }
    downstream_status = str(
        grey_box_field_calibration_summary.get(
            "summary_status",
            "grey_box_field_calibration_summary_not_available",
        )
    )
    return {
        "candidate_preflight_status": str(
            grey_box_calibration_preflight.get(
                "package_status",
                "grey_box_calibration_package_preflight_status_missing",
            )
        ),
        "candidate_preflight_pass": bool(
            grey_box_calibration_preflight.get("package_preflight_pass", False)
        ),
        "candidate_matched_batch_count": int(
            grey_box_calibration_preflight.get("matched_batch_count", 0) or 0
        ),
        "candidate_matched_node_count": 0,
        "candidate_matched_edge_count": 0,
        "candidate_matched_transition_count": 0,
        "candidate_matched_sample_count": 0,
        "can_route_to_downstream_calibration": bool(
            grey_box_calibration_preflight.get(
                "can_route_to_agent53_field_calibration",
                False,
            )
        ),
        "can_route_to_downstream_interface": bool(
            grey_box_calibration_preflight.get(
                "can_route_to_agent53_field_calibration",
                False,
            )
        ),
        "downstream_calibration_status": downstream_status,
        "downstream_interface_status": downstream_status,
        "can_run_agent53_field_calibration": bool(
            grey_box_field_calibration_summary.get(
                "can_run_agent53_field_calibration",
                False,
            )
        ),
        "agent53_field_candidate_ready": bool(
            grey_box_field_calibration_summary.get(
                "agent53_field_candidate_ready",
                False,
            )
        ),
        "candidate_next_operator_action": str(
            grey_box_field_calibration_summary.get(
                "next_operator_action",
                grey_box_calibration_preflight.get("next_operator_action", ""),
            )
        ),
        "candidate_ready_status": "interface_preflight_ready_for_agent53_field_calibration",
    }


def _field_supported_kg_edge_preflight_context(
    field_supported_kg_edge_preflight: dict[str, Any],
) -> dict[str, Any]:
    if not field_supported_kg_edge_preflight:
        return {
            "candidate_preflight_status": "field_supported_kg_edge_package_preflight_not_available",
            "candidate_preflight_pass": False,
            "candidate_matched_batch_count": 0,
            "candidate_matched_node_count": 0,
            "candidate_matched_edge_count": 0,
            "candidate_matched_transition_count": 0,
            "candidate_matched_sample_count": 0,
            "can_route_to_downstream_calibration": False,
            "can_route_to_downstream_interface": False,
            "downstream_calibration_status": "not_applicable_for_field_supported_kg_edge_package",
            "downstream_interface_status": "field_supported_kg_edge_package_preflight_not_available",
            "can_run_agent53_field_calibration": False,
            "agent53_field_candidate_ready": False,
            "candidate_ready_status": "interface_preflight_ready_for_kg_reasoning_field_edge_update",
            "candidate_next_operator_action": "",
        }
    can_route = bool(
        field_supported_kg_edge_preflight.get(
            "can_route_to_kg_reasoning_field_edge_update",
            False,
        )
    )
    return {
        "candidate_preflight_status": str(
            field_supported_kg_edge_preflight.get(
                "package_status",
                "field_supported_kg_edge_package_preflight_status_missing",
            )
        ),
        "candidate_preflight_pass": bool(
            field_supported_kg_edge_preflight.get("package_preflight_pass", False)
        ),
        "candidate_matched_batch_count": 0,
        "candidate_matched_node_count": 0,
        "candidate_matched_edge_count": int(
            field_supported_kg_edge_preflight.get("matched_edge_count", 0) or 0
        ),
        "candidate_matched_transition_count": 0,
        "candidate_matched_sample_count": 0,
        "can_route_to_downstream_calibration": False,
        "can_route_to_downstream_interface": can_route,
        "downstream_calibration_status": "not_applicable_for_field_supported_kg_edge_package",
        "downstream_interface_status": str(
            field_supported_kg_edge_preflight.get(
                "package_status",
                "field_supported_kg_edge_package_preflight_status_missing",
            )
        ),
        "can_run_agent53_field_calibration": False,
        "agent53_field_candidate_ready": False,
        "candidate_ready_status": "interface_preflight_ready_for_kg_reasoning_field_edge_update",
        "candidate_next_operator_action": str(
            field_supported_kg_edge_preflight.get("next_operator_action", "")
        ),
    }


def _sparse_topology_installability_preflight_context(
    sparse_topology_installability_preflight: dict[str, Any],
) -> dict[str, Any]:
    if not sparse_topology_installability_preflight:
        return {
            "candidate_preflight_status": "sparse_topology_installability_package_preflight_not_available",
            "candidate_preflight_pass": False,
            "candidate_matched_batch_count": 0,
            "candidate_matched_node_count": 0,
            "candidate_matched_edge_count": 0,
            "candidate_matched_transition_count": 0,
            "candidate_matched_sample_count": 0,
            "can_route_to_downstream_calibration": False,
            "can_route_to_downstream_interface": False,
            "downstream_calibration_status": "not_applicable_for_sparse_topology_installability_package",
            "downstream_interface_status": "sparse_topology_installability_package_preflight_not_available",
            "can_run_agent53_field_calibration": False,
            "agent53_field_candidate_ready": False,
            "candidate_ready_status": "interface_preflight_ready_for_agent48_sparse_layout_holdout",
            "candidate_next_operator_action": "",
        }
    can_route = bool(
        sparse_topology_installability_preflight.get(
            "can_route_to_agent48_sparse_layout_holdout",
            False,
        )
    )
    return {
        "candidate_preflight_status": str(
            sparse_topology_installability_preflight.get(
                "package_status",
                "sparse_topology_installability_package_preflight_status_missing",
            )
        ),
        "candidate_preflight_pass": bool(
            sparse_topology_installability_preflight.get("package_preflight_pass", False)
        ),
        "candidate_matched_batch_count": 0,
        "candidate_matched_node_count": int(
            sparse_topology_installability_preflight.get("matched_node_count", 0) or 0
        ),
        "candidate_matched_edge_count": 0,
        "candidate_matched_transition_count": 0,
        "candidate_matched_sample_count": 0,
        "can_route_to_downstream_calibration": False,
        "can_route_to_downstream_interface": can_route,
        "downstream_calibration_status": "not_applicable_for_sparse_topology_installability_package",
        "downstream_interface_status": str(
            sparse_topology_installability_preflight.get(
                "package_status",
                "sparse_topology_installability_package_preflight_status_missing",
            )
        ),
        "can_run_agent53_field_calibration": False,
        "agent53_field_candidate_ready": False,
        "candidate_ready_status": "interface_preflight_ready_for_agent48_sparse_layout_holdout",
        "candidate_next_operator_action": str(
            sparse_topology_installability_preflight.get("next_operator_action", "")
        ),
    }


def _field_control_replay_preflight_context(
    field_control_replay_preflight: dict[str, Any],
) -> dict[str, Any]:
    if not field_control_replay_preflight:
        return {
            "candidate_preflight_status": "field_control_replay_package_preflight_not_available",
            "candidate_preflight_pass": False,
            "candidate_matched_batch_count": 0,
            "candidate_matched_node_count": 0,
            "candidate_matched_edge_count": 0,
            "candidate_matched_transition_count": 0,
            "candidate_matched_sample_count": 0,
            "can_route_to_downstream_calibration": False,
            "can_route_to_downstream_interface": False,
            "downstream_calibration_status": "not_applicable_for_field_control_replay_package",
            "downstream_interface_status": "field_control_replay_package_preflight_not_available",
            "can_run_agent53_field_calibration": False,
            "agent53_field_candidate_ready": False,
            "candidate_ready_status": "interface_preflight_ready_for_agent49_field_control_replay",
            "candidate_next_operator_action": "",
        }
    can_route = bool(
        field_control_replay_preflight.get(
            "can_route_to_agent49_field_control_replay",
            False,
        )
    )
    return {
        "candidate_preflight_status": str(
            field_control_replay_preflight.get(
                "package_status",
                "field_control_replay_package_preflight_status_missing",
            )
        ),
        "candidate_preflight_pass": bool(
            field_control_replay_preflight.get("package_preflight_pass", False)
        ),
        "candidate_matched_batch_count": 0,
        "candidate_matched_node_count": 0,
        "candidate_matched_edge_count": 0,
        "candidate_matched_transition_count": int(
            field_control_replay_preflight.get("matched_transition_count", 0) or 0
        ),
        "candidate_matched_sample_count": 0,
        "can_route_to_downstream_calibration": False,
        "can_route_to_downstream_interface": can_route,
        "downstream_calibration_status": "not_applicable_for_field_control_replay_package",
        "downstream_interface_status": str(
            field_control_replay_preflight.get(
                "package_status",
                "field_control_replay_package_preflight_status_missing",
            )
        ),
        "can_run_agent53_field_calibration": False,
        "agent53_field_candidate_ready": False,
        "candidate_ready_status": "interface_preflight_ready_for_agent49_field_control_replay",
        "candidate_next_operator_action": str(
            field_control_replay_preflight.get("next_operator_action", "")
        ),
    }


def _field_missingness_replay_preflight_context(
    field_missingness_replay_preflight: dict[str, Any],
) -> dict[str, Any]:
    if not field_missingness_replay_preflight:
        return {
            "candidate_preflight_status": "field_missingness_replay_package_preflight_not_available",
            "candidate_preflight_pass": False,
            "candidate_matched_batch_count": 0,
            "candidate_matched_node_count": 0,
            "candidate_matched_edge_count": 0,
            "candidate_matched_transition_count": 0,
            "candidate_matched_sample_count": 0,
            "can_route_to_downstream_calibration": False,
            "can_route_to_downstream_interface": False,
            "downstream_calibration_status": "not_applicable_for_field_missingness_replay_package",
            "downstream_interface_status": "field_missingness_replay_package_preflight_not_available",
            "can_run_agent53_field_calibration": False,
            "agent53_field_candidate_ready": False,
            "candidate_ready_status": "interface_preflight_ready_for_agent54_field_missingness_replay",
            "candidate_next_operator_action": "",
        }
    can_route = bool(
        field_missingness_replay_preflight.get(
            "can_route_to_agent54_field_missingness_replay",
            False,
        )
    )
    return {
        "candidate_preflight_status": str(
            field_missingness_replay_preflight.get(
                "package_status",
                "field_missingness_replay_package_preflight_status_missing",
            )
        ),
        "candidate_preflight_pass": bool(
            field_missingness_replay_preflight.get("package_preflight_pass", False)
        ),
        "candidate_matched_batch_count": 0,
        "candidate_matched_node_count": 0,
        "candidate_matched_edge_count": 0,
        "candidate_matched_transition_count": 0,
        "candidate_matched_sample_count": int(
            field_missingness_replay_preflight.get("matched_sample_count", 0) or 0
        ),
        "can_route_to_downstream_calibration": False,
        "can_route_to_downstream_interface": can_route,
        "downstream_calibration_status": "not_applicable_for_field_missingness_replay_package",
        "downstream_interface_status": str(
            field_missingness_replay_preflight.get(
                "package_status",
                "field_missingness_replay_package_preflight_status_missing",
            )
        ),
        "can_run_agent53_field_calibration": False,
        "agent53_field_candidate_ready": False,
        "candidate_ready_status": "interface_preflight_ready_for_agent54_field_missingness_replay",
        "candidate_next_operator_action": str(
            field_missingness_replay_preflight.get("next_operator_action", "")
        ),
    }


def _candidate_status(item: dict[str, Any], preflight: dict[str, Any]) -> str:
    if preflight.get("candidate_preflight_pass"):
        return str(
            preflight.get(
                "candidate_ready_status",
                "interface_preflight_ready_for_downstream_interface",
            )
        )
    preflight_status = str(preflight.get("candidate_preflight_status", ""))
    if preflight_status and preflight_status != "interface_preflight_not_implemented_yet":
        return "admissible_contract_candidate_waiting_for_interface_preflight"
    text = " ".join(
        str(item.get(key, ""))
        for key in ["implementation_status", "next_experiment", "failure_boundary"]
    ).lower()
    if "waiting_on_real_field_package_external_blocker" in text:
        return "defer_existing_external_package_channel_first"
    if any(marker in text for marker in ["needs field", "field_", "field ", "holdout", "calibration"]):
        return "admissible_contract_candidate_waiting_for_interface_preflight"
    return "defer_until_priority_item_exposes_external_validation_need"


def _is_admissible_or_ready_status(status: str) -> bool:
    return status.startswith("admissible") or status.startswith("interface_preflight_ready")


def _gate_status(
    *,
    stage_decision: str,
    internal_expansion_allowed: bool,
    admissible_count: int,
) -> str:
    if stage_decision != "stop_expansion_wait_for_real_field_package_or_new_core_interface":
        return "new_core_interface_candidate_gate_not_at_stage_boundary"
    if internal_expansion_allowed:
        return "new_core_interface_candidate_gate_internal_expansion_still_allowed"
    if admissible_count > 0:
        return "new_core_interface_candidate_gate_ready_with_ranked_contracts"
    return "new_core_interface_candidate_gate_no_admissible_contract"
