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
from water_ai.process_dynamics import generate_sensor_stream_from_process_state, initial_process_state


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "outputs" / "scenario_sweep"


def run_chain(scenario: str) -> dict[str, object]:
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
    return {
        "scenario": scenario,
        "dq_summary": dq_report.summary,
        "state": soft_report.metrics["state_estimate"],
        "fault_top": fault_report.metrics["ranked_faults"][0],
        "catalyst_lifecycle": lifecycle_report.metrics["maintenance_decision"],
        "validation_plan": validation_report.metrics["validation_plan"],
        "strategy_profile": strategy_report.metrics["selected_profile"],
        "final_plan": arbitration_report.metrics["final_plan"],
        "blocked_actions": arbitration_report.metrics["blocked_actions"],
        "summary": arbitration_report.summary,
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    scenarios = [
        "clean_release",
        "sensor_faults",
        "oxidant_limitation",
        "reaction_time_insufficient",
        "catalyst_deactivation",
        "matrix_shock",
    ]
    results = [run_chain(scenario) for scenario in scenarios]
    (OUT_DIR / "scenario_sweep.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = ["# 多场景闭环决策扫查", ""]
    for result in results:
        lines.extend(
            [
                f"## {result['scenario']}",
                "",
                f"- summary: {result['summary']}",
                f"- state: `{result['state']}`",
                f"- top fault: `{result['fault_top']}`",
                f"- catalyst lifecycle: `{result['catalyst_lifecycle']}`",
                f"- validation plan: `{result['validation_plan']}`",
                f"- strategy profile: `{result['strategy_profile']}`",
                f"- final actions: `{[a['action_id'] for a in result['final_plan']]}`",
                f"- blocked: `{result['blocked_actions']}`",
                "",
            ]
        )
    (OUT_DIR / "scenario_sweep.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(f"{r['scenario']}: {[a['action_id'] for a in r['final_plan']]} blocked={r['blocked_actions']}" for r in results))


if __name__ == "__main__":
    main()
