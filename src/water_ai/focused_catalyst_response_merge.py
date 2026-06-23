from __future__ import annotations

from copy import deepcopy
from typing import Any


PREFLIGHT_ID = "R8u112_focused_catalyst_response_merge_preflight"
REPAIR_WORK_ORDER_ID = "R8u127_focused_catalyst_response_repair_work_order"
TARGET_HIDDEN_STATE = "catalyst_activity"
FOCUSED_PACKAGE_TYPE = "focused_catalyst_activity_response"
FULL_PACKAGE_TYPE = "field_activation_evidence_response"


def build_focused_catalyst_response_merge_preflight(
    *,
    focused_response: dict[str, Any],
    focused_schema: dict[str, Any],
    full_response_template: dict[str, Any],
    merge_plan: dict[str, Any],
    source_path: str = "",
    external_response_supplied: bool = False,
    source_preflight: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate a focused catalyst response and merge it into a full response candidate."""

    source_gate = source_preflight if isinstance(source_preflight, dict) else {}
    source_can_run = bool(source_gate.get("can_run_merge_preflight", True))
    required_top = _string_list(focused_schema.get("required_top_level_fields"))
    required_row_fields = _string_list(focused_schema.get("required_row_fields"))
    expected_row_ids = _string_list(merge_plan.get("focused_response_row_ids"))
    row_count_must_equal = _int(focused_schema.get("row_count_must_equal"), default=len(expected_row_ids) or 6)
    minimum_batch_count = _int(focused_response.get("minimum_matched_batch_count"), default=3)
    top_level_issues = _top_level_issues(focused_response, required_top, row_count_must_equal)
    row_results = _row_results(
        focused_response=focused_response,
        expected_row_ids=expected_row_ids,
        required_row_fields=required_row_fields,
    )
    batch_alignment = _batch_alignment(row_results, minimum_batch_count)
    row_content_pass = not top_level_issues and all(row["row_status"] == "focused_row_ready" for row in row_results)
    row_preflight_pass = row_content_pass and bool(batch_alignment["matched_batch_requirement_pass"])
    merged_candidate = _merged_full_response_candidate(
        full_response_template=full_response_template,
        row_results=row_results,
        focused_response=focused_response,
        source_preflight_status=str(
            source_gate.get(
                "source_preflight_status",
                "focused_catalyst_response_source_preflight_not_available",
            )
        ),
        external_response_supplied=external_response_supplied,
        row_preflight_pass=row_preflight_pass,
        batch_alignment=batch_alignment,
    )
    status = _preflight_status(
        source_can_run=source_can_run,
        external_response_supplied=external_response_supplied,
        top_level_issues=top_level_issues,
        row_content_pass=row_content_pass,
        row_preflight_pass=row_preflight_pass,
        batch_pass=bool(batch_alignment["matched_batch_requirement_pass"]),
    )
    return {
        "preflight_id": PREFLIGHT_ID,
        "preflight_type": "focused_catalyst_response_to_full_response_merge_preflight",
        "preflight_status": status,
        "source_env_var": "FOCUSED_CATALYST_RESPONSE_PATH",
        "source_path": source_path,
        "external_response_supplied": external_response_supplied,
        "source_preflight": source_gate,
        "source_preflight_status": source_gate.get(
            "source_preflight_status",
            "focused_catalyst_response_source_preflight_not_available",
        ),
        "source_can_run_merge_preflight": source_can_run,
        "source_package_type": focused_response.get("package_type", ""),
        "target_full_package_type": FULL_PACKAGE_TYPE,
        "target_hidden_state": TARGET_HIDDEN_STATE,
        "top_level_issue_count": len(top_level_issues),
        "top_level_issues": top_level_issues,
        "expected_focused_response_row_count": row_count_must_equal,
        "provided_focused_response_row_count": len(_list_of_dicts(focused_response.get("evidence_rows"))),
        "missing_focused_response_row_count": sum(1 for row in row_results if row["row_status"] == "missing_focused_row"),
        "blocked_focused_response_row_count": sum(1 for row in row_results if row["blocking_issue_count"] > 0),
        "row_preflight_pass": row_preflight_pass,
        "row_results": row_results,
        "batch_alignment": batch_alignment,
        "merged_full_response_candidate": merged_candidate,
        "merged_full_response_candidate_availability_status": merged_candidate[
            "candidate_availability_status"
        ],
        "merged_full_response_candidate_preflight_submit_ready": merged_candidate[
            "candidate_preflight_submit_ready"
        ],
        "merged_full_response_candidate_self_declared_submit_ready": merged_candidate[
            "candidate_self_declared_submit_ready"
        ],
        "merged_full_response_candidate_external_response_supplied": merged_candidate[
            "external_focused_response_supplied"
        ],
        "merged_full_response_candidate_submit_ready_semantics": merged_candidate[
            "candidate_submit_ready_semantics"
        ],
        "merged_full_response_candidate_use_boundary": merged_candidate["candidate_use_boundary"],
        "merged_full_response_candidate_row_count": len(_list_of_dicts(merged_candidate.get("evidence_rows"))),
        "merged_replacement_row_count": sum(1 for row in row_results if row["row_status"] == "focused_row_ready"),
        "remaining_full_response_row_count": _int(merge_plan.get("remaining_full_response_row_count"), default=0),
        "can_emit_merged_full_response_candidate": row_preflight_pass,
        "can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH": row_preflight_pass,
        "can_route_to_catalyst_evidence_response_gate": row_preflight_pass,
        "can_route_to_full_external_activation_router": False,
        "can_route_to_agent51_field_proxy_holdout": False,
        "can_relax_agent49_catalyst_uncertainty_block": False,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "next_operator_action": _next_operator_action(status),
        "full_response_boundary": (
            "The merged candidate only replaces the six catalyst_activity rows inside the full 33-row response. "
            "The remaining rows may still contain TODO/template markers and can still block R8u98 full response "
            "preflight. Passing this merge preflight does not create field validation."
        ),
        "no_write_boundary": (
            "This merge preflight cannot authorize actuator writes, release-gate writes, Agent51 holdout pass, "
            "Agent49 guardrail relaxation, field-supported claims or external activation router readiness."
        ),
    }


def _preflight_status(
    *,
    source_can_run: bool,
    external_response_supplied: bool,
    top_level_issues: list[str],
    row_content_pass: bool,
    row_preflight_pass: bool,
    batch_pass: bool,
) -> str:
    if not source_can_run:
        return "focused_catalyst_response_merge_blocked_at_source_preflight"
    if not external_response_supplied:
        return "focused_catalyst_response_merge_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH"
    if top_level_issues:
        return "focused_catalyst_response_merge_blocked_at_source_shape"
    if not row_content_pass:
        return "focused_catalyst_response_merge_blocked_at_row_preflight"
    if not batch_pass:
        return "focused_catalyst_response_merge_blocked_at_batch_alignment"
    if not row_preflight_pass:
        return "focused_catalyst_response_merge_blocked_at_row_preflight"
    return "focused_catalyst_response_merge_ready_for_FIELD_ACTIVATION_RESPONSE_PATH_candidate"


def _next_operator_action(status: str) -> str:
    return {
        "focused_catalyst_response_merge_blocked_at_source_preflight": (
            "repair_FOCUSED_CATALYST_RESPONSE_PATH_file_or_json_shape"
        ),
        "focused_catalyst_response_merge_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH": (
            "fill_focused_catalyst_response_template_and_set_FOCUSED_CATALYST_RESPONSE_PATH"
        ),
        "focused_catalyst_response_merge_blocked_at_source_shape": "repair_focused_catalyst_response_top_level_shape",
        "focused_catalyst_response_merge_blocked_at_batch_alignment": (
            "add_three_shared_real_field_batch_ids_to_all_focused_rows"
        ),
        "focused_catalyst_response_merge_blocked_at_row_preflight": "repair_focused_catalyst_response_rows",
        "focused_catalyst_response_merge_ready_for_FIELD_ACTIVATION_RESPONSE_PATH_candidate": (
            "set_FIELD_ACTIVATION_RESPONSE_PATH_to_merged_full_response_candidate"
        ),
    }.get(status, "inspect_focused_catalyst_response_merge_preflight")


def preflight_focused_catalyst_response_source(
    *,
    source_path: str,
    load_status: str,
    response: dict[str, Any],
    default_response_template: dict[str, Any],
) -> dict[str, Any]:
    """Classify the focused response source before row-level merge preflight."""

    supplied = bool(source_path)
    loaded = load_status == "focused_catalyst_response_source_loaded"
    using_default_template = not supplied
    can_run = using_default_template or loaded
    source_status = _source_preflight_status(
        load_status=load_status,
        using_default_template=using_default_template,
        can_run=can_run,
    )
    evidence_rows = _list_of_dicts(response.get("evidence_rows"))
    default_rows = _list_of_dicts(default_response_template.get("evidence_rows"))
    return {
        "source_preflight_id": "R8u126_focused_catalyst_response_source_preflight",
        "source_preflight_type": "focused_catalyst_response_source_preflight",
        "source_env_var": "FOCUSED_CATALYST_RESPONSE_PATH",
        "source_path": source_path,
        "source_load_status": load_status,
        "source_preflight_status": source_status,
        "external_response_supplied": loaded,
        "using_default_template": using_default_template,
        "can_run_merge_preflight": can_run,
        "provided_top_level_type": "object" if isinstance(response, dict) else type(response).__name__,
        "provided_package_type": response.get("package_type", "") if isinstance(response, dict) else "",
        "provided_row_count": len(evidence_rows),
        "default_template_row_count": len(default_rows),
        "next_operator_action": _source_preflight_next_operator_action(source_status),
        "can_emit_merged_full_response_candidate": False,
        "can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH": False,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "no_write_boundary": (
            "This source preflight only checks whether FOCUSED_CATALYST_RESPONSE_PATH can be loaded for "
            "focused catalyst merge preflight. It cannot create field evidence, emit a full response candidate, "
            "resume the model chain, write actuator policy or write a release gate."
        ),
    }


def _source_preflight_status(
    *,
    load_status: str,
    using_default_template: bool,
    can_run: bool,
) -> str:
    if using_default_template:
        return "focused_catalyst_response_source_using_default_template"
    if load_status == "focused_catalyst_response_source_file_missing":
        return "focused_catalyst_response_source_file_missing"
    if load_status == "focused_catalyst_response_source_invalid_json":
        return "focused_catalyst_response_source_invalid_json"
    if load_status == "focused_catalyst_response_source_root_not_object":
        return "focused_catalyst_response_source_root_not_object"
    if can_run:
        return "focused_catalyst_response_source_loaded"
    return "focused_catalyst_response_source_blocked"


def _source_preflight_next_operator_action(source_status: str) -> str:
    return {
        "focused_catalyst_response_source_using_default_template": (
            "fill_focused_catalyst_response_template_and_set_FOCUSED_CATALYST_RESPONSE_PATH"
        ),
        "focused_catalyst_response_source_file_missing": "repair_FOCUSED_CATALYST_RESPONSE_PATH_file_path",
        "focused_catalyst_response_source_invalid_json": "repair_focused_catalyst_response_json_syntax",
        "focused_catalyst_response_source_root_not_object": "submit_focused_catalyst_response_as_json_object",
        "focused_catalyst_response_source_loaded": "run_focused_catalyst_response_merge_preflight",
    }.get(source_status, "inspect_focused_catalyst_response_source_preflight")


def build_focused_catalyst_response_repair_work_order(
    *,
    source_preflight: dict[str, Any],
    merge_preflight: dict[str, Any],
) -> dict[str, Any]:
    """Turn focused response source/row/batch blockers into an operator repair contract."""

    source_status = str(
        source_preflight.get(
            "source_preflight_status",
            "focused_catalyst_response_source_preflight_not_available",
        )
    )
    merge_status = str(
        merge_preflight.get(
            "preflight_status",
            "focused_catalyst_response_merge_not_available",
        )
    )
    batch_alignment = merge_preflight.get("batch_alignment", {})
    if not isinstance(batch_alignment, dict):
        batch_alignment = {}
    minimum_matched = _int(batch_alignment.get("minimum_matched_batch_count"), default=3)
    matched_count = _int(batch_alignment.get("matched_batch_count"), default=0)
    matched_deficit = max(minimum_matched - matched_count, 0)
    repair_items = _focused_repair_items(
        source_preflight=source_preflight,
        merge_preflight=merge_preflight,
        source_status=source_status,
        merge_status=merge_status,
        matched_deficit=matched_deficit,
    )
    status = _focused_repair_work_order_status(
        source_status=source_status,
        source_can_run=bool(source_preflight.get("can_run_merge_preflight", False)),
        merge_status=merge_status,
        repair_items=repair_items,
    )
    highest_priority = repair_items[0]["repair_id"] if repair_items else ""
    return {
        "work_order_id": REPAIR_WORK_ORDER_ID,
        "work_order_type": "focused_catalyst_response_operator_repair_contract",
        "work_order_status": status,
        "source_env_var": "FOCUSED_CATALYST_RESPONSE_PATH",
        "source_path": str(source_preflight.get("source_path", "")),
        "source_preflight_status": source_status,
        "source_can_run_merge_preflight": bool(source_preflight.get("can_run_merge_preflight", False)),
        "merge_preflight_status": merge_status,
        "focused_row_count": _int(merge_preflight.get("provided_focused_response_row_count"), default=0),
        "blocked_focused_response_row_count": _int(
            merge_preflight.get("blocked_focused_response_row_count"),
            default=0,
        ),
        "top_level_issue_count": _int(merge_preflight.get("top_level_issue_count"), default=0),
        "matched_batch_count": matched_count,
        "minimum_matched_batch_count": minimum_matched,
        "matched_batch_deficit": matched_deficit,
        "repair_item_count": len(repair_items),
        "highest_priority_repair_id": highest_priority,
        "repair_items": repair_items,
        "next_operator_action": _focused_repair_next_operator_action(
            status=status,
            repair_items=repair_items,
            merge_preflight=merge_preflight,
            source_preflight=source_preflight,
        ),
        "can_emit_merged_full_response_candidate": bool(
            merge_preflight.get("can_emit_merged_full_response_candidate", False)
        )
        and not repair_items,
        "can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH": bool(
            merge_preflight.get("can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH", False)
        )
        and not repair_items,
        "can_route_to_agent51_field_proxy_holdout": False,
        "can_relax_agent49_catalyst_uncertainty_block": False,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "evidence_boundary": (
            "The work order only describes how to repair the external focused catalyst response artifact. "
            "It cannot create field observations, cannot validate remaining non-catalyst rows, and cannot replace "
            "full response preflight, R7 package acceptance, Agent51 holdout or operator review."
        ),
        "no_write_boundary": (
            "This repair work order is a no-write planning artifact. It cannot authorize actuator writes, "
            "release-gate writes, field-supported claims, Agent49 guardrail relaxation or model-chain resumption."
        ),
    }


def _focused_repair_items(
    *,
    source_preflight: dict[str, Any],
    merge_preflight: dict[str, Any],
    source_status: str,
    merge_status: str,
    matched_deficit: int,
) -> list[dict[str, Any]]:
    if source_status == "focused_catalyst_response_source_using_default_template":
        return [
            _repair_item(
                priority="P0",
                repair_id="FOCUSED_SOURCE_SUBMIT_RESPONSE",
                repair_scope="source",
                issue="FOCUSED_CATALYST_RESPONSE_PATH_not_supplied",
                next_operator_action=(
                    "fill_outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json_"
                    "with_real_field_values_then_set_FOCUSED_CATALYST_RESPONSE_PATH"
                ),
            )
        ]
    if not bool(source_preflight.get("can_run_merge_preflight", False)):
        return [
            _repair_item(
                priority="P0",
                repair_id="FOCUSED_SOURCE_REPAIR_LOAD",
                repair_scope="source",
                issue=source_status,
                next_operator_action=str(
                    source_preflight.get(
                        "next_operator_action",
                        "repair_FOCUSED_CATALYST_RESPONSE_PATH_file_or_json_shape",
                    )
                ),
            )
        ]

    items: list[dict[str, Any]] = []
    for issue in _string_list(merge_preflight.get("top_level_issues")):
        items.append(
            _repair_item(
                priority="P0",
                repair_id=f"FOCUSED_TOP_LEVEL_{_slug(issue)}",
                repair_scope="top_level",
                issue=issue,
                next_operator_action=_top_level_repair_action(issue),
            )
        )
    if merge_status == "focused_catalyst_response_merge_blocked_at_batch_alignment" and matched_deficit > 0:
        items.append(
            _repair_item(
                priority="P0",
                repair_id="FOCUSED_BATCH_ALIGNMENT",
                repair_scope="batch_alignment",
                issue=f"matched_batch_deficit:{matched_deficit}",
                next_operator_action="add_at_least_three_shared_real_field_batch_ids_to_all_six_focused_rows",
            )
        )
    for row in _list_of_dicts(merge_preflight.get("row_results")):
        row_id = str(row.get("response_row_id", ""))
        for issue in _string_list(row.get("blocking_issues")):
            items.append(
                _repair_item(
                    priority=_row_issue_priority(issue),
                    repair_id=f"FOCUSED_ROW_{_slug(row_id)}_{_slug(issue)}",
                    repair_scope="row",
                    issue=issue,
                    response_row_id=row_id,
                    next_operator_action=_row_repair_action(issue),
                )
            )
    return sorted(items, key=lambda item: (str(item["priority"]), str(item["repair_id"])))


def _repair_item(
    *,
    priority: str,
    repair_id: str,
    repair_scope: str,
    issue: str,
    next_operator_action: str,
    response_row_id: str = "",
) -> dict[str, Any]:
    item = {
        "priority": priority,
        "repair_id": repair_id,
        "repair_scope": repair_scope,
        "issue": issue,
        "next_operator_action": next_operator_action,
        "evidence_boundary": (
            "Use only real field/lab/operator records and keep no_write_boundary_confirmed=true. "
            "Do not replace missing evidence with synthetic/sample/template values."
        ),
    }
    if response_row_id:
        item["response_row_id"] = response_row_id
    return item


def _focused_repair_work_order_status(
    *,
    source_status: str,
    source_can_run: bool,
    merge_status: str,
    repair_items: list[dict[str, Any]],
) -> str:
    if source_status == "focused_catalyst_response_source_using_default_template":
        return "focused_catalyst_response_repair_work_order_waiting_for_external_response"
    if not source_can_run:
        return "focused_catalyst_response_repair_work_order_blocked_at_source_preflight"
    if merge_status == "focused_catalyst_response_merge_ready_for_FIELD_ACTIVATION_RESPONSE_PATH_candidate":
        return "focused_catalyst_response_repair_work_order_ready_for_FIELD_ACTIVATION_RESPONSE_PATH_candidate"
    if merge_status == "focused_catalyst_response_merge_blocked_at_batch_alignment":
        return "focused_catalyst_response_repair_work_order_blocked_at_batch_alignment"
    if merge_status == "focused_catalyst_response_merge_blocked_at_source_shape":
        return "focused_catalyst_response_repair_work_order_blocked_at_source_shape"
    if repair_items:
        return "focused_catalyst_response_repair_work_order_blocked_at_row_preflight"
    return "focused_catalyst_response_repair_work_order_blocked_by_merge_preflight"


def _focused_repair_next_operator_action(
    *,
    status: str,
    repair_items: list[dict[str, Any]],
    merge_preflight: dict[str, Any],
    source_preflight: dict[str, Any],
) -> str:
    if repair_items:
        return str(repair_items[0]["next_operator_action"])
    if status == "focused_catalyst_response_repair_work_order_ready_for_FIELD_ACTIVATION_RESPONSE_PATH_candidate":
        return str(
            merge_preflight.get(
                "next_operator_action",
                "set_FIELD_ACTIVATION_RESPONSE_PATH_to_merged_full_response_candidate",
            )
        )
    return str(
        source_preflight.get(
            "next_operator_action",
            merge_preflight.get("next_operator_action", "inspect_focused_catalyst_response_repair_work_order"),
        )
    )


def _top_level_repair_action(issue: str) -> str:
    if issue == "package_type_mismatch":
        return "set_package_type_to_focused_catalyst_activity_response"
    if issue == "target_hidden_state_mismatch":
        return "set_target_hidden_state_to_catalyst_activity"
    if issue == "focused_row_count_mismatch":
        return "provide_exactly_six_focused_catalyst_activity_rows"
    if issue == "missing_no_write_boundary":
        return "add_no_write_boundary_text_confirming_no_actuator_or_release_gate_write"
    if issue.startswith("missing_top_level:"):
        return f"fill_required_top_level_field_{issue.split(':', 1)[1]}"
    return "repair_focused_catalyst_response_top_level_shape"


def _row_issue_priority(issue: str) -> str:
    if issue in {"missing_focused_row", "hidden_state_mismatch"}:
        return "P0"
    if issue in {"data_origin_not_field", "template_marker_present", "missing_batch_ids"}:
        return "P1"
    return "P2"


def _row_repair_action(issue: str) -> str:
    if issue == "missing_focused_row":
        return "add_required_focused_response_row"
    if issue == "extra_focused_row":
        return "remove_extra_focused_response_row"
    if issue == "hidden_state_mismatch":
        return "set_hidden_state_to_catalyst_activity"
    if issue == "data_origin_not_field":
        return "set_data_origin_field_only_for_real_records"
    if issue == "template_marker_present":
        return "replace_template_markers_with_real_field_values"
    if issue == "no_write_boundary_not_confirmed":
        return "set_no_write_boundary_confirmed_true_after_operator_review"
    if issue == "missing_evidence_value_reference":
        return "fill_real_evidence_value_reference"
    if issue == "missing_batch_ids":
        return "fill_three_shared_real_batch_ids"
    if issue.startswith("missing_row_field:"):
        return f"fill_required_row_field_{issue.split(':', 1)[1]}"
    return "repair_focused_catalyst_response_row"


def _slug(value: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in value).strip("_").upper() or "UNKNOWN"


def _top_level_issues(response: dict[str, Any], required_top: list[str], row_count_must_equal: int) -> list[str]:
    issues: list[str] = []
    for field in required_top:
        if field not in response:
            issues.append(f"missing_top_level:{field}")
    if str(response.get("package_type", "")) != FOCUSED_PACKAGE_TYPE:
        issues.append("package_type_mismatch")
    if str(response.get("target_hidden_state", "")) != TARGET_HIDDEN_STATE:
        issues.append("target_hidden_state_mismatch")
    if len(_list_of_dicts(response.get("evidence_rows"))) != row_count_must_equal:
        issues.append("focused_row_count_mismatch")
    if _has_template_marker(response.get("no_write_boundary", "")):
        issues.append("missing_no_write_boundary")
    return issues


def _row_results(
    *,
    focused_response: dict[str, Any],
    expected_row_ids: list[str],
    required_row_fields: list[str],
) -> list[dict[str, Any]]:
    rows_by_id = {
        str(row.get("response_row_id", "")): row
        for row in _list_of_dicts(focused_response.get("evidence_rows"))
        if str(row.get("response_row_id", ""))
    }
    results = []
    for row_id in expected_row_ids:
        row = rows_by_id.get(row_id)
        if row is None:
            results.append(
                {
                    "response_row_id": row_id,
                    "row_status": "missing_focused_row",
                    "blocking_issue_count": 1,
                    "blocking_issues": ["missing_focused_row"],
                    "batch_ids": [],
                    "merged_row": {},
                }
            )
            continue
        issues = _row_issues(row, required_row_fields)
        results.append(
            {
                "response_row_id": row_id,
                "row_status": "focused_row_ready" if not issues else "focused_row_blocked",
                "blocking_issue_count": len(issues),
                "blocking_issues": issues,
                "batch_ids": _batch_ids(row),
                "observation_role": row.get("observation_role", ""),
                "required_evidence": row.get("required_evidence", ""),
                "merged_row": row,
            }
        )
    extra = sorted(row_id for row_id in rows_by_id if row_id not in set(expected_row_ids))
    for row_id in extra:
        results.append(
            {
                "response_row_id": row_id,
                "row_status": "extra_focused_row",
                "blocking_issue_count": 1,
                "blocking_issues": ["extra_focused_row"],
                "batch_ids": _batch_ids(rows_by_id[row_id]),
                "merged_row": rows_by_id[row_id],
            }
        )
    return results


def _row_issues(row: dict[str, Any], required_row_fields: list[str]) -> list[str]:
    issues: list[str] = []
    for field in required_row_fields:
        if field not in row:
            issues.append(f"missing_row_field:{field}")
    if str(row.get("hidden_state", "")) != TARGET_HIDDEN_STATE:
        issues.append("hidden_state_mismatch")
    if str(row.get("data_origin", "")).strip().lower() != "field":
        issues.append("data_origin_not_field")
    if _required_fields_have_template_marker(row, required_row_fields):
        issues.append("template_marker_present")
    if not _truthy(row.get("no_write_boundary_confirmed")):
        issues.append("no_write_boundary_not_confirmed")
    if not str(row.get("evidence_value_reference", "")).strip():
        issues.append("missing_evidence_value_reference")
    if not _batch_ids(row):
        issues.append("missing_batch_ids")
    return sorted(set(issues))


def _batch_alignment(row_results: list[dict[str, Any]], minimum_batch_count: int) -> dict[str, Any]:
    ready_rows = [row for row in row_results if row["row_status"] == "focused_row_ready"]
    role_to_batches = {
        str(row.get("observation_role") or row["response_row_id"]): set(_string_list(row.get("batch_ids")))
        for row in ready_rows
    }
    if role_to_batches and len(role_to_batches) == len([row for row in row_results if row["row_status"] != "extra_focused_row"]):
        shared = set.intersection(*role_to_batches.values()) if role_to_batches else set()
    else:
        shared = set()
    return {
        "minimum_matched_batch_count": minimum_batch_count,
        "role_to_batch_ids": {role: sorted(batch_ids) for role, batch_ids in role_to_batches.items()},
        "matched_batch_count": len(shared),
        "matched_batch_ids_sample": sorted(shared)[:8],
        "matched_batch_requirement_pass": len(shared) >= minimum_batch_count,
    }


def _merged_full_response_candidate(
    *,
    full_response_template: dict[str, Any],
    row_results: list[dict[str, Any]],
    focused_response: dict[str, Any],
    source_preflight_status: str,
    external_response_supplied: bool,
    row_preflight_pass: bool,
    batch_alignment: dict[str, Any],
) -> dict[str, Any]:
    candidate = deepcopy(full_response_template)
    replacement_by_id = {
        str(row["response_row_id"]): deepcopy(row["merged_row"])
        for row in row_results
        if row["row_status"] == "focused_row_ready" and isinstance(row.get("merged_row"), dict)
    }
    merged_rows = []
    for row in _list_of_dicts(candidate.get("evidence_rows")):
        row_id = str(row.get("response_row_id", ""))
        merged_rows.append(replacement_by_id.get(row_id, row))
    candidate["template_id"] = "R8u112_merged_full_field_activation_response_candidate"
    candidate["package_type"] = FULL_PACKAGE_TYPE
    candidate["focused_source_template_id"] = focused_response.get("template_id", "")
    candidate["focused_replacement_row_count"] = len(replacement_by_id)
    candidate["candidate_availability_status"] = _candidate_availability_status(
        source_preflight_status=source_preflight_status,
        external_response_supplied=external_response_supplied,
        row_preflight_pass=row_preflight_pass,
    )
    candidate["can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH"] = row_preflight_pass
    candidate["candidate_preflight_submit_ready"] = row_preflight_pass
    candidate["candidate_self_declared_submit_ready"] = row_preflight_pass
    candidate["candidate_submit_ready_semantics"] = (
        "candidate_preflight_submit_ready means the focused six-row merge gate passed and the file may be "
        "used only as FIELD_ACTIVATION_RESPONSE_PATH input to downstream full response/package/replay gates. "
        "It is not field validation, model-chain resume readiness, actuator readiness or release readiness."
    )
    candidate["external_focused_response_supplied"] = external_response_supplied
    candidate["source_preflight_status"] = source_preflight_status
    candidate["focused_row_preflight_pass"] = row_preflight_pass
    candidate["focused_matched_batch_count"] = _int(batch_alignment.get("matched_batch_count"), default=0)
    candidate["focused_minimum_matched_batch_count"] = _int(
        batch_alignment.get("minimum_matched_batch_count"),
        default=3,
    )
    candidate["focused_matched_batch_requirement_pass"] = bool(
        batch_alignment.get("matched_batch_requirement_pass", False)
    )
    candidate["evidence_rows"] = merged_rows
    candidate["no_write_boundary"] = (
        "This merged candidate is a preflight artifact only. It cannot authorize actuator or release-gate writes."
    )
    candidate["candidate_use_boundary"] = (
        "Only use this file as FIELD_ACTIVATION_RESPONSE_PATH when "
        "can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH is true and downstream full response, "
        "field package, replay, holdout, operator-review, actuator and release gates still pass. "
        "If false, this file is a diagnostic artifact and must not be routed as field evidence."
    )
    return candidate


def _candidate_availability_status(
    *,
    source_preflight_status: str,
    external_response_supplied: bool,
    row_preflight_pass: bool,
) -> str:
    if row_preflight_pass:
        return "candidate_ready_for_FIELD_ACTIVATION_RESPONSE_PATH_preflight_only"
    if not external_response_supplied:
        return "candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH"
    if source_preflight_status != "focused_catalyst_response_source_loaded":
        return "candidate_not_submittable_blocked_at_source_preflight"
    return "candidate_not_submittable_blocked_at_focused_row_or_batch_preflight"


def _batch_ids(row: dict[str, Any]) -> list[str]:
    candidates = row.get("matched_batch_ids")
    if candidates is None:
        candidates = row.get("batch_ids")
    if candidates is None:
        candidates = row.get("batch_id")
    return [
        part
        for item in _list(candidates)
        for part in _split_batch_value(str(item))
        if part and not _has_template_marker(part)
    ]


def _split_batch_value(value: str) -> list[str]:
    return [part.strip() for part in value.replace(";", ",").replace("|", ",").split(",") if part.strip()]


def _required_fields_have_template_marker(row: dict[str, Any], required_row_fields: list[str]) -> bool:
    return any(_has_template_marker(row.get(field, "")) for field in required_row_fields)


def _has_template_marker(value: object) -> bool:
    if isinstance(value, list):
        return any(_has_template_marker(item) for item in value)
    text = str(value).strip().lower()
    return not text or "todo" in text or "template" in text or text in {"nan", "none", "null"}


def _truthy(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def _int(value: object, *, default: int) -> int:
    try:
        return int(value or default)
    except (TypeError, ValueError):
        return default


def _string_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if value is None:
        return []
    return [str(value)]


def _list(value: object) -> list[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def _list_of_dicts(value: object) -> list[dict[str, Any]]:
    return [item for item in _list(value) if isinstance(item, dict)]
