# 项目成果包入口

本目录是整理阶段的统一入口。原始代码、报告和模板仍保留在各自目录中，避免破坏实验脚本路径；这里负责把它们组织成可查、可汇报、可继续实证校准的成果包。

## 一句话结论

最新增量：R8u187 修复了 formal search 人工非法律审查 operator packet 的上游依赖漂移。此前 Agent60 在无 `FORMAL_SEARCH_RESULT_PACKAGE_PATH` 的默认环境刷新后，会把 response template 合法退回 0 行，导致已有 7 行 AI brief/handoff 被误判为 `blocked_by_response_template`；现在 operator packet 会显式携带 `FORMAL_SEARCH_RESULT_PACKAGE_PATH=...preliminary_formal_search_result_package.json`，并从已通过边界的 AI brief 维持 7 行人工审查合同。当前系统仍处于 `internal_expansion_saturated_waiting_for_external_input`：最高主链下一步仍是提交真实 `FOCUSED_CATALYST_RESPONSE_PATH`，formal search 通道只作为人工审查 handoff，不生成法律意见、权利要求文本、field evidence、control readiness、actuator 或 release gate。

当前项目已完成原有 59-agent 工作链：从低成本传感、软传感灰箱估计、多智能体机理诊断、闭环控制、campaign 级重规划、恢复放量，到真实数据接口、现场校准门控、管网布点与稀疏感知、多设施协同控制、模型核心优化治理、灰箱/工程约束、可推理 KG、主链回接、现场验证队列对齐和 claim-specific 现场采集包。最新阶段已进入“模型架构复盘、模块化整合与核心链路减冗”：Agent60 仅作为复盘治理工具，已将原有 59 个 agent 映射为 9 个模块。R1/R1b 已完成统一 evidence gate 和 source_basis detail library，R2 已完成 Agent48/51/54 观测契约合并，R3/R3b/R3c 已把 Agent49/52 控制 replay 从反事实压力测试推进到 reward prior guardrails 与 guardrail-aware replay；R4 已把 R3c resolved cases 反写为灰箱机制边界和现场 replay 必采字段；R4b 已让 Agent53/58/59 消费这些 patch；R5 已把 guardrail 必采字段补入 Agent30/42 schema；R6 已把 claim package 的 source_basis_completion_rate 提升到 1.000。当前 R7 已形成真实现场数据包验收 facade，并将 Agent44 导入入口扩展为可直接读取 `REAL_FIELD_REPLAY_PACKAGE_DIR` 指向的 field package；R7 coverage 现已输出可机读 `patch_plan`，当前 5 个补包项把 R7a 具体化为 metadata provenance 替换和四张 CSV 真实 timestamped rows 补入；同时新增最小 timestamped replay 包契约，要求至少 3 个跨四张 replay 表对齐的共同 `batch_id`、可执行且时间可解析的 operation action、QA 通过且数值可用的 offline lab 结果、足够 proxy 事件、可解析 field-labeled fast proxy 标签，且这些有效 action/lab/proxy 证据必须落在同一批次，并满足 lab result、operation effect、proxy label 的时间顺序后才能进入 Agent42 smoke replay。Agent51 现已能从 R7j 包中提取 catalyst proxy field holdout 摘要，生成可评分批次数、相关性、MAE 和证据边界；R7S4b 已把 Agent49/52 多设施控制晋级与 Agent51 催化剂代理 holdout 接入真实包验收，确保 field replay evidence chain 局部通过也不能绕过催化剂 field validation 直接输出 protective control candidate；Agent48 已新增 hidden-state requirement ledger，把六类隐藏状态逐一转成 primary axes、required modalities、field evidence 和 minimum cost patch，当前 hard-unresolved hidden state 为 `catalyst_activity`；R2 observation contract 已消费该账本并新增 `R2_FV4_agent48_hidden_state_requirement_patch`；Agent60 已接入 R7 pipeline/coverage/replay contract 审计，同时在无真实 field package 时启用 offline fallback `R8b_agent48_pressure_headloss_candidate_pool_design`。

最新治理边界：External activation router 已把 `route_ready` 拆成 `model_chain_ready` 与 `handoff_ready`。R7 field package 和 R8u-66 path/endpoint package 通过预检时才允许恢复模型主链；R8u-79 formal search result package 即使通过预检，也只是外部/人工非法律检索交接 ready，不能被解释为 field replay、现场控制、field-supported claim、actuator 或 release gate ready。当前 R8u-108 已新增 field activation response submission packet，把 `FIELD_ACTIVATION_RESPONSE_PATH` 的填写、提交、预检命令和 no-write 边界集中为唯一入口；R8u-109 进一步把 R2/Agent48/51/54 的 `catalyst_activity` 观测弱轴映射到 6 条最高优先级 response rows，形成“观测合同 -> 现场补证模板 -> Agent51 holdout -> Agent49 guardrail”的可执行桥；R8u-110 再把这 6 条行升级为 focused response gate，用于检查真实 field origin、no-write、证据引用和至少 3 个共同 batch；R8u-111 将这 6 行生成 focused submission kit、schema 和 merge plan，降低外部 operator 从 33 行模板中回填的摩擦；R8u-112 新增 `FOCUSED_CATALYST_RESPONSE_PATH` source/preflight/merge 入口，可把填写后的 focused 小包合并成 full response candidate；R8u-126 又把该 source 入口升级为独立 source preflight，可区分未设置、缺文件、JSON 语法错误和根对象错误；R8u-130 进一步新增 `external_activation_operator_action_packet`，把当前最高外部动作整理为填写 6 行 focused catalyst response、设置 `FOCUSED_CATALYST_RESPONSE_PATH`、运行 focused merge、ready 后再设置 `FIELD_ACTIVATION_RESPONSE_PATH` 的可机读操作包，并显式列出拒收条件与 no-write 边界；R8u-131 已把该 packet 回接 Agent50 scorecard、priority ranking、governance report 和 manifest latest 指针；R8u-113 则把同一催化剂活性缺口进一步落到 R7/Agent51 真实包侧的四表 CSV 切片模板和 `CATALYST_FIELD_PACKAGE_SLICE_DIR` 预检，要求 sensor/lab/operation 至少 3 个共同 batch 与有效床层几何；R8u-114 进一步把 valid catalyst slice 覆盖进 full R7 package candidate 并运行 R7 preflight，显式暴露 metadata、required replay tables、path/endpoint labels 等剩余全包缺口；R8u-117 在 full response 进入 package assembly 前新增 coherence audit，检查隐藏状态 batch 对齐、sensor/operation 时间节点字段、offline lab method/detection limit、chain-of-custody 和 node 映射复核，防止“行级字段填满但证据组不可回放”的外部响应继续往 router 走；R8u-119 进一步把 `evidence_value` 加入 33 行 response row 合同，区分 `evidence_value_reference` 的溯源作用和实际机器可读值 payload，防止“只有引用、没有可计算值”的响应进入 package assembly；R8u-120 则把这些 value payload 转成 no-write CSV row blueprints，并让 materialized package preflight 检查 operator 物化包是否真正承接 response payload；R8u-124 把 33 行外部响应完成度做成 completion ledger；R8u-125 将 `next_hidden_state_focus=catalyst_activity` 自动路由到 6 行 focused catalyst handoff。Agent50 当前推荐已切换为 `FIELD_ACTIVATION_RESPONSE_FOCUS_HANDOFF_NEXT_ACTION`：先填写 focused catalyst 模板、设置 `FOCUSED_CATALYST_RESPONSE_PATH` 并运行 merge preflight，再把合并候选作为 `FIELD_ACTIVATION_RESPONSE_PATH` 重跑主链；系统仍不能绕过完整 response/package/router、field replay/holdout、operator review、actuator gate 或 release gate。

R8u-164 已把 grey-box submission readiness 的五张缺表合同继续投影到 operator-facing 外部包入口：`external_package_readiness_board.json`、`external_package_operator_action_packet.json`、对应 Markdown 和 manifest 现在都能直接看到 `GREY_BOX_CALIBRATION_PACKAGE_DIR` 的 `missing_table_count=5`、五张表 `batch_inlet_outlet_lab / hydraulic_rtd_or_tracer / oxidant_dose_residual_log / catalyst_age_regeneration_log / byproduct_panel`、模板目录和 preflight 命令。同步新增 `deliverables/model_core_optimization/engineering_model_governance_adapter.md`，从桌面复杂项目治理协议中只吸收低摩擦工程规则：current_basis/not_current_basis、紧凑路由、人看/机器看分层、manual_action_required 边界、子代理边界和 anti-bloat gate。当前完整回归为 `629 passed`，CodeGraph fallback 为 `405 files / 5323 nodes / 8448 edges`；本轮仍不生成 field evidence、不恢复模型链、不写 actuator/release gate。

R8u-165 在 R8u-164 基础上继续把 external package operator packet 升级为机器可恢复 handoff：`outputs/model_core_governance/external_package_operator_action_packet.json`、对应 Markdown 和 manifest 现在新增 `route_event=external_activation_wait`、`route_reason`、`evidence_level=operator_handoff_only_not_field_evidence`、`manual_action_required`、`current_basis_refs`、`not_current_basis_refs`、`can_prove` 与 `cannot_prove`。这让后续 agent 只读 operator packet 或 manifest 就能知道：当前只能提交真实外部包，不能把模板、synthetic、sample 或 literature 当成 field 证据，也不能恢复模型链或写 actuator/release gate。当前完整回归为 `630 passed`，CodeGraph fallback 为 `405 files / 5329 nodes / 8454 edges`。

R8u-166 已把 external package acquisition maturity gate 对齐当前 goal 的可计算终止条件：`outputs/model_core_governance/external_package_acquisition_maturity_gate.json`、对应 Markdown 和 manifest 现在直接显示输入/输出契约完整度、外部包交接状态变量覆盖、下游回接率、证据边界、失败边界、no-write 边界、终止状态和 blocker。当前接口合同与边界均为 `1.0`，但 `downstream_reconnection_rate=0.0`、`field_package_ready_rate=0.0`，所以 `module_stage_termination_pass=False`，终止阻断为 `downstream_reconnection_rate_below_0.80` 与 `field_package_ready_rate_below_1.00`。这说明系统骨架已经能机器判断“接口成熟但必须等待真实现场包”，而不是继续内部扩张。当前完整回归为 `631 passed`，CodeGraph fallback 为 `405 files / 5337 nodes / 8462 edges`；本轮仍不生成 field evidence、不恢复模型链、不写 actuator/release gate。

R8u-167 已把 R8u-166 的 acquisition termination snapshot 回接到最高核心阶段门：`outputs/model_core_governance/core_score_termination_gate.json` 与 `outputs/model_core_governance/priority_ranking.json` 现在都直接包含 `external_package_acquisition_stage_gate`，并在 `external_resume_conditions.new_core_interface` 下暴露 `external_package_acquisition_contract_termination_status`、`module_stage_termination_pass`、`termination_blockers`、`downstream_reconnection_rate` 和 `field_package_ready_rate`。这样后续只读主治理入口，也能知道 NEW_CORE_INTERFACE 当前不是“可继续内部扩张”，而是“接口成熟、真实外部包未就绪、阶段终止未通过”。当前完整回归为 `632 passed`，CodeGraph fallback 为 `405 files / 5340 nodes / 8465 edges`；本轮不提高 core_score、不生成 field evidence、不恢复模型链、不写 actuator/release gate。

R8u-168 已把同一 acquisition termination snapshot 继续回接到阶段边界外部行动板：`outputs/model_core_governance/stage_boundary_external_action_board.json`、`deliverables/model_core_optimization/stage_boundary_external_action_board.md` 和 manifest 现在都能直接看到 `new_core_interface_acquisition_contract_termination_status=external_package_contracts_complete_but_waiting_for_field_packages`、`module_stage_termination_pass=False`、`downstream_reconnection_rate=0.0`、`field_package_ready_rate=0.0` 与两个 termination blockers。该轮借鉴桌面复杂项目治理协议的“机器看版 handoff / next_route 不漂移 / 阶段门控”思想，修复的是最高操作者入口的恢复链断点：后续只看 action board 也不会误把 `NEW_CORE_INTERFACE` 理解成可继续内部扩张。当前完整回归为 `634 passed`，CodeGraph fallback 为 `405 files / 5345 nodes / 8470 edges`；本轮不提高 core_score、不生成 field evidence、不恢复模型链、不写 actuator/release gate。

R8u-169 已把阶段边界外部行动板升级为可独立恢复的机器看版入口：`outputs/model_core_governance/stage_boundary_external_action_board.json` 现在新增 `machine_handoff`，Markdown 报告新增 `## Machine Handoff`，manifest 同步暴露通用和 Agent50 两组 handoff 摘要。当前 handoff 明确显示 `route_event=external_activation_wait`、`next_route=submit_real_external_input_then_rerun_stage_preflight_and_agent50`、`next_route_source_env_var=FOCUSED_CATALYST_RESPONSE_PATH`、`manual_action_required=True`，并区分 `current_basis_refs`、`not_current_basis_refs`、`can_prove` 和 `cannot_prove`。这轮继续吸收桌面复杂项目治理协议的低摩擦恢复思想，解决“只读 action board 仍无法恢复阶段语义”的问题。当前完整回归为 `636 passed`，CodeGraph fallback 为 `405 files / 5352 nodes / 8477 edges`；本轮不生成 field evidence、不恢复模型链、不写 actuator/release gate。

