# Upgrades after access handoff

Keep stage=grant, existing protections, and developer access. Workflow/hook pins
and validation configuration change through CODEOWNER-reviewed PRs. Run current
required validation with the proposed tooling, observe negative cases, verify the
merged commit, then accept renewed evidence. Do not reset onboarding or disable
rules to make an upgrade mergeable.

Evidence binds repository ID, content commit, workflow/hook revisions, validation
configuration digest, required-check contract, policy revision, run IDs, and UTC
observation time. Current fixture adapter uses a conservative 24-hour freshness
window; live freshness policy is an explicit pilot decision. Changes to any bound
tooling/configuration/check/protection assumption, missing or failed runs, policy
invalidation, or expiry make evidence stale. Unrelated source changes still need
current PR CI but need not invalidate the tooling contract itself.

Required-check migration:

1. Ship tooling reporting old and new contexts, both reflecting real validation.
2. Demonstrate positive/negative results for both contexts on eligible PR runs.
3. Add the new requirement while retaining old enforcement.
4. Verify effective protection; preserve overlap in accepted evidence.
5. Remove old requirement through reviewed root change.
6. Remove old compatibility context afterward.

No permanently successful compatibility aliases. If overlap cannot be implemented,
retain a stable aggregate check name. Root policy refuses removing all prior
contexts in one step. Actual emitted contexts can include caller/reusable job
names; live observation is mandatory.

## Caller protection

Generic CODEOWNERS protects all .github files (including itself), hook config,
tests/scripts, Go module manifests, Terraform files/lockfiles, inventory/evidence,
and validation configuration. Confirm effective patterns and actual owner access;
later matching lines can override earlier entries. Require code-owner review and
dismiss stale approvals. CODEOWNERS from the base branch protects a PR deleting it.

Live dummy-substitution test: replace real validation with a successful job using
the observed required context; also try changing CODEOWNERS/validation settings.
The check may pass; merging must remain blocked without the required owner review.
Reviewers must reject the bypass. Administrators/bypass actors remain trusted.
If approved local callers must not be able to substitute validation, add centrally
required workflows with centrally constrained validation after plan entitlement is
verified. Status context/integration identity is not workflow implementation proof.

Module releases, workflows, and hooks are independently versioned. No releases
are published locally. Root lockfiles pin providers and module source must be
pinned before rollout. Internal resource address changes need moved blocks.
