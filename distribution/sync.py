#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import tempfile
import urllib.request
from pathlib import Path

DEFAULT_REPO = "MrWizard94-Compile/Agents-Constitution"
FILES = [
    "SKILL.md",
    "VERSION",
    "SOURCE.json",
    "references/always-load.md",
    "references/pack-root.local.example",
    "references/.gitignore",
    "scripts/resolve-pack.ps1",
]
KEEP_ALWAYS = {
    ".GENERATED-MIRROR.json",
    "references/pack-root.local",
}


def request(url: str) -> bytes:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "agents-constitution-sync"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


def resolve_commit(repo: str, ref: str) -> str:
    payload = json.loads(request(f"https://api.github.com/repos/{repo}/commits/{ref}").decode("utf-8"))
    sha = payload.get("sha", "")
    if len(sha) != 40:
        raise SystemExit(f"could not resolve {repo}@{ref} to an immutable commit")
    return sha


def fetch(repo: str, commit: str, rel: str) -> bytes:
    return request(f"https://raw.githubusercontent.com/{repo}/{commit}/{rel}")


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as tmp:
        tmp.write(data)
        tmp_path = Path(tmp.name)
    os.replace(tmp_path, path)


def looks_like_skill(target: Path) -> bool:
    source = target / "SOURCE.json"
    if source.is_file():
        try:
            data = json.loads(source.read_text(encoding="utf-8-sig"))
            if data.get("name") == "agents-constitution":
                return True
        except (OSError, json.JSONDecodeError):
            pass
    skill = target / "SKILL.md"
    if skill.is_file():
        head = skill.read_text(encoding="utf-8-sig", errors="replace")[:800]
        return "name: agents-constitution" in head
    return False


def prune_stale(target: Path) -> None:
    if not looks_like_skill(target):
        return
    keep = set(FILES) | KEEP_ALWAYS
    for path in sorted(target.rglob("*"), reverse=True):
        if path.is_symlink():
            continue
        rel = path.relative_to(target).as_posix()
        if path.is_file() and rel not in keep:
            path.unlink()
        elif path.is_dir():
            try:
                next(path.iterdir())
            except StopIteration:
                path.rmdir()


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync generated agents-constitution mirrors")
    parser.add_argument("targets", nargs="*", help="local skill directories; defaults come from SOURCE.json")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--ref", default="main", help="branch, tag, or commit to resolve once")
    parser.add_argument("--pack-root", default="")
    args = parser.parse_args()

    commit = resolve_commit(args.repo, args.ref)
    source = json.loads(fetch(args.repo, commit, "SOURCE.json").decode("utf-8"))
    if source.get("canonical_repository") != args.repo:
        raise SystemExit("canonical repository mismatch")
    version = fetch(args.repo, commit, "VERSION").decode("utf-8").strip()

    targets = list(args.targets)
    if not targets:
        targets = [str(p) for p in source.get("default_mirror_paths") or []]
    if not targets:
        raise SystemExit("no sync targets given and SOURCE.json has no default_mirror_paths")

    # All files are fetched from the same immutable commit. `main` cannot move
    # underneath a partially completed sync.
    payload = {rel: fetch(args.repo, commit, rel) for rel in FILES}
    for target_text in targets:
        target = Path(target_text).expanduser().resolve()
        for rel, data in payload.items():
            atomic_write(target / rel, data)
        if args.pack_root:
            atomic_write(target / "references/pack-root.local", (args.pack_root.rstrip() + "\n").encode("utf-8"))
        prune_stale(target)
        provenance = {
            "generated": True,
            "canonical_repository": args.repo,
            "canonical_url": source.get("canonical_url", f"https://github.com/{args.repo}"),
            "requested_ref": args.ref,
            "source_commit": commit,
            "skill_version": version,
        }
        atomic_write(target / ".GENERATED-MIRROR.json", (json.dumps(provenance, indent=2) + "\n").encode("utf-8"))
        print(f"Synced agents-constitution {version} ({commit[:12]}) -> {target}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
