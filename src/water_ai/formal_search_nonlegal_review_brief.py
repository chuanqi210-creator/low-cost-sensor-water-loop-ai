from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from typing import Any


BRIEF_ID = "R8u134_formal_search_ai_nonlegal_review_brief"


def build_formal_search_ai_nonlegal_review_brief(
    *,
    preliminary_formal_search_result_package: dict[str, Any],
    nonlegal_comparison_review_packet: dict[str, Any],
    technical_claim_skeleton_scaffold: dict[str, Any] | None = None,
) -> dict[str, Any]:
    review_rows = nonlegal_comparison_review_packet.get("review_packet_rows", [])
    package_results = preliminary_formal_search_result_package.get("work_package_results", {})
    claims = _claim_rows(technical_claim_skeleton_scaffold or {})

    brief_rows: list[dict[str, Any]] = []
    missing_source_rows: list[str] = []
    missing_claim_rows: list[str] = []
    for index, review_row in enumerate(review_rows, start=1):
        work_package_id = str(review_row.get("linked_work_package_id", ""))
        result = package_results.get(work_package_id, {})
        hit = _first_row(result, "prior_art_hit_table")
        comparison = _first_row(result, "claim_element_comparison_chart")
        fallback = _first_row(result, "fallback_claim_scope_recommendation")
        covered_feature_ids = [
            str(item) for item in review_row.get("covered_project_element_ids", [])
        ]
        mapped_claims = _mapped_claims(claims, covered_feature_ids)
        if not hit.get("url_or_reference"):
            missing_source_rows.append(str(review_row.get("review_packet_row_id", "")))
        if not mapped_claims:
            missing_claim_rows.append(str(review_row.get("review_packet_row_id", "")))

        risk_tier = _risk_tier(str(hit.get("novelty_risk_signal", "")), str(hit.get("overlap_level", "")))
        brief_rows.append(
            {
                "brief_row_id": f"FSNAIB{index}_{review_row.get('review_packet_row_id', '')}",
                "review_packet_row_id": review_row.get("review_packet_row_id", ""),
                "linked_work_package_id": work_package_id,
                "hit_id": review_row.get("hit_id", hit.get("hit_id", "")),
                "source_database": hit.get("source_database", review_row.get("source_database", "")),
                "publication_or_reference": hit.get("publication_or_patent_id", ""),
                "title": hit.get("title", ""),
                "url_or_reference": hit.get("url_or_reference", ""),
                "covered_project_element_ids": covered_feature_ids,
                "mapped_claim_scaffold_ids": [claim["claim_id"] for claim in mapped_claims],
                "mapped_claim_titles": [claim["claim_title"] for claim in mapped_claims],
                "risk_tier_for_human_triage": risk_tier,
                "overlap_level": hit.get("overlap_level", ""),
                "risk_signal": hit.get("novelty_risk_signal", ""),
                "disclosed_capabilities": hit.get("disclosed_capabilities", ""),
                "missing_project_elements": hit.get("missing_project_elements", ""),
                "project_element_text": comparison.get("project_element_text", ""),
                "prior_art_disclosure_text": comparison.get("prior_art_disclosure_text", ""),
                "distinguishing_technical_detail_from_preliminary_record": comparison.get(
                    "missing_or_distinguishing_detail", ""
                ),
                "ai_suggested_review_focus": _suggested_focus(
                    risk_tier=risk_tier,
                    overlap_level=str(hit.get("overlap_level", "")),
                    missing_project_elements=str(hit.get("missing_project_elements", "")),
                ),
                "ai_suggested_nonlegal_starting_option": _starting_option(
                    risk_tier=risk_tier,
                    overlap_level=str(hit.get("overlap_level", "")),
                ),
                "human_reviewer_must_confirm": [
                    "overlap_level",
                    "distinguishing_technical_detail",
                    "fallback_scope_recommendation",
                    "preserved_field_validation_gate",
                    "whether additional search rows are needed",
                ],
                "preserved_field_validation_gate_from_preliminary_record": fallback.get(
                    "preserved_field_validation_gate",
                    comparison.get("field_validation_gate_to_preserve", ""),
                ),
                "cannot_route_to_claim_scope_patch_draft": True,
                "human_review_completed": False,
                "legal_status": "ai_assisted_brief_not_legal_opinion",
                "field_claim_upgrade_allowed": False,
                "evidence_boundary": (
                    "AI briefing only; it may help a human compare technical overlap, "
                    "but it is not a human review response, not legal advice and not field evidence."
                ),
            }
        )

    risk_counts = Counter(str(row["risk_tier_for_human_triage"]) for row in brief_rows)
    status = (
        "formal_search_ai_nonlegal_review_brief_ready_for_human_review"
        if brief_rows and not missing_source_rows
        else "formal_search_ai_nonlegal_review_brief_needs_source_alignment"
    )
    return {
        "brief_metadata": {
            "brief_id": BRIEF_ID,
            "brief_status": status,
            "brief_role": "ai_assisted_pre_review_not_human_review",
            "created_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "input_formal_search_result_package_status": preliminary_formal_search_result_package.get(
                "_preflight_summary", {}
            ).get("package_status", ""),
            "input_nonlegal_review_packet_status": nonlegal_comparison_review_packet.get(
                "formal_search_nonlegal_comparison_review_packet_status", ""
            ),
        },
        "review_readiness": {
            "review_packet_row_count": len(review_rows),
            "brief_row_count": len(brief_rows),
            "missing_source_row_count": len(missing_source_rows),
            "missing_claim_mapping_row_count": len(missing_claim_rows),
            "risk_tier_counts": dict(risk_counts),
            "can_help_human_nonlegal_review": bool(brief_rows and not missing_source_rows),
            "can_route_to_claim_scope_patch_draft": False,
            "human_review_completed": False,
            "can_generate_prior_art_result": False,
            "legal_opinion_allowed": False,
            "field_claim_upgrade_allowed": False,
        },
        "brief_rows": brief_rows,
        "operator_next_action": {
            "expected_env_var": "FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH",
            "response_template_path": (
                "outputs/agent_architecture_consolidation/"
                "formal_search_nonlegal_review_response_template.json"
            ),
            "next_operator_action": (
                "Use this AI-assisted brief only as a reading aid, then complete a human "
                "nonlegal technical comparison response and submit it via "
                "FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH."
            ),
        },
        "boundary": {
            "can_emit_claim_text": False,
            "can_resume_model_chain": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "cannot_do": [
                "cannot replace human nonlegal review response",
                "cannot assert novelty or inventiveness",
                "cannot assert authorization likelihood",
                "cannot upgrade public-source comparison into field-supported claim",
                "cannot write actuator or release gate",
            ],
        },
    }


