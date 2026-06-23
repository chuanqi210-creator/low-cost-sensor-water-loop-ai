from water_ai.agents.deliverable_organization_agent import DeliverableOrganizationAgent


def test_deliverable_organization_agent_builds_ready_pack() -> None:
    report = DeliverableOrganizationAgent(
        manifest=_manifest(),
        project_synthesis_metrics=_project_metrics(),
        field_data_metrics=_field_metrics(),
        artifact_existence={path: True for path in _all_paths()},
        latest_regression="127 passed",
    ).run([])

    readiness = report.metrics["readiness"]
    core = report.metrics["core_metrics"]

    assert readiness["deliverable_status"] == "deliverable_pack_ready"
    assert core["total_agent_chain_count"] == 31
    assert len(report.metrics["presentation_outline"]) == 8
    assert report.metrics["presentation_outline"][0]["title"].startswith("研究缘起")
    assert report.metrics["presentation_outline"][-1]["title"] == "下一步实证校准"
    assert any(issue.issue_type == "field_validation_not_completed" for issue in report.issues)


def test_deliverable_organization_agent_flags_missing_artifacts() -> None:
    existence = {path: True for path in _all_paths()}
    existence["outputs/agent30_field_data_interface/agent30_report.md"] = False

    report = DeliverableOrganizationAgent(
        manifest=_manifest(),
        project_synthesis_metrics=_project_metrics(),
        field_data_metrics=_field_metrics(),
        artifact_existence=existence,
    ).run([])

    readiness = report.metrics["readiness"]

    assert readiness["deliverable_status"] == "deliverable_pack_needs_minor_patch"
    assert "outputs/agent30_field_data_interface/agent30_report.md" in readiness["missing_artifacts"]
    assert report.issues[0].issue_type == "deliverable_artifact_missing"


def test_deliverable_organization_agent_preserves_recovery_boundary_metric() -> None:
    report = DeliverableOrganizationAgent(
        manifest=_manifest(),
        project_synthesis_metrics=_project_metrics(),
        field_data_metrics=_field_metrics(),
        artifact_existence={path: True for path in _all_paths()},
    ).run([])

    metrics = {row["metric"]: row for row in report.metrics["key_metrics_table"]}

    assert metrics["next_intake_fraction"]["value"] == 0.75
    assert metrics["fallback_intake_fraction"]["value"] == 0.6
    assert "条件恢复" in metrics["next_intake_fraction"]["interpretation"]


def test_deliverable_organization_agent_counts_presentation_layer_when_available() -> None:
    manifest = _manifest_with_presentation_assets()
    report = DeliverableOrganizationAgent(
        manifest=manifest,
        project_synthesis_metrics=_project_metrics(),
        field_data_metrics=_field_metrics(),
        artifact_existence={path: True for path in _paths_from_manifest(manifest)},
    ).run([])

    core = report.metrics["core_metrics"]
    metrics = {row["metric"]: row for row in report.metrics["key_metrics_table"]}

    assert core["total_agent_chain_count"] == 32
    assert core["organizing_interface_agent_count"] == 4
    assert metrics["agent_chain_count"]["value"] == 32
    assert "4 个综合、接口、整理、展示素材 agent" in metrics["agent_chain_count"]["interpretation"]
    assert report.metrics["presentation_outline"][2]["evidence"][0] == "total_agent_chain_count=32"


def test_deliverable_organization_agent_indexes_formal_deck_outputs() -> None:
    manifest = _manifest_with_formal_deck()
    report = DeliverableOrganizationAgent(
        manifest=manifest,
        project_synthesis_metrics=_project_metrics(),
        field_data_metrics=_field_metrics(),
        artifact_existence={path: True for path in _paths_from_manifest(manifest)},
    ).run([])

    core = report.metrics["core_metrics"]
    formal_deck_entries = [
        item for item in report.metrics["artifact_index"] if item["category"] == "formal_deck"
    ]

    assert core["total_agent_chain_count"] == 33
    assert core["organizing_interface_agent_count"] == 5
    assert len(formal_deck_entries) == 4
    assert all(item["role"] == "正式 PPT 与展示 QA 交付" for item in formal_deck_entries)


def test_deliverable_organization_agent_indexes_field_calibration_gate_outputs() -> None:
    manifest = _manifest_with_field_calibration_gate()
    report = DeliverableOrganizationAgent(
        manifest=manifest,
        project_synthesis_metrics=_project_metrics(),
        field_data_metrics=_field_metrics(),
        artifact_existence={path: True for path in _paths_from_manifest(manifest)},
    ).run([])

    core = report.metrics["core_metrics"]
    field_gate_entries = [
        item for item in report.metrics["artifact_index"] if item["category"] == "field_calibration_gate"
    ]

    assert core["total_agent_chain_count"] == 34
    assert core["organizing_interface_agent_count"] == 6
    assert core["support_layer_label"].endswith("校准门控")
    assert len(field_gate_entries) == 4
    assert all(item["role"] == "现场校准门控与运行手册" for item in field_gate_entries)


def test_deliverable_organization_agent_indexes_model_realism_audit_outputs() -> None:
    manifest = _manifest_with_model_realism_audit()
    report = DeliverableOrganizationAgent(
        manifest=manifest,
        project_synthesis_metrics=_project_metrics(),
        field_data_metrics=_field_metrics(),
        artifact_existence={path: True for path in _paths_from_manifest(manifest)},
    ).run([])

    core = report.metrics["core_metrics"]
    audit_entries = [
        item for item in report.metrics["artifact_index"] if item["category"] == "model_realism_audit"
    ]

    assert core["total_agent_chain_count"] == 35
    assert core["organizing_interface_agent_count"] == 7
    assert core["support_layer_label"].endswith("模型真实性审计")
    assert len(audit_entries) == 3
    assert all(item["role"] == "模型真实性审计与优化路线" for item in audit_entries)


