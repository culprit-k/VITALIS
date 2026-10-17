import numpy as np

from scripts.evaluate_physiological_features import VITALS, personal_z


def test_personal_physiology_features_are_prior_only_and_patient_local():
    columns = list(VITALS)
    normal_a = [
        [70, 98, 36.8, 120, 90, 75, 16],
        [72, 97, 36.9, 121, 91, 76, 17],
        [69, 98, 36.7, 119, 89, 74, 15],
        [71, 97, 36.8, 122, 92, 77, 16],
        [70, 98, 36.8, 120, 90, 75, 16],
    ]
    normal_b = [
        [140, 98, 36.8, 120, 90, 75, 16],
        [142, 97, 36.9, 121, 91, 76, 17],
        [139, 98, 36.7, 119, 89, 74, 15],
        [141, 97, 36.8, 122, 92, 77, 16],
        [140, 98, 36.8, 120, 90, 75, 16],
    ]
    rows_a = normal_a * 2 + [[95, 90, 38.5, 95, 70, 60, 28]]
    rows_b = normal_b * 2 + [[160, 92, 38.0, 100, 73, 63, 25]]
    X = np.asarray(rows_a + rows_b, dtype=np.float32)
    groups = np.asarray([1] * len(rows_a) + [2] * len(rows_b), dtype=np.int32)

    z = personal_z(X, groups, columns)

    # The expanding scale requires five valid prior deviations after warm-up.
    assert np.isnan(z[:10]).all()
    assert np.isnan(z[11:21]).all()
    assert np.isfinite(z[10]).any()
    assert np.isfinite(z[21]).any()
    # Patient-specific references and current deviations differ between patients.
    assert not np.allclose(z[10], z[21], equal_nan=True)


from scripts.evaluate_physiological_features import paired_brier_cluster_bootstrap, calibration_summary


def test_paired_brier_bootstrap_is_paired_and_aggregate_only():
    y = np.asarray([0, 1, 0, 1, 0, 0], dtype=np.int8)
    baseline = np.asarray([0.2, 0.4, 0.3, 0.6, 0.1, 0.2])
    candidate = np.asarray([0.1, 0.6, 0.2, 0.7, 0.1, 0.1])
    groups = np.asarray([1, 1, 2, 2, 3, 3])
    result = paired_brier_cluster_bootstrap(y, baseline, candidate, groups, 100, 7)
    expected = float(np.mean((candidate-y)**2) - np.mean((baseline-y)**2))
    assert np.isclose(result["point_estimate"], expected)
    assert result["bootstrap_replicates"] == 100
    assert result["unique_patients"] == 3
    assert result["bootstrap_unit"] == "Set B patient cluster"
    assert "predictions" not in result


def test_calibration_summary_is_descriptive_and_does_not_transform_probabilities():
    y = np.asarray([0, 0, 0, 1, 0, 1, 0, 0], dtype=np.int8)
    p = np.asarray([0.1, 0.7, 0.15, 0.2, 0.8, 0.6, 0.05, 0.4])
    groups = np.repeat(np.arange(4), 2)
    result = calibration_summary(y, p, groups)
    assert np.isfinite(result["calibration_intercept_slope_fixed_1"])
    assert np.isfinite(result["calibration_intercept_free_slope"])
    assert np.isfinite(result["calibration_slope"])
    cluster = result["patient_cluster_intercept_slope_uncertainty"]
    assert cluster["calibration_intercept_slope_status"] == "estimated"
    assert cluster["calibration_intercept_slope_intervals_95"] is not None
    assert "no calibration transformation applied" in result["interpretation"]
