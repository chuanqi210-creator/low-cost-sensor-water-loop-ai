from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from water_ai.real_field_package_acceptance_gate import RealFieldPackageAcceptanceGate


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
FIELD_REPLAY_IMPORT_METRICS_PATH = PROJECT_ROOT / "outputs" / "field_replay_import" / "import_acceptance_metrics.json"
TIMESTAMPED_REPLAY_REPORT_PATH = PROJECT_ROOT / "outputs" / "agent42_timestamped_campaign_replay" / "agent42_report.json"
FIELD_REPLAY_GATE_METRICS_PATH = PROJECT_ROOT / "outputs" / "field_replay_calibration_gate" / "g6_p6_gate_metrics.json"
FIELD_REPLAY_EVIDENCE_CHAIN_METRICS_PATH = PROJECT_ROOT / "outputs" / "field_replay_evidence_chain" / "evidence_chain_metrics.json"
MULTI_FACILITY_REPLAY_EVALUATION_METRICS_PATH = (
    PROJECT_ROOT / "outputs" / "multi_facility_replay_evaluation" / "replay_evaluation_metrics.json"
)
SOFT_SENSOR_FIELD_HOLDOUT_METRICS_PATH = (
    PROJECT_ROOT / "outputs" / "soft_sensor_field_holdout_gate" / "field_holdout_gate_metrics.json"
)
CLAIM_PACKAGE_METRICS_PATH = PROJECT_ROOT / "outputs" / "claim_specific_field_package" / "claim_specific_field_package_metrics.json"
UNIFIED_FIELD_EVIDENCE_GATE_METRICS_PATH = (
    PROJECT_ROOT / "outputs" / "unified_field_evidence_gate" / "unified_field_evidence_gate_metrics.json"
)
OUT_DIR = PROJECT_ROOT / "outputs" / "real_field_package_acceptance_gate"
REPORT_DIR = PROJECT_ROOT / "outputs" / "real_field_package_acceptance_gate_report"
DELIVERABLE_PATH = PROJECT_ROOT / "deliverables" / "model_core_optimization" / "real_field_package_acceptance_gate.md"
METRICS_PATH = OUT_DIR / "real_field_package_acceptance_gate_metrics.json"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLE_PATH.parent.mkdir(parents=True, exist_ok=True)

    result = RealFieldPackageAcceptanceGate(
        field_replay_import_metrics=_read_json(FIELD_REPLAY_IMPORT_METRICS_PATH),
        timestamped_replay_metrics=_extract_report_metrics(
            _read_json(TIMESTAMPED_REPLAY_REPORT_PATH),
            "timestamped_campaign_replay",
        ),
        field_replay_gate_metrics=_read_json(FIELD_REPLAY_GATE_METRICS_PATH),
        field_replay_evidence_chain_metrics=_read_json(FIELD_REPLAY_EVIDENCE_CHAIN_METRICS_PATH),
        multi_facility_replay_evaluation_metrics=_read_json(MULTI_FACILITY_REPLAY_EVALUATION_METRICS_PATH),
        soft_sensor_field_holdout_gate_metrics=_read_json(SOFT_SENSOR_FIELD_HOLDOUT_METRICS_PATH),
        claim_specific_package_metrics=_read_json(CLAIM_PACKAGE_METRICS_PATH),
        unified_field_evidence_gate_metrics=_read_json(UNIFIED_FIELD_EVIDENCE_GATE_METRICS_PATH),
    ).build()

    METRICS_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    (REPORT_DIR / "real_field_package_acceptance_gate_report.md").write_text(_report_md(result), encoding="utf-8")
    DELIVERABLE_PATH.write_text(_deliverable_md(result), encoding="utf-8")
    _update_manifest(result)

    readiness = result["readiness"]
    print(f"Real field package acceptance gate: {readiness['real_field_package_acceptance_status']}")
    print(f"- passed: {readiness['passed_stage_count']}/{readiness['total_stage_count']}")
    print(f"- next: {result['next_refactor_action']['action_id']}")
    print(f"deliverable: {DELIVERABLE_PATH}")
    print(f"metrics: {METRICS_PATH}")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_report_metrics(payload: dict[str, Any], key: str) -> dict[str, Any]:
    block = payload.get(key, {})
    if isinstance(block, dict) and isinstance(block.get("metrics"), dict):
        return block["metrics"]
    metrics = payload.get("metrics", {})
    return metrics if isinstance(metrics, dict) else {}


