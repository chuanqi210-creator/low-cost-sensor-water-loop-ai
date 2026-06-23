from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class FieldReplayCalibrationGateAgent(BaseAgent):
    """Turn timestamped replay metrics into a hard G6/P6 field-calibration gate."""

    name = "field_replay_calibration_gate_agent"

    def __init__(
        self,
        *,
        timestamped_replay_report: AgentReport | None = None,
        timestamped_replay_metrics: dict[str, object] | None = None,
        matrix_fast_proxy_metrics: dict[str, object] | None = None,
        minimum_proxy_events: int = 12,
        minimum_precision: float = 0.82,
        minimum_recall: float = 0.78,
        minimum_timestamp_coverage: float = 0.95,
        minimum_protective_lead_time_min: float = 30.0,
        maximum_actuator_p90_latency_min: float = 15.0,
        maximum_false_positive_cost_index: float = 0.15,
    ) -> None:
        self.timestamped_replay_report = timestamped_replay_report
        self.timestamped_replay_metrics = timestamped_replay_metrics or {}
        self.matrix_fast_proxy_metrics = matrix_fast_proxy_metrics or {}
        self.minimum_proxy_events = minimum_proxy_events
        self.minimum_precision = minimum_precision
        self.minimum_recall = minimum_recall
        self.minimum_timestamp_coverage = minimum_timestamp_coverage
        self.minimum_protective_lead_time_min = minimum_protective_lead_time_min
        self.maximum_actuator_p90_latency_min = maximum_actuator_p90_latency_min
        self.maximum_false_positive_cost_index = maximum_false_positive_cost_index

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        replay = self._replay_payload()
        gate_results = self._gate_results(replay)
        writeback = self._writeback_policy(gate_results)
        readiness = self._readiness(gate_results, writeback)
        issues = self._issues(gate_results, readiness)
        recommendations = self._recommendations(readiness, writeback)
        summary = (
            f"现场回放校准门：{readiness['field_replay_gate_status']}；"
            f"G6 {gate_results['accepted_gate_count']}/{gate_results['total_gate_count']}，"
            f"保护性写回 {writeback['can_write_to_protective_control']}。"
        )
        confidence = round(
            min(0.92, max(0.16, 0.34 + 0.44 * readiness["field_replay_gate_score"] - 0.03 * len(issues))),
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
                "thresholds": self._thresholds(),
                "timestamped_replay": replay,
                "gate_results": gate_results,
                "writeback_policy": writeback,
                "readiness": readiness,
            },
        )

    def _replay_payload(self) -> dict[str, object]:
        metrics = self.timestamped_replay_metrics
        if self.timestamped_replay_report is not None:
            metrics = self.timestamped_replay_report.metrics
        readiness = self._dict(metrics.get("readiness"))
        replay_metrics = self._dict(metrics.get("replay_metrics"))
        table_audit = self._dict(metrics.get("table_audit"))
        linkage = self._dict(metrics.get("linkage"))
        matrix_readiness = self._matrix_readiness()
        return {
            "data_origin": str(metrics.get("data_origin", "unknown")),
            "timestamped_replay_status": str(readiness.get("timestamped_replay_status", "unknown")),
            "timestamp_coverage": self._number(readiness, "timestamp_coverage", self._number(replay_metrics, "timestamp_coverage", 0.0)),
            "can_calibrate_fast_proxy": bool(readiness.get("can_calibrate_fast_proxy", False)),
            "can_write_to_protective_control": bool(readiness.get("can_write_to_protective_control", False)),
            "proxy_label_count": int(self._number(replay_metrics, "proxy_label_count", 0.0)),
            "proxy_precision": self._number(replay_metrics, "proxy_precision", 0.0),
            "proxy_recall": self._number(replay_metrics, "proxy_recall", 0.0),
            "mean_protective_action_lead_time_min": self._number(replay_metrics, "mean_protective_action_lead_time_min", 0.0),
            "p90_lab_turnaround_min": self._number(replay_metrics, "p90_lab_turnaround_min", 0.0),
            "p90_actuator_latency_min": self._number(replay_metrics, "p90_actuator_latency_min", 999.0),
            "mean_false_positive_cost_index": self._number(replay_metrics, "mean_false_positive_cost_index", 1.0),
            "table_audit": table_audit,
            "linkage": linkage,
            "matrix_fast_proxy_readiness": matrix_readiness,
        }

    def _gate_results(self, replay: dict[str, object]) -> dict[str, object]:
        table_audit = self._dict(replay.get("table_audit"))
        linkage = self._dict(replay.get("linkage"))
        table_statuses = {
            table: self._dict(audit).get("status")
            for table, audit in table_audit.items()
        }
        failed_tables = sorted(table for table, status in table_statuses.items() if status != "timestamp_ready")
        orphan_batches = list(linkage.get("orphan_reference_batches", [])) if isinstance(linkage.get("orphan_reference_batches"), list) else []
        unlabeled_proxy_batches = list(linkage.get("unlabeled_proxy_batches", [])) if isinstance(linkage.get("unlabeled_proxy_batches"), list) else []
        matrix_readiness = self._dict(replay.get("matrix_fast_proxy_readiness"))
        release_blocked = matrix_readiness.get("can_write_to_release_gate") is False or matrix_readiness == {}
        gates = [
            self._gate(
                "G6_1_field_origin",
                replay["data_origin"] == "field",
                "data_origin 必须为 field，synthetic/sample 不得写入快代理控制。",
                {"data_origin": replay["data_origin"]},
            ),
            self._gate(
                "G6_2_timestamp_schema_ready",
                not failed_tables and float(replay["timestamp_coverage"]) >= self.minimum_timestamp_coverage,
                "四张 replay 表必须时间戳完整，且 timestamp coverage 达标。",
                {"failed_tables": failed_tables, "timestamp_coverage": replay["timestamp_coverage"]},
            ),
            self._gate(
                "G6_3_batch_linkage_complete",
                not orphan_batches and not unlabeled_proxy_batches,
                "sensor、lab、operation 和 fast_proxy_event_log 必须能按 batch_id 回连。",
                {"orphan_reference_batches": orphan_batches, "unlabeled_proxy_batches": unlabeled_proxy_batches},
            ),
            self._gate(
                "G6_4_proxy_label_volume",
                int(replay["proxy_label_count"]) >= self.minimum_proxy_events,
                "快代理验证必须有足够 field-labeled events。",
                {"proxy_label_count": replay["proxy_label_count"], "minimum_proxy_events": self.minimum_proxy_events},
            ),
            self._gate(
                "G6_5_proxy_precision_recall",
                float(replay["proxy_precision"]) >= self.minimum_precision and float(replay["proxy_recall"]) >= self.minimum_recall,
                "快代理 precision/recall 必须同时达标。",
                {"proxy_precision": replay["proxy_precision"], "proxy_recall": replay["proxy_recall"]},
            ),
            self._gate(
                "G6_6_latency_action_margin",
                float(replay["mean_protective_action_lead_time_min"]) >= self.minimum_protective_lead_time_min
                and float(replay["p90_actuator_latency_min"]) <= self.maximum_actuator_p90_latency_min,
                "保护性动作必须早于慢标签足够长时间，且执行器 P90 延迟不能过高。",
                {
                    "mean_protective_action_lead_time_min": replay["mean_protective_action_lead_time_min"],
                    "p90_actuator_latency_min": replay["p90_actuator_latency_min"],
                },
            ),
            self._gate(
                "G6_7_false_positive_cost",
                float(replay["mean_false_positive_cost_index"]) <= self.maximum_false_positive_cost_index,
                "误触发成本必须低于保护性控制可接受阈值。",
                {"mean_false_positive_cost_index": replay["mean_false_positive_cost_index"]},
            ),
            self._gate(
                "G6_8_release_boundary_preserved",
                release_blocked,
                "快代理只能写入保护性控制，不能写入自动放行门。",
                {"matrix_fast_proxy_readiness": matrix_readiness},
            ),
        ]
        accepted = sum(1 for gate in gates if gate["accepted"])
        return {
            "gates": gates,
            "accepted_gate_count": accepted,
            "total_gate_count": len(gates),
            "failed_gate_ids": [str(gate["gate_id"]) for gate in gates if not gate["accepted"]],
            "blocking_gate_ids": [str(gate["gate_id"]) for gate in gates if not gate["accepted"] and str(gate["gate_id"]).startswith(("G6_1", "G6_2", "G6_3"))],
            "calibration_gate_ids": [str(gate["gate_id"]) for gate in gates if not gate["accepted"] and not str(gate["gate_id"]).startswith(("G6_1", "G6_2", "G6_3"))],
        }

    def _writeback_policy(self, gate_results: dict[str, object]) -> dict[str, object]:
        ready = not gate_results["failed_gate_ids"]
        return {
            "target_agent": "MatrixShockFastProxyAgent",
            "parameter_scope": [
                "field_proxy_precision",
                "field_proxy_recall",
                "protective_action_lead_time_min",
                "false_positive_cost_index",
                "protective_trigger_boundary",
            ],
            "can_write_to_protective_control": ready,
            "can_write_to_release_gate": False,
            "release_policy": "block_release_until_lab_and_field_conformal_calibration",
            "writeback_mode": "field_protective_control_gate" if ready else "blocked_until_field_replay_passes_g6",
            "blocked_by": gate_results["failed_gate_ids"],
        }

    @staticmethod
    def _readiness(gate_results: dict[str, object], writeback: dict[str, object]) -> dict[str, object]:
        accepted = int(gate_results["accepted_gate_count"])
        total = int(gate_results["total_gate_count"])
        score = round(accepted / max(1, total), 3)
        failed = list(gate_results["failed_gate_ids"])
        blocking = list(gate_results["blocking_gate_ids"])
        if not failed:
            status = "field_fast_proxy_protective_control_gate_ready"
        elif "G6_1_field_origin" in failed:
            status = "synthetic_replay_gate_blocked"
        elif blocking:
            status = "field_replay_schema_gate_failed"
        else:
            status = "field_fast_proxy_calibration_gate_failed"
        return {
            "field_replay_gate_status": status,
            "field_replay_gate_score": score,
            "accepted_gate_count": accepted,
            "total_gate_count": total,
            "failed_gate_ids": failed,
            "can_write_to_protective_control": bool(writeback["can_write_to_protective_control"]),
            "can_write_to_release_gate": False,
        }

    def _issues(self, gate_results: dict[str, object], readiness: dict[str, object]) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        for gate in gate_results["gates"]:
            if gate["accepted"]:
                continue
            severity = Severity.CRITICAL if gate["gate_id"] in {"G6_1_field_origin", "G6_2_timestamp_schema_ready", "G6_3_batch_linkage_complete"} else Severity.WARNING
            issues.append(
                QualityIssue(
                    sensor="field_replay_calibration_gate",
                    issue_type=str(gate["gate_id"]),
                    severity=severity,
                    message=str(gate["rule"]),
                    evidence=gate["evidence"] if isinstance(gate["evidence"], dict) else {},
                )
            )
        if readiness["can_write_to_release_gate"]:
            issues.append(
                QualityIssue(
                    sensor="field_replay_calibration_gate",
                    issue_type="release_gate_writeback_forbidden",
                    severity=Severity.CRITICAL,
                    message="快代理现场回放通过也不能授权自动放行。",
                    evidence=readiness,
                )
            )
        return issues

    @staticmethod
    def _recommendations(readiness: dict[str, object], writeback: dict[str, object]) -> list[str]:
        if readiness["can_write_to_protective_control"]:
            return [
                "G6/P6 已允许把快代理参数写入保护性控制，但 release gate 仍必须等待离线标签和 field conformal calibration。",
                "写回后应重跑 matrix_shock、clean_release 和 oxidant_limitation 三类 replay，检查误触发成本和安全边界。",
            ]
        return [
            "不要把当前 replay 写入保护性控制；先补齐失败的 G6 gate。",
            "优先采集真实 field-labeled fast_proxy_event_log，并保留 result_time_min、effect_time_min、field_label_matrix_shock 和 false_positive_cost_index。",
            "synthetic replay 只能作为接口联调，不得作为现场 precision/recall 或保护性控制证据。",
        ]

    def _thresholds(self) -> dict[str, object]:
        return {
            "minimum_proxy_events": self.minimum_proxy_events,
            "minimum_precision": self.minimum_precision,
            "minimum_recall": self.minimum_recall,
            "minimum_timestamp_coverage": self.minimum_timestamp_coverage,
            "minimum_protective_lead_time_min": self.minimum_protective_lead_time_min,
            "maximum_actuator_p90_latency_min": self.maximum_actuator_p90_latency_min,
            "maximum_false_positive_cost_index": self.maximum_false_positive_cost_index,
        }

    @staticmethod
    def _method_contract() -> dict[str, object]:
        return {
            "upgrade_id": "field_replay_calibration_gate_for_fast_proxy_writeback",
            "borrowed_from": [
                "timestamped_campaign_replay_for_fast_proxy_validation",
                "model_validation_and_uncertainty_skill",
                "academic_research_agent_evidence_before_claims",
                "matrix_shock_fast_proxy_latency_aware_control",
            ],
            "reality_mapping": "把真实 timestamped replay 指标转化为 G6/P6 验收门，只有 field-labeled precision/recall、提前量和误触发成本达标时才允许写入保护性控制。",
            "data_needs": [
                "field_origin_timestamped_replay",
                "result_time_min",
                "effect_time_min",
                "field_label_matrix_shock",
                "false_positive_cost_index",
                "proxy_precision",
                "proxy_recall",
            ],
            "implementation_path": [
                "src/water_ai/agents/field_replay_calibration_gate_agent.py",
                "experiments/run_agent43_field_replay_calibration_gate.py",
                "outputs/field_replay_calibration_gate/g6_p6_gate_metrics.json",
            ],
            "evaluation_metrics": [
                "G6_gate_pass_rate",
                "proxy_precision",
                "proxy_recall",
                "protective_action_lead_time_min",
                "false_positive_cost_index",
                "writeback_mode",
            ],
            "failure_boundary": "G6/P6 通过只允许写入 matrix_shock 保护性控制；不能替代污染物达标、离线标签或 release conformal calibration。",
        }

    @staticmethod
    def _gate(gate_id: str, accepted: bool, rule: str, evidence: dict[str, object]) -> dict[str, object]:
        return {
            "gate_id": gate_id,
            "accepted": bool(accepted),
            "rule": rule,
            "evidence": evidence,
        }

    def _matrix_readiness(self) -> dict[str, object]:
        readiness = self._dict(self.matrix_fast_proxy_metrics.get("readiness"))
        if readiness:
            return readiness
        if "scenario_reports" in self.matrix_fast_proxy_metrics:
            scenarios = self._dict(self.matrix_fast_proxy_metrics.get("scenario_reports"))
            matrix = self._dict(scenarios.get("matrix_shock"))
            return self._dict(matrix.get("readiness"))
        return {}

    @staticmethod
    def _dict(value: object) -> dict[str, object]:
        return value if isinstance(value, dict) else {}

    @staticmethod
    def _number(data: dict[str, object], key: str, default: float) -> float:
        value = data.get(key)
        if isinstance(value, int | float):
            return float(value)
        return default
