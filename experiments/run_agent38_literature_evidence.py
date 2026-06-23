from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.literature_evidence_agent import LiteratureEvidenceAgent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
AGENT37_REPORT = PROJECT_ROOT / "outputs" / "agent37_knowledge_graph_curation" / "agent37_report.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent38_literature_evidence"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    kg_metrics = _read_kg_metrics()
    report = LiteratureEvidenceAgent(kg_curation_metrics=kg_metrics).run([])
    generated_files = {
        "literature_evidence_matrix": str(DELIVERABLES_DIR / "literature_evidence_matrix.md"),
        "literature_evidence_schema": str(DELIVERABLES_DIR / "literature_evidence_schema.md"),
        "agent38_report": str(OUT_DIR / "agent38_report.md"),
        "literature_evidence_records": str(OUT_DIR / "literature_evidence_records.json"),
    }

    (DELIVERABLES_DIR / "literature_evidence_matrix.md").write_text(_matrix_md(report), encoding="utf-8")
    (DELIVERABLES_DIR / "literature_evidence_schema.md").write_text(_schema_md(report), encoding="utf-8")
    (OUT_DIR / "literature_evidence_records.json").write_text(
        json.dumps(report.metrics["evidence_records"], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    payload = {
        "literature_evidence": {
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
        },
        "generated_files": generated_files,
    }
    (OUT_DIR / "agent38_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "agent38_report.md").write_text(_report_md(report, generated_files), encoding="utf-8")
    _update_manifest(generated_files)

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent38_report.md'}")
    for key, path in generated_files.items():
        print(f"{key}: {path}")


def _read_kg_metrics() -> dict[str, object]:
    if not AGENT37_REPORT.exists():
        return {}
    payload = json.loads(AGENT37_REPORT.read_text(encoding="utf-8"))
    curation = payload.get("knowledge_graph_curation", {})
    if isinstance(curation, dict):
        metrics = curation.get("metrics", {})
        if isinstance(metrics, dict):
            return metrics
    return {}


def _matrix_md(report) -> str:
    readiness = report.metrics["readiness"]
    gap = report.metrics["kg_gap_closure"]
    lines = [
        "# 文献证据矩阵",
        "",
        f"- literature_evidence_status：`{readiness['literature_evidence_status']}`",
        f"- literature_evidence_score：`{readiness['literature_evidence_score']}`",
        f"- record_count：`{readiness['record_count']}`",
        f"- kg_gap_closure_score：`{readiness['kg_gap_closure_score']}`",
        f"- field_supported_record_count：`{readiness['field_supported_record_count']}`",
        "",
        "## KG 缺口覆盖",
        "",
        f"- covered_missing：`{gap['covered_missing']}`",
        f"- remaining_missing：`{gap['remaining_missing']}`",
        "",
        "## 文献记录",
        "",
        "| citation_key | 年份 | 借鉴点 | 项目映射 | 数据需求 | 失败边界 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for record in report.metrics["evidence_records"]:
        lines.append(
            "| `{citation}` | `{year}` | {borrowed} | {mapping} | {data} | {boundary} |".format(
                citation=record["citation_key"],
                year=record["year"],
                borrowed=record["borrowed_idea"],
                mapping=record["project_mapping"],
                data=", ".join(record["data_requirements"]),
                boundary=record["failure_boundary"],
            )
        )
    lines.extend(["", "## 模型升级映射", ""])
    for upgrade in report.metrics["model_upgrade_map"]:
        lines.append(f"- `{upgrade['upgrade_id']}`：{upgrade['reality_mapping']}")
        lines.append(f"  - borrowed_from：{', '.join(upgrade['borrowed_from'])}")
        lines.append(f"  - data_needs：{', '.join(upgrade['data_needs'])}")
        lines.append(f"  - metrics：{', '.join(upgrade['evaluation_metrics'])}")
        lines.append(f"  - failure_boundary：{upgrade['failure_boundary']}")
    lines.extend(["", "## 结论", ""])
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    return "\n".join(lines)


def _schema_md(report) -> str:
    lines = [
        "# Literature Evidence Extraction Schema",
        "",
        "该 schema 用于把文献转成可写入 Scientific KG 和模型升级 backlog 的结构化记录。",
        "",
        "| 字段 | 为什么需要 | 服务对象 |",
        "| --- | --- | --- |",
    ]
    for field in report.metrics["extraction_schema"]:
        lines.append(
            f"| `{field['field']}` | {field['why']} | {', '.join(field['required_for'])} |"
        )
    lines.extend(["", "## Sources", ""])
    for record in report.metrics["evidence_records"]:
        lines.append(f"- `{record['citation_key']}`：{record['title']} ({record['year']}), {record['source_url']}")
    lines.extend(["", "## 强制边界", ""])
    lines.append("- `literature_supported` 只能作为模型升级假设或 KG seed。")
    lines.append("- 任何参数写回、release gate 修改或 field 结论，必须另有真实数据 G0-G5 验收。")
    lines.append("- 摘要/元数据级记录必须在进入参数范围前做全文表格化抽取。")
    return "\n".join(lines)


def _report_md(report, generated_files: dict[str, str]) -> str:
    readiness = report.metrics["readiness"]
    lines = [
        "# Agent 38 文献证据抽取报告",
        "",
        f"- summary: {report.summary}",
        f"- literature_evidence_status: `{readiness['literature_evidence_status']}`",
        f"- literature_evidence_score: `{readiness['literature_evidence_score']}`",
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


def _update_manifest(generated_files: dict[str, str]) -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    relative_generated = {
        key: str(Path(path).relative_to(PROJECT_ROOT))
        for key, path in generated_files.items()
    }
    manifest["status"] = "文献证据抽取层已生成"
    manifest["literature_evidence"] = relative_generated
    manifest["next_stage"] = "按 literature_evidence_matrix.md 推进软传感 field conformal calibration、灰箱动态控制延迟和 field-supported KG edges"
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
