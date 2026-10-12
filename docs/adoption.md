# Existing repository adoption

Adoption is part of repository core, not a new-repository creation attempt.
`examples/adoption` has no account defaults. Its `existing` object must match the
current description, homepage, topics, visibility, merge methods, merged-branch
deletion, auto-merge/update-branch settings, archive state, and features. Set
initialization to none. Unexposed ignored fields remain externally owned.

The example import block imports only github_repository. It does not recursively
import subordinate resources. The optional `components` object forwards selected
default_branch, team_permissions, actions_policy, workflow_permissions, and
repository_ruleset configurations through the module's typed validation.

Before credentialed adoption:

1. Inventory remote settings, grants, default branch, branch protections/rulesets,
   inherited permissions, Actions restrictions, and installed Apps.
2. Match all owned settings; preserve external protections.
3. Import repository by name. Import every selected subordinate resource using
   its stable module address and documented provider ID syntax.
4. Obtain a complete no-change plan before proposing any new defaults.
5. Create an accepted identity/stage baseline only after observation and review.
6. Add missing source files via a reviewed PR; never overwrite during adoption.

Future import address patterns (examples, not commands executed):

| Address under module.repository | Provider import ID |
|---|---|
| github_repository.this | repository name |
| github_branch_default.this["managed"] | repository name |
| github_team_repository.this["TEAM_ID_OR_SLUG"] | team ID/name:repository |
| github_actions_repository_permissions.this["managed"] | repository name |
| github_workflow_repository_permissions.this["managed"] | repository name |
| github_repository_ruleset.this["managed"] | repository:ruleset ID |

The ordinary onboarding policy rejects imports, reconstruction, and drift. Adopt
using this separately reviewed procedure; do not fabricate a create-stage record
for an already configured repository. Advanced rename/protection migration and
archival rehearsals are follow-on work. All live import/no-change acceptance is
pending. Provider-mocked intent tests do not prove import behavior.

References: [repository import](https://registry.terraform.io/providers/integrations/github/6.13.0/docs/resources/repository),
[team association import](https://registry.terraform.io/providers/integrations/github/6.13.0/docs/resources/team_repository),
[ruleset import](https://registry.terraform.io/providers/integrations/github/6.13.0/docs/resources/repository_ruleset).
