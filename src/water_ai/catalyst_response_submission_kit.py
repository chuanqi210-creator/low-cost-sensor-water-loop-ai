from __future__ import annotations

from typing import Any


KIT_ID = "R8u111_catalyst_response_submission_kit"
TARGET_HIDDEN_STATE = "catalyst_activity"
REQUIRED_ROW_FIELDS = (
    "response_row_id",
    "hidden_state",
    "required_evidence",
    "evidence_channel",
    "table_name",
    "field_name",
    "data_origin",
    "batch_id",
    "matched_batch_ids",
    "timestamp",
    "node_id",
    "sensor_id",
    "evidence_value_reference",
    "offline_method_id",
    "detection_limit",
    "chain_of_custody_id",
    "operator_id",
    "no_write_boundary_confirmed",
    "review_notes",
)


def build_catalyst_response_submission_kit(
    *,
    observation_response_bridge: dict[str, Any],
    full_response_template: dict[str, Any],
    catalyst_evidence_response_gate: dict[str, Any],
) -> dict[str, Any]:
    """Build a small operator-facing response kit for the catalyst_activity rows."""

    target_rows = _target_rows(observation_response_bridge)
    full_rows = _full_rows_by_id(full_response_template)
    template_rows = [
        _focused_template_row(target_row=target, full_row=full_rows.get(str(target["response_row_id"])))
        for target in target_rows
    ]
    missing_from_full = [
        str(target["response_row_id"])
        for target in target_rows
        if str(target["response_row_id"]) not in full_rows
    ]
    minimum_batch_count = _minimum_matched_batch_count(observation_response_bridge)
    kit_status = (
        "catalyst_response_submission_kit_ready_for_operator_fill"
        if template_rows and not missing_from_full
        else "catalyst_response_submission_kit_blocked_by_missing_full_template_rows"
    )
    return {
        "kit_id": KIT_ID,
        "kit_type": "focused_catalyst_activity_response_submission_kit",
        "kit_status": kit_status,
        "target_hidden_state": TARGET_HIDDEN_STATE,
        "source_bridge_id": observation_response_bridge.get("bridge_id", "unknown_bridge"),
        "source_full_template_id": full_response_template.get("template_id", "unknown_full_response_template"),
        "source_focused_gate_id": catalyst_evidence_response_gate.get("gate_id", "unknown_focused_gate"),
        "source_focused_gate_status": catalyst_evidence_response_gate.get("gate_status", "unknown"),
        "target_response_row_count": len(template_rows),
        "missing_full_template_row_ids": missing_from_full,
        "minimum_matched_batch_count": minimum_batch_count,
        "required_row_fields": list(REQUIRED_ROW_FIELDS),
        "focused_response_template": {
            "template_id": "R8u111_focused_catalyst_activity_response_template",
            "package_type": "focused_catalyst_activity_response",
            "source_interface_id": full_response_template.get(
                "source_interface_id",
                "R8u97_field_activation_matrix_interface",
            ),
            "target_hidden_state": TARGET_HIDDEN_STATE,
            "required_response_row_count": len(template_rows),
            "minimum_matched_batch_count": minimum_batch_count,
            "evidence_rows": template_rows,
            "operator_instructions": _operator_instructions(minimum_batch_count),
            "no_write_boundary": _no_write_boundary(),
        },
        "focused_response_schema": _focused_response_schema(),
        "full_response_merge_plan": _merge_plan(
            target_rows=template_rows,
            full_response_template=full_response_template,
        ),
        "can_replace_full_field_activation_response": False,
        "can_route_to_catalyst_evidence_response_gate": False,
        "can_route_to_agent51_field_proxy_holdout": False,
        "can_relax_agent49_catalyst_uncertainty_block": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "next_operator_action": "fill_focused_catalyst_response_template_then_merge_into_full_FIELD_ACTIVATION_RESPONSE_PATH",
        "field_boundary": (
            "The focused template reduces operator scanning from the full 33-row response to six catalyst_activity "
            "rows. Filled rows must still be merged into a valid full field activation response or inspected by "
            "R8u110; no field claim is created by the template itself."
        ),
        "no_write_boundary": _no_write_boundary(),
    }


def _focused_template_row(*, target_row: dict[str, Any], full_row: dict[str, Any] | None) -> dict[str, Any]:
    source = full_row if full_row is not None else target_row
    row = {
        field: source.get(field, f"TODO_{field}")
        for field in REQUIRED_ROW_FIELDS
        if field != "matched_batch_ids"
    }
    row["response_row_id"] = target_row.get("response_row_id", row.get("response_row_id", ""))
    row["hidden_state"] = TARGET_HIDDEN_STATE
    row["required_evidence"] = target_row.get("required_evidence", row.get("required_evidence", ""))
    row["evidence_channel"] = target_row.get("evidence_channel", row.get("evidence_channel", "R7_REAL_FIELD_PACKAGE"))
    row["table_name"] = target_row.get("table_name", row.get("table_name", ""))
    row["field_name"] = target_row.get("field_name", row.get("field_name", ""))
    row["observation_role"] = target_row.get("observation_role", "unknown_role")
    row["priority"] = target_row.get("priority", "P1")
    row["priority_rank"] = target_row.get("priority_rank", 9)
    row["matched_batch_ids"] = ["TODO_batch_id_1", "TODO_batch_id_2", "TODO_batch_id_3"]
    row["data_origin"] = "TODO_field"
    row["batch_id"] = "TODO_batch_id_1,TODO_batch_id_2,TODO_batch_id_3"
    row["no_write_boundary_confirmed"] = "TODO_true"
    row["field_value_boundary"] = (
        "Use only real data_origin=field evidence references. Template/sample values keep R8u110 blocked."
    )
    return row


