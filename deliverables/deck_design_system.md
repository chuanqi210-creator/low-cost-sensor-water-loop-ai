# 正式 PPT 设计系统

- 任务模式：`create`
- Deck profile：`engineering-platform`
- 画布：16:9 widescreen

## 字体策略

- 中文主字体：`Microsoft YaHei`
- Mac 备用：`PingFang SC`
- 西文/数字：`Aptos`
- 原因：避免中文在 Word/PPT 兼容环境中出现乱码或缺字。

## 调色板

- `ink`: `#1E293B`
- `paper`: `#F8FAFC`
- `blue`: `#2563EB`
- `green`: `#059669`
- `amber`: `#D97706`
- `red`: `#DC2626`
- `line`: `#CBD5E1`

## 版式规则

- 每页只有一个可复述主张，证据图形必须支撑该主张。
- 图形节点保持明确方向、分组和边界，不使用装饰性连接线。
- 所有边界页必须显式写出 synthetic/sample 不能代表现场实证。
- 恢复控制页必须同时出现 0.75 条件恢复和 0.60 回退线。