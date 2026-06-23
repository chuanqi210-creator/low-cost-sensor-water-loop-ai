from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.field_replay_evidence_chain_agent import FieldReplayEvidenceChainAgent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
AGENT44_REPORT = PROJECT_ROOT / "outputs" / "agent44_field_replay_import" / "agent44_report.json"
AGENT41_METRICS = PROJECT_ROOT / "outputs" / "matrix_shock_fast_proxy" / "fast_proxy_metrics.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent45_field_replay_evidence_chain"
CHAIN_DIR = PROJECT_ROOT / "outputs" / "field_replay_evidence_chain"
CHAIN_METRICS = CHAIN_DIR / "evidence_chain_metrics.json"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CHAIN_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    import_metrics = _read_agent44_metrics()
    matrix_metrics = _read_json(AGENT41_METRICS)
    report = FieldReplayEvidenceChainAgent(
        import_metrics=import_metrics,
        matrix_fast_proxy_metrics=matrix_metrics,
        minimum_proxy_events=12,
    ).run([])
    generated_files = {
        "field_replay_evidence_chain": str(DELIVERABLES_DIR / "field_replay_evidence_chain.md"),
        "agent45_report": str(OUT_DIR / "agent45_report.md"),
        "evidence_chain_metrics": str(CHAIN_METRICS),
    }
    (DELIVERABLES_DIR / "field_replay_evidence_chain.md").write_text(
        _deliverable_md(report, generated_files),
        encoding="utf-8",
    )
    CHAIN_METRICS.write_text(
        json.dumps(
            {
                "method_contract": report.metrics["method_contract"],
                "import_stage": _without_normalized_rows(report.metrics["import_stage"]),
                "timestamped_replay_stage": report.metrics["timestamped_replay_stage"],
                "g6_stage": report.metrics["g6_stage"],
                "writeback_candidate": report.metrics["writeback_candidate"],
                "readiness": report.metrics["readiness"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    payload = {
        "source_agent44_report": str(AGENT44_REPORT),
        "source_agent41_metrics": str(AGENT41_METRICS),
        "field_replay_evidence_chain": {
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
    (OUT_DIR / "agent45_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "agent45_report.md").write_text(_report_md(report, generated_files), encoding="utf-8")
    _update_manifest(generated_files)

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent45_report.md'}")
    for key, path in generated_files.items():
        print(f"{key}: {path}")


def _read_agent44_metrics() -> dict[str, object]:
    payload = _read_json(AGENT44_REPORT)
    import_payload = payload.get("field_replay_import", {})
    if not isinstance(import_payload, dict):
        return {}
    metrics = import_payload.get("metrics", {})
    return metrics if isinstance(metrics, dict) else {}


def _read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _without_normalized_rows(import_stage: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in import_stage.items() if key != "normalized_datasets"}


def _deliverable_md(report, generated_files: dict[str, str]) -> str:
    readiness = report.metrics["readiness"]
    import_stage = _without_normalized_rows(report.metrics["import_stage"])
    timestamp_stage = report.metrics["timestamped_replay_stage"]
    g6_stage = report.metrics["g6_stage"]
    writeback = report.metrics["writeback_candidate"]
    contract = report.metrics["method_contract"]
    lines = [
        "# Field Replay Evidence Chain",
        "",
        f"- field_replay_evidence_chain_status：`{readiness['field_replay_evidence_chain_status']}`",
        f"- field_replay_evidence_chain_score：`{readiness['field_replay_evidence_chain_score']}`",
        f"- import_ready：`{readiness['import_ready']}`",
        f"- timestamped_replay_ready：`{readiness['timestamped_replay_ready']}`",
        f"- g6_ready：`{readiness['g6_ready']}`",
        f"- can_emit_protective_writeback_candidate：`{writeback['can_emit_protective_writeback_candidate']}`",
        f"- can_write_to_release_gate：`{writeback['can_write_to_release_gate']}`",
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
        "## 三段证据链",
        "",
        f"- Agent44 import_stage：`{import_stage}`",
        f"- Agent42 timestamped_replay_stage：`{timestamp_stage}`",
        f"- Agent43 g6_stage：`{g6_stage}`",
        "",
        "## 生成文件",
        "",
    ]
    for key, path in generated_files.items():
        lines.append(f"- {key}: `{path}`")
    lines.extend(["", "## 结论", ""])
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    return "\n".join(lines)


def _report_md(report, generated_files: dict[str, str]) -> str:
    readiness = report.metrics["readiness"]
    writeback = report.metrics["writeback_candidate"]
    lines = [
        "# Agent 45 Field Replay Evidence Chain 报告",
        "",
        f"- summary: {report.summary}",
        f"- field_replay_evidence_chain_status: `{readiness['field_replay_evidence_chain_status']}`",
        f"- can_emit_protective_writeback_candidate: `{writeback['can_emit_protective_writeback_candidate']}`",
        f"- can_write_to_release_gate: `{writeback['can_write_to_release_gate']}`",
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
    manifest["status"] = "field replay evidence chain 已生成"
    manifest["field_replay_evidence_chain"] = relative_generated
    manifest["next_stage"] = "导入真实 field replay 包，通过 Agent44->Agent42->Agent43->Agent45 证据链后形成保护性写回候选"
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
