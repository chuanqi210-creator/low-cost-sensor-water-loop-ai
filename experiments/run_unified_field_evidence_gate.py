from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from water_ai.field_evidence_gate import UnifiedFieldEvidenceGate


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ALIGNMENT_METRICS_PATH = PROJECT_ROOT / "outputs" / "field_validation_queue_alignment" / "field_validation_queue_alignment_metrics.json"
CLAIM_PACKAGE_METRICS_PATH = PROJECT_ROOT / "outputs" / "claim_specific_field_package" / "claim_specific_field_package_metrics.json"
IMPORT_METRICS_PATH = PROJECT_ROOT / "outputs" / "field_replay_import" / "import_acceptance_metrics.json"
REPLAY_GATE_METRICS_PATH = PROJECT_ROOT / "outputs" / "field_replay_calibration_gate" / "g6_p6_gate_metrics.json"
EVIDENCE_CHAIN_METRICS_PATH = PROJECT_ROOT / "outputs" / "field_replay_evidence_chain" / "evidence_chain_metrics.json"
SOFT_SENSOR_GATE_METRICS_PATH = PROJECT_ROOT / "outputs" / "soft_sensor_field_holdout_gate" / "field_holdout_gate_metrics.json"
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "unified_field_evidence_gate"
REPORT_DIR = PROJECT_ROOT / "outputs" / "unified_field_evidence_gate_report"
DELIVERABLE_PATH = PROJECT_ROOT / "deliverables" / "model_core_optimization" / "unified_field_evidence_gate.md"
METRICS_PATH = OUT_DIR / "unified_field_evidence_gate_metrics.json"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLE_PATH.parent.mkdir(parents=True, exist_ok=True)

    result = UnifiedFieldEvidenceGate(
        field_validation_alignment_metrics=_read_json(ALIGNMENT_METRICS_PATH),
        claim_specific_package_metrics=_read_json(CLAIM_PACKAGE_METRICS_PATH),
        field_replay_import_metrics=_read_json(IMPORT_METRICS_PATH),
        field_replay_gate_metrics=_read_json(REPLAY_GATE_METRICS_PATH),
        field_replay_evidence_chain_metrics=_read_json(EVIDENCE_CHAIN_METRICS_PATH),
        soft_sensor_field_holdout_gate_metrics=_read_json(SOFT_SENSOR_GATE_METRICS_PATH),
    ).build()

    METRICS_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    report_md = _report_md(result)
    (REPORT_DIR / "unified_field_evidence_gate_report.md").write_text(report_md, encoding="utf-8")
    DELIVERABLE_PATH.write_text(_deliverable_md(result), encoding="utf-8")
    _update_manifest(result)

    readiness = result["readiness"]
    print(f"Unified field evidence gate: {readiness['unified_field_evidence_gate_status']}")
    print(f"- records: {readiness['unified_evidence_record_count']}")
    print(f"- source_basis_completion_rate: {readiness['source_basis_completion_rate']}")
    print(f"- citation_detail_completion_rate: {readiness['citation_detail_completion_rate']}")
    print(f"- source_basis_parameter_boundary_coverage: {readiness['source_basis_parameter_boundary_coverage']}")
    print(f"- effective_literature_traceability: {readiness['effective_literature_traceability']}")
    print(f"- field_supported_edge_ratio: {result['source_basis_detail_status']['field_supported_edge_ratio']}")
    print(f"- claim_basis_promotion_gate_status: {result['claim_basis_promotion_gate']['gate_status']}")
    print(f"- ready_promotion_count: {result['claim_basis_promotion_gate']['ready_promotion_count']}")
    print(f"- next: {result['next_refactor_action']['action_id']}")
    print(f"deliverable: {DELIVERABLE_PATH}")
    print(f"metrics: {METRICS_PATH}")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _report_md(result: dict[str, Any]) -> str:
    readiness = result["readiness"]
    lines = [
        "# 统一 Field Evidence Gate 报告",
        "",
        f"- 状态：`{readiness['unified_field_evidence_gate_status']}`",
        f"- 统一证据记录数：{readiness['unified_evidence_record_count']}",
        f"- gate 来源合并覆盖率：{readiness['gate_source_consolidation_coverage']}",
        f"- source_basis_completion_rate（Agent59 原始任务完成率）：{readiness['source_basis_completion_rate']}",
        f"- citation_detail_completion_rate（统一 gate 补充后的文献细节率）：{readiness['citation_detail_completion_rate']}",
        f"- source_basis_parameter_boundary_coverage：{readiness['source_basis_parameter_boundary_coverage']}",
        f"- effective_literature_traceability：{readiness['effective_literature_traceability']}",
        f"- field_supported_edge_ratio：{result['source_basis_detail_status']['field_supported_edge_ratio']}",
        f"- claim_basis_promotion_gate_status：{result['claim_basis_promotion_gate']['gate_status']}",
        f"- promotion_decision_count：{result['claim_basis_promotion_gate']['promotion_decision_count']}",
        f"- ready_promotion_count：{result['claim_basis_promotion_gate']['ready_promotion_count']}",
        f"- blocked_promotion_count：{result['claim_basis_promotion_gate']['blocked_promotion_count']}",
        f"- field_import_pass：{readiness['field_import_pass']}",
        f"- field_replay_evidence_chain_pass：{readiness['field_replay_evidence_chain_pass']}",
        f"- soft_sensor_field_holdout_gate_pass：{readiness['soft_sensor_field_holdout_gate_pass']}",
        f"- can_emit_field_claim_upgrade：{readiness['can_emit_field_claim_upgrade']}",
        f"- can_write_to_release_gate：{readiness['can_write_to_release_gate']}",
        "",
        "## 下一步",
        "",
        f"- `{result['next_refactor_action']['action_id']}`：{result['next_refactor_action']['title']}",
        f"- 原因：{result['next_refactor_action']['reason']}",
        f"- 禁止事项：{result['next_refactor_action']['must_not_do']}",
        "",
        "## 统一记录",
        "",
    ]
    for record in result["unified_evidence_records"]:
        lines.extend(
            [
                f"### {record['need_id']} {record['field_validation_need']}",
                "",
                f"- evidence_stage：`{record['evidence_stage']}`",
                f"- supporting_entries：{', '.join(record['supporting_entries'])}",
                f"- replay_gate_ids：{', '.join(record['replay_gate_ids'])}",
                f"- source_basis_present：{record['source_basis_status']['source_basis_present']}",
                f"- citation_detail_complete：{record['source_basis_status']['citation_detail_complete']}",
                f"- detail_library_complete：{record['source_basis_status']['detail_library_complete']}",
                f"- blockers：{', '.join(record['claim_upgrade_blocked_by'])}",
                "",
            ]
        )
    lines.extend(
        [
            "## Claim Basis Promotion Gate",
            "",
            f"- gate_status：`{result['claim_basis_promotion_gate']['gate_status']}`",
            f"- evidence_level：`{result['claim_basis_promotion_gate']['evidence_level']}`",
            f"- can_emit_field_claim_upgrade：{result['claim_basis_promotion_gate']['can_emit_field_claim_upgrade']}",
            f"- can_write_to_actuator：{result['claim_basis_promotion_gate']['can_write_to_actuator']}",
            f"- can_write_to_release_gate：{result['claim_basis_promotion_gate']['can_write_to_release_gate']}",
            "",
        ]
    )
    for row in result["claim_basis_promotion_gate"]["promotion_rows"]:
        lines.extend(
            [
                f"### {row['need_id']} promotion",
                "",
                f"- status：`{row['promotion_status']}`",
                f"- allowed_promotion_level：`{row['allowed_promotion_level']}`",
                f"- current_basis：{row['current_basis']}",
                f"- not_current_basis：{', '.join(row['not_current_basis'])}",
                f"- blocked_by：{', '.join(row['blocked_by'])}",
                f"- next_required_gate：`{row['next_required_gate']}`",
                "",
            ]
        )
    return "\n".join(lines)


