from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.adaptive_portfolio_agent import AdaptivePortfolioAgent
from water_ai.agents.campaign_telemetry_agent import CampaignTelemetryAgent
from water_ai.agents.implementation_stress_test_agent import ImplementationStressTestAgent
from water_ai.agents.long_term_economics_agent import LongTermEconomicsAgent
from water_ai.agents.online_project_control_agent import OnlineProjectControlAgent
from water_ai.agents.operations_scheduling_agent import OperationsSchedulingAgent
from water_ai.agents.phased_implementation_agent import PhasedImplementationAgent
from water_ai.agents.replanning_orchestrator_agent import ReplanningOrchestratorAgent
from water_ai.agents.resource_expansion_agent import ResourceExpansionAgent
from water_ai.operations import run_multibatch_campaign


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "outputs" / "agent21_replanning_orchestrator"


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
    ).run([])
    stress_report = ImplementationStressTestAgent(
        selected_program=economics_report.metrics["selected_program"],
        phase_plan=implementation_report.metrics["phase_plan"],
        intake_policy=implementation_report.metrics["intake_policy"],
        inventory_policy=implementation_report.metrics["inventory_policy"],
        validation_staffing_plan=implementation_report.metrics["validation_staffing_plan"],
    ).run([])
    portfolio_report = AdaptivePortfolioAgent(
        ranked_stress_scenarios=stress_report.metrics["ranked_stress_scenarios"],
        guardrails=stress_report.metrics["guardrails"],
        selected_program=economics_report.metrics["selected_program"],
        budget_limit_increment=1.2,
    ).run([])
    telemetry_report = CampaignTelemetryAgent(
        batch_records=batch_records,
        update_cut_points=[2, 5, 8],
        initial_catalyst_spares=1,
        initial_oxidant_stock_units=2.2,
        validation_staff_hours_capacity=5.5,
        campaign_time_budget_min=960,
        budget_release_plan={
            0: {"budget_release_fraction": 0.55, "budget_released_items": ["外包低价值验证"]},
            1: {"budget_release_fraction": 0.82, "budget_released_items": ["催化剂备用供应商", "验证能力批复"]},
            2: {"budget_release_fraction": 1.0, "budget_released_items": ["催化剂库存批复", "氧化剂库存批复"]},
        },
        planned_ready_campaign=2,
    ).run([])
    control_report = OnlineProjectControlAgent(
        selected_portfolio=portfolio_report.metrics["selected_portfolio"],
        budget_sequence=portfolio_report.metrics["budget_sequence"],
        load_control_policy=portfolio_report.metrics["load_control_policy"],
        rolling_campaigns=telemetry_report.metrics["rolling_campaign_updates"],
        catalyst_safety_stock=implementation_report.metrics["inventory_policy"]["catalyst_safety_stock"],
        oxidant_safety_stock_units=implementation_report.metrics["inventory_policy"]["oxidant_safety_stock_units"],
    ).run([])
    replan_report = ReplanningOrchestratorAgent(
        current_control_state=control_report.metrics["current_control_state"],
        batch_records=batch_records,
        queue_candidate_plans=_queue_candidate_plans(),
        catalyst_spares_remaining=campaign.catalyst_spares_remaining,
        oxidant_stock_units_remaining=campaign.oxidant_stock_units_remaining,
        validation_staff_hours_capacity=5.5,
        campaign_time_budget_min=960,
        budget_limit_increment=1.2,
    ).run([])

    payload = {
        "campaign": campaign.as_dict(),
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
        "replanning_orchestrator": {
            "agent_name": replan_report.agent_name,
            "confidence": replan_report.confidence,
            "summary": replan_report.summary,
            "recommendations": replan_report.recommendations,
            "metrics": replan_report.metrics,
            "issues": [
                {
                    "sensor": issue.sensor,
                    "issue_type": issue.issue_type,
                    "severity": issue.severity.value,
                    "message": issue.message,
                    "evidence": issue.evidence,
                }
                for issue in replan_report.issues
            ],
        },
    }
    (OUT_DIR / "agent21_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    trace = replan_report.metrics["replan_trace"]
    lines = [
        "# Agent 21 自动重规划编排模拟报告",
        "",
        f"- control_summary: {control_report.summary}",
        f"- replan_summary: {replan_report.summary}",
        f"- replan_executed: `{replan_report.metrics['replan_executed']}`",
        "",
        "## 重规划链路",
        "",
        f"- queue_planning: {trace['queue_planning']['summary']}",
        f"- resource_expansion: {trace['resource_expansion']['summary']}",
        f"- long_term_economics: {trace['long_term_economics']['summary']}",
        f"- phased_implementation: {trace['phased_implementation']['summary']}",
        f"- implementation_stress_test: {trace['implementation_stress_test']['summary']}",
        f"- adaptive_portfolio: {trace['adaptive_portfolio']['summary']}",
        "",
        "## 关键输出",
        "",
        f"- selected_queue_policy: `{trace['queue_planning']['selected_policy'].get('policy_id', 'none')}`",
        f"- selected_intervention: `{trace['resource_expansion']['selected_intervention'].get('intervention_id', 'none')}`",
        f"- selected_program: `{trace['long_term_economics']['selected_program'].get('program_id', 'none')}`",
        f"- selected_portfolio: `{trace['adaptive_portfolio']['selected_portfolio'].get('package_id', 'none')}`",
        f"- load_control_policy: `{trace['adaptive_portfolio']['load_control_policy']}`",
        "",
        "## 建议",
        "",
    ]
    for rec in replan_report.recommendations:
        lines.append(f"- {rec}")
    (OUT_DIR / "agent21_report.md").write_text("\n".join(lines), encoding="utf-8")

    print(replan_report.summary)
    for rec in replan_report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent21_report.md'}")


def _queue_candidate_plans() -> list[dict[str, object]]:
    base_scenarios = [
        "sensor_faults",
        "oxidant_limitation",
        "reaction_time_insufficient",
        "matrix_shock",
        "catalyst_deactivation",
        "oxidant_limitation",
        "matrix_shock",
        "catalyst_deactivation",
    ]
    policies = {
        "arrival_order": base_scenarios,
        "validation_smoothed": [
            "reaction_time_insufficient",
            "sensor_faults",
            "oxidant_limitation",
            "matrix_shock",
            "oxidant_limitation",
            "catalyst_deactivation",
            "matrix_shock",
            "catalyst_deactivation",
        ],
        "high_risk_first": [
            "matrix_shock",
            "catalyst_deactivation",
            "matrix_shock",
            "catalyst_deactivation",
            "oxidant_limitation",
            "oxidant_limitation",
            "sensor_faults",
            "reaction_time_insufficient",
        ],
    }
    return [
        _evaluate_policy(policy_id, ordered)
        for policy_id, ordered in policies.items()
    ]


def _evaluate_policy(policy_id: str, scenarios: list[str]) -> dict[str, object]:
    campaign = run_multibatch_campaign(
        scenarios,
        max_steps_per_batch=5,
        initial_catalyst_spares=1,
        initial_oxidant_stock_units=2.2,
        seed=7,
    )
    operations_report = OperationsSchedulingAgent(
        batch_records=[record.as_dict() for record in campaign.records],
        catalyst_spares_remaining=campaign.catalyst_spares_remaining,
        oxidant_stock_units_remaining=campaign.oxidant_stock_units_remaining,
        validation_staff_hours_capacity=5.5,
        campaign_time_budget_min=960,
    ).run([])
    return {
        "policy_id": policy_id,
        "description": policy_id,
        "scenarios": scenarios,
        "campaign_metrics": operations_report.metrics["campaign_metrics"],
        "bottlenecks": operations_report.metrics["bottlenecks"],
        "schedule": operations_report.metrics["schedule"],
    }


if __name__ == "__main__":
    main()
