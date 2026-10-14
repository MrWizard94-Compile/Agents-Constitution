from __future__ import annotations

import importlib.util
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


if __name__ == "__main__":
    unittest.main()
