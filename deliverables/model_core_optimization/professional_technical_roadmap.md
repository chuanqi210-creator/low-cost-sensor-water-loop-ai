# 专业技术导图：低成本传感循环式水处理智能灰箱闭环系统

生成时间：2026-06-04  
定位：面向专业人士的系统技术路线导图。它展示的是模型核心骨架、工程实现路径、创新点、证据边界和当前成熟度，不是展示材料美化稿。

## 读图摘要

本项目的核心不是“用 AI 做水处理”这个泛泛命题，而是一个受限观测条件下的工程闭环系统：

> 低成本传感导致水处理过程不可完全观测；循环/暂存结构为低频检测和软传感估计争取时间；稀疏布点与软传感把黑箱变成灰箱；知识图谱、灰箱机理和多智能体系统给出诊断与控制候选；field replay、holdout、operator review 和 release gate 决定哪些候选能被升级，哪些必须停留在 synthetic/literature/template 阶段。

当前状态是：架构合同、观测合同、source_basis、synthetic replay 和治理终止条件已经形成；真实现场数据包、field holdout、operator review、actuator feedback 和 release validation 仍未完成。

## 图 1：系统总技术路线

```mermaid
flowchart LR
    P0["真实污染场景<br/>污染物/废水基质/处理单元/管网拓扑/循环结构"] --> C0["核心工程矛盾<br/>低成本传感 + 低频采样 + 中间黑箱"]
    C0 --> T0["循环式结构争取时间<br/>回流/暂存/延长停留/分段验证"]
    T0 --> O0["稀疏观测层<br/>node-modality 矩阵<br/>pH/ORP/EC/UV254/浊度/流量/温度"]
    O0 --> S0["状态估计层<br/>软传感 + 灰箱先验<br/>隐藏状态 ledger"]
    S0 --> K0["机理证据层<br/>KG/source_basis/参数边界/失败边界"]
    K0 --> D0["诊断决策层<br/>多智能体解释/故障诊断/控制候选/策略蒸馏"]
    D0 --> A0["闭环执行候选<br/>回流/暂存/加药/切换单元/再生/阻断/放行候选"]
    A0 --> T0
    A0 --> V0["验证治理层<br/>synthetic replay/field package/holdout/operator review/release gate"]
    V0 -->|通过 field gate| F0["field-supported candidate<br/>可进入人工复核后的工程试验"]
    V0 -->|未通过| W0["等待态/外部阻断<br/>不写 actuator<br/>不写 release gate<br/>不升级 field claim"]

    classDef problem fill:#fff1f2,stroke:#be123c,color:#111827;
    classDef core fill:#ecfeff,stroke:#0891b2,color:#111827;
    classDef evidence fill:#fefce8,stroke:#ca8a04,color:#111827;
    classDef action fill:#ecfdf5,stroke:#059669,color:#111827;
    classDef gate fill:#f5f3ff,stroke:#7c3aed,color:#111827;
    class C0 problem;
    class T0,O0,S0 core;
    class K0 evidence;
    class D0,A0 action;
    class V0,F0,W0 gate;
```

## 图 2：七层系统骨架与当前产物

