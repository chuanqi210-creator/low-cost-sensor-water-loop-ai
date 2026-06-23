# 实证校准任务板

| 任务 | 状态 | 下一步 | 阻塞项 |
| --- | --- | --- | --- |
| `P1_sensor_noise_drift` 真实传感器噪声、漂移和污染结垢标定 | `template_ready` | 导入真实传感器原始时间序列与校准/清洗记录。 | [] |
| `P2_soft_sensor_retraining` 软传感器真实标签重训 | `template_ready` | 对齐离线检测标签与传感窗口，重训软传感器。 | [] |
| `P3_catalyst_lifecycle` 催化剂寿命、再生收益和副产物风险校准 | `template_ready` | 补充催化剂活性、压降、再生和寿命记录。 | [] |
| `P4_loop_time_budget` 循环、暂存、验证错峰和回退门槛校准 | `template_ready` | 导入真实动作开始/结束时间，校准错峰收益和回退阈值。 | [] |
| `P5_cost_deployment` 经济性和现场部署接口校准 | `template_ready` | 替换真实报价、人工成本、提前期和 PLC/SCADA 点表。 | [] |
| `P6_pressure_headloss_replay_contract` 压降/水头损失候选观测的现场 replay 校准 | `template_ready` | 补齐真实数据并重新运行接口检查。 | [] |
| `P6_timestamped_fast_proxy_replay` 时间戳回放与快代理校准 | `field_replay_required` | 导入真实 fast_proxy_event_log，对齐 result_time_min、effect_time_min、field_label_matrix_shock 和 false_positive_cost_index。 | ['field_labeled_timestamped_replay_missing'] |
| `P7_field_replay_import_package` 现场 replay 包导入与 provenance 验收 | `field_package_required` | 准备带 metadata.json 的真实 sensor/lab/operation/fast_proxy CSV 包，先通过 Agent44 再进入 Agent42/Agent43。 | ['field_metadata_and_csv_package_missing'] |
| `P8_field_replay_evidence_chain` 现场 replay 导入-回放-G6 证据链 | `evidence_chain_waiting_for_field_package` | 按 Agent44 -> Agent42 -> Agent43 -> Agent45 顺序重跑证据链，只在完整链条通过后形成保护性写回候选。 | ['agent44_field_package_not_passed'] |
| `P9_soft_sensor_field_holdout_gate` 软传感 field holdout 放行门控 | `field_holdout_required` | 采集真实 field holdout 标签，重跑 Agent36/Agent39/Agent46，只有全门控通过才形成软传感 release gate 校准候选。 | ['field_holdout_labels_missing'] |
| `P10_weak_target_stratified_conformal` 弱目标分层保形校准 | `field_holdout_required` | 补 matrix_interference 与 catalyst_activity 的真实场景标签，重跑 Agent47 后再交给 Agent46 审查。 | ['weak_target_field_labels_missing'] |
| `P11_sensor_network_sparse_placement` 管网布点与稀疏感知 | `field_topology_required` | 补真实管网/处理单元拓扑、水力停留时间、节点维护成本和节点级标签，重跑 Agent48 更新软传感观测矩阵。 | ['field_topology_and_node_labels_missing'] |
| `P12_multi_facility_collaborative_control` 多设施协同控制与策略蒸馏 | `field_coordination_replay_required` | 补真实多节点 sensor/lab/operation/action replay，重跑 Agent49 校准 joint_action_accuracy、reward_regret 和决策树蒸馏准确度。 | ['multi_node_state_action_replay_missing', 'distilled_policy_field_accuracy_missing'] |
| `P13_model_core_optimization_governance` 全局系统架构治理与模型核心优化 | `active_model_core_governance` | 以全局七层系统骨架和六类能力为准星运行架构治理；普通新想法先沉淀，只有阶段边界或硬风险时才做深度重排。 | [] |
| `P14_catalyst_activity_proxy` 催化剂活性弱观测代理 | `field_proxy_holdout_required` | 采集催化剂床前后 UV254/ORP、压降、再生事件和离线 catalyst_activity 标签，重跑 Agent51 形成 field_proxy_holdout，再由 Agent50 判断是否切回 P2 或推进 P3。 | ['field_catalyst_activity_labels_missing', 'pressure_drop_and_regeneration_events_missing'] |
| `P15_multi_facility_replay_evaluation` 多设施协同控制 replay 离线评估 | `field_multinode_replay_required` | 采集真实多节点 sensor/lab/operation/action/reward replay，重跑 Agent52 校准 joint_action_accuracy、reward_regret、误保护成本和决策树 replay accuracy。 | ['multi_node_state_action_reward_replay_missing', 'operator_or_validated_expert_action_labels_missing'] |
| `P16_minimal_grey_box_physics` 最小灰箱物理机制校准 | `field_physics_calibration_required` | 采集 RTD/池容/流量、进出水目标污染物、氧化剂投加与余量、催化剂再生历史和副产物面板，重跑 Agent53 校准 k_eff、质量残差和副产物风险。 | ['field_rtd_or_hydraulic_replay_missing', 'inlet_outlet_target_pollutant_labels_missing', 'byproduct_lab_panel_missing'] |
| `P17_soft_sensor_matrix_coupling` 软传感 node-modality/missingness 矩阵耦合 | `field_missingness_replay_required` | 采集 node-specific 传感值、layout_id holdout split、缺测原因和 field missingness replay，重跑 Agent54 后再训练 layout-aware soft sensor baseline。 | ['node_specific_sensor_values_missing', 'layout_holdout_split_missing', 'field_missingness_reason_labels_missing'] |