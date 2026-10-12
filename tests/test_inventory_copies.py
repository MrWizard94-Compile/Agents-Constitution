from __future__ import annotations

import tempfile
import unittest
import json
import os
from pathlib import Path
from unittest.mock import patch

from tools import inventory_copies
from tools.inventory_copies import inspect_file, scan, scan_resumable, write_report


class InventoryCopiesTests(unittest.TestCase):
    def test_detects_content_signature_in_renamed_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "unrelated-name.md"
            candidate.write_text("Binding rule CONST-GATE-001 applies.", encoding="utf-8")
            hit = inspect_file(candidate, 1024)
            self.assertIsNotNone(hit)
            assert hit is not None
            self.assertIn("content", hit.reasons)
            self.assertIn("const-gate-001", hit.markers)

    def test_detects_path_candidate_even_for_binary_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "SOULv2" / "archive.bin"
            candidate.parent.mkdir()
            candidate.write_bytes(b"\x00\x01\x02")
            hit = inspect_file(candidate, 1024)
            self.assertIsNotNone(hit)
            assert hit is not None
            self.assertEqual(("path",), hit.reasons)

    def test_scan_does_not_follow_directory_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            real = root / "real"
            real.mkdir()
            (real / "AGENTS.md").write_text("ordinary project instructions", encoding="utf-8")
            link = root / "loop"
            try:
                link.symlink_to(root, target_is_directory=True)
            except OSError:
                self.skipTest("directory symlinks are unavailable")
            hits, errors, examined = scan([root], 1024)
            self.assertEqual(1, examined)
            self.assertEqual(1, len(hits))
            self.assertEqual([], errors)

    def test_interrupted_scan_resumes_without_partial_final_report_or_duplicate_hits(self) -> None:
        with tempfile.TemporaryDirectory() as root_dir, tempfile.TemporaryDirectory() as audit_dir:
            root = Path(root_dir)
            (root / "first").mkdir()
            (root / "second").mkdir()
            (root / "first" / "AGENTS.md").write_text("project notes", encoding="utf-8")
            (root / "second" / "copy.md").write_text("CONST-GATE-001", encoding="utf-8")
            output = Path(audit_dir) / "inventory.json"
            checkpoint = Path(audit_dir) / "inventory.checkpoint.json"
            original = inventory_copies.inspect_directory
            calls = 0

            def interrupt_once(directory: Path, max_bytes: int, excluded_files: frozenset[str]):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise KeyboardInterrupt
                return original(directory, max_bytes, excluded_files)

            with patch.object(inventory_copies, "inspect_directory", side_effect=interrupt_once):
                with self.assertRaises(KeyboardInterrupt):
                    scan_resumable([root], 1024, output, checkpoint, resume=False, checkpoint_directories=1)
            self.assertFalse(output.exists())
            partial = json.loads(checkpoint.read_text(encoding="utf-8"))
            self.assertEqual("partial", partial["status"])
            self.assertTrue(partial["pending_directories"])

            hits, errors, examined = scan_resumable(
                [root], 1024, output, checkpoint, resume=True, checkpoint_directories=1,
            )
            expected_hits, expected_errors, expected_examined = scan([root], 1024)
            self.assertEqual(expected_hits, sorted(hits, key=lambda hit: hit.path.casefold()))
            self.assertEqual(expected_errors, errors)
            self.assertEqual(expected_examined, examined)
            write_report(output, [root], hits, errors, examined)
            final = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual("complete", final["status"])
            self.assertEqual(2, final["hit_count"])

    def test_resume_rejects_changed_scan_parameters_and_escaped_frontier(self) -> None:
        with tempfile.TemporaryDirectory() as root_dir, tempfile.TemporaryDirectory() as audit_dir:
            root = Path(root_dir)
            output = Path(audit_dir) / "inventory.json"
            checkpoint = Path(audit_dir) / "inventory.checkpoint.json"
            scan_resumable([root], 1024, output, checkpoint, resume=False, checkpoint_directories=1)
            with self.assertRaisesRegex(ValueError, "max_text_bytes"):
                scan_resumable([root], 2048, output, checkpoint, resume=True)
            payload = json.loads(checkpoint.read_text(encoding="utf-8"))
            payload["status"] = "partial"
            payload["pending_directories"] = [str(Path(audit_dir))]
            checkpoint.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "outside scan roots"):
                scan_resumable([root], 1024, output, checkpoint, resume=True)

    def test_resume_accepts_a_frontier_on_another_windows_drive(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            first = base / "first"
            second = base / "second"
            first.mkdir()
            second.mkdir()
            output = base / "inventory.json"
            checkpoint = base / "inventory.checkpoint.json"
            progress = inventory_copies._fresh_progress([first, second], 1024, output)
            checkpoint.write_text(json.dumps(progress), encoding="utf-8")
            original_commonpath = os.path.commonpath
            normalized_first = os.path.normcase(os.path.realpath(first))

            def distinct_drives(paths: tuple[str, str]) -> str:
                if paths[1] == normalized_first and paths[0] != normalized_first:
                    raise ValueError("Paths don't have the same drive")
                return original_commonpath(paths)

            with patch.object(inventory_copies.os.path, "commonpath", side_effect=distinct_drives):
                hits, errors, examined = scan_resumable(
                    [first, second], 1024, output, checkpoint, resume=True,
                    checkpoint_directories=1,
                )
            self.assertEqual([], hits)
            self.assertEqual([], errors)
            self.assertEqual(0, examined)
            final_checkpoint = json.loads(checkpoint.read_text(encoding="utf-8"))
            self.assertEqual("complete", final_checkpoint["status"])

    def test_resume_rejects_a_frontier_through_a_parent_link(self) -> None:
        with tempfile.TemporaryDirectory() as root_dir, tempfile.TemporaryDirectory() as outside_dir:
            root = Path(root_dir)
            outside = Path(outside_dir)
            (outside / "child").mkdir()
            link = root / "link"
            try:
                link.symlink_to(outside, target_is_directory=True)
            except OSError:
                self.skipTest("directory symlinks are unavailable")
            output = root / "inventory.json"
            checkpoint = root / "inventory.checkpoint.json"
            progress = inventory_copies._fresh_progress([root], 1024, output)
            progress["pending_directories"] = [str(link / "child")]
            checkpoint.write_text(json.dumps(progress), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "outside scan roots"):
                scan_resumable([root], 1024, output, checkpoint, resume=True)

    def test_overlapping_roots_are_rejected_before_checkpoint(self) -> None:
        with tempfile.TemporaryDirectory() as root_dir, tempfile.TemporaryDirectory() as audit_dir:
            root = Path(root_dir)
            child = root / "child"
            child.mkdir()
            output = Path(audit_dir) / "inventory.json"
            checkpoint = Path(audit_dir) / "inventory.checkpoint.json"
            with self.assertRaisesRegex(ValueError, "overlap"):
                scan_resumable([root, child], 1024, output, checkpoint, resume=False)
            self.assertFalse(checkpoint.exists())

    def test_scanner_excludes_its_own_checkpoint_inside_scanned_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("project notes", encoding="utf-8")
            output = root / "WPAI Constitution" / "inventory.json"
            checkpoint = Path(str(output) + ".checkpoint.json")
            hits, errors, examined = scan_resumable(
                [root], 1024, output, checkpoint, resume=False, checkpoint_directories=1,
            )
            self.assertEqual(1, examined)
            self.assertEqual(1, len(hits))
            self.assertEqual([], errors)
            self.assertEqual("AGENTS.md", Path(hits[0].path).name)


if __name__ == "__main__":
    unittest.main()