def test_deliverable_organization_agent_indexes_soft_sensor_uncertainty_outputs() -> None:
    manifest = _manifest_with_soft_sensor_uncertainty()
    report = DeliverableOrganizationAgent(
        manifest=manifest,
        project_synthesis_metrics=_project_metrics(),
        field_data_metrics=_field_metrics(),
        artifact_existence={path: True for path in _paths_from_manifest(manifest)},
    ).run([])

    core = report.metrics["core_metrics"]
    entries = [
        item for item in report.metrics["artifact_index"] if item["category"] == "soft_sensor_uncertainty"
    ]

    assert core["total_agent_chain_count"] == 36
    assert core["organizing_interface_agent_count"] == 8
    assert core["support_layer_label"].endswith("软传感不确定性验证")
    assert len(entries) == 3
    assert all(item["role"] == "软传感不确定性验证" for item in entries)


def test_deliverable_organization_agent_indexes_knowledge_graph_curation_outputs() -> None:
    manifest = _manifest_with_knowledge_graph_curation()
    report = DeliverableOrganizationAgent(
        manifest=manifest,
        project_synthesis_metrics=_project_metrics(),
        field_data_metrics=_field_metrics(),
        artifact_existence={path: True for path in _paths_from_manifest(manifest)},
    ).run([])

    core = report.metrics["core_metrics"]
    entries = [
        item for item in report.metrics["artifact_index"] if item["category"] == "knowledge_graph_curation"
    ]

    assert core["total_agent_chain_count"] == 37
    assert core["organizing_interface_agent_count"] == 9
    assert core["support_layer_label"].endswith("知识图谱策展")
    assert len(entries) == 4
    assert all(item["role"] == "知识图谱策展与证据矩阵" for item in entries)


def test_deliverable_organization_agent_indexes_literature_evidence_outputs() -> None:
    manifest = _manifest_with_literature_evidence()
    report = DeliverableOrganizationAgent(
        manifest=manifest,
        project_synthesis_metrics=_project_metrics(),
        field_data_metrics=_field_metrics(),
        artifact_existence={path: True for path in _paths_from_manifest(manifest)},
    ).run([])

    core = report.metrics["core_metrics"]
    entries = [
        item for item in report.metrics["artifact_index"] if item["category"] == "literature_evidence"
    ]

    assert core["total_agent_chain_count"] == 38
    assert core["organizing_interface_agent_count"] == 10
    assert core["support_layer_label"].endswith("文献证据抽取")
    assert len(entries) == 4
    assert all(item["role"] == "文献证据抽取与模型升级映射" for item in entries)


def test_deliverable_organization_agent_indexes_conformal_calibration_outputs() -> None:
    manifest = _manifest_with_conformal_calibration()
    report = DeliverableOrganizationAgent(
        manifest=manifest,
        project_synthesis_metrics=_project_metrics(),
        field_data_metrics=_field_metrics(),
        artifact_existence={path: True for path in _paths_from_manifest(manifest)},
    ).run([])

    core = report.metrics["core_metrics"]
    entries = [
        item for item in report.metrics["artifact_index"] if item["category"] == "soft_sensor_conformal_calibration"
    ]

    assert core["total_agent_chain_count"] == 39
    assert core["organizing_interface_agent_count"] == 11
    assert core["support_layer_label"].endswith("软传感保形校准")
    assert len(entries) == 3
    assert all(item["role"] == "软传感保形校准接口" for item in entries)


def test_deliverable_organization_agent_indexes_grey_box_dynamic_latency_outputs() -> None:
    manifest = _manifest_with_grey_box_dynamic_latency()
    report = DeliverableOrganizationAgent(
        manifest=manifest,
        project_synthesis_metrics=_project_metrics(),
        field_data_metrics=_field_metrics(),
        artifact_existence={path: True for path in _paths_from_manifest(manifest)},
    ).run([])

    core = report.metrics["core_metrics"]
    entries = [
        item for item in report.metrics["artifact_index"] if item["category"] == "grey_box_dynamic_latency"
    ]

    assert core["total_agent_chain_count"] == 40
    assert core["organizing_interface_agent_count"] == 12
    assert core["support_layer_label"].endswith("灰箱动态延迟审计")
    assert len(entries) == 3
    assert all(item["role"] == "灰箱动态延迟审计" for item in entries)


def test_deliverable_organization_agent_indexes_matrix_shock_fast_proxy_outputs() -> None:
    manifest = _manifest_with_matrix_shock_fast_proxy()
    report = DeliverableOrganizationAgent(
        manifest=manifest,
        project_synthesis_metrics=_project_metrics(),
        field_data_metrics=_field_metrics(),
        artifact_existence={path: True for path in _paths_from_manifest(manifest)},
    ).run([])

    core = report.metrics["core_metrics"]
    entries = [
        item for item in report.metrics["artifact_index"] if item["category"] == "matrix_shock_fast_proxy_control"
    ]

    assert core["total_agent_chain_count"] == 41
    assert core["organizing_interface_agent_count"] == 13
    assert core["support_layer_label"].endswith("基质冲击快代理控制")
    assert len(entries) == 3
    assert all(item["role"] == "基质冲击快代理与延迟感知控制" for item in entries)


