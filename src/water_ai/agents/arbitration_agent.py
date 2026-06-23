from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class ArbitrationAgent(BaseAgent):
    """Fuse all upstream agents into a final risk-constrained decision."""

    name = "arbitration_agent"

    def __init__(
        self,
        *,
        soft_sensor_report: AgentReport | None = None,
        control_report: AgentReport | None = None,
        cost_safety_report: AgentReport | None = None,
        engineering_constraints_report: AgentReport | None = None,
    ) -> None:
        self.soft_sensor_report = soft_sensor_report
        self.control_report = control_report
        self.cost_safety_report = cost_safety_report
        self.engineering_constraints_report = engineering_constraints_report

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        state = self._state()
        action_pool = self._action_pool()
        blocked_actions = self._blocked_actions(state, action_pool)
        final_plan = self._final_plan(action_pool, blocked_actions, state)
        safety_gates = self._safety_gates(state) + self._engineering_safety_gates()

        issues = [
            QualityIssue(
                sensor="arbitration",
                issue_type=gate["gate_id"],
                severity=Severity.CRITICAL if not gate["passed"] else Severity.INFO,
                message=gate["message"],
                evidence=gate,
            )
            for gate in safety_gates
            if not gate["passed"]
        ]
        recommendations = [self._sentence(action) for action in final_plan]
        if blocked_actions:
            recommendations.append(f"禁止动作：{', '.join(blocked_actions)}。")
        summary = self._summary(final_plan, safety_gates)
        confidence = round(
            min(
                0.95,
                max(0.1, sum(self._decision_score(action) for action in final_plan[:3]) / max(1, min(3, len(final_plan)))),
            ),
            3,
        )

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations or ["未形成最终动作，维持暂存并请求人工复核。"],
            metrics={
                "final_plan": final_plan,
                "blocked_actions": blocked_actions,
                "safety_gates": safety_gates,
                "state_used": state,
                "engineering_constraints_used": self._engineering_constraints_used(),
            },
        )

    def _action_pool(self) -> list[dict[str, object]]:
        if self.cost_safety_report is None:
            return []
        evaluated = self.cost_safety_report.metrics.get("evaluated_actions", [])
        if not isinstance(evaluated, list):
            return []
        return [item for item in evaluated if isinstance(item, dict)]

    def _blocked_actions(self, state: dict[str, float], actions: list[dict[str, object]]) -> list[str]:
        blocked: list[str] = []
        release_readiness = state.get("release_readiness", 0.0)
        residual = state.get("pollutant_residual_risk", 1.0)
        oxidant_remaining = state.get("oxidant_remaining", 1.0)
        recycle_gain = state.get("recycle_gain", 0.0)
        catalyst = state.get("catalyst_activity", 1.0)
        replacement_urgency = state.get("catalyst_replacement_urgency", 0.0)
        regeneration_potential = state.get("catalyst_regeneration_potential", 1.0)
        sensor_conf = state.get("sensor_confidence", 0.0)
        hydraulic_conf = state.get("hydraulic_confidence", 1.0)
        byproduct = state.get("byproduct_risk", 0.0)

        if release_readiness < 0.82 or residual > 0.35 or sensor_conf < 0.75 or hydraulic_conf < 0.7 or byproduct > 0.65:
            blocked.append("release")
        if byproduct >= 0.70:
            blocked.append("dose_oxidant")
        if oxidant_remaining >= 0.45:
            blocked.append("dose_oxidant")
        if recycle_gain < 0.2:
            blocked.append("recirculate")
        if catalyst > 0.68:
            blocked.append("regenerate_catalyst")
        if replacement_urgency < 0.55:
            blocked.append("replace_catalyst")
        if replacement_urgency >= 0.72 and regeneration_potential <= 0.30:
            blocked.append("regenerate_catalyst")
        if sensor_conf < 0.7:
            blocked.append("automatic_release")
        blocked.extend(self._engineering_blocked_actions())
        return list(dict.fromkeys(blocked))

    def _final_plan(self, actions: list[dict[str, object]], blocked_actions: list[str], state: dict[str, float]) -> list[dict[str, object]]:
        blocked = set(blocked_actions)
        selected: list[dict[str, object]] = []
        for action in actions:
            action_id = str(action["action_id"])
            if action_id in blocked:
                continue
            if float(action["original_score"]) < 0.35 or self._decision_score(action) < 0.35:
                continue
            selected.append(action)
        release_actions = [action for action in selected if str(action["action_id"]) == "release"]
        if release_actions:
            return release_actions[:1]
        selected = self._remove_mutually_exclusive_catalyst_actions(selected)
        return self._apply_order_constraints(selected[:4], state)

    def _remove_mutually_exclusive_catalyst_actions(self, selected: list[dict[str, object]]) -> list[dict[str, object]]:
        catalyst_actions = [action for action in selected if str(action["action_id"]) in {"regenerate_catalyst", "replace_catalyst"}]
        if len(catalyst_actions) <= 1:
            return selected
        best_catalyst_action = max(catalyst_actions, key=self._decision_score)
        return [
            action
            for action in selected
            if str(action["action_id"]) not in {"regenerate_catalyst", "replace_catalyst"}
            or action is best_catalyst_action
        ]

    def _apply_order_constraints(self, selected: list[dict[str, object]], state: dict[str, float]) -> list[dict[str, object]]:
        matrix = state.get("matrix_interference", 0.0)
        hydraulic_conf = state.get("hydraulic_confidence", 1.0)
        catalyst = state.get("catalyst_activity", 1.0)
        replacement_urgency = state.get("catalyst_replacement_urgency", 0.0)

        def priority(action: dict[str, object]) -> tuple[int, float]:
            action_id = str(action["action_id"])
            if matrix >= 0.75 and action_id == "switch_or_pretreat":
                return (0, -self._decision_score(action))
            if hydraulic_conf < 0.7 and action_id == "inspect_hydraulics":
                return (0, -self._decision_score(action))
            if replacement_urgency >= 0.62 and action_id == "replace_catalyst":
                return (0, -self._decision_score(action))
            if catalyst < 0.55 and action_id == "regenerate_catalyst":
                return (0, -self._decision_score(action))
            if action_id == "recirculate":
                return (2, -self._decision_score(action))
            return (1, -self._decision_score(action))

        return sorted(selected, key=priority)

    def _safety_gates(self, state: dict[str, float]) -> list[dict[str, object]]:
        release_readiness = state.get("release_readiness", 0.0)
        sensor_conf = state.get("sensor_confidence", 0.0)
        hydraulic_conf = state.get("hydraulic_confidence", 1.0)
        byproduct = state.get("byproduct_risk", 0.0)
        residual = state.get("pollutant_residual_risk", 1.0)
        return [
            {
                "gate_id": "release_readiness_gate",
                "passed": release_readiness >= 0.82,
                "value": release_readiness,
                "threshold": 0.82,
                "message": "放行准备度不足，禁止自动放行。",
            },
            {
                "gate_id": "sensor_confidence_gate",
                "passed": sensor_conf >= 0.75,
                "value": sensor_conf,
                "threshold": 0.75,
                "message": "传感可信度不足，需要校准或旁路验证。",
            },
            {
                "gate_id": "residual_risk_gate",
                "passed": residual <= 0.35,
                "value": residual,
                "threshold": 0.35,
                "message": "污染物残留风险偏高，禁止放行。",
            },
            {
                "gate_id": "hydraulic_confidence_gate",
                "passed": hydraulic_conf >= 0.7,
                "value": hydraulic_conf,
                "threshold": 0.7,
                "message": "水力置信度不足，需要核查泵阀、回流管路和实际 HRT。",
            },
            {
                "gate_id": "byproduct_risk_gate",
                "passed": byproduct <= 0.65,
                "value": byproduct,
                "threshold": 0.65,
                "message": "副产物或过氧化风险偏高，禁止自动放行。",
            },
        ]

    def _engineering_blocked_actions(self) -> list[str]:
        if self.engineering_constraints_report is None:
            return []
        arbitration_patch = self.engineering_constraints_report.metrics.get("arbitration_patch", {})
        if isinstance(arbitration_patch, dict):
            blocked = arbitration_patch.get("blocked_action_ids", [])
            if isinstance(blocked, list):
                return [str(item) for item in blocked]
        patch = self.engineering_constraints_report.metrics.get("action_constraint_patch", {})
        if not isinstance(patch, dict):
            return []
        return [action_id for action_id, item in patch.items() if isinstance(item, dict) and bool(item.get("hard_block", False))]

    def _engineering_safety_gates(self) -> list[dict[str, object]]:
        if self.engineering_constraints_report is None:
            return []
        readiness = self.engineering_constraints_report.metrics.get("readiness", {})
        readiness = readiness if isinstance(readiness, dict) else {}
        blocked = self._engineering_blocked_actions()
        return [
            {
                "gate_id": "engineering_execution_field_gate",
                "passed": bool(readiness.get("field_ready", False)),
                "value": readiness.get("engineering_constraints_status", "not_available"),
                "threshold": "field_execution_replay + PLC/SCADA + SOP",
                "message": "工程执行约束尚未通过现场执行 replay，只允许候选排序和人工复核，不允许自动执行器写入。",
            },
            {
                "gate_id": "engineering_hard_block_gate",
                "passed": not blocked,
                "value": blocked,
                "threshold": "no hard-blocked actions in final arbitration patch",
                "message": "存在池容、库存、维护窗口、执行器延迟或人工复核硬约束，相关动作必须阻断或降级。",
            },
        ]

    def _engineering_constraints_used(self) -> dict[str, object]:
        if self.engineering_constraints_report is None:
            return {"available": False}
        readiness = self.engineering_constraints_report.metrics.get("readiness", {})
        return {
            "available": True,
            "blocked_action_ids": self._engineering_blocked_actions(),
            "readiness": readiness if isinstance(readiness, dict) else {},
        }

    def _state(self) -> dict[str, float]:
        if self.soft_sensor_report is None:
            return {}
        state = self.soft_sensor_report.metrics.get("state_estimate", {})
        if not isinstance(state, dict):
            return {}
        return {str(k): float(v) for k, v in state.items() if isinstance(v, int | float)}

    @staticmethod
    def _sentence(action: dict[str, object]) -> str:
        decision_score = ArbitrationAgent._decision_score(action)
        return f"执行：{action['action_name']}；策略目标 {decision_score}，净收益 {action['net_score']}；参数 {action['parameters']}。"

    @staticmethod
    def _summary(final_plan: list[dict[str, object]], safety_gates: list[dict[str, object]]) -> str:
        failed = [gate["gate_id"] for gate in safety_gates if not gate["passed"]]
        if not final_plan:
            return f"最终仲裁：无自动执行动作；未通过安全门 {failed}。"
        return f"最终仲裁：执行 {final_plan[0]['action_name']} 等 {len(final_plan)} 个动作；未通过安全门 {failed}。"

    @staticmethod
    def _decision_score(action: dict[str, object]) -> float:
        return float(action.get("objective_score", action.get("net_score", 0.0)))
