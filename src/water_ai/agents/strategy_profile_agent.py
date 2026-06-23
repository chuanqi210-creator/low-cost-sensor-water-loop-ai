from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class StrategyProfileAgent(BaseAgent):
    """Select the strategy-objective profile for the downstream optimizer."""

    name = "strategy_profile_agent"

    def __init__(
        self,
        *,
        soft_sensor_report: AgentReport | None = None,
        fault_report: AgentReport | None = None,
    ) -> None:
        self.soft_sensor_report = soft_sensor_report
        self.fault_report = fault_report

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        state = self._state()
        faults = self._faults()
        candidates = self._score_profiles(state, faults)
        ranked = sorted(candidates, key=lambda item: float(item["score"]), reverse=True)
        selected = str(ranked[0]["profile"]) if ranked else "balanced"
        issues = self._issues(selected, state, faults)
        recommendations = [
            f"采用 {selected} 策略目标模板；依据：{'; '.join(ranked[0]['rationale']) if ranked else '无显著偏置'}。"
        ]
        confidence = round(min(0.95, max(0.35, float(ranked[0]["score"]) if ranked else 0.45)), 3)

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=f"策略目标模板：{selected}。",
            issues=issues,
            recommendations=recommendations,
            metrics={
                "selected_profile": selected,
                "profile_scores": ranked,
                "state_used": state,
                "faults_used": faults,
            },
        )

    def _score_profiles(self, state: dict[str, float], faults: list[dict[str, object]]) -> list[dict[str, object]]:
        release_readiness = state.get("release_readiness", 0.0)
        residual = state.get("pollutant_residual_risk", 1.0)
        sensor_conf = state.get("sensor_confidence", 1.0)
        hydraulic_conf = state.get("hydraulic_confidence", 1.0)
        byproduct = state.get("byproduct_risk", 0.0)
        matrix = state.get("matrix_interference", 0.0)
        recycle_gain = state.get("recycle_gain", 0.0)
        oxidant = state.get("oxidant_remaining", 0.0)
        catalyst = state.get("catalyst_activity", 1.0)

        fault_ids = {str(fault.get("fault_id")) for fault in faults}
        high_safety_pressure = (
            sensor_conf < 0.78
            or hydraulic_conf < 0.72
            or byproduct > 0.58
            or matrix > 0.72
            or "byproduct_or_overoxidation_risk" in fault_ids
            or "hydraulic_retention_anomaly" in fault_ids
        )
        urgent_reaction_gap = (
            release_readiness < 0.78
            and recycle_gain > 0.32
            and oxidant < 0.35
            and byproduct < 0.45
            and "oxidant_limitation" in fault_ids
        )
        cost_sensitive_finish = release_readiness >= 0.83 and residual <= 0.28 and sensor_conf >= 0.9 and hydraulic_conf >= 0.85
        regeneration_pressure = catalyst < 0.45 and "catalyst_deactivation" in fault_ids

        return [
            {
                "profile": "safety_first",
                "score": round(
                    0.36
                    + (0.22 if high_safety_pressure else 0.0)
                    + (0.10 if regeneration_pressure else 0.0)
                    + max(0.0, residual - 0.35) * 0.6
                    + max(0.0, byproduct - 0.5) * 0.5,
                    3,
                ),
                "rationale": self._rationale(
                    [
                        (high_safety_pressure, "存在放行、传感、水力或副产物安全压力"),
                        (regeneration_pressure, "催化剂失活会扩大误判代价"),
                        (residual > 0.35, "污染物残留风险高于放行门槛"),
                    ]
                ),
            },
            {
                "profile": "emergency_response",
                "score": round(
                    0.34
                    + (0.24 if urgent_reaction_gap else 0.0)
                    + max(0.0, recycle_gain - 0.28) * 0.28
                    + max(0.0, 0.35 - oxidant) * 0.22,
                    3,
                ),
                "rationale": self._rationale(
                    [
                        (urgent_reaction_gap, "氧化剂不足且回流收益明确，需要快速响应"),
                        (recycle_gain > 0.28, "回流边际收益较高"),
                        (oxidant < 0.35, "氧化剂余量偏低"),
                    ]
                ),
            },
            {
                "profile": "cost_first",
                "score": round(
                    0.32
                    + (0.26 if cost_sensitive_finish else 0.0)
                    + max(0.0, release_readiness - 0.82) * 0.35
                    + max(0.0, 0.30 - residual) * 0.25,
                    3,
                ),
                "rationale": self._rationale(
                    [
                        (cost_sensitive_finish, "放行证据充分，可降低无效等待和能耗"),
                        (release_readiness >= 0.82, "放行准备度已通过门槛"),
                        (residual <= 0.30, "残留风险较低"),
                    ]
                ),
            },
            {
                "profile": "balanced",
                "score": 0.42,
                "rationale": ["没有强烈场景偏置，采用平衡目标"],
            },
        ]

    def _issues(self, selected: str, state: dict[str, float], faults: list[dict[str, object]]) -> list[QualityIssue]:
        if selected != "safety_first":
            return []
        return [
            QualityIssue(
                sensor="strategy_profile",
                issue_type="safety_weighting_active",
                severity=Severity.INFO,
                message="当前策略目标提高安全与误放行风险权重。",
                evidence={"state": state, "faults": faults},
            )
        ]

    def _state(self) -> dict[str, float]:
        if self.soft_sensor_report is None:
            return {}
        state = self.soft_sensor_report.metrics.get("state_estimate", {})
        if not isinstance(state, dict):
            return {}
        return {str(key): float(value) for key, value in state.items() if isinstance(value, int | float)}

    def _faults(self) -> list[dict[str, object]]:
        if self.fault_report is None:
            return []
        faults = self.fault_report.metrics.get("ranked_faults", [])
        if not isinstance(faults, list):
            return []
        credible_faults = []
        for fault in faults:
            if not isinstance(fault, dict):
                continue
            score = float(fault.get("score", 0.0))
            if score >= 0.55:
                credible_faults.append(fault)
        return credible_faults

    @staticmethod
    def _rationale(items: list[tuple[bool, str]]) -> list[str]:
        reasons = [message for active, message in items if active]
        return reasons or ["无显著触发项"]
