from water_ai.agents.data_quality_agent import DataQualityAgent
from water_ai.agents.fault_diagnosis_agent import FaultDiagnosisAgent
from water_ai.agents.mechanism_agent import MechanismAgent
from water_ai.agents.soft_sensor_agent import SoftSensorAgent
from water_ai.domain import AgentReport
from water_ai.process_dynamics import generate_sensor_stream_from_process_state, initial_process_state
from water_ai.simulation import generate_low_cost_sensor_stream


def test_fault_diagnosis_prioritizes_actionable_faults() -> None:
    readings = generate_low_cost_sensor_stream(n=72, seed=7, inject_faults=True)
    dq_report = DataQualityAgent().run(readings)
    soft_report = SoftSensorAgent(data_quality_report=dq_report).run(readings)
    mechanism_report = MechanismAgent(data_quality_report=dq_report, soft_sensor_report=soft_report).run(readings)
    report = FaultDiagnosisAgent(
        data_quality_report=dq_report,
        soft_sensor_report=soft_report,
        mechanism_report=mechanism_report,
    ).run(readings)

    fault_ids = [fault["fault_id"] for fault in report.metrics["ranked_faults"]]
    assert "sensor_data_unreliable" in fault_ids
    assert "hydraulic_retention_anomaly" in fault_ids
    assert "release_evidence_insufficient" in fault_ids
    assert report.metrics["ranked_faults"][0]["score"] >= report.metrics["ranked_faults"][-1]["score"]
    assert report.recommendations


def test_fault_diagnosis_turns_loop_buffer_into_actionable_fault() -> None:
    readings = generate_sensor_stream_from_process_state(initial_process_state("reaction_time_insufficient"), n=24, seed=7)
    dq_report = DataQualityAgent().run(readings)
    soft_report = SoftSensorAgent(data_quality_report=dq_report).run(readings)
    mechanism_report = MechanismAgent(data_quality_report=dq_report, soft_sensor_report=soft_report).run(readings)
    report = FaultDiagnosisAgent(
        data_quality_report=dq_report,
        soft_sensor_report=soft_report,
        mechanism_report=mechanism_report,
    ).run(readings)

    fault_ids = [fault["fault_id"] for fault in report.metrics["ranked_faults"]]
    assert "cycle_window_insufficient" in fault_ids
    assert "reaction_time_insufficient" in fault_ids


def test_fault_diagnosis_carries_knowledge_support_into_fault_evidence() -> None:
    readings = generate_sensor_stream_from_process_state(initial_process_state("matrix_shock"), n=24, seed=7)
    dq_report = DataQualityAgent().run(readings)
    soft_report = SoftSensorAgent(data_quality_report=dq_report).run(readings)
    mechanism_report = MechanismAgent(data_quality_report=dq_report, soft_sensor_report=soft_report).run(readings)
    report = FaultDiagnosisAgent(
        data_quality_report=dq_report,
        soft_sensor_report=soft_report,
        mechanism_report=mechanism_report,
    ).run(readings)

    matrix_fault = next(fault for fault in report.metrics["ranked_faults"] if fault["fault_id"] == "matrix_interference")
    assert matrix_fault["evidence"]["knowledge_support"][0]["entry_id"] == "kb_matrix_aop_inhibition"


def test_fault_diagnosis_turns_byproduct_mechanism_into_fault() -> None:
    soft_report = AgentReport(
        agent_name="soft_sensor_agent",
        confidence=0.9,
        summary="",
        issues=[],
        recommendations=[],
        metrics={
            "state_estimate": {
                "pollutant_residual_risk": 0.22,
                "reaction_completion": 0.82,
                "oxidant_remaining": 0.82,
                "catalyst_activity": 0.72,
                "matrix_interference": 0.64,
                "byproduct_risk": 0.72,
                "hydraulic_confidence": 0.95,
                "sensor_confidence": 0.95,
                "compliance_probability": 0.84,
                "recycle_gain": 0.12,
                "release_readiness": 0.72,
                "cycle_id": 3,
            }
        },
    )
    mechanism_report = AgentReport(
        agent_name="mechanism_agent",
        confidence=0.9,
        summary="",
        issues=[],
        recommendations=[],
        metrics={"ranked_hypotheses": [{"rule_id": "byproduct_risk"}]},
    )
    report = FaultDiagnosisAgent(soft_sensor_report=soft_report, mechanism_report=mechanism_report).run([])
    fault_ids = [fault["fault_id"] for fault in report.metrics["ranked_faults"]]
    assert "byproduct_or_overoxidation_risk" in fault_ids
