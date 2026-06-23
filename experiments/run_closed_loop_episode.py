from __future__ import annotations

import json
from pathlib import Path

from water_ai.closed_loop import run_closed_loop_episode


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "outputs" / "closed_loop"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    scenarios = ["sensor_faults", "oxidant_limitation", "reaction_time_insufficient", "catalyst_deactivation", "matrix_shock"]
    results = {scenario: [step.__dict__ for step in run_closed_loop_episode(initial_scenario=scenario)] for scenario in scenarios}
    (OUT_DIR / "closed_loop_episodes.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = ["# 多轮闭环执行仿真", ""]
    for scenario, steps in results.items():
        lines.extend([f"## {scenario}", ""])
        for step in steps:
            lines.extend(
                [
                    f"### Step {step['step_id']} / {step['scenario']}",
                    "",
                    f"- summary: {step['summary']}",
                    f"- strategy profile: `{step['strategy_profile']}`",
                    f"- state: `{step['state']}`",
                    f"- final actions: `{step['final_actions']}`",
                    f"- blocked: `{step['blocked_actions']}`",
                    f"- next scenario: `{step['next_scenario']}`",
                    "",
                ]
            )
    (OUT_DIR / "closed_loop_episodes.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(f"{scenario}: {steps[-1]['next_scenario'] if steps else None} in {len(steps)} steps" for scenario, steps in results.items()))


if __name__ == "__main__":
    main()
