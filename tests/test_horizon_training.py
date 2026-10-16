from pathlib import Path

import pandas as pd

from scripts.train_horizon_model import train_one_horizon


def make_synthetic_cohort(directory: Path, patients: int = 30, rows: int = 14) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for patient in range(patients):
        event = patient < patients // 2
        records = []
        for hour in range(rows):
            positive = int(event and hour >= 10)
            changed = event and hour >= 7
            records.append({
                "HR": 70 + 0.1 * hour + (18 if changed else 0),
                "O2Sat": 98 - (3 if changed else 0),
                "Resp": 15 + (4 if changed else 0),
                "SBP": 120 - (8 if changed else 0),
                "Age": 25 + patient,
                "ICULOS": hour,
                "HospAdmTime": -2.0 - hour,
                "SepsisLabel": positive,
            })
        pd.DataFrame(records).to_csv(directory / f"p{patient:03d}.psv", sep="|", index=False)


def test_horizon_training_runs_end_to_end_on_synthetic_patient_files(tmp_path):
    data_dir = tmp_path / "synthetic_psv"
    make_synthetic_cohort(data_dir)
    result = train_one_horizon(
        data_dir, horizon_hours=3, seed=42, threshold=0.5,
        refractory_hours=3, n_bootstrap=20,
    )
    assert result["horizon_hours"] == 3
    assert result["patient_counts"]["train"] > 0
    assert result["patient_counts"]["validation"] > 0
    assert result["patient_counts"]["test"] > 0
    assert result["test_metrics"]["auroc"] is not None
    assert result["test_patient_warning_metrics"]["eligible_hours"] > 0
    assert result["test_patient_warning_metric_bootstrap_95ci"]["unique_patients"] == result["patient_counts"]["test"]
    assert "patient_predictions" not in result
    assert "patient_ids" not in result