def test_deliverable_organization_agent_indexes_timestamped_replay_outputs() -> None:
    manifest = _manifest_with_timestamped_campaign_replay()
    report = DeliverableOrganizationAgent(
        manifest=manifest,
        project_synthesis_metrics=_project_metrics(),
        field_data_metrics=_field_metrics(),
        artifact_existence={path: True for path in _paths_from_manifest(manifest)},
    ).run([])

    core = report.metrics["core_metrics"]
    entries = [
        item for item in report.metrics["artifact_index"] if item["category"] == "timestamped_campaign_replay"
    ]

    assert core["total_agent_chain_count"] == 42
    assert core["organizing_interface_agent_count"] == 14
    assert core["support_layer_label"].endswith("时间戳回放接口")
    assert len(entries) == 5
    assert all(item["role"] == "现场时间戳回放接口" for item in entries)


def test_deliverable_organization_agent_indexes_field_replay_calibration_gate_outputs() -> None:
    manifest = _manifest_with_field_replay_calibration_gate()
    report = DeliverableOrganizationAgent(
        manifest=manifest,
        project_synthesis_metrics=_project_metrics(),
        field_data_metrics=_field_metrics(),
        artifact_existence={path: True for path in _paths_from_manifest(manifest)},
    ).run([])

    core = report.metrics["core_metrics"]
    entries = [
        item for item in report.metrics["artifact_index"] if item["category"] == "field_replay_calibration_gate"
    ]
    tasks = {task["task_id"]: task for task in report.metrics["calibration_task_board"]}

    assert core["total_agent_chain_count"] == 43
    assert core["organizing_interface_agent_count"] == 15
    assert core["support_layer_label"].endswith("现场回放校准门控")
    assert len(entries) == 3
    assert all(item["role"] == "现场回放校准门控" for item in entries)
    assert tasks["P6_timestamped_fast_proxy_replay"]["current_status"] == "field_replay_required"


def test_deliverable_organization_agent_indexes_field_replay_import_outputs() -> None:
    manifest = _manifest_with_field_replay_import()
    report = DeliverableOrganizationAgent(
        manifest=manifest,
        project_synthesis_metrics=_project_metrics(),
        field_data_metrics=_field_metrics(),
        artifact_existence={path: True for path in _paths_from_manifest(manifest)},
    ).run([])

    core = report.metrics["core_metrics"]
    entries = [
        item for item in report.metrics["artifact_index"] if item["category"] == "field_replay_import"
    ]
    tasks = {task["task_id"]: task for task in report.metrics["calibration_task_board"]}

    assert core["total_agent_chain_count"] == 44
    assert core["organizing_interface_agent_count"] == 16
    assert core["support_layer_label"].endswith("现场 replay 导入门")
    assert len(entries) == 5
    assert all(item["role"] == "现场 replay 包导入与 provenance 验收" for item in entries)
    assert tasks["P7_field_replay_import_package"]["current_status"] == "field_package_required"


def test_deliverable_organization_agent_indexes_field_replay_evidence_chain_outputs() -> None:
    manifest = _manifest_with_field_replay_evidence_chain()
    report = DeliverableOrganizationAgent(
        manifest=manifest,
        project_synthesis_metrics=_project_metrics(),
        field_data_metrics=_field_metrics(),
        artifact_existence={path: True for path in _paths_from_manifest(manifest)},
    ).run([])

    core = report.metrics["core_metrics"]
    entries = [
        item for item in report.metrics["artifact_index"] if item["category"] == "field_replay_evidence_chain"
    ]
    tasks = {task["task_id"]: task for task in report.metrics["calibration_task_board"]}

    assert core["total_agent_chain_count"] == 45
    assert core["organizing_interface_agent_count"] == 17
    assert core["support_layer_label"].endswith("现场 replay 证据链")
    assert len(entries) == 3
    assert all(item["role"] == "现场 replay 校准证据链" for item in entries)
    assert tasks["P8_field_replay_evidence_chain"]["current_status"] == "evidence_chain_waiting_for_field_package"


def test_deliverable_organization_agent_indexes_soft_sensor_field_holdout_gate_outputs() -> None:
    manifest = _manifest_with_soft_sensor_field_holdout_gate()
    report = DeliverableOrganizationAgent(
        manifest=manifest,
        project_synthesis_metrics=_project_metrics(),
        field_data_metrics=_field_metrics(),
        artifact_existence={path: True for path in _paths_from_manifest(manifest)},
    ).run([])

    core = report.metrics["core_metrics"]
    entries = [
        item for item in report.metrics["artifact_index"] if item["category"] == "soft_sensor_field_holdout_gate"
    ]
    tasks = {task["task_id"]: task for task in report.metrics["calibration_task_board"]}

    assert core["total_agent_chain_count"] == 46
    assert core["organizing_interface_agent_count"] == 18
    assert core["support_layer_label"].endswith("软传感 field holdout 放行门控")
    assert len(entries) == 3
    assert all(item["role"] == "软传感 field holdout 放行门控" for item in entries)
    assert tasks["P9_soft_sensor_field_holdout_gate"]["current_status"] == "field_holdout_required"


def test_deliverable_organization_agent_indexes_weak_target_stratified_conformal_outputs() -> None:
    manifest = _manifest_with_weak_target_stratified_conformal()
    report = DeliverableOrganizationAgent(
        manifest=manifest,
        project_synthesis_metrics=_project_metrics(),
        field_data_metrics=_field_metrics(),
        artifact_existence={path: True for path in _paths_from_manifest(manifest)},
    ).run([])

    core = report.metrics["core_metrics"]
    entries = [
        item for item in report.metrics["artifact_index"] if item["category"] == "weak_target_stratified_conformal"
    ]
    tasks = {task["task_id"]: task for task in report.metrics["calibration_task_board"]}

    assert core["total_agent_chain_count"] == 47
    assert core["organizing_interface_agent_count"] == 19
    assert core["support_layer_label"].endswith("弱目标分层保形校准")
    assert len(entries) == 3
    assert all(item["role"] == "弱目标分层保形校准" for item in entries)
    assert tasks["P10_weak_target_stratified_conformal"]["current_status"] == "field_holdout_required"


