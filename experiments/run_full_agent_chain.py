from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.arbitration_agent import ArbitrationAgent
from water_ai.agents.catalyst_lifecycle_agent import CatalystLifecycleAgent
from water_ai.agents.control_strategy_agent import ControlStrategyAgent
from water_ai.agents.cost_safety_agent import CostSafetyAgent
from water_ai.agents.data_quality_agent import DataQualityAgent
from water_ai.agents.fault_diagnosis_agent import FaultDiagnosisAgent
from water_ai.agents.mechanism_agent import MechanismAgent
from water_ai.agents.soft_sensor_agent import SoftSensorAgent
from water_ai.agents.strategy_profile_agent import StrategyProfileAgent
from water_ai.agents.validation_planning_agent import ValidationPlanningAgent
from water_ai.simulation import generate_low_cost_sensor_stream


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "outputs" / "full_chain"


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
    strategy_report = StrategyProfileAgent(soft_sensor_report=soft_report, fault_report=fault_report).run(readings)
    cost_report = CostSafetyAgent(
        control_report=control_report,
        objective_profile=str(strategy_report.metrics["selected_profile"]),
    ).run(readings)
    arbitration_report = ArbitrationAgent(
        soft_sensor_report=soft_report,
        control_report=control_report,
        cost_safety_report=cost_report,
    ).run(readings)

    reports = {
        "data_quality": dq_report,
        "soft_sensor": soft_report,
        "mechanism": mechanism_report,
        "fault_diagnosis": fault_report,
        "catalyst_lifecycle": lifecycle_report,
        "validation_planning": validation_report,
        "control_strategy": control_report,
        "strategy_profile": strategy_report,
        "cost_safety": cost_report,
        "arbitration": arbitration_report,
    }

    payload = {}
    for name, report in reports.items():
        payload[name] = {
            "agent_name": report.agent_name,
            "confidence": report.confidence,
            "summary": report.summary,
            "recommendations": report.recommendations,
            "metrics": report.metrics,
        }
    (OUT_DIR / "full_chain_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = ["# 多智能体闭环全链条模拟报告", ""]
    for name, report in reports.items():
        lines.extend(
            [
                f"## {name}",
                "",
                f"- Agent: `{report.agent_name}`",
                f"- confidence: `{report.confidence}`",
                f"- summary: {report.summary}",
                "",
            ]
        )
        for rec in report.recommendations[:5]:
            lines.append(f"- {rec}")
        lines.append("")
    (OUT_DIR / "full_chain_report.md").write_text("\n".join(lines), encoding="utf-8")

    print(arbitration_report.summary)
    print(f"wrote {OUT_DIR / 'full_chain_report.md'}")


if __name__ == "__main__":
    main()
