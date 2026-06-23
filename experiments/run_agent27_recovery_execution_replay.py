from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.recovery_execution_replay_agent import RecoveryExecutionReplayAgent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_REPORT = PROJECT_ROOT / "outputs" / "agent26_recovery_strategy_writeback" / "agent26_report.json"
CAMPAIGN_REPORT = PROJECT_ROOT / "outputs" / "agent24_recovery_ramp" / "agent24_report.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent27_recovery_execution_replay"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    source = json.loads(SOURCE_REPORT.read_text(encoding="utf-8"))
    campaign_source = json.loads(CAMPAIGN_REPORT.read_text(encoding="utf-8"))
    baseline = source["recovery_strategy_writeback"]["metrics"]["recovery_strategy_baseline"]
    campaign = campaign_source["campaign"]
    report = RecoveryExecutionReplayAgent(
        source_records=campaign["records"],
        recovery_baseline=baseline,
        catalyst_spares_remaining=campaign["catalyst_spares_remaining"],
        oxidant_stock_units_remaining=campaign["oxidant_stock_units_remaining"],
        validation_staff_hours_capacity=5.5,
        campaign_time_budget_min=960,
    ).run([])

    payload = {
        "source_report": str(SOURCE_REPORT),
        "campaign_report": str(CAMPAIGN_REPORT),
        "recovery_execution_replay": {
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
    (OUT_DIR / "agent27_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    comparison = report.metrics["comparison"]
    before = report.metrics["without_recovery_strategy"]
    after = report.metrics["with_recovery_strategy"]
    lines = [
        "# Agent 27 恢复策略执行回放报告",
        "",
        f"- source_report: `{SOURCE_REPORT}`",
        f"- campaign_report: `{CAMPAIGN_REPORT}`",
        f"- summary: {report.summary}",
        f"- replay_verdict: `{comparison['replay_verdict']}`",
        f"- target_intake_fraction: `{comparison['target_intake_fraction']}`",
        f"- recommended_next_intake_fraction: `{comparison['recommended_next_intake_fraction']}`",
        f"- fallback_required: `{comparison['fallback_required']}`",
        f"- time_usage_without_strategy: `{comparison['time_usage_without_strategy']}`",
        f"- time_usage_with_strategy: `{comparison['time_usage_with_strategy']}`",
        f"- time_usage_reduction: `{comparison['time_usage_reduction']}`",
        f"- expected_time_budget_usage: `{comparison['expected_time_budget_usage']}`",
        f"- time_usage_delta_from_expected: `{comparison['time_usage_delta_from_expected']}`",
        f"- validation_usage_with_strategy: `{comparison['validation_usage_with_strategy']}`",
        f"- elapsed_reduction_min: `{comparison['elapsed_reduction_min']}`",
        "",
        "## 无错峰 vs 写回策略",
        "",
        f"- without_strategy_bottlenecks: `{comparison['without_strategy_bottleneck_ids']}`",
        f"- with_strategy_bottlenecks: `{comparison['strategy_bottleneck_ids']}`",
        f"- without_strategy_mode: `{before['schedule']['operating_mode']}`",
        f"- with_strategy_mode: `{after['schedule']['operating_mode']}`",
        f"- scenario_sequence: `{after['scenario_sequence']}`",
        "",
        "## 建议",
        "",
    ]
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    (OUT_DIR / "agent27_report.md").write_text("\n".join(lines), encoding="utf-8")

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent27_report.md'}")


if __name__ == "__main__":
    main()
