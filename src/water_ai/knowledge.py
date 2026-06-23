from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class MechanismRule:
    rule_id: str
    mechanism: str
    explanation: str
    action_hint: str


ComparisonOp = Literal[">", ">=", "<", "<="]


@dataclass(frozen=True)
class SignalCondition:
    signal: str
    op: ComparisonOp
    threshold: float


@dataclass(frozen=True)
class KnowledgeEntry:
    entry_id: str
    pollutant_class: str
    material_family: str
    mechanism_tags: tuple[str, ...]
    signal_conditions: tuple[SignalCondition, ...]
    dq_issue_conditions: tuple[str, ...]
    soft_issue_conditions: tuple[str, ...]
    supports_rules: tuple[str, ...]
    action_biases: dict[str, float]
    explanation: str
    action_hint: str
    evidence_stage: str = "literature_informed_simulation"
    field_validation_need: tuple[str, ...] = ()
    source_basis: tuple[str, ...] = ()


@dataclass(frozen=True)
class KnowledgeGraphNode:
    node_id: str
    node_type: str
    label: str
    properties: dict[str, object]


@dataclass(frozen=True)
class KnowledgeGraphEdge:
    edge_id: str
    source: str
    target: str
    edge_type: str
    weight: float
    evidence_stage: str
    entry_id: str
    field_validation_need: tuple[str, ...]
    source_basis: tuple[str, ...]
    claim_boundary: str
    properties: dict[str, object]


MECHANISM_RULES: dict[str, MechanismRule] = {
    "sensor_uncertainty": MechanismRule(
        rule_id="sensor_uncertainty",
        mechanism="传感不确定性主导",
        explanation="低成本传感通道出现缺失、突变、卡死或漂移时，软测量虽然可以估计状态，但放行决策应受传感可信度约束。",
        action_hint="进入旁路快检或离线校准，禁止直接自动放行。",
    ),
    "hydraulic_anomaly": MechanismRule(
        rule_id="hydraulic_anomaly",
        mechanism="水力停留时间异常",
        explanation="流量持续偏低、短窗口平均流量不足或水力置信度低，会改变实际停留时间和回流收益，使模型对反应进程的判断出现偏差。",
        action_hint="核查泵阀、管路堵塞和实际回流比，再更新停留时间估计。",
    ),
    "loop_buffer_needed": MechanismRule(
        rule_id="loop_buffer_needed",
        mechanism="需要循环缓冲窗口",
        explanation="污染物残留风险尚未完全压低，但氧化能力和回流边际收益仍存在，说明系统不一定要立即加药或切换单元，而应利用循环结构争取传感、反应和诊断时间。",
        action_hint="保持受控回流或延长停留，等待下一窗口软传感与旁路验证共同更新状态。",
    ),
    "matrix_interference": MechanismRule(
        rule_id="matrix_interference",
        mechanism="基质干扰增强",
        explanation="电导率、浊度或 pH 偏离提示高盐、高 COD、颗粒物或缓冲体系可能消耗氧化剂并抑制高级氧化反应。",
        action_hint="评估预处理、提高氧化剂投加、调 pH 或切换到更适合高基质负荷的单元。",
    ),
    "oxidant_limitation": MechanismRule(
        rule_id="oxidant_limitation",
        mechanism="氧化剂不足",
        explanation="ORP 偏低且污染物残留风险高时，说明氧化能力可能不足，继续单纯延长停留的收益有限。",
        action_hint="优先评估补加氧化剂，再判断是否回流。",
    ),
    "byproduct_risk": MechanismRule(
        rule_id="byproduct_risk",
        mechanism="副产物或过氧化风险升高",
        explanation="氧化剂余量偏高、基质干扰较强或处理窗口过长时，继续加药可能带来副产物、过氧化或残余氧化剂风险。",
        action_hint="限制继续投加氧化剂，优先旁路验证副产物/余氧化剂，并考虑预处理削弱基质前体。",
    ),
    "catalyst_deactivation": MechanismRule(
        rule_id="catalyst_deactivation",
        mechanism="催化剂活性下降",
        explanation="反应完成度低、催化活性指数低且回流收益下降时，可能是催化剂失活或活性位受污染。",
        action_hint="考虑催化剂再生、更换或切换处理单元。",
    ),
    "reaction_time_insufficient": MechanismRule(
        rule_id="reaction_time_insufficient",
        mechanism="反应时间不足",
        explanation="污染物残留风险高但氧化剂余量仍足、催化活性尚可时，问题更可能是停留时间不足。",
        action_hint="优先延长停留时间或回流，而不是立即增加药剂。",
    ),
    "likely_treated_but_not_releasable": MechanismRule(
        rule_id="likely_treated_but_not_releasable",
        mechanism="水质可能已处理完成但证据不足",
        explanation="软测量显示达标概率较高，但传感可信度不足或存在漂移，不能把模型估计直接等同于安全放行。",
        action_hint="保持暂存，进行旁路快检；若校准通过再放行。",
    ),
}


