from dataclasses import replace

from water_ai.agents.catalyst_lifecycle_agent import CatalystLifecycleAgent
from water_ai.agents.control_strategy_agent import ControlStrategyAgent
from water_ai.agents.data_quality_agent import DataQualityAgent
from water_ai.agents.fault_diagnosis_agent import FaultDiagnosisAgent
from water_ai.agents.mechanism_agent import MechanismAgent
from water_ai.agents.soft_sensor_agent import SoftSensorAgent
from water_ai.domain import AgentReport
from water_ai.process_dynamics import apply_actions_to_process_state, generate_sensor_stream_from_process_state, initial_process_state


def test_lifecycle_agent_prefers_regeneration_when_life_remains() -> None:
    readings = generate_sensor_stream_from_process_state(initial_process_state("catalyst_deactivation"), n=24, seed=7)
    dq_report = DataQualityAgent().run(readings)
    soft_report = SoftSensorAgent(data_quality_report=dq_report).run(readings)
    mechanism_report = MechanismAgent(data_quality_report=dq_report, soft_sensor_report=soft_report).run(readings)
    fault_report = FaultDiagnosisAgent(
        data_quality_report=dq_report,
        soft_sensor_report=soft_report,
        mechanism_report=mechanism_report,
    ).run(readings)

    report = CatalystLifecycleAgent(soft_sensor_report=soft_report, fault_report=fault_report).run(readings)

    assert report.metrics["maintenance_decision"]["action_id"] == "regenerate_catalyst"
    assert report.metrics["lifecycle_state"]["replacement_urgency"] < 0.62


def test_lifecycle_agent_prefers_replacement_when_regeneration_is_exhausted() -> None:
    soft_report = _soft_report(
        {
            "catalyst_activity": 0.28,
            "catalyst_lifetime_fraction": 0.24,
            "catalyst_regen_count": 3,
            "catalyst_age_cycles": 12,
            "catalyst_regeneration_potential": 0.18,
            "catalyst_replacement_urgency": 0.86,
        }
    )
    fault_report = _fault_report("catalyst_lifecycle_exhaustion", 0.82)

    report = CatalystLifecycleAgent(soft_sensor_report=soft_report, fault_report=fault_report).run([])

    assert report.metrics["maintenance_decision"]["action_id"] == "replace_catalyst"
    assert report.issues


def test_process_dynamics_tracks_regeneration_decay_and_replacement_reset() -> None:
    state = replace(
        initial_process_state("catalyst_deactivation"),
        catalyst_activity=0.28,
        catalyst_lifetime_fraction=0.35,
        catalyst_regen_count=2,
        catalyst_age_cycles=11,
    )

    regenerated = apply_actions_to_process_state(
        state,
        [{"action_id": "regenerate_catalyst", "parameters": {"regen_intensity": 0.8, "downtime_min": 60}}],
    )
    assert regenerated is not None
    assert regenerated.catalyst_regen_count == 3
    assert regenerated.catalyst_lifetime_fraction < state.catalyst_lifetime_fraction
    assert regenerated.catalyst_activity > state.catalyst_activity

    replaced = apply_actions_to_process_state(
        regenerated,
        [{"action_id": "replace_catalyst", "parameters": {"downtime_min": 90}}],
    )
    assert replaced is not None
    assert replaced.catalyst_regen_count == 0
    assert replaced.catalyst_age_cycles == 0
    assert replaced.catalyst_lifetime_fraction == 1.0
    assert replaced.catalyst_activity > regenerated.catalyst_activity


def test_control_strategy_uses_lifecycle_agent_for_replacement_action() -> None:
    soft_report = _soft_report(
        {
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
    )
    fault_report = _fault_report("catalyst_lifecycle_exhaustion", 0.82)
    lifecycle_report = CatalystLifecycleAgent(soft_sensor_report=soft_report, fault_report=fault_report).run([])

    report = ControlStrategyAgent(
        soft_sensor_report=soft_report,
        fault_report=fault_report,
        catalyst_lifecycle_report=lifecycle_report,
    ).run([])

    actions = {action["action_id"]: action for action in report.metrics["ranked_actions"]}
    assert actions["replace_catalyst"]["score"] >= 0.7
    assert actions["replace_catalyst"]["score"] > actions["regenerate_catalyst"]["score"]


def _soft_report(state: dict[str, float]) -> AgentReport:
    return AgentReport(
        agent_name="soft_sensor_agent",
        confidence=0.9,
        summary="",
        issues=[],
        recommendations=[],
        metrics={"state_estimate": state},
    )


def _fault_report(fault_id: str, score: float) -> AgentReport:
    return AgentReport(
        agent_name="fault_diagnosis_agent",
        confidence=0.8,
        summary="",
        issues=[],
        recommendations=[],
        metrics={"ranked_faults": [{"fault_id": fault_id, "score": score}]},
    )
