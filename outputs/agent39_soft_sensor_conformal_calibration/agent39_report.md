# Agent 39 软传感保形校准报告

- summary: 软传感保形校准：synthetic_conformal_interface_ready_needs_field_holdout；验证覆盖率 0.975，平均区间宽度 0.233。
- conformal_status: `synthetic_conformal_interface_ready_needs_field_holdout`
- overall_conformal_coverage: `0.975`
- can_write_to_release_gate: `False`

## 生成文件

- soft_sensor_conformal_calibration: `deliverables/soft_sensor_conformal_calibration.md`
- agent39_report: `outputs/agent39_soft_sensor_conformal_calibration/agent39_report.md`
- conformal_metrics: `outputs/soft_sensor_training/soft_sensor_conformal_metrics.json`

## 风险边界

- `field_holdout_required_for_conformal_calibration`：当前保形校准只在 synthetic split 上验证，不能写入现场 release gate。