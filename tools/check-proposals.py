#!/usr/bin/env python3
"""Check proposal decisions and archived evidence without GitHub or mutations."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUSES = {"pending", "incorporated", "covered", "superseded", "obsolete"}
KINDS = {"public-patch", "local-proposal", "historical-pr"}
SHA = re.compile(r"[0-9a-f]{40}\Z")
DIGEST = re.compile(r"[0-9a-f]{64}\Z")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def regular_file(root: Path, relative: str, limit: int) -> bytes:
    current = root
    for part in Path(relative).parts:
        if part in {"..", "."}:
            raise ValueError("unsafe evidence path")
        current = current / part
        if current.is_symlink() or getattr(current, "is_junction", lambda: False)():
            raise ValueError("linked evidence is not accepted")
    if not current.resolve().is_relative_to(root.resolve()):
        raise ValueError("evidence escapes source root")
    if not current.is_file() or current.stat().st_size > limit:
        raise ValueError("missing, non-regular or oversized evidence")
    with current.open("rb") as stream:
        content = stream.read(limit + 1)
    if len(content) > limit:
        raise ValueError("evidence grew beyond its size bound")
    return content


def check(root: Path = ROOT, require_resolved: bool = False) -> tuple[list[str], dict[str, int]]:
    errors: list[str] = []
    counts: Counter[str] = Counter()
    try:
        manifest = json.loads(regular_file(root, "evolution/proposals/manifest.json", 200_000),
                              object_pairs_hook=unique_object)
        if not isinstance(manifest, dict) or manifest.get("schema") != 2:
            raise ValueError("schema-2 proposal register required")
        if not isinstance(manifest.get("reviewed_against"), str) or not SHA.fullmatch(manifest["reviewed_against"]):
            raise ValueError("full reviewed-against SHA required")
        if not re.fullmatch(r"\d+\.\d+\.\d+", str(manifest.get("resolution_version", ""))):
            raise ValueError("resolution version required")
        entries = manifest.get("entries")
        if not isinstance(entries, list) or len(entries) > 1000:
            raise ValueError("bounded entry list required")
        homes = set()
        for relative in ("AGENTS.md", "SOP.md", "governance/EVOLUTION.md", "law/ENGINEERING.md",
                         "law/OPERATIONS.md", "law/SECURITY.md", "law/COLLABORATION.md", "law/SPECIALIST.md"):
            text = regular_file(root, relative, 200_000).decode("utf-8-sig")
            homes.update(re.findall(r"^#{2,3} ([A-Z][A-Z0-9-]*-\d{3})\b", text, re.MULTILINE))
        ids, commits, patches = set(), set(), set()
        for entry in entries:
            if not isinstance(entry, dict):
                errors.append("proposal entry must be an object")
                continue
            identity = entry.get("id")
            if not isinstance(identity, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,99}", identity) or identity in ids:
                errors.append("proposal IDs must be valid and unique")
                continue
            ids.add(identity)
            status, kind = entry.get("status"), entry.get("kind")
            if not isinstance(status, str) or status not in STATUSES:
                errors.append(f"{identity}: invalid decision status")
                continue
            counts[status] += 1
            if kind not in KINDS:
                errors.append(f"{identity}: invalid provenance kind")
            if any(not isinstance(entry.get(field), str) or not entry[field].strip() for field in ("title", "reason")):
                errors.append(f"{identity}: title and reason required")
            rules = entry.get("rule_ids")
            if (not isinstance(rules, list) or not rules or any(not isinstance(r, str) or r not in homes for r in rules)
                    or len(rules) != len(set(rules))):
                errors.append(f"{identity}: existing, unique canonical rule homes required")
            prs = entry.get("original_prs", [])
            if (not isinstance(prs, list) or any(type(n) is not int or n <= 0 for n in prs)
                    or len(prs) != len(set(prs))):
                errors.append(f"{identity}: invalid original PR provenance")
            commit = entry.get("commit")
            if commit is not None:
                if not isinstance(commit, str) or not SHA.fullmatch(commit) or commit in commits:
                    errors.append(f"{identity}: source commit must be full and unique")
                else:
                    commits.add(commit)
            if kind == "public-patch":
                patch = entry.get("patch")
                safe = (isinstance(patch, str) and re.fullmatch(r"archive/[0-9a-f]{12}\.patch", patch)
                        and isinstance(commit, str) and patch == f"archive/{commit[:12]}.patch")
                if not safe or patch in patches:
                    errors.append(f"{identity}: unsafe or duplicate patch path")
                    continue
                patches.add(patch)
                if not isinstance(entry.get("parent"), str) or not SHA.fullmatch(entry["parent"]):
                    errors.append(f"{identity}: original parent SHA required")
                content = regular_file(root, "evolution/proposals/" + patch, 1_000_000)
                if not content.startswith(b"diff --git ") or hashlib.sha256(content).hexdigest() != entry.get("sha256"):
                    errors.append(f"{identity}: archived patch bytes or digest mismatch")
            elif kind == "local-proposal":
                digest = entry.get("content_sha256")
                if entry.get("private_recovery") is not True or (commit is None and
                        (not isinstance(digest, str) or not DIGEST.fullmatch(digest))):
                    errors.append(f"{identity}: private source recovery and commit or content digest required")
                if "patch" in entry:
                    errors.append(f"{identity}: private raw patch must not be published")
            elif kind == "historical-pr" and not prs:
                errors.append(f"{identity}: historical closure must name its PR")
        archive = root / "evolution/proposals/archive"
        if archive.is_symlink() or getattr(archive, "is_junction", lambda: False)():
            raise ValueError("linked archive is not accepted")
        actual = {"archive/" + p.name for p in archive.iterdir()} if archive.exists() else set()
        if actual != patches:
            errors.append("archive contains missing or unregistered evidence")
        source = json.loads(regular_file(root, "SOURCE.json", 100_000), object_pairs_hook=unique_object)
        if (not isinstance(source, dict) or not isinstance(source.get("mirror_files"), list)
                or any(not isinstance(p, str) for p in source["mirror_files"])):
            raise ValueError("valid binding mirror manifest required")
        source_version = source.get("skill_version")
        if (not isinstance(source_version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", source_version)
                or tuple(map(int, manifest["resolution_version"].split("."))) > tuple(map(int, source_version.split(".")))):
            errors.append("resolution version cannot be newer than its containing source")
        if any(p.startswith("evolution/proposals/") for p in source["mirror_files"]):
            errors.append("proposal evidence must remain outside binding law mirrors")
        if require_resolved and counts["pending"]:
            errors.append(f"{counts['pending']} unresolved proposal(s) remain")
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        errors.append(f"proposal register unreadable or invalid: {type(exc).__name__}: {exc}")
    return errors, dict(counts)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-resolved", action="store_true")
    args = parser.parse_args(argv)
    errors, counts = check(require_resolved=args.require_resolved)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"PASS: {sum(counts.values())} proposals verified; {counts.get('pending', 0)} unresolved; "
          "archive integrity and canonical decision homes valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
