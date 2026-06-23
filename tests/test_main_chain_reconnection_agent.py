from water_ai.agents.arbitration_agent import ArbitrationAgent
from water_ai.agents.control_strategy_agent import ControlStrategyAgent
from water_ai.agents.cost_safety_agent import CostSafetyAgent
from water_ai.agents.data_quality_agent import DataQualityAgent
from water_ai.agents.engineering_execution_constraint_agent import EngineeringExecutionConstraintAgent
from water_ai.agents.fault_diagnosis_agent import FaultDiagnosisAgent
from water_ai.agents.main_chain_reconnection_agent import MainChainReconnectionAgent
from water_ai.agents.mechanism_agent import MechanismAgent
from water_ai.agents.multi_facility_collaborative_control_agent import MultiFacilityCollaborativeControlAgent
from water_ai.agents.sensor_network_sparse_placement_agent import SensorNetworkSparsePlacementAgent
from water_ai.agents.soft_sensor_agent import SoftSensorAgent
from water_ai.process_dynamics import generate_sensor_stream_from_process_state, initial_process_state


def test_main_chain_reconnection_agent_audits_core_prior_consumption() -> None:
    sparse_report = SensorNetworkSparsePlacementAgent(max_sensors=6, budget_limit=5.8).run([])
    grey_box_metrics = _grey_box_metrics()
    readings = generate_sensor_stream_from_process_state(initial_process_state("matrix_shock"), n=72, seed=57)
    dq_report = DataQualityAgent().run(readings)
    soft_report = SoftSensorAgent(
        data_quality_report=dq_report,
        sensor_layout_interface=sparse_report.metrics["soft_sensor_interface"],
        grey_box_physics_metrics=grey_box_metrics,
    ).run(readings)
    mechanism_report = MechanismAgent(data_quality_report=dq_report, soft_sensor_report=soft_report).run(readings)
    fault_report = FaultDiagnosisAgent(
        data_quality_report=dq_report,
        soft_sensor_report=soft_report,
        mechanism_report=mechanism_report,
    ).run(readings)
    control_report = ControlStrategyAgent(soft_sensor_report=soft_report, fault_report=fault_report).run(readings)
    collab_report = MultiFacilityCollaborativeControlAgent(sparse_placement_metrics=sparse_report.metrics).run([])
    engineering_report = EngineeringExecutionConstraintAgent(
        collaborative_control_metrics=collab_report.metrics,
    ).run([])
    cost_report = CostSafetyAgent(
        control_report=control_report,
        engineering_constraints_report=engineering_report,
        collaborative_control_report=collab_report,
    ).run(readings)
    arbitration_report = ArbitrationAgent(
        soft_sensor_report=soft_report,
        control_report=control_report,
        cost_safety_report=cost_report,
        engineering_constraints_report=engineering_report,
    ).run(readings)

    report = MainChainReconnectionAgent(
        soft_sensor_report=soft_report,
        mechanism_report=mechanism_report,
        fault_report=fault_report,
        control_report=control_report,
        cost_safety_report=cost_report,
        arbitration_report=arbitration_report,
        multi_facility_control_metrics=collab_report.metrics,
        grey_box_physics_metrics=grey_box_metrics,
    ).run([])

    readiness = report.metrics["readiness"]
    coupling = {row["link_id"]: row for row in report.metrics["coupling_table"]}

    assert readiness["main_chain_reconnection_status"] == "synthetic_main_chain_reconnection_ready_needs_field_replay"
    assert readiness["main_chain_prior_consumption_rate"] >= 0.84
    assert coupling["L1_agent53_grey_box_to_agent2_soft_sensor"]["consumed"] is True
    assert coupling["L3_agent56_kg_to_agent5_control"]["consumed"] is True
    assert coupling["L5_agent55_engineering_to_agent10_arbitration"]["consumed"] is True
    assert coupling["L6_agent49_multi_facility_to_agent10_arbitration"]["consumed"] is True
    assert readiness["can_write_to_actuator"] is False


def _grey_box_metrics() -> dict[str, object]:
    return {
        "scenario_physics_table": [
            {"scenario": "matrix_shock", "grey_box_residual": 0.12, "byproduct_risk": 0.66},
            {"scenario": "reaction_time_insufficient", "grey_box_residual": 0.09, "byproduct_risk": 0.42},
        ],
        "readiness": {
            "grey_box_physics_status": "synthetic_grey_box_physics_prior_ready_needs_field_calibration",
            "synthetic_prior_ready": True,
            "can_update_soft_sensor_physics_prior": True,
            "mean_grey_box_residual": 0.105,
            "max_byproduct_risk": 0.66,
            "scenario_count": 2,
            "field_ready": False,
        },
    }
