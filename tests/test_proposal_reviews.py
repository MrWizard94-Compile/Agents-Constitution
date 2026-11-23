from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec and spec.loader
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


REGISTER = module("proposal_register", "tools/check-proposals.py")
VALIDATOR = module("reviewed_source", "tools/validate-source.py")
BASE = "c5331af55d3aadf30633c96ae2404845ec830723"


class ProposalRegisterTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)
        for relative in ("AGENTS.md", "governance/EVOLUTION.md", "SOURCE.json",
                         "law/ENGINEERING.md", "law/OPERATIONS.md", "law/SECURITY.md",
                         "law/COLLABORATION.md", "law/SPECIALIST.md"):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        self.data = json.loads((ROOT / "evolution/proposals/manifest.json").read_text())
        self.data["entries"] = [next(e for e in self.data["entries"] if e["kind"] == "public-patch")]
        self.entry = self.data["entries"][0]
        target = self.root / "evolution/proposals" / self.entry["patch"]
        target.parent.mkdir(parents=True)
        shutil.copyfile(ROOT / "evolution/proposals" / self.entry["patch"], target)
        self.save()

    def save(self):
        (self.root / "evolution/proposals/manifest.json").write_text(json.dumps(self.data), encoding="utf-8")

    def test_valid_evidence_and_visible_pending_have_different_completion_results(self):
        self.assertEqual(REGISTER.check(self.root, True), ([], {"incorporated": 1}))
        self.entry["status"] = "pending"
        self.save()
        self.assertEqual(REGISTER.check(self.root), ([], {"pending": 1}))
        errors, counts = REGISTER.check(self.root, True)
        self.assertEqual(counts, {"pending": 1})
        self.assertIn("1 unresolved proposal(s) remain", errors)

    def test_corrupt_bytes_false_digest_or_unregistered_archive_file_fails(self):
        target = self.root / "evolution/proposals" / self.entry["patch"]
        original = target.read_bytes()
        target.write_bytes(original + b"corruption")
        self.assertTrue(REGISTER.check(self.root)[0])
        target.write_bytes(original)
        self.entry["sha256"] = "0" * 64
        self.save()
        self.assertTrue(REGISTER.check(self.root)[0])
        self.entry["sha256"] = json.loads((ROOT / "evolution/proposals/manifest.json").read_text())["entries"][0]["sha256"]
        self.save()
        (target.parent / "orphan.patch").write_text("unregistered")
        self.assertIn("archive contains missing or unregistered evidence", REGISTER.check(self.root)[0])

    def test_absolute_traversal_duplicate_and_mismatched_patch_paths_fail(self):
        original = self.entry["patch"]
        for path in ("../secret.patch", "/outside.patch", "archive/000000000000.patch", "archive/nested/file.patch"):
            with self.subTest(path=path):
                self.entry["patch"] = path
                self.save()
                self.assertTrue(REGISTER.check(self.root)[0])
        self.entry["patch"] = original
        other = dict(self.entry, id="another-id")
        self.data["entries"].append(other)
        self.save()
        self.assertTrue(REGISTER.check(self.root)[0])

    def test_linked_evidence_is_rejected_without_reading_target(self):
        # Model the platform's link classification at the file boundary; no
        # privileged Windows symlink creation or real outside read is needed.
        original = Path.is_symlink
        def linked(path):
            return path.name.endswith(".patch") or original(path)
        with patch.object(Path, "is_symlink", linked):
            errors, _ = REGISTER.check(self.root)
        self.assertTrue(any("linked evidence" in e for e in errors), errors)

    def test_missing_reason_bad_home_status_and_duplicate_identity_fail(self):
        original = dict(self.entry)
        for field, value in (("reason", ""), ("rule_ids", ["MISSING-HOME-001"]),
                             ("status", "accepted-because-archived"), ("commit", "short"),
                             ("parent", "unknown"), ("original_prs", [True])):
            with self.subTest(field=field):
                self.entry.clear()
                self.entry.update(original, **{field: value})
                self.save()
                self.assertTrue(REGISTER.check(self.root)[0])
        self.entry.clear()
        self.entry.update(original)
        self.data["entries"].append(dict(original))
        self.save()
        self.assertIn("proposal IDs must be valid and unique", REGISTER.check(self.root)[0])

    def test_private_raw_patch_and_unsupported_historical_closure_fail(self):
        self.entry.update(kind="local-proposal", private_recovery=True)
        self.save()
        self.assertTrue(any("private raw patch" in e for e in REGISTER.check(self.root)[0]))
        self.entry.update(kind="historical-pr", original_prs=[])
        self.save()
        self.assertTrue(any("must name its PR" in e for e in REGISTER.check(self.root)[0]))

    def test_invalid_json_duplicate_keys_and_mirror_exposure_fail_closed(self):
        manifest = self.root / "evolution/proposals/manifest.json"
        for content in ('{"schema": 2, "schema": 2}', '[]', '{broken'):
            with self.subTest(content=content):
                manifest.write_text(content)
                self.assertTrue(REGISTER.check(self.root)[0])
        self.save()
        source = self.root / "SOURCE.json"
        data = json.loads(source.read_text())
        data["mirror_files"].append("evolution/proposals/manifest.json")
        source.write_text(json.dumps(data))
        self.assertIn("proposal evidence must remain outside binding law mirrors", REGISTER.check(self.root)[0])
        source.write_text('[]')
        self.assertTrue(REGISTER.check(self.root)[0])

    def test_unavailable_oversized_evidence_and_future_resolution_fail(self):
        self.data["resolution_version"] = "999.0.0"
        self.save()
        self.assertIn("resolution version cannot be newer than its containing source", REGISTER.check(self.root)[0])
        target = self.root / "evolution/proposals" / self.entry["patch"]
        target.write_bytes(b"x" * 1_000_001)
        self.assertTrue(REGISTER.check(self.root)[0])
        target.unlink()
        self.assertTrue(REGISTER.check(self.root)[0])

    def test_current_register_and_original_git_archive_have_independent_provenance(self):
        self.assertEqual(REGISTER.check(ROOT)[0], [])
        def blob(relative):
            return subprocess.run(["git", "show", BASE + ":" + relative], cwd=ROOT,
                                  check=True, capture_output=True).stdout
        original = json.loads(blob("evolution/pending/manifest.json"))
        current = json.loads((ROOT / "evolution/proposals/manifest.json").read_text())
        by_commit = {e["commit"]: e for e in current["entries"] if e["kind"] == "public-patch"}
        self.assertEqual(len(original["entries"]), 9)
        for entry in original["entries"]:
            with self.subTest(commit=entry["commit"]):
                reviewed = by_commit[entry["commit"]]
                self.assertEqual(reviewed["parent"], entry["parent"])
                self.assertEqual(reviewed["sha256"], entry["sha256"])
                self.assertEqual((ROOT / "evolution/proposals" / reviewed["patch"]).read_bytes(),
                                 blob("evolution/pending/" + entry["patch"]))

    def test_all_reviewed_local_variants_and_historical_closures_remain_traceable(self):
        data = json.loads((ROOT / "evolution/proposals/manifest.json").read_text())
        by_id = {entry["id"]: entry for entry in data["entries"]}
        expected = {
            "local-5a95b5e85396": "incorporated", "local-complete-file-repair": "incorporated",
            "local-f8bb2b75e764": "superseded", "local-b62e221cf894": "superseded",
            "historical-pr-5": "covered", "historical-pr-7": "obsolete",
            "historical-pr-9": "obsolete", "historical-pr-10": "covered",
        }
        for identity, status in expected.items():
            with self.subTest(identity=identity):
                self.assertIn(identity, by_id)
                self.assertEqual(by_id[identity]["status"], status)
                self.assertTrue(by_id[identity]["reason"])
                self.assertTrue(by_id[identity]["rule_ids"])


class ReviewedEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "source"
        self.addCleanup(self.temporary.cleanup)
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(".git", ".local-audit", "__pycache__"))

    def test_current_source_and_reflowed_prose_keep_reviewed_contracts(self):
        self.assertEqual(VALIDATOR.reviewed_evidence_contract_errors(self.root), [])
        for relative in ("law/ENGINEERING.md", "law/OPERATIONS.md", "law/COLLABORATION.md", "law/SPECIALIST.md", "SOP.md"):
            target = self.root / relative
            target.write_text(target.read_text().upper().replace("NAMED QUANTITY THROUGH", "NAMED\nQUANTITY THROUGH"))
        self.assertEqual(VALIDATOR.reviewed_evidence_contract_errors(self.root), [])

    def test_removing_each_distinct_evidence_boundary_fails(self):
        mutations = (
            ("ENGINEERING", "project-owned compile tasks", "ENG-STACK-001"),
            ("ENGINEERING", "positive repair marker", "ENG-FW-001"),
            ("ENGINEERING", "absent-or-zero payload buffer", "TEST-QUALITY-001"),
            ("ENGINEERING", "round-trips the declared cell count", "TEST-QUALITY-001"),
            ("ENGINEERING", "without sliding", "TEST-QUALITY-001"),
            ("ENGINEERING", "independent outward-winding oracle", "TEST-QUALITY-001"),
            ("OPERATIONS", "only in combination", "VCS-INTEG-001"),
            ("OPERATIONS", "another path does not satisfy the action", "MIG-VERIFY-001"),
            ("OPERATIONS", "intentionally authorized deletion", "OPS-DEL-002"),
            ("OPERATIONS", "do not treat the approval record as that observation", "REL-HARDEN-001"),
            ("COLLABORATION", "each worker's delta", "AI-COORD-002"),
            ("COLLABORATION", "immutable integrated candidate", "AI-COORD-003"),
            ("SPECIALIST", "inactive consumer joining later", "LOW-RISK-001"),
        )
        for home, phrase, rule in mutations:
            with self.subTest(phrase=phrase):
                target = self.root / "law" / (home + ".md")
                original = target.read_text()
                needle = r"\s+".join(re.escape(word) for word in phrase.split())
                mutated, count = re.subn(needle, "removed evidence", original, count=1)
                self.assertEqual(count, 1, "the complete semantic clause must actually be removed")
                target.write_text(mutated)
                self.assertIn(f"{rule} reviewed safeguard missing: {phrase}",
                              VALIDATOR.reviewed_evidence_contract_errors(self.root))
                target.write_text(original)

    def test_guard_cannot_borrow_missing_clause_from_another_section_or_archive(self):
        target = self.root / "law/ENGINEERING.md"
        text = target.read_text().replace("without sliding", "with proxy evidence")
        target.write_text(text + "\n## Historical note\nwithout sliding\n")
        self.assertIn("TEST-QUALITY-001 reviewed safeguard missing: without sliding",
                      VALIDATOR.reviewed_evidence_contract_errors(self.root))

    def test_missing_home_and_sop_routes_fail(self):
        target = self.root / "law/OPERATIONS.md"
        target.write_text(target.read_text().replace("### VCS-INTEG-001", "### Removed rule"))
        sop = self.root / "SOP.md"
        sop.write_text(sop.read_text().replace("REL-HARDEN-001", "REMOVED-RULE"))
        errors = VALIDATOR.reviewed_evidence_contract_errors(self.root)
        self.assertIn("VCS-INTEG-001 reviewed evidence home missing", errors)
        self.assertIn("SOP.md missing reviewed evidence route: REL-HARDEN-001", errors)

    def test_full_source_validator_rejects_a_removed_reviewed_clause(self):
        self.assertEqual(VALIDATOR.validate(self.root), [])
        target = self.root / "law/OPERATIONS.md"
        target.write_text(target.read_text().replace("another path does not satisfy the action", "a sibling log is enough"))
        self.assertIn("MIG-VERIFY-001 reviewed safeguard missing: another path does not satisfy the action",
                      VALIDATOR.validate(self.root))


if __name__ == "__main__":
    unittest.main()
