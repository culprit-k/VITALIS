import importlib.util
from pathlib import Path

import pytest

MODULE = Path(__file__).parents[1] / "scripts" / "check_repository_hygiene.py"
SPEC = importlib.util.spec_from_file_location("repository_hygiene", MODULE)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def test_clean_tree_passes_and_ignores_git_and_cache_dirs(tmp_path):
    (tmp_path / "README.md").write_text("safe", encoding="utf-8")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "hidden.npz").write_bytes(b"private")
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "ignored.npy").write_bytes(b"cache")
    assert MOD.audit_repository(tmp_path) == []


@pytest.mark.parametrize("filename", ["cohort.psv", "scores.npz", "cache.npy", "records.csv", "model.joblib"])
def test_data_bearing_extensions_fail(tmp_path, filename):
    (tmp_path / filename).write_bytes(b"synthetic")
    issues = MOD.audit_repository(tmp_path)
    assert len(issues) == 1
    assert filename in issues[0]


def test_large_file_fails_with_configurable_limit(tmp_path):
    (tmp_path / "unexpected.bin").write_bytes(b"123456")
    issues = MOD.audit_repository(tmp_path, max_bytes=5)
    assert len(issues) == 1
    assert "exceeds 5 byte limit" in issues[0]


def test_invalid_root_and_limit_rejected(tmp_path):
    with pytest.raises(ValueError):
        MOD.audit_repository(tmp_path / "missing")
    with pytest.raises(ValueError):
        MOD.audit_repository(tmp_path, max_bytes=0)
