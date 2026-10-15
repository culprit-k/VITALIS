import numpy as np

from scripts.evaluate_physiological_features import VITALS, personal_z


def test_personal_physiology_features_are_prior_only_and_patient_local():
    columns = list(VITALS)
    rows_a = [
        [70, 98, 36.8, 120, 90, 75, 16],
        [72, 97, 36.9, 121, 91, 76, 17],
        [69, 98, 36.7, 119, 89, 74, 15],
        [71, 97, 36.8, 122, 92, 77, 16],
        [70, 98, 36.8, 120, 90, 75, 16],
        [95, 90, 38.5, 95, 70, 60, 28],
    ]
    rows_b = [
        [140, 98, 36.8, 120, 90, 75, 16],
        [142, 97, 36.9, 121, 91, 76, 17],
        [139, 98, 36.7, 119, 89, 74, 15],
        [141, 97, 36.8, 122, 92, 77, 16],
        [140, 98, 36.8, 120, 90, 75, 16],
        [165, 90, 38.5, 95, 70, 60, 28],
    ]
    X = np.asarray(rows_a + rows_b, dtype=np.float32)
    groups = np.asarray([1] * len(rows_a) + [2] * len(rows_b), dtype=np.int32)

    z = personal_z(X, groups, columns)

    assert np.isnan(z[:5]).all()
    assert np.isnan(z[6:11]).all()
    assert np.isfinite(z[5]).any()
    assert np.isfinite(z[11]).any()
    # A patient-specific reference must not be shared across patient blocks.
    assert not np.allclose(z[5], z[11], equal_nan=True)
