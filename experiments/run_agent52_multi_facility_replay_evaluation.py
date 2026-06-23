from __future__ import annotations

import csv
import json
from pathlib import Path

from water_ai.agents.multi_facility_collaborative_control_agent import MultiFacilityCollaborativeControlAgent
from water_ai.agents.multi_facility_replay_evaluation_agent import MultiFacilityReplayEvaluationAgent
from water_ai.agents.sensor_network_sparse_placement_agent import SensorNetworkSparsePlacementAgent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
SPARSE_METRICS_PATH = PROJECT_ROOT / "outputs" / "sensor_network_sparse_placement" / "sparse_placement_metrics.json"
COLLAB_METRICS_PATH = PROJECT_ROOT / "outputs" / "multi_facility_collaborative_control" / "collaborative_control_metrics.json"
CATALYST_PROXY_METRICS_PATH = PROJECT_ROOT / "outputs" / "catalyst_activity_proxy" / "catalyst_activity_proxy_metrics.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent52_multi_facility_replay_evaluation"
METRICS_DIR = PROJECT_ROOT / "outputs" / "multi_facility_replay_evaluation"
REPLAY_EXPORT_DIR = METRICS_DIR / "agent52_replay_export"
REPLAY_EXPORT_MANIFEST_PATH = REPLAY_EXPORT_DIR / "agent52_replay_export_manifest.json"
REPLAY_EXPORT_CSV_PATH = REPLAY_EXPORT_DIR / "agent52_replay_table.csv"
REPLAY_EXPORT_ROWS_PATH = REPLAY_EXPORT_DIR / "agent52_replay_table.rows.json"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables"
METRICS_PATH = METRICS_DIR / "replay_evaluation_metrics.json"
AGENT52_REPLAY_EXPORT_FIELDS = [
    "work_package_id",
    "replay_episode_id",
    "batch_id",
    "timestamp_min",
    "scenario",
    "policy_action_id",
    "guardrail_aware_policy_action_id",
    "expert_action_id",
    "reward_regret",
    "guardrail_aware_reward_regret",
    "pressure_source_conflict_count",
    "resolved_pressure_source_conflict_count",
    "unresolved_pressure_source_conflict_count",
    "pressure_source_resolution_record_count",
    "pressure_source_conflict_requires_operator_review",
    "pressure_source_conflict_control_block",
    "control_policy_baseline_comparison_status",
    "data_origin",
    "evidence_status",
    "can_create_field_evidence_by_export_only",
    "can_write_to_actuator",
    "can_write_to_release_gate",
]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    REPLAY_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    collaborative_metrics = _load_collaborative_metrics()
    catalyst_proxy_metrics = _read_optional_json(CATALYST_PROXY_METRICS_PATH)
    report = MultiFacilityReplayEvaluationAgent(
        collaborative_control_metrics=collaborative_metrics,
        catalyst_proxy_metrics=catalyst_proxy_metrics,
    ).run([])
    replay_export = _agent52_replay_export_payload(report)
    _write_agent52_replay_export(replay_export)
    generated_files = {
        "multi_facility_replay_evaluation": str(DELIVERABLES_DIR / "multi_facility_replay_evaluation.md"),
        "agent52_report": str(OUT_DIR / "agent52_report.md"),
        "replay_evaluation_metrics": str(METRICS_PATH),
        "agent52_replay_export_manifest": str(REPLAY_EXPORT_MANIFEST_PATH),
        "agent52_replay_table_csv": str(REPLAY_EXPORT_CSV_PATH),
        "agent52_replay_table_rows_json": str(REPLAY_EXPORT_ROWS_PATH),
    }

    (DELIVERABLES_DIR / "multi_facility_replay_evaluation.md").write_text(_deliverable_md(report), encoding="utf-8")
    METRICS_PATH.write_text(
        json.dumps(
            {
                "method_contract": report.metrics["method_contract"],
                "replay_schema": report.metrics["replay_schema"],
                "replay_table": report.metrics["replay_table"],
                "offline_evaluation_metrics": report.metrics["offline_evaluation_metrics"],
                "control_policy_comparison": report.metrics["control_policy_comparison"],
                "control_baseline_contract": report.metrics["control_baseline_contract"],
                "agent52_replay_export_contract": replay_export["manifest"],
                "reward_diagnostics": report.metrics["reward_diagnostics"],
                "distillation_evaluation": report.metrics["distillation_evaluation"],
                "catalyst_proxy_context": report.metrics["catalyst_proxy_context"],
                "pressure_headloss_context": report.metrics["pressure_headloss_context"],
                "readiness": report.metrics["readiness"],
                "agent49_writeback": report.metrics["agent49_writeback"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    payload = {
        "multi_facility_replay_evaluation": {
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
        "agent52_replay_export": replay_export,
        "generated_files": generated_files,
    }
    (OUT_DIR / "agent52_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "agent52_report.md").write_text(_report_md(report, generated_files), encoding="utf-8")
    _update_manifest(generated_files)

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent52_report.md'}")
    for key, path in generated_files.items():
        print(f"{key}: {path}")


def _agent52_replay_export_payload(report) -> dict[str, object]:
    readiness = report.metrics["readiness"]
    contract = report.metrics["control_baseline_contract"]
    rows = _agent52_replay_export_rows(report)
    all_rows_field_origin = all(row["data_origin"] == "field_coordination_replay" for row in rows)
    field_ready = bool(readiness["field_ready"]) and all_rows_field_origin
    export_status = (
        "agent52_replay_export_field_candidate_ready_needs_r8p_operator_release_gates"
        if field_ready
        else "agent52_replay_export_ready_synthetic_only"
    )
    manifest = {
        "export_id": "agent52_replay_export_v1",
        "work_package_id": "R8U25_AGENT52_REPLAY_EXPORT_WORK_PACKAGE",
        "export_status": export_status,
        "replay_run_id": f"agent52_multi_facility_replay_{rows[0]['data_origin'] if rows else 'empty'}",
        "source_policy_id": "agent49_policy_and_guardrail_aware_policy",
        "expert_review_basis": (
            "operator_or_validated_expert_action"
            if field_ready
            else "synthetic expert labels for interface and baseline validation only"
        ),
        "row_count": len(rows),
        "required_fields": [
            "batch_id",
            "scenario",
            "policy_action_id",
            "expert_action_id",
            "pressure_source_conflict_count",
            "resolved_pressure_source_conflict_count",
            "unresolved_pressure_source_conflict_count",
            "pressure_source_resolution_record_count",
            "pressure_source_conflict_requires_operator_review",
            "pressure_source_conflict_control_block",
            "data_origin",
        ],
        "provided_fields": AGENT52_REPLAY_EXPORT_FIELDS,
        "expected_output_files": [
            "agent52_replay_export_manifest.json",
            "agent52_replay_table.csv",
            "agent52_replay_table.rows.json",
        ],
        "control_policy_baseline_comparison_status": contract["comparison_status"],
        "control_policy_baseline_strategy_count": contract["baseline_strategy_count"],
        "all_rows_field_origin": all_rows_field_origin,
        "can_route_to_r8p_candidate_rows": field_ready,
        "can_create_field_evidence_by_export_only": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "downstream_validation_gates": [
            "Agent61 R8p schema/provenance/template-marker gate",
            "Agent61 same-batch six-table bundle gate",
            "Agent61 downstream routing preflight",
            "operator final execution review",
            "release validation and actuator interlock",
        ],
        "failure_boundary": (
            "Agent52 replay export supplies replay-origin action/conflict evidence only. "
            "Synthetic rows cannot become field evidence, and even field replay rows must pass R8p/R8v/operator/release gates before execution."
        ),
    }
    return {"manifest": manifest, "rows": rows}


def _agent52_replay_export_rows(report) -> list[dict[str, object]]:
    contract = report.metrics["control_baseline_contract"]
    rows: list[dict[str, object]] = []
    for row in report.metrics["replay_table"]:
        data_origin = str(row["data_origin"])
        field_origin = data_origin == "field_coordination_replay"
        rows.append(
            {
                "work_package_id": "R8U25_AGENT52_REPLAY_EXPORT_WORK_PACKAGE",
                "replay_episode_id": (
                    f"agent52:{data_origin}:{row['batch_id']}:{row['scenario']}:{row['timestamp_min']}"
                ),
                "batch_id": row["batch_id"],
                "timestamp_min": row["timestamp_min"],
                "scenario": row["scenario"],
                "policy_action_id": row["policy_action_id"],
                "guardrail_aware_policy_action_id": row["guardrail_aware_policy_action_id"],
                "expert_action_id": row["expert_action_id"],
                "reward_regret": row["reward_regret"],
                "guardrail_aware_reward_regret": row["guardrail_aware_reward_regret"],
                "pressure_source_conflict_count": row["pressure_source_conflict_count"],
                "resolved_pressure_source_conflict_count": row["resolved_pressure_source_conflict_count"],
                "unresolved_pressure_source_conflict_count": row["unresolved_pressure_source_conflict_count"],
                "pressure_source_resolution_record_count": row["pressure_source_resolution_record_count"],
                "pressure_source_conflict_requires_operator_review": row[
                    "pressure_source_conflict_requires_operator_review"
                ],
                "pressure_source_conflict_control_block": row["pressure_source_conflict_control_block"],
                "control_policy_baseline_comparison_status": contract["comparison_status"],
                "data_origin": data_origin,
                "evidence_status": (
                    "field_replay_candidate_needs_r8p_operator_release_gates"
                    if field_origin
                    else "synthetic_replay_candidate_not_field_evidence"
                ),
                "can_create_field_evidence_by_export_only": False,
                "can_write_to_actuator": False,
                "can_write_to_release_gate": False,
            }
        )
    return rows


def _write_agent52_replay_export(replay_export: dict[str, object]) -> None:
    manifest = replay_export["manifest"]
    rows = replay_export["rows"]
    REPLAY_EXPORT_MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    REPLAY_EXPORT_ROWS_PATH.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    with REPLAY_EXPORT_CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=AGENT52_REPLAY_EXPORT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _read_optional_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _load_collaborative_metrics() -> dict[str, object]:
    if COLLAB_METRICS_PATH.exists():
        return json.loads(COLLAB_METRICS_PATH.read_text(encoding="utf-8"))
    sparse_metrics = _load_sparse_metrics()
    report = MultiFacilityCollaborativeControlAgent(sparse_placement_metrics=sparse_metrics).run([])
    return dict(report.metrics)


def _load_sparse_metrics() -> dict[str, object]:
    if SPARSE_METRICS_PATH.exists():
        return json.loads(SPARSE_METRICS_PATH.read_text(encoding="utf-8"))
    report = SensorNetworkSparsePlacementAgent(max_sensors=6, budget_limit=5.8).run([])
    return {
        "selected_sensor_plan": report.metrics["selected_sensor_plan"],
        "coverage": report.metrics["coverage"],
        "readiness": report.metrics["readiness"],
        "soft_sensor_interface": report.metrics["soft_sensor_interface"],
    }


def _deliverable_md(report) -> str:
    readiness = report.metrics["readiness"]
    metrics = report.metrics["offline_evaluation_metrics"]
    writeback = report.metrics["agent49_writeback"]
    catalyst = report.metrics["catalyst_proxy_context"]
    pressure = report.metrics["pressure_headloss_context"]
    comparison = report.metrics["control_policy_comparison"]
    contract = report.metrics["control_baseline_contract"]
    replay_export = _agent52_replay_export_payload(report)
    export_manifest = replay_export["manifest"]
    lines = [
        "# 多设施协同控制 Replay-Ready 离线评估",
        "",
        f"- replay_evaluation_status：`{readiness['replay_evaluation_status']}`",
        f"- replay_case_count：`{metrics['replay_case_count']}`",
        f"- joint_action_accuracy：`{metrics['joint_action_accuracy']}`",
        f"- mean_reward_regret：`{metrics['mean_reward_regret']}`",
        f"- protective_false_positive_rate：`{metrics['protective_false_positive_rate']}`",
        f"- guardrail_aware_joint_action_accuracy：`{metrics['guardrail_aware_joint_action_accuracy']}`",
        f"- guardrail_aware_mean_reward_regret：`{metrics['guardrail_aware_mean_reward_regret']}`",
        f"- guardrail_aware_false_positive_action_cost：`{metrics['guardrail_aware_false_positive_action_cost']}`",
        f"- field_replay_coverage：`{metrics['field_replay_coverage']}`",
        f"- catalyst_proxy_summary_status：`{metrics['catalyst_proxy_summary_status']}`",
        f"- catalyst_proxy_scoreable_batch_count：`{metrics['catalyst_proxy_scoreable_batch_count']}`",
        f"- catalyst_proxy_field_validation_pass：`{metrics['catalyst_proxy_field_validation_pass']}`",
        f"- pressure_headloss_boundary_consumed：`{metrics['pressure_headloss_boundary_consumed']}`",
        f"- pressure_headloss_candidate_count：`{metrics['pressure_headloss_candidate_count']}`",
        f"- pressure_headloss_blocked_guardrail_case_count：`{metrics['pressure_headloss_blocked_guardrail_case_count']}`",
        f"- pressure_headloss_can_relax_control_guardrail：`{metrics['pressure_headloss_can_relax_control_guardrail']}`",
        f"- control_policy_baseline_comparison_status：`{contract['comparison_status']}`",
        f"- control_policy_baseline_strategy_count：`{contract['baseline_strategy_count']}`",
        f"- agent52_replay_export_status：`{export_manifest['export_status']}`",
        f"- agent52_replay_export_row_count：`{export_manifest['row_count']}`",
        f"- can_write_to_actuator：`{readiness['can_write_to_actuator']}`",
        "",
        "## Replay Schema",
        "",
        "| 字段 | 说明 |",
        "| --- | --- |",
    ]
    for field in report.metrics["replay_schema"]["required_fields"]:
        lines.append(f"| `{field}` | state-action-reward replay 必需字段 |")
    lines.extend(
        [
            "",
            "## Synthetic Replay Cases",
            "",
            "| Case | Scenario | Baseline Policy | R3b Policy | Expert | Baseline Regret | R3b Regret | False Positive Cost |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in report.metrics["replay_table"]:
        lines.append(
            f"| `{row['batch_id']}` | {row['scenario']} | `{row['policy_action_id']}` | "
            f"`{row['guardrail_aware_policy_action_id']}` | `{row['expert_action_id']}` | "
            f"`{row['reward_regret']}` | `{row['guardrail_aware_reward_regret']}` | "
            f"`{row['false_positive_action_cost']}` |"
        )
    lines.extend(["", "## Agent49 Writeback Boundary", ""])
    lines.append(f"- allowed_writeback：`{writeback['allowed_writeback']}`")
    lines.append(f"- blocked_writeback：`{writeback['blocked_writeback']}`")
    lines.append(f"- policy_effect：`{writeback['policy_effect']}`")
    lines.extend(
        [
            "",
            "## Control Policy Baseline Comparison",
            "",
            "| Strategy | Accuracy | Mean Regret | P95 Regret | False Positive Cost | Release Mismatch | Unsafe Rate |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for strategy_id in comparison["strategy_order"]:
        row = comparison["metrics_by_strategy"][strategy_id]
        lines.append(
            f"| `{strategy_id}` | `{row['joint_action_accuracy']}` | `{row['mean_reward_regret']}` | "
            f"`{row['p95_reward_regret']}` | `{row['false_positive_action_cost']}` | "
            f"`{row['release_gate_mismatch_rate']}` | `{row['unsafe_action_rate']}` |"
        )
    lines.extend(["", "### Baseline Delta Summary", ""])
    for key, value in comparison["delta_summary"].items():
        lines.append(f"- {key}：`{value}`")
    lines.extend(["", "### Baseline Boundary", ""])
    for item in contract["cannot_do"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Agent52 Replay Export Work Package", ""])
    lines.append(f"- work_package_id：`{export_manifest['work_package_id']}`")
    lines.append(f"- export_status：`{export_manifest['export_status']}`")
    lines.append(f"- all_rows_field_origin：`{export_manifest['all_rows_field_origin']}`")
    lines.append(f"- can_route_to_r8p_candidate_rows：`{export_manifest['can_route_to_r8p_candidate_rows']}`")
    lines.append(f"- can_create_field_evidence_by_export_only：`{export_manifest['can_create_field_evidence_by_export_only']}`")
    lines.append(f"- expected_output_files：`{export_manifest['expected_output_files']}`")
    lines.append(f"- failure_boundary：{export_manifest['failure_boundary']}")
    lines.extend(["", "## Agent51 Catalyst Proxy Context", ""])
    lines.append(f"- summary_status：`{catalyst['summary_status']}`")
    lines.append(f"- ready_for_agent51_validation：`{catalyst['ready_for_agent51_validation']}`")
    lines.append(f"- field_validation_pass：`{catalyst['field_validation_pass']}`")
    lines.append(f"- scoreable_batch_count：`{catalyst['scoreable_batch_count']}`")
    lines.append(f"- guardrail_mode：`{catalyst['guardrail_mode']}`")
    lines.extend(["", "## Pressure/Headloss Replay Boundary", ""])
    lines.append(f"- pool_status：`{pressure['pool_status']}`")
    lines.append(f"- candidate_ids：`{pressure['candidate_ids']}`")
    lines.append(f"- consumed_by_agent52：`{pressure['consumed_by_agent52']}`")
    lines.append(f"- field_validation_required：`{pressure['field_validation_required']}`")
    lines.append(f"- control_boundary：{pressure['control_boundary']}")
    lines.extend(["", "## 结论", ""])
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    return "\n".join(lines)


def _report_md(report, generated_files: dict[str, str]) -> str:
    readiness = report.metrics["readiness"]
    metrics = report.metrics["offline_evaluation_metrics"]
    catalyst = report.metrics["catalyst_proxy_context"]
    pressure = report.metrics["pressure_headloss_context"]
    contract = report.metrics["control_baseline_contract"]
    export_manifest = _agent52_replay_export_payload(report)["manifest"]
    lines = [
        "# Agent 52 多设施 Replay 离线评估报告",
        "",
        f"- summary: {report.summary}",
        f"- replay_evaluation_status: `{readiness['replay_evaluation_status']}`",
        f"- joint_action_accuracy: `{metrics['joint_action_accuracy']}`",
        f"- mean_reward_regret: `{metrics['mean_reward_regret']}`",
        f"- guardrail_aware_joint_action_accuracy: `{metrics['guardrail_aware_joint_action_accuracy']}`",
        f"- guardrail_aware_mean_reward_regret: `{metrics['guardrail_aware_mean_reward_regret']}`",
        f"- catalyst_proxy_summary_status: `{catalyst['summary_status']}`",
        f"- catalyst_guardrail_mode: `{catalyst['guardrail_mode']}`",
        f"- pressure_headloss_boundary_consumed: `{pressure['consumed_by_agent52']}`",
        f"- pressure_headloss_candidate_count: `{pressure['candidate_count']}`",
        f"- pressure_headloss_field_validation_required: `{pressure['field_validation_required']}`",
        f"- control_policy_baseline_comparison_status: `{contract['comparison_status']}`",
        f"- control_policy_baseline_strategy_count: `{contract['baseline_strategy_count']}`",
        f"- agent52_replay_export_status: `{export_manifest['export_status']}`",
        f"- agent52_replay_export_row_count: `{export_manifest['row_count']}`",
        f"- can_write_to_actuator: `{readiness['can_write_to_actuator']}`",
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
    manifest["status"] = "R8u-61 已让 Agent52 输出 replay export work package，并保持 synthetic/field 与 actuator/release gate 边界"
    manifest["multi_facility_replay_evaluation"] = relative_generated
    manifest["latest_agent52_guardrail_aware_replay_status"] = "R8u61_replay_export_work_package_ready_synthetic_only"
    manifest["latest_agent52_control_baseline_strategy_count"] = 6
    manifest["latest_agent52_control_baseline_boundary"] = "baseline comparison can update reward-prior and experiment design only; field replay/operator/release/actuator gates still block deployment"
    manifest["latest_agent52_replay_export_status"] = "agent52_replay_export_ready_synthetic_only"
    manifest["latest_agent52_replay_export_row_count"] = 6
    manifest["latest_agent52_replay_export_boundary"] = "Agent52 export supplies replay-origin action/conflict rows only; synthetic rows cannot become field evidence and no export can write actuator/release gates."
    manifest["next_stage"] = "若无真实包，继续补 Agent49/52 replay export 的 field-origin package 路由与 Agent48 topology-aware placement；所有 R8u-61 改善仍为 synthetic replay，不得写执行器或 release gate"
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
