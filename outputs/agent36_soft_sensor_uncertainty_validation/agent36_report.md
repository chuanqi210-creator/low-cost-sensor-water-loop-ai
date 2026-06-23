# Agent 36 软传感不确定性验证报告

- summary: 软传感不确定性验证：synthetic_uncertainty_layer_ready_needs_field_holdout；区间覆盖率 1.000，OOD 警报 0 次。
- uncertainty_validation_status: `synthetic_uncertainty_layer_ready_needs_field_holdout`
- overall_interval_coverage: `1.0`

## 生成文件

- soft_sensor_uncertainty_validation: `deliverables/soft_sensor_uncertainty_validation.md`
- agent36_report: `outputs/agent36_soft_sensor_uncertainty_validation/agent36_report.md`
- uncertainty_metrics: `outputs/soft_sensor_training/soft_sensor_uncertainty_metrics.json`

## 风险边界

- `field_holdout_required_for_uncertainty`：当前不确定性验证只在 synthetic holdout 上成立，必须用真实 field holdout 校准后才能作为现场放行依据。