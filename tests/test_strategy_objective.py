import pytest

from water_ai.strategy_objective import StrategyObjectiveWeights, compute_strategy_objective, get_strategy_objective_weights


def test_strategy_objective_penalizes_false_release_risk() -> None:
    unsafe_release = compute_strategy_objective(
        action_id="release",
        original_score=0.92,
        safety_gain=0.72,
        money_cost=0.02,
        time_cost=0.0,
        energy_cost=0.0,
        risk_cost=0.08,
        requires_human_review=False,
        evidence={
            "release_readiness": 0.55,
            "pollutant_residual_risk": 0.62,
            "hydraulic_confidence": 0.62,
            "sensor_confidence": 0.68,
            "byproduct_risk": 0.45,
        },
    )
    validation_hold = compute_strategy_objective(
        action_id="hold_for_validation",
        original_score=0.68,
        safety_gain=0.78,
        money_cost=0.25,
        time_cost=0.42,
        energy_cost=0.05,
        risk_cost=0.12,
        requires_human_review=False,
        evidence={
            "release_readiness": 0.55,
            "pollutant_residual_risk": 0.62,
            "hydraulic_confidence": 0.62,
            "sensor_confidence": 0.68,
            "byproduct_risk": 0.45,
        },
    )

    assert unsafe_release["false_release_risk"] > validation_hold["false_release_risk"]
    assert validation_hold["objective_score"] > unsafe_release["objective_score"]


def test_strategy_objective_exposes_tunable_weight_effects() -> None:
    default_objective = compute_strategy_objective(
        action_id="recirculate",
        original_score=0.82,
        safety_gain=0.72,
        money_cost=0.22,
        time_cost=0.32,
        energy_cost=0.28,
        risk_cost=0.12,
        requires_human_review=False,
        evidence={"recycle_gain": 0.4, "knowledge_action_bias": 0.18},
        knowledge_action_bias=0.18,
    )
    time_sensitive_objective = compute_strategy_objective(
        action_id="recirculate",
        original_score=0.82,
        safety_gain=0.72,
        money_cost=0.22,
        time_cost=0.32,
        energy_cost=0.28,
        risk_cost=0.12,
        requires_human_review=False,
        evidence={"recycle_gain": 0.4, "knowledge_action_bias": 0.18},
        knowledge_action_bias=0.18,
        weights=StrategyObjectiveWeights(time_cost=0.35),
    )

    assert default_objective["benefit_terms"]["knowledge_alignment"] > 0.05
    assert time_sensitive_objective["objective_score"] < default_objective["objective_score"]


def test_strategy_objective_profiles_are_named_and_validated() -> None:
    safety_first = get_strategy_objective_weights("safety_first")
    cost_first = get_strategy_objective_weights("cost_first")

    assert safety_first.false_release_risk > cost_first.false_release_risk
    assert cost_first.money_cost > safety_first.money_cost
    with pytest.raises(ValueError):
        get_strategy_objective_weights("unknown_profile")
