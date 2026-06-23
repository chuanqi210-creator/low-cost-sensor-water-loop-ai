from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.adaptive_portfolio_agent import AdaptivePortfolioAgent
from water_ai.agents.implementation_stress_test_agent import ImplementationStressTestAgent
from water_ai.agents.long_term_economics_agent import LongTermEconomicsAgent
from water_ai.agents.phased_implementation_agent import PhasedImplementationAgent
from water_ai.agents.resource_expansion_agent import ResourceExpansionAgent
from water_ai.operations import run_multibatch_campaign


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "outputs" / "agent18_adaptive_portfolio"


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
    portfolio_report = AdaptivePortfolioAgent(
        ranked_stress_scenarios=stress_report.metrics["ranked_stress_scenarios"],
        guardrails=stress_report.metrics["guardrails"],
        selected_program=economics_report.metrics["selected_program"],
        budget_limit_increment=1.2,
    ).run([])

    payload = {
        "campaign": campaign.as_dict(),
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
        "adaptive_portfolio": {
            "agent_name": portfolio_report.agent_name,
            "confidence": portfolio_report.confidence,
            "summary": portfolio_report.summary,
            "recommendations": portfolio_report.recommendations,
            "metrics": portfolio_report.metrics,
            "issues": [
                {
                    "sensor": issue.sensor,
                    "issue_type": issue.issue_type,
                    "severity": issue.severity.value,
                    "message": issue.message,
                    "evidence": issue.evidence,
                }
                for issue in portfolio_report.issues
            ],
        },
    }
    (OUT_DIR / "agent18_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    selected = portfolio_report.metrics["selected_portfolio"]
    lines = [
        "# Agent 18 自适应项目组合模拟报告",
        "",
        f"- stress_summary: {stress_report.summary}",
        f"- portfolio_summary: {portfolio_report.summary}",
        f"- selected_portfolio: `{selected.get('package_id')}`",
        f"- dominant_stress_signals: `{portfolio_report.metrics['dominant_stress_signals']}`",
        f"- load_control_policy: `{portfolio_report.metrics['load_control_policy']}`",
        "",
        "## 项目包排序",
        "",
    ]
    for item in portfolio_report.metrics["ranked_portfolios"]:
        lines.extend(
            [
                f"### {item['package_id']}",
                "",
                f"- portfolio_score: `{item['portfolio_score']}`",
                f"- coverage_score: `{item['coverage_score']}`",
                f"- expected_risk_reduction: `{item['expected_risk_reduction']}`",
                f"- residual_risk: `{item['residual_risk']}`",
                f"- budget_pressure: `{item['budget_pressure']}`",
                f"- covered_signals: `{item['covered_signals']}`",
                f"- missing_signals: `{item['missing_signals']}`",
                f"- budget_items: `{item['budget_items']}`",
                "",
            ]
        )
    lines.extend(["## 预算释放顺序", ""])
    for item in portfolio_report.metrics["budget_sequence"]:
        lines.append(f"- {item['order']}. {item['budget_item']}：{item['release_rule']}")
    lines.extend(["", "## 建议", ""])
    for rec in portfolio_report.recommendations:
        lines.append(f"- {rec}")
    (OUT_DIR / "agent18_report.md").write_text("\n".join(lines), encoding="utf-8")

    print(portfolio_report.summary)
    for rec in portfolio_report.recommendations[:5]:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent18_report.md'}")


if __name__ == "__main__":
    main()
