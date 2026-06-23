# 文献证据矩阵

- literature_evidence_status：`literature_seed_ready_field_validation_required`
- literature_evidence_score：`0.804`
- record_count：`8`
- kg_gap_closure_score：`0.889`
- field_supported_record_count：`0`

## KG 缺口覆盖

- covered_missing：`{'pollutant_axes': ['农药', '抗生素', '染料'], 'process_axes': ['pH 调节', '流量/水力'], 'observable_signal_axes': ['pH', '流量', '温度']}`
- remaining_missing：`{'pollutant_axes': [], 'process_axes': ['温度'], 'observable_signal_axes': []}`

## 文献记录

| citation_key | 年份 | 借鉴点 | 项目映射 | 数据需求 | 失败边界 |
| --- | --- | --- | --- | --- | --- |
| `pan_2026_ecomats` | `2026` | 把多智能体从简单分工升级为专家知识图谱、候选生成、理论筛选和盲审一致性融合的科学审查链。 | 本项目不直接宣称能自主发现催化剂，但可借鉴其 KG + 多 agent 审查结构，用于审查污染物-材料-机制-动作边。 | 候选材料属性, 目标污染物离线标签, pH 范围, 实际废水样本来源, 盲审评分记录 | 该文献支持多智能体材料发现范式，不证明本项目当前软传感或现场闭环控制已被 field 验证。 |
| `ching_2021_wwtp_soft_sensor_review` | `2021` | 软传感器不能只汇报 MAE/R2，还要记录硬件传感可靠性、噪声、场站差异和模型适用上下文。 | 对应 Agent36 的不确定性层，并要求 field holdout 按场景和传感故障分层评价。 | 传感器缺失/漂移日志, 场站或批次 ID, 离线水质标签, 传感器维护记录 | 综述支持软传感方向和挑战，不能替代本项目真实现场数据重训与校准。 |
| `parsa_2024_dynamic_control_review` | `2024` | 把闭环控制从动作枚举推进到动态模型、执行器、采样延迟和现场可测性的共同设计。 | 对应本项目循环结构、暂存验证、低频采样和 field calibration gate；下一步要把 PLC/人工复核/检测排队作为控制延迟参数。 | 进出水时间序列, 执行器动作日志, 采样和检测延迟, 流量/水力记录, 在线与离线标签对齐 | 该综述支持动态建模和控制约束，但本项目当前控制结果仍是 synthetic replay，不是现场运行证明。 |
| `angelopoulos_2021_conformal_prediction_intro` | `2021` | 用 calibration set 把软传感 prediction interval 从启发式区间升级为有覆盖率目标的保形区间。 | 对应 Agent36 的下一步：field holdout 上做 prediction interval coverage 和 release probability calibration。 | field_holdout_features, field_holdout_labels, nonconformity_score, 污染物/基质分层标签 | 保形预测依赖校准数据可交换性或适当分层；现场分布漂移严重时必须单独标记 OOD 和重新校准。 |
| `nsr_2026_scientific_kg_survey` | `2026` | 知识库应包含 typed nodes/edges、证据来源、可推理路径和 claim boundary，而不是只存自由文本解释。 | 对应 Agent37 的 KG schema 和 Agent38 的 evidence extraction schema。 | typed_edge, evidence_stage, citation_key, source_basis, field_validation_need | SciKG 范式支持结构化证据组织，不自动保证每条水处理机制边在本项目现场成立。 |
| `lupu_2023_antibiotics_aop_review` | `2023` | 补齐抗生素污染物轴时，要把处理机制、pH/光照/电流/氧化剂条件和副产物风险一起进入 KG。 | 对应 Agent37 缺失污染物轴中的抗生素，并补过程条件轴中的 pH 调节和光照/电流。 | antibiotic_compound, influent_effluent_concentration, AOP_type, pH, oxidant_dose, byproduct_label | 抗生素 AOP 文献不能泛化到所有 PPCPs；必须按具体化合物、基质和副产物标签校准。 |
| `water_2021_textile_dye_aop_review` | `2021` | 补染料轴时，把 UV254/色度、盐度、pH、能耗和矿化/副产物分开建模。 | 对应 Agent37 缺失污染物轴中的染料，并强化 UV254 原始信号到残留/副产物状态的证据边。 | dye_class, color_or_UV254, TOC_or_COD, energy_per_order, pH, salt_conductivity | 染料去色不等于矿化或无毒化，不能把 UV254/色度改善直接等同于安全放行。 |
| `sustainability_2025_pesticide_aop_review` | `2025` | 补农药轴时必须记录实际适用性、反应条件和潜在中间产物，而不是只记录去除率。 | 对应 Agent37 缺失污染物轴中的农药，并与副产物风险和 field validation need 绑定。 | pesticide_class, intermediate_products, toxicity_proxy, AOP_type, matrix_NOM, pH | 农药降解路径和中间体高度依赖化合物类别，不能用单一 AOP 仿真参数外推到所有农药废水。 |

