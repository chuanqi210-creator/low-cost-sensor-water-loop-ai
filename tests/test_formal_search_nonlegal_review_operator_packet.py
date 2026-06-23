from water_ai.formal_search_nonlegal_review_operator_packet import (
    build_formal_search_nonlegal_review_operator_packet,
)


def test_operator_packet_compresses_human_review_handoff_without_unlocking_claim_patch() -> None:
    packet = build_formal_search_nonlegal_review_operator_packet(
        ai_nonlegal_review_brief=_ready_ai_brief(),
        nonlegal_review_response_template=_response_template(),
        nonlegal_review_response_source_preflight=_waiting_preflight(),
        formal_search_review_readiness=_review_readiness(),
        claim_scope_patch_draft=_claim_scope_patch_draft(),
    )

    metadata = packet["operator_packet_metadata"]
    action = packet["operator_action"]
    contract = packet["response_contract"]
    downstream = packet["downstream_state"]
    boundary = packet["boundary"]

    assert metadata["packet_status"] == (
        "formal_search_nonlegal_review_operator_packet_ready_waiting_for_human_response"
    )
    assert action["source_env_var"] == "FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH"
    assert action["recommended_output_path"].endswith(
        "formal_search_nonlegal_review_response.json"
    )
    assert action["expected_review_packet_row_count"] == 2
    assert action["high_priority_review_row_count"] == 1
    assert action["accepted_review_row_count"] == 0
    assert action["rejected_review_row_count"] == 0
    assert "experiments/run_agent60_agent_architecture_consolidation.py" in (
        action["validation_commands"][0]
    )
    assert "experiments/run_agent50_model_core_governance.py" in (
        action["validation_commands"][1]
    )
    assert contract["expected_review_packet_row_ids"] == ["FSNR1", "FSNR2"]
    assert contract["template_row_count"] == 2
    assert len(packet["human_review_rows"]) == 2
    assert packet["human_review_rows"][0]["required_human_fields"] == [
        "review_packet_row_id",
        "human_nonlegal_overlap_assessment",
        "human_nonlegal_distinction_notes",
    ]
    assert "TODO/template marker remains" in packet["rejection_conditions"]
    assert downstream["can_route_to_claim_scope_patch_draft"] is False
    assert downstream["claim_scope_patch_draft_status"] == (
        "formal_search_claim_scope_patch_draft_blocked_at_nonlegal_review_response"
    )
    assert boundary["legal_opinion_allowed"] is False
    assert boundary["field_claim_upgrade_allowed"] is False
    assert boundary["can_emit_claim_text"] is False
    assert boundary["can_write_to_actuator"] is False
    assert boundary["can_write_to_release_gate"] is False


def test_operator_packet_blocks_when_ai_brief_boundary_is_not_preserved() -> None:
    brief = _ready_ai_brief()
    brief["boundary"]["can_emit_claim_text"] = True

    packet = build_formal_search_nonlegal_review_operator_packet(
        ai_nonlegal_review_brief=brief,
        nonlegal_review_response_template=_response_template(),
        nonlegal_review_response_source_preflight=_waiting_preflight(),
        formal_search_review_readiness=_review_readiness(),
        claim_scope_patch_draft=_claim_scope_patch_draft(),
    )

    assert packet["operator_packet_metadata"]["packet_status"] == (
        "formal_search_nonlegal_review_operator_packet_blocked_by_ai_brief"
    )
    assert packet["operator_action"]["next_operator_action"] == (
        "repair upstream AI brief, review template or review readiness before asking for human response"
    )
    assert packet["downstream_state"]["can_route_to_claim_scope_patch_draft"] is False


