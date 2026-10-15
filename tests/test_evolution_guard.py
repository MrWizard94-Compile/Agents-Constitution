from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SOURCE = Path(__file__).resolve().parents[1] / "tools" / "evolution-guard.py"
spec = importlib.util.spec_from_file_location("wpai_evolution_guard", SOURCE)
assert spec and spec.loader
GUARD = importlib.util.module_from_spec(spec)
spec.loader.exec_module(GUARD)


class EvolutionGuardTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.git("init", "-q")
        self.write("VERSION", "1.0.0\n")
        self.write("evolution/LEDGER.md", "# Ledger\n")
        self.write("AGENTS.md", "# Law\n\n**Version:** 1.0.0\n\nKeep evidence.\n")
        self.write("SKILL.md", '---\nname: fixture\nmetadata:\n  skill-version: "1.0.0"\n---\nRead law.\n')
        self.write("SOURCE.json", '{"skill_version": "1.0.0", "mirror_files": ["AGENTS.md"]}\n')
        self.write("tools/sample.py", "if enabled:\n    run()\nfinish()\n")
        self.base = self.commit()
        self.addCleanup(patch.stopall)
        patch.object(GUARD, "ROOT", self.root).start()

    def git(self, *args: str) -> str:
        done = subprocess.run(
            ["git", "-c", "user.name=test", "-c", "user.email=test@example.invalid",
             "-c", "commit.gpgsign=false", "-c", "core.autocrlf=false", *args],
            cwd=self.root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8",
        )
        return done.stdout.strip()

    def write(self, path: str, content: str):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="")

    def commit(self) -> str:
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "fixture")
        return self.git("rev-parse", "HEAD")

    def release_metadata(self):
        self.write("VERSION", "1.0.1\n")
        self.write("evolution/LEDGER.md", "# Ledger\n\nA claimed improvement.\n")

    def run_guard(self, expected: int, base: str | None = None) -> str:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = GUARD.main(["--base", base or self.base])
        self.assertEqual(result, expected, output.getvalue())
        return output.getvalue()

    def test_agents_version_only_is_not_evolution(self):
        self.release_metadata()
        self.write("AGENTS.md", "# Law\n\n**Version:** 1.0.1\n\nKeep evidence.\n")
        self.commit()
        self.run_guard(1)

    def test_synchronized_release_versions_are_not_evolution(self):
        self.release_metadata()
        for path in ("AGENTS.md", "SKILL.md", "SOURCE.json"):
            self.write(path, (self.root / path).read_text(encoding="utf-8").replace("1.0.0", "1.0.1"))
        self.write("CHANGELOG.md", "# Changelog\n\n1.0.1\n")
        self.commit()
        self.run_guard(1)

    def test_each_known_version_surface_is_ignored_independently(self):
        cases = {
            "AGENTS.md": b"# Law\n\n**Version:** 1.0.0\n",
            "SOP.md": b"# Process\n\n**Version:** 1.0.0\n",
            "governance/EVOLUTION.md": b"# Evolution\n\n**Version:** 1.0.0\n",
            "SKILL.md": b'---\nmetadata:\n  skill-version: "1.0.0"\n---\nBody\n',
            "SOURCE.json": b'{"skill_version": "1.0.0", "schema": 2}',
        }
        for path, before in cases.items():
            for content in (before, before.replace(b"\n", b"\r\n")):
                with self.subTest(path=path, crlf=b"\r" in content):
                    self.assertEqual(GUARD.normalized_content(path, content),
                                     GUARD.normalized_content(path, content.replace(b"1.0.0", b"1.0.1")))

    def test_source_json_formatting_and_version_only_fail(self):
        self.release_metadata()
        self.write("SOURCE.json", json.dumps({"mirror_files": ["AGENTS.md"], "skill_version": "1.0.1"}, indent=2))
        self.commit()
        self.run_guard(1)

    def test_source_manifest_change_remains_a_candidate(self):
        self.release_metadata()
        self.write("SOURCE.json", '{"skill_version": "1.0.1", "mirror_files": ["AGENTS.md", "SKILL.md"]}\n')
        self.commit()
        self.assertIn("- SOURCE.json", self.run_guard(0))

    def test_skill_body_change_remains_a_candidate(self):
        self.release_metadata()
        self.write("SKILL.md", (self.root / "SKILL.md").read_text(encoding="utf-8")
                   .replace("1.0.0", "1.0.1").replace("Read law.", "Read law and verify evidence."))
        self.commit()
        self.assertIn("- SKILL.md", self.run_guard(0))

    def test_semantic_whitespace_and_version_literals_are_preserved(self):
        cases = [
            ("AGENTS.md", b"# Rule\n\nKeep 1.0.0 compatibility.\n", b"# Rule\n\nKeep 1.0.1 compatibility.\n"),
            ("AGENTS.md", b"- First\n  - Nested\n", b"- First\n- Nested\n"),
            ("tools/sample.py", b"if enabled:\n    run()\nfinish()\n", b"if enabled:\n    run()\n    finish()\n"),
            ("SKILL.md", b'---\nname: skill\n---\n  skill-version: "1.0.0"\n',
             b'---\nname: skill\n---\n  skill-version: "1.0.1"\n'),
        ]
        for path, before, after in cases:
            with self.subTest(path=path):
                self.assertNotEqual(GUARD.normalized_content(path, before), GUARD.normalized_content(path, after))

    def test_python_indentation_change_passes_with_review_qualification(self):
        self.release_metadata()
        self.write("tools/sample.py", "if enabled:\n    run()\n    finish()\n")
        self.commit()
        output = self.run_guard(0)
        self.assertIn("semantic usefulness still requires review", output)
        self.assertNotIn("contains substantive source changes", output)

    def test_workflow_only_change_does_not_expand_existing_contract(self):
        self.release_metadata()
        self.write(".github/workflows/validate.yml", "name: Improved check\njobs: {}\n")
        self.commit()
        self.run_guard(1)

    def test_exact_rename_alone_is_not_evolution(self):
        self.release_metadata()
        self.git("mv", "tools/sample.py", "tools/renamed.py")
        self.commit()
        self.run_guard(1)

    def test_new_source_and_deleted_source_are_candidates(self):
        self.release_metadata()
        self.write("tools/new file.py", "print('verify')\n")
        self.commit()
        self.assertIn("- tools/new file.py", self.run_guard(0))
        deletion_base = self.git("rev-parse", "HEAD")
        self.write("VERSION", "1.0.2\n")
        self.write("evolution/LEDGER.md", "# Ledger\n\nRetire obsolete code.\n")
        self.git("rm", "tools/new file.py")
        self.commit()
        self.assertIn("- tools/new file.py", self.run_guard(0, deletion_base))

    def test_no_committed_change_and_missing_required_metadata_fail(self):
        self.run_guard(1)
        self.write("tools/sample.py", "run()\n")
        self.run_guard(1)
        self.commit()
        self.assertIn("must bump VERSION", self.run_guard(1))
        self.write("VERSION", "1.0.1\n")
        self.commit()
        self.assertIn("update evolution/LEDGER.md", self.run_guard(1))

    def test_version_must_increase_numerically(self):
        self.release_metadata()
        self.write("VERSION", "1.0.0 \n")
        self.write("tools/sample.py", "run()\n")
        self.commit()
        self.assertIn("VERSION must increase", self.run_guard(1))
        self.write("VERSION", "1.0.10\n")
        self.commit()
        self.run_guard(0)

    def test_invalid_base_or_malformed_manifest_fails_closed(self):
        self.run_guard(2, "missing-ref")
        self.release_metadata()
        self.write("SOURCE.json", "not JSON\n")
        self.commit()
        self.run_guard(2)
        self.write("SOURCE.json", '{"skill_version": "1.0.1", "schema": 1, "schema": 2}\n')
        self.commit()
        self.assertIn("duplicate object key", self.run_guard(2))

    def test_base_branch_drift_uses_merge_base_content(self):
        self.git("checkout", "-q", "-b", "upstream")
        self.write("AGENTS.md", "# Upstream law\n")
        upstream = self.commit()
        self.git("checkout", "-q", "-b", "proposal", self.base)
        self.release_metadata()
        self.write("AGENTS.md", "# Law\n\n**Version:** 1.0.1\n\nKeep evidence.\n")
        self.commit()
        self.run_guard(1, upstream)

    def test_cli_checks_real_commits(self):
        self.release_metadata()
        self.write("AGENTS.md", "# Law\n\n**Version:** 1.0.1\n\nKeep evidence.\n")
        self.commit()
        self.write("tools/evolution-guard.py", SOURCE.read_text(encoding="utf-8"))
        result = subprocess.run([sys.executable, str(self.root / "tools/evolution-guard.py"), "--base", self.base],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("no source-content change", result.stdout)


if __name__ == "__main__":
    unittest.main()
