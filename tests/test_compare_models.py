from scripts.compare_models import compare


def test_comparison_reports_temporal_minus_static_deltas(monkeypatch, tmp_path):
    def fake_train(data_dir, temporal, seed):
        base = 0.7 if temporal else 0.6
        return {"test_metrics": {"auroc": base, "auprc": base - 0.1, "brier_score": 0.2}}

    monkeypatch.setattr("scripts.compare_models.train_and_evaluate", fake_train)
    report = compare(tmp_path, seed=42)
    assert report["temporal_minus_static_test_metric_delta"]["auroc"] == 0.1
    assert report["temporal_minus_static_test_metric_delta"]["brier_score"] == 0.0
