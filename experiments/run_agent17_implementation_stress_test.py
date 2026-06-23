from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.implementation_stress_test_agent import ImplementationStressTestAgent
from water_ai.agents.long_term_economics_agent import LongTermEconomicsAgent
from water_ai.agents.phased_implementation_agent import PhasedImplementationAgent
from water_ai.agents.resource_expansion_agent import ResourceExpansionAgent
from water_ai.operations import run_multibatch_campaign


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "outputs" / "agent17_implementation_stress_test"


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
    stress_report = ImplementationStressTestAgent(
        selected_program=economics_report.metrics["selected_program"],
        phase_plan=implementation_report.metrics["phase_plan"],
        intake_policy=implementation_report.metrics["intake_policy"],
        inventory_policy=implementation_report.metrics["inventory_policy"],
        validation_staffing_plan=implementation_report.metrics["validation_staffing_plan"],
        planning_horizon_campaigns=4,
    ).run([])

    payload = {
        "campaign": campaign.as_dict(),
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
        "implementation_stress_test": {
            "agent_name": stress_report.agent_name,
            "confidence": stress_report.confidence,
            "summary": stress_report.summary,
            "recommendations": stress_report.recommendations,
            "metrics": stress_report.metrics,
            "issues": [
                {
                    "sensor": issue.sensor,
                    "issue_type": issue.issue_type,
                    "severity": issue.severity.value,
                    "message": issue.message,
                    "evidence": issue.evidence,
                }
                for issue in stress_report.issues
            ],
        },
    }
    (OUT_DIR / "agent17_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Agent 17 实施压力测试模拟报告",
        "",
        f"- implementation_summary: {implementation_report.summary}",
        f"- stress_summary: {stress_report.summary}",
        f"- robustness_score: `{stress_report.metrics['robustness_score']}`",
        f"- guardrails: `{stress_report.metrics['guardrails']}`",
        "",
        "## 压力情景排序",
        "",
    ]
    for item in stress_report.metrics["ranked_stress_scenarios"]:
        lines.extend(
            [
                f"### {item['scenario_id']}",
                "",
                f"- scenario_risk: `{item['scenario_risk']}`",
                f"- adjusted_ready_campaign: `{item['adjusted_ready_campaign']}`",
                f"- protected_intake_fraction: `{item['protected_intake_fraction']}`",
                f"- catalyst_stockout_risk: `{item['catalyst_stockout_risk']}`",
                f"- validation_overload_risk: `{item['validation_overload_risk']}`",
                "- contingency_actions:",
            ]
        )
        for action in item["contingency_actions"]:
            lines.append(f"  - {action}")
        lines.append("")
    lines.extend(["## 触发阈值", ""])
    for trigger in stress_report.metrics["trigger_table"]:
        lines.append(f"- `{trigger['scenario_id']}`: {trigger['trigger']} -> {trigger['response']}")
    lines.extend(["", "## 建议", ""])
    for rec in stress_report.recommendations:
        lines.append(f"- {rec}")
    (OUT_DIR / "agent17_report.md").write_text("\n".join(lines), encoding="utf-8")

    print(stress_report.summary)
    for rec in stress_report.recommendations[:5]:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent17_report.md'}")


if __name__ == "__main__":
    main()
