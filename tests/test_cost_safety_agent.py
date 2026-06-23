from water_ai.agents.control_strategy_agent import ControlStrategyAgent
from water_ai.agents.cost_safety_agent import CostSafetyAgent
from water_ai.agents.data_quality_agent import DataQualityAgent
from water_ai.agents.fault_diagnosis_agent import FaultDiagnosisAgent
from water_ai.agents.mechanism_agent import MechanismAgent
from water_ai.agents.soft_sensor_agent import SoftSensorAgent
from water_ai.domain import AgentReport
from water_ai.simulation import generate_low_cost_sensor_stream
from water_ai.strategy_objective import StrategyObjectiveWeights


def test_cost_safety_penalizes_release_and_expensive_switching() -> None:
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
    report = CostSafetyAgent(control_report=control_report).run(readings)

    evaluated = {item["action_id"]: item for item in report.metrics["evaluated_actions"]}
    assert evaluated["release"]["net_score"] < evaluated["hold_for_validation"]["net_score"]
    assert evaluated["switch_or_pretreat"]["net_score"] < evaluated["hold_for_validation"]["net_score"]
    assert "hold_for_validation" in report.metrics["recommended_action_ids"]
    assert all("预处理或切换处理单元" not in rec for rec in report.recommendations)


def test_cost_safety_prioritizes_pretreatment_under_matrix_shock() -> None:
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
    report = CostSafetyAgent(control_report=control_report).run(readings)

    evaluated = {item["action_id"]: item for item in report.metrics["evaluated_actions"]}
    assert evaluated["switch_or_pretreat"]["net_score"] > evaluated["recirculate"]["net_score"]


def test_cost_safety_penalizes_dosing_under_byproduct_risk() -> None:
    control_report = AgentReport(
        agent_name="control_strategy_agent",
        confidence=0.9,
        summary="",
        issues=[],
        recommendations=[],
        metrics={
            "ranked_actions": [
                {
                    "action_id": "dose_oxidant",
                    "action_name": "补加氧化剂",
                    "score": 0.9,
                    "parameters": {"dose_factor": 0.32},
                    "requires_human_review": False,
                    "evidence": {"oxidant_remaining": 0.2, "byproduct_risk": 0.72, "dose_factor": 0.32},
                },
                {
                    "action_id": "hold_for_validation",
                    "action_name": "暂存并旁路验证",
                    "score": 0.65,
                    "parameters": {"hold_min": 20},
                    "requires_human_review": False,
                    "evidence": {},
                },
            ]
        },
    )
    report = CostSafetyAgent(control_report=control_report).run([])
    evaluated = {item["action_id"]: item for item in report.metrics["evaluated_actions"]}
    assert evaluated["dose_oxidant"]["risk_cost"] >= 0.58
    assert evaluated["dose_oxidant"]["net_score"] < evaluated["hold_for_validation"]["net_score"]


def test_cost_safety_accepts_regeneration_when_catalyst_is_low() -> None:
    control_report = AgentReport(
        agent_name="control_strategy_agent",
        confidence=0.9,
        summary="",
        issues=[],
        recommendations=[],
        metrics={
            "ranked_actions": [
                {
                    "action_id": "regenerate_catalyst",
                    "action_name": "再生或更换催化剂",
                    "score": 0.83,
                    "parameters": {"regen_intensity": 0.72, "downtime_min": 58},
                    "requires_human_review": True,
                    "evidence": {"catalyst_activity": 0.28, "reaction_completion": 0.46},
                },
                {
                    "action_id": "recirculate",
                    "action_name": "继续回流处理",
                    "score": 0.72,
                    "parameters": {"recycle_ratio": 0.5, "extra_retention_min": 34},
                    "requires_human_review": False,
                    "evidence": {"recycle_gain": 0.36},
                },
            ]
        },
    )
    report = CostSafetyAgent(control_report=control_report).run([])
    evaluated = {item["action_id"]: item for item in report.metrics["evaluated_actions"]}
    assert evaluated["regenerate_catalyst"]["safety_gain"] >= 0.9
    assert evaluated["regenerate_catalyst"]["net_score"] >= 0.35
    assert "regenerate_catalyst" in report.metrics["recommended_action_ids"]


def test_cost_safety_prefers_replacement_when_regeneration_is_exhausted() -> None:
    control_report = AgentReport(
        agent_name="control_strategy_agent",
        confidence=0.9,
        summary="",
        issues=[],
        recommendations=[],
        metrics={
            "ranked_actions": [
                {
                    "action_id": "regenerate_catalyst",
                    "action_name": "再生或更换催化剂",
                    "score": 0.64,
                    "parameters": {"regen_intensity": 0.8, "downtime_min": 60},
                    "requires_human_review": True,
                    "evidence": {
                        "catalyst_activity": 0.28,
                        "catalyst_regeneration_potential": 0.18,
                        "catalyst_replacement_urgency": 0.86,
                    },
                },
                {
                    "action_id": "replace_catalyst",
                    "action_name": "更换催化剂模块",
                    "score": 0.82,
                    "parameters": {"downtime_min": 108},
                    "requires_human_review": True,
                    "evidence": {
                        "catalyst_activity": 0.28,
                        "catalyst_lifetime_fraction": 0.24,
                        "catalyst_regen_count": 3,
                        "catalyst_regeneration_potential": 0.18,
                        "catalyst_replacement_urgency": 0.86,
                    },
                },
            ]
        },
    )
    report = CostSafetyAgent(control_report=control_report).run([])
    evaluated = {item["action_id"]: item for item in report.metrics["evaluated_actions"]}

    assert evaluated["regenerate_catalyst"]["risk_cost"] >= 0.44
    assert evaluated["replace_catalyst"]["safety_gain"] >= 0.95
    assert evaluated["replace_catalyst"]["objective_score"] > evaluated["regenerate_catalyst"]["objective_score"]


