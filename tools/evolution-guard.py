#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NON_SUBSTANTIVE = {
    "VERSION",
    "CHANGELOG.md",
    "evolution/LEDGER.md",
}


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True, help="base commit SHA")
    args = parser.parse_args()

    changed = [p for p in git("diff", "--name-only", f"{args.base}...HEAD").splitlines() if p]
    if not changed:
        print("FAIL: evolution PR contains no changed files")
        return 1

    if "VERSION" not in changed:
        print("FAIL: every accepted source evolution must bump VERSION")
        return 1
    if "evolution/LEDGER.md" not in changed:
        print("FAIL: every accepted source evolution must update evolution/LEDGER.md")
        return 1

    substantive = [
        p for p in changed
        if p not in NON_SUBSTANTIVE
        and not p.startswith(".github/")
    ]
    if not substantive:
        print("FAIL: only version/ledger/changelog/workflow metadata changed; no meaningful skill improvement detected")
        return 1

    print("PASS: evolution PR contains substantive source changes")
    for path in substantive:
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
