#!/usr/bin/env python3
"""Fail when a project still consumes a retired Constitution pack or SOUL copy.

This is a read-only migration check. Run it after changing project entry points,
CI, generators, and manifests, before removing a vendored pack. It inspects
tracked text and the top-level old-pack directory; it never follows symlinks.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

TEXT_SUFFIXES = {".md", ".mdc", ".json", ".toml", ".yaml", ".yml", ".ps1", ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx"}
LEGACY = re.compile(r"AGENTS Constitution|skills[\\/]+agents-constitution|name:\s*agents-constitution|SOULv2\.0\.0\.md|verify-pack\.ps1|gate_check\.py", re.IGNORECASE)
FULL_SOUL = re.compile(r"(?:^# SOUL\.md\s*[—-]\s*The Constitution of an AI Empire|^## 40\. Constitutional Integrity)", re.MULTILINE)
ACTIVE_SOUL_READ = re.compile(r"(?:localStorage|sessionStorage)\.getItem\(\s*['\"]soul_config['\"]\s*\)")
PROMPT_CONSUMER = re.compile(r"\bsystemPrompt\b|\brole\s*:\s*['\"]system['\"]|\.chat\.completions\.create\(")
HISTORICAL_RECOVERY = re.compile(
    r"^\s*(?:[-*]\s*)?Historical recovery \(not active law\):\s*`?git show [0-9a-f]{40}:[^`]+`?\s*$",
    re.IGNORECASE,
)
CANONICAL_CHECKOUT = re.compile(
    r"^\s*repository\s*:\s*['\"]?MrWizard94-Compile/Agents-Constitution['\"]?\s*(?:#.*)?$",
    re.IGNORECASE,
)
PINNED_REF = re.compile(r"^\s*ref\s*:\s*['\"]?[0-9a-f]{40}['\"]?\s*(?:#.*)?$", re.IGNORECASE)
FLOATING_SOURCE_URL = re.compile(
    r"https?://(?:raw\.githubusercontent\.com/MrWizard94-Compile/Agents-Constitution/"
    r"|github\.com/MrWizard94-Compile/Agents-Constitution/(?:raw|blob)/)(?:main|master)/",
    re.IGNORECASE,
)
MAX_TEXT_BYTES = 4 * 1024 * 1024


def project_files(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    paths = [root / Path(item.decode("utf-8", errors="surrogateescape")) for item in result.stdout.split(b"\0") if item]
    paths.extend(root / name for name in ("SOUL.md", "SOULv2.0.0.md") if (root / name).exists())
    return sorted(set(paths))


def workflow_source_findings(relative: str, lines: list[str]) -> list[tuple[str, str, int]]:
    """Catch literal floating source references without interpreting arbitrary YAML."""
    findings: list[tuple[str, str, int]] = []
    for index, line in enumerate(lines):
        if FLOATING_SOURCE_URL.search(line):
            findings.append(("FLOATING_CANONICAL_URL", relative, index + 1))
        if not CANONICAL_CHECKOUT.fullmatch(line):
            continue
        indentation = len(line) - len(line.lstrip(" \t"))
        start = index
        while start > 0:
            candidate = lines[start - 1]
            depth = len(candidate) - len(candidate.lstrip(" \t"))
            if depth < indentation and candidate.lstrip().startswith("- "):
                break
            start -= 1
        end = index + 1
        while end < len(lines):
            candidate = lines[end]
            depth = len(candidate) - len(candidate.lstrip(" \t"))
            if depth < indentation and candidate.lstrip().startswith("- "):
                break
            end += 1
        if not any(PINNED_REF.fullmatch(candidate) for candidate in lines[start:end]):
            findings.append(("UNPINNED_CANONICAL_CHECKOUT", relative, index + 1))
    return findings


def inspect(root: Path) -> list[tuple[str, str, int]]:
    root = root.resolve(strict=True)
    git_root = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    ).stdout.strip()
    if not root.samefile(Path(git_root)):
        raise ValueError("project path must be its Git repository root")

    findings: list[tuple[str, str, int]] = []
    old_pack = root / "AGENTS Constitution"
    if old_pack.is_symlink() or (old_pack.is_dir() and any(path.is_file() or path.is_symlink() for path in old_pack.rglob("*"))):
        findings.append(("OLD_PACK_DIRECTORY", "AGENTS Constitution", 0))

    for path in project_files(root):
        relative = path.relative_to(root).as_posix()
        if "AGENTS Constitution" in path.parts and relative.startswith("AGENTS Constitution/"):
            continue  # one directory finding is enough
        if path.is_symlink():
            if LEGACY.search(relative):
                findings.append(("LEGACY_SYMLINK", relative, 0))
            continue
        if not path.is_file() or path.suffix.casefold() not in TEXT_SUFFIXES:
            continue
        if path.stat().st_size > MAX_TEXT_BYTES:
            findings.append(("TEXT_TOO_LARGE_UNCHECKED", relative, 0))
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        lines = text.splitlines()
        if FULL_SOUL.search(text):
            findings.append(("FULL_SOUL_COPY", relative, 1))
        if relative.startswith(".github/workflows/") and path.suffix.casefold() in {".yml", ".yaml"}:
            findings.extend(workflow_source_findings(relative, lines))
        if path.suffix.casefold() in {".js", ".mjs", ".cjs", ".ts", ".tsx"} and PROMPT_CONSUMER.search(text):
            for match in ACTIVE_SOUL_READ.finditer(text):
                findings.append(("ACTIVE_LEGACY_PROMPT", relative, text.count("\n", 0, match.start()) + 1))
        for number, line in enumerate(lines, start=1):
            if LEGACY.search(line) and not (path.suffix.casefold() == ".md" and HISTORICAL_RECOVERY.fullmatch(line)):
                findings.append(("LEGACY_REFERENCE", relative, number))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, help="exact project Git root")
    args = parser.parse_args()
    try:
        findings = inspect(args.project)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: adoption check could not complete: {exc}", file=sys.stderr)
        return 2
    for code, path, line in findings:
        suffix = f":{line}" if line else ""
        print(f"{code}: {path}{suffix}")
    if findings:
        print(f"FAIL: {len(findings)} unresolved Constitution adoption findings")
        return 1
    print("PASS: no detected active legacy Constitution consumer or top-level pack; indirect data flow still requires review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
