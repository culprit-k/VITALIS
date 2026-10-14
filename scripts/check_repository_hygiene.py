#!/usr/bin/env python3
"""Fail-closed scan for data-bearing artifacts in the current repository tree.

This is a current-tree hygiene guard, not a history-wide secret scanner and
not proof that private data was never committed in an earlier revision.
"""
from __future__ import annotations

import argparse
from pathlib import Path

FORBIDDEN_SUFFIXES = {
    ".psv", ".npz", ".npy", ".parquet", ".feather", ".arrow",
    ".pkl", ".pickle", ".joblib", ".sqlite", ".sqlite3", ".db",
    ".csv", ".tsv", ".xlsx", ".xls", ".sav", ".dta",
}
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache"}


def audit_repository(root: Path, *, max_bytes: int = 5 * 1024 * 1024) -> list[str]:
    """Return actionable issues for data-like files and unexpectedly large blobs."""
    if max_bytes < 1:
        raise ValueError("max_bytes must be positive")
    root = root.resolve()
    if not root.is_dir():
        raise ValueError("root must be an existing directory")
    issues = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        rel = path.relative_to(root).as_posix()
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            issues.append(f"forbidden data/artifact extension: {rel}")
        try:
            size = path.stat().st_size
        except OSError as exc:
            issues.append(f"could not stat {rel}: {exc}")
            continue
        if size > max_bytes:
            issues.append(f"file exceeds {max_bytes} byte limit ({size} bytes): {rel}")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--max-bytes", type=int, default=5 * 1024 * 1024)
    args = parser.parse_args()
    try:
        issues = audit_repository(args.root, max_bytes=args.max_bytes)
    except ValueError as exc:
        parser.error(str(exc))
    if issues:
        print("Repository hygiene check FAILED:")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"Repository hygiene check passed: no forbidden data-like files or files over {args.max_bytes} bytes.")
    print("Scope: current working tree only; Git history and secrets require separate review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
