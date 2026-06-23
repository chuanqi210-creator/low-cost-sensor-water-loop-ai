from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class CatalystLifecycleAgent(BaseAgent):
    """Assess catalyst aging, regeneration value, and replacement timing."""

    name = "catalyst_lifecycle_agent"

    def __init__(
        self,
        *,
        soft_sensor_report: AgentReport | None = None,
        fault_report: AgentReport | None = None,
    ) -> None:
        self.soft_sensor_report = soft_sensor_report
        self.fault_report = fault_report

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        state = self._state()
        fault_ids = self._fault_ids()
        lifecycle_state = self._lifecycle_state(state)
        options = self._rank_options(lifecycle_state, fault_ids)
        decision = options[0]

        issues = [
            QualityIssue(
                sensor="catalyst_lifecycle",
                issue_type="catalyst_replacement_urgency",
                severity=Severity.CRITICAL if lifecycle_state["replacement_urgency"] >= 0.75 else Severity.WARNING,
                message="催化剂寿命风险偏高，需要比较再生和更换。",
                evidence=lifecycle_state,
            )
        ] if lifecycle_state["replacement_urgency"] >= 0.55 else []
        recommendations = [self._sentence(option) for option in options if option["score"] >= 0.35][:3]
        summary = f"催化剂生命周期建议：{decision['action_name']}，评分 {decision['score']}。"
        confidence = round(min(0.95, max(0.15, 0.45 + lifecycle_state["evidence_strength"] * 0.35)), 3)

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations or ["催化剂生命周期风险较低，继续监测即可。"],
            metrics={
                "lifecycle_state": lifecycle_state,
                "maintenance_decision": decision,
                "ranked_maintenance_options": options,
                "fault_ids": sorted(fault_ids),
            },
        )

    def _lifecycle_state(self, state: dict[str, float]) -> dict[str, float]:
        catalyst_activity = state.get("catalyst_activity", 1.0)
        lifetime_fraction = state.get("catalyst_lifetime_fraction", 1.0)
        regen_count = state.get("catalyst_regen_count", 0.0)
        age_cycles = state.get("catalyst_age_cycles", state.get("cycle_id", 0.0))
        regeneration_potential = state.get(
            "catalyst_regeneration_potential",
            self._clip(0.70 * lifetime_fraction + 0.20 * max(0.0, 0.64 - catalyst_activity) - 0.08 * regen_count),
        )
        replacement_urgency = state.get(
            "catalyst_replacement_urgency",
            self._clip(
                0.40 * (1.0 - lifetime_fraction)
                + 0.12 * regen_count
                + 0.10 * min(age_cycles / 10.0, 1.0)
                + 0.22 * max(0.0, 0.45 - catalyst_activity)
                + 0.14 * (1.0 - regeneration_potential)
            ),
        )
        evidence_strength = self._clip(
            0.34
            + 0.18 * min(age_cycles / 6.0, 1.0)
            + 0.20 * min(regen_count / 3.0, 1.0)
            + 0.28 * (1.0 if "catalyst_lifetime_fraction" in state else 0.0)
        )
        return {
            "catalyst_activity": round(catalyst_activity, 3),
            "catalyst_lifetime_fraction": round(lifetime_fraction, 3),
            "catalyst_regen_count": round(regen_count, 3),
            "catalyst_age_cycles": round(age_cycles, 3),
            "regeneration_potential": round(regeneration_potential, 3),
            "replacement_urgency": round(replacement_urgency, 3),
            "evidence_strength": round(evidence_strength, 3),
        }

    def _rank_options(
        self,
        lifecycle_state: dict[str, float],
        fault_ids: set[str],
    ) -> list[dict[str, object]]:
        catalyst = lifecycle_state["catalyst_activity"]
        lifetime = lifecycle_state["catalyst_lifetime_fraction"]
        regen_count = lifecycle_state["catalyst_regen_count"]
        age_cycles = lifecycle_state["catalyst_age_cycles"]
        regeneration_potential = lifecycle_state["regeneration_potential"]
        replacement_urgency = lifecycle_state["replacement_urgency"]
        catalyst_fault = "catalyst_deactivation" in fault_ids or "catalyst_lifecycle_exhaustion" in fault_ids

        options = [
            {
                "action_id": "regenerate_catalyst",
                "action_name": "优先再生催化剂",
                "score": self._clip(
                    (0.36 if catalyst_fault else 0.0)
                    + max(0.0, 0.56 - catalyst) * 0.82
                    + regeneration_potential * 0.42
                    - max(0.0, replacement_urgency - 0.58) * 0.55
                ),
                "rationale": "活性不足但仍有可恢复寿命，适合先再生再回流验证。",
            },
            {
                "action_id": "replace_catalyst",
                "action_name": "更换催化剂模块",
                "score": self._clip(
                    max(0.0, replacement_urgency - 0.46) * 1.25
                    + max(0.0, 0.30 - regeneration_potential) * 0.95
                    + (0.10 if regen_count >= 2 else 0.0)
                    + (0.08 if lifetime <= 0.36 else 0.0)
                ),
                "rationale": "再生边际收益下降，继续再生可能增加停机和材料损耗。",
            },
            {
                "action_id": "monitor_catalyst",
                "action_name": "维持监测",
                "score": self._clip(
                    0.52
                    + lifetime * 0.28
                    - max(0.0, 0.52 - catalyst) * 0.45
                    - replacement_urgency * 0.40
                    - min(age_cycles / 12.0, 1.0) * 0.08
                ),
                "rationale": "寿命风险尚可接受，暂不触发维护动作。",
            },
        ]
        for option in options:
            option["score"] = round(float(option["score"]), 3)
        options.sort(key=lambda item: item["score"], reverse=True)
        return options

    def _state(self) -> dict[str, float]:
        if self.soft_sensor_report is None:
            return {}
        state = self.soft_sensor_report.metrics.get("state_estimate", {})
        if not isinstance(state, dict):
            return {}
        return {str(k): float(v) for k, v in state.items() if isinstance(v, int | float)}

    def _fault_ids(self) -> set[str]:
        if self.fault_report is None:
            return set()
        faults = self.fault_report.metrics.get("ranked_faults", [])
        if not isinstance(faults, list):
            return set()
        return {str(fault["fault_id"]) for fault in faults if isinstance(fault, dict) and float(fault.get("score", 0.0)) >= 0.35}

    @staticmethod
    def _sentence(option: dict[str, object]) -> str:
        return f"{option['action_name']}：评分 {option['score']}；依据：{option['rationale']}"

    @staticmethod
    def _clip(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
        return max(lo, min(hi, value))
