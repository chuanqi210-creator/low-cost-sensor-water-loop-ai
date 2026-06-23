from __future__ import annotations

import csv
import json
from pathlib import Path
from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.agents.timestamped_campaign_replay_agent import TimestampedCampaignReplayAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


R7J_CATALYST_PROXY_TEMPLATE_HEADERS = {
    "sensor_timeseries": [
        "sensor_status",
        "instrument_id",
        "acquisition_time_min",
        "ingest_time_min",
    ],
    "node_modality_sensor_timeseries": [
        "batch_id",
        "timestamp_min",
        "node_id",
        "zone",
        "modality",
        "value",
        "sensor_status",
        "instrument_id",
        "acquisition_time_min",
        "ingest_time_min",
    ],
    "offline_lab_results": ["lab_label_time_min", "detection_limit", "method", "unit"],
    "site_topology_or_bed_geometry": ["node_id", "bed_volume", "nominal_HRT_min", "flow_Lmin"],
}

R8U66_FIELD_PATH_ENDPOINT_TEMPLATE_HEADERS = {
    "node_modality_sensor_timeseries": [
        "layout_id",
        "availability_mask",
        "time_since_last_observed_min",
        "data_origin",
        "sensor_value",
    ],
    "site_topology_or_bed_geometry": [
        "site_id",
        "zone",
        "upstream_node_id",
        "downstream_node_id",
        "path_stage_id",
        "hydraulic_path_role",
        "nominal_flow_Lmin",
        "nominal_HRT_min",
        "recycle_ratio",
        "release_boundary_flag",
        "recirculation_loop_flag",
    ],
    "hydraulic_path_stage_labels": [
        "batch_id",
        "layout_id",
        "node_id",
        "zone",
        "path_stage_id",
        "hydraulic_path_role",
        "stage_coverage_label",
        "direct_path_stage_coverage_label",
        "proxy_path_stage_coverage_label",
        "label_source",
        "reviewer_id",
        "review_time_min",
    ],
    "final_effluent_endpoint_labels": [
        "batch_id",
        "endpoint_node_id",
        "sample_time_min",
        "final_effluent_direct_observed",
        "release_gate_label",
        "release_risk_label",
        "analyte",
        "value",
        "unit",
        "qa_flag",
        "reviewer_id",
    ],
    "campaign_operation_log": [
        "operator_override",
    ],
    "offline_lab_results": [
        "sample_source",
    ],
}


