from __future__ import annotations

from pathlib import Path
from typing import Any

from water_ai.agents.field_replay_evidence_chain_agent import FieldReplayEvidenceChainAgent
from water_ai.agents.field_replay_import_agent import (
    FieldReplayImportAgent,
    load_field_replay_package,
    preflight_field_replay_package,
)
from water_ai.agents.soft_sensor_matrix_coupling_agent import (
    preflight_field_path_endpoint_label_package,
)
from water_ai.catalyst_proxy_field_holdout import build_catalyst_proxy_field_holdout_summary
from water_ai.domain import AgentReport
from water_ai.field_package_coverage import assess_field_package_coverage
from water_ai.real_field_package_acceptance_gate import RealFieldPackageAcceptanceGate


def build_real_field_replay_pipeline(
    package_dir: str | Path,
    *,
    matrix_fast_proxy_metrics: dict[str, Any] | None = None,
    soft_sensor_field_holdout_gate_metrics: dict[str, Any] | None = None,
    claim_specific_package_metrics: dict[str, Any] | None = None,
    catalyst_proxy_metrics: dict[str, Any] | None = None,
    multi_facility_replay_evaluation_metrics: dict[str, Any] | None = None,
    unified_field_evidence_gate_metrics: dict[str, Any] | None = None,
    field_package_submission_repair_response: dict[str, Any] | None = None,
    minimum_proxy_events: int = 12,
) -> dict[str, Any]:
    """Run the R7 import -> replay evidence chain without mutating canonical outputs."""

    metadata, raw_tables = load_field_replay_package(package_dir)
    import_report = FieldReplayImportAgent(metadata=metadata, raw_tables=raw_tables).run([])
    chain_report = FieldReplayEvidenceChainAgent(
        import_report=import_report,
        matrix_fast_proxy_metrics=matrix_fast_proxy_metrics or {},
        minimum_proxy_events=minimum_proxy_events,
    ).run([])
    coverage = assess_field_package_coverage(
        package_dir,
        claim_specific_package_metrics=claim_specific_package_metrics or {},
        soft_sensor_field_holdout_gate_metrics=soft_sensor_field_holdout_gate_metrics or {},
        catalyst_proxy_metrics=catalyst_proxy_metrics or {},
    )
    path_endpoint_preflight = preflight_field_path_endpoint_label_package(raw_tables)
    catalyst_holdout_summary = (
        build_catalyst_proxy_field_holdout_summary(package_dir)
        if catalyst_proxy_metrics
        else {}
    )
    timestamped_metrics = _stage_metrics(chain_report, "timestamped_replay_stage")
    g6_metrics = _stage_metrics(chain_report, "g6_stage")
    package_preflight = preflight_field_replay_package(package_dir)
    r7_result = RealFieldPackageAcceptanceGate(
        field_replay_import_metrics=import_report.metrics,
        timestamped_replay_metrics=timestamped_metrics,
        field_replay_gate_metrics=g6_metrics,
        field_replay_evidence_chain_metrics=chain_report.metrics,
        multi_facility_replay_evaluation_metrics=multi_facility_replay_evaluation_metrics or {},
        soft_sensor_field_holdout_gate_metrics=soft_sensor_field_holdout_gate_metrics or {},
        claim_specific_package_metrics=claim_specific_package_metrics or {},
        unified_field_evidence_gate_metrics=unified_field_evidence_gate_metrics or {},
    ).build()
    pipeline_readiness = _pipeline_readiness(
        import_report,
        chain_report,
        r7_result,
        coverage,
        catalyst_holdout_summary,
        path_endpoint_preflight,
    )
    submission_readiness = _field_package_submission_readiness(
        package_preflight,
        coverage,
        path_endpoint_preflight,
        r7_result,
        pipeline_readiness,
    )
    repair_work_order = submission_readiness["field_package_submission_repair_work_order"]
    repair_response_template = build_field_package_submission_repair_response_template(repair_work_order)
    repair_response_preflight = preflight_field_package_submission_repair_response(
        field_package_submission_repair_response or repair_response_template,
        repair_work_order,
    )
    return {
        "package_dir": str(Path(package_dir)),
        "preflight": package_preflight,
        "field_path_endpoint_label_package_preflight": path_endpoint_preflight,
        "field_package_submission_readiness": submission_readiness,
        "field_package_submission_repair_response_template": repair_response_template,
        "field_package_submission_repair_response_preflight": repair_response_preflight,
        "field_package_coverage": coverage,
        "agent51_field_proxy_holdout_summary": catalyst_holdout_summary,
        "import_report": _report_payload(import_report),
        "field_replay_evidence_chain_report": _report_payload(chain_report, strip_normalized=True),
        "r7_acceptance": r7_result,
        "pipeline_readiness": {
            **pipeline_readiness,
            "field_package_submission_readiness_status": submission_readiness[
                "submission_readiness_status"
            ],
            "field_package_submission_highest_priority_blocker": submission_readiness[
                "highest_priority_blocker"
            ],
            "field_package_submission_next_operator_action": submission_readiness[
                "next_operator_action"
            ],
            "field_package_submission_blocking_stage_count": submission_readiness[
                "blocking_stage_count"
            ],
            "field_package_submission_can_submit_to_agent42_smoke_replay": submission_readiness[
                "can_submit_to_agent42_smoke_replay"
            ],
            "field_package_submission_can_route_to_path_endpoint_layout_holdout": submission_readiness[
                "can_route_to_path_endpoint_layout_holdout"
            ],
            "field_package_submission_no_write_boundary_pass": submission_readiness[
                "no_write_boundary_pass"
            ],
            "field_package_submission_repair_work_order_status": submission_readiness[
                "field_package_submission_repair_work_order"
            ]["work_order_status"],
            "field_package_submission_repair_item_count": submission_readiness[
                "field_package_submission_repair_work_order"
            ]["repair_item_count"],
            "field_package_submission_repair_response_preflight_status": repair_response_preflight[
                "preflight_status"
            ],
            "field_package_submission_repair_response_missing_item_count": repair_response_preflight[
                "missing_response_item_count"
            ],
            "field_package_submission_repair_response_template_marker_count": repair_response_preflight[
                "template_marker_count"
            ],
            "field_package_submission_repair_response_can_route_to_r7_preflight": repair_response_preflight[
                "can_route_to_r7_preflight"
            ],
        },
    }


