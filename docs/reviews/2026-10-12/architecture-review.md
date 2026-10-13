# GitHub Repository Provisioning Platform: Architecture Review and Implementation Plan

**Review date:** 2026-10-12  
**Scope:** `github-module`, sibling `github-infra`, and sibling `github-workflows`  
**Status:** Planning proposal; no implementation authorized by this document

This review reads current checkout contents as evidence. Existing implementation, local changes, ADR status labels, release references, and historical verification statements do not constitute approval of the proposed production design.

No files were modified, tests executed, Terraform applied, secrets retrieved, git state changed, or agents spawned. Live GitHub settings, releases, deployment runs, IAM policies, backend state, and accepted records were not verified.

## 1. Executive verdict

The repository set has a useful foundation for a provisioning platform:

- A small Terraform module with explicit repository ownership.
- A separate inventory root.
- Shared workflows and hooks.
- Deterministic aggregate validation.
- Semantic inspection of complete Terraform plans.
- Separate desired stages and accepted deployment records.
- Explicit rejection of fixture evidence as deployment authorization.
- A narrowly scoped recovery path for a reportedly applied but unaccepted pilot.

**It is not yet an engineering-organization-quality production platform.** The principal blockers are incomplete live lifecycle authorization, account-specific deployment code, insufficiently established separation between candidate execution and privileged authority, and an unresolved enforcement model for validation implementation identity.

The recommended direction is to retain the three-repository boundary, use reviewed exact-source bootstrap PRs as the production default, and build an organization-specific control plane around the existing module. Organization-wide security policy must be established independently of repository creation.

Production rollout should wait until the platform demonstrates:

1. Verified account capabilities and independent approval.
2. Restricted and audited credential paths.
3. Trusted observation for every supported lifecycle transition.
4. Exact-plan authorization and safe recovery.
5. Validation that cannot be replaced merely by emitting the same check name.
6. No-change adoption and explicit ownership handoff.
7. Controlled upgrades across module, workflows, hooks, policy, and providers.

A personal-account pilot can validate selected mechanics. It cannot establish organization access governance or production approval guarantees.

## 2. Concrete current state

Paths below are relative to `github-module`; `../github-infra` and `../github-workflows` identify the sibling repositories.

### 2.1 Repository module

| Observation | Supporting paths | Architectural implication |
|---|---|---|
| One module instance owns one repository. Provider owner is supplied by the root. | `repository.tf`, `variables.tf`, `versions.tf` | A suitable reusable boundary; organization identity and policy remain external. |
| Managed settings include visibility, topics, merge methods, features, archive state, and related repository options. | `repository.tf`, `variables.tf` | Defaults can alter adopted repositories unless explicitly matched first. |
| Creation supports `basic`, `template`, and `none`. Template selection has no source ref. | `repository.tf`, `variables.tf` | Template provenance cannot provide exact source pinning. |
| Repository destruction is blocked with literal `prevent_destroy`; `archive_on_destroy` is also configured. | `repository.tf` | Useful defense in depth, but not a complete retirement or removal policy. |
| Creation fields and several externally owned fields are ignored after creation. Default branch has a separate optional resource. | `repository.tf`, `docs/ownership.md` | Ownership is deliberately divided, but provider update behavior requires acceptance testing. |
| Team grants are additive, optional resources. | `access.tf`, `variables.tf` | These grants do not describe all effective access. |
| Actions policy and workflow-token defaults are optional managed resources. | `actions.tf` | Omission at creation and removal after management have different consequences. |
| Rulesets protect the default branch against deletion and force pushes and can require reviews and status checks. | `ruleset.tf`, `variables.tf` | Good baseline mechanics; effective inherited policy and check trust remain separate questions. |
| `managed_components` describes configured ownership, expressly not readiness. | `outputs.tf` | Preserve this distinction in all future APIs and reporting. |

The module supports Terraform `>= 1.7, < 2.0` and GitHub provider `>= 6.13.0, < 7.0.0` (`versions.tf`). Root selections and compatibility testing therefore matter; local module behavior does not prove behavior of a published release.

### 2.2 Inventory root

`../github-infra/repositories.tf` uses stable inventory keys and forwards repository settings to a pinned module release, `v0.1.0-rc.2`. It does not consume the current sibling module checkout.

The root:

