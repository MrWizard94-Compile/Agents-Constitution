#!/usr/bin/env python3
"""Install a verified, commit-pinned WPAI Constitution mirror.

Download every declared file before touching a target. Unknown files are never
pruned; only files named by the target's prior generated manifest may be removed.
The final manifest is written last and is the invocation's integrity check.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path, PurePosixPath

DEFAULT_REPO = "MrWizard94-Compile/Agents-Constitution"
MANIFEST_NAME = ".GENERATED-MIRROR.json"
SHA_RE = re.compile(r"[0-9a-fA-F]{40}\Z")


def request(url: str) -> bytes:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "wpai-constitution-sync"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as response:
        return response.read()


def resolve_commit(repo: str, ref: str) -> str:
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", repo):
        raise ValueError("repository must be owner/name")
    api = f"https://api.github.com/repos/{repo}/commits/{urllib.parse.quote(ref, safe='')}"
    sha = json.loads(request(api)).get("sha", "")
    if not isinstance(sha, str) or not SHA_RE.fullmatch(sha):
        raise ValueError("ref did not resolve to an immutable commit")
    return sha.lower()


def relative_file(value: str) -> str:
    path = PurePosixPath(value)
    if not value or value.startswith("/") or "\\" in value or any(p in ("", ".", "..") for p in value.split("/")):
        raise ValueError(f"unsafe manifest path: {value!r}")
    if path.as_posix() != value or path.name == MANIFEST_NAME:
        raise ValueError(f"unsafe manifest path: {value!r}")
    return value


def validate_source(source: dict, repo: str, version: str) -> list[str]:
    if source.get("schema") != 2 or source.get("name") != "wpai-constitution":
        raise ValueError("not a WPAI Constitution schema-2 source")
    if source.get("canonical_repository") != repo or source.get("skill_version") != version:
        raise ValueError("repository or version mismatch")
    if source.get("local_install_is_authoritative") is not False:
        raise ValueError("a generated install cannot be authoritative")
    files = source.get("mirror_files")
    if not isinstance(files, list) or not files or any(not isinstance(p, str) for p in files):
        raise ValueError("mirror_files must be a non-empty string list")
    validated = [relative_file(p) for p in files]
    if len(validated) != len(set(validated)) or not {"SKILL.md", "AGENTS.md", "SOP.md", "SOURCE.json", "VERSION"}.issubset(validated):
        raise ValueError("mirror_files has duplicates or omits required law")
    return validated


def fetch_snapshot(repo: str, commit: str) -> tuple[dict, str, dict[str, bytes]]:
    prefix = f"https://raw.githubusercontent.com/{repo}/{commit}/"
    source_data = request(prefix + "SOURCE.json")
    version_data = request(prefix + "VERSION")
    source = json.loads(source_data)
    version = version_data.decode("utf-8-sig").strip()
    files = validate_source(source, repo, version)
    payload = {rel: request(prefix + urllib.parse.quote(rel, safe="/")) for rel in files}
    if payload["SOURCE.json"] != source_data or payload["VERSION"] != version_data:
        raise ValueError("snapshot source changed during fetch")
    return source, version, payload


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temp:
        temp.write(data)
        pending = Path(temp.name)
    try:
        os.replace(pending, path)
    finally:
        pending.unlink(missing_ok=True)


def safe_target_file(target: Path, rel: str) -> Path:
    relative_file(rel)
    path = target / Path(rel)
    current = path.parent
    while current != target:
        if current.is_symlink():
            raise ValueError(f"refusing symlinked mirror directory: {current}")
        current = current.parent
    if path.is_symlink():
        raise ValueError(f"refusing symlinked mirror file: {path}")
    return path


def prior_generated_hashes(target: Path) -> dict[str, str]:
    manifest = target / MANIFEST_NAME
    if manifest.is_symlink():
        raise ValueError("refusing symlinked provenance manifest")
    if not manifest.is_file():
        return {}
    prior = json.loads(manifest.read_text(encoding="utf-8"))
    if prior.get("generated") is not True or prior.get("canonical_repository") != DEFAULT_REPO:
        raise ValueError("target has noncanonical provenance; inspect it before sync")
    hashes = prior.get("file_sha256", {})
    if not isinstance(hashes, dict) or any(not isinstance(p, str) or not isinstance(h, str) or not re.fullmatch(r"[0-9a-f]{64}", h) for p, h in hashes.items()):
        raise ValueError("invalid prior generated-file manifest")
    return {relative_file(p): h for p, h in hashes.items()}


def sync_target(target: Path, source: dict, version: str, commit: str, payload: dict[str, bytes]) -> None:
    target = target.expanduser().absolute()
    for ancestor in (target, *target.parents):
        if ancestor.is_symlink():
            raise ValueError(f"refusing symlinked mirror path: {ancestor}")
    if target.exists() and not target.is_dir():
        raise ValueError(f"mirror target is not a directory: {target}")
    previous = prior_generated_hashes(target)
    paths = {rel: safe_target_file(target, rel) for rel in payload}
    obsolete = {rel: safe_target_file(target, rel) for rel in previous.keys() - payload.keys()}
    for rel, path in paths.items():
        if path.exists():
            current = hashlib.sha256(path.read_bytes()).hexdigest()
            expected = previous.get(rel)
            incoming = hashlib.sha256(payload[rel]).hexdigest()
            if current != incoming and current != expected:
                raise ValueError(f"local or unknown file conflicts with mirror update: {rel}")
    for rel, path in obsolete.items():
        if path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() != previous[rel]:
            raise ValueError(f"modified generated file cannot be pruned: {rel}")
    target.mkdir(parents=True, exist_ok=True)
    for rel, data in payload.items():
        atomic_write(paths[rel], data)
    for rel, path in obsolete.items():
        if path.is_file():
            path.unlink()
    hashes = {rel: hashlib.sha256(data).hexdigest() for rel, data in payload.items()}
    provenance = {
        "generated": True,
        "canonical_repository": DEFAULT_REPO,
        "canonical_url": source["canonical_url"],
        "source_commit": commit,
        "skill_version": version,
        "file_sha256": hashes,
    }
    atomic_write(target / MANIFEST_NAME, (json.dumps(provenance, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    verify_target(target)


def verify_target(target: Path) -> None:
    provenance = json.loads((target / MANIFEST_NAME).read_text(encoding="utf-8"))
    if provenance.get("generated") is not True or provenance.get("canonical_repository") != DEFAULT_REPO or not SHA_RE.fullmatch(str(provenance.get("source_commit", ""))):
        raise ValueError("invalid mirror provenance")
    for rel, expected in provenance["file_sha256"].items():
        actual = hashlib.sha256(safe_target_file(target, rel).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"mirror integrity mismatch: {rel}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("targets", nargs="*", help="mirror folders; defaults in SOURCE.json")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--ref", default="main")
    args = parser.parse_args()
    if args.repo != DEFAULT_REPO:
        parser.error("only the canonical repository is a source")
    commit = resolve_commit(args.repo, args.ref)
    source, version, payload = fetch_snapshot(args.repo, commit)
    targets = args.targets or source.get("default_mirror_paths", [])
    if not targets:
        parser.error("no mirror targets configured")
    for candidate in targets:
        target = Path(candidate)
        sync_target(target, source, version, commit, payload)
        print(f"Verified WPAI Constitution {version} ({commit[:12]}) -> {target.expanduser().absolute()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
