# Agent 42 Timestamped Campaign Replay 报告

- summary: 时间戳回放接口：synthetic_timestamp_schema_ready_needs_field_replay；时间戳覆盖 1.000，快代理标签事件 12。
- timestamped_replay_status: `synthetic_timestamp_schema_ready_needs_field_replay`
- timestamp_coverage: `1.0`
- proxy_precision: `1.0`
- proxy_recall: `1.0`
- pressure_headloss_event_count: `12`
- pressure_headloss_matched_batch_count: `12`
- can_calibrate_fast_proxy: `False`

## 生成文件

- timestamped_campaign_replay_schema: `deliverables/timestamped_campaign_replay_schema.md`
- agent42_report: `outputs/agent42_timestamped_campaign_replay/agent42_report.md`
- timestamped_replay_schema_json: `outputs/timestamped_campaign_replay/timestamped_replay_schema.json`
- timestamped_replay_templates: `outputs/timestamped_campaign_replay/templates`
- synthetic_timestamped_replay_package: `outputs/timestamped_campaign_replay/synthetic_timestamped_replay`

## 风险边界

- `field_timestamped_replay_required`：当前 timestamped replay 包只能验证接口，不能替代现场 replay。