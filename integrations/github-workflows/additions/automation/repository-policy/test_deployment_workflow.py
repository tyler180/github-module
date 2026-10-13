"""Exercise the apply condition and executable authorization/preflight gates."""
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
import yaml

SHARED_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = SHARED_ROOT / '.github' / 'workflows' / 'terraform-deploy.yml'
if not WORKFLOW.exists():
    WORKFLOW = SHARED_ROOT.parent / 'updates' / '.github' / 'workflows' / 'terraform-deploy.yml'
POLICY_WORKFLOW = SHARED_ROOT / '.github' / 'workflows' / 'repository-policy.yml'


def load():
    return yaml.load(WORKFLOW.read_text(), Loader=yaml.BaseLoader)


def applies(required, authorization, changes='true', plan='success', cancelled=False):
    # Evaluate the small trusted GitHub expression as a boolean truth table.
    expression = load()['jobs']['apply']['if']
    expression = re.sub(r'needs\.([\w-]+)\.outputs\.([\w-]+)', r"needs['\1']['outputs']['\2']", expression)
    expression = re.sub(r'needs\.([\w-]+)\.result', r"needs['\1']['result']", expression)
    expression = re.sub(r'inputs\.([\w-]+)', r"inputs['\1']", expression)
    expression = expression.replace('&&', ' and ').replace('||', ' or ')
    expression = re.sub(r'!(?!=)', 'not ', expression)
    context = {'inputs': {'repository-policy-required': required},
               'needs': {'plan': {'result': plan, 'outputs': {'changes': changes}},
                         'repository-authorization': {'result': authorization}},
               'always': lambda: True, 'cancelled': lambda: cancelled}
    return eval(expression, {'__builtins__': {}}, context)


class DeploymentTests(unittest.TestCase):
    def test_existing_non_inventory_flow(self):
        self.assertTrue(applies(False, 'skipped'))

    def test_no_changes_never_apply(self):
        for required in (True, False):
            self.assertFalse(applies(required, 'success', changes='false'))

    def test_required_gate_failure_skip_or_cancel_blocks_apply(self):
        for result in ('failure', 'skipped', 'cancelled'):
            with self.subTest(result=result):
                self.assertFalse(applies(True, result))

    def test_failed_plan_and_cancelled_runs_block_apply(self):
        self.assertFalse(applies(True, 'success', plan='failure'))
        self.assertFalse(applies(True, 'success', cancelled=True))

    def test_fixture_authorization_always_fails(self):
        step = load()['jobs']['repository-authorization']['steps'][0]
        self.assertNotEqual(subprocess.run(['bash', '-c', step['run']], capture_output=True).returncode, 0)

    def test_inventory_cannot_disable_policy(self):
        steps = load()['jobs']['plan']['steps']
        step = next(s for s in steps if s.get('name') == 'Require repository policy for inventory roots')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            command = ['bash', '-c', step['run']]
            self.assertEqual(subprocess.run(command, cwd=root, env={'POLICY_REQUIRED': 'false'}, capture_output=True).returncode, 0)
            (root / 'repositories.json').write_text('{}')
            self.assertNotEqual(subprocess.run(command, cwd=root, env={'POLICY_REQUIRED': 'false'}, capture_output=True).returncode, 0)
            self.assertNotEqual(subprocess.run(command, cwd=root, env={'POLICY_REQUIRED': 'true'}, capture_output=True).returncode, 0)
            self.assertEqual(subprocess.run(command, cwd=root, env={'POLICY_REQUIRED': 'true', 'POLICY_REF': 'a'*40, 'BASE_REF': 'b'*40, 'RECORD_REF': 'c'*40}, capture_output=True).returncode, 0)

    def test_policy_is_isolated_and_required_dependency(self):
        jobs = load()['jobs']
        self.assertIn('repository-authorization', jobs['apply']['needs'])
        self.assertEqual(jobs['repository-authorization']['needs'], 'repository-policy')
        self.assertEqual(jobs['repository-policy']['permissions']['id-token'], 'none')
        self.assertEqual(jobs['repository-policy']['uses'], './.github/workflows/repository-policy.yml')
        self.assertNotIn('continue-on-error', jobs['repository-authorization'])
        policy = yaml.load(POLICY_WORKFLOW.read_text(), Loader=yaml.BaseLoader)
        self.assertFalse(any('terraform' in s.get('uses', '') for s in policy['jobs']['policy']['steps']))

    def test_environment_credential_is_confined_to_apply(self):
        workflow = load()
        jobs = workflow['jobs']
        self.assertEqual(jobs['apply']['environment'], '${{ inputs.environment }}')
        self.assertIn('secrets.TF_GITHUB_APPLY_TOKEN', jobs['apply']['env']['GITHUB_TOKEN'])
        self.assertNotIn('TF_GITHUB_APPLY_TOKEN', str(jobs['plan']))
        self.assertIn('TF_GITHUB_APPLY_TOKEN', workflow['on']['workflow_call']['secrets'])

    def test_planning_uses_read_credential(self):
        workflow = load()
        self.assertEqual(workflow['env']['GITHUB_TOKEN'],
                         '${{ secrets.TF_GITHUB_PLAN_TOKEN || secrets.terraform-github-token }}')
        self.assertIn('TF_GITHUB_PLAN_TOKEN', workflow['on']['workflow_call']['secrets'])
        step = next(s for s in workflow['jobs']['plan']['steps']
                    if s.get('name') == 'Require repository planning credential')
        self.assertEqual(step['if'], 'inputs.repository-policy-required')
        result = subprocess.run(['bash', '-c', step['run']], env={'GITHUB_TOKEN': ''}, capture_output=True)
        self.assertNotEqual(result.returncode, 0)

    def test_missing_repository_apply_credential_fails(self):
        step = next(s for s in load()['jobs']['apply']['steps']
                    if s.get('name') == 'Require repository apply credential')
        self.assertEqual(step['if'], 'inputs.repository-policy-required')
        for token, expected in (('', False), ('synthetic-test-value', True)):
            result = subprocess.run(['bash', '-c', step['run']],
                                    env={'GITHUB_TOKEN': token}, capture_output=True)
            self.assertEqual(result.returncode == 0, expected)
            if token:
                self.assertNotIn(token.encode(), result.stdout + result.stderr)

    def test_manual_dispatch_uses_same_gates(self):
        jobs = load()['jobs']
        self.assertIn('workflow_dispatch', jobs['plan']['if'])
        self.assertNotIn('event_name', jobs['apply']['if'])


if __name__ == '__main__':
    unittest.main()