R8u-170 已给 `machine_handoff` 增加可计算合同门：`outputs/model_core_governance/stage_boundary_external_action_board.json` 现在新增 `machine_handoff_contract_gate`，Markdown 和 manifest 同步暴露 gate status、score、stage pass 和 blockers。当前 `contract_score=1.0`、`contract_stage_pass=True`，说明 route、manual action、basis boundary、proof boundary、no-write boundary 和 recovery linkage 六个 handoff 合同维度都完整；同时 `external_wait_blockers=[real_external_input_required]` 明确说明这只是机器恢复合同完整，不是 field evidence 或模型链恢复。当前完整回归为 `638 passed`，CodeGraph fallback 为 `405 files / 5361 nodes / 8486 edges`；本轮不生成现场证据、不写 actuator/release gate、不输出法律/专利结论。

R8u-171 已把桌面复杂项目治理协议中的 `resource_boundary` 思想接入最高阶段边界行动板：`outputs/model_core_governance/stage_boundary_external_action_board.json` 现在新增 `resource_boundary` 与 `resource_boundary_gate`，Markdown 和 manifest 同步暴露通用/Agent50 两组资源边界摘要。当前 `resource_boundary_score=1.0`、`resource_boundary_stage_pass=True`，说明 allowed basis、forbidden basis、supplementary basis、gray zone、tool policy、manual annotation policy 和 no-write policy 七个维度已经机器可读；明确禁止把 template/synthetic/sample/literature-only rows、自声明未预检候选、formal-search handoff 或下游 gate 前的写入动作升级成 field evidence、法律/专利意见或 actuator/release 准备。当前完整回归为 `640 passed`，CodeGraph fallback 为 `405 files / 5369 nodes / 8494 edges`；本轮只增强依据边界和证据泄漏防护，不生成 field evidence、不恢复模型链、不写 actuator/release gate。

R8u-172 已新增跨产物恢复链一致性审计：`outputs/model_core_governance/governance_recovery_integrity_audit.json` 和 `deliverables/model_core_optimization/governance_recovery_integrity_audit.md` 现在检查 manifest 与 stage board 的 next route/source env var/manual action/resource forbidden basis 是否一致，validation command 是否存在，stage board JSON/Markdown 指针是否新鲜，manual action、basis boundary、resource boundary 和 no-write boundary 是否完整。当前 `recovery_integrity_score=1.0`、`recovery_integrity_stage_pass=True`、`blockers=[]`、`stale_or_mismatch_fields=[]`，`safe_next_route=submit_real_external_input_then_rerun_stage_preflight_and_agent50`；`change_inventory` 确认 stage board JSON、stage board Markdown、focused catalyst validation command 和 manifest 均存在。当前完整回归为 `642 passed`，CodeGraph fallback 为 `409 files / 5404 nodes / 8555 edges`；本轮只证明恢复链一致性，不生成 field evidence、不恢复模型链、不写 actuator/release gate。

R8u-173 已把桌面复杂项目启动前置治理协议进一步转译成工程模型恢复门，而不是复制成第二套协议。`governance_recovery_integrity_audit.json` 现在新增 `numeric_calculation_trace`，用 `mean(check_scores)` 复算 7 个恢复检查项，当前 `computed_score=1.0`、`reported_score=1.0`、`score_delta=0.0`、`trace_pass=True`；同时新增 `protocol_adaptation`，选择性吸收 `current_basis_contract`、`resource_boundary_contract`、`numeric_calculation_trace`、`dynamic_stage_handoff`、`micro_task_execution_check` 和 `subagent_orchestration_probe` 六条规则，延后四条会造成协议膨胀的规则，并通过 `anti_protocol_bloat_gate=pass_selective_adoption_not_full_protocol_copy`。manifest 已暴露 numeric/protocol 字段，后续 agent 不必扫完整 Markdown 也能恢复该治理状态；当前 targeted tests `103 passed`，完整回归 `642 passed`，CodeGraph fallback 为 `409 files / 5408 nodes / 8560 edges`；本轮仍只增强验证治理层，不生成 field evidence、不恢复模型链、不写 actuator/release gate。

R8u-174 已把恢复链 route alignment 从“只看 next_route”扩展到“路由事件、验证命令和依据边界也必须同步”。`governance_recovery_integrity_audit` 现在会比对 manifest 与 stage board 的 `route_event`、`next_route_validation_command`、`current_basis_refs` 和 `not_current_basis_refs`；若这些字段陈旧，即使 next_route 仍一致，也会把 `manifest_stage_board_route_alignment` 降为 `0.0`，并把 `safe_next_route` 改为 `repair_recovery_integrity_blockers_before_next_route`。通用和 Agent50 的 handoff manifest 摘要也已新增 validation command 字段。当前 targeted tests `104 passed`，完整回归 `643 passed`，CodeGraph fallback 为 `409 files / 5410 nodes / 8562 edges`；本轮只增强 stale route 防护，不生成 field evidence、不恢复模型链、不写 actuator/release gate。

R8u-175 已把桌面复杂项目治理协议中的子代理编排规则从“selected protocol rule”升级为真实工程检查。`stage_boundary_external_action_board.json` 现在新增 `subagent_orchestration_probe`，当前状态为 `subagent_orchestration_not_needed_for_external_wait`、`capability=not_needed`、`strategy=not_needed`、`tool_discovered=False`、`spawn_attempted=False`、`open_agent_cleanup_required=False`，并写明 no-spawn 原因；`governance_recovery_integrity_audit` 新增 `subagent_orchestration_integrity` 检查，能阻断“available 但没有 tool/spawn 证据”或“parallel_domains 但没有 roles”的虚报。manifest 已暴露通用和 Agent50 两组 subagent 摘要，`numeric_calculation_trace.component_count` 升级为 8。当前 targeted tests `107 passed`，完整回归 `646 passed`，CodeGraph fallback 为 `409 files / 5417 nodes / 8569 edges`。本轮只增强验证治理层、子代理能力边界和恢复可演化性，不实际开启子代理，不生成 field evidence、不恢复模型链、不写 actuator/release gate。

R8u-176/R8u-177 继续借鉴桌面复杂项目启动前置治理协议，但只把它转译成两个对当前工程模型有直接边际价值的运行门控。`stage_boundary_external_action_board.json` 现在新增 `low_friction_round_gate`，当前 `gate_status=low_friction_single_action_waiting_for_external_input`、`round_score=1.0`，把下一步收束为单一最高优先外部动作 `FIELD_ACTIVATION_RESPONSE_FOCUS_HANDOFF_NEXT_ACTION`，避免治理审查和自我打断过频。`governance_recovery_integrity_audit.json` 现在新增 `minimum_traceability_gate`，当前 `gate_status=minimum_recovery_traceability_pass`、`traceability_score=1.0`、`missing_link_count=0`，只追溯恢复路由中的依据、人工动作、资源/no-write 边界和 anti-bloat 规则，不扩大为全项目 traceability matrix。Agent60 的 formal search nonlegal review response AI 草稿边界也已刷新，AI 草稿不能替代人工非法律 review response。当前核心 targeted tests `126 passed`，完整回归 `652 passed`，CodeGraph fallback 为 `409 files / 5430 nodes / 8582 edges`。本轮仍只增强验证治理层，不生成 field evidence、不恢复模型链、不写 actuator/release gate、不输出法律/专利结论。

R8u-178 已把统一 field evidence gate 进一步升级为“主张升级边界”接口。`outputs/unified_field_evidence_gate/unified_field_evidence_gate_metrics.json` 现在新增 `claim_basis_promotion_gate`，每条统一证据记录都会生成 promotion row，说明当前可用依据、不可用依据、阻断原因、允许升级级别和下一步所需 gate。当前真实项目状态为 `claim_basis_promotion_blocked_until_field_validation`，5 条 promotion decision 全部被阻断，`ready_promotion_count=0`、`blocked_promotion_count=5`、`can_emit_field_claim_upgrade=False`、`can_write_to_actuator=False`、`can_write_to_release_gate=False`。这意味着 source_basis 文献细节完整只能增强 literature traceability，不能把 synthetic、template、formal handoff 或 literature 误写成 field-supported claim。Agent50 scorecard 与 manifest 已同步暴露该 gate。当前 targeted tests `68 passed`，完整回归 `656 passed`，CodeGraph fallback 为 `409 files / 5450 nodes / 8603 edges`；本轮只增强验证治理层、可保护性和证据升级边界，不生成 field evidence、不恢复模型链、不输出法律/专利结论、不写 actuator/release gate。

R8u-179 已把 `claim_basis_promotion_gate` 回接到最高阶段边界行动板。`stage_boundary_external_action_board.json` 现在新增 `claim_basis_promotion_snapshot`，因此后续只读 stage board 也能知道当前 5 条主张升级仍被真实 field validation 阻断，而不是只看到泛化的 `field_claim_upgrade_allowed=False`。当前 snapshot 为 `claim_basis_promotion_blocked_until_field_validation`，`ready_promotion_count=0`、`blocked_promotion_count=5`、`can_emit_field_claim_upgrade=False`，stage boundary effect 为 `keep_external_wait_until_real_field_validation_and_human_review`。`run_stage_boundary_external_action_board.py` 和 `run_agent50_model_core_governance.py` 均已写入通用/Agent50 manifest 字段。当前 targeted tests `74 passed`，完整回归 `658 passed`，CodeGraph fallback 为 `409 files / 5457 nodes / 8610 edges`；本轮只是恢复入口可见性回接，不改变 action 排序，不生成 field evidence、不恢复模型链、不写 actuator/release gate。

R8u-180 已把 Agent50 的模块阶段终止门从汇总判断升级为逐项可审查证明表。`core_score_termination_gate.json` 的 `module_stage_termination_gate` 现在包含 `termination_proof_status`、`termination_pass_rate` 和 7 行 `termination_proof_rows`，每行都说明 metric、阈值、当前值、是否通过、系统层、核心能力、证据来源、失败边界、field-claim boundary 以及 actuator/release no-write 边界。manifest 同步暴露 `latest_agent50_module_stage_termination_proof_status=module_stage_termination_proof_complete`、`latest_agent50_module_stage_termination_pass_rate=1.0`、`latest_agent50_module_stage_termination_proof_row_count=7`。当前 targeted tests `76 passed`，完整回归 `660 passed`，CodeGraph fallback 为 `409 files / 5462 nodes / 8615 edges`；本轮只增强验证治理层和阶段终止可解释性，不生成 field evidence、不恢复模型链、不写 actuator/release gate。

R8u-181 已把低摩擦阶段入口的“底层包语义”和“当前人机动作语义”分开。`stage_boundary_external_action_board.json` 的 `low_friction_round_gate` 现在保留 `selected_action_id=R8u139_R7_REAL_FIELD_PACKAGE` 与 `selected_underlying_action_id=R8u139_R7_REAL_FIELD_PACKAGE`，同时新增 `selected_canonical_action_id=FIELD_ACTIVATION_RESPONSE_FOCUS_HANDOFF_NEXT_ACTION`；这表示底层仍服务 R7 real field package，但当前真正要执行的是填写 6 行 focused catalyst response 并设置 `FOCUSED_CATALYST_RESPONSE_PATH`。通用和 Agent50 manifest 已同步暴露 canonical/underlying 字段。当前 targeted tests `35 passed`，完整回归 `660 passed`，CodeGraph fallback 为 `409 files / 5465 nodes / 8618 edges`；本轮只减少恢复入口歧义，不生成 field evidence、不恢复模型链、不写 actuator/release gate。

R8u-182 已把 `external_activation_operator_action_packet` 的下一步动作接口统一到项目通用字段。该 packet 仍保留 `packet_next_operator_action`，同时新增顶层 `next_operator_action`，两者当前均指向 `fill_outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json_with_real_field_values_then_set_FOCUSED_CATALYST_RESPONSE_PATH`；终端输出、Markdown 报告和 manifest latest 指针也统一消费该通用字段。这样后续 agent 或操作者只读 operator packet 时，不需要记忆特殊字段名即可恢复下一步 focused catalyst 外部填报动作。当前 targeted tests `78 passed`；本轮只增强工程可恢复性与接口一致性，不生成 field evidence、不恢复模型链、不写 actuator/release gate。

R8u-183 已把同一 focused catalyst 外部输入链路的 validation command 从裸脚本路径统一为可执行命令合同。`stage_boundary_external_action_board.json` 的 `machine_handoff.next_route_validation_command`、`low_friction_round_gate.manual_action_required.validation_command`、governance recovery audit 和 Agent50 推荐文本现在均使用 `.venv/bin/python experiments/run_focused_catalyst_response_merge.py`；Agent50 后续重跑提示也同步使用 `.venv/bin/python experiments/run_field_activation_matrix.py` 与 `.venv/bin/python experiments/run_agent50_model_core_governance.py`。这让最高优先真实输入动作可以直接复制执行，减少恢复摩擦；当前 targeted tests `3 passed`，recovery integrity 仍为 `1.0`。本轮不生成 field evidence、不恢复模型链、不写 actuator/release gate。

R8u-184 已把 focused catalyst operator packet 的最小执行包嵌入最高阶段入口。`stage_boundary_external_action_board.json` 的 R7/focused action row、operator runbook、`machine_handoff.manual_action_required`、`low_friction_round_gate.manual_action_required` 以及通用/Agent50 manifest 现在都直接暴露 focused template、schema、merge plan 和命令序列。也就是说，只读 stage board 或 manifest 即可知道：填 `outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json`，按 `focused_catalyst_response_schema.json`，设置 `FOCUSED_CATALYST_RESPONSE_PATH`，再运行 `.venv/bin/python experiments/run_focused_catalyst_response_merge.py`。当前 manifest 集成测试通过，recovery integrity 仍为 `1.0`；本轮只减少真实数据提交前的跨文件扫描，不生成 field evidence、不恢复模型链、不写 actuator/release gate。