KNOWLEDGE_BASE: tuple[KnowledgeEntry, ...] = (
    KnowledgeEntry(
        entry_id="kb_matrix_aop_inhibition",
        pollutant_class="高盐/高 COD 难降解有机废水",
        material_family="高级氧化或催化氧化材料",
        mechanism_tags=("matrix_interference", "radical_scavenging", "mass_transfer_limitation"),
        signal_conditions=(
            SignalCondition("matrix_interference", ">", 0.55),
            SignalCondition("pollutant_residual_risk", ">", 0.38),
        ),
        dq_issue_conditions=(),
        soft_issue_conditions=(),
        supports_rules=("matrix_interference", "reaction_time_insufficient", "loop_buffer_needed"),
        action_biases={"switch_or_pretreat": 0.18, "recirculate": 0.08, "dose_oxidant": -0.06},
        explanation="高盐、高 COD、颗粒物或缓冲体系会竞争氧化剂/自由基并降低传质效率，使同一剂量和停留时间下的去除率下降。",
        action_hint="先判断是否需要混凝、吸附、膜分离或稀释预处理，再决定是否继续回流。",
    ),
    KnowledgeEntry(
        entry_id="kb_oxidant_limited_refractory_organics",
        pollutant_class="高负荷还原性或难降解有机污染物",
        material_family="氧化剂驱动体系",
        mechanism_tags=("oxidant_limitation", "electron_demand_excess"),
        signal_conditions=(
            SignalCondition("pollutant_residual_risk", ">", 0.45),
            SignalCondition("oxidant_remaining", "<", 0.35),
        ),
        dq_issue_conditions=(),
        soft_issue_conditions=(),
        supports_rules=("oxidant_limitation", "loop_buffer_needed"),
        action_biases={"dose_oxidant": 0.20, "recirculate": 0.10, "release": -0.20},
        explanation="残留风险高而氧化剂余量低，通常说明电子受体或活性氧供给不足，单纯延长停留的边际收益有限。",
        action_hint="先用余氧化剂快检确认，再采用小步补加与回流联合策略。",
    ),
    KnowledgeEntry(
        entry_id="kb_catalyst_site_fouling",
        pollutant_class="含络合物、天然有机质或颗粒物的复杂废水",
        material_family="负载型催化剂/类芬顿/光催化材料",
        mechanism_tags=("catalyst_deactivation", "active_site_blocking", "surface_fouling"),
        signal_conditions=(
            SignalCondition("catalyst_activity", "<", 0.45),
            SignalCondition("reaction_completion", "<", 0.62),
            SignalCondition("oxidant_remaining", ">", 0.45),
        ),
        dq_issue_conditions=(),
        soft_issue_conditions=(),
        supports_rules=("catalyst_deactivation", "loop_buffer_needed"),
        action_biases={"regenerate_catalyst": 0.24, "recirculate": 0.06, "dose_oxidant": -0.08},
        explanation="氧化剂仍较充足但反应完成度低且催化活性低，更像活性位被污染、堵塞或材料循环性能衰减，而不是简单缺药。",
        action_hint="优先做催化剂活性复测、冲洗/再生或更换对照，再安排回流验证。",
    ),
    KnowledgeEntry(
        entry_id="kb_loop_buffer_for_slow_sensing",
        pollutant_class="目标污染物需慢检测或低成本代理检测的废水",
        material_family="循环式反应器/旁路快检系统",
        mechanism_tags=("loop_buffer_needed", "soft_sensor_delay", "grey_box_inference"),
        signal_conditions=(
            SignalCondition("pollutant_residual_risk", ">", 0.32),
            SignalCondition("recycle_gain", ">", 0.20),
            SignalCondition("release_readiness", "<", 0.86),
        ),
        dq_issue_conditions=(),
        soft_issue_conditions=("release_blocked_by_uncertainty",),
        supports_rules=("loop_buffer_needed",),
        action_biases={"hold_for_validation": 0.16, "recirculate": 0.14, "release": -0.18},
        explanation="当软传感认为继续循环仍有收益，而放行证据不足时，循环结构可以为慢检测、模型复估和旁路验证争取时间。",
        action_hint="不要强行实时控制；设置暂存/回流窗口，让慢证据进入下一轮状态估计。",
    ),
    KnowledgeEntry(
        entry_id="kb_overoxidation_byproduct_precursor",
        pollutant_class="含芳香族、卤代前体或天然有机质的废水",
        material_family="强氧化体系",
        mechanism_tags=("byproduct_risk", "overoxidation", "precursor_control"),
        signal_conditions=(
            SignalCondition("byproduct_risk", ">", 0.55),
            SignalCondition("oxidant_remaining", ">", 0.62),
        ),
        dq_issue_conditions=(),
        soft_issue_conditions=(),
        supports_rules=("byproduct_risk", "likely_treated_but_not_releasable"),
        action_biases={"dose_oxidant": -0.24, "hold_for_validation": 0.20, "switch_or_pretreat": 0.10},
        explanation="氧化剂余量高且副产物风险上升时，继续加药可能把残留问题转化为副产物或余氧化剂问题。",
        action_hint="暂停盲目加药，优先做副产物/余氧化剂快检，并考虑吸附抛光或预处理削弱前体。",
    ),
    KnowledgeEntry(
        entry_id="kb_sensor_limited_release_evidence",
        pollutant_class="低浓度目标污染物或慢检测指标",
        material_family="低成本传感 + 软传感系统",
        mechanism_tags=("sensor_uncertainty", "release_evidence_gap"),
        signal_conditions=(
            SignalCondition("sensor_confidence", "<", 0.82),
            SignalCondition("release_readiness", "<", 0.82),
        ),
        dq_issue_conditions=("missing", "spike", "flatline", "drift_suspected", "low_flow_absolute"),
        soft_issue_conditions=("release_blocked_by_uncertainty",),
        supports_rules=("sensor_uncertainty", "likely_treated_but_not_releasable"),
        action_biases={"calibrate_sensors": 0.20, "hold_for_validation": 0.18, "release": -0.25},
        explanation="低成本代理信号出现缺失、漂移或置信度不足时，软传感结果不能直接等同于放行证据。",
        action_hint="进入校准、降权或旁路检测流程；模型估计只能作为排序依据，不能替代放行门槛。",
        field_validation_need=("真实传感漂移记录", "离线放行标签", "低浓度目标物检测限"),
        source_basis=("low_cost_proxy_sensing", "soft_sensor_release_gate"),
    ),
    KnowledgeEntry(
        entry_id="kb_pfas_adsorption_or_membrane_needed",
        pollutant_class="PFAS 或高度持久性氟代有机物",
        material_family="吸附/离子交换/膜分离/抛光单元",
        mechanism_tags=("persistent_micropollutant", "low_aop_destructibility", "polishing_unit_needed"),
        signal_conditions=(
            SignalCondition("pollutant_residual_risk", ">", 0.55),
            SignalCondition("reaction_completion", "<", 0.40),
            SignalCondition("oxidant_remaining", ">", 0.52),
            SignalCondition("matrix_interference", "<", 0.55),
            SignalCondition("release_readiness", "<", 0.60),
        ),
        dq_issue_conditions=(),
        soft_issue_conditions=(),
        supports_rules=("reaction_time_insufficient", "loop_buffer_needed"),
        action_biases={"switch_or_pretreat": 0.22, "hold_for_validation": 0.18, "dose_oxidant": -0.16, "release": -0.24},
        explanation="若氧化能力仍在但残留风险长期下降缓慢，应警惕目标物并非适合单纯 AOP 快速降解的类型，可能需要吸附、离子交换、膜分离或末端抛光。",
        action_hint="不要把继续加药当作唯一选择；应进入目标污染物确认、吸附/膜抛光或组合工艺评估。",
        field_validation_need=("目标物 LC-MS/LC-MS-MS 标签", "处理前后 PFAS 或难降解微污染物浓度", "吸附/膜抛光前后对照"),
        source_basis=("persistent_micropollutant_treatment", "adsorption_membrane_polishing"),
    ),
    KnowledgeEntry(
        entry_id="kb_heavy_metal_not_destroyed_by_oxidation",
        pollutant_class="重金属或金属络合物废水",
        material_family="沉淀/吸附/离子交换/膜分离材料",
        mechanism_tags=("non_degradable_species", "speciation_control", "separation_required"),
        signal_conditions=(
            SignalCondition("pollutant_residual_risk", ">", 0.46),
            SignalCondition("oxidant_remaining", ">", 0.48),
            SignalCondition("matrix_interference", ">", 0.62),
            SignalCondition("reaction_completion", "<", 0.58),
            SignalCondition("catalyst_activity", ">", 0.55),
        ),
        dq_issue_conditions=(),
        soft_issue_conditions=(),
        supports_rules=("matrix_interference", "reaction_time_insufficient"),
        action_biases={"switch_or_pretreat": 0.26, "hold_for_validation": 0.12, "dose_oxidant": -0.18, "recirculate": -0.04},
        explanation="金属污染物不能通过氧化被真正矿化，氧化可能只改变价态或络合形态；若高基质下残留风险不降，应转向沉淀、吸附、离子交换或膜分离。",
        action_hint="优先确认金属形态和络合状态，再选择分离/固定化单元，而不是盲目延长氧化循环。",
        field_validation_need=("ICP/金属离子标签", "价态/络合形态", "沉淀或吸附出水对照"),
        source_basis=("heavy_metal_speciation", "separation_process_required"),
    ),
    KnowledgeEntry(
        entry_id="kb_biological_effluent_low_orp_load",
        pollutant_class="生化尾水或含营养盐/可生化有机物废水",
        material_family="生物处理耦合/曝气/后氧化抛光",
        mechanism_tags=("biological_residual_load", "oxygen_demand", "hybrid_treatment_needed"),
        signal_conditions=(
            SignalCondition("pollutant_residual_risk", ">", 0.42),
            SignalCondition("oxidant_remaining", "<", 0.42),
            SignalCondition("matrix_interference", ">", 0.38),
            SignalCondition("sensor_confidence", ">", 0.80),
            SignalCondition("byproduct_risk", "<", 0.45),
        ),
        dq_issue_conditions=(),
        soft_issue_conditions=(),
        supports_rules=("oxidant_limitation", "matrix_interference", "loop_buffer_needed"),
        action_biases={"dose_oxidant": 0.10, "switch_or_pretreat": 0.14, "recirculate": 0.08, "release": -0.18},
        explanation="若低成本信号稳定但 ORP/氧化剂余量偏低且残留风险高，可能反映生化尾水的持续需氧量或营养盐/可生化有机物负荷，需要生物处理与后氧化协同。",
        action_hint="区分目标微污染物与背景可生化负荷，必要时先做曝气/生物单元或分流，再进入后氧化抛光。",
        field_validation_need=("COD/BOD/氨氮/总氮标签", "ORP 与曝气记录", "生物单元前后对照"),
        source_basis=("biological_effluent_polishing", "hybrid_treatment"),
    ),
)


