from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.long_term_economics_agent import LongTermEconomicsAgent
from water_ai.agents.resource_expansion_agent import ResourceExpansionAgent
from water_ai.operations import run_multibatch_campaign


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "outputs" / "agent15_long_term_economics"


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
    batch_records = [record.as_dict() for record in campaign.records]
    expansion_report = ResourceExpansionAgent(
        batch_records=batch_records,
        catalyst_spares_remaining=campaign.catalyst_spares_remaining,
        oxidant_stock_units_remaining=campaign.oxidant_stock_units_remaining,
        validation_staff_hours_capacity=5.5,
        campaign_time_budget_min=960,
    ).run([])
    economics_report = LongTermEconomicsAgent(
        batch_records=batch_records,
        resource_interventions=expansion_report.metrics["ranked_interventions"],
        catalyst_spares_remaining=campaign.catalyst_spares_remaining,
        oxidant_stock_units_remaining=campaign.oxidant_stock_units_remaining,
        validation_staff_hours_capacity=5.5,
        campaign_time_budget_min=960,
        planning_horizon_campaigns=4,
        budget_index_limit=4.2,
        catalyst_lead_time_campaigns=2,
        oxidant_lead_time_campaigns=1,
        validation_staff_ramp_campaigns=1,
    ).run([])

    payload = {
        "campaign": campaign.as_dict(),
        "resource_expansion": {
            "agent_name": expansion_report.agent_name,
            "confidence": expansion_report.confidence,
            "summary": expansion_report.summary,
            "recommendations": expansion_report.recommendations,
            "metrics": expansion_report.metrics,
            "issues": [
                {
                    "sensor": issue.sensor,
                    "issue_type": issue.issue_type,
                    "severity": issue.severity.value,
                    "message": issue.message,
                    "evidence": issue.evidence,
                }
                for issue in expansion_report.issues
            ],
        },
        "long_term_economics": {
            "agent_name": economics_report.agent_name,
            "confidence": economics_report.confidence,
            "summary": economics_report.summary,
            "recommendations": economics_report.recommendations,
            "metrics": economics_report.metrics,
            "issues": [
                {
                    "sensor": issue.sensor,
                    "issue_type": issue.issue_type,
                    "severity": issue.severity.value,
                    "message": issue.message,
                    "evidence": issue.evidence,
                }
                for issue in economics_report.issues
            ],
        },
    }
    (OUT_DIR / "agent15_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    selected = economics_report.metrics["selected_program"]
    lines = [
        "# Agent 15 长期经济性与提前期模拟报告",
        "",
        f"- resource_expansion_summary: {expansion_report.summary}",
        f"- long_term_summary: {economics_report.summary}",
        f"- selected_program: `{selected.get('program_id')}`",
        f"- planning_assumptions: `{economics_report.metrics['planning_assumptions']}`",
        "",
        "## 长期项目排序",
        "",
    ]
    for item in economics_report.metrics["ranked_programs"]:
        lines.extend(
            [
                f"### {item['program_id']}",
                "",
                f"- program_score: `{item['program_score']}`",
                f"- service_level: `{item['service_level']}`",
                f"- resource_resilience: `{item['resource_resilience']}`",
                f"- multi_campaign_cost_index: `{item['multi_campaign_cost_index']}`",
                f"- budget_pressure: `{item['budget_pressure']}`",
                f"- lead_time_risk: `{item['lead_time_risk']}`",
                f"- residual_operational_risk: `{item['residual_operational_risk']}`",
                f"- residual_bottlenecks: `{item['residual_bottleneck_ids']}`",
                f"- actions: `{item['actions']}`",
                "",
            ]
        )
    lines.extend(["## 建议", ""])
    for rec in economics_report.recommendations:
        lines.append(f"- {rec}")
    (OUT_DIR / "agent15_report.md").write_text("\n".join(lines), encoding="utf-8")

    print(economics_report.summary)
    for rec in economics_report.recommendations[:5]:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent15_report.md'}")


if __name__ == "__main__":
    main()
