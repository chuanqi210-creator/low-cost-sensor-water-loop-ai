from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.data_quality_agent import DataQualityAgent
from water_ai.agents.mechanism_agent import MechanismAgent
from water_ai.agents.soft_sensor_agent import SoftSensorAgent
from water_ai.simulation import generate_low_cost_sensor_stream


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "outputs" / "agent3_mechanism"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    readings = generate_low_cost_sensor_stream(n=72, seed=7, inject_faults=True)
    dq_report = DataQualityAgent().run(readings)
    soft_report = SoftSensorAgent(data_quality_report=dq_report).run(readings)
    report = MechanismAgent(data_quality_report=dq_report, soft_sensor_report=soft_report).run(readings)

    payload = {
        "agent_name": report.agent_name,
        "confidence": report.confidence,
        "summary": report.summary,
        "metrics": report.metrics,
        "recommendations": report.recommendations,
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
    }
    (OUT_DIR / "agent3_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Agent 3 机理解释模拟报告",
        "",
        f"- Agent: `{report.agent_name}`",
        f"- 解释可信度: `{report.confidence}`",
        f"- 摘要: {report.summary}",
        "",
        "## 机理假设排序",
        "",
    ]
    for h in report.metrics["ranked_hypotheses"]:
        lines.extend(
            [
                f"### {h['mechanism']}（score={h['score']}）",
                "",
                f"- 解释: {h['explanation']}",
                f"- 行动提示: {h['action_hint']}",
                f"- 证据: `{h['evidence']}`",
                "",
            ]
        )
    lines.extend(["## 知识库命中", ""])
    for match in report.metrics.get("knowledge_matches", []):
        lines.extend(
            [
                f"### {match['entry_id']}（score={match['match_score']}）",
                "",
                f"- 污染物场景: {match['pollutant_class']}",
                f"- 材料/工艺族: {match['material_family']}",
                f"- 机制标签: `{match['mechanism_tags']}`",
                f"- 支持规则: `{match['supports_rules']}`",
                f"- 解释: {match['explanation']}",
                f"- 行动提示: {match['action_hint']}",
                "",
            ]
        )
    lines.extend(["## 建议", ""])
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    (OUT_DIR / "agent3_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(report.summary)
    print(f"wrote {OUT_DIR / 'agent3_report.md'}")


if __name__ == "__main__":
    main()
