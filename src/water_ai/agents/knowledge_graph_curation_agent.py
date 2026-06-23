from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity
from water_ai.knowledge import KNOWLEDGE_BASE, KnowledgeEntry


class KnowledgeGraphCurationAgent(BaseAgent):
    """Curate the literature-informed knowledge base into an auditable scientific KG."""

    name = "knowledge_graph_curation_agent"

    REQUIRED_AXES: dict[str, tuple[str, ...]] = {
        "pollutant_axes": ("PPCPs/微污染物", "染料", "PFAS", "抗生素", "农药", "重金属", "有机氯/卤代有机物"),
        "water_matrix_axes": ("COD/有机负荷", "盐度/电导", "pH", "浊度/颗粒物", "天然有机质", "共存离子/络合物"),
        "material_axes": ("催化剂", "吸附/离子交换", "膜分离", "AOP/强氧化", "光催化", "电催化", "生物处理耦合"),
        "process_axes": ("停留时间/回流", "剂量/氧化剂", "光照/电流", "pH 调节", "温度", "流量/水力", "再生周期"),
        "observable_signal_axes": ("pH", "ORP", "电导", "浊度", "UV254", "流量", "温度"),
        "hidden_state_axes": ("残留污染物风险", "反应完成度", "副产物风险", "催化剂活性", "基质抑制"),
        "evidence_axes": ("文献支持", "仿真支持", "真实数据支持", "仅假设"),
    }

    RAW_SENSOR_SIGNALS = {"pH", "ORP_mV", "EC_uScm", "turbidity_NTU", "UV254_abs", "flow_Lmin", "temp_C"}

    def __init__(self, *, entries: Sequence[KnowledgeEntry] | None = None) -> None:
        self.entries = list(entries or KNOWLEDGE_BASE)

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        graph_records = [self._record_for_entry(entry) for entry in self.entries]
        axis_coverage = self._axis_coverage(graph_records)
        evidence_audit = self._evidence_audit(graph_records)
        scientific_review_chain = self._scientific_review_chain()
        upgrade_backlog = self._upgrade_backlog(axis_coverage, evidence_audit)
        readiness = self._readiness(axis_coverage, evidence_audit, graph_records)
        issues = self._issues(axis_coverage, evidence_audit, graph_records)
        recommendations = self._recommendations(upgrade_backlog)
        summary = (
            f"知识图谱策展：{readiness['kg_curation_status']}；"
            f"轴覆盖 {readiness['axis_coverage_score']:.3f}，"
            f"field-supported edges {evidence_audit['field_supported_entry_count']} 条。"
        )
        confidence = round(min(0.88, max(0.28, 0.44 + 0.34 * readiness["kg_curation_score"] - 0.035 * len(issues))), 3)

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "graph_records": graph_records,
                "axis_coverage": axis_coverage,
                "evidence_audit": evidence_audit,
                "scientific_review_chain": scientific_review_chain,
                "kg_upgrade_backlog": upgrade_backlog,
                "readiness": readiness,
            },
        )

    def _record_for_entry(self, entry: KnowledgeEntry) -> dict[str, object]:
        text = " ".join(
            [
                entry.pollutant_class,
                entry.material_family,
                entry.explanation,
                entry.action_hint,
                " ".join(entry.mechanism_tags),
                " ".join(entry.source_basis),
            ]
        )
        condition_signals = tuple(condition.signal for condition in entry.signal_conditions)
        return {
            "entry_id": entry.entry_id,
            "pollutant_class": entry.pollutant_class,
            "material_family": entry.material_family,
            "pollutant_axes": self._pollutant_axes(text),
            "water_matrix_axes": self._water_matrix_axes(text, condition_signals),
            "material_axes": self._material_axes(text),
            "process_axes": self._process_axes(text, condition_signals),
            "observable_signal_axes": self._observable_signal_axes(text),
            "hidden_state_axes": self._hidden_state_axes(text, condition_signals),
            "mechanism_tags": list(entry.mechanism_tags),
            "condition_signals": list(condition_signals),
            "raw_sensor_condition_signals": sorted(set(condition_signals) & self.RAW_SENSOR_SIGNALS),
            "supports_rules": list(entry.supports_rules),
            "action_biases": entry.action_biases,
            "evidence_stage": entry.evidence_stage,
            "evidence_axes": self._evidence_axes(entry),
            "field_validation_need": list(entry.field_validation_need),
            "source_basis": list(entry.source_basis),
            "claim_boundary": self._claim_boundary(entry),
        }

    @classmethod
    def _axis_coverage(cls, records: list[dict[str, object]]) -> dict[str, object]:
        coverage: dict[str, object] = {}
        for axis_name, required in cls.REQUIRED_AXES.items():
            covered = sorted(
                {
                    str(value)
                    for record in records
                    for value in cls._as_list(record.get(axis_name, []))
                    if value in required
                }
            )
            missing = [axis for axis in required if axis not in covered]
            coverage[axis_name] = {
                "required": list(required),
                "covered": covered,
                "missing": missing,
                "coverage": round(len(covered) / max(1, len(required)), 3),
            }
        return coverage

    @staticmethod
    def _evidence_audit(records: list[dict[str, object]]) -> dict[str, object]:
        evidence_counts = {"文献支持": 0, "仿真支持": 0, "真实数据支持": 0, "仅假设": 0}
        source_basis_counts: dict[str, int] = {}
        field_need_counts: dict[str, int] = {}
        for record in records:
            for axis in KnowledgeGraphCurationAgent._as_list(record.get("evidence_axes", [])):
                evidence_counts[str(axis)] = evidence_counts.get(str(axis), 0) + 1
            for source in KnowledgeGraphCurationAgent._as_list(record.get("source_basis", [])):
                source_basis_counts[str(source)] = source_basis_counts.get(str(source), 0) + 1
            for need in KnowledgeGraphCurationAgent._as_list(record.get("field_validation_need", [])):
                field_need_counts[str(need)] = field_need_counts.get(str(need), 0) + 1
        return {
            "entry_count": len(records),
            "evidence_counts": evidence_counts,
            "field_supported_entry_count": evidence_counts.get("真实数据支持", 0),
            "literature_supported_entry_count": evidence_counts.get("文献支持", 0),
            "simulation_supported_entry_count": evidence_counts.get("仿真支持", 0),
            "source_basis_counts": source_basis_counts,
            "field_validation_need_counts": field_need_counts,
        }

    @staticmethod
    def _scientific_review_chain() -> list[dict[str, object]]:
        return [
            {
                "agent": "LiteratureEvidenceAgent",
                "role": "系统检索和抽取水处理、环境材料、软传感、灰箱控制文献。",
                "borrowed_skill_pattern": "systematic_literature_review",
                "output_contract": ["claim", "method", "parameter_range", "limitation", "evidence_stage", "citation_key"],
            },
            {
                "agent": "KnowledgeGraphCurationAgent",
                "role": "把文献和仿真证据转成污染物-基质-材料-过程-信号-状态-动作图谱。",
                "borrowed_skill_pattern": "scientific_knowledge_graph",
                "output_contract": ["typed_edge", "mechanism_tag", "action_constraint", "field_validation_need"],
            },
            {
                "agent": "MechanismBorrowingAgent",
                "role": "从已有研究迁移动力学、传质、催化衰减、软传感和控制约束。",
                "borrowed_skill_pattern": "academic_research_agent",
                "output_contract": ["borrowed_mechanism", "mapped_project_state", "assumption", "failure_boundary"],
            },
            {
                "agent": "UncertaintyValidationAgent",
                "role": "审查预测区间、校准曲线、bootstrap/conformal uncertainty 和 OOD 风险。",
                "borrowed_skill_pattern": "model_validation_and_uncertainty",
                "output_contract": ["coverage", "calibration_error", "ood_flag", "release_gate_adjustment"],
            },
            {
                "agent": "FieldRealismAgent",
                "role": "检查现场采样频率、低成本传感漂移、PLC/SCADA 延迟、人工复核和成本边界。",
                "borrowed_skill_pattern": "claim_verification_and_human_gates",
                "output_contract": ["field_gate", "operator_action", "latency_budget", "cannot_claim_until"],
            },
        ]

    @staticmethod
    def _upgrade_backlog(axis_coverage: dict[str, object], evidence_audit: dict[str, object]) -> list[dict[str, object]]:
        pollutant_missing = KnowledgeGraphCurationAgent._coverage_missing(axis_coverage, "pollutant_axes")
        process_missing = KnowledgeGraphCurationAgent._coverage_missing(axis_coverage, "process_axes")
        signal_missing = KnowledgeGraphCurationAgent._coverage_missing(axis_coverage, "observable_signal_axes")
        backlog: list[dict[str, object]] = [
            {
                "priority": "P0",
                "work_id": "field_supported_kg_edges",
                "title": "为每条高风险知识边补真实 field 或离线标签验证",
                "why": "当前知识图谱没有真实数据支持边，不能把文献/仿真边当现场结论。",
                "needed_fields": ["batch_id", "offline_target_concentration", "raw_sensor_trace", "action_taken", "post_action_outcome"],
            },
            {
                "priority": "P1",
                "work_id": "literature_evidence_extraction_schema",
                "title": "按系统综述格式抽取污染物、基质、材料、机制、参数范围和限制",
                "why": "知识库应成为可追溯证据矩阵，而不是不可审计的经验条目。",
                "needed_fields": ["citation_key", "study_type", "water_matrix", "material_system", "rate_or_capacity_range", "reported_limitation"],
            },
            {
                "priority": "P1",
                "work_id": "raw_signal_to_hidden_state_edges",
                "title": "补低成本原始信号到隐藏状态的证据边",
                "why": "当前多数字段从隐藏状态触发知识条目，仍需要 pH/ORP/EC/UV254 等原始信号到机制的可审查映射。",
                "needed_fields": ["sensor_name", "feature_window", "transformation", "target_hidden_state", "calibration_dataset"],
            },
        ]
        if pollutant_missing:
            backlog.append(
                {
                    "priority": "P2",
                    "work_id": "pollutant_axis_expansion",
                    "title": f"补齐污染物轴：{', '.join(pollutant_missing)}",
                    "why": "真实污染场景需要覆盖 PPCPs、染料、抗生素、农药和有机氯等不同处理机制。",
                    "needed_fields": ["pollutant_axis", "representative_compound", "treatability_assumption", "required_lab_label"],
                }
            )
        if process_missing:
            backlog.append(
                {
                    "priority": "P2",
                    "work_id": "process_condition_axis_expansion",
                    "title": f"补齐过程条件轴：{', '.join(process_missing)}",
                    "why": "动力学和控制不能只靠笼统回流，需要剂量、pH、温度、光照/电流、再生周期等可校准参数。",
                    "needed_fields": ["condition_axis", "parameter_name", "literature_range", "field_calibration_method"],
                }
            )
        if signal_missing:
            backlog.append(
                {
                    "priority": "P2",
                    "work_id": "observable_signal_axis_expansion",
                    "title": f"补齐低成本信号轴：{', '.join(signal_missing)}",
                    "why": "软传感灰箱必须说明每个低成本信号怎样约束隐藏状态和控制动作。",
                    "needed_fields": ["signal_axis", "sensor_cost", "noise_model", "sampling_interval", "failure_mode"],
                }
            )
        if int(evidence_audit["field_supported_entry_count"]) == 0:
            backlog.append(
                {
                    "priority": "P0",
                    "work_id": "claim_boundary_enforcement",
                    "title": "所有图谱结论强制标注 simulation/literature/field 边界",
                    "why": "防止 synthetic/sample 数据被误说成实证结论。",
                    "needed_fields": ["evidence_stage", "claim_allowed", "claim_blocked_until"],
                }
            )
        return backlog

    @staticmethod
    def _readiness(
        axis_coverage: dict[str, object],
        evidence_audit: dict[str, object],
        records: list[dict[str, object]],
    ) -> dict[str, object]:
        axis_scores = [float(value["coverage"]) for value in axis_coverage.values() if isinstance(value, dict)]
        axis_coverage_score = round(sum(axis_scores) / max(1, len(axis_scores)), 3)
        raw_signal_edges = sum(len(KnowledgeGraphCurationAgent._as_list(record.get("raw_sensor_condition_signals", []))) for record in records)
        raw_signal_grounding_score = min(1.0, raw_signal_edges / max(1, len(records)))
        field_ratio = int(evidence_audit["field_supported_entry_count"]) / max(1, int(evidence_audit["entry_count"]))
        evidence_score = round(
            0.55 * min(1.0, int(evidence_audit["literature_supported_entry_count"]) / max(1, int(evidence_audit["entry_count"])))
            + 0.25 * min(1.0, int(evidence_audit["simulation_supported_entry_count"]) / max(1, int(evidence_audit["entry_count"])))
            + 0.20 * field_ratio,
            3,
        )
        score = round(0.58 * axis_coverage_score + 0.27 * evidence_score + 0.15 * raw_signal_grounding_score, 3)
        if field_ratio == 0:
            status = "scientific_kg_seed_needs_literature_and_field_evidence"
        elif score < 0.78:
            status = "scientific_kg_needs_axis_expansion"
        else:
            status = "scientific_kg_ready_for_model_coupling"
        return {
            "kg_curation_status": status,
            "kg_curation_score": score,
            "axis_coverage_score": axis_coverage_score,
            "evidence_score": evidence_score,
            "raw_signal_grounding_score": round(raw_signal_grounding_score, 3),
            "entry_count": len(records),
        }

    @staticmethod
    def _issues(
        axis_coverage: dict[str, object],
        evidence_audit: dict[str, object],
        records: list[dict[str, object]],
    ) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        if int(evidence_audit["field_supported_entry_count"]) == 0:
            issues.append(
                QualityIssue(
                    sensor="knowledge_graph",
                    issue_type="no_field_supported_knowledge_edges",
                    severity=Severity.WARNING,
                    message="当前知识图谱没有真实数据支持边，只能作为文献/仿真 seed，不能宣称现场验证成立。",
                    evidence=evidence_audit,
                )
            )
        pollutant_missing = KnowledgeGraphCurationAgent._coverage_missing(axis_coverage, "pollutant_axes")
        if pollutant_missing:
            issues.append(
                QualityIssue(
                    sensor="knowledge_graph",
                    issue_type="pollutant_axis_undercoverage",
                    severity=Severity.INFO,
                    message=f"污染物轴仍缺：{', '.join(pollutant_missing)}。",
                    evidence={"missing": pollutant_missing},
                )
            )
        raw_signal_edges = [
            signal
            for record in records
            for signal in KnowledgeGraphCurationAgent._as_list(record.get("raw_sensor_condition_signals", []))
        ]
        if len(raw_signal_edges) < 3:
            issues.append(
                QualityIssue(
                    sensor="knowledge_graph",
                    issue_type="raw_signal_grounding_weak",
                    severity=Severity.WARNING,
                    message="知识条目主要由隐藏状态触发，低成本原始信号到机制/状态的证据边仍偏弱。",
                    evidence={"raw_signal_condition_edge_count": len(raw_signal_edges)},
                )
            )
        return issues

    @staticmethod
    def _recommendations(backlog: list[dict[str, object]]) -> list[str]:
        return [f"{item['priority']} {item['title']}" for item in backlog[:5]]

    @staticmethod
    def _pollutant_axes(text: str) -> list[str]:
        axes: set[str] = set()
        if any(token in text for token in ("微污染", "低浓度", "慢检测", "PPCP")):
            axes.add("PPCPs/微污染物")
        if "染料" in text:
            axes.add("染料")
        if "PFAS" in text or "氟代" in text:
            axes.add("PFAS")
        if "抗生素" in text:
            axes.add("抗生素")
        if "农药" in text:
            axes.add("农药")
        if "重金属" in text or "金属" in text:
            axes.add("重金属")
        if "卤代" in text or "有机氯" in text:
            axes.add("有机氯/卤代有机物")
        return sorted(axes)

    @staticmethod
    def _water_matrix_axes(text: str, condition_signals: tuple[str, ...]) -> list[str]:
        axes: set[str] = set()
        if any(token in text for token in ("COD", "有机负荷", "需氧量", "electron_demand")):
            axes.add("COD/有机负荷")
        if any(token in text for token in ("盐", "电导", "EC")) or "matrix_interference" in condition_signals:
            axes.add("盐度/电导")
        if "pH" in text:
            axes.add("pH")
        if any(token in text for token in ("浊度", "颗粒")):
            axes.add("浊度/颗粒物")
        if "天然有机质" in text:
            axes.add("天然有机质")
        if any(token in text for token in ("共存离子", "络合", "高盐", "金属")):
            axes.add("共存离子/络合物")
        return sorted(axes)

    @staticmethod
    def _material_axes(text: str) -> list[str]:
        axes: set[str] = set()
        if "催化" in text or "类芬顿" in text:
            axes.add("催化剂")
        if "吸附" in text or "离子交换" in text:
            axes.add("吸附/离子交换")
        if "膜" in text:
            axes.add("膜分离")
        if "高级氧化" in text or "强氧化" in text or "氧化剂" in text:
            axes.add("AOP/强氧化")
        if "光催化" in text:
            axes.add("光催化")
        if "电催化" in text:
            axes.add("电催化")
        if "生物" in text:
            axes.add("生物处理耦合")
        return sorted(axes)

    @staticmethod
    def _process_axes(text: str, condition_signals: tuple[str, ...]) -> list[str]:
        axes: set[str] = set()
        if any(token in text for token in ("停留", "回流", "循环", "reaction_time", "retention")):
            axes.add("停留时间/回流")
        if any(token in text for token in ("投加", "剂量", "氧化剂", "dose")) or "oxidant_remaining" in condition_signals:
            axes.add("剂量/氧化剂")
        if "光" in text or "电" in text:
            axes.add("光照/电流")
        if "pH" in text:
            axes.add("pH 调节")
        if "温度" in text or "temp" in text:
            axes.add("温度")
        if "水力" in text or "流量" in text:
            axes.add("流量/水力")
        if "再生" in text or "寿命" in text:
            axes.add("再生周期")
        return sorted(axes)

    @staticmethod
    def _observable_signal_axes(text: str) -> list[str]:
        axes: set[str] = set()
        if "pH" in text:
            axes.add("pH")
        if "ORP" in text or "氧化剂" in text:
            axes.add("ORP")
        if "电导" in text or "盐" in text or "EC" in text:
            axes.add("电导")
        if "浊度" in text or "颗粒" in text:
            axes.add("浊度")
        if any(token in text for token in ("UV254", "芳香", "天然有机质")):
            axes.add("UV254")
        if "流量" in text or "水力" in text:
            axes.add("流量")
        if "温度" in text or "temp" in text:
            axes.add("温度")
        return sorted(axes)

    @staticmethod
    def _hidden_state_axes(text: str, condition_signals: tuple[str, ...]) -> list[str]:
        axes: set[str] = set()
        joined_conditions = " ".join(condition_signals)
        combined = f"{text} {joined_conditions}"
        if "pollutant_residual_risk" in combined or "残留" in combined:
            axes.add("残留污染物风险")
        if "reaction_completion" in combined or "反应完成度" in combined:
            axes.add("反应完成度")
        if "byproduct_risk" in combined or "副产物" in combined:
            axes.add("副产物风险")
        if "catalyst_activity" in combined or "催化活性" in combined:
            axes.add("催化剂活性")
        if "matrix_interference" in combined or "基质" in combined:
            axes.add("基质抑制")
        return sorted(axes)

    @staticmethod
    def _evidence_axes(entry: KnowledgeEntry) -> list[str]:
        axes: set[str] = set()
        stage = entry.evidence_stage.lower()
        source_text = " ".join(entry.source_basis).lower()
        if "literature" in stage or entry.source_basis:
            axes.add("文献支持")
        if "simulation" in stage or "synthetic" in stage:
            axes.add("仿真支持")
        if "field" in stage or "field" in source_text or "现场" in source_text:
            axes.add("真实数据支持")
        if not axes:
            axes.add("仅假设")
        return sorted(axes)

    @staticmethod
    def _claim_boundary(entry: KnowledgeEntry) -> str:
        axes = KnowledgeGraphCurationAgent._evidence_axes(entry)
        if "真实数据支持" in axes:
            return "可作为 field-supported candidate，但仍需按 G0-G5 审计来源。"
        if "仿真支持" in axes and "文献支持" in axes:
            return "可作为 literature-informed simulation edge，不能写成现场实证。"
        if "文献支持" in axes:
            return "可作为 literature hypothesis，需要仿真和 field label 验证。"
        return "仅假设，不能进入控制写回。"

    @staticmethod
    def _coverage_missing(axis_coverage: dict[str, object], axis_name: str) -> list[str]:
        axis = axis_coverage.get(axis_name, {})
        if isinstance(axis, dict):
            missing = axis.get("missing", [])
            if isinstance(missing, list):
                return [str(item) for item in missing]
        return []

    @staticmethod
    def _as_list(value: object) -> list[object]:
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        return []