class FieldReplayImportAgent(BaseAgent):
    """Validate and normalize real field replay packages before timestamped replay."""

    name = "field_replay_import_agent"

    REQUIRED_METADATA_FIELDS = [
        "data_origin",
        "site_id",
        "campaign_id",
        "sampling_start",
        "sampling_end",
        "operator_id",
        "instrument_snapshot_id",
        "chain_of_custody_id",
    ]

    NUMERIC_FIELDS = {
        "sensor_timeseries": [
            "timestamp_min",
            "EC_uScm",
            "turbidity_NTU",
            "UV254_abs",
            "pH",
            "ORP_mV",
            "flow_Lmin",
            "acquisition_time_min",
            "ingest_time_min",
            "pressure_drop_kPa",
            "headloss_kPa_per_m",
            "bed_inlet_pressure_kPa",
            "bed_outlet_pressure_kPa",
        ],
        "node_modality_sensor_timeseries": ["timestamp_min", "value", "acquisition_time_min", "ingest_time_min"],
        "offline_lab_results": ["sample_time_min", "result_time_min", "value", "lab_label_time_min"],
        "campaign_operation_log": [
            "command_time_min",
            "effect_time_min",
            "start_min",
            "end_min",
            "recycle_ratio",
            "tank_storage_margin",
            "actuator_latency_p90",
            "hold_time_min",
        ],
        "fast_proxy_event_log": [
            "event_time_min",
            "proxy_score",
            "specificity_guard_score",
            "lab_label_time_min",
            "false_positive_cost_index",
        ],
        "pressure_headloss_event_log": [
            "event_time_min",
            "pressure_drop_kPa",
            "headloss_kPa_per_m",
            "flow_Lmin",
            "matched_lab_sample_time_min",
            "flow_normalized_pressure_residual",
            "expected_clean_bed_pressure_drop_kPa",
        ],
    }

    BOOLEAN_FIELDS = {
        "offline_lab_results": ["proxy_holdout_label", "pressure_headloss_proxy_label"],
        "campaign_operation_log": ["regeneration_event", "pressure_headloss_review_required"],
        "fast_proxy_event_log": ["protective_triggered", "field_label_matrix_shock"],
        "pressure_headloss_event_log": ["regeneration_event", "hydraulic_anomaly_label", "operator_review_required"],
    }

    PLACEHOLDER_TOKENS = {"todo", "tbd", "template", "replace_me", "placeholder", "填入", "待填", "示例"}

    def __init__(
        self,
        *,
        metadata: dict[str, object] | None = None,
        raw_tables: dict[str, list[dict[str, object]]] | None = None,
        expected_data_origin: str = "field",
    ) -> None:
        self.metadata = metadata or {}
        self.raw_tables = raw_tables or {}
        self.expected_data_origin = expected_data_origin
        self.contract = TimestampedCampaignReplayAgent.replay_schema_contract()

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        metadata_audit = self._metadata_audit()
        table_audit, normalized_datasets = self._table_import_audit()
        linkage_audit = self._linkage_audit(normalized_datasets)
        readiness = self._readiness(metadata_audit, table_audit, linkage_audit)
        export_policy = self._export_policy(readiness)
        issues = self._issues(metadata_audit, table_audit, linkage_audit, readiness)
        recommendations = self._recommendations(readiness)
        summary = (
            f"现场 replay 导入门：{readiness['field_replay_import_status']}；"
            f"表验收 {readiness['accepted_table_count']}/{readiness['total_table_count']}，"
            f"可进入 timestamped replay {readiness['can_pass_to_timestamped_replay']}。"
        )
        confidence = round(
            min(0.9, max(0.15, 0.34 + 0.42 * readiness["field_replay_import_score"] - 0.025 * len(issues))),
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
                "import_schema_contract": self._import_schema_contract(),
                "metadata": self.metadata,
                "metadata_audit": metadata_audit,
                "table_import_audit": table_audit,
                "linkage_audit": linkage_audit,
                "normalized_datasets": normalized_datasets,
                "readiness": readiness,
                "export_policy": export_policy,
            },
        )

    def _metadata_audit(self) -> dict[str, object]:
        missing_required = [
            field
            for field in self.REQUIRED_METADATA_FIELDS
            if self._is_missing_value(self.metadata.get(field))
        ]
        data_origin = str(self.metadata.get("data_origin", "missing")).lower()
        origin_ready = data_origin == self.expected_data_origin
        status = "metadata_ready"
        if not self.metadata:
            status = "metadata_missing"
        elif missing_required:
            status = "metadata_required_fields_missing"
        elif not origin_ready:
            status = "non_field_origin_blocked"
        return {
            "status": status,
            "data_origin": data_origin,
            "expected_data_origin": self.expected_data_origin,
            "origin_ready": origin_ready,
            "missing_required_fields": missing_required,
            "provenance_fields": {
                "site_id": self.metadata.get("site_id"),
                "campaign_id": self.metadata.get("campaign_id"),
                "operator_id": self.metadata.get("operator_id"),
                "instrument_snapshot_id": self.metadata.get("instrument_snapshot_id"),
                "chain_of_custody_id": self.metadata.get("chain_of_custody_id"),
            },
        }

    def _table_import_audit(self) -> tuple[dict[str, dict[str, object]], dict[str, list[dict[str, object]]]]:
        audit: dict[str, dict[str, object]] = {}
        normalized: dict[str, list[dict[str, object]]] = {}
        for table, spec in self.contract.items():
            rows = self.raw_tables.get(table, [])
            required_fields = [str(field) for field in spec["required_fields"]]
            missing_required = sorted(
                field
                for field in required_fields
                if not rows or any(self._is_missing_value(row.get(field)) for row in rows)
            )
            normalized_rows, type_errors = self._normalize_rows(table, rows)
            normalized[table] = normalized_rows
            status = self._table_status(rows, missing_required, type_errors)
            audit[table] = {
                "record_count": len(rows),
                "normalized_record_count": len(normalized_rows),
                "required_fields": required_fields,
                "missing_required_fields": missing_required,
                "numeric_fields": self.NUMERIC_FIELDS.get(table, []),
                "boolean_fields": self.BOOLEAN_FIELDS.get(table, []),
                "type_errors": type_errors,
                "status": status,
            }
        return audit, normalized

    def _normalize_rows(self, table: str, rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
        normalized_rows: list[dict[str, object]] = []
        errors: list[dict[str, object]] = []
        numeric_fields = set(self.NUMERIC_FIELDS.get(table, []))
        boolean_fields = set(self.BOOLEAN_FIELDS.get(table, []))
        for index, row in enumerate(rows):
            normalized = dict(row)
            for field in numeric_fields:
                if field not in row:
                    continue
                parsed, message = self._parse_number(row.get(field))
                if message:
                    errors.append({"row_index": index, "field": field, "value": row.get(field), "error": message})
                else:
                    normalized[field] = parsed
            for field in boolean_fields:
                if field not in row:
                    continue
                parsed_bool, message = self._parse_bool(row.get(field))
                if message:
                    errors.append({"row_index": index, "field": field, "value": row.get(field), "error": message})
                else:
                    normalized[field] = parsed_bool
            normalized_rows.append(normalized)
        return normalized_rows, errors

    @staticmethod
    def _is_missing_value(value: object) -> bool:
        if value in {None, ""}:
            return True
        if not isinstance(value, str):
            return False
        token = value.strip().lower()
        if not token:
            return True
        return any(marker in token for marker in FieldReplayImportAgent.PLACEHOLDER_TOKENS)

    @staticmethod
    def _parse_number(value: object) -> tuple[float, str | None]:
        if value in {None, ""}:
            return 0.0, "missing_numeric_value"
        if isinstance(value, bool):
            return 0.0, "boolean_is_not_numeric"
        if isinstance(value, int | float):
            return float(value), None
        try:
            return float(str(value).strip()), None
        except ValueError:
            return 0.0, "invalid_numeric_value"

    @staticmethod
    def _parse_bool(value: object) -> tuple[bool, str | None]:
        if isinstance(value, bool):
            return value, None
        if value in {None, ""}:
            return False, "missing_boolean_value"
        token = str(value).strip().lower()
        if token in {"true", "1", "yes", "y", "t", "是"}:
            return True, None
        if token in {"false", "0", "no", "n", "f", "否"}:
            return False, None
        return False, "invalid_boolean_value"

    @staticmethod
    def _table_status(rows: list[dict[str, object]], missing_required: list[str], type_errors: list[dict[str, object]]) -> str:
        if not rows:
            return "missing_table"
        if missing_required:
            return "required_fields_missing"
        if type_errors:
            return "type_coercion_failed"
        return "import_ready"

    @staticmethod
    def _linkage_audit(datasets: dict[str, list[dict[str, object]]]) -> dict[str, object]:
        sensor_batches = FieldReplayImportAgent._batch_set(datasets, "sensor_timeseries")
        lab_batches = FieldReplayImportAgent._batch_set(datasets, "offline_lab_results")
        operation_batches = FieldReplayImportAgent._batch_set(datasets, "campaign_operation_log")
        proxy_batches = FieldReplayImportAgent._batch_set(datasets, "fast_proxy_event_log")
        pressure_batches = FieldReplayImportAgent._batch_set(datasets, "pressure_headloss_event_log")
        all_reference_batches = lab_batches | operation_batches | proxy_batches | pressure_batches
        orphan_reference_batches = sorted(all_reference_batches - sensor_batches)
        unlabeled_proxy_batches = sorted(proxy_batches - lab_batches)
        pressure_headloss_without_lab_batches = sorted(pressure_batches - lab_batches)
        operation_without_proxy_batches = sorted(operation_batches - proxy_batches)
        status = "linkage_ready"
        if orphan_reference_batches or unlabeled_proxy_batches or pressure_headloss_without_lab_batches:
            status = "linkage_blocked"
        return {
            "status": status,
            "sensor_batch_count": len(sensor_batches),
            "lab_batch_count": len(lab_batches),
            "operation_batch_count": len(operation_batches),
            "proxy_batch_count": len(proxy_batches),
            "pressure_headloss_batch_count": len(pressure_batches),
            "orphan_reference_batches": orphan_reference_batches,
            "unlabeled_proxy_batches": unlabeled_proxy_batches,
            "pressure_headloss_without_lab_batches": pressure_headloss_without_lab_batches,
            "operation_without_proxy_batches": operation_without_proxy_batches,
        }

    @staticmethod
    def _batch_set(datasets: dict[str, list[dict[str, object]]], table: str) -> set[str]:
        return {
            str(row.get("batch_id"))
            for row in datasets.get(table, [])
            if row.get("batch_id")
        }

    def _readiness(
        self,
        metadata_audit: dict[str, object],
        table_audit: dict[str, dict[str, object]],
        linkage_audit: dict[str, object],
    ) -> dict[str, object]:
        total = len(table_audit)
        accepted = sum(1 for item in table_audit.values() if item["status"] == "import_ready")
        metadata_ready = metadata_audit["status"] == "metadata_ready"
        field_origin = metadata_audit["data_origin"] == self.expected_data_origin
        tables_ready = accepted == total
        type_ready = all(not item["type_errors"] for item in table_audit.values())
        linkage_ready = linkage_audit["status"] == "linkage_ready"
        score = round(
            0.22 * float(metadata_ready)
            + 0.18 * float(field_origin)
            + 0.24 * (accepted / max(1, total))
            + 0.18 * float(type_ready)
            + 0.18 * float(linkage_ready),
            3,
        )
        if metadata_audit["status"] == "metadata_missing":
            status = "field_replay_import_missing_metadata"
        elif not field_origin:
            status = "field_replay_import_blocked_non_field_origin"
        elif not metadata_ready:
            status = "field_replay_import_metadata_blocked"
        elif not tables_ready:
            status = "field_replay_import_schema_blocked"
        elif not linkage_ready:
            status = "field_replay_import_linkage_blocked"
        else:
            status = "field_replay_import_ready_for_timestamped_replay"
        ready = status == "field_replay_import_ready_for_timestamped_replay"
        return {
            "field_replay_import_status": status,
            "field_replay_import_score": score,
            "accepted_table_count": accepted,
            "total_table_count": total,
            "accepted_data_origin": self.expected_data_origin if ready else "blocked",
            "can_pass_to_timestamped_replay": ready,
            "can_pass_to_g6": ready,
            "can_write_to_protective_control": False,
        }

    @staticmethod
    def _export_policy(readiness: dict[str, object]) -> dict[str, object]:
        ready = bool(readiness["can_pass_to_timestamped_replay"])
        return {
            "allowed_downstream_agent": "TimestampedCampaignReplayAgent" if ready else "none",
            "blocked_downstream_agents": [] if ready else ["TimestampedCampaignReplayAgent", "FieldReplayCalibrationGateAgent"],
            "can_write_to_protective_control": False,
            "writeback_boundary": "Agent44 只负责导入验收；保护性控制写回必须继续通过 Agent42 replay 和 Agent43 G6/P6。",
        }

    def _issues(
        self,
        metadata_audit: dict[str, object],
        table_audit: dict[str, dict[str, object]],
        linkage_audit: dict[str, object],
        readiness: dict[str, object],
    ) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        if metadata_audit["status"] != "metadata_ready":
            issues.append(
                QualityIssue(
                    sensor="field_replay_metadata",
                    issue_type=str(metadata_audit["status"]),
                    severity=Severity.CRITICAL,
                    message="现场 replay 包 metadata 未达到 provenance 和 field origin 要求。",
                    evidence=metadata_audit,
                )
            )
        for table, audit in table_audit.items():
            if audit["status"] != "import_ready":
                issues.append(
                    QualityIssue(
                        sensor=table,
                        issue_type=str(audit["status"]),
                        severity=Severity.CRITICAL if audit["status"] in {"missing_table", "type_coercion_failed"} else Severity.WARNING,
                        message="现场 replay CSV 未通过字段/类型导入验收。",
                        evidence=audit,
                    )
                )
        if linkage_audit["status"] != "linkage_ready":
            issues.append(
                QualityIssue(
                    sensor="field_replay_batch_linkage",
                    issue_type=str(linkage_audit["status"]),
                    severity=Severity.CRITICAL,
                    message="现场 replay 包无法按 batch_id 回连 sensor、lab、operation、fast proxy event 和 pressure/headloss event。",
                    evidence=linkage_audit,
                )
            )
        if readiness["can_write_to_protective_control"]:
            issues.append(
                QualityIssue(
                    sensor="field_replay_import_boundary",
                    issue_type="import_agent_writeback_forbidden",
                    severity=Severity.CRITICAL,
                    message="导入 Agent 不得直接授权保护性控制写回。",
                    evidence=readiness,
                )
            )
        return issues

    @staticmethod
    def _recommendations(readiness: dict[str, object]) -> list[str]:
        if readiness["can_pass_to_timestamped_replay"]:
            return [
                "将 normalized_datasets 传入 TimestampedCampaignReplayAgent，并保持 data_origin=field。",
                "继续通过 Agent43 G6/P6 检查 precision/recall、提前量、执行器延迟和误触发成本后，再讨论保护性控制写回。",
                "pressure_headloss_event_log 已通过导入门控后，仍需在 Agent42 replay 中检查 matched lab anchor，不能直接放松控制 guardrail。",
            ]
        return [
            "不要把当前 replay 包传给 G6/P6；先补齐 metadata provenance、CSV 必需字段、类型转换和 batch 关联。",
            "synthetic/sample 包只能用于接口联调，不得作为现场快代理 precision/recall 证据。",
            "真实导入包至少应包含 data_origin=field、site_id、campaign_id、operator_id、instrument_snapshot_id 和 chain_of_custody_id。",
            "若使用 pressure/headloss 作为水力代理，必须提供 pressure_headloss_event_log.csv，并确保每个 pressure batch 有同 batch 离线标签锚点。",
        ]

    @staticmethod
    def _method_contract() -> dict[str, object]:
        return {
            "upgrade_id": "field_replay_import_gate_before_timestamped_replay",
            "borrowed_from": [
                "academic_research_agent_evidence_before_claims",
                "systematic_literature_review_data_extraction_gates",
                "model_validation_and_uncertainty_provenance_checks",
                "timestamped_campaign_replay_for_fast_proxy_validation",
            ],
            "reality_mapping": "把真实现场 replay 包从“几张 CSV”提升为可追溯、可类型验收、可 batch 回连的数据入口，防止 synthetic/sample 数据误入现场校准。",
            "data_needs": [
                "metadata.json",
                "sensor_timeseries.csv",
                "offline_lab_results.csv",
                "campaign_operation_log.csv",
                "fast_proxy_event_log.csv",
                "pressure_headloss_event_log.csv",
                "node_modality_sensor_timeseries.csv for Agent51 catalyst proxy holdout",
                "site_topology_or_bed_geometry.csv for Agent51 catalyst proxy holdout",
                "pressure/headloss batch labels and bed_id linkage",
                "site_id",
                "campaign_id",
                "instrument_snapshot_id",
                "chain_of_custody_id",
            ],
            "implementation_path": [
                "src/water_ai/agents/field_replay_import_agent.py",
                "experiments/run_agent44_field_replay_import.py",
                "outputs/field_replay_import/import_acceptance_metrics.json",
            ],
            "evaluation_metrics": [
                "field_replay_import_score",
                "accepted_table_count",
                "type_coercion_error_count",
                "metadata_origin_ready",
                "batch_linkage_status",
            ],
            "failure_boundary": "导入通过只代表现场 replay 包可进入 Agent42；不能替代 Agent42 replay 指标、Agent43 G6/P6 或真实污染物达标验证。",
        }

    def _import_schema_contract(self) -> dict[str, object]:
        return {
            "metadata_required_fields": self.REQUIRED_METADATA_FIELDS,
            "table_contract": self.contract,
            "template_headers": _field_replay_template_headers(),
            "optional_supplement_files": ["node_modality_sensor_timeseries.csv", "site_topology_or_bed_geometry.csv"],
            "r7j_catalyst_proxy_holdout_template": {
                "headers": R7J_CATALYST_PROXY_TEMPLATE_HEADERS,
                "minimum_matched_batch_count": 3,
                "required_patch_signals": [
                    "N3_catalyst_bed_outlet:UV254_abs",
                    "N3_catalyst_bed_outlet:ORP_mV",
                    "N3_catalyst_bed:pressure_drop_kPa",
                ],
                "field_boundary": (
                    "Optional for Agent44 import; required by R7j when Agent51 weak_axis_repair_plan is evaluated."
                ),
            },
            "numeric_fields": self.NUMERIC_FIELDS,
            "boolean_fields": self.BOOLEAN_FIELDS,
        }


def load_field_replay_package(package_dir: str | Path) -> tuple[dict[str, object], dict[str, list[dict[str, object]]]]:
    """Load metadata.json and replay CSVs from a field replay package directory."""

    root = Path(package_dir)
    metadata_path = root / "metadata.json"
    metadata: dict[str, object] = {}
    if metadata_path.exists():
        metadata_payload = json.loads(metadata_path.read_text(encoding="utf-8"))
        if isinstance(metadata_payload, dict):
            metadata = metadata_payload
    tables: dict[str, list[dict[str, object]]] = {}
    table_names = _dict(field_replay_package_template_spec().get("csv_headers"))
    for table in table_names:
        csv_path = root / f"{table}.csv"
        if not csv_path.exists():
            continue
        with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            tables[table] = [dict(row) for row in reader]
    return metadata, tables


def field_replay_package_template_spec() -> dict[str, object]:
    """Return the minimum R7 package template without making synthetic evidence claims."""

    csv_headers = _field_replay_template_headers()
    return {
        "metadata": {
            "data_origin": "field",
            "site_id": "TODO_REAL_SITE_ID",
            "campaign_id": "TODO_REAL_CAMPAIGN_ID",
            "sampling_start": "TODO_ISO8601_START_TIME",
            "sampling_end": "TODO_ISO8601_END_TIME",
            "operator_id": "TODO_REAL_OPERATOR_ID",
            "instrument_snapshot_id": "TODO_SENSOR_AND_LAB_INSTRUMENT_SNAPSHOT_ID",
            "chain_of_custody_id": "TODO_SIGNED_CHAIN_OF_CUSTODY_ID",
            "notes": "Replace every TODO value before running Agent44 as real field evidence.",
        },
        "csv_headers": csv_headers,
        "required_files": [
            "metadata.json",
            *[f"{table}.csv" for table in TimestampedCampaignReplayAgent.replay_schema_contract()],
        ],
        "optional_supplement_files": [
            "node_modality_sensor_timeseries.csv",
            "site_topology_or_bed_geometry.csv",
            "hydraulic_path_stage_labels.csv",
            "final_effluent_endpoint_labels.csv",
        ],
        "r7j_catalyst_proxy_holdout_template": {
            "purpose": (
                "Optional scaffold for Agent51 catalyst_activity weak-axis field proxy holdout; "
                "it becomes required only when R7 coverage consumes Agent51 weak_axis_repair_plan."
            ),
            "headers": R7J_CATALYST_PROXY_TEMPLATE_HEADERS,
            "minimum_matched_batch_count": 3,
            "required_patch_signals": [
                "N3_catalyst_bed_outlet:UV254_abs",
                "N3_catalyst_bed_outlet:ORP_mV",
                "N3_catalyst_bed:pressure_drop_kPa",
            ],
            "field_boundary": (
                "These headers only prepare field_proxy_holdout collection. They do not make catalyst proxy "
                "field-supported until real rows pass R7j and downstream Agent51/R2/Agent49 gates."
            ),
        },
        "numeric_fields": FieldReplayImportAgent.NUMERIC_FIELDS,
        "boolean_fields": FieldReplayImportAgent.BOOLEAN_FIELDS,
        "field_boundary": (
            "This template is not evidence. It is only a collection scaffold until metadata placeholders are "
            "replaced and all CSVs contain real timestamped field rows."
        ),
    }


def write_field_replay_package_template(package_dir: str | Path) -> dict[str, object]:
    """Write a header-only R7 field replay package template."""

    root = Path(package_dir)
    root.mkdir(parents=True, exist_ok=True)
    spec = field_replay_package_template_spec()
    (root / "metadata.json").write_text(json.dumps(spec["metadata"], ensure_ascii=False, indent=2), encoding="utf-8")
    for table, headers in spec["csv_headers"].items():
        with (root / f"{table}.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=headers)
            writer.writeheader()
    return {
        "template_dir": str(root),
        "required_files": spec["required_files"],
        "optional_supplement_files": spec["optional_supplement_files"],
        "field_boundary": spec["field_boundary"],
    }


def preflight_field_replay_package(package_dir: str | Path) -> dict[str, object]:
    """Run file/header/placeholder checks before the Agent44 import gate."""

    root = Path(package_dir)
    spec = field_replay_package_template_spec()
    metadata, raw_tables = load_field_replay_package(root)
    import_report = FieldReplayImportAgent(metadata=metadata, raw_tables=raw_tables).run([])
    file_audit = _field_replay_file_audit(root)
    header_ready = all(item["status"] == "header_ready" for item in file_audit["csv_files"].values())
    files_ready = bool(file_audit["metadata_exists"]) and header_ready
    placeholder_metadata_fields = [
        field
        for field in FieldReplayImportAgent.REQUIRED_METADATA_FIELDS
        if FieldReplayImportAgent._is_missing_value(metadata.get(field))
    ]
    row_counts = {
        table: len(rows)
        for table, rows in raw_tables.items()
    }
    expected_tables = set(TimestampedCampaignReplayAgent.replay_schema_contract())
    row_counts = {table: row_counts.get(table, 0) for table in sorted(expected_tables)}
    real_rows_ready = all(count > 0 for count in row_counts.values())
    import_ready = bool(import_report.metrics["readiness"]["can_pass_to_timestamped_replay"])
    agent44_status = str(import_report.metrics["readiness"]["field_replay_import_status"])
    table_import_audit = _dict(import_report.metrics.get("table_import_audit"))
    linkage_audit = _dict(import_report.metrics.get("linkage_audit"))
    agent44_diagnostics = _agent44_preflight_diagnostics(table_import_audit, linkage_audit)
    if import_ready:
        status = "field_package_preflight_ready_for_agent42"
    elif agent44_status == "field_replay_import_blocked_non_field_origin":
        status = "field_package_preflight_blocked_non_field_origin"
    elif not files_ready:
        status = "field_package_preflight_missing_files_or_headers"
    elif placeholder_metadata_fields or not real_rows_ready:
        status = "field_package_template_ready_needs_real_values_and_rows"
    else:
        status = "field_package_preflight_agent44_blocked"
    return {
        "package_dir": str(root),
        "status": status,
        "required_files": spec["required_files"],
        "file_audit": file_audit,
        "r7j_supplement_audit": file_audit.get("r7j_supplement_csv_files", {}),
        "placeholder_metadata_fields": placeholder_metadata_fields,
        "row_counts": row_counts,
        "files_ready": files_ready,
        "real_rows_ready": real_rows_ready,
        "agent44_import_status": agent44_status,
        "agent44_import_score": import_report.metrics["readiness"]["field_replay_import_score"],
        "agent44_blocking_table_statuses": agent44_diagnostics["blocking_table_statuses"],
        "agent44_type_error_count": agent44_diagnostics["type_error_count"],
        "agent44_type_error_tables": agent44_diagnostics["type_error_tables"],
        "agent44_required_field_blockers": agent44_diagnostics["required_field_blockers"],
        "agent44_linkage_blockers": agent44_diagnostics["linkage_blockers"],
        "can_pass_to_timestamped_replay": import_ready,
        "next_actions": _field_replay_preflight_next_actions(
            files_ready,
            placeholder_metadata_fields,
            real_rows_ready,
            import_ready,
            agent44_status,
            agent44_diagnostics,
        ),
        "field_boundary": spec["field_boundary"],
    }


def _agent44_preflight_diagnostics(
    table_import_audit: dict[str, object],
    linkage_audit: dict[str, object],
) -> dict[str, object]:
    blocking_table_statuses: dict[str, str] = {}
    type_error_tables: dict[str, list[object]] = {}
    required_field_blockers: dict[str, list[str]] = {}
    type_error_count = 0
    for table, audit_value in sorted(table_import_audit.items()):
        audit = _dict(audit_value)
        status = str(audit.get("status", "unknown"))
        if status != "import_ready":
            blocking_table_statuses[str(table)] = status
        missing_required = [str(field) for field in _list(audit.get("missing_required_fields"))]
        if missing_required:
            required_field_blockers[str(table)] = missing_required
        type_errors = _list(audit.get("type_errors"))
        if type_errors:
            type_error_tables[str(table)] = type_errors[:12]
            type_error_count += len(type_errors)
    linkage_blockers = {
        "orphan_reference_batches": _list(linkage_audit.get("orphan_reference_batches")),
        "unlabeled_proxy_batches": _list(linkage_audit.get("unlabeled_proxy_batches")),
        "pressure_headloss_without_lab_batches": _list(linkage_audit.get("pressure_headloss_without_lab_batches")),
        "operation_without_proxy_batches": _list(linkage_audit.get("operation_without_proxy_batches")),
    }
    linkage_blockers = {key: value for key, value in linkage_blockers.items() if value}
    return {
        "blocking_table_statuses": blocking_table_statuses,
        "type_error_count": type_error_count,
        "type_error_tables": type_error_tables,
        "required_field_blockers": required_field_blockers,
        "linkage_blockers": linkage_blockers,
    }


def _field_replay_file_audit(root: Path) -> dict[str, object]:
    metadata_path = root / "metadata.json"
    csv_files: dict[str, dict[str, object]] = {}
    contract = TimestampedCampaignReplayAgent.replay_schema_contract()
    spec = field_replay_package_template_spec()
    headers = {
        table: fields
        for table, fields in _dict(spec.get("csv_headers")).items()
        if table in contract
    }
    for table, expected_headers in headers.items():
        csv_path = root / f"{table}.csv"
        exists = csv_path.exists()
        actual_headers: list[str] = []
        if exists:
            with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.reader(handle)
                try:
                    actual_headers = next(reader)
                except StopIteration:
                    actual_headers = []
        required_fields = [str(field) for field in contract[table]["required_fields"]]
        missing_required_headers = [field for field in required_fields if field not in actual_headers]
        missing_optional_headers = [field for field in expected_headers if field not in actual_headers and field not in missing_required_headers]
        status = "header_ready"
        if not exists:
            status = "missing_csv_file"
        elif missing_required_headers:
            status = "missing_required_headers"
        return_item = {
            "exists": exists,
            "status": status,
            "required_headers": required_fields,
            "expected_headers": expected_headers,
            "actual_headers": actual_headers,
            "missing_required_headers": missing_required_headers,
            "missing_optional_headers": missing_optional_headers,
        }
        csv_files[table] = return_item
    return {
        "metadata_exists": metadata_path.exists(),
        "csv_files": csv_files,
        "r7j_supplement_csv_files": _r7j_supplement_file_audit(root, spec),
    }


def _field_replay_template_headers() -> dict[str, list[str]]:
    headers = {
        table: list(fields)
        for table, fields in TimestampedCampaignReplayAgent.template_headers().items()
    }
    for table, supplement_headers in R7J_CATALYST_PROXY_TEMPLATE_HEADERS.items():
        if table not in headers:
            headers[table] = list(supplement_headers)
            continue
        for field in supplement_headers:
            if field not in headers[table]:
                headers[table].append(field)
    for table, supplement_headers in R8U66_FIELD_PATH_ENDPOINT_TEMPLATE_HEADERS.items():
        if table not in headers:
            headers[table] = list(supplement_headers)
            continue
        for field in supplement_headers:
            if field not in headers[table]:
                headers[table].append(field)
    return headers


def _r7j_supplement_file_audit(root: Path, spec: dict[str, object]) -> dict[str, dict[str, object]]:
    audit: dict[str, dict[str, object]] = {}
    headers = _dict(spec.get("csv_headers"))
    for file_name in _list(spec.get("optional_supplement_files")):
        table = str(file_name).removesuffix(".csv")
        csv_path = root / str(file_name)
        expected_headers = [str(field) for field in _list(headers.get(table))]
        actual_headers: list[str] = []
        if csv_path.exists():
            with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.reader(handle)
                try:
                    actual_headers = next(reader)
                except StopIteration:
                    actual_headers = []
        missing_headers = [field for field in expected_headers if field not in actual_headers]
        row_count = 0
        if csv_path.exists() and actual_headers:
            with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
                row_count = sum(1 for _ in csv.DictReader(handle))
        status = "supplement_header_ready"
        if not csv_path.exists():
            status = "supplement_missing_optional_file"
        elif missing_headers:
            status = "supplement_missing_headers"
        return_item = {
            "exists": csv_path.exists(),
            "status": status,
            "expected_headers": expected_headers,
            "actual_headers": actual_headers,
            "missing_headers": missing_headers,
            "row_count": row_count,
            "field_boundary": (
                "Optional for Agent44 import, but required by R7j when Agent51 catalyst proxy holdout is evaluated."
            ),
        }
        audit[table] = return_item
    return audit


def _field_replay_preflight_next_actions(
    files_ready: bool,
    placeholder_metadata_fields: list[str],
    real_rows_ready: bool,
    import_ready: bool,
    agent44_status: str,
    agent44_diagnostics: dict[str, object],
) -> list[str]:
    if import_ready:
        return [
            "Run experiments/run_agent44_field_replay_import.py with REAL_FIELD_REPLAY_PACKAGE_DIR pointing to this package.",
            "Then run Agent42 timestamped replay, Agent43 G6/P6, Agent45 evidence chain and R7 acceptance gate.",
        ]
    actions: list[str] = []
    if agent44_status == "field_replay_import_blocked_non_field_origin":
        actions.append("Use this package only for interface testing; create a separate package with data_origin=field and real provenance before replay.")
    if not files_ready:
        actions.append("Create metadata.json and all required CSV files with required headers from the R7 template.")
    if placeholder_metadata_fields:
        actions.append(f"Replace placeholder metadata fields: {', '.join(placeholder_metadata_fields)}.")
    if not real_rows_ready:
        actions.append("Add real timestamped field rows to every CSV; header-only templates cannot enter field replay.")
    blocking_tables = _dict(agent44_diagnostics.get("blocking_table_statuses"))
    type_error_tables = _dict(agent44_diagnostics.get("type_error_tables"))
    required_field_blockers = _dict(agent44_diagnostics.get("required_field_blockers"))
    linkage_blockers = _dict(agent44_diagnostics.get("linkage_blockers"))
    if blocking_tables and real_rows_ready and files_ready and not placeholder_metadata_fields:
        actions.append(
            "Repair Agent44 import blockers by table: "
            + ", ".join(f"{table}={status}" for table, status in sorted(blocking_tables.items()))
            + "."
        )
    if type_error_tables:
        actions.append(
            "Fix Agent44 type coercion errors in: "
            + ", ".join(str(table) for table in sorted(type_error_tables))
            + "."
        )
    if required_field_blockers:
        actions.append(
            "Fill Agent44 required fields in: "
            + ", ".join(str(table) for table in sorted(required_field_blockers))
            + "."
        )
    if linkage_blockers:
        actions.append(
            "Align batch_id linkage before replay: "
            + ", ".join(f"{key}={value}" for key, value in sorted(linkage_blockers.items()))
            + "."
        )
    if not actions:
        actions.append("Run Agent44 and inspect type, batch linkage or provenance blockers.")
    actions.append("Do not label this package field-supported until Agent44/42/43/45/46/59/R7 gates pass.")
    return actions


def _dict(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def _list(value: object) -> list[object]:
    return value if isinstance(value, list) else []
