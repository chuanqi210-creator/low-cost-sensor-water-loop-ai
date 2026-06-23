from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.weak_target_stratified_conformal_agent import WeakTargetStratifiedConformalAgent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
AGENT39_REPORT = PROJECT_ROOT / "outputs" / "agent39_soft_sensor_conformal_calibration" / "agent39_report.json"
CONFORMAL_METRICS_PATH = PROJECT_ROOT / "outputs" / "soft_sensor_training" / "soft_sensor_conformal_metrics.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent47_weak_target_stratified_conformal"
METRICS_DIR = PROJECT_ROOT / "outputs" / "weak_target_stratified_conformal"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables"
METRICS_PATH = METRICS_DIR / "weak_target_stratified_metrics.json"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    agent39_payload = _read_json(AGENT39_REPORT)
    conformal_metrics = _read_json(CONFORMAL_METRICS_PATH)
    validation_records = _validation_records(agent39_payload)
    report = WeakTargetStratifiedConformalAgent(
        conformal_metrics=conformal_metrics,
        validation_records=validation_records,
    ).run([])
    generated_files = {
        "weak_target_stratified_conformal": str(DELIVERABLES_DIR / "weak_target_stratified_conformal.md"),
        "agent47_report": str(OUT_DIR / "agent47_report.md"),
        "weak_target_stratified_metrics": str(METRICS_PATH),
    }

    (DELIVERABLES_DIR / "weak_target_stratified_conformal.md").write_text(_deliverable_md(report), encoding="utf-8")
    METRICS_PATH.write_text(
        json.dumps(
            {
                "evidence": report.metrics["evidence"],
                "weak_target_profiles": report.metrics["weak_target_profiles"],
                "gate_checks": report.metrics["gate_checks"],
                "readiness": report.metrics["readiness"],
                "handoff_policy": report.metrics["handoff_policy"],
                "method_contract": report.metrics["method_contract"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    payload = {
        "weak_target_stratified_conformal": {
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
    (OUT_DIR / "agent47_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "agent47_report.md").write_text(_report_md(report, generated_files), encoding="utf-8")
    _update_manifest(generated_files)

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent47_report.md'}")
    for key, path in generated_files.items():
        print(f"{key}: {path}")


def _read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _validation_records(agent39_payload: dict[str, object]) -> list[dict[str, object]]:
    section = agent39_payload.get("soft_sensor_conformal_calibration", {})
    if not isinstance(section, dict):
        return []
    metrics = section.get("metrics", {})
    if not isinstance(metrics, dict):
        return []
    records = metrics.get("validation_records", [])
    return records if isinstance(records, list) else []


def _deliverable_md(report) -> str:
    readiness = report.metrics["readiness"]
    evidence = report.metrics["evidence"]
    handoff = report.metrics["handoff_policy"]
    lines = [
        "# 弱目标分层保形校准",
        "",
        f"- weak_target_stratified_status：`{readiness['weak_target_stratified_status']}`",
        f"- weak_target_stratified_score：`{readiness['weak_target_stratified_score']}`",
        f"- evidence_stage：`{evidence['evidence_stage']}`",
        f"- can_pass_candidate_to_agent46：`{handoff['can_pass_candidate_to_agent46']}`",
        f"- can_write_to_release_gate：`{handoff['can_write_to_release_gate']}`",
        "",
        "## Weak Target Profiles",
        "",
        "| Target | Coverage | Gap | Base Width | Candidate Width | Mode |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for profile in report.metrics["weak_target_profiles"]:
        lines.append(
            f"| `{profile['target']}` | `{profile['current_coverage']}` | `{profile['coverage_gap']}` | "
            f"`{profile['base_width']}` | `{profile['candidate_width']}` | `{profile['recommended_mode']}` |"
        )
    lines.extend(["", "## Gate Checks", "", "| Check | Pass | Rationale |", "| --- | --- | --- |"])
    for check in report.metrics["gate_checks"]:
        lines.append(f"| `{check['check_id']}` | `{check['passed']}` | {check['rationale']} |")
    lines.extend(["", "## 结论", ""])
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    return "\n".join(lines)


def _report_md(report, generated_files: dict[str, str]) -> str:
    readiness = report.metrics["readiness"]
    lines = [
        "# Agent 47 弱目标分层保形校准报告",
        "",
        f"- summary: {report.summary}",
        f"- weak_target_stratified_status: `{readiness['weak_target_stratified_status']}`",
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
    manifest["status"] = "弱目标分层保形校准层已生成"
    manifest["weak_target_stratified_conformal"] = relative_generated
    manifest["next_stage"] = "采集真实 field holdout，重跑 Agent36/Agent39/Agent47/Agent46；先修复弱目标分层 coverage，再由 Agent46 形成 release gate 校准候选"
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
