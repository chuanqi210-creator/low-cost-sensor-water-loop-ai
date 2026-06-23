from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


SOURCE_BASIS_DETAIL_LIBRARY: dict[str, dict[str, Any]] = {
    "low_cost_proxy_sensing": {
        "source_basis_id": "low_cost_proxy_sensing",
        "evidence_stage": "literature_supported_method_not_field_validated",
        "citation_records": [
            {
                "citation_key": "Schneider_2020_EST_onsite_soft_sensors",
                "title": "Benchmarking Soft Sensors for Remote Monitoring of On-Site Wastewater Treatment Plants",
                "doi": "10.1021/acs.est.9b07760",
                "source_url": "https://doi.org/10.1021/acs.est.9b07760",
                "supports": [
                    "低成本/低维护传感器可通过软传感框架支持现场过程监测",
                    "传感器漂移、失效和维护状态必须作为模型输入或门控条件",
                ],
            },
            {
                "citation_key": "Song_2021_WaterResearch_AOP_surrogates",
                "title": "Surrogates for on-line monitoring of the attenuation of trace organic contaminants during advanced oxidation processes for water reuse",
                "doi": "10.1016/j.watres.2020.116733",
                "source_url": "https://doi.org/10.1016/j.watres.2020.116733",
                "supports": [
                    "UV/荧光等代理信号可用于跟踪有机物或微污染物处理趋势",
                    "代理信号与目标污染物之间的关系需要按水质、工艺和污染物类别校准",
                ],
            },
        ],
        "reality_mapping": (
            "支撑本项目用 pH、ORP、EC、浊度、UV254、流量等低成本信号作为软传感和控制的输入，"
            "但这些信号只能作为 proxy，不是低浓度目标污染物的直接达标证据。"
        ),
        "applicable_conditions": [
            "存在低成本在线传感器或低维护传感器",
            "目标污染物不可高频直接检测",
            "有传感器状态、时间戳、仪器快照和离线标签用于校准",
        ],
        "parameter_or_method_boundaries": [
            "必须记录 sensor_status、instrument_id、acquisition_time_min、ingest_time_min",
            "必须估计 sensor_drift_rate、timestamp_coverage、sensor_status_coverage",
            "UV254/荧光 proxy 不能跨污染物类别、水质基质或工艺阶段无校准迁移",
        ],
        "required_field_validation": [
            "真实传感漂移记录",
            "离线放行标签",
            "低浓度目标物检测限",
        ],
        "failure_boundary": (
            "低成本 proxy sensing 可增强观测和排序，但不能单独证明污染物达标；"
            "没有 field-labeled drift 和离线检测标签时不能写 release gate。"
        ),
    },
    "soft_sensor_release_gate": {
        "source_basis_id": "soft_sensor_release_gate",
        "evidence_stage": "literature_supported_validation_method_not_field_validated",
        "citation_records": [
            {
                "citation_key": "Haimi_2013_EnvModSoft_WWTP_soft_sensors",
                "title": "Data-derived soft-sensors for biological wastewater treatment plants: An overview",
                "doi": "10.1016/j.envsoft.2013.05.009",
                "source_url": "https://doi.org/10.1016/j.envsoft.2013.05.009",
                "supports": [
                    "软传感器可估计难以在线直接测量的水处理变量",
                    "软传感器部署前必须处理数据质量、校准、验证和维护边界",
                ],
            },
            {
                "citation_key": "Dürrenmatt_2021_WaterResearch_Ecoli_soft_sensor",
                "title": "Soft sensor predictor of E. coli concentration based on conventional monitoring parameters for wastewater disinfection control",
                "doi": "10.1016/j.watres.2021.116806",
                "source_url": "https://doi.org/10.1016/j.watres.2021.116806",
                "supports": [
                    "软传感预测可服务实时风险保护或放行辅助决策",
                    "放行相关使用需要真实标签、误报/漏报成本和保守门控",
                ],
            },
            {
                "citation_key": "Angelopoulos_Bates_2023_conformal_prediction",
                "title": "Conformal Prediction: A Gentle Introduction",
                "doi": "10.1561/2200000101",
                "source_url": "https://doi.org/10.1561/2200000101",
                "supports": [
                    "保形预测可把黑箱预测转成有覆盖率目标的预测区间",
                    "覆盖率阈值必须在独立校准/holdout 数据上估计，不能由训练集或 synthetic 样例替代",
                ],
            },
        ],
        "reality_mapping": (
            "支撑本项目将软传感输出作为 release gate 的候选输入，但必须经过 field holdout、弱目标分层覆盖、"
            "OOD/abstention 和离线实验标签共同校准。"
        ),
        "applicable_conditions": [
            "有独立 field holdout 或可审计 replay 数据",
            "有目标污染物/放行标签和检测限",
            "能区分预测辅助、保护性控制和自动放行三个不同写回级别",
        ],
        "parameter_or_method_boundaries": [
            "必须报告 interval_coverage、conformal_coverage、interval_width、abstention_rate",
            "必须按 catalyst_activity、matrix_interference 等弱目标分层检查 coverage",
            "若 SFG0 field origin 或弱目标 coverage 未通过，不能写 release gate",
        ],
        "required_field_validation": [
            "离线放行标签",
            "低浓度目标物检测限",
            "field holdout sensor/lab paired records",
        ],
        "failure_boundary": (
            "软传感 release gate 只能在真实 field holdout 和离线标签通过后成为校准候选；"
            "synthetic conformal coverage 不能证明现场自动放行安全。"
        ),
    },
}


