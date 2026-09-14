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
    "scripts/resolve-pack.ps1",
]


def fetch(repo: str, ref: str, rel: str) -> bytes:
    url = f"https://raw.githubusercontent.com/{repo}/{ref}/{rel}"
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read()


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as tmp:
        tmp.write(data)
        tmp_path = Path(tmp.name)
    os.replace(tmp_path, path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync generated agents-constitution mirrors")
    parser.add_argument("targets", nargs="+", help="one or more local skill directories")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--ref", default="main")
    parser.add_argument("--pack-root", default="")
    args = parser.parse_args()

    source = json.loads(fetch(args.repo, args.ref, "SOURCE.json").decode("utf-8"))
    if source.get("canonical_repository") != args.repo:
        raise SystemExit("canonical repository mismatch")
    version = fetch(args.repo, args.ref, "VERSION").decode("utf-8").strip()

    payload = {rel: fetch(args.repo, args.ref, rel) for rel in FILES}
    for target_text in args.targets:
        target = Path(target_text).expanduser().resolve()
        for rel, data in payload.items():
            atomic_write(target / rel, data)
        if args.pack_root:
            atomic_write(target / "references/pack-root.local", (args.pack_root.rstrip() + "\n").encode("utf-8"))
        provenance = {
            "generated": True,
            "canonical_repository": args.repo,
            "source_ref": args.ref,
            "skill_version": version,
        }
        atomic_write(target / ".GENERATED-MIRROR.json", (json.dumps(provenance, indent=2) + "\n").encode("utf-8"))
        print(f"Synced agents-constitution {version} -> {target}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
