from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.inventory_copies import inspect_file, scan


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


if __name__ == "__main__":
    unittest.main()
