import pandas as pd
import pytest

from scripts.build_cohort import build_inventory


def test_inventory_summarizes_without_patient_records(tmp_path):
    pd.DataFrame({"HR": [70, None], "SepsisLabel": [0, 1]}).to_csv(tmp_path / "a.psv", sep="|", index=False)
    pd.DataFrame({"HR": [90], "SepsisLabel": [0]}).to_csv(tmp_path / "b.psv", sep="|", index=False)
    report = build_inventory(tmp_path)
    assert report["patient_file_count"] == 2
    assert report["hourly_row_count"] == 3
    assert report["positive_label_row_count"] == 1
    assert report["patients_with_positive_labels"] == 1
    assert "patient_ids" not in report


def test_inventory_rejects_invalid_label(tmp_path):
    pd.DataFrame({"SepsisLabel": [0, 3]}).to_csv(tmp_path / "a.psv", sep="|", index=False)
    with pytest.raises(ValueError, match="Invalid or missing"):
        build_inventory(tmp_path)
