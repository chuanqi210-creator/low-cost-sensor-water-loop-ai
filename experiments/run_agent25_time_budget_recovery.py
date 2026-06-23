from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.time_budget_recovery_agent import TimeBudgetRecoveryAgent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_REPORT = PROJECT_ROOT / "outputs" / "agent24_recovery_ramp" / "agent24_report.json"
BASELINE_REPORT = PROJECT_ROOT / "outputs" / "agent22_control_baseline_update" / "agent22_report.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent25_time_budget_recovery"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    source = json.loads(SOURCE_REPORT.read_text(encoding="utf-8"))
    baseline_source = json.loads(BASELINE_REPORT.read_text(encoding="utf-8"))
    updated = baseline_source["control_baseline_update"]["metrics"]["updated_baseline"]
    baseline = updated["online_control_config"]
    campaign = source["campaign"]
    ramp_metrics = source["recovery_ramp"]["metrics"]
    report = TimeBudgetRecoveryAgent(
        source_records=campaign["records"],
        recovery_ramp_metrics=ramp_metrics,
        online_control_config={**baseline, "baseline_version": updated["baseline_version"]},
        catalyst_spares_remaining=campaign["catalyst_spares_remaining"],
        oxidant_stock_units_remaining=campaign["oxidant_stock_units_remaining"],
        validation_staff_hours_capacity=5.5,
        campaign_time_budget_min=960,
    ).run([])

    payload = {
        "source_report": str(SOURCE_REPORT),
        "baseline_report": str(BASELINE_REPORT),
        "time_budget_recovery": {
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
    (OUT_DIR / "agent25_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    metrics = report.metrics
    selected = metrics["selected_candidate"]
    lines = [
        "# Agent 25 时间预算恢复方案报告",
        "",
        f"- source_report: `{SOURCE_REPORT}`",
        f"- baseline_report: `{BASELINE_REPORT}`",
        f"- summary: {report.summary}",
        f"- verdict: `{metrics['strategy_verdict']}`",
        f"- target_intake_fraction: `{metrics['target_intake_fraction']}`",
        f"- safe_intake_fraction: `{metrics['safe_intake_fraction']}`",
        f"- selected_candidate: `{selected['candidate_id']}`",
        f"- selected_time_budget_usage: `{selected['time_budget_usage']}`",
        f"- selected_actual_throughput_fraction: `{selected['actual_throughput_fraction']}`",
        "",
        "## 候选方案对比",
        "",
        "| candidate | stable | target_recovery | throughput | time_usage | validation_usage | added_window | elapsed_reduction | bottlenecks | score |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |",
    ]
    for item in metrics["candidate_results"]:
        lines.append(
            "| "
            f"{item['candidate_id']} | "
            f"{item['stable']} | "
            f"{item['target_recovery']} | "
            f"{item['actual_throughput_fraction']} | "
            f"{item['time_budget_usage']} | "
            f"{item['validation_staff_usage']} | "
            f"{item['added_campaign_window_min']} | "
            f"{item['elapsed_reduction_min']} | "
            f"`{item['bottleneck_ids']}` | "
            f"{item['candidate_score']} |"
        )
    lines.extend(
        [
            "",
            "## 推荐方案批次顺序",
            "",
            f"- queue_policy: `{selected['queue_policy']}`",
            f"- scenario_sequence: `{selected['scenario_sequence']}`",
            "",
            "## 建议",
            "",
        ]
    )
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    (OUT_DIR / "agent25_report.md").write_text("\n".join(lines), encoding="utf-8")

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent25_report.md'}")


if __name__ == "__main__":
    main()
