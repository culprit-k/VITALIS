"""Privacy-safe diagnostics for fresh VITALIS feature caches.

Prints only schema/cache fingerprints and aggregate integrity statistics. It never
writes patient identifiers, source rows, feature rows, or model predictions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


EXPECTED = {
    "A": {"patients": 20336, "rows": 790215, "positive_labels": 17136},
    "B": {"patients": 20000, "rows": 761995, "positive_labels": 10780},
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def audit(cache: Path, cohort: str) -> dict[str, object]:
    meta = json.loads((cache / "meta.json").read_text(encoding="utf-8"))
    X = np.load(cache / "X.npy", mmap_mode="r")
    y = np.load(cache / "y.npy", mmap_mode="r")
    groups = np.load(cache / "g.npy", mmap_mode="r")

    if X.ndim != 2 or y.ndim != 1 or groups.ndim != 1:
        raise ValueError(f"Set {cohort}: invalid cache dimensions")
    if X.shape[0] != len(y) or len(y) != len(groups):
        raise ValueError(f"Set {cohort}: cache arrays have inconsistent row counts")
    if X.shape[1] != len(meta.get("columns", [])):
        raise ValueError(f"Set {cohort}: feature schema does not match matrix width")
    if len(np.unique(groups)) != EXPECTED[cohort]["patients"]:
        raise ValueError(f"Set {cohort}: unexpected unique patient count")
    if len(y) != EXPECTED[cohort]["rows"] or int(np.asarray(y).sum()) != EXPECTED[cohort]["positive_labels"]:
        raise ValueError(f"Set {cohort}: cohort row/label totals mismatch")
    if not np.isin(y, [0, 1]).all():
        raise ValueError(f"Set {cohort}: non-binary labels")
    if not np.isfinite(np.asarray(X)).any():
        raise ValueError(f"Set {cohort}: feature matrix has no finite values")

    # Patient codes must form contiguous blocks in the same order as cache metadata.
    changes = np.r_[0, np.flatnonzero(groups[1:] != groups[:-1]) + 1, len(groups)]
    block_ids = np.asarray(groups[changes[:-1]])
    if len(block_ids) != EXPECTED[cohort]["patients"]:
        raise ValueError(f"Set {cohort}: patient groups are not contiguous blocks")
    if len(np.unique(block_ids)) != len(block_ids):
        raise ValueError(f"Set {cohort}: patient group reappears after another patient")
    block_rows = np.diff(changes)
    if block_rows.tolist() != meta.get("rows_per_patient"):
        raise ValueError(f"Set {cohort}: group block lengths differ from rows_per_patient")
    if meta.get("files") is None or len(meta["files"]) != len(block_ids):
        raise ValueError(f"Set {cohort}: source-file ordering metadata invalid")

    finite_counts = np.zeros(X.shape[1], dtype=np.int64)
    finite_means = np.zeros(X.shape[1], dtype=np.float64)
    finite_stds = np.zeros(X.shape[1], dtype=np.float64)
    # Process feature columns one at a time to keep memory bounded.
    for j in range(X.shape[1]):
        col = np.asarray(X[:, j], dtype=np.float64)
        finite = col[np.isfinite(col)]
        finite_counts[j] = len(finite)
        if len(finite):
            finite_means[j] = float(np.mean(finite))
            finite_stds[j] = float(np.std(finite))
    schema = json.dumps(meta["columns"], separators=(",", ":"), ensure_ascii=False).encode()
    ordered_files = json.dumps(meta["files"], separators=(",", ":"), ensure_ascii=False).encode()
    return {
        "cohort": cohort,
        "patients": int(len(block_ids)),
        "rows": int(len(y)),
        "positive_labels": int(np.asarray(y).sum()),
        "feature_count": int(X.shape[1]),
        "schema_sha256": hashlib.sha256(schema).hexdigest(),
        "ordered_source_file_list_sha256": hashlib.sha256(ordered_files).hexdigest(),
        "X_npy_sha256": sha256_file(cache / "X.npy"),
        "y_npy_sha256": sha256_file(cache / "y.npy"),
        "g_npy_sha256": sha256_file(cache / "g.npy"),
        "feature_finite_count_min": int(finite_counts.min()),
        "feature_finite_count_max": int(finite_counts.max()),
        "feature_all_missing_columns": int(np.sum(finite_counts == 0)),
        "feature_summary_sha256": hashlib.sha256(
            np.column_stack([finite_counts, finite_means, finite_stds]).tobytes()
        ).hexdigest(),
        "patient_blocks_contiguous": True,
        "patient_block_lengths_match_metadata": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--set-a-cache", type=Path, required=True)
    parser.add_argument("--set-b-cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = {
        "audit_type": "privacy_safe_feature_cache_integrity",
        "diagnostic_only": True,
        "cohorts": [
            audit(args.set_a_cache, "A"),
            audit(args.set_b_cache, "B"),
        ],
    }
    if report["cohorts"][0]["schema_sha256"] != report["cohorts"][1]["schema_sha256"]:
        raise SystemExit("Set A and Set B ordered feature schema hashes differ")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
