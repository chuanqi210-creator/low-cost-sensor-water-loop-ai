from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from water_ai.core_interface_consolidation import (
    build_core_interface_consolidation,
    core_interface_consolidation_report_md,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables" / "model_core_optimization"
OUT_DIR = PROJECT_ROOT / "outputs" / "model_core_governance"
CONSOLIDATION_PATH = OUT_DIR / "core_interface_consolidation.json"
REPORT_PATH = DELIVERABLES_DIR / "core_interface_consolidation.md"

AGENT48_METRICS_PATH = PROJECT_ROOT / "outputs" / "sensor_network_sparse_placement" / "sparse_placement_metrics.json"
AGENT52_REPLAY_METRICS_PATH = PROJECT_ROOT / "outputs" / "multi_facility_replay_evaluation" / "replay_evaluation_metrics.json"
FIELD_CONTROL_REPLAY_PREFLIGHT_PATH = (
    PROJECT_ROOT / "outputs" / "field_control_replay_package" / "field_control_replay_package_preflight.json"
)
SPARSE_TOPOLOGY_INSTALLABILITY_PREFLIGHT_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "sparse_topology_installability_package"
    / "sparse_topology_installability_package_preflight.json"
)
GREY_BOX_COLLECTION_WORK_ORDER_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "grey_box_calibration_package"
    / "grey_box_calibration_collection_work_order.json"
)
GREY_BOX_SUBMISSION_READINESS_GATE_PATH = (
    PROJECT_ROOT / "outputs" / "grey_box_calibration_package" / "grey_box_submission_readiness_gate.json"
)
EXTERNAL_PACKAGE_ACQUISITION_MATURITY_GATE_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "external_package_acquisition_maturity_gate.json"
)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    consolidation = build_core_interface_consolidation(
        agent48_metrics=_read_json(AGENT48_METRICS_PATH),
        field_control_replay_preflight=_read_optional_json(FIELD_CONTROL_REPLAY_PREFLIGHT_PATH),
        sparse_topology_installability_preflight=_read_optional_json(SPARSE_TOPOLOGY_INSTALLABILITY_PREFLIGHT_PATH),
        grey_box_collection_work_order=_read_optional_json(GREY_BOX_COLLECTION_WORK_ORDER_PATH),
        grey_box_submission_readiness_gate=_read_optional_json(GREY_BOX_SUBMISSION_READINESS_GATE_PATH),
        external_package_acquisition_maturity_gate=_read_optional_json(EXTERNAL_PACKAGE_ACQUISITION_MATURITY_GATE_PATH),
        agent52_replay_metrics=_read_optional_json(AGENT52_REPLAY_METRICS_PATH),
    )
    CONSOLIDATION_PATH.write_text(json.dumps(consolidation, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_PATH.write_text(core_interface_consolidation_report_md(consolidation), encoding="utf-8")
    _update_manifest(consolidation)

    priority = consolidation["priority_decision"]
    print(f"Core interface consolidation: {consolidation['consolidation_id']}")
    print(f"- top_external_action_env_var: {priority['top_external_action_env_var']}")
    print(f"- top_internal_action: {priority['top_internal_action']}")
    print(f"- new_agent_recommendation: {priority['new_agent_recommendation']}")
    print(f"json: {CONSOLIDATION_PATH}")
    print(f"report: {REPORT_PATH}")


def _update_manifest(consolidation: dict[str, Any]) -> None:
    manifest = _read_optional_json(MANIFEST_PATH)
    priority = consolidation["priority_decision"]
    facades = consolidation["facades"]
    manifest["latest_core_interface_consolidation"] = str(CONSOLIDATION_PATH.relative_to(PROJECT_ROOT))
    manifest["latest_core_interface_consolidation_report"] = str(REPORT_PATH.relative_to(PROJECT_ROOT))
    manifest["latest_core_interface_consolidation_id"] = consolidation["consolidation_id"]
    manifest["latest_core_interface_consolidation_facade_count"] = consolidation["facade_count"]
    manifest["latest_core_interface_consolidation_top_external_action_env_var"] = priority[
        "top_external_action_env_var"
    ]
    manifest["latest_core_interface_consolidation_top_internal_action"] = priority["top_internal_action"]
    manifest["latest_core_interface_consolidation_new_agent_recommendation"] = priority[
        "new_agent_recommendation"
    ]
    manifest["latest_core_interface_consolidation_external_lifecycle_status"] = facades[
        "external_package_lifecycle"
    ]["facade_status"]
    grey_box_lifecycle_row = next(
        row
        for row in facades["external_package_lifecycle"]["package_lifecycle_rows"]
        if row["package_key"] == "grey_box_calibration"
    )
    manifest["latest_core_interface_consolidation_grey_box_submission_readiness_gate_status"] = (
        grey_box_lifecycle_row["submission_readiness_gate_status"]
    )
    manifest["latest_core_interface_consolidation_grey_box_submission_readiness_score"] = (
        grey_box_lifecycle_row["submission_readiness_score"]
    )
    manifest["latest_core_interface_consolidation_grey_box_submission_highest_priority_gap_type"] = (
        grey_box_lifecycle_row["submission_highest_priority_gap_type"]
    )
    manifest["latest_core_interface_consolidation_grey_box_submission_highest_priority_gap_table"] = (
        grey_box_lifecycle_row["submission_highest_priority_gap_table"]
    )
    manifest["latest_core_interface_consolidation_grey_box_submission_missing_table_count"] = (
        grey_box_lifecycle_row["submission_missing_table_count"]
    )
    manifest["latest_core_interface_consolidation_grey_box_submission_missing_tables"] = (
        grey_box_lifecycle_row["submission_missing_tables"]
    )
    manifest["latest_core_interface_consolidation_grey_box_submission_source_env_var"] = (
        grey_box_lifecycle_row["submission_source_env_var"]
    )
    manifest["latest_core_interface_consolidation_can_submit_to_agent53_field_calibration"] = (
        grey_box_lifecycle_row["can_submit_to_agent53_field_calibration"]
    )
    manifest["latest_core_interface_consolidation_can_submit_to_agent53_field_candidate"] = (
        grey_box_lifecycle_row["can_submit_to_agent53_field_candidate"]
    )
    manifest["latest_core_interface_consolidation_sparse_benchmark_status"] = facades[
        "sparse_layout_soft_sensor_coupling_benchmark"
    ]["benchmark_status"]
    manifest["latest_core_interface_consolidation_control_crosswalk_status"] = facades[
        "field_control_replay_crosswalk"
    ]["crosswalk_status"]
    manifest["latest_core_interface_consolidation_can_generate_field_evidence"] = consolidation[
        "boundary"
    ]["can_generate_field_evidence"]
    manifest["latest_core_interface_consolidation_can_write_to_actuator"] = consolidation["boundary"][
        "can_write_to_actuator"
    ]
    manifest["latest_core_interface_consolidation_can_write_to_release_gate"] = consolidation[
        "boundary"
    ]["can_write_to_release_gate"]
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
