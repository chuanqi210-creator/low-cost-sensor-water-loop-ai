from __future__ import annotations

from typing import Any


TARGET_HIDDEN_STATE = "catalyst_activity"


def build_observation_response_bridge(
    *,
    observation_contract_metrics: dict[str, Any],
    response_template: dict[str, Any],
    response_submission_packet: dict[str, Any],
    catalyst_holdout_summary: dict[str, Any],
    soft_sensor_matrix_metrics: dict[str, Any],
) -> dict[str, Any]:
    """Map the observation weak axis to the field-activation response rows."""

    readiness = _dict(observation_contract_metrics.get("readiness"))
    r2_fv4 = _requirement(
        observation_contract_metrics,
        "R2_FV4_agent48_hidden_state_requirement_patch",
    )
    target_states = _target_hidden_states(readiness, r2_fv4)
    response_rows = [
        row
        for row in _list_of_dicts(response_template.get("evidence_rows"))
        if str(row.get("hidden_state", "")) in target_states
    ]
    row_mappings = [_response_row_mapping(row, r2_fv4) for row in response_rows]
    role_coverage = _role_coverage(row_mappings)
    minimum_batch_count = int(r2_fv4.get("minimum_matched_batch_count", 3) or 3)
    ready = bool(response_rows) and role_coverage["coverage_rate"] >= 1.0
    catalyst_ready = bool(catalyst_holdout_summary.get("ready_for_agent51_validation", False))
    can_route_to_agent51 = ready and catalyst_ready
    status = _bridge_status(
        ready=ready,
        can_route_to_agent51=can_route_to_agent51,
        response_submission_packet=response_submission_packet,
    )
    return {
        "bridge_id": "R8u109_observation_response_bridge",
        "bridge_type": "observation_contract_to_field_activation_response_bridge",
        "bridge_status": status,
        "target_hidden_states": target_states,
        "primary_target_hidden_state": TARGET_HIDDEN_STATE,
        "source_observation_contract_status": readiness.get("observation_contract_status", "unknown"),
        "source_response_template_id": response_template.get("template_id", "unknown_response_template"),
        "source_submission_packet_id": response_submission_packet.get("packet_id", "unknown_submission_packet"),
        "response_submission_packet_status": response_submission_packet.get("packet_status", "unknown"),
        "response_submission_next_operator_action": response_submission_packet.get("next_operator_action", ""),
        "r2_fv4_requirement": {
            "requirement_id": r2_fv4.get("requirement_id", "R2_FV4_agent48_hidden_state_requirement_patch"),
            "needed_for": r2_fv4.get("needed_for", ""),
            "minimum_matched_batch_count": minimum_batch_count,
            "required_tables": _string_list(r2_fv4.get("required_tables")),
            "required_signals_or_fields": _string_list(r2_fv4.get("required_signals_or_fields")),
            "pressure_headloss_candidate_ids": _string_list(r2_fv4.get("pressure_headloss_candidate_ids")),
        },
        "agent51_holdout_context": {
            "summary_status": catalyst_holdout_summary.get("field_proxy_holdout_summary_status", "unknown"),
            "ready_for_agent51_validation": catalyst_ready,
            "field_validation_pass": bool(catalyst_holdout_summary.get("field_validation_pass", False)),
            "scoreable_batch_count": int(catalyst_holdout_summary.get("scoreable_batch_count", 0) or 0),
            "minimum_batch_count": int(catalyst_holdout_summary.get("minimum_batch_count", minimum_batch_count) or minimum_batch_count),
            "required_node_signals": _string_list(catalyst_holdout_summary.get("required_node_signals")),
            "missing_required_signals": _string_list(catalyst_holdout_summary.get("missing_required_signals")),
            "can_relax_agent49_catalyst_uncertainty_block": bool(
                catalyst_holdout_summary.get("can_relax_agent49_catalyst_uncertainty_block", False)
            ),
        },
        "agent54_soft_sensor_context": _soft_sensor_context(soft_sensor_matrix_metrics),
        "response_row_count": len(response_rows),
        "mapped_response_row_count": sum(1 for row in row_mappings if row["mapped_to_observation_requirement"]),
        "required_role_count": role_coverage["required_role_count"],
        "mapped_role_count": role_coverage["mapped_role_count"],
        "required_role_coverage_rate": role_coverage["coverage_rate"],
        "missing_required_roles": role_coverage["missing_roles"],
        "priority_response_rows": sorted(
            row_mappings,
            key=lambda row: (row["priority_rank"], row["response_row_id"]),
        ),
        "operator_priority_fill_plan": _operator_priority_fill_plan(
            row_mappings,
            minimum_batch_count=minimum_batch_count,
        ),
        "can_route_to_agent51_field_proxy_holdout": can_route_to_agent51,
        "can_relax_agent49_catalyst_uncertainty_block": bool(
            catalyst_holdout_summary.get("can_relax_agent49_catalyst_uncertainty_block", False)
        ),
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "batch_alignment_policy": (
            "The response rows identify which field evidence must be submitted first, but batch alignment is "
            f"proved only when at least {minimum_batch_count} real field batch_id values are matched across "
            "node_modality_sensor_timeseries, offline_lab_results, campaign_operation_log and "
            "site_topology_or_bed_geometry. A filled response JSON alone is not field validation."
        ),
        "no_write_boundary": (
            "This bridge only prioritizes existing observation-contract evidence rows inside the field activation "
            "response template. It does not create field evidence, does not validate catalyst activity, does not "
            "relax Agent49 guardrails, and cannot write actuator policy or release gate."
        ),
    }


