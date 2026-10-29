# VITALIS AI Mathematics & Algorithm Lab

> **Research mathematics, not a clinical recipe.** This page explains the mathematics that exists in the repository and separates implemented behavior from experiments that still require validation. None of these scores or thresholds is approved for patient-care decisions.

<div align="center">

<img src="assets/math-robust-baseline.svg" width="100%" alt="Animated illustration of a robust median baseline that is less influenced by an outlier"/>

</div>

## The big picture: two separate algorithm tracks

VITALIS explores two complementary but **separate** questions:

| Track | Question | Output semantics |
|---|---|---|
| **Adaptive physiological twin** | How does a current observation differ from a person's recent and frozen reference patterns, and is the deviation persistent across systems? | Unitless heuristic deviation and trajectory summary—not a probability. |
| **Retrospective supervised ML** | Given historical features, how well can a fitted model distinguish or forecast entry into the supplied Challenge label window? | A model score/probability for a defined benchmark target; not a validated clinical risk. |

The two outputs are deliberately not added, averaged, multiplied, or fused. The streaming demo is synthetic-only, and the supervised offline workflow is not automatically loaded as a ready-to-use live model.

---

## 1. Input contract: valid, causal observations first

An observation is represented by a channel, timestamp, numeric value, unit, quality flag, and optional source. The timestamped adapter checks known channels, timezone-aware timestamps, units, non-finite/missing values, quality status, freshness, monotonically increasing per-channel timestamps, and explicitly identified source changes.

\`\`\`text
observation
    ↓
channel + unit + timestamp + quality checks
    ↓
fresh, valid per-channel frame
    ↓
adaptive twin (only when enough data are available)
\`\`\`

These are software input checks, not proof that a physical sensor is accurate. The current adapter does not provide sophisticated asynchronous sensor synchronisation or comprehensive artifact detection.

## 2. Robust personal reference: median and MAD

For channel \(j\) at time \(t\), let \(H_{j,t}\) contain previous accepted observations only. The current observation is scored **before** it can update its own history.

$$
m_{j,t}=\operatorname{median}(H_{j,t})
$$

$$
s_{j,t}=\max\left(1.4826\,\operatorname{MAD}(H_{j,t}),\epsilon_j\right)
$$

Here, \(\operatorname{MAD}(H)=\operatorname{median}(|x-m|)\). The factor 1.4826 is a conventional robust scale conversion for normally distributed data; the numerical floor \(\epsilon_j\) prevents division by a vanishing scale. Channel-specific floors can be configured because values can use different units.

<div align="center">

<img src="assets/math-robust-baseline.svg" width="100%" alt="Median and median absolute deviation baseline illustration"/>

</div>

**Why robust statistics?** A median is less pulled by a single extreme observation than a mean. That property can help in exploratory signal analysis, but does not make the baseline a true healthy baseline. Early measurements may already reflect illness, treatment, or measurement error.

## 3. Standardised deviation and clipping

For a current value \(x_{j,t}\):

$$
z_{j,t}=\frac{x_{j,t}-m_{j,t}}{s_{j,t}}
$$

The code freezes a reference centre and scale after the minimum-history warm-up. It also compares with that initial reference:

$$
z^0_{j,t}=\frac{x_{j,t}-m^0_j}{s^0_j}
$$

The current channel's effective deviation magnitude is the larger absolute deviation relative to the rolling and frozen baselines, clipped to a bounded range:

$$
q_{j,t}=\frac{\min(\max(|z_{j,t}|,|z^0_{j,t}|),z_{\max})}{z_{\max}}
$$

This creates a unitless score between 0 and 1 for aggregation. It is **not** the probability that sepsis is present or will develop.

<div align="center">

<img src="assets/math-zscore.svg" width="100%" alt="Animated explainer showing a standardized difference between current value and personal baseline"/>

</div>

## 4. Two-sided CUSUM: expose persistent drift

A rolling baseline can gradually follow a persistent shift. To help expose that pattern, the twin keeps cumulative positive and negative departures from the frozen reference:

$$
C^+_{j,t}=\max(0,C^+_{j,t-1}+z^0_{j,t}-k)
$$

$$
C^-_{j,t}=\max(0,C^-_{j,t-1}-z^0_{j,t}-k)
$$

A configured cumulative shift condition is reached when:

$$
\max(C^+_{j,t},C^-_{j,t})\ge h
$$

The allowance \(k\) and threshold \(h\) are **engineering parameters requiring validation**. They are not clinical alarm cutoffs. When a large deviation or CUSUM trigger is present, the point is not absorbed into the rolling baseline, which is a safeguard against immediately learning away a sharp or persistent change.

<div align="center">

<img src="assets/math-cusum.svg" width="100%" alt="Animated CUSUM diagram showing how gradual deviations accumulate against a configurable threshold"/>

</div>

## 5. From channels to systems to a smoothed trajectory

Channels map into physiological groups (for example, cardiovascular, oxygenation, respiratory, temperature, and perfusion). First, average the available channel scores inside each represented system \(g\):

$$
Q_{g,t}=\frac{1}{|J_{g,t}|}\sum_{j\in J_{g,t}}q_{j,t}
$$

Then take the equal-weight mean of the represented systems:

$$
u_t=\frac{1}{|G_t|}\sum_{g\in G_t}Q_{g,t}
$$

Equal system weights mean a group does not dominate only because it has more configured channels. An exponentially weighted moving average (EWMA) smooths the aggregate:

$$
S_t=\alpha u_t+(1-\alpha)S_{t-1}
$$

The implementation also tracks consecutive channel deviations and cross-system concordance. It withholds a scored aggregate unless coverage, scored-channel count, and represented-system minimums pass. The default \(\alpha\), score cutoffs, persistence step count, and minimums are configurable engineering values, not learned medical weights or clinically selected thresholds.

<div align="center">

<img src="assets/math-ewma-systems.svg" width="100%" alt="Animated diagram of channel aggregation, equal-weight system averaging, and EWMA smoothing"/>

</div>

### What the adaptive-twin states mean

The implementation can emit states such as \`insufficient_data\`, \`within_person_range\`, \`deviation_detected\`, \`marked_deviation\`, \`persistent_multisystem_deviation\`, \`cumulative_shift_detected\`, and \`cumulative_multisystem_shift\`.

These names summarise the algorithm's configured rules. They do not describe a diagnosis, severity classification, validated time-to-deterioration estimate, or clinical action. A \`trajectory_score\` is a unitless heuristic.

## 6. VITALIS-PB: causal patient-baseline feature engineering

The separate retrospective VITALIS-PB feature generator creates personal-baseline features for patient \(i\), variable \(j\), and row \(t\), using valid observations strictly before \(t\):

$$
b_{i,j,t}=\operatorname{median}\{x_{i,j,\tau}:\tau<t,\ x_{i,j,\tau}\text{ observed}\}
$$

$$
d_{i,j,t}=x_{i,j,t}-b_{i,j,t},\qquad z_{i,j,t}=\frac{d_{i,j,t}}{s_{i,j,t}}
$$

The experimental feature set can include current measurements, existing covariates, within-patient lags, one-step deltas, trailing six-row means, personal baseline, deviation, and robust normalised deviation. By default, the PB generator requires at least three previous valid observations; when scale is too small or unavailable, normalized deviation stays missing for the training-fold imputation pipeline rather than being assigned an arbitrary value.

<div align="center">

<img src="assets/math-personal-baseline.svg" width="100%" alt="Animated flow from earlier observations to causal baseline features and a supervised model"/>

</div>

The supervised model in this workflow is logistic regression. Imputation, missingness indicators, feature filtering, and scaling are learned from training folds only. Patient-level groups must not cross train, validation, and test partitions. The current implementation does not know a patient's true healthy state and does not establish clinical utility or algorithmic novelty.

## 7. Temporal supervised model and 1-, 3-, and 6-hour targets

For the future-label experiment, if the current Challenge label is zero, the target is whether any of the next \(H\) hourly Challenge labels is positive:

$$
Y^{(H)}_{i,t}=\mathbb{1}\left[Y_{i,t}=0\ \land\ \max_{r=1,\ldots,H}Y_{i,t+r}=1\right]
$$

The configured horizons are \(H\in\{1,3,6\}\). The last \(H\) rows per patient are excluded when a complete forward window is not available. The target does not cross patient boundaries.

<div align="center">

<img src="assets/math-horizon-forecast.svg" width="100%" alt="Animated diagram of a retrospective supervised future Challenge-label-window target"/>

</div>

**Crucial label definition:** PhysioNet/CinC Challenge 2019's supplied \`SepsisLabel\` already uses a six-hour lead convention. These experiments forecast entry into that challenge-positive label window. They do not predict an independently adjudicated biological sepsis-onset time. Set B is a held-out benchmark evaluation partition within the same challenge—not independent external clinical validation.

## 8. Keep twin and supervised outputs independent

<div align="center">

<img src="assets/math-dual-output.svg" width="100%" alt="Animated illustration showing the adaptive twin heuristic and supervised model output as separate streams that must not be fused"/>

</div>

| Adaptive twin | Supervised workflow |
|---|---|
| Online heuristic against rolling and frozen references | Retrospective fitted classifier for a defined label |
| Unitless deviation, persistence, coverage and trajectory summary | Probability/score for a specific benchmark target, when a model is fitted and available |
| Not a clinical risk probability | Not established as calibrated or clinically actionable |
| No clinical recommendation | No clinical recommendation |

The integrated interface deliberately returns an unavailable/null supervised probability when no frozen predictor is supplied. It does not replace that missing output with zero, and it does not convert the twin score into a probability.

## 9. Validation is part of the algorithm

<div align="center">

<img src="assets/math-validation-gates.svg" width="100%" alt="Animated research validation gates from software tests and reproducibility through independent cohort and governance review"/>

</div>

The validation work still matters as much as the formulas. The research programme must keep software correctness, exact-source reproducibility, patient-level leakage safeguards, model calibration, subgroup and missingness analysis, genuinely independent-cohort evaluation, and clinical/governance review as separate gates. Synthetic edge-case tests show behavior on constructed examples; they do not validate real sensors or clinical outcomes.

### Useful source files and reproducibility documents

- [Adaptive twin algorithm and validation contract](ADAPTIVE_TWIN_IMPLEMENTATION.md)
- [Patient-baseline algorithm (VITALIS-PB)](VITALIS_PB_ALGORITHM.md)
- [Future-label forecasting protocol](HORIZON_FORECASTING.md)
- [Separate output/interface contract](STREAMING_SUPERVISED_INTERFACE.md)
- [Research model card](MODEL_CARD.md)
- [Strict source reproducibility runbook](STRICT_SOURCE_REPRODUCIBILITY_RUNBOOK.md)
- [Independent evaluation protocol](INDEPENDENT_EVALUATION_PROTOCOL.md)
- Run the synthetic adaptive-twin example locally: \`python scripts/demo_adaptive_twin.py\`

---

<div align="center">

**VITALIS is a research prototype, not a medical device.** Do not use its outputs for diagnosis, triage, monitoring, treatment, or other patient-care decisions. No clinical validity, novelty, or patentability is claimed.

</div>
