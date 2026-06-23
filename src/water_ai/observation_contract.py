from __future__ import annotations

from dataclasses import dataclass
from typing import Any


DEFAULT_PATCH_MODALITY_COST = {
    "UV254_abs": 1.012,
    "ORP_mV": 0.756,
    "pressure_drop_kPa": 0.68,
    "flow_Lmin": 0.476,
    "turbidity_NTU": 0.749,
    "EC_uScm": 0.434,
}


@dataclass(frozen=True)
class ObservationContractMerge:
    """Facade that merges Agent48/51/54 into one layout-aware observation contract."""

    sparse_placement_metrics: dict[str, Any]
    catalyst_proxy_metrics: dict[str, Any]
    soft_sensor_matrix_metrics: dict[str, Any]

    def build(self) -> dict[str, Any]:
        base_layout = self._base_layout()
        patch_records = self._patch_records(base_layout)
        contract_candidates = self._contract_candidates(base_layout, patch_records)
        recommended = self._recommended_contract(contract_candidates)
        readiness = self._readiness(base_layout, patch_records, recommended)
        return {
            "method_contract": self._method_contract(),
            "base_layout_contract": base_layout,
            "proxy_patch_records": patch_records,
            "contract_candidates": contract_candidates,
            "recommended_observation_contract": recommended,
            "soft_sensor_schema_patch": self._soft_sensor_schema_patch(),
            "field_validation_requirements": self._field_validation_requirements(),
            "readiness": readiness,
            "writeback_policy": self._writeback_policy(readiness),
            "next_refactor_action": self._next_refactor_action(readiness),
        }

    @staticmethod
    def _method_contract() -> dict[str, Any]:
        return {
            "upgrade_id": "R2_agent48_51_54_observation_contract_merge",
            "borrowed_from": [
                "sparse sensor placement reconstruction/classification interface",
                "hidden-state requirement ledger from Agent48",
                "catalyst proxy observability patch from Agent51",
                "layout-aware missingness tensor contract from Agent54",
                "cost-aware replacement instead of blindly adding sensors",
            ],
            "reality_mapping": (
                "把 Agent48 的 node-modality 布点、Agent51 的 catalyst_activity 代理补点、"
                "Agent54 的软传感 mask/schema 合并为一个 observation contract。"
            ),
            "data_needs": [
                "selected_sensor_plan",
                "coverage_for_soft_sensor",
                "catalyst_proxy recommended_sensor_patches",
                "soft_sensor feature_contract and training_schema_gap",
                "field topology, node-specific values and proxy labels for validation",
            ],
            "evaluation_metrics": [
                "hidden_state_requirement_ledger.ready_hidden_state_count",
                "hidden_state_requirement_ledger.minimum_cost_requirement_patch.patch_status",
                "layout_alignment_pass",
                "proxy_enhanced_weak_state_coverage",
                "budget_rebalanced_cost_index",
                "estimated_missingness_robustness_after_patch",
                "schema_patch_term_count",
            ],
            "failure_boundary": (
                "R2 只能生成 synthetic/design-prior observation contract；没有 field topology、node-specific values、"
                "proxy holdout labels 和 missingness replay 前，不能最终定点、不能放松 Agent49 催化剂保护、不能写 release gate。"
            ),
        }

    def _base_layout(self) -> dict[str, Any]:
        selected = self._selected_sensor_plan()
        coverage = self._sparse_coverage()
        soft_contract = self._soft_feature_contract()
        sparse_interface = self.sparse_placement_metrics.get("soft_sensor_interface", {})
        sparse_interface = sparse_interface if isinstance(sparse_interface, dict) else {}
        soft_nodes = set(str(node) for node in soft_contract.get("selected_nodes", []))
        sparse_nodes = set(str(node) for node in sparse_interface.get("selected_nodes", []))
        soft_modalities = set(str(modality) for modality in soft_contract.get("selected_modalities", []))
        sparse_modalities = set(str(modality) for modality in sparse_interface.get("selected_modalities", []))
        hidden_ledger = self._hidden_state_requirement_ledger()
        hidden_patch = hidden_ledger.get("minimum_cost_requirement_patch", {})
        hidden_patch = hidden_patch if isinstance(hidden_patch, dict) else {}
        pressure_pool = hidden_ledger.get("pressure_headloss_candidate_pool", {})
        pressure_pool = pressure_pool if isinstance(pressure_pool, dict) else {}
        return {
            "layout_id": str(sparse_interface.get("layout_id") or soft_contract.get("layout_id", "missing_layout_id")),
            "selected_sensor_plan": selected,
            "selected_pairs": [str(item["candidate_id"]) for item in selected],
            "selected_nodes": sorted({str(item["node_id"]) for item in selected}),
            "selected_modalities": sorted({str(item["modality"]) for item in selected}),
            "coverage": coverage,
            "layout_alignment_pass": bool(soft_nodes == sparse_nodes and soft_modalities == sparse_modalities),
            "layout_alignment_detail": {
                "sparse_nodes": sorted(sparse_nodes),
                "soft_sensor_nodes": sorted(soft_nodes),
                "sparse_modalities": sorted(sparse_modalities),
                "soft_sensor_modalities": sorted(soft_modalities),
            },
            "base_total_cost_index": float(coverage.get("total_cost_index", 0.0)),
            "budget_limit": float(self._sparse_readiness().get("budget_limit", 5.8)),
            "current_weak_state_coverage": float(coverage.get("weak_state_coverage", 0.0)),
            "current_catalyst_activity_observability": float(
                coverage.get("catalyst_activity_observability", 0.0)
            ),
            "current_matrix_interference_observability": float(
                coverage.get("matrix_interference_observability", 0.0)
            ),
            "current_missingness_robustness_score": float(
                self._soft_readiness().get("missingness_robustness_score", 0.0)
            ),
            "hidden_state_requirement_ledger_status": str(hidden_ledger.get("ledger_status", "missing_hidden_state_ledger")),
            "hidden_state_ready_count": int(hidden_ledger.get("ready_hidden_state_count", 0) or 0),
            "hidden_state_count": int(hidden_ledger.get("hidden_state_count", 0) or 0),
            "hidden_state_unresolved_count": int(hidden_ledger.get("unresolved_hidden_state_count", 0) or 0),
            "hidden_state_minimum_patch_status": str(hidden_patch.get("patch_status", "missing_minimum_cost_patch")),
            "hidden_state_hard_unresolved": [
                str(item) for item in hidden_patch.get("hard_unresolved_hidden_states", [])
            ],
            "pressure_headloss_candidate_pool_status": str(pressure_pool.get("pool_status", "missing_pressure_headloss_pool")),
            "pressure_headloss_candidate_count": int(pressure_pool.get("candidate_count", 0) or 0),
            "pressure_headloss_candidate_ids": [
                str(item) for item in pressure_pool.get("candidate_ids", [])
            ],
            "pressure_headloss_field_package_contract": pressure_pool.get("field_package_contract", {}),
            "hidden_state_requirement_rows": hidden_ledger.get("state_rows", []),
            "field_boundary": "base layout is synthetic until field topology and node-specific timeseries are imported",
        }

    def _patch_records(self, base_layout: dict[str, Any]) -> list[dict[str, Any]]:
        recommended = self._proxy_metrics().get("recommended_sensor_patches", [])
        recommended = recommended if isinstance(recommended, list) else []
        repair_plan = self._weak_axis_repair_plan()
        repair_patch_index = self._repair_patch_index(repair_plan)
        selected_pairs = set(base_layout["selected_pairs"])
        selected_nodes = set(base_layout["selected_nodes"])
        modality_costs = self._inferred_modality_costs()
        proxy_support = self._proxy_support_by_signal()
        records: list[dict[str, Any]] = []
        for signal in recommended:
            node_id, modality = self._split_signal(str(signal))
            estimated_cost = self._patch_cost(node_id, modality, selected_nodes, modality_costs)
            repair_patch = repair_patch_index.get(str(signal), {})
            records.append(
                {
                    "patch_id": f"patch_{len(records) + 1}",
                    "candidate_id": str(signal),
                    "node_id": node_id,
                    "modality": modality,
                    "already_selected": str(signal) in selected_pairs,
                    "patch_type": self._patch_type(node_id, selected_nodes),
                    "estimated_cost_index": estimated_cost,
                    "supports_proxy_ids": proxy_support.get(str(signal), []),
                    "priority": self._patch_priority(modality),
                    "repair_priority_score": float(repair_patch.get("repair_priority_score", 0.0) or 0.0),
                    "weak_axis_repair_status": repair_plan.get("repair_status", "unknown"),
                    "repair_why_needed": repair_patch.get("why_needed", "proxy patch from Agent51"),
                    "evidence_stage": "synthetic_proxy_design_not_field_validated",
                    "field_validation_required": [
                        "node_specific_sensor_timeseries",
                        "offline_catalyst_activity_label",
                        "proxy_holdout_correlation_or_mae",
                    ],
                    "failure_boundary": (
                        "该补点只能作为 observation contract 设计先验；field proxy holdout 前不能解除 Agent49 catalyst block。"
                    ),
                }
            )
        records.sort(
            key=lambda item: (
                -float(item["repair_priority_score"]),
                -float(item["priority"]),
                float(item["estimated_cost_index"]),
                item["candidate_id"],
            )
        )
        return records

    def _contract_candidates(
        self,
        base_layout: dict[str, Any],
        patch_records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        base_candidate = self._candidate(
            candidate_id="base_agent48_layout",
            base_layout=base_layout,
            add_patches=[],
            remove_pairs=[],
            rationale="Agent48 当前稀疏布点，不引入 Agent51 catalyst proxy patch。",
        )
        full_candidate = self._candidate(
            candidate_id="full_proxy_patch_contract",
            base_layout=base_layout,
            add_patches=patch_records,
            remove_pairs=[],
            rationale="完整加入 Agent51 推荐的 catalyst_activity 代理补点，观测增强最大但可能超预算。",
        )
        budget_candidate = self._budget_rebalanced_candidate(base_layout, patch_records)
        candidates = [base_candidate, full_candidate, budget_candidate]
        for rank, candidate in enumerate(
            sorted(candidates, key=lambda item: (-float(item["contract_score"]), item["candidate_id"])),
            start=1,
        ):
            candidate["rank"] = rank
        return candidates

    def _candidate(
        self,
        *,
        candidate_id: str,
        base_layout: dict[str, Any],
        add_patches: list[dict[str, Any]],
        remove_pairs: list[str],
        rationale: str,
    ) -> dict[str, Any]:
        base_pairs = set(base_layout["selected_pairs"])
        add_pairs = {str(patch["candidate_id"]) for patch in add_patches}
        contract_pairs = sorted((base_pairs | add_pairs) - set(remove_pairs))
        added_cost = sum(float(patch["estimated_cost_index"]) for patch in add_patches)
        removed_cost = sum(self._pair_cost(pair) for pair in remove_pairs)
        cost_index = round(float(base_layout["base_total_cost_index"]) + added_cost - removed_cost, 3)
        budget_limit = float(base_layout["budget_limit"])
        patch_completion = len(add_patches) / max(1, len(self._proxy_metrics().get("recommended_sensor_patches", [])))
        proxy_metrics = self._proxy_metrics()
        current_catalyst = float(base_layout["current_catalyst_activity_observability"])
        full_proxy = float(proxy_metrics.get("proxy_observability_after_recommended_patch", current_catalyst))
        catalyst_after = round(current_catalyst + (full_proxy - current_catalyst) * patch_completion, 3)
        weak_after = round(
            min(catalyst_after, float(base_layout["current_matrix_interference_observability"])),
            3,
        )
        missingness_after = self._missingness_after_patch(
            base_layout=base_layout,
            weak_after=weak_after,
            add_patches=add_patches,
            remove_pairs=remove_pairs,
        )
        contract_score = round(
            0.30 * min(1.0, weak_after / 0.55)
            + 0.18 * min(1.0, missingness_after / 0.72)
            + 0.18 * float(cost_index <= budget_limit)
            + 0.14 * float(base_layout["layout_alignment_pass"])
            + 0.12 * patch_completion
            + 0.08 * float(bool(self._soft_sensor_schema_patch()["missing_layout_terms"])),
            3,
        )
        return {
            "candidate_id": candidate_id,
            "contract_id": f"{base_layout['layout_id']}::{candidate_id}",
            "rationale": rationale,
            "contract_pairs": contract_pairs,
            "added_patch_pairs": sorted(add_pairs),
            "removed_base_pairs": sorted(remove_pairs),
            "sensor_count": len(contract_pairs),
            "estimated_total_cost_index": cost_index,
            "budget_limit": budget_limit,
            "budget_margin": round(budget_limit - cost_index, 3),
            "budget_pass": cost_index <= budget_limit,
            "patch_completion_rate": round(patch_completion, 3),
            "proxy_enhanced_catalyst_activity_observability": catalyst_after,
            "proxy_enhanced_weak_state_coverage": weak_after,
            "estimated_missingness_robustness_after_patch": missingness_after,
            "weak_axis_repair_status": self._weak_axis_repair_plan().get("repair_status", "unknown"),
            "weak_axis_repair_score": self._weak_axis_repair_plan().get("repair_score", 0.0),
            "field_repair_evidence_requirement_count": len(
                self._weak_axis_repair_plan().get("field_repair_evidence_requirements", [])
            ),
            "layout_alignment_pass": base_layout["layout_alignment_pass"],
            "contract_score": contract_score,
            "evidence_stage": "synthetic_observation_design_prior",
            "cannot_do": [
                "cannot finalize field sensor placement without field topology",
                "cannot relax catalyst uncertainty block without field proxy labels",
                "cannot write release gate from observation contract",
            ],
        }

    def _budget_rebalanced_candidate(
        self,
        base_layout: dict[str, Any],
        patch_records: list[dict[str, Any]],
    ) -> dict[str, Any]:
        critical_patches = [patch for patch in patch_records if patch["modality"] in {"UV254_abs", "ORP_mV"}]
        base_cost = float(base_layout["base_total_cost_index"])
        budget_limit = float(base_layout["budget_limit"])
        added_cost = sum(float(patch["estimated_cost_index"]) for patch in critical_patches)
        remove_pairs: list[str] = []
        if base_cost + added_cost > budget_limit:
            remove_pairs = self._lowest_marginal_pairs_until_budget(
                required_reduction=base_cost + added_cost - budget_limit,
                protected_nodes={"N3_catalyst_bed_outlet", "N4_recirculation_loop", "N2_reactor_mid"},
            )
        return self._candidate(
            candidate_id="budget_rebalanced_proxy_contract",
            base_layout=base_layout,
            add_patches=critical_patches,
            remove_pairs=remove_pairs,
            rationale=(
                "优先加入床出口 UV254/ORP 两个高价值代理补点，并替换最低边际、非核心节点的原始传感点，"
                "使 catalyst_activity 过 0.55 的同时维持预算约束。"
            ),
        )

    def _recommended_contract(self, candidates: list[dict[str, Any]]) -> dict[str, Any]:
        feasible = [
            candidate
            for candidate in candidates
            if bool(candidate["budget_pass"])
            and float(candidate["proxy_enhanced_weak_state_coverage"]) >= 0.55
            and bool(candidate["layout_alignment_pass"])
        ]
        pool = feasible or candidates
        return dict(sorted(pool, key=lambda item: (-float(item["contract_score"]), item["candidate_id"]))[0])

    def _readiness(
        self,
        base_layout: dict[str, Any],
        patch_records: list[dict[str, Any]],
        recommended: dict[str, Any],
    ) -> dict[str, Any]:
        field_topology_ready = self._sparse_readiness().get("data_origin") == "field_topology"
        field_proxy_ready = bool(self._catalyst_readiness().get("field_validated", False))
        field_missingness_ready = bool(self._soft_readiness().get("field_ready", False))
        contract_ready = (
            bool(recommended.get("budget_pass"))
            and bool(recommended.get("layout_alignment_pass"))
            and float(recommended.get("proxy_enhanced_weak_state_coverage", 0.0)) >= 0.55
        )
        score = round(
            0.24 * min(1.0, float(recommended.get("proxy_enhanced_weak_state_coverage", 0.0)) / 0.55)
            + 0.18 * min(1.0, float(recommended.get("estimated_missingness_robustness_after_patch", 0.0)) / 0.72)
            + 0.16 * float(recommended.get("budget_pass", False))
            + 0.14 * float(base_layout["layout_alignment_pass"])
            + 0.10 * float(bool(self._soft_sensor_schema_patch()["missing_layout_terms"]))
            + 0.06 * float(bool(patch_records))
            + 0.04 * float(field_topology_ready)
            + 0.04 * float(field_proxy_ready)
            + 0.04 * float(field_missingness_ready),
            3,
        )
        if contract_ready and field_topology_ready and field_proxy_ready and field_missingness_ready:
            status = "field_observation_contract_candidate_ready"
        elif contract_ready:
            status = "synthetic_observation_contract_ready_needs_field_topology_proxy_labels_and_missingness"
        else:
            status = "observation_contract_needs_redesign"
        return {
            "observation_contract_status": status,
            "observation_contract_score": score,
            "base_layout_alignment_pass": base_layout["layout_alignment_pass"],
            "base_weak_state_coverage": base_layout["current_weak_state_coverage"],
            "recommended_contract_id": recommended["candidate_id"],
            "recommended_sensor_count": recommended["sensor_count"],
            "recommended_cost_index": recommended["estimated_total_cost_index"],
            "budget_pass": recommended["budget_pass"],
            "proxy_enhanced_weak_state_coverage": recommended["proxy_enhanced_weak_state_coverage"],
            "catalyst_observability_gain": round(
                float(recommended["proxy_enhanced_catalyst_activity_observability"])
                - float(base_layout["current_catalyst_activity_observability"]),
                3,
            ),
            "weak_axis_repair_status": recommended.get("weak_axis_repair_status", "unknown"),
            "weak_axis_repair_score": recommended.get("weak_axis_repair_score", 0.0),
            "field_repair_evidence_requirement_count": recommended.get("field_repair_evidence_requirement_count", 0),
            "missingness_robustness_after_patch": recommended["estimated_missingness_robustness_after_patch"],
            "schema_patch_term_count": len(self._soft_sensor_schema_patch()["missing_layout_terms"]),
            "field_topology_ready": field_topology_ready,
            "field_proxy_labels_ready": field_proxy_ready,
            "field_missingness_ready": field_missingness_ready,
            "agent48_hidden_state_ledger_status": base_layout["hidden_state_requirement_ledger_status"],
            "agent48_hidden_state_ready_count": base_layout["hidden_state_ready_count"],
            "agent48_hidden_state_count": base_layout["hidden_state_count"],
            "agent48_hidden_state_unresolved_count": base_layout["hidden_state_unresolved_count"],
            "agent48_hidden_state_minimum_patch_status": base_layout["hidden_state_minimum_patch_status"],
            "agent48_hidden_state_hard_unresolved": base_layout["hidden_state_hard_unresolved"],
            "agent48_pressure_headloss_candidate_pool_status": base_layout["pressure_headloss_candidate_pool_status"],
            "agent48_pressure_headloss_candidate_count": base_layout["pressure_headloss_candidate_count"],
            "agent48_pressure_headloss_candidate_ids": base_layout["pressure_headloss_candidate_ids"],
            "can_update_agent48_design_prior": contract_ready,
            "can_update_agent54_observation_contract": contract_ready,
            "can_relax_agent49_catalyst_uncertainty_block": field_proxy_ready,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        }

    @staticmethod
    def _writeback_policy(readiness: dict[str, Any]) -> dict[str, Any]:
        return {
            "allowed_writeback": [
                "agent48_design_prior_patch",
                "agent54_observation_contract_patch",
                "agent49_state_patch_candidate",
                "agent51_weak_axis_repair_plan",
                "architecture_consolidation_R2_status",
            ],
            "blocked_writeback": [
                "final_field_sensor_deployment",
                "agent49_catalyst_uncertainty_relaxation",
                "actuator_policy",
                "release_gate_policy",
            ],
            "can_update_agent48_design_prior": readiness["can_update_agent48_design_prior"],
            "can_update_agent54_observation_contract": readiness["can_update_agent54_observation_contract"],
            "can_write_to_release_gate": False,
            "policy_effect": "R2 observation contract can feed design priors, not field claims.",
        }

    @staticmethod
    def _next_refactor_action(readiness: dict[str, Any]) -> dict[str, Any]:
        if readiness["can_update_agent48_design_prior"] and readiness["can_update_agent54_observation_contract"]:
            return {
                "action_id": "R3_agent49_replay_counterfactual_stress",
                "title": "对 Agent49/52 做协同控制 replay 反事实压力测试",
                "reason": "观测契约已把 weak_state_coverage 推过 0.55 的设计门槛；下一步应检验控制策略在反事实 replay 下是否稳健。",
                "must_not_do": "不能训练黑箱 MARL 或写执行器；先做离线 replay、reward regret 和保护性误触发压力测试。",
            }
        return {
            "action_id": "R2b_observation_contract_redesign_under_budget",
            "title": "继续重设预算约束下的观测契约",
            "reason": "当前观测契约未同时满足预算、弱状态覆盖和 layout 对齐。",
            "must_not_do": "不能靠无限加点解决稀疏感知问题。",
        }

    def _soft_sensor_schema_patch(self) -> dict[str, Any]:
        training_gap = self.soft_sensor_matrix_metrics.get("training_schema_gap", {})
        training_gap = training_gap if isinstance(training_gap, dict) else {}
        missing_terms = [str(term) for term in training_gap.get("missing_layout_terms", [])]
        return {
            "required_before_layout_holdout": missing_terms,
            "missing_layout_terms": missing_terms,
            "patch_target": "SoftSensor training and inference feature schema",
            "field_boundary": "schema patch needs field node-specific values and missingness labels before performance claim",
        }

    def _field_validation_requirements(self) -> list[dict[str, Any]]:
        requirements = [
            {
                "requirement_id": "R2_FV1_field_topology_and_installability",
                "needed_for": "final field sensor placement",
                "required_tables": ["site_topology", "sensor_install_costs", "maintenance_access"],
            },
            {
                "requirement_id": "R2_FV2_proxy_holdout_labels",
                "needed_for": "relaxing catalyst uncertainty block",
                "required_tables": ["offline_catalyst_activity_labels", "pressure_drop_log", "regeneration_event_log"],
            },
            {
                "requirement_id": "R2_FV3_node_specific_missingness_replay",
                "needed_for": "soft sensor layout holdout performance",
                "required_tables": ["sensor_timeseries", "missingness_event_log", "layout_holdout_split"],
            },
        ]
        ledger = self._hidden_state_requirement_ledger()
        patch = ledger.get("minimum_cost_requirement_patch", {})
        patch = patch if isinstance(patch, dict) else {}
        if patch.get("hard_unresolved_hidden_states"):
            pressure_pool = self._hidden_state_requirement_ledger().get("pressure_headloss_candidate_pool", {})
            pressure_pool = pressure_pool if isinstance(pressure_pool, dict) else {}
            requirements.append(
                {
                    "requirement_id": "R2_FV4_agent48_hidden_state_requirement_patch",
                    "needed_for": "resolving Agent48 hard unresolved hidden-state sensing needs",
                    "required_tables": [
                        "node_modality_sensor_timeseries",
                        "offline_lab_results",
                        "campaign_operation_log",
                        "site_topology_or_bed_geometry",
                    ],
                    "hard_unresolved_hidden_states": [
                        str(item) for item in patch.get("hard_unresolved_hidden_states", [])
                    ],
                    "pressure_headloss_candidate_pool_status": pressure_pool.get(
                        "pool_status",
                        "missing_pressure_headloss_pool",
                    ),
                    "pressure_headloss_candidate_ids": [
                        str(item) for item in pressure_pool.get("candidate_ids", [])
                    ],
                    "minimum_matched_batch_count": (
                        pressure_pool.get("field_package_contract", {}).get("minimum_matched_batch_count", 3)
                        if isinstance(pressure_pool.get("field_package_contract", {}), dict)
                        else 3
                    ),
                    "required_signals_or_fields": [
                        "pressure_drop_kPa_or_headloss_proxy",
                        "catalyst_activity_label",
                        "regeneration_event",
                        "nominal_HRT_min",
                    ],
                }
            )
        return requirements

    def _selected_sensor_plan(self) -> list[dict[str, Any]]:
        selected = self.sparse_placement_metrics.get("selected_sensor_plan", [])
        return selected if isinstance(selected, list) else []

    def _sparse_coverage(self) -> dict[str, Any]:
        coverage = self.sparse_placement_metrics.get("coverage", {})
        return coverage if isinstance(coverage, dict) else {}

    def _sparse_readiness(self) -> dict[str, Any]:
        readiness = self.sparse_placement_metrics.get("readiness", {})
        return readiness if isinstance(readiness, dict) else {}

    def _hidden_state_requirement_ledger(self) -> dict[str, Any]:
        ledger = self.sparse_placement_metrics.get("hidden_state_requirement_ledger", {})
        return ledger if isinstance(ledger, dict) else {}

    def _proxy_metrics(self) -> dict[str, Any]:
        proxy_metrics = self.catalyst_proxy_metrics.get("proxy_metrics", {})
        return proxy_metrics if isinstance(proxy_metrics, dict) else {}

    def _weak_axis_repair_plan(self) -> dict[str, Any]:
        repair_plan = self.catalyst_proxy_metrics.get("weak_axis_repair_plan", {})
        return repair_plan if isinstance(repair_plan, dict) else {}

    @staticmethod
    def _repair_patch_index(repair_plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
        patches = repair_plan.get("prioritized_proxy_patches", [])
        patches = patches if isinstance(patches, list) else []
        return {
            str(patch.get("patch_signal")): dict(patch)
            for patch in patches
            if isinstance(patch, dict) and patch.get("patch_signal")
        }

    def _catalyst_readiness(self) -> dict[str, Any]:
        readiness = self.catalyst_proxy_metrics.get("readiness", {})
        return readiness if isinstance(readiness, dict) else {}

    def _soft_readiness(self) -> dict[str, Any]:
        readiness = self.soft_sensor_matrix_metrics.get("readiness", {})
        return readiness if isinstance(readiness, dict) else {}

    def _soft_feature_contract(self) -> dict[str, Any]:
        contract = self.soft_sensor_matrix_metrics.get("feature_contract", {})
        return contract if isinstance(contract, dict) else {}

    def _inferred_modality_costs(self) -> dict[str, float]:
        costs: dict[str, list[float]] = {}
        for row in self._selected_sensor_plan():
            modality = str(row.get("modality", "unknown"))
            costs.setdefault(modality, []).append(float(row.get("cost_index", DEFAULT_PATCH_MODALITY_COST.get(modality, 0.8))))
        inferred = {
            modality: round(sum(values) / max(1, len(values)), 3)
            for modality, values in costs.items()
        }
        return {**DEFAULT_PATCH_MODALITY_COST, **inferred}

    def _pair_cost(self, pair: str) -> float:
        for row in self._selected_sensor_plan():
            if str(row.get("candidate_id")) == pair:
                return float(row.get("cost_index", 0.0))
        _, modality = self._split_signal(pair)
        return DEFAULT_PATCH_MODALITY_COST.get(modality, 0.8)

    @staticmethod
    def _split_signal(signal: str) -> tuple[str, str]:
        if ":" in signal:
            node_id, modality = signal.split(":", 1)
            return node_id, modality
        return "operation_or_lab", signal

    @staticmethod
    def _patch_type(node_id: str, selected_nodes: set[str]) -> str:
        if node_id == "operation_or_lab":
            return "operation_or_lab_field"
        if node_id in selected_nodes:
            return "add_modality_to_existing_node"
        return "add_node_modality"

    @staticmethod
    def _patch_priority(modality: str) -> float:
        if modality == "UV254_abs":
            return 1.0
        if modality == "ORP_mV":
            return 0.88
        if modality == "pressure_drop_kPa":
            return 0.78
        return 0.55

    @staticmethod
    def _patch_cost(
        node_id: str,
        modality: str,
        selected_nodes: set[str],
        modality_costs: dict[str, float],
    ) -> float:
        base = modality_costs.get(modality, DEFAULT_PATCH_MODALITY_COST.get(modality, 0.8))
        install_penalty = 0.0 if node_id in selected_nodes or node_id == "operation_or_lab" else 0.20
        return round(base + install_penalty, 3)

    def _proxy_support_by_signal(self) -> dict[str, list[str]]:
        support: dict[str, list[str]] = {}
        catalog = self.catalyst_proxy_metrics.get("proxy_catalog", [])
        catalog = catalog if isinstance(catalog, list) else []
        for item in catalog:
            proxy_id = str(item.get("proxy_id", "unknown_proxy"))
            for signal in item.get("recommended_patch", []):
                support.setdefault(str(signal), [])
                if proxy_id not in support[str(signal)]:
                    support[str(signal)].append(proxy_id)
        return {signal: sorted(proxy_ids) for signal, proxy_ids in support.items()}

    def _lowest_marginal_pairs_until_budget(
        self,
        *,
        required_reduction: float,
        protected_nodes: set[str],
    ) -> list[str]:
        candidates = [
            row
            for row in self._selected_sensor_plan()
            if str(row.get("node_id")) not in protected_nodes
        ]
        candidates.sort(key=lambda row: (float(row.get("marginal_score", 1.0)), -float(row.get("cost_index", 0.0))))
        removed: list[str] = []
        reduction = 0.0
        for row in candidates:
            removed.append(str(row["candidate_id"]))
            reduction += float(row.get("cost_index", 0.0))
            if reduction >= required_reduction:
                break
        return removed

    @staticmethod
    def _missingness_after_patch(
        *,
        base_layout: dict[str, Any],
        weak_after: float,
        add_patches: list[dict[str, Any]],
        remove_pairs: list[str],
    ) -> float:
        current = float(base_layout["current_missingness_robustness_score"])
        weak_gain = max(0.0, weak_after - float(base_layout["current_weak_state_coverage"]))
        patch_bonus = min(0.035, 0.012 * len(add_patches))
        replacement_penalty = min(0.04, 0.015 * len(remove_pairs))
        return round(min(1.0, current + 0.12 * weak_gain + patch_bonus - replacement_penalty), 3)
