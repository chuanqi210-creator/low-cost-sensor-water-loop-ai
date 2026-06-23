from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.recovery_strategy_writeback_agent import RecoveryStrategyWritebackAgent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_REPORT = PROJECT_ROOT / "outputs" / "agent25_time_budget_recovery" / "agent25_report.json"
BASELINE_REPORT = PROJECT_ROOT / "outputs" / "agent22_control_baseline_update" / "agent22_report.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent26_recovery_strategy_writeback"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    source = json.loads(SOURCE_REPORT.read_text(encoding="utf-8"))
    baseline_source = json.loads(BASELINE_REPORT.read_text(encoding="utf-8"))
    updated = baseline_source["control_baseline_update"]["metrics"]["updated_baseline"]
    report = RecoveryStrategyWritebackAgent(
        time_budget_recovery_metrics=source["time_budget_recovery"]["metrics"],
        previous_baseline=updated["online_control_config"],
        baseline_version=updated["baseline_version"],
    ).run([])

    payload = {
        "source_report": str(SOURCE_REPORT),
        "baseline_report": str(BASELINE_REPORT),
        "recovery_strategy_writeback": {
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
    (OUT_DIR / "agent26_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    baseline = report.metrics["recovery_strategy_baseline"]
    decision = baseline["writeback_decision"]
    config = baseline["online_control_config"]
    recovery = config["recovery_control_policy"]
    lines = [
        "# Agent 26 恢复策略写回报告",
        "",
        f"- source_report: `{SOURCE_REPORT}`",
        f"- baseline_report: `{BASELINE_REPORT}`",
        f"- summary: {report.summary}",
        f"- baseline_version: `{baseline['baseline_version']}`",
        f"- previous_baseline_version: `{baseline['previous_baseline_version']}`",
        f"- writeback_mode: `{decision['writeback_mode']}`",
        f"- selected_candidate_id: `{decision['selected_candidate_id']}`",
        f"- next_intake_fraction: `{decision['next_intake_fraction']}`",
        f"- fallback_intake_fraction: `{decision['fallback_intake_fraction']}`",
        f"- expected_time_budget_usage: `{decision['expected_time_budget_usage']}`",
        f"- expected_validation_staff_usage: `{decision['expected_validation_staff_usage']}`",
        "",
        "## 恢复控制策略",
        "",
        f"- enabled: `{recovery['enabled']}`",
        f"- target_intake_fraction: `{recovery['target_intake_fraction']}`",
        f"- fallback_intake_fraction: `{recovery['fallback_intake_fraction']}`",
        f"- queue_policy: `{recovery['queue_policy']}`",
        f"- scenario_sequence: `{recovery['scenario_sequence']}`",
        f"- required_post_campaign_checks: `{recovery['required_post_campaign_checks']}`",
        f"- fallback_triggers: `{recovery['fallback_triggers']}`",
        f"- execution_requirements: `{recovery['execution_requirements']}`",
        f"- validation_overlap_rule: `{recovery.get('validation_overlap_rule', {})}`",
        "",
        "## 写回规则",
        "",
        f"- load_control_policy: `{config['load_control_policy']}`",
        f"- writeback_rules: `{config['writeback_rules']}`",
        f"- guardrails: `{config['guardrails']}`",
        f"- runtime_recovery_override: `{config['selected_queue_policy'].get('runtime_recovery_override', {})}`",
        "",
        "## 建议",
        "",
    ]
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    (OUT_DIR / "agent26_report.md").write_text("\n".join(lines), encoding="utf-8")

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent26_report.md'}")


if __name__ == "__main__":
    main()
