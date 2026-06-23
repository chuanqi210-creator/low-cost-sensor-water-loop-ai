from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.data_quality_agent import DataQualityAgent
from water_ai.agents.fault_diagnosis_agent import FaultDiagnosisAgent
from water_ai.agents.mechanism_agent import MechanismAgent
from water_ai.agents.soft_sensor_agent import SoftSensorAgent
from water_ai.agents.validation_planning_agent import ValidationPlanningAgent
from water_ai.process_dynamics import generate_sensor_stream_from_process_state, initial_process_state


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "outputs" / "agent11_validation_planning"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    scenarios = [
        "sensor_faults",
        "oxidant_limitation",
        "reaction_time_insufficient",
        "catalyst_deactivation",
        "matrix_shock",
    ]
    results = [_run_case(scenario) for scenario in scenarios]
    (OUT_DIR / "agent11_report.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = ["# Agent 11 旁路验证规划模拟报告", ""]
    for result in results:
        lines.extend(
            [
                f"## {result['scenario']}",
                "",
                f"- summary: {result['summary']}",
                f"- validation plan: `{result['validation_plan']}`",
                f"- top fault: `{result['top_fault']}`",
                "",
            ]
        )
    (OUT_DIR / "agent11_report.md").write_text("\n".join(lines), encoding="utf-8")

    for result in results:
        plan = result["validation_plan"]
        print(f"{result['scenario']}: {plan['plan_name']} targets={plan['targets']}")
    print(f"wrote {OUT_DIR / 'agent11_report.md'}")


def _run_case(scenario: str) -> dict[str, object]:
    observation_window_min = 72 if scenario == "clean_release" else 24
    readings = generate_sensor_stream_from_process_state(initial_process_state(scenario), n=observation_window_min, seed=7)
    dq_report = DataQualityAgent().run(readings)
    soft_report = SoftSensorAgent(data_quality_report=dq_report).run(readings)
    mechanism_report = MechanismAgent(data_quality_report=dq_report, soft_sensor_report=soft_report).run(readings)
    fault_report = FaultDiagnosisAgent(
        data_quality_report=dq_report,
        soft_sensor_report=soft_report,
        mechanism_report=mechanism_report,
    ).run(readings)
    validation_report = ValidationPlanningAgent(soft_sensor_report=soft_report, fault_report=fault_report).run(readings)
    return {
        "scenario": scenario,
        "summary": validation_report.summary,
        "validation_plan": validation_report.metrics["validation_plan"],
        "top_fault": fault_report.metrics["ranked_faults"][0],
        "recommendations": validation_report.recommendations,
    }


if __name__ == "__main__":
    main()
