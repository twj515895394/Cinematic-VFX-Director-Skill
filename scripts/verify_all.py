#!/usr/bin/env python3
"""One-command local acceptance preflight on Windows/macOS/Linux.

Only standard Python + requirements-dev.txt. No network/video model calls.
Actual video/image evaluation always happens later with user-provided media.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(label, argv, *, expect_failure=False):
    print("\n" + "=" * 65, flush=True)
    print(label + ": " + " ".join(argv), flush=True)
    result = subprocess.run([sys.executable, *argv], cwd=ROOT)
    if expect_failure and result.returncode == 0:
        raise RuntimeError("Expected hard failure was accepted: " + label)
    if not expect_failure and result.returncode != 0:
        raise RuntimeError("Validation failed: " + label + " (exit %d)" % result.returncode)
    print("PASS: " + label, flush=True)


def main():
    p = argparse.ArgumentParser(description="Run all cinematic VFX Skill release-candidate checks")
    p.add_argument("--fast", action="store_true", help="Skip the complete unittest suite")
    args = p.parse_args()
    cases = [
        ("Release docs/source/scope", ["scripts/release_check.py"]),
        ("Source-derived 90 reference cases", ["adapters/sakuga_catalog.py", "--check"]),
        ("All datasets and schemas", ["scripts/validate_data.py"]),
        ("H3 model default", ["scripts/adapt_prompt.py", "--card", "sample.sword-activation", "--json"]),
        ("Explicit Seedance model", ["scripts/adapt_prompt.py", "--card", "sample.rainy-street", "--model", "seedance", "--json"]),
        ("Novice options must wait for confirmation", ["scripts/recommend_options.py", "--package", "examples/recommendations/sword-image.json"]),
        ("Continuous shot VFX", ["scripts/check_shot_states.py", "--file", "examples/sequences/continuous-sword.json"]),
        ("Independent montage VFX", ["scripts/check_shot_states.py", "--file", "examples/sequences/montage-weather.json"]),
        ("Design QC pass is not visual acceptance", ["scripts/review_vfx.py", "--review", "tests/fixtures/qc/design-good-sword.json", "--json"]),
        ("Hard failure blocks even when total score is high", ["scripts/review_vfx.py", "--review", "tests/fixtures/qc/design-bad-no-choice.json", "--fail-on-blocked"]),
    ]
    if not args.fast:
        cases.insert(3, ("Complete automated regression", ["-m", "unittest", "discover", "-s", "tests", "-v"]))
    try:
        for label, argv in cases:
            run(label, argv, expect_failure=label.startswith("Hard failure"))
    except (OSError, RuntimeError) as exc:
        print("\nFAIL: " + str(exc), file=sys.stderr)
        return 1
    print("\nALL OFFLINE CHECKS PASSED. Real H3/Seedance video quality is NOT yet tested.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
