from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.minimal_grey_box_physics_agent import MinimalGreyBoxPhysicsAgent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
CONTROL_GUARDRAIL_BACKPROP_METRICS_PATH = (
    PROJECT_ROOT / "outputs" / "control_guardrail_backpropagation" / "control_guardrail_backpropagation_metrics.json"
)
OUT_DIR = PROJECT_ROOT / "outputs" / "agent53_minimal_grey_box_physics"
METRICS_DIR = PROJECT_ROOT / "outputs" / "minimal_grey_box_physics"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables"
METRICS_PATH = METRICS_DIR / "grey_box_physics_metrics.json"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)

    report = MinimalGreyBoxPhysicsAgent(
        control_guardrail_backpropagation_metrics=_read_optional_json(CONTROL_GUARDRAIL_BACKPROP_METRICS_PATH)
    ).run([])
    generated_files = {
        "minimal_grey_box_physics": str(DELIVERABLES_DIR / "minimal_grey_box_physics.md"),
        "agent53_report": str(OUT_DIR / "agent53_report.md"),
        "grey_box_physics_metrics": str(METRICS_PATH),
    }

    (DELIVERABLES_DIR / "minimal_grey_box_physics.md").write_text(_deliverable_md(report), encoding="utf-8")
    METRICS_PATH.write_text(
        json.dumps(
            {
                "method_contract": report.metrics["method_contract"],
                "scenario_physics_table": report.metrics["scenario_physics_table"],
                "guardrail_failure_boundary_patch": report.metrics["guardrail_failure_boundary_patch"],
                "control_guardrail_backpropagation_context": report.metrics["control_guardrail_backpropagation_context"],
                "readiness": report.metrics["readiness"],
                "calibration_contract": report.metrics["calibration_contract"],
                "agent50_writeback": report.metrics["agent50_writeback"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    payload = {
        "minimal_grey_box_physics": {
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
    (OUT_DIR / "agent53_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "agent53_report.md").write_text(_report_md(report, generated_files), encoding="utf-8")
    _update_manifest(generated_files)

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    for key, path in generated_files.items():
        print(f"{key}: {path}")


def _deliverable_md(report) -> str:
    readiness = report.metrics["readiness"]
    lines = [
        "# 最小灰箱物理机制增强",
        "",
        f"- grey_box_physics_status：`{readiness['grey_box_physics_status']}`",
        f"- mean_grey_box_residual：`{readiness['mean_grey_box_residual']}`",
        f"- max_mass_balance_residual：`{readiness['max_mass_balance_residual']}`",
        f"- max_byproduct_risk：`{readiness['max_byproduct_risk']}`",
        f"- can_write_to_actuator：`{readiness['can_write_to_actuator']}`",
        f"- can_write_to_release_gate：`{readiness['can_write_to_release_gate']}`",
        "",
        "## 方法契约",
        "",
    ]
    contract = report.metrics["method_contract"]
    lines.append(f"- upgrade_id：`{contract['upgrade_id']}`")
    lines.append(f"- reality_mapping：{contract['reality_mapping']}")
    lines.append(f"- failure_boundary：{contract['failure_boundary']}")
    lines.extend(["", "## 场景物理残差表", "", "| Scenario | k_eff | RTD risk | Predicted outlet | Synthetic observed | Residual | Mass residual | Byproduct risk | Failure modes |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"])
    for row in report.metrics["scenario_physics_table"]:
        lines.append(
            f"| `{row['scenario']}` | `{row['pseudo_first_order_k_per_min']}` | `{row['rtd_short_circuit_risk']}` | "
            f"`{row['predicted_outlet_load']}` | `{row['observed_synthetic_residual']}` | `{row['grey_box_residual']}` | "
            f"`{row['mass_balance_residual']}` | `{row['byproduct_risk']}` | `{row['failure_modes']}` |"
        )
    if report.metrics["guardrail_failure_boundary_patch"]:
        lines.extend(["", "## R4b Guardrail Failure Boundary Patch", ""])
        for patch in report.metrics["guardrail_failure_boundary_patch"]:
            lines.append(
                f"- `{patch['scenario']}` / `{patch['mechanism_family']}`：{patch['control_implication']}；"
                f"boundary={patch['field_boundary']}"
            )
    lines.extend(["", "## 校准需求", ""])
    for item in report.metrics["calibration_contract"]["minimum_field_tables"]:
        lines.append(f"- {item}")
    lines.extend(["", "## 结论与边界", ""])
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    return "\n".join(lines)


def _report_md(report, generated_files: dict[str, str]) -> str:
    readiness = report.metrics["readiness"]
    lines = [
        "# Agent 53 最小灰箱物理机制报告",
        "",
        f"- summary: {report.summary}",
        f"- grey_box_physics_status: `{readiness['grey_box_physics_status']}`",
        f"- mean_grey_box_residual: `{readiness['mean_grey_box_residual']}`",
        f"- can_write_to_release_gate: `{readiness['can_write_to_release_gate']}`",
        f"- guardrail_boundary_consumption_rate: `{readiness['agent53_guardrail_boundary_consumption_rate']}`",
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
    manifest["status"] = "Agent53 已消费 R4 grey-box failure boundary patches"
    manifest["minimal_grey_box_physics"] = relative_generated
    manifest["latest_agent53_guardrail_boundary_consumption_rate"] = "1.000"
    manifest["next_stage"] = "继续推进 R4b：让 Agent58/59 同步消费 R4 field requirement patches，并保持 field validation 边界"
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def _read_optional_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