def _stage_metrics(chain_report: AgentReport, stage_key: str) -> dict[str, Any]:
    stage = chain_report.metrics.get(stage_key, {})
    if not isinstance(stage, dict):
        return {}
    readiness = stage.get("readiness", {})
    return {
        "readiness": readiness if isinstance(readiness, dict) else {},
        "stage_summary": stage.get("summary", ""),
        "issue_types": stage.get("issue_types", []),
    }


def _report_payload(report: AgentReport, *, strip_normalized: bool = False) -> dict[str, Any]:
    metrics = report.metrics
    if strip_normalized:
        metrics = _strip_normalized(metrics)
    return {
        "agent_name": report.agent_name,
        "confidence": report.confidence,
        "summary": report.summary,
        "recommendations": report.recommendations,
        "issue_types": [issue.issue_type for issue in report.issues],
        "metrics": metrics,
    }


def _strip_normalized(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _strip_normalized(item)
            for key, item in value.items()
            if key != "normalized_datasets"
        }
    if isinstance(value, list):
        return [_strip_normalized(item) for item in value]
    return value


def _pipeline_readiness(
    import_report: AgentReport,
    chain_report: AgentReport,
    r7_result: dict[str, Any],
    coverage: dict[str, Any],
    catalyst_holdout_summary: dict[str, Any],
    path_endpoint_preflight: dict[str, Any],
) -> dict[str, Any]:
    import_readiness = import_report.metrics.get("readiness", {})
    chain_readiness = chain_report.metrics.get("readiness", {})
    r7_readiness = r7_result.get("readiness", {})
    coverage_readiness = coverage.get("readiness", {})
    patch_plan = coverage.get("patch_plan", {})
    path_endpoint_ready = bool(_get(path_endpoint_preflight, "can_route_to_field_layout_holdout", False))
    path_endpoint_final_label_ready = _field_path_endpoint_final_effluent_label_ready(path_endpoint_preflight)
    can_route_to_field_holdout = bool(_get(coverage_readiness, "can_route_to_field_holdout", False))
    return {
        "field_replay_import_status": _get(import_readiness, "field_replay_import_status", "unknown"),
        "field_replay_evidence_chain_status": _get(
            chain_readiness,
            "field_replay_evidence_chain_status",
            "unknown",
        ),
        "field_package_coverage_status": _get(coverage_readiness, "field_package_coverage_status", "unknown"),
        "claim_specific_coverage_rate": _get(coverage_readiness, "claim_specific_coverage_rate", 0.0),
        "soft_holdout_coverage_pass": _get(coverage_readiness, "soft_holdout_coverage_pass", False),
        "field_proxy_holdout_status": _get(coverage_readiness, "field_proxy_holdout_status", "unknown"),
        "field_proxy_holdout_required": bool(_get(coverage_readiness, "field_proxy_holdout_required", False)),
        "field_proxy_holdout_coverage_pass": bool(
            _get(coverage_readiness, "field_proxy_holdout_coverage_pass", False)
        ),
        "field_proxy_holdout_matched_batch_count": _get(
            coverage_readiness,
            "field_proxy_holdout_matched_batch_count",
            0,
        ),
        "field_proxy_holdout_minimum_matched_batch_count": _get(
            coverage_readiness,
            "field_proxy_holdout_minimum_matched_batch_count",
            0,
        ),
        "pressure_source_conflict_count": _get(coverage_readiness, "pressure_source_conflict_count", 0),
        "resolved_pressure_source_conflict_count": _get(
            coverage_readiness,
            "resolved_pressure_source_conflict_count",
            0,
        ),
        "unresolved_pressure_source_conflict_count": _get(
            coverage_readiness,
            "unresolved_pressure_source_conflict_count",
            0,
        ),
        "pressure_source_resolution_record_count": _get(
            coverage_readiness,
            "pressure_source_resolution_record_count",
            0,
        ),
        "pressure_source_conflict_requires_operator_review": bool(
            _get(coverage_readiness, "pressure_source_conflict_requires_operator_review", False)
        ),
        "pressure_source_conflict_batch_ids_sample": _get(
            coverage_readiness,
            "pressure_source_conflict_batch_ids_sample",
            [],
        ),
        "field_package_pressure_conflict_resolution_status": _get(
            coverage_readiness,
            "field_package_pressure_conflict_resolution_status",
            "unknown",
        ),
        "field_package_pressure_conflict_resolution_ready": bool(
            _get(coverage_readiness, "field_package_pressure_conflict_resolution_ready", False)
        ),
        "agent51_pressure_source_conflict_count": _get(
            catalyst_holdout_summary,
            "pressure_source_conflict_count",
            0,
        ),
        "agent51_resolved_pressure_source_conflict_count": _get(
            catalyst_holdout_summary,
            "resolved_pressure_source_conflict_count",
            0,
        ),
        "agent51_unresolved_pressure_source_conflict_count": _get(
            catalyst_holdout_summary,
            "unresolved_pressure_source_conflict_count",
            0,
        ),
        "agent51_pressure_source_resolution_record_count": _get(
            catalyst_holdout_summary,
            "pressure_source_resolution_record_count",
            0,
        ),
        "agent51_pressure_source_conflict_requires_operator_review": bool(
            _get(catalyst_holdout_summary, "conflict_requires_operator_review", False)
        ),
        "agent51_field_proxy_summary_status": _get(
            catalyst_holdout_summary,
            "field_proxy_holdout_summary_status",
            "not_requested",
        ),
        "agent51_field_proxy_scoreable_batch_count": _get(
            catalyst_holdout_summary,
            "scoreable_batch_count",
            0,
        ),
        "agent51_field_proxy_validation_pass": bool(
            _get(catalyst_holdout_summary, "field_validation_pass", False)
        ),
        "agent51_field_proxy_holdout_mae": _get(
            _get(catalyst_holdout_summary, "field_validation_metrics", {}),
            "holdout_mae",
            None,
        ),
        "agent51_field_proxy_label_correlation": _get(
            _get(catalyst_holdout_summary, "field_validation_metrics", {}),
            "proxy_label_correlation",
            None,
        ),
        "minimum_replay_contract_status": _get(
            coverage_readiness,
            "minimum_replay_contract_status",
            "unknown",
        ),
        "minimum_replay_contract_pass": bool(_get(coverage_readiness, "minimum_replay_contract_pass", False)),
        "field_evidence_sufficiency_status": _get(
            coverage_readiness,
            "field_evidence_sufficiency_status",
            "unknown",
        ),
        "field_evidence_sufficiency_score": _get(
            coverage_readiness,
            "field_evidence_sufficiency_score",
            0.0,
        ),
        "field_evidence_smoke_pass": bool(_get(coverage_readiness, "field_evidence_smoke_pass", False)),
        "field_evidence_calibration_volume_pass": bool(
            _get(coverage_readiness, "field_evidence_calibration_volume_pass", False)
        ),
        "can_route_to_agent42_smoke_replay": bool(
            _get(coverage_readiness, "can_route_to_agent42_smoke_replay", False)
        ),
        "can_route_to_field_holdout": bool(_get(coverage_readiness, "can_route_to_field_holdout", False)),
        "field_path_endpoint_label_preflight_status": _get(
            path_endpoint_preflight,
            "preflight_status",
            "not_available",
        ),
        "field_path_endpoint_matched_batch_count": _get(path_endpoint_preflight, "matched_batch_count", 0),
        "field_path_endpoint_minimum_matched_batch_count": _get(
            path_endpoint_preflight,
            "minimum_matched_batch_count",
            5,
        ),
        "field_path_endpoint_missing_tables": _get(path_endpoint_preflight, "missing_tables", []),
        "field_path_endpoint_required_field_gap_count": _get(
            path_endpoint_preflight,
            "required_field_gap_count",
            0,
        ),
        "field_path_endpoint_template_marker_count": _get(
            path_endpoint_preflight,
            "template_marker_count",
            0,
        ),
        "field_path_endpoint_table_row_counts": _get(
            path_endpoint_preflight,
            "table_row_counts",
            {},
        ),
        "field_path_endpoint_table_batch_counts": _get(
            path_endpoint_preflight,
            "table_batch_counts",
            {},
        ),
        "field_path_endpoint_batch_alignment_gap_count": _get(
            path_endpoint_preflight,
            "batch_alignment_gap_count",
            0,
        ),
        "field_path_endpoint_required_matched_batch_deficit": _get(
            path_endpoint_preflight,
            "required_matched_batch_deficit",
            0,
        ),
        "field_path_endpoint_alignment_patch_plan_status": _get(
            _get(path_endpoint_preflight, "alignment_patch_plan", {}),
            "patch_plan_status",
            "not_available",
        ),
        "field_path_endpoint_alignment_patch_plan_item_count": _get(
            _get(path_endpoint_preflight, "alignment_patch_plan", {}),
            "item_count",
            0,
        ),
        "field_path_endpoint_label_package_ready": path_endpoint_ready,
        "field_path_endpoint_final_effluent_label_ready": path_endpoint_final_label_ready,
        "can_route_to_field_layout_holdout_with_path_labels": can_route_to_field_holdout and path_endpoint_ready,
        "release_gate_endpoint_label_blocked": not path_endpoint_final_label_ready,
        "can_route_to_human_review_candidate": bool(
            _get(coverage_readiness, "can_route_to_human_review_candidate", False)
        ),
        "field_supported_claim_upgrade_ready": bool(
            _get(coverage_readiness, "field_supported_claim_upgrade_ready", False)
        ),
        "multi_facility_control_promotion_pass": bool(
            _get(r7_readiness, "multi_facility_control_promotion_pass", False)
        ),
        "catalyst_proxy_field_validation_pass": bool(
            _get(r7_readiness, "catalyst_proxy_field_validation_pass", False)
        ),
        "minimum_common_batch_count": _get(coverage_readiness, "minimum_common_batch_count", 0),
        "minimum_valid_matched_batch_count": _get(coverage_readiness, "minimum_valid_matched_batch_count", 0),
        "minimum_valid_operation_action_count": _get(coverage_readiness, "minimum_valid_operation_action_count", 0),
        "minimum_invalid_operation_action_count": _get(coverage_readiness, "minimum_invalid_operation_action_count", 0),
        "minimum_valid_lab_result_count": _get(coverage_readiness, "minimum_valid_lab_result_count", 0),
        "minimum_invalid_lab_result_count": _get(coverage_readiness, "minimum_invalid_lab_result_count", 0),
        "minimum_proxy_event_count": _get(coverage_readiness, "minimum_proxy_event_count", 0),
        "minimum_valid_proxy_label_count": _get(coverage_readiness, "minimum_valid_proxy_label_count", 0),
        "minimum_invalid_proxy_label_count": _get(coverage_readiness, "minimum_invalid_proxy_label_count", 0),
        "minimum_pressure_headloss_event_count": _get(
            coverage_readiness,
            "minimum_pressure_headloss_event_count",
            0,
        ),
        "minimum_valid_pressure_headloss_event_count": _get(
            coverage_readiness,
            "minimum_valid_pressure_headloss_event_count",
            0,
        ),
        "minimum_invalid_pressure_headloss_event_count": _get(
            coverage_readiness,
            "minimum_invalid_pressure_headloss_event_count",
            0,
        ),
        "minimum_valid_pressure_headloss_batch_count": _get(
            coverage_readiness,
            "minimum_valid_pressure_headloss_batch_count",
            0,
        ),
        "minimum_time_order_violation_count": _get(coverage_readiness, "minimum_time_order_violation_count", 0),
        "coverage_patch_plan_status": _get(patch_plan, "patch_plan_status", "unknown"),
        "coverage_patch_plan_item_count": _get(patch_plan, "item_count", 0),
        "r7_status": _get(r7_readiness, "real_field_package_acceptance_status", "unknown"),
        "r7_score": _get(r7_readiness, "real_field_package_acceptance_score", 0.0),
        "r7_next_action": _get(r7_readiness, "next_recommended_core_action", "unknown"),
        "can_emit_protective_control_candidate": bool(
            _get(r7_readiness, "can_emit_protective_control_candidate", False)
        ),
        "can_emit_field_supported_claim_candidate": bool(
            _get(r7_readiness, "can_emit_field_supported_claim_candidate", False)
        ),
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }


