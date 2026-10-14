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
