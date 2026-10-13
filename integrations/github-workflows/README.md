# github-workflows local integration

The sibling checkout now contains the shared additions and deployment-gate
integration. additions/ retains shared new files; updates/ retains the modified
terraform-deploy.yml. local-additions.patch installs both against the committed
pre-integration baseline and appends the documentation addendum. It is intended
for a checkout without these local changes, not reapplication over the updated
sibling. baseline-sha256.json identifies the original baseline bytes.

Repository policy executes separately from candidate Terraform. The connected
authorization gate deliberately rejects fixture-only deployment; independent
live collection, protected record storage/writing, and fresh pre-apply rechecks
remain necessary. No deployment has been enabled or remotely executed.

Shared hygiene now includes checksum-pinned Gitleaks 8.30.1. The generic hook
configuration includes staged secret detection. Tests require Gitleaks 8.30.1,
PyYAML 6.0.3, Python 3.10+, Terraform and actionlint. See ../../docs/security-scanning.md
and ../../docs/deployment-gates.md for scope and remaining integration.
