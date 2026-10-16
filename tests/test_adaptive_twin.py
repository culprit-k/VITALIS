from vitalis.adaptive_twin import AdaptivePhysiologicalTwin, TwinConfig


def twin():
    return AdaptivePhysiologicalTwin(
        channels=["heart_rate", "spo2", "respiratory_rate"],
        config=TwinConfig(
            min_history=3, history_window=8, min_channels=2, min_systems=2,
            min_coverage=0.5, persistence_steps=2,
        ),
    )


def warm(t):
    for _ in range(3):
        t.update({"heart_rate": 70, "spo2": 98, "respiratory_rate": 16})


def test_first_observation_is_not_scored_against_itself():
    t = twin()
    result = t.update({"heart_rate": 70, "spo2": 98, "respiratory_rate": 16})
    assert result["state"] == "insufficient_data"
    assert result["trajectory_score"] is None
    assert result["channels"]["heart_rate"]["baseline"] is None


def test_current_measurement_is_scored_before_baseline_update():
    t = twin()
    warm(t)
    result = t.update({"heart_rate": 110, "spo2": 90, "respiratory_rate": 28})
    assert result["eligible"] is True
    assert result["channels"]["heart_rate"]["baseline"] == 70
    assert result["channels"]["heart_rate"]["baseline_updated"] is False
    assert result["trajectory_score"] is not None
    assert result["score_semantics"].startswith("unitless heuristic")


def test_persistent_multisystem_deviation_is_detected_without_clinical_claim():
    t = twin()
    warm(t)
    t.update({"heart_rate": 110, "spo2": 90, "respiratory_rate": 28})
    result = t.update({"heart_rate": 112, "spo2": 89, "respiratory_rate": 30})
    assert result["state"] == "persistent_multisystem_deviation"
    assert result["clinical_recommendation"] is None
    assert "not for patient-care" in result["warning"]


def test_missing_channels_reduce_coverage_and_prevent_scoring():
    t = twin()
    warm(t)
    result = t.update({"heart_rate": 70, "spo2": None, "respiratory_rate": float("nan")})
    assert result["coverage"] == 1 / 3
    assert result["eligible"] is False
    assert result["state"] == "insufficient_data"


def test_missing_sample_breaks_consecutive_deviation_streak():
    t = twin()
    warm(t)
    t.update({"heart_rate": 110, "spo2": 90, "respiratory_rate": 28})
    t.update({"heart_rate": 111, "spo2": 91, "respiratory_rate": 29})
    assert t.states["heart_rate"].consecutive_deviations == 2
    t.update({"heart_rate": None, "spo2": 91, "respiratory_rate": 29})
    assert t.states["heart_rate"].consecutive_deviations == 0


def test_trajectory_reports_direction_after_first_eligible_score():
    t = twin()
    warm(t)
    first = t.update({"heart_rate": 70, "spo2": 98, "respiratory_rate": 16})
    second = t.update({"heart_rate": 110, "spo2": 90, "respiratory_rate": 28})
    assert first["trajectory_direction"] is None
    assert second["trajectory_direction"] == "rising"
    assert second["trajectory_delta"] > 0


def test_reset_prevents_patient_state_carryover():
    t = twin()
    warm(t)
    t.update({"heart_rate": 110, "spo2": 90, "respiratory_rate": 28})
    t.reset()
    result = t.update({"heart_rate": 75, "spo2": 97, "respiratory_rate": 17})
    assert result["state"] == "insufficient_data"
    assert result["channels"]["heart_rate"]["history_count"] == 0


def test_invalid_configuration_is_rejected():
    try:
        TwinConfig(ewma_alpha=0)
    except ValueError:
        pass
    else:
        raise AssertionError("ewma_alpha=0 should be rejected")


def test_cusum_detects_gradual_multisystem_shift():
    t = AdaptivePhysiologicalTwin(
        channels=["heart_rate", "spo2", "respiratory_rate"],
        config=TwinConfig(
            min_history=3, history_window=12, min_channels=2, min_systems=2,
            min_coverage=0.5, cusum_allowance=0.25, cusum_threshold=2.0,
        ),
    )
    for heart_rate, spo2, respiratory_rate in [(68, 97, 14), (70, 98, 15), (72, 99, 16)]:
        t.update({
            "heart_rate": heart_rate,
            "spo2": spo2,
            "respiratory_rate": respiratory_rate,
        })
    result = None
    for heart_rate, spo2, respiratory_rate in [
        (73, 97.7, 16.5), (74, 97.4, 17), (75, 97.1, 17.5),
    ]:
        result = t.update({
            "heart_rate": heart_rate,
            "spo2": spo2,
            "respiratory_rate": respiratory_rate,
        })
    assert result is not None
    assert result["channels"]["heart_rate"]["cusum_triggered"] is True
    assert result["channels"]["respiratory_rate"]["cusum_triggered"] is True
    assert result["state"] == "cumulative_multisystem_shift"
    assert result["channels"]["heart_rate"]["baseline_updated"] is False


