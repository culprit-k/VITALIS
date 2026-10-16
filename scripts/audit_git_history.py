#!/usr/bin/env python3
"""Audit reachable Git history for data artifacts, oversized blobs, and high-confidence secrets.

This local helper reports file paths, object/commit IDs, and rule names only;
it never prints matched credential text. A clean result is not a substitute
for GitHub secret scanning or independent security review.
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
from pathlib import Path

FORBIDDEN_SUFFIXES = {
    ".psv", ".npz", ".npy", ".parquet", ".feather", ".arrow", ".pkl",
    ".pickle", ".joblib", ".sqlite", ".sqlite3", ".db", ".csv", ".tsv",
    ".xlsx", ".xls", ".sav", ".dta",
}
SECRET_PATTERNS = {
    "private_key_block": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "aws_access_key_id": re.compile(rb"\bAKIA[0-9A-Z]{16}\b"),
    "github_token": re.compile(rb"\b(?:gh[pousr]_[A-Za-z0-9_]{30,}|github_pat_[A-Za-z0-9_]{50,})\b"),
    "slack_token": re.compile(rb"\bxox[baprs]-[0-9A-Za-z-]{10,}\b"),
    "google_api_key": re.compile(rb"\bAIza[0-9A-Za-z_-]{35}\b"),
}
SKIP_BINARY_MARKER = b"\x00"


def _git(root: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), *args], input=input_bytes,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise ValueError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout


def _parse_batch_objects(payload: bytes):
    """Yield (sha, object_type, content) from batch object output."""
    cursor = 0
    while cursor < len(payload):
        newline = payload.find(b"\n", cursor)
        if newline < 0:
            raise ValueError("malformed git cat-file batch header")
        header = payload[cursor:newline].split()
        cursor = newline + 1
        if len(header) != 3:
            raise ValueError("malformed git cat-file batch response")
        sha, kind, size_raw = header
        size = int(size_raw)
        content = payload[cursor:cursor + size]
        if len(content) != size or payload[cursor + size:cursor + size + 1] != b"\n":
            raise ValueError("truncated git cat-file batch response")
        cursor += size + 1
        yield sha.decode("ascii"), kind.decode("ascii"), content


def audit_history(root: Path, *, max_bytes: int = 5 * 1024 * 1024) -> dict[str, object]:
    """Audit all commits reachable from local refs; require a complete Git repository."""
    root = root.resolve()
    if max_bytes < 1:
        raise ValueError("max_bytes must be positive")
    if not root.is_dir() or not (root / ".git").exists():
        raise ValueError("root must be a Git working tree with a .git directory")
    shallow = _git(root, "rev-parse", "--is-shallow-repository").strip() == b"true"
    if shallow:
        raise ValueError("repository is shallow; fetch full history before auditing")

    commits = _git(root, "rev-list", "--all", "--count").decode("ascii").strip()
    object_lines = _git(root, "rev-list", "--objects", "--all").decode("utf-8", errors="replace").splitlines()
    object_paths: dict[str, str] = {}
    object_ids: list[str] = []
    for line in object_lines:
        parts = line.split(" ", 1)
        sha = parts[0]
        if re.fullmatch(r"[0-9a-f]{40,64}", sha) and sha not in object_paths:
            object_paths[sha] = parts[1] if len(parts) == 2 else "(path unavailable)"
            object_ids.append(sha)

    sizes = _git(root, "cat-file", "--batch-check", input_bytes=("\n".join(object_ids) + "\n").encode())
    blob_records: list[tuple[str, int]] = []
    for line in sizes.decode("ascii", errors="replace").splitlines():
        fields = line.split()
        if len(fields) == 3 and fields[1] == "blob":
            blob_records.append((fields[0], int(fields[2])))

    findings: list[dict[str, str | int]] = []
    seen_artifact_path: set[str] = set()
    path_history = _git(root, "log", "--all", "--full-history", "--format=", "--name-only").decode(
        "utf-8", errors="replace"
    )
    for raw_path in path_history.splitlines():
        path = raw_path.strip()
        if not path:
            continue
        if Path(path).suffix.lower() in FORBIDDEN_SUFFIXES and path not in seen_artifact_path:
            seen_artifact_path.add(path)
            findings.append({"rule": "historical_data_artifact_path", "path": path})

    scan_ids: list[str] = []
    for sha, size in blob_records:
        path = object_paths.get(sha, "(path unavailable)")
        if size > max_bytes:
            findings.append({"rule": "historical_oversized_blob", "path": path, "blob_sha": sha, "size_bytes": size})
        elif size > 0:
            scan_ids.append(sha)

    if scan_ids:
        payload = _git(root, "cat-file", "--batch", input_bytes=("\n".join(scan_ids) + "\n").encode())
        for sha, kind, data in _parse_batch_objects(payload):
            if kind != "blob" or SKIP_BINARY_MARKER in data:
                continue
            for rule, pattern in SECRET_PATTERNS.items():
                if pattern.search(data):
                    findings.append({
                        "rule": f"possible_{rule}",
                        "path": object_paths.get(sha, "(path unavailable)"),
                        "blob_sha": sha,
                    })

    unique = {json.dumps(item, sort_keys=True): item for item in findings}
    ordered = sorted(unique.values(), key=lambda item: (str(item["rule"]), str(item["path"]), str(item.get("blob_sha", ""))))
    return {
        "scope": "all commits and blobs reachable from local refs",
        "commit_count": int(commits or 0),
        "unique_blob_count": len(blob_records),
        "max_blob_bytes": max_bytes,
        "findings_count": len(ordered),
        "findings": ordered,
        "limitations": [
            "Only refs fetched into this clone are scanned; fetch all relevant branches and tags first.",
            "Credential-pattern matches are heuristics and require human triage.",
            "A clean result does not prove that no sensitive information was ever exposed.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--max-bytes", type=int, default=5 * 1024 * 1024)
    parser.add_argument("--json-output", type=Path, help="optional JSON report path; keep outside the repository")
    args = parser.parse_args()
    try:
        report = audit_history(args.root, max_bytes=args.max_bytes)
    except ValueError as exc:
        parser.error(str(exc))
    serialized = json.dumps(report, indent=2) + "\n"
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    return 1 if report["findings_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
