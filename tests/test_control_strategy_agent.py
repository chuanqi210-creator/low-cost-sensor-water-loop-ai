from water_ai.agents.control_strategy_agent import ControlStrategyAgent
from water_ai.agents.data_quality_agent import DataQualityAgent
from water_ai.agents.fault_diagnosis_agent import FaultDiagnosisAgent
from water_ai.agents.mechanism_agent import MechanismAgent
from water_ai.agents.soft_sensor_agent import SoftSensorAgent
from water_ai.domain import AgentReport
from water_ai.process_dynamics import generate_sensor_stream_from_process_state, initial_process_state
from water_ai.simulation import generate_low_cost_sensor_stream


def test_control_strategy_blocks_release_under_uncertainty() -> None:
    readings = generate_low_cost_sensor_stream(n=72, seed=7, inject_faults=True)
    dq_report = DataQualityAgent().run(readings)
    soft_report = SoftSensorAgent(data_quality_report=dq_report).run(readings)
    mechanism_report = MechanismAgent(data_quality_report=dq_report, soft_sensor_report=soft_report).run(readings)
    fault_report = FaultDiagnosisAgent(
        data_quality_report=dq_report,
        soft_sensor_report=soft_report,
        mechanism_report=mechanism_report,
    ).run(readings)
    report = ControlStrategyAgent(soft_sensor_report=soft_report, fault_report=fault_report).run(readings)

    actions = report.metrics["ranked_actions"]
    action_ids = [action["action_id"] for action in actions]
    executable_ids = [action["action_id"] for action in report.metrics["executable_plan"]]
    assert "hold_for_validation" in action_ids
    assert "hold_for_validation" in executable_ids
    assert "inspect_hydraulics" in action_ids
    assert "calibrate_sensors" in action_ids
    assert actions[0]["action_id"] != "release"
    assert next(action for action in actions if action["action_id"] == "release")["score"] < 0.35


def test_control_strategy_maps_cycle_window_fault_to_dynamic_recirculation() -> None:
    readings = generate_sensor_stream_from_process_state(initial_process_state("reaction_time_insufficient"), n=24, seed=7)
    dq_report = DataQualityAgent().run(readings)
    soft_report = SoftSensorAgent(data_quality_report=dq_report).run(readings)
    mechanism_report = MechanismAgent(data_quality_report=dq_report, soft_sensor_report=soft_report).run(readings)
    fault_report = FaultDiagnosisAgent(
        data_quality_report=dq_report,
        soft_sensor_report=soft_report,
        mechanism_report=mechanism_report,
    ).run(readings)
    report = ControlStrategyAgent(soft_sensor_report=soft_report, fault_report=fault_report).run(readings)

    actions = report.metrics["ranked_actions"]
    recirculate = next(action for action in actions if action["action_id"] == "recirculate")
    assert actions[0]["action_id"] == "recirculate"
    assert recirculate["parameters"]["recycle_ratio"] > 0.35
    assert recirculate["parameters"]["extra_retention_min"] > 15


def test_control_strategy_maps_catalyst_deactivation_to_regeneration() -> None:
    readings = generate_sensor_stream_from_process_state(initial_process_state("catalyst_deactivation"), n=24, seed=7)
    dq_report = DataQualityAgent().run(readings)
    soft_report = SoftSensorAgent(data_quality_report=dq_report).run(readings)
    mechanism_report = MechanismAgent(data_quality_report=dq_report, soft_sensor_report=soft_report).run(readings)
    fault_report = FaultDiagnosisAgent(
        data_quality_report=dq_report,
        soft_sensor_report=soft_report,
        mechanism_report=mechanism_report,
    ).run(readings)
    report = ControlStrategyAgent(soft_sensor_report=soft_report, fault_report=fault_report).run(readings)

    actions = report.metrics["ranked_actions"]
    regenerate = next(action for action in actions if action["action_id"] == "regenerate_catalyst")
    assert regenerate["score"] >= 0.75
    assert regenerate["parameters"]["regen_intensity"] >= 0.6
    assert "regenerate_catalyst" in [action["action_id"] for action in report.metrics["executable_plan"]]


def test_control_strategy_applies_knowledge_action_biases() -> None:
    soft_report = AgentReport(
        agent_name="soft_sensor_agent",
        confidence=0.9,
        summary="",
        issues=[],
        recommendations=[],
        metrics={
            "state_estimate": {
                "pollutant_residual_risk": 0.46,
                "reaction_completion": 0.45,
                "oxidant_remaining": 0.36,
                "catalyst_activity": 0.7,
                "matrix_interference": 0.32,
                "byproduct_risk": 0.1,
                "hydraulic_confidence": 0.95,
                "sensor_confidence": 0.96,
                "compliance_probability": 0.66,
                "recycle_gain": 0.32,
                "release_readiness": 0.66,
                "cycle_id": 1,
            }
        },
    )
    fault_report = AgentReport(
        agent_name="fault_diagnosis_agent",
        confidence=0.8,
        summary="",
        issues=[],
        recommendations=[],
        metrics={
            "ranked_faults": [{"fault_id": "oxidant_limitation", "score": 0.5}],
            "knowledge_matches": [
                {
                    "entry_id": "kb_oxidant_limited_refractory_organics",
                    "match_score": 0.82,
                    "action_biases": {"dose_oxidant": 0.20, "recirculate": 0.10, "release": -0.20},
                }
            ],
        },
    )

    report = ControlStrategyAgent(soft_sensor_report=soft_report, fault_report=fault_report).run([])
    dose = next(action for action in report.metrics["ranked_actions"] if action["action_id"] == "dose_oxidant")

    assert report.metrics["knowledge_action_biases"]["dose_oxidant"] > 0
    assert dose["score"] >= 0.40
    assert dose["evidence"]["knowledge_action_bias"] > 0


def test_control_strategy_suppresses_low_matrix_switching() -> None:
    readings = generate_sensor_stream_from_process_state(initial_process_state("sensor_faults"), n=24, seed=7)
    dq_report = DataQualityAgent().run(readings)
    soft_report = SoftSensorAgent(data_quality_report=dq_report).run(readings)
    mechanism_report = MechanismAgent(data_quality_report=dq_report, soft_sensor_report=soft_report).run(readings)
    fault_report = FaultDiagnosisAgent(
        data_quality_report=dq_report,
        soft_sensor_report=soft_report,
        mechanism_report=mechanism_report,
    ).run(readings)
    report = ControlStrategyAgent(soft_sensor_report=soft_report, fault_report=fault_report).run(readings)

    switch = next(action for action in report.metrics["ranked_actions"] if action["action_id"] == "switch_or_pretreat")
    assert switch["score"] < 0.35
