from scripts.run_experiment_suite import run_suite, summarize


def _report(seed, static_auroc, temporal_auroc):
    return {
        "seed": seed,
        "static": {"test_metrics": {"auroc": static_auroc}},
        "temporal": {"test_metrics": {"auroc": temporal_auroc}},
        "temporal_minus_static_test_metric_delta": {"auroc": temporal_auroc - static_auroc},
    }


def test_summary_reports_mean_and_seed_sd_not_confidence_interval():
    summary = summarize([_report(1, 0.7, 0.72), _report(2, 0.8, 0.81)])
    assert summary["static"]["auroc"]["mean_across_seeds"] == 0.75
    assert summary["temporal"]["auroc"]["mean_across_seeds"] == 0.765
    assert summary["temporal_minus_static_delta"]["auroc"]["mean_across_seeds"] == 0.015
    assert summary["static"]["auroc"]["valid_seeds"] == 2


def test_run_suite_rejects_duplicate_seeds(tmp_path, monkeypatch):
    import scripts.run_experiment_suite as suite

    monkeypatch.setattr(suite, "compare", lambda data_dir, seed: _report(seed, 0.7, 0.72))
    try:
        run_suite(tmp_path, [42, 42])
    except ValueError as exc:
        assert "unique" in str(exc)
    else:
        raise AssertionError("duplicate seeds should be rejected")
