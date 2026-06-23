from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.data_quality_agent import DataQualityAgent
from water_ai.agents.soft_sensor_agent import SoftSensorAgent
from water_ai.agents.soft_sensor_matrix_coupling_agent import SoftSensorMatrixCouplingAgent
from water_ai.process_dynamics import generate_sensor_stream_from_process_state, initial_process_state


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
SPARSE_METRICS_PATH = PROJECT_ROOT / "outputs" / "sensor_network_sparse_placement" / "sparse_placement_metrics.json"
TRAINING_METRICS_PATH = PROJECT_ROOT / "outputs" / "soft_sensor_training" / "soft_sensor_training_metrics.json"
GREY_BOX_METRICS_PATH = PROJECT_ROOT / "outputs" / "minimal_grey_box_physics" / "grey_box_physics_metrics.json"
OBSERVATION_CONTRACT_METRICS_PATH = PROJECT_ROOT / "outputs" / "observation_contract_merge" / "observation_contract_metrics.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent54_soft_sensor_matrix_coupling"
METRICS_DIR = PROJECT_ROOT / "outputs" / "soft_sensor_matrix_coupling"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables"
METRICS_PATH = METRICS_DIR / "soft_sensor_matrix_metrics.json"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)

    sparse_metrics = _read_optional_json(SPARSE_METRICS_PATH)
    training_metrics = _read_optional_json(TRAINING_METRICS_PATH)
    grey_box_metrics = _read_optional_json(GREY_BOX_METRICS_PATH)
    observation_contract_metrics = _read_optional_json(OBSERVATION_CONTRACT_METRICS_PATH)
    interface = sparse_metrics.get("soft_sensor_interface", {}) if isinstance(sparse_metrics, dict) else {}
    readings = generate_sensor_stream_from_process_state(initial_process_state("matrix_shock"), n=48, seed=54)
    dq_report = DataQualityAgent().run(readings)
    soft_report = SoftSensorAgent(data_quality_report=dq_report, sensor_layout_interface=interface).run(readings)
    layout_context = soft_report.metrics["layout_context"]

    report = SoftSensorMatrixCouplingAgent(
        sensor_layout_interface=interface if isinstance(interface, dict) else {},
        sparse_placement_metrics=sparse_metrics,
        observation_contract_metrics=observation_contract_metrics,
        soft_sensor_training_metrics=training_metrics,
        grey_box_physics_metrics=grey_box_metrics,
        soft_sensor_layout_context=layout_context,
    ).run(readings)

    generated_files = {
        "soft_sensor_matrix_coupling": str(DELIVERABLES_DIR / "soft_sensor_matrix_coupling.md"),
        "agent54_report": str(OUT_DIR / "agent54_report.md"),
        "soft_sensor_matrix_metrics": str(METRICS_PATH),
        "field_path_endpoint_label_package_contract": str(
            METRICS_DIR / "field_path_endpoint_label_package_contract.json"
        ),
        "field_path_endpoint_label_package_preflight": str(
            METRICS_DIR / "field_path_endpoint_label_package_preflight.json"
        ),
        "field_path_endpoint_label_package_template": str(
            METRICS_DIR / "field_path_endpoint_label_package_template.json"
        ),
    }
    (DELIVERABLES_DIR / "soft_sensor_matrix_coupling.md").write_text(_deliverable_md(report), encoding="utf-8")
    METRICS_PATH.write_text(
        json.dumps(
            {
                "method_contract": report.metrics["method_contract"],
                "feature_contract": report.metrics["feature_contract"],
                "missingness_stress_tests": report.metrics["missingness_stress_tests"],
                "training_schema_gap": report.metrics["training_schema_gap"],
                "readiness": report.metrics["readiness"],
                "agent50_writeback": report.metrics["agent50_writeback"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    path_package_contract = report.metrics["feature_contract"]["field_path_endpoint_label_package_contract"]
    path_package_preflight = report.metrics["field_path_endpoint_label_package_preflight"]
    Path(generated_files["field_path_endpoint_label_package_contract"]).write_text(
        json.dumps(path_package_contract, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    Path(generated_files["field_path_endpoint_label_package_preflight"]).write_text(
        json.dumps(path_package_preflight, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    Path(generated_files["field_path_endpoint_label_package_template"]).write_text(
        json.dumps(_field_path_endpoint_label_template(path_package_contract), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    payload = {
        "soft_sensor_matrix_coupling": {
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
        "soft_sensor_layout_context": layout_context,
        "generated_files": generated_files,
    }
    (OUT_DIR / "agent54_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "agent54_report.md").write_text(_report_md(report, generated_files), encoding="utf-8")
    _update_manifest(generated_files)

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    for key, path in generated_files.items():
        print(f"{key}: {path}")


def _read_optional_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _deliverable_md(report) -> str:
    readiness = report.metrics["readiness"]
    contract = report.metrics["feature_contract"]
    lines = [
        "# 软传感 Node-Modality/Missingness 矩阵耦合",
        "",
        f"- soft_sensor_matrix_status：`{readiness['soft_sensor_matrix_status']}`",
        f"- layout_id：`{contract['layout_id']}`",
        f"- layout_contract_score：`{readiness['layout_contract_score']}`",
        f"- missingness_robustness_score：`{readiness['missingness_robustness_score']}`",
        f"- live_layout_context_status：`{readiness['live_layout_context_status']}`",
        f"- pressure_headloss_candidate_pool_status：`{readiness['pressure_headloss_candidate_pool_status']}`",
        f"- pressure_headloss_candidate_count：`{readiness['pressure_headloss_candidate_count']}`",
        f"- hydraulic_path_contract_status：`{readiness['hydraulic_path_contract_status']}`",
        f"- hydraulic_path_covered_stage_count：`{readiness['hydraulic_path_covered_stage_count']}/{readiness['hydraulic_path_stage_count']}`",
        f"- hydraulic_path_feature_variation_status：`{readiness['hydraulic_path_feature_variation_status']}`",
        f"- layout_holdout_status：`{readiness['layout_holdout_status']}`",
        f"- layout_holdout_mean_mae：`{readiness['layout_holdout_mean_mae']}`",
        f"- hydraulic_path_final_release_gate_needs_effluent_label：`{readiness['hydraulic_path_final_release_gate_needs_effluent_label']}`",
        f"- can_write_to_release_gate：`{readiness['can_write_to_release_gate']}`",
        "",
        "## Feature Tensor Contract",
        "",
        f"- tensor_axes：`{contract['tensor_axes']}`",
        f"- feature_channels：`{contract['feature_channels']}`",
        f"- mask_shape：`{contract['mask_shape']}`",
        f"- selected_nodes：`{contract['selected_nodes']}`",
        f"- selected_modalities：`{contract['selected_modalities']}`",
        "",
        "## Hydraulic Path Feature Contract",
        "",
    ]
    path_contract = contract["hydraulic_path_feature_contract"]
    lines.append(f"- source：`{path_contract['source']}`")
    lines.append(f"- contract_status：`{path_contract['contract_status']}`")
    lines.append(f"- feature_terms：`{path_contract['feature_terms']}`")
    lines.append(f"- field_schema_terms：`{path_contract['field_schema_terms']}`")
    lines.append(f"- covered_stage_count：`{path_contract['covered_stage_count']}/{path_contract['path_stage_count']}`")
    lines.append(f"- recirculation_loop_observed：`{path_contract['recirculation_loop_observed']}`")
    lines.append(f"- final_release_gate_needs_effluent_label：`{path_contract['final_release_gate_needs_effluent_label']}`")
    lines.append(f"- can_use_for_release_gate：`{path_contract['can_use_for_release_gate']}`")
    lines.extend(
        [
            "",
            "## Layout Holdout Boundary",
            "",
            f"- hydraulic_path_feature_variation_ready：`{readiness['hydraulic_path_feature_variation_ready']}`",
            f"- layout_holdout_ready：`{readiness['layout_holdout_ready']}`",
            f"- layout_holdout_train_layout_count：`{readiness['layout_holdout_train_layout_count']}`",
            f"- layout_holdout_heldout_layout_count：`{readiness['layout_holdout_heldout_layout_count']}`",
            f"- layout_holdout_field_boundary：{readiness['layout_holdout_field_boundary']}",
        ]
    )
    package_contract = contract["field_path_endpoint_label_package_contract"]
    package_preflight = report.metrics["field_path_endpoint_label_package_preflight"]
    lines.extend(
        [
            "",
            "## Field Path/Endpoint Label Package Gate",
            "",
            f"- package_contract_id：`{package_contract['contract_id']}`",
            f"- minimum_matched_batch_count：`{package_contract['minimum_matched_batch_count']}`",
            f"- required_tables：`{package_contract['required_tables']}`",
            f"- preflight_status：`{package_preflight['preflight_status']}`",
            f"- matched_batch_count：`{package_preflight['matched_batch_count']}`",
            f"- can_route_to_field_layout_holdout：`{package_preflight['can_route_to_field_layout_holdout']}`",
            f"- next_operator_action：`{package_preflight['next_operator_action']}`",
            f"- field_boundary：{package_preflight['field_boundary']}",
        ]
    )
    lines.extend(
        [
            "",
            "## Missingness Stress Tests",
            "",
            "| Scenario | Critical target | Missing fraction | Support | Fallback |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in report.metrics["missingness_stress_tests"]:
        lines.append(
            f"| `{row['scenario_id']}` | `{row['critical_target']}` | `{row['missing_fraction']}` | "
            f"`{row['estimated_masked_state_support']}` | {row['fallback']} |"
        )
    lines.extend(["", "## Training Schema Gap", ""])
    gap = report.metrics["training_schema_gap"]
    lines.append(f"- current_model_layout_aware：`{gap['current_model_layout_aware']}`")
    lines.append(f"- missing_layout_terms：`{gap['missing_layout_terms']}`")
    lines.append(f"- missing_pressure_headloss_terms：`{gap['missing_pressure_headloss_terms']}`")
    lines.append(f"- missing_hydraulic_path_terms：`{gap['missing_hydraulic_path_terms']}`")
    lines.extend(["", "## Pressure/Headloss Candidate Contract", ""])
    pressure_contract = contract["pressure_headloss_candidate_contract"]
    lines.append(f"- source：`{pressure_contract['source']}`")
    lines.append(f"- candidate_ids：`{pressure_contract['candidate_ids']}`")
    lines.append(f"- field_required_tables：`{pressure_contract['field_required_tables']}`")
    lines.append(f"- can_use_as_installed_sensor：`{pressure_contract['can_use_as_installed_sensor']}`")
    lines.extend(["", "## 结论与边界", ""])
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    return "\n".join(lines)


def _report_md(report, generated_files: dict[str, str]) -> str:
    readiness = report.metrics["readiness"]
    lines = [
        "# Agent 54 软传感矩阵耦合报告",
        "",
        f"- summary: {report.summary}",
        f"- soft_sensor_matrix_status: `{readiness['soft_sensor_matrix_status']}`",
        f"- missingness_robustness_score: `{readiness['missingness_robustness_score']}`",
        f"- pressure_headloss_candidate_pool_status: `{readiness['pressure_headloss_candidate_pool_status']}`",
        f"- pressure_headloss_candidate_count: `{readiness['pressure_headloss_candidate_count']}`",
        f"- hydraulic_path_contract_status: `{readiness['hydraulic_path_contract_status']}`",
        f"- hydraulic_path_covered_stage_count: `{readiness['hydraulic_path_covered_stage_count']}/{readiness['hydraulic_path_stage_count']}`",
        f"- hydraulic_path_feature_variation_status: `{readiness['hydraulic_path_feature_variation_status']}`",
        f"- layout_holdout_status: `{readiness['layout_holdout_status']}`",
        f"- layout_holdout_mean_mae: `{readiness['layout_holdout_mean_mae']}`",
        f"- field_path_endpoint_label_package_status: `{readiness['field_path_endpoint_label_package_status']}`",
        f"- field_path_endpoint_label_matched_batch_count: `{readiness['field_path_endpoint_label_matched_batch_count']}`",
        f"- hydraulic_path_final_release_gate_needs_effluent_label: `{readiness['hydraulic_path_final_release_gate_needs_effluent_label']}`",
        f"- can_write_to_release_gate: `{readiness['can_write_to_release_gate']}`",
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
    training_metrics = _read_optional_json(TRAINING_METRICS_PATH)
    relative_generated = {
        key: str(Path(path).relative_to(PROJECT_ROOT))
        for key, path in generated_files.items()
    }
    metrics = _read_optional_json(METRICS_PATH)
    readiness = metrics.get("readiness", {}) if isinstance(metrics, dict) else {}
    manifest["status"] = "软传感矩阵耦合层已接入 synthetic layout holdout 与 hydraulic path feature contract"
    manifest["soft_sensor_matrix_coupling"] = relative_generated
    if isinstance(readiness, dict):
        manifest["latest_agent54_hydraulic_path_contract_status"] = readiness.get("hydraulic_path_contract_status")
        manifest["latest_agent54_hydraulic_path_schema_ready"] = readiness.get("hydraulic_path_schema_ready")
        manifest["latest_agent54_hydraulic_path_feature_variation_status"] = readiness.get(
            "hydraulic_path_feature_variation_status"
        )
        manifest["latest_agent54_layout_holdout_status"] = readiness.get("layout_holdout_status")
        manifest["latest_agent54_layout_holdout_mean_mae"] = readiness.get("layout_holdout_mean_mae")
        manifest["latest_agent54_field_path_endpoint_label_package_status"] = readiness.get(
            "field_path_endpoint_label_package_status"
        )
        manifest["latest_agent54_field_path_endpoint_label_matched_batch_count"] = readiness.get(
            "field_path_endpoint_label_matched_batch_count"
        )
        manifest["latest_agent54_can_route_to_field_layout_holdout"] = readiness.get("can_route_to_field_layout_holdout")
        manifest["latest_agent54_hydraulic_path_final_release_gate_needs_effluent_label"] = readiness.get(
            "hydraulic_path_final_release_gate_needs_effluent_label"
        )
        manifest["latest_agent54_next_recommended_core_action"] = readiness.get("next_recommended_core_action")
    if isinstance(training_metrics, dict):
        layout_holdout = training_metrics.get("layout_holdout", {})
        layout_holdout = layout_holdout if isinstance(layout_holdout, dict) else {}
        manifest["latest_soft_sensor_model_version"] = training_metrics.get("model_version")
        manifest["latest_soft_sensor_feature_count"] = len(training_metrics.get("features", []) or [])
        manifest["latest_soft_sensor_hydraulic_path_feature_count"] = len(
            training_metrics.get("hydraulic_path_features", []) or []
        )
        manifest["latest_soft_sensor_mean_mae"] = training_metrics.get("mean_mae")
        manifest["latest_soft_sensor_hydraulic_path_feature_status"] = training_metrics.get(
            "hydraulic_path_feature_variation_status"
        )
        manifest["latest_soft_sensor_layout_variant_count"] = len(training_metrics.get("layout_variants", []) or [])
        manifest["latest_soft_sensor_layout_holdout_status"] = layout_holdout.get("status")
        manifest["latest_soft_sensor_layout_holdout_mean_mae"] = layout_holdout.get("mean_mae")
    manifest["next_stage"] = (
        "R8u-65 已形成 P5 软传感 synthetic layout holdout/path-stage contract；下一步应补真实 "
        "path_stage/endpoint labels、node-specific field values、final effluent 端点标签和 release gate validation"
    )
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def _field_path_endpoint_label_template(contract: dict[str, object]) -> dict[str, list[dict[str, object]]]:
    table_contracts = contract.get("table_contracts", {})
    table_contracts = table_contracts if isinstance(table_contracts, dict) else {}
    template: dict[str, list[dict[str, object]]] = {}
    for table, spec in table_contracts.items():
        spec = spec if isinstance(spec, dict) else {}
        required_fields = [str(field) for field in spec.get("required_fields", [])]
        row = {field: f"TODO_{field}" for field in required_fields}
        row["template_only"] = True
        row["evidence_status"] = "template_not_field_evidence"
        row["field_boundary"] = "replace every TODO/template value with real field rows before preflight"
        template[str(table)] = [row]
    return template


if __name__ == "__main__":
    main()