def test_deliverable_organization_agent_indexes_sensor_network_sparse_placement_outputs() -> None:
    manifest = _manifest_with_sensor_network_sparse_placement()
    report = DeliverableOrganizationAgent(
        manifest=manifest,
        project_synthesis_metrics=_project_metrics(),
        field_data_metrics=_field_metrics(),
        artifact_existence={path: True for path in _paths_from_manifest(manifest)},
    ).run([])

    core = report.metrics["core_metrics"]
    entries = [
        item for item in report.metrics["artifact_index"] if item["category"] == "sensor_network_sparse_placement"
    ]
    tasks = {task["task_id"]: task for task in report.metrics["calibration_task_board"]}

    assert core["total_agent_chain_count"] == 48
    assert core["organizing_interface_agent_count"] == 20
    assert core["support_layer_label"].endswith("管网布点与稀疏感知")
    assert len(entries) == 3
    assert all(item["role"] == "管网布点与稀疏感知" for item in entries)
    assert tasks["P11_sensor_network_sparse_placement"]["current_status"] == "field_topology_required"


def test_deliverable_organization_agent_indexes_multi_facility_collaborative_control_outputs() -> None:
    manifest = _manifest_with_multi_facility_collaborative_control()
    report = DeliverableOrganizationAgent(
        manifest=manifest,
        project_synthesis_metrics=_project_metrics(),
        field_data_metrics=_field_metrics(),
        artifact_existence={path: True for path in _paths_from_manifest(manifest)},
    ).run([])

    core = report.metrics["core_metrics"]
    entries = [
        item for item in report.metrics["artifact_index"] if item["category"] == "multi_facility_collaborative_control"
    ]
    tasks = {task["task_id"]: task for task in report.metrics["calibration_task_board"]}

    assert core["total_agent_chain_count"] == 49
    assert core["organizing_interface_agent_count"] == 21
    assert core["support_layer_label"].endswith("多设施协同控制")
    assert len(entries) == 3
    assert all(item["role"] == "多设施协同控制与策略蒸馏" for item in entries)
    assert tasks["P12_multi_facility_collaborative_control"]["current_status"] == "field_coordination_replay_required"


def test_deliverable_organization_agent_indexes_model_core_optimization_governance_outputs() -> None:
    manifest = _manifest_with_model_core_optimization_governance()
    report = DeliverableOrganizationAgent(
        manifest=manifest,
        project_synthesis_metrics=_project_metrics(),
        field_data_metrics=_field_metrics(),
        artifact_existence={path: True for path in _paths_from_manifest(manifest)},
    ).run([])

    core = report.metrics["core_metrics"]
    entries = [
        item for item in report.metrics["artifact_index"] if item["category"] == "model_core_optimization_governance"
    ]
    tasks = {task["task_id"]: task for task in report.metrics["calibration_task_board"]}

    assert core["total_agent_chain_count"] == 50
    assert core["organizing_interface_agent_count"] == 22
    assert core["support_layer_label"].endswith("模型核心优化治理")
    assert len(entries) == 14
    assert any(item["path"].endswith("goal_iteration_trace.md") for item in entries)
    assert any(item["path"].endswith("core_interface_consolidation.json") for item in entries)
    assert any(item["path"].endswith("core_interface_consolidation.md") for item in entries)
    assert any(item["path"].endswith("grey_box_submission_readiness_gate.json") for item in entries)
    assert any(item["path"].endswith("grey_box_submission_readiness_gate.md") for item in entries)
    assert all(item["role"] == "全局系统架构治理与模型核心优化" for item in entries)
    assert tasks["P13_model_core_optimization_governance"]["current_status"] == "active_model_core_governance"
    assert tasks["P13_model_core_optimization_governance"]["title"] == "全局系统架构治理与模型核心优化"


def test_deliverable_organization_agent_indexes_catalyst_activity_proxy_outputs() -> None:
    manifest = _manifest_with_catalyst_activity_proxy()
    report = DeliverableOrganizationAgent(
        manifest=manifest,
        project_synthesis_metrics=_project_metrics(),
        field_data_metrics=_field_metrics(),
        artifact_existence={path: True for path in _paths_from_manifest(manifest)},
    ).run([])

    core = report.metrics["core_metrics"]
    entries = [
        item for item in report.metrics["artifact_index"] if item["category"] == "catalyst_activity_proxy"
    ]
    tasks = {task["task_id"]: task for task in report.metrics["calibration_task_board"]}

    assert core["total_agent_chain_count"] == 51
    assert core["organizing_interface_agent_count"] == 23
    assert core["support_layer_label"].endswith("催化剂活性代理观测")
    assert len(entries) == 3
    assert all(item["role"] == "催化剂活性代理观测" for item in entries)
    assert tasks["P14_catalyst_activity_proxy"]["current_status"] == "field_proxy_holdout_required"


def test_deliverable_organization_agent_indexes_multi_facility_replay_evaluation_outputs() -> None:
    manifest = _manifest_with_multi_facility_replay_evaluation()
    report = DeliverableOrganizationAgent(
        manifest=manifest,
        project_synthesis_metrics=_project_metrics(),
        field_data_metrics=_field_metrics(),
        artifact_existence={path: True for path in _paths_from_manifest(manifest)},
    ).run([])

    core = report.metrics["core_metrics"]
    entries = [
        item for item in report.metrics["artifact_index"] if item["category"] == "multi_facility_replay_evaluation"
    ]
    tasks = {task["task_id"]: task for task in report.metrics["calibration_task_board"]}

    assert core["total_agent_chain_count"] == 52
    assert core["organizing_interface_agent_count"] == 24
    assert core["support_layer_label"].endswith("多设施 replay 离线评估")
    assert len(entries) == 3
    assert all(item["role"] == "多设施 replay 离线评估" for item in entries)
    assert tasks["P15_multi_facility_replay_evaluation"]["current_status"] == "field_multinode_replay_required"


