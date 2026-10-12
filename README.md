# GitHub repository module — local v1

One repository per module. Terraform owns settings and explicitly selected
components; templates initialize source files, and reviewed PRs maintain them.
Organization policy, credentials, backend selection, and onboarding history stay
in the consuming root. No deployment or release has been enabled.

## Contents

- Root: repository, default branch, non-authoritative team grants, optional Actions
  permissions/token defaults, and default-branch ruleset.
- `examples/minimal`, `examples/template`, `examples/adoption`: consuming examples.
- `examples/consuming-root`: empty inventory, structural stage guards, no backend.
- `templates/generic`: one materializable generic template source.
- `examples/go-pilot`: the single language pilot caller.
- `integrations/github-workflows`: staged shared additions and reviewable patch.
- `tests`: provider-mocked, **plan-only** Terraform tests.
- `docs`: contracts, ADRs, verification status, adoption, upgrades, and live checklist.

## Local verification

Terraform >= 1.7 (< 2), Python >= 3.10, and actionlint are needed. The local test
host has Terraform 1.15.8. Provider baseline is integrations/github 6.13.0.

Run `bash scripts/validate-local.sh`. It never runs `terraform apply` or a
credentialed plan. Provider/module downloads need network access. All supplied
Terraform tests use `command = plan` and a mock provider. Do not add unmocked
provider tests to this credential-free suite.

See [verification status](docs/verification.md): local policy and workflow checks
passed; provider RPC execution is blocked by this session's sandbox, so Terraform
validation and mocked-test execution are not claimed successful.

## Usage

Configure the root provider owner explicitly; provide runtime credentials only
for a separately authorized integration. Use `examples/minimal` for basic private
creation and `examples/adoption` to match/import existing configuration. Defaults
are owned settings, **not** preservation behavior.

The module intentionally does not manage files, organization membership/policy,
secret values, environments, backend configuration, webhooks, deployments,
advanced security licensing, push rulesets, merge queues, or Codex review.

## Inputs

| Input | Default / ownership |
|---|---|
| `name` | Required, managed |
| `description`, `homepage_url` | Empty, managed; omission clears |
| `topics` | Empty complete managed set |
| `visibility` | Private, managed |
| `initialization` | Basic, immutable creation intent; none for adoption |
| `template` | Null; owner/repository selection, default branch only, no ref |
| `merge_methods` | Squash only, managed |
| `delete_branch_on_merge` | True, managed |
| `allow_auto_merge`, `allow_update_branch` | False / true, managed; match explicitly during adoption |
| `features` | Issues true; discussions/wiki/projects false, managed |
| `archived` | False, managed; retirement requires separate procedure |
| `default_branch`, `rename_default_branch` | Null / false; optional branch ownership |
| `team_permissions` | Empty map; existing IDs/slugs to built-in provider roles |
| `actions_policy` | Null initially unmanaged; explicit enabled/allowlist/SHA policy when enabled |
| `workflow_permissions` | Null initially unmanaged; both token/review-approval settings explicit |
| `repository_ruleset` | Null initially unmanaged; branch target only, disabled/active, explicit checks |

Outputs: `name`, `full_name`, `repository_id`, `node_id`, `html_url`, clone URLs,
optional `managed_ruleset_id`, and `managed_components`. None attests readiness.

Read [ownership](docs/ownership.md) before changing an optional component to null.

## Shared automation

Reuse `github-workflows` and its existing Terraform plan/deploy contract. Its
credentialed workflows are unchanged; validation is a separate reusable workflow.
The sibling checkout is outside this session's writable roots, so additions are
staged here with a patch instead of claiming they were applied there.

No caller is installed or enabled in `.github/workflows` in github-module.
Template `.in` files require actual reviewed pins and reviewer identities. The
Go caller also requires an explicit toolchain version.

## Safety and trust

Module validation/preconditions block malformed intent. Trusted failing policy
steps compare an accepted base inventory/record, candidate inventory, independently
supplied observations, and the complete plan. There are no mandatory check blocks.
The delivered policy adapter is fixture-only and receipts always say
`deployment_authorized: false`. Implement and approve the live collector and
deployment gates before using any receipt for a live integration.

See [onboarding](docs/onboarding.md), [trusted policy boundary](docs/policy.md),
[upgrades](docs/upgrades.md), and [pending live acceptance](docs/live-acceptance.md).
