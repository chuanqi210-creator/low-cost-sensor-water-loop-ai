from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.project_synthesis_agent import ProjectSynthesisAgent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "outputs" / "agent29_project_synthesis"
PROJECT_OVERVIEW = PROJECT_ROOT / "docs" / "project_overview_28_agent.md"
REPORT_PATHS = {
    "agent23": PROJECT_ROOT / "outputs" / "agent23_post_replan_replay" / "agent23_report.json",
    "agent25": PROJECT_ROOT / "outputs" / "agent25_time_budget_recovery" / "agent25_report.json",
    "agent27": PROJECT_ROOT / "outputs" / "agent27_recovery_execution_replay" / "agent27_report.json",
    "agent28": PROJECT_ROOT / "outputs" / "agent28_recovery_online_control" / "agent28_report.json",
}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    reports = {key: _read_json(path) for key, path in REPORT_PATHS.items()}
    agent28_metrics = reports["agent28"]["recovery_online_control"]["metrics"]
    report = ProjectSynthesisAgent(
        synthesized_agent_count=28,
        latest_control_metrics=agent28_metrics,
        milestone_reports={
            "agent23": reports["agent23"],
            "agent25": reports["agent25"],
            "agent27": reports["agent27"],
        },
        artifact_paths={
            "agent29_report": str(OUT_DIR / "agent29_report.md"),
            "project_overview": str(PROJECT_OVERVIEW),
        },
        latest_regression="133 passed",
    ).run([])

    payload = {
        "source_reports": {key: str(path) for key, path in REPORT_PATHS.items()},
        "project_synthesis": {
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
    }
    (OUT_DIR / "agent29_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    report_md = _build_report_markdown(report)
    (OUT_DIR / "agent29_report.md").write_text(report_md, encoding="utf-8")
    PROJECT_OVERVIEW.write_text(_build_project_overview(report), encoding="utf-8")

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent29_report.md'}")
    print(f"wrote {PROJECT_OVERVIEW}")


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _build_report_markdown(report) -> str:
    metrics = report.metrics
    readiness = metrics["readiness_assessment"]
    latest = metrics["latest_control_state"]
    lines = [
        "# Agent 29 项目综合总览报告",
        "",
        f"- summary: {report.summary}",
        f"- synthesized_agent_count: `{metrics['synthesized_agent_count']}`",
        f"- maturity_level: `{readiness['maturity_level']}`",
        f"- latest_regression: `{metrics['latest_regression']}`",
        f"- recovery_control_mode: `{latest.get('recovery_control_mode')}`",
        f"- next_intake_fraction: `{latest.get('next_intake_fraction')}`",
        f"- fallback_intake_fraction: `{latest.get('fallback_intake_fraction')}`",
        f"- replan_required: `{latest.get('replan_required')}`",
        "",
        "## 总流程图",
        "",
        "```mermaid",
        metrics["project_mermaid"],
        "```",
        "",
        "## 模块分组",
        "",
        "| 模块 | Agent | 研究作用 | 核心输出 |",
        "| --- | --- | --- | --- |",
    ]
    for group in metrics["module_groups"]:
        lines.append(
            "| "
            + str(group["title"])
            + " | "
            + str(group["agent_range"])
            + " | "
            + str(group["research_role"])
            + " | "
            + ", ".join(str(item) for item in group["core_outputs"])
            + " |"
        )
    lines.extend(["", "## 关键证据链", ""])
    for item in metrics["evidence_chain"]:
        lines.extend(
            [
                f"### {item['step']}",
                "",
                f"- 判断：{item['claim']}",
                f"- 证据：{item['evidence']}",
            ]
        )
        if item.get("metrics"):
            lines.append(f"- 指标：`{json.dumps(item['metrics'], ensure_ascii=False)}`")
        lines.append("")
    lines.extend(
        [
            "## 真实数据校准路线",
            "",
            "| 阶段 | 主题 | 需要的数据 | 模型更新 |",
            "| --- | --- | --- | --- |",
        ]
    )
    for phase in metrics["calibration_roadmap"]:
        lines.append(
            "| "
            + str(phase["phase"])
            + " | "
            + str(phase["title"])
            + " | "
            + "；".join(str(item) for item in phase["data_needed"])
            + " | "
            + str(phase["model_update"])
            + " |"
        )
    lines.extend(["", "## 建议", ""])
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    lines.extend(["", "## 风险边界", ""])
    for issue in report.issues:
        lines.append(f"- `{issue.issue_type}`：{issue.message}")
    return "\n".join(lines)


def _build_project_overview(report) -> str:
    metrics = report.metrics
    readiness = metrics["readiness_assessment"]
    latest = metrics["latest_control_state"]
    lines = [
        "# 28-agent 研究平台项目级总览",
        "",
        "## 一句话定位",
        "",
        "这套原型不是单纯用机器学习拟合黑箱过程，而是用循环式水处理结构为低成本传感和慢证据争取时间，再用软传感器、多智能体诊断、闭环控制、项目重规划和恢复回放，把黑箱逐步变成可解释、可干预、可回退的灰箱系统。",
        "",
        "## 当前结论",
        "",
        f"- 当前成熟度：`{readiness['maturity_level']}`。",
        f"- 最新恢复控制：`{latest.get('recovery_control_mode')}`。",
        f"- 下一轮条件恢复进水比例：`{latest.get('next_intake_fraction')}`。",
        f"- 失败回退比例：`{latest.get('fallback_intake_fraction')}`。",
        f"- 是否需要重规划：`{latest.get('replan_required')}`。",
        f"- 当前回归：`{metrics['latest_regression']}`。",
        "",
        "## 总流程",
        "",
        "```mermaid",
        metrics["project_mermaid"],
        "```",
        "",
        "## 模块架构",
        "",
    ]
    for group in metrics["module_groups"]:
        lines.extend(
            [
                f"### {group['agent_range']} {group['title']}",
                "",
                f"- Agent：{', '.join(str(agent) for agent in group['agents'])}",
                f"- 作用：{group['research_role']}",
                f"- 输出：{', '.join(str(item) for item in group['core_outputs'])}",
                "",
            ]
        )
    lines.extend(["## 证据链", ""])
    for item in metrics["evidence_chain"]:
        lines.extend([f"- {item['claim']} {item['evidence']}"])
    lines.extend(
        [
            "",
            "## 下一步校准",
            "",
            "当前可以作为研究原型、项目书和汇报核心方案，但仍需要真实数据校准，尤其是传感器漂移、软传感器标签、催化剂寿命、副产物风险、时间预算和现场控制接口。",
            "",
        ]
    )
    for phase in metrics["calibration_roadmap"]:
        lines.append(f"- {phase['phase']} {phase['title']}：{phase['model_update']}")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
