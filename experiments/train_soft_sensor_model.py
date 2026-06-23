from __future__ import annotations

import json
import random
from dataclasses import replace
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputRegressor

from water_ai.agents.sensor_network_sparse_placement_agent import SensorNetworkSparsePlacementAgent
from water_ai.process_dynamics import ProcessState, generate_sensor_stream_from_process_state, initial_process_state
from water_ai.simulation import generate_low_cost_sensor_stream
from water_ai.soft_sensor_model import (
    FEATURE_COLUMNS,
    HYDRAULIC_PATH_FEATURE_COLUMNS,
    TARGET_COLUMNS,
    readings_to_training_frame,
    save_soft_sensor_model,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "outputs" / "soft_sensor_training"
MODEL_PATH = PROJECT_ROOT / "models" / "soft_sensor_calibrator.pkl"
SCENARIOS = [
    "clean_release",
    "sensor_faults",
    "oxidant_limitation",
    "reaction_time_insufficient",
    "catalyst_deactivation",
    "matrix_shock",
]

LAYOUT_VARIANT_SPECS = [
    {
        "variant_id": "low_cost_stage_gap",
        "placement_strategy": "greedy_marginal",
        "max_sensors": 4,
        "budget_limit": 3.2,
        "holdout_role": "train",
    },
    {
        "variant_id": "default_proxy_release",
        "placement_strategy": "greedy_marginal",
        "max_sensors": 6,
        "budget_limit": 5.8,
        "holdout_role": "train",
    },
    {
        "variant_id": "direct_effluent_full_budget",
        "placement_strategy": "greedy_marginal",
        "max_sensors": 8,
        "budget_limit": 7.0,
        "holdout_role": "holdout",
    },
    {
        "variant_id": "cost_only_effluent",
        "placement_strategy": "cost_only_baseline",
        "max_sensors": 4,
        "budget_limit": 3.2,
        "holdout_role": "train",
    },
    {
        "variant_id": "random_direct_release",
        "placement_strategy": "deterministic_random_baseline",
        "max_sensors": 5,
        "budget_limit": 4.2,
        "holdout_role": "train",
    },
    {
        "variant_id": "classification_proxy_release_gap",
        "placement_strategy": "classification_sspoc_proxy",
        "max_sensors": 5,
        "budget_limit": 4.2,
        "holdout_role": "holdout",
    },
    {
        "variant_id": "topology_robust_release_direct",
        "placement_strategy": "topology_robust_cost_proxy",
        "max_sensors": 4,
        "budget_limit": 3.2,
        "holdout_role": "train",
    },
]


def build_dataset() -> pd.DataFrame:
    frames = []
    layout_interfaces = build_layout_interfaces()
    for scenario in SCENARIOS:
        for seed in range(40):
            sensor_layout_interface = select_layout_interface(
                layout_interfaces,
                scenario=scenario,
                seed=seed,
                source="legacy_scenario",
                window_min=72,
            )
            readings = generate_low_cost_sensor_stream(
                n=72,
                seed=seed,
                inject_faults=scenario == "sensor_faults",
                scenario=scenario,
            )
            frame = readings_to_training_frame(
                readings,
                scenario=scenario,
                seed=seed,
                sensor_layout_interface=sensor_layout_interface,
            )
            _attach_layout_metadata(frame, sensor_layout_interface)
            frame["source"] = "legacy_scenario"
            frame["window_min"] = 72
            frames.append(frame)

    for scenario in SCENARIOS:
        for seed in range(40):
            state = _jitter_process_state(initial_process_state(scenario), seed=seed)
            for window_min in (24, 48, 72):
                sensor_layout_interface = select_layout_interface(
                    layout_interfaces,
                    scenario=scenario,
                    seed=seed,
                    source="process_dynamics",
                    window_min=window_min,
                )
                readings = generate_sensor_stream_from_process_state(state, n=window_min, seed=seed)
                frame = readings_to_training_frame(
                    readings,
                    scenario=scenario,
                    seed=seed,
                    sensor_layout_interface=sensor_layout_interface,
                )
                _attach_layout_metadata(frame, sensor_layout_interface)
                frame["source"] = "process_dynamics"
                frame["window_min"] = window_min
                frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def build_layout_interfaces() -> list[dict[str, object]]:
    interfaces: list[dict[str, object]] = []
    seen_layout_ids: set[str] = set()
    for spec in LAYOUT_VARIANT_SPECS:
        report = SensorNetworkSparsePlacementAgent(
            max_sensors=int(spec["max_sensors"]),
            budget_limit=float(spec["budget_limit"]),
            placement_strategy=str(spec["placement_strategy"]),
        ).run([])
        interface = dict(report.metrics["soft_sensor_interface"])
        layout_id = str(interface["layout_id"])
        if layout_id in seen_layout_ids:
            continue
        seen_layout_ids.add(layout_id)
        contract = interface.get("hydraulic_path_contract", {})
        contract = contract if isinstance(contract, dict) else {}
        interface["layout_variant_id"] = str(spec["variant_id"])
        interface["layout_holdout_role"] = str(spec["holdout_role"])
        interface["layout_variant_spec"] = {
            "placement_strategy": str(spec["placement_strategy"]),
            "max_sensors": int(spec["max_sensors"]),
            "budget_limit": float(spec["budget_limit"]),
        }
        interface["layout_variant_summary"] = {
            "covered_stage_count": int(contract.get("covered_stage_count", 0) or 0),
            "directly_covered_stage_count": int(contract.get("directly_covered_stage_count", 0) or 0),
            "proxy_covered_stage_count": int(contract.get("proxy_covered_stage_count", 0) or 0),
            "final_effluent_directly_observed": bool(contract.get("final_effluent_directly_observed", False)),
            "final_release_gate_needs_effluent_label": bool(contract.get("final_release_gate_needs_effluent_label", True)),
        }
        interfaces.append(interface)
    return interfaces


def select_layout_interface(
    layout_interfaces: list[dict[str, object]],
    *,
    scenario: str,
    seed: int,
    source: str,
    window_min: int,
) -> dict[str, object]:
    if not layout_interfaces:
        raise ValueError("at least one layout interface is required")
    scenario_index = SCENARIOS.index(scenario) if scenario in SCENARIOS else 0
    source_offset = 3 if source == "process_dynamics" else 0
    index = (scenario_index * 11 + seed * 5 + window_min + source_offset) % len(layout_interfaces)
    return layout_interfaces[index]


def _attach_layout_metadata(frame: pd.DataFrame, sensor_layout_interface: dict[str, object]) -> None:
    contract = sensor_layout_interface.get("hydraulic_path_contract", {})
    contract = contract if isinstance(contract, dict) else {}
    frame["layout_id"] = str(sensor_layout_interface.get("layout_id", "unknown_layout"))
    frame["layout_variant_id"] = str(sensor_layout_interface.get("layout_variant_id", "unknown_variant"))
    frame["layout_holdout_role"] = str(sensor_layout_interface.get("layout_holdout_role", "train"))
    matrix_shape = sensor_layout_interface.get("matrix_shape", [0])
    frame["selected_sensor_count"] = int(matrix_shape[0]) if isinstance(matrix_shape, list) and matrix_shape else 0
    frame["path_stage_count"] = int(contract.get("path_stage_count", 0) or 0)
    frame["covered_stage_count"] = int(contract.get("covered_stage_count", 0) or 0)


def _jitter_process_state(state: ProcessState, *, seed: int) -> ProcessState:
    label_offset = sum((idx + 1) * ord(ch) for idx, ch in enumerate(state.label))
    rng = random.Random(seed + label_offset)
    return replace(
        state,
        pollutant_load=_clip(state.pollutant_load + rng.uniform(-0.08, 0.08), 0.05, 0.95),
        oxidant_level=_clip(state.oxidant_level + rng.uniform(-0.07, 0.07), 0.04, 0.98),
        catalyst_activity=_clip(state.catalyst_activity + rng.uniform(-0.06, 0.06), 0.35, 0.95),
        matrix_interference=_clip(state.matrix_interference + rng.uniform(-0.08, 0.08), 0.05, 0.95),
        sensor_health=_clip(state.sensor_health + rng.uniform(-0.08, 0.08), 0.25, 1.0),
        hydraulic_efficiency=_clip(state.hydraulic_efficiency + rng.uniform(-0.08, 0.08), 0.25, 0.98),
    )


def _clip(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    dataset = build_dataset()
    dataset.to_csv(OUT_DIR / "soft_sensor_training_data.csv", index=False)

    x = dataset[FEATURE_COLUMNS]
    y = dataset[TARGET_COLUMNS]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=13, shuffle=True)
    model = _soft_sensor_estimator(random_state=13)
    model.fit(x_train, y_train)
    pred = model.predict(x_test)

    mae_by_target = {
        target: round(float(mean_absolute_error(y_test[target], pred[:, idx])), 5)
        for idx, target in enumerate(TARGET_COLUMNS)
    }
    r2_by_target = {
        target: round(float(r2_score(y_test[target], pred[:, idx])), 5)
        for idx, target in enumerate(TARGET_COLUMNS)
    }
    metrics = {
        "model_version": "rf_multioutput_v5_path_layout_holdout",
        "rows": int(len(dataset)),
        "rows_by_source": {str(k): int(v) for k, v in dataset["source"].value_counts().to_dict().items()},
        "rows_by_window_min": {str(k): int(v) for k, v in dataset["window_min"].value_counts().sort_index().to_dict().items()},
        "rows_by_layout_id": {str(k): int(v) for k, v in dataset["layout_id"].value_counts().sort_index().to_dict().items()},
        "rows_by_layout_holdout_role": {
            str(k): int(v) for k, v in dataset["layout_holdout_role"].value_counts().sort_index().to_dict().items()
        },
        "features": FEATURE_COLUMNS,
        "hydraulic_path_features": HYDRAULIC_PATH_FEATURE_COLUMNS,
        "targets": TARGET_COLUMNS,
        "feature_ranges": _feature_ranges(dataset),
        "hydraulic_path_feature_unique_counts": _feature_unique_counts(dataset, HYDRAULIC_PATH_FEATURE_COLUMNS),
        "hydraulic_path_feature_variation_status": _path_feature_variation_status(dataset),
        "layout_variants": _layout_variant_summary(dataset),
        "layout_holdout": _layout_holdout_metrics(dataset),
        "mae_by_target": mae_by_target,
        "r2_by_target": r2_by_target,
        "mean_mae": round(float(sum(mae_by_target.values()) / len(mae_by_target)), 5),
    }

    save_soft_sensor_model(
        MODEL_PATH,
        {
            "model_version": metrics["model_version"],
            "model": model,
            "features": FEATURE_COLUMNS,
            "targets": TARGET_COLUMNS,
            "metrics": metrics,
            "feature_ranges": metrics["feature_ranges"],
        },
    )
    (OUT_DIR / "soft_sensor_training_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# 软传感器校正模型训练报告",
        "",
        f"- model_version: `{metrics['model_version']}`",
        f"- rows: `{metrics['rows']}`",
        f"- layout_variant_count: `{len(metrics['layout_variants'])}`",
        f"- layout_holdout_status: `{metrics['layout_holdout']['status']}`",
        f"- mean_mae: `{metrics['mean_mae']}`",
        f"- layout_holdout_mean_mae: `{metrics['layout_holdout']['mean_mae']}`",
        "",
        "## MAE",
        "",
    ]
    for target, value in mae_by_target.items():
        lines.append(f"- {target}: {value}")
    lines.extend(["", "## R2", ""])
    for target, value in r2_by_target.items():
        lines.append(f"- {target}: {value}")
    lines.extend(["", "## Layout Holdout", ""])
    for target, value in metrics["layout_holdout"]["mae_by_target"].items():
        lines.append(f"- {target}: {value}")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- layout holdout uses synthetic layout variants only; it validates schema and benchmark readiness, not field deployment.",
            "- field path labels, node-specific sensor values and final effluent endpoint labels are still required before release-gate claims.",
        ]
    )
    (OUT_DIR / "soft_sensor_training_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    print(f"saved {MODEL_PATH}")


def _soft_sensor_estimator(*, random_state: int, n_estimators: int = 120) -> MultiOutputRegressor:
    return MultiOutputRegressor(
        RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=14,
            min_samples_leaf=3,
            random_state=random_state,
            n_jobs=-1,
        )
    )


