from water_ai.agents.catalyst_lifecycle_agent import CatalystLifecycleAgent
from water_ai.agents.control_strategy_agent import ControlStrategyAgent
from water_ai.agents.data_quality_agent import DataQualityAgent
from water_ai.agents.fault_diagnosis_agent import FaultDiagnosisAgent
from water_ai.agents.matrix_shock_fast_proxy_agent import MatrixShockFastProxyAgent
from water_ai.agents.mechanism_agent import MechanismAgent
from water_ai.agents.soft_sensor_agent import SoftSensorAgent
from water_ai.agents.validation_planning_agent import ValidationPlanningAgent
from water_ai.process_dynamics import generate_sensor_stream_from_process_state, initial_process_state


def test_matrix_shock_fast_proxy_triggers_protective_control_without_release_authority() -> None:
    readings = generate_sensor_stream_from_process_state(initial_process_state("matrix_shock"), n=24, seed=7)

    report = MatrixShockFastProxyAgent(latency_metrics=_latency_metrics()).run(readings)

    proxy = report.metrics["proxy"]
    mitigation = report.metrics["mitigation_budget"]
    readiness = report.metrics["readiness"]

    assert proxy["protective_triggered"] is True
    assert proxy["release_block_recommended"] is True
    assert mitigation["latency_failure_resolved_for_control"] is True
    assert mitigation["protective_action_margin_min"] > 20
    assert mitigation["projected_evidence_margin_after_extension_min"] > 0
    assert readiness["fast_proxy_status"] == "synthetic_fast_proxy_ready_needs_field_timestamp_validation"
    assert readiness["can_write_to_release_gate"] is False
    assert any(issue.issue_type == "release_blocked_by_matrix_fast_proxy" for issue in report.issues)


def test_matrix_shock_fast_proxy_does_not_trigger_on_clean_or_oxidant_only_scenarios() -> None:
    for scenario in ("clean_release", "oxidant_limitation"):
        readings = generate_sensor_stream_from_process_state(initial_process_state(scenario), n=24, seed=7)
        report = MatrixShockFastProxyAgent(latency_metrics=_latency_metrics()).run(readings)

        assert report.metrics["proxy"]["protective_triggered"] is False
        assert report.metrics["proxy"]["specificity_guard_score"] < 0.46
        assert report.metrics["readiness"]["fast_proxy_status"] == "fast_proxy_not_triggered_keep_standard_matrix_workup"
        assert not report.issues


def test_control_strategy_uses_matrix_fast_proxy_for_latency_aware_pretreatment() -> None:
    readings = generate_sensor_stream_from_process_state(initial_process_state("matrix_shock"), n=24, seed=7)
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
    proxy_report = MatrixShockFastProxyAgent(latency_metrics=_latency_metrics()).run(readings)

    control_report = ControlStrategyAgent(
        soft_sensor_report=soft_report,
        fault_report=fault_report,
        catalyst_lifecycle_report=lifecycle_report,
        validation_planning_report=validation_report,
        matrix_shock_fast_proxy_report=proxy_report,
    ).run(readings)

    ranked = control_report.metrics["ranked_actions"]
    switch = next(action for action in ranked if action["action_id"] == "switch_or_pretreat")
    hold = next(action for action in ranked if action["action_id"] == "hold_for_validation")

    assert switch["parameters"]["protective_mode"] is True
    assert switch["parameters"]["release_policy"] == "block_release_until_lab_and_field_conformal_calibration"
    assert switch["evidence"]["matrix_fast_proxy"]["protective_triggered"] is True
    assert hold["parameters"]["hold_min"] >= 90
    assert "salinity_or_EC_reference" in hold["parameters"]["validation"]
    assert control_report.metrics["matrix_shock_fast_proxy"]["readiness"]["can_write_to_release_gate"] is False


def _latency_metrics() -> dict[str, object]:
    return {
        "latency_budget": [
            {
                "scenario": "matrix_shock",
                "action_deadline_min": 85.0,
                "release_evidence_latency_min": 115.0,
                "loop_time_credit_min": 84.0,
                "evidence_margin_min": -31.0,
                "action_latency_margin_min": 47.0,
                "failure_boundary": "synthetic replay is not field validation.",
            }
        ]
    }
