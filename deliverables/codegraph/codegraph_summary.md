# 项目 CodeGraph 知识图谱摘要

用途：减少后续 scan 摩擦。以后进入项目时，先读根目录 `CODEGRAPH.md`，再按本图谱定位文件、agent、实验、测试和产物。

## 生成信息

- 生成时间：`2026-06-22T09:36:58.883650+00:00`
- 来源：已安装 GitHub `lzehrung/codegraph` skill；由于当前机器没有 Node.js 24.10+ / `codegraph` CLI，本次使用项目本地 fallback 构建。
- 文件数：`409`
- 节点数：`5481`
- 边数：`8636`
- Agent workflow 数：`58`

## 层级计数

| 层级 | 节点数 |
| --- | ---: |
| `agent_logic` | 1530 |
| `agent_workflow` | 58 |
| `core_model` | 876 |
| `deliverable` | 293 |
| `experiment_runner` | 642 |
| `generated_artifact` | 303 |
| `governance_deliverable` | 400 |
| `project_memory` | 28 |
| `project_root` | 15 |
| `specification` | 60 |
| `unknown` | 146 |
| `verification` | 1130 |

## 高优先级扫描入口

| 优先级 | 文件 | 层级 | 入边 | 出边 | 说明 |
| ---: | --- | --- | ---: | ---: | --- |
| 1 | `deliverables/artifact_index.md` | `deliverable` | 4 | 164 | 成果索引 |
| 2 | `src/water_ai/domain.py` | `core_model` | 79 | 8 | from __future__ import annotations |
| 3 | `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py` | `experiment_runner` | 5 | 131 | from __future__ import annotations |
| 4 | `src/water_ai/agents/base.py` | `agent_logic` | 61 | 7 | from __future__ import annotations |
| 5 | `README.md` | `project_root` | 0 | 111 | 低成本传感循环式水处理智能闭环项目 |
| 6 | `src/water_ai/agents/data_quality_agent.py` | `agent_logic` | 31 | 17 | from __future__ import annotations |
| 7 | `src/water_ai/agents/control_strategy_agent.py` | `agent_logic` | 21 | 22 | from __future__ import annotations |
| 8 | `src/water_ai/agents/fault_diagnosis_agent.py` | `agent_logic` | 22 | 19 | from __future__ import annotations |
| 9 | `src/water_ai/agents/long_term_economics_agent.py` | `agent_logic` | 12 | 26 | from __future__ import annotations |
| 10 | `src/water_ai/agents/cost_safety_agent.py` | `agent_logic` | 14 | 21 | from __future__ import annotations |
| 11 | `src/water_ai/agents/phased_implementation_agent.py` | `agent_logic` | 10 | 26 | from __future__ import annotations |
| 12 | `experiments/run_agent41_matrix_shock_fast_proxy.py` | `experiment_runner` | 4 | 37 | from __future__ import annotations |
| 13 | `src/water_ai/agents/arbitration_agent.py` | `agent_logic` | 11 | 23 | from __future__ import annotations |
| 14 | `src/water_ai/agents/resource_expansion_agent.py` | `agent_logic` | 13 | 18 | from __future__ import annotations |
| 15 | `src/water_ai/simulation.py` | `core_model` | 19 | 6 | from __future__ import annotations |

## Agent 索引

