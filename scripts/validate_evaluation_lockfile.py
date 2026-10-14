#!/usr/bin/env python3
"""Validate a frozen VITALIS independent-evaluation lockfile before outcome access.

This is a completeness/invariant check, not ethics approval or proof that the
model is clinically safe. It intentionally refuses templates and Set-B reuse.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def validate_lockfile(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["lockfile root must be a JSON object"]
    if data.get("status") != "frozen":
        errors.append("status must be 'frozen'; templates/drafts cannot authorize evaluation")

    required_strings = {
        "protocol_version": data.get("protocol_version"),
        "model_commit_sha": data.get("model_commit_sha"),
        "environment_lock_hash": data.get("environment_lock_hash"),
        "feature_schema_hash": data.get("feature_schema_hash"),
        "model_artifact_hash": data.get("model_artifact_hash"),
        "population": data.get("population"),
        "event_definition": data.get("event_definition"),
        "primary_endpoint": data.get("primary_endpoint"),
        "prediction_index_time": data.get("prediction_index_time"),
        "analysis_plan_version": data.get("analysis_plan_version"),
    }
    for key, value in required_strings.items():
        if not isinstance(value, str) or not value.strip() or value.strip().lower() in {
            "todo", "tbd", "placeholder", "fill me", "unknown"
        }:
            errors.append(f"{key} must be a specific non-placeholder string")

    # Freeze-gate identifiers must be actual immutable content identifiers,
    # not merely nonempty strings. This is syntax validation, not verification
    # that the referenced artifact or environment is trustworthy.
    hash_lengths = {
        "model_commit_sha": 40,
        "environment_lock_hash": 64,
        "feature_schema_hash": 64,
        "model_artifact_hash": 64,
    }
    for key, length in hash_lengths.items():
        value = data.get(key)
        if isinstance(value, str) and value.strip().lower() not in {
            "todo", "tbd", "placeholder", "fill me", "unknown"
        } and (len(value) != length or any(c not in "0123456789abcdefABCDEF" for c in value)):
            errors.append(f"{key} must be a {length}-character hexadecimal digest")

    cohort = data.get("evaluation_cohort")
    if not isinstance(cohort, dict):
        errors.append("evaluation_cohort must be an object")
    else:
        if cohort.get("independent") is not True:
            errors.append("evaluation_cohort.independent must be true")
        name = cohort.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append("evaluation_cohort.name must identify the new cohort")
        elif name.strip().lower() in {"set b", "training_setb", "physionet set b", "challenge training set b"}:
            errors.append("Set B has already been inspected and cannot be the final threshold-policy evaluation cohort")
        if not isinstance(cohort.get("data_manifest_sha256"), str) or len(cohort["data_manifest_sha256"]) != 64:
            errors.append("evaluation_cohort.data_manifest_sha256 must be a SHA-256 hex digest")
        elif any(c not in "0123456789abcdefABCDEF" for c in cohort["data_manifest_sha256"]):
            errors.append("evaluation_cohort.data_manifest_sha256 must be hexadecimal")

    target = data.get("target")
    if not isinstance(target, dict):
        errors.append("target must be an object")
    else:
        if not isinstance(target.get("definition"), str) or not target["definition"].strip():
            errors.append("target.definition must be explicit")
        if target.get("independently_adjudicated") is not True:
            errors.append("target.independently_adjudicated must be true for clinical-onset claims")
        if target.get("challenge_label_proxy") is True and target.get("claim_type") == "clinical_onset":
            errors.append("Challenge-label proxy cannot support a clinical-onset claim")
        if target.get("claim_type") not in {"proxy-label prediction", "clinical_onset"}:
            errors.append("target.claim_type must be 'proxy-label prediction' or 'clinical_onset'")

    horizons = data.get("horizons_hours")
    if not isinstance(horizons, list) or not horizons or any(
        isinstance(h, bool) or not isinstance(h, int) or h < 1 for h in horizons
    ) or len(set(horizons)) != len(horizons):
        errors.append("horizons_hours must be a nonempty list of unique positive integers")

    thresholds = data.get("thresholds")
    if not isinstance(thresholds, list) or not thresholds or any(
        isinstance(t, bool) or not isinstance(t, (int, float)) or not 0 < t <= 1 for t in thresholds
    ) or len(set(thresholds)) != len(thresholds):
        errors.append("thresholds must be a nonempty list of unique numbers in (0, 1]")

    for key in ("primary_metrics", "secondary_metrics", "subgroup_plan", "missing_data_plan", "stopping_rules"):
        value = data.get(key)
        if not isinstance(value, list) or not value or any(not isinstance(x, str) or not x.strip() for x in value):
            errors.append(f"{key} must be a nonempty list of explicit entries")

    policy = data.get("frozen_policy")
    if not isinstance(policy, dict):
        errors.append("frozen_policy must be an object")
    else:
        for key in ("model_family", "preprocessing", "calibration", "refractory_hours", "feature_set"):
            value = policy.get(key)
            if value is None or value == "" or value == []:
                errors.append(f"frozen_policy.{key} must be specified")
        refractory = policy.get("refractory_hours")
        if isinstance(refractory, bool) or not isinstance(refractory, int) or refractory < 1:
            errors.append("frozen_policy.refractory_hours must be a positive integer")
        if policy.get("threshold_selection_frozen") is not True:
            errors.append("frozen_policy.threshold_selection_frozen must be true")

    approvals = data.get("approvals")
    if not isinstance(approvals, dict):
        errors.append("approvals must be an object")
    else:
        for key in ("clinical_owner", "independent_statistician", "data_governance", "ethics_determination", "software_reviewer"):
            entry = approvals.get(key)
            if not isinstance(entry, dict) or entry.get("approved") is not True or not isinstance(entry.get("reviewer"), str) or not entry["reviewer"].strip() or not isinstance(entry.get("date"), str) or not entry["date"].strip():
                errors.append(f"approvals.{key} requires approved=true, reviewer, and date")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lockfile", type=Path, help="JSON lockfile stored in an approved environment")
    args = parser.parse_args()
    try:
        data = json.loads(args.lockfile.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        parser.error(f"cannot read JSON lockfile: {exc}")
    errors = validate_lockfile(data)
    if errors:
        print(json.dumps({"valid": False, "errors": errors}, indent=2))
        return 1
    print(json.dumps({
        "valid": True,
        "status": "frozen",
        "evaluation_cohort": data["evaluation_cohort"]["name"],
        "horizons_hours": data["horizons_hours"],
        "thresholds": data["thresholds"],
        "warning": "Completeness check only; does not replace independent review, governance approval, or clinical validation.",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
