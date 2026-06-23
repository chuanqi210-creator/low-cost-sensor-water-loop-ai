# Agent 链条复盘与承接顺序

本复盘不服务展示层，目标是找出前面 agent 在全局视角下的联动缺口，并按边际价值决定下一步模型核心修改。

| Rank | Gap | Affected Agents | Current Status | Next Carryover |
| --- | --- | --- | --- | --- |
| `1` | `G0_flat_knowledge_not_coupled_to_decisions` | `Agent3_Mechanism, Agent4_FaultDiagnosis, Agent5_ControlStrategy` | `patched_by_typed_kg_reasoning` | 把同一 KG patch 继续接入灰箱物理残差、稀疏布点和工程仲裁。 |
| `2` | `G1_parallel_core_agents_not_fully_reconnected` | `Agent48, Agent49, Agent53, Agent54, Agent55` | `partially_open` | 优先把 KG evidence path 作为共同接口，再逐步把 grey_box_prior、layout_mask 和 engineering_patch 接入主链。 |
| `3` | `G2_field_validation_queue_not_action_specific` | `Agent37, Agent43, Agent46, Agent50` | `patched_as_field_validation_queue` | 把 field_validation_queue 与 Agent30/42/44/45 的数据接口逐项对齐。 |
| `4` | `G3_claim_boundary_missing_for_source_poor_entries` | `Agent37, Agent38, Agent50` | `exposed_by_unsupported_claims` | 下一轮外部文献抽取优先补齐 source_basis、参数范围和适用边界。 |

## 根基判断

最高边际价值的问题是 `G0_flat_knowledge_not_coupled_to_decisions`：知识库若不能成为 typed evidence path，后续机理、故障、控制和工程仲裁就只能共享松散文本。Agent56 已把它改成可被 Agent3/4/5 消费的 KG reasoning patch。

下一步不应回到 PPT/Word，而应处理 `G1_parallel_core_agents_not_fully_reconnected`：把 Agent53 灰箱 prior、Agent54 layout/missingness 合同、Agent55 engineering patch 继续接回主闭环链条。