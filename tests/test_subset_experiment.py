from pathlib import Path

import pytest

from scripts.run_subset_experiment import select_patient_files


def test_patient_sampling_is_deterministic_and_without_replacement(tmp_path: Path):
    for name in ("p3.psv", "p1.psv", "p2.psv"):
        (tmp_path / name).write_text("SepsisLabel\n0\n", encoding="utf-8")
    first = select_patient_files(tmp_path, 2, 2026)
    second = select_patient_files(tmp_path, 2, 2026)
    assert first == second
    assert len(first) == 2
    assert len(set(first)) == 2
    assert first == sorted(first)


def test_patient_sampling_rejects_invalid_size(tmp_path: Path):
    (tmp_path / "p1.psv").write_text("SepsisLabel\n0\n", encoding="utf-8")
    with pytest.raises(ValueError, match="at least 2"):
        select_patient_files(tmp_path, 1, 2026)
    with pytest.raises(ValueError, match="only 1 files"):
        select_patient_files(tmp_path, 3, 2026)
