#!/usr/bin/env python3
"""Validate the canonical WPAI Constitution source without network access."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = "MrWizard94-Compile/Agents-Constitution"
VERSION_RE = re.compile(r"\d+\.\d+\.\d+\Z")
HEADING_ID_RE = re.compile(r"^#{2,3} ([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+-\d{3})\b", re.MULTILINE)
LINK_RE = re.compile(r"(?<!!)\[[^]]+\]\(([^)]+)\)")
PROTECTED = {
    "CONST-AUTH-001", "CONST-COMPLETE-001", "CONST-DEP-001",
    "CONST-DONE-001", "CONST-GATE-001", "CONST-CRAFT-001", "ENG-WARN-001",
    "TEST-BEHAVIOR-001", "DOC-SYNC-001", "SEC-INPUT-001",
    "GOV-SSOT-001", "GOV-EVOLVE-001",
}
MINIMUM_MIRROR = {
    "SKILL.md", "AGENTS.md", "SOP.md", "VERSION", "SOURCE.json",
    "references/always-load.md", "docs/QUALITY-ASSURANCE-MAP.md",
    "governance/EVOLUTION.md",
    "governance/RULE-REGISTRY.md", "law/ENGINEERING.md", "law/SECURITY.md",
    "law/OPERATIONS.md", "law/COLLABORATION.md", "law/SPECIALIST.md",
}


def local_links(path: Path, root: Path, body: str) -> list[str]:
    errors: list[str] = []
    for raw in LINK_RE.findall(body):
        target = raw.split("#", 1)[0].strip("<>")
        if not target or re.match(r"[a-z]+://", target) or target.startswith("mailto:"):
            continue
        resolved = (path.parent / target).resolve()
        if not resolved.is_relative_to(root.resolve()) or not resolved.exists():
            errors.append(f"broken local link in {path.relative_to(root)}: {raw}")
    return errors


def craft_contract_errors(agents: str) -> list[str]:
    """Guard the operational anti-slop rule, not just its registry entry."""
    section = re.search(
        r"^### CONST-CRAFT-001\b.*?\n(.*?)(?=^## |\Z)",
        agents,
        re.MULTILINE | re.DOTALL,
    )
    if section is None:
        return ["CONST-CRAFT-001 detailed rule missing"]
    normalized = " ".join(section.group(1).casefold().split())
    required = ("ai slop", "generic filler", "real intended use", "independent oracle", "human-accepted")
    return [f"CONST-CRAFT-001 missing operational safeguard: {term}" for term in required if term not in normalized]


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    required = MINIMUM_MIRROR | {"README.md", "CHANGELOG.md", "evolution/LEDGER.md", "docs/ARCHITECTURE.md", "docs/SOURCE-INVENTORY.md"}
    for rel in sorted(required):
        if not (root / rel).is_file():
            errors.append(f"missing required file: {rel}")
    if errors:
        return errors

    version = (root / "VERSION").read_text(encoding="utf-8-sig").strip()
    if not VERSION_RE.fullmatch(version):
        errors.append(f"invalid VERSION: {version!r}")
    try:
        source = json.loads((root / "SOURCE.json").read_text(encoding="utf-8-sig"))
    except (ValueError, OSError) as exc:
        return errors + [f"invalid SOURCE.json: {exc}"]
    if source.get("schema") != 2 or source.get("name") != "wpai-constitution":
        errors.append("SOURCE.json must identify schema-2 wpai-constitution")
    if source.get("canonical_repository") != REPO or source.get("canonical_url") != f"https://github.com/{REPO}":
        errors.append("SOURCE.json canonical identity mismatch")
    if source.get("skill_version") != version:
        errors.append("SOURCE.json version mismatch")
    for field, expected in (("local_install_is_authoritative", False), ("freeze_revision_per_invocation", True), ("mandatory_meaningful_evolution_per_invocation", True)):
        if source.get(field) is not expected:
            errors.append(f"SOURCE.json {field} mismatch")
    mirrors = source.get("default_mirror_paths", [])
    if not isinstance(mirrors, list) or not any(".codex/skills/wpai-constitution" in str(p) for p in mirrors) or not any(".grok/skills/wpai-constitution" in str(p) for p in mirrors):
        errors.append("default Codex and Grok WPAI mirrors required")
    files = source.get("mirror_files", [])
    if not isinstance(files, list) or any(not isinstance(p, str) or p.startswith("/") or "\\" in p or ".." in p.split("/") for p in files):
        errors.append("unsafe or invalid mirror_files")
        files = []
    if len(files) != len(set(files)) or not MINIMUM_MIRROR.issubset(files):
        errors.append("mirror manifest duplicates or omits binding files")
    for rel in files:
        if not (root / rel).is_file():
            errors.append(f"mirror file absent: {rel}")

    skill = (root / "SKILL.md").read_text(encoding="utf-8-sig")
    agents = (root / "AGENTS.md").read_text(encoding="utf-8-sig")
    evolution = (root / "governance/EVOLUTION.md").read_text(encoding="utf-8-sig")
    registry = (root / "governance/RULE-REGISTRY.md").read_text(encoding="utf-8-sig")
    if not re.search(r"^name: wpai-constitution$", skill, re.MULTILINE):
        errors.append("skill name mismatch")
    if not re.search(rf'^\s*skill-version: "{re.escape(version)}"$', skill, re.MULTILINE):
        errors.append("skill-version mismatch")
    if "# WPAI Constitution" not in agents or "15 Section 0" not in skill or "one coherent" not in skill.casefold():
        errors.append("skill or law lost core loading/gate/evolution language")
    gate = re.search(r"^## 0\. Mandatory pre-delivery gate\n(.*?)(?=^## |\Z)", agents, re.MULTILINE | re.DOTALL)
    gate_numbers = re.findall(r"^\| (\d+) \|", gate.group(1), re.MULTILINE) if gate else []
    if gate_numbers != [str(number) for number in range(1, 16)]:
        errors.append("Section 0 must contain exactly 15 ordered checks")
    if "staged, not propagated" not in skill.casefold() or "later invocation" not in skill.casefold():
        errors.append("skill lost staged/frozen invocation boundary")
    if "GOV-FREEZE-001" not in evolution or "GOV-RATCHET-001" not in evolution:
        errors.append("governance lost freeze or quality ratchet")
    for rule in PROTECTED:
        if rule not in agents or rule not in registry:
            errors.append(f"protected rule missing from entry/registry: {rule}")
    errors.extend(craft_contract_errors(agents))
    if "never counts" not in (root / "evolution/LEDGER.md").read_text(encoding="utf-8-sig").casefold():
        errors.append("ledger must say ledger-only edits never count")

    home_files = [root / "AGENTS.md", root / "governance/EVOLUTION.md"] + sorted((root / "law").glob("*.md"))
    defined: dict[str, str] = {}
    for path in home_files:
        body = path.read_text(encoding="utf-8-sig")
        for rule in HEADING_ID_RE.findall(body):
            if rule in defined:
                errors.append(f"duplicate rule definition {rule}: {defined[rule]}, {path.relative_to(root)}")
            defined[rule] = path.relative_to(root).as_posix()
    for rule in PROTECTED - set(defined):
        if rule not in {"CONST-AUTH-001", "CONST-COMPLETE-001", "CONST-DEP-001", "CONST-DONE-001", "CONST-GATE-001"}:
            errors.append(f"protected rule has no detailed definition: {rule}")
    family_homes = {
        "ENG": "law/ENGINEERING.md", "TEST": "law/ENGINEERING.md",
        "DOC": "law/ENGINEERING.md", "DEP": "law/ENGINEERING.md",
        "PERF": "law/ENGINEERING.md", "SEC": "law/SECURITY.md",
        "OBS": "law/SECURITY.md", "VCS": "law/OPERATIONS.md",
        "REF": "law/OPERATIONS.md", "MIG": "law/OPERATIONS.md",
        "OPS": "law/OPERATIONS.md", "REL": "law/OPERATIONS.md",
        "LIFE": "law/OPERATIONS.md", "REV": "law/COLLABORATION.md",
        "AI": "law/COLLABORATION.md", "CTX": "law/COLLABORATION.md",
        "MEM": "law/COLLABORATION.md", "RND": "law/SPECIALIST.md",
        "IP": "law/SPECIALIST.md", "NET": "law/SPECIALIST.md",
        "LOW": "law/SPECIALIST.md", "HW": "law/SPECIALIST.md",
        "COST": "law/SPECIALIST.md", "GOV": "governance/EVOLUTION.md",
    }
    for rule, home in defined.items():
        expected_home = "AGENTS.md" if rule.startswith("CONST-") else family_homes.get(rule.split("-", 1)[0])
        if home != expected_home:
            errors.append(f"rule in wrong canonical home: {rule} in {home}")
        if rule not in registry:
            errors.append(f"active rule absent from registry: {rule}")

    docs = [root / rel for rel in files if rel.endswith(".md")] + [root / rel for rel in ("README.md", "CHANGELOG.md", "docs/ARCHITECTURE.md", "docs/SOURCE-INVENTORY.md", "evolution/LEDGER.md")]
    for path in docs:
        if path.is_file():
            errors.extend(local_links(path, root, path.read_text(encoding="utf-8-sig")))
    if (root / ".GENERATED-MIRROR.json").exists():
        errors.append("canonical root contains generated mirror provenance")
    try:
        tracked = subprocess.run(
            ["git", "-C", str(root), "ls-files", "--cached", "-z"],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        ).stdout
        if any(Path(item.decode("utf-8", errors="surrogateescape")).name == ".GENERATED-MIRROR.json" for item in tracked.split(b"\0") if item):
            errors.append("generated mirror provenance is tracked in canonical source")
    except (OSError, subprocess.CalledProcessError):
        pass  # Archive/fixture validation can run without Git metadata.
    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"PASS: WPAI Constitution source v{(ROOT / 'VERSION').read_text().strip()} validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
