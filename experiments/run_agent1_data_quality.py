from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.data_quality_agent import DataQualityAgent
from water_ai.simulation import generate_low_cost_sensor_stream


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "outputs" / "agent1_data_quality"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    readings = generate_low_cost_sensor_stream(n=72, seed=7, inject_faults=True)
    agent = DataQualityAgent()
    report = agent.run(readings)

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
                "timestamp_min": issue.timestamp_min,
                "evidence": issue.evidence,
            }
            for issue in report.issues
        ],
    }

    (OUT_DIR / "agent1_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "sensor_stream.json").write_text(
        json.dumps(
            [
                {
                    "timestamp_min": r.timestamp_min,
                    "cycle_id": r.cycle_id,
                    "values": r.values,
                    "ground_truth_faults": r.ground_truth_faults,
                }
                for r in readings
            ],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    lines = [
        "# Agent 1 数据质控模拟报告",
        "",
        f"- Agent: `{report.agent_name}`",
        f"- 传感可信度: `{report.confidence}`",
        f"- 摘要: {report.summary}",
        "",
        "## 指标",
        "",
    ]
    for k, v in report.metrics.items():
        lines.append(f"- {k}: {v}")
    lines.extend(["", "## 建议", ""])
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    lines.extend(["", "## 传感通道可信权重", ""])
    for sensor, score in report.metrics["sensor_scores"].items():
        lines.append(f"- {sensor}: {score}")
    lines.extend(["", "## 前 12 个问题", ""])
    for issue in report.issues[:12]:
        lines.append(f"- [{issue.severity.value}] {issue.sensor} / {issue.issue_type}: {issue.message}")
    (OUT_DIR / "agent1_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(report.summary)
    print(f"wrote {OUT_DIR / 'agent1_report.md'}")


if __name__ == "__main__":
    main()
