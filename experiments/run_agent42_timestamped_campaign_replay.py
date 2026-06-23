from __future__ import annotations

import csv
import json
from pathlib import Path

from water_ai.agents.timestamped_campaign_replay_agent import TimestampedCampaignReplayAgent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
AGENT41_METRICS = PROJECT_ROOT / "outputs" / "matrix_shock_fast_proxy" / "fast_proxy_metrics.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent42_timestamped_campaign_replay"
REPLAY_DIR = PROJECT_ROOT / "outputs" / "timestamped_campaign_replay"
TEMPLATE_DIR = REPLAY_DIR / "templates"
SAMPLE_DIR = REPLAY_DIR / "synthetic_timestamped_replay"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    datasets = _synthetic_timestamped_package()
    report = TimestampedCampaignReplayAgent(
        datasets=datasets,
        data_origin="synthetic",
        minimum_proxy_events=12,
    ).run([])
    generated_files = {
        "timestamped_campaign_replay_schema": str(DELIVERABLES_DIR / "timestamped_campaign_replay_schema.md"),
        "agent42_report": str(OUT_DIR / "agent42_report.md"),
        "timestamped_replay_schema_json": str(REPLAY_DIR / "timestamped_replay_schema.json"),
        "timestamped_replay_templates": str(TEMPLATE_DIR),
        "synthetic_timestamped_replay_package": str(SAMPLE_DIR),
    }
    _write_schema_and_templates(report)
    _write_sample_package(datasets, report.metrics["template_headers"])
    (DELIVERABLES_DIR / "timestamped_campaign_replay_schema.md").write_text(
        _schema_md(report, generated_files),
        encoding="utf-8",
    )
    payload = {
        "source_agent41_metrics": str(AGENT41_METRICS),
        "timestamped_campaign_replay": {
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
    (OUT_DIR / "agent42_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "agent42_report.md").write_text(_report_md(report, generated_files), encoding="utf-8")
    _update_manifest(generated_files)

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent42_report.md'}")
    for key, path in generated_files.items():
        print(f"{key}: {path}")


def _synthetic_timestamped_package() -> dict[str, list[dict[str, object]]]:
    scenarios = [
        ("matrix_shock", True, True, 0.559, 0.633, 0.0),
        ("matrix_shock", True, True, 0.571, 0.641, 0.0),
        ("matrix_shock", True, True, 0.552, 0.619, 0.0),
        ("matrix_shock", True, True, 0.601, 0.671, 0.0),
        ("matrix_shock", True, True, 0.583, 0.652, 0.0),
        ("matrix_shock", True, True, 0.564, 0.635, 0.0),
        ("clean_release", False, False, 0.008, 0.009, 0.0),
        ("clean_release", False, False, 0.012, 0.015, 0.0),
        ("oxidant_limitation", False, False, 0.149, 0.035, 0.0),
        ("oxidant_limitation", False, False, 0.161, 0.044, 0.0),
        ("sensor_faults", False, False, 0.218, 0.201, 0.0),
        ("clean_release", False, False, 0.018, 0.017, 0.0),
    ]
    sensor_rows: list[dict[str, object]] = []
    lab_rows: list[dict[str, object]] = []
    operation_rows: list[dict[str, object]] = []
    proxy_rows: list[dict[str, object]] = []
    pressure_rows: list[dict[str, object]] = []
    for index, (scenario, triggered, label, proxy_score, guard_score, false_cost) in enumerate(scenarios, start=1):
        batch_id = f"TS{index:03d}"
        event_time = 10 + index % 4
        sample_time = 18 + index % 3
        result_time = 92 + index % 9
        command_time = event_time if triggered else 38 + index
        effect_time = command_time + (6 if triggered else 10)
        action_id = "switch_or_pretreat" if triggered else "standard_monitoring"
        sensor_rows.extend(_sensor_rows(batch_id, scenario))
        hydraulic_anomaly = scenario in {"matrix_shock", "sensor_faults"}
        lab_rows.append(
            {
                "batch_id": batch_id,
                "sample_time_min": sample_time,
                "result_time_min": result_time,
                "analyte": "matrix_shock_label",
                "value": 1.0 if label else 0.0,
                "qa_flag": "synthetic_pass",
                "proxy_holdout_label": True,
                "pressure_headloss_proxy_label": hydraulic_anomaly,
            }
        )
        operation_rows.append(
            {
                "campaign_id": "synthetic_timestamped_campaign",
                "batch_id": batch_id,
                "action_id": action_id,
                "command_time_min": command_time,
                "effect_time_min": effect_time,
                "start_min": effect_time,
                "end_min": effect_time + (45 if triggered else 20),
                "release_policy": "block_release_until_lab_and_field_conformal_calibration" if triggered else "standard_release_gate",
                "recycle_ratio": 0.25 if triggered else 0.0,
                "tank_storage_margin": 0.42 if triggered else 0.67,
                "actuator_latency_p90": effect_time - command_time,
                "pump_valve_result": "ok",
                "hold_time_min": 45 if triggered else 20,
                "regeneration_event": False,
                "bed_id": "BED_A",
                "pressure_headloss_review_required": hydraulic_anomaly,
            }
        )
        pressure_rows.append(
            _pressure_headloss_event(
                batch_id=batch_id,
                event_time=event_time + 4,
                matched_sample_time=sample_time,
                scenario=scenario,
                anomaly=hydraulic_anomaly,
            )
        )
        proxy_rows.append(
            {
                "campaign_id": "synthetic_timestamped_campaign",
                "batch_id": batch_id,
                "event_time_min": event_time,
                "proxy_score": proxy_score,
                "specificity_guard_score": guard_score,
                "protective_triggered": triggered,
                "triggered_action_id": action_id if triggered else "none",
                "field_label_matrix_shock": label,
                "lab_label_time_min": result_time,
                "false_positive_cost_index": false_cost,
            }
        )
    return {
        "sensor_timeseries": sensor_rows,
        "offline_lab_results": lab_rows,
        "campaign_operation_log": operation_rows,
        "pressure_headloss_event_log": pressure_rows,
        "fast_proxy_event_log": proxy_rows,
    }


def _sensor_rows(batch_id: str, scenario: str) -> list[dict[str, object]]:
    if scenario == "matrix_shock":
        ec, turbidity, uv, ph, orp, pressure, headloss = 2990.0, 39.0, 0.85, 7.75, 512.0, 6.6, 8.25
    elif scenario == "oxidant_limitation":
        ec, turbidity, uv, ph, orp, pressure, headloss = 1280.0, 19.0, 0.82, 7.1, 278.0, 4.4, 5.5
    elif scenario == "sensor_faults":
        ec, turbidity, uv, ph, orp, pressure, headloss = 1680.0, 24.0, 0.62, 7.4, 390.0, 6.1, 7.65
    else:
        ec, turbidity, uv, ph, orp, pressure, headloss = 1100.0, 7.0, 0.30, 7.1, 635.0, 3.4, 4.25
    return [
        {
            "batch_id": batch_id,
            "timestamp_min": timestamp,
            "EC_uScm": round(ec + timestamp * 0.5, 3),
            "turbidity_NTU": round(max(0.0, turbidity - timestamp * 0.08), 3),
            "UV254_abs": round(uv, 4),
            "pH": round(ph, 3),
            "ORP_mV": round(orp, 3),
            "flow_Lmin": 1.1,
            "pressure_drop_kPa": round(pressure + timestamp * 0.015, 3),
            "headloss_kPa_per_m": round(headloss + timestamp * 0.018, 3),
            "bed_inlet_pressure_kPa": round(102.0 + pressure / 2, 3),
            "bed_outlet_pressure_kPa": round(102.0 - pressure / 2, 3),
        }
        for timestamp in (0, 5, 10, 15, 20)
    ]


def _pressure_headloss_event(
    *,
    batch_id: str,
    event_time: int,
    matched_sample_time: int,
    scenario: str,
    anomaly: bool,
) -> dict[str, object]:
    pressure_drop = 6.7 if anomaly else 3.7
    if scenario == "oxidant_limitation":
        pressure_drop = 4.4
    headloss = pressure_drop / 0.8
    return {
        "campaign_id": "synthetic_timestamped_campaign",
        "batch_id": batch_id,
        "event_time_min": event_time,
        "bed_id": "BED_A",
        "pressure_drop_kPa": round(pressure_drop, 3),
        "headloss_kPa_per_m": round(headloss, 3),
        "flow_Lmin": 1.1,
        "matched_lab_sample_time_min": matched_sample_time,
        "regeneration_event": False,
        "hydraulic_anomaly_label": anomaly,
        "flow_normalized_pressure_residual": round(max(0.0, pressure_drop - 3.2) / 1.1, 3),
        "expected_clean_bed_pressure_drop_kPa": 3.2,
        "operator_review_required": anomaly,
    }


def _write_schema_and_templates(report) -> None:
    (REPLAY_DIR / "timestamped_replay_schema.json").write_text(
        json.dumps(report.metrics["replay_schema_contract"], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    for table, headers in report.metrics["template_headers"].items():
        with (TEMPLATE_DIR / f"{table}.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=headers)
            writer.writeheader()


def _write_sample_package(datasets: dict[str, list[dict[str, object]]], headers: dict[str, list[str]]) -> None:
    for table, rows in datasets.items():
        with (SAMPLE_DIR / f"{table}.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=headers[table], extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)


def _schema_md(report, generated_files: dict[str, str]) -> str:
    readiness = report.metrics["readiness"]
    replay = report.metrics["replay_metrics"]
    lines = [
        "# Timestamped Campaign Replay Schema",
        "",
        f"- timestamped_replay_status：`{readiness['timestamped_replay_status']}`",
        f"- timestamped_replay_score：`{readiness['timestamped_replay_score']}`",
        f"- data_origin：`{report.metrics['data_origin']}`",
        f"- timestamp_coverage：`{readiness['timestamp_coverage']}`",
        f"- proxy_precision：`{replay['proxy_precision']}`",
        f"- proxy_recall：`{replay['proxy_recall']}`",
        f"- pressure_headloss_event_count：`{replay['pressure_headloss_event_count']}`",
        f"- pressure_headloss_matched_batch_count：`{replay['pressure_headloss_matched_batch_count']}`",
        f"- can_calibrate_fast_proxy：`{readiness['can_calibrate_fast_proxy']}`",
        "",
        "## 生成文件",
        "",
    ]
    for key, path in generated_files.items():
        lines.append(f"- {key}: `{path}`")
    lines.extend(["", "## 表结构", ""])
    for table, spec in report.metrics["replay_schema_contract"].items():
        lines.append(f"### {table}")
        lines.append("")
        lines.append(f"- 描述：{spec['description']}")
        lines.append(f"- 必需字段：{', '.join(spec['required_fields'])}")
        if spec.get("optional_fields"):
            lines.append(f"- 可选字段：{', '.join(spec['optional_fields'])}")
        lines.append(f"- 时间字段：{', '.join(spec['timestamp_fields'])}")
        lines.append("")
    lines.extend(["## 结论", ""])
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    return "\n".join(lines)


def _report_md(report, generated_files: dict[str, str]) -> str:
    readiness = report.metrics["readiness"]
    replay = report.metrics["replay_metrics"]
    lines = [
        "# Agent 42 Timestamped Campaign Replay 报告",
        "",
        f"- summary: {report.summary}",
        f"- timestamped_replay_status: `{readiness['timestamped_replay_status']}`",
        f"- timestamp_coverage: `{readiness['timestamp_coverage']}`",
        f"- proxy_precision: `{replay['proxy_precision']}`",
        f"- proxy_recall: `{replay['proxy_recall']}`",
        f"- pressure_headloss_event_count: `{replay['pressure_headloss_event_count']}`",
        f"- pressure_headloss_matched_batch_count: `{replay['pressure_headloss_matched_batch_count']}`",
        f"- can_calibrate_fast_proxy: `{readiness['can_calibrate_fast_proxy']}`",
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
    manifest["status"] = "timestamped campaign replay 接口已生成"
    manifest["timestamped_campaign_replay"] = relative_generated
    manifest["next_stage"] = "采集真实 timestamped campaign replay，验证 matrix_shock 快代理 precision/recall、提前量和误触发成本"
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
