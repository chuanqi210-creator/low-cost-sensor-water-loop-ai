from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from water_ai.observation_response_bridge import build_observation_response_bridge


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OBSERVATION_CONTRACT_METRICS_PATH = (
    PROJECT_ROOT / "outputs" / "observation_contract_merge" / "observation_contract_metrics.json"
)
RESPONSE_TEMPLATE_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "field_activation_response_template.json"
)
RESPONSE_SUBMISSION_PACKET_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "field_activation_response_submission_packet.json"
)
CATALYST_HOLDOUT_SUMMARY_PATH = (
    PROJECT_ROOT / "outputs" / "catalyst_activity_proxy" / "field_proxy_holdout_summary.json"
)
SOFT_SENSOR_MATRIX_METRICS_PATH = (
    PROJECT_ROOT / "outputs" / "soft_sensor_matrix_coupling" / "soft_sensor_matrix_metrics.json"
)
OUT_DIR = PROJECT_ROOT / "outputs" / "observation_response_bridge"
METRICS_PATH = OUT_DIR / "observation_response_bridge_metrics.json"
DELIVERABLE_PATH = PROJECT_ROOT / "deliverables" / "model_core_optimization" / "observation_response_bridge.md"
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLE_PATH.parent.mkdir(parents=True, exist_ok=True)

    result = build_observation_response_bridge(
        observation_contract_metrics=_read_json(OBSERVATION_CONTRACT_METRICS_PATH),
        response_template=_read_json(RESPONSE_TEMPLATE_PATH),
        response_submission_packet=_read_json(RESPONSE_SUBMISSION_PACKET_PATH),
        catalyst_holdout_summary=_read_json(CATALYST_HOLDOUT_SUMMARY_PATH),
        soft_sensor_matrix_metrics=_read_json(SOFT_SENSOR_MATRIX_METRICS_PATH),
    )
    METRICS_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    DELIVERABLE_PATH.write_text(_deliverable_md(result), encoding="utf-8")
    _update_manifest(result)

    print(f"Observation response bridge: {result['bridge_status']}")
    print(f"- target: {result['primary_target_hidden_state']}")
    print(f"- rows: {result['response_row_count']}")
    print(f"- role coverage: {result['required_role_coverage_rate']}")
    print(f"- next: {result['response_submission_next_operator_action']}")
    print(f"metrics: {METRICS_PATH}")
    print(f"deliverable: {DELIVERABLE_PATH}")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _deliverable_md(result: dict[str, Any]) -> str:
    lines = [
        "# R8u109 Observation Response Bridge",
        "",
        "## 定位",
        "",
        (
            "该桥把 R2/Agent48/51/54 的观测弱轴需求映射到 R8u108 field activation response "
            "template 中的优先响应行，避免现场补证时在完整模板里重新扫描 catalyst_activity 证据。"
        ),
        "",
        "## Readiness",
        "",
        f"- bridge_status: `{result['bridge_status']}`",
        f"- target_hidden_states: `{result['target_hidden_states']}`",
        f"- response_row_count: `{result['response_row_count']}`",
        f"- required_role_coverage_rate: `{result['required_role_coverage_rate']}`",
        f"- missing_required_roles: `{result['missing_required_roles']}`",
        f"- response_submission_packet_status: `{result['response_submission_packet_status']}`",
        f"- response_submission_next_operator_action: `{result['response_submission_next_operator_action']}`",
        f"- can_route_to_agent51_field_proxy_holdout: `{result['can_route_to_agent51_field_proxy_holdout']}`",
        f"- can_relax_agent49_catalyst_uncertainty_block: `{result['can_relax_agent49_catalyst_uncertainty_block']}`",
        f"- can_write_to_actuator: `{result['can_write_to_actuator']}`",
        f"- can_write_to_release_gate: `{result['can_write_to_release_gate']}`",
        "",
        "## Priority Response Rows",
        "",
        "| row | role | priority | table | field |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in result["priority_response_rows"]:
        lines.append(
            f"| `{row['response_row_id']}` | `{row['observation_role']}` | "
            f"`{row['priority']}` | `{row['table_name']}` | `{row['field_name']}` |"
        )
    lines.extend(
        [
            "",
            "## Batch Alignment",
            "",
            result["batch_alignment_policy"],
            "",
            "## No-Write Boundary",
            "",
            result["no_write_boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def _update_manifest(result: dict[str, Any]) -> None:
    manifest = _read_json(MANIFEST_PATH)
    manifest["latest_observation_response_bridge"] = str(METRICS_PATH.relative_to(PROJECT_ROOT))
    manifest["latest_observation_response_bridge_doc"] = str(DELIVERABLE_PATH.relative_to(PROJECT_ROOT))
    manifest["latest_observation_response_bridge_status"] = result["bridge_status"]
    manifest["latest_observation_response_bridge_target_hidden_state"] = result[
        "primary_target_hidden_state"
    ]
    manifest["latest_observation_response_bridge_response_row_count"] = result["response_row_count"]
    manifest["latest_observation_response_bridge_required_role_coverage_rate"] = result[
        "required_role_coverage_rate"
    ]
    manifest["latest_observation_response_bridge_can_route_to_agent51_field_proxy_holdout"] = result[
        "can_route_to_agent51_field_proxy_holdout"
    ]
    manifest["latest_observation_response_bridge_can_relax_agent49_catalyst_uncertainty_block"] = result[
        "can_relax_agent49_catalyst_uncertainty_block"
    ]
    manifest["latest_observation_response_bridge_can_write_to_actuator"] = result[
        "can_write_to_actuator"
    ]
    manifest["latest_observation_response_bridge_can_write_to_release_gate"] = result[
        "can_write_to_release_gate"
    ]
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
