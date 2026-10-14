"""Run a deterministic synthetic-data demonstration of the adaptive twin.

No real patient data are read or generated. The script illustrates software flow
only; its values and outputs have no clinical meaning.
"""
from __future__ import annotations

import argparse
import json
import random

from vitalis.adaptive_twin import AdaptivePhysiologicalTwin, TwinConfig


def synthetic_stream(seed: int = 2026):
    rng = random.Random(seed)
    for step in range(36):
        drift = max(0, step - 23)
        yield {
            "heart_rate": rng.gauss(74 + 2.0 * drift, 2.0),
            "spo2": rng.gauss(98 - 0.45 * drift, 0.35),
            "respiratory_rate": rng.gauss(15 + 0.7 * drift, 1.0),
            "systolic_bp": rng.gauss(122 - 1.5 * drift, 3.0),
            "temperature": rng.gauss(36.8 + 0.06 * drift, 0.08),
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()
    twin = AdaptivePhysiologicalTwin(
        config=TwinConfig(min_history=5, history_window=24, min_channels=2, min_systems=2)
    )
    for step, observation in enumerate(synthetic_stream(args.seed), start=1):
        result = twin.update(observation)
        print(json.dumps({
            "step": step,
            "state": result["state"],
            "coverage": round(float(result["coverage"]), 3),
            "trajectory_score": (
                None if result["trajectory_score"] is None
                else round(float(result["trajectory_score"]), 4)
            ),
            "cross_system_concordance": result["cross_system_concordance"],
        }, sort_keys=True))
    print(json.dumps({
        "notice": "Synthetic demonstration only; not a clinical forecast or patient-care tool."
    }))


if __name__ == "__main__":
    main()
