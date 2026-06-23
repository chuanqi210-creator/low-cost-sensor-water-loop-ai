from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


PACKAGE_ID = "R8u133_preliminary_formal_search_result_package"
REVIEWER_ID = "codex_preliminary_external_search"
SEARCH_EXECUTOR = "codex_web_search"
SEARCH_DATE = "2026-06-22"


HIT_LIBRARY: dict[str, dict[str, object]] = {
    "FSWP1_cyclic_greybox_soft_sensor_release_gate_search": {
        "source_database": "Google Patents",
        "publication_or_patent_id": "EP2414901B1",
        "title": "System and method for monitoring an integrated system",
        "assignee_or_authors": "BL Technologies Inc; Vijaysai Prasad et al.",
        "publication_date": "2019-05-22",
        "url_or_reference": "https://patents.google.com/patent/EP2414901B1/en",
        "matched_query": '"low cost sensor" "grey-box" "wastewater" "closed-loop control"',
        "disclosed_capabilities": (
            "Water purification monitoring with soft sensing, estimator, predictor, "
            "supervisory control and integrated treatment units."
        ),
        "missing_project_elements": (
            "No node-modality sparse sensing contract, no low-frequency cyclic evidence window, "
            "and no replay/operator/release-gate sequence for writeback."
        ),
        "overlap_level": "partial",
        "risk_signal": "medium_overlap_requires_review",
        "comparison_element": "PTF2_soft_sensor_grey_state_estimation + PTF4_cyclic_low_frequency_control",
        "project_element_text": (
            "Project combines sparse observation, soft-sensor grey-state estimation, cyclic hold/recycle "
            "time buffer and evidence-gated release control."
        ),
        "prior_art_disclosure_text": (
            "Reference describes real-time parameter estimation, present-state comparison, event prediction "
            "and supervisory execution for water purification components."
        ),
        "distinguishing_detail": (
            "Reference is broader integrated monitoring/control; it does not expose the project's "
            "state-level external evidence package, focused catalyst response gate or replay/release boundary."
        ),
    },
    "FSWP2_node_modality_sparse_hidden_state_search": {
        "source_database": "GitHub",
        "publication_or_patent_id": "dynamicslab/pysensors; JOSS 2021",
        "title": "PySensors: sparse sensor placement for reconstruction or classification",
        "assignee_or_authors": "Brian M. de Silva, Krithika Manohar, Emily Clark, Bingni W. Brunton, J. Nathan Kutz, Steven L. Brunton",
        "publication_date": "2021",
        "url_or_reference": "https://github.com/dynamicslab/pysensors",
        "matched_query": '"SSPOR" OR "SSPOC" "water quality" "sensor placement"',
        "disclosed_capabilities": (
            "Sparse sensor selection for reconstruction and classification, including constrained "
            "sensor placement options."
        ),
        "missing_project_elements": (
            "No water-treatment node-modality contract, no catalyst-activity hidden-state evidence rows, "
            "and no downstream field holdout or actuator boundary."
        ),
        "overlap_level": "method_component_overlap",
        "risk_signal": "sensor_placement_component_requires_scope_split",
        "comparison_element": "PTF1_node_modality_sparse_sensing",
        "project_element_text": (
            "Project constrains sparse sensing by water-treatment node, modality, hidden state, "
            "missingness, field evidence and downstream control gate."
        ),
        "prior_art_disclosure_text": (
            "Reference provides generic sparse sensor placement algorithms for reconstruction and "
            "classification with basis and optimizer choices."
        ),
        "distinguishing_detail": (
            "Reference is not a water-treatment evidence contract and does not link selected sensors to "
            "catalyst guardrails, focused field response rows or release-gate validation."
        ),
    },
    "FSWP3_greybox_multi_agent_safety_arbitration_search": {
        "source_database": "Google Scholar",
        "publication_or_patent_id": "Nature npj Clean Water s41545-025-00512-z",
        "title": "Pollution-based integrated real-time control for urban drainage systems: a multi-agent deep reinforcement learning approach",
        "assignee_or_authors": "npj Clean Water authors",
        "publication_date": "2025",
        "url_or_reference": "https://www.nature.com/articles/s41545-025-00512-z",
        "matched_query": '"multi-agent" "wastewater" "grey-box" "safety arbitration"',
        "disclosed_capabilities": (
            "Multi-agent deep reinforcement learning for pollution-based real-time control in "
            "urban drainage systems."
        ),
        "missing_project_elements": (
            "No catalyst-activity guardrail, no knowledge-source action constraint, no no-write "
            "field replay boundary, and no focused external evidence package."
        ),
        "overlap_level": "control_architecture_overlap",
        "risk_signal": "multi_agent_control_overlap_requires_guardrail_distinction",
        "comparison_element": "PTF7_engineering_execution_constraints + PTF8_stage_gated_model_governance",
        "project_element_text": (
            "Project uses multi-agent diagnosis/control only after observation, grey-box, evidence, "
            "engineering and replay gates preserve protective boundaries."
        ),
        "prior_art_disclosure_text": (
            "Reference applies multi-agent learning to coordinated drainage control using pollution-oriented "
            "objectives."
        ),
        "distinguishing_detail": (
            "Reference does not disclose the project's staged field-evidence route, catalyst proxy holdout, "
            "formal no-write operator package or grey-box mechanism arbitration chain."
        ),
    },
    "FSWP4_low_cost_observation_gated_flowsheet_search": {
        "source_database": "WaterTAP/QSDsan/Pyomo documentation",
        "publication_or_patent_id": "WaterTAP documentation",
        "title": "WaterTAP water treatment process modeling and optimization documentation",
        "assignee_or_authors": "WaterTAP development team",
        "publication_date": "2026",
        "url_or_reference": "https://watertap.readthedocs.io/en/latest/index.html",
        "matched_query": '"water treatment" "flowsheet" "low-cost sensors" "control"',
        "disclosed_capabilities": (
            "Open-source water-treatment process modeling, costing and optimization workflows."
        ),
        "missing_project_elements": (
            "No low-cost observation sufficiency gate, no cyclic delay budget for low-frequency evidence, "
            "and no field response package for hidden-state validation."
        ),
        "overlap_level": "flowsheet_modeling_component_overlap",
        "risk_signal": "process_modeling_component_requires_observation_gate_distinction",
        "comparison_element": "PTF3_grey_box_mechanism_boundary + PTF7_engineering_execution_constraints",
        "project_element_text": (
            "Project uses process/engineering constraints as part of a grey-box closed loop that refuses "
            "writeback until field replay and operator gates pass."
        ),
        "prior_art_disclosure_text": (
            "Reference provides process-modeling and optimization infrastructure for water treatment."
        ),
        "distinguishing_detail": (
            "Reference is a modeling framework rather than a sensor-limited cyclic evidence-gated "
            "control architecture."
        ),
    },
    "FSWP5_scientific_kg_action_constraint_claim_gate_search": {
        "source_database": "Google Scholar",
        "publication_or_patent_id": "HICAI-ZJU/SciKGs survey repository",
        "title": "A Survey on Knowledge Graphs in AI for Science",
        "assignee_or_authors": "HICAI-ZJU/SciKGs authors",
        "publication_date": "2026",
        "url_or_reference": "https://github.com/HICAI-ZJU/SciKGs",
        "matched_query": '"scientific knowledge graph" "water treatment" "control constraint"',
        "disclosed_capabilities": (
            "Scientific knowledge graph survey resources for organizing AI-for-science entities, "
            "relations and evidence."
        ),
        "missing_project_elements": (
            "No water-treatment actuator constraint, no release-gate tie-in, and no field package "
            "validation path."
        ),
        "overlap_level": "evidence_organization_overlap",
        "risk_signal": "kg_component_requires_action_gate_distinction",
        "comparison_element": "PTF5_mechanism_kg_evidence_constraint",
        "project_element_text": (
            "Project uses mechanism/source-basis records to constrain diagnostic and control candidates "
            "inside a water-treatment field validation chain."
        ),
        "prior_art_disclosure_text": (
            "Reference surveys knowledge graphs for AI-for-science knowledge organization."
        ),
        "distinguishing_detail": (
            "Reference does not itself define a wastewater control action boundary, no-write operator packet, "
            "or field replay release gate."
        ),
    },
    "FSWP6_operational_catalyst_activity_guardrail_search": {
        "source_database": "Google Scholar",
        "publication_or_patent_id": "Nature Water 4, 630-642 (2026)",
        "title": "Multi-agent artificial intelligence designs novel catalysts for ultrafast water purification",
        "assignee_or_authors": "Yao Pan, Junxi Guo, Yizhan Huang et al.",
        "publication_date": "2026-04-30",
        "url_or_reference": "https://www.nature.com/articles/s44221-026-00634-9",
        "matched_query": '"AI" "catalyst discovery" "wastewater" "closed-loop control"',
        "disclosed_capabilities": (
            "Multi-agent AI, expert-validated knowledge graphs and catalyst evaluation for "
            "water purification material discovery."
        ),
        "missing_project_elements": (
            "No operational low-cost catalyst-activity proxy holdout, no cyclic treatment action policy, "
            "and no actuator/release no-write gate."
        ),
        "overlap_level": "strong_material_discovery_overlap",
        "risk_signal": "catalyst_ai_overlap_requires_operational_guardrail_focus",
        "comparison_element": "PTF2_soft_sensor_grey_state_estimation + PTF6_field_replay_release_gate",
        "project_element_text": (
            "Project treats catalyst activity as an operational hidden state estimated from low-cost proxy "
            "signals and blocked from control relaxation until field holdout evidence exists."
        ),
        "prior_art_disclosure_text": (
            "Reference presents multi-agent AI for PMS-activating catalyst design and water-purification "
            "performance validation."
        ),
        "distinguishing_detail": (
            "Reference is primarily material discovery; it does not disclose the project's low-cost "
            "sensor-cycle-control guardrail and field response merge path."
        ),
    },
    "FSWP7_pressure_resolution_protective_release_gate_search": {
        "source_database": "Google Scholar",
        "publication_or_patent_id": "arXiv:2006.04779",
        "title": "Conservative Q-Learning for Offline Reinforcement Learning",
        "assignee_or_authors": "Aviral Kumar, Aurick Zhou, George Tucker, Sergey Levine",
        "publication_date": "2020",
        "url_or_reference": "https://arxiv.org/abs/2006.04779",
        "matched_query": '"field replay" "release gate" "wastewater"',
        "disclosed_capabilities": (
            "Offline reinforcement learning method designed to learn from logged data while reducing "
            "over-optimistic action values."
        ),
        "missing_project_elements": (
            "No water-treatment pressure-source conflict semantics, no same-batch provenance bundle, "
            "and no operator-reviewed release gate for actuator writeback."
        ),
        "overlap_level": "offline_policy_evaluation_component_overlap",
        "risk_signal": "offline_rl_component_requires_domain_gate_distinction",
        "comparison_element": "PTF6_field_replay_release_gate + PTF8_stage_gated_model_governance",
        "project_element_text": (
            "Project requires pressure/source provenance, same-batch replay rows, operator review and "
            "release-gate blocking before protective writeback."
        ),
        "prior_art_disclosure_text": (
            "Reference provides a conservative offline RL algorithmic basis for learning from logged data."
        ),
        "distinguishing_detail": (
            "Reference is not a water-treatment pressure-resolution package and does not define the "
            "project's field provenance or release gate evidence chain."
        ),
    },
}


