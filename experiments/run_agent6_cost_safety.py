from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.catalyst_lifecycle_agent import CatalystLifecycleAgent
from water_ai.agents.control_strategy_agent import ControlStrategyAgent
from water_ai.agents.cost_safety_agent import CostSafetyAgent
from water_ai.agents.data_quality_agent import DataQualityAgent
from water_ai.agents.fault_diagnosis_agent import FaultDiagnosisAgent
from water_ai.agents.mechanism_agent import MechanismAgent
from water_ai.agents.soft_sensor_agent import SoftSensorAgent
from water_ai.agents.validation_planning_agent import ValidationPlanningAgent
from water_ai.simulation import generate_low_cost_sensor_stream


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "outputs" / "agent6_cost_safety"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    readings = generate_low_cost_sensor_stream(n=72, seed=7, inject_faults=True)
    dq_report = DataQualityAgent().run(readings)
    soft_report = SoftSensorAgent(data_quality_report=dq_report).run(readings)
    mechanism_report = MechanismAgent(data_quality_report=dq_report, soft_sensor_report=soft_report).run(readings)
    fault_report = FaultDiagnosisAgent(
        data_quality_report=dq_report,
        soft_sensor_report=soft_report,
        mechanism_report=mechanism_report,
    ).run(readings)
    lifecycle_report = CatalystLifecycleAgent(soft_sensor_report=soft_report, fault_report=fault_report).run(readings)
    validation_report = ValidationPlanningAgent(soft_sensor_report=soft_report, fault_report=fault_report).run(readings)
    control_report = ControlStrategyAgent(
        soft_sensor_report=soft_report,
        fault_report=fault_report,
        catalyst_lifecycle_report=lifecycle_report,
        validation_planning_report=validation_report,
    ).run(readings)
    report = CostSafetyAgent(control_report=control_report).run(readings)

    payload = {
        "agent_name": report.agent_name,
        "confidence": report.confidence,
        "summary": report.summary,
        "metrics": report.metrics,
        "recommendations": report.recommendations,
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
    }
    (OUT_DIR / "agent6_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Agent 6 成本安全评价模拟报告",
        "",
        f"- Agent: `{report.agent_name}`",
        f"- 评价可信度: `{report.confidence}`",
        f"- 摘要: {report.summary}",
        "",
        "## 动作成本安全排序",
        "",
    ]
    for item in report.metrics["evaluated_actions"]:
        lines.extend(
            [
                f"### {item['action_name']}（net={item['net_score']}，original={item['original_score']}）",
                "",
                f"- 安全收益: {item['safety_gain']}",
                f"- 金钱成本: {item['money_cost']}",
                f"- 时间成本: {item['time_cost']}",
                f"- 能耗成本: {item['energy_cost']}",
                f"- 风险成本: {item['risk_cost']}",
                f"- 需要人工复核: `{item['requires_human_review']}`",
                "",
            ]
        )
    lines.extend(["## 建议", ""])
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    (OUT_DIR / "agent6_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(report.summary)
    print(f"wrote {OUT_DIR / 'agent6_report.md'}")


if __name__ == "__main__":
    main()
