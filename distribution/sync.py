#!/usr/bin/env python3
"""Install a verified, commit-pinned WPAI Constitution mirror.

Download and preflight every target before installation. A local undo journal
protects each target against interrupted file replacement; ordinary failures
roll back every target in the invocation. Unknown files are never pruned.
"""
from __future__ import annotations

import argparse
from contextlib import ExitStack, contextmanager
import hashlib
import json
import os
import re
import shutil
import stat
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path, PurePosixPath

DEFAULT_REPO = "MrWizard94-Compile/Agents-Constitution"
MANIFEST_NAME = ".GENERATED-MIRROR.json"
JOURNAL_NAME = ".GENERATED-MIRROR-UNDO"
PREPARING_NAME = ".GENERATED-MIRROR-PREPARING"
LOCK_NAME = ".GENERATED-MIRROR.lock"
PREPARING_MARKER = b"wpai-constitution-sync-prepare-v1\n"
COMMITTED_NAME = "COMMITTED.json"
ROLLED_BACK_NAME = "ROLLED-BACK.json"
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
    if path.as_posix() != value or path.name == MANIFEST_NAME or path.parts[0] in (JOURNAL_NAME, PREPARING_NAME, LOCK_NAME):
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


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def target_path(target: Path, rel: str) -> Path:
    return target / MANIFEST_NAME if rel == MANIFEST_NAME else safe_target_file(target, rel)


def check_target_root(target: Path) -> None:
    for ancestor in (target, *target.parents):
        if ancestor.is_symlink():
            raise ValueError(f"refusing symlinked mirror path: {ancestor}")
    if target.exists() and not target.is_dir():
        raise ValueError(f"mirror target is not a directory: {target}")


@contextmanager
def mirror_lock(target: Path):
    """Hold an OS-owned lock; leave its stable empty file in place after exit."""
    check_target_root(target)
    target.mkdir(parents=True, exist_ok=True)
    check_target_root(target)
    path = target / LOCK_NAME
    if path.is_symlink():
        raise ValueError(f"refusing symlinked mirror lock: {path}")
    flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o600)
    with os.fdopen(descriptor, "r+b", buffering=0) as lock_file:
        opened = os.fstat(lock_file.fileno())
        current = path.lstat()
        if (not stat.S_ISREG(opened.st_mode) or opened.st_size != 0 or
                stat.S_ISLNK(current.st_mode) or
                (opened.st_dev, opened.st_ino) != (current.st_dev, current.st_ino)):
            raise ValueError(f"invalid mirror lock file: {path}")
        if os.name == "nt":
            import msvcrt

            lock_file.seek(0)
            try:
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as error:
                raise RuntimeError(f"cannot lock mirror target {target}; another sync may be active") from error
            try:
                yield
            finally:
                lock_file.seek(0)
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            try:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as error:
                raise RuntimeError(f"cannot lock mirror target {target}; another sync may be active") from error
            try:
                yield
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


@contextmanager
def mirror_locks(targets: list[Path]):
    """Lock every target in stable order so overlapping batches cannot race."""
    with ExitStack() as stack:
        for target in sorted(targets, key=lambda path: (str(path).casefold(), str(path))):
            stack.enter_context(mirror_lock(target))
        yield


