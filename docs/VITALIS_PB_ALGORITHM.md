# VITALIS-PB: Patient Baseline Deviation Model

**Status:** proposed research algorithm implemented as an experimental feature generator. It is not clinically validated and is not claimed to be novel or patentable.

## Mathematical definition

For patient \(i\), variable \(j\), and hourly index \(t\), let \(x_{i,j,t}\) be the observed measurement. Only valid observations strictly before \(t\) are eligible for the personal reference.

The causal reference is the expanding median:

\[
b_{i,j,t}=\operatorname{median}\{x_{i,j,\tau}:\tau<t,\;x_{i,j,\tau}\text{ observed}\}.
\]

The robust scale is defined from historical absolute deviations from the causal baseline available at each earlier time:

\[
s_{i,j,t}=1.4826\operatorname{median}\{|x_{i,j,\tau}-b_{i,j,\tau}|:\tau<t\}.
\]

The raw personal deviation and normalized deviation are:

\[
d_{i,j,t}=x_{i,j,t}-b_{i,j,t},\qquad
z_{i,j,t}=\frac{d_{i,j,t}}{s_{i,j,t}}.
\]

The implementation requires at least three previous valid observations by default. If the robust scale is below a numerical floor, normalized deviation is missing rather than assigned an arbitrary value. Missingness is subsequently handled by the training-fold imputation pipeline. This avoids pretending a zero-variability baseline gives a well-defined z-score.

## Model comparison

The experimental personalized model combines:
- current candidate measurements and existing covariates;
- within-patient lag, one-step delta and trailing six-row mean features;
- causal personal baseline, deviation and robust normalized deviation features for prespecified physiological measurements.

A logistic regression learns coefficients from training patients only. Patient groups must be disjoint between train, validation and test. Any imputation and all-missing feature filtering are fitted on the training fold. The default threshold 0.5 is only a reference threshold, not a clinical operating point.

## Critical assumptions and limitations

1. The PSV row order is treated as chronological; input order must be verified before interpreting temporal features.
2. Baselines can be unreliable early in a stay and during prolonged abnormal physiology. The current implementation does not claim to identify a patient's true healthy baseline.
3. A patient's earlier ICU measurements are not necessarily healthy reference measurements.
4. Robust deviations may be undefined when historical variability is zero or insufficient; those values remain missing.
5. The feature generator must be compared against matched static and temporal baselines on identical patient splits.
6. Challenge `SepsisLabel` is used as supplied and is not shifted again. Row-level discrimination is not clinical event-level utility.
7. No clinical use, novelty, patentability, or regulatory claim follows from implementing this mathematical definition.

## Reproducibility

Use the model comparison command with a local PhysioNet/CinC Challenge 2019 training partition. The aggregate report includes all three models and metric deltas. Keep raw patient data and patient-level predictions outside the public repository.
