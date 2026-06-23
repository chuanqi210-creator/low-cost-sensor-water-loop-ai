# 基质冲击快代理与延迟感知控制

- fast_proxy_status：`synthetic_fast_proxy_ready_needs_field_timestamp_validation`
- proxy_score：`0.559`
- specificity_guard_score：`0.633`
- protective_triggered：`True`
- protective_action_margin_min：`59.0`
- original_evidence_margin_min：`-31.0`
- projected_evidence_margin_after_extension_min：`14.0`
- can_write_to_release_gate：`False`

## 场景区分

| 场景 | proxy_score | specificity_guard | protective_triggered | release_block |
| --- | ---: | ---: | --- | --- |
| `matrix_shock` | 0.559 | 0.633 | True | True |
| `clean_release` | 0.008 | 0.009 | False | False |
| `oxidant_limitation` | 0.149 | 0.035 | False | False |

## 控制接入效果

- baseline_hold_min：`35`
- adapted_hold_min：`90`
- adapted_switch_protective_mode：`True`
- adapted_release_policy：`block_release_until_lab_and_field_conformal_calibration`
- adapted_final_plan：`['switch_or_pretreat', 'hold_for_validation', 'recirculate']`

## 结论

- 快代理解决的是保护性动作的提前触发，不解决自动放行。
- `matrix_shock` 在 synthetic replay 中可由 EC/浊度/UV254/pH/ORP 快代理提前进入预处理/切换和暂存验证。
- 真实写入前必须用 timestamped campaign replay 验证 precision、recall、提前量和误触发成本。