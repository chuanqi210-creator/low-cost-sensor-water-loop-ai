# Field Replay Evidence Chain

- field_replay_evidence_chain_status：`field_replay_evidence_chain_blocked_at_import`
- field_replay_evidence_chain_score：`0.0`
- import_ready：`False`
- timestamped_replay_ready：`False`
- g6_ready：`False`
- can_emit_protective_writeback_candidate：`False`
- can_write_to_release_gate：`False`

## 方法契约

- upgrade_id：`field_replay_import_to_g6_evidence_chain`
- borrowed_from：`['academic_research_agent_evidence_before_claims', 'model_validation_and_uncertainty_provenance_checks', 'timestamped_campaign_replay_for_fast_proxy_validation', 'field_replay_calibration_gate_for_fast_proxy_writeback']`
- 现实映射：把 Agent44 导入门、Agent42 时间戳回放和 Agent43 G6/P6 变成不可绕过的现场校准证据链，只有完整链条通过才形成保护性控制写回候选。
- 数据需求：agent44_import_ready_report, normalized_field_replay_datasets, field_label_matrix_shock, result_time_min, effect_time_min, false_positive_cost_index, matrix_fast_proxy_release_boundary
- 评价指标：field_replay_evidence_chain_score, import_ready, timestamped_replay_ready, g6_ready, can_emit_protective_writeback_candidate
- 失败边界：证据链通过也只形成保护性控制候选，不能自动写入现场 PLC/SCADA，不能替代 release gate、污染物达标或 field conformal calibration。

## 三段证据链

- Agent44 import_stage：`{'import_ready': False, 'import_status': 'field_replay_import_blocked_non_field_origin', 'data_origin': 'synthetic', 'accepted_table_count': 4, 'total_table_count': 4, 'can_pass_to_timestamped_replay': False, 'can_pass_to_g6': False, 'blocking_reasons': ['data_origin=synthetic', 'field_replay_import_blocked_non_field_origin']}`
- Agent42 timestamped_replay_stage：`{'stage_name': 'timestamped_campaign_replay', 'stage_status': 'not_run'}`
- Agent43 g6_stage：`{'stage_name': 'field_replay_calibration_gate', 'stage_status': 'not_run'}`

## 生成文件

- field_replay_evidence_chain: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/deliverables/field_replay_evidence_chain.md`
- agent45_report: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/outputs/agent45_field_replay_evidence_chain/agent45_report.md`
- evidence_chain_metrics: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/outputs/field_replay_evidence_chain/evidence_chain_metrics.json`

## 结论

- 先补真实 metadata.json 与四张 replay CSV，并通过 Agent44；不要单独运行 Agent42/Agent43 来绕过导入门。
- synthetic/sample 包只能作为接口联调，不能产生任何现场保护性写回候选。