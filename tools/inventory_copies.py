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
RETIRED_LAW_BACKUP = re.compile(r"^(?:soul|agents)\.md\.legacy-pre-pack-[\w.-]+$", re.IGNORECASE)
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
DEFAULT_CHECKPOINT_DIRECTORIES = 1000


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


def _lexical_path_key(path: str | Path) -> str:
    return os.path.normcase(os.path.abspath(path))


def _canonical_path_key(path: str | Path) -> str:
    """Compare aliases without replacing the scanner's traversal guards.

    Windows 8.3 names can differ from the names returned by scandir. Resolve
    the small set of roots/output paths and report comparisons, not every
    examined file. Unresolvable error paths retain their lexical spelling;
    their errors must still keep overall coverage incomplete.
    """
    try:
        return os.path.normcase(normalize_path(Path(path)))
    except (OSError, RuntimeError):
        return _lexical_path_key(path)


def _same_path(first: str | Path, second: str | Path) -> bool:
    return (
        _lexical_path_key(first) == _lexical_path_key(second)
        or _canonical_path_key(first) == _canonical_path_key(second)
    )


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
    if path.name.casefold() in EXACT_NAMES or RETIRED_LAW_BACKUP.fullmatch(path.name):
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
        normalized_root = _canonical_path_key(root)
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