```mermaid
flowchart TB
    L1["1 现场对象层<br/>污染物/基质/处理单元/管网/循环/催化剂/膜/生物单元"]
    L2["2 观测层<br/>Agent48 稀疏布点<br/>R2 观测合同<br/>低成本 node-modality 矩阵"]
    L3["3 状态估计层<br/>Agent2 软传感<br/>Agent53 灰箱物理<br/>Agent54 缺测/路径特征<br/>隐藏状态 coverage ledger"]
    L4["4 机理证据层<br/>Agent37/56 KG<br/>Agent38 文献 evidence<br/>source_basis detail<br/>参数与失败边界"]
    L5["5 诊断决策层<br/>Agent3/4 机理诊断<br/>Agent49/52 多设施控制 replay<br/>R3 反事实压力测试"]
    L6["6 闭环执行层<br/>Agent5/6 控制与成本安全<br/>Agent55 工程约束<br/>回流/暂存/加药/切换/再生/放行候选"]
    L7["7 验证治理层<br/>Agent44/42/43/45 field replay<br/>Agent46/47 holdout/conformal<br/>Agent50 量化终止门<br/>R7 真实包验收"]

    L1 --> L2 --> L3 --> L4 --> L5 --> L6 --> L7
    L7 -->|校准反馈| L2
    L7 -->|证据升级或阻断| L4
    L7 -->|禁止未验证写回| L6

    classDef layer fill:#f8fafc,stroke:#334155,color:#0f172a;
    classDef ready fill:#dcfce7,stroke:#16a34a,color:#0f172a;
    classDef wait fill:#fffbeb,stroke:#d97706,color:#0f172a;
    class L1,L2,L3,L4,L5,L6,L7 layer;
```

## 图 3：核心工程实现路径

```mermaid
flowchart LR
    A48["Agent48<br/>稀疏传感布点<br/>多策略比较<br/>水力路径覆盖合同"] --> R2["R2 观测合同合并<br/>Agent48 + Agent51 + Agent54<br/>预算内 7 点合同"]
    A51["Agent51<br/>catalyst_activity 代理观测<br/>UV254/ORP/压降/再生事件需求"] --> R2
    A54["Agent54<br/>node-modality/missingness<br/>路径阶段特征<br/>layout holdout schema"] --> R2
    R2 --> SS["软传感训练/推理接口<br/>23 特征<br/>路径特征 8 项<br/>layout holdout"]
    R2 --> A49["Agent49<br/>多设施协同控制<br/>状态-动作-奖励候选<br/>工程约束 reward"]
    A49 --> A52["Agent52<br/>离线 replay 评估<br/>多策略 baseline comparison"]
    A52 --> R3["R3 反事实压力测试<br/>guardrail candidate<br/>reward prior patch"]
    R3 --> R3B["R3b/R3c<br/>guardrail 回写<br/>失败案例反写灰箱机制/field schema"]
    A56["Agent56 KG reasoning<br/>evidence traceability=1.0<br/>constraint hit rate=1.0"] --> A57["Agent57 主链回接<br/>prior consumption=1.0"]
    A57 --> A58["Agent58<br/>field validation queue 对齐<br/>table/gate coverage=1.0"]
    A58 --> A59["Agent59<br/>claim-specific field package<br/>source_basis completion=1.0"]
    A59 --> R1["R1 unified evidence gate<br/>citation detail=1.0<br/>field_supported_edge=0.0"]
    R1 --> R7["R7 real field package acceptance<br/>当前 blocked at import"]
    R7 --> A50["Agent50<br/>core_score=0.960<br/>stop expansion wait state"]
    R3B --> A50

    classDef sensor fill:#e0f2fe,stroke:#0284c7,color:#0f172a;
    classDef control fill:#dcfce7,stroke:#16a34a,color:#0f172a;
    classDef evidence fill:#fef9c3,stroke:#ca8a04,color:#0f172a;
    classDef gate fill:#ede9fe,stroke:#7c3aed,color:#0f172a;
    class A48,A51,A54,R2,SS sensor;
    class A49,A52,R3,R3B control;
    class A56,A57,A58,A59,R1 evidence;
    class R7,A50 gate;
```

## 图 4：观测层技术路径

