from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from water_ai.agents.field_replay_import_agent import (
    FieldReplayImportAgent,
    load_field_replay_package,
    preflight_field_replay_package,
    write_field_replay_package_template,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent44_field_replay_import"
IMPORT_DIR = PROJECT_ROOT / "outputs" / "field_replay_import"
SYNTHETIC_SOURCE_DIR = PROJECT_ROOT / "outputs" / "timestamped_campaign_replay" / "synthetic_timestamped_replay"
SYNTHETIC_IMPORT_PACKAGE = IMPORT_DIR / "synthetic_replay_import_package"
REAL_FIELD_PACKAGE_TEMPLATE = IMPORT_DIR / "real_field_package_template"
ACCEPTANCE_METRICS = IMPORT_DIR / "import_acceptance_metrics.json"
PREFLIGHT_METRICS = IMPORT_DIR / "real_field_package_preflight_metrics.json"
TEMPLATE_PREFLIGHT_METRICS = IMPORT_DIR / "real_field_package_template_preflight_metrics.json"
IMPORT_SCHEMA = IMPORT_DIR / "import_schema.json"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    IMPORT_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    template_result = write_field_replay_package_template(REAL_FIELD_PACKAGE_TEMPLATE)
    template_preflight = preflight_field_replay_package(REAL_FIELD_PACKAGE_TEMPLATE)
    source_package_dir, source_package_type = _resolve_import_package()
    preflight = preflight_field_replay_package(source_package_dir)
    metadata, raw_tables = load_field_replay_package(source_package_dir)
    report = FieldReplayImportAgent(
        metadata=metadata,
        raw_tables=raw_tables,
    ).run([])
    report.metrics["source_package_type"] = source_package_type
    report.metrics["source_package_dir"] = str(source_package_dir)
    report.metrics["preflight"] = preflight
    report.metrics["real_field_package_template"] = template_result
    report.metrics["real_field_package_template_preflight"] = template_preflight
    generated_files = {
        "field_replay_import_protocol": str(DELIVERABLES_DIR / "field_replay_import_protocol.md"),
        "agent44_report": str(OUT_DIR / "agent44_report.md"),
        "import_acceptance_metrics": str(ACCEPTANCE_METRICS),
        "preflight_metrics": str(PREFLIGHT_METRICS),
        "template_preflight_metrics": str(TEMPLATE_PREFLIGHT_METRICS),
        "import_schema": str(IMPORT_SCHEMA),
        "real_field_package_template": str(REAL_FIELD_PACKAGE_TEMPLATE),
        "input_replay_package": str(source_package_dir),
    }
    (DELIVERABLES_DIR / "field_replay_import_protocol.md").write_text(
        _deliverable_md(report, generated_files),
        encoding="utf-8",
    )
    ACCEPTANCE_METRICS.write_text(
        json.dumps(
            {
                "method_contract": report.metrics["method_contract"],
                "metadata_audit": report.metrics["metadata_audit"],
                "table_import_audit": report.metrics["table_import_audit"],
                "linkage_audit": report.metrics["linkage_audit"],
                "readiness": report.metrics["readiness"],
                "export_policy": report.metrics["export_policy"],
                "source_package_type": source_package_type,
                "source_package_dir": str(source_package_dir),
                "preflight": preflight,
                "real_field_package_template": template_result,
                "real_field_package_template_preflight": template_preflight,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    PREFLIGHT_METRICS.write_text(json.dumps(preflight, ensure_ascii=False, indent=2), encoding="utf-8")
    TEMPLATE_PREFLIGHT_METRICS.write_text(
        json.dumps(template_preflight, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    IMPORT_SCHEMA.write_text(
        json.dumps(report.metrics["import_schema_contract"], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    payload = {
        "source_package_type": source_package_type,
        "source_package_dir": str(source_package_dir),
        "preflight": preflight,
        "real_field_package_template": template_result,
        "real_field_package_template_preflight": template_preflight,
        "source_synthetic_replay_package": str(SYNTHETIC_SOURCE_DIR) if source_package_type == "synthetic_interface_package" else None,
        "field_replay_import": {
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
    (OUT_DIR / "agent44_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "agent44_report.md").write_text(_report_md(report, generated_files), encoding="utf-8")
    _update_manifest(generated_files)

    print(report.summary)
    print(f"source_package_type: {source_package_type}")
    print(f"source_package_dir: {source_package_dir}")
    for rec in report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent44_report.md'}")
    for key, path in generated_files.items():
        print(f"{key}: {path}")


def _resolve_import_package() -> tuple[Path, str]:
    real_package_dir = os.environ.get("REAL_FIELD_REPLAY_PACKAGE_DIR", "").strip()
    if real_package_dir:
        package_dir = Path(real_package_dir).expanduser().resolve()
        if not package_dir.exists():
            raise FileNotFoundError(f"REAL_FIELD_REPLAY_PACKAGE_DIR does not exist: {package_dir}")
        if not package_dir.is_dir():
            raise NotADirectoryError(f"REAL_FIELD_REPLAY_PACKAGE_DIR is not a directory: {package_dir}")
        return package_dir, "user_provided_field_package"
    SYNTHETIC_IMPORT_PACKAGE.mkdir(parents=True, exist_ok=True)
    _write_synthetic_import_package()
    return SYNTHETIC_IMPORT_PACKAGE, "synthetic_interface_package"


def _write_synthetic_import_package() -> None:
    metadata = {
        "data_origin": "synthetic",
        "site_id": "synthetic_site_for_interface_test",
        "campaign_id": "synthetic_timestamped_campaign",
        "sampling_start": "2026-05-31T08:00:00+08:00",
        "sampling_end": "2026-05-31T12:00:00+08:00",
        "operator_id": "codex_interface_test",
        "instrument_snapshot_id": "synthetic_sensor_snapshot_v1",
        "chain_of_custody_id": "synthetic_not_for_field_calibration",
        "intended_use": "interface_test_only",
    }
    (SYNTHETIC_IMPORT_PACKAGE / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    for csv_path in SYNTHETIC_SOURCE_DIR.glob("*.csv"):
        shutil.copyfile(csv_path, SYNTHETIC_IMPORT_PACKAGE / csv_path.name)


def _deliverable_md(report, generated_files: dict[str, str]) -> str:
    readiness = report.metrics["readiness"]
    metadata = report.metrics["metadata_audit"]
    linkage = report.metrics["linkage_audit"]
    contract = report.metrics["method_contract"]
    source_package_type = report.metrics.get("source_package_type", "unknown")
    source_package_dir = report.metrics.get("source_package_dir", "unknown")
    preflight = report.metrics.get("preflight", {})
    template = report.metrics.get("real_field_package_template", {})
    template_preflight = report.metrics.get("real_field_package_template_preflight", {})
    supplement = preflight.get("r7j_supplement_audit", {}) if isinstance(preflight, dict) else {}
    template_supplement = (
        template_preflight.get("r7j_supplement_audit", {}) if isinstance(template_preflight, dict) else {}
    )
    lines = [
        "# Field Replay Import Protocol",
        "",
        f"- source_package_type：`{source_package_type}`",
        f"- source_package_dir：`{source_package_dir}`",
        f"- preflight_status：`{preflight.get('status', 'unknown')}`",
        f"- field_replay_import_status：`{readiness['field_replay_import_status']}`",
        f"- field_replay_import_score：`{readiness['field_replay_import_score']}`",
        f"- accepted_tables：`{readiness['accepted_table_count']}/{readiness['total_table_count']}`",
        f"- data_origin：`{metadata['data_origin']}`",
        f"- linkage_status：`{linkage['status']}`",
        f"- can_pass_to_timestamped_replay：`{readiness['can_pass_to_timestamped_replay']}`",
        f"- can_pass_to_g6：`{readiness['can_pass_to_g6']}`",
        f"- can_write_to_protective_control：`{readiness['can_write_to_protective_control']}`",
        f"- real_field_template_optional_supplements：`{template.get('optional_supplement_files', [])}`",
        f"- real_field_template_preflight_status：`{template_preflight.get('status', 'unknown')}`",
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
        "## 表导入验收",
        "",
        "| Table | 行数 | 状态 | 缺失字段 | 类型错误数 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for table, audit in report.metrics["table_import_audit"].items():
        lines.append(
            f"| `{table}` | `{audit['record_count']}` | `{audit['status']}` | "
            f"`{audit['missing_required_fields']}` | `{len(audit['type_errors'])}` |"
        )
    if preflight:
        lines.extend(["", "## Preflight 下一步", ""])
        for action in preflight.get("next_actions", []):
            lines.append(f"- {action}")
    if supplement:
        lines.extend(
            [
                "",
                "## R7j Catalyst Proxy Holdout Supplement",
                "",
                "| Supplement Table | 状态 | 行数 | 缺失字段 |",
                "| --- | --- | --- | --- |",
            ]
        )
        for table, audit in supplement.items():
            lines.append(
                f"| `{table}` | `{audit.get('status', 'unknown')}` | "
                f"`{audit.get('row_count', 0)}` | `{audit.get('missing_headers', [])}` |"
            )
        lines.append("")
        lines.append(
            "- R7j supplement 对 Agent44 导入是 optional；当 R7 coverage 消费 Agent51 weak_axis_repair_plan 时，"
            "它会成为 catalyst proxy field holdout 的证据要求。"
        )
    if template_supplement:
        lines.extend(
            [
                "",
                "## Real Field Template R7j Supplement",
                "",
                "| Supplement Table | 状态 | 行数 | 缺失字段 |",
                "| --- | --- | --- | --- |",
            ]
        )
        for table, audit in template_supplement.items():
            lines.append(
                f"| `{table}` | `{audit.get('status', 'unknown')}` | "
                f"`{audit.get('row_count', 0)}` | `{audit.get('missing_headers', [])}` |"
            )
    lines.extend(["", "## 生成文件", ""])
    for key, path in generated_files.items():
        lines.append(f"- {key}: `{path}`")
    lines.extend(["", "## 结论", ""])
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    return "\n".join(lines)


def _report_md(report, generated_files: dict[str, str]) -> str:
    readiness = report.metrics["readiness"]
    template = report.metrics.get("real_field_package_template", {})
    preflight = report.metrics.get("preflight", {})
    template_preflight = report.metrics.get("real_field_package_template_preflight", {})
    lines = [
        "# Agent 44 Field Replay Import 报告",
        "",
        f"- summary: {report.summary}",
        f"- source_package_type: `{report.metrics.get('source_package_type', 'unknown')}`",
        f"- source_package_dir: `{report.metrics.get('source_package_dir', 'unknown')}`",
        f"- preflight_status: `{report.metrics.get('preflight', {}).get('status', 'unknown')}`",
        f"- field_replay_import_status: `{readiness['field_replay_import_status']}`",
        f"- can_pass_to_timestamped_replay: `{readiness['can_pass_to_timestamped_replay']}`",
        f"- can_pass_to_g6: `{readiness['can_pass_to_g6']}`",
        f"- optional_supplement_files: `{template.get('optional_supplement_files', [])}`",
        f"- r7j_supplement_audit: `{preflight.get('r7j_supplement_audit', {})}`",
        f"- template_preflight_status: `{template_preflight.get('status', 'unknown')}`",
        f"- template_r7j_supplement_audit: `{template_preflight.get('r7j_supplement_audit', {})}`",
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
        key: _relative_or_absolute(Path(path))
        for key, path in generated_files.items()
    }
    manifest["status"] = "field replay import gate 已生成，并已扩展 R7j Agent51 catalyst proxy holdout 采集模板"
    manifest["field_replay_import"] = relative_generated
    manifest["next_stage"] = (
        "导入真实 field metadata 与 CSV replay 包，通过 Agent44 后再进入 Agent42/Agent43 G6/P6；"
        "若要验证 Agent51 catalyst_activity 弱轴修复，还需按模板补齐 site_topology_or_bed_geometry.csv "
        "以及 node_modality_sensor_timeseries.csv 中 node_id/modality/value/sensor_status 等节点级字段。"
    )
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def _relative_or_absolute(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    main()