def query_knowledge_base(
    state: dict[str, float],
    *,
    dq_issue_types: set[str] | None = None,
    soft_issue_types: set[str] | None = None,
    min_score: float = 0.58,
) -> list[dict[str, object]]:
    """Return structured knowledge entries supported by current process evidence."""

    dq_issue_types = dq_issue_types or set()
    soft_issue_types = soft_issue_types or set()
    matches = [_score_entry(entry, state, dq_issue_types, soft_issue_types) for entry in KNOWLEDGE_BASE]
    filtered = [match for match in matches if float(match["match_score"]) >= min_score]
    filtered.sort(key=lambda item: float(item["match_score"]), reverse=True)
    return filtered


def build_knowledge_graph(entries: tuple[KnowledgeEntry, ...] = KNOWLEDGE_BASE) -> dict[str, object]:
    """Build a typed, serializable KG seed from the curated knowledge entries."""

    nodes: dict[str, KnowledgeGraphNode] = {}
    edges: list[KnowledgeGraphEdge] = []

    def add_node(node_id: str, node_type: str, label: str, **properties: object) -> None:
        if node_id not in nodes:
            nodes[node_id] = KnowledgeGraphNode(
                node_id=node_id,
                node_type=node_type,
                label=label,
                properties=properties,
            )

    def add_edge(
        *,
        source: str,
        target: str,
        edge_type: str,
        entry: KnowledgeEntry,
        weight: float,
        **properties: object,
    ) -> None:
        safe_type = edge_type.replace(" ", "_")
        edge_id = f"{entry.entry_id}:{safe_type}:{len(edges) + 1}"
        edges.append(
            KnowledgeGraphEdge(
                edge_id=edge_id,
                source=source,
                target=target,
                edge_type=edge_type,
                weight=round(max(0.0, min(1.0, weight)), 3),
                evidence_stage=entry.evidence_stage,
                entry_id=entry.entry_id,
                field_validation_need=entry.field_validation_need,
                source_basis=entry.source_basis,
                claim_boundary=_claim_boundary(entry),
                properties=properties,
            )
        )

    for entry in entries:
        entry_node = f"entry:{entry.entry_id}"
        pollutant_node = f"pollutant:{entry.pollutant_class}"
        material_node = f"material:{entry.material_family}"
        add_node(entry_node, "knowledge_entry", entry.entry_id, evidence_stage=entry.evidence_stage)
        add_node(pollutant_node, "pollutant_class", entry.pollutant_class)
        add_node(material_node, "material_family", entry.material_family)
        add_edge(source=entry_node, target=pollutant_node, edge_type="describes_pollutant", entry=entry, weight=0.82)
        add_edge(source=entry_node, target=material_node, edge_type="uses_material_family", entry=entry, weight=0.78)

        for tag in entry.mechanism_tags:
            mechanism_node = f"mechanism:{tag}"
            add_node(mechanism_node, "mechanism_tag", tag)
            add_edge(source=pollutant_node, target=mechanism_node, edge_type="has_mechanism", entry=entry, weight=0.78)
            add_edge(source=material_node, target=mechanism_node, edge_type="affected_by_mechanism", entry=entry, weight=0.70)
            add_edge(source=entry_node, target=mechanism_node, edge_type="claims_mechanism", entry=entry, weight=0.84)

        for condition in entry.signal_conditions:
            signal_node = f"signal:{condition.signal}"
            add_node(signal_node, "observable_or_hidden_signal", condition.signal)
            for tag in entry.mechanism_tags:
                add_edge(
                    source=signal_node,
                    target=f"mechanism:{tag}",
                    edge_type="observes_condition",
                    entry=entry,
                    weight=0.74,
                    op=condition.op,
                    threshold=condition.threshold,
                )

        for rule_id in entry.supports_rules:
            rule = MECHANISM_RULES.get(rule_id)
            rule_node = f"rule:{rule_id}"
            add_node(rule_node, "mechanism_rule", rule_id, mechanism=rule.mechanism if rule else rule_id)
            for tag in entry.mechanism_tags:
                add_edge(source=f"mechanism:{tag}", target=rule_node, edge_type="supports_rule", entry=entry, weight=0.86)

        for action_id, bias in entry.action_biases.items():
            action_node = f"action:{action_id}"
            add_node(action_node, "control_action", action_id)
            for rule_id in entry.supports_rules:
                add_edge(
                    source=f"rule:{rule_id}",
                    target=action_node,
                    edge_type="biases_action",
                    entry=entry,
                    weight=min(1.0, abs(float(bias)) * 3.2),
                    action_bias=float(bias),
                    direction="support" if float(bias) > 0 else "suppress",
                )

        for need in entry.field_validation_need:
            need_node = f"field_need:{need}"
            add_node(need_node, "field_validation_need", need)
            add_edge(source=entry_node, target=need_node, edge_type="needs_field_validation", entry=entry, weight=0.90)

    return {
        "nodes": [_node_to_dict(node) for node in nodes.values()],
        "edges": [_edge_to_dict(edge) for edge in edges],
        "summary": summarize_knowledge_graph(nodes.values(), edges),
    }


