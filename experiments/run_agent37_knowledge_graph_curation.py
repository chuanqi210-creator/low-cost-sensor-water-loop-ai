from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.knowledge_graph_curation_agent import KnowledgeGraphCurationAgent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent37_knowledge_graph_curation"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    report = KnowledgeGraphCurationAgent().run([])
    generated_files = {
        "knowledge_graph_curation": str(DELIVERABLES_DIR / "knowledge_graph_curation.md"),
        "knowledge_graph_schema": str(DELIVERABLES_DIR / "knowledge_graph_schema.md"),
        "agent37_report": str(OUT_DIR / "agent37_report.md"),
        "knowledge_graph_records": str(OUT_DIR / "knowledge_graph_records.json"),
    }

    (DELIVERABLES_DIR / "knowledge_graph_curation.md").write_text(_curation_md(report), encoding="utf-8")
    (DELIVERABLES_DIR / "knowledge_graph_schema.md").write_text(_schema_md(report), encoding="utf-8")
    (OUT_DIR / "knowledge_graph_records.json").write_text(
        json.dumps(report.metrics["graph_records"], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    payload = {
        "knowledge_graph_curation": {
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
    (OUT_DIR / "agent37_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "agent37_report.md").write_text(_report_md(report, generated_files), encoding="utf-8")
    _update_manifest(generated_files)

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent37_report.md'}")
    for key, path in generated_files.items():
        print(f"{key}: {path}")


def _curation_md(report) -> str:
    readiness = report.metrics["readiness"]
    evidence = report.metrics["evidence_audit"]
    lines = [
        "# 知识图谱策展审计",
        "",
        f"- kg_curation_status：`{readiness['kg_curation_status']}`",
        f"- kg_curation_score：`{readiness['kg_curation_score']}`",
        f"- axis_coverage_score：`{readiness['axis_coverage_score']}`",
        f"- evidence_score：`{readiness['evidence_score']}`",
        f"- raw_signal_grounding_score：`{readiness['raw_signal_grounding_score']}`",
        f"- entry_count：`{readiness['entry_count']}`",
        f"- field_supported_entry_count：`{evidence['field_supported_entry_count']}`",
        "",
        "## 轴覆盖",
        "",
        "| 轴 | 覆盖率 | 已覆盖 | 缺口 |",
        "| --- | --- | --- | --- |",
    ]
    for axis_name, axis in report.metrics["axis_coverage"].items():
        lines.append(
            f"| `{axis_name}` | `{axis['coverage']}` | {', '.join(axis['covered']) or '无'} | {', '.join(axis['missing']) or '无'} |"
        )
    lines.extend(["", "## 证据等级", ""])
    for key, value in evidence["evidence_counts"].items():
        lines.append(f"- `{key}`：{value}")
    lines.extend(["", "## 模型改进 Backlog", ""])
    for item in report.metrics["kg_upgrade_backlog"]:
        lines.append(f"- `{item['priority']}` `{item['work_id']}`：{item['title']}；原因：{item['why']}")
    lines.extend(["", "## 结论", ""])
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    return "\n".join(lines)


def _schema_md(report) -> str:
    lines = [
        "# Scientific Knowledge Graph Schema",
        "",
        "## 节点层",
        "",
        "- `Pollutant`：污染物类型、代表化合物、检测限、目标标签。",
        "- `WaterMatrix`：COD、盐度、pH、浊度、天然有机质、共存离子。",
        "- `MaterialSystem`：催化剂、吸附剂、膜、AOP、光/电催化、生物耦合。",
        "- `ProcessCondition`：停留时间、剂量、光照/电流、pH、温度、流量、再生周期。",
        "- `ObservableSignal`：pH、ORP、电导、浊度、UV254、流量、温度。",
        "- `HiddenState`：残留风险、反应完成度、副产物风险、催化剂活性、基质抑制。",
        "- `ControlAction`：暂存验证、回流、加药、预处理/切换、再生、更换、放行。",
        "- `Evidence`：文献支持、仿真支持、真实数据支持、仅假设。",
        "",
        "## 关键边",
        "",
        "- `Pollutant -affected_by-> WaterMatrix`",
        "- `WaterMatrix -modulates-> Mechanism`",
        "- `MaterialSystem -implements-> Mechanism`",
        "- `ProcessCondition -controls-> HiddenState`",
        "- `ObservableSignal -estimates-> HiddenState`",
        "- `HiddenState -triggers-> ControlAction`",
        "- `Evidence -supports_or_blocks-> TypedEdge`",
        "",
        "## 科学审查链",
        "",
        "| Agent | 职责 | 借鉴 workflow | 输出契约 |",
        "| --- | --- | --- | --- |",
    ]
    for item in report.metrics["scientific_review_chain"]:
        lines.append(
            f"| `{item['agent']}` | {item['role']} | `{item['borrowed_skill_pattern']}` | {', '.join(item['output_contract'])} |"
        )
    lines.extend(["", "## 强制边界", ""])
    lines.append("- `simulation` 和 `literature` 边可以影响候选动作排序，但不能作为 field parameter writeback。")
    lines.append("- `field` 边必须经过 G0-G5 数据来源和质量门控后，才能进入软传感重训或控制参数校准。")
    lines.append("- 所有可宣称结论必须带 `evidence_stage`、`source_basis`、`field_validation_need` 和 `claim_boundary`。")
    return "\n".join(lines)


def _report_md(report, generated_files: dict[str, str]) -> str:
    readiness = report.metrics["readiness"]
    lines = [
        "# Agent 37 知识图谱策展报告",
        "",
        f"- summary: {report.summary}",
        f"- kg_curation_status: `{readiness['kg_curation_status']}`",
        f"- kg_curation_score: `{readiness['kg_curation_score']}`",
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
    manifest["status"] = "知识图谱策展层已生成"
    manifest["knowledge_graph_curation"] = relative_generated
    manifest["next_stage"] = "按 knowledge_graph_curation.md 补文献证据抽取、原始信号边和真实 field-supported KG edges"
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
