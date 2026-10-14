from __future__ import annotations

import contextlib
import importlib.util
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "tools" / "check-frozen-load.py"
spec = importlib.util.spec_from_file_location("wpai_frozen_load", SOURCE)
assert spec and spec.loader
FROZEN = importlib.util.module_from_spec(spec)
spec.loader.exec_module(FROZEN)

IDENTITY = ("-c", "user.name=test", "-c", "user.email=test@example.invalid", "-c", "commit.gpgsign=false")


def run_git(root: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(root), *IDENTITY, *args], check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return done.stdout.strip()


def skill_text(version: str) -> str:
    return f'---\nname: wpai-constitution\nmetadata:\n  skill-version: "{version}"\n---\n# body\n'


class FrozenLoadTests(unittest.TestCase):
    def make_repo(self, base: Path, version: str = "6.6.1", listed: tuple[str, ...] = ("SKILL.md", "AGENTS.md")) -> tuple[Path, str]:
        root = base / "checkout"
        root.mkdir()
        run_git(root, "init", "-q")
        (root / "SKILL.md").write_bytes(skill_text(version).encode())
        (root / "AGENTS.md").write_bytes(b"binding law\n")
        manifest = ", ".join(f'"{name}"' for name in listed)
        (root / "SOURCE.json").write_text(
            f'{{"skill_version": "{version}", "mirror_files": [{manifest}]}}\n', encoding="utf-8")
        run_git(root, "add", "-A")
        run_git(root, "commit", "-q", "-m", "frozen")
        return root, run_git(root, "rev-parse", "HEAD")

    def test_version_comparison_is_numeric_not_textual(self):
        self.assertEqual(FROZEN.compare_loader("6.5.0", "6.6.1"), "stale")
        self.assertEqual(FROZEN.compare_loader("6.6.1", "6.6.1"), "match")
        self.assertEqual(FROZEN.compare_loader("6.10.0", "6.9.0"), "ahead")
        self.assertEqual(FROZEN.compare_loader("6.9.0", "6.10.0"), "stale")
        self.assertEqual(FROZEN.compare_loader(None, "6.6.1"), "unknown")
        self.assertEqual(FROZEN.compare_loader("six", "6.6.1"), "unknown")

    def test_loader_version_reads_quoted_and_bare_headers(self):
        self.assertEqual(FROZEN.loader_version(skill_text("6.5.0")), "6.5.0")
        self.assertEqual(FROZEN.loader_version("metadata:\n  skill-version: 6.7.0\n"), "6.7.0")
        self.assertIsNone(FROZEN.loader_version("name: wpai-constitution\n"))

    def test_clean_checkout_of_frozen_sha_passes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, sha = self.make_repo(Path(temporary))
            self.assertEqual(FROZEN.verify_checkout(root, sha), [])

    def test_rejects_short_sha_branch_name_and_other_head(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, sha = self.make_repo(Path(temporary))
            self.assertIn("full lowercase 40-hex", FROZEN.verify_checkout(root, sha[:12])[0])
            self.assertIn("full lowercase 40-hex", FROZEN.verify_checkout(root, "main")[0])
            (root / "later.md").write_text("later\n", encoding="utf-8")
            run_git(root, "add", "-A")
            run_git(root, "commit", "-q", "-m", "later")
            self.assertIn("not frozen revision", FROZEN.verify_checkout(root, sha)[0])

    def test_rejects_modified_tracked_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, sha = self.make_repo(Path(temporary))
            (root / "AGENTS.md").write_bytes(b"binding law, quietly paraphrased\n")
            errors = FROZEN.verify_checkout(root, sha)
            self.assertTrue(any("tracked files differ" in error for error in errors), errors)
            self.assertTrue(any("bytes differ" in error and "AGENTS.md" in error for error in errors), errors)

    def test_hash_check_catches_change_that_git_status_hides(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, sha = self.make_repo(Path(temporary))
            run_git(root, "update-index", "--skip-worktree", "AGENTS.md")
            (root / "AGENTS.md").write_bytes(b"binding law, truncated")
            self.assertEqual(run_git(root, "status", "--porcelain", "--untracked-files=no"), "")
            errors = FROZEN.verify_checkout(root, sha)
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("bytes differ from the frozen revision: AGENTS.md", errors[0])

    def test_rejects_binding_file_missing_from_revision_and_unsafe_paths(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, sha = self.make_repo(Path(temporary), listed=("SKILL.md", "law/ABSENT.md", "../escape.md"))
            errors = FROZEN.verify_checkout(root, sha)
            self.assertIn("binding file absent from frozen revision: law/ABSENT.md", errors)
            self.assertIn("unsafe mirror_files path: '../escape.md'", errors)

    def test_rejects_directory_that_is_not_a_checkout(self):
        with tempfile.TemporaryDirectory() as temporary:
            self.assertIn("not a Git checkout", FROZEN.verify_checkout(Path(temporary), "a" * 40)[0])

    def test_cli_reports_stale_loader_without_failing_integrity(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, sha = self.make_repo(Path(temporary), version="6.6.1")
            loader = Path(temporary) / "running-SKILL.md"
            loader.write_text(skill_text("6.5.0"), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = FROZEN.main(["--sha", sha, "--root", str(root), "--loader", str(loader)])
            self.assertEqual(code, 0)
            self.assertIn("PASS:", output.getvalue())
            self.assertIn("STALE LOADER: running skill-version 6.5.0, frozen law 6.6.1", output.getvalue())

    def test_cli_matching_loader_and_failure_exit_codes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, sha = self.make_repo(Path(temporary), version="6.6.1")
            loader = Path(temporary) / "running-SKILL.md"
            loader.write_text(skill_text("6.6.1"), encoding="utf-8")
            command = [sys.executable, str(SOURCE), "--sha", sha, "--root", str(root), "--loader", str(loader)]
            matched = subprocess.run(command, stdout=subprocess.PIPE, text=True)
            self.assertEqual(matched.returncode, 0)
            self.assertIn("matches frozen law", matched.stdout)
            (root / "AGENTS.md").write_bytes(b"tampered\n")
            failed = subprocess.run(command, stdout=subprocess.PIPE, text=True)
            self.assertEqual(failed.returncode, 1)
            self.assertIn("FAIL:", failed.stdout)
            self.assertNotIn("LOADER", failed.stdout)


if __name__ == "__main__":
    unittest.main()