def preflight_target(target: Path, source: dict, version: str, commit: str,
                     payload: dict[str, bytes]) -> tuple[dict[str, bytes | None], dict[str, bytes | None]]:
    check_target_root(target)
    previous = prior_generated_hashes(target)
    for rel, expected in previous.items():
        path = safe_target_file(target, rel)
        if not path.is_file() or sha256(path.read_bytes()) != expected:
            raise ValueError(f"existing mirror integrity mismatch conflicts with update: {rel}")
    hashes = {rel: sha256(data) for rel, data in payload.items()}
    provenance = {
        "generated": True,
        "canonical_repository": DEFAULT_REPO,
        "canonical_url": source["canonical_url"],
        "source_commit": commit,
        "skill_version": version,
        "file_sha256": hashes,
    }
    incoming: dict[str, bytes | None] = dict(payload)
    incoming.update({rel: None for rel in previous.keys() - payload.keys()})
    incoming[MANIFEST_NAME] = (json.dumps(provenance, indent=2, sort_keys=True) + "\n").encode("utf-8")
    original: dict[str, bytes | None] = {}
    for rel, data in incoming.items():
        path = target_path(target, rel)
        if path.exists() and not path.is_file():
            raise ValueError(f"mirror path is not a regular file: {rel}")
        old = path.read_bytes() if path.is_file() else None
        if rel != MANIFEST_NAME and old is not None:
            expected = previous.get(rel)
            if sha256(old) not in (expected, sha256(data) if data is not None else None):
                raise ValueError(f"local or unknown file conflicts with mirror update: {rel}")
        original[rel] = old
    return original, incoming


def journal_bytes(data: dict) -> bytes:
    return (json.dumps(data, sort_keys=True) + "\n").encode("utf-8")


def journal_backup(journal: Path, index: int, rel: str) -> Path:
    path = journal / "old" / str(index) / rel
    for ancestor in (path, *path.parents):
        if ancestor == journal:
            break
        if ancestor.is_symlink():
            raise ValueError(f"symlinked mirror backup path: {ancestor}")
    return path


def discard_preparing(coordinator: Path) -> None:
    preparing = coordinator / PREPARING_NAME
    if not preparing.exists() and not preparing.is_symlink():
        return
    marker = preparing / "PREPARING"
    if preparing.is_symlink() or not preparing.is_dir() or marker.is_symlink() or not marker.is_file() or marker.read_bytes() != PREPARING_MARKER:
        raise ValueError(f"unknown mirror preparation at {preparing}; inspect before sync")
    for path in preparing.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"symlink in mirror preparation: {path}")
    shutil.rmtree(preparing)


def prepare_journal(plans: list[tuple[Path, dict[str, bytes | None], dict[str, bytes | None]]],
                    commit: str) -> dict:
    coordinator = plans[0][0]
    coordinator.mkdir(parents=True, exist_ok=True)
    preparing = coordinator / PREPARING_NAME
    journal = coordinator / JOURNAL_NAME
    if preparing.exists() or preparing.is_symlink() or journal.exists() or journal.is_symlink():
        raise ValueError(f"unfinished or foreign mirror transaction at {coordinator}; inspect before sync")
    preparing.mkdir()
    metadata = {"schema": 2, "targets": [str(target) for target, _, _ in plans],
                "commit": commit, "entries": []}
    try:
        atomic_write(preparing / "PREPARING", PREPARING_MARKER)
        for index, (_target, original, incoming) in enumerate(plans):
            entries = {}
            for rel, old in original.items():
                entries[rel] = {"old": sha256(old) if old is not None else None,
                                "new": sha256(incoming[rel]) if incoming[rel] is not None else None}
                if old is not None:
                    atomic_write(journal_backup(preparing, index, rel), old)
            metadata["entries"].append(entries)
        atomic_write(preparing / "journal.json", journal_bytes(metadata))
        os.replace(preparing, journal)
    except Exception:
        if (preparing / "PREPARING").is_file():
            discard_preparing(coordinator)
        elif preparing.is_dir() and not preparing.is_symlink():
            # The marker write itself failed; no installation could start.
            shutil.rmtree(preparing)
        raise
    return metadata