| Agent | slug | runner | source | test | output |
| ---: | --- | --- | --- | --- | --- |
| 1 | `data_quality` | `experiments/run_agent1_data_quality.py` | `src/water_ai/agents/data_quality_agent.py` | `tests/test_data_quality_agent.py` | `outputs/agent1_data_quality` |
| 2 | `soft_sensor` | `experiments/run_agent2_soft_sensor.py` | `src/water_ai/agents/soft_sensor_agent.py` | `tests/test_soft_sensor_agent.py` | `outputs/agent2_soft_sensor` |
| 3 | `mechanism` | `experiments/run_agent3_mechanism.py` | `src/water_ai/agents/mechanism_agent.py` | `tests/test_mechanism_agent.py` | `outputs/agent3_mechanism` |
| 4 | `fault_diagnosis` | `experiments/run_agent4_fault_diagnosis.py` | `src/water_ai/agents/fault_diagnosis_agent.py` | `tests/test_fault_diagnosis_agent.py` | `outputs/agent4_fault_diagnosis` |
| 5 | `control_strategy` | `experiments/run_agent5_control_strategy.py` | `src/water_ai/agents/control_strategy_agent.py` | `tests/test_control_strategy_agent.py` | `outputs/agent5_control_strategy` |
| 6 | `cost_safety` | `experiments/run_agent6_cost_safety.py` | `src/water_ai/agents/cost_safety_agent.py` | `tests/test_cost_safety_agent.py` | `outputs/agent6_cost_safety` |
| 10 | `catalyst_lifecycle` | `experiments/run_agent10_catalyst_lifecycle.py` | `src/water_ai/agents/catalyst_lifecycle_agent.py` | `tests/test_catalyst_lifecycle_agent.py` | `outputs/agent10_catalyst_lifecycle` |
| 11 | `validation_planning` | `experiments/run_agent11_validation_planning.py` | `src/water_ai/agents/validation_planning_agent.py` | `tests/test_validation_planning_agent.py` | `outputs/agent11_validation_planning` |
| 12 | `operations_scheduling` | `experiments/run_agent12_operations_scheduling.py` | `src/water_ai/agents/operations_scheduling_agent.py` | `tests/test_operations_scheduling_agent.py` | `outputs/agent12_operations_scheduling` |
| 13 | `queue_planning` | `experiments/run_agent13_queue_planning.py` | `src/water_ai/agents/queue_planning_agent.py` | `tests/test_queue_planning_agent.py` | `outputs/agent13_queue_planning` |
| 14 | `resource_expansion` | `experiments/run_agent14_resource_expansion.py` | `src/water_ai/agents/resource_expansion_agent.py` | `tests/test_resource_expansion_agent.py` | `outputs/agent14_resource_expansion` |
| 15 | `long_term_economics` | `experiments/run_agent15_long_term_economics.py` | `src/water_ai/agents/long_term_economics_agent.py` | `tests/test_long_term_economics_agent.py` | `outputs/agent15_long_term_economics` |
| 16 | `phased_implementation` | `experiments/run_agent16_phased_implementation.py` | `src/water_ai/agents/phased_implementation_agent.py` | `tests/test_phased_implementation_agent.py` | `outputs/agent16_phased_implementation` |
| 17 | `implementation_stress_test` | `experiments/run_agent17_implementation_stress_test.py` | `src/water_ai/agents/implementation_stress_test_agent.py` | `tests/test_implementation_stress_test_agent.py` | `outputs/agent17_implementation_stress_test` |
| 18 | `adaptive_portfolio` | `experiments/run_agent18_adaptive_portfolio.py` | `src/water_ai/agents/adaptive_portfolio_agent.py` | `tests/test_adaptive_portfolio_agent.py` | `outputs/agent18_adaptive_portfolio` |
| 19 | `online_project_control` | `experiments/run_agent19_online_project_control.py` | `src/water_ai/agents/online_project_control_agent.py` | `tests/test_online_project_control_agent.py` | `outputs/agent19_online_project_control` |
| 20 | `campaign_telemetry` | `experiments/run_agent20_campaign_telemetry.py` | `src/water_ai/agents/campaign_telemetry_agent.py` | `tests/test_campaign_telemetry_agent.py` | `outputs/agent20_campaign_telemetry` |
| 21 | `replanning_orchestrator` | `experiments/run_agent21_replanning_orchestrator.py` | `src/water_ai/agents/replanning_orchestrator_agent.py` | `tests/test_replanning_orchestrator_agent.py` | `outputs/agent21_replanning_orchestrator` |
| 22 | `control_baseline_update` | `experiments/run_agent22_control_baseline_update.py` | `src/water_ai/agents/control_baseline_update_agent.py` | `tests/test_control_baseline_update_agent.py` | `outputs/agent22_control_baseline_update` |
| 23 | `post_replan_replay` | `experiments/run_agent23_post_replan_replay.py` | `src/water_ai/agents/post_replan_replay_agent.py` | `tests/test_post_replan_replay_agent.py` | `outputs/agent23_post_replan_replay` |
| 24 | `recovery_ramp` | `experiments/run_agent24_recovery_ramp.py` | `src/water_ai/agents/recovery_ramp_agent.py` | `tests/test_recovery_ramp_agent.py` | `outputs/agent24_recovery_ramp` |
| 25 | `time_budget_recovery` | `experiments/run_agent25_time_budget_recovery.py` | `src/water_ai/agents/time_budget_recovery_agent.py` | `tests/test_time_budget_recovery_agent.py` | `outputs/agent25_time_budget_recovery` |
| 26 | `recovery_strategy_writeback` | `experiments/run_agent26_recovery_strategy_writeback.py` | `src/water_ai/agents/recovery_strategy_writeback_agent.py` | `tests/test_recovery_strategy_writeback_agent.py` | `outputs/agent26_recovery_strategy_writeback` |
| 27 | `recovery_execution_replay` | `experiments/run_agent27_recovery_execution_replay.py` | `src/water_ai/agents/recovery_execution_replay_agent.py` | `tests/test_recovery_execution_replay_agent.py` | `outputs/agent27_recovery_execution_replay` |
| 28 | `recovery_online_control` | `experiments/run_agent28_recovery_online_control.py` | `src/water_ai/agents/recovery_online_control_agent.py` | `tests/test_recovery_online_control_agent.py` | `outputs/agent28_recovery_online_control` |
| 29 | `project_synthesis` | `experiments/run_agent29_project_synthesis.py` | `src/water_ai/agents/project_synthesis_agent.py` | `tests/test_project_synthesis_agent.py` | `outputs/agent29_project_synthesis` |
| 30 | `field_data_interface` | `experiments/run_agent30_field_data_interface.py` | `src/water_ai/agents/field_data_interface_agent.py` | `tests/test_field_data_interface_agent.py` | `outputs/agent30_field_data_interface` |
| 31 | `deliverable_organization` | `experiments/run_agent31_deliverable_organization.py` | `src/water_ai/agents/deliverable_organization_agent.py` | `tests/test_deliverable_organization_agent.py` | `outputs/agent31_deliverable_organization` |
| 32 | `presentation_assets` | `experiments/run_agent32_presentation_assets.py` | `` | `` | `outputs/agent32_presentation_assets` |
| 33 | `presentation_deck` | `experiments/run_agent33_presentation_deck.py` | `src/water_ai/agents/presentation_deck_agent.py` | `tests/test_presentation_deck_agent.py` | `outputs/agent33_presentation_deck` |
| 34 | `field_calibration_gate` | `experiments/run_agent34_field_calibration_gate.py` | `src/water_ai/agents/field_calibration_gate_agent.py` | `tests/test_field_calibration_gate_agent.py` | `outputs/agent34_field_calibration_gate` |
| 35 | `model_realism_audit` | `experiments/run_agent35_model_realism_audit.py` | `src/water_ai/agents/model_realism_audit_agent.py` | `tests/test_model_realism_audit_agent.py` | `outputs/agent35_model_realism_audit` |
| 36 | `soft_sensor_uncertainty_validation` | `experiments/run_agent36_soft_sensor_uncertainty_validation.py` | `src/water_ai/agents/soft_sensor_uncertainty_validation_agent.py` | `tests/test_soft_sensor_uncertainty_validation_agent.py` | `outputs/agent36_soft_sensor_uncertainty_validation` |
| 37 | `knowledge_graph_curation` | `experiments/run_agent37_knowledge_graph_curation.py` | `src/water_ai/agents/knowledge_graph_curation_agent.py` | `tests/test_knowledge_graph_curation_agent.py` | `outputs/agent37_knowledge_graph_curation` |
| 38 | `literature_evidence` | `experiments/run_agent38_literature_evidence.py` | `src/water_ai/agents/literature_evidence_agent.py` | `tests/test_literature_evidence_agent.py` | `outputs/agent38_literature_evidence` |
| 39 | `soft_sensor_conformal_calibration` | `experiments/run_agent39_soft_sensor_conformal_calibration.py` | `src/water_ai/agents/soft_sensor_conformal_calibration_agent.py` | `tests/test_soft_sensor_conformal_calibration_agent.py` | `outputs/agent39_soft_sensor_conformal_calibration` |
| 40 | `grey_box_dynamic_latency` | `experiments/run_agent40_grey_box_dynamic_latency.py` | `src/water_ai/agents/grey_box_dynamic_latency_agent.py` | `tests/test_grey_box_dynamic_latency_agent.py` | `outputs/agent40_grey_box_dynamic_latency` |
| 41 | `matrix_shock_fast_proxy` | `experiments/run_agent41_matrix_shock_fast_proxy.py` | `src/water_ai/agents/matrix_shock_fast_proxy_agent.py` | `tests/test_matrix_shock_fast_proxy_agent.py` | `outputs/agent41_matrix_shock_fast_proxy` |
| 42 | `timestamped_campaign_replay` | `experiments/run_agent42_timestamped_campaign_replay.py` | `src/water_ai/agents/timestamped_campaign_replay_agent.py` | `tests/test_timestamped_campaign_replay_agent.py` | `outputs/agent42_timestamped_campaign_replay` |
| 43 | `field_replay_calibration_gate` | `experiments/run_agent43_field_replay_calibration_gate.py` | `src/water_ai/agents/field_replay_calibration_gate_agent.py` | `tests/test_field_replay_calibration_gate_agent.py` | `outputs/agent43_field_replay_calibration_gate` |
| 44 | `field_replay_import` | `experiments/run_agent44_field_replay_import.py` | `src/water_ai/agents/field_replay_import_agent.py` | `tests/test_field_replay_import_agent.py` | `outputs/agent44_field_replay_import` |
| 45 | `field_replay_evidence_chain` | `experiments/run_agent45_field_replay_evidence_chain.py` | `src/water_ai/agents/field_replay_evidence_chain_agent.py` | `tests/test_field_replay_evidence_chain_agent.py` | `outputs/agent45_field_replay_evidence_chain` |
| 46 | `soft_sensor_field_holdout_gate` | `experiments/run_agent46_soft_sensor_field_holdout_gate.py` | `src/water_ai/agents/soft_sensor_field_holdout_gate_agent.py` | `tests/test_soft_sensor_field_holdout_gate_agent.py` | `outputs/agent46_soft_sensor_field_holdout_gate` |
| 47 | `weak_target_stratified_conformal` | `experiments/run_agent47_weak_target_stratified_conformal.py` | `src/water_ai/agents/weak_target_stratified_conformal_agent.py` | `tests/test_weak_target_stratified_conformal_agent.py` | `outputs/agent47_weak_target_stratified_conformal` |
| 48 | `sensor_network_sparse_placement` | `experiments/run_agent48_sensor_network_sparse_placement.py` | `src/water_ai/agents/sensor_network_sparse_placement_agent.py` | `tests/test_sensor_network_sparse_placement_agent.py` | `outputs/agent48_sensor_network_sparse_placement` |
| 49 | `multi_facility_collaborative_control` | `experiments/run_agent49_multi_facility_collaborative_control.py` | `src/water_ai/agents/multi_facility_collaborative_control_agent.py` | `tests/test_multi_facility_collaborative_control_agent.py` | `outputs/agent49_multi_facility_collaborative_control` |
| 50 | `model_core_governance` | `experiments/run_agent50_model_core_governance.py` | `` | `` | `outputs/agent50_model_core_governance` |
| 51 | `catalyst_activity_proxy` | `experiments/run_agent51_catalyst_activity_proxy.py` | `src/water_ai/agents/catalyst_activity_proxy_agent.py` | `tests/test_catalyst_activity_proxy_agent.py` | `outputs/agent51_catalyst_activity_proxy` |
| 52 | `multi_facility_replay_evaluation` | `experiments/run_agent52_multi_facility_replay_evaluation.py` | `src/water_ai/agents/multi_facility_replay_evaluation_agent.py` | `tests/test_multi_facility_replay_evaluation_agent.py` | `outputs/agent52_multi_facility_replay_evaluation` |
| 53 | `minimal_grey_box_physics` | `experiments/run_agent53_minimal_grey_box_physics.py` | `src/water_ai/agents/minimal_grey_box_physics_agent.py` | `tests/test_minimal_grey_box_physics_agent.py` | `outputs/agent53_minimal_grey_box_physics` |
| 54 | `soft_sensor_matrix_coupling` | `experiments/run_agent54_soft_sensor_matrix_coupling.py` | `src/water_ai/agents/soft_sensor_matrix_coupling_agent.py` | `tests/test_soft_sensor_matrix_coupling_agent.py` | `outputs/agent54_soft_sensor_matrix_coupling` |
| 55 | `engineering_execution_constraints` | `experiments/run_agent55_engineering_execution_constraints.py` | `` | `` | `outputs/agent55_engineering_execution_constraints` |
| 56 | `knowledge_graph_reasoning` | `experiments/run_agent56_knowledge_graph_reasoning.py` | `src/water_ai/agents/knowledge_graph_reasoning_agent.py` | `tests/test_knowledge_graph_reasoning_agent.py` | `outputs/agent56_knowledge_graph_reasoning` |
| 57 | `main_chain_reconnection` | `experiments/run_agent57_main_chain_reconnection.py` | `src/water_ai/agents/main_chain_reconnection_agent.py` | `tests/test_main_chain_reconnection_agent.py` | `outputs/agent57_main_chain_reconnection` |
| 58 | `field_validation_queue_alignment` | `experiments/run_agent58_field_validation_queue_alignment.py` | `src/water_ai/agents/field_validation_queue_alignment_agent.py` | `tests/test_field_validation_queue_alignment_agent.py` | `outputs/agent58_field_validation_queue_alignment` |
| 59 | `claim_specific_field_package` | `experiments/run_agent59_claim_specific_field_package.py` | `src/water_ai/agents/claim_specific_field_package_agent.py` | `tests/test_claim_specific_field_package_agent.py` | `outputs/agent59_claim_specific_field_package` |
| 60 | `agent_architecture_consolidation` | `experiments/run_agent60_agent_architecture_consolidation.py` | `src/water_ai/agents/agent_architecture_consolidation_agent.py` | `tests/test_agent_architecture_consolidation_agent.py` | `outputs/agent60_agent_architecture_consolidation` |
| 61 | `pressure_resolution_replay_scenario_pack` | `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py` | `src/water_ai/agents/pressure_resolution_replay_scenario_pack_agent.py` | `tests/test_pressure_resolution_replay_scenario_pack_agent.py` | `outputs/agent61_pressure_resolution_replay_scenario_pack` |

## 机器可读文件

- `deliverables/codegraph/project_codegraph.json`：完整节点、边、agent 索引、hotspot 和 scan shortcut。
- `deliverables/codegraph/project_codegraph_nodes.csv`：节点表。
- `deliverables/codegraph/project_codegraph_edges.csv`：边表。
- `deliverables/codegraph/scan_shortcuts.md`：给后续 agent 的最短阅读路径。
- `deliverables/codegraph/task_routes.json`：按工作流主题组织的跳转索引。
- `deliverables/codegraph/packets/`：核心 agent 的 packet 式上下文包。
- `deliverables/codegraph/native_vs_fallback_evaluation.md`：原生 CodeGraph 与本地 fallback 的效果对比。