```mermaid
flowchart TB
    N0["候选节点<br/>influent/equalization/reactor/catalyst bed/recirculation/polishing/effluent"] --> M0["候选模态<br/>pH ORP EC UV254 turbidity flow temp pressure/headloss"]
    M0 --> X0["node-modality 向量矩阵<br/>观测能力/控制时延收益/重构收益/成本/维护可达性"]
    X0 --> H0["隐藏状态需求 ledger<br/>pollutant_residual<br/>reaction_completion<br/>catalyst_activity<br/>matrix_interference<br/>hydraulic_delay<br/>release_or_byproduct_risk"]
    H0 --> B0["多策略布点比较<br/>greedy<br/>QR/D-optimal proxy<br/>classification proxy<br/>topology robust cost proxy"]
    B0 --> R20["R2 budget-rebalanced contract<br/>7 个 sensor pair<br/>cost index=5.272<br/>budget pass=true"]
    R20 --> U0["关键提升<br/>weak_state_coverage 0.30 -> 0.58<br/>catalyst observability gain=0.28<br/>missingness robustness=0.727"]
    U0 --> F0["field 需求<br/>site topology<br/>proxy holdout labels<br/>node-specific missingness replay<br/>pressure/headloss validation"]

    classDef input fill:#f8fafc,stroke:#334155,color:#0f172a;
    classDef alg fill:#e0f2fe,stroke:#0284c7,color:#0f172a;
    classDef out fill:#dcfce7,stroke:#16a34a,color:#0f172a;
    classDef need fill:#fffbeb,stroke:#d97706,color:#0f172a;
    class N0,M0,H0 input;
    class X0,B0,R20 alg;
    class U0 out;
    class F0 need;
```

## 图 5：状态估计与灰箱化路径

```mermaid
flowchart LR
    O1["低成本观测<br/>稀疏/缺测/延迟/噪声"] --> P1["预处理与质量门<br/>availability mask<br/>time_since_last_observed<br/>sensor status<br/>OOD/漂移标记"]
    P1 --> S1["软传感模型<br/>多输出残留/反应/风险估计<br/>路径阶段特征<br/>layout holdout"]
    G1["灰箱物理先验<br/>停留时间<br/>准一级反应<br/>基质抑制<br/>催化剂衰减<br/>副产物风险"] --> S1
    K1["KG/source_basis<br/>材料-污染物-工况<br/>参数边界<br/>failure boundary"] --> S1
    S1 --> Z1["灰箱状态向量<br/>可估计状态 + 不确定性 + 禁止外推边界"]
    Z1 --> D1["诊断与控制候选<br/>允许解释/排序<br/>禁止直接放行"]
    D1 --> V1["field holdout / conformal / replay<br/>通过后才可升级候选"]

    classDef obs fill:#e0f2fe,stroke:#0284c7,color:#0f172a;
    classDef mech fill:#fef9c3,stroke:#ca8a04,color:#0f172a;
    classDef state fill:#dcfce7,stroke:#16a34a,color:#0f172a;
    classDef gate fill:#ede9fe,stroke:#7c3aed,color:#0f172a;
    class O1,P1,S1 obs;
    class G1,K1 mech;
    class Z1,D1 state;
    class V1 gate;
```

## 图 6：闭环控制与 replay 验证路径

```mermaid
flowchart TB
    SV["facility state vector<br/>软传感状态/灰箱 residual/KG constraint/工程约束"] --> ACT["动作候选集合<br/>回流/暂存/延长停留/投药/切换单元/再生/放行候选"]
    ACT --> RWD["reward contract<br/>处理效果<br/>风险<br/>成本/能耗<br/>误保护成本<br/>执行可行性"]
    RWD --> POL["Agent49 policy candidate<br/>多设施协同动作排序<br/>决策树蒸馏"]
    POL --> REP["Agent52 offline replay<br/>policy vs expert/reward_by_action"]
    REP --> STR["R3 counterfactual stress<br/>catalyst_uncertain_low_proxy<br/>hydraulic_delay_violation"]
    STR --> GR["guardrail reward prior<br/>R3G1 catalyst uncertain -> standby/review<br/>R3G2 hydraulic delay unknown -> block recycle escalation"]
    GR --> POL
    STR --> GATE["field replay gate<br/>field_state_action_reward<br/>operator action<br/>tank margin/latency<br/>proxy label/pressure/regeneration"]
    GATE -->|未通过| NW["no-write boundary<br/>不写 actuator<br/>不写 release gate"]
    GATE -->|通过+人工复核| CAND["protective control candidate<br/>仅候选晋级"]

    classDef control fill:#dcfce7,stroke:#16a34a,color:#0f172a;
    classDef replay fill:#e0f2fe,stroke:#0284c7,color:#0f172a;
    classDef gate fill:#ede9fe,stroke:#7c3aed,color:#0f172a;
    class SV,ACT,RWD,POL,GR control;
    class REP,STR replay;
    class GATE,NW,CAND gate;
```