def build_preliminary_formal_search_result_package(
    formal_search_execution_route_plan: dict[str, Any],
) -> dict[str, Any]:
    route_rows = formal_search_execution_route_plan.get("route_rows", [])
    if not isinstance(route_rows, list):
        route_rows = []

    work_package_results: dict[str, dict[str, object]] = {}
    for index, route in enumerate(route_rows, start=1):
        if not isinstance(route, dict):
            continue
        work_package_id = str(route.get("linked_work_package_id", ""))
        if not work_package_id:
            continue
        hit = HIT_LIBRARY.get(work_package_id)
        if hit is None:
            continue
        work_package_results[work_package_id] = _work_package_result(index, route, hit)

    expected_ids = [
        str(route.get("linked_work_package_id", ""))
        for route in route_rows
        if isinstance(route, dict) and route.get("linked_work_package_id")
    ]
    missing_ids = [work_package_id for work_package_id in expected_ids if work_package_id not in work_package_results]

    package = {
        "package_metadata": {
            "package_id": PACKAGE_ID,
            "package_type": "formal_search_result_package",
            "search_executor": SEARCH_EXECUTOR,
            "search_date": SEARCH_DATE,
            "reviewer_id": REVIEWER_ID,
            "review_time": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "review_boundary_statement": "Comparison record only; no grant prediction or field upgrade asserted.",
            "legal_status": "not_legal_opinion",
            "evidence_status": "external_public_source_preliminary_record",
        },
        "work_package_results": work_package_results,
    }
    package["_preflight_summary"] = {
        "package_status": (
            "preliminary_formal_search_result_package_complete"
            if not missing_ids
            else "preliminary_formal_search_result_package_missing_routes"
        ),
        "expected_work_package_count": len(expected_ids),
        "filled_work_package_count": len(work_package_results),
        "missing_work_package_ids": missing_ids,
        "can_route_to_agent60_formal_search_preflight": not missing_ids,
        "can_generate_prior_art_result": False,
        "legal_opinion_allowed": False,
        "field_claim_upgrade_allowed": False,
        "boundary": (
            "This is a preliminary public-source comparison package for Agent60 preflight and "
            "human nonlegal technical review; it does not rank patentability, does not emit claim text, "
            "and does not upgrade any field claim."
        ),
    }
    return package


