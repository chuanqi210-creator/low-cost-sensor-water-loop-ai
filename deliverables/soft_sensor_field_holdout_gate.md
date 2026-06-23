# 软传感 Field Holdout 放行门控

- gate_status：`soft_sensor_release_gate_blocked_non_field_holdout`
- gate_score：`0.714`
- uncertainty_evidence_stage：`synthetic_holdout`
- conformal_evidence_stage：`synthetic_holdout`
- can_write_to_release_gate：`False`
- can_auto_release_treated_water：`False`

## Calibration Snapshot

- uncertainty_record_count：`48`
- conformal_record_count：`48`
- evaluation_pair_count：`80`
- conformal_overall_coverage：`0.975`
- uncertainty_overall_interval_coverage：`1.0`
- release_abstention_rate：`0.125`
- conformal_ood_alert_rate：`0.0`

## Gate Checks

| Check | Pass | Rationale |
| --- | --- | --- |
| `SFG0_field_holdout_origin` | `False` | 软传感不确定性与 conformal 校准都必须来自真实 field holdout。 |
| `SFG1_record_volume` | `True` | field holdout 记录数和评估 target-pair 数必须足以支撑 release gate。 |
| `SFG2_interval_coverage` | `True` | 预测区间和 conformal 区间覆盖率必须同时达标。 |
| `SFG3_interval_width` | `True` | 区间不能靠无限放宽来获得覆盖率。 |
| `SFG4_abstention_and_ood` | `True` | abstention 和 OOD 不能过高，否则闭环控制会频繁进入人工/回退。 |
| `SFG5_weak_target_coverage` | `False` | 催化剂活性和基质抑制是弱观测目标，不能只看总体覆盖率。 |
| `SFG6_scenario_diversity` | `True` | field holdout 必须覆盖多个真实工况，且不能只在单一轻松场景中过线。 |

## Release Policy

- write_scope：`no_release_gate_write`
- requires_human_review_before_application：`True`
- requires_offline_lab_confirmation_for_compliance：`True`

## 结论

- 当前只能保留 synthetic holdout 作为接口验证，不要写入 release gate。
- 下一步采集真实 field holdout：传感时间序列、离线污染物标签、场景标签、软传感误差和 control outcome。
- 重新运行 Agent36、Agent39，再由本 agent 决定是否形成 release gate 校准候选。