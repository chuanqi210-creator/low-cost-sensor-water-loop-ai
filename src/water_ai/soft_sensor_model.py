from __future__ import annotations

import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from water_ai.domain import SENSOR_RANGES, SensorReading


TARGET_COLUMNS = [
    "pollutant_residual_risk",
    "reaction_completion",
    "oxidant_remaining",
    "catalyst_activity",
    "matrix_interference",
]


FEATURE_COLUMNS = [
    "timestamp_min",
    "cycle_id",
    "pH",
    "ORP_mV",
    "EC_uScm",
    "turbidity_NTU",
    "temp_C",
    "flow_Lmin",
    "UV254_abs",
    "uv254_removal",
    "orp_norm",
    "ec_norm",
    "turbidity_norm",
    "ph_penalty",
    "flow_penalty",
]


HYDRAULIC_PATH_FEATURE_COLUMNS = [
    "hydraulic_path_coverage_rate",
    "direct_hydraulic_path_coverage_rate",
    "proxy_hydraulic_path_coverage_rate",
    "recirculation_loop_observed_flag",
    "low_frequency_time_buffer_observed_flag",
    "release_boundary_proxy_flag",
    "final_effluent_direct_observed_flag",
    "release_endpoint_label_missing_flag",
]


FEATURE_COLUMNS = [*FEATURE_COLUMNS, *HYDRAULIC_PATH_FEATURE_COLUMNS]


DEFAULT_HYDRAULIC_PATH_FEATURE_PRIOR = {
    "hydraulic_path_coverage_rate": 1.0,
    "direct_hydraulic_path_coverage_rate": 0.833333,
    "proxy_hydraulic_path_coverage_rate": 0.166667,
    "recirculation_loop_observed_flag": 1.0,
    "low_frequency_time_buffer_observed_flag": 1.0,
    "release_boundary_proxy_flag": 1.0,
    "final_effluent_direct_observed_flag": 0.0,
    "release_endpoint_label_missing_flag": 1.0,
}


@dataclass(frozen=True)
class SoftSensorPrediction:
    state: dict[str, float]
    model_version: str
    model_path: str
    uncertainty: dict[str, Any]


def readings_to_feature_frame(
    readings: list[SensorReading],
    *,
    sensor_layout_interface: dict[str, object] | None = None,
) -> pd.DataFrame:
    rows: list[dict[str, float]] = []
    start_time = int(readings[0].timestamp_min) if readings else 0
    for reading in readings:
        row: dict[str, float] = {
            "timestamp_min": float(int(reading.timestamp_min) - start_time),
            "cycle_id": float(reading.cycle_id),
        }
        for sensor in SENSOR_RANGES:
            value = reading.values.get(sensor)
            row[sensor] = float(value) if value is not None else float("nan")
        rows.append(row)
    frame = pd.DataFrame(rows).sort_values("timestamp_min").reset_index(drop=True)
    for sensor in SENSOR_RANGES:
        lo, hi = SENSOR_RANGES[sensor]
        fallback = (lo + hi) / 2
        frame[sensor] = pd.to_numeric(frame[sensor], errors="coerce")
        frame[sensor] = frame[sensor].interpolate(limit_direction="both").ffill().bfill().fillna(fallback)

    uv_start = max(float(frame.head(min(8, len(frame)))["UV254_abs"].median()), 0.05)
    frame["uv254_removal"] = ((uv_start - frame["UV254_abs"]) / uv_start).clip(0, 1)
    frame["orp_norm"] = ((frame["ORP_mV"] - 200) / 450).clip(0, 1)
    frame["ec_norm"] = ((frame["EC_uScm"] - 500) / 2000).clip(0, 1)
    frame["turbidity_norm"] = (frame["turbidity_NTU"] / 35).clip(0, 1)
    frame["ph_penalty"] = ((frame["pH"] - 7.2).abs() / 2.6).clip(0, 1)
    frame["flow_penalty"] = (1.0 - ((frame["flow_Lmin"] - 0.35) / 0.8).clip(0, 1)).clip(0, 1)
    path_features = hydraulic_path_feature_values(sensor_layout_interface)
    for feature, value in path_features.items():
        frame[feature] = float(value)
    return frame[FEATURE_COLUMNS]


