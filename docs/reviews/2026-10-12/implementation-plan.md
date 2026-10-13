# Phased platform implementation plan

Planning proposal; read with architecture-review.md and proposed-adrs.md.


Owners below are proposed roles, not assignments to named people. No phase authorizes execution by itself.

| Phase | Dependencies and owners | Deliverables and measurable exit criteria | Recovery and rollback |
|---|---|---|---|
| **0. Evidence and design baseline** | None. Platform lead, security, repository owners | Reconcile inventory/docs; identify published versus local versions; approve ADRs; classify every readiness claim. Exit: no contradictory operational claim and every production blocker has an owner. | Preserve historical claims; return unresolved decisions to review without deploying. |
| **1. Organization and authority foundation** | Phase 0. Security/IAM and platform operations | Capability matrix, effective-access baseline, protected environments, scoped plan/apply/record roles, single state ownership. Exit: independently verified approval and denied unauthorized credential/record access in a sandbox. | Disable dispatch or credential minting; revoke sandbox credentials; retain audit evidence. |
| **2. Canonical validation and schema** | Phase 0; Phase 1 needed before privileged tests. Developer platform | Strict inventory schema; full workflow lint/test scope; local parity commands; protected nested paths; authoritative tooling source. Exit: all intended profiles and malformed inputs covered; required aggregates fail on failure/cancel/skip; no unexplained copy drift. | Keep consumers on prior approved pins; revert tooling through reviewed PR. |
| **3. Trusted create and bootstrap** | Phases 1–2. Provisioning and repository owner | Organization-capable create adapter, exact-plan bindings, constrained record publisher, exact-source bootstrap PR service. Exit: disposable organization repository created/accepted, second no-change plan, provenance reproduced, retry does not recreate or overwrite. | Preserve partial resources/state; constrained reconciliation; archive disposable repository only through approved procedure. |
| **4. Live verify/protect/grant** | Phase 3. Assurance collector, security, developer platform | Live evidence collection and stage-specific authorization; chosen central validation boundary; effective-rule/access observations. Exit: direct push/force push/deletion denied; stale reviews invalidated; dummy bypass resisted; failure/cancel/skip/fork cases exercised; grant occurs only after accepted protection. | Keep developer access withheld; retain baseline rules; fix and collect fresh evidence. |
| **5. Adoption and lifecycle operations** | Phase 4. Platform operations and repository owners | Adoption/handoff/rename/retirement runbooks and authorizers. Exit: representative existing repository imported with no-change plan; handoff preserved remote policy; partial-apply and acceptance-write failures recovered without duplicate creation. | Restore management from reviewed backups where necessary; preserve history; never reuse consumed plans. |
| **6. Upgrade governance and canary rollout** | Phases 4–5. Release owner and security | Compatibility manifest, automated update PRs, canary cohorts, check-overlap procedure, release provenance. Exit: one successful and one failed upgrade rehearsal; previous approved version restored without protection/access gaps. | Stop rollout; use prior approved immutable pins or compatibility release; retain required checks. |
| **7. Production onboarding and operations** | All previous phases. Platform service owner | Support model, SLOs, audit retention, drift reporting, incident playbooks, controlled expansion. Exit: organization acceptance signed off; agreed observation period has no unexplained drift, unauthorized grant, or unresolved recovery. | Stop new onboarding; preserve existing protections; recover affected repositories individually. |

### Recovery principles across phases

- Terraform state and accepted history are distinct; reconcile both.
- Never delete accepted history to make deployment pass.
- Never force-unlock without proving the lock is orphaned.
- Never recreate a repository to repair missing acceptance.
- Never reuse a plan after partial application.
- Never reset a granted repository to an earlier stage for an upgrade.
- Treat S3 conditional-write conflicts as reconciliation events.
- Restore state only through reviewed lineage/serial-aware recovery.
- Keep record history append-only or versioned with auditable publication.
- Rollback must preserve or strengthen the security baseline.

## 14. Shared automation upgrade governance

`github-workflows` serves existing consumers beyond this provisioning platform (`../github-workflows/README.md`, `TERRAFORM.md`). Security changes must therefore be evaluated for both provisioning and ordinary release/deployment consumers.

Recommended governance:

1. Declare authoritative automation and policy sources.
2. Protect workflows, helpers, tests, scanner rules, and release configuration.
3. Require security review for credential, event, artifact, approval, or policy-selection changes.
4. Publish compatibility metadata for module, root schema, policy, workflows, hooks, Terraform, and providers.
5. Promote policy independently through trusted configuration; candidate-selected immutable refs are not automatically approved refs.
6. Canary shared changes before broad consumer updates.
7. Update caller workflow and tooling revisions consistently.
8. Migrate checks with genuine old/new overlap.
9. Recollect evidence bound to changed tooling/configuration.
10. Preserve an approved rollback version and publish compatibility fixes when old checks would otherwise deadlock rollback.

Immutable release tags can be used only after their immutability and resolved commits are verified. SHA pins are appropriate where action policy demands them. The current resolver verifies workflow releases; it does not by itself establish module-release governance or approval.

## 15. Explicit open decisions

Before implementation, resolve:

1. **Production organization and plan:** Which account, visibility types, required-workflow capabilities, and private approval features?
2. **Validation authority:** Central required workflow, independent check issuer, or accepted reviewer-based residual trust?
3. **Credential model:** GitHub App capabilities, any necessary PAT exception, scopes, rotation, and minting owner?
4. **Approval separation:** Required reviewers, self-review prevention, administrator bypass, break-glass process?
5. **State partitioning:** Organization-wide root or bounded partitions; unique ownership and concurrency registry?
6. **Record authority:** Restricted publisher architecture, storage versioning, retention, and recovery authorization?
7. **Evidence lifetime:** Separate freshness limits for plan authorization, protection, access, and tooling?
8. **Pre-protection rulesets:** Disabled stable resource or omission, based on verified entitlement?
9. **Bootstrap exceptions:** When is mutable template creation acceptable, and who approves it?
10. **Adoption scope:** Supported existing protections, unmanaged settings, and initial repository cohort?
11. **Security standards:** Go vulnerability/IaC scanners, severity policy, exception expiry, and remediation ownership?
12. **Version policy:** Supported Terraform/provider/Go combinations and immutable tag versus SHA conventions?
13. **Integration copies:** Mechanically generated installation artifacts or removal in favor of canonical shared releases?
14. **Operations:** Support owner, incident severity, acceptance latency targets, audit retention, and drift response?
15. **Codex advisory:** Allowed data, authentication, retention, budget, requesters, and outage behavior?

The next authorized work should be **Phase 0 design reconciliation and ADR review**. Further implementation should follow the selected production trust model, rather than treating existing checkout behavior as the approved architecture.