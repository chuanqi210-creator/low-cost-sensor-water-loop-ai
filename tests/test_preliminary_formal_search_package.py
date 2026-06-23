import json

from water_ai.agents.agent_architecture_consolidation_agent import (
    AGENT_MODULE_MAP,
    AgentArchitectureConsolidationAgent,
)
from water_ai.preliminary_formal_search_package import (
    build_preliminary_formal_search_handoff,
    build_preliminary_formal_search_result_package,
)


def test_preliminary_formal_search_package_passes_agent60_preflight(tmp_path) -> None:
    baseline = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
    ).run([])
    package = build_preliminary_formal_search_result_package(
        baseline.metrics["formal_search_execution_route_plan"]
    )
    package_path = tmp_path / "preliminary_formal_search_result_package.json"
    package_path.write_text(json.dumps(package, ensure_ascii=False), encoding="utf-8")

    replay = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        formal_search_result_package_path=str(package_path),
    ).run([])
    source_preflight = replay.metrics["formal_search_result_package_source_preflight"]
    row_preflight = replay.metrics["formal_search_result_package_row_preflight"]
    validation_execution = replay.metrics["formal_search_result_validation_execution"]
    nonlegal_packet = replay.metrics["formal_search_nonlegal_comparison_review_packet"]

    assert package["_preflight_summary"]["package_status"] == (
        "preliminary_formal_search_result_package_complete"
    )
    assert package["_preflight_summary"]["filled_work_package_count"] == 7
    assert source_preflight["formal_search_result_package_source_status"] == (
        "formal_search_result_package_source_ready_for_validation_gate"
    )
    assert source_preflight["template_marker_gap_count"] == 0
    assert row_preflight["formal_search_result_package_row_preflight_status"] == (
        "formal_search_result_package_row_preflight_ready_for_validation_gate"
    )
    assert row_preflight["checked_work_package_count"] == 7
    assert row_preflight["checked_hit_row_count"] == 7
    assert row_preflight["row_gap_count"] == 0
    assert row_preflight["comparison_coverage_gap_count"] == 0
    assert row_preflight["forbidden_review_boundary_count"] == 0
    assert validation_execution["formal_search_result_validation_execution_status"] == (
        "formal_search_result_validation_execution_ready_for_human_nonlegal_comparison_review"
    )
    assert validation_execution["validated_hit_count"] == 7
    assert validation_execution["rejected_hit_count"] == 0
    assert validation_execution["can_enter_human_nonlegal_comparison_review"] is True
    assert validation_execution["can_generate_prior_art_result"] is False
    assert validation_execution["legal_opinion_allowed"] is False
    assert validation_execution["field_claim_upgrade_allowed"] is False
    assert nonlegal_packet["formal_search_nonlegal_comparison_review_packet_status"] == (
        "formal_search_nonlegal_review_packet_ready_waiting_for_human_review"
    )
    assert nonlegal_packet["review_packet_row_count"] == 7


def test_preliminary_formal_search_handoff_keeps_no_write_boundaries() -> None:
    baseline = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
    ).run([])
    package = build_preliminary_formal_search_result_package(
        baseline.metrics["formal_search_execution_route_plan"]
    )
    handoff = build_preliminary_formal_search_handoff(
        package,
        package_path="/tmp/preliminary_formal_search_result_package.json",
    )

    assert handoff["handoff_status"] == (
        "preliminary_formal_search_package_ready_for_FORMAL_SEARCH_RESULT_PACKAGE_PATH"
    )
    assert handoff["source_env_var"] == "FORMAL_SEARCH_RESULT_PACKAGE_PATH"
    assert handoff["filled_work_package_count"] == 7
    assert handoff["expected_work_package_count"] == 7
    assert handoff["can_route_to_agent60_formal_search_preflight"] is True
    assert handoff["can_resume_model_chain"] is False
    assert handoff["can_write_to_actuator"] is False
    assert handoff["can_write_to_release_gate"] is False
    assert handoff["can_generate_prior_art_result"] is False
    assert handoff["legal_opinion_allowed"] is False
    assert handoff["field_claim_upgrade_allowed"] is False
