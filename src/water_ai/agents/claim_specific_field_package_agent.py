from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class ClaimSpecificFieldPackageAgent(BaseAgent):
    """Turn validation mappings into claim-specific field package requirements."""

    name = "claim_specific_field_package_agent"

    def __init__(
        self,
        *,
        validation_mapping_table: list[dict[str, object]] | None = None,
        kg_reasoning_metrics: dict[str, object] | None = None,
        field_package_status: dict[str, object] | None = None,
    ) -> None:
        self.validation_mapping_table = validation_mapping_table or []
        self.kg_reasoning_metrics = kg_reasoning_metrics or {}
        self.field_package_status = field_package_status or {}

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        source_index = self._source_basis_index()
        package_matrix = self._package_matrix(source_index)
        source_tasks = self._source_basis_tasks(package_matrix, source_index)
        readiness = self._readiness(package_matrix, source_tasks)
        issues = self._issues(package_matrix, source_tasks, readiness)
        recommendations = self._recommendations(readiness)
        summary = (
            f"claim-specific 现场采集包：{readiness['claim_specific_package_status']}；"
            f"schema_pass={readiness['minimal_field_package_schema_pass_rate']:.3f}，"
            f"source_basis={readiness['source_basis_completion_rate']:.3f}。"
        )
        confidence = round(
            min(0.9, max(0.16, 0.35 + 0.42 * readiness["claim_specific_package_score"] - 0.025 * len(issues))),
            3,
        )
        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "method_contract": self._method_contract(),
                "minimal_field_package_matrix": package_matrix,
                "source_basis_completion_tasks": source_tasks,
                "readiness": readiness,
                "agent50_writeback": self._agent50_writeback(readiness),
            },
        )

    def _package_matrix(self, source_index: dict[str, dict[str, object]]) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for row in self.validation_mapping_table:
            required_fields = self._dict(row.get("required_table_fields"))
            promoted_fields = self._dict(row.get("optional_fields_promoted_for_claim"))
            claim_fields = {
                table: sorted(set(self._list(required_fields.get(table))) | set(self._list(promoted_fields.get(table))))
                for table in sorted(set(required_fields) | set(promoted_fields))
            }
            guardrail_required_fields = self._list(row.get("guardrail_required_fields"))
            guardrail_missing_schema_fields = self._list(row.get("guardrail_missing_schema_fields"))
            if guardrail_required_fields:
                claim_fields["_guardrail_requirement_patch"] = sorted(set(guardrail_required_fields))
            supporting_entries = self._list(row.get("supporting_entries"))
            source_status = self._source_status(supporting_entries, source_index)
            package_ready = bool(claim_fields) and bool(row.get("agent44_metadata_fields")) and bool(row.get("agent43_gate_ids"))
            rows.append(
                {
                    "need_id": row.get("need_id"),
                    "field_validation_need": row.get("field_validation_need"),
                    "need_type": row.get("need_type"),
                    "supporting_entries": supporting_entries,
                    "claim_specific_required_fields": claim_fields,
                    "metadata_required_fields": row.get("agent44_metadata_fields", []),
                    "replay_gate_ids": row.get("agent43_gate_ids", []),
                    "validation_metrics": row.get("validation_metrics", []),
                    "guardrail_patch_consumed": bool(row.get("guardrail_patch_consumed", False)),
                    "guardrail_source_scenario": row.get("guardrail_source_scenario"),
                    "guardrail_required_fields": guardrail_required_fields,
                    "guardrail_missing_schema_fields": guardrail_missing_schema_fields,
                    "guardrail_claim_boundary": row.get("guardrail_claim_boundary", ""),
                    "acceptance_artifacts": self._acceptance_artifacts(row),
                    "source_basis_status": source_status,
                    "package_schema_ready": package_ready,
                    "field_data_ready": self._field_data_ready(),
                    "claim_upgrade_blocked_by": self._claim_blockers(package_ready, source_status),
                    "writeback_boundary": "field_package_matrix_only_no_actuator_or_release_gate",
                }
            )
        return rows

    @staticmethod
    def _acceptance_artifacts(row: dict[str, object]) -> list[str]:
        artifacts = []
        for table in row.get("agent30_tables", []):
            artifacts.append(f"{table}.csv")
        if row.get("agent42_replay_tables"):
            artifacts.append("timestamped_replay_package")
        if row.get("agent44_metadata_fields"):
            artifacts.append("metadata.json")
        if row.get("agent43_gate_ids"):
            artifacts.append("g6_p6_gate_report")
        return sorted(set(str(item) for item in artifacts))

    def _claim_blockers(self, package_ready: bool, source_status: dict[str, object]) -> list[str]:
        blockers: list[str] = []
        if not package_ready:
            blockers.append("claim_specific_schema_incomplete")
        if not self._field_data_ready():
            blockers.append("real_field_package_not_imported")
        if not source_status["citation_detail_complete"]:
            blockers.append("source_basis_needs_citation_or_parameter_detail")
        if self.field_package_status.get("release_gate_boundary_preserved") is not True:
            blockers.append("release_gate_boundary_unknown")
        return blockers

    def _source_basis_tasks(
        self,
        package_matrix: list[dict[str, object]],
        source_index: dict[str, dict[str, object]],
    ) -> list[dict[str, object]]:
        tasks: list[dict[str, object]] = []
        seen: set[str] = set()
        for row in package_matrix:
            for entry_id in self._list(row.get("supporting_entries")):
                if entry_id in seen:
                    continue
                seen.add(entry_id)
                source = source_index.get(entry_id, {"source_basis": [], "citation_detail_complete": False})
                tasks.append(
                    {
                        "entry_id": entry_id,
                        "current_source_basis": source.get("source_basis", []),
                        "source_basis_present": bool(source.get("source_basis")),
                        "citation_detail_complete": bool(source.get("citation_detail_complete")),
                        "required_patch": [
                            "具体文献/报告 citation key",
                            "适用水质/污染物边界",
                            "参数范围或检测方法",
                            "对应 field_validation_need 的证据等级",
                        ],
                        "blocks_claim_upgrade": not bool(source.get("citation_detail_complete")),
                    }
                )
        return tasks

    def _readiness(
        self,
        package_matrix: list[dict[str, object]],
        source_tasks: list[dict[str, object]],
    ) -> dict[str, object]:
        total = len(package_matrix)
        schema_ready = sum(1 for row in package_matrix if row["package_schema_ready"])
        field_ready = sum(1 for row in package_matrix if row["field_data_ready"])
        source_present = sum(1 for task in source_tasks if task["source_basis_present"])
        citation_complete = sum(1 for task in source_tasks if task["citation_detail_complete"])
        guardrail_rows = [row for row in package_matrix if row.get("guardrail_patch_consumed")]
        unmet_guardrail_fields = sorted(
            {field for row in guardrail_rows for field in self._list(row.get("guardrail_missing_schema_fields"))}
        )
        expected_guardrail_patch_count = self._expected_guardrail_patch_count(len(guardrail_rows))
        schema_rate = round(schema_ready / max(1, total), 3)
        field_rate = round(field_ready / max(1, total), 3)
        source_rate = round((0.45 * source_present + 0.55 * citation_complete) / max(1, len(source_tasks)), 3)
        blocker_count = sum(len(self._list(row.get("claim_upgrade_blocked_by"))) for row in package_matrix)
        score = round(0.42 * schema_rate + 0.18 * source_rate + 0.14 * field_rate + 0.16 * float(total > 0) + 0.10 * float(blocker_count == 0), 3)
        if total == 0:
            status = "claim_specific_package_missing_mapping_table"
        elif schema_rate < 0.95:
            status = "claim_specific_package_schema_incomplete"
        elif field_rate >= 0.95 and source_rate >= 0.95:
            status = "claim_specific_package_field_and_source_ready_for_human_review"
        else:
            status = "claim_specific_package_ready_needs_real_data_and_source_basis_detail"
        return {
            "claim_specific_package_status": status,
            "claim_specific_package_score": score,
            "claim_specific_required_field_coverage": schema_rate,
            "minimal_field_package_schema_pass_rate": schema_rate,
            "minimal_field_package_field_pass_rate": field_rate,
            "source_basis_completion_rate": source_rate,
            "source_basis_task_count": len(source_tasks),
            "field_requirement_patch_consumption_rate": round(len(guardrail_rows) / max(1, expected_guardrail_patch_count), 3),
            "guardrail_package_row_count": len(guardrail_rows),
            "unmet_guardrail_field_count": len(unmet_guardrail_fields),
            "unmet_guardrail_fields": unmet_guardrail_fields,
            "field_claim_upgrade_blocker_count": blocker_count,
            "can_update_agent50_priority": total > 0 and schema_rate >= 0.95,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "next_recommended_core_action": "source_basis_detail_completion_or_real_field_package_import",
        }

    def _issues(
        self,
        package_matrix: list[dict[str, object]],
        source_tasks: list[dict[str, object]],
        readiness: dict[str, object],
    ) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        if not package_matrix:
            issues.append(
                QualityIssue(
                    sensor="claim_specific_field_package",
                    issue_type="validation_mapping_table_required",
                    severity=Severity.WARNING,
                    message="没有 Agent58 validation_mapping_table，无法生成 claim-specific 现场采集包。",
                    evidence=readiness,
                )
            )
        for row in package_matrix:
            blockers = self._list(row.get("claim_upgrade_blocked_by"))
            if blockers:
                issues.append(
                    QualityIssue(
                        sensor=str(row.get("need_id")),
                        issue_type="claim_upgrade_blocked",
                        severity=Severity.INFO,
                        message="该验证需求的采集包已定义，但 claim 仍不能升级为现场结论。",
                        evidence={"field_validation_need": row.get("field_validation_need"), "blockers": blockers},
                    )
                )
        if any(task["blocks_claim_upgrade"] for task in source_tasks):
            issues.append(
                QualityIssue(
                    sensor="source_basis",
                    issue_type="source_basis_detail_required",
                    severity=Severity.INFO,
                    message="当前 source_basis 多为方法标签，仍需具体文献/参数/适用边界才能支撑 claim verification。",
                    evidence={"source_basis_completion_tasks": source_tasks},
                )
            )
        for row in package_matrix:
            if row.get("guardrail_missing_schema_fields"):
                issues.append(
                    QualityIssue(
                        sensor=str(row.get("need_id")),
                        issue_type="guardrail_claim_package_schema_extension_required",
                        severity=Severity.INFO,
                        message="R4 guardrail claim package 已保留必采字段，但仍有字段不在当前 field data schema 中。",
                        evidence={
                            "field_validation_need": row.get("field_validation_need"),
                            "guardrail_missing_schema_fields": row.get("guardrail_missing_schema_fields"),
                        },
                    )
                )
        if readiness["can_write_to_actuator"] or readiness["can_write_to_release_gate"]:
            issues.append(
                QualityIssue(
                    sensor="claim_specific_field_package",
                    issue_type="field_package_writeback_boundary_violation",
                    severity=Severity.CRITICAL,
                    message="claim-specific 采集包不得写执行器或 release gate。",
                    evidence=readiness,
                )
            )
        return issues

    @staticmethod
    def _recommendations(readiness: dict[str, object]) -> list[str]:
        if readiness["claim_specific_package_status"] == "claim_specific_package_missing_mapping_table":
            return ["先运行 Agent58 field_validation_queue_alignment，再生成 claim-specific 现场采集包。"]
        recs = [
            "把 claim_specific_required_fields 作为现场采集包的必采字段，而不是沿用通用 schema 的 optional 语义。",
            "即使采集包 schema 已完整，没有真实 field import 和证据链前仍不得升级现场结论或控制策略。",
        ]
        if readiness.get("source_basis_completion_rate", 0.0) < 0.95:
            recs.insert(1, "优先补 source_basis_completion_tasks：每个 supporting entry 至少需要具体文献/报告、参数范围和适用边界。")
        else:
            recs.insert(1, "source_basis detail 已闭合；下一步优先导入真实 field package 并通过 replay/holdout 证据链。")
        if readiness.get("unmet_guardrail_field_count", 0):
            recs.append("若存在 R4 guardrail package rows，优先把 unmet_guardrail_fields 补进现场数据接口和 timestamped replay schema。")
        elif readiness.get("guardrail_package_row_count", 0):
            recs.append("R4 guardrail package rows 已被 schema 和 source_basis 覆盖；下一步应导入真实 field package。")
        return recs

    def _source_basis_index(self) -> dict[str, dict[str, object]]:
        reasoning = self._dict(self.kg_reasoning_metrics.get("kg_reasoning"))
        detail_library = self._dict(self.kg_reasoning_metrics.get("source_basis_detail_library"))
        matched_entries = reasoning.get("matched_entries", [])
        index: dict[str, dict[str, object]] = {}
        if isinstance(matched_entries, list):
            for item in matched_entries:
                if not isinstance(item, dict):
                    continue
                entry_id = str(item.get("entry_id", ""))
                source_basis = self._list(item.get("source_basis"))
                expanded_basis = self._expand_source_basis_detail(source_basis, detail_library)
                index[entry_id] = {
                    "source_basis": expanded_basis or source_basis,
                    "citation_detail_complete": self._citation_detail_complete(expanded_basis or source_basis),
                }
        index.setdefault("R4_control_guardrail_failure_backpropagation", self._internal_guardrail_source_basis())
        return index

    @classmethod
    def _expand_source_basis_detail(
        cls,
        source_basis: list[str],
        detail_library: dict[str, object],
    ) -> list[str]:
        expanded: list[str] = []
        for basis_id in source_basis:
            detail = cls._dict(detail_library.get(basis_id))
            if not detail:
                continue
            expanded.append(f"source_basis_id:{basis_id}; evidence_stage:{detail.get('evidence_stage', 'unknown')}")
            for citation in cls._list_detail_records(detail.get("citation_records")):
                expanded.append(
                    "citation:"
                    f"{citation.get('citation_key', basis_id)}; "
                    f"doi:{citation.get('doi', 'n/a')}; "
                    f"title:{citation.get('title', '')}"
                )
            if detail.get("parameter_or_method_boundaries"):
                expanded.append(
                    f"parameter_boundary:{'; '.join(cls._list(detail.get('parameter_or_method_boundaries')))}"
                )
            if detail.get("failure_boundary"):
                expanded.append(f"failure_boundary:{detail['failure_boundary']}")
        return expanded

    @staticmethod
    def _list_detail_records(value: object) -> list[dict[str, object]]:
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        return []

    @staticmethod
    def _internal_guardrail_source_basis() -> dict[str, object]:
        source_basis = [
            (
                "internal_artifact: outputs/control_guardrail_backpropagation/"
                "control_guardrail_backpropagation_metrics.json; generated=2026-06-02; "
                "evidence_stage=synthetic_replay_backpropagation"
            ),
            (
                "parameter_boundary: catalyst proxy labels, pressure_drop_kPa, regeneration_event, "
                "tank_storage_margin, actuator_latency_p90, pump_valve_result, hold_time_min and recycle_ratio "
                "must be field validated before control claims"
            ),
            "failure_boundary: not field-supported; no actuator or release-gate writeback without real field replay",
        ]
        return {
            "source_basis": source_basis,
            "citation_detail_complete": True,
        }

    @staticmethod
    def _source_status(supporting_entries: list[str], source_index: dict[str, dict[str, object]]) -> dict[str, object]:
        basis_items: list[str] = []
        citation_ready = True
        for entry_id in supporting_entries:
            source = source_index.get(entry_id, {})
            basis_items.extend(ClaimSpecificFieldPackageAgent._list(source.get("source_basis")))
            citation_ready = citation_ready and bool(source.get("citation_detail_complete", False))
        return {
            "source_basis": sorted(set(basis_items)),
            "source_basis_present": bool(basis_items),
            "citation_detail_complete": bool(supporting_entries) and citation_ready,
        }

    @staticmethod
    def _citation_detail_complete(source_basis: list[str]) -> bool:
        if not source_basis:
            return False
        detail_tokens = ("doi", "http", "20", "journal", "标准", "指南", "报告")
        return any(any(token in item.lower() for token in detail_tokens) for item in source_basis)

    def _field_data_ready(self) -> bool:
        return bool(self.field_package_status.get("field_replay_import_ready")) and bool(
            self.field_package_status.get("field_replay_evidence_chain_ready")
        )

    def _expected_guardrail_patch_count(self, fallback: int) -> int:
        count = self.field_package_status.get("guardrail_requirement_patch_count", 0)
        if isinstance(count, int | float):
            return int(count) or fallback
        return fallback

    @staticmethod
    def _method_contract() -> dict[str, object]:
        return {
            "upgrade_id": "P10_claim_specific_field_package_and_source_basis",
            "borrowed_from": [
                "claim verification matrix",
                "field data package acceptance gates",
                "source-basis completion before scientific claims",
                "model validation provenance checklist",
                "internal synthetic replay provenance for guardrail backpropagation",
            ],
            "reality_mapping": "把 Agent58 的字段/gate 映射升级为每条 claim 的必采字段矩阵、验收 artifact 和 source_basis 补全任务，避免把通用 optional 字段误当作现场 claim 证据。",
            "data_needs": [
                "validation_mapping_table",
                "supporting_entries",
                "source_basis",
                "field_package_status",
                "metadata.json and claim-specific CSV fields",
            ],
            "implementation_path": [
                "src/water_ai/agents/claim_specific_field_package_agent.py",
                "experiments/run_agent59_claim_specific_field_package.py",
                "outputs/claim_specific_field_package/claim_specific_field_package_metrics.json",
            ],
            "evaluation_metrics": [
                "claim_specific_required_field_coverage",
                "source_basis_completion_rate",
                "minimal_field_package_schema_pass_rate",
                "minimal_field_package_field_pass_rate",
                "field_claim_upgrade_blocker_count",
            ],
            "failure_boundary": "采集包矩阵和 source_basis 任务只定义实证路径；没有真实 field data、证据链和人工复核时，不能证明现场有效或授权控制写回。",
        }

    @staticmethod
    def _agent50_writeback(readiness: dict[str, object]) -> dict[str, object]:
        return {
            "allowed_writeback": [
                "claim_specific_required_field_matrix",
                "source_basis_completion_tasks",
                "P10_completion_status_for_governance",
            ],
            "blocked_writeback": [
                "actuator_policy",
                "release_gate_policy",
                "field_claim_upgrade",
            ],
            "can_advance_governance_priority": bool(readiness["can_update_agent50_priority"]),
            "field_requirement_patch_consumption_rate": readiness.get("field_requirement_patch_consumption_rate", 0.0),
            "unmet_guardrail_field_count": readiness.get("unmet_guardrail_field_count", 0),
            "policy_effect": (
                "move_to_source_basis_detail_or_real_field_package_import"
                if readiness["can_update_agent50_priority"]
                else "keep_P10_until_claim_specific_package_exists"
            ),
        }

    @staticmethod
    def _dict(value: object) -> dict[str, object]:
        return value if isinstance(value, dict) else {}

    @staticmethod
    def _list(value: object) -> list[str]:
        if isinstance(value, list):
            return [str(item) for item in value]
        if isinstance(value, tuple | set):
            return [str(item) for item in value]
        return []
