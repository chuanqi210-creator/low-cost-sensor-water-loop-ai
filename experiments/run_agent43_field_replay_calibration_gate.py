from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.field_replay_calibration_gate_agent import FieldReplayCalibrationGateAgent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
AGENT42_REPORT = PROJECT_ROOT / "outputs" / "agent42_timestamped_campaign_replay" / "agent42_report.json"
AGENT41_METRICS = PROJECT_ROOT / "outputs" / "matrix_shock_fast_proxy" / "fast_proxy_metrics.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent43_field_replay_calibration_gate"
GATE_DIR = PROJECT_ROOT / "outputs" / "field_replay_calibration_gate"
GATE_METRICS = GATE_DIR / "g6_p6_gate_metrics.json"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    GATE_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    timestamped_metrics = _read_agent42_metrics()
    matrix_metrics = _read_json(AGENT41_METRICS)
    report = FieldReplayCalibrationGateAgent(
        timestamped_replay_metrics=timestamped_metrics,
        matrix_fast_proxy_metrics=matrix_metrics,
        minimum_proxy_events=12,
    ).run([])
    generated_files = {
        "field_replay_calibration_gate": str(DELIVERABLES_DIR / "field_replay_calibration_gate.md"),
        "agent43_report": str(OUT_DIR / "agent43_report.md"),
        "g6_p6_gate_metrics": str(GATE_METRICS),
    }
    (DELIVERABLES_DIR / "field_replay_calibration_gate.md").write_text(
        _deliverable_md(report),
        encoding="utf-8",
    )
    GATE_METRICS.write_text(
        json.dumps(
            {
                "method_contract": report.metrics["method_contract"],
                "thresholds": report.metrics["thresholds"],
                "timestamped_replay": report.metrics["timestamped_replay"],
                "gate_results": report.metrics["gate_results"],
                "writeback_policy": report.metrics["writeback_policy"],
                "readiness": report.metrics["readiness"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    payload = {
        "source_agent42_report": str(AGENT42_REPORT),
        "source_agent41_metrics": str(AGENT41_METRICS),
        "field_replay_calibration_gate": {
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
    (OUT_DIR / "agent43_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "agent43_report.md").write_text(_report_md(report, generated_files), encoding="utf-8")
    _update_manifest(generated_files)

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent43_report.md'}")
    for key, path in generated_files.items():
        print(f"{key}: {path}")


def _read_agent42_metrics() -> dict[str, object]:
    payload = _read_json(AGENT42_REPORT)
    replay = payload.get("timestamped_campaign_replay", {})
    if not isinstance(replay, dict):
        return {}
    metrics = replay.get("metrics", {})
    return metrics if isinstance(metrics, dict) else {}


def _read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _deliverable_md(report) -> str:
    readiness = report.metrics["readiness"]
    writeback = report.metrics["writeback_policy"]
    contract = report.metrics["method_contract"]
    lines = [
        "# Field Replay Calibration Gate",
        "",
        f"- field_replay_gate_status：`{readiness['field_replay_gate_status']}`",
        f"- field_replay_gate_score：`{readiness['field_replay_gate_score']}`",
        f"- accepted_gates：`{readiness['accepted_gate_count']}/{readiness['total_gate_count']}`",
        f"- can_write_to_protective_control：`{writeback['can_write_to_protective_control']}`",
        f"- can_write_to_release_gate：`{writeback['can_write_to_release_gate']}`",
        f"- writeback_mode：`{writeback['writeback_mode']}`",
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
        "## G6 验收门",
        "",
        "| Gate | 通过 | 规则 | 证据 |",
        "| --- | --- | --- | --- |",
    ]
    for gate in report.metrics["gate_results"]["gates"]:
        evidence = json.dumps(gate["evidence"], ensure_ascii=False)
        lines.append(f"| `{gate['gate_id']}` | `{gate['accepted']}` | {gate['rule']} | `{evidence}` |")
    lines.extend(["", "## 写回边界", ""])
    for key, value in writeback.items():
        lines.append(f"- {key}：`{value}`")
    lines.extend(["", "## 结论", ""])
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    return "\n".join(lines)


def _report_md(report, generated_files: dict[str, str]) -> str:
    readiness = report.metrics["readiness"]
    writeback = report.metrics["writeback_policy"]
    lines = [
        "# Agent 43 Field Replay Calibration Gate 报告",
        "",
        f"- summary: {report.summary}",
        f"- field_replay_gate_status: `{readiness['field_replay_gate_status']}`",
        f"- accepted_gates: `{readiness['accepted_gate_count']}/{readiness['total_gate_count']}`",
        f"- can_write_to_protective_control: `{writeback['can_write_to_protective_control']}`",
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
    manifest["status"] = "field replay calibration gate 已生成"
    manifest["field_replay_calibration_gate"] = relative_generated
    manifest["next_stage"] = "导入真实 field-labeled timestamped replay，通过 G6/P6 后再把 matrix_shock 快代理写入保护性控制"
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
