"""Calibration and missingness summaries for aggregate-only model evaluation."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss


def calibration_summary(
    y_true: np.ndarray | pd.Series,
    probability: np.ndarray,
    *,
    bins: int = 10,
    epsilon: float = 1e-6,
) -> dict[str, object]:
    """Return aggregate calibration diagnostics; never returns row-level predictions.

    Calibration slope/intercept are estimated by regressing outcomes on the logit
    of predicted probabilities. These are descriptive diagnostics, not proof that
    a model is calibrated or clinically useful.
    """
    y = np.asarray(y_true, dtype=int).reshape(-1)
    p = np.asarray(probability, dtype=float).reshape(-1)
    if y.size == 0 or y.size != p.size:
        raise ValueError("y_true and probability must have the same non-zero length")
    if not np.isin(y, [0, 1]).all():
        raise ValueError("y_true must contain only 0/1 labels")
    if not np.isfinite(p).all() or ((p < 0) | (p > 1)).any():
        raise ValueError("probabilities must be finite values between 0 and 1")
    if bins < 2:
        raise ValueError("bins must be at least 2")

    clipped = np.clip(p, epsilon, 1 - epsilon)
    logits = np.log(clipped / (1 - clipped))
    slope = intercept = None
    if np.unique(y).size == 2:
        calibrator = LogisticRegression(C=1e6, solver="lbfgs", max_iter=1000)
        calibrator.fit(logits.reshape(-1, 1), y)
        slope = float(calibrator.coef_[0, 0])
        intercept = float(calibrator.intercept_[0])

    edges = np.linspace(0.0, 1.0, bins + 1)
    bin_rows: list[dict[str, float | int]] = []
    for i in range(bins):
        mask = (p >= edges[i]) & ((p < edges[i + 1]) if i < bins - 1 else (p <= edges[i + 1]))
        if mask.any():
            bin_rows.append({
                "bin_lower": float(edges[i]),
                "bin_upper": float(edges[i + 1]),
                "count": int(mask.sum()),
                "mean_predicted": float(p[mask].mean()),
                "observed_fraction": float(y[mask].mean()),
            })

    return {
        "rows": int(y.size),
        "prevalence": float(y.mean()),
        "brier_score": float(brier_score_loss(y, p)),
        "log_loss": float(log_loss(y, clipped, labels=[0, 1])),
        "calibration_intercept": intercept,
        "calibration_slope": slope,
        "reliability_bins": bin_rows,
        "interpretation_note": (
            "Aggregate descriptive diagnostics only. Calibration estimates can be unstable "
            "in small or low-event samples and do not establish clinical utility."
        ),
    }


def missingness_summary(features: pd.DataFrame) -> dict[str, object]:
    """Summarize predictor missingness by column without exposing patient rows."""
    if features.empty:
        raise ValueError("features must contain at least one row and one column")
    rates = features.isna().mean()
    return {
        "rows": int(features.shape[0]),
        "feature_count": int(features.shape[1]),
        "overall_cell_missingness": float(features.isna().to_numpy().mean()),
        "features": [
            {"feature": str(name), "missing_fraction": float(rate)}
            for name, rate in rates.sort_values(ascending=False).items()
        ],
    }
