from water_ai.agents.control_strategy_agent import ControlStrategyAgent
from water_ai.agents.data_quality_agent import DataQualityAgent
from water_ai.agents.fault_diagnosis_agent import FaultDiagnosisAgent
from water_ai.agents.knowledge_graph_reasoning_agent import KnowledgeGraphReasoningAgent
from water_ai.agents.mechanism_agent import MechanismAgent
from water_ai.agents.soft_sensor_agent import SoftSensorAgent
from water_ai.knowledge import build_knowledge_graph, reason_over_knowledge_graph
from water_ai.simulation import generate_low_cost_sensor_stream


def _byproduct_state() -> dict[str, float]:
    return {
        "pollutant_residual_risk": 0.58,
        "reaction_completion": 0.56,
        "oxidant_remaining": 0.78,
        "catalyst_activity": 0.63,
        "matrix_interference": 0.68,
        "byproduct_risk": 0.72,
        "recycle_gain": 0.34,
        "release_readiness": 0.58,
        "sensor_confidence": 0.91,
    }


def test_build_knowledge_graph_has_typed_nodes_edges_and_boundaries() -> None:
    graph = build_knowledge_graph()
    summary = graph["summary"]
    edges = graph["edges"]

    assert summary["node_count"] > 0
    assert summary["edge_count"] > 0
    assert summary["edge_type_counts"]["biases_action"] > 0
    assert summary["edge_type_counts"]["needs_field_validation"] > 0
    assert all(edge["entry_id"] for edge in edges)
    assert all(edge["claim_boundary"] for edge in edges)


def test_reason_over_knowledge_graph_returns_action_constraints() -> None:
    reasoning = reason_over_knowledge_graph(_byproduct_state())

    patch = {row["action_id"]: row for row in reasoning["action_constraint_patch"]}

    assert reasoning["readiness"]["evidence_traceability"] > 0
    assert reasoning["readiness"]["constraint_hit_rate"] > 0
    assert "dose_oxidant" in patch
    assert patch["dose_oxidant"]["direction"] == "suppress"
    assert patch["dose_oxidant"]["writeback_boundary"] == "score_prior_only_until_field_validation"
    assert reasoning["readiness"]["can_write_to_release_gate"] is False


def test_knowledge_graph_reasoning_agent_retrospective_marks_root_gap_patched() -> None:
    report = KnowledgeGraphReasoningAgent(state_estimate=_byproduct_state()).run([])

    readiness = report.metrics["readiness"]
    retrospective = report.metrics["agent_chain_retrospective"]

    assert readiness["kg_reasoning_status"] == "kg_reasoning_patch_ready_needs_field_supported_edges"
    assert readiness["can_update_mechanism_evidence"] is True
    assert readiness["can_update_action_bias_prior"] is True
    assert any(
        gap["gap_id"] == "G0_flat_knowledge_not_coupled_to_decisions"
        and gap["after_agent56_status"] == "patched_by_typed_kg_reasoning"
        for gap in retrospective
    )


def test_main_mechanism_fault_control_chain_consumes_typed_kg_constraints() -> None:
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

    assert mechanism_report.metrics["kg_reasoning"]["evidence_paths"]
    assert fault_report.metrics["kg_reasoning"]["action_constraint_patch"]
    assert control_report.metrics["knowledge_reasoning_source"] == "typed_kg_action_constraint_patch"
