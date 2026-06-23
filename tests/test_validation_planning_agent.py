from water_ai.agents.control_strategy_agent import ControlStrategyAgent
from water_ai.agents.validation_planning_agent import ValidationPlanningAgent
from water_ai.domain import AgentReport


def test_validation_planning_agent_targets_byproduct_guard() -> None:
    soft_report = _soft_report(
        {
            "pollutant_residual_risk": 0.32,
            "release_readiness": 0.61,
            "sensor_confidence": 0.92,
            "byproduct_risk": 0.72,
            "oxidant_remaining": 0.78,
            "matrix_interference": 0.62,
            "catalyst_replacement_urgency": 0.2,
        }
    )
    fault_report = _fault_report(["byproduct_or_overoxidation_risk", "matrix_interference"])

    report = ValidationPlanningAgent(soft_sensor_report=soft_report, fault_report=fault_report).run([])
    plan = report.metrics["validation_plan"]

    assert plan["plan_name"] == "matrix_shock_characterization"
    assert "byproduct_screening" in plan["targets"]
    assert plan["validation_delay_min"] >= 22
    assert plan["urgency"] >= 0.7


def test_control_strategy_uses_validation_plan_for_hold_action() -> None:
    soft_report = _soft_report(
        {
            "pollutant_residual_risk": 0.48,
            "reaction_completion": 0.64,
            "oxidant_remaining": 0.72,
            "catalyst_activity": 0.72,
            "matrix_interference": 0.2,
            "byproduct_risk": 0.16,
            "hydraulic_confidence": 0.92,
            "sensor_confidence": 0.58,
            "compliance_probability": 0.66,
            "recycle_gain": 0.24,
            "release_readiness": 0.42,
            "cycle_id": 2,
        }
    )
    fault_report = _fault_report(["sensor_data_unreliable", "release_evidence_insufficient"])
    validation_report = ValidationPlanningAgent(soft_sensor_report=soft_report, fault_report=fault_report).run([])

    control_report = ControlStrategyAgent(
        soft_sensor_report=soft_report,
        fault_report=fault_report,
        validation_planning_report=validation_report,
    ).run([])
    hold_action = next(action for action in control_report.metrics["ranked_actions"] if action["action_id"] == "hold_for_validation")

    assert hold_action["parameters"]["validation_plan"] == "release_gate_validation"
    assert hold_action["parameters"]["hold_min"] >= 32
    assert "target_pollutant" in hold_action["parameters"]["validation"]


def _soft_report(state: dict[str, float]) -> AgentReport:
    return AgentReport(
        agent_name="soft_sensor_agent",
        confidence=0.9,
        summary="",
        issues=[],
        recommendations=[],
        metrics={"state_estimate": state},
    )


def _fault_report(fault_ids: list[str]) -> AgentReport:
    return AgentReport(
        agent_name="fault_diagnosis_agent",
        confidence=0.8,
        summary="",
        issues=[],
        recommendations=[],
        metrics={"ranked_faults": [{"fault_id": fault_id, "score": 0.75} for fault_id in fault_ids]},
    )