def _layout_holdout_metrics(dataset: pd.DataFrame) -> dict[str, object]:
    holdout_mask = dataset["layout_holdout_role"] == "holdout"
    train = dataset.loc[~holdout_mask]
    holdout = dataset.loc[holdout_mask]
    if train.empty or holdout.empty:
        return {
            "status": "layout_holdout_not_available",
            "train_layout_ids": sorted(str(item) for item in train.get("layout_id", pd.Series(dtype=str)).unique()),
            "holdout_layout_ids": sorted(str(item) for item in holdout.get("layout_id", pd.Series(dtype=str)).unique()),
            "train_rows": int(len(train)),
            "holdout_rows": int(len(holdout)),
            "mae_by_target": {},
            "r2_by_target": {},
            "mean_mae": None,
            "field_boundary": "layout holdout requires at least one train layout and one held-out layout",
        }
    holdout_model = _soft_sensor_estimator(random_state=29, n_estimators=80)
    holdout_model.fit(train[FEATURE_COLUMNS], train[TARGET_COLUMNS])
    pred = holdout_model.predict(holdout[FEATURE_COLUMNS])
    mae_by_target = {
        target: round(float(mean_absolute_error(holdout[target], pred[:, idx])), 5)
        for idx, target in enumerate(TARGET_COLUMNS)
    }
    r2_by_target = {
        target: round(float(r2_score(holdout[target], pred[:, idx])), 5)
        for idx, target in enumerate(TARGET_COLUMNS)
    }
    return {
        "status": "synthetic_layout_holdout_ready_needs_field_path_labels",
        "train_layout_ids": sorted(str(item) for item in train["layout_id"].unique()),
        "holdout_layout_ids": sorted(str(item) for item in holdout["layout_id"].unique()),
        "train_rows": int(len(train)),
        "holdout_rows": int(len(holdout)),
        "mae_by_target": mae_by_target,
        "r2_by_target": r2_by_target,
        "mean_mae": round(float(sum(mae_by_target.values()) / len(mae_by_target)), 5),
        "estimator": "random_forest_multioutput_80_tree_layout_holdout_evaluator",
        "field_boundary": (
            "synthetic layout holdout checks path-feature schema generalization only; it cannot prove field "
            "performance without path labels, node-specific values and endpoint lab labels"
        ),
    }


