from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RealFieldPackageAcceptanceGate:
    """Facade for the R7 real field package import/replay/holdout acceptance gate."""

    field_replay_import_metrics: dict[str, Any]
    timestamped_replay_metrics: dict[str, Any]
    field_replay_gate_metrics: dict[str, Any]
    field_replay_evidence_chain_metrics: dict[str, Any]
    soft_sensor_field_holdout_gate_metrics: dict[str, Any]
    claim_specific_package_metrics: dict[str, Any]
    unified_field_evidence_gate_metrics: dict[str, Any]
    multi_facility_replay_evaluation_metrics: dict[str, Any] = field(default_factory=dict)

    def build(self) -> dict[str, Any]:
        matrix = self._acceptance_matrix()
        readiness = self._readiness(matrix)
        return {
            "method_contract": self._method_contract(),
            "minimum_real_field_package": self._minimum_real_field_package(),
            "acceptance_matrix": matrix,
            "readiness": readiness,
            "writeback_policy": self._writeback_policy(readiness),
            "next_refactor_action": self._next_refactor_action(readiness),
        }

    @staticmethod
    def _method_contract() -> dict[str, Any]:
        return {
            "upgrade_id": "R7_real_field_package_import_acceptance_gate",
            "borrowed_from": [
                "field data package acceptance gates",
                "timestamped campaign replay validation",
                "soft sensor field holdout release gate",
                "multi-facility replay control-promotion gate",
                "evidence-before-claims workflow",
                "human-reviewed field deployment gate",
            ],
            "reality_mapping": (
                "把真实 sensor/lab/operation/catalyst 数据包导入、timestamped replay、G6/P6 保护性控制门、"
                "软传感 field holdout 和 claim-specific 采集包验收合成一个 R7 总门。"
            ),
            "data_needs": [
                "metadata.json with data_origin=field",
                "sensor_timeseries.csv",
                "offline_lab_results.csv",
                "campaign_operation_log.csv",
                "fast_proxy_event_log.csv",
                "catalyst_lifecycle.csv",
                "claim-specific holdout labels and chain-of-custody metadata",
            ],
            "evaluation_metrics": [
                "field_package_import_pass",
                "timestamped_replay_pass",
                "field_replay_evidence_chain_pass",
                "multi_facility_control_promotion_pass",
                "catalyst_proxy_field_validation_pass",
                "soft_sensor_field_holdout_gate_pass",
                "claim_specific_field_package_pass",
                "field_supported_edge_ratio",
            ],
            "failure_boundary": (
                "R7 can produce acceptance status and human-review candidates only. It must not treat synthetic templates as field replay, "
                "must not bypass offline lab confirmation, and must not auto-write actuator or release-gate policy."
            ),
        }

    @staticmethod
    def _minimum_real_field_package() -> dict[str, Any]:
        return {
            "metadata_required_fields": [
                "data_origin",
                "site_id",
                "campaign_id",
                "sampling_start",
                "sampling_end",
                "operator_id",
                "instrument_snapshot_id",
                "chain_of_custody_id",
            ],
            "metadata_required_values": {
                "data_origin": "field",
            },
            "csv_tables": [
                "sensor_timeseries.csv",
                "offline_lab_results.csv",
                "campaign_operation_log.csv",
                "fast_proxy_event_log.csv",
                "catalyst_lifecycle.csv",
                "cost_deployment.csv",
            ],
            "guardrail_required_fields": [
                "proxy_holdout_label",
                "regeneration_event",
                "tank_storage_margin",
                "actuator_latency_p90",
                "pump_valve_result",
                "hold_time_min",
                "recycle_ratio",
            ],
            "minimum_gate_sequence": [
                "Agent44 field origin/import gate",
                "Agent42 timestamped replay",
                "Agent43 G6/P6 replay gate",
                "Agent45 field replay evidence chain",
                "Agent52 multi-facility replay promotion gate with Agent51 catalyst proxy holdout",
                "Agent46 soft-sensor field holdout gate",
                "human review before any release-gate calibration writeback",
            ],
        }

    def _acceptance_matrix(self) -> list[dict[str, Any]]:
        import_readiness = self._readiness_block(self.field_replay_import_metrics)
        timestamp_readiness = self._readiness_block(self.timestamped_replay_metrics)
        replay_gate_readiness = self._readiness_block(self.field_replay_gate_metrics)
        evidence_readiness = self._readiness_block(self.field_replay_evidence_chain_metrics)
        control_readiness = self._readiness_block(self.multi_facility_replay_evaluation_metrics)
        control_metrics = self.multi_facility_replay_evaluation_metrics.get("offline_evaluation_metrics", {})
        control_metrics = control_metrics if isinstance(control_metrics, dict) else {}
        soft_gate_readiness = self._readiness_block(self.soft_sensor_field_holdout_gate_metrics)
        claim_readiness = self._readiness_block(self.claim_specific_package_metrics)
        unified_readiness = self._readiness_block(self.unified_field_evidence_gate_metrics)

        return [
            self._stage(
                stage_id="R7S1_field_package_import",
                title="真实 field package 导入与 provenance",
                status=str(import_readiness.get("field_replay_import_status", "not_available")),
                passed=bool(import_readiness.get("can_pass_to_timestamped_replay", False)),
                gate_metric="can_pass_to_timestamped_replay",
                blocker_when_failed="field_package_not_imported_or_data_origin_not_field",
                evidence={
                    "accepted_data_origin": import_readiness.get("accepted_data_origin", "unknown"),
                    "accepted_table_count": import_readiness.get("accepted_table_count", 0),
                    "total_table_count": import_readiness.get("total_table_count", 0),
                },
            ),
            self._stage(
                stage_id="R7S2_timestamped_replay",
                title="sensor/lab/operation/proxy 同轴 replay",
                status=str(timestamp_readiness.get("timestamped_replay_status", "not_available")),
                passed=(
                    str(timestamp_readiness.get("timestamped_replay_status", "")).startswith("field_")
                    and bool(timestamp_readiness.get("can_calibrate_fast_proxy", False))
                )
                or bool(evidence_readiness.get("timestamped_replay_ready", False)),
                gate_metric="timestamped_replay_ready",
                blocker_when_failed="timestamped_replay_not_field_ready",
                evidence={
                    "timestamp_coverage": timestamp_readiness.get("timestamp_coverage"),
                    "proxy_precision": self._metric(self.timestamped_replay_metrics, "replay_metrics", "proxy_precision"),
                    "proxy_recall": self._metric(self.timestamped_replay_metrics, "replay_metrics", "proxy_recall"),
                },
            ),
            self._stage(
                stage_id="R7S3_g6_p6_replay_gate",
                title="G6/P6 replay gate 与保护性控制候选",
                status=str(replay_gate_readiness.get("field_replay_gate_status", "not_available")),
                passed=bool(replay_gate_readiness.get("can_write_to_protective_control", False))
                or bool(evidence_readiness.get("g6_ready", False)),
                gate_metric="can_write_to_protective_control",
                blocker_when_failed="g6_p6_replay_gate_not_passed",
                evidence={
                    "accepted_gate_count": replay_gate_readiness.get("accepted_gate_count"),
                    "total_gate_count": replay_gate_readiness.get("total_gate_count"),
                    "failed_gate_ids": replay_gate_readiness.get("failed_gate_ids", []),
                },
            ),
            self._stage(
                stage_id="R7S4_field_replay_evidence_chain",
                title="Agent44 -> Agent42 -> Agent43 -> Agent45 证据链",
                status=str(evidence_readiness.get("field_replay_evidence_chain_status", "not_available")),
                passed=bool(evidence_readiness.get("can_emit_protective_writeback_candidate", False)),
                gate_metric="can_emit_protective_writeback_candidate",
                blocker_when_failed="field_replay_evidence_chain_not_passed",
                evidence={
                    "import_ready": evidence_readiness.get("import_ready", False),
                    "timestamped_replay_ready": evidence_readiness.get("timestamped_replay_ready", False),
                    "g6_ready": evidence_readiness.get("g6_ready", False),
                },
            ),
            self._stage(
                stage_id="R7S4b_multi_facility_control_promotion",
                title="Agent49/52 多设施控制晋级与催化剂代理验证门",
                status=str(control_readiness.get("replay_evaluation_status", "not_available")),
                passed=bool(control_readiness.get("field_ready", False))
                and bool(control_readiness.get("catalyst_proxy_field_validation_pass", False)),
                gate_metric="field_ready_and_catalyst_proxy_field_validation_pass",
                blocker_when_failed="multi_facility_control_or_catalyst_proxy_holdout_not_passed",
                evidence={
                    "field_ready": control_readiness.get("field_ready", False),
                    "can_write_to_actuator_candidate": control_readiness.get("can_write_to_actuator", False),
                    "field_replay_coverage": control_metrics.get("field_replay_coverage"),
                    "joint_action_accuracy": control_metrics.get("joint_action_accuracy"),
                    "mean_reward_regret": control_metrics.get("mean_reward_regret"),
                    "catalyst_proxy_summary_status": control_metrics.get("catalyst_proxy_summary_status"),
                    "catalyst_proxy_scoreable_batch_count": control_metrics.get(
                        "catalyst_proxy_scoreable_batch_count"
                    ),
                    "catalyst_proxy_field_validation_pass": control_readiness.get(
                        "catalyst_proxy_field_validation_pass",
                        control_metrics.get("catalyst_proxy_field_validation_pass", False),
                    ),
                    "catalyst_guardrail_mode": control_readiness.get(
                        "catalyst_guardrail_mode",
                        control_metrics.get("catalyst_guardrail_mode"),
                    ),
                },
            ),
            self._stage(
                stage_id="R7S5_soft_sensor_field_holdout",
                title="软传感 field holdout release calibration gate",
                status=str(soft_gate_readiness.get("soft_sensor_field_holdout_gate_status", "not_available")),
                passed=bool(soft_gate_readiness.get("can_write_to_release_gate", False)),
                gate_metric="can_write_to_release_gate",
                blocker_when_failed="soft_sensor_field_holdout_gate_not_passed",
                evidence={
                    "passed_check_count": soft_gate_readiness.get("passed_check_count"),
                    "total_check_count": soft_gate_readiness.get("total_check_count"),
                    "failed_check_ids": soft_gate_readiness.get("failed_check_ids", []),
                },
            ),
            self._stage(
                stage_id="R7S6_claim_specific_field_package",
                title="claim-specific 字段、source_basis 与真实 field rows",
                status=str(claim_readiness.get("claim_specific_package_status", "not_available")),
                passed=(
                    float(claim_readiness.get("source_basis_completion_rate", 0.0)) >= 0.95
                    and float(claim_readiness.get("minimal_field_package_schema_pass_rate", 0.0)) >= 0.95
                    and float(claim_readiness.get("minimal_field_package_field_pass_rate", 0.0)) >= 0.95
                ),
                gate_metric="minimal_field_package_field_pass_rate",
                blocker_when_failed="claim_specific_real_field_rows_not_passed",
                evidence={
                    "source_basis_completion_rate": claim_readiness.get("source_basis_completion_rate", 0.0),
                    "minimal_field_package_schema_pass_rate": claim_readiness.get(
                        "minimal_field_package_schema_pass_rate", 0.0
                    ),
                    "minimal_field_package_field_pass_rate": claim_readiness.get(
                        "minimal_field_package_field_pass_rate", 0.0
                    ),
                },
            ),
            self._stage(
                stage_id="R7S7_unified_field_evidence_gate",
                title="统一 evidence gate 的 field-supported 升级判断",
                status=str(unified_readiness.get("unified_field_evidence_gate_status", "not_available")),
                passed=bool(unified_readiness.get("can_emit_field_claim_upgrade", False)),
                gate_metric="can_emit_field_claim_upgrade",
                blocker_when_failed="unified_field_evidence_gate_not_passed",
                evidence={
                    "field_import_pass": unified_readiness.get("field_import_pass", False),
                    "field_replay_evidence_chain_pass": unified_readiness.get(
                        "field_replay_evidence_chain_pass", False
                    ),
                    "soft_sensor_field_holdout_gate_pass": unified_readiness.get(
                        "soft_sensor_field_holdout_gate_pass", False
                    ),
                    "field_supported_edge_ratio": unified_readiness.get("field_supported_edge_ratio", 0.0),
                },
            ),
        ]

    @staticmethod
    def _stage(
        *,
        stage_id: str,
        title: str,
        status: str,
        passed: bool,
        gate_metric: str,
        blocker_when_failed: str,
        evidence: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "stage_id": stage_id,
            "title": title,
            "status": status,
            "passed": passed,
            "gate_metric": gate_metric,
            "blocker": "" if passed else blocker_when_failed,
            "evidence": evidence,
        }

    def _readiness(self, matrix: list[dict[str, Any]]) -> dict[str, Any]:
        passed_count = sum(1 for stage in matrix if stage["passed"])
        blockers = [stage["blocker"] for stage in matrix if stage["blocker"]]
        pass_by_id = {stage["stage_id"]: bool(stage["passed"]) for stage in matrix}
        if not pass_by_id["R7S1_field_package_import"]:
            status = "real_field_package_acceptance_blocked_at_import"
            next_action = "R7a_import_real_field_package_with_metadata_and_csv"
        elif not pass_by_id["R7S4_field_replay_evidence_chain"]:
            status = "real_field_package_acceptance_blocked_at_replay_chain"
            next_action = "R7b_run_timestamped_replay_g6_and_evidence_chain"
        elif not pass_by_id["R7S4b_multi_facility_control_promotion"]:
            status = "real_field_package_acceptance_blocked_at_multi_facility_control_gate"
            next_action = "R7c_validate_agent49_52_control_replay_and_agent51_catalyst_holdout"
        elif not pass_by_id["R7S5_soft_sensor_field_holdout"]:
            status = "real_field_package_acceptance_blocked_at_soft_sensor_holdout"
            next_action = "R7d_collect_soft_sensor_field_holdout_labels"
        elif not pass_by_id["R7S6_claim_specific_field_package"]:
            status = "real_field_package_acceptance_blocked_at_claim_field_rows"
            next_action = "R7e_link_claim_specific_field_rows"
        elif not pass_by_id["R7S7_unified_field_evidence_gate"]:
            status = "real_field_package_acceptance_blocked_at_unified_evidence_gate"
            next_action = "R7f_refresh_unified_evidence_gate"
        else:
            status = "real_field_package_acceptance_ready_for_human_review"
            next_action = "R7g_human_review_before_field_supported_upgrade"
        score = round(
            0.20 * float(pass_by_id["R7S1_field_package_import"])
            + 0.10 * float(pass_by_id["R7S2_timestamped_replay"])
            + 0.10 * float(pass_by_id["R7S3_g6_p6_replay_gate"])
            + 0.14 * float(pass_by_id["R7S4_field_replay_evidence_chain"])
            + 0.14 * float(pass_by_id["R7S4b_multi_facility_control_promotion"])
            + 0.14 * float(pass_by_id["R7S5_soft_sensor_field_holdout"])
            + 0.10 * float(pass_by_id["R7S6_claim_specific_field_package"])
            + 0.08 * float(pass_by_id["R7S7_unified_field_evidence_gate"]),
            3,
        )
        return {
            "real_field_package_acceptance_status": status,
            "real_field_package_acceptance_score": score,
            "passed_stage_count": passed_count,
            "total_stage_count": len(matrix),
            "failed_stage_ids": [stage["stage_id"] for stage in matrix if not stage["passed"]],
            "blocking_reasons": blockers,
            "field_package_import_pass": pass_by_id["R7S1_field_package_import"],
            "timestamped_replay_pass": pass_by_id["R7S2_timestamped_replay"],
            "field_replay_evidence_chain_pass": pass_by_id["R7S4_field_replay_evidence_chain"],
            "multi_facility_control_promotion_pass": pass_by_id["R7S4b_multi_facility_control_promotion"],
            "catalyst_proxy_field_validation_pass": bool(
                self._readiness_block(self.multi_facility_replay_evaluation_metrics).get(
                    "catalyst_proxy_field_validation_pass",
                    False,
                )
            ),
            "soft_sensor_field_holdout_gate_pass": pass_by_id["R7S5_soft_sensor_field_holdout"],
            "claim_specific_field_package_pass": pass_by_id["R7S6_claim_specific_field_package"],
            "unified_field_evidence_gate_pass": pass_by_id["R7S7_unified_field_evidence_gate"],
            "can_emit_protective_control_candidate": pass_by_id["R7S4_field_replay_evidence_chain"]
            and pass_by_id["R7S4b_multi_facility_control_promotion"],
            "can_emit_release_gate_calibration_candidate": pass_by_id["R7S5_soft_sensor_field_holdout"],
            "can_emit_field_supported_claim_candidate": all(pass_by_id.values()),
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "next_recommended_core_action": next_action,
        }

    @staticmethod
    def _writeback_policy(readiness: dict[str, Any]) -> dict[str, Any]:
        allowed = ["R7_acceptance_status_for_governance", "field_package_blocker_table"]
        if readiness["can_emit_protective_control_candidate"]:
            allowed.append("human_reviewed_protective_control_candidate")
        if readiness["can_emit_release_gate_calibration_candidate"]:
            allowed.append("human_reviewed_soft_sensor_release_calibration_candidate")
        return {
            "allowed_writeback": allowed,
            "blocked_writeback": [
                "actuator_policy",
                "automatic_release_gate_policy",
                "field_control_effectiveness_claim_without_human_review",
                "synthetic_template_as_field_evidence",
            ],
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "policy_effect": "R7 can route real-field acceptance evidence to human review; it cannot auto-authorize control or discharge.",
        }

    @staticmethod
    def _next_refactor_action(readiness: dict[str, Any]) -> dict[str, Any]:
        action_id = str(readiness["next_recommended_core_action"])
        title_by_action = {
            "R7a_import_real_field_package_with_metadata_and_csv": "导入 data_origin=field 的真实 metadata 与 CSV 包",
            "R7b_run_timestamped_replay_g6_and_evidence_chain": "重跑 timestamped replay、G6/P6 和证据链",
            "R7c_validate_agent49_52_control_replay_and_agent51_catalyst_holdout": (
                "验证 Agent49/52 多设施控制 replay，并通过 Agent51 催化剂代理 field holdout"
            ),
            "R7d_collect_soft_sensor_field_holdout_labels": "采集并导入软传感 field holdout 标签",
            "R7e_link_claim_specific_field_rows": "把真实 field rows 绑定到 claim-specific package",
            "R7f_refresh_unified_evidence_gate": "刷新统一 evidence gate 的 field-supported 判断",
            "R7g_human_review_before_field_supported_upgrade": "人工复核后再考虑 field-supported 升级",
        }
        return {
            "action_id": action_id,
            "title": title_by_action.get(action_id, "继续 R7 真实现场验收"),
            "reason": "; ".join(readiness["blocking_reasons"]) or "所有 R7 自动门已通过，仍需人工复核。",
            "must_not_do": "不能把 synthetic/sample 包当成真实现场 replay；不能绕过人工复核写执行器或 release gate。",
        }

    @staticmethod
    def _readiness_block(metrics: dict[str, Any]) -> dict[str, Any]:
        readiness = metrics.get("readiness", {})
        return readiness if isinstance(readiness, dict) else {}

    @staticmethod
    def _metric(metrics: dict[str, Any], block: str, key: str) -> Any:
        value = metrics.get(block, {})
        if isinstance(value, dict):
            return value.get(key)
        return None
