from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.long_term_economics_agent import LongTermEconomicsAgent
from water_ai.agents.phased_implementation_agent import PhasedImplementationAgent
from water_ai.agents.resource_expansion_agent import ResourceExpansionAgent
from water_ai.operations import run_multibatch_campaign


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "outputs" / "agent16_phased_implementation"


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
    implementation_report = PhasedImplementationAgent(
        selected_program=economics_report.metrics["selected_program"],
        ranked_programs=economics_report.metrics["ranked_programs"],
        baseline=economics_report.metrics["baseline"],
        planning_assumptions=economics_report.metrics["planning_assumptions"],
        catalyst_spares_remaining=campaign.catalyst_spares_remaining,
        oxidant_stock_units_remaining=campaign.oxidant_stock_units_remaining,
        validation_staff_hours_capacity=5.5,
        campaign_time_budget_min=960,
        planning_horizon_campaigns=4,
    ).run([])

    payload = {
        "campaign": campaign.as_dict(),
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
        "phased_implementation": {
            "agent_name": implementation_report.agent_name,
            "confidence": implementation_report.confidence,
            "summary": implementation_report.summary,
            "recommendations": implementation_report.recommendations,
            "metrics": implementation_report.metrics,
            "issues": [
                {
                    "sensor": issue.sensor,
                    "issue_type": issue.issue_type,
                    "severity": issue.severity.value,
                    "message": issue.message,
                    "evidence": issue.evidence,
                }
                for issue in implementation_report.issues
            ],
        },
    }
    (OUT_DIR / "agent16_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Agent 16 分阶段实施模拟报告",
        "",
        f"- long_term_summary: {economics_report.summary}",
        f"- implementation_summary: {implementation_report.summary}",
        f"- execution_score: `{implementation_report.metrics['execution_score']}`",
        f"- schedule_risk: `{implementation_report.metrics['schedule_risk']}`",
        f"- readiness: `{implementation_report.metrics['readiness']}`",
        "",
        "## 阶段计划",
        "",
    ]
    for phase in implementation_report.metrics["phase_plan"]:
        lines.extend(
            [
                f"### {phase['phase_id']}",
                "",
                f"- campaign_window: `{phase['campaign_start']} -> {phase['campaign_end']}`",
                f"- objective: {phase['objective']}",
                f"- expected_bottlenecks: `{phase['expected_bottlenecks']}`",
                f"- readiness_gain: `{phase['readiness_gain']}`",
                "- actions:",
            ]
        )
        for action in phase["actions"]:
            lines.append(f"  - {action}")
        lines.extend(["- acceptance_criteria:"])
        for criterion in phase["acceptance_criteria"]:
            lines.append(f"  - {criterion}")
        lines.append("")
    lines.extend(
        [
            "## 库存与班次策略",
            "",
            f"- inventory_policy: `{implementation_report.metrics['inventory_policy']}`",
            f"- validation_staffing_plan: `{implementation_report.metrics['validation_staffing_plan']}`",
            f"- intake_policy: `{implementation_report.metrics['intake_policy']}`",
            "",
            "## 建议",
            "",
        ]
    )
    for rec in implementation_report.recommendations:
        lines.append(f"- {rec}")
    (OUT_DIR / "agent16_report.md").write_text("\n".join(lines), encoding="utf-8")

    print(implementation_report.summary)
    for rec in implementation_report.recommendations[:5]:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent16_report.md'}")


if __name__ == "__main__":
    main()
