from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.model_realism_audit_agent import ModelRealismAuditAgent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
TRAINING_METRICS = PROJECT_ROOT / "outputs" / "soft_sensor_training" / "soft_sensor_training_metrics.json"
UNCERTAINTY_METRICS = PROJECT_ROOT / "outputs" / "soft_sensor_training" / "soft_sensor_uncertainty_metrics.json"
AGENT34_REPORT = PROJECT_ROOT / "outputs" / "agent34_field_calibration_gate" / "agent34_report.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent35_model_realism_audit"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    manifest = _read_json(MANIFEST_PATH)
    training_metrics = _read_json(TRAINING_METRICS)
    if UNCERTAINTY_METRICS.exists():
        uncertainty_metrics = _read_json(UNCERTAINTY_METRICS)
        training_metrics["uncertainty_metrics"] = uncertainty_metrics.get("uncertainty_metrics", uncertainty_metrics)
        training_metrics["uncertainty_evidence_stage"] = uncertainty_metrics.get("evidence_stage", "unknown")
    agent34 = _read_json(AGENT34_REPORT)
    field_gate_metrics = agent34["field_calibration_gate"]["metrics"]
    report = ModelRealismAuditAgent(
        training_metrics=training_metrics,
        field_gate_metrics=field_gate_metrics,
        latest_regression=str(manifest.get("latest_regression", "145 passed")),
    ).run([])

    generated_files = {
        "model_realism_audit": str(DELIVERABLES_DIR / "model_realism_audit.md"),
        "model_upgrade_backlog": str(DELIVERABLES_DIR / "model_upgrade_backlog.md"),
        "agent35_report": str(OUT_DIR / "agent35_report.md"),
    }
    (DELIVERABLES_DIR / "model_realism_audit.md").write_text(_audit_md(report), encoding="utf-8")
    (DELIVERABLES_DIR / "model_upgrade_backlog.md").write_text(_backlog_md(report), encoding="utf-8")

    payload = {
        "source_reports": {
            "manifest": str(MANIFEST_PATH),
            "training_metrics": str(TRAINING_METRICS),
            "agent34": str(AGENT34_REPORT),
        },
        "model_realism_audit": {
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
    (OUT_DIR / "agent35_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "agent35_report.md").write_text(_report_md(report, generated_files), encoding="utf-8")
    _update_manifest(generated_files)

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent35_report.md'}")
    for key, path in generated_files.items():
        print(f"{key}: {path}")


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _audit_md(report) -> str:
    metrics = report.metrics
    knowledge = metrics["knowledge_audit"]
    validation = metrics["validation_audit"]
    field = metrics["field_audit"]
    process = metrics["process_audit"]
    readiness = metrics["readiness"]
    lines = [
        "# 模型真实性审计",
        "",
        f"- 当前状态：`{readiness['realism_status']}`",
        f"- realism_score：`{readiness['realism_score']}`",
        f"- 最新回归：`{metrics['latest_regression']}`",
        "",
        "## 1. 知识库审计",
        "",
        f"- 条目数：`{knowledge['entry_count']}`",
        f"- 覆盖状态：`{knowledge['coverage_status']}`",
        f"- 机制标签数：`{knowledge['mechanism_tag_count']}`",
        f"- 现场验证需求数：`{knowledge['field_validation_need_count']}`",
        f"- 缺口轴：{knowledge['missing_axes']}",
        "",
        "## 2. 软传感和模型验证审计",
        "",
        f"- 模型版本：`{validation['model_version']}`",
        f"- 训练行数：`{validation['rows']}`",
        f"- field_rows：`{validation['field_rows']}`",
        f"- synthetic_rows：`{validation['synthetic_rows']}`",
        f"- validation_status：`{validation['validation_status']}`",
        f"- weaker_targets：{validation['weaker_targets']}",
        f"- has_uncertainty_layer：`{validation['has_uncertainty_layer']}`",
        "",
        "## 3. 现场校准门控",
        "",
        f"- field_status：`{field['field_status']}`",
        f"- data_origin：`{field['data_origin']}`",
        f"- accepted_gates：`{field['accepted_gate_count']}/{field['total_gate_count']}`",
        f"- blocking_gates：{field['blocking_gates']}",
        "",
        "## 4. 过程模型现实性缺口",
        "",
    ]
    for gap in process["gaps"]:
        lines.extend(
            [
                f"### {gap['gap_id']}",
                "",
                f"- 当前状态：{gap['current_state']}",
                f"- 现实化升级：{gap['realism_upgrade']}",
                f"- 需要数据：{gap['validation_data']}",
                "",
            ]
        )
    lines.extend(["## 5. 可借鉴 skill 工作流", ""])
    for item in metrics["skill_inspired_workflow"]:
        lines.append(f"- `{item['skill_family']}`：{item['borrowed_idea']} 项目用法：{item['project_use']}")
    return "\n".join(lines)


def _backlog_md(report) -> str:
    lines = ["# 模型优化 Backlog", "", "| 优先级 | 工作项 | 为什么重要 | 主要阻塞/需求 | 目标文件 |", "| --- | --- | --- | --- | --- |"]
    for item in report.metrics["model_upgrade_backlog"]:
        lines.append(
            f"| `{item['priority']}` | `{item['work_id']}` {item['title']} | "
            f"{item['why']} | {item['blocks']} | {item['target_files']} |"
        )
    return "\n".join(lines)


def _report_md(report, generated_files: dict[str, str]) -> str:
    readiness = report.metrics["readiness"]
    lines = [
        "# Agent 35 模型真实性审计报告",
        "",
        f"- summary: {report.summary}",
        f"- realism_status: `{readiness['realism_status']}`",
        f"- realism_score: `{readiness['realism_score']}`",
        "",
        "## 生成文件",
        "",
    ]
    for key, path in generated_files.items():
        lines.append(f"- {key}: `{path}`")
    lines.extend(["", "## 优先建议", ""])
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    lines.extend(["", "## 风险边界", ""])
    for issue in report.issues:
        lines.append(f"- `{issue.issue_type}`：{issue.message}")
    return "\n".join(lines)


def _update_manifest(generated_files: dict[str, str]) -> None:
    manifest = _read_json(MANIFEST_PATH)
    relative_generated = {
        key: str(Path(path).relative_to(PROJECT_ROOT))
        for key, path in generated_files.items()
    }
    manifest["status"] = "模型真实性审计已生成"
    manifest["model_realism_audit"] = relative_generated
    manifest["next_stage"] = "优先按 model_upgrade_backlog.md 补充真实数据验收、软传感不确定性层和知识图谱证据矩阵"
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
