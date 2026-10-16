import numpy as np

from scripts.evaluate_horizon_cross_cohort import evaluate_one_horizon


COLUMNS = ["HR", "Age", "HR_lag1", "HR_delta1", "HR_rollmean6"]


def synthetic_cache(patients=40, rows_per_patient=16, cohort_shift=0.0):
    y, groups, features = [], [], []
    for patient in range(patients):
        event = patient < patients // 2
        previous_hr = 70.0
        local_labels = []
        local_features = []
        for hour in range(rows_per_patient):
            label = int(event and hour >= 12)
            hr = 70.0 + cohort_shift + (18.0 if event and hour >= 8 else 0.0) + 0.1 * hour
            lag = previous_hr if hour else np.nan
            delta = hr - lag if hour else np.nan
            roll = np.mean([70.0 + cohort_shift + (18.0 if event and h >= 8 else 0.0) + 0.1 * h
                            for h in range(max(0, hour - 5), hour + 1)])
            local_labels.append(label)
            local_features.append([hr, 25 + patient, lag, delta, roll])
            previous_hr = hr
        y.extend(local_labels)
        groups.extend([patient + 1] * rows_per_patient)
        features.extend(local_features)
    meta = {
        "patient_count": patients,
        "row_count": patients * rows_per_patient,
        "columns": COLUMNS,
        "rows_per_patient": [rows_per_patient] * patients,
    }
    return meta, np.asarray(features, dtype=np.float32), np.asarray(y, dtype=np.int8), np.asarray(groups, dtype=np.int32)


def test_cross_cohort_horizon_evaluation_uses_disjoint_set_a_patients_and_all_set_b():
    meta_a, Xa, ya, ga = synthetic_cache()
    meta_b, Xb, yb, gb = synthetic_cache(cohort_shift=1.5)
    result = evaluate_one_horizon(
        meta_a, Xa, ya, ga, meta_b, Xb, yb, gb, COLUMNS,
        horizon_hours=3, seed=42, threshold=0.5, refractory_hours=3, n_bootstrap=20,
        predict_chunk_rows=100,
    )
    assert result["horizon_hours"] == 3
    assert result["patient_counts"]["set_a_train_eligible"] > 0
    assert result["patient_counts"]["set_a_heldout_unused_eligible"] > 0
    assert result["patient_counts"]["set_b_test_eligible"] == 40
    assert result["row_counts"]["set_b_eligible"] > 0
    assert set(result["models"]) == {"static", "temporal"}
    for model in result["models"].values():
        assert model["set_b_test_metrics"]["auroc"] is not None
        assert model["set_b_patient_warning_metrics"]["eligible_hours"] > 0
        assert model["set_b_patient_warning_metric_bootstrap_95ci"]["unique_patients"] == 40
    serialized = str(result)
    assert "patient_ids" not in serialized
    assert "patient_predictions" not in serialized


def test_cross_cohort_horizon_target_does_not_cross_patient_boundaries():
    from scripts.evaluate_horizon_cross_cohort import horizon_rows

    labels = np.asarray([0, 0, 0, 1, 0, 0, 0, 0], dtype=np.int8)
    groups = np.asarray([1, 1, 1, 1, 2, 2, 2, 2], dtype=np.int32)
    target = horizon_rows(labels, groups, 1)
    assert target.row_indices.tolist() == [0, 1, 2, 4, 5, 6]
    assert target.targets.tolist() == [0, 0, 1, 0, 0, 0]
    assert target.patient_ids.tolist() == [1, 1, 1, 2, 2, 2]
