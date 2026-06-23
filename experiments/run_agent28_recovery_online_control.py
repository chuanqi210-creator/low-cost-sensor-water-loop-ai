from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.recovery_online_control_agent import RecoveryOnlineControlAgent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_REPORT = PROJECT_ROOT / "outputs" / "agent27_recovery_execution_replay" / "agent27_report.json"
BASELINE_REPORT = PROJECT_ROOT / "outputs" / "agent26_recovery_strategy_writeback" / "agent26_report.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent28_recovery_online_control"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    source = json.loads(SOURCE_REPORT.read_text(encoding="utf-8"))
    baseline_source = json.loads(BASELINE_REPORT.read_text(encoding="utf-8"))
    recovery_baseline = baseline_source["recovery_strategy_writeback"]["metrics"]["recovery_strategy_baseline"]
    report = RecoveryOnlineControlAgent(
        recovery_execution_metrics=source["recovery_execution_replay"]["metrics"],
        recovery_baseline=recovery_baseline,
    ).run([])

    payload = {
        "source_report": str(SOURCE_REPORT),
        "baseline_report": str(BASELINE_REPORT),
        "recovery_online_control": {
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
    (OUT_DIR / "agent28_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    adjusted = report.metrics["adjusted_control_state"]
    update = report.metrics["recovery_campaign_update"]
    base_state = adjusted["base_online_state"]
    lines = [
        "# Agent 28 恢复在线控制接入报告",
        "",
        f"- source_report: `{SOURCE_REPORT}`",
        f"- baseline_report: `{BASELINE_REPORT}`",
        f"- summary: {report.summary}",
        f"- recovery_control_mode: `{adjusted['recovery_control_mode']}`",
        f"- next_intake_fraction: `{adjusted['next_intake_fraction']}`",
        f"- fallback_intake_fraction: `{adjusted['fallback_intake_fraction']}`",
        f"- replan_required: `{adjusted['replan_required']}`",
        f"- recovery_replay_verdict: `{adjusted['recovery_replay_verdict']}`",
        "",
        "## 恢复 campaign 更新",
        "",
        f"- acceptance_passed: `{update['acceptance_passed']}`",
        f"- validation_staff_usage: `{update['validation_staff_usage']}`",
        f"- time_budget_usage: `{update['time_budget_usage']}`",
        f"- bottleneck_ids: `{update['bottleneck_ids']}`",
        f"- recovery_policy_applied: `{update['recovery_policy_applied']}`",
        f"- source_scenarios: `{update['source_scenarios']}`",
        "",
        "## OnlineProjectControl 原始判断",
        "",
        f"- base_project_mode: `{base_state.get('project_mode')}`",
        f"- base_next_intake_fraction: `{base_state.get('next_intake_fraction')}`",
        f"- base_replan_required: `{base_state.get('replan_required')}`",
        f"- base_dominant_signals: `{base_state.get('dominant_signals')}`",
        "",
        "## 建议",
        "",
    ]
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    (OUT_DIR / "agent28_report.md").write_text("\n".join(lines), encoding="utf-8")

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent28_report.md'}")


if __name__ == "__main__":
    main()