def _get(mapping: Any, key: str, default: Any) -> Any:
    if isinstance(mapping, dict):
        return mapping.get(key, default)
    return default


def _field_path_endpoint_final_effluent_label_ready(preflight: dict[str, Any]) -> bool:
    return bool(_get(preflight, "can_route_to_field_layout_holdout", False))


def _field_package_submission_readiness(
    package_preflight: dict[str, Any],
    coverage: dict[str, Any],
    path_endpoint_preflight: dict[str, Any],
    r7_result: dict[str, Any],
    pipeline_readiness: dict[str, Any],
) -> dict[str, Any]:
    coverage_readiness = coverage.get("readiness", {})
    coverage_readiness = coverage_readiness if isinstance(coverage_readiness, dict) else {}
    coverage_patch_plan = coverage.get("patch_plan", {})
    coverage_patch_plan = coverage_patch_plan if isinstance(coverage_patch_plan, dict) else {}
    path_alignment_patch_plan = path_endpoint_preflight.get("alignment_patch_plan", {})
    path_alignment_patch_plan = path_alignment_patch_plan if isinstance(path_alignment_patch_plan, dict) else {}
    r7_readiness = r7_result.get("readiness", {})
    r7_readiness = r7_readiness if isinstance(r7_readiness, dict) else {}

    import_ready = bool(package_preflight.get("can_pass_to_timestamped_replay", False))
    smoke_ready = bool(coverage_readiness.get("field_evidence_smoke_pass", False))
    human_review_ready = bool(coverage_readiness.get("can_route_to_human_review_candidate", False))
    path_endpoint_ready = bool(path_endpoint_preflight.get("can_route_to_field_layout_holdout", False))
    path_endpoint_layout_ready = bool(
        pipeline_readiness.get("can_route_to_field_layout_holdout_with_path_labels", False)
    )
    no_write_boundary_pass = not bool(pipeline_readiness.get("can_write_to_actuator", False)) and not bool(
        pipeline_readiness.get("can_write_to_release_gate", False)
    )

    stage_checks = [
        _submission_stage(
            "R7A_IMPORT_PREFLIGHT",
            "import_preflight",
            str(package_preflight.get("status", "unknown")),
            import_ready,
            package_preflight.get("next_actions", []),
            "Required before any timestamped replay. Header-only or non-field packages stop here.",
        ),
        _submission_stage(
            "R7I_MINIMUM_REPLAY_CONTRACT",
            "minimum_replay_contract",
            str(coverage_readiness.get("minimum_replay_contract_status", "unknown")),
            bool(coverage_readiness.get("minimum_replay_contract_pass", False)),
            _coverage_patch_actions(coverage_patch_plan),
            "Required before Agent42 smoke replay and fast-proxy replay evidence.",
        ),
        _submission_stage(
            "R8U66_PATH_ENDPOINT_ALIGNMENT",
            "path_endpoint_alignment",
            str(path_endpoint_preflight.get("preflight_status", "unknown")),
            path_endpoint_ready,
            _path_endpoint_patch_actions(path_alignment_patch_plan),
            "Required before field layout holdout and final-effluent endpoint release evidence review.",
        ),
        _submission_stage(
            "R7_FIELD_EVIDENCE_SUFFICIENCY",
            "field_evidence_sufficiency",
            str(coverage_readiness.get("field_evidence_sufficiency_status", "unknown")),
            smoke_ready,
            coverage.get("next_actions", []),
            "Separates smoke replay readiness from calibration volume and human-review readiness.",
        ),
        _submission_stage(
            "R7_ACCEPTANCE",
            "r7_acceptance",
            str(r7_readiness.get("real_field_package_acceptance_status", "unknown")),
            bool(r7_readiness.get("can_emit_field_supported_claim_candidate", False)),
            [str(r7_readiness.get("next_recommended_core_action", "inspect_r7_acceptance_gate"))],
            "Field-supported claims remain blocked until all R7 acceptance stages pass.",
        ),
        _submission_stage(
            "NO_WRITE_BOUNDARY",
            "no_write_boundary",
            "no_write_boundary_pass" if no_write_boundary_pass else "no_write_boundary_violation",
            no_write_boundary_pass,
            ["Keep actuator and release-gate writeback disabled until replay, review and release validation pass."],
            "This pipeline is a validation gate and never authorizes actuator or release-gate writes.",
        ),
    ]
    blocking_stages = [stage for stage in stage_checks if not stage["pass"]]
    highest_priority_blocker = str(blocking_stages[0]["stage_id"]) if blocking_stages else "none"
    next_operator_action = _submission_next_operator_action(blocking_stages, human_review_ready)
    status = _submission_status(
        import_ready=import_ready,
        smoke_ready=smoke_ready,
        human_review_ready=human_review_ready,
        path_endpoint_ready=path_endpoint_ready,
        path_endpoint_layout_ready=path_endpoint_layout_ready,
        no_write_boundary_pass=no_write_boundary_pass,
    )
    repair_work_order = _submission_repair_work_order(
        blocking_stages=blocking_stages,
        coverage_patch_plan=coverage_patch_plan,
        path_alignment_patch_plan=path_alignment_patch_plan,
        path_endpoint_preflight=path_endpoint_preflight,
        status=status,
        highest_priority_blocker=highest_priority_blocker,
        next_operator_action=next_operator_action,
        import_ready=import_ready,
        smoke_ready=smoke_ready,
        path_endpoint_layout_ready=path_endpoint_layout_ready,
        human_review_ready=human_review_ready,
        no_write_boundary_pass=no_write_boundary_pass,
    )
    return {
        "gate_id": "R8u77_field_package_submission_readiness_gate",
        "submission_readiness_status": status,
        "highest_priority_blocker": highest_priority_blocker,
        "blocking_stage_count": len(blocking_stages),
        "stage_checks": stage_checks,
        "can_submit_to_agent42_smoke_replay": import_ready and smoke_ready,
        "can_route_to_path_endpoint_layout_holdout": path_endpoint_layout_ready,
        "can_route_to_human_review_candidate": human_review_ready,
        "can_emit_field_supported_claim_candidate": bool(
            r7_readiness.get("can_emit_field_supported_claim_candidate", False)
        ),
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "no_write_boundary_pass": no_write_boundary_pass,
        "path_endpoint_required_matched_batch_deficit": int(
            path_endpoint_preflight.get("required_matched_batch_deficit", 0) or 0
        ),
        "path_endpoint_alignment_patch_plan_status": path_alignment_patch_plan.get(
            "patch_plan_status",
            "not_available",
        ),
        "coverage_patch_plan_status": coverage_patch_plan.get("patch_plan_status", "unknown"),
        "next_operator_action": next_operator_action,
        "operator_action_queue": _submission_operator_action_queue(blocking_stages),
        "field_package_submission_repair_work_order": repair_work_order,
        "field_boundary": (
            "Submission readiness only prioritizes field package repair and routing. It does not create field "
            "evidence, does not upgrade claims, and cannot authorize actuator or release-gate writeback."
        ),
    }