def _report_md(result: dict[str, Any]) -> str:
    readiness = result["readiness"]
    lines = [
        "# R7 Real Field Package Acceptance Gate 报告",
        "",
        f"- 状态：`{readiness['real_field_package_acceptance_status']}`",
        f"- 分数：`{readiness['real_field_package_acceptance_score']}`",
        f"- 通过阶段：`{readiness['passed_stage_count']}/{readiness['total_stage_count']}`",
        f"- can_emit_protective_control_candidate：`{readiness['can_emit_protective_control_candidate']}`",
        f"- multi_facility_control_promotion_pass：`{readiness['multi_facility_control_promotion_pass']}`",
        f"- catalyst_proxy_field_validation_pass：`{readiness['catalyst_proxy_field_validation_pass']}`",
        f"- can_emit_release_gate_calibration_candidate：`{readiness['can_emit_release_gate_calibration_candidate']}`",
        f"- can_emit_field_supported_claim_candidate：`{readiness['can_emit_field_supported_claim_candidate']}`",
        f"- can_write_to_release_gate：`{readiness['can_write_to_release_gate']}`",
        "",
        "## Blocking Reasons",
        "",
    ]
    for reason in readiness["blocking_reasons"]:
        lines.append(f"- `{reason}`")
    lines.extend(
        [
            "",
            "## Acceptance Matrix",
            "",
            "| Stage | Status | Passed | Blocker |",
            "| --- | --- | --- | --- |",
        ]
    )
    for stage in result["acceptance_matrix"]:
        lines.append(
            f"| `{stage['stage_id']}` {stage['title']} | `{stage['status']}` | "
            f"`{stage['passed']}` | `{stage['blocker'] or '-'}` |"
        )
    lines.extend(
        [
            "",
            "## Next",
            "",
            f"- `{result['next_refactor_action']['action_id']}`：{result['next_refactor_action']['title']}",
            f"- reason：{result['next_refactor_action']['reason']}",
            f"- must_not_do：{result['next_refactor_action']['must_not_do']}",
            "",
        ]
    )
    return "\n".join(lines)


def _deliverable_md(result: dict[str, Any]) -> str:
    readiness = result["readiness"]
    package = result["minimum_real_field_package"]
    lines = [
        "# R7 真实 Field Package 导入与 Replay/Holdout 验收门",
        "",
        "## 核心判断",
        "",
        "R7 的作用是把真实现场数据包从“有文件”变成“可进入 replay、holdout 和 claim 审查的证据”。"
        "它不是 field-supported 结论本身，也不允许自动写执行器或 release gate。",
        "",
        f"- 状态：`{readiness['real_field_package_acceptance_status']}`",
        f"- 通过阶段：{readiness['passed_stage_count']}/{readiness['total_stage_count']}",
        f"- 阻断原因：{', '.join(readiness['blocking_reasons']) or '-'}",
        f"- 多设施控制晋级：`{readiness['multi_facility_control_promotion_pass']}`，catalyst_proxy_field_validation_pass=`{readiness['catalyst_proxy_field_validation_pass']}`",
        f"- 下一步：`{result['next_refactor_action']['action_id']}`",
        "",
        "## 最小真实数据包",
        "",
        f"- metadata required fields：{', '.join(package['metadata_required_fields'])}",
        f"- metadata required values：{package['metadata_required_values']}",
        f"- csv tables：{', '.join(package['csv_tables'])}",
        f"- guardrail required fields：{', '.join(package['guardrail_required_fields'])}",
        "",
        "## 验收链",
        "",
    ]
    for step in package["minimum_gate_sequence"]:
        lines.append(f"- {step}")
    lines.extend(
        [
            "",
            "## Acceptance Matrix",
            "",
            "| Stage | 作用 | 当前状态 | 通过 | 下一阻断 |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for stage in result["acceptance_matrix"]:
        lines.append(
            f"| `{stage['stage_id']}` | {stage['title']} | `{stage['status']}` | "
            f"`{stage['passed']}` | `{stage['blocker'] or '-'}` |"
        )
    lines.extend(
        [
            "",
            "## 写回边界",
            "",
        ]
    )
    policy = result["writeback_policy"]
    lines.append(f"- allowed_writeback：{', '.join(policy['allowed_writeback'])}")
    lines.append(f"- blocked_writeback：{', '.join(policy['blocked_writeback'])}")
    lines.append("- 当前没有真实 field package 通过前，所有结果仍是 field-validation-required。")
    lines.append("- 即使未来 R7 自动门全过，也只能进入人工复核，不能自动放行。")
    return "\n".join(lines)


def _update_manifest(result: dict[str, Any]) -> None:
    manifest = _read_json(MANIFEST_PATH)
    readiness = result["readiness"]
    manifest["status"] = "R7 真实 field package acceptance gate 已生成"
    manifest["real_field_package_acceptance_gate"] = {
        "real_field_package_acceptance_gate": str(DELIVERABLE_PATH.relative_to(PROJECT_ROOT)),
        "real_field_package_acceptance_gate_report": str(
            (REPORT_DIR / "real_field_package_acceptance_gate_report.md").relative_to(PROJECT_ROOT)
        ),
        "real_field_package_acceptance_gate_metrics": str(METRICS_PATH.relative_to(PROJECT_ROOT)),
    }
    manifest["latest_real_field_package_acceptance_status"] = readiness["real_field_package_acceptance_status"]
    manifest["latest_real_field_package_acceptance_score"] = readiness["real_field_package_acceptance_score"]
    manifest["next_stage"] = (
        f"按 R7 acceptance gate，下一步执行 {result['next_refactor_action']['action_id']}："
        f"{result['next_refactor_action']['title']}。仍不得把 synthetic/sample 包当作 field-supported evidence。"
    )
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
