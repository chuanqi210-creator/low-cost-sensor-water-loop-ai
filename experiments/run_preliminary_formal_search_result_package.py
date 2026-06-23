from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from water_ai.agents.agent_architecture_consolidation_agent import (
    AGENT_MODULE_MAP,
    AgentArchitectureConsolidationAgent,
)
from water_ai.preliminary_formal_search_package import (
    build_preliminary_formal_search_handoff,
    build_preliminary_formal_search_result_package,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
ROUTE_PLAN_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "agent_architecture_consolidation"
    / "formal_search_execution_route_plan.json"
)
OUT_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "agent_architecture_consolidation"
    / "preliminary_formal_search_result_package.json"
)
HANDOFF_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "agent_architecture_consolidation"
    / "preliminary_formal_search_handoff.json"
)
VALIDATION_SUMMARY_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "agent_architecture_consolidation"
    / "preliminary_formal_search_result_package_validation_summary.json"
)
REPORT_PATH = (
    PROJECT_ROOT
    / "deliverables"
    / "model_core_optimization"
    / "preliminary_formal_search_result_package.md"
)


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    route_plan = _read_json(ROUTE_PLAN_PATH)
    package = build_preliminary_formal_search_result_package(route_plan)
    handoff = build_preliminary_formal_search_handoff(package, package_path=str(OUT_PATH))
    validation_summary = _validate_package(OUT_PATH, package)

    OUT_PATH.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")
    HANDOFF_PATH.write_text(json.dumps(handoff, ensure_ascii=False, indent=2), encoding="utf-8")
    VALIDATION_SUMMARY_PATH.write_text(
        json.dumps(validation_summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    REPORT_PATH.write_text(_report_md(package, handoff, validation_summary), encoding="utf-8")
    _update_manifest(package, handoff, validation_summary)

    summary = package["_preflight_summary"]
    print(f"Preliminary formal search package: {summary['package_status']}")
    print(f"- filled_work_package_count: {summary['filled_work_package_count']}")
    print(f"- expected_work_package_count: {summary['expected_work_package_count']}")
    print(f"- source_preflight: {validation_summary['source_preflight_status']}")
    print(f"- row_preflight: {validation_summary['row_preflight_status']}")
    print(f"- validation_execution: {validation_summary['validation_execution_status']}")
    print(f"- can_enter_human_nonlegal_comparison_review: {validation_summary['can_enter_human_nonlegal_comparison_review']}")
    print(f"package: {OUT_PATH}")
    print(f"handoff: {HANDOFF_PATH}")
    print(f"report: {REPORT_PATH}")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_package(path: Path, package: dict[str, Any]) -> dict[str, object]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")
    report = AgentArchitectureConsolidationAgent(
        agent_names=list(AGENT_MODULE_MAP),
        formal_search_result_package_path=str(path),
    ).run([])
    source_preflight = report.metrics["formal_search_result_package_source_preflight"]
    row_preflight = report.metrics["formal_search_result_package_row_preflight"]
    validation_execution = report.metrics["formal_search_result_validation_execution"]
    nonlegal_packet = report.metrics["formal_search_nonlegal_comparison_review_packet"]
    return {
        "source_preflight_status": source_preflight["formal_search_result_package_source_status"],
        "source_can_route_to_validation_gate": source_preflight["can_route_to_validation_gate"],
        "source_template_marker_gap_count": source_preflight["template_marker_gap_count"],
        "row_preflight_status": row_preflight["formal_search_result_package_row_preflight_status"],
        "checked_work_package_count": row_preflight["checked_work_package_count"],
        "checked_hit_row_count": row_preflight["checked_hit_row_count"],
        "checked_comparison_row_count": row_preflight["checked_comparison_row_count"],
        "checked_fallback_row_count": row_preflight["checked_fallback_row_count"],
        "row_gap_count": row_preflight["row_gap_count"],
        "comparison_coverage_gap_count": row_preflight["comparison_coverage_gap_count"],
        "forbidden_review_boundary_count": row_preflight["forbidden_review_boundary_count"],
        "row_can_route_to_validation_gate": row_preflight["can_route_to_validation_gate"],
        "validation_execution_status": validation_execution[
            "formal_search_result_validation_execution_status"
        ],
        "validated_hit_count": validation_execution["validated_hit_count"],
        "rejected_hit_count": validation_execution["rejected_hit_count"],
        "can_enter_human_nonlegal_comparison_review": validation_execution[
            "can_enter_human_nonlegal_comparison_review"
        ],
        "nonlegal_review_packet_status": nonlegal_packet[
            "formal_search_nonlegal_comparison_review_packet_status"
        ],
        "nonlegal_review_packet_row_count": nonlegal_packet["review_packet_row_count"],
        "can_generate_prior_art_result": validation_execution["can_generate_prior_art_result"],
        "legal_opinion_allowed": validation_execution["legal_opinion_allowed"],
        "field_claim_upgrade_allowed": validation_execution["field_claim_upgrade_allowed"],
    }


def _report_md(
    package: dict[str, Any],
    handoff: dict[str, object],
    validation_summary: dict[str, object],
) -> str:
    summary = package["_preflight_summary"]
    metadata = package["package_metadata"]
    lines = [
        "# Preliminary Formal Search Result Package",
        "",
        "## 定位",
        "",
        (
            "该包把当前阶段门允许的 `FORMAL_SEARCH_RESULT_PACKAGE_PATH` 通道推进一步："
            "用真实公开来源填充 7 个 formal search work package 的初步比较记录。"
            "它只用于 Agent60 预检和人工非法律技术比较，不是专利结论，也不是现场证据。"
        ),
        "",
        "## Package Summary",
        "",
        f"- package_id: `{metadata['package_id']}`",
        f"- package_status: `{summary['package_status']}`",
        f"- filled_work_package_count: `{summary['filled_work_package_count']}`",
        f"- expected_work_package_count: `{summary['expected_work_package_count']}`",
        f"- source_env_var: `{handoff['source_env_var']}`",
        f"- package_path: `{handoff['package_path']}`",
        f"- can_route_to_agent60_formal_search_preflight: `{summary['can_route_to_agent60_formal_search_preflight']}`",
        f"- can_generate_prior_art_result: `{summary['can_generate_prior_art_result']}`",
        f"- legal_opinion_allowed: `{summary['legal_opinion_allowed']}`",
        f"- field_claim_upgrade_allowed: `{summary['field_claim_upgrade_allowed']}`",
        "",
        "## Validation Summary",
        "",
        f"- source_preflight_status: `{validation_summary['source_preflight_status']}`",
        f"- row_preflight_status: `{validation_summary['row_preflight_status']}`",
        f"- validation_execution_status: `{validation_summary['validation_execution_status']}`",
        f"- checked_work_package_count: `{validation_summary['checked_work_package_count']}`",
        f"- validated_hit_count: `{validation_summary['validated_hit_count']}`",
        f"- rejected_hit_count: `{validation_summary['rejected_hit_count']}`",
        f"- can_enter_human_nonlegal_comparison_review: `{validation_summary['can_enter_human_nonlegal_comparison_review']}`",
        "",
        "## Handoff Commands",
        "",
    ]
    for command in handoff["validation_commands"]:
        lines.append(f"- `{command}`")
    lines.extend(
        [
            "",
            "## Work Package Hits",
            "",
            "| work package | source database | title | source |",
            "| --- | --- | --- | --- |",
        ]
    )
    for work_package_id, result in package["work_package_results"].items():
        hit = result["prior_art_hit_table"][0]
        lines.append(
            "| `{}` | `{}` | {} | {} |".format(
                work_package_id,
                hit["source_database"],
                hit["title"],
                hit["url_or_reference"],
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            (
                "通过该包只能进入 Agent60 formal search validation 和人工非法律技术比较；"
                "仍不能写 actuator、release gate、权利要求文本或现场结论。"
            ),
            "",
        ]
    )
    return "\n".join(lines)


def _update_manifest(
    package: dict[str, Any],
    handoff: dict[str, object],
    validation_summary: dict[str, object],
) -> None:
    manifest = _read_json(MANIFEST_PATH)
    summary = package["_preflight_summary"]
    manifest["latest_preliminary_formal_search_result_package"] = str(
        OUT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_preliminary_formal_search_result_package_status"] = summary[
        "package_status"
    ]
    manifest["latest_preliminary_formal_search_result_package_filled_work_package_count"] = summary[
        "filled_work_package_count"
    ]
    manifest["latest_preliminary_formal_search_result_package_expected_work_package_count"] = summary[
        "expected_work_package_count"
    ]
    manifest["latest_preliminary_formal_search_handoff"] = str(
        HANDOFF_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_preliminary_formal_search_handoff_status"] = handoff[
        "handoff_status"
    ]
    manifest["latest_preliminary_formal_search_package_validation_summary"] = str(
        VALIDATION_SUMMARY_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_preliminary_formal_search_source_preflight_status"] = validation_summary[
        "source_preflight_status"
    ]
    manifest["latest_preliminary_formal_search_row_preflight_status"] = validation_summary[
        "row_preflight_status"
    ]
    manifest["latest_preliminary_formal_search_validation_execution_status"] = validation_summary[
        "validation_execution_status"
    ]
    manifest["latest_preliminary_formal_search_can_enter_human_nonlegal_comparison_review"] = (
        validation_summary["can_enter_human_nonlegal_comparison_review"]
    )
    manifest["latest_preliminary_formal_search_can_generate_prior_art_result"] = (
        validation_summary["can_generate_prior_art_result"]
    )
    manifest["latest_preliminary_formal_search_legal_opinion_allowed"] = (
        validation_summary["legal_opinion_allowed"]
    )
    manifest["latest_preliminary_formal_search_field_claim_upgrade_allowed"] = (
        validation_summary["field_claim_upgrade_allowed"]
    )
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
