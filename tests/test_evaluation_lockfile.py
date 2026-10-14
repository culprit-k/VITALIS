import importlib.util
from pathlib import Path

MODULE = Path(__file__).parents[1] / "scripts" / "validate_evaluation_lockfile.py"
SPEC = importlib.util.spec_from_file_location("evaluation_lockfile_validator", MODULE)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def valid_lockfile():
    approvals = {
        key: {"approved": True, "reviewer": f"Reviewer {key}", "date": "2026-10-15"}
        for key in ("clinical_owner", "independent_statistician", "data_governance",
                    "ethics_determination", "software_reviewer")
    }
    return {
        "status": "frozen",
        "protocol_version": "1.0",
        "model_commit_sha": "a" * 40,
        "environment_lock_hash": "b" * 64,
        "feature_schema_hash": "c" * 64,
        "model_artifact_hash": "d" * 64,
        "population": "Adult ICU admissions at participating site",
        "prediction_index_time": "Hourly index time before outcome window",
        "event_definition": "Independently adjudicated clinical event time",
        "primary_endpoint": "Sensitivity for adjudicated event within 6 hours",
        "analysis_plan_version": "SAP-1.0",
        "evaluation_cohort": {
            "name": "Independent Site C cohort",
            "independent": True,
            "data_manifest_sha256": "e" * 64,
        },
        "target": {
            "definition": "Adjudicated clinical sepsis onset within forecast horizon",
            "claim_type": "clinical_onset",
            "challenge_label_proxy": False,
            "independently_adjudicated": True,
        },
        "horizons_hours": [1, 3, 6],
        "thresholds": [0.005, 0.01],
        "primary_metrics": ["sensitivity"],
        "secondary_metrics": ["PPV", "alerts per patient-day", "window coverage"],
        "subgroup_plan": ["site", "sex", "age band"],
        "missing_data_plan": ["Report missingness and freshness by feature"],
        "stopping_rules": ["Pause if data integrity fails"],
        "frozen_policy": {
            "model_family": "Logistic regression",
            "preprocessing": "Frozen median imputation and indicators",
            "calibration": "Frozen Platt calibration artifact",
            "feature_set": "Versioned temporal feature schema",
            "refractory_hours": 6,
            "threshold_selection_frozen": True,
        },
        "approvals": approvals,
    }


def test_valid_frozen_independent_evaluation_lockfile_passes():
    assert MOD.validate_lockfile(valid_lockfile()) == []


def test_template_is_not_accepted_as_frozen_protocol():
    from pathlib import Path
    import json
    template = Path(__file__).parents[1] / "configs" / "independent_evaluation_lockfile.template.json"
    errors = MOD.validate_lockfile(json.loads(template.read_text(encoding="utf-8")))
    assert any("status must be 'frozen'" in error for error in errors)
    assert any("independent must be true" in error for error in errors)


def test_rejects_set_b_as_final_independent_cohort():
    data = valid_lockfile()
    data["evaluation_cohort"]["name"] = "Set B"
    errors = MOD.validate_lockfile(data)
    assert any("cannot be the final" in error for error in errors)


def test_rejects_challenge_proxy_for_clinical_onset_claim():
    data = valid_lockfile()
    data["target"]["challenge_label_proxy"] = True
    errors = MOD.validate_lockfile(data)
    assert any("cannot support a clinical-onset claim" in error for error in errors)


def test_rejects_missing_independent_approval():
    data = valid_lockfile()
    data["approvals"]["independent_statistician"]["approved"] = False
    errors = MOD.validate_lockfile(data)
    assert any("approvals.independent_statistician" in error for error in errors)


def test_rejects_unfrozen_threshold_policy():
    data = valid_lockfile()
    data["frozen_policy"]["threshold_selection_frozen"] = False
    errors = MOD.validate_lockfile(data)
    assert any("threshold_selection_frozen must be true" in error for error in errors)



def test_rejects_malformed_model_commit_and_artifact_hashes():
    data = valid_lockfile()
    data["model_commit_sha"] = "g" * 40
    data["environment_lock_hash"] = "a" * 63
    data["feature_schema_hash"] = "z" * 64
    data["model_artifact_hash"] = "not-a-hash"
    errors = MOD.validate_lockfile(data)
    assert any("model_commit_sha must be a 40-character hexadecimal digest" in e for e in errors)
    assert any("environment_lock_hash must be a 64-character hexadecimal digest" in e for e in errors)
    assert any("feature_schema_hash must be a 64-character hexadecimal digest" in e for e in errors)
    assert any("model_artifact_hash must be a 64-character hexadecimal digest" in e for e in errors)
