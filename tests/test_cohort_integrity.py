from vitalis.validation import assert_disjoint_patient_splits


def test_disjoint_patient_splits_pass():
    assert_disjoint_patient_splits({"p1", "p2"}, {"p3"}, {"p4"}) is None


def test_overlapping_patient_splits_fail():
    try:
        assert_disjoint_patient_splits({"p1", "p2"}, {"p2"}, {"p3"})
    except ValueError as exc:
        assert "overlap" in str(exc).lower()
    else:
        raise AssertionError("Expected overlap to raise ValueError")
