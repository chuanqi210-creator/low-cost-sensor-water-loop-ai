from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from water_ai.governance_recovery_integrity_audit import (
    build_governance_recovery_integrity_audit,
    governance_recovery_integrity_audit_report_md,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
STAGE_BOUNDARY_BOARD_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "stage_boundary_external_action_board.json"
)
CORE_GATE_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "core_score_termination_gate.json"
)
OUT_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "governance_recovery_integrity_audit.json"
)
REPORT_PATH = (
    PROJECT_ROOT
    / "deliverables"
    / "model_core_optimization"
    / "governance_recovery_integrity_audit.md"
)


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    audit = build_governance_recovery_integrity_audit(
        project_root=PROJECT_ROOT,
        manifest=_read_json(MANIFEST_PATH),
        stage_boundary_external_action_board=_read_json(STAGE_BOUNDARY_BOARD_PATH),
        core_score_termination_gate=_read_json(CORE_GATE_PATH),
    )
    OUT_PATH.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_PATH.write_text(
        governance_recovery_integrity_audit_report_md(audit),
        encoding="utf-8",
    )
    _update_manifest(audit)
    print(f"Governance recovery integrity audit: {audit['audit_metadata']['audit_status']}")
    print(f"- recovery_integrity_score: {audit['recovery_integrity_score']}")
    print(f"- recovery_integrity_stage_pass: {audit['recovery_integrity_stage_pass']}")
    print(f"- safe_next_route: {audit['safe_next_route']}")
    print(f"audit: {OUT_PATH}")
    print(f"report: {REPORT_PATH}")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _update_manifest(audit: dict[str, Any]) -> None:
    manifest = _read_json(MANIFEST_PATH)
    metadata = audit["audit_metadata"]
    manifest["latest_governance_recovery_integrity_audit"] = str(
        OUT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_governance_recovery_integrity_audit_report"] = str(
        REPORT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_governance_recovery_integrity_audit_status"] = metadata[
        "audit_status"
    ]
    manifest["latest_governance_recovery_integrity_score"] = audit[
        "recovery_integrity_score"
    ]
    manifest["latest_governance_recovery_integrity_stage_pass"] = audit[
        "recovery_integrity_stage_pass"
    ]
    manifest["latest_governance_recovery_integrity_blockers"] = audit["blockers"]
    manifest["latest_governance_recovery_integrity_stale_or_mismatch_fields"] = audit[
        "stale_or_mismatch_fields"
    ]
    manifest["latest_governance_recovery_integrity_safe_next_route"] = audit[
        "safe_next_route"
    ]
    manifest["latest_governance_recovery_integrity_change_inventory"] = audit[
        "change_inventory"
    ]
    numeric_trace = audit["numeric_calculation_trace"]
    manifest["latest_governance_recovery_integrity_numeric_trace_status"] = (
        numeric_trace["trace_status"]
    )
    manifest["latest_governance_recovery_integrity_numeric_trace_pass"] = (
        numeric_trace["trace_pass"]
    )
    manifest["latest_governance_recovery_integrity_numeric_trace_score_delta"] = (
        numeric_trace["score_delta"]
    )
    manifest["latest_governance_recovery_integrity_numeric_trace_component_count"] = (
        numeric_trace["component_count"]
    )
    protocol_adaptation = audit["protocol_adaptation"]
    anti_bloat_gate = protocol_adaptation["anti_protocol_bloat_gate"]
    trace_gate = audit["minimum_traceability_gate"]
    manifest["latest_governance_recovery_integrity_protocol_adaptation_status"] = (
        protocol_adaptation["adaptation_status"]
    )
    manifest["latest_governance_recovery_integrity_protocol_anti_bloat_gate_status"] = (
        anti_bloat_gate["gate_status"]
    )
    manifest["latest_governance_recovery_integrity_protocol_selected_rule_count"] = (
        anti_bloat_gate["selected_rule_count"]
    )
    manifest["latest_governance_recovery_integrity_protocol_deferred_rule_count"] = (
        anti_bloat_gate["deferred_rule_count"]
    )
    manifest["latest_governance_recovery_traceability_gate_status"] = trace_gate[
        "gate_status"
    ]
    manifest["latest_governance_recovery_traceability_score"] = trace_gate[
        "traceability_score"
    ]
    manifest["latest_governance_recovery_traceability_missing_link_count"] = (
        trace_gate["missing_link_count"]
    )
    manifest["latest_governance_recovery_decision_log_status"] = trace_gate[
        "decision_log_status"
    ]
    manifest["latest_agent50_governance_recovery_integrity_audit_status"] = metadata[
        "audit_status"
    ]
    manifest["latest_agent50_governance_recovery_integrity_score"] = audit[
        "recovery_integrity_score"
    ]
    manifest["latest_agent50_governance_recovery_integrity_stage_pass"] = audit[
        "recovery_integrity_stage_pass"
    ]
    manifest["latest_agent50_governance_recovery_integrity_numeric_trace_status"] = (
        numeric_trace["trace_status"]
    )
    manifest["latest_agent50_governance_recovery_integrity_protocol_adaptation_status"] = (
        protocol_adaptation["adaptation_status"]
    )
    manifest["latest_agent50_governance_recovery_traceability_gate_status"] = trace_gate[
        "gate_status"
    ]
    manifest["latest_agent50_governance_recovery_traceability_score"] = trace_gate[
        "traceability_score"
    ]
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
