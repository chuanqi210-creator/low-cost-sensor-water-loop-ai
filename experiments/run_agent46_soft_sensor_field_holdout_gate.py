from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.soft_sensor_field_holdout_gate_agent import SoftSensorFieldHoldoutGateAgent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
UNCERTAINTY_METRICS_PATH = PROJECT_ROOT / "outputs" / "soft_sensor_training" / "soft_sensor_uncertainty_metrics.json"
CONFORMAL_METRICS_PATH = PROJECT_ROOT / "outputs" / "soft_sensor_training" / "soft_sensor_conformal_metrics.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent46_soft_sensor_field_holdout_gate"
GATE_OUT_DIR = PROJECT_ROOT / "outputs" / "soft_sensor_field_holdout_gate"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables"
GATE_METRICS_PATH = GATE_OUT_DIR / "field_holdout_gate_metrics.json"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    GATE_OUT_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    uncertainty_metrics = _read_json(UNCERTAINTY_METRICS_PATH)
    conformal_metrics = _read_json(CONFORMAL_METRICS_PATH)
    report = SoftSensorFieldHoldoutGateAgent(
        uncertainty_metrics=uncertainty_metrics,
        conformal_metrics=conformal_metrics,
    ).run([])
    generated_files = {
        "soft_sensor_field_holdout_gate": str(DELIVERABLES_DIR / "soft_sensor_field_holdout_gate.md"),
        "agent46_report": str(OUT_DIR / "agent46_report.md"),
        "field_holdout_gate_metrics": str(GATE_METRICS_PATH),
    }

    (DELIVERABLES_DIR / "soft_sensor_field_holdout_gate.md").write_text(_gate_md(report), encoding="utf-8")
    GATE_METRICS_PATH.write_text(
        json.dumps(
            {
                "evidence": report.metrics["evidence"],
                "calibration": report.metrics["calibration"],
                "gate_checks": report.metrics["gate_checks"],
                "readiness": report.metrics["readiness"],
                "release_policy": report.metrics["release_policy"],
                "method_contract": report.metrics["method_contract"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    payload = {
        "soft_sensor_field_holdout_gate": {
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
    (OUT_DIR / "agent46_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "agent46_report.md").write_text(_report_md(report, generated_files), encoding="utf-8")
    _update_manifest(generated_files)

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent46_report.md'}")
    for key, path in generated_files.items():
        print(f"{key}: {path}")


def _read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _gate_md(report) -> str:
    readiness = report.metrics["readiness"]
    evidence = report.metrics["evidence"]
    calibration = report.metrics["calibration"]
    release_policy = report.metrics["release_policy"]
    lines = [
        "# 软传感 Field Holdout 放行门控",
        "",
        f"- gate_status：`{readiness['soft_sensor_field_holdout_gate_status']}`",
        f"- gate_score：`{readiness['soft_sensor_field_holdout_gate_score']}`",
        f"- uncertainty_evidence_stage：`{evidence['uncertainty_evidence_stage']}`",
        f"- conformal_evidence_stage：`{evidence['conformal_evidence_stage']}`",
        f"- can_write_to_release_gate：`{release_policy['can_write_to_release_gate']}`",
        f"- can_auto_release_treated_water：`{release_policy['can_auto_release_treated_water']}`",
        "",
        "## Calibration Snapshot",
        "",
        f"- uncertainty_record_count：`{calibration['uncertainty_record_count']}`",
        f"- conformal_record_count：`{calibration['conformal_record_count']}`",
        f"- evaluation_pair_count：`{calibration['evaluation_pair_count']}`",
        f"- conformal_overall_coverage：`{calibration['conformal_overall_coverage']}`",
        f"- uncertainty_overall_interval_coverage：`{calibration['uncertainty_overall_interval_coverage']}`",
        f"- release_abstention_rate：`{calibration['release_abstention_rate']}`",
        f"- conformal_ood_alert_rate：`{calibration['conformal_ood_alert_rate']}`",
        "",
        "## Gate Checks",
        "",
        "| Check | Pass | Rationale |",
        "| --- | --- | --- |",
    ]
    for check in report.metrics["gate_checks"]:
        lines.append(f"| `{check['check_id']}` | `{check['passed']}` | {check['rationale']} |")
    lines.extend(
        [
            "",
            "## Release Policy",
            "",
            f"- write_scope：`{release_policy['write_scope']}`",
            f"- requires_human_review_before_application：`{release_policy['requires_human_review_before_application']}`",
            f"- requires_offline_lab_confirmation_for_compliance：`{release_policy['requires_offline_lab_confirmation_for_compliance']}`",
            "",
            "## 结论",
            "",
        ]
    )
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    return "\n".join(lines)


def _report_md(report, generated_files: dict[str, str]) -> str:
    readiness = report.metrics["readiness"]
    release_policy = report.metrics["release_policy"]
    lines = [
        "# Agent 46 软传感 Field Holdout 放行门控报告",
        "",
        f"- summary: {report.summary}",
        f"- gate_status: `{readiness['soft_sensor_field_holdout_gate_status']}`",
        f"- can_write_to_release_gate: `{release_policy['can_write_to_release_gate']}`",
        f"- failed_check_ids: `{readiness['failed_check_ids']}`",
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
    manifest["status"] = "软传感 field holdout 放行门控已生成"
    manifest["soft_sensor_field_holdout_gate"] = relative_generated
    manifest["next_stage"] = "采集真实 field holdout，重跑 Agent36/Agent39/Agent46；只有 Agent46 全门控通过后才形成软传感 release gate 校准候选"
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