def read_journal(coordinator: Path, targets: list[Path]) -> dict:
    journal = coordinator / JOURNAL_NAME
    if journal.is_symlink() or not journal.is_dir():
        raise ValueError(f"invalid mirror undo journal at {coordinator}")
    for name in (COMMITTED_NAME, ROLLED_BACK_NAME, "journal.json"):
        candidate = journal / name
        if candidate.is_symlink():
            raise ValueError(f"symlinked mirror transaction metadata: {candidate}")
    metadata_file = journal / "journal.json"
    if not metadata_file.is_file():
        markers = [journal / name for name in (COMMITTED_NAME, ROLLED_BACK_NAME)]
        metadata_file = next((p for p in markers if p.is_file()), metadata_file)
    data = json.loads(metadata_file.read_text(encoding="utf-8"))
    if data.get("schema") != 2 or data.get("targets") != [str(t) for t in targets] or not SHA_RE.fullmatch(str(data.get("commit", ""))):
        raise ValueError("mirror transaction target or commit mismatch; rerun with original target order")
    entries = data.get("entries")
    if not isinstance(entries, list) or len(entries) != len(targets):
        raise ValueError("invalid mirror undo journal metadata")
    for item in entries:
        if not isinstance(item, dict) or MANIFEST_NAME not in item:
            raise ValueError("invalid mirror undo journal entry set")
        for rel, hashes in item.items():
            if rel != MANIFEST_NAME:
                relative_file(rel)
            if not isinstance(hashes, dict) or set(hashes) != {"old", "new"}:
                raise ValueError("invalid mirror undo journal entry")
            if any(value is not None and (not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value)) for value in hashes.values()):
                raise ValueError("invalid mirror undo journal hash")
    return data


def check_target_state(target: Path, entries: dict, phase: str) -> None:
    for rel, hashes in entries.items():
        path = target_path(target, rel)
        if path.is_symlink() or (path.exists() and not path.is_file()):
            raise ValueError(f"mirror recovery conflict: {rel}")
        current = sha256(path.read_bytes()) if path.is_file() else None
        expected = hashes[phase]
        if current != expected:
            raise ValueError(f"mirror recovery conflict: {rel}")


def cleanup_journal(coordinator: Path, metadata: dict) -> None:
    journal = coordinator / JOURNAL_NAME
    parents = set()
    for index, entries in enumerate(metadata["entries"]):
        for rel, hashes in entries.items():
            if hashes["old"] is not None:
                backup = journal_backup(journal, index, rel)
                if backup.is_file():
                    if sha256(backup.read_bytes()) != hashes["old"]:
                        raise ValueError(f"modified mirror backup: {backup}")
                    backup.unlink()
                parents.update(backup.parents)
    for parent in sorted((p for p in parents if p != journal and journal in p.parents), key=lambda p: len(p.parts), reverse=True):
        if parent.is_dir():
            parent.rmdir()
    for name in ("journal.json", "PREPARING", COMMITTED_NAME, ROLLED_BACK_NAME):
        path = journal / name
        if path.is_symlink():
            raise ValueError(f"symlinked mirror journal file: {path}")
        if path.is_file():
            path.unlink()
    journal.rmdir()


def recover_batch(coordinator: Path, targets: list[Path]) -> None:
    journal = coordinator / JOURNAL_NAME
    if not journal.exists() and not journal.is_symlink():
        return
    if journal.is_dir() and not any(journal.iterdir()):
        journal.rmdir()
        return
    metadata = read_journal(coordinator, targets)
    if (journal / COMMITTED_NAME).is_file() or (journal / ROLLED_BACK_NAME).is_file():
        phase = "new" if (journal / COMMITTED_NAME).is_file() else "old"
        for target, entries in zip(targets, metadata["entries"]):
            check_target_state(target, entries, phase)
        cleanup_journal(coordinator, metadata)
        return
    for index, (target, entries) in enumerate(zip(targets, metadata["entries"])):
        for rel, hashes in entries.items():
            if hashes["old"] is not None:
                backup = journal_backup(journal, index, rel)
                if not backup.is_file() or sha256(backup.read_bytes()) != hashes["old"]:
                    raise ValueError(f"mirror undo backup damaged: {rel}")
            path = target_path(target, rel)
            if path.is_symlink() or (path.exists() and not path.is_file()):
                raise ValueError(f"mirror recovery conflict: {rel}")
            current = sha256(path.read_bytes()) if path.is_file() else None
            if current not in (hashes["old"], hashes["new"]):
                raise ValueError(f"mirror recovery conflict: {rel}")
    for index, (target, entries) in enumerate(zip(targets, metadata["entries"])):
        for rel, hashes in entries.items():
            path = target_path(target, rel)
            if hashes["old"] is None:
                if path.is_file():
                    path.unlink()
            else:
                atomic_write(path, journal_backup(journal, index, rel).read_bytes())
        check_target_state(target, entries, "old")
        if entries[MANIFEST_NAME]["old"] is not None:
            verify_target(target)
    atomic_write(journal / ROLLED_BACK_NAME, journal_bytes(metadata))
    cleanup_journal(coordinator, metadata)