def test_reference_baseline_remains_separate_from_rolling_baseline():
    t = AdaptivePhysiologicalTwin(
        channels=["heart_rate", "spo2"],
        config=TwinConfig(min_history=2, history_window=4, min_channels=2, min_systems=2),
    )
    t.update({"heart_rate": 68, "spo2": 97})
    t.update({"heart_rate": 72, "spo2": 99})
    result = t.update({"heart_rate": 70, "spo2": 98})
    assert result["channels"]["heart_rate"]["reference_baseline"] == 70
    assert result["channels"]["heart_rate"]["baseline"] == 70


def test_scale_floor_can_be_configured_per_channel():
    t = AdaptivePhysiologicalTwin(
        channels=["heart_rate", "spo2"],
        scale_floors={"heart_rate": 1.0},
        config=TwinConfig(min_history=3, history_window=6, min_channels=2, min_systems=2),
    )
    for _ in range(3):
        t.update({"heart_rate": 70, "spo2": 98})
    result = t.update({"heart_rate": 71, "spo2": 98})
    assert result["channels"]["heart_rate"]["reference_z_score"] == 1.0



def test_flatline_history_keeps_deviation_scores_finite():
    t = AdaptivePhysiologicalTwin(
        channels=["heart_rate", "spo2", "respiratory_rate"],
        scale_floors={"heart_rate": 1.0, "spo2": 0.5, "respiratory_rate": 0.5},
        config=TwinConfig(min_history=3, history_window=8, min_channels=2, min_systems=2),
    )
    for _ in range(10):
        result = t.update({"heart_rate": 70, "spo2": 98, "respiratory_rate": 16})
    assert result["eligible"] is True
    for channel in result["channels"].values():
        if channel["z_score"] is not None:
            assert abs(channel["z_score"]) < float("inf")


def test_single_channel_spike_is_not_absorbed_into_rolling_baseline():
    t = twin()
    warm(t)
    spike = t.update({"heart_rate": 150, "spo2": 98, "respiratory_rate": 16})
    assert spike["channels"]["heart_rate"]["baseline_updated"] is False
    assert spike["channels"]["heart_rate"]["baseline"] == 70
    recovery = t.update({"heart_rate": 71, "spo2": 98, "respiratory_rate": 16})
    assert recovery["channels"]["heart_rate"]["baseline"] == 70


def test_correlated_channels_are_aggregated_by_system_not_counted_as_two_systems():
    t = AdaptivePhysiologicalTwin(
        channels=["heart_rate", "systolic_bp", "spo2"],
        config=TwinConfig(min_history=2, history_window=6, min_channels=2, min_systems=2),
    )
    for _ in range(2):
        t.update({"heart_rate": 70, "systolic_bp": 120, "spo2": 98})
    result = t.update({"heart_rate": 71, "systolic_bp": 121, "spo2": 97})
    assert set(result["system_scores"]) == {"cardiovascular", "oxygenation"}
    assert len(result["system_scores"]) == 2
    assert result["eligible"] is True


def test_custom_channels_must_have_explicit_system_mapping():
    try:
        AdaptivePhysiologicalTwin(channels=["unmapped_channel"])
    except ValueError as exc:
        assert "channel_systems" in str(exc)
    else:
        raise AssertionError("unmapped channel should be rejected")


def test_unknown_observation_keys_are_ignored_without_state_creation():
    t = twin()
    warm(t)
    result = t.update({
        "heart_rate": 70,
        "spo2": 98,
        "respiratory_rate": 16,
        "patient_id": "must-not-become-a-channel",
        "unconfigured_sensor": 999,
    })
    assert "patient_id" not in result["channels"]
    assert "unconfigured_sensor" not in result["channels"]
    assert set(t.states) == {"heart_rate", "spo2", "respiratory_rate"}


def test_reset_channel_clears_history_and_trajectory_continuity():
    t = twin()
    warm(t)
    t.update({"heart_rate": 110, "spo2": 90, "respiratory_rate": 28})
    t.reset_channel("heart_rate")
    result = t.update({"heart_rate": 75, "spo2": 97, "respiratory_rate": 17})
    assert result["channels"]["heart_rate"]["history_count"] == 0
    assert result["channels"]["heart_rate"]["baseline"] is None
    assert result["trajectory_direction"] is None


def test_rejects_nonfinite_or_nonpositive_custom_scale_floors():
    import pytest

    with pytest.raises(ValueError, match="finite and positive"):
        AdaptivePhysiologicalTwin(
            channels=["heart_rate"],
            scale_floors={"heart_rate": float("nan")},
        )
    with pytest.raises(ValueError, match="finite and positive"):
        AdaptivePhysiologicalTwin(
            channels=["heart_rate"],
            scale_floors={"heart_rate": 0},
        )
