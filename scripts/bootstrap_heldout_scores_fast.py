#!/usr/bin/env python3
"""Numba-accelerated paired patient-cluster bootstrap for local score archives.

The input NPZ must remain outside the repository and contain only y, groups,
p_static, and p_temporal. Output JSON is aggregate-only; no row-level scores or
bootstrap differences are written.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
from numba import njit


@njit(cache=True)
def weighted_metrics(y, p, order_asc, order_desc, multiplicity, row_group):
    """Compute tie-aware weighted AUROC, average precision, and Brier score."""
    pos_total = 0.0
    neg_total = 0.0
    total_weight = 0.0
    brier_sum = 0.0
    area = 0.0
    neg_before = 0.0
    i = 0
    while i < len(y):
        score = p[order_asc[i]]
        group_pos = 0.0
        group_neg = 0.0
        while i < len(y) and p[order_asc[i]] == score:
            j = order_asc[i]
            weight = multiplicity[row_group[j]]
            if weight:
                total_weight += weight
                delta = p[j] - y[j]
                brier_sum += weight * delta * delta
                if y[j] == 1:
                    group_pos += weight
                    pos_total += weight
                else:
                    group_neg += weight
                    neg_total += weight
            i += 1
        area += group_pos * (neg_before + 0.5 * group_neg)
        neg_before += group_neg
    if pos_total <= 0 or neg_total <= 0 or total_weight <= 0:
        return np.nan, np.nan, np.nan
    auroc = area / (pos_total * neg_total)

    ap = 0.0
    cumulative_pos = 0.0
    cumulative_total = 0.0
    i = 0
    while i < len(y):
        score = p[order_desc[i]]
        group_pos = 0.0
        group_total = 0.0
        while i < len(y) and p[order_desc[i]] == score:
            j = order_desc[i]
            weight = multiplicity[row_group[j]]
            group_pos += weight * y[j]
            group_total += weight
            i += 1
        cumulative_pos += group_pos
        cumulative_total += group_total
        if group_pos > 0 and cumulative_total > 0:
            ap += (group_pos / pos_total) * (cumulative_pos / cumulative_total)
    return auroc, ap, brier_sum / total_weight


def validate_archive_path(path: Path, repository_root: Path) -> Path:
    resolved = path.expanduser().resolve()
    try:
        resolved.relative_to(repository_root.resolve())
    except ValueError:
        return resolved
    raise ValueError("row-level score archives must remain outside the repository")


def run_bootstrap(y, p_static, p_temporal, groups, *, replicates: int, model_seed: int, batch_size: int = 8) -> dict:
    y = np.asarray(y, dtype=np.int8)
    p_static = np.asarray(p_static, dtype=np.float64)
    p_temporal = np.asarray(p_temporal, dtype=np.float64)
    groups = np.asarray(groups)
    if y.ndim != 1 or groups.ndim != 1 or p_static.ndim != 1 or p_temporal.ndim != 1:
        raise ValueError("labels, groups, and probabilities must be one-dimensional")
    if len(y) == 0 or not (len(y) == len(groups) == len(p_static) == len(p_temporal)):
        raise ValueError("labels, groups, and probabilities must be nonempty and aligned")
    if not np.isin(y, [0, 1]).all():
        raise ValueError("labels must be binary")
    for p in (p_static, p_temporal):
        if not np.isfinite(p).all() or np.any((p < 0) | (p > 1)):
            raise ValueError("probabilities must be finite and in [0, 1]")
    if replicates < 20 or batch_size < 1:
        raise ValueError("replicates must be >=20 and batch_size must be >=1")
    unique_groups, row_group = np.unique(groups, return_inverse=True)
    if len(unique_groups) < 2:
        raise ValueError("at least two patient groups are required")
    row_group = row_group.astype(np.int32, copy=False)
    n_groups = len(unique_groups)

    prepared = []
    for p in (p_static, p_temporal):
        prepared.append((p, np.argsort(p, kind="mergesort"), np.argsort(-p, kind="mergesort")))
    rng = np.random.default_rng(model_seed + 90000)
    differences = []
    done = 0
    started = time.time()
    while done < replicates:
        batch = min(batch_size, replicates - done)
        sampled = rng.integers(0, n_groups, size=(batch, n_groups))
        for sample in sampled:
            multiplicity = np.bincount(sample, minlength=n_groups).astype(np.uint16)
            static = weighted_metrics(y, prepared[0][0], prepared[0][1], prepared[0][2], multiplicity, row_group)
            temporal = weighted_metrics(y, prepared[1][0], prepared[1][1], prepared[1][2], multiplicity, row_group)
            if np.isfinite(static).all() and np.isfinite(temporal).all():
                differences.append(np.asarray(temporal) - np.asarray(static))
        done += batch
    values = np.asarray(differences, dtype=np.float64)
    if len(values) < max(20, int(0.8 * replicates)) or not np.isfinite(values).all():
        raise ValueError("too few valid or non-finite bootstrap replicates")
    names = ("auroc", "auprc", "brier_score")
    summary = {
        name: {
            "mean_bootstrap_difference": float(values[:, i].mean()),
            "ci_95_percentile": [float(np.quantile(values[:, i], 0.025)), float(np.quantile(values[:, i], 0.975))],
        }
        for i, name in enumerate(names)
    }
    return {
        "project": "VITALIS",
        "method": "paired patient-cluster percentile bootstrap; Numba-accelerated exact tie-aware weighted AUROC/AP and Brier score",
        "model_split_seed": model_seed,
        "bootstrap_seed": model_seed + 90000,
        "replicates_requested": replicates,
        "replicates_valid": len(values),
        "test_rows": len(y),
        "test_patients": n_groups,
        "positive_hourly_labels": int(y.sum()),
        "temporal_minus_static": summary,
        "elapsed_seconds": time.time() - started,
        "privacy": "Aggregate-only JSON output; local row-level scores and patient groups are never exported.",
        "limitations": [
            "Conditional on the held-out split",
            "Retrospective hourly challenge labels, not clinical event-level outcomes",
            "Input score archive provenance must be verified separately",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scores", type=Path, required=True, help="Local-only NPZ with y, groups, p_static, p_temporal")
    parser.add_argument("--replicates", type=int, default=1000)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--seed", type=int, required=True, help="Original patient split/model seed")
    parser.add_argument("--output", type=Path, required=True, help="Aggregate-only JSON output")
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    try:
        scores_path = validate_archive_path(args.scores, repo_root)
    except ValueError as exc:
        parser.error(str(exc))
    with np.load(scores_path, allow_pickle=False) as data:
        if set(data.files) != {"y", "groups", "p_static", "p_temporal"}:
            parser.error("score archive must contain exactly y, groups, p_static, p_temporal")
        result = run_bootstrap(data["y"], data["p_static"], data["p_temporal"], data["groups"], replicates=args.replicates, model_seed=args.seed, batch_size=args.batch_size)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote aggregate-only output: {args.output}", flush=True)


if __name__ == "__main__":
    main()
