# Pending live acceptance

Every item below is PENDING. Offline fixtures do not satisfy it.

| Area | Acceptance |
|---|---|
| Account | Confirm owner type, private-repo rulesets, review availability, Actions/shared-repo access, and billing limits |
| Core | Private creation, initial commit/default branch, second no-change plan, no unintended defaults |
| Adoption | Matching imports of repository and every owned subordinate resource, full no-change plan before new defaults |
| Access | Effective inherited permissions, restricted bootstrap claim, provisioner identity, intended grant and unauthorized denial |
| Workflow | Eligible successful PR run, deliberate failure/cancellation/skip cases, observed context, fork-safe behavior |
| Hooks | Actual pinned pre-commit installation and identical hygiene failures in CI |
| Caller protection | CODEOWNERS patterns/owner access; dummy-job, CODEOWNERS deletion, and configuration-bypass PRs blocked pending review |
| Protection | Direct-push/force-push/deletion rejection, stale approval invalidation, compliant PR merge, narrow admin trust |
| Lifecycle | Optional omission/import/update/removal/handoff/reimport; unrelated updates preserve unmanaged settings |
| Provenance | Real source observations, initial/merged commits, tree comparison, exact-source alternative |
| Recovery | Partial apply/state loss/retry, unchanged accepted stage, fresh complete plan and safe bootstrap PR resume |
| Deployment | Trusted live collector; exact binary/JSON/snapshot origin; protected record writer; mandatory gates on manual/rerun paths |
| State | Selected remote locking/encryption/access, recovery, unique state ownership, existing shared workflow OIDC/roles |
| Upgrade | Pins/config renewed evidence, post-merge verification, check overlap without protection/access gap |

Live pilot decisions: owner/account plan, root location (review github-infra before
choosing), Go toolchain/repository, actual reviewer/provisioner/developer identities,
template vs exact-source need, backend/state identity, GitHub credential minting,
protected environment, record storage/writer, observation freshness and policy
promotion. None blocks credential-free local coding/fixtures.

No live deployment caller/backend/credentials are provided. Do not enable the
existing deployment workflow for this root until required protections and trusted
gates are integrated. It can apply immediately if its environment is unprotected.
Never run apply merely to test a pipeline.

Codex review remains optional advisory follow-on: decide authentication, budget,
allowed code/diff access, retention, who requests reviews, and failure/rate-limit
handling. Advisory outages cannot replace or satisfy deterministic validation.
