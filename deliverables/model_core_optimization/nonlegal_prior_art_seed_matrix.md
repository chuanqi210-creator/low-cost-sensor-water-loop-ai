# 非法律 Prior-Art 种子矩阵

生成日期：2026-06-04

## 定位

本文件不是正式专利检索报告、不是法律意见、不是新颖性/创造性结论。它的作用是把当前公开来源中已经能看到的相邻技术族先整理出来，作为后续 `formal_search_result_package`、人工非法律比对和专利代理人审查的输入种子。

当前模型不能把“AI、多智能体、软传感、知识图谱、闭环控制、稀疏布点”本身当作创新点。真正可能具备保护价值的是这些技术特征的受限观测组合链：

> 低成本 node-modality 稀疏感知 -> 软传感/灰箱隐藏状态估计 -> 循环/暂存结构争取低频证据时间 -> 机理证据/KG 约束诊断 -> 多智能体只生成保护性候选 -> field replay / operator review / release-actuator gate 决定是否晋级。

## Patentability 基准来源

| 来源 | 可借鉴规则 | 对本项目的约束 |
| --- | --- | --- |
| WIPO, How to Protect Inventions through Patents, https://www.wipo.int/en/web/patents/protection | 实质审查通常关注可专利主题、新颖性、创造性/非显而易见性、工业适用性和充分公开。 | 本项目不能只写抽象算法，要写成可制造/可使用的水处理系统结构、状态变量、动作和验证门。 |
| CNIPA, Patent Law of the PRC translation, https://english.cnipa.gov.cn/art/2022/10/13/art_3068_179273.html | 发明/实用新型授权需要新颖性、创造性和实用性。 | 后续交底要证明不是已有软传感、MARL、流程建模和水厂诊断系统的简单拼接。 |

## Prior-Art 种子表

| Seed | 外部来源 | 已公开能力 | 对本项目的风险 | 本项目可保留的区别点 | 需要补的证据 |
| --- | --- | --- | --- | --- | --- |
| PA1 | EP2414901B1, water purification soft sensor/control system, Google Patents, https://patents.google.com/patent/EP2414901B1/en | 已公开水净化系统中使用实时传感、COD soft sensor、状态估计、预测事件和控制。 | “软传感 + 状态估计 + 控制”不能作为独立创新点。 | 强调低成本稀疏 node-modality 布点、循环争取低频证据时间、field replay/operator/release gate 和保护性候选 no-write 边界。 | claim element chart：逐项比较 COD soft sensor、estimator、predictor 与本项目七层门控链。 |
| PA2 | WO2019071384A1, intelligent diagnosis/anomaly detection/control in wastewater or drinking water plants, Google Patents, https://patents.google.com/patent/WO2019071384A1/en | 已公开水厂数据采集、诊断、异常检测和控制动作。 | “智能水厂诊断 + 动态控制”表述非常宽，容易覆盖泛化 AI 控制说法。 | 把权利要求收窄到低成本受限观测、循环/暂存窗口、同 batch field replay 证据束、operator review、protective candidate evaluation。 | 对比其 claim 1-4 与本项目 R8p/R8v/R8u-56 的 gate 序列。 |
| PA3 | Advances in soft sensors for WWTPs: systematic review, Journal of Water Process Engineering 2021, https://doi.org/10.1016/j.jwpe.2021.102367 | WWTP soft sensor 已从机理模型发展到机器学习，并用于在线监测。 | 论文不能把“用软传感估计难测水质”当新贡献。 | 贡献应放在软传感如何被灰箱边界、不确定性、field holdout 和 release gate 约束，而不是点预测本身。 | field holdout、interval coverage、OOD/abstention、release gate 不写入证明。 |
| PA4 | Soft sensor enabled real-time chemical dosing control, Journal of Water Process Engineering 2024, https://doi.org/10.1016/j.jwpe.2024.105431 | 已有 soft sensor 支撑加药控制并进入 full-scale 应用。 | “软传感 + 投药控制 + 节省药剂”已是强相邻工作。 | 本项目不是单一投药控制，而是回流/暂存/延长停留/催化剂再生/单元切换/阻断放行的多动作保护性候选链。 | 对比单变量 dosing control 与多设施保护性候选 action bundle 的状态、动作、gate 差异。 |
| PA5 | PySensors repository and docs, https://github.com/dynamicslab/pysensors; https://python-sensors.readthedocs.io/en/stable/api/pysensors.reconstruction.html | 已有 sparse sensor placement for reconstruction/classification、SSPOR/SSPOC、SVD/PCA basis、QR/CCQR/GQR 等。 | “稀疏传感器布点优化”本身不是新。 | 本项目的布点矩阵必须绑定污染过程隐藏状态、低成本维护约束、软传感不确定性和下游控制晋级，而不是只优化重构误差。 | Agent48 多策略对照：random、cost-only、greedy、SSPOR-like、topology-aware；需真实 topology/labels。 |
| PA6 | Multi-agent RL optimal control for sustainable WWTPs, Chemosphere 2021, https://doi.org/10.1016/j.chemosphere.2021.130498 | 已有 MADDPG/MARL 用于 WWTP DO/加药优化，结合 LCA reward。 | “多智能体强化学习优化污水厂”已公开。 | 本项目应避免主张黑箱 MARL；强调多 agent 只生成候选，受 grey-box/KG/field replay/operator review/release gate 限制。 | Agent49/52 对比：无 guardrail MARL、规则控制、保护性候选 replay、误动作成本。 |
| PA7 | Multi-agent AI reinforcement full-scale WWTP digital multi-solution, Journal of Water Process Engineering 2023, https://doi.org/10.1016/j.jwpe.2023.103533 | 已有 full-scale WWTP 下多 influent 条件的 multi-agent reinforcement optimal operation。 | 多智能体运行优化与 full-scale 场景已不是空白。 | 本项目应把重点放在低成本传感不足、循环窗口、证据分级、模板/仿真阻断和 no-write 安全边界。 | 对比其 full-scale optimal operation 与本项目 field package / release gate 的执行前证据链。 |
| PA8 | Pollution-based integrated RTC for urban drainage systems using MARL, npj Clean Water 2025, https://www.nature.com/articles/s41545-025-00512-z | 已有 MARL 协调 sewer、WWTP、receiving water 的系统级实时控制。 | “多设施协同控制水系统”已有近期强工作。 | 本项目可保护点不在城市排水系统 MARL，而在处理单元内部受限观测下的循环式灰箱保护控制和 field replay 晋级。 | 对比系统边界、动作粒度、证据门和低成本传感假设。 |
| PA9 | WNTR official documentation, https://usepa.github.io/WNTR/overview.html | WNTR/EPANET 可建模管、泵、阀、节点、储罐、水力和水质模拟，支持事件/恢复策略。 | “水网络拓扑/水力仿真”不是新。 | 本项目可借鉴图拓扑，但差异在反应器/处理单元/回流环与污染反应状态估计，不是饮用水管网韧性仿真。 | 需要 site_topology_or_bed_geometry、flow/HRT/RTD、pressure/headloss field rows。 |
| PA10 | WaterTAP documentation, https://watertap.readthedocs.io/en/latest/index.html | WaterTAP 提供水处理 process/unit/network models，用于设计、优化和成本/能耗评估。 | “水处理流程建模/优化/成本”已有成熟框架。 | 本项目不和 WaterTAP 比高保真 flowsheet，而是定义低成本观测下的可验证控制 gate；WaterTAP 可作为实施例中的 process prior。 | 最小单元模型参数、进出水污染物、药剂/能耗、现场校准边界。 |
| PA11 | QSDsan documentation and RSC paper, https://qsdsan.readthedocs.io/; https://pubs.rsc.org/en/content/articlelanding/2022/ew/d2ew00455k | QSDsan 集成 process modeling、system simulation、TEA、LCA，用于 sanitation/resource recovery 系统设计。 | “系统仿真 + TEA/LCA”不是新。 | 本项目可以把 TEA/LCA 作为 reward/工程约束字段，不把经济性框架作为核心创新。 | CAPEX/OPEX、药剂、能耗、维护、再生周期和副产物风险实测/估计表。 |
| PA12 | Offline RL / Conservative Q-Learning, https://arxiv.org/abs/2006.04779; D4RL, https://github.com/Farama-Foundation/D4RL | 已有固定数据集、离线策略评估、保守学习和 benchmark 思路。 | “用 replay/offline RL 评估策略”不是新。 | 本项目可强调 replay 不是为了直接训练黑箱策略，而是作为写执行器/放行前的证据门。 | field state-action-reward replay、operator labels、action outcome、unsafe action blocker。 |

