#!/usr/bin/env python3
"""Build a local memory-mapped feature cache for VITALIS full-cohort experiments.

Raw PhysioNet files and generated cache files must remain outside version control.
Run chunks sequentially; each chunk writes a disjoint, explicitly selected patient range.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

BASE = [
    "HR", "O2Sat", "Temp", "SBP", "MAP", "DBP", "Resp", "EtCO2",
    "BaseExcess", "HCO3", "FiO2", "pH", "PaCO2", "SaO2", "AST", "BUN",
    "Alkalinephos", "Calcium", "Chloride", "Creatinine", "Bilirubin_direct",
    "Glucose", "Lactate", "Magnesium", "Phosphate", "Potassium",
    "Bilirubin_total", "TroponinI", "Hct", "Hgb", "PTT", "WBC",
    "Fibrinogen", "Platelets", "Age", "Gender", "Unit1", "Unit2",
    "HospAdmTime", "ICULOS",
]
MEAS = [
    "HR", "O2Sat", "Temp", "SBP", "MAP", "DBP", "Resp", "EtCO2",
    "BaseExcess", "HCO3", "FiO2", "pH", "PaCO2", "SaO2", "BUN",
    "Creatinine", "Glucose", "Lactate", "Potassium", "Hct", "Hgb",
    "WBC", "Platelets",
]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("dataset_dir", type=Path, help="Directory of per-patient .psv files")
    ap.add_argument("--cache-dir", type=Path, required=True)
    ap.add_argument("--start", type=int, required=True, help="Zero-based first patient index, inclusive")
    ap.add_argument("--end", type=int, required=True, help="Zero-based last patient index, exclusive")
    args = ap.parse_args()
    paths = sorted(args.dataset_dir.glob("*.psv"))
    if not paths:
        ap.error(f"No .psv files found in {args.dataset_dir}")
    args.cache_dir.mkdir(parents=True, exist_ok=True)
    meta_path = args.cache_dir / "meta.json"
    if not meta_path.exists():
        counts = []
        for path in paths:
            with path.open("r", encoding="utf-8") as handle:
                counts.append(sum(1 for _ in handle) - 1)
        columns = BASE.copy()
        for col in MEAS:
            columns.extend([f"{col}_lag1", f"{col}_delta1", f"{col}_rollmean6"])
        meta = {
            "files": [p.name for p in paths],
            "rows_per_patient": counts,
            "columns": columns,
            "patient_count": len(paths),
            "row_count": int(sum(counts)),
            "feature_definition": "baseline fields plus prior-row lag, one-step difference, and trailing six-row mean",
        }
        tmp = meta_path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
        tmp.replace(meta_path)
    else:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if meta["files"] != [p.name for p in paths]:
            ap.error("Cache metadata file list does not match dataset directory; use a fresh cache directory")
    if not (0 <= args.start < args.end <= len(paths)):
        ap.error(f"Require 0 <= start < end <= {len(paths)}")
    total, columns = meta["row_count"], meta["columns"]
    index = {name: i for i, name in enumerate(columns)}
    x_path, y_path, g_path = (args.cache_dir / name for name in ("X.npy", "y.npy", "g.npy"))
    if not x_path.exists():
        np.lib.format.open_memmap(x_path, mode="w+", dtype=np.float32, shape=(total, len(columns)))[:] = np.nan
    if not y_path.exists():
        np.lib.format.open_memmap(y_path, mode="w+", dtype=np.int8, shape=(total,))[:] = 0
    if not g_path.exists():
        np.lib.format.open_memmap(g_path, mode="w+", dtype=np.int32, shape=(total,))[:] = 0
    X = np.lib.format.open_memmap(x_path, mode="r+")
    y = np.lib.format.open_memmap(y_path, mode="r+")
    groups = np.lib.format.open_memmap(g_path, mode="r+")
    offset = int(sum(meta["rows_per_patient"][:args.start]))
    started = time.time()
    for patient_index in range(args.start, args.end):
        path = paths[patient_index]
        nrows = int(meta["rows_per_patient"][patient_index])
        frame = pd.read_csv(path, sep="|", usecols=lambda c: c == "SepsisLabel" or c in BASE)
        labels = frame["SepsisLabel"].to_numpy(dtype=np.int8)
        for col in BASE:
            if col not in frame:
                continue
            values = pd.to_numeric(frame[col], errors="coerce").to_numpy(dtype=np.float32)
            X[offset:offset+nrows, index[col]] = values
            if col not in MEAS:
                continue
            lag = np.full(nrows, np.nan, dtype=np.float32)
            if nrows > 1:
                lag[1:] = values[:-1]
            X[offset:offset+nrows, index[f"{col}_lag1"]] = lag
            X[offset:offset+nrows, index[f"{col}_delta1"]] = values - lag
            valid = np.isfinite(values)
            clean = np.where(valid, values, 0.0).astype(np.float64, copy=False)
            csum = np.cumsum(clean)
            ccount = np.cumsum(valid, dtype=np.int32)
            rolling_sum, rolling_count = csum.copy(), ccount.copy()
            if nrows > 6:
                rolling_sum[6:] -= csum[:-6]
                rolling_count[6:] -= ccount[:-6]
            rolling = np.divide(
                rolling_sum, rolling_count, out=np.full(nrows, np.nan), where=rolling_count > 0
            )
            X[offset:offset+nrows, index[f"{col}_rollmean6"]] = rolling.astype(np.float32)
        y[offset:offset+nrows] = labels
        groups[offset:offset+nrows] = patient_index + 1
        offset += nrows
        if (patient_index + 1) % 1000 == 0:
            print(f"processed {patient_index + 1}/{len(paths)} patients", flush=True)
    X.flush()
    y.flush()
    groups.flush()
    marker = args.cache_dir / f"chunk_{args.start}_{args.end}.done"
    marker.write_text(json.dumps({"start": args.start, "end": args.end, "seconds": time.time()-started}) + "\n")
    print(f"complete: patients {args.start}:{args.end}; elapsed {time.time()-started:.1f}s", flush=True)


if __name__ == "__main__":
    main()
