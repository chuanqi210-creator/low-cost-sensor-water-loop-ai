from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.field_calibration_gate_agent import FieldCalibrationGateAgent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
AGENT30_REPORT = PROJECT_ROOT / "outputs" / "agent30_field_data_interface" / "agent30_report.json"
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent34_field_calibration_gate"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    agent30 = _read_json(AGENT30_REPORT)
    manifest = _read_json(MANIFEST_PATH)
    field_metrics = agent30["field_data_interface"]["metrics"]
    report = FieldCalibrationGateAgent(
        field_data_metrics=field_metrics,
        latest_regression=str(manifest.get("latest_regression", "141 passed")),
    ).run([])

    generated_files = {
        "calibration_protocol": str(DELIVERABLES_DIR / "field_calibration_protocol.md"),
        "acceptance_gates": str(DELIVERABLES_DIR / "field_data_acceptance_gates.md"),
        "calibration_runbook": str(DELIVERABLES_DIR / "field_calibration_runbook.md"),
        "agent34_report": str(OUT_DIR / "agent34_report.md"),
    }
    (DELIVERABLES_DIR / "field_calibration_protocol.md").write_text(_protocol_md(report), encoding="utf-8")
    (DELIVERABLES_DIR / "field_data_acceptance_gates.md").write_text(_gates_md(report), encoding="utf-8")
    (DELIVERABLES_DIR / "field_calibration_runbook.md").write_text(_runbook_md(report), encoding="utf-8")

    payload = {
        "source_reports": {"agent30": str(AGENT30_REPORT)},
        "field_calibration_gate": {
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
    (OUT_DIR / "agent34_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "agent34_report.md").write_text(_report_md(report, generated_files), encoding="utf-8")
    _update_manifest(generated_files)

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent34_report.md'}")
    for key, path in generated_files.items():
        print(f"{key}: {path}")


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _protocol_md(report) -> str:
    readiness = report.metrics["readiness"]
    core = report.metrics["core"]
    lines = [
        "# 现场实证校准协议",
        "",
        f"- 当前门控状态：`{readiness['calibration_gate_status']}`",
        f"- 数据来源：`{core['data_origin']}`",
        f"- 当前接口状态：`{core['interface_status']}`",
        f"- 回归基线：`{core['latest_regression']}`",
        "",
        "## 校准顺序",
        "",
    ]
    for phase in report.metrics["calibration_sequence"]:
        blockers = phase["current_blockers"] or []
        lines.extend(
            [
                f"### {phase['phase_id']} {phase['title']}",
                "",
                f"- 动作：{phase['action']}",
                f"- 上游任务是否就绪：`{phase['upstream_task_ready']}`",
                f"- 当前阻塞项：{blockers}",
                "",
            ]
        )
    lines.extend(["## 参数写回对象", ""])
    for item in report.metrics["writeback_plan"]:
        lines.append(f"- `{item['target']}`：{item['writeback']}")
    return "\n".join(lines)


def _gates_md(report) -> str:
    lines = ["# 现场数据验收门", "", "| Gate | 状态 | 验收规则 | 最小现场包 | 阻塞项 |", "| --- | --- | --- | --- | --- |"]
    for gate in report.metrics["acceptance_gates"]:
        status = "通过" if gate["gate_ready"] else "未通过"
        lines.append(
            f"| `{gate['gate_id']}` {gate['title']} | {status} | "
            f"{gate['acceptance_rule']} | {gate['minimum_field_package']} | {gate['blockers']} |"
        )
    return "\n".join(lines)


def _runbook_md(report) -> str:
    lines = ["# 现场校准运行手册", ""]
    for step in report.metrics["runbook"]:
        lines.extend(
            [
                f"## {step['step']} {step['title']}",
                "",
                f"- 操作：{step['detail']}",
                f"- 退出条件：{step['exit_criteria']}",
                "",
            ]
        )
    lines.extend(["## 建议", ""])
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    return "\n".join(lines)


def _report_md(report, generated_files: dict[str, str]) -> str:
    readiness = report.metrics["readiness"]
    lines = [
        "# Agent 34 实证校准入口门控报告",
        "",
        f"- summary: {report.summary}",
        f"- calibration_gate_status: `{readiness['calibration_gate_status']}`",
        f"- gate_score: `{readiness['gate_score']}`",
        f"- accepted_gates: `{readiness['accepted_gate_count']}/{readiness['total_gate_count']}`",
        "",
        "## 生成文件",
        "",
    ]
    for key, path in generated_files.items():
        lines.append(f"- {key}: `{path}`")
    lines.extend(["", "## 建议", ""])
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
    manifest["status"] = "实证校准入口门控已生成"
    manifest["field_calibration_gate"] = relative_generated
    manifest["next_stage"] = "按 field_calibration_runbook.md 导入真实现场数据，并用 field_data_acceptance_gates.md 做采集验收"
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
