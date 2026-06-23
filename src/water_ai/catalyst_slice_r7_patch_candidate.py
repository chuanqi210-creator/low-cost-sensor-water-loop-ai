from __future__ import annotations

import csv
import shutil
from pathlib import Path
from typing import Any

from water_ai.agents.field_replay_import_agent import (
    field_replay_package_template_spec,
    preflight_field_replay_package,
    write_field_replay_package_template,
)
from water_ai.catalyst_field_package_slice import (
    REQUIRED_TABLES as CATALYST_SLICE_TABLES,
    SOURCE_ENV_VAR as SLICE_ENV_VAR,
    build_catalyst_field_package_slice_preflight,
)


PATCH_ID = "R8u114_catalyst_slice_r7_patch_candidate"
BASE_PACKAGE_ENV_VAR = "R7_BASE_FIELD_PACKAGE_DIR"
CANDIDATE_PACKAGE_ENV_VAR = "CATALYST_R7_PATCH_CANDIDATE_DIR"


def build_catalyst_slice_r7_patch_candidate(
    *,
    slice_dir: str | Path | None = None,
    candidate_dir: str | Path,
    base_package_dir: str | Path | None = None,
    external_slice_supplied: bool = False,
    base_package_supplied: bool = False,
) -> dict[str, Any]:
    """Overlay a valid catalyst field-package slice onto a full R7 package candidate."""

    source = Path(slice_dir) if slice_dir not in (None, "") else None
    candidate = Path(candidate_dir)
    base = Path(base_package_dir) if base_package_dir not in (None, "") else None
    slice_preflight = build_catalyst_field_package_slice_preflight(
        source_dir=source,
        external_slice_supplied=external_slice_supplied,
    )
    if not slice_preflight["slice_preflight_pass"]:
        return _payload(
            slice_preflight=slice_preflight,
            candidate_dir=candidate,
            base_package_dir=base,
            base_package_supplied=base_package_supplied,
            patch_status="catalyst_slice_r7_patch_waiting_for_valid_catalyst_slice",
            candidate_materialized=False,
            overlay_audit={},
            candidate_preflight={},
            full_package_gap_summary=_empty_full_package_gap_summary(),
        )

    if base_package_supplied and (base is None or not base.exists() or not base.is_dir()):
        return _payload(
            slice_preflight=slice_preflight,
            candidate_dir=candidate,
            base_package_dir=base,
            base_package_supplied=base_package_supplied,
            patch_status="catalyst_slice_r7_patch_blocked_by_missing_base_package",
            candidate_materialized=False,
            overlay_audit={},
            candidate_preflight={},
            full_package_gap_summary=_empty_full_package_gap_summary(),
        )

    _prepare_candidate_dir(candidate, base if base_package_supplied else None)
    overlay_audit = _overlay_slice_tables(source, candidate)
    candidate_preflight = preflight_field_replay_package(candidate)
    gap_summary = _full_package_gap_summary(candidate_preflight)
    patch_status = _patch_status(candidate_preflight)
    return _payload(
        slice_preflight=slice_preflight,
        candidate_dir=candidate,
        base_package_dir=base,
        base_package_supplied=base_package_supplied,
        patch_status=patch_status,
        candidate_materialized=True,
        overlay_audit=overlay_audit,
        candidate_preflight=candidate_preflight,
        full_package_gap_summary=gap_summary,
    )


def _payload(
    *,
    slice_preflight: dict[str, Any],
    candidate_dir: Path,
    base_package_dir: Path | None,
    base_package_supplied: bool,
    patch_status: str,
    candidate_materialized: bool,
    overlay_audit: dict[str, Any],
    candidate_preflight: dict[str, Any],
    full_package_gap_summary: dict[str, Any],
) -> dict[str, Any]:
    candidate_preflight_status = str(candidate_preflight.get("status", "not_run"))
    full_preflight_pass = candidate_preflight_status == "field_package_preflight_ready_for_agent42"
    return {
        "patch_id": PATCH_ID,
        "patch_type": "catalyst_activity_slice_to_full_r7_package_patch_candidate",
        "source_env_var": SLICE_ENV_VAR,
        "base_package_env_var": BASE_PACKAGE_ENV_VAR,
        "candidate_package_env_var": CANDIDATE_PACKAGE_ENV_VAR,
        "source_slice_path": slice_preflight.get("source_path", ""),
        "base_package_path": "" if base_package_dir is None else str(base_package_dir),
        "base_package_supplied": base_package_supplied,
        "candidate_package_dir": str(candidate_dir),
        "patch_status": patch_status,
        "slice_preflight_status": slice_preflight.get("slice_status", "unknown"),
        "slice_preflight_pass": bool(slice_preflight.get("slice_preflight_pass", False)),
        "slice_matched_batch_count": int(slice_preflight.get("matched_batch_count", 0) or 0),
        "candidate_materialized": candidate_materialized,
        "overlay_audit": overlay_audit,
        "candidate_preflight_status": candidate_preflight_status,
        "candidate_preflight": candidate_preflight,
        "full_package_gap_summary": full_package_gap_summary,
        "can_run_r7_import_preflight_on_candidate": candidate_materialized,
        "can_submit_candidate_as_REAL_FIELD_REPLAY_PACKAGE_DIR": full_preflight_pass,
        "can_route_to_agent51_field_proxy_holdout": False,
        "can_relax_agent49_catalyst_uncertainty_block": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "next_operator_action": _next_operator_action(patch_status, full_preflight_pass),
        "field_boundary": (
            "This patch candidate only overlays the catalyst_activity four-table slice onto a full R7 package "
            "candidate. A valid slice can repair Agent51-focused rows, but it cannot replace metadata, generic "
            "timestamped replay rows, fast proxy events, pressure-headloss events, path labels or release evidence."
        ),
        "no_write_boundary": (
            "R8u114 cannot authorize actuator writes, release-gate writes, Agent51 holdout pass, Agent49 guardrail "
            "relaxation or field-supported claims. Only a complete R7 package import/replay/holdout chain can do that."
        ),
    }