def test_cost_safety_uses_knowledge_bias_for_cost_adjustment() -> None:
    control_report = AgentReport(
        agent_name="control_strategy_agent",
        confidence=0.9,
        summary="",
        issues=[],
        recommendations=[],
        metrics={
            "ranked_actions": [
                {
                    "action_id": "hold_for_validation",
                    "action_name": "暂存并旁路验证",
                    "score": 0.8,
                    "parameters": {"hold_min": 20},
                    "requires_human_review": False,
                    "evidence": {"knowledge_action_bias": 0.2},
                },
                {
                    "action_id": "release",
                    "action_name": "达标放行",
                    "score": 0.8,
                    "parameters": {},
                    "requires_human_review": False,
                    "evidence": {
                        "release_readiness": 0.9,
                        "byproduct_risk": 0.2,
                        "knowledge_action_bias": -0.2,
                    },
                },
            ]
        },
    )
    report = CostSafetyAgent(control_report=control_report).run([])
    evaluated = {item["action_id"]: item for item in report.metrics["evaluated_actions"]}

    assert evaluated["hold_for_validation"]["safety_gain"] > 0.78
    assert evaluated["hold_for_validation"]["risk_cost"] < 0.12
    assert evaluated["hold_for_validation"]["objective_score"] > evaluated["release"]["objective_score"]
    assert evaluated["hold_for_validation"]["objective"]["benefit_terms"]["knowledge_alignment"] > evaluated["release"]["objective"]["benefit_terms"]["knowledge_alignment"]
    assert evaluated["release"]["safety_gain"] < 0.72
    assert evaluated["release"]["risk_cost"] > 0.08
    assert evaluated["release"]["knowledge_cost_adjustment"]["risk_cost_delta"] > 0


def test_cost_safety_accepts_custom_strategy_weights() -> None:
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
                    "parameters": {"recycle_ratio": 0.5, "extra_retention_min": 42},
                    "requires_human_review": False,
                    "evidence": {"recycle_gain": 0.42},
                }
            ]
        },
    )
    report = CostSafetyAgent(
        control_report=control_report,
        objective_weights=StrategyObjectiveWeights(time_cost=0.35),
    ).run([])
    evaluated = report.metrics["evaluated_actions"][0]

    assert report.metrics["strategy_objective_weights"]["time_cost"] == 0.35
    assert report.metrics["strategy_objective_profile"] == "custom"
    assert evaluated["objective"]["penalty_terms"]["time_cost"] > 0.1


def test_cost_safety_accepts_strategy_profile() -> None:
    control_report = AgentReport(
        agent_name="control_strategy_agent",
        confidence=0.9,
        summary="",
        issues=[],
        recommendations=[],
        metrics={
            "ranked_actions": [
                {
                    "action_id": "release",
                    "action_name": "达标放行",
                    "score": 0.9,
                    "parameters": {},
                    "requires_human_review": False,
                    "evidence": {
                        "release_readiness": 0.72,
                        "pollutant_residual_risk": 0.48,
                        "sensor_confidence": 0.7,
                        "hydraulic_confidence": 0.8,
                    },
                }
            ]
        },
    )
    report = CostSafetyAgent(control_report=control_report, objective_profile="safety_first").run([])
    evaluated = report.metrics["evaluated_actions"][0]

    assert report.metrics["strategy_objective_profile"] == "safety_first"
    assert evaluated["objective"]["weights"]["false_release_risk"] == 0.4


def test_cost_safety_can_consume_agent49_joint_actions() -> None:
    control_report = AgentReport(
        agent_name="control_strategy_agent",
        confidence=0.9,
        summary="",
        issues=[],
        recommendations=[],
        metrics={"ranked_actions": []},
    )
    collaborative_report = AgentReport(
        agent_name="multi_facility_collaborative_control_agent",
        confidence=0.8,
        summary="",
        issues=[],
        recommendations=[],
        metrics={
            "joint_action_matrix": [
                {
                    "joint_action_id": "J0_matrix_shock_equalize_and_recycle",
                    "joint_policy_score": 0.74,
                    "facility_agents": ["F0_equalization_buffer_agent", "F3_recirculation_loop_agent"],
                    "actions": ["hold_and_homogenize", "increase_recycle_ratio"],
                    "control_intent": "基质冲击先削峰再回流。",
                    "combined_state_vector": {"release_risk_visibility": 0.7},
                    "reward_components": {"weighted_reward": 0.74},
                    "writeback_boundary": "synthetic collaborative candidate only",
                }
            ]
        },
    )

    report = CostSafetyAgent(
        control_report=control_report,
        collaborative_control_report=collaborative_report,
    ).run([])
    evaluated = report.metrics["evaluated_actions"][0]

    assert evaluated["action_id"] == "J0_matrix_shock_equalize_and_recycle"
    assert evaluated["joint_action_id"] == "J0_matrix_shock_equalize_and_recycle"
    assert evaluated["requires_human_review"] is True
    assert "J0_matrix_shock_equalize_and_recycle" in report.metrics["recommended_action_ids"]
