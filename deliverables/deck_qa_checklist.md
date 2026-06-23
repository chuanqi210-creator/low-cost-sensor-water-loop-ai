# PPTX QA 检查清单

- `cjk_font_compatibility`：PPTX 采用 Microsoft YaHei / PingFang SC / Aptos 字体策略，避免中文乱码。
- `recovery_boundary_integrity`：必须同时显示 0.75 条件恢复和 0.6 失败回退。
- `field_validation_disclosure`：必须说明当前数据来源为 synthetic/sample，不得表述为现场自治结论。
- `artifact_consistency`：当前 PPTX 是 Agent33 快照；若后续主动改 deck，再把口径更新为 40 agent、55/55 成果索引和 166 passed 回归基线。
- `render_layout_check`：导出前必须渲染预览并检查中文、线条、图表标签和页脚没有重叠。