def reason_over_knowledge_graph(
    state: dict[str, float],
    *,
    dq_issue_types: set[str] | None = None,
    soft_issue_types: set[str] | None = None,
    min_score: float = 0.58,
) -> dict[str, object]:
    """Return graph-backed evidence paths and action constraints for the current state."""

    matches = query_knowledge_base(
        state,
        dq_issue_types=dq_issue_types,
        soft_issue_types=soft_issue_types,
        min_score=min_score,
    )
    graph = build_knowledge_graph()
    paths: list[dict[str, object]] = []
    action_biases: dict[str, dict[str, object]] = {}
    field_validation_queue: dict[str, dict[str, object]] = {}
    unsupported_claims: list[dict[str, object]] = []

    entries = {entry.entry_id: entry for entry in KNOWLEDGE_BASE}
    for match in matches:
        entry = entries[str(match["entry_id"])]
        evidence_weight = _evidence_weight(entry)
        source_basis = list(entry.source_basis)
        if not source_basis:
            unsupported_claims.append(
                {
                    "entry_id": entry.entry_id,
                    "reason": "source_basis_missing",
                    "claim_boundary": _claim_boundary(entry),
                }
            )
        if "field" not in entry.evidence_stage.lower():
            unsupported_claims.append(
                {
                    "entry_id": entry.entry_id,
                    "reason": "not_field_supported",
                    "evidence_stage": entry.evidence_stage,
                    "claim_boundary": _claim_boundary(entry),
                }
            )
        for need in entry.field_validation_need:
            field_validation_queue.setdefault(
                need,
                {
                    "field_validation_need": need,
                    "supporting_entries": [],
                    "required_before": "actuator_or_release_gate_claim",
                },
            )
            field_validation_queue[need]["supporting_entries"].append(entry.entry_id)

        for rule_id in match.get("supports_rules", []):
            rule_id_str = str(rule_id)
            path = {
                "path_id": f"{entry.entry_id}->{rule_id_str}",
                "entry_id": entry.entry_id,
                "rule_id": rule_id_str,
                "path_nodes": [
                    f"entry:{entry.entry_id}",
                    f"pollutant:{entry.pollutant_class}",
                    *[f"mechanism:{tag}" for tag in entry.mechanism_tags],
                    f"rule:{rule_id_str}",
                ],
                "mechanism_tags": list(entry.mechanism_tags),
                "matched_signal_count": len(match.get("signal_hits", [])),
                "matched_issue_count": len(match.get("dq_issue_hits", [])) + len(match.get("soft_issue_hits", [])),
                "match_score": match["match_score"],
                "evidence_stage": entry.evidence_stage,
                "evidence_weight": evidence_weight,
                "field_validation_need": list(entry.field_validation_need),
                "source_basis": source_basis,
                "claim_boundary": _claim_boundary(entry),
            }
            paths.append(path)

        for action_id, bias in entry.action_biases.items():
            weighted_bias = float(match["match_score"]) * float(bias) * evidence_weight
            row = action_biases.setdefault(
                str(action_id),
                {
                    "action_id": str(action_id),
                    "bias_score": 0.0,
                    "supporting_entries": [],
                    "evidence_paths": [],
                    "claim_boundaries": [],
                },
            )
            row["bias_score"] = float(row["bias_score"]) + weighted_bias
            row["supporting_entries"].append(entry.entry_id)
            row["evidence_paths"].extend(
                f"{entry.entry_id}->{rule_id}" for rule_id in match.get("supports_rules", [])
            )
            row["claim_boundaries"].append(_claim_boundary(entry))

    action_constraint_patch = []
    for action_id, row in sorted(action_biases.items()):
        bias = round(max(-0.22, min(0.22, float(row["bias_score"]))), 3)
        if abs(bias) < 0.01:
            continue
        action_constraint_patch.append(
            {
                "action_id": action_id,
                "bias_score": bias,
                "direction": "support" if bias > 0 else "suppress",
                "supporting_entries": sorted(set(str(item) for item in row["supporting_entries"])),
                "evidence_paths": sorted(set(str(item) for item in row["evidence_paths"])),
                "claim_boundaries": sorted(set(str(item) for item in row["claim_boundaries"])),
                "writeback_boundary": "score_prior_only_until_field_validation",
            }
        )

    graph_summary = graph["summary"] if isinstance(graph.get("summary"), dict) else {}
    field_ratio = float(graph_summary.get("field_supported_edge_ratio", 0.0))
    evidence_traceability = round(min(1.0, len(paths) / max(1, len(matches))), 3)
    constraint_hit_rate = round(len(action_constraint_patch) / max(1, len({action for match in matches for action in match.get("action_biases", {})})), 3)
    readiness = {
        "kg_reasoning_status": "kg_reasoning_patch_ready_needs_field_supported_edges"
        if paths
        else "kg_reasoning_no_state_match",
        "matched_entry_count": len(matches),
        "evidence_path_count": len(paths),
        "action_constraint_count": len(action_constraint_patch),
        "field_supported_edge_ratio": field_ratio,
        "evidence_traceability": evidence_traceability,
        "constraint_hit_rate": constraint_hit_rate,
        "claim_verification_pass_rate": round(1.0 - len(unsupported_claims) / max(1, len(matches) * 2), 3),
        "can_update_mechanism_evidence": bool(paths),
        "can_update_action_bias_prior": bool(action_constraint_patch),
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }
    return {
        "graph_summary": graph_summary,
        "matched_entries": matches,
        "evidence_paths": paths,
        "action_constraint_patch": action_constraint_patch,
        "field_validation_queue": list(field_validation_queue.values()),
        "unsupported_claims": unsupported_claims,
        "readiness": readiness,
    }


