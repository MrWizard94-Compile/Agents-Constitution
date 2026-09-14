#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "SKILL.md",
    "VERSION",
    "SOURCE.json",
    "references/always-load.md",
    "references/pack-root.local.example",
    "scripts/resolve-pack.ps1",
    "distribution/sync.ps1",
    "evolution/LEDGER.md",
]

CRITICAL_PHRASES = [
    "only editable source",
    "Every top-level invocation",
    "meaningful",
    "later invocation",
    "exactly one evolution obligation per top-level invocation",
    "highest quality reasonably achievable",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def normalize_prose(text: str) -> str:
    """Normalize Markdown prose for semantic phrase checks.

    Line wrapping, tabs, and repeated spaces are presentation details. Critical
    invariant checks should fail when meaning disappears, not when an editor
    reflows a paragraph.
    """
    return " ".join(text.casefold().split())


def main() -> int:
    for rel in REQUIRED:
        if not (ROOT / rel).is_file():
            fail(f"missing required file: {rel}")

    version = (ROOT / "VERSION").read_text(encoding="utf-8-sig").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        fail(f"VERSION is not semver: {version!r}")

    source = json.loads((ROOT / "SOURCE.json").read_text(encoding="utf-8-sig"))
    if source.get("canonical_repository") != "MrWizard94-Compile/Agents-Constitution":
        fail("SOURCE.json canonical_repository is incorrect")
    if source.get("local_install_is_authoritative") is not False:
        fail("local_install_is_authoritative must be false")
    if source.get("freeze_revision_per_invocation") is not True:
        fail("freeze_revision_per_invocation must be true")
    if source.get("mandatory_meaningful_evolution_per_invocation") is not True:
        fail("mandatory_meaningful_evolution_per_invocation must be true")

    skill = normalize_prose((ROOT / "SKILL.md").read_text(encoding="utf-8-sig"))
    for phrase in CRITICAL_PHRASES:
        if normalize_prose(phrase) not in skill:
            fail(f"SKILL.md lost critical invariant phrase: {phrase}")

    generated_markers = list(ROOT.rglob(".GENERATED-MIRROR.json"))
    if generated_markers:
        fail("generated-mirror marker must never be committed to canonical source")

    ledger = normalize_prose((ROOT / "evolution/LEDGER.md").read_text(encoding="utf-8-sig"))
    anti_churn_patterns = (
        "does not count",
        "doesn't count",
        "never counts",
        "never count",
    )
    if not any(pattern in ledger for pattern in anti_churn_patterns):
        fail("evolution ledger must explicitly state that ledger-only evidence does not satisfy meaningful evolution")

    print(f"PASS: canonical agents-constitution source v{version} is structurally valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
