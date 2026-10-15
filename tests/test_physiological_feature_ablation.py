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
