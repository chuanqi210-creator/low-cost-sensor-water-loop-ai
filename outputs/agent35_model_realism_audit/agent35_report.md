# Agent 35 模型真实性审计报告

- summary: 模型现实性审计：simulation_baseline_needs_field_grounding；知识库 9 条，field 门控 5/6 通过。
- realism_status: `simulation_baseline_needs_field_grounding`
- realism_score: `0.771`

## 生成文件

- model_realism_audit: `deliverables/model_realism_audit.md`
- model_upgrade_backlog: `deliverables/model_upgrade_backlog.md`
- agent35_report: `outputs/agent35_model_realism_audit/agent35_report.md`

## 优先建议

- P0 先通过真实数据 G0-G2，再允许任何参数写回
- P1 用 field holdout 和保形校准验证软传感不确定性
- P1 把知识库扩展为污染物-材料-机制-信号-动作-证据等级矩阵
- P2 引入污染物类别、催化剂、pH、基质和停留时间的参数化速率范围。
- P2 用真实离线标签做 prediction interval coverage、release probability calibration 和 conformal calibration。

## 风险边界

- `field_validation_missing`：当前模型只能作为仿真基线，真实参数写回必须等待 field 数据通过 G0-G5。
- `uncertainty_validation_missing`：软传感器仍缺少现场 holdout 校准；当前不确定性层不能替代 field validation。