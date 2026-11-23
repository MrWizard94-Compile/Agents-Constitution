from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import subprocess
import unittest
from contextlib import redirect_stdout
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("branch_policy", ROOT / "tools/check-branch-policy.py")
assert SPEC and SPEC.loader
POLICY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(POLICY)


def fixture():
    repository = {"default_branch": "main", "delete_branch_on_merge": True}
    branches = [{"name": "main"}, {"name": POLICY.REVIEW}]
    detail = {"id": 123, "name": POLICY.NAME, "target": "branch", "enforcement": "active",
              "bypass_actors": [], "conditions": {"ref_name": {
                  "include": ["~ALL"], "exclude": ["refs/heads/main", f"refs/heads/{POLICY.REVIEW}"]}},
              "rules": [{"type": "creation"}]}
    effective = {"main": [{"type": "deletion", "ruleset_id": 456}], POLICY.REVIEW: [],
                 POLICY.PROBE: [{"type": "creation", "ruleset_id": 123}]}
    return repository, branches, detail, effective


class BranchPolicyTests(unittest.TestCase):
    def test_main_alone_and_one_review_slot_pass(self):
        args = fixture()
        self.assertEqual(POLICY.audit(*args), [])
        args[1].pop()
        self.assertEqual(POLICY.audit(*args), [])
        args[2]["conditions"]["ref_name"]["exclude"].reverse()
        self.assertEqual(POLICY.audit(*args), [])

    def test_third_branch_missing_main_duplicate_or_incomplete_listing_fails(self):
        for branches in ([{"name": "main"}, {"name": "forgotten"}],
                         [{"name": POLICY.REVIEW}], [{"name": "main"}] * 2,
                         [{"name": "main"}] * 100, [{}], None):
            with self.subTest(branches=branches):
                repo, _, detail, effective = fixture()
                self.assertTrue(POLICY.audit(repo, branches, detail, effective))

    def test_disabled_automatic_deletion_or_changed_default_fails(self):
        for field, value in (("delete_branch_on_merge", False), ("delete_branch_on_merge", 1),
                             ("default_branch", "develop")):
            with self.subTest(field=field, value=value):
                args = fixture()
                args[0][field] = value
                self.assertTrue(POLICY.audit(*args))

    def test_bypass_wildcards_disabled_or_extra_restrictions_fail(self):
        for mutation in ("bypass", "disabled", "target", "wildcard", "include", "extra", "duplicate"):
            with self.subTest(mutation=mutation):
                args = fixture()
                detail = args[2]
                if mutation == "bypass":
                    detail["bypass_actors"] = [{"actor_id": 1}]
                elif mutation == "disabled":
                    detail["enforcement"] = "evaluate"
                elif mutation == "target":
                    detail["target"] = "tag"
                elif mutation == "wildcard":
                    detail["conditions"]["ref_name"]["exclude"][1] = "refs/heads/codex/*"
                elif mutation == "include":
                    detail["conditions"]["ref_name"]["include"] = ["refs/heads/feature/*"]
                elif mutation == "duplicate":
                    detail["conditions"]["ref_name"]["exclude"] = ["refs/heads/main"] * 2
                else:
                    detail["rules"].append({"type": "update"})
                self.assertTrue(POLICY.audit(*args))

    def test_effective_creation_rule_must_cover_only_prohibited_names(self):
        for mutation in ("absent", "wrong_ruleset", "main_blocked", "review_blocked", "incomplete"):
            with self.subTest(mutation=mutation):
                args = fixture()
                effective = args[3]
                if mutation == "absent":
                    effective[POLICY.PROBE] = []
                elif mutation == "wrong_ruleset":
                    effective[POLICY.PROBE][0]["ruleset_id"] = 999
                elif mutation == "incomplete":
                    effective[POLICY.REVIEW] = [{}] * 100
                else:
                    name = "main" if mutation == "main_blocked" else POLICY.REVIEW
                    effective[name].append({"type": "creation", "ruleset_id": 999})
                self.assertTrue(POLICY.audit(*args))

    def test_cli_never_confuses_outage_redaction_drift_and_success(self):
        repo, branches, detail, effective = fixture()
        listing = [{"name": POLICY.NAME, "id": detail["id"]}]
        passing = [listing, detail, repo, branches, *effective.values()]
        drift = deepcopy(passing)
        drift[3].append({"name": "stale"})
        cases = ((passing, 0, "PASS:"), (drift, 1, "DRIFT:"),
                 ([[]], 1, "DRIFT:"), ([listing * 2], 1, "DRIFT:"),
                 ([listing, {k: v for k, v in detail.items() if k != "bypass_actors"}], 2, "UNVERIFIED:"),
                 (subprocess.CalledProcessError(1, ["gh", "api"]), 2, "UNVERIFIED:"),
                 (subprocess.TimeoutExpired(["gh", "api"], 20), 2, "UNVERIFIED:"),
                 ([[{}] * 100], 2, "UNVERIFIED:"))
        for responses, expected, prefix in cases:
            with self.subTest(code=expected, prefix=prefix):
                output = io.StringIO()
                with patch.object(POLICY, "fetch_json", side_effect=responses), redirect_stdout(output):
                    self.assertEqual(POLICY.main(), expected)
                self.assertTrue(output.getvalue().startswith(prefix), output.getvalue())

    def test_public_archived_patches_match_manifest_and_are_outside_binding_set(self):
        folder = ROOT / "evolution/proposals"
        manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
        entries = [e for e in manifest["entries"] if e["kind"] == "public-patch"]
        self.assertEqual(manifest["schema"], 2)
        self.assertEqual(len(entries), 9)
        self.assertEqual({n for entry in entries for n in entry["original_prs"]}, {42, 44, 46, 47, 48, 49})
        expected_files = set()
        for entry in entries:
            with self.subTest(commit=entry["commit"]):
                self.assertEqual(entry["status"], "incorporated")
                self.assertRegex(entry["commit"], r"^[0-9a-f]{40}$")
                self.assertRegex(entry["parent"], r"^[0-9a-f]{40}$")
                self.assertEqual(entry["patch"], "archive/" + entry["commit"][:12] + ".patch")
                content = (folder / entry["patch"]).read_bytes()
                self.assertEqual(hashlib.sha256(content).hexdigest(), entry["sha256"])
                self.assertTrue(content.startswith(b"diff --git "))
                expected_files.add(entry["patch"])
        self.assertEqual({p.relative_to(folder).as_posix() for p in folder.glob("archive/*.patch")}, expected_files)
        source = json.loads((ROOT / "SOURCE.json").read_text(encoding="utf-8"))
        self.assertFalse(any(p.startswith("evolution/proposals/") for p in source["mirror_files"]))


if __name__ == "__main__":
    unittest.main()
