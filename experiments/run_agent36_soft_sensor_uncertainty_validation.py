from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.data_quality_agent import DataQualityAgent
from water_ai.agents.soft_sensor_agent import SoftSensorAgent
from water_ai.agents.soft_sensor_uncertainty_validation_agent import SoftSensorUncertaintyValidationAgent
from water_ai.simulation import generate_low_cost_sensor_stream
from water_ai.soft_sensor_model import TARGET_COLUMNS


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent36_soft_sensor_uncertainty_validation"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables"
UNCERTAINTY_METRICS_PATH = PROJECT_ROOT / "outputs" / "soft_sensor_training" / "soft_sensor_uncertainty_metrics.json"
SCENARIOS = [
    "clean_release",
    "sensor_faults",
    "oxidant_limitation",
    "reaction_time_insufficient",
    "catalyst_deactivation",
    "matrix_shock",
]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    validation_records = _validation_records()
    report = SoftSensorUncertaintyValidationAgent(
        validation_records=validation_records,
        evidence_stage="synthetic_holdout",
    ).run([])
    generated_files = {
        "soft_sensor_uncertainty_validation": str(DELIVERABLES_DIR / "soft_sensor_uncertainty_validation.md"),
        "agent36_report": str(OUT_DIR / "agent36_report.md"),
        "uncertainty_metrics": str(UNCERTAINTY_METRICS_PATH),
    }

    (DELIVERABLES_DIR / "soft_sensor_uncertainty_validation.md").write_text(_validation_md(report), encoding="utf-8")
    UNCERTAINTY_METRICS_PATH.write_text(
        json.dumps(
            {
                "evidence_stage": "synthetic_holdout",
                "uncertainty_metrics": report.metrics["aggregate"],
                "readiness": report.metrics["readiness"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    payload = {
        "soft_sensor_uncertainty_validation": {
            "agent_name": report.agent_name,
            "confidence": report.confidence,
            "summary": report.summary,
            "recommendations": report.recommendations,
            "metrics": report.metrics,
            "issues": [
                {
                    "sensor": issue.sensor,
                    "issue_type": issue.issue_type,
                    "severity": issue.severity.value,
                    "message": issue.message,
                    "evidence": issue.evidence,
                }
                for issue in report.issues
            ],
        },
        "generated_files": generated_files,
    }
    (OUT_DIR / "agent36_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "agent36_report.md").write_text(_report_md(report, generated_files), encoding="utf-8")
    _update_manifest(generated_files)

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent36_report.md'}")
    for key, path in generated_files.items():
        print(f"{key}: {path}")


def _validation_records() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for scenario in SCENARIOS:
        for seed in range(8):
            readings = generate_low_cost_sensor_stream(
                n=72,
                seed=seed,
                inject_faults=scenario == "sensor_faults",
                scenario=scenario,
            )
            dq_report = DataQualityAgent().run(readings)
            soft_report = SoftSensorAgent(data_quality_report=dq_report).run(readings)
            state = soft_report.metrics["state_estimate"]
            uncertainty = soft_report.metrics["uncertainty"]
            truth = readings[-1].ground_truth_state
            target_abs_errors: dict[str, float] = {}
            target_interval_coverage: dict[str, bool] = {}
            target_interval_widths: dict[str, float] = {}
            intervals = uncertainty.get("prediction_interval_90", {})
            if not isinstance(intervals, dict):
                intervals = {}
            for target in TARGET_COLUMNS:
                estimate = float(state[target])
                actual = float(truth[target])
                target_abs_errors[target] = round(abs(estimate - actual), 4)
                interval = intervals.get(target)
                if isinstance(interval, list | tuple) and len(interval) == 2:
                    lo, hi = float(interval[0]), float(interval[1])
                    target_interval_coverage[target] = lo <= actual <= hi
                    target_interval_widths[target] = round(max(0.0, hi - lo), 4)
            records.append(
                {
                    "scenario": scenario,
                    "seed": seed,
                    "uncertainty_score": state["soft_sensor_uncertainty"],
                    "ood_risk": state["ood_risk"],
                    "release_readiness": state["release_readiness"],
                    "compliance_probability": state["compliance_probability"],
                    "release_blocked_by_uncertainty": bool(
                        state["release_readiness"] < 0.82 and state["compliance_probability"] >= 0.82
                    ),
                    "target_abs_errors": target_abs_errors,
                    "target_interval_coverage": target_interval_coverage,
                    "target_interval_widths": target_interval_widths,
                }
            )
    return records


def _validation_md(report) -> str:
    aggregate = report.metrics["aggregate"]
    readiness = report.metrics["readiness"]
    lines = [
        "# 软传感不确定性验证",
        "",
        f"- uncertainty_validation_status：`{readiness['uncertainty_validation_status']}`",
        f"- uncertainty_validation_score：`{readiness['uncertainty_validation_score']}`",
        f"- evidence_stage：`{report.metrics['evidence_stage']}`",
        f"- record_count：`{aggregate['record_count']}`",
        f"- overall_interval_coverage：`{aggregate['overall_interval_coverage']}`",
        f"- mean_abs_error：`{aggregate['mean_abs_error']}`",
        f"- mean_interval_width：`{aggregate['mean_interval_width']}`",
        f"- uncertainty_tracks_error：`{aggregate['uncertainty_tracks_error']}`",
        f"- ood_alert_count：`{aggregate['ood_alert_count']}`",
        "",
        "## Target Coverage",
        "",
    ]
    for target, value in aggregate["coverage_by_target"].items():
        lines.append(f"- `{target}`：{value}")
    lines.extend(["", "## 结论", ""])
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    return "\n".join(lines)


def _report_md(report, generated_files: dict[str, str]) -> str:
    readiness = report.metrics["readiness"]
    aggregate = report.metrics["aggregate"]
    lines = [
        "# Agent 36 软传感不确定性验证报告",
        "",
        f"- summary: {report.summary}",
        f"- uncertainty_validation_status: `{readiness['uncertainty_validation_status']}`",
        f"- overall_interval_coverage: `{aggregate['overall_interval_coverage']}`",
        "",
        "## 生成文件",
        "",
    ]
    for key, path in generated_files.items():
        lines.append(f"- {key}: `{path}`")
    lines.extend(["", "## 风险边界", ""])
    for issue in report.issues:
        lines.append(f"- `{issue.issue_type}`：{issue.message}")
    return "\n".join(lines)


def _update_manifest(generated_files: dict[str, str]) -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    relative_generated = {
        key: str(Path(path).relative_to(PROJECT_ROOT))
        for key, path in generated_files.items()
    }
    manifest["status"] = "软传感不确定性层已生成"
    manifest["soft_sensor_uncertainty"] = relative_generated
    manifest["next_stage"] = "用真实 field holdout 校准软传感预测区间，并继续扩展知识图谱证据矩阵"
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