def summarize_knowledge_graph(
    nodes: object,
    edges: object | None = None,
) -> dict[str, object]:
    node_list = list(nodes) if not isinstance(nodes, dict) else list(nodes.values())
    edge_list = list(edges or [])
    node_type_counts: dict[str, int] = {}
    edge_type_counts: dict[str, int] = {}
    evidence_stage_counts: dict[str, int] = {}
    field_supported_edges = 0
    for node in node_list:
        node_type = node.node_type if isinstance(node, KnowledgeGraphNode) else str(node.get("node_type", "unknown"))
        node_type_counts[node_type] = node_type_counts.get(node_type, 0) + 1
    for edge in edge_list:
        edge_type = edge.edge_type if isinstance(edge, KnowledgeGraphEdge) else str(edge.get("edge_type", "unknown"))
        evidence_stage = edge.evidence_stage if isinstance(edge, KnowledgeGraphEdge) else str(edge.get("evidence_stage", "unknown"))
        edge_type_counts[edge_type] = edge_type_counts.get(edge_type, 0) + 1
        evidence_stage_counts[evidence_stage] = evidence_stage_counts.get(evidence_stage, 0) + 1
        if "field" in evidence_stage.lower():
            field_supported_edges += 1
    return {
        "node_count": len(node_list),
        "edge_count": len(edge_list),
        "node_type_counts": dict(sorted(node_type_counts.items())),
        "edge_type_counts": dict(sorted(edge_type_counts.items())),
        "evidence_stage_counts": dict(sorted(evidence_stage_counts.items())),
        "field_supported_edge_ratio": round(field_supported_edges / max(1, len(edge_list)), 3),
        "graph_status": "typed_kg_seed_needs_field_supported_edges",
    }


