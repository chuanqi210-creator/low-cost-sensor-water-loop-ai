from water_ai.agents.arbitration_agent import ArbitrationAgent
from water_ai.agents.control_strategy_agent import ControlStrategyAgent
from water_ai.agents.cost_safety_agent import CostSafetyAgent
from water_ai.agents.data_quality_agent import DataQualityAgent
from water_ai.agents.fault_diagnosis_agent import FaultDiagnosisAgent
from water_ai.agents.mechanism_agent import MechanismAgent
from water_ai.agents.soft_sensor_agent import SoftSensorAgent
from water_ai.domain import AgentReport
from water_ai.process_dynamics import generate_sensor_stream_from_process_state, initial_process_state
from water_ai.simulation import generate_low_cost_sensor_stream


def test_arbitration_blocks_unsafe_release_and_keeps_validation_plan() -> None:
    readings = generate_low_cost_sensor_stream(n=72, seed=7, inject_faults=True)
    dq_report = DataQualityAgent().run(readings)
    soft_report = SoftSensorAgent(data_quality_report=dq_report).run(readings)
    mechanism_report = MechanismAgent(data_quality_report=dq_report, soft_sensor_report=soft_report).run(readings)
    fault_report = FaultDiagnosisAgent(
        data_quality_report=dq_report,
        soft_sensor_report=soft_report,
        mechanism_report=mechanism_report,
    ).run(readings)
    control_report = ControlStrategyAgent(soft_sensor_report=soft_report, fault_report=fault_report).run(readings)
    cost_report = CostSafetyAgent(control_report=control_report).run(readings)
    report = ArbitrationAgent(
        soft_sensor_report=soft_report,
        control_report=control_report,
        cost_safety_report=cost_report,
    ).run(readings)

    final_ids = [action["action_id"] for action in report.metrics["final_plan"]]
    assert "release" not in final_ids
    assert "dose_oxidant" not in final_ids
    assert "recirculate" not in final_ids
    assert "hold_for_validation" in final_ids
    assert "release" in report.metrics["blocked_actions"]
    assert any(not gate["passed"] for gate in report.metrics["safety_gates"])


def test_arbitration_blocks_release_when_residual_gate_fails() -> None:
    readings = generate_low_cost_sensor_stream(n=24, seed=7, scenario="reaction_time_insufficient")
    dq_report = DataQualityAgent().run(readings)
    soft_report = SoftSensorAgent(data_quality_report=dq_report).run(readings)
    mechanism_report = MechanismAgent(data_quality_report=dq_report, soft_sensor_report=soft_report).run(readings)
    fault_report = FaultDiagnosisAgent(
        data_quality_report=dq_report,
        soft_sensor_report=soft_report,
        mechanism_report=mechanism_report,
    ).run(readings)
    control_report = ControlStrategyAgent(soft_sensor_report=soft_report, fault_report=fault_report).run(readings)
    cost_report = CostSafetyAgent(control_report=control_report).run(readings)
    report = ArbitrationAgent(
        soft_sensor_report=soft_report,
        control_report=control_report,
        cost_safety_report=cost_report,
    ).run(readings)

    final_ids = [action["action_id"] for action in report.metrics["final_plan"]]
    assert "release" not in final_ids
    assert "release" in report.metrics["blocked_actions"]


def test_arbitration_treats_release_as_terminal_action() -> None:
    readings = generate_low_cost_sensor_stream(n=72, seed=11, scenario="clean_release")
    dq_report = DataQualityAgent().run(readings)
    soft_report = SoftSensorAgent(data_quality_report=dq_report).run(readings)
    mechanism_report = MechanismAgent(data_quality_report=dq_report, soft_sensor_report=soft_report).run(readings)
    fault_report = FaultDiagnosisAgent(
        data_quality_report=dq_report,
        soft_sensor_report=soft_report,
        mechanism_report=mechanism_report,
    ).run(readings)
    control_report = ControlStrategyAgent(soft_sensor_report=soft_report, fault_report=fault_report).run(readings)
    cost_report = CostSafetyAgent(control_report=control_report).run(readings)
    report = ArbitrationAgent(
        soft_sensor_report=soft_report,
        control_report=control_report,
        cost_safety_report=cost_report,
    ).run(readings)

    final_ids = [action["action_id"] for action in report.metrics["final_plan"]]
    assert final_ids == ["release"]


def test_arbitration_blocks_release_under_low_hydraulic_confidence() -> None:
    readings = generate_sensor_stream_from_process_state(initial_process_state("sensor_faults"), n=24, seed=7)
    dq_report = DataQualityAgent().run(readings)
    soft_report = SoftSensorAgent(data_quality_report=dq_report).run(readings)
    mechanism_report = MechanismAgent(data_quality_report=dq_report, soft_sensor_report=soft_report).run(readings)
    fault_report = FaultDiagnosisAgent(
        data_quality_report=dq_report,
        soft_sensor_report=soft_report,
        mechanism_report=mechanism_report,
    ).run(readings)
    control_report = ControlStrategyAgent(soft_sensor_report=soft_report, fault_report=fault_report).run(readings)
    cost_report = CostSafetyAgent(control_report=control_report).run(readings)
    report = ArbitrationAgent(
        soft_sensor_report=soft_report,
        control_report=control_report,
        cost_safety_report=cost_report,
    ).run(readings)

    final_ids = [action["action_id"] for action in report.metrics["final_plan"]]
    failed_gates = [gate["gate_id"] for gate in report.metrics["safety_gates"] if not gate["passed"]]
    assert "release" not in final_ids
    assert "release" in report.metrics["blocked_actions"]
    assert "hydraulic_confidence_gate" in failed_gates