def build_preliminary_formal_search_handoff(
    package: dict[str, Any],
    *,
    package_path: str,
) -> dict[str, object]:
    summary = package.get("_preflight_summary", {})
    if not isinstance(summary, dict):
        summary = {}
    return {
        "handoff_id": "R8u133_preliminary_formal_search_handoff",
        "handoff_status": "preliminary_formal_search_package_ready_for_FORMAL_SEARCH_RESULT_PACKAGE_PATH",
        "package_path": package_path,
        "source_env_var": "FORMAL_SEARCH_RESULT_PACKAGE_PATH",
        "validation_commands": [
            f"export FORMAL_SEARCH_RESULT_PACKAGE_PATH={package_path}",
            ".venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py",
            ".venv/bin/python experiments/run_external_activation_router.py",
            ".venv/bin/python experiments/run_agent50_model_core_governance.py",
        ],
        "filled_work_package_count": int(summary.get("filled_work_package_count", 0)),
        "expected_work_package_count": int(summary.get("expected_work_package_count", 0)),
        "can_route_to_agent60_formal_search_preflight": bool(
            summary.get("can_route_to_agent60_formal_search_preflight", False)
        ),
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "can_generate_prior_art_result": False,
        "legal_opinion_allowed": False,
        "field_claim_upgrade_allowed": False,
    }