R8u-185 已把同一最高入口的证据拒收条件补齐。`stage_boundary_external_action_board.json` 的 machine handoff、low-friction gate、operator runbook 以及通用/Agent50 manifest 现在都直接携带 `rejection_boundaries`、`boundary_checks` 和 `no_write_boundary`：明确拒收 template/sample/synthetic rows 作为 field evidence、拒收 TODO/template markers、拒收不足共同真实 batch 或未确认 no-write 的响应，并禁止跳过 focused merge、full response preflight、materialized package preflight、replay/holdout 和 operator review。当前 manifest 集成测试通过，recovery integrity 仍为 `1.0`；本轮只增强证据边界完整性，不生成 field evidence、不恢复模型链、不写 actuator/release gate。

R8u-132 已进一步把 `external_activation_operator_action_packet` 接入 `core_score_termination_gate.json` 的 `next_allowed_actions.NEW_CORE_INTERFACE` 与 `external_resume_conditions.new_core_interface`。因此后续只读取核心阶段门时，也能看到当前 operator packet 状态、目标隐藏状态、`FOCUSED_CATALYST_RESPONSE_PATH`、6 行 focused response 要求、下一操作和 no-write/no-resume 边界。

R8u-133 已新增 preliminary formal search result package：在没有真实 focused catalyst field response 的情况下，转向阶段门允许的 `FORMAL_SEARCH_RESULT_PACKAGE_PATH` 通道，生成 7/7 个 formal search work package 的公开来源比较包，并通过 Agent60 source preflight、row preflight 与 validation execution。当前 router 已显示 `handoff_ready_route_count=1`、`handoff_ready_channel_ids=[R8U79_FORMAL_SEARCH_RESULT_PACKAGE]`，但 `model_chain_ready_route_count=0`；这只允许进入人工非法律技术比较，不能恢复 field replay/control，不能写 actuator/release gate，也不能输出法律结论或权利要求文本。

R8u-134 已新增 formal search AI nonlegal review brief：在不越过人工审查门的前提下，把 R8u-133 的 7 个公开来源命中项压缩成 AI-assisted pre-review。该 brief 已映射 source URL、PTF 技术特征、TCS 技术骨架、risk tier、初步区别点、人工审查关注点和 preserved field validation gate；当前 `brief_row_count=7`、`missing_source_row_count=0`、`missing_claim_mapping_row_count=0`、`can_help_human_nonlegal_review=True`。它仍不是人工 review response，不是法律意见，不进入 claim patch，不生成权利要求文本；下一步若推进可保护性，仍必须提交 `FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH`。

R8u-135 已让 Agent50 消费 R8u-134 brief：现在 Agent50 scorecard、governance report、priority ranking 和 manifest 都能直接看到 `formal_search_ai_nonlegal_review_brief_ready_for_human_review`、7 行 brief、0 个 source/claim mapping 缺口、`can_help_human_review=True` 与 `can_route_to_claim_scope_patch_draft=False`。这只提升可保护性链的治理可见性；系统主链最高动作仍是 `FIELD_ACTIVATION_RESPONSE_FOCUS_HANDOFF_NEXT_ACTION`，即补真实 focused catalyst response。

R8u-136 已新增 formal search nonlegal review operator packet：现在人工非法律技术比较不再需要分散查找 AI brief、response template、source preflight、review readiness 和 claim patch blocker，而是统一读取 `outputs/agent_architecture_consolidation/formal_search_nonlegal_review_operator_packet.json` 或 `deliverables/model_core_optimization/formal_search_nonlegal_review_operator_packet.md`。当前 packet 显示 `expected_review_packet_row_count=7`、`high_priority_review_row_count=1`、`accepted_review_row_count=0`，下一步仍是设置 `FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH` 并提交人工 response；它不生成法律意见、prior-art 结论、权利要求文本或 field evidence，也不能恢复模型链、写 actuator 或 release gate。

R8u-137 已让 Agent50 消费 R8u-136 operator packet：现在 Agent50 scorecard、governance report、priority ranking 和 manifest 都能直接看到 `formal_search_nonlegal_review_operator_packet_ready_waiting_for_human_response`、7 行 human review contract、1 行 high-priority row、0 行 accepted row、`FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH` 与 `can_route_to_claim_scope_patch_draft=False`。这进一步压实可保护性链的治理可见性；它不替代人工审查、不生成法律意见、不生成权利要求文本，也不能恢复 field replay/control 或任何写入动作。

R8u-138 已把 R8u-136/R8u-137 的 operator packet 状态回接到最高核心阶段门：`core_score_termination_gate.json` 的 R8U79 formal-search action 和 `external_resume_conditions.formal_search_nonlegal_review_operator_packet` 现在都能看到 7 行人工 review contract、`FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH`、`can_route_to_claim_scope_patch_draft=False`、`can_resume_model_chain=False`、`can_emit_claim_text=False`、`can_write_to_actuator=False` 和 `can_write_to_release_gate=False`。这意味着后续只读核心阶段门的 agent 也不会误把 formal-search handoff 当成 field replay/control 或 claim text 通道。

R8u-139 已新增阶段边界外部行动板：当前 `core_score=0.96`、`iteration_delta=0.0`、`continue_expansion_allowed=False`，所以系统不应继续内部扩张，而应转向外部真实输入。新的 `outputs/model_core_governance/stage_boundary_external_action_board.json` 和 `deliverables/model_core_optimization/stage_boundary_external_action_board.md` 将下一步统一排序为：1）`FOCUSED_CATALYST_RESPONSE_PATH` 补 6 行 catalyst_activity focused field response；2）`FIELD_PATH_ENDPOINT_LABEL_PACKAGE_DIR` 补路径/终点标签包；3）`FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH` 补 7 行人工非法律 review response；4）只有在真正有新可测试接口时才走 `NEW_CORE_INTERFACE`。该行动板不生成证据、不恢复模型链、不写 actuator/release gate。

R8u-140 已把阶段边界外部行动板接入 Agent50 自动刷新链路：现在每次运行 `experiments/run_agent50_model_core_governance.py`，都会在刷新 core gate 后同步生成 `outputs/model_core_governance/stage_boundary_external_action_board.json` 和 `deliverables/model_core_optimization/stage_boundary_external_action_board.md`，并写入 Agent50 payload、`generated_files`、manifest 的 `latest_agent50_stage_boundary_external_action_board_*` 与通用 `latest_stage_boundary_external_action_board_*` 字段。当前自动刷新状态仍为 `stage_boundary_external_action_board_waiting_for_external_inputs`，`model_chain_resume_ready_count=0`，最高优先级仍是 `FOCUSED_CATALYST_RESPONSE_PATH`，且保持 actuator/release gate 不可写。

R8u-141 已把 focused merge 候选文件加入自证式 availability watermark：`outputs/focused_catalyst_response_merge/merged_full_field_activation_response_candidate.json` 现在即使被单独读取，也会显示 `candidate_availability_status`、`can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH`、外部 focused response 是否已提交、row/batch preflight 状态和候选使用边界。当前未提交 `FOCUSED_CATALYST_RESPONSE_PATH`，所以候选状态为 `candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH`、`self_declared_submit_ready=False`。Agent50 scorecard 和 manifest 已同步消费该状态，避免把 template/default candidate 文件误当成可提交 field evidence。

R8u-142 已把 R8u-141 的候选 availability 回接到阶段边界外部行动板：现在 `outputs/model_core_governance/stage_boundary_external_action_board.json` 的最高优先级 `R7_REAL_FIELD_PACKAGE` action row 不只显示 `FOCUSED_CATALYST_RESPONSE_PATH`，还显示 `focused_candidate_availability_status=candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH`、`focused_candidate_self_declared_submit_ready=False` 和外部 focused response 尚未提交。Agent50 自动刷新 action board 时也会同步这些字段，并写入 manifest。这样最高操作入口也能区分“候选文件存在”和“候选可提交”。

R8u-143 已把同一候选 availability 回接到 operator-facing 执行包：`outputs/model_core_governance/external_activation_operator_action_packet.json` 现在直接显示 `focused_candidate_availability_status=candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH`、`focused_candidate_operator_packet_submit_ready=False` 和候选使用边界。Agent50 scorecard、field evidence wait status、core gate 的 `new_core_interface` 与 `external_resume_conditions` 也同步消费这些字段。这样操作者只看 operator packet，也不会把 `merged_full_field_activation_response_candidate.json` 误当成可提交的 field activation response。

R8u-144 已把候选 availability 继续回接到最高 core gate 的 R7 action row：现在 `outputs/model_core_governance/core_score_termination_gate.json` 中的 `next_allowed_actions.R7_REAL_FIELD_PACKAGE` 直接显示 `external_activation_operator_action_packet_focused_candidate_availability_status=candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH`、`external_activation_operator_action_packet_focused_candidate_operator_packet_submit_ready=False`，并保留 `can_resume_model_chain=False`、`can_write_to_actuator=False`、`can_write_to_release_gate=False`。因此只读 core gate 的流程，也不会把候选文件误解为可提交外部证据包。

R8u-145 已进一步收紧阶段边界外部行动板的 submit-ready 语义：`highest_priority_focused_candidate_submit_ready` 不再等价于候选文件自声明 ready，而是必须同时通过 operator packet readiness、focused merge can-submit gate 和 row preflight。现在 `outputs/model_core_governance/stage_boundary_external_action_board.json`、`deliverables/model_core_optimization/stage_boundary_external_action_board.md` 与 `deliverables/manifest.json` 均区分 `focused_candidate_self_declared_submit_ready`、`focused_candidate_operator_packet_submit_ready` 和 canonical `focused_candidate_submit_ready`；当前两项可提交指标仍为 `False`。这样 action board 作为最高操作入口时，不会因字段命名把 diagnostic candidate 误读为可进入 field activation 的外部证据。

R8u-146 已把同一 submit-ready 语义收紧回推到 focused merge 源头：`outputs/focused_catalyst_response_merge/focused_catalyst_response_merge_preflight.json` 和 `outputs/focused_catalyst_response_merge/merged_full_field_activation_response_candidate.json` 现在新增 `candidate_preflight_submit_ready` / `merged_full_response_candidate_preflight_submit_ready` 与 `candidate_submit_ready_semantics`。`deliverables/model_core_optimization/focused_catalyst_response_merge.md` 不再只用含混的 self-declared 标签，而是明确该候选文件即使通过 focused 六行 merge gate，也只是 `FIELD_ACTIVATION_RESPONSE_PATH` 的下游预检输入，不是 field validation、model-chain resume、actuator 或 release readiness。Agent50 scorecard、priority ranking 和 manifest 也已消费该字段；当前 preflight submit-ready 仍为 `False`。

R8u-147 已把 `NEW_CORE_INTERFACE` 从泛化入口升级为 ranked candidate gate：新增 `outputs/model_core_governance/new_core_interface_candidate_gate.json` 和 `deliverables/model_core_optimization/new_core_interface_candidate_gate.md`，并接入 Agent50 自动刷新链路和 stage boundary action board。当前候选门显示 `candidate_count=5`、`admissible_candidate_count=5`，最高候选为 `NCI1_GREY_BOX_CALIBRATION_PACKAGE` / `GREY_BOX_CALIBRATION_PACKAGE_DIR`，对应灰箱物理校准接口；其后依次是 field-supported KG edge、field control replay、sparse topology installability 和 field missingness replay 等候选接口。该门只用于判断“如果没有真实 focused response，下一类值得定义的新核心接口是什么”，不实现 preflight、不生成 field evidence、不恢复模型链、不写 actuator/release gate。

R8u-148 已把 R8u-147 的最高候选 `GREY_BOX_CALIBRATION_PACKAGE_DIR` 落成灰箱校准包 preflight：新增 `outputs/grey_box_calibration_package/grey_box_calibration_package_preflight.json`、`outputs/grey_box_calibration_package/grey_box_calibration_package_template/` 和 `deliverables/model_core_optimization/grey_box_calibration_package_preflight.md`。该包要求五张最小现场校准表：进出水实验室对、水力 HRT/RTD、氧化剂/能耗、催化剂年龄/再生/活性标签、副产物 panel，并要求至少 3 个共同 `batch_id` 通过 field origin、QA、数值合法性和五表对齐。当前默认状态为 `grey_box_calibration_package_waiting_for_GREY_BOX_CALIBRATION_PACKAGE_DIR`，说明还没有外部真实校准包；候选门和阶段行动板已同步显示该 waiting 状态。该接口只判断能否进入 Agent53 field calibration consumer，不证明机理有效、不生成 field evidence、不写 actuator/release gate。

R8u-149 已把灰箱校准包 preflight 继续接到 Agent53 可消费的校准摘要：新增 `outputs/grey_box_calibration_package/grey_box_field_calibration_summary.json`，并让 `new_core_interface_candidate_gate`、`stage_boundary_external_action_board`、Agent50 generated files 和 manifest 同步消费 downstream calibration status。该 summary 从共同 batch 的进出水 lab、HRT/RTD 与副产物 panel 计算 `field_physics_coverage`、`max_field_residual`、`max_mass_balance_residual`、`mean_observed_k_per_min` 等 `field_calibration_for_agent53` 指标。当前默认仍未设置 `GREY_BOX_CALIBRATION_PACKAGE_DIR`，所以状态为 `grey_box_field_calibration_waiting_for_preflight_ready`、`can_run_agent53_field_calibration=False`、`agent53_field_candidate_ready=False`。该 adapter 只让通过 preflight 的外部包能进入 Agent53 field calibration，不生成 field evidence、不恢复模型链、不写 actuator/release gate。

