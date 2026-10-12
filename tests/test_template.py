import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TemplateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.destination = Path(self.temp.name) / "starter"
        self.args = [sys.executable, "-I", str(ROOT / "scripts/render-template.py"),
                     "--destination", str(self.destination), "--code-owner", "fixture-owner/platform",
                     "--workflow-sha", "a"*40, "--hook-sha", "b"*40]

    def run_renderer(self, extra=None, args=None):
        return subprocess.run((args or self.args) + (extra or []), capture_output=True, text=True, check=False)

    def test_generic_has_pins_and_protects_codeowners(self):
        self.assertEqual(self.run_renderer().returncode, 0)
        ci = (self.destination / ".github/workflows/ci.yml").read_text()
        self.assertIn("@" + "a"*40, ci)
        self.assertIn("b"*40, (self.destination / ".pre-commit-config.yaml").read_text())
        self.assertIn("/.github/ @fixture-owner/platform", (self.destination / ".github/CODEOWNERS").read_text())
        self.assertFalse(any("{{" in p.read_text() for p in self.destination.rglob("*") if p.is_file()))

    def test_go_pilot(self):
        self.assertEqual(self.run_renderer(["--go-version", "1.25.0"]).returncode, 0)
        ci = (self.destination / ".github/workflows/ci.yml").read_text()
        self.assertIn("go-validate.yml@" + "a"*40, ci)
        self.assertIn("go-version: '1.25.0'", ci)

    def test_refuses_overwrite(self):
        self.destination.mkdir()
        sentinel = self.destination / "existing"
        sentinel.write_text("preserve")
        self.assertNotEqual(self.run_renderer().returncode, 0)
        self.assertEqual(sentinel.read_text(), "preserve")

    def test_requires_full_pin(self):
        args = self.args.copy()
        args[args.index("--workflow-sha")+1] = "main"
        self.assertNotEqual(self.run_renderer(args=args).returncode, 0)
        self.assertFalse(self.destination.exists())

    def test_rejects_owner_injection(self):
        args = self.args.copy()
        args[args.index("--code-owner")+1] = "owner\n* @other"
        self.assertNotEqual(self.run_renderer(args=args).returncode, 0)

    def test_requires_explicit_go_version(self):
        self.assertNotEqual(self.run_renderer(["--go-version", "stable"]).returncode, 0)


if __name__ == "__main__":
    unittest.main()
