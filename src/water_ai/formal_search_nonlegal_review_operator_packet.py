from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


PACKET_ID = "R8u136_formal_search_nonlegal_review_operator_packet"


def build_formal_search_nonlegal_review_operator_packet(
    *,
    ai_nonlegal_review_brief: dict[str, Any],
    nonlegal_review_response_template: dict[str, Any],
    nonlegal_review_response_source_preflight: dict[str, Any],
    formal_search_review_readiness: dict[str, Any],
    claim_scope_patch_draft: dict[str, Any] | None = None,
    upstream_formal_search_result_package_path: str = "",
) -> dict[str, Any]:
    brief_readiness = _dict(ai_nonlegal_review_brief.get("review_readiness"))
    brief_metadata = _dict(ai_nonlegal_review_brief.get("brief_metadata"))
    brief_rows = _list(ai_nonlegal_review_brief.get("brief_rows"))
    brief_fallback_ready = bool(
        upstream_formal_search_result_package_path
        and _brief_ready(ai_nonlegal_review_brief)
        and brief_rows
    )
    expected_row_ids = [
        str(row_id)
        for row_id in nonlegal_review_response_template.get(
            "expected_review_packet_row_ids",
            [],
        )
    ]
    template_rows = _list(nonlegal_review_response_template.get("response_template_rows"))
    contract_basis = "agent60_response_template"
    if not expected_row_ids and brief_fallback_ready:
        expected_row_ids = _review_packet_row_ids_from_brief(brief_rows)
        template_rows = _fallback_template_rows(
            brief_rows=brief_rows,
            review_row_required_fields=_list(
                nonlegal_review_response_template.get("review_row_required_fields")
            ),
        )
        contract_basis = "ai_brief_rows_with_upstream_formal_search_package_dependency"
    high_priority_rows = [
        row for row in brief_rows
        if str(row.get("risk_tier_for_human_triage", "")).startswith("high_overlap")
    ]
    status = _packet_status(
        ai_nonlegal_review_brief=ai_nonlegal_review_brief,
        nonlegal_review_response_template=nonlegal_review_response_template,
        nonlegal_review_response_source_preflight=nonlegal_review_response_source_preflight,
        formal_search_review_readiness=formal_search_review_readiness,
        brief_fallback_ready=brief_fallback_ready,
    )
    source_env_var = str(
        nonlegal_review_response_template.get(
            "expected_env_var",
            "FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH",
        )
    )
    recommended_output_path = str(
        nonlegal_review_response_template.get(
            "recommended_output_path",
            "outputs/agent_architecture_consolidation/formal_search_nonlegal_review_response.json",
        )
    )
    accepted_count = _int(
        nonlegal_review_response_source_preflight.get("accepted_review_row_count")
    )
    can_route_to_claim_scope_patch = bool(
        nonlegal_review_response_source_preflight.get("can_route_to_claim_scope_patch_draft")
    )
    upstream_env_var = "FORMAL_SEARCH_RESULT_PACKAGE_PATH"
    validation_command = _agent60_validation_command(
        source_env_var=source_env_var,
        recommended_output_path=recommended_output_path,
        upstream_env_var=upstream_env_var,
        upstream_formal_search_result_package_path=upstream_formal_search_result_package_path,
    )
    return {
        "operator_packet_metadata": {
            "packet_id": PACKET_ID,
            "packet_status": status,
            "packet_role": "human_nonlegal_review_submission_operator_packet",
            "created_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "linked_ai_brief_id": brief_metadata.get("brief_id", ""),
            "linked_ai_brief_status": brief_metadata.get("brief_status", ""),
            "linked_review_readiness_status": formal_search_review_readiness.get(
                "formal_search_review_readiness_status",
                "",
            ),
        },
        "operator_action": {
            "upstream_source_env_var": upstream_env_var,
            "upstream_formal_search_result_package_path": upstream_formal_search_result_package_path,
            "required_env_vars": _required_env_vars(
                source_env_var=source_env_var,
                upstream_formal_search_result_package_path=upstream_formal_search_result_package_path,
            ),
            "source_env_var": source_env_var,
            "recommended_output_path": recommended_output_path,
            "expected_review_packet_row_count": len(expected_row_ids),
            "accepted_review_row_count": accepted_count,
            "rejected_review_row_count": _int(
                nonlegal_review_response_source_preflight.get("rejected_review_row_count")
            ),
            "high_priority_review_row_count": len(high_priority_rows),
            "next_operator_action": _next_operator_action(
                status=status,
                source_env_var=source_env_var,
                recommended_output_path=recommended_output_path,
                upstream_env_var=upstream_env_var,
                upstream_formal_search_result_package_path=upstream_formal_search_result_package_path,
            ),
            "validation_commands": [
                validation_command,
                ".venv/bin/python experiments/run_agent50_model_core_governance.py",
            ],
        },
        "response_contract": {
            "contract_basis": contract_basis,
            "required_root_keys": nonlegal_review_response_template.get("required_root_keys", []),
            "review_metadata_required_fields": nonlegal_review_response_template.get(
                "review_metadata_required_fields",
                [],
            ),
            "review_row_required_fields": nonlegal_review_response_template.get(
                "review_row_required_fields",
                [],
            ),
            "expected_review_packet_row_ids": expected_row_ids,
            "expected_review_packet_row_id_count": len(expected_row_ids),
            "template_row_count": len(template_rows),
        },
        "human_review_rows": _human_review_rows(brief_rows=brief_rows, template_rows=template_rows),
        "pre_submission_checklist": [
            "Replace every TODO_* value and remove template_only markers.",
            "Use only human nonlegal technical comparison wording.",
            "Preserve field replay, operator review and release gate as validation boundaries.",
            "Do not assert novelty, inventiveness, patentability or authorization likelihood.",
            "Do not state that literature/search results are field-supported claims.",
            "Submit all expected review_packet_row_ids exactly once.",
        ],
        "rejection_conditions": [
            "missing review_metadata root",
            "missing review_rows root",
            "unknown or missing review_packet_row_id",
            "TODO/template marker remains",
            "legal opinion or authorization likelihood wording appears",
            "field claim upgrade wording appears",
            "accepted row count is below expected row count",
        ],
        "downstream_state": {
            "source_preflight_status": nonlegal_review_response_source_preflight.get(
                "formal_search_nonlegal_review_response_source_status",
                "",
            ),
            "review_response_supplied": bool(
                nonlegal_review_response_source_preflight.get("review_response_supplied")
            ),
            "human_review_completed": bool(
                nonlegal_review_response_source_preflight.get("human_review_completed")
            ),
            "can_route_to_claim_scope_patch_draft": can_route_to_claim_scope_patch,
            "claim_scope_patch_draft_status": _dict(claim_scope_patch_draft).get(
                "formal_search_claim_scope_patch_draft_status",
                "",
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
            "boundary_statement": (
                "This packet only helps a human prepare and submit a nonlegal technical "
                "comparison response. It is not a review result, legal opinion, claim text, "
                "field evidence or control authorization."
            ),
        },
    }


def _packet_status(
    *,
    ai_nonlegal_review_brief: dict[str, Any],
        nonlegal_review_response_template: dict[str, Any],
        nonlegal_review_response_source_preflight: dict[str, Any],
        formal_search_review_readiness: dict[str, Any],
        brief_fallback_ready: bool = False,
) -> str:
    if not _brief_ready(ai_nonlegal_review_brief):
        return "formal_search_nonlegal_review_operator_packet_blocked_by_ai_brief"
    template_status = str(
        nonlegal_review_response_template.get(
            "formal_search_nonlegal_review_response_template_status",
            "",
        )
    )
    template_ready = (
        template_status
        == "formal_search_nonlegal_review_response_template_ready_waiting_for_human_submission"
    )
    if not template_ready and not brief_fallback_ready:
        return "formal_search_nonlegal_review_operator_packet_blocked_by_response_template"
    readiness_status = str(
        formal_search_review_readiness.get("formal_search_review_readiness_status", "")
    )
    if readiness_status == "formal_search_review_invalid_boundary_violation":
        return "formal_search_nonlegal_review_operator_packet_blocked_by_review_readiness"
    if (
        not brief_fallback_ready
        and readiness_status != "formal_search_review_ready_for_human_nonlegal_comparison"
    ):
        return "formal_search_nonlegal_review_operator_packet_blocked_by_review_readiness"
    preflight_status = str(
        nonlegal_review_response_source_preflight.get(
            "formal_search_nonlegal_review_response_source_status",
            "",
        )
    )
    if preflight_status == "formal_search_nonlegal_review_response_ready_for_claim_scope_patch_draft":
        return "formal_search_nonlegal_review_operator_packet_human_response_ready_for_agent60_patch_gate"
    return "formal_search_nonlegal_review_operator_packet_ready_waiting_for_human_response"


def _brief_ready(brief: dict[str, Any]) -> bool:
    metadata = _dict(brief.get("brief_metadata"))
    readiness = _dict(brief.get("review_readiness"))
    boundary = _dict(brief.get("boundary"))
    return (
        metadata.get("brief_status") == "formal_search_ai_nonlegal_review_brief_ready_for_human_review"
        and readiness.get("can_help_human_nonlegal_review") is True
        and readiness.get("can_route_to_claim_scope_patch_draft") is False
        and readiness.get("legal_opinion_allowed") is False
        and readiness.get("field_claim_upgrade_allowed") is False
        and boundary.get("can_emit_claim_text") is False
        and boundary.get("can_write_to_actuator") is False
        and boundary.get("can_write_to_release_gate") is False
    )


def _human_review_rows(
    *,
    brief_rows: list[Any],
    template_rows: list[Any],
) -> list[dict[str, Any]]:
    template_by_row_id = {
        str(row.get("review_packet_row_id", "")): row
        for row in template_rows
        if isinstance(row, dict)
    }
    rows: list[dict[str, Any]] = []
    for index, row in enumerate(brief_rows, start=1):
        if not isinstance(row, dict):
            continue
        row_id = str(row.get("review_packet_row_id", ""))
        template = template_by_row_id.get(row_id, {})
        rows.append(
            {
                "operator_row_id": f"FSNROP{index}_{row_id}",
                "review_packet_row_id": row_id,
                "linked_work_package_id": row.get("linked_work_package_id", ""),
                "hit_id": row.get("hit_id", ""),
                "risk_tier_for_human_triage": row.get("risk_tier_for_human_triage", ""),
                "ai_suggested_nonlegal_starting_option": row.get(
                    "ai_suggested_nonlegal_starting_option",
                    "",
                ),
                "mapped_claim_scaffold_ids": row.get("mapped_claim_scaffold_ids", []),
                "required_human_fields": [
                    key for key in template.keys()
                    if key not in {"template_only"}
                ],
                "must_confirm": row.get("human_reviewer_must_confirm", []),
                "preserved_field_validation_gate": row.get(
                    "preserved_field_validation_gate_from_preliminary_record",
                    "",
                ),
                "boundary": row.get("evidence_boundary", ""),
            }
        )
    return rows


def _review_packet_row_ids_from_brief(brief_rows: list[Any]) -> list[str]:
    return [
        str(row.get("review_packet_row_id", ""))
        for row in brief_rows
        if isinstance(row, dict) and str(row.get("review_packet_row_id", ""))
    ]


def _fallback_template_rows(
    *,
    brief_rows: list[Any],
    review_row_required_fields: list[Any],
) -> list[dict[str, Any]]:
    required_fields = [
        str(field)
        for field in review_row_required_fields
        if isinstance(field, str) and field
    ]
    if not required_fields:
        required_fields = [
            "review_packet_row_id",
            "reviewer_id",
            "review_time",
            "nonlegal_overlap_assessment",
            "distinguishing_technical_detail",
            "fallback_scope_recommendation",
            "preserved_field_validation_gate",
            "evidence_boundary_acknowledgement",
            "reviewer_signature_or_trace_id",
            "legal_status",
        ]
    rows: list[dict[str, Any]] = []
    for brief_row in brief_rows:
        if not isinstance(brief_row, dict):
            continue
        row_id = str(brief_row.get("review_packet_row_id", ""))
        if not row_id:
            continue
        template = {field: "TODO" for field in required_fields}
        template["review_packet_row_id"] = row_id
        template["template_only"] = True
        rows.append(template)
    return rows


def _required_env_vars(
    *,
    source_env_var: str,
    upstream_formal_search_result_package_path: str,
) -> list[str]:
    if upstream_formal_search_result_package_path:
        return ["FORMAL_SEARCH_RESULT_PACKAGE_PATH", source_env_var]
    return [source_env_var]


def _agent60_validation_command(
    *,
    source_env_var: str,
    recommended_output_path: str,
    upstream_env_var: str,
    upstream_formal_search_result_package_path: str,
) -> str:
    env_parts = []
    if upstream_formal_search_result_package_path:
        env_parts.append(f"{upstream_env_var}={upstream_formal_search_result_package_path}")
    env_parts.append(f"{source_env_var}={recommended_output_path}")
    return (
        " ".join(env_parts)
        + " .venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py"
    )


def _next_operator_action(
    *,
    status: str,
    source_env_var: str,
    recommended_output_path: str,
    upstream_env_var: str,
    upstream_formal_search_result_package_path: str,
) -> str:
    if status == "formal_search_nonlegal_review_operator_packet_human_response_ready_for_agent60_patch_gate":
        return (
            "rerun Agent60 and inspect formal_search_claim_scope_patch_draft; keep formal counsel "
            "and no-claim-text boundaries active"
        )
    if status.endswith("ready_waiting_for_human_response"):
        upstream_clause = ""
        if upstream_formal_search_result_package_path:
            upstream_clause = (
                f", keep {upstream_env_var}={upstream_formal_search_result_package_path}"
            )
        return (
            f"complete a human nonlegal review response at {recommended_output_path}, set "
            f"{source_env_var}{upstream_clause}, then run Agent60 source preflight"
        )
    return "repair upstream AI brief, review template or review readiness before asking for human response"


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0
