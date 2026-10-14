import subprocess
import shutil
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

    def test_complete_go_starter_with_release_refs(self):
        args = self.args.copy()
        args[args.index("--workflow-sha") + 1] = "v2.2.0-rc.1"
        args[args.index("--hook-sha") + 1] = "v2.2.0-rc.1"
        result = self.run_renderer(["--go-version", "1.26.5", "--go-module", "github.com/fixture-owner/pilot"], args)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("module github.com/fixture-owner/pilot", (self.destination / "go.mod").read_text())
        for name in ("main.go", "main_test.go", "scripts/validate.sh", "scripts/setup.sh", "Makefile", "BOOTSTRAP.md"):
            self.assertTrue((self.destination / name).is_file(), name)
        self.assertTrue((self.destination / "scripts/validate.sh").stat().st_mode & 0o111)
        self.assertTrue((self.destination / "scripts/setup.sh").stat().st_mode & 0o111)
        self.assertIn("setup:", (self.destination / "Makefile").read_text())
        self.assertIn("/.venv/", (self.destination / ".gitignore").read_text())
        hooks = (self.destination / ".pre-commit-config.yaml").read_text()
        self.assertIn("secret-scan-setup", hooks)
        self.assertEqual(hooks.count("id: go-validation"), 1)
        self.assertFalse((self.destination / "terraform").exists())
        self.assertEqual((self.destination / ".github/CODEOWNERS").read_text(), "* @fixture-owner/platform\n")
        self.assertFalse(any(p.name.endswith(".in") for p in self.destination.rglob("*")))

    def test_rejects_go_module_injection(self):
        result = self.run_renderer(["--go-version", "1.26.5", "--go-module", "example.com/pilot\ngo 1.0"])
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.destination.exists())

    def test_renderer_excludes_local_developer_environment(self):
        source = Path(self.temp.name) / "source"
        (source / "scripts").mkdir(parents=True)
        shutil.copy(ROOT / "scripts/render-template.py", source / "scripts/render-template.py")
        shutil.copytree(ROOT / "templates", source / "templates")
        shutil.copytree(ROOT / "examples/go-pilot", source / "examples/go-pilot",
                        ignore=shutil.ignore_patterns(".venv", ".terraform", "__pycache__"))
        environment = source / "examples/go-pilot/.venv"
        environment.mkdir()
        (environment / "local-only.txt").write_text("must not be bootstrapped")
        args = self.args.copy()
        args[2] = str(source / "scripts/render-template.py")
        result = self.run_renderer(["--go-version", "1.26.5"], args)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.destination / ".venv").exists())

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

    def test_go_terraform_starter_is_disabled_and_manual(self):
        result = self.run_renderer(["--go-version", "1.26.5", "--terraform-version", "1.15.0",
                                    "--terraform-workflow-ref", "c" * 40])
        self.assertEqual(result.returncode, 0, result.stderr)
        ci = (self.destination / ".github/workflows/ci.yml").read_text()
        self.assertIn("go-validate.yml", ci)
        deploy = (self.destination / ".github/workflows/terraform-deploy.yml").read_text()
        self.assertIn("workflow_dispatch:", deploy)
        self.assertNotIn("  push:", deploy)
        self.assertIn("vars.TERRAFORM_DEPLOY_ENABLED == 'true'", deploy)
        self.assertIn("@" + "c" * 40, deploy)
        self.assertNotIn("{{TERRAFORM_", deploy)
        self.assertIn("*.tfstate", (self.destination / ".gitignore").read_text())

    def test_terraform_release_version_is_preserved(self):
        result = self.run_renderer(["--workflows-only", "--terraform-version", "1.15.0",
                                    "--terraform-workflow-ref", "v2.3.0-rc.3"])
        self.assertEqual(result.returncode, 0, result.stderr)
        for name in ("terraform-plan.yml", "terraform-deploy.yml"):
            self.assertIn("@v2.3.0-rc.3", (self.destination / ".github/workflows" / name).read_text())

    def test_workflows_only_does_not_copy_application_or_go_ci(self):
        args = [sys.executable, "-I", str(ROOT / "scripts/render-template.py"),
                "--destination", str(self.destination), "--workflows-only",
                "--terraform-version", "1.15.0", "--terraform-workflow-ref", "c" * 40]
        result = self.run_renderer(args=args)
        self.assertEqual(result.returncode, 0, result.stderr)
        files = {str(p.relative_to(self.destination)) for p in self.destination.rglob("*") if p.is_file()}
        self.assertEqual(files, {".github/workflows/terraform-plan.yml", ".github/workflows/terraform-deploy.yml", "TERRAFORM-STARTER.md"})
        plan = (self.destination / ".github/workflows/terraform-plan.yml").read_text()
        self.assertIn("vars.TERRAFORM_ENABLED == 'true'", plan)
        self.assertIn("github.event.pull_request.head.repo.full_name == github.repository", plan)
        self.assertNotIn("paths:", plan)

    def test_terraform_rejects_unsafe_configuration_without_writes(self):
        for field, value in [("--terraform-version", "latest"), ("--terraform-workflow-ref", "main"), ("--terraform-workflow-ref", "v2"),
                             ("--terraform-directory", "../terraform"), ("--terraform-directory", "terraform\nfoo")]:
            args = ["--workflows-only", "--terraform-version", "1.15.0", "--terraform-workflow-ref", "c" * 40]
            if field in args:
                args[args.index(field) + 1] = value
            else:
                args.extend([field, value])
            with self.subTest(field=field, value=value):
                self.assertNotEqual(self.run_renderer(args).returncode, 0)
                self.assertFalse(self.destination.exists())

    def test_workflows_only_refuses_existing_destination(self):
        self.destination.mkdir()
        sentinel = self.destination / "main.go"
        sentinel.write_text("existing application")
        result = self.run_renderer(["--workflows-only", "--terraform-version", "1.15.0", "--terraform-workflow-ref", "c" * 40])
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(sentinel.read_text(), "existing application")
        self.assertFalse((self.destination / ".github").exists())


if __name__ == "__main__":
    unittest.main()