def _bridge_status(
    *,
    ready: bool,
    can_route_to_agent51: bool,
    response_submission_packet: dict[str, Any],
) -> str:
    if can_route_to_agent51:
        return "observation_response_bridge_ready_for_agent51_field_proxy_holdout"
    if ready:
        status = str(response_submission_packet.get("packet_status", ""))
        if status == "field_activation_response_submission_packet_response_ready_for_package_assembly":
            return "observation_response_bridge_waiting_for_materialized_field_package"
        return "observation_response_bridge_ready_for_priority_field_response_fill"
    return "observation_response_bridge_blocked_by_missing_target_response_rows"


def _response_row_mapping(row: dict[str, Any], r2_fv4: dict[str, Any]) -> dict[str, Any]:
    evidence = str(row.get("required_evidence", ""))
    table_name = str(row.get("table_name", ""))
    field_name = str(row.get("field_name", ""))
    role = _row_role(evidence=evidence, table_name=table_name, field_name=field_name)
    priority_rank = {
        "pressure_headloss_proxy": 1,
        "catalyst_activity_label": 1,
        "regeneration_event": 1,
        "hydraulic_normalizer": 1,
        "bed_outlet_uv254_proxy": 2,
        "bed_outlet_orp_proxy": 2,
    }.get(role, 9)
    return {
        "response_row_id": row.get("response_row_id", ""),
        "hidden_state": row.get("hidden_state", ""),
        "required_evidence": evidence,
        "evidence_channel": row.get("evidence_channel", ""),
        "table_name": table_name,
        "field_name": field_name,
        "observation_role": role,
        "priority": "P1" if priority_rank == 1 else "P2",
        "priority_rank": priority_rank,
        "mapped_to_observation_requirement": role in _required_roles(),
        "source_requirement_id": r2_fv4.get("requirement_id", "R2_FV4_agent48_hidden_state_requirement_patch"),
        "downstream_consumers": [
            "Agent51 catalyst proxy field holdout",
            "Agent49 catalyst uncertainty guardrail",
            "Agent54 pressure/headloss soft-sensor schema",
        ],
        "field_value_boundary": (
            "Fill with real data_origin=field provenance and evidence references only; TODO/template/sample values "
            "keep the row blocked."
        ),
    }


def _row_role(*, evidence: str, table_name: str, field_name: str) -> str:
    text = f"{evidence}.{table_name}.{field_name}".lower()
    if "pressure_drop" in text or "headloss" in text:
        return "pressure_headloss_proxy"
    if "catalyst_activity" in text and "offline_lab_results" in text:
        return "catalyst_activity_label"
    if "regeneration_event" in text:
        return "regeneration_event"
    if "nominal_hrt" in text or "bed_geometry" in text:
        return "hydraulic_normalizer"
    if "uv254" in text:
        return "bed_outlet_uv254_proxy"
    if "orp" in text:
        return "bed_outlet_orp_proxy"
    return "supporting_observation_evidence"


