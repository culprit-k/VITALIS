# VITALIS Research Prototype — v0.1.0 (Research Preview)

**Release date:** 29 October 2026  
**Release type:** Research software preview — not a clinical release  
**Repository:** https://github.com/culprit-k/VITALIS

## Summary

VITALIS explores adaptive physiological baseline modelling and research workflows for studying early warning signals of sepsis-related clinical deterioration. This preview brings together retrospective benchmark workflows, an adaptive-deviation demonstration, a synthetic streaming interface, aggregate evaluation dashboards, research protocols, and a proposed hardware-integration blueprint.

This is a software research snapshot. It is not a completed wearable device, a medical device, or a clinically validated decision-support system.

## Included capabilities

- Retrospective static and temporal benchmark training/evaluation workflows.
- Patient-level split and evaluation safeguards, with the Challenge Set B reserved for evaluation rather than model tuning.
- An adaptive physiological deviation component and synthetic signal demonstration.
- A timestamped stream contract with unit/freshness checks, quality flags, out-of-order rejection, and session reset.
- Synthetic ESP32-to-host software gateway for generated test values only.
- Aggregate-only evaluation dashboard and research documentation.
- Hardware-integration plan for a future wrist-worn sensor gateway and bedside compute unit.

## Evidence and limitations

The repository records earlier full-cohort reproduction evidence, including a documented reconciliation of 42/42 metric mean/sample-standard-deviation pairs and 84/84 scalar values at the stated six-decimal tolerance. These are historical, commit-specific results; they must not be assumed to have been freshly reproduced on the exact repository head associated with this release note.

The documented Set A-to-Set B benchmark is retrospective benchmark evaluation, not external clinical validation. The target is the Challenge label window, not independently adjudicated sepsis onset. The documented results do not establish clinically useful calibrated risk probabilities or an appropriate clinical alert threshold.

The adaptive twin's deviation/trajectory outputs are not themselves calibrated clinical risk estimates. The integrated demonstration does not invent supervised probabilities when no trained, versioned predictor is loaded.

## Hardware status

The wristband, custom PCB, sensor interfaces, battery/charging design, and bedside hardware are **proposed work, not completed hardware**. The synthetic ESP32 gateway emits generated test values and does not yet acquire data from physical sensors. Do not connect this research software to a patient or use the synthetic bench as a sensor-safety test.

## Not yet completed

- Fresh clean-checkout reproduction and CI verification on the exact release commit.
- Independent statistical/clinical methods review.
- Physical bench testing and electrical/biomedical safety review.
- Approved access to a genuinely independent cohort, institutional governance review, and external evaluation.
- Prospective clinical evaluation, regulatory assessment, and evidence of clinical utility.

## Safety and intended use

**Research and educational use only. Do not use VITALIS to diagnose, triage, monitor, or make treatment decisions for any person. Do not connect the prototype to a patient.** No clinical validity, patient benefit, regulatory authorization, novelty, or patentability is claimed.

## Suggested first run

See the repository [README](README.md) for installation and tests, and run the generated-signal demo:

```bash
python scripts/demo_adaptive_twin.py
python scripts/demo_integrated_inference.py
```

For the dashboard, follow the README instructions. All demo values are synthetic.
