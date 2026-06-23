from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class FieldDataInterfaceAgent(BaseAgent):
    """Validate the field-data package needed to calibrate the research platform."""

    name = "field_data_interface_agent"

    def __init__(
        self,
        *,
        datasets: dict[str, list[dict[str, object]]] | None = None,
        data_origin: str = "unknown",
        minimum_records: dict[str, int] | None = None,
    ) -> None:
        self.datasets = datasets or {}
        self.data_origin = data_origin
        self.minimum_records = {
            "sensor_timeseries": 24,
            "offline_lab_results": 6,
            "catalyst_lifecycle": 2,
            "campaign_operation_log": 4,
            "cost_deployment": 3,
            "site_topology_or_bed_geometry": 1,
            **(minimum_records or {}),
        }

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        datasets = self._datasets_from_readings(readings) if readings else self.datasets
        table_statuses = self._table_statuses(datasets)
        linkage = self._linkage_checks(datasets)
        calibration_tasks = self._calibration_tasks(table_statuses, linkage)
        readiness = self._readiness(table_statuses, linkage)
        issues = self._issues(table_statuses, linkage, readiness)
        recommendations = self._recommendations(readiness, calibration_tasks)
        summary = (
            f"真实数据接口：{readiness['interface_status']}；字段完整度 "
            f"{readiness['field_coverage']:.3f}，校准就绪度 {readiness['calibration_readiness_score']:.3f}。"
        )
        confidence = round(min(0.9, max(0.18, 0.35 + 0.5 * readiness["calibration_readiness_score"])), 3)

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "data_origin": self.data_origin,
                "schema_contract": self.schema_contract(),
                "table_statuses": table_statuses,
                "linkage_checks": linkage,
                "calibration_tasks": calibration_tasks,
                "readiness": readiness,
                "template_headers": self.template_headers(),
            },
        )

    @classmethod
    def schema_contract(cls) -> dict[str, dict[str, object]]:
        return {
            "sensor_timeseries": {
                "description": "低成本在线传感器原始时间序列。",
                "required_fields": [
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
                "optional_fields": [
                    "sensor_status",
                    "operator_note",
                    "instrument_id",
                    "acquisition_time_min",
                    "ingest_time_min",
                    "pressure_drop_kPa",
                    "headloss_kPa_per_m",
                    "bed_inlet_pressure_kPa",
                    "bed_outlet_pressure_kPa",
                    "flow_normalized_pressure_residual",
                ],
                "primary_key": ["batch_id", "timestamp_min"],
                "calibrates": ["DataQualityAgent", "SoftSensorAgent", "sensor_noise_multiplier"],
            },
            "offline_lab_results": {
                "description": "旁路快检/离线检测标签，用于校准软传感器和放行门。",
                "required_fields": ["batch_id", "sample_time_min", "analyte", "value", "unit", "method", "qa_flag"],
                "optional_fields": [
                    "result_time_min",
                    "turnaround_min",
                    "detection_limit",
                    "lab_id",
                    "replicate_id",
                    "sample_source",
                    "proxy_holdout_label",
                ],
                "primary_key": ["batch_id", "sample_time_min", "analyte"],
                "calibrates": ["SoftSensorAgent", "ValidationPlanningAgent", "release_gate"],
            },
            "catalyst_lifecycle": {
                "description": "催化剂寿命、再生和更换记录。",
                "required_fields": [
                    "catalyst_id",
                    "batch_id",
                    "cycle_count",
                    "regen_count",
                    "activity_assay",
                    "pressure_drop_kPa",
                    "lifetime_fraction",
                ],
                "optional_fields": [
                    "surface_pollution_index",
                    "replacement_flag",
                    "regen_method",
                    "regeneration_event",
                    "headloss_kPa_per_m",
                    "bed_geometry_id",
                    "catalyst_bed_depth_m",
                ],
                "primary_key": ["catalyst_id", "batch_id"],
                "calibrates": ["CatalystLifecycleAgent", "RecoveryStrategyWritebackAgent"],
            },
            "campaign_operation_log": {
                "description": "批次运行、动作执行和闭环控制日志。",
                "required_fields": [
                    "campaign_id",
                    "batch_id",
                    "action_id",
                    "start_min",
                    "end_min",
                    "intake_fraction",
                    "success",
                ],
                "optional_fields": [
                    "command_time_min",
                    "effect_time_min",
                    "recycle_start_min",
                    "recycle_end_min",
                    "pretreatment_effect_time_min",
                    "fast_proxy_score",
                    "release_policy",
                    "recycle_ratio",
                    "dose_factor",
                    "validation_minutes",
                    "operator_override",
                    "tank_storage_margin",
                    "actuator_latency_p90",
                    "pump_valve_result",
                    "hold_time_min",
                    "regeneration_event",
                    "bed_id",
                    "pressure_headloss_review_required",
                ],
                "primary_key": ["campaign_id", "batch_id", "action_id", "start_min"],
                "calibrates": ["CampaignTelemetryAgent", "RecoveryRampAgent", "RecoveryOnlineControlAgent"],
            },
            "site_topology_or_bed_geometry": {
                "description": "处理单元拓扑、催化剂床几何和水力先验，用于把压降/水头损失候选信号从黑箱代理转成可校准灰箱边界。",
                "required_fields": [
                    "site_id",
                    "node_id",
                    "zone",
                    "upstream_node_id",
                    "downstream_node_id",
                    "bed_id",
                    "bed_depth_m",
                    "bed_area_m2",
                    "nominal_flow_Lmin",
                    "nominal_HRT_min",
                ],
                "optional_fields": [
                    "pressure_sensor_location",
                    "install_access_score",
                    "bed_media",
                    "hydraulic_position",
                    "expected_clean_bed_pressure_drop_kPa",
                ],
                "primary_key": ["site_id", "node_id", "bed_id"],
                "calibrates": [
                    "SensorNetworkSparsePlacementAgent",
                    "SoftSensorMatrixCouplingAgent",
                    "MultiFacilityReplayEvaluationAgent",
                    "RealFieldReplayPipeline",
                ],
            },
            "cost_deployment": {
                "description": "传感器、试剂、催化剂、人工和部署接口的经济性参数。",
                "required_fields": ["item_id", "category", "unit_cost_cny", "quantity", "lead_time_days"],
                "optional_fields": ["vendor", "maintenance_hours_per_month", "interface_point"],
                "primary_key": ["item_id"],
                "calibrates": ["SensitivityAnalysisAgent", "ResourceExpansionAgent", "LongTermEconomicsAgent"],
            },
        }

    @classmethod
    def template_headers(cls) -> dict[str, list[str]]:
        headers: dict[str, list[str]] = {}
        for table, spec in cls.schema_contract().items():
            headers[table] = list(spec["required_fields"]) + list(spec["optional_fields"])
        return headers

    def _datasets_from_readings(self, readings: Sequence[SensorReading]) -> dict[str, list[dict[str, object]]]:
        rows: list[dict[str, object]] = []
        for reading in readings:
            row = {
                "batch_id": "reading_stream",
                "timestamp_min": reading.timestamp_min,
                "cycle_id": reading.cycle_id,
                **reading.values,
            }
            rows.append(row)
        merged = dict(self.datasets)
        merged.setdefault("sensor_timeseries", rows)
        return merged

    def _table_statuses(self, datasets: dict[str, list[dict[str, object]]]) -> dict[str, dict[str, object]]:
        statuses: dict[str, dict[str, object]] = {}
        for table, spec in self.schema_contract().items():
            rows = datasets.get(table, [])
            required_fields = list(spec["required_fields"])
            primary_key = list(spec["primary_key"])
            missing_required = sorted(
                field
                for field in required_fields
                if any(field not in row or row.get(field) in {None, ""} for row in rows)
            )
            duplicate_keys = self._duplicate_keys(rows, primary_key)
            record_count = len(rows)
            minimum = self.minimum_records.get(table, 1)
            field_coverage = 0.0 if not required_fields else (len(required_fields) - len(missing_required)) / len(required_fields)
            volume_coverage = min(1.0, record_count / max(1, minimum))
            table_score = round(0.65 * field_coverage + 0.25 * volume_coverage + 0.10 * float(not duplicate_keys), 3)
            statuses[table] = {
                "record_count": record_count,
                "minimum_records": minimum,
                "required_fields": required_fields,
                "missing_required_fields": missing_required,
                "duplicate_primary_keys": duplicate_keys,
                "field_coverage": round(field_coverage, 3),
                "volume_coverage": round(volume_coverage, 3),
                "table_score": table_score,
                "status": self._table_status(record_count, missing_required, duplicate_keys, volume_coverage),
            }
        return statuses

    @staticmethod
    def _duplicate_keys(rows: list[dict[str, object]], primary_key: list[str]) -> list[str]:
        seen: set[tuple[object, ...]] = set()
        duplicates: list[str] = []
        for row in rows:
            key = tuple(row.get(field) for field in primary_key)
            if any(value in {None, ""} for value in key):
                continue
            if key in seen:
                duplicates.append("|".join(str(value) for value in key))
            seen.add(key)
        return sorted(set(duplicates))

    @staticmethod
    def _table_status(
        record_count: int,
        missing_required: list[str],
        duplicate_keys: list[str],
        volume_coverage: float,
    ) -> str:
        if record_count == 0:
            return "missing_table"
        if missing_required:
            return "schema_incomplete"
        if duplicate_keys:
            return "duplicate_keys"
        if volume_coverage < 0.75:
            return "low_volume"
        return "import_ready"

    @staticmethod
    def _linkage_checks(datasets: dict[str, list[dict[str, object]]]) -> dict[str, object]:
        sensor_batches = {str(row.get("batch_id")) for row in datasets.get("sensor_timeseries", []) if row.get("batch_id")}
        lab_batches = {str(row.get("batch_id")) for row in datasets.get("offline_lab_results", []) if row.get("batch_id")}
        catalyst_batches = {str(row.get("batch_id")) for row in datasets.get("catalyst_lifecycle", []) if row.get("batch_id")}
        operation_batches = {str(row.get("batch_id")) for row in datasets.get("campaign_operation_log", []) if row.get("batch_id")}
        all_reference_batches = lab_batches | catalyst_batches | operation_batches
        orphan_reference_batches = sorted(all_reference_batches - sensor_batches)
        unlabeled_sensor_batches = sorted(sensor_batches - lab_batches)
        operation_without_catalyst = sorted(operation_batches - catalyst_batches)
        score_components = [
            float(not orphan_reference_batches),
            min(1.0, len(lab_batches) / max(1, len(sensor_batches))),
            float(not operation_without_catalyst),
        ]
        linkage_score = round(sum(score_components) / len(score_components), 3)
        return {
            "sensor_batch_count": len(sensor_batches),
            "lab_labeled_batch_count": len(lab_batches),
            "catalyst_batch_count": len(catalyst_batches),
            "operation_batch_count": len(operation_batches),
            "orphan_reference_batches": orphan_reference_batches,
            "unlabeled_sensor_batches": unlabeled_sensor_batches,
            "operation_without_catalyst_batches": operation_without_catalyst,
            "linkage_score": linkage_score,
        }

    def _calibration_tasks(
        self,
        table_statuses: dict[str, dict[str, object]],
        linkage: dict[str, object],
    ) -> list[dict[str, object]]:
        return [
            self._task(
                "P1_sensor_noise_drift",
                "真实传感器噪声、漂移和污染结垢标定",
                ["sensor_timeseries"],
                table_statuses,
                linkage,
                "校准 DataQualityAgent 阈值、采样噪声模型和 sensor_confidence。",
            ),
            self._task(
                "P2_soft_sensor_retraining",
                "软传感器真实标签重训",
                ["sensor_timeseries", "offline_lab_results"],
                table_statuses,
                linkage,
                "重训 soft sensor calibrator，并估计不可观测状态的不确定性。",
            ),
            self._task(
                "P3_catalyst_lifecycle",
                "催化剂寿命、再生收益和副产物风险校准",
                ["catalyst_lifecycle", "offline_lab_results"],
                table_statuses,
                linkage,
                "校准再生/更换门槛、寿命衰减和副产物安全门。",
            ),
            self._task(
                "P4_loop_time_budget",
                "循环、暂存、验证错峰和回退门槛校准",
                ["campaign_operation_log", "offline_lab_results"],
                table_statuses,
                linkage,
                "校准 Agent24-28 的时间预算、错峰收益、恢复爬坡和 fallback triggers。",
            ),
            self._task(
                "P5_cost_deployment",
                "经济性和现场部署接口校准",
                ["cost_deployment", "campaign_operation_log"],
                table_statuses,
                linkage,
                "校准传感器经济性、资源扩容成本、预算释放顺序和 PLC/SCADA 接口。",
            ),
            self._task(
                "P6_pressure_headloss_replay_contract",
                "压降/水头损失候选观测的现场 replay 校准",
                [
                    "sensor_timeseries",
                    "offline_lab_results",
                    "catalyst_lifecycle",
                    "campaign_operation_log",
                    "site_topology_or_bed_geometry",
                ],
                table_statuses,
                linkage,
                "校准 pressure/headloss 是否能作为 catalyst_activity 与 hydraulic anomaly 的候选代理，并保持执行器阻断边界。",
            ),
        ]

    @staticmethod
    def _task(
        task_id: str,
        title: str,
        required_tables: list[str],
        table_statuses: dict[str, dict[str, object]],
        linkage: dict[str, object],
        model_update: str,
    ) -> dict[str, object]:
        table_scores = [float(table_statuses[table]["table_score"]) for table in required_tables]
        table_ready = all(table_statuses[table]["status"] in {"import_ready", "low_volume"} for table in required_tables)
        score = round(0.78 * (sum(table_scores) / len(table_scores)) + 0.22 * float(linkage["linkage_score"]), 3)
        blockers = [
            f"{table}:{table_statuses[table]['status']}"
            for table in required_tables
            if table_statuses[table]["status"] != "import_ready"
        ]
        return {
            "task_id": task_id,
            "title": title,
            "required_tables": required_tables,
            "task_ready": table_ready and not blockers and score >= 0.8,
            "readiness_score": score,
            "blockers": blockers,
            "model_update": model_update,
        }

    def _readiness(
        self,
        table_statuses: dict[str, dict[str, object]],
        linkage: dict[str, object],
    ) -> dict[str, object]:
        table_scores = [float(status["table_score"]) for status in table_statuses.values()]
        field_coverage = sum(float(status["field_coverage"]) for status in table_statuses.values()) / len(table_statuses)
        volume_coverage = sum(float(status["volume_coverage"]) for status in table_statuses.values()) / len(table_statuses)
        table_score = sum(table_scores) / len(table_scores)
        score = round(0.45 * field_coverage + 0.2 * volume_coverage + 0.25 * table_score + 0.1 * float(linkage["linkage_score"]), 3)
        missing_tables = [table for table, status in table_statuses.items() if status["status"] == "missing_table"]
        incomplete_tables = [table for table, status in table_statuses.items() if status["status"] in {"schema_incomplete", "duplicate_keys"}]
        if missing_tables or incomplete_tables:
            interface_status = "schema_blocked"
        elif self.data_origin != "field":
            interface_status = "template_ready_not_field_validated"
        elif score >= 0.86:
            interface_status = "field_calibration_ready"
        else:
            interface_status = "field_package_needs_more_records"
        return {
            "interface_status": interface_status,
            "field_coverage": round(field_coverage, 3),
            "volume_coverage": round(volume_coverage, 3),
            "table_score": round(table_score, 3),
            "linkage_score": linkage["linkage_score"],
            "calibration_readiness_score": score,
            "missing_tables": missing_tables,
            "incomplete_tables": incomplete_tables,
            "data_origin": self.data_origin,
        }

    def _issues(
        self,
        table_statuses: dict[str, dict[str, object]],
        linkage: dict[str, object],
        readiness: dict[str, object],
    ) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        for table, status in table_statuses.items():
            if status["status"] == "missing_table":
                issues.append(
                    QualityIssue(
                        sensor=table,
                        issue_type="missing_field_data_table",
                        severity=Severity.CRITICAL,
                        message=f"{table} 为空，无法支撑对应校准任务。",
                        evidence={"required_fields": status["required_fields"]},
                    )
                )
            elif status["status"] == "schema_incomplete":
                issues.append(
                    QualityIssue(
                        sensor=table,
                        issue_type="field_data_schema_incomplete",
                        severity=Severity.WARNING,
                        message=f"{table} 缺少必需字段：{status['missing_required_fields']}。",
                        evidence=status,
                    )
                )
            elif status["status"] == "duplicate_keys":
                issues.append(
                    QualityIssue(
                        sensor=table,
                        issue_type="field_data_duplicate_primary_key",
                        severity=Severity.WARNING,
                        message=f"{table} 存在重复主键，导入前需要去重。",
                        evidence={"duplicate_primary_keys": status["duplicate_primary_keys"]},
                    )
                )
        if linkage["orphan_reference_batches"]:
            issues.append(
                QualityIssue(
                    sensor="field_data_linkage",
                    issue_type="orphan_reference_batches",
                    severity=Severity.WARNING,
                    message="离线、催化剂或操作日志中存在无法回连到传感时间序列的 batch。",
                    evidence={"orphan_reference_batches": linkage["orphan_reference_batches"]},
                )
            )
        if self.data_origin != "field" and readiness["interface_status"] != "schema_blocked":
            issues.append(
                QualityIssue(
                    sensor="field_data_origin",
                    issue_type="synthetic_template_not_field_validated",
                    severity=Severity.INFO,
                    message="当前数据包可用于接口演示，但不是现场实测数据，不能作为实证校准结论。",
                    evidence={"data_origin": self.data_origin},
                )
            )
        return issues

    @staticmethod
    def _recommendations(readiness: dict[str, object], tasks: list[dict[str, object]]) -> list[str]:
        if readiness["interface_status"] == "schema_blocked":
            return [
                f"优先补齐缺失或不完整表：{readiness['missing_tables'] + readiness['incomplete_tables']}。",
                "按 schema_contract 生成采集模板后，再导入真实传感、离线检测、催化剂和 campaign 日志。",
            ]
        next_tasks = [task for task in tasks if not task["task_ready"]]
        if readiness["interface_status"] == "template_ready_not_field_validated":
            if not next_tasks:
                return [
                    "当前接口模板可运行，下一步用真实现场数据替换 synthetic/sample 行。",
                    "P1-P5 校准任务在字段契约上均已具备模板入口；真实采集时应优先保证 batch_id 可回连。",
                    "先采集同一批次的在线传感时间序列、离线检测标签和 campaign 操作日志，再补催化剂寿命与经济性记录。",
                ]
            return [
                "当前接口模板可运行，下一步用真实现场数据替换 synthetic/sample 行。",
                "优先采集同一 batch_id 下的在线传感时间序列、离线检测标签和 campaign 操作日志，保证可回连。",
                f"最先需要实证推进的校准任务：{[task['task_id'] for task in next_tasks[:3]]}。",
            ]
        return [
            "可以进入真实数据校准：先运行 P1/P2，再把校准参数写回软传感器和数据质控配置。",
            "保留原始数据快照和导入版本号，避免现场数据清洗后无法审计。",
        ]
