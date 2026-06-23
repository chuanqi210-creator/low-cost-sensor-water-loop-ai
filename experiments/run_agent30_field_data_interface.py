from __future__ import annotations

import csv
import json
from pathlib import Path

from water_ai.agents.field_data_interface_agent import FieldDataInterfaceAgent
from water_ai.simulation import generate_low_cost_sensor_stream


PROJECT_ROOT = Path(__file__).resolve().parents[1]
AGENT23_REPORT = PROJECT_ROOT / "outputs" / "agent23_post_replan_replay" / "agent23_report.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent30_field_data_interface"
TEMPLATE_DIR = OUT_DIR / "field_data_templates"
SAMPLE_DIR = OUT_DIR / "synthetic_field_data_package"
DOC_PATH = PROJECT_ROOT / "docs" / "field_data_interface_spec.md"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    campaign_records = _campaign_records()
    datasets = _build_synthetic_field_package(campaign_records)

    agent = FieldDataInterfaceAgent(datasets=datasets, data_origin="synthetic")
    report = agent.run([])

    _write_schema(report.metrics["schema_contract"])
    _write_templates(report.metrics["template_headers"])
    _write_sample_package(datasets)

    payload = {
        "source_report": str(AGENT23_REPORT),
        "field_data_interface": {
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
        "generated_files": {
            "schema": str(OUT_DIR / "field_data_schema.json"),
            "templates": str(TEMPLATE_DIR),
            "synthetic_package": str(SAMPLE_DIR),
            "doc": str(DOC_PATH),
        },
    }
    (OUT_DIR / "agent30_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "agent30_report.md").write_text(_build_report_markdown(report, payload["generated_files"]), encoding="utf-8")
    DOC_PATH.write_text(_build_doc(report, payload["generated_files"]), encoding="utf-8")

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent30_report.md'}")
    print(f"wrote {DOC_PATH}")


def _campaign_records() -> list[dict[str, object]]:
    payload = json.loads(AGENT23_REPORT.read_text(encoding="utf-8"))
    records = payload.get("campaign", {}).get("records", [])
    return records if isinstance(records, list) else []


def _build_synthetic_field_package(records: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    selected = records[:8]
    sensor_rows: list[dict[str, object]] = []
    lab_rows: list[dict[str, object]] = []
    catalyst_rows: list[dict[str, object]] = []
    operation_rows: list[dict[str, object]] = []
    topology_rows = [
        {
            "site_id": "synthetic_loop_site",
            "node_id": "N3_catalyst_bed",
            "zone": "catalyst_bed",
            "upstream_node_id": "N2_reactor_mid",
            "downstream_node_id": "N4_recirculation_loop",
            "bed_id": "BED_A",
            "bed_depth_m": 0.8,
            "bed_area_m2": 0.12,
            "nominal_flow_Lmin": 1.1,
            "nominal_HRT_min": 24,
            "pressure_sensor_location": "bed_inlet_outlet_pair",
            "expected_clean_bed_pressure_drop_kPa": 2.1,
        }
    ]
    for record in selected:
        batch_id = f"B{int(record.get('batch_id', 0)):03d}"
        scenario = str(record.get("scenario", "sensor_faults"))
        stream = generate_low_cost_sensor_stream(n=36, seed=100 + int(record.get("batch_id", 0)), scenario=scenario, inject_faults=False)
        final_state = stream[-1].ground_truth_state
        for reading in stream:
            sensor_rows.append(
                {
                    "batch_id": batch_id,
                    "timestamp_min": reading.timestamp_min,
                    "cycle_id": reading.cycle_id,
                    **reading.values,
                    "pressure_drop_kPa": round(3.0 + 3.8 * (1.0 - final_state["catalyst_activity"]), 3),
                    "headloss_kPa_per_m": round(3.75 + 4.75 * (1.0 - final_state["catalyst_activity"]), 3),
                    "flow_normalized_pressure_residual": round(0.2 * (1.0 - final_state["catalyst_activity"]), 3),
                    "sensor_status": "synthetic_template",
                    "instrument_id": "LC-SIM-01",
                }
            )
        lab_rows.extend(
            [
                _lab_row(batch_id, 36, "COD", round(20 + 85 * final_state["pollutant_residual_risk"], 3), "mg/L"),
                _lab_row(batch_id, 36, "target_pollutant_proxy", final_state["pollutant_residual_risk"], "risk_index"),
                _lab_row(batch_id, 36, "UV254_reference", stream[-1].values["UV254_abs"] or 0.0, "abs"),
            ]
        )
        catalyst_rows.append(
            {
                "catalyst_id": "CAT-A",
                "batch_id": batch_id,
                "cycle_count": int(record.get("catalyst_age_cycles_end", 0)),
                "regen_count": int(record.get("catalyst_regen_count_end", 0)),
                "activity_assay": float(record.get("catalyst_activity_end", final_state["catalyst_activity"])),
                "pressure_drop_kPa": round(2.8 + 5.2 * (1.0 - float(record.get("catalyst_lifetime_fraction_end", 0.8))), 3),
                "headloss_kPa_per_m": round(3.5 + 6.5 * (1.0 - float(record.get("catalyst_lifetime_fraction_end", 0.8))), 3),
                "lifetime_fraction": float(record.get("catalyst_lifetime_fraction_end", 0.8)),
                "surface_pollution_index": round(1.0 - float(record.get("catalyst_activity_end", 0.8)), 3),
                "regeneration_event": "regen" in " ".join(str(action) for action in record.get("all_actions", [])),
                "bed_geometry_id": "BED_A",
                "catalyst_bed_depth_m": 0.8,
            }
        )
        operation_rows.extend(_operation_rows(batch_id, record))
    cost_rows = [
        {
            "item_id": "sensor_uv254",
            "category": "sensor",
            "unit_cost_cny": 4200,
            "quantity": 1,
            "lead_time_days": 7,
            "vendor": "template_vendor",
            "maintenance_hours_per_month": 1.5,
            "interface_point": "AI_UV254",
        },
        {
            "item_id": "sensor_orp",
            "category": "sensor",
            "unit_cost_cny": 1600,
            "quantity": 1,
            "lead_time_days": 5,
            "vendor": "template_vendor",
            "maintenance_hours_per_month": 1.2,
            "interface_point": "AI_ORP",
        },
        {
            "item_id": "catalyst_module",
            "category": "catalyst",
            "unit_cost_cny": 12000,
            "quantity": 3,
            "lead_time_days": 21,
            "vendor": "template_vendor",
            "maintenance_hours_per_month": 0.4,
            "interface_point": "inventory_catalyst",
        },
        {
            "item_id": "validation_shift",
            "category": "labor",
            "unit_cost_cny": 900,
            "quantity": 4,
            "lead_time_days": 3,
            "vendor": "internal_lab",
            "maintenance_hours_per_month": 0,
            "interface_point": "lab_schedule",
        },
    ]
    return {
        "sensor_timeseries": sensor_rows,
        "offline_lab_results": lab_rows,
        "catalyst_lifecycle": catalyst_rows,
        "campaign_operation_log": operation_rows,
        "site_topology_or_bed_geometry": topology_rows,
        "cost_deployment": cost_rows,
    }


def _lab_row(batch_id: str, sample_time_min: int, analyte: str, value: object, unit: str) -> dict[str, object]:
    return {
        "batch_id": batch_id,
        "sample_time_min": sample_time_min,
        "analyte": analyte,
        "value": value,
        "unit": unit,
        "method": "synthetic_reference",
        "qa_flag": "pass",
        "lab_id": "SIM-LAB",
        "proxy_holdout_label": analyte in {"target_pollutant_proxy", "UV254_reference"},
    }


def _operation_rows(batch_id: str, record: dict[str, object]) -> list[dict[str, object]]:
    actions = record.get("all_actions", [])
    action_list = [str(action) for action in actions] if isinstance(actions, list) else ["unknown_action"]
    elapsed = max(1.0, float(record.get("elapsed_min", 1)))
    span = max(1.0, elapsed / max(1, len(action_list)))
    rows = []
    for index, action in enumerate(action_list):
        start = round(index * span, 3)
        end = round(min(elapsed, (index + 1) * span), 3)
        rows.append(
            {
                "campaign_id": "synthetic_campaign_from_agent23",
                "batch_id": batch_id,
                "action_id": action,
                "start_min": start,
                "end_min": end,
                "intake_fraction": 0.75,
                "success": bool(record.get("success", False)),
                "validation_minutes": int(record.get("validation_minutes", 0)),
                "operator_override": False,
                "recycle_ratio": 0.35 if "recirculate" in action else 0.0,
                "tank_storage_margin": round(max(0.0, 1.0 - float(record.get("intake_fraction", 0.75))), 3),
                "actuator_latency_p90": round(max(1.0, end - start), 3),
                "pump_valve_result": "ok" if bool(record.get("success", False)) else "needs_review",
                "hold_time_min": round(max(0.0, end - start), 3) if "hold" in action or "recirculate" in action else 0.0,
                "regeneration_event": "regen" in action,
                "bed_id": "BED_A",
                "pressure_headloss_review_required": "regen" in action or "recirculate" in action,
            }
        )
    return rows


def _write_schema(schema: dict[str, object]) -> None:
    (OUT_DIR / "field_data_schema.json").write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_templates(headers: dict[str, list[str]]) -> None:
    for table, fields in headers.items():
        with (TEMPLATE_DIR / f"{table}.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()


def _write_sample_package(datasets: dict[str, list[dict[str, object]]]) -> None:
    for table, rows in datasets.items():
        fieldnames = FieldDataInterfaceAgent.template_headers()[table]
        with (SAMPLE_DIR / f"{table}.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)


def _build_report_markdown(report, generated_files: dict[str, str]) -> str:
    metrics = report.metrics
    readiness = metrics["readiness"]
    lines = [
        "# Agent 30 真实数据接口与校准准备报告",
        "",
        f"- summary: {report.summary}",
        f"- data_origin: `{metrics['data_origin']}`",
        f"- interface_status: `{readiness['interface_status']}`",
        f"- calibration_readiness_score: `{readiness['calibration_readiness_score']}`",
        f"- field_coverage: `{readiness['field_coverage']}`",
        f"- linkage_score: `{readiness['linkage_score']}`",
        "",
        "## 生成文件",
        "",
    ]
    for key, value in generated_files.items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## 数据表状态", "", "| 表 | 记录数 | 状态 | 表评分 | 缺失字段 |", "| --- | ---: | --- | ---: | --- |"])
    for table, status in metrics["table_statuses"].items():
        lines.append(
            f"| {table} | {status['record_count']} | `{status['status']}` | "
            f"{status['table_score']} | {status['missing_required_fields']} |"
        )
    lines.extend(["", "## 校准任务", "", "| 任务 | 就绪 | 得分 | 阻塞项 | 模型更新 |", "| --- | --- | ---: | --- | --- |"])
    for task in metrics["calibration_tasks"]:
        lines.append(
            f"| {task['task_id']} | `{task['task_ready']}` | {task['readiness_score']} | "
            f"{task['blockers']} | {task['model_update']} |"
        )
    lines.extend(["", "## 建议", ""])
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    lines.extend(["", "## 风险边界", ""])
    for issue in report.issues:
        lines.append(f"- `{issue.issue_type}`：{issue.message}")
    return "\n".join(lines)


def _build_doc(report, generated_files: dict[str, str]) -> str:
    metrics = report.metrics
    readiness = metrics["readiness"]
    lines = [
        "# 真实数据接口与校准准备规范",
        "",
        "## 目的",
        "",
        "Agent30 的作用是把当前仿真研究平台推进到真实数据校准阶段：先规定现场数据包必须包含哪些表、哪些字段、怎样用 batch_id 回连，再判断当前数据包能否进入软传感器、时间预算、催化剂寿命和经济性校准。",
        "",
        "## 当前状态",
        "",
        f"- 数据来源：`{metrics['data_origin']}`。",
        f"- 接口状态：`{readiness['interface_status']}`。",
        f"- 校准就绪度：`{readiness['calibration_readiness_score']}`。",
        f"- 生成 schema：`{generated_files['schema']}`。",
        f"- 生成采集模板：`{generated_files['templates']}`。",
        f"- 合成样例数据包：`{generated_files['synthetic_package']}`。",
        "",
        "## 数据表契约",
        "",
    ]
    for table, spec in metrics["schema_contract"].items():
        lines.extend(
            [
                f"### {table}",
                "",
                f"- 说明：{spec['description']}",
                f"- 必需字段：{', '.join(str(field) for field in spec['required_fields'])}",
                f"- 可选字段：{', '.join(str(field) for field in spec['optional_fields'])}",
                f"- 主键：{', '.join(str(field) for field in spec['primary_key'])}",
                f"- 校准对象：{', '.join(str(field) for field in spec['calibrates'])}",
                "",
            ]
        )
    lines.extend(["## 下一步", ""])
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