R8u-150 已把第二个 new-core-interface 候选 `FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR` 落成现场支持 KG 边包 preflight：新增 `outputs/field_supported_kg_edge_package/field_supported_kg_edge_package_preflight.json`、`outputs/field_supported_kg_edge_package/field_supported_kg_edge_package_template/` 和 `deliverables/model_core_optimization/field_supported_kg_edge_package_preflight.md`。该包要求五张表共同证明一条 KG 边：污染物-材料/工况边、source_basis、field support、failure boundary、claim/action constraint，并要求至少 3 个共同 `edge_id` 通过 field origin、QA、field-supported evidence stage、现场支持分数和人工复核约束。当前默认未设置外部目录，所以状态为 `field_supported_kg_edge_package_waiting_for_FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR`。它只打开 KG reasoning 的现场边输入接口，不生成 site-specific mechanism claim、不生成 claim text、不写 actuator/release gate。

R8u-151 已把 P1/Agent48 的 new-core-interface 候选 `SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR` 落成真实拓扑与安装约束包 preflight：新增 `outputs/sparse_topology_installability_package/sparse_topology_installability_package_preflight.json`、`outputs/sparse_topology_installability_package/sparse_topology_installability_package_template/` 和 `deliverables/model_core_optimization/sparse_topology_installability_package_preflight.md`。该包要求五张表共同支撑稀疏感知布点：site topology graph、candidate node-modality costs、installability/maintenance constraints、node hydraulic delay 和 labeled state matrix，并要求至少 3 个共同 `node_id` 通过 field origin、QA、可安装/供电/通信、水力延迟、维护约束和隐藏状态标签检查。当前默认未设置外部目录，所以状态为 `sparse_topology_installability_package_waiting_for_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR`。它只允许后续进入 Agent48 sparse layout holdout，不证明可部署传感布局、不生成 field soft-sensor performance、不写 actuator/release gate。

R8u-152 已把 P3/Agent49/52 的 new-core-interface 候选 `FIELD_CONTROL_REPLAY_PACKAGE_DIR` 落成真实控制回放包 preflight：新增 `outputs/field_control_replay_package/field_control_replay_package_preflight.json`、`outputs/field_control_replay_package/field_control_replay_package_template/` 和 `deliverables/model_core_optimization/field_control_replay_package_preflight.md`。该包要求五张表共同支撑离线控制 replay：state-action-next-state transitions、reward components、operator/expert action labels、actuator latency/results 和 unsafe/override events，并要求至少 3 个共同 `transition_id` 通过 field origin、QA、状态转移、reward 分量、专家动作标签、执行器延迟一致性和人工复核安全边界。当前默认未设置外部目录，所以状态为 `field_control_replay_package_waiting_for_FIELD_CONTROL_REPLAY_PACKAGE_DIR`。它只允许后续进入 Agent49/52 offline replay，不证明策略优越、不解除 guardrail、不写 actuator/release gate。

R8u-153 已把 P5/Agent54 的 new-core-interface 候选 `FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR` 落成真实缺测回放包 preflight：新增 `outputs/field_missingness_replay_package/field_missingness_replay_package_preflight.json`、`outputs/field_missingness_replay_package/field_missingness_replay_package_template/` 和 `deliverables/model_core_optimization/field_missingness_replay_package_preflight.md`。该包要求五张表共同支撑软传感 missingness holdout：node-modality time series、availability mask、time-since-last-observed、sensor quality status 和 offline hidden-state labels，并要求至少 3 个共同 `sample_id` 通过 field origin、QA、缺测掩码、时间间隔、传感器质量和离线标签检查；同时要求至少 1 个真实 unavailable/missing 样本，避免全 available 数据伪装成缺测回放。当前默认未设置外部目录，所以状态为 `field_missingness_replay_package_waiting_for_FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR`。它只允许后续进入 Agent54/soft-sensor missingness holdout，不证明 field soft-sensor accuracy、不写 actuator/release gate。

R8u-154 已把五个 new-core-interface 外部包入口收束为统一 external package readiness board：新增 `outputs/model_core_governance/external_package_readiness_board.json` 和 `deliverables/model_core_optimization/external_package_readiness_board.md`，并接入 Agent50 主治理报告、payload、generated files 和 manifest。当前 board 显示 `package_count=5`、`ready_package_count=0`、`waiting_package_count=5`、`blocked_package_count=0`、`unimplemented_package_count=0`、`all_candidate_interfaces_have_preflight=True`；五个包分别是灰箱校准、field-supported KG edge、field control replay、sparse topology installability 和 field missingness replay，下一 operator env var 为 `GREY_BOX_CALIBRATION_PACKAGE_DIR`。这轮不新增 synthetic 模型能力，而是把真实数据采集入口做成统一工程看板：每个包都有模板路径、预检 JSON、报告、验证命令、next action 和 no-write boundary；它不运行 downstream replay/holdout/calibration，不生成 field evidence，不恢复模型链，不写 actuator 或 release gate。

R8u-155 已把 R8u-154 的 readiness board 进一步转成 external package operator action packet：新增 `outputs/model_core_governance/external_package_operator_action_packet.json` 和 `deliverables/model_core_optimization/external_package_operator_action_packet.md`，并接入 Agent50 主治理报告、payload、generated files 和 manifest。当前 packet 显示 `external_package_operator_packet_waiting_for_field_packages`，五个外部包全部处于采集等待态；下一操作是填写灰箱校准包模板、设置 `GREY_BOX_CALIBRATION_PACKAGE_DIR`，并运行 `.venv/bin/python experiments/run_grey_box_calibration_package_preflight.py`。这轮把“看见缺口”推进到“可执行采集队列”：每个包都带 `action_status`、模板目录、环境变量、验证命令、提交后运行命令、最小行数、输入/输出合同、失败边界和拒收规则；仍不生成 field evidence、不运行 downstream replay/holdout/calibration、不恢复模型链、不写 actuator 或 release gate。

R8u-156 已把 external package readiness board 与 operator action packet 转成 acquisition maturity gate：新增 `outputs/model_core_governance/external_package_acquisition_maturity_gate.json` 和 `deliverables/model_core_optimization/external_package_acquisition_maturity_gate.md`，并接入 Agent50 主治理报告、payload、generated files 和 manifest。当前五个外部包接口均已有 preflight 和 operator action contract，no-write boundary 完整，`acquisition_maturity_score=0.85`；但真实包 ready 数仍为 0，`field_package_ready_rate=0.0`。因此该门只说明“采集接口成熟，下一步应停止内部扩张并采集真实外部包”，不说明现场证据成熟。当前下一步仍是补 `GREY_BOX_CALIBRATION_PACKAGE_DIR` 并运行 `.venv/bin/python experiments/run_grey_box_calibration_package_preflight.py`；不生成 field evidence、不恢复模型链、不运行 downstream replay/holdout/calibration、不写 actuator 或 release gate。

R8u-157 已把当前最高优先级的 `GREY_BOX_CALIBRATION_PACKAGE_DIR` 进一步落成灰箱校准采集工单：新增 `outputs/grey_box_calibration_package/grey_box_calibration_collection_work_order.json` 和 `deliverables/model_core_optimization/grey_box_calibration_collection_work_order.md`，并接入 grey-box runner、manifest、Agent50 generated files 和 Agent50 payload。工单把五张表 `batch_inlet_outlet_lab`、`hydraulic_rtd_or_tracer`、`oxidant_dose_residual_log`、`catalyst_age_regeneration_log`、`byproduct_panel` 逐项列出模板 CSV、必填列、共同 `batch_id`、最小 3 个共同批次、`data_origin=field`、QA 要求、当前有效行数和修复状态。当前状态为 `grey_box_calibration_collection_work_order_waiting_for_external_package`，说明仍需要真实外部包；它不运行 Agent53 field calibration、不生成 field evidence、不恢复模型链、不写 actuator 或 release gate。

R8u-158 已把本轮子代理复盘结果压成 `core_interface_consolidation_facade`：新增 `outputs/model_core_governance/core_interface_consolidation.json` 和 `deliverables/model_core_optimization/core_interface_consolidation.md`。该 facade 不再新增线性 agent，而是把当前核心模型接口收束成三块：`external_package_lifecycle` 统一灰箱校准、field control replay、sparse topology/installability 三类外部包生命周期；`sparse_layout_soft_sensor_coupling_benchmark` 将 Agent48 六类布点策略与 missingness stress、软传感 schema readiness、`catalyst_activity` blocker 和 pressure/headloss gap 统一评分；`field_control_replay_crosswalk` 将 `FIELD_CONTROL_REPLAY_PACKAGE_DIR` 的五张表映射到 Agent52 replay schema 与 release gate 条件。当前 `top_external_action_env_var=GREY_BOX_CALIBRATION_PACKAGE_DIR`，`new_agent_recommendation=do_not_add_linear_agent`，后续只有真实 field package、Agent48 layout metrics 或 Agent52 replay schema 变化时才刷新该 facade。验证：R8u158/外部包/Agent48/field-control targeted tests `45 passed`，完整回归 `616 passed`，CodeGraph 为 `402 files / 5277 nodes / 8384 edges`。它不生成 field evidence、不恢复模型链、不放松 Agent49 guardrail、不写 actuator 或 release gate。

R8u-159 已把 R8u158 facade 回接到 Agent50 主治理运行：`experiments/run_agent50_model_core_governance.py` 现在自动刷新 `core_interface_consolidation.json` 与对应 Markdown，并把它写入 Agent50 report、JSON payload、generated files 和 manifest。新增 `tests/test_agent50_core_interface_integration.py` 保护该消费链路，deliverable organization 的 governance index 也已包含 core interface JSON/Markdown。当前 Agent50 明确输出 `core_interface_consolidation_consumed_by_agent50=True`、`core_interface_consolidation_refresh_status=agent50_runner_refreshed_current_facade`、`top_external_action_env_var=GREY_BOX_CALIBRATION_PACKAGE_DIR`、`new_agent_recommendation=do_not_add_linear_agent`。验证：R8u159 targeted tests `113 passed`，完整回归 `618 passed`，CodeGraph 为 `403 files / 5280 nodes / 8395 edges`。它是治理主链回接，不生成 field evidence、不恢复模型链、不写 actuator/release gate；下一步最高外部证据动作仍是补齐 `GREY_BOX_CALIBRATION_PACKAGE_DIR` 灰箱校准真实包。

R8u-160 已把 `GREY_BOX_CALIBRATION_PACKAGE_DIR` 从“等待真实包 + 表级工单”推进为可计算 submission readiness gate：新增 `outputs/grey_box_calibration_package/grey_box_submission_readiness_gate.json` 和 `deliverables/model_core_optimization/grey_box_submission_readiness_gate.md`，并接入 grey-box runner、Agent50 report/payload/generated files、manifest 和 deliverable organization。该 gate 计算 source package、schema、field origin、matched batch、signal validity、Agent53 summary、residual threshold 和 no-write boundary 等组件分数，输出 `readiness_score`、`gate_status`、`highest_priority_gap`、`can_submit_to_agent53_field_calibration` 和 `can_submit_to_agent53_field_candidate`。当前默认无外部包，所以状态为 `grey_box_submission_readiness_waiting_for_external_package`、score=`0.143`、gap=`missing_external_package`。验证：R8u160 targeted tests `96 passed`，完整回归 `623 passed`，CodeGraph 为 `404 files / 5301 nodes / 8422 edges`。它不生成 field evidence、不证明机理、不恢复模型链、不写 actuator/release gate；下一步仍是提交真实灰箱校准五表包。

R8u-161 已把 R8u160 的 grey-box submission readiness gate 回接到 `core_interface_consolidation`：`external_package_lifecycle` 的 `grey_box_calibration` 行现在直接显示 `submission_readiness_gate_status`、`submission_readiness_score`、最高缺口、Agent53 提交标志和 no-write 边界；`run_core_interface_consolidation.py` 与 Agent50 runner 都会读取 `outputs/grey_box_calibration_package/grey_box_submission_readiness_gate.json` 并刷新 core interface JSON/Markdown 与 manifest 摘要。当前 core interface 显示 `grey_box_submission_readiness_waiting_for_external_package / 0.143`，最高缺口仍为 `missing_external_package`，说明下一步仍是提交真实 `GREY_BOX_CALIBRATION_PACKAGE_DIR` 五表包。验证：相关测试 `25 passed`，core/grey-box/Agent50/组织/治理 targeted tests `91 passed`，完整回归 `627 passed`，CodeGraph fallback 为 `404 files / 5309 nodes / 8431 edges`。它是接口回接和消费证明，不生成 field evidence、不恢复模型链、不写 actuator 或 release gate。

R8u-162 已把 grey-box submission readiness 的默认缺口从空表名修正为可机器路由的外部包缺失说明：当 `GREY_BOX_CALIBRATION_PACKAGE_DIR` 未提交时，`highest_priority_gap` 现在显示 `table=all_required_tables`、`missing_table_count=5`，并列出 `batch_inlet_outlet_lab`、`hydraulic_rtd_or_tracer`、`oxidant_dose_residual_log`、`catalyst_age_regeneration_log`、`byproduct_panel` 五张必需表。core interface 的 `grey_box_calibration` lifecycle row 也同步投影 `submission_missing_table_count`、`submission_missing_tables` 和 `submission_source_env_var`，Markdown 报告显示 `missing_tables=5`。验证：grey-box/core/Agent50/组织/治理 targeted tests `91 passed`，完整回归 `627 passed`，CodeGraph fallback 为 `404 files / 5309 nodes / 8431 edges`。它只是证据边界和外部提交可执行性修复，`readiness_score` 仍为 `0.143`，不生成 field evidence、不恢复模型链、不写 actuator 或 release gate。

