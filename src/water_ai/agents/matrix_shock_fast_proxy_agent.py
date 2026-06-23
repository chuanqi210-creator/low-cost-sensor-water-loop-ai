from __future__ import annotations

from collections.abc import Sequence
from statistics import median

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class MatrixShockFastProxyAgent(BaseAgent):
    """Use low-cost fast proxies to trigger protective control before slow lab evidence returns."""

    name = "matrix_shock_fast_proxy_agent"

    def __init__(
        self,
        *,
        latency_metrics: dict[str, object] | None = None,
        conformal_readiness: dict[str, object] | None = None,
        evidence_stage: str = "synthetic_replay",
        field_proxy_validation: dict[str, object] | None = None,
    ) -> None:
        self.latency_metrics = latency_metrics or {}
        self.conformal_readiness = conformal_readiness or {}
        self.evidence_stage = evidence_stage
        self.field_proxy_validation = field_proxy_validation or {}

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        if not readings:
            return AgentReport(
                agent_name=self.name,
                confidence=0.0,
                summary="基质冲击快代理：无传感输入，不能触发保护性控制。",
                issues=[
                    QualityIssue(
                        sensor="matrix_shock_fast_proxy",
                        issue_type="empty_sensor_stream",
                        severity=Severity.CRITICAL,
                        message="缺少低成本传感时间序列，无法计算 EC/浊度/UV254/pH/ORP 快代理。",
                    )
                ],
                recommendations=["暂停自动控制，先补齐低成本传感时间序列。"],
                metrics={},
            )

        proxy = self._proxy_features(readings)
        original_latency = self._matrix_latency_record()
        mitigation = self._mitigation_budget(proxy, original_latency)
        control_adaptation = self._control_adaptation(proxy, mitigation)
        readiness = self._readiness(proxy, mitigation)
        issues = self._issues(proxy, mitigation, readiness)
        recommendations = self._recommendations(proxy, mitigation, readiness)
        summary = (
            f"基质冲击快代理：{readiness['fast_proxy_status']}；"
            f"proxy_score {proxy['proxy_score']:.3f}，"
            f"保护动作余量 {mitigation['protective_action_margin_min']:.1f} min。"
        )
        confidence = round(
            min(0.9, max(0.2, 0.40 + 0.34 * readiness["fast_proxy_readiness_score"] - 0.035 * len(issues))),
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
                "proxy": proxy,
                "original_latency": original_latency,
                "mitigation_budget": mitigation,
                "control_adaptation": control_adaptation,
                "readiness": readiness,
                "evidence_stage": self.evidence_stage,
                "field_proxy_validation": self.field_proxy_validation,
                "conformal_readiness": self.conformal_readiness,
            },
        )

    def _proxy_features(self, readings: Sequence[SensorReading]) -> dict[str, object]:
        ordered = sorted(readings, key=lambda item: item.timestamp_min)
        early = ordered[: max(3, min(8, len(ordered)))]
        late = ordered[-max(3, min(8, len(ordered))) :]
        full = list(ordered)

        early_ec = self._median_sensor(early, "EC_uScm")
        late_ec = self._median_sensor(late, "EC_uScm")
        early_turbidity = self._median_sensor(early, "turbidity_NTU")
        late_turbidity = self._median_sensor(late, "turbidity_NTU")
        late_uv = self._median_sensor(late, "UV254_abs")
        late_orp = self._median_sensor(late, "ORP_mV")
        late_ph = self._median_sensor(late, "pH")

        ec_level = self._clip((late_ec - 1500.0) / 2200.0)
        ec_surge = self._clip((late_ec - early_ec) / 900.0)
        turbidity_level = self._clip((late_turbidity - 18.0) / 30.0)
        turbidity_surge = self._clip((late_turbidity - early_turbidity) / 18.0)
        uv_load = self._clip((late_uv - 0.45) / 0.60)
        ph_shift = self._clip(abs(late_ph - 7.2) / 2.0)
        orp_suppression = self._clip((430.0 - late_orp) / 280.0)
        low_cost_signal_count = sum(
            1
            for sensor in ("EC_uScm", "turbidity_NTU", "UV254_abs", "pH", "ORP_mV")
            if any(self._sensor_value(reading, sensor) is not None for reading in full)
        )
        specificity_guard = self._clip(
            0.42 * ec_level
            + 0.30 * turbidity_level
            + 0.18 * uv_load
            + 0.10 * ph_shift
            - 0.18 * max(0.0, orp_suppression - max(ec_level, turbidity_level))
        )
        proxy_score = self._clip(
            0.34 * ec_level
            + 0.12 * ec_surge
            + 0.28 * turbidity_level
            + 0.08 * turbidity_surge
            + 0.18 * uv_load
            + 0.06 * ph_shift
            + 0.04 * orp_suppression
        )
        protective_triggered = proxy_score >= 0.52 and specificity_guard >= 0.46 and low_cost_signal_count >= 4
        release_block = proxy_score >= 0.42 or specificity_guard >= 0.45
        return {
            "proxy_score": round(proxy_score, 3),
            "specificity_guard_score": round(specificity_guard, 3),
            "protective_triggered": protective_triggered,
            "release_block_recommended": release_block,
            "low_cost_signal_count": low_cost_signal_count,
            "feature_scores": {
                "ec_level": round(ec_level, 3),
                "ec_surge": round(ec_surge, 3),
                "turbidity_level": round(turbidity_level, 3),
                "turbidity_surge": round(turbidity_surge, 3),
                "uv254_load": round(uv_load, 3),
                "ph_shift": round(ph_shift, 3),
                "orp_suppression": round(orp_suppression, 3),
            },
            "raw_medians": {
                "early_EC_uScm": round(early_ec, 3),
                "late_EC_uScm": round(late_ec, 3),
                "early_turbidity_NTU": round(early_turbidity, 3),
                "late_turbidity_NTU": round(late_turbidity, 3),
                "late_UV254_abs": round(late_uv, 4),
                "late_ORP_mV": round(late_orp, 3),
                "late_pH": round(late_ph, 3),
            },
        }

    def _matrix_latency_record(self) -> dict[str, object]:
        records = self.latency_metrics.get("latency_budget", [])
        if isinstance(records, list):
            for record in records:
                if isinstance(record, dict) and record.get("scenario") == "matrix_shock":
                    return record
        return {
            "scenario": "matrix_shock",
            "action_deadline_min": 85.0,
            "release_evidence_latency_min": 115.0,
            "loop_time_credit_min": 84.0,
            "evidence_margin_min": -31.0,
            "action_latency_margin_min": 47.0,
            "failure_boundary": "synthetic replay 中的闭环稳定不等于现场低频采样和慢检测条件下可执行。",
        }

    def _mitigation_budget(self, proxy: dict[str, object], original_latency: dict[str, object]) -> dict[str, object]:
        protective_triggered = bool(proxy["protective_triggered"])
        proxy_observation_latency = 3.0 + 6.0 + 1.0
        operator_or_interlock_delay = 3.0 if protective_triggered else 10.0
        actuator_delay = 5.0
        mixing_delay = 8.0
        protective_action_latency = proxy_observation_latency + operator_or_interlock_delay + actuator_delay + mixing_delay
        action_deadline = self._number(original_latency, "action_deadline_min", 85.0)
        protective_margin = action_deadline - protective_action_latency
        original_evidence_margin = self._number(original_latency, "evidence_margin_min", -31.0)
        recommended_hold_extension = 0.0
        if original_evidence_margin < 0:
            recommended_hold_extension = min(60.0, 15.0 * int((-original_evidence_margin + 14.999) // 15.0))
        projected_evidence_margin = original_evidence_margin + recommended_hold_extension
        latency_failure_resolved_for_control = protective_triggered and protective_margin >= 20.0
        release_still_waits_for_slow_evidence = True
        return {
            "proxy_observation_latency_min": round(proxy_observation_latency, 3),
            "operator_or_interlock_delay_min": round(operator_or_interlock_delay, 3),
            "actuator_delay_min": actuator_delay,
            "mixing_delay_min": mixing_delay,
            "protective_action_latency_min": round(protective_action_latency, 3),
            "protective_action_margin_min": round(protective_margin, 3),
            "original_evidence_margin_min": round(original_evidence_margin, 3),
            "recommended_hold_extension_min": round(recommended_hold_extension, 3),
            "projected_evidence_margin_after_extension_min": round(projected_evidence_margin, 3),
            "latency_failure_resolved_for_control": latency_failure_resolved_for_control,
            "release_still_waits_for_slow_evidence": release_still_waits_for_slow_evidence,
            "unsafe_release_prevented": bool(proxy["release_block_recommended"]),
        }

    def _control_adaptation(self, proxy: dict[str, object], mitigation: dict[str, object]) -> dict[str, object]:
        recommended_hold_min = 45.0 + float(mitigation["recommended_hold_extension_min"])
        return {
            "action_id": "switch_or_pretreat",
            "protective_mode": bool(proxy["protective_triggered"]),
            "score_boost": round(0.24 * float(proxy["proxy_score"]), 3),
            "automatic_release_allowed": False,
            "release_policy": "block_release_until_lab_and_field_conformal_calibration",
            "recommended_hold_min": round(recommended_hold_min, 3),
            "validation_targets": [
                "salinity_or_EC_reference",
                "turbidity_reference",
                "UV254_reference",
                "COD_or_TOC",
                "target_pollutant_or_proxy",
            ],
            "latency_basis": {
                "protective_action_margin_min": mitigation["protective_action_margin_min"],
                "original_evidence_margin_min": mitigation["original_evidence_margin_min"],
                "projected_evidence_margin_after_extension_min": mitigation["projected_evidence_margin_after_extension_min"],
            },
        }

    def _readiness(self, proxy: dict[str, object], mitigation: dict[str, object]) -> dict[str, object]:
        field_precision = self._number(self.field_proxy_validation, "precision", 0.0)
        field_recall = self._number(self.field_proxy_validation, "recall", 0.0)
        timestamp_coverage = self._number(self.field_proxy_validation, "timestamp_coverage", 0.0)
        field_validated = (
            self.evidence_stage == "field_timestamped"
            and field_precision >= 0.82
            and field_recall >= 0.78
            and timestamp_coverage >= 0.85
        )
        score = round(
            0.30 * float(proxy["proxy_score"])
            + 0.18 * float(proxy["specificity_guard_score"])
            + 0.16 * float(mitigation["latency_failure_resolved_for_control"])
            + 0.12 * max(0.0, min(1.0, float(mitigation["protective_action_margin_min"]) / 60.0))
            + 0.12 * timestamp_coverage
            + 0.12 * float(field_validated),
            3,
        )
        if not proxy["protective_triggered"]:
            status = "fast_proxy_not_triggered_keep_standard_matrix_workup"
        elif not field_validated:
            status = "synthetic_fast_proxy_ready_needs_field_timestamp_validation"
        else:
            status = "field_fast_proxy_protective_control_ready"
        return {
            "fast_proxy_status": status,
            "fast_proxy_readiness_score": score,
            "field_proxy_validation_required": not field_validated,
            "can_write_to_protective_control": field_validated and bool(mitigation["latency_failure_resolved_for_control"]),
            "can_write_to_release_gate": False,
            "release_gate_block_reason": "fast proxy can trigger protection, but release still requires lab evidence and field conformal calibration",
        }

    def _issues(
        self,
        proxy: dict[str, object],
        mitigation: dict[str, object],
        readiness: dict[str, object],
    ) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        if readiness["field_proxy_validation_required"] and proxy["protective_triggered"]:
            issues.append(
                QualityIssue(
                    sensor="matrix_shock_fast_proxy",
                    issue_type="field_timestamp_validation_required",
                    severity=Severity.WARNING,
                    message="快代理目前只在 synthetic replay 中验证，必须用现场时间戳和离线标签验证 precision/recall。",
                    evidence=readiness,
                )
            )
        if proxy["release_block_recommended"]:
            issues.append(
                QualityIssue(
                    sensor="matrix_shock_fast_proxy",
                    issue_type="release_blocked_by_matrix_fast_proxy",
                    severity=Severity.WARNING,
                    message="低成本快代理提示基质冲击风险，允许保护性动作，但禁止自动放行。",
                    evidence=proxy,
                )
            )
        if proxy["protective_triggered"] and not mitigation["latency_failure_resolved_for_control"]:
            issues.append(
                QualityIssue(
                    sensor="matrix_shock_fast_proxy",
                    issue_type="protective_action_latency_not_resolved",
                    severity=Severity.CRITICAL,
                    message="快代理没有给保护性动作留下足够时间，需要自动联锁或更短采样/质控窗口。",
                    evidence=mitigation,
                )
            )
        return issues

    @staticmethod
    def _recommendations(
        proxy: dict[str, object],
        mitigation: dict[str, object],
        readiness: dict[str, object],
    ) -> list[str]:
        if not proxy["protective_triggered"]:
            return [
                "当前低成本信号不足以触发 matrix_shock 快代理，保持标准旁路验证和人工复核。",
                "不要为了追求快响应降低 specificity guard；假阳性会带来不必要预处理和停留时间成本。",
            ]
        recommendations = [
            "用 EC、浊度、UV254、pH 和 ORP 组成 matrix_shock 快代理，先触发保护性预处理/切换，不等待慢实验结果才动作。",
            "快代理只允许触发 protective control；放行仍必须等待离线证据、field holdout 保形校准和 release gate。",
            f"把 matrix_shock 暂存窗口至少增加 {mitigation['recommended_hold_extension_min']} min，或用等价快检/预处理降低慢证据压力。",
        ]
        if readiness["field_proxy_validation_required"]:
            recommendations.append("下一步用 timestamped campaign replay 评估快代理 precision、recall、提前量和误触发成本。")
        return recommendations

    @staticmethod
    def _method_contract() -> dict[str, object]:
        return {
            "upgrade_id": "matrix_shock_fast_proxy_latency_aware_control",
            "borrowed_from": [
                "parsa_2024_dynamic_control_review",
                "water_2021_textile_dye_aop_review",
                "nsr_2026_scientific_kg_survey",
            ],
            "reality_mapping": "用低成本原始信号先触发保护性控制，把慢离线证据从动作触发条件改为放行/校准条件。",
            "data_needs": [
                "EC_uScm_timeseries",
                "turbidity_NTU_timeseries",
                "UV254_abs_timeseries",
                "pH_timeseries",
                "ORP_mV_timeseries",
                "offline_COD_TOC_or_target_label",
                "actuator_command_timestamp",
                "pretreatment_effect_timestamp",
                "false_positive_cost",
            ],
            "implementation_path": [
                "src/water_ai/agents/matrix_shock_fast_proxy_agent.py",
                "src/water_ai/agents/control_strategy_agent.py",
                "experiments/run_agent41_matrix_shock_fast_proxy.py",
            ],
            "evaluation_metrics": [
                "field_proxy_precision",
                "field_proxy_recall",
                "protective_action_lead_time_min",
                "matrix_shock_latency_violation_rate",
                "false_positive_cost_index",
            ],
            "failure_boundary": "快代理能支持提前保护，不能证明污染物已经达标；field validation 前不得写入自动放行门。",
        }

    @staticmethod
    def _median_sensor(readings: Sequence[SensorReading], sensor: str) -> float:
        values = [
            float(value)
            for reading in readings
            for value in [MatrixShockFastProxyAgent._sensor_value(reading, sensor)]
            if value is not None
        ]
        if not values:
            return 0.0
        return float(median(values))

    @staticmethod
    def _sensor_value(reading: SensorReading, sensor: str) -> float | None:
        value = reading.values.get(sensor)
        if isinstance(value, int | float):
            return float(value)
        return None

    @staticmethod
    def _number(mapping: dict[str, object], key: str, default: float) -> float:
        value = mapping.get(key, default)
        if isinstance(value, int | float):
            return float(value)
        return default

    @staticmethod
    def _clip(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
        return max(lo, min(hi, value))
