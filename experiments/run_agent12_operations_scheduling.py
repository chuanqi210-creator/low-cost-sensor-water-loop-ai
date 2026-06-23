from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.operations_scheduling_agent import OperationsSchedulingAgent
from water_ai.operations import run_multibatch_campaign


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "outputs" / "agent12_operations_scheduling"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    scenarios = [
        "sensor_faults",
        "oxidant_limitation",
        "reaction_time_insufficient",
        "matrix_shock",
        "catalyst_deactivation",
        "oxidant_limitation",
        "matrix_shock",
        "catalyst_deactivation",
    ]
    campaign = run_multibatch_campaign(
        scenarios,
        max_steps_per_batch=5,
        initial_catalyst_spares=1,
        initial_oxidant_stock_units=2.2,
        seed=7,
    )
    report = OperationsSchedulingAgent(
        batch_records=[record.as_dict() for record in campaign.records],
        catalyst_spares_remaining=campaign.catalyst_spares_remaining,
        oxidant_stock_units_remaining=campaign.oxidant_stock_units_remaining,
        validation_staff_hours_capacity=5.5,
        campaign_time_budget_min=960,
    ).run([])

    payload = {
        "campaign": campaign.as_dict(),
        "operations_scheduling": {
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
    (OUT_DIR / "agent12_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Agent 12 多批次运行调度模拟报告",
        "",
        f"- summary: {report.summary}",
        f"- campaign batches: {len(campaign.records)}",
        f"- total elapsed min: {campaign.total_elapsed_min}",
        f"- total cost: {campaign.total_cost}",
        f"- total energy: {campaign.total_energy}",
        f"- catalyst spares remaining: {campaign.catalyst_spares_remaining}",
        f"- oxidant stock remaining: {campaign.oxidant_stock_units_remaining}",
        "",
        "## 调度建议",
        "",
    ]
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    lines.extend(["", "## 批次记录", ""])
    for record in campaign.records:
        lines.extend(
            [
                f"### Batch {record.batch_id}: {record.scenario}",
                "",
                f"- success: `{record.success}`",
                f"- elapsed_min: `{record.elapsed_min}`",
                f"- all_actions: `{record.all_actions}`",
                f"- validation_minutes: `{record.validation_minutes}`",
                f"- catalyst_lifetime_fraction_end: `{record.catalyst_lifetime_fraction_end}`",
                f"- catalyst_regen_count_end: `{record.catalyst_regen_count_end}`",
                "",
            ]
        )
    (OUT_DIR / "agent12_report.md").write_text("\n".join(lines), encoding="utf-8")

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent12_report.md'}")


if __name__ == "__main__":
    main()
