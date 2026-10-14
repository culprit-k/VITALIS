import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

MODULE = Path(__file__).parents[1] / "scripts" / "audit_patient_level_availability.py"
SPEC = importlib.util.spec_from_file_location("audit_patient_level_availability", MODULE)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def make_cache(path: Path, X: np.ndarray, y: np.ndarray, groups: np.ndarray) -> None:
    path.mkdir()
    (path / "meta.json").write_text(json.dumps({
        "columns": ["DBP", "EtCO2"], "row_count": len(y), "patient_count": len(np.unique(groups))
    }), encoding="utf-8")
    np.save(path / "X.npy", X)
    np.save(path / "y.npy", y)
    np.save(path / "g.npy", groups)


def test_patient_level_availability_and_outcome_are_aggregated(tmp_path):
    cache = tmp_path / "cache"
    X = np.array([[1.0, np.nan], [np.nan, np.nan], [2.0, 3.0], [np.nan, 4.0]])
    y = np.array([0, 1, 0, 0], dtype=np.int8)
    groups = np.array([10, 10, 20, 20], dtype=np.int32)
    make_cache(cache, X, y, groups)
    out = MOD.audit_cache(cache, ["DBP", "EtCO2"])
    assert out["patients"] == 2
    assert out["patients_with_any_positive_hourly_label"] == 1
    assert out["features"]["DBP"]["patients_with_any_finite_value"] == 2
    assert out["features"]["EtCO2"]["patients_with_any_finite_value"] == 1
    assert out["features"]["EtCO2"]["positive_label_patient_rate_feature_absent"] == 1.0
    assert out["duration_strata"][0]["duration_hours"] == "1-24 h"
    assert out["duration_strata"][0]["patients"] == 2
    assert out["duration_strata"][0]["positive_label_patient_rate"] == 0.5
    assert out["duration_strata"][0]["features"]["EtCO2"]["availability_rate_positive_label"] == 0.0
    assert out["duration_strata"][0]["features"]["EtCO2"]["availability_rate_no_positive_label"] == 1.0


def test_rejects_non_contiguous_patient_rows(tmp_path):
    cache = tmp_path / "cache"
    X = np.ones((3, 2))
    y = np.zeros(3, dtype=np.int8)
    groups = np.array([1, 2, 1], dtype=np.int32)
    make_cache(cache, X, y, groups)
    with pytest.raises(ValueError, match="not contiguous"):
        MOD.audit_cache(cache, ["DBP"])


def test_rejects_cache_shape_mismatch(tmp_path):
    cache = tmp_path / "cache"
    make_cache(cache, np.ones((2, 2)), np.zeros(2, dtype=np.int8), np.array([1, 1]))
    meta = json.loads((cache / "meta.json").read_text())
    meta["row_count"] = 3
    (cache / "meta.json").write_text(json.dumps(meta))
    with pytest.raises(ValueError, match="dimensions"):
        MOD.audit_cache(cache, ["DBP"])