def test_deliverable_organization_agent_indexes_minimal_grey_box_physics_outputs() -> None:
    manifest = _manifest_with_minimal_grey_box_physics()
    report = DeliverableOrganizationAgent(
        manifest=manifest,
        project_synthesis_metrics=_project_metrics(),
        field_data_metrics=_field_metrics(),
        artifact_existence={path: True for path in _paths_from_manifest(manifest)},
    ).run([])

    core = report.metrics["core_metrics"]
    entries = [
        item for item in report.metrics["artifact_index"] if item["category"] == "minimal_grey_box_physics"
    ]
    tasks = {task["task_id"]: task for task in report.metrics["calibration_task_board"]}

    assert core["total_agent_chain_count"] == 53
    assert core["organizing_interface_agent_count"] == 25
    assert core["support_layer_label"].endswith("最小灰箱物理机制")
    assert len(entries) == 3
    assert all(item["role"] == "最小灰箱物理机制增强" for item in entries)
    assert tasks["P16_minimal_grey_box_physics"]["current_status"] == "field_physics_calibration_required"


def test_deliverable_organization_agent_indexes_soft_sensor_matrix_coupling_outputs() -> None:
    manifest = _manifest_with_soft_sensor_matrix_coupling()
    report = DeliverableOrganizationAgent(
        manifest=manifest,
        project_synthesis_metrics=_project_metrics(),
        field_data_metrics=_field_metrics(),
        artifact_existence={path: True for path in _paths_from_manifest(manifest)},
    ).run([])

    core = report.metrics["core_metrics"]
    entries = [
        item for item in report.metrics["artifact_index"] if item["category"] == "soft_sensor_matrix_coupling"
    ]
    tasks = {task["task_id"]: task for task in report.metrics["calibration_task_board"]}

    assert core["total_agent_chain_count"] == 54
    assert core["organizing_interface_agent_count"] == 26
    assert core["support_layer_label"].endswith("软传感矩阵耦合")
    assert len(entries) == 3
    assert all(item["role"] == "软传感矩阵耦合" for item in entries)
    assert tasks["P17_soft_sensor_matrix_coupling"]["current_status"] == "field_missingness_replay_required"


def _manifest() -> dict[str, object]:
    return {
        "core_documents": [
            "docs/研究方案_Word兼容版.docx",
            "docs/agent_system_spec.md",
            "docs/project_overview_28_agent.md",
            "docs/field_data_interface_spec.md",
        ],
        "key_reports": [
            "outputs/agent29_project_synthesis/agent29_report.md",
            "outputs/agent30_field_data_interface/agent30_report.md",
        ],
        "field_data_interface": {
            "schema": "outputs/agent30_field_data_interface/field_data_schema.json",
            "templates": "outputs/agent30_field_data_interface/field_data_templates/",
            "synthetic_sample_package": "outputs/agent30_field_data_interface/synthetic_field_data_package/",
        },
    }


def _manifest_with_presentation_assets() -> dict[str, object]:
    manifest = _manifest()
    manifest["presentation_assets"] = {
        "visual_storyboard": "deliverables/visual_storyboard.md",
        "figure_specs": "deliverables/figure_specs.md",
        "slide_narrative_script": "deliverables/slide_narrative_script.md",
        "project_book_sections": "deliverables/project_book_sections.md",
    }
    return manifest


def _manifest_with_formal_deck() -> dict[str, object]:
    manifest = _manifest_with_presentation_assets()
    manifest["formal_deck"] = {
        "claim_spine": "deliverables/deck_claim_spine.md",
        "design_system": "deliverables/deck_design_system.md",
        "qa_checklist": "deliverables/deck_qa_checklist.md",
        "pptx": "deliverables/ppt/low_cost_water_ai_formal_deck.pptx",
    }
    return manifest


def _manifest_with_field_calibration_gate() -> dict[str, object]:
    manifest = _manifest_with_formal_deck()
    manifest["field_calibration_gate"] = {
        "calibration_protocol": "deliverables/field_calibration_protocol.md",
        "acceptance_gates": "deliverables/field_data_acceptance_gates.md",
        "calibration_runbook": "deliverables/field_calibration_runbook.md",
        "agent34_report": "outputs/agent34_field_calibration_gate/agent34_report.md",
    }
    return manifest


def _manifest_with_model_realism_audit() -> dict[str, object]:
    manifest = _manifest_with_field_calibration_gate()
    manifest["model_realism_audit"] = {
        "model_realism_audit": "deliverables/model_realism_audit.md",
        "model_upgrade_backlog": "deliverables/model_upgrade_backlog.md",
        "agent35_report": "outputs/agent35_model_realism_audit/agent35_report.md",
    }
    return manifest


def _manifest_with_soft_sensor_uncertainty() -> dict[str, object]:
    manifest = _manifest_with_model_realism_audit()
    manifest["soft_sensor_uncertainty"] = {
        "soft_sensor_uncertainty_validation": "deliverables/soft_sensor_uncertainty_validation.md",
        "agent36_report": "outputs/agent36_soft_sensor_uncertainty_validation/agent36_report.md",
        "uncertainty_metrics": "outputs/soft_sensor_training/soft_sensor_uncertainty_metrics.json",
    }
    return manifest


