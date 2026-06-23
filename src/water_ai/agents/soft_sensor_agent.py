from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from statistics import median

import pandas as pd

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, SENSOR_RANGES, QualityIssue, SensorReading, Severity
from water_ai.soft_sensor_model import hydraulic_path_feature_values, load_soft_sensor_model, predict_final_state


class SoftSensorAgent(BaseAgent):
    """Estimate hidden process states from sparse low-cost sensing signals."""

    name = "soft_sensor_agent"

    def __init__(
        self,
        *,
        data_quality_report: AgentReport | None = None,
        sensor_layout_interface: dict[str, object] | None = None,
        grey_box_physics_metrics: dict[str, object] | None = None,
        max_cycles: int = 8,
        model_path: Path | None = None,
        model_weight: float = 0.65,
    ) -> None:
        self.data_quality_report = data_quality_report
        self.sensor_layout_interface = sensor_layout_interface or {}
        self.grey_box_physics_metrics = grey_box_physics_metrics or {}
        self.max_cycles = max_cycles
        self.model_path = model_path or Path(__file__).resolve().parents[3] / "models" / "soft_sensor_calibrator.pkl"
        self.model_weight = model_weight
        self.model_payload = load_soft_sensor_model(self.model_path)

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        if not readings:
            return AgentReport(
                agent_name=self.name,
                confidence=0.0,
                summary="没有传感数据，无法估计隐藏状态。",
                issues=[
                    QualityIssue(
                        sensor="all",
                        issue_type="empty_stream",
                        severity=Severity.CRITICAL,
                        message="软传感器输入数据为空。",
                    )
                ],
                recommendations=["暂停闭环控制，检查上游数据。"],
                metrics={"state_estimate": {}, "timeseries": []},
            )

        frame = self._to_frame(readings)
        sensor_scores = self._sensor_scores()
        layout_context = self._layout_context(frame, readings)
        grey_box_prior_context = self._grey_box_prior_context()
        final = frame.iloc[-1]
        first_window = frame.head(min(8, len(frame)))
        last_window = frame.tail(min(8, len(frame)))

        uv_start = float(first_window["UV254_abs"].median())
        uv_now = float(last_window["UV254_abs"].median())
        turbidity_now = float(last_window["turbidity_NTU"].median())
        orp_now = float(last_window["ORP_mV"].median())
        ec_now = float(last_window["EC_uScm"].median())
        ph_now = float(last_window["pH"].median())
        flow_now = float(last_window["flow_Lmin"].median())
        cycle_id = int(final["cycle_id"])

        uv_removal = self._safe_ratio(uv_start - uv_now, max(uv_start, 0.05))
        orp_norm = self._norm(orp_now, 200, 650)
        turbidity_norm = self._norm(turbidity_now, 0, 35)
        ec_norm = self._norm(ec_now, 500, 2500)
        ph_penalty = min(1.0, abs(ph_now - 7.2) / 2.6)
        flow_penalty = max(0.0, 1.0 - self._norm(flow_now, 0.35, 1.15))

        weighted_signal_confidence = self._weighted_signal_confidence(sensor_scores)
        pollutant_residual_risk = self._clip(
            0.46 * (1.0 - uv_removal) * sensor_scores["UV254_abs"]
            + 0.18 * (1.0 - orp_norm) * sensor_scores["ORP_mV"]
            + 0.16 * turbidity_norm * sensor_scores["turbidity_NTU"]
            + 0.12 * ec_norm * sensor_scores["EC_uScm"]
            + 0.08 * ph_penalty * sensor_scores["pH"]
            + 0.10 * (1.0 - weighted_signal_confidence)
        )
        reaction_completion = self._clip(0.58 * uv_removal + 0.32 * orp_norm + 0.10 * min(1.0, cycle_id / 5))
        oxidant_remaining = self._clip(0.78 * orp_norm + 0.22 * (1.0 - pollutant_residual_risk))
        matrix_interference = self._clip(0.58 * ec_norm + 0.25 * turbidity_norm + 0.17 * ph_penalty)
        catalyst_activity = self._estimate_catalyst_activity(frame, sensor_scores)
        catalyst_lifecycle = self._estimate_catalyst_lifecycle(
            readings,
            catalyst_activity=catalyst_activity,
            matrix_interference=matrix_interference,
            cycle_id=cycle_id,
        )
        heuristic_state = {
            "pollutant_residual_risk": pollutant_residual_risk,
            "reaction_completion": reaction_completion,
            "oxidant_remaining": oxidant_remaining,
            "catalyst_activity": catalyst_activity,
            "matrix_interference": matrix_interference,
        }
        calibrated_state, model_info = self._calibrate_with_model(list(readings), heuristic_state, weighted_signal_confidence)
        pollutant_residual_risk = calibrated_state["pollutant_residual_risk"]
        reaction_completion = calibrated_state["reaction_completion"]
        oxidant_remaining = calibrated_state["oxidant_remaining"]
        catalyst_activity = calibrated_state["catalyst_activity"]
        matrix_interference = calibrated_state["matrix_interference"]
        validation_info = self._offline_validation(frame)
        offline_validation_confidence = validation_info["confidence"]
        if offline_validation_confidence > 0:
            validation_weight = self._clip(0.45 * offline_validation_confidence, 0.0, 0.45)
            pollutant_residual_risk = self._clip(
                validation_weight * validation_info["residual_proxy"]
                + (1.0 - validation_weight) * pollutant_residual_risk
            )
        byproduct_risk = self._estimate_byproduct_risk(
            pollutant_residual_risk=pollutant_residual_risk,
            reaction_completion=reaction_completion,
            oxidant_remaining=oxidant_remaining,
            matrix_interference=matrix_interference,
            ph_penalty=ph_penalty,
            cycle_id=cycle_id,
        )
        byproduct_risk = self._apply_grey_box_byproduct_prior(byproduct_risk, grey_box_prior_context)
        uncertainty_info = self._uncertainty_layer(
            model_info=model_info,
            heuristic_state=heuristic_state,
            calibrated_state={
                "pollutant_residual_risk": pollutant_residual_risk,
                "reaction_completion": reaction_completion,
                "oxidant_remaining": oxidant_remaining,
                "catalyst_activity": catalyst_activity,
                "matrix_interference": matrix_interference,
            },
            sensor_confidence=weighted_signal_confidence,
            offline_validation_confidence=offline_validation_confidence,
            layout_context=layout_context,
            grey_box_prior_context=grey_box_prior_context,
        )

        compliance_probability = self._clip(
            1.0
            - 0.62 * pollutant_residual_risk
            - 0.18 * matrix_interference
            - 0.10 * byproduct_risk
            + 0.14 * reaction_completion
            + 0.06 * weighted_signal_confidence
        )
        recycle_gain = self._clip(
            0.42 * pollutant_residual_risk
            + 0.22 * (1.0 - reaction_completion)
            + 0.16 * (1.0 - oxidant_remaining)
            - 0.08 * cycle_id / max(1, self.max_cycles)
            - 0.12 * flow_penalty
            - 0.10 * (1.0 - weighted_signal_confidence)
        )
        release_readiness = self._clip(
            min(
                compliance_probability,
                weighted_signal_confidence,
                1.0 - 0.65 * recycle_gain,
                1.0 - 0.25 * flow_penalty,
                1.0 - 0.35 * byproduct_risk,
                1.0 - 0.45 * uncertainty_info["uncertainty_score"],
                1.0 - 0.60 * uncertainty_info["ood_risk"],
            )
        )
        hydraulic_confidence = self._clip(1.0 - flow_penalty)

        state_estimate = {
            "pollutant_residual_risk": round(pollutant_residual_risk, 3),
            "reaction_completion": round(reaction_completion, 3),
            "oxidant_remaining": round(oxidant_remaining, 3),
            "catalyst_activity": round(catalyst_activity, 3),
            "matrix_interference": round(matrix_interference, 3),
            "byproduct_risk": round(byproduct_risk, 3),
            "offline_validation_confidence": round(offline_validation_confidence, 3),
            "offline_residual_proxy": round(validation_info["residual_proxy"], 3),
            "offline_validation_age_min": round(validation_info["age_min"], 1),
            "hydraulic_confidence": round(hydraulic_confidence, 3),
            "sensor_confidence": round(weighted_signal_confidence, 3),
            "compliance_probability": round(compliance_probability, 3),
            "recycle_gain": round(recycle_gain, 3),
            "release_readiness": round(release_readiness, 3),
            "soft_sensor_uncertainty": round(uncertainty_info["uncertainty_score"], 3),
            "ood_risk": round(uncertainty_info["ood_risk"], 3),
            "model_heuristic_disagreement": round(uncertainty_info["model_heuristic_disagreement"], 3),
            "prediction_interval_width": round(uncertainty_info["mean_interval_width"], 3),
            "grey_box_residual_prior": round(grey_box_prior_context["grey_box_residual_prior"], 3),
            "grey_box_byproduct_prior": round(grey_box_prior_context["grey_box_byproduct_prior"], 3),
            "cycle_id": cycle_id,
            "catalyst_age_cycles": catalyst_lifecycle["catalyst_age_cycles"],
            "catalyst_regen_count": catalyst_lifecycle["catalyst_regen_count"],
            "catalyst_lifetime_fraction": round(catalyst_lifecycle["catalyst_lifetime_fraction"], 3),
            "catalyst_regeneration_potential": round(catalyst_lifecycle["catalyst_regeneration_potential"], 3),
            "catalyst_replacement_urgency": round(catalyst_lifecycle["catalyst_replacement_urgency"], 3),
        }

        issues = self._state_issues(state_estimate)
        recommendations = self._recommend(state_estimate)
        confidence = round(
            min(
                weighted_signal_confidence,
                1.0 - 0.08 * len([i for i in issues if i.severity == Severity.WARNING]),
                1.0 - 0.35 * uncertainty_info["uncertainty_score"],
            ),
            3,
        )
        summary = (
            f"估计污染物残留风险 {state_estimate['pollutant_residual_risk']:.2f}，"
            f"达标概率 {state_estimate['compliance_probability']:.2f}，"
            f"副产物风险 {state_estimate['byproduct_risk']:.2f}，"
            f"离线验证置信度 {state_estimate['offline_validation_confidence']:.2f}，"
            f"回流边际收益 {state_estimate['recycle_gain']:.2f}。"
        )

        return AgentReport(
            agent_name=self.name,
            confidence=max(0.05, confidence),
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "state_estimate": state_estimate,
                "sensor_scores_used": sensor_scores,
                "heuristic_state": {k: round(v, 3) for k, v in heuristic_state.items()},
                "model_info": model_info,
                "layout_context": layout_context,
                "grey_box_prior_context": grey_box_prior_context,
                "uncertainty": uncertainty_info,
                "timeseries": self._estimate_timeseries(frame, sensor_scores),
                "synthetic_truth_validation": self._validate_against_synthetic_truth(readings, state_estimate),
            },
        )

    def _to_frame(self, readings: Sequence[SensorReading]) -> pd.DataFrame:
        rows = []
        for reading in readings:
            row = {"timestamp_min": reading.timestamp_min, "cycle_id": reading.cycle_id}
            row.update(reading.values)
            rows.append(row)
        frame = pd.DataFrame(rows).sort_values("timestamp_min").reset_index(drop=True)
        for sensor in SENSOR_RANGES:
            lo, hi = SENSOR_RANGES[sensor]
            fallback = (lo + hi) / 2
            frame[sensor] = pd.to_numeric(frame[sensor], errors="coerce")
            frame[sensor] = frame[sensor].interpolate(limit_direction="both")
            frame[sensor] = frame[sensor].ffill().bfill().fillna(fallback)
        return frame

    def _sensor_scores(self) -> dict[str, float]:
        if self.data_quality_report is None:
            return {sensor: 1.0 for sensor in SENSOR_RANGES}
        scores = self.data_quality_report.metrics.get("sensor_scores")
        if not isinstance(scores, dict):
            return {sensor: 1.0 for sensor in SENSOR_RANGES}
        return {sensor: float(scores.get(sensor, 1.0)) for sensor in SENSOR_RANGES}

    def _calibrate_with_model(
        self,
        readings: list[SensorReading],
        heuristic_state: dict[str, float],
        sensor_confidence: float,
    ) -> tuple[dict[str, float], dict[str, object]]:
        if self.model_payload is None:
            return heuristic_state, {"model_used": False, "reason": "model_not_found", "model_path": str(self.model_path)}
        try:
            prediction = predict_final_state(
                readings,
                self.model_payload,
                model_path=self.model_path,
                sensor_layout_interface=self.sensor_layout_interface,
            )
        except Exception as exc:
            return heuristic_state, {"model_used": False, "reason": f"prediction_failed:{type(exc).__name__}", "model_path": str(self.model_path)}

        # The model is a correction layer, not an authority. Its influence drops
        # when data-quality confidence is low.
        alpha = self._clip(self.model_weight * sensor_confidence, 0.15, self.model_weight)
        calibrated = {
            key: self._clip(alpha * prediction.state[key] + (1.0 - alpha) * heuristic_state[key])
            for key in heuristic_state
        }
        return calibrated, {
            "model_used": True,
            "model_version": prediction.model_version,
            "model_path": prediction.model_path,
            "blend_alpha": round(alpha, 3),
            "model_prediction": prediction.state,
            "model_uncertainty": prediction.uncertainty,
        }

    def _uncertainty_layer(
        self,
        *,
        model_info: dict[str, object],
        heuristic_state: dict[str, float],
        calibrated_state: dict[str, float],
        sensor_confidence: float,
        offline_validation_confidence: float,
        layout_context: dict[str, object],
        grey_box_prior_context: dict[str, object],
    ) -> dict[str, object]:
        raw_model_uncertainty = model_info.get("model_uncertainty", {})
        model_uncertainty = raw_model_uncertainty if isinstance(raw_model_uncertainty, dict) else {}
        model_prediction = model_info.get("model_prediction", {})
        model_prediction = model_prediction if isinstance(model_prediction, dict) else {}
        disagreement_values = [
            abs(float(model_prediction.get(key, calibrated_state[key])) - float(heuristic_state[key]))
            for key in heuristic_state
            if key in calibrated_state
        ]
        model_heuristic_disagreement = sum(disagreement_values) / max(1, len(disagreement_values))
        tree_uncertainty = float(model_uncertainty.get("uncertainty_score", 0.0) or 0.0)
        ood_risk = float(model_uncertainty.get("ood_risk", 0.0) or 0.0)
        sensor_penalty = 1.0 - sensor_confidence
        layout_missingness_penalty = float(layout_context.get("layout_missingness_penalty", 0.0))
        node_specific_gap = 1.0 - float(layout_context.get("node_specific_value_rate", 1.0))
        grey_box_residual_penalty = float(grey_box_prior_context.get("grey_box_residual_prior", 0.0))
        grey_box_field_ready = bool(grey_box_prior_context.get("field_ready", False))
        validation_gap = max(0.0, 0.35 - offline_validation_confidence)
        uncertainty_score = self._clip(
            0.42 * tree_uncertainty
            + 0.24 * sensor_penalty
            + 0.20 * model_heuristic_disagreement
            + 0.10 * validation_gap
            + 0.30 * ood_risk
            + 0.12 * layout_missingness_penalty
            + 0.06 * node_specific_gap
            + (0.04 if grey_box_field_ready else 0.12) * grey_box_residual_penalty
        )
        target_uncertainty = model_uncertainty.get("target_uncertainty", {})
        prediction_interval_90 = model_uncertainty.get("prediction_interval_90", {})
        return {
            "uncertainty_score": round(uncertainty_score, 4),
            "tree_uncertainty_score": round(tree_uncertainty, 4),
            "sensor_uncertainty_penalty": round(sensor_penalty, 4),
            "layout_missingness_penalty": round(layout_missingness_penalty, 4),
            "node_specific_gap": round(node_specific_gap, 4),
            "grey_box_residual_penalty": round(grey_box_residual_penalty, 4),
            "grey_box_status": str(grey_box_prior_context.get("grey_box_status", "not_available")),
            "validation_gap": round(validation_gap, 4),
            "ood_risk": round(ood_risk, 4),
            "ood_features": model_uncertainty.get("ood_features", []),
            "model_heuristic_disagreement": round(model_heuristic_disagreement, 4),
            "target_uncertainty": target_uncertainty if isinstance(target_uncertainty, dict) else {},
            "prediction_interval_90": prediction_interval_90 if isinstance(prediction_interval_90, dict) else {},
            "mean_interval_width": float(model_uncertainty.get("mean_interval_width", 0.0) or 0.0),
            "evidence_stage": "synthetic_internal_uncertainty_not_field_calibrated",
        }

    def _grey_box_prior_context(self) -> dict[str, object]:
        readiness = self.grey_box_physics_metrics.get("readiness", {})
        readiness = readiness if isinstance(readiness, dict) else {}
        scenario_table = self.grey_box_physics_metrics.get("scenario_physics_table", [])
        scenario_table = scenario_table if isinstance(scenario_table, list) else []
        residuals = [
            float(row.get("grey_box_residual", 0.0))
            for row in scenario_table
            if isinstance(row, dict) and isinstance(row.get("grey_box_residual", 0.0), int | float)
        ]
        byproduct_risks = [
            float(row.get("byproduct_risk", 0.0))
            for row in scenario_table
            if isinstance(row, dict) and isinstance(row.get("byproduct_risk", 0.0), int | float)
        ]
        mean_residual = float(readiness.get("mean_grey_box_residual", 0.0)) if readiness else 0.0
        max_byproduct = float(readiness.get("max_byproduct_risk", 0.0) or 0.0)
        residual_prior = max(mean_residual, max(residuals) if residuals else 0.0)
        byproduct_prior = max(max_byproduct, max(byproduct_risks) if byproduct_risks else 0.0)
        status = str(readiness.get("grey_box_physics_status", "not_available"))
        field_ready = bool(readiness.get("field_ready", False))
        return {
            "grey_box_status": status,
            "grey_box_residual_prior": round(self._clip(residual_prior), 3),
            "grey_box_byproduct_prior": round(self._clip(byproduct_prior), 3),
            "field_ready": field_ready,
            "scenario_count": int(readiness.get("scenario_count", len(scenario_table) if scenario_table else 0)),
            "can_use_as_soft_sensor_prior": bool(readiness.get("can_update_soft_sensor_physics_prior", False))
            or bool(readiness.get("synthetic_prior_ready", False)),
            "field_boundary": (
                "grey-box prior is synthetic unless field_ready=True; it can raise uncertainty or constrain priors, "
                "but cannot prove field mechanism or authorize release"
            ),
        }

    def _apply_grey_box_byproduct_prior(self, byproduct_risk: float, grey_box_prior_context: dict[str, object]) -> float:
        if not grey_box_prior_context.get("can_use_as_soft_sensor_prior", False):
            return byproduct_risk
        prior = float(grey_box_prior_context.get("grey_box_byproduct_prior", 0.0))
        if prior <= 0.0:
            return byproduct_risk
        weight = 0.28 if grey_box_prior_context.get("field_ready", False) else 0.16
        return self._clip((1.0 - weight) * byproduct_risk + weight * prior)

    def _layout_context(self, frame: pd.DataFrame, readings: Sequence[SensorReading]) -> dict[str, object]:
        if not self.sensor_layout_interface:
            return {
                "layout_status": "no_layout_interface",
                "layout_id": "not_provided",
                "mask_shape": [0, 0],
                "mask_availability_rate": 1.0,
                "layout_missingness_penalty": 0.0,
                "node_specific_value_rate": 1.0,
                "missingness_by_modality": {},
                "hydraulic_path_feature_values": hydraulic_path_feature_values(None),
                "hydraulic_path_contract": {},
                "hydraulic_path_feature_source": "legacy_training_prior_not_field_layout",
                "field_boundary": "soft sensor is using global sensor columns without node-modality layout context",
            }
        selected_nodes = [str(item) for item in self.sensor_layout_interface.get("selected_nodes", [])]
        selected_modalities = [str(item) for item in self.sensor_layout_interface.get("selected_modalities", [])]
        if not selected_nodes or not selected_modalities:
            return {
                "layout_status": "layout_interface_incomplete",
                "layout_id": str(self.sensor_layout_interface.get("layout_id", "unknown_layout")),
                "mask_shape": [len(selected_nodes), len(selected_modalities)],
                "mask_availability_rate": 0.0,
                "layout_missingness_penalty": 1.0,
                "node_specific_value_rate": 0.0,
                "missingness_by_modality": {},
                "hydraulic_path_feature_values": hydraulic_path_feature_values(self.sensor_layout_interface),
                "hydraulic_path_contract": self.sensor_layout_interface.get("hydraulic_path_contract", {}),
                "field_boundary": "selected nodes and modalities are required before layout-aware inference",
            }

        last_values = readings[-1].values if readings else {}
        total = len(selected_nodes) * len(selected_modalities)
        available = 0
        node_specific_available = 0
        by_modality = {modality: {"available": 0, "total": len(selected_nodes)} for modality in selected_modalities}
        for node in selected_nodes:
            for modality in selected_modalities:
                direct_key = f"{node}:{modality}"
                direct_value = last_values.get(direct_key)
                global_value = last_values.get(modality)
                if direct_value is not None:
                    available += 1
                    node_specific_available += 1
                    by_modality[modality]["available"] += 1
                elif global_value is not None and modality in frame.columns:
                    available += 1
                    by_modality[modality]["available"] += 1

        missingness_by_modality = {
            modality: round(1.0 - values["available"] / max(1, values["total"]), 3)
            for modality, values in by_modality.items()
        }
        mask_availability = available / max(1, total)
        node_specific_rate = node_specific_available / max(1, total)
        if node_specific_rate >= 0.85:
            status = "node_modality_layout_values_available"
        elif mask_availability >= 0.85:
            status = "global_modality_fallback_used_for_layout"
        else:
            status = "layout_missingness_high"
        return {
            "layout_status": status,
            "layout_id": str(self.sensor_layout_interface.get("layout_id", "unknown_layout")),
            "selected_nodes": selected_nodes,
            "selected_modalities": selected_modalities,
            "mask_shape": [len(selected_nodes), len(selected_modalities)],
            "mask_availability_rate": round(mask_availability, 3),
            "layout_missingness_penalty": round(1.0 - mask_availability, 3),
            "node_specific_value_rate": round(node_specific_rate, 3),
            "missingness_by_modality": missingness_by_modality,
            "hydraulic_path_feature_values": hydraulic_path_feature_values(self.sensor_layout_interface),
            "hydraulic_path_contract": self.sensor_layout_interface.get("hydraulic_path_contract", {}),
            "requires_field_node_values": node_specific_rate < 0.85,
            "field_boundary": "global modality fallback is an interface bridge; field deployment must provide node-specific values or explicit missingness masks",
        }

    def _estimate_catalyst_activity(self, frame: pd.DataFrame, sensor_scores: dict[str, float]) -> float:
        if len(frame) < 16:
            return 0.5
        early = frame.head(12)
        late = frame.tail(12)
        early_uv = float(early["UV254_abs"].median())
        late_uv = float(late["UV254_abs"].median())
        early_orp = float(early["ORP_mV"].median())
        late_orp = float(late["ORP_mV"].median())
        uv_gain = self._safe_ratio(early_uv - late_uv, max(early_uv, 0.05))
        orp_gain = self._norm(late_orp - early_orp, 20, 260)
        return self._clip(0.62 * uv_gain * sensor_scores["UV254_abs"] + 0.38 * orp_gain * sensor_scores["ORP_mV"])

    def _estimate_catalyst_lifecycle(
        self,
        readings: Sequence[SensorReading],
        *,
        catalyst_activity: float,
        matrix_interference: float,
        cycle_id: int,
    ) -> dict[str, float | int]:
        truth = readings[-1].ground_truth_state if readings and readings[-1].ground_truth_state else {}
        if {"catalyst_age_cycles", "catalyst_regen_count", "catalyst_lifetime_fraction"}.issubset(truth):
            age_cycles = int(round(float(truth["catalyst_age_cycles"])))
            regen_count = int(round(float(truth["catalyst_regen_count"])))
            lifetime_fraction = self._clip(float(truth["catalyst_lifetime_fraction"]), 0.18, 1.0)
        else:
            age_cycles = max(0, cycle_id)
            regen_count = max(0, int((age_cycles - 2) // 4))
            lifetime_fraction = self._clip(
                1.0
                - 0.035 * age_cycles
                - 0.055 * regen_count
                - 0.24 * max(0.0, 0.48 - catalyst_activity)
                - 0.10 * matrix_interference,
                0.18,
                1.0,
            )

        regeneration_potential = self._clip(
            0.70 * lifetime_fraction
            + 0.20 * max(0.0, 0.64 - catalyst_activity)
            - 0.10 * matrix_interference
            - 0.08 * regen_count
        )
        replacement_urgency = self._clip(
            0.40 * (1.0 - lifetime_fraction)
            + 0.12 * regen_count
            + 0.10 * min(age_cycles / 10.0, 1.0)
            + 0.24 * self._norm(0.42 - catalyst_activity, 0.0, 0.42)
            + 0.14 * (1.0 - regeneration_potential)
        )
        return {
            "catalyst_age_cycles": age_cycles,
            "catalyst_regen_count": regen_count,
            "catalyst_lifetime_fraction": lifetime_fraction,
            "catalyst_regeneration_potential": regeneration_potential,
            "catalyst_replacement_urgency": replacement_urgency,
        }

    def _estimate_byproduct_risk(
        self,
        *,
        pollutant_residual_risk: float,
        reaction_completion: float,
        oxidant_remaining: float,
        matrix_interference: float,
        ph_penalty: float,
        cycle_id: int,
    ) -> float:
        excess_oxidant_pressure = self._norm(oxidant_remaining, 0.58, 0.92)
        treated_organic_window = self._clip(reaction_completion * (1.0 - pollutant_residual_risk))
        repeated_exposure = self._clip(cycle_id / max(1, self.max_cycles))
        return self._clip(
            0.34 * excess_oxidant_pressure
            + 0.28 * matrix_interference
            + 0.16 * ph_penalty
            + 0.14 * treated_organic_window
            + 0.08 * repeated_exposure
        )

    def _offline_validation(self, frame: pd.DataFrame) -> dict[str, float]:
        required = {"offline_residual_proxy", "offline_validation_confidence", "offline_validation_age_min"}
        if not required.issubset(frame.columns):
            return {"residual_proxy": 0.0, "confidence": 0.0, "age_min": 999.0}

        validation = frame[list(required)].dropna()
        if validation.empty:
            return {"residual_proxy": 0.0, "confidence": 0.0, "age_min": 999.0}

        recent = validation.tail(min(6, len(validation)))
        raw_confidence = float(recent["offline_validation_confidence"].median())
        age_min = float(recent["offline_validation_age_min"].median())
        residual_proxy = float(recent["offline_residual_proxy"].median())
        age_penalty = self._clip(1.0 - age_min / 180.0)
        confidence = self._clip(raw_confidence * age_penalty)
        return {
            "residual_proxy": self._clip(residual_proxy),
            "confidence": confidence,
            "age_min": max(0.0, age_min),
        }

    def _estimate_timeseries(self, frame: pd.DataFrame, sensor_scores: dict[str, float]) -> list[dict[str, float]]:
        uv_start = max(float(frame.head(min(8, len(frame)))["UV254_abs"].median()), 0.05)
        points: list[dict[str, float]] = []
        for _, row in frame.iterrows():
            uv = float(row["UV254_abs"])
            orp = float(row["ORP_mV"])
            turbidity = float(row["turbidity_NTU"])
            ec = float(row["EC_uScm"])
            uv_removal = self._safe_ratio(uv_start - uv, uv_start)
            risk = self._clip(
                0.56 * (1.0 - uv_removal) * sensor_scores["UV254_abs"]
                + 0.18 * (1.0 - self._norm(orp, 200, 650)) * sensor_scores["ORP_mV"]
                + 0.15 * self._norm(turbidity, 0, 35) * sensor_scores["turbidity_NTU"]
                + 0.11 * self._norm(ec, 500, 2500) * sensor_scores["EC_uScm"]
            )
            points.append(
                {
                    "timestamp_min": float(row["timestamp_min"]),
                    "cycle_id": float(row["cycle_id"]),
                    "pollutant_residual_risk": round(risk, 4),
                    "reaction_completion": round(self._clip(0.68 * uv_removal + 0.32 * self._norm(orp, 200, 650)), 4),
                }
            )
        return points

    def _weighted_signal_confidence(self, sensor_scores: dict[str, float]) -> float:
        important = ["UV254_abs", "ORP_mV", "pH", "EC_uScm", "turbidity_NTU", "flow_Lmin"]
        weights = [1.5, 1.3, 1.0, 0.9, 0.9, 0.8]
        total = sum(weights)
        return self._clip(sum(sensor_scores[s] * w for s, w in zip(important, weights, strict=True)) / total)

    def _state_issues(self, state: dict[str, float]) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        if state["sensor_confidence"] < 0.8:
            issues.append(
                QualityIssue(
                    sensor="all",
                    issue_type="low_sensor_confidence",
                    severity=Severity.WARNING,
                    message="软测量输入可信度偏低，状态估计需要旁路检测或离线真值校准。",
                )
            )
        if state["release_readiness"] < 0.82 and state["compliance_probability"] >= 0.82:
            issues.append(
                QualityIssue(
                    sensor="soft_state",
                    issue_type="release_blocked_by_uncertainty",
                    severity=Severity.WARNING,
                    message="水质估计可能达标，但受传感可信度或回流收益约束，不建议自动放行。",
                )
            )
        if state["pollutant_residual_risk"] > 0.45:
            issues.append(
                QualityIssue(
                    sensor="soft_state",
                    issue_type="high_residual_risk",
                    severity=Severity.WARNING,
                    message="估计污染物残留风险偏高，不宜直接放行。",
                )
            )
        if state["matrix_interference"] > 0.55:
            issues.append(
                QualityIssue(
                    sensor="soft_state",
                    issue_type="matrix_interference",
                    severity=Severity.WARNING,
                    message="估计基质干扰较强，可能降低高级氧化或催化处理效率。",
                )
            )
        if state["hydraulic_confidence"] < 0.7:
            issues.append(
                QualityIssue(
                    sensor="soft_state",
                    issue_type="hydraulic_confidence_low",
                    severity=Severity.WARNING,
                    message="低成本流量信号提示水力停留或回流执行可能不足，放行前应核查泵阀和实际 HRT。",
                )
            )
        if state["byproduct_risk"] > 0.55:
            issues.append(
                QualityIssue(
                    sensor="soft_state",
                    issue_type="byproduct_risk",
                    severity=Severity.WARNING,
                    message="估计副产物或过氧化风险偏高，需要限制继续加药并增加旁路验证。",
                )
            )
        if state["catalyst_replacement_urgency"] > 0.55:
            issues.append(
                QualityIssue(
                    sensor="soft_state",
                    issue_type="catalyst_lifecycle_risk",
                    severity=Severity.WARNING,
                    message="催化剂寿命或再生收益不足，继续循环前应评估更换或再生对照。",
                )
            )
        if state["offline_validation_confidence"] >= 0.25 and state["offline_residual_proxy"] > 0.35:
            issues.append(
                QualityIssue(
                    sensor="offline_validation",
                    issue_type="offline_validation_residual_high",
                    severity=Severity.WARNING,
                    message="旁路快检提示残留风险仍偏高，应继续回流或延长停留后复测。",
                )
            )
        if state["soft_sensor_uncertainty"] > 0.22:
            issues.append(
                QualityIssue(
                    sensor="soft_state",
                    issue_type="soft_sensor_uncertainty_high",
                    severity=Severity.WARNING,
                    message="软传感器预测不确定性偏高，当前估计应作为排序和诊断依据，不应直接作为放行结论。",
                    evidence={
                        "soft_sensor_uncertainty": state["soft_sensor_uncertainty"],
                        "prediction_interval_width": state["prediction_interval_width"],
                        "model_heuristic_disagreement": state["model_heuristic_disagreement"],
                    },
                )
            )
        if state["ood_risk"] > 0.12:
            issues.append(
                QualityIssue(
                    sensor="soft_state",
                    issue_type="soft_sensor_ood_risk",
                    severity=Severity.WARNING,
                    message="当前传感特征存在训练域外风险，应优先触发旁路验证或人工复核。",
                    evidence={"ood_risk": state["ood_risk"]},
                )
            )
        return issues

    def _recommend(self, state: dict[str, float]) -> list[str]:
        recommendations: list[str] = []
        if state["release_readiness"] >= 0.82:
            recommendations.append("达标概率和传感可信度均较高，可进入候选放行状态。")
        elif state["compliance_probability"] >= 0.82:
            recommendations.append("水质估计达标概率较高，但释放准备度不足，应先进入机理诊断或旁路校准。")
        if state["recycle_gain"] >= 0.28:
            recommendations.append("回流边际收益仍为正，建议继续循环或延长停留后再判断。")
        if state["oxidant_remaining"] < 0.35:
            recommendations.append("估计氧化剂余量偏低，若继续处理应优先评估补加药剂。")
        if state["matrix_interference"] > 0.55:
            recommendations.append("基质干扰偏强，建议多智能体诊断阶段重点检查高盐、高 COD 或浊度扰动。")
        if state["byproduct_risk"] > 0.55:
            recommendations.append("副产物风险偏高，应限制继续氧化剂投加，并优先安排旁路验证或预处理。")
        if state["catalyst_replacement_urgency"] > 0.55:
            recommendations.append("催化剂生命周期风险偏高，应比较再生与更换的长期成本，而不是只看单次出水。")
        elif state["catalyst_regeneration_potential"] >= 0.55 and state["catalyst_activity"] < 0.52:
            recommendations.append("催化剂仍有再生潜力，可优先安排再生后回流验证。")
        if state["offline_validation_confidence"] >= 0.25:
            recommendations.append("已有旁路快检证据，应将其作为软传感校准参考；若快检过期需重新采样。")
        if state["soft_sensor_uncertainty"] > 0.22:
            recommendations.append("软传感不确定性偏高，建议增加离线标签或延长循环窗口后重新估计。")
        if state["ood_risk"] > 0.12:
            recommendations.append("检测到训练域外风险，建议把该批次纳入 field holdout/OOD 审计数据。")
        if state["sensor_confidence"] < 0.75:
            recommendations.append("传感可信度不足，建议旁路快检或离线校准后再执行自动放行。")
        return recommendations or ["状态估计稳定，可交给机理解释 Agent 做下一步诊断。"]

    def _validate_against_synthetic_truth(
        self,
        readings: Sequence[SensorReading],
        state: dict[str, float],
    ) -> dict[str, float]:
        truth = readings[-1].ground_truth_state if readings and readings[-1].ground_truth_state else {}
        mapping = {
            "pollutant_residual_risk": "pollutant_residual_risk",
            "reaction_completion": "reaction_completion",
            "oxidant_remaining": "oxidant_remaining",
            "catalyst_activity": "catalyst_activity",
            "catalyst_lifetime_fraction": "catalyst_lifetime_fraction",
            "matrix_interference": "matrix_interference",
        }
        errors: dict[str, float] = {}
        for estimate_key, truth_key in mapping.items():
            if truth_key in truth:
                errors[f"{estimate_key}_abs_error"] = round(abs(float(state[estimate_key]) - float(truth[truth_key])), 4)
        return errors

    @staticmethod
    def _clip(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
        return max(lo, min(hi, value))

    @staticmethod
    def _norm(value: float, lo: float, hi: float) -> float:
        if hi == lo:
            return 0.0
        return max(0.0, min(1.0, (value - lo) / (hi - lo)))

    @staticmethod
    def _safe_ratio(num: float, den: float) -> float:
        if abs(den) < 1e-9:
            return 0.0
        return max(0.0, min(1.0, num / den))
