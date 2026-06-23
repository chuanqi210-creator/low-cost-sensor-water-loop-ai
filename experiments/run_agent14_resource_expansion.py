from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.resource_expansion_agent import ResourceExpansionAgent
from water_ai.operations import run_multibatch_campaign


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "outputs" / "agent14_resource_expansion"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    scenarios = [
        "matrix_shock",
        "catalyst_deactivation",
        "matrix_shock",
        "catalyst_deactivation",
        "oxidant_limitation",
        "oxidant_limitation",
        "sensor_faults",
        "reaction_time_insufficient",
    ]
    campaign = run_multibatch_campaign(
        scenarios,
        max_steps_per_batch=5,
        initial_catalyst_spares=1,
        initial_oxidant_stock_units=2.2,
        seed=7,
    )
    report = ResourceExpansionAgent(
        batch_records=[record.as_dict() for record in campaign.records],
        catalyst_spares_remaining=campaign.catalyst_spares_remaining,
        oxidant_stock_units_remaining=campaign.oxidant_stock_units_remaining,
        validation_staff_hours_capacity=5.5,
        campaign_time_budget_min=960,
    ).run([])

    payload = {
        "campaign": campaign.as_dict(),
        "resource_expansion": {
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
    (OUT_DIR / "agent14_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Agent 14 资源扩容对比模拟报告",
        "",
        f"- summary: {report.summary}",
        f"- baseline: `{report.metrics['baseline']['campaign_metrics']}`",
        "",
        "## 干预方案排序",
        "",
    ]
    for item in report.metrics["ranked_interventions"]:
        lines.extend(
            [
                f"### {item['intervention_id']}",
                "",
                f"- score: `{item['intervention_score']}`",
                f"- bottleneck_relief: `{item['bottleneck_relief']}`",
                f"- cost_index: `{item['implementation_cost_index']}`",
                f"- validation_staff_usage: `{item['adjusted_validation_staff_usage']}`",
                f"- time_budget_usage: `{item['adjusted_time_budget_usage']}`",
                f"- catalyst_spares_remaining: `{item['adjusted_catalyst_spares_remaining']}`",
                f"- residual_bottlenecks: `{item['residual_bottleneck_ids']}`",
                "",
            ]
        )
    lines.extend(["## 建议", ""])
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    (OUT_DIR / "agent14_report.md").write_text("\n".join(lines), encoding="utf-8")

    print(report.summary)
    for rec in report.recommendations[:4]:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent14_report.md'}")


if __name__ == "__main__":
    main()
