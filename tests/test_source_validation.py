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


if __name__ == "__main__":
    unittest.main()
