#!/usr/bin/env python3
"""Reject metadata-only evolution; surviving content still needs semantic review."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NON_SUBSTANTIVE = {
    "VERSION",
    "CHANGELOG.md",
    "evolution/LEDGER.md",
}
VERSION_HEADERS = {"AGENTS.md", "SOP.md", "governance/EVOLUTION.md"}
VERSION_RE = re.compile(r"\d+\.\d+\.\d+\Z")


def git(*args: str) -> bytes:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout


def revision(name: str) -> str:
    """Resolve user input before using it in a revision/path expression."""
    return git("rev-parse", "--verify", "--end-of-options", f"{name}^{{commit}}").decode().strip()


def blob(commit: str, path: str | None) -> bytes:
    return b"" if path is None else git("show", f"{commit}:{path}")


def changed_paths(base: str, head: str) -> list[tuple[str | None, str | None]]:
    """Keep paths unquoted and pair exact renames with their original blob."""
    fields = git("diff", "--name-status", "--no-ext-diff", "--find-renames=100%",
                 "-z", base, head, "--").decode("utf-8", errors="surrogateescape").split("\0")
    changes: list[tuple[str | None, str | None]] = []
    index = 0
    while index < len(fields) - 1:
        status, path = fields[index:index + 2]
        index += 2
        if status == "R100":
            changes.append((path, fields[index]))
            index += 1
        elif status in {"A", "D", "M", "T"}:
            changes.append((None if status == "A" else path, None if status == "D" else path))
        else:
            raise ValueError(f"unsupported Git change status: {status}")
    return changes


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("SOURCE.json contains a duplicate object key")
        result[key] = value
    return result


def normalized_content(path: str, content: bytes) -> object:
    """Ignore only known release-version fields, never general whitespace."""
    if path == "SOURCE.json":
        source = json.loads(content, object_pairs_hook=unique_object)
        if not isinstance(source, dict):
            raise ValueError("SOURCE.json must contain an object")
        source.pop("skill_version", None)
        return source
    if path in VERSION_HEADERS:
        return re.sub(rb"(?m)^(\*\*Version:\*\* )\d+\.\d+\.\d+(?=\r?$)",
                      rb"\1<version>", content, count=1)
    if path == "SKILL.md":
        header = re.match(rb"\A---\r?\n.*?\r?\n---(?:\r?\n|\Z)", content, re.DOTALL)
        if header:
            normalized = re.sub(
                rb'(?m)^(  skill-version: ")\d+\.\d+\.\d+("\r?$)',
                rb"\1<version>\2", header.group(), count=1,
            )
            return normalized + content[header.end():]
    return content


def candidate_paths(base: str, head: str, changes: list[tuple[str | None, str | None]]) -> list[str]:
    candidates: list[str] = []
    for old_path, new_path in changes:
        paths = [path for path in (old_path, new_path) if path is not None]
        if all(path in NON_SUBSTANTIVE or path.startswith(".github/") for path in paths):
            continue
        before, after = blob(base, old_path), blob(head, new_path)
        if before == after:
            continue
        # New/deleted files retain their complete content; only existing metadata
        # fields are ignored. Removing a whole manifest is not a version bump.
        if old_path is not None and new_path is not None:
            if normalized_content(old_path, before) == normalized_content(new_path, after):
                continue
        candidates.append(new_path or old_path or "")
    return candidates


def check(base_name: str) -> int:
    head = revision("HEAD")
    base = git("merge-base", revision(base_name), head).decode().strip()
    changes = changed_paths(base, head)
    changed = {path for pair in changes for path in pair if path is not None}
    if not changed:
        print("FAIL: evolution PR contains no changed files")
        return 1
    if "VERSION" not in changed:
        print("FAIL: every accepted source evolution must bump VERSION")
        return 1
    versions = [blob(commit, "VERSION").decode("utf-8").strip() for commit in (base, head)]
    if (any(not VERSION_RE.fullmatch(value) for value in versions)
            or tuple(map(int, versions[1].split("."))) <= tuple(map(int, versions[0].split(".")))):
        print("FAIL: VERSION must increase from a valid major.minor.patch version")
        return 1
    if "evolution/LEDGER.md" not in changed:
        print("FAIL: every accepted source evolution must update evolution/LEDGER.md")
        return 1
    candidates = candidate_paths(base, head, changes)
    if not candidates:
        print("FAIL: no source-content change remains after excluding release metadata and workflows")
        return 1
    print("PASS: source-content candidates detected; semantic usefulness still requires review")
    for path in candidates:
        print(f"- {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True, help="base commit SHA")
    args = parser.parse_args(argv)
    try:
        return check(args.base)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"FAIL: could not inspect committed evolution: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
