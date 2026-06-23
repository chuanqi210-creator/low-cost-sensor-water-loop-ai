from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.catalyst_lifecycle_agent import CatalystLifecycleAgent
from water_ai.agents.control_strategy_agent import ControlStrategyAgent
from water_ai.agents.data_quality_agent import DataQualityAgent
from water_ai.agents.fault_diagnosis_agent import FaultDiagnosisAgent
from water_ai.agents.mechanism_agent import MechanismAgent
from water_ai.agents.soft_sensor_agent import SoftSensorAgent
from water_ai.agents.validation_planning_agent import ValidationPlanningAgent
from water_ai.simulation import generate_low_cost_sensor_stream


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "outputs" / "agent5_control_strategy"


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
    report = ControlStrategyAgent(
        soft_sensor_report=soft_report,
        fault_report=fault_report,
        catalyst_lifecycle_report=lifecycle_report,
        validation_planning_report=validation_report,
    ).run(readings)

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
    (OUT_DIR / "agent5_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Agent 5 控制策略模拟报告",
        "",
        f"- Agent: `{report.agent_name}`",
        f"- 策略可信度: `{report.confidence}`",
        f"- 摘要: {report.summary}",
        "",
        "## 动作排序",
        "",
    ]
    for action in report.metrics["ranked_actions"]:
        lines.extend(
            [
                f"### {action['action_name']}（score={action['score']}）",
                "",
                f"- 参数: `{action['parameters']}`",
                f"- 需要人工复核: `{action['requires_human_review']}`",
                f"- 依据: `{action['evidence']}`",
                "",
            ]
        )
    lines.extend(["## 可执行计划", ""])
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    (OUT_DIR / "agent5_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(report.summary)
    print(f"wrote {OUT_DIR / 'agent5_report.md'}")


if __name__ == "__main__":
    main()
