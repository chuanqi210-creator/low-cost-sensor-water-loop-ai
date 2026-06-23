# 知识图谱策展审计

- kg_curation_status：`scientific_kg_seed_needs_literature_and_field_evidence`
- kg_curation_score：`0.622`
- axis_coverage_score：`0.7`
- evidence_score：`0.8`
- raw_signal_grounding_score：`0.0`
- entry_count：`9`
- field_supported_entry_count：`0`

## 轴覆盖

| 轴 | 覆盖率 | 已覆盖 | 缺口 |
| --- | --- | --- | --- |
| `pollutant_axes` | `0.571` | PFAS, PPCPs/微污染物, 有机氯/卤代有机物, 重金属 | 染料, 抗生素, 农药 |
| `water_matrix_axes` | `0.833` | COD/有机负荷, 共存离子/络合物, 天然有机质, 浊度/颗粒物, 盐度/电导 | pH |
| `material_axes` | `0.857` | AOP/强氧化, 催化剂, 光催化, 吸附/离子交换, 生物处理耦合, 膜分离 | 电催化 |
| `process_axes` | `0.571` | 停留时间/回流, 光照/电流, 再生周期, 剂量/氧化剂 | pH 调节, 温度, 流量/水力 |
| `observable_signal_axes` | `0.571` | ORP, UV254, 浊度, 电导 | pH, 流量, 温度 |
| `hidden_state_axes` | `1.0` | 催化剂活性, 副产物风险, 反应完成度, 基质抑制, 残留污染物风险 | 无 |
| `evidence_axes` | `0.5` | 仿真支持, 文献支持 | 真实数据支持, 仅假设 |

## 证据等级

- `文献支持`：9
- `仿真支持`：9
- `真实数据支持`：0
- `仅假设`：0

## 模型改进 Backlog

- `P0` `field_supported_kg_edges`：为每条高风险知识边补真实 field 或离线标签验证；原因：当前知识图谱没有真实数据支持边，不能把文献/仿真边当现场结论。
- `P1` `literature_evidence_extraction_schema`：按系统综述格式抽取污染物、基质、材料、机制、参数范围和限制；原因：知识库应成为可追溯证据矩阵，而不是不可审计的经验条目。
- `P1` `raw_signal_to_hidden_state_edges`：补低成本原始信号到隐藏状态的证据边；原因：当前多数字段从隐藏状态触发知识条目，仍需要 pH/ORP/EC/UV254 等原始信号到机制的可审查映射。
- `P2` `pollutant_axis_expansion`：补齐污染物轴：染料, 抗生素, 农药；原因：真实污染场景需要覆盖 PPCPs、染料、抗生素、农药和有机氯等不同处理机制。
- `P2` `process_condition_axis_expansion`：补齐过程条件轴：pH 调节, 温度, 流量/水力；原因：动力学和控制不能只靠笼统回流，需要剂量、pH、温度、光照/电流、再生周期等可校准参数。
- `P2` `observable_signal_axis_expansion`：补齐低成本信号轴：pH, 流量, 温度；原因：软传感灰箱必须说明每个低成本信号怎样约束隐藏状态和控制动作。
- `P0` `claim_boundary_enforcement`：所有图谱结论强制标注 simulation/literature/field 边界；原因：防止 synthetic/sample 数据被误说成实证结论。

## 结论

- P0 为每条高风险知识边补真实 field 或离线标签验证
- P1 按系统综述格式抽取污染物、基质、材料、机制、参数范围和限制
- P1 补低成本原始信号到隐藏状态的证据边
- P2 补齐污染物轴：染料, 抗生素, 农药
- P2 补齐过程条件轴：pH 调节, 温度, 流量/水力