from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


def load_sync():
    source = Path(__file__).resolve().parents[1] / "distribution" / "sync.py"
    spec = importlib.util.spec_from_file_location("wpai_sync", source)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SYNC = load_sync()
COMMIT = "a" * 40


class DistributionTests(unittest.TestCase):
    def source(self, files: list[str]) -> dict:
        return {
            "schema": 2,
            "name": "wpai-constitution",
            "canonical_repository": SYNC.DEFAULT_REPO,
            "canonical_url": "https://github.com/" + SYNC.DEFAULT_REPO,
            "skill_version": "6.0.0",
            "local_install_is_authoritative": False,
            "mirror_files": files,
        }

    def test_same_commit_manifest_and_unknown_file_preservation(self):
        payload = {
            "SKILL.md": b"skill law\n",
            "AGENTS.md": b"quality law\n",
            "SOP.md": b"process law\n",
            "SOURCE.json": b"{}\n",
            "VERSION": b"6.0.0\n",
        }
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "mirror"
            target.mkdir()
            (target / "user-notes.txt").write_text("preserve", encoding="utf-8")
            SYNC.sync_target(target, self.source(list(payload)), "6.0.0", COMMIT, payload)
            self.assertEqual((target / "user-notes.txt").read_text(), "preserve")
            manifest = json.loads((target / SYNC.MANIFEST_NAME).read_text())
            self.assertEqual(manifest["source_commit"], COMMIT)
            self.assertEqual(set(manifest["file_sha256"]), set(payload))
            SYNC.verify_target(target)
            (target / "AGENTS.md").write_text("tampered", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "integrity mismatch"):
                SYNC.verify_target(target)

    def test_prunes_only_previously_generated_files(self):
        base = {name: name.encode() for name in ("SKILL.md", "AGENTS.md", "SOP.md", "SOURCE.json", "VERSION")}
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "mirror"
            initial = dict(base, **{"old-generated.md": b"old"})
            SYNC.sync_target(target, self.source(list(initial)), "6.0.0", COMMIT, initial)
            (target / "unknown.md").write_text("user", encoding="utf-8")
            SYNC.sync_target(target, self.source(list(base)), "6.0.0", COMMIT, base)
            self.assertFalse((target / "old-generated.md").exists())
            self.assertEqual((target / "unknown.md").read_text(), "user")

    def test_rejects_traversal_and_foreign_manifest(self):
        with self.assertRaisesRegex(ValueError, "unsafe manifest path"):
            SYNC.relative_file("../outside.md")
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            (target / SYNC.MANIFEST_NAME).write_text('{"generated": true, "canonical_repository": "other/repo"}')
            with self.assertRaisesRegex(ValueError, "noncanonical provenance"):
                SYNC.prior_generated_hashes(target)

    def test_rejects_modified_or_unknown_files_before_writing(self):
        base = {name: name.encode() for name in ("SKILL.md", "AGENTS.md", "SOP.md", "SOURCE.json", "VERSION")}
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "mirror"
            target.mkdir()
            (target / "AGENTS.md").write_text("private user edit", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "conflicts"):
                SYNC.sync_target(target, self.source(list(base)), "6.0.0", COMMIT, base)
            self.assertFalse((target / SYNC.MANIFEST_NAME).exists())
            self.assertEqual((target / "AGENTS.md").read_text(), "private user edit")

    def test_rejects_modified_generated_file(self):
        base = {name: name.encode() for name in ("SKILL.md", "AGENTS.md", "SOP.md", "SOURCE.json", "VERSION")}
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "mirror"
            SYNC.sync_target(target, self.source(list(base)), "6.0.0", COMMIT, base)
            (target / "AGENTS.md").write_text("modified", encoding="utf-8")
            updated = dict(base, **{"AGENTS.md": b"replacement"})
            with self.assertRaisesRegex(ValueError, "conflicts"):
                SYNC.sync_target(target, self.source(list(updated)), "6.0.0", COMMIT, updated)
            self.assertEqual((target / "AGENTS.md").read_text(), "modified")

    def test_second_target_write_failure_rolls_back_both_mirrors(self):
        base = {name: name.encode() for name in ("SKILL.md", "AGENTS.md", "SOP.md", "SOURCE.json", "VERSION")}
        changed = dict(base, **{"AGENTS.md": b"new constitutional text", "VERSION": b"6.1.0"})
        with tempfile.TemporaryDirectory() as temporary:
            first = Path(temporary) / "first"
            second = Path(temporary) / "second"
            for target in (first, second):
                SYNC.sync_target(target, self.source(list(base)), "6.0.0", COMMIT, base)
                (target / "user-notes.txt").write_text("preserve", encoding="utf-8")
            before = [(target / SYNC.MANIFEST_NAME).read_bytes() for target in (first, second)]
            write = SYNC.atomic_write
            failed = False

            def fail_second_target(path, data):
                nonlocal failed
                if path == second / "AGENTS.md" and not failed:
                    failed = True
                    raise OSError("injected install failure")
                write(path, data)

            with patch.object(SYNC, "atomic_write", side_effect=fail_second_target):
                with self.assertRaisesRegex(OSError, "injected install failure"):
                    SYNC.sync_targets([first, second], self.source(list(changed)), "6.1.0", "b" * 40, changed)
            for target, manifest in zip((first, second), before):
                self.assertEqual((target / SYNC.MANIFEST_NAME).read_bytes(), manifest)
                self.assertEqual((target / "AGENTS.md").read_bytes(), base["AGENTS.md"])
                self.assertEqual((target / "user-notes.txt").read_text(), "preserve")
                self.assertFalse((target / SYNC.JOURNAL_NAME).exists())
                SYNC.verify_target(target)

    def test_interrupted_install_recovers_on_next_sync(self):
        base = {name: name.encode() for name in ("SKILL.md", "AGENTS.md", "SOP.md", "SOURCE.json", "VERSION")}
        changed = dict(base, **{"AGENTS.md": b"new law"})
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "mirror"
            SYNC.sync_target(target, self.source(list(base)), "6.0.0", COMMIT, base)
            write = SYNC.atomic_write

            def interrupt(path, data):
                if path == target / "AGENTS.md":
                    raise KeyboardInterrupt("simulated process interruption")
                write(path, data)

            with patch.object(SYNC, "atomic_write", side_effect=interrupt):
                with self.assertRaises(KeyboardInterrupt):
                    SYNC.sync_target(target, self.source(list(changed)), "6.0.0", "b" * 40, changed)
            self.assertTrue((target / SYNC.JOURNAL_NAME).is_dir())
            SYNC.sync_target(target, self.source(list(changed)), "6.0.0", "b" * 40, changed)
            self.assertEqual((target / "AGENTS.md").read_bytes(), b"new law")
            self.assertFalse((target / SYNC.JOURNAL_NAME).exists())
            SYNC.verify_target(target)

    def test_recovery_preserves_post_interruption_user_edit(self):
        base = {name: name.encode() for name in ("SKILL.md", "AGENTS.md", "SOP.md", "SOURCE.json", "VERSION")}
        changed = dict(base, **{"AGENTS.md": b"new law"})
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "mirror"
            SYNC.sync_target(target, self.source(list(base)), "6.0.0", COMMIT, base)
            write = SYNC.atomic_write

            def interrupt(path, data):
                if path == target / "AGENTS.md":
                    raise KeyboardInterrupt("simulated process interruption")
                write(path, data)

            with patch.object(SYNC, "atomic_write", side_effect=interrupt):
                with self.assertRaises(KeyboardInterrupt):
                    SYNC.sync_target(target, self.source(list(changed)), "6.0.0", "b" * 40, changed)
            (target / "AGENTS.md").write_bytes(b"user edit after interruption")
            with self.assertRaisesRegex(ValueError, "recovery conflict"):
                SYNC.sync_target(target, self.source(list(changed)), "6.0.0", "b" * 40, changed)
            self.assertEqual((target / "AGENTS.md").read_bytes(), b"user edit after interruption")
            self.assertTrue((target / SYNC.JOURNAL_NAME).is_dir())

    def test_failed_journal_preparation_never_touches_mirror(self):
        base = {name: name.encode() for name in ("SKILL.md", "AGENTS.md", "SOP.md", "SOURCE.json", "VERSION")}
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "mirror"
            SYNC.sync_target(target, self.source(list(base)), "6.0.0", COMMIT, base)
            before = (target / SYNC.MANIFEST_NAME).read_bytes()
            write = SYNC.atomic_write

            def fail_preparation(path, data):
                if path == target / SYNC.PREPARING_NAME / "journal.json":
                    raise OSError("injected preparation failure")
                write(path, data)

            with patch.object(SYNC, "atomic_write", side_effect=fail_preparation):
                with self.assertRaisesRegex(OSError, "injected preparation failure"):
                    SYNC.sync_target(target, self.source(list(base)), "6.0.0", "b" * 40, base)
            self.assertEqual((target / SYNC.MANIFEST_NAME).read_bytes(), before)
            self.assertFalse((target / SYNC.PREPARING_NAME).exists())
            self.assertFalse((target / SYNC.JOURNAL_NAME).exists())
            SYNC.verify_target(target)

    def test_interrupted_second_target_rolls_back_batch_before_retry(self):
        base = {name: name.encode() for name in ("SKILL.md", "AGENTS.md", "SOP.md", "SOURCE.json", "VERSION")}
        changed = dict(base, **{"AGENTS.md": b"new law"})
        with tempfile.TemporaryDirectory() as temporary:
            first, second = (Path(temporary) / name for name in ("first", "second"))
            for target in (first, second):
                SYNC.sync_target(target, self.source(list(base)), "6.0.0", COMMIT, base)
            write = SYNC.atomic_write

            def interrupt(path, data):
                if path == second / "AGENTS.md":
                    raise KeyboardInterrupt("simulated interruption")
                write(path, data)

            with patch.object(SYNC, "atomic_write", side_effect=interrupt):
                with self.assertRaises(KeyboardInterrupt):
                    SYNC.sync_targets([first, second], self.source(list(changed)), "6.0.0", "b" * 40, changed)
            self.assertTrue((first / SYNC.JOURNAL_NAME).is_dir())
            self.assertEqual((first / "AGENTS.md").read_bytes(), b"new law")
            self.assertEqual((second / "AGENTS.md").read_bytes(), base["AGENTS.md"])
            SYNC.sync_targets([first, second], self.source(list(changed)), "6.0.0", "b" * 40, changed)
            for target in (first, second):
                self.assertEqual((target / "AGENTS.md").read_bytes(), b"new law")
                SYNC.verify_target(target)
            self.assertFalse((first / SYNC.JOURNAL_NAME).exists())

    def test_interrupted_committed_cleanup_finishes_without_rollback(self):
        base = {name: name.encode() for name in ("SKILL.md", "AGENTS.md", "SOP.md", "SOURCE.json", "VERSION")}
        changed = dict(base, **{"AGENTS.md": b"new law"})
        with tempfile.TemporaryDirectory() as temporary:
            first, second = (Path(temporary) / name for name in ("first", "second"))
            for target in (first, second):
                SYNC.sync_target(target, self.source(list(base)), "6.0.0", COMMIT, base)
            with patch.object(SYNC, "cleanup_journal", side_effect=KeyboardInterrupt("simulated cleanup interruption")):
                with self.assertRaises(KeyboardInterrupt):
                    SYNC.sync_targets([first, second], self.source(list(changed)), "6.0.0", "b" * 40, changed)
            self.assertTrue((first / SYNC.JOURNAL_NAME / SYNC.COMMITTED_NAME).is_file())
            SYNC.sync_targets([first, second], self.source(list(changed)), "6.0.0", "b" * 40, changed)
            for target in (first, second):
                self.assertEqual((target / "AGENTS.md").read_bytes(), b"new law")
                SYNC.verify_target(target)
            self.assertFalse((first / SYNC.JOURNAL_NAME).exists())

    def test_interrupted_preparation_is_discarded_before_retry(self):
        base = {name: name.encode() for name in ("SKILL.md", "AGENTS.md", "SOP.md", "SOURCE.json", "VERSION")}
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "mirror"
            SYNC.sync_target(target, self.source(list(base)), "6.0.0", COMMIT, base)
            write = SYNC.atomic_write

            def interrupt(path, data):
                if SYNC.PREPARING_NAME in path.parts and path.name == "AGENTS.md":
                    raise KeyboardInterrupt("simulated preparation interruption")
                write(path, data)

            with patch.object(SYNC, "atomic_write", side_effect=interrupt):
                with self.assertRaises(KeyboardInterrupt):
                    SYNC.sync_target(target, self.source(list(base)), "6.0.0", "b" * 40, base)
            self.assertTrue((target / SYNC.PREPARING_NAME).is_dir())
            self.assertFalse((target / SYNC.JOURNAL_NAME).exists())
            SYNC.sync_target(target, self.source(list(base)), "6.0.0", "b" * 40, base)
            self.assertFalse((target / SYNC.PREPARING_NAME).exists())
            SYNC.verify_target(target)

    def test_commit_record_failure_rolls_back_both_targets(self):
        base = {name: name.encode() for name in ("SKILL.md", "AGENTS.md", "SOP.md", "SOURCE.json", "VERSION")}
        changed = dict(base, **{"AGENTS.md": b"new law"})
        with tempfile.TemporaryDirectory() as temporary:
            first, second = (Path(temporary) / name for name in ("first", "second"))
            for target in (first, second):
                SYNC.sync_target(target, self.source(list(base)), "6.0.0", COMMIT, base)
            write = SYNC.atomic_write

            def fail_commit(path, data):
                if path == first / SYNC.JOURNAL_NAME / SYNC.COMMITTED_NAME:
                    raise OSError("injected commit-record failure")
                write(path, data)

            with patch.object(SYNC, "atomic_write", side_effect=fail_commit):
                with self.assertRaisesRegex(OSError, "injected commit-record failure"):
                    SYNC.sync_targets([first, second], self.source(list(changed)), "6.0.0", "b" * 40, changed)
            for target in (first, second):
                self.assertEqual((target / "AGENTS.md").read_bytes(), base["AGENTS.md"])
                SYNC.verify_target(target)
            self.assertFalse((first / SYNC.JOURNAL_NAME).exists())

    def test_cleanup_interrupted_after_backup_deletion_resumes(self):
        base = {name: name.encode() for name in ("SKILL.md", "AGENTS.md", "SOP.md", "SOURCE.json", "VERSION")}
        changed = dict(base, **{"AGENTS.md": b"new law"})
        with tempfile.TemporaryDirectory() as temporary:
            first, second = (Path(temporary) / name for name in ("first", "second"))
            for target in (first, second):
                SYNC.sync_target(target, self.source(list(base)), "6.0.0", COMMIT, base)
            unlink = Path.unlink
            failed = False

            def interrupt_cleanup(path, *args, **kwargs):
                nonlocal failed
                if SYNC.JOURNAL_NAME in path.parts and path.name == "AGENTS.md" and not failed:
                    failed = True
                    raise KeyboardInterrupt("simulated partial cleanup")
                return unlink(path, *args, **kwargs)

            with patch.object(Path, "unlink", interrupt_cleanup):
                with self.assertRaises(KeyboardInterrupt):
                    SYNC.sync_targets([first, second], self.source(list(changed)), "6.0.0", "b" * 40, changed)
            self.assertTrue((first / SYNC.JOURNAL_NAME / SYNC.COMMITTED_NAME).is_file())
            SYNC.sync_targets([first, second], self.source(list(changed)), "6.0.0", "b" * 40, changed)
            for target in (first, second):
                self.assertEqual((target / "AGENTS.md").read_bytes(), b"new law")
                SYNC.verify_target(target)
            self.assertFalse((first / SYNC.JOURNAL_NAME).exists())

    def test_recover_only_cli_rolls_back_without_fetching_source(self):
        base = {name: name.encode() for name in ("SKILL.md", "AGENTS.md", "SOP.md", "SOURCE.json", "VERSION")}
        changed = dict(base, **{"AGENTS.md": b"new law"})
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "mirror"
            SYNC.sync_target(target, self.source(list(base)), "6.0.0", COMMIT, base)
            write = SYNC.atomic_write

            def interrupt(path, data):
                if path == target / "AGENTS.md":
                    raise KeyboardInterrupt("simulated interruption")
                write(path, data)

            with patch.object(SYNC, "atomic_write", side_effect=interrupt):
                with self.assertRaises(KeyboardInterrupt):
                    SYNC.sync_target(target, self.source(list(changed)), "6.0.0", "b" * 40, changed)
            with patch.object(sys, "argv", ["sync.py", "--recover-only", str(target)]), \
                 patch.object(SYNC, "resolve_commit", side_effect=AssertionError("network must not be used")):
                self.assertEqual(SYNC.main(), 0)
            self.assertEqual((target / "AGENTS.md").read_bytes(), base["AGENTS.md"])
            self.assertFalse((target / SYNC.JOURNAL_NAME).exists())
            SYNC.verify_target(target)


if __name__ == "__main__":
    unittest.main()
