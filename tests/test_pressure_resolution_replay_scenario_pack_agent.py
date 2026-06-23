import csv
import json

from experiments.run_agent61_pressure_resolution_replay_scenario_pack import (
    _field_rows_batch_bundle_preflight,
    _field_rows_collection_checklist,
    _field_rows_downstream_route_handoff,
    _field_rows_downstream_routing_preflight,
    _field_rows_downstream_target_gate_result_arbitration,
    _field_rows_downstream_target_gate_result_intake_schema,
    _field_rows_downstream_target_gate_operator_review_preflight,
    _field_rows_downstream_target_gate_operator_review_template,
    _field_rows_downstream_target_gate_post_review_gate,
    _field_rows_downstream_target_gate_protective_candidate_evaluation,
    _field_rows_downstream_target_gate_result_preflight,
    _field_rows_downstream_target_gate_preflight,
    _field_rows_patch_plan,
    _field_rows_package_schema,
    _field_rows_scenario_semantic_preflight,
    _field_rows_schema_validation,
    _field_rows_temporal_window_preflight,
    _field_rows_operator_handoff,
    _field_rows_r7_alignment,
    _field_rows_r7_completion_plan,
    _field_rows_r7_completion_route_contracts,
    _field_rows_r7_completion_route_work_packages,
    _field_rows_r7_completion_route_work_package_assembly_gate,
    _field_rows_r7_completion_route_work_package_patch_plan,
    _field_rows_r7_completion_route_work_package_submission_preflight,
    _field_rows_r7_staging_preflight,
    _field_rows_source_package_route_preflight,
    _field_rows_source_package_submission_route_guide,
    _field_rows_submission_readiness_review,
    _read_field_rows_package,
    _required_fields_for_table,
    _write_field_rows_csv_template,
    _write_r7_completion_route_work_package_templates,
)
from water_ai.agents.pressure_resolution_replay_scenario_pack_agent import (
    PRESSURE_RESOLUTION_SCENARIOS,
    REQUIRED_TABLE_FIELDS,
    PressureResolutionReplayScenarioPackAgent,
)


def test_pressure_resolution_replay_scenario_pack_is_schema_ready_but_blocks_without_field_rows() -> None:
    report = PressureResolutionReplayScenarioPackAgent(
        r7_pipeline_metrics=_r7_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        collaborative_control_metrics=_collaborative_control_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
    ).run([])

    readiness = report.metrics["readiness"]
    row_readiness = report.metrics["row_collection_readiness"]
    matrix = report.metrics["pressure_resolution_replay_scenario_matrix"]
    row_plan = report.metrics["row_collection_plan"]
    template_rows = report.metrics["template_rows_by_table"]

    assert readiness["scenario_pack_status"] == "pressure_resolution_scenario_pack_ready_needs_real_replay_rows"
    assert readiness["scenario_schema_coverage"] == 1.0
    assert readiness["field_scenario_coverage"] == 0.0
    assert readiness["source_chain_resolution_fields_ready"] is True
    assert readiness["can_update_agent60_fallback"] is True
    assert readiness["can_upgrade_field_supported_claim"] is False
    assert readiness["can_write_to_actuator"] is False
    assert readiness["can_write_to_release_gate"] is False
    assert len(matrix) == len(PRESSURE_RESOLUTION_SCENARIOS)
    assert all(row["scenario_schema_ready"] for row in matrix)
    assert all(not row["field_evidence_ready"] for row in matrix)
    assert row_readiness["row_collection_plan_status"] == "row_collection_plan_ready_needs_real_rows"
    assert row_readiness["missing_scenario_count"] == len(PRESSURE_RESOLUTION_SCENARIOS)
    assert row_readiness["minimum_real_batch_count"] == len(PRESSURE_RESOLUTION_SCENARIOS)
    assert row_readiness["template_rows_are_field_evidence"] is False
    assert row_readiness["can_write_to_actuator"] is False
    assert row_readiness["can_write_to_release_gate"] is False
    assert len(row_plan) == len(PRESSURE_RESOLUTION_SCENARIOS)
    assert all(row["cannot_write_to_actuator"] for row in row_plan)
    assert all(row["cannot_write_to_release_gate"] for row in row_plan)
    assert set(template_rows) == {*REQUIRED_TABLE_FIELDS, "agent52_replay_table"}
    assert row_readiness["template_row_count"] == len(PRESSURE_RESOLUTION_SCENARIOS) * (
        len(REQUIRED_TABLE_FIELDS) + 1
    )
    assert all(row["template_only"] for rows in template_rows.values() for row in rows)
    assert all(row["evidence_status"] == "template_not_field_evidence" for rows in template_rows.values() for row in rows)
    assert any(issue.issue_type == "pressure_resolution_field_replay_rows_required" for issue in report.issues)


def test_pressure_resolution_replay_scenario_pack_accepts_complete_field_scenario_evidence() -> None:
    evidence = {scenario["scenario_id"]: 1 for scenario in PRESSURE_RESOLUTION_SCENARIOS}
    replay_metrics = _replay_evaluation_metrics()
    replay_metrics["pressure_resolution_replay_scenario_evidence"] = evidence
    report = PressureResolutionReplayScenarioPackAgent(
        r7_pipeline_metrics=_r7_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        collaborative_control_metrics=_collaborative_control_metrics(),
        replay_evaluation_metrics=replay_metrics,
    ).run([])

    readiness = report.metrics["readiness"]
    row_readiness = report.metrics["row_collection_readiness"]
    writeback = report.metrics["agent60_writeback"]

    assert readiness["scenario_pack_status"] == "pressure_resolution_scenario_pack_field_replay_ready_for_human_review"
    assert readiness["field_scenario_coverage"] == 1.0
    assert readiness["can_upgrade_field_supported_claim"] is True
    assert readiness["can_write_to_actuator"] is False
    assert readiness["can_write_to_release_gate"] is False
    assert readiness["next_recommended_core_action"] == (
        "R8v_route_pressure_resolution_rows_to_field_replay_and_holdout_gates"
    )
    assert row_readiness["row_collection_plan_status"] == "row_collection_plan_field_scenarios_ready"
    assert row_readiness["missing_scenario_count"] == 0
    assert row_readiness["template_row_count"] == 0
    assert writeback["completion_status_for_architecture_consolidation"] == "R8o_pressure_resolution_scenario_pack_ready"
    assert writeback["recommended_next_fallback_action"] == (
        "R8v_route_pressure_resolution_rows_to_field_replay_and_holdout_gates"
    )
    assert not any(issue.issue_type == "pressure_resolution_scenario_missing_field_evidence" for issue in report.issues)


def test_pressure_resolution_replay_scenario_pack_accepts_complete_real_field_row_bundle() -> None:
    rows_by_table = _complete_field_rows_by_table()
    report = PressureResolutionReplayScenarioPackAgent(
        r7_pipeline_metrics=_r7_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        collaborative_control_metrics=_collaborative_control_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        field_replay_rows_by_table=rows_by_table,
    ).run([])
    source = {
        "field_rows_source_status": "field_rows_file_loaded",
        "field_rows_source_path": "memory://complete_rows",
        "expected_tables": sorted({*REQUIRED_TABLE_FIELDS, "agent52_replay_table"}),
        "missing_tables": [],
        "empty_tables": [],
        "invalid_table_shapes": [],
        "unknown_tables": [],
        "preflight_blockers": [],
        "table_count": len(REQUIRED_TABLE_FIELDS) + 1,
        "row_count": sum(len(rows) for rows in rows_by_table.values()),
    }
    schema = _field_rows_package_schema()
    validation = _field_rows_schema_validation(source, rows_by_table, schema)
    bundle_preflight = _field_rows_batch_bundle_preflight(report, source, rows_by_table, schema, validation)
    temporal_preflight = _field_rows_temporal_window_preflight(
        report,
        source,
        rows_by_table,
        validation,
        bundle_preflight,
    )
    semantic_preflight = _field_rows_scenario_semantic_preflight(
        report,
        source,
        rows_by_table,
        validation,
        bundle_preflight,
        temporal_preflight,
    )
    downstream_routing_preflight = _field_rows_downstream_routing_preflight(
        report,
        source,
        validation,
        bundle_preflight,
        temporal_preflight,
        semantic_preflight,
    )
    downstream_route_handoff = _field_rows_downstream_route_handoff(downstream_routing_preflight)
    downstream_target_gate_preflight = _field_rows_downstream_target_gate_preflight(
        downstream_route_handoff
    )
    result_intake_schema = _field_rows_downstream_target_gate_result_intake_schema(
        downstream_target_gate_preflight
    )
    result_preflight = _field_rows_downstream_target_gate_result_preflight(
        downstream_target_gate_preflight,
        result_intake_schema,
        None,
    )
    result_arbitration = _field_rows_downstream_target_gate_result_arbitration(result_preflight)

    readiness = report.metrics["readiness"]
    row_readiness = report.metrics["row_collection_readiness"]
    field_acceptance = report.metrics["field_row_acceptance"]

    assert bundle_preflight["field_rows_batch_bundle_preflight_status"] == (
        "batch_bundle_preflight_passed_ready_for_scenario_acceptance"
    )
    assert bundle_preflight["complete_bundle_count"] == len(PRESSURE_RESOLUTION_SCENARIOS)
    assert bundle_preflight["partial_bundle_count"] == 0
    assert bundle_preflight["scenario_bundle_ready_count"] == len(PRESSURE_RESOLUTION_SCENARIOS)
    assert temporal_preflight["field_rows_temporal_window_preflight_status"] == (
        "temporal_window_preflight_passed_ready_for_scenario_acceptance"
    )
    assert temporal_preflight["temporal_valid_batch_count"] == len(PRESSURE_RESOLUTION_SCENARIOS)
    assert temporal_preflight["temporal_violation_count"] == 0
    assert temporal_preflight["hold_time_violation_count"] == 0
    assert semantic_preflight["field_rows_scenario_semantic_preflight_status"] == (
        "scenario_semantic_preflight_passed_ready_for_scenario_acceptance"
    )
    assert semantic_preflight["semantic_valid_batch_count"] == len(PRESSURE_RESOLUTION_SCENARIOS)
    assert semantic_preflight["semantic_violation_count"] == 0
    assert semantic_preflight["scenario_semantic_ready_count"] == len(PRESSURE_RESOLUTION_SCENARIOS)
    assert downstream_routing_preflight["field_rows_downstream_routing_preflight_status"] == (
        "downstream_routing_preflight_passed_ready_for_r8v_field_replay_and_holdout_gates"
    )
    assert downstream_routing_preflight["routing_target_count"] == 4
    assert downstream_routing_preflight["routing_ready_target_count"] == 4
    assert downstream_routing_preflight["can_route_to_r8v"] is True
    assert downstream_routing_preflight["can_write_to_actuator"] is False
    assert downstream_routing_preflight["can_write_to_release_gate"] is False
    assert downstream_route_handoff["downstream_route_handoff_status"] == (
        "downstream_route_handoff_ready_for_r8v_target_gates"
    )
    assert downstream_route_handoff["handoff_target_count"] == 4
    assert downstream_route_handoff["ready_handoff_target_count"] == 4
    assert downstream_route_handoff["blocked_handoff_target_count"] == 0
    assert downstream_route_handoff["can_route_to_r8v"] is True
    assert downstream_route_handoff["can_write_to_actuator"] is False
    assert downstream_route_handoff["can_write_to_release_gate"] is False
    assert downstream_route_handoff["field_claim_upgrade_allowed"] is False
    assert downstream_target_gate_preflight["downstream_target_gate_preflight_status"] == (
        "downstream_target_gate_preflight_ready_for_r8v_execution"
    )
    assert downstream_target_gate_preflight["target_gate_count"] == 4
    assert downstream_target_gate_preflight["ready_target_gate_count"] == 4
    assert downstream_target_gate_preflight["blocked_target_gate_count"] == 0
    assert downstream_target_gate_preflight["can_execute_all_target_gates"] is True
    assert downstream_target_gate_preflight["can_write_to_actuator"] is False
    assert downstream_target_gate_preflight["can_write_to_release_gate"] is False
    assert result_intake_schema["expected_target_count"] == 4
    assert "agent51_catalyst_proxy_holdout" in result_intake_schema["expected_target_ids"]
    assert result_preflight["downstream_target_gate_result_preflight_status"] == (
        "downstream_target_gate_result_preflight_waiting_for_result_package"
    )
    assert result_preflight["missing_target_ids"] == result_intake_schema["expected_target_ids"]
    assert result_preflight["next_operator_action"] == "R8v_submit_target_gate_result_package"
    assert result_preflight["can_route_to_result_arbitration"] is False
    assert result_preflight["can_write_to_actuator"] is False
    assert result_preflight["can_write_to_release_gate"] is False
    assert result_arbitration["downstream_target_gate_result_arbitration_status"] == (
        "downstream_target_gate_result_arbitration_blocked_by_result_preflight"
    )
    assert result_arbitration["can_route_to_operator_review"] is False
    assert result_arbitration["can_emit_protective_control_candidate"] is False
    agent51_preflight = next(
        target
        for target in downstream_target_gate_preflight["target_gate_preflights"]
        if target["target_id"] == "agent51_catalyst_proxy_holdout"
    )
    assert agent51_preflight["validation_command"].endswith(
        "experiments/run_agent51_catalyst_activity_proxy.py"
    )
    agent49_preflight = next(
        target
        for target in downstream_target_gate_preflight["target_gate_preflights"]
        if target["target_id"] == "agent49_guardrail_context"
    )
    assert agent49_preflight["target_gate_output_contract"]["must_report_can_write_to_actuator"] is True
    r7_preflight = next(
        target
        for target in downstream_target_gate_preflight["target_gate_preflights"]
        if target["target_id"] == "r7_evidence_chain"
    )
    assert r7_preflight["target_gate_output_contract"]["must_report_can_write_to_release_gate"] is True
    agent49_handoff = next(
        target
        for target in downstream_route_handoff["handoff_targets"]
        if target["target_id"] == "agent49_guardrail_context"
    )
    assert agent49_handoff["gate_contract"]["must_run_before_control_or_release"] is True
    assert "actuator" in agent49_handoff["blocked_writes"]
    assert "release_gate" in agent49_handoff["blocked_writes"]
    assert field_acceptance["field_row_acceptance_status"] == "field_replay_rows_accepted_for_all_scenarios"
    assert field_acceptance["accepted_scenario_count"] == len(PRESSURE_RESOLUTION_SCENARIOS)
    assert field_acceptance["accepted_batch_count"] == len(PRESSURE_RESOLUTION_SCENARIOS)
    assert readiness["scenario_pack_status"] == "pressure_resolution_scenario_pack_field_replay_ready_for_human_review"
    assert readiness["field_scenario_coverage"] == 1.0
    assert readiness["accepted_field_scenario_count"] == len(PRESSURE_RESOLUTION_SCENARIOS)
    assert readiness["can_upgrade_field_supported_claim"] is True
    assert readiness["can_write_to_actuator"] is False
    assert readiness["can_write_to_release_gate"] is False
    assert row_readiness["row_collection_plan_status"] == "row_collection_plan_field_scenarios_ready"
    assert row_readiness["template_row_count"] == 0
    assert not any(issue.issue_type == "pressure_resolution_field_rows_rejected" for issue in report.issues)


