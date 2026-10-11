#!/usr/bin/env python3
"""Inventory WPAI Constitution variants without following filesystem links.

The scanner is deliberately read-only. It inventories path-name candidates and
text files that contain stable Constitution signatures, hashes every hit, and
records access failures so an "all drives" claim remains auditable.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import re
import stat
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator

PATH_MARKERS = (
    "agents constitution",
    "agents-constitution",
    "wpai constitution",
    "wpai-constitution",
    "soulv2",
    "soul v2",
)
CONTENT_MARKERS = (
    "constitution of an ai empire",
    "const-gate-001",
    "agents constitution",
    "wpai constitution",
    "mandatory meaningful evolution",
    "every top-level invocation",
)
EXACT_NAMES = {
    "agents.md",
    "skill.md",
    "soul.md",
    "soulv2.md",
    "soul-v2.md",
    "soulv2.0.0.md",
}
TEXT_SUFFIXES = {
    ".md",
    ".mdc",
    ".txt",
    ".rst",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".ps1",
    ".py",
}
DEFAULT_MAX_TEXT_BYTES = 8 * 1024 * 1024


@dataclass(frozen=True)
class Hit:
    path: str
    size: int
    sha256: str
    reasons: tuple[str, ...]
    markers: tuple[str, ...]


@dataclass(frozen=True)
class ScanError:
    path: str
    operation: str
    error: str


def windows_fixed_roots() -> list[Path]:
    """Return mounted fixed/removable Windows drive roots.

    Optical/network drives are excluded because they are not local PC storage.
    """
    if os.name != "nt":
        return [Path("/")]
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    roots: list[Path] = []
    for index in range(26):
        if not bitmask & (1 << index):
            continue
        root = f"{chr(ord('A') + index)}:\\"
        drive_type = ctypes.windll.kernel32.GetDriveTypeW(root)
        if drive_type in {2, 3}:  # removable, fixed
            roots.append(Path(root))
    return roots


def normalize_path(path: Path) -> str:
    return str(path.resolve(strict=False))


def is_link_or_reparse(entry: os.DirEntry[str]) -> bool:
    try:
        if entry.is_symlink():
            return True
        attrs = entry.stat(follow_symlinks=False).st_file_attributes
        return bool(attrs & stat.FILE_ATTRIBUTE_REPARSE_POINT)
    except (AttributeError, OSError):
        return entry.is_symlink()


def walk_files(root: Path, errors: list[ScanError]) -> Iterator[Path]:
    stack = [root]
    while stack:
        directory = stack.pop()
        try:
            with os.scandir(directory) as entries:
                for entry in entries:
                    try:
                        if is_link_or_reparse(entry):
                            continue
                        if entry.is_dir(follow_symlinks=False):
                            stack.append(Path(entry.path))
                        elif entry.is_file(follow_symlinks=False):
                            yield Path(entry.path)
                    except OSError as exc:
                        errors.append(ScanError(entry.path, "stat", str(exc)))
        except OSError as exc:
            errors.append(ScanError(str(directory), "scandir", str(exc)))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_file(path: Path, max_text_bytes: int) -> Hit | None:
    lowered_path = str(path).casefold()
    reasons: list[str] = []
    markers: list[str] = []
    if any(marker in lowered_path for marker in PATH_MARKERS):
        reasons.append("path")
    if path.name.casefold() in EXACT_NAMES:
        reasons.append("name")

    size = path.stat().st_size
    text_candidate = path.suffix.casefold() in TEXT_SUFFIXES and size <= max_text_bytes
    if text_candidate:
        raw = path.read_bytes()
        if b"\x00" not in raw[:4096]:
            text = raw.decode("utf-8-sig", errors="replace").casefold()
            markers = [marker for marker in CONTENT_MARKERS if marker in text]
            if markers:
                reasons.append("content")

    if not reasons:
        return None
    return Hit(
        path=normalize_path(path),
        size=size,
        sha256=sha256_file(path),
        reasons=tuple(sorted(set(reasons))),
        markers=tuple(markers),
    )


def scan(roots: Iterable[Path], max_text_bytes: int) -> tuple[list[Hit], list[ScanError], int]:
    hits: list[Hit] = []
    errors: list[ScanError] = []
    examined = 0
    seen: set[str] = set()
    for root in roots:
        normalized_root = normalize_path(root).casefold()
        if normalized_root in seen:
            continue
        seen.add(normalized_root)
        for path in walk_files(root, errors):
            examined += 1
            try:
                hit = inspect_file(path, max_text_bytes)
                if hit:
                    hits.append(hit)
            except OSError as exc:
                errors.append(ScanError(str(path), "inspect", str(exc)))
    hits.sort(key=lambda item: item.path.casefold())
    errors.sort(key=lambda item: (item.path.casefold(), item.operation))
    return hits, errors, examined


def write_report(output: Path, roots: list[Path], hits: list[Hit], errors: list[ScanError], examined: int) -> None:
    payload = {
        "schema": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "roots": [normalize_path(root) for root in roots],
        "files_examined": examined,
        "hit_count": len(hits),
        "error_count": len(errors),
        "hits": [asdict(hit) for hit in hits],
        "errors": [asdict(error) for error in errors],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, output)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", action="append", default=[], help="root to scan; repeatable")
    parser.add_argument("--output", required=True, help="JSON report path")
    parser.add_argument("--max-text-bytes", type=int, default=DEFAULT_MAX_TEXT_BYTES)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    roots = [Path(item).resolve() for item in args.root] if args.root else windows_fixed_roots()
    missing = [str(root) for root in roots if not root.exists()]
    if missing:
        raise SystemExit(f"scan roots do not exist: {', '.join(missing)}")
    hits, errors, examined = scan(roots, args.max_text_bytes)
    output = Path(args.output).resolve()
    write_report(output, roots, hits, errors, examined)
    print(f"PASS: examined {examined} files; {len(hits)} candidates; {len(errors)} access errors")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
