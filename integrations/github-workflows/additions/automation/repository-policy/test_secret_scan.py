"""Real pinned scanner tests with synthetic tokens in disposable repositories."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCANNER = Path(__file__).resolve().parents[2] / 'hooks' / 'secret_scan.py'
TOKEN = 'ghp_' + 'aB3dE5fG7hI9jK1lM2nO4pQ6rS8tU0vW3xY5'


class SecretScanTests(unittest.TestCase):
    def run_scan(self, contents, staged=False, suppress=False, remove=False):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args):
                return subprocess.run(['git', '-C', directory, *args], check=True, capture_output=True)
            git('init', '-q')
            git('config', 'user.name', 'Fixture')
            git('config', 'user.email', 'fixture@example.invalid')
            (root / 'settings.txt').write_text(contents)
            if suppress:
                (root / '.gitleaks.toml').write_text('[allowlist]\npaths = [".*"]\n')
            git('add', '.')
            if not staged:
                git('commit', '-qm', 'Fixture')
                if remove:
                    (root / 'settings.txt').write_text('clean\n');git('add', '.');git('commit', '-qm', 'Remove fixture')
            result = subprocess.run(['python3', '-I', str(SCANNER), *(['--staged'] if staged else []), directory], capture_output=True, text=True)
            self.assertNotIn(TOKEN, result.stdout + result.stderr)
            return result.returncode

    def test_clean_history(self):
        self.assertEqual(self.run_scan('documented configuration\n'), 0)

    def test_secret_in_staged_content(self):
        self.assertEqual(self.run_scan('token = "' + TOKEN + '"\n', staged=True), 1)

    def test_removed_secret_still_detected_in_history(self):
        self.assertEqual(self.run_scan('token = "' + TOKEN + '"\n', remove=True), 1)

    def test_candidate_suppressions_cannot_disable_rules(self):
        self.assertEqual(self.run_scan('token = "' + TOKEN + '" # gitleaks:allow\n', suppress=True), 1)


if __name__ == '__main__':
    unittest.main()
