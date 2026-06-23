# 专业技术导图证据映射与边界审计

生成时间：2026-06-04  
对应导图：[professional_technical_roadmap.md](professional_technical_roadmap.md)  
机器可读审计：`outputs/model_core_governance/professional_technical_roadmap_evidence_audit.json`

## 审计结论

专业技术导图当前可以作为“技术路线与方法成熟度说明”使用，但不能作为现场实证结论使用。

- 导图主张数：12
- 可追溯主张数：12
- 未支持主张数：0
- field 过度声明数：0
- field-supported claim 数：0
- no-write boundary：已保留
- 当前阶段：`external_field_package_or_new_core_interface_required`

## 证据映射表

| ID | 导图位置 | 主张 | 证据阶段 | 核心证据 | 当前边界 |
|---|---|---|---|---|---|
| TR01 | 图 1 | 低成本传感、循环结构、软传感灰箱估计、多智能体诊断控制与 field evidence gate 构成主系统链 | architecture contract | `outputs/model_core_governance/core_score_termination_gate.json`，`core_score=0.960` | 架构链路，不是现场运行证明 |
| TR02 | 图 2 | 6 个关键隐藏状态均已进入可追踪合同 | synthetic architecture contract | `state_variable_contract_coverage=1.000` | `field_validated_state_coverage=0.000` |
| TR03 | 图 3/4 | R2 已形成预算内 node-modality 观测合同 | synthetic observation design prior | `recommended_sensor_count=7`，`cost_index=5.272`，`budget_pass=true` | 不是最终现场布点 |
| TR04 | 图 4/8 | catalyst_activity 可由 UV254/ORP/pressure/headloss/再生事件形成代理验证链 | synthetic proxy design | `proxy_enhanced_weak_state_coverage=0.580`，`catalyst_observability_gain=0.280` | 不能证明真实催化剂衰减 |
| TR05 | 图 5 | 软传感已接入路径阶段特征与 layout holdout schema | synthetic training/schema readiness | manifest 中 `rf_multioutput_v5_path_layout_holdout`、23 特征、8 个路径特征 | 仍需 field path labels |
| TR06 | 图 5 | 灰箱物理先验覆盖最小机制层 | synthetic grey-box prior | `outputs/minimal_grey_box_physics/grey_box_physics_metrics.json` | 未经 field RTD、lab、byproduct 标签校准 |
| TR07 | 图 6 | R3 反事实压力测试可把危险动作转成 guardrail reward prior | synthetic counterfactual replay | `accuracy_gain_guardrail=0.333`，`field_replay_coverage=0.000` | 不代表现场控制有效 |
| TR08 | 图 7 | source_basis citation、参数边界和 failure boundary 已闭合 | literature traceability | `citation_detail_completion_rate=1.000`，`field_supported_edge_ratio=0.000` | 不能升级 field claim |
| TR09 | 图 7/下一步 | 当前进入真实 field package 或新核心接口阶段边界 | governance stage boundary | `recommended_next_core_action=WAIT_real_field_package_or_new_core_interface` | 不应继续堆旧 P 队列 |
| TR10 | 图 6/7 | actuator、release gate、field claim 写回均被阻断 | safety boundary | `can_write_to_actuator=false`，`can_write_to_release_gate=false` | 无真实 replay 和人工复核不得写回 |
| TR11 | 图 8/专利骨架 | 创新点应表达为组合链而非 AI 词汇本身 | patent disclosure scaffold | `model_maturity_patent_paper_audit.md`，`patent_technical_feature_ledger.json` | 不是授权判断或法律意见 |
| TR12 | 图 9 | PySensors、WNTR、WaterTAP、QSDsan、Pyomo 只是方法启发 | external method reference | `external_evidence_matrix.md` | 不声明已完整复现或验证现场性能 |

## 图级边界

### 图 1-2：系统主链与七层骨架

可说：

- 系统主链已经被明确为“低成本观测 -> 循环争取时间 -> 灰箱状态估计 -> 多智能体诊断控制 -> field gate”。
- 七层骨架已经形成，并且当前 Agent50 的 core_score 为 0.960。

不可说：

- 不能说该系统已经在真实现场闭环运行。
- 不能说 0.960 代表现场准确率或工程部署成熟度。

### 图 3-4：观测合同与稀疏传感

可说：

- R2 已经把 Agent48、Agent51、Agent54 的观测逻辑合并为预算内 7 点观测合同。
- weak_state_coverage 从 0.30 提升到 0.58，说明设计层面弱观测问题被缓解。

不可说：

- 不能说传感器布点已经可以直接施工。
- 不能说 catalyst_activity 已经真实可测或可用于解除控制保护。

### 图 5：软传感与灰箱化

可说：

- 软传感训练接口已经有路径阶段特征、缺测 mask、layout holdout 和灰箱 prior 入口。
- 黑箱已经在架构上被拆成可估计状态、灰箱 residual、证据边界和校准需求。

不可说：

- 不能说软传感模型已通过真实 field holdout。
- 不能说 release gate 可由当前软传感直接驱动。

### 图 6：控制 replay 与 guardrail

可说：

- R3 synthetic counterfactual stress 中，guardrail candidate 修正了高 regret/误保护场景。
- 这些结果可以进入 reward prior 和 stress suite。

不可说：

- 不能说 Agent49/52 已具备现场自动控制能力。
- 不能训练在线 MARL 或写 actuator。

### 图 7：证据门控与终止条件

可说：

- source_basis 和 schema 已形成，但 field package 未导入。
- 当前正确状态是停止内部扩张，等待真实 field package 或定义新核心接口。

不可说：

- 不能把 template 当 field evidence。
- 不能把 literature traceability 当现场支持。

### 图 8-9：创新点与外部工程借鉴

可说：

- 核心创新应是受限观测、循环时间缓冲、灰箱状态估计、多智能体保护性候选与 field gate 的组合技术链。
- PySensors、WNTR、WaterTAP、QSDsan、Pyomo 等提供可借鉴的工程方法族。

不可说：

- 不能把“AI、多智能体、KG、闭环控制”这些词本身作为创新点。
- 不能声明已经完成正式 prior art search、法律创造性判断或框架完整复现。

## 后续使用规则

1. 对外讲技术路线时，优先使用 `architecture_contract`、`synthetic_design_prior`、`literature_traceability`、`governance_stage_boundary` 这些证据阶段词。
2. 涉及现场效果时，必须改成“待 field package / field replay / field holdout / operator review 验证”。
3. 若后续新增真实 field package，应先刷新 R7、Agent44->42->43->45、Agent46/47、Agent50，再更新导图。
4. 若没有真实 field package，不要继续美化导图或堆旧 P 队列；只允许推进 formal search、人工审查、新核心接口定义或真实数据采集准备。
