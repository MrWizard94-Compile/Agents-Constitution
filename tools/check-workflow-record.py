#!/usr/bin/env python3
"""Validate a local SOP record, never execute or fetch its evidence references.

Exit 0: internally consistent record (not proof of compliance). Exit 1: invalid
record or unmet requested completion. Exit 2: unreadable/invalid JSON input.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

KINDS = {"analysis", "review", "source", "package", "install", "runtime",
         "physical", "authorization", "publication"}
MAX_BYTES = 1_000_000


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def check(record: object, require_complete: bool = False) -> list[str]:
    errors: list[str] = []

    def text(value):
        return isinstance(value, str) and bool(value.strip()) and len(value) <= 10_000

    def fields(value, names, label):
        if not isinstance(value, dict) or set(value) != set(names.split()):
            errors.append(f"{label}: exact required fields missing or unknown fields present")
            return False
        return True

    def rows(value, label):
        if not isinstance(value, list) or len(value) > 1000:
            errors.append(f"{label}: bounded list required")
            return []
        return value

    required = "schema invocation law_sha scope candidate claim stages acceptance section0 evidence evolution self_audit remaining"
    if not fields(record, required, "record"):
        return errors
    if type(record["schema"]) is not int or record["schema"] != 1:
        errors.append("schema: integer 1 required")
    for key in ("invocation", "scope", "candidate"):
        if not text(record[key]):
            errors.append(f"{key}: nonempty bounded text required")
    if not isinstance(record["law_sha"], str) or not re.fullmatch(r"[0-9a-f]{40}", record["law_sha"]):
        errors.append("law_sha: full frozen commit required")
    if record["claim"] not in ("complete", "partial", "stopped"):
        errors.append("claim: complete, partial or stopped required")
    closing = require_complete or record["claim"] == "complete"
    if require_complete and record["claim"] != "complete":
        errors.append("completion requested but record does not claim complete")

    evidence = {}
    for item in rows(record["evidence"], "evidence"):
        if not fields(item, "id kind subject reference", "evidence item"):
            continue
        identity = item["id"]
        if not text(identity) or identity in evidence:
            errors.append("evidence: nonempty unique ID required")
            continue
        if not isinstance(item["kind"], str) or item["kind"] not in KINDS:
            errors.append(f"{identity}: unknown evidence class")
        if not text(item["subject"]) or not text(item["reference"]):
            errors.append(f"{identity}: subject and reference required")
        evidence[identity] = item

    def references(value, label, needed=False):
        refs = rows(value, label)
        valid = []
        seen = set()
        for identity in refs:
            if not isinstance(identity, str) or identity not in evidence or identity in seen:
                errors.append(f"{label}: unknown, invalid or duplicate evidence reference")
                continue
            seen.add(identity)
            valid.append(evidence[identity])
        if needed and not valid:
            errors.append(f"{label}: evidence required")
        return valid

    stages = rows(record["stages"], "stages")
    stage_ids = []
    for item in stages:
        if not fields(item, "stage status reason evidence", "stage"):
            continue
        number, status = item["stage"], item["status"]
        if type(number) is not int:
            errors.append("stage: integer required")
        stage_ids.append(number)
        if status not in ("done", "open", "na"):
            errors.append("stage: unknown status")
        refs = references(item["evidence"], f"stage {number}", status == "done")
        if not text(item["reason"]):
            errors.append(f"stage {number}: exit result or reason required")
        if status == "na" and number not in (3, 9):
            errors.append(f"stage {number}: cannot be N/A")
        if closing and status == "open":
            errors.append(f"stage {number}: open at completion")
        if number in (5, 6, 7, 8, 10) and status == "done" and not any(
                r["subject"] == record["candidate"] for r in refs):
            errors.append(f"stage {number}: current candidate evidence required")
        if number == 9 and status == "done":
            kinds = {r["kind"] for r in refs if isinstance(r["kind"], str)
                     and r["subject"] == record["candidate"]}
            if "authorization" not in kinds or "publication" not in kinds:
                errors.append("stage 9: authorization and observed destination evidence required")
    if stage_ids != list(range(1, 11)):
        errors.append("all ten stages must appear exactly once in order")

    criteria = rows(record["acceptance"], "acceptance")
    if not criteria:
        errors.append("at least one acceptance criterion required")
    seen_criteria = set()
    for item in criteria:
        if not fields(item, "id criterion status required_evidence evidence", "criterion"):
            continue
        identity = item["id"]
        if not text(identity) or identity in seen_criteria:
            errors.append("criterion: unique nonempty ID required")
            continue
        seen_criteria.add(identity)
        if not text(item["criterion"]) or item["status"] not in ("pass", "fail", "open"):
            errors.append(f"{identity}: criterion and valid status required")
        needed = rows(item["required_evidence"], f"{identity} required_evidence")
        if (not needed or any(not isinstance(k, str) or k not in KINDS for k in needed)
                or len(set(k for k in needed if isinstance(k, str))) != len(needed)):
            errors.append(f"{identity}: unique known evidence classes required")
        refs = references(item["evidence"], identity, item["status"] == "pass")
        if item["status"] == "pass":
            current = {r["kind"] for r in refs if r["subject"] == record["candidate"] and isinstance(r["kind"], str)}
            if any(not isinstance(kind, str) or kind not in current for kind in needed):
                errors.append(f"{identity}: required evidence on the current candidate missing")
        if closing and item["status"] != "pass":
            errors.append(f"{identity}: unmet acceptance at completion")

    gate_ids = []
    for item in rows(record["section0"], "section0"):
        if not fields(item, "item status reason evidence", "Section 0 item"):
            continue
        number, status = item["item"], item["status"]
        if type(number) is not int:
            errors.append("Section 0: integer item required")
        gate_ids.append(number)
        if status not in ("pass", "fail", "na", "open") or not text(item["reason"]):
            errors.append(f"Section 0 {number}: status and reason required")
        refs = references(item["evidence"], f"Section 0 {number}", status == "pass")
        if status == "pass" and not any(r["subject"] == record["candidate"] for r in refs):
            errors.append(f"Section 0 {number}: current candidate evidence required")
        if closing and status in ("fail", "open"):
            errors.append(f"Section 0 {number}: incomplete at completion")
    if gate_ids != list(range(1, 16)):
        errors.append("all 15 Section 0 items must appear exactly once in order")

    evolution = record["evolution"]
    if fields(evolution, "status evidence", "evolution"):
        if evolution["status"] not in ("unstarted", "staged", "in-pr", "accepted"):
            errors.append("evolution: unknown status")
        references(evolution["evidence"], "evolution", evolution["status"] != "unstarted")
        if closing and evolution["status"] == "unstarted":
            errors.append("evolution: missing at completion")
    audit = rows(record["self_audit"], "self_audit")
    if any(not text(line) for line in audit) or (closing and not 3 <= len(audit) <= 12):
        errors.append("self_audit: completion requires 3-12 nonempty lines")
    if any(not text(line) for line in rows(record["remaining"], "remaining")):
        errors.append("remaining: nonempty next-action descriptions required")
    return errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args(argv)
    try:
        with args.record.open("rb") as stream:
            data = stream.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ValueError("record exceeds size bound")
        record = json.loads(data.decode("utf-8-sig"), object_pairs_hook=unique_object)
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        print(f"UNREADABLE: workflow record ({type(exc).__name__})")
        return 2
    errors = check(record, args.require_complete)
    if errors:
        for error in errors:
            print(f"INVALID RECORD: {error}")
        return 1
    print(f"VALID RECORD ({record['claim']}): independently inspect cited evidence; "
          "this is not proof of execution, authorization or compliance")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
