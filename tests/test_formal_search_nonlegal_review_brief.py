import json

from water_ai.agents.agent_architecture_consolidation_agent import (
    AGENT_MODULE_MAP,
    AgentArchitectureConsolidationAgent,
)
from water_ai.formal_search_nonlegal_review_brief import (
    build_formal_search_ai_nonlegal_review_brief,
)
from water_ai.preliminary_formal_search_package import (
    build_preliminary_formal_search_result_package,
)


def _agent60_with_preliminary_package(tmp_path):
    baseline = AgentArchitectureConsolidationAgent(agent_names=list(AGENT_MODULE_MAP)).run([])
    package = build_preliminary_formal_search_result_package(
        baseline.metrics["formal_search_execution_route_plan"]
    )
    package_path = tmp_path / "preliminary_formal_search_result_package.json"
    package_path.write_text(json.dumps(package, ensure_ascii=False), encoding="utf-8")
    replay = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        formal_search_result_package_path=str(package_path),
    ).run([])
    return package, replay


def test_ai_nonlegal_review_brief_maps_all_rows_to_claim_scaffolds(tmp_path) -> None:
    package, replay = _agent60_with_preliminary_package(tmp_path)
    brief = build_formal_search_ai_nonlegal_review_brief(
        preliminary_formal_search_result_package=package,
        nonlegal_comparison_review_packet=replay.metrics[
            "formal_search_nonlegal_comparison_review_packet"
        ],
        technical_claim_skeleton_scaffold=replay.metrics[
            "technical_claim_skeleton_scaffold"
        ],
    )

    readiness = brief["review_readiness"]
    assert brief["brief_metadata"]["brief_status"] == (
        "formal_search_ai_nonlegal_review_brief_ready_for_human_review"
    )
    assert readiness["review_packet_row_count"] == 7
    assert readiness["brief_row_count"] == 7
    assert readiness["missing_source_row_count"] == 0
    assert readiness["missing_claim_mapping_row_count"] == 0
    assert readiness["can_help_human_nonlegal_review"] is True
    assert readiness["can_route_to_claim_scope_patch_draft"] is False

    for row in brief["brief_rows"]:
        assert row["url_or_reference"]
        assert row["mapped_claim_scaffold_ids"]
        assert row["distinguishing_technical_detail_from_preliminary_record"]
        assert row["human_review_completed"] is False
        assert row["cannot_route_to_claim_scope_patch_draft"] is True


def test_ai_nonlegal_review_brief_preserves_no_write_and_no_legal_boundaries(tmp_path) -> None:
    package, replay = _agent60_with_preliminary_package(tmp_path)
    brief = build_formal_search_ai_nonlegal_review_brief(
        preliminary_formal_search_result_package=package,
        nonlegal_comparison_review_packet=replay.metrics[
            "formal_search_nonlegal_comparison_review_packet"
        ],
        technical_claim_skeleton_scaffold=replay.metrics[
            "technical_claim_skeleton_scaffold"
        ],
    )

    boundary = brief["boundary"]
    readiness = brief["review_readiness"]
    assert boundary["can_emit_claim_text"] is False
    assert boundary["can_resume_model_chain"] is False
    assert boundary["can_write_to_actuator"] is False
    assert boundary["can_write_to_release_gate"] is False
    assert readiness["can_generate_prior_art_result"] is False
    assert readiness["legal_opinion_allowed"] is False
    assert readiness["field_claim_upgrade_allowed"] is False

    high_priority_rows = [
        row for row in brief["brief_rows"]
        if row["risk_tier_for_human_triage"] == "high_overlap_human_review_priority"
    ]
    assert high_priority_rows
    assert high_priority_rows[0]["ai_suggested_nonlegal_starting_option"] == (
        "mark_high_overlap_needs_external_patent_counsel_review"
    )
