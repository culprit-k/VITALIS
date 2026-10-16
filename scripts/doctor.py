"""Check that a local VITALIS research environment is installed and importable.

This is an environment diagnostic only. It does not validate model performance,
cohort integrity, clinical safety, or availability of a trained predictor.
"""
from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import sys

CORE_MODULES = (
    "vitalis.adaptive_twin",
    "vitalis.stream",
    "vitalis.integrated_inference",
    "vitalis.reporting",
)
CORE_DISTRIBUTIONS = ("numpy", "pandas", "scikit-learn")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dashboard",
        action="store_true",
        help="also verify the optional Streamlit dashboard dependency",
    )
    args = parser.parse_args()

    failures = 0

    def report(label: str, ok: bool, detail: str) -> None:
        nonlocal failures
        print(f"[{'OK' if ok else 'FAIL'}] {label}: {detail}")
        if not ok:
            failures += 1

    report("Python", sys.version_info >= (3, 10), sys.version.split()[0] +
           (" (supported)" if sys.version_info >= (3, 10) else " (requires Python >=3.10)"))

    for distribution in CORE_DISTRIBUTIONS:
        try:
            version = importlib.metadata.version(distribution)
            report(f"dependency {distribution}", True, version)
        except importlib.metadata.PackageNotFoundError:
            report(f"dependency {distribution}", False, "not installed")

    for module_name in CORE_MODULES:
        try:
            importlib.import_module(module_name)
            report(f"module {module_name}", True, "import succeeded")
        except Exception as exc:  # diagnostic must show import/dependency failures clearly
            report(f"module {module_name}", False, f"{type(exc).__name__}: {exc}")

    if args.dashboard:
        try:
            version = importlib.metadata.version("streamlit")
            report("dependency streamlit", True, version)
        except importlib.metadata.PackageNotFoundError:
            report("dependency streamlit", False, "not installed; install with pip install -e \".[dashboard]\"")

    if failures:
        print(f"\nVITALIS environment check failed: {failures} check(s) need attention.")
        print('Install from the repository with: python -m pip install -e ".[dev,dashboard]"')
        return 1

    print("\nVITALIS core environment check passed.")
    print("This does not certify research results or clinical readiness.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