R8u-163 已把同一缺表清单压到 manifest 入口：现在只读 `deliverables/manifest.json`，也能直接看到 `latest_grey_box_submission_readiness_missing_table_count=5`、五张 `missing_tables`、`source_env_var=GREY_BOX_CALIBRATION_PACKAGE_DIR`，并且 Agent50 与 core-interface 两组 manifest 摘要同步一致。这样后续 agent 不必再打开多个 JSON 才知道灰箱真实包到底要补哪几张表。验证：manifest 契约单测通过，core/grey-box/Agent50/组织/治理 targeted tests `91 passed`，完整回归 `627 passed`，CodeGraph fallback 为 `404 files / 5309 nodes / 8431 edges`。它仍只是 manifest 入口与工程提交可执行性修复，不改变 `readiness_score=0.143`，不生成 field evidence、不写 actuator 或 release gate。

## 核心文档

| 类型 | 文件 | 用途 |
| --- | --- | --- |
| CodeGraph 入口 | `CODEGRAPH.md` | 后续进入项目时的结构化入口，减少重复全仓扫描 |
| CodeGraph 摘要 | `deliverables/codegraph/codegraph_summary.md` | 机器生成的文件、Agent、实验、测试、产物关系索引 |
| Word 研究方案 | `docs/研究方案_Word兼容版.docx` | 对外阅读和汇报的 Word 版方案 |
| 系统规格 | `docs/agent_system_spec.md` | 执行链、支持层、动作空间、安全门和验证结果 |
| 项目级总览 | `docs/project_overview_28_agent.md` | 28 个执行 agent 的模块化总览和证据链 |
| 真实数据接口 | `docs/field_data_interface_spec.md` | 现场数据表 schema、字段、主键和校准对象 |
| 当前状态 | `notes/current_status.md` | 最新模型状态、验证结果和下一步 |
| 迭代日志 | `notes/iteration_log.md` | 每轮 agent 迭代的原因、修复、结果和结论 |

## CodeGraph 导航层

| 内容 | 路径 | 用途 |
| --- | --- | --- |
| 根入口 | `CODEGRAPH.md` | 进入项目后先读，按核心链路跳转，不再盲目 scan |
| 图谱配置 | `codegraph.config.json` | 未来安装原生 CodeGraph CLI 后复用的扫描边界 |
| 本地构建脚本 | `tools/build_project_codegraph.py` | 当前无 Node/CLI 条件下的项目级图谱生成器 |
| 完整图谱 JSON | `deliverables/codegraph/project_codegraph.json` | 节点、边、agent 索引、hotspot 和 scan shortcut |
| 节点/边 CSV | `deliverables/codegraph/project_codegraph_nodes.csv`、`deliverables/codegraph/project_codegraph_edges.csv` | 可表格查看或继续加工 |
| 最短阅读路径 | `deliverables/codegraph/scan_shortcuts.md` | 后续 agent/人类协作时的低摩擦阅读顺序 |

## 核心模型逻辑图

| 内容 | 路径 | 用途 |
| --- | --- | --- |
| 全模型逻辑图 v2 | `deliverables/model_core_optimization/whole_model_logic_map_v2.png` | 展示“低成本稀疏感知 -> 软传感灰箱 -> 多智能体诊断 -> 循环控制 -> 现场校准写回”的完整模型逻辑 |
| 当前兼容入口 | `deliverables/model_core_optimization/whole_model_logic_map.png` | 与旧文件名兼容，内容已同步为 v2 |

## 关键报告

| 阶段 | 报告 | 说明 |
| --- | --- | --- |
| 全链条 | `outputs/full_chain/full_chain_report.md` | 单批次 agent 链条汇总 |
| 多场景 | `outputs/scenario_sweep/scenario_sweep.md` | 典型污染/故障场景扫查 |
| 鲁棒性 | `outputs/closed_loop_robustness/closed_loop_robustness.md` | 多 seed 闭环鲁棒性结果 |
| 传感配置 | `outputs/design_sensitivity/design_sensitivity.md` | 低成本传感窗口与成本敏感性 |
| 重规划验证 | `outputs/agent23_post_replan_replay/agent23_report.md` | 自动重规划写回后的回放验证 |
| 恢复执行 | `outputs/agent27_recovery_execution_replay/agent27_report.md` | 0.75 条件恢复执行回放 |
| 恢复在线控制 | `outputs/agent28_recovery_online_control/agent28_report.md` | 0.75 维持、0.60 回退线和重规划状态 |
| 项目综合 | `outputs/agent29_project_synthesis/agent29_report.md` | 模块表、总流程图、证据链和校准路线 |
| 真实数据接口 | `outputs/agent30_field_data_interface/agent30_report.md` | schema 检查、模板状态和校准任务 |
| 成果整理 | `outputs/agent31_deliverable_organization/agent31_report.md` | 执行摘要、汇报提纲、关键数值和成果索引 |
| 图表素材 | `outputs/agent32_presentation_assets/agent32_report.md` | 视觉故事板、图表规格、讲述脚本和项目书素材 |
| 正式展示包 | `outputs/agent33_presentation_deck/agent33_report.md` | claim spine、设计系统、QA 清单和 PPTX 交付 |
| 实证校准门控 | `outputs/agent34_field_calibration_gate/agent34_report.md` | 现场校准协议、验收门、运行手册和参数写回顺序 |
| 模型真实性审计 | `outputs/agent35_model_realism_audit/agent35_report.md` | 知识库、软传感、现场校准、过程模型和 skill 工作流审计 |
| 软传感不确定性验证 | `outputs/agent36_soft_sensor_uncertainty_validation/agent36_report.md` | synthetic holdout 上的预测区间覆盖、误差关联、OOD 门和 field holdout 需求 |
| 知识图谱策展 | `outputs/agent37_knowledge_graph_curation/agent37_report.md` | KG 轴覆盖、证据等级、科学审查链和 field-supported edge 缺口 |
| 文献证据抽取 | `outputs/agent38_literature_evidence/agent38_report.md` | 文献 claim 到模型升级、数据需求、评价指标和失败边界的映射 |
| 软传感保形校准 | `outputs/agent39_soft_sensor_conformal_calibration/agent39_report.md` | split conformal 区间、覆盖率、区间宽度、放行 abstention 和 field holdout 写回边界 |
| 灰箱动态延迟审计 | `outputs/agent40_grey_box_dynamic_latency/agent40_report.md` | 采样、检测、人工复核、执行器、混合、暂存和回流的时序约束与延迟违约边界 |
| 基质冲击快代理控制 | `outputs/agent41_matrix_shock_fast_proxy/agent41_report.md` | EC/浊度/UV254/pH/ORP 快代理、保护性预处理/切换和禁止自动放行边界 |
| 时间戳回放接口 | `outputs/agent42_timestamped_campaign_replay/agent42_report.md` | sensor/lab/operation/fast_proxy_event_log 同轴回放、快代理 precision/recall 和误触发成本校准入口 |
| 现场回放校准门控 | `outputs/agent43_field_replay_calibration_gate/agent43_report.md` | G6/P6 硬验收门、保护性控制写回许可和自动放行禁止边界 |
| 现场 replay 导入门 | `outputs/agent44_field_replay_import/agent44_report.md` | metadata provenance、field origin、CSV 字段、类型转换和 batch 回连验收 |
| 现场 replay 证据链 | `outputs/agent45_field_replay_evidence_chain/agent45_report.md` | Agent44 -> Agent42 -> Agent43 完整链条与保护性写回候选边界 |
| 软传感 field holdout 放行门控 | `outputs/agent46_soft_sensor_field_holdout_gate/agent46_report.md` | Agent36 -> Agent39 -> Agent46 的 release gate 校准候选硬门控 |
| 弱目标分层保形校准 | `outputs/agent47_weak_target_stratified_conformal/agent47_report.md` | catalyst_activity / matrix_interference 的 target/scenario coverage 审查 |
| 管网布点与稀疏感知 | `outputs/agent48_sensor_network_sparse_placement/agent48_report.md` | node-modality 稀疏观测矩阵与布点候选 |
| 多设施协同控制 | `outputs/agent49_multi_facility_collaborative_control/agent49_report.md` | facility-state/action 矩阵、联合奖励函数、决策树策略蒸馏，以及 Agent51 catalyst holdout summary 到 R3G1 控制边界的联动 |
| 模型核心优化治理 | `outputs/agent50_model_core_governance/agent50_report.md` | 边际价值排序、外部方法 evidence matrix 和自我打断评估 |
| 催化剂活性代理观测 | `outputs/agent51_catalyst_activity_proxy/agent51_report.md` | catalyst_activity 代理观测、补点设计和 Agent49 保护边界 |
| Agent51 field holdout 摘要 | `outputs/catalyst_activity_proxy/field_proxy_holdout_summary.json` | 从 R7j package 提取 catalyst proxy 可评分批次、相关性、MAE 和写回边界 |
| 多设施 replay 离线评估 | `outputs/agent52_multi_facility_replay_evaluation/agent52_report.md` | Agent49 state-action-reward replay schema、离线评价指标、Agent51 catalyst proxy field validation gate 和写回边界 |
| 最小灰箱物理机制 | `outputs/agent53_minimal_grey_box_physics/agent53_report.md` | 停留时间、旁路短流、反应速率、质量守恒和副产物风险的 physics prior |
| 软传感矩阵耦合 | `outputs/agent54_soft_sensor_matrix_coupling/agent54_report.md` | Agent48 布点矩阵、缺失掩码、低频/延迟观测和 Agent53 灰箱先验到软传感输入合同的连接 |
| 工程执行约束 | `outputs/agent55_engineering_execution_constraints/agent55_report.md` | 池容、泵阀、药剂库存、维护窗口、人工复核和误动作成本进入 Agent49 reward 与最终仲裁 |
| 架构复盘与减冗治理 | `outputs/agent60_agent_architecture_consolidation/agent60_report.md` | 原有 59-agent 系统的模块映射、核心链路消费关系、冗余合并清单和下一轮重构排序 |
| 统一证据门控 | `outputs/unified_field_evidence_gate_report/unified_field_evidence_gate_report.md` | 合并 Agent43/44/45/46/58/59 的 field evidence、claim package、source_basis 和 replay/holdout gate |
| 观测契约合并 | `outputs/observation_contract_merge_report/observation_contract_merge_report.md` | 合并 Agent48 稀疏布点、Agent51 催化剂代理观测和 Agent54 软传感矩阵合同 |
| 控制 replay 反事实压力测试 | `outputs/control_replay_counterfactual_stress_report/control_replay_counterfactual_stress_report.md` | 比较 baseline、R2 observation-aware policy 和 R3 guardrail candidate 的 regret、误保护和工程阻断 |

## 正式展示包

| 内容 | 路径 |
| --- | --- |
| PPTX | `deliverables/ppt/low_cost_water_ai_formal_deck.pptx` |
| Claim spine | `deliverables/deck_claim_spine.md` |
| 设计系统 | `deliverables/deck_design_system.md` |
| QA 清单 | `deliverables/deck_qa_checklist.md` |

## 真实数据模板

| 内容 | 路径 |
| --- | --- |
| Schema JSON | `outputs/agent30_field_data_interface/field_data_schema.json` |
| 空 CSV 采集模板 | `outputs/agent30_field_data_interface/field_data_templates/` |
| 合成样例数据包 | `outputs/agent30_field_data_interface/synthetic_field_data_package/` |

注意：`synthetic_field_data_package/` 只用于接口演示和导入流程测试，不能作为现场实证结论。

## 实证校准门控

| 内容 | 路径 |
| --- | --- |
| 现场实证校准协议 | `deliverables/field_calibration_protocol.md` |
| 现场数据验收门 | `deliverables/field_data_acceptance_gates.md` |
| 现场校准运行手册 | `deliverables/field_calibration_runbook.md` |

当前 Agent34 判断：`calibration_protocol_ready_waiting_for_field_data`。基础 G0-G5 门控已有 5/6 个可按模板检查，阻塞项是 `G0_data_origin`，即必须导入真实 `field` 数据，不能用 synthetic/sample 行进行参数校准。Agent43 后已扩展 G6 时间戳回放门，快代理保护性控制还必须补真实 field-labeled fast_proxy_event_log。

## 模型真实性审计

| 内容 | 路径 |
| --- | --- |
| 模型真实性审计 | `deliverables/model_realism_audit.md` |
| 模型优化 Backlog | `deliverables/model_upgrade_backlog.md` |

当前 Agent35 判断：`simulation_baseline_needs_field_grounding`。知识库已扩展到 9 条并新增证据阶段/现场验证需求，但训练数据仍是 synthetic-only；软传感器已有 synthetic 不确定性层，下一步必须用真实 field holdout 校准预测区间、释放概率和外推风险门。

## 软传感不确定性验证

| 内容 | 路径 |
| --- | --- |
| 软传感不确定性验证 | `deliverables/soft_sensor_uncertainty_validation.md` |
| Agent36 报告 | `outputs/agent36_soft_sensor_uncertainty_validation/agent36_report.md` |
| 不确定性指标 JSON | `outputs/soft_sensor_training/soft_sensor_uncertainty_metrics.json` |

当前 Agent36 判断：`synthetic_uncertainty_layer_ready_needs_field_holdout`。不确定性层已进入软传感 release gate，synthetic holdout 上区间覆盖率为 1.0，且高不确定性样本平均误差高于低不确定性样本；但这仍然只是仿真 holdout，不等同于现场校准。

## 知识图谱策展

| 内容 | 路径 |
| --- | --- |
| 知识图谱策展审计 | `deliverables/knowledge_graph_curation.md` |
| KG schema | `deliverables/knowledge_graph_schema.md` |
| Agent37 报告 | `outputs/agent37_knowledge_graph_curation/agent37_report.md` |
| KG records JSON | `outputs/agent37_knowledge_graph_curation/knowledge_graph_records.json` |

当前 Agent37 判断：`scientific_kg_seed_needs_literature_and_field_evidence`。知识库已被整理为污染物、基质、材料、过程条件、低成本信号、隐藏状态和证据等级七类轴；当前轴覆盖分数为 0.700，最大边界是 field-supported edges 仍为 0，污染物轴还缺染料、抗生素和农药，原始低成本信号到隐藏状态的证据边仍偏弱。

