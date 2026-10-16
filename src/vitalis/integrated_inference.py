"Research-only adapter exposing twin and supervised outputs separately.

The adapter does not train/load a model and does not fuse heuristic twin scores
with supervised probabilities. A caller must inject a frozen predictor explicitly.
"""
from __future__ import annotations

from datetime import datetime, timezone
from math import isfinite
from numbers import Real
from typing import Callable, Mapping, Any

from vitalis.stream import Observation, TimestampedTwinStream

Predictor = Callable[[Mapping[str, float], int], float]
SUPPORTED_HORIZONS = (1, 3, 6)


def _timestamp(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class IntegratedResearchInference:
    """Join stream/twin scoring with optional externally supplied frozen inference.

    The predictor receives a feature mapping and horizon in hours and must return
    a calibrated probability from a frozen, versioned model. This class cannot
    verify clinical calibration or the feature schema; caller governance remains
    necessary. With no predictor, supervised results are explicitly unavailable.
    """

    def __init__(
        self,
        stream: TimestampedTwinStream,
        *,
        predictor: Predictor | None = None,
        model_version: str | None = None,
        calibration_version: str | None = None,
        feature_schema_version: str | None = None,
        expected_feature_names: tuple[str, ...] | None = None,
    ) -> None:
        if predictor is not None and not all(
            isinstance(item, str) and item.strip()
            for item in (model_version, calibration_version, feature_schema_version)
        ):
            raise ValueError(
                "predictor requires model_version, calibration_version, "
                "and feature_schema_version"
            )
        if predictor is not None and (
            not expected_feature_names
            or any(not isinstance(name, str) or not name for name in expected_feature_names)
            or len(set(expected_feature_names)) != len(expected_feature_names)
        ):
            raise ValueError(
                "predictor requires unique, non-empty expected_feature_names "
                "matching its frozen feature schema"
            )
        self.stream = stream
        self.predictor = predictor
        self.model_version = model_version
        self.calibration_version = calibration_version
        self.feature_schema_version = feature_schema_version
        self.expected_feature_names = (
            tuple(expected_feature_names) if expected_feature_names is not None else None
        )

    def ingest(self, observation: Observation) -> bool:
        """Validate and forward an observation to the timestamped stream."""
        return self.stream.ingest(observation)

    def score(
        self,
        timestamp: datetime,
        *,
        supervised_features: Mapping[str, float] | None = None,
        horizons: tuple[int, ...] = SUPPORTED_HORIZONS,
    ) -> dict[str, Any]:
        """Return independently typed twin and supervised outputs.

        A twin score is a heuristic, never a probability. Missing model/features
        yield null probabilities and explicit statuses rather than false zeroes.
        """
        observed_at = _timestamp(timestamp)
        if (
            not horizons
            or any(
                isinstance(h, bool) or not isinstance(h, int) or h not in SUPPORTED_HORIZONS
                for h in horizons
            )
        ):
            raise ValueError("horizons must be a non-empty subset of integer values (1, 3, 6)")
        if len(set(horizons)) != len(horizons):
            raise ValueError("horizons must not contain duplicates")

        twin_result = self.stream.score(timestamp)
        twin = {
            "status": "eligible" if twin_result.get("eligible") else "insufficient_data",
            "coverage": float(twin_result["coverage"]),
            "deviation_state": twin_result["state"],
            "trajectory_score": twin_result.get("trajectory_score"),
            "trajectory_direction": twin_result.get("trajectory_direction"),
            "score_semantics": twin_result.get(
                "score_semantics", "unitless heuristic; not a clinical probability"
            ),
            "clinical_recommendation": None,
        }

        supervised_results: dict[str, dict[str, Any]] = {}
        for horizon in horizons:
            item: dict[str, Any] = {
                "status": "unavailable",
                "target_definition": "future Challenge SepsisLabel-positive-window entry",
                "horizon_hours": horizon,
                "probability": None,
                "model_version": self.model_version,
                "calibration_version": self.calibration_version,
                "feature_schema_version": self.feature_schema_version,
            }
            if self.predictor is None:
                item["reason"] = "no supervised predictor supplied"
            elif supervised_features is None:
                item["reason"] = "supervised features unavailable"
            else:
                if any(not isinstance(key, str) or not key for key in supervised_features):
                    raise ValueError("feature names must be non-empty strings")
                supplied_names = set(supervised_features)
                expected_names = set(self.expected_feature_names or ())
                if supplied_names != expected_names:
                    missing = sorted(expected_names - supplied_names)
                    extra = sorted(supplied_names - expected_names)
                    raise ValueError(
                        f"feature schema mismatch; missing={missing}, extra={extra}"
                    )
                features: dict[str, float] = {}
                for key, raw in supervised_features.items():
                    if isinstance(raw, bool) or not isinstance(raw, Real):
                        raise ValueError(f"feature {key!r} must be a real numeric scalar")
                    value = float(raw)
                    if not isfinite(value):
                        raise ValueError(f"feature {key!r} must be finite")
                    features[key] = value
                raw_probability = self.predictor(features, horizon)
                if isinstance(raw_probability, bool) or not isinstance(raw_probability, Real):
                    raise ValueError("supervised predictor must return a numeric scalar probability")
                probability = float(raw_probability)
                if not isfinite(probability) or not 0.0 <= probability <= 1.0:
                    raise ValueError("supervised predictor must return a finite probability in [0, 1]")
                item.update(status="scored", probability=probability)
            supervised_results[str(horizon)] = item

        return {
            "schema_version": "vitalis.output.v1",
            "observed_at": observed_at,
            "twin": twin,
            "supervised": supervised_results,
            "limitations": [
                "research-only",
                "not clinically validated",
                "not for patient-care decisions",
                "twin heuristic scores are not probabilities",
                "Challenge-label target is not independently adjudicated sepsis onset",
            ],
        }
