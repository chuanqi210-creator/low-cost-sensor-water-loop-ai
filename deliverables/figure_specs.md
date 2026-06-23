# 图表素材规格

## grey_box_loop 黑箱到灰箱逻辑图

- 类型：`mermaid`

```mermaid
flowchart LR
    A["进水/出水低成本可测"] --> B["中间过程黑箱"]
    B --> C["循环/暂存争取时间"]
    C --> D["软传感估计隐藏状态"]
    D --> E["多智能体解释与诊断"]
    E --> F["灰箱：可解释、可干预、可回退"]
```

## control_loop 循环式闭环控制图

- 类型：`mermaid`

```mermaid
flowchart LR
    S["低成本传感"] --> Q["数据质控"]
    Q --> H["软传感隐藏状态"]
    H --> M["机理解释/故障诊断"]
    M --> A["动作生成"]
    A --> C["成本安全仲裁"]
    C --> R{"是否可放行?"}
    R -- 否 --> L["回流/暂存/加药/再生/预处理"]
    L --> S
    R -- 是 --> O["达标放行"]
```

## agent_layer_map Agent 分层图

- 类型：`mermaid`

```mermaid
flowchart TB
    G1["1-2 感知与软传感"] --> G2["3-4 机理诊断"]
    G2 --> G3["5-10 控制与仲裁"]
    G3 --> G4["11-13 传感配置与批次调度"]
    G4 --> G5["14-18 资源/经济/实施"]
    G5 --> G6["19-23 在线重规划"]
    G6 --> G7["24-28 恢复控制"]
    G7 --> G8["29-30 项目总览与真实数据接口"]
    G8 --> G9[31-33 整理/汇报/正式 deck"]
```

## evidence_waterfall 瓶颈到重规划证据链

- 类型：`mermaid`

```mermaid
flowchart LR
    B1["多批次瓶颈<br/>验证/时间/催化剂"] --> B2["资源扩容对比"]
    B2 --> B3["长期经济性与分阶段实施"]
    B3 --> B4["压力测试与项目组合"]
    B4 --> B5["在线重规划"]
    B5 --> B6["基线写回"]
    B6 --> B7["回放验证通过"]
```

## recovery_boundary 恢复进水边界图

- 类型：`mermaid`

```mermaid
flowchart LR
    P["保护/恢复控制"] --> T["目标进水 0.75"]
    T --> C{"campaign 后复核"}
    C -- "稳定且无瓶颈" --> K["维持条件恢复"]
    C -- "时间/验证/库存触发" --> F["回退 0.6"]
    F --> R["重新运行重规划链"]
```

## field_data_schema 真实数据接口图

- 类型：`mermaid`

```mermaid
flowchart TB
    B["batch_id"] --> S["sensor_timeseries"]
    B --> L["offline_lab_results"]
    B --> C["catalyst_lifecycle"]
    B --> O["campaign_operation_log"]
    D["cost_deployment"] --> P["经济性/部署校准"]
    S --> M["软传感/质控校准"]
    L --> M
    C --> K["催化剂寿命校准"]
    O --> T["时间预算/回退门槛校准"]
```

## validation_boundary 边界说明卡片

- 类型：`callout`
- 当前可用于项目书、原型展示和实证前仿真基线。
- 当前 synthetic/sample 数据只能验证接口，不等于现场实证。
- 必须继续校准真实传感漂移、催化剂寿命、副产物风险和部署接口。

## calibration_roadmap P1-P6 实证校准路线

- 类型：`timeline`
- P1 传感器噪声与漂移
- P2 软传感器真实标签重训
- P3 催化剂寿命与副产物风险
- P4 时间预算与回退门槛
- P5 经济性与部署接口
- P6 时间戳回放与快代理校准
