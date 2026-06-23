from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class ControlStrategyAgent(BaseAgent):
    """Convert diagnosis results into executable circular-treatment actions."""

    name = "control_strategy_agent"

    def __init__(
        self,
        *,
        soft_sensor_report: AgentReport | None = None,
        fault_report: AgentReport | None = None,
        catalyst_lifecycle_report: AgentReport | None = None,
        validation_planning_report: AgentReport | None = None,
        matrix_shock_fast_proxy_report: AgentReport | None = None,
    ) -> None:
        self.soft_sensor_report = soft_sensor_report
        self.fault_report = fault_report
        self.catalyst_lifecycle_report = catalyst_lifecycle_report
        self.validation_planning_report = validation_planning_report
        self.matrix_shock_fast_proxy_report = matrix_shock_fast_proxy_report

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        state = self._state()
        faults = self._faults()
        catalyst_lifecycle = self._catalyst_lifecycle()
        validation_plan = self._validation_plan()
        knowledge_action_biases = self._knowledge_action_biases()
        knowledge_reasoning_source = self._knowledge_reasoning_source()
        matrix_shock_fast_proxy = self._matrix_shock_fast_proxy()
        actions = self._rank_actions(state, faults, knowledge_action_biases, catalyst_lifecycle, validation_plan, matrix_shock_fast_proxy)
        executable_plan = [action for action in actions if action["score"] >= 0.35]

        issues = [
            QualityIssue(
                sensor="control",
                issue_type=action["action_id"],
                severity=Severity.WARNING if action["requires_human_review"] else Severity.INFO,
                message=action["action_name"],
                evidence=action["evidence"],
            )
            for action in executable_plan
        ]
        recommendations = [self._action_sentence(action) for action in executable_plan[:4]]
        summary = self._summary(executable_plan)
        confidence = round(min(0.95, max(0.1, sum(a["score"] for a in executable_plan[:3]) / max(1, min(3, len(executable_plan))))), 3)

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations or ["暂不执行自动动作，继续采集数据。"],
            metrics={
                "ranked_actions": actions,
                "executable_plan": executable_plan,
                "state_used": state,
                "fault_ids": [fault["fault_id"] for fault in faults],
                "knowledge_action_biases": knowledge_action_biases,
                "knowledge_reasoning_source": knowledge_reasoning_source,
                "catalyst_lifecycle": catalyst_lifecycle,
                "validation_plan": validation_plan,
                "matrix_shock_fast_proxy": matrix_shock_fast_proxy,
            },
        )

    def _rank_actions(
        self,
        state: dict[str, float],
        faults: list[dict[str, object]],
        knowledge_action_biases: dict[str, float],
        catalyst_lifecycle: dict[str, object],
        validation_plan: dict[str, object],
        matrix_shock_fast_proxy: dict[str, object],
    ) -> list[dict[str, object]]:
        fault_ids = {str(fault["fault_id"]) for fault in faults if fault.get("score", 0) >= 0.35}
        residual = state.get("pollutant_residual_risk", 0.0)
        release = state.get("release_readiness", 0.0)
        compliance = state.get("compliance_probability", 0.0)
        recycle_gain = state.get("recycle_gain", 0.0)
        oxidant = state.get("oxidant_remaining", 1.0)
        matrix = state.get("matrix_interference", 0.0)
        catalyst = state.get("catalyst_activity", 1.0)
        catalyst_lifetime = state.get("catalyst_lifetime_fraction", 1.0)
        catalyst_regen_count = state.get("catalyst_regen_count", 0.0)
        regeneration_potential = state.get("catalyst_regeneration_potential", 1.0)
        replacement_urgency = state.get("catalyst_replacement_urgency", 0.0)
        lifecycle_decision = str(catalyst_lifecycle.get("decision_action_id", "monitor_catalyst"))
        byproduct = state.get("byproduct_risk", 0.0)
        hydraulic_confidence = state.get("hydraulic_confidence", 1.0)
        cycle_id = int(state.get("cycle_id", 0.0))
        cycle_window_fault = "cycle_window_insufficient" in fault_ids or "reaction_time_insufficient" in fault_ids
        catalyst_fault = "catalyst_deactivation" in fault_ids
        recycle_ratio = round(self._clip(0.28 + recycle_gain * 0.55 + max(0.0, residual - 0.35) * 0.25, 0.25, 0.65), 2)
        extra_retention_min = int(round(12 + recycle_gain * 28 + max(0.0, residual - 0.35) * 35 + (8 if cycle_window_fault else 0)))
        hold_min = int(round(15 + max(0.0, 0.82 - release) * 45 + (8 if cycle_window_fault else 0)))
        validation_delay_min = int(round(8 + max(0.0, 0.82 - release) * 18 + (8 if byproduct >= 0.55 else 0)))
        validation_urgency = float(validation_plan.get("urgency", 0.0)) if isinstance(validation_plan.get("urgency", 0.0), int | float) else 0.0
        hold_min = max(hold_min, int(validation_plan.get("hold_min", hold_min)) if isinstance(validation_plan.get("hold_min", hold_min), int | float) else hold_min)
        validation_delay_min = max(
            validation_delay_min,
            int(validation_plan.get("validation_delay_min", validation_delay_min))
            if isinstance(validation_plan.get("validation_delay_min", validation_delay_min), int | float)
            else validation_delay_min,
        )
        proxy_control = matrix_shock_fast_proxy.get("control_adaptation", {})
        proxy_readiness = matrix_shock_fast_proxy.get("readiness", {})
        proxy_metrics = matrix_shock_fast_proxy.get("proxy", {})
        proxy_protective_mode = bool(proxy_control.get("protective_mode", False)) if isinstance(proxy_control, dict) else False
        if proxy_protective_mode and isinstance(proxy_control, dict):
            hold_min = max(
                hold_min,
                int(proxy_control.get("recommended_hold_min", hold_min))
                if isinstance(proxy_control.get("recommended_hold_min", hold_min), int | float)
                else hold_min,
            )
        raw_dose_factor = 0.10 + max(0.0, 0.38 - oxidant) * 0.75 + max(0.0, residual - 0.42) * 0.18
        dose_factor = round(self._clip(raw_dose_factor * (1.0 - 0.45 * max(0.0, byproduct - 0.45)), 0.06, 0.35), 2)
        regen_intensity = round(
            self._clip(
                0.34
                + max(0.0, 0.45 - catalyst) * 1.15
                + max(0.0, 0.68 - state.get("reaction_completion", 1.0)) * 0.34
                + (0.12 if catalyst_fault else 0.0),
                0.25,
                0.90,
            ),
            2,
        )
        downtime_min = int(round(25 + regen_intensity * 45 + max(0.0, residual - 0.45) * 20))
        replacement_downtime_min = int(round(70 + replacement_urgency * 45 + max(0.0, residual - 0.45) * 20))
        proxy_score_boost = (
            float(proxy_control.get("score_boost", 0.0))
            if isinstance(proxy_control, dict) and isinstance(proxy_control.get("score_boost", 0.0), int | float)
            else 0.0
        )
        switch_score = self._clip(matrix * 0.75 + (0.22 if "matrix_interference" in fault_ids and matrix >= 0.55 else 0.0) + proxy_score_boost)
        if matrix < 0.55:
            switch_score = min(switch_score, 0.32)
        if proxy_protective_mode:
            switch_score = max(switch_score, self._clip(0.88 + proxy_score_boost))
        release_possible = release >= 0.82 and residual <= 0.35 and hydraulic_confidence >= 0.7 and byproduct <= 0.65

        actions = [
            {
                "action_id": "hold_for_validation",
                "action_name": "暂存并旁路验证",
                "score": self._clip(
                    (0.82 - release) * 0.55
                    + (0.72 if "release_evidence_insufficient" in fault_ids else 0.0)
                    + (0.16 if cycle_window_fault and residual <= 0.45 else 0.0)
                    + (0.20 if "byproduct_or_overoxidation_risk" in fault_ids else 0.0)
                    + validation_urgency * 0.16
                ),
                "parameters": {
                    "hold_min": hold_min,
                    "validation_delay_min": validation_delay_min,
                    "validation": proxy_control.get("validation_targets", validation_plan.get("targets", ["COD/TOC、目标污染物、余氧化剂或副产物快检"]))
                    if isinstance(proxy_control, dict) and proxy_protective_mode
                    else validation_plan.get("targets", ["COD/TOC、目标污染物、余氧化剂或副产物快检"]),
                    "validation_plan": validation_plan.get("plan_name", "default_validation"),
                    "release_policy": proxy_control.get("release_policy")
                    if isinstance(proxy_control, dict) and proxy_protective_mode
                    else "standard_release_gate",
                },
                "requires_human_review": False,
                "evidence": {
                    "release_readiness": release,
                    "compliance_probability": compliance,
                    "byproduct_risk": byproduct,
                    "validation_urgency": validation_urgency,
                    "matrix_fast_proxy": proxy_metrics if proxy_protective_mode else {},
                    "fault_ids": sorted(fault_ids),
                },
            },
            {
                "action_id": "inspect_hydraulics",
                "action_name": "核查泵阀与回流管路",
                "score": 0.78 if "hydraulic_retention_anomaly" in fault_ids else 0.05,
                "parameters": {"check_items": ["pump", "valve", "recycle_line", "actual_flow"], "pause_release": True},
                "requires_human_review": True,
                "evidence": {"fault_ids": sorted(fault_ids)},
            },
            {
                "action_id": "calibrate_sensors",
                "action_name": "校准或降权异常传感器",
                "score": 0.72 if "sensor_data_unreliable" in fault_ids else 0.05,
                "parameters": {"channels": "use Agent 1 low-score channels", "apply_to_soft_sensor": True},
                "requires_human_review": True,
                "evidence": {"fault_ids": sorted(fault_ids)},
            },
            {
                "action_id": "recirculate",
                "action_name": "继续回流处理",
                "score": self._clip(
                    0.10
                    + recycle_gain * 1.7
                    + max(0.0, residual - 0.30) * 0.8
                    + (0.24 if cycle_window_fault else 0.0)
                    - cycle_id * 0.015
                ),
                "parameters": {"recycle_ratio": recycle_ratio, "extra_retention_min": extra_retention_min},
                "requires_human_review": False,
                "evidence": {"recycle_gain": recycle_gain, "pollutant_residual_risk": residual, "cycle_id": cycle_id, "fault_ids": sorted(fault_ids)},
            },
            {
                "action_id": "regenerate_catalyst",
                "action_name": "再生或更换催化剂",
                "score": self._clip(
                    (0.58 if catalyst_fault else 0.0)
                    + max(0.0, 0.45 - catalyst) * 1.25
                    + max(0.0, residual - 0.36) * 0.28
                    + max(0.0, oxidant - 0.45) * 0.12
                    + regeneration_potential * 0.16
                    + (0.12 if lifecycle_decision == "regenerate_catalyst" else 0.0)
                    - max(0.0, replacement_urgency - 0.55) * 0.42
                    - byproduct * 0.08
                ),
                "parameters": {"regen_intensity": regen_intensity, "downtime_min": downtime_min, "confirm_with": "催化剂活性、表面污染或压降快检"},
                "requires_human_review": True,
                "evidence": {
                    "catalyst_activity": catalyst,
                    "catalyst_lifetime_fraction": catalyst_lifetime,
                    "catalyst_regen_count": catalyst_regen_count,
                    "catalyst_regeneration_potential": regeneration_potential,
                    "catalyst_replacement_urgency": replacement_urgency,
                    "lifecycle_decision": lifecycle_decision,
                    "reaction_completion": state.get("reaction_completion", 1.0),
                    "pollutant_residual_risk": residual,
                    "oxidant_remaining": oxidant,
                    "fault_ids": sorted(fault_ids),
                },
            },
            {
                "action_id": "replace_catalyst",
                "action_name": "更换催化剂模块",
                "score": self._clip(
                    (0.62 if lifecycle_decision == "replace_catalyst" else 0.0)
                    + max(0.0, replacement_urgency - 0.48) * 1.20
                    + max(0.0, 0.30 - regeneration_potential) * 0.85
                    + min(catalyst_regen_count / 3.0, 1.0) * 0.16
                    + max(0.0, 0.36 - catalyst_lifetime) * 0.35
                ),
                "parameters": {
                    "downtime_min": replacement_downtime_min,
                    "commissioning_confidence": 0.84,
                    "confirm_with": "再生后活性恢复率、压降、表面污染和库存模块状态",
                },
                "requires_human_review": True,
                "evidence": {
                    "catalyst_activity": catalyst,
                    "catalyst_lifetime_fraction": catalyst_lifetime,
                    "catalyst_regen_count": catalyst_regen_count,
                    "catalyst_regeneration_potential": regeneration_potential,
                    "catalyst_replacement_urgency": replacement_urgency,
                    "lifecycle_decision": lifecycle_decision,
                    "pollutant_residual_risk": residual,
                    "fault_ids": sorted(fault_ids),
                },
            },
            {
                "action_id": "dose_oxidant",
                "action_name": "补加氧化剂",
                "score": self._clip(
                    (0.50 if oxidant < 0.35 else 0.0)
                    + max(0.0, 0.35 - oxidant) * 1.05
                    + max(0.0, residual - 0.35) * 0.25
                    + (0.25 if "oxidant_limitation" in fault_ids else 0.0)
                    - byproduct * 0.30
                ),
                "parameters": {"dose_factor": dose_factor, "confirm_with": "余氧化剂快检"},
                "requires_human_review": False,
                "evidence": {"oxidant_remaining": oxidant, "byproduct_risk": byproduct, "dose_factor": dose_factor, "fault_ids": sorted(fault_ids)},
            },
            {
                "action_id": "switch_or_pretreat",
                "action_name": "预处理或切换处理单元",
                "score": switch_score,
                "parameters": {
                    "candidate_units": ["coagulation", "adsorption", "membrane", "deep_oxidation"],
                    "protective_mode": proxy_protective_mode,
                    "release_policy": proxy_control.get("release_policy", "standard_release_gate") if isinstance(proxy_control, dict) else "standard_release_gate",
                    "latency_basis": proxy_control.get("latency_basis", {}) if isinstance(proxy_control, dict) else {},
                },
                "requires_human_review": True,
                "evidence": {
                    "matrix_interference": matrix,
                    "fault_ids": sorted(fault_ids),
                    "matrix_fast_proxy": proxy_metrics if proxy_protective_mode else {},
                    "fast_proxy_status": proxy_readiness.get("fast_proxy_status") if isinstance(proxy_readiness, dict) else None,
                },
            },
            {
                "action_id": "release",
                "action_name": "达标放行",
                "score": self._clip((0.58 + (release - 0.82) * 1.25) if release_possible else min(release - 0.75, 0.25)),
                "parameters": {"release_gate": "release_readiness >= 0.82 and residual <= 0.35 and hydraulic_confidence >= 0.7 and byproduct_risk <= 0.65"},
                "requires_human_review": False,
                "evidence": {"release_readiness": release, "compliance_probability": compliance, "pollutant_residual_risk": residual, "hydraulic_confidence": hydraulic_confidence, "byproduct_risk": byproduct},
            },
        ]
        self._apply_knowledge_action_biases(actions, knowledge_action_biases)
        for action in actions:
            action["score"] = round(float(action["score"]), 3)
            action["_sort_priority"] = 0.1 if proxy_protective_mode and action["action_id"] == "switch_or_pretreat" else 0.0
        actions.sort(key=lambda item: (item["score"], item["_sort_priority"]), reverse=True)
        for action in actions:
            action.pop("_sort_priority", None)
        return actions

    def _state(self) -> dict[str, float]:
        if self.soft_sensor_report is None:
            return {}
        state = self.soft_sensor_report.metrics.get("state_estimate", {})
        if not isinstance(state, dict):
            return {}
        return {str(k): float(v) for k, v in state.items() if isinstance(v, int | float)}

    def _faults(self) -> list[dict[str, object]]:
        if self.fault_report is None:
            return []
        faults = self.fault_report.metrics.get("ranked_faults", [])
        if not isinstance(faults, list):
            return []
        return [fault for fault in faults if isinstance(fault, dict)]

    def _knowledge_action_biases(self) -> dict[str, float]:
        kg_biases = self._kg_action_biases()
        if kg_biases:
            return kg_biases
        if self.fault_report is None:
            return {}
        matches = self.fault_report.metrics.get("knowledge_matches", [])
        if not isinstance(matches, list):
            return {}

        biases: dict[str, float] = {}
        for match in matches:
            if not isinstance(match, dict):
                continue
            match_score = float(match.get("match_score", 0.0))
            action_biases = match.get("action_biases", {})
            if not isinstance(action_biases, dict):
                continue
            for action_id, bias in action_biases.items():
                biases[str(action_id)] = biases.get(str(action_id), 0.0) + match_score * float(bias)
        return {action_id: round(self._clip(value, -0.22, 0.22), 3) for action_id, value in biases.items() if abs(value) >= 0.01}

    def _kg_action_biases(self) -> dict[str, float]:
        if self.fault_report is None:
            return {}
        kg_reasoning = self.fault_report.metrics.get("kg_reasoning", {})
        if not isinstance(kg_reasoning, dict):
            return {}
        patch = kg_reasoning.get("action_constraint_patch", [])
        if not isinstance(patch, list):
            return {}
        biases: dict[str, float] = {}
        for item in patch:
            if not isinstance(item, dict) or not item.get("action_id"):
                continue
            biases[str(item["action_id"])] = float(item.get("bias_score", 0.0))
        return {action_id: round(self._clip(value, -0.22, 0.22), 3) for action_id, value in biases.items() if abs(value) >= 0.01}

    def _knowledge_reasoning_source(self) -> str:
        if self._kg_action_biases():
            return "typed_kg_action_constraint_patch"
        if self.fault_report is not None and self.fault_report.metrics.get("knowledge_matches"):
            return "flat_knowledge_matches"
        return "no_knowledge_bias"

    def _catalyst_lifecycle(self) -> dict[str, object]:
        if self.catalyst_lifecycle_report is None:
            return {"decision_action_id": "monitor_catalyst"}
        decision = self.catalyst_lifecycle_report.metrics.get("maintenance_decision", {})
        lifecycle_state = self.catalyst_lifecycle_report.metrics.get("lifecycle_state", {})
        if not isinstance(decision, dict):
            decision = {}
        if not isinstance(lifecycle_state, dict):
            lifecycle_state = {}
        return {
            "decision_action_id": str(decision.get("action_id", "monitor_catalyst")),
            "decision_score": float(decision.get("score", 0.0)) if isinstance(decision.get("score", 0.0), int | float) else 0.0,
            "lifecycle_state": lifecycle_state,
        }

    def _validation_plan(self) -> dict[str, object]:
        if self.validation_planning_report is None:
            return {"plan_name": "default_validation", "urgency": 0.0}
        plan = self.validation_planning_report.metrics.get("validation_plan", {})
        return plan if isinstance(plan, dict) else {"plan_name": "default_validation", "urgency": 0.0}

    def _matrix_shock_fast_proxy(self) -> dict[str, object]:
        if self.matrix_shock_fast_proxy_report is None:
            return {}
        metrics = self.matrix_shock_fast_proxy_report.metrics
        return metrics if isinstance(metrics, dict) else {}

    def _apply_knowledge_action_biases(
        self,
        actions: list[dict[str, object]],
        knowledge_action_biases: dict[str, float],
    ) -> None:
        if not knowledge_action_biases:
            return
        for action in actions:
            action_id = str(action["action_id"])
            bias = knowledge_action_biases.get(action_id)
            if bias is None:
                continue
            action["score"] = self._clip(float(action["score"]) + bias)
            evidence = action.get("evidence", {})
            if isinstance(evidence, dict):
                evidence["knowledge_action_bias"] = bias
                action["evidence"] = evidence

    @staticmethod
    def _action_sentence(action: dict[str, object]) -> str:
        return f"{action['action_name']}：参数 {action['parameters']}；依据 {action['evidence']}。"

    @staticmethod
    def _summary(actions: list[dict[str, object]]) -> str:
        if not actions:
            return "暂无可执行控制动作。"
        top = actions[0]
        return f"首要控制动作：{top['action_name']}，评分 {top['score']}。"

    @staticmethod
    def _clip(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
        return max(lo, min(hi, value))
