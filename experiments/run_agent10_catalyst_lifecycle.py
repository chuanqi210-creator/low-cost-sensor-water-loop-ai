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
from water_ai.agents.validation_planning_agent import ValidationPlanningAgent
from water_ai.domain import AgentReport
from water_ai.process_dynamics import generate_sensor_stream_from_process_state, initial_process_state


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "outputs" / "agent10_catalyst_lifecycle"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cases = [_regeneration_case(), _replacement_case()]
    (OUT_DIR / "agent10_report.json").write_text(json.dumps(cases, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = ["# Agent 10 催化剂生命周期模拟报告", ""]
    for case in cases:
        lines.extend(
            [
                f"## {case['case_id']}",
                "",
                f"- lifecycle summary: {case['lifecycle_summary']}",
                f"- lifecycle state: `{case['lifecycle_state']}`",
                f"- maintenance decision: `{case['maintenance_decision']}`",
                f"- validation plan: `{case['validation_plan']}`",
                f"- final actions: `{case['final_actions']}`",
                f"- blocked: `{case['blocked_actions']}`",
                "",
            ]
        )
    (OUT_DIR / "agent10_report.md").write_text("\n".join(lines), encoding="utf-8")

    for case in cases:
        print(f"{case['case_id']}: {case['final_actions']}")
    print(f"wrote {OUT_DIR / 'agent10_report.md'}")


def _regeneration_case() -> dict[str, object]:
    readings = generate_sensor_stream_from_process_state(initial_process_state("catalyst_deactivation"), n=24, seed=7)
    dq_report = DataQualityAgent().run(readings)
    soft_report = SoftSensorAgent(data_quality_report=dq_report).run(readings)
    mechanism_report = MechanismAgent(data_quality_report=dq_report, soft_sensor_report=soft_report).run(readings)
    fault_report = FaultDiagnosisAgent(
        data_quality_report=dq_report,
        soft_sensor_report=soft_report,
        mechanism_report=mechanism_report,
    ).run(readings)
    return _run_downstream_case(
        case_id="remaining_life_regeneration",
        soft_report=soft_report,
        fault_report=fault_report,
        readings=readings,
    )


def _replacement_case() -> dict[str, object]:
    soft_report = AgentReport(
        agent_name="soft_sensor_agent",
        confidence=0.9,
        summary="synthetic exhausted lifecycle state",
        issues=[],
        recommendations=[],
        metrics={
            "state_estimate": {
                "pollutant_residual_risk": 0.58,
                "reaction_completion": 0.42,
                "oxidant_remaining": 0.72,
                "catalyst_activity": 0.28,
                "catalyst_lifetime_fraction": 0.24,
                "catalyst_regen_count": 3,
                "catalyst_age_cycles": 12,
                "catalyst_regeneration_potential": 0.18,
                "catalyst_replacement_urgency": 0.86,
                "matrix_interference": 0.26,
                "byproduct_risk": 0.18,
                "hydraulic_confidence": 0.91,
                "sensor_confidence": 0.93,
                "compliance_probability": 0.46,
                "recycle_gain": 0.34,
                "release_readiness": 0.40,
                "cycle_id": 4,
            }
        },
    )
    fault_report = AgentReport(
        agent_name="fault_diagnosis_agent",
        confidence=0.82,
        summary="synthetic lifecycle exhaustion fault",
        issues=[],
        recommendations=[],
        metrics={"ranked_faults": [{"fault_id": "catalyst_lifecycle_exhaustion", "score": 0.82}]},
    )
    return _run_downstream_case(
        case_id="exhausted_life_replacement",
        soft_report=soft_report,
        fault_report=fault_report,
        readings=[],
    )


def _run_downstream_case(
    *,
    case_id: str,
    soft_report: AgentReport,
    fault_report: AgentReport,
    readings: list,
) -> dict[str, object]:
    lifecycle_report = CatalystLifecycleAgent(soft_sensor_report=soft_report, fault_report=fault_report).run(readings)
    validation_report = ValidationPlanningAgent(soft_sensor_report=soft_report, fault_report=fault_report).run(readings)
    control_report = ControlStrategyAgent(
        soft_sensor_report=soft_report,
        fault_report=fault_report,
        catalyst_lifecycle_report=lifecycle_report,
        validation_planning_report=validation_report,
    ).run(readings)
    cost_report = CostSafetyAgent(control_report=control_report).run(readings)
    arbitration_report = ArbitrationAgent(
        soft_sensor_report=soft_report,
        control_report=control_report,
        cost_safety_report=cost_report,
    ).run(readings)
    final_actions = [action["action_id"] for action in arbitration_report.metrics["final_plan"]]
    return {
        "case_id": case_id,
        "lifecycle_summary": lifecycle_report.summary,
        "lifecycle_state": lifecycle_report.metrics["lifecycle_state"],
        "maintenance_decision": lifecycle_report.metrics["maintenance_decision"],
        "validation_plan": validation_report.metrics["validation_plan"],
        "evaluated_actions": cost_report.metrics["evaluated_actions"],
        "final_actions": final_actions,
        "blocked_actions": arbitration_report.metrics["blocked_actions"],
    }


if __name__ == "__main__":
    main()
