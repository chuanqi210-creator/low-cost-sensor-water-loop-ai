from water_ai.agents.strategy_profile_agent import StrategyProfileAgent
from water_ai.domain import AgentReport
from water_ai.pipeline import run_agent_chain
from water_ai.process_dynamics import generate_sensor_stream_from_process_state, initial_process_state


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
        confidence=0.9,
        summary="",
        issues=[],
        recommendations=[],
        metrics={"ranked_faults": [{"fault_id": fault_id, "score": 0.8} for fault_id in fault_ids]},
    )


def test_strategy_profile_agent_selects_safety_first_under_sensor_uncertainty() -> None:
    report = StrategyProfileAgent(
        soft_sensor_report=_soft_report(
            {
                "release_readiness": 0.72,
                "pollutant_residual_risk": 0.48,
                "sensor_confidence": 0.64,
                "hydraulic_confidence": 0.66,
                "byproduct_risk": 0.35,
                "recycle_gain": 0.25,
                "oxidant_remaining": 0.7,
                "catalyst_activity": 0.6,
            }
        ),
        fault_report=_fault_report(["hydraulic_retention_anomaly"]),
    ).run([])

    assert report.metrics["selected_profile"] == "safety_first"
    assert any(issue.issue_type == "safety_weighting_active" for issue in report.issues)


def test_strategy_profile_agent_selects_emergency_response_for_oxidant_gap() -> None:
    report = StrategyProfileAgent(
        soft_sensor_report=_soft_report(
            {
                "release_readiness": 0.7,
                "pollutant_residual_risk": 0.55,
                "sensor_confidence": 0.95,
                "hydraulic_confidence": 0.95,
                "byproduct_risk": 0.2,
                "recycle_gain": 0.55,
                "oxidant_remaining": 0.12,
                "catalyst_activity": 0.7,
            }
        ),
        fault_report=_fault_report(["oxidant_limitation"]),
    ).run([])

    assert report.metrics["selected_profile"] == "emergency_response"


def test_strategy_profile_agent_selects_cost_first_when_release_evidence_is_strong() -> None:
    report = StrategyProfileAgent(
        soft_sensor_report=_soft_report(
            {
                "release_readiness": 0.91,
                "pollutant_residual_risk": 0.16,
                "sensor_confidence": 0.96,
                "hydraulic_confidence": 0.94,
                "byproduct_risk": 0.22,
                "recycle_gain": 0.05,
                "oxidant_remaining": 0.6,
                "catalyst_activity": 0.74,
            }
        ),
        fault_report=_fault_report([]),
    ).run([])

    assert report.metrics["selected_profile"] == "cost_first"


def test_pipeline_passes_strategy_profile_to_cost_safety_agent() -> None:
    readings = generate_sensor_stream_from_process_state(initial_process_state("sensor_faults"), n=24, seed=7)
    result = run_agent_chain(readings)

    selected = result.strategy_profile.metrics["selected_profile"]
    assert selected == result.cost_safety.metrics["strategy_objective_profile"]
