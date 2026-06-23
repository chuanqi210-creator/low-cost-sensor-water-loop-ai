from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.operations_scheduling_agent import OperationsSchedulingAgent
from water_ai.agents.queue_planning_agent import QueuePlanningAgent
from water_ai.operations import run_multibatch_campaign


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "outputs" / "agent13_queue_planning"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
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
        "arrival_order": {
            "description": "按到达顺序处理。",
            "scenarios": base_scenarios,
        },
        "validation_smoothed": {
            "description": "把高验证负担场景分散到队列中间，避免慢证据集中排队。",
            "scenarios": [
                "reaction_time_insufficient",
                "sensor_faults",
                "oxidant_limitation",
                "matrix_shock",
                "oxidant_limitation",
                "catalyst_deactivation",
                "matrix_shock",
                "catalyst_deactivation",
            ],
        },
        "catalyst_preserving": {
            "description": "尽量推迟连续催化剂压力批次，先处理非催化剂瓶颈。",
            "scenarios": [
                "sensor_faults",
                "reaction_time_insufficient",
                "oxidant_limitation",
                "matrix_shock",
                "oxidant_limitation",
                "matrix_shock",
                "catalyst_deactivation",
                "catalyst_deactivation",
            ],
        },
        "high_risk_first": {
            "description": "优先处理基质冲击和催化剂风险，尽早暴露维护瓶颈。",
            "scenarios": [
                "matrix_shock",
                "catalyst_deactivation",
                "matrix_shock",
                "catalyst_deactivation",
                "oxidant_limitation",
                "oxidant_limitation",
                "sensor_faults",
                "reaction_time_insufficient",
            ],
        },
    }
    candidate_plans = [
        _evaluate_policy(policy_id, payload["description"], payload["scenarios"])
        for policy_id, payload in policies.items()
    ]
    report = QueuePlanningAgent(candidate_plans=candidate_plans).run([])

    payload = {
        "candidate_plans": candidate_plans,
        "queue_planning": {
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
    (OUT_DIR / "agent13_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Agent 13 批次队列规划模拟报告",
        "",
        f"- summary: {report.summary}",
        "",
        "## 策略排序",
        "",
    ]
    for item in report.metrics["ranked_policies"]:
        lines.extend(
            [
                f"### {item['policy_id']}",
                "",
                f"- score: `{item['queue_score']}`",
                f"- operating_mode: `{item['operating_mode']}`",
                f"- validation_staff_usage: `{item['validation_staff_usage']}`",
                f"- time_budget_usage: `{item['time_budget_usage']}`",
                f"- catalyst_spares_remaining: `{item['catalyst_spares_remaining']}`",
                f"- bottlenecks: `{item['bottleneck_ids']}`",
                f"- next_batches: `{item['next_batches']}`",
                "",
            ]
        )
    lines.extend(["## 建议", ""])
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    (OUT_DIR / "agent13_report.md").write_text("\n".join(lines), encoding="utf-8")

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent13_report.md'}")


def _evaluate_policy(policy_id: str, description: str, scenarios: list[str]) -> dict[str, object]:
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
        "description": description,
        "scenarios": scenarios,
        "campaign": campaign.as_dict(),
        "campaign_metrics": operations_report.metrics["campaign_metrics"],
        "bottlenecks": operations_report.metrics["bottlenecks"],
        "schedule": operations_report.metrics["schedule"],
    }


if __name__ == "__main__":
    main()
