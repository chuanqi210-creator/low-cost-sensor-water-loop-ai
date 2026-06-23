# Field Replay Calibration Gate

- field_replay_gate_status：`synthetic_replay_gate_blocked`
- field_replay_gate_score：`0.875`
- accepted_gates：`7/8`
- can_write_to_protective_control：`False`
- can_write_to_release_gate：`False`
- writeback_mode：`blocked_until_field_replay_passes_g6`

## 方法契约

- upgrade_id：`field_replay_calibration_gate_for_fast_proxy_writeback`
- borrowed_from：`['timestamped_campaign_replay_for_fast_proxy_validation', 'model_validation_and_uncertainty_skill', 'academic_research_agent_evidence_before_claims', 'matrix_shock_fast_proxy_latency_aware_control']`
- 现实映射：把真实 timestamped replay 指标转化为 G6/P6 验收门，只有 field-labeled precision/recall、提前量和误触发成本达标时才允许写入保护性控制。
- 数据需求：field_origin_timestamped_replay, result_time_min, effect_time_min, field_label_matrix_shock, false_positive_cost_index, proxy_precision, proxy_recall
- 评价指标：G6_gate_pass_rate, proxy_precision, proxy_recall, protective_action_lead_time_min, false_positive_cost_index, writeback_mode
- 失败边界：G6/P6 通过只允许写入 matrix_shock 保护性控制；不能替代污染物达标、离线标签或 release conformal calibration。

## G6 验收门

| Gate | 通过 | 规则 | 证据 |
| --- | --- | --- | --- |
| `G6_1_field_origin` | `False` | data_origin 必须为 field，synthetic/sample 不得写入快代理控制。 | `{"data_origin": "synthetic"}` |
| `G6_2_timestamp_schema_ready` | `True` | 四张 replay 表必须时间戳完整，且 timestamp coverage 达标。 | `{"failed_tables": [], "timestamp_coverage": 1.0}` |
| `G6_3_batch_linkage_complete` | `True` | sensor、lab、operation 和 fast_proxy_event_log 必须能按 batch_id 回连。 | `{"orphan_reference_batches": [], "unlabeled_proxy_batches": []}` |
| `G6_4_proxy_label_volume` | `True` | 快代理验证必须有足够 field-labeled events。 | `{"proxy_label_count": 12, "minimum_proxy_events": 12}` |
| `G6_5_proxy_precision_recall` | `True` | 快代理 precision/recall 必须同时达标。 | `{"proxy_precision": 1.0, "proxy_recall": 1.0}` |
| `G6_6_latency_action_margin` | `True` | 保护性动作必须早于慢标签足够长时间，且执行器 P90 延迟不能过高。 | `{"mean_protective_action_lead_time_min": 84.0, "p90_actuator_latency_min": 10.0}` |
| `G6_7_false_positive_cost` | `True` | 误触发成本必须低于保护性控制可接受阈值。 | `{"mean_false_positive_cost_index": 0.0}` |
| `G6_8_release_boundary_preserved` | `True` | 快代理只能写入保护性控制，不能写入自动放行门。 | `{"matrix_fast_proxy_readiness": {"fast_proxy_status": "synthetic_fast_proxy_ready_needs_field_timestamp_validation", "fast_proxy_readiness_score": 0.56, "field_proxy_validation_required": true, "can_write_to_protective_control": false, "can_write_to_release_gate": false, "release_gate_block_reason": "fast proxy can trigger protection, but release still requires lab evidence and field conformal calibration"}}` |

## 写回边界

- target_agent：`MatrixShockFastProxyAgent`
- parameter_scope：`['field_proxy_precision', 'field_proxy_recall', 'protective_action_lead_time_min', 'false_positive_cost_index', 'protective_trigger_boundary']`
- can_write_to_protective_control：`False`
- can_write_to_release_gate：`False`
- release_policy：`block_release_until_lab_and_field_conformal_calibration`
- writeback_mode：`blocked_until_field_replay_passes_g6`
- blocked_by：`['G6_1_field_origin']`

## 结论

- 不要把当前 replay 写入保护性控制；先补齐失败的 G6 gate。
- 优先采集真实 field-labeled fast_proxy_event_log，并保留 result_time_min、effect_time_min、field_label_matrix_shock 和 false_positive_cost_index。
- synthetic replay 只能作为接口联调，不得作为现场 precision/recall 或保护性控制证据。