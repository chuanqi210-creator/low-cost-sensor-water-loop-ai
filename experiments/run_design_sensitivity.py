from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from water_ai.agents.sensitivity_analysis_agent import SensitivityAnalysisAgent
from water_ai.robustness import PROBLEM_SCENARIOS, evaluate_closed_loop_robustness
from water_ai.sensor_economics import compute_sensor_economics


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "outputs" / "design_sensitivity"
CACHE_DIR = OUT_DIR / "cache"
CACHE_VERSION = "design_sensitivity_v6_validation_planning"
MAX_STEPS = 6


DESIGNS = [
    {
        "design_id": "full_24min_1min",
        "description": "完整低成本传感，24 min 观测窗口，每 1 min 采样。",
        "observation_window_min": 24,
        "sampling_interval_min": 1,
        "disabled_sensors": [],
        "sensor_noise_multiplier": 0.55,
    },
    {
        "design_id": "full_36min_3min",
        "description": "完整低成本传感，36 min 观测窗口，每 3 min 采样。",
        "observation_window_min": 36,
        "sampling_interval_min": 3,
        "disabled_sensors": [],
        "sensor_noise_multiplier": 0.75,
    },
    {
        "design_id": "no_uv_48min_3min",
        "description": "取消 UV254，依靠更长循环窗口和 ORP/浊度/EC 兜底。",
        "observation_window_min": 48,
        "sampling_interval_min": 3,
        "disabled_sensors": ["UV254_abs"],
        "sensor_noise_multiplier": 0.95,
    },
    {
        "design_id": "core_48min_5min",
        "description": "核心传感配置，取消 UV254 和温度，48 min 观测窗口，每 5 min 采样。",
        "observation_window_min": 48,
        "sampling_interval_min": 5,
        "disabled_sensors": ["UV254_abs", "temp_C"],
        "sensor_noise_multiplier": 1.15,
    },
    {
        "design_id": "minimal_60min_5min",
        "description": "极简配置，取消 UV254、温度和流量，靠循环时间换传感成本。",
        "observation_window_min": 60,
        "sampling_interval_min": 5,
        "disabled_sensors": ["UV254_abs", "temp_C", "flow_Lmin"],
        "sensor_noise_multiplier": 1.35,
    },
]


def evaluate_designs(*, seeds: range = range(10), use_cache: bool = True, force_refresh: bool = False) -> list[dict[str, object]]:
    evaluations: list[dict[str, object]] = []
    seed_values = list(seeds)
    if not seed_values:
        raise ValueError("seeds must contain at least one value")
    for base_design in DESIGNS:
        design = _with_sensor_economics(base_design)
        cache_key = _cache_key(design=design, seeds=seed_values)
        cached_records = None if force_refresh or not use_cache else _read_cache(cache_key)
        if cached_records is not None:
            evaluations.extend(cached_records)
            continue
        result = evaluate_closed_loop_robustness(
            scenarios=PROBLEM_SCENARIOS,
            seeds=range(min(seed_values), max(seed_values) + 1) if _is_contiguous(seed_values) else seed_values,
            max_steps=MAX_STEPS,
            observation_window_min=int(design["observation_window_min"]),
            sampling_interval_min=int(design["sampling_interval_min"]),
            disabled_sensors=set(design["disabled_sensors"]),
            sensor_noise_multiplier=float(design["sensor_noise_multiplier"]),
        )
        records: list[dict[str, object]] = []
        for summary in result["scenario_summaries"]:
            mean_total_elapsed_min = round(
                float(summary["mean_elapsed_min"])
                + float(summary["mean_steps"]) * int(design["observation_window_min"]),
                1,
            )
            record = {
                "design_id": design["design_id"],
                "description": design["description"],
                "disabled_sensors": design["disabled_sensors"],
                "observation_window_min": design["observation_window_min"],
                "sampling_interval_min": design["sampling_interval_min"],
                "sensor_cost_index": design["sensor_cost_index"],
                "sensor_economics": design["sensor_economics"],
                "sensor_noise_multiplier": design["sensor_noise_multiplier"],
                "scenario": summary["scenario"],
                "success_rate": summary["success_rate"],
                "mean_steps": summary["mean_steps"],
                "mean_cost": summary["mean_cost"],
                "mean_energy": summary["mean_energy"],
                "mean_elapsed_min": summary["mean_elapsed_min"],
                "mean_total_elapsed_min": mean_total_elapsed_min,
                "failure_count": len(summary["failures"]),
            }
            evaluations.append(record)
            records.append(record)
        if use_cache:
            _write_cache(cache_key, records)
    return evaluations