## Claim 收缩建议

### 不宜作为主创新点的表述

- “使用 AI 进行污水处理控制。”
- “使用多智能体系统优化水处理。”
- “使用软传感器预测水质。”
- “使用知识图谱解释污染物-材料关系。”
- “使用稀疏传感器降低成本。”

这些都容易被 PA1-PA12 覆盖或组合。

### 更适合作为主权利要求链条的表述

一种面向低成本稀疏传感条件的循环式水处理灰箱闭环控制方法，包括：

1. 构建处理单元、管网/反应器拓扑、循环/暂存结构和候选传感模态的 node-modality 观测矩阵。
2. 根据低成本传感值、缺测/延迟/噪声、离线检测标签和灰箱机理先验估计不可直接观测过程状态。
3. 基于知识图谱/source_basis 和灰箱机理边界对状态估计和故障诊断进行证据约束。
4. 由多智能体模块生成保护性控制候选动作，而不是直接生成执行器命令。
5. 通过 field package、同批次 replay、operator review、release gate 和 actuator safety interlock 判断候选动作是否晋级。
6. 根据门控结果动态选择回流、延长停留、暂存等待、投药调整候选、催化剂再生/更换候选、预处理/切换单元候选或继续阻断放行。

### 从属/分案更稳的方向

- 催化剂活性代理观测：UV254、ORP、pressure/headloss、再生事件、HRT/床体积和 offline catalyst_activity label 的同批次 holdout。
- pressure/headloss 多源冲突解除：node_modality pressure 与 pressure_headloss_event_log 冲突时，必须经 operator review、authoritative source 和 calibration action 才能进入控制晋级。
- 低频传感-循环窗口协同：用暂存/回流/延长停留显式换取 lab/proxy/operator evidence 到达时间。
- field replay 保护性写回：synthetic/template/literature 只能作为候选，field/operator-reviewed/release-gated 才能晋级执行边界。

## 对下一轮模型工作的影响

最高边际价值不变：

1. 如果能获得真实数据，优先导入 R7/R8p field package。
2. 如果没有真实数据，优先把 Agent48/49/52 做成可对比 baseline 的 replay/placement 实验，而不是继续加 agent。
3. 同步准备 formal search result package，但必须由真实检索结果和人工非法律 review 填充，不能把本 seed matrix 伪装成正式检索结果。

