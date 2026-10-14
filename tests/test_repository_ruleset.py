from __future__ import annotations

import importlib.util
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ruleset_audit", ROOT / "tools" / "check-repository-ruleset.py")
assert spec and spec.loader
AUDIT = importlib.util.module_from_spec(spec)
spec.loader.exec_module(AUDIT)


def fixture():
    rules = [
        {"type": "deletion"},
        {"type": "non_fast_forward"},
        {"type": "pull_request", "parameters": {
            "required_approving_review_count": 0,
            "require_code_owner_review": False,
            "require_last_push_approval": False,
            "require_extra_approval_for_unattributed_changes": False,
            "required_reviewers": [],
        }},
        {"type": "required_status_checks", "parameters": {
            "required_status_checks": [{"context": "validate", "integration_id": AUDIT.GITHUB_ACTIONS_APP_ID}],
            "strict_required_status_checks_policy": True,
        }},
    ]
    listing = [{"id": 42, "name": AUDIT.NAME}]
    detail = {"id": 42, "target": "branch", "enforcement": "active", "bypass_actors": [],
              "conditions": {"ref_name": {"include": ["refs/heads/main"], "exclude": []}},
              "rules": rules}
    effective = [{"type": rule["type"], "ruleset_id": 42} for rule in rules]
    return listing, detail, effective


class RulesetAuditTests(unittest.TestCase):
    def test_approved_policy_passes(self):
        self.assertEqual(AUDIT.audit(*fixture()), [])

    def test_all_bypass_paths_and_missing_rules_fail(self):
        for mutation in ("bypass", "approval", "required_reviewer", "extra_approval", "wrong_branch", "loose_check", "wrong_check_app", "missing_effective"):
            with self.subTest(mutation=mutation):
                listing, detail, effective = deepcopy(fixture())
                if mutation == "bypass":
                    detail["bypass_actors"] = [{"actor_id": 1}]
                elif mutation == "approval":
                    detail["rules"][2]["parameters"]["required_approving_review_count"] = 1
                elif mutation == "required_reviewer":
                    detail["rules"][2]["parameters"]["required_reviewers"] = [{"minimum_approvals": 1}]
                elif mutation == "extra_approval":
                    detail["rules"][2]["parameters"]["require_extra_approval_for_unattributed_changes"] = True
                elif mutation == "wrong_branch":
                    detail["conditions"]["ref_name"]["include"] = ["refs/heads/dev"]
                elif mutation == "loose_check":
                    detail["rules"][3]["parameters"]["strict_required_status_checks_policy"] = False
                elif mutation == "wrong_check_app":
                    detail["rules"][3]["parameters"]["required_status_checks"][0]["integration_id"] = 1
                else:
                    effective.pop()
                self.assertTrue(AUDIT.audit(listing, detail, effective))

    def test_duplicate_or_incomplete_listing_fails(self):
        listing, detail, effective = fixture()
        self.assertTrue(AUDIT.audit(listing + listing, detail, effective))
        self.assertTrue(AUDIT.audit(listing * 100, detail, effective))


if __name__ == "__main__":
    unittest.main()
