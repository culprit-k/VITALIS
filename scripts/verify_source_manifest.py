#!/usr/bin/env python3
"""Create an external source/environment manifest for a clean VITALIS checkout.

This verifies selected working-tree files against Git blobs at HEAD. It does
not verify dataset provenance or reproduce model results.
"""
from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCE_PATHS = (
    "pyproject.toml",
    "scripts/evaluate_horizon_cross_cohort.py",
    "scripts/evaluate_horizon_calibration.py",
    "scripts/bootstrap_heldout_scores_fast.py",
    "scripts/verify_source_manifest.py",
    "src/vitalis/horizon.py",
    "src/vitalis/utility.py",
)


def git(root: Path, *args: str) -> str:
    """Run Git and return stdout, raising a useful error on failure."""
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode:
        detail = result.stderr.strip()
        raise ValueError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout.strip()


def build_manifest(root: Path) -> dict[str, object]:
    """Verify clean-tree/source-blob invariants and capture environment details."""
    root = root.resolve()
    if not root.is_dir():
        raise ValueError("root must be an existing directory")
    git_root = Path(git(root, "rev-parse", "--show-toplevel")).resolve()
    if root != git_root:
        raise ValueError(f"--root must be the repository top-level directory: {git_root}")

    status = git(root, "status", "--porcelain", "--untracked-files=all")
    if status:
        raise ValueError("working tree is not clean; commit or remove changes before manifest capture")

    commit = git(root, "rev-parse", "HEAD")
    tree = git(root, "rev-parse", "HEAD^{tree}")
    source_checks = []
    for relative_path in SOURCE_PATHS:
        path = root / relative_path
        if not path.is_file():
            raise ValueError(f"required source file is missing: {relative_path}")
        expected = git(root, "rev-parse", f"HEAD:{relative_path}")
        actual = git(root, "hash-object", relative_path)
        if expected != actual:
            raise ValueError(f"source blob mismatch at {relative_path}: expected {expected}, got {actual}")
        source_checks.append({
            "path": relative_path,
            "git_blob_sha": expected,
            "working_tree_blob_sha": actual,
            "match": True,
        })

    freeze = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if freeze.returncode:
        raise ValueError(f"pip freeze failed: {freeze.stderr.strip()}")

    return {
        "manifest_version": 1,
        "verified": True,
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "repository_root_name": root.name,
        "git_commit": commit,
        "git_tree": tree,
        "git_branch": git(root, "branch", "--show-current") or None,
        "working_tree_clean": True,
        "source_checks": source_checks,
        "runtime": {
            "python_version": sys.version,
            "python_executable_name": Path(sys.executable).name,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "pip_freeze": freeze.stdout.splitlines(),
        },
        "scope_note": (
            "Source and environment provenance only. This manifest does not validate "
            "data-source provenance, model metrics, clinical performance, or full-cohort reproduction."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True, help="manifest JSON path outside the repository")
    args = parser.parse_args()

    root = args.root.resolve()
    output = args.output.resolve()
    try:
        git_root = Path(git(root, "rev-parse", "--show-toplevel")).resolve()
        if output == git_root or git_root in output.parents:
            parser.error("--output must be outside the Git repository")
        manifest = build_manifest(root)
    except ValueError as exc:
        parser.error(str(exc))

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "verified": manifest["verified"],
        "commit": manifest["git_commit"],
        "source_files_verified": len(manifest["source_checks"]),
        "manifest_path": str(output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