- Recognizes `create`, `bootstrap`, `verify`, `protect`, and `grant`.
- Requires configured checks at `protect` and `grant`.
- Requires disjoint provisioning and developer team keys.
- Adds developer grants only at `grant`.
- Creates a repository ruleset only at `protect` or `grant`.

The current `../github-infra/repositories.json` contains **two** create-stage entries: `pilot` and `example_go_pilot`. Both are private, use basic initialization, request `main`, and have empty team and check maps.

This conflicts with `../github-infra/README.MD`, which describes the first pilot and says example entries are outside the deployed inventory. The root processes the actual inventory; documentation does not limit its scope.

The example root behaves differently: `examples/consuming-root/main.tf` always configures a baseline ruleset, disabled before protection. The real root omits it beforehand. This difference affects entitlement, resource lifecycle, and operational expectations.

### 2.3 Policy and deployment paths

There are two distinct paths.

**General staged policy path**

`../github-workflows/automation/repository-policy/policy.py`:

- Compares candidate inventory with an accepted baseline.
- Restricts ordinary transitions to the same stage or one forward stage.
- Rejects removal, destructive actions, replacement, imports, drift, unsupported resources, incomplete plans, and critical unknowns.
- Inspects both resource changes and complete planned values.
- Enforces expected grants, ruleset settings, and optional-component ownership.
- Requires overlap when changing protected check contracts.
- Supports later-stage observations only when marked `offline-fixture`.

`repository-policy.yml` and `verify_receipt.py` produce and verify offline bindings. They expressly deny deployment authorization.

`../github-workflows/.github/workflows/terraform-deploy.yml` includes an authorization job that deliberately fails for this offline policy path.

**Restricted live create path**

`repository-create-deploy.yml` and `live_create.py` implement a separate create-only path:

- Restricted caller repository, branch, and trigger.
- Saved-plan artifact identified through the planning job.
- Independent JSON decoding using specified official providers.
- Production environment checks.
- Configuration, plan, policy, and accepted-record bindings.
- Pre-apply recheck.
- Post-apply repository verification.
- Conditional S3 accepted-record write.

Its scope is explicitly personal-pilot-specific:

- Hardcoded owner, owner ID, reviewer ID, repository, bucket, and record key.
- Create stage only.
- No team grants.
- No optional Actions or workflow-permission policies.
- One-hour authorization validity.

The live path must not be described as implementation of all five stages.

### 2.4 Recovery

`repository-create-recover.yml` and `recover_create.py` implement acceptance-only recovery for a particular reported run, source revision, and repository ID.

The recovery checks:

- Original run identity and referenced workflow revision.
- Successful authorization and apply steps.
- Exact expected Terraform state ownership.
- Current repository settings and identity.
- Absence of an existing accepted record.

It conditionally creates the initial accepted record and runs no Terraform commands.

This is useful incident-specific code. It is not a general recovery service or adoption workflow.

### 2.5 Workflows, hooks, and standards

| Area | Observed implementation |
|---|---|
| Go validation | `go-validate.yml`: formatting, `go vet`, race tests, hygiene, and an `always()` aggregate gate that requires successful dependencies. |
| Terraform module validation | `terraform-module-validate.yml`: formatting, backend-disabled initialization, validation, Terraform tests, hygiene, aggregate gate. |
| Root validation | `../github-infra/scripts/validate-local.sh`: backend-disabled initialization with read-only lockfile and mocked tests. |
| Shared hygiene | `repository-hygiene.yml` and `hooks/repository_hygiene.py`: trailing whitespace and conflict markers; skips symlinks and patch/diff files. |
| Secret detection | `hooks/secret_scan.py`: exact Gitleaks version, central configuration, redaction, candidate suppressions disabled; staged scanning locally and history scanning in CI. |
| Local hooks | `.pre-commit-hooks.yaml` and generic `.pre-commit-config.yaml.in`: hygiene and secret scanning. |
| Bootstrap | `scripts/render-template.py`: explicit substitutions into a new directory, refuses an existing destination. |
| Caller protection | Generic CODEOWNERS protects `.github`, selected validation files, root Terraform files, inventory, and evidence paths. |
| Tests | Mocked Terraform plan tests and Python policy, receipt, deployment, recovery, scanner, hygiene, and template fixtures exist. Their presence does not establish that they pass now. |

