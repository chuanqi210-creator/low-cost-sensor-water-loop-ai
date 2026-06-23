from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.adaptive_portfolio_agent import AdaptivePortfolioAgent
from water_ai.agents.implementation_stress_test_agent import ImplementationStressTestAgent
from water_ai.agents.long_term_economics_agent import LongTermEconomicsAgent
from water_ai.agents.online_project_control_agent import OnlineProjectControlAgent
from water_ai.agents.phased_implementation_agent import PhasedImplementationAgent
from water_ai.agents.resource_expansion_agent import ResourceExpansionAgent
from water_ai.operations import run_multibatch_campaign


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "outputs" / "agent19_online_project_control"


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
    control_report = OnlineProjectControlAgent(
        selected_portfolio=portfolio_report.metrics["selected_portfolio"],
        budget_sequence=portfolio_report.metrics["budget_sequence"],
        load_control_policy=portfolio_report.metrics["load_control_policy"],
        rolling_campaigns=_rolling_campaign_updates(),
        catalyst_safety_stock=implementation_report.metrics["inventory_policy"]["catalyst_safety_stock"],
        oxidant_safety_stock_units=implementation_report.metrics["inventory_policy"]["oxidant_safety_stock_units"],
    ).run([])

    payload = {
        "campaign": campaign.as_dict(),
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
        "online_project_control": {
            "agent_name": control_report.agent_name,
            "confidence": control_report.confidence,
            "summary": control_report.summary,
            "recommendations": control_report.recommendations,
            "metrics": control_report.metrics,
            "issues": [
                {
                    "sensor": issue.sensor,
                    "issue_type": issue.issue_type,
                    "severity": issue.severity.value,
                    "message": issue.message,
                    "evidence": issue.evidence,
                }
                for issue in control_report.issues
            ],
        },
    }
    (OUT_DIR / "agent19_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    state = control_report.metrics["current_control_state"]
    lines = [
        "# Agent 19 在线滚动项目控制模拟报告",
        "",
        f"- portfolio_summary: {portfolio_report.summary}",
        f"- control_summary: {control_report.summary}",
        f"- current_project_mode: `{state.get('project_mode')}`",
        f"- next_intake_fraction: `{state.get('next_intake_fraction')}`",
        f"- next_budget_item: `{state.get('next_budget_item')}`",
        "",
        "## 滚动决策",
        "",
    ]
    for decision in control_report.metrics["rolling_decisions"]:
        lines.extend(
            [
                f"### campaign {decision['campaign_id']}",
                "",
                f"- mode: `{decision['project_mode']}`",
                f"- rolling_risk: `{decision['rolling_risk']}`",
                f"- dominant_signals: `{decision['dominant_signals']}`",
                f"- stable_streak: `{decision['stable_streak']}`",
                f"- next_intake_fraction: `{decision['next_intake_fraction']}`",
                f"- next_budget_item: `{decision['next_budget_item']}`",
                f"- replan_required: `{decision['replan_required']}`",
                f"- replan_reasons: `{decision['replan_reasons']}`",
                "",
            ]
        )
    lines.extend(["## 建议", ""])
    for rec in control_report.recommendations:
        lines.append(f"- {rec}")
    (OUT_DIR / "agent19_report.md").write_text("\n".join(lines), encoding="utf-8")

    print(control_report.summary)
    for rec in control_report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent19_report.md'}")


def _rolling_campaign_updates() -> list[dict[str, object]]:
    return [
        {
            "campaign_id": 0,
            "acceptance_passed": True,
            "success_rate": 1.0,
            "validation_staff_usage": 0.88,
            "time_budget_usage": 0.91,
            "catalyst_spares_remaining": 1,
            "oxidant_stock_units_remaining": 1.3,
            "intake_pressure_multiplier": 1.10,
            "budget_release_fraction": 0.75,
            "budget_released_items": ["外包低价值验证"],
        },
        {
            "campaign_id": 1,
            "acceptance_passed": True,
            "success_rate": 1.0,
            "validation_staff_usage": 0.80,
            "time_budget_usage": 0.84,
            "catalyst_spares_remaining": 2,
            "oxidant_stock_units_remaining": 1.5,
            "intake_pressure_multiplier": 1.0,
            "budget_release_fraction": 0.92,
            "budget_released_items": ["催化剂备用供应商", "验证能力批复"],
        },
        {
            "campaign_id": 2,
            "acceptance_passed": True,
            "success_rate": 1.0,
            "validation_staff_usage": 0.72,
            "time_budget_usage": 0.78,
            "catalyst_spares_remaining": 2,
            "oxidant_stock_units_remaining": 1.6,
            "intake_pressure_multiplier": 1.0,
            "budget_release_fraction": 1.0,
            "budget_released_items": ["催化剂库存批复", "氧化剂库存批复"],
        },
    ]


if __name__ == "__main__":
    main()