## 图 7：证据分层与终止条件

```mermaid
flowchart LR
    SYN["synthetic<br/>接口联调/仿真基线/反事实压力测试"] --> LIT["literature/source_basis<br/>citation/参数边界/适用条件"]
    LIT --> TEMP["template/schema<br/>field package 模板<br/>claim-specific required fields"]
    TEMP --> FIELD["field package<br/>data_origin=field<br/>sensor/lab/operation/proxy/catalyst rows"]
    FIELD --> REPLAY["timestamped replay<br/>Agent44 -> 42 -> 43 -> 45"]
    REPLAY --> HOLD["field holdout/conformal<br/>软传感校准<br/>弱目标分层 coverage"]
    HOLD --> HUMAN["operator/human review<br/>冲突解释<br/>控制候选复核"]
    HUMAN --> WRITE["候选写回<br/>protective candidate<br/>release calibration candidate"]

    SYN -.禁止.-> WRITE
    LIT -.禁止.-> WRITE
    TEMP -.禁止.-> WRITE

    WAIT["当前 Agent50 终止条件<br/>source_basis/schema/R2/R3 已形成<br/>field_import_ready=false<br/>continue_expansion_allowed=false"] --> FIELD

    classDef ok fill:#dcfce7,stroke:#16a34a,color:#0f172a;
    classDef mid fill:#fef9c3,stroke:#ca8a04,color:#0f172a;
    classDef wait fill:#fff1f2,stroke:#be123c,color:#0f172a;
    class SYN,LIT,TEMP mid;
    class FIELD,REPLAY,HOLD,HUMAN,WRITE ok;
    class WAIT wait;
```

## 图 8：创新点与工程技术效果映射

```mermaid
flowchart TB
    ROOT["核心创新主张<br/>低成本受限观测下的循环式水处理智能灰箱闭环系统"]

    I1["I1 循环争取时间<br/>把慢检测/低频传感限制转成可控的暂存-回流-再估计窗口"]
    I2["I2 稀疏观测合同<br/>node-modality + 隐藏状态 ledger + 成本约束布点"]
    I3["I3 黑箱转灰箱<br/>软传感 + 灰箱物理 prior + 路径阶段特征"]
    I4["I4 catalyst_activity 弱状态修复<br/>UV254/ORP/pressure/headloss/再生事件代理链"]
    I5["I5 多智能体科学审查链<br/>KG/source_basis/诊断/控制/验证各司其职并互相制约"]
    I6["I6 offline replay guardrail<br/>反事实压力测试把危险动作转成 reward prior 与保护规则"]
    I7["I7 证据门控治理<br/>synthetic/literature/template/field 严格分层<br/>no-write boundary"]
    I8["I8 可计算终止条件<br/>core_score + external blocker + wait/new-interface gate"]

    ROOT --> I1 --> E1["技术效果<br/>传感/反应速度要求下降<br/>成本降低但不冒进放行"]
    ROOT --> I2 --> E2["技术效果<br/>用少量传感点覆盖关键隐藏状态<br/>R2 weak coverage 0.30 -> 0.58"]
    ROOT --> I3 --> E3["技术效果<br/>从进出水黑箱变成过程灰箱<br/>状态估计可解释、可校准"]
    ROOT --> I4 --> E4["技术效果<br/>催化剂衰减/堵塞从不可观测变成可设计验证"]
    ROOT --> I5 --> E5["技术效果<br/>控制建议可追溯到证据路径和失败边界"]
    ROOT --> I6 --> E6["技术效果<br/>synthetic stress 下 guardrail accuracy gain=0.333<br/>误保护成本下降"]
    ROOT --> I7 --> E7["技术效果<br/>防止 synthetic claim 外溢<br/>保护专利/论文叙事可信度"]
    ROOT --> I8 --> E8["技术效果<br/>避免无限迭代<br/>当前进入真实 field 包或新接口阶段边界"]

    classDef root fill:#111827,stroke:#111827,color:#ffffff;
    classDef innovation fill:#e0f2fe,stroke:#0284c7,color:#0f172a;
    classDef effect fill:#dcfce7,stroke:#16a34a,color:#0f172a;
    class ROOT root;
    class I1,I2,I3,I4,I5,I6,I7,I8 innovation;
    class E1,E2,E3,E4,E5,E6,E7,E8 effect;
```