def _submission_stage(
    stage_id: str,
    stage_type: str,
    status: str,
    passed: bool,
    actions: Any,
    boundary: str,
) -> dict[str, Any]:
    return {
        "stage_id": stage_id,
        "stage_type": stage_type,
        "status": status,
        "pass": bool(passed),
        "next_actions": [str(action) for action in _list_like(actions)[:5]],
        "boundary": boundary,
    }


def _coverage_patch_actions(patch_plan: dict[str, Any]) -> list[str]:
    items = patch_plan.get("items", [])
    actions: list[str] = []
    for item in _list_like(items)[:5]:
        if isinstance(item, dict):
            target = item.get("target_file") or item.get("target_table") or item.get("need_id") or "-"
            actions.append(f"{item.get('item_id', 'coverage_patch')}: {item.get('action', 'repair')} -> {target}")
        else:
            actions.append(str(item))
    if not actions and patch_plan.get("patch_plan_status"):
        actions.append(str(patch_plan.get("patch_plan_status")))
    return actions


def _path_endpoint_patch_actions(patch_plan: dict[str, Any]) -> list[str]:
    items = patch_plan.get("items", [])
    actions: list[str] = []
    for item in _list_like(items)[:5]:
        if isinstance(item, dict):
            actions.append(
                f"{item.get('item_id', 'path_endpoint_patch')}: "
                f"{item.get('action', 'repair')} -> {item.get('target_table', '-')}"
            )
        else:
            actions.append(str(item))
    if not actions and patch_plan.get("patch_plan_status"):
        actions.append(str(patch_plan.get("patch_plan_status")))
    return actions


