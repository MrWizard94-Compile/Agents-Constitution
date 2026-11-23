#!/usr/bin/env python3
"""Read-only live audit of the canonical repository's two-name branch budget."""
from __future__ import annotations

import json
import subprocess
import sys

REPO = "repos/MrWizard94-Compile/Agents-Constitution"
NAME = "WPAI Constitution two-branch budget"
REVIEW = "codex/constitution-review"
ALLOWED = {"main", REVIEW}
PROBE = "wpai-branch-policy-probe"


def fetch_json(path: str) -> object:
    result = subprocess.run(
        ["gh", "api", f"{REPO}{path}"], check=True, timeout=20,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if len(result.stdout) > 1_000_000:
        raise ValueError("GitHub response exceeds audit size limit")
    return json.loads(result.stdout)


def audit(repository: object, branches: object, detail: object,
          effective: dict[str, object]) -> list[str]:
    """Reject drift without modifying refs, settings, or repository contents."""
    errors: list[str] = []
    if not isinstance(repository, dict) or repository.get("default_branch") != "main":
        errors.append("default branch must be main")
    if not isinstance(repository, dict) or repository.get("delete_branch_on_merge") is not True:
        errors.append("automatic head-branch deletion must be enabled")
    if (not isinstance(branches, list) or len(branches) >= 100
            or any(not isinstance(b, dict) or not isinstance(b.get("name"), str) for b in branches)):
        errors.append("branch listing is invalid or incomplete")
    else:
        names = [b["name"] for b in branches]
        if len(names) != len(set(names)) or "main" not in names or not set(names) <= ALLOWED:
            errors.append("only main and the optional codex/constitution-review branch are allowed")
    if not isinstance(detail, dict):
        return errors + ["branch-budget ruleset detail is invalid"]
    if detail.get("name") != NAME or detail.get("target") != "branch" or detail.get("enforcement") != "active":
        errors.append("the named branch-budget ruleset must be active")
    if detail.get("bypass_actors") != []:
        errors.append("branch-budget ruleset must have no bypass actors")
    refs = detail.get("conditions", {})
    refs = refs.get("ref_name", {}) if isinstance(refs, dict) else {}
    excluded = refs.get("exclude") if isinstance(refs, dict) else None
    if (not isinstance(refs, dict) or refs.get("include") != ["~ALL"]
            or not isinstance(excluded, list) or len(excluded) != 2
            or any(not isinstance(name, str) for name in excluded)
            or set(excluded) != {f"refs/heads/{name}" for name in ALLOWED}):
        errors.append("creation restriction must exclude exactly the two allowed names")
    if detail.get("rules") != [{"type": "creation"}]:
        errors.append("branch-budget ruleset must contain only a creation restriction")
    for name in ("main", REVIEW, PROBE):
        rules = effective.get(name)
        if not isinstance(rules, list) or len(rules) >= 100 or any(not isinstance(r, dict) for r in rules):
            errors.append(f"effective rules for {name} are invalid or incomplete")
            continue
        creations = [rule for rule in rules if rule.get("type") == "creation"]
        if name in ALLOWED and creations:
            errors.append(f"an effective creation restriction blocks allowed branch {name}")
        if name == PROBE and not any(rule.get("ruleset_id") == detail.get("id") for rule in creations):
            errors.append("the budget creation restriction is not effective on prohibited names")
    return errors


def main() -> int:
    try:
        listing = fetch_json("/rulesets?per_page=100")
        if not isinstance(listing, list) or len(listing) >= 100:
            raise ValueError("ruleset listing is invalid or incomplete")
        found = [r for r in listing if isinstance(r, dict) and r.get("name") == NAME]
        if len(found) != 1 or type(found[0].get("id")) is not int:
            print(f"DRIFT: expected one branch-budget ruleset, found {len(found)}")
            return 1
        detail = fetch_json(f"/rulesets/{found[0]['id']}")
        if (not isinstance(detail, dict) or detail.get("id") != found[0]["id"]
                or not isinstance(detail.get("bypass_actors"), list)):
            raise ValueError("ruleset detail is mismatched or redacted; authenticate gh")
        repository = fetch_json("")
        branches = fetch_json("/branches?per_page=100")
        effective = {name: fetch_json(f"/rules/branches/{name}?per_page=100")
                     for name in ("main", REVIEW, PROBE)}
        errors = audit(repository, branches, detail, effective)
    except (OSError, ValueError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        print(f"UNVERIFIED: branch policy could not be audited ({type(exc).__name__})")
        return 2
    if errors:
        for error in errors:
            print(f"DRIFT: {error}")
        return 1
    print("PASS: main plus at most one review branch; automatic deletion enabled; "
          "effective creation restriction allows only those names without bypass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
