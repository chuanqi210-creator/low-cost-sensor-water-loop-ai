# 软传感不确定性验证

- uncertainty_validation_status：`synthetic_uncertainty_layer_ready_needs_field_holdout`
- uncertainty_validation_score：`0.9`
- evidence_stage：`synthetic_holdout`
- record_count：`48`
- overall_interval_coverage：`1.0`
- mean_abs_error：`0.0613`
- mean_interval_width：`0.0174`
- uncertainty_tracks_error：`True`
- ood_alert_count：`0`

## Target Coverage

- `pollutant_residual_risk`：1.0
- `reaction_completion`：1.0
- `oxidant_remaining`：1.0
- `catalyst_activity`：1.0
- `matrix_interference`：1.0

## 结论

- 保留当前不确定性层作为 synthetic 内部风险门，不要把它表述为现场校准完成。
- 下一步用真实离线标签构建 field holdout，并做 prediction interval coverage 与 release probability calibration。
- 若 field 覆盖率不足，优先使用 conformal calibration 或按污染物类别分层标定区间。