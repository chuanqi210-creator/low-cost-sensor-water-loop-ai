from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class ValidationPlanningAgent(BaseAgent):
    """Plan slow/side-stream validation that a circular loop can wait for."""

    name = "validation_planning_agent"

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
        plan = self._build_plan(state, fault_ids)

        issues = [
            QualityIssue(
                sensor="validation",
                issue_type="validation_required",
                severity=Severity.WARNING if plan["urgency"] >= 0.45 else Severity.INFO,
                message="需要旁路或离线慢证据来校准软传感和放行判断。",
                evidence=plan,
            )
        ] if plan["urgency"] >= 0.35 else []
        recommendations = [self._sentence(plan)] if plan["urgency"] >= 0.25 else ["当前慢证据需求较低，可维持在线软传感监测。"]
        summary = f"验证规划：{plan['plan_name']}，紧迫度 {plan['urgency']}。"
        confidence = round(min(0.95, max(0.2, 0.50 + 0.35 * plan["urgency"])), 3)

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "validation_plan": plan,
                "fault_ids": sorted(fault_ids),
                "state_used": state,
            },
        )

    def _build_plan(self, state: dict[str, float], fault_ids: set[str]) -> dict[str, object]:
        residual = state.get("pollutant_residual_risk", 0.0)
        release = state.get("release_readiness", 0.0)
        sensor_conf = state.get("sensor_confidence", 1.0)
        byproduct = state.get("byproduct_risk", 0.0)
        oxidant = state.get("oxidant_remaining", 1.0)
        matrix = state.get("matrix_interference", 0.0)
        replacement_urgency = state.get("catalyst_replacement_urgency", 0.0)

        validation_targets: list[str] = []
        plan_name = "routine_soft_sensor_audit"
        urgency = 0.18 + max(0.0, 0.82 - release) * 0.28 + max(0.0, residual - 0.35) * 0.32
        hold_min = 18
        validation_delay_min = 8

        if "sensor_data_unreliable" in fault_ids or sensor_conf < 0.75:
            plan_name = "sensor_reliability_cross_check"
            validation_targets.extend(["grab_sample_COD_or_TOC", "target_pollutant_proxy", "sensor_calibration_check"])
            urgency += 0.30
            hold_min = max(hold_min, 28)
            validation_delay_min = max(validation_delay_min, 12)
        if "release_evidence_insufficient" in fault_ids:
            plan_name = "release_gate_validation"
            validation_targets.extend(["target_pollutant", "COD_or_TOC", "UV254_reference"])
            urgency += 0.24
            hold_min = max(hold_min, 32)
            validation_delay_min = max(validation_delay_min, 14)
        if "oxidant_limitation" in fault_ids or oxidant < 0.35:
            validation_targets.extend(["residual_oxidant_quick_test"])
            urgency += 0.14
            hold_min = max(hold_min, 18)
            validation_delay_min = min(max(validation_delay_min, 6), 14)
        if "byproduct_or_overoxidation_risk" in fault_ids or byproduct >= 0.55:
            plan_name = "byproduct_guard_validation"
            validation_targets.extend(["residual_oxidant", "byproduct_screening", "pH_confirm"])
            urgency += 0.30
            hold_min = max(hold_min, 38)
            validation_delay_min = max(validation_delay_min, 22)
        if "matrix_interference" in fault_ids or matrix >= 0.55:
            plan_name = "matrix_shock_characterization"
            validation_targets.extend(["salinity_or_EC_reference", "turbidity_reference", "COD_or_TOC"])
            urgency += 0.22
            hold_min = max(hold_min, 35)
            validation_delay_min = max(validation_delay_min, 18)
        if "catalyst_lifecycle_exhaustion" in fault_ids or replacement_urgency >= 0.55:
            plan_name = "catalyst_lifecycle_validation"
            validation_targets.extend(["catalyst_activity_assay", "pressure_drop_check", "surface_fouling_inspection"])
            urgency += 0.26
            hold_min = max(hold_min, 45)
            validation_delay_min = max(validation_delay_min, 28)

        if not validation_targets:
            validation_targets = ["periodic_grab_sample_COD_or_TOC"]

        return {
            "plan_name": plan_name,
            "urgency": round(self._clip(urgency), 3),
            "hold_min": int(hold_min),
            "validation_delay_min": int(validation_delay_min),
            "targets": sorted(set(validation_targets)),
            "release_gate": "use validation evidence to update offline_residual_proxy before release",
        }

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
    def _sentence(plan: dict[str, object]) -> str:
        return (
            f"{plan['plan_name']}：暂存 {plan['hold_min']} min，等待验证 {plan['validation_delay_min']} min，"
            f"验证目标 {plan['targets']}。"
        )

    @staticmethod
    def _clip(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
        return max(lo, min(hi, value))
