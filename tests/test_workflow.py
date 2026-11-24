from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECKER = load("workflow_checker", "tools/check-workflow-record.py")
VALIDATOR = load("workflow_source", "tools/validate-source.py")


def reviewed_proposal():
    """Synthetic review-only contract; no deployment or authority is implied."""
    record = json.loads((ROOT / "templates/WORKFLOW-RECORD.json").read_text(encoding="utf-8"))
    record.update(invocation="fixture-review", law_sha="a" * 40,
                  scope="Review a policy and prepare an apply-ready amendment; no publication",
                  candidate="fixture-proposal-v1", claim="complete")
    record["evidence"] = [
        {"id": "review", "kind": "review", "subject": "fixture-proposal-v1", "reference": "fixture independent review"},
        {"id": "tests", "kind": "source", "subject": "fixture-proposal-v1", "reference": "fixture test log"},
    ]
    record["acceptance"] = [{"id": "A1", "criterion": "Reviewed complete amendment with tested gate",
                             "status": "pass", "required_evidence": ["review", "source"],
                             "evidence": ["review", "tests"]}]
    for stage in record["stages"]:
        stage.update(status="done", reason="Fixture exit reviewed", evidence=["review"])
    record["stages"][8].update(status="na", reason="Review-only outcome; publication not requested", evidence=[])
    for item in record["section0"]:
        item.update(status="pass", reason="Fixture review result", evidence=["review"])
    record["evolution"] = {"status": "staged", "evidence": ["review", "tests"]}
    record["self_audit"] = ["Fixture source checked.", "Fixture proposal reviewed.", "No publication performed."]
    record["remaining"] = ["Director: review adoption separately"]
    return record


class WorkflowRecordTests(unittest.TestCase):
    def test_review_only_can_complete_with_staged_evolution_and_no_publication(self):
        self.assertEqual(CHECKER.check(reviewed_proposal(), True), [])

    def test_source_qa_cannot_substitute_for_requested_live_deployment(self):
        record = reviewed_proposal()
        record["acceptance"][0]["required_evidence"].append("runtime")
        self.assertIn("A1: required evidence on the current candidate missing", CHECKER.check(record))

    def test_requested_publication_cannot_be_hidden_as_not_applicable(self):
        record = reviewed_proposal()
        record["acceptance"].append({"id": "A2", "criterion": "Publish the reviewed artifact",
                                     "status": "open", "required_evidence": ["publication"], "evidence": []})
        self.assertIn("A2: unmet acceptance at completion", CHECKER.check(record))

    def test_approval_and_destination_observation_are_both_required(self):
        for missing in ("authorization", "publication"):
            with self.subTest(missing=missing):
                record = reviewed_proposal()
                other = "publication" if missing == "authorization" else "authorization"
                record["evidence"].append({"id": other, "kind": other, "subject": record["candidate"],
                                           "reference": "fixture observation"})
                record["stages"][8].update(status="done", evidence=[other])
                self.assertIn("stage 9: authorization and observed destination evidence required", CHECKER.check(record))

    def test_observed_authorized_publication_can_close(self):
        record = reviewed_proposal()
        for kind in ("authorization", "publication"):
            record["evidence"].append({"id": kind, "kind": kind, "subject": record["candidate"],
                                       "reference": "fixture observed result"})
        record["stages"][8].update(status="done", evidence=["authorization", "publication"])
        self.assertEqual(CHECKER.check(record, True), [])

    def test_changed_candidate_invalidates_old_pass_evidence(self):
        record = reviewed_proposal()
        record["candidate"] = "fixture-proposal-v2"
        self.assertIn("A1: required evidence on the current candidate missing", CHECKER.check(record))

    def test_missing_duplicate_reordered_and_invalid_stage_ids_fail(self):
        for replacement in ([], [1] * 10, list(range(10, 0, -1)), [True] + list(range(2, 11))):
            record = reviewed_proposal()
            record["stages"] = [dict(record["stages"][0], stage=i) for i in replacement]
            self.assertTrue(CHECKER.check(record))

    def test_section_zero_cannot_reuse_old_candidate_after_other_evidence_refresh(self):
        record = reviewed_proposal()
        record["evidence"].append({"id": "old-review", "kind": "review", "subject": "fixture-proposal-v0",
                                   "reference": "historical gate evidence"})
        for item in record["section0"]:
            item["evidence"] = ["old-review"]
        errors = CHECKER.check(record, True)
        for number in range(1, 16):
            self.assertIn(f"Section 0 {number}: current candidate evidence required", errors)

    def test_equivalence_review_can_reference_old_and_current_evidence(self):
        record = reviewed_proposal()
        record["evidence"].append({"id": "old-input", "kind": "source", "subject": "unchanged-environment-v1",
                                   "reference": "historical input verification"})
        record["section0"][1].update(evidence=["old-input", "review"],
                                     reason="Current candidate review established unchanged relevant environment inputs")
        self.assertEqual(CHECKER.check(record, True), [])

    def test_workflow_and_section_zero_cannot_hide_open_or_failed_gates(self):
        for area, field, status in (("stages", "stage", "open"), ("section0", "item", "fail"),
                                     ("section0", "item", "open")):
            record = reviewed_proposal()
            record[area][5]["status"] = status
            self.assertTrue(CHECKER.check(record), (area, field, status))
        record = reviewed_proposal()
        record["section0"].pop()
        self.assertIn("all 15 Section 0 items must appear exactly once in order", CHECKER.check(record))

    def test_n_a_needs_reason_and_cannot_waive_verification(self):
        record = reviewed_proposal()
        record["stages"][5].update(status="na", reason="Small task")
        self.assertIn("stage 6: cannot be N/A", CHECKER.check(record))
        record = reviewed_proposal()
        record["stages"][8]["reason"] = " "
        self.assertTrue(CHECKER.check(record))

    def test_partial_and_stop_records_remain_honest_without_completing_evolution(self):
        for state in ("partial", "stopped"):
            record = reviewed_proposal()
            record.update(claim=state)
            record["stages"][9].update(status="open", evidence=[])
            record["acceptance"][0]["status"] = "open"
            record["evolution"] = {"status": "unstarted", "evidence": []}
            record["self_audit"] = []
            self.assertEqual(CHECKER.check(record), [])
            self.assertTrue(CHECKER.check(record, True))

    def test_undefined_duplicate_and_missing_evidence_fail(self):
        for change in ("unknown", "duplicate", "empty"):
            record = reviewed_proposal()
            record["acceptance"][0]["evidence"] = {"unknown": ["unobserved"],
                                                    "duplicate": ["review", "review"], "empty": []}[change]
            self.assertTrue(CHECKER.check(record))
        record = reviewed_proposal()
        record["evidence"].append(copy.deepcopy(record["evidence"][0]))
        self.assertTrue(CHECKER.check(record))

    def test_unknown_and_malformed_fields_fail_without_exceptions(self):
        record = reviewed_proposal()
        for key in record:
            for wrong in (None, [], {}, True, 42):
                if key == "remaining" and wrong == []:
                    continue  # A completed task may have no remaining work.
                changed = copy.deepcopy(record)
                changed[key] = wrong
                with self.subTest(key=key, wrong=wrong):
                    self.assertTrue(CHECKER.check(changed))
        for section in ("stages", "acceptance", "section0", "evidence"):
            for key in record[section][0]:
                for wrong in (None, {}, True):
                    changed = copy.deepcopy(record)
                    changed[section][0][key] = wrong
                    with self.subTest(section=section, key=key, wrong=wrong):
                        self.assertTrue(CHECKER.check(changed))
        changed = copy.deepcopy(record)
        changed["acceptance"][0]["required_evidence"] = [{}]
        self.assertTrue(CHECKER.check(changed))
        changed = copy.deepcopy(record)
        changed["unexpected"] = "typo"
        self.assertTrue(CHECKER.check(changed))

    def test_complete_scope_may_have_no_remaining_work(self):
        record = reviewed_proposal()
        record["remaining"] = []
        self.assertEqual(CHECKER.check(record, True), [])

    def test_template_is_not_a_completed_run(self):
        record = json.loads((ROOT / "templates/WORKFLOW-RECORD.json").read_text())
        self.assertTrue(CHECKER.check(record, True))

    def test_cli_distinguishes_unreadable_invalid_partial_and_complete(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "record.json"
            command = [sys.executable, str(ROOT / "tools/check-workflow-record.py"), str(path)]
            cases = [("{", 2), ('{"schema":1,"schema":1}', 2), ("x" * (CHECKER.MAX_BYTES + 1), 2),
                     (json.dumps({}), 1), (json.dumps(reviewed_proposal()), 0)]
            for body, expected in cases:
                path.write_text(body, encoding="utf-8")
                result = subprocess.run(command, capture_output=True, text=True)
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
                self.assertNotIn("Traceback", result.stderr)
            self.assertIn("not proof", result.stdout)
            record = reviewed_proposal()
            record["claim"] = "partial"
            path.write_text(json.dumps(record), encoding="utf-8")
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertEqual(subprocess.run(command + ["--require-complete"], capture_output=True).returncode, 1)


class WorkflowSourceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for relative in ("SOP.md", "SKILL.md", "AGENTS.md", "references/always-load.md"):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)

    def test_complete_candidate_routes_and_stages_pass(self):
        self.assertEqual(VALIDATOR.workflow_contract_errors(self.root), [])

    def test_rule_name_only_sop_cannot_replace_execution_workflow(self):
        (self.root / "SOP.md").write_text("# Empty SOP\nSOP-EXEC-001 CONST-RESOURCEFUL-001\n")
        errors = VALIDATOR.workflow_contract_errors(self.root)
        self.assertIn("SOP-EXEC-001 execution contract missing", errors)
        self.assertIn("SOP must define ten ordered stages exactly once", errors)

    def test_each_deleted_stage_is_detected(self):
        import re
        path = self.root / "SOP.md"
        original = path.read_text(encoding="utf-8")
        for number in range(1, 11):
            path.write_text(re.sub(rf"^## {number}\. [^\n]+\n.*?(?=^## |\Z)", "", original,
                                   flags=re.M | re.S), encoding="utf-8")
            self.assertIn("SOP must define ten ordered stages exactly once", VALIDATOR.workflow_contract_errors(self.root))

    def test_gate_safeguard_cannot_be_borrowed_from_another_stage(self):
        path = self.root / "SOP.md"
        original = path.read_text(encoding="utf-8")
        changed = original.replace("Verify remote state", "Record attempted state")
        changed += "\n## Historical notes\nVerify remote state\n"
        path.write_text(changed, encoding="utf-8")
        self.assertIn("SOP stage 9 missing safeguard: verify remote state", VALIDATOR.workflow_contract_errors(self.root))

    def test_removing_each_entrypoint_route_is_detected(self):
        for relative in ("SKILL.md", "AGENTS.md", "references/always-load.md"):
            path = self.root / relative
            original = path.read_bytes()
            path.write_bytes(original.replace(b"SOP-EXEC-001", b"no-workflow-route"))
            self.assertIn(f"{relative} must route to SOP-EXEC-001", VALIDATOR.workflow_contract_errors(self.root))
            path.write_bytes(original)


if __name__ == "__main__":
    unittest.main()
