"""Run a deterministic, patient-sampled, three-model Phase 1 comparison.

Raw PSV files and patient-level predictions remain local. The output contains
aggregate metrics and paired patient-cluster bootstrap intervals only.
"""
from __future__ import annotations

import argparse
import json
import random
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, log_loss, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from scripts.train_baseline import load_patient_rows, observed_training_features


def metric_set(y: np.ndarray, p: np.ndarray) -> dict[str, float | int | None]:
    return {
        "rows": int(len(y)),
        "positive_rows": int(y.sum()),
        "prevalence": float(y.mean()),
        "auroc": float(roc_auc_score(y, p)) if np.unique(y).size == 2 else None,
        "average_precision": float(average_precision_score(y, p)),
        "brier_score": float(brier_score_loss(y, p)),
        "log_loss": float(log_loss(y, p, labels=[0, 1])),
    }


def paired_cluster_bootstrap(
    y: np.ndarray, a: np.ndarray, b: np.ndarray, groups: np.ndarray,
    *, seed: int, replicates: int = 200,
) -> dict[str, dict[str, float | int | None]]:
    frame = pd.DataFrame({"patient": groups, "y": y, "a": a, "b": b})
    by_patient = {k: v for k, v in frame.groupby("patient", sort=True)}
    patient_ids = np.asarray(list(by_patient))
    rng = np.random.default_rng(seed)
    values: dict[str, list[float]] = {
        "auroc": [], "average_precision": [], "brier_score": []
    }
    for _ in range(replicates):
        chosen = rng.choice(patient_ids, size=len(patient_ids), replace=True)
        sample = pd.concat([by_patient[k] for k in chosen], ignore_index=True)
        labels = sample["y"].to_numpy(dtype=int)
        pa = sample["a"].to_numpy(dtype=float)
        pb = sample["b"].to_numpy(dtype=float)
        if np.unique(labels).size == 2:
            values["auroc"].append(roc_auc_score(labels, pb) - roc_auc_score(labels, pa))
            values["average_precision"].append(
                average_precision_score(labels, pb) - average_precision_score(labels, pa)
            )
        values["brier_score"].append(
            brier_score_loss(labels, pb) - brier_score_loss(labels, pa)
        )
    return {
        name: {
            "lower_95": float(np.percentile(vals, 2.5)) if vals else None,
            "upper_95": float(np.percentile(vals, 97.5)) if vals else None,
            "valid_replicates": len(vals),
            "requested_replicates": replicates,
        }
        for name, vals in values.items()
    }


def run(data_dir: Path, sample_size: int, sampling_seed: int,
        split_seeds: list[int], replicates: int) -> dict[str, object]:
    paths = sorted(data_dir.glob("*.psv"))
    if not paths:
        raise FileNotFoundError(f"No .psv files found in {data_dir}")
    if sample_size < 2 or sample_size > len(paths):
        raise ValueError(f"sample_size must be between 2 and {len(paths)}")
    chosen = sorted(random.Random(sampling_seed).sample(paths, sample_size))
    with tempfile.TemporaryDirectory(prefix="vitalis_phase1_") as tmp:
        subset = Path(tmp)
        for i, path in enumerate(chosen):
            (subset / f"patient_{i:06d}.psv").symlink_to(path.resolve())
        matrices = {}
        labels = groups = None
        for name, temporal, personalized in (
            ("static", False, False),
            ("temporal", True, False),
            ("personalized", True, True),
        ):
            X, y, g, _ = load_patient_rows(subset, temporal=temporal, personalized=personalized)
            matrices[name] = X
            if labels is None:
                labels, groups = y.to_numpy(dtype=int), g.to_numpy()
            elif not np.array_equal(labels, y.to_numpy(dtype=int)) or not np.array_equal(
                groups, g.to_numpy()
            ):
                raise RuntimeError("Model variants do not share identical row/label/group order")
        assert labels is not None and groups is not None
        runs = []
        for seed in split_seeds:
            first = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=seed)
            train_val, test = next(first.split(matrices["static"], labels, groups))
            second = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=seed + 1)
            train_rel, val_rel = next(
                second.split(matrices["static"].iloc[train_val], labels[train_val], groups[train_val])
            )
            train, validation = train_val[train_rel], train_val[val_rel]
            patient_sets = [set(groups[ix]) for ix in (train, validation, test)]
            if any(patient_sets[i] & patient_sets[j] for i in range(3) for j in range(i + 1, 3)):
                raise RuntimeError("Patient overlap detected between splits")
            predictions = {}
            model_results = {}
            for name, X in matrices.items():
                observed, dropped = observed_training_features(X.iloc[train])
                model = make_pipeline(
                    SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True),
                    StandardScaler(),
                    LogisticRegression(
                        max_iter=1000, class_weight="balanced", solver="lbfgs", random_state=seed
                    ),
                )
                model.fit(X.iloc[train][observed], labels[train])
                pred = model.predict_proba(X.iloc[test][observed])[:, 1]
                predictions[name] = pred
                model_results[name] = {
                    "features_available": int(X.shape[1]),
                    "features_used": len(observed),
                    "dropped_all_missing_training_features": dropped,
                    "test_metrics": metric_set(labels[test], pred),
                }
            comparisons = {}
            for index, (a, b) in enumerate((
                ("static", "temporal"),
                ("temporal", "personalized"),
                ("static", "personalized"),
            )):
                comparisons[f"{b}_minus_{a}"] = paired_cluster_bootstrap(
                    labels[test], predictions[a], predictions[b], groups[test],
                    seed=seed * 100 + index, replicates=replicates,
                )
            runs.append({
                "seed": seed,
                "validation_seed": seed + 1,
                "patients": {
                    "train": len(patient_sets[0]),
                    "validation": len(patient_sets[1]),
                    "test": len(patient_sets[2]),
                },
                "rows": {
                    "train": int(len(train)),
                    "validation": int(len(validation)),
                    "test": int(len(test)),
                },
                "positive_test_rows": int(labels[test].sum()),
                "models": model_results,
                "paired_patient_cluster_bootstrap_intervals": comparisons,
            })
    return {
        "project": "VITALIS",
        "protocol": {
            "sampled_patients": sample_size,
            "sampling_seed": sampling_seed,
            "split_seeds": split_seeds,
            "split_unit": "patient",
            "bootstrap_replicates": replicates,
            "threshold_selected": False,
            "label_handling": "Use challenge SepsisLabel as supplied; do not shift again.",
        },
        "runs": runs,
        "limitations": [
            "Exploratory sampled internal evaluation; not full-cohort or external validation.",
            "Hourly-row metrics do not establish event-level clinical utility.",
            "No clinically selected operating threshold or clinical-readiness claim.",
            "Patient-level predictions and identifiers are not exported.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_dir", type=Path)
    parser.add_argument("--sample-size", type=int, default=500)
    parser.add_argument("--sampling-seed", type=int, default=20261014)
    parser.add_argument("--split-seeds", type=int, nargs="+", default=[42, 123, 2026])
    parser.add_argument("--bootstrap-replicates", type=int, default=200)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(
        args.data_dir, args.sample_size, args.sampling_seed,
        args.split_seeds, args.bootstrap_replicates,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "sampled_patients": result["protocol"]["sampled_patients"],
        "runs": len(result["runs"]),
    }, indent=2))


if __name__ == "__main__":
    main()
