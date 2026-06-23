from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class FaultDiagnosisAgent(BaseAgent):
    """Rank actionable fault modes from quality, soft-state, and mechanism reports."""

    name = "fault_diagnosis_agent"

    def __init__(
        self,
        *,
        data_quality_report: AgentReport | None = None,
        soft_sensor_report: AgentReport | None = None,
        mechanism_report: AgentReport | None = None,
    ) -> None:
        self.data_quality_report = data_quality_report
        self.soft_sensor_report = soft_sensor_report
        self.mechanism_report = mechanism_report

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        state = self._state()
        dq_types = self._issue_types(self.data_quality_report)
        mechanism_ids = self._mechanism_ids()
        knowledge_matches = self._knowledge_matches()
        kg_reasoning = self._kg_reasoning()
        fault_modes = self._rank_faults(state, dq_types, mechanism_ids, knowledge_matches)

        issues = [
            QualityIssue(
                sensor="fault",
                issue_type=fault["fault_id"],
                severity=Severity.CRITICAL if fault["risk_level"] == "high" else Severity.WARNING,
                message=fault["fault_name"],
                evidence=fault["evidence"],
            )
            for fault in fault_modes
            if fault["score"] >= 0.35
        ]
        recommendations = [fault["next_check"] for fault in fault_modes[:4] if fault["score"] >= 0.35]
        summary = self._summary(fault_modes)
        confidence = round(min(0.95, max(0.1, sum(f["score"] for f in fault_modes[:3]) / 3)), 3)

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations or ["故障证据不足，建议继续采集一个循环窗口。"],
            metrics={
                "ranked_faults": fault_modes,
                "state_used": state,
                "dq_issue_types": sorted(dq_types),
                "mechanism_ids": mechanism_ids,
                "knowledge_matches": knowledge_matches,
                "kg_reasoning": kg_reasoning,
            },
        )

    def _rank_faults(
        self,
        state: dict[str, float],
        dq_types: set[str],
        mechanism_ids: list[str],
        knowledge_matches: list[dict[str, object]],
    ) -> list[dict[str, object]]:
        residual = state.get("pollutant_residual_risk", 0.0)
        completion = state.get("reaction_completion", 1.0)
        oxidant = state.get("oxidant_remaining", 1.0)
        catalyst = state.get("catalyst_activity", 1.0)
        catalyst_lifetime = state.get("catalyst_lifetime_fraction", 1.0)
        catalyst_regen_count = state.get("catalyst_regen_count", 0.0)
        catalyst_replacement_urgency = state.get("catalyst_replacement_urgency", 0.0)
        matrix = state.get("matrix_interference", 0.0)
        byproduct = state.get("byproduct_risk", 0.0)
        sensor_conf = state.get("sensor_confidence", 1.0)
        hydraulic_confidence = state.get("hydraulic_confidence", 1.0)
        release = state.get("release_readiness", state.get("compliance_probability", 0.0))
        recycle = state.get("recycle_gain", 0.0)
        hydraulic_issue = bool({"sustained_shift", "low_flow_absolute"} & dq_types) or hydraulic_confidence < 0.7 or "hydraulic_anomaly" in mechanism_ids
        loop_buffer_needed = "loop_buffer_needed" in mechanism_ids or (residual > 0.32 and recycle >= 0.2 and oxidant >= 0.45 and release < 0.86)
        knowledge_support = self._knowledge_support_by_rule(knowledge_matches)

        faults = [
            {
                "fault_id": "sensor_data_unreliable",
                "fault_name": "传感数据不可靠",
                "score": self._clip(0.2 + (1.0 - sensor_conf) * 0.65 + 0.06 * len(dq_types)),
                "risk_level": "medium" if sensor_conf >= 0.55 else "high",
                "evidence": {"sensor_confidence": sensor_conf, "dq_issue_types": sorted(dq_types)},
                "next_check": "先做传感器校准/旁路快检；在校准前禁止自动放行。",
            },
            {
                "fault_id": "hydraulic_retention_anomaly",
                "fault_name": "水力停留时间或回流执行异常",
                "score": self._clip((0.72 if hydraulic_issue else 0.1) + 0.15 * recycle + max(0.0, 0.7 - hydraulic_confidence) * 0.2),
                "risk_level": "medium",
                "evidence": {
                    "sustained_shift": "sustained_shift" in dq_types,
                    "low_flow_absolute": "low_flow_absolute" in dq_types,
                    "hydraulic_confidence": hydraulic_confidence,
                    "mechanism_ids": mechanism_ids,
                    "recycle_gain": recycle,
                },
                "next_check": "核查泵、阀、回流管路和实际流量；必要时重新计算 HRT。",
            },
            {
                "fault_id": "cycle_window_insufficient",
                "fault_name": "循环缓冲或验证窗口不足",
                "score": self._clip(
                    (0.62 if loop_buffer_needed else 0.0)
                    + max(0.0, residual - 0.32) * 0.35
                    + recycle * 0.18
                    + max(0.0, 0.86 - release) * 0.12
                    + 0.08 * knowledge_support.get("loop_buffer_needed", 0.0)
                ),
                "risk_level": "medium",
                "evidence": {
                    "pollutant_residual_risk": residual,
                    "oxidant_remaining": oxidant,
                    "release_readiness": release,
                    "recycle_gain": recycle,
                    "mechanism_ids": mechanism_ids,
                    "knowledge_support": self._knowledge_evidence(knowledge_matches, "loop_buffer_needed"),
                },
                "next_check": "安排下一回流/停留窗口，并同步进行软传感复估与旁路快检，而不是立即放行。",
            },
            {
                "fault_id": "release_evidence_insufficient",
                "fault_name": "达标证据不足导致放行受阻",
                "score": self._clip((0.78 if "likely_treated_but_not_releasable" in mechanism_ids else 0.15) + (0.82 - release) * 0.2),
                "risk_level": "medium",
                "evidence": {"release_readiness": release, "mechanism_ids": mechanism_ids},
                "next_check": "维持暂存并进行快速离线验证；验证通过后再进入放行候选。",
            },
            {
                "fault_id": "matrix_interference",
                "fault_name": "基质干扰或新扰动进入系统",
                "score": self._clip(0.15 + matrix * 0.55 + (0.18 if "drift_suspected" in dq_types else 0.0) + 0.12 * knowledge_support.get("matrix_interference", 0.0)),
                "risk_level": "medium" if matrix < 0.7 else "high",
                "evidence": {"matrix_interference": matrix, "drift_suspected": "drift_suspected" in dq_types, "knowledge_support": self._knowledge_evidence(knowledge_matches, "matrix_interference")},
                "next_check": "检测盐度、COD/TOC、浊度来源；判断是否需要预处理或切换单元。",
            },
            {
                "fault_id": "byproduct_or_overoxidation_risk",
                "fault_name": "副产物或过氧化风险",
                "score": self._clip((0.55 if "byproduct_risk" in mechanism_ids else 0.0) + byproduct * 0.45 + max(0.0, oxidant - 0.65) * 0.18 + 0.12 * knowledge_support.get("byproduct_risk", 0.0)),
                "risk_level": "high" if byproduct >= 0.7 else "medium",
                "evidence": {"byproduct_risk": byproduct, "oxidant_remaining": oxidant, "matrix_interference": matrix, "mechanism_ids": mechanism_ids, "knowledge_support": self._knowledge_evidence(knowledge_matches, "byproduct_risk")},
                "next_check": "暂停追加氧化剂，检测余氧化剂和潜在副产物；必要时转入预处理或吸附抛光。",
            },
            {
                "fault_id": "oxidant_limitation",
                "fault_name": "氧化剂不足",
                "score": self._clip((0.45 if residual > 0.45 else 0.0) + max(0.0, 0.42 - oxidant) * 0.8 + 0.10 * knowledge_support.get("oxidant_limitation", 0.0)),
                "risk_level": "high" if residual > 0.65 and oxidant < 0.3 else "medium",
                "evidence": {"pollutant_residual_risk": residual, "oxidant_remaining": oxidant, "knowledge_support": self._knowledge_evidence(knowledge_matches, "oxidant_limitation")},
                "next_check": "做余氧化剂快检；若确认不足，再进入补加药剂策略。",
            },
            {
                "fault_id": "catalyst_deactivation",
                "fault_name": "催化剂失活或活性位受污染",
                "score": self._clip((0.32 if completion < 0.65 and catalyst < 0.46 else 0.0) + max(0.0, 0.48 - catalyst) * 1.15 + 0.14 * knowledge_support.get("catalyst_deactivation", 0.0)),
                "risk_level": "medium",
                "evidence": {
                    "reaction_completion": completion,
                    "catalyst_activity": catalyst,
                    "catalyst_lifetime_fraction": catalyst_lifetime,
                    "catalyst_regen_count": catalyst_regen_count,
                    "knowledge_support": self._knowledge_evidence(knowledge_matches, "catalyst_deactivation"),
                },
                "next_check": "检查催化剂循环前后活性，必要时进行再生或替换对照实验。",
            },
            {
                "fault_id": "catalyst_lifecycle_exhaustion",
                "fault_name": "催化剂再生收益衰减或寿命接近耗尽",
                "score": self._clip(
                    catalyst_replacement_urgency * 0.72
                    + max(0.0, 0.45 - catalyst_lifetime) * 0.35
                    + min(catalyst_regen_count / 3.0, 1.0) * 0.20
                ),
                "risk_level": "high" if catalyst_replacement_urgency >= 0.75 else "medium",
                "evidence": {
                    "catalyst_replacement_urgency": catalyst_replacement_urgency,
                    "catalyst_lifetime_fraction": catalyst_lifetime,
                    "catalyst_regen_count": catalyst_regen_count,
                    "catalyst_activity": catalyst,
                },
                "next_check": "比较催化剂再生、补充新材料和整体更换的长期成本，并记录再生后活性恢复率。",
            },
            {
                "fault_id": "reaction_time_insufficient",
                "fault_name": "反应时间不足",
                "score": self._clip(
                    (0.5 if residual > 0.45 and oxidant >= 0.45 and catalyst >= 0.45 else 0.0)
                    + (0.24 if loop_buffer_needed and catalyst >= 0.46 else 0.0)
                    + recycle * 0.2
                    + 0.08 * knowledge_support.get("reaction_time_insufficient", 0.0)
                ),
                "risk_level": "medium",
                "evidence": {"pollutant_residual_risk": residual, "oxidant_remaining": oxidant, "catalyst_activity": catalyst, "recycle_gain": recycle, "knowledge_support": self._knowledge_evidence(knowledge_matches, "reaction_time_insufficient")},
                "next_check": "优先延长停留或增加回流窗口，而不是立即加药。",
            },
        ]
        for fault in faults:
            fault["score"] = round(float(fault["score"]), 3)
        faults.sort(key=lambda item: item["score"], reverse=True)
        return faults

    def _state(self) -> dict[str, float]:
        if self.soft_sensor_report is None:
            return {}
        state = self.soft_sensor_report.metrics.get("state_estimate", {})
        if not isinstance(state, dict):
            return {}
        return {str(k): float(v) for k, v in state.items() if isinstance(v, int | float)}

    @staticmethod
    def _issue_types(report: AgentReport | None) -> set[str]:
        if report is None:
            return set()
        return {issue.issue_type for issue in report.issues}

    def _mechanism_ids(self) -> list[str]:
        if self.mechanism_report is None:
            return []
        hypotheses = self.mechanism_report.metrics.get("ranked_hypotheses", [])
        if not isinstance(hypotheses, list):
            return []
        return [str(item["rule_id"]) for item in hypotheses if isinstance(item, dict) and "rule_id" in item]

    def _knowledge_matches(self) -> list[dict[str, object]]:
        if self.mechanism_report is None:
            return []
        matches = self.mechanism_report.metrics.get("knowledge_matches", [])
        if not isinstance(matches, list):
            return []
        return [match for match in matches if isinstance(match, dict)]

    def _kg_reasoning(self) -> dict[str, object]:
        if self.mechanism_report is None:
            return {}
        reasoning = self.mechanism_report.metrics.get("kg_reasoning", {})
        return reasoning if isinstance(reasoning, dict) else {}

    @staticmethod
    def _knowledge_support_by_rule(knowledge_matches: list[dict[str, object]]) -> dict[str, float]:
        support: dict[str, float] = {}
        for match in knowledge_matches:
            score = float(match.get("match_score", 0.0))
            for rule_id in match.get("supports_rules", []):
                support[str(rule_id)] = max(support.get(str(rule_id), 0.0), score)
        return support

    @staticmethod
    def _knowledge_evidence(knowledge_matches: list[dict[str, object]], rule_id: str) -> list[dict[str, object]]:
        evidence: list[dict[str, object]] = []
        for match in knowledge_matches:
            if rule_id not in [str(item) for item in match.get("supports_rules", [])]:
                continue
            evidence.append(
                {
                    "entry_id": match.get("entry_id"),
                    "match_score": match.get("match_score"),
                    "pollutant_class": match.get("pollutant_class"),
                    "material_family": match.get("material_family"),
                }
            )
        return evidence[:3]

    @staticmethod
    def _summary(fault_modes: list[dict[str, object]]) -> str:
        if not fault_modes:
            return "未形成故障诊断结果。"
        top = fault_modes[0]
        return f"首要故障模式：{top['fault_name']}，评分 {top['score']}。"

    @staticmethod
    def _clip(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
        return max(lo, min(hi, value))
