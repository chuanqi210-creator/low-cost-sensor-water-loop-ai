# Scientific Knowledge Graph Schema

## 节点层

- `Pollutant`：污染物类型、代表化合物、检测限、目标标签。
- `WaterMatrix`：COD、盐度、pH、浊度、天然有机质、共存离子。
- `MaterialSystem`：催化剂、吸附剂、膜、AOP、光/电催化、生物耦合。
- `ProcessCondition`：停留时间、剂量、光照/电流、pH、温度、流量、再生周期。
- `ObservableSignal`：pH、ORP、电导、浊度、UV254、流量、温度。
- `HiddenState`：残留风险、反应完成度、副产物风险、催化剂活性、基质抑制。
- `ControlAction`：暂存验证、回流、加药、预处理/切换、再生、更换、放行。
- `Evidence`：文献支持、仿真支持、真实数据支持、仅假设。

## 关键边

- `Pollutant -affected_by-> WaterMatrix`
- `WaterMatrix -modulates-> Mechanism`
- `MaterialSystem -implements-> Mechanism`
- `ProcessCondition -controls-> HiddenState`
- `ObservableSignal -estimates-> HiddenState`
- `HiddenState -triggers-> ControlAction`
- `Evidence -supports_or_blocks-> TypedEdge`

## 科学审查链

| Agent | 职责 | 借鉴 workflow | 输出契约 |
| --- | --- | --- | --- |
| `LiteratureEvidenceAgent` | 系统检索和抽取水处理、环境材料、软传感、灰箱控制文献。 | `systematic_literature_review` | claim, method, parameter_range, limitation, evidence_stage, citation_key |
| `KnowledgeGraphCurationAgent` | 把文献和仿真证据转成污染物-基质-材料-过程-信号-状态-动作图谱。 | `scientific_knowledge_graph` | typed_edge, mechanism_tag, action_constraint, field_validation_need |
| `MechanismBorrowingAgent` | 从已有研究迁移动力学、传质、催化衰减、软传感和控制约束。 | `academic_research_agent` | borrowed_mechanism, mapped_project_state, assumption, failure_boundary |
| `UncertaintyValidationAgent` | 审查预测区间、校准曲线、bootstrap/conformal uncertainty 和 OOD 风险。 | `model_validation_and_uncertainty` | coverage, calibration_error, ood_flag, release_gate_adjustment |
| `FieldRealismAgent` | 检查现场采样频率、低成本传感漂移、PLC/SCADA 延迟、人工复核和成本边界。 | `claim_verification_and_human_gates` | field_gate, operator_action, latency_budget, cannot_claim_until |

## 强制边界

- `simulation` 和 `literature` 边可以影响候选动作排序，但不能作为 field parameter writeback。
- `field` 边必须经过 G0-G5 数据来源和质量门控后，才能进入软传感重训或控制参数校准。
- 所有可宣称结论必须带 `evidence_stage`、`source_basis`、`field_validation_need` 和 `claim_boundary`。