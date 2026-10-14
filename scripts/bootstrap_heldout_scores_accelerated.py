#!/usr/bin/env python3
"""Accelerated paired patient-cluster bootstrap for local held-out score archives.

Requires the optional accelerated-bootstrap dependency extra. Input NPZ files
and optional per-replicate difference archives must remain outside the repository.
Only aggregate JSON results should be committed.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
from numba import njit


@njit(cache=True)
def weighted_metrics(y, probability, order_asc, order_desc, multiplicity, row_group):
    """Exact tie-aware weighted AUROC, average precision, and Brier score."""
    n = len(y)
    positive_total = 0.0
    negative_total = 0.0
    total_weight = 0.0
    brier_sum = 0.0
    area = 0.0
    negative_before = 0.0
    i = 0
    while i < n:
        score = probability[order_asc[i]]
        group_positive = 0.0
        group_negative = 0.0
        while i < n and probability[order_asc[i]] == score:
            j = order_asc[i]
            weight = multiplicity[row_group[j]]
            if weight:
                total_weight += weight
                error = probability[j] - y[j]
                brier_sum += weight * error * error
                if y[j] == 1:
                    group_positive += weight
                    positive_total += weight
                else:
                    group_negative += weight
                    negative_total += weight
            i += 1
        area += group_positive * (negative_before + 0.5 * group_negative)
        negative_before += group_negative
    if positive_total <= 0 or negative_total <= 0 or total_weight <= 0:
        return np.nan, np.nan, np.nan
    auroc = area / (positive_total * negative_total)

    average_precision = 0.0
    cumulative_positive = 0.0
    cumulative_total = 0.0
    i = 0
    while i < n:
        score = probability[order_desc[i]]
        group_positive = 0.0
        group_total = 0.0
        while i < n and probability[order_desc[i]] == score:
            j = order_desc[i]
            weight = multiplicity[row_group[j]]
            group_positive += weight * y[j]
            group_total += weight
            i += 1
        cumulative_positive += group_positive
        cumulative_total += group_total
        if group_positive > 0 and cumulative_total > 0:
            average_precision += (group_positive / positive_total) * (
                cumulative_positive / cumulative_total
            )
    return auroc, average_precision, brier_sum / total_weight


def validate_external_path(path: Path, repository_root: Path) -> Path:
    """Resolve a local-only artifact path and reject paths inside the repository."""
    resolved = path.expanduser().resolve()
    root = repository_root.resolve()
    if resolved == root or root in resolved.parents:
        raise ValueError("local score artifacts must be stored outside the repository")
    return resolved


def run_bootstrap(
    scores_path: Path,
    replicates: int,
    model_seed: int,
    output_path: Path,
    *,
    offset: int = 0,
    private_differences_output: Path | None = None,
) -> dict:
    """Run a deterministic chunk of paired patient-cluster replicates."""
    if replicates < 20:
        raise ValueError("replicates must be >=20")
    if offset < 0:
        raise ValueError("offset must be nonnegative")
    repository_root = Path(__file__).resolve().parents[1]
    scores_path = validate_external_path(scores_path, repository_root)
    if private_differences_output is not None:
        private_differences_output = validate_external_path(
            private_differences_output, repository_root
        )

    started = time.time()
    with np.load(scores_path, allow_pickle=False) as data:
        required = {"y", "groups", "p_static", "p_temporal"}
        if not required.issubset(data.files):
            raise ValueError("score archive is missing required arrays")
        y = np.asarray(data["y"], dtype=np.int8)
        groups = np.asarray(data["groups"])
        p_static = np.asarray(data["p_static"], dtype=np.float64)
        p_temporal = np.asarray(data["p_temporal"], dtype=np.float64)

    if y.ndim != 1 or not np.isin(y, [0, 1]).all():
        raise ValueError("labels must be a one-dimensional binary vector")
    if not (len(y) == len(groups) == len(p_static) == len(p_temporal)):
        raise ValueError("labels, groups, and score vectors must have equal lengths")
    for probability in (p_static, p_temporal):
        if probability.ndim != 1 or not np.isfinite(probability).all():
            raise ValueError("probabilities must be finite one-dimensional vectors")
        if np.any((probability < 0) | (probability > 1)):
            raise ValueError("probabilities must be in [0, 1]")

    unique_groups, row_group = np.unique(groups, return_inverse=True)
    row_group = row_group.astype(np.int32, copy=False)
    group_count = len(unique_groups)
    if group_count < 2:
        raise ValueError("at least two patient groups are required")

    static_order_asc = np.argsort(p_static, kind="mergesort")
    static_order_desc = np.argsort(-p_static, kind="mergesort")
    temporal_order_asc = np.argsort(p_temporal, kind="mergesort")
    temporal_order_desc = np.argsort(-p_temporal, kind="mergesort")

    rng = np.random.default_rng(model_seed + 90000)
    skipped = offset
    while skipped > 0:
        skip_batch = min(8, skipped)
        rng.integers(0, group_count, size=(skip_batch, group_count))
        skipped -= skip_batch

    differences = []
    completed = 0
    batch_size = 8
    while completed < replicates:
        batch = min(batch_size, replicates - completed)
        sampled_groups = rng.integers(0, group_count, size=(batch, group_count))
        for sample in sampled_groups:
            multiplicity = np.bincount(sample, minlength=group_count).astype(np.uint16)
            static_metrics = weighted_metrics(
                y, p_static, static_order_asc, static_order_desc, multiplicity, row_group
            )
            temporal_metrics = weighted_metrics(
                y, p_temporal, temporal_order_asc, temporal_order_desc,
                multiplicity, row_group,
            )
            if np.isfinite(static_metrics).all() and np.isfinite(temporal_metrics).all():
                differences.append(np.asarray(temporal_metrics) - np.asarray(static_metrics))
        completed += batch
        if completed % 100 == 0 or completed == replicates:
            print(
                f"seed={model_seed} completed={completed}/{replicates} "
                f"elapsed={time.time() - started:.1f}s",
                flush=True,
            )

    values = np.asarray(differences, dtype=np.float64)
    if len(values) < max(20, int(0.8 * replicates)) or not np.isfinite(values).all():
        raise ValueError("too few valid or non-finite bootstrap replicates")
    names = ("auroc", "auprc", "brier_score")
    summary = {
        name: {
            "mean_bootstrap_difference": float(values[:, i].mean()),
            "ci_95_percentile": [
                float(np.quantile(values[:, i], 0.025)),
                float(np.quantile(values[:, i], 0.975)),
            ],
        }
        for i, name in enumerate(names)
    }
    result = {
        "project": "VITALIS",
        "method": "paired patient-cluster percentile bootstrap; Numba-accelerated exact tie-aware weighted AUROC/AP",
        "model_split_seed": model_seed,
        "bootstrap_seed": model_seed + 90000,
        "replicates_requested": replicates,
        "replicate_offset": offset,
        "replicates_valid": len(values),
        "test_rows": len(y),
        "test_patients": group_count,
        "positive_hourly_labels": int(y.sum()),
        "temporal_minus_static": summary,
        "elapsed_seconds": time.time() - started,
        "privacy": "Aggregate JSON only; row-level score archives and optional per-replicate differences stay local.",
        "limitations": [
            "Conditional on the held-out split",
            "Retrospective hourly challenge labels, not clinical event-level outcomes",
            "The script does not verify provenance of supplied local score vectors",
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if private_differences_output is not None:
        np.savez_compressed(private_differences_output, differences=values)
    print(f"Wrote aggregate-only output: {output_path}", flush=True)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scores", type=Path, required=True)
    parser.add_argument("--replicates", type=int, default=1000)
    parser.add_argument("--seed", type=int, required=True, help="Original model split seed")
    parser.add_argument("--output", type=Path, required=True, help="Aggregate-only JSON output")
    parser.add_argument("--offset", type=int, default=0, help="Replicate offset for deterministic chunking")
    parser.add_argument(
        "--private-differences-output",
        type=Path,
        default=None,
        help="Optional per-replicate metric differences; must be outside the repository",
    )
    args = parser.parse_args()
    try:
        run_bootstrap(
            args.scores,
            args.replicates,
            args.seed,
            args.output,
            offset=args.offset,
            private_differences_output=args.private_differences_output,
        )
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