def _score_entry(
    entry: KnowledgeEntry,
    state: dict[str, float],
    dq_issue_types: set[str],
    soft_issue_types: set[str],
) -> dict[str, object]:
    signal_hits: list[dict[str, object]] = []
    signal_misses: list[dict[str, object]] = []
    for condition in entry.signal_conditions:
        value = state.get(condition.signal)
        evidence = {
            "signal": condition.signal,
            "op": condition.op,
            "threshold": condition.threshold,
            "value": value,
        }
        if value is not None and _condition_matches(float(value), condition.op, condition.threshold):
            signal_hits.append(evidence)
        else:
            signal_misses.append(evidence)

    dq_hits = sorted(set(entry.dq_issue_conditions) & dq_issue_types)
    soft_hits = sorted(set(entry.soft_issue_conditions) & soft_issue_types)

    signal_score = len(signal_hits) / max(1, len(entry.signal_conditions))
    issue_condition_count = len(entry.dq_issue_conditions) + len(entry.soft_issue_conditions)
    issue_score = (len(dq_hits) + len(soft_hits)) / max(1, issue_condition_count)
    has_issue_conditions = issue_condition_count > 0
    if not has_issue_conditions:
        issue_score = 0.0

    if not signal_hits and not dq_hits and not soft_hits:
        match_score = 0.0
    else:
        match_score = 0.20 + 0.62 * signal_score + 0.18 * issue_score

    return {
        "entry_id": entry.entry_id,
        "pollutant_class": entry.pollutant_class,
        "material_family": entry.material_family,
        "mechanism_tags": list(entry.mechanism_tags),
        "supports_rules": list(entry.supports_rules),
        "action_biases": entry.action_biases,
        "explanation": entry.explanation,
        "action_hint": entry.action_hint,
        "evidence_stage": entry.evidence_stage,
        "field_validation_need": list(entry.field_validation_need),
        "source_basis": list(entry.source_basis),
        "signal_hits": signal_hits,
        "signal_misses": signal_misses,
        "dq_issue_hits": dq_hits,
        "soft_issue_hits": soft_hits,
        "match_score": round(max(0.0, min(1.0, match_score)), 3),
    }