def _with_sensor_economics(design: dict[str, object]) -> dict[str, object]:
    economics = compute_sensor_economics(
        disabled_sensors=list(design["disabled_sensors"]),
        sampling_interval_min=int(design["sampling_interval_min"]),
        observation_window_min=int(design["observation_window_min"]),
    )
    return {
        **design,
        "sensor_cost_index": economics["engineering_cost_index"],
        "sensor_economics": economics,
    }


def _cache_key(*, design: dict[str, object], seeds: list[int]) -> str:
    payload = {
        "version": CACHE_VERSION,
        "design_id": design["design_id"],
        "observation_window_min": design["observation_window_min"],
        "sampling_interval_min": design["sampling_interval_min"],
        "disabled_sensors": sorted(design["disabled_sensors"]),
        "sensor_cost_index": design["sensor_cost_index"],
        "sensor_noise_multiplier": design["sensor_noise_multiplier"],
        "scenarios": PROBLEM_SCENARIOS,
        "seeds": seeds,
        "max_steps": MAX_STEPS,
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _read_cache(cache_key: str) -> list[dict[str, object]] | None:
    path = CACHE_DIR / f"{cache_key}.json"
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("version") != CACHE_VERSION:
        return None
    records = payload.get("records")
    if not isinstance(records, list):
        return None
    return [record for record in records if isinstance(record, dict)]


def _write_cache(cache_key: str, records: list[dict[str, object]]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"{cache_key}.json"
    payload = {"version": CACHE_VERSION, "records": records}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _is_contiguous(values: list[int]) -> bool:
    if not values:
        return False
    return values == list(range(min(values), max(values) + 1))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run sensing and loop-window design sensitivity analysis.")
    parser.add_argument("--force-refresh", action="store_true", help="Recompute all closed-loop evaluations and replace cache entries.")
    parser.add_argument("--no-cache", action="store_true", help="Disable cache reads and writes for this run.")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    evaluations = evaluate_designs(use_cache=not args.no_cache, force_refresh=args.force_refresh)
    report = SensitivityAnalysisAgent(evaluations=evaluations).run([])
    payload = {
        "designs": [_with_sensor_economics(design) for design in DESIGNS],
        "report": {
            "summary": report.summary,
            "confidence": report.confidence,
            "recommendations": report.recommendations,
            "issues": [issue.__dict__ for issue in report.issues],
            "metrics": report.metrics,
        },
    }
    (OUT_DIR / "design_sensitivity.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# 低成本传感-循环窗口敏感性分析",
        "",
        report.summary,
        "",
        "## 推荐",
        "",
    ]
    lines.extend(f"- {item}" for item in report.recommendations)
    lines.extend(["", "## 设计排序", ""])
    for item in report.metrics["ranked_designs"]:
        lines.extend(
            [
                f"### {item['design_id']}",
                "",
                f"- utility_score: `{item['utility_score']}`",
                f"- mean_success_rate: `{item['mean_success_rate']}`",
                f"- worst_success_rate: `{item['worst_success_rate']}`",
                f"- mean_total_elapsed_min: `{item['mean_total_elapsed_min']}`",
                f"- mean_cost: `{item['mean_cost']}`",
                f"- mean_energy: `{item['mean_energy']}`",
                f"- sensor_cost_index: `{item['sensor_cost_index']}`",
                f"- sensor_noise_multiplier: `{item['sensor_noise_multiplier']}`",
                f"- purchase_cost_cny: `{item['purchase_cost_cny']}`",
                f"- annual_maintenance_cny: `{item['annual_maintenance_cny']}`",
                f"- calibration_hours_per_month: `{item['calibration_hours_per_month']}`",
                f"- sampling_load_index: `{item['sampling_load_index']}`",
                f"- disabled_sensors: `{item['disabled_sensors']}`",
                "",
            ]
        )
    (OUT_DIR / "design_sensitivity.md").write_text("\n".join(lines), encoding="utf-8")
    print(report.summary)
    for item in report.metrics["ranked_designs"]:
        print(
            f"{item['design_id']}: score={item['utility_score']} success={item['mean_success_rate']} "
            f"elapsed={item['mean_total_elapsed_min']} sensor_cost={item['sensor_cost_index']}"
        )


if __name__ == "__main__":
    main()
