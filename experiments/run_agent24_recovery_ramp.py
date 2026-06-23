from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.recovery_ramp_agent import RecoveryRampAgent
from water_ai.operations import run_multibatch_campaign


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_REPORT = PROJECT_ROOT / "outputs" / "agent22_control_baseline_update" / "agent22_report.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent24_recovery_ramp"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    source = json.loads(SOURCE_REPORT.read_text(encoding="utf-8"))
    updated = source["control_baseline_update"]["metrics"]["updated_baseline"]
    baseline = updated["online_control_config"]
    scenarios = baseline["selected_queue_policy"]["scenarios"]
    campaign = run_multibatch_campaign(
        scenarios,
        max_steps_per_batch=5,
        initial_catalyst_spares=1,
        initial_oxidant_stock_units=2.2,
        seed=7,
    )
    report = RecoveryRampAgent(
        source_records=[record.as_dict() for record in campaign.records],
        online_control_config={**baseline, "baseline_version": updated["baseline_version"]},
        catalyst_spares_remaining=campaign.catalyst_spares_remaining,
        oxidant_stock_units_remaining=campaign.oxidant_stock_units_remaining,
        validation_staff_hours_capacity=5.5,
        campaign_time_budget_min=960,
    ).run([])

    payload = {
        "source_report": str(SOURCE_REPORT),
        "campaign": campaign.as_dict(),
        "recovery_ramp": {
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
    (OUT_DIR / "agent24_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    metrics = report.metrics
    lines = [
        "# Agent 24 恢复放量爬坡验证报告",
        "",
        f"- source_report: `{SOURCE_REPORT}`",
        f"- summary: {report.summary}",
        f"- verdict: `{metrics['ramp_verdict']}`",
        f"- start_fraction: `{metrics['start_fraction']}`",
        f"- ramp_step: `{metrics['ramp_step']}`",
        f"- stable_campaigns_completed: `{metrics['stable_campaigns_completed']}/{metrics['target_stable_campaigns']}`",
        f"- final_safe_intake_fraction: `{metrics['final_safe_intake_fraction']}`",
        f"- final_safe_throughput_fraction: `{metrics['final_safe_throughput_fraction']}`",
        f"- limiting_attempted_fraction: `{metrics['limiting_attempted_fraction']}`",
        f"- limiting_bottlenecks: `{metrics['limiting_bottlenecks']}`",
        "",
        "## 资源投影",
        "",
    ]
    for key, value in metrics["resource_projection"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## 爬坡路径",
            "",
            "| step | attempted_intake | actual_throughput | admitted_batches | stable | bottlenecks | validation_usage | time_usage | mode |",
            "| --- | ---: | ---: | ---: | --- | --- | ---: | ---: | --- |",
        ]
    )
    for item in metrics["ramp_path"]:
        lines.append(
            "| "
            f"{item['step_index']} | "
            f"{item['attempted_intake_fraction']} | "
            f"{item['actual_throughput_fraction']} | "
            f"{item['admitted_batch_count']} | "
            f"{item['stable']} | "
            f"`{item['bottleneck_ids']}` | "
            f"{item['validation_staff_usage']} | "
            f"{item['time_budget_usage']} | "
            f"{item['operating_mode']} |"
        )
    lines.extend(["", "## 建议", ""])
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    (OUT_DIR / "agent24_report.md").write_text("\n".join(lines), encoding="utf-8")

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent24_report.md'}")


if __name__ == "__main__":
    main()
