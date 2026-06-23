from __future__ import annotations

from collections.abc import Sequence
from math import log

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class CatalystActivityProxyAgent(BaseAgent):
    """Design low-cost proxy observations for catalyst activity."""

    name = "catalyst_activity_proxy_agent"

    def __init__(
        self,
        *,
        sparse_placement_metrics: dict[str, object] | None = None,
        proxy_cases: list[dict[str, float | str]] | None = None,
        data_origin: str = "synthetic_proxy_design",
        field_validation: dict[str, float] | None = None,
        field_proxy_holdout_summary: dict[str, object] | None = None,
        min_proxy_observability: float = 0.58,
        min_field_correlation: float = 0.68,
        max_field_mae: float = 0.16,
    ) -> None:
        self.sparse_placement_metrics = sparse_placement_metrics or {}
        self.proxy_cases = proxy_cases or self._default_proxy_cases()
        self.data_origin = data_origin
        self.field_proxy_holdout_summary = field_proxy_holdout_summary or {}
        summary_validation = self._field_validation_from_holdout_summary(self.field_proxy_holdout_summary)
        self.field_validation = {**summary_validation, **(field_validation or {})}
        if (
            self.data_origin == "synthetic_proxy_design"
            and self.field_proxy_holdout_summary.get("ready_for_agent51_validation") is True
        ):
            self.data_origin = "field_proxy_holdout"
        self.min_proxy_observability = min_proxy_observability
        self.min_field_correlation = min_field_correlation
        self.max_field_mae = max_field_mae

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        sparse_context = self._sparse_context()
        proxy_catalog = self._proxy_catalog(sparse_context)
        proxy_feature_table = self._proxy_feature_table()
        proxy_metrics = self._proxy_metrics(proxy_feature_table, proxy_catalog, sparse_context)
        weak_axis_repair_plan = self._weak_axis_repair_plan(proxy_catalog, proxy_metrics, sparse_context)
        readiness = self._readiness(proxy_metrics)
        agent49_interface = self._agent49_interface(readiness, proxy_metrics, weak_axis_repair_plan)
        issues = self._issues(proxy_catalog, readiness, proxy_metrics, weak_axis_repair_plan)
        recommendations = self._recommendations(proxy_catalog, readiness, weak_axis_repair_plan)
        summary = (
            f"催化剂活性代理观测：{readiness['catalyst_proxy_status']}；"
            f"当前代理观测 {proxy_metrics['current_proxy_observability']:.3f}，"
            f"补点后 {proxy_metrics['proxy_observability_after_recommended_patch']:.3f}。"
        )
        confidence = round(
            min(0.90, max(0.20, 0.34 + 0.42 * readiness["catalyst_proxy_score"] - 0.035 * len(issues))),
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
                "sparse_context": sparse_context,
                "proxy_catalog": proxy_catalog,
                "proxy_feature_table": proxy_feature_table,
                "proxy_metrics": proxy_metrics,
                "field_proxy_holdout_summary": self.field_proxy_holdout_summary,
                "weak_axis_repair_plan": weak_axis_repair_plan,
                "readiness": readiness,
                "agent49_interface": agent49_interface,
            },
        )

    def _sparse_context(self) -> dict[str, object]:
        selected = self.sparse_placement_metrics.get("selected_sensor_plan", [])
        coverage = self.sparse_placement_metrics.get("coverage", {})
        readiness = self.sparse_placement_metrics.get("readiness", {})
        placement_diagnostics = self.sparse_placement_metrics.get("placement_diagnostics", {})
        if not isinstance(selected, list):
            selected = []
        if not isinstance(coverage, dict):
            coverage = {}
        if not isinstance(readiness, dict):
            readiness = {}
        if not isinstance(placement_diagnostics, dict):
            placement_diagnostics = {}
        weak_axis_gaps = placement_diagnostics.get("weak_axis_gaps", [])
        weak_axis_gaps = weak_axis_gaps if isinstance(weak_axis_gaps, list) else []
        catalyst_axis_gap = next(
            (
                dict(gap)
                for gap in weak_axis_gaps
                if isinstance(gap, dict) and str(gap.get("axis")) == "catalyst_activity_observability"
            ),
            {},
        )
        available_pairs = sorted(
            {
                f"{item.get('node_id')}:{item.get('modality')}"
                for item in selected
                if isinstance(item, dict) and item.get("node_id") and item.get("modality")
            }
        )
        available_nodes = sorted(
            {str(item.get("node_id")) for item in selected if isinstance(item, dict) and item.get("node_id")}
        )
        available_modalities = sorted(
            {str(item.get("modality")) for item in selected if isinstance(item, dict) and item.get("modality")}
        )
        return {
            "available_node_modalities": available_pairs,
            "available_nodes": available_nodes,
            "available_modalities": available_modalities,
            "current_weak_state_coverage": float(coverage.get("weak_state_coverage", 0.0)),
            "current_catalyst_activity_observability": float(coverage.get("catalyst_activity_observability", 0.0)),
            "sparse_placement_status": readiness.get("sparse_placement_status", "unknown"),
            "selected_strategy_id": self._selected_strategy_id(),
            "placement_diagnostics": {
                "diagnostic_status": placement_diagnostics.get("diagnostic_status", "unknown"),
                "axis_span_rank_ratio": float(placement_diagnostics.get("axis_span_rank_ratio", 0.0) or 0.0),
                "condition_number_proxy": float(placement_diagnostics.get("condition_number_proxy", 0.0) or 0.0),
                "reconstruction_stability_score": float(
                    placement_diagnostics.get("reconstruction_stability_score", 0.0) or 0.0
                ),
                "weak_axis_gap_count": int(placement_diagnostics.get("weak_axis_gap_count", 0) or 0),
                "single_point_dependency_count": int(
                    placement_diagnostics.get("single_point_dependency_count", 0) or 0
                ),
            },
            "agent48_weak_axis_gaps": weak_axis_gaps,
            "agent48_catalyst_axis_gap": catalyst_axis_gap,
        }

    def _selected_strategy_id(self) -> str:
        selected_strategy = self.sparse_placement_metrics.get("selected_strategy", {})
        if isinstance(selected_strategy, dict):
            return str(selected_strategy.get("strategy_id", "unknown"))
        return "unknown"

    def _proxy_catalog(self, sparse_context: dict[str, object]) -> list[dict[str, object]]:
        available = set(sparse_context["available_node_modalities"])
        definitions = [
            {
                "proxy_id": "bed_uv254_removal_delta",
                "proxy_name": "催化剂床前后 UV254 去除率",
                "required_signals": ["N4_recirculation_loop:UV254_abs", "N3_catalyst_bed_outlet:UV254_abs"],
                "recommended_patch": ["N3_catalyst_bed_outlet:UV254_abs"],
                "weight": 0.30,
                "formula": "(UV254_in - UV254_out) / max(UV254_in, eps)",
                "reality_mapping": "用催化剂床前后芳香/共轭有机物吸收下降作为活性代理。",
            },
            {
                "proxy_id": "orp_decay_across_bed",
                "proxy_name": "催化剂床前后 ORP 衰减/利用",
                "required_signals": ["N2_reactor_mid:ORP_mV", "N3_catalyst_bed_outlet:ORP_mV"],
                "recommended_patch": ["N3_catalyst_bed_outlet:ORP_mV"],
                "weight": 0.18,
                "formula": "clip((ORP_in - ORP_out) / 180, 0, 1)",
                "reality_mapping": "用氧化还原电位变化辅助判断催化反应是否发生，而不是单看出口水质。",
            },
            {
                "proxy_id": "turbidity_pressure_fouling",
                "proxy_name": "浊度/压降污染堵塞代理",
                "required_signals": ["N3_catalyst_bed_outlet:turbidity_NTU", "N3_catalyst_bed:pressure_drop_kPa"],
                "recommended_patch": ["N3_catalyst_bed:pressure_drop_kPa"],
                "weight": 0.17,
                "formula": "0.55 * turbidity_delta_norm + 0.45 * pressure_drop_norm",
                "reality_mapping": "区分活性位失活与床层堵塞/污堵，避免把水力或悬浮物问题误判为催化剂本征失活。",
            },
            {
                "proxy_id": "regeneration_response_gain",
                "proxy_name": "再生前后响应增益",
                "required_signals": ["operation_log:regeneration_event", "pre_post_regeneration:uv254_or_rate_gain"],
                "recommended_patch": ["campaign_operation_log.regeneration_event", "pre_post_regeneration_lab_label"],
                "weight": 0.17,
                "formula": "post_regen_removal_or_rate - pre_regen_removal_or_rate",
                "reality_mapping": "如果再生后活性代理明显恢复，说明更像可逆污染；若不恢复，则提示寿命耗尽或不可逆失活。",
            },
            {
                "proxy_id": "residence_time_normalized_rate_residual",
                "proxy_name": "停留时间归一化反应速率残差",
                "required_signals": ["N4_recirculation_loop:UV254_abs", "N3_catalyst_bed_outlet:UV254_abs", "N1_equalization_tank:flow_Lmin", "N2_reactor_mid:ORP_mV"],
                "recommended_patch": ["N3_catalyst_bed_outlet:UV254_abs", "reactor_bed_volume_or_HRT"],
                "weight": 0.18,
                "formula": "-ln(UV254_out / UV254_in) / HRT compared with expected oxidant-adjusted rate",
                "reality_mapping": "把单次去除率转为受停留时间和氧化剂条件约束的灰箱残差。",
            },
        ]
        catalog: list[dict[str, object]] = []
        for item in definitions:
            required = list(item["required_signals"])
            present = [signal for signal in required if signal in available]
            support = round(len(present) / max(1, len(required)), 3)
            missing = [signal for signal in required if signal not in available]
            catalog.append(
                {
                    **item,
                    "currently_supported_signals": present,
                    "missing_signals": missing,
                    "current_support_score": support,
                    "support_after_recommended_patch": 1.0 if missing else support,
                    "evidence_stage": self.data_origin,
                    "failure_boundary": "proxy design only until field catalyst labels, pressure/drop data and regeneration events are observed",
                }
            )
        return catalog

    def _proxy_feature_table(self) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for case in self.proxy_cases:
            uv_in = float(case["uv254_in"])
            uv_out = float(case["uv254_out"])
            hrt = max(1.0, float(case["hrt_min"]))
            uv_removal = self._clip((uv_in - uv_out) / max(1e-6, uv_in))
            orp_decay = self._clip((float(case["orp_in_mV"]) - float(case["orp_out_mV"])) / 180.0)
            turbidity_delta_norm = self._clip((float(case["turbidity_out_NTU"]) - float(case["turbidity_in_NTU"])) / 18.0)
            pressure_drop_norm = self._clip(float(case["pressure_drop_kPa"]) / 0.42)
            fouling_load = self._clip(0.55 * turbidity_delta_norm + 0.45 * pressure_drop_norm)
            regen_gain = self._clip(float(case["post_regen_uv254_removal"]) - float(case["pre_regen_uv254_removal"]))
            observed_rate = -log(max(1e-6, uv_out / max(1e-6, uv_in))) / hrt
            expected_rate = max(1e-4, float(case["expected_rate_per_min"]))
            rate_residual_score = self._clip(observed_rate / expected_rate)
            activity_proxy = self._clip(
                0.36 * uv_removal
                + 0.16 * orp_decay
                + 0.20 * rate_residual_score
                + 0.14 * regen_gain
                + 0.14 * (1.0 - fouling_load)
            )
            label = float(case["catalyst_activity_label"])
            rows.append(
                {
                    "case_id": str(case["case_id"]),
                    "scenario": str(case["scenario"]),
                    "uv254_removal_ratio": round(uv_removal, 3),
                    "orp_decay_score": round(orp_decay, 3),
                    "fouling_load_score": round(fouling_load, 3),
                    "regeneration_response_gain": round(regen_gain, 3),
                    "residence_time_normalized_rate_score": round(rate_residual_score, 3),
                    "catalyst_activity_proxy_score": round(activity_proxy, 3),
                    "catalyst_activity_label": round(label, 3),
                    "absolute_proxy_error": round(abs(activity_proxy - label), 3),
                    "evidence_stage": self.data_origin,
                }
            )
        return rows

    def _proxy_metrics(
        self,
        proxy_feature_table: list[dict[str, object]],
        proxy_catalog: list[dict[str, object]],
        sparse_context: dict[str, object],
    ) -> dict[str, object]:
        weighted_support = sum(float(item["weight"]) * float(item["current_support_score"]) for item in proxy_catalog)
        weighted_patch_support = sum(float(item["weight"]) * float(item["support_after_recommended_patch"]) for item in proxy_catalog)
        current_proxy_observability = round(
            max(float(sparse_context["current_catalyst_activity_observability"]), 0.72 * weighted_support),
            3,
        )
        after_patch = round(
            max(current_proxy_observability, min(0.72, 0.72 * weighted_patch_support)),
            3,
        )
        errors = [float(row["absolute_proxy_error"]) for row in proxy_feature_table]
        proxy_scores = [float(row["catalyst_activity_proxy_score"]) for row in proxy_feature_table]
        labels = [float(row["catalyst_activity_label"]) for row in proxy_feature_table]
        correlation = self._correlation(proxy_scores, labels)
        mean_error = round(sum(errors) / max(1, len(errors)), 3)
        weak_after_patch = round(max(float(sparse_context["current_weak_state_coverage"]), after_patch), 3)
        return {
            "current_proxy_observability": current_proxy_observability,
            "proxy_observability_after_recommended_patch": after_patch,
            "weak_state_coverage_after_proxy_design": weak_after_patch,
            "weighted_current_proxy_support": round(weighted_support, 3),
            "weighted_patch_proxy_support": round(weighted_patch_support, 3),
            "synthetic_proxy_label_mae": mean_error,
            "synthetic_proxy_label_correlation": correlation,
            "field_validation": self.field_validation,
            "field_validation_source": self._field_validation_source(),
            "field_proxy_holdout_summary_status": self.field_proxy_holdout_summary.get(
                "field_proxy_holdout_summary_status",
                "not_supplied",
            ),
            "recommended_sensor_patches": self._recommended_sensor_patches(proxy_catalog),
            "proxy_case_count": len(proxy_feature_table),
        }

    def _weak_axis_repair_plan(
        self,
        proxy_catalog: list[dict[str, object]],
        proxy_metrics: dict[str, object],
        sparse_context: dict[str, object],
    ) -> dict[str, object]:
        catalyst_gap = sparse_context.get("agent48_catalyst_axis_gap", {})
        catalyst_gap = catalyst_gap if isinstance(catalyst_gap, dict) else {}
        diagnostics = sparse_context.get("placement_diagnostics", {})
        diagnostics = diagnostics if isinstance(diagnostics, dict) else {}
        gap_detected = bool(catalyst_gap)
        recoverable_by_candidate_pool = bool(catalyst_gap.get("recoverable_by_current_candidate_pool", True))
        current_coverage = float(catalyst_gap.get("current_coverage", sparse_context["current_catalyst_activity_observability"]))
        target = float(catalyst_gap.get("target", self.min_proxy_observability))
        projected = float(proxy_metrics["proxy_observability_after_recommended_patch"])
        prioritized_patches = self._prioritized_repair_patches(proxy_catalog)
        evidence_records = self._field_repair_evidence_requirements(prioritized_patches)
        repair_score = round(
            min(
                1.0,
                0.34 * min(1.0, projected / max(target, 1e-6))
                + 0.22 * float(bool(prioritized_patches))
                + 0.16 * min(1.0, float(proxy_metrics["synthetic_proxy_label_correlation"]))
                + 0.12 * min(1.0, 1.0 - float(proxy_metrics["synthetic_proxy_label_mae"]))
                + 0.10 * float(not recoverable_by_candidate_pool)
                + 0.06 * float(diagnostics.get("reconstruction_stability_score", 0.0) < 0.55),
            ),
            3,
        )
        status = "agent48_catalyst_axis_no_gap_detected"
        if gap_detected and not recoverable_by_candidate_pool:
            status = "agent48_catalyst_axis_requires_proxy_patch_and_field_label"
        elif gap_detected:
            status = "agent48_catalyst_axis_repairable_with_existing_candidate_pool"
        return {
            "repair_status": status,
            "target_axis": "catalyst_activity_observability",
            "agent48_gap_detected": gap_detected,
            "current_axis_coverage": round(current_coverage, 3),
            "target_axis_coverage": round(target, 3),
            "agent48_best_available_candidate": catalyst_gap.get("best_available_candidate", "unknown"),
            "agent48_best_available_value": round(float(catalyst_gap.get("best_available_value", 0.0) or 0.0), 3),
            "recoverable_by_current_candidate_pool": recoverable_by_candidate_pool,
            "proxy_projected_axis_coverage": round(projected, 3),
            "repair_score": repair_score,
            "prioritized_proxy_patches": prioritized_patches,
            "field_repair_evidence_requirements": evidence_records,
            "design_boundary": (
                "This repair plan can update Agent48/R2/Agent49 design priors, but cannot relax catalyst uncertainty "
                "or write actuator/release decisions until field_proxy_holdout passes."
            ),
        }

    @staticmethod
    def _prioritized_repair_patches(proxy_catalog: list[dict[str, object]]) -> list[dict[str, object]]:
        records: dict[str, dict[str, object]] = {}
        for item in proxy_catalog:
            proxy_id = str(item["proxy_id"])
            weight = float(item["weight"])
            for patch in item["recommended_patch"]:
                patch_id = str(patch)
                if patch_id in item["currently_supported_signals"]:
                    continue
                record = records.setdefault(
                    patch_id,
                    {
                        "patch_signal": patch_id,
                        "supports_proxy_ids": [],
                        "proxy_weight_sum": 0.0,
                        "patch_class": CatalystActivityProxyAgent._patch_class(patch_id),
                    },
                )
                if proxy_id not in record["supports_proxy_ids"]:
                    record["supports_proxy_ids"].append(proxy_id)
                record["proxy_weight_sum"] = round(float(record["proxy_weight_sum"]) + weight, 3)
        priority_bonus = {
            "low_cost_sensor": 0.18,
            "hydraulic_or_geometry_field": 0.10,
            "operation_log_field": 0.08,
            "offline_lab_label": 0.06,
        }
        prioritized: list[dict[str, object]] = []
        for record in records.values():
            score = round(
                min(1.0, float(record["proxy_weight_sum"]) + priority_bonus.get(str(record["patch_class"]), 0.0)),
                3,
            )
            prioritized.append(
                {
                    **record,
                    "supports_proxy_ids": sorted(str(proxy_id) for proxy_id in record["supports_proxy_ids"]),
                    "repair_priority_score": score,
                    "why_needed": CatalystActivityProxyAgent._patch_why_needed(str(record["patch_signal"])),
                }
            )
        prioritized.sort(
            key=lambda item: (-float(item["repair_priority_score"]), str(item["patch_class"]), str(item["patch_signal"]))
        )
        return prioritized

    @staticmethod
    def _patch_class(patch_signal: str) -> str:
        if ":" in patch_signal:
            return "low_cost_sensor"
        if "regeneration_event" in patch_signal:
            return "operation_log_field"
        if "lab_label" in patch_signal:
            return "offline_lab_label"
        if "HRT" in patch_signal or "bed_volume" in patch_signal:
            return "hydraulic_or_geometry_field"
        return "field_metadata"

    @staticmethod
    def _patch_why_needed(patch_signal: str) -> str:
        if patch_signal.endswith(":UV254_abs"):
            return "床出口 UV254 与回流/床入口 UV254 组成差分，支撑活性和停留时间归一化速率残差。"
        if patch_signal.endswith(":ORP_mV"):
            return "床出口 ORP 与反应核心 ORP 组成氧化剂利用/衰减代理。"
        if "pressure_drop" in patch_signal:
            return "压降用于区分催化剂活性衰减与床层堵塞/污堵。"
        if "regeneration_event" in patch_signal:
            return "再生事件用于判断活性下降是否可逆。"
        if "lab_label" in patch_signal:
            return "离线标签用于把 synthetic proxy 升级为 field_proxy_holdout。"
        if "HRT" in patch_signal or "bed_volume" in patch_signal:
            return "床体积或停留时间用于把去除率转化为灰箱速率残差。"
        return "用于补齐催化剂活性代理观测链。"

    @staticmethod
    def _field_repair_evidence_requirements(prioritized_patches: list[dict[str, object]]) -> list[dict[str, object]]:
        class_to_requirement = {
            "low_cost_sensor": {
                "required_table": "node_modality_sensor_timeseries",
                "required_fields": ["timestamp_min", "batch_id", "node_id", "modality", "value", "sensor_status"],
                "minimum_evidence": "same-batch inlet/outlet signal pairs with calibration status",
            },
            "operation_log_field": {
                "required_table": "campaign_operation_log",
                "required_fields": ["batch_id", "regeneration_event", "command_time_min", "effect_time_min"],
                "minimum_evidence": "time-aligned regeneration events before/after proxy response",
            },
            "offline_lab_label": {
                "required_table": "offline_lab_results",
                "required_fields": ["batch_id", "analyte", "value", "qa_flag", "lab_label_time_min"],
                "minimum_evidence": "QA-passed catalyst activity or regeneration response labels",
            },
            "hydraulic_or_geometry_field": {
                "required_table": "site_topology_or_bed_geometry",
                "required_fields": ["node_id", "bed_volume", "nominal_HRT_min", "flow_Lmin"],
                "minimum_evidence": "bed geometry and flow records to normalize reaction rate residuals",
            },
        }
        seen: set[str] = set()
        requirements: list[dict[str, object]] = []
        for patch in prioritized_patches:
            patch_class = str(patch["patch_class"])
            if patch_class in seen:
                continue
            seen.add(patch_class)
            requirement = dict(class_to_requirement.get(patch_class, {}))
            if not requirement:
                continue
            requirement["requirement_id"] = f"CAX_{len(requirements) + 1}_{patch_class}"
            requirement["patch_class"] = patch_class
            requirement["supports_patch_signals"] = [
                str(item["patch_signal"]) for item in prioritized_patches if str(item["patch_class"]) == patch_class
            ]
            requirement["evidence_stage_required"] = "field_proxy_holdout"
            requirements.append(requirement)
        return requirements

    @staticmethod
    def _recommended_sensor_patches(proxy_catalog: list[dict[str, object]]) -> list[str]:
        patches: list[str] = []
        for item in proxy_catalog:
            for patch in item["recommended_patch"]:
                if patch not in patches and patch in item["missing_signals"]:
                    patches.append(str(patch))
        return patches

    def _readiness(self, proxy_metrics: dict[str, object]) -> dict[str, object]:
        field_summary_ready = self.field_proxy_holdout_summary.get("ready_for_agent51_validation") is True
        field_ready = self.data_origin == "field_proxy_holdout" or field_summary_ready
        field_correlation = float(self.field_validation.get("proxy_label_correlation", proxy_metrics["synthetic_proxy_label_correlation"]))
        field_mae = float(self.field_validation.get("holdout_mae", proxy_metrics["synthetic_proxy_label_mae"]))
        field_label_coverage = float(self.field_validation.get("field_label_coverage", 0.0))
        proxy_ready = float(proxy_metrics["proxy_observability_after_recommended_patch"]) >= self.min_proxy_observability
        field_validated = (
            field_ready
            and field_label_coverage >= 0.75
            and field_correlation >= self.min_field_correlation
            and field_mae <= self.max_field_mae
        )
        score = round(
            0.34 * min(1.0, float(proxy_metrics["proxy_observability_after_recommended_patch"]) / self.min_proxy_observability)
            + 0.16 * min(1.0, float(proxy_metrics["weighted_patch_proxy_support"]))
            + 0.16 * min(1.0, max(0.0, field_correlation))
            + 0.14 * min(1.0, max(0.0, 1.0 - field_mae))
            + 0.10 * float(field_ready)
            + 0.10 * float(field_validated),
            3,
        )
        if not field_ready:
            status = "synthetic_catalyst_proxy_design_ready_needs_field_labels"
        elif not proxy_ready or not field_validated:
            status = "field_catalyst_proxy_needs_recalibration"
        else:
            status = "field_catalyst_proxy_candidate_ready"
        return {
            "catalyst_proxy_status": status,
            "catalyst_proxy_score": score,
            "data_origin": self.data_origin,
            "field_proxy_holdout_summary_status": self.field_proxy_holdout_summary.get(
                "field_proxy_holdout_summary_status",
                "not_supplied",
            ),
            "field_holdout_scoreable_batch_count": int(
                self.field_proxy_holdout_summary.get("scoreable_batch_count", 0) or 0
            ),
            "field_holdout_matched_batch_count": int(
                self.field_proxy_holdout_summary.get("matched_batch_count", 0) or 0
            ),
            "pressure_evidence_source_contract": [
                "node_modality_sensor_timeseries",
                "pressure_headloss_event_log",
            ],
            "accepted_pressure_evidence_sources": self.field_proxy_holdout_summary.get(
                "accepted_pressure_evidence_sources",
                [],
            ),
            "pressure_headloss_event_source_batch_count": int(
                self.field_proxy_holdout_summary.get("pressure_headloss_event_source_batch_count", 0) or 0
            ),
            "pressure_evidence_source_batch_counts": self.field_proxy_holdout_summary.get(
                "pressure_evidence_source_batch_counts",
                {},
            ),
            "field_labels_required": not field_ready,
            "proxy_ready": proxy_ready,
            "field_validated": field_validated,
            "can_update_agent48_prior": True,
            "can_relax_agent49_catalyst_uncertainty_block": field_validated,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        }

    @staticmethod
    def _agent49_interface(
        readiness: dict[str, object],
        proxy_metrics: dict[str, object],
        weak_axis_repair_plan: dict[str, object],
    ) -> dict[str, object]:
        return {
            "facility_agent": "catalyst_bed_agent",
            "state_patch": {
                "catalyst_activity_proxy_observability": proxy_metrics["proxy_observability_after_recommended_patch"],
                "weak_state_coverage_after_proxy_design": proxy_metrics["weak_state_coverage_after_proxy_design"],
                "recommended_sensor_patches": proxy_metrics["recommended_sensor_patches"],
                "weak_axis_repair_status": weak_axis_repair_plan["repair_status"],
                "prioritized_proxy_patches": weak_axis_repair_plan["prioritized_proxy_patches"],
            },
            "policy_effect": (
                "keep_R3_catalyst_uncertainty_block"
                if not readiness["can_relax_agent49_catalyst_uncertainty_block"]
                else "allow_field_reviewed_relaxation_of_R3_catalyst_uncertainty_block"
            ),
            "can_relax_catalyst_uncertainty_block": readiness["can_relax_agent49_catalyst_uncertainty_block"],
            "boundary": "synthetic proxy design cannot relax Agent49 actuator or release gate blocks",
        }

    def _issues(
        self,
        proxy_catalog: list[dict[str, object]],
        readiness: dict[str, object],
        proxy_metrics: dict[str, object],
        weak_axis_repair_plan: dict[str, object],
    ) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        missing = {
            str(signal)
            for item in proxy_catalog
            for signal in item["missing_signals"]
        }
        if missing:
            issues.append(
                QualityIssue(
                    sensor="catalyst_activity_proxy",
                    issue_type="proxy_required_signals_missing",
                    severity=Severity.WARNING,
                    message="催化剂活性代理仍缺少床前后差分、压降或再生事件相关信号。",
                    evidence={"missing_signals": sorted(missing)},
                )
            )
        if readiness["field_labels_required"]:
            issues.append(
                QualityIssue(
                    sensor="catalyst_activity_proxy",
                    issue_type="field_catalyst_labels_required",
                    severity=Severity.WARNING,
                    message="当前代理只是在 synthetic proxy cases 上可计算，必须用真实催化剂活性/再生/压降标签验证。",
                    evidence={"data_origin": self.data_origin},
                )
            )
        if self.field_proxy_holdout_summary and not self.field_proxy_holdout_summary.get(
            "ready_for_agent51_validation",
            False,
        ):
            issues.append(
                QualityIssue(
                    sensor="agent51_field_proxy_holdout",
                    issue_type="field_proxy_holdout_summary_not_ready",
                    severity=Severity.WARNING,
                    message="已提供 field proxy holdout 摘要，但批次、信号、标签或主表上下文不足，暂不能作为 Agent51 field validation 输入。",
                    evidence={
                        "status": self.field_proxy_holdout_summary.get("field_proxy_holdout_summary_status"),
                        "matched_batch_count": self.field_proxy_holdout_summary.get("matched_batch_count"),
                        "scoreable_batch_count": self.field_proxy_holdout_summary.get("scoreable_batch_count"),
                    },
                )
            )
        if (
            self.field_proxy_holdout_summary.get("ready_for_agent51_validation") is True
            and not readiness["field_validated"]
        ):
            issues.append(
                QualityIssue(
                    sensor="agent51_field_proxy_holdout",
                    issue_type="field_proxy_holdout_recalibration_required",
                    severity=Severity.WARNING,
                    message="现场包已经可以进入 Agent51 holdout 评分，但相关性、MAE 或标签覆盖尚未达到放松 Agent49 催化剂保护的阈值。",
                    evidence={
                        "field_validation": self.field_validation,
                        "thresholds": {
                            "min_field_correlation": self.min_field_correlation,
                            "max_field_mae": self.max_field_mae,
                        },
                    },
                )
            )
        if not readiness["can_relax_agent49_catalyst_uncertainty_block"]:
            issues.append(
                QualityIssue(
                    sensor="agent49_catalyst_block",
                    issue_type="catalyst_proxy_cannot_relax_agent49_block",
                    severity=Severity.INFO,
                    message="未通过 field proxy holdout 前，Agent49 的催化剂不确定性保护规则仍必须保留。",
                    evidence=proxy_metrics,
                )
            )
        if weak_axis_repair_plan["repair_status"] == "agent48_catalyst_axis_requires_proxy_patch_and_field_label":
            issues.append(
                QualityIssue(
                    sensor="agent48_catalyst_axis",
                    issue_type="agent48_catalyst_axis_not_recoverable_by_current_candidate_pool",
                    severity=Severity.WARNING,
                    message="Agent48 诊断显示 catalyst_activity 弱轴无法由当前低成本候选池自然补足，必须通过代理补点和 field labels 修复。",
                    evidence=weak_axis_repair_plan,
                )
            )
        return issues

    @staticmethod
    def _recommendations(
        proxy_catalog: list[dict[str, object]],
        readiness: dict[str, object],
        weak_axis_repair_plan: dict[str, object],
    ) -> list[str]:
        patches = sorted(
            {
                str(patch)
                for item in proxy_catalog
                for patch in item["recommended_patch"]
                if patch in item["missing_signals"]
            }
        )
        recs = [
            "把 catalyst_activity 从单点弱状态改成床前后差分、反应速率残差、污堵/压降和再生响应共同支持的代理观测。",
            "将 proxy_observability_after_recommended_patch 写回 Agent48/Agent49 作为设计先验，但 synthetic 阶段不能解除执行器保护规则。",
        ]
        if patches:
            recs.append(f"优先补充这些信号或字段：{patches}。")
        if weak_axis_repair_plan["repair_status"] == "agent48_catalyst_axis_requires_proxy_patch_and_field_label":
            recs.append(
                "Agent48 已证明 catalyst_activity 不是当前候选池可自然补足的弱轴；下一步应按 weak_axis_repair_plan "
                "优先补床出口 UV254/ORP、压降、再生事件和离线活性标签。"
            )
        if readiness["field_labels_required"]:
            recs.append("下一步需要 field_proxy_holdout：至少包含催化剂活性离线标签、压降、再生事件和床前后 UV254/ORP。")
        elif readiness.get("field_validated"):
            recs.append("field_proxy_holdout 已达到 Agent51 候选阈值；下一步只能进入 Agent49 replay 和人工证据门控，仍不能直接写执行器。")
        else:
            recs.append("field_proxy_holdout 已接入 Agent51，但需要重新校准代理公式或补更多现场批次后再考虑放松催化剂保护。")
        return recs

    @staticmethod
    def _method_contract() -> dict[str, object]:
        return {
            "upgrade_id": "catalyst_activity_proxy_observability",
            "borrowed_from": [
                "UV254 removal monitoring for organic oxidation progress",
                "ORP as low-cost oxidation process signal",
                "pressure-drop/turbidity fouling diagnostics for packed or catalyst beds",
                "regeneration response gain for catalyst deactivation diagnosis",
                "grey-box residence-time-normalized rate residual",
            ],
            "reality_mapping": "把不可直接在线观测的 catalyst_activity 拆成床前后水质差分、氧化还原变化、污堵/压降、再生响应和停留时间归一化速率残差。",
            "input_contract": [
                "Agent48 sparse placement metrics",
                "paired catalyst bed inlet/outlet UV254 or ORP",
                "turbidity and pressure drop around catalyst bed",
                "operation log regeneration events",
                "field catalyst activity labels for holdout validation",
                "R7j node_modality_sensor_timeseries + pressure_headloss_event_log + offline_lab_results + operation log + bed geometry package",
            ],
            "output_contract": [
                "proxy_catalog",
                "proxy_feature_table",
                "proxy_observability_after_recommended_patch",
                "weak_state_coverage_after_proxy_design",
                "field_proxy_holdout_summary",
                "weak_axis_repair_plan",
                "agent49_interface",
            ],
            "data_needs": [
                "catalyst_bed_inlet_outlet_uv254",
                "catalyst_bed_inlet_outlet_orp",
                "pressure_drop_kPa",
                "pressure_headloss_event_log.pressure_drop_kPa",
                "pressure_headloss_event_log.headloss_kPa_per_m",
                "turbidity_delta",
                "bed_hydraulic_residence_time",
                "regeneration_event_log",
                "offline_catalyst_activity_label",
            ],
            "evaluation_metrics": [
                "proxy_observability_after_recommended_patch",
                "weak_state_coverage_after_proxy_design",
                "proxy_label_correlation",
                "holdout_mae",
                "can_relax_agent49_catalyst_uncertainty_block",
                "weak_axis_repair_plan.repair_score",
                "weak_axis_repair_plan.field_repair_evidence_requirements",
                "field_proxy_holdout_summary.scoreable_batch_count",
                "field_proxy_holdout_summary.accepted_pressure_evidence_sources",
                "field_proxy_holdout_summary.pressure_headloss_event_source_batch_count",
            ],
            "failure_boundary": "synthetic proxy design can update model priors, but cannot prove real catalyst deactivation or relax Agent49 actuator/release gates without field_proxy_holdout.",
        }

    @staticmethod
    def _field_validation_from_holdout_summary(summary: dict[str, object]) -> dict[str, float]:
        metrics = summary.get("field_validation_metrics", {})
        if not isinstance(metrics, dict):
            return {}
        keys = ("field_label_coverage", "proxy_label_correlation", "holdout_mae")
        parsed: dict[str, float] = {}
        for key in keys:
            value = metrics.get(key)
            if isinstance(value, int | float):
                parsed[key] = float(value)
        return parsed

    def _field_validation_source(self) -> str:
        if self.field_proxy_holdout_summary:
            return "field_proxy_holdout_summary"
        if self.field_validation:
            return "manual_field_validation_metrics"
        return "synthetic_proxy_cases"

    @staticmethod
    def _default_proxy_cases() -> list[dict[str, float | str]]:
        return [
            {
                "case_id": "C0_healthy_active",
                "scenario": "healthy_active_catalyst",
                "uv254_in": 1.05,
                "uv254_out": 0.34,
                "orp_in_mV": 710.0,
                "orp_out_mV": 595.0,
                "turbidity_in_NTU": 4.0,
                "turbidity_out_NTU": 4.8,
                "pressure_drop_kPa": 0.08,
                "hrt_min": 18.0,
                "expected_rate_per_min": 0.055,
                "pre_regen_uv254_removal": 0.58,
                "post_regen_uv254_removal": 0.70,
                "catalyst_activity_label": 0.78,
            },
            {
                "case_id": "C1_reversible_fouling",
                "scenario": "fouled_but_regenerable",
                "uv254_in": 1.10,
                "uv254_out": 0.68,
                "orp_in_mV": 690.0,
                "orp_out_mV": 635.0,
                "turbidity_in_NTU": 5.0,
                "turbidity_out_NTU": 18.0,
                "pressure_drop_kPa": 0.30,
                "hrt_min": 20.0,
                "expected_rate_per_min": 0.050,
                "pre_regen_uv254_removal": 0.36,
                "post_regen_uv254_removal": 0.61,
                "catalyst_activity_label": 0.46,
            },
            {
                "case_id": "C2_exhausted_low_response",
                "scenario": "exhausted_or_irreversible_deactivation",
                "uv254_in": 1.00,
                "uv254_out": 0.78,
                "orp_in_mV": 705.0,
                "orp_out_mV": 675.0,
                "turbidity_in_NTU": 4.0,
                "turbidity_out_NTU": 6.5,
                "pressure_drop_kPa": 0.13,
                "hrt_min": 22.0,
                "expected_rate_per_min": 0.052,
                "pre_regen_uv254_removal": 0.21,
                "post_regen_uv254_removal": 0.27,
                "catalyst_activity_label": 0.28,
            },
            {
                "case_id": "C3_matrix_suppressed",
                "scenario": "matrix_interference_masks_activity",
                "uv254_in": 1.25,
                "uv254_out": 0.78,
                "orp_in_mV": 650.0,
                "orp_out_mV": 610.0,
                "turbidity_in_NTU": 9.0,
                "turbidity_out_NTU": 16.0,
                "pressure_drop_kPa": 0.19,
                "hrt_min": 24.0,
                "expected_rate_per_min": 0.040,
                "pre_regen_uv254_removal": 0.33,
                "post_regen_uv254_removal": 0.43,
                "catalyst_activity_label": 0.52,
            },
        ]

    @staticmethod
    def _clip(value: float) -> float:
        return max(0.0, min(1.0, value))

    @staticmethod
    def _correlation(xs: list[float], ys: list[float]) -> float:
        if len(xs) < 2 or len(xs) != len(ys):
            return 0.0
        mean_x = sum(xs) / len(xs)
        mean_y = sum(ys) / len(ys)
        num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys, strict=True))
        den_x = sum((x - mean_x) ** 2 for x in xs) ** 0.5
        den_y = sum((y - mean_y) ** 2 for y in ys) ** 0.5
        return round(num / max(1e-9, den_x * den_y), 3)
