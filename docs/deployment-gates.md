# Deployment gates and pilot acceptance recovery

The workflow code lives in tyler180/github-workflows. It is not published or
activated by this local change. A gate is a required Actions job that must succeed
before Terraform apply is eligible to run; an environment approval cannot bypass it.

The shared terraform-deploy.yml now accepts repository-policy-required (default
false for existing non-inventory consumers), trusted-policy-ref, approved-base-ref,
and accepted-record-ref. A working directory containing repositories.json rejects
policy-disabled execution before assuming cloud credentials. Required policy also
requires full immutable policy/base/record revisions before planning.

The planning job exports the saved plan, its JSON, and an archive of source at the
triggering SHA. A separate policy runner evaluates that data without Terraform or
cloud/OIDC write permission. The apply job depends on a separate authorization job
as well as successful planning. Failure, skip, cancellation, or no-change plans do
not run a repository apply. Manual dispatch uses the same path.

**Live repository apply remains deliberately blocked.** Observations are currently
empty fixture inputs and receipts cannot authorize deployment. The authorization
job exits nonzero even if offline evaluation succeeds. There is no boolean override
or environment-approval bypass for fixture-only authorization. Existing ordinary
Terraform consumers without repository inventories retain their original flow.

## Remaining integration required before enabling repository apply

1. Choose a pilot repository and consuming configuration root.
2. Store accepted records in a protected source separate from candidate writes.
   The current policy workflow reads onboarding/accepted.json from an explicitly
   pinned accepted-record revision in the caller's configuration repository.
3. Independently collect fresh GitHub check, protection, access, and commit facts.
   Negative-test evidence must be reviewed and tied to actual test identities/runs.
4. Independently verify source snapshots and JSON/saved-plan relationships. The
   candidate planning job's claimed hashes are not sufficient authorization.
5. Implement a live authorizer that binds exact artifacts, policy, source and
   accepted record, then rechecks record/evidence freshness after environment
   approval and immediately before apply. Reruns must repeat those gates.
6. Verify post-apply effective protections and only then advance the accepted
   record using a restricted writer. Partial applies never advance it.
7. Run disposable live acceptance tests before replacing the explicit block.

Do not delete the authorization block merely to make the workflow pass. These
remaining items depend on deployment/storage/identity choices; local fixture tests
cannot establish live protection. No live credentials, applies, pushes, releases,
or remote configuration changes are authorized by the local integration.

## Credential wiring and selected record storage

The reusable deployment accepts TF_GITHUB_PLAN_TOKEN for read-only planning and
TF_GITHUB_APPLY_TOKEN for the environment-bound apply job. Missing credentials
fail repository deployments. Existing secret input names remain compatible.
The caller must pass the same secret names explicitly; production resolves its
environment token only inside the apply job. Use TF_AWS_APPLY_ROLE_ARN as the
caller value for apply-role-arn. Credentials never bypass repository authorization.

The user selected s3://749rmw-tf-backends/github/github-infra/onboarding/ for
accepted records. This selection is not proof of storage access isolation. The
shared github-deploy role is trusted by several repositories; its S3 state access
does not establish an exclusive record writer. A restricted writer and conditional
record updates must be verified before these records can be trusted. No record
has been written and no live authorizer has been enabled by this credential change.

The local plan adapter now accepts omitted rulesets before protect/grant, matching
the personal-account pilot. Protect/grant still require a validated active ruleset.
Regression tests cover both cases.

## Create-stage live adapter (local implementation)

repository-create-deploy.yml is a separate, manually dispatched workflow for the
personal-account pilot. The original offline deployment block remains intact.
It supports create-stage inventories only: no team grants, optional Actions policy
changes, bootstrap, verification, protection, or grant transitions are authorized.

The production job independently decodes the same-run saved binary plan with
fixed official provider versions, evaluates the inventory contract, checks main
freshness and environment protections, and reads the S3 accepted record. It
binds configuration bytes, plan bytes, plan JSON and accepted-record ETag.
After Terraform initialization it rechecks those bindings before applying the
saved plan. After apply succeeds, it reads GitHub settings/IDs and conditionally
writes accepted.json using If-Match or initial If-None-Match. Failures do not
advance the record. Partial apply requires explicit recovery; it cannot silently
adopt unrecorded repositories on rerun.

The caller uses the same immutable release version for workflow and trusted-policy-ref.
The release resolver checks published immutability and exact tag/checkout agreement;
receipts bind both version and resolved commit. The tag-support update is reviewable
in github-workflows PR #5; github-infra PR #4 uses v2.1.0-rc.2 and module v0.1.0-rc.2.

The access preflight is a separate reviewable github-infra PR. It uses production
approval to test OIDC and S3 prefix access, retaining a uniquely named probe.
It does not run Terraform or mutate GitHub. Token read success is not proof of
repository creation permissions. Actual live tests remain pending publication
on main, dispatch and environment approval.

## Completed pilot apply and pending acceptance

Run 38320705436 successfully applied configuration
1064d83772acb9c345dc5a0156ec63a4a7b081b1: three resources added, no changes or
destruction. GitHub and persisted Terraform state both identify the private
github-module-pilot repository as 1416221483. Final settings verification failed,
so accepted.json remains absent. Current settings match the original inventory
under an administrator API response; the original read-token response is unavailable.

v2.1.0-rc.4 uses the production credential for post-apply reads and adds missing
field diagnostics. Its separate acceptance-only recovery is restricted to that
reviewed run, original immutable workflow revision, source and repository ID.
It verifies successful authorization/apply job steps, exact root state ownership,
current live settings and environment protections before conditionally creating
the initial accepted record. It never runs Terraform or overwrites existing
accepted history. Recovery still requires publication of the caller and production
approval. Do not rerun ordinary deployment until recovery succeeds.