def _submission_next_operator_action(blocking_stages: list[dict[str, Any]], human_review_ready: bool) -> str:
    if not blocking_stages:
        return "route_to_field_supported_claim_review_without_writeback"
    first = blocking_stages[0]
    stage_id = str(first.get("stage_id"))
    if stage_id == "R7A_IMPORT_PREFLIGHT":
        return "repair_metadata_headers_and_real_rows_before_agent42"
    if stage_id == "R7I_MINIMUM_REPLAY_CONTRACT":
        return "collect_minimum_same_batch_replay_rows"
    if stage_id == "R8U66_PATH_ENDPOINT_ALIGNMENT":
        return "collect_path_endpoint_same_batch_rows_for_layout_holdout"
    if stage_id == "R7_FIELD_EVIDENCE_SUFFICIENCY":
        return "increase_field_replay_or_calibration_evidence_volume"
    if stage_id == "R7_ACCEPTANCE" and human_review_ready:
        return "route_to_operator_review_candidate_keep_no_write"
    if stage_id == "NO_WRITE_BOUNDARY":
        return "restore_no_write_boundary_before_any_submission"
    return f"inspect_{stage_id.lower()}"


def _submission_operator_action_queue(blocking_stages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    queue: list[dict[str, Any]] = []
    for index, stage in enumerate(blocking_stages, start=1):
        actions = _list_like(stage.get("next_actions", []))
        queue.append(
            {
                "rank": index,
                "stage_id": stage.get("stage_id"),
                "status": stage.get("status"),
                "primary_action": actions[0] if actions else f"inspect_{stage.get('stage_id')}",
                "boundary": stage.get("boundary"),
            }
        )
    return queue


def _submission_repair_work_order(
    *,
    blocking_stages: list[dict[str, Any]],
    coverage_patch_plan: dict[str, Any],
    path_alignment_patch_plan: dict[str, Any],
    path_endpoint_preflight: dict[str, Any],
    status: str,
    highest_priority_blocker: str,
    next_operator_action: str,
    import_ready: bool,
    smoke_ready: bool,
    path_endpoint_layout_ready: bool,
    human_review_ready: bool,
    no_write_boundary_pass: bool,
) -> dict[str, Any]:
    repair_items = [
        *_repair_items_from_patch_plan(
            source_stage_id="R7I_MINIMUM_REPLAY_CONTRACT",
            source_plan_name="coverage_patch_plan",
            patch_plan=coverage_patch_plan,
        ),
        *_repair_items_from_patch_plan(
            source_stage_id="R8U66_PATH_ENDPOINT_ALIGNMENT",
            source_plan_name="field_path_endpoint_alignment_patch_plan",
            patch_plan=path_alignment_patch_plan,
        ),
    ]
    if not repair_items:
        repair_items = _repair_items_from_blocking_stages(blocking_stages)
    work_order_status = _submission_repair_work_order_status(highest_priority_blocker)
    return {
        "work_order_id": "R8u86_field_package_submission_repair_work_order",
        "work_order_status": work_order_status,
        "submission_readiness_status": status,
        "highest_priority_blocker": highest_priority_blocker,
        "next_operator_action": next_operator_action,
        "blocking_stage_count": len(blocking_stages),
        "repair_item_count": len(repair_items),
        "repair_items": repair_items,
        "submission_requirements": {
            "required_package_env_var": "REAL_FIELD_REPLAY_PACKAGE_DIR",
            "metadata_data_origin_must_equal": "field",
            "reject_header_only_template": True,
            "reject_synthetic_or_sample_rows_as_field_evidence": True,
            "minimum_same_batch_replay_batch_count": 3,
            "minimum_path_endpoint_matched_batch_count": int(
                path_endpoint_preflight.get("minimum_matched_batch_count", 5) or 5
            ),
            "required_path_endpoint_matched_batch_deficit": int(
                path_endpoint_preflight.get("required_matched_batch_deficit", 0) or 0
            ),
        },
        "routing_contract": {
            "can_submit_to_agent42_smoke_replay": bool(import_ready and smoke_ready),
            "can_route_to_path_endpoint_layout_holdout": bool(path_endpoint_layout_ready),
            "can_route_to_human_review_candidate": bool(human_review_ready),
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "no_write_boundary_pass": bool(no_write_boundary_pass),
        },
        "field_boundary": (
            "This work order converts blocking preflight and patch-plan facts into operator repair tasks only. "
            "It does not synthesize field rows, does not validate field performance, and does not authorize "
            "actuator or release-gate writeback."
        ),
    }


def _repair_items_from_patch_plan(
    *,
    source_stage_id: str,
    source_plan_name: str,
    patch_plan: dict[str, Any],
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for index, item in enumerate(_list_like(patch_plan.get("items", [])), start=1):
        if not isinstance(item, dict):
            items.append(
                {
                    "work_item_id": f"{source_stage_id}_PATCH_{index}",
                    "source_stage_id": source_stage_id,
                    "source_plan_name": source_plan_name,
                    "priority": "P1",
                    "target": "-",
                    "action": str(item),
                    "acceptance": "Rerun R7 package preflight after completing this operator action.",
                }
            )
            continue
        normalized = {
            "work_item_id": str(item.get("item_id", f"{source_stage_id}_PATCH_{index}")),
            "source_stage_id": source_stage_id,
            "source_plan_name": source_plan_name,
            "source_patch_stage": item.get("stage", "-"),
            "priority": str(item.get("priority", "P1")),
            "target": _repair_item_target(item),
            "action": str(item.get("action", "repair_field_package_rows")),
            "acceptance": str(
                item.get(
                    "acceptance",
                    item.get("minimum_evidence", item.get("why_required", "Rerun R7 preflight after patching.")),
                )
            ),
            "why_required": str(item.get("why_required", "Required before this package can advance through R7.")),
        }
        for key in (
            "fields_to_add",
            "fields_to_fill",
            "required_fields",
            "required_headers",
            "required_analytes",
            "required_patch_signals",
            "target_tables",
            "minimum_rows",
            "minimum_rows_hint",
            "minimum_matched_batch_count",
            "required_matched_batch_deficit",
            "minimum_valid_label_count",
            "minimum_valid_operation_action_count",
            "minimum_valid_lab_result_count",
            "minimum_valid_proxy_label_count",
            "minimum_valid_pressure_headloss_event_count",
            "current_valid_label_count",
            "current_valid_operation_action_count",
            "current_valid_lab_result_count",
            "current_valid_proxy_label_count",
            "current_valid_pressure_headloss_event_count",
            "missing_batch_ids_sample",
            "missing_batch_id_count",
            "pressure_source_conflict_count",
            "operator_review_required",
        ):
            if key in item and item.get(key) not in (None, "", [], {}):
                normalized[key] = item.get(key)
        items.append(normalized)
    return items


def _repair_item_target(item: dict[str, Any]) -> Any:
    for key in ("target_file", "target_table", "target_tables", "need_id"):
        value = item.get(key)
        if value not in (None, "", [], {}):
            return value
    return "-"


def _repair_items_from_blocking_stages(blocking_stages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for stage_index, stage in enumerate(blocking_stages, start=1):
        actions = _list_like(stage.get("next_actions", []))
        for action_index, action in enumerate(actions or [f"inspect_{stage.get('stage_id')}"], start=1):
            items.append(
                {
                    "work_item_id": f"{stage.get('stage_id', 'UNKNOWN_STAGE')}_ACTION_{action_index}",
                    "source_stage_id": stage.get("stage_id"),
                    "source_plan_name": "submission_stage_check",
                    "priority": "P1" if stage_index == 1 else "P2",
                    "target": stage.get("stage_type", "-"),
                    "action": str(action),
                    "acceptance": "Rerun the R7 real field replay pipeline after completing this action.",
                    "why_required": stage.get("boundary", "Required before package submission can advance."),
                }
            )
    return items


def _submission_repair_work_order_status(highest_priority_blocker: str) -> str:
    if highest_priority_blocker == "none":
        return "field_package_submission_repair_work_order_clear"
    if highest_priority_blocker == "R7A_IMPORT_PREFLIGHT":
        return "field_package_submission_repair_work_order_blocked_at_import_preflight"
    if highest_priority_blocker == "R7I_MINIMUM_REPLAY_CONTRACT":
        return "field_package_submission_repair_work_order_requires_minimum_replay_contract"
    if highest_priority_blocker == "R8U66_PATH_ENDPOINT_ALIGNMENT":
        return "field_package_submission_repair_work_order_requires_path_endpoint_alignment"
    if highest_priority_blocker == "R7_FIELD_EVIDENCE_SUFFICIENCY":
        return "field_package_submission_repair_work_order_requires_field_evidence_sufficiency"
    if highest_priority_blocker == "R7_ACCEPTANCE":
        return "field_package_submission_repair_work_order_requires_r7_acceptance_review"
    if highest_priority_blocker == "NO_WRITE_BOUNDARY":
        return "field_package_submission_repair_work_order_invalid_no_write_boundary_violation"
    return "field_package_submission_repair_work_order_requires_stage_inspection"


def build_field_package_submission_repair_response_template(work_order: dict[str, Any]) -> dict[str, Any]:
    repair_items = _list_like(work_order.get("repair_items", []))
    rows: list[dict[str, Any]] = []
    for item in repair_items:
        if not isinstance(item, dict):
            continue
        rows.append(
            {
                "work_item_id": str(item.get("work_item_id", "unknown_work_item")),
                "operator_status": "TODO_submitted_or_blocked_with_reason",
                "target": item.get("target", "-"),
                "source_stage_id": item.get("source_stage_id", "-"),
                "action": item.get("action", "repair_field_package_rows"),
                "evidence_artifact": "TODO_path_or_table_rows_added",
                "evidence_type": "TODO_metadata_or_csv_rows_or_review_record",
                "data_origin_assertion": "TODO_field",
                "batch_id_count": "TODO_integer_if_applicable",
                "reviewer_id": "TODO_operator_or_reviewer_id",
                "review_time": "TODO_review_time",
                "no_write_boundary_confirmed": "TODO_true",
                "operator_notes": "TODO_explain_repair_or_blocker",
                "template_only": True,
            }
        )
    return {
        "template_id": "R8u87_field_package_submission_repair_response_template",
        "linked_work_order_id": work_order.get("work_order_id", "unknown_work_order"),
        "linked_work_order_status": work_order.get("work_order_status", "unknown"),
        "required_work_item_count": len(rows),
        "accepted_operator_statuses": [
            "submitted",
            "submitted_for_r7_preflight",
            "blocked_with_reason",
            "not_applicable_with_reason",
        ],
        "repair_response_rows": rows,
        "operator_instructions": [
            "Replace every TODO value before submission.",
            "Use submitted/submitted_for_r7_preflight only when real field metadata, CSV rows, or review records have been supplied.",
            "Use blocked_with_reason when the item cannot be repaired yet; blocked rows do not route to R7 preflight.",
            "This response does not create field evidence; R7/Agent44 preflight must still inspect the package directory.",
        ],
        "field_boundary": (
            "This template is an operator response scaffold. It is template-only until all TODO/template markers are "
            "removed and it still cannot authorize actuator or release-gate writeback."
        ),
    }


def preflight_field_package_submission_repair_response(
    response: dict[str, Any],
    work_order: dict[str, Any],
) -> dict[str, Any]:
    required_ids = [
        str(item.get("work_item_id"))
        for item in _list_like(work_order.get("repair_items", []))
        if isinstance(item, dict) and item.get("work_item_id")
    ]
    required_id_set = set(required_ids)
    if not isinstance(response, dict):
        return _repair_response_preflight_payload(
            status="repair_response_preflight_invalid_root",
            required_ids=required_ids,
            rows=[],
            invalid_root=True,
        )
    rows = _list_like(response.get("repair_response_rows", []))
    return _repair_response_preflight_payload(
        status="",
        required_ids=required_ids,
        rows=rows,
        invalid_root=False,
        expected_work_order_id=str(work_order.get("work_order_id", "")),
        submitted_work_order_id=str(response.get("linked_work_order_id", "")),
        required_id_set=required_id_set,
    )


def _repair_response_preflight_payload(
    *,
    status: str,
    required_ids: list[str],
    rows: list[Any],
    invalid_root: bool,
    expected_work_order_id: str = "",
    submitted_work_order_id: str = "",
    required_id_set: set[str] | None = None,
) -> dict[str, Any]:
    if invalid_root:
        required_id_set = set(required_ids)
    else:
        required_id_set = required_id_set or set(required_ids)
    valid_rows = [row for row in rows if isinstance(row, dict)]
    invalid_row_count = len(rows) - len(valid_rows)
    response_ids = [str(row.get("work_item_id", "")) for row in valid_rows]
    missing_ids = [item_id for item_id in required_ids if item_id not in set(response_ids)]
    unexpected_ids = sorted({item_id for item_id in response_ids if item_id and item_id not in required_id_set})
    duplicate_ids = sorted({item_id for item_id in response_ids if item_id and response_ids.count(item_id) > 1})
    template_marker_rows = [
        row.get("work_item_id", f"row_{index}")
        for index, row in enumerate(valid_rows)
        if _repair_response_has_template_marker(row)
    ]
    submitted_rows = [row for row in valid_rows if str(row.get("operator_status", "")).strip() in {"submitted", "submitted_for_r7_preflight"}]
    blocked_rows = [
        row
        for row in valid_rows
        if str(row.get("operator_status", "")).strip()
        in {"blocked_with_reason", "not_applicable_with_reason"}
    ]
    accepted_statuses = {
        "submitted",
        "submitted_for_r7_preflight",
        "blocked_with_reason",
        "not_applicable_with_reason",
    }
    invalid_status_rows = [
        row.get("work_item_id", f"row_{index}")
        for index, row in enumerate(valid_rows)
        if str(row.get("operator_status", "")).strip() not in accepted_statuses
    ]
    submitted_missing_evidence = [
        row.get("work_item_id", f"row_{index}")
        for index, row in enumerate(submitted_rows)
        if _submitted_response_missing_evidence(row)
    ]
    work_order_mismatch = bool(expected_work_order_id and submitted_work_order_id and expected_work_order_id != submitted_work_order_id)
    if not status:
        status = _repair_response_preflight_status(
            invalid_row_count=invalid_row_count,
            work_order_mismatch=work_order_mismatch,
            template_marker_count=len(template_marker_rows),
            missing_response_item_count=len(missing_ids),
            unexpected_item_count=len(unexpected_ids),
            duplicate_item_count=len(duplicate_ids),
            invalid_status_count=len(invalid_status_rows),
            submitted_missing_evidence_count=len(submitted_missing_evidence),
            blocked_item_count=len(blocked_rows),
            submitted_item_count=len(submitted_rows),
            required_item_count=len(required_ids),
        )
    can_route = status == "repair_response_preflight_ready_for_r7_preflight"
    return {
        "preflight_id": "R8u87_field_package_submission_repair_response_preflight",
        "preflight_status": status,
        "linked_work_order_id": expected_work_order_id or submitted_work_order_id or "unknown",
        "required_work_item_count": len(required_ids),
        "response_row_count": len(valid_rows),
        "submitted_item_count": len(submitted_rows),
        "blocked_item_count": len(blocked_rows),
        "missing_response_item_count": len(missing_ids),
        "unexpected_item_count": len(unexpected_ids),
        "duplicate_item_count": len(duplicate_ids),
        "invalid_row_count": invalid_row_count,
        "invalid_status_count": len(invalid_status_rows),
        "template_marker_count": len(template_marker_rows),
        "submitted_missing_evidence_count": len(submitted_missing_evidence),
        "work_order_id_mismatch": work_order_mismatch,
        "missing_response_item_ids": missing_ids[:20],
        "unexpected_response_item_ids": unexpected_ids[:20],
        "duplicate_response_item_ids": duplicate_ids[:20],
        "invalid_status_item_ids": [str(item) for item in invalid_status_rows[:20]],
        "template_marker_item_ids": [str(item) for item in template_marker_rows[:20]],
        "submitted_missing_evidence_item_ids": [str(item) for item in submitted_missing_evidence[:20]],
        "can_route_to_r7_preflight": can_route,
        "next_operator_action": (
            "rerun_r7_field_package_preflight_with_repaired_package"
            if can_route
            else _repair_response_next_operator_action(status)
        ),
        "field_boundary": (
            "Repair response preflight only checks operator response completeness. Even when it is ready, "
            "R7/Agent44 must still inspect the real package rows before any field evidence, actuator policy or "
            "release-gate claim can be created."
        ),
    }


def _repair_response_preflight_status(
    *,
    invalid_row_count: int,
    work_order_mismatch: bool,
    template_marker_count: int,
    missing_response_item_count: int,
    unexpected_item_count: int,
    duplicate_item_count: int,
    invalid_status_count: int,
    submitted_missing_evidence_count: int,
    blocked_item_count: int,
    submitted_item_count: int,
    required_item_count: int,
) -> str:
    if invalid_row_count:
        return "repair_response_preflight_invalid_rows"
    if work_order_mismatch:
        return "repair_response_preflight_work_order_id_mismatch"
    if template_marker_count:
        return "repair_response_preflight_blocked_at_template_markers"
    if missing_response_item_count:
        return "repair_response_preflight_missing_required_work_items"
    if unexpected_item_count or duplicate_item_count:
        return "repair_response_preflight_item_identity_gaps"
    if invalid_status_count:
        return "repair_response_preflight_invalid_operator_status"
    if submitted_missing_evidence_count:
        return "repair_response_preflight_submitted_items_missing_evidence"
    if blocked_item_count:
        return "repair_response_preflight_has_operator_blockers"
    if submitted_item_count < required_item_count:
        return "repair_response_preflight_incomplete_submission"
    return "repair_response_preflight_ready_for_r7_preflight"


def _repair_response_next_operator_action(status: str) -> str:
    mapping = {
        "repair_response_preflight_invalid_root": "resubmit_repair_response_as_json_object",
        "repair_response_preflight_invalid_rows": "repair_response_rows_as_objects",
        "repair_response_preflight_work_order_id_mismatch": "resubmit_response_for_current_r7_work_order",
        "repair_response_preflight_blocked_at_template_markers": "replace_todo_template_markers_before_submission",
        "repair_response_preflight_missing_required_work_items": "respond_to_every_repair_work_item",
        "repair_response_preflight_item_identity_gaps": "repair_duplicate_or_unknown_work_item_ids",
        "repair_response_preflight_invalid_operator_status": "use_allowed_operator_status_values",
        "repair_response_preflight_submitted_items_missing_evidence": "attach_evidence_artifact_reviewer_and_field_assertions",
        "repair_response_preflight_has_operator_blockers": "resolve_blocked_repair_items_before_r7_preflight",
        "repair_response_preflight_incomplete_submission": "submit_all_required_repair_items",
    }
    return mapping.get(status, "inspect_repair_response_preflight")


def _repair_response_has_template_marker(row: dict[str, Any]) -> bool:
    if bool(row.get("template_only", False)):
        return True
    for value in row.values():
        text = str(value).lower()
        if text.startswith("todo") or "todo_" in text or "template" in text or "sample_not_" in text:
            return True
    return False


def _submitted_response_missing_evidence(row: dict[str, Any]) -> bool:
    evidence_artifact = str(row.get("evidence_artifact", "")).strip()
    reviewer_id = str(row.get("reviewer_id", "")).strip()
    data_origin = str(row.get("data_origin_assertion", "")).strip().lower()
    no_write = str(row.get("no_write_boundary_confirmed", "")).strip().lower()
    return (
        not evidence_artifact
        or not reviewer_id
        or data_origin != "field"
        or no_write not in {"true", "1", "yes", "y", "confirmed"}
    )


def _submission_status(
    *,
    import_ready: bool,
    smoke_ready: bool,
    human_review_ready: bool,
    path_endpoint_ready: bool,
    path_endpoint_layout_ready: bool,
    no_write_boundary_pass: bool,
) -> str:
    if not no_write_boundary_pass:
        return "field_package_submission_invalid_no_write_boundary_violation"
    if not import_ready:
        return "field_package_submission_blocked_at_import_preflight"
    if not smoke_ready:
        if not path_endpoint_ready:
            return "field_package_submission_import_ready_needs_replay_and_path_endpoint_alignment"
        return "field_package_submission_import_ready_needs_replay_evidence"
    if not path_endpoint_ready:
        return "field_package_submission_smoke_ready_needs_path_endpoint_alignment_for_layout_holdout"
    if not path_endpoint_layout_ready:
        return "field_package_submission_path_endpoint_ready_needs_claim_or_holdout_gates"
    if human_review_ready:
        return "field_package_submission_ready_for_human_review_candidate_no_write"
    return "field_package_submission_ready_for_field_layout_holdout_candidate_no_write"


def _list_like(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []
