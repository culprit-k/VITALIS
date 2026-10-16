"""Patient-cluster uncertainty summaries for probability calibration metrics."""
from __future__ import annotations

import numpy as np

DEFAULT_CALIBRATION_BINS = (0.0, 0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 0.5, 1.0)


def patient_cluster_bootstrap_calibration_metrics(
    labels,
    probabilities,
    patient_ids,
    *,
    comparison_probabilities=None,
    n_bootstrap: int = 200,
    seed: int = 42,
    calibration_bins=DEFAULT_CALIBRATION_BINS,
) -> dict[str, object]:
    """Bootstrap calibration metrics by resampling whole patients.

    Patient blocks must be contiguous, but eligible rows within a block may
    have time gaps because current-positive labels and incomplete future tails
    are excluded by the horizon target builder. The optional comparison stream
    is paired on the same rows and is used for a calibrated-minus-raw Brier
    difference interval.
    """
    y = np.asarray(labels, dtype=np.int8)
    p = np.asarray(probabilities, dtype=np.float64)
    groups = np.asarray(patient_ids)
    q = None if comparison_probabilities is None else np.asarray(comparison_probabilities, dtype=np.float64)
    if y.ndim != 1 or p.ndim != 1 or groups.ndim != 1 or len(y) == 0 or not (len(y) == len(p) == len(groups)):
        raise ValueError("labels, probabilities, and patient_ids must be nonempty aligned vectors")
    if not np.isin(y, [0, 1]).all():
        raise ValueError("labels must be binary")
    if not np.isfinite(p).all() or np.any((p < 0) | (p > 1)):
        raise ValueError("probabilities must be finite and in [0, 1]")
    if q is not None and (q.ndim != 1 or len(q) != len(y) or not np.isfinite(q).all() or np.any((q < 0) | (q > 1))):
        raise ValueError("comparison_probabilities must be finite, in [0, 1], and aligned")
    if isinstance(n_bootstrap, bool) or not isinstance(n_bootstrap, int) or n_bootstrap < 20:
        raise ValueError("n_bootstrap must be an integer of at least 20")
    edges = np.asarray(calibration_bins, dtype=np.float64)
    if edges.ndim != 1 or len(edges) < 3 or not np.isfinite(edges).all() or edges[0] != 0 or edges[-1] != 1 or np.any(np.diff(edges) <= 0):
        raise ValueError("calibration_bins must be strictly increasing from 0 to 1")
    if groups.dtype.kind in "fc" and np.isnan(groups).any():
        raise ValueError("patient_ids cannot be missing")
    if groups.dtype.kind == "O" and any(x is None or (isinstance(x, float) and np.isnan(x)) for x in groups):
        raise ValueError("patient_ids cannot be missing")

    boundaries = np.r_[0, np.flatnonzero(groups[1:] != groups[:-1]) + 1, len(groups)]
    seen = set()
    for start, end in zip(boundaries[:-1], boundaries[1:]):
        value = groups[start].item() if hasattr(groups[start], "item") else groups[start]
        if value in seen:
            raise ValueError("patient rows must form contiguous blocks")
        seen.add(value)
    n_patients, n_bins = len(boundaries) - 1, len(edges) - 1
    if n_patients < 2:
        raise ValueError("at least two patients are required for cluster bootstrap")

    clipped = np.clip(p, 1e-12, 1 - 1e-12)
    row_bin = np.searchsorted(edges[1:-1], p, side="right")
    patient_rows = np.zeros(n_patients, dtype=np.float64)
    patient_positive = np.zeros(n_patients, dtype=np.float64)
    patient_p_sum = np.zeros(n_patients, dtype=np.float64)
    patient_brier_sum = np.zeros(n_patients, dtype=np.float64)
    patient_logloss_sum = np.zeros(n_patients, dtype=np.float64)
    patient_comparison_brier_diff = np.zeros(n_patients, dtype=np.float64) if q is not None else None
    patient_bin_count = np.zeros((n_patients, n_bins), dtype=np.float64)
    patient_bin_p_sum = np.zeros((n_patients, n_bins), dtype=np.float64)
    patient_bin_y_sum = np.zeros((n_patients, n_bins), dtype=np.float64)
    for j, (start, end) in enumerate(zip(boundaries[:-1], boundaries[1:])):
        yy, pp, bb = y[start:end], p[start:end], row_bin[start:end]
        patient_rows[j] = end - start
        patient_positive[j] = yy.sum()
        patient_p_sum[j] = pp.sum()
        patient_brier_sum[j] = np.square(pp - yy).sum()
        patient_logloss_sum[j] = (-(yy * np.log(clipped[start:end]) + (1 - yy) * np.log(1 - clipped[start:end]))).sum()
        if q is not None:
            patient_comparison_brier_diff[j] = (np.square(pp - yy) - np.square(q[start:end] - yy)).sum()
        patient_bin_count[j] = np.bincount(bb, minlength=n_bins)
        patient_bin_p_sum[j] = np.bincount(bb, weights=pp, minlength=n_bins)
        patient_bin_y_sum[j] = np.bincount(bb, weights=yy, minlength=n_bins)

    total_rows = float(patient_rows.sum())
    prevalence = float(patient_positive.sum() / total_rows)
    brier = float(patient_brier_sum.sum() / total_rows)
    point = {
        "prevalence": prevalence,
        "mean_predicted_probability": float(patient_p_sum.sum() / total_rows),
        "brier_score": brier,
        "constant_prevalence_brier_reference": prevalence * (1 - prevalence),
        "brier_minus_constant_prevalence_reference": brier - prevalence * (1 - prevalence),
        "log_loss": float(patient_logloss_sum.sum() / total_rows),
        "fixed_bin_expected_calibration_error": None,
    }
    point["fixed_bin_expected_calibration_error"] = float(sum(
        (patient_bin_count[:, b].sum() / total_rows)
        * abs(patient_bin_p_sum[:, b].sum() / patient_bin_count[:, b].sum() - patient_bin_y_sum[:, b].sum() / patient_bin_count[:, b].sum())
        for b in range(n_bins) if patient_bin_count[:, b].sum() > 0
    ))
    if q is not None:
        point["brier_difference_vs_comparison"] = float(patient_comparison_brier_diff.sum() / total_rows)

    rng = np.random.default_rng(seed)
    sample = rng.integers(0, n_patients, size=(n_bootstrap, n_patients))
    rows_b = patient_rows[sample].sum(axis=1)
    pos_b = patient_positive[sample].sum(axis=1)
    brier_b = patient_brier_sum[sample].sum(axis=1) / rows_b
    prevalence_b = pos_b / rows_b
    pred_mean_b = patient_p_sum[sample].sum(axis=1) / rows_b
    logloss_b = patient_logloss_sum[sample].sum(axis=1) / rows_b
    ece_b = np.zeros(n_bootstrap, dtype=np.float64)
    for b in range(n_bins):
        count = patient_bin_count[:, b][sample].sum(axis=1)
        psum = patient_bin_p_sum[:, b][sample].sum(axis=1)
        ysum = patient_bin_y_sum[:, b][sample].sum(axis=1)
        nonzero = count > 0
        ece_b[nonzero] += count[nonzero] / rows_b[nonzero] * np.abs(psum[nonzero] / count[nonzero] - ysum[nonzero] / count[nonzero])
    boot = {
        "prevalence": prevalence_b,
        "mean_predicted_probability": pred_mean_b,
        "brier_score": brier_b,
        "constant_prevalence_brier_reference": prevalence_b * (1 - prevalence_b),
        "brier_minus_constant_prevalence_reference": brier_b - prevalence_b * (1 - prevalence_b),
        "log_loss": logloss_b,
        "fixed_bin_expected_calibration_error": ece_b,
    }
    if q is not None:
        boot["brier_difference_vs_comparison"] = patient_comparison_brier_diff[sample].sum(axis=1) / rows_b
    intervals = {}
    for name, values in boot.items():
        intervals[name] = {
            "lower_95": float(np.percentile(values, 2.5)),
            "upper_95": float(np.percentile(values, 97.5)),
            "valid_replicates": int(len(values)),
            "requested_replicates": n_bootstrap,
        }
    return {
        "method": "patient-cluster percentile bootstrap of per-patient sufficient statistics",
        "patients": int(n_patients),
        "rows": int(len(y)),
        "seed": int(seed),
        "point_estimates": point,
        "intervals": intervals,
        "interpretation_note": "Conditional retrospective cohort uncertainty; not prospective or clinical validation.",
    }