def _manifest_with_knowledge_graph_curation() -> dict[str, object]:
    manifest = _manifest_with_soft_sensor_uncertainty()
    manifest["knowledge_graph_curation"] = {
        "knowledge_graph_curation": "deliverables/knowledge_graph_curation.md",
        "knowledge_graph_schema": "deliverables/knowledge_graph_schema.md",
        "agent37_report": "outputs/agent37_knowledge_graph_curation/agent37_report.md",
        "knowledge_graph_records": "outputs/agent37_knowledge_graph_curation/knowledge_graph_records.json",
    }
    return manifest


def _manifest_with_literature_evidence() -> dict[str, object]:
    manifest = _manifest_with_knowledge_graph_curation()
    manifest["literature_evidence"] = {
        "literature_evidence_matrix": "deliverables/literature_evidence_matrix.md",
        "literature_evidence_schema": "deliverables/literature_evidence_schema.md",
        "agent38_report": "outputs/agent38_literature_evidence/agent38_report.md",
        "literature_evidence_records": "outputs/agent38_literature_evidence/literature_evidence_records.json",
    }
    return manifest


def _manifest_with_conformal_calibration() -> dict[str, object]:
    manifest = _manifest_with_literature_evidence()
    manifest["soft_sensor_conformal_calibration"] = {
        "soft_sensor_conformal_calibration": "deliverables/soft_sensor_conformal_calibration.md",
        "agent39_report": "outputs/agent39_soft_sensor_conformal_calibration/agent39_report.md",
        "conformal_metrics": "outputs/soft_sensor_training/soft_sensor_conformal_metrics.json",
    }
    return manifest


def _manifest_with_grey_box_dynamic_latency() -> dict[str, object]:
    manifest = _manifest_with_conformal_calibration()
    manifest["grey_box_dynamic_latency"] = {
        "grey_box_dynamic_latency": "deliverables/grey_box_dynamic_latency.md",
        "agent40_report": "outputs/agent40_grey_box_dynamic_latency/agent40_report.md",
        "latency_budget_metrics": "outputs/grey_box_dynamic_latency/latency_budget_metrics.json",
    }
    return manifest


def _manifest_with_matrix_shock_fast_proxy() -> dict[str, object]:
    manifest = _manifest_with_grey_box_dynamic_latency()
    manifest["matrix_shock_fast_proxy_control"] = {
        "matrix_shock_fast_proxy_control": "deliverables/matrix_shock_fast_proxy_control.md",
        "agent41_report": "outputs/agent41_matrix_shock_fast_proxy/agent41_report.md",
        "fast_proxy_metrics": "outputs/matrix_shock_fast_proxy/fast_proxy_metrics.json",
    }
    return manifest


def _manifest_with_timestamped_campaign_replay() -> dict[str, object]:
    manifest = _manifest_with_matrix_shock_fast_proxy()
    manifest["timestamped_campaign_replay"] = {
        "timestamped_campaign_replay_schema": "deliverables/timestamped_campaign_replay_schema.md",
        "agent42_report": "outputs/agent42_timestamped_campaign_replay/agent42_report.md",
        "timestamped_replay_schema_json": "outputs/timestamped_campaign_replay/timestamped_replay_schema.json",
        "timestamped_replay_templates": "outputs/timestamped_campaign_replay/templates",
        "synthetic_timestamped_replay_package": "outputs/timestamped_campaign_replay/synthetic_timestamped_replay",
    }
    return manifest


def _manifest_with_field_replay_calibration_gate() -> dict[str, object]:
    manifest = _manifest_with_timestamped_campaign_replay()
    manifest["field_replay_calibration_gate"] = {
        "field_replay_calibration_gate": "deliverables/field_replay_calibration_gate.md",
        "agent43_report": "outputs/agent43_field_replay_calibration_gate/agent43_report.md",
        "g6_p6_gate_metrics": "outputs/field_replay_calibration_gate/g6_p6_gate_metrics.json",
    }
    return manifest


def _manifest_with_field_replay_import() -> dict[str, object]:
    manifest = _manifest_with_field_replay_calibration_gate()
    manifest["field_replay_import"] = {
        "field_replay_import_protocol": "deliverables/field_replay_import_protocol.md",
        "agent44_report": "outputs/agent44_field_replay_import/agent44_report.md",
        "import_acceptance_metrics": "outputs/field_replay_import/import_acceptance_metrics.json",
        "import_schema": "outputs/field_replay_import/import_schema.json",
        "synthetic_replay_import_package": "outputs/field_replay_import/synthetic_replay_import_package",
    }
    return manifest


def _manifest_with_field_replay_evidence_chain() -> dict[str, object]:
    manifest = _manifest_with_field_replay_import()
    manifest["field_replay_evidence_chain"] = {
        "field_replay_evidence_chain": "deliverables/field_replay_evidence_chain.md",
        "agent45_report": "outputs/agent45_field_replay_evidence_chain/agent45_report.md",
        "evidence_chain_metrics": "outputs/field_replay_evidence_chain/evidence_chain_metrics.json",
    }
    return manifest


def _manifest_with_soft_sensor_field_holdout_gate() -> dict[str, object]:
    manifest = _manifest_with_field_replay_evidence_chain()
    manifest["soft_sensor_field_holdout_gate"] = {
        "soft_sensor_field_holdout_gate": "deliverables/soft_sensor_field_holdout_gate.md",
        "agent46_report": "outputs/agent46_soft_sensor_field_holdout_gate/agent46_report.md",
        "field_holdout_gate_metrics": "outputs/soft_sensor_field_holdout_gate/field_holdout_gate_metrics.json",
    }
    return manifest


