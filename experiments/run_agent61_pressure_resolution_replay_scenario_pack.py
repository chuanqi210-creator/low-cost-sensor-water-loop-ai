from __future__ import annotations

import csv
import json
import os
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from water_ai.agents.field_replay_import_agent import field_replay_package_template_spec
from water_ai.agents.pressure_resolution_replay_scenario_pack_agent import (
    REQUIRED_TABLE_FIELDS,
    PressureResolutionReplayScenarioPackAgent,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
R7_METRICS_PATH = PROJECT_ROOT / "outputs" / "r7_real_field_replay_pipeline" / "r7_real_field_replay_pipeline_metrics.json"
CATALYST_PROXY_METRICS_PATH = PROJECT_ROOT / "outputs" / "catalyst_activity_proxy" / "catalyst_activity_proxy_metrics.json"
COLLABORATIVE_CONTROL_METRICS_PATH = (
    PROJECT_ROOT / "outputs" / "multi_facility_collaborative_control" / "collaborative_control_metrics.json"
)
REPLAY_EVALUATION_METRICS_PATH = (
    PROJECT_ROOT / "outputs" / "multi_facility_replay_evaluation" / "replay_evaluation_metrics.json"
)
OUT_DIR = PROJECT_ROOT / "outputs" / "agent61_pressure_resolution_replay_scenario_pack"
METRICS_DIR = PROJECT_ROOT / "outputs" / "pressure_resolution_replay_scenario_pack"
DELIVERABLE_PATH = PROJECT_ROOT / "deliverables" / "model_core_optimization" / "pressure_resolution_replay_scenario_pack.md"
METRICS_PATH = METRICS_DIR / "pressure_resolution_replay_scenario_pack_metrics.json"
DEFAULT_FIELD_ROWS_PATH = METRICS_DIR / "pressure_resolution_replay_rows.json"
TEMPLATE_ROWS_PATH = METRICS_DIR / "pressure_resolution_replay_rows_template.json"
ROWS_CSV_TEMPLATE_DIR = METRICS_DIR / "pressure_resolution_replay_rows_csv_template"
ROWS_R7_ALIGNMENT_PATH = METRICS_DIR / "pressure_resolution_replay_rows_r7_alignment.json"
ROWS_R7_STAGING_PREFLIGHT_PATH = METRICS_DIR / "pressure_resolution_replay_rows_r7_staging_preflight.json"
ROWS_R7_STAGED_DRAFT_PATH = METRICS_DIR / "pressure_resolution_replay_rows_r7_staged_draft.json"
ROWS_R7_COMPLETION_PLAN_PATH = METRICS_DIR / "pressure_resolution_replay_rows_r7_completion_plan.json"
ROWS_R7_COMPLETION_ROUTE_CONTRACTS_PATH = (
    METRICS_DIR / "pressure_resolution_replay_rows_r7_completion_route_contracts.json"
)
ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGES_PATH = (
    METRICS_DIR / "pressure_resolution_replay_rows_r7_completion_route_work_packages.json"
)
ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_TEMPLATE_DIR = (
    METRICS_DIR / "pressure_resolution_replay_rows_r7_completion_route_work_package_templates"
)
ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_PREFLIGHT_PATH = (
    METRICS_DIR / "pressure_resolution_replay_rows_r7_completion_route_work_package_preflight.json"
)
ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_PATCH_PLAN_PATH = (
    METRICS_DIR / "pressure_resolution_replay_rows_r7_completion_route_work_package_patch_plan.json"
)
ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_ASSEMBLY_GATE_PATH = (
    METRICS_DIR / "pressure_resolution_replay_rows_r7_completion_route_work_package_assembly_gate.json"
)
ROWS_SCHEMA_PATH = METRICS_DIR / "pressure_resolution_replay_rows_schema.json"
ROWS_COLLECTION_CHECKLIST_PATH = METRICS_DIR / "pressure_resolution_replay_rows_collection_checklist.json"
ROWS_BATCH_BUNDLE_PREFLIGHT_PATH = METRICS_DIR / "pressure_resolution_replay_rows_batch_bundle_preflight.json"
ROWS_TEMPORAL_WINDOW_PREFLIGHT_PATH = METRICS_DIR / "pressure_resolution_replay_rows_temporal_window_preflight.json"
ROWS_SCENARIO_SEMANTIC_PREFLIGHT_PATH = METRICS_DIR / "pressure_resolution_replay_rows_scenario_semantic_preflight.json"
ROWS_DOWNSTREAM_ROUTING_PREFLIGHT_PATH = METRICS_DIR / "pressure_resolution_replay_rows_downstream_routing_preflight.json"
ROWS_DOWNSTREAM_ROUTE_HANDOFF_PATH = METRICS_DIR / "pressure_resolution_replay_rows_downstream_route_handoff.json"
ROWS_DOWNSTREAM_TARGET_GATE_PREFLIGHT_PATH = (
    METRICS_DIR / "pressure_resolution_replay_rows_downstream_target_gate_preflight.json"
)
ROWS_DOWNSTREAM_TARGET_GATE_RESULT_INTAKE_SCHEMA_PATH = (
    METRICS_DIR / "pressure_resolution_replay_rows_downstream_target_gate_result_intake_schema.json"
)
ROWS_DOWNSTREAM_TARGET_GATE_RESULT_PREFLIGHT_PATH = (
    METRICS_DIR / "pressure_resolution_replay_rows_downstream_target_gate_result_preflight.json"
)
ROWS_DOWNSTREAM_TARGET_GATE_RESULT_ARBITRATION_PATH = (
    METRICS_DIR / "pressure_resolution_replay_rows_downstream_target_gate_result_arbitration.json"
)
ROWS_DOWNSTREAM_TARGET_GATE_OPERATOR_REVIEW_TEMPLATE_PATH = (
    METRICS_DIR / "pressure_resolution_replay_rows_downstream_target_gate_operator_review_template.json"
)
ROWS_DOWNSTREAM_TARGET_GATE_OPERATOR_REVIEW_PREFLIGHT_PATH = (
    METRICS_DIR / "pressure_resolution_replay_rows_downstream_target_gate_operator_review_preflight.json"
)
ROWS_DOWNSTREAM_TARGET_GATE_POST_REVIEW_GATE_PATH = (
    METRICS_DIR / "pressure_resolution_replay_rows_downstream_target_gate_post_review_gate.json"
)
ROWS_DOWNSTREAM_TARGET_GATE_PROTECTIVE_CANDIDATE_EVALUATION_PATH = (
    METRICS_DIR / "pressure_resolution_replay_rows_downstream_target_gate_protective_candidate_evaluation.json"
)
ROWS_SUBMISSION_READINESS_REVIEW_PATH = (
    METRICS_DIR / "pressure_resolution_replay_rows_submission_readiness_review.json"
)
ROWS_SOURCE_PACKAGE_SUBMISSION_ROUTE_GUIDE_PATH = (
    METRICS_DIR / "pressure_resolution_replay_rows_source_package_submission_route_guide.json"
)
ROWS_SOURCE_PACKAGE_ROUTE_PREFLIGHT_PATH = (
    METRICS_DIR / "pressure_resolution_replay_rows_source_package_route_preflight.json"
)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLE_PATH.parent.mkdir(parents=True, exist_ok=True)

    field_rows_path = _field_rows_path()
    field_rows_by_table, field_rows_source = _read_field_rows_package(field_rows_path)
    report = PressureResolutionReplayScenarioPackAgent(
        r7_pipeline_metrics=_read_optional_json(R7_METRICS_PATH),
        catalyst_proxy_metrics=_read_optional_json(CATALYST_PROXY_METRICS_PATH),
        collaborative_control_metrics=_read_optional_json(COLLABORATIVE_CONTROL_METRICS_PATH),
        replay_evaluation_metrics=_read_optional_json(REPLAY_EVALUATION_METRICS_PATH),
        field_replay_rows_by_table=field_rows_by_table,
    ).run([])

    field_rows_package_schema = _field_rows_package_schema()
    field_rows_schema_validation = _field_rows_schema_validation(
        field_rows_source,
        field_rows_by_table,
        field_rows_package_schema,
    )
    field_rows_batch_bundle_preflight = _field_rows_batch_bundle_preflight(
        report,
        field_rows_source,
        field_rows_by_table,
        field_rows_package_schema,
        field_rows_schema_validation,
    )
    field_rows_temporal_window_preflight = _field_rows_temporal_window_preflight(
        report,
        field_rows_source,
        field_rows_by_table,
        field_rows_schema_validation,
        field_rows_batch_bundle_preflight,
    )
    field_rows_scenario_semantic_preflight = _field_rows_scenario_semantic_preflight(
        report,
        field_rows_source,
        field_rows_by_table,
        field_rows_schema_validation,
        field_rows_batch_bundle_preflight,
        field_rows_temporal_window_preflight,
    )
    field_rows_downstream_routing_preflight = _field_rows_downstream_routing_preflight(
        report,
        field_rows_source,
        field_rows_schema_validation,
        field_rows_batch_bundle_preflight,
        field_rows_temporal_window_preflight,
        field_rows_scenario_semantic_preflight,
    )
    field_rows_downstream_route_handoff = _field_rows_downstream_route_handoff(
        field_rows_downstream_routing_preflight
    )
    field_rows_downstream_target_gate_preflight = _field_rows_downstream_target_gate_preflight(
        field_rows_downstream_route_handoff
    )
    field_rows_downstream_target_gate_result_intake_schema = (
        _field_rows_downstream_target_gate_result_intake_schema(
            field_rows_downstream_target_gate_preflight
        )
    )
    field_rows_downstream_target_gate_result_preflight = (
        _field_rows_downstream_target_gate_result_preflight(
            field_rows_downstream_target_gate_preflight,
            field_rows_downstream_target_gate_result_intake_schema,
            _r8v_target_gate_result_package_path(),
        )
    )
    field_rows_downstream_target_gate_result_arbitration = (
        _field_rows_downstream_target_gate_result_arbitration(
            field_rows_downstream_target_gate_result_preflight
        )
    )
    field_rows_downstream_target_gate_operator_review_template = (
        _field_rows_downstream_target_gate_operator_review_template(
            field_rows_downstream_target_gate_result_arbitration
        )
    )
    field_rows_downstream_target_gate_operator_review_preflight = (
        _field_rows_downstream_target_gate_operator_review_preflight(
            field_rows_downstream_target_gate_result_arbitration,
            field_rows_downstream_target_gate_operator_review_template,
            _r8v_target_gate_operator_review_path(),
        )
    )
    field_rows_downstream_target_gate_post_review_gate = (
        _field_rows_downstream_target_gate_post_review_gate(
            field_rows_downstream_target_gate_operator_review_preflight
        )
    )
    field_rows_downstream_target_gate_protective_candidate_evaluation = (
        _field_rows_downstream_target_gate_protective_candidate_evaluation(
            field_rows_downstream_target_gate_post_review_gate
        )
    )
    field_rows_patch_plan = _field_rows_patch_plan(
        report,
        field_rows_source,
        field_rows_schema_validation,
        field_rows_batch_bundle_preflight,
        field_rows_temporal_window_preflight,
        field_rows_scenario_semantic_preflight,
    )
    field_rows_collection_checklist = _field_rows_collection_checklist(
        report,
        field_rows_source,
        field_rows_patch_plan,
        field_rows_package_schema,
        field_rows_schema_validation,
        field_rows_batch_bundle_preflight,
        field_rows_temporal_window_preflight,
        field_rows_scenario_semantic_preflight,
    )
    field_rows_operator_handoff = _field_rows_operator_handoff(
        report,
        field_rows_source,
        field_rows_patch_plan,
        field_rows_package_schema,
        field_rows_schema_validation,
        field_rows_collection_checklist,
        field_rows_batch_bundle_preflight,
        field_rows_temporal_window_preflight,
        field_rows_scenario_semantic_preflight,
        field_rows_downstream_routing_preflight,
    )
    field_rows_csv_template = _write_field_rows_csv_template(
        ROWS_CSV_TEMPLATE_DIR,
        report.metrics["template_rows_by_table"],
    )
    field_rows_r7_alignment = _field_rows_r7_alignment(field_rows_package_schema)
    field_rows_r7_staging_preflight = _field_rows_r7_staging_preflight(
        _r7_field_package_path(),
        field_rows_r7_alignment,
        field_rows_package_schema,
    )
    field_rows_r7_completion_plan = _field_rows_r7_completion_plan(
        field_rows_r7_staging_preflight,
        field_rows_r7_alignment,
    )
    field_rows_r7_completion_route_contracts = _field_rows_r7_completion_route_contracts(
        field_rows_r7_completion_plan
    )
    field_rows_r7_completion_route_work_packages = _field_rows_r7_completion_route_work_packages(
        field_rows_r7_completion_route_contracts
    )
    field_rows_r7_completion_route_work_package_templates = (
        _write_r7_completion_route_work_package_templates(
            field_rows_r7_completion_route_work_packages,
            ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_TEMPLATE_DIR,
        )
    )
    field_rows_r7_completion_route_work_package_preflight = (
        _field_rows_r7_completion_route_work_package_submission_preflight(
            field_rows_r7_completion_route_work_packages,
            _r7_completion_route_work_package_submission_path(),
        )
    )
    field_rows_r7_completion_route_work_package_patch_plan = (
        _field_rows_r7_completion_route_work_package_patch_plan(
            field_rows_r7_completion_route_work_package_preflight
        )
    )
    field_rows_r7_completion_route_work_package_assembly_gate = (
        _field_rows_r7_completion_route_work_package_assembly_gate(
            field_rows_r7_completion_route_work_package_preflight,
            field_rows_r7_completion_route_work_package_patch_plan,
        )
    )
    field_rows_submission_readiness_review = _field_rows_submission_readiness_review(
        report,
        field_rows_source,
        field_rows_schema_validation,
        field_rows_batch_bundle_preflight,
        field_rows_temporal_window_preflight,
        field_rows_scenario_semantic_preflight,
        field_rows_downstream_routing_preflight,
        field_rows_patch_plan,
        field_rows_collection_checklist,
        field_rows_operator_handoff,
        field_rows_r7_completion_plan,
        field_rows_r7_completion_route_work_package_patch_plan,
        field_rows_r7_completion_route_work_package_assembly_gate,
    )
    field_rows_source_package_submission_route_guide = _field_rows_source_package_submission_route_guide(
        report,
        field_rows_source,
        field_rows_package_schema,
        field_rows_patch_plan,
        field_rows_operator_handoff,
        field_rows_submission_readiness_review,
        field_rows_r7_completion_plan,
        field_rows_r7_completion_route_contracts,
        field_rows_r7_completion_route_work_packages,
        field_rows_r7_completion_route_work_package_patch_plan,
    )
    field_rows_source_package_route_preflight = _field_rows_source_package_route_preflight(
        field_rows_source,
        field_rows_source_package_submission_route_guide,
        field_rows_r7_completion_route_work_package_preflight,
        field_rows_r7_completion_route_work_package_assembly_gate,
    )
    metrics_payload = {
        "method_contract": report.metrics["method_contract"],
        "source_snapshot": report.metrics["source_snapshot"],
        "required_table_field_matrix": report.metrics["required_table_field_matrix"],
        "pressure_resolution_replay_scenario_matrix": report.metrics[
            "pressure_resolution_replay_scenario_matrix"
        ],
        "row_collection_plan": report.metrics["row_collection_plan"],
        "template_rows_by_table": report.metrics["template_rows_by_table"],
        "field_rows_csv_template": field_rows_csv_template,
        "field_rows_r7_alignment": field_rows_r7_alignment,
        "field_rows_r7_staging_preflight": field_rows_r7_staging_preflight,
        "field_rows_r7_completion_plan": field_rows_r7_completion_plan,
        "field_rows_r7_completion_route_contracts": field_rows_r7_completion_route_contracts,
        "field_rows_r7_completion_route_work_packages": field_rows_r7_completion_route_work_packages,
        "field_rows_r7_completion_route_work_package_templates": (
            field_rows_r7_completion_route_work_package_templates
        ),
        "field_rows_r7_completion_route_work_package_preflight": (
            field_rows_r7_completion_route_work_package_preflight
        ),
        "field_rows_r7_completion_route_work_package_patch_plan": (
            field_rows_r7_completion_route_work_package_patch_plan
        ),
        "field_rows_r7_completion_route_work_package_assembly_gate": (
            field_rows_r7_completion_route_work_package_assembly_gate
        ),
        "field_rows_submission_readiness_review": field_rows_submission_readiness_review,
        "field_rows_source_package_submission_route_guide": (
            field_rows_source_package_submission_route_guide
        ),
        "field_rows_source_package_route_preflight": field_rows_source_package_route_preflight,
        "field_rows_source": field_rows_source,
        "field_row_acceptance": report.metrics["field_row_acceptance"],
        "field_rows_package_schema": field_rows_package_schema,
        "field_rows_schema_validation": field_rows_schema_validation,
        "field_rows_batch_bundle_preflight": field_rows_batch_bundle_preflight,
        "field_rows_temporal_window_preflight": field_rows_temporal_window_preflight,
        "field_rows_scenario_semantic_preflight": field_rows_scenario_semantic_preflight,
        "field_rows_downstream_routing_preflight": field_rows_downstream_routing_preflight,
        "field_rows_downstream_route_handoff": field_rows_downstream_route_handoff,
        "field_rows_downstream_target_gate_preflight": field_rows_downstream_target_gate_preflight,
        "field_rows_downstream_target_gate_result_intake_schema": (
            field_rows_downstream_target_gate_result_intake_schema
        ),
        "field_rows_downstream_target_gate_result_preflight": (
            field_rows_downstream_target_gate_result_preflight
        ),
        "field_rows_downstream_target_gate_result_arbitration": (
            field_rows_downstream_target_gate_result_arbitration
        ),
        "field_rows_downstream_target_gate_operator_review_template": (
            field_rows_downstream_target_gate_operator_review_template
        ),
        "field_rows_downstream_target_gate_operator_review_preflight": (
            field_rows_downstream_target_gate_operator_review_preflight
        ),
        "field_rows_downstream_target_gate_post_review_gate": (
            field_rows_downstream_target_gate_post_review_gate
        ),
        "field_rows_downstream_target_gate_protective_candidate_evaluation": (
            field_rows_downstream_target_gate_protective_candidate_evaluation
        ),
        "field_rows_patch_plan": field_rows_patch_plan,
        "field_rows_collection_checklist": field_rows_collection_checklist,
        "field_rows_operator_handoff": field_rows_operator_handoff,
        "row_collection_readiness": report.metrics["row_collection_readiness"],
        "readiness": report.metrics["readiness"],
        "agent60_writeback": report.metrics["agent60_writeback"],
    }
    METRICS_PATH.write_text(json.dumps(metrics_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    TEMPLATE_ROWS_PATH.write_text(
        json.dumps(report.metrics["template_rows_by_table"], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    ROWS_SCHEMA_PATH.write_text(json.dumps(field_rows_package_schema, ensure_ascii=False, indent=2), encoding="utf-8")
    ROWS_R7_ALIGNMENT_PATH.write_text(
        json.dumps(field_rows_r7_alignment, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    ROWS_R7_STAGING_PREFLIGHT_PATH.write_text(
        json.dumps(field_rows_r7_staging_preflight, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    ROWS_R7_STAGED_DRAFT_PATH.write_text(
        json.dumps(
            field_rows_r7_staging_preflight["staged_draft_rows_by_table"],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    ROWS_R7_COMPLETION_PLAN_PATH.write_text(
        json.dumps(field_rows_r7_completion_plan, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    ROWS_R7_COMPLETION_ROUTE_CONTRACTS_PATH.write_text(
        json.dumps(field_rows_r7_completion_route_contracts, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGES_PATH.write_text(
        json.dumps(field_rows_r7_completion_route_work_packages, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_PREFLIGHT_PATH.write_text(
        json.dumps(field_rows_r7_completion_route_work_package_preflight, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_PATCH_PLAN_PATH.write_text(
        json.dumps(field_rows_r7_completion_route_work_package_patch_plan, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_ASSEMBLY_GATE_PATH.write_text(
        json.dumps(field_rows_r7_completion_route_work_package_assembly_gate, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    ROWS_COLLECTION_CHECKLIST_PATH.write_text(
        json.dumps(field_rows_collection_checklist, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    ROWS_BATCH_BUNDLE_PREFLIGHT_PATH.write_text(
        json.dumps(field_rows_batch_bundle_preflight, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    ROWS_TEMPORAL_WINDOW_PREFLIGHT_PATH.write_text(
        json.dumps(field_rows_temporal_window_preflight, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    ROWS_SCENARIO_SEMANTIC_PREFLIGHT_PATH.write_text(
        json.dumps(field_rows_scenario_semantic_preflight, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    ROWS_DOWNSTREAM_ROUTING_PREFLIGHT_PATH.write_text(
        json.dumps(field_rows_downstream_routing_preflight, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    ROWS_DOWNSTREAM_ROUTE_HANDOFF_PATH.write_text(
        json.dumps(field_rows_downstream_route_handoff, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    ROWS_DOWNSTREAM_TARGET_GATE_PREFLIGHT_PATH.write_text(
        json.dumps(field_rows_downstream_target_gate_preflight, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    ROWS_DOWNSTREAM_TARGET_GATE_RESULT_INTAKE_SCHEMA_PATH.write_text(
        json.dumps(
            field_rows_downstream_target_gate_result_intake_schema,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    ROWS_DOWNSTREAM_TARGET_GATE_RESULT_PREFLIGHT_PATH.write_text(
        json.dumps(
            field_rows_downstream_target_gate_result_preflight,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    ROWS_DOWNSTREAM_TARGET_GATE_RESULT_ARBITRATION_PATH.write_text(
        json.dumps(
            field_rows_downstream_target_gate_result_arbitration,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    ROWS_DOWNSTREAM_TARGET_GATE_OPERATOR_REVIEW_TEMPLATE_PATH.write_text(
        json.dumps(
            field_rows_downstream_target_gate_operator_review_template,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    ROWS_DOWNSTREAM_TARGET_GATE_OPERATOR_REVIEW_PREFLIGHT_PATH.write_text(
        json.dumps(
            field_rows_downstream_target_gate_operator_review_preflight,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    ROWS_DOWNSTREAM_TARGET_GATE_POST_REVIEW_GATE_PATH.write_text(
        json.dumps(
            field_rows_downstream_target_gate_post_review_gate,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    ROWS_DOWNSTREAM_TARGET_GATE_PROTECTIVE_CANDIDATE_EVALUATION_PATH.write_text(
        json.dumps(
            field_rows_downstream_target_gate_protective_candidate_evaluation,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    ROWS_SUBMISSION_READINESS_REVIEW_PATH.write_text(
        json.dumps(field_rows_submission_readiness_review, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    ROWS_SOURCE_PACKAGE_SUBMISSION_ROUTE_GUIDE_PATH.write_text(
        json.dumps(field_rows_source_package_submission_route_guide, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    ROWS_SOURCE_PACKAGE_ROUTE_PREFLIGHT_PATH.write_text(
        json.dumps(field_rows_source_package_route_preflight, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    DELIVERABLE_PATH.write_text(
        _deliverable_md(
            report,
            field_rows_source,
            field_rows_schema_validation,
            field_rows_collection_checklist,
            field_rows_batch_bundle_preflight,
            field_rows_temporal_window_preflight,
            field_rows_scenario_semantic_preflight,
            field_rows_downstream_routing_preflight,
            field_rows_downstream_route_handoff,
            field_rows_downstream_target_gate_preflight,
            field_rows_downstream_target_gate_result_intake_schema,
            field_rows_downstream_target_gate_result_preflight,
            field_rows_downstream_target_gate_result_arbitration,
            field_rows_downstream_target_gate_operator_review_template,
            field_rows_downstream_target_gate_operator_review_preflight,
            field_rows_downstream_target_gate_post_review_gate,
            field_rows_downstream_target_gate_protective_candidate_evaluation,
            field_rows_r7_staging_preflight,
            field_rows_r7_completion_plan,
            field_rows_r7_completion_route_contracts,
            field_rows_r7_completion_route_work_packages,
            field_rows_r7_completion_route_work_package_templates,
            field_rows_r7_completion_route_work_package_preflight,
            field_rows_r7_completion_route_work_package_patch_plan,
            field_rows_r7_completion_route_work_package_assembly_gate,
            field_rows_submission_readiness_review,
            field_rows_source_package_submission_route_guide,
            field_rows_source_package_route_preflight,
        ),
        encoding="utf-8",
    )
    generated_files = {
        "pressure_resolution_replay_scenario_pack": str(DELIVERABLE_PATH),
        "agent61_report": str(OUT_DIR / "agent61_report.md"),
        "pressure_resolution_replay_scenario_pack_metrics": str(METRICS_PATH),
        "pressure_resolution_replay_rows_template": str(TEMPLATE_ROWS_PATH),
        "pressure_resolution_replay_rows_csv_template": str(ROWS_CSV_TEMPLATE_DIR),
        "pressure_resolution_replay_rows_r7_alignment": str(ROWS_R7_ALIGNMENT_PATH),
        "pressure_resolution_replay_rows_r7_staging_preflight": str(ROWS_R7_STAGING_PREFLIGHT_PATH),
        "pressure_resolution_replay_rows_r7_staged_draft": str(ROWS_R7_STAGED_DRAFT_PATH),
        "pressure_resolution_replay_rows_r7_completion_plan": str(ROWS_R7_COMPLETION_PLAN_PATH),
        "pressure_resolution_replay_rows_r7_completion_route_contracts": str(
            ROWS_R7_COMPLETION_ROUTE_CONTRACTS_PATH
        ),
        "pressure_resolution_replay_rows_r7_completion_route_work_packages": str(
            ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGES_PATH
        ),
        "pressure_resolution_replay_rows_r7_completion_route_work_package_templates": str(
            ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_TEMPLATE_DIR
        ),
        "pressure_resolution_replay_rows_r7_completion_route_work_package_preflight": str(
            ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_PREFLIGHT_PATH
        ),
        "pressure_resolution_replay_rows_r7_completion_route_work_package_patch_plan": str(
            ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_PATCH_PLAN_PATH
        ),
        "pressure_resolution_replay_rows_r7_completion_route_work_package_assembly_gate": str(
            ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_ASSEMBLY_GATE_PATH
        ),
        "pressure_resolution_replay_rows_schema": str(ROWS_SCHEMA_PATH),
        "pressure_resolution_replay_rows_collection_checklist": str(ROWS_COLLECTION_CHECKLIST_PATH),
        "pressure_resolution_replay_rows_batch_bundle_preflight": str(ROWS_BATCH_BUNDLE_PREFLIGHT_PATH),
        "pressure_resolution_replay_rows_temporal_window_preflight": str(ROWS_TEMPORAL_WINDOW_PREFLIGHT_PATH),
        "pressure_resolution_replay_rows_scenario_semantic_preflight": str(ROWS_SCENARIO_SEMANTIC_PREFLIGHT_PATH),
        "pressure_resolution_replay_rows_downstream_routing_preflight": str(ROWS_DOWNSTREAM_ROUTING_PREFLIGHT_PATH),
        "pressure_resolution_replay_rows_downstream_route_handoff": str(ROWS_DOWNSTREAM_ROUTE_HANDOFF_PATH),
        "pressure_resolution_replay_rows_downstream_target_gate_preflight": str(
            ROWS_DOWNSTREAM_TARGET_GATE_PREFLIGHT_PATH
        ),
        "pressure_resolution_replay_rows_downstream_target_gate_result_intake_schema": str(
            ROWS_DOWNSTREAM_TARGET_GATE_RESULT_INTAKE_SCHEMA_PATH
        ),
        "pressure_resolution_replay_rows_downstream_target_gate_result_preflight": str(
            ROWS_DOWNSTREAM_TARGET_GATE_RESULT_PREFLIGHT_PATH
        ),
        "pressure_resolution_replay_rows_downstream_target_gate_result_arbitration": str(
            ROWS_DOWNSTREAM_TARGET_GATE_RESULT_ARBITRATION_PATH
        ),
        "pressure_resolution_replay_rows_downstream_target_gate_operator_review_template": str(
            ROWS_DOWNSTREAM_TARGET_GATE_OPERATOR_REVIEW_TEMPLATE_PATH
        ),
        "pressure_resolution_replay_rows_downstream_target_gate_operator_review_preflight": str(
            ROWS_DOWNSTREAM_TARGET_GATE_OPERATOR_REVIEW_PREFLIGHT_PATH
        ),
        "pressure_resolution_replay_rows_downstream_target_gate_post_review_gate": str(
            ROWS_DOWNSTREAM_TARGET_GATE_POST_REVIEW_GATE_PATH
        ),
        "pressure_resolution_replay_rows_downstream_target_gate_protective_candidate_evaluation": str(
            ROWS_DOWNSTREAM_TARGET_GATE_PROTECTIVE_CANDIDATE_EVALUATION_PATH
        ),
        "pressure_resolution_replay_rows_submission_readiness_review": str(
            ROWS_SUBMISSION_READINESS_REVIEW_PATH
        ),
        "pressure_resolution_replay_rows_source_package_submission_route_guide": str(
            ROWS_SOURCE_PACKAGE_SUBMISSION_ROUTE_GUIDE_PATH
        ),
        "pressure_resolution_replay_rows_source_package_route_preflight": str(
            ROWS_SOURCE_PACKAGE_ROUTE_PREFLIGHT_PATH
        ),
    }
    (OUT_DIR / "agent61_report.md").write_text(
        _report_md(
            report,
            generated_files,
            field_rows_source,
            field_rows_schema_validation,
            field_rows_collection_checklist,
            field_rows_batch_bundle_preflight,
            field_rows_temporal_window_preflight,
            field_rows_scenario_semantic_preflight,
            field_rows_downstream_routing_preflight,
            field_rows_downstream_route_handoff,
            field_rows_downstream_target_gate_preflight,
            field_rows_downstream_target_gate_result_intake_schema,
            field_rows_downstream_target_gate_result_preflight,
            field_rows_downstream_target_gate_result_arbitration,
            field_rows_downstream_target_gate_operator_review_template,
            field_rows_downstream_target_gate_operator_review_preflight,
            field_rows_downstream_target_gate_post_review_gate,
            field_rows_downstream_target_gate_protective_candidate_evaluation,
            field_rows_r7_staging_preflight,
            field_rows_r7_completion_plan,
            field_rows_r7_completion_route_contracts,
            field_rows_r7_completion_route_work_packages,
            field_rows_r7_completion_route_work_package_templates,
            field_rows_r7_completion_route_work_package_preflight,
            field_rows_r7_completion_route_work_package_patch_plan,
            field_rows_r7_completion_route_work_package_assembly_gate,
            field_rows_submission_readiness_review,
            field_rows_source_package_submission_route_guide,
            field_rows_source_package_route_preflight,
        ),
        encoding="utf-8",
    )
    (OUT_DIR / "agent61_report.json").write_text(
        json.dumps(
            {
                "pressure_resolution_replay_scenario_pack": _report_payload(report),
                "field_rows_source": field_rows_source,
                "field_rows_package_schema": field_rows_package_schema,
                "field_rows_schema_validation": field_rows_schema_validation,
                "field_rows_batch_bundle_preflight": field_rows_batch_bundle_preflight,
                "field_rows_temporal_window_preflight": field_rows_temporal_window_preflight,
                "field_rows_scenario_semantic_preflight": field_rows_scenario_semantic_preflight,
                "field_rows_downstream_routing_preflight": field_rows_downstream_routing_preflight,
                "field_rows_downstream_route_handoff": field_rows_downstream_route_handoff,
                "field_rows_downstream_target_gate_preflight": field_rows_downstream_target_gate_preflight,
                "field_rows_downstream_target_gate_result_intake_schema": (
                    field_rows_downstream_target_gate_result_intake_schema
                ),
                "field_rows_downstream_target_gate_result_preflight": (
                    field_rows_downstream_target_gate_result_preflight
                ),
                "field_rows_downstream_target_gate_result_arbitration": (
                    field_rows_downstream_target_gate_result_arbitration
                ),
                "field_rows_downstream_target_gate_operator_review_template": (
                    field_rows_downstream_target_gate_operator_review_template
                ),
                "field_rows_downstream_target_gate_operator_review_preflight": (
                    field_rows_downstream_target_gate_operator_review_preflight
                ),
                "field_rows_downstream_target_gate_post_review_gate": (
                    field_rows_downstream_target_gate_post_review_gate
                ),
                "field_rows_downstream_target_gate_protective_candidate_evaluation": (
                    field_rows_downstream_target_gate_protective_candidate_evaluation
                ),
                "field_rows_collection_checklist": field_rows_collection_checklist,
                "field_rows_operator_handoff": field_rows_operator_handoff,
                "field_rows_csv_template": field_rows_csv_template,
                "field_rows_r7_alignment": field_rows_r7_alignment,
                "field_rows_r7_staging_preflight": field_rows_r7_staging_preflight,
                "field_rows_r7_completion_plan": field_rows_r7_completion_plan,
                "field_rows_r7_completion_route_contracts": field_rows_r7_completion_route_contracts,
                "field_rows_r7_completion_route_work_packages": field_rows_r7_completion_route_work_packages,
                "field_rows_r7_completion_route_work_package_templates": (
                    field_rows_r7_completion_route_work_package_templates
                ),
                "field_rows_r7_completion_route_work_package_preflight": (
                    field_rows_r7_completion_route_work_package_preflight
                ),
                "field_rows_r7_completion_route_work_package_patch_plan": (
                    field_rows_r7_completion_route_work_package_patch_plan
                ),
                "field_rows_r7_completion_route_work_package_assembly_gate": (
                    field_rows_r7_completion_route_work_package_assembly_gate
                ),
                "field_rows_submission_readiness_review": field_rows_submission_readiness_review,
                "field_rows_source_package_submission_route_guide": (
                    field_rows_source_package_submission_route_guide
                ),
                "field_rows_source_package_route_preflight": field_rows_source_package_route_preflight,
                "generated_files": generated_files,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    _update_manifest(
        generated_files,
        report,
        field_rows_source,
        field_rows_schema_validation,
        field_rows_collection_checklist,
        field_rows_batch_bundle_preflight,
        field_rows_temporal_window_preflight,
        field_rows_scenario_semantic_preflight,
        field_rows_downstream_routing_preflight,
        field_rows_downstream_route_handoff,
        field_rows_downstream_target_gate_preflight,
        field_rows_downstream_target_gate_result_intake_schema,
        field_rows_downstream_target_gate_result_preflight,
        field_rows_downstream_target_gate_result_arbitration,
        field_rows_downstream_target_gate_operator_review_template,
        field_rows_downstream_target_gate_operator_review_preflight,
        field_rows_downstream_target_gate_post_review_gate,
        field_rows_downstream_target_gate_protective_candidate_evaluation,
        field_rows_r7_staging_preflight,
        field_rows_r7_completion_plan,
        field_rows_r7_completion_route_contracts,
        field_rows_r7_completion_route_work_packages,
        field_rows_r7_completion_route_work_package_templates,
        field_rows_r7_completion_route_work_package_preflight,
        field_rows_r7_completion_route_work_package_patch_plan,
        field_rows_r7_completion_route_work_package_assembly_gate,
        field_rows_submission_readiness_review,
        field_rows_source_package_submission_route_guide,
        field_rows_source_package_route_preflight,
    )

    print(report.summary)
    for recommendation in report.recommendations:
        print(f"- {recommendation}")
    for key, path in generated_files.items():
        print(f"{key}: {path}")


def _read_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _field_rows_path() -> Path:
    configured = os.environ.get("PRESSURE_RESOLUTION_REPLAY_ROWS_PATH")
    return Path(configured).expanduser() if configured else DEFAULT_FIELD_ROWS_PATH


def _r7_field_package_path() -> Path | None:
    configured = os.environ.get("REAL_FIELD_REPLAY_PACKAGE_DIR", "").strip()
    return Path(configured).expanduser() if configured else None


def _r7_completion_route_work_package_submission_path() -> Path | None:
    configured = os.environ.get("R7_TO_R8P_WORK_PACKAGE_DIR", "").strip()
    return Path(configured).expanduser() if configured else None


def _r8v_target_gate_result_package_path() -> Path | None:
    configured = os.environ.get("R8V_TARGET_GATE_RESULT_PACKAGE_PATH", "").strip()
    return Path(configured).expanduser() if configured else None


def _r8v_target_gate_operator_review_path() -> Path | None:
    configured = os.environ.get("R8V_TARGET_GATE_OPERATOR_REVIEW_PATH", "").strip()
    return Path(configured).expanduser() if configured else None


def _read_field_rows_package(path: Path) -> tuple[dict[str, list[dict[str, object]]], dict[str, object]]:
    expected_tables = sorted({*REQUIRED_TABLE_FIELDS, "agent52_replay_table"})
    source = "env_PRESSURE_RESOLUTION_REPLAY_ROWS_PATH" if os.environ.get("PRESSURE_RESOLUTION_REPLAY_ROWS_PATH") else "default_path"
    base = {
        "field_rows_source_path": str(path),
        "field_rows_source": source,
        "expected_tables": expected_tables,
        "accepted_source_formats": ["json_table_mapping", "csv_directory_with_optional_metadata_json"],
        "can_be_field_evidence_by_source_only": False,
    }
    if not path.exists():
        return {}, {
            **base,
            "field_rows_source_status": "field_rows_file_missing",
            "field_rows_source_format": "missing",
            "table_count": 0,
            "row_count": 0,
            "missing_tables": expected_tables,
            "empty_tables": [],
            "invalid_table_shapes": [],
            "unknown_tables": [],
            "preflight_blockers": ["field_rows_file_missing"],
        }
    if path.is_dir():
        return _read_field_rows_csv_directory(path, expected_tables, base)
    return _read_field_rows_json_file(path, expected_tables, base)


def _read_field_rows_json_file(
    path: Path,
    expected_tables: list[str],
    base: dict[str, object],
) -> tuple[dict[str, list[dict[str, object]]], dict[str, object]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except JSONDecodeError as exc:
        return {}, {
            **base,
            "field_rows_source_status": "field_rows_file_invalid_json",
            "field_rows_source_format": "json_table_mapping",
            "table_count": 0,
            "row_count": 0,
            "missing_tables": expected_tables,
            "empty_tables": [],
            "invalid_table_shapes": [],
            "unknown_tables": [],
            "preflight_blockers": [f"invalid_json:{exc.msg}"],
        }
    if not isinstance(payload, dict):
        return {}, {
            **base,
            "field_rows_source_status": "field_rows_file_invalid_shape",
            "field_rows_source_format": "json_table_mapping",
            "table_count": 0,
            "row_count": 0,
            "missing_tables": expected_tables,
            "empty_tables": [],
            "invalid_table_shapes": ["root:not_object"],
            "unknown_tables": [],
            "preflight_blockers": ["root_json_must_be_object_mapping_table_to_rows"],
        }

    rows_by_table: dict[str, list[dict[str, object]]] = {}
    invalid_shapes: list[str] = []
    table_summaries: list[dict[str, object]] = []
    missing_tables = [table for table in expected_tables if table not in payload]
    unknown_tables = sorted(str(table) for table in payload if str(table) not in expected_tables)
    for table in expected_tables:
        raw_rows = payload.get(table, [])
        if not isinstance(raw_rows, list):
            invalid_shapes.append(f"{table}:not_list")
            rows_by_table[table] = []
            table_summaries.append({"table": table, "row_count": 0, "non_object_row_count": 0})
            continue
        valid_rows = [row for row in raw_rows if isinstance(row, dict)]
        non_object_count = len(raw_rows) - len(valid_rows)
        if non_object_count:
            invalid_shapes.append(f"{table}:non_object_rows={non_object_count}")
        rows_by_table[table] = valid_rows
        table_summaries.append(
            {
                "table": table,
                "row_count": len(valid_rows),
                "non_object_row_count": non_object_count,
            }
        )
    row_count = sum(len(rows) for rows in rows_by_table.values())
    empty_tables = [table for table, rows in rows_by_table.items() if not rows]
    blockers = [*invalid_shapes, *(f"{table}:missing_table" for table in missing_tables)]
    if not row_count:
        blockers.append("no_object_rows_loaded")
    status = "field_rows_file_loaded"
    if not row_count:
        status = "field_rows_file_empty_or_no_object_rows"
    elif missing_tables:
        status = "field_rows_file_loaded_with_schema_gaps"
    elif invalid_shapes or unknown_tables:
        status = "field_rows_file_loaded_with_shape_warnings"
    return rows_by_table, {
        **base,
        "field_rows_source_status": status,
        "field_rows_source_format": "json_table_mapping",
        "table_count": len(rows_by_table),
        "row_count": row_count,
        "table_summaries": table_summaries,
        "missing_tables": missing_tables,
        "empty_tables": empty_tables,
        "invalid_table_shapes": invalid_shapes,
        "unknown_tables": unknown_tables,
        "preflight_blockers": blockers,
    }


def _read_field_rows_csv_directory(
    path: Path,
    expected_tables: list[str],
    base: dict[str, object],
) -> tuple[dict[str, list[dict[str, object]]], dict[str, object]]:
    rows_by_table: dict[str, list[dict[str, object]]] = {}
    invalid_shapes: list[str] = []
    table_summaries: list[dict[str, object]] = []
    metadata_audit = _read_field_rows_directory_metadata(path)
    expected_csv_names = {f"{table}.csv" for table in expected_tables}
    observed_csv_paths = sorted(path.glob("*.csv"))
    observed_csv_names = {csv_path.name for csv_path in observed_csv_paths}
    missing_tables = [
        table
        for table in expected_tables
        if f"{table}.csv" not in observed_csv_names
    ]
    unknown_tables = sorted(
        csv_path.stem
        for csv_path in observed_csv_paths
        if csv_path.name not in expected_csv_names
    )

    for table in expected_tables:
        csv_path = path / f"{table}.csv"
        if not csv_path.exists():
            continue
        rows, table_invalid_shapes, header = _read_field_rows_csv_table(csv_path)
        rows_by_table[table] = rows
        invalid_shapes.extend(f"{table}:{shape}" for shape in table_invalid_shapes)
        table_summaries.append(
            {
                "table": table,
                "source_file": str(csv_path),
                "row_count": len(rows),
                "csv_header": header,
                "non_object_row_count": 0,
            }
        )

    row_count = sum(len(rows) for rows in rows_by_table.values())
    empty_tables = [table for table, rows in rows_by_table.items() if not rows]
    blockers = [*invalid_shapes, *(f"{table}:missing_table" for table in missing_tables)]
    if not row_count:
        blockers.append("no_object_rows_loaded")

    status = "field_rows_directory_loaded"
    if not row_count:
        status = "field_rows_directory_empty_or_no_object_rows"
    elif missing_tables:
        status = "field_rows_directory_loaded_with_schema_gaps"
    elif invalid_shapes or unknown_tables:
        status = "field_rows_directory_loaded_with_shape_warnings"
    return rows_by_table, {
        **base,
        "field_rows_source_status": status,
        "field_rows_source_format": "csv_directory_with_optional_metadata_json",
        "field_rows_directory_metadata": metadata_audit,
        "table_count": len(rows_by_table),
        "row_count": row_count,
        "table_summaries": table_summaries,
        "missing_tables": missing_tables,
        "empty_tables": empty_tables,
        "invalid_table_shapes": invalid_shapes,
        "unknown_tables": unknown_tables,
        "preflight_blockers": blockers,
        "source_boundary": (
            "A CSV directory only improves field-row ingestion ergonomics. It does not prove field evidence "
            "until row-level provenance, same-batch bundles, temporal windows, scenario semantics, and R8v/R7 gates pass."
        ),
    }


def _read_field_rows_csv_table(csv_path: Path) -> tuple[list[dict[str, object]], list[str], list[str]]:
    invalid_shapes: list[str] = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return [], ["missing_header"], []
        header = [str(field) for field in reader.fieldnames if field is not None]
        rows: list[dict[str, object]] = []
        for row_index, raw_row in enumerate(reader):
            if None in raw_row:
                invalid_shapes.append(f"row_{row_index}:extra_values_without_header")
            normalized: dict[str, object] = {}
            for field, value in raw_row.items():
                if field is None:
                    continue
                normalized[str(field)] = _coerce_csv_field_value(str(field), value)
            rows.append(normalized)
    return rows, invalid_shapes, header


def _coerce_csv_field_value(field: str, value: object) -> object:
    if value is None:
        return ""
    if not isinstance(value, str):
        return value
    text = value.strip()
    expected = _field_schema(field).get("type")
    if expected == "boolean":
        lowered = text.lower()
        if lowered in {"true", "1", "yes", "y", "t", "是"}:
            return True
        if lowered in {"false", "0", "no", "n", "f", "否"}:
            return False
        return text
    if expected == ["number", "integer"]:
        if not text:
            return text
        try:
            numeric = float(text)
        except ValueError:
            return text
        return int(numeric) if numeric.is_integer() else numeric
    return text


def _read_field_rows_directory_metadata(path: Path) -> dict[str, object]:
    metadata_path = path / "metadata.json"
    if not metadata_path.exists():
        return {
            "metadata_status": "metadata_missing_optional_for_r8p_rows",
            "metadata_path": str(metadata_path),
            "metadata_boundary": "R8p row-level data_origin remains authoritative for field evidence gating.",
        }
    try:
        payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    except JSONDecodeError as exc:
        return {
            "metadata_status": "metadata_invalid_json_optional_for_r8p_rows",
            "metadata_path": str(metadata_path),
            "metadata_error": exc.msg,
            "metadata_boundary": "Invalid metadata does not create field evidence; row-level gates still decide acceptance.",
        }
    if not isinstance(payload, dict):
        return {
            "metadata_status": "metadata_invalid_shape_optional_for_r8p_rows",
            "metadata_path": str(metadata_path),
            "metadata_boundary": "Metadata must be an object if supplied, but row-level gates still decide acceptance.",
        }
    return {
        "metadata_status": "metadata_loaded_optional_for_r8p_rows",
        "metadata_path": str(metadata_path),
        "data_origin": payload.get("data_origin"),
        "site_id": payload.get("site_id"),
        "campaign_id": payload.get("campaign_id"),
        "chain_of_custody_id": payload.get("chain_of_custody_id"),
        "metadata_boundary": "Metadata is provenance context only; every required row still needs field-origin values.",
    }


def _write_field_rows_csv_template(
    package_dir: Path,
    template_rows_by_table: dict[str, list[dict[str, object]]],
) -> dict[str, object]:
    expected_tables = sorted({*REQUIRED_TABLE_FIELDS, "agent52_replay_table"})
    package_dir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "data_origin": "TODO_FIELD_PROVENANCE_NOT_EVIDENCE_UNTIL_REPLACED",
        "site_id": "TODO_REAL_SITE_ID",
        "campaign_id": "TODO_REAL_CAMPAIGN_ID",
        "sampling_start": "TODO_ISO8601_START_TIME",
        "sampling_end": "TODO_ISO8601_END_TIME",
        "operator_id": "TODO_REAL_OPERATOR_ID",
        "instrument_snapshot_id": "TODO_SENSOR_AND_LAB_INSTRUMENT_SNAPSHOT_ID",
        "chain_of_custody_id": "TODO_SIGNED_CHAIN_OF_CUSTODY_ID",
        "package_role": "R8p_pressure_resolution_rows_csv_template",
        "evidence_boundary": (
            "This directory is a collection template, not field evidence. Replace every TODO/template marker "
            "and rerun Agent61 before any R8v/R7 routing."
        ),
    }
    (package_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    table_summaries: list[dict[str, object]] = []
    for table in expected_tables:
        rows = template_rows_by_table.get(table, [])
        fieldnames = _field_rows_csv_template_fieldnames(table, rows)
        csv_path = package_dir / f"{table}.csv"
        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        table_summaries.append(
            {
                "table": table,
                "csv_path": str(csv_path),
                "row_count": len(rows),
                "header_count": len(fieldnames),
                "headers": fieldnames,
                "required_fields": _required_fields_for_table(table),
            }
        )
    return {
        "template_dir": str(package_dir),
        "source_format": "csv_directory_with_optional_metadata_json",
        "required_files": ["metadata.json", *[f"{table}.csv" for table in expected_tables]],
        "required_tables": expected_tables,
        "table_count": len(expected_tables),
        "template_row_count": sum(len(template_rows_by_table.get(table, [])) for table in expected_tables),
        "table_summaries": table_summaries,
        "validation_command_with_env_override": (
            f"PRESSURE_RESOLUTION_REPLAY_ROWS_PATH={package_dir} "
            ".venv/bin/python experiments/run_agent61_pressure_resolution_replay_scenario_pack.py"
        ),
        "template_boundary": (
            "The generated CSV rows intentionally retain TODO/template markers and template_only flags. "
            "Submitting this directory unchanged must fail R8p template-marker/source gates."
        ),
        "can_be_field_evidence_by_template": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }


def _field_rows_csv_template_fieldnames(table: str, rows: list[dict[str, object]]) -> list[str]:
    required_fields = _required_fields_for_table(table)
    preferred_fields = [
        *required_fields,
        "scenario_id",
        "scenario_type",
        "collection_id",
        "template_only",
        "evidence_status",
        "source_stage",
    ]
    observed_fields = sorted({str(field) for row in rows for field in row})
    fieldnames: list[str] = []
    seen: set[str] = set()
    for field in [*preferred_fields, *observed_fields]:
        if field not in observed_fields or field in seen:
            continue
        fieldnames.append(field)
        seen.add(field)
    return fieldnames


def _field_rows_r7_alignment(field_rows_package_schema: dict[str, object]) -> dict[str, object]:
    r7_spec = field_replay_package_template_spec()
    r7_headers = {
        str(table): [str(field) for field in fields]
        for table, fields in dict(r7_spec.get("csv_headers", {})).items()
        if isinstance(fields, list)
    }
    expected_tables = [str(table) for table in field_rows_package_schema.get("required", [])]
    table_alignments = [
        _r7_alignment_for_table(table, r7_headers)
        for table in expected_tables
    ]
    direct_count = sum(int(item["direct_field_count"]) for item in table_alignments)
    alias_count = sum(int(item["alias_field_count"]) for item in table_alignments)
    metadata_count = sum(int(item["metadata_field_count"]) for item in table_alignments)
    supplement_count = sum(int(item["supplement_required_field_count"]) for item in table_alignments)
    agent52_count = sum(int(item["agent52_export_required_field_count"]) for item in table_alignments)
    reusable_table_count = sum(
        1
        for item in table_alignments
        if item["table_reuse_status"] in {
            "fully_reusable_from_r7_package_with_metadata_copy",
            "reusable_from_r7_package_with_aliases_and_supplements",
        }
    )
    status = "r7_to_r8p_alignment_ready_requires_r8p_supplements_and_agent52_export"
    if agent52_count == 0 and supplement_count == 0:
        status = "r7_to_r8p_alignment_fully_reusable_after_metadata_copy"
    return {
        "alignment_id": "R8u20_r7_to_r8p_pressure_resolution_rows_alignment",
        "alignment_path": str(ROWS_R7_ALIGNMENT_PATH),
        "alignment_status": status,
        "model_core_layers": ["observability_layer", "verification_governance_layer"],
        "source_package": "R7_Agent44_real_field_package",
        "target_package": "R8p_pressure_resolution_replay_rows",
        "expected_table_count": len(expected_tables),
        "r7_shared_table_count": sum(1 for item in table_alignments if item["r7_source_table_present"]),
        "r8p_reusable_table_count": reusable_table_count,
        "direct_field_count": direct_count,
        "alias_field_count": alias_count,
        "metadata_field_count": metadata_count,
        "supplement_required_field_count": supplement_count,
        "agent52_export_required_field_count": agent52_count,
        "table_alignments": table_alignments,
        "required_pipeline_sequence": [
            "Fill and pass Agent44/R7 metadata+CSV field package import gates.",
            "Copy or transform R7 shared CSV rows into the R8p pressure-resolution row package.",
            "Add R8p scenario identifiers and operator pressure-source resolution supplement fields.",
            "Export Agent49/52 replay rows into agent52_replay_table.csv instead of fabricating them from field CSV.",
            "Run Agent61 R8p schema, provenance, template-marker, bundle, temporal, semantic, and downstream-routing gates.",
        ],
        "technical_feature_mapping": {
            "technical_problem": (
                "R7 field packages and R8p pressure-resolution replay packages collect overlapping evidence but use "
                "different field names and different model-output tables, which can create duplicate entry and hidden gaps."
            ),
            "technical_means": (
                "A machine-readable crosswalk separates directly reusable R7 fields, alias transforms, metadata-to-row "
                "provenance copies, operator supplements, and Agent52 replay export requirements."
            ),
            "technical_effect": (
                "The same low-cost field package can feed pressure-source conflict replay without weakening evidence gates "
                "or fabricating control replay rows."
            ),
            "prior_art_distinction_candidate": (
                "The alignment treats sparse field observations, operator review records, and offline replay actions as "
                "separate evidence classes with explicit routing and failure boundaries."
            ),
        },
        "field_boundary": (
            "This alignment is an interface contract only. It does not transform template rows into field evidence, "
            "does not generate Agent52 replay evidence, and cannot write actuator or release gates."
        ),
        "can_generate_field_evidence_from_template": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }


def _field_rows_r7_staging_preflight(
    r7_package_path: Path | None,
    field_rows_r7_alignment: dict[str, object],
    field_rows_package_schema: dict[str, object],
) -> dict[str, object]:
    expected_tables = [str(table) for table in field_rows_package_schema.get("required", [])]
    empty_rows = {table: [] for table in expected_tables}
    base = {
        "staging_id": "R8u21_r7_to_r8p_pressure_resolution_rows_staging_preflight",
        "model_core_layers": ["observability_layer", "verification_governance_layer"],
        "source_package": "R7_Agent44_real_field_package",
        "target_package": "R8p_pressure_resolution_replay_rows",
        "r7_package_env_override": "REAL_FIELD_REPLAY_PACKAGE_DIR",
        "staging_preflight_path": str(ROWS_R7_STAGING_PREFLIGHT_PATH),
        "staged_draft_path": str(ROWS_R7_STAGED_DRAFT_PATH),
        "expected_tables": expected_tables,
        "staged_draft_rows_by_table": empty_rows,
        "can_generate_field_evidence_from_staging": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "staging_boundary": (
            "R7-to-R8p staging only copies reusable field/package values into a draft. It does not create Agent52 replay "
            "rows, does not replace operator review/calibration supplements, and does not make field-supported claims until "
            "Agent44/R7 and Agent61/R8p gates pass."
        ),
    }
    if r7_package_path is None:
        return {
            **base,
            "r7_staging_preflight_status": "r7_to_r8p_staging_preflight_no_r7_package_supplied",
            "r7_package_path": None,
            "metadata_audit": {"metadata_status": "not_checked_no_package"},
            "source_table_audit": [],
            "table_staging_preflight": [],
            "staged_table_count": 0,
            "staged_row_count": 0,
            "required_field_gap_count": 0,
            "supplement_required_field_gap_count": 0,
            "agent52_export_required_field_gap_count": int(
                field_rows_r7_alignment.get("agent52_export_required_field_count", 0)
            ),
            "can_enter_r8p_schema_preflight": False,
            "next_operator_action": "Set REAL_FIELD_REPLAY_PACKAGE_DIR to a real R7 metadata+CSV package and rerun Agent61.",
        }
    if not r7_package_path.exists():
        return {
            **base,
            "r7_staging_preflight_status": "r7_to_r8p_staging_preflight_invalid_r7_package_path",
            "r7_package_path": str(r7_package_path),
            "metadata_audit": {"metadata_status": "not_checked_path_missing"},
            "source_table_audit": [],
            "table_staging_preflight": [],
            "staged_table_count": 0,
            "staged_row_count": 0,
            "required_field_gap_count": 0,
            "supplement_required_field_gap_count": 0,
            "agent52_export_required_field_gap_count": int(
                field_rows_r7_alignment.get("agent52_export_required_field_count", 0)
            ),
            "can_enter_r8p_schema_preflight": False,
            "next_operator_action": "Point REAL_FIELD_REPLAY_PACKAGE_DIR to an existing R7 field package directory.",
        }
    if not r7_package_path.is_dir():
        return {
            **base,
            "r7_staging_preflight_status": "r7_to_r8p_staging_preflight_r7_package_not_directory",
            "r7_package_path": str(r7_package_path),
            "metadata_audit": {"metadata_status": "not_checked_path_not_directory"},
            "source_table_audit": [],
            "table_staging_preflight": [],
            "staged_table_count": 0,
            "staged_row_count": 0,
            "required_field_gap_count": 0,
            "supplement_required_field_gap_count": 0,
            "agent52_export_required_field_gap_count": int(
                field_rows_r7_alignment.get("agent52_export_required_field_count", 0)
            ),
            "can_enter_r8p_schema_preflight": False,
            "next_operator_action": "Provide the R7 metadata+CSV directory, not a single file.",
        }

    r7_spec = field_replay_package_template_spec()
    r7_headers = {
        str(table): [str(field) for field in fields]
        for table, fields in dict(r7_spec.get("csv_headers", {})).items()
        if isinstance(fields, list)
    }
    metadata_audit = _read_r7_staging_metadata(r7_package_path)
    r7_rows_by_table, source_table_audit = _read_r7_staging_csv_tables(r7_package_path, r7_headers)
    table_staging_preflight: list[dict[str, object]] = []
    staged_draft_rows_by_table: dict[str, list[dict[str, object]]] = {table: [] for table in expected_tables}
    required_field_gap_count = 0
    supplement_required_field_gap_count = 0
    agent52_export_required_field_gap_count = 0

    alignments = [
        item
        for item in field_rows_r7_alignment.get("table_alignments", [])
        if isinstance(item, dict)
    ]
    for table_alignment in alignments:
        table = str(table_alignment.get("target_table", ""))
        required_fields = [str(field) for field in table_alignment.get("required_fields", [])]
        if table == "agent52_replay_table":
            agent52_export_required_field_gap_count += len(required_fields)
            table_staging_preflight.append(
                {
                    "target_table": table,
                    "table_staging_status": "requires_agent52_replay_export_not_r7_staging",
                    "source_row_count": 0,
                    "staged_row_count": 0,
                    "required_fields": required_fields,
                    "missing_required_fields": required_fields,
                    "required_field_gap_count": len(required_fields),
                    "supplement_required_field_gap_count": 0,
                    "agent52_export_required_field_gap_count": len(required_fields),
                    "field_checks": [
                        {
                            "target_field": field,
                            "stage_status": "agent52_replay_export_required",
                            "field_boundary": "Must be exported from Agent49/52 replay after pressure-source conflict evaluation.",
                        }
                        for field in required_fields
                    ],
                }
            )
            continue

        source_rows = r7_rows_by_table.get(table, [])
        if not source_rows:
            required_field_gap_count += len(required_fields)
            table_staging_preflight.append(
                {
                    "target_table": table,
                    "table_staging_status": "r7_source_table_missing_or_empty",
                    "source_row_count": 0,
                    "staged_row_count": 0,
                    "required_fields": required_fields,
                    "missing_required_fields": required_fields,
                    "required_field_gap_count": len(required_fields),
                    "supplement_required_field_gap_count": int(
                        table_alignment.get("supplement_required_field_count", 0)
                    ),
                    "agent52_export_required_field_gap_count": 0,
                    "field_checks": [],
                }
            )
            supplement_required_field_gap_count += int(table_alignment.get("supplement_required_field_count", 0))
            continue

        table_missing_required: set[str] = set()
        table_supplement_gap_count = 0
        table_field_checks: list[dict[str, object]] = []
        for row_index, source_row in enumerate(source_rows):
            staged_row: dict[str, object] = {}
            row_field_checks: list[dict[str, object]] = []
            for mapping in table_alignment.get("field_mappings", []):
                if not isinstance(mapping, dict):
                    continue
                field_check = _stage_r7_field(mapping, source_row, metadata_audit)
                row_field_checks.append({"row_index": row_index, **field_check})
                if field_check["stage_status"] == "staged":
                    staged_row[str(field_check["target_field"])] = field_check["staged_value"]
                else:
                    table_missing_required.add(str(field_check["target_field"]))
                    if field_check["source_kind"] == "r8p_supplement_or_operator_record_required":
                        table_supplement_gap_count += 1
            if staged_row:
                staged_draft_rows_by_table[table].append(staged_row)
            table_field_checks.extend(row_field_checks[: len(required_fields)])

        missing_required_fields = [field for field in required_fields if field in table_missing_required]
        required_field_gap_count += len(missing_required_fields)
        supplement_required_field_gap_count += table_supplement_gap_count
        status = "r7_table_staged_ready_for_r8p_schema_preflight"
        if missing_required_fields:
            status = "r7_table_staged_with_required_field_gaps"
        table_staging_preflight.append(
            {
                "target_table": table,
                "table_staging_status": status,
                "source_row_count": len(source_rows),
                "staged_row_count": len(staged_draft_rows_by_table[table]),
                "required_fields": required_fields,
                "missing_required_fields": missing_required_fields,
                "required_field_gap_count": len(missing_required_fields),
                "supplement_required_field_gap_count": table_supplement_gap_count,
                "agent52_export_required_field_gap_count": 0,
                "field_checks": table_field_checks[:30],
            }
        )

    staged_table_count = sum(1 for rows in staged_draft_rows_by_table.values() if rows)
    staged_row_count = sum(len(rows) for rows in staged_draft_rows_by_table.values())
    metadata_status = str(metadata_audit.get("metadata_status", "metadata_unknown"))
    metadata_origin_ready = bool(metadata_audit.get("field_origin_ready"))
    if metadata_status != "metadata_loaded":
        status = "r7_to_r8p_staging_blocked_at_r7_metadata_preflight"
    elif not metadata_origin_ready:
        status = "r7_to_r8p_staging_blocked_at_r7_metadata_provenance"
    elif staged_row_count == 0:
        status = "r7_to_r8p_staging_no_reusable_r7_rows_loaded"
    elif required_field_gap_count or supplement_required_field_gap_count or agent52_export_required_field_gap_count:
        status = "r7_to_r8p_staging_ready_requires_supplements_and_agent52_export"
    else:
        status = "r7_to_r8p_staging_ready_for_r8p_schema_preflight"
    can_enter = status == "r7_to_r8p_staging_ready_for_r8p_schema_preflight"
    return {
        **base,
        "r7_staging_preflight_status": status,
        "r7_package_path": str(r7_package_path),
        "metadata_audit": metadata_audit,
        "source_table_audit": source_table_audit,
        "table_staging_preflight": table_staging_preflight,
        "staged_draft_rows_by_table": staged_draft_rows_by_table,
        "staged_table_count": staged_table_count,
        "staged_row_count": staged_row_count,
        "required_field_gap_count": required_field_gap_count,
        "supplement_required_field_gap_count": supplement_required_field_gap_count,
        "agent52_export_required_field_gap_count": agent52_export_required_field_gap_count,
        "can_enter_r8p_schema_preflight": can_enter,
        "r8p_schema_preflight_command_with_staged_draft": (
            f"PRESSURE_RESOLUTION_REPLAY_ROWS_PATH={ROWS_R7_STAGED_DRAFT_PATH} "
            ".venv/bin/python experiments/run_agent61_pressure_resolution_replay_scenario_pack.py"
        ),
        "next_operator_action": _r7_staging_next_action(
            status,
            required_field_gap_count,
            supplement_required_field_gap_count,
            agent52_export_required_field_gap_count,
        ),
    }


def _read_r7_staging_metadata(root: Path) -> dict[str, object]:
    metadata_path = root / "metadata.json"
    if not metadata_path.exists():
        return {
            "metadata_status": "metadata_missing",
            "metadata_path": str(metadata_path),
            "field_origin_ready": False,
            "metadata": {},
        }
    try:
        payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    except JSONDecodeError as exc:
        return {
            "metadata_status": "metadata_invalid_json",
            "metadata_path": str(metadata_path),
            "metadata_error": exc.msg,
            "field_origin_ready": False,
            "metadata": {},
        }
    if not isinstance(payload, dict):
        return {
            "metadata_status": "metadata_invalid_shape",
            "metadata_path": str(metadata_path),
            "field_origin_ready": False,
            "metadata": {},
        }
    data_origin = payload.get("data_origin")
    return {
        "metadata_status": "metadata_loaded",
        "metadata_path": str(metadata_path),
        "data_origin": data_origin,
        "site_id": payload.get("site_id"),
        "campaign_id": payload.get("campaign_id"),
        "instrument_snapshot_id": payload.get("instrument_snapshot_id"),
        "chain_of_custody_id": payload.get("chain_of_custody_id"),
        "field_origin_ready": _is_field_origin_value(data_origin),
        "metadata": payload,
        "metadata_boundary": (
            "Metadata can provide provenance context and data_origin copy only; Agent44 and R8p row gates still decide field acceptance."
        ),
    }


def _read_r7_staging_csv_tables(
    root: Path,
    r7_headers: dict[str, list[str]],
) -> tuple[dict[str, list[dict[str, object]]], list[dict[str, object]]]:
    rows_by_table: dict[str, list[dict[str, object]]] = {}
    source_table_audit: list[dict[str, object]] = []
    for table, expected_headers in sorted(r7_headers.items()):
        csv_path = root / f"{table}.csv"
        if not csv_path.exists():
            source_table_audit.append(
                {
                    "table": table,
                    "csv_path": str(csv_path),
                    "source_table_status": "r7_csv_missing",
                    "row_count": 0,
                    "expected_headers": expected_headers,
                    "actual_headers": [],
                    "invalid_shapes": [],
                }
            )
            continue
        rows, invalid_shapes, actual_headers = _read_field_rows_csv_table(csv_path)
        rows_by_table[table] = rows
        missing_expected_headers = [field for field in expected_headers if field not in actual_headers]
        status = "r7_csv_loaded"
        if invalid_shapes:
            status = "r7_csv_loaded_with_shape_warnings"
        source_table_audit.append(
            {
                "table": table,
                "csv_path": str(csv_path),
                "source_table_status": status,
                "row_count": len(rows),
                "expected_headers": expected_headers,
                "actual_headers": actual_headers,
                "missing_expected_headers": missing_expected_headers,
                "invalid_shapes": invalid_shapes,
            }
        )
    return rows_by_table, source_table_audit


def _stage_r7_field(
    mapping: dict[str, object],
    source_row: dict[str, object],
    metadata_audit: dict[str, object],
) -> dict[str, object]:
    target_field = str(mapping.get("target_field", ""))
    source_kind = str(mapping.get("source_kind", "unknown"))
    source_field = str(mapping.get("source_field", ""))
    metadata = metadata_audit.get("metadata") if isinstance(metadata_audit.get("metadata"), dict) else {}
    stage_status = "missing_required_value"
    source_value: object = None
    used_source_field = source_field
    if source_kind in {"direct_csv_field", "alias_csv_field"}:
        source_value = source_row.get(source_field)
    elif source_kind == "metadata_to_row_copy_after_agent44_gate":
        source_value = metadata.get(source_field)
    elif source_kind == "r8p_supplement_or_operator_record_required":
        used_source_field, source_value = _r7_supplement_candidate_value(target_field, source_field, source_row, metadata)
    elif source_kind == "agent52_replay_export_required":
        return {
            "target_field": target_field,
            "source_kind": source_kind,
            "source_field": source_field,
            "stage_status": "agent52_replay_export_required",
            "can_be_staged_from_r7": False,
            "field_boundary": mapping.get("field_boundary", "Must be exported from Agent49/52 replay."),
        }

    if source_kind == "metadata_to_row_copy_after_agent44_gate" and not _is_field_origin_value(source_value):
        stage_status = "metadata_field_origin_not_ready"
    elif source_value is None or source_value == "" or _is_template_marker_value(source_value):
        stage_status = "missing_or_template_value"
    else:
        stage_status = "staged"
    result = {
        "target_field": target_field,
        "source_kind": source_kind,
        "source_field": used_source_field,
        "stage_status": stage_status,
        "can_be_staged_from_r7": stage_status == "staged",
        "field_boundary": mapping.get("field_boundary", "Staged value must still pass R8p row gates."),
    }
    if stage_status == "staged":
        result["staged_value"] = _coerce_csv_field_value(target_field, source_value)
    return result


def _r7_supplement_candidate_value(
    target_field: str,
    source_field: str,
    source_row: dict[str, object],
    metadata: dict[str, object],
) -> tuple[str, object]:
    candidates: list[str] = []
    if "/" in source_field:
        candidates.extend(part.strip() for part in source_field.split("/") if part.strip())
    elif "." not in source_field:
        candidates.append(source_field)
    candidates.append(target_field)
    if target_field == "instrument_id":
        candidates.extend(["instrument_id", "instrument_snapshot_id"])
    if target_field == "proxy_event_type":
        candidates.extend(["proxy_event_type", "triggered_action_id"])
    for candidate in candidates:
        if candidate in source_row and source_row.get(candidate) not in {None, ""}:
            return candidate, source_row.get(candidate)
        if candidate in metadata and metadata.get(candidate) not in {None, ""}:
            return f"metadata.json:{candidate}", metadata.get(candidate)
    return source_field, None


def _r7_staging_next_action(
    status: str,
    required_field_gap_count: int,
    supplement_required_field_gap_count: int,
    agent52_export_required_field_gap_count: int,
) -> str:
    if status == "r7_to_r8p_staging_ready_for_r8p_schema_preflight":
        return "Run Agent61 with PRESSURE_RESOLUTION_REPLAY_ROWS_PATH pointing to the staged draft, then continue R8p gates."
    if status == "r7_to_r8p_staging_blocked_at_r7_metadata_preflight":
        return "Fix R7 metadata.json before staging; missing or invalid metadata cannot provide provenance context."
    if status == "r7_to_r8p_staging_blocked_at_r7_metadata_provenance":
        return "Replace non-field/template data_origin in R7 metadata before copying provenance into R8p rows."
    if status == "r7_to_r8p_staging_no_reusable_r7_rows_loaded":
        return "Add real rows to the five R7/R8p shared CSV tables before building an R8p draft."
    gaps: list[str] = []
    if required_field_gap_count:
        gaps.append(f"{required_field_gap_count} required field gaps")
    if supplement_required_field_gap_count:
        gaps.append(f"{supplement_required_field_gap_count} operator/R8p supplement gaps")
    if agent52_export_required_field_gap_count:
        gaps.append(f"{agent52_export_required_field_gap_count} Agent52 replay export fields")
    return "Complete the staged draft before R8p acceptance: " + ", ".join(gaps) + "."


def _field_rows_r7_completion_plan(
    field_rows_r7_staging_preflight: dict[str, object],
    field_rows_r7_alignment: dict[str, object],
) -> dict[str, object]:
    staging_status = str(
        field_rows_r7_staging_preflight.get(
            "r7_staging_preflight_status",
            "r7_to_r8p_staging_preflight_not_run",
        )
    )
    completion_items: list[dict[str, object]] = []
    if staging_status in {
        "r7_to_r8p_staging_preflight_no_r7_package_supplied",
        "r7_to_r8p_staging_preflight_invalid_r7_package_path",
        "r7_to_r8p_staging_preflight_r7_package_not_directory",
        "r7_to_r8p_staging_blocked_at_r7_metadata_preflight",
        "r7_to_r8p_staging_blocked_at_r7_metadata_provenance",
        "r7_to_r8p_staging_no_reusable_r7_rows_loaded",
    }:
        completion_items.append(_r7_source_package_completion_item(staging_status))

    completion_items.extend(_operator_supplement_completion_items(field_rows_r7_alignment))
    completion_items.append(_agent52_export_completion_item(field_rows_r7_alignment))
    if staging_status == "r7_to_r8p_staging_ready_for_r8p_schema_preflight":
        completion_items.append(
            {
                "item_id": "R8U22_RUN_R8P_SCHEMA_PREFLIGHT_ON_STAGED_DRAFT",
                "priority": "P1",
                "completion_class": "r8p_schema_preflight",
                "target_table": "all_required_tables",
                "target_fields": [],
                "operator_action": (
                    "Run Agent61 with PRESSURE_RESOLUTION_REPLAY_ROWS_PATH pointing to the staged draft and inspect "
                    "schema/provenance/template/bundle/temporal/semantic/downstream gates."
                ),
                "validation_gate": "Agent61 R8p schema and scenario preflights",
                "can_create_field_evidence_by_item_only": False,
            }
        )

    item_class_counts: dict[str, int] = {}
    field_gap_count_by_class: dict[str, int] = {}
    for item in completion_items:
        item_class = str(item.get("completion_class", "unknown"))
        item_class_counts[item_class] = item_class_counts.get(item_class, 0) + 1
        field_gap_count_by_class[item_class] = field_gap_count_by_class.get(item_class, 0) + len(
            [field for field in item.get("target_fields", []) if isinstance(field, str)]
        )
    if staging_status == "r7_to_r8p_staging_ready_for_r8p_schema_preflight":
        status = "r7_to_r8p_completion_plan_ready_for_r8p_schema_preflight"
    elif staging_status == "r7_to_r8p_staging_ready_requires_supplements_and_agent52_export":
        status = "r7_to_r8p_completion_plan_ready_requires_supplement_and_agent52_export"
    elif "no_r7_package" in staging_status or "invalid_r7_package" in staging_status or "not_directory" in staging_status:
        status = "r7_to_r8p_completion_plan_waiting_for_r7_package"
    elif "metadata" in staging_status:
        status = "r7_to_r8p_completion_plan_blocked_at_r7_metadata"
    else:
        status = "r7_to_r8p_completion_plan_waiting_for_reusable_r7_rows"
    return {
        "completion_plan_id": "R8u22_r7_to_r8p_pressure_resolution_rows_completion_plan",
        "completion_plan_path": str(ROWS_R7_COMPLETION_PLAN_PATH),
        "completion_plan_status": status,
        "source_staging_status": staging_status,
        "model_core_layers": ["observability_layer", "verification_governance_layer"],
        "source_package": "R7_Agent44_real_field_package",
        "target_package": "R8p_pressure_resolution_replay_rows",
        "item_count": len(completion_items),
        "item_class_counts": item_class_counts,
        "field_gap_count_by_class": field_gap_count_by_class,
        "completion_items": completion_items,
        "required_execution_order": [
            "R7 source package and metadata provenance",
            "R7-to-R8p staging draft",
            "operator supplement records",
            "Agent49/52 replay export",
            "Agent61 R8p schema/provenance/template/bundle/temporal/semantic/routing gates",
            "R8v route to Agent51/49/52/R7 evidence chain",
        ],
        "technical_feature_mapping": {
            "technical_problem": (
                "R7 field observations, operator review records, and Agent52 replay outputs belong to different evidence "
                "classes, but pressure-resolution replay requires all of them in one row package."
            ),
            "technical_means": (
                "A completion planner converts staging gaps into ordered evidence-class tasks: source package, operator "
                "supplement, replay export, and R8p validation gates."
            ),
            "technical_effect": (
                "The field package can be completed with fewer duplicated entries while preserving proof boundaries between "
                "field observation, human review, and replay-derived control evidence."
            ),
            "prior_art_distinction_candidate": (
                "Unlike a single CSV importer, the planner keeps low-cost sparse observation, delayed human review, and "
                "offline replay as separate gated evidence routes before any control/release claim."
            ),
        },
        "field_boundary": (
            "The completion plan is an operator/replay work order. It does not make the staged draft field evidence, "
            "does not execute replay export, and cannot write actuator or release gates."
        ),
        "can_generate_field_evidence_from_plan": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }


def _field_rows_r7_completion_route_contracts(
    field_rows_r7_completion_plan: dict[str, object],
) -> dict[str, object]:
    completion_items = [
        item for item in field_rows_r7_completion_plan.get("completion_items", []) if isinstance(item, dict)
    ]
    items_by_class: dict[str, list[dict[str, object]]] = {}
    for item in completion_items:
        item_class = str(item.get("completion_class", "unknown"))
        items_by_class.setdefault(item_class, []).append(item)

    plan_status = str(
        field_rows_r7_completion_plan.get(
            "completion_plan_status",
            "r7_to_r8p_completion_plan_not_run",
        )
    )
    upstream_routes_open = any(
        items_by_class.get(item_class)
        for item_class in ("r7_source_package", "operator_supplement", "agent52_replay_export")
    )
    route_contracts = [
        _r7_completion_route_contract(
            route_id="r7_source_package",
            route_status=(
                "route_blocked_waiting_for_r7_source_package"
                if items_by_class.get("r7_source_package")
                else "route_clear_r7_source_staged_or_not_required"
            ),
            producer="R7/Agent44 field package importer",
            required_items=items_by_class.get("r7_source_package", []),
            required_tables=sorted(REQUIRED_TABLE_FIELDS),
            input_contract="REAL_FIELD_REPLAY_PACKAGE_DIR points to a field-origin R7 metadata.json + CSV directory.",
            output_contract="R7-to-R8p staged draft rows for the five shared field tables.",
            validation_gates=[
                "Agent44/R7 import preflight",
                "Agent61 R7 staging preflight",
                "metadata data_origin field provenance gate",
            ],
            validation_command=".venv/bin/python experiments/run_agent61_pressure_resolution_replay_scenario_pack.py",
            downstream_consumers=["R8p staged draft", "operator supplement merge", "Agent61 schema preflight"],
            failure_boundary="Do not infer missing field rows from template CSVs or non-field metadata.",
        ),
        _r7_completion_route_contract(
            route_id="operator_supplement",
            route_status=(
                "route_waiting_for_operator_supplement_records"
                if items_by_class.get("operator_supplement")
                else "route_clear_no_operator_supplement_gap"
            ),
            producer="field operator review and calibration workflow",
            required_items=items_by_class.get("operator_supplement", []),
            required_tables=sorted(
                {
                    str(item.get("target_table"))
                    for item in items_by_class.get("operator_supplement", [])
                    if item.get("target_table")
                }
            ),
            input_contract="Reviewed operator/calibration records for pressure source resolution and R8p-only supplement fields.",
            output_contract="Supplemented R8p target-table fields with reviewed values and reviewer/calibration provenance.",
            validation_gates=[
                "Agent61 schema required-field gate",
                "field provenance gate",
                "scenario semantic operator-review gate",
            ],
            validation_command=".venv/bin/python experiments/run_agent61_pressure_resolution_replay_scenario_pack.py",
            downstream_consumers=["R8p scenario semantic preflight", "R8v R7 evidence chain"],
            failure_boundary="Do not replace operator review fields with model guesses, TODO markers, or default false values.",
        ),
        _r7_completion_route_contract(
            route_id="agent52_replay_export",
            route_status=(
                "route_waiting_for_agent52_replay_export"
                if items_by_class.get("agent52_replay_export")
                else "route_clear_no_agent52_replay_export_gap"
            ),
            producer="Agent49/Agent52 replay evaluation chain",
            required_items=items_by_class.get("agent52_replay_export", []),
            required_tables=["agent52_replay_table"] if items_by_class.get("agent52_replay_export") else [],
            input_contract="Agent49/52 replay outputs after pressure-source conflict evaluation and expert/policy action comparison.",
            output_contract="agent52_replay_table rows with policy/expert actions and pressure-source conflict counters.",
            validation_gates=[
                "Agent52 replay clearance",
                "Agent61 schema/provenance gate",
                "R8v downstream routing preflight",
            ],
            validation_command=".venv/bin/python experiments/run_agent52_multi_facility_replay_evaluation.py",
            downstream_consumers=["Agent61 R8p schema preflight", "Agent49 guardrail context", "R8v routing"],
            failure_boundary="Do not fabricate policy_action_id, expert_action_id, or conflict counters from R7 field CSVs.",
        ),
        _r7_completion_route_contract(
            route_id="r8p_validation_gates",
            route_status=(
                "route_waiting_for_upstream_evidence_routes"
                if upstream_routes_open
                else "route_ready_for_agent61_r8p_preflight"
            ),
            producer="Agent61 pressure resolution replay scenario pack",
            required_items=items_by_class.get("r8p_schema_preflight", []),
            required_tables=sorted({*REQUIRED_TABLE_FIELDS, "agent52_replay_table"}),
            input_contract="Completed R8p row package assembled from R7 field rows, operator supplement records, and Agent52 replay export.",
            output_contract="R8p schema/provenance/template/bundle/temporal/semantic/downstream routing gate results.",
            validation_gates=[
                "schema validation",
                "field provenance gate",
                "template marker gate",
                "same-batch six-table bundle gate",
                "temporal-window gate",
                "scenario-semantic gate",
                "downstream-routing gate",
            ],
            validation_command=".venv/bin/python experiments/run_agent61_pressure_resolution_replay_scenario_pack.py",
            downstream_consumers=["Agent51 holdout", "Agent49 guardrail context", "Agent52 replay clearance", "R7 evidence chain"],
            failure_boundary="R8p validation gates can route accepted rows forward, but cannot write actuator or release gates.",
        ),
    ]
    open_route_ids = [
        str(route["route_id"])
        for route in route_contracts
        if str(route.get("route_status", "")).startswith(("route_blocked", "route_waiting"))
    ]
    if plan_status == "r7_to_r8p_completion_plan_waiting_for_r7_package":
        contract_status = "completion_route_contracts_ready_waiting_for_r7_package"
    elif plan_status == "r7_to_r8p_completion_plan_ready_requires_supplement_and_agent52_export":
        contract_status = "completion_route_contracts_ready_requires_supplement_and_agent52_export"
    elif plan_status == "r7_to_r8p_completion_plan_ready_for_r8p_schema_preflight":
        contract_status = "completion_route_contracts_ready_for_r8p_validation_gates"
    elif "metadata" in plan_status:
        contract_status = "completion_route_contracts_blocked_at_r7_metadata"
    else:
        contract_status = "completion_route_contracts_ready_with_plan_status_review"
    return {
        "completion_route_contracts_id": "R8u24_r7_to_r8p_completion_route_execution_contracts",
        "completion_route_contracts_path": str(ROWS_R7_COMPLETION_ROUTE_CONTRACTS_PATH),
        "completion_route_contracts_status": contract_status,
        "source_completion_plan_status": plan_status,
        "route_contract_count": len(route_contracts),
        "open_route_count": len(open_route_ids),
        "open_route_ids": open_route_ids,
        "route_contracts": route_contracts,
        "execution_order": field_rows_r7_completion_plan.get("required_execution_order", []),
        "technical_feature_mapping": {
            "technical_problem": (
                "Completion items identify missing evidence, but an executable grey-box control pipeline needs route-level "
                "input/output contracts and validation gates before field/replay evidence can be assembled."
            ),
            "technical_means": (
                "The route contract layer groups completion items by evidence producer and defines source package, operator "
                "supplement, replay export, and R8p validation interfaces with explicit gates and failure boundaries."
            ),
            "technical_effect": (
                "Field observations, human review, and replay-derived control evidence remain separable while becoming "
                "machine-routable into the pressure-resolution replay package."
            ),
            "prior_art_distinction_candidate": (
                "Unlike an importer or a generic checklist, the contract layer preserves low-cost sensing, delayed review, "
                "and offline replay as gated evidence routes before closed-loop control claims."
            ),
        },
        "can_generate_field_evidence_from_contracts": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }


def _field_rows_r7_completion_route_work_packages(
    field_rows_r7_completion_route_contracts: dict[str, object],
) -> dict[str, object]:
    route_contracts = [
        route
        for route in field_rows_r7_completion_route_contracts.get("route_contracts", [])
        if isinstance(route, dict)
    ]
    work_packages = [_r7_completion_route_work_package(route) for route in route_contracts]
    open_work_package_ids = [
        str(package["work_package_id"])
        for package in work_packages
        if str(package.get("work_package_status", "")).startswith(("work_package_open", "work_package_blocked"))
    ]
    source_status = str(
        field_rows_r7_completion_route_contracts.get(
            "completion_route_contracts_status",
            "completion_route_contracts_not_run",
        )
    )
    if source_status == "completion_route_contracts_ready_waiting_for_r7_package":
        status = "route_work_packages_ready_waiting_for_r7_package"
    elif source_status == "completion_route_contracts_ready_requires_supplement_and_agent52_export":
        status = "route_work_packages_ready_requires_supplement_and_agent52_export"
    elif source_status == "completion_route_contracts_ready_for_r8p_validation_gates":
        status = "route_work_packages_ready_for_r8p_validation_gates"
    elif "blocked" in source_status:
        status = "route_work_packages_blocked_by_contract_status"
    elif route_contracts:
        status = "route_work_packages_ready_with_contract_status_review"
    else:
        status = "route_work_packages_not_available"
    return {
        "route_work_packages_id": "R8u25_r7_to_r8p_completion_route_work_packages",
        "route_work_packages_path": str(ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGES_PATH),
        "route_work_packages_status": status,
        "source_route_contracts_status": source_status,
        "work_package_count": len(work_packages),
        "open_work_package_count": len(open_work_package_ids),
        "open_work_package_ids": open_work_package_ids,
        "work_packages": work_packages,
        "execution_order": field_rows_r7_completion_route_contracts.get("execution_order", []),
        "technical_feature_mapping": {
            "technical_problem": (
                "Route contracts define producers and gates, but field engineering still needs route-specific submitted "
                "files, required fields, clearance criteria, and non-bypassable evidence boundaries."
            ),
            "technical_means": (
                "The work-package layer converts each R7-to-R8p evidence route into a producer-facing submission contract "
                "with expected files, required table fields, acceptance checks, validation commands, and downstream gates."
            ),
            "technical_effect": (
                "Operators and replay agents can complete missing pressure-resolution evidence through separable work "
                "packages while the grey-box control chain keeps field, operator-reviewed, replay, and validation claims distinct."
            ),
            "prior_art_distinction_candidate": (
                "Unlike a generic data checklist, the work packages bind delayed low-cost sensing, operator review, "
                "offline replay, and validation gates into an auditable route-by-route evidence assembly mechanism."
            ),
        },
        "can_generate_field_evidence_from_work_packages": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }


def _r7_completion_route_work_package(route: dict[str, object]) -> dict[str, object]:
    route_id = str(route.get("route_id", "unknown_route"))
    route_status = str(route.get("route_status", "route_status_unknown"))
    required_fields_by_table = {
        str(table): [str(field) for field in fields if isinstance(field, str)]
        for table, fields in route.get("required_fields_by_table", {}).items()
        if isinstance(fields, list)
    }
    route_specs = _r7_completion_route_work_package_specs()
    spec = route_specs.get(route_id, route_specs["unknown_route"])
    if route_status.startswith("route_clear") or route_status.startswith("route_ready"):
        package_status = f"work_package_clear_{route_id}"
    elif route_status.startswith("route_blocked"):
        package_status = f"work_package_blocked_{route_id}"
    elif route_status.startswith("route_waiting"):
        package_status = f"work_package_open_{route_id}"
    else:
        package_status = f"work_package_review_{route_id}"
    acceptance_checks = list(spec["acceptance_checks"])
    acceptance_checks.extend(
        [
            "must keep can_write_to_actuator false until downstream replay and release gates clear",
            "must keep can_write_to_release_gate false until field/operator/replay evidence is validated",
        ]
    )
    return {
        "work_package_id": f"R8U25_{_safe_patch_token(route_id)}_WORK_PACKAGE",
        "route_id": route_id,
        "work_package_status": package_status,
        "producer": route.get("producer", ""),
        "route_status": route_status,
        "expected_input_files": spec["expected_input_files"],
        "expected_output_files": spec["expected_output_files"],
        "required_completion_item_ids": route.get("required_completion_item_ids", []),
        "required_tables": route.get("required_tables", []),
        "required_fields_by_table": required_fields_by_table,
        "submission_contract": spec["submission_contract"],
        "acceptance_checks": acceptance_checks,
        "validation_command": route.get("validation_command", ""),
        "validation_gates": route.get("validation_gates", []),
        "downstream_consumers": route.get("downstream_consumers", []),
        "evidence_level_after_package": spec["evidence_level_after_package"],
        "failure_boundary": route.get("failure_boundary", ""),
        "can_generate_field_evidence_by_package_only": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }


def _r7_completion_route_work_package_specs() -> dict[str, dict[str, object]]:
    r7_csv_files = [f"{table}.csv" for table in sorted(REQUIRED_TABLE_FIELDS)]
    return {
        "r7_source_package": {
            "expected_input_files": ["metadata.json", *r7_csv_files],
            "expected_output_files": [
                str(ROWS_R7_STAGING_PREFLIGHT_PATH),
                str(ROWS_R7_STAGED_DRAFT_PATH),
            ],
            "submission_contract": (
                "Provide a field-origin R7 package directory through REAL_FIELD_REPLAY_PACKAGE_DIR with metadata.json "
                "and five shared-table CSV files; rows remain candidate field evidence until staging and provenance gates clear."
            ),
            "acceptance_checks": [
                "metadata.data_origin must be field",
                "metadata must include site_id, campaign_id, and collection_window",
                "shared-table CSVs must include batch_id and timestamp/sample time fields where required",
                "template markers and TODO values are rejected",
            ],
            "evidence_level_after_package": "field_candidate_until_r7_staging_and_r8p_schema_gates_clear",
        },
        "operator_supplement": {
            "expected_input_files": [
                "operator_supplement_records.csv",
                "calibration_review_log.csv",
            ],
            "expected_output_files": [
                "pressure_resolution_operator_supplement_rows.json",
                str(ROWS_SCENARIO_SEMANTIC_PREFLIGHT_PATH),
            ],
            "submission_contract": (
                "Provide reviewed operator and calibration records for R8p-only pressure-source resolution fields, including "
                "reviewer identity, review time, pressure source resolution, and calibration basis."
            ),
            "acceptance_checks": [
                "reviewer_id and review_time must be present for operator-reviewed fields",
                "pressure_source_resolution must be explicit, not inferred from default values",
                "calibration_basis must identify the instrument or observation that supports the review",
                "operator supplement rows must keep field/operator provenance separable",
            ],
            "evidence_level_after_package": "operator_reviewed_candidate_until_scenario_semantic_gate_clear",
        },
        "agent52_replay_export": {
            "expected_input_files": [
                "agent52_replay_export_manifest.json",
                "agent52_replay_table.csv",
            ],
            "expected_output_files": [
                "agent52_replay_table.rows.json",
                str(ROWS_DOWNSTREAM_ROUTING_PREFLIGHT_PATH),
            ],
            "submission_contract": (
                "Provide Agent49/52 replay export rows after pressure-source conflict replay, including policy/expert "
                "actions, conflict counters, replay episode identity, and replay evidence provenance."
            ),
            "acceptance_checks": [
                "policy_action_id and expert_action_id must be present",
                "pressure_source_conflict_count must be numeric and replay-derived",
                "replay_episode_id must link back to the same batch/scenario window",
                "R7 field CSVs cannot fabricate replay action or conflict fields",
            ],
            "evidence_level_after_package": "replay_candidate_until_agent52_and_r8v_routing_gates_clear",
        },
        "r8p_validation_gates": {
            "expected_input_files": [
                str(DEFAULT_FIELD_ROWS_PATH),
                str(ROWS_SCHEMA_PATH),
                str(ROWS_R7_COMPLETION_ROUTE_CONTRACTS_PATH),
            ],
            "expected_output_files": [
                str(ROWS_BATCH_BUNDLE_PREFLIGHT_PATH),
                str(ROWS_TEMPORAL_WINDOW_PREFLIGHT_PATH),
                str(ROWS_SCENARIO_SEMANTIC_PREFLIGHT_PATH),
                str(ROWS_DOWNSTREAM_ROUTING_PREFLIGHT_PATH),
            ],
            "submission_contract": (
                "Run Agent61 validation gates over the assembled R8p row package after R7 source, operator supplement, "
                "and Agent52 replay work packages are complete."
            ),
            "acceptance_checks": [
                "all six required tables must be present in the same batch bundle",
                "data_origin must remain field or replay/operator-reviewed as specified by the table contract",
                "temporal-window and hold-time constraints must pass before downstream routing",
                "accepted rows can route forward but cannot directly write actuator or release gates",
            ],
            "evidence_level_after_package": "validated_candidate_until_r8v_agent51_agent49_agent52_and_release_gates_clear",
        },
        "unknown_route": {
            "expected_input_files": [],
            "expected_output_files": [],
            "submission_contract": "Unknown route requires manual review before evidence packaging.",
            "acceptance_checks": ["manual review required"],
            "evidence_level_after_package": "not_evidence_until_route_is_mapped",
        },
    }


def _write_r7_completion_route_work_package_templates(
    field_rows_r7_completion_route_work_packages: dict[str, object],
    template_dir: Path,
) -> dict[str, object]:
    work_packages = [
        package
        for package in field_rows_r7_completion_route_work_packages.get("work_packages", [])
        if isinstance(package, dict)
    ]
    template_dir.mkdir(parents=True, exist_ok=True)
    package_templates = [
        _write_r7_completion_route_work_package_template(package, template_dir)
        for package in work_packages
    ]
    manifest = {
        "route_work_package_templates_id": "R8u26_r7_to_r8p_route_work_package_submission_templates",
        "route_work_package_templates_status": "route_work_package_templates_ready_not_evidence",
        "template_dir": str(template_dir),
        "work_package_template_count": len(package_templates),
        "package_templates": package_templates,
        "submission_env_var": "R7_TO_R8P_WORK_PACKAGE_DIR",
        "submission_preflight_command": (
            f"R7_TO_R8P_WORK_PACKAGE_DIR={template_dir} "
            ".venv/bin/python experiments/run_agent61_pressure_resolution_replay_scenario_pack.py"
        ),
        "template_boundary": (
            "These package directories are fillable submission templates. They intentionally contain TODO/header-only "
            "placeholders and cannot create field, operator-reviewed, replay, actuator, or release-gate evidence."
        ),
        "can_generate_field_evidence_from_templates": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }
    (template_dir / "work_package_template_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return manifest


def _write_r7_completion_route_work_package_template(
    package: dict[str, object],
    template_dir: Path,
) -> dict[str, object]:
    work_package_id = str(package.get("work_package_id", "UNKNOWN_WORK_PACKAGE"))
    package_dir = template_dir / work_package_id
    package_dir.mkdir(parents=True, exist_ok=True)
    manifest_payload = {
        "work_package_id": work_package_id,
        "route_id": package.get("route_id", ""),
        "producer": package.get("producer", ""),
        "submission_contract": package.get("submission_contract", ""),
        "evidence_level_after_package": package.get("evidence_level_after_package", ""),
        "data_origin": "TODO_REPLACE_WITH_FIELD_OPERATOR_OR_REPLAY_ORIGIN",
        "submission_status": "template_only_not_evidence",
        "evidence_boundary": (
            "Fill this package with real source/operator/replay values and rerun Agent61 preflight. "
            "This template is not field evidence."
        ),
    }
    (package_dir / "submission_manifest.json").write_text(
        json.dumps(manifest_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    file_templates: list[dict[str, object]] = []
    for expected_file in _work_package_relative_submission_files(package):
        file_path = package_dir / expected_file
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if expected_file.endswith(".csv"):
            headers = _work_package_submission_file_headers(package, expected_file)
            with file_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=headers)
                writer.writeheader()
            file_templates.append(
                {
                    "file": expected_file,
                    "path": str(file_path),
                    "format": "csv_header_only_template",
                    "headers": headers,
                    "row_count": 0,
                    "template_boundary": "Header-only CSV must be populated with real rows before preflight can pass.",
                }
            )
        elif expected_file.endswith(".json"):
            payload = _work_package_json_template_payload(package, expected_file)
            file_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            file_templates.append(
                {
                    "file": expected_file,
                    "path": str(file_path),
                    "format": "json_template",
                    "template_boundary": "JSON template contains TODO provenance and must be replaced before evidence gates.",
                }
            )
        else:
            file_path.write_text("TODO_REPLACE_WITH_REAL_SUBMISSION_CONTENT\n", encoding="utf-8")
            file_templates.append(
                {
                    "file": expected_file,
                    "path": str(file_path),
                    "format": "text_template",
                    "template_boundary": "Text template is not evidence until replaced and reviewed.",
                }
            )
    return {
        "work_package_id": work_package_id,
        "route_id": package.get("route_id", ""),
        "template_package_dir": str(package_dir),
        "relative_submission_files": _work_package_relative_submission_files(package),
        "project_dependency_files": _work_package_project_dependency_files(package),
        "file_templates": file_templates,
        "can_generate_field_evidence_from_template": False,
    }


def _field_rows_r7_completion_route_work_package_submission_preflight(
    field_rows_r7_completion_route_work_packages: dict[str, object],
    submission_dir: Path | None,
) -> dict[str, object]:
    work_packages = [
        package
        for package in field_rows_r7_completion_route_work_packages.get("work_packages", [])
        if isinstance(package, dict)
    ]
    base = {
        "route_work_package_preflight_id": "R8u26_r7_to_r8p_route_work_package_submission_preflight",
        "route_work_package_preflight_path": str(ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_PREFLIGHT_PATH),
        "submission_env_var": "R7_TO_R8P_WORK_PACKAGE_DIR",
        "configured_submission_dir": str(submission_dir) if submission_dir else "",
        "expected_work_package_count": len(work_packages),
        "can_generate_field_evidence_from_preflight": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }
    if submission_dir is None:
        return {
            **base,
            "route_work_package_preflight_status": "route_work_package_preflight_waiting_for_submission_dir",
            "submitted_work_package_count": 0,
            "passed_work_package_count": 0,
            "blocked_work_package_count": len(work_packages),
            "missing_work_package_ids": [str(package.get("work_package_id", "")) for package in work_packages],
            "package_preflights": [],
            "preflight_boundary": (
                "No R7_TO_R8P_WORK_PACKAGE_DIR was supplied. Generated templates are not evidence."
            ),
        }
    if not submission_dir.exists():
        return {
            **base,
            "route_work_package_preflight_status": "route_work_package_preflight_invalid_submission_dir",
            "submitted_work_package_count": 0,
            "passed_work_package_count": 0,
            "blocked_work_package_count": len(work_packages),
            "missing_work_package_ids": [str(package.get("work_package_id", "")) for package in work_packages],
            "package_preflights": [],
            "preflight_boundary": "Configured submission directory does not exist.",
        }
    if not submission_dir.is_dir():
        return {
            **base,
            "route_work_package_preflight_status": "route_work_package_preflight_submission_path_not_directory",
            "submitted_work_package_count": 0,
            "passed_work_package_count": 0,
            "blocked_work_package_count": len(work_packages),
            "missing_work_package_ids": [str(package.get("work_package_id", "")) for package in work_packages],
            "package_preflights": [],
            "preflight_boundary": "Configured submission path must be a directory containing work package subdirectories.",
        }
    package_preflights = [
        _r7_completion_route_work_package_submission_preflight_item(package, submission_dir)
        for package in work_packages
    ]
    passed = [
        item for item in package_preflights if item["package_preflight_status"] == "submission_package_preflight_passed_candidate"
    ]
    blocked = [item for item in package_preflights if item not in passed]
    missing_work_package_ids = [
        str(item["work_package_id"])
        for item in package_preflights
        if item["package_preflight_status"] == "submission_package_missing"
    ]
    status = (
        "route_work_package_preflight_passed_candidate_submission"
        if len(passed) == len(work_packages)
        else "route_work_package_preflight_blocked_submission_gaps"
    )
    return {
        **base,
        "route_work_package_preflight_status": status,
        "submitted_work_package_count": len(package_preflights) - len(missing_work_package_ids),
        "passed_work_package_count": len(passed),
        "blocked_work_package_count": len(blocked),
        "missing_work_package_ids": missing_work_package_ids,
        "missing_file_count": sum(int(item.get("missing_file_count", 0)) for item in package_preflights),
        "csv_header_gap_count": sum(int(item.get("csv_header_gap_count", 0)) for item in package_preflights),
        "empty_csv_count": sum(int(item.get("empty_csv_count", 0)) for item in package_preflights),
        "json_error_count": sum(int(item.get("json_error_count", 0)) for item in package_preflights),
        "template_marker_count": sum(int(item.get("template_marker_count", 0)) for item in package_preflights),
        "metadata_provenance_gap_count": sum(
            int(item.get("metadata_provenance_gap_count", 0)) for item in package_preflights
        ),
        "package_preflights": package_preflights,
        "preflight_boundary": (
            "Passing work-package preflight only means submission files are candidate-complete. It does not bypass "
            "R7 import, R8p schema/provenance/semantic gates, R8v routing, field holdout, actuator, or release gates."
        ),
    }


def _field_rows_r7_completion_route_work_package_patch_plan(
    route_work_package_preflight: dict[str, object],
) -> dict[str, object]:
    status = str(route_work_package_preflight.get("route_work_package_preflight_status", ""))
    patch_items: list[dict[str, object]] = []
    configured_submission_dir = str(route_work_package_preflight.get("configured_submission_dir", ""))
    expected_count = int(route_work_package_preflight.get("expected_work_package_count", 0) or 0)
    if status == "route_work_package_preflight_waiting_for_submission_dir":
        patch_items.append(
            {
                "patch_id": "R8U27_SET_R7_TO_R8P_WORK_PACKAGE_DIR",
                "priority": "P0",
                "patch_type": "submission_source_preflight",
                "blocking_condition": "missing_submission_dir",
                "target_work_package_id": "ALL_OPEN_R7_TO_R8P_WORK_PACKAGES",
                "operator_action": (
                    "Copy the generated work-package templates to a real submission directory, replace all TODO/header-only "
                    "content with field/operator/replay values, set R7_TO_R8P_WORK_PACKAGE_DIR to that directory, and rerun Agent61."
                ),
                "acceptance_check": (
                    "R7_TO_R8P_WORK_PACKAGE_DIR must point to an existing directory containing every expected work-package "
                    "subdirectory before package-level preflight can evaluate evidence gaps."
                ),
                "technical_feature_mapping": [
                    "field package evidence gate",
                    "operator-reviewed route submission",
                    "template is not evidence boundary",
                ],
                "failure_boundary": "No package can become field evidence until a real submission directory is supplied.",
            }
        )
        plan_status = "route_work_package_patch_plan_waiting_for_submission_dir"
    elif status == "route_work_package_preflight_invalid_submission_dir":
        patch_items.append(
            {
                "patch_id": "R8U27_FIX_MISSING_R7_TO_R8P_WORK_PACKAGE_DIR",
                "priority": "P0",
                "patch_type": "submission_source_preflight",
                "blocking_condition": "configured_submission_dir_missing",
                "target_work_package_id": "ALL_OPEN_R7_TO_R8P_WORK_PACKAGES",
                "operator_action": (
                    f"Create or correct the configured R7_TO_R8P_WORK_PACKAGE_DIR path: {configured_submission_dir or 'not_set'}."
                ),
                "acceptance_check": "Configured submission path exists and contains work-package subdirectories.",
                "technical_feature_mapping": ["field package evidence gate", "site submission path contract"],
                "failure_boundary": "A missing path cannot be inferred or auto-filled by synthetic/template data.",
            }
        )
        plan_status = "route_work_package_patch_plan_blocked_at_submission_path"
    elif status == "route_work_package_preflight_submission_path_not_directory":
        patch_items.append(
            {
                "patch_id": "R8U27_REPLACE_FILE_WITH_WORK_PACKAGE_DIR",
                "priority": "P0",
                "patch_type": "submission_source_preflight",
                "blocking_condition": "configured_submission_path_not_directory",
                "target_work_package_id": "ALL_OPEN_R7_TO_R8P_WORK_PACKAGES",
                "operator_action": (
                    f"Replace the configured file path with a directory containing work packages: {configured_submission_dir}."
                ),
                "acceptance_check": "Configured path is a directory, not a file.",
                "technical_feature_mapping": ["field package evidence gate", "submission directory contract"],
                "failure_boundary": "A single file cannot satisfy multi-route R7-to-R8p work-package submission.",
            }
        )
        plan_status = "route_work_package_patch_plan_blocked_at_submission_path"
    elif status == "route_work_package_preflight_passed_candidate_submission":
        plan_status = "route_work_package_patch_plan_clear_for_r8p_gate_submission_review"
    elif status == "route_work_package_preflight_blocked_submission_gaps":
        for package_preflight in route_work_package_preflight.get("package_preflights", []):
            if isinstance(package_preflight, dict):
                patch_items.extend(_r7_completion_route_work_package_preflight_patch_items(package_preflight))
        plan_status = "route_work_package_patch_plan_ready_for_submission_repairs"
    else:
        patch_items.append(
            {
                "patch_id": "R8U27_REVIEW_UNKNOWN_WORK_PACKAGE_PREFLIGHT_STATUS",
                "priority": "P1",
                "patch_type": "preflight_status_review",
                "blocking_condition": status or "missing_preflight_status",
                "target_work_package_id": "ALL_OPEN_R7_TO_R8P_WORK_PACKAGES",
                "operator_action": "Review Agent61 work-package preflight output before routing any candidate evidence forward.",
                "acceptance_check": "Preflight status is mapped to a known pass/block/waiting state.",
                "technical_feature_mapping": ["evidence governance", "preflight status boundary"],
                "failure_boundary": "Unknown preflight status cannot authorize field replay routing.",
            }
        )
        plan_status = "route_work_package_patch_plan_review_required"
    sorted_items = sorted(
        patch_items,
        key=lambda item: (
            {"P0": 0, "P1": 1, "P2": 2, "P3": 3}.get(str(item.get("priority", "P3")), 3),
            str(item.get("patch_id", "")),
        ),
    )
    type_counts: dict[str, int] = {}
    for item in sorted_items:
        patch_type = str(item.get("patch_type", "unknown_patch_type"))
        type_counts[patch_type] = type_counts.get(patch_type, 0) + 1
    highest_priority_patch_id = str(sorted_items[0]["patch_id"]) if sorted_items else ""
    return {
        "route_work_package_patch_plan_id": "R8u27_r7_to_r8p_route_work_package_preflight_patch_plan",
        "route_work_package_patch_plan_path": str(ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_PATCH_PLAN_PATH),
        "route_work_package_patch_plan_status": plan_status,
        "source_preflight_status": status or "route_work_package_preflight_missing",
        "configured_submission_dir": configured_submission_dir,
        "expected_work_package_count": expected_count,
        "patch_item_count": len(sorted_items),
        "highest_priority_patch_id": highest_priority_patch_id,
        "patch_item_type_counts": type_counts,
        "patch_items": sorted_items,
        "next_operator_action": (
            sorted_items[0]["operator_action"] if sorted_items else "Run R8p schema/provenance/semantic gates on the candidate submission."
        ),
        "can_generate_field_evidence_from_patch_plan": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "patch_plan_boundary": (
            "This patch plan converts preflight blockers into operator-repair tasks only. It is not field evidence, does not "
            "replace R7 import, and cannot bypass R8p/R8v/holdout/release gates."
        ),
    }


def _field_rows_r7_completion_route_work_package_assembly_gate(
    route_work_package_preflight: dict[str, object],
    route_work_package_patch_plan: dict[str, object],
) -> dict[str, object]:
    preflight_status = str(route_work_package_preflight.get("route_work_package_preflight_status", ""))
    patch_plan_status = str(route_work_package_patch_plan.get("route_work_package_patch_plan_status", ""))
    highest_patch_id = str(route_work_package_patch_plan.get("highest_priority_patch_id", ""))
    configured_submission_dir = str(route_work_package_preflight.get("configured_submission_dir", ""))
    if preflight_status == "route_work_package_preflight_passed_candidate_submission":
        gate_status = "route_work_package_assembly_gate_candidate_ready_needs_rows_materialization"
        readiness_mode = "candidate_ready"
    elif preflight_status == "route_work_package_preflight_waiting_for_submission_dir":
        gate_status = "route_work_package_assembly_gate_blocked_waiting_for_submission_dir"
        readiness_mode = "waiting_for_submission_dir"
    elif preflight_status in {
        "route_work_package_preflight_invalid_submission_dir",
        "route_work_package_preflight_submission_path_not_directory",
    }:
        gate_status = "route_work_package_assembly_gate_blocked_at_submission_path"
        readiness_mode = "submission_path_blocked"
    elif preflight_status == "route_work_package_preflight_blocked_submission_gaps":
        gate_status = "route_work_package_assembly_gate_blocked_by_work_package_repairs"
        readiness_mode = "repair_blocked"
    else:
        gate_status = "route_work_package_assembly_gate_review_required"
        readiness_mode = "review_required"
    assembly_steps = _r7_completion_route_work_package_assembly_steps(
        readiness_mode,
        highest_patch_id,
    )
    ready_steps = [step for step in assembly_steps if step["assembly_step_status"].startswith("assembly_step_ready")]
    blocked_steps = [
        step
        for step in assembly_steps
        if step["assembly_step_status"].startswith(("assembly_step_blocked", "assembly_step_review"))
    ]
    next_assembly_action = (
        blocked_steps[0]["operator_action"]
        if blocked_steps
        else "Materialize the candidate R8p rows package, set PRESSURE_RESOLUTION_REPLAY_ROWS_PATH to it, and rerun Agent61 gates."
    )
    return {
        "route_work_package_assembly_gate_id": "R8u28_r7_to_r8p_route_work_package_assembly_gate",
        "route_work_package_assembly_gate_path": str(ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_ASSEMBLY_GATE_PATH),
        "route_work_package_assembly_gate_status": gate_status,
        "source_preflight_status": preflight_status or "route_work_package_preflight_missing",
        "source_patch_plan_status": patch_plan_status or "route_work_package_patch_plan_missing",
        "configured_submission_dir": configured_submission_dir,
        "assembly_step_count": len(assembly_steps),
        "ready_assembly_step_count": len(ready_steps),
        "blocked_assembly_step_count": len(blocked_steps),
        "highest_priority_patch_id": highest_patch_id,
        "next_assembly_action": next_assembly_action,
        "assembly_steps": assembly_steps,
        "candidate_rows_package_path": str(DEFAULT_FIELD_ROWS_PATH),
        "candidate_rows_package_format": "json_table_mapping_or_metadata_plus_six_csv_directory",
        "required_env_after_materialization": "PRESSURE_RESOLUTION_REPLAY_ROWS_PATH",
        "technical_feature_mapping": {
            "technical_problem": (
                "Route-specific work packages can pass file preflight but still need a deterministic, auditable order for "
                "turning R7 field rows, operator review, and Agent52 replay export into a single R8p rows package."
            ),
            "technical_means": (
                "The assembly gate defines the ordered route-to-rows merge sequence, required input packages, output "
                "artifacts, rerun commands, and non-bypassable evidence gates before any field replay/control claim."
            ),
            "technical_effect": (
                "The system can accept low-cost delayed field submissions without manually guessing merge order, while "
                "keeping field, operator-reviewed, replay, and validation evidence boundaries explicit."
            ),
            "prior_art_distinction_candidate": (
                "Unlike a generic ETL step, this gate ties sparse-sensing field packages, delayed operator review, "
                "offline replay export, and grey-box control validation into a staged evidence assembly mechanism."
            ),
        },
        "can_materialize_candidate_rows_package": readiness_mode == "candidate_ready",
        "can_generate_field_evidence_from_assembly_gate": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "assembly_gate_boundary": (
            "This assembly gate only defines when candidate R8p rows can be materialized from submitted work packages. "
            "It does not prove field validity, does not replace R8p/R8v gates, and cannot authorize actuator or release decisions."
        ),
    }


def _r7_completion_route_work_package_assembly_steps(
    readiness_mode: str,
    highest_patch_id: str,
) -> list[dict[str, object]]:
    route_steps = [
        {
            "assembly_step_id": "R8U28_VALIDATE_WORK_PACKAGE_SUBMISSION",
            "sequence": 1,
            "required_work_package_ids": [
                "R8U25_R7_SOURCE_PACKAGE_WORK_PACKAGE",
                "R8U25_OPERATOR_SUPPLEMENT_WORK_PACKAGE",
                "R8U25_AGENT52_REPLAY_EXPORT_WORK_PACKAGE",
                "R8U25_R8P_VALIDATION_GATES_WORK_PACKAGE",
            ],
            "required_input_artifacts": ["R7_TO_R8P_WORK_PACKAGE_DIR"],
            "output_artifact": str(ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_PREFLIGHT_PATH),
            "operator_action": "Submit a complete R7_TO_R8P_WORK_PACKAGE_DIR and rerun Agent61 work-package preflight.",
            "acceptance_check": "route_work_package_preflight_status must be route_work_package_preflight_passed_candidate_submission.",
        },
        {
            "assembly_step_id": "R8U28_STAGE_R7_SOURCE_PACKAGE_ROWS",
            "sequence": 2,
            "required_work_package_ids": ["R8U25_R7_SOURCE_PACKAGE_WORK_PACKAGE"],
            "required_input_artifacts": ["metadata.json", "five shared R7 CSV files"],
            "output_artifact": str(ROWS_R7_STAGED_DRAFT_PATH),
            "operator_action": "Convert field-origin R7 shared tables into R8p staged draft rows and preserve provenance columns.",
            "acceptance_check": "R7 staged draft exists with direct/alias/metadata-copy provenance and no template markers.",
        },
        {
            "assembly_step_id": "R8U28_MERGE_OPERATOR_SUPPLEMENT_ROWS",
            "sequence": 3,
            "required_work_package_ids": ["R8U25_OPERATOR_SUPPLEMENT_WORK_PACKAGE"],
            "required_input_artifacts": ["operator_supplement_records.csv", "calibration_review_log.csv"],
            "output_artifact": "pressure_resolution_operator_supplement_rows.json",
            "operator_action": "Merge reviewer, calibration, pressure-source resolution, and manual hold/release context into staged rows.",
            "acceptance_check": "All operator supplement fields have reviewer/calibration provenance and join to scenario batch_id.",
        },
        {
            "assembly_step_id": "R8U28_MERGE_AGENT52_REPLAY_EXPORT",
            "sequence": 4,
            "required_work_package_ids": ["R8U25_AGENT52_REPLAY_EXPORT_WORK_PACKAGE"],
            "required_input_artifacts": ["agent52_replay_export_manifest.json", "agent52_replay_table.csv"],
            "output_artifact": "agent52_replay_table.rows.json",
            "operator_action": "Merge replay episode, policy/expert action, conflict counter, and clearance evidence into R8p rows.",
            "acceptance_check": "Agent52 replay rows link to the same batch/scenario windows and remain replay-origin evidence.",
        },
        {
            "assembly_step_id": "R8U28_MATERIALIZE_R8P_ROWS_PACKAGE",
            "sequence": 5,
            "required_work_package_ids": [
                "R8U25_R7_SOURCE_PACKAGE_WORK_PACKAGE",
                "R8U25_OPERATOR_SUPPLEMENT_WORK_PACKAGE",
                "R8U25_AGENT52_REPLAY_EXPORT_WORK_PACKAGE",
            ],
            "required_input_artifacts": ["staged draft rows", "operator supplement rows", "agent52 replay rows"],
            "output_artifact": str(DEFAULT_FIELD_ROWS_PATH),
            "operator_action": "Materialize a candidate R8p rows JSON/table directory package and point PRESSURE_RESOLUTION_REPLAY_ROWS_PATH to it.",
            "acceptance_check": "Candidate package contains six required tables plus agent52_replay_table with source/origin columns intact.",
        },
        {
            "assembly_step_id": "R8U28_RERUN_R8P_AND_R8V_VALIDATION_GATES",
            "sequence": 6,
            "required_work_package_ids": ["R8U25_R8P_VALIDATION_GATES_WORK_PACKAGE"],
            "required_input_artifacts": [
                str(ROWS_SCHEMA_PATH),
                str(ROWS_BATCH_BUNDLE_PREFLIGHT_PATH),
                str(ROWS_TEMPORAL_WINDOW_PREFLIGHT_PATH),
                str(ROWS_SCENARIO_SEMANTIC_PREFLIGHT_PATH),
                str(ROWS_DOWNSTREAM_ROUTING_PREFLIGHT_PATH),
            ],
            "output_artifact": str(METRICS_PATH),
            "operator_action": "Rerun Agent61 with the candidate rows package and review R8p/R8v gates before routing to field replay.",
            "acceptance_check": "R8p schema/provenance/template/bundle/temporal/semantic gates and R8v routing preflight must pass.",
        },
    ]
    if readiness_mode == "candidate_ready":
        return [
            {
                **step,
                "assembly_step_status": "assembly_step_ready_candidate_pending_validation"
                if step["sequence"] < 6
                else "assembly_step_ready_candidate_requires_gate_rerun",
                "blocking_patch_id": "",
            }
            for step in route_steps
        ]
    if readiness_mode == "waiting_for_submission_dir":
        status = "assembly_step_blocked_waiting_for_submission_dir"
    elif readiness_mode == "submission_path_blocked":
        status = "assembly_step_blocked_at_submission_path"
    elif readiness_mode == "repair_blocked":
        status = "assembly_step_blocked_by_work_package_repairs"
    else:
        status = "assembly_step_review_required"
    return [
        {
            **step,
            "assembly_step_status": status,
            "blocking_patch_id": highest_patch_id,
        }
        for step in route_steps
    ]


def _r7_completion_route_work_package_preflight_patch_items(
    package_preflight: dict[str, object],
) -> list[dict[str, object]]:
    work_package_id = str(package_preflight.get("work_package_id", "UNKNOWN_WORK_PACKAGE"))
    route_id = str(package_preflight.get("route_id", "unknown_route"))
    package_status = str(package_preflight.get("package_preflight_status", ""))
    package_dir = str(package_preflight.get("package_dir", ""))
    if package_status == "submission_package_missing":
        return [
            {
                "patch_id": f"R8U27_{_safe_patch_token(work_package_id)}_CREATE_PACKAGE_DIR",
                "priority": "P0",
                "patch_type": "missing_work_package_dir",
                "blocking_condition": "submission_package_missing",
                "target_work_package_id": work_package_id,
                "target_route_id": route_id,
                "target_path": package_dir,
                "operator_action": (
                    "Create the missing work-package directory and populate all expected files from real field/operator/replay sources."
                ),
                "acceptance_check": "Package directory exists and every expected file is present before package preflight runs.",
                "technical_feature_mapping": ["route-specific evidence package", "field package import readiness"],
                "failure_boundary": "Missing package directories block all downstream evidence routing.",
            }
        ]
    if package_status == "submission_package_waiting_for_project_dependencies":
        return [
            {
                "patch_id": f"R8U27_{_safe_patch_token(work_package_id)}_SATISFY_PROJECT_DEPENDENCIES",
                "priority": "P0",
                "patch_type": "project_dependency_gate",
                "blocking_condition": "submission_package_waiting_for_project_dependencies",
                "target_work_package_id": work_package_id,
                "target_route_id": route_id,
                "project_dependency_files": package_preflight.get("project_dependency_files", []),
                "operator_action": (
                    "Assemble upstream project outputs and rerun Agent61/R8p validation gates instead of submitting an empty package."
                ),
                "acceptance_check": "Project dependency files exist, are current, and R8p validation gates rerun on accepted rows.",
                "technical_feature_mapping": ["replay validation gate", "source-to-control evidence propagation"],
                "failure_boundary": "Project dependency routes cannot pass from empty folders or template placeholders.",
            }
        ]
    patch_items: list[dict[str, object]] = []
    for file_preflight in package_preflight.get("file_preflights", []):
        if isinstance(file_preflight, dict):
            patch_items.extend(
                _r7_completion_route_work_package_file_patch_items(
                    work_package_id,
                    route_id,
                    file_preflight,
                )
            )
    return patch_items


def _r7_completion_route_work_package_file_patch_items(
    work_package_id: str,
    route_id: str,
    file_preflight: dict[str, object],
) -> list[dict[str, object]]:
    file_name = str(file_preflight.get("file", "unknown_file"))
    file_status = str(file_preflight.get("file_status", ""))
    token = f"R8U27_{_safe_patch_token(work_package_id)}_{_safe_patch_token(file_name)}"
    patch_items: list[dict[str, object]] = []
    if file_status == "missing_file":
        patch_items.append(
            {
                "patch_id": f"{token}_ADD_MISSING_FILE",
                "priority": "P0",
                "patch_type": "missing_submission_file",
                "blocking_condition": "missing_file",
                "target_work_package_id": work_package_id,
                "target_route_id": route_id,
                "target_file": file_name,
                "operator_action": "Add the missing file using real field/operator/replay data, not generated placeholder values.",
                "acceptance_check": "File exists and passes format/header/provenance preflight.",
                "technical_feature_mapping": ["route-specific evidence package", "field package completeness"],
                "failure_boundary": "Missing files cannot be inferred from other tables or synthetic baselines.",
            }
        )
    missing_headers = [str(header) for header in file_preflight.get("missing_headers", [])]
    if missing_headers:
        patch_items.append(
            {
                "patch_id": f"{token}_ADD_REQUIRED_HEADERS",
                "priority": "P0",
                "patch_type": "csv_header_contract",
                "blocking_condition": "required_headers_missing",
                "target_work_package_id": work_package_id,
                "target_route_id": route_id,
                "target_file": file_name,
                "missing_headers": missing_headers,
                "operator_action": f"Add required CSV headers: {', '.join(missing_headers)}.",
                "acceptance_check": "CSV header contains every required field in the package contract.",
                "technical_feature_mapping": ["schema contract", "R8p acceptance gate"],
                "failure_boundary": "Rows without required columns cannot enter replay/holdout gates.",
            }
        )
    if file_preflight.get("format") == "csv" and int(file_preflight.get("row_count", 0) or 0) == 0:
        patch_items.append(
            {
                "patch_id": f"{token}_POPULATE_ROWS",
                "priority": "P0",
                "patch_type": "empty_csv_rows",
                "blocking_condition": "csv_header_only_or_empty",
                "target_work_package_id": work_package_id,
                "target_route_id": route_id,
                "target_file": file_name,
                "operator_action": "Populate the CSV with real rows that share batch_id/sample_time links with the scenario bundle.",
                "acceptance_check": "CSV has at least one non-template row and can join to required scenario/batch context.",
                "technical_feature_mapping": ["field replay row evidence", "temporal bundle readiness"],
                "failure_boundary": "Header-only CSV templates are collection aids, not field evidence.",
            }
        )
    if file_status == "invalid_json":
        patch_items.append(
            {
                "patch_id": f"{token}_FIX_JSON",
                "priority": "P0",
                "patch_type": "invalid_json",
                "blocking_condition": str(file_preflight.get("json_error", "invalid_json")),
                "target_work_package_id": work_package_id,
                "target_route_id": route_id,
                "target_file": file_name,
                "operator_action": "Repair JSON syntax and preserve required provenance fields.",
                "acceptance_check": "JSON parses and contains no template markers or provenance gaps.",
                "technical_feature_mapping": ["metadata provenance gate", "source package contract"],
                "failure_boundary": "Invalid JSON cannot be reviewed as source metadata.",
            }
        )
    template_marker_count = int(file_preflight.get("template_marker_count", 0) or 0)
    if template_marker_count:
        patch_items.append(
            {
                "patch_id": f"{token}_REMOVE_TEMPLATE_MARKERS",
                "priority": "P0",
                "patch_type": "template_marker_replacement",
                "blocking_condition": "template_marker_values_present",
                "target_work_package_id": work_package_id,
                "target_route_id": route_id,
                "target_file": file_name,
                "template_marker_count": template_marker_count,
                "operator_action": "Replace TODO/template marker values with traceable real field/operator/replay values.",
                "acceptance_check": "No TODO/template placeholder values remain in the file.",
                "technical_feature_mapping": ["template-not-evidence boundary", "operator-reviewed evidence source"],
                "failure_boundary": "Template markers make the package non-evidence even if file shape is valid.",
            }
        )
    metadata_gap_count = int(file_preflight.get("metadata_provenance_gap_count", 0) or 0)
    if metadata_gap_count:
        patch_items.append(
            {
                "patch_id": f"{token}_FIX_PROVENANCE",
                "priority": "P0",
                "patch_type": "metadata_provenance",
                "blocking_condition": "metadata_data_origin_not_field",
                "target_work_package_id": work_package_id,
                "target_route_id": route_id,
                "target_file": file_name,
                "metadata_provenance_gap_count": metadata_gap_count,
                "operator_action": "Set metadata provenance to a real field origin and attach source/collection context.",
                "acceptance_check": "metadata.json has data_origin=field and source context suitable for R7/R8p review.",
                "technical_feature_mapping": ["field origin gate", "claim evidence boundary"],
                "failure_boundary": "Non-field metadata cannot upgrade package claims to field-supported evidence.",
            }
        )
    return patch_items


def _r7_completion_route_work_package_submission_preflight_item(
    package: dict[str, object],
    submission_dir: Path,
) -> dict[str, object]:
    work_package_id = str(package.get("work_package_id", "UNKNOWN_WORK_PACKAGE"))
    package_dir = submission_dir / work_package_id
    relative_files = _work_package_relative_submission_files(package)
    if not package_dir.exists():
        return {
            "work_package_id": work_package_id,
            "route_id": package.get("route_id", ""),
            "package_dir": str(package_dir),
            "package_preflight_status": "submission_package_missing",
            "missing_file_count": len(relative_files),
            "missing_files": relative_files,
            "csv_header_gap_count": 0,
            "empty_csv_count": 0,
            "json_error_count": 0,
            "template_marker_count": 0,
            "metadata_provenance_gap_count": 0,
            "file_preflights": [],
        }
    if not relative_files and _work_package_project_dependency_files(package):
        return {
            "work_package_id": work_package_id,
            "route_id": package.get("route_id", ""),
            "package_dir": str(package_dir),
            "package_preflight_status": "submission_package_waiting_for_project_dependencies",
            "missing_file_count": 0,
            "missing_files": [],
            "csv_header_gap_count": 0,
            "empty_csv_count": 0,
            "json_error_count": 0,
            "template_marker_count": 0,
            "metadata_provenance_gap_count": 0,
            "project_dependency_files": _work_package_project_dependency_files(package),
            "file_preflights": [],
            "package_boundary": (
                "This work package is satisfied by upstream project outputs and validation gates, not by an empty "
                "submission directory. It cannot pass until upstream evidence packages are assembled and Agent61 gates run."
            ),
        }
    file_preflights = [
        _r7_completion_route_work_package_file_preflight(package, package_dir, expected_file)
        for expected_file in relative_files
    ]
    missing_file_count = sum(1 for item in file_preflights if item["file_status"] == "missing_file")
    csv_header_gap_count = sum(len(item.get("missing_headers", [])) for item in file_preflights)
    empty_csv_count = sum(1 for item in file_preflights if item.get("row_count") == 0 and item.get("format") == "csv")
    json_error_count = sum(1 for item in file_preflights if item["file_status"] == "invalid_json")
    template_marker_count = sum(int(item.get("template_marker_count", 0)) for item in file_preflights)
    metadata_provenance_gap_count = sum(int(item.get("metadata_provenance_gap_count", 0)) for item in file_preflights)
    if any(
        [
            missing_file_count,
            csv_header_gap_count,
            empty_csv_count,
            json_error_count,
            template_marker_count,
            metadata_provenance_gap_count,
        ]
    ):
        status = "submission_package_incomplete"
    else:
        status = "submission_package_preflight_passed_candidate"
    return {
        "work_package_id": work_package_id,
        "route_id": package.get("route_id", ""),
        "package_dir": str(package_dir),
        "package_preflight_status": status,
        "missing_file_count": missing_file_count,
        "missing_files": [item["file"] for item in file_preflights if item["file_status"] == "missing_file"],
        "csv_header_gap_count": csv_header_gap_count,
        "empty_csv_count": empty_csv_count,
        "json_error_count": json_error_count,
        "template_marker_count": template_marker_count,
        "metadata_provenance_gap_count": metadata_provenance_gap_count,
        "file_preflights": file_preflights,
    }


def _r7_completion_route_work_package_file_preflight(
    package: dict[str, object],
    package_dir: Path,
    expected_file: str,
) -> dict[str, object]:
    file_path = package_dir / expected_file
    if not file_path.exists():
        return {
            "file": expected_file,
            "path": str(file_path),
            "file_status": "missing_file",
            "format": "unknown",
            "missing_headers": _work_package_submission_file_headers(package, expected_file)
            if expected_file.endswith(".csv")
            else [],
        }
    if expected_file.endswith(".csv"):
        rows, invalid_shapes, header = _read_field_rows_csv_table(file_path)
        required_headers = _work_package_submission_file_headers(package, expected_file)
        missing_headers = [field for field in required_headers if field not in header]
        template_marker_count = sum(
            1
            for row in rows
            for value in row.values()
            if _contains_template_marker_value(value)
        )
        return {
            "file": expected_file,
            "path": str(file_path),
            "file_status": "csv_preflight_passed" if not missing_headers and rows and not template_marker_count else "csv_preflight_gaps",
            "format": "csv",
            "row_count": len(rows),
            "header": header,
            "missing_headers": missing_headers,
            "invalid_shapes": invalid_shapes,
            "template_marker_count": template_marker_count,
        }
    if expected_file.endswith(".json"):
        try:
            payload = json.loads(file_path.read_text(encoding="utf-8"))
        except JSONDecodeError as exc:
            return {
                "file": expected_file,
                "path": str(file_path),
                "file_status": "invalid_json",
                "format": "json",
                "json_error": exc.msg,
            }
        template_marker_count = _json_template_marker_count(payload)
        metadata_provenance_gap_count = (
            1
            if expected_file == "metadata.json"
            and (not isinstance(payload, dict) or str(payload.get("data_origin", "")).lower() != "field")
            else 0
        )
        return {
            "file": expected_file,
            "path": str(file_path),
            "file_status": (
                "json_preflight_passed"
                if isinstance(payload, dict) and not template_marker_count and not metadata_provenance_gap_count
                else "json_preflight_gaps"
            ),
            "format": "json",
            "template_marker_count": template_marker_count,
            "metadata_provenance_gap_count": metadata_provenance_gap_count,
        }
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    marker_count = 1 if _contains_template_marker_value(text) else 0
    return {
        "file": expected_file,
        "path": str(file_path),
        "file_status": "text_preflight_passed" if text.strip() and not marker_count else "text_preflight_gaps",
        "format": "text",
        "template_marker_count": marker_count,
    }


def _work_package_relative_submission_files(package: dict[str, object]) -> list[str]:
    return [
        str(path)
        for path in package.get("expected_input_files", [])
        if isinstance(path, str) and path and not Path(path).is_absolute()
    ]


def _work_package_project_dependency_files(package: dict[str, object]) -> list[str]:
    return [
        str(path)
        for path in package.get("expected_input_files", [])
        if isinstance(path, str) and path and Path(path).is_absolute()
    ]


def _work_package_submission_file_headers(package: dict[str, object], expected_file: str) -> list[str]:
    if not expected_file.endswith(".csv"):
        return []
    stem = Path(expected_file).stem
    if stem in REQUIRED_TABLE_FIELDS or stem == "agent52_replay_table":
        return _required_fields_for_table(stem)
    if expected_file == "operator_supplement_records.csv":
        fields = [
            "batch_id",
            "target_table",
            "reviewer_id",
            "review_time",
            "calibration_basis",
            "data_origin",
        ]
        for table_fields in package.get("required_fields_by_table", {}).values():
            if isinstance(table_fields, list):
                for field in table_fields:
                    if isinstance(field, str) and field not in fields:
                        fields.append(field)
        return fields
    if expected_file == "calibration_review_log.csv":
        return [
            "batch_id",
            "instrument_id",
            "calibration_basis",
            "reviewer_id",
            "review_time",
            "data_origin",
        ]
    return ["batch_id", "data_origin"]


def _work_package_json_template_payload(package: dict[str, object], expected_file: str) -> dict[str, object]:
    payload = {
        "work_package_id": package.get("work_package_id", ""),
        "route_id": package.get("route_id", ""),
        "data_origin": "TODO_REPLACE_WITH_REAL_ORIGIN",
        "submission_status": "template_only_not_evidence",
        "evidence_boundary": "Template JSON must be replaced with real submission metadata before preflight can pass.",
    }
    if expected_file == "metadata.json":
        payload.update(
            {
                "site_id": "TODO_REAL_SITE_ID",
                "campaign_id": "TODO_REAL_CAMPAIGN_ID",
                "collection_window": "TODO_REAL_COLLECTION_WINDOW",
                "chain_of_custody_id": "TODO_SIGNED_CHAIN_OF_CUSTODY_ID",
            }
        )
    if expected_file == "agent52_replay_export_manifest.json":
        payload.update(
            {
                "replay_run_id": "TODO_AGENT52_REPLAY_RUN_ID",
                "source_policy_id": "TODO_AGENT49_POLICY_ID",
                "expert_review_basis": "TODO_EXPERT_OR_RULE_BASIS",
            }
        )
    return payload


def _json_template_marker_count(payload: object) -> int:
    if isinstance(payload, dict):
        return sum(_json_template_marker_count(value) for value in payload.values())
    if isinstance(payload, list):
        return sum(_json_template_marker_count(value) for value in payload)
    return 1 if _contains_template_marker_value(payload) else 0


def _contains_template_marker_value(value: object) -> bool:
    text = str(value).strip().lower()
    return any(marker in text for marker in ("todo", "template", "sample", "placeholder"))


def _r7_completion_route_contract(
    *,
    route_id: str,
    route_status: str,
    producer: str,
    required_items: list[dict[str, object]],
    required_tables: list[str],
    input_contract: str,
    output_contract: str,
    validation_gates: list[str],
    validation_command: str,
    downstream_consumers: list[str],
    failure_boundary: str,
) -> dict[str, object]:
    return {
        "route_id": route_id,
        "route_status": route_status,
        "producer": producer,
        "input_contract": input_contract,
        "output_contract": output_contract,
        "required_completion_item_ids": [str(item.get("item_id")) for item in required_items],
        "required_tables": required_tables,
        "required_fields_by_table": _required_fields_by_completion_table(required_items),
        "validation_gates": validation_gates,
        "validation_command": validation_command,
        "downstream_consumers": downstream_consumers,
        "failure_boundary": failure_boundary,
        "can_generate_field_evidence_by_route_only": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }


def _required_fields_by_completion_table(required_items: list[dict[str, object]]) -> dict[str, list[str]]:
    fields_by_table: dict[str, list[str]] = {}
    for item in required_items:
        table = str(item.get("target_table", ""))
        if not table:
            continue
        fields = [str(field) for field in item.get("target_fields", []) if isinstance(field, str)]
        fields_by_table.setdefault(table, [])
        for field in fields:
            if field not in fields_by_table[table]:
                fields_by_table[table].append(field)
    return fields_by_table


def _r7_source_package_completion_item(staging_status: str) -> dict[str, object]:
    action_by_status = {
        "r7_to_r8p_staging_preflight_no_r7_package_supplied": (
            "Set REAL_FIELD_REPLAY_PACKAGE_DIR to a real R7 metadata+CSV package and rerun Agent61."
        ),
        "r7_to_r8p_staging_preflight_invalid_r7_package_path": (
            "Point REAL_FIELD_REPLAY_PACKAGE_DIR to an existing R7 package directory."
        ),
        "r7_to_r8p_staging_preflight_r7_package_not_directory": (
            "Provide a directory containing metadata.json and R7 CSV files, not a single file."
        ),
        "r7_to_r8p_staging_blocked_at_r7_metadata_preflight": (
            "Fix missing or invalid R7 metadata.json before staging pressure-resolution rows."
        ),
        "r7_to_r8p_staging_blocked_at_r7_metadata_provenance": (
            "Replace non-field/template data_origin and provenance placeholders in R7 metadata.json."
        ),
        "r7_to_r8p_staging_no_reusable_r7_rows_loaded": (
            "Add real rows to the five R7/R8p shared CSV tables before building an R8p draft."
        ),
    }
    return {
        "item_id": f"R8U22_R7_SOURCE_PACKAGE_{_safe_patch_token(staging_status)}",
        "priority": "P0",
        "completion_class": "r7_source_package",
        "target_table": "R7_Agent44_package",
        "target_fields": [],
        "operator_action": action_by_status.get(staging_status, "Repair R7 source package before staging."),
        "validation_gate": "Agent44/R7 import preflight and Agent61 R7 staging preflight",
        "can_create_field_evidence_by_item_only": False,
    }


def _operator_supplement_completion_items(field_rows_r7_alignment: dict[str, object]) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    for table_alignment in field_rows_r7_alignment.get("table_alignments", []):
        if not isinstance(table_alignment, dict):
            continue
        table = str(table_alignment.get("target_table", ""))
        supplement_mappings = [
            mapping
            for mapping in table_alignment.get("field_mappings", [])
            if isinstance(mapping, dict)
            and mapping.get("source_kind") == "r8p_supplement_or_operator_record_required"
        ]
        if not supplement_mappings:
            continue
        target_fields = [str(mapping.get("target_field")) for mapping in supplement_mappings]
        items.append(
            {
                "item_id": f"R8U22_OPERATOR_SUPPLEMENT_{_safe_patch_token(table)}",
                "priority": "P0" if table == "campaign_operation_log" else "P1",
                "completion_class": "operator_supplement",
                "target_table": table,
                "target_fields": target_fields,
                "field_sources": [
                    {
                        "target_field": str(mapping.get("target_field")),
                        "source_table": mapping.get("source_table"),
                        "source_field": mapping.get("source_field"),
                        "transformation": mapping.get("transformation"),
                        "field_boundary": mapping.get("field_boundary"),
                    }
                    for mapping in supplement_mappings
                ],
                "operator_action": (
                    f"Add reviewed R8p supplement values for `{table}` fields: "
                    + ", ".join(f"`{field}`" for field in target_fields)
                    + "."
                ),
                "validation_gate": "Agent61 R8p schema, provenance, scenario semantic, and operator review gates",
                "can_create_field_evidence_by_item_only": False,
            }
        )
    return items


def _agent52_export_completion_item(field_rows_r7_alignment: dict[str, object]) -> dict[str, object]:
    agent52_alignment = next(
        (
            item
            for item in field_rows_r7_alignment.get("table_alignments", [])
            if isinstance(item, dict) and item.get("target_table") == "agent52_replay_table"
        ),
        {},
    )
    target_fields = [str(field) for field in agent52_alignment.get("required_fields", [])]
    return {
        "item_id": "R8U22_AGENT52_REPLAY_EXPORT_AGENT52_REPLAY_TABLE",
        "priority": "P0",
        "completion_class": "agent52_replay_export",
        "target_table": "agent52_replay_table",
        "target_fields": target_fields,
        "operator_action": (
            "Export Agent49/52 replay rows after pressure-source conflict evaluation; do not fabricate "
            "`policy_action_id`, `expert_action_id`, or conflict counters from R7 field CSVs."
        ),
        "validation_gate": "Agent52 replay clearance, Agent61 R8p schema, and R8v downstream routing gates",
        "can_create_field_evidence_by_item_only": False,
    }


def _r7_alignment_for_table(table: str, r7_headers: dict[str, list[str]]) -> dict[str, object]:
    required_fields = _required_fields_for_table(table)
    if table == "agent52_replay_table":
        field_mappings = [
            {
                "target_field": field,
                "source_kind": "agent52_replay_export_required",
                "source_table": "Agent49/52 replay output",
                "source_field": field,
                "transformation": "export policy_action/expert_action and pressure-source conflict counters after replay.",
                "can_be_filled_from_r7_csv_only": False,
                "field_boundary": "Must not be fabricated from field package rows.",
            }
            for field in required_fields
        ]
        return _summarize_r7_table_alignment(table, required_fields, False, [], field_mappings)

    r7_table_headers = r7_headers.get(table, [])
    field_mappings = [
        _r7_field_mapping(table, field, r7_table_headers)
        for field in required_fields
    ]
    return _summarize_r7_table_alignment(table, required_fields, bool(r7_table_headers), r7_table_headers, field_mappings)


def _r7_field_mapping(table: str, field: str, r7_table_headers: list[str]) -> dict[str, object]:
    if field == "data_origin":
        return {
            "target_field": field,
            "source_kind": "metadata_to_row_copy_after_agent44_gate",
            "source_table": "metadata.json",
            "source_field": "data_origin",
            "transformation": "copy metadata data_origin to each row only after Agent44 metadata provenance passes.",
            "can_be_filled_from_r7_csv_only": False,
            "field_boundary": "Metadata copy is provenance context; R8p row gates still decide acceptance.",
        }
    if field in r7_table_headers:
        return {
            "target_field": field,
            "source_kind": "direct_csv_field",
            "source_table": table,
            "source_field": field,
            "transformation": "copy_value",
            "can_be_filled_from_r7_csv_only": True,
        }
    alias = _r7_alias_field(table, field, r7_table_headers)
    if alias:
        return {
            "target_field": field,
            "source_kind": "alias_csv_field",
            "source_table": table,
            "source_field": alias,
            "transformation": f"rename `{alias}` to `{field}` for R8p.",
            "can_be_filled_from_r7_csv_only": True,
        }
    supplement = _r7_supplement_source(table, field)
    return {
        "target_field": field,
        "source_kind": "r8p_supplement_or_operator_record_required",
        "source_table": supplement["source_table"],
        "source_field": supplement["source_field"],
        "transformation": supplement["transformation"],
        "can_be_filled_from_r7_csv_only": False,
        "field_boundary": supplement["field_boundary"],
    }


def _r7_alias_field(table: str, field: str, r7_table_headers: list[str]) -> str | None:
    aliases = {
        ("node_modality_sensor_timeseries", "sample_time_min"): "timestamp_min",
        ("fast_proxy_event_log", "proxy_label_time_min"): "event_time_min",
    }
    alias = aliases.get((table, field))
    if alias and alias in r7_table_headers:
        return alias
    return None


def _r7_supplement_source(table: str, field: str) -> dict[str, str]:
    if table == "node_modality_sensor_timeseries" and field == "unit":
        return {
            "source_table": "node_modality_sensor_timeseries or modality dictionary",
            "source_field": "unit",
            "transformation": "add explicit unit column, or derive from a reviewed modality-unit dictionary.",
            "field_boundary": "Unit inference must be reviewed; do not assume every modality is kPa.",
        }
    if table == "pressure_headloss_event_log" and field == "instrument_id":
        return {
            "source_table": "metadata.json or pressure_headloss_event_log",
            "source_field": "instrument_snapshot_id/instrument_id",
            "transformation": "copy instrument snapshot into row-level instrument_id or add row-level instrument_id.",
            "field_boundary": "Instrument provenance must remain traceable to calibration records.",
        }
    if table == "campaign_operation_log":
        sources = {
            "operator_review_required": ("pressure_headloss_review_required", "rename optional R7 guardrail review flag if present."),
            "pressure_source_resolution": ("operator_resolution_supplement.pressure_source_resolution", "add operator review outcome."),
            "authoritative_pressure_source": ("operator_resolution_supplement.authoritative_pressure_source", "add reviewed source selection."),
            "reviewer_id": ("operator_resolution_supplement.reviewer_id", "add reviewer identity or approved role id."),
            "review_time": ("operator_resolution_supplement.review_time", "add timestamp for review completion."),
            "calibration_action_id": ("operator_resolution_supplement.calibration_action_id", "add calibration action id."),
            "calibration_note": ("operator_resolution_supplement.calibration_note", "add calibration note."),
        }
        source_field, transformation = sources.get(field, (field, "add R8p-specific operation supplement."))
        return {
            "source_table": "campaign_operation_log or operator_resolution_supplement",
            "source_field": source_field,
            "transformation": transformation,
            "field_boundary": "Operator review fields must come from real review/calibration records.",
        }
    if table == "fast_proxy_event_log" and field == "proxy_event_type":
        return {
            "source_table": "fast_proxy_event_log",
            "source_field": "triggered_action_id/proxy_event_type",
            "transformation": "add proxy_event_type or map from reviewed triggered_action_id taxonomy.",
            "field_boundary": "Event type taxonomy must be stable before replay comparison.",
        }
    return {
        "source_table": f"{table}_r8p_supplement",
        "source_field": field,
        "transformation": "add field explicitly for R8p pressure-resolution replay.",
        "field_boundary": "Supplement must be field/operator/replay supported before acceptance.",
    }


def _summarize_r7_table_alignment(
    table: str,
    required_fields: list[str],
    r7_source_table_present: bool,
    r7_table_headers: list[str],
    field_mappings: list[dict[str, object]],
) -> dict[str, object]:
    direct_count = _count_mapping_kind(field_mappings, "direct_csv_field")
    alias_count = _count_mapping_kind(field_mappings, "alias_csv_field")
    metadata_count = _count_mapping_kind(field_mappings, "metadata_to_row_copy_after_agent44_gate")
    supplement_count = _count_mapping_kind(field_mappings, "r8p_supplement_or_operator_record_required")
    agent52_count = _count_mapping_kind(field_mappings, "agent52_replay_export_required")
    if agent52_count:
        status = "requires_agent52_replay_export"
    elif supplement_count:
        status = "reusable_from_r7_package_with_aliases_and_supplements"
    elif r7_source_table_present:
        status = "fully_reusable_from_r7_package_with_metadata_copy"
    else:
        status = "r7_source_table_missing"
    return {
        "target_table": table,
        "r7_source_table": None if table == "agent52_replay_table" else table,
        "r7_source_table_present": r7_source_table_present,
        "r7_headers": r7_table_headers,
        "required_fields": required_fields,
        "table_reuse_status": status,
        "direct_field_count": direct_count,
        "alias_field_count": alias_count,
        "metadata_field_count": metadata_count,
        "supplement_required_field_count": supplement_count,
        "agent52_export_required_field_count": agent52_count,
        "field_mappings": field_mappings,
    }


def _count_mapping_kind(mappings: list[dict[str, object]], kind: str) -> int:
    return sum(1 for item in mappings if item.get("source_kind") == kind)


def _field_rows_package_schema() -> dict[str, object]:
    expected_tables = sorted({*REQUIRED_TABLE_FIELDS, "agent52_replay_table"})
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "pressure_resolution_replay_rows.schema.json",
        "title": "R8p pressure resolution replay real field rows package",
        "description": (
            "Machine-readable structure contract for the real pressure-resolution replay rows package. "
            "Passing this schema does not make rows field evidence; R8p acceptance still checks real values, "
            "same-batch scenario linkage, template rejection, field-origin provenance in every required table, "
            "and downstream R8v/R7 gates."
        ),
        "type": "object",
        "required": expected_tables,
        "additionalProperties": False,
        "properties": {
            table: _table_schema(table)
            for table in expected_tables
        },
        "x_required_tables": expected_tables,
        "x_schema_boundary": (
            "Schema validity is only source/table preflight. It cannot write actuator, release gate, "
            "or field-supported claims."
        ),
        "x_downstream_acceptance": [
            "R8p field_row_acceptance",
            "R8v pressure-resolution row routing",
            "Agent51/49/52 field replay and holdout gates",
            "R7 evidence chain and human review",
        ],
    }


def _table_schema(table: str) -> dict[str, object]:
    required_fields = _required_fields_for_table(table)
    properties = {
        field: _field_schema(field)
        for field in sorted({*required_fields, "scenario_id", "scenario_type", "collection_id", "data_origin"})
    }
    return {
        "type": "array",
        "minItems": 1,
        "items": {
            "type": "object",
            "required": required_fields,
            "additionalProperties": True,
            "properties": properties,
        },
        "description": f"Field-origin rows for `{table}`. Extra metadata columns are allowed but do not bypass R8p acceptance.",
    }


def _field_schema(field: str) -> dict[str, object]:
    if field in {
        "value",
        "sample_time_min",
        "pressure_drop_kPa",
        "headloss_kPa_per_m",
        "flow_Lmin",
        "event_time_min",
        "matched_lab_sample_time_min",
        "hold_time_min",
        "recycle_ratio",
        "lab_label_time_min",
        "proxy_label_time_min",
        "false_positive_cost_index",
        "pressure_source_conflict_count",
        "resolved_pressure_source_conflict_count",
        "unresolved_pressure_source_conflict_count",
        "pressure_source_resolution_record_count",
    }:
        return {"type": ["number", "integer"]}
    if field in {
        "operator_review_required",
        "protective_triggered",
        "pressure_source_conflict_requires_operator_review",
        "pressure_source_conflict_control_block",
    }:
        return {"type": "boolean"}
    return {"type": "string", "minLength": 1}


def _field_rows_schema_validation(
    field_rows_source: dict[str, object],
    rows_by_table: dict[str, list[dict[str, object]]],
    field_rows_package_schema: dict[str, object],
) -> dict[str, object]:
    expected_tables = [str(table) for table in field_rows_package_schema.get("required", [])]
    source_status = str(field_rows_source.get("field_rows_source_status", "unknown"))
    table_validations: list[dict[str, object]] = []
    required_field_gap_count = 0
    invalid_type_count = 0
    template_marker_gap_count = 0
    field_origin_gap_count = 0

    for table in expected_tables:
        required_fields = _required_fields_for_table(table)
        rows = rows_by_table.get(table, [])
        table_missing_required: list[dict[str, object]] = []
        table_invalid_types: list[dict[str, object]] = []
        table_template_marker_gaps: list[dict[str, object]] = []
        table_field_origin_gaps: list[dict[str, object]] = []
        if table not in rows_by_table:
            table_status = "schema_table_missing"
        elif not rows:
            table_status = "schema_table_empty"
        else:
            for row_index, row in enumerate(rows):
                missing_fields = [field for field in required_fields if field not in row]
                if missing_fields:
                    table_missing_required.append(
                        {
                            "row_index": row_index,
                            "missing_fields": missing_fields,
                        }
                    )
                for field in required_fields:
                    if field not in row:
                        continue
                    if _is_template_marker_value(row.get(field)):
                        table_template_marker_gaps.append(
                            {
                                "row_index": row_index,
                                "field": field,
                                "observed_value": row.get(field),
                                "acceptance_rule": "must_replace_template_or_todo_with_real_field_value",
                            }
                        )
                    if not _value_matches_field_schema(field, row.get(field)):
                        table_invalid_types.append(
                            {
                                "row_index": row_index,
                                "field": field,
                                "expected_schema": _field_schema(field),
                                "observed_type": type(row.get(field)).__name__,
                            }
                        )
                    elif field == "data_origin" and not _is_field_origin_value(row.get(field)):
                        table_field_origin_gaps.append(
                            {
                                "row_index": row_index,
                                "field": field,
                                "observed_value": row.get(field),
                                "acceptance_rule": "must_be_field_origin_not_template_synthetic_or_todo",
                            }
                        )
            if table_missing_required or table_invalid_types or table_template_marker_gaps or table_field_origin_gaps:
                table_status = "schema_table_row_contract_failed"
            else:
                table_status = "schema_table_contract_passed"

        missing_count = sum(len(item["missing_fields"]) for item in table_missing_required)
        invalid_count = len(table_invalid_types)
        template_gap_count = len(table_template_marker_gaps)
        origin_gap_count = len(table_field_origin_gaps)
        required_field_gap_count += missing_count
        invalid_type_count += invalid_count
        template_marker_gap_count += template_gap_count
        field_origin_gap_count += origin_gap_count
        table_validations.append(
            {
                "table": table,
                "table_schema_status": table_status,
                "row_count": len(rows),
                "required_fields": required_fields,
                "missing_required_field_count": missing_count,
                "invalid_type_count": invalid_count,
                "template_marker_gap_count": template_gap_count,
                "field_origin_gap_count": origin_gap_count,
                "missing_required_fields_by_row": table_missing_required,
                "invalid_types_by_row": table_invalid_types,
                "template_marker_gaps_by_row": table_template_marker_gaps,
                "field_origin_gaps_by_row": table_field_origin_gaps,
            }
        )

    missing_table_count = len(field_rows_source.get("missing_tables", []) or [])
    empty_table_count = len(field_rows_source.get("empty_tables", []) or [])
    invalid_shape_count = len(field_rows_source.get("invalid_table_shapes", []) or [])
    unknown_table_count = len(field_rows_source.get("unknown_tables", []) or [])
    if source_status in {"field_rows_file_missing", "field_rows_file_invalid_json", "field_rows_file_invalid_shape"}:
        status = "schema_validation_blocked_at_source_preflight"
    elif missing_table_count or empty_table_count or invalid_shape_count or unknown_table_count:
        status = "schema_validation_failed_table_contract"
    elif template_marker_gap_count:
        status = "schema_validation_failed_template_marker_contract"
    elif required_field_gap_count or invalid_type_count:
        status = "schema_validation_failed_row_contract"
    elif field_origin_gap_count:
        status = "schema_validation_failed_provenance_contract"
    else:
        status = "schema_validation_passed_structure_contract"
    return {
        "field_rows_schema_validation_status": status,
        "schema_path": str(ROWS_SCHEMA_PATH),
        "schema_id": field_rows_package_schema.get("$id"),
        "source_status": source_status,
        "required_table_count": len(expected_tables),
        "loaded_table_count": int(field_rows_source.get("table_count", 0) or 0),
        "loaded_row_count": int(field_rows_source.get("row_count", 0) or 0),
        "missing_table_count": missing_table_count,
        "empty_table_count": empty_table_count,
        "invalid_shape_count": invalid_shape_count,
        "unknown_table_count": unknown_table_count,
        "required_field_gap_count": required_field_gap_count,
        "invalid_type_count": invalid_type_count,
        "template_marker_gap_count": template_marker_gap_count,
        "field_origin_gap_count": field_origin_gap_count,
        "source_blockers": field_rows_source.get("preflight_blockers", []),
        "table_validations": table_validations,
        "schema_validation_boundary": (
            "This validation checks source/table/required-field shape, coarse types, TODO/template markers, "
            "and data_origin provenance; R8p acceptance still checks real values, scenario linkage, "
            "all-table field origin, and downstream gates."
        ),
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }


def _field_rows_batch_bundle_preflight(
    report,
    field_rows_source: dict[str, object],
    rows_by_table: dict[str, list[dict[str, object]]],
    field_rows_package_schema: dict[str, object],
    field_rows_schema_validation: dict[str, object] | None = None,
) -> dict[str, object]:
    expected_tables = [str(table) for table in field_rows_package_schema.get("required", [])]
    source_status = str(field_rows_source.get("field_rows_source_status", "unknown"))
    schema_status = str(
        (field_rows_schema_validation or {}).get(
            "field_rows_schema_validation_status",
            "schema_validation_not_run",
        )
    )
    source_blockers = {"field_rows_file_missing", "field_rows_file_invalid_json", "field_rows_file_invalid_shape"}
    if source_status in source_blockers:
        status = "batch_bundle_preflight_blocked_at_source_preflight"
        candidate_batch_bundles: list[dict[str, object]] = []
        scenario_bundle_status = _empty_scenario_bundle_status(report, status)
    elif schema_status != "schema_validation_passed_structure_contract":
        status = "batch_bundle_preflight_blocked_at_schema_preflight"
        candidate_batch_bundles = _candidate_batch_bundles(rows_by_table, expected_tables)
        scenario_bundle_status = _scenario_bundle_status(report, candidate_batch_bundles)
    else:
        candidate_batch_bundles = _candidate_batch_bundles(rows_by_table, expected_tables)
        scenario_bundle_status = _scenario_bundle_status(report, candidate_batch_bundles)
        complete_scenario_count = sum(
            1
            for item in scenario_bundle_status
            if item.get("bundle_preflight_status") == "scenario_has_complete_six_table_batch_bundle"
        )
        partial_count = sum(
            1
            for item in candidate_batch_bundles
            if item.get("bundle_status") == "partial_batch_bundle"
        )
        if not candidate_batch_bundles:
            status = "batch_bundle_preflight_failed_no_candidate_batches"
        elif complete_scenario_count == len(report.metrics["row_collection_plan"]):
            status = "batch_bundle_preflight_passed_ready_for_scenario_acceptance"
        elif partial_count:
            status = "batch_bundle_preflight_failed_partial_batch_bundles"
        else:
            status = "batch_bundle_preflight_failed_no_complete_six_table_batches"

    complete_bundle_count = sum(
        1 for item in candidate_batch_bundles if item.get("bundle_status") == "complete_six_table_bundle"
    )
    partial_bundle_count = sum(
        1 for item in candidate_batch_bundles if item.get("bundle_status") == "partial_batch_bundle"
    )
    missing_bundle_table_count = sum(
        len(item.get("tables_missing", []) or [])
        for item in candidate_batch_bundles
    )
    return {
        "field_rows_batch_bundle_preflight_status": status,
        "preflight_path": str(ROWS_BATCH_BUNDLE_PREFLIGHT_PATH),
        "expected_tables": expected_tables,
        "source_status": source_status,
        "schema_validation_status": schema_status,
        "candidate_batch_count": len(candidate_batch_bundles),
        "complete_bundle_count": complete_bundle_count,
        "partial_bundle_count": partial_bundle_count,
        "missing_bundle_table_count": missing_bundle_table_count,
        "required_scenario_count": len(report.metrics["row_collection_plan"]),
        "scenario_bundle_ready_count": sum(
            1
            for item in scenario_bundle_status
            if item.get("bundle_preflight_status") == "scenario_has_complete_six_table_batch_bundle"
        ),
        "candidate_batch_bundles": candidate_batch_bundles,
        "scenario_bundle_status": scenario_bundle_status,
        "batch_bundle_boundary": (
            "This preflight only checks same-batch six-table availability and scenario linkage hints. "
            "It does not prove semantic validity, field-supported claims, actuator permission, or release-gate clearance."
        ),
        "next_operator_action": _batch_bundle_next_operator_action(status),
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }


def _candidate_batch_bundles(
    rows_by_table: dict[str, list[dict[str, object]]],
    expected_tables: list[str],
) -> list[dict[str, object]]:
    by_batch: dict[str, dict[str, object]] = {}
    for table in expected_tables:
        for row in rows_by_table.get(table, []) or []:
            if not isinstance(row, dict) or not _is_real_bundle_value(row.get("batch_id")):
                continue
            batch_id = str(row.get("batch_id"))
            bundle = by_batch.setdefault(
                batch_id,
                {
                    "batch_id": batch_id,
                    "tables_present": set(),
                    "row_counts_by_table": {expected_table: 0 for expected_table in expected_tables},
                    "scenario_ids_seen": set(),
                    "scenario_types_seen": set(),
                    "tables_with_scenario_linkage": set(),
                },
            )
            bundle["tables_present"].add(table)
            bundle["row_counts_by_table"][table] += 1
            scenario_id = row.get("scenario_id")
            if _is_real_bundle_value(scenario_id):
                bundle["scenario_ids_seen"].add(str(scenario_id))
                bundle["tables_with_scenario_linkage"].add(table)
            scenario_type = row.get("scenario_type", row.get("scenario"))
            if _is_real_bundle_value(scenario_type):
                bundle["scenario_types_seen"].add(str(scenario_type))
                bundle["tables_with_scenario_linkage"].add(table)

    bundles: list[dict[str, object]] = []
    for batch_id, raw_bundle in sorted(by_batch.items()):
        tables_present = sorted(str(table) for table in raw_bundle["tables_present"])
        tables_missing = [table for table in expected_tables if table not in raw_bundle["tables_present"]]
        scenario_ids_seen = sorted(str(value) for value in raw_bundle["scenario_ids_seen"])
        scenario_types_seen = sorted(str(value) for value in raw_bundle["scenario_types_seen"])
        tables_with_scenario_linkage = sorted(str(value) for value in raw_bundle["tables_with_scenario_linkage"])
        bundles.append(
            {
                "batch_id": batch_id,
                "bundle_status": "complete_six_table_bundle" if not tables_missing else "partial_batch_bundle",
                "tables_present": tables_present,
                "tables_missing": tables_missing,
                "row_counts_by_table": raw_bundle["row_counts_by_table"],
                "scenario_ids_seen": scenario_ids_seen,
                "scenario_types_seen": scenario_types_seen,
                "tables_with_scenario_linkage": tables_with_scenario_linkage,
                "scenario_linkage_table_gap_count": len(expected_tables) - len(tables_with_scenario_linkage),
                "can_attempt_scenario_acceptance": not tables_missing,
            }
        )
    return bundles


def _scenario_bundle_status(report, candidate_batch_bundles: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for plan in report.metrics["row_collection_plan"]:
        scenario_id = str(plan["scenario_id"])
        scenario_type = str(plan["scenario_type"])
        batch_role = str(plan["batch_role"])
        candidate_batches = [
            bundle
            for bundle in candidate_batch_bundles
            if _bundle_matches_scenario(bundle, scenario_id, scenario_type, batch_role)
        ]
        complete_batches = [
            str(bundle["batch_id"])
            for bundle in candidate_batches
            if bundle.get("bundle_status") == "complete_six_table_bundle"
        ]
        missing_tables_by_candidate_batch = {
            str(bundle["batch_id"]): bundle.get("tables_missing", [])
            for bundle in candidate_batches
            if bundle.get("tables_missing")
        }
        if complete_batches:
            status = "scenario_has_complete_six_table_batch_bundle"
        elif candidate_batches:
            status = "scenario_has_partial_batch_bundle"
        else:
            status = "scenario_has_no_candidate_batch_bundle"
        rows.append(
            {
                "scenario_id": scenario_id,
                "scenario_type": scenario_type,
                "batch_role": batch_role,
                "candidate_batches": [str(bundle["batch_id"]) for bundle in candidate_batches],
                "complete_candidate_batches": complete_batches,
                "missing_tables_by_candidate_batch": missing_tables_by_candidate_batch,
                "bundle_preflight_status": status,
            }
        )
    return rows


def _empty_scenario_bundle_status(report, status: str) -> list[dict[str, object]]:
    return [
        {
            "scenario_id": str(plan["scenario_id"]),
            "scenario_type": str(plan["scenario_type"]),
            "batch_role": str(plan["batch_role"]),
            "candidate_batches": [],
            "complete_candidate_batches": [],
            "missing_tables_by_candidate_batch": {},
            "bundle_preflight_status": status,
        }
        for plan in report.metrics["row_collection_plan"]
    ]


def _bundle_matches_scenario(bundle: dict[str, object], scenario_id: str, scenario_type: str, batch_role: str) -> bool:
    batch_id = str(bundle.get("batch_id", ""))
    scenario_ids_seen = {str(value) for value in bundle.get("scenario_ids_seen", []) or []}
    scenario_types_seen = {str(value) for value in bundle.get("scenario_types_seen", []) or []}
    return (
        scenario_id in scenario_ids_seen
        or scenario_type in scenario_types_seen
        or batch_role in batch_id
        or scenario_id in batch_id
    )


def _is_real_bundle_value(value: object) -> bool:
    if value is None:
        return False
    text = str(value).strip()
    if not text:
        return False
    lowered = text.lower()
    return not (
        lowered.startswith("todo")
        or "todo_" in lowered
        or "template" in lowered
        or lowered in {"nan", "none", "null", "field_validation_required", "replace_me", "sample_only"}
    )


def _batch_bundle_next_operator_action(status: str) -> str:
    if status == "batch_bundle_preflight_blocked_at_source_preflight":
        return "R8p_fix_field_rows_source_preflight"
    if status == "batch_bundle_preflight_blocked_at_schema_preflight":
        return "R8p_fix_schema_template_provenance_or_table_contracts"
    if status in {
        "batch_bundle_preflight_failed_no_candidate_batches",
        "batch_bundle_preflight_failed_partial_batch_bundles",
        "batch_bundle_preflight_failed_no_complete_six_table_batches",
    }:
        return "R8p_complete_same_batch_six_table_bundles"
    return "R8p_continue_to_scenario_acceptance_and_r8v_routing"


def _field_rows_temporal_window_preflight(
    report,
    field_rows_source: dict[str, object],
    rows_by_table: dict[str, list[dict[str, object]]],
    field_rows_schema_validation: dict[str, object] | None = None,
    field_rows_batch_bundle_preflight: dict[str, object] | None = None,
) -> dict[str, object]:
    source_status = str(field_rows_source.get("field_rows_source_status", "unknown"))
    schema_status = str(
        (field_rows_schema_validation or {}).get(
            "field_rows_schema_validation_status",
            "schema_validation_not_run",
        )
    )
    batch_status = str(
        (field_rows_batch_bundle_preflight or {}).get(
            "field_rows_batch_bundle_preflight_status",
            "batch_bundle_preflight_not_run",
        )
    )
    source_blockers = {"field_rows_file_missing", "field_rows_file_invalid_json", "field_rows_file_invalid_shape"}
    batch_checks: list[dict[str, object]] = []
    if source_status in source_blockers:
        status = "temporal_window_preflight_blocked_at_source_preflight"
        scenario_temporal_status = _empty_scenario_temporal_status(report, status)
    elif schema_status != "schema_validation_passed_structure_contract":
        status = "temporal_window_preflight_blocked_at_schema_preflight"
        scenario_temporal_status = _empty_scenario_temporal_status(report, status)
    elif batch_status != "batch_bundle_preflight_passed_ready_for_scenario_acceptance":
        status = "temporal_window_preflight_blocked_at_batch_bundle_preflight"
        scenario_temporal_status = _empty_scenario_temporal_status(report, status)
    else:
        scenario_temporal_status = []
        bundle_by_batch = {
            str(bundle.get("batch_id")): bundle
            for bundle in (field_rows_batch_bundle_preflight or {}).get("candidate_batch_bundles", []) or []
            if isinstance(bundle, dict)
        }
        for scenario_bundle in (field_rows_batch_bundle_preflight or {}).get("scenario_bundle_status", []) or []:
            if not isinstance(scenario_bundle, dict):
                continue
            scenario_id = str(scenario_bundle.get("scenario_id", ""))
            scenario_type = str(scenario_bundle.get("scenario_type", ""))
            batch_checks_for_scenario = []
            valid_batches = []
            for batch_id in scenario_bundle.get("complete_candidate_batches", []) or []:
                batch_id_text = str(batch_id)
                check = _temporal_window_check_for_batch(rows_by_table, batch_id_text)
                check["scenario_id"] = scenario_id
                check["scenario_type"] = scenario_type
                check["bundle_status"] = bundle_by_batch.get(batch_id_text, {}).get("bundle_status", "unknown")
                batch_checks.append(check)
                batch_checks_for_scenario.append(check)
                if check["temporal_window_status"] == "temporal_window_passed":
                    valid_batches.append(batch_id_text)
            if valid_batches:
                scenario_status = "scenario_has_temporal_valid_batch"
            elif batch_checks_for_scenario:
                scenario_status = "scenario_has_temporal_window_violations"
            else:
                scenario_status = "scenario_has_no_complete_batch_for_temporal_check"
            scenario_temporal_status.append(
                {
                    "scenario_id": scenario_id,
                    "scenario_type": scenario_type,
                    "complete_candidate_batches": scenario_bundle.get("complete_candidate_batches", []),
                    "temporal_valid_batches": valid_batches,
                    "violations_by_batch": {
                        str(check["batch_id"]): check["violations"]
                        for check in batch_checks_for_scenario
                        if check.get("violations")
                    },
                    "latency_margin_min_by_batch": {
                        str(check["batch_id"]): check.get("latency_margin_min")
                        for check in batch_checks_for_scenario
                    },
                    "temporal_preflight_status": scenario_status,
                }
            )
        if scenario_temporal_status and all(
            item.get("temporal_preflight_status") == "scenario_has_temporal_valid_batch"
            for item in scenario_temporal_status
        ):
            status = "temporal_window_preflight_passed_ready_for_scenario_acceptance"
        elif any("hold_time_budget_must_cover_slowest_evidence_label" in check.get("violations", []) for check in batch_checks):
            status = "temporal_window_preflight_failed_hold_time_budget_contract"
        else:
            status = "temporal_window_preflight_failed_temporal_order_contract"

    violation_count = sum(len(check.get("violations", []) or []) for check in batch_checks)
    temporal_valid_batch_count = sum(
        1 for check in batch_checks if check.get("temporal_window_status") == "temporal_window_passed"
    )
    hold_time_violation_count = sum(
        1
        for check in batch_checks
        if "hold_time_budget_must_cover_slowest_evidence_label" in check.get("violations", [])
    )
    return {
        "field_rows_temporal_window_preflight_status": status,
        "preflight_path": str(ROWS_TEMPORAL_WINDOW_PREFLIGHT_PATH),
        "source_status": source_status,
        "schema_validation_status": schema_status,
        "batch_bundle_preflight_status": batch_status,
        "checked_batch_count": len(batch_checks),
        "temporal_valid_batch_count": temporal_valid_batch_count,
        "temporal_violation_count": violation_count,
        "hold_time_violation_count": hold_time_violation_count,
        "scenario_temporal_ready_count": sum(
            1
            for item in scenario_temporal_status
            if item.get("temporal_preflight_status") == "scenario_has_temporal_valid_batch"
        ),
        "batch_temporal_checks": batch_checks,
        "scenario_temporal_status": scenario_temporal_status,
        "temporal_window_boundary": (
            "This preflight checks whether low-frequency sensing, proxy labels, offline lab labels, "
            "operator review, and hold/recycle time form a feasible same-batch temporal window. "
            "It does not prove field-supported claims or permit actuator/release-gate writes."
        ),
        "next_operator_action": _temporal_window_next_operator_action(status),
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }


def _temporal_window_check_for_batch(
    rows_by_table: dict[str, list[dict[str, object]]],
    batch_id: str,
) -> dict[str, object]:
    node_row = _first_batch_row(rows_by_table, "node_modality_sensor_timeseries", batch_id)
    pressure_row = _first_batch_row(rows_by_table, "pressure_headloss_event_log", batch_id)
    operation_row = _first_batch_row(rows_by_table, "campaign_operation_log", batch_id)
    lab_row = _first_batch_row(rows_by_table, "offline_lab_results", batch_id)
    proxy_row = _first_batch_row(rows_by_table, "fast_proxy_event_log", batch_id)
    times = {
        "sensor_sample_time_min": _numeric_time_value(node_row.get("sample_time_min")),
        "pressure_event_time_min": _numeric_time_value(pressure_row.get("event_time_min")),
        "matched_lab_sample_time_min": _numeric_time_value(pressure_row.get("matched_lab_sample_time_min")),
        "offline_lab_sample_time_min": _numeric_time_value(lab_row.get("sample_time_min")),
        "offline_lab_label_time_min": _numeric_time_value(lab_row.get("lab_label_time_min")),
        "fast_proxy_label_time_min": _numeric_time_value(proxy_row.get("proxy_label_time_min")),
        "hold_time_min": _numeric_time_value(operation_row.get("hold_time_min")),
    }
    violations: list[str] = []
    if _gt(times["sensor_sample_time_min"], times["pressure_event_time_min"]):
        violations.append("temporal_order_requires_sensor_sample_before_pressure_event")
    if _gt(times["pressure_event_time_min"], times["fast_proxy_label_time_min"]):
        violations.append("temporal_order_requires_pressure_event_before_fast_proxy")
    if _gt(times["offline_lab_sample_time_min"], times["offline_lab_label_time_min"]):
        violations.append("temporal_order_requires_lab_sample_before_lab_label")
    if (
        times["pressure_event_time_min"] is not None
        and times["matched_lab_sample_time_min"] is not None
        and times["offline_lab_label_time_min"] is not None
        and not (
            times["pressure_event_time_min"]
            <= times["matched_lab_sample_time_min"]
            <= times["offline_lab_label_time_min"]
        )
    ):
        violations.append("temporal_order_requires_pressure_matched_lab_within_label_window")
    if _gt(times["fast_proxy_label_time_min"], times["offline_lab_label_time_min"]):
        violations.append("temporal_order_requires_fast_proxy_before_lab_label")
    evidence_times = [
        value
        for key, value in times.items()
        if key != "hold_time_min" and value is not None
    ]
    latest_required_evidence_time = max(evidence_times) if evidence_times else None
    latency_margin_min = (
        round(times["hold_time_min"] - latest_required_evidence_time, 6)
        if times["hold_time_min"] is not None and latest_required_evidence_time is not None
        else None
    )
    if latency_margin_min is not None and latency_margin_min < 0:
        violations.append("hold_time_budget_must_cover_slowest_evidence_label")
    return {
        "batch_id": batch_id,
        "temporal_window_status": "temporal_window_passed" if not violations else "temporal_window_failed",
        "times": times,
        "latest_required_evidence_time_min": latest_required_evidence_time,
        "latency_margin_min": latency_margin_min,
        "violations": violations,
    }


def _first_batch_row(
    rows_by_table: dict[str, list[dict[str, object]]],
    table: str,
    batch_id: str,
) -> dict[str, object]:
    for row in rows_by_table.get(table, []) or []:
        if isinstance(row, dict) and str(row.get("batch_id", "")) == batch_id:
            return row
    return {}


def _numeric_time_value(value: object) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def _gt(left: float | None, right: float | None) -> bool:
    return left is not None and right is not None and left > right


def _empty_scenario_temporal_status(report, status: str) -> list[dict[str, object]]:
    return [
        {
            "scenario_id": str(plan["scenario_id"]),
            "scenario_type": str(plan["scenario_type"]),
            "complete_candidate_batches": [],
            "temporal_valid_batches": [],
            "violations_by_batch": {},
            "latency_margin_min_by_batch": {},
            "temporal_preflight_status": status,
        }
        for plan in report.metrics["row_collection_plan"]
    ]


def _temporal_window_next_operator_action(status: str) -> str:
    if status == "temporal_window_preflight_blocked_at_source_preflight":
        return "R8p_fix_field_rows_source_preflight"
    if status == "temporal_window_preflight_blocked_at_schema_preflight":
        return "R8p_fix_schema_template_provenance_or_table_contracts"
    if status == "temporal_window_preflight_blocked_at_batch_bundle_preflight":
        return "R8p_complete_same_batch_six_table_bundles"
    if status in {
        "temporal_window_preflight_failed_hold_time_budget_contract",
        "temporal_window_preflight_failed_temporal_order_contract",
    }:
        return "R8p_fix_same_batch_timestamps_and_hold_time_budget"
    return "R8p_continue_to_scenario_acceptance_and_r8v_routing"


def _field_rows_scenario_semantic_preflight(
    report,
    field_rows_source: dict[str, object],
    rows_by_table: dict[str, list[dict[str, object]]],
    field_rows_schema_validation: dict[str, object] | None = None,
    field_rows_batch_bundle_preflight: dict[str, object] | None = None,
    field_rows_temporal_window_preflight: dict[str, object] | None = None,
) -> dict[str, object]:
    source_status = str(field_rows_source.get("field_rows_source_status", "unknown"))
    schema_status = str(
        (field_rows_schema_validation or {}).get(
            "field_rows_schema_validation_status",
            "schema_validation_not_run",
        )
    )
    batch_status = str(
        (field_rows_batch_bundle_preflight or {}).get(
            "field_rows_batch_bundle_preflight_status",
            "batch_bundle_preflight_not_run",
        )
    )
    temporal_status = str(
        (field_rows_temporal_window_preflight or {}).get(
            "field_rows_temporal_window_preflight_status",
            "temporal_window_preflight_not_run",
        )
    )
    source_blockers = {"field_rows_file_missing", "field_rows_file_invalid_json", "field_rows_file_invalid_shape"}
    semantic_checks: list[dict[str, object]] = []
    if source_status in source_blockers:
        status = "scenario_semantic_preflight_blocked_at_source_preflight"
        scenario_semantic_status = _empty_scenario_semantic_status(report, status)
    elif schema_status != "schema_validation_passed_structure_contract":
        status = "scenario_semantic_preflight_blocked_at_schema_preflight"
        scenario_semantic_status = _empty_scenario_semantic_status(report, status)
    elif batch_status != "batch_bundle_preflight_passed_ready_for_scenario_acceptance":
        status = "scenario_semantic_preflight_blocked_at_batch_bundle_preflight"
        scenario_semantic_status = _empty_scenario_semantic_status(report, status)
    elif temporal_status != "temporal_window_preflight_passed_ready_for_scenario_acceptance":
        status = "scenario_semantic_preflight_blocked_at_temporal_window_preflight"
        scenario_semantic_status = _empty_scenario_semantic_status(report, status)
    else:
        scenario_semantic_status = []
        for scenario_temporal in (field_rows_temporal_window_preflight or {}).get("scenario_temporal_status", []) or []:
            if not isinstance(scenario_temporal, dict):
                continue
            scenario_id = str(scenario_temporal.get("scenario_id", ""))
            scenario_type = str(scenario_temporal.get("scenario_type", ""))
            semantic_valid_batches: list[str] = []
            scenario_checks: list[dict[str, object]] = []
            for batch_id in scenario_temporal.get("temporal_valid_batches", []) or []:
                check = _scenario_semantic_check_for_batch(rows_by_table, str(batch_id), scenario_id, scenario_type)
                semantic_checks.append(check)
                scenario_checks.append(check)
                if check["semantic_status"] == "scenario_semantics_passed":
                    semantic_valid_batches.append(str(batch_id))
            if semantic_valid_batches:
                scenario_status = "scenario_has_semantic_valid_batch"
            elif scenario_checks:
                scenario_status = "scenario_has_semantic_contract_violations"
            else:
                scenario_status = "scenario_has_no_temporal_valid_batch_for_semantic_check"
            scenario_semantic_status.append(
                {
                    "scenario_id": scenario_id,
                    "scenario_type": scenario_type,
                    "temporal_valid_batches": scenario_temporal.get("temporal_valid_batches", []),
                    "semantic_valid_batches": semantic_valid_batches,
                    "violations_by_batch": {
                        str(check["batch_id"]): check["semantic_violations"]
                        for check in scenario_checks
                        if check.get("semantic_violations")
                    },
                    "condition_checks_by_batch": {
                        str(check["batch_id"]): check["condition_checks"]
                        for check in scenario_checks
                    },
                    "scenario_semantic_preflight_status": scenario_status,
                }
            )
        if scenario_semantic_status and all(
            item.get("scenario_semantic_preflight_status") == "scenario_has_semantic_valid_batch"
            for item in scenario_semantic_status
        ):
            status = "scenario_semantic_preflight_passed_ready_for_scenario_acceptance"
        else:
            status = _scenario_semantic_failure_status(semantic_checks)

    semantic_violation_count = sum(len(check.get("semantic_violations", []) or []) for check in semantic_checks)
    condition_violation_counts = _semantic_condition_violation_counts(semantic_checks)
    return {
        "field_rows_scenario_semantic_preflight_status": status,
        "preflight_path": str(ROWS_SCENARIO_SEMANTIC_PREFLIGHT_PATH),
        "source_status": source_status,
        "schema_validation_status": schema_status,
        "batch_bundle_preflight_status": batch_status,
        "temporal_window_preflight_status": temporal_status,
        "checked_batch_count": len(semantic_checks),
        "semantic_valid_batch_count": sum(
            1 for check in semantic_checks if check.get("semantic_status") == "scenario_semantics_passed"
        ),
        "semantic_violation_count": semantic_violation_count,
        "condition_violation_counts": condition_violation_counts,
        "scenario_semantic_ready_count": sum(
            1
            for item in scenario_semantic_status
            if item.get("scenario_semantic_preflight_status") == "scenario_has_semantic_valid_batch"
        ),
        "batch_semantic_checks": semantic_checks,
        "scenario_semantic_status": scenario_semantic_status,
        "scenario_semantic_boundary": (
            "This preflight checks pressure-resolution scenario meaning: unresolved conflicts must remain reviewed "
            "and blocked, resolved conflicts must cite an authoritative source and resolution record, and guardrail "
            "clearance must not bypass control-block/review flags. It does not prove field-supported claims or permit "
            "actuator/release-gate writes."
        ),
        "next_operator_action": _scenario_semantic_next_operator_action(status),
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }


def _scenario_semantic_check_for_batch(
    rows_by_table: dict[str, list[dict[str, object]]],
    batch_id: str,
    scenario_id: str,
    scenario_type: str,
) -> dict[str, object]:
    operation_row = _first_batch_row(rows_by_table, "campaign_operation_log", batch_id)
    replay_row = _first_batch_row(rows_by_table, "agent52_replay_table", batch_id)
    condition_checks: dict[str, bool] = {}
    violations: list[str] = []
    if scenario_type == "unresolved_conflict_review_block":
        resolution = str(operation_row.get("pressure_source_resolution", "")).lower()
        condition_checks["unresolved_operation_requires_review"] = (
            resolution in {"unresolved", "pending", "pending_operator_review"}
            and bool(operation_row.get("operator_review_required", False))
        )
        condition_checks["unresolved_replay_requires_operator_review"] = (
            _integer_count(replay_row.get("unresolved_pressure_source_conflict_count")) > 0
            and bool(replay_row.get("pressure_source_conflict_requires_operator_review", False))
        )
        condition_checks["unresolved_replay_keeps_control_block"] = bool(
            replay_row.get("pressure_source_conflict_control_block", False)
        )
    elif scenario_type in {
        "resolved_conflict_authoritative_source",
        "agent51_scoreability_recovery",
        "guardrail_clearance_replay",
    }:
        condition_checks["resolved_operation_has_authoritative_source"] = (
            str(operation_row.get("pressure_source_resolution", "")).lower() == "resolved"
            and _is_real_bundle_value(operation_row.get("authoritative_pressure_source"))
        )
        condition_checks["resolved_replay_has_resolution_record"] = (
            _integer_count(replay_row.get("resolved_pressure_source_conflict_count")) > 0
            and _integer_count(replay_row.get("pressure_source_resolution_record_count")) > 0
        )
        if scenario_type == "guardrail_clearance_replay":
            condition_checks["guardrail_clearance_has_no_control_block"] = (
                not bool(replay_row.get("pressure_source_conflict_control_block", False))
                and not bool(replay_row.get("pressure_source_conflict_requires_operator_review", False))
            )
    elif scenario_type == "operator_review_latency_budget":
        condition_checks["operator_review_latency_has_review_time_and_hold_time"] = (
            _is_real_bundle_value(operation_row.get("review_time"))
            and _numeric_time_value(operation_row.get("hold_time_min")) is not None
        )
    for condition, passed in condition_checks.items():
        if not passed:
            violations.append(condition)
    return {
        "scenario_id": scenario_id,
        "scenario_type": scenario_type,
        "batch_id": batch_id,
        "semantic_status": "scenario_semantics_passed" if not violations else "scenario_semantics_failed",
        "condition_checks": condition_checks,
        "semantic_violations": violations,
    }


def _integer_count(value: object) -> int:
    if isinstance(value, bool) or value is None:
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return 0


def _empty_scenario_semantic_status(report, status: str) -> list[dict[str, object]]:
    return [
        {
            "scenario_id": str(plan["scenario_id"]),
            "scenario_type": str(plan["scenario_type"]),
            "temporal_valid_batches": [],
            "semantic_valid_batches": [],
            "violations_by_batch": {},
            "condition_checks_by_batch": {},
            "scenario_semantic_preflight_status": status,
        }
        for plan in report.metrics["row_collection_plan"]
    ]


def _semantic_condition_violation_counts(semantic_checks: list[dict[str, object]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for check in semantic_checks:
        for violation in check.get("semantic_violations", []) or []:
            key = str(violation)
            counts[key] = counts.get(key, 0) + 1
    return counts


def _scenario_semantic_failure_status(semantic_checks: list[dict[str, object]]) -> str:
    violations = {
        str(violation)
        for check in semantic_checks
        for violation in (check.get("semantic_violations", []) or [])
    }
    if {
        "unresolved_operation_requires_review",
        "unresolved_replay_requires_operator_review",
        "unresolved_replay_keeps_control_block",
    } & violations:
        return "scenario_semantic_preflight_failed_unresolved_conflict_contract"
    if "guardrail_clearance_has_no_control_block" in violations:
        return "scenario_semantic_preflight_failed_guardrail_clearance_contract"
    if {
        "resolved_operation_has_authoritative_source",
        "resolved_replay_has_resolution_record",
    } & violations:
        return "scenario_semantic_preflight_failed_resolved_conflict_contract"
    if "operator_review_latency_has_review_time_and_hold_time" in violations:
        return "scenario_semantic_preflight_failed_operator_review_latency_contract"
    return "scenario_semantic_preflight_failed_scenario_semantic_contract"


def _scenario_semantic_next_operator_action(status: str) -> str:
    if status == "scenario_semantic_preflight_blocked_at_source_preflight":
        return "R8p_fix_field_rows_source_preflight"
    if status == "scenario_semantic_preflight_blocked_at_schema_preflight":
        return "R8p_fix_schema_template_provenance_or_table_contracts"
    if status == "scenario_semantic_preflight_blocked_at_batch_bundle_preflight":
        return "R8p_complete_same_batch_six_table_bundles"
    if status == "scenario_semantic_preflight_blocked_at_temporal_window_preflight":
        return "R8p_fix_same_batch_timestamps_and_hold_time_budget"
    if status.startswith("scenario_semantic_preflight_failed"):
        return "R8p_fix_pressure_resolution_scenario_semantics"
    return "R8p_continue_to_scenario_acceptance_and_r8v_routing"


def _field_rows_downstream_routing_preflight(
    report,
    field_rows_source: dict[str, object],
    field_rows_schema_validation: dict[str, object] | None = None,
    field_rows_batch_bundle_preflight: dict[str, object] | None = None,
    field_rows_temporal_window_preflight: dict[str, object] | None = None,
    field_rows_scenario_semantic_preflight: dict[str, object] | None = None,
) -> dict[str, object]:
    source_status = str(field_rows_source.get("field_rows_source_status", "unknown"))
    schema_status = str(
        (field_rows_schema_validation or {}).get(
            "field_rows_schema_validation_status",
            "schema_validation_not_run",
        )
    )
    batch_status = str(
        (field_rows_batch_bundle_preflight or {}).get(
            "field_rows_batch_bundle_preflight_status",
            "batch_bundle_preflight_not_run",
        )
    )
    temporal_status = str(
        (field_rows_temporal_window_preflight or {}).get(
            "field_rows_temporal_window_preflight_status",
            "temporal_window_preflight_not_run",
        )
    )
    semantic_status = str(
        (field_rows_scenario_semantic_preflight or {}).get(
            "field_rows_scenario_semantic_preflight_status",
            "scenario_semantic_preflight_not_run",
        )
    )
    field_acceptance = report.metrics["field_row_acceptance"]
    acceptance_status = str(field_acceptance.get("field_row_acceptance_status", "unknown"))
    accepted_batches_by_scenario = {
        str(scenario_id): [str(batch) for batch in batches]
        for scenario_id, batches in (field_acceptance.get("accepted_batches_by_scenario", {}) or {}).items()
        if isinstance(batches, list)
    }
    accepted_batches = sorted(
        {
            batch
            for batches in accepted_batches_by_scenario.values()
            for batch in batches
        }
    )
    source_blockers = {"field_rows_file_missing", "field_rows_file_invalid_json", "field_rows_file_invalid_shape"}
    if source_status in source_blockers:
        status = "downstream_routing_preflight_blocked_at_source_preflight"
    elif schema_status != "schema_validation_passed_structure_contract":
        status = "downstream_routing_preflight_blocked_at_schema_preflight"
    elif batch_status != "batch_bundle_preflight_passed_ready_for_scenario_acceptance":
        status = "downstream_routing_preflight_blocked_at_batch_bundle_preflight"
    elif temporal_status != "temporal_window_preflight_passed_ready_for_scenario_acceptance":
        status = "downstream_routing_preflight_blocked_at_temporal_window_preflight"
    elif semantic_status != "scenario_semantic_preflight_passed_ready_for_scenario_acceptance":
        status = "downstream_routing_preflight_blocked_at_scenario_semantic_preflight"
    elif acceptance_status != "field_replay_rows_accepted_for_all_scenarios":
        status = "downstream_routing_preflight_blocked_at_field_row_acceptance"
    else:
        status = "downstream_routing_preflight_passed_ready_for_r8v_field_replay_and_holdout_gates"

    can_route = status == "downstream_routing_preflight_passed_ready_for_r8v_field_replay_and_holdout_gates"
    routing_targets = _downstream_routing_targets(accepted_batches, can_route)
    return {
        "field_rows_downstream_routing_preflight_status": status,
        "preflight_path": str(ROWS_DOWNSTREAM_ROUTING_PREFLIGHT_PATH),
        "source_status": source_status,
        "schema_validation_status": schema_status,
        "batch_bundle_preflight_status": batch_status,
        "temporal_window_preflight_status": temporal_status,
        "scenario_semantic_preflight_status": semantic_status,
        "field_row_acceptance_status": acceptance_status,
        "accepted_scenario_count": field_acceptance.get("accepted_scenario_count", 0),
        "accepted_batch_count": field_acceptance.get("accepted_batch_count", 0),
        "accepted_batches_by_scenario": accepted_batches_by_scenario,
        "accepted_batches_for_routing": accepted_batches,
        "routing_target_count": len(routing_targets),
        "routing_ready_target_count": sum(
            1 for target in routing_targets if target.get("routing_status") == "ready_for_downstream_gate"
        ),
        "routing_targets": routing_targets,
        "downstream_gate_sequence": [
            "Agent51 catalyst proxy holdout consumes accepted pressure-resolution rows as scoreability/recovery context.",
            "Agent49 guardrail context consumes accepted rows before any control protection relaxation.",
            "Agent52 replay clearance consumes accepted rows for policy/expert action agreement and conflict-clearance replay.",
            "R7 evidence chain consumes accepted rows for field package, replay, holdout, claim gate, and operator review boundaries.",
        ],
        "downstream_routing_boundary": (
            "Routing only moves R8p-accepted field rows to downstream replay/holdout/evidence gates. It does not "
            "upgrade a field-supported claim and does not permit actuator or release-gate writes."
        ),
        "next_operator_action": _downstream_routing_next_operator_action(status),
        "can_route_to_r8v": can_route,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }


def _downstream_routing_targets(accepted_batches: list[str], can_route: bool) -> list[dict[str, object]]:
    routing_status = "ready_for_downstream_gate" if can_route else "blocked_by_upstream_preflight"
    return [
        {
            "target_id": "agent51_catalyst_proxy_holdout",
            "target_agent": "Agent51",
            "routing_status": routing_status,
            "accepted_batches": accepted_batches if can_route else [],
            "required_inputs": [
                "node_modality_sensor_timeseries",
                "offline_lab_results",
                "campaign_operation_log",
                "pressure_headloss_event_log",
            ],
            "expected_gate_metrics": [
                "field_proxy_holdout_summary_status",
                "scoreable_batch_count",
                "agent51_scoreable_batch_count_after_resolution",
            ],
            "technical_effect": "Resolved pressure-source rows can restore catalyst proxy scoreability only after field holdout checks.",
        },
        {
            "target_id": "agent49_guardrail_context",
            "target_agent": "Agent49",
            "routing_status": routing_status,
            "accepted_batches": accepted_batches if can_route else [],
            "required_inputs": [
                "pressure_headloss_event_log",
                "campaign_operation_log",
                "agent52_replay_table",
            ],
            "expected_gate_metrics": [
                "agent49_pressure_conflict_guardrail_clear",
                "pressure_source_conflict_control_block",
                "can_write_to_actuator",
            ],
            "technical_effect": "Guardrail relaxation remains gated by reviewed pressure-source evidence and cannot bypass actuator safety.",
        },
        {
            "target_id": "agent52_replay_clearance",
            "target_agent": "Agent52",
            "routing_status": routing_status,
            "accepted_batches": accepted_batches if can_route else [],
            "required_inputs": [
                "agent52_replay_table",
                "campaign_operation_log",
                "field_rows_scenario_semantic_preflight",
            ],
            "expected_gate_metrics": [
                "agent52_pressure_source_conflict_clear",
                "joint_action_accuracy",
                "human_review_gate_pass",
            ],
            "technical_effect": "Replay clearance must agree with scenario semantics before any strategy can be promoted.",
        },
        {
            "target_id": "r7_evidence_chain",
            "target_agent": "R7 facade",
            "routing_status": routing_status,
            "accepted_batches": accepted_batches if can_route else [],
            "required_inputs": [
                "all_six_r8p_required_tables",
                "field_rows_temporal_window_preflight",
                "field_rows_scenario_semantic_preflight",
                "field_rows_operator_handoff",
            ],
            "expected_gate_metrics": [
                "field_replay_evidence_chain_pass",
                "claim_gate_status",
                "operator_review_gate_pass",
                "can_write_to_release_gate",
            ],
            "technical_effect": "Accepted rows remain field evidence candidates until replay, holdout, claim gate, and operator review pass.",
        },
    ]


def _downstream_routing_next_operator_action(status: str) -> str:
    if status == "downstream_routing_preflight_blocked_at_source_preflight":
        return "R8p_fix_field_rows_source_preflight"
    if status == "downstream_routing_preflight_blocked_at_schema_preflight":
        return "R8p_fix_schema_template_provenance_or_table_contracts"
    if status == "downstream_routing_preflight_blocked_at_batch_bundle_preflight":
        return "R8p_complete_same_batch_six_table_bundles"
    if status == "downstream_routing_preflight_blocked_at_temporal_window_preflight":
        return "R8p_fix_same_batch_timestamps_and_hold_time_budget"
    if status == "downstream_routing_preflight_blocked_at_scenario_semantic_preflight":
        return "R8p_fix_pressure_resolution_scenario_semantics"
    if status == "downstream_routing_preflight_blocked_at_field_row_acceptance":
        return "R8p_complete_field_row_acceptance"
    return "R8v_route_pressure_resolution_rows_to_field_replay_and_holdout_gates"


def _field_rows_downstream_route_handoff(
    field_rows_downstream_routing_preflight: dict[str, object],
) -> dict[str, object]:
    """Convert R8v routing readiness into per-target handoff contracts.

    This is an interface contract only. It does not run downstream replay,
    relax control protection, write a release gate, or upgrade field claims.
    """

    downstream_status = str(
        field_rows_downstream_routing_preflight.get(
            "field_rows_downstream_routing_preflight_status",
            "",
        )
    )
    can_route_to_r8v = bool(field_rows_downstream_routing_preflight.get("can_route_to_r8v", False))
    upstream_next_action = str(
        field_rows_downstream_routing_preflight.get(
            "next_operator_action",
            _downstream_routing_next_operator_action(downstream_status),
        )
    )
    accepted_batches = [
        str(batch)
        for batch in field_rows_downstream_routing_preflight.get("accepted_batches_for_routing", [])
        or []
    ]
    handoff_targets: list[dict[str, object]] = []
    for order, target in enumerate(
        field_rows_downstream_routing_preflight.get("routing_targets", []) or [],
        start=1,
    ):
        if not isinstance(target, dict):
            continue
        routing_status = str(target.get("routing_status", ""))
        target_id = str(target.get("target_id", "unknown_target"))
        ready = routing_status == "ready_for_downstream_gate" and can_route_to_r8v
        handoff_status = (
            "downstream_target_handoff_ready_for_replay_or_holdout_gate"
            if ready
            else "downstream_target_handoff_blocked_by_r8p_or_r8v_preflight"
        )
        handoff_targets.append(
            {
                "execution_order": order,
                "target_id": target_id,
                "target_agent": target.get("target_agent", ""),
                "handoff_status": handoff_status,
                "linked_routing_status": routing_status,
                "accepted_batches": target.get("accepted_batches", []) if ready else [],
                "required_input_tables_or_artifacts": target.get("required_inputs", []),
                "expected_gate_metrics": target.get("expected_gate_metrics", []),
                "input_contract": {
                    "batch_key": "batch_id",
                    "minimum_accepted_batch_count": 1,
                    "accepted_batches_must_come_from": "R8p field_row_acceptance accepted_batches_for_routing",
                    "upstream_preflight_required": (
                        "downstream_routing_preflight_passed_ready_for_r8v_field_replay_and_holdout_gates"
                    ),
                },
                "gate_contract": {
                    "must_run_before_control_or_release": True,
                    "must_preserve_operator_review_gate": True,
                    "must_preserve_holdout_or_replay_boundary": True,
                    "expected_gate_metrics": target.get("expected_gate_metrics", []),
                },
                "next_operator_action": (
                    f"R8v_run_{target_id}_gate"
                    if ready
                    else upstream_next_action
                ),
                "technical_effect": target.get("technical_effect", ""),
                "blocked_writes": [
                    "actuator",
                    "release_gate",
                    "protective_control_relaxation",
                    "field_supported_claim_upgrade",
                ],
                "can_write_to_actuator": False,
                "can_write_to_release_gate": False,
                "field_claim_upgrade_allowed": False,
            }
        )

    ready_handoff_target_count = sum(
        1
        for target in handoff_targets
        if target.get("handoff_status") == "downstream_target_handoff_ready_for_replay_or_holdout_gate"
    )
    blocked_handoff_target_count = len(handoff_targets) - ready_handoff_target_count
    if can_route_to_r8v:
        handoff_status = "downstream_route_handoff_ready_for_r8v_target_gates"
        next_operator_action = "R8v_run_downstream_replay_holdout_and_evidence_chain_gates"
    elif downstream_status == "downstream_routing_preflight_blocked_at_field_row_acceptance":
        handoff_status = "downstream_route_handoff_waiting_for_r8p_accepted_rows"
        next_operator_action = upstream_next_action
    else:
        handoff_status = "downstream_route_handoff_blocked_by_upstream_r8p_preflight"
        next_operator_action = upstream_next_action

    return {
        "downstream_route_handoff_id": "R8u50_downstream_route_handoff",
        "downstream_route_handoff_status": handoff_status,
        "handoff_path": str(ROWS_DOWNSTREAM_ROUTE_HANDOFF_PATH),
        "linked_downstream_routing_preflight_status": downstream_status,
        "model_core_layers": [
            "diagnostic_decision_layer",
            "closed_loop_execution_layer",
            "verification_governance_layer",
        ],
        "core_capabilities": [
            "controllability",
            "verifiability",
            "engineering_feasibility",
            "protectability",
        ],
        "accepted_batch_count": int(
            field_rows_downstream_routing_preflight.get("accepted_batch_count", 0) or 0
        ),
        "accepted_batches_for_handoff": accepted_batches if can_route_to_r8v else [],
        "handoff_target_count": len(handoff_targets),
        "ready_handoff_target_count": ready_handoff_target_count,
        "blocked_handoff_target_count": blocked_handoff_target_count,
        "next_operator_action": next_operator_action,
        "handoff_execution_order": [target["target_id"] for target in handoff_targets],
        "handoff_targets": handoff_targets,
        "technical_feature_mapping": {
            "technical_problem": (
                "After pressure-resolution rows pass R8p, the system still needs a deterministic way to hand "
                "accepted batches to holdout, replay, guardrail, and evidence-chain gates without implying control release."
            ),
            "technical_means": (
                "A downstream route handoff binds each R8v target to required input tables, accepted batch ids, "
                "expected gate metrics, execution order, blocked writes, and replay/holdout boundaries."
            ),
            "technical_effect": (
                "Accepted field rows can be routed to the right validation gates with less manual ambiguity while "
                "actuator, release-gate, and field-claim upgrades remain blocked until downstream evidence passes."
            ),
            "prior_art_distinction_candidate": (
                "Unlike generic data routing, this handoff links sparse pressure conflict evidence to grey-box "
                "control guardrails, catalyst proxy holdout, replay clearance, and claim-gate preservation."
            ),
        },
        "evidence_boundaries": [
            "This handoff is not field evidence and does not run downstream gates.",
            "Ready handoff targets only receive R8p-accepted batches; they cannot write actuator or release gate.",
            "Agent49 guardrail relaxation remains blocked until downstream replay and operator review gates pass.",
            "Field-supported claims remain blocked until R7 evidence chain, holdout, replay, and human review pass.",
        ],
        "can_route_to_r8v": can_route_to_r8v,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "field_claim_upgrade_allowed": False,
    }


def _field_rows_downstream_target_gate_preflight(
    field_rows_downstream_route_handoff: dict[str, object],
) -> dict[str, object]:
    """Turn route handoff targets into executable downstream gate preflight records.

    This only prepares target gate contracts. It does not run Agent51/49/52/R7,
    does not consume target outputs, and cannot upgrade field claims.
    """

    handoff_status = str(
        field_rows_downstream_route_handoff.get("downstream_route_handoff_status", "")
    )
    can_route_to_r8v = bool(field_rows_downstream_route_handoff.get("can_route_to_r8v", False))
    upstream_next_action = str(
        field_rows_downstream_route_handoff.get(
            "next_operator_action",
            "R8p_fix_field_rows_source_preflight",
        )
    )
    target_preflights: list[dict[str, object]] = []
    for target in field_rows_downstream_route_handoff.get("handoff_targets", []) or []:
        if not isinstance(target, dict):
            continue
        target_id = str(target.get("target_id", "unknown_target"))
        target_agent = str(target.get("target_agent", ""))
        handoff_ready = (
            target.get("handoff_status")
            == "downstream_target_handoff_ready_for_replay_or_holdout_gate"
            and can_route_to_r8v
        )
        target_preflight_status = (
            "target_gate_preflight_ready_waiting_for_downstream_gate_execution"
            if handoff_ready
            else "target_gate_preflight_blocked_by_route_handoff"
        )
        required_inputs = [
            str(item)
            for item in target.get("required_input_tables_or_artifacts", []) or []
        ]
        expected_metrics = [
            str(item)
            for item in target.get("expected_gate_metrics", []) or []
        ]
        blocking_reasons = [] if handoff_ready else [
            f"handoff_status={target.get('handoff_status', 'unknown')}",
            f"linked_route_handoff_status={handoff_status or 'not_available'}",
        ]
        command_contract = _r8v_target_gate_command_contract(target_id)
        target_preflights.append(
            {
                "execution_order": int(target.get("execution_order", len(target_preflights) + 1) or 0),
                "target_id": target_id,
                "target_agent": target_agent,
                "target_gate_preflight_status": target_preflight_status,
                "linked_handoff_status": target.get("handoff_status", ""),
                "accepted_batches": target.get("accepted_batches", []) if handoff_ready else [],
                "required_input_tables_or_artifacts": required_inputs,
                "required_input_count": len(required_inputs),
                "expected_gate_metrics": expected_metrics,
                "expected_gate_metric_count": len(expected_metrics),
                "validation_command": command_contract["validation_command"],
                "expected_metrics_artifact": command_contract["expected_metrics_artifact"],
                "target_gate_output_contract": {
                    "must_report_expected_metrics": expected_metrics,
                    "must_preserve_batch_id": True,
                    "must_preserve_operator_review_boundary": True,
                    "must_report_can_write_to_actuator": "can_write_to_actuator" in expected_metrics
                    or target_id == "agent49_guardrail_context",
                    "must_report_can_write_to_release_gate": "can_write_to_release_gate" in expected_metrics
                    or target_id == "r7_evidence_chain",
                },
                "target_gate_preflight_blocking_reasons": blocking_reasons,
                "blocked_writes": target.get("blocked_writes", []),
                "next_operator_action": (
                    f"R8v_execute_{target_id}_gate_and_collect_metrics"
                    if handoff_ready
                    else upstream_next_action
                ),
                "field_boundary": (
                    "Target gate preflight only confirms the target can receive R8p accepted batches. "
                    "The downstream gate output must still pass replay/holdout/operator-review checks."
                ),
                "can_execute_target_gate": handoff_ready,
                "can_write_to_actuator": False,
                "can_write_to_release_gate": False,
                "field_claim_upgrade_allowed": False,
            }
        )

    ready_target_gate_count = sum(
        1
        for target in target_preflights
        if target.get("target_gate_preflight_status")
        == "target_gate_preflight_ready_waiting_for_downstream_gate_execution"
    )
    blocked_target_gate_count = len(target_preflights) - ready_target_gate_count
    if can_route_to_r8v and ready_target_gate_count == len(target_preflights) and target_preflights:
        target_gate_preflight_status = "downstream_target_gate_preflight_ready_for_r8v_execution"
        next_operator_action = "R8v_execute_target_gates_in_order_and_collect_gate_metrics"
    elif handoff_status:
        target_gate_preflight_status = "downstream_target_gate_preflight_blocked_by_downstream_route_handoff"
        next_operator_action = upstream_next_action
    else:
        target_gate_preflight_status = "downstream_target_gate_preflight_not_run_missing_handoff"
        next_operator_action = "R8p_run_downstream_route_handoff_first"

    return {
        "downstream_target_gate_preflight_id": "R8u51_downstream_target_gate_preflight",
        "downstream_target_gate_preflight_status": target_gate_preflight_status,
        "target_gate_preflight_path": str(ROWS_DOWNSTREAM_TARGET_GATE_PREFLIGHT_PATH),
        "linked_downstream_route_handoff_status": handoff_status,
        "model_core_layers": [
            "diagnostic_decision_layer",
            "closed_loop_execution_layer",
            "verification_governance_layer",
        ],
        "core_capabilities": [
            "controllability",
            "verifiability",
            "engineering_feasibility",
            "protectability",
        ],
        "target_gate_count": len(target_preflights),
        "ready_target_gate_count": ready_target_gate_count,
        "blocked_target_gate_count": blocked_target_gate_count,
        "target_gate_execution_order": [
            str(target.get("target_id", "")) for target in target_preflights
        ],
        "target_gate_preflights": target_preflights,
        "next_operator_action": next_operator_action,
        "technical_feature_mapping": {
            "technical_problem": (
                "A route handoff can identify downstream validation targets, but an operator still needs a "
                "deterministic gate-execution contract for each target before replay, holdout, or evidence-chain checks."
            ),
            "technical_means": (
                "A target-gate preflight board binds each R8v target to validation command, required inputs, "
                "expected output metrics, batch preservation rules, blocked writes, and target-specific blocking reasons."
            ),
            "technical_effect": (
                "The pressure-resolution handoff becomes executable without treating handoff readiness as gate success "
                "or allowing actuator/release writes before downstream validation."
            ),
            "prior_art_distinction_candidate": (
                "Unlike generic workflow dispatch, the target-gate preflight preserves grey-box control safety, "
                "field evidence tiers, and operator-review boundaries for each downstream validation target."
            ),
        },
        "evidence_boundaries": [
            "Target-gate preflight is not downstream replay, holdout, evidence-chain pass, or field evidence.",
            "Ready target gates only mean R8p accepted batches can be submitted to the target gate.",
            "Any actuator, release-gate, protective-control relaxation, or field-claim upgrade remains blocked until target outputs pass their own gates.",
        ],
        "can_route_to_r8v": can_route_to_r8v,
        "can_execute_all_target_gates": (
            can_route_to_r8v
            and ready_target_gate_count == len(target_preflights)
            and bool(target_preflights)
        ),
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "field_claim_upgrade_allowed": False,
    }


def _field_rows_downstream_target_gate_result_intake_schema(
    field_rows_downstream_target_gate_preflight: dict[str, object],
) -> dict[str, object]:
    target_schemas = []
    for target in field_rows_downstream_target_gate_preflight.get("target_gate_preflights", []) or []:
        if not isinstance(target, dict):
            continue
        target_schemas.append(
            {
                "target_id": str(target.get("target_id", "")),
                "target_agent": str(target.get("target_agent", "")),
                "expected_metrics_artifact": str(target.get("expected_metrics_artifact", "")),
                "expected_gate_metrics": [
                    str(item) for item in target.get("expected_gate_metrics", []) or []
                ],
                "required_result_fields": [
                    "target_id",
                    "target_gate_status",
                    "batch_ids",
                    "source_metrics_artifact",
                    "reported_metrics",
                    "operator_review_boundary_preserved",
                    "can_write_to_actuator",
                    "can_write_to_release_gate",
                    "field_claim_upgrade_allowed",
                ],
                "required_boolean_fields": [
                    "operator_review_boundary_preserved",
                    "can_write_to_actuator",
                    "can_write_to_release_gate",
                    "field_claim_upgrade_allowed",
                ],
                "accepted_status_values": [
                    "target_gate_result_passed",
                    "target_gate_result_failed",
                    "target_gate_result_blocked",
                    "target_gate_result_waiting_for_operator_review",
                ],
                "must_preserve_batch_id": True,
                "must_preserve_operator_review_boundary": True,
                "intake_cannot_authorize_actuator_or_release": True,
            }
        )
    return {
        "downstream_target_gate_result_intake_schema_id": (
            "R8u52_downstream_target_gate_result_intake_schema"
        ),
        "schema_path": str(ROWS_DOWNSTREAM_TARGET_GATE_RESULT_INTAKE_SCHEMA_PATH),
        "result_package_env_var": "R8V_TARGET_GATE_RESULT_PACKAGE_PATH",
        "linked_target_gate_preflight_status": field_rows_downstream_target_gate_preflight.get(
            "downstream_target_gate_preflight_status",
            "",
        ),
        "expected_target_count": len(target_schemas),
        "expected_target_ids": [schema["target_id"] for schema in target_schemas],
        "target_result_schemas": target_schemas,
        "package_shape": {
            "root_type": "object",
            "required_top_level_fields": ["package_metadata", "target_gate_results"],
            "target_gate_results_type": "list_of_objects",
        },
        "model_core_layers": [
            "diagnostic_decision_layer",
            "closed_loop_execution_layer",
            "verification_governance_layer",
        ],
        "core_capabilities": [
            "verifiability",
            "engineering_feasibility",
            "protectability",
        ],
        "technical_feature_mapping": {
            "technical_problem": (
                "Downstream gate commands are not enough: the returned gate results need a deterministic intake "
                "contract before they can influence grey-box control arbitration."
            ),
            "technical_means": (
                "A result-intake schema binds each downstream target to required result fields, expected gate "
                "metrics, source artifact provenance, batch preservation, and protective write boundaries."
            ),
            "technical_effect": (
                "The system can receive Agent51/49/52/R7 outputs without treating arbitrary metrics files as "
                "field replay success, actuator clearance, or release-gate clearance."
            ),
            "prior_art_distinction_candidate": (
                "Unlike generic pipeline output collection, the intake schema preserves target-level evidence "
                "tiers, batch traceability, and grey-box safety boundaries."
            ),
        },
        "evidence_boundaries": [
            "The intake schema is not a downstream target result.",
            "A structurally valid result package is not field-supported success unless later arbitration and review pass.",
            "The intake layer never authorizes actuator or release-gate writes.",
        ],
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "field_claim_upgrade_allowed": False,
    }


def _field_rows_downstream_target_gate_result_preflight(
    field_rows_downstream_target_gate_preflight: dict[str, object],
    result_intake_schema: dict[str, object],
    result_package_path: Path | None,
) -> dict[str, object]:
    target_gate_preflight_status = str(
        field_rows_downstream_target_gate_preflight.get(
            "downstream_target_gate_preflight_status",
            "",
        )
    )
    expected_target_ids = [
        str(target_id) for target_id in result_intake_schema.get("expected_target_ids", []) or []
    ]
    target_schema_by_id = {
        str(schema.get("target_id", "")): schema
        for schema in result_intake_schema.get("target_result_schemas", []) or []
        if isinstance(schema, dict)
    }
    can_accept_results = (
        target_gate_preflight_status == "downstream_target_gate_preflight_ready_for_r8v_execution"
        and bool(field_rows_downstream_target_gate_preflight.get("can_execute_all_target_gates", False))
    )
    source_path = str(result_package_path) if result_package_path else ""
    base = {
        "downstream_target_gate_result_preflight_id": "R8u52_downstream_target_gate_result_preflight",
        "preflight_path": str(ROWS_DOWNSTREAM_TARGET_GATE_RESULT_PREFLIGHT_PATH),
        "result_package_env_var": "R8V_TARGET_GATE_RESULT_PACKAGE_PATH",
        "result_package_source_path": source_path,
        "linked_target_gate_preflight_status": target_gate_preflight_status,
        "expected_target_count": len(expected_target_ids),
        "expected_target_ids": expected_target_ids,
        "model_core_layers": [
            "diagnostic_decision_layer",
            "closed_loop_execution_layer",
            "verification_governance_layer",
        ],
        "core_capabilities": [
            "verifiability",
            "engineering_feasibility",
            "protectability",
        ],
    }
    if not can_accept_results:
        return {
            **base,
            "downstream_target_gate_result_preflight_status": (
                "downstream_target_gate_result_preflight_blocked_by_target_gate_preflight"
            ),
            "source_status": "result_package_not_checked_until_target_gates_ready",
            "submitted_target_result_count": 0,
            "accepted_target_result_count": 0,
            "rejected_target_result_count": 0,
            "missing_target_ids": expected_target_ids,
            "unknown_target_ids": [],
            "target_result_validations": [],
            "blocking_reasons": [
                f"target_gate_preflight_status={target_gate_preflight_status or 'not_available'}",
                "target gates cannot accept results until R8p accepted rows can execute all target gates",
            ],
            "next_operator_action": field_rows_downstream_target_gate_preflight.get(
                "next_operator_action",
                "R8p_fix_field_rows_source_preflight",
            ),
            "can_route_to_result_arbitration": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "field_claim_upgrade_allowed": False,
        }
    if result_package_path is None:
        return {
            **base,
            "downstream_target_gate_result_preflight_status": (
                "downstream_target_gate_result_preflight_waiting_for_result_package"
            ),
            "source_status": "result_package_path_not_configured",
            "submitted_target_result_count": 0,
            "accepted_target_result_count": 0,
            "rejected_target_result_count": 0,
            "missing_target_ids": expected_target_ids,
            "unknown_target_ids": [],
            "target_result_validations": [],
            "blocking_reasons": ["R8V_TARGET_GATE_RESULT_PACKAGE_PATH_not_configured"],
            "next_operator_action": "R8v_submit_target_gate_result_package",
            "can_route_to_result_arbitration": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "field_claim_upgrade_allowed": False,
        }
    if not result_package_path.exists():
        return {
            **base,
            "downstream_target_gate_result_preflight_status": (
                "downstream_target_gate_result_preflight_missing_result_package"
            ),
            "source_status": "result_package_file_missing",
            "submitted_target_result_count": 0,
            "accepted_target_result_count": 0,
            "rejected_target_result_count": 0,
            "missing_target_ids": expected_target_ids,
            "unknown_target_ids": [],
            "target_result_validations": [],
            "blocking_reasons": ["result_package_file_missing"],
            "next_operator_action": "R8v_submit_target_gate_result_package",
            "can_route_to_result_arbitration": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "field_claim_upgrade_allowed": False,
        }
    try:
        payload = json.loads(result_package_path.read_text(encoding="utf-8"))
    except JSONDecodeError as exc:
        return {
            **base,
            "downstream_target_gate_result_preflight_status": (
                "downstream_target_gate_result_preflight_invalid_json"
            ),
            "source_status": "result_package_invalid_json",
            "submitted_target_result_count": 0,
            "accepted_target_result_count": 0,
            "rejected_target_result_count": 0,
            "missing_target_ids": expected_target_ids,
            "unknown_target_ids": [],
            "target_result_validations": [],
            "blocking_reasons": [f"invalid_json:{exc.msg}"],
            "next_operator_action": "R8v_fix_target_gate_result_package_json",
            "can_route_to_result_arbitration": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "field_claim_upgrade_allowed": False,
        }
    if not isinstance(payload, dict) or not isinstance(payload.get("target_gate_results"), list):
        return {
            **base,
            "downstream_target_gate_result_preflight_status": (
                "downstream_target_gate_result_preflight_invalid_shape"
            ),
            "source_status": "result_package_invalid_shape",
            "submitted_target_result_count": 0,
            "accepted_target_result_count": 0,
            "rejected_target_result_count": 0,
            "missing_target_ids": expected_target_ids,
            "unknown_target_ids": [],
            "target_result_validations": [],
            "blocking_reasons": ["root_must_be_object_with_target_gate_results_list"],
            "next_operator_action": "R8v_fix_target_gate_result_package_shape",
            "can_route_to_result_arbitration": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "field_claim_upgrade_allowed": False,
        }

    target_results = payload.get("target_gate_results", [])
    validations: list[dict[str, object]] = []
    seen_target_ids: set[str] = set()
    unknown_target_ids: list[str] = []
    any_write_requested = False
    for index, result in enumerate(target_results):
        if not isinstance(result, dict):
            validations.append(
                {
                    "row_index": index,
                    "target_id": "",
                    "target_result_status": "target_result_rejected_invalid_row_shape",
                    "missing_fields": ["row_must_be_object"],
                    "missing_expected_metrics": [],
                    "boundary_violations": [],
                }
            )
            continue
        target_id = str(result.get("target_id", ""))
        seen_target_ids.add(target_id)
        schema = target_schema_by_id.get(target_id)
        if schema is None:
            unknown_target_ids.append(target_id)
            validations.append(
                {
                    "row_index": index,
                    "target_id": target_id,
                    "target_result_status": "target_result_rejected_unknown_target",
                    "missing_fields": [],
                    "missing_expected_metrics": [],
                    "boundary_violations": ["unknown_target_id"],
                }
            )
            continue
        required_fields = [str(field) for field in schema.get("required_result_fields", []) or []]
        missing_fields = [field for field in required_fields if field not in result]
        reported_metrics = result.get("reported_metrics", {})
        if not isinstance(reported_metrics, dict):
            reported_metrics = {}
            if "reported_metrics" not in missing_fields:
                missing_fields.append("reported_metrics")
        expected_metrics = [str(metric) for metric in schema.get("expected_gate_metrics", []) or []]
        missing_expected_metrics = [
            metric for metric in expected_metrics if metric not in reported_metrics
        ]
        boundary_violations: list[str] = []
        target_gate_status = str(result.get("target_gate_status", ""))
        accepted_status_values = [
            str(status) for status in schema.get("accepted_status_values", []) or []
        ]
        if target_gate_status not in accepted_status_values:
            boundary_violations.append("target_gate_status_not_accepted_value")
        expected_artifact = str(schema.get("expected_metrics_artifact", ""))
        if str(result.get("source_metrics_artifact", "")) != expected_artifact:
            boundary_violations.append("source_metrics_artifact_mismatch")
        batch_ids = result.get("batch_ids", [])
        if not isinstance(batch_ids, list) or not batch_ids:
            boundary_violations.append("batch_ids_must_be_non_empty_list")
        if result.get("operator_review_boundary_preserved") is not True:
            boundary_violations.append("operator_review_boundary_not_preserved")
        for field in schema.get("required_boolean_fields", []) or []:
            if field in result and not isinstance(result.get(field), bool):
                boundary_violations.append(f"{field}_must_be_boolean")
        if bool(result.get("can_write_to_actuator", False)):
            any_write_requested = True
            boundary_violations.append("target_result_requests_actuator_write")
        if bool(result.get("can_write_to_release_gate", False)):
            any_write_requested = True
            boundary_violations.append("target_result_requests_release_gate_write")
        if bool(result.get("field_claim_upgrade_allowed", False)):
            boundary_violations.append("target_result_requests_field_claim_upgrade")
        target_result_status = (
            "target_result_accepted_for_result_arbitration"
            if not missing_fields and not missing_expected_metrics and not boundary_violations
            else "target_result_rejected_by_intake_contract"
        )
        validations.append(
            {
                "row_index": index,
                "target_id": target_id,
                "target_result_status": target_result_status,
                "target_gate_status": target_gate_status,
                "batch_ids": batch_ids,
                "source_metrics_artifact": result.get("source_metrics_artifact", ""),
                "missing_fields": missing_fields,
                "missing_expected_metrics": missing_expected_metrics,
                "boundary_violations": boundary_violations,
            }
        )

    missing_target_ids = [target_id for target_id in expected_target_ids if target_id not in seen_target_ids]
    accepted_count = sum(
        1
        for validation in validations
        if validation.get("target_result_status") == "target_result_accepted_for_result_arbitration"
    )
    rejected_count = len(validations) - accepted_count
    if missing_target_ids or unknown_target_ids:
        status = "downstream_target_gate_result_preflight_failed_target_coverage"
        next_operator_action = "R8v_complete_target_gate_result_package_coverage"
    elif any_write_requested:
        status = "downstream_target_gate_result_preflight_failed_protective_write_boundary"
        next_operator_action = "R8v_remove_unreviewed_actuator_or_release_write_requests"
    elif rejected_count:
        status = "downstream_target_gate_result_preflight_failed_result_contract"
        next_operator_action = "R8v_fix_target_gate_result_fields_and_metrics"
    else:
        status = "downstream_target_gate_result_preflight_passed_ready_for_result_arbitration"
        next_operator_action = "R8v_arbitrate_target_gate_results_before_any_control_write"
    return {
        **base,
        "downstream_target_gate_result_preflight_status": status,
        "source_status": "result_package_loaded",
        "submitted_target_result_count": len(validations),
        "accepted_target_result_count": accepted_count,
        "rejected_target_result_count": rejected_count,
        "missing_target_ids": missing_target_ids,
        "unknown_target_ids": unknown_target_ids,
        "target_result_validations": validations,
        "blocking_reasons": [
            reason
            for reason in [
                f"missing_target_ids={missing_target_ids}" if missing_target_ids else "",
                f"unknown_target_ids={unknown_target_ids}" if unknown_target_ids else "",
                "target_result_requests_protective_write" if any_write_requested else "",
                f"rejected_target_result_count={rejected_count}" if rejected_count else "",
            ]
            if reason
        ],
        "next_operator_action": next_operator_action,
        "can_route_to_result_arbitration": (
            status == "downstream_target_gate_result_preflight_passed_ready_for_result_arbitration"
        ),
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "field_claim_upgrade_allowed": False,
    }


def _field_rows_downstream_target_gate_result_arbitration(
    field_rows_downstream_target_gate_result_preflight: dict[str, object],
) -> dict[str, object]:
    preflight_status = str(
        field_rows_downstream_target_gate_result_preflight.get(
            "downstream_target_gate_result_preflight_status",
            "",
        )
    )
    validations = [
        validation
        for validation in field_rows_downstream_target_gate_result_preflight.get(
            "target_result_validations",
            [],
        )
        or []
        if isinstance(validation, dict)
    ]
    expected_target_ids = [
        str(target_id)
        for target_id in field_rows_downstream_target_gate_result_preflight.get(
            "expected_target_ids",
            [],
        )
        or []
    ]
    accepted_validations = [
        validation
        for validation in validations
        if validation.get("target_result_status") == "target_result_accepted_for_result_arbitration"
    ]
    status_counts = {
        "target_gate_result_passed": 0,
        "target_gate_result_failed": 0,
        "target_gate_result_blocked": 0,
        "target_gate_result_waiting_for_operator_review": 0,
        "target_gate_result_invalid_or_missing": 0,
    }
    target_gate_decisions = []
    accepted_status_values = set(status_counts) - {"target_gate_result_invalid_or_missing"}
    for validation in accepted_validations:
        target_gate_status = str(validation.get("target_gate_status", ""))
        if target_gate_status not in accepted_status_values:
            status_counts["target_gate_result_invalid_or_missing"] += 1
        else:
            status_counts[target_gate_status] += 1
        target_gate_decisions.append(
            {
                "target_id": validation.get("target_id", ""),
                "target_gate_status": target_gate_status or "target_gate_status_missing",
                "source_metrics_artifact": validation.get("source_metrics_artifact", ""),
                "batch_ids": validation.get("batch_ids", []),
                "arbitration_boundary": (
                    "Target gate status can only route to operator review or blocked remediation; "
                    "it cannot authorize actuator or release-gate writes."
                ),
            }
        )
    base = {
        "downstream_target_gate_result_arbitration_id": (
            "R8u53_downstream_target_gate_result_arbitration"
        ),
        "arbitration_path": str(ROWS_DOWNSTREAM_TARGET_GATE_RESULT_ARBITRATION_PATH),
        "linked_result_preflight_status": preflight_status,
        "expected_target_count": len(expected_target_ids),
        "expected_target_ids": expected_target_ids,
        "accepted_target_result_count": len(accepted_validations),
        "target_gate_status_counts": status_counts,
        "target_gate_decisions": target_gate_decisions,
        "model_core_layers": [
            "diagnostic_decision_layer",
            "closed_loop_execution_layer",
            "verification_governance_layer",
        ],
        "core_capabilities": [
            "controllability",
            "verifiability",
            "engineering_feasibility",
            "protectability",
        ],
        "technical_feature_mapping": {
            "technical_problem": (
                "A structurally valid downstream result package still does not prove that all target gates "
                "agree on safe replay, holdout, evidence-chain, and control-boundary status."
            ),
            "technical_means": (
                "A target-gate result arbitration gate aggregates accepted Agent51/49/52/R7 target statuses, "
                "separates passed, failed, blocked, and operator-review states, and routes only unanimous pass "
                "cases to human review before any control write."
            ),
            "technical_effect": (
                "The grey-box closed loop gains a deterministic safety gate between downstream validation results "
                "and any later protective-control or release-gate decision."
            ),
            "prior_art_distinction_candidate": (
                "Unlike generic workflow result aggregation, the arbitration gate preserves multi-target evidence "
                "tiers, operator review, and no-write safety constraints for low-cost sensing water-treatment control."
            ),
        },
        "evidence_boundaries": [
            "Arbitration is not field-supported success and is not legal or patentability opinion.",
            "A unanimous pass can only route to operator review; it cannot write actuator or release gate.",
            "Any failed, blocked, waiting, invalid, missing, or unreviewed target keeps control and release blocked.",
        ],
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "field_claim_upgrade_allowed": False,
    }
    if preflight_status != "downstream_target_gate_result_preflight_passed_ready_for_result_arbitration":
        return {
            **base,
            "downstream_target_gate_result_arbitration_status": (
                "downstream_target_gate_result_arbitration_blocked_by_result_preflight"
            ),
            "blocking_reasons": [
                f"result_preflight_status={preflight_status or 'not_available'}"
            ],
            "next_operator_action": field_rows_downstream_target_gate_result_preflight.get(
                "next_operator_action",
                "R8v_fix_target_gate_result_preflight_first",
            ),
            "can_route_to_operator_review": False,
            "can_emit_protective_control_candidate": False,
        }
    if len(accepted_validations) != len(expected_target_ids):
        return {
            **base,
            "downstream_target_gate_result_arbitration_status": (
                "downstream_target_gate_result_arbitration_blocked_by_incomplete_intake_acceptance"
            ),
            "blocking_reasons": [
                f"accepted_target_result_count={len(accepted_validations)}",
                f"expected_target_count={len(expected_target_ids)}",
            ],
            "next_operator_action": "R8v_fix_target_gate_result_intake_acceptance",
            "can_route_to_operator_review": False,
            "can_emit_protective_control_candidate": False,
        }
    if status_counts["target_gate_result_invalid_or_missing"]:
        arbitration_status = "downstream_target_gate_result_arbitration_blocked_by_invalid_target_status"
        next_operator_action = "R8v_fix_invalid_target_gate_status_before_arbitration"
        blocking_reasons = ["target_gate_result_invalid_or_missing"]
    elif status_counts["target_gate_result_failed"] or status_counts["target_gate_result_blocked"]:
        arbitration_status = "downstream_target_gate_result_arbitration_blocked_by_target_gate_failure"
        next_operator_action = "R8v_return_failed_or_blocked_target_gates_for_remediation"
        blocking_reasons = [
            f"target_gate_result_failed={status_counts['target_gate_result_failed']}",
            f"target_gate_result_blocked={status_counts['target_gate_result_blocked']}",
        ]
    elif status_counts["target_gate_result_waiting_for_operator_review"]:
        arbitration_status = "downstream_target_gate_result_arbitration_waiting_for_operator_review"
        next_operator_action = "R8v_complete_operator_review_for_waiting_target_gates"
        blocking_reasons = [
            f"target_gate_result_waiting_for_operator_review={status_counts['target_gate_result_waiting_for_operator_review']}"
        ]
    elif status_counts["target_gate_result_passed"] == len(expected_target_ids):
        arbitration_status = "downstream_target_gate_result_arbitration_ready_for_operator_review"
        next_operator_action = "R8v_operator_review_arbitrated_target_gate_results"
        blocking_reasons = []
    else:
        arbitration_status = "downstream_target_gate_result_arbitration_blocked_by_unclassified_target_mix"
        next_operator_action = "R8v_review_unclassified_target_gate_status_mix"
        blocking_reasons = ["target_gate_status_mix_not_unanimous_pass_or_explicit_block"]
    return {
        **base,
        "downstream_target_gate_result_arbitration_status": arbitration_status,
        "blocking_reasons": blocking_reasons,
        "next_operator_action": next_operator_action,
        "can_route_to_operator_review": (
            arbitration_status == "downstream_target_gate_result_arbitration_ready_for_operator_review"
        ),
        "can_emit_protective_control_candidate": False,
    }


def _field_rows_downstream_target_gate_operator_review_template(
    field_rows_downstream_target_gate_result_arbitration: dict[str, object],
) -> dict[str, object]:
    target_gate_decisions = [
        decision
        for decision in field_rows_downstream_target_gate_result_arbitration.get(
            "target_gate_decisions",
            [],
        )
        or []
        if isinstance(decision, dict)
    ]
    target_review_templates = []
    for decision in target_gate_decisions:
        target_review_templates.append(
            {
                "target_id": str(decision.get("target_id", "")),
                "target_gate_status": str(decision.get("target_gate_status", "")),
                "source_metrics_artifact": str(decision.get("source_metrics_artifact", "")),
                "batch_ids": [str(batch_id) for batch_id in decision.get("batch_ids", []) or []],
                "operator_review_decision": "TODO_operator_approved_or_rejected_or_hold",
                "reviewer_id": "TODO_field_operator_or_reviewer_id",
                "review_time": "TODO_iso8601_review_time",
                "review_notes": "TODO_review_notes",
                "boundary_acknowledgement": False,
                "can_write_to_actuator": False,
                "can_write_to_release_gate": False,
                "field_claim_upgrade_allowed": False,
            }
        )
    return {
        "downstream_target_gate_operator_review_template_id": (
            "R8u54_downstream_target_gate_operator_review_template"
        ),
        "template_path": str(ROWS_DOWNSTREAM_TARGET_GATE_OPERATOR_REVIEW_TEMPLATE_PATH),
        "operator_review_env_var": "R8V_TARGET_GATE_OPERATOR_REVIEW_PATH",
        "linked_result_arbitration_status": field_rows_downstream_target_gate_result_arbitration.get(
            "downstream_target_gate_result_arbitration_status",
            "",
        ),
        "expected_target_count": len(target_review_templates),
        "expected_target_ids": [
            template["target_id"]
            for template in target_review_templates
            if template.get("target_id")
        ],
        "required_top_level_fields": ["review_metadata", "review_rows"],
        "review_rows_type": "list_of_objects",
        "required_review_row_fields": [
            "target_id",
            "target_gate_status",
            "operator_review_decision",
            "reviewer_id",
            "review_time",
            "review_notes",
            "boundary_acknowledgement",
            "can_write_to_actuator",
            "can_write_to_release_gate",
            "field_claim_upgrade_allowed",
        ],
        "accepted_operator_review_decisions": [
            "operator_approved_for_post_review_gate",
            "operator_rejected_requires_remediation",
            "operator_hold_requires_more_evidence",
        ],
        "target_review_templates": target_review_templates,
        "model_core_layers": [
            "diagnostic_decision_layer",
            "closed_loop_execution_layer",
            "verification_governance_layer",
        ],
        "core_capabilities": [
            "controllability",
            "verifiability",
            "engineering_feasibility",
            "protectability",
        ],
        "technical_feature_mapping": {
            "technical_problem": (
                "A target-gate arbitration result still needs a traceable human review response before any "
                "later post-review control gate can consider protective action candidates."
            ),
            "technical_means": (
                "The operator-review template binds every arbitrated target decision to reviewer identity, "
                "review time, explicit approve/reject/hold decision, boundary acknowledgement, and no-write flags."
            ),
            "technical_effect": (
                "The closed-loop system can collect human review without letting review text or pass labels "
                "silently bypass actuator, release-gate, or field-claim protection."
            ),
            "prior_art_distinction_candidate": (
                "Unlike generic manual approval notes, the template is target-level, batch-preserving, "
                "machine-preflighted, and coupled to no-write grey-box safety boundaries."
            ),
        },
        "evidence_boundaries": [
            "The template is not an operator review response.",
            "Operator approval can only route to a later post-review gate; it cannot write actuators or release gates.",
            "Rejected or held targets remain remediation items, not control candidates.",
        ],
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "field_claim_upgrade_allowed": False,
    }


def _field_rows_downstream_target_gate_operator_review_preflight(
    field_rows_downstream_target_gate_result_arbitration: dict[str, object],
    operator_review_template: dict[str, object],
    operator_review_path: Path | None,
) -> dict[str, object]:
    arbitration_status = str(
        field_rows_downstream_target_gate_result_arbitration.get(
            "downstream_target_gate_result_arbitration_status",
            "",
        )
    )
    expected_target_ids = [
        str(target_id) for target_id in operator_review_template.get("expected_target_ids", []) or []
    ]
    decision_by_target_id = {
        str(decision.get("target_id", "")): decision
        for decision in field_rows_downstream_target_gate_result_arbitration.get(
            "target_gate_decisions",
            [],
        )
        or []
        if isinstance(decision, dict)
    }
    source_path = str(operator_review_path) if operator_review_path else ""
    base = {
        "downstream_target_gate_operator_review_preflight_id": (
            "R8u54_downstream_target_gate_operator_review_preflight"
        ),
        "preflight_path": str(ROWS_DOWNSTREAM_TARGET_GATE_OPERATOR_REVIEW_PREFLIGHT_PATH),
        "operator_review_env_var": "R8V_TARGET_GATE_OPERATOR_REVIEW_PATH",
        "operator_review_source_path": source_path,
        "linked_result_arbitration_status": arbitration_status,
        "expected_target_count": len(expected_target_ids),
        "expected_target_ids": expected_target_ids,
        "model_core_layers": [
            "diagnostic_decision_layer",
            "closed_loop_execution_layer",
            "verification_governance_layer",
        ],
        "core_capabilities": [
            "controllability",
            "verifiability",
            "engineering_feasibility",
            "protectability",
        ],
    }
    can_accept_review = (
        arbitration_status == "downstream_target_gate_result_arbitration_ready_for_operator_review"
        and bool(field_rows_downstream_target_gate_result_arbitration.get("can_route_to_operator_review", False))
    )
    if not can_accept_review:
        return {
            **base,
            "downstream_target_gate_operator_review_preflight_status": (
                "downstream_target_gate_operator_review_preflight_blocked_by_arbitration"
            ),
            "source_status": "operator_review_not_checked_until_arbitration_ready",
            "submitted_operator_review_count": 0,
            "approved_operator_review_count": 0,
            "rejected_operator_review_count": 0,
            "hold_operator_review_count": 0,
            "missing_target_ids": expected_target_ids,
            "unknown_target_ids": [],
            "operator_review_validations": [],
            "blocking_reasons": [
                f"result_arbitration_status={arbitration_status or 'not_available'}",
                "operator review package cannot be accepted until target-gate arbitration is ready",
            ],
            "next_operator_action": field_rows_downstream_target_gate_result_arbitration.get(
                "next_operator_action",
                "R8v_fix_target_gate_result_arbitration_first",
            ),
            "can_route_to_post_review_gate": False,
            "can_emit_protective_control_candidate": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "field_claim_upgrade_allowed": False,
        }
    if operator_review_path is None:
        return {
            **base,
            "downstream_target_gate_operator_review_preflight_status": (
                "downstream_target_gate_operator_review_preflight_waiting_for_review_package"
            ),
            "source_status": "operator_review_path_not_configured",
            "submitted_operator_review_count": 0,
            "approved_operator_review_count": 0,
            "rejected_operator_review_count": 0,
            "hold_operator_review_count": 0,
            "missing_target_ids": expected_target_ids,
            "unknown_target_ids": [],
            "operator_review_validations": [],
            "blocking_reasons": ["R8V_TARGET_GATE_OPERATOR_REVIEW_PATH_not_configured"],
            "next_operator_action": "R8v_submit_operator_review_response_package",
            "can_route_to_post_review_gate": False,
            "can_emit_protective_control_candidate": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "field_claim_upgrade_allowed": False,
        }
    if not operator_review_path.exists():
        return {
            **base,
            "downstream_target_gate_operator_review_preflight_status": (
                "downstream_target_gate_operator_review_preflight_missing_review_package"
            ),
            "source_status": "operator_review_file_missing",
            "submitted_operator_review_count": 0,
            "approved_operator_review_count": 0,
            "rejected_operator_review_count": 0,
            "hold_operator_review_count": 0,
            "missing_target_ids": expected_target_ids,
            "unknown_target_ids": [],
            "operator_review_validations": [],
            "blocking_reasons": ["operator_review_file_missing"],
            "next_operator_action": "R8v_submit_operator_review_response_package",
            "can_route_to_post_review_gate": False,
            "can_emit_protective_control_candidate": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "field_claim_upgrade_allowed": False,
        }
    try:
        payload = json.loads(operator_review_path.read_text(encoding="utf-8"))
    except JSONDecodeError as exc:
        return {
            **base,
            "downstream_target_gate_operator_review_preflight_status": (
                "downstream_target_gate_operator_review_preflight_invalid_json"
            ),
            "source_status": "operator_review_invalid_json",
            "submitted_operator_review_count": 0,
            "approved_operator_review_count": 0,
            "rejected_operator_review_count": 0,
            "hold_operator_review_count": 0,
            "missing_target_ids": expected_target_ids,
            "unknown_target_ids": [],
            "operator_review_validations": [],
            "blocking_reasons": [f"invalid_json:{exc.msg}"],
            "next_operator_action": "R8v_fix_operator_review_package_json",
            "can_route_to_post_review_gate": False,
            "can_emit_protective_control_candidate": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "field_claim_upgrade_allowed": False,
        }
    if not isinstance(payload, dict) or not isinstance(payload.get("review_rows"), list):
        return {
            **base,
            "downstream_target_gate_operator_review_preflight_status": (
                "downstream_target_gate_operator_review_preflight_invalid_shape"
            ),
            "source_status": "operator_review_invalid_shape",
            "submitted_operator_review_count": 0,
            "approved_operator_review_count": 0,
            "rejected_operator_review_count": 0,
            "hold_operator_review_count": 0,
            "missing_target_ids": expected_target_ids,
            "unknown_target_ids": [],
            "operator_review_validations": [],
            "blocking_reasons": ["root_must_be_object_with_review_rows_list"],
            "next_operator_action": "R8v_fix_operator_review_package_shape",
            "can_route_to_post_review_gate": False,
            "can_emit_protective_control_candidate": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "field_claim_upgrade_allowed": False,
        }

    required_fields = [
        str(field) for field in operator_review_template.get("required_review_row_fields", []) or []
    ]
    accepted_decisions = [
        str(decision)
        for decision in operator_review_template.get("accepted_operator_review_decisions", []) or []
    ]
    review_rows = payload.get("review_rows", [])
    validations: list[dict[str, object]] = []
    seen_target_ids: set[str] = set()
    unknown_target_ids: list[str] = []
    any_write_requested = False
    for index, row in enumerate(review_rows):
        if not isinstance(row, dict):
            validations.append(
                {
                    "row_index": index,
                    "target_id": "",
                    "operator_review_row_status": "operator_review_rejected_invalid_row_shape",
                    "operator_review_decision": "",
                    "missing_fields": ["row_must_be_object"],
                    "boundary_violations": [],
                }
            )
            continue
        target_id = str(row.get("target_id", ""))
        seen_target_ids.add(target_id)
        decision = decision_by_target_id.get(target_id)
        if decision is None:
            unknown_target_ids.append(target_id)
        missing_fields = [field for field in required_fields if field not in row]
        boundary_violations: list[str] = []
        if decision is None:
            boundary_violations.append("unknown_target_id")
        expected_target_gate_status = str((decision or {}).get("target_gate_status", ""))
        if str(row.get("target_gate_status", "")) != expected_target_gate_status:
            boundary_violations.append("target_gate_status_mismatch")
        operator_review_decision = str(row.get("operator_review_decision", ""))
        if operator_review_decision not in accepted_decisions:
            boundary_violations.append("operator_review_decision_not_accepted_value")
        for text_field in ["reviewer_id", "review_time", "review_notes"]:
            if text_field in row and not str(row.get(text_field, "")).strip():
                boundary_violations.append(f"{text_field}_must_be_non_empty")
        if row.get("boundary_acknowledgement") is not True:
            boundary_violations.append("boundary_acknowledgement_required")
        for bool_field in [
            "boundary_acknowledgement",
            "can_write_to_actuator",
            "can_write_to_release_gate",
            "field_claim_upgrade_allowed",
        ]:
            if bool_field in row and not isinstance(row.get(bool_field), bool):
                boundary_violations.append(f"{bool_field}_must_be_boolean")
        if bool(row.get("can_write_to_actuator", False)):
            any_write_requested = True
            boundary_violations.append("operator_review_requests_actuator_write")
        if bool(row.get("can_write_to_release_gate", False)):
            any_write_requested = True
            boundary_violations.append("operator_review_requests_release_gate_write")
        if bool(row.get("field_claim_upgrade_allowed", False)):
            boundary_violations.append("operator_review_requests_field_claim_upgrade")
        operator_review_row_status = (
            "operator_review_row_accepted"
            if not missing_fields and not boundary_violations
            else "operator_review_row_rejected_by_contract"
        )
        validations.append(
            {
                "row_index": index,
                "target_id": target_id,
                "operator_review_row_status": operator_review_row_status,
                "operator_review_decision": operator_review_decision,
                "missing_fields": missing_fields,
                "boundary_violations": boundary_violations,
            }
        )

    missing_target_ids = [target_id for target_id in expected_target_ids if target_id not in seen_target_ids]
    accepted_rows = [
        validation
        for validation in validations
        if validation.get("operator_review_row_status") == "operator_review_row_accepted"
    ]
    approved_count = sum(
        1
        for validation in accepted_rows
        if validation.get("operator_review_decision")
        == "operator_approved_for_post_review_gate"
    )
    rejected_count = sum(
        1
        for validation in accepted_rows
        if validation.get("operator_review_decision") == "operator_rejected_requires_remediation"
    )
    hold_count = sum(
        1
        for validation in accepted_rows
        if validation.get("operator_review_decision") == "operator_hold_requires_more_evidence"
    )
    contract_rejected_count = len(validations) - len(accepted_rows)
    if missing_target_ids or unknown_target_ids:
        status = "downstream_target_gate_operator_review_preflight_failed_target_coverage"
        next_operator_action = "R8v_complete_operator_review_target_coverage"
    elif any_write_requested:
        status = "downstream_target_gate_operator_review_preflight_failed_protective_write_boundary"
        next_operator_action = "R8v_remove_operator_review_actuator_or_release_write_requests"
    elif contract_rejected_count:
        status = "downstream_target_gate_operator_review_preflight_failed_review_contract"
        next_operator_action = "R8v_fix_operator_review_required_fields_and_boundaries"
    elif rejected_count or hold_count:
        status = "downstream_target_gate_operator_review_preflight_blocked_by_operator_decision"
        next_operator_action = "R8v_remediate_operator_rejected_or_held_targets"
    elif approved_count == len(expected_target_ids):
        status = "downstream_target_gate_operator_review_preflight_passed_ready_for_post_review_gate"
        next_operator_action = "R8v_route_operator_approved_targets_to_post_review_gate"
    else:
        status = "downstream_target_gate_operator_review_preflight_blocked_by_unclassified_review_mix"
        next_operator_action = "R8v_review_unclassified_operator_decision_mix"
    return {
        **base,
        "downstream_target_gate_operator_review_preflight_status": status,
        "source_status": "operator_review_package_loaded",
        "submitted_operator_review_count": len(validations),
        "accepted_operator_review_count": len(accepted_rows),
        "approved_operator_review_count": approved_count,
        "rejected_operator_review_count": rejected_count,
        "hold_operator_review_count": hold_count,
        "contract_rejected_operator_review_count": contract_rejected_count,
        "missing_target_ids": missing_target_ids,
        "unknown_target_ids": unknown_target_ids,
        "operator_review_validations": validations,
        "blocking_reasons": [
            reason
            for reason in [
                f"missing_target_ids={missing_target_ids}" if missing_target_ids else "",
                f"unknown_target_ids={unknown_target_ids}" if unknown_target_ids else "",
                "operator_review_requests_protective_write" if any_write_requested else "",
                f"contract_rejected_operator_review_count={contract_rejected_count}"
                if contract_rejected_count
                else "",
                f"rejected_operator_review_count={rejected_count}" if rejected_count else "",
                f"hold_operator_review_count={hold_count}" if hold_count else "",
            ]
            if reason
        ],
        "next_operator_action": next_operator_action,
        "can_route_to_post_review_gate": (
            status == "downstream_target_gate_operator_review_preflight_passed_ready_for_post_review_gate"
        ),
        "can_emit_protective_control_candidate": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "field_claim_upgrade_allowed": False,
    }


def _field_rows_downstream_target_gate_post_review_gate(
    operator_review_preflight: dict[str, object],
) -> dict[str, object]:
    review_status = str(
        operator_review_preflight.get(
            "downstream_target_gate_operator_review_preflight_status",
            "",
        )
    )
    validations = [
        validation
        for validation in operator_review_preflight.get("operator_review_validations", []) or []
        if isinstance(validation, dict)
    ]
    expected_target_ids = [
        str(target_id) for target_id in operator_review_preflight.get("expected_target_ids", []) or []
    ]
    approved_validations = [
        validation
        for validation in validations
        if validation.get("operator_review_row_status") == "operator_review_row_accepted"
        and validation.get("operator_review_decision") == "operator_approved_for_post_review_gate"
    ]
    candidate_targets = [
        {
            "target_id": str(validation.get("target_id", "")),
            "post_review_target_status": "post_review_target_ready_for_protective_candidate_evaluation",
            "permitted_candidate_scope": "protective_control_candidate_only_no_actuator_or_release_write",
            "required_next_gates": [
                "protective_control_candidate_policy_gate",
                "actuator_safety_interlock_gate",
                "operator_final_execution_review",
                "release_gate_remains_separate_and_blocked",
            ],
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "field_claim_upgrade_allowed": False,
        }
        for validation in approved_validations
    ]
    base = {
        "downstream_target_gate_post_review_gate_id": (
            "R8u55_downstream_target_gate_post_review_protective_candidate_gate"
        ),
        "post_review_gate_path": str(ROWS_DOWNSTREAM_TARGET_GATE_POST_REVIEW_GATE_PATH),
        "linked_operator_review_preflight_status": review_status,
        "expected_target_count": len(expected_target_ids),
        "expected_target_ids": expected_target_ids,
        "approved_operator_review_count": len(approved_validations),
        "post_review_candidate_targets": candidate_targets,
        "model_core_layers": [
            "diagnostic_decision_layer",
            "closed_loop_execution_layer",
            "verification_governance_layer",
        ],
        "core_capabilities": [
            "controllability",
            "verifiability",
            "engineering_feasibility",
            "protectability",
        ],
        "technical_feature_mapping": {
            "technical_problem": (
                "Operator-approved downstream target-gate results still need a deterministic boundary before "
                "they can become even protective control candidates in a low-cost grey-box water-treatment loop."
            ),
            "technical_means": (
                "A post-review gate checks that every target has an accepted operator approval, converts the "
                "approved targets into protective-candidate evaluation rows, and preserves actuator, release-gate, "
                "and field-claim write prohibitions."
            ),
            "technical_effect": (
                "The system separates human-reviewed evidence from executable control, reducing accidental "
                "promotion of replay/holdout success into pump, valve, dose, or release actions."
            ),
            "prior_art_distinction_candidate": (
                "Unlike generic human-in-the-loop approval, the gate is downstream-target specific, batch-traceable, "
                "and limited to protective candidate evaluation under explicit no-write boundaries."
            ),
        },
        "evidence_boundaries": [
            "Post-review readiness is not actuator permission and is not release clearance.",
            "A protective control candidate still needs policy, safety interlock, actuator feedback, and final operator gates.",
            "Release gate and field-supported claim upgrades remain separate blocked boundaries.",
        ],
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "field_claim_upgrade_allowed": False,
    }
    if review_status != "downstream_target_gate_operator_review_preflight_passed_ready_for_post_review_gate":
        return {
            **base,
            "downstream_target_gate_post_review_gate_status": (
                "downstream_target_gate_post_review_gate_blocked_by_operator_review_preflight"
            ),
            "blocking_reasons": [
                f"operator_review_preflight_status={review_status or 'not_available'}"
            ],
            "next_operator_action": operator_review_preflight.get(
                "next_operator_action",
                "R8v_fix_operator_review_preflight_first",
            ),
            "can_route_to_protective_candidate_evaluation": False,
            "can_emit_protective_control_candidate": False,
        }
    if len(approved_validations) != len(expected_target_ids):
        return {
            **base,
            "downstream_target_gate_post_review_gate_status": (
                "downstream_target_gate_post_review_gate_blocked_by_incomplete_operator_approval"
            ),
            "blocking_reasons": [
                f"approved_operator_review_count={len(approved_validations)}",
                f"expected_target_count={len(expected_target_ids)}",
            ],
            "next_operator_action": "R8v_complete_operator_approval_for_all_target_gates",
            "can_route_to_protective_candidate_evaluation": False,
            "can_emit_protective_control_candidate": False,
        }
    return {
        **base,
        "downstream_target_gate_post_review_gate_status": (
            "downstream_target_gate_post_review_gate_passed_ready_for_protective_candidate_evaluation"
        ),
        "blocking_reasons": [],
        "next_operator_action": "R8v_evaluate_operator_approved_protective_control_candidate",
        "can_route_to_protective_candidate_evaluation": True,
        "can_emit_protective_control_candidate": True,
    }


def _field_rows_downstream_target_gate_protective_candidate_evaluation(
    post_review_gate: dict[str, object],
) -> dict[str, object]:
    post_review_status = str(
        post_review_gate.get(
            "downstream_target_gate_post_review_gate_status",
            "",
        )
    )
    candidate_targets = [
        target
        for target in post_review_gate.get("post_review_candidate_targets", []) or []
        if isinstance(target, dict)
    ]
    expected_target_ids = [str(target_id) for target_id in post_review_gate.get("expected_target_ids", []) or []]
    candidate_target_ids = [str(target.get("target_id", "")) for target in candidate_targets]
    target_id_set = set(candidate_target_ids)
    target_contributions = []
    if "agent51_catalyst_proxy_holdout" in target_id_set:
        target_contributions.append(
            {
                "target_id": "agent51_catalyst_proxy_holdout",
                "contribution": (
                    "catalyst_activity_proxy_and_regeneration_or_replacement_boundary"
                ),
                "candidate_actions": [
                    "hold_for_catalyst_proxy_review",
                    "catalyst_regeneration_candidate",
                    "catalyst_replacement_candidate",
                ],
            }
        )
    if "agent49_guardrail_context" in target_id_set:
        target_contributions.append(
            {
                "target_id": "agent49_guardrail_context",
                "contribution": "multi_facility_guardrail_context_and_action_constraints",
                "candidate_actions": [
                    "protective_recycle_candidate",
                    "extend_retention_candidate",
                    "dose_adjustment_candidate",
                    "unit_switch_candidate",
                ],
            }
        )
    if "agent52_replay_clearance" in target_id_set:
        target_contributions.append(
            {
                "target_id": "agent52_replay_clearance",
                "contribution": "state_action_reward_replay_clearance_and_regret_boundary",
                "candidate_actions": [
                    "replay_supported_protective_action_candidate",
                    "continue_block_if_replay_regret_or_false_positive_cost_exceeds_gate",
                ],
            }
        )
    if "r7_evidence_chain" in target_id_set:
        target_contributions.append(
            {
                "target_id": "r7_evidence_chain",
                "contribution": "field_package_replay_holdout_and_evidence_chain_boundary",
                "candidate_actions": [
                    "field_evidence_preserving_hold_candidate",
                    "release_gate_remains_blocked_until_separate_release_validation",
                ],
            }
        )

    required_target_ids = [
        "agent51_catalyst_proxy_holdout",
        "agent49_guardrail_context",
        "agent52_replay_clearance",
        "r7_evidence_chain",
    ]
    missing_required_target_ids = [
        target_id for target_id in required_target_ids if target_id not in target_id_set
    ]
    no_write_boundary_preserved = all(
        target.get("can_write_to_actuator") is False
        and target.get("can_write_to_release_gate") is False
        and target.get("field_claim_upgrade_allowed") is False
        for target in candidate_targets
    )
    candidate_action_bundle = {
        "candidate_bundle_id": "R8U56_PROTECTIVE_CONTROL_CANDIDATE_BUNDLE",
        "candidate_scope": "protective_control_candidate_only_no_actuator_no_release_write",
        "candidate_actions": [
            "temporarily_hold_batch",
            "extend_retention_time",
            "increase_recycle_or_return_flow_for_review",
            "adjust_dose_as_candidate_not_command",
            "trigger_catalyst_regeneration_or_replacement_review",
            "switch_or_bypass_unit_as_candidate_not_command",
            "keep_release_gate_blocked",
        ],
        "candidate_inputs": [
            "operator_approved_target_gate_results",
            "Agent51 catalyst proxy holdout boundary",
            "Agent49 guardrail context",
            "Agent52 replay clearance",
            "R7 field evidence chain",
        ],
        "required_final_gates_before_execution": [
            "protective_control_policy_gate",
            "actuator_safety_interlock_gate",
            "operator_final_execution_review",
            "actuator_feedback_replay_gate",
            "release_gate_separate_validation_remains_required",
        ],
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "field_claim_upgrade_allowed": False,
    }
    base = {
        "downstream_target_gate_protective_candidate_evaluation_id": (
            "R8u56_downstream_target_gate_protective_candidate_evaluation"
        ),
        "protective_candidate_evaluation_path": str(
            ROWS_DOWNSTREAM_TARGET_GATE_PROTECTIVE_CANDIDATE_EVALUATION_PATH
        ),
        "linked_post_review_gate_status": post_review_status,
        "expected_target_count": len(expected_target_ids),
        "expected_target_ids": expected_target_ids,
        "candidate_target_count": len(candidate_targets),
        "candidate_target_ids": candidate_target_ids,
        "target_contributions": target_contributions,
        "candidate_action_bundle": candidate_action_bundle,
        "model_core_layers": [
            "diagnostic_decision_layer",
            "closed_loop_execution_layer",
            "verification_governance_layer",
        ],
        "core_capabilities": [
            "controllability",
            "verifiability",
            "engineering_feasibility",
            "protectability",
        ],
        "technical_feature_mapping": {
            "technical_problem": (
                "Even post-review target approval only proves evidence readiness; it does not define a bounded, "
                "non-executing protective control candidate that can be reviewed before field actuation."
            ),
            "technical_means": (
                "A protective candidate evaluation gate converts the four approved downstream target contributions "
                "into a candidate action bundle, preserves target-specific evidence paths, and requires final "
                "policy, interlock, operator, actuator-feedback, and release-gate validations before execution."
            ),
            "technical_effect": (
                "The grey-box loop can present actionable protective options under delayed low-cost sensing while "
                "preventing automatic pump, valve, dose, or release writes."
            ),
            "prior_art_distinction_candidate": (
                "Unlike generic multi-agent action selection, this candidate gate separates evidence approval, "
                "protective candidate generation, final execution review, and release validation in a field "
                "replay-governed water-treatment loop."
            ),
        },
        "evidence_boundaries": [
            "Protective candidate evaluation is not online control execution.",
            "It cannot write actuator, pump, valve, dosing, bypass, or release-gate commands.",
            "It cannot upgrade synthetic/template/sample evidence to field-supported claims.",
            "Final execution still needs policy gate, safety interlock, operator final review, and actuator feedback.",
        ],
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "field_claim_upgrade_allowed": False,
    }
    if post_review_status != "downstream_target_gate_post_review_gate_passed_ready_for_protective_candidate_evaluation":
        return {
            **base,
            "downstream_target_gate_protective_candidate_evaluation_status": (
                "protective_candidate_evaluation_blocked_by_post_review_gate"
            ),
            "blocking_reasons": [
                f"post_review_gate_status={post_review_status or 'not_available'}"
            ],
            "next_operator_action": post_review_gate.get(
                "next_operator_action",
                "R8v_fix_post_review_gate_first",
            ),
            "can_emit_protective_control_candidate": False,
            "can_route_to_final_execution_review": False,
        }
    if missing_required_target_ids:
        return {
            **base,
            "downstream_target_gate_protective_candidate_evaluation_status": (
                "protective_candidate_evaluation_blocked_by_missing_target_contributions"
            ),
            "blocking_reasons": [
                f"missing_required_target_ids={missing_required_target_ids}"
            ],
            "next_operator_action": "R8v_complete_all_downstream_target_contributions_before_candidate_evaluation",
            "can_emit_protective_control_candidate": False,
            "can_route_to_final_execution_review": False,
        }
    if not no_write_boundary_preserved:
        return {
            **base,
            "downstream_target_gate_protective_candidate_evaluation_status": (
                "protective_candidate_evaluation_failed_no_write_boundary"
            ),
            "blocking_reasons": ["candidate_target_requested_actuator_release_or_field_claim_write"],
            "next_operator_action": "R8v_remove_candidate_target_write_requests_before_evaluation",
            "can_emit_protective_control_candidate": False,
            "can_route_to_final_execution_review": False,
        }
    return {
        **base,
        "downstream_target_gate_protective_candidate_evaluation_status": (
            "protective_candidate_evaluation_passed_ready_for_final_execution_review"
        ),
        "blocking_reasons": [],
        "next_operator_action": "R8v_submit_protective_candidate_bundle_for_final_execution_review",
        "can_emit_protective_control_candidate": True,
        "can_route_to_final_execution_review": True,
    }


def _r8v_target_gate_command_contract(target_id: str) -> dict[str, str]:
    contracts = {
        "agent51_catalyst_proxy_holdout": {
            "validation_command": ".venv/bin/python experiments/run_agent51_catalyst_activity_proxy.py",
            "expected_metrics_artifact": "outputs/catalyst_activity_proxy/catalyst_activity_proxy_metrics.json",
        },
        "agent49_guardrail_context": {
            "validation_command": ".venv/bin/python experiments/run_agent49_multi_facility_collaborative_control.py",
            "expected_metrics_artifact": "outputs/multi_facility_collaborative_control/collaborative_control_metrics.json",
        },
        "agent52_replay_clearance": {
            "validation_command": ".venv/bin/python experiments/run_agent52_multi_facility_replay_evaluation.py",
            "expected_metrics_artifact": "outputs/multi_facility_replay_evaluation/replay_evaluation_metrics.json",
        },
        "r7_evidence_chain": {
            "validation_command": ".venv/bin/python experiments/run_r7_real_field_replay_pipeline.py",
            "expected_metrics_artifact": "outputs/r7_real_field_replay_pipeline/r7_real_field_replay_pipeline_metrics.json",
        },
    }
    return contracts.get(
        target_id,
        {
            "validation_command": "R8v_target_gate_command_not_mapped",
            "expected_metrics_artifact": "R8v_target_gate_metrics_artifact_not_mapped",
        },
    )


def _value_matches_field_schema(field: str, value: object) -> bool:
    expected = _field_schema(field).get("type")
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == ["number", "integer"]:
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "string":
        return isinstance(value, str) and bool(value.strip())
    return True


def _is_template_marker_value(value: object) -> bool:
    if value is None:
        return False
    lowered = str(value).strip().lower()
    if not lowered:
        return False
    return (
        lowered.startswith("todo")
        or "todo_" in lowered
        or "template" in lowered
        or lowered in {"field_validation_required", "replace_me", "sample_only"}
    )


def _is_field_origin_value(value: object) -> bool:
    if value is None:
        return False
    text = str(value).strip()
    if not text:
        return False
    lowered = text.lower()
    if lowered.startswith("todo") or "todo_" in lowered or "template" in lowered:
        return False
    if lowered in {"nan", "none", "null"}:
        return False
    return "field" in lowered and "synthetic" not in lowered and "todo" not in lowered


def _field_rows_patch_plan(
    report,
    field_rows_source: dict[str, object],
    field_rows_schema_validation: dict[str, object] | None = None,
    field_rows_batch_bundle_preflight: dict[str, object] | None = None,
    field_rows_temporal_window_preflight: dict[str, object] | None = None,
    field_rows_scenario_semantic_preflight: dict[str, object] | None = None,
) -> dict[str, object]:
    field_acceptance = report.metrics["field_row_acceptance"]
    row_collection_plan = report.metrics["row_collection_plan"]
    expected_tables = [str(table) for table in field_rows_source.get("expected_tables", [])]
    patch_items: list[dict[str, object]] = []
    field_rows_schema_validation = field_rows_schema_validation or {}
    field_rows_batch_bundle_preflight = field_rows_batch_bundle_preflight or {}
    field_rows_temporal_window_preflight = field_rows_temporal_window_preflight or {}
    field_rows_scenario_semantic_preflight = field_rows_scenario_semantic_preflight or {}

    source_status = str(field_rows_source.get("field_rows_source_status", "unknown"))
    source_path = str(field_rows_source.get("field_rows_source_path", ""))
    if source_status == "field_rows_file_missing":
        patch_items.append(
            {
                "patch_id": "R8P_SOURCE_MISSING_FIELD_ROWS_FILE",
                "priority": "P0",
                "patch_type": "source_preflight",
                "blocking_condition": "field_rows_file_missing",
                "target": source_path,
                "operator_action": (
                    "Create a real field rows JSON file or a six-table CSV directory at this path, or set "
                    "PRESSURE_RESOLUTION_REPLAY_ROWS_PATH to either source format. Use templates only as a form, "
                    "then replace every TODO/template marker with field-origin rows."
                ),
                "required_tables": expected_tables,
                "acceptance_check": (
                    "field_rows_source_status must become field_rows_file_loaded, field_rows_directory_loaded, "
                    "or a scenario-level accepted row status."
                ),
                "evidence_boundary": "Creating the file is not field evidence; rows still must pass R8p acceptance.",
            }
        )

    for table in field_rows_source.get("missing_tables", []) or []:
        patch_items.append(
            {
                "patch_id": f"R8P_MISSING_TABLE_{str(table).upper()}",
                "priority": "P1",
                "patch_type": "source_preflight",
                "blocking_condition": "missing_table",
                "target": str(table),
                "operator_action": f"Add `{table}` as a list of field-origin row objects.",
                "required_fields": _required_fields_for_table(str(table)),
                "acceptance_check": f"`{table}` is present, list-shaped, and non-empty.",
                "evidence_boundary": "A present table still must include non-template values and scenario-linked batch_id rows.",
            }
        )

    for table in field_rows_source.get("empty_tables", []) or []:
        patch_items.append(
            {
                "patch_id": f"R8P_EMPTY_TABLE_{str(table).upper()}",
                "priority": "P1",
                "patch_type": "source_preflight",
                "blocking_condition": "empty_table",
                "target": str(table),
                "operator_action": f"Populate `{table}` with at least one real row for each required pressure-resolution scenario.",
                "required_fields": _required_fields_for_table(str(table)),
                "acceptance_check": f"`{table}` has object rows with real field values.",
                "evidence_boundary": "Synthetic/sample/template rows remain rejected even if the table is non-empty.",
            }
        )

    for shape in field_rows_source.get("invalid_table_shapes", []) or []:
        patch_items.append(
            {
                "patch_id": f"R8P_INVALID_SHAPE_{_safe_patch_token(str(shape))}",
                "priority": "P0",
                "patch_type": "source_preflight",
                "blocking_condition": "invalid_shape",
                "target": str(shape),
                "operator_action": "Fix JSON shape: root must be an object mapping table names to lists of row objects.",
                "acceptance_check": "invalid_table_shapes must be empty before row-level acceptance can be trusted.",
                "evidence_boundary": "Shape validity only proves the package can be read, not that evidence is accepted.",
            }
        )

    for table in field_rows_source.get("unknown_tables", []) or []:
        patch_items.append(
            {
                "patch_id": f"R8P_UNKNOWN_TABLE_{_safe_patch_token(str(table))}",
                "priority": "P2",
                "patch_type": "source_preflight",
                "blocking_condition": "unknown_table",
                "target": str(table),
                "operator_action": "Remove the unknown table or map it to one of the expected R8p tables.",
                "acceptance_check": "unknown_tables should be empty for a clean field rows package.",
                "evidence_boundary": "Unknown tables are ignored by the current acceptance gate.",
            }
        )

    for table_validation in field_rows_schema_validation.get("table_validations", []) or []:
        if not isinstance(table_validation, dict):
            continue
        table = str(table_validation.get("table", "unknown_table"))
        if int(table_validation.get("missing_required_field_count", 0) or 0):
            patch_items.append(
                {
                    "patch_id": f"R8P_SCHEMA_REQUIRED_FIELDS_{_safe_patch_token(table)}",
                    "priority": "P1",
                    "patch_type": "schema_row_contract",
                    "blocking_condition": "missing_required_fields",
                    "target": table,
                    "operator_action": f"Fill missing required fields in `{table}` rows before scenario acceptance.",
                    "missing_required_fields_by_row": table_validation.get("missing_required_fields_by_row", []),
                    "acceptance_check": f"`{table}` missing_required_field_count becomes 0.",
                    "evidence_boundary": "Required-field presence only proves schema readiness, not field evidence.",
                }
            )
        if int(table_validation.get("invalid_type_count", 0) or 0):
            patch_items.append(
                {
                    "patch_id": f"R8P_SCHEMA_INVALID_TYPES_{_safe_patch_token(table)}",
                    "priority": "P1",
                    "patch_type": "schema_row_contract",
                    "blocking_condition": "invalid_required_field_types",
                    "target": table,
                    "operator_action": f"Fix required field types in `{table}` rows according to pressure_resolution_replay_rows_schema.json.",
                    "invalid_types_by_row": table_validation.get("invalid_types_by_row", []),
                    "acceptance_check": f"`{table}` invalid_type_count becomes 0.",
                    "evidence_boundary": "Type validity only proves schema readiness, not field evidence.",
                }
            )
        if int(table_validation.get("template_marker_gap_count", 0) or 0):
            patch_items.append(
                {
                    "patch_id": f"R8P_SCHEMA_TEMPLATE_MARKERS_{_safe_patch_token(table)}",
                    "priority": "P0",
                    "patch_type": "template_marker_contract",
                    "blocking_condition": "template_or_todo_required_values",
                    "target": table,
                    "operator_action": (
                        f"Replace TODO/template/sample placeholder values in `{table}` required fields with real "
                        "field-origin measurements, labels, review records, or replay action values."
                    ),
                    "template_marker_gaps_by_row": table_validation.get("template_marker_gaps_by_row", []),
                    "acceptance_check": f"`{table}` template_marker_gap_count becomes 0.",
                    "evidence_boundary": (
                        "Replacing template markers is required before any row can be considered field evidence; "
                        "rows still need field-origin provenance, scenario linkage, downstream gates, and human review."
                    ),
                }
            )
        if int(table_validation.get("field_origin_gap_count", 0) or 0):
            patch_items.append(
                {
                    "patch_id": f"R8P_SCHEMA_FIELD_ORIGIN_{_safe_patch_token(table)}",
                    "priority": "P0",
                    "patch_type": "field_origin_contract",
                    "blocking_condition": "non_field_data_origin",
                    "target": table,
                    "operator_action": (
                        f"Replace non-field `data_origin` values in `{table}` rows with field-origin provenance "
                        "from the real source package; synthetic/template/TODO provenance is rejected."
                    ),
                    "field_origin_gaps_by_row": table_validation.get("field_origin_gaps_by_row", []),
                    "acceptance_check": f"`{table}` field_origin_gap_count becomes 0.",
                    "evidence_boundary": (
                        "Field-origin provenance is only an entry gate; rows still need same-batch linkage, "
                        "scenario acceptance, downstream replay/holdout gates, and human review."
                    ),
                }
            )

    batch_preflight_status = str(
        field_rows_batch_bundle_preflight.get("field_rows_batch_bundle_preflight_status", "")
    )
    if batch_preflight_status in {
        "batch_bundle_preflight_failed_no_candidate_batches",
        "batch_bundle_preflight_failed_partial_batch_bundles",
        "batch_bundle_preflight_failed_no_complete_six_table_batches",
    }:
        for scenario_bundle in field_rows_batch_bundle_preflight.get("scenario_bundle_status", []) or []:
            if not isinstance(scenario_bundle, dict):
                continue
            if scenario_bundle.get("bundle_preflight_status") == "scenario_has_complete_six_table_batch_bundle":
                continue
            scenario_id = str(scenario_bundle.get("scenario_id", "unknown_scenario"))
            patch_items.append(
                {
                    "patch_id": f"R8P_BATCH_BUNDLE_{_safe_patch_token(scenario_id)}",
                    "priority": "P1",
                    "patch_type": "batch_bundle_contract",
                    "blocking_condition": str(scenario_bundle.get("bundle_preflight_status", "unknown")),
                    "target": scenario_id,
                    "scenario_type": scenario_bundle.get("scenario_type"),
                    "operator_action": (
                        "Complete a same-batch six-table field evidence bundle for this pressure-resolution "
                        "scenario. Use one real `batch_id` shared by sensor, pressure/headloss, operation, "
                        "offline lab, fast proxy, and Agent52 replay tables."
                    ),
                    "candidate_batches_seen": scenario_bundle.get("candidate_batches", []),
                    "complete_candidate_batches": scenario_bundle.get("complete_candidate_batches", []),
                    "missing_tables_by_candidate_batch": scenario_bundle.get("missing_tables_by_candidate_batch", {}),
                    "required_tables": field_rows_batch_bundle_preflight.get("expected_tables", expected_tables),
                    "acceptance_check": (
                        "field_rows_batch_bundle_preflight_status becomes "
                        "batch_bundle_preflight_passed_ready_for_scenario_acceptance, then scenario acceptance can run."
                    ),
                    "evidence_boundary": (
                        "A complete six-table batch only proves bundle availability. Semantic validity, replay routing, "
                        "holdout gates, operator review, and release protection still apply."
                    ),
                }
            )

    temporal_preflight_status = str(
        field_rows_temporal_window_preflight.get("field_rows_temporal_window_preflight_status", "")
    )
    if temporal_preflight_status in {
        "temporal_window_preflight_failed_hold_time_budget_contract",
        "temporal_window_preflight_failed_temporal_order_contract",
    }:
        for scenario_temporal in field_rows_temporal_window_preflight.get("scenario_temporal_status", []) or []:
            if not isinstance(scenario_temporal, dict):
                continue
            if scenario_temporal.get("temporal_preflight_status") == "scenario_has_temporal_valid_batch":
                continue
            scenario_id = str(scenario_temporal.get("scenario_id", "unknown_scenario"))
            patch_items.append(
                {
                    "patch_id": f"R8P_TEMPORAL_WINDOW_{_safe_patch_token(scenario_id)}",
                    "priority": "P1",
                    "patch_type": "temporal_window_contract",
                    "blocking_condition": str(scenario_temporal.get("temporal_preflight_status", "unknown")),
                    "target": scenario_id,
                    "scenario_type": scenario_temporal.get("scenario_type"),
                    "operator_action": (
                        "Fix same-batch timestamp ordering and hold/recycle time budget so low-frequency sensor, "
                        "pressure/headloss event, fast proxy, offline lab label, and operator review evidence can "
                        "arrive before the batch is released."
                    ),
                    "complete_candidate_batches": scenario_temporal.get("complete_candidate_batches", []),
                    "violations_by_batch": scenario_temporal.get("violations_by_batch", {}),
                    "latency_margin_min_by_batch": scenario_temporal.get("latency_margin_min_by_batch", {}),
                    "acceptance_check": (
                        "field_rows_temporal_window_preflight_status becomes "
                        "temporal_window_preflight_passed_ready_for_scenario_acceptance."
                    ),
                    "evidence_boundary": (
                        "A temporal-valid batch only proves the circular hold/recycle window can support evidence "
                        "arrival. Scenario semantics, downstream replay/holdout gates, release protection, and human "
                        "review still apply."
                    ),
                }
            )

    semantic_preflight_status = str(
        field_rows_scenario_semantic_preflight.get("field_rows_scenario_semantic_preflight_status", "")
    )
    if semantic_preflight_status.startswith("scenario_semantic_preflight_failed"):
        for scenario_semantic in field_rows_scenario_semantic_preflight.get("scenario_semantic_status", []) or []:
            if not isinstance(scenario_semantic, dict):
                continue
            if scenario_semantic.get("scenario_semantic_preflight_status") == "scenario_has_semantic_valid_batch":
                continue
            scenario_id = str(scenario_semantic.get("scenario_id", "unknown_scenario"))
            patch_items.append(
                {
                    "patch_id": f"R8P_SCENARIO_SEMANTIC_{_safe_patch_token(scenario_id)}",
                    "priority": "P1",
                    "patch_type": "scenario_semantic_contract",
                    "blocking_condition": str(scenario_semantic.get("scenario_semantic_preflight_status", "unknown")),
                    "target": scenario_id,
                    "scenario_type": scenario_semantic.get("scenario_type"),
                    "operator_action": (
                        "Fix pressure-resolution semantic evidence for this scenario: unresolved conflicts must keep "
                        "operator-review and control-block flags; resolved conflicts must include authoritative source "
                        "and resolution record; guardrail clearance must show no control block or review-required flag."
                    ),
                    "temporal_valid_batches": scenario_semantic.get("temporal_valid_batches", []),
                    "semantic_valid_batches": scenario_semantic.get("semantic_valid_batches", []),
                    "violations_by_batch": scenario_semantic.get("violations_by_batch", {}),
                    "condition_checks_by_batch": scenario_semantic.get("condition_checks_by_batch", {}),
                    "acceptance_check": (
                        "field_rows_scenario_semantic_preflight_status becomes "
                        "scenario_semantic_preflight_passed_ready_for_scenario_acceptance."
                    ),
                    "evidence_boundary": (
                        "Scenario-semantic validity only proves the pressure-resolution meaning is internally coherent. "
                        "Downstream replay/holdout gates, release protection, and human review still apply."
                    ),
                }
            )

    for scenario in field_acceptance.get("scenario_acceptance", []) or []:
        if not isinstance(scenario, dict):
            continue
        if str(scenario.get("acceptance_status")) == "accepted_field_replay_rows":
            continue
        scenario_id = str(scenario.get("scenario_id", "unknown_scenario"))
        plan = _row_plan_by_scenario(row_collection_plan).get(scenario_id, {})
        patch_items.append(
            {
                "patch_id": f"R8P_SCENARIO_ROWS_{_safe_patch_token(scenario_id)}",
                "priority": "P1",
                "patch_type": "scenario_acceptance",
                "blocking_condition": str(scenario.get("acceptance_status", "unknown")),
                "target": scenario_id,
                "scenario_type": scenario.get("scenario_type"),
                "batch_role": plan.get("batch_role", "unknown_batch_role"),
                "operator_action": (
                    "Supply at least one same-batch field row bundle across all required tables, including "
                    "node pressure, pressure/headloss event, operation review, offline lab label, fast proxy event, "
                    "and Agent52 replay row."
                ),
                "candidate_batches_seen": scenario.get("candidate_batches", []),
                "accepted_batches": scenario.get("accepted_batches", []),
                "blocking_reasons": scenario.get("blocking_reasons", []),
                "required_tables": plan.get("required_tables", expected_tables),
                "required_agent52_fields": plan.get("agent52_replay_required_fields", []),
                "acceptance_check": "scenario acceptance_status must become accepted_field_replay_rows.",
                "evidence_boundary": "Scenario acceptance permits R8v routing review; it still cannot write actuator or release gate.",
            }
        )

    if not patch_items:
        status = "field_rows_patch_plan_clear_ready_for_r8v_routing"
        next_action = "R8v_route_pressure_resolution_rows_to_field_replay_and_holdout_gates"
    elif source_status in {"field_rows_file_missing", "field_rows_file_invalid_json", "field_rows_file_invalid_shape"}:
        status = "field_rows_patch_plan_blocked_at_source_preflight"
        next_action = "R8p_fix_field_rows_source_preflight"
    elif any(item["patch_type"] == "source_preflight" for item in patch_items):
        status = "field_rows_patch_plan_blocked_at_table_preflight"
        next_action = "R8p_complete_required_tables_and_shapes"
    elif any(item["patch_type"] == "template_marker_contract" for item in patch_items):
        status = "field_rows_patch_plan_blocked_at_template_marker_contract"
        next_action = "R8p_replace_template_markers_with_field_values"
    elif any(item["patch_type"] == "field_origin_contract" for item in patch_items):
        status = "field_rows_patch_plan_blocked_at_field_origin_contract"
        next_action = "R8p_fix_field_origin_provenance"
    elif any(item["patch_type"] == "schema_row_contract" for item in patch_items):
        status = "field_rows_patch_plan_blocked_at_schema_row_contract"
        next_action = "R8p_fix_schema_required_fields_and_types"
    elif any(item["patch_type"] == "batch_bundle_contract" for item in patch_items):
        status = "field_rows_patch_plan_blocked_at_batch_bundle_contract"
        next_action = "R8p_complete_same_batch_six_table_bundles"
    elif any(item["patch_type"] == "temporal_window_contract" for item in patch_items):
        status = "field_rows_patch_plan_blocked_at_temporal_window_contract"
        next_action = "R8p_fix_same_batch_timestamps_and_hold_time_budget"
    elif any(item["patch_type"] == "scenario_semantic_contract" for item in patch_items):
        status = "field_rows_patch_plan_blocked_at_scenario_semantic_contract"
        next_action = "R8p_fix_pressure_resolution_scenario_semantics"
    else:
        status = "field_rows_patch_plan_blocked_at_scenario_acceptance"
        next_action = "R8p_complete_pressure_resolution_scenario_rows"

    priority_order = {"P0": 0, "P1": 1, "P2": 2}
    patch_type_order = {
        "source_preflight": 0,
        "template_marker_contract": 1,
        "field_origin_contract": 2,
        "schema_row_contract": 3,
        "batch_bundle_contract": 4,
        "temporal_window_contract": 5,
        "scenario_semantic_contract": 6,
        "scenario_acceptance": 7,
    }
    patch_items.sort(
        key=lambda item: (
            priority_order.get(str(item["priority"]), 9),
            patch_type_order.get(str(item["patch_type"]), 9),
            str(item["patch_id"]),
        )
    )
    return {
        "field_rows_patch_plan_status": status,
        "next_operator_action": next_action,
        "patch_item_count": len(patch_items),
        "highest_priority_patch_id": patch_items[0]["patch_id"] if patch_items else None,
        "patch_items": patch_items,
        "template_rows_are_field_evidence": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }


def _field_rows_collection_checklist(
    report,
    field_rows_source: dict[str, object],
    patch_plan: dict[str, object],
    field_rows_package_schema: dict[str, object],
    field_rows_schema_validation: dict[str, object] | None = None,
    field_rows_batch_bundle_preflight: dict[str, object] | None = None,
    field_rows_temporal_window_preflight: dict[str, object] | None = None,
    field_rows_scenario_semantic_preflight: dict[str, object] | None = None,
) -> dict[str, object]:
    """Machine-readable collection contract for real R8p rows.

    This is intentionally not a data generator. It only turns the existing
    scenario plan, schema contract, and patch plan into an executable checklist
    for field collection and validation.
    """

    field_rows_schema_validation = field_rows_schema_validation or {}
    field_rows_batch_bundle_preflight = field_rows_batch_bundle_preflight or {}
    field_rows_temporal_window_preflight = field_rows_temporal_window_preflight or {}
    field_rows_scenario_semantic_preflight = field_rows_scenario_semantic_preflight or {}
    row_collection_plan = report.metrics["row_collection_plan"]
    field_acceptance = report.metrics["field_row_acceptance"]
    scenario_matrix = report.metrics["pressure_resolution_replay_scenario_matrix"]
    row_readiness = report.metrics["row_collection_readiness"]
    expected_tables = [str(table) for table in field_rows_package_schema.get("required", [])]
    schema_validation_status = str(
        field_rows_schema_validation.get("field_rows_schema_validation_status", "schema_validation_not_run")
    )
    patch_status = str(patch_plan.get("field_rows_patch_plan_status", ""))
    if patch_status.startswith("field_rows_patch_plan_clear"):
        checklist_status = "field_rows_collection_checklist_complete_ready_for_r8v_routing"
    elif schema_validation_status == "schema_validation_blocked_at_source_preflight":
        checklist_status = "field_rows_collection_checklist_ready_needs_source_package"
    elif patch_status.endswith("table_preflight"):
        checklist_status = "field_rows_collection_checklist_ready_needs_table_completion"
    elif patch_status.endswith("template_marker_contract"):
        checklist_status = "field_rows_collection_checklist_ready_needs_template_marker_replacement"
    elif patch_status.endswith("field_origin_contract"):
        checklist_status = "field_rows_collection_checklist_ready_needs_field_origin_provenance"
    elif patch_status.endswith("schema_row_contract"):
        checklist_status = "field_rows_collection_checklist_ready_needs_schema_row_contract_fixes"
    elif patch_status.endswith("batch_bundle_contract"):
        checklist_status = "field_rows_collection_checklist_ready_needs_same_batch_bundle_completion"
    elif patch_status.endswith("temporal_window_contract"):
        checklist_status = "field_rows_collection_checklist_ready_needs_temporal_window_fixes"
    elif patch_status.endswith("scenario_semantic_contract"):
        checklist_status = "field_rows_collection_checklist_ready_needs_scenario_semantic_fixes"
    else:
        checklist_status = "field_rows_collection_checklist_ready_needs_scenario_row_completion"

    scenario_acceptance_by_id = {
        str(row.get("scenario_id", "")): row
        for row in field_acceptance.get("scenario_acceptance", [])
        if isinstance(row, dict)
    }
    scenario_by_id = {
        str(row.get("scenario_id", "")): row
        for row in scenario_matrix
        if isinstance(row, dict)
    }
    table_validation_by_name = {
        str(row.get("table", "")): row
        for row in field_rows_schema_validation.get("table_validations", []) or []
        if isinstance(row, dict)
    }

    table_field_checklist = []
    for table in expected_tables:
        required_fields = _required_fields_for_table(table)
        table_field_checklist.append(
            {
                "table": table,
                "table_role": _table_collection_role(table),
                "table_schema_status": table_validation_by_name.get(table, {}).get(
                    "table_schema_status",
                    "schema_validation_not_run",
                ),
                "minimum_real_rows_per_required_scenario": 1,
                "required_fields": [
                    {
                        "field": field,
                        "expected_type": _field_schema(field).get("type"),
                        "evidence_role": _field_collection_role(table, field),
                        "validation_rule": _field_validation_rule(field),
                        "required": True,
                    }
                    for field in required_fields
                ],
            }
        )

    scenario_collection_checklist = []
    for plan in row_collection_plan:
        scenario_id = str(plan["scenario_id"])
        scenario_info = scenario_by_id.get(scenario_id, {})
        acceptance = scenario_acceptance_by_id.get(scenario_id, {})
        scenario_collection_checklist.append(
            {
                "collection_id": plan["collection_id"],
                "scenario_id": scenario_id,
                "scenario_type": plan["scenario_type"],
                "purpose": scenario_info.get("purpose", ""),
                "batch_role": plan["batch_role"],
                "minimum_real_batches": plan["minimum_real_batches"],
                "required_tables": plan["required_tables"],
                "agent52_replay_required_fields": plan["agent52_replay_required_fields"],
                "cross_table_join_keys": plan["cross_table_join_keys"],
                "minimum_resolution_fields": plan["minimum_resolution_fields"],
                "acceptance_metrics": plan["acceptance_metrics"],
                "current_acceptance_status": acceptance.get("acceptance_status", "missing_field_rows"),
                "current_blocking_reasons": acceptance.get("blocking_reasons", ["no_field_replay_rows_supplied"]),
                "candidate_batches_seen": acceptance.get("candidate_batches", []),
                "accepted_batches": acceptance.get("accepted_batches", []),
            }
        )

    operator_acceptance_sequence = [
        {
            "step": "source_package",
            "required_evidence": (
                "Create or point PRESSURE_RESOLUTION_REPLAY_ROWS_PATH to a real JSON table-mapping file "
                "or a metadata.json plus six required CSV directory package."
            ),
            "acceptance_check": (
                "field_rows_source_status is loaded and expected tables map to non-empty row lists, regardless "
                "of JSON or CSV-directory source format."
            ),
        },
        {
            "step": "schema_contract",
            "required_evidence": "All six required tables are present, non-empty, and required fields have coarse valid types.",
            "acceptance_check": "field_rows_schema_validation_status becomes schema_validation_passed_structure_contract.",
        },
        {
            "step": "scenario_bundle",
            "required_evidence": "Each pressure-resolution scenario has a same-batch bundle across sensor, pressure/headloss, operation, lab, proxy, and Agent52 replay rows.",
            "acceptance_check": "field_row_acceptance_status becomes field_replay_rows_accepted_for_all_scenarios.",
        },
        {
            "step": "downstream_routing",
            "required_evidence": "Accepted rows are routed to Agent51 holdout, Agent49 guardrail context, Agent52 replay, and R7 evidence chain.",
            "acceptance_check": "R8v/R7 gates pass before any protective-control or field claim upgrade.",
        },
    ]

    return {
        "checklist_id": "R8u11_pressure_resolution_real_rows_collection_checklist",
        "field_rows_collection_checklist_status": checklist_status,
        "checklist_path": str(ROWS_COLLECTION_CHECKLIST_PATH),
        "model_core_layers": [
            "observability_layer",
            "diagnostic_decision_layer",
            "closed_loop_execution_layer",
            "verification_governance_layer",
        ],
        "core_capabilities": [
            "observability",
            "verifiability",
            "engineering_feasibility",
            "protectability",
        ],
        "source_status": field_rows_source.get("field_rows_source_status", "unknown"),
        "patch_plan_status": patch_status,
        "highest_priority_patch_id": patch_plan.get("highest_priority_patch_id"),
        "schema_validation_status": schema_validation_status,
        "batch_bundle_preflight_status": field_rows_batch_bundle_preflight.get(
            "field_rows_batch_bundle_preflight_status",
            "batch_bundle_preflight_not_run",
        ),
        "complete_batch_bundle_count": field_rows_batch_bundle_preflight.get("complete_bundle_count", 0),
        "partial_batch_bundle_count": field_rows_batch_bundle_preflight.get("partial_bundle_count", 0),
        "missing_bundle_table_count": field_rows_batch_bundle_preflight.get("missing_bundle_table_count", 0),
        "temporal_window_preflight_status": field_rows_temporal_window_preflight.get(
            "field_rows_temporal_window_preflight_status",
            "temporal_window_preflight_not_run",
        ),
        "temporal_valid_batch_count": field_rows_temporal_window_preflight.get("temporal_valid_batch_count", 0),
        "temporal_violation_count": field_rows_temporal_window_preflight.get("temporal_violation_count", 0),
        "hold_time_violation_count": field_rows_temporal_window_preflight.get("hold_time_violation_count", 0),
        "scenario_semantic_preflight_status": field_rows_scenario_semantic_preflight.get(
            "field_rows_scenario_semantic_preflight_status",
            "scenario_semantic_preflight_not_run",
        ),
        "semantic_valid_batch_count": field_rows_scenario_semantic_preflight.get("semantic_valid_batch_count", 0),
        "semantic_violation_count": field_rows_scenario_semantic_preflight.get("semantic_violation_count", 0),
        "required_scenario_count": len(row_collection_plan),
        "missing_scenario_count": row_readiness.get("missing_scenario_count", 0),
        "accepted_scenario_count": field_acceptance.get("accepted_scenario_count", 0),
        "minimum_real_batch_count": row_readiness.get("minimum_real_batch_count", 0),
        "required_table_count": len(expected_tables),
        "required_tables": expected_tables,
        "table_field_checklist": table_field_checklist,
        "scenario_collection_checklist": scenario_collection_checklist,
        "scenario_bundle_status": field_rows_batch_bundle_preflight.get("scenario_bundle_status", []),
        "scenario_temporal_status": field_rows_temporal_window_preflight.get("scenario_temporal_status", []),
        "scenario_semantic_status": field_rows_scenario_semantic_preflight.get("scenario_semantic_status", []),
        "operator_acceptance_sequence": operator_acceptance_sequence,
        "technical_feature_mapping": {
            "technical_problem": (
                "Low-cost sparse sensing cannot directly observe internal pressure-source conflicts, "
                "operator review status, and downstream guardrail clearance in a circular treatment loop."
            ),
            "technical_means": (
                "Use a same-batch six-table field-row bundle plus schema validation, scenario acceptance, "
                "and downstream replay gates to turn pressure conflict resolution into auditable grey-box evidence."
            ),
            "technical_effect": (
                "The system can keep protective blocking when conflicts are unresolved and only route resolved "
                "operator-reviewed batches toward holdout/replay gates without increasing online sensor speed."
            ),
            "prior_art_distinction_candidate": (
                "The checklist couples sparse pressure observations, operator calibration records, replay actions, "
                "and circular hold/recycle timing into one field-validation contract rather than using a single "
                "black-box prediction score."
            ),
            "claim_boundary": "Technical-feature scaffold only; not a legal opinion and not field-supported without real rows.",
        },
        "evidence_boundaries": [
            "This checklist is not field evidence.",
            "Template/TODO rows remain rejected.",
            "Every required table row must include field-origin data_origin.",
            "Schema validity does not prove field origin or scenario linkage.",
            "Scenario acceptance still cannot write actuator or release gate.",
            "Field-supported claims require R8v/R7 downstream gates and human review.",
        ],
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }


def _field_rows_operator_handoff(
    report,
    field_rows_source: dict[str, object],
    patch_plan: dict[str, object],
    field_rows_package_schema: dict[str, object] | None = None,
    field_rows_schema_validation: dict[str, object] | None = None,
    field_rows_collection_checklist: dict[str, object] | None = None,
    field_rows_batch_bundle_preflight: dict[str, object] | None = None,
    field_rows_temporal_window_preflight: dict[str, object] | None = None,
    field_rows_scenario_semantic_preflight: dict[str, object] | None = None,
    field_rows_downstream_routing_preflight: dict[str, object] | None = None,
) -> dict[str, object]:
    patch_status = str(patch_plan.get("field_rows_patch_plan_status", ""))
    patch_item_count = int(patch_plan.get("patch_item_count", 0) or 0)
    if patch_item_count == 0:
        handoff_status = "field_rows_operator_handoff_ready_for_r8v_routing"
    elif patch_status.endswith("source_preflight"):
        handoff_status = "field_rows_operator_handoff_ready_needs_source_package"
    elif patch_status.endswith("table_preflight"):
        handoff_status = "field_rows_operator_handoff_ready_needs_table_completion"
    elif patch_status.endswith("batch_bundle_contract"):
        handoff_status = "field_rows_operator_handoff_ready_needs_same_batch_bundle_completion"
    elif patch_status.endswith("temporal_window_contract"):
        handoff_status = "field_rows_operator_handoff_ready_needs_temporal_window_fixes"
    elif patch_status.endswith("scenario_semantic_contract"):
        handoff_status = "field_rows_operator_handoff_ready_needs_scenario_semantic_fixes"
    else:
        handoff_status = "field_rows_operator_handoff_ready_needs_scenario_rows"

    default_validation_command = ".venv/bin/python experiments/run_agent61_pressure_resolution_replay_scenario_pack.py"
    env_override_name = "PRESSURE_RESOLUTION_REPLAY_ROWS_PATH"
    configured_path = str(field_rows_source.get("field_rows_source_path", DEFAULT_FIELD_ROWS_PATH))
    expected_tables = [str(table) for table in field_rows_source.get("expected_tables", [])]
    if not expected_tables:
        expected_tables = sorted({*REQUIRED_TABLE_FIELDS, "agent52_replay_table"})
    field_origin_required_tables = [
        table
        for table in expected_tables
        if "data_origin" in _required_fields_for_table(table)
    ]
    all_tables_require_data_origin = len(field_origin_required_tables) == len(expected_tables)
    schema_status = "field_rows_package_schema_ready"
    if field_rows_package_schema and sorted(field_rows_package_schema.get("required", [])) != expected_tables:
        schema_status = "field_rows_package_schema_table_mismatch"
    field_rows_schema_validation = field_rows_schema_validation or {}
    field_rows_collection_checklist = field_rows_collection_checklist or {}
    field_rows_batch_bundle_preflight = field_rows_batch_bundle_preflight or {}
    field_rows_temporal_window_preflight = field_rows_temporal_window_preflight or {}
    field_rows_scenario_semantic_preflight = field_rows_scenario_semantic_preflight or {}
    field_rows_downstream_routing_preflight = field_rows_downstream_routing_preflight or {}

    return {
        "field_rows_operator_handoff_status": handoff_status,
        "field_rows_package_schema_status": schema_status,
        "field_rows_schema_validation_status": field_rows_schema_validation.get(
            "field_rows_schema_validation_status",
            "schema_validation_not_run",
        ),
        "working_directory": str(PROJECT_ROOT),
        "default_field_rows_path": str(DEFAULT_FIELD_ROWS_PATH),
        "configured_field_rows_path": configured_path,
        "template_rows_path": str(TEMPLATE_ROWS_PATH),
        "csv_template_dir": str(ROWS_CSV_TEMPLATE_DIR),
        "r7_to_r8p_alignment_path": str(ROWS_R7_ALIGNMENT_PATH),
        "rows_schema_path": str(ROWS_SCHEMA_PATH),
        "collection_checklist_path": str(ROWS_COLLECTION_CHECKLIST_PATH),
        "field_rows_collection_checklist_status": field_rows_collection_checklist.get(
            "field_rows_collection_checklist_status",
            "collection_checklist_not_generated",
        ),
        "field_rows_batch_bundle_preflight_status": field_rows_batch_bundle_preflight.get(
            "field_rows_batch_bundle_preflight_status",
            "batch_bundle_preflight_not_run",
        ),
        "field_rows_batch_bundle_preflight_path": str(ROWS_BATCH_BUNDLE_PREFLIGHT_PATH),
        "field_rows_temporal_window_preflight_status": field_rows_temporal_window_preflight.get(
            "field_rows_temporal_window_preflight_status",
            "temporal_window_preflight_not_run",
        ),
        "field_rows_temporal_window_preflight_path": str(ROWS_TEMPORAL_WINDOW_PREFLIGHT_PATH),
        "field_rows_scenario_semantic_preflight_status": field_rows_scenario_semantic_preflight.get(
            "field_rows_scenario_semantic_preflight_status",
            "scenario_semantic_preflight_not_run",
        ),
        "field_rows_scenario_semantic_preflight_path": str(ROWS_SCENARIO_SEMANTIC_PREFLIGHT_PATH),
        "field_rows_downstream_routing_preflight_status": field_rows_downstream_routing_preflight.get(
            "field_rows_downstream_routing_preflight_status",
            "downstream_routing_preflight_not_run",
        ),
        "field_rows_downstream_routing_preflight_path": str(ROWS_DOWNSTREAM_ROUTING_PREFLIGHT_PATH),
        "field_rows_collection_checklist_item_count": len(
            field_rows_collection_checklist.get("scenario_collection_checklist", []) or []
        )
        + len(field_rows_collection_checklist.get("table_field_checklist", []) or []),
        "env_override_name": env_override_name,
        "validation_command_default": default_validation_command,
        "validation_command_with_env_override": (
            f"{env_override_name}=/absolute/path/to/pressure_resolution_replay_rows.json "
            f"{default_validation_command}"
        ),
        "next_operator_action": patch_plan.get("next_operator_action"),
        "highest_priority_patch_id": patch_plan.get("highest_priority_patch_id"),
        "required_root_shape": (
            "JSON object mapping expected table names to row lists, or metadata.json plus required CSV directory."
        ),
        "required_tables": expected_tables,
        "required_table_fields": {
            table: _required_fields_for_table(table)
            for table in expected_tables
        },
        "field_rows_all_tables_require_data_origin": all_tables_require_data_origin,
        "field_rows_provenance_gate_status": (
            "all_required_tables_require_field_origin"
            if all_tables_require_data_origin
            else "field_origin_contract_incomplete"
        ),
        "field_rows_provenance_required_table_count": len(field_origin_required_tables),
        "schema_boundary": (
            "The schema validates root/table/required-field shape only. R8p acceptance still rejects TODO, "
            "template rows, weak scenario linkage, and non-field provenance in any required table."
        ),
        "schema_validation_summary": {
            "required_field_gap_count": field_rows_schema_validation.get("required_field_gap_count", 0),
            "invalid_type_count": field_rows_schema_validation.get("invalid_type_count", 0),
            "template_marker_gap_count": field_rows_schema_validation.get("template_marker_gap_count", 0),
            "field_origin_gap_count": field_rows_schema_validation.get("field_origin_gap_count", 0),
            "missing_table_count": field_rows_schema_validation.get("missing_table_count", 0),
            "empty_table_count": field_rows_schema_validation.get("empty_table_count", 0),
            "unknown_table_count": field_rows_schema_validation.get("unknown_table_count", 0),
        },
        "batch_bundle_preflight_summary": {
            "candidate_batch_count": field_rows_batch_bundle_preflight.get("candidate_batch_count", 0),
            "complete_bundle_count": field_rows_batch_bundle_preflight.get("complete_bundle_count", 0),
            "partial_bundle_count": field_rows_batch_bundle_preflight.get("partial_bundle_count", 0),
            "missing_bundle_table_count": field_rows_batch_bundle_preflight.get("missing_bundle_table_count", 0),
            "scenario_bundle_ready_count": field_rows_batch_bundle_preflight.get("scenario_bundle_ready_count", 0),
        },
        "temporal_window_preflight_summary": {
            "checked_batch_count": field_rows_temporal_window_preflight.get("checked_batch_count", 0),
            "temporal_valid_batch_count": field_rows_temporal_window_preflight.get("temporal_valid_batch_count", 0),
            "temporal_violation_count": field_rows_temporal_window_preflight.get("temporal_violation_count", 0),
            "hold_time_violation_count": field_rows_temporal_window_preflight.get("hold_time_violation_count", 0),
            "scenario_temporal_ready_count": field_rows_temporal_window_preflight.get(
                "scenario_temporal_ready_count",
                0,
            ),
        },
        "scenario_semantic_preflight_summary": {
            "checked_batch_count": field_rows_scenario_semantic_preflight.get("checked_batch_count", 0),
            "semantic_valid_batch_count": field_rows_scenario_semantic_preflight.get("semantic_valid_batch_count", 0),
            "semantic_violation_count": field_rows_scenario_semantic_preflight.get("semantic_violation_count", 0),
            "condition_violation_counts": field_rows_scenario_semantic_preflight.get("condition_violation_counts", {}),
            "scenario_semantic_ready_count": field_rows_scenario_semantic_preflight.get(
                "scenario_semantic_ready_count",
                0,
            ),
        },
        "downstream_routing_preflight_summary": {
            "accepted_scenario_count": field_rows_downstream_routing_preflight.get("accepted_scenario_count", 0),
            "accepted_batch_count": field_rows_downstream_routing_preflight.get("accepted_batch_count", 0),
            "routing_target_count": field_rows_downstream_routing_preflight.get("routing_target_count", 0),
            "routing_ready_target_count": field_rows_downstream_routing_preflight.get("routing_ready_target_count", 0),
            "can_route_to_r8v": field_rows_downstream_routing_preflight.get("can_route_to_r8v", False),
        },
        "template_rejection_rules": [
            "Do not submit pressure_resolution_replay_rows_template.json as the real field rows package.",
            "Do not submit pressure_resolution_replay_rows_csv_template/ unchanged as the real field rows package.",
            "Replace every TODO/template placeholder with field-origin values before validation.",
            "Rows with template_only=True are rejected as field evidence.",
            "Rows with evidence_status=template_not_field_evidence are rejected as field evidence.",
            "Every required table row must include field-origin `data_origin`; synthetic/template/TODO provenance is rejected.",
            "Rows must preserve same-batch linkage across sensor, pressure/headloss, operation, lab, proxy, and Agent52 replay tables.",
            "Rows must preserve timestamp order and enough hold/recycle time for slow evidence and review to arrive before release.",
            "Rows must preserve scenario semantics: unresolved conflicts stay reviewed/blocked, resolved conflicts carry authoritative source and resolution record, and guardrail clearance has no review/control block.",
        ],
        "acceptance_milestones": [
            {
                "milestone": "source_preflight",
                "acceptance": (
                    "field_rows_source_status becomes a loaded JSON-file or CSV-directory status, including "
                    "schema-gap/shape-warning variants for targeted repair."
                ),
            },
            {
                "milestone": "table_preflight",
                "acceptance": "missing_tables, empty_tables, invalid_table_shapes, and unknown_tables are cleared.",
            },
            {
                "milestone": "scenario_acceptance",
                "acceptance": "Every pressure-resolution scenario acceptance_status becomes accepted_field_replay_rows.",
            },
            {
                "milestone": "r8v_routing",
                "acceptance": (
                    "R8p rows route to Agent51 holdout, Agent49 guardrail context, "
                    "Agent52 replay clearance, and R7 evidence chain for human review."
                ),
            },
        ],
        "field_evidence_boundary": (
            "This handoff is an operator data-ingestion contract, not field evidence. "
            "The template is only a scaffold; real rows still require R8p acceptance, R8v routing, "
            "Agent51/49/52/R7 gates, and human review before any field-supported claim."
        ),
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }


def _field_rows_submission_readiness_review(
    report,
    field_rows_source: dict[str, object],
    field_rows_schema_validation: dict[str, object],
    field_rows_batch_bundle_preflight: dict[str, object],
    field_rows_temporal_window_preflight: dict[str, object],
    field_rows_scenario_semantic_preflight: dict[str, object],
    field_rows_downstream_routing_preflight: dict[str, object],
    field_rows_patch_plan: dict[str, object],
    field_rows_collection_checklist: dict[str, object],
    field_rows_operator_handoff: dict[str, object],
    field_rows_r7_completion_plan: dict[str, object],
    field_rows_r7_completion_route_work_package_patch_plan: dict[str, object],
    field_rows_r7_completion_route_work_package_assembly_gate: dict[str, object],
) -> dict[str, object]:
    """Aggregate R8p/R7 submission gates into one operator-facing review.

    This is deliberately a synthesizer, not a new model. It makes the next
    evidence-producing action explicit while preserving every downstream gate.
    """

    readiness = report.metrics["readiness"]
    field_acceptance = report.metrics["field_row_acceptance"]
    row_readiness = report.metrics["row_collection_readiness"]
    direct_patch_count = int(field_rows_patch_plan.get("patch_item_count", 0) or 0)
    r7_patch_count = int(
        field_rows_r7_completion_route_work_package_patch_plan.get("patch_item_count", 0) or 0
    )
    downstream_status = str(
        field_rows_downstream_routing_preflight.get(
            "field_rows_downstream_routing_preflight_status",
            "",
        )
    )
    source_status = str(field_rows_source.get("field_rows_source_status", ""))
    schema_status = str(
        field_rows_schema_validation.get("field_rows_schema_validation_status", "")
    )
    bundle_status = str(
        field_rows_batch_bundle_preflight.get("field_rows_batch_bundle_preflight_status", "")
    )
    temporal_status = str(
        field_rows_temporal_window_preflight.get("field_rows_temporal_window_preflight_status", "")
    )
    semantic_status = str(
        field_rows_scenario_semantic_preflight.get("field_rows_scenario_semantic_preflight_status", "")
    )
    r7_assembly_status = str(
        field_rows_r7_completion_route_work_package_assembly_gate.get(
            "route_work_package_assembly_gate_status",
            "",
        )
    )

    if downstream_status == "downstream_routing_preflight_passed_ready_for_r8v_field_replay_and_holdout_gates":
        review_status = "submission_readiness_review_ready_for_r8v_field_replay_and_holdout_gates"
        next_action = "R8v_route_pressure_resolution_rows_to_field_replay_and_holdout_gates"
    elif source_status in {
        "field_rows_file_missing",
        "field_rows_file_invalid_json",
        "field_rows_file_invalid_shape",
    }:
        review_status = "submission_readiness_review_blocked_at_source_package"
        next_action = "R8p_fix_field_rows_source_preflight"
    elif "failed" in schema_status:
        review_status = "submission_readiness_review_blocked_at_schema_or_provenance_contract"
        next_action = str(field_rows_patch_plan.get("next_operator_action", "R8p_fix_schema_contract"))
    elif "failed" in bundle_status:
        review_status = "submission_readiness_review_blocked_at_same_batch_bundle_contract"
        next_action = "R8p_complete_same_batch_six_table_bundles"
    elif "failed" in temporal_status:
        review_status = "submission_readiness_review_blocked_at_temporal_window_contract"
        next_action = "R8p_fix_same_batch_timestamps_and_hold_time_budget"
    elif "failed" in semantic_status:
        review_status = "submission_readiness_review_blocked_at_scenario_semantic_contract"
        next_action = "R8p_fix_pressure_resolution_scenario_semantics"
    elif r7_assembly_status.startswith("route_work_package_assembly_gate_blocked"):
        review_status = "submission_readiness_review_waiting_for_r7_to_r8p_work_package_submission"
        next_action = str(
            field_rows_r7_completion_route_work_package_patch_plan.get(
                "highest_priority_patch_id",
                "R8U27_SET_R7_TO_R8P_WORK_PACKAGE_DIR",
            )
        )
    elif direct_patch_count:
        review_status = "submission_readiness_review_blocked_at_scenario_acceptance"
        next_action = str(field_rows_patch_plan.get("next_operator_action", "R8p_complete_pressure_resolution_scenario_rows"))
    else:
        review_status = "submission_readiness_review_needs_manual_gate_review"
        next_action = "review_r8p_r7_gate_status_before_routing"

    gate_sequence = [
        _submission_gate(
            "source_package",
            source_status,
            field_rows_source.get("preflight_blockers", []),
            "load JSON table mapping or metadata.json plus required CSV directory",
        ),
        _submission_gate(
            "schema_provenance_template",
            schema_status,
            [
                f"required_field_gap_count={field_rows_schema_validation.get('required_field_gap_count', 0)}",
                f"invalid_type_count={field_rows_schema_validation.get('invalid_type_count', 0)}",
                f"template_marker_gap_count={field_rows_schema_validation.get('template_marker_gap_count', 0)}",
                f"field_origin_gap_count={field_rows_schema_validation.get('field_origin_gap_count', 0)}",
            ],
            "clear required fields, coarse types, TODO/template markers, and row-level field origin",
        ),
        _submission_gate(
            "same_batch_bundle",
            bundle_status,
            [
                f"complete_bundle_count={field_rows_batch_bundle_preflight.get('complete_bundle_count', 0)}",
                f"partial_bundle_count={field_rows_batch_bundle_preflight.get('partial_bundle_count', 0)}",
                f"missing_bundle_table_count={field_rows_batch_bundle_preflight.get('missing_bundle_table_count', 0)}",
            ],
            "one shared batch_id must connect sensor, pressure/headloss, operation, lab, proxy, and Agent52 replay rows",
        ),
        _submission_gate(
            "temporal_window",
            temporal_status,
            [
                f"temporal_valid_batch_count={field_rows_temporal_window_preflight.get('temporal_valid_batch_count', 0)}",
                f"temporal_violation_count={field_rows_temporal_window_preflight.get('temporal_violation_count', 0)}",
                f"hold_time_violation_count={field_rows_temporal_window_preflight.get('hold_time_violation_count', 0)}",
            ],
            "slow labels and operator review must arrive inside hold/recycle time before release",
        ),
        _submission_gate(
            "scenario_semantics",
            semantic_status,
            [
                f"semantic_valid_batch_count={field_rows_scenario_semantic_preflight.get('semantic_valid_batch_count', 0)}",
                f"semantic_violation_count={field_rows_scenario_semantic_preflight.get('semantic_violation_count', 0)}",
            ],
            "unresolved conflicts stay blocked; resolved conflicts carry authoritative source and resolution record",
        ),
        _submission_gate(
            "downstream_routing",
            downstream_status,
            [
                f"routing_ready_target_count={field_rows_downstream_routing_preflight.get('routing_ready_target_count', 0)}",
                f"routing_target_count={field_rows_downstream_routing_preflight.get('routing_target_count', 0)}",
                f"can_route_to_r8v={field_rows_downstream_routing_preflight.get('can_route_to_r8v', False)}",
            ],
            "route accepted rows to Agent51 holdout, Agent49 guardrail context, Agent52 replay, and R7 evidence chain",
        ),
        _submission_gate(
            "r7_to_r8p_work_package_assembly",
            r7_assembly_status,
            [
                f"patch_plan_status={field_rows_r7_completion_route_work_package_patch_plan.get('route_work_package_patch_plan_status', '')}",
                f"patch_item_count={r7_patch_count}",
                f"blocked_assembly_step_count={field_rows_r7_completion_route_work_package_assembly_gate.get('blocked_assembly_step_count', 0)}",
            ],
            "optional route for assembling R8p rows from R7 source package, operator supplement, and Agent52 export",
        ),
    ]
    direct_top_patch = (
        field_rows_patch_plan.get("patch_items", [{}])[0]
        if field_rows_patch_plan.get("patch_items")
        else {}
    )
    route_top_patch = (
        field_rows_r7_completion_route_work_package_patch_plan.get("patch_items", [{}])[0]
        if field_rows_r7_completion_route_work_package_patch_plan.get("patch_items")
        else {}
    )
    return {
        "submission_readiness_review_id": "R8u47_pressure_resolution_submission_readiness_review",
        "submission_readiness_review_status": review_status,
        "review_path": str(ROWS_SUBMISSION_READINESS_REVIEW_PATH),
        "model_core_layers": [
            "observability_layer",
            "closed_loop_execution_layer",
            "verification_governance_layer",
        ],
        "core_capabilities": [
            "observability",
            "controllability",
            "verifiability",
            "engineering_feasibility",
            "protectability",
        ],
        "next_operator_action": next_action,
        "direct_r8p_patch_plan_status": field_rows_patch_plan.get("field_rows_patch_plan_status", ""),
        "direct_r8p_highest_priority_patch_id": field_rows_patch_plan.get("highest_priority_patch_id"),
        "direct_r8p_highest_priority_operator_action": direct_top_patch.get("operator_action", ""),
        "r7_to_r8p_completion_plan_status": field_rows_r7_completion_plan.get("completion_plan_status", ""),
        "r7_to_r8p_route_patch_plan_status": field_rows_r7_completion_route_work_package_patch_plan.get(
            "route_work_package_patch_plan_status",
            "",
        ),
        "r7_to_r8p_highest_priority_patch_id": field_rows_r7_completion_route_work_package_patch_plan.get(
            "highest_priority_patch_id"
        ),
        "r7_to_r8p_highest_priority_operator_action": route_top_patch.get("operator_action", ""),
        "operator_handoff_status": field_rows_operator_handoff.get("field_rows_operator_handoff_status", ""),
        "collection_checklist_status": field_rows_collection_checklist.get(
            "field_rows_collection_checklist_status",
            "",
        ),
        "scenario_pack_status": readiness.get("scenario_pack_status", ""),
        "field_row_acceptance_status": field_acceptance.get("field_row_acceptance_status", ""),
        "row_collection_plan_status": row_readiness.get("row_collection_plan_status", ""),
        "missing_scenario_count": row_readiness.get("missing_scenario_count", 0),
        "accepted_scenario_count": field_acceptance.get("accepted_scenario_count", 0),
        "accepted_batch_count": field_acceptance.get("accepted_batch_count", 0),
        "gate_sequence": gate_sequence,
        "operator_decision_policy": [
            "If a real R8p rows package exists, fix direct_r8p_highest_priority_patch_id first.",
            "If no real R8p package exists but an R7 field package can be produced, use the R7-to-R8p route work package templates.",
            "Do not generate Agent52 replay rows from R7 field CSV values; export them from Agent49/52 replay.",
            "Do not treat route work package templates or CSV headers as field evidence.",
            "Route to R8v only after downstream_routing_preflight passes.",
        ],
        "technical_feature_mapping": {
            "technical_problem": (
                "Field operators face many validation gates when converting low-cost sparse pressure observations, "
                "operator review, and offline replay into usable grey-box control evidence."
            ),
            "technical_means": (
                "A submission readiness review aggregates source, schema, provenance, bundle, temporal, semantic, "
                "downstream routing, and optional R7-to-R8p assembly gates into one ordered operator action."
            ),
            "technical_effect": (
                "The field package can be completed with fewer repair loops while keeping unresolved conflicts blocked "
                "and preserving delayed evidence, hold/recycle windows, and replay/holdout gates."
            ),
            "prior_art_distinction_candidate": (
                "Unlike a single importer or black-box prediction score, the review exposes where sparse sensing, "
                "human pressure-source resolution, and offline replay each enter the closed-loop control evidence chain."
            ),
        },
        "evidence_boundaries": [
            "This review is an aggregation of gate outputs, not field evidence.",
            "A ready review can route data to R8v, but cannot write actuator or release gate.",
            "Template, TODO, sample, and synthetic rows remain rejected before field acceptance.",
            "Agent52 replay rows must come from replay export, not be inferred from field CSVs.",
            "Field-supported claims still require R8v/R7 evidence chain, holdout gates, and human review.",
        ],
        "can_route_to_r8v": downstream_status
        == "downstream_routing_preflight_passed_ready_for_r8v_field_replay_and_holdout_gates",
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "field_claim_upgrade_allowed": False,
    }


def _field_rows_source_package_submission_route_guide(
    report,
    field_rows_source: dict[str, object],
    field_rows_package_schema: dict[str, object],
    field_rows_patch_plan: dict[str, object],
    field_rows_operator_handoff: dict[str, object],
    field_rows_submission_readiness_review: dict[str, object],
    field_rows_r7_completion_plan: dict[str, object],
    field_rows_r7_completion_route_contracts: dict[str, object],
    field_rows_r7_completion_route_work_packages: dict[str, object],
    field_rows_r7_completion_route_work_package_patch_plan: dict[str, object],
) -> dict[str, object]:
    """Make the source-package submission route explicit for field operators.

    This does not validate new evidence. It chooses the next source-package
    submission path and points to existing templates, schemas, and validation
    commands without relaxing any downstream gate.
    """

    source_status = str(field_rows_source.get("field_rows_source_status", ""))
    readiness_status = str(
        field_rows_submission_readiness_review.get(
            "submission_readiness_review_status",
            "",
        )
    )
    can_route_to_r8v = bool(field_rows_submission_readiness_review.get("can_route_to_r8v", False))
    if can_route_to_r8v:
        guide_status = "source_package_submission_route_guide_ready_for_r8v_no_source_repair_needed"
        recommended_route_id = "route_to_r8v_field_replay_and_holdout_gates"
        next_operator_action = "R8v_route_pressure_resolution_rows_to_field_replay_and_holdout_gates"
    elif source_status in {
        "field_rows_file_missing",
        "field_rows_file_invalid_json",
        "field_rows_file_invalid_shape",
    }:
        guide_status = "source_package_submission_route_guide_ready_for_source_package_submission"
        recommended_route_id = "direct_r8p_json_or_csv_source_package"
        next_operator_action = "R8p_submit_direct_json_or_csv_source_package"
    else:
        guide_status = "source_package_submission_route_guide_ready_for_loaded_package_repairs"
        recommended_route_id = "repair_loaded_r8p_source_package"
        next_operator_action = str(
            field_rows_submission_readiness_review.get(
                "next_operator_action",
                field_rows_patch_plan.get("next_operator_action", "R8p_repair_loaded_source_package"),
            )
        )

    expected_tables = list(field_rows_package_schema.get("x_required_tables", []))
    required_fields_by_table = {
        table: _required_fields_for_table(table)
        for table in expected_tables
    }
    direct_patch_items = field_rows_patch_plan.get("patch_items", [])
    direct_top_patch = direct_patch_items[0] if direct_patch_items else {}
    r7_patch_items = field_rows_r7_completion_route_work_package_patch_plan.get("patch_items", [])
    r7_top_patch = r7_patch_items[0] if r7_patch_items else {}
    validation_command = str(
        field_rows_operator_handoff.get(
            "validation_command_default",
            ".venv/bin/python experiments/run_agent61_pressure_resolution_replay_scenario_pack.py",
        )
    )
    env_override_name = str(field_rows_operator_handoff.get("env_override_name", "PRESSURE_RESOLUTION_REPLAY_ROWS_PATH"))
    default_field_rows_path = str(field_rows_operator_handoff.get("default_field_rows_path", DEFAULT_FIELD_ROWS_PATH))

    route_options = [
        {
            "route_id": "direct_r8p_json_table_mapping",
            "route_kind": "direct_r8p_source_package",
            "when_to_use": (
                "Use when field rows can be exported directly as a JSON table mapping with all required tables."
            ),
            "submission_target": default_field_rows_path,
            "env_override": f"{env_override_name}=/absolute/path/to/pressure_resolution_replay_rows.json",
            "required_inputs": [
                "one JSON object whose keys are required table names",
                "six required field-origin tables plus agent52_replay_table",
                "non-template reviewer, calibration, operation, lab, pressure/headloss, and replay fields",
            ],
            "required_tables": expected_tables,
            "required_fields_by_table": required_fields_by_table,
            "validation_command": validation_command,
            "source_format_after_load": "json_table_mapping",
            "highest_priority_patch_id": field_rows_patch_plan.get("highest_priority_patch_id"),
            "operator_action": direct_top_patch.get("operator_action", ""),
            "failure_boundary": (
                "A JSON package that loads still must pass schema, provenance, template-marker, bundle, temporal, "
                "semantic, downstream routing, and R8p acceptance gates."
            ),
        },
        {
            "route_id": "direct_r8p_csv_directory",
            "route_kind": "direct_r8p_source_package",
            "when_to_use": (
                "Use when field rows are easier to collect as metadata.json plus one CSV per required table."
            ),
            "submission_target": str(ROWS_CSV_TEMPLATE_DIR),
            "env_override": f"{env_override_name}=/absolute/path/to/pressure_resolution_replay_rows_csv_directory",
            "required_inputs": [
                "metadata.json",
                "one CSV file per required table",
                "all TODO/template placeholders replaced by field values",
                "field-origin data_origin values in every required table row",
            ],
            "required_files": [
                "metadata.json",
                *[f"{table}.csv" for table in expected_tables],
            ],
            "validation_command": validation_command,
            "source_format_after_load": "csv_directory_with_optional_metadata_json",
            "highest_priority_patch_id": field_rows_patch_plan.get("highest_priority_patch_id"),
            "operator_action": direct_top_patch.get("operator_action", ""),
            "failure_boundary": (
                "The CSV directory template is a scaffold only; header-only or TODO/template rows are rejected before "
                "field acceptance."
            ),
        },
        {
            "route_id": "r7_to_r8p_route_work_package_submission",
            "route_kind": "assembled_from_r7_field_package_operator_supplement_and_agent52_export",
            "when_to_use": (
                "Use when an R7 field package already exists and R8p rows should be assembled from R7 shared tables, "
                "operator supplement records, and Agent52 replay export."
            ),
            "submission_target": str(ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_TEMPLATE_DIR),
            "env_override": "R7_TO_R8P_WORK_PACKAGE_DIR=/absolute/path/to/r7_to_r8p_work_package_submission",
            "required_inputs": [
                "R7 source package work package",
                "operator supplement work package",
                "Agent52 replay export work package",
                "R8p validation gates work package",
            ],
            "route_contracts_status": field_rows_r7_completion_route_contracts.get(
                "completion_route_contracts_status",
                "",
            ),
            "work_packages_status": field_rows_r7_completion_route_work_packages.get(
                "route_work_packages_status",
                "",
            ),
            "completion_plan_status": field_rows_r7_completion_plan.get("completion_plan_status", ""),
            "highest_priority_patch_id": field_rows_r7_completion_route_work_package_patch_plan.get(
                "highest_priority_patch_id"
            ),
            "operator_action": r7_top_patch.get("operator_action", ""),
            "validation_command": validation_command,
            "failure_boundary": (
                "R7 shared field CSV values cannot invent Agent52 replay rows; replay rows must come from the "
                "Agent49/52 replay export route and then pass R8p/R8v gates."
            ),
        },
    ]
    action_queue = [
        {
            "order": 1,
            "action_id": next_operator_action,
            "route_id": recommended_route_id,
            "why_first": (
                "Current submission readiness is blocked before R8v routing."
                if not can_route_to_r8v
                else "All R8p downstream routing gates are ready."
            ),
        },
        {
            "order": 2,
            "action_id": field_rows_submission_readiness_review.get(
                "next_operator_action",
                field_rows_patch_plan.get("next_operator_action", ""),
            ),
            "route_id": "submission_readiness_review_next_action",
            "why_first": "Keeps source-package repair aligned with the aggregated R8p/R7 gate sequence.",
        },
        {
            "order": 3,
            "action_id": field_rows_r7_completion_route_work_package_patch_plan.get(
                "highest_priority_patch_id",
                "",
            ),
            "route_id": "r7_to_r8p_route_work_package_submission",
            "why_first": "Use only if the direct R8p source package cannot be produced from field exports.",
        },
    ]
    return {
        "source_package_submission_route_guide_id": "R8u48_source_package_submission_route_guide",
        "source_package_submission_route_guide_status": guide_status,
        "guide_path": str(ROWS_SOURCE_PACKAGE_SUBMISSION_ROUTE_GUIDE_PATH),
        "model_core_layers": [
            "observability_layer",
            "closed_loop_execution_layer",
            "verification_governance_layer",
        ],
        "core_capabilities": [
            "observability",
            "verifiability",
            "engineering_feasibility",
            "protectability",
        ],
        "current_source_status": source_status,
        "submission_readiness_review_status": readiness_status,
        "recommended_route_id": recommended_route_id,
        "alternate_route_ids": [
            option["route_id"]
            for option in route_options
            if option["route_id"] != recommended_route_id
        ],
        "next_operator_action": next_operator_action,
        "route_option_count": len(route_options),
        "route_options": route_options,
        "operator_action_queue": action_queue,
        "accepted_source_formats": field_rows_source.get("accepted_source_formats", []),
        "default_field_rows_path": default_field_rows_path,
        "env_override_name": env_override_name,
        "validation_command_default": validation_command,
        "validation_command_with_env_override": str(
            field_rows_operator_handoff.get(
                "validation_command_with_env_override",
                f"{env_override_name}=<path> {validation_command}",
            )
        ),
        "source_package_contract": {
            "expected_tables": expected_tables,
            "required_fields_by_table": required_fields_by_table,
            "schema_path": str(ROWS_SCHEMA_PATH),
            "collection_checklist_path": str(ROWS_COLLECTION_CHECKLIST_PATH),
            "submission_readiness_review_path": str(ROWS_SUBMISSION_READINESS_REVIEW_PATH),
        },
        "technical_feature_mapping": {
            "technical_problem": (
                "The pressure-resolution evidence chain allows multiple source-package entry routes, "
                "but field operators need a single route decision before replay/holdout gates can run."
            ),
            "technical_means": (
                "A source-package route guide compares direct JSON, direct CSV-directory, and R7-to-R8p work-package "
                "submission routes using the same schema, provenance, and downstream gate contracts."
            ),
            "technical_effect": (
                "Source-package repair loops are reduced while preventing template rows, generated replay surrogates, "
                "or incomplete R7 packages from bypassing the grey-box replay evidence chain."
            ),
        },
        "evidence_boundaries": [
            "This route guide is not field evidence.",
            "It does not validate row contents beyond the existing R8p gates.",
            "It cannot generate Agent52 replay rows from R7 source values.",
            "It cannot write actuator, protective control, release gate, or field-supported claim.",
        ],
        "can_route_to_r8v": can_route_to_r8v,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "field_claim_upgrade_allowed": False,
    }


def _field_rows_source_package_route_preflight(
    field_rows_source: dict[str, object],
    field_rows_source_package_submission_route_guide: dict[str, object],
    field_rows_r7_completion_route_work_package_preflight: dict[str, object],
    field_rows_r7_completion_route_work_package_assembly_gate: dict[str, object],
) -> dict[str, object]:
    """Check whether each source-package submission route is currently actionable.

    The route guide explains what an operator can submit. This preflight turns
    that guide into a machine-readable gate without reclassifying templates,
    synthetic rows, or work-package scaffolds as field evidence.
    """

    source_status = str(field_rows_source.get("field_rows_source_status", ""))
    source_format = str(field_rows_source.get("field_rows_source_format", "unknown"))
    source_path = Path(str(field_rows_source.get("field_rows_source_path", ""))).expanduser()
    source_exists = source_path.exists()
    source_is_dir = source_path.is_dir() if source_exists else False
    source_blockers = [str(item) for item in field_rows_source.get("preflight_blockers", []) or []]
    validation_command = str(
        field_rows_source_package_submission_route_guide.get(
            "validation_command_default",
            ".venv/bin/python experiments/run_agent61_pressure_resolution_replay_scenario_pack.py",
        )
    )
    env_override_name = str(
        field_rows_source_package_submission_route_guide.get(
            "env_override_name",
            "PRESSURE_RESOLUTION_REPLAY_ROWS_PATH",
        )
    )
    can_route_to_r8v = bool(
        field_rows_source_package_submission_route_guide.get("can_route_to_r8v", False)
    )
    json_loaded_statuses = {
        "field_rows_file_loaded",
        "field_rows_file_loaded_with_schema_gaps",
        "field_rows_file_loaded_with_shape_warnings",
    }
    csv_loaded_statuses = {
        "field_rows_directory_loaded",
        "field_rows_directory_loaded_with_schema_gaps",
        "field_rows_directory_loaded_with_shape_warnings",
    }

    def _direct_route_result(route_id: str, expected_format: str) -> dict[str, object]:
        route_is_json = expected_format == "json_table_mapping"
        loaded_statuses = json_loaded_statuses if route_is_json else csv_loaded_statuses
        invalid_statuses = (
            {"field_rows_file_invalid_json", "field_rows_file_invalid_shape"}
            if route_is_json
            else set()
        )
        route_matches_current_source = source_format == expected_format
        if can_route_to_r8v and route_matches_current_source:
            status = "route_preflight_ready_for_r8v_routing"
            next_action = "R8v_route_pressure_resolution_rows_to_field_replay_and_holdout_gates"
            blockers: list[str] = []
        elif route_matches_current_source and source_status in loaded_statuses:
            status = "route_preflight_ready_for_loaded_source_package_gate_repairs"
            next_action = "R8p_run_validation_and_repair_loaded_source_package"
            blockers = source_blockers
        elif route_matches_current_source and source_status in invalid_statuses:
            status = "route_preflight_blocked_by_invalid_source_package"
            next_action = f"R8p_repair_{route_id}_source_package"
            blockers = source_blockers or [source_status]
        elif source_status == "field_rows_file_missing":
            status = "route_preflight_waiting_for_source_package_submission"
            next_action = f"R8p_submit_{route_id}"
            blockers = ["source_package_not_submitted"]
        else:
            status = "route_preflight_waiting_for_matching_source_package_route"
            next_action = f"R8p_submit_{route_id}_or_use_current_loaded_route"
            blockers = [
                f"current_source_format={source_format}",
                f"expected_source_format={expected_format}",
            ]
        return {
            "route_id": route_id,
            "route_kind": "direct_r8p_source_package",
            "expected_source_format": expected_format,
            "route_preflight_status": status,
            "configured_path": str(source_path),
            "path_exists": source_exists,
            "path_is_directory": source_is_dir,
            "current_source_status": source_status,
            "current_source_format": source_format,
            "route_matches_current_source": route_matches_current_source,
            "validation_command": validation_command,
            "env_override": f"{env_override_name}=<path> {validation_command}",
            "next_operator_action": next_action,
            "blockers": blockers,
            "can_route_to_r8v": bool(can_route_to_r8v and route_matches_current_source),
            "can_generate_field_evidence_by_route_only": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "field_claim_upgrade_allowed": False,
        }

    r7_status = str(
        field_rows_r7_completion_route_work_package_preflight.get(
            "route_work_package_preflight_status",
            "",
        )
    )
    r7_assembly_status = str(
        field_rows_r7_completion_route_work_package_assembly_gate.get(
            "route_work_package_assembly_gate_status",
            "",
        )
    )
    if can_route_to_r8v:
        r7_route_status = "route_preflight_not_needed_after_r8p_ready_for_r8v"
        r7_next_action = "R8v_route_pressure_resolution_rows_to_field_replay_and_holdout_gates"
        r7_blockers: list[str] = []
    elif r7_status.startswith("route_work_package_preflight_passed") and not r7_assembly_status.startswith(
        "route_work_package_assembly_gate_blocked"
    ):
        r7_route_status = "route_preflight_ready_for_r7_to_r8p_assembly"
        r7_next_action = "R8p_assemble_rows_from_r7_to_r8p_work_package"
        r7_blockers = []
    elif "waiting" in r7_status or not str(
        field_rows_r7_completion_route_work_package_preflight.get("configured_submission_dir", "")
    ):
        r7_route_status = "route_preflight_waiting_for_r7_to_r8p_work_package_submission"
        r7_next_action = "R8p_submit_r7_to_r8p_work_package_directory"
        r7_blockers = ["R7_TO_R8P_WORK_PACKAGE_DIR_not_configured_or_not_submitted"]
    else:
        r7_route_status = "route_preflight_blocked_by_r7_to_r8p_work_package_gates"
        r7_next_action = "R8p_repair_r7_to_r8p_work_package"
        r7_blockers = [
            r7_status,
            r7_assembly_status,
            *[
                str(item)
                for item in field_rows_r7_completion_route_work_package_preflight.get(
                    "preflight_blockers",
                    [],
                )
                or []
            ],
        ]
    route_preflight_results = [
        _direct_route_result("direct_r8p_json_table_mapping", "json_table_mapping"),
        _direct_route_result(
            "direct_r8p_csv_directory",
            "csv_directory_with_optional_metadata_json",
        ),
        {
            "route_id": "r7_to_r8p_route_work_package_submission",
            "route_kind": "assembled_from_r7_field_package_operator_supplement_and_agent52_export",
            "expected_source_format": "r7_to_r8p_work_package_directory",
            "route_preflight_status": r7_route_status,
            "configured_path": str(
                field_rows_r7_completion_route_work_package_preflight.get(
                    "configured_submission_dir",
                    "",
                )
            ),
            "path_exists": bool(
                field_rows_r7_completion_route_work_package_preflight.get(
                    "configured_submission_dir_exists",
                    False,
                )
            ),
            "submitted_work_package_count": int(
                field_rows_r7_completion_route_work_package_preflight.get(
                    "submitted_work_package_count",
                    0,
                )
                or 0
            ),
            "passed_work_package_count": int(
                field_rows_r7_completion_route_work_package_preflight.get(
                    "passed_work_package_count",
                    0,
                )
                or 0
            ),
            "blocked_work_package_count": int(
                field_rows_r7_completion_route_work_package_preflight.get(
                    "blocked_work_package_count",
                    0,
                )
                or 0
            ),
            "route_work_package_preflight_status": r7_status,
            "route_work_package_assembly_gate_status": r7_assembly_status,
            "validation_command": validation_command,
            "env_override": f"R7_TO_R8P_WORK_PACKAGE_DIR=<dir> {validation_command}",
            "next_operator_action": r7_next_action,
            "blockers": r7_blockers,
            "can_route_to_r8v": False,
            "can_generate_field_evidence_by_route_only": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "field_claim_upgrade_allowed": False,
        },
    ]
    if can_route_to_r8v:
        route_preflight_results.append(
            {
                "route_id": "route_to_r8v_field_replay_and_holdout_gates",
                "route_kind": "downstream_field_replay_and_holdout_gate",
                "route_preflight_status": "route_preflight_ready_for_r8v_routing",
                "configured_path": str(source_path),
                "path_exists": source_exists,
                "current_source_status": source_status,
                "current_source_format": source_format,
                "validation_command": validation_command,
                "next_operator_action": (
                    "R8v_route_pressure_resolution_rows_to_field_replay_and_holdout_gates"
                ),
                "blockers": [],
                "can_route_to_r8v": True,
                "can_generate_field_evidence_by_route_only": False,
                "can_write_to_actuator": False,
                "can_write_to_release_gate": False,
                "field_claim_upgrade_allowed": False,
            }
        )

    ready_route_count = sum(
        1
        for result in route_preflight_results
        if str(result["route_preflight_status"]).startswith("route_preflight_ready")
    )
    waiting_route_count = sum(
        1
        for result in route_preflight_results
        if "waiting" in str(result["route_preflight_status"])
    )
    blocked_route_count = sum(
        1
        for result in route_preflight_results
        if "blocked" in str(result["route_preflight_status"])
    )
    recommended_route_id = str(
        field_rows_source_package_submission_route_guide.get("recommended_route_id", "")
    )
    if recommended_route_id == "direct_r8p_json_or_csv_source_package":
        direct_results = [
            result
            for result in route_preflight_results
            if result["route_id"] in {"direct_r8p_json_table_mapping", "direct_r8p_csv_directory"}
        ]
        if any(str(result["route_preflight_status"]).startswith("route_preflight_ready") for result in direct_results):
            recommended_route_preflight_status = "recommended_route_preflight_ready_for_loaded_source_package"
        elif all("blocked" in str(result["route_preflight_status"]) for result in direct_results):
            recommended_route_preflight_status = "recommended_route_preflight_blocked_for_direct_source_package"
        else:
            recommended_route_preflight_status = "recommended_route_preflight_waiting_for_direct_source_package"
    else:
        recommended_result = next(
            (
                result
                for result in route_preflight_results
                if result["route_id"] == recommended_route_id
            ),
            {},
        )
        recommended_route_preflight_status = str(
            recommended_result.get(
                "route_preflight_status",
                "recommended_route_preflight_not_available",
            )
        )

    if can_route_to_r8v:
        preflight_status = "source_package_route_preflight_ready_for_r8v_routing"
        next_operator_action = "R8v_route_pressure_resolution_rows_to_field_replay_and_holdout_gates"
    elif ready_route_count:
        preflight_status = "source_package_route_preflight_ready_for_loaded_source_package_gate_repairs"
        next_operator_action = "R8p_run_validation_and_repair_loaded_source_package"
    elif blocked_route_count and not waiting_route_count:
        preflight_status = "source_package_route_preflight_blocked_all_submission_routes"
        next_operator_action = "R8p_repair_blocked_source_package_routes"
    else:
        preflight_status = "source_package_route_preflight_waiting_for_source_package_submission"
        next_operator_action = "R8p_submit_direct_json_or_csv_source_package"

    return {
        "source_package_route_preflight_id": "R8u49_source_package_route_preflight",
        "source_package_route_preflight_status": preflight_status,
        "route_preflight_path": str(ROWS_SOURCE_PACKAGE_ROUTE_PREFLIGHT_PATH),
        "model_core_layers": [
            "observability_layer",
            "closed_loop_execution_layer",
            "verification_governance_layer",
        ],
        "core_capabilities": [
            "observability",
            "verifiability",
            "engineering_feasibility",
            "protectability",
        ],
        "current_source_status": source_status,
        "current_source_format": source_format,
        "current_source_path": str(source_path),
        "source_path_exists": source_exists,
        "recommended_route_id": recommended_route_id,
        "recommended_route_preflight_status": recommended_route_preflight_status,
        "next_operator_action": next_operator_action,
        "ready_route_count": ready_route_count,
        "waiting_route_count": waiting_route_count,
        "blocked_route_count": blocked_route_count,
        "route_preflight_results": route_preflight_results,
        "technical_feature_mapping": {
            "technical_problem": (
                "A route guide can still leave field operators guessing whether the current submitted package, "
                "CSV directory, or R7 work-package route is actually actionable before replay gates."
            ),
            "technical_means": (
                "A route-level preflight converts direct JSON, direct CSV-directory, and R7-to-R8p work-package "
                "routes into explicit ready/waiting/blocked states with path, format, validation command, and blockers."
            ),
            "technical_effect": (
                "The system can select the next source-package action before R8v replay without treating templates, "
                "invalid packages, or incomplete work packages as field evidence."
            ),
            "prior_art_distinction_candidate": (
                "Unlike a generic importer, the preflight binds sparse field evidence submission routes to the same "
                "closed-loop replay/holdout boundary used by the grey-box control chain."
            ),
        },
        "evidence_boundaries": [
            "This preflight is route readiness metadata, not field evidence.",
            "Ready source-package routing still cannot write actuator, protective control, release gate, or field claim.",
            "Synthetic, sample, template, TODO, and header-only packages remain non-field evidence.",
            "R7 work packages cannot fabricate Agent52 replay rows; replay export remains a separate evidence source.",
        ],
        "can_route_to_r8v": can_route_to_r8v,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "field_claim_upgrade_allowed": False,
    }


def _submission_gate(
    gate_id: str,
    status: str,
    blockers: object,
    operator_action: str,
) -> dict[str, object]:
    if not isinstance(blockers, list):
        blockers = [blockers] if blockers not in (None, "") else []
    status_text = str(status)
    gate_passed = status_text.startswith(("schema_validation_passed", "batch_bundle_preflight_passed", "temporal_window_preflight_passed", "scenario_semantic_preflight_passed", "downstream_routing_preflight_passed"))
    return {
        "gate_id": gate_id,
        "status": status_text,
        "gate_passed": gate_passed,
        "blockers_or_summary": [str(item) for item in blockers],
        "operator_action": operator_action,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }


def _table_collection_role(table: str) -> str:
    roles = {
        "node_modality_sensor_timeseries": "low_cost_node_pressure_signal",
        "pressure_headloss_event_log": "pressure_headloss_event_evidence",
        "campaign_operation_log": "operator_review_and_control_action_evidence",
        "offline_lab_results": "slow_label_and_holdout_evidence",
        "fast_proxy_event_log": "fast_proxy_protective_trigger_evidence",
        "agent52_replay_table": "offline_control_replay_action_evidence",
    }
    return roles.get(table, "field_rows_evidence")


def _field_collection_role(table: str, field: str) -> str:
    if field == "data_origin":
        return "field_provenance_gate"
    if field == "batch_id":
        return "same_batch_join_key"
    if field in {"scenario", "scenario_id", "scenario_type"}:
        return "scenario_linkage"
    if field in {"sample_time_min", "event_time_min", "matched_lab_sample_time_min", "lab_label_time_min", "proxy_label_time_min"}:
        return "timestamp_ordering"
    if field in {"pressure_drop_kPa", "headloss_kPa_per_m", "value", "flow_Lmin"}:
        return "measured_process_signal"
    if field in {"pressure_source_resolution", "authoritative_pressure_source", "reviewer_id", "review_time", "calibration_action_id", "calibration_note"}:
        return "operator_review_calibration_record"
    if field in {"policy_action_id", "expert_action_id"}:
        return "control_replay_action_pair"
    if field in {"operator_review_required", "protective_triggered", "pressure_source_conflict_requires_operator_review", "pressure_source_conflict_control_block"}:
        return "binary_gate_or_guardrail_state"
    if field in {
        "pressure_source_conflict_count",
        "resolved_pressure_source_conflict_count",
        "unresolved_pressure_source_conflict_count",
        "pressure_source_resolution_record_count",
    }:
        return "pressure_conflict_resolution_counter"
    if table == "offline_lab_results":
        return "offline_label_or_method_metadata"
    return "field_metadata"


def _field_validation_rule(field: str) -> str:
    if field == "data_origin":
        return "must_be_field_origin_not_template_synthetic_or_todo"
    expected = _field_schema(field).get("type")
    if expected == "boolean":
        return "must_be_boolean_not_string"
    if expected == ["number", "integer"]:
        return "must_be_numeric_not_boolean"
    return "must_be_non_empty_string"


def _required_fields_for_table(table: str) -> list[str]:
    if table == "agent52_replay_table":
        return [
            "batch_id",
            "scenario",
            "policy_action_id",
            "expert_action_id",
            "pressure_source_conflict_count",
            "resolved_pressure_source_conflict_count",
            "unresolved_pressure_source_conflict_count",
            "pressure_source_resolution_record_count",
            "pressure_source_conflict_requires_operator_review",
            "pressure_source_conflict_control_block",
            "data_origin",
        ]
    return [str(field) for field in REQUIRED_TABLE_FIELDS.get(table, [])]


def _row_plan_by_scenario(row_collection_plan: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    return {
        str(row.get("scenario_id", "")): row
        for row in row_collection_plan
        if isinstance(row, dict) and row.get("scenario_id")
    }


def _safe_patch_token(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() else "_" for ch in value.upper())
    return "_".join(part for part in cleaned.split("_") if part)[:96] or "UNKNOWN"


def _deliverable_md(
    report,
    field_rows_source: dict[str, object],
    field_rows_schema_validation: dict[str, object] | None = None,
    field_rows_collection_checklist: dict[str, object] | None = None,
    field_rows_batch_bundle_preflight: dict[str, object] | None = None,
    field_rows_temporal_window_preflight: dict[str, object] | None = None,
    field_rows_scenario_semantic_preflight: dict[str, object] | None = None,
    field_rows_downstream_routing_preflight: dict[str, object] | None = None,
    field_rows_downstream_route_handoff: dict[str, object] | None = None,
    field_rows_downstream_target_gate_preflight: dict[str, object] | None = None,
    field_rows_downstream_target_gate_result_intake_schema: dict[str, object] | None = None,
    field_rows_downstream_target_gate_result_preflight: dict[str, object] | None = None,
    field_rows_downstream_target_gate_result_arbitration: dict[str, object] | None = None,
    field_rows_downstream_target_gate_operator_review_template: dict[str, object] | None = None,
    field_rows_downstream_target_gate_operator_review_preflight: dict[str, object] | None = None,
    field_rows_downstream_target_gate_post_review_gate: dict[str, object] | None = None,
    field_rows_downstream_target_gate_protective_candidate_evaluation: dict[str, object] | None = None,
    field_rows_r7_staging_preflight: dict[str, object] | None = None,
    field_rows_r7_completion_plan: dict[str, object] | None = None,
    field_rows_r7_completion_route_contracts: dict[str, object] | None = None,
    field_rows_r7_completion_route_work_packages: dict[str, object] | None = None,
    field_rows_r7_completion_route_work_package_templates: dict[str, object] | None = None,
    field_rows_r7_completion_route_work_package_preflight: dict[str, object] | None = None,
    field_rows_r7_completion_route_work_package_patch_plan: dict[str, object] | None = None,
    field_rows_r7_completion_route_work_package_assembly_gate: dict[str, object] | None = None,
    field_rows_submission_readiness_review: dict[str, object] | None = None,
    field_rows_source_package_submission_route_guide: dict[str, object] | None = None,
    field_rows_source_package_route_preflight: dict[str, object] | None = None,
) -> str:
    readiness = report.metrics["readiness"]
    row_readiness = report.metrics["row_collection_readiness"]
    field_acceptance = report.metrics["field_row_acceptance"]
    field_rows_package_schema = _field_rows_package_schema()
    field_rows_schema_validation = field_rows_schema_validation or {}
    field_rows_batch_bundle_preflight = field_rows_batch_bundle_preflight or {}
    field_rows_temporal_window_preflight = field_rows_temporal_window_preflight or {}
    field_rows_scenario_semantic_preflight = field_rows_scenario_semantic_preflight or {}
    field_rows_downstream_routing_preflight = field_rows_downstream_routing_preflight or {}
    field_rows_downstream_route_handoff = field_rows_downstream_route_handoff or {}
    field_rows_downstream_target_gate_preflight = field_rows_downstream_target_gate_preflight or {}
    field_rows_downstream_target_gate_result_intake_schema = (
        field_rows_downstream_target_gate_result_intake_schema or {}
    )
    field_rows_downstream_target_gate_result_preflight = (
        field_rows_downstream_target_gate_result_preflight or {}
    )
    field_rows_downstream_target_gate_result_arbitration = (
        field_rows_downstream_target_gate_result_arbitration or {}
    )
    field_rows_downstream_target_gate_operator_review_template = (
        field_rows_downstream_target_gate_operator_review_template or {}
    )
    field_rows_downstream_target_gate_operator_review_preflight = (
        field_rows_downstream_target_gate_operator_review_preflight or {}
    )
    field_rows_downstream_target_gate_post_review_gate = (
        field_rows_downstream_target_gate_post_review_gate or {}
    )
    field_rows_downstream_target_gate_protective_candidate_evaluation = (
        field_rows_downstream_target_gate_protective_candidate_evaluation or {}
    )
    field_rows_r7_staging_preflight = field_rows_r7_staging_preflight or {}
    field_rows_r7_completion_plan = field_rows_r7_completion_plan or {}
    field_rows_r7_completion_route_contracts = field_rows_r7_completion_route_contracts or {}
    field_rows_r7_completion_route_work_packages = field_rows_r7_completion_route_work_packages or {}
    field_rows_r7_completion_route_work_package_templates = (
        field_rows_r7_completion_route_work_package_templates or {}
    )
    field_rows_r7_completion_route_work_package_preflight = (
        field_rows_r7_completion_route_work_package_preflight or {}
    )
    field_rows_r7_completion_route_work_package_patch_plan = (
        field_rows_r7_completion_route_work_package_patch_plan or {}
    )
    field_rows_r7_completion_route_work_package_assembly_gate = (
        field_rows_r7_completion_route_work_package_assembly_gate or {}
    )
    field_rows_submission_readiness_review = field_rows_submission_readiness_review or {}
    field_rows_source_package_submission_route_guide = field_rows_source_package_submission_route_guide or {}
    field_rows_source_package_route_preflight = field_rows_source_package_route_preflight or {}
    patch_plan = _field_rows_patch_plan(
        report,
        field_rows_source,
        field_rows_schema_validation,
        field_rows_batch_bundle_preflight,
        field_rows_temporal_window_preflight,
        field_rows_scenario_semantic_preflight,
    )
    field_rows_collection_checklist = field_rows_collection_checklist or _field_rows_collection_checklist(
        report,
        field_rows_source,
        patch_plan,
        field_rows_package_schema,
        field_rows_schema_validation,
        field_rows_batch_bundle_preflight,
        field_rows_temporal_window_preflight,
        field_rows_scenario_semantic_preflight,
    )
    operator_handoff = _field_rows_operator_handoff(
        report,
        field_rows_source,
        patch_plan,
        field_rows_package_schema,
        field_rows_schema_validation,
        field_rows_collection_checklist,
        field_rows_batch_bundle_preflight,
        field_rows_temporal_window_preflight,
        field_rows_scenario_semantic_preflight,
        field_rows_downstream_routing_preflight,
    )
    lines = [
        "# R8o Pressure Resolution Replay 场景采集包",
        "",
        f"- scenario_pack_status：`{readiness['scenario_pack_status']}`",
        f"- scenario_schema_coverage：`{readiness['scenario_schema_coverage']}`",
        f"- field_scenario_coverage：`{readiness['field_scenario_coverage']}`",
        f"- source_chain_resolution_fields_ready：`{readiness['source_chain_resolution_fields_ready']}`",
        f"- can_update_agent60_fallback：`{readiness['can_update_agent60_fallback']}`",
        f"- can_upgrade_field_supported_claim：`{readiness['can_upgrade_field_supported_claim']}`",
        f"- can_write_to_actuator：`{readiness['can_write_to_actuator']}`",
        f"- can_write_to_release_gate：`{readiness['can_write_to_release_gate']}`",
        f"- row_collection_plan_status：`{row_readiness['row_collection_plan_status']}`",
        f"- missing_scenario_count：`{row_readiness['missing_scenario_count']}`",
        f"- template_row_count：`{row_readiness['template_row_count']}`",
        f"- field_row_acceptance_status：`{field_acceptance['field_row_acceptance_status']}`",
        f"- accepted_field_scenario_count：`{field_acceptance['accepted_scenario_count']}`",
        f"- accepted_field_batch_count：`{field_acceptance['accepted_batch_count']}`",
        f"- field_rows_source_status：`{field_rows_source['field_rows_source_status']}`",
        f"- field_rows_source_path：`{field_rows_source['field_rows_source_path']}`",
        f"- field_rows_patch_plan_status：`{patch_plan['field_rows_patch_plan_status']}`",
        f"- field_rows_patch_item_count：`{patch_plan['patch_item_count']}`",
        f"- field_rows_operator_handoff_status：`{operator_handoff['field_rows_operator_handoff_status']}`",
        f"- field_rows_package_schema_status：`{operator_handoff['field_rows_package_schema_status']}`",
        f"- field_rows_schema_validation_status：`{operator_handoff['field_rows_schema_validation_status']}`",
        f"- field_rows_collection_checklist_status：`{operator_handoff['field_rows_collection_checklist_status']}`",
        f"- field_rows_batch_bundle_preflight_status：`{operator_handoff['field_rows_batch_bundle_preflight_status']}`",
        f"- schema_required_field_gap_count：`{field_rows_schema_validation.get('required_field_gap_count', 0)}`",
        f"- schema_invalid_type_count：`{field_rows_schema_validation.get('invalid_type_count', 0)}`",
        f"- schema_template_marker_gap_count：`{field_rows_schema_validation.get('template_marker_gap_count', 0)}`",
        f"- schema_field_origin_gap_count：`{field_rows_schema_validation.get('field_origin_gap_count', 0)}`",
        f"- complete_batch_bundle_count：`{field_rows_batch_bundle_preflight.get('complete_bundle_count', 0)}`",
        f"- partial_batch_bundle_count：`{field_rows_batch_bundle_preflight.get('partial_bundle_count', 0)}`",
        f"- missing_bundle_table_count：`{field_rows_batch_bundle_preflight.get('missing_bundle_table_count', 0)}`",
        f"- field_rows_temporal_window_preflight_status：`{operator_handoff['field_rows_temporal_window_preflight_status']}`",
        f"- temporal_valid_batch_count：`{field_rows_temporal_window_preflight.get('temporal_valid_batch_count', 0)}`",
        f"- temporal_violation_count：`{field_rows_temporal_window_preflight.get('temporal_violation_count', 0)}`",
        f"- hold_time_violation_count：`{field_rows_temporal_window_preflight.get('hold_time_violation_count', 0)}`",
        f"- field_rows_scenario_semantic_preflight_status：`{operator_handoff['field_rows_scenario_semantic_preflight_status']}`",
        f"- semantic_valid_batch_count：`{field_rows_scenario_semantic_preflight.get('semantic_valid_batch_count', 0)}`",
        f"- semantic_violation_count：`{field_rows_scenario_semantic_preflight.get('semantic_violation_count', 0)}`",
        f"- field_rows_downstream_routing_preflight_status：`{operator_handoff['field_rows_downstream_routing_preflight_status']}`",
        f"- routing_ready_target_count：`{field_rows_downstream_routing_preflight.get('routing_ready_target_count', 0)}`",
        f"- can_route_to_r8v：`{field_rows_downstream_routing_preflight.get('can_route_to_r8v', False)}`",
        f"- field_rows_downstream_route_handoff_status：`{field_rows_downstream_route_handoff.get('downstream_route_handoff_status', 'not_run')}`",
        f"- downstream_handoff_ready_target_count：`{field_rows_downstream_route_handoff.get('ready_handoff_target_count', 0)}`",
        f"- downstream_handoff_blocked_target_count：`{field_rows_downstream_route_handoff.get('blocked_handoff_target_count', 0)}`",
        f"- field_rows_downstream_target_gate_preflight_status：`{field_rows_downstream_target_gate_preflight.get('downstream_target_gate_preflight_status', 'not_run')}`",
        f"- downstream_target_gate_ready_count：`{field_rows_downstream_target_gate_preflight.get('ready_target_gate_count', 0)}`",
        f"- downstream_target_gate_blocked_count：`{field_rows_downstream_target_gate_preflight.get('blocked_target_gate_count', 0)}`",
        f"- field_rows_downstream_target_gate_result_preflight_status：`{field_rows_downstream_target_gate_result_preflight.get('downstream_target_gate_result_preflight_status', 'not_run')}`",
        f"- downstream_target_gate_result_accepted_count：`{field_rows_downstream_target_gate_result_preflight.get('accepted_target_result_count', 0)}`",
        f"- downstream_target_gate_result_rejected_count：`{field_rows_downstream_target_gate_result_preflight.get('rejected_target_result_count', 0)}`",
        f"- field_rows_downstream_target_gate_result_arbitration_status：`{field_rows_downstream_target_gate_result_arbitration.get('downstream_target_gate_result_arbitration_status', 'not_run')}`",
        f"- downstream_target_gate_result_arbitration_next_action：`{field_rows_downstream_target_gate_result_arbitration.get('next_operator_action', '')}`",
        f"- field_rows_downstream_target_gate_operator_review_preflight_status：`{field_rows_downstream_target_gate_operator_review_preflight.get('downstream_target_gate_operator_review_preflight_status', 'not_run')}`",
        f"- downstream_target_gate_operator_review_approved_count：`{field_rows_downstream_target_gate_operator_review_preflight.get('approved_operator_review_count', 0)}`",
        f"- downstream_target_gate_operator_review_hold_count：`{field_rows_downstream_target_gate_operator_review_preflight.get('hold_operator_review_count', 0)}`",
        f"- downstream_target_gate_operator_review_next_action：`{field_rows_downstream_target_gate_operator_review_preflight.get('next_operator_action', '')}`",
        f"- field_rows_downstream_target_gate_post_review_gate_status：`{field_rows_downstream_target_gate_post_review_gate.get('downstream_target_gate_post_review_gate_status', 'not_run')}`",
        f"- downstream_target_gate_post_review_can_route_to_protective_candidate：`{field_rows_downstream_target_gate_post_review_gate.get('can_route_to_protective_candidate_evaluation', False)}`",
        f"- downstream_target_gate_post_review_can_emit_protective_candidate：`{field_rows_downstream_target_gate_post_review_gate.get('can_emit_protective_control_candidate', False)}`",
        f"- downstream_target_gate_post_review_next_action：`{field_rows_downstream_target_gate_post_review_gate.get('next_operator_action', '')}`",
        f"- field_rows_downstream_target_gate_protective_candidate_evaluation_status：`{field_rows_downstream_target_gate_protective_candidate_evaluation.get('downstream_target_gate_protective_candidate_evaluation_status', 'not_run')}`",
        f"- downstream_target_gate_protective_candidate_can_emit：`{field_rows_downstream_target_gate_protective_candidate_evaluation.get('can_emit_protective_control_candidate', False)}`",
        f"- downstream_target_gate_protective_candidate_can_route_to_final_execution_review：`{field_rows_downstream_target_gate_protective_candidate_evaluation.get('can_route_to_final_execution_review', False)}`",
        f"- downstream_target_gate_protective_candidate_next_action：`{field_rows_downstream_target_gate_protective_candidate_evaluation.get('next_operator_action', '')}`",
        f"- r7_to_r8p_staging_status：`{field_rows_r7_staging_preflight.get('r7_staging_preflight_status', 'not_run')}`",
        f"- r7_staged_row_count：`{field_rows_r7_staging_preflight.get('staged_row_count', 0)}`",
        f"- r7_staging_required_field_gap_count：`{field_rows_r7_staging_preflight.get('required_field_gap_count', 0)}`",
        f"- r7_staging_agent52_export_gap_count：`{field_rows_r7_staging_preflight.get('agent52_export_required_field_gap_count', 0)}`",
        f"- r7_to_r8p_completion_plan_status：`{field_rows_r7_completion_plan.get('completion_plan_status', 'not_run')}`",
        f"- r7_to_r8p_completion_item_count：`{field_rows_r7_completion_plan.get('item_count', 0)}`",
        f"- r7_completion_route_contracts_status：`{field_rows_r7_completion_route_contracts.get('completion_route_contracts_status', 'not_run')}`",
        f"- r7_completion_open_route_count：`{field_rows_r7_completion_route_contracts.get('open_route_count', 0)}`",
        f"- r7_completion_route_work_packages_status：`{field_rows_r7_completion_route_work_packages.get('route_work_packages_status', 'not_run')}`",
        f"- r7_completion_open_work_package_count：`{field_rows_r7_completion_route_work_packages.get('open_work_package_count', 0)}`",
        f"- r7_completion_route_work_package_templates_status：`{field_rows_r7_completion_route_work_package_templates.get('route_work_package_templates_status', 'not_run')}`",
        f"- r7_completion_route_work_package_preflight_status：`{field_rows_r7_completion_route_work_package_preflight.get('route_work_package_preflight_status', 'not_run')}`",
        f"- r7_completion_blocked_work_package_count：`{field_rows_r7_completion_route_work_package_preflight.get('blocked_work_package_count', 0)}`",
        f"- r7_completion_route_work_package_patch_plan_status：`{field_rows_r7_completion_route_work_package_patch_plan.get('route_work_package_patch_plan_status', 'not_run')}`",
        f"- r7_completion_route_work_package_patch_item_count：`{field_rows_r7_completion_route_work_package_patch_plan.get('patch_item_count', 0)}`",
        f"- r7_completion_route_work_package_highest_priority_patch_id：`{field_rows_r7_completion_route_work_package_patch_plan.get('highest_priority_patch_id', '')}`",
        f"- r7_completion_route_work_package_assembly_gate_status：`{field_rows_r7_completion_route_work_package_assembly_gate.get('route_work_package_assembly_gate_status', 'not_run')}`",
        f"- r7_completion_route_work_package_blocked_assembly_step_count：`{field_rows_r7_completion_route_work_package_assembly_gate.get('blocked_assembly_step_count', 0)}`",
        f"- field_rows_submission_readiness_review_status：`{field_rows_submission_readiness_review.get('submission_readiness_review_status', 'not_run')}`",
        f"- field_rows_submission_readiness_next_action：`{field_rows_submission_readiness_review.get('next_operator_action', '')}`",
        f"- field_rows_submission_readiness_can_route_to_r8v：`{field_rows_submission_readiness_review.get('can_route_to_r8v', False)}`",
        f"- field_rows_source_package_route_guide_status：`{field_rows_source_package_submission_route_guide.get('source_package_submission_route_guide_status', 'not_run')}`",
        f"- field_rows_source_package_recommended_route：`{field_rows_source_package_submission_route_guide.get('recommended_route_id', '')}`",
        f"- field_rows_source_package_route_option_count：`{field_rows_source_package_submission_route_guide.get('route_option_count', 0)}`",
        f"- field_rows_source_package_route_preflight_status：`{field_rows_source_package_route_preflight.get('source_package_route_preflight_status', 'not_run')}`",
        f"- field_rows_source_package_recommended_route_preflight：`{field_rows_source_package_route_preflight.get('recommended_route_preflight_status', '')}`",
        f"- field_rows_source_package_ready_route_count：`{field_rows_source_package_route_preflight.get('ready_route_count', 0)}`",
        f"- real_rows_template_path：`{TEMPLATE_ROWS_PATH}`",
        f"- real_rows_csv_template_dir：`{ROWS_CSV_TEMPLATE_DIR}`",
        f"- r7_to_r8p_alignment_path：`{ROWS_R7_ALIGNMENT_PATH}`",
        f"- r7_to_r8p_staging_preflight_path：`{ROWS_R7_STAGING_PREFLIGHT_PATH}`",
        f"- r7_to_r8p_staged_draft_path：`{ROWS_R7_STAGED_DRAFT_PATH}`",
        f"- r7_to_r8p_completion_plan_path：`{ROWS_R7_COMPLETION_PLAN_PATH}`",
        f"- r7_to_r8p_completion_route_contracts_path：`{ROWS_R7_COMPLETION_ROUTE_CONTRACTS_PATH}`",
        f"- r7_to_r8p_completion_route_work_packages_path：`{ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGES_PATH}`",
        f"- r7_to_r8p_completion_route_work_package_template_dir：`{ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_TEMPLATE_DIR}`",
        f"- r7_to_r8p_completion_route_work_package_preflight_path：`{ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_PREFLIGHT_PATH}`",
        f"- r7_to_r8p_completion_route_work_package_patch_plan_path：`{ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_PATCH_PLAN_PATH}`",
        f"- r7_to_r8p_completion_route_work_package_assembly_gate_path：`{ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_ASSEMBLY_GATE_PATH}`",
        f"- real_rows_schema_path：`{ROWS_SCHEMA_PATH}`",
        f"- batch_bundle_preflight_path：`{ROWS_BATCH_BUNDLE_PREFLIGHT_PATH}`",
        f"- temporal_window_preflight_path：`{ROWS_TEMPORAL_WINDOW_PREFLIGHT_PATH}`",
        f"- scenario_semantic_preflight_path：`{ROWS_SCENARIO_SEMANTIC_PREFLIGHT_PATH}`",
        f"- downstream_routing_preflight_path：`{ROWS_DOWNSTREAM_ROUTING_PREFLIGHT_PATH}`",
        "",
        "## Scenario Matrix",
        "",
        "| Scenario | Type | Field Evidence | Purpose | Acceptance Metrics |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for row in report.metrics["pressure_resolution_replay_scenario_matrix"]:
        lines.append(
            f"| `{row['scenario_id']}` | `{row['scenario_type']}` | `{row['field_evidence_count']}` | "
            f"{row['purpose']} | `{row['acceptance_metrics']}` |"
        )
    lines.extend(["", "## Required Table Fields", ""])
    for table, fields in report.metrics["required_table_field_matrix"].items():
        lines.append(f"- `{table}`：`{fields}`")
    lines.extend(
        [
            "",
            "## R8p Row Collection Plan",
            "",
            "| Collection | Scenario | Batch Role | Status | Required Tables | Agent52 Fields |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in report.metrics["row_collection_plan"]:
        lines.append(
            f"| `{row['collection_id']}` | `{row['scenario_id']}` | `{row['batch_role']}` | "
            f"`{row['collection_status']}` | `{row['required_tables']}` | "
            f"`{row['agent52_replay_required_fields']}` |"
        )
    lines.extend(
        [
            "",
            "## R8p Field Row Acceptance Gate",
            "",
            "| Scenario | Status | Candidate Batches | Accepted Batches | Blocking Reasons |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in field_acceptance["scenario_acceptance"]:
        lines.append(
            f"| `{row['scenario_id']}` | `{row['acceptance_status']}` | "
            f"`{row.get('candidate_batches', [])}` | `{row['accepted_batches']}` | "
            f"`{row['blocking_reasons']}` |"
        )
    lines.extend(
        [
            "",
            "## Field Rows Source Preflight",
            "",
            f"- source：`{field_rows_source['field_rows_source']}`",
            f"- status：`{field_rows_source['field_rows_source_status']}`",
            f"- path：`{field_rows_source['field_rows_source_path']}`",
            f"- row_count：`{field_rows_source['row_count']}`",
            f"- missing_tables：`{field_rows_source['missing_tables']}`",
            f"- empty_tables：`{field_rows_source['empty_tables']}`",
            f"- invalid_table_shapes：`{field_rows_source['invalid_table_shapes']}`",
            f"- unknown_tables：`{field_rows_source['unknown_tables']}`",
            f"- preflight_blockers：`{field_rows_source['preflight_blockers']}`",
        ]
    )
    lines.extend(
        [
            "",
            "## R8p Field Rows Schema Validation",
            "",
            f"- status：`{field_rows_schema_validation.get('field_rows_schema_validation_status', 'schema_validation_not_run')}`",
            f"- schema_id：`{field_rows_schema_validation.get('schema_id', '')}`",
            f"- source_status：`{field_rows_schema_validation.get('source_status', '')}`",
            f"- required_table_count：`{field_rows_schema_validation.get('required_table_count', 0)}`",
            f"- loaded_table_count：`{field_rows_schema_validation.get('loaded_table_count', 0)}`",
            f"- loaded_row_count：`{field_rows_schema_validation.get('loaded_row_count', 0)}`",
            f"- required_field_gap_count：`{field_rows_schema_validation.get('required_field_gap_count', 0)}`",
            f"- invalid_type_count：`{field_rows_schema_validation.get('invalid_type_count', 0)}`",
            f"- template_marker_gap_count：`{field_rows_schema_validation.get('template_marker_gap_count', 0)}`",
            f"- field_origin_gap_count：`{field_rows_schema_validation.get('field_origin_gap_count', 0)}`",
            f"- boundary：{field_rows_schema_validation.get('schema_validation_boundary', '')}",
            "",
            "| Table | Status | Rows | Missing Required Fields | Invalid Types | Template Markers | Field Origin Gaps |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for table_validation in field_rows_schema_validation.get("table_validations", []) or []:
        if not isinstance(table_validation, dict):
            continue
        lines.append(
            f"| `{table_validation.get('table')}` | `{table_validation.get('table_schema_status')}` | "
            f"{table_validation.get('row_count', 0)} | "
            f"{table_validation.get('missing_required_field_count', 0)} | "
            f"{table_validation.get('invalid_type_count', 0)} | "
            f"{table_validation.get('template_marker_gap_count', 0)} | "
            f"{table_validation.get('field_origin_gap_count', 0)} |"
        )
    lines.extend(
        [
            "",
            "## R8p Same-Batch Bundle Preflight",
            "",
            f"- status：`{field_rows_batch_bundle_preflight.get('field_rows_batch_bundle_preflight_status', 'batch_bundle_preflight_not_run')}`",
            f"- preflight_path：`{field_rows_batch_bundle_preflight.get('preflight_path', ROWS_BATCH_BUNDLE_PREFLIGHT_PATH)}`",
            f"- candidate_batch_count：`{field_rows_batch_bundle_preflight.get('candidate_batch_count', 0)}`",
            f"- complete_bundle_count：`{field_rows_batch_bundle_preflight.get('complete_bundle_count', 0)}`",
            f"- partial_bundle_count：`{field_rows_batch_bundle_preflight.get('partial_bundle_count', 0)}`",
            f"- missing_bundle_table_count：`{field_rows_batch_bundle_preflight.get('missing_bundle_table_count', 0)}`",
            f"- boundary：{field_rows_batch_bundle_preflight.get('batch_bundle_boundary', '')}",
            "",
            "| Scenario | Bundle Status | Candidate Batches | Complete Batches | Missing Tables By Batch |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for scenario_bundle in field_rows_batch_bundle_preflight.get("scenario_bundle_status", []) or []:
        if not isinstance(scenario_bundle, dict):
            continue
        lines.append(
            f"| `{scenario_bundle.get('scenario_id')}` | `{scenario_bundle.get('bundle_preflight_status')}` | "
            f"`{scenario_bundle.get('candidate_batches', [])}` | "
            f"`{scenario_bundle.get('complete_candidate_batches', [])}` | "
            f"`{scenario_bundle.get('missing_tables_by_candidate_batch', {})}` |"
        )
    lines.extend(
        [
            "",
            "## R8p Temporal Window Preflight",
            "",
            f"- status：`{field_rows_temporal_window_preflight.get('field_rows_temporal_window_preflight_status', 'temporal_window_preflight_not_run')}`",
            f"- preflight_path：`{field_rows_temporal_window_preflight.get('preflight_path', ROWS_TEMPORAL_WINDOW_PREFLIGHT_PATH)}`",
            f"- checked_batch_count：`{field_rows_temporal_window_preflight.get('checked_batch_count', 0)}`",
            f"- temporal_valid_batch_count：`{field_rows_temporal_window_preflight.get('temporal_valid_batch_count', 0)}`",
            f"- temporal_violation_count：`{field_rows_temporal_window_preflight.get('temporal_violation_count', 0)}`",
            f"- hold_time_violation_count：`{field_rows_temporal_window_preflight.get('hold_time_violation_count', 0)}`",
            f"- boundary：{field_rows_temporal_window_preflight.get('temporal_window_boundary', '')}",
            "",
            "| Scenario | Temporal Status | Valid Batches | Violations By Batch | Latency Margin By Batch |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for scenario_temporal in field_rows_temporal_window_preflight.get("scenario_temporal_status", []) or []:
        if not isinstance(scenario_temporal, dict):
            continue
        lines.append(
            f"| `{scenario_temporal.get('scenario_id')}` | `{scenario_temporal.get('temporal_preflight_status')}` | "
            f"`{scenario_temporal.get('temporal_valid_batches', [])}` | "
            f"`{scenario_temporal.get('violations_by_batch', {})}` | "
            f"`{scenario_temporal.get('latency_margin_min_by_batch', {})}` |"
        )
    lines.extend(
        [
            "",
            "## R8p Scenario Semantic Preflight",
            "",
            f"- status：`{field_rows_scenario_semantic_preflight.get('field_rows_scenario_semantic_preflight_status', 'scenario_semantic_preflight_not_run')}`",
            f"- preflight_path：`{field_rows_scenario_semantic_preflight.get('preflight_path', ROWS_SCENARIO_SEMANTIC_PREFLIGHT_PATH)}`",
            f"- checked_batch_count：`{field_rows_scenario_semantic_preflight.get('checked_batch_count', 0)}`",
            f"- semantic_valid_batch_count：`{field_rows_scenario_semantic_preflight.get('semantic_valid_batch_count', 0)}`",
            f"- semantic_violation_count：`{field_rows_scenario_semantic_preflight.get('semantic_violation_count', 0)}`",
            f"- condition_violation_counts：`{field_rows_scenario_semantic_preflight.get('condition_violation_counts', {})}`",
            f"- boundary：{field_rows_scenario_semantic_preflight.get('scenario_semantic_boundary', '')}",
            "",
            "| Scenario | Semantic Status | Temporal Valid Batches | Semantic Valid Batches | Violations By Batch | Condition Checks By Batch |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for scenario_semantic in field_rows_scenario_semantic_preflight.get("scenario_semantic_status", []) or []:
        if not isinstance(scenario_semantic, dict):
            continue
        lines.append(
            f"| `{scenario_semantic.get('scenario_id')}` | `{scenario_semantic.get('scenario_semantic_preflight_status')}` | "
            f"`{scenario_semantic.get('temporal_valid_batches', [])}` | "
            f"`{scenario_semantic.get('semantic_valid_batches', [])}` | "
            f"`{scenario_semantic.get('violations_by_batch', {})}` | "
            f"`{scenario_semantic.get('condition_checks_by_batch', {})}` |"
        )
    lines.extend(
        [
            "",
            "## R8v Downstream Routing Preflight",
            "",
            f"- status：`{field_rows_downstream_routing_preflight.get('field_rows_downstream_routing_preflight_status', 'downstream_routing_preflight_not_run')}`",
            f"- preflight_path：`{field_rows_downstream_routing_preflight.get('preflight_path', ROWS_DOWNSTREAM_ROUTING_PREFLIGHT_PATH)}`",
            f"- field_row_acceptance_status：`{field_rows_downstream_routing_preflight.get('field_row_acceptance_status', '')}`",
            f"- accepted_batch_count：`{field_rows_downstream_routing_preflight.get('accepted_batch_count', 0)}`",
            f"- routing_target_count：`{field_rows_downstream_routing_preflight.get('routing_target_count', 0)}`",
            f"- routing_ready_target_count：`{field_rows_downstream_routing_preflight.get('routing_ready_target_count', 0)}`",
            f"- can_route_to_r8v：`{field_rows_downstream_routing_preflight.get('can_route_to_r8v', False)}`",
            f"- boundary：{field_rows_downstream_routing_preflight.get('downstream_routing_boundary', '')}",
            "",
            "| Target | Status | Agent | Expected Gate Metrics |",
            "| --- | --- | --- | --- |",
        ]
    )
    for target in field_rows_downstream_routing_preflight.get("routing_targets", []) or []:
        if not isinstance(target, dict):
            continue
        lines.append(
            f"| `{target.get('target_id')}` | `{target.get('routing_status')}` | "
            f"`{target.get('target_agent')}` | `{target.get('expected_gate_metrics', [])}` |"
        )
    if field_rows_downstream_route_handoff:
        lines.extend(
            [
                "",
                "## R8v Downstream Route Handoff",
                "",
                f"- status：`{field_rows_downstream_route_handoff.get('downstream_route_handoff_status', '')}`",
                f"- handoff_path：`{field_rows_downstream_route_handoff.get('handoff_path', ROWS_DOWNSTREAM_ROUTE_HANDOFF_PATH)}`",
                f"- handoff_target_count：`{field_rows_downstream_route_handoff.get('handoff_target_count', 0)}`",
                f"- ready_handoff_target_count：`{field_rows_downstream_route_handoff.get('ready_handoff_target_count', 0)}`",
                f"- blocked_handoff_target_count：`{field_rows_downstream_route_handoff.get('blocked_handoff_target_count', 0)}`",
                f"- next_operator_action：`{field_rows_downstream_route_handoff.get('next_operator_action', '')}`",
                "",
                "| Target | Handoff Status | Agent | Next Action |",
                "| --- | --- | --- | --- |",
            ]
        )
        for target in field_rows_downstream_route_handoff.get("handoff_targets", []) or []:
            if not isinstance(target, dict):
                continue
            lines.append(
                f"| `{target.get('target_id')}` | `{target.get('handoff_status')}` | "
                f"`{target.get('target_agent')}` | `{target.get('next_operator_action')}` |"
            )
    if field_rows_downstream_target_gate_preflight:
        lines.extend(
            [
                "",
                "## R8v Downstream Target Gate Preflight",
                "",
                "- status："
                f"`{field_rows_downstream_target_gate_preflight.get('downstream_target_gate_preflight_status', '')}`",
                "- target_gate_preflight_path："
                f"`{field_rows_downstream_target_gate_preflight.get('target_gate_preflight_path', ROWS_DOWNSTREAM_TARGET_GATE_PREFLIGHT_PATH)}`",
                "- target_gate_count："
                f"`{field_rows_downstream_target_gate_preflight.get('target_gate_count', 0)}`",
                "- ready_target_gate_count："
                f"`{field_rows_downstream_target_gate_preflight.get('ready_target_gate_count', 0)}`",
                "- blocked_target_gate_count："
                f"`{field_rows_downstream_target_gate_preflight.get('blocked_target_gate_count', 0)}`",
                "- next_operator_action："
                f"`{field_rows_downstream_target_gate_preflight.get('next_operator_action', '')}`",
                "- boundary：target gate preflight only prepares executable downstream contracts; it is not replay, holdout, field evidence, or release clearance.",
                "",
                "| Target | Status | Command | Expected Artifact |",
                "| --- | --- | --- | --- |",
            ]
        )
        for target in field_rows_downstream_target_gate_preflight.get("target_gate_preflights", []) or []:
            if not isinstance(target, dict):
                continue
            lines.append(
                f"| `{target.get('target_id')}` | `{target.get('target_gate_preflight_status')}` | "
                f"`{target.get('validation_command')}` | `{target.get('expected_metrics_artifact')}` |"
            )
    if field_rows_downstream_target_gate_result_preflight:
        lines.extend(
            [
                "",
                "## R8v Downstream Target Gate Result Intake",
                "",
                "- schema_status："
                f"`{field_rows_downstream_target_gate_result_intake_schema.get('downstream_target_gate_result_intake_schema_id', '')}`",
                "- result_preflight_status："
                f"`{field_rows_downstream_target_gate_result_preflight.get('downstream_target_gate_result_preflight_status', '')}`",
                "- result_package_env_var："
                f"`{field_rows_downstream_target_gate_result_preflight.get('result_package_env_var', 'R8V_TARGET_GATE_RESULT_PACKAGE_PATH')}`",
                "- submitted/accepted/rejected："
                f"`{field_rows_downstream_target_gate_result_preflight.get('submitted_target_result_count', 0)}`/"
                f"`{field_rows_downstream_target_gate_result_preflight.get('accepted_target_result_count', 0)}`/"
                f"`{field_rows_downstream_target_gate_result_preflight.get('rejected_target_result_count', 0)}`",
                "- next_operator_action："
                f"`{field_rows_downstream_target_gate_result_preflight.get('next_operator_action', '')}`",
                "- boundary：result intake validates returned target-gate result package structure only; it never authorizes actuator or release-gate writes.",
                "",
                "| Target | Result Status | Missing Fields | Missing Metrics | Boundary Violations |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for target in field_rows_downstream_target_gate_result_preflight.get(
            "target_result_validations",
            [],
        ) or []:
            if not isinstance(target, dict):
                continue
            lines.append(
                f"| `{target.get('target_id')}` | `{target.get('target_result_status')}` | "
                f"`{target.get('missing_fields', [])}` | "
                f"`{target.get('missing_expected_metrics', [])}` | "
                f"`{target.get('boundary_violations', [])}` |"
            )
    if field_rows_downstream_target_gate_operator_review_preflight:
        lines.extend(
            [
                "",
                "## R8v Downstream Target Gate Operator Review",
                "",
                "- template_status："
                f"`{field_rows_downstream_target_gate_operator_review_template.get('downstream_target_gate_operator_review_template_id', '')}`",
                "- operator_review_preflight_status："
                f"`{field_rows_downstream_target_gate_operator_review_preflight.get('downstream_target_gate_operator_review_preflight_status', '')}`",
                "- operator_review_env_var："
                f"`{field_rows_downstream_target_gate_operator_review_preflight.get('operator_review_env_var', 'R8V_TARGET_GATE_OPERATOR_REVIEW_PATH')}`",
                "- submitted/approved/rejected/hold："
                f"`{field_rows_downstream_target_gate_operator_review_preflight.get('submitted_operator_review_count', 0)}`/"
                f"`{field_rows_downstream_target_gate_operator_review_preflight.get('approved_operator_review_count', 0)}`/"
                f"`{field_rows_downstream_target_gate_operator_review_preflight.get('rejected_operator_review_count', 0)}`/"
                f"`{field_rows_downstream_target_gate_operator_review_preflight.get('hold_operator_review_count', 0)}`",
                "- can_route_to_post_review_gate："
                f"`{field_rows_downstream_target_gate_operator_review_preflight.get('can_route_to_post_review_gate', False)}`",
                "- boundary：operator review can only route to a later post-review gate; it never authorizes actuator or release-gate writes.",
            ]
        )
    if field_rows_downstream_target_gate_post_review_gate:
        lines.extend(
            [
                "",
                "## R8v Downstream Target Gate Post Review Gate",
                "",
                "- post_review_gate_status："
                f"`{field_rows_downstream_target_gate_post_review_gate.get('downstream_target_gate_post_review_gate_status', '')}`",
                "- approved_operator_review_count："
                f"`{field_rows_downstream_target_gate_post_review_gate.get('approved_operator_review_count', 0)}`",
                "- can_route_to_protective_candidate_evaluation："
                f"`{field_rows_downstream_target_gate_post_review_gate.get('can_route_to_protective_candidate_evaluation', False)}`",
                "- can_emit_protective_control_candidate："
                f"`{field_rows_downstream_target_gate_post_review_gate.get('can_emit_protective_control_candidate', False)}`",
                "- next_operator_action："
                f"`{field_rows_downstream_target_gate_post_review_gate.get('next_operator_action', '')}`",
                "- boundary：post-review gate can emit only a protective-control candidate for later evaluation; actuator, release-gate and field-claim writes remain blocked.",
            ]
        )
    if field_rows_downstream_target_gate_protective_candidate_evaluation:
        candidate_bundle = field_rows_downstream_target_gate_protective_candidate_evaluation.get(
            "candidate_action_bundle",
            {},
        )
        candidate_actions = candidate_bundle.get("candidate_actions", []) if isinstance(candidate_bundle, dict) else []
        lines.extend(
            [
                "",
                "## R8v Protective Control Candidate Evaluation",
                "",
                "- candidate_evaluation_status："
                f"`{field_rows_downstream_target_gate_protective_candidate_evaluation.get('downstream_target_gate_protective_candidate_evaluation_status', '')}`",
                "- candidate_target_count："
                f"`{field_rows_downstream_target_gate_protective_candidate_evaluation.get('candidate_target_count', 0)}`",
                "- candidate_action_count："
                f"`{len(candidate_actions)}`",
                "- can_emit_protective_control_candidate："
                f"`{field_rows_downstream_target_gate_protective_candidate_evaluation.get('can_emit_protective_control_candidate', False)}`",
                "- can_route_to_final_execution_review："
                f"`{field_rows_downstream_target_gate_protective_candidate_evaluation.get('can_route_to_final_execution_review', False)}`",
                "- next_operator_action："
                f"`{field_rows_downstream_target_gate_protective_candidate_evaluation.get('next_operator_action', '')}`",
                "- boundary：candidate evaluation emits only a protective action candidate bundle; final execution, actuator write and release validation remain separate blocked gates.",
            ]
        )
    lines.extend(
        [
            "",
            "## R8p Field Rows Collection Checklist",
            "",
            f"- status：`{field_rows_collection_checklist.get('field_rows_collection_checklist_status')}`",
            f"- checklist_path：`{field_rows_collection_checklist.get('checklist_path')}`",
            f"- required_scenario_count：`{field_rows_collection_checklist.get('required_scenario_count')}`",
            f"- required_table_count：`{field_rows_collection_checklist.get('required_table_count')}`",
            f"- minimum_real_batch_count：`{field_rows_collection_checklist.get('minimum_real_batch_count')}`",
            f"- highest_priority_patch_id：`{field_rows_collection_checklist.get('highest_priority_patch_id')}`",
            f"- technical_effect：{field_rows_collection_checklist.get('technical_feature_mapping', {}).get('technical_effect', '')}",
            "",
            "| Step | Required Evidence | Acceptance Check |",
            "| --- | --- | --- |",
        ]
    )
    for step in field_rows_collection_checklist.get("operator_acceptance_sequence", []) or []:
        if not isinstance(step, dict):
            continue
        lines.append(
            f"| `{step.get('step')}` | {step.get('required_evidence')} | {step.get('acceptance_check')} |"
        )
    lines.extend(
        [
            "",
            "## R8p Field Rows Patch Plan",
            "",
            f"- status：`{patch_plan['field_rows_patch_plan_status']}`",
            f"- next_operator_action：`{patch_plan['next_operator_action']}`",
            f"- highest_priority_patch_id：`{patch_plan['highest_priority_patch_id']}`",
            "",
            "| Patch | Priority | Type | Target | Operator Action | Acceptance Check |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in patch_plan["patch_items"]:
        lines.append(
            f"| `{item['patch_id']}` | `{item['priority']}` | `{item['patch_type']}` | "
            f"`{item['target']}` | {item['operator_action']} | {item['acceptance_check']} |"
        )
    lines.extend(
        [
            "",
            "## R8p Operator Handoff",
            "",
            f"- status：`{operator_handoff['field_rows_operator_handoff_status']}`",
            f"- working_directory：`{operator_handoff['working_directory']}`",
            f"- default_real_rows_path：`{operator_handoff['default_field_rows_path']}`",
            f"- configured_real_rows_path：`{operator_handoff['configured_field_rows_path']}`",
            f"- template_rows_path：`{operator_handoff['template_rows_path']}`",
            f"- csv_template_dir：`{operator_handoff['csv_template_dir']}`",
            f"- r7_to_r8p_alignment_path：`{operator_handoff['r7_to_r8p_alignment_path']}`",
            f"- rows_schema_path：`{operator_handoff['rows_schema_path']}`",
            f"- collection_checklist_path：`{operator_handoff['collection_checklist_path']}`",
            f"- batch_bundle_preflight_path：`{operator_handoff['field_rows_batch_bundle_preflight_path']}`",
            f"- temporal_window_preflight_path：`{operator_handoff['field_rows_temporal_window_preflight_path']}`",
            f"- scenario_semantic_preflight_path：`{operator_handoff['field_rows_scenario_semantic_preflight_path']}`",
            f"- downstream_routing_preflight_path：`{operator_handoff['field_rows_downstream_routing_preflight_path']}`",
            f"- schema_status：`{operator_handoff['field_rows_package_schema_status']}`",
            f"- schema_validation_status：`{operator_handoff['field_rows_schema_validation_status']}`",
            f"- collection_checklist_status：`{operator_handoff['field_rows_collection_checklist_status']}`",
            f"- batch_bundle_preflight_status：`{operator_handoff['field_rows_batch_bundle_preflight_status']}`",
            f"- temporal_window_preflight_status：`{operator_handoff['field_rows_temporal_window_preflight_status']}`",
            f"- scenario_semantic_preflight_status：`{operator_handoff['field_rows_scenario_semantic_preflight_status']}`",
            f"- downstream_routing_preflight_status：`{operator_handoff['field_rows_downstream_routing_preflight_status']}`",
            f"- schema_validation_summary：`{operator_handoff['schema_validation_summary']}`",
            f"- batch_bundle_preflight_summary：`{operator_handoff['batch_bundle_preflight_summary']}`",
            f"- temporal_window_preflight_summary：`{operator_handoff['temporal_window_preflight_summary']}`",
            f"- scenario_semantic_preflight_summary：`{operator_handoff['scenario_semantic_preflight_summary']}`",
            f"- downstream_routing_preflight_summary：`{operator_handoff['downstream_routing_preflight_summary']}`",
            f"- env_override：`{operator_handoff['env_override_name']}`",
            f"- validation_command_default：`{operator_handoff['validation_command_default']}`",
            f"- validation_command_with_env_override：`{operator_handoff['validation_command_with_env_override']}`",
            f"- schema_boundary：{operator_handoff['schema_boundary']}",
            f"- field_evidence_boundary：{operator_handoff['field_evidence_boundary']}",
            "",
            "| Milestone | Acceptance |",
            "| --- | --- |",
        ]
    )
    for milestone in operator_handoff["acceptance_milestones"]:
        lines.append(f"| `{milestone['milestone']}` | {milestone['acceptance']} |")
    lines.extend(
        [
            "",
            "### Template Rejection Rules",
            "",
        ]
    )
    for rule in operator_handoff["template_rejection_rules"]:
        lines.append(f"- {rule}")
    if field_rows_source_package_submission_route_guide:
        lines.extend(
            [
                "",
                "## Field Rows Source Package Route Guide",
                "",
                "- status："
                f"`{field_rows_source_package_submission_route_guide.get('source_package_submission_route_guide_status', '')}`",
                "- recommended_route："
                f"`{field_rows_source_package_submission_route_guide.get('recommended_route_id', '')}`",
                "- next_operator_action："
                f"`{field_rows_source_package_submission_route_guide.get('next_operator_action', '')}`",
                "- route_option_count："
                f"`{field_rows_source_package_submission_route_guide.get('route_option_count', 0)}`",
                "",
                "| Route | Kind | Submission Target |",
                "| --- | --- | --- |",
            ]
        )
        for option in field_rows_source_package_submission_route_guide.get("route_options", []):
            lines.append(
                f"| `{option['route_id']}` | `{option['route_kind']}` | "
                f"`{option['submission_target']}` |"
            )
    if field_rows_source_package_route_preflight:
        lines.extend(
            [
                "",
                "## Field Rows Source Package Route Preflight",
                "",
                "- status："
                f"`{field_rows_source_package_route_preflight.get('source_package_route_preflight_status', '')}`",
                "- recommended_route："
                f"`{field_rows_source_package_route_preflight.get('recommended_route_id', '')}`",
                "- recommended_route_preflight："
                f"`{field_rows_source_package_route_preflight.get('recommended_route_preflight_status', '')}`",
                "- next_operator_action："
                f"`{field_rows_source_package_route_preflight.get('next_operator_action', '')}`",
                "- ready/waiting/blocked："
                f"`{field_rows_source_package_route_preflight.get('ready_route_count', 0)}`/"
                f"`{field_rows_source_package_route_preflight.get('waiting_route_count', 0)}`/"
                f"`{field_rows_source_package_route_preflight.get('blocked_route_count', 0)}`",
                "",
                "| Route | Status | Next Action | Blockers |",
                "| --- | --- | --- | --- |",
            ]
        )
        for result in field_rows_source_package_route_preflight.get("route_preflight_results", []):
            if not isinstance(result, dict):
                continue
            lines.append(
                f"| `{result.get('route_id')}` | `{result.get('route_preflight_status')}` | "
                f"`{result.get('next_operator_action')}` | `{result.get('blockers', [])}` |"
            )
    lines.extend(["", "## Template Row Summary", ""])
    lines.append(
        "Template rows are TODO scaffolds only; they must not be imported as field evidence or used for actuator/release-gate decisions."
    )
    lines.append(f"- template_file：`{TEMPLATE_ROWS_PATH}`")
    for table, rows in report.metrics["template_rows_by_table"].items():
        lines.append(f"- `{table}`：{len(rows)} template rows")
    lines.extend(["", "## 边界", ""])
    for issue in report.issues:
        lines.append(f"- `{issue.issue_type}`：{issue.message}")
    return "\n".join(lines)


def _report_md(
    report,
    generated_files: dict[str, str],
    field_rows_source: dict[str, object],
    field_rows_schema_validation: dict[str, object] | None = None,
    field_rows_collection_checklist: dict[str, object] | None = None,
    field_rows_batch_bundle_preflight: dict[str, object] | None = None,
    field_rows_temporal_window_preflight: dict[str, object] | None = None,
    field_rows_scenario_semantic_preflight: dict[str, object] | None = None,
    field_rows_downstream_routing_preflight: dict[str, object] | None = None,
    field_rows_downstream_route_handoff: dict[str, object] | None = None,
    field_rows_downstream_target_gate_preflight: dict[str, object] | None = None,
    field_rows_downstream_target_gate_result_intake_schema: dict[str, object] | None = None,
    field_rows_downstream_target_gate_result_preflight: dict[str, object] | None = None,
    field_rows_downstream_target_gate_result_arbitration: dict[str, object] | None = None,
    field_rows_downstream_target_gate_operator_review_template: dict[str, object] | None = None,
    field_rows_downstream_target_gate_operator_review_preflight: dict[str, object] | None = None,
    field_rows_downstream_target_gate_post_review_gate: dict[str, object] | None = None,
    field_rows_downstream_target_gate_protective_candidate_evaluation: dict[str, object] | None = None,
    field_rows_r7_staging_preflight: dict[str, object] | None = None,
    field_rows_r7_completion_plan: dict[str, object] | None = None,
    field_rows_r7_completion_route_contracts: dict[str, object] | None = None,
    field_rows_r7_completion_route_work_packages: dict[str, object] | None = None,
    field_rows_r7_completion_route_work_package_templates: dict[str, object] | None = None,
    field_rows_r7_completion_route_work_package_preflight: dict[str, object] | None = None,
    field_rows_r7_completion_route_work_package_patch_plan: dict[str, object] | None = None,
    field_rows_r7_completion_route_work_package_assembly_gate: dict[str, object] | None = None,
    field_rows_submission_readiness_review: dict[str, object] | None = None,
    field_rows_source_package_submission_route_guide: dict[str, object] | None = None,
    field_rows_source_package_route_preflight: dict[str, object] | None = None,
) -> str:
    readiness = report.metrics["readiness"]
    row_readiness = report.metrics["row_collection_readiness"]
    field_acceptance = report.metrics["field_row_acceptance"]
    field_rows_package_schema = _field_rows_package_schema()
    field_rows_schema_validation = field_rows_schema_validation or {}
    field_rows_batch_bundle_preflight = field_rows_batch_bundle_preflight or {}
    field_rows_temporal_window_preflight = field_rows_temporal_window_preflight or {}
    field_rows_scenario_semantic_preflight = field_rows_scenario_semantic_preflight or {}
    field_rows_downstream_routing_preflight = field_rows_downstream_routing_preflight or {}
    field_rows_downstream_route_handoff = field_rows_downstream_route_handoff or {}
    field_rows_downstream_target_gate_preflight = field_rows_downstream_target_gate_preflight or {}
    field_rows_downstream_target_gate_result_intake_schema = (
        field_rows_downstream_target_gate_result_intake_schema or {}
    )
    field_rows_downstream_target_gate_result_preflight = (
        field_rows_downstream_target_gate_result_preflight or {}
    )
    field_rows_downstream_target_gate_result_arbitration = (
        field_rows_downstream_target_gate_result_arbitration or {}
    )
    field_rows_downstream_target_gate_operator_review_template = (
        field_rows_downstream_target_gate_operator_review_template or {}
    )
    field_rows_downstream_target_gate_operator_review_preflight = (
        field_rows_downstream_target_gate_operator_review_preflight or {}
    )
    field_rows_downstream_target_gate_post_review_gate = (
        field_rows_downstream_target_gate_post_review_gate or {}
    )
    field_rows_downstream_target_gate_protective_candidate_evaluation = (
        field_rows_downstream_target_gate_protective_candidate_evaluation or {}
    )
    field_rows_r7_staging_preflight = field_rows_r7_staging_preflight or {}
    field_rows_r7_completion_plan = field_rows_r7_completion_plan or {}
    field_rows_r7_completion_route_contracts = field_rows_r7_completion_route_contracts or {}
    field_rows_r7_completion_route_work_packages = field_rows_r7_completion_route_work_packages or {}
    field_rows_r7_completion_route_work_package_templates = (
        field_rows_r7_completion_route_work_package_templates or {}
    )
    field_rows_r7_completion_route_work_package_preflight = (
        field_rows_r7_completion_route_work_package_preflight or {}
    )
    field_rows_r7_completion_route_work_package_patch_plan = (
        field_rows_r7_completion_route_work_package_patch_plan or {}
    )
    field_rows_r7_completion_route_work_package_assembly_gate = (
        field_rows_r7_completion_route_work_package_assembly_gate or {}
    )
    field_rows_submission_readiness_review = field_rows_submission_readiness_review or {}
    field_rows_source_package_submission_route_guide = field_rows_source_package_submission_route_guide or {}
    field_rows_source_package_route_preflight = field_rows_source_package_route_preflight or {}
    patch_plan = _field_rows_patch_plan(
        report,
        field_rows_source,
        field_rows_schema_validation,
        field_rows_batch_bundle_preflight,
        field_rows_temporal_window_preflight,
        field_rows_scenario_semantic_preflight,
    )
    field_rows_collection_checklist = field_rows_collection_checklist or _field_rows_collection_checklist(
        report,
        field_rows_source,
        patch_plan,
        field_rows_package_schema,
        field_rows_schema_validation,
        field_rows_batch_bundle_preflight,
        field_rows_temporal_window_preflight,
        field_rows_scenario_semantic_preflight,
    )
    operator_handoff = _field_rows_operator_handoff(
        report,
        field_rows_source,
        patch_plan,
        field_rows_package_schema,
        field_rows_schema_validation,
        field_rows_collection_checklist,
        field_rows_batch_bundle_preflight,
        field_rows_temporal_window_preflight,
        field_rows_scenario_semantic_preflight,
        field_rows_downstream_routing_preflight,
    )
    lines = [
        "# Agent61 Pressure Resolution Replay Scenario Pack 报告",
        "",
        f"- summary: {report.summary}",
        f"- scenario_pack_status: `{readiness['scenario_pack_status']}`",
        f"- field_scenario_coverage: `{readiness['field_scenario_coverage']}`",
        f"- missing_field_scenarios: `{readiness['missing_field_scenarios']}`",
        f"- row_collection_plan_status: `{row_readiness['row_collection_plan_status']}`",
        f"- missing_scenario_count: `{row_readiness['missing_scenario_count']}`",
        f"- template_row_count: `{row_readiness['template_row_count']}`",
        f"- field_row_acceptance_status: `{field_acceptance['field_row_acceptance_status']}`",
        f"- accepted_field_scenario_count: `{field_acceptance['accepted_scenario_count']}`",
        f"- accepted_field_batch_count: `{field_acceptance['accepted_batch_count']}`",
        f"- field_rows_source_status: `{field_rows_source['field_rows_source_status']}`",
        f"- field_rows_patch_plan_status: `{patch_plan['field_rows_patch_plan_status']}`",
        f"- field_rows_patch_item_count: `{patch_plan['patch_item_count']}`",
        f"- field_rows_operator_handoff_status: `{operator_handoff['field_rows_operator_handoff_status']}`",
        f"- field_rows_package_schema_status: `{operator_handoff['field_rows_package_schema_status']}`",
        f"- field_rows_schema_validation_status: `{operator_handoff['field_rows_schema_validation_status']}`",
        f"- field_rows_collection_checklist_status: `{operator_handoff['field_rows_collection_checklist_status']}`",
        f"- field_rows_batch_bundle_preflight_status: `{operator_handoff['field_rows_batch_bundle_preflight_status']}`",
        f"- schema_required_field_gap_count: `{field_rows_schema_validation.get('required_field_gap_count', 0)}`",
        f"- schema_invalid_type_count: `{field_rows_schema_validation.get('invalid_type_count', 0)}`",
        f"- schema_template_marker_gap_count: `{field_rows_schema_validation.get('template_marker_gap_count', 0)}`",
        f"- schema_field_origin_gap_count: `{field_rows_schema_validation.get('field_origin_gap_count', 0)}`",
        f"- complete_batch_bundle_count: `{field_rows_batch_bundle_preflight.get('complete_bundle_count', 0)}`",
        f"- partial_batch_bundle_count: `{field_rows_batch_bundle_preflight.get('partial_bundle_count', 0)}`",
        f"- missing_bundle_table_count: `{field_rows_batch_bundle_preflight.get('missing_bundle_table_count', 0)}`",
        f"- field_rows_temporal_window_preflight_status: `{operator_handoff['field_rows_temporal_window_preflight_status']}`",
        f"- temporal_valid_batch_count: `{field_rows_temporal_window_preflight.get('temporal_valid_batch_count', 0)}`",
        f"- temporal_violation_count: `{field_rows_temporal_window_preflight.get('temporal_violation_count', 0)}`",
        f"- hold_time_violation_count: `{field_rows_temporal_window_preflight.get('hold_time_violation_count', 0)}`",
        f"- field_rows_scenario_semantic_preflight_status: `{operator_handoff['field_rows_scenario_semantic_preflight_status']}`",
        f"- semantic_valid_batch_count: `{field_rows_scenario_semantic_preflight.get('semantic_valid_batch_count', 0)}`",
        f"- semantic_violation_count: `{field_rows_scenario_semantic_preflight.get('semantic_violation_count', 0)}`",
        f"- field_rows_downstream_routing_preflight_status: `{operator_handoff['field_rows_downstream_routing_preflight_status']}`",
        f"- routing_ready_target_count: `{field_rows_downstream_routing_preflight.get('routing_ready_target_count', 0)}`",
        f"- can_route_to_r8v: `{field_rows_downstream_routing_preflight.get('can_route_to_r8v', False)}`",
        f"- field_rows_downstream_route_handoff_status: `{field_rows_downstream_route_handoff.get('downstream_route_handoff_status', 'not_run')}`",
        f"- downstream_handoff_ready_target_count: `{field_rows_downstream_route_handoff.get('ready_handoff_target_count', 0)}`",
        f"- downstream_handoff_blocked_target_count: `{field_rows_downstream_route_handoff.get('blocked_handoff_target_count', 0)}`",
        f"- field_rows_downstream_target_gate_preflight_status: `{field_rows_downstream_target_gate_preflight.get('downstream_target_gate_preflight_status', 'not_run')}`",
        f"- downstream_target_gate_ready_count: `{field_rows_downstream_target_gate_preflight.get('ready_target_gate_count', 0)}`",
        f"- downstream_target_gate_blocked_count: `{field_rows_downstream_target_gate_preflight.get('blocked_target_gate_count', 0)}`",
        f"- field_rows_downstream_target_gate_result_preflight_status: `{field_rows_downstream_target_gate_result_preflight.get('downstream_target_gate_result_preflight_status', 'not_run')}`",
        f"- downstream_target_gate_result_accepted_count: `{field_rows_downstream_target_gate_result_preflight.get('accepted_target_result_count', 0)}`",
        f"- downstream_target_gate_result_rejected_count: `{field_rows_downstream_target_gate_result_preflight.get('rejected_target_result_count', 0)}`",
        f"- field_rows_downstream_target_gate_result_arbitration_status: `{field_rows_downstream_target_gate_result_arbitration.get('downstream_target_gate_result_arbitration_status', 'not_run')}`",
        f"- downstream_target_gate_result_arbitration_next_action: `{field_rows_downstream_target_gate_result_arbitration.get('next_operator_action', '')}`",
        f"- field_rows_downstream_target_gate_operator_review_preflight_status: `{field_rows_downstream_target_gate_operator_review_preflight.get('downstream_target_gate_operator_review_preflight_status', 'not_run')}`",
        f"- downstream_target_gate_operator_review_approved_count: `{field_rows_downstream_target_gate_operator_review_preflight.get('approved_operator_review_count', 0)}`",
        f"- downstream_target_gate_operator_review_hold_count: `{field_rows_downstream_target_gate_operator_review_preflight.get('hold_operator_review_count', 0)}`",
        f"- downstream_target_gate_operator_review_next_action: `{field_rows_downstream_target_gate_operator_review_preflight.get('next_operator_action', '')}`",
        f"- field_rows_downstream_target_gate_post_review_gate_status: `{field_rows_downstream_target_gate_post_review_gate.get('downstream_target_gate_post_review_gate_status', 'not_run')}`",
        f"- downstream_target_gate_post_review_can_route_to_protective_candidate: `{field_rows_downstream_target_gate_post_review_gate.get('can_route_to_protective_candidate_evaluation', False)}`",
        f"- downstream_target_gate_post_review_can_emit_protective_candidate: `{field_rows_downstream_target_gate_post_review_gate.get('can_emit_protective_control_candidate', False)}`",
        f"- downstream_target_gate_post_review_next_action: `{field_rows_downstream_target_gate_post_review_gate.get('next_operator_action', '')}`",
        f"- field_rows_downstream_target_gate_protective_candidate_evaluation_status: `{field_rows_downstream_target_gate_protective_candidate_evaluation.get('downstream_target_gate_protective_candidate_evaluation_status', 'not_run')}`",
        f"- downstream_target_gate_protective_candidate_can_emit: `{field_rows_downstream_target_gate_protective_candidate_evaluation.get('can_emit_protective_control_candidate', False)}`",
        f"- downstream_target_gate_protective_candidate_can_route_to_final_execution_review: `{field_rows_downstream_target_gate_protective_candidate_evaluation.get('can_route_to_final_execution_review', False)}`",
        f"- downstream_target_gate_protective_candidate_next_action: `{field_rows_downstream_target_gate_protective_candidate_evaluation.get('next_operator_action', '')}`",
        f"- r7_to_r8p_staging_status: `{field_rows_r7_staging_preflight.get('r7_staging_preflight_status', 'not_run')}`",
        f"- r7_staged_row_count: `{field_rows_r7_staging_preflight.get('staged_row_count', 0)}`",
        f"- r7_staging_required_field_gap_count: `{field_rows_r7_staging_preflight.get('required_field_gap_count', 0)}`",
        f"- r7_staging_supplement_gap_count: `{field_rows_r7_staging_preflight.get('supplement_required_field_gap_count', 0)}`",
        f"- r7_staging_agent52_export_gap_count: `{field_rows_r7_staging_preflight.get('agent52_export_required_field_gap_count', 0)}`",
        f"- r7_to_r8p_completion_plan_status: `{field_rows_r7_completion_plan.get('completion_plan_status', 'not_run')}`",
        f"- r7_to_r8p_completion_item_count: `{field_rows_r7_completion_plan.get('item_count', 0)}`",
        f"- r7_completion_route_contracts_status: `{field_rows_r7_completion_route_contracts.get('completion_route_contracts_status', 'not_run')}`",
        f"- r7_completion_open_route_count: `{field_rows_r7_completion_route_contracts.get('open_route_count', 0)}`",
        f"- r7_completion_route_work_packages_status: `{field_rows_r7_completion_route_work_packages.get('route_work_packages_status', 'not_run')}`",
        f"- r7_completion_open_work_package_count: `{field_rows_r7_completion_route_work_packages.get('open_work_package_count', 0)}`",
        f"- r7_completion_route_work_package_templates_status: `{field_rows_r7_completion_route_work_package_templates.get('route_work_package_templates_status', 'not_run')}`",
        f"- r7_completion_route_work_package_preflight_status: `{field_rows_r7_completion_route_work_package_preflight.get('route_work_package_preflight_status', 'not_run')}`",
        f"- r7_completion_blocked_work_package_count: `{field_rows_r7_completion_route_work_package_preflight.get('blocked_work_package_count', 0)}`",
        f"- r7_completion_route_work_package_patch_plan_status: `{field_rows_r7_completion_route_work_package_patch_plan.get('route_work_package_patch_plan_status', 'not_run')}`",
        f"- r7_completion_route_work_package_patch_item_count: `{field_rows_r7_completion_route_work_package_patch_plan.get('patch_item_count', 0)}`",
        f"- r7_completion_route_work_package_highest_priority_patch_id: `{field_rows_r7_completion_route_work_package_patch_plan.get('highest_priority_patch_id', '')}`",
        f"- r7_completion_route_work_package_assembly_gate_status: `{field_rows_r7_completion_route_work_package_assembly_gate.get('route_work_package_assembly_gate_status', 'not_run')}`",
        f"- r7_completion_route_work_package_blocked_assembly_step_count: `{field_rows_r7_completion_route_work_package_assembly_gate.get('blocked_assembly_step_count', 0)}`",
        f"- field_rows_submission_readiness_review_status: `{field_rows_submission_readiness_review.get('submission_readiness_review_status', 'not_run')}`",
        f"- field_rows_submission_readiness_next_action: `{field_rows_submission_readiness_review.get('next_operator_action', '')}`",
        f"- field_rows_submission_readiness_can_route_to_r8v: `{field_rows_submission_readiness_review.get('can_route_to_r8v', False)}`",
        f"- field_rows_source_package_route_guide_status: `{field_rows_source_package_submission_route_guide.get('source_package_submission_route_guide_status', 'not_run')}`",
        f"- field_rows_source_package_recommended_route: `{field_rows_source_package_submission_route_guide.get('recommended_route_id', '')}`",
        f"- field_rows_source_package_route_option_count: `{field_rows_source_package_submission_route_guide.get('route_option_count', 0)}`",
        f"- field_rows_source_package_route_preflight_status: `{field_rows_source_package_route_preflight.get('source_package_route_preflight_status', 'not_run')}`",
        f"- field_rows_source_package_recommended_route_preflight: `{field_rows_source_package_route_preflight.get('recommended_route_preflight_status', '')}`",
        f"- field_rows_source_package_ready_route_count: `{field_rows_source_package_route_preflight.get('ready_route_count', 0)}`",
        f"- field_rows_source_path: `{field_rows_source['field_rows_source_path']}`",
        f"- real_rows_template_path: `{TEMPLATE_ROWS_PATH}`",
        f"- r7_staging_preflight_path: `{ROWS_R7_STAGING_PREFLIGHT_PATH}`",
        f"- r7_staged_draft_path: `{ROWS_R7_STAGED_DRAFT_PATH}`",
        f"- r7_completion_plan_path: `{ROWS_R7_COMPLETION_PLAN_PATH}`",
        f"- r7_completion_route_contracts_path: `{ROWS_R7_COMPLETION_ROUTE_CONTRACTS_PATH}`",
        f"- r7_completion_route_work_packages_path: `{ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGES_PATH}`",
        f"- r7_completion_route_work_package_template_dir: `{ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_TEMPLATE_DIR}`",
        f"- r7_completion_route_work_package_preflight_path: `{ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_PREFLIGHT_PATH}`",
        f"- r7_completion_route_work_package_patch_plan_path: `{ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_PATCH_PLAN_PATH}`",
        f"- r7_completion_route_work_package_assembly_gate_path: `{ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_ASSEMBLY_GATE_PATH}`",
        f"- real_rows_schema_path: `{ROWS_SCHEMA_PATH}`",
        f"- batch_bundle_preflight_path: `{ROWS_BATCH_BUNDLE_PREFLIGHT_PATH}`",
        f"- temporal_window_preflight_path: `{ROWS_TEMPORAL_WINDOW_PREFLIGHT_PATH}`",
        f"- scenario_semantic_preflight_path: `{ROWS_SCENARIO_SEMANTIC_PREFLIGHT_PATH}`",
        f"- downstream_routing_preflight_path: `{ROWS_DOWNSTREAM_ROUTING_PREFLIGHT_PATH}`",
        f"- downstream_route_handoff_path: `{ROWS_DOWNSTREAM_ROUTE_HANDOFF_PATH}`",
        f"- downstream_target_gate_preflight_path: `{ROWS_DOWNSTREAM_TARGET_GATE_PREFLIGHT_PATH}`",
        f"- downstream_target_gate_result_intake_schema_path: `{ROWS_DOWNSTREAM_TARGET_GATE_RESULT_INTAKE_SCHEMA_PATH}`",
        f"- downstream_target_gate_result_preflight_path: `{ROWS_DOWNSTREAM_TARGET_GATE_RESULT_PREFLIGHT_PATH}`",
        f"- downstream_target_gate_result_arbitration_path: `{ROWS_DOWNSTREAM_TARGET_GATE_RESULT_ARBITRATION_PATH}`",
        f"- downstream_target_gate_operator_review_template_path: `{ROWS_DOWNSTREAM_TARGET_GATE_OPERATOR_REVIEW_TEMPLATE_PATH}`",
        f"- downstream_target_gate_operator_review_preflight_path: `{ROWS_DOWNSTREAM_TARGET_GATE_OPERATOR_REVIEW_PREFLIGHT_PATH}`",
        f"- downstream_target_gate_post_review_gate_path: `{ROWS_DOWNSTREAM_TARGET_GATE_POST_REVIEW_GATE_PATH}`",
        f"- downstream_target_gate_protective_candidate_evaluation_path: `{ROWS_DOWNSTREAM_TARGET_GATE_PROTECTIVE_CANDIDATE_EVALUATION_PATH}`",
        "",
        "## 生成文件",
        "",
    ]
    for key, path in generated_files.items():
        lines.append(f"- {key}: `{path}`")
    lines.extend(["", "## 建议", ""])
    for recommendation in report.recommendations:
        lines.append(f"- {recommendation}")
    lines.extend(["", "## R8p 补包计划", ""])
    lines.append(f"- status: `{patch_plan['field_rows_patch_plan_status']}`")
    lines.append(f"- next_operator_action: `{patch_plan['next_operator_action']}`")
    lines.append(f"- highest_priority_patch_id: `{patch_plan['highest_priority_patch_id']}`")
    for item in patch_plan["patch_items"][:8]:
        lines.append(f"- `{item['patch_id']}`：{item['operator_action']}")
    lines.extend(
        [
            "",
            "## R8p schema 验证摘要",
            "",
            f"- status: `{field_rows_schema_validation.get('field_rows_schema_validation_status', 'schema_validation_not_run')}`",
            f"- required_field_gap_count: `{field_rows_schema_validation.get('required_field_gap_count', 0)}`",
            f"- invalid_type_count: `{field_rows_schema_validation.get('invalid_type_count', 0)}`",
            f"- template_marker_gap_count: `{field_rows_schema_validation.get('template_marker_gap_count', 0)}`",
            f"- field_origin_gap_count: `{field_rows_schema_validation.get('field_origin_gap_count', 0)}`",
            f"- missing_table_count: `{field_rows_schema_validation.get('missing_table_count', 0)}`",
            f"- empty_table_count: `{field_rows_schema_validation.get('empty_table_count', 0)}`",
            f"- unknown_table_count: `{field_rows_schema_validation.get('unknown_table_count', 0)}`",
            f"- boundary: {field_rows_schema_validation.get('schema_validation_boundary', '')}",
        ]
    )
    lines.extend(
        [
            "",
            "## R8p same-batch bundle 预检摘要",
            "",
            f"- status: `{field_rows_batch_bundle_preflight.get('field_rows_batch_bundle_preflight_status', 'batch_bundle_preflight_not_run')}`",
            f"- candidate_batch_count: `{field_rows_batch_bundle_preflight.get('candidate_batch_count', 0)}`",
            f"- complete_bundle_count: `{field_rows_batch_bundle_preflight.get('complete_bundle_count', 0)}`",
            f"- partial_bundle_count: `{field_rows_batch_bundle_preflight.get('partial_bundle_count', 0)}`",
            f"- missing_bundle_table_count: `{field_rows_batch_bundle_preflight.get('missing_bundle_table_count', 0)}`",
            f"- scenario_bundle_ready_count: `{field_rows_batch_bundle_preflight.get('scenario_bundle_ready_count', 0)}`",
            f"- boundary: {field_rows_batch_bundle_preflight.get('batch_bundle_boundary', '')}",
        ]
    )
    lines.extend(
        [
            "",
            "## R8p temporal-window 预检摘要",
            "",
            f"- status: `{field_rows_temporal_window_preflight.get('field_rows_temporal_window_preflight_status', 'temporal_window_preflight_not_run')}`",
            f"- checked_batch_count: `{field_rows_temporal_window_preflight.get('checked_batch_count', 0)}`",
            f"- temporal_valid_batch_count: `{field_rows_temporal_window_preflight.get('temporal_valid_batch_count', 0)}`",
            f"- temporal_violation_count: `{field_rows_temporal_window_preflight.get('temporal_violation_count', 0)}`",
            f"- hold_time_violation_count: `{field_rows_temporal_window_preflight.get('hold_time_violation_count', 0)}`",
            f"- scenario_temporal_ready_count: `{field_rows_temporal_window_preflight.get('scenario_temporal_ready_count', 0)}`",
            f"- boundary: {field_rows_temporal_window_preflight.get('temporal_window_boundary', '')}",
        ]
    )
    lines.extend(
        [
            "",
            "## R8p scenario-semantic 预检摘要",
            "",
            f"- status: `{field_rows_scenario_semantic_preflight.get('field_rows_scenario_semantic_preflight_status', 'scenario_semantic_preflight_not_run')}`",
            f"- checked_batch_count: `{field_rows_scenario_semantic_preflight.get('checked_batch_count', 0)}`",
            f"- semantic_valid_batch_count: `{field_rows_scenario_semantic_preflight.get('semantic_valid_batch_count', 0)}`",
            f"- semantic_violation_count: `{field_rows_scenario_semantic_preflight.get('semantic_violation_count', 0)}`",
            f"- scenario_semantic_ready_count: `{field_rows_scenario_semantic_preflight.get('scenario_semantic_ready_count', 0)}`",
            f"- condition_violation_counts: `{field_rows_scenario_semantic_preflight.get('condition_violation_counts', {})}`",
            f"- boundary: {field_rows_scenario_semantic_preflight.get('scenario_semantic_boundary', '')}",
        ]
    )
    lines.extend(
        [
            "",
            "## R8v downstream-routing 预检摘要",
            "",
            f"- status: `{field_rows_downstream_routing_preflight.get('field_rows_downstream_routing_preflight_status', 'downstream_routing_preflight_not_run')}`",
            f"- accepted_batch_count: `{field_rows_downstream_routing_preflight.get('accepted_batch_count', 0)}`",
            f"- routing_target_count: `{field_rows_downstream_routing_preflight.get('routing_target_count', 0)}`",
            f"- routing_ready_target_count: `{field_rows_downstream_routing_preflight.get('routing_ready_target_count', 0)}`",
            f"- can_route_to_r8v: `{field_rows_downstream_routing_preflight.get('can_route_to_r8v', False)}`",
            f"- boundary: {field_rows_downstream_routing_preflight.get('downstream_routing_boundary', '')}",
        ]
    )
    lines.extend(
        [
            "",
            "## R8v downstream-target-gate 预检摘要",
            "",
            f"- status: `{field_rows_downstream_target_gate_preflight.get('downstream_target_gate_preflight_status', 'downstream_target_gate_preflight_not_run')}`",
            f"- target_gate_count: `{field_rows_downstream_target_gate_preflight.get('target_gate_count', 0)}`",
            f"- ready_target_gate_count: `{field_rows_downstream_target_gate_preflight.get('ready_target_gate_count', 0)}`",
            f"- blocked_target_gate_count: `{field_rows_downstream_target_gate_preflight.get('blocked_target_gate_count', 0)}`",
            f"- can_execute_all_target_gates: `{field_rows_downstream_target_gate_preflight.get('can_execute_all_target_gates', False)}`",
            f"- next_operator_action: `{field_rows_downstream_target_gate_preflight.get('next_operator_action', '')}`",
            "- boundary: target gate preflight is only an executable contract board; downstream gates must still run and pass their own evidence boundaries.",
        ]
    )
    lines.extend(
        [
            "",
            "## R8v downstream-target-gate result intake 摘要",
            "",
            f"- schema_expected_target_count: `{field_rows_downstream_target_gate_result_intake_schema.get('expected_target_count', 0)}`",
            f"- status: `{field_rows_downstream_target_gate_result_preflight.get('downstream_target_gate_result_preflight_status', 'downstream_target_gate_result_preflight_not_run')}`",
            f"- submitted_target_result_count: `{field_rows_downstream_target_gate_result_preflight.get('submitted_target_result_count', 0)}`",
            f"- accepted_target_result_count: `{field_rows_downstream_target_gate_result_preflight.get('accepted_target_result_count', 0)}`",
            f"- rejected_target_result_count: `{field_rows_downstream_target_gate_result_preflight.get('rejected_target_result_count', 0)}`",
            f"- missing_target_ids: `{field_rows_downstream_target_gate_result_preflight.get('missing_target_ids', [])}`",
            f"- next_operator_action: `{field_rows_downstream_target_gate_result_preflight.get('next_operator_action', '')}`",
            "- boundary: result intake validates target-gate result package shape and metrics only; downstream arbitration/review must still pass before any control write.",
        ]
    )
    lines.extend(
        [
            "",
            "## R8v downstream-target-gate result arbitration 摘要",
            "",
            f"- status: `{field_rows_downstream_target_gate_result_arbitration.get('downstream_target_gate_result_arbitration_status', 'downstream_target_gate_result_arbitration_not_run')}`",
            f"- accepted_target_result_count: `{field_rows_downstream_target_gate_result_arbitration.get('accepted_target_result_count', 0)}`",
            f"- target_gate_status_counts: `{field_rows_downstream_target_gate_result_arbitration.get('target_gate_status_counts', {})}`",
            f"- can_route_to_operator_review: `{field_rows_downstream_target_gate_result_arbitration.get('can_route_to_operator_review', False)}`",
            f"- can_emit_protective_control_candidate: `{field_rows_downstream_target_gate_result_arbitration.get('can_emit_protective_control_candidate', False)}`",
            f"- next_operator_action: `{field_rows_downstream_target_gate_result_arbitration.get('next_operator_action', '')}`",
            "- boundary: arbitration is still not actuator or release-gate permission; operator review and later gates remain required.",
        ]
    )
    lines.extend(
        [
            "",
            "## R8v downstream-target-gate operator-review preflight 摘要",
            "",
            f"- template_expected_target_count: `{field_rows_downstream_target_gate_operator_review_template.get('expected_target_count', 0)}`",
            f"- status: `{field_rows_downstream_target_gate_operator_review_preflight.get('downstream_target_gate_operator_review_preflight_status', 'downstream_target_gate_operator_review_preflight_not_run')}`",
            f"- submitted_operator_review_count: `{field_rows_downstream_target_gate_operator_review_preflight.get('submitted_operator_review_count', 0)}`",
            f"- approved_operator_review_count: `{field_rows_downstream_target_gate_operator_review_preflight.get('approved_operator_review_count', 0)}`",
            f"- rejected_operator_review_count: `{field_rows_downstream_target_gate_operator_review_preflight.get('rejected_operator_review_count', 0)}`",
            f"- hold_operator_review_count: `{field_rows_downstream_target_gate_operator_review_preflight.get('hold_operator_review_count', 0)}`",
            f"- can_route_to_post_review_gate: `{field_rows_downstream_target_gate_operator_review_preflight.get('can_route_to_post_review_gate', False)}`",
            f"- can_emit_protective_control_candidate: `{field_rows_downstream_target_gate_operator_review_preflight.get('can_emit_protective_control_candidate', False)}`",
            f"- next_operator_action: `{field_rows_downstream_target_gate_operator_review_preflight.get('next_operator_action', '')}`",
            "- boundary: operator review is a machine-preflighted human response gate only; post-review, actuator, release, and field-claim gates remain blocked until later validation.",
        ]
    )
    lines.extend(
        [
            "",
            "## R8v downstream-target-gate post-review gate 摘要",
            "",
            f"- status: `{field_rows_downstream_target_gate_post_review_gate.get('downstream_target_gate_post_review_gate_status', 'downstream_target_gate_post_review_gate_not_run')}`",
            f"- approved_operator_review_count: `{field_rows_downstream_target_gate_post_review_gate.get('approved_operator_review_count', 0)}`",
            f"- candidate_target_count: `{len(field_rows_downstream_target_gate_post_review_gate.get('post_review_candidate_targets', []) or [])}`",
            f"- can_route_to_protective_candidate_evaluation: `{field_rows_downstream_target_gate_post_review_gate.get('can_route_to_protective_candidate_evaluation', False)}`",
            f"- can_emit_protective_control_candidate: `{field_rows_downstream_target_gate_post_review_gate.get('can_emit_protective_control_candidate', False)}`",
            f"- next_operator_action: `{field_rows_downstream_target_gate_post_review_gate.get('next_operator_action', '')}`",
            "- boundary: post-review gate only emits a protective-control candidate for later policy/interlock review; actuator writes, release-gate writes and field-claim upgrades remain blocked.",
        ]
    )
    candidate_bundle = field_rows_downstream_target_gate_protective_candidate_evaluation.get(
        "candidate_action_bundle",
        {},
    )
    candidate_actions = candidate_bundle.get("candidate_actions", []) if isinstance(candidate_bundle, dict) else []
    lines.extend(
        [
            "",
            "## R8v protective-control candidate evaluation 摘要",
            "",
            f"- status: `{field_rows_downstream_target_gate_protective_candidate_evaluation.get('downstream_target_gate_protective_candidate_evaluation_status', 'protective_candidate_evaluation_not_run')}`",
            f"- candidate_target_count: `{field_rows_downstream_target_gate_protective_candidate_evaluation.get('candidate_target_count', 0)}`",
            f"- candidate_action_count: `{len(candidate_actions)}`",
            f"- can_emit_protective_control_candidate: `{field_rows_downstream_target_gate_protective_candidate_evaluation.get('can_emit_protective_control_candidate', False)}`",
            f"- can_route_to_final_execution_review: `{field_rows_downstream_target_gate_protective_candidate_evaluation.get('can_route_to_final_execution_review', False)}`",
            f"- next_operator_action: `{field_rows_downstream_target_gate_protective_candidate_evaluation.get('next_operator_action', '')}`",
            "- boundary: protective candidate evaluation is not online actuation; final execution review, actuator interlock, actuator feedback, and separate release validation remain required.",
        ]
    )
    lines.extend(
        [
            "",
            "## R8p 采集清单摘要",
            "",
            f"- status: `{field_rows_collection_checklist.get('field_rows_collection_checklist_status')}`",
            f"- checklist_path: `{field_rows_collection_checklist.get('checklist_path')}`",
            f"- required_scenario_count: `{field_rows_collection_checklist.get('required_scenario_count')}`",
            f"- required_table_count: `{field_rows_collection_checklist.get('required_table_count')}`",
            f"- minimum_real_batch_count: `{field_rows_collection_checklist.get('minimum_real_batch_count')}`",
            f"- highest_priority_patch_id: `{field_rows_collection_checklist.get('highest_priority_patch_id')}`",
        ]
    )
    lines.extend(
        [
            "",
            "## R8p 现场行包操作交接",
            "",
            f"- status: `{operator_handoff['field_rows_operator_handoff_status']}`",
            f"- working_directory: `{operator_handoff['working_directory']}`",
            f"- default_real_rows_path: `{operator_handoff['default_field_rows_path']}`",
            f"- template_rows_path: `{operator_handoff['template_rows_path']}`",
            f"- csv_template_dir: `{operator_handoff['csv_template_dir']}`",
            f"- r7_to_r8p_alignment_path: `{operator_handoff['r7_to_r8p_alignment_path']}`",
            f"- rows_schema_path: `{operator_handoff['rows_schema_path']}`",
            f"- collection_checklist_path: `{operator_handoff['collection_checklist_path']}`",
            f"- batch_bundle_preflight_path: `{operator_handoff['field_rows_batch_bundle_preflight_path']}`",
            f"- temporal_window_preflight_path: `{operator_handoff['field_rows_temporal_window_preflight_path']}`",
            f"- scenario_semantic_preflight_path: `{operator_handoff['field_rows_scenario_semantic_preflight_path']}`",
            f"- downstream_routing_preflight_path: `{operator_handoff['field_rows_downstream_routing_preflight_path']}`",
            f"- schema_status: `{operator_handoff['field_rows_package_schema_status']}`",
            f"- schema_validation_status: `{operator_handoff['field_rows_schema_validation_status']}`",
            f"- collection_checklist_status: `{operator_handoff['field_rows_collection_checklist_status']}`",
            f"- batch_bundle_preflight_status: `{operator_handoff['field_rows_batch_bundle_preflight_status']}`",
            f"- temporal_window_preflight_status: `{operator_handoff['field_rows_temporal_window_preflight_status']}`",
            f"- scenario_semantic_preflight_status: `{operator_handoff['field_rows_scenario_semantic_preflight_status']}`",
            f"- downstream_routing_preflight_status: `{operator_handoff['field_rows_downstream_routing_preflight_status']}`",
            f"- schema_validation_summary: `{operator_handoff['schema_validation_summary']}`",
            f"- batch_bundle_preflight_summary: `{operator_handoff['batch_bundle_preflight_summary']}`",
            f"- temporal_window_preflight_summary: `{operator_handoff['temporal_window_preflight_summary']}`",
            f"- scenario_semantic_preflight_summary: `{operator_handoff['scenario_semantic_preflight_summary']}`",
            f"- downstream_routing_preflight_summary: `{operator_handoff['downstream_routing_preflight_summary']}`",
            f"- env_override: `{operator_handoff['env_override_name']}`",
            f"- validation_command_default: `{operator_handoff['validation_command_default']}`",
            f"- validation_command_with_env_override: `{operator_handoff['validation_command_with_env_override']}`",
            f"- schema_boundary: {operator_handoff['schema_boundary']}",
            f"- boundary: {operator_handoff['field_evidence_boundary']}",
        ]
    )
    lines.extend(["", "## 风险边界", ""])
    for issue in report.issues:
        lines.append(f"- `{issue.issue_type}`：{issue.message}")
    return "\n".join(lines)


def _report_payload(report) -> dict[str, object]:
    return {
        "agent_name": report.agent_name,
        "confidence": report.confidence,
        "summary": report.summary,
        "recommendations": report.recommendations,
        "metrics": report.metrics,
        "issues": [
            {
                "sensor": issue.sensor,
                "issue_type": issue.issue_type,
                "severity": issue.severity.value,
                "message": issue.message,
                "evidence": issue.evidence,
            }
            for issue in report.issues
        ],
    }


def _update_manifest(
    generated_files: dict[str, str],
    report,
    field_rows_source: dict[str, object],
    field_rows_schema_validation: dict[str, object] | None = None,
    field_rows_collection_checklist: dict[str, object] | None = None,
    field_rows_batch_bundle_preflight: dict[str, object] | None = None,
    field_rows_temporal_window_preflight: dict[str, object] | None = None,
    field_rows_scenario_semantic_preflight: dict[str, object] | None = None,
    field_rows_downstream_routing_preflight: dict[str, object] | None = None,
    field_rows_downstream_route_handoff: dict[str, object] | None = None,
    field_rows_downstream_target_gate_preflight: dict[str, object] | None = None,
    field_rows_downstream_target_gate_result_intake_schema: dict[str, object] | None = None,
    field_rows_downstream_target_gate_result_preflight: dict[str, object] | None = None,
    field_rows_downstream_target_gate_result_arbitration: dict[str, object] | None = None,
    field_rows_downstream_target_gate_operator_review_template: dict[str, object] | None = None,
    field_rows_downstream_target_gate_operator_review_preflight: dict[str, object] | None = None,
    field_rows_downstream_target_gate_post_review_gate: dict[str, object] | None = None,
    field_rows_downstream_target_gate_protective_candidate_evaluation: dict[str, object] | None = None,
    field_rows_r7_staging_preflight: dict[str, object] | None = None,
    field_rows_r7_completion_plan: dict[str, object] | None = None,
    field_rows_r7_completion_route_contracts: dict[str, object] | None = None,
    field_rows_r7_completion_route_work_packages: dict[str, object] | None = None,
    field_rows_r7_completion_route_work_package_templates: dict[str, object] | None = None,
    field_rows_r7_completion_route_work_package_preflight: dict[str, object] | None = None,
    field_rows_r7_completion_route_work_package_patch_plan: dict[str, object] | None = None,
    field_rows_r7_completion_route_work_package_assembly_gate: dict[str, object] | None = None,
    field_rows_submission_readiness_review: dict[str, object] | None = None,
    field_rows_source_package_submission_route_guide: dict[str, object] | None = None,
    field_rows_source_package_route_preflight: dict[str, object] | None = None,
) -> None:
    manifest = _read_optional_json(MANIFEST_PATH)
    readiness = report.metrics["readiness"]
    manifest["pressure_resolution_replay_scenario_pack"] = {
        key: str(Path(path).relative_to(PROJECT_ROOT))
        for key, path in generated_files.items()
    }
    manifest["latest_r8o_pressure_resolution_scenario_pack_status"] = readiness["scenario_pack_status"]
    manifest["latest_r8o_field_scenario_coverage"] = readiness["field_scenario_coverage"]
    manifest["latest_r8o_source_chain_resolution_fields_ready"] = readiness[
        "source_chain_resolution_fields_ready"
    ]
    manifest["latest_r8o_next_recommended_core_action"] = readiness["next_recommended_core_action"]
    row_readiness = report.metrics["row_collection_readiness"]
    manifest["latest_r8p_row_collection_plan_status"] = row_readiness["row_collection_plan_status"]
    manifest["latest_r8p_missing_scenario_count"] = row_readiness["missing_scenario_count"]
    manifest["latest_r8p_template_row_count"] = row_readiness["template_row_count"]
    field_acceptance = report.metrics["field_row_acceptance"]
    manifest["latest_r8p_field_row_acceptance_status"] = field_acceptance["field_row_acceptance_status"]
    manifest["latest_r8p_accepted_field_scenario_count"] = field_acceptance["accepted_scenario_count"]
    manifest["latest_r8p_accepted_field_batch_count"] = field_acceptance["accepted_batch_count"]
    manifest["latest_r8p_field_rows_source_status"] = field_rows_source["field_rows_source_status"]
    manifest["latest_r8p_field_rows_source_format"] = field_rows_source.get("field_rows_source_format", "unknown")
    manifest["latest_r8p_field_rows_accepted_source_formats"] = field_rows_source.get("accepted_source_formats", [])
    manifest["latest_r8p_field_rows_source_path"] = field_rows_source["field_rows_source_path"]
    field_rows_package_schema = _field_rows_package_schema()
    field_rows_schema_validation = field_rows_schema_validation or {}
    field_rows_batch_bundle_preflight = field_rows_batch_bundle_preflight or {}
    field_rows_temporal_window_preflight = field_rows_temporal_window_preflight or {}
    field_rows_scenario_semantic_preflight = field_rows_scenario_semantic_preflight or {}
    field_rows_downstream_routing_preflight = field_rows_downstream_routing_preflight or {}
    field_rows_downstream_route_handoff = field_rows_downstream_route_handoff or {}
    field_rows_downstream_target_gate_preflight = field_rows_downstream_target_gate_preflight or {}
    field_rows_downstream_target_gate_result_intake_schema = (
        field_rows_downstream_target_gate_result_intake_schema or {}
    )
    field_rows_downstream_target_gate_result_preflight = (
        field_rows_downstream_target_gate_result_preflight or {}
    )
    field_rows_downstream_target_gate_result_arbitration = (
        field_rows_downstream_target_gate_result_arbitration or {}
    )
    field_rows_downstream_target_gate_operator_review_template = (
        field_rows_downstream_target_gate_operator_review_template or {}
    )
    field_rows_downstream_target_gate_operator_review_preflight = (
        field_rows_downstream_target_gate_operator_review_preflight or {}
    )
    field_rows_downstream_target_gate_post_review_gate = (
        field_rows_downstream_target_gate_post_review_gate or {}
    )
    field_rows_downstream_target_gate_protective_candidate_evaluation = (
        field_rows_downstream_target_gate_protective_candidate_evaluation or {}
    )
    patch_plan = _field_rows_patch_plan(
        report,
        field_rows_source,
        field_rows_schema_validation,
        field_rows_batch_bundle_preflight,
        field_rows_temporal_window_preflight,
        field_rows_scenario_semantic_preflight,
    )
    field_rows_collection_checklist = field_rows_collection_checklist or _field_rows_collection_checklist(
        report,
        field_rows_source,
        patch_plan,
        field_rows_package_schema,
        field_rows_schema_validation,
        field_rows_batch_bundle_preflight,
        field_rows_temporal_window_preflight,
        field_rows_scenario_semantic_preflight,
    )
    operator_handoff = _field_rows_operator_handoff(
        report,
        field_rows_source,
        patch_plan,
        field_rows_package_schema,
        field_rows_schema_validation,
        field_rows_collection_checklist,
        field_rows_batch_bundle_preflight,
        field_rows_temporal_window_preflight,
        field_rows_scenario_semantic_preflight,
    )
    manifest["latest_r8p_field_rows_patch_plan_status"] = patch_plan["field_rows_patch_plan_status"]
    manifest["latest_r8p_field_rows_patch_item_count"] = patch_plan["patch_item_count"]
    manifest["latest_r8p_highest_priority_patch_id"] = patch_plan["highest_priority_patch_id"]
    manifest["latest_r8p_field_rows_operator_handoff_status"] = operator_handoff[
        "field_rows_operator_handoff_status"
    ]
    manifest["latest_r8p_field_rows_package_schema_status"] = operator_handoff[
        "field_rows_package_schema_status"
    ]
    manifest["latest_r8p_field_rows_schema_validation_status"] = operator_handoff[
        "field_rows_schema_validation_status"
    ]
    manifest["latest_r8p_field_rows_schema_required_field_gap_count"] = field_rows_schema_validation.get(
        "required_field_gap_count",
        0,
    )
    manifest["latest_r8p_field_rows_schema_invalid_type_count"] = field_rows_schema_validation.get(
        "invalid_type_count",
        0,
    )
    manifest["latest_r8p_field_rows_schema_template_marker_gap_count"] = field_rows_schema_validation.get(
        "template_marker_gap_count",
        0,
    )
    manifest["latest_r8p_field_rows_schema_field_origin_gap_count"] = field_rows_schema_validation.get(
        "field_origin_gap_count",
        0,
    )
    source_status = str(field_rows_source.get("field_rows_source_status", ""))
    template_marker_gap_count = int(field_rows_schema_validation.get("template_marker_gap_count", 0) or 0)
    field_origin_gap_count = int(field_rows_schema_validation.get("field_origin_gap_count", 0) or 0)
    if source_status in {"field_rows_file_missing", "field_rows_file_invalid_json", "field_rows_file_invalid_shape"}:
        template_preflight_status = "template_marker_preflight_blocked_at_source_preflight"
        provenance_preflight_status = "provenance_preflight_blocked_at_source_preflight"
    elif template_marker_gap_count:
        template_preflight_status = "template_marker_preflight_failed_template_values_present"
        provenance_preflight_status = (
            "provenance_preflight_failed_non_field_data_origin"
            if field_origin_gap_count
            else "provenance_preflight_clear_for_loaded_rows"
        )
    elif field_origin_gap_count:
        template_preflight_status = "template_marker_preflight_clear_for_loaded_rows"
        provenance_preflight_status = "provenance_preflight_failed_non_field_data_origin"
    else:
        template_preflight_status = "template_marker_preflight_clear_for_loaded_rows"
        provenance_preflight_status = "provenance_preflight_clear_for_loaded_rows"
    manifest["latest_r8p_field_rows_template_marker_preflight_status"] = template_preflight_status
    manifest["latest_r8p_field_rows_provenance_preflight_status"] = provenance_preflight_status
    manifest["latest_r8p_field_rows_collection_checklist_status"] = field_rows_collection_checklist.get(
        "field_rows_collection_checklist_status",
        "collection_checklist_not_generated",
    )
    manifest["latest_r8p_field_rows_batch_bundle_preflight_status"] = field_rows_batch_bundle_preflight.get(
        "field_rows_batch_bundle_preflight_status",
        "batch_bundle_preflight_not_run",
    )
    manifest["latest_r8p_field_rows_complete_batch_bundle_count"] = field_rows_batch_bundle_preflight.get(
        "complete_bundle_count",
        0,
    )
    manifest["latest_r8p_field_rows_partial_batch_bundle_count"] = field_rows_batch_bundle_preflight.get(
        "partial_bundle_count",
        0,
    )
    manifest["latest_r8p_field_rows_missing_bundle_table_count"] = field_rows_batch_bundle_preflight.get(
        "missing_bundle_table_count",
        0,
    )
    manifest["latest_r8p_field_rows_scenario_bundle_ready_count"] = field_rows_batch_bundle_preflight.get(
        "scenario_bundle_ready_count",
        0,
    )
    manifest["latest_r8p_field_rows_temporal_window_preflight_status"] = field_rows_temporal_window_preflight.get(
        "field_rows_temporal_window_preflight_status",
        "temporal_window_preflight_not_run",
    )
    manifest["latest_r8p_field_rows_temporal_valid_batch_count"] = field_rows_temporal_window_preflight.get(
        "temporal_valid_batch_count",
        0,
    )
    manifest["latest_r8p_field_rows_temporal_violation_count"] = field_rows_temporal_window_preflight.get(
        "temporal_violation_count",
        0,
    )
    manifest["latest_r8p_field_rows_hold_time_violation_count"] = field_rows_temporal_window_preflight.get(
        "hold_time_violation_count",
        0,
    )
    manifest["latest_r8p_field_rows_scenario_temporal_ready_count"] = field_rows_temporal_window_preflight.get(
        "scenario_temporal_ready_count",
        0,
    )
    manifest["latest_r8p_field_rows_scenario_semantic_preflight_status"] = (
        field_rows_scenario_semantic_preflight.get(
            "field_rows_scenario_semantic_preflight_status",
            "scenario_semantic_preflight_not_run",
                )
            )
    manifest["latest_r8p_field_rows_semantic_valid_batch_count"] = field_rows_scenario_semantic_preflight.get(
        "semantic_valid_batch_count",
        0,
    )
    manifest["latest_r8p_field_rows_semantic_violation_count"] = field_rows_scenario_semantic_preflight.get(
        "semantic_violation_count",
        0,
    )
    manifest["latest_r8p_field_rows_scenario_semantic_ready_count"] = field_rows_scenario_semantic_preflight.get(
        "scenario_semantic_ready_count",
        0,
    )
    expected_tables = sorted({*REQUIRED_TABLE_FIELDS, "agent52_replay_table"})
    field_origin_required_tables = [
        table
        for table in expected_tables
        if "data_origin" in _required_fields_for_table(table)
    ]
    all_tables_require_data_origin = len(field_origin_required_tables) == len(expected_tables)
    manifest["latest_r8p_field_rows_all_tables_require_data_origin"] = all_tables_require_data_origin
    manifest["latest_r8p_field_rows_provenance_gate_status"] = (
        "all_required_tables_require_field_origin"
        if all_tables_require_data_origin
        else "field_origin_contract_incomplete"
    )
    manifest["latest_r8p_field_rows_provenance_required_table_count"] = len(field_origin_required_tables)
    manifest["latest_r8p_pressure_resolution_replay_rows_collection_checklist"] = str(
        ROWS_COLLECTION_CHECKLIST_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_r8p_pressure_resolution_replay_rows_batch_bundle_preflight"] = str(
        ROWS_BATCH_BUNDLE_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_r8p_pressure_resolution_replay_rows_temporal_window_preflight"] = str(
        ROWS_TEMPORAL_WINDOW_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_r8p_pressure_resolution_replay_rows_scenario_semantic_preflight"] = str(
        ROWS_SCENARIO_SEMANTIC_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_r8v_field_rows_downstream_routing_preflight_status"] = (
        field_rows_downstream_routing_preflight.get(
            "field_rows_downstream_routing_preflight_status",
            "downstream_routing_preflight_not_run",
        )
    )
    manifest["latest_r8v_field_rows_routing_ready_target_count"] = field_rows_downstream_routing_preflight.get(
        "routing_ready_target_count",
        0,
    )
    manifest["latest_r8v_field_rows_downstream_routing_target_count"] = field_rows_downstream_routing_preflight.get(
        "routing_target_count",
        0,
    )
    manifest["latest_r8v_field_rows_routing_accepted_batch_count"] = field_rows_downstream_routing_preflight.get(
        "accepted_batch_count",
        0,
    )
    manifest["latest_r8v_pressure_resolution_replay_rows_downstream_routing_preflight"] = str(
        ROWS_DOWNSTREAM_ROUTING_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_r8v_pressure_resolution_replay_rows_downstream_route_handoff"] = str(
        ROWS_DOWNSTREAM_ROUTE_HANDOFF_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_r8v_downstream_route_handoff_status"] = field_rows_downstream_route_handoff.get(
        "downstream_route_handoff_status",
        "downstream_route_handoff_not_run",
    )
    manifest["latest_r8v_downstream_handoff_target_count"] = field_rows_downstream_route_handoff.get(
        "handoff_target_count",
        0,
    )
    manifest["latest_r8v_downstream_ready_handoff_target_count"] = field_rows_downstream_route_handoff.get(
        "ready_handoff_target_count",
        0,
    )
    manifest["latest_r8v_downstream_blocked_handoff_target_count"] = field_rows_downstream_route_handoff.get(
        "blocked_handoff_target_count",
        0,
    )
    manifest["latest_r8v_downstream_route_handoff_next_operator_action"] = (
        field_rows_downstream_route_handoff.get("next_operator_action", "")
    )
    manifest["latest_r8v_downstream_route_handoff_can_route_to_r8v"] = (
        field_rows_downstream_route_handoff.get("can_route_to_r8v", False)
    )
    manifest["latest_r8v_pressure_resolution_replay_rows_downstream_target_gate_preflight"] = str(
        ROWS_DOWNSTREAM_TARGET_GATE_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_r8v_downstream_target_gate_preflight_status"] = (
        field_rows_downstream_target_gate_preflight.get(
            "downstream_target_gate_preflight_status",
            "downstream_target_gate_preflight_not_run",
        )
    )
    manifest["latest_r8v_downstream_target_gate_count"] = (
        field_rows_downstream_target_gate_preflight.get("target_gate_count", 0)
    )
    manifest["latest_r8v_downstream_ready_target_gate_count"] = (
        field_rows_downstream_target_gate_preflight.get("ready_target_gate_count", 0)
    )
    manifest["latest_r8v_downstream_blocked_target_gate_count"] = (
        field_rows_downstream_target_gate_preflight.get("blocked_target_gate_count", 0)
    )
    manifest["latest_r8v_downstream_target_gate_preflight_next_operator_action"] = (
        field_rows_downstream_target_gate_preflight.get("next_operator_action", "")
    )
    manifest["latest_r8v_downstream_target_gate_preflight_can_execute_all_target_gates"] = (
        field_rows_downstream_target_gate_preflight.get("can_execute_all_target_gates", False)
    )
    manifest["latest_r8v_pressure_resolution_replay_rows_downstream_target_gate_result_intake_schema"] = str(
        ROWS_DOWNSTREAM_TARGET_GATE_RESULT_INTAKE_SCHEMA_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_r8v_pressure_resolution_replay_rows_downstream_target_gate_result_preflight"] = str(
        ROWS_DOWNSTREAM_TARGET_GATE_RESULT_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_r8v_pressure_resolution_replay_rows_downstream_target_gate_result_arbitration"] = str(
        ROWS_DOWNSTREAM_TARGET_GATE_RESULT_ARBITRATION_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_r8v_pressure_resolution_replay_rows_downstream_target_gate_operator_review_template"] = str(
        ROWS_DOWNSTREAM_TARGET_GATE_OPERATOR_REVIEW_TEMPLATE_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_r8v_pressure_resolution_replay_rows_downstream_target_gate_operator_review_preflight"] = str(
        ROWS_DOWNSTREAM_TARGET_GATE_OPERATOR_REVIEW_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_r8v_pressure_resolution_replay_rows_downstream_target_gate_post_review_gate"] = str(
        ROWS_DOWNSTREAM_TARGET_GATE_POST_REVIEW_GATE_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_r8v_pressure_resolution_replay_rows_downstream_target_gate_protective_candidate_evaluation"] = str(
        ROWS_DOWNSTREAM_TARGET_GATE_PROTECTIVE_CANDIDATE_EVALUATION_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_r8v_downstream_target_gate_result_intake_expected_target_count"] = (
        field_rows_downstream_target_gate_result_intake_schema.get("expected_target_count", 0)
    )
    manifest["latest_r8v_downstream_target_gate_result_preflight_status"] = (
        field_rows_downstream_target_gate_result_preflight.get(
            "downstream_target_gate_result_preflight_status",
            "downstream_target_gate_result_preflight_not_run",
        )
    )
    manifest["latest_r8v_downstream_target_gate_result_submitted_count"] = (
        field_rows_downstream_target_gate_result_preflight.get("submitted_target_result_count", 0)
    )
    manifest["latest_r8v_downstream_target_gate_result_accepted_count"] = (
        field_rows_downstream_target_gate_result_preflight.get("accepted_target_result_count", 0)
    )
    manifest["latest_r8v_downstream_target_gate_result_rejected_count"] = (
        field_rows_downstream_target_gate_result_preflight.get("rejected_target_result_count", 0)
    )
    manifest["latest_r8v_downstream_target_gate_result_missing_target_ids"] = (
        field_rows_downstream_target_gate_result_preflight.get("missing_target_ids", [])
    )
    manifest["latest_r8v_downstream_target_gate_result_next_operator_action"] = (
        field_rows_downstream_target_gate_result_preflight.get("next_operator_action", "")
    )
    manifest["latest_r8v_downstream_target_gate_result_can_route_to_arbitration"] = (
        field_rows_downstream_target_gate_result_preflight.get("can_route_to_result_arbitration", False)
    )
    manifest["latest_r8v_downstream_target_gate_result_arbitration_status"] = (
        field_rows_downstream_target_gate_result_arbitration.get(
            "downstream_target_gate_result_arbitration_status",
            "downstream_target_gate_result_arbitration_not_run",
        )
    )
    manifest["latest_r8v_downstream_target_gate_result_arbitration_next_operator_action"] = (
        field_rows_downstream_target_gate_result_arbitration.get("next_operator_action", "")
    )
    manifest["latest_r8v_downstream_target_gate_result_arbitration_status_counts"] = (
        field_rows_downstream_target_gate_result_arbitration.get("target_gate_status_counts", {})
    )
    manifest["latest_r8v_downstream_target_gate_result_can_route_to_operator_review"] = (
        field_rows_downstream_target_gate_result_arbitration.get("can_route_to_operator_review", False)
    )
    manifest["latest_r8v_downstream_target_gate_result_can_emit_protective_control_candidate"] = (
        field_rows_downstream_target_gate_result_arbitration.get(
            "can_emit_protective_control_candidate",
            False,
        )
    )
    manifest["latest_r8v_downstream_target_gate_operator_review_template_expected_target_count"] = (
        field_rows_downstream_target_gate_operator_review_template.get("expected_target_count", 0)
    )
    manifest["latest_r8v_downstream_target_gate_operator_review_preflight_status"] = (
        field_rows_downstream_target_gate_operator_review_preflight.get(
            "downstream_target_gate_operator_review_preflight_status",
            "downstream_target_gate_operator_review_preflight_not_run",
        )
    )
    manifest["latest_r8v_downstream_target_gate_operator_review_submitted_count"] = (
        field_rows_downstream_target_gate_operator_review_preflight.get(
            "submitted_operator_review_count",
            0,
        )
    )
    manifest["latest_r8v_downstream_target_gate_operator_review_approved_count"] = (
        field_rows_downstream_target_gate_operator_review_preflight.get(
            "approved_operator_review_count",
            0,
        )
    )
    manifest["latest_r8v_downstream_target_gate_operator_review_rejected_count"] = (
        field_rows_downstream_target_gate_operator_review_preflight.get(
            "rejected_operator_review_count",
            0,
        )
    )
    manifest["latest_r8v_downstream_target_gate_operator_review_hold_count"] = (
        field_rows_downstream_target_gate_operator_review_preflight.get(
            "hold_operator_review_count",
            0,
        )
    )
    manifest["latest_r8v_downstream_target_gate_operator_review_next_operator_action"] = (
        field_rows_downstream_target_gate_operator_review_preflight.get("next_operator_action", "")
    )
    manifest["latest_r8v_downstream_target_gate_operator_review_can_route_to_post_review_gate"] = (
        field_rows_downstream_target_gate_operator_review_preflight.get(
            "can_route_to_post_review_gate",
            False,
        )
    )
    manifest["latest_r8v_downstream_target_gate_operator_review_can_emit_protective_control_candidate"] = (
        field_rows_downstream_target_gate_operator_review_preflight.get(
            "can_emit_protective_control_candidate",
            False,
        )
    )
    manifest["latest_r8v_downstream_target_gate_post_review_gate_status"] = (
        field_rows_downstream_target_gate_post_review_gate.get(
            "downstream_target_gate_post_review_gate_status",
            "downstream_target_gate_post_review_gate_not_run",
        )
    )
    manifest["latest_r8v_downstream_target_gate_post_review_candidate_target_count"] = len(
        field_rows_downstream_target_gate_post_review_gate.get("post_review_candidate_targets", []) or []
    )
    manifest["latest_r8v_downstream_target_gate_post_review_can_route_to_protective_candidate"] = (
        field_rows_downstream_target_gate_post_review_gate.get(
            "can_route_to_protective_candidate_evaluation",
            False,
        )
    )
    manifest["latest_r8v_downstream_target_gate_post_review_can_emit_protective_control_candidate"] = (
        field_rows_downstream_target_gate_post_review_gate.get(
            "can_emit_protective_control_candidate",
            False,
        )
    )
    manifest["latest_r8v_downstream_target_gate_post_review_next_operator_action"] = (
        field_rows_downstream_target_gate_post_review_gate.get("next_operator_action", "")
    )
    protective_candidate_bundle = (
        field_rows_downstream_target_gate_protective_candidate_evaluation.get("candidate_action_bundle", {})
    )
    protective_candidate_actions = (
        protective_candidate_bundle.get("candidate_actions", [])
        if isinstance(protective_candidate_bundle, dict)
        else []
    )
    manifest["latest_r8v_downstream_target_gate_protective_candidate_evaluation_status"] = (
        field_rows_downstream_target_gate_protective_candidate_evaluation.get(
            "downstream_target_gate_protective_candidate_evaluation_status",
            "protective_candidate_evaluation_not_run",
        )
    )
    manifest["latest_r8v_downstream_target_gate_protective_candidate_target_count"] = (
        field_rows_downstream_target_gate_protective_candidate_evaluation.get("candidate_target_count", 0)
    )
    manifest["latest_r8v_downstream_target_gate_protective_candidate_action_count"] = len(
        protective_candidate_actions
    )
    manifest["latest_r8v_downstream_target_gate_protective_candidate_can_emit"] = (
        field_rows_downstream_target_gate_protective_candidate_evaluation.get(
            "can_emit_protective_control_candidate",
            False,
        )
    )
    manifest["latest_r8v_downstream_target_gate_protective_candidate_can_route_to_final_execution_review"] = (
        field_rows_downstream_target_gate_protective_candidate_evaluation.get(
            "can_route_to_final_execution_review",
            False,
        )
    )
    manifest["latest_r8v_downstream_target_gate_protective_candidate_next_operator_action"] = (
        field_rows_downstream_target_gate_protective_candidate_evaluation.get("next_operator_action", "")
    )
    manifest["latest_r8p_field_rows_validation_command"] = operator_handoff["validation_command_default"]
    manifest["latest_r8p_default_field_rows_path"] = operator_handoff["default_field_rows_path"]
    manifest["latest_r8p_pressure_resolution_replay_rows_schema"] = str(
        ROWS_SCHEMA_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_r8p_pressure_resolution_replay_rows_template"] = str(
        TEMPLATE_ROWS_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_r8p_pressure_resolution_replay_rows_csv_template"] = str(
        ROWS_CSV_TEMPLATE_DIR.relative_to(PROJECT_ROOT)
    )
    r7_alignment = _field_rows_r7_alignment(field_rows_package_schema)
    manifest["latest_r8p_pressure_resolution_replay_rows_r7_alignment"] = str(
        ROWS_R7_ALIGNMENT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_r8p_r7_alignment_status"] = r7_alignment["alignment_status"]
    manifest["latest_r8p_r7_shared_table_count"] = r7_alignment["r7_shared_table_count"]
    manifest["latest_r8p_r7_agent52_export_required_field_count"] = r7_alignment[
        "agent52_export_required_field_count"
    ]
    manifest["latest_r8p_r7_supplement_required_field_count"] = r7_alignment[
        "supplement_required_field_count"
    ]
    r7_staging = field_rows_r7_staging_preflight or {}
    manifest["latest_r8p_pressure_resolution_replay_rows_r7_staging_preflight"] = str(
        ROWS_R7_STAGING_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_r8p_pressure_resolution_replay_rows_r7_staged_draft"] = str(
        ROWS_R7_STAGED_DRAFT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_r8p_r7_staging_status"] = r7_staging.get(
        "r7_staging_preflight_status",
        "r7_to_r8p_staging_preflight_not_run",
    )
    manifest["latest_r8p_r7_staged_table_count"] = r7_staging.get("staged_table_count", 0)
    manifest["latest_r8p_r7_staged_row_count"] = r7_staging.get("staged_row_count", 0)
    manifest["latest_r8p_r7_staging_required_field_gap_count"] = r7_staging.get(
        "required_field_gap_count",
        0,
    )
    manifest["latest_r8p_r7_staging_supplement_gap_count"] = r7_staging.get(
        "supplement_required_field_gap_count",
        0,
    )
    manifest["latest_r8p_r7_staging_agent52_export_gap_count"] = r7_staging.get(
        "agent52_export_required_field_gap_count",
        0,
    )
    manifest["latest_r8p_r7_staging_can_enter_r8p_schema_preflight"] = r7_staging.get(
        "can_enter_r8p_schema_preflight",
        False,
    )
    r7_completion = field_rows_r7_completion_plan or {}
    manifest["latest_r8p_pressure_resolution_replay_rows_r7_completion_plan"] = str(
        ROWS_R7_COMPLETION_PLAN_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_r8p_r7_completion_plan_status"] = r7_completion.get(
        "completion_plan_status",
        "r7_to_r8p_completion_plan_not_run",
    )
    manifest["latest_r8p_r7_completion_item_count"] = r7_completion.get("item_count", 0)
    manifest["latest_r8p_r7_completion_item_class_counts"] = r7_completion.get("item_class_counts", {})
    manifest["latest_r8p_r7_completion_field_gap_count_by_class"] = r7_completion.get(
        "field_gap_count_by_class",
        {},
    )
    r7_route_contracts = field_rows_r7_completion_route_contracts or {}
    manifest["latest_r8p_pressure_resolution_replay_rows_r7_completion_route_contracts"] = str(
        ROWS_R7_COMPLETION_ROUTE_CONTRACTS_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_r8p_r7_completion_route_contracts_status"] = r7_route_contracts.get(
        "completion_route_contracts_status",
        "completion_route_contracts_not_run",
    )
    manifest["latest_r8p_r7_completion_route_contract_count"] = r7_route_contracts.get("route_contract_count", 0)
    manifest["latest_r8p_r7_completion_open_route_count"] = r7_route_contracts.get("open_route_count", 0)
    manifest["latest_r8p_r7_completion_open_route_ids"] = r7_route_contracts.get("open_route_ids", [])
    r7_route_work_packages = field_rows_r7_completion_route_work_packages or {}
    manifest["latest_r8p_pressure_resolution_replay_rows_r7_completion_route_work_packages"] = str(
        ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGES_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_r8p_r7_completion_route_work_packages_status"] = r7_route_work_packages.get(
        "route_work_packages_status",
        "route_work_packages_not_run",
    )
    manifest["latest_r8p_r7_completion_route_work_package_count"] = r7_route_work_packages.get(
        "work_package_count",
        0,
    )
    manifest["latest_r8p_r7_completion_open_work_package_count"] = r7_route_work_packages.get(
        "open_work_package_count",
        0,
    )
    manifest["latest_r8p_r7_completion_open_work_package_ids"] = r7_route_work_packages.get(
        "open_work_package_ids",
        [],
    )
    r7_route_work_package_templates = field_rows_r7_completion_route_work_package_templates or {}
    r7_route_work_package_preflight = field_rows_r7_completion_route_work_package_preflight or {}
    r7_route_work_package_patch_plan = field_rows_r7_completion_route_work_package_patch_plan or {}
    r7_route_work_package_assembly_gate = field_rows_r7_completion_route_work_package_assembly_gate or {}
    field_rows_submission_readiness_review = field_rows_submission_readiness_review or {}
    field_rows_source_package_submission_route_guide = field_rows_source_package_submission_route_guide or {}
    field_rows_source_package_route_preflight = field_rows_source_package_route_preflight or {}
    manifest["latest_r8p_pressure_resolution_replay_rows_r7_completion_route_work_package_templates"] = str(
        ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_TEMPLATE_DIR.relative_to(PROJECT_ROOT)
    )
    manifest["latest_r8p_pressure_resolution_replay_rows_r7_completion_route_work_package_preflight"] = str(
        ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_r8p_pressure_resolution_replay_rows_r7_completion_route_work_package_patch_plan"] = str(
        ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_PATCH_PLAN_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_r8p_pressure_resolution_replay_rows_r7_completion_route_work_package_assembly_gate"] = str(
        ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_ASSEMBLY_GATE_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_r8p_r7_completion_route_work_package_templates_status"] = (
        r7_route_work_package_templates.get(
            "route_work_package_templates_status",
            "route_work_package_templates_not_run",
        )
    )
    manifest["latest_r8p_r7_completion_route_work_package_template_count"] = (
        r7_route_work_package_templates.get("work_package_template_count", 0)
    )
    manifest["latest_r8p_r7_completion_route_work_package_preflight_status"] = (
        r7_route_work_package_preflight.get(
            "route_work_package_preflight_status",
            "route_work_package_preflight_not_run",
        )
    )
    manifest["latest_r8p_r7_completion_route_work_package_preflight_submission_dir"] = (
        r7_route_work_package_preflight.get("configured_submission_dir", "")
    )
    manifest["latest_r8p_r7_completion_submitted_work_package_count"] = (
        r7_route_work_package_preflight.get("submitted_work_package_count", 0)
    )
    manifest["latest_r8p_r7_completion_passed_work_package_count"] = (
        r7_route_work_package_preflight.get("passed_work_package_count", 0)
    )
    manifest["latest_r8p_r7_completion_blocked_work_package_count"] = (
        r7_route_work_package_preflight.get("blocked_work_package_count", 0)
    )
    manifest["latest_r8p_r7_completion_route_work_package_patch_plan_status"] = (
        r7_route_work_package_patch_plan.get(
            "route_work_package_patch_plan_status",
            "route_work_package_patch_plan_not_run",
        )
    )
    manifest["latest_r8p_r7_completion_route_work_package_patch_item_count"] = (
        r7_route_work_package_patch_plan.get("patch_item_count", 0)
    )
    manifest["latest_r8p_r7_completion_route_work_package_highest_priority_patch_id"] = (
        r7_route_work_package_patch_plan.get("highest_priority_patch_id", "")
    )
    manifest["latest_r8p_r7_completion_route_work_package_assembly_gate_status"] = (
        r7_route_work_package_assembly_gate.get(
            "route_work_package_assembly_gate_status",
            "route_work_package_assembly_gate_not_run",
        )
    )
    manifest["latest_r8p_r7_completion_route_work_package_assembly_step_count"] = (
        r7_route_work_package_assembly_gate.get("assembly_step_count", 0)
    )
    manifest["latest_r8p_r7_completion_route_work_package_ready_assembly_step_count"] = (
        r7_route_work_package_assembly_gate.get("ready_assembly_step_count", 0)
    )
    manifest["latest_r8p_r7_completion_route_work_package_blocked_assembly_step_count"] = (
        r7_route_work_package_assembly_gate.get("blocked_assembly_step_count", 0)
    )
    manifest["latest_r8p_pressure_resolution_replay_rows_submission_readiness_review"] = str(
        ROWS_SUBMISSION_READINESS_REVIEW_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_r8p_submission_readiness_review_status"] = (
        field_rows_submission_readiness_review.get(
            "submission_readiness_review_status",
            "submission_readiness_review_not_run",
        )
    )
    manifest["latest_r8p_submission_readiness_next_operator_action"] = (
        field_rows_submission_readiness_review.get("next_operator_action", "")
    )
    manifest["latest_r8p_submission_readiness_can_route_to_r8v"] = (
        field_rows_submission_readiness_review.get("can_route_to_r8v", False)
    )
    manifest["latest_r8p_submission_readiness_direct_highest_priority_patch_id"] = (
        field_rows_submission_readiness_review.get("direct_r8p_highest_priority_patch_id")
    )
    manifest["latest_r8p_submission_readiness_r7_highest_priority_patch_id"] = (
        field_rows_submission_readiness_review.get("r7_to_r8p_highest_priority_patch_id")
    )
    manifest["latest_r8p_pressure_resolution_replay_rows_source_package_submission_route_guide"] = str(
        ROWS_SOURCE_PACKAGE_SUBMISSION_ROUTE_GUIDE_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_r8p_source_package_route_guide_status"] = (
        field_rows_source_package_submission_route_guide.get(
            "source_package_submission_route_guide_status",
            "source_package_submission_route_guide_not_run",
        )
    )
    manifest["latest_r8p_source_package_recommended_route_id"] = (
        field_rows_source_package_submission_route_guide.get("recommended_route_id", "")
    )
    manifest["latest_r8p_source_package_next_operator_action"] = (
        field_rows_source_package_submission_route_guide.get("next_operator_action", "")
    )
    manifest["latest_r8p_source_package_route_option_count"] = (
        field_rows_source_package_submission_route_guide.get("route_option_count", 0)
    )
    manifest["latest_r8p_source_package_can_route_to_r8v"] = (
        field_rows_source_package_submission_route_guide.get("can_route_to_r8v", False)
    )
    manifest["latest_r8p_pressure_resolution_replay_rows_source_package_route_preflight"] = str(
        ROWS_SOURCE_PACKAGE_ROUTE_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_r8p_source_package_route_preflight_status"] = (
        field_rows_source_package_route_preflight.get(
            "source_package_route_preflight_status",
            "source_package_route_preflight_not_run",
        )
    )
    manifest["latest_r8p_source_package_recommended_route_preflight_status"] = (
        field_rows_source_package_route_preflight.get("recommended_route_preflight_status", "")
    )
    manifest["latest_r8p_source_package_route_preflight_next_operator_action"] = (
        field_rows_source_package_route_preflight.get("next_operator_action", "")
    )
    manifest["latest_r8p_source_package_ready_route_count"] = (
        field_rows_source_package_route_preflight.get("ready_route_count", 0)
    )
    manifest["latest_r8p_source_package_waiting_route_count"] = (
        field_rows_source_package_route_preflight.get("waiting_route_count", 0)
    )
    manifest["latest_r8p_source_package_blocked_route_count"] = (
        field_rows_source_package_route_preflight.get("blocked_route_count", 0)
    )
    manifest["next_stage"] = (
        "按 Agent60/R8o 复盘，继续 R7a 真实 field package 导入；无真实包时，"
        "优先执行 R8p_fix_field_rows_source_preflight，按 R8p operator handoff、R7-to-R8p route contracts "
        "和 R8u-25 route work packages，并使用 R8u-26 submission templates/preflight、R8u-27 patch plan "
        "与 R8u-28 assembly gate 创建/修复/装配真实行包并运行验收命令。"
    )
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
