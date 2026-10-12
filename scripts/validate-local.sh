#!/usr/bin/env bash
# Offline/provider-mocked checks only. Never runs apply or a credentialed plan.
set -euo pipefail
cd "$(dirname "$0")/.."
export GITHUB_TOKEN='' GH_TOKEN='' AWS_ACCESS_KEY_ID='' AWS_SECRET_ACCESS_KEY='' AWS_SESSION_TOKEN=''
export AWS_EC2_METADATA_DISABLED=true
terraform fmt -check -recursive
terraform init -backend=false -input=false
terraform validate -no-color
terraform test -no-color
for directory in examples/minimal examples/adoption examples/template examples/consuming-root; do
  terraform -chdir="$directory" init -backend=false -input=false
  terraform -chdir="$directory" validate -no-color
done
terraform -chdir=examples/consuming-root test -no-color
for suite in test_policy test_receipt test_hygiene; do
  python3 -I "integrations/github-workflows/additions/automation/repository-policy/$suite.py"
done
python3 -I tests/test_template.py
if command -v actionlint >/dev/null 2>&1; then
  actionlint integrations/github-workflows/additions/.github/workflows/*.yml
else
  echo "actionlint is required for complete workflow validation" >&2
  exit 1
fi