## 文献证据抽取

| 内容 | 路径 |
| --- | --- |
| 文献证据矩阵 | `deliverables/literature_evidence_matrix.md` |
| 文献抽取 schema | `deliverables/literature_evidence_schema.md` |
| Agent38 报告 | `outputs/agent38_literature_evidence/agent38_report.md` |
| 文献证据 records JSON | `outputs/agent38_literature_evidence/literature_evidence_records.json` |

当前 Agent38 判断：`literature_seed_ready_field_validation_required`。8 条文献 seed 覆盖 KG 缺口 0.889，已补染料、抗生素、农药轴，并把软传感保形校准、灰箱动态控制延迟、Scientific KG field-supported edges 和污染物特异过程轴列为模型升级映射；但所有文献记录仍标注为 `field_validation_required`。

## 软传感保形校准

| 内容 | 路径 |
| --- | --- |
| 软传感保形校准报告 | `deliverables/soft_sensor_conformal_calibration.md` |
| Agent39 报告 | `outputs/agent39_soft_sensor_conformal_calibration/agent39_report.md` |
| 保形校准指标 JSON | `outputs/soft_sensor_training/soft_sensor_conformal_metrics.json` |

当前 Agent39 判断：`synthetic_conformal_interface_ready_needs_field_holdout`。split conformal 接口已能从 Agent36 的验证误差中生成目标级阈值、覆盖率、区间宽度、scenario full coverage、放行 abstention 和 OOD 风险统计；当前 synthetic holdout 覆盖率为 0.975，平均区间宽度为 0.233，但 `can_write_to_release_gate=False`，必须在真实 field holdout 上重算阈值后才能写入放行门。

## 灰箱动态延迟审计

| 内容 | 路径 |
| --- | --- |
| 灰箱动态延迟审计 | `deliverables/grey_box_dynamic_latency.md` |
| Agent40 报告 | `outputs/agent40_grey_box_dynamic_latency/agent40_report.md` |
| 延迟预算指标 JSON | `outputs/grey_box_dynamic_latency/latency_budget_metrics.json` |

当前 Agent40 判断：`synthetic_latency_budget_ready_needs_field_timestamps`。延迟预算已把采样间隔、质控窗口、软传感计算、人工复核、离线检测、执行器响应、混合、暂存和回流统一成时序约束；当前 synthetic replay 延迟违约率为 0.200，`matrix_shock` 场景慢证据余量为 -31 min。该层只能作为模型真实性审计，必须采集现场 timestamped campaign replay 后才能写入 release gate。

## 基质冲击快代理控制

| 内容 | 路径 |
| --- | --- |
| 基质冲击快代理控制 | `deliverables/matrix_shock_fast_proxy_control.md` |
| Agent41 报告 | `outputs/agent41_matrix_shock_fast_proxy/agent41_report.md` |
| 快代理指标 JSON | `outputs/matrix_shock_fast_proxy/fast_proxy_metrics.json` |

当前 Agent41 判断：`synthetic_fast_proxy_ready_needs_field_timestamp_validation`。`matrix_shock` 在 synthetic replay 中由 EC、浊度、UV254、pH 和 ORP 快代理触发保护性控制，proxy_score 为 0.559，保护动作余量为 59 min；控制接入后暂存窗口从 35 min 增至 90 min，`release_policy` 为 `block_release_until_lab_and_field_conformal_calibration`。该层必须用现场 timestamped replay 验证 precision、recall、提前量和误触发成本后，才可写入保护性控制。

## 时间戳回放接口

| 内容 | 路径 |
| --- | --- |
| 时间戳回放 schema | `deliverables/timestamped_campaign_replay_schema.md` |
| Agent42 报告 | `outputs/agent42_timestamped_campaign_replay/agent42_report.md` |
| 时间戳回放 schema JSON | `outputs/timestamped_campaign_replay/timestamped_replay_schema.json` |
| 时间戳回放模板 | `outputs/timestamped_campaign_replay/templates/` |
| synthetic 时间戳样例包 | `outputs/timestamped_campaign_replay/synthetic_timestamped_replay/` |

当前 Agent42 判断：`synthetic_timestamp_schema_ready_needs_field_replay`。已把低成本传感、离线检测结果返回、控制动作生效和 fast_proxy_event_log 对齐到同一 batch 时间轴；synthetic 样例覆盖率为 1.0，快代理标签事件 12 个，接口可计算 precision、recall、protective action lead time、lab turnaround 和 actuator latency。该层当前只能证明 schema 和 replay 计算可运行，`can_calibrate_fast_proxy=False`、`can_write_to_protective_control=False`，必须导入真实 field-labeled timestamped replay 后才能写入保护性控制。

## 现场回放校准门控

| 内容 | 路径 |
| --- | --- |
| 现场回放校准门控 | `deliverables/field_replay_calibration_gate.md` |
| Agent43 报告 | `outputs/agent43_field_replay_calibration_gate/agent43_report.md` |
| G6/P6 指标 JSON | `outputs/field_replay_calibration_gate/g6_p6_gate_metrics.json` |

当前 Agent43 判断：`synthetic_replay_gate_blocked`。G6 已有 7/8 项在 synthetic 样例中可计算，但 `G6_1_field_origin` 未通过，因此 `can_write_to_protective_control=False`、`can_write_to_release_gate=False`。该层把 Agent42 的 replay 指标转成硬门控：只有真实 field-labeled replay 同时满足时间戳覆盖、batch 回连、proxy label 数、precision/recall、保护性提前量、执行器延迟和误触发成本阈值后，才允许写入 matrix_shock 保护性控制；自动放行门始终禁止。

## 现场 replay 包导入门

| 内容 | 路径 |
| --- | --- |
| 导入协议 | `deliverables/field_replay_import_protocol.md` |
| Agent44 报告 | `outputs/agent44_field_replay_import/agent44_report.md` |
| 导入验收指标 JSON | `outputs/field_replay_import/import_acceptance_metrics.json` |
| Preflight 指标 JSON | `outputs/field_replay_import/real_field_package_preflight_metrics.json` |
| 导入 schema JSON | `outputs/field_replay_import/import_schema.json` |
| 真实包模板 | `outputs/field_replay_import/real_field_package_template/` |
| synthetic 导入联调包 | `outputs/field_replay_import/synthetic_replay_import_package/` |
| R7 端到端管线 | `deliverables/model_core_optimization/r7_real_field_replay_pipeline.md` |
| R7 管线报告 | `outputs/r7_real_field_replay_pipeline/r7_real_field_replay_pipeline_report.md` |
| R7 管线指标 JSON | `outputs/r7_real_field_replay_pipeline/r7_real_field_replay_pipeline_metrics.json` |
| R7 submission 修复工单 JSON | `outputs/r7_real_field_replay_pipeline/field_package_submission_repair_work_order.json` |
| R7 submission 响应模板 JSON | `outputs/r7_real_field_replay_pipeline/field_package_submission_repair_response_template.json` |
| R7 submission 响应预检 JSON | `outputs/r7_real_field_replay_pipeline/field_package_submission_repair_response_preflight.json` |

当前 Agent44 判断：`field_replay_import_blocked_non_field_origin`，preflight 判断：`field_package_preflight_blocked_non_field_origin`。这表示四张 CSV 的字段、类型和 batch 回连可运行，但 metadata 的 `data_origin=synthetic` 被正确阻断；该层只允许真实 `field` 包进入 Agent42 timestamped replay，且自身永远不授权保护性控制写回。`real_field_package_template/` 是 header-only 采集模板，含 TODO provenance，不能作为 field evidence；模板已包含 R7j 采集骨架，但保持主 replay 宽表和节点级 holdout 证据分离：`sensor_timeseries.csv` 仍用于主 replay，只增加 `sensor_status/instrument_id/acquisition_time_min/ingest_time_min`；N3 床出口 UV254/ORP 与催化剂床压差进入 `node_modality_sensor_timeseries.csv`；`offline_lab_results.csv` 增加 `lab_label_time_min/detection_limit/method/unit`；`site_topology_or_bed_geometry.csv` 用于床体积/HRT/流量。模板专用 preflight 位于 `outputs/field_replay_import/real_field_package_template_preflight_metrics.json`，其中 R7j supplement header 已 ready。

当前 R7 端到端管线判断：`real_field_package_acceptance_blocked_at_import`，field package coverage 判断：`field_package_coverage_blocked_before_import`，minimum replay contract 判断：`minimum_replay_contract_blocked_missing_rows`，valid_matched_batch_count 为 0，valid_operation_action_count 为 0，valid_lab_result_count 为 0，valid_proxy_label_count 为 0，time_order_violation_count 为 0，patch plan 判断：`patch_plan_blocked_at_import_preflight`。当前 submission repair work order 判断：`field_package_submission_repair_work_order_blocked_at_import_preflight`，共 13 个修复项，把 R7A metadata/真实行补包、R7I 最小 replay 契约和 R8U66 path/endpoint 对齐缺口合并为可机读 operator work order；其中包括替换 `metadata.json` placeholder provenance，为 `campaign_operation_log`、`fast_proxy_event_log`、`offline_lab_results`、`pressure_headloss_event_log`、`sensor_timeseries` 添加真实 timestamped rows，并补齐 `site_topology_or_bed_geometry`、`node_modality_sensor_timeseries`、`hydraulic_path_stage_labels`、`final_effluent_endpoint_labels` 等路径/终点标签表。当前 submission repair response preflight 判断：`repair_response_preflight_blocked_at_template_markers`，template_marker_count=`13`、can_route_to_r7_preflight=`False`；这表示系统已生成 operator response 模板，但模板/TODO 响应不能进入 R7 preflight。若设置 `FIELD_PACKAGE_SUBMISSION_REPAIR_RESPONSE_PATH=/path/to/repair_response.json`，脚本会先检查 operator response 是否逐项填完、是否声明 field 来源、是否确认 no-write boundary；即便 response 通过，也只允许“重跑 R7/Agent44 preflight”，仍不能直接形成 field evidence。若设置 `REAL_FIELD_REPLAY_PACKAGE_DIR=/path/to/field_package`，脚本会把真实包送入 Agent44 preflight/import、Agent45 内部 Agent42/43 replay/G6，再进入 R7 acceptance gate，同时审计 package 是否覆盖 claim-specific 字段、soft holdout 弱目标标签，是否具备至少 3 个跨 replay 表对齐的共同 `batch_id`、至少 3 组同批次可执行且时间可解析的 operation action、QA 通过且数值可用的 offline lab 结果和可解析的 field-labeled fast proxy 事件，以及离线检测、执行器动作和 proxy 标签时间顺序是否有效；真实包通过 R7a 后，R7j 会继续检查 N3 床出口 UV254/ORP、催化剂床压降、床体积/HRT、再生事件和 `catalyst_activity` 标签是否在至少 3 个同批次 holdout 中对齐。若未设置真实包，则只用 header-only template 做 preflight 演练，不产生 field evidence。

## 现场 replay 证据链

| 内容 | 路径 |
| --- | --- |
| 证据链报告 | `deliverables/field_replay_evidence_chain.md` |
| Agent45 报告 | `outputs/agent45_field_replay_evidence_chain/agent45_report.md` |
| 证据链指标 JSON | `outputs/field_replay_evidence_chain/evidence_chain_metrics.json` |

当前 Agent45 判断：`field_replay_evidence_chain_blocked_at_import`。这表示 synthetic 包没有通过 Agent44，因此 Agent45 不运行 Agent42/Agent43 downstream，也不会产生保护性写回候选；真实包通过后，仍只形成人工复核前的保护性控制候选，自动放行门保持禁止。

## 软传感 field holdout 放行门控

| 内容 | 路径 |
| --- | --- |
| 放行门控报告 | `deliverables/soft_sensor_field_holdout_gate.md` |
| Agent46 报告 | `outputs/agent46_soft_sensor_field_holdout_gate/agent46_report.md` |
| field holdout gate 指标 JSON | `outputs/soft_sensor_field_holdout_gate/field_holdout_gate_metrics.json` |

当前 Agent46 判断：`soft_sensor_release_gate_blocked_non_field_holdout`。这表示 Agent36/Agent39 的 synthetic holdout 指标只能证明接口可运行，不能写入 release gate；只有真实 field holdout 同时满足覆盖率、区间宽度、OOD/abstention、弱目标覆盖和场景多样性门控后，才形成软传感 release gate 校准候选，且仍不能直接授权自动放行。

## 弱目标分层保形校准

| 内容 | 路径 |
| --- | --- |
| 弱目标分层报告 | `deliverables/weak_target_stratified_conformal.md` |
| Agent47 报告 | `outputs/agent47_weak_target_stratified_conformal/agent47_report.md` |
| 弱目标分层指标 JSON | `outputs/weak_target_stratified_conformal/weak_target_stratified_metrics.json` |

当前 Agent47 判断：`weak_target_stratified_synthetic_candidate_needs_field_holdout`。最弱目标是 `matrix_interference`，coverage 为 0.875；这说明总体 conformal coverage 0.975 不能替代弱目标分层 coverage。Agent47 只能生成 diagnostic candidate，必须用真实 field holdout 复核后再交给 Agent46。

## 管网布点与稀疏感知

| 内容 | 路径 |
| --- | --- |
| 管网布点报告 | `deliverables/sensor_network_sparse_placement.md` |
| Agent48 报告 | `outputs/agent48_sensor_network_sparse_placement/agent48_report.md` |
| 稀疏布点指标 JSON | `outputs/sensor_network_sparse_placement/sparse_placement_metrics.json` |

