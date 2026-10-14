#!/usr/bin/env python3
"""Batched paired patient-cluster bootstrap from local held-out score vectors.

The NPZ input is a local-only artifact containing labels, patient group indices,
and static/temporal probabilities. The JSON output contains aggregate intervals
only; never commit the NPZ or any row-level scores.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np


def prepare_score_metrics(y_true: np.ndarray, probability: np.ndarray) -> dict:
    """Precompute stable score order and exact tie boundaries once per model."""
    y = np.asarray(y_true, dtype=np.int8)
    p = np.asarray(probability, dtype=np.float64)
    if y.ndim != 1 or p.ndim != 1 or len(y) != len(p) or len(y) == 0:
        raise ValueError("labels and probabilities must be nonempty equal-length vectors")
    if not np.isfinite(p).all() or np.any((p < 0) | (p > 1)):
        raise ValueError("probabilities must be finite and in [0, 1]")
    if not np.isin(y, [0, 1]).all():
        raise ValueError("labels must be binary")

    order_asc = np.argsort(p, kind="mergesort")
    sorted_asc = p[order_asc]
    ends_asc = np.r_[np.flatnonzero(sorted_asc[1:] != sorted_asc[:-1]), len(p) - 1]
    order_desc = np.argsort(-p, kind="mergesort")
    sorted_desc = p[order_desc]
    ends_desc = np.r_[np.flatnonzero(sorted_desc[1:] != sorted_desc[:-1]), len(p) - 1]
    return {
        "y": y,
        "p": p,
        "order_asc": order_asc,
        "ends_asc": ends_asc,
        "order_desc": order_desc,
        "ends_desc": ends_desc,
    }


def _group_differences(cumulative: np.ndarray, ends: np.ndarray) -> np.ndarray:
    """Convert cumulative values at tie-group endpoints to group totals."""
    at_ends = cumulative[:, ends]
    previous = np.zeros_like(at_ends)
    if len(ends) > 1:
        previous[:, 1:] = at_ends[:, :-1]
    return at_ends - previous


def batch_weighted_rank_metrics(prepared: dict, row_weights: np.ndarray) -> np.ndarray | None:
    """Compute exact tie-aware weighted AUROC, AP, and Brier for a batch.

    Returns a (batch, 3) array in AUROC/AP/Brier order, or None if any
    replicate has no positive or no negative weight.
    """
    y = prepared["y"]
    w = np.asarray(row_weights, dtype=np.float64)
    if w.ndim != 2 or w.shape[1] != len(y):
        raise ValueError("row_weights must have shape (batch, number of rows)")
    if np.any(w < 0) or not np.isfinite(w).all():
        raise ValueError("row weights must be finite and nonnegative")
    positive_total = (w * y).sum(axis=1)
    negative_total = (w * (1 - y)).sum(axis=1)
    if np.any(positive_total <= 0) or np.any(negative_total <= 0):
        return None

    # AUROC: each positive receives full credit for lower-scored negatives
    # and half credit for negatives tied at the same score.
    order = prepared["order_asc"]
    sorted_y = y[order]
    sorted_w = w[:, order]
    cumulative_positive = np.cumsum(sorted_w * sorted_y[None, :], axis=1)
    cumulative_total = np.cumsum(sorted_w, axis=1)
    group_positive = _group_differences(cumulative_positive, prepared["ends_asc"])
    group_total = _group_differences(cumulative_total, prepared["ends_asc"])
    group_negative = group_total - group_positive
    negative_before = np.cumsum(group_negative, axis=1) - group_negative
    auroc = np.sum(group_positive * (negative_before + 0.5 * group_negative), axis=1)
    auroc /= positive_total * negative_total

    # Average precision is evaluated at unique descending score thresholds.
    order = prepared["order_desc"]
    sorted_y = y[order]
    sorted_w = w[:, order]
    cumulative_positive = np.cumsum(sorted_w * sorted_y[None, :], axis=1)
    cumulative_total = np.cumsum(sorted_w, axis=1)
    group_positive = _group_differences(cumulative_positive, prepared["ends_desc"])
    cumulative_positive_at_threshold = cumulative_positive[:, prepared["ends_desc"]]
    cumulative_total_at_threshold = cumulative_total[:, prepared["ends_desc"]]
    valid_threshold = cumulative_total_at_threshold > 0
    precision = np.divide(
        cumulative_positive_at_threshold,
        cumulative_total_at_threshold,
        out=np.zeros_like(cumulative_positive_at_threshold),
        where=valid_threshold,
    )
    auprc = np.sum(
        (group_positive / positive_total[:, None]) * precision,
        axis=1,
    )

    brier = np.sum(w * (prepared["p"] - y)[None, :] ** 2, axis=1) / np.sum(w, axis=1)
    return np.column_stack((auroc, auprc, brier))


def run_bootstrap(
    y: np.ndarray,
    p_static: np.ndarray,
    p_temporal: np.ndarray,
    groups: np.ndarray,
    *,
    replicates: int,
    model_seed: int,
    batch_size: int = 8,
) -> dict:
    """Run paired patient-cluster resampling and return aggregate-only results."""
    y = np.asarray(y, dtype=np.int8)
    groups = np.asarray(groups)
    p_static = np.asarray(p_static, dtype=np.float64)
    p_temporal = np.asarray(p_temporal, dtype=np.float64)
    if not (len(y) == len(p_static) == len(p_temporal) == len(groups)):
        raise ValueError("labels, probabilities, and groups must have equal lengths")
    if replicates < 20 or batch_size < 1:
        raise ValueError("replicates must be >=20 and batch_size must be >=1")
    unique_groups, group_index = np.unique(groups, return_inverse=True)
    if len(unique_groups) < 2:
        raise ValueError("at least two patient groups are required")

    static = prepare_score_metrics(y, p_static)
    temporal = prepare_score_metrics(y, p_temporal)
    bootstrap_seed = model_seed + 90000
    rng = np.random.default_rng(bootstrap_seed)
    differences: list[np.ndarray] = []
    done = 0
    started = time.time()
    while done < replicates:
        batch = min(batch_size, replicates - done)
        sampled = rng.integers(0, len(unique_groups), size=(batch, len(unique_groups)))
        multiplicity = np.zeros((batch, len(unique_groups)), dtype=np.uint16)
        for i in range(batch):
            np.add.at(multiplicity[i], sampled[i], 1)
        row_weights = multiplicity[:, group_index].astype(np.float64)
        static_metrics = batch_weighted_rank_metrics(static, row_weights)
        temporal_metrics = batch_weighted_rank_metrics(temporal, row_weights)
        if static_metrics is not None and temporal_metrics is not None:
            differences.extend(temporal_metrics - static_metrics)
        done += batch

    values = np.asarray(differences, dtype=np.float64)
    if len(values) < max(20, int(0.8 * replicates)) or not np.isfinite(values).all():
        raise ValueError("too few valid or non-finite bootstrap replicates")
    metric_names = ("auroc", "auprc", "brier_score")
    summary = {
        name: {
            "mean_bootstrap_difference": float(values[:, i].mean()),
            "ci_95_percentile": [
                float(np.quantile(values[:, i], 0.025)),
                float(np.quantile(values[:, i], 0.975)),
            ],
        }
        for i, name in enumerate(metric_names)
    }
    return {
        "project": "VITALIS",
        "method": "paired patient-cluster percentile bootstrap; batched multiplicity weights; exact tie-aware weighted AUROC/AP",
        "model_split_seed": model_seed,
        "bootstrap_seed": bootstrap_seed,
        "replicates_requested": replicates,
        "replicates_valid": len(values),
        "test_rows": len(y),
        "test_patients": len(unique_groups),
        "positive_hourly_labels": int(y.sum()),
        "temporal_minus_static": summary,
        "elapsed_seconds": time.time() - started,
        "privacy": "Aggregate-only output; row-level score vectors and patient groups are not exported.",
        "limitations": [
            "Conditional on the held-out split",
            "Retrospective hourly challenge labels, not clinical event-level outcomes",
            "This script does not verify provenance of the supplied local score vectors",
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
    with np.load(args.scores, allow_pickle=False) as data:
        required = {"y", "groups", "p_static", "p_temporal"}
        if not required.issubset(data.files):
            parser.error("score archive is missing required arrays")
        result = run_bootstrap(
            data["y"], data["p_static"], data["p_temporal"], data["groups"],
            replicates=args.replicates, model_seed=args.seed, batch_size=args.batch_size,
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote aggregate-only output: {args.output}", flush=True)


if __name__ == "__main__":
    main()
