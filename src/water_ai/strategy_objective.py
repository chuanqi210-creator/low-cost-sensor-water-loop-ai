from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class StrategyObjectiveWeights:
    """Weights for a unified engineering objective over candidate actions."""

    control_priority: float = 0.40
    safety_gain: float = 0.34
    money_cost: float = 0.16
    time_cost: float = 0.11
    energy_cost: float = 0.09
    risk_cost: float = 0.22
    false_release_risk: float = 0.30
    byproduct_risk: float = 0.10
    human_review: float = 0.06
    knowledge_alignment: float = 0.08

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


DEFAULT_STRATEGY_WEIGHTS = StrategyObjectiveWeights()

STRATEGY_OBJECTIVE_PROFILES: dict[str, StrategyObjectiveWeights] = {
    "balanced": DEFAULT_STRATEGY_WEIGHTS,
    "safety_first": StrategyObjectiveWeights(
        control_priority=0.34,
        safety_gain=0.38,
        money_cost=0.10,
        time_cost=0.08,
        energy_cost=0.07,
        risk_cost=0.28,
        false_release_risk=0.40,
        byproduct_risk=0.16,
        human_review=0.05,
        knowledge_alignment=0.10,
    ),
    "cost_first": StrategyObjectiveWeights(
        control_priority=0.38,
        safety_gain=0.30,
        money_cost=0.28,
        time_cost=0.14,
        energy_cost=0.14,
        risk_cost=0.20,
        false_release_risk=0.28,
        byproduct_risk=0.10,
        human_review=0.05,
        knowledge_alignment=0.06,
    ),
    "emergency_response": StrategyObjectiveWeights(
        control_priority=0.46,
        safety_gain=0.32,
        money_cost=0.12,
        time_cost=0.05,
        energy_cost=0.07,
        risk_cost=0.24,
        false_release_risk=0.34,
        byproduct_risk=0.12,
        human_review=0.04,
        knowledge_alignment=0.08,
    ),
}


def get_strategy_objective_weights(profile: str = "balanced") -> StrategyObjectiveWeights:
    try:
        return STRATEGY_OBJECTIVE_PROFILES[profile]
    except KeyError as exc:
        valid = ", ".join(sorted(STRATEGY_OBJECTIVE_PROFILES))
        raise ValueError(f"unknown strategy objective profile {profile!r}; valid profiles: {valid}") from exc


def compute_strategy_objective(
    *,
    action_id: str,
    original_score: float,
    safety_gain: float,
    money_cost: float,
    time_cost: float,
    energy_cost: float,
    risk_cost: float,
    requires_human_review: bool,
    evidence: dict[str, object],
    knowledge_action_bias: float = 0.0,
    weights: StrategyObjectiveWeights = DEFAULT_STRATEGY_WEIGHTS,
) -> dict[str, object]:
    """Compute a transparent, tunable objective for one candidate action."""

    false_release_risk = _estimate_false_release_risk(action_id, evidence)
    byproduct_pressure = _estimate_byproduct_pressure(action_id, evidence)
    human_review_penalty = 1.0 if requires_human_review else 0.0
    knowledge_alignment = _clip((knowledge_action_bias + 0.22) / 0.44)

    benefit_terms = {
        "control_priority": weights.control_priority * _clip(original_score),
        "safety_gain": weights.safety_gain * _clip(safety_gain),
        "knowledge_alignment": weights.knowledge_alignment * knowledge_alignment,
    }
    penalty_terms = {
        "money_cost": weights.money_cost * _clip(money_cost),
        "time_cost": weights.time_cost * _clip(time_cost),
        "energy_cost": weights.energy_cost * _clip(energy_cost),
        "risk_cost": weights.risk_cost * _clip(risk_cost),
        "false_release_risk": weights.false_release_risk * false_release_risk,
        "byproduct_risk": weights.byproduct_risk * byproduct_pressure,
        "human_review": weights.human_review * human_review_penalty,
    }

    benefit_total = sum(benefit_terms.values())
    penalty_total = sum(penalty_terms.values())
    objective_score = _clip(benefit_total - penalty_total)
    return {
        "objective_score": round(objective_score, 3),
        "benefit_total": round(benefit_total, 3),
        "penalty_total": round(penalty_total, 3),
        "benefit_terms": {key: round(value, 3) for key, value in benefit_terms.items()},
        "penalty_terms": {key: round(value, 3) for key, value in penalty_terms.items()},
        "false_release_risk": round(false_release_risk, 3),
        "byproduct_pressure": round(byproduct_pressure, 3),
        "weights": weights.as_dict(),
    }


def _estimate_false_release_risk(action_id: str, evidence: dict[str, object]) -> float:
    release_readiness = float(evidence.get("release_readiness", 1.0))
    residual = float(evidence.get("pollutant_residual_risk", 0.0))
    hydraulic_confidence = float(evidence.get("hydraulic_confidence", 1.0))
    byproduct_risk = float(evidence.get("byproduct_risk", 0.0))
    sensor_confidence = float(evidence.get("sensor_confidence", 1.0))

    risk = _clip(
        max(0.0, 0.82 - release_readiness) * 1.4
        + max(0.0, residual - 0.35) * 1.2
        + max(0.0, 0.70 - hydraulic_confidence) * 0.9
        + max(0.0, byproduct_risk - 0.65) * 1.1
        + max(0.0, 0.75 - sensor_confidence) * 0.9
    )
    if action_id == "release":
        return risk
    return 0.35 * risk


def _estimate_byproduct_pressure(action_id: str, evidence: dict[str, object]) -> float:
    byproduct_risk = float(evidence.get("byproduct_risk", 0.0))
    oxidant_remaining = float(evidence.get("oxidant_remaining", 0.0))
    dose_factor = float(evidence.get("dose_factor", 0.0))
    pressure = _clip(0.60 * byproduct_risk + 0.25 * max(0.0, oxidant_remaining - 0.55) + 0.35 * max(0.0, dose_factor - 0.20))
    if action_id == "dose_oxidant":
        return pressure
    if action_id == "release":
        return _clip(byproduct_risk)
    return 0.45 * pressure


def _clip(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))
