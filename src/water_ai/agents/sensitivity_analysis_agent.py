from __future__ import annotations

from collections.abc import Sequence
from statistics import mean

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class SensitivityAnalysisAgent(BaseAgent):
    """Rank sensing and loop-window designs by robustness, cost, and delay."""

    name = "sensitivity_analysis_agent"

    def __init__(self, *, evaluations: list[dict[str, object]]) -> None:
        self.evaluations = evaluations

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        if not self.evaluations:
            return AgentReport(
                agent_name=self.name,
                confidence=0.0,
                summary="没有敏感性评估结果，无法排序设计方案。",
                issues=[
                    QualityIssue(
                        sensor="design",
                        issue_type="empty_design_evaluation",
                        severity=Severity.CRITICAL,
                        message="设计敏感性 Agent 未收到任何候选方案评估结果。",
                    )
                ],
                recommendations=["先运行多场景设计扫查，再进行低成本传感方案排序。"],
                metrics={"ranked_designs": []},
            )

        design_summaries = self._summarize_designs(self.evaluations)
        ranked = self._rank_designs(design_summaries)
        issues = self._issues(ranked)
        recommendations = self._recommend(ranked)
        top = ranked[0]
        confidence = round(max(0.1, min(0.95, mean(float(item["mean_success_rate"]) for item in ranked[:3]))), 3)

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=f"推荐设计：{top['design_id']}，综合评分 {top['utility_score']}，平均成功率 {top['mean_success_rate']}。",
            issues=issues,
            recommendations=recommendations,
            metrics={
                "ranked_designs": ranked,
                "evaluations": self.evaluations,
            },
        )

    def _summarize_designs(self, evaluations: list[dict[str, object]]) -> list[dict[str, object]]:
        design_ids = sorted({str(item["design_id"]) for item in evaluations})
        summaries: list[dict[str, object]] = []
        for design_id in design_ids:
            items = [item for item in evaluations if str(item["design_id"]) == design_id]
            first = items[0]
            sensor_economics = first.get("sensor_economics", {})
            if not isinstance(sensor_economics, dict):
                sensor_economics = {}
            summaries.append(
                {
                    "design_id": design_id,
                    "description": str(first.get("description", design_id)),
                    "disabled_sensors": list(first.get("disabled_sensors", [])),
                    "observation_window_min": int(first.get("observation_window_min", 24)),
                    "sampling_interval_min": int(first.get("sampling_interval_min", 1)),
                    "sensor_noise_multiplier": round(float(first.get("sensor_noise_multiplier", 0.0)), 3),
                    "sensor_cost_index": round(float(first.get("sensor_cost_index", sensor_economics.get("engineering_cost_index", 1.0))), 3),
                    "sensor_economics": sensor_economics,
                    "purchase_cost_cny": round(float(sensor_economics.get("purchase_cost_cny", 0.0)), 1),
                    "annual_maintenance_cny": round(float(sensor_economics.get("annual_maintenance_cny", 0.0)), 1),
                    "calibration_hours_per_month": round(float(sensor_economics.get("calibration_hours_per_month", 0.0)), 2),
                    "sampling_load_index": round(float(sensor_economics.get("sampling_load_index", 0.0)), 3),
                    "mean_success_rate": round(mean(float(item["success_rate"]) for item in items), 3),
                    "worst_success_rate": round(min(float(item["success_rate"]) for item in items), 3),
                    "mean_steps": round(mean(float(item["mean_steps"]) for item in items), 3),
                    "mean_total_elapsed_min": round(mean(float(item["mean_total_elapsed_min"]) for item in items), 1),
                    "mean_cost": round(mean(float(item["mean_cost"]) for item in items), 3),
                    "mean_energy": round(mean(float(item["mean_energy"]) for item in items), 3),
                    "scenario_results": items,
                }
            )
        return summaries

    def _rank_designs(self, summaries: list[dict[str, object]]) -> list[dict[str, object]]:
        elapsed_values = [float(item["mean_total_elapsed_min"]) for item in summaries]
        cost_values = [float(item["mean_cost"]) for item in summaries]
        energy_values = [float(item["mean_energy"]) for item in summaries]
        sensor_cost_values = [float(item["sensor_cost_index"]) for item in summaries]

        ranked: list[dict[str, object]] = []
        for item in summaries:
            success = float(item["mean_success_rate"])
            elapsed_score = 1.0 - _normalize(float(item["mean_total_elapsed_min"]), elapsed_values)
            cost_score = 1.0 - _normalize(float(item["mean_cost"]), cost_values)
            energy_score = 1.0 - _normalize(float(item["mean_energy"]), energy_values)
            sensor_cost_score = 1.0 - _normalize(float(item["sensor_cost_index"]), sensor_cost_values)
            stability_penalty = max(0.0, 0.98 - float(item["worst_success_rate"])) * 1.2
            utility = _clip(
                0.42 * success
                + 0.20 * elapsed_score
                + 0.14 * cost_score
                + 0.10 * energy_score
                + 0.14 * sensor_cost_score
                - stability_penalty
            )
            ranked.append(
                {
                    **item,
                    "utility_score": round(utility, 3),
                    "elapsed_score": round(elapsed_score, 3),
                    "cost_score": round(cost_score, 3),
                    "energy_score": round(energy_score, 3),
                    "sensor_cost_score": round(sensor_cost_score, 3),
                    "stability_penalty": round(stability_penalty, 3),
                }
            )
        ranked.sort(key=lambda item: float(item["utility_score"]), reverse=True)
        return ranked

    def _issues(self, ranked: list[dict[str, object]]) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        for item in ranked:
            if float(item["worst_success_rate"]) < 0.95:
                issues.append(
                    QualityIssue(
                        sensor="design",
                        issue_type="unstable_design",
                        severity=Severity.WARNING,
                        message=f"{item['design_id']} 在至少一个场景中成功率偏低。",
                        evidence={"worst_success_rate": item["worst_success_rate"], "scenario_results": item["scenario_results"]},
                    )
                )
            if float(item["mean_total_elapsed_min"]) > 220:
                issues.append(
                    QualityIssue(
                        sensor="design",
                        issue_type="slow_design",
                        severity=Severity.WARNING,
                        message=f"{item['design_id']} 平均总耗时偏高，不适合作为默认低成本方案。",
                        evidence={"mean_total_elapsed_min": item["mean_total_elapsed_min"]},
                    )
                )
            if float(item.get("calibration_hours_per_month", 0.0)) > 12:
                issues.append(
                    QualityIssue(
                        sensor="design",
                        issue_type="maintenance_heavy_design",
                        severity=Severity.INFO,
                        message=f"{item['design_id']} 月校准维护工时偏高，应确认现场运维能力。",
                        evidence={
                            "calibration_hours_per_month": item["calibration_hours_per_month"],
                            "annual_maintenance_cny": item["annual_maintenance_cny"],
                        },
                    )
                )
        return issues

    def _recommend(self, ranked: list[dict[str, object]]) -> list[str]:
        top = ranked[0]
        fallback = next((item for item in ranked if float(item["worst_success_rate"]) >= 0.95 and item is not top), None)
        recommendations = [
            (
                f"默认采用 {top['design_id']}：观测窗口 {top['observation_window_min']} min，"
                f"采样间隔 {top['sampling_interval_min']} min，噪声倍率 {top['sensor_noise_multiplier']}，"
                f"禁用传感器 {top['disabled_sensors']}，"
                f"工程成本指数 {top['sensor_cost_index']}，月校准 {top['calibration_hours_per_month']} h，"
                f"平均总耗时 {top['mean_total_elapsed_min']} min。"
            )
        ]
        if fallback is not None:
            recommendations.append(
                f"若现场更看重冗余，可保留 {fallback['design_id']} 作为稳健备选，综合评分 {fallback['utility_score']}。"
            )
        recommendations.append("任何低成本配置都不应绕过最终放行安全门；节省传感成本只能通过循环窗口和旁路验证换取。")
        return recommendations


def _normalize(value: float, values: list[float]) -> float:
    lo = min(values)
    hi = max(values)
    if abs(hi - lo) < 1e-9:
        return 0.0
    return _clip((value - lo) / (hi - lo))


def _clip(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))
