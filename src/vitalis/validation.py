"""Validation helpers for patient-level evaluation."""

from collections.abc import Iterable


def assert_disjoint_patient_splits(
    train_patients: Iterable[str],
    validation_patients: Iterable[str],
    test_patients: Iterable[str],
) -> None:
    """Raise ValueError if any patient identifier occurs in multiple splits."""
    splits = {
        "train": set(train_patients),
        "validation": set(validation_patients),
        "test": set(test_patients),
    }
    names = list(splits)
    for index, left_name in enumerate(names):
        for right_name in names[index + 1 :]:
            overlap = splits[left_name] & splits[right_name]
            if overlap:
                sample = sorted(map(str, overlap))[:5]
                raise ValueError(
                    f"Patient overlap between {left_name} and {right_name}; sample={sample}"
                )
