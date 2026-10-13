# Proposed platform ADRs

Extracted from architecture-review.md. Status: proposed; existing ADRs remain unchanged.


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

