from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class FieldCalibrationGateAgent(BaseAgent):
    """Plan the gate between template-ready data interfaces and field calibration."""

    name = "field_calibration_gate_agent"

    def __init__(
        self,
        *,
        field_data_metrics: dict[str, object] | None = None,
        latest_regression: str = "unknown",
    ) -> None:
        self.field_data_metrics = field_data_metrics or {}
        self.latest_regression = latest_regression

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        core = self._core()
        acceptance_gates = self._acceptance_gates(core)
        calibration_sequence = self._calibration_sequence(core)
        writeback_plan = self._writeback_plan()
        runbook = self._runbook(core, acceptance_gates)
        readiness = self._readiness(core, acceptance_gates)
        issues = self._issues(core, readiness)
        recommendations = self._recommendations(readiness)
        summary = (
            f"实证校准门控：{readiness['calibration_gate_status']}；"
            f"数据门 {readiness['accepted_gate_count']}/{readiness['total_gate_count']} 通过。"
        )
        confidence = round(min(0.9, max(0.25, 0.42 + 0.42 * readiness["gate_score"] - 0.03 * len(issues))), 3)

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "core": core,
                "acceptance_gates": acceptance_gates,
                "calibration_sequence": calibration_sequence,
                "writeback_plan": writeback_plan,
                "runbook": runbook,
                "readiness": readiness,
            },
        )

    def _core(self) -> dict[str, object]:
        readiness = self.field_data_metrics.get("readiness", {})
        if not isinstance(readiness, dict):
            readiness = {}
        linkage = self.field_data_metrics.get("linkage_checks", {})
        if not isinstance(linkage, dict):
            linkage = {}
        table_statuses = self.field_data_metrics.get("table_statuses", {})
        if not isinstance(table_statuses, dict):
            table_statuses = {}
        tasks = self.field_data_metrics.get("calibration_tasks", [])
        if not isinstance(tasks, list):
            tasks = []
        data_origin = str(self.field_data_metrics.get("data_origin", readiness.get("data_origin", "unknown")))
        return {
            "data_origin": data_origin,
            "interface_status": readiness.get("interface_status", "unknown"),
            "calibration_readiness_score": readiness.get("calibration_readiness_score", 0.0),
            "field_coverage": readiness.get("field_coverage", 0.0),
            "volume_coverage": readiness.get("volume_coverage", 0.0),
            "linkage_score": linkage.get("linkage_score", readiness.get("linkage_score", 0.0)),
            "table_statuses": table_statuses,
            "calibration_tasks": tasks,
            "latest_regression": self.latest_regression,
        }

    @staticmethod
    def _acceptance_gates(core: dict[str, object]) -> list[dict[str, object]]:
        table_statuses = core["table_statuses"]
        assert isinstance(table_statuses, dict)
        gate_specs = [
            {
                "gate_id": "G0_data_origin",
                "title": "真实数据来源确认",
                "required_tables": [],
                "acceptance_rule": "data_origin 必须为 field，且保留原始数据快照、导入版本号和采样说明。",
                "model_target": "所有后续校准任务",
                "minimum_field_package": "至少 3 个真实 batch 的在线传感、离线标签和操作日志。",
            },
            {
                "gate_id": "G1_sensor_stream_quality",
                "title": "传感时间序列验收",
                "required_tables": ["sensor_timeseries"],
                "acceptance_rule": "每个 batch 至少覆盖完整循环窗口；主键 batch_id+timestamp_min 无重复；传感器状态可追溯。",
                "model_target": "DataQualityAgent / SoftSensorAgent",
                "minimum_field_package": "每个 batch >= 24 条记录，建议包含清洗前后和一次低流量扰动。",
            },
            {
                "gate_id": "G2_lab_label_alignment",
                "title": "离线检测标签对齐",
                "required_tables": ["sensor_timeseries", "offline_lab_results"],
                "acceptance_rule": "离线标签必须能回连同一 batch 的传感窗口，并含 qa_flag、method 和单位。",
                "model_target": "SoftSensorAgent / ValidationPlanningAgent / release_gate",
                "minimum_field_package": "每个关键 batch 至少 2 个标签时点，覆盖处理前/后或回流前/后。",
            },
            {
                "gate_id": "G3_catalyst_lifecycle_alignment",
                "title": "催化剂寿命与副产物风险对齐",
                "required_tables": ["catalyst_lifecycle", "offline_lab_results"],
                "acceptance_rule": "催化剂活性、压降、再生次数和寿命比例必须能回连 batch_id 与离线标签。",
                "model_target": "CatalystLifecycleAgent / RecoveryStrategyWritebackAgent",
                "minimum_field_package": "至少覆盖新鲜、再生后和活性下降三个状态点。",
            },
            {
                "gate_id": "G4_loop_time_budget_alignment",
                "title": "循环时间预算与回退门槛验收",
                "required_tables": ["campaign_operation_log", "offline_lab_results"],
                "acceptance_rule": "动作开始/结束、验证耗时、回流/暂存参数和成功标记必须完整。",
                "model_target": "CampaignTelemetryAgent / RecoveryRampAgent / RecoveryOnlineControlAgent",
                "minimum_field_package": "至少 1 个完整 campaign，含一次回流或暂存动作。",
            },
            {
                "gate_id": "G5_cost_deployment_alignment",
                "title": "成本和部署接口验收",
                "required_tables": ["cost_deployment", "campaign_operation_log"],
                "acceptance_rule": "传感器、试剂、催化剂、人工与接口成本必须可追溯到部署项和 lead time。",
                "model_target": "SensitivityAnalysisAgent / ResourceExpansionAgent / LongTermEconomicsAgent",
                "minimum_field_package": "至少包含传感器、离线检测、催化剂、氧化剂和 PLC/SCADA 接口条目。",
            },
        ]
        gates: list[dict[str, object]] = []
        for spec in gate_specs:
            required_tables = list(spec["required_tables"])
            blockers = []
            for table in required_tables:
                status = table_statuses.get(table, {})
                if not isinstance(status, dict) or status.get("status") != "import_ready":
                    blockers.append(f"{table}:{status.get('status', 'missing')}")
            if spec["gate_id"] == "G0_data_origin" and core["data_origin"] != "field":
                blockers.append(f"data_origin:{core['data_origin']}")
            gate_score = 1.0 if not blockers else 0.55 if required_tables else 0.0
            gates.append(
                {
                    **spec,
                    "gate_ready": not blockers,
                    "gate_score": gate_score,
                    "blockers": blockers,
                    "current_evidence": _current_evidence(required_tables, table_statuses, core),
                }
            )
        return gates

    @staticmethod
    def _calibration_sequence(core: dict[str, object]) -> list[dict[str, object]]:
        task_lookup = {
            str(task.get("task_id")): task
            for task in core["calibration_tasks"]
            if isinstance(task, dict)
        }
        sequence = [
            ("P0_field_snapshot", "冻结现场原始数据快照", "先建立 raw/imported/accepted 三层数据目录，记录采样设备、人员和导入版本。"),
            ("P1_sensor_noise_drift", "标定传感噪声与漂移", "更新 DataQualityAgent 阈值、sensor_confidence 和采样噪声模型。"),
            ("P2_soft_sensor_retraining", "重训软传感器", "用离线标签校准污染物残留、反应完成度、副产物风险和达标概率。"),
            ("P3_catalyst_lifecycle", "校准催化剂寿命", "更新再生/更换门槛、寿命衰减和压降风险。"),
            ("P4_loop_time_budget", "校准循环时间预算", "更新暂存/回流/验证错峰收益和 0.75/0.60 恢复边界。"),
            ("P5_cost_deployment", "校准成本与部署接口", "更新传感器经济性、资源扩容成本和 PLC/SCADA 接口约束。"),
        ]
        return [
            {
                "phase_id": phase_id,
                "title": title,
                "action": action,
                "upstream_task_ready": bool(task_lookup.get(phase_id, {}).get("task_ready", phase_id == "P0_field_snapshot")),
                "current_blockers": task_lookup.get(phase_id, {}).get("blockers", []),
            }
            for phase_id, title, action in sequence
        ]

    @staticmethod
    def _writeback_plan() -> list[dict[str, str]]:
        return [
            {"target": "DataQualityAgent", "writeback": "sensor_ranges、rate_limits、flatline_eps、sensor_confidence thresholds"},
            {"target": "SoftSensorAgent", "writeback": "soft_sensor_calibrator、label windows、uncertainty calibration"},
            {"target": "ValidationPlanningAgent", "writeback": "offline validation delay、release gate、qa_flag weighting"},
            {"target": "CatalystLifecycleAgent", "writeback": "regen threshold、replacement urgency、lifetime decay curve"},
            {"target": "RecoveryOnlineControlAgent", "writeback": "next_intake_fraction、fallback triggers、campaign review gates"},
            {"target": "LongTermEconomicsAgent", "writeback": "unit costs、lead times、staff capacity、deployment interface points"},
        ]

    @staticmethod
    def _runbook(core: dict[str, object], acceptance_gates: list[dict[str, object]]) -> list[dict[str, object]]:
        return [
            {
                "step": "R1_collect",
                "title": "采集最小现场数据包",
                "detail": "先围绕同一批次采集 sensor_timeseries、offline_lab_results 和 campaign_operation_log，再补 catalyst_lifecycle 与 cost_deployment。",
                "exit_criteria": "G0-G2 通过，且 batch_id 可回连。",
            },
            {
                "step": "R2_accept",
                "title": "运行验收门",
                "detail": "逐表检查必需字段、主键重复、记录量、qa_flag、时间窗口和跨表 batch_id。",
                "exit_criteria": f"当前通过 {sum(1 for gate in acceptance_gates if gate['gate_ready'])}/{len(acceptance_gates)} 个 gate。",
            },
            {
                "step": "R3_calibrate",
                "title": "按 P1-P5 写回模型",
                "detail": "先写回数据质控和软传感，再写回催化剂、时间预算和成本部署参数。",
                "exit_criteria": "校准后重新运行 closed_loop、scenario_sweep、robustness 和 recovery online control。",
            },
            {
                "step": "R4_audit",
                "title": "形成现场校准审计包",
                "detail": "保留原始数据、清洗脚本、参数 diff、回归结果和边界说明。",
                "exit_criteria": f"回归结果不低于当前基线：{core['latest_regression']}。",
            },
        ]

    @staticmethod
    def _readiness(core: dict[str, object], acceptance_gates: list[dict[str, object]]) -> dict[str, object]:
        accepted = sum(1 for gate in acceptance_gates if gate["gate_ready"])
        total = len(acceptance_gates)
        gate_score = round(sum(float(gate["gate_score"]) for gate in acceptance_gates) / max(1, total), 3)
        if core["data_origin"] != "field":
            status = "calibration_protocol_ready_waiting_for_field_data"
        elif accepted == total and float(core["calibration_readiness_score"]) >= 0.86:
            status = "field_calibration_can_start"
        else:
            status = "field_package_needs_gate_fixes"
        return {
            "calibration_gate_status": status,
            "gate_score": gate_score,
            "accepted_gate_count": accepted,
            "total_gate_count": total,
            "data_origin": core["data_origin"],
            "field_data_required": core["data_origin"] != "field",
            "blocking_gates": [gate["gate_id"] for gate in acceptance_gates if not gate["gate_ready"]],
        }

    @staticmethod
    def _issues(core: dict[str, object], readiness: dict[str, object]) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        if readiness["field_data_required"]:
            issues.append(
                QualityIssue(
                    sensor="field_calibration_gate",
                    issue_type="field_data_required_before_calibration",
                    severity=Severity.INFO,
                    message="当前只能生成校准门控和采集验收计划；必须导入真实 field 数据后才能执行参数校准。",
                    evidence={"data_origin": core["data_origin"], "blocking_gates": readiness["blocking_gates"]},
                )
            )
        elif readiness["calibration_gate_status"] != "field_calibration_can_start":
            issues.append(
                QualityIssue(
                    sensor="field_calibration_gate",
                    issue_type="field_package_needs_gate_fixes",
                    severity=Severity.WARNING,
                    message="现场数据包仍有验收门未通过，暂不应写回模型参数。",
                    evidence=readiness,
                )
            )
        return issues

    @staticmethod
    def _recommendations(readiness: dict[str, object]) -> list[str]:
        if readiness["calibration_gate_status"] == "calibration_protocol_ready_waiting_for_field_data":
            return [
                "先按 G0-G2 采集最小现场数据包：传感时间序列、离线标签和 campaign 操作日志。",
                "不要用 synthetic/sample 行重训软传感器；它们只用于接口演示和脚本联调。",
                "现场数据通过验收门后，再按 P1-P5 顺序写回模型参数并重跑全链条回归。",
            ]
        if readiness["calibration_gate_status"] == "field_package_needs_gate_fixes":
            return [
                f"先修复未通过的验收门：{readiness['blocking_gates']}。",
                "修复后重新运行 Agent30 和 Agent34，再进入参数写回。",
            ]
        return [
            "可以启动实证校准：先写回 DataQualityAgent 与 SoftSensorAgent，再逐步写回催化剂、时间预算和成本部署参数。",
            "每次写回后运行 scenario_sweep、closed_loop_robustness 和 recovery online control，保留参数 diff。",
        ]


def _current_evidence(
    required_tables: list[str],
    table_statuses: dict[str, object],
    core: dict[str, object],
) -> dict[str, object]:
    def table_evidence(table: str) -> dict[str, object]:
        status = table_statuses.get(table, {})
        if not isinstance(status, dict):
            status = {}
        return {
            "status": status.get("status"),
            "record_count": status.get("record_count"),
            "field_coverage": status.get("field_coverage"),
            "volume_coverage": status.get("volume_coverage"),
        }

    return {
        "data_origin": core["data_origin"],
        "tables": {table: table_evidence(table) for table in required_tables},
    }
