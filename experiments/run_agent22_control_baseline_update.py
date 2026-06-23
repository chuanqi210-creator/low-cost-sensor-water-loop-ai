from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.control_baseline_update_agent import ControlBaselineUpdateAgent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_REPORT = PROJECT_ROOT / "outputs" / "agent21_replanning_orchestrator" / "agent21_report.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent22_control_baseline_update"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    source = json.loads(SOURCE_REPORT.read_text(encoding="utf-8"))
    replan = source["replanning_orchestrator"]
    report = ControlBaselineUpdateAgent(
        replan_executed=bool(replan["metrics"]["replan_executed"]),
        replan_trace=replan["metrics"]["replan_trace"],
        previous_baseline={
            "load_control_policy": {
                "protected_intake_fraction": source["online_project_control"]["metrics"]["current_control_state"]["next_intake_fraction"],
            }
        },
        baseline_version="baseline_v1",
    ).run([])

    payload = {
        "source_report": str(SOURCE_REPORT),
        "control_baseline_update": {
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
    (OUT_DIR / "agent22_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    updated = report.metrics["updated_baseline"]
    config = updated["online_control_config"]
    lines = [
        "# Agent 22 控制基线写回模拟报告",
        "",
        f"- source_report: `{SOURCE_REPORT}`",
        f"- summary: {report.summary}",
        f"- update_required: `{updated['update_required']}`",
        f"- baseline_version: `{updated['baseline_version']}`",
        f"- writeback_summary: {updated['writeback_summary']}",
        "",
        "## 写回配置",
        "",
        f"- selected_queue_policy: `{config.get('selected_queue_policy', {})}`",
        f"- selected_portfolio: `{config.get('selected_portfolio', {})}`",
        f"- load_control_policy: `{config.get('load_control_policy', {})}`",
        f"- budget_sequence: `{config.get('budget_sequence', [])}`",
        f"- guardrails: `{config.get('guardrails', {})}`",
        f"- writeback_rules: `{config.get('writeback_rules', {})}`",
        "",
        "## 建议",
        "",
    ]
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    (OUT_DIR / "agent22_report.md").write_text("\n".join(lines), encoding="utf-8")

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent22_report.md'}")


if __name__ == "__main__":
    main()