## 图 9：工程借鉴路径与本项目映射

```mermaid
flowchart LR
    PS["PySensors/SSPOR/SSPOC<br/>稀疏传感布点<br/>重构/分类/约束选择"] --> MPS["本项目映射<br/>Agent48 多策略布点<br/>R2 node-modality 合同"]
    WN["WNTR/EPANET 风格<br/>管网拓扑/水力路径/场景扰动"] --> MWN["本项目映射<br/>水力路径覆盖<br/>循环/暂存/回流阶段 prior"]
    WT["WaterTAP / QSDsan<br/>处理流程建模<br/>成本/能耗/TEA/LCA"] --> MWT["本项目映射<br/>灰箱单元约束<br/>Agent55 reward/工程可行性"]
    PY["Pyomo/优化建模<br/>变量/目标/约束/Pareto"] --> MPY["本项目映射<br/>布点优化<br/>动作候选约束<br/>成本-风险权衡"]
    SS["Soft sensor + conformal<br/>难测变量估计<br/>不确定性/覆盖率/校准"] --> MSS["本项目映射<br/>软传感 field holdout<br/>release gate 前置校准"]
    OPE["Offline replay / MPC / guardrail<br/>离线策略评估<br/>保护性控制"] --> MOPE["本项目映射<br/>Agent52/R3 replay stress<br/>R3G1/R3G2 guardrail"]
    KG["Scientific KG / evidence-first workflow<br/>source_basis/claim verification"] --> MKG["本项目映射<br/>Agent56/58/59/R1<br/>证据分层与 claim gate"]

    classDef source fill:#f8fafc,stroke:#475569,color:#0f172a;
    classDef map fill:#ecfeff,stroke:#0891b2,color:#0f172a;
    class PS,WN,WT,PY,SS,OPE,KG source;
    class MPS,MWN,MWT,MPY,MSS,MOPE,MKG map;
```

## 当前关键指标快照

| 维度 | 当前值 | 含义 | 边界 |
|---|---:|---|---|
| Agent50 core_score | 0.960 | 架构/接口/证据治理成熟度高 | 不是 field validation 分数 |
| hidden state contract coverage | 1.000 | 6 个关键隐藏状态均进入可追踪合同 | field_validated_state_coverage 仍为 0 |
| sparse_estimation_ready_coverage | 0.667 | 4/6 状态具备 sparse estimation ready | catalyst/matrix 仍需 field label 或补丁验证 |
| R2 proxy_enhanced_weak_state_coverage | 0.580 | catalyst_activity 设计覆盖从 0.30 提升到 0.58 | 仍需 proxy holdout labels |
| R2 recommended sensor count | 7 | 预算内观测合同 | 不是最终现场布点 |
| R2 cost index | 5.272 | budget pass=true | 仍需 installability/topology 校验 |
| R3 guardrail accuracy gain | 0.333 | synthetic counterfactual stress 下 guardrail 提升 | 不代表现场控制有效 |
| source_basis completion | 1.000 | 文献依据、参数边界、failure boundary 已闭合 | field_supported_edge_ratio=0 |
| field_import_ready | false | 真实包未导入 | 当前进入等待态 |
| continue_expansion_allowed | false | 内部继续堆 P1-P11 低边际 | 下一步需真实 field 包或新核心接口 |

