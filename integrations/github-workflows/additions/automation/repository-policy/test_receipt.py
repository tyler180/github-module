import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("verify", HERE / "verify_receipt.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)
spec = importlib.util.spec_from_file_location("fixtures", HERE / "test_policy.py")
fixtures = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixtures)


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = self.root / "candidate"
        self.config.mkdir()
        self.now = datetime.now(timezone.utc)
        base, record, candidate, evidence, plan = fixtures.fixture()
        evidence["repositories"]["pilot"]["observed_at"] = self.now.isoformat()
        for name, value in (("base", base), ("record", record), ("evidence", evidence), ("plan", plan)):
            (self.root / (name + ".json")).write_text(json.dumps(value))
        (self.config / "repositories.json").write_text(json.dumps(candidate))
        (self.config / "main.tf").write_text("# Offline fixture snapshot\n")
        self.saved = self.root / "saved.tfplan"
        self.saved.write_bytes(b"OFFLINE FIXTURE: not a Terraform saved plan")
        self.plan = self.root / "plan.json"
        self.receipt = self.root / "receipt.json"
        self.args = [sys.executable, "-I", str(HERE / "policy.py"),
                     "--base", str(self.root / "base.json"),
                     "--record", str(self.root / "record.json"),
                     "--candidate", str(self.config / "repositories.json"),
                     "--evidence", str(self.root / "evidence.json"),
                     "--plan-json", str(self.plan), "--saved-plan", str(self.saved),
                     "--configuration", str(self.config), "--receipt", str(self.receipt),
                     "--configuration-sha", "a"*40, "--policy-sha", "b"*40, "--base-sha", "1"*40]
        self.run_policy()

    def run_policy(self):
        result = subprocess.run(self.args, cwd=self.config, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)

    def check_binding(self, receipt=None):
        receipt = receipt or json.loads(self.receipt.read_text())
        trusted_inputs = {key: json.loads((self.root / (filename + ".json")).read_text()) for key, filename in (("base", "base"), ("record", "record"), ("evidence", "evidence"), ("plan-json", "plan"))}
        trusted_inputs["candidate"] = json.loads((self.config / "repositories.json").read_text())
        verify.verify(receipt, self.config, self.saved, self.plan, HERE / "policy.py", self.now + timedelta(seconds=1), trusted_inputs, "a"*40, "b"*40, "1"*40)

    def test_exact_binding(self):
        self.check_binding()
        self.assertIs(json.loads(self.receipt.read_text())["deployment_authorized"], False)

    def test_configuration_substitution(self):
        (self.config / "main.tf").write_text("different")
        with self.assertRaises(ValueError):
            self.check_binding()

    def test_saved_plan_substitution(self):
        self.saved.write_bytes(b"other plan")
        with self.assertRaises(ValueError):
            self.check_binding()

    def test_json_plan_substitution(self):
        self.plan.write_text("{}")
        with self.assertRaises(ValueError):
            self.check_binding()

    def test_cannot_authorize_deployment(self):
        receipt = json.loads(self.receipt.read_text())
        receipt["deployment_authorized"] = True
        with self.assertRaises(ValueError):
            self.check_binding(receipt)

    def test_expired_receipt(self):
        receipt = json.loads(self.receipt.read_text())
        receipt["evaluated_at"] = (self.now - timedelta(hours=25)).isoformat()
        with self.assertRaises(ValueError):
            self.check_binding(receipt)

    def test_new_deployment_record_invalidates_rerun(self):
        path = self.root / "record.json"
        record = json.loads(path.read_text())
        record["repositories"]["pilot"]["stage"] = "grant"
        path.write_text(json.dumps(record))
        with self.assertRaises(ValueError):
            self.check_binding()

    def test_new_evidence_invalidates_receipt(self):
        path = self.root / "evidence.json"
        evidence = json.loads(path.read_text())
        evidence["repositories"]["pilot"]["checks"][0]["conclusion"] = "failure"
        path.write_text(json.dumps(evidence))
        with self.assertRaises(ValueError):
            self.check_binding()

    def test_candidate_python_never_executes(self):
        sentinel = self.root / "executed"
        (self.config / "policy.py").write_text(f"open({str(sentinel)!r}, 'w').write('executed')")
        (self.config / "json.py").write_text(f"open({str(sentinel)!r}, 'w').write('executed')")
        # Isolation excludes the cwd and PYTHONPATH from trusted imports.
        result = subprocess.run(self.args, cwd=self.config,
                                env={**os.environ, "PYTHONPATH": str(self.config)},
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(sentinel.exists())

    def test_failure_has_nonzero_exit_and_no_new_receipt(self):
        bad = json.loads((self.root / "evidence.json").read_text())
        bad["repositories"] = {}
        (self.root / "evidence.json").write_text(json.dumps(bad))
        self.receipt.unlink()
        result = subprocess.run(self.args, capture_output=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.receipt.exists())


if __name__ == "__main__":
    unittest.main()
