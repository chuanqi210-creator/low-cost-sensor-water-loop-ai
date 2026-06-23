from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.catalyst_activity_proxy_agent import CatalystActivityProxyAgent
from water_ai.agents.sensor_network_sparse_placement_agent import SensorNetworkSparsePlacementAgent
from water_ai.catalyst_proxy_field_holdout import build_catalyst_proxy_field_holdout_summary


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
SPARSE_METRICS_PATH = PROJECT_ROOT / "outputs" / "sensor_network_sparse_placement" / "sparse_placement_metrics.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent51_catalyst_activity_proxy"
METRICS_DIR = PROJECT_ROOT / "outputs" / "catalyst_activity_proxy"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables"
METRICS_PATH = METRICS_DIR / "catalyst_activity_proxy_metrics.json"
FIELD_PACKAGE_TEMPLATE_DIR = PROJECT_ROOT / "outputs" / "field_replay_import" / "real_field_package_template"
FIELD_HOLDOUT_SUMMARY_PATH = METRICS_DIR / "field_proxy_holdout_summary.json"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    sparse_metrics = _load_sparse_metrics()
    field_holdout_summary = _load_field_holdout_summary()
    report = CatalystActivityProxyAgent(
        sparse_placement_metrics=sparse_metrics,
        field_proxy_holdout_summary=field_holdout_summary,
    ).run([])
    generated_files = {
        "catalyst_activity_proxy": str(DELIVERABLES_DIR / "catalyst_activity_proxy.md"),
        "agent51_report": str(OUT_DIR / "agent51_report.md"),
        "catalyst_activity_proxy_metrics": str(METRICS_PATH),
        "field_proxy_holdout_summary": str(FIELD_HOLDOUT_SUMMARY_PATH),
    }

    (DELIVERABLES_DIR / "catalyst_activity_proxy.md").write_text(_deliverable_md(report), encoding="utf-8")
    FIELD_HOLDOUT_SUMMARY_PATH.write_text(
        json.dumps(field_holdout_summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    METRICS_PATH.write_text(
        json.dumps(
            {
                "method_contract": report.metrics["method_contract"],
                "sparse_context": report.metrics["sparse_context"],
                "proxy_catalog": report.metrics["proxy_catalog"],
                "proxy_feature_table": report.metrics["proxy_feature_table"],
                "proxy_metrics": report.metrics["proxy_metrics"],
                "field_proxy_holdout_summary": report.metrics["field_proxy_holdout_summary"],
                "weak_axis_repair_plan": report.metrics["weak_axis_repair_plan"],
                "readiness": report.metrics["readiness"],
                "agent49_interface": report.metrics["agent49_interface"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    payload = {
        "catalyst_activity_proxy": {
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
    (OUT_DIR / "agent51_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "agent51_report.md").write_text(_report_md(report, generated_files), encoding="utf-8")
    _update_manifest(generated_files)

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent51_report.md'}")
    for key, path in generated_files.items():
        print(f"{key}: {path}")


def _load_sparse_metrics() -> dict[str, object]:
    if SPARSE_METRICS_PATH.exists():
        return json.loads(SPARSE_METRICS_PATH.read_text(encoding="utf-8"))
    report = SensorNetworkSparsePlacementAgent(max_sensors=6, budget_limit=5.8).run([])
    return {
        "selected_sensor_plan": report.metrics["selected_sensor_plan"],
        "coverage": report.metrics["coverage"],
        "readiness": report.metrics["readiness"],
        "selected_strategy": report.metrics["selected_strategy"],
    }


def _load_field_holdout_summary() -> dict[str, object]:
    if not FIELD_PACKAGE_TEMPLATE_DIR.exists():
        return {}
    return build_catalyst_proxy_field_holdout_summary(FIELD_PACKAGE_TEMPLATE_DIR)


def _deliverable_md(report) -> str:
    readiness = report.metrics["readiness"]
    proxy_metrics = report.metrics["proxy_metrics"]
    repair = report.metrics["weak_axis_repair_plan"]
    interface = report.metrics["agent49_interface"]
    holdout = report.metrics.get("field_proxy_holdout_summary", {})
    holdout = holdout if isinstance(holdout, dict) else {}
    lines = [
        "# 催化剂活性代理观测设计",
        "",
        f"- catalyst_proxy_status：`{readiness['catalyst_proxy_status']}`",
        f"- catalyst_proxy_score：`{readiness['catalyst_proxy_score']}`",
        f"- current_proxy_observability：`{proxy_metrics['current_proxy_observability']}`",
        f"- proxy_observability_after_recommended_patch：`{proxy_metrics['proxy_observability_after_recommended_patch']}`",
        f"- weak_state_coverage_after_proxy_design：`{proxy_metrics['weak_state_coverage_after_proxy_design']}`",
        f"- weak_axis_repair_status：`{repair['repair_status']}`",
        f"- repair_score：`{repair['repair_score']}`",
        f"- can_relax_agent49_catalyst_uncertainty_block：`{interface['can_relax_catalyst_uncertainty_block']}`",
        f"- field_proxy_holdout_summary_status：`{holdout.get('field_proxy_holdout_summary_status', 'not_supplied')}`",
        f"- field_proxy_holdout_scoreable_batch_count：`{holdout.get('scoreable_batch_count', 0)}`",
        "",
        "## Proxy Catalog",
        "",
        "| Proxy | Current Support | Missing Signals | Recommended Patch | Formula |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in report.metrics["proxy_catalog"]:
        lines.append(
            f"| `{item['proxy_id']}` {item['proxy_name']} | `{item['current_support_score']}` | "
            f"{item['missing_signals']} | {item['recommended_patch']} | `{item['formula']}` |"
        )
    lines.extend(
        [
            "",
            "## Synthetic Proxy Cases",
            "",
            "| Case | Scenario | Proxy Score | Label | Error |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in report.metrics["proxy_feature_table"]:
        lines.append(
            f"| `{row['case_id']}` | {row['scenario']} | `{row['catalyst_activity_proxy_score']}` | "
            f"`{row['catalyst_activity_label']}` | `{row['absolute_proxy_error']}` |"
        )
    lines.extend(
        [
            "",
            "## Agent48 Weak Axis Repair Plan",
            "",
            f"- target_axis：`{repair['target_axis']}`",
            f"- current_axis_coverage：`{repair['current_axis_coverage']}`",
            f"- target_axis_coverage：`{repair['target_axis_coverage']}`",
            f"- agent48_best_available_candidate：`{repair['agent48_best_available_candidate']}`",
            f"- recoverable_by_current_candidate_pool：`{repair['recoverable_by_current_candidate_pool']}`",
            f"- proxy_projected_axis_coverage：`{repair['proxy_projected_axis_coverage']}`",
            "",
            "| Patch | Class | Priority | Supports | Why |",
            "| --- | --- | ---: | --- | --- |",
        ]
    )
    for patch in repair["prioritized_proxy_patches"]:
        lines.append(
            f"| `{patch['patch_signal']}` | `{patch['patch_class']}` | `{patch['repair_priority_score']}` | "
            f"{patch['supports_proxy_ids']} | {patch['why_needed']} |"
        )
    lines.extend(["", "## Field Repair Evidence Requirements", ""])
    for requirement in repair["field_repair_evidence_requirements"]:
        lines.append(
            f"- `{requirement['requirement_id']}`：table=`{requirement['required_table']}`，"
            f"fields={requirement['required_fields']}，minimum={requirement['minimum_evidence']}"
        )
    lines.extend(["", "## Field Proxy Holdout Summary", ""])
    if holdout:
        lines.extend(
            [
                f"- status：`{holdout.get('field_proxy_holdout_summary_status')}`",
                f"- matched_batch_count：`{holdout.get('matched_batch_count')}`",
                f"- scoreable_batch_count：`{holdout.get('scoreable_batch_count')}`",
                f"- field_validation_metrics：`{holdout.get('field_validation_metrics')}`",
                f"- boundary：{holdout.get('boundary')}",
            ]
        )
    else:
        lines.append("- 当前未提供 field package，Agent51 仍只输出 synthetic proxy design 和 R7j 数据需求。")
    lines.extend(["", "## Agent49 Interface", ""])
    lines.append(f"- policy_effect：`{interface['policy_effect']}`")
    lines.append(f"- boundary：{interface['boundary']}")
    lines.extend(["", "## 结论", ""])
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    return "\n".join(lines)


def _report_md(report, generated_files: dict[str, str]) -> str:
    readiness = report.metrics["readiness"]
    proxy_metrics = report.metrics["proxy_metrics"]
    repair = report.metrics["weak_axis_repair_plan"]
    holdout = report.metrics.get("field_proxy_holdout_summary", {})
    holdout = holdout if isinstance(holdout, dict) else {}
    lines = [
        "# Agent 51 催化剂活性代理观测报告",
        "",
        f"- summary: {report.summary}",
        f"- catalyst_proxy_status: `{readiness['catalyst_proxy_status']}`",
        f"- proxy_observability_after_recommended_patch: `{proxy_metrics['proxy_observability_after_recommended_patch']}`",
        f"- weak_state_coverage_after_proxy_design: `{proxy_metrics['weak_state_coverage_after_proxy_design']}`",
        f"- weak_axis_repair_status: `{repair['repair_status']}`",
        f"- repair_score: `{repair['repair_score']}`",
        f"- field_proxy_holdout_summary_status: `{holdout.get('field_proxy_holdout_summary_status', 'not_supplied')}`",
        f"- field_proxy_holdout_scoreable_batch_count: `{holdout.get('scoreable_batch_count', 0)}`",
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
    manifest["status"] = "催化剂活性代理观测层已生成"
    manifest["catalyst_activity_proxy"] = relative_generated
    manifest["next_stage"] = "按低摩擦阶段边界运行 Agent50；Agent51 已形成 catalyst_activity synthetic proxy design，下一步需要 field_proxy_holdout 或转入 Agent49 replay-ready 离线评估"
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