当前 Agent48 判断：`sparse_sensor_layout_ready_needs_field_topology`。它已生成 6x10 node-modality 观测矩阵，并比较 greedy、deterministic random、cost-only、reconstruction QR proxy、classification SSPOC proxy 和 topology robust cost proxy 六类布点策略；当前选中 `greedy_marginal`，comparable_score 为 0.726，best_vs_random_delta=0.062，best_vs_cost_only_delta=0.258。但 weak_state_coverage 只有 0.300，说明常规低成本水质传感对 `catalyst_activity` 直接观测不足，下一步需要催化剂床前后差分、UV254/ORP/浊度/压降等代理观测和真实节点级标签。

## 多设施协同控制

| 内容 | 路径 |
| --- | --- |
| 多设施协同控制报告 | `deliverables/multi_facility_collaborative_control.md` |
| Agent49 报告 | `outputs/agent49_multi_facility_collaborative_control/agent49_report.md` |
| 协同控制指标 JSON | `outputs/multi_facility_collaborative_control/collaborative_control_metrics.json` |

当前 Agent49 判断：`synthetic_collaborative_policy_needs_field_replay`。它把 Agent48 的 node-modality 观测矩阵接入均质池、反应核心、催化剂床、回流环和末端精处理 5 个 facility agent，生成 5 个候选联动动作，并用 ID3 风格决策树蒸馏策略；当前蒸馏准确度代理值为 0.790，说明它能作为解释草案，但必须有真实多节点 sensor/lab/operation/action replay 后才能进入执行器候选。

Agent48 现在不只输出 coverage 和候选布点，还输出稀疏观测矩阵诊断：当前 selected matrix rank 为 6，axis_span_rank_ratio 为 0.667，condition_number_proxy 为 61.726，reconstruction_stability_score 为 0.401，weak_axis_gap_count 为 2。最关键缺口仍是 `catalyst_activity_observability`：当前覆盖 0.300，目标 0.550，候选池最佳 `N3_catalyst_bed_outlet:UV254_abs` 也只有 0.404，说明这个弱状态不能只靠现有低成本模态自然补足，后续必须依赖 Agent51 catalyst proxy、真实 field topology benchmark 或新增催化剂生命周期标签。

Agent51 已把这个弱轴诊断转成 `weak_axis_repair_plan`：repair_status=`agent48_catalyst_axis_requires_proxy_patch_and_field_label`，repair_score=0.983，优先级最高的修复信号是 `N3_catalyst_bed_outlet:UV254_abs`，随后是床出口 ORP 和催化剂床压降。R2 observation contract 已消费该计划，推荐的 budget-rebalanced contract 加入床出口 UV254/ORP、移除低边际末端浊度，使 weak_state_coverage 达到 0.580 且预算通过。Agent49 也已消费该修复先验，但报告中保留 `catalyst_axis_repair_prior_not_field_validated`：没有 field_proxy_labels 前，不能解除催化剂保护规则。R7 coverage 现在新增 `R7j_agent51_catalyst_proxy_holdout_contract`，会显式检查真实包中是否存在 N3 节点级 UV254/ORP/压降、床体积/HRT、再生事件和 QA 通过的 catalyst_activity 标签，并要求至少 3 个同批次 matched holdout。

## 模型核心优化治理

| 内容 | 路径 |
| --- | --- |
| 模型核心 goal | `deliverables/model_core_optimization/model_core_goal.md` |
| 用户打断约束 | `deliverables/model_core_optimization/user_interrupt_lessons.md` |
| 外部 evidence matrix | `deliverables/model_core_optimization/external_evidence_matrix.md` |
| 问题优先级排序 | `deliverables/model_core_optimization/issue_priority_ranking.md` |
| 后续执行 prompt | `deliverables/model_core_optimization/execution_prompt.md` |
| 自我打断 checklist | `deliverables/model_core_optimization/self_interrupt_checklist.md` |
| 治理报告 | `deliverables/model_core_optimization/governance_report.md` |
| Agent50 报告 | `outputs/agent50_model_core_governance/agent50_report.md` |
| 优先级 JSON | `outputs/model_core_governance/priority_ranking.json` |
| 量化阶段门 JSON | `outputs/model_core_governance/core_score_termination_gate.json` |
| 外部激活合同 JSON | `outputs/model_core_governance/external_activation_contract.json` |
| 外部激活 router JSON | `outputs/model_core_governance/external_activation_router.json` |
| 外部激活 router 报告 | `deliverables/model_core_optimization/external_activation_router.md` |
| 隐藏状态级 field activation matrix | `outputs/model_core_governance/field_activation_matrix.json` |
| field activation matrix 说明 | `deliverables/model_core_optimization/field_activation_matrix.md` |
| field activation response template | `outputs/model_core_governance/field_activation_response_template.json` |
| field activation response source preflight | `outputs/model_core_governance/field_activation_response_source_preflight.json` |
| field activation response repair work order | `outputs/model_core_governance/field_activation_response_repair_work_order.json` |
| field activation response preflight | `outputs/model_core_governance/field_activation_response_preflight.json` |
| field activation response completion ledger | `outputs/model_core_governance/field_activation_response_completion_ledger.json` |
| field activation response focus handoff | `outputs/model_core_governance/field_activation_response_focus_handoff.json` |
| focused catalyst response source preflight | `outputs/focused_catalyst_response_merge/focused_catalyst_response_source_preflight.json` |
| focused catalyst response repair work order | `outputs/focused_catalyst_response_merge/focused_catalyst_response_repair_work_order.json` |
| field activation response coherence audit | `outputs/model_core_governance/field_activation_response_coherence_audit.json` |
| field activation package assembly plan | `outputs/model_core_governance/field_activation_package_assembly_plan.json` |
| field activation package staging manifest | `outputs/model_core_governance/field_activation_package_staging_manifest.json` |
| field activation materialized package preflight | `outputs/model_core_governance/field_activation_materialized_package_preflight.json` |
| field activation downstream R7 preview | `outputs/model_core_governance/field_activation_downstream_r7_preview.json` |
| field activation downstream path/endpoint preview | `outputs/model_core_governance/field_activation_downstream_path_endpoint_preview.json` |
| field activation external readiness gate | `outputs/model_core_governance/field_activation_external_readiness_gate.json` |
| field activation schema contract | `outputs/model_core_governance/field_activation_schema_contract.json` |
| field activation schema preflight | `outputs/model_core_governance/field_activation_schema_preflight.json` |
| R7 真实现场包验收 | `deliverables/model_core_optimization/real_field_package_acceptance_gate.md` |

当前 Agent50 阶段判定仍是 `stop_expansion_wait_for_real_field_package_or_new_core_interface`；自我打断结论仍是 `stage_boundary_wait_for_external_activation`。这不是展示偏移触发的 hard interrupt，也不是允许继续堆叠内部模型，而是阶段边界等待外部激活。`core_score_termination_gate.json` 已直接暴露 `effective_iteration_gate`、`next_allowed_actions` 与 `external_resume_conditions`：当前 `previous_core_score=0.960`、`core_score=0.960`、`iteration_delta=0.000`、`score_delta_pass=False`、`stage_boundary_termination_pass=True`、`validity_basis=stage_boundary_external_wait_not_score_gain`，说明有效性来自阶段终止和新接口证据链，而非分数增益。允许动作是提交 `REAL_FIELD_REPLAY_PACKAGE_DIR`、提交 `FIELD_PATH_ENDPOINT_LABEL_PACKAGE_DIR`、提交 `FORMAL_SEARCH_RESULT_PACKAGE_PATH`，或使用新的可测试核心接口。

R8u97-R8u125 已把 field activation 链条拆成可机读合同：6/6 个隐藏状态矩阵、33 行响应模板、assembly plan、schema preflight、repair work order、staging manifest、materialized package preflight，以及 `catalyst_activity` focused handoff。当前 focused catalyst response 仍未由真实外部证据填写，`response_source_preflight_status=field_activation_response_source_using_default_template`，`repair_item_count=7`，最高优先修复项仍是 `R8U102_SUBMIT_FIELD_ACTIVATION_RESPONSE`。因此该链条仍只能帮助采集和预检真实证据，不能恢复 field replay/control，不能写 actuator，不能写 release gate。

R8u133 已补充 `FORMAL_SEARCH_RESULT_PACKAGE_PATH` 通道的 preliminary formal search result package。设置该路径后，当前 router 为 `external_activation_router_has_handoff_ready_routes`，`handoff_ready_route_count=1`，`handoff_ready_channel_ids=[R8U79_FORMAL_SEARCH_RESULT_PACKAGE]`，但 `model_chain_ready_route_count=0`。这表示 formal search 结果包已经通过 Agent60 source/row/validation execution，可进入人工非法律技术比较；它不等于真实现场包，不等于法律意见，不允许生成权利要求文本，也不能让现场模型链恢复执行。R7 真实包仍必须走 Agent44 field replay package preflight，path/endpoint 包仍必须走 Agent54 path label preflight，formal search result 包仍只走 Agent60 的 source/row/human-review 链。当前系统仍缺 field holdout/replay 和真实现场包，不能写入执行器、release gate、法律结论或 field-supported claim。

R8u106 已补齐 field activation 外部接入顺序门：当前 `field_activation_external_readiness_gate_status=field_activation_external_readiness_waiting_for_external_response`，第一阻断是 `response_source`，最高阻断是 `R8U106_SUBMIT_FIELD_ACTIVATION_RESPONSE`，下一步是先设置 `FIELD_ACTIVATION_RESPONSE_PATH`，而不是直接设置 `REAL_FIELD_REPLAY_PACKAGE_DIR`。只有 response/source/schema/repair/assembly/staging/materialized package 全部通过后，才允许进入 external activation router；即便如此也仍不代表 field replay、actuator 或 release gate ready。

R8u107/R8u108 已把 Agent50 顶层推荐对齐到 field activation 顺序门和 submission packet；R8u124/R8u125 又进一步把 submission packet 拆细为 completion ledger 与 focused handoff，R8u126/R8u127 则把 focused catalyst response 的 source preflight 和 repair work order 固化，R8u128 已把 repair work order 的动作回接到 focus handoff 与 external router，R8u129 进一步把同一 repair handoff 暴露到 `core_score_termination_gate.json` 的 `next_allowed_actions.NEW_CORE_INTERFACE` 与 `external_resume_conditions.new_core_interface`，R8u130 则把当前外部激活动作压成 `outputs/model_core_governance/external_activation_operator_action_packet.json`，R8u131 已让 Agent50 消费该 packet，R8u132 又把该 packet 直接暴露到 `core_score_termination_gate.json` 的 `NEW_CORE_INTERFACE` allowed action 和 `external_resume_conditions.new_core_interface`。当前 `latest_agent50_recommended_next_core_action=FIELD_ACTIVATION_RESPONSE_FOCUS_HANDOFF_NEXT_ACTION`，`latest_agent50_field_activation_response_focus_handoff_status=field_activation_response_focus_handoff_ready_for_catalyst_activity`，`latest_agent50_focused_catalyst_response_repair_work_order_status=focused_catalyst_response_repair_work_order_waiting_for_external_response`，`latest_agent50_external_activation_operator_action_packet_status=operator_packet_waiting_for_focused_catalyst_response`，下一步优先填写 6 行 focused catalyst response，设置 `FOCUSED_CATALYST_RESPONSE_PATH` 并运行 `experiments/run_focused_catalyst_response_merge.py`。如果 source/row/batch 被阻断，focus handoff/router/core gate/operator packet 会优先采用 `focused_catalyst_response_repair_work_order.json` 中的具体修复动作；如果 merge 预检通过，再把合并候选作为 `FIELD_ACTIVATION_RESPONSE_PATH` 重跑 field activation 和 Agent50。这仍只是外部响应提交路径优化，不能替代完整 response/package/router、field replay/holdout 或人工复核。

R8u115 已把 R8u114 的 catalyst slice -> R7 patch candidate 状态接入 external activation router 与 Agent50。当前 `external_activation_router.json` 顶层和 R7 route row 都显示 `catalyst_patch_candidate_status=catalyst_slice_r7_patch_waiting_for_valid_catalyst_slice`、`catalyst_patch_candidate_can_submit_as_REAL_FIELD_REPLAY_PACKAGE_DIR=False`，说明还没有真实 catalyst 四表切片可作为 R7 候选包提交。未来如果 R8u114 的 candidate 通过 full R7 preflight，router 可以提示 `set_REAL_FIELD_REPLAY_PACKAGE_DIR_to_catalyst_patch_candidate`，但仍不会直接把 route 标记 ready；operator 必须显式设置 `REAL_FIELD_REPLAY_PACKAGE_DIR` 并让完整 R7 preflight 通过后，模型链才可能恢复。该回接只减少真实包提交摩擦，不生成 field evidence、不运行 Agent51 holdout、不解除 Agent49 guardrail、不写 actuator/release gate。

R8u116 已把 field activation external readiness gate 和 field activation response submission packet 接入 external activation router；R8u125 又把 focus handoff 接入 router。当前 R7 route row 显示 `field_activation_upstream_status=field_activation_external_readiness_waiting_for_external_response`、`field_activation_upstream_first_blocked_step=response_source`、`field_activation_upstream_highest_priority_blocker=R8U106_SUBMIT_FIELD_ACTIVATION_RESPONSE`、`field_activation_upstream_focus_handoff_status=field_activation_response_focus_handoff_ready_for_catalyst_activity`，所以 router 顶层下一步已经切换为 `fill_focused_catalyst_response_template_then_set_FOCUSED_CATALYST_RESPONSE_PATH_and_merge_to_FIELD_ACTIVATION_RESPONSE_PATH`。这修正了 R8u115 后 router 与 Agent50 推荐之间的顺序不一致：没有真实 R7 路径、没有可提交 catalyst R7 candidate 时，应先补状态级 response；当 focused catalyst handoff ready 时，应先走 6 行小包，而不是直接设置 R7 目录或回到 full 33 行扫描。该回接仍不生成 field evidence，也不让任何 route ready。