def readings_to_training_frame(
    readings: list[SensorReading],
    *,
    scenario: str,
    seed: int,
    sensor_layout_interface: dict[str, object] | None = None,
) -> pd.DataFrame:
    features = readings_to_feature_frame(readings, sensor_layout_interface=sensor_layout_interface)
    targets: list[dict[str, float]] = []
    for reading in readings:
        row = {target: float(reading.ground_truth_state[target]) for target in TARGET_COLUMNS}
        row["scenario"] = scenario
        row["seed"] = seed
        targets.append(row)
    return pd.concat([features, pd.DataFrame(targets)], axis=1)


def load_soft_sensor_model(model_path: Path) -> Any | None:
    if not model_path.exists():
        return None
    with model_path.open("rb") as f:
        return pickle.load(f)


def save_soft_sensor_model(model_path: Path, payload: Any) -> None:
    model_path.parent.mkdir(parents=True, exist_ok=True)
    with model_path.open("wb") as f:
        pickle.dump(payload, f)


def predict_final_state(
    readings: list[SensorReading],
    model_payload: Any,
    *,
    model_path: Path,
    sensor_layout_interface: dict[str, object] | None = None,
) -> SoftSensorPrediction:
    features = readings_to_feature_frame(readings, sensor_layout_interface=sensor_layout_interface)
    model = model_payload["model"]
    model_features = model_payload.get("features", FEATURE_COLUMNS) if isinstance(model_payload, dict) else FEATURE_COLUMNS
    if not isinstance(model_features, list) or not model_features:
        model_features = FEATURE_COLUMNS
    final_features = features.reindex(columns=[str(feature) for feature in model_features], fill_value=0.0).tail(1)
    prediction = model.predict(final_features)[0]
    state = {target: round(float(max(0.0, min(1.0, value))), 3) for target, value in zip(TARGET_COLUMNS, prediction, strict=True)}
    return SoftSensorPrediction(
        state=state,
        model_version=str(model_payload.get("model_version", "unknown")),
        model_path=str(model_path),
        uncertainty=estimate_prediction_uncertainty(final_features, model_payload),
    )


def estimate_prediction_uncertainty(feature_frame: pd.DataFrame, model_payload: Any) -> dict[str, Any]:
    """Estimate uncertainty from RF tree disagreement and feature-domain checks."""

    model = model_payload.get("model") if isinstance(model_payload, dict) else None
    final_features = feature_frame.tail(1)
    target_uncertainty: dict[str, float] = {}
    prediction_interval_90: dict[str, list[float]] = {}
    tree_prediction_count = 0
    if model is not None and hasattr(model, "estimators_"):
        final_array = final_features.to_numpy()
        for target, estimator in zip(TARGET_COLUMNS, model.estimators_, strict=True):
            trees = getattr(estimator, "estimators_", [])
            if not trees:
                continue
            values = np.array(
                [max(0.0, min(1.0, float(tree.predict(final_array)[0]))) for tree in trees],
                dtype=float,
            )
            tree_prediction_count = max(tree_prediction_count, len(values))
            lo, hi = np.quantile(values, [0.05, 0.95])
            target_uncertainty[target] = round(float(np.std(values)), 4)
            prediction_interval_90[target] = [round(float(lo), 4), round(float(hi), 4)]

    ood = feature_domain_risk(final_features, model_payload)
    interval_widths = [hi - lo for lo, hi in prediction_interval_90.values()]
    mean_interval_width = float(np.mean(interval_widths)) if interval_widths else 0.0
    mean_tree_std = float(np.mean(list(target_uncertainty.values()))) if target_uncertainty else 0.0
    uncertainty_score = max(0.0, min(1.0, 1.8 * mean_tree_std + 0.65 * mean_interval_width + 0.55 * float(ood["ood_risk"])))
    return {
        "method": "rf_tree_disagreement_plus_feature_domain",
        "target_uncertainty": target_uncertainty,
        "prediction_interval_90": prediction_interval_90,
        "mean_interval_width": round(mean_interval_width, 4),
        "mean_tree_std": round(mean_tree_std, 4),
        "tree_prediction_count": tree_prediction_count,
        "ood_risk": ood["ood_risk"],
        "ood_features": ood["ood_features"],
        "uncertainty_score": round(uncertainty_score, 4),
        "evidence_stage": "synthetic_model_internal_uncertainty",
    }