def _feature_ranges(dataset: pd.DataFrame) -> dict[str, dict[str, float]]:
    return {
        feature: {
            "min": round(float(dataset[feature].min()), 6),
            "max": round(float(dataset[feature].max()), 6),
        }
        for feature in FEATURE_COLUMNS
    }


def _feature_unique_counts(dataset: pd.DataFrame, features: list[str]) -> dict[str, int]:
    return {feature: int(dataset[feature].nunique(dropna=False)) for feature in features}


def _path_feature_variation_status(dataset: pd.DataFrame) -> str:
    unique_counts = _feature_unique_counts(dataset, HYDRAULIC_PATH_FEATURE_COLUMNS)
    varied_features = [feature for feature, count in unique_counts.items() if count > 1]
    if len(varied_features) >= 4:
        return "synthetic_path_feature_variation_ready_for_layout_holdout"
    if varied_features:
        return "synthetic_path_feature_variation_partial"
    return "synthetic_path_features_constant_not_evaluable"


def _layout_variant_summary(dataset: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    group_cols = [
        "layout_id",
        "layout_variant_id",
        "layout_holdout_role",
        "selected_sensor_count",
        "path_stage_count",
        "covered_stage_count",
        *HYDRAULIC_PATH_FEATURE_COLUMNS,
    ]
    for values, group in dataset.groupby(group_cols, dropna=False):
        record = dict(zip(group_cols, values, strict=True))
        record["row_count"] = int(len(group))
        rows.append(record)
    rows.sort(key=lambda item: (str(item["layout_holdout_role"]), str(item["layout_id"])))
    return rows


if __name__ == "__main__":
    main()
