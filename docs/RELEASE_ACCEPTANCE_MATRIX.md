# VITALIS release acceptance matrix

**Release type:** research software only. This matrix does not authorize clinical deployment.

A gate is **PASS** only when its evidence is reproducible from a named commit and independently inspectable. A written procedure, a reconstructed local run, or a successful CI run alone is not proof of a full-cohort reproduction.

| Gate | Acceptance criteria | Current disposition |
|---|---|---|
| Historical baseline reconciliation | Freeze both historical artifacts and their provenance; reproduce each candidate from a clean checkout; compare all 42 expected pairs / 84 scalar values using the existing six-decimal acceptance rule; publish a machine-readable mismatch report; explain every mismatch from evidence. No relaxing tolerance, dropping pairs, rounding inputs earlier, or overwriting historical values. | **OPEN** — last recorded comparison reconciled 37/42 pairs and 75/84 scalars; five pairs / nine scalars remain unexplained. |
| Probability quality | Compare raw and calibrated probabilities on identical eligible patients/rows; report Brier score, log loss, mean predicted probability, calibration diagnostics, AUROC/AUPRC, and constant-prevalence reference. Preserve patient-cluster uncertainty and report seed × horizon results. Calibration must not be declared successful merely because ranking metrics improve. | **PARTIAL** — paired static-versus-temporal comparison and calibration reports exist. Brier/calibration evidence is mixed; Set-B Brier can remain worse than prevalence reference. No probability-quality winner is established. |
| Set-B isolation | Set B is used only for final retrospective evaluation; no threshold, feature, model, or calibration selection from it. | **REQUIRED INVARIANT** |
| Twin/supervised interface | Distinct versioned output fields; heuristic twin score is never represented as probability; explicit missing/unavailable states; timestamps, units, quality, freshness, model/schema/calibration versions; contract and synthetic end-to-end tests. | **PARTIAL** — runtime envelope adapter, contract tests, and synthetic demo are implemented. No frozen supervised model artifact is wired into the demo; actual trained-model inference and clean-checkout CI confirmation remain pending. |
| Reproducible environment | Clean checkout; source/blob manifest; supported Python version; dependency inventory and successful `pip check`; source compile; full tests; privacy/hygiene checks; pinned/locked environment or reviewed immutable container. | **PARTIAL** — CI/test workflow exists; full-cohort clean-checkout reproduction and fully locked environment remain outstanding. |
| Working demonstration | One command runs a deterministic synthetic-only stream; a second integration demonstration covers the explicit supervised-unavailable state and, where a model artifact is supplied, a versioned supervised result. Output semantics and non-clinical limitations are printed. | **IMPLEMENTED; CI PENDING** — deterministic synthetic integrated demo added and wired into CI; success is not claimed until the workflow completes. |
| Model limitations and governance | Model card, target/label semantics, limitations, data boundary, and research-only status are visible; no patient-level data, caches, credentials, or predictions enter Git. | **PARTIAL** — documentation and hygiene checks exist; final history/privacy audit and independent review still required. |
| Release decision | All blockers resolved, CI passed on exact release commit, final diff and history reviewed, artifacts reproducible, and explicit human release decision recorded. | **BLOCKED** — keep PR draft/unmerged. |

## Historical baseline protocol (non-negotiable)

1. Preserve the historical reference files unchanged and record their Git blob SHA and provenance.
2. Run the committed evaluator from a clean detached checkout with the exact documented data/cache inputs.
3. Compare expected and observed values without pre-rounding. Apply the already documented six-decimal acceptance rule only at the final comparison stage.
4. Emit per-pair and per-scalar expected value, observed value, absolute difference, pass/fail, source commit, and input-artifact identity.
5. Investigate mismatches by tracing source, split membership, feature schema, preprocessing, seeds, label handling, and environment. Never adjust acceptance criteria to make the run pass.
6. Keep raw data, caches, individual predictions, and row-level logs outside the repository.

## Probability-quality interpretation

Discrimination (AUROC/AUPRC) and probability quality (Brier/log loss/calibration) are different properties. Report both. A calibrated score can have poor discrimination; a high-ranking model can be overconfident or worse than a prevalence-only probability baseline. Report alert burden/operating-point results separately and do not select a threshold on Set B. Current retrospective results do not establish clinical utility.

## Research-only warning

The Challenge label already uses a six-hour lead convention and is not independently adjudicated biological onset. Set B is another cohort in the same challenge, not prospective clinical validation. VITALIS is not a medical device or validated clinical decision-support system; do not use its outputs to guide patient care.
