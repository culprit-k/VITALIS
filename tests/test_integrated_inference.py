from datetime import datetime, timezone

import pytest

from vitalis.adaptive_twin import AdaptivePhysiologicalTwin, TwinConfig
from vitalis.integrated_inference import IntegratedResearchInference
from vitalis.stream import Observation, TimestampedTwinStream


NOW = datetime(2026, 10, 16, 12, tzinfo=timezone.utc)


def make_inference(predictor=None, **versions):
    twin = AdaptivePhysiologicalTwin(
        channels=["heart_rate", "spo2"],
        config=TwinConfig(min_history=2, history_window=4, min_channels=2, min_systems=2),
    )
    stream = TimestampedTwinStream(twin, max_age_seconds=60)
    return IntegratedResearchInference(stream, predictor=predictor, **versions)


def warm(inference):
    for index in range(3):
        ts = NOW.replace(second=index)
        inference.ingest(Observation("heart_rate", ts, 70, "bpm"))
        inference.ingest(Observation("spo2", ts, 98, "%"))
        inference.score(ts)


def test_missing_predictor_is_explicitly_unavailable_not_zero():
    inference = make_inference()
    warm(inference)
    result = inference.score(NOW.replace(second=3))
    assert result["schema_version"] == "vitalis.output.v1"
    assert result["twin"]["status"] == "eligible"
    assert result["supervised"]["1"]["status"] == "unavailable"
    assert result["supervised"]["1"]["probability"] is None
    assert result["supervised"]["1"]["reason"] == "no supervised predictor supplied"


def test_supervised_outputs_keep_distinct_horizons_and_versions():
    seen = []

    def predictor(features, horizon):
        seen.append((dict(features), horizon))
        return {1: 0.1, 3: 0.2, 6: 0.3}[horizon]

    inference = make_inference(
        predictor,
        model_version="model-sha",
        calibration_version="cal-sha",
        feature_schema_version="features-v1",
        expected_feature_names=("heart_rate",),
    )
    warm(inference)
    result = inference.score(
        NOW.replace(second=3), supervised_features={"heart_rate": 90.0}
    )
    assert [result["supervised"][str(h)]["probability"] for h in (1, 3, 6)] == [
        0.1, 0.2, 0.3
    ]
    assert [call[1] for call in seen] == [1, 3, 6]
    assert result["supervised"]["3"]["model_version"] == "model-sha"
    assert result["supervised"]["3"]["calibration_version"] == "cal-sha"
    assert result["twin"]["trajectory_score"] != result["supervised"]["3"]["probability"]


def test_predictor_requires_immutable_version_metadata():
    with pytest.raises(ValueError, match="requires model_version"):
        make_inference(lambda features, horizon: 0.5)


@pytest.mark.parametrize("bad", [-0.1, 1.1, float("nan"), float("inf")])
def test_invalid_probability_fails_closed(bad):
    inference = make_inference(
        lambda features, horizon: bad,
        model_version="m1",
        calibration_version="c1",
        feature_schema_version="f1",
        expected_feature_names=("x",),
        expected_feature_names=("x",),
    )
    warm(inference)
    with pytest.raises(ValueError, match="finite probability"):
        inference.score(NOW.replace(second=3), supervised_features={"x": 1.0})


def test_feature_schema_mismatch_is_rejected():
    inference = make_inference(
        lambda features, horizon: 0.5,
        model_version="m1",
        calibration_version="c1",
        feature_schema_version="f1",
        expected_feature_names=("expected",),
    )
    with pytest.raises(ValueError, match="feature schema mismatch"):
        inference.score(NOW, supervised_features={"unexpected": 1.0})


def test_nonfinite_features_are_rejected():
    inference = make_inference(
        lambda features, horizon: 0.5,
        model_version="m1",
        calibration_version="c1",
        feature_schema_version="f1",
    )
    with pytest.raises(ValueError, match="must be finite"):
        inference.score(NOW, supervised_features={"x": float("nan")})


def test_naive_score_timestamp_is_rejected():
    inference = make_inference()
    with pytest.raises(ValueError, match="timezone-aware"):
        inference.score(datetime(2026, 10, 16, 12))
