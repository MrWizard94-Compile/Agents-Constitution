#!/usr/bin/env python3
"""Confirm a checkout is the byte-exact frozen revision and report loader drift.

Read-only. Point it at a Git checkout of the accepted commit that a top-level
skill call froze. It fails unless HEAD is that full SHA, tracked files are
unmodified, and every binding file named in the frozen `SOURCE.json` has the
exact raw bytes of its Git blob. With `--loader` it also compares the running
loader's `skill-version` with the frozen version, so a stale or newer loader is
disclosed rather than silently obeyed (GOV-FREEZE-001). A pass proves the law
text is faithful to that commit; it does not prove the commit is accepted
`main`, or that any mirror, runtime, or project uses it.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHA_RE = re.compile(r"[0-9a-f]{40}\Z")
SEMVER_RE = re.compile(r"\d+\.\d+\.\d+\Z")
SKILL_VERSION_RE = re.compile(r'^\s*skill-version:\s*"?(\d+\.\d+\.\d+)"?\s*$', re.MULTILINE)
MAX_LISTED = 5


def git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )


def loader_version(skill_text: str) -> str | None:
    """Return the `skill-version` declared by a SKILL.md header, if any."""
    match = SKILL_VERSION_RE.search(skill_text)
    return match.group(1) if match else None


def compare_loader(loader: str | None, frozen: str) -> str:
    """Return match, stale, ahead, or unknown by numeric SemVer comparison."""
    if loader is None or not SEMVER_RE.fullmatch(loader) or not SEMVER_RE.fullmatch(frozen):
        return "unknown"
    running = tuple(int(part) for part in loader.split("."))
    law = tuple(int(part) for part in frozen.split("."))
    if running == law:
        return "match"
    return "stale" if running < law else "ahead"


def read_source(root: Path, sha: str) -> dict:
    """Read SOURCE.json as committed at `sha`, not as it sits in the worktree."""
    shown = git(root, "show", f"{sha}:SOURCE.json")
    if shown.returncode != 0:
        raise ValueError(f"cannot read SOURCE.json at {sha[:12]}: {shown.stderr.decode(errors='replace').strip()}")
    try:
        source = json.loads(shown.stdout.decode("utf-8-sig"))
    except ValueError as error:
        raise ValueError(f"invalid SOURCE.json at {sha[:12]}: {error}") from error
    files = source.get("mirror_files")
    if not isinstance(files, list) or not files or not all(isinstance(item, str) for item in files):
        raise ValueError("SOURCE.json mirror_files must be a non-empty string list")
    if not isinstance(source.get("skill_version"), str):
        raise ValueError("SOURCE.json skill_version must be a string")
    return source


def safe_relative(value: str) -> bool:
    return bool(value) and not value.startswith("/") and "\\" not in value and ".." not in value.split("/")


def verify_checkout(root: Path, sha: str) -> list[str]:
    """Return every reason `root` is not the byte-exact frozen revision `sha`."""
    if not SHA_RE.fullmatch(sha):
        return [f"frozen revision must be a full lowercase 40-hex SHA, not {sha!r}"]
    head = git(root, "rev-parse", "--verify", "HEAD^{commit}")
    if head.returncode != 0:
        return [f"not a Git checkout with a commit: {root}"]
    actual = head.stdout.decode().strip()
    if actual != sha:
        return [f"checkout HEAD is {actual[:12]}, not frozen revision {sha[:12]}"]
    errors: list[str] = []
    status = git(root, "status", "--porcelain", "--untracked-files=no")
    changed = [line for line in status.stdout.decode(errors="replace").splitlines() if line]
    if status.returncode != 0:
        errors.append("git status failed; cannot show tracked files are unmodified")
    elif changed:
        shown = "; ".join(changed[:MAX_LISTED]) + (" ..." if len(changed) > MAX_LISTED else "")
        errors.append(f"tracked files differ from the frozen revision: {shown}")
    try:
        source = read_source(root, sha)
    except ValueError as error:
        return errors + [str(error)]
    for rel in source["mirror_files"]:
        if not safe_relative(rel):
            errors.append(f"unsafe mirror_files path: {rel!r}")
            continue
        blob = git(root, "rev-parse", "--verify", f"{sha}:{rel}")
        if blob.returncode != 0:
            errors.append(f"binding file absent from frozen revision: {rel}")
            continue
        path = root / rel
        if path.is_symlink() or not path.is_file():
            errors.append(f"binding file is not a regular file in the checkout: {rel}")
            continue
        # --no-filters hashes the raw bytes on disk. `git status` can be blind to
        # skip-worktree entries and line-ending filters; this check is not.
        raw = git(root, "hash-object", "--no-filters", "--", rel)
        if raw.returncode != 0 or raw.stdout.decode().strip() != blob.stdout.decode().strip():
            errors.append(f"bytes differ from the frozen revision: {rel}")
    return errors


def loader_report(loader_path: Path, frozen_version: str) -> str:
    version = loader_version(loader_path.read_text(encoding="utf-8-sig"))
    state = compare_loader(version, frozen_version)
    if state == "match":
        return f"LOADER: running skill-version {version} matches frozen law {frozen_version}"
    if state == "unknown":
        return (f"LOADER UNKNOWN: no readable skill-version in {loader_path}; frozen law is {frozen_version}. "
                "Follow the frozen SKILL.md and disclose the unknown loader in the handoff.")
    label = "STALE LOADER" if state == "stale" else "LOADER AHEAD"
    return (f"{label}: running skill-version {version}, frozen law {frozen_version}. "
            "Follow the frozen SKILL.md, not the running loader's differing steps, "
            "and name both versions in the handoff.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sha", required=True, help="full 40-hex SHA frozen for this call")
    parser.add_argument("--root", type=Path, default=ROOT, help="checkout to verify (default: this repository)")
    parser.add_argument("--loader", type=Path, help="running loader SKILL.md to compare with the frozen version")
    args = parser.parse_args(argv)

    errors = verify_checkout(args.root, args.sha)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    source = read_source(args.root, args.sha)
    print(f"PASS: {args.root} is byte-exact frozen revision {args.sha[:12]} "
          f"(skill {source['skill_version']}; {len(source['mirror_files'])} binding files hashed)")
    if args.loader is not None:
        try:
            print(loader_report(args.loader, source["skill_version"]))
        except OSError as error:
            print(f"FAIL: cannot read loader {args.loader}: {error}")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
