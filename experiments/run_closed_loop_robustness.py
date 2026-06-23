from __future__ import annotations

import json
from pathlib import Path

from water_ai.robustness import evaluate_closed_loop_robustness


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "outputs" / "closed_loop_robustness"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    result = evaluate_closed_loop_robustness(seeds=range(30), max_steps=6)
    (OUT_DIR / "closed_loop_robustness.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = ["# 多随机种子闭环鲁棒性评估", ""]
    lines.extend(["## 场景汇总", ""])
    for summary in result["scenario_summaries"]:
        lines.extend(
            [
                f"### {summary['scenario']}",
                "",
                f"- runs: `{summary['runs']}`",
                f"- success_rate: `{summary['success_rate']}`",
                f"- mean_steps: `{summary['mean_steps']}`",
                f"- mean_elapsed_min: `{summary['mean_elapsed_min']}`",
                f"- mean_cost: `{summary['mean_cost']}`",
                f"- mean_energy: `{summary['mean_energy']}`",
                f"- failures: `{len(summary['failures'])}`",
                "",
            ]
        )
    lines.extend(["## 失败样本", ""])
    failures = [failure for summary in result["scenario_summaries"] for failure in summary["failures"]]
    if not failures:
        lines.append("未发现失败样本。")
    else:
        for failure in failures:
            lines.append(f"- `{failure}`")
    (OUT_DIR / "closed_loop_robustness.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n".join(f"{item['scenario']}: success_rate={item['success_rate']} mean_steps={item['mean_steps']}" for item in result["scenario_summaries"]))


if __name__ == "__main__":
    main()
