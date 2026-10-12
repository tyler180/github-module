# Ownership and lifecycle

## Meaning of omission

An omitted module input with a default remains managed. Provider attribute
omission is not ownership release: optional/noncomputed attributes may acquire
defaults or reset, while optional/computed attributes may retain observed values.
An initially omitted resource is unmanaged. Removing a managed resource normally
invokes deletion/reset. Unmanaged does not imply organization inheritance; verify
effective settings separately.

All exposed repository attributes are continuously owned, except creation intent.
`auto_init` and `template` are ignored after creation. The consuming policy forbids
changing initialization intent; the module does not attempt a template upgrade.

The literal ignore list covers unexposed external fields: security_and_analysis,
allow_forking, Pages, deprecated default_branch, vulnerability_alerts, is_template,
web_commit_signoff_required, and merge/squash message/title settings. Separate
github_branch_default owns branch selection only when configured. Ignore lists
protect planning; provider-wide update payload behavior still needs live testing.

`has_downloads` is a deprecated provider field with no useful v1 API ownership.
Provider creation defaults for unexposed fields are not preservation guarantees.
New repositories need inspection of effective configuration before handoff.

## Optional components

| Component | Initially absent | Ordinary removal |
|---|---|---|
| Default branch | No selection/rename resource | Provider-specific relinquishment; use explicit handoff for consistency |
| Team grant | No grant; other access can still exist | Removes that association |
| Actions permissions | No local owner | Provider requests enabled=true and allowed_actions=all |
| Workflow permissions | No local owner | Provider requests read defaults and PR approval=false |
| Ruleset | No local owner; other rules may exist | Deletes that ruleset |

The consuming root keeps its baseline ruleset present (disabled before protect,
active afterward), retaining its stable address. Baseline root policy has no bypass
actors and developer grants are limited to pull/triage/push. The reusable module
can model explicit provisioning/admin grants and narrowly specified bypasses.

For enabled optional objects, configure the entire supported object. Removing
individual fields is not an ownership mechanism. All ruleset review fields have
documented managed defaults in variables.tf.

## Handoff

Unmanaged -> managed: inventory, match values, import each resource, obtain a
no-change plan, then propose changed defaults separately.

Managed -> unmanaged preserving remote configuration: retain an inventory/state
backup, explicitly remove management without destruction, then remove configuration
and validate remote settings and subsequent unrelated updates. Terraform removed
blocks with `destroy = false` are preferred where their addressing scope fits;
selective map instances may need a reviewed state-rm operation. No handoff command
has been executed. Do not remove a resource block first and assume preservation.

Per-attribute ownership switches are not supported in v1. A tested migration must
change a literal ownership contract, or relinquish the entire resource. Do not
duplicate github_repository resources or parameterize lifecycle ignore lists.

`prevent_destroy = true` is literal for the repository; it disappears if its
configuration is removed. Root plan policy also rejects delete/replacement,
visibility changes, archival, ruleset weakening, drift, and component deletion.
archive_on_destroy is a fallback, not a safe general destroy procedure.

## Verification

Mock plans assert omission and explicit configuration. Policy fixtures reject
deletion/reset/security relaxation. Live handoff tests must demonstrate initial
omission, matching import, intended update, ordinary removal behavior, explicit
preserve-and-release, unrelated updates after handoff, and no-change reimport.
All remote preservation tests are pending.

Sources: [provider repository code](https://github.com/integrations/terraform-provider-github/blob/v6.13.0/github/resource_github_repository.go),
[Actions deletion](https://github.com/integrations/terraform-provider-github/blob/v6.13.0/github/resource_github_actions_repository_permissions.go),
[workflow permissions deletion](https://github.com/integrations/terraform-provider-github/blob/v6.13.0/github/resource_github_workflow_repository_permissions.go),
[Terraform management removal](https://developer.hashicorp.com/terraform/language/block/removed).
