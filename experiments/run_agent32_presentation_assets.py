from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.presentation_asset_agent import PresentationAssetAgent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
AGENT29_REPORT = PROJECT_ROOT / "outputs" / "agent29_project_synthesis" / "agent29_report.json"
AGENT30_REPORT = PROJECT_ROOT / "outputs" / "agent30_field_data_interface" / "agent30_report.json"
AGENT31_REPORT = PROJECT_ROOT / "outputs" / "agent31_deliverable_organization" / "agent31_report.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent32_presentation_assets"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables"
MANIFEST_PATH = DELIVERABLES_DIR / "manifest.json"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    agent29 = _read_json(AGENT29_REPORT)
    agent30 = _read_json(AGENT30_REPORT)
    agent31 = _read_json(AGENT31_REPORT)
    report = PresentationAssetAgent(
        deliverable_metrics=agent31["deliverable_organization"]["metrics"],
        project_synthesis_metrics=agent29["project_synthesis"]["metrics"],
        field_data_metrics=agent30["field_data_interface"]["metrics"],
    ).run([])

    generated_files = {
        "visual_storyboard": str(DELIVERABLES_DIR / "visual_storyboard.md"),
        "figure_specs": str(DELIVERABLES_DIR / "figure_specs.md"),
        "slide_narrative_script": str(DELIVERABLES_DIR / "slide_narrative_script.md"),
        "project_book_sections": str(DELIVERABLES_DIR / "project_book_sections.md"),
    }
    (DELIVERABLES_DIR / "visual_storyboard.md").write_text(_visual_storyboard_md(report), encoding="utf-8")
    (DELIVERABLES_DIR / "figure_specs.md").write_text(_figure_specs_md(report), encoding="utf-8")
    (DELIVERABLES_DIR / "slide_narrative_script.md").write_text(_script_md(report), encoding="utf-8")
    (DELIVERABLES_DIR / "project_book_sections.md").write_text(_book_sections_md(report), encoding="utf-8")

    payload = {
        "source_reports": {
            "agent29": str(AGENT29_REPORT),
            "agent30": str(AGENT30_REPORT),
            "agent31": str(AGENT31_REPORT),
        },
        "presentation_assets": {
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
    (OUT_DIR / "agent32_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "agent32_report.md").write_text(_report_md(report, generated_files), encoding="utf-8")
    _update_manifest(generated_files)

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent32_report.md'}")
    for path in generated_files.values():
        print(f"wrote {path}")


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _visual_storyboard_md(report) -> str:
    lines = ["# 视觉故事板", ""]
    visuals = {visual["visual_id"]: visual for visual in report.metrics["visual_assets"]}
    for slide in report.metrics["slide_specs"]:
        visual = visuals.get(slide["visual_id"], {})
        lines.extend(
            [
                f"## {slide['slide_id']} {slide['title']}",
                "",
                f"- 页面目的：{slide['purpose']}",
                f"- 视觉素材：`{slide['visual_id']}` {visual.get('title', '')}",
                f"- 讲述重点：{slide['speaker_focus']}",
                "",
            ]
        )
    return "\n".join(lines)


def _figure_specs_md(report) -> str:
    lines = ["# 图表素材规格", ""]
    for visual in report.metrics["visual_assets"]:
        lines.extend([f"## {visual['visual_id']} {visual['title']}", "", f"- 类型：`{visual['type']}`"])
        if visual["type"] == "mermaid":
            lines.extend(["", "```mermaid", visual["mermaid"], "```", ""])
        elif visual["type"] == "timeline":
            for milestone in visual["milestones"]:
                lines.append(f"- {milestone}")
            lines.append("")
        else:
            for item in visual.get("content", []):
                lines.append(f"- {item}")
            lines.append("")
    return "\n".join(lines)


def _script_md(report) -> str:
    lines = ["# 逐页讲述脚本", ""]
    for item in report.metrics["narrative_script"]:
        lines.extend([f"## {item['slide_id']}", "", item["speaker_note"], ""])
    return "\n".join(lines)


def _book_sections_md(report) -> str:
    lines = ["# 项目书章节素材", ""]
    for section in report.metrics["project_book_sections"]:
        lines.extend(
            [
                f"## {section['section']}",
                "",
                f"- 建议使用图表：{', '.join(str(item) for item in section['include_assets'])}",
                f"- 必须表达：{section['must_say']}",
                "",
            ]
        )
    return "\n".join(lines)


def _report_md(report, generated_files: dict[str, str]) -> str:
    readiness = report.metrics["readiness"]
    lines = [
        "# Agent 32 图表与汇报素材报告",
        "",
        f"- summary: {report.summary}",
        f"- asset_status: `{readiness['asset_status']}`",
        f"- asset_score: `{readiness['asset_score']}`",
        f"- slide_count: `{readiness['slide_count']}`",
        f"- visual_asset_count: `{readiness['visual_asset_count']}`",
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
    manifest["status"] = "整理阶段图表素材已生成"
    manifest["presentation_assets"] = relative_generated
    manifest["next_stage"] = "基于 visual_storyboard.md、figure_specs.md 和 slide_narrative_script.md 制作正式 PPT 或项目书图表"
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
