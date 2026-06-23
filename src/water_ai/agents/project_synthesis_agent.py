from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class ProjectSynthesisAgent(BaseAgent):
    """Summarize the multi-agent prototype as a project-level research platform."""

    name = "project_synthesis_agent"

    def __init__(
        self,
        *,
        synthesized_agent_count: int = 28,
        latest_control_metrics: dict[str, object] | None = None,
        milestone_reports: dict[str, object] | None = None,
        artifact_paths: dict[str, str] | None = None,
        latest_regression: str = "unknown",
    ) -> None:
        self.synthesized_agent_count = synthesized_agent_count
        self.latest_control_metrics = latest_control_metrics or {}
        self.milestone_reports = milestone_reports or {}
        self.artifact_paths = artifact_paths or {}
        self.latest_regression = latest_regression

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        latest_state = self._latest_control_state()
        module_groups = self._module_groups()
        evidence_chain = self._evidence_chain(latest_state)
        readiness = self._readiness_assessment(latest_state, evidence_chain)
        calibration_roadmap = self._calibration_roadmap()
        deliverables = self._deliverables()
        issues = self._issues(readiness)
        recommendations = self._recommendations(readiness)
        summary = (
            f"项目综合总览：已综合 {self.synthesized_agent_count} 个执行 agent；"
            f"当前成熟度为 {readiness['maturity_level']}，下一轮应进入真实数据校准。"
        )
        confidence = round(
            min(
                0.92,
                max(
                    0.42,
                    0.62
                    + 0.08 * bool(readiness["prototype_chain_complete"])
                    + 0.05 * bool(readiness["latest_control_stable"])
                    + 0.03 * bool("passed" in self.latest_regression),
                ),
            ),
            3,
        )

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "synthesized_agent_count": self.synthesized_agent_count,
                "module_groups": module_groups,
                "evidence_chain": evidence_chain,
                "readiness_assessment": readiness,
                "calibration_roadmap": calibration_roadmap,
                "project_mermaid": self._project_mermaid(),
                "deliverables": deliverables,
                "latest_control_state": latest_state,
                "latest_regression": self.latest_regression,
            },
        )

    def _latest_control_state(self) -> dict[str, object]:
        latest = self.latest_control_metrics.get("adjusted_control_state", {})
        if isinstance(latest, dict):
            state = deepcopy(latest)
        else:
            state = {}
        update = self.latest_control_metrics.get("recovery_campaign_update", {})
        if isinstance(update, dict):
            state.setdefault("acceptance_passed", update.get("acceptance_passed"))
            state.setdefault("validation_staff_usage", update.get("validation_staff_usage"))
            state.setdefault("time_budget_usage", update.get("time_budget_usage"))
            state.setdefault("bottleneck_ids", update.get("bottleneck_ids", []))
        return state

    @staticmethod
    def _module_groups() -> list[dict[str, object]]:
        return [
            {
                "group_id": "G1",
                "agent_range": "1-2",
                "title": "低成本感知与灰箱状态估计",
                "agents": ["DataQualityAgent", "SoftSensorAgent"],
                "research_role": "把低成本传感流转换为可用于控制的隐藏过程状态。",
                "core_outputs": ["sensor_confidence", "soft_state", "hydraulic_confidence", "release_readiness"],
            },
            {
                "group_id": "G2",
                "agent_range": "3-4",
                "title": "机理解释与故障诊断",
                "agents": ["MechanismAgent", "FaultDiagnosisAgent"],
                "research_role": "把软传感状态解释为污染物、材料和过程故障机制。",
                "core_outputs": ["mechanism_hypotheses", "fault_modes", "knowledge_matches"],
            },
            {
                "group_id": "G3",
                "agent_range": "5-10",
                "title": "动作生成、成本安全与闭环仲裁",
                "agents": [
                    "CatalystLifecycleAgent",
                    "ValidationPlanningAgent",
                    "ControlStrategyAgent",
                    "StrategyProfileAgent",
                    "CostSafetyAgent",
                    "ArbitrationAgent",
                ],
                "research_role": "把诊断结论转化为回流、暂存、加药、再生、更换、放行等可执行动作。",
                "core_outputs": ["control_actions", "objective_score", "final_action", "safety_gates"],
            },
            {
                "group_id": "G4",
                "agent_range": "11-13",
                "title": "传感配置、慢证据窗口与批次队列",
                "agents": ["SensitivityAnalysisAgent", "OperationsSchedulingAgent", "QueuePlanningAgent"],
                "research_role": "检验低成本传感是否能靠循环窗口和队列组织变得可执行。",
                "core_outputs": ["sensor_design_rankings", "campaign_bottlenecks", "queue_policy"],
            },
            {
                "group_id": "G5",
                "agent_range": "14-18",
                "title": "资源扩容、长期经济性与实施韧性",
                "agents": [
                    "ResourceExpansionAgent",
                    "LongTermEconomicsAgent",
                    "PhasedImplementationAgent",
                    "ImplementationStressTestAgent",
                    "AdaptivePortfolioAgent",
                ],
                "research_role": "把运行瓶颈转成资源建设、预算释放和备用项目包。",
                "core_outputs": ["selected_intervention", "selected_program", "phase_plan", "selected_portfolio"],
            },
            {
                "group_id": "G6",
                "agent_range": "19-23",
                "title": "在线项目控制、遥测接入与自动重规划",
                "agents": [
                    "OnlineProjectControlAgent",
                    "CampaignTelemetryAgent",
                    "ReplanningOrchestratorAgent",
                    "ControlBaselineUpdateAgent",
                    "PostReplanReplayAgent",
                ],
                "research_role": "把真实 campaign 遥测接回项目控制，并自动重跑规划链与写回基线。",
                "core_outputs": ["rolling_control_state", "replan_trace", "updated_baseline", "post_replan_replay"],
            },
            {
                "group_id": "G7",
                "agent_range": "24-28",
                "title": "恢复放量、时间预算修复与恢复在线控制",
                "agents": [
                    "RecoveryRampAgent",
                    "TimeBudgetRecoveryAgent",
                    "RecoveryStrategyWritebackAgent",
                    "RecoveryExecutionReplayAgent",
                    "RecoveryOnlineControlAgent",
                ],
                "research_role": "把保护性限流后的恢复负荷做成带回退线的条件恢复闭环。",
                "core_outputs": ["safe_ramp_fraction", "recovery_policy", "execution_replay", "fallback_rule"],
            },
        ]

    def _evidence_chain(self, latest_state: dict[str, object]) -> list[dict[str, object]]:
        agent23 = self._report_metrics("agent23")
        agent25 = self._report_metrics("agent25")
        agent27 = self._report_metrics("agent27")
        bottlenecks = latest_state.get("bottleneck_ids", [])
        return [
            {
                "step": "problem_framing",
                "claim": "低成本传感不是直接替代高端仪器，而是通过循环、暂存和慢证据窗口把黑箱过程变成可推断灰箱。",
                "evidence": "Agent1-11 已形成传感质控、软传感估计、机理解释、动作仲裁和传感配置敏感性分析。",
            },
            {
                "step": "campaign_bottleneck_discovery",
                "claim": "单批次闭环可行不等于多批次运行可行，真实瓶颈会出现在验证工时、总时间窗口和催化剂库存。",
                "evidence": "Agent12-13 识别验证容量、campaign 时间预算和催化剂库存瓶颈，仅靠队列排序不能完全解除。",
            },
            {
                "step": "resource_replanning",
                "claim": "系统需要能把瓶颈转化为资源、预算和实施阶段，而不是停留在控制动作层。",
                "evidence": "Agent14-23 完成资源扩容、长期经济性、分阶段实施、压力测试、项目组合、在线重规划和基线写回。",
                "metrics": self._post_replan_metrics(agent23),
            },
            {
                "step": "conditional_recovery",
                "claim": "循环结构可以降低传感与反应速度要求，但恢复负荷必须被时间预算和回退线约束。",
                "evidence": "Agent24 发现 0.75 会触发时间预算瓶颈，Agent25 通过验证错峰使 0.75 条件恢复可行。",
                "metrics": self._time_budget_metrics(agent25),
            },
            {
                "step": "execution_validation",
                "claim": "恢复策略需要执行回放验证，不能只写在报告或配置里。",
                "evidence": "Agent27 显示无错峰 0.75 时间占用 0.978，执行错峰后降到 0.884，瓶颈为空。",
                "metrics": self._execution_metrics(agent27),
            },
            {
                "step": "online_control_state",
                "claim": "最新状态可以维持条件恢复，但仍不是永久满负荷基线。",
                "evidence": "Agent28 接回在线控制后维持 0.75，保留 0.60 回退线，当前无需重规划。",
                "metrics": {
                    "recovery_control_mode": latest_state.get("recovery_control_mode"),
                    "next_intake_fraction": latest_state.get("next_intake_fraction"),
                    "fallback_intake_fraction": latest_state.get("fallback_intake_fraction"),
                    "replan_required": latest_state.get("replan_required"),
                    "bottleneck_ids": bottlenecks,
                },
            },
        ]

    def _readiness_assessment(
        self,
        latest_state: dict[str, object],
        evidence_chain: list[dict[str, object]],
    ) -> dict[str, object]:
        prototype_complete = self.synthesized_agent_count >= 28 and len(evidence_chain) >= 6
        latest_stable = (
            latest_state.get("recovery_control_mode") == "maintain_conditional_recovery"
            and latest_state.get("replan_required") is False
        )
        return {
            "prototype_chain_complete": prototype_complete,
            "latest_control_stable": latest_stable,
            "maturity_level": "research_platform_ready_for_field_calibration"
            if prototype_complete and latest_stable
            else "prototype_requires_more_internal_iteration",
            "can_be_used_for": [
                "重大项目研究方案论证",
                "低成本传感-软传感-多智能体闭环的原型展示",
                "实验方案拆解、瓶颈诊断和资源配置推演",
                "后续真实水样和中试数据接入前的仿真基线",
            ],
            "not_yet_validated_for": [
                "真实污水连续运行条件下的外推性能",
                "真实传感器漂移、污染结垢和维护周期",
                "真实催化剂寿命、再生效率和副产物风险",
                "现场 PLC/SCADA 通信和安全联锁",
            ],
            "go_no_go": "可以作为研究原型与项目书核心方案；不应直接宣称已具备现场自治运行能力。",
        }

    @staticmethod
    def _calibration_roadmap() -> list[dict[str, object]]:
        return [
            {
                "phase": "P1",
                "title": "真实传感器噪声与漂移标定",
                "data_needed": ["pH/ORP/EC/浊度/流量/UV254 原始时间序列", "人工校准记录", "传感器污染结垢/清洗记录"],
                "model_update": "校准 DataQualityAgent 阈值、采样噪声模型和 sensor_confidence 计算。",
            },
            {
                "phase": "P2",
                "title": "软传感器真实水样重训",
                "data_needed": ["目标污染物/COD/TOC/UV254 离线检测", "反应时间、加药量、回流比", "达标/未达标标签"],
                "model_update": "用真实标签更新 soft sensor calibrator，并加入不确定性输出。",
            },
            {
                "phase": "P3",
                "title": "催化剂生命周期与副产物风险校准",
                "data_needed": ["催化剂循环次数", "再生前后活性", "压降/表面污染", "副产物或余氧化剂检测"],
                "model_update": "校准再生收益衰减、replace trigger、副产物安全门和验证规划规则。",
            },
            {
                "phase": "P4",
                "title": "闭环控制与循环时间预算中试验证",
                "data_needed": ["批次运行记录", "暂存/回流/验证并行时间", "失败回退案例", "人工干预记录"],
                "model_update": "校准 Agent24-28 的时间预算、错峰收益、恢复爬坡和 fallback triggers。",
            },
            {
                "phase": "P5",
                "title": "经济性与部署接口验证",
                "data_needed": ["传感器报价", "试剂/催化剂/人工成本", "PLC/SCADA 点表", "安全联锁要求"],
                "model_update": "校准 sensor economics、资源扩容成本、预算释放顺序和现场执行接口。",
            },
        ]

    @staticmethod
    def _project_mermaid() -> str:
        return """flowchart LR
    A["低成本传感"] --> B["数据质控"]
    B --> C["软传感灰箱状态"]
    C --> D["机理解释与故障诊断"]
    D --> E["控制动作生成"]
    E --> F["成本安全与仲裁"]
    F --> G["循环处理反馈"]
    G --> A
    F --> H["传感配置与批次调度"]
    H --> I["队列规划与资源扩容"]
    I --> J["长期经济性与分阶段实施"]
    J --> K["压力测试与项目组合"]
    K --> L["在线项目控制"]
    L --> M["遥测接入与自动重规划"]
    M --> N["基线写回与回放验证"]
    N --> O["恢复爬坡与时间预算修复"]
    O --> P["恢复在线控制"]
    P --> L
    P --> Q["项目综合总览与真实数据校准路线"]"""

    def _deliverables(self) -> list[dict[str, str]]:
        defaults = {
            "research_plan_docx": "docs/研究方案_Word兼容版.docx",
            "agent_system_spec": "docs/agent_system_spec.md",
            "current_status": "notes/current_status.md",
            "iteration_log": "notes/iteration_log.md",
            "latest_agent28_report": "outputs/agent28_recovery_online_control/agent28_report.md",
            "agent29_report": "outputs/agent29_project_synthesis/agent29_report.md",
            "project_overview": "docs/project_overview_28_agent.md",
        }
        merged = {**defaults, **self.artifact_paths}
        return [{"artifact": key, "path": value} for key, value in merged.items()]

    def _issues(self, readiness: dict[str, object]) -> list[QualityIssue]:
        issues = [
            QualityIssue(
                sensor="project_synthesis",
                issue_type="field_validation_missing",
                severity=Severity.WARNING,
                message="当前链条已适合研究原型与项目论证，但尚未用真实连续运行数据完成现场校准。",
                evidence={"not_yet_validated_for": readiness["not_yet_validated_for"]},
            )
        ]
        if not readiness["latest_control_stable"]:
            issues.append(
                QualityIssue(
                    sensor="project_synthesis",
                    issue_type="latest_control_not_stable",
                    severity=Severity.WARNING,
                    message="最新在线控制状态仍不稳定，需要继续内部闭环迭代。",
                    evidence={"readiness": readiness},
                )
            )
        return issues

    @staticmethod
    def _recommendations(readiness: dict[str, object]) -> list[str]:
        if readiness["latest_control_stable"]:
            return [
                "将当前 28-agent 执行链作为项目书和汇报的核心原型，明确其定位为“可校准研究平台”。",
                "下一轮优先接入真实传感器时间序列和离线检测标签，校准软传感器、时间预算和 fallback triggers。",
                "保留 0.75 条件恢复、0.60 回退线和 campaign 后复核，不把仿真稳定结果写成永久满负荷结论。",
            ]
        return [
            "继续内部迭代最新在线控制状态，先解除 replan 或 fallback 冲突。",
            "在状态稳定前，不应进入真实数据校准之外的对外结论包装。",
        ]

    def _report_metrics(self, key: str) -> dict[str, object]:
        payload = self.milestone_reports.get(key, {})
        if not isinstance(payload, dict):
            return {}
        for section in payload.values():
            if isinstance(section, dict) and isinstance(section.get("metrics"), dict):
                return section["metrics"]
        return payload.get("metrics", {}) if isinstance(payload.get("metrics"), dict) else {}

    @staticmethod
    def _post_replan_metrics(metrics: dict[str, object]) -> dict[str, object]:
        comparison = metrics.get("comparison", {})
        if not isinstance(comparison, dict):
            return {}
        return {
            "verdict": comparison.get("verdict"),
            "validation_usage_before": comparison.get(
                "validation_usage_before", comparison.get("before_validation_staff_usage")
            ),
            "validation_usage_after": comparison.get(
                "validation_usage_after", comparison.get("after_validation_staff_usage")
            ),
            "time_usage_before": comparison.get("time_usage_before", comparison.get("before_time_budget_usage")),
            "time_usage_after": comparison.get("time_usage_after", comparison.get("after_time_budget_usage")),
            "removed_bottlenecks": comparison.get(
                "removed_bottlenecks", comparison.get("removed_bottleneck_ids", [])
            ),
        }

    @staticmethod
    def _time_budget_metrics(metrics: dict[str, object]) -> dict[str, object]:
        selected = metrics.get("selected_candidate", {})
        if not isinstance(selected, dict):
            return {}
        return {
            "selected_candidate_id": selected.get("candidate_id"),
            "target_intake_fraction": selected.get("target_intake_fraction"),
            "time_budget_usage": selected.get("time_budget_usage"),
            "validation_staff_usage": selected.get("validation_staff_usage"),
            "elapsed_reduction_min": selected.get("elapsed_reduction_min"),
        }

    @staticmethod
    def _execution_metrics(metrics: dict[str, object]) -> dict[str, object]:
        comparison = metrics.get("comparison", {})
        if not isinstance(comparison, dict):
            return {}
        return {
            "replay_verdict": comparison.get("replay_verdict"),
            "time_usage_without_strategy": comparison.get("time_usage_without_strategy"),
            "time_usage_with_strategy": comparison.get("time_usage_with_strategy"),
            "strategy_bottleneck_ids": comparison.get("strategy_bottleneck_ids", []),
            "recommended_next_intake_fraction": comparison.get("recommended_next_intake_fraction"),
        }