Important differences:

- The module validation script and shared Terraform module workflow do not use `-lockfile=readonly`; the infrastructure root does.
- `examples/go-pilot/scripts/validate.sh` adds an executable smoke assertion absent from shared Go validation.
- Local pre-commit configuration does not run Go or Terraform standards.
- Generic CODEOWNERS covers root-level Terraform patterns, not every nested Terraform configuration or lockfile.
- `repository-live-policy-tests.yml` watches policy code and its own workflow, but not all deployment workflows.
- `validate-terraform.yml` lints a limited workflow set.
- The module’s local script tests copied policy tooling under `integrations/github-workflows`, while the sibling checkout has additional live adapters and tests.
- The rendered Go caller references `v2.2.0-rc.1`; infrastructure deployment references `v2.1.0-rc.4`. Independent versions are reasonable, but compatibility must be demonstrated.

## 3. Readiness reconciliation

### 3.1 Conflicting evidence

| Source | Repository statement | Review interpretation |
|---|---|---|
| `docs/architecture.md`, `docs/live-acceptance.md` | Live integration/callers remain pending or absent. | Earlier architectural status; incomplete for current checkout. |
| `docs/verification.md` | Multiple rounds of local passes, restrictions, and follow-ups. | Historical claims, not checks performed in this review. |
| `docs/deployment-gates.md` | Reported apply added three resources; acceptance failed; recovery pending. | A partial operational outcome is documented, not independently verified. |
| `../github-infra/README.MD` | Initially says no repository created, later describes completed apply recovery. | Contradictory readiness narrative. |
| `../github-workflows/TERRAFORM.md` | General repository deployment remains offline-blocked. | Correct for that workflow path; does not describe the separate create adapter fully. |
| Existing ADRs | Local approval labels and pending live rollout. | Historical decision records; not production design approval. |

### 3.2 Recommended readiness model

Replace a single “ready” label with independent dimensions:

1. **Authored:** code/configuration exists.
2. **Locally verified:** named checks passed against an identified commit and environment.
3. **Published:** exact releases and resolved commits verified.
4. **Access verified:** actual credential and backend capabilities tested.
5. **Applied:** a particular operation completed.
6. **Accepted:** post-operation verification advanced the protected record.
7. **Lifecycle accepted:** specified stages and negative scenarios passed.
8. **Production approved:** security, operations, and ownership requirements accepted.

The current defensible verdict is: **implementation exists; historical local verification and partial pilot apply are documented; current live acceptance and organization readiness are unverified.**

A future readiness ledger should record scope, commit, run, observer, timestamp, limitations, and evidence location. Historical documentation should remain historical rather than being silently rewritten as current proof.

## 4. Severity-ranked gaps and threat model

Severity reflects production consequence. It does not assert that an exploit or live misconfiguration has occurred.

