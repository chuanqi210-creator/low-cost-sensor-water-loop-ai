from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity
from water_ai.strategy_objective import StrategyObjectiveWeights, compute_strategy_objective, get_strategy_objective_weights


class CostSafetyAgent(BaseAgent):
    """Evaluate candidate actions by safety, cost, time, and operational burden."""

    name = "cost_safety_agent"

    def __init__(
        self,
        *,
        control_report: AgentReport | None = None,
        engineering_constraints_report: AgentReport | None = None,
        collaborative_control_report: AgentReport | None = None,
        objective_profile: str = "balanced",
        objective_weights: StrategyObjectiveWeights | None = None,
    ) -> None:
        self.control_report = control_report
        self.engineering_constraints_report = engineering_constraints_report
        self.collaborative_control_report = collaborative_control_report
        self.objective_profile = "custom" if objective_weights is not None else objective_profile
        self.objective_weights = objective_weights or get_strategy_objective_weights(objective_profile)

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        actions = self._actions()
        evaluated = [self._evaluate_action(action) for action in actions]
        evaluated.sort(key=lambda item: item["objective_score"], reverse=True)

        issues = [
            QualityIssue(
                sensor="cost_safety",
                issue_type=item["action_id"],
                severity=Severity.WARNING if item["risk_cost"] >= 0.55 else Severity.INFO,
                message=item["action_name"],
                evidence=item,
            )
            for item in evaluated
            if item["original_score"] >= 0.35
        ]
        recommendations = [self._sentence(item) for item in evaluated if self._is_recommended(item)][:4]
        summary = self._summary(evaluated)
        confidence = round(min(0.95, max(0.1, sum(item["objective_score"] for item in evaluated[:3]) / 3)), 3)

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations or ["没有需要成本安全评价的候选动作。"],
            metrics={
                "evaluated_actions": evaluated,
                "recommended_action_ids": [item["action_id"] for item in evaluated if self._is_recommended(item)],
                "strategy_objective_profile": self.objective_profile,
                "strategy_objective_weights": self.objective_weights.as_dict(),
            },
        )

    def _evaluate_action(self, action: dict[str, object]) -> dict[str, object]:
        action_id = str(action["action_id"])
        base = float(action["score"])

        cost_table = {
            "hold_for_validation": {"safety_gain": 0.78, "money_cost": 0.25, "time_cost": 0.42, "energy_cost": 0.05, "risk_cost": 0.12},
            "inspect_hydraulics": {"safety_gain": 0.72, "money_cost": 0.18, "time_cost": 0.35, "energy_cost": 0.03, "risk_cost": 0.08},
            "calibrate_sensors": {"safety_gain": 0.68, "money_cost": 0.22, "time_cost": 0.34, "energy_cost": 0.02, "risk_cost": 0.08},
            "recirculate": {"safety_gain": 0.72, "money_cost": 0.22, "time_cost": 0.32, "energy_cost": 0.28, "risk_cost": 0.12},
            "regenerate_catalyst": {"safety_gain": 0.84, "money_cost": 0.48, "time_cost": 0.52, "energy_cost": 0.16, "risk_cost": 0.12},
            "replace_catalyst": {"safety_gain": 0.90, "money_cost": 0.78, "time_cost": 0.68, "energy_cost": 0.08, "risk_cost": 0.10},
            "dose_oxidant": {"safety_gain": 0.78, "money_cost": 0.32, "time_cost": 0.16, "energy_cost": 0.06, "risk_cost": 0.16},
            "switch_or_pretreat": {"safety_gain": 0.86, "money_cost": 0.52, "time_cost": 0.45, "energy_cost": 0.35, "risk_cost": 0.18},
            "release": {"safety_gain": 0.72, "money_cost": 0.02, "time_cost": 0.0, "energy_cost": 0.0, "risk_cost": 0.08},
        }
        costs = cost_table.get(action_id, {"safety_gain": 0.3, "money_cost": 0.3, "time_cost": 0.3, "energy_cost": 0.2, "risk_cost": 0.3})
        if action.get("joint_action_id"):
            costs = {
                "safety_gain": 0.82,
                "money_cost": 0.42,
                "time_cost": 0.46,
                "energy_cost": 0.34,
                "risk_cost": 0.14,
            }
        evidence = action.get("evidence", {})
        knowledge_action_bias = 0.0
        if isinstance(evidence, dict):
            knowledge_action_bias = float(evidence.get("knowledge_action_bias", 0.0))
            if action_id == "release" and float(evidence.get("release_readiness", 0.0)) < 0.82:
                costs = {**costs, "safety_gain": 0.1, "risk_cost": 0.9}
            if action_id == "release" and float(evidence.get("byproduct_risk", 0.0)) > 0.65:
                costs = {**costs, "safety_gain": 0.1, "risk_cost": 0.88}
            if action_id == "dose_oxidant" and float(evidence.get("oxidant_remaining", 1.0)) >= 0.45:
                costs = {**costs, "safety_gain": 0.15, "risk_cost": 0.62}
            if action_id == "dose_oxidant" and (float(evidence.get("byproduct_risk", 0.0)) >= 0.55 or float(evidence.get("dose_factor", 0.0)) >= 0.28):
                costs = {**costs, "safety_gain": min(costs["safety_gain"], 0.35), "risk_cost": max(costs["risk_cost"], 0.58)}
            if action_id == "switch_or_pretreat" and float(evidence.get("matrix_interference", 0.0)) < 0.55:
                costs = {**costs, "safety_gain": 0.4, "money_cost": 0.68, "time_cost": 0.62, "risk_cost": 0.35}
            if action_id == "switch_or_pretreat" and float(evidence.get("matrix_interference", 0.0)) >= 0.75:
                costs = {**costs, "safety_gain": 1.0, "money_cost": 0.42, "time_cost": 0.36, "energy_cost": 0.30, "risk_cost": 0.07}
            if action_id == "regenerate_catalyst" and float(evidence.get("catalyst_activity", 1.0)) < 0.48:
                costs = {**costs, "safety_gain": 0.96, "money_cost": 0.42, "time_cost": 0.46, "risk_cost": 0.07}
            if action_id == "regenerate_catalyst" and float(evidence.get("catalyst_activity", 1.0)) > 0.64:
                costs = {**costs, "safety_gain": 0.24, "money_cost": 0.64, "time_cost": 0.72, "risk_cost": 0.42}
            if action_id == "regenerate_catalyst" and (
                float(evidence.get("catalyst_replacement_urgency", 0.0)) >= 0.68
                or float(evidence.get("catalyst_regeneration_potential", 1.0)) <= 0.28
            ):
                costs = {**costs, "safety_gain": 0.34, "money_cost": 0.62, "time_cost": 0.70, "risk_cost": 0.44}
            if action_id == "replace_catalyst" and float(evidence.get("catalyst_replacement_urgency", 0.0)) >= 0.62:
                costs = {**costs, "safety_gain": 0.98, "money_cost": 0.72, "time_cost": 0.64, "energy_cost": 0.07, "risk_cost": 0.05}
            if action_id == "replace_catalyst" and float(evidence.get("catalyst_replacement_urgency", 0.0)) < 0.55:
                costs = {**costs, "safety_gain": 0.32, "money_cost": 0.86, "time_cost": 0.76, "risk_cost": 0.36}
            costs = self._apply_knowledge_cost_adjustment(costs, knowledge_action_bias)
        engineering_patch = self._engineering_action_patch(action_id)
        costs = self._apply_engineering_constraint_patch(costs, engineering_patch)
        review_penalty = 0.08 if action.get("requires_human_review") else 0.0
        net_score = self._clip(
            0.55 * base
            + 0.35 * costs["safety_gain"]
            - 0.18 * costs["money_cost"]
            - 0.12 * costs["time_cost"]
            - 0.10 * costs["energy_cost"]
            - 0.28 * costs["risk_cost"]
            - review_penalty
        )
        objective = compute_strategy_objective(
            action_id=action_id,
            original_score=base,
            safety_gain=float(costs["safety_gain"]),
            money_cost=float(costs["money_cost"]),
            time_cost=float(costs["time_cost"]),
            energy_cost=float(costs["energy_cost"]),
            risk_cost=float(costs["risk_cost"]),
            requires_human_review=bool(action.get("requires_human_review")),
            evidence=evidence if isinstance(evidence, dict) else {},
            knowledge_action_bias=knowledge_action_bias,
            weights=self.objective_weights,
        )
        return {
            "action_id": action_id,
            "joint_action_id": action.get("joint_action_id"),
            "action_name": action["action_name"],
            "original_score": round(base, 3),
            "net_score": round(net_score, 3),
            "objective_score": objective["objective_score"],
            "objective": objective,
            "safety_gain": costs["safety_gain"],
            "money_cost": costs["money_cost"],
            "time_cost": costs["time_cost"],
            "energy_cost": costs["energy_cost"],
            "risk_cost": costs["risk_cost"],
            "knowledge_action_bias": round(knowledge_action_bias, 3),
            "knowledge_cost_adjustment": costs.get("knowledge_cost_adjustment", {}),
            "engineering_constraint_patch": engineering_patch,
            "engineering_constraint_penalty": round(float(engineering_patch.get("engineering_penalty", 0.0)), 3),
            "engineering_hard_block": bool(engineering_patch.get("hard_block", False)),
            "requires_human_review": bool(action.get("requires_human_review")),
            "parameters": action.get("parameters", {}),
        }

    def _actions(self) -> list[dict[str, object]]:
        actions: list[dict[str, object]] = []
        if self.control_report is None:
            base_actions = []
        else:
            base_actions = self.control_report.metrics.get("ranked_actions", [])
            base_actions = base_actions if isinstance(base_actions, list) else []
        actions.extend(action for action in base_actions if isinstance(action, dict))
        actions.extend(self._collaborative_actions())
        return actions

    def _collaborative_actions(self) -> list[dict[str, object]]:
        if self.collaborative_control_report is None:
            return []
        joint_actions = self.collaborative_control_report.metrics.get("joint_action_matrix", [])
        if not isinstance(joint_actions, list):
            return []
        converted: list[dict[str, object]] = []
        for row in joint_actions[:3]:
            if not isinstance(row, dict) or not row.get("joint_action_id"):
                continue
            reward = row.get("reward_components", {})
            reward = reward if isinstance(reward, dict) else {}
            converted.append(
                {
                    "action_id": str(row["joint_action_id"]),
                    "joint_action_id": str(row["joint_action_id"]),
                    "action_name": f"多设施协同：{row.get('control_intent', row['joint_action_id'])}",
                    "score": float(row.get("joint_policy_score", 0.0)),
                    "parameters": {
                        "facility_agents": row.get("facility_agents", []),
                        "local_actions": row.get("actions", []),
                        "control_intent": row.get("control_intent", ""),
                    },
                    "requires_human_review": True,
                    "evidence": {
                        "joint_action_id": row["joint_action_id"],
                        "combined_state_vector": row.get("combined_state_vector", {}),
                        "reward_components": reward,
                        "engineering_constraint_evaluation": row.get("engineering_constraint_evaluation", {}),
                        "writeback_boundary": row.get("writeback_boundary", "collaborative action candidate only"),
                    },
                }
            )
        return converted

    @staticmethod
    def _sentence(item: dict[str, object]) -> str:
        return (
            f"{item['action_name']}：策略目标评分 {item['objective_score']}，净收益评分 {item['net_score']}；"
            f"安全收益 {item['safety_gain']}，成本 {item['money_cost']}，时间 {item['time_cost']}，风险 {item['risk_cost']}。"
        )

    @staticmethod
    def _summary(evaluated: list[dict[str, object]]) -> str:
        if not evaluated:
            return "没有候选动作可评价。"
        top = evaluated[0]
        return f"成本安全最优动作：{top['action_name']}，策略目标评分 {top['objective_score']}，净收益评分 {top['net_score']}。"

    @staticmethod
    def _is_recommended(item: dict[str, object]) -> bool:
        return float(item["original_score"]) >= 0.35 and float(item["objective_score"]) >= 0.35

    def _apply_knowledge_cost_adjustment(
        self,
        costs: dict[str, float],
        knowledge_action_bias: float,
    ) -> dict[str, float | dict[str, float]]:
        if abs(knowledge_action_bias) < 1e-9:
            return costs

        safety_delta = 0.22 * knowledge_action_bias
        risk_delta = -0.34 * knowledge_action_bias
        time_delta = -0.08 * knowledge_action_bias if knowledge_action_bias > 0 else 0.06 * abs(knowledge_action_bias)
        adjusted = {
            **costs,
            "safety_gain": self._clip(costs["safety_gain"] + safety_delta),
            "risk_cost": self._clip(costs["risk_cost"] + risk_delta),
            "time_cost": self._clip(costs["time_cost"] + time_delta),
            "knowledge_cost_adjustment": {
                "safety_gain_delta": round(safety_delta, 3),
                "risk_cost_delta": round(risk_delta, 3),
                "time_cost_delta": round(time_delta, 3),
            },
        }
        return adjusted

    def _engineering_action_patch(self, action_id: str) -> dict[str, object]:
        if self.engineering_constraints_report is None:
            return {}
        patch_block = self.engineering_constraints_report.metrics.get("action_constraint_patch", {})
        if not isinstance(patch_block, dict):
            arbitration_patch = self.engineering_constraints_report.metrics.get("arbitration_patch", {})
            if isinstance(arbitration_patch, dict):
                patch_block = arbitration_patch.get("action_constraint_patch", {})
        if not isinstance(patch_block, dict):
            return {}
        patch = patch_block.get(action_id, {})
        return patch if isinstance(patch, dict) else {}

    def _apply_engineering_constraint_patch(
        self,
        costs: dict[str, float | dict[str, float]],
        patch: dict[str, object],
    ) -> dict[str, float | dict[str, float]]:
        if not patch:
            return costs
        penalty = float(patch.get("engineering_penalty", 0.0))
        feasibility = float(patch.get("execution_feasibility", 1.0))
        hard_block = bool(patch.get("hard_block", False))
        adjusted = {
            **costs,
            "money_cost": self._clip(float(costs["money_cost"]) + 0.16 * penalty),
            "time_cost": self._clip(float(costs["time_cost"]) + 0.22 * penalty + 0.10 * max(0.0, 0.55 - feasibility)),
            "energy_cost": self._clip(float(costs["energy_cost"]) + 0.10 * penalty),
            "risk_cost": self._clip(float(costs["risk_cost"]) + 0.30 * penalty + (0.25 if hard_block else 0.0)),
            "safety_gain": self._clip(float(costs["safety_gain"]) - 0.24 * penalty - (0.35 if hard_block else 0.0)),
            "engineering_cost_adjustment": {
                "engineering_penalty": round(penalty, 3),
                "execution_feasibility": round(feasibility, 3),
                "hard_block": hard_block,
                "block_reasons": patch.get("block_reasons", []),
            },
        }
        return adjusted

    @staticmethod
    def _clip(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
        return max(lo, min(hi, value))
