from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.agents.field_replay_calibration_gate_agent import FieldReplayCalibrationGateAgent
from water_ai.agents.timestamped_campaign_replay_agent import TimestampedCampaignReplayAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class FieldReplayEvidenceChainAgent(BaseAgent):
    """Run the auditable import -> replay -> G6 chain for field replay calibration."""

    name = "field_replay_evidence_chain_agent"

    def __init__(
        self,
        *,
        import_report: AgentReport | None = None,
        import_metrics: dict[str, object] | None = None,
        matrix_fast_proxy_metrics: dict[str, object] | None = None,
        minimum_proxy_events: int = 12,
    ) -> None:
        self.import_report = import_report
        self.import_metrics = import_metrics or {}
        self.matrix_fast_proxy_metrics = matrix_fast_proxy_metrics or {}
        self.minimum_proxy_events = minimum_proxy_events

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        import_stage = self._import_stage()
        timestamp_report = self._timestamp_report(import_stage)
        g6_report = self._g6_report(timestamp_report)
        chain_readiness = self._chain_readiness(import_stage, timestamp_report, g6_report)
        writeback_candidate = self._writeback_candidate(chain_readiness, g6_report)
        issues = self._issues(import_stage, timestamp_report, g6_report, chain_readiness)
        recommendations = self._recommendations(chain_readiness)
        summary = (
            f"现场 replay 证据链：{chain_readiness['field_replay_evidence_chain_status']}；"
            f"导入通过 {import_stage['import_ready']}，"
            f"G6 保护性候选 {writeback_candidate['can_emit_protective_writeback_candidate']}。"
        )
        confidence = round(
            min(0.92, max(0.14, 0.32 + 0.45 * chain_readiness["field_replay_evidence_chain_score"] - 0.025 * len(issues))),
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
                "import_stage": import_stage,
                "timestamped_replay_stage": self._stage_from_report(timestamp_report, "timestamped_campaign_replay"),
                "g6_stage": self._stage_from_report(g6_report, "field_replay_calibration_gate"),
                "writeback_candidate": writeback_candidate,
                "readiness": chain_readiness,
            },
        )

    def _import_stage(self) -> dict[str, object]:
        metrics = self.import_metrics
        if self.import_report is not None:
            metrics = self.import_report.metrics
        readiness = self._dict(metrics.get("readiness"))
        metadata_audit = self._dict(metrics.get("metadata_audit"))
        export_policy = self._dict(metrics.get("export_policy"))
        normalized_datasets = self._dict(metrics.get("normalized_datasets"))
        import_ready = (
            readiness.get("field_replay_import_status") == "field_replay_import_ready_for_timestamped_replay"
            and readiness.get("can_pass_to_timestamped_replay") is True
            and metadata_audit.get("data_origin") == "field"
            and export_policy.get("allowed_downstream_agent") == "TimestampedCampaignReplayAgent"
            and bool(normalized_datasets)
        )
        missing_reasons: list[str] = []
        if not metrics:
            missing_reasons.append("missing_import_report")
        if readiness.get("field_replay_import_status") != "field_replay_import_ready_for_timestamped_replay":
            missing_reasons.append(str(readiness.get("field_replay_import_status", "import_status_unknown")))
        if metadata_audit.get("data_origin") != "field":
            missing_reasons.append(f"data_origin={metadata_audit.get('data_origin', 'missing')}")
        if not normalized_datasets:
            missing_reasons.append("normalized_datasets_missing")
        return {
            "import_ready": import_ready,
            "import_status": readiness.get("field_replay_import_status", "missing_import_gate"),
            "data_origin": metadata_audit.get("data_origin", "missing"),
            "accepted_table_count": readiness.get("accepted_table_count", 0),
            "total_table_count": readiness.get("total_table_count", 0),
            "can_pass_to_timestamped_replay": bool(readiness.get("can_pass_to_timestamped_replay", False)),
            "can_pass_to_g6": bool(readiness.get("can_pass_to_g6", False)),
            "normalized_datasets": normalized_datasets,
            "blocking_reasons": sorted(set(missing_reasons)),
        }

    def _timestamp_report(self, import_stage: dict[str, object]) -> AgentReport | None:
        if not import_stage["import_ready"]:
            return None
        datasets = self._dict(import_stage.get("normalized_datasets"))
        return TimestampedCampaignReplayAgent(
            datasets={table: list(rows) for table, rows in datasets.items() if isinstance(rows, list)},
            data_origin="field",
            minimum_proxy_events=self.minimum_proxy_events,
        ).run([])

    def _g6_report(self, timestamp_report: AgentReport | None) -> AgentReport | None:
        if timestamp_report is None:
            return None
        return FieldReplayCalibrationGateAgent(
            timestamped_replay_report=timestamp_report,
            matrix_fast_proxy_metrics=self.matrix_fast_proxy_metrics,
            minimum_proxy_events=self.minimum_proxy_events,
        ).run([])

    @staticmethod
    def _chain_readiness(
        import_stage: dict[str, object],
        timestamp_report: AgentReport | None,
        g6_report: AgentReport | None,
    ) -> dict[str, object]:
        timestamp_ready = False
        g6_ready = False
        timestamp_status = "not_run"
        g6_status = "not_run"
        if timestamp_report is not None:
            replay_readiness = timestamp_report.metrics.get("readiness", {})
            if isinstance(replay_readiness, dict):
                timestamp_status = str(replay_readiness.get("timestamped_replay_status", "unknown"))
                timestamp_ready = bool(replay_readiness.get("can_calibrate_fast_proxy", False))
        if g6_report is not None:
            g6_readiness = g6_report.metrics.get("readiness", {})
            if isinstance(g6_readiness, dict):
                g6_status = str(g6_readiness.get("field_replay_gate_status", "unknown"))
                g6_ready = bool(g6_readiness.get("can_write_to_protective_control", False))
        import_ready = bool(import_stage["import_ready"])
        score = round(0.34 * float(import_ready) + 0.28 * float(timestamp_ready) + 0.38 * float(g6_ready), 3)
        if not import_ready:
            status = "field_replay_evidence_chain_blocked_at_import"
        elif not timestamp_ready:
            status = "field_replay_evidence_chain_blocked_at_timestamped_replay"
        elif not g6_ready:
            status = "field_replay_evidence_chain_blocked_at_g6"
        else:
            status = "field_replay_protective_writeback_candidate_ready"
        return {
            "field_replay_evidence_chain_status": status,
            "field_replay_evidence_chain_score": score,
            "import_ready": import_ready,
            "timestamped_replay_ready": timestamp_ready,
            "g6_ready": g6_ready,
            "timestamped_replay_status": timestamp_status,
            "field_replay_gate_status": g6_status,
            "can_emit_protective_writeback_candidate": import_ready and timestamp_ready and g6_ready,
            "can_write_to_release_gate": False,
        }

    @staticmethod
    def _writeback_candidate(chain_readiness: dict[str, object], g6_report: AgentReport | None) -> dict[str, object]:
        g6_writeback = {}
        if g6_report is not None:
            value = g6_report.metrics.get("writeback_policy", {})
            if isinstance(value, dict):
                g6_writeback = value
        can_emit = bool(chain_readiness["can_emit_protective_writeback_candidate"])
        return {
            "target_agent": "MatrixShockFastProxyAgent",
            "candidate_type": "field_protective_control_parameter_update" if can_emit else "no_candidate",
            "can_emit_protective_writeback_candidate": can_emit,
            "can_write_to_release_gate": False,
            "requires_human_review_before_application": True,
            "source_chain": ["FieldReplayImportAgent", "TimestampedCampaignReplayAgent", "FieldReplayCalibrationGateAgent"],
            "g6_writeback_policy": g6_writeback,
        }

    def _issues(
        self,
        import_stage: dict[str, object],
        timestamp_report: AgentReport | None,
        g6_report: AgentReport | None,
        chain_readiness: dict[str, object],
    ) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        if not import_stage["import_ready"]:
            issues.append(
                QualityIssue(
                    sensor="field_replay_evidence_chain",
                    issue_type="import_gate_not_passed",
                    severity=Severity.CRITICAL,
                    message="未通过 Agent44 导入门时，不得运行或采纳 Agent42/Agent43 现场校准结论。",
                    evidence={key: value for key, value in import_stage.items() if key != "normalized_datasets"},
                )
            )
        for report in (timestamp_report, g6_report):
            if report is None:
                continue
            issues.extend(report.issues)
        if chain_readiness["can_write_to_release_gate"]:
            issues.append(
                QualityIssue(
                    sensor="field_replay_evidence_chain",
                    issue_type="release_gate_writeback_forbidden",
                    severity=Severity.CRITICAL,
                    message="现场 replay 证据链通过也不能授权自动放行门。",
                    evidence=chain_readiness,
                )
            )
        return issues

    @staticmethod
    def _recommendations(chain_readiness: dict[str, object]) -> list[str]:
        status = str(chain_readiness["field_replay_evidence_chain_status"])
        if status == "field_replay_protective_writeback_candidate_ready":
            return [
                "证据链已形成保护性控制写回候选；应用前仍需人工复核、现场运行窗口确认和 release gate 独立校准。",
                "写回后必须重跑 matrix_shock、clean_release 和 oxidant_limitation replay，确认误触发成本和安全边界。",
            ]
        if status == "field_replay_evidence_chain_blocked_at_import":
            return [
                "先补真实 metadata.json 与四张 replay CSV，并通过 Agent44；不要单独运行 Agent42/Agent43 来绕过导入门。",
                "synthetic/sample 包只能作为接口联调，不能产生任何现场保护性写回候选。",
            ]
        if status == "field_replay_evidence_chain_blocked_at_timestamped_replay":
            return [
                "修复 timestamp coverage、result_time_min、effect_time_min、field_label_matrix_shock 或 proxy label 数量后重新运行证据链。",
            ]
        return [
            "修复 G6/P6 失败门，尤其是 precision/recall、保护性提前量、执行器延迟和误触发成本。",
        ]

    @staticmethod
    def _stage_from_report(report: AgentReport | None, stage_name: str) -> dict[str, object]:
        if report is None:
            return {"stage_name": stage_name, "stage_status": "not_run"}
        return {
            "stage_name": stage_name,
            "agent_name": report.agent_name,
            "confidence": report.confidence,
            "summary": report.summary,
            "readiness": report.metrics.get("readiness", {}),
            "issue_types": [issue.issue_type for issue in report.issues],
        }

    @staticmethod
    def _method_contract() -> dict[str, object]:
        return {
            "upgrade_id": "field_replay_import_to_g6_evidence_chain",
            "borrowed_from": [
                "academic_research_agent_evidence_before_claims",
                "model_validation_and_uncertainty_provenance_checks",
                "timestamped_campaign_replay_for_fast_proxy_validation",
                "field_replay_calibration_gate_for_fast_proxy_writeback",
            ],
            "reality_mapping": "把 Agent44 导入门、Agent42 时间戳回放和 Agent43 G6/P6 变成不可绕过的现场校准证据链，只有完整链条通过才形成保护性控制写回候选。",
            "data_needs": [
                "agent44_import_ready_report",
                "normalized_field_replay_datasets",
                "field_label_matrix_shock",
                "result_time_min",
                "effect_time_min",
                "false_positive_cost_index",
                "matrix_fast_proxy_release_boundary",
            ],
            "implementation_path": [
                "src/water_ai/agents/field_replay_evidence_chain_agent.py",
                "experiments/run_agent45_field_replay_evidence_chain.py",
                "outputs/field_replay_evidence_chain/evidence_chain_metrics.json",
            ],
            "evaluation_metrics": [
                "field_replay_evidence_chain_score",
                "import_ready",
                "timestamped_replay_ready",
                "g6_ready",
                "can_emit_protective_writeback_candidate",
            ],
            "failure_boundary": "证据链通过也只形成保护性控制候选，不能自动写入现场 PLC/SCADA，不能替代 release gate、污染物达标或 field conformal calibration。",
        }

    @staticmethod
    def _dict(value: object) -> dict[str, object]:
        return value if isinstance(value, dict) else {}