| Severity | Gap or threat | Evidence | Recommendation |
|---|---|---|---|
| Critical | A production platform claim could exceed the implemented authorization scope. Later-stage evidence remains fixture-only. | `policy.py`, `live_create.py`, `repository-policy.yml` | Keep unsupported transitions blocked until a trusted live collector and stage-specific authorizers exist. |
| Critical | Credentialed Terraform execution precedes semantic inspection. Malicious providers, external execution, or modified configuration can misuse credentials before policy rejects the plan. | `repository-create-deploy.yml`, `terraform-plan.yml`, `live_create.py` | Treat credentialed configuration authors as privileged; add trusted static source/dependency restrictions before credential issuance and isolate execution. |
| High | Check context and integration identity do not establish validation implementation identity. A replacement Actions job can emit the same context. | `ruleset.tf`, `docs/upgrades.md`, caller templates | Require central workflows where supported, or a narrowly scoped independent check issuer. CODEOWNER review is a human control with explicit residual trust. |
| High | The live adapter is bound to one personal account and one infrastructure repository. | `live_create.py`, `recover_create.py`, create/recovery workflows | Introduce protected organization configuration and independently verified identities; never let candidate inputs choose authority. |
| High | Environment approval guarantees depend on plan entitlement and actual settings. Current checker requires one specific reviewer but does not explicitly check self-review prevention. | `live_create.py::verify_environment` | Verify capabilities, prevent self-review, disable bypass, constrain branches, and separate approval roles. |
| High | The create planning job uses the supplied apply AWS role. Role policies are not present as evidence here. | `repository-create-deploy.yml` | Separate plan/backend access, apply/state-write access, and record-write access. Do not infer least privilege from role names. |
| High | State and accepted-record writes are not atomic. Apply can succeed while acceptance fails. | `live_create.py`, recovery code, `docs/deployment-gates.md` | Model partial completion explicitly; preserve evidence and require constrained reconciliation. |
| High | Team maps do not account for organization base access, inherited teams, direct collaborators, Apps, deploy keys, or owners. | `access.tf`, `docs/onboarding.md` | Collect effective access before claiming a restricted bootstrap window. |
| High | Optional resource removal can delete or reset security configuration. | `actions.tf`, `ruleset.tf`, `docs/ownership.md` | Require explicit handoff; block ordinary security-component removal. |
| High | General workflow policy auto-detection depends on a conventional `repositories.json` filename. | `terraform-deploy.yml`; root `inventory_file` variable | Enforce policy by registered state/root identity, not candidate-controlled file presence. |
| Medium | Documentation and example-root behavior diverge from real-root behavior. | `docs/ownership.md`, `docs/onboarding.md`, both roots | Establish one supported lifecycle contract and acceptance matrix. |
| Medium | Workflow changes can fall outside relevant automated test triggers and lint scope. | `repository-live-policy-tests.yml`, `validate-terraform.yml` | Cover all security-sensitive workflow/helper changes and their dependency graph. |
| Medium | Module integration copies can drift from authoritative shared automation. | `integrations/github-workflows`, sibling automation | Declare the authoritative source and mechanically verify or retire copies. |
| Medium | Schema validation permits incompletely specified intent and relies on downstream checks. | `policy.py::inventories`, root `try(...)` defaults | Add strict schema, unknown-field rejection, capability checks, and cross-field validation. |
| Medium | Secret scanning is present; dependency and IaC vulnerability standards remain undecided. | `docs/security-scanning.md` | Define mandatory scanners, severity thresholds, exceptions, and remediation expectations. |

### Threat boundaries

**Assets:** repository identity/history, organization access, branch protection, automation credentials, backend state, accepted history, bootstrap provenance, deployment authority.

**Potential adversaries:** external PR authors, compromised developers, malicious dependencies, compromised shared automation maintainers, compromised provisioning credentials, and operators making unsafe recovery changes.

**Explicitly trusted roles:** organization owners, security policy maintainers, approved provisioning operators, and authorized reviewers. Their actions require auditability; branch rules cannot fully constrain an organization owner who can change the rules.

**Residual races:** branch advancement, environment changes, access changes, and remote settings changes can occur after observation. Rechecks reduce these windows; they do not create a transaction across GitHub and Terraform.

## 5. Ownership and security matrix

| Surface | Accountable owner | Normal authority | Boundary and recovery |
|---|---|---|---|
| Organization policy, base permissions, Apps, enterprise rules | Organization security | Dedicated administrative path | Outside repository module; audited exceptions. |
| Inventory and requested lifecycle | Platform provisioning | Reviewed infrastructure PR | Intent cannot create accepted history. |
| Terraform module | Platform infrastructure | Module release PR | No source-file or organization-policy ownership. |
| Shared workflows/hooks | Developer platform | Protected automation release | Security review for privilege and trust changes. |
| Application source and repository callers | Repository team | Reviewed source PR | Central controls protect validation assumptions. |
| Credentialed plan | Provisioning executor | Read-oriented GitHub access; scoped backend locks/reads | Candidate execution isolated; no accepted-record writes. |
| Apply | Provisioning operator | Approved short-lived credential; scoped state writes | Exact authorized saved plan only. |
| Live evidence collection | Platform assurance | Read-only GitHub/API authority | Independent of candidate claims; identity-bound evidence. |
| Accepted-record publication | Assurance publisher | Restricted conditional record write | No candidate code, Terraform execution, or arbitrary file publication. |
| Adoption/handoff/retirement | Platform plus repository owner and security | Exceptional reviewed operation | Separate authorization and no-change baseline. |
| Emergency access | Security incident owner | Time-bounded break-glass | Reason, approval, audit, expiration, follow-up reconciliation. |
| Advisory Codex review | Repository team with security oversight | Approved read scope | No merge, apply, credential, or readiness authority. |

