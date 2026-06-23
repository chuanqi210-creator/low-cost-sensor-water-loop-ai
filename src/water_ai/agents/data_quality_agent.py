from __future__ import annotations

from collections.abc import Sequence
from statistics import median

from water_ai.agents.base import BaseAgent
from water_ai.domain import (
    AgentReport,
    FLATLINE_EPS,
    QualityIssue,
    RATE_LIMITS,
    SENSOR_RANGES,
    SensorReading,
    Severity,
)


class DataQualityAgent(BaseAgent):
    """Detect low-cost sensor quality problems before downstream reasoning."""

    name = "data_quality_agent"

    def __init__(self, *, flatline_window: int = 6, drift_window: int = 12) -> None:
        self.flatline_window = flatline_window
        self.drift_window = drift_window

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        issues: list[QualityIssue] = []
        if not readings:
            return AgentReport(
                agent_name=self.name,
                confidence=0.0,
                summary="没有传感数据，无法进行质控。",
                issues=[
                    QualityIssue(
                        sensor="all",
                        issue_type="empty_stream",
                        severity=Severity.CRITICAL,
                        message="输入数据为空。",
                    )
                ],
                recommendations=["暂停放行，检查数据采集链路。"],
                metrics={"readings": 0, "issue_count": 1},
            )

        sensors = list(SENSOR_RANGES)
        missing_count = 0
        total_expected = len(readings) * len(sensors)

        previous_values: dict[str, tuple[int, float]] = {}
        history: dict[str, list[tuple[int, float]]] = {sensor: [] for sensor in sensors}

        for reading in readings:
            for sensor in sensors:
                value = reading.values.get(sensor)
                if value is None:
                    missing_count += 1
                    issues.append(
                        QualityIssue(
                            sensor=sensor,
                            issue_type="missing",
                            severity=Severity.WARNING,
                            message=f"{sensor} 在 {reading.timestamp_min} min 缺失。",
                            timestamp_min=reading.timestamp_min,
                        )
                    )
                    continue

                lo, hi = SENSOR_RANGES[sensor]
                if value < lo or value > hi:
                    issues.append(
                        QualityIssue(
                            sensor=sensor,
                            issue_type="out_of_range",
                            severity=Severity.CRITICAL,
                            message=f"{sensor}={value} 超出工程合理范围 [{lo}, {hi}]。",
                            timestamp_min=reading.timestamp_min,
                            evidence={"value": value, "min": lo, "max": hi},
                        )
                    )

                previous = previous_values.get(sensor)
                if previous is not None:
                    prev_t, prev_v = previous
                    dt = max(1, reading.timestamp_min - prev_t)
                    rate = abs(value - prev_v) / dt
                    if rate > RATE_LIMITS[sensor]:
                        issues.append(
                            QualityIssue(
                                sensor=sensor,
                                issue_type="spike",
                                severity=Severity.WARNING,
                                message=f"{sensor} 在 {reading.timestamp_min} min 出现突变，变化率 {rate:.3g}/min。",
                                timestamp_min=reading.timestamp_min,
                                evidence={"previous": prev_v, "current": value, "rate": rate},
                            )
                        )

                history[sensor].append((reading.timestamp_min, float(value)))
                previous_values[sensor] = (reading.timestamp_min, float(value))

        issues.extend(self._detect_flatlines(history))
        issues.extend(self._detect_drift(history))
        issues.extend(self._detect_absolute_low_flow(history))
        issues.extend(self._detect_sustained_shifts(history))

        critical_count = sum(1 for issue in issues if issue.severity == Severity.CRITICAL)
        warning_count = sum(1 for issue in issues if issue.severity == Severity.WARNING)
        issue_penalty = min(0.85, 0.08 * critical_count + 0.025 * warning_count)
        missing_penalty = min(0.35, missing_count / max(1, total_expected) * 3)
        confidence = max(0.05, round(1.0 - issue_penalty - missing_penalty, 3))

        recommendations = self._recommend(issues, confidence)
        summary = self._summarize(issues, confidence)
        sensor_scores = self._sensor_scores(issues)
        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "readings": len(readings),
                "sensor_count": len(sensors),
                "missing_count": missing_count,
                "issue_count": len(issues),
                "critical_count": critical_count,
                "warning_count": warning_count,
                "confidence": confidence,
                "sensor_scores": sensor_scores,
            },
        )

    def _detect_flatlines(self, history: dict[str, list[tuple[int, float]]]) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        for sensor, series in history.items():
            if len(series) < self.flatline_window:
                continue
            eps = FLATLINE_EPS[sensor]
            for i in range(self.flatline_window - 1, len(series)):
                window = series[i - self.flatline_window + 1 : i + 1]
                values = [v for _, v in window]
                if max(values) - min(values) <= eps:
                    issues.append(
                        QualityIssue(
                            sensor=sensor,
                            issue_type="flatline",
                            severity=Severity.WARNING,
                            message=f"{sensor} 在 {window[0][0]}-{window[-1][0]} min 近似卡死。",
                            timestamp_min=window[-1][0],
                            evidence={"window": [window[0][0], window[-1][0]], "range": max(values) - min(values)},
                        )
                    )
                    break
        return issues

    def _detect_drift(self, history: dict[str, list[tuple[int, float]]]) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        for sensor, series in history.items():
            if len(series) < self.drift_window * 2:
                continue
            first = [v for _, v in series[: self.drift_window]]
            last = [v for _, v in series[-self.drift_window :]]
            first_med = median(first)
            last_med = median(last)
            delta = last_med - first_med

            if sensor == "turbidity_NTU":
                # In the current simulator turbidity should decay during treatment.
                # Compare both whole-run medians and local recent windows: a late
                # upward trend can be hidden if the run started very turbid.
                previous = [v for _, v in series[-self.drift_window * 2 : -self.drift_window]]
                previous_med = median(previous)
                local_delta = last_med - previous_med
                if delta > 7.0 or local_delta > 4.0:
                    issues.append(
                        QualityIssue(
                            sensor=sensor,
                            issue_type="drift_suspected",
                            severity=Severity.WARNING,
                            message="浊度后段中位数明显高于前段，疑似传感漂移或新扰动进入系统。",
                            evidence={
                                "first_median": first_med,
                                "previous_window_median": previous_med,
                                "last_median": last_med,
                                "whole_run_delta": delta,
                                "local_delta": local_delta,
                                "expected": "decrease",
                            },
                        )
                    )
            elif sensor == "temp_C" and abs(delta) > 5.0:
                issues.append(
                    QualityIssue(
                        sensor=sensor,
                        issue_type="drift_suspected",
                        severity=Severity.WARNING,
                        message="温度长期漂移超过 5 摄氏度，需核查传感器或环境负荷。",
                        evidence={"first_median": first_med, "last_median": last_med, "delta": delta},
                    )
                )
        return issues

    def _detect_sustained_shifts(self, history: dict[str, list[tuple[int, float]]]) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        for sensor, series in history.items():
            if len(series) < self.flatline_window * 2:
                continue
            if sensor != "flow_Lmin":
                continue

            baseline_values = [v for _, v in series[: self.drift_window]]
            baseline = median(baseline_values)
            if baseline <= 0:
                continue

            for i in range(self.flatline_window - 1, len(series)):
                window = series[i - self.flatline_window + 1 : i + 1]
                values = [v for _, v in window]
                window_med = median(values)
                if window_med < baseline * 0.45:
                    issues.append(
                        QualityIssue(
                            sensor=sensor,
                            issue_type="sustained_shift",
                            severity=Severity.WARNING,
                            message=f"{sensor} 在 {window[0][0]}-{window[-1][0]} min 持续低于基线，疑似泵阀异常或管路堵塞。",
                            timestamp_min=window[-1][0],
                            evidence={"baseline_median": baseline, "window_median": window_med, "window": [window[0][0], window[-1][0]]},
                        )
                    )
                    break
        return issues

    def _detect_absolute_low_flow(self, history: dict[str, list[tuple[int, float]]]) -> list[QualityIssue]:
        series = history.get("flow_Lmin", [])
        if len(series) < self.drift_window:
            return []

        values = [v for _, v in series]
        flow_median = median(values)
        if flow_median >= 0.75:
            return []

        return [
            QualityIssue(
                sensor="flow_Lmin",
                issue_type="low_flow_absolute",
                severity=Severity.WARNING,
                message="短窗口平均流量偏低，疑似泵阀开度、回流支路或停留时间异常。",
                timestamp_min=series[-1][0],
                evidence={"median_flow": flow_median, "threshold": 0.75, "window": [series[0][0], series[-1][0]]},
            )
        ]

    def _recommend(self, issues: list[QualityIssue], confidence: float) -> list[str]:
        issue_types = {issue.issue_type for issue in issues}
        sensors = {issue.sensor for issue in issues}
        recommendations: list[str] = []

        if "missing" in issue_types:
            recommendations.append("检查数据采集链路；缺失窗口内禁止直接放行高风险水样。")
        if "out_of_range" in issue_types or "spike" in issue_types:
            recommendations.append("触发旁路复测或离线快检，避免异常尖峰直接驱动加药/回流决策。")
        if "flatline" in issue_types:
            recommendations.append("对卡死传感器进行清洗、校准或更换；下游软传感器降低该通道权重。")
        if "drift_suspected" in issue_types:
            recommendations.append("将疑似漂移通道标记为低可信，并增加最近一次离线真值校准。")
        if "sustained_shift" in issue_types:
            recommendations.append("持续偏移通道需要结合设备状态解释；控制器应暂停使用该通道做精细投加判断。")
        if "low_flow_absolute" in issue_types:
            recommendations.append("短窗口低流量应触发泵阀、回流管路和实际 HRT 核查。")
        if "flow_Lmin" in sensors:
            recommendations.append("核查泵阀状态；低流量可能改变实际停留时间和回流收益。")
        if confidence < 0.65:
            recommendations.append("整体传感可信度不足，建议暂存待检，不进入自动达标放行。")

        return recommendations or ["传感数据质量可接受，可进入软传感器状态估计。"]

    def _sensor_scores(self, issues: list[QualityIssue]) -> dict[str, float]:
        scores = {sensor: 1.0 for sensor in SENSOR_RANGES}
        penalties = {
            "missing": 0.18,
            "out_of_range": 0.45,
            "spike": 0.14,
            "flatline": 0.35,
            "drift_suspected": 0.32,
            "sustained_shift": 0.28,
            "low_flow_absolute": 0.25,
        }
        for issue in issues:
            if issue.sensor not in scores:
                continue
            scores[issue.sensor] -= penalties.get(issue.issue_type, 0.1)
            if issue.severity == Severity.CRITICAL:
                scores[issue.sensor] -= 0.15
        return {sensor: round(max(0.05, min(1.0, score)), 3) for sensor, score in scores.items()}

    def _summarize(self, issues: list[QualityIssue], confidence: float) -> str:
        if not issues:
            return "未发现明显传感质量问题，可进入后续软测量。"
        critical_count = sum(1 for issue in issues if issue.severity == Severity.CRITICAL)
        warning_count = sum(1 for issue in issues if issue.severity == Severity.WARNING)
        return f"发现 {critical_count} 个严重问题、{warning_count} 个警告；传感可信度评分 {confidence:.2f}。"
