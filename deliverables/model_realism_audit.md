# 模型真实性审计

- 当前状态：`simulation_baseline_needs_field_grounding`
- realism_score：`0.771`
- 最新回归：`213 passed`

## 1. 知识库审计

- 条目数：`9`
- 覆盖状态：`knowledge_base_seed_ready`
- 机制标签数：`25`
- 现场验证需求数：`12`
- 缺口轴：[]

## 2. 软传感和模型验证审计

- 模型版本：`rf_multioutput_v3_catalyst`
- 训练行数：`51840`
- field_rows：`0`
- synthetic_rows：`51840`
- validation_status：`synthetic_uncertainty_ready_field_holdout_missing`
- weaker_targets：['catalyst_activity', 'matrix_interference']
- has_uncertainty_layer：`True`

## 3. 现场校准门控

- field_status：`field_validation_blocked`
- data_origin：`synthetic`
- accepted_gates：`5/6`
- blocking_gates：['G0_data_origin']

## 4. 过程模型现实性缺口

### mechanistic_kinetics_parameterization

- 当前状态：过程动力学使用可解释启发式速率，尚未由真实反应动力学或现场参数校准。
- 现实化升级：引入污染物类别、催化剂、pH、基质和停留时间的参数化速率范围。
- 需要数据：['批内浓度时间序列', '剂量/停留时间记录', '目标物和副产物标签']

### uncertainty_and_extrapolation

- 当前状态：软传感器已有 synthetic 不确定性、预测区间和 OOD 风险门，但尚未用真实 field holdout 校准。
- 现实化升级：用真实离线标签做 prediction interval coverage、release probability calibration 和 conformal calibration。
- 需要数据：['field holdout set', '离线标签', '传感器漂移与缺失日志']

### target_specific_byproduct_speciation

- 当前状态：副产物风险是综合指标，尚未区分卤代副产物、过氧化残留或目标物中间体。
- 现实化升级：按污染物类别建立副产物风险子节点，并绑定必须检测的离线指标。
- 需要数据：['副产物检测', '余氧化剂', '目标物中间体']

### field_control_latency

- 当前状态：循环和延迟已建模，但 PLC/SCADA 接口、人工复核和检测排队时间仍偏简化。
- 现实化升级：把控制动作拆为可执行时序、人工/仪器资源和失败重试。
- 需要数据：['操作日志', '采样/检测排队', '人工覆盖记录']

### timestamped_fast_proxy_validation

- 当前状态：Agent42 已建立 sensor、lab、operation 和 fast_proxy_event_log 的时间戳回放接口，但样例数据仍为 synthetic。
- 现实化升级：用真实 field-labeled timestamped replay 校准 matrix_shock 快代理 precision、recall、提前量和误触发成本。
- 需要数据：['fast_proxy_event_log', 'field_label_matrix_shock', 'lab_label_time_min', 'actuator_effect_time_min', 'false_positive_cost_index']

### field_replay_calibration_gate

- 当前状态：Agent43 已将 Agent42 replay 指标转成 G6/P6 硬验收门；synthetic replay 被 `G6_1_field_origin` 阻断。
- 现实化升级：真实 replay 通过 G6/P6 后，只允许写入 matrix_shock 保护性控制，仍禁止写入自动放行门。
- 需要数据：['field_origin_timestamped_replay', 'proxy_precision', 'proxy_recall', 'protective_action_lead_time_min', 'false_positive_cost_index']

### field_replay_import

- 当前状态：Agent44 已建立现场 replay 包导入门；synthetic metadata 被 `field_replay_import_blocked_non_field_origin` 阻断。
- 现实化升级：真实包必须带 metadata.json、site/campaign/operator/instrument/custody provenance，并通过四张 CSV 的字段、数字/布尔类型转换和 batch 回连验收。
- 需要数据：['metadata.json', 'site_id', 'campaign_id', 'instrument_snapshot_id', 'chain_of_custody_id', 'sensor/lab/operation/fast_proxy CSV']

### field_replay_evidence_chain

- 当前状态：Agent45 已把 Agent44 导入门、Agent42 时间戳回放和 Agent43 G6/P6 串成不可绕过的证据链；synthetic 包被阻断在 import stage。
- 现实化升级：真实 replay 包通过完整链条后，只形成 matrix_shock 保护性写回候选，仍需人工复核与 release gate 独立校准。
- 需要数据：['agent44_import_ready_report', 'normalized_field_replay_datasets', 'timestamped_replay_metrics', 'g6_p6_gate_metrics', 'human_review_record']

### soft_sensor_field_holdout_release_gate

- 当前状态：Agent46 已把 Agent36 软传感不确定性验证和 Agent39 保形校准接成 release gate 硬门控；synthetic holdout 被 `SFG0_field_holdout_origin` 阻断，且弱目标门 `SFG5_weak_target_coverage` 也提示 matrix_interference/catalyst_activity 仍需 field 分层校准。
- 现实化升级：真实 field holdout 同时通过覆盖率、区间宽度、OOD/abstention、弱目标覆盖和场景多样性门控后，只形成软传感 release gate 校准候选。
- 需要数据：['field_holdout_sensor_timeseries', 'offline_lab_labels', 'target_abs_errors_by_hidden_state', 'prediction_interval_coverage_by_target', 'scenario_labels', 'ood_and_abstention_records']

### weak_target_stratified_conformal

- 当前状态：Agent47 已把 `catalyst_activity` 和 `matrix_interference` 从总体 conformal coverage 中拆出；当前最弱目标为 `matrix_interference`，synthetic coverage 为 0.875。
- 现实化升级：真实 field holdout 需要按 matrix_shock、catalyst_deactivation 和 clean_release 等场景计算 target/scenario coverage，并只把候选交给 Agent46 审查。
- 需要数据：['field_holdout_target_abs_errors', 'scenario_labels', 'per_target_prediction_intervals', 'offline_lab_or_maintenance_labels_for_weak_targets', 'ood_and_abstention_records']

## 5. 可借鉴 skill 工作流

- `systematic_literature_review`：从单篇论文阅读转为跨论文抽取研究问题、方法、发现、限制和可迁移参数。 项目用法：建立污染物-材料-机制-信号-动作的证据矩阵。
- `academic_research_agent`：evidence before claims、claim verification 和 human approval gates。 项目用法：所有 field 结论必须经过 G0-G5 门控，synthetic 只能标注为仿真基线。
- `scientific_knowledge_graph`：用结构化知识图谱组织异构科学证据，并用可追溯路径解释预测。 项目用法：把知识库从动作偏置升级为可审计机制证据层。
- `model_validation_and_uncertainty`：校准曲线、预测区间、bootstrap/ensemble uncertainty 和外推风险。 项目用法：升级 SoftSensorAgent 的 release gate 和 field holdout 评价。
