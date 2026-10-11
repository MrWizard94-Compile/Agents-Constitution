from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


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


if __name__ == "__main__":
    unittest.main()
