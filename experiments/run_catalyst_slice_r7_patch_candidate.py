from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from water_ai.catalyst_slice_r7_patch_candidate import (
    BASE_PACKAGE_ENV_VAR,
    CANDIDATE_PACKAGE_ENV_VAR,
    SLICE_ENV_VAR,
    build_catalyst_slice_r7_patch_candidate,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "outputs" / "catalyst_slice_r7_patch_candidate"
DEFAULT_CANDIDATE_DIR = OUT_DIR / "r7_patch_candidate_package"
METRICS_PATH = OUT_DIR / "catalyst_slice_r7_patch_candidate_metrics.json"
DELIVERABLE_PATH = PROJECT_ROOT / "deliverables" / "model_core_optimization" / "catalyst_slice_r7_patch_candidate.md"
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLE_PATH.parent.mkdir(parents=True, exist_ok=True)

    slice_path = os.environ.get(SLICE_ENV_VAR, "").strip()
    base_path = os.environ.get(BASE_PACKAGE_ENV_VAR, "").strip()
    candidate_path = os.environ.get(CANDIDATE_PACKAGE_ENV_VAR, "").strip()
    candidate_dir = Path(candidate_path).expanduser().resolve() if candidate_path else DEFAULT_CANDIDATE_DIR
    result = build_catalyst_slice_r7_patch_candidate(
        slice_dir=slice_path or None,
        candidate_dir=candidate_dir,
        base_package_dir=base_path or None,
        external_slice_supplied=bool(slice_path and Path(slice_path).exists()),
        base_package_supplied=bool(base_path),
    )
    result["candidate_package_dir_relative"] = _relative_or_absolute(Path(result["candidate_package_dir"]))
    METRICS_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    DELIVERABLE_PATH.write_text(_deliverable_md(result), encoding="utf-8")
    _update_manifest(result)

    print(f"Catalyst slice R7 patch candidate: {result['patch_status']}")
    print(f"- slice pass: {result['slice_preflight_pass']}")
    print(f"- candidate materialized: {result['candidate_materialized']}")
    print(f"- candidate preflight: {result['candidate_preflight_status']}")
    print(f"- remaining gaps: {result['full_package_gap_summary']['remaining_gap_count']}")
    print(f"- next: {result['next_operator_action']}")


def _deliverable_md(result: dict[str, Any]) -> str:
    gap = result["full_package_gap_summary"]
    return "\n".join(
        [
            "# R8u114 Catalyst Slice To R7 Patch Candidate",
            "",
            "## 定位",
            "",
            (
                "该接口把 R8u113 的 catalyst_activity 四表切片覆盖进一个 full R7 field package candidate，"
                "并立即运行 R7 package preflight。它只生成补丁候选和剩余缺口，不生成 field validation。"
            ),
            "",
            "## Readiness",
            "",
            f"- patch_status: `{result['patch_status']}`",
            f"- source_env_var: `{result['source_env_var']}`",
            f"- base_package_env_var: `{result['base_package_env_var']}`",
            f"- candidate_package_env_var: `{result['candidate_package_env_var']}`",
            f"- slice_preflight_status: `{result['slice_preflight_status']}`",
            f"- slice_preflight_pass: `{result['slice_preflight_pass']}`",
            f"- slice_matched_batch_count: `{result['slice_matched_batch_count']}`",
            f"- candidate_materialized: `{result['candidate_materialized']}`",
            f"- candidate_package_dir: `{result['candidate_package_dir_relative']}`",
            f"- candidate_preflight_status: `{result['candidate_preflight_status']}`",
            f"- can_submit_candidate_as_REAL_FIELD_REPLAY_PACKAGE_DIR: `{result['can_submit_candidate_as_REAL_FIELD_REPLAY_PACKAGE_DIR']}`",
            f"- can_route_to_agent51_field_proxy_holdout: `{result['can_route_to_agent51_field_proxy_holdout']}`",
            "",
            "## Full Package Gaps",
            "",
            f"- required_file_count: `{gap['required_file_count']}`",
            f"- missing_required_files: `{gap['missing_required_files']}`",
            f"- header_blocked_tables: `{gap['header_blocked_tables']}`",
            f"- placeholder_metadata_fields: `{gap['placeholder_metadata_fields']}`",
            f"- header_only_required_tables: `{gap['header_only_required_tables']}`",
            f"- remaining_gap_count: `{gap['remaining_gap_count']}`",
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
    manifest["latest_catalyst_slice_r7_patch_candidate_metrics"] = str(METRICS_PATH.relative_to(PROJECT_ROOT))
    manifest["latest_catalyst_slice_r7_patch_candidate_doc"] = str(DELIVERABLE_PATH.relative_to(PROJECT_ROOT))
    manifest["latest_catalyst_slice_r7_patch_candidate_dir"] = result["candidate_package_dir_relative"]
    manifest["latest_catalyst_slice_r7_patch_candidate_status"] = result["patch_status"]
    manifest["latest_catalyst_slice_r7_patch_candidate_materialized"] = result["candidate_materialized"]
    manifest["latest_catalyst_slice_r7_patch_candidate_preflight_status"] = result["candidate_preflight_status"]
    manifest["latest_catalyst_slice_r7_patch_candidate_remaining_gap_count"] = result[
        "full_package_gap_summary"
    ]["remaining_gap_count"]
    manifest["latest_catalyst_slice_r7_patch_candidate_can_submit_as_REAL_FIELD_REPLAY_PACKAGE_DIR"] = result[
        "can_submit_candidate_as_REAL_FIELD_REPLAY_PACKAGE_DIR"
    ]
    manifest["latest_catalyst_slice_r7_patch_candidate_next_operator_action"] = result["next_operator_action"]
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def _relative_or_absolute(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    main()