def _prepare_candidate_dir(candidate: Path, base: Path | None) -> None:
    if candidate.exists():
        shutil.rmtree(candidate)
    if base is None:
        write_field_replay_package_template(candidate)
        return
    shutil.copytree(base, candidate)


def _overlay_slice_tables(source: Path | None, candidate: Path) -> dict[str, Any]:
    if source is None:
        return {"overlay_pass": False, "blocking_reason": "missing_source_slice_dir"}
    table_results: dict[str, dict[str, Any]] = {}
    for table in CATALYST_SLICE_TABLES:
        source_csv = source / f"{table}.csv"
        target_csv = candidate / f"{table}.csv"
        shutil.copyfile(source_csv, target_csv)
        row_count, headers = _csv_shape(target_csv)
        table_results[table] = {
            "source_csv": str(source_csv),
            "target_csv": str(target_csv),
            "row_count": row_count,
            "headers": headers,
        }
    return {
        "overlay_pass": True,
        "patched_table_count": len(table_results),
        "patched_tables": sorted(table_results),
        "table_results": table_results,
    }


def _csv_shape(path: Path) -> tuple[int, list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = list(reader.fieldnames or [])
        row_count = sum(1 for _ in reader)
    return row_count, headers


def _full_package_gap_summary(candidate_preflight: dict[str, Any]) -> dict[str, Any]:
    if not candidate_preflight:
        return _empty_full_package_gap_summary()
    spec = field_replay_package_template_spec()
    required_files = [str(item) for item in spec.get("required_files", [])]
    row_counts = {
        str(table): int(count or 0)
        for table, count in dict(candidate_preflight.get("row_counts", {})).items()
    }
    missing_required_files = _missing_required_files(candidate_preflight)
    header_blocked_tables = _header_blocked_tables(candidate_preflight)
    header_only_required_tables = [
        table
        for table, count in sorted(row_counts.items())
        if count <= 0
    ]
    return {
        "required_file_count": len(required_files),
        "missing_required_files": missing_required_files,
        "header_blocked_tables": header_blocked_tables,
        "placeholder_metadata_fields": list(candidate_preflight.get("placeholder_metadata_fields", [])),
        "header_only_required_tables": header_only_required_tables,
        "row_counts": row_counts,
        "remaining_gap_count": (
            len(missing_required_files)
            + len(header_blocked_tables)
            + len(candidate_preflight.get("placeholder_metadata_fields", []))
            + len(header_only_required_tables)
        ),
        "gap_boundary": (
            "A catalyst slice only covers four Agent51-focused tables. Remaining gaps must be repaired in the full "
            "R7 package before setting REAL_FIELD_REPLAY_PACKAGE_DIR."
        ),
    }


def _missing_required_files(candidate_preflight: dict[str, Any]) -> list[str]:
    file_audit = dict(candidate_preflight.get("file_audit", {}))
    missing = []
    if not file_audit.get("metadata_exists", False):
        missing.append("metadata.json")
    for table, audit in dict(file_audit.get("csv_files", {})).items():
        if not dict(audit).get("exists", False):
            missing.append(f"{table}.csv")
    return sorted(missing)


def _header_blocked_tables(candidate_preflight: dict[str, Any]) -> list[str]:
    file_audit = dict(candidate_preflight.get("file_audit", {}))
    blocked = []
    for table, audit in dict(file_audit.get("csv_files", {})).items():
        status = str(dict(audit).get("status", "unknown"))
        if status != "header_ready":
            blocked.append(str(table))
    return sorted(blocked)


def _empty_full_package_gap_summary() -> dict[str, Any]:
    return {
        "required_file_count": 0,
        "missing_required_files": [],
        "header_blocked_tables": [],
        "placeholder_metadata_fields": [],
        "header_only_required_tables": [],
        "row_counts": {},
        "remaining_gap_count": 0,
        "gap_boundary": "No candidate package preflight has run yet.",
    }


def _patch_status(candidate_preflight: dict[str, Any]) -> str:
    status = str(candidate_preflight.get("status", "not_run"))
    if status == "field_package_preflight_ready_for_agent42":
        return "catalyst_slice_r7_patch_candidate_ready_for_REAL_FIELD_REPLAY_PACKAGE_DIR"
    return "catalyst_slice_r7_patch_candidate_materialized_but_full_package_blocked"


def _next_operator_action(patch_status: str, full_preflight_pass: bool) -> str:
    if patch_status == "catalyst_slice_r7_patch_waiting_for_valid_catalyst_slice":
        return "fill_valid_catalyst_slice_and_set_CATALYST_FIELD_PACKAGE_SLICE_DIR"
    if patch_status == "catalyst_slice_r7_patch_blocked_by_missing_base_package":
        return "provide_existing_R7_BASE_FIELD_PACKAGE_DIR_or_let_runner_use_template_base"
    if full_preflight_pass:
        return "set_REAL_FIELD_REPLAY_PACKAGE_DIR_to_candidate_package_and_run_r7_pipeline"
    return "repair_remaining_full_r7_package_gaps_before_setting_REAL_FIELD_REPLAY_PACKAGE_DIR"