def _focused_response_schema() -> dict[str, Any]:
    return {
        "schema_id": "R8u111_focused_catalyst_activity_response_schema",
        "package_type": "focused_catalyst_activity_response",
        "required_top_level_fields": [
            "template_id",
            "package_type",
            "source_interface_id",
            "target_hidden_state",
            "required_response_row_count",
            "minimum_matched_batch_count",
            "evidence_rows",
            "no_write_boundary",
        ],
        "required_row_fields": list(REQUIRED_ROW_FIELDS),
        "row_count_must_equal": 6,
        "target_hidden_state_must_equal": TARGET_HIDDEN_STATE,
        "matched_batch_requirement": (
            "Every row should reference at least three shared real field batch_id values before R8u110 can pass."
        ),
        "no_write_required": True,
    }


def _merge_plan(*, target_rows: list[dict[str, Any]], full_response_template: dict[str, Any]) -> dict[str, Any]:
    full_row_ids = [
        str(row.get("response_row_id", ""))
        for row in _list_of_dicts(full_response_template.get("evidence_rows"))
    ]
    focused_row_ids = [str(row.get("response_row_id", "")) for row in target_rows]
    return {
        "merge_plan_id": "R8u111_focused_to_full_field_activation_response_merge_plan",
        "merge_strategy": "replace_rows_by_response_row_id",
        "source_focused_package_type": "focused_catalyst_activity_response",
        "target_full_package_type": "field_activation_evidence_response",
        "target_full_template_row_count": len(full_row_ids),
        "focused_replacement_row_count": len(focused_row_ids),
        "focused_response_row_ids": focused_row_ids,
        "remaining_full_response_row_count": max(0, len(full_row_ids) - len(focused_row_ids)),
        "merge_steps": [
            "Fill focused_catalyst_response_template.json with real field provenance for all six rows.",
            "Copy the six filled rows into outputs/model_core_governance/field_activation_response_template.json by response_row_id.",
            "Save the merged full response JSON outside the generated template path.",
            "Run FIELD_ACTIVATION_RESPONSE_PATH=/path/to/merged_full_response.json .venv/bin/python experiments/run_field_activation_matrix.py.",
            "Run .venv/bin/python experiments/run_catalyst_evidence_response_gate.py to inspect the focused catalyst rows.",
        ],
        "merge_boundary": (
            "Merging the six focused rows does not make the full 33-row response pass. Non-catalyst rows may still "
            "block the full response preflight, and catalyst rows still need package and holdout validation."
        ),
    }


def _operator_instructions(minimum_batch_count: int) -> list[str]:
    return [
        "Fill only with real field provenance; do not leave TODO/template/sample markers.",
        f"Use at least {minimum_batch_count} shared batch_id values across all six rows.",
        "Confirm no_write_boundary_confirmed=true on every row.",
        "For node_modality_sensor_timeseries rows, point evidence_value_reference to real node/modality/value/status records.",
        "For offline_lab_results, point to QA-passed catalyst_activity labels and method metadata.",
        "For campaign_operation_log, point to regeneration_event records aligned by batch_id.",
        "For site_topology_or_bed_geometry, point to nominal_HRT_min or bed geometry/flow records.",
    ]


def _no_write_boundary() -> str:
    return (
        "This focused submission kit cannot authorize actuator writes, release-gate writes, field-supported claims, "
        "Agent51 holdout pass, or Agent49 catalyst guardrail relaxation."
    )


def _target_rows(bridge: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        row
        for row in _list_of_dicts(bridge.get("priority_response_rows"))
        if str(row.get("hidden_state", "")) == TARGET_HIDDEN_STATE
    ]
    return sorted(rows, key=lambda row: (int(row.get("priority_rank", 9) or 9), str(row.get("response_row_id", ""))))


def _full_rows_by_id(response_template: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("response_row_id", "")): row
        for row in _list_of_dicts(response_template.get("evidence_rows"))
        if str(row.get("response_row_id", ""))
    }


def _minimum_matched_batch_count(bridge: dict[str, Any]) -> int:
    requirement = bridge.get("r2_fv4_requirement", {})
    if not isinstance(requirement, dict):
        return 3
    try:
        return int(requirement.get("minimum_matched_batch_count", 3) or 3)
    except (TypeError, ValueError):
        return 3


def _list_of_dicts(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]
