from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.post_replan_replay_agent import PostReplanReplayAgent
from water_ai.operations import run_multibatch_campaign


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_REPORT = PROJECT_ROOT / "outputs" / "agent22_control_baseline_update" / "agent22_report.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent23_post_replan_replay"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    source = json.loads(SOURCE_REPORT.read_text(encoding="utf-8"))
    baseline = source["control_baseline_update"]["metrics"]["updated_baseline"]["online_control_config"]
    scenarios = baseline["selected_queue_policy"]["scenarios"]
    campaign = run_multibatch_campaign(
        scenarios,
        max_steps_per_batch=5,
        initial_catalyst_spares=1,
        initial_oxidant_stock_units=2.2,
        seed=7,
    )
    report = PostReplanReplayAgent(
        pre_replan_records=[record.as_dict() for record in campaign.records],
        online_control_config={
            **baseline,
            "baseline_version": source["control_baseline_update"]["metrics"]["updated_baseline"]["baseline_version"],
        },
        catalyst_spares_remaining=campaign.catalyst_spares_remaining,
        oxidant_stock_units_remaining=campaign.oxidant_stock_units_remaining,
        validation_staff_hours_capacity=5.5,
        campaign_time_budget_min=960,
    ).run([])

    payload = {
        "source_report": str(SOURCE_REPORT),
        "campaign": campaign.as_dict(),
        "post_replan_replay": {
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
    (OUT_DIR / "agent23_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    comparison = report.metrics["comparison"]
    projection = report.metrics["projection"]
    lines = [
        "# Agent 23 重规划后回放验证报告",
        "",
        f"- source_report: `{SOURCE_REPORT}`",
        f"- summary: {report.summary}",
        f"- verdict: `{comparison['verdict']}`",
        f"- impact_score: `{comparison['impact_score']}`",
        "",
        "## 对比结果",
        "",
        f"- validation_staff_usage: `{comparison['before_validation_staff_usage']} -> {comparison['after_validation_staff_usage']}`",
        f"- time_budget_usage: `{comparison['before_time_budget_usage']} -> {comparison['after_time_budget_usage']}`",
        f"- removed_bottlenecks: `{comparison['removed_bottleneck_ids']}`",
        f"- remaining_bottlenecks: `{comparison['remaining_bottleneck_ids']}`",
        f"- throughput_fraction: `{comparison['throughput_fraction']}`",
        f"- admitted_batch_count: `{comparison['admitted_batch_count']}`",
        "",
        "## 回放投影",
        "",
        f"- baseline_version: `{projection['baseline_version']}`",
        f"- intake_fraction: `{projection['intake_fraction']}`",
        f"- validation_minutes_multiplier: `{projection['validation_minutes_multiplier']}`",
        f"- validation_hours_delta: `{projection['validation_hours_delta']}`",
        f"- catalyst_spares_delta: `{projection['catalyst_spares_delta']}`",
        f"- oxidant_stock_delta: `{projection['oxidant_stock_delta']}`",
        f"- budget_items_applied: `{projection['budget_items_applied']}`",
        "",
        "## 建议",
        "",
    ]
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    (OUT_DIR / "agent23_report.md").write_text("\n".join(lines), encoding="utf-8")

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent23_report.md'}")


if __name__ == "__main__":
    main()
