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


if __name__ == "__main__":
    unittest.main()