def test_pressure_resolution_target_gate_result_preflight_accepts_full_result_package(tmp_path) -> None:
    downstream_target_gate_preflight, result_intake_schema = _ready_downstream_target_gate_preflight()
    result_package_path = tmp_path / "target_gate_results.json"
    result_package_path.write_text(
        json.dumps(
            _target_gate_result_package(result_intake_schema),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    result_preflight = _field_rows_downstream_target_gate_result_preflight(
        downstream_target_gate_preflight,
        result_intake_schema,
        result_package_path,
    )

    assert result_preflight["downstream_target_gate_result_preflight_status"] == (
        "downstream_target_gate_result_preflight_passed_ready_for_result_arbitration"
    )
    assert result_preflight["submitted_target_result_count"] == 4
    assert result_preflight["accepted_target_result_count"] == 4
    assert result_preflight["rejected_target_result_count"] == 0
    assert result_preflight["missing_target_ids"] == []
    assert result_preflight["unknown_target_ids"] == []
    assert result_preflight["can_route_to_result_arbitration"] is True
    assert result_preflight["can_write_to_actuator"] is False
    assert result_preflight["can_write_to_release_gate"] is False
    assert result_preflight["field_claim_upgrade_allowed"] is False
    result_arbitration = _field_rows_downstream_target_gate_result_arbitration(result_preflight)
    assert result_arbitration["downstream_target_gate_result_arbitration_status"] == (
        "downstream_target_gate_result_arbitration_ready_for_operator_review"
    )
    assert result_arbitration["target_gate_status_counts"]["target_gate_result_passed"] == 4
    assert result_arbitration["can_route_to_operator_review"] is True
    assert result_arbitration["can_emit_protective_control_candidate"] is False
    assert result_arbitration["can_write_to_actuator"] is False
    assert result_arbitration["can_write_to_release_gate"] is False


def test_pressure_resolution_target_gate_result_arbitration_blocks_failed_target(tmp_path) -> None:
    downstream_target_gate_preflight, result_intake_schema = _ready_downstream_target_gate_preflight()
    result_package_path = tmp_path / "target_gate_results_with_failure.json"
    result_package_path.write_text(
        json.dumps(
            _target_gate_result_package(
                result_intake_schema,
                status_by_target_id={"agent52_replay_clearance": "target_gate_result_failed"},
            ),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    result_preflight = _field_rows_downstream_target_gate_result_preflight(
        downstream_target_gate_preflight,
        result_intake_schema,
        result_package_path,
    )
    result_arbitration = _field_rows_downstream_target_gate_result_arbitration(result_preflight)

    assert result_preflight["downstream_target_gate_result_preflight_status"] == (
        "downstream_target_gate_result_preflight_passed_ready_for_result_arbitration"
    )
    assert result_arbitration["downstream_target_gate_result_arbitration_status"] == (
        "downstream_target_gate_result_arbitration_blocked_by_target_gate_failure"
    )
    assert result_arbitration["target_gate_status_counts"]["target_gate_result_failed"] == 1
    assert result_arbitration["can_route_to_operator_review"] is False
    assert result_arbitration["can_emit_protective_control_candidate"] is False
    assert result_arbitration["can_write_to_actuator"] is False
    assert result_arbitration["can_write_to_release_gate"] is False


def test_pressure_resolution_target_gate_result_preflight_blocks_protective_write_request(tmp_path) -> None:
    downstream_target_gate_preflight, result_intake_schema = _ready_downstream_target_gate_preflight()
    result_package_path = tmp_path / "target_gate_results_with_write_request.json"
    result_package_path.write_text(
        json.dumps(
            _target_gate_result_package(
                result_intake_schema,
                release_gate_write_target_id="r7_evidence_chain",
            ),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    result_preflight = _field_rows_downstream_target_gate_result_preflight(
        downstream_target_gate_preflight,
        result_intake_schema,
        result_package_path,
    )
    r7_validation = next(
        validation
        for validation in result_preflight["target_result_validations"]
        if validation["target_id"] == "r7_evidence_chain"
    )

    assert result_preflight["downstream_target_gate_result_preflight_status"] == (
        "downstream_target_gate_result_preflight_failed_protective_write_boundary"
    )
    assert result_preflight["can_route_to_result_arbitration"] is False
    assert result_preflight["can_write_to_actuator"] is False
    assert result_preflight["can_write_to_release_gate"] is False
    assert "target_result_requests_release_gate_write" in r7_validation["boundary_violations"]


def test_pressure_resolution_operator_review_blocks_until_result_arbitration_ready() -> None:
    downstream_target_gate_preflight, result_intake_schema = _ready_downstream_target_gate_preflight()
    result_preflight = _field_rows_downstream_target_gate_result_preflight(
        downstream_target_gate_preflight,
        result_intake_schema,
        None,
    )
    result_arbitration = _field_rows_downstream_target_gate_result_arbitration(result_preflight)
    review_template = _field_rows_downstream_target_gate_operator_review_template(result_arbitration)
    review_preflight = _field_rows_downstream_target_gate_operator_review_preflight(
        result_arbitration,
        review_template,
        None,
    )

    assert result_arbitration["downstream_target_gate_result_arbitration_status"] == (
        "downstream_target_gate_result_arbitration_blocked_by_result_preflight"
    )
    assert review_preflight["downstream_target_gate_operator_review_preflight_status"] == (
        "downstream_target_gate_operator_review_preflight_blocked_by_arbitration"
    )
    assert review_preflight["can_route_to_post_review_gate"] is False
    assert review_preflight["can_emit_protective_control_candidate"] is False
    assert review_preflight["can_write_to_actuator"] is False
    assert review_preflight["can_write_to_release_gate"] is False


def test_pressure_resolution_operator_review_waits_for_review_package_after_unanimous_arbitration(
    tmp_path,
) -> None:
    result_arbitration = _ready_downstream_target_gate_result_arbitration(tmp_path)
    review_template = _field_rows_downstream_target_gate_operator_review_template(result_arbitration)
    review_preflight = _field_rows_downstream_target_gate_operator_review_preflight(
        result_arbitration,
        review_template,
        None,
    )

    assert review_template["expected_target_count"] == 4
    assert review_preflight["downstream_target_gate_operator_review_preflight_status"] == (
        "downstream_target_gate_operator_review_preflight_waiting_for_review_package"
    )
    assert review_preflight["next_operator_action"] == "R8v_submit_operator_review_response_package"
    assert review_preflight["can_route_to_post_review_gate"] is False


def test_pressure_resolution_operator_review_accepts_approved_review_for_post_review_gate(tmp_path) -> None:
    result_arbitration = _ready_downstream_target_gate_result_arbitration(tmp_path)
    review_template = _field_rows_downstream_target_gate_operator_review_template(result_arbitration)
    review_package_path = tmp_path / "operator_review.json"
    review_package_path.write_text(
        json.dumps(
            _operator_review_package(review_template),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    review_preflight = _field_rows_downstream_target_gate_operator_review_preflight(
        result_arbitration,
        review_template,
        review_package_path,
    )

    assert review_preflight["downstream_target_gate_operator_review_preflight_status"] == (
        "downstream_target_gate_operator_review_preflight_passed_ready_for_post_review_gate"
    )
    assert review_preflight["submitted_operator_review_count"] == 4
    assert review_preflight["approved_operator_review_count"] == 4
    assert review_preflight["rejected_operator_review_count"] == 0
    assert review_preflight["hold_operator_review_count"] == 0
    assert review_preflight["can_route_to_post_review_gate"] is True
    assert review_preflight["can_emit_protective_control_candidate"] is False
    assert review_preflight["can_write_to_actuator"] is False
    assert review_preflight["can_write_to_release_gate"] is False
    assert review_preflight["field_claim_upgrade_allowed"] is False


def test_pressure_resolution_operator_review_blocks_protective_write_request(tmp_path) -> None:
    result_arbitration = _ready_downstream_target_gate_result_arbitration(tmp_path)
    review_template = _field_rows_downstream_target_gate_operator_review_template(result_arbitration)
    review_package_path = tmp_path / "operator_review_with_write.json"
    review_package_path.write_text(
        json.dumps(
            _operator_review_package(
                review_template,
                release_gate_write_target_id="r7_evidence_chain",
            ),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    review_preflight = _field_rows_downstream_target_gate_operator_review_preflight(
        result_arbitration,
        review_template,
        review_package_path,
    )
    r7_validation = next(
        validation
        for validation in review_preflight["operator_review_validations"]
        if validation["target_id"] == "r7_evidence_chain"
    )

    assert review_preflight["downstream_target_gate_operator_review_preflight_status"] == (
        "downstream_target_gate_operator_review_preflight_failed_protective_write_boundary"
    )
    assert review_preflight["can_route_to_post_review_gate"] is False
    assert review_preflight["can_emit_protective_control_candidate"] is False
    assert review_preflight["can_write_to_actuator"] is False
    assert review_preflight["can_write_to_release_gate"] is False
    assert "operator_review_requests_release_gate_write" in r7_validation["boundary_violations"]


def test_pressure_resolution_post_review_gate_blocks_until_operator_review_passes() -> None:
    result_preflight = {
        "downstream_target_gate_result_preflight_status": (
            "downstream_target_gate_result_preflight_blocked_by_target_gate_preflight"
        ),
        "expected_target_ids": ["agent51_catalyst_proxy_holdout"],
        "target_result_validations": [],
        "next_operator_action": "R8p_fix_field_rows_source_preflight",
    }
    result_arbitration = _field_rows_downstream_target_gate_result_arbitration(result_preflight)
    review_template = _field_rows_downstream_target_gate_operator_review_template(result_arbitration)
    review_preflight = _field_rows_downstream_target_gate_operator_review_preflight(
        result_arbitration,
        review_template,
        None,
    )
    post_review_gate = _field_rows_downstream_target_gate_post_review_gate(review_preflight)

    assert post_review_gate["downstream_target_gate_post_review_gate_status"] == (
        "downstream_target_gate_post_review_gate_blocked_by_operator_review_preflight"
    )
    assert post_review_gate["can_route_to_protective_candidate_evaluation"] is False
    assert post_review_gate["can_emit_protective_control_candidate"] is False
    assert post_review_gate["can_write_to_actuator"] is False
    assert post_review_gate["can_write_to_release_gate"] is False


def test_pressure_resolution_protective_candidate_evaluation_blocks_until_post_review_passes() -> None:
    result_preflight = {
        "downstream_target_gate_result_preflight_status": (
            "downstream_target_gate_result_preflight_blocked_by_target_gate_preflight"
        ),
        "expected_target_ids": ["agent51_catalyst_proxy_holdout"],
        "target_result_validations": [],
        "next_operator_action": "R8p_fix_field_rows_source_preflight",
    }
    result_arbitration = _field_rows_downstream_target_gate_result_arbitration(result_preflight)
    review_template = _field_rows_downstream_target_gate_operator_review_template(result_arbitration)
    review_preflight = _field_rows_downstream_target_gate_operator_review_preflight(
        result_arbitration,
        review_template,
        None,
    )
    post_review_gate = _field_rows_downstream_target_gate_post_review_gate(review_preflight)
    candidate_evaluation = _field_rows_downstream_target_gate_protective_candidate_evaluation(
        post_review_gate
    )

    assert candidate_evaluation["downstream_target_gate_protective_candidate_evaluation_status"] == (
        "protective_candidate_evaluation_blocked_by_post_review_gate"
    )
    assert candidate_evaluation["can_emit_protective_control_candidate"] is False
    assert candidate_evaluation["can_route_to_final_execution_review"] is False
    assert candidate_evaluation["can_write_to_actuator"] is False
    assert candidate_evaluation["can_write_to_release_gate"] is False


def test_pressure_resolution_post_review_gate_emits_only_protective_candidate_after_approval(
    tmp_path,
) -> None:
    result_arbitration = _ready_downstream_target_gate_result_arbitration(tmp_path)
    review_template = _field_rows_downstream_target_gate_operator_review_template(result_arbitration)
    review_package_path = tmp_path / "operator_review.json"
    review_package_path.write_text(
        json.dumps(
            _operator_review_package(review_template),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    review_preflight = _field_rows_downstream_target_gate_operator_review_preflight(
        result_arbitration,
        review_template,
        review_package_path,
    )
    post_review_gate = _field_rows_downstream_target_gate_post_review_gate(review_preflight)

    assert review_preflight["downstream_target_gate_operator_review_preflight_status"] == (
        "downstream_target_gate_operator_review_preflight_passed_ready_for_post_review_gate"
    )
    assert post_review_gate["downstream_target_gate_post_review_gate_status"] == (
        "downstream_target_gate_post_review_gate_passed_ready_for_protective_candidate_evaluation"
    )
    assert post_review_gate["approved_operator_review_count"] == 4
    assert len(post_review_gate["post_review_candidate_targets"]) == 4
    assert post_review_gate["can_route_to_protective_candidate_evaluation"] is True
    assert post_review_gate["can_emit_protective_control_candidate"] is True
    assert post_review_gate["can_write_to_actuator"] is False
    assert post_review_gate["can_write_to_release_gate"] is False
    assert post_review_gate["field_claim_upgrade_allowed"] is False
    assert all(
        target["can_write_to_actuator"] is False
        and target["can_write_to_release_gate"] is False
        for target in post_review_gate["post_review_candidate_targets"]
    )


def test_pressure_resolution_protective_candidate_evaluation_emits_candidate_not_actuator(
    tmp_path,
) -> None:
    result_arbitration = _ready_downstream_target_gate_result_arbitration(tmp_path)
    review_template = _field_rows_downstream_target_gate_operator_review_template(result_arbitration)
    review_package_path = tmp_path / "operator_review.json"
    review_package_path.write_text(
        json.dumps(
            _operator_review_package(review_template),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    review_preflight = _field_rows_downstream_target_gate_operator_review_preflight(
        result_arbitration,
        review_template,
        review_package_path,
    )
    post_review_gate = _field_rows_downstream_target_gate_post_review_gate(review_preflight)
    candidate_evaluation = _field_rows_downstream_target_gate_protective_candidate_evaluation(
        post_review_gate
    )

    assert candidate_evaluation["downstream_target_gate_protective_candidate_evaluation_status"] == (
        "protective_candidate_evaluation_passed_ready_for_final_execution_review"
    )
    assert candidate_evaluation["candidate_target_count"] == 4
    assert len(candidate_evaluation["target_contributions"]) == 4
    assert candidate_evaluation["can_emit_protective_control_candidate"] is True
    assert candidate_evaluation["can_route_to_final_execution_review"] is True
    assert candidate_evaluation["can_write_to_actuator"] is False
    assert candidate_evaluation["can_write_to_release_gate"] is False
    assert candidate_evaluation["field_claim_upgrade_allowed"] is False
    candidate_bundle = candidate_evaluation["candidate_action_bundle"]
    assert "keep_release_gate_blocked" in candidate_bundle["candidate_actions"]
    assert "actuator_safety_interlock_gate" in candidate_bundle["required_final_gates_before_execution"]
    assert candidate_bundle["can_write_to_actuator"] is False


def test_pressure_resolution_replay_scenario_pack_rejects_non_field_origin_in_any_required_table() -> None:
    rows = _complete_field_rows_by_table()
    rows["node_modality_sensor_timeseries"][0]["data_origin"] = "synthetic_lab_demo"
    report = PressureResolutionReplayScenarioPackAgent(
        r7_pipeline_metrics=_r7_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        collaborative_control_metrics=_collaborative_control_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        field_replay_rows_by_table=rows,
    ).run([])

    readiness = report.metrics["readiness"]
    field_acceptance = report.metrics["field_row_acceptance"]
    first_scenario = next(
        row
        for row in field_acceptance["scenario_acceptance"]
        if row["scenario_id"] == PRESSURE_RESOLUTION_SCENARIOS[0]["scenario_id"]
    )

    assert field_acceptance["field_row_acceptance_status"] == "field_replay_rows_partially_accepted"
    assert field_acceptance["accepted_scenario_count"] == len(PRESSURE_RESOLUTION_SCENARIOS) - 1
    assert readiness["can_upgrade_field_supported_claim"] is False
    assert "node_modality_sensor_timeseries:missing_real_required_fields_or_field_origin" in first_scenario[
        "blocking_reasons"
    ]
    assert any(issue.issue_type == "pressure_resolution_field_rows_rejected" for issue in report.issues)


def test_pressure_resolution_replay_scenario_pack_rejects_template_rows_as_field_evidence() -> None:
    template_report = PressureResolutionReplayScenarioPackAgent(
        r7_pipeline_metrics=_r7_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        collaborative_control_metrics=_collaborative_control_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
    ).run([])
    report = PressureResolutionReplayScenarioPackAgent(
        r7_pipeline_metrics=_r7_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        collaborative_control_metrics=_collaborative_control_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        field_replay_rows_by_table=template_report.metrics["template_rows_by_table"],
    ).run([])

    readiness = report.metrics["readiness"]
    field_acceptance = report.metrics["field_row_acceptance"]

    assert field_acceptance["field_row_acceptance_status"] == "field_replay_rows_present_but_not_accepted"
    assert field_acceptance["supplied_field_row_count"] > 0
    assert field_acceptance["accepted_scenario_count"] == 0
    assert readiness["field_scenario_coverage"] == 0.0
    assert readiness["can_upgrade_field_supported_claim"] is False
    assert any(issue.issue_type == "pressure_resolution_field_rows_rejected" for issue in report.issues)


def test_pressure_resolution_field_rows_package_preflight_reports_missing_file(tmp_path) -> None:
    rows, source = _read_field_rows_package(tmp_path / "missing_rows.json")
    report = PressureResolutionReplayScenarioPackAgent(
        r7_pipeline_metrics=_r7_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        collaborative_control_metrics=_collaborative_control_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        field_replay_rows_by_table=rows,
    ).run([])
    patch_plan = _field_rows_patch_plan(report, source)

    assert rows == {}
    assert source["field_rows_source_status"] == "field_rows_file_missing"
    assert source["row_count"] == 0
    assert source["missing_tables"] == sorted({*REQUIRED_TABLE_FIELDS, "agent52_replay_table"})
    assert "field_rows_file_missing" in source["preflight_blockers"]
    assert patch_plan["field_rows_patch_plan_status"] == "field_rows_patch_plan_blocked_at_source_preflight"
    assert patch_plan["highest_priority_patch_id"] == "R8P_SOURCE_MISSING_FIELD_ROWS_FILE"
    assert patch_plan["can_write_to_actuator"] is False
    assert patch_plan["can_write_to_release_gate"] is False


def test_pressure_resolution_operator_handoff_exposes_validation_path_for_missing_file(tmp_path) -> None:
    rows, source = _read_field_rows_package(tmp_path / "missing_rows.json")
    report = PressureResolutionReplayScenarioPackAgent(
        r7_pipeline_metrics=_r7_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        collaborative_control_metrics=_collaborative_control_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        field_replay_rows_by_table=rows,
    ).run([])
    patch_plan = _field_rows_patch_plan(report, source)
    handoff = _field_rows_operator_handoff(report, source, patch_plan)

    assert handoff["field_rows_operator_handoff_status"] == (
        "field_rows_operator_handoff_ready_needs_source_package"
    )
    assert handoff["env_override_name"] == "PRESSURE_RESOLUTION_REPLAY_ROWS_PATH"
    assert handoff["configured_field_rows_path"].endswith("missing_rows.json")
    assert handoff["default_field_rows_path"].endswith("pressure_resolution_replay_rows.json")
    assert handoff["template_rows_path"].endswith("pressure_resolution_replay_rows_template.json")
    assert handoff["rows_schema_path"].endswith("pressure_resolution_replay_rows_schema.json")
    assert handoff["field_rows_package_schema_status"] == "field_rows_package_schema_ready"
    assert handoff["field_rows_all_tables_require_data_origin"] is True
    assert handoff["field_rows_provenance_gate_status"] == "all_required_tables_require_field_origin"
    assert handoff["field_rows_provenance_required_table_count"] == 6
    assert handoff["validation_command_default"] == (
        ".venv/bin/python experiments/run_agent61_pressure_resolution_replay_scenario_pack.py"
    )
    assert "PRESSURE_RESOLUTION_REPLAY_ROWS_PATH=" in handoff["validation_command_with_env_override"]
    assert "source_preflight" in {item["milestone"] for item in handoff["acceptance_milestones"]}
    assert "agent52_replay_table" in handoff["required_tables"]
    assert "template_only=True" in " ".join(handoff["template_rejection_rules"])
    assert handoff["highest_priority_patch_id"] == "R8P_SOURCE_MISSING_FIELD_ROWS_FILE"
    assert handoff["can_write_to_actuator"] is False
    assert handoff["can_write_to_release_gate"] is False
    assert "not field evidence" in handoff["field_evidence_boundary"]
    assert "R8p acceptance" in handoff["schema_boundary"]


def test_pressure_resolution_submission_readiness_review_prioritizes_missing_source_package(tmp_path) -> None:
    rows, source = _read_field_rows_package(tmp_path / "missing_rows.json")
    report = PressureResolutionReplayScenarioPackAgent(
        r7_pipeline_metrics=_r7_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        collaborative_control_metrics=_collaborative_control_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        field_replay_rows_by_table=rows,
    ).run([])
    schema = _field_rows_package_schema()
    validation = _field_rows_schema_validation(source, rows, schema)
    bundle_preflight = _field_rows_batch_bundle_preflight(report, source, rows, schema, validation)
    temporal_preflight = _field_rows_temporal_window_preflight(report, source, rows, validation, bundle_preflight)
    semantic_preflight = _field_rows_scenario_semantic_preflight(
        report,
        source,
        rows,
        validation,
        bundle_preflight,
        temporal_preflight,
    )
    downstream_preflight = _field_rows_downstream_routing_preflight(
        report,
        source,
        validation,
        bundle_preflight,
        temporal_preflight,
        semantic_preflight,
    )
    downstream_route_handoff = _field_rows_downstream_route_handoff(downstream_preflight)
    downstream_target_gate_preflight = _field_rows_downstream_target_gate_preflight(
        downstream_route_handoff
    )
    patch_plan = _field_rows_patch_plan(
        report,
        source,
        validation,
        bundle_preflight,
        temporal_preflight,
        semantic_preflight,
    )
    checklist = _field_rows_collection_checklist(
        report,
        source,
        patch_plan,
        schema,
        validation,
        bundle_preflight,
        temporal_preflight,
        semantic_preflight,
    )
    handoff = _field_rows_operator_handoff(
        report,
        source,
        patch_plan,
        schema,
        validation,
        checklist,
        bundle_preflight,
        temporal_preflight,
        semantic_preflight,
        downstream_preflight,
    )
    r7_alignment = _field_rows_r7_alignment(schema)
    r7_staging = _field_rows_r7_staging_preflight(None, r7_alignment, schema)
    r7_completion = _field_rows_r7_completion_plan(r7_staging, r7_alignment)
    route_contracts = _field_rows_r7_completion_route_contracts(r7_completion)
    route_work_packages = _field_rows_r7_completion_route_work_packages(route_contracts)
    route_preflight = _field_rows_r7_completion_route_work_package_submission_preflight(
        route_work_packages,
        None,
    )
    route_patch_plan = _field_rows_r7_completion_route_work_package_patch_plan(route_preflight)
    assembly_gate = _field_rows_r7_completion_route_work_package_assembly_gate(
        route_preflight,
        route_patch_plan,
    )
    review = _field_rows_submission_readiness_review(
        report,
        source,
        validation,
        bundle_preflight,
        temporal_preflight,
        semantic_preflight,
        downstream_preflight,
        patch_plan,
        checklist,
        handoff,
        r7_completion,
        route_patch_plan,
        assembly_gate,
    )

    assert review["submission_readiness_review_status"] == (
        "submission_readiness_review_blocked_at_source_package"
    )
    assert review["next_operator_action"] == "R8p_fix_field_rows_source_preflight"
    assert review["direct_r8p_highest_priority_patch_id"] == "R8P_SOURCE_MISSING_FIELD_ROWS_FILE"
    assert review["r7_to_r8p_highest_priority_patch_id"] == "R8U27_SET_R7_TO_R8P_WORK_PACKAGE_DIR"
    assert review["can_route_to_r8v"] is False
    assert review["can_write_to_actuator"] is False
    assert review["can_write_to_release_gate"] is False
    assert review["field_claim_upgrade_allowed"] is False
    assert downstream_route_handoff["downstream_route_handoff_status"] == (
        "downstream_route_handoff_blocked_by_upstream_r8p_preflight"
    )
    assert downstream_route_handoff["ready_handoff_target_count"] == 0
    assert downstream_route_handoff["blocked_handoff_target_count"] == 4
    assert downstream_route_handoff["can_route_to_r8v"] is False
    assert downstream_route_handoff["can_write_to_actuator"] is False
    assert downstream_route_handoff["can_write_to_release_gate"] is False
    assert downstream_target_gate_preflight["downstream_target_gate_preflight_status"] == (
        "downstream_target_gate_preflight_blocked_by_downstream_route_handoff"
    )
    assert downstream_target_gate_preflight["ready_target_gate_count"] == 0
    assert downstream_target_gate_preflight["blocked_target_gate_count"] == 4
    assert downstream_target_gate_preflight["can_execute_all_target_gates"] is False
    assert downstream_target_gate_preflight["can_write_to_actuator"] is False
    assert downstream_target_gate_preflight["can_write_to_release_gate"] is False
    assert {gate["gate_id"] for gate in review["gate_sequence"]} == {
        "source_package",
        "schema_provenance_template",
        "same_batch_bundle",
        "temporal_window",
        "scenario_semantics",
        "downstream_routing",
        "r7_to_r8p_work_package_assembly",
    }
    assert "not field evidence" in " ".join(review["evidence_boundaries"])

    route_guide = _field_rows_source_package_submission_route_guide(
        report,
        source,
        schema,
        patch_plan,
        handoff,
        review,
        r7_completion,
        route_contracts,
        route_work_packages,
        route_patch_plan,
    )

    assert route_guide["source_package_submission_route_guide_status"] == (
        "source_package_submission_route_guide_ready_for_source_package_submission"
    )
    assert route_guide["recommended_route_id"] == "direct_r8p_json_or_csv_source_package"
    assert route_guide["next_operator_action"] == "R8p_submit_direct_json_or_csv_source_package"
    assert route_guide["route_option_count"] == 3
    assert {option["route_id"] for option in route_guide["route_options"]} == {
        "direct_r8p_json_table_mapping",
        "direct_r8p_csv_directory",
        "r7_to_r8p_route_work_package_submission",
    }
    direct_json = next(
        option for option in route_guide["route_options"] if option["route_id"] == "direct_r8p_json_table_mapping"
    )
    assert "agent52_replay_table" in direct_json["required_tables"]
    assert direct_json["highest_priority_patch_id"] == "R8P_SOURCE_MISSING_FIELD_ROWS_FILE"
    r7_route = next(
        option
        for option in route_guide["route_options"]
        if option["route_id"] == "r7_to_r8p_route_work_package_submission"
    )
    assert r7_route["highest_priority_patch_id"] == "R8U27_SET_R7_TO_R8P_WORK_PACKAGE_DIR"
    assert route_guide["can_route_to_r8v"] is False
    assert route_guide["can_write_to_actuator"] is False
    assert route_guide["can_write_to_release_gate"] is False
    assert route_guide["field_claim_upgrade_allowed"] is False
    assert "not field evidence" in " ".join(route_guide["evidence_boundaries"])

    route_preflight = _field_rows_source_package_route_preflight(
        source,
        route_guide,
        route_preflight,
        assembly_gate,
    )

    assert route_preflight["source_package_route_preflight_status"] == (
        "source_package_route_preflight_waiting_for_source_package_submission"
    )
    assert route_preflight["recommended_route_id"] == "direct_r8p_json_or_csv_source_package"
    assert route_preflight["recommended_route_preflight_status"] == (
        "recommended_route_preflight_waiting_for_direct_source_package"
    )
    assert route_preflight["ready_route_count"] == 0
    assert route_preflight["waiting_route_count"] == 3
    assert route_preflight["blocked_route_count"] == 0
    assert route_preflight["can_route_to_r8v"] is False
    assert route_preflight["can_write_to_actuator"] is False
    assert route_preflight["can_write_to_release_gate"] is False
    assert route_preflight["field_claim_upgrade_allowed"] is False
    assert {result["route_id"] for result in route_preflight["route_preflight_results"]} == {
        "direct_r8p_json_table_mapping",
        "direct_r8p_csv_directory",
        "r7_to_r8p_route_work_package_submission",
    }


def test_pressure_resolution_field_rows_package_schema_covers_required_tables_and_boundaries() -> None:
    schema = _field_rows_package_schema()
    expected_tables = sorted({*REQUIRED_TABLE_FIELDS, "agent52_replay_table"})

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["type"] == "object"
    assert schema["required"] == expected_tables
    assert schema["additionalProperties"] is False
    assert schema["x_required_tables"] == expected_tables
    assert "not make rows field evidence" in schema["description"]
    assert "R8p field_row_acceptance" in schema["x_downstream_acceptance"]

    properties = schema["properties"]
    assert set(properties) == set(expected_tables)
    for table in expected_tables:
        table_schema = properties[table]
        assert table_schema["type"] == "array"
        assert table_schema["minItems"] == 1
        assert table_schema["items"]["required"] == _required_fields_for_table(table)
        assert "data_origin" in table_schema["items"]["required"]
        assert table_schema["items"]["additionalProperties"] is True
        assert "batch_id" in table_schema["items"]["properties"]
    agent52_row = properties["agent52_replay_table"]["items"]
    assert "data_origin" in agent52_row["required"]
    assert agent52_row["properties"]["pressure_source_conflict_requires_operator_review"]["type"] == "boolean"
    assert agent52_row["properties"]["pressure_source_conflict_count"]["type"] == ["number", "integer"]


def test_pressure_resolution_schema_validation_blocks_missing_source_package(tmp_path) -> None:
    rows, source = _read_field_rows_package(tmp_path / "missing_rows.json")
    validation = _field_rows_schema_validation(source, rows, _field_rows_package_schema())

    assert validation["field_rows_schema_validation_status"] == "schema_validation_blocked_at_source_preflight"
    assert validation["source_status"] == "field_rows_file_missing"
    assert validation["required_table_count"] == len(REQUIRED_TABLE_FIELDS) + 1
    assert validation["loaded_table_count"] == 0
    assert validation["loaded_row_count"] == 0
    assert validation["missing_table_count"] == len(REQUIRED_TABLE_FIELDS) + 1
    assert validation["required_field_gap_count"] == 0
    assert validation["invalid_type_count"] == 0
    assert validation["template_marker_gap_count"] == 0
    assert validation["field_origin_gap_count"] == 0
    assert validation["can_write_to_actuator"] is False
    assert validation["can_write_to_release_gate"] is False


def test_pressure_resolution_schema_validation_finds_required_field_and_type_gaps(tmp_path) -> None:
    payload = _complete_field_rows_by_table()
    del payload["node_modality_sensor_timeseries"][0]["value"]
    payload["campaign_operation_log"][0]["operator_review_required"] = "true"
    path = tmp_path / "rows.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    rows, source = _read_field_rows_package(path)
    validation = _field_rows_schema_validation(source, rows, _field_rows_package_schema())
    report = PressureResolutionReplayScenarioPackAgent(
        r7_pipeline_metrics=_r7_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        collaborative_control_metrics=_collaborative_control_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        field_replay_rows_by_table=rows,
    ).run([])
    patch_plan = _field_rows_patch_plan(report, source, validation)
    handoff = _field_rows_operator_handoff(report, source, patch_plan, _field_rows_package_schema(), validation)

    assert validation["field_rows_schema_validation_status"] == "schema_validation_failed_row_contract"
    assert validation["required_field_gap_count"] >= 1
    assert validation["invalid_type_count"] >= 1
    assert validation["template_marker_gap_count"] == 0
    node_validation = next(
        item for item in validation["table_validations"] if item["table"] == "node_modality_sensor_timeseries"
    )
    campaign_validation = next(
        item for item in validation["table_validations"] if item["table"] == "campaign_operation_log"
    )
    assert node_validation["missing_required_field_count"] == 1
    assert campaign_validation["invalid_type_count"] == 1
    assert patch_plan["field_rows_patch_plan_status"] == "field_rows_patch_plan_blocked_at_schema_row_contract"
    assert patch_plan["next_operator_action"] == "R8p_fix_schema_required_fields_and_types"
    assert any(item["patch_type"] == "schema_row_contract" for item in patch_plan["patch_items"])
    assert handoff["field_rows_schema_validation_status"] == "schema_validation_failed_row_contract"
    assert handoff["schema_validation_summary"]["required_field_gap_count"] >= 1
    assert handoff["schema_validation_summary"]["invalid_type_count"] >= 1


def test_pressure_resolution_schema_validation_rejects_template_markers_before_acceptance(tmp_path) -> None:
    template_report = PressureResolutionReplayScenarioPackAgent(
        r7_pipeline_metrics=_r7_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        collaborative_control_metrics=_collaborative_control_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
    ).run([])
    path = tmp_path / "template_rows.json"
    path.write_text(
        json.dumps(template_report.metrics["template_rows_by_table"], ensure_ascii=False),
        encoding="utf-8",
    )

    rows, source = _read_field_rows_package(path)
    validation = _field_rows_schema_validation(source, rows, _field_rows_package_schema())
    report = PressureResolutionReplayScenarioPackAgent(
        r7_pipeline_metrics=_r7_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        collaborative_control_metrics=_collaborative_control_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        field_replay_rows_by_table=rows,
    ).run([])
    patch_plan = _field_rows_patch_plan(report, source, validation)
    checklist = _field_rows_collection_checklist(report, source, patch_plan, _field_rows_package_schema(), validation)
    handoff = _field_rows_operator_handoff(
        report,
        source,
        patch_plan,
        _field_rows_package_schema(),
        validation,
        checklist,
    )

    assert source["field_rows_source_status"] == "field_rows_file_loaded"
    assert validation["field_rows_schema_validation_status"] == "schema_validation_failed_template_marker_contract"
    assert validation["template_marker_gap_count"] > 0
    assert validation["invalid_type_count"] > 0
    assert validation["field_origin_gap_count"] > 0
    node_validation = next(
        item for item in validation["table_validations"] if item["table"] == "node_modality_sensor_timeseries"
    )
    assert node_validation["template_marker_gap_count"] > 0
    assert any(
        gap["field"] == "batch_id" and "TODO" in str(gap["observed_value"])
        for gap in node_validation["template_marker_gaps_by_row"]
    )
    assert patch_plan["field_rows_patch_plan_status"] == "field_rows_patch_plan_blocked_at_template_marker_contract"
    assert patch_plan["next_operator_action"] == "R8p_replace_template_markers_with_field_values"
    assert patch_plan["highest_priority_patch_id"].startswith("R8P_SCHEMA_TEMPLATE_MARKERS_")
    assert any(item["patch_type"] == "template_marker_contract" for item in patch_plan["patch_items"])
    assert checklist["field_rows_collection_checklist_status"] == (
        "field_rows_collection_checklist_ready_needs_template_marker_replacement"
    )
    assert handoff["field_rows_schema_validation_status"] == "schema_validation_failed_template_marker_contract"
    assert handoff["schema_validation_summary"]["template_marker_gap_count"] > 0
    assert handoff["schema_validation_summary"]["field_origin_gap_count"] > 0
    assert handoff["can_write_to_actuator"] is False
    assert handoff["can_write_to_release_gate"] is False


def test_pressure_resolution_schema_validation_finds_non_field_data_origin_before_acceptance(tmp_path) -> None:
    payload = _complete_field_rows_by_table()
    payload["pressure_headloss_event_log"][0]["data_origin"] = "synthetic_lab_demo"
    path = tmp_path / "rows.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    rows, source = _read_field_rows_package(path)
    validation = _field_rows_schema_validation(source, rows, _field_rows_package_schema())
    report = PressureResolutionReplayScenarioPackAgent(
        r7_pipeline_metrics=_r7_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        collaborative_control_metrics=_collaborative_control_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        field_replay_rows_by_table=rows,
    ).run([])
    patch_plan = _field_rows_patch_plan(report, source, validation)
    checklist = _field_rows_collection_checklist(report, source, patch_plan, _field_rows_package_schema(), validation)
    handoff = _field_rows_operator_handoff(
        report,
        source,
        patch_plan,
        _field_rows_package_schema(),
        validation,
        checklist,
    )

    assert validation["field_rows_schema_validation_status"] == "schema_validation_failed_provenance_contract"
    assert validation["required_field_gap_count"] == 0
    assert validation["invalid_type_count"] == 0
    assert validation["template_marker_gap_count"] == 0
    assert validation["field_origin_gap_count"] == 1
    pressure_validation = next(
        item for item in validation["table_validations"] if item["table"] == "pressure_headloss_event_log"
    )
    assert pressure_validation["field_origin_gap_count"] == 1
    assert pressure_validation["field_origin_gaps_by_row"][0]["observed_value"] == "synthetic_lab_demo"
    assert patch_plan["field_rows_patch_plan_status"] == "field_rows_patch_plan_blocked_at_field_origin_contract"
    assert patch_plan["next_operator_action"] == "R8p_fix_field_origin_provenance"
    assert patch_plan["highest_priority_patch_id"] == "R8P_SCHEMA_FIELD_ORIGIN_PRESSURE_HEADLOSS_EVENT_LOG"
    assert any(item["patch_type"] == "field_origin_contract" for item in patch_plan["patch_items"])
    assert checklist["field_rows_collection_checklist_status"] == (
        "field_rows_collection_checklist_ready_needs_field_origin_provenance"
    )
    assert handoff["field_rows_schema_validation_status"] == "schema_validation_failed_provenance_contract"
    assert handoff["schema_validation_summary"]["field_origin_gap_count"] == 1
    assert handoff["can_write_to_actuator"] is False
    assert handoff["can_write_to_release_gate"] is False


def test_pressure_resolution_batch_bundle_preflight_finds_same_batch_table_gaps(tmp_path) -> None:
    payload = _complete_field_rows_by_table()
    first_scenario_id = str(PRESSURE_RESOLUTION_SCENARIOS[0]["scenario_id"])
    original_batch = f"FIELD_{first_scenario_id}"
    payload["fast_proxy_event_log"][0]["batch_id"] = "FIELD_R8U14_UNLINKED_FAST_PROXY_BATCH"
    path = tmp_path / "rows.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    rows, source = _read_field_rows_package(path)
    schema = _field_rows_package_schema()
    validation = _field_rows_schema_validation(source, rows, schema)
    report = PressureResolutionReplayScenarioPackAgent(
        r7_pipeline_metrics=_r7_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        collaborative_control_metrics=_collaborative_control_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        field_replay_rows_by_table=rows,
    ).run([])
    bundle_preflight = _field_rows_batch_bundle_preflight(report, source, rows, schema, validation)
    patch_plan = _field_rows_patch_plan(report, source, validation, bundle_preflight)
    checklist = _field_rows_collection_checklist(report, source, patch_plan, schema, validation, bundle_preflight)
    handoff = _field_rows_operator_handoff(
        report,
        source,
        patch_plan,
        schema,
        validation,
        checklist,
        bundle_preflight,
    )

    first_scenario_bundle = next(
        item for item in bundle_preflight["scenario_bundle_status"] if item["scenario_id"] == first_scenario_id
    )

    assert validation["field_rows_schema_validation_status"] == "schema_validation_passed_structure_contract"
    assert validation["template_marker_gap_count"] == 0
    assert validation["field_origin_gap_count"] == 0
    assert bundle_preflight["field_rows_batch_bundle_preflight_status"] == (
        "batch_bundle_preflight_failed_partial_batch_bundles"
    )
    assert bundle_preflight["partial_bundle_count"] >= 1
    assert bundle_preflight["missing_bundle_table_count"] >= 1
    assert first_scenario_bundle["bundle_preflight_status"] == "scenario_has_partial_batch_bundle"
    assert first_scenario_bundle["missing_tables_by_candidate_batch"][original_batch] == ["fast_proxy_event_log"]
    assert patch_plan["field_rows_patch_plan_status"] == "field_rows_patch_plan_blocked_at_batch_bundle_contract"
    assert patch_plan["next_operator_action"] == "R8p_complete_same_batch_six_table_bundles"
    assert patch_plan["highest_priority_patch_id"] == (
        "R8P_BATCH_BUNDLE_R8O_S1_UNRESOLVED_PRESSURE_CONFLICT_REVIEW_BLOCK"
    )
    assert any(item["patch_type"] == "batch_bundle_contract" for item in patch_plan["patch_items"])
    assert checklist["field_rows_collection_checklist_status"] == (
        "field_rows_collection_checklist_ready_needs_same_batch_bundle_completion"
    )
    assert handoff["field_rows_operator_handoff_status"] == (
        "field_rows_operator_handoff_ready_needs_same_batch_bundle_completion"
    )
    assert handoff["batch_bundle_preflight_summary"]["partial_bundle_count"] >= 1
    assert handoff["can_write_to_actuator"] is False
    assert handoff["can_write_to_release_gate"] is False


def test_pressure_resolution_temporal_window_preflight_finds_hold_time_budget_gaps(tmp_path) -> None:
    payload = _complete_field_rows_by_table()
    first_scenario_id = str(PRESSURE_RESOLUTION_SCENARIOS[0]["scenario_id"])
    original_batch = f"FIELD_{first_scenario_id}"
    payload["campaign_operation_log"][0]["hold_time_min"] = 12
    path = tmp_path / "rows.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    rows, source = _read_field_rows_package(path)
    schema = _field_rows_package_schema()
    validation = _field_rows_schema_validation(source, rows, schema)
    report = PressureResolutionReplayScenarioPackAgent(
        r7_pipeline_metrics=_r7_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        collaborative_control_metrics=_collaborative_control_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        field_replay_rows_by_table=rows,
    ).run([])
    bundle_preflight = _field_rows_batch_bundle_preflight(report, source, rows, schema, validation)
    temporal_preflight = _field_rows_temporal_window_preflight(
        report,
        source,
        rows,
        validation,
        bundle_preflight,
    )
    patch_plan = _field_rows_patch_plan(report, source, validation, bundle_preflight, temporal_preflight)
    checklist = _field_rows_collection_checklist(
        report,
        source,
        patch_plan,
        schema,
        validation,
        bundle_preflight,
        temporal_preflight,
    )
    handoff = _field_rows_operator_handoff(
        report,
        source,
        patch_plan,
        schema,
        validation,
        checklist,
        bundle_preflight,
        temporal_preflight,
    )
    first_scenario_acceptance = next(
        item for item in report.metrics["field_row_acceptance"]["scenario_acceptance"] if item["scenario_id"] == first_scenario_id
    )
    first_scenario_temporal = next(
        item for item in temporal_preflight["scenario_temporal_status"] if item["scenario_id"] == first_scenario_id
    )

    assert validation["field_rows_schema_validation_status"] == "schema_validation_passed_structure_contract"
    assert bundle_preflight["field_rows_batch_bundle_preflight_status"] == (
        "batch_bundle_preflight_passed_ready_for_scenario_acceptance"
    )
    assert temporal_preflight["field_rows_temporal_window_preflight_status"] == (
        "temporal_window_preflight_failed_hold_time_budget_contract"
    )
    assert temporal_preflight["hold_time_violation_count"] == 1
    assert temporal_preflight["temporal_valid_batch_count"] == len(PRESSURE_RESOLUTION_SCENARIOS) - 1
    assert first_scenario_temporal["temporal_preflight_status"] == "scenario_has_temporal_window_violations"
    assert first_scenario_temporal["latency_margin_min_by_batch"][original_batch] < 0
    assert first_scenario_temporal["violations_by_batch"][original_batch] == [
        "hold_time_budget_must_cover_slowest_evidence_label"
    ]
    assert "hold_time_budget_must_cover_slowest_evidence_label" in first_scenario_acceptance["blocking_reasons"]
    assert patch_plan["field_rows_patch_plan_status"] == "field_rows_patch_plan_blocked_at_temporal_window_contract"
    assert patch_plan["next_operator_action"] == "R8p_fix_same_batch_timestamps_and_hold_time_budget"
    assert patch_plan["highest_priority_patch_id"] == (
        "R8P_TEMPORAL_WINDOW_R8O_S1_UNRESOLVED_PRESSURE_CONFLICT_REVIEW_BLOCK"
    )
    assert any(item["patch_type"] == "temporal_window_contract" for item in patch_plan["patch_items"])
    assert checklist["field_rows_collection_checklist_status"] == (
        "field_rows_collection_checklist_ready_needs_temporal_window_fixes"
    )
    assert handoff["field_rows_operator_handoff_status"] == (
        "field_rows_operator_handoff_ready_needs_temporal_window_fixes"
    )
    assert handoff["temporal_window_preflight_summary"]["hold_time_violation_count"] == 1
    assert handoff["can_write_to_actuator"] is False
    assert handoff["can_write_to_release_gate"] is False


def test_pressure_resolution_scenario_semantic_preflight_blocks_unresolved_conflict_without_control_block() -> None:
    rows = _complete_field_rows_by_table()
    first_scenario_id = str(PRESSURE_RESOLUTION_SCENARIOS[0]["scenario_id"])
    original_batch = f"FIELD_{first_scenario_id}"
    rows["agent52_replay_table"][0]["pressure_source_conflict_control_block"] = False
    source = _field_source_for_rows(rows)
    schema = _field_rows_package_schema()
    validation = _field_rows_schema_validation(source, rows, schema)
    report = PressureResolutionReplayScenarioPackAgent(
        r7_pipeline_metrics=_r7_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        collaborative_control_metrics=_collaborative_control_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        field_replay_rows_by_table=rows,
    ).run([])
    bundle_preflight = _field_rows_batch_bundle_preflight(report, source, rows, schema, validation)
    temporal_preflight = _field_rows_temporal_window_preflight(
        report,
        source,
        rows,
        validation,
        bundle_preflight,
    )
    semantic_preflight = _field_rows_scenario_semantic_preflight(
        report,
        source,
        rows,
        validation,
        bundle_preflight,
        temporal_preflight,
    )
    downstream_routing_preflight = _field_rows_downstream_routing_preflight(
        report,
        source,
        validation,
        bundle_preflight,
        temporal_preflight,
        semantic_preflight,
    )
    downstream_route_handoff = _field_rows_downstream_route_handoff(downstream_routing_preflight)
    downstream_target_gate_preflight = _field_rows_downstream_target_gate_preflight(
        downstream_route_handoff
    )
    patch_plan = _field_rows_patch_plan(
        report,
        source,
        validation,
        bundle_preflight,
        temporal_preflight,
        semantic_preflight,
    )
    checklist = _field_rows_collection_checklist(
        report,
        source,
        patch_plan,
        schema,
        validation,
        bundle_preflight,
        temporal_preflight,
        semantic_preflight,
    )
    handoff = _field_rows_operator_handoff(
        report,
        source,
        patch_plan,
        schema,
        validation,
        checklist,
        bundle_preflight,
        temporal_preflight,
        semantic_preflight,
    )
    first_scenario_acceptance = next(
        item
        for item in report.metrics["field_row_acceptance"]["scenario_acceptance"]
        if item["scenario_id"] == first_scenario_id
    )
    first_scenario_semantic = next(
        item for item in semantic_preflight["scenario_semantic_status"] if item["scenario_id"] == first_scenario_id
    )

    assert validation["field_rows_schema_validation_status"] == "schema_validation_passed_structure_contract"
    assert bundle_preflight["field_rows_batch_bundle_preflight_status"] == (
        "batch_bundle_preflight_passed_ready_for_scenario_acceptance"
    )
    assert temporal_preflight["field_rows_temporal_window_preflight_status"] == (
        "temporal_window_preflight_passed_ready_for_scenario_acceptance"
    )
    assert semantic_preflight["field_rows_scenario_semantic_preflight_status"] == (
        "scenario_semantic_preflight_failed_unresolved_conflict_contract"
    )
    assert semantic_preflight["semantic_valid_batch_count"] == len(PRESSURE_RESOLUTION_SCENARIOS) - 1
    assert semantic_preflight["semantic_violation_count"] == 1
    assert downstream_routing_preflight["field_rows_downstream_routing_preflight_status"] == (
        "downstream_routing_preflight_blocked_at_scenario_semantic_preflight"
    )
    assert downstream_routing_preflight["routing_ready_target_count"] == 0
    assert downstream_routing_preflight["can_route_to_r8v"] is False
    assert downstream_route_handoff["downstream_route_handoff_status"] == (
        "downstream_route_handoff_blocked_by_upstream_r8p_preflight"
    )
    assert downstream_route_handoff["ready_handoff_target_count"] == 0
    assert downstream_route_handoff["blocked_handoff_target_count"] == 4
    assert downstream_route_handoff["can_write_to_actuator"] is False
    assert downstream_route_handoff["can_write_to_release_gate"] is False
    assert first_scenario_semantic["scenario_semantic_preflight_status"] == "scenario_has_semantic_contract_violations"
    assert first_scenario_semantic["violations_by_batch"][original_batch] == [
        "unresolved_replay_keeps_control_block"
    ]
    assert "unresolved_conflict_requires_operator_review_and_replay_block" in first_scenario_acceptance[
        "blocking_reasons"
    ]
    assert patch_plan["field_rows_patch_plan_status"] == "field_rows_patch_plan_blocked_at_scenario_semantic_contract"
    assert patch_plan["next_operator_action"] == "R8p_fix_pressure_resolution_scenario_semantics"
    assert patch_plan["highest_priority_patch_id"] == (
        "R8P_SCENARIO_SEMANTIC_R8O_S1_UNRESOLVED_PRESSURE_CONFLICT_REVIEW_BLOCK"
    )
    assert any(item["patch_type"] == "scenario_semantic_contract" for item in patch_plan["patch_items"])
    assert checklist["field_rows_collection_checklist_status"] == (
        "field_rows_collection_checklist_ready_needs_scenario_semantic_fixes"
    )
    assert handoff["field_rows_operator_handoff_status"] == (
        "field_rows_operator_handoff_ready_needs_scenario_semantic_fixes"
    )
    assert handoff["scenario_semantic_preflight_summary"]["semantic_violation_count"] == 1
    assert handoff["can_write_to_actuator"] is False
    assert handoff["can_write_to_release_gate"] is False


def test_pressure_resolution_collection_checklist_maps_tables_scenarios_and_boundaries(tmp_path) -> None:
    rows, source = _read_field_rows_package(tmp_path / "missing_rows.json")
    report = PressureResolutionReplayScenarioPackAgent(
        r7_pipeline_metrics=_r7_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        collaborative_control_metrics=_collaborative_control_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        field_replay_rows_by_table=rows,
    ).run([])
    schema = _field_rows_package_schema()
    validation = _field_rows_schema_validation(source, rows, schema)
    patch_plan = _field_rows_patch_plan(report, source, validation)
    checklist = _field_rows_collection_checklist(report, source, patch_plan, schema, validation)
    handoff = _field_rows_operator_handoff(report, source, patch_plan, schema, validation, checklist)

    assert checklist["field_rows_collection_checklist_status"] == (
        "field_rows_collection_checklist_ready_needs_source_package"
    )
    assert checklist["required_scenario_count"] == len(PRESSURE_RESOLUTION_SCENARIOS)
    assert checklist["required_table_count"] == len(REQUIRED_TABLE_FIELDS) + 1
    assert checklist["minimum_real_batch_count"] == len(PRESSURE_RESOLUTION_SCENARIOS)
    assert len(checklist["scenario_collection_checklist"]) == len(PRESSURE_RESOLUTION_SCENARIOS)
    assert len(checklist["table_field_checklist"]) == len(REQUIRED_TABLE_FIELDS) + 1
    assert {step["step"] for step in checklist["operator_acceptance_sequence"]} == {
        "source_package",
        "schema_contract",
        "scenario_bundle",
        "downstream_routing",
    }
    node_table = next(
        item for item in checklist["table_field_checklist"] if item["table"] == "node_modality_sensor_timeseries"
    )
    value_field = next(item for item in node_table["required_fields"] if item["field"] == "value")
    assert value_field["evidence_role"] == "measured_process_signal"
    assert value_field["validation_rule"] == "must_be_numeric_not_boolean"
    assert "same-batch six-table field-row bundle" in checklist["technical_feature_mapping"]["technical_means"]
    assert checklist["can_write_to_actuator"] is False
    assert checklist["can_write_to_release_gate"] is False
    assert handoff["field_rows_collection_checklist_status"] == checklist["field_rows_collection_checklist_status"]
    assert handoff["collection_checklist_path"].endswith("pressure_resolution_replay_rows_collection_checklist.json")


def test_pressure_resolution_collection_checklist_clears_only_after_real_scenarios_are_accepted() -> None:
    report = PressureResolutionReplayScenarioPackAgent(
        r7_pipeline_metrics=_r7_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        collaborative_control_metrics=_collaborative_control_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        field_replay_rows_by_table=_complete_field_rows_by_table(),
    ).run([])
    source = {
        "field_rows_source_status": "field_rows_file_loaded",
        "field_rows_source_path": "memory://complete_rows",
        "expected_tables": sorted({*REQUIRED_TABLE_FIELDS, "agent52_replay_table"}),
        "table_count": len(REQUIRED_TABLE_FIELDS) + 1,
        "row_count": len(PRESSURE_RESOLUTION_SCENARIOS) * (len(REQUIRED_TABLE_FIELDS) + 1),
        "missing_tables": [],
        "empty_tables": [],
        "invalid_table_shapes": [],
        "unknown_tables": [],
        "preflight_blockers": [],
    }
    schema = _field_rows_package_schema()
    validation = _field_rows_schema_validation(source, _complete_field_rows_by_table(), schema)
    patch_plan = _field_rows_patch_plan(report, source, validation)
    checklist = _field_rows_collection_checklist(report, source, patch_plan, schema, validation)

    assert validation["field_rows_schema_validation_status"] == "schema_validation_passed_structure_contract"
    assert validation["template_marker_gap_count"] == 0
    assert validation["field_origin_gap_count"] == 0
    assert patch_plan["field_rows_patch_plan_status"] == "field_rows_patch_plan_clear_ready_for_r8v_routing"
    assert checklist["field_rows_collection_checklist_status"] == (
        "field_rows_collection_checklist_complete_ready_for_r8v_routing"
    )
    assert checklist["accepted_scenario_count"] == len(PRESSURE_RESOLUTION_SCENARIOS)
    assert checklist["minimum_real_batch_count"] == 0
    assert checklist["can_write_to_actuator"] is False
    assert checklist["can_write_to_release_gate"] is False


def test_pressure_resolution_submission_readiness_review_routes_only_after_all_gates_pass() -> None:
    rows = _complete_field_rows_by_table()
    source = _field_source_for_rows(rows)
    schema = _field_rows_package_schema()
    validation = _field_rows_schema_validation(source, rows, schema)
    report = PressureResolutionReplayScenarioPackAgent(
        r7_pipeline_metrics=_r7_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        collaborative_control_metrics=_collaborative_control_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        field_replay_rows_by_table=rows,
    ).run([])
    bundle_preflight = _field_rows_batch_bundle_preflight(report, source, rows, schema, validation)
    temporal_preflight = _field_rows_temporal_window_preflight(report, source, rows, validation, bundle_preflight)
    semantic_preflight = _field_rows_scenario_semantic_preflight(
        report,
        source,
        rows,
        validation,
        bundle_preflight,
        temporal_preflight,
    )
    downstream_preflight = _field_rows_downstream_routing_preflight(
        report,
        source,
        validation,
        bundle_preflight,
        temporal_preflight,
        semantic_preflight,
    )
    patch_plan = _field_rows_patch_plan(
        report,
        source,
        validation,
        bundle_preflight,
        temporal_preflight,
        semantic_preflight,
    )
    checklist = _field_rows_collection_checklist(
        report,
        source,
        patch_plan,
        schema,
        validation,
        bundle_preflight,
        temporal_preflight,
        semantic_preflight,
    )
    handoff = _field_rows_operator_handoff(
        report,
        source,
        patch_plan,
        schema,
        validation,
        checklist,
        bundle_preflight,
        temporal_preflight,
        semantic_preflight,
        downstream_preflight,
    )
    r7_alignment = _field_rows_r7_alignment(schema)
    r7_staging = _field_rows_r7_staging_preflight(None, r7_alignment, schema)
    r7_completion = _field_rows_r7_completion_plan(r7_staging, r7_alignment)
    route_contracts = _field_rows_r7_completion_route_contracts(r7_completion)
    route_work_packages = _field_rows_r7_completion_route_work_packages(route_contracts)
    route_preflight = _field_rows_r7_completion_route_work_package_submission_preflight(
        route_work_packages,
        None,
    )
    route_patch_plan = _field_rows_r7_completion_route_work_package_patch_plan(route_preflight)
    assembly_gate = _field_rows_r7_completion_route_work_package_assembly_gate(
        route_preflight,
        route_patch_plan,
    )
    review = _field_rows_submission_readiness_review(
        report,
        source,
        validation,
        bundle_preflight,
        temporal_preflight,
        semantic_preflight,
        downstream_preflight,
        patch_plan,
        checklist,
        handoff,
        r7_completion,
        route_patch_plan,
        assembly_gate,
    )

    assert review["submission_readiness_review_status"] == (
        "submission_readiness_review_ready_for_r8v_field_replay_and_holdout_gates"
    )
    assert review["next_operator_action"] == "R8v_route_pressure_resolution_rows_to_field_replay_and_holdout_gates"
    assert review["direct_r8p_highest_priority_patch_id"] is None
    assert review["can_route_to_r8v"] is True
    assert review["can_write_to_actuator"] is False
    assert review["can_write_to_release_gate"] is False
    assert review["field_claim_upgrade_allowed"] is False
    assert review["accepted_scenario_count"] == len(PRESSURE_RESOLUTION_SCENARIOS)
    assert review["accepted_batch_count"] == len(PRESSURE_RESOLUTION_SCENARIOS)
    assert next(gate for gate in review["gate_sequence"] if gate["gate_id"] == "downstream_routing")[
        "gate_passed"
    ] is True
    assert "cannot write actuator" in " ".join(review["evidence_boundaries"])

    route_guide = _field_rows_source_package_submission_route_guide(
        report,
        source,
        schema,
        patch_plan,
        handoff,
        review,
        r7_completion,
        route_contracts,
        route_work_packages,
        route_patch_plan,
    )

    assert route_guide["source_package_submission_route_guide_status"] == (
        "source_package_submission_route_guide_ready_for_r8v_no_source_repair_needed"
    )
    assert route_guide["recommended_route_id"] == "route_to_r8v_field_replay_and_holdout_gates"
    assert route_guide["next_operator_action"] == "R8v_route_pressure_resolution_rows_to_field_replay_and_holdout_gates"
    assert route_guide["route_option_count"] == 3
    assert route_guide["can_route_to_r8v"] is True
    assert route_guide["can_write_to_actuator"] is False
    assert route_guide["can_write_to_release_gate"] is False
    assert route_guide["field_claim_upgrade_allowed"] is False

    route_preflight = _field_rows_source_package_route_preflight(
        source,
        route_guide,
        route_preflight,
        assembly_gate,
    )

    assert route_preflight["source_package_route_preflight_status"] == (
        "source_package_route_preflight_ready_for_r8v_routing"
    )
    assert route_preflight["recommended_route_id"] == "route_to_r8v_field_replay_and_holdout_gates"
    assert route_preflight["recommended_route_preflight_status"] == "route_preflight_ready_for_r8v_routing"
    assert route_preflight["ready_route_count"] == 1
    assert route_preflight["can_route_to_r8v"] is True
    assert route_preflight["can_write_to_actuator"] is False
    assert route_preflight["can_write_to_release_gate"] is False
    assert route_preflight["field_claim_upgrade_allowed"] is False


def test_pressure_resolution_field_rows_package_preflight_rejects_invalid_root_shape(tmp_path) -> None:
    path = tmp_path / "rows.json"
    path.write_text(json.dumps([{"batch_id": "B1"}], ensure_ascii=False), encoding="utf-8")

    rows, source = _read_field_rows_package(path)

    assert rows == {}
    assert source["field_rows_source_status"] == "field_rows_file_invalid_shape"
    assert source["missing_tables"] == sorted({*REQUIRED_TABLE_FIELDS, "agent52_replay_table"})
    assert "root:not_object" in source["invalid_table_shapes"]
    assert "root_json_must_be_object_mapping_table_to_rows" in source["preflight_blockers"]


def test_pressure_resolution_field_rows_package_preflight_reports_missing_expected_tables(tmp_path) -> None:
    path = tmp_path / "rows.json"
    path.write_text(
        json.dumps(
            {
                "node_modality_sensor_timeseries": [
                    {
                        "batch_id": "B_partial",
                        "scenario_id": "R8O_S1_unresolved_pressure_conflict_review_block",
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    rows, source = _read_field_rows_package(path)
    report = PressureResolutionReplayScenarioPackAgent(
        r7_pipeline_metrics=_r7_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        collaborative_control_metrics=_collaborative_control_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        field_replay_rows_by_table=rows,
    ).run([])
    patch_plan = _field_rows_patch_plan(report, source)

    assert source["field_rows_source_status"] == "field_rows_file_loaded_with_schema_gaps"
    assert source["row_count"] == 1
    assert "agent52_replay_table" in source["missing_tables"]
    assert "pressure_headloss_event_log" in source["missing_tables"]
    assert "agent52_replay_table:missing_table" in source["preflight_blockers"]
    assert rows["node_modality_sensor_timeseries"][0]["batch_id"] == "B_partial"
    assert patch_plan["field_rows_patch_plan_status"] == "field_rows_patch_plan_blocked_at_table_preflight"
    assert any(
        item["patch_id"] == "R8P_MISSING_TABLE_AGENT52_REPLAY_TABLE"
        for item in patch_plan["patch_items"]
    )
    assert any(item["patch_type"] == "scenario_acceptance" for item in patch_plan["patch_items"])


def test_pressure_resolution_field_rows_package_preflight_loads_object_rows(tmp_path) -> None:
    path = tmp_path / "rows.json"
    payload = _complete_field_rows_by_table()
    payload["unexpected_table"] = [{"batch_id": "B_extra"}]
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    rows, source = _read_field_rows_package(path)

    assert source["field_rows_source_status"] == "field_rows_file_loaded_with_shape_warnings"
    assert source["row_count"] == sum(len(value) for key, value in payload.items() if key != "unexpected_table")
    assert source["missing_tables"] == []
    assert source["unknown_tables"] == ["unexpected_table"]
    assert set(rows) == {*REQUIRED_TABLE_FIELDS, "agent52_replay_table"}
    assert all(isinstance(row, dict) for table_rows in rows.values() for row in table_rows)


def test_pressure_resolution_field_rows_package_preflight_loads_csv_directory_and_passes_gates(tmp_path) -> None:
    package_dir = tmp_path / "field_rows_package"
    rows_by_table = _complete_field_rows_by_table()
    _write_field_rows_csv_directory(package_dir, rows_by_table)

    rows, source = _read_field_rows_package(package_dir)
    report = PressureResolutionReplayScenarioPackAgent(
        r7_pipeline_metrics=_r7_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        collaborative_control_metrics=_collaborative_control_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        field_replay_rows_by_table=rows,
    ).run([])
    schema = _field_rows_package_schema()
    validation = _field_rows_schema_validation(source, rows, schema)
    bundle_preflight = _field_rows_batch_bundle_preflight(report, source, rows, schema, validation)
    temporal_preflight = _field_rows_temporal_window_preflight(report, source, rows, validation, bundle_preflight)
    semantic_preflight = _field_rows_scenario_semantic_preflight(
        report,
        source,
        rows,
        validation,
        bundle_preflight,
        temporal_preflight,
    )
    downstream_routing_preflight = _field_rows_downstream_routing_preflight(
        report,
        source,
        validation,
        bundle_preflight,
        temporal_preflight,
        semantic_preflight,
    )
    downstream_route_handoff = _field_rows_downstream_route_handoff(downstream_routing_preflight)
    downstream_target_gate_preflight = _field_rows_downstream_target_gate_preflight(
        downstream_route_handoff
    )

    assert source["field_rows_source_status"] == "field_rows_directory_loaded"
    assert source["field_rows_source_format"] == "csv_directory_with_optional_metadata_json"
    assert source["field_rows_directory_metadata"]["metadata_status"] == "metadata_loaded_optional_for_r8p_rows"
    assert source["row_count"] == sum(len(table_rows) for table_rows in rows_by_table.values())
    assert source["missing_tables"] == []
    assert isinstance(rows["node_modality_sensor_timeseries"][0]["value"], float)
    assert isinstance(rows["fast_proxy_event_log"][0]["protective_triggered"], bool)
    assert validation["field_rows_schema_validation_status"] == "schema_validation_passed_structure_contract"
    assert bundle_preflight["field_rows_batch_bundle_preflight_status"] == (
        "batch_bundle_preflight_passed_ready_for_scenario_acceptance"
    )
    assert temporal_preflight["field_rows_temporal_window_preflight_status"] == (
        "temporal_window_preflight_passed_ready_for_scenario_acceptance"
    )
    assert semantic_preflight["field_rows_scenario_semantic_preflight_status"] == (
        "scenario_semantic_preflight_passed_ready_for_scenario_acceptance"
    )
    assert downstream_routing_preflight["field_rows_downstream_routing_preflight_status"] == (
        "downstream_routing_preflight_passed_ready_for_r8v_field_replay_and_holdout_gates"
    )
    assert downstream_routing_preflight["can_route_to_r8v"] is True
    assert downstream_route_handoff["downstream_route_handoff_status"] == (
        "downstream_route_handoff_ready_for_r8v_target_gates"
    )
    assert downstream_route_handoff["handoff_target_count"] == 4
    assert downstream_route_handoff["ready_handoff_target_count"] == 4
    assert downstream_route_handoff["blocked_handoff_target_count"] == 0
    assert downstream_route_handoff["can_write_to_actuator"] is False
    assert downstream_route_handoff["can_write_to_release_gate"] is False
    assert downstream_target_gate_preflight["downstream_target_gate_preflight_status"] == (
        "downstream_target_gate_preflight_ready_for_r8v_execution"
    )
    assert downstream_target_gate_preflight["ready_target_gate_count"] == 4
    assert downstream_target_gate_preflight["blocked_target_gate_count"] == 0
    assert downstream_target_gate_preflight["can_execute_all_target_gates"] is True
    assert report.metrics["field_row_acceptance"]["field_row_acceptance_status"] == (
        "field_replay_rows_accepted_for_all_scenarios"
    )
    assert report.metrics["readiness"]["can_write_to_actuator"] is False
    assert report.metrics["readiness"]["can_write_to_release_gate"] is False


def test_pressure_resolution_field_rows_package_preflight_reports_missing_csv_table(tmp_path) -> None:
    package_dir = tmp_path / "field_rows_package"
    rows_by_table = _complete_field_rows_by_table()
    del rows_by_table["agent52_replay_table"]
    _write_field_rows_csv_directory(package_dir, rows_by_table)

    rows, source = _read_field_rows_package(package_dir)
    report = PressureResolutionReplayScenarioPackAgent(
        r7_pipeline_metrics=_r7_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        collaborative_control_metrics=_collaborative_control_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        field_replay_rows_by_table=rows,
    ).run([])
    validation = _field_rows_schema_validation(source, rows, _field_rows_package_schema())
    patch_plan = _field_rows_patch_plan(report, source, validation)

    assert source["field_rows_source_status"] == "field_rows_directory_loaded_with_schema_gaps"
    assert source["field_rows_source_format"] == "csv_directory_with_optional_metadata_json"
    assert "agent52_replay_table" in source["missing_tables"]
    assert "agent52_replay_table:missing_table" in source["preflight_blockers"]
    assert validation["field_rows_schema_validation_status"] == "schema_validation_failed_table_contract"
    assert patch_plan["field_rows_patch_plan_status"] == "field_rows_patch_plan_blocked_at_table_preflight"
    assert any(
        item["patch_id"] == "R8P_MISSING_TABLE_AGENT52_REPLAY_TABLE"
        for item in patch_plan["patch_items"]
    )


def test_pressure_resolution_csv_template_directory_is_written_with_six_required_tables(tmp_path) -> None:
    report = PressureResolutionReplayScenarioPackAgent(
        r7_pipeline_metrics=_r7_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        collaborative_control_metrics=_collaborative_control_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
    ).run([])
    template_dir = tmp_path / "pressure_resolution_replay_rows_csv_template"

    summary = _write_field_rows_csv_template(template_dir, report.metrics["template_rows_by_table"])

    assert summary["source_format"] == "csv_directory_with_optional_metadata_json"
    assert summary["can_be_field_evidence_by_template"] is False
    assert summary["template_row_count"] == len(PRESSURE_RESOLUTION_SCENARIOS) * (
        len(REQUIRED_TABLE_FIELDS) + 1
    )
    assert (template_dir / "metadata.json").exists()
    metadata = json.loads((template_dir / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["data_origin"].startswith("TODO_")
    for table in sorted({*REQUIRED_TABLE_FIELDS, "agent52_replay_table"}):
        csv_path = template_dir / f"{table}.csv"
        assert csv_path.exists()
        with csv_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            header = reader.fieldnames or []
            rows = list(reader)
        assert set(_required_fields_for_table(table)).issubset(set(header))
        assert len(rows) == len(PRESSURE_RESOLUTION_SCENARIOS)


def test_pressure_resolution_csv_template_directory_is_blocked_as_template_not_evidence(tmp_path) -> None:
    report = PressureResolutionReplayScenarioPackAgent(
        r7_pipeline_metrics=_r7_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        collaborative_control_metrics=_collaborative_control_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
    ).run([])
    template_dir = tmp_path / "pressure_resolution_replay_rows_csv_template"
    _write_field_rows_csv_template(template_dir, report.metrics["template_rows_by_table"])

    rows, source = _read_field_rows_package(template_dir)
    validation = _field_rows_schema_validation(source, rows, _field_rows_package_schema())
    patch_plan = _field_rows_patch_plan(
        PressureResolutionReplayScenarioPackAgent(
            r7_pipeline_metrics=_r7_metrics(),
            catalyst_proxy_metrics=_catalyst_proxy_metrics(),
            collaborative_control_metrics=_collaborative_control_metrics(),
            replay_evaluation_metrics=_replay_evaluation_metrics(),
            field_replay_rows_by_table=rows,
        ).run([]),
        source,
        validation,
    )

    assert source["field_rows_source_status"] == "field_rows_directory_loaded"
    assert source["field_rows_source_format"] == "csv_directory_with_optional_metadata_json"
    assert validation["field_rows_schema_validation_status"] == "schema_validation_failed_template_marker_contract"
    assert validation["template_marker_gap_count"] > 0
    assert patch_plan["field_rows_patch_plan_status"] == "field_rows_patch_plan_blocked_at_template_marker_contract"
    assert patch_plan["next_operator_action"] == "R8p_replace_template_markers_with_field_values"


def test_pressure_resolution_r7_to_r8p_alignment_separates_shared_fields_and_replay_export() -> None:
    alignment = _field_rows_r7_alignment(_field_rows_package_schema())

    assert alignment["alignment_status"] == "r7_to_r8p_alignment_ready_requires_r8p_supplements_and_agent52_export"
    assert alignment["expected_table_count"] == len(REQUIRED_TABLE_FIELDS) + 1
    assert alignment["r7_shared_table_count"] == len(REQUIRED_TABLE_FIELDS)
    assert alignment["agent52_export_required_field_count"] == len(_required_fields_for_table("agent52_replay_table"))
    assert alignment["can_generate_field_evidence_from_template"] is False
    agent52 = next(item for item in alignment["table_alignments"] if item["target_table"] == "agent52_replay_table")
    assert agent52["table_reuse_status"] == "requires_agent52_replay_export"
    assert all(mapping["source_kind"] == "agent52_replay_export_required" for mapping in agent52["field_mappings"])

    node = next(item for item in alignment["table_alignments"] if item["target_table"] == "node_modality_sensor_timeseries")
    sample_time = next(mapping for mapping in node["field_mappings"] if mapping["target_field"] == "sample_time_min")
    assert sample_time["source_kind"] == "alias_csv_field"
    assert sample_time["source_field"] == "timestamp_min"
    data_origin = next(mapping for mapping in node["field_mappings"] if mapping["target_field"] == "data_origin")
    assert data_origin["source_kind"] == "metadata_to_row_copy_after_agent44_gate"

    operation = next(item for item in alignment["table_alignments"] if item["target_table"] == "campaign_operation_log")
    pressure_resolution = next(
        mapping for mapping in operation["field_mappings"] if mapping["target_field"] == "pressure_source_resolution"
    )
    assert pressure_resolution["source_kind"] == "r8p_supplement_or_operator_record_required"
    assert pressure_resolution["can_be_filled_from_r7_csv_only"] is False


def test_pressure_resolution_r7_staging_blocks_without_r7_package() -> None:
    staging = _field_rows_r7_staging_preflight(
        None,
        _field_rows_r7_alignment(_field_rows_package_schema()),
        _field_rows_package_schema(),
    )

    assert staging["r7_staging_preflight_status"] == "r7_to_r8p_staging_preflight_no_r7_package_supplied"
    assert staging["staged_row_count"] == 0
    assert staging["can_enter_r8p_schema_preflight"] is False
    assert staging["can_generate_field_evidence_from_staging"] is False
    assert staging["can_write_to_actuator"] is False
    assert staging["can_write_to_release_gate"] is False


def test_pressure_resolution_r7_completion_plan_waits_for_source_package_without_r7_input() -> None:
    alignment = _field_rows_r7_alignment(_field_rows_package_schema())
    staging = _field_rows_r7_staging_preflight(None, alignment, _field_rows_package_schema())
    plan = _field_rows_r7_completion_plan(staging, alignment)
    route_contracts = _field_rows_r7_completion_route_contracts(plan)
    work_packages = _field_rows_r7_completion_route_work_packages(route_contracts)

    assert plan["completion_plan_status"] == "r7_to_r8p_completion_plan_waiting_for_r7_package"
    assert plan["can_generate_field_evidence_from_plan"] is False
    assert plan["can_write_to_actuator"] is False
    assert plan["can_write_to_release_gate"] is False
    assert plan["item_class_counts"]["r7_source_package"] == 1
    assert plan["item_class_counts"]["operator_supplement"] >= 1
    assert plan["item_class_counts"]["agent52_replay_export"] == 1
    source_item = next(item for item in plan["completion_items"] if item["completion_class"] == "r7_source_package")
    assert source_item["priority"] == "P0"
    assert "REAL_FIELD_REPLAY_PACKAGE_DIR" in source_item["operator_action"]
    assert route_contracts["completion_route_contracts_status"] == (
        "completion_route_contracts_ready_waiting_for_r7_package"
    )
    assert route_contracts["route_contract_count"] == 4
    assert route_contracts["open_route_count"] == 4
    assert route_contracts["open_route_ids"] == [
        "r7_source_package",
        "operator_supplement",
        "agent52_replay_export",
        "r8p_validation_gates",
    ]
    r7_route = next(route for route in route_contracts["route_contracts"] if route["route_id"] == "r7_source_package")
    assert r7_route["route_status"] == "route_blocked_waiting_for_r7_source_package"
    assert "REAL_FIELD_REPLAY_PACKAGE_DIR" in r7_route["input_contract"]
    assert r7_route["can_write_to_actuator"] is False
    assert work_packages["route_work_packages_status"] == "route_work_packages_ready_waiting_for_r7_package"
    assert work_packages["work_package_count"] == 4
    assert work_packages["open_work_package_count"] == 4
    assert work_packages["open_work_package_ids"][0] == "R8U25_R7_SOURCE_PACKAGE_WORK_PACKAGE"
    r7_package = next(
        package for package in work_packages["work_packages"] if package["route_id"] == "r7_source_package"
    )
    assert r7_package["work_package_status"] == "work_package_blocked_r7_source_package"
    assert "metadata.json" in r7_package["expected_input_files"]
    assert any("metadata.data_origin" in check for check in r7_package["acceptance_checks"])
    assert r7_package["can_generate_field_evidence_by_package_only"] is False
    assert r7_package["can_write_to_release_gate"] is False


def test_pressure_resolution_r7_work_package_templates_are_not_evidence_and_preflight_blocks_them(tmp_path) -> None:
    alignment = _field_rows_r7_alignment(_field_rows_package_schema())
    staging = _field_rows_r7_staging_preflight(None, alignment, _field_rows_package_schema())
    plan = _field_rows_r7_completion_plan(staging, alignment)
    route_contracts = _field_rows_r7_completion_route_contracts(plan)
    work_packages = _field_rows_r7_completion_route_work_packages(route_contracts)

    templates = _write_r7_completion_route_work_package_templates(work_packages, tmp_path / "wp_templates")
    waiting_preflight = _field_rows_r7_completion_route_work_package_submission_preflight(work_packages, None)
    template_preflight = _field_rows_r7_completion_route_work_package_submission_preflight(
        work_packages,
        tmp_path / "wp_templates",
    )
    waiting_patch_plan = _field_rows_r7_completion_route_work_package_patch_plan(waiting_preflight)
    template_patch_plan = _field_rows_r7_completion_route_work_package_patch_plan(template_preflight)
    waiting_assembly_gate = _field_rows_r7_completion_route_work_package_assembly_gate(
        waiting_preflight,
        waiting_patch_plan,
    )
    template_assembly_gate = _field_rows_r7_completion_route_work_package_assembly_gate(
        template_preflight,
        template_patch_plan,
    )

    assert templates["route_work_package_templates_status"] == "route_work_package_templates_ready_not_evidence"
    assert templates["work_package_template_count"] == 4
    assert templates["can_generate_field_evidence_from_templates"] is False
    r7_template = next(
        item for item in templates["package_templates"] if item["work_package_id"] == "R8U25_R7_SOURCE_PACKAGE_WORK_PACKAGE"
    )
    assert (tmp_path / "wp_templates" / "work_package_template_manifest.json").exists()
    assert (tmp_path / "wp_templates" / "R8U25_R7_SOURCE_PACKAGE_WORK_PACKAGE" / "metadata.json").exists()
    assert "metadata.json" in r7_template["relative_submission_files"]
    assert waiting_preflight["route_work_package_preflight_status"] == (
        "route_work_package_preflight_waiting_for_submission_dir"
    )
    assert waiting_preflight["blocked_work_package_count"] == 4
    assert waiting_preflight["can_generate_field_evidence_from_preflight"] is False
    assert waiting_patch_plan["route_work_package_patch_plan_status"] == (
        "route_work_package_patch_plan_waiting_for_submission_dir"
    )
    assert waiting_patch_plan["patch_item_count"] == 1
    assert waiting_patch_plan["highest_priority_patch_id"] == "R8U27_SET_R7_TO_R8P_WORK_PACKAGE_DIR"
    assert waiting_patch_plan["can_generate_field_evidence_from_patch_plan"] is False
    assert waiting_assembly_gate["route_work_package_assembly_gate_status"] == (
        "route_work_package_assembly_gate_blocked_waiting_for_submission_dir"
    )
    assert waiting_assembly_gate["assembly_step_count"] == 6
    assert waiting_assembly_gate["blocked_assembly_step_count"] == 6
    assert waiting_assembly_gate["can_materialize_candidate_rows_package"] is False
    assert waiting_assembly_gate["can_generate_field_evidence_from_assembly_gate"] is False
    assert template_preflight["route_work_package_preflight_status"] == (
        "route_work_package_preflight_blocked_submission_gaps"
    )
    assert template_preflight["submitted_work_package_count"] == 4
    assert template_preflight["passed_work_package_count"] == 0
    assert template_preflight["blocked_work_package_count"] == 4
    assert template_preflight["empty_csv_count"] > 0
    assert template_preflight["template_marker_count"] > 0
    assert template_preflight["metadata_provenance_gap_count"] >= 1
    assert template_preflight["can_write_to_actuator"] is False
    assert template_preflight["can_write_to_release_gate"] is False
    assert template_patch_plan["route_work_package_patch_plan_status"] == (
        "route_work_package_patch_plan_ready_for_submission_repairs"
    )
    assert template_patch_plan["patch_item_count"] > 0
    assert template_patch_plan["can_write_to_actuator"] is False
    assert template_patch_plan["can_write_to_release_gate"] is False
    patch_types = template_patch_plan["patch_item_type_counts"]
    assert patch_types["empty_csv_rows"] > 0
    assert patch_types["template_marker_replacement"] > 0
    assert patch_types["metadata_provenance"] >= 1
    assert patch_types["project_dependency_gate"] >= 1
    assert template_assembly_gate["route_work_package_assembly_gate_status"] == (
        "route_work_package_assembly_gate_blocked_by_work_package_repairs"
    )
    assert template_assembly_gate["assembly_step_count"] == 6
    assert template_assembly_gate["blocked_assembly_step_count"] == 6
    assert template_assembly_gate["highest_priority_patch_id"] == template_patch_plan["highest_priority_patch_id"]


def test_pressure_resolution_r7_staging_builds_draft_but_keeps_operator_and_agent52_gaps(tmp_path) -> None:
    package_dir = tmp_path / "r7_field_package"
    _write_r7_package_for_pressure_staging(package_dir)

    alignment = _field_rows_r7_alignment(_field_rows_package_schema())
    staging = _field_rows_r7_staging_preflight(
        package_dir,
        alignment,
        _field_rows_package_schema(),
    )
    plan = _field_rows_r7_completion_plan(staging, alignment)
    route_contracts = _field_rows_r7_completion_route_contracts(plan)
    work_packages = _field_rows_r7_completion_route_work_packages(route_contracts)

    assert staging["r7_staging_preflight_status"] == (
        "r7_to_r8p_staging_ready_requires_supplements_and_agent52_export"
    )
    assert staging["staged_table_count"] == len(REQUIRED_TABLE_FIELDS)
    assert staging["staged_row_count"] == len(REQUIRED_TABLE_FIELDS)
    assert staging["agent52_export_required_field_gap_count"] == len(_required_fields_for_table("agent52_replay_table"))
    assert staging["supplement_required_field_gap_count"] > 0
    assert staging["required_field_gap_count"] > 0
    assert staging["can_enter_r8p_schema_preflight"] is False
    assert staging["can_generate_field_evidence_from_staging"] is False

    staged_rows = staging["staged_draft_rows_by_table"]
    node_row = staged_rows["node_modality_sensor_timeseries"][0]
    assert node_row["sample_time_min"] == 10
    assert node_row["data_origin"] == "field"
    assert "unit" not in node_row

    pressure_row = staged_rows["pressure_headloss_event_log"][0]
    assert pressure_row["instrument_id"] == "INSTRUMENT_REAL_001"
    operation_row = staged_rows["campaign_operation_log"][0]
    assert operation_row["operator_review_required"] is True
    assert "pressure_source_resolution" not in operation_row
    operation_preflight = next(
        item for item in staging["table_staging_preflight"] if item["target_table"] == "campaign_operation_log"
    )
    assert "pressure_source_resolution" in operation_preflight["missing_required_fields"]
    agent52_preflight = next(
        item for item in staging["table_staging_preflight"] if item["target_table"] == "agent52_replay_table"
    )
    assert agent52_preflight["table_staging_status"] == "requires_agent52_replay_export_not_r7_staging"
    assert plan["completion_plan_status"] == "r7_to_r8p_completion_plan_ready_requires_supplement_and_agent52_export"
    assert plan["item_class_counts"]["operator_supplement"] >= 1
    assert plan["item_class_counts"]["agent52_replay_export"] == 1
    operation_item = next(
        item
        for item in plan["completion_items"]
        if item["completion_class"] == "operator_supplement" and item["target_table"] == "campaign_operation_log"
    )
    assert "pressure_source_resolution" in operation_item["target_fields"]
    assert "reviewer_id" in operation_item["target_fields"]
    export_item = next(item for item in plan["completion_items"] if item["completion_class"] == "agent52_replay_export")
    assert "policy_action_id" in export_item["target_fields"]
    assert export_item["can_create_field_evidence_by_item_only"] is False
    assert route_contracts["completion_route_contracts_status"] == (
        "completion_route_contracts_ready_requires_supplement_and_agent52_export"
    )
    assert "r7_source_package" not in route_contracts["open_route_ids"]
    assert "operator_supplement" in route_contracts["open_route_ids"]
    assert "agent52_replay_export" in route_contracts["open_route_ids"]
    r7_route = next(route for route in route_contracts["route_contracts"] if route["route_id"] == "r7_source_package")
    assert r7_route["route_status"] == "route_clear_r7_source_staged_or_not_required"
    operator_route = next(route for route in route_contracts["route_contracts"] if route["route_id"] == "operator_supplement")
    assert "campaign_operation_log" in operator_route["required_fields_by_table"]
    assert "pressure_source_resolution" in operator_route["required_fields_by_table"]["campaign_operation_log"]
    assert work_packages["route_work_packages_status"] == (
        "route_work_packages_ready_requires_supplement_and_agent52_export"
    )
    assert "R8U25_R7_SOURCE_PACKAGE_WORK_PACKAGE" not in work_packages["open_work_package_ids"]
    assert "R8U25_OPERATOR_SUPPLEMENT_WORK_PACKAGE" in work_packages["open_work_package_ids"]
    assert "R8U25_AGENT52_REPLAY_EXPORT_WORK_PACKAGE" in work_packages["open_work_package_ids"]
    operator_package = next(
        package for package in work_packages["work_packages"] if package["route_id"] == "operator_supplement"
    )
    assert operator_package["work_package_status"] == "work_package_open_operator_supplement"
    assert "operator_supplement_records.csv" in operator_package["expected_input_files"]
    assert "pressure_source_resolution" in operator_package["required_fields_by_table"]["campaign_operation_log"]
    assert any("reviewer_id" in check for check in operator_package["acceptance_checks"])
    agent52_package = next(
        package for package in work_packages["work_packages"] if package["route_id"] == "agent52_replay_export"
    )
    assert "agent52_replay_table.csv" in agent52_package["expected_input_files"]
    assert agent52_package["evidence_level_after_package"].startswith("replay_candidate")


def test_pressure_resolution_patch_plan_targets_rejected_template_scenario_rows() -> None:
    template_report = PressureResolutionReplayScenarioPackAgent(
        r7_pipeline_metrics=_r7_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        collaborative_control_metrics=_collaborative_control_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
    ).run([])
    report = PressureResolutionReplayScenarioPackAgent(
        r7_pipeline_metrics=_r7_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        collaborative_control_metrics=_collaborative_control_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        field_replay_rows_by_table=template_report.metrics["template_rows_by_table"],
    ).run([])
    source = {
        "field_rows_source_status": "field_rows_file_loaded",
        "field_rows_source_path": "memory://template_rows",
        "expected_tables": sorted({*REQUIRED_TABLE_FIELDS, "agent52_replay_table"}),
        "missing_tables": [],
        "empty_tables": [],
        "invalid_table_shapes": [],
        "unknown_tables": [],
        "preflight_blockers": [],
    }
    patch_plan = _field_rows_patch_plan(report, source)

    assert patch_plan["field_rows_patch_plan_status"] == "field_rows_patch_plan_blocked_at_scenario_acceptance"
    assert patch_plan["patch_item_count"] == len(PRESSURE_RESOLUTION_SCENARIOS)
    assert all(item["patch_type"] == "scenario_acceptance" for item in patch_plan["patch_items"])
    assert all(item["can_write_to_actuator"] is False for item in [patch_plan])
    assert patch_plan["template_rows_are_field_evidence"] is False


def test_pressure_resolution_patch_plan_clears_after_all_real_scenarios_are_accepted() -> None:
    report = PressureResolutionReplayScenarioPackAgent(
        r7_pipeline_metrics=_r7_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        collaborative_control_metrics=_collaborative_control_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        field_replay_rows_by_table=_complete_field_rows_by_table(),
    ).run([])
    source = {
        "field_rows_source_status": "field_rows_file_loaded",
        "field_rows_source_path": "memory://complete_rows",
        "expected_tables": sorted({*REQUIRED_TABLE_FIELDS, "agent52_replay_table"}),
        "missing_tables": [],
        "empty_tables": [],
        "invalid_table_shapes": [],
        "unknown_tables": [],
        "preflight_blockers": [],
    }
    patch_plan = _field_rows_patch_plan(report, source)
    handoff = _field_rows_operator_handoff(report, source, patch_plan)

    assert patch_plan["field_rows_patch_plan_status"] == "field_rows_patch_plan_clear_ready_for_r8v_routing"
    assert patch_plan["next_operator_action"] == "R8v_route_pressure_resolution_rows_to_field_replay_and_holdout_gates"
    assert patch_plan["patch_item_count"] == 0
    assert patch_plan["highest_priority_patch_id"] is None
    assert handoff["field_rows_operator_handoff_status"] == "field_rows_operator_handoff_ready_for_r8v_routing"
    assert handoff["next_operator_action"] == "R8v_route_pressure_resolution_rows_to_field_replay_and_holdout_gates"
    assert handoff["can_write_to_actuator"] is False
    assert handoff["can_write_to_release_gate"] is False


def _field_source_for_rows(rows: dict[str, list[dict[str, object]]]) -> dict[str, object]:
    return {
        "field_rows_source_status": "field_rows_file_loaded",
        "field_rows_source_path": "memory://complete_rows",
        "expected_tables": sorted({*REQUIRED_TABLE_FIELDS, "agent52_replay_table"}),
        "missing_tables": [],
        "empty_tables": [],
        "invalid_table_shapes": [],
        "unknown_tables": [],
        "preflight_blockers": [],
        "table_count": len(REQUIRED_TABLE_FIELDS) + 1,
        "row_count": sum(len(table_rows) for table_rows in rows.values()),
    }


def _write_r7_package_for_pressure_staging(package_dir) -> None:
    package_dir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "data_origin": "field",
        "site_id": "SITE_REAL_001",
        "campaign_id": "CAMPAIGN_REAL_001",
        "sampling_start": "2026-06-02T09:00:00+08:00",
        "sampling_end": "2026-06-02T12:00:00+08:00",
        "operator_id": "OP_REAL_001",
        "instrument_snapshot_id": "INSTRUMENT_REAL_001",
        "chain_of_custody_id": "COC_REAL_001",
    }
    (package_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False), encoding="utf-8")
    _write_csv(
        package_dir / "node_modality_sensor_timeseries.csv",
        {
            "batch_id": "BATCH_REAL_001",
            "timestamp_min": "10",
            "node_id": "N3_catalyst_bed",
            "zone": "catalyst_zone",
            "modality": "pressure_drop_kPa",
            "value": "4.2",
            "sensor_status": "qa_pass",
            "instrument_id": "PRESSURE_NODE_001",
            "acquisition_time_min": "9",
            "ingest_time_min": "11",
        },
    )
    _write_csv(
        package_dir / "pressure_headloss_event_log.csv",
        {
            "campaign_id": "CAMPAIGN_REAL_001",
            "batch_id": "BATCH_REAL_001",
            "event_time_min": "12",
            "bed_id": "N3_catalyst_bed",
            "pressure_drop_kPa": "4.4",
            "headloss_kPa_per_m": "0.7",
            "flow_Lmin": "12.5",
            "matched_lab_sample_time_min": "18",
            "regeneration_event": "false",
            "hydraulic_anomaly_label": "pressure_source_conflict",
            "operator_review_required": "true",
        },
    )
    _write_csv(
        package_dir / "campaign_operation_log.csv",
        {
            "campaign_id": "CAMPAIGN_REAL_001",
            "batch_id": "BATCH_REAL_001",
            "action_id": "operator_review_pressure_source",
            "command_time_min": "13",
            "effect_time_min": "15",
            "start_min": "13",
            "end_min": "45",
            "release_policy": "hold_until_review",
            "recycle_ratio": "0.35",
            "hold_time_min": "45",
            "pressure_headloss_review_required": "true",
        },
    )
    _write_csv(
        package_dir / "offline_lab_results.csv",
        {
            "batch_id": "BATCH_REAL_001",
            "sample_time_min": "15",
            "result_time_min": "24",
            "lab_label_time_min": "24",
            "analyte": "catalyst_activity",
            "value": "0.72",
            "unit": "activity_index",
            "method": "offline_activity_panel",
            "qa_flag": "pass",
        },
    )
    _write_csv(
        package_dir / "fast_proxy_event_log.csv",
        {
            "campaign_id": "CAMPAIGN_REAL_001",
            "batch_id": "BATCH_REAL_001",
            "event_time_min": "16",
            "proxy_score": "0.81",
            "specificity_guard_score": "0.76",
            "protective_triggered": "true",
            "triggered_action_id": "hold_for_pressure_review",
            "field_label_matrix_shock": "false",
            "lab_label_time_min": "24",
            "false_positive_cost_index": "0.2",
        },
    )


def _write_csv(path, row: dict[str, object]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row))
        writer.writeheader()
        writer.writerow(row)


def _ready_downstream_target_gate_preflight() -> tuple[dict[str, object], dict[str, object]]:
    rows_by_table = _complete_field_rows_by_table()
    report = PressureResolutionReplayScenarioPackAgent(
        r7_pipeline_metrics=_r7_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        collaborative_control_metrics=_collaborative_control_metrics(),
        replay_evaluation_metrics=_replay_evaluation_metrics(),
        field_replay_rows_by_table=rows_by_table,
    ).run([])
    source = {
        "field_rows_source_status": "field_rows_file_loaded",
        "field_rows_source_path": "memory://complete_rows",
        "expected_tables": sorted({*REQUIRED_TABLE_FIELDS, "agent52_replay_table"}),
        "missing_tables": [],
        "empty_tables": [],
        "invalid_table_shapes": [],
        "unknown_tables": [],
        "preflight_blockers": [],
        "table_count": len(REQUIRED_TABLE_FIELDS) + 1,
        "row_count": sum(len(rows) for rows in rows_by_table.values()),
    }
    schema = _field_rows_package_schema()
    validation = _field_rows_schema_validation(source, rows_by_table, schema)
    bundle_preflight = _field_rows_batch_bundle_preflight(report, source, rows_by_table, schema, validation)
    temporal_preflight = _field_rows_temporal_window_preflight(
        report,
        source,
        rows_by_table,
        validation,
        bundle_preflight,
    )
    semantic_preflight = _field_rows_scenario_semantic_preflight(
        report,
        source,
        rows_by_table,
        validation,
        bundle_preflight,
        temporal_preflight,
    )
    downstream_routing_preflight = _field_rows_downstream_routing_preflight(
        report,
        source,
        validation,
        bundle_preflight,
        temporal_preflight,
        semantic_preflight,
    )
    downstream_route_handoff = _field_rows_downstream_route_handoff(downstream_routing_preflight)
    downstream_target_gate_preflight = _field_rows_downstream_target_gate_preflight(
        downstream_route_handoff
    )
    return downstream_target_gate_preflight, _field_rows_downstream_target_gate_result_intake_schema(
        downstream_target_gate_preflight
    )


def _target_gate_result_package(
    result_intake_schema: dict[str, object],
    release_gate_write_target_id: str = "",
    status_by_target_id: dict[str, str] | None = None,
) -> dict[str, object]:
    status_by_target_id = status_by_target_id or {}
    target_gate_results = []
    for target_schema in result_intake_schema.get("target_result_schemas", []) or []:
        target_id = str(target_schema.get("target_id", ""))
        expected_metrics = [
            str(metric) for metric in target_schema.get("expected_gate_metrics", []) or []
        ]
        target_gate_results.append(
            {
                "target_id": target_id,
                "target_gate_status": status_by_target_id.get(target_id, "target_gate_result_passed"),
                "batch_ids": [f"FIELD_{scenario['scenario_id']}" for scenario in PRESSURE_RESOLUTION_SCENARIOS],
                "source_metrics_artifact": str(target_schema.get("expected_metrics_artifact", "")),
                "reported_metrics": {metric: 1 for metric in expected_metrics},
                "operator_review_boundary_preserved": True,
                "can_write_to_actuator": False,
                "can_write_to_release_gate": target_id == release_gate_write_target_id,
                "field_claim_upgrade_allowed": False,
            }
        )
    return {
        "package_metadata": {
            "package_id": "R8V_TARGET_GATE_RESULTS_TEST_PACKAGE",
            "evidence_status": "test_fixture_not_field_evidence",
        },
        "target_gate_results": target_gate_results,
    }


def _ready_downstream_target_gate_result_arbitration(tmp_path) -> dict[str, object]:
    downstream_target_gate_preflight, result_intake_schema = _ready_downstream_target_gate_preflight()
    result_package_path = tmp_path / "target_gate_results_ready_for_review.json"
    result_package_path.write_text(
        json.dumps(
            _target_gate_result_package(result_intake_schema),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    result_preflight = _field_rows_downstream_target_gate_result_preflight(
        downstream_target_gate_preflight,
        result_intake_schema,
        result_package_path,
    )
    return _field_rows_downstream_target_gate_result_arbitration(result_preflight)


def _operator_review_package(
    review_template: dict[str, object],
    release_gate_write_target_id: str = "",
    decision_by_target_id: dict[str, str] | None = None,
) -> dict[str, object]:
    decision_by_target_id = decision_by_target_id or {}
    review_rows = []
    for template_row in review_template.get("target_review_templates", []) or []:
        target_id = str(template_row.get("target_id", ""))
        review_rows.append(
            {
                "target_id": target_id,
                "target_gate_status": str(template_row.get("target_gate_status", "")),
                "operator_review_decision": decision_by_target_id.get(
                    target_id,
                    "operator_approved_for_post_review_gate",
                ),
                "reviewer_id": "operator_reviewer_001",
                "review_time": "2026-06-04T10:00:00+08:00",
                "review_notes": "reviewed target gate outputs and no-write boundaries",
                "boundary_acknowledgement": True,
                "can_write_to_actuator": False,
                "can_write_to_release_gate": target_id == release_gate_write_target_id,
                "field_claim_upgrade_allowed": False,
            }
        )
    return {
        "review_metadata": {
            "package_id": "R8V_OPERATOR_REVIEW_TEST_PACKAGE",
            "evidence_status": "test_fixture_not_field_evidence",
        },
        "review_rows": review_rows,
    }


def _r7_metrics() -> dict[str, object]:
    readiness = {
        "pressure_source_conflict_count": 0,
        "resolved_pressure_source_conflict_count": 0,
        "unresolved_pressure_source_conflict_count": 0,
        "pressure_source_resolution_record_count": 0,
        "pressure_source_conflict_requires_operator_review": False,
        "field_package_pressure_conflict_resolution_status": "pressure_source_conflict_resolution_clear",
        "field_package_pressure_conflict_resolution_ready": True,
    }
    return {
        "pipeline_readiness": dict(readiness),
        "field_package_coverage": {"readiness": dict(readiness)},
    }


def _catalyst_proxy_metrics() -> dict[str, object]:
    return {
        "readiness": {
            "pressure_source_conflict_count": 0,
            "resolved_pressure_source_conflict_count": 0,
            "unresolved_pressure_source_conflict_count": 0,
            "pressure_source_resolution_record_count": 0,
            "conflict_requires_operator_review": False,
            "field_holdout_scoreable_batch_count": 0,
        },
        "field_proxy_holdout_summary": {
            "pressure_source_conflict_count": 0,
            "resolved_pressure_source_conflict_count": 0,
            "unresolved_pressure_source_conflict_count": 0,
            "pressure_source_resolution_record_count": 0,
            "conflict_requires_operator_review": False,
            "scoreable_batch_count": 0,
        },
    }


def _collaborative_control_metrics() -> dict[str, object]:
    return {
        "control_replay_guardrail_context": {
            "pressure_source_conflict_count": 0,
            "resolved_pressure_source_conflict_count": 0,
            "unresolved_pressure_source_conflict_count": 0,
            "pressure_source_resolution_record_count": 0,
            "pressure_source_conflict_control_block": False,
            "conflict_requires_operator_review": False,
        }
    }


def _replay_evaluation_metrics() -> dict[str, object]:
    pressure_fields = {
        "pressure_source_conflict_count": 0,
        "resolved_pressure_source_conflict_count": 0,
        "unresolved_pressure_source_conflict_count": 0,
        "pressure_source_resolution_record_count": 0,
        "pressure_source_conflict_clear": True,
        "pressure_source_conflict_requires_operator_review": False,
        "pressure_source_conflict_replay_blocked_case_count": 0,
    }
    return {
        "offline_evaluation_metrics": dict(pressure_fields),
        "readiness": dict(pressure_fields),
        "pressure_headloss_context": dict(pressure_fields),
        "agent49_writeback": {"metric_patch": dict(pressure_fields)},
    }


def _complete_field_rows_by_table() -> dict[str, list[dict[str, object]]]:
    rows_by_table: dict[str, list[dict[str, object]]] = {
        table: []
        for table in REQUIRED_TABLE_FIELDS
    }
    rows_by_table["agent52_replay_table"] = []
    for scenario in PRESSURE_RESOLUTION_SCENARIOS:
        scenario_id = str(scenario["scenario_id"])
        scenario_type = str(scenario["scenario_type"])
        batch_id = f"FIELD_{scenario_id}"
        unresolved = scenario_type == "unresolved_conflict_review_block"
        resolved = not unresolved
        rows_by_table["node_modality_sensor_timeseries"].append(
            {
                "scenario_id": scenario_id,
                "scenario_type": scenario_type,
                "batch_id": batch_id,
                "node_id": "N3_catalyst_bed",
                "modality": "pressure_drop_kPa",
                "value": 4.2,
                "unit": "kPa",
                "sample_time_min": 10,
                "instrument_id": "P_SENSOR_01",
                "sensor_status": "qa_pass",
                "data_origin": "field",
            }
        )
        rows_by_table["pressure_headloss_event_log"].append(
            {
                "scenario_id": scenario_id,
                "scenario_type": scenario_type,
                "batch_id": batch_id,
                "bed_id": "N3_catalyst_bed",
                "pressure_drop_kPa": 4.4,
                "headloss_kPa_per_m": 0.7,
                "flow_Lmin": 12.5,
                "event_time_min": 12,
                "matched_lab_sample_time_min": 18,
                "hydraulic_anomaly_label": "pressure_source_conflict" if unresolved else "reviewed_clear",
                "instrument_id": "P_EVENT_01",
                "data_origin": "field",
            }
        )
        rows_by_table["campaign_operation_log"].append(
            {
                "scenario_id": scenario_id,
                "scenario_type": scenario_type,
                "batch_id": batch_id,
                "action_id": "operator_review_pressure_source",
                "operator_review_required": unresolved,
                "pressure_source_resolution": "unresolved" if unresolved else "resolved",
                "authoritative_pressure_source": "pending_operator_review"
                if unresolved
                else "pressure_headloss_event_log",
                "reviewer_id": "OP_REVIEWER_01",
                "review_time": "2026-06-02T10:15:00+08:00",
                "calibration_action_id": "pending_calibration" if unresolved else "CAL_PRESSURE_001",
                "calibration_note": "operator reviewed pressure source chain",
                "hold_time_min": 45,
                "recycle_ratio": 0.35,
                "data_origin": "field",
            }
        )
        rows_by_table["offline_lab_results"].append(
            {
                "scenario_id": scenario_id,
                "scenario_type": scenario_type,
                "batch_id": batch_id,
                "sample_time_min": 15,
                "lab_label_time_min": 24,
                "analyte": "catalyst_activity",
                "value": 0.72,
                "unit": "activity_index",
                "method": "offline_activity_panel",
                "qa_flag": "pass",
                "data_origin": "field",
            }
        )
        rows_by_table["fast_proxy_event_log"].append(
            {
                "scenario_id": scenario_id,
                "scenario_type": scenario_type,
                "batch_id": batch_id,
                "proxy_label_time_min": 14,
                "proxy_event_type": "pressure_resolution_review",
                "protective_triggered": unresolved,
                "false_positive_cost_index": 0.2 if unresolved else 0.0,
                "data_origin": "field",
            }
        )
        rows_by_table["agent52_replay_table"].append(
            {
                "scenario_id": scenario_id,
                "scenario": scenario_type,
                "scenario_type": scenario_type,
                "batch_id": batch_id,
                "policy_action_id": "hold_for_operator_review" if unresolved else "guardrail_clearance_candidate",
                "expert_action_id": "hold_for_operator_review" if unresolved else "guardrail_clearance_candidate",
                "pressure_source_conflict_count": 1,
                "resolved_pressure_source_conflict_count": 0 if unresolved else 1,
                "unresolved_pressure_source_conflict_count": 1 if unresolved else 0,
                "pressure_source_resolution_record_count": 0 if unresolved else 1,
                "pressure_source_conflict_requires_operator_review": unresolved,
                "pressure_source_conflict_control_block": unresolved,
                "data_origin": "field_replay",
            }
        )
    return rows_by_table


def _write_field_rows_csv_directory(path, rows_by_table: dict[str, list[dict[str, object]]]) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / "metadata.json").write_text(
        json.dumps(
            {
                "data_origin": "field",
                "site_id": "TEST_SITE",
                "campaign_id": "TEST_CAMPAIGN",
                "chain_of_custody_id": "TEST_CHAIN",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    for table, rows in rows_by_table.items():
        fieldnames = sorted({field for row in rows for field in row})
        with (path / f"{table}.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