R8u117 已把 field activation response coherence audit 接入 response -> package assembly -> repair work order -> external readiness gate -> Agent50 scorecard。当前默认无外部响应时，`field_activation_response_coherence_audit_status=field_activation_response_coherence_audit_waiting_for_response_preflight`，这是正确阻断；如果后续提交的 response 虽通过行级 preflight，但同一 hidden state 的 batch 无法对齐、sensor/operation 行缺 timestamp/node/sensor、offline lab 行缺 method/detection limit，则 package assembly 会停在 `field_activation_package_assembly_plan_blocked_by_response_coherence_audit`。该 audit 只验证工程可拼接性和可回放性，不把 response 升级为 field evidence。

R8u118 已修正 R8u117 的等待态归因：在 `response_preflight` 未 ready 前，coherence audit 不再把模板行缺口计入 hard blockers，而是输出 `audit_execution_status=coherence_checks_deferred_until_response_preflight_ready`、`hard_blocker_count=0`。这保证第一阻断仍清楚地指向 `FIELD_ACTIVATION_RESPONSE_PATH` 外部响应提交，而不是把模板 TODO 误报为 coherence 审计失败。

R8u119 已把 field activation response 的“值本体”纳入机器合同：每一行现在必须同时具备 `evidence_value_reference` 和 `evidence_value`，前者用于追溯来源，后者用于提供 measured value、label、event flag 或 JSON payload。当前默认模板 `response_missing_value_payload_row_count=0`、`response_template_value_payload_row_count=33`，repair work order 为 7 项，说明 33 行都还只是模板值；如果只填引用不填 `evidence_value`，response preflight 会阻断。该门控只保证可进入后续 package/replay 的值 payload 形态，不证明现场数据真实有效。

R8u120 已把 `evidence_value` 推进到外部包物化层：当 response 和 assembly ready 后，staging manifest 会生成 `row_blueprints` 与 `value_payload_mappings`，明确每个 response payload 应进入哪张 CSV、哪一行、哪一列；materialized package preflight 会检查 operator 写出的 CSV 是否匹配这些蓝图，缺失时触发 `R8U105_TABLE_BLUEPRINT_ROWS_MISSING`。当前默认未提交外部 response，`package_staging_selected_row_blueprint_count=0`、`package_staging_selected_value_payload_mapping_count=0`，这是正确等待态。该层仍然不生成 field evidence，只减少 response 到 CSV package 的工程断链风险。

R8u121 已把 R8u105 之后的下游 R7/Agent44 导入门做成 no-write preview：当 materialized package preflight ready 后，系统会只读调用 R7 field replay package preflight，提前暴露缺表、真实行、类型转换、必需字段或 batch linkage 阻断。当前默认仍未提交外部 response，所以 preview 状态为 `field_activation_downstream_r7_preview_blocked_by_materialized_package_preflight`、`preview_executed=False`；测试中的 ready materialized package 会执行 preview 并证明 R8u105 通过不等于 R7/Agent44 可进入 timestamped replay。该层仍不恢复模型链、不运行 replay/holdout、不写 actuator/release gate。

R8u122 已把同一 materialized package 到 R8u66/Agent54 path-endpoint label gate 的下游预检补上：当 R8u105 ready 后，系统会只读调用 path/endpoint label preflight，提前暴露路径阶段标签、最终出水终点标签、共同 batch、operation log、offline lab rows 和 release gate endpoint 证据缺口。当前默认状态为 `field_activation_downstream_path_endpoint_preview_blocked_by_materialized_package_preflight`、`preview_executed=False`；测试中的 ready materialized package 会执行 preview 并证明 R8u105 通过不等于 field layout holdout ready。该层仍不恢复模型链、不运行 layout holdout/replay、不写 actuator/release gate。

R8u123 已修正 downstream preview 未执行时的指标语义：R7 preview 与 path/endpoint preview 现在都会输出 `preview_metric_evaluation_status=deferred_until_materialized_package_preflight_ready` 和 `not_evaluated_metric_names`，明确这些 count=0 不是“下游无缺口”，而是“下游预检尚未运行”。path/endpoint preview 还在默认等待态暴露合同门槛：6 张必需表、至少 5 个共同 batch。该层只增强证据边界解释，不新增 field evidence。

R8u124 已把 `FIELD_ACTIVATION_RESPONSE_PATH` 的 33 行外部响应填写状态压成可计算 completion ledger：新增 `outputs/model_core_governance/field_activation_response_completion_ledger.json`，按响应行、hidden_state 和 table 汇总 completion ratio、issue scopes、completed/incomplete rows、next hidden-state focus 和 next action。当前默认无外部响应时，ledger 明确显示 `completion_ratio=0.0`、`completed_response_row_count=0`、`next_hidden_state_focus=catalyst_activity`，防止把模板行误解为现场证据。Agent50、manifest 与 field activation Markdown 已消费该账本；该层只减少真实响应包提交和预检摩擦，不生成 field evidence、不运行 replay/holdout、不写 actuator 或 release gate。

## 可推理 KG、主链回接与现场验证队列

| 内容 | 路径 |
| --- | --- |
| 可推理 KG 报告 | `deliverables/knowledge_graph_reasoning.md` |
| 主链回接审计 | `deliverables/main_chain_reconnection.md` |
| 现场验证队列对齐 | `deliverables/field_validation_queue_alignment.md` |
| claim-specific 采集包 | `deliverables/claim_specific_field_package.md` |

当前 Agent56 判断：`kg_reasoning_patch_ready_needs_field_supported_edges`；Agent57 判断：`synthetic_main_chain_reconnection_ready_needs_field_replay`；Agent58 判断：`field_validation_alignment_ready_needs_real_field_package`；Agent59 判断：`claim_specific_package_ready_needs_real_data_and_source_basis_detail`。这条链把“知识库结论 -> 主链消费 -> 需要哪些现场字段/gate -> 每条 claim 的必采字段和 source_basis 补全”串起来，但仍不能替代真实 field validation。

## 催化剂活性代理观测

| 内容 | 路径 |
| --- | --- |
| 代理观测报告 | `deliverables/catalyst_activity_proxy.md` |
| Agent51 报告 | `outputs/agent51_catalyst_activity_proxy/agent51_report.md` |
| 代理指标 JSON | `outputs/catalyst_activity_proxy/catalyst_activity_proxy_metrics.json` |

当前 Agent51 判断：`synthetic_catalyst_proxy_design_ready_needs_field_labels`。它把不可直接在线观测的 `catalyst_activity` 拆成床前后 UV254 去除率、ORP 衰减、浊度/压降污堵、再生响应增益和停留时间归一化速率残差；当前代理观测从 0.331 提升到补点设计后的 0.720，weak_state_coverage_after_proxy_design 为 0.720。该结果只能写回为 Agent48/49 设计先验；没有 field_proxy_holdout 前，不能解除 Agent49 的催化剂不确定性保护规则，也不能写执行器或 release gate。

## 多设施 Replay 离线评估

| 内容 | 路径 |
| --- | --- |
| Replay 离线评估报告 | `deliverables/multi_facility_replay_evaluation.md` |
| Agent52 报告 | `outputs/agent52_multi_facility_replay_evaluation/agent52_report.md` |
| Replay 指标 JSON | `outputs/multi_facility_replay_evaluation/replay_evaluation_metrics.json` |

当前 Agent52 判断：`synthetic_replay_evaluation_ready_needs_field_replay`。它把 Agent49 的多设施协同控制候选转成可回放的 state-action-reward 评估合同，输出 replay schema、synthetic replay table、joint_action_accuracy、mean_reward_regret、保护性误触发成本和决策树蒸馏回放准确率。当前 synthetic joint_action_accuracy 为 0.667，mean_reward_regret 为 0.055，`R2_catalyst_uncertain_low_proxy` 的保护性误触发成本为 0.18；该层只能写回 reward prior、replay schema 和 offline metric contract，不能写执行器、release gate 或 online MARL。

## 最小灰箱物理机制

| 内容 | 路径 |
| --- | --- |
| 最小灰箱物理报告 | `deliverables/minimal_grey_box_physics.md` |
| Agent53 报告 | `outputs/agent53_minimal_grey_box_physics/agent53_report.md` |
| 灰箱物理指标 JSON | `outputs/minimal_grey_box_physics/grey_box_physics_metrics.json` |

当前 Agent53 判断：`synthetic_grey_box_physics_prior_ready_needs_field_calibration`。它把停留时间分布、旁路/短流、拟一级反应、基质抑制、催化剂有效活性、氧化剂消耗、质量守恒和副产物风险写成最小 physics prior。修正后的 synthetic mean_grey_box_residual 为 0.131，max_mass_balance_residual 为 0.000，仍在 `reaction_time_insufficient`、`catalyst_deactivation` 和 `matrix_shock` 场景保留物理审计信号。该层只能写回 soft_sensor_physics_prior、Agent49 reward residual candidate 和 P4 completion status，不能写执行器、release gate 或现场机理结论。

## 工程执行约束

| 内容 | 路径 |
| --- | --- |
| 工程执行约束报告 | `deliverables/engineering_execution_constraints.md` |
| Agent55 报告 | `outputs/agent55_engineering_execution_constraints/agent55_report.md` |
| 工程约束指标 JSON | `outputs/engineering_execution_constraints/engineering_constraints_metrics.json` |
| Agent49 约束补丁后摘要 | `outputs/agent55_engineering_execution_constraints/agent49_engineering_patched_report.md` |

当前 Agent55 判断：`synthetic_engineering_constraints_reward_patch_ready_needs_plc_scada_and_field_replay`。它把池容、泵阀动作次数、执行器延迟、药剂库存、维护窗口、人工复核和误动作成本转成 Agent49 reward patch 与 Arbitration action patch。当前 mean_execution_feasibility 为 0.980，hard_blocked_joint_action_count 为 1，主要触发项是 `J2_catalyst_protection_before_regeneration` 的维护窗口压力；该层只能改变候选排序和人工复核边界，没有 PLC/SCADA 点表、SOP 和 field execution replay 前，不能写执行器或 release gate。

## 当前验证

```bash
.venv/bin/pytest -q
```

当前完整回归结果：`616 passed`。

## 推荐阅读顺序

1. `docs/project_overview_28_agent.md`
2. `docs/agent_system_spec.md`
3. `outputs/agent29_project_synthesis/agent29_report.md`
4. `docs/field_data_interface_spec.md`
5. `outputs/agent30_field_data_interface/agent30_report.md`
6. `deliverables/presentation_outline.md`
7. `deliverables/key_metrics_table.md`
8. `deliverables/visual_storyboard.md`
9. `deliverables/figure_specs.md`
10. `deliverables/field_calibration_protocol.md`
11. `deliverables/field_data_acceptance_gates.md`
12. `deliverables/field_calibration_runbook.md`
13. `deliverables/model_realism_audit.md`
14. `deliverables/model_upgrade_backlog.md`
15. `deliverables/soft_sensor_uncertainty_validation.md`
16. `deliverables/knowledge_graph_curation.md`
17. `deliverables/knowledge_graph_schema.md`
18. `deliverables/literature_evidence_matrix.md`
19. `deliverables/literature_evidence_schema.md`
20. `deliverables/soft_sensor_conformal_calibration.md`
21. `deliverables/grey_box_dynamic_latency.md`
22. `deliverables/matrix_shock_fast_proxy_control.md`
23. `deliverables/timestamped_campaign_replay_schema.md`
24. `deliverables/field_replay_calibration_gate.md`
25. `deliverables/field_replay_import_protocol.md`
26. `deliverables/field_replay_evidence_chain.md`
27. `deliverables/soft_sensor_field_holdout_gate.md`
28. `deliverables/weak_target_stratified_conformal.md`
29. `deliverables/sensor_network_sparse_placement.md`
30. `deliverables/multi_facility_collaborative_control.md`
31. `deliverables/model_core_optimization/governance_report.md`
32. `deliverables/catalyst_activity_proxy.md`
33. `deliverables/multi_facility_replay_evaluation.md`
34. `deliverables/minimal_grey_box_physics.md`
35. `deliverables/model_core_optimization/issue_priority_ranking.md`
36. `notes/current_status.md`

## 下一步

正式 PPTX 已冻结为 Agent33 快照。当前进入模型核心优化阶段后，Agent56-59 已完成本轮复盘承接：KG reasoning、主链回接、现场验证队列对齐和 claim-specific 采集包矩阵。R1/R1b 已完成统一 evidence gate 与 source_basis detail library，R2 已完成 layout-aware observation contract，R3/R3b/R3c 已完成 counterfactual control replay stress、Agent49 reward prior guardrails 和 Agent52 guardrail-aware replay；R4/R4b/R5/R6 已完成 control guardrail backpropagation、patch consumption、schema 覆盖和 source_basis detail 接入。R7 当前已把真实现场验收拆成 8 个阶段并阻断在导入层，其中 R7S4b 会检查 Agent49/52 多设施控制晋级与 Agent51 催化剂代理 holdout；Agent60 已把 R7 pipeline coverage 纳入 `ranked_refactor_actions`，当前进入 `R7a_import_real_field_package_with_metadata_and_csv`，后续会按真实包覆盖、控制晋级、弱目标标签、最小共同批次、operation action 质量、lab/proxy 标签质量和时间顺序缺口切换。没有真实 field package 时，Agent60 会启用离线核心 fallback `R8b_agent48_pressure_headloss_candidate_pool_design`。所有 synthetic 结果只作为仿真或接口基线，不能替代 field validation。
