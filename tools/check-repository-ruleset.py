#!/usr/bin/env python3
"""Read-only audit of the GitHub controls protecting canonical main."""
from __future__ import annotations

import json
import subprocess
import sys

REPO = "repos/MrWizard94-Compile/Agents-Constitution"
NAME = "WPAI Constitution main PR and validation gate"
GITHUB_ACTIONS_APP_ID = 15368
EXPECTED_TYPES = {"deletion", "non_fast_forward", "pull_request", "required_status_checks"}


def fetch_json(path: str) -> object:
    result = subprocess.run(
        ["gh", "api", f"{REPO}{path}"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20, check=True,
    )
    if len(result.stdout) > 1_000_000:
        raise ValueError("GitHub response exceeds audit size limit")
    return json.loads(result.stdout)


def audit(rulesets: object, detail: object, effective: object) -> list[str]:
    """Return policy drift from authenticated GitHub read responses."""
    errors: list[str] = []
    if not isinstance(rulesets, list) or len(rulesets) >= 100:
        return ["ruleset listing is invalid or incomplete"]
    matching = [item for item in rulesets if isinstance(item, dict) and item.get("name") == NAME]
    if len(matching) != 1:
        return [f"expected one named ruleset, found {len(matching)}"]
    item = matching[0]
    if not isinstance(detail, dict) or detail.get("id") != item.get("id"):
        return ["ruleset detail does not match listing"]
    if detail.get("target") != "branch" or detail.get("enforcement") != "active":
        errors.append("ruleset must actively target branches")
    if detail.get("bypass_actors") != []:
        errors.append("ruleset has bypass actors")
    conditions = detail.get("conditions")
    if not isinstance(conditions, dict) or conditions.get("ref_name") != {"include": ["refs/heads/main"], "exclude": []}:
        errors.append("ruleset must target only refs/heads/main")
    rules = detail.get("rules")
    if not isinstance(rules, list) or {rule.get("type") for rule in rules if isinstance(rule, dict)} != EXPECTED_TYPES or len(rules) != 4:
        return errors + ["ruleset does not contain exactly the four expected rules"]
    by_type = {rule["type"]: rule for rule in rules}
    pull = by_type["pull_request"].get("parameters", {})
    if not isinstance(pull, dict) or type(pull.get("required_approving_review_count")) is not int or pull.get("required_approving_review_count") != 0 or pull.get("required_reviewers") != [] or any(pull.get(key) is not False for key in (
        "require_code_owner_review", "require_last_push_approval", "require_extra_approval_for_unattributed_changes",
    )):
        errors.append("pull requests must require zero approvals, including unattributed changes")
    checks = by_type["required_status_checks"].get("parameters", {})
    if not isinstance(checks, dict) or checks.get("required_status_checks") != [{"context": "validate", "integration_id": GITHUB_ACTIONS_APP_ID}] or checks.get("strict_required_status_checks_policy") is not True:
        errors.append("the sole required check must be strict validate from GitHub Actions")
    if not isinstance(effective, list) or len(effective) >= 100:
        return errors + ["effective branch rules response is invalid"]
    applied = [rule for rule in effective if isinstance(rule, dict) and rule.get("ruleset_id") == item["id"]]
    if len(applied) != 4 or {rule.get("type") for rule in applied} != EXPECTED_TYPES:
        errors.append("all four rules are not effective on main")
    return errors


def main() -> int:
    try:
        rulesets = fetch_json("/rulesets?per_page=100")
        if not isinstance(rulesets, list) or len(rulesets) >= 100:
            print("UNVERIFIED: ruleset listing is invalid or incomplete")
            return 2
        matching = [item for item in rulesets if isinstance(item, dict) and item.get("name") == NAME]
        if len(matching) != 1 or not isinstance(matching[0].get("id"), int):
            print(f"DRIFT: expected one named ruleset, found {len(matching)}")
            return 1
        detail = fetch_json(f"/rulesets/{matching[0]['id']}")
        effective = fetch_json("/rules/branches/main?per_page=100")
        errors = audit(rulesets, detail, effective)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"UNVERIFIED: GitHub ruleset audit could not complete ({type(exc).__name__})")
        return 2
    if errors:
        for error in errors:
            print(f"DRIFT: {error}")
        return 1
    print(f"PASS: active canonical main ruleset {matching[0]['id']} requires PR, strict GitHub Actions validate, no approvals, and blocks force-push/deletion")
    return 0


if __name__ == "__main__":
    sys.exit(main())
