from water_ai.agents.data_quality_agent import DataQualityAgent
from water_ai.agents.mechanism_agent import MechanismAgent
from water_ai.agents.soft_sensor_agent import SoftSensorAgent
from water_ai.domain import AgentReport
from water_ai.process_dynamics import generate_sensor_stream_from_process_state, initial_process_state
from water_ai.simulation import generate_low_cost_sensor_stream


def test_mechanism_agent_ranks_uncertainty_and_hydraulics() -> None:
    readings = generate_low_cost_sensor_stream(n=72, seed=7, inject_faults=True)
    dq_report = DataQualityAgent().run(readings)
    soft_report = SoftSensorAgent(data_quality_report=dq_report).run(readings)
    report = MechanismAgent(data_quality_report=dq_report, soft_sensor_report=soft_report).run(readings)

    rule_ids = [h["rule_id"] for h in report.metrics["ranked_hypotheses"]]
    assert "sensor_uncertainty" in rule_ids
    assert "hydraulic_anomaly" in rule_ids
    assert "likely_treated_but_not_releasable" in rule_ids
    assert report.metrics["ranked_hypotheses"][0]["score"] >= report.metrics["ranked_hypotheses"][-1]["score"]
    assert report.recommendations


def test_mechanism_agent_uses_short_window_hydraulic_evidence() -> None:
    readings = generate_sensor_stream_from_process_state(initial_process_state("sensor_faults"), n=24, seed=7)
    dq_report = DataQualityAgent().run(readings)
    soft_report = SoftSensorAgent(data_quality_report=dq_report).run(readings)
    report = MechanismAgent(data_quality_report=dq_report, soft_sensor_report=soft_report).run(readings)

    rule_ids = [h["rule_id"] for h in report.metrics["ranked_hypotheses"]]
    assert "hydraulic_anomaly" in rule_ids


def test_mechanism_agent_explains_loop_buffer_need() -> None:
    readings = generate_sensor_stream_from_process_state(initial_process_state("reaction_time_insufficient"), n=24, seed=7)
    dq_report = DataQualityAgent().run(readings)
    soft_report = SoftSensorAgent(data_quality_report=dq_report).run(readings)
    report = MechanismAgent(data_quality_report=dq_report, soft_sensor_report=soft_report).run(readings)

    rule_ids = [h["rule_id"] for h in report.metrics["ranked_hypotheses"]]
    assert "loop_buffer_needed" in rule_ids


def test_mechanism_agent_attaches_structured_knowledge_support() -> None:
    readings = generate_sensor_stream_from_process_state(initial_process_state("matrix_shock"), n=24, seed=7)
    dq_report = DataQualityAgent().run(readings)
    soft_report = SoftSensorAgent(data_quality_report=dq_report).run(readings)
    report = MechanismAgent(data_quality_report=dq_report, soft_sensor_report=soft_report).run(readings)

    matches = report.metrics["knowledge_matches"]
    matrix_hypothesis = next(h for h in report.metrics["ranked_hypotheses"] if h["rule_id"] == "matrix_interference")
    support = matrix_hypothesis["evidence"]["knowledge_support"]
    assert matches[0]["entry_id"] == "kb_matrix_aop_inhibition"
    assert support[0]["entry_id"] == "kb_matrix_aop_inhibition"


def test_mechanism_agent_explains_byproduct_risk() -> None:
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
    report = MechanismAgent(soft_sensor_report=soft_report).run([])
    rule_ids = [h["rule_id"] for h in report.metrics["ranked_hypotheses"]]
    assert "byproduct_risk" in rule_ids
