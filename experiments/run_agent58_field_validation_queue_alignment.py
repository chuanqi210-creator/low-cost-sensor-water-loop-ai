from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from water_ai.agents.field_validation_queue_alignment_agent import FieldValidationQueueAlignmentAgent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
KG_METRICS_PATH = PROJECT_ROOT / "outputs" / "knowledge_graph_reasoning" / "kg_reasoning_metrics.json"
FIELD_DATA_REPORT_PATH = PROJECT_ROOT / "outputs" / "agent30_field_data_interface" / "agent30_report.json"
TIMESTAMPED_REPLAY_REPORT_PATH = PROJECT_ROOT / "outputs" / "agent42_timestamped_campaign_replay" / "agent42_report.json"
FIELD_REPLAY_IMPORT_METRICS_PATH = PROJECT_ROOT / "outputs" / "field_replay_import" / "import_acceptance_metrics.json"
EVIDENCE_CHAIN_METRICS_PATH = PROJECT_ROOT / "outputs" / "field_replay_evidence_chain" / "evidence_chain_metrics.json"
CONTROL_GUARDRAIL_BACKPROP_METRICS_PATH = (
    PROJECT_ROOT / "outputs" / "control_guardrail_backpropagation" / "control_guardrail_backpropagation_metrics.json"
)
OUT_DIR = PROJECT_ROOT / "outputs" / "agent58_field_validation_queue_alignment"
METRICS_DIR = PROJECT_ROOT / "outputs" / "field_validation_queue_alignment"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables"
METRICS_PATH = METRICS_DIR / "field_validation_queue_alignment_metrics.json"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)

    kg_metrics = _read_optional_json(KG_METRICS_PATH)
    field_data_metrics = _extract_report_metrics(_read_optional_json(FIELD_DATA_REPORT_PATH), "field_data_interface")
    timestamped_replay_metrics = _extract_report_metrics(
        _read_optional_json(TIMESTAMPED_REPLAY_REPORT_PATH),
        "timestamped_campaign_replay",
    )
    import_metrics = _read_optional_json(FIELD_REPLAY_IMPORT_METRICS_PATH)
    evidence_chain_metrics = _read_optional_json(EVIDENCE_CHAIN_METRICS_PATH)
    control_guardrail_backpropagation_metrics = _read_optional_json(CONTROL_GUARDRAIL_BACKPROP_METRICS_PATH)

    queue = kg_metrics.get("field_validation_queue", [])
    report = FieldValidationQueueAlignmentAgent(
        field_validation_queue=queue if isinstance(queue, list) else [],
        field_data_metrics=field_data_metrics,
        timestamped_replay_metrics=timestamped_replay_metrics,
        field_replay_import_metrics=import_metrics,
        evidence_chain_metrics=evidence_chain_metrics,
        control_guardrail_backpropagation_metrics=control_guardrail_backpropagation_metrics,
    ).run([])

    metrics_payload = {
        "method_contract": report.metrics["method_contract"],
        "validation_mapping_table": report.metrics["validation_mapping_table"],
        "field_package_status": report.metrics["field_package_status"],
        "coverage": report.metrics["coverage"],
        "readiness": report.metrics["readiness"],
        "agent50_writeback": report.metrics["agent50_writeback"],
    }
    METRICS_PATH.write_text(json.dumps(metrics_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    generated_files = {
        "field_validation_queue_alignment": str(DELIVERABLES_DIR / "field_validation_queue_alignment.md"),
        "agent58_report": str(OUT_DIR / "agent58_report.md"),
        "field_validation_queue_alignment_metrics": str(METRICS_PATH),
    }
    (DELIVERABLES_DIR / "field_validation_queue_alignment.md").write_text(
        _deliverable_md(report),
        encoding="utf-8",
    )
    (OUT_DIR / "agent58_report.md").write_text(
        _report_md(report, generated_files),
        encoding="utf-8",
    )
    (OUT_DIR / "agent58_report.json").write_text(
        json.dumps(
            {
                "field_validation_queue_alignment": _report_payload(report),
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


def _extract_report_metrics(payload: dict[str, Any], key: str) -> dict[str, object]:
    block = payload.get(key, {})
    if isinstance(block, dict):
        metrics = block.get("metrics", {})
        if isinstance(metrics, dict):
            return metrics
    metrics = payload.get("metrics", {})
    return metrics if isinstance(metrics, dict) else {}


def _deliverable_md(report) -> str:
    readiness = report.metrics["readiness"]
    status = report.metrics["field_package_status"]
    lines = [
        "# 现场验证队列对齐",
        "",
        f"- field_validation_alignment_status：`{readiness['field_validation_alignment_status']}`",
        f"- field_need_to_table_coverage：`{readiness['field_need_to_table_coverage']}`",
        f"- field_need_to_gate_coverage：`{readiness['field_need_to_gate_coverage']}`",
        f"- schema_extension_required_count：`{readiness['schema_extension_required_count']}`",
        f"- field_requirement_patch_consumption_rate：`{readiness['field_requirement_patch_consumption_rate']}`",
        f"- guardrail_missing_schema_field_count：`{readiness['guardrail_missing_schema_field_count']}`",
        f"- claim_upgrade_blocker_count：`{readiness['claim_upgrade_blocker_count']}`",
        f"- can_write_to_actuator：`{readiness['can_write_to_actuator']}`",
        f"- can_write_to_release_gate：`{readiness['can_write_to_release_gate']}`",
        "",
        "## Field Package Status",
        "",
    ]
    for key, value in status.items():
        lines.append(f"- {key}：`{value}`")
    lines.extend(
        [
            "",
            "## Validation Mapping Table",
            "",
            "| Need | Type | Agent30 Tables | Agent42 Tables | Agent43 Gates | Claim Fields | Boundary |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in report.metrics["validation_mapping_table"]:
        promoted = row["optional_fields_promoted_for_claim"]
        lines.append(
            f"| `{row['field_validation_need']}` | `{row['need_type']}` | "
            f"`{', '.join(row['agent30_tables'])}` | `{', '.join(row['agent42_replay_tables'])}` | "
            f"`{', '.join(row['agent43_gate_ids'])}` | `{promoted}` | {row['failure_boundary']} |"
        )
    lines.extend(["", "## 结论边界", ""])
    for issue in report.issues:
        lines.append(f"- `{issue.issue_type}`：{issue.message}")
    return "\n".join(lines)


def _report_md(report, generated_files: dict[str, str]) -> str:
    readiness = report.metrics["readiness"]
    lines = [
        "# Agent 58 现场验证队列对齐报告",
        "",
        f"- summary: {report.summary}",
        f"- field_validation_alignment_status: `{readiness['field_validation_alignment_status']}`",
        f"- field_need_to_table_coverage: `{readiness['field_need_to_table_coverage']}`",
        f"- field_need_to_gate_coverage: `{readiness['field_need_to_gate_coverage']}`",
        f"- unmapped_validation_need_count: `{readiness['unmapped_validation_need_count']}`",
        f"- field_requirement_patch_consumption_rate: `{readiness['field_requirement_patch_consumption_rate']}`",
        f"- guardrail_missing_schema_field_count: `{readiness['guardrail_missing_schema_field_count']}`",
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
    manifest["status"] = "Agent58 已消费 R4 field requirement patches 并映射到数据接口/replay gate"
    manifest["field_validation_queue_alignment"] = {
        key: str(Path(path).relative_to(PROJECT_ROOT))
        for key, path in generated_files.items()
    }
    manifest["latest_field_validation_alignment_status"] = report.metrics["readiness"]["field_validation_alignment_status"]
    manifest["latest_agent58_field_requirement_patch_consumption_rate"] = str(
        report.metrics["readiness"]["field_requirement_patch_consumption_rate"]
    )
    manifest["next_stage"] = (
        "继续推进 R4b：让 Agent59 将 R4 guardrail required fields 保留到 claim-specific field package；"
        "仍不得把 synthetic 对齐结果当作现场实证。"
    )
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
