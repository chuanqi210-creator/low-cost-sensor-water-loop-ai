# 可推理知识图谱与主链回接

- kg_reasoning_status：`kg_reasoning_patch_ready_needs_field_supported_edges`
- node_count：`88`
- edge_count：`305`
- evidence_traceability：`1.0`
- constraint_hit_rate：`1.0`
- field_supported_edge_ratio：`0.0`
- can_write_to_actuator：`False`
- can_write_to_release_gate：`False`

## 主链耦合状态

- mechanism_consumes_kg_reasoning：`True`
- fault_passes_kg_reasoning：`True`
- control_uses_typed_kg_constraints：`True`
- control_action_biases：`{'calibrate_sensors': 0.159, 'hold_for_validation': 0.22, 'recirculate': 0.067, 'release': -0.22}`
- top_control_action：`hold_for_validation`

## Action Constraint Patch

| Action | Direction | Bias | Evidence Paths | Boundary |
| --- | --- | --- | --- | --- |
| `calibrate_sensors` | `support` | `0.159` | `['kb_sensor_limited_release_evidence->likely_treated_but_not_releasable', 'kb_sensor_limited_release_evidence->sensor_uncertainty']` | `score_prior_only_until_field_validation` |
| `hold_for_validation` | `support` | `0.22` | `['kb_loop_buffer_for_slow_sensing->loop_buffer_needed', 'kb_sensor_limited_release_evidence->likely_treated_but_not_releasable', 'kb_sensor_limited_release_evidence->sensor_uncertainty']` | `score_prior_only_until_field_validation` |
| `recirculate` | `support` | `0.067` | `['kb_loop_buffer_for_slow_sensing->loop_buffer_needed']` | `score_prior_only_until_field_validation` |
| `release` | `suppress` | `-0.22` | `['kb_loop_buffer_for_slow_sensing->loop_buffer_needed', 'kb_sensor_limited_release_evidence->likely_treated_but_not_releasable', 'kb_sensor_limited_release_evidence->sensor_uncertainty']` | `score_prior_only_until_field_validation` |

## 结论边界

- `no_field_supported_kg_edges`：KG 已能约束机理和动作先验，但所有匹配边仍缺真实现场支持，不能写执行器或放行门。
- `source_or_field_claim_boundary_required`：部分知识边缺 source_basis 或 field evidence，需要在后续文献抽取/现场验证中补齐。
- `G1_parallel_core_agents_not_fully_reconnected`：Agent48/49/53/54/55 已有核心能力，但部分结果仍通过实验报告并联存在，没有全部进入主闭环 Agent1-9。