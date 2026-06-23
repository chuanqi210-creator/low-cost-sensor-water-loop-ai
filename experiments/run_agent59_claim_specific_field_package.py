from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from water_ai.agents.claim_specific_field_package_agent import ClaimSpecificFieldPackageAgent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
KG_METRICS_PATH = PROJECT_ROOT / "outputs" / "knowledge_graph_reasoning" / "kg_reasoning_metrics.json"
UNIFIED_FIELD_EVIDENCE_GATE_METRICS_PATH = (
    PROJECT_ROOT / "outputs" / "unified_field_evidence_gate" / "unified_field_evidence_gate_metrics.json"
)
FIELD_VALIDATION_ALIGNMENT_METRICS_PATH = PROJECT_ROOT / "outputs" / "field_validation_queue_alignment" / "field_validation_queue_alignment_metrics.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent59_claim_specific_field_package"
METRICS_DIR = PROJECT_ROOT / "outputs" / "claim_specific_field_package"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables"
METRICS_PATH = METRICS_DIR / "claim_specific_field_package_metrics.json"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)

    kg_metrics = _read_optional_json(KG_METRICS_PATH)
    unified_gate_metrics = _read_optional_json(UNIFIED_FIELD_EVIDENCE_GATE_METRICS_PATH)
    if isinstance(unified_gate_metrics.get("source_basis_detail_library"), dict):
        kg_metrics = {
            **kg_metrics,
            "source_basis_detail_library": unified_gate_metrics["source_basis_detail_library"],
        }
    alignment_metrics = _read_optional_json(FIELD_VALIDATION_ALIGNMENT_METRICS_PATH)
    mapping_table = alignment_metrics.get("validation_mapping_table", [])
    field_package_status = alignment_metrics.get("field_package_status", {})
    if isinstance(field_package_status, dict):
        coverage = alignment_metrics.get("coverage", {})
        readiness = alignment_metrics.get("readiness", {})
        if isinstance(coverage, dict):
            field_package_status = {
                **field_package_status,
                "guardrail_requirement_patch_count": coverage.get("guardrail_requirement_patch_count", 0),
            }
        if isinstance(readiness, dict):
            field_package_status = {
                **field_package_status,
                "field_requirement_patch_consumption_rate": readiness.get("field_requirement_patch_consumption_rate", 0.0),
            }
    report = ClaimSpecificFieldPackageAgent(
        validation_mapping_table=mapping_table if isinstance(mapping_table, list) else [],
        kg_reasoning_metrics=kg_metrics,
        field_package_status=field_package_status if isinstance(field_package_status, dict) else {},
    ).run([])

    metrics_payload = {
        "method_contract": report.metrics["method_contract"],
        "minimal_field_package_matrix": report.metrics["minimal_field_package_matrix"],
        "source_basis_completion_tasks": report.metrics["source_basis_completion_tasks"],
        "readiness": report.metrics["readiness"],
        "agent50_writeback": report.metrics["agent50_writeback"],
    }
    METRICS_PATH.write_text(json.dumps(metrics_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    generated_files = {
        "claim_specific_field_package": str(DELIVERABLES_DIR / "claim_specific_field_package.md"),
        "agent59_report": str(OUT_DIR / "agent59_report.md"),
        "claim_specific_field_package_metrics": str(METRICS_PATH),
    }
    (DELIVERABLES_DIR / "claim_specific_field_package.md").write_text(
        _deliverable_md(report),
        encoding="utf-8",
    )
    (OUT_DIR / "agent59_report.md").write_text(
        _report_md(report, generated_files),
        encoding="utf-8",
    )
    (OUT_DIR / "agent59_report.json").write_text(
        json.dumps(
            {
                "claim_specific_field_package": _report_payload(report),
                "generated_files": generated_files,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    _update_manifest(generated_files, report)

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    for key, path in generated_files.items():
        print(f"{key}: {path}")


def _read_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _deliverable_md(report) -> str:
    readiness = report.metrics["readiness"]
    lines = [
        "# Claim-Specific 现场采集包",
        "",
        f"- claim_specific_package_status：`{readiness['claim_specific_package_status']}`",
        f"- claim_specific_required_field_coverage：`{readiness['claim_specific_required_field_coverage']}`",
        f"- minimal_field_package_schema_pass_rate：`{readiness['minimal_field_package_schema_pass_rate']}`",
        f"- minimal_field_package_field_pass_rate：`{readiness['minimal_field_package_field_pass_rate']}`",
        f"- source_basis_completion_rate：`{readiness['source_basis_completion_rate']}`",
        f"- field_requirement_patch_consumption_rate：`{readiness['field_requirement_patch_consumption_rate']}`",
        f"- unmet_guardrail_field_count：`{readiness['unmet_guardrail_field_count']}`",
        f"- field_claim_upgrade_blocker_count：`{readiness['field_claim_upgrade_blocker_count']}`",
        f"- can_write_to_actuator：`{readiness['can_write_to_actuator']}`",
        f"- can_write_to_release_gate：`{readiness['can_write_to_release_gate']}`",
        "",
        "## Minimal Field Package Matrix",
        "",
        "| Need | Required Fields | Metadata | Gates | Blockers |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in report.metrics["minimal_field_package_matrix"]:
        lines.append(
            f"| `{row['field_validation_need']}` | `{row['claim_specific_required_fields']}` | "
            f"`{row['metadata_required_fields']}` | `{row['replay_gate_ids']}` | `{row['claim_upgrade_blocked_by']}` |"
        )
    lines.extend(["", "## Source Basis Completion Tasks", ""])
    for task in report.metrics["source_basis_completion_tasks"]:
        lines.append(
            f"- `{task['entry_id']}`：current={task['current_source_basis']}；"
            f"required_patch={task['required_patch']}"
        )
    lines.extend(["", "## 结论边界", ""])
    for issue in report.issues:
        lines.append(f"- `{issue.issue_type}`：{issue.message}")
    return "\n".join(lines)


def _report_md(report, generated_files: dict[str, str]) -> str:
    readiness = report.metrics["readiness"]
    lines = [
        "# Agent 59 Claim-Specific Field Package 报告",
        "",
        f"- summary: {report.summary}",
        f"- claim_specific_package_status: `{readiness['claim_specific_package_status']}`",
        f"- source_basis_completion_rate: `{readiness['source_basis_completion_rate']}`",
        f"- field_requirement_patch_consumption_rate: `{readiness['field_requirement_patch_consumption_rate']}`",
        f"- unmet_guardrail_field_count: `{readiness['unmet_guardrail_field_count']}`",
        f"- field_claim_upgrade_blocker_count: `{readiness['field_claim_upgrade_blocker_count']}`",
        "",
        "## 生成文件",
        "",
    ]
    for key, path in generated_files.items():
        lines.append(f"- {key}: `{path}`")
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


def _update_manifest(generated_files: dict[str, str], report) -> None:
    manifest = _read_optional_json(MANIFEST_PATH)
    manifest["status"] = "Agent59 已将 R4 guardrail required fields 保留到 claim-specific field package"
    manifest["claim_specific_field_package"] = {
        key: str(Path(path).relative_to(PROJECT_ROOT))
        for key, path in generated_files.items()
    }
    manifest["latest_claim_specific_package_status"] = report.metrics["readiness"]["claim_specific_package_status"]
    manifest["latest_agent59_field_requirement_patch_consumption_rate"] = str(
        report.metrics["readiness"]["field_requirement_patch_consumption_rate"]
    )
    manifest["latest_agent59_unmet_guardrail_field_count"] = int(report.metrics["readiness"]["unmet_guardrail_field_count"])
    manifest["next_stage"] = (
        "R4b 已让 Agent53/58/59 消费 R4 patches；下一轮应按 Agent60 判断，优先补 unmet_guardrail_fields 的 field schema/replay schema。"
    )
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
