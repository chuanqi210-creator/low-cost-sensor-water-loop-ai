from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class TimestampedCampaignReplayAgent(BaseAgent):
    """Audit field timestamp coverage for replaying fast-proxy and delayed-control decisions."""

    name = "timestamped_campaign_replay_agent"

    def __init__(
        self,
        *,
        datasets: dict[str, list[dict[str, object]]] | None = None,
        data_origin: str = "synthetic",
        minimum_proxy_events: int = 12,
    ) -> None:
        self.datasets = datasets or {}
        self.data_origin = data_origin
        self.minimum_proxy_events = minimum_proxy_events

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        contract = self.replay_schema_contract()
        table_audit = self._table_audit(contract)
        linkage = self._linkage()
        replay_metrics = self._replay_metrics(table_audit)
        readiness = self._readiness(table_audit, linkage, replay_metrics)
        issues = self._issues(table_audit, linkage, replay_metrics, readiness)
        recommendations = self._recommendations(readiness, replay_metrics)
        summary = (
            f"时间戳回放接口：{readiness['timestamped_replay_status']}；"
            f"时间戳覆盖 {readiness['timestamp_coverage']:.3f}，"
            f"快代理标签事件 {replay_metrics['proxy_label_count']}。"
        )
        confidence = round(
            min(0.9, max(0.18, 0.35 + 0.38 * readiness["timestamped_replay_score"] - 0.025 * len(issues))),
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
                "replay_schema_contract": contract,
                "data_origin": self.data_origin,
                "table_audit": table_audit,
                "linkage": linkage,
                "replay_metrics": replay_metrics,
                "readiness": readiness,
                "template_headers": self.template_headers(),
            },
        )

    @classmethod
    def replay_schema_contract(cls) -> dict[str, dict[str, object]]:
        return {
            "sensor_timeseries": {
                "description": "低成本传感原始时间序列，支撑快代理触发时间。",
                "required_fields": ["batch_id", "timestamp_min", "EC_uScm", "turbidity_NTU", "UV254_abs", "pH", "ORP_mV"],
                "optional_fields": [
                    "flow_Lmin",
                    "pressure_drop_kPa",
                    "headloss_kPa_per_m",
                    "bed_inlet_pressure_kPa",
                    "bed_outlet_pressure_kPa",
                ],
                "timestamp_fields": ["timestamp_min"],
                "primary_key": ["batch_id", "timestamp_min"],
            },
            "offline_lab_results": {
                "description": "离线标签与结果返回时间，用于计算检测 turnaround 和快代理标签。",
                "required_fields": ["batch_id", "sample_time_min", "result_time_min", "analyte", "value", "qa_flag"],
                "optional_fields": ["proxy_holdout_label", "catalyst_activity_label", "pressure_headloss_proxy_label"],
                "timestamp_fields": ["sample_time_min", "result_time_min"],
                "primary_key": ["batch_id", "sample_time_min", "analyte"],
            },
            "campaign_operation_log": {
                "description": "控制动作命令、执行和生效时间，用于计算执行器/预处理延迟。",
                "required_fields": ["campaign_id", "batch_id", "action_id", "command_time_min", "effect_time_min", "start_min", "end_min", "release_policy"],
                "optional_fields": [
                    "recycle_ratio",
                    "tank_storage_margin",
                    "actuator_latency_p90",
                    "pump_valve_result",
                    "hold_time_min",
                    "regeneration_event",
                    "bed_id",
                    "pressure_headloss_review_required",
                ],
                "timestamp_fields": ["command_time_min", "effect_time_min", "start_min", "end_min"],
                "primary_key": ["campaign_id", "batch_id", "action_id", "command_time_min"],
            },
            "pressure_headloss_event_log": {
                "description": "压降/水头损失候选代理事件，用于 replay 催化剂床堵塞、水力异常和 guardrail 阻断边界。",
                "required_fields": [
                    "campaign_id",
                    "batch_id",
                    "event_time_min",
                    "bed_id",
                    "pressure_drop_kPa",
                    "headloss_kPa_per_m",
                    "flow_Lmin",
                    "matched_lab_sample_time_min",
                    "regeneration_event",
                    "hydraulic_anomaly_label",
                ],
                "optional_fields": [
                    "flow_normalized_pressure_residual",
                    "expected_clean_bed_pressure_drop_kPa",
                    "operator_review_required",
                ],
                "timestamp_fields": ["event_time_min", "matched_lab_sample_time_min"],
                "primary_key": ["campaign_id", "batch_id", "bed_id", "event_time_min"],
            },
            "fast_proxy_event_log": {
                "description": "基质冲击快代理事件与现场标签，用于 precision/recall、提前量和误触发成本校准。",
                "required_fields": [
                    "campaign_id",
                    "batch_id",
                    "event_time_min",
                    "proxy_score",
                    "specificity_guard_score",
                    "protective_triggered",
                    "triggered_action_id",
                    "field_label_matrix_shock",
                    "lab_label_time_min",
                    "false_positive_cost_index",
                ],
                "timestamp_fields": ["event_time_min", "lab_label_time_min"],
                "primary_key": ["campaign_id", "batch_id", "event_time_min"],
            },
        }

    @classmethod
    def template_headers(cls) -> dict[str, list[str]]:
        return {
            table: list(spec["required_fields"]) + list(spec.get("optional_fields", []))
            for table, spec in cls.replay_schema_contract().items()
        }

    @staticmethod
    def _method_contract() -> dict[str, object]:
        return {
            "upgrade_id": "timestamped_campaign_replay_for_fast_proxy_validation",
            "borrowed_from": [
                "parsa_2024_dynamic_control_review",
                "ching_2021_wwtp_soft_sensor_review",
                "matrix_shock_fast_proxy_latency_aware_control",
                "R8e_pressure_headloss_timestamped_replay_contract",
            ],
            "reality_mapping": "把快代理触发、离线标签返回、执行器生效和回流/暂存时间统一到同一 batch 时间轴，支撑现场 replay。",
            "data_needs": [
                "sensor_timestamp_min",
                "offline_sample_time_min",
                "offline_result_time_min",
                "actuator_command_time_min",
                "actuator_effect_time_min",
                "fast_proxy_event_time_min",
                "field_label_matrix_shock",
                "false_positive_cost_index",
                "pressure_headloss_event_time_min",
                "matched_lab_sample_time_min",
                "bed_id_and_bed_geometry",
            ],
            "implementation_path": [
                "src/water_ai/agents/timestamped_campaign_replay_agent.py",
                "experiments/run_agent42_timestamped_campaign_replay.py",
                "outputs/timestamped_campaign_replay/",
            ],
            "evaluation_metrics": [
                "timestamp_coverage",
                "proxy_precision",
                "proxy_recall",
                "protective_action_lead_time_min",
                "lab_turnaround_p90_min",
                "actuator_latency_p90_min",
                "pressure_headloss_event_count",
                "pressure_headloss_matched_batch_count",
            ],
            "failure_boundary": "timestamped synthetic package 只能验证接口和 replay 计算；不能替代现场 timestamped campaign replay。",
        }

    def _table_audit(self, contract: dict[str, dict[str, object]]) -> dict[str, dict[str, object]]:
        audit: dict[str, dict[str, object]] = {}
        for table, spec in contract.items():
            rows = self.datasets.get(table, [])
            required_fields = [str(field) for field in spec["required_fields"]]
            optional_fields = [str(field) for field in spec.get("optional_fields", [])]
            timestamp_fields = [str(field) for field in spec["timestamp_fields"]]
            missing_required = sorted(
                field
                for field in required_fields
                if any(field not in row or row.get(field) in {None, ""} for row in rows)
            )
            timestamp_values = [
                row.get(field)
                for row in rows
                for field in timestamp_fields
                if field in row
            ]
            timestamp_present = sum(1 for value in timestamp_values if isinstance(value, int | float))
            timestamp_coverage = timestamp_present / max(1, len(rows) * len(timestamp_fields))
            invalid_time_rows = self._invalid_time_rows(table, rows)
            audit[table] = {
                "record_count": len(rows),
                "required_fields": required_fields,
                "optional_fields": optional_fields,
                "optional_fields_present": sorted(
                    field for field in optional_fields if any(field in row and row.get(field) not in {None, ""} for row in rows)
                ),
                "timestamp_fields": timestamp_fields,
                "missing_required_fields": missing_required,
                "timestamp_coverage": round(timestamp_coverage, 3),
                "invalid_time_rows": invalid_time_rows,
                "status": self._table_status(len(rows), missing_required, timestamp_coverage, invalid_time_rows),
            }
        return audit

    @staticmethod
    def _invalid_time_rows(table: str, rows: list[dict[str, object]]) -> list[str]:
        invalid: list[str] = []
        for index, row in enumerate(rows):
            if table == "offline_lab_results":
                sample = row.get("sample_time_min")
                result = row.get("result_time_min")
                if isinstance(sample, int | float) and isinstance(result, int | float) and result < sample:
                    invalid.append(str(index))
            elif table == "campaign_operation_log":
                command = row.get("command_time_min")
                effect = row.get("effect_time_min")
                start = row.get("start_min")
                end = row.get("end_min")
                if all(isinstance(value, int | float) for value in (command, effect, start, end)):
                    if not (command <= effect <= end and start <= end):
                        invalid.append(str(index))
            elif table == "fast_proxy_event_log":
                event_time = row.get("event_time_min")
                label_time = row.get("lab_label_time_min")
                if isinstance(event_time, int | float) and isinstance(label_time, int | float) and label_time < event_time:
                    invalid.append(str(index))
            elif table == "pressure_headloss_event_log":
                event_time = row.get("event_time_min")
                sample_time = row.get("matched_lab_sample_time_min")
                if isinstance(event_time, int | float) and isinstance(sample_time, int | float) and sample_time < 0:
                    invalid.append(str(index))
        return invalid

    @staticmethod
    def _table_status(record_count: int, missing_required: list[str], timestamp_coverage: float, invalid_time_rows: list[str]) -> str:
        if record_count == 0:
            return "missing_table"
        if missing_required:
            return "schema_incomplete"
        if invalid_time_rows:
            return "invalid_time_order"
        if timestamp_coverage < 0.9:
            return "timestamp_coverage_low"
        return "timestamp_ready"

    def _linkage(self) -> dict[str, object]:
        sensor_batches = self._batch_set("sensor_timeseries")
        lab_batches = self._batch_set("offline_lab_results")
        operation_batches = self._batch_set("campaign_operation_log")
        proxy_batches = self._batch_set("fast_proxy_event_log")
        pressure_batches = self._batch_set("pressure_headloss_event_log")
        all_reference_batches = lab_batches | operation_batches | proxy_batches | pressure_batches
        return {
            "sensor_batch_count": len(sensor_batches),
            "lab_batch_count": len(lab_batches),
            "operation_batch_count": len(operation_batches),
            "proxy_batch_count": len(proxy_batches),
            "pressure_headloss_batch_count": len(pressure_batches),
            "orphan_reference_batches": sorted(all_reference_batches - sensor_batches),
            "unlabeled_proxy_batches": sorted(proxy_batches - lab_batches),
            "pressure_headloss_without_lab_batches": sorted(pressure_batches - lab_batches),
            "operation_without_proxy_batches": sorted(operation_batches - proxy_batches),
        }

    def _batch_set(self, table: str) -> set[str]:
        return {
            str(row.get("batch_id"))
            for row in self.datasets.get(table, [])
            if row.get("batch_id")
        }

    def _replay_metrics(self, table_audit: dict[str, dict[str, object]]) -> dict[str, object]:
        lab_rows = self.datasets.get("offline_lab_results", [])
        operation_rows = self.datasets.get("campaign_operation_log", [])
        proxy_rows = self.datasets.get("fast_proxy_event_log", [])
        pressure_rows = self.datasets.get("pressure_headloss_event_log", [])
        lab_turnarounds = [
            float(row["result_time_min"]) - float(row["sample_time_min"])
            for row in lab_rows
            if isinstance(row.get("sample_time_min"), int | float) and isinstance(row.get("result_time_min"), int | float)
        ]
        actuator_latencies = [
            float(row["effect_time_min"]) - float(row["command_time_min"])
            for row in operation_rows
            if isinstance(row.get("command_time_min"), int | float) and isinstance(row.get("effect_time_min"), int | float)
        ]
        proxy_labels = [
            row
            for row in proxy_rows
            if isinstance(row.get("field_label_matrix_shock"), bool)
            and isinstance(row.get("protective_triggered"), bool)
        ]
        tp = sum(1 for row in proxy_labels if row["protective_triggered"] and row["field_label_matrix_shock"])
        fp = sum(1 for row in proxy_labels if row["protective_triggered"] and not row["field_label_matrix_shock"])
        fn = sum(1 for row in proxy_labels if (not row["protective_triggered"]) and row["field_label_matrix_shock"])
        precision = tp / max(1, tp + fp)
        recall = tp / max(1, tp + fn)
        lead_times = [
            float(row["lab_label_time_min"]) - float(row["event_time_min"])
            for row in proxy_labels
            if row.get("protective_triggered")
            and isinstance(row.get("lab_label_time_min"), int | float)
            and isinstance(row.get("event_time_min"), int | float)
        ]
        false_positive_costs = [
            float(row.get("false_positive_cost_index", 0.0))
            for row in proxy_labels
            if row.get("protective_triggered") and not row.get("field_label_matrix_shock")
        ]
        pressure_events = [
            row
            for row in pressure_rows
            if isinstance(row.get("event_time_min"), int | float)
            and isinstance(row.get("matched_lab_sample_time_min"), int | float)
            and isinstance(row.get("pressure_drop_kPa"), int | float)
            and isinstance(row.get("headloss_kPa_per_m"), int | float)
        ]
        timestamp_coverages = [float(item["timestamp_coverage"]) for item in table_audit.values()]
        return {
            "timestamp_coverage": round(sum(timestamp_coverages) / max(1, len(timestamp_coverages)), 3),
            "proxy_label_count": len(proxy_labels),
            "true_positive_count": tp,
            "false_positive_count": fp,
            "false_negative_count": fn,
            "proxy_precision": round(precision, 3),
            "proxy_recall": round(recall, 3),
            "mean_protective_action_lead_time_min": round(sum(lead_times) / max(1, len(lead_times)), 3),
            "mean_lab_turnaround_min": round(sum(lab_turnarounds) / max(1, len(lab_turnarounds)), 3),
            "p90_lab_turnaround_min": round(self._percentile(lab_turnarounds, 0.9), 3),
            "mean_actuator_latency_min": round(sum(actuator_latencies) / max(1, len(actuator_latencies)), 3),
            "p90_actuator_latency_min": round(self._percentile(actuator_latencies, 0.9), 3),
            "mean_false_positive_cost_index": round(sum(false_positive_costs) / max(1, len(false_positive_costs)), 3),
            "pressure_headloss_event_count": len(pressure_events),
            "pressure_headloss_matched_batch_count": len({str(row.get("batch_id")) for row in pressure_events if row.get("batch_id")}),
        }

    def _readiness(
        self,
        table_audit: dict[str, dict[str, object]],
        linkage: dict[str, object],
        replay_metrics: dict[str, object],
    ) -> dict[str, object]:
        all_tables_ready = all(item["status"] == "timestamp_ready" for item in table_audit.values())
        no_orphans = (
            not linkage["orphan_reference_batches"]
            and not linkage["unlabeled_proxy_batches"]
            and not linkage["pressure_headloss_without_lab_batches"]
        )
        enough_proxy_labels = int(replay_metrics["proxy_label_count"]) >= self.minimum_proxy_events
        precision_ready = float(replay_metrics["proxy_precision"]) >= 0.82
        recall_ready = float(replay_metrics["proxy_recall"]) >= 0.78
        field_origin = self.data_origin == "field"
        score = round(
            0.24 * float(all_tables_ready)
            + 0.18 * float(no_orphans)
            + 0.18 * min(1.0, float(replay_metrics["timestamp_coverage"]))
            + 0.12 * float(enough_proxy_labels)
            + 0.12 * float(precision_ready)
            + 0.10 * float(recall_ready)
            + 0.06 * float(field_origin),
            3,
        )
        if not field_origin:
            status = "synthetic_timestamp_schema_ready_needs_field_replay"
        elif not all_tables_ready or not no_orphans:
            status = "field_timestamped_replay_schema_blocked"
        elif not enough_proxy_labels:
            status = "field_timestamped_replay_needs_more_proxy_labels"
        elif not (precision_ready and recall_ready):
            status = "field_fast_proxy_validation_failed"
        else:
            status = "field_timestamped_replay_ready_for_fast_proxy_calibration"
        return {
            "timestamped_replay_status": status,
            "timestamped_replay_score": score,
            "timestamp_coverage": float(replay_metrics["timestamp_coverage"]),
            "field_replay_required": not field_origin,
            "can_calibrate_fast_proxy": field_origin and status == "field_timestamped_replay_ready_for_fast_proxy_calibration",
            "can_write_to_protective_control": field_origin and status == "field_timestamped_replay_ready_for_fast_proxy_calibration",
        }

    def _issues(
        self,
        table_audit: dict[str, dict[str, object]],
        linkage: dict[str, object],
        replay_metrics: dict[str, object],
        readiness: dict[str, object],
    ) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        for table, audit in table_audit.items():
            if audit["status"] != "timestamp_ready":
                issues.append(
                    QualityIssue(
                        sensor=table,
                        issue_type=str(audit["status"]),
                        severity=Severity.WARNING,
                        message="时间戳回放字段尚未达到 replay 要求。",
                        evidence=audit,
                    )
                )
        if linkage["orphan_reference_batches"] or linkage["unlabeled_proxy_batches"]:
            issues.append(
                QualityIssue(
                    sensor="timestamped_campaign_replay",
                    issue_type="timestamped_replay_linkage_incomplete",
                    severity=Severity.WARNING,
                    message="快代理、离线标签或操作日志无法完整回连 sensor batch。",
                    evidence=linkage,
                )
            )
        if linkage["pressure_headloss_without_lab_batches"]:
            issues.append(
                QualityIssue(
                    sensor="pressure_headloss_event_log",
                    issue_type="pressure_headloss_event_without_lab_anchor",
                    severity=Severity.WARNING,
                    message="压降/水头损失 replay 事件缺少同 batch 离线标签锚点，不能用于现场 guardrail 校准。",
                    evidence=linkage,
                )
            )
        if readiness["field_replay_required"]:
            issues.append(
                QualityIssue(
                    sensor="timestamped_campaign_replay",
                    issue_type="field_timestamped_replay_required",
                    severity=Severity.WARNING,
                    message="当前 timestamped replay 包只能验证接口，不能替代现场 replay。",
                    evidence=readiness,
                )
            )
        if int(replay_metrics["proxy_label_count"]) < self.minimum_proxy_events:
            issues.append(
                QualityIssue(
                    sensor="fast_proxy_event_log",
                    issue_type="proxy_label_count_too_low",
                    severity=Severity.INFO,
                    message="快代理 precision/recall 需要更多 field-labeled events。",
                    evidence=replay_metrics,
                )
            )
        return issues

    @staticmethod
    def _recommendations(readiness: dict[str, object], replay_metrics: dict[str, object]) -> list[str]:
        recommendations = [
            "把 sensor、lab、operation 和 fast_proxy_event_log 放到同一 batch 时间轴，优先保证 result_time_min 与 effect_time_min。",
            "用 field-labeled fast_proxy_event_log 计算 precision、recall、提前量和误触发成本，再决定是否写入保护性控制。",
            "pressure_headloss_event_log 必须回连同 batch 的传感、离线标签和床层信息，才能从候选水力代理进入 guardrail replay。",
        ]
        if readiness["field_replay_required"]:
            recommendations.append("当前 synthetic timestamped package 只能作为模板联调，不得作为 Agent41 现场有效性证据。")
        else:
            recommendations.append(
                f"当前 proxy precision={replay_metrics['proxy_precision']}，recall={replay_metrics['proxy_recall']}；未达标时不要写入自动保护控制。"
            )
        return recommendations

    @staticmethod
    def _percentile(values: list[float], quantile: float) -> float:
        if not values:
            return 0.0
        ordered = sorted(values)
        index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * quantile)))
        return ordered[index]
