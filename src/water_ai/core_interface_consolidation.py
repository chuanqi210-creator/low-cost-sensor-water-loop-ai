from __future__ import annotations

from typing import Any

from water_ai.field_control_replay_package import (
    ACTUATOR_TABLE,
    EXPERT_LABEL_TABLE,
    REWARD_TABLE,
    TABLE_COLUMNS as CONTROL_REPLAY_TABLE_COLUMNS,
    TRANSITION_TABLE,
    UNSAFE_TABLE,
)


CONSOLIDATION_ID = "R8u158_core_interface_consolidation_facade"

HIDDEN_SUPPORT_AXES = (
    "pollutant_residual_observability",
    "reaction_completion_observability",
    "oxidant_observability",
    "catalyst_activity_observability",
    "matrix_interference_observability",
    "hydraulic_observability",
    "fault_classification_observability",
    "soft_sensor_reconstruction_gain",
)


def build_core_interface_consolidation(
    *,
    agent48_metrics: dict[str, Any],
    field_control_replay_preflight: dict[str, Any],
    sparse_topology_installability_preflight: dict[str, Any],
    grey_box_collection_work_order: dict[str, Any],
    grey_box_submission_readiness_gate: dict[str, Any] | None = None,
    external_package_acquisition_maturity_gate: dict[str, Any],
    agent52_replay_metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Consolidate high-value model interfaces without adding another linear agent."""

    lifecycle = _external_package_lifecycle(
        grey_box_collection_work_order=grey_box_collection_work_order,
        grey_box_submission_readiness_gate=grey_box_submission_readiness_gate or {},
        field_control_replay_preflight=field_control_replay_preflight,
        sparse_topology_installability_preflight=sparse_topology_installability_preflight,
        external_package_acquisition_maturity_gate=external_package_acquisition_maturity_gate,
    )
    sparse_benchmark = _sparse_layout_soft_sensor_coupling_benchmark(agent48_metrics)
    control_crosswalk = _field_control_replay_crosswalk(
        field_control_replay_preflight=field_control_replay_preflight,
        agent52_replay_metrics=agent52_replay_metrics or {},
    )
    return {
        "consolidation_id": CONSOLIDATION_ID,
        "facade_type": "core_interface_consolidation",
        "architecture_layers": [
            "verification_governance",
            "observation",
            "state_estimation",
            "closed_loop_execution",
        ],
        "enhanced_abilities": [
            "verifiability",
            "engineering_feasibility",
            "evolvability",
            "observability",
            "controllability",
        ],
        "facade_count": 3,
        "facades": {
            "external_package_lifecycle": lifecycle,
            "sparse_layout_soft_sensor_coupling_benchmark": sparse_benchmark,
            "field_control_replay_crosswalk": control_crosswalk,
        },
        "subagent_synthesis": [
            {
                "source": "Mendel_agent_chain_audit",
                "finding": "linear agent growth should be compressed into facade/schema interfaces",
                "absorbed_as": "external_package_lifecycle",
            },
            {
                "source": "Euclid_agent48_sparse_sensing_audit",
                "finding": "layout strategies need a shared soft-sensor/missingness benchmark",
                "absorbed_as": "sparse_layout_soft_sensor_coupling_benchmark",
            },
            {
                "source": "Gauss_agent49_control_replay_audit",
                "finding": "field control replay package needs an Agent52 schema crosswalk",
                "absorbed_as": "field_control_replay_crosswalk",
            },
        ],
        "priority_decision": _priority_decision(lifecycle, sparse_benchmark, control_crosswalk),
        "boundary": _boundary(),
    }


def core_interface_consolidation_report_md(consolidation: dict[str, Any]) -> str:
    lifecycle = consolidation["facades"]["external_package_lifecycle"]
    benchmark = consolidation["facades"]["sparse_layout_soft_sensor_coupling_benchmark"]
    crosswalk = consolidation["facades"]["field_control_replay_crosswalk"]
    priority = consolidation["priority_decision"]
    lines = [
        "# Core Interface Consolidation Facade",
        "",
        "## Role",
        "",
        (
            "This R8u158 artifact compresses the current core model work into three machine-readable "
            "facades: external package lifecycle, sparse-layout soft-sensor coupling, and field-control "
            "replay schema crosswalk. It is not a field validation result and cannot generate field evidence."
        ),
        "",
        "## Status",
        "",
        f"- consolidation_id: `{consolidation['consolidation_id']}`",
        f"- facade_count: `{consolidation['facade_count']}`",
        f"- top_external_action_env_var: `{priority['top_external_action_env_var']}`",
        f"- top_external_action: `{priority['top_external_action']}`",
        f"- top_internal_action: `{priority['top_internal_action']}`",
        f"- new_agent_recommendation: `{priority['new_agent_recommendation']}`",
        "",
        "## Facades",
        "",
        f"- external_package_lifecycle: `{lifecycle['facade_status']}`",
        (
            "- sparse_layout_soft_sensor_coupling_benchmark: "
            f"`{benchmark['benchmark_status']}`"
        ),
        f"- field_control_replay_crosswalk: `{crosswalk['crosswalk_status']}`",
        "",
        "## External Package Lifecycle",
        "",
        "| package | env var | status | matched | submission readiness | downstream | next action |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in lifecycle["package_lifecycle_rows"]:
        submission_readiness = "{} / {}".format(
            row.get("submission_readiness_gate_status", "not_applicable"),
            row.get("submission_readiness_score", "n/a"),
        )
        if row.get("submission_missing_table_count"):
            submission_readiness = "{}; missing_tables={}".format(
                submission_readiness,
                row["submission_missing_table_count"],
            )
        lines.append(
            "| `{}` | `{}` | `{}` | `{}/{}` | `{}` | `{}` | `{}` |".format(
                row["package_key"],
                row["source_env_var"],
                row["package_status"],
                row["matched_unit_count"],
                row["minimum_matched_unit_count"],
                submission_readiness,
                row["downstream_consumer"],
                row["next_operator_action"],
            )
        )
    lines.extend(
        [
            "",
            "## Sparse Layout Coupling Benchmark",
            "",
            "| rank | strategy | score | catalyst support | missingness robustness | pressure/headloss penalty |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in benchmark["layout_benchmark_rows"]:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                row["rank"],
                row["strategy_id"],
                row["layout_coupling_score"],
                row["catalyst_activity_support"],
                row["missingness_robustness_score"],
                row["pressure_headloss_gap_penalty"],
            )
        )
    lines.extend(
        [
            "",
            "## Field Control Replay Crosswalk",
            "",
            "| source table | target fields | required for |",
            "| --- | --- | --- |",
        ]
    )
    for row in crosswalk["table_to_replay_schema_rows"]:
        lines.append(
            f"| `{row['source_table']}` | `{row['agent52_target_fields']}` | `{row['required_for']}` |"
        )
    lines.extend(
        [
            "",
            "## Cannot Claim",
            "",
        ]
    )
    for claim in sorted(set(benchmark["cannot_claim"] + crosswalk["cannot_claim"])):
        lines.append(f"- {claim}")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            (
                "This facade cannot generate field evidence, cannot resume the model chain, "
                "cannot write actuator policy and cannot write a release gate."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def _external_package_lifecycle(
    *,
    grey_box_collection_work_order: dict[str, Any],
    grey_box_submission_readiness_gate: dict[str, Any],
    field_control_replay_preflight: dict[str, Any],
    sparse_topology_installability_preflight: dict[str, Any],
    external_package_acquisition_maturity_gate: dict[str, Any],
) -> dict[str, Any]:
    grey_box_row = _package_lifecycle_row(
        package_key="grey_box_calibration",
        source_env_var=str(grey_box_collection_work_order.get("source_env_var", "GREY_BOX_CALIBRATION_PACKAGE_DIR")),
        package_status=str(
            grey_box_collection_work_order.get(
                "work_order_status",
                grey_box_collection_work_order.get("package_status", "unknown"),
            )
        ),
        matched_unit_kind="batch",
        matched_unit_count=_int(grey_box_collection_work_order.get("matched_batch_count", 0)),
        minimum_matched_unit_count=_int(grey_box_collection_work_order.get("minimum_matched_batch_count", 3)),
        downstream_consumer="Agent53_minimal_grey_box_physics",
        next_operator_action=str(grey_box_collection_work_order.get("next_operator_action", "")),
        can_route_downstream=bool(grey_box_collection_work_order.get("agent53_field_candidate_ready", False)),
    )
    grey_box_row.update(_grey_box_submission_readiness_projection(grey_box_submission_readiness_gate))
    rows = [
        grey_box_row,
        _package_lifecycle_row(
            package_key="field_control_replay",
            source_env_var=str(field_control_replay_preflight.get("source_env_var", "FIELD_CONTROL_REPLAY_PACKAGE_DIR")),
            package_status=str(field_control_replay_preflight.get("package_status", "unknown")),
            matched_unit_kind="transition",
            matched_unit_count=_int(field_control_replay_preflight.get("matched_transition_count", 0)),
            minimum_matched_unit_count=_int(field_control_replay_preflight.get("minimum_matched_transition_count", 3)),
            downstream_consumer="Agent49_52_offline_control_replay",
            next_operator_action=str(field_control_replay_preflight.get("next_operator_action", "")),
            can_route_downstream=bool(
                field_control_replay_preflight.get("can_route_to_agent52_policy_replay_evaluation", False)
            ),
        ),
        _package_lifecycle_row(
            package_key="sparse_topology_installability",
            source_env_var=str(
                sparse_topology_installability_preflight.get(
                    "source_env_var",
                    "SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR",
                )
            ),
            package_status=str(sparse_topology_installability_preflight.get("package_status", "unknown")),
            matched_unit_kind="node",
            matched_unit_count=_int(sparse_topology_installability_preflight.get("matched_node_count", 0)),
            minimum_matched_unit_count=_int(sparse_topology_installability_preflight.get("minimum_matched_node_count", 3)),
            downstream_consumer="Agent48_54_layout_holdout",
            next_operator_action=str(sparse_topology_installability_preflight.get("next_operator_action", "")),
            can_route_downstream=bool(
                sparse_topology_installability_preflight.get("can_route_to_agent48_sparse_layout_holdout", False)
            ),
        ),
    ]
    ready_count = sum(1 for row in rows if row["can_route_downstream"])
    waiting_count = len(rows) - ready_count
    return {
        "facade_id": "R8u158_external_package_lifecycle_facade",
        "facade_status": (
            "external_package_lifecycle_ready_for_downstream_gates"
            if ready_count == len(rows)
            else "external_package_lifecycle_waiting_for_field_packages"
        ),
        "source_maturity_gate_status": str(external_package_acquisition_maturity_gate.get("gate_status", "unknown")),
        "source_field_package_ready_rate": float(
            external_package_acquisition_maturity_gate.get("field_package_ready_rate", 0.0) or 0.0
        ),
        "package_lifecycle_rows": rows,
        "ready_package_count": ready_count,
        "waiting_package_count": waiting_count,
        "next_external_action_env_var": str(
            external_package_acquisition_maturity_gate.get(
                "next_operator_source_env_var",
                rows[0]["source_env_var"],
            )
        ),
        "next_external_action": str(
            external_package_acquisition_maturity_gate.get(
                "next_operator_action",
                rows[0]["next_operator_action"],
            )
        ),
        "boundary": _boundary(),
    }


def _package_lifecycle_row(
    *,
    package_key: str,
    source_env_var: str,
    package_status: str,
    matched_unit_kind: str,
    matched_unit_count: int,
    minimum_matched_unit_count: int,
    downstream_consumer: str,
    next_operator_action: str,
    can_route_downstream: bool,
) -> dict[str, Any]:
    return {
        "package_key": package_key,
        "source_env_var": source_env_var,
        "package_status": package_status,
        "matched_unit_kind": matched_unit_kind,
        "matched_unit_count": matched_unit_count,
        "minimum_matched_unit_count": minimum_matched_unit_count,
        "downstream_consumer": downstream_consumer,
        "next_operator_action": next_operator_action or f"set_{source_env_var}_and_run_package_preflight",
        "can_route_downstream": can_route_downstream,
        "can_generate_field_evidence": False,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }


def _grey_box_submission_readiness_projection(gate: dict[str, Any]) -> dict[str, Any]:
    highest_priority_gap = _dict(gate.get("highest_priority_gap"))
    gate_status = str(
        gate.get(
            "gate_status",
            "grey_box_submission_readiness_gate_not_consumed_by_core_interface",
        )
    )
    return {
        "submission_readiness_gate_id": str(
            gate.get("gate_id", "R8u160_grey_box_submission_readiness_gate")
        ),
        "submission_readiness_gate_status": gate_status,
        "submission_readiness_score": round(_float(gate.get("readiness_score", 0.0)), 3),
        "submission_highest_priority_gap_type": str(
            highest_priority_gap.get("gap_type", "not_consumed_by_core_interface")
        ),
        "submission_highest_priority_gap_table": str(highest_priority_gap.get("table", "")),
        "submission_missing_table_count": _int(highest_priority_gap.get("missing_table_count", 0)),
        "submission_missing_tables": [
            str(item) for item in highest_priority_gap.get("missing_tables", [])
        ],
        "submission_source_env_var": str(highest_priority_gap.get("source_env_var", "")),
        "can_submit_to_agent53_field_calibration": bool(
            gate.get("can_submit_to_agent53_field_calibration", False)
        ),
        "can_submit_to_agent53_field_candidate": bool(
            gate.get("can_submit_to_agent53_field_candidate", False)
        ),
        "submission_gate_can_generate_field_evidence": bool(
            gate.get("can_generate_field_evidence", False)
        ),
        "submission_gate_can_write_to_actuator": bool(gate.get("can_write_to_actuator", False)),
        "submission_gate_can_write_to_release_gate": bool(
            gate.get("can_write_to_release_gate", False)
        ),
    }


def _sparse_layout_soft_sensor_coupling_benchmark(agent48_metrics: dict[str, Any]) -> dict[str, Any]:
    comparison = agent48_metrics.get("algorithm_comparison", [])
    if not isinstance(comparison, list):
        comparison = []
    rows = [_layout_benchmark_row(item) for item in comparison if isinstance(item, dict)]
    rows.sort(key=lambda row: (-float(row["layout_coupling_score"]), str(row["strategy_id"])))
    for rank, row in enumerate(rows, start=1):
        row["rank"] = rank
    hard_blockers = sorted(
        {
            "catalyst_activity"
            for row in rows
            if float(row["catalyst_activity_support"]) < 0.55
        }
        | {
            "pressure_headloss_field_proxy"
            for row in rows
            if float(row["pressure_headloss_gap_penalty"]) > 0.0
        }
        | {"field_topology", "field_missingness_replay"}
    )
    return {
        "facade_id": "R8u158_sparse_layout_soft_sensor_coupling_benchmark",
        "benchmark_status": "synthetic_layout_coupling_benchmark_ready_needs_field_topology_missingness_labels",
        "strategy_count": len(rows),
        "layout_benchmark_rows": rows,
        "score_formula": (
            "0.24*comparable + 0.18*masked_state_support + 0.16*catalyst_support + "
            "0.14*missingness_robustness + 0.12*budget + 0.10*schema - pressure_headloss_penalty"
        ),
        "hard_blockers": hard_blockers,
        "cannot_claim": [
            "cannot claim field soft-sensor accuracy",
            "cannot claim field-optimal sensor placement",
            "cannot claim catalyst deactivation is validated",
            "cannot relax Agent49 catalyst guardrail",
            "cannot write actuator policy",
            "cannot write release gate",
        ],
        "boundary": _boundary(),
    }


def _layout_benchmark_row(strategy: dict[str, Any]) -> dict[str, Any]:
    coverage = _dict(strategy.get("coverage"))
    selected = strategy.get("selected_sensor_plan", [])
    selected = selected if isinstance(selected, list) else []
    selected_ids = [str(item.get("candidate_id", "")) for item in selected if isinstance(item, dict)]
    comparable = _float(strategy.get("comparable_score", 0.0))
    masked_support = _mean(_float(coverage.get(axis, 0.0)) for axis in HIDDEN_SUPPORT_AXES)
    catalyst_support = _float(coverage.get("catalyst_activity_observability", 0.0))
    missingness_scores = _missingness_stress_scores(selected)
    missingness_robustness = round(
        0.45 * _float(strategy.get("robustness_objective", 0.0))
        + 0.35 * _mean(missingness_scores.values())
        + 0.20 * _float(strategy.get("layout_redundancy_score", 0.0)),
        3,
    )
    pressure_penalty = 0.0 if _has_pressure_or_headloss(selected) else 0.12
    budget_score = _float(coverage.get("cost_efficiency", strategy.get("cost_objective", 0.0)))
    schema_readiness = 0.86 if selected_ids and coverage else 0.0
    score = round(
        max(
            0.0,
            min(
                1.0,
                0.24 * comparable
                + 0.18 * masked_support
                + 0.16 * catalyst_support
                + 0.14 * missingness_robustness
                + 0.12 * budget_score
                + 0.10 * schema_readiness
                - pressure_penalty,
            ),
        ),
        3,
    )
    return {
        "rank": 0,
        "strategy_id": str(strategy.get("strategy_id", "unknown_strategy")),
        "selected_sensor_ids": selected_ids,
        "selected_sensor_count": len(selected_ids),
        "total_cost_index": _float(coverage.get("total_cost_index", 0.0)),
        "comparable_score": comparable,
        "masked_state_support_mean": round(masked_support, 3),
        "catalyst_activity_support": round(catalyst_support, 3),
        "missingness_stress_scores": missingness_scores,
        "missingness_robustness_score": missingness_robustness,
        "pressure_headloss_gap_penalty": pressure_penalty,
        "budget_score": round(budget_score, 3),
        "soft_sensor_schema_readiness": schema_readiness,
        "weak_axis_gap_count": _int(strategy.get("weak_axis_gap_count", 0)),
        "layout_coupling_score": score,
        "can_finalize_field_deployment": False,
        "can_relax_agent49": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "field_boundary": (
            "synthetic coupling benchmark only; field topology, missingness replay and catalyst labels "
            "are required before deployment or control relaxation"
        ),
    }


def _missingness_stress_scores(selected: list[Any]) -> dict[str, float]:
    pairs = {
        str(item.get("candidate_id", "")): item
        for item in selected
        if isinstance(item, dict)
    }
    modalities_by_node: dict[str, set[str]] = {}
    for item in selected:
        if not isinstance(item, dict):
            continue
        modalities_by_node.setdefault(str(item.get("node_id", "")), set()).add(str(item.get("modality", "")))
    catalyst_modalities = modalities_by_node.get("N3_catalyst_bed_outlet", set())
    return {
        "catalyst_bed_uv_orp_missing": 0.82 if catalyst_modalities & {"UV254_abs", "ORP_mV"} else 0.34,
        "recycle_delay_missing": 0.78 if "N4_recirculation_loop" in modalities_by_node else 0.42,
        "matrix_shock_fast_proxy_missing": 0.80 if {"N0_influent", "N1_equalization_tank"} & set(modalities_by_node) else 0.48,
        "single_point_dropout": round(max(0.25, min(0.9, 0.36 + 0.06 * len(pairs))), 3),
    }


def _has_pressure_or_headloss(selected: list[Any]) -> bool:
    for item in selected:
        if not isinstance(item, dict):
            continue
        modality = str(item.get("modality", "")).lower()
        candidate_id = str(item.get("candidate_id", "")).lower()
        if "pressure" in modality or "headloss" in modality or "pressure" in candidate_id or "headloss" in candidate_id:
            return True
    return False


def _field_control_replay_crosswalk(
    *,
    field_control_replay_preflight: dict[str, Any],
    agent52_replay_metrics: dict[str, Any],
) -> dict[str, Any]:
    del agent52_replay_metrics
    preflight_pass = bool(field_control_replay_preflight.get("package_preflight_pass", False))
    return {
        "facade_id": "R8u158_field_control_replay_crosswalk",
        "crosswalk_status": (
            "field_control_replay_crosswalk_ready_for_agent52_schema_check"
            if preflight_pass
            else "field_control_replay_crosswalk_ready_waiting_for_FIELD_CONTROL_REPLAY_PACKAGE_DIR"
        ),
        "source_env_var": str(field_control_replay_preflight.get("source_env_var", "FIELD_CONTROL_REPLAY_PACKAGE_DIR")),
        "matched_transition_count": _int(field_control_replay_preflight.get("matched_transition_count", 0)),
        "minimum_matched_transition_count": _int(field_control_replay_preflight.get("minimum_matched_transition_count", 3)),
        "table_to_replay_schema_rows": _control_replay_crosswalk_rows(),
        "policy_candidate_columns": [
            "agent49_policy",
            "guardrail_aware_policy",
            "safe_standby_rule",
            "release_first_rule",
            "random_baseline",
            "expert_upper_bound",
        ],
        "release_gate_requirements": {
            "package_preflight_pass": preflight_pass,
            "field_replay_coverage_min": 0.85,
            "joint_action_accuracy_min": 0.90,
            "reward_regret_max": 0.08,
            "requires_catalyst_proxy_holdout_pass": True,
            "requires_pressure_source_conflict_cleared": True,
            "requires_operator_review": True,
            "can_authorize_policy_promotion": False,
            "can_generate_field_evidence": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        },
        "cannot_claim": [
            "cannot claim field policy superiority",
            "cannot claim online MARL readiness",
            "cannot authorize actuator writes",
            "cannot authorize release gate writes",
        ],
        "boundary": _boundary(),
    }


def _control_replay_crosswalk_rows() -> list[dict[str, Any]]:
    return [
        {
            "source_table": TRANSITION_TABLE,
            "source_columns": CONTROL_REPLAY_TABLE_COLUMNS[TRANSITION_TABLE],
            "agent52_target_fields": [
                "transition_id",
                "batch_id",
                "facility_id",
                "state_vector_ref",
                "action_id",
                "next_state_vector_ref",
                "observed_outcome",
            ],
            "required_for": "state-action-next-state replay row",
        },
        {
            "source_table": REWARD_TABLE,
            "source_columns": CONTROL_REPLAY_TABLE_COLUMNS[REWARD_TABLE],
            "agent52_target_fields": [
                "reward_components",
                "component_value",
                "component_weight",
                "objective_direction",
            ],
            "required_for": "reward calculation and regret audit",
        },
        {
            "source_table": EXPERT_LABEL_TABLE,
            "source_columns": CONTROL_REPLAY_TABLE_COLUMNS[EXPERT_LABEL_TABLE],
            "agent52_target_fields": [
                "expert_action_id",
                "expert_action_label",
                "action_match_required",
            ],
            "required_for": "joint action accuracy and policy distillation audit",
        },
        {
            "source_table": ACTUATOR_TABLE,
            "source_columns": CONTROL_REPLAY_TABLE_COLUMNS[ACTUATOR_TABLE],
            "agent52_target_fields": [
                "actuator_id",
                "commanded_action_id",
                "latency_min",
                "execution_result",
            ],
            "required_for": "execution feasibility and latency guardrail",
        },
        {
            "source_table": UNSAFE_TABLE,
            "source_columns": CONTROL_REPLAY_TABLE_COLUMNS[UNSAFE_TABLE],
            "agent52_target_fields": [
                "unsafe_action_flag",
                "override_flag",
                "override_reason",
                "human_review_required",
            ],
            "required_for": "operator review and no-write safety boundary",
        },
    ]


def _priority_decision(
    lifecycle: dict[str, Any],
    benchmark: dict[str, Any],
    crosswalk: dict[str, Any],
) -> dict[str, Any]:
    return {
        "decision_id": "R8u158_priority_after_subagent_synthesis",
        "top_external_action_env_var": lifecycle["next_external_action_env_var"],
        "top_external_action": lifecycle["next_external_action"],
        "top_internal_action": (
            "maintain_core_interface_facades_and_refresh_only_when field packages, "
            "Agent48 layout metrics or Agent52 replay schema change"
        ),
        "new_agent_recommendation": "do_not_add_linear_agent",
        "why": [
            "external field package ready rate is still zero",
            "Agent48 and Agent49 already have candidate logic; current gap is interface alignment",
            "facades reduce scan friction and prevent duplicate schema/report growth",
        ],
        "completed_internal_consolidations": [
            benchmark["facade_id"],
            crosswalk["facade_id"],
            lifecycle["facade_id"],
        ],
    }


def _boundary() -> dict[str, bool | str]:
    return {
        "can_generate_field_evidence": False,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "can_emit_field_supported_claim": False,
        "boundary_statement": (
            "This facade is a synthetic/interface consolidation artifact. It can guide package "
            "collection, benchmark schema readiness and replay crosswalks, but it cannot substitute "
            "for field replay, holdout, calibration, operator review, actuator gates or release gates."
        ),
    }


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _mean(values: Any) -> float:
    items = [float(value) for value in values]
    if not items:
        return 0.0
    return sum(items) / len(items)
