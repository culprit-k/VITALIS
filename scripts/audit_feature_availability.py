#!/usr/bin/env python3
"""Compare finite-value feature availability across local VITALIS feature caches.

Only aggregate counts and rates are written. Raw records, group identifiers, and
row-level values must remain local and outside version control.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def audit_cache(cache_dir: Path, chunk_rows: int = 50_000) -> dict:
    """Return feature finite counts/rates after checking cache metadata and shapes."""
    if chunk_rows < 1:
        raise ValueError("chunk_rows must be positive")
    meta_path = cache_dir / "meta.json"
    x_path = cache_dir / "X.npy"
    if not meta_path.is_file() or not x_path.is_file():
        raise ValueError(f"{cache_dir} must contain meta.json and X.npy")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    columns = meta.get("columns")
    rows = meta.get("row_count")
    if not isinstance(columns, list) or not columns or not isinstance(rows, int) or rows < 1:
        raise ValueError(f"invalid cache metadata in {meta_path}")
    X = np.load(x_path, mmap_mode="r", allow_pickle=False)
    if X.ndim != 2 or X.shape != (rows, len(columns)):
        raise ValueError(f"feature matrix shape {X.shape} does not match metadata {(rows, len(columns))}")
    if len(set(columns)) != len(columns):
        raise ValueError("feature column names must be unique")

    finite_counts = np.zeros(len(columns), dtype=np.int64)
    for start in range(0, rows, chunk_rows):
        block = X[start : min(start + chunk_rows, rows)]
        finite_counts += np.isfinite(block).sum(axis=0, dtype=np.int64)
    features = {
        name: {
            "finite_rows": int(count),
            "finite_rate": float(count / rows),
        }
        for name, count in zip(columns, finite_counts)
    }
    return {
        "rows": rows,
        "feature_columns": len(columns),
        "features": features,
    }


def compare_caches(set_a: dict, set_b: dict, threshold: float = 0.05) -> dict:
    """Compare availability rates; this is descriptive, not feature selection."""
    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be between 0 and 1")
    if set_a["features"].keys() != set_b["features"].keys():
        raise ValueError("Set A and Set B feature schemas differ")
    shifts = []
    a_only_missing, b_only_missing = [], []
    for feature in set_a["features"]:
        a = set_a["features"][feature]
        b = set_b["features"][feature]
        delta = b["finite_rate"] - a["finite_rate"]
        if a["finite_rows"] == 0 and b["finite_rows"] > 0:
            a_only_missing.append(feature)
        if b["finite_rows"] == 0 and a["finite_rows"] > 0:
            b_only_missing.append(feature)
        if abs(delta) >= threshold:
            shifts.append({
                "feature": feature,
                "set_a_finite_rows": a["finite_rows"],
                "set_b_finite_rows": b["finite_rows"],
                "set_a_finite_rate": a["finite_rate"],
                "set_b_finite_rate": b["finite_rate"],
                "set_b_minus_a_rate": delta,
            })
    shifts.sort(key=lambda item: (-abs(item["set_b_minus_a_rate"]), item["feature"]))
    return {
        "threshold_absolute_rate_difference": threshold,
        "set_a": {k: v for k, v in set_a.items() if k != "features"},
        "set_b": {k: v for k, v in set_b.items() if k != "features"},
        "features_all_missing_in_A_but_observed_in_B": a_only_missing,
        "features_all_missing_in_B_but_observed_in_A": b_only_missing,
        "features_over_threshold": shifts,
        "feature_availability_only": True,
        "model_fitted": False,
        "set_b_used_for_tuning": False,
        "row_level_data_exported": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--set-a-cache", type=Path, required=True)
    parser.add_argument("--set-b-cache", type=Path, required=True)
    parser.add_argument("--threshold", type=float, default=0.05,
                        help="Absolute finite-rate difference threshold (default: 0.05)")
    parser.add_argument("--chunk-rows", type=int, default=50_000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.chunk_rows < 1:
        parser.error("--chunk-rows must be positive")
    if not 0 <= args.threshold <= 1:
        parser.error("--threshold must be between 0 and 1")
    try:
        a = audit_cache(args.set_a_cache, args.chunk_rows)
        b = audit_cache(args.set_b_cache, args.chunk_rows)
        result = compare_caches(a, b, args.threshold)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"Audited {a['feature_columns']} features across {a['rows']:,} Set-A rows "
        f"and {b['rows']:,} Set-B rows; {len(result['features_over_threshold'])} "
        f"features meet the {args.threshold:.1%} absolute-rate threshold."
    )


if __name__ == "__main__":
    main()
