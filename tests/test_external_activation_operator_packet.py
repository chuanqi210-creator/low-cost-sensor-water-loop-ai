from water_ai.external_activation_operator_packet import (
    build_external_activation_operator_action_packet,
)


def test_external_activation_operator_packet_guides_focused_response_fill() -> None:
    packet = build_external_activation_operator_action_packet(
        core_gate=_core_gate(),
        external_activation_router=_router_waiting(),
        catalyst_response_submission_kit=_catalyst_kit(),
        focused_catalyst_response_merge=_focused_merge_waiting(),
        focused_catalyst_response_template=_focused_template(),
    )

    assert packet["packet_id"] == "R8u130_external_activation_operator_action_packet"
    assert packet["packet_status"] == "operator_packet_waiting_for_focused_catalyst_response"
    assert packet["architecture_layer"] == "verification_governance_to_external_execution_handoff"
    assert packet["target_hidden_state"] == "catalyst_activity"
    assert packet["source_env_var"] == "FOCUSED_CATALYST_RESPONSE_PATH"
    assert packet["target_full_response_env_var"] == "FIELD_ACTIVATION_RESPONSE_PATH"
    assert packet["focused_template_path"] == (
        "outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json"
    )
    assert packet["expected_focused_response_row_count"] == 6
    assert packet["template_evidence_row_count"] == 6
    assert packet["focused_template_ready"] is True
    assert packet["minimum_matched_batch_count"] == 3
    assert packet["focused_repair_work_order_status"] == (
        "focused_catalyst_response_repair_work_order_waiting_for_external_response"
    )
    assert packet["focused_candidate_availability_status"] == (
        "candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH"
    )
    assert packet["focused_candidate_self_declared_submit_ready"] is False
    assert packet["focused_candidate_external_response_supplied"] is False
    assert packet["focused_candidate_operator_packet_submit_ready"] is False
    assert packet["packet_next_operator_action"] == (
        "fill_outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json_"
        "with_real_field_values_then_set_FOCUSED_CATALYST_RESPONSE_PATH"
    )
    assert packet["next_operator_action"] == packet["packet_next_operator_action"]
    assert packet["current_commands"] == [
        "fill outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json with real field values",
        "export FOCUSED_CATALYST_RESPONSE_PATH=/absolute/path/to/filled_focused_response.json",
        ".venv/bin/python experiments/run_focused_catalyst_response_merge.py",
    ]
    assert packet["operator_packet_boundary_pass"] is True
    assert packet["can_generate_field_evidence"] is False
    assert packet["can_resume_model_chain"] is False
    assert packet["can_write_to_actuator"] is False
    assert packet["can_write_to_release_gate"] is False
    assert packet["can_emit_field_supported_claim"] is False
    assert "cannot generate field evidence" in packet["no_write_boundary"]


def test_external_activation_operator_packet_routes_ready_candidate_to_full_response_env() -> None:
    packet = build_external_activation_operator_action_packet(
        core_gate=_core_gate(),
        external_activation_router=_router_waiting(),
        catalyst_response_submission_kit=_catalyst_kit(),
        focused_catalyst_response_merge={
            **_focused_merge_waiting(),
            "preflight_status": (
                "focused_catalyst_response_merge_ready_for_FIELD_ACTIVATION_RESPONSE_PATH_candidate"
            ),
            "source_preflight_status": "focused_catalyst_response_source_loaded",
            "row_preflight_pass": True,
            "can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH": True,
            "merged_full_response_candidate_availability_status": (
                "candidate_ready_for_FIELD_ACTIVATION_RESPONSE_PATH_preflight_only"
            ),
            "merged_full_response_candidate_self_declared_submit_ready": True,
            "merged_full_response_candidate_external_response_supplied": True,
            "merged_full_response_candidate_use_boundary": (
                "Only use after downstream gates still pass."
            ),
            "focused_catalyst_response_repair_work_order": {
                "work_order_status": (
                    "focused_catalyst_response_repair_work_order_ready_for_FIELD_ACTIVATION_RESPONSE_PATH_candidate"
                ),
                "repair_item_count": 0,
                "highest_priority_repair_id": "",
                "next_operator_action": "set_FIELD_ACTIVATION_RESPONSE_PATH_to_merged_full_response_candidate",
            },
        },
        focused_catalyst_response_template=_focused_template(),
    )

    assert packet["packet_status"] == "operator_packet_ready_to_set_FIELD_ACTIVATION_RESPONSE_PATH"
    assert packet["packet_next_operator_action"] == (
        "set_FIELD_ACTIVATION_RESPONSE_PATH_to_merged_full_response_candidate"
    )
    assert packet["next_operator_action"] == packet["packet_next_operator_action"]
    assert packet["current_commands"] == [
        (
            "export FIELD_ACTIVATION_RESPONSE_PATH="
            "outputs/focused_catalyst_response_merge/merged_full_field_activation_response_candidate.json"
        ),
        ".venv/bin/python experiments/run_field_activation_matrix.py",
        ".venv/bin/python experiments/run_agent50_model_core_governance.py",
    ]
    assert packet["focused_merge_can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH"] is True
    assert packet["focused_candidate_availability_status"] == (
        "candidate_ready_for_FIELD_ACTIVATION_RESPONSE_PATH_preflight_only"
    )
    assert packet["focused_candidate_self_declared_submit_ready"] is True
    assert packet["focused_candidate_operator_packet_submit_ready"] is True
    assert packet["can_resume_model_chain"] is False
    assert packet["can_write_to_actuator"] is False
    assert packet["can_write_to_release_gate"] is False


