import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

MODULE = Path(__file__).parents[1] / "scripts" / "audit_feature_availability.py"
SPEC = importlib.util.spec_from_file_location("audit_feature_availability", MODULE)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def make_cache(path: Path, columns: list[str], values: np.ndarray) -> None:
    path.mkdir()
    (path / "meta.json").write_text(
        json.dumps({"columns": columns, "row_count": int(values.shape[0])}),
        encoding="utf-8",
    )
    np.save(path / "X.npy", values)


def test_audit_counts_finite_values_in_chunks(tmp_path):
    cache = tmp_path / "cache"
    values = np.array([[1.0, np.nan], [np.inf, 2.0], [3.0, np.nan]])
    make_cache(cache, ["observed", "sparse"], values)
    result = MOD.audit_cache(cache, chunk_rows=2)
    assert result["rows"] == 3
    assert result["features"]["observed"]["finite_rows"] == 2
    assert result["features"]["sparse"]["finite_rows"] == 1
    assert result["features"]["sparse"]["finite_rate"] == pytest.approx(1 / 3)


def test_compare_reports_shift_and_missingness_without_predictions():
    a = {"rows": 4, "feature_columns": 2, "features": {
        "x": {"finite_rows": 0, "finite_rate": 0.0},
        "y": {"finite_rows": 4, "finite_rate": 1.0},
    }}
    b = {"rows": 4, "feature_columns": 2, "features": {
        "x": {"finite_rows": 1, "finite_rate": 0.25},
        "y": {"finite_rows": 3, "finite_rate": 0.75},
    }}
    result = MOD.compare_caches(a, b, threshold=0.2)
    assert result["features_all_missing_in_A_but_observed_in_B"] == ["x"]
    assert result["features_all_missing_in_B_but_observed_in_A"] == []
    assert [x["feature"] for x in result["features_over_threshold"]] == ["x", "y"]
    assert result["set_b_used_for_tuning"] is False
    assert result["row_level_data_exported"] is False
    assert "predictions" not in json.dumps(result)


def test_audit_rejects_metadata_shape_mismatch(tmp_path):
    cache = tmp_path / "cache"
    make_cache(cache, ["x"], np.ones((2, 1)))
    (cache / "meta.json").write_text(
        json.dumps({"columns": ["x"], "row_count": 3}), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="shape"):
        MOD.audit_cache(cache)


def test_compare_rejects_schema_mismatch():
    a = {"rows": 1, "feature_columns": 1, "features": {"a": {"finite_rows": 1, "finite_rate": 1.0}}}
    b = {"rows": 1, "feature_columns": 1, "features": {"b": {"finite_rows": 1, "finite_rate": 1.0}}}
    with pytest.raises(ValueError, match="schemas differ"):
        MOD.compare_caches(a, b)


@pytest.mark.parametrize("threshold", [-0.1, 1.1])
def test_compare_rejects_invalid_threshold(threshold):
    with pytest.raises(ValueError, match="threshold"):
        MOD.compare_caches({"features": {}}, {"features": {}}, threshold)
