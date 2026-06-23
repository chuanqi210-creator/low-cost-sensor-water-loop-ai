from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from water_ai.formal_search_nonlegal_review_brief import (
    build_formal_search_ai_nonlegal_review_brief,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
AGENT60_DIR = PROJECT_ROOT / "outputs" / "agent_architecture_consolidation"
PACKAGE_PATH = AGENT60_DIR / "preliminary_formal_search_result_package.json"
NONLEGAL_PACKET_PATH = AGENT60_DIR / "formal_search_nonlegal_comparison_review_packet.json"
CLAIM_SKELETON_PATH = AGENT60_DIR / "technical_claim_skeleton_scaffold.json"
OUT_PATH = AGENT60_DIR / "formal_search_ai_nonlegal_review_brief.json"
REPORT_PATH = (
    PROJECT_ROOT
    / "deliverables"
    / "model_core_optimization"
    / "formal_search_ai_nonlegal_review_brief.md"
)


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    package = _read_json(PACKAGE_PATH)
    nonlegal_packet = _read_json(NONLEGAL_PACKET_PATH)
    claim_skeleton = _read_json(CLAIM_SKELETON_PATH)
    brief = build_formal_search_ai_nonlegal_review_brief(
        preliminary_formal_search_result_package=package,
        nonlegal_comparison_review_packet=nonlegal_packet,
        technical_claim_skeleton_scaffold=claim_skeleton,
    )
    OUT_PATH.write_text(json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_PATH.write_text(_report_md(brief), encoding="utf-8")
    _update_manifest(brief)

    readiness = brief["review_readiness"]
    metadata = brief["brief_metadata"]
    print(f"Formal search AI nonlegal review brief: {metadata['brief_status']}")
    print(f"- brief_row_count: {readiness['brief_row_count']}")
    print(f"- missing_source_row_count: {readiness['missing_source_row_count']}")
    print(f"- missing_claim_mapping_row_count: {readiness['missing_claim_mapping_row_count']}")
    print(f"- can_help_human_nonlegal_review: {readiness['can_help_human_nonlegal_review']}")
    print(f"- can_route_to_claim_scope_patch_draft: {readiness['can_route_to_claim_scope_patch_draft']}")
    print(f"- legal_opinion_allowed: {readiness['legal_opinion_allowed']}")
    print(f"brief: {OUT_PATH}")
    print(f"report: {REPORT_PATH}")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _report_md(brief: dict[str, Any]) -> str:
    metadata = brief["brief_metadata"]
    readiness = brief["review_readiness"]
    lines = [
        "# Formal Search AI Nonlegal Review Brief",
        "",
        "## Position",
        "",
        (
            "This brief compresses the preliminary formal-search result package into a human "
            "nonlegal technical comparison aid. It is not a human review response, not legal "
            "advice, not a prior-art conclusion and not field evidence."
        ),
        "",
        "## Readiness",
        "",
        f"- brief_id: `{metadata['brief_id']}`",
        f"- brief_status: `{metadata['brief_status']}`",
        f"- brief_role: `{metadata['brief_role']}`",
        f"- review_packet_row_count: `{readiness['review_packet_row_count']}`",
        f"- brief_row_count: `{readiness['brief_row_count']}`",
        f"- missing_source_row_count: `{readiness['missing_source_row_count']}`",
        f"- missing_claim_mapping_row_count: `{readiness['missing_claim_mapping_row_count']}`",
        f"- can_help_human_nonlegal_review: `{readiness['can_help_human_nonlegal_review']}`",
        f"- can_route_to_claim_scope_patch_draft: `{readiness['can_route_to_claim_scope_patch_draft']}`",
        f"- legal_opinion_allowed: `{readiness['legal_opinion_allowed']}`",
        f"- field_claim_upgrade_allowed: `{readiness['field_claim_upgrade_allowed']}`",
        "",
        "## Human Review Triage Rows",
        "",
        "| row | work package | risk tier | suggested starting option | mapped claim scaffolds |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in brief["brief_rows"]:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | {} |".format(
                row["review_packet_row_id"],
                row["linked_work_package_id"],
                row["risk_tier_for_human_triage"],
                row["ai_suggested_nonlegal_starting_option"],
                ", ".join(f"`{claim}`" for claim in row["mapped_claim_scaffold_ids"]),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- The next valid operator action remains a human nonlegal review response.",
            "- Submit that response with `FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH`.",
            "- This brief cannot emit claim text, resume model control, write actuators or open a release gate.",
            "",
        ]
    )
    return "\n".join(lines)


def _update_manifest(brief: dict[str, Any]) -> None:
    manifest = _read_json(MANIFEST_PATH)
    metadata = brief["brief_metadata"]
    readiness = brief["review_readiness"]
    manifest["latest_formal_search_ai_nonlegal_review_brief"] = str(
        OUT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_formal_search_ai_nonlegal_review_brief_report"] = str(
        REPORT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_formal_search_ai_nonlegal_review_brief_status"] = metadata[
        "brief_status"
    ]
    manifest["latest_formal_search_ai_nonlegal_review_brief_row_count"] = readiness[
        "brief_row_count"
    ]
    manifest["latest_formal_search_ai_nonlegal_review_brief_missing_source_row_count"] = (
        readiness["missing_source_row_count"]
    )
    manifest["latest_formal_search_ai_nonlegal_review_brief_missing_claim_mapping_row_count"] = (
        readiness["missing_claim_mapping_row_count"]
    )
    manifest["latest_formal_search_ai_nonlegal_review_brief_can_help_human_review"] = (
        readiness["can_help_human_nonlegal_review"]
    )
    manifest["latest_formal_search_ai_nonlegal_review_brief_can_route_to_claim_scope_patch_draft"] = (
        readiness["can_route_to_claim_scope_patch_draft"]
    )
    manifest["latest_formal_search_ai_nonlegal_review_brief_legal_opinion_allowed"] = (
        readiness["legal_opinion_allowed"]
    )
    manifest["latest_formal_search_ai_nonlegal_review_brief_field_claim_upgrade_allowed"] = (
        readiness["field_claim_upgrade_allowed"]
    )
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
