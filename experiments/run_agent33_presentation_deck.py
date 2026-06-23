from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.presentation_deck_agent import PresentationDeckAgent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
AGENT32_REPORT = PROJECT_ROOT / "outputs" / "agent32_presentation_assets" / "agent32_report.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent33_presentation_deck"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables"
MANIFEST_PATH = DELIVERABLES_DIR / "manifest.json"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    agent32 = _read_json(AGENT32_REPORT)
    metrics = agent32["presentation_assets"]["metrics"]
    output_targets = {
        "pptx": "deliverables/ppt/low_cost_water_ai_formal_deck.pptx",
        "claim_spine": "deliverables/deck_claim_spine.md",
        "design_system": "deliverables/deck_design_system.md",
        "qa_checklist": "deliverables/deck_qa_checklist.md",
    }
    report = PresentationDeckAgent(
        presentation_asset_metrics=metrics,
        output_targets=output_targets,
    ).run([])

    (DELIVERABLES_DIR / "deck_claim_spine.md").write_text(_claim_spine_md(report), encoding="utf-8")
    (DELIVERABLES_DIR / "deck_design_system.md").write_text(_design_system_md(report), encoding="utf-8")
    (DELIVERABLES_DIR / "deck_qa_checklist.md").write_text(_qa_checklist_md(report), encoding="utf-8")

    generated_files = {
        "claim_spine": str(DELIVERABLES_DIR / "deck_claim_spine.md"),
        "design_system": str(DELIVERABLES_DIR / "deck_design_system.md"),
        "qa_checklist": str(DELIVERABLES_DIR / "deck_qa_checklist.md"),
        "pptx": str(PROJECT_ROOT / output_targets["pptx"]),
    }
    payload = {
        "source_reports": {"agent32": str(AGENT32_REPORT)},
        "presentation_deck": {
            "agent_name": report.agent_name,
            "confidence": report.confidence,
            "summary": report.summary,
            "recommendations": report.recommendations,
            "metrics": report.metrics,
            "issues": [
                {
                    "sensor": issue.sensor,
                    "issue_type": issue.issue_type,
                    "severity": issue.severity.value,
                    "message": issue.message,
                    "evidence": issue.evidence,
                }
                for issue in report.issues
            ],
        },
        "generated_files": generated_files,
    }
    (OUT_DIR / "agent33_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "agent33_report.md").write_text(_report_md(report, generated_files), encoding="utf-8")
    _update_manifest(generated_files)

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent33_report.md'}")
    for key, path in generated_files.items():
        print(f"{key}: {path}")


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _claim_spine_md(report) -> str:
    lines = ["# 正式汇报 Claim Spine", ""]
    for slide in report.metrics["deck_plan"]:
        lines.extend(
            [
                f"## {slide['slide_id']} {slide['title']}",
                "",
                f"- 主张：{slide['claim']}",
                f"- 证据对象：{slide['proof_object']}",
                f"- 版式：`{slide['layout']}`",
                f"- 必须保留：{', '.join(str(item) for item in slide['must_keep']) or '无'}",
                f"- 页脚口径：{slide['footer_evidence']}",
                "",
            ]
        )
    return "\n".join(lines)


def _design_system_md(report) -> str:
    design = report.metrics["design_system"]
    font_policy = design["font_policy"]
    palette = design["palette"]
    lines = [
        "# 正式 PPT 设计系统",
        "",
        f"- 任务模式：`{design['task_mode']}`",
        f"- Deck profile：`{design['deck_profile']}`",
        f"- 画布：{design['canvas']}",
        "",
        "## 字体策略",
        "",
        f"- 中文主字体：`{font_policy['primary_cjk']}`",
        f"- Mac 备用：`{font_policy['mac_fallback']}`",
        f"- 西文/数字：`{font_policy['latin']}`",
        f"- 原因：{font_policy['reason']}",
        "",
        "## 调色板",
        "",
    ]
    for key, value in palette.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## 版式规则", ""])
    for rule in design["layout_rules"]:
        lines.append(f"- {rule}")
    return "\n".join(lines)


def _qa_checklist_md(report) -> str:
    lines = ["# PPTX QA 检查清单", ""]
    for gate in report.metrics["qa_gates"]:
        lines.append(f"- `{gate['gate']}`：{gate['requirement']}")
    return "\n".join(lines)


def _report_md(report, generated_files: dict[str, str]) -> str:
    readiness = report.metrics["readiness"]
    lines = [
        "# Agent 33 正式展示包规划报告",
        "",
        f"- summary: {report.summary}",
        f"- deck_status: `{readiness['deck_status']}`",
        f"- deck_score: `{readiness['deck_score']}`",
        f"- slide_count: `{readiness['slide_count']}`",
        f"- qa_gate_count: `{readiness['qa_gate_count']}`",
        "",
        "## 生成文件",
        "",
    ]
    for key, path in generated_files.items():
        lines.append(f"- {key}: `{path}`")
    lines.extend(["", "## 建议", ""])
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    lines.extend(["", "## 风险边界", ""])
    for issue in report.issues:
        lines.append(f"- `{issue.issue_type}`：{issue.message}")
    return "\n".join(lines)


def _update_manifest(generated_files: dict[str, str]) -> None:
    manifest = _read_json(MANIFEST_PATH)
    relative_generated = {
        key: str(Path(path).relative_to(PROJECT_ROOT))
        for key, path in generated_files.items()
    }
    manifest["status"] = "整理阶段正式 PPTX 已生成"
    manifest["formal_deck"] = relative_generated
    manifest["next_stage"] = "用 deck_qa_checklist.md 对正式 PPTX 做中文字体、边界说明和布局复核，再进入真实现场数据导入与校准"
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
