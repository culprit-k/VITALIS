import importlib.util
from pathlib import Path
import subprocess

import pytest

MODULE = Path(__file__).parents[1] / "scripts" / "audit_git_history.py"
SPEC = importlib.util.spec_from_file_location("audit_git_history", MODULE)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def init_repo(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-q")
    git(root, "config", "user.name", "VITALIS test")
    git(root, "config", "user.email", "test@example.invalid")
    return root


def commit_file(root, name, content):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content if isinstance(content, bytes) else content.encode())
    git(root, "add", "--", name)
    git(root, "commit", "-qm", "fixture")
    return path


def test_history_audit_finds_deleted_data_artifact_path(tmp_path):
    root = init_repo(tmp_path)
    path = commit_file(root, "private/training.psv", "synthetic,label\n1,0\n")
    git(root, "rm", "-q", str(path.relative_to(root)))
    git(root, "commit", "-qm", "remove artifact")
    report = MOD.audit_history(root)
    assert any(f["rule"] == "historical_data_artifact_path"
               and f["path"] == "private/training.psv" for f in report["findings"])


def test_history_audit_flags_high_confidence_token_without_disclosing_value(tmp_path):
    root = init_repo(tmp_path)
    token = "ghp_" + "A" * 36
    commit_file(root, "notes.txt", "placeholder credential: " + token)
    report = MOD.audit_history(root)
    matches = [f for f in report["findings"] if f["rule"] == "possible_github_token"]
    assert matches
    assert token not in str(report)


def test_history_audit_flags_oversized_historical_blob(tmp_path):
    root = init_repo(tmp_path)
    commit_file(root, "large.txt", "x" * 100)
    report = MOD.audit_history(root, max_bytes=32)
    assert any(f["rule"] == "historical_oversized_blob" and f["path"] == "large.txt"
               for f in report["findings"])


def test_history_audit_rejects_shallow_repository(tmp_path):
    root = init_repo(tmp_path)
    commit_file(root, "notes.txt", "synthetic fixture")
    # Simulate a shallow repository using Git's standard marker.
    (root / ".git" / "shallow").write_text("0" * 40 + "\n", encoding="ascii")
    with pytest.raises(ValueError, match="shallow"):
        MOD.audit_history(root)


def test_history_audit_rejects_non_git_directory(tmp_path):
    root = tmp_path / "not-a-repo"
    root.mkdir()
    with pytest.raises(ValueError, match="Git working tree"):
        MOD.audit_history(root)