def _role_coverage(row_mappings: list[dict[str, Any]]) -> dict[str, Any]:
    roles = _required_roles()
    mapped = {str(row["observation_role"]) for row in row_mappings}
    missing = sorted(role for role in roles if role not in mapped)
    return {
        "required_role_count": len(roles),
        "mapped_role_count": len(roles) - len(missing),
        "coverage_rate": round((len(roles) - len(missing)) / max(1, len(roles)), 3),
        "missing_roles": missing,
    }


def _required_roles() -> set[str]:
    return {
        "bed_outlet_uv254_proxy",
        "bed_outlet_orp_proxy",
        "pressure_headloss_proxy",
        "catalyst_activity_label",
        "regeneration_event",
        "hydraulic_normalizer",
    }


def _operator_priority_fill_plan(
    row_mappings: list[dict[str, Any]],
    *,
    minimum_batch_count: int,
) -> list[dict[str, Any]]:
    return [
        {
            "step_id": "R8U109_FILL_CATALYST_OBSERVATION_RESPONSE_ROWS",
            "priority": "P1",
            "target_response_row_ids": [
                str(row["response_row_id"])
                for row in sorted(row_mappings, key=lambda item: (item["priority_rank"], item["response_row_id"]))
            ],
            "minimum_matched_batch_count": minimum_batch_count,
            "acceptance": (
                "Fill these response rows with real field provenance and references to downstream package tables; "
                "then run FIELD_ACTIVATION_RESPONSE_PATH=/path/to/filled_response.json "
                ".venv/bin/python experiments/run_field_activation_matrix.py."
            ),
        },
        {
            "step_id": "R8U109_KEEP_CATALYST_GUARDRAIL_UNTIL_AGENT51_HOLDOUT",
            "priority": "P1",
            "target_response_row_ids": [
                str(row["response_row_id"])
                for row in row_mappings
                if row["observation_role"] in {"pressure_headloss_proxy", "catalyst_activity_label", "regeneration_event"}
            ],
            "minimum_matched_batch_count": minimum_batch_count,
            "acceptance": (
                "Agent49 catalyst guardrail stays active until Agent51 scores matched pressure/headloss, "
                "offline catalyst labels and regeneration events from real field batches."
            ),
        },
    ]


def _soft_sensor_context(soft_sensor_matrix_metrics: dict[str, Any]) -> dict[str, Any]:
    readiness = _dict(soft_sensor_matrix_metrics.get("readiness"))
    feature_contract = _dict(soft_sensor_matrix_metrics.get("feature_contract"))
    pressure_contract = _dict(feature_contract.get("pressure_headloss_candidate_contract"))
    return {
        "soft_sensor_matrix_status": readiness.get("soft_sensor_matrix_status", "unknown"),
        "pressure_headloss_candidate_pool_status": readiness.get("pressure_headloss_candidate_pool_status", "unknown"),
        "pressure_headloss_schema_ready": bool(readiness.get("pressure_headloss_schema_ready", False)),
        "pressure_headloss_candidate_ids": _string_list(
            pressure_contract.get("candidate_ids")
            or readiness.get("pressure_headloss_candidate_ids")
        ),
        "can_use_pressure_headloss_for_field_claim": bool(
            readiness.get("can_use_pressure_headloss_for_field_claim", False)
        ),
    }


def _target_hidden_states(readiness: dict[str, Any], r2_fv4: dict[str, Any]) -> list[str]:
    states = _string_list(readiness.get("agent48_hidden_state_hard_unresolved"))
    if not states:
        states = _string_list(r2_fv4.get("hard_unresolved_hidden_states"))
    return states or [TARGET_HIDDEN_STATE]


def _requirement(metrics: dict[str, Any], requirement_id: str) -> dict[str, Any]:
    for row in _list_of_dicts(metrics.get("field_validation_requirements")):
        if str(row.get("requirement_id", "")) == requirement_id:
            return row
    return {"requirement_id": requirement_id}


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list_of_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [row for row in value if isinstance(row, dict)]


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]