## 模型升级映射

- `soft_sensor_field_conformal_calibration`：软传感器必须处理硬件噪声、场站差异和 field holdout 上的覆盖率，而不是只在 synthetic 上看 MAE。
  - borrowed_from：ching_2021_wwtp_soft_sensor_review, angelopoulos_2021_conformal_prediction_intro
  - data_needs：field_holdout_labels, sensor_fault_logs, batch_id, nonconformity_score
  - metrics：coverage_at_90pct, mean_interval_width, sensor_fault_stratified_error
  - failure_boundary：field holdout 未通过前，不确定性层只能作为 synthetic 风险门。
- `grey_box_dynamic_control_latency`：循环、暂存、低频采样和执行器动作需要被建成时序约束，而不是只作为控制动作名称。
  - borrowed_from：parsa_2024_dynamic_control_review
  - data_needs：actuator_log, sampling_delay_min, lab_turnaround_time, flow_hydraulic_trace
  - metrics：latency_budget_violation_rate, field_replay_success_rate, closed_loop_stability
  - failure_boundary：仿真闭环稳定不等于 PLC/人工复核/仪器排队条件下可执行。
- `scientific_kg_field_supported_edges`：把 KG 作为 typed evidence graph，并用多 agent 审查链约束 claim；文献边和 field 边必须分开。
  - borrowed_from：pan_2026_ecomats, nsr_2026_scientific_kg_survey
  - data_needs：citation_key, typed_edge, field_validation_need, claim_boundary, field_label
  - metrics：edge_traceability_rate, field_supported_edge_count, blind_review_consistency
  - failure_boundary：知识图谱结构化不等于知识边已被本项目现场验证。
- `pollutant_specific_process_axes`：补齐染料、抗生素、农药轴时，必须绑定 pH、氧化剂、光/电条件、能耗和副产物/中间体标签。
  - borrowed_from：lupu_2023_antibiotics_aop_review, water_2021_textile_dye_aop_review, sustainability_2025_pesticide_aop_review
  - data_needs：compound_class, AOP_type, pH, oxidant_dose, UV254_or_color, intermediate_products
  - metrics：compound_specific_removal, TOC_or_COD_reduction, byproduct_or_intermediate_risk
  - failure_boundary：污染物轴不能共用一个统一去除率假设；必须按化合物和基质分层。

## 结论

- P0 保持所有文献记录的 claim_boundary，禁止把 literature seed 写成 field 结论。
- P1 将 soft_sensor_field_conformal_calibration 作为下一步可实现模型升级。
- P1 将 grey_box_dynamic_control_latency 接入 process_dynamics 和 field runbook。
- P2 继续补 KG 未覆盖轴：{'process_axes': ['温度']}
- P2 将 literature evidence records 写回 KG typed edges 前，先做人工/规则双重审查。