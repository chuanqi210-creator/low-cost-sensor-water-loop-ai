from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from water_ai.formal_search_nonlegal_review_operator_packet import (
    build_formal_search_nonlegal_review_operator_packet,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LEGACY_PROJECT_ROOTS = (
    Path("/legacy/workspaces/low-cost-sensor-water-loop-ai"),
    Path("/legacy/workspaces/low-cost-sensor-water-loop-ai-cn"),
    Path("/legacy/workspaces/py-learning/low-cost-sensor-water-loop-ai-cn"),
)
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
AGENT60_DIR = PROJECT_ROOT / "outputs" / "agent_architecture_consolidation"
AI_BRIEF_PATH = AGENT60_DIR / "formal_search_ai_nonlegal_review_brief.json"
RESPONSE_TEMPLATE_PATH = (
    AGENT60_DIR / "formal_search_nonlegal_review_response_template.json"
)
RESPONSE_PREFLIGHT_PATH = (
    AGENT60_DIR / "formal_search_nonlegal_review_response_source_preflight.json"
)
PRELIMINARY_FORMAL_SEARCH_HANDOFF_PATH = (
    AGENT60_DIR / "preliminary_formal_search_handoff.json"
)
REVIEW_READINESS_PATH = AGENT60_DIR / "formal_search_review_readiness.json"
CLAIM_SCOPE_PATCH_DRAFT_PATH = AGENT60_DIR / "formal_search_claim_scope_patch_draft.json"
OUT_PATH = AGENT60_DIR / "formal_search_nonlegal_review_operator_packet.json"
REPORT_PATH = (
    PROJECT_ROOT
    / "deliverables"
    / "model_core_optimization"
    / "formal_search_nonlegal_review_operator_packet.md"
)


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    packet = build_formal_search_nonlegal_review_operator_packet(
        ai_nonlegal_review_brief=_read_json(AI_BRIEF_PATH),
        nonlegal_review_response_template=_read_json(RESPONSE_TEMPLATE_PATH),
        nonlegal_review_response_source_preflight=_read_json(RESPONSE_PREFLIGHT_PATH),
        formal_search_review_readiness=_read_json(REVIEW_READINESS_PATH),
        claim_scope_patch_draft=_read_json(CLAIM_SCOPE_PATCH_DRAFT_PATH),
        upstream_formal_search_result_package_path=_upstream_formal_search_result_package_path(),
    )
    _write_json(OUT_PATH, packet)
    _write_text(REPORT_PATH, _report_md(packet))
    _update_manifest(packet)

    metadata = packet["operator_packet_metadata"]
    action = packet["operator_action"]
    downstream = packet["downstream_state"]
    print(f"Formal search nonlegal review operator packet: {metadata['packet_status']}")
    print(f"- expected_review_packet_row_count: {action['expected_review_packet_row_count']}")
    print(f"- high_priority_review_row_count: {action['high_priority_review_row_count']}")
    print(f"- accepted_review_row_count: {action['accepted_review_row_count']}")
    print(f"- source_env_var: {action['source_env_var']}")
    print(f"- can_route_to_claim_scope_patch_draft: {downstream['can_route_to_claim_scope_patch_draft']}")
    print(f"packet: {OUT_PATH}")
    print(f"report: {REPORT_PATH}")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _project_relative(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def _report_md(packet: dict[str, Any]) -> str:
    metadata = packet["operator_packet_metadata"]
    action = packet["operator_action"]
    contract = packet["response_contract"]
    downstream = packet["downstream_state"]
    boundary = packet["boundary"]
    lines = [
        "# Formal Search Nonlegal Review Operator Packet",
        "",
        "## Position",
        "",
        (
            "This packet is a machine-readable handoff for the human nonlegal technical "
            "comparison stage. It consolidates the R8u134 AI brief, Agent60 response "
            "template, source preflight and review readiness state into one operator "
            "surface. It is not legal advice, not a prior-art conclusion, not claim text "
            "and not field evidence."
        ),
        "",
        "## Packet State",
        "",
        f"- packet_id: `{metadata['packet_id']}`",
        f"- packet_status: `{metadata['packet_status']}`",
        f"- linked_ai_brief_status: `{metadata['linked_ai_brief_status']}`",
        f"- linked_review_readiness_status: `{metadata['linked_review_readiness_status']}`",
        f"- upstream_source_env_var: `{action['upstream_source_env_var']}`",
        f"- upstream_formal_search_result_package_path: `{action['upstream_formal_search_result_package_path']}`",
        f"- source_env_var: `{action['source_env_var']}`",
        f"- recommended_output_path: `{action['recommended_output_path']}`",
        f"- expected_review_packet_row_count: `{action['expected_review_packet_row_count']}`",
        f"- high_priority_review_row_count: `{action['high_priority_review_row_count']}`",
        f"- accepted_review_row_count: `{action['accepted_review_row_count']}`",
        f"- can_route_to_claim_scope_patch_draft: `{downstream['can_route_to_claim_scope_patch_draft']}`",
        "",
        "## Required Response Contract",
        "",
        f"- required_root_keys: `{contract['required_root_keys']}`",
        f"- contract_basis: `{contract['contract_basis']}`",
        f"- review_metadata_required_fields: `{contract['review_metadata_required_fields']}`",
        f"- review_row_required_fields: `{contract['review_row_required_fields']}`",
        f"- expected_review_packet_row_id_count: `{contract['expected_review_packet_row_id_count']}`",
        "",
        "## Human Review Rows",
        "",
        "| row | work package | risk tier | AI starting option | required human fields |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in packet["human_review_rows"]:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | {} |".format(
                row["review_packet_row_id"],
                row["linked_work_package_id"],
                row["risk_tier_for_human_triage"],
                row["ai_suggested_nonlegal_starting_option"],
                ", ".join(f"`{field}`" for field in row["required_human_fields"]),
            )
        )
    lines.extend(
        [
            "",
            "## Operator Checklist",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in packet["pre_submission_checklist"])
    lines.extend(
        [
            "",
            "## Rejection Conditions",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in packet["rejection_conditions"])
    lines.extend(
        [
            "",
            "## Validation Commands",
            "",
        ]
    )
    lines.extend(f"- `{command}`" for command in action["validation_commands"])
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            f"- can_emit_claim_text: `{boundary['can_emit_claim_text']}`",
            f"- legal_opinion_allowed: `{boundary['legal_opinion_allowed']}`",
            f"- field_claim_upgrade_allowed: `{boundary['field_claim_upgrade_allowed']}`",
            f"- can_write_to_actuator: `{boundary['can_write_to_actuator']}`",
            f"- can_write_to_release_gate: `{boundary['can_write_to_release_gate']}`",
            f"- boundary_statement: {boundary['boundary_statement']}",
            "",
        ]
    )
    return "\n".join(lines)


def _update_manifest(packet: dict[str, Any]) -> None:
    manifest = _read_json(MANIFEST_PATH)
    metadata = packet["operator_packet_metadata"]
    action = packet["operator_action"]
    downstream = packet["downstream_state"]
    boundary = packet["boundary"]
    manifest["latest_formal_search_nonlegal_review_operator_packet"] = _project_relative(
        OUT_PATH
    )
    manifest["latest_formal_search_nonlegal_review_operator_packet_report"] = _project_relative(
        REPORT_PATH
    )
    manifest["latest_formal_search_nonlegal_review_operator_packet_status"] = metadata[
        "packet_status"
    ]
    manifest["latest_formal_search_nonlegal_review_operator_packet_expected_review_packet_row_count"] = (
        action["expected_review_packet_row_count"]
    )
    manifest["latest_formal_search_nonlegal_review_operator_packet_high_priority_review_row_count"] = (
        action["high_priority_review_row_count"]
    )
    manifest["latest_formal_search_nonlegal_review_operator_packet_accepted_review_row_count"] = (
        action["accepted_review_row_count"]
    )
    manifest["latest_formal_search_nonlegal_review_operator_packet_source_env_var"] = action[
        "source_env_var"
    ]
    manifest["latest_formal_search_nonlegal_review_operator_packet_upstream_source_env_var"] = action[
        "upstream_source_env_var"
    ]
    manifest["latest_formal_search_nonlegal_review_operator_packet_upstream_formal_search_result_package_path"] = action[
        "upstream_formal_search_result_package_path"
    ]
    manifest["latest_formal_search_nonlegal_review_operator_packet_contract_basis"] = packet[
        "response_contract"
    ]["contract_basis"]
    manifest["latest_formal_search_nonlegal_review_operator_packet_can_route_to_claim_scope_patch_draft"] = (
        downstream["can_route_to_claim_scope_patch_draft"]
    )
    manifest["latest_formal_search_nonlegal_review_operator_packet_can_emit_claim_text"] = boundary[
        "can_emit_claim_text"
    ]
    manifest["latest_formal_search_nonlegal_review_operator_packet_legal_opinion_allowed"] = boundary[
        "legal_opinion_allowed"
    ]
    manifest["latest_formal_search_nonlegal_review_operator_packet_field_claim_upgrade_allowed"] = (
        boundary["field_claim_upgrade_allowed"]
    )
    manifest["latest_formal_search_nonlegal_review_operator_packet_can_write_to_actuator"] = (
        boundary["can_write_to_actuator"]
    )
    manifest["latest_formal_search_nonlegal_review_operator_packet_can_write_to_release_gate"] = (
        boundary["can_write_to_release_gate"]
    )
    _write_json(MANIFEST_PATH, manifest)


def _upstream_formal_search_result_package_path() -> str:
    handoff = _read_json(PRELIMINARY_FORMAL_SEARCH_HANDOFF_PATH)
    if handoff.get("handoff_status") != (
        "preliminary_formal_search_package_ready_for_FORMAL_SEARCH_RESULT_PACKAGE_PATH"
    ):
        return ""
    return _local_project_path_from_handoff(str(handoff.get("package_path", "")))


def _local_project_path_from_handoff(package_path: str) -> str:
    if not package_path:
        return ""
    path = Path(package_path)
    for legacy_root in LEGACY_PROJECT_ROOTS:
        try:
            relative_path = path.relative_to(legacy_root)
        except ValueError:
            continue
        return str(PROJECT_ROOT / relative_path)
    return package_path


if __name__ == "__main__":
    main()
