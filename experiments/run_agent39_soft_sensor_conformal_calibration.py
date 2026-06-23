from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.soft_sensor_conformal_calibration_agent import SoftSensorConformalCalibrationAgent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
AGENT36_REPORT = PROJECT_ROOT / "outputs" / "agent36_soft_sensor_uncertainty_validation" / "agent36_report.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent39_soft_sensor_conformal_calibration"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables"
CONFORMAL_METRICS_PATH = PROJECT_ROOT / "outputs" / "soft_sensor_training" / "soft_sensor_conformal_metrics.json"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    validation_records = _read_validation_records()
    report = SoftSensorConformalCalibrationAgent(
        validation_records=validation_records,
        evidence_stage="synthetic_holdout",
        alpha=0.10,
    ).run([])
    generated_files = {
        "soft_sensor_conformal_calibration": str(DELIVERABLES_DIR / "soft_sensor_conformal_calibration.md"),
        "agent39_report": str(OUT_DIR / "agent39_report.md"),
        "conformal_metrics": str(CONFORMAL_METRICS_PATH),
    }

    (DELIVERABLES_DIR / "soft_sensor_conformal_calibration.md").write_text(_calibration_md(report), encoding="utf-8")
    CONFORMAL_METRICS_PATH.write_text(
        json.dumps(
            {
                "evidence_stage": "synthetic_holdout",
                "alpha": report.metrics["alpha"],
                "split": report.metrics["split"],
                "conformal": report.metrics["conformal"],
                "readiness": report.metrics["readiness"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    payload = {
        "soft_sensor_conformal_calibration": {
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
    (OUT_DIR / "agent39_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "agent39_report.md").write_text(_report_md(report, generated_files), encoding="utf-8")
    _update_manifest(generated_files)

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent39_report.md'}")
    for key, path in generated_files.items():
        print(f"{key}: {path}")


def _read_validation_records() -> list[dict[str, object]]:
    if not AGENT36_REPORT.exists():
        return []
    payload = json.loads(AGENT36_REPORT.read_text(encoding="utf-8"))
    section = payload.get("soft_sensor_uncertainty_validation", {})
    if not isinstance(section, dict):
        return []
    metrics = section.get("metrics", {})
    if not isinstance(metrics, dict):
        return []
    records = metrics.get("validation_records", [])
    return records if isinstance(records, list) else []


def _calibration_md(report) -> str:
    conformal = report.metrics["conformal"]
    readiness = report.metrics["readiness"]
    split = report.metrics["split"]
    lines = [
        "# 软传感保形校准",
        "",
        f"- conformal_status：`{readiness['conformal_status']}`",
        f"- conformal_score：`{readiness['conformal_score']}`",
        f"- evidence_stage：`{report.metrics['evidence_stage']}`",
        f"- alpha：`{report.metrics['alpha']}`",
        f"- calibration_count：`{split['calibration_count']}`",
        f"- evaluation_count：`{split['evaluation_count']}`",
        f"- target_coverage_level：`{conformal['target_coverage_level']}`",
        f"- overall_conformal_coverage：`{conformal['overall_conformal_coverage']}`",
        f"- mean_conformal_interval_width：`{conformal['mean_conformal_interval_width']}`",
        f"- release_abstention_rate：`{conformal['release_abstention_rate']}`",
        f"- can_write_to_release_gate：`{readiness['can_write_to_release_gate']}`",
        "",
        "## Target Thresholds",
        "",
    ]
    for target, value in conformal["target_nonconformity_thresholds"].items():
        lines.append(f"- `{target}`：threshold={value}, coverage={conformal['coverage_by_target'][target]}, width={conformal['width_by_target'][target]}")
    lines.extend(["", "## Scenario Full Coverage", ""])
    for scenario, value in conformal["scenario_full_coverage"].items():
        lines.append(f"- `{scenario}`：{value}")
    lines.extend(["", "## 结论", ""])
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    return "\n".join(lines)


def _report_md(report, generated_files: dict[str, str]) -> str:
    readiness = report.metrics["readiness"]
    conformal = report.metrics["conformal"]
    lines = [
        "# Agent 39 软传感保形校准报告",
        "",
        f"- summary: {report.summary}",
        f"- conformal_status: `{readiness['conformal_status']}`",
        f"- overall_conformal_coverage: `{conformal['overall_conformal_coverage']}`",
        f"- can_write_to_release_gate: `{readiness['can_write_to_release_gate']}`",
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
    manifest["status"] = "软传感保形校准接口已生成"
    manifest["soft_sensor_conformal_calibration"] = relative_generated
    manifest["next_stage"] = "用真实 field holdout 重算 conformal thresholds，并接入 release gate 前完成 G0-G5 验收"
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