## 专利/论文层面的创新表达骨架

```mermaid
flowchart LR
    Q["技术问题<br/>低成本受限观测下，水处理过程黑箱且直接传感昂贵/延迟高"] --> S["技术方案<br/>循环时间缓冲 + 稀疏传感 + 软传感灰箱估计 + 多智能体诊断控制 + field evidence gate"]
    S --> C1["可保护特征 1<br/>循环结构与低频证据窗口耦合"]
    S --> C2["可保护特征 2<br/>node-modality 隐藏状态覆盖合同"]
    S --> C3["可保护特征 3<br/>catalyst_activity 代理观测与保护性控制边界"]
    S --> C4["可保护特征 4<br/>offline replay guardrail 与 no-write field gate"]
    S --> C5["可保护特征 5<br/>可计算终止条件与 external blocker routing"]
    C1 --> R["技术效果<br/>降低传感与响应速度要求<br/>提升低成本可控性"]
    C2 --> R
    C3 --> R
    C4 --> R
    C5 --> R
    R --> B["当前证据边界<br/>可写专利交底/方法论文框架<br/>不能写现场实证论文结论<br/>不能声称已达工程部署"]
```

## 下一步专业路线判断

```mermaid
flowchart TB
    NOW["当前阶段<br/>架构合同完成<br/>source_basis 完成<br/>R2/R3 synthetic 链条形成<br/>Agent50 stop expansion"]
    NOW --> D1{"是否有 data_origin=field 的真实包？"}
    D1 -->|有| F1["运行 R7 / Agent44->42->43->45<br/>field import + timestamped replay + evidence chain"]
    F1 --> F2["运行 Agent46/47<br/>field holdout + weak target conformal"]
    F2 --> F3["operator review<br/>pressure/headloss conflict resolution<br/>release/actuator candidate gate"]
    D1 -->|没有| D2{"是否定义了新的核心接口或真实工程约束？"}
    D2 -->|有| I1["开启新一轮内部迭代<br/>必须说明输入/输出/指标/失败边界/下游消费者"]
    D2 -->|没有| W1["保持等待态<br/>不继续堆 agent<br/>不加工展示材料<br/>不升级 field claim"]
```

## 方法来源与借鉴说明

本导图中的外部工程路径只作为方法启发和接口设计依据，不等同于本项目已经安装或完整复现这些框架。

- PySensors：借鉴 sparse sensor placement、重构/分类任务、约束传感选择思想，用于 Agent48/R2 的 node-modality 布点合同。项目源：[dynamicslab/pysensors](https://github.com/dynamicslab/pysensors)。
- WNTR/EPANET 风格：借鉴管网拓扑、水力路径和事件扰动模拟思想，用于循环/回流/暂存路径覆盖合同。项目源：[USEPA/WNTR](https://github.com/USEPA/WNTR)。
- WaterTAP：借鉴水处理 flowsheet、单元模型、约束与成本建模组织方式，用于灰箱过程和工程约束设计。项目源：[watertap-org/watertap](https://github.com/watertap-org/watertap)。
- QSDsan：借鉴系统模拟、技术经济和可持续性评价组织方式，用于 reward/cost/sustainability 字段设计。项目源：[QSD-Group/QSDsan](https://github.com/QSD-Group/QSDsan)。
- Pyomo：借鉴结构化优化建模，把布点、动作选择、成本、风险和约束转成可求解接口。项目源：[Pyomo/pyomo](https://github.com/Pyomo/pyomo)。

## 一句话专业结论

本项目当前最强的技术主张是：把低成本传感、循环式水处理、软传感灰箱估计、知识证据、多智能体诊断控制和 field replay gate 组织成一个可验证、可终止、可逐步工程化的复杂系统，而不是单独宣称某个 AI 模型能够直接解决水处理问题。