def _core_gate() -> dict[str, object]:
    return {
        "stage_decision": "stop_expansion_wait_for_real_field_package_or_new_core_interface",
        "self_interrupt_verdict": "stage_boundary_wait_for_external_activation",
        "external_resume_conditions": {
            "router_next_operator_action": (
                "fill_focused_catalyst_response_template_then_set_FOCUSED_CATALYST_RESPONSE_PATH_"
                "and_merge_to_FIELD_ACTIVATION_RESPONSE_PATH"
            )
        },
    }


def _router_waiting() -> dict[str, object]:
    return {
        "router_status": "external_activation_router_waiting_for_external_paths",
        "highest_priority_blocker": (
            "R7_REAL_FIELD_PACKAGE:field_activation_upstream_not_ready:"
            "R8U106_SUBMIT_FIELD_ACTIVATION_RESPONSE"
        ),
        "next_operator_action": (
            "fill_focused_catalyst_response_template_then_set_FOCUSED_CATALYST_RESPONSE_PATH_"
            "and_merge_to_FIELD_ACTIVATION_RESPONSE_PATH"
        ),
    }


def _catalyst_kit() -> dict[str, object]:
    return {
        "target_response_row_count": 6,
        "minimum_matched_batch_count": 3,
        "focused_response_template_path": (
            "outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json"
        ),
        "focused_response_schema_path": (
            "outputs/catalyst_response_submission_kit/focused_catalyst_response_schema.json"
        ),
        "full_response_merge_plan_path": (
            "outputs/catalyst_response_submission_kit/focused_to_full_response_merge_plan.json"
        ),
        "required_row_fields": [
            "response_row_id",
            "hidden_state",
            "data_origin",
            "batch_id",
            "matched_batch_ids",
            "evidence_value_reference",
            "no_write_boundary_confirmed",
        ],
    }


def _focused_merge_waiting() -> dict[str, object]:
    return {
        "preflight_status": "focused_catalyst_response_merge_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH",
        "source_preflight_status": "focused_catalyst_response_source_using_default_template",
        "source_env_var": "FOCUSED_CATALYST_RESPONSE_PATH",
        "target_hidden_state": "catalyst_activity",
        "expected_focused_response_row_count": 6,
        "row_preflight_pass": False,
        "can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH": False,
        "merged_full_response_candidate_availability_status": (
            "candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH"
        ),
        "merged_full_response_candidate_self_declared_submit_ready": False,
        "merged_full_response_candidate_external_response_supplied": False,
        "merged_full_response_candidate_use_boundary": (
            "If false, this file is a diagnostic artifact and must not be routed as field evidence."
        ),
        "focused_catalyst_response_repair_work_order": {
            "work_order_status": (
                "focused_catalyst_response_repair_work_order_waiting_for_external_response"
            ),
            "repair_item_count": 1,
            "highest_priority_repair_id": "FOCUSED_SOURCE_SUBMIT_RESPONSE",
            "next_operator_action": (
                "fill_outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json_"
                "with_real_field_values_then_set_FOCUSED_CATALYST_RESPONSE_PATH"
            ),
        },
    }


def _focused_template() -> dict[str, object]:
    rows = []
    for idx in range(6):
        rows.append(
            {
                "response_row_id": f"catalyst_activity_{idx}",
                "hidden_state": "catalyst_activity",
                "data_origin": "TODO_field",
                "batch_id": "TODO_batch_id_1,TODO_batch_id_2,TODO_batch_id_3",
                "matched_batch_ids": [
                    "TODO_batch_id_1",
                    "TODO_batch_id_2",
                    "TODO_batch_id_3",
                ],
                "evidence_value_reference": "TODO_table_column_or_file_reference",
                "no_write_boundary_confirmed": "TODO_true",
            }
        )
    return {
        "target_hidden_state": "catalyst_activity",
        "package_type": "focused_catalyst_activity_response",
        "required_response_row_count": 6,
        "minimum_matched_batch_count": 3,
        "operator_instructions": [
            "Fill only with real field provenance; do not leave TODO/template/sample markers.",
            "Use at least 3 shared batch_id values across all six rows.",
        ],
        "evidence_rows": rows,
    }
