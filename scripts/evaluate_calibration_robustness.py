"""Evaluate held-out calibration and missingness for matched VITALIS feature sets.

Only aggregate metrics are written. Recalibration is fitted on validation patients
and evaluated once on held-out test patients; test outcomes never fit the mapping.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from scripts.train_baseline import load_patient_rows, observed_training_features
from vitalis.calibration import calibration_summary, missingness_summary
from vitalis.validation import assert_disjoint_patient_splits


def _fit_recalibrator(y_validation: np.ndarray, p_validation: np.ndarray):
    """Fit a logistic calibration map using validation outcomes only."""
    if np.unique(y_validation).size < 2:
        return None
    p = np.clip(np.asarray(p_validation, dtype=float), 1e-6, 1 - 1e-6)
    logits = np.log(p / (1 - p)).reshape(-1, 1)
    model = LogisticRegression(C=1e6, solver="lbfgs", max_iter=1000)
    model.fit(logits, y_validation)
    return model


def _apply_recalibrator(model, probability: np.ndarray) -> np.ndarray:
    p = np.clip(np.asarray(probability, dtype=float), 1e-6, 1 - 1e-6)
    logits = np.log(p / (1 - p)).reshape(-1, 1)
    return model.predict_proba(logits)[:, 1]


def evaluate(data_dir: Path, sample_size: int | None, sampling_seed: int,
             split_seeds: list[int], bins: int = 10) -> dict[str, object]:
    paths = sorted(data_dir.glob("*.psv"))
    if not paths:
        raise FileNotFoundError(f"No .psv files found in {data_dir}")
    if sample_size is not None:
        import random
        if sample_size < 2 or sample_size > len(paths):
            raise ValueError(f"sample_size must be between 2 and {len(paths)}")
        paths = sorted(random.Random(sampling_seed).sample(paths, sample_size))
        # Use a temporary symlink directory so the canonical loader reads only the sample.
        import tempfile
        with tempfile.TemporaryDirectory(prefix="vitalis_calibration_") as tmp:
            subset = Path(tmp)
            for i, path in enumerate(paths):
                (subset / f"patient_{i:06d}.psv").symlink_to(path.resolve())
            return _evaluate_directory(subset, split_seeds, bins, sample_size, sampling_seed)
    return _evaluate_directory(data_dir, split_seeds, bins, len(paths), None)


def _evaluate_directory(data_dir: Path, split_seeds: list[int], bins: int,
                        sampled_patients: int, sampling_seed: int | None) -> dict[str, object]:
    matrices = {}
    labels = groups = None
    modes = (("static", False, False), ("temporal", True, False), ("personalized", True, True))
    for name, temporal, personalized in modes:
        X, y, g, _ = load_patient_rows(data_dir, temporal=temporal, personalized=personalized)
        matrices[name] = X
        if labels is None:
            labels, groups = y.to_numpy(dtype=int), g.to_numpy()
        elif not np.array_equal(labels, y.to_numpy(dtype=int)) or not np.array_equal(groups, g.to_numpy()):
            raise RuntimeError("Feature variants have inconsistent row/label/group ordering")
    assert labels is not None and groups is not None
    outputs = []
    for seed in split_seeds:
        first = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=seed)
        train_val, test = next(first.split(matrices["static"], labels, groups))
        second = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=seed + 1)
        train_rel, validation_rel = next(
            second.split(matrices["static"].iloc[train_val], labels[train_val], groups[train_val])
        )
        train, validation = train_val[train_rel], train_val[validation_rel]
        patient_sets = [set(groups[ix]) for ix in (train, validation, test)]
        assert_disjoint_patient_splits(*patient_sets)
        model_outputs = {}
        for name, X in matrices.items():
            observed, dropped = observed_training_features(X.iloc[train])
            model = make_pipeline(
                SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True),
                StandardScaler(),
                LogisticRegression(max_iter=1000, class_weight="balanced", solver="lbfgs", random_state=seed),
            )
            model.fit(X.iloc[train][observed], labels[train])
            p_val = model.predict_proba(X.iloc[validation][observed])[:, 1]
            p_test = model.predict_proba(X.iloc[test][observed])[:, 1]
            calibrator = _fit_recalibrator(labels[validation], p_val)
            calibrated_test = _apply_recalibrator(calibrator, p_test) if calibrator is not None else None
            model_outputs[name] = {
                "features_available": int(X.shape[1]),
                "features_used": len(observed),
                "dropped_all_missing_training_features": dropped,
                "calibration_validation": calibration_summary(labels[validation], p_val, bins=bins),
                "calibration_test_raw": calibration_summary(labels[test], p_test, bins=bins),
                "calibration_test_validation_recalibrated": (
                    calibration_summary(labels[test], calibrated_test, bins=bins)
                    if calibrated_test is not None else None
                ),
                "missingness": {
                    "train": missingness_summary(X.iloc[train]),
                    "validation": missingness_summary(X.iloc[validation]),
                    "test": missingness_summary(X.iloc[test]),
                },
                "recalibration_fit": (
                    "validation patients only; logistic map on predicted log-odds"
                    if calibrator is not None else "not fitted: validation labels contain one class"
                ),
            }
        outputs.append({
            "seed": seed,
            "validation_seed": seed + 1,
            "patient_counts": {
                "train": len(patient_sets[0]), "validation": len(patient_sets[1]), "test": len(patient_sets[2])
            },
            "row_counts": {
                "train": len(train), "validation": len(validation), "test": len(test)
            },
            "positive_rows": {
                "train": int(labels[train].sum()),
                "validation": int(labels[validation].sum()),
                "test": int(labels[test].sum()),
            },
            "models": model_outputs,
        })
    return {
        "project": "VITALIS",
        "protocol": {
            "sampled_patients": sampled_patients,
            "sampling_seed": sampling_seed,
            "split_seeds": split_seeds,
            "split_unit": "patient",
            "recalibration_fit": "validation only",
            "test_used_for_model_or_recalibration_fitting": False,
            "label_handling": "Use Challenge SepsisLabel as supplied; do not shift again.",
        },
        "runs": outputs,
        "limitations": [
            "Retrospective challenge dataset; not external or prospective validation.",
            "Calibration estimates may be unstable with few positive patients or label windows.",
            "Hourly-row calibration is not event-level clinical utility.",
            "Raw rows and patient-level predictions are not exported.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_dir", type=Path)
    parser.add_argument("--sample-size", type=int, default=500)
    parser.add_argument("--sampling-seed", type=int, default=20261014)
    parser.add_argument("--split-seeds", type=int, nargs="+", default=[42, 123, 2026])
    parser.add_argument("--bins", type=int, default=10)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = evaluate(args.data_dir, args.sample_size, args.sampling_seed, args.split_seeds, args.bins)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "sampled_patients": result["protocol"]["sampled_patients"],
        "split_count": len(result["runs"]),
        "models": ["static", "temporal", "personalized"],
    }, indent=2))


if __name__ == "__main__":
    main()