def normalized_targets(targets: list[Path]) -> list[Path]:
    normalized = [path.expanduser().absolute() for path in targets]
    if not normalized:
        raise ValueError("no mirror targets configured")
    if len(set(normalized)) != len(normalized):
        raise ValueError("duplicate mirror target")
    if any(left in right.parents or right in left.parents for index, left in enumerate(normalized) for right in normalized[index + 1:]):
        raise ValueError("nested mirror targets are not supported")
    for target in normalized:
        check_target_root(target)
    return normalized


def check_coordinator_journals(targets: list[Path]) -> None:
    for target in targets[1:]:
        if (target / JOURNAL_NAME).exists() or (target / JOURNAL_NAME).is_symlink():
            raise ValueError(f"mirror transaction at non-coordinator target {target}; rerun with original target order")


def recover_only(targets: list[Path]) -> None:
    normalized = normalized_targets(targets)
    with mirror_locks(normalized):
        check_coordinator_journals(normalized)
        coordinator = normalized[0]
        discard_preparing(coordinator)
        recover_batch(coordinator, normalized)


def sync_targets(targets: list[Path], source: dict, version: str, commit: str,
                 payload: dict[str, bytes]) -> None:
    normalized = normalized_targets(targets)
    with mirror_locks(normalized):
        check_coordinator_journals(normalized)
        coordinator = normalized[0]
        discard_preparing(coordinator)
        recover_batch(coordinator, normalized)
        plans = [(target, *preflight_target(target, source, version, commit, payload)) for target in normalized]
        metadata = prepare_journal(plans, commit)
        try:
            for target, _original, incoming in plans:
                for rel, data in incoming.items():
                    if rel == MANIFEST_NAME:
                        continue
                    path = target_path(target, rel)
                    if data is None:
                        if path.is_file():
                            path.unlink()
                    else:
                        atomic_write(path, data)
                atomic_write(target / MANIFEST_NAME, incoming[MANIFEST_NAME])
                verify_target(target)
            atomic_write(coordinator / JOURNAL_NAME / COMMITTED_NAME, journal_bytes(metadata))
        except Exception as failure:
            try:
                recover_batch(coordinator, normalized)
            except Exception as recovery_error:
                raise RuntimeError(f"mirror install failed and rollback needs inspection: {recovery_error}") from failure
            raise
        cleanup_journal(coordinator, metadata)


def sync_target(target: Path, source: dict, version: str, commit: str, payload: dict[str, bytes]) -> None:
    sync_targets([target], source, version, commit, payload)


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
    parser.add_argument("--recover-only", action="store_true", help="recover an interrupted batch without network access; requires its original ordered targets")
    args = parser.parse_args()
    if args.repo != DEFAULT_REPO:
        parser.error("only the canonical repository is a source")
    if args.recover_only:
        if not args.targets:
            parser.error("--recover-only requires the original ordered targets")
        recover_only([Path(candidate) for candidate in args.targets])
        print("WPAI Constitution mirror recovery complete")
        return 0
    commit = resolve_commit(args.repo, args.ref)
    source, version, payload = fetch_snapshot(args.repo, commit)
    targets = args.targets or source.get("default_mirror_paths", [])
    if not targets:
        parser.error("no mirror targets configured")
    sync_targets([Path(candidate) for candidate in targets], source, version, commit, payload)
    for candidate in targets:
        target = Path(candidate)
        print(f"Verified WPAI Constitution {version} ({commit[:12]}) -> {target.expanduser().absolute()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
