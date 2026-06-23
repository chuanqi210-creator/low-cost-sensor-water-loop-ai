from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from water_ai.new_core_interface_candidate_gate import (
    build_new_core_interface_candidate_gate,
    new_core_interface_candidate_gate_report_md,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
CORE_GATE_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "core_score_termination_gate.json"
)
PRIORITY_RANKING_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "priority_ranking.json"
)
GREY_BOX_CALIBRATION_PREFLIGHT_PATH = (
    PROJECT_ROOT / "outputs" / "grey_box_calibration_package" / "grey_box_calibration_package_preflight.json"
)
GREY_BOX_FIELD_CALIBRATION_SUMMARY_PATH = (
    PROJECT_ROOT / "outputs" / "grey_box_calibration_package" / "grey_box_field_calibration_summary.json"
)
FIELD_SUPPORTED_KG_EDGE_PREFLIGHT_PATH = (
    PROJECT_ROOT / "outputs" / "field_supported_kg_edge_package" / "field_supported_kg_edge_package_preflight.json"
)
SPARSE_TOPOLOGY_INSTALLABILITY_PREFLIGHT_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "sparse_topology_installability_package"
    / "sparse_topology_installability_package_preflight.json"
)
FIELD_CONTROL_REPLAY_PREFLIGHT_PATH = (
    PROJECT_ROOT / "outputs" / "field_control_replay_package" / "field_control_replay_package_preflight.json"
)
FIELD_MISSINGNESS_REPLAY_PREFLIGHT_PATH = (
    PROJECT_ROOT / "outputs" / "field_missingness_replay_package" / "field_missingness_replay_package_preflight.json"
)
OUT_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "new_core_interface_candidate_gate.json"
)
REPORT_PATH = (
    PROJECT_ROOT
    / "deliverables"
    / "model_core_optimization"
    / "new_core_interface_candidate_gate.md"
)


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    gate = build_new_core_interface_candidate_gate(
        core_gate=_read_json(CORE_GATE_PATH),
        priority_ranking=_priority_ranking_rows(_read_json(PRIORITY_RANKING_PATH)),
        grey_box_calibration_preflight=_read_json(GREY_BOX_CALIBRATION_PREFLIGHT_PATH),
        grey_box_field_calibration_summary=_read_json(GREY_BOX_FIELD_CALIBRATION_SUMMARY_PATH),
        field_supported_kg_edge_preflight=_read_json(FIELD_SUPPORTED_KG_EDGE_PREFLIGHT_PATH),
        sparse_topology_installability_preflight=_read_json(
            SPARSE_TOPOLOGY_INSTALLABILITY_PREFLIGHT_PATH
        ),
        field_control_replay_preflight=_read_json(FIELD_CONTROL_REPLAY_PREFLIGHT_PATH),
        field_missingness_replay_preflight=_read_json(FIELD_MISSINGNESS_REPLAY_PREFLIGHT_PATH),
    )
    OUT_PATH.write_text(json.dumps(gate, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_PATH.write_text(new_core_interface_candidate_gate_report_md(gate), encoding="utf-8")
    _update_manifest(gate)

    metadata = gate["gate_metadata"]
    summary = gate["candidate_summary"]
    print(f"New core interface candidate gate: {metadata['gate_status']}")
    print(f"- candidate_count: {summary['candidate_count']}")
    print(f"- admissible_candidate_count: {summary['admissible_candidate_count']}")
    print(f"- highest_priority_candidate_id: {summary['highest_priority_candidate_id']}")
    print(f"- highest_priority_source_env_var: {summary['highest_priority_source_env_var']}")
    print(
        "- highest_priority_downstream_calibration_status: "
        f"{summary['highest_priority_downstream_calibration_status']}"
    )
    print(f"gate: {OUT_PATH}")
    print(f"report: {REPORT_PATH}")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _priority_ranking_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("priority_ranking", [])
    return rows if isinstance(rows, list) else []


def _update_manifest(gate: dict[str, Any]) -> None:
    manifest = _read_json(MANIFEST_PATH)
    metadata = gate["gate_metadata"]
    summary = gate["candidate_summary"]
    manifest["latest_new_core_interface_candidate_gate"] = str(
        OUT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_new_core_interface_candidate_gate_report"] = str(
        REPORT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_new_core_interface_candidate_gate_status"] = metadata["gate_status"]
    manifest["latest_new_core_interface_candidate_count"] = summary["candidate_count"]
    manifest["latest_new_core_interface_admissible_candidate_count"] = summary[
        "admissible_candidate_count"
    ]
    manifest["latest_new_core_interface_highest_priority_candidate_id"] = summary[
        "highest_priority_candidate_id"
    ]
    manifest["latest_new_core_interface_highest_priority_source_env_var"] = summary[
        "highest_priority_source_env_var"
    ]
    manifest["latest_new_core_interface_highest_priority_validation_command"] = summary[
        "highest_priority_validation_command"
    ]
    manifest["latest_new_core_interface_highest_priority_next_interface_action"] = summary[
        "highest_priority_next_interface_action"
    ]
    manifest["latest_new_core_interface_highest_priority_preflight_status"] = summary[
        "highest_priority_preflight_status"
    ]
    manifest["latest_new_core_interface_highest_priority_preflight_pass"] = summary[
        "highest_priority_preflight_pass"
    ]
    manifest["latest_new_core_interface_highest_priority_can_route_to_downstream_calibration"] = (
        summary["highest_priority_can_route_to_downstream_calibration"]
    )
    manifest["latest_new_core_interface_highest_priority_can_route_to_downstream_interface"] = (
        summary["highest_priority_can_route_to_downstream_interface"]
    )
    manifest["latest_new_core_interface_highest_priority_downstream_calibration_status"] = (
        summary["highest_priority_downstream_calibration_status"]
    )
    manifest["latest_new_core_interface_highest_priority_downstream_interface_status"] = (
        summary["highest_priority_downstream_interface_status"]
    )
    manifest["latest_new_core_interface_highest_priority_can_run_agent53_field_calibration"] = (
        summary["highest_priority_can_run_agent53_field_calibration"]
    )
    manifest["latest_new_core_interface_highest_priority_agent53_field_candidate_ready"] = (
        summary["highest_priority_agent53_field_candidate_ready"]
    )
    manifest["latest_new_core_interface_can_generate_field_evidence"] = summary[
        "can_generate_field_evidence"
    ]
    manifest["latest_new_core_interface_can_write_to_actuator"] = summary[
        "can_write_to_actuator"
    ]
    manifest["latest_new_core_interface_can_write_to_release_gate"] = summary[
        "can_write_to_release_gate"
    ]
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
