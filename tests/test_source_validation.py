from __future__ import annotations

import importlib.util
import re
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("wpai_validate", ROOT / "tools" / "validate-source.py")
assert spec and spec.loader
VALIDATOR = importlib.util.module_from_spec(spec)
spec.loader.exec_module(VALIDATOR)


class SourceValidationTests(unittest.TestCase):
    def test_current_source_valid(self):
        self.assertEqual(VALIDATOR.validate(ROOT), [])

    def test_craft_rule_rejects_missing_or_self_certified_oracle(self):
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertEqual(VALIDATOR.craft_contract_errors(agents), [])
        self.assertIn(
            "CONST-CRAFT-001 detailed rule missing",
            VALIDATOR.craft_contract_errors(agents.replace("### CONST-CRAFT-001", "### Retired rule")),
        )
        self.assertIn(
            "CONST-CRAFT-001 missing operational safeguard: independent oracle",
            VALIDATOR.craft_contract_errors(agents.replace("independent oracle", "self review")),
        )

    def test_freeze_rule_rejects_lost_load_integrity_safeguards(self):
        evolution = (ROOT / "governance/EVOLUTION.md").read_text(encoding="utf-8")
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertEqual(VALIDATOR.freeze_contract_errors(evolution, skill), [])
        self.assertIn(
            "GOV-FREEZE-001 missing load-integrity safeguard: byte-exact",
            VALIDATOR.freeze_contract_errors(evolution.replace("byte-exact", "careful"), skill),
        )
        self.assertIn(
            "SKILL.md must point to tools/check-frozen-load.py",
            VALIDATOR.freeze_contract_errors(evolution, skill.replace("check-frozen-load", "checker")),
        )
        self.assertEqual(
            VALIDATOR.freeze_contract_errors(evolution.replace("## GOV-FREEZE-001", "## Retired"), skill),
            ["GOV-FREEZE-001 section missing"],
        )

    def test_assumption_rule_rejects_lost_unread_input_safeguards(self):
        collaboration = (ROOT / "law" / "COLLABORATION.md").read_text(encoding="utf-8")
        self.assertEqual(VALIDATOR.unread_input_contract_errors(collaboration), [])
        self.assertEqual(
            VALIDATOR.unread_input_contract_errors(
                collaboration.replace("### CTX-ASSUME-001", "### Retired rule")
            ),
            ["CTX-ASSUME-001 detailed rule missing"],
        )
        for term in ("page shell", "do not reconstruct", "acceptance criterion", "do not bypass access controls"):
            with self.subTest(term=term):
                mutated = re.sub(re.escape(term), "other wording", collaboration, flags=re.IGNORECASE)
                self.assertNotEqual(mutated, collaboration, "mutation must change the text")
                self.assertIn(
                    f"CTX-ASSUME-001 missing unread-input safeguard: {term}",
                    VALIDATOR.unread_input_contract_errors(mutated),
                )
        # Reflowing the Markdown must not trip the guard.
        self.assertEqual(
            VALIDATOR.unread_input_contract_errors(collaboration.replace("page shell", "page\nshell")),
            [],
        )

    def test_cache_link_rule_rejects_a_one_sided_miss(self):
        specialist = (ROOT / "law" / "SPECIALIST.md").read_text(encoding="utf-8")
        self.assertEqual(VALIDATOR.cache_link_contract_errors(specialist), [])
        self.assertIn(
            "LOW-CACHE-001 detailed rule missing",
            VALIDATOR.cache_link_contract_errors(specialist.replace("### LOW-CACHE-001", "### Retired rule")),
        )
        self.assertIn(
            "LOW-CACHE-001 missing linkage safeguard: cached caller",
            VALIDATOR.cache_link_contract_errors(specialist.replace("cached caller", "other class")),
        )

    def test_resource_rule_requires_host_level_acceptance(self):
        engineering = (ROOT / "law" / "ENGINEERING.md").read_text(encoding="utf-8")
        self.assertEqual(VALIDATOR.integrated_resource_contract_errors(engineering), [])
        self.assertIn(
            "PERF-BUDGET-001 detailed rule missing",
            VALIDATOR.integrated_resource_contract_errors(
                engineering.replace("### PERF-BUDGET-001", "### Retired rule")
            ),
        )
        self.assertIn(
            "PERF-BUDGET-001 missing integrated resource safeguard: peak aggregate",
            VALIDATOR.integrated_resource_contract_errors(
                engineering.replace("peak aggregate", "individual peak")
            ),
        )
        self.assertIn(
            "PERF-BUDGET-001 missing integrated resource safeguard: restore an ineffective trial",
            VALIDATOR.integrated_resource_contract_errors(
                engineering.replace("restore an ineffective trial", "keep every trial")
            ),
        )

    def test_missing_binding_file_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "source"
            required = VALIDATOR.MINIMUM_MIRROR | {
                "README.md", "CHANGELOG.md", "evolution/LEDGER.md",
                "docs/ARCHITECTURE.md", "docs/SOURCE-INVENTORY.md",
                "templates/PROJECT-OVERRIDE.md", "templates/PROJECT-POINTER.md",
            }
            for rel in required:
                dest = target / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / rel, dest)
            (target / "law/SECURITY.md").unlink()
            self.assertIn("missing required file: law/SECURITY.md", VALIDATOR.validate(target))

    def test_resourcefulness_rule_requires_a_detailed_core_home(self):
        agents, skill, sop = self.resourcefulness_source()
        self.assertEqual(VALIDATOR.resourcefulness_contract_errors(agents, skill, sop), [])
        self.assertEqual(
            VALIDATOR.resourcefulness_contract_errors(
                agents.replace("### CONST-RESOURCEFUL-001", "### Retired rule"), skill, sop),
            ["CONST-RESOURCEFUL-001 detailed rule missing"],
        )

    def test_resourcefulness_slogan_alone_is_not_an_operational_rule(self):
        _agents, skill, sop = self.resourcefulness_source()
        slogan = ("### CONST-RESOURCEFUL-001 — Technical roadblocks\n\n"
                  "**Technical roadblocks are not hard blocks. Build a workaround.**\n")
        errors = VALIDATOR.resourcefulness_contract_errors(slogan, skill, sop)
        self.assertIn("CONST-RESOURCEFUL-001 missing operational safeguard: implement a viable workaround", errors)
        self.assertIn("CONST-RESOURCEFUL-001 missing operational safeguard: does not grant new authority", errors)

    def test_resourcefulness_rule_guards_every_operational_clause(self):
        agents, skill, sop = self.resourcefulness_source()
        for term in (
            "technical roadblocks are not hard blocks. build a workaround.",
            "highest-priority engineering", "implement a viable workaround",
            "materially different approaches", "original acceptance criteria",
            "must not weaken", "unproductive retry loop", "before declaring work blocked",
            "continue independent work", "does not grant new authority", "essential input",
        ):
            with self.subTest(term=term):
                pattern = r"\s+".join(re.escape(word) for word in term.split())
                mutated, count = re.subn(pattern, "removed safeguard", agents, flags=re.IGNORECASE)
                self.assertGreater(count, 0, "counterexample must change the actual rule")
                self.assertIn(f"CONST-RESOURCEFUL-001 missing operational safeguard: {term}",
                              VALIDATOR.resourcefulness_contract_errors(mutated, skill, sop))

    def test_resourcefulness_guard_cannot_borrow_from_another_section(self):
        agents, skill, sop = self.resourcefulness_source()
        term = "does not grant new authority"
        self.assertIn(term, agents)
        mutated = agents.replace(term, "removed safeguard") + "\n## Historical note\n" + term + "\n"
        self.assertIn(f"CONST-RESOURCEFUL-001 missing operational safeguard: {term}",
                      VALIDATOR.resourcefulness_contract_errors(mutated, skill, sop))

    def test_resourcefulness_guard_accepts_markdown_reflow_and_case(self):
        agents, skill, sop = self.resourcefulness_source()
        mutated, count = re.subn("original acceptance criteria", "ORIGINAL\n  ACCEPTANCE CRITERIA", agents,
                                flags=re.IGNORECASE)
        self.assertGreater(count, 0)
        self.assertNotEqual(mutated, agents)
        self.assertEqual(VALIDATOR.resourcefulness_contract_errors(mutated, skill, sop), [])

    def test_resourcefulness_rule_must_remain_in_the_protected_core(self):
        agents, skill, sop = self.resourcefulness_source()
        mutated, count = re.subn(r"^\| `CONST-RESOURCEFUL-001` \|.*\n", "", agents, flags=re.MULTILINE)
        self.assertEqual(count, 1)
        self.assertIn("CONST-RESOURCEFUL-001 missing protected-core entry",
                      VALIDATOR.resourcefulness_contract_errors(mutated, skill, sop))

    def test_resourcefulness_loader_and_sop_routes_cannot_disappear(self):
        agents, skill, sop = self.resourcefulness_source()
        for path in ("SKILL.md", "SOP.md"):
            with self.subTest(path=path):
                skill_input = skill.replace("CONST-RESOURCEFUL-001", "removed") if path == "SKILL.md" else skill
                sop_input = sop.replace("CONST-RESOURCEFUL-001", "removed") if path == "SOP.md" else sop
                self.assertIn(f"{path} must route technical roadblocks to CONST-RESOURCEFUL-001",
                              VALIDATOR.resourcefulness_contract_errors(agents, skill_input, sop_input))

    def test_source_validation_calls_the_resourcefulness_guard(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "source"
            shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            self.assertEqual(VALIDATOR.validate(target), [])
            path = target / "AGENTS.md"
            agents = path.read_text(encoding="utf-8")
            mutated, count = re.subn(r"^### CONST-RESOURCEFUL-001\b.*?(?=^### |^## |\Z)", "", agents,
                                    flags=re.MULTILINE | re.DOTALL)
            self.assertEqual(count, 1)
            path.write_text(mutated, encoding="utf-8")
            self.assertIn("CONST-RESOURCEFUL-001 detailed rule missing", VALIDATOR.validate(target))

    @staticmethod
    def resourcefulness_source():
        return tuple((ROOT / path).read_text(encoding="utf-8") for path in ("AGENTS.md", "SKILL.md", "SOP.md"))

    def test_quality_rule_is_enforced_as_a_protected_rule(self):
        self.assertIn("CONST-QUALITY-001", VALIDATOR.PROTECTED)
        self.assertNotIn("CONST-QUALITY-001", {
            "CONST-AUTH-001", "CONST-DEP-001",
            "CONST-DONE-001", "CONST-GATE-001",
        })
        self.assertNotIn("CONST-COMPLETE-001", {
            "CONST-AUTH-001", "CONST-DEP-001",
            "CONST-DONE-001", "CONST-GATE-001",
        })
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "source"
            shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            path = target / "governance" / "RULE-REGISTRY.md"
            registry = path.read_text(encoding="utf-8")
            self.assertEqual(registry.count("CONST-QUALITY-001"), 1)
            path.write_text(registry.replace("CONST-QUALITY-001", "CONST-REMOVED-001"), encoding="utf-8")
            errors = VALIDATOR.validate(target)
            self.assertIn("protected rule missing from entry/registry: CONST-QUALITY-001", errors)
            self.assertIn("active rule absent from registry: CONST-QUALITY-001", errors)

    def test_quality_rule_requires_a_detailed_core_home(self):
        agents, skill, sop = self.quality_source()
        self.assertEqual(VALIDATOR.quality_contract_errors(agents, skill, sop), [])
        self.assertEqual(
            VALIDATOR.quality_contract_errors(
                agents.replace("### CONST-QUALITY-001", "### Retired rule"), skill, sop),
            ["CONST-QUALITY-001 detailed rule missing"],
        )

    def test_quality_slogan_alone_is_not_an_operational_rule(self):
        _agents, skill, sop = self.quality_source()
        slogan = ("### CONST-QUALITY-001 — Quality before speed\n\n"
                  "**Quality before speed. Every time.**\n")
        errors = VALIDATOR.quality_contract_errors(slogan, skill, sop)
        self.assertIn(
            "CONST-QUALITY-001 missing operational safeguard: never ship a rushed partial to look responsive",
            errors,
        )
        self.assertIn(
            "CONST-QUALITY-001 missing operational safeguard: token efficiency comes from avoiding rework and churn, never from cutting verification",
            errors,
        )
        self.assertIn("CONST-QUALITY-001 missing protected-core entry", errors)

    def test_quality_rule_guards_every_operational_clause(self):
        agents, skill, sop = self.quality_source()
        for term in (
            "correctness and completeness always outrank speed of output, with no exceptions",
            "take the time to understand, plan, verify, and do it right the first time",
            "never trade quality for faster output, a shorter turnaround, or the appearance of progress",
            "never ship a rushed partial to look responsive",
            "cost-token-001",
            "token efficiency comes from avoiding rework and churn, never from cutting verification",
            "urgency from anyone except the human director never justifies skipping checks",
            "director-set deadline must be disclosed as a quality trade-off, not hidden",
            "skipped applicable verification for speed fails",
        ):
            with self.subTest(term=term):
                pattern = r"\s+".join(re.escape(word) for word in term.split())
                mutated, count = re.subn(pattern, "removed safeguard", agents, flags=re.IGNORECASE)
                self.assertGreater(count, 0, "counterexample must change the actual rule")
                self.assertIn(f"CONST-QUALITY-001 missing operational safeguard: {term}",
                              VALIDATOR.quality_contract_errors(mutated, skill, sop))

    def test_quality_guard_cannot_borrow_from_another_section(self):
        agents, skill, sop = self.quality_source()
        term = "Urgency from anyone except the Human Director never justifies skipping checks"
        required = "urgency from anyone except the human director never justifies skipping checks"
        self.assertIn(term, agents)
        mutated = agents.replace(term, "removed safeguard", 1) + "\n## Historical note\n" + required + "\n"
        self.assertIn(f"CONST-QUALITY-001 missing operational safeguard: {required}",
                      VALIDATOR.quality_contract_errors(mutated, skill, sop))

    def test_quality_guard_accepts_markdown_reflow_and_case(self):
        agents, skill, sop = self.quality_source()
        mutated, count = re.subn(
            "do it right the first time", "DO IT\n  RIGHT THE FIRST TIME", agents, flags=re.IGNORECASE)
        self.assertGreater(count, 0)
        self.assertNotEqual(mutated, agents)
        self.assertEqual(VALIDATOR.quality_contract_errors(mutated, skill, sop), [])

    def test_quality_rule_must_remain_in_the_protected_core(self):
        agents, skill, sop = self.quality_source()
        mutated, count = re.subn(r"^\| `CONST-QUALITY-001` \|.*\n", "", agents, flags=re.MULTILINE)
        self.assertEqual(count, 1)
        self.assertIn("CONST-QUALITY-001 missing protected-core entry",
                      VALIDATOR.quality_contract_errors(mutated, skill, sop))

    def test_quality_rule_ranks_immediately_after_human_authority(self):
        agents, skill, sop = self.quality_source()
        quality_row = ("| `CONST-QUALITY-001` | Quality before speed: correctness and completeness "
                       "outrank speed of output, with no exceptions. | This file |\n")
        resource_row = ("| `CONST-RESOURCEFUL-001` | Technical roadblocks are not hard blocks: "
                        "engineer and verify an authorized workaround. | This file |\n")
        self.assertIn(quality_row + resource_row, agents)
        mutated = agents.replace(quality_row + resource_row, resource_row + quality_row, 1)
        self.assertIn("CONST-QUALITY-001 must rank immediately after CONST-AUTH-001",
                      VALIDATOR.quality_contract_errors(mutated, skill, sop))

    def test_quality_done_and_gate_wiring_cannot_disappear(self):
        agents, skill, sop = self.quality_source()
        without_done = re.sub(
            r"(^## Definition of Done\n.*?)(?=^## |\Z)",
            lambda match: match.group(0).replace("CONST-QUALITY-001", "REMOVED-RULE"),
            agents, count=1, flags=re.MULTILINE | re.DOTALL)
        self.assertNotEqual(without_done, agents)
        self.assertIn("Definition of Done must apply CONST-QUALITY-001",
                      VALIDATOR.quality_contract_errors(without_done, skill, sop))
        without_gate = re.sub(
            r"(^\| 1 \|.*)skipped applicable verification for speed",
            r"\1removed speed failure",
            agents, count=1, flags=re.MULTILINE)
        self.assertNotEqual(without_gate, agents)
        self.assertIn("Section 0 item 1 must fail a delivery that skipped applicable verification for speed",
                      VALIDATOR.quality_contract_errors(without_gate, skill, sop))

    def test_quality_loader_and_sop_routes_cannot_disappear(self):
        agents, skill, sop = self.quality_source()
        for path in ("SKILL.md", "SOP.md"):
            with self.subTest(path=path):
                skill_input = skill.replace("CONST-QUALITY-001", "removed") if path == "SKILL.md" else skill
                sop_input = sop.replace("CONST-QUALITY-001", "removed") if path == "SOP.md" else sop
                self.assertIn(f"{path} must route speed pressure to CONST-QUALITY-001",
                              VALIDATOR.quality_contract_errors(agents, skill_input, sop_input))

    def test_source_validation_calls_the_quality_guard(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "source"
            shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            self.assertEqual(VALIDATOR.validate(target), [])
            path = target / "AGENTS.md"
            agents = path.read_text(encoding="utf-8")
            mutated, count = re.subn(r"^### CONST-QUALITY-001\b.*?(?=^### |^## |\Z)", "", agents,
                                    flags=re.MULTILINE | re.DOTALL)
            self.assertEqual(count, 1)
            path.write_text(mutated, encoding="utf-8")
            errors = VALIDATOR.validate(target)
            self.assertIn("CONST-QUALITY-001 detailed rule missing", errors)
            self.assertIn("protected rule has no detailed definition: CONST-QUALITY-001", errors)

    def test_completeness_rule_requires_a_detailed_core_home(self):
        agents, skill, sop = self.quality_source()
        self.assertEqual(VALIDATOR.completeness_contract_errors(agents, skill, sop), [])
        self.assertEqual(
            VALIDATOR.completeness_contract_errors(
                agents.replace("### CONST-COMPLETE-001", "### Retired rule"), skill, sop),
            ["CONST-COMPLETE-001 detailed rule missing"],
        )

    def test_completeness_slogan_alone_is_not_an_operational_rule(self):
        _agents, skill, sop = self.quality_source()
        slogan = ("### CONST-COMPLETE-001 — Complete, wired units\n\n"
                  "Deliver complete units.\n")
        errors = VALIDATOR.completeness_contract_errors(slogan, skill, sop)
        self.assertIn(
            "CONST-COMPLETE-001 missing operational safeguard: each named item is an independent acceptance unit",
            errors,
        )
        self.assertIn("CONST-COMPLETE-001 missing protected-core entry", errors)

    def test_completeness_rule_guards_named_control_clauses(self):
        agents, skill, sop = self.quality_source()
        for term in (
            "complete, wired, dependency-closed",
            "no placeholders or production todos",
            "each named item is an independent acceptance unit",
            "enumerates named player-facing controls, fields, or surfaces",
            "recorded as an unmet acceptance item",
        ):
            with self.subTest(term=term):
                pattern = r"\s+".join(re.escape(word) for word in term.split())
                mutated, count = re.subn(pattern, "removed safeguard", agents, flags=re.IGNORECASE)
                self.assertGreater(count, 0, "counterexample must change the actual rule")
                self.assertIn(f"CONST-COMPLETE-001 missing operational safeguard: {term}",
                              VALIDATOR.completeness_contract_errors(mutated, skill, sop))

    def test_completeness_done_gate_and_routes_cannot_disappear(self):
        agents, skill, sop = self.quality_source()
        without_done = re.sub(
            r"(^## Definition of Done\n.*?)(?=^## |\Z)",
            lambda match: match.group(0).replace("CONST-COMPLETE-001", "REMOVED-RULE"),
            agents, count=1, flags=re.MULTILINE | re.DOTALL)
        self.assertIn("Definition of Done must apply CONST-COMPLETE-001",
                      VALIDATOR.completeness_contract_errors(without_done, skill, sop))
        without_gate = re.sub(
            r"(^\| 1 \|.*)enumerated named controls under `CONST-COMPLETE-001`",
            r"\1removed named-control check",
            agents, count=1, flags=re.MULTILINE)
        self.assertNotEqual(without_gate, agents)
        self.assertIn("Section 0 item 1 must apply CONST-COMPLETE-001",
                      VALIDATOR.completeness_contract_errors(without_gate, skill, sop))
        for path in ("SKILL.md", "SOP.md"):
            with self.subTest(path=path):
                skill_input = skill.replace("CONST-COMPLETE-001", "removed") if path == "SKILL.md" else skill
                sop_input = sop.replace("CONST-COMPLETE-001", "removed") if path == "SOP.md" else sop
                self.assertIn(
                    f"{path} must route enumerated named controls to CONST-COMPLETE-001",
                    VALIDATOR.completeness_contract_errors(agents, skill_input, sop_input),
                )

    @staticmethod
    def quality_source():
        return tuple((ROOT / path).read_text(encoding="utf-8") for path in ("AGENTS.md", "SKILL.md", "SOP.md"))


if __name__ == "__main__":
    unittest.main()