def test_operator_packet_marks_human_response_ready_but_preserves_no_claim_text_boundary() -> None:
    preflight = _waiting_preflight()
    preflight["formal_search_nonlegal_review_response_source_status"] = (
        "formal_search_nonlegal_review_response_ready_for_claim_scope_patch_draft"
    )
    preflight["review_response_supplied"] = True
    preflight["human_review_completed"] = True
    preflight["accepted_review_row_count"] = 2
    preflight["can_route_to_claim_scope_patch_draft"] = True

    packet = build_formal_search_nonlegal_review_operator_packet(
        ai_nonlegal_review_brief=_ready_ai_brief(),
        nonlegal_review_response_template=_response_template(),
        nonlegal_review_response_source_preflight=preflight,
        formal_search_review_readiness=_review_readiness(),
        claim_scope_patch_draft=_claim_scope_patch_draft(),
    )

    assert packet["operator_packet_metadata"]["packet_status"] == (
        "formal_search_nonlegal_review_operator_packet_human_response_ready_for_agent60_patch_gate"
    )
    assert packet["downstream_state"]["can_route_to_claim_scope_patch_draft"] is True
    assert packet["boundary"]["can_emit_claim_text"] is False
    assert packet["boundary"]["legal_opinion_allowed"] is False
    assert packet["boundary"]["field_claim_upgrade_allowed"] is False


def test_operator_packet_uses_ready_ai_brief_when_agent60_template_was_refreshed_without_upstream_package() -> None:
    blocked_template = _response_template()
    blocked_template["formal_search_nonlegal_review_response_template_status"] = (
        "formal_search_nonlegal_review_response_template_blocked_at_review_packet"
    )
    blocked_template["expected_review_packet_row_ids"] = []
    blocked_template["response_template_rows"] = []
    blocked_preflight = _waiting_preflight()
    blocked_preflight["formal_search_nonlegal_review_response_source_status"] = (
        "formal_search_nonlegal_review_response_preflight_blocked_at_template"
    )
    readiness = _review_readiness()
    readiness["formal_search_review_readiness_status"] = (
        "formal_search_review_blocked_at_result_package_source_preflight"
    )

    packet = build_formal_search_nonlegal_review_operator_packet(
        ai_nonlegal_review_brief=_ready_ai_brief(),
        nonlegal_review_response_template=blocked_template,
        nonlegal_review_response_source_preflight=blocked_preflight,
        formal_search_review_readiness=readiness,
        claim_scope_patch_draft=_claim_scope_patch_draft(),
        upstream_formal_search_result_package_path=(
            "outputs/agent_architecture_consolidation/"
            "preliminary_formal_search_result_package.json"
        ),
    )

    assert packet["operator_packet_metadata"]["packet_status"] == (
        "formal_search_nonlegal_review_operator_packet_ready_waiting_for_human_response"
    )
    assert packet["operator_action"]["upstream_source_env_var"] == (
        "FORMAL_SEARCH_RESULT_PACKAGE_PATH"
    )
    assert packet["operator_action"]["upstream_formal_search_result_package_path"].endswith(
        "preliminary_formal_search_result_package.json"
    )
    assert packet["operator_action"]["required_env_vars"] == [
        "FORMAL_SEARCH_RESULT_PACKAGE_PATH",
        "FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH",
    ]
    assert packet["operator_action"]["expected_review_packet_row_count"] == 2
    assert packet["response_contract"]["contract_basis"] == (
        "ai_brief_rows_with_upstream_formal_search_package_dependency"
    )
    assert packet["response_contract"]["expected_review_packet_row_ids"] == [
        "FSNR1",
        "FSNR2",
    ]
    assert packet["response_contract"]["template_row_count"] == 2
    assert len(packet["human_review_rows"]) == 2
    assert "FORMAL_SEARCH_RESULT_PACKAGE_PATH=" in packet["operator_action"][
        "validation_commands"
    ][0]
    assert "FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH=" in packet["operator_action"][
        "validation_commands"
    ][0]
    assert packet["downstream_state"]["can_route_to_claim_scope_patch_draft"] is False
    assert packet["boundary"]["can_emit_claim_text"] is False
    assert packet["boundary"]["can_write_to_actuator"] is False
    assert packet["boundary"]["can_write_to_release_gate"] is False


