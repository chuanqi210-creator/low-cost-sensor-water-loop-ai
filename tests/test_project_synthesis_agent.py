from water_ai.agents.project_synthesis_agent import ProjectSynthesisAgent


def test_project_synthesis_agent_groups_full_chain() -> None:
    report = ProjectSynthesisAgent(
        synthesized_agent_count=28,
        latest_control_metrics=_latest_control_metrics(stable=True),
        milestone_reports=_milestone_reports(),
        latest_regression="120 passed",
    ).run([])

    metrics = report.metrics
    readiness = metrics["readiness_assessment"]

    assert metrics["synthesized_agent_count"] == 28
    assert len(metrics["module_groups"]) == 7
    assert len(metrics["evidence_chain"]) == 6
    assert readiness["prototype_chain_complete"] is True
    assert readiness["latest_control_stable"] is True
    assert readiness["maturity_level"] == "research_platform_ready_for_field_calibration"
    assert "恢复在线控制" in metrics["project_mermaid"]
    assert "真实数据校准路线" in metrics["project_mermaid"]
    assert report.issues[0].issue_type == "field_validation_missing"


def test_project_synthesis_agent_preserves_recovery_control_state() -> None:
    report = ProjectSynthesisAgent(
        latest_control_metrics=_latest_control_metrics(stable=True),
        milestone_reports=_milestone_reports(),
        latest_regression="120 passed",
    ).run([])

    latest = report.metrics["latest_control_state"]
    evidence = report.metrics["evidence_chain"][-1]

    assert latest["recovery_control_mode"] == "maintain_conditional_recovery"
    assert latest["next_intake_fraction"] == 0.75
    assert latest["fallback_intake_fraction"] == 0.6
    assert evidence["metrics"]["replan_required"] is False
    assert "0.60 回退线" in report.recommendations[-1]


def test_project_synthesis_agent_flags_unstable_latest_control() -> None:
    report = ProjectSynthesisAgent(
        latest_control_metrics=_latest_control_metrics(stable=False),
        milestone_reports=_milestone_reports(),
    ).run([])

    readiness = report.metrics["readiness_assessment"]

    assert readiness["latest_control_stable"] is False
    assert readiness["maturity_level"] == "prototype_requires_more_internal_iteration"
    assert [issue.issue_type for issue in report.issues] == [
        "field_validation_missing",
        "latest_control_not_stable",
    ]


def _latest_control_metrics(*, stable: bool) -> dict[str, object]:
    return {
        "adjusted_control_state": {
            "recovery_control_mode": "maintain_conditional_recovery" if stable else "fallback_to_safe_fraction",
            "next_intake_fraction": 0.75 if stable else 0.6,
            "fallback_intake_fraction": 0.6,
            "replan_required": not stable,
            "bottleneck_ids": [] if stable else ["campaign_time_budget"],
        },
        "recovery_campaign_update": {
            "acceptance_passed": stable,
            "validation_staff_usage": 0.394,
            "time_budget_usage": 0.884 if stable else 0.94,
            "bottleneck_ids": [] if stable else ["campaign_time_budget"],
        },
    }


def _milestone_reports() -> dict[str, object]:
    return {
        "agent23": {
            "post_replan_replay": {
                "metrics": {
                    "comparison": {
                        "verdict": "validated",
                        "validation_usage_before": 1.406,
                        "validation_usage_after": 0.337,
                        "time_usage_before": 1.188,
                        "time_usage_after": 0.755,
                        "removed_bottlenecks": [
                            "campaign_time_budget",
                            "catalyst_inventory",
                            "validation_capacity",
                        ],
                    }
                }
            }
        },
        "agent25": {
            "time_budget_recovery": {
                "metrics": {
                    "selected_candidate": {
                        "candidate_id": "stagger_validation_overlap",
                        "target_intake_fraction": 0.75,
                        "time_budget_usage": 0.884,
                        "validation_staff_usage": 0.394,
                        "elapsed_reduction_min": 90.2,
                    }
                }
            }
        },
        "agent27": {
            "recovery_execution_replay": {
                "metrics": {
                    "comparison": {
                        "replay_verdict": "recovery_execution_validated",
                        "time_usage_without_strategy": 0.978,
                        "time_usage_with_strategy": 0.884,
                        "strategy_bottleneck_ids": [],
                        "recommended_next_intake_fraction": 0.75,
                    }
                }
            }
        },
    }