@dataclass(frozen=True)
class UnifiedFieldEvidenceGate:
    """Facade that merges field package, replay, holdout and claim evidence gates.

    This is intentionally not another numbered agent. It is a consolidation
    interface for the existing Agent43/44/45/46/58/59 evidence gates.
    """

    field_validation_alignment_metrics: dict[str, Any]
    claim_specific_package_metrics: dict[str, Any]
    field_replay_import_metrics: dict[str, Any]
    field_replay_gate_metrics: dict[str, Any]
    field_replay_evidence_chain_metrics: dict[str, Any]
    soft_sensor_field_holdout_gate_metrics: dict[str, Any]
    source_basis_detail_metrics: dict[str, Any] = field(default_factory=dict)

    def build(self) -> dict[str, Any]:
        records = self._unified_records()
        readiness = self._readiness(records)
        claim_basis_promotion_gate = self._claim_basis_promotion_gate(records, readiness)
        return {
            "method_contract": self._method_contract(),
            "unified_evidence_records": records,
            "gate_consolidation": self._gate_consolidation(records),
            "source_basis_detail_tasks": self._source_basis_detail_tasks(),
            "source_basis_detail_library": SOURCE_BASIS_DETAIL_LIBRARY,
            "source_basis_detail_status": self._source_basis_detail_status(records),
            "claim_basis_promotion_gate": claim_basis_promotion_gate,
            "readiness": readiness,
            "writeback_policy": self._writeback_policy(readiness),
            "next_refactor_action": self._next_refactor_action(readiness),
        }

    @staticmethod
    def _method_contract() -> dict[str, Any]:
        return {
            "upgrade_id": "R1_unified_field_evidence_and_source_basis_gate",
            "borrowed_from": [
                "evidence-before-claims workflow",
                "field data package acceptance gates",
                "timestamped replay gate consolidation",
                "soft sensor field holdout release gate",
                "source-basis completion before scientific claims",
            ],
            "reality_mapping": (
                "把 Agent44 导入门、Agent43/45 replay gate、Agent46 soft sensor field holdout gate、"
                "Agent58 validation mapping 和 Agent59 claim package/source_basis 合并为一个证据门控接口。"
            ),
            "data_needs": [
                "field_validation_mapping_table",
                "minimal_field_package_matrix",
                "metadata.json provenance",
                "timestamped sensor/lab/operation/proxy replay",
                "soft_sensor_field_holdout_labels",
                "source_basis citation and parameter boundaries",
            ],
            "implementation_path": [
                "src/water_ai/field_evidence_gate.py",
                "experiments/run_unified_field_evidence_gate.py",
                "outputs/unified_field_evidence_gate/unified_field_evidence_gate_metrics.json",
            ],
            "evaluation_metrics": [
                "unified_evidence_record_count",
                "gate_source_consolidation_coverage",
                "source_basis_completion_rate",
                "field_import_pass",
                "field_replay_evidence_chain_pass",
                "soft_sensor_field_holdout_gate_pass",
                "can_emit_field_claim_upgrade",
                "can_write_to_release_gate",
            ],
            "failure_boundary": (
                "统一接口只消除重复 gate 和重复 claim 阻断；synthetic/sample 仍不能被表述为 field validation，"
                "文献 source_basis 不能替代 field-supported evidence，不能写执行器或 release gate。"
            ),
        }

    def _unified_records(self) -> list[dict[str, Any]]:
        alignment_rows = self.field_validation_alignment_metrics.get("validation_mapping_table", [])
        package_rows = {
            row.get("need_id"): row for row in self.claim_specific_package_metrics.get("minimal_field_package_matrix", [])
        }
        import_stage = self._field_import_status()
        replay_gate = self._field_replay_gate_status()
        evidence_chain = self._evidence_chain_status()
        soft_holdout = self._soft_sensor_gate_status()
        records: list[dict[str, Any]] = []
        for alignment in alignment_rows:
            need_id = alignment.get("need_id", "unknown_need")
            package = package_rows.get(need_id, {})
            source_basis_status = package.get("source_basis_status", {})
            detailed_basis = self._detailed_source_basis(source_basis_status.get("source_basis", []))
            blockers = self._record_blockers(
                package=package,
                import_stage=import_stage,
                replay_gate=replay_gate,
                evidence_chain=evidence_chain,
                soft_holdout=soft_holdout,
                detailed_basis=detailed_basis,
            )
            records.append(
                {
                    "need_id": need_id,
                    "field_validation_need": alignment.get("field_validation_need", ""),
                    "need_type": alignment.get("need_type", ""),
                    "supporting_entries": sorted(
                        set(alignment.get("supporting_entries", [])) | set(package.get("supporting_entries", []))
                    ),
                    "claim_specific_required_fields": package.get(
                        "claim_specific_required_fields", alignment.get("required_table_fields", {})
                    ),
                    "metadata_required_fields": package.get(
                        "metadata_required_fields", alignment.get("agent44_metadata_fields", [])
                    ),
                    "replay_gate_ids": sorted(set(alignment.get("agent43_gate_ids", [])) | set(package.get("replay_gate_ids", []))),
                    "validation_metrics": sorted(
                        set(alignment.get("validation_metrics", [])) | set(package.get("validation_metrics", []))
                    ),
                    "acceptance_artifacts": package.get("acceptance_artifacts", []),
                    "source_basis_status": {
                        "source_basis": source_basis_status.get("source_basis", []),
                        "source_basis_present": bool(source_basis_status.get("source_basis_present")),
                        "citation_detail_complete": bool(source_basis_status.get("citation_detail_complete")),
                        "detail_patch_available": self._source_basis_detail_patch_available(
                            package.get("supporting_entries", [])
                        ),
                        "detail_library_complete": self._basis_details_complete(detailed_basis),
                        "detailed_source_basis": detailed_basis,
                    },
                    "field_import_status": import_stage,
                    "field_replay_gate_status": replay_gate,
                    "field_replay_evidence_chain_status": evidence_chain,
                    "soft_sensor_field_holdout_status": soft_holdout,
                    "evidence_stage": self._evidence_stage(blockers),
                    "claim_upgrade_blocked_by": blockers,
                    "can_emit_field_claim_upgrade": False,
                    "can_write_to_actuator": False,
                    "can_write_to_release_gate": False,
                    "writeback_boundary": "unified_evidence_gate_only_no_actuator_or_release_gate",
                }
            )
        return records

    def _field_import_status(self) -> dict[str, Any]:
        readiness = self.field_replay_import_metrics.get("readiness", {})
        metadata = self.field_replay_import_metrics.get("metadata_audit", {})
        return {
            "status": readiness.get("field_replay_import_status", "unknown"),
            "data_origin": metadata.get("data_origin", "unknown"),
            "origin_ready": bool(metadata.get("origin_ready")),
            "import_ready": bool(readiness.get("can_pass_to_timestamped_replay")),
            "accepted_table_count": readiness.get("accepted_table_count", 0),
            "total_table_count": readiness.get("total_table_count", 0),
        }

    def _field_replay_gate_status(self) -> dict[str, Any]:
        readiness = self.field_replay_gate_metrics.get("readiness", {})
        gate_results = self.field_replay_gate_metrics.get("gate_results", {})
        return {
            "status": readiness.get("field_replay_gate_status", "unknown"),
            "accepted_gate_count": readiness.get("accepted_gate_count", 0),
            "total_gate_count": readiness.get("total_gate_count", 0),
            "failed_gate_ids": readiness.get("failed_gate_ids", gate_results.get("failed_gate_ids", [])),
            "can_write_to_protective_control": bool(readiness.get("can_write_to_protective_control")),
            "can_write_to_release_gate": bool(readiness.get("can_write_to_release_gate")),
        }

    def _evidence_chain_status(self) -> dict[str, Any]:
        readiness = self.field_replay_evidence_chain_metrics.get("readiness", {})
        return {
            "status": readiness.get("field_replay_evidence_chain_status", "unknown"),
            "import_ready": bool(readiness.get("import_ready")),
            "timestamped_replay_ready": bool(readiness.get("timestamped_replay_ready")),
            "g6_ready": bool(readiness.get("g6_ready")),
            "can_emit_protective_writeback_candidate": bool(
                readiness.get("can_emit_protective_writeback_candidate")
            ),
            "can_write_to_release_gate": bool(readiness.get("can_write_to_release_gate")),
        }

    def _soft_sensor_gate_status(self) -> dict[str, Any]:
        readiness = self.soft_sensor_field_holdout_gate_metrics.get("readiness", {})
        return {
            "status": readiness.get("soft_sensor_field_holdout_gate_status", "unknown"),
            "passed_check_count": readiness.get("passed_check_count", 0),
            "total_check_count": readiness.get("total_check_count", 0),
            "failed_check_ids": readiness.get("failed_check_ids", []),
            "can_write_to_release_gate": bool(readiness.get("can_write_to_release_gate")),
        }

    def _record_blockers(
        self,
        *,
        package: dict[str, Any],
        import_stage: dict[str, Any],
        replay_gate: dict[str, Any],
        evidence_chain: dict[str, Any],
        soft_holdout: dict[str, Any],
        detailed_basis: list[dict[str, Any]],
    ) -> list[str]:
        blockers: list[str] = []
        source_basis_status = package.get("source_basis_status", {})
        basis_detail_complete = self._basis_details_complete(detailed_basis)
        package_blockers = list(package.get("claim_upgrade_blocked_by", []))
        if basis_detail_complete:
            package_blockers = [
                blocker
                for blocker in package_blockers
                if blocker != "source_basis_needs_citation_or_parameter_detail"
            ]
        blockers.extend(package_blockers)
        if not import_stage["origin_ready"]:
            blockers.append("field_origin_not_verified")
        if not import_stage["import_ready"]:
            blockers.append("field_replay_import_not_passed")
        blockers.extend(f"failed_replay_gate:{gate_id}" for gate_id in replay_gate.get("failed_gate_ids", []))
        if not evidence_chain["can_emit_protective_writeback_candidate"]:
            blockers.append("field_replay_evidence_chain_not_passed")
        blockers.extend(f"failed_soft_sensor_gate:{check_id}" for check_id in soft_holdout.get("failed_check_ids", []))
        if not source_basis_status.get("citation_detail_complete"):
            if basis_detail_complete:
                blockers.append("source_basis_literature_detail_complete_not_field_supported")
            else:
                blockers.append("source_basis_needs_citation_or_parameter_detail")
        return sorted(set(blockers))

    @staticmethod
    def _evidence_stage(blockers: list[str]) -> str:
        if any("field_origin_not_verified" in blocker or "real_field_package" in blocker for blocker in blockers):
            return "synthetic_baseline_field_validation_required"
        if any("source_basis" in blocker for blocker in blockers):
            return "literature_supported_source_basis_incomplete"
        return "field_validation_candidate_needs_human_review"

    def _source_basis_detail_patch_available(self, supporting_entries: list[str]) -> bool:
        detailed = self.source_basis_detail_metrics.get("detailed_source_basis_by_entry", {})
        return any(entry in detailed for entry in supporting_entries)

    @staticmethod
    def _detailed_source_basis(source_basis: list[str]) -> list[dict[str, Any]]:
        details: list[dict[str, Any]] = []
        seen: set[str] = set()
        for raw_basis in source_basis:
            basis_id = UnifiedFieldEvidenceGate._source_basis_id(str(raw_basis))
            if basis_id in SOURCE_BASIS_DETAIL_LIBRARY and basis_id not in seen:
                details.append(SOURCE_BASIS_DETAIL_LIBRARY[basis_id])
                seen.add(basis_id)
        return details

    @staticmethod
    def _source_basis_id(raw_basis: str) -> str:
        if raw_basis in SOURCE_BASIS_DETAIL_LIBRARY:
            return raw_basis
        prefix = "source_basis_id:"
        if raw_basis.startswith(prefix):
            return raw_basis[len(prefix) :].split(";", 1)[0].strip()
        return ""

    @staticmethod
    def _basis_details_complete(details: list[dict[str, Any]]) -> bool:
        if not details:
            return False
        required = (
            "citation_records",
            "reality_mapping",
            "applicable_conditions",
            "parameter_or_method_boundaries",
            "required_field_validation",
            "failure_boundary",
        )
        for detail in details:
            if any(not detail.get(field) for field in required):
                return False
            if not all(record.get("source_url") and record.get("citation_key") for record in detail["citation_records"]):
                return False
        return True

    def _gate_consolidation(self, records: list[dict[str, Any]]) -> dict[str, Any]:
        consumed_sources = [
            "Agent43_FieldReplayCalibrationGate",
            "Agent44_FieldReplayImport",
            "Agent45_FieldReplayEvidenceChain",
            "Agent46_SoftSensorFieldHoldoutGate",
            "Agent58_FieldValidationQueueAlignment",
            "Agent59_ClaimSpecificFieldPackage",
        ]
        blocker_kinds = sorted({blocker.split(":")[0] for record in records for blocker in record["claim_upgrade_blocked_by"]})
        return {
            "consumed_gate_sources": consumed_sources,
            "consumed_gate_source_count": len(consumed_sources),
            "expected_gate_source_count": 6,
            "gate_source_consolidation_coverage": 1.0,
            "duplicate_gate_cluster_resolved_as_interface": True,
            "unified_blocker_kinds": blocker_kinds,
            "field_related_agents_not_deleted": True,
            "consolidation_boundary": (
                "现阶段通过 facade 统一接口压缩重复 gate；不删除历史 Agent43/44/45/46/58/59，避免破坏既有验证链。"
            ),
        }

    def _source_basis_detail_tasks(self) -> list[dict[str, Any]]:
        tasks = self.claim_specific_package_metrics.get("source_basis_completion_tasks", [])
        return [
            {
                **task,
                "routed_to_unified_gate": True,
                "required_before": "field_claim_upgrade_or_release_gate_candidate",
            }
            for task in tasks
        ]

    def _readiness(self, records: list[dict[str, Any]]) -> dict[str, Any]:
        claim_readiness = self.claim_specific_package_metrics.get("readiness", {})
        import_readiness = self.field_replay_import_metrics.get("readiness", {})
        evidence_chain_readiness = self.field_replay_evidence_chain_metrics.get("readiness", {})
        soft_readiness = self.soft_sensor_field_holdout_gate_metrics.get("readiness", {})
        field_import_pass = bool(import_readiness.get("can_pass_to_timestamped_replay"))
        evidence_chain_pass = bool(evidence_chain_readiness.get("can_emit_protective_writeback_candidate"))
        soft_gate_pass = bool(soft_readiness.get("can_write_to_release_gate"))
        source_basis_rate = float(claim_readiness.get("source_basis_completion_rate", 0.0))
        detail_status = self._source_basis_detail_status(records)
        effective_source_basis_traceability = detail_status["citation_detail_completion_rate"]
        can_emit_claim_upgrade = all(
            not record["claim_upgrade_blocked_by"] and record["evidence_stage"].startswith("field_validation")
            for record in records
        )
        score = round(
            0.20 * 1.0
            + 0.08 * source_basis_rate
            + 0.10 * effective_source_basis_traceability
            + 0.18 * float(field_import_pass)
            + 0.16 * float(evidence_chain_pass)
            + 0.16 * float(soft_gate_pass)
            + 0.12 * float(can_emit_claim_upgrade),
            3,
        )
        return {
            "unified_field_evidence_gate_status": "unified_gate_ready_blocking_field_claim_upgrade",
            "unified_field_evidence_gate_score": score,
            "unified_evidence_record_count": len(records),
            "gate_source_consolidation_coverage": 1.0,
            "source_basis_completion_rate": source_basis_rate,
            "citation_detail_completion_rate": detail_status["citation_detail_completion_rate"],
            "source_basis_parameter_boundary_coverage": detail_status["parameter_boundary_coverage"],
            "effective_literature_traceability": effective_source_basis_traceability,
            "field_import_pass": field_import_pass,
            "field_replay_evidence_chain_pass": evidence_chain_pass,
            "soft_sensor_field_holdout_gate_pass": soft_gate_pass,
            "can_emit_field_claim_upgrade": can_emit_claim_upgrade,
            "can_write_to_protective_control": False,
            "can_write_to_release_gate": False,
            "can_write_to_actuator": False,
            "synthetic_boundary_preserved": True,
        }

    @staticmethod
    def _writeback_policy(readiness: dict[str, Any]) -> dict[str, Any]:
        return {
            "allowed_writeback": [
                "unified_claim_blocker_table",
                "unified_field_package_requirements",
                "source_basis_detail_tasks",
                "architecture_consolidation_R1_status",
            ],
            "blocked_writeback": [
                "actuator_policy",
                "release_gate_policy",
                "field_mechanism_claim",
                "field_control_effectiveness_claim",
            ],
            "can_emit_field_claim_upgrade": readiness["can_emit_field_claim_upgrade"],
            "can_write_to_release_gate": False,
            "can_write_to_actuator": False,
            "policy_effect": "R1 interface baseline formed; keep source_basis and field-origin blockers explicit.",
        }

    def _claim_basis_promotion_gate(
        self, records: list[dict[str, Any]], readiness: dict[str, Any]
    ) -> dict[str, Any]:
        rows = [self._claim_basis_promotion_row(record) for record in records]
        ready_count = len(
            [
                row
                for row in rows
                if row["promotion_status"] == "field_supported_candidate_ready_for_human_review"
            ]
        )
        blocked_count = len([row for row in rows if row["promotion_status"] == "blocked"])
        can_emit_field_claim_upgrade = (
            bool(readiness.get("can_emit_field_claim_upgrade"))
            and ready_count == len(rows)
            and blocked_count == 0
            and bool(rows)
        )
        return {
            "gate_id": "R8u178_claim_basis_promotion_gate",
            "gate_status": (
                "claim_basis_promotion_ready_for_field_supported_candidate_review"
                if can_emit_field_claim_upgrade
                else "claim_basis_promotion_blocked_until_field_validation"
            ),
            "evidence_level": "claim_basis_promotion_gate_not_field_evidence",
            "promotion_decision_count": len(rows),
            "ready_promotion_count": ready_count,
            "blocked_promotion_count": blocked_count,
            "can_emit_field_claim_upgrade": can_emit_field_claim_upgrade,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "can_emit_patent_or_legal_conclusion": False,
            "promotion_rows": rows,
            "failure_boundary": (
                "该 gate 只判断统一证据记录是否可升级为 field-supported claim candidate；"
                "即使通过，也不能写 actuator、release gate、专利/法律结论或现场自动放行。"
            ),
        }

    @staticmethod
    def _claim_basis_promotion_row(record: dict[str, Any]) -> dict[str, Any]:
        source_basis = record.get("source_basis_status", {})
        field_import = record.get("field_import_status", {})
        replay_chain = record.get("field_replay_evidence_chain_status", {})
        soft_holdout = record.get("soft_sensor_field_holdout_status", {})
        blockers = list(record.get("claim_upgrade_blocked_by", []))
        field_import_pass = (
            field_import.get("data_origin") == "field"
            and bool(field_import.get("origin_ready"))
            and bool(field_import.get("import_ready"))
        )
        replay_chain_pass = bool(replay_chain.get("can_emit_protective_writeback_candidate"))
        soft_holdout_pass = bool(soft_holdout.get("can_write_to_release_gate"))
        evidence_stage = str(record.get("evidence_stage", ""))
        ready_for_candidate = (
            not blockers
            and field_import_pass
            and replay_chain_pass
            and soft_holdout_pass
            and evidence_stage.startswith("field_validation")
        )
        return {
            "need_id": record.get("need_id", "unknown_need"),
            "field_validation_need": record.get("field_validation_need", ""),
            "promotion_status": (
                "field_supported_candidate_ready_for_human_review"
                if ready_for_candidate
                else "blocked"
            ),
            "allowed_promotion_level": (
                "field_supported_claim_candidate_not_release_or_actuator"
                if ready_for_candidate
                else "no_field_claim_upgrade"
            ),
            "current_basis": {
                "evidence_stage": evidence_stage,
                "source_basis_traceability": (
                    "literature_detail_complete"
                    if source_basis.get("citation_detail_complete")
                    or source_basis.get("detail_library_complete")
                    else "literature_detail_incomplete"
                ),
                "field_import": "passed" if field_import_pass else "not_passed",
                "replay_evidence_chain": "passed" if replay_chain_pass else "not_passed",
                "soft_sensor_holdout": "passed" if soft_holdout_pass else "not_passed",
                "supporting_entries": record.get("supporting_entries", []),
                "replay_gate_ids": record.get("replay_gate_ids", []),
            },
            "not_current_basis": [
                "synthetic_rows_as_field_evidence",
                "template_rows_as_field_evidence",
                "literature_only_rows_as_field_evidence",
                "formal_search_handoff_as_field_evidence",
                "actuator_policy",
                "release_gate_policy",
                "patent_or_legal_conclusion",
            ],
            "blocked_by": blockers,
            "requires_human_review": ready_for_candidate,
            "next_required_gate": (
                "human_review_then_separate_release_and_actuator_gates"
                if ready_for_candidate
                else "import_real_field_package_then_replay_holdout_and_human_review"
            ),
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        }

    @staticmethod
    def _next_refactor_action(readiness: dict[str, Any]) -> dict[str, Any]:
        if readiness["citation_detail_completion_rate"] < 0.8:
            return {
                "action_id": "R1b_source_basis_detail_completion_inside_unified_gate",
                "title": "在统一 evidence gate 内补 source_basis 的 citation、参数范围和适用边界",
                "reason": "统一 gate 已形成，但 source_basis_completion_rate 仍低，claim 仍被文献依据细节阻断。",
                "must_not_do": "不能把 citation detail 当作 field-supported evidence；只能升级 literature-supported traceability。",
            }
        return {
            "action_id": "R2_agent48_51_54_observation_contract_merge",
            "title": "合并稀疏布点、催化剂代理与软传感观测矩阵合同",
            "reason": "field evidence gate 已统一且 source_basis 细节已补齐；下一步回到观测基础链路提升 Agent48/51/54 联动。",
            "must_not_do": "不能仅增加传感器数量，必须保留成本、拓扑和 field label 边界。",
        }

    def _source_basis_detail_status(self, records: list[dict[str, Any]]) -> dict[str, Any]:
        basis_ids = sorted(
            {
                basis_id
                for record in records
                for raw_basis in record["source_basis_status"].get("source_basis", [])
                for basis_id in [self._source_basis_id(str(raw_basis))]
                if basis_id
            }
        )
        detailed = [SOURCE_BASIS_DETAIL_LIBRARY[basis_id] for basis_id in basis_ids if basis_id in SOURCE_BASIS_DETAIL_LIBRARY]
        complete_detail_count = len([detail for detail in detailed if self._basis_details_complete([detail])])
        citation_count = sum(len(detail.get("citation_records", [])) for detail in detailed)
        doi_or_url_count = sum(
            1
            for detail in detailed
            for citation in detail.get("citation_records", [])
            if citation.get("doi") or citation.get("source_url")
        )
        parameter_boundary_count = len([detail for detail in detailed if detail.get("parameter_or_method_boundaries")])
        return {
            "source_basis_ids": basis_ids,
            "source_basis_id_count": len(basis_ids),
            "detail_record_count": len(detailed),
            "complete_detail_count": complete_detail_count,
            "citation_record_count": citation_count,
            "citation_with_doi_or_url_count": doi_or_url_count,
            "citation_detail_completion_rate": round(complete_detail_count / max(1, len(basis_ids)), 3),
            "parameter_boundary_coverage": round(parameter_boundary_count / max(1, len(basis_ids)), 3),
            "field_supported_edge_ratio": 0.0,
            "evidence_stage": "literature_supported_traceability_complete_needs_field_validation",
            "failure_boundary": (
                "source_basis detail 补齐后只代表文献依据、参数边界和适用条件可追溯；"
                "field_supported_edge_ratio 仍为 0，不能升级现场 claim。"
            ),
        }
