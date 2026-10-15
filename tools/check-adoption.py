#!/usr/bin/env python3
"""Fail when a project retains retired law artifacts or active consumers.

This is a read-only migration check. Run it after changing project entry points,
CI, generators, and manifests, before removing a vendored pack. It inspects
tracked and unignored files plus bounded ignored agent-config locations; it
checks every candidate's components before reading, reporting links and Windows
reparse points as unresolved coverage. It does not crawl arbitrary ignored
caches. Run on a quiescent tree: these pathname checks are not a sandbox against
concurrent replacement of directories. A clean static result still needs
consumer review.

Use --filesystem for an explicit project directory that is not its own Git
root. This mode audits first-party files, including built output, without
consulting a parent repository's ignore rules. Known dependency caches are
excluded; links, nested repositories, and scan limits cannot yield a pass.
"""
from __future__ import annotations

import argparse
import re
import stat
import subprocess
import sys
from pathlib import Path

TEXT_SUFFIXES = {".md", ".mdc", ".json", ".toml", ".yaml", ".yml", ".ps1", ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx"}
AGENT_CONFIG_DIRS = (".agents", ".claude", ".codex", ".grok")
RETIRED_SOUL_NAMES = {"soul.md", "soulv2.0.0.md", "soulv2.md", "soul-v2.md"}
INSTRUCTION_NAMES = {"agents.md", "claude.md"}
AUDITED_NAMES = RETIRED_SOUL_NAMES | INSTRUCTION_NAMES
LEGACY = re.compile(r"AGENTS Constitution|skills[\\/]+agents-constitution|name:\s*agents-constitution|SOULv2\.0\.0\.md|verify-pack\.ps1|gate_check\.py", re.IGNORECASE)
FULL_SOUL = re.compile(r"(?:^# SOUL\.md\s*[—-]\s*The Constitution of an AI Empire|^## 40\. Constitutional Integrity)", re.MULTILINE)
RETIRED_LAW_BACKUP = re.compile(r"^(?:soul|agents)\.md\.legacy-pre-pack-[\w.-]+$", re.IGNORECASE)
ACTIVE_SOUL_LAW = re.compile(
    r"(?:\b(?:law|binding\s+constitution|governing\s+standard)\s*:\s*[\s*`]*\bSOUL\.md\b"
    r"|\bSOUL\.md\b[`*\s]*(?:is|remains)\s+(?:the\s+)?(?:immutable\s+)?law\b)",
    re.IGNORECASE,
)
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
MAX_FILESYSTEM_ENTRIES = 100_000
DEPENDENCY_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}


