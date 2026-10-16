# VITALIS release acceptance matrix

**Release type:** research software only. This matrix does not authorize clinical deployment.

A gate is **PASS** only when its evidence is reproducible from a named commit and independently inspectable. A written procedure, a reconstructed local run, or a successful CI run alone is not proof of a full-cohort reproduction.

| Gate | Acceptance criteria | Current disposition |
|---|---|---|
| Historical baseline reconciliation | Freeze both historical artifacts and their provenance; reproduce each candidate from a clean checkout; compare all 42 expected pairs / 84 scalar values using the existing six-decimal acceptance rule; publish a machine-readable mismatch report; explain every mismatch from evidence. No relaxing tolerance, dropping pairs, rounding inputs earlier, or overwriting historical values. | **PASS — current head reproduced** — clean-checkout Python 3.11 run [#38875089170](https://github.com/culprit-k/VITALIS/actions/runs/38875089170), attempt 2 on commit `f46bfa7ecf56631a3b4ff8b1e8c97e95abdcb6a3`, passed unchanged six-decimal reconciliation: 42/42 mean/SD pairs, 84/84 scalar values, zero mismatches. Python 3.13 diagnostic [#38875089216](https://github.com/culprit-k/VITALIS/actions/runs/38875089216) also completed successfully as diagnostic evidence only. Review the retained aggregate artifact before release. |
| Probability quality | Compare raw and calibrated probabilities on identical eligible patients/rows; report Brier score, log loss, mean predicted probability, calibration diagnostics, AUROC/AUPRC, and constant-prevalence reference. Preserve patient-cluster uncertainty and report seed × horizon results. Calibration must not be declared successful merely because ranking metrics improve. | **PARTIAL** — paired static-versus-temporal comparison and calibration reports exist. Brier/calibration evidence is mixed; Set-B Brier can remain worse than prevalence reference. No probability-quality winner is established. |
| Set-B isolation | Set B is used only for final retrospective evaluation; no threshold, feature, model, or calibration selection from it. | **REQUIRED INVARIANT** |
| Twin/supervised interface | Distinct versioned output fields; heuristic twin score is never represented as probability; explicit missing/unavailable states; timestamps, units, quality, freshness, model/schema/calibration versions; contract and synthetic end-to-end tests. | **PARTIAL** — runtime envelope adapter, contract tests, and synthetic demo are implemented; latest standard CI passed on current head. No frozen supervised model artifact is wired into the demo, so trained-model inference remains unavailable. |
| Reproducible environment | Clean checkout; source/blob manifest; supported Python version; dependency inventory and successful `pip check`; source compile; full tests; privacy/hygiene checks; pinned/locked environment or reviewed immutable container. | **PASS for automated current-head checks** — standard tests [#38875089161](https://github.com/culprit-k/VITALIS/actions/runs/38875089161), dashboard tests [#38875089165](https://github.com/culprit-k/VITALIS/actions/runs/38875089165), Python 3.11 full reproduction [#38875089170](https://github.com/culprit-k/VITALIS/actions/runs/38875089170), and Python 3.13 diagnostic [#38875089216](https://github.com/culprit-k/VITALIS/actions/runs/38875089216) all passed on `f46bfa7ecf56631a3b4ff8b1e8c97e95abdcb6a3`. Human history/privacy triage and independent methods review remain outstanding. |
| Working demonstration | One command runs a deterministic synthetic-only stream; a second integration demonstration covers the explicit supervised-unavailable state and, where a model artifact is supplied, a versioned supervised result. Output semantics and non-clinical limitations are printed. | **IMPLEMENTED; CI PASSED** — deterministic synthetic integrated demo is wired into the standard test workflow, which passed on commit `33fa7f6`. No frozen supervised model artifact is connected. |
| Model limitations and governance | Model card, target/label semantics, limitations, data boundary, and research-only status are visible; no patient-level data, caches, credentials, or predictions enter Git. | **PARTIAL** — documentation and hygiene checks exist; final history/privacy audit and independent review still required. |
| Release decision | All blockers resolved, CI passed on exact release commit, final diff and history reviewed, artifacts reproducible, and explicit human release decision recorded. | **BLOCKED pending human review** — automated current-head gates pass, but history-scan human triage, independent methods review, final diff review, and an explicit release decision remain outstanding. Keep PR draft/unmerged. |

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


## Latest cross-runtime diagnostic (16 October 2026)

- Python 3.13 diagnostic run [#38831794049](https://github.com/culprit-k/VITALIS/actions/runs/38831794049) completed all cohort/cache/evaluation steps on source commit `33fa7f6362e44ee126ddbebd20be6dc9738a12cb`; its comparison remains 37/42 mean/SD pairs and 75/84 scalar matches.
- Earlier pinned Python 3.11 run [#38748749241](https://github.com/culprit-k/VITALIS/actions/runs/38748749241) reported 42/42 pairs and 84/84 scalar matches, but its evaluator blob was `5739a64807b970f0c945404896fc5536dba687da`; the current evaluator blob is `891b84ad4a5da039f1dc38411211c503c971167c`. Do not count the earlier pass as acceptance evidence for the current evaluator.
- The audited cohort and cache fingerprints match across these artifacts. The remaining controlled comparison is a fresh pinned Python 3.11 run on the current evaluator source, followed by same-source comparison with Python 3.13.
- The workflow configuration fix is committed as `b626ca6f723b293820a17175a11396018112ab29`; the same-cache/source diagnosis is documented in `docs/REPRODUCTION_FAILURE_TRIAGE_2026-10-15.md`.


## Updated current-head status — 16 October 2026

- Latest PR head at the time of this update: `4346f0f1e5ef1de3ac9a2213f7912a3507d27aa6`; PR #2 remains draft/open/unmerged.
- Standard tests [#38859873903](https://github.com/culprit-k/VITALIS/actions/runs/38859873903) and dashboard tests [#38859873797](https://github.com/culprit-k/VITALIS/actions/runs/38859873797) passed on that head.
- Current-head pinned Python 3.11 full-cohort run [#38859873792](https://github.com/culprit-k/VITALIS/actions/runs/38859873792) and Python 3.13 diagnostic [#38859873780](https://github.com/culprit-k/VITALIS/actions/runs/38859873780) were still in progress when this status was recorded. No final claim about either run is made here.
- Earlier successful controlled runs establish that the preserved aggregate can be reproduced with OpenBLAS `SkylakeX`; they do not replace the pending current-head checks.
- Probability-quality decision remains unchanged: no model is promoted as clinically superior; physiology features improve ranking modestly but worsen Brier; Platt calibration at the fixed 0.5 reference operating point has near-zero sensitivity. Set B remains evaluation-only.
- The exploratory 5% Set-A feature-coverage rule is not clinically justified and must not be presented as optimal.
- Release remains blocked pending current-head workflow completion, a complete history/privacy audit, and independent methods review. Do not merge PR #2 or initiate hardware integration yet.


## Current-head verification checkpoint — 16 October 2026

- Commit: `f46bfa7ecf56631a3b4ff8b1e8c97e95abdcb6a3`.
- Standard tests: [#38875089161](https://github.com/culprit-k/VITALIS/actions/runs/38875089161) — passed.
- Reporting/dashboard tests: [#38875089165](https://github.com/culprit-k/VITALIS/actions/runs/38875089165) — passed.
- Clean-checkout pinned Python 3.11 full-cohort reproduction: [#38875089170](https://github.com/culprit-k/VITALIS/actions/runs/38875089170), attempt 2 — passed unchanged reconciliation, 42/42 pairs, 84/84 scalar values, zero mismatches.
- Python 3.13 diagnostic: [#38875089216](https://github.com/culprit-k/VITALIS/actions/runs/38875089216) — completed successfully; diagnostic only, not the pinned acceptance gate.
- Reachable-history scan in standard CI reported 780 commits, 760 unique blobs, and zero automated findings at this commit. This is limited to refs fetched by CI and heuristic patterns; human triage and any external GitHub security scan remain separate.
- Still blocked: independent qualified methods review, final full diff/history human review, and explicit human research-release decision. No clinical validation is implied.
