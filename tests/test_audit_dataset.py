import pandas as pd
import pytest

from scripts.audit_dataset import audit_directory


def test_audit_returns_aggregate_only(tmp_path):
    pd.DataFrame({"HR": [70, 75], "SepsisLabel": [0, 1]}).to_csv(
        tmp_path / "p1.psv", sep="|", index=False
    )
    report = audit_directory(tmp_path)
    assert report["patient_file_count"] == 1
    assert report["total_hourly_rows"] == 2
    assert report["positive_label_rows"] == 1
    assert "patient_id" not in report


def test_audit_rejects_missing_target(tmp_path):
    pd.DataFrame({"HR": [70]}).to_csv(tmp_path / "p1.psv", sep="|", index=False)
    with pytest.raises(ValueError, match="SepsisLabel"):
        audit_directory(tmp_path)


def test_audit_rejects_non_binary_target(tmp_path):
    pd.DataFrame({"SepsisLabel": [0, 2]}).to_csv(tmp_path / "p1.psv", sep="|", index=False)
    with pytest.raises(ValueError, match="outside binary"):
        audit_directory(tmp_path)