def _first_row(result: dict[str, Any], key: str) -> dict[str, Any]:
    rows = result.get(key, [])
    if isinstance(rows, list) and rows:
        row = rows[0]
        if isinstance(row, dict):
            return row
    return {}


def _claim_rows(scaffold: dict[str, Any] | list[Any]) -> list[dict[str, Any]]:
    if isinstance(scaffold, list):
        rows = scaffold
    else:
        rows = scaffold.get("claims", [])
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _mapped_claims(
    claims: list[dict[str, Any]],
    covered_feature_ids: list[str],
) -> list[dict[str, str]]:
    covered = set(covered_feature_ids)
    mapped: list[dict[str, str]] = []
    for claim in claims:
        feature_ids = set(str(item) for item in claim.get("mapped_feature_ids", []))
        if covered and covered.intersection(feature_ids):
            mapped.append(
                {
                    "claim_id": str(claim.get("claim_id", "")),
                    "claim_title": str(claim.get("claim_title", "")),
                }
            )
    return mapped


def _risk_tier(risk_signal: str, overlap_level: str) -> str:
    text = f"{risk_signal} {overlap_level}".lower()
    if "strong" in text or "high" in text:
        return "high_overlap_human_review_priority"
    if "component" in text or "control_architecture" in text:
        return "component_or_architecture_overlap_review"
    if "medium" in text or "partial" in text:
        return "partial_overlap_review"
    return "unknown_overlap_needs_human_review"


def _starting_option(*, risk_tier: str, overlap_level: str) -> str:
    text = f"{risk_tier} {overlap_level}".lower()
    if "high_overlap" in text or "strong" in text:
        return "mark_high_overlap_needs_external_patent_counsel_review"
    if "component" in text:
        return "move_to_dependent_or_fallback_claim"
    if "partial" in text or "architecture" in text:
        return "narrow_to_distinguishing_greybox_loop_feature"
    return "request_additional_search_or_comparison_rows"


def _suggested_focus(
    *,
    risk_tier: str,
    overlap_level: str,
    missing_project_elements: str,
) -> list[str]:
    focus = [
        "Confirm whether the cited source discloses the full seven-layer closed loop or only one component.",
        "Preserve field replay, operator review and release gate as non-bypassable validation gates.",
        "Check whether low-cost sparse observation, cyclic delay budget and hidden-state evidence are jointly present.",
    ]
    text = f"{risk_tier} {overlap_level} {missing_project_elements}".lower()
    if "catalyst" in text:
        focus.append(
            "Focus on operational catalyst-activity guardrails, not AI catalyst discovery alone."
        )
    if "sensor" in text or "sparse" in text:
        focus.append(
            "Separate generic sparse sensor placement from node-modality hidden-state evidence contracts."
        )
    if "multi-agent" in text or "control" in text:
        focus.append(
            "Separate generic multi-agent control from evidence-gated no-write arbitration."
        )
    return focus