def _ready_ai_brief() -> dict[str, object]:
    return {
        "brief_metadata": {
            "brief_id": "R8u134_formal_search_ai_nonlegal_review_brief",
            "brief_status": "formal_search_ai_nonlegal_review_brief_ready_for_human_review",
        },
        "review_readiness": {
            "can_help_human_nonlegal_review": True,
            "can_route_to_claim_scope_patch_draft": False,
            "legal_opinion_allowed": False,
            "field_claim_upgrade_allowed": False,
        },
        "brief_rows": [
            {
                "review_packet_row_id": "FSNR1",
                "linked_work_package_id": "FSWP1",
                "hit_id": "HIT1",
                "risk_tier_for_human_triage": "component_overlap_human_review",
                "ai_suggested_nonlegal_starting_option": "mark_partial_overlap",
                "mapped_claim_scaffold_ids": ["TCS1"],
                "human_reviewer_must_confirm": ["confirm_scope"],
                "preserved_field_validation_gate_from_preliminary_record": "field_holdout",
                "evidence_boundary": "public_source_preliminary",
            },
            {
                "review_packet_row_id": "FSNR2",
                "linked_work_package_id": "FSWP6",
                "hit_id": "HIT2",
                "risk_tier_for_human_triage": "high_overlap_human_review_priority",
                "ai_suggested_nonlegal_starting_option": (
                    "mark_high_overlap_needs_external_patent_counsel_review"
                ),
                "mapped_claim_scaffold_ids": ["TCS3"],
                "human_reviewer_must_confirm": ["confirm_agent_overlap"],
                "preserved_field_validation_gate_from_preliminary_record": "field_holdout",
                "evidence_boundary": "public_source_preliminary",
            },
        ],
        "boundary": {
            "can_emit_claim_text": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        },
    }


def _response_template() -> dict[str, object]:
    return {
        "formal_search_nonlegal_review_response_template_status": (
            "formal_search_nonlegal_review_response_template_ready_waiting_for_human_submission"
        ),
        "expected_env_var": "FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH",
        "recommended_output_path": (
            "outputs/agent_architecture_consolidation/"
            "formal_search_nonlegal_review_response.json"
        ),
        "required_root_keys": ["review_metadata", "review_rows"],
        "review_metadata_required_fields": ["reviewer_name", "review_completed_at"],
        "review_row_required_fields": [
            "review_packet_row_id",
            "human_nonlegal_overlap_assessment",
            "human_nonlegal_distinction_notes",
        ],
        "expected_review_packet_row_ids": ["FSNR1", "FSNR2"],
        "response_template_rows": [
            {
                "review_packet_row_id": "FSNR1",
                "human_nonlegal_overlap_assessment": "TODO",
                "human_nonlegal_distinction_notes": "TODO",
                "template_only": True,
            },
            {
                "review_packet_row_id": "FSNR2",
                "human_nonlegal_overlap_assessment": "TODO",
                "human_nonlegal_distinction_notes": "TODO",
                "template_only": True,
            },
        ],
    }


def _waiting_preflight() -> dict[str, object]:
    return {
        "formal_search_nonlegal_review_response_source_status": (
            "formal_search_nonlegal_review_response_preflight_waiting_for_submission_path"
        ),
        "review_response_supplied": False,
        "human_review_completed": False,
        "accepted_review_row_count": 0,
        "rejected_review_row_count": 0,
        "can_route_to_claim_scope_patch_draft": False,
    }


def _review_readiness() -> dict[str, object]:
    return {
        "formal_search_review_readiness_status": (
            "formal_search_review_ready_for_human_nonlegal_comparison"
        )
    }


def _claim_scope_patch_draft() -> dict[str, object]:
    return {
        "formal_search_claim_scope_patch_draft_status": (
            "formal_search_claim_scope_patch_draft_blocked_at_nonlegal_review_response"
        )
    }