def _manifest_with_weak_target_stratified_conformal() -> dict[str, object]:
    manifest = _manifest_with_soft_sensor_field_holdout_gate()
    manifest["weak_target_stratified_conformal"] = {
        "weak_target_stratified_conformal": "deliverables/weak_target_stratified_conformal.md",
        "agent47_report": "outputs/agent47_weak_target_stratified_conformal/agent47_report.md",
        "weak_target_stratified_metrics": "outputs/weak_target_stratified_conformal/weak_target_stratified_metrics.json",
    }
    return manifest


def _manifest_with_sensor_network_sparse_placement() -> dict[str, object]:
    manifest = _manifest_with_weak_target_stratified_conformal()
    manifest["sensor_network_sparse_placement"] = {
        "sensor_network_sparse_placement": "deliverables/sensor_network_sparse_placement.md",
        "agent48_report": "outputs/agent48_sensor_network_sparse_placement/agent48_report.md",
        "sparse_placement_metrics": "outputs/sensor_network_sparse_placement/sparse_placement_metrics.json",
    }
    return manifest


def _manifest_with_multi_facility_collaborative_control() -> dict[str, object]:
    manifest = _manifest_with_sensor_network_sparse_placement()
    manifest["multi_facility_collaborative_control"] = {
        "multi_facility_collaborative_control": "deliverables/multi_facility_collaborative_control.md",
        "agent49_report": "outputs/agent49_multi_facility_collaborative_control/agent49_report.md",
        "collaborative_control_metrics": "outputs/multi_facility_collaborative_control/collaborative_control_metrics.json",
    }
    return manifest


def _manifest_with_model_core_optimization_governance() -> dict[str, object]:
    manifest = _manifest_with_multi_facility_collaborative_control()
    manifest["model_core_optimization_governance"] = {
        "model_core_goal": "deliverables/model_core_optimization/model_core_goal.md",
        "goal_iteration_trace": "deliverables/model_core_optimization/goal_iteration_trace.md",
        "user_interrupt_lessons": "deliverables/model_core_optimization/user_interrupt_lessons.md",
        "external_evidence_matrix": "deliverables/model_core_optimization/external_evidence_matrix.md",
        "issue_priority_ranking": "deliverables/model_core_optimization/issue_priority_ranking.md",
        "execution_prompt": "deliverables/model_core_optimization/execution_prompt.md",
        "self_interrupt_checklist": "deliverables/model_core_optimization/self_interrupt_checklist.md",
        "governance_report": "deliverables/model_core_optimization/governance_report.md",
        "agent50_report": "outputs/agent50_model_core_governance/agent50_report.md",
        "priority_ranking": "outputs/model_core_governance/priority_ranking.json",
        "core_interface_consolidation": "outputs/model_core_governance/core_interface_consolidation.json",
        "core_interface_consolidation_report": "deliverables/model_core_optimization/core_interface_consolidation.md",
        "grey_box_submission_readiness_gate": "outputs/grey_box_calibration_package/grey_box_submission_readiness_gate.json",
        "grey_box_submission_readiness_gate_report": "deliverables/model_core_optimization/grey_box_submission_readiness_gate.md",
    }
    return manifest


def _manifest_with_catalyst_activity_proxy() -> dict[str, object]:
    manifest = _manifest_with_model_core_optimization_governance()
    manifest["catalyst_activity_proxy"] = {
        "catalyst_activity_proxy": "deliverables/catalyst_activity_proxy.md",
        "agent51_report": "outputs/agent51_catalyst_activity_proxy/agent51_report.md",
        "catalyst_activity_proxy_metrics": "outputs/catalyst_activity_proxy/catalyst_activity_proxy_metrics.json",
    }
    return manifest


def _manifest_with_multi_facility_replay_evaluation() -> dict[str, object]:
    manifest = _manifest_with_catalyst_activity_proxy()
    manifest["multi_facility_replay_evaluation"] = {
        "multi_facility_replay_evaluation": "deliverables/multi_facility_replay_evaluation.md",
        "agent52_report": "outputs/agent52_multi_facility_replay_evaluation/agent52_report.md",
        "replay_evaluation_metrics": "outputs/multi_facility_replay_evaluation/replay_evaluation_metrics.json",
    }
    return manifest


def _manifest_with_minimal_grey_box_physics() -> dict[str, object]:
    manifest = _manifest_with_multi_facility_replay_evaluation()
    manifest["minimal_grey_box_physics"] = {
        "minimal_grey_box_physics": "deliverables/minimal_grey_box_physics.md",
        "agent53_report": "outputs/agent53_minimal_grey_box_physics/agent53_report.md",
        "grey_box_physics_metrics": "outputs/minimal_grey_box_physics/grey_box_physics_metrics.json",
    }
    return manifest


def _manifest_with_soft_sensor_matrix_coupling() -> dict[str, object]:
    manifest = _manifest_with_minimal_grey_box_physics()
    manifest["soft_sensor_matrix_coupling"] = {
        "soft_sensor_matrix_coupling": "deliverables/soft_sensor_matrix_coupling.md",
        "agent54_report": "outputs/agent54_soft_sensor_matrix_coupling/agent54_report.md",
        "soft_sensor_matrix_metrics": "outputs/soft_sensor_matrix_coupling/soft_sensor_matrix_metrics.json",
    }
    return manifest


def _all_paths() -> list[str]:
    return _paths_from_manifest(_manifest())


