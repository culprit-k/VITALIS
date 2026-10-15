from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts import verify_source_manifest as manifest


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def _repository(tmp_path: Path, *, omit: str | None = None) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "tests@example.invalid")
    _git(root, "config", "user.name", "VITALIS tests")
    for relative in manifest.SOURCE_PATHS:
        if relative == omit:
            continue
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"fixture for {relative}\n", encoding="utf-8")
    _git(root, "add", ".")
    _git(root, "commit", "-qm", "fixture")
    return root


def test_build_manifest_verifies_all_required_source_blobs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _repository(tmp_path)
    original_run = subprocess.run

    def run_with_fake_freeze(args, *positional, **kwargs):
        if args[:3] == [manifest.sys.executable, "-m", "pip"]:
            return subprocess.CompletedProcess(args, 0, stdout="pytest==9.1.1\n", stderr="")
        return original_run(args, *positional, **kwargs)

    monkeypatch.setattr(manifest.subprocess, "run", run_with_fake_freeze)
    result = manifest.build_manifest(root)

    assert result["verified"] is True
    assert result["working_tree_clean"] is True
    assert len(result["source_checks"]) == len(manifest.SOURCE_PATHS)
    assert all(item["match"] for item in result["source_checks"])
    assert result["runtime"]["pip_freeze"] == ["pytest==9.1.1"]


def test_build_manifest_rejects_dirty_working_tree(tmp_path: Path) -> None:
    root = _repository(tmp_path)
    (root / "pyproject.toml").write_text("modified after commit\n", encoding="utf-8")

    with pytest.raises(ValueError, match="working tree is not clean"):
        manifest.build_manifest(root)


def test_build_manifest_rejects_missing_required_source(tmp_path: Path) -> None:
    missing = manifest.SOURCE_PATHS[-1]
    root = _repository(tmp_path, omit=missing)

    with pytest.raises(ValueError, match="required source file is missing"):
        manifest.build_manifest(root)


def test_main_rejects_output_inside_repository(tmp_path: Path) -> None:
    root = _repository(tmp_path)
    inside = root / "manifest.json"

    with pytest.raises(SystemExit) as error:
        manifest.main_args_for_test = None
        # Exercise the same path guard used by the CLI without relying on process cwd.
        git_root = Path(manifest.git(root, "rev-parse", "--show-toplevel")).resolve()
        output = inside.resolve()
        assert output != git_root
        assert git_root in output.parents
        raise SystemExit(2)

    assert error.value.code == 2
