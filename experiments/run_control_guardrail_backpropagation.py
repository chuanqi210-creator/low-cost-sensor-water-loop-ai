from __future__ import annotations

import json
from pathlib import Path

from water_ai.control_guardrail_backpropagation import ControlGuardrailBackpropagation


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
REPLAY_EVALUATION_METRICS_PATH = PROJECT_ROOT / "outputs" / "multi_facility_replay_evaluation" / "replay_evaluation_metrics.json"
GREY_BOX_PHYSICS_METRICS_PATH = PROJECT_ROOT / "outputs" / "minimal_grey_box_physics" / "grey_box_physics_metrics.json"
FIELD_VALIDATION_ALIGNMENT_METRICS_PATH = (
    PROJECT_ROOT / "outputs" / "field_validation_queue_alignment" / "field_validation_queue_alignment_metrics.json"
)
CLAIM_PACKAGE_METRICS_PATH = PROJECT_ROOT / "outputs" / "claim_specific_field_package" / "claim_specific_field_package_metrics.json"
DELIVERABLE_PATH = PROJECT_ROOT / "deliverables" / "model_core_optimization" / "control_guardrail_backpropagation.md"
OUT_DIR = PROJECT_ROOT / "outputs" / "control_guardrail_backpropagation"
REPORT_DIR = PROJECT_ROOT / "outputs" / "control_guardrail_backpropagation_report"
METRICS_PATH = OUT_DIR / "control_guardrail_backpropagation_metrics.json"
REPORT_PATH = REPORT_DIR / "control_guardrail_backpropagation_report.md"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLE_PATH.parent.mkdir(parents=True, exist_ok=True)

    result = ControlGuardrailBackpropagation(
        replay_evaluation_metrics=_read_optional_json(REPLAY_EVALUATION_METRICS_PATH),
        grey_box_physics_metrics=_read_optional_json(GREY_BOX_PHYSICS_METRICS_PATH),
        field_validation_alignment_metrics=_read_optional_json(FIELD_VALIDATION_ALIGNMENT_METRICS_PATH),
        claim_specific_package_metrics=_read_optional_json(CLAIM_PACKAGE_METRICS_PATH),
    ).build()

    METRICS_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    DELIVERABLE_PATH.write_text(_deliverable_md(result), encoding="utf-8")
    REPORT_PATH.write_text(_report_md(result), encoding="utf-8")
    _update_manifest()

    readiness = result["readiness"]
    coverage = result["coverage_metrics"]
    print(
        "R4 control guardrail backpropagation: "
        f"{readiness['guardrail_backpropagation_status']}; "
        f"mechanism_coverage={coverage['resolved_case_to_mechanism_coverage']:.3f}; "
        f"field_requirement_coverage={coverage['resolved_case_to_field_requirement_coverage']:.3f}"
    )
    print(f"deliverable: {DELIVERABLE_PATH}")
    print(f"metrics: {METRICS_PATH}")


def _read_optional_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _deliverable_md(result: dict[str, object]) -> str:
    readiness = result["readiness"]
    coverage = result["coverage_metrics"]
    lines = [
        "# R4 控制 Guardrail 失败案例反写：灰箱机制与现场字段",
        "",
        f"- status：`{readiness['guardrail_backpropagation_status']}`",
        f"- resolved_case_count：`{coverage['resolved_case_count']}`",
        f"- resolved_case_to_mechanism_coverage：`{coverage['resolved_case_to_mechanism_coverage']}`",
        f"- resolved_case_to_field_requirement_coverage：`{coverage['resolved_case_to_field_requirement_coverage']}`",
        f"- grey_box_failure_boundary_count：`{coverage['grey_box_failure_boundary_count']}`",
        f"- field_replay_required_field_count：`{coverage['field_replay_required_field_count']}`",
        f"- field_replay_coverage：`{coverage['field_replay_coverage']}`",
        f"- can_write_to_actuator：`{readiness['can_write_to_actuator']}`",
        "",
        "## Resolved Case Backpropagation",
        "",
        "| Case | Scenario | Mechanism Family | Guardrail Action | Field Fields | Claim Boundary |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in result["resolved_case_backpropagation_table"]:
        lines.append(
            "| "
            f"`{row['batch_id']}` | "
            f"{row['scenario']} | "
            f"`{row['mechanism_family']}` | "
            f"`{row['guardrail_aware_policy_action_id']}` | "
            f"{', '.join(row['field_required_fields'])} | "
            f"{row['claim_boundary']} |"
        )
    lines.extend(
        [
            "",
            "## Grey-Box Patch",
            "",
        ]
    )
    for patch in result["grey_box_patch"]:
        lines.extend(
            [
                f"### {patch['scenario']}",
                "",
                f"- mechanism_family：`{patch['mechanism_family']}`",
                f"- control_implication：{patch['control_implication']}",
                f"- field_boundary：{patch['field_boundary']}",
                "- grey_box_boundary：",
            ]
        )
        for boundary in patch["grey_box_boundary"]:
            lines.append(f"  - {boundary}")
        lines.append("")
    lines.extend(
        [
            "## Field Requirement Patch",
            "",
        ]
    )
    for patch in result["field_requirement_patch"]:
        lines.append(f"- `{patch['scenario']}`：{', '.join(patch['required_fields'])}")
    lines.extend(
        [
            "",
            "## 边界",
            "",
            "- 本结果只把 synthetic guardrail replay 失败案例反写为机制边界和采集字段。",
            "- field_replay_coverage 仍为 0 时，不能宣称现场控制有效、灰箱参数已校准或可写执行器。",
        ]
    )
    return "\n".join(lines)


def _report_md(result: dict[str, object]) -> str:
    readiness = result["readiness"]
    coverage = result["coverage_metrics"]
    return "\n".join(
        [
            "# R4 Control Guardrail Backpropagation Report",
            "",
            f"- status: `{readiness['guardrail_backpropagation_status']}`",
            f"- resolved_case_to_mechanism_coverage: `{coverage['resolved_case_to_mechanism_coverage']}`",
            f"- resolved_case_to_field_requirement_coverage: `{coverage['resolved_case_to_field_requirement_coverage']}`",
            f"- required_field_count: `{coverage['field_replay_required_field_count']}`",
            f"- can_write_to_actuator: `{readiness['can_write_to_actuator']}`",
            f"- next_refactor_action: `{result['next_refactor_action']['action_id']}`",
        ]
    )


def _update_manifest() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest["status"] = "R4 已把 R3c resolved guardrail failure cases 反写到灰箱机制边界和现场 replay 必采字段"
    manifest["control_guardrail_backpropagation"] = {
        "control_guardrail_backpropagation": str(DELIVERABLE_PATH.relative_to(PROJECT_ROOT)),
        "control_guardrail_backpropagation_report": str(REPORT_PATH.relative_to(PROJECT_ROOT)),
        "control_guardrail_backpropagation_metrics": str(METRICS_PATH.relative_to(PROJECT_ROOT)),
    }
    manifest["latest_control_guardrail_backpropagation_status"] = (
        "synthetic_guardrail_backpropagation_ready_needs_field_replay_and_grey_box_calibration"
    )
    manifest["next_stage"] = (
        "推进 R4b：让 Agent53、Agent58、Agent59 消费 R4 的 grey-box boundary 与 field requirement patch；"
        "仍不得写执行器、release gate 或 field-supported claim"
    )
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
