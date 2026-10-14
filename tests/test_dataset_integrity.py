import pandas as pd
import pytest

from scripts.check_dataset_integrity import check_dataset


def test_check_dataset_reports_aggregate_integrity(tmp_path):
    pd.DataFrame({"HR": [80, 90], "SepsisLabel": [0, 1]}).to_csv(
        tmp_path / "a.psv", sep="|", index=False
    )
    pd.DataFrame({"HR": [70], "SepsisLabel": [0]}).to_csv(
        tmp_path / "b.psv", sep="|", index=False
    )
    result = check_dataset(tmp_path)
    assert result["patient_file_count"] == 2
    assert result["hourly_row_count"] == 3
    assert result["positive_challenge_label_rows"] == 1
    assert result["patients_with_positive_challenge_labels"] == 1
    assert result["files_with_column_set_mismatch"] == 0
    assert "columns_union" in result


def test_check_dataset_rejects_invalid_target(tmp_path):
    pd.DataFrame({"SepsisLabel": [0, 2]}).to_csv(
        tmp_path / "a.psv", sep="|", index=False
    )
    with pytest.raises(ValueError, match="non-binary target"):
        check_dataset(tmp_path)


def test_check_dataset_rejects_empty_partition(tmp_path):
    with pytest.raises(FileNotFoundError, match="No .psv"):
        check_dataset(tmp_path)
