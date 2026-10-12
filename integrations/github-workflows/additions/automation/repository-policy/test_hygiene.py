import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("hygiene", Path(__file__).resolve().parents[2] / "hooks" / "repository_hygiene.py")
hygiene = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hygiene)


class HookTests(unittest.TestCase):
    def test_clean_file(self):
        self.assertEqual(hygiene.violations("clean\n"), [])

    def test_bad_file(self):
        self.assertEqual(len(hygiene.violations("bad \n<<<<<<< branch\n=======\n>>>>>>> branch\n")), 4)

    def test_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.txt"
            path.write_text("bad \n")
            self.assertEqual(hygiene.main([str(path)]), 1)
            self.assertEqual(path.read_text(), "bad \n")

    def test_patch_context_is_not_source_whitespace(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "review.patch"
            path.write_text(" \n")
            self.assertEqual(hygiene.main([str(path)]), 0)


if __name__ == "__main__":
    unittest.main()
