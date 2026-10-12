from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "tools" / "check-adoption.py"
spec = importlib.util.spec_from_file_location("wpai_adoption", SOURCE)
assert spec and spec.loader
ADOPTION = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ADOPTION)


class AdoptionCheckTests(unittest.TestCase):
    def make_repo(self, root: Path) -> None:
        subprocess.run(["git", "init", "-q", str(root)], check=True)

    def test_accepts_canonical_url_without_confusing_old_repo_slug_with_skill(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_repo(root)
            (root / "AGENTS.md").write_text(
                "Canonical: https://github.com/MrWizard94-Compile/Agents-Constitution\n"
                "Use wpai-constitution from a pinned SHA.\n", encoding="utf-8",
            )
            subprocess.run(["git", "-C", str(root), "add", "AGENTS.md"], check=True)
            self.assertEqual(ADOPTION.inspect(root), [])

    def test_detects_old_pack_and_ci_consumer(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_repo(root)
            old_pack = root / "AGENTS Constitution"
            old_pack.mkdir()
            (old_pack / "AGENTS.md").write_text("old law", encoding="utf-8")
            workflow = root / ".github" / "workflows" / "ci.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text('run: pwsh -File "AGENTS Constitution/tools/verify-pack.ps1"\n', encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
            codes = [code for code, _, _ in ADOPTION.inspect(root)]
            self.assertIn("OLD_PACK_DIRECTORY", codes)
            self.assertIn("LEGACY_REFERENCE", codes)

    def test_detects_untracked_full_soul_without_following_links(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_repo(root)
            (root / "SOUL.md").write_text(
                "# SOUL.md — The Constitution of an AI Empire\n## 40. Constitutional Integrity\n",
                encoding="utf-8",
            )
            codes = [code for code, _, _ in ADOPTION.inspect(root)]
            self.assertIn("FULL_SOUL_COPY", codes)

    def test_empty_retired_directory_is_not_shadow_law(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_repo(root)
            (root / "AGENTS Constitution" / "docs" / "migration").mkdir(parents=True)
            self.assertEqual(ADOPTION.inspect(root), [])

    def test_detects_legacy_storage_sent_to_runtime_prompt(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_repo(root)
            source = root / "src" / "chat.ts"
            source.parent.mkdir()
            source.write_text(
                "const soul = localStorage.getItem('soul_config');\n"
                "const systemPrompt = `Bound by this constitution: ${soul}`;\n"
                "engine.chat.completions.create({messages: [{role: 'system', content: systemPrompt}]});\n",
                encoding="utf-8",
            )
            findings = ADOPTION.inspect(root)
            self.assertIn(("ACTIVE_LEGACY_PROMPT", "src/chat.ts", 1), findings)

    def test_allows_explicit_historical_recovery_and_inert_legacy_export(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_repo(root)
            (root / "README.md").write_text(
                "Historical recovery (not active law): `git show " + "a" * 40 + ":public/SOULv2.0.0.md`\n",
                encoding="utf-8",
            )
            source = root / "src" / "persona.ts"
            source.parent.mkdir()
            source.write_text("export const legacyDraft = localStorage.getItem('soul_config');\n", encoding="utf-8")
            self.assertEqual(ADOPTION.inspect(root), [])

    def test_requires_literal_commit_pin_for_canonical_workflow_checkout(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_repo(root)
            workflow = root / ".github" / "workflows" / "ci.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text(
                "jobs:\n  verify:\n    steps:\n"
                "      - uses: actions/checkout@v4\n"
                "        with:\n          repository: MrWizard94-Compile/Agents-Constitution\n"
                "          ref: main\n"
                "      - uses: actions/checkout@v4\n"
                "        with:\n          ref: " + "a" * 40 + "\n",
                encoding="utf-8",
            )
            self.assertIn(("UNPINNED_CANONICAL_CHECKOUT", ".github/workflows/ci.yml", 6), ADOPTION.inspect(root))
            workflow.write_text(workflow.read_text(encoding="utf-8").replace("          ref: main\n", ""), encoding="utf-8")
            self.assertIn(("UNPINNED_CANONICAL_CHECKOUT", ".github/workflows/ci.yml", 6), ADOPTION.inspect(root))
            workflow.write_text(workflow.read_text(encoding="utf-8").replace("          repository: MrWizard94-Compile/Agents-Constitution\n", "          repository: MrWizard94-Compile/Agents-Constitution\n          ref: ${{ env.CONSTITUTION_REF }}\n"), encoding="utf-8")
            self.assertIn(("UNPINNED_CANONICAL_CHECKOUT", ".github/workflows/ci.yml", 6), ADOPTION.inspect(root))
            workflow.write_text(workflow.read_text(encoding="utf-8").replace("ref: ${{ env.CONSTITUTION_REF }}", "ref: " + "b" * 40), encoding="utf-8")
            self.assertEqual(ADOPTION.inspect(root), [])

    def test_detects_floating_canonical_raw_url_only_in_workflows(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_repo(root)
            url = "https://raw.githubusercontent.com/MrWizard94-Compile/Agents-Constitution/main/SKILL.md"
            (root / "README.md").write_text(url + "\n", encoding="utf-8")
            workflow = root / ".github" / "workflows" / "ci.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text("run: curl " + url + "\n", encoding="utf-8")
            self.assertEqual(ADOPTION.inspect(root), [("FLOATING_CANONICAL_URL", ".github/workflows/ci.yml", 1)])


if __name__ == "__main__":
    unittest.main()