Use GitHub Apps and short-lived installation credentials where the required creation and administrative capabilities support them. Validate exact permissions in a sandbox organization. If a PAT is necessary for organization repository creation, document that exception, minimize scope and lifetime, and isolate its use.

The record writer must be a constrained publisher, not merely a different IAM role in a job that can execute candidate material.

## 6. Source bootstrap decision

| Approach | Strength | Limitation | Proposed use |
|---|---|---|---|
| GitHub repository template | Simple creation-time starter copy | Provider cannot select an exact source ref; mutable source and no continuous upgrade relationship | Optional convenience mode with explicit provenance limitations |
| Exact-source bootstrap PR | Reviewed diff, reproducible source selection, repository-owned files | Requires an initial branch/commit and transformation manifest | Production default |
| Terraform-managed repository files | Declarative continuous ownership | Competes with developer ownership, introduces drift/deletion behavior, couples source changes to infrastructure credentials | Exclude from standard platform |

**Recommendation:** Terraform owns repository settings and selected grants/policies. Repository files become repository-team-owned through a reviewed bootstrap PR.

For exact-source bootstrap:

1. Create a basic repository with a minimal initial commit.
2. Select an approved source commit independently of the candidate repository.
3. Materialize a manifest of permitted paths and explicit substitutions.
4. Validate output paths, file modes, symlinks, unresolved placeholders, and prohibited content.
5. Record source commit/tree, transformation digest, destination base commit, PR, and merged commit.
6. Reuse an existing bootstrap PR on retry; never overwrite developer changes.
7. Deliver subsequent upgrades through PRs.

`docs/bootstrap.md` recommends basic initialization for this procedure. Do not equate `initialization=none` with a ready-to-open bootstrap PR: an empty repository needs a separate initial-commit procedure.

The current renderer defaults the Go module path to an example value (`scripts/render-template.py`). Production generation should require the real module path explicitly.

## 7. Target module, lifecycle, adoption, and security design

### 7.1 Module API

Retain a narrowly typed, one-repository API:

- Owner/provider supplied externally.
- Explicit managed settings with documented defaults.
- Immutable creation intent.
- Optional subordinate resources with whole-object ownership.
- Stable resource addresses.
- Repository IDs and configured ownership outputs.

Keep these outside the module:

- Organization policy.
- Backend and provider credentials.
- Workflow execution.
- Bootstrap file writes.
- Accepted records and evidence.
- Stage authorization.
- AI review.

Add root-level policy for owner type, account entitlement, approved naming, visibility, profile, administrative grants, security exceptions, and state ownership. The reusable module may remain broader than the production policy.

Null must not mean “preserve whatever is remote” after management has begun.

### 7.2 Lifecycle

| Stage | Operation | Required acceptance |
|---|---|---|
| Create | Repository/settings and restricted provisioning access | Stable identity, branch/initial commit, actual defaults and access |
| Bootstrap | Reviewed exact-source PR | Provenance, approved owners, pins and configuration, merged content |
| Verify | Deterministic eligible validation | Successful run plus deliberate failure, cancellation, and skip cases |
| Protect | Activate required checks/reviews | Effective inherited/local rules and negative enforcement tests |
| Grant | Add intended developer access | Accepted protection baseline and fresh effective-access verification |

Track operation status separately: `planned`, `authorized`, `applied`, `verification_failed`, `accepted`, or `recovery_required`.

Recommended rules:

- Normal transitions are same-stage or one forward step.
- No desired-stage advancement implies completion.
- Grant requires an accepted protected state.
- Root inventory removals, renames, visibility changes, and retirement require exceptional workflows.
- Production pre-protection ruleset strategy depends on verified entitlement: disabled stable ruleset where appropriate, omission where necessary, with both behaviors explicitly tested.
- Each state partition has one authoritative root and deployment authority.

### 7.3 Exact-plan authorization

The authorization bundle should bind:

- Caller and owner immutable IDs.
- Configuration commit and snapshot.
- Module, provider, workflow, hook, and policy revisions.
- Terraform/tool versions.
- Saved binary plan and independently decoded JSON.
- State lineage/serial and backend identity.
- Accepted-record version.
- Evidence identity, content/configuration digests, observation time, and expiration.
- Run, attempt, artifact identity, and approval scope.

