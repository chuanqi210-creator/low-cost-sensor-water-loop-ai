from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity
from water_ai.knowledge import KNOWLEDGE_BASE


class ModelRealismAuditAgent(BaseAgent):
    """Audit whether the current model is scientifically grounded and field-ready."""

    name = "model_realism_audit_agent"

    def __init__(
        self,
        *,
        training_metrics: dict[str, object] | None = None,
        field_gate_metrics: dict[str, object] | None = None,
        latest_regression: str = "unknown",
    ) -> None:
        self.training_metrics = training_metrics or {}
        self.field_gate_metrics = field_gate_metrics or {}
        self.latest_regression = latest_regression

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        knowledge_audit = self._knowledge_audit()
        validation_audit = self._validation_audit()
        field_audit = self._field_audit()
        process_audit = self._process_audit(validation_audit)
        skill_workflow = self._skill_inspired_workflow()
        backlog = self._backlog(knowledge_audit, validation_audit, field_audit, process_audit)
        readiness = self._readiness(knowledge_audit, validation_audit, field_audit, backlog)
        issues = self._issues(readiness, knowledge_audit, validation_audit, field_audit)
        recommendations = self._recommendations(backlog)
        summary = (
            f"模型现实性审计：{readiness['realism_status']}；"
            f"知识库 {knowledge_audit['entry_count']} 条，"
            f"field 门控 {field_audit['accepted_gate_count']}/{field_audit['total_gate_count']} 通过。"
        )
        confidence = round(min(0.9, max(0.28, 0.46 + 0.32 * readiness["realism_score"] - 0.035 * len(issues))), 3)

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "knowledge_audit": knowledge_audit,
                "validation_audit": validation_audit,
                "field_audit": field_audit,
                "process_audit": process_audit,
                "skill_inspired_workflow": skill_workflow,
                "model_upgrade_backlog": backlog,
                "readiness": readiness,
                "latest_regression": self.latest_regression,
            },
        )

    @staticmethod
    def _knowledge_audit() -> dict[str, object]:
        entries = list(KNOWLEDGE_BASE)
        pollutant_classes = sorted({entry.pollutant_class for entry in entries})
        material_families = sorted({entry.material_family for entry in entries})
        mechanism_tags = sorted({tag for entry in entries for tag in entry.mechanism_tags})
        field_needs = sorted({need for entry in entries for need in entry.field_validation_need})
        source_basis = sorted({source for entry in entries for source in entry.source_basis})
        expected_axes = {
            "persistent_micropollutant": any("PFAS" in entry.pollutant_class or "持久性" in entry.pollutant_class for entry in entries),
            "heavy_metal_or_speciation": any("重金属" in entry.pollutant_class or "金属" in entry.pollutant_class for entry in entries),
            "biological_or_nutrient_effluent": any("生化" in entry.pollutant_class or "营养盐" in entry.pollutant_class for entry in entries),
            "catalyst_lifecycle": any("catalyst_deactivation" in entry.mechanism_tags for entry in entries),
            "sensor_uncertainty": any("sensor_uncertainty" in entry.mechanism_tags for entry in entries),
            "byproduct_risk": any("byproduct_risk" in entry.mechanism_tags for entry in entries),
        }
        missing_axes = [axis for axis, covered in expected_axes.items() if not covered]
        coverage_score = round(
            0.35 * min(1.0, len(entries) / 12)
            + 0.25 * (1.0 - len(missing_axes) / max(1, len(expected_axes)))
            + 0.20 * min(1.0, len(field_needs) / 10)
            + 0.20 * min(1.0, len(source_basis) / 8),
            3,
        )
        return {
            "entry_count": len(entries),
            "pollutant_classes": pollutant_classes,
            "material_families": material_families,
            "mechanism_tag_count": len(mechanism_tags),
            "mechanism_tags": mechanism_tags,
            "field_validation_need_count": len(field_needs),
            "source_basis_count": len(source_basis),
            "expected_axes": expected_axes,
            "missing_axes": missing_axes,
            "coverage_score": coverage_score,
            "coverage_status": "knowledge_base_needs_expansion" if coverage_score < 0.78 else "knowledge_base_seed_ready",
        }

    def _validation_audit(self) -> dict[str, object]:
        rows_by_source = self._as_dict(self.training_metrics.get("rows_by_source", {}))
        mae_by_target = self._as_dict(self.training_metrics.get("mae_by_target", {}))
        r2_by_target = self._as_dict(self.training_metrics.get("r2_by_target", {}))
        rows = int(float(self.training_metrics.get("rows", 0) or 0))
        field_rows = int(float(rows_by_source.get("field", 0) or 0))
        synthetic_rows = rows - field_rows
        weaker_targets = [
            target
            for target, value in r2_by_target.items()
            if isinstance(value, int | float) and float(value) < 0.93
        ]
        has_uncertainty_layer = bool(self.training_metrics.get("uncertainty_metrics"))
        uncertainty_evidence_stage = str(self.training_metrics.get("uncertainty_evidence_stage", "missing"))
        validation_score = round(
            0.20 * min(1.0, rows / 50000)
            + 0.30 * (field_rows > 0)
            + 0.20 * (1.0 - min(1.0, len(weaker_targets) / 5))
            + 0.20 * has_uncertainty_layer
            + 0.10 * bool(mae_by_target),
            3,
        )
        if field_rows == 0 and has_uncertainty_layer:
            validation_status = "synthetic_uncertainty_ready_field_holdout_missing"
        elif field_rows == 0 or not has_uncertainty_layer:
            validation_status = "synthetic_only_uncertainty_missing"
        else:
            validation_status = "field_calibrated_uncertainty_ready"
        return {
            "model_version": self.training_metrics.get("model_version", "unknown"),
            "rows": rows,
            "field_rows": field_rows,
            "synthetic_rows": synthetic_rows,
            "rows_by_source": rows_by_source,
            "mean_mae": self.training_metrics.get("mean_mae"),
            "weaker_targets": weaker_targets,
            "has_uncertainty_layer": has_uncertainty_layer,
            "uncertainty_evidence_stage": uncertainty_evidence_stage,
            "validation_score": validation_score,
            "validation_status": validation_status,
            "required_next_metrics": [
                "field holdout MAE/R2",
                "calibration curve for release probability",
                "prediction interval coverage",
                "out-of-distribution / extrapolation flag",
                "target-specific uncertainty for catalyst and matrix estimates",
            ],
        }

    def _field_audit(self) -> dict[str, object]:
        readiness = self._as_dict(self.field_gate_metrics.get("readiness", {}))
        accepted = int(float(readiness.get("accepted_gate_count", 0) or 0))
        total = int(float(readiness.get("total_gate_count", 0) or 0))
        blocking = readiness.get("blocking_gates", [])
        return {
            "calibration_gate_status": readiness.get("calibration_gate_status", "unknown"),
            "accepted_gate_count": accepted,
            "total_gate_count": total,
            "blocking_gates": blocking if isinstance(blocking, list) else [],
            "data_origin": readiness.get("data_origin", "unknown"),
            "field_data_required": bool(readiness.get("field_data_required", True)),
            "field_status": "field_validation_blocked" if readiness.get("field_data_required", True) else "field_validation_can_start",
        }

    @staticmethod
    def _process_audit(validation_audit: dict[str, object]) -> dict[str, object]:
        has_uncertainty_layer = bool(validation_audit.get("has_uncertainty_layer"))
        uncertainty_gap = (
            {
                "gap_id": "uncertainty_and_extrapolation",
                "current_state": "软传感器已有 synthetic 不确定性、预测区间和 OOD 风险门，但尚未用真实 field holdout 校准。",
                "realism_upgrade": "用真实离线标签做 prediction interval coverage、release probability calibration 和 conformal calibration。",
                "validation_data": ["field holdout set", "离线标签", "传感器漂移与缺失日志"],
            }
            if has_uncertainty_layer
            else {
                "gap_id": "uncertainty_and_extrapolation",
                "current_state": "软传感器有传感置信度降权，但缺少预测区间、校准曲线和外推风险门。",
                "realism_upgrade": "加入 bootstrap/ensemble uncertainty、release probability calibration 和 OOD 标记。",
                "validation_data": ["field holdout set", "离线标签", "传感器漂移与缺失日志"],
            }
        )
        gaps = [
            {
                "gap_id": "mechanistic_kinetics_parameterization",
                "current_state": "过程动力学使用可解释启发式速率，尚未由真实反应动力学或现场参数校准。",
                "realism_upgrade": "引入污染物类别、催化剂、pH、基质和停留时间的参数化速率范围。",
                "validation_data": ["批内浓度时间序列", "剂量/停留时间记录", "目标物和副产物标签"],
            },
            uncertainty_gap,
            {
                "gap_id": "target_specific_byproduct_speciation",
                "current_state": "副产物风险是综合指标，尚未区分卤代副产物、过氧化残留或目标物中间体。",
                "realism_upgrade": "按污染物类别建立副产物风险子节点，并绑定必须检测的离线指标。",
                "validation_data": ["副产物检测", "余氧化剂", "目标物中间体"],
            },
            {
                "gap_id": "field_control_latency",
                "current_state": "循环和延迟已建模，但 PLC/SCADA 接口、人工复核和检测排队时间仍偏简化。",
                "realism_upgrade": "把控制动作拆为可执行时序、人工/仪器资源和失败重试。",
                "validation_data": ["操作日志", "采样/检测排队", "人工覆盖记录"],
            },
        ]
        return {"gap_count": len(gaps), "gaps": gaps, "process_realism_status": "grey_box_seed_needs_field_parameterization"}

    @staticmethod
    def _skill_inspired_workflow() -> list[dict[str, str]]:
        return [
            {
                "skill_family": "systematic_literature_review",
                "borrowed_idea": "从单篇论文阅读转为跨论文抽取研究问题、方法、发现、限制和可迁移参数。",
                "project_use": "建立污染物-材料-机制-信号-动作的证据矩阵。",
            },
            {
                "skill_family": "academic_research_agent",
                "borrowed_idea": "evidence before claims、claim verification 和 human approval gates。",
                "project_use": "所有 field 结论必须经过 G0-G5 门控，synthetic 只能标注为仿真基线。",
            },
            {
                "skill_family": "scientific_knowledge_graph",
                "borrowed_idea": "用结构化知识图谱组织异构科学证据，并用可追溯路径解释预测。",
                "project_use": "把知识库从动作偏置升级为可审计机制证据层。",
            },
            {
                "skill_family": "model_validation_and_uncertainty",
                "borrowed_idea": "校准曲线、预测区间、bootstrap/ensemble uncertainty 和外推风险。",
                "project_use": "升级 SoftSensorAgent 的 release gate 和 field holdout 评价。",
            },
        ]

    @staticmethod
    def _backlog(
        knowledge_audit: dict[str, object],
        validation_audit: dict[str, object],
        field_audit: dict[str, object],
        process_audit: dict[str, object],
    ) -> list[dict[str, object]]:
        soft_sensor_work = (
            {
                "priority": "P1",
                "work_id": "soft_sensor_uncertainty_field_calibration",
                "title": "用 field holdout 和保形校准验证软传感不确定性",
                "why": "当前已有 synthetic 不确定性层，但还不能替代真实现场 holdout 与释放概率校准。",
                "blocks": validation_audit["required_next_metrics"],
                "target_files": [
                    "src/water_ai/agents/soft_sensor_agent.py",
                    "src/water_ai/agents/soft_sensor_uncertainty_validation_agent.py",
                    "experiments/train_soft_sensor_model.py",
                ],
            }
            if validation_audit.get("has_uncertainty_layer")
            else {
                "priority": "P1",
                "work_id": "soft_sensor_uncertainty_layer",
                "title": "给软传感器增加不确定性、校准曲线和外推风险门",
                "why": "当前模型有 MAE/R2，但没有 release probability calibration 和 prediction interval coverage。",
                "blocks": validation_audit["required_next_metrics"],
                "target_files": ["src/water_ai/agents/soft_sensor_agent.py", "experiments/train_soft_sensor_model.py"],
            }
        )
        backlog = [
            {
                "priority": "P0",
                "work_id": "field_data_acceptance_before_retraining",
                "title": "先通过真实数据 G0-G2，再允许任何参数写回",
                "why": "当前最大现实性风险是 synthetic/sample 被误当成现场校准。",
                "blocks": field_audit["blocking_gates"],
                "target_files": ["outputs/agent30_field_data_interface/", "deliverables/field_data_acceptance_gates.md"],
            },
            soft_sensor_work,
            {
                "priority": "P1",
                "work_id": "knowledge_graph_evidence_matrix",
                "title": "把知识库扩展为污染物-材料-机制-信号-动作-证据等级矩阵",
                "why": "知识库已有 seed，但仍需要系统文献综述式扩展和证据等级管理。",
                "blocks": knowledge_audit["missing_axes"],
                "target_files": ["src/water_ai/knowledge.py", "deliverables/model_realism_audit.md"],
            },
        ]
        for gap in process_audit["gaps"]:
            backlog.append(
                {
                    "priority": "P2",
                    "work_id": gap["gap_id"],
                    "title": gap["realism_upgrade"],
                    "why": gap["current_state"],
                    "blocks": gap["validation_data"],
                    "target_files": ["src/water_ai/process_dynamics.py", "outputs/agent35_model_realism_audit/"],
                }
            )
        return backlog

    @staticmethod
    def _readiness(
        knowledge_audit: dict[str, object],
        validation_audit: dict[str, object],
        field_audit: dict[str, object],
        backlog: list[dict[str, object]],
    ) -> dict[str, object]:
        score = round(
            0.32 * float(knowledge_audit["coverage_score"])
            + 0.30 * float(validation_audit["validation_score"])
            + 0.24 * (int(field_audit["accepted_gate_count"]) / max(1, int(field_audit["total_gate_count"])))
            + 0.14 * (1.0 - min(1.0, len([item for item in backlog if item["priority"] == "P0"]) / 3)),
            3,
        )
        if field_audit["field_data_required"]:
            status = "simulation_baseline_needs_field_grounding"
        elif score < 0.72:
            status = "model_needs_realism_upgrades"
        else:
            status = "field_calibrated_model_iteration_ready"
        return {
            "realism_status": status,
            "realism_score": score,
            "p0_blocker_count": len([item for item in backlog if item["priority"] == "P0"]),
            "p1_upgrade_count": len([item for item in backlog if item["priority"] == "P1"]),
        }

    @staticmethod
    def _issues(
        readiness: dict[str, object],
        knowledge_audit: dict[str, object],
        validation_audit: dict[str, object],
        field_audit: dict[str, object],
    ) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        if field_audit["field_data_required"]:
            issues.append(
                QualityIssue(
                    sensor="model_realism",
                    issue_type="field_validation_missing",
                    severity=Severity.WARNING,
                    message="当前模型只能作为仿真基线，真实参数写回必须等待 field 数据通过 G0-G5。",
                    evidence=field_audit,
                )
            )
        if validation_audit["validation_status"] in {"synthetic_only_uncertainty_missing", "synthetic_uncertainty_ready_field_holdout_missing"}:
            issues.append(
                QualityIssue(
                    sensor="soft_sensor_model",
                    issue_type="uncertainty_validation_missing",
                    severity=Severity.WARNING,
                    message="软传感器仍缺少现场 holdout 校准；当前不确定性层不能替代 field validation。",
                    evidence=validation_audit,
                )
            )
        if knowledge_audit["coverage_status"] == "knowledge_base_needs_expansion":
            issues.append(
                QualityIssue(
                    sensor="knowledge_base",
                    issue_type="knowledge_base_undercoverage",
                    severity=Severity.INFO,
                    message="知识库仍是 seed 层，需要系统文献综述式扩展。",
                    evidence=knowledge_audit,
                )
            )
        if readiness["realism_score"] < 0.7:
            issues.append(
                QualityIssue(
                    sensor="model_realism",
                    issue_type="model_realism_score_low",
                    severity=Severity.INFO,
                    message="模型结构已有雏形，但距离真实现场可用仍需补充 field calibration 和不确定性验证。",
                    evidence=readiness,
                )
            )
        return issues

    @staticmethod
    def _recommendations(backlog: list[dict[str, object]]) -> list[str]:
        return [
            f"{item['priority']} {item['title']}"
            for item in backlog[:5]
        ]

    @staticmethod
    def _as_dict(value: object) -> dict[str, object]:
        return value if isinstance(value, dict) else {}