def inspect_directory(
    directory: Path, max_text_bytes: int, excluded_files: frozenset[str] = frozenset(),
) -> tuple[list[Path], list[Hit], list[ScanError], int]:
    """Inspect one directory as the atomic unit of resumable progress."""
    children: list[Path] = []
    hits: list[Hit] = []
    errors: list[ScanError] = []
    examined = 0
    try:
        metadata = os.lstat(directory)
        if stat.S_ISLNK(metadata.st_mode) or bool(
            getattr(metadata, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
        ):
            errors.append(ScanError(str(directory), "reparse", "directory became a link or reparse point"))
            return children, hits, errors, examined
        with os.scandir(directory) as entries:
            for entry in entries:
                try:
                    if is_link_or_reparse(entry):
                        continue
                    if entry.is_dir(follow_symlinks=False):
                        children.append(Path(entry.path))
                    elif entry.is_file(follow_symlinks=False):
                        if _lexical_path_key(entry.path) in excluded_files:
                            continue
                        examined += 1
                        try:
                            hit = inspect_file(Path(entry.path), max_text_bytes)
                            if hit:
                                hits.append(hit)
                        except OSError as exc:
                            errors.append(ScanError(entry.path, "inspect", str(exc)))
                except OSError as exc:
                    errors.append(ScanError(entry.path, "stat", str(exc)))
    except OSError as exc:
        errors.append(ScanError(str(directory), "scandir", str(exc)))
    return children, hits, errors, examined


def _write_json_atomic(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _fresh_progress(roots: list[Path], max_text_bytes: int, output: Path) -> dict[str, object]:
    return {
        "schema": 1,
        "status": "partial",
        "roots": [normalize_path(root) for root in roots],
        "max_text_bytes": max_text_bytes,
        "output": normalize_path(output),
        "pending_directories": [normalize_path(root) for root in reversed(roots)],
        "directories_completed": 0,
        "files_examined": 0,
        "hits": [],
        "errors": [],
    }


def _load_progress(checkpoint: Path, roots: list[Path], max_text_bytes: int, output: Path) -> dict[str, object]:
    try:
        progress = json.loads(checkpoint.read_text(encoding="utf-8"))
        expected = _fresh_progress(roots, max_text_bytes, output)
        for key in ("schema", "roots", "max_text_bytes", "output"):
            if progress[key] != expected[key]:
                raise ValueError(f"checkpoint {key} does not match this scan")
        if progress["status"] not in ("partial", "complete"):
            raise ValueError("checkpoint has invalid status")
        for key in ("files_examined", "directories_completed"):
            if type(progress[key]) is not int or progress[key] < 0:
                raise ValueError(f"checkpoint has invalid {key}")
        if not isinstance(progress["hits"], list) or not isinstance(progress["errors"], list):
            raise ValueError("checkpoint has invalid results")
        pending = progress["pending_directories"]
        if not isinstance(pending, list) or any(not isinstance(item, str) for item in pending):
            raise ValueError("checkpoint has invalid pending directories")
        normalized_roots = [os.path.normcase(os.path.realpath(root)) for root in roots]
        for item in pending:
            if not os.path.isabs(item):
                raise ValueError("checkpoint directory is outside scan roots")
            candidate = os.path.normcase(os.path.realpath(item))
            within_root = False
            for root in normalized_roots:
                try:
                    common = os.path.commonpath((candidate, root))
                except ValueError:
                    # Windows drives have no common path; another root may match.
                    continue
                if common == root:
                    within_root = True
                    break
            if not within_root:
                raise ValueError("checkpoint directory is outside scan roots")
        for hit in progress["hits"]:
            Hit(**hit)
        for error in progress["errors"]:
            ScanError(**error)
        if progress["status"] == "complete" and pending:
            raise ValueError("complete checkpoint still has pending directories")
        return progress
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise ValueError(f"invalid checkpoint {checkpoint}: {exc}") from exc


def scan_resumable(
    roots: list[Path], max_text_bytes: int, output: Path, checkpoint: Path,
    *, resume: bool, checkpoint_directories: int = DEFAULT_CHECKPOINT_DIRECTORIES,
) -> tuple[list[Hit], list[ScanError], int]:
    """Checkpoint only fully inspected directories; never publish a partial final report."""
    if checkpoint_directories < 1:
        raise ValueError("checkpoint_directories must be positive")
    normalized_roots = [_canonical_path_key(root) for root in roots]
    for index, root in enumerate(normalized_roots):
        for earlier in normalized_roots[:index]:
            try:
                common = os.path.commonpath((root, earlier))
            except ValueError:
                # Distinct Windows drives have no common path.
                continue
            if common in (root, earlier):
                raise ValueError("scan roots overlap; name each filesystem area once")
    excluded_files = frozenset(
        _canonical_path_key(path)
        for path in (output, checkpoint, output.with_suffix(output.suffix + ".tmp"),
                     checkpoint.with_suffix(checkpoint.suffix + ".tmp"))
    )
    if resume:
        progress = _load_progress(checkpoint, roots, max_text_bytes, output)
        if progress["status"] == "partial" and output.exists():
            raise ValueError(f"partial checkpoint conflicts with existing final report: {output}")
    else:
        if checkpoint.exists():
            raise ValueError(f"checkpoint already exists; use --resume: {checkpoint}")
        if output.exists():
            raise ValueError(f"final report already exists; choose a new output: {output}")
        progress = _fresh_progress(roots, max_text_bytes, output)
        _write_json_atomic(checkpoint, progress)

    pending = progress["pending_directories"]
    assert isinstance(pending, list)
    since_checkpoint = 0
    while pending:
        directory = Path(pending.pop())
        try:
            children, hits, errors, examined = inspect_directory(directory, max_text_bytes, excluded_files)
        except BaseException:
            pending.append(str(directory))
            _write_json_atomic(checkpoint, progress)
            raise
        pending.extend(str(child) for child in children)
        progress["hits"].extend(asdict(hit) for hit in hits)
        progress["errors"].extend(asdict(error) for error in errors)
        progress["files_examined"] += examined
        progress["directories_completed"] += 1
        since_checkpoint += 1
        if since_checkpoint >= checkpoint_directories:
            _write_json_atomic(checkpoint, progress)
            print(
                f"PROGRESS: {progress['directories_completed']} directories, "
                f"{progress['files_examined']} files, {len(progress['hits'])} hits, "
                f"{len(progress['errors'])} access errors",
                flush=True,
            )
            since_checkpoint = 0
    progress["status"] = "complete"
    _write_json_atomic(checkpoint, progress)
    hits = sorted((Hit(**item) for item in progress["hits"]), key=lambda item: item.path.casefold())
    errors = sorted(
        (ScanError(**item) for item in progress["errors"]),
        key=lambda item: (item.path.casefold(), item.operation),
    )
    return hits, errors, progress["files_examined"]


def _path_within_root(path: str, root: str) -> bool:
    # Preserve lexical attribution for a rejected link inside a named root.
    # Only a failed lexical comparison needs the alias-aware fallback.
    for key in (_lexical_path_key, _canonical_path_key):
        candidate = key(path)
        normalized_root = key(root)
        try:
            if os.path.commonpath((candidate, normalized_root)) == normalized_root:
                return True
        except ValueError:
            # Distinct drive spellings may still resolve to the same area.
            continue
    return False


def summarize_coverage(roots: list[Path], hits: list[Hit], errors: list[ScanError]) -> dict[str, object]:
    """Separate completed traversal from evidence that every named root was readable.

    Links and reparse points are intentionally not traversed. Even a result
    without recorded errors is not an absence proof for their targets.
    """
    root_results: list[dict[str, object]] = []
    attributed_errors = 0
    for root in roots:
        named_root = normalize_path(root)
        root_errors = [error for error in errors if _path_within_root(error.path, named_root)]
        attributed_errors += len(root_errors)
        root_inaccessible = any(
            error.operation == "scandir"
            and _same_path(error.path, named_root)
            for error in root_errors
        )
        root_results.append({
            "root": named_root,
            "status": "inaccessible" if root_inaccessible else "partial" if root_errors else "scanned",
            "candidate_count": sum(_path_within_root(hit.path, named_root) for hit in hits),
            "error_count": len(root_errors),
        })
    return {
        "status": "incomplete" if errors or not roots else "no_recorded_access_gaps",
        "scope": "named_roots_without_link_or_reparse_traversal",
        "root_results": root_results,
        "unattributed_error_count": len(errors) - attributed_errors,
    }


def write_report(
    output: Path, roots: list[Path], hits: list[Hit], errors: list[ScanError], examined: int,
) -> dict[str, object]:
    coverage = summarize_coverage(roots, hits, errors)
    payload = {
        "schema": 3,
        "status": "complete",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "roots": [normalize_path(root) for root in roots],
        "files_examined": examined,
        "hit_count": len(hits),
        "error_count": len(errors),
        "coverage": coverage,
        "hits": [asdict(hit) for hit in hits],
        "errors": [asdict(error) for error in errors],
    }
    _write_json_atomic(output, payload)
    return coverage


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", action="append", default=[], help="root to scan; repeatable")
    parser.add_argument("--output", required=True, help="JSON report path")
    parser.add_argument("--max-text-bytes", type=int, default=DEFAULT_MAX_TEXT_BYTES)
    parser.add_argument("--checkpoint", help="checkpoint path; defaults to <output>.checkpoint.json")
    parser.add_argument("--resume", action="store_true", help="resume an existing matching checkpoint")
    parser.add_argument("--checkpoint-directories", type=int, default=DEFAULT_CHECKPOINT_DIRECTORIES)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    roots = [Path(item).resolve() for item in args.root] if args.root else windows_fixed_roots()
    if not roots:
        raise SystemExit("no scan roots are available; name at least one --root")
    missing = [str(root) for root in roots if not root.exists()]
    if missing:
        raise SystemExit(f"scan roots do not exist: {', '.join(missing)}")
    if args.max_text_bytes < 0:
        raise SystemExit("--max-text-bytes must be nonnegative")
    output = Path(args.output).resolve()
    checkpoint = Path(args.checkpoint).resolve() if args.checkpoint else Path(str(output) + ".checkpoint.json")
    if checkpoint == output:
        raise SystemExit("checkpoint and final report must be different paths")
    try:
        hits, errors, examined = scan_resumable(
            roots, args.max_text_bytes, output, checkpoint,
            resume=args.resume, checkpoint_directories=args.checkpoint_directories,
        )
    except KeyboardInterrupt:
        print(f"INTERRUPTED: resume with --resume; checkpoint: {checkpoint}", file=sys.stderr)
        return 130
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    coverage = write_report(output, roots, hits, errors, examined)
    if coverage["status"] == "incomplete":
        print(
            f"INCOMPLETE COVERAGE: examined {examined} files; {len(hits)} candidates; "
            f"{len(errors)} access errors. Inspect report root_results before cleanup.",
            file=sys.stderr,
        )
        print(output)
        return 2
    print(f"PASS: examined {examined} files; {len(hits)} candidates; no recorded access gaps")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
