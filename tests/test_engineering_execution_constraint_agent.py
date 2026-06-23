from water_ai.agents.arbitration_agent import ArbitrationAgent
from water_ai.agents.cost_safety_agent import CostSafetyAgent
from water_ai.agents.engineering_execution_constraint_agent import EngineeringExecutionConstraintAgent
from water_ai.agents.multi_facility_collaborative_control_agent import MultiFacilityCollaborativeControlAgent
from water_ai.agents.sensor_network_sparse_placement_agent import SensorNetworkSparsePlacementAgent
from water_ai.domain import AgentReport


def test_engineering_constraints_agent_builds_reward_and_arbitration_patch() -> None:
    agent49_report = MultiFacilityCollaborativeControlAgent(sparse_placement_metrics=_sparse_metrics()).run([])
    report = EngineeringExecutionConstraintAgent(
        collaborative_control_metrics=agent49_report.metrics,
        engineering_profile={
            "available_buffer_storage_m3": 10.0,
            "chemical_inventory_fraction_available": 0.12,
            "maintenance_window_available_min": 20.0,
        },
    ).run([])

    readiness = report.metrics["readiness"]
    reward_patch = report.metrics["agent49_reward_patch"]
    arbitration_patch = report.metrics["arbitration_patch"]

    assert readiness["engineering_constraints_status"].startswith("synthetic_")
    assert readiness["can_update_agent49_reward_contract"] is True
    assert readiness["can_write_to_actuator"] is False
    assert len(reward_patch) >= 5
    assert any(item["hard_blocked_by_engineering"] for item in reward_patch)
    assert "recirculate" in arbitration_patch["blocked_action_ids"]


def test_agent49_consumes_engineering_constraint_patch_in_joint_reward() -> None:
    sparse = _sparse_metrics()
    base_report = MultiFacilityCollaborativeControlAgent(sparse_placement_metrics=sparse).run([])
    engineering_report = EngineeringExecutionConstraintAgent(
        collaborative_control_metrics=base_report.metrics,
        engineering_profile={"available_buffer_storage_m3": 10.0},
    ).run([])

    patched_report = MultiFacilityCollaborativeControlAgent(
        sparse_placement_metrics=sparse,
        engineering_constraints_metrics=engineering_report.metrics,
    ).run([])

    base_by_id = {item["joint_action_id"]: item for item in base_report.metrics["joint_action_matrix"]}
    patched_by_id = {item["joint_action_id"]: item for item in patched_report.metrics["joint_action_matrix"]}
    action_id = "J4_safe_low_cost_standby"

    assert patched_report.metrics["readiness"]["engineering_constraints_integrated"] is True
    assert patched_by_id[action_id]["reward_components"]["engineering_constraint_penalty"] > 0
    assert patched_by_id[action_id]["joint_policy_score"] < base_by_id[action_id]["joint_policy_score"]
    assert patched_by_id[action_id]["engineering_constraint_evaluation"]["hard_blocked_by_engineering"] is True


def test_cost_safety_agent_applies_engineering_penalty_to_action_objective() -> None:
    control_report = AgentReport(
        agent_name="control_strategy_agent",
        confidence=0.9,
        summary="",
        issues=[],
        recommendations=[],
        metrics={
            "ranked_actions": [
                {
                    "action_id": "recirculate",
                    "action_name": "继续回流处理",
                    "score": 0.82,
                    "parameters": {"recycle_ratio": 0.5},
                    "requires_human_review": False,
                    "evidence": {"recycle_gain": 0.45},
                }
            ]
        },
    )
    engineering_report = _engineering_report({"available_buffer_storage_m3": 6.0})

    without_patch = CostSafetyAgent(control_report=control_report).run([])
    with_patch = CostSafetyAgent(
        control_report=control_report,
        engineering_constraints_report=engineering_report,
    ).run([])

    base_action = without_patch.metrics["evaluated_actions"][0]
    patched_action = with_patch.metrics["evaluated_actions"][0]

    assert patched_action["engineering_constraint_penalty"] > 0
    assert patched_action["engineering_hard_block"] is True
    assert patched_action["objective_score"] < base_action["objective_score"]
    assert patched_action["risk_cost"] > base_action["risk_cost"]


def test_arbitration_blocks_engineering_infeasible_actions() -> None:
    soft_report = AgentReport(
        agent_name="soft_sensor_agent",
        confidence=0.9,
        summary="",
        issues=[],
        recommendations=[],
        metrics={
            "state_estimate": {
                "pollutant_residual_risk": 0.30,
                "reaction_completion": 0.82,
                "oxidant_remaining": 0.18,
                "catalyst_activity": 0.62,
                "matrix_interference": 0.44,
                "byproduct_risk": 0.28,
                "hydraulic_confidence": 0.88,
                "sensor_confidence": 0.90,
                "compliance_probability": 0.78,
                "recycle_gain": 0.46,
                "release_readiness": 0.70,
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
                    "net_score": 0.78,
                    "objective_score": 0.74,
                    "parameters": {"recycle_ratio": 0.5},
                },
                {
                    "action_id": "hold_for_validation",
                    "action_name": "暂存并旁路验证",
                    "original_score": 0.74,
                    "net_score": 0.64,
                    "objective_score": 0.62,
                    "parameters": {"hold_min": 20},
                },
            ]
        },
    )
    engineering_report = _engineering_report({"available_buffer_storage_m3": 6.0})

    report = ArbitrationAgent(
        soft_sensor_report=soft_report,
        cost_safety_report=cost_report,
        engineering_constraints_report=engineering_report,
    ).run([])

    final_ids = [action["action_id"] for action in report.metrics["final_plan"]]
    failed_gates = [gate["gate_id"] for gate in report.metrics["safety_gates"] if not gate["passed"]]

    assert "recirculate" not in final_ids
    assert "recirculate" in report.metrics["blocked_actions"]
    assert "engineering_hard_block_gate" in failed_gates
    assert report.metrics["engineering_constraints_used"]["available"] is True


def _sparse_metrics() -> dict[str, object]:
    report = SensorNetworkSparsePlacementAgent(max_sensors=6, budget_limit=5.8).run([])
    return {
        "selected_sensor_plan": report.metrics["selected_sensor_plan"],
        "coverage": dict(report.metrics["coverage"]),
        "readiness": dict(report.metrics["readiness"]),
        "soft_sensor_interface": report.metrics["soft_sensor_interface"],
    }


def _engineering_report(profile: dict[str, object]) -> AgentReport:
    agent49_report = MultiFacilityCollaborativeControlAgent(sparse_placement_metrics=_sparse_metrics()).run([])
    return EngineeringExecutionConstraintAgent(
        collaborative_control_metrics=agent49_report.metrics,
        engineering_profile=profile,
    ).run([])