def _deliverable_md(result: dict[str, Any]) -> str:
    readiness = result["readiness"]
    gate = result["gate_consolidation"]
    lines = [
        "# 统一 Field Evidence Gate",
        "",
        "## 核心判断",
        "",
        "这一步不是新增业务 agent，而是把分散在 Agent43/44/45/46/58/59 的 field evidence、claim package、source_basis、"
        "replay/holdout gate 合成一个统一证据门控接口。它的价值是减少重复阻断、统一 claim 升级边界，并让后续模块只消费一个证据接口。",
        "",
        f"- 状态：`{readiness['unified_field_evidence_gate_status']}`",
        f"- 统一证据记录数：{readiness['unified_evidence_record_count']}",
        f"- 消费 gate 来源数：{gate['consumed_gate_source_count']}/{gate['expected_gate_source_count']}",
        f"- source_basis_completion_rate（Agent59 原始任务完成率）：{readiness['source_basis_completion_rate']}",
        f"- citation_detail_completion_rate（统一 gate 补充后的文献细节率）：{readiness['citation_detail_completion_rate']}",
        f"- source_basis_parameter_boundary_coverage：{readiness['source_basis_parameter_boundary_coverage']}",
        f"- effective_literature_traceability：{readiness['effective_literature_traceability']}",
        f"- field_supported_edge_ratio：{result['source_basis_detail_status']['field_supported_edge_ratio']}",
        f"- claim_basis_promotion_gate_status：{result['claim_basis_promotion_gate']['gate_status']}",
        f"- ready_promotion_count：{result['claim_basis_promotion_gate']['ready_promotion_count']}",
        f"- blocked_promotion_count：{result['claim_basis_promotion_gate']['blocked_promotion_count']}",
        f"- synthetic 边界保留：{readiness['synthetic_boundary_preserved']}",
        "",
        "## 已合并的证据来源",
        "",
    ]
    for source in gate["consumed_gate_sources"]:
        lines.append(f"- {source}")
    lines.extend(
        [
            "",
            "## 统一阻断类型",
            "",
        ]
    )
    for blocker in gate["unified_blocker_kinds"]:
        lines.append(f"- {blocker}")
    lines.extend(
        [
            "",
            "## 证据记录",
            "",
            "| Need | Stage | Raw source detail flag | Detail library complete | Field import | Evidence chain | Soft gate |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for record in result["unified_evidence_records"]:
        lines.append(
            "| "
            f"{record['need_id']} | "
            f"{record['evidence_stage']} | "
            f"{record['source_basis_status']['citation_detail_complete']} | "
            f"{record['source_basis_status']['detail_library_complete']} | "
            f"{record['field_import_status']['import_ready']} | "
            f"{record['field_replay_evidence_chain_status']['can_emit_protective_writeback_candidate']} | "
            f"{record['soft_sensor_field_holdout_status']['can_write_to_release_gate']} |"
        )
    lines.extend(
        [
            "",
            "## Claim Basis Promotion Gate",
            "",
            "该 gate 把每条统一证据记录转成主张升级决策行，明确哪些依据是当前可用依据，"
            "哪些依据绝不能被误写为 field evidence、release gate、actuator policy 或法律/专利结论。",
            "",
            f"- gate_status：`{result['claim_basis_promotion_gate']['gate_status']}`",
            f"- promotion_decision_count：{result['claim_basis_promotion_gate']['promotion_decision_count']}",
            f"- ready_promotion_count：{result['claim_basis_promotion_gate']['ready_promotion_count']}",
            f"- blocked_promotion_count：{result['claim_basis_promotion_gate']['blocked_promotion_count']}",
            f"- can_emit_field_claim_upgrade：{result['claim_basis_promotion_gate']['can_emit_field_claim_upgrade']}",
            f"- can_write_to_actuator：{result['claim_basis_promotion_gate']['can_write_to_actuator']}",
            f"- can_write_to_release_gate：{result['claim_basis_promotion_gate']['can_write_to_release_gate']}",
            "",
            "| Need | Promotion status | Allowed level | Next required gate | Blockers |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in result["claim_basis_promotion_gate"]["promotion_rows"]:
        lines.append(
            "| "
            f"{row['need_id']} | "
            f"{row['promotion_status']} | "
            f"{row['allowed_promotion_level']} | "
            f"{row['next_required_gate']} | "
            f"{'; '.join(row['blocked_by'])} |"
        )
    lines.extend(
        [
            "",
            "## Source Basis Detail Library",
            "",
            "这一步把原先的 source_basis 方法标签补成可追溯的文献、适用条件、参数边界和失败边界。"
            "它只提升 literature-supported traceability，不产生 field-supported claim。",
            "",
        ]
    )
    for basis_id, detail in result["source_basis_detail_library"].items():
        lines.extend(
            [
                f"### {basis_id}",
                "",
                f"- evidence_stage：`{detail['evidence_stage']}`",
                f"- citation_count：{len(detail['citation_records'])}",
                f"- parameter_or_method_boundaries：{'; '.join(detail['parameter_or_method_boundaries'])}",
                f"- required_field_validation：{'; '.join(detail['required_field_validation'])}",
                f"- failure_boundary：{detail['failure_boundary']}",
                "",
            ]
        )
    lines.extend(
        [
            "",
            "## 下一步",
            "",
            f"- `{result['next_refactor_action']['action_id']}`：{result['next_refactor_action']['title']}",
            f"- 原因：{result['next_refactor_action']['reason']}",
            f"- 禁止事项：{result['next_refactor_action']['must_not_do']}",
            "",
            "## 边界",
            "",
            "- 统一 gate 只合并接口和阻断口径，不产生 field-supported 结论。",
            "- source_basis citation detail 只能增强 literature-supported traceability，不能替代真实 field package。",
            "- 当前不写执行器、不写 release gate、不删除历史 Agent43/44/45/46/58/59。",
            "",
        ]
    )
    return "\n".join(lines)


def _update_manifest(result: dict[str, Any]) -> None:
    manifest = _read_json(MANIFEST_PATH)
    manifest["status"] = "统一 Field Evidence Gate 已形成"
    manifest["unified_field_evidence_gate"] = {
        "unified_field_evidence_gate": str(DELIVERABLE_PATH.relative_to(PROJECT_ROOT)),
        "unified_field_evidence_gate_report": str(
            (REPORT_DIR / "unified_field_evidence_gate_report.md").relative_to(PROJECT_ROOT)
        ),
        "unified_field_evidence_gate_metrics": str(METRICS_PATH.relative_to(PROJECT_ROOT)),
    }
    manifest["latest_unified_field_evidence_gate_status"] = result["readiness"][
        "unified_field_evidence_gate_status"
    ]
    promotion_gate = result["claim_basis_promotion_gate"]
    manifest["latest_claim_basis_promotion_gate_status"] = promotion_gate["gate_status"]
    manifest["latest_claim_basis_promotion_gate_ready_promotion_count"] = promotion_gate[
        "ready_promotion_count"
    ]
    manifest["latest_claim_basis_promotion_gate_blocked_promotion_count"] = promotion_gate[
        "blocked_promotion_count"
    ]
    manifest["latest_claim_basis_promotion_gate_can_emit_field_claim_upgrade"] = promotion_gate[
        "can_emit_field_claim_upgrade"
    ]
    manifest["latest_claim_basis_promotion_gate_can_write_to_actuator"] = promotion_gate[
        "can_write_to_actuator"
    ]
    manifest["latest_claim_basis_promotion_gate_can_write_to_release_gate"] = promotion_gate[
        "can_write_to_release_gate"
    ]
    manifest["next_stage"] = (
        f"按统一 evidence gate 结果，下一步优先推进 {result['next_refactor_action']['action_id']}："
        f"{result['next_refactor_action']['title']}。"
    )
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
