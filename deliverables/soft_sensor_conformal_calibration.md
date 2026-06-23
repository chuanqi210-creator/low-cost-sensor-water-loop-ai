# 软传感保形校准

- conformal_status：`synthetic_conformal_interface_ready_needs_field_holdout`
- conformal_score：`0.854`
- evidence_stage：`synthetic_holdout`
- alpha：`0.1`
- calibration_count：`32`
- evaluation_count：`16`
- target_coverage_level：`0.9`
- overall_conformal_coverage：`0.975`
- mean_conformal_interval_width：`0.233`
- release_abstention_rate：`0.125`
- can_write_to_release_gate：`False`

## Target Thresholds

- `pollutant_residual_risk`：threshold=0.0818, coverage=1.0, width=0.1636
- `reaction_completion`：threshold=0.1447, coverage=1.0, width=0.2894
- `oxidant_remaining`：threshold=0.0624, coverage=1.0, width=0.1248
- `catalyst_activity`：threshold=0.2075, coverage=1.0, width=0.415
- `matrix_interference`：threshold=0.086, coverage=0.875, width=0.172

## Scenario Full Coverage

- `catalyst_deactivation`：0.75
- `matrix_shock`：1.0

## 结论

- 保留当前 split conformal 层作为 synthetic 接口验证，不要写入现场放行门。
- 下一步用真实 field holdout 重新计算 nonconformity thresholds，并按污染物/基质分层评估 coverage。
- 只有 field 覆盖率、区间宽度和 abstention rate 同时通过后，才允许把 conformal interval 写入 release gate。