def _condition_matches(value: float, op: ComparisonOp, threshold: float) -> bool:
    if op == ">":
        return value > threshold
    if op == ">=":
        return value >= threshold
    if op == "<":
        return value < threshold
    if op == "<=":
        return value <= threshold
    return False


def _node_to_dict(node: KnowledgeGraphNode) -> dict[str, object]:
    return {
        "node_id": node.node_id,
        "node_type": node.node_type,
        "label": node.label,
        "properties": node.properties,
    }


def _edge_to_dict(edge: KnowledgeGraphEdge) -> dict[str, object]:
    return {
        "edge_id": edge.edge_id,
        "source": edge.source,
        "target": edge.target,
        "edge_type": edge.edge_type,
        "weight": edge.weight,
        "evidence_stage": edge.evidence_stage,
        "entry_id": edge.entry_id,
        "field_validation_need": list(edge.field_validation_need),
        "source_basis": list(edge.source_basis),
        "claim_boundary": edge.claim_boundary,
        "properties": edge.properties,
    }


def _evidence_weight(entry: KnowledgeEntry) -> float:
    stage = entry.evidence_stage.lower()
    if "field" in stage:
        return 1.0
    if "literature" in stage and ("simulation" in stage or "synthetic" in stage):
        return 0.82
    if "literature" in stage:
        return 0.72
    if "simulation" in stage or "synthetic" in stage:
        return 0.64
    return 0.48


def _claim_boundary(entry: KnowledgeEntry) -> str:
    stage = entry.evidence_stage.lower()
    if "field" in stage:
        return "field-supported candidate; still requires provenance and acceptance gate audit"
    if "literature" in stage and ("simulation" in stage or "synthetic" in stage):
        return "literature-informed simulation edge; may constrain reasoning but cannot prove field effect"
    if "literature" in stage:
        return "literature hypothesis; requires simulation and field validation"
    if "simulation" in stage or "synthetic" in stage:
        return "simulation-only edge; usable for interface tests, not field claims"
    return "hypothesis-only edge; cannot drive control writeback"
