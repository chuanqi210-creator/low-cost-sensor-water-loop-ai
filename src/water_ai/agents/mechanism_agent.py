from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity
from water_ai.knowledge import MECHANISM_RULES, query_knowledge_base, reason_over_knowledge_graph


class MechanismAgent(BaseAgent):
    """Explain likely process mechanisms with evidence from upstream agents."""

    name = "mechanism_agent"

    def __init__(
        self,
        *,
        data_quality_report: AgentReport | None = None,
        soft_sensor_report: AgentReport | None = None,
    ) -> None:
        self.data_quality_report = data_quality_report
        self.soft_sensor_report = soft_sensor_report

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        state = self._state()
        dq_issue_types = self._issue_types(self.data_quality_report)
        soft_issue_types = self._issue_types(self.soft_sensor_report)
        knowledge_matches = query_knowledge_base(state, dq_issue_types=dq_issue_types, soft_issue_types=soft_issue_types)
        kg_reasoning = reason_over_knowledge_graph(state, dq_issue_types=dq_issue_types, soft_issue_types=soft_issue_types)
        hypotheses = self._build_hypotheses(state, dq_issue_types, soft_issue_types)
        hypotheses = self._apply_knowledge_support(hypotheses, knowledge_matches, kg_reasoning)

        issues = [
            QualityIssue(
                sensor="mechanism",
                issue_type=h["rule_id"],
                severity=Severity.WARNING if h["score"] >= 0.55 else Severity.INFO,
                message=h["mechanism"],
                evidence=h["evidence"],
            )
            for h in hypotheses
            if h["score"] >= 0.35
        ]
        recommendations = [h["action_hint"] for h in hypotheses[:3] if h["score"] >= 0.35]
        confidence = round(min(0.95, max(0.1, sum(h["score"] for h in hypotheses[:3]) / 3)), 3)
        summary = self._summary(hypotheses)

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations or ["未形成强机理假设，建议补充实验或离线检测。"],
            metrics={
                "ranked_hypotheses": hypotheses,
                "state_used": state,
                "dq_issue_types": sorted(dq_issue_types),
                "soft_issue_types": sorted(soft_issue_types),
                "knowledge_matches": knowledge_matches,
                "kg_reasoning": kg_reasoning,
            },
        )

    def _build_hypotheses(
        self,
        state: dict[str, float],
        dq_issue_types: set[str],
        soft_issue_types: set[str],
    ) -> list[dict[str, object]]:
        hypotheses: list[dict[str, object]] = []

        def add(rule_id: str, score: float, evidence: dict[str, object]) -> None:
            rule = MECHANISM_RULES[rule_id]
            hypotheses.append(
                {
                    "rule_id": rule_id,
                    "mechanism": rule.mechanism,
                    "score": round(max(0.0, min(1.0, score)), 3),
                    "explanation": rule.explanation,
                    "action_hint": rule.action_hint,
                    "evidence": evidence,
                }
            )

        sensor_conf = state.get("sensor_confidence", 1.0)
        compliance = state.get("compliance_probability", 0.0)
        release = state.get("release_readiness", compliance)
        residual = state.get("pollutant_residual_risk", 0.0)
        completion = state.get("reaction_completion", 0.0)
        oxidant = state.get("oxidant_remaining", 0.0)
        catalyst = state.get("catalyst_activity", 1.0)
        matrix = state.get("matrix_interference", 0.0)
        byproduct = state.get("byproduct_risk", 0.0)
        recycle = state.get("recycle_gain", 0.0)
        hydraulic_confidence = state.get("hydraulic_confidence", 1.0)

        if sensor_conf < 0.82 or {"missing", "spike", "flatline", "drift_suspected"} & dq_issue_types:
            add(
                "sensor_uncertainty",
                0.35 + (1.0 - sensor_conf) * 0.55 + 0.05 * len({"missing", "spike", "flatline", "drift_suspected"} & dq_issue_types),
                {"sensor_confidence": sensor_conf, "dq_issue_types": sorted(dq_issue_types)},
            )

        if {"sustained_shift", "low_flow_absolute"} & dq_issue_types or hydraulic_confidence < 0.7:
            add(
                "hydraulic_anomaly",
                0.45 + (0.25 if {"sustained_shift", "low_flow_absolute"} & dq_issue_types else 0.0) + max(0.0, 0.7 - hydraulic_confidence) * 0.45,
                {"dq_issue_types": sorted(dq_issue_types), "hydraulic_confidence": hydraulic_confidence, "recycle_gain": recycle},
            )

        if matrix > 0.55 or {"drift_suspected", "flatline"} & dq_issue_types:
            add(
                "matrix_interference",
                0.25 + matrix * 0.55 + (0.15 if "drift_suspected" in dq_issue_types else 0.0),
                {"matrix_interference": matrix, "dq_issue_types": sorted(dq_issue_types)},
            )

        if residual > 0.45 and oxidant < 0.35:
            add(
                "oxidant_limitation",
                0.45 + residual * 0.35 + (0.35 - oxidant) * 0.3,
                {"pollutant_residual_risk": residual, "oxidant_remaining": oxidant},
            )

        if byproduct > 0.55 or (oxidant > 0.72 and matrix > 0.55):
            add(
                "byproduct_risk",
                0.35 + byproduct * 0.45 + max(0.0, oxidant - 0.62) * 0.18 + max(0.0, matrix - 0.45) * 0.18,
                {"byproduct_risk": byproduct, "oxidant_remaining": oxidant, "matrix_interference": matrix, "cycle_id": state.get("cycle_id", 0.0)},
            )

        if completion < 0.62 and catalyst < 0.45:
            add(
                "catalyst_deactivation",
                0.35 + (0.62 - completion) * 0.35 + (0.45 - catalyst) * 0.85,
                {"reaction_completion": completion, "catalyst_activity": catalyst},
            )

        if residual > 0.45 and oxidant >= 0.45 and catalyst >= 0.45:
            add(
                "reaction_time_insufficient",
                0.45 + residual * 0.25 + recycle * 0.25,
                {"pollutant_residual_risk": residual, "oxidant_remaining": oxidant, "catalyst_activity": catalyst, "recycle_gain": recycle},
            )

        if residual > 0.32 and recycle >= 0.20 and oxidant >= 0.45 and release < 0.86:
            add(
                "loop_buffer_needed",
                0.38 + residual * 0.22 + recycle * 0.35 + max(0.0, 0.86 - release) * 0.25,
                {
                    "pollutant_residual_risk": residual,
                    "oxidant_remaining": oxidant,
                    "release_readiness": release,
                    "recycle_gain": recycle,
                    "cycle_id": state.get("cycle_id", 0.0),
                },
            )

        if compliance >= 0.82 and release < 0.82:
            add(
                "likely_treated_but_not_releasable",
                0.7 + (compliance - release) * 0.2,
                {"compliance_probability": compliance, "release_readiness": release, "soft_issue_types": sorted(soft_issue_types)},
            )

        hypotheses.sort(key=lambda item: item["score"], reverse=True)
        return hypotheses

    def _apply_knowledge_support(
        self,
        hypotheses: list[dict[str, object]],
        knowledge_matches: list[dict[str, object]],
        kg_reasoning: dict[str, object] | None = None,
    ) -> list[dict[str, object]]:
        by_rule: dict[str, list[dict[str, object]]] = {}
        for match in knowledge_matches:
            for rule_id in match.get("supports_rules", []):
                by_rule.setdefault(str(rule_id), []).append(match)
        kg_reasoning = kg_reasoning or {}
        kg_paths = kg_reasoning.get("evidence_paths", [])
        paths_by_rule: dict[str, list[dict[str, object]]] = {}
        if isinstance(kg_paths, list):
            for path in kg_paths:
                if isinstance(path, dict) and path.get("rule_id"):
                    paths_by_rule.setdefault(str(path["rule_id"]), []).append(path)

        existing_rules = {str(item["rule_id"]) for item in hypotheses}
        for hypothesis in hypotheses:
            rule_id = str(hypothesis["rule_id"])
            support = by_rule.get(rule_id, [])
            if not support:
                continue
            top_support = support[:3]
            boost = min(0.10, 0.08 * max(float(item["match_score"]) for item in top_support))
            hypothesis["score"] = round(min(1.0, float(hypothesis["score"]) + boost), 3)
            evidence = hypothesis.get("evidence", {})
            if isinstance(evidence, dict):
                evidence["knowledge_support"] = [
                    {
                        "entry_id": item["entry_id"],
                        "match_score": item["match_score"],
                        "pollutant_class": item["pollutant_class"],
                        "material_family": item["material_family"],
                        "mechanism_tags": item["mechanism_tags"],
                    }
                    for item in top_support
                ]
                evidence["kg_evidence_paths"] = [
                    {
                        "path_id": path["path_id"],
                        "entry_id": path["entry_id"],
                        "match_score": path["match_score"],
                        "evidence_stage": path["evidence_stage"],
                        "claim_boundary": path["claim_boundary"],
                    }
                    for path in paths_by_rule.get(rule_id, [])[:3]
                ]
                hypothesis["evidence"] = evidence

        for match in knowledge_matches:
            if float(match["match_score"]) < 0.70:
                continue
            for rule_id in match.get("supports_rules", []):
                rule_id = str(rule_id)
                if rule_id in existing_rules or rule_id not in MECHANISM_RULES:
                    continue
                rule = MECHANISM_RULES[rule_id]
                hypotheses.append(
                    {
                        "rule_id": rule_id,
                        "mechanism": rule.mechanism,
                        "score": round(min(0.72, 0.34 + 0.36 * float(match["match_score"])), 3),
                        "explanation": f"{rule.explanation} 知识库补充：{match['explanation']}",
                        "action_hint": match["action_hint"],
                        "evidence": {
                            "knowledge_support": [
                                {
                                    "entry_id": match["entry_id"],
                                    "match_score": match["match_score"],
                                    "pollutant_class": match["pollutant_class"],
                                    "material_family": match["material_family"],
                                    "mechanism_tags": match["mechanism_tags"],
                                }
                            ],
                            "signal_hits": match["signal_hits"],
                            "dq_issue_hits": match["dq_issue_hits"],
                            "soft_issue_hits": match["soft_issue_hits"],
                            "kg_evidence_paths": [
                                {
                                    "path_id": path["path_id"],
                                    "entry_id": path["entry_id"],
                                    "match_score": path["match_score"],
                                    "evidence_stage": path["evidence_stage"],
                                    "claim_boundary": path["claim_boundary"],
                                }
                                for path in paths_by_rule.get(rule_id, [])[:3]
                            ],
                        },
                    }
                )
                existing_rules.add(rule_id)

        hypotheses.sort(key=lambda item: item["score"], reverse=True)
        return hypotheses

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

    @staticmethod
    def _summary(hypotheses: list[dict[str, object]]) -> str:
        if not hypotheses:
            return "未形成明确机理解释。"
        top = hypotheses[0]
        return f"首要机理假设：{top['mechanism']}，评分 {top['score']}。"
