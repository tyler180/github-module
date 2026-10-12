# Root onboarding stages

The empty `examples/consuming-root/repositories.json` is safe scaffolding, not a
configured account. Copy the root into the selected configuration repository,
replace the local module source with a reviewed release/commit later, and supply
the real owner explicitly. No backend or enabled deployment caller is included.

Inventory schema 1 uses stable keys and repository fields documented in README.
Stage values are create, bootstrap, verify, protect, and grant (developer access).
Provisioning and developer teams are separate disjoint maps. Tooling records carry
actual workflow/hook pins and validation-configuration digests when onboarding.
`tests/*.json` entries are fictional offline fixtures, not pilot configuration.

| Stage | Operation | Required advancement evidence |
|---|---|---|
| create | Repository/settings, provisioner grants, disabled baseline ruleset | Repository identity, initial commit, effective access |
| bootstrap | Reviewed PR materializes repository-owned files | Source/destination commits, bootstrap PR/commit, pins |
| verify | Eligible deterministic PR checks and negative validation | Actual check contexts, successful run and failing test |
| protect | Activate same ruleset and required checks | Effective rules, push/review/check negative tests |
| grant | Add developer grants | Previously accepted protect stage plus fresh protection recheck |

Each transition is a reviewed root change. The complete root is planned; no routine
targeting, module key change, or Terraform provisioner advances stages. Desired
stage is intent only. terraform_data.contract has failing preconditions for
schema/stage, configured checks, and team classification. Historical enforcement
lives in trusted policy code, never Terraform check blocks.

Accepted record schema 1 has configuration_sha, inventory_digest, and repositories.
Each repository record has repository_id, name, stage, and tooling_digest. These
bind the last accepted base inventory to the last successful deployment, not
merely the current default branch. Restricted record writing/storage is a live
integration decision; no successful record is created by this implementation.

PR policy uses a reviewed base revision; deployment must use the accepted record's
configuration revision. Validate both before deployment so merged but unapplied
transitions cannot be treated as completed. Ordinary transitions allow same stage
or exactly one forward stage; new entries start at create. Baseline rules remain
present. Backtracking, removal, and retirement use separate reviewed procedures.

After partial failure, keep the accepted stage unchanged, inspect Terraform state
and GitHub, import a successfully created but unrecorded object if necessary, and
generate a fresh complete plan. Locate/resume the existing bootstrap PR. Do not
repeat template creation, replace the repository, force-unlock state, or reuse a
partially applied plan. Evidence/grant failures fail closed.

Inherited organization base/parent-team/collaborator/App access can defeat the
restricted bootstrap window. Inspect effective access before making that claim.
Use appropriate none/read base permissions or explicitly accept an unrestricted
window with existing baseline controls. Changing organization policy is outside
the module. Disabled rulesets can still require a paid plan for private repos;
local scaffolding/tests do not imply the account supports them.