Apply only that saved plan. After approval, recheck configuration freshness, baseline version, artifact bindings, policy version, and relevant live protections.

Plan policy must run before privileged mutation, but it also needs a **pre-execution boundary**: approved module/provider sources, no provisioners or executable external data, reviewed backend definitions, and isolated execution before credentials are exposed.

### 7.4 Adoption and handoff

Follow `docs/adoption.md`, but turn it into an explicit supported operation:

1. Inventory settings, protections, effective access, Apps, and ownership.
2. Match every managed attribute.
3. Import each selected resource.
4. Require a complete no-change plan.
5. Accept an identity and ownership baseline.
6. Propose defaults or bootstrap changes separately.

Do not fabricate create-stage acceptance for an existing repository.

For handoff, preserve remote configuration through reviewed management removal, supported `removed` blocks where applicable, or tightly scoped state operations. Verify the remote object and a subsequent unrelated update. Ordinary resource deletion is not handoff.

Retirement should archive by default, preserve history and ownership records, revoke unnecessary automation, and require a separately approved deletion process.

### 7.5 Security posture

Before developer handoff, verify:

- Read-only default workflow token.
- Actions PR-review approval disabled.
- Approved action/reusable-workflow sources.
- Approved immutable pin policy.
- Effective branch and tag protections.
- Effective contributor access and administrative exceptions.
- Secret detection.
- Profile-specific dependency and IaC scanning.
- Security reporting ownership.

The module ignores several security-related fields (`repository.tf`). Give each an explicit external owner and observer. `ignore_changes` is not proof that security is configured correctly.

## 8. Required-check bypass resistance and PR trust

### 8.1 Required-check contract

Use a stable aggregate check and observe its actual emitted context. Do not infer reusable-workflow context names from YAML job names.

The existing aggregate gates correctly require dependency results to equal `success`. Preserve this property:

- Failure, cancellation, skipped validation, missing results, and scanner errors fail acceptance.
- No `continue-on-error` on required validation.
- No permanently successful compatibility alias.
- No workflow-level path filter that prevents a required result.
- `merge_group` support before enabling merge queues.