def patient_cluster_bootstrap_paired_model_metrics(
    labels,
    reference_probabilities,
    comparison_probabilities,
    patient_ids,
    *,
    n_bootstrap: int = 200,
    seed: int = 42,
) -> dict[str, object]:
    """Paired patient-cluster intervals for comparison-minus-reference metrics.

    This compares two frozen probability streams on exactly the same eligible
    rows. Whole patient blocks are resampled; row-level predictions are never
    returned. AUROC/AUPRC use score-tie groups precomputed once so each bootstrap
    replicate can be evaluated using patient multiplicities without re-sorting
    the full cohort.
    """
    from sklearn.metrics import average_precision_score, brier_score_loss, log_loss, roc_auc_score

    y = np.asarray(labels, dtype=np.int8)
    p_ref = np.asarray(reference_probabilities, dtype=np.float64)
    p_cmp = np.asarray(comparison_probabilities, dtype=np.float64)
    groups = np.asarray(patient_ids)
    if y.ndim != 1 or p_ref.ndim != 1 or p_cmp.ndim != 1 or groups.ndim != 1:
        raise ValueError("labels, scores, and patient_ids must be one-dimensional")
    if len(y) == 0 or not (len(y) == len(p_ref) == len(p_cmp) == len(groups)):
        raise ValueError("labels, scores, and patient_ids must be nonempty aligned vectors")
    if not np.isin(y, [0, 1]).all() or len(np.unique(y)) != 2:
        raise ValueError("labels must contain both binary classes")
    for name, score in (("reference_probabilities", p_ref), ("comparison_probabilities", p_cmp)):
        if not np.isfinite(score).all() or np.any((score < 0) | (score > 1)):
            raise ValueError(f"{name} must be finite and in [0, 1]")
    if isinstance(n_bootstrap, bool) or not isinstance(n_bootstrap, int) or n_bootstrap < 20:
        raise ValueError("n_bootstrap must be an integer of at least 20")
    if groups.dtype.kind in "fc" and np.isnan(groups).any():
        raise ValueError("patient_ids cannot be missing")
    if groups.dtype.kind == "O" and any(x is None or (isinstance(x, float) and np.isnan(x)) for x in groups):
        raise ValueError("patient_ids cannot be missing")

    boundaries = np.r_[0, np.flatnonzero(groups[1:] != groups[:-1]) + 1, len(groups)]
    seen = set()
    row_patient = np.empty(len(groups), dtype=np.int64)
    for patient_idx, (start, end) in enumerate(zip(boundaries[:-1], boundaries[1:])):
        value = groups[start].item() if hasattr(groups[start], "item") else groups[start]
        if value in seen:
            raise ValueError("patient rows must form contiguous blocks")
        seen.add(value)
        row_patient[start:end] = patient_idx
    n_patients = len(boundaries) - 1
    if n_patients < 2:
        raise ValueError("at least two patients are required for cluster bootstrap")

    def prepare(score):
        order = np.argsort(score, kind="mergesort")
        sorted_score = score[order]
        group_index = np.r_[0, np.flatnonzero(sorted_score[1:] != sorted_score[:-1]) + 1]
        row_group = np.empty(len(score), dtype=np.int64)
        row_group[order] = np.repeat(np.arange(len(group_index)), np.diff(np.r_[group_index, len(score)]))
        return row_group, len(group_index)

    ref_group, n_ref_groups = prepare(p_ref)
    cmp_group, n_cmp_groups = prepare(p_cmp)

    def weighted_auc_ap(row_group, n_score_groups, row_weights):
        positive = np.bincount(row_group, weights=row_weights * y, minlength=n_score_groups)
        negative = np.bincount(row_group, weights=row_weights * (1 - y), minlength=n_score_groups)
        total_pos, total_neg = positive.sum(), negative.sum()
        if total_pos <= 0 or total_neg <= 0:
            return None, None
        neg_below = np.cumsum(negative) - negative
        auc = float(np.sum(positive * (neg_below + 0.5 * negative)) / (total_pos * total_neg))
        pos_desc, neg_desc = positive[::-1], negative[::-1]
        tp = np.cumsum(pos_desc)
        fp = np.cumsum(neg_desc)
        precision = np.divide(tp, tp + fp, out=np.zeros_like(tp), where=(tp + fp) > 0)
        ap = float(np.sum((pos_desc / total_pos) * precision))
        return auc, ap

    p_ref_clip = np.clip(p_ref, 1e-12, 1 - 1e-12)
    p_cmp_clip = np.clip(p_cmp, 1e-12, 1 - 1e-12)
    point_ref = {
        "auroc": float(roc_auc_score(y, p_ref)),
        "auprc": float(average_precision_score(y, p_ref)),
        "brier_score": float(brier_score_loss(y, p_ref)),
        "log_loss": float(log_loss(y, p_ref_clip, labels=[0, 1])),
    }
    point_cmp = {
        "auroc": float(roc_auc_score(y, p_cmp)),
        "auprc": float(average_precision_score(y, p_cmp)),
        "brier_score": float(brier_score_loss(y, p_cmp)),
        "log_loss": float(log_loss(y, p_cmp_clip, labels=[0, 1])),
    }
    point_diff = {name: point_cmp[name] - point_ref[name] for name in point_ref}

    rows_per_patient = np.bincount(row_patient, minlength=n_patients).astype(np.float64)
    ref_brier = np.bincount(row_patient, weights=np.square(p_ref - y), minlength=n_patients)
    cmp_brier = np.bincount(row_patient, weights=np.square(p_cmp - y), minlength=n_patients)
    ref_loss = np.bincount(row_patient, weights=-(y * np.log(p_ref_clip) + (1-y) * np.log(1-p_ref_clip)), minlength=n_patients)
    cmp_loss = np.bincount(row_patient, weights=-(y * np.log(p_cmp_clip) + (1-y) * np.log(1-p_cmp_clip)), minlength=n_patients)

    rng = np.random.default_rng(seed)
    samples = rng.integers(0, n_patients, size=(n_bootstrap, n_patients))
    differences = {name: [] for name in point_ref}
    for sample in samples:
        patient_multiplicity = np.bincount(sample, minlength=n_patients).astype(np.float64)
        row_weights = patient_multiplicity[row_patient]
        total_rows = float(np.dot(patient_multiplicity, rows_per_patient))
        if total_rows <= 0:
            continue
        ref_auc, ref_ap = weighted_auc_ap(ref_group, n_ref_groups, row_weights)
        cmp_auc, cmp_ap = weighted_auc_ap(cmp_group, n_cmp_groups, row_weights)
        if ref_auc is None or cmp_auc is None:
            continue
        differences["auroc"].append(cmp_auc - ref_auc)
        differences["auprc"].append(cmp_ap - ref_ap)
        differences["brier_score"].append(float(np.dot(patient_multiplicity, cmp_brier - ref_brier) / total_rows))
        differences["log_loss"].append(float(np.dot(patient_multiplicity, cmp_loss - ref_loss) / total_rows))

    intervals = {}
    for name, values in differences.items():
        arr = np.asarray(values, dtype=np.float64)
        if len(arr) < 20:
            raise ValueError("fewer than 20 valid patient-cluster bootstrap replicates")
        intervals[name] = {"lower_95": float(np.percentile(arr, 2.5)), "upper_95": float(np.percentile(arr, 97.5)),
                           "valid_replicates": int(len(arr)), "requested_replicates": n_bootstrap}
    return {
        "method": "paired patient-cluster percentile bootstrap; comparison minus reference",
        "reference_model": "static",
        "comparison_model": "temporal",
        "patients": int(n_patients),
        "rows": int(len(y)),
        "seed": int(seed),
        "point_estimates": {"reference": point_ref, "comparison": point_cmp, "comparison_minus_reference": point_diff},
        "intervals_comparison_minus_reference": intervals,
        "interpretation_note": "Conditional retrospective uncertainty for frozen predictions; not prospective or clinical validation.",
    }