def test_arbitration_orders_pretreatment_before_recirculation_under_matrix_shock() -> None:
    readings = generate_low_cost_sensor_stream(n=72, seed=7, scenario="matrix_shock")
    dq_report = DataQualityAgent().run(readings)
    soft_report = SoftSensorAgent(data_quality_report=dq_report).run(readings)
    mechanism_report = MechanismAgent(data_quality_report=dq_report, soft_sensor_report=soft_report).run(readings)
    fault_report = FaultDiagnosisAgent(
        data_quality_report=dq_report,
        soft_sensor_report=soft_report,
        mechanism_report=mechanism_report,
    ).run(readings)
    control_report = ControlStrategyAgent(soft_sensor_report=soft_report, fault_report=fault_report).run(readings)
    cost_report = CostSafetyAgent(control_report=control_report).run(readings)
    report = ArbitrationAgent(
        soft_sensor_report=soft_report,
        control_report=control_report,
        cost_safety_report=cost_report,
    ).run(readings)

    final_ids = [action["action_id"] for action in report.metrics["final_plan"]]
    assert final_ids[0] == "switch_or_pretreat"
    assert "recirculate" in final_ids
    assert final_ids.index("switch_or_pretreat") < final_ids.index("recirculate")


def test_arbitration_orders_regeneration_before_recirculation_under_catalyst_deactivation() -> None:
    readings = generate_sensor_stream_from_process_state(initial_process_state("catalyst_deactivation"), n=24, seed=7)
    dq_report = DataQualityAgent().run(readings)
    soft_report = SoftSensorAgent(data_quality_report=dq_report).run(readings)
    mechanism_report = MechanismAgent(data_quality_report=dq_report, soft_sensor_report=soft_report).run(readings)
    fault_report = FaultDiagnosisAgent(
        data_quality_report=dq_report,
        soft_sensor_report=soft_report,
        mechanism_report=mechanism_report,
    ).run(readings)
    control_report = ControlStrategyAgent(soft_sensor_report=soft_report, fault_report=fault_report).run(readings)
    cost_report = CostSafetyAgent(control_report=control_report).run(readings)
    report = ArbitrationAgent(
        soft_sensor_report=soft_report,
        control_report=control_report,
        cost_safety_report=cost_report,
    ).run(readings)

    final_ids = [action["action_id"] for action in report.metrics["final_plan"]]
    assert final_ids[:2] == ["regenerate_catalyst", "recirculate"]
    assert "release" in report.metrics["blocked_actions"]


def test_arbitration_uses_strategy_objective_for_final_selection() -> None:
    soft_report = AgentReport(
        agent_name="soft_sensor_agent",
        confidence=0.9,
        summary="",
        issues=[],
        recommendations=[],
        metrics={
            "state_estimate": {
                "pollutant_residual_risk": 0.22,
                "reaction_completion": 0.86,
                "oxidant_remaining": 0.12,
                "catalyst_activity": 0.72,
                "matrix_interference": 0.2,
                "byproduct_risk": 0.2,
                "hydraulic_confidence": 0.94,
                "sensor_confidence": 0.95,
                "compliance_probability": 0.9,
                "recycle_gain": 0.5,
                "release_readiness": 0.86,
                "cycle_id": 2,
            }
        },
    )
    cost_report = AgentReport(
        agent_name="cost_safety_agent",
        confidence=0.9,
        summary="",
        issues=[],
        recommendations=[],
        metrics={
            "evaluated_actions": [
                {
                    "action_id": "recirculate",
                    "action_name": "继续回流处理",
                    "original_score": 0.82,
                    "net_score": 0.8,
                    "objective_score": 0.2,
                    "parameters": {"recycle_ratio": 0.5},
                },
                {
                    "action_id": "hold_for_validation",
                    "action_name": "暂存并旁路验证",
                    "original_score": 0.72,
                    "net_score": 0.12,
                    "objective_score": 0.68,
                    "parameters": {"hold_min": 20},
                },
            ]
        },
    )
    report = ArbitrationAgent(soft_sensor_report=soft_report, cost_safety_report=cost_report).run([])

    final_ids = [action["action_id"] for action in report.metrics["final_plan"]]
    assert final_ids == ["hold_for_validation"]


def test_arbitration_blocks_release_under_byproduct_risk() -> None:
    soft_report = AgentReport(
        agent_name="soft_sensor_agent",
        confidence=0.9,
        summary="",
        issues=[],
        recommendations=[],
        metrics={
            "state_estimate": {
                "pollutant_residual_risk": 0.18,
                "reaction_completion": 0.86,
                "oxidant_remaining": 0.82,
                "catalyst_activity": 0.72,
                "matrix_interference": 0.62,
                "byproduct_risk": 0.72,
                "hydraulic_confidence": 0.94,
                "sensor_confidence": 0.95,
                "compliance_probability": 0.9,
                "recycle_gain": 0.1,
                "release_readiness": 0.86,
                "cycle_id": 3,
            }
        },
    )
    cost_report = AgentReport(
        agent_name="cost_safety_agent",
        confidence=0.9,
        summary="",
        issues=[],
        recommendations=[],
        metrics={
            "evaluated_actions": [
                {
                    "action_id": "release",
                    "action_name": "达标放行",
                    "original_score": 0.8,
                    "net_score": 0.8,
                    "parameters": {},
                }
            ]
        },
    )
    report = ArbitrationAgent(soft_sensor_report=soft_report, cost_safety_report=cost_report).run([])

    final_ids = [action["action_id"] for action in report.metrics["final_plan"]]
    failed_gates = [gate["gate_id"] for gate in report.metrics["safety_gates"] if not gate["passed"]]
    assert "release" not in final_ids
    assert "release" in report.metrics["blocked_actions"]
    assert "byproduct_risk_gate" in failed_gates