def _work_package_result(
    index: int,
    route: dict[str, object],
    hit: dict[str, object],
) -> dict[str, object]:
    work_package_id = str(route["linked_work_package_id"])
    hit_id = f"R8U133_HIT_{index:02d}"
    comparison_id = f"R8U133_CMP_{index:02d}"
    matched_query = str(hit["matched_query"])
    source_database = str(hit["source_database"])
    return {
        "package_manifest": {
            "package_id": f"R8U133_FSRP_{index:02d}",
            "linked_work_package_id": work_package_id,
            "search_executor": SEARCH_EXECUTOR,
            "search_date": SEARCH_DATE,
            "databases_searched": [source_database],
            "query_log": [matched_query],
            "reviewer_id": REVIEWER_ID,
            "review_time": "2026-06-22T00:00:00Z",
            "review_boundary_statement": "Comparison record only; no grant prediction or field upgrade asserted.",
            "legal_status": "not_legal_opinion",
            "evidence_status": "external_public_source_preliminary_record",
        },
        "prior_art_hit_table": [
            {
                "hit_id": hit_id,
                "linked_work_package_id": work_package_id,
                "source_database": source_database,
                "publication_or_patent_id": hit["publication_or_patent_id"],
                "title": hit["title"],
                "assignee_or_authors": hit["assignee_or_authors"],
                "publication_date": hit["publication_date"],
                "url_or_reference": hit["url_or_reference"],
                "matched_query": matched_query,
                "matched_claim_elements": [hit["comparison_element"]],
                "disclosed_capabilities": hit["disclosed_capabilities"],
                "missing_project_elements": hit["missing_project_elements"],
                "overlap_level": hit["overlap_level"],
                "novelty_risk_signal": hit["risk_signal"],
                "combination_risk_signal": "human_nonlegal_combination_review_needed",
                "reviewer_id": REVIEWER_ID,
                "review_status": "reviewed_for_preliminary_structural_comparison",
                "legal_status": "not_legal_opinion",
                "evidence_status": "external_public_source_preliminary_record",
            }
        ],
        "claim_element_comparison_chart": [
            {
                "comparison_id": comparison_id,
                "linked_hit_id": hit_id,
                "linked_work_package_id": work_package_id,
                "claim_or_feature_element": hit["comparison_element"],
                "project_element_text": hit["project_element_text"],
                "prior_art_disclosure_text": hit["prior_art_disclosure_text"],
                "match_level": hit["overlap_level"],
                "missing_or_distinguishing_detail": hit["distinguishing_detail"],
                "fallback_claim_scope_impact": "keep narrow technical scope pending human comparison review",
                "field_validation_gate_to_preserve": "field replay, operator review and release gate",
                "reviewer_decision": "comparison_record_only",
                "legal_status": "not_legal_opinion",
                "evidence_status": "external_public_source_preliminary_record",
            }
        ],
        "fallback_claim_scope_recommendation": [
            {
                "linked_work_package_id": work_package_id,
                "claim_scope_decision_option": "retain_candidate_scope_pending_human_nonlegal_review",
                "decision_rationale": "preliminary external source shows partial overlap but not the full system chain",
                "triggering_hit_ids": [hit_id],
                "preserved_field_validation_gate": "field replay, operator review and release gate",
                "reviewer_id": REVIEWER_ID,
                "legal_status": "not_legal_opinion",
                "evidence_status": "external_public_source_preliminary_record",
            }
        ],
    }
