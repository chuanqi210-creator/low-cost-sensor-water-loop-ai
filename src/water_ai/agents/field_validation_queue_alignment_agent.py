from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.agents.field_data_interface_agent import FieldDataInterfaceAgent
from water_ai.agents.field_replay_import_agent import FieldReplayImportAgent
from water_ai.agents.timestamped_campaign_replay_agent import TimestampedCampaignReplayAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class FieldValidationQueueAlignmentAgent(BaseAgent):
    """Map KG field-validation needs to concrete field tables, fields and gates."""

    name = "field_validation_queue_alignment_agent"

    def __init__(
        self,
        *,
        field_validation_queue: list[dict[str, object]] | None = None,
        field_data_metrics: dict[str, object] | None = None,
        timestamped_replay_metrics: dict[str, object] | None = None,
        field_replay_import_metrics: dict[str, object] | None = None,
        evidence_chain_metrics: dict[str, object] | None = None,
        control_guardrail_backpropagation_metrics: dict[str, object] | None = None,
    ) -> None:
        self.field_validation_queue = field_validation_queue or []
        self.field_data_metrics = field_data_metrics or {}
        self.timestamped_replay_metrics = timestamped_replay_metrics or {}
        self.field_replay_import_metrics = field_replay_import_metrics or {}
        self.evidence_chain_metrics = evidence_chain_metrics or {}
        self.control_guardrail_backpropagation_metrics = control_guardrail_backpropagation_metrics or {}
        self.field_contract = FieldDataInterfaceAgent.schema_contract()
        self.replay_contract = TimestampedCampaignReplayAgent.replay_schema_contract()

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        mapping_table = self._validation_mapping_table()
        coverage = self._coverage(mapping_table)
        readiness = self._readiness(mapping_table, coverage)
        issues = self._issues(mapping_table, readiness)
        recommendations = self._recommendations(mapping_table, readiness)
        summary = (
            f"现场验证队列对齐：{readiness['field_validation_alignment_status']}；"
            f"table_coverage={readiness['field_need_to_table_coverage']:.3f}，"
            f"gate_coverage={readiness['field_need_to_gate_coverage']:.3f}。"
        )
        confidence = round(
            min(0.92, max(0.18, 0.36 + 0.46 * readiness["field_validation_alignment_score"] - 0.025 * len(issues))),
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
                "validation_mapping_table": mapping_table,
                "field_package_status": self._field_package_status(),
                "coverage": coverage,
                "readiness": readiness,
                "agent50_writeback": self._agent50_writeback(readiness),
            },
        )

    def _validation_mapping_table(self) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for index, item in enumerate(self.field_validation_queue, start=1):
            need = str(item.get("field_validation_need", "")).strip()
            rows.append(
                self._mapping_for_need(
                    need_id=f"FVQ{index:02d}",
                    need=need,
                    supporting_entries=self._list(item.get("supporting_entries")),
                    required_before=str(item.get("required_before", "field_claim_upgrade")),
                )
            )
        rows.extend(self._guardrail_validation_rows(start_index=len(rows) + 1))
        return rows

    def _guardrail_validation_rows(self, *, start_index: int) -> list[dict[str, object]]:
        patches = self.control_guardrail_backpropagation_metrics.get("field_requirement_patch", [])
        if not isinstance(patches, list):
            return []
        rows: list[dict[str, object]] = []
        for offset, patch in enumerate(patches):
            if not isinstance(patch, dict):
                continue
            scenario = str(patch.get("scenario", ""))
            required_fields = self._list(patch.get("required_fields"))
            if scenario == "catalyst_uncertain_low_proxy":
                row = self._row(
                    need_id=f"R4F{start_index + offset:02d}",
                    need="R4 guardrail 催化剂代理不确定现场验证",
                    supporting_entries=["R4_control_guardrail_failure_backpropagation"],
                    required_before="catalyst_control_claim_upgrade",
                    need_type="guardrail_catalyst_proxy_uncertainty_validation",
                    agent30_tables=["catalyst_lifecycle", "offline_lab_results", "sensor_timeseries", "campaign_operation_log"],
                    required_table_fields={
                        "catalyst_lifecycle": [
                            "catalyst_id",
                            "batch_id",
                            "cycle_count",
                            "regen_count",
                            "activity_assay",
                            "pressure_drop_kPa",
                            "lifetime_fraction",
                        ],
                        "offline_lab_results": ["batch_id", "sample_time_min", "analyte", "value", "unit", "method", "qa_flag"],
                        "sensor_timeseries": [
                            "batch_id",
                            "timestamp_min",
                            "cycle_id",
                            "pH",
                            "ORP_mV",
                            "EC_uScm",
                            "turbidity_NTU",
                            "temp_C",
                            "flow_Lmin",
                            "UV254_abs",
                        ],
                        "campaign_operation_log": [
                            "campaign_id",
                            "batch_id",
                            "action_id",
                            "start_min",
                            "end_min",
                            "intake_fraction",
                            "success",
                        ],
                    },
                    optional_promoted_fields={
                        "campaign_operation_log": ["operator_override"],
                        "catalyst_lifecycle": ["surface_pollution_index", "replacement_flag", "regen_method"],
                    },
                    agent42_tables=["sensor_timeseries", "offline_lab_results", "campaign_operation_log"],
                    agent42_timestamp_fields={
                        "sensor_timeseries": ["timestamp_min"],
                        "offline_lab_results": ["sample_time_min", "result_time_min"],
                        "campaign_operation_log": ["command_time_min", "effect_time_min", "start_min", "end_min"],
                    },
                    agent44_metadata_fields=["data_origin", "site_id", "campaign_id", "operator_id", "chain_of_custody_id"],
                    agent43_gate_ids=["G6_1_field_origin", "G6_2_timestamp_schema_ready", "G6_3_batch_linkage_complete", "G6_7_false_positive_cost"],
                    validation_metrics=[
                        "proxy_holdout_label_coverage",
                        "pressure_drop_trend",
                        "regeneration_event_traceability",
                        "catalyst_action_override_rate",
                    ],
                    failure_boundary=str(patch.get("claim_boundary", "field catalyst replay required before claim upgrade.")),
                )
            elif scenario == "hydraulic_delay_violation":
                row = self._row(
                    need_id=f"R4F{start_index + offset:02d}",
                    need="R4 guardrail 水力延迟与池容执行验证",
                    supporting_entries=["R4_control_guardrail_failure_backpropagation"],
                    required_before="recycle_control_claim_upgrade",
                    need_type="guardrail_hydraulic_latency_storage_validation",
                    agent30_tables=["campaign_operation_log", "sensor_timeseries"],
                    required_table_fields={
                        "campaign_operation_log": [
                            "campaign_id",
                            "batch_id",
                            "action_id",
                            "start_min",
                            "end_min",
                            "intake_fraction",
                            "success",
                        ],
                        "sensor_timeseries": [
                            "batch_id",
                            "timestamp_min",
                            "cycle_id",
                            "pH",
                            "ORP_mV",
                            "EC_uScm",
                            "turbidity_NTU",
                            "temp_C",
                            "flow_Lmin",
                            "UV254_abs",
                        ],
                    },
                    optional_promoted_fields={
                        "campaign_operation_log": [
                            "command_time_min",
                            "effect_time_min",
                            "recycle_ratio",
                            "validation_minutes",
                            "operator_override",
                        ]
                    },
                    agent42_tables=["campaign_operation_log", "sensor_timeseries", "fast_proxy_event_log"],
                    agent42_timestamp_fields={
                        "campaign_operation_log": ["command_time_min", "effect_time_min", "start_min", "end_min"],
                        "sensor_timeseries": ["timestamp_min"],
                        "fast_proxy_event_log": ["event_time_min", "lab_label_time_min"],
                    },
                    agent44_metadata_fields=["data_origin", "site_id", "campaign_id", "operator_id", "chain_of_custody_id"],
                    agent43_gate_ids=[
                        "G6_1_field_origin",
                        "G6_2_timestamp_schema_ready",
                        "G6_3_batch_linkage_complete",
                        "G6_6_latency_action_margin",
                    ],
                    validation_metrics=[
                        "tank_storage_margin_coverage",
                        "actuator_latency_p90_min",
                        "pump_valve_success_rate",
                        "recycle_ratio_traceability",
                    ],
                    failure_boundary=str(patch.get("claim_boundary", "field hydraulic replay required before claim upgrade.")),
                )
            else:
                row = self._mapping_for_need(
                    need_id=f"R4F{start_index + offset:02d}",
                    need=f"R4 guardrail 未映射场景 {scenario}",
                    supporting_entries=["R4_control_guardrail_failure_backpropagation"],
                    required_before="field_claim_upgrade",
                )
            row = {
                **row,
                "guardrail_patch_consumed": True,
                "guardrail_source_scenario": scenario,
                "guardrail_required_fields": required_fields,
                "guardrail_missing_schema_fields": self._missing_guardrail_schema_fields(required_fields),
                "guardrail_claim_boundary": patch.get("claim_boundary", ""),
            }
            rows.append(row)
        return rows

    def _mapping_for_need(
        self,
        *,
        need_id: str,
        need: str,
        supporting_entries: list[str],
        required_before: str,
    ) -> dict[str, object]:
        token = need.lower()
        if any(key in token for key in ("漂移", "传感", "sensor", "drift")):
            return self._row(
                need_id=need_id,
                need=need,
                supporting_entries=supporting_entries,
                required_before=required_before,
                need_type="sensor_drift_and_low_cost_signal_validity",
                agent30_tables=["sensor_timeseries"],
                required_table_fields={
                    "sensor_timeseries": [
                        "batch_id",
                        "timestamp_min",
                        "cycle_id",
                        "pH",
                        "ORP_mV",
                        "EC_uScm",
                        "turbidity_NTU",
                        "temp_C",
                        "flow_Lmin",
                        "UV254_abs",
                    ]
                },
                optional_promoted_fields={
                    "sensor_timeseries": ["sensor_status", "instrument_id", "acquisition_time_min", "ingest_time_min"]
                },
                agent42_tables=["sensor_timeseries"],
                agent42_timestamp_fields={"sensor_timeseries": ["timestamp_min"]},
                agent44_metadata_fields=["data_origin", "site_id", "instrument_snapshot_id", "chain_of_custody_id"],
                agent43_gate_ids=["G6_1_field_origin", "G6_2_timestamp_schema_ready", "G6_3_batch_linkage_complete"],
                validation_metrics=[
                    "sensor_drift_rate",
                    "timestamp_coverage",
                    "sensor_status_coverage",
                    "batch_linkage_status",
                ],
                failure_boundary="真实漂移记录只能校准 sensor_confidence 和软传感不确定性；不能单独授权 release gate。",
            )
        if any(key in token for key in ("检测限", "低浓度", "limit", "detection")):
            return self._row(
                need_id=need_id,
                need=need,
                supporting_entries=supporting_entries,
                required_before=required_before,
                need_type="low_concentration_detection_limit_for_target_pollutants",
                agent30_tables=["offline_lab_results"],
                required_table_fields={
                    "offline_lab_results": [
                        "batch_id",
                        "sample_time_min",
                        "analyte",
                        "value",
                        "unit",
                        "method",
                        "qa_flag",
                    ]
                },
                optional_promoted_fields={
                    "offline_lab_results": ["detection_limit", "result_time_min", "sample_source", "replicate_id"]
                },
                agent42_tables=["offline_lab_results"],
                agent42_timestamp_fields={"offline_lab_results": ["sample_time_min", "result_time_min"]},
                agent44_metadata_fields=["data_origin", "site_id", "campaign_id", "chain_of_custody_id"],
                agent43_gate_ids=["G6_1_field_origin", "G6_2_timestamp_schema_ready", "G6_3_batch_linkage_complete"],
                validation_metrics=[
                    "detection_limit_coverage",
                    "qa_pass_rate",
                    "low_concentration_label_count",
                    "lab_turnaround_p90_min",
                ],
                failure_boundary="检测限缺失时不能把低浓度残留或达标放行升级为现场结论；只能作为待验证 claim。",
            )
        if any(key in token for key in ("离线", "放行", "标签", "lab", "release", "label")):
            return self._row(
                need_id=need_id,
                need=need,
                supporting_entries=supporting_entries,
                required_before=required_before,
                need_type="offline_release_label_for_soft_sensor_and_claim_gate",
                agent30_tables=["offline_lab_results"],
                required_table_fields={
                    "offline_lab_results": [
                        "batch_id",
                        "sample_time_min",
                        "analyte",
                        "value",
                        "unit",
                        "method",
                        "qa_flag",
                    ]
                },
                optional_promoted_fields={"offline_lab_results": ["result_time_min", "detection_limit", "sample_source"]},
                agent42_tables=["offline_lab_results"],
                agent42_timestamp_fields={"offline_lab_results": ["sample_time_min", "result_time_min"]},
                agent44_metadata_fields=["data_origin", "site_id", "campaign_id", "chain_of_custody_id"],
                agent43_gate_ids=["G6_1_field_origin", "G6_2_timestamp_schema_ready", "G6_3_batch_linkage_complete"],
                validation_metrics=[
                    "field_holdout_label_count",
                    "soft_sensor_interval_coverage",
                    "release_label_precision",
                    "lab_turnaround_p90_min",
                ],
                failure_boundary="离线放行标签只能支持软传感校准和人工审核；release gate 仍需独立 conformal/field holdout 门控。",
            )
        if any(key in token for key in ("催化", "再生", "活性", "catalyst", "regen", "activity")):
            return self._row(
                need_id=need_id,
                need=need,
                supporting_entries=supporting_entries,
                required_before=required_before,
                need_type="catalyst_activity_and_lifecycle_validation",
                agent30_tables=["catalyst_lifecycle", "offline_lab_results"],
                required_table_fields={
                    "catalyst_lifecycle": [
                        "catalyst_id",
                        "batch_id",
                        "cycle_count",
                        "regen_count",
                        "activity_assay",
                        "pressure_drop_kPa",
                        "lifetime_fraction",
                    ],
                    "offline_lab_results": ["batch_id", "sample_time_min", "analyte", "value", "unit", "method", "qa_flag"],
                },
                optional_promoted_fields={"catalyst_lifecycle": ["surface_pollution_index", "replacement_flag", "regen_method"]},
                agent42_tables=["offline_lab_results"],
                agent42_timestamp_fields={"offline_lab_results": ["sample_time_min", "result_time_min"]},
                agent44_metadata_fields=["data_origin", "site_id", "campaign_id", "chain_of_custody_id"],
                agent43_gate_ids=["G6_1_field_origin", "G6_3_batch_linkage_complete"],
                validation_metrics=[
                    "activity_assay_coverage",
                    "pressure_drop_trend",
                    "post_regen_response_gain",
                    "byproduct_label_count",
                ],
                failure_boundary="催化剂代理变量未通过 field holdout 前，不能解除 Agent49 的 catalyst uncertainty 保护性阻断。",
            )
        if any(key in token for key in ("循环", "回流", "停留", "动作", "药剂", "执行", "control", "recycle", "dose")):
            return self._row(
                need_id=need_id,
                need=need,
                supporting_entries=supporting_entries,
                required_before=required_before,
                need_type="operation_action_and_closed_loop_validation",
                agent30_tables=["campaign_operation_log", "offline_lab_results"],
                required_table_fields={
                    "campaign_operation_log": [
                        "campaign_id",
                        "batch_id",
                        "action_id",
                        "start_min",
                        "end_min",
                        "intake_fraction",
                        "success",
                    ],
                    "offline_lab_results": ["batch_id", "sample_time_min", "analyte", "value", "unit", "method", "qa_flag"],
                },
                optional_promoted_fields={
                    "campaign_operation_log": [
                        "command_time_min",
                        "effect_time_min",
                        "recycle_ratio",
                        "dose_factor",
                        "validation_minutes",
                    ]
                },
                agent42_tables=["campaign_operation_log", "offline_lab_results", "fast_proxy_event_log"],
                agent42_timestamp_fields={
                    "campaign_operation_log": ["command_time_min", "effect_time_min", "start_min", "end_min"],
                    "offline_lab_results": ["sample_time_min", "result_time_min"],
                    "fast_proxy_event_log": ["event_time_min", "lab_label_time_min"],
                },
                agent44_metadata_fields=["data_origin", "site_id", "campaign_id", "operator_id", "chain_of_custody_id"],
                agent43_gate_ids=[
                    "G6_1_field_origin",
                    "G6_2_timestamp_schema_ready",
                    "G6_3_batch_linkage_complete",
                    "G6_6_latency_action_margin",
                    "G6_7_false_positive_cost",
                ],
                validation_metrics=[
                    "state_action_reward_replay_coverage",
                    "actuator_latency_p90_min",
                    "protective_action_lead_time_min",
                    "false_positive_cost_index",
                ],
                failure_boundary="闭环动作回放通过也只产生保护性写回候选；执行器策略仍需人工复核和工程窗口确认。",
            )
        return self._row(
            need_id=need_id,
            need=need,
            supporting_entries=supporting_entries,
            required_before=required_before,
            need_type="unmapped_validation_need",
            agent30_tables=[],
            required_table_fields={},
            optional_promoted_fields={},
            agent42_tables=[],
            agent42_timestamp_fields={},
            agent44_metadata_fields=[],
            agent43_gate_ids=[],
            validation_metrics=[],
            failure_boundary="该验证需求尚未映射到现场数据接口，不能升级任何 claim。",
        )

    def _row(
        self,
        *,
        need_id: str,
        need: str,
        supporting_entries: list[str],
        required_before: str,
        need_type: str,
        agent30_tables: list[str],
        required_table_fields: dict[str, list[str]],
        optional_promoted_fields: dict[str, list[str]],
        agent42_tables: list[str],
        agent42_timestamp_fields: dict[str, list[str]],
        agent44_metadata_fields: list[str],
        agent43_gate_ids: list[str],
        validation_metrics: list[str],
        failure_boundary: str,
    ) -> dict[str, object]:
        field_checks = self._field_contract_checks(required_table_fields, optional_promoted_fields)
        replay_checks = self._replay_contract_checks(agent42_tables, agent42_timestamp_fields)
        metadata_missing = sorted(set(agent44_metadata_fields) - set(FieldReplayImportAgent.REQUIRED_METADATA_FIELDS))
        return {
            "need_id": need_id,
            "field_validation_need": need,
            "need_type": need_type,
            "supporting_entries": supporting_entries,
            "required_before": required_before,
            "agent30_tables": agent30_tables,
            "required_table_fields": required_table_fields,
            "optional_fields_promoted_for_claim": optional_promoted_fields,
            "field_contract_check": field_checks,
            "agent42_replay_tables": agent42_tables,
            "agent42_timestamp_fields": agent42_timestamp_fields,
            "replay_contract_check": replay_checks,
            "agent44_metadata_fields": agent44_metadata_fields,
            "metadata_contract_check": {
                "metadata_fields_available": not metadata_missing,
                "missing_metadata_fields": metadata_missing,
            },
            "agent43_gate_ids": agent43_gate_ids,
            "agent45_chain_stages": [
                "FieldReplayImportAgent",
                "TimestampedCampaignReplayAgent",
                "FieldReplayCalibrationGateAgent",
                "FieldReplayEvidenceChainAgent",
            ]
            if agent42_tables or agent43_gate_ids
            else [],
            "validation_metrics": validation_metrics,
            "schema_extension_required": bool(field_checks["optional_fields_promoted_for_claim"]),
            "mapped_to_field_tables": bool(agent30_tables) and bool(field_checks["all_required_fields_available"]),
            "mapped_to_replay_or_gate": bool(agent42_tables or agent43_gate_ids),
            "claim_upgrade_blocked": True,
            "writeback_boundary": "field_validation_mapping_only_no_actuator_or_release_gate",
            "failure_boundary": failure_boundary,
        }

    def _field_contract_checks(
        self,
        required_table_fields: dict[str, list[str]],
        optional_promoted_fields: dict[str, list[str]],
    ) -> dict[str, object]:
        missing_tables = sorted(table for table in required_table_fields if table not in self.field_contract)
        missing_required: dict[str, list[str]] = {}
        promoted_available: dict[str, list[str]] = {}
        for table, fields in required_table_fields.items():
            spec = self.field_contract.get(table, {})
            required = set(self._list(spec.get("required_fields")))
            optional = set(self._list(spec.get("optional_fields")))
            missing_required[table] = sorted(field for field in fields if field not in required and field not in optional)
            promoted_available[table] = sorted(
                field
                for field in optional_promoted_fields.get(table, [])
                if field in optional and field not in required
            )
        return {
            "missing_tables": missing_tables,
            "missing_required_fields": {table: fields for table, fields in missing_required.items() if fields},
            "optional_fields_promoted_for_claim": {
                table: fields for table, fields in promoted_available.items() if fields
            },
            "all_required_fields_available": not missing_tables and not any(missing_required.values()),
        }

    def _replay_contract_checks(
        self,
        agent42_tables: list[str],
        agent42_timestamp_fields: dict[str, list[str]],
    ) -> dict[str, object]:
        missing_tables = sorted(table for table in agent42_tables if table not in self.replay_contract)
        missing_timestamp_fields: dict[str, list[str]] = {}
        for table, fields in agent42_timestamp_fields.items():
            spec = self.replay_contract.get(table, {})
            timestamps = set(self._list(spec.get("timestamp_fields")))
            missing_timestamp_fields[table] = sorted(field for field in fields if field not in timestamps)
        return {
            "missing_replay_tables": missing_tables,
            "missing_timestamp_fields": {
                table: fields for table, fields in missing_timestamp_fields.items() if fields
            },
            "all_replay_fields_available": not missing_tables and not any(missing_timestamp_fields.values()),
        }

    def _coverage(self, mapping_table: list[dict[str, object]]) -> dict[str, object]:
        total = len(mapping_table)
        table_mapped = sum(1 for row in mapping_table if row["mapped_to_field_tables"])
        gate_mapped = sum(1 for row in mapping_table if row["mapped_to_replay_or_gate"])
        unmapped = [row for row in mapping_table if row["need_type"] == "unmapped_validation_need"]
        schema_extensions = [row for row in mapping_table if row["schema_extension_required"]]
        guardrail_rows = [row for row in mapping_table if row.get("guardrail_patch_consumed")]
        guardrail_required_fields = [
            field for row in guardrail_rows for field in self._list(row.get("guardrail_required_fields"))
        ]
        guardrail_missing_schema_fields = sorted(
            {field for row in guardrail_rows for field in self._list(row.get("guardrail_missing_schema_fields"))}
        )
        field_contract_ok = sum(
            1
            for row in mapping_table
            if self._dict(row.get("field_contract_check")).get("all_required_fields_available") is True
        )
        replay_contract_ok = sum(
            1
            for row in mapping_table
            if self._dict(row.get("replay_contract_check")).get("all_replay_fields_available") is True
        )
        return {
            "validation_need_count": total,
            "table_mapped_count": table_mapped,
            "gate_mapped_count": gate_mapped,
            "field_contract_ok_count": field_contract_ok,
            "replay_contract_ok_count": replay_contract_ok,
            "schema_extension_required_count": len(schema_extensions),
            "unmapped_validation_need_count": len(unmapped),
            "guardrail_requirement_patch_count": len(guardrail_rows),
            "guardrail_required_field_count": len(set(guardrail_required_fields)),
            "guardrail_missing_schema_field_count": len(guardrail_missing_schema_fields),
            "guardrail_missing_schema_fields": guardrail_missing_schema_fields,
            "field_requirement_patch_consumption_rate": round(
                len(guardrail_rows)
                / max(
                    1,
                    len(
                        self.control_guardrail_backpropagation_metrics.get("field_requirement_patch", [])
                        if isinstance(
                            self.control_guardrail_backpropagation_metrics.get("field_requirement_patch", []),
                            list,
                        )
                        else []
                    ),
                ),
                3,
            ),
            "claim_upgrade_blocker_count": sum(1 for row in mapping_table if row["claim_upgrade_blocked"]),
            "field_need_to_table_coverage": round(table_mapped / max(1, total), 3),
            "field_need_to_gate_coverage": round(gate_mapped / max(1, total), 3),
            "field_contract_coverage": round(field_contract_ok / max(1, total), 3),
            "replay_contract_coverage": round(replay_contract_ok / max(1, total), 3),
            "unmapped_need_ids": [row["need_id"] for row in unmapped],
            "schema_extension_need_ids": [row["need_id"] for row in schema_extensions],
        }

    def _readiness(
        self,
        mapping_table: list[dict[str, object]],
        coverage: dict[str, object],
    ) -> dict[str, object]:
        field_status = self._field_package_status()
        total = int(coverage["validation_need_count"])
        table_coverage = float(coverage["field_need_to_table_coverage"])
        gate_coverage = float(coverage["field_need_to_gate_coverage"])
        field_contract_coverage = float(coverage["field_contract_coverage"])
        replay_contract_coverage = float(coverage["replay_contract_coverage"])
        no_unmapped = int(coverage["unmapped_validation_need_count"]) == 0 and total > 0
        import_ready = field_status["field_replay_import_ready"] is True
        evidence_chain_ready = field_status["field_replay_evidence_chain_ready"] is True
        score = round(
            0.30 * table_coverage
            + 0.24 * gate_coverage
            + 0.18 * field_contract_coverage
            + 0.14 * replay_contract_coverage
            + 0.08 * float(no_unmapped)
            + 0.03 * float(import_ready)
            + 0.03 * float(evidence_chain_ready),
            3,
        )
        if total == 0:
            status = "field_validation_alignment_empty_queue"
        elif not no_unmapped:
            status = "field_validation_alignment_incomplete"
        elif evidence_chain_ready:
            status = "field_validation_alignment_field_chain_ready_for_human_review"
        else:
            status = "field_validation_alignment_ready_needs_real_field_package"
        return {
            "field_validation_alignment_status": status,
            "field_validation_alignment_score": score,
            "field_need_to_table_coverage": table_coverage,
            "field_need_to_gate_coverage": gate_coverage,
            "field_contract_coverage": field_contract_coverage,
            "replay_contract_coverage": replay_contract_coverage,
            "unmapped_validation_need_count": int(coverage["unmapped_validation_need_count"]),
            "schema_extension_required_count": int(coverage["schema_extension_required_count"]),
            "guardrail_requirement_patch_count": int(coverage["guardrail_requirement_patch_count"]),
            "guardrail_required_field_count": int(coverage["guardrail_required_field_count"]),
            "guardrail_missing_schema_field_count": int(coverage["guardrail_missing_schema_field_count"]),
            "field_requirement_patch_consumption_rate": float(coverage["field_requirement_patch_consumption_rate"]),
            "claim_upgrade_blocker_count": int(coverage["claim_upgrade_blocker_count"]),
            "can_update_agent50_priority": total > 0 and no_unmapped and table_coverage >= 0.95 and gate_coverage >= 0.95,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "next_recommended_core_action": "claim_specific_field_package_or_source_basis_completion",
        }

    def _field_package_status(self) -> dict[str, object]:
        field_readiness = self._dict(self.field_data_metrics.get("readiness"))
        timestamp_readiness = self._dict(self.timestamped_replay_metrics.get("readiness"))
        import_readiness = self._dict(self.field_replay_import_metrics.get("readiness"))
        chain_readiness = self._dict(self.evidence_chain_metrics.get("readiness"))
        patches = self.control_guardrail_backpropagation_metrics.get("field_requirement_patch", [])
        patch_count = len(patches) if isinstance(patches, list) else 0
        return {
            "field_data_interface_status": field_readiness.get("interface_status", "not_available"),
            "field_data_origin": field_readiness.get("data_origin", self.field_data_metrics.get("data_origin", "unknown")),
            "timestamped_replay_status": timestamp_readiness.get("timestamped_replay_status", "not_available"),
            "field_replay_import_status": import_readiness.get("field_replay_import_status", "not_available"),
            "field_replay_import_ready": bool(import_readiness.get("can_pass_to_timestamped_replay", False)),
            "field_replay_evidence_chain_status": chain_readiness.get("field_replay_evidence_chain_status", "not_available"),
            "field_replay_evidence_chain_ready": bool(chain_readiness.get("can_emit_protective_writeback_candidate", False)),
            "release_gate_boundary_preserved": chain_readiness.get("can_write_to_release_gate", False) is False,
            "guardrail_requirement_patch_count": patch_count,
        }

    def _issues(
        self,
        mapping_table: list[dict[str, object]],
        readiness: dict[str, object],
    ) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        if not mapping_table:
            issues.append(
                QualityIssue(
                    sensor="field_validation_queue",
                    issue_type="field_validation_queue_empty",
                    severity=Severity.WARNING,
                    message="Agent56 没有输出可对齐的 field_validation_queue，不能升级 KG claim。",
                    evidence=readiness,
                )
            )
        for row in mapping_table:
            if row["need_type"] == "unmapped_validation_need":
                issues.append(
                    QualityIssue(
                        sensor=str(row["need_id"]),
                        issue_type="field_validation_need_unmapped",
                        severity=Severity.WARNING,
                        message=f"验证需求 `{row['field_validation_need']}` 未映射到 Agent30/42/44/45。",
                        evidence=row,
                    )
                )
            if row["schema_extension_required"]:
                issues.append(
                    QualityIssue(
                        sensor=str(row["need_id"]),
                        issue_type="claim_specific_optional_fields_promoted",
                        severity=Severity.INFO,
                        message="该 claim 需要把当前 optional 字段提升为本验证任务的必采字段。",
                        evidence={
                            "field_validation_need": row["field_validation_need"],
                            "optional_fields_promoted_for_claim": row["optional_fields_promoted_for_claim"],
                        },
                    )
                )
            if row.get("guardrail_missing_schema_fields"):
                issues.append(
                    QualityIssue(
                        sensor=str(row["need_id"]),
                        issue_type="guardrail_field_schema_extension_required",
                        severity=Severity.INFO,
                        message="R4 guardrail patch 中的部分必采字段尚不在当前 Agent30/42 field schema 内，需要后续扩展数据接口。",
                        evidence={
                            "field_validation_need": row["field_validation_need"],
                            "guardrail_missing_schema_fields": row["guardrail_missing_schema_fields"],
                        },
                    )
                )
        if readiness["claim_upgrade_blocker_count"] > 0:
            issues.append(
                QualityIssue(
                    sensor="field_validation_alignment",
                    issue_type="field_package_required_before_claim_upgrade",
                    severity=Severity.INFO,
                    message="验证需求已映射到接口，但没有真实 field 包和证据链前仍不能升级为现场结论。",
                    evidence=readiness,
                )
            )
        if readiness["can_write_to_actuator"] or readiness["can_write_to_release_gate"]:
            issues.append(
                QualityIssue(
                    sensor="field_validation_alignment",
                    issue_type="alignment_writeback_boundary_violation",
                    severity=Severity.CRITICAL,
                    message="验证队列对齐 Agent 不得写执行器或 release gate。",
                    evidence=readiness,
                )
            )
        return issues

    @staticmethod
    def _recommendations(mapping_table: list[dict[str, object]], readiness: dict[str, object]) -> list[str]:
        if not mapping_table:
            return [
                "先重跑 Agent56 或补 KG validation need，再执行现场接口对齐。",
                "不要把空验证队列当作 KG field-supported 证据。",
            ]
        recs = [
            "按 validation_mapping_table 生成现场采集优先级：先保证 sensor_timeseries、offline_lab_results 与 metadata provenance，再进入 replay gate。",
            "optional_fields_promoted_for_claim 中的字段在通用 schema 里虽是可选，但对对应 claim 必须作为必采字段处理。",
            "Agent58 只负责把验证需求落到表、字段、gate 和指标；没有真实 field 包时不允许升级现场结论、执行器策略或 release gate。",
        ]
        if readiness["unmapped_validation_need_count"]:
            recs.append("仍有未映射验证需求，优先补映射规则或扩展 Agent30/42 schema。")
        if readiness.get("guardrail_missing_schema_field_count", 0):
            recs.append("R4b 已把 control guardrail field patches 接入 Agent58；下一步应补齐 guardrail_missing_schema_fields 对应的数据接口字段。")
        elif readiness.get("guardrail_requirement_patch_count", 0):
            recs.append("R5 已覆盖 R4 guardrail 必采字段；下一步应转向真实 field package 导入、source_basis 细节和 replay 证据链。")
        return recs

    @staticmethod
    def _method_contract() -> dict[str, object]:
        return {
            "upgrade_id": "P9_field_validation_queue_alignment",
            "borrowed_from": [
                "evidence-before-claims workflow",
                "model validation provenance gates",
                "timestamped campaign replay and G6/P6 field gate",
                "claim-specific data dictionary governance",
            ],
            "reality_mapping": "把 KG 提出的 field_validation_need 从笼统阻塞项变成 Agent30 数据表、Agent42 时间戳 replay、Agent44 metadata provenance、Agent43/45 证据链 gate 和验收指标。",
            "data_needs": [
                "field_validation_queue",
                "field_data_schema_contract",
                "timestamped_replay_schema_contract",
                "field_replay_import_metadata",
                "field_replay_evidence_chain_status",
            ],
            "implementation_path": [
                "src/water_ai/agents/field_validation_queue_alignment_agent.py",
                "experiments/run_agent58_field_validation_queue_alignment.py",
                "outputs/field_validation_queue_alignment/field_validation_queue_alignment_metrics.json",
            ],
            "evaluation_metrics": [
                "field_need_to_table_coverage",
                "field_need_to_gate_coverage",
                "unmapped_validation_need_count",
                "schema_extension_required_count",
                "claim_upgrade_blocker_count",
            ],
            "failure_boundary": "验证队列对齐只能说明需要采哪些字段、通过哪些 gate；没有真实 field 包和证据链通过时，不能证明现场有效或授权执行器/release gate。",
        }

    @staticmethod
    def _agent50_writeback(readiness: dict[str, object]) -> dict[str, object]:
        return {
            "allowed_writeback": [
                "field_validation_mapping_table",
                "claim_specific_required_field_patch",
                "P9_completion_status_for_governance",
            ],
            "blocked_writeback": [
                "actuator_policy",
                "release_gate_policy",
                "field_mechanism_claim",
                "field_control_effectiveness_claim",
            ],
            "can_advance_governance_priority": bool(readiness["can_update_agent50_priority"]),
            "policy_effect": (
                "move_to_claim_specific_field_package_or_source_basis_completion"
                if readiness["can_update_agent50_priority"]
                else "keep_P9_until_validation_needs_are_mapped"
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

    def _missing_guardrail_schema_fields(self, fields: list[str]) -> list[str]:
        schema_fields: set[str] = set()
        for spec in self.field_contract.values():
            schema_fields.update(self._list(spec.get("required_fields")))
            schema_fields.update(self._list(spec.get("optional_fields")))
        normalized_fields = {field.split(":", 1)[1] if ":" in field else field for field in fields}
        return sorted(field for field in normalized_fields if field not in schema_fields)
