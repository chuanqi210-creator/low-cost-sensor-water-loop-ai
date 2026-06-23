from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt

from water_ai.agents.data_quality_agent import DataQualityAgent
from water_ai.agents.soft_sensor_agent import SoftSensorAgent
from water_ai.simulation import generate_low_cost_sensor_stream


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "outputs" / "agent2_soft_sensor"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    readings = generate_low_cost_sensor_stream(n=72, seed=7, inject_faults=True)
    dq_report = DataQualityAgent().run(readings)
    report = SoftSensorAgent(data_quality_report=dq_report).run(readings)

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
    (OUT_DIR / "agent2_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    timeseries = report.metrics["timeseries"]
    with (OUT_DIR / "soft_state_timeseries.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(timeseries[0]))
        writer.writeheader()
        writer.writerows(timeseries)

    plt.figure(figsize=(8, 4.2))
    plt.plot([p["timestamp_min"] for p in timeseries], [p["pollutant_residual_risk"] for p in timeseries], label="residual risk")
    plt.plot([p["timestamp_min"] for p in timeseries], [p["reaction_completion"] for p in timeseries], label="reaction completion")
    plt.xlabel("time (min)")
    plt.ylabel("estimated state")
    plt.ylim(0, 1)
    plt.grid(alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_DIR / "soft_state_plot.png", dpi=160)
    plt.close()

    lines = [
        "# Agent 2 软传感器模拟报告",
        "",
        f"- Agent: `{report.agent_name}`",
        f"- 估计可信度: `{report.confidence}`",
        f"- 摘要: {report.summary}",
        "",
        "## 隐藏状态估计",
        "",
    ]
    for k, v in report.metrics["state_estimate"].items():
        lines.append(f"- {k}: {v}")
    lines.extend(["", "## 合成真值校验", ""])
    for k, v in report.metrics["synthetic_truth_validation"].items():
        lines.append(f"- {k}: {v}")
    lines.extend(["", "## 建议", ""])
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    lines.extend(["", "## 状态问题", ""])
    for issue in report.issues:
        lines.append(f"- [{issue.severity.value}] {issue.issue_type}: {issue.message}")
    (OUT_DIR / "agent2_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(report.summary)
    print(f"wrote {OUT_DIR / 'agent2_report.md'}")


if __name__ == "__main__":
    main()