def _paths_from_manifest(manifest: dict[str, object]) -> list[str]:
    paths = (
        list(manifest["core_documents"])
        + list(manifest["key_reports"])
        + list(manifest["field_data_interface"].values())
    )
    presentation_assets = manifest.get("presentation_assets", {})
    if isinstance(presentation_assets, dict):
        paths.extend(presentation_assets.values())
    formal_deck = manifest.get("formal_deck", {})
    if isinstance(formal_deck, dict):
        paths.extend(formal_deck.values())
    field_calibration_gate = manifest.get("field_calibration_gate", {})
    if isinstance(field_calibration_gate, dict):
        paths.extend(field_calibration_gate.values())
    model_realism_audit = manifest.get("model_realism_audit", {})
    if isinstance(model_realism_audit, dict):
        paths.extend(model_realism_audit.values())
    soft_sensor_uncertainty = manifest.get("soft_sensor_uncertainty", {})
    if isinstance(soft_sensor_uncertainty, dict):
        paths.extend(soft_sensor_uncertainty.values())
    knowledge_graph_curation = manifest.get("knowledge_graph_curation", {})
    if isinstance(knowledge_graph_curation, dict):
        paths.extend(knowledge_graph_curation.values())
    literature_evidence = manifest.get("literature_evidence", {})
    if isinstance(literature_evidence, dict):
        paths.extend(literature_evidence.values())
    soft_sensor_conformal_calibration = manifest.get("soft_sensor_conformal_calibration", {})
    if isinstance(soft_sensor_conformal_calibration, dict):
        paths.extend(soft_sensor_conformal_calibration.values())
    soft_sensor_field_holdout_gate = manifest.get("soft_sensor_field_holdout_gate", {})
    if isinstance(soft_sensor_field_holdout_gate, dict):
        paths.extend(soft_sensor_field_holdout_gate.values())
    weak_target_stratified_conformal = manifest.get("weak_target_stratified_conformal", {})
    if isinstance(weak_target_stratified_conformal, dict):
        paths.extend(weak_target_stratified_conformal.values())
    sensor_network_sparse_placement = manifest.get("sensor_network_sparse_placement", {})
    if isinstance(sensor_network_sparse_placement, dict):
        paths.extend(sensor_network_sparse_placement.values())
    multi_facility_collaborative_control = manifest.get("multi_facility_collaborative_control", {})
    if isinstance(multi_facility_collaborative_control, dict):
        paths.extend(multi_facility_collaborative_control.values())
    model_core_optimization_governance = manifest.get("model_core_optimization_governance", {})
    if isinstance(model_core_optimization_governance, dict):
        paths.extend(model_core_optimization_governance.values())
    catalyst_activity_proxy = manifest.get("catalyst_activity_proxy", {})
    if isinstance(catalyst_activity_proxy, dict):
        paths.extend(catalyst_activity_proxy.values())
    multi_facility_replay_evaluation = manifest.get("multi_facility_replay_evaluation", {})
    if isinstance(multi_facility_replay_evaluation, dict):
        paths.extend(multi_facility_replay_evaluation.values())
    minimal_grey_box_physics = manifest.get("minimal_grey_box_physics", {})
    if isinstance(minimal_grey_box_physics, dict):
        paths.extend(minimal_grey_box_physics.values())
    soft_sensor_matrix_coupling = manifest.get("soft_sensor_matrix_coupling", {})
    if isinstance(soft_sensor_matrix_coupling, dict):
        paths.extend(soft_sensor_matrix_coupling.values())
    grey_box_dynamic_latency = manifest.get("grey_box_dynamic_latency", {})
    if isinstance(grey_box_dynamic_latency, dict):
        paths.extend(grey_box_dynamic_latency.values())
    matrix_shock_fast_proxy = manifest.get("matrix_shock_fast_proxy_control", {})
    if isinstance(matrix_shock_fast_proxy, dict):
        paths.extend(matrix_shock_fast_proxy.values())
    timestamped_campaign_replay = manifest.get("timestamped_campaign_replay", {})
    if isinstance(timestamped_campaign_replay, dict):
        paths.extend(timestamped_campaign_replay.values())
    field_replay_calibration_gate = manifest.get("field_replay_calibration_gate", {})
    if isinstance(field_replay_calibration_gate, dict):
        paths.extend(field_replay_calibration_gate.values())
    field_replay_import = manifest.get("field_replay_import", {})
    if isinstance(field_replay_import, dict):
        paths.extend(field_replay_import.values())
    field_replay_evidence_chain = manifest.get("field_replay_evidence_chain", {})
    if isinstance(field_replay_evidence_chain, dict):
        paths.extend(field_replay_evidence_chain.values())
    return paths


def _project_metrics() -> dict[str, object]:
    return {
        "synthesized_agent_count": 28,
        "readiness_assessment": {"maturity_level": "research_platform_ready_for_field_calibration"},
        "latest_control_state": {
            "recovery_control_mode": "maintain_conditional_recovery",
            "next_intake_fraction": 0.75,
            "fallback_intake_fraction": 0.6,
            "replan_required": False,
        },
    }


def _field_metrics() -> dict[str, object]:
    return {
        "data_origin": "synthetic",
        "readiness": {"interface_status": "template_ready_not_field_validated"},
        "table_statuses": {
            "sensor_timeseries": {"status": "import_ready"},
            "offline_lab_results": {"status": "import_ready"},
            "catalyst_lifecycle": {"status": "import_ready"},
            "campaign_operation_log": {"status": "import_ready"},
            "cost_deployment": {"status": "import_ready"},
        },
        "calibration_tasks": [
            {"task_id": "P1_sensor_noise_drift", "title": "真实传感器噪声、漂移和污染结垢标定", "task_ready": True, "blockers": []},
            {"task_id": "P2_soft_sensor_retraining", "title": "软传感器真实标签重训", "task_ready": True, "blockers": []},
        ],
    }
