"""Tests for the local environment diagnostic."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_doctor_runs_and_reports_core_environment() -> None:
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, str(root / "scripts" / "doctor.py")],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + "\n" + result.stderr
    assert "VITALIS core environment check passed." in result.stdout
    assert "does not certify research results or clinical readiness" in result.stdout


def test_doctor_dashboard_flag_is_recognized() -> None:
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, str(root / "scripts" / "doctor.py"), "--help"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "--dashboard" in result.stdout
