import numpy as np
import pandas as pd
import pytest

from vitalis.validation import assert_disjoint_patient_splits


def test_disjoint_patient_splits_accept_distinct_groups():
    assert_disjoint_patient_splits(["p1", "p2"], ["p3"], ["p4", "p5"])


@pytest.mark.parametrize(
    ("train", "validation", "test", "left", "right"),
    [
        (["p1", "p2"], ["p2"], ["p3"], "train", "validation"),
        (["p1"], ["p2", "p3"], ["p3"], "validation", "test"),
        (["p1", "p3"], ["p2"], ["p1"], "train", "test"),
    ],
)
def test_disjoint_patient_splits_reject_overlap(train, validation, test, left, right):
    with pytest.raises(ValueError, match=f"overlap between {left} and {right}"):
        assert_disjoint_patient_splits(train, validation, test)