GitHub status rules select contexts and can constrain the reporting App; they do not establish which workflow implementation ran. GitHub also requires merge-group triggers when required checks are used with merge queues. [GitHub rules documentation](https://docs.github.com/en/enterprise-cloud%40latest/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets), [rules troubleshooting](https://docs.github.com/en/enterprise-cloud%40latest/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/troubleshooting-rules).

### 8.2 Production enforcement choice

Prefer organization-required central workflows where supported. Central workflows must also constrain their inputs and validation scope; a required central workflow that trusts arbitrary caller-selected paths can still validate the wrong thing.

If unavailable, evaluate a dedicated narrowly scoped check issuer that verifies trusted workflow provenance and candidate identity. Account for `workflow_run`, artifact, and repository trust before introducing it.

Protected local callers with CODEOWNER review are an acceptable interim model only if production owners explicitly accept reviewer trust. The dummy-substitution test demonstrates review protection, not immutable execution identity.

### 8.3 PR and fork boundaries

- Run credential-free validation on forks and same-repository PRs.
- Treat test scripts, Terraform providers/modules, and build dependencies as executable candidate content.
- Never execute submitted code with privileges through `pull_request_target`.
- Same-repository PR authors are not automatically safe for cloud credentials.
- Restrict credentialed plans to an approved trust path.
- Do not pass `secrets: inherit` to ordinary validation.
- Use ephemeral runners without production network access.
- Avoid restoring untrusted caches or artifacts into privileged jobs.
- Bind artifacts to repository, run, attempt, commit, and producer.
- Use `persist-credentials: false`, narrow permissions, timeouts, and explicit event conditions.

A fork’s successful unprivileged CI can satisfy source validation; it cannot authorize provisioning or prove protected environment access.

## 9. Local parity and Go/Terraform standards

### 9.1 Local hooks

Local hooks provide feedback and remain bypassable. CI is mandatory.

Recommended parity means the same rule implementation, revision, and configuration, while allowing different scopes:

- Local secret scan: staged changes.
- CI secret scan: fetched history.
- Local and CI hygiene: identical rejection semantics.
- Local language validation: a documented command matching CI’s required checks.

Document installation, tool versions, update procedure, offline failure behavior, and exceptions. Add nested validation/configuration paths to protected ownership patterns.

### 9.2 Go profile

Keep formatting, vet, and race tests. Define:

- Explicit supported Go versions.
- Explicit module path.
- Multi-module/workspace policy.
- Dependency/lockfile consistency.
- Vulnerability scanning and remediation threshold.
- Smoke/integration checks where meaningful.
- Whether static analysis or coverage is mandatory.

Reconcile the starter’s local smoke assertion with shared CI. Avoid a generic coverage target that does not reflect product risk.

### 9.3 Terraform profile

Separate three standards:

1. **Reusable module:** formatting, validation, plan-only mocked tests, API/default/lifecycle tests.
2. **Infrastructure root:** schema, lockfile, pinned modules/providers, backend-disabled validation and semantic policy fixtures.
3. **Credentialed execution:** approved sources, remote locking, exact saved plan, authorization, post-operation verification.

Standardize read-only lockfiles for execution. Root provider locks are authoritative for deployments; module lockfiles do not lock downstream consumers.

Require all security-sensitive workflows to pass lint and dependency-graph tests. Extend compatibility tests to the actual minimum Terraform version and supported provider selections. Mocked tests do not establish import or GitHub update semantics.

## 10. Advisory Codex review boundaries

ADR 012 correctly leaves this deferred (`docs/adr/012-advisory.md`).

Recommended boundaries:

- Opt-in advisory review.
- Approved code/diff scope and retention policy.
- No infrastructure credentials or accepted-record writes.
- No authority to approve, merge, bypass, apply, or certify readiness.
- Budget and rate limits.
- Clear handling of outages and unavailable reviews.
- Candidate text treated as untrusted instructions.
- Human review of findings; deterministic checks remain mandatory.

AI recommendations cannot replace security review, test evidence, or live acceptance.

## 11. Production organization versus personal-account pilot

A production organization needs team governance, organization base permissions, inherited rules, centrally managed Apps, independent reviewers, and administrative separation.

A personal-account pilot cannot demonstrate team grants, organization inheritance, or separation from the repository owner. The current live adapter deliberately rejects team grants and later stages (`live_create.py`).

Rulesets are available for private repositories on specified paid plans, but individual rule capabilities must still be checked. Private repository environment required reviewers are a separate entitlement: GitHub documents them as public-only for Free, Pro, and Team plans. An environment existing is not proof that its approval protection is available. [Ruleset availability](https://docs.github.com/en/enterprise-cloud%40latest/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets), [deployment environment protections](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments).

Therefore:

- Verify the exact production organization plan before choosing enforcement.
- Verify internal visibility eligibility.
- Confirm private shared-workflow access and fork behavior.
- Require an independently enforceable approval mechanism.
- Do not transfer personal pilot readiness claims to organization production.

## 12. Proposed ADRs

All ADRs below are **proposed**. They should amend or supersede relevant existing records after review.

### ADR P01 — Three repositories, explicit control-plane ownership

**Context:** ADR 001 and current files already divide module, root, and automation responsibilities.

**Decision:** Retain that split. Security owns organization baseline; platform owns inventory and provisioning; repository teams own source.

**Alternatives:** Organization monolith; independent automation copies per repository.

**Consequences:** Smaller ownership boundaries, but cross-repository compatibility and release governance become mandatory.

**Acceptance criteria:** One documented owner per resource/control; one state owner per repository; compatibility manifest; no source-file resources or organization administration inside the module.

### ADR P02 — Exact-source bootstrap PR as production default

**Context:** Templates cannot select an exact source revision; developer source should not be continuously controlled by Terraform.

**Decision:** Use basic creation plus reviewed exact-source PR. Templates remain an explicitly weaker convenience mode.

**Alternatives:** Template-only provisioning; Terraform file resources; unrestricted bootstrap scripts.

**Consequences:** Additional orchestration and provenance records; clearer review and safe retries.

**Acceptance criteria:** Reproducible output manifest; explicit substitutions; safe paths/modes; no unresolved placeholders; no overwrite; retry resumes the same PR.

### ADR P03 — Accepted state is independent of desired state

**Context:** Stage variables are intent; apply and acceptance can fail independently.

**Decision:** Use protected versioned accepted history, monotonic ordinary transitions, and explicit operation status.

**Alternatives:** Main-branch inventory as truth; candidate-written evidence.

**Consequences:** More state and reconciliation logic; failures cannot silently advance readiness.

**Acceptance criteria:** Missing/stale/conflicting evidence fails closed; conditional publication; partial apply leaves accepted stage unchanged; later stages use live evidence rather than fixture flags.

### ADR P04 — Authorize both execution inputs and exact plans

**Context:** Plan inspection occurs after credentialed Terraform execution.

**Decision:** Restrict executable inputs before credentials, inspect exact complete plans afterward, and separate plan/apply/record authority.

**Alternatives:** Plan-only semantic policy; fully trusted unrestricted roots.

**Consequences:** Reduced extensibility; stronger privilege boundaries.

**Acceptance criteria:** Unauthorized modules/providers/external execution rejected before credential exposure; separate scoped roles; exact artifact/source bindings; no candidate execution in the record publisher.

### ADR P05 — Centrally governed validation contract

**Context:** Context/App identity alone does not prove validation behavior.

**Decision:** Prefer central required workflows; otherwise adopt an explicitly reviewed alternative with documented residual trust.

**Alternatives:** Status-only rules; protected local caller only; unrestricted bot check.

**Consequences:** Entitlement dependency or additional verifier operations.

**Acceptance criteria:** Dummy context substitution cannot bypass the chosen production boundary; caller/CODEOWNERS deletion tests; failure/cancellation/skip tests; correct candidate and merge-group identity.

### ADR P06 — Explicit lifecycle ownership and exceptional operations

**Context:** Optional-resource removal can reset or delete policy; normal deployment rejects adoption and destruction.

**Decision:** Preserve whole-object ownership and provide separate adoption, handoff, rename, visibility-change, and retirement procedures.

**Alternatives:** Null-as-preserve; implicit import; ordinary inventory deletion.

**Consequences:** More deliberate operations, fewer silent changes.

**Acceptance criteria:** No-change adoption; subordinate imports; preserved configuration after handoff; identity retained during migration; archived retirement with audit record.

### ADR P07 — Verified organization capabilities

**Context:** The current adapter is personal-account-specific; approval and ruleset availability vary.

**Decision:** Production onboarding requires a capability/access acceptance record for the selected organization.

**Alternatives:** Infer capability from plan name or personal pilot.

**Consequences:** A production prerequisite and potential entitlement cost.

**Acceptance criteria:** Independent approval, actual rule enforcement, private workflow access, effective access inventory, credential permissions, and backend isolation verified.

### ADR P08 — Independent component releases with governed promotion

**Context:** Module, automation, hooks, and policy use different versions; copies exist.

**Decision:** Maintain independent versions with a compatibility manifest, approved promotion, canaries, and protected update PRs.

**Alternatives:** One global release; automatic floating updates; permanent copied automation.

**Consequences:** Upgrade coordination, but smaller release blast radius.

**Acceptance criteria:** Approved revisions and resolved commits; centrally governed policy selection; tests of mixed supported versions; overlap check migration; rollback without relaxing protections.

### ADR P09 — Deterministic profile standards; advisory AI

**Context:** Go/Terraform checks exist, local parity is incomplete, and AI review is deferred.

**Decision:** Publish deterministic profile contracts and keep Codex advisory.

**Alternatives:** Mandatory AI gate; ad hoc per-repository validation.

**Consequences:** Explicit exception and scanner governance.

**Acceptance criteria:** Documented local/CI commands, pinned tooling, meaningful negative tests, scanner thresholds, AI access/budget policy, and no AI deployment authority.

## 13. Phased implementation plan

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

## Review provenance

Generated by Codex CLI 0.162.1 in a read-only session. Review includes uncommitted checkout contents; HEAD commits alone do not identify the reviewed trees.

- github-module HEAD: `5bc0ee4d295f5f85fa4b5f25788240b7ae6df8a3`
- github-infra HEAD: `ba0016d4245b2e41819efc4f6d66a9e80efb0511`
- github-workflows HEAD: `af06ebbdfe069ce16beee12d86c9ee03591592d7`

Paths in the review are relative to the github-module repository root, not this document directory. No live deployment or test results were verified during this review.