def is_link_or_reparse(path: Path) -> bool:
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(metadata.st_mode) or bool(
        getattr(metadata, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
    )


def first_link(root: Path, path: Path) -> Path | None:
    """Check outermost-first without statting a descendant through a link.

    Paths must be lexical descendants, not already resolved through a link.
    Do not cache results between candidates: the check is immediately before
    inspection, although it cannot prevent another process racing that read.
    """
    relative = path.relative_to(root)
    if ".." in relative.parts:
        raise ValueError("audit path must not contain parent traversal; use an absolute project path")
    current = root
    if is_link_or_reparse(current):
        return current
    for part in relative.parts:
        current = current / part
        if is_link_or_reparse(current):
            return current
    return None


def project_files(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    paths = [root / Path(item.decode("utf-8", errors="surrogateescape")) for item in result.stdout.split(b"\0") if item]
    for directory in (root, *(root / name for name in AGENT_CONFIG_DIRS)):
        if is_link_or_reparse(directory) or not directory.is_dir():
            continue
        for child in directory.iterdir():
            if child.name.casefold() in AUDITED_NAMES or RETIRED_LAW_BACKUP.fullmatch(child.name):
                paths.append(child)
    return sorted(set(paths))


def filesystem_files(root: Path) -> tuple[list[Path], list[tuple[str, str, int]]]:
    """Audit one explicit tree without Git, never following a linked path."""
    paths: list[Path] = []
    findings: list[tuple[str, str, int]] = []
    pending = [root]
    entries = 0
    while pending:
        for child in sorted(pending.pop().iterdir()):
            entries += 1
            if entries > MAX_FILESYSTEM_ENTRIES:
                raise ValueError("filesystem scan limit reached; no clean result is possible")
            relative = child.relative_to(root).as_posix()
            if child.name.casefold() in DEPENDENCY_DIRS:
                continue
            if is_link_or_reparse(child):
                findings.append(("LINKED_PATH_UNINSPECTED", relative, 0))
            elif child.is_dir():
                if (child / ".git").exists():
                    findings.append(("NESTED_GIT_REPOSITORY_UNINSPECTED", relative, 0))
                elif child.name.casefold() == "agents constitution":
                    if contains_pack_file(child):
                        findings.append(("OLD_PACK_DIRECTORY", relative, 0))
                else:
                    pending.append(child)
            elif child.is_file():
                paths.append(child)
    return sorted(paths), findings


def contains_pack_file(path: Path) -> bool:
    """Check a known pack location without entering a linked directory."""
    if is_link_or_reparse(path):
        return True
    if not path.is_dir():
        return path.is_file()
    pending = [path]
    while pending:
        for child in pending.pop().iterdir():
            if is_link_or_reparse(child) or child.is_file():
                return True
            if child.is_dir():
                pending.append(child)
    return False


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


def inspect(root: Path, *, filesystem: bool = False) -> list[tuple[str, str, int]]:
    root = root.absolute()
    if first_link(Path(root.anchor), root) is not None:
        raise ValueError("project root must not be a link or reparse point, or descend through one")
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("project path must be a directory")
    if filesystem:
        paths, findings = filesystem_files(root)
    else:
        git_root = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        ).stdout.strip()
        if not root.samefile(Path(git_root)):
            raise ValueError("project path must be its Git repository root")
        paths = project_files(root)
        findings = []

    if not filesystem:
        for directory in (root, *(root / name for name in AGENT_CONFIG_DIRS)):
            if directory != root and is_link_or_reparse(directory):
                findings.append(("AGENT_DIR_SYMLINK_UNINSPECTED", directory.relative_to(root).as_posix(), 0))
                continue
            old_pack = directory / "AGENTS Constitution"
            if contains_pack_file(old_pack):
                findings.append(("OLD_PACK_DIRECTORY", old_pack.relative_to(root).as_posix(), 0))

    reported_links = {path for code, path, _ in findings if code in {
        "LINKED_PATH_UNINSPECTED", "AGENT_DIR_SYMLINK_UNINSPECTED",
    }}
    for path in paths:
        relative = path.relative_to(root).as_posix()
        linked = first_link(root, path)
        if linked is not None:
            linked_relative = linked.relative_to(root).as_posix()
            if linked_relative not in reported_links:
                findings.append(("LINKED_PATH_UNINSPECTED", linked_relative, 0))
                reported_links.add(linked_relative)
            if linked == path:
                if path.name.casefold() in RETIRED_SOUL_NAMES:
                    findings.append(("RETIRED_SOUL_FILE", relative, 0))
                elif RETIRED_LAW_BACKUP.fullmatch(path.name):
                    findings.append(("RETIRED_LAW_BACKUP", relative, 0))
                if LEGACY.search(relative):
                    findings.append(("LEGACY_SYMLINK", relative, 0))
            continue
        if not path.exists():
            continue  # git ls-files still names deleted paths until their deletion is staged
        if "AGENTS Constitution" in path.parts and relative.startswith("AGENTS Constitution/"):
            continue  # one directory finding is enough
        if path.name.casefold() in RETIRED_SOUL_NAMES:
            findings.append(("RETIRED_SOUL_FILE", relative, 0))
        elif RETIRED_LAW_BACKUP.fullmatch(path.name):
            findings.append(("RETIRED_LAW_BACKUP", relative, 0))
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
            if ACTIVE_SOUL_LAW.search(line):
                findings.append(("ACTIVE_LEGACY_LAW", relative, number))
            if LEGACY.search(line) and not (path.suffix.casefold() == ".md" and HISTORICAL_RECOVERY.fullmatch(line)):
                findings.append(("LEGACY_REFERENCE", relative, number))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, help="exact project directory (Git root by default)")
    parser.add_argument("--filesystem", action="store_true", help="audit an exact first-party directory without Git; known dependency caches are excluded")
    args = parser.parse_args()
    try:
        findings = inspect(args.project, filesystem=args.filesystem)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: adoption check could not complete: {exc}", file=sys.stderr)
        return 2
    for code, path, line in findings:
        suffix = f":{line}" if line else ""
        print(f"{code}: {path}{suffix}")
    if findings:
        print(f"FAIL: {len(findings)} unresolved Constitution adoption findings")
        return 1
    scope = "first-party filesystem (dependency caches excluded)" if args.filesystem else "Git project and bounded agent-config locations"
    print(f"PASS: no detected retired law artifact, active legacy consumer, or pack in {scope}; indirect data flow still requires review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