def feature_domain_risk(feature_frame: pd.DataFrame, model_payload: Any) -> dict[str, Any]:
    final = feature_frame.tail(1).iloc[0]
    ranges = {}
    if isinstance(model_payload, dict):
        raw_ranges = model_payload.get("feature_ranges", {})
        if isinstance(raw_ranges, dict):
            ranges = raw_ranges
    if not ranges:
        ranges = default_feature_ranges()

    ood_features: list[dict[str, float | str]] = []
    model_features = model_payload.get("features", FEATURE_COLUMNS) if isinstance(model_payload, dict) else FEATURE_COLUMNS
    if not isinstance(model_features, list) or not model_features:
        model_features = FEATURE_COLUMNS
    checked_features = [str(feature) for feature in model_features]
    for feature in checked_features:
        if feature not in final or feature not in ranges:
            continue
        lo = float(ranges[feature]["min"] if isinstance(ranges[feature], dict) else ranges[feature][0])
        hi = float(ranges[feature]["max"] if isinstance(ranges[feature], dict) else ranges[feature][1])
        value = float(final[feature])
        tolerance = max(1e-9, 0.05 * (hi - lo))
        if value < lo - tolerance or value > hi + tolerance:
            distance = min(abs(value - lo), abs(value - hi)) / max(1e-9, hi - lo)
            ood_features.append({"feature": feature, "value": round(value, 4), "min": round(lo, 4), "max": round(hi, 4), "distance": round(distance, 4)})
    ood_risk = round(
        min(
            1.0,
            len(ood_features) / max(1, len(checked_features))
            + sum(float(item["distance"]) for item in ood_features) / 3,
        ),
        4,
    )
    return {"ood_risk": ood_risk, "ood_features": ood_features}


def default_feature_ranges() -> dict[str, dict[str, float]]:
    ranges = {
        "timestamp_min": {"min": 0.0, "max": 720.0},
        "cycle_id": {"min": 0.0, "max": 16.0},
    }
    for sensor, (lo, hi) in SENSOR_RANGES.items():
        ranges[sensor] = {"min": float(lo), "max": float(hi)}
    for feature in ("uv254_removal", "orp_norm", "ec_norm", "turbidity_norm", "ph_penalty", "flow_penalty"):
        ranges[feature] = {"min": 0.0, "max": 1.0}
    for feature in HYDRAULIC_PATH_FEATURE_COLUMNS:
        ranges[feature] = {"min": 0.0, "max": 1.0}
    return ranges


def hydraulic_path_feature_values(sensor_layout_interface: dict[str, object] | None = None) -> dict[str, float]:
    interface = sensor_layout_interface if isinstance(sensor_layout_interface, dict) else {}
    raw_contract = interface.get("hydraulic_path_contract", {})
    contract = raw_contract if isinstance(raw_contract, dict) else {}
    if not contract:
        return dict(DEFAULT_HYDRAULIC_PATH_FEATURE_PRIOR)
    path_stage_count = int(contract.get("path_stage_count", 0) or 0)
    covered_stage_count = int(contract.get("covered_stage_count", 0) or 0)
    direct_stage_count = int(contract.get("directly_covered_stage_count", 0) or 0)
    proxy_stage_count = int(contract.get("proxy_covered_stage_count", 0) or 0)
    final_release_needs_label = bool(contract.get("final_release_gate_needs_effluent_label", not bool(contract)))
    final_effluent_direct = bool(contract.get("final_effluent_directly_observed", False))
    return {
        "hydraulic_path_coverage_rate": _ratio(covered_stage_count, path_stage_count),
        "direct_hydraulic_path_coverage_rate": _ratio(direct_stage_count, path_stage_count),
        "proxy_hydraulic_path_coverage_rate": _ratio(proxy_stage_count, path_stage_count),
        "recirculation_loop_observed_flag": float(bool(contract.get("recirculation_loop_observed", False))),
        "low_frequency_time_buffer_observed_flag": float(bool(contract.get("low_frequency_time_buffer_observed", False))),
        "release_boundary_proxy_flag": float(final_release_needs_label and not final_effluent_direct),
        "final_effluent_direct_observed_flag": float(final_effluent_direct),
        "release_endpoint_label_missing_flag": float(final_release_needs_label),
    }


def _ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(max(0.0, min(1.0, float(numerator) / float(denominator))), 6)
