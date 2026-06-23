from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.grey_box_dynamic_latency_agent import GreyBoxDynamicLatencyAgent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
AGENT39_METRICS = PROJECT_ROOT / "outputs" / "soft_sensor_training" / "soft_sensor_conformal_metrics.json"
AGENT27_REPORT = PROJECT_ROOT / "outputs" / "agent27_recovery_execution_replay" / "agent27_report.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent40_grey_box_dynamic_latency"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables"
LATENCY_METRICS_PATH = PROJECT_ROOT / "outputs" / "grey_box_dynamic_latency" / "latency_budget_metrics.json"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    LATENCY_METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    conformal = _read_conformal_readiness()
    campaign_context = _read_campaign_context()
    report = GreyBoxDynamicLatencyAgent(
        evidence_stage="synthetic_replay",
        field_timestamp_coverage=0.0,
        conformal_readiness=conformal,
        campaign_context=campaign_context,
    ).run([])
    generated_files = {
        "grey_box_dynamic_latency": str(DELIVERABLES_DIR / "grey_box_dynamic_latency.md"),
        "agent40_report": str(OUT_DIR / "agent40_report.md"),
        "latency_budget_metrics": str(LATENCY_METRICS_PATH),
    }

    (DELIVERABLES_DIR / "grey_box_dynamic_latency.md").write_text(_latency_md(report), encoding="utf-8")
    LATENCY_METRICS_PATH.write_text(
        json.dumps(
            {
                "evidence_stage": report.metrics["evidence_stage"],
                "field_timestamp_coverage": report.metrics["field_timestamp_coverage"],
                "method_contract": report.metrics["method_contract"],
                "latency_budget": report.metrics["latency_budget"],
                "readiness": report.metrics["readiness"],
                "conformal_readiness": report.metrics["conformal_readiness"],
                "campaign_context": report.metrics["campaign_context"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    payload = {
        "grey_box_dynamic_latency": {
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
    (OUT_DIR / "agent40_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "agent40_report.md").write_text(_report_md(report, generated_files), encoding="utf-8")
    _update_manifest(generated_files)

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent40_report.md'}")
    for key, path in generated_files.items():
        print(f"{key}: {path}")


def _read_conformal_readiness() -> dict[str, object]:
    if not AGENT39_METRICS.exists():
        return {}
    payload = json.loads(AGENT39_METRICS.read_text(encoding="utf-8"))
    readiness = payload.get("readiness", {})
    return readiness if isinstance(readiness, dict) else {}


def _read_campaign_context() -> dict[str, object]:
    if not AGENT27_REPORT.exists():
        return {}
    payload = json.loads(AGENT27_REPORT.read_text(encoding="utf-8"))
    replay = payload.get("recovery_execution_replay", {})
    if not isinstance(replay, dict):
        return {}
    metrics = replay.get("metrics", {})
    if not isinstance(metrics, dict):
        return {}
    comparison = metrics.get("comparison", {})
    with_strategy = metrics.get("with_recovery_strategy", {})
    return {
        "source_agent": "agent27_recovery_execution_replay",
        "comparison": comparison if isinstance(comparison, dict) else {},
        "with_recovery_strategy": with_strategy if isinstance(with_strategy, dict) else {},
    }


def _latency_md(report) -> str:
    readiness = report.metrics["readiness"]
    contract = report.metrics["method_contract"]
    lines = [
        "# 灰箱动态延迟审计",
        "",
        f"- latency_status：`{readiness['latency_status']}`",
        f"- latency_readiness_score：`{readiness['latency_readiness_score']}`",
        f"- evidence_stage：`{report.metrics['evidence_stage']}`",
        f"- field_timestamp_coverage：`{report.metrics['field_timestamp_coverage']}`",
        f"- latency_budget_violation_rate：`{readiness['latency_budget_violation_rate']}`",
        f"- minimum_evidence_margin_min：`{readiness['minimum_evidence_margin_min']}`",
        f"- minimum_action_margin_min：`{readiness['minimum_action_margin_min']}`",
        f"- release_gate_can_use_latency_budget：`{readiness['release_gate_can_use_latency_budget']}`",
        "",
        "## 方法契约",
        "",
        f"- upgrade_id：`{contract['upgrade_id']}`",
        f"- borrowed_from：`{contract['borrowed_from']}`",
        f"- 现实映射：{contract['reality_mapping']}",
        f"- 数据需求：{', '.join(contract['data_needs'])}",
        f"- 评价指标：{', '.join(contract['evaluation_metrics'])}",
        f"- 失败边界：{contract['failure_boundary']}",
        "",
        "## 场景延迟预算",
        "",
        "| 场景 | 状态 | 行动余量 min | 证据余量 min | 循环时间信用 min | 慢证据延迟 min | 失败边界 |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in report.metrics["latency_budget"]:
        lines.append(
            "| "
            f"`{item['scenario']}` | `{item['latency_status']}` | "
            f"{item['action_latency_margin_min']} | {item['evidence_margin_min']} | "
            f"{item['loop_time_credit_min']} | {item['release_evidence_latency_min']} | "
            f"{item['failure_boundary']} |"
        )
    lines.extend(["", "## 结论", ""])
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    return "\n".join(lines)


def _report_md(report, generated_files: dict[str, str]) -> str:
    readiness = report.metrics["readiness"]
    lines = [
        "# Agent 40 灰箱动态延迟审计报告",
        "",
        f"- summary: {report.summary}",
        f"- latency_status: `{readiness['latency_status']}`",
        f"- latency_budget_violation_rate: `{readiness['latency_budget_violation_rate']}`",
        f"- release_gate_can_use_latency_budget: `{readiness['release_gate_can_use_latency_budget']}`",
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
    manifest["status"] = "灰箱动态延迟审计层已生成"
    manifest["grey_box_dynamic_latency"] = relative_generated
    manifest["next_stage"] = "采集现场 timestamped campaign replay，校准采样/检测/执行器/回流延迟后再接入 release gate"
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
