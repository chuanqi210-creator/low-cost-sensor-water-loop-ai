from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Any

from water_ai.catalyst_field_package_slice import (
    SOURCE_ENV_VAR,
    TABLE_COLUMNS,
    build_catalyst_field_package_slice_preflight,
    build_catalyst_field_package_slice_template,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "outputs" / "catalyst_field_package_slice"
TEMPLATE_DIR = OUT_DIR / "focused_field_package_slice_template"
METRICS_PATH = OUT_DIR / "catalyst_field_package_slice_metrics.json"
TEMPLATE_SUMMARY_PATH = OUT_DIR / "focused_field_package_slice_template_summary.json"
DELIVERABLE_PATH = PROJECT_ROOT / "deliverables" / "model_core_optimization" / "catalyst_field_package_slice.md"
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLE_PATH.parent.mkdir(parents=True, exist_ok=True)

    template = build_catalyst_field_package_slice_template()
    _write_template_csvs(template)
    TEMPLATE_SUMMARY_PATH.write_text(json.dumps(template, ensure_ascii=False, indent=2), encoding="utf-8")

    source_path = os.environ.get(SOURCE_ENV_VAR, "").strip()
    external_supplied = bool(source_path and Path(source_path).exists())
    result = build_catalyst_field_package_slice_preflight(
        source_dir=source_path or None,
        external_slice_supplied=external_supplied,
    )
    result["focused_field_package_slice_template_dir"] = str(TEMPLATE_DIR.relative_to(PROJECT_ROOT))
    result["focused_field_package_slice_template_summary_path"] = str(TEMPLATE_SUMMARY_PATH.relative_to(PROJECT_ROOT))
    result["planned_node_modality_row_count"] = template["table_row_counts"]["node_modality_sensor_timeseries"]
    result["planned_offline_lab_row_count"] = template["table_row_counts"]["offline_lab_results"]
    result["planned_campaign_operation_row_count"] = template["table_row_counts"]["campaign_operation_log"]
    result["planned_geometry_row_count"] = template["table_row_counts"]["site_topology_or_bed_geometry"]

    METRICS_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    DELIVERABLE_PATH.write_text(_deliverable_md(result), encoding="utf-8")
    _update_manifest(result)

    print(f"Catalyst field package slice: {result['slice_status']}")
    print(f"- preflight pass: {result['slice_preflight_pass']}")
    print(f"- matched batches: {result['matched_batch_count']}")
    print(f"- template dir: {TEMPLATE_DIR}")
    print(f"- next: {result['next_operator_action']}")


def _write_template_csvs(template: dict[str, Any]) -> None:
    tables = template["tables"]
    for table_name, table in tables.items():
        path = TEMPLATE_DIR / f"{table_name}.csv"
        columns = TABLE_COLUMNS[table_name]
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            for row in table["rows"]:
                writer.writerow({column: row.get(column, "") for column in columns})


def _deliverable_md(result: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# R8u113 Catalyst Field Package Slice",
            "",
            "## 定位",
            "",
            (
                "该切片把 catalyst_activity 的现场补数范围压缩为四张 CSV 表："
                "`node_modality_sensor_timeseries`、`offline_lab_results`、"
                "`campaign_operation_log`、`site_topology_or_bed_geometry`。"
                "它服务 R7/Agent51 的真实 field package 补齐，但不替代完整 field package import。"
            ),
            "",
            "## Readiness",
            "",
            f"- slice_status: `{result['slice_status']}`",
            f"- source_env_var: `{result['source_env_var']}`",
            f"- external_slice_supplied: `{result['external_slice_supplied']}`",
            f"- slice_preflight_pass: `{result['slice_preflight_pass']}`",
            f"- matched_batch_count: `{result['matched_batch_count']}`",
            f"- matched_batch_requirement_pass: `{result['matched_batch_requirement_pass']}`",
            f"- template_dir: `{result['focused_field_package_slice_template_dir']}`",
            f"- can_route_to_r7_field_package_patch_candidate: `{result['can_route_to_r7_field_package_patch_candidate']}`",
            f"- can_route_to_agent51_field_proxy_holdout: `{result['can_route_to_agent51_field_proxy_holdout']}`",
            f"- can_relax_agent49_catalyst_uncertainty_block: `{result['can_relax_agent49_catalyst_uncertainty_block']}`",
            "",
            "## Required Tables",
            "",
            "| table | planned rows | purpose |",
            "| --- | ---: | --- |",
            (
                f"| `node_modality_sensor_timeseries` | {result['planned_node_modality_row_count']} | "
                "UV254、ORP、pressure_drop 三个低成本/过程代理信号 |"
            ),
            (
                f"| `offline_lab_results` | {result['planned_offline_lab_row_count']} | "
                "QA-passed catalyst_activity 离线标签 |"
            ),
            (
                f"| `campaign_operation_log` | {result['planned_campaign_operation_row_count']} | "
                "再生事件和动作时延对齐 |"
            ),
            (
                f"| `site_topology_or_bed_geometry` | {result['planned_geometry_row_count']} | "
                "床层体积、HRT、流量等几何归一化信息 |"
            ),
            "",
            "## Blocking Reasons",
            "",
            *[f"- `{reason}`" for reason in result["blocking_reasons"]],
            "",
            "## Boundary",
            "",
            result["field_boundary"],
            "",
            result["no_write_boundary"],
            "",
        ]
    )


def _update_manifest(result: dict[str, Any]) -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest["latest_catalyst_field_package_slice_metrics"] = str(METRICS_PATH.relative_to(PROJECT_ROOT))
    manifest["latest_catalyst_field_package_slice_doc"] = str(DELIVERABLE_PATH.relative_to(PROJECT_ROOT))
    manifest["latest_catalyst_field_package_slice_template_dir"] = str(TEMPLATE_DIR.relative_to(PROJECT_ROOT))
    manifest["latest_catalyst_field_package_slice_status"] = result["slice_status"]
    manifest["latest_catalyst_field_package_slice_preflight_pass"] = result["slice_preflight_pass"]
    manifest["latest_catalyst_field_package_slice_matched_batch_count"] = result["matched_batch_count"]
    manifest["latest_catalyst_field_package_slice_can_route_to_r7_field_package_patch_candidate"] = result[
        "can_route_to_r7_field_package_patch_candidate"
    ]
    manifest["latest_catalyst_field_package_slice_can_route_to_agent51_field_proxy_holdout"] = result[
        "can_route_to_agent51_field_proxy_holdout"
    ]
    manifest["latest_catalyst_field_package_slice_next_operator_action"] = result["next_operator_action"]
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
