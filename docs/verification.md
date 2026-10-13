# Local verification — 2026-10-12

No Terraform apply, GitHub mutation, deployment enablement, publish, or push occurred.

| Check | Result |
|---|---|
| Terraform fmt -check -recursive | PASS (module, examples, tests, lockfile) |
| Provider installation | PASS for module and all four consuming examples using local mirror of official 6.13.0 darwin_arm64 archive; SHA256 verified against published sums |
| Module Terraform validate | PASS after authorized credential-free execution outside the socket restriction |
| Module mocked Terraform tests | PASS: 11 plan-only mocked tests |
| Consuming-root validate/mocked tests | PASS: all consuming roots validate; 3 mocked stage tests |
| Other examples' provider validation | PASS: minimal, adoption, template and consuming-root configurations |
| Policy fixtures | PASS: 48 standard-library tests (including policy regression fixes) |
| Receipt/isolation fixtures | PASS: 10 tests |
| Shared hook fixtures | PASS: 4 tests |
| Template materialization fixtures | PASS: 6 tests |
| Actionlint 1.7.12 | PASS: 5 new shared workflows, 2 existing plan/deploy workflows, 2 rendered starter/pilot callers |
| Native Terraform JSON smoke | PASS: built-in-only credential-free terraform_data fixture validated/planned; exact binary/JSON/snapshot receipt evaluated and rechecked; no apply |
| Sibling patch | PASS: git apply --check and apply to isolated temporary copy; original plan/deploy workflow bytes preserved |
| Real github-workflows checkout | Shared additions and deployment gates now applied locally; no push |
| Live account, import, enforcement, credentials/backend, collector/deployment gates | PENDING |

Terraform 1.15.8 is installed locally. Module minimum 1.7 supports mocks and removed
blocks, but this session could not execute provider-mocked tests. The ordinary policy
adapter accepts full JSON format 1.2 with complete/errored/applyable indicators;
future integrations must verify their chosen Terraform version produces that shape.

14 plan-only Terraform test runs are authored (7 core, 4 optional components, 3 root
stage guards). They use mock_provider github and contain no apply test runs. Run
scripts/validate-local.sh in an environment permitting provider RPC to complete them.

The provider error was confirmed as `listen unix ...: bind: operation not permitted`,
not missing account credentials. Local init initially hit registry DNS restriction;
the official release archive was downloaded, its published checksum verified, and
a temporary filesystem mirror used. The root lockfile includes published archive
checksums for released platforms plus the installed platform hash. No sandbox
escape or alternative credentialed execution was used.

Policy tests use fictional identities and explicitly marked offline observations.
The native plan smoke uses an empty inventory, fictional revision labels, and only
a built-in Terraform resource. Neither constitutes successful live acceptance or
an accepted deployment record. All receipts explicitly deny deployment authorization.

The staged sibling patch is integrations/github-workflows/local-additions.patch.
It adds new reusable tooling and appends documentation; existing workflow files
are not changed. Live trust/collector integration is documented but not enabled.

Policy regression follow-up: 48 policy, 10 receipt, 4 hygiene, and 6 template
tests pass (68 total). The revised regression suite fails against the pre-fix
policy implementation. Both policy copies match, and the regenerated original
installation patch passes git apply --check against the committed sibling
baseline. No deployment integration or Terraform-provider execution is claimed.

## Validation, scanner, and gate follow-up

Provider startup succeeded outside the sandbox: module and all four examples
validate; all 14 mocked Terraform tests pass. Added four real Gitleaks tests and
eight deployment-workflow tests. The latter exercise the actual apply expression,
fixture authorization rejection, required dependency graph, manual runs, missing
trusted revisions, and inventory-policy disablement. Shared committed histories
scan clean. No live apply or deployment authorization was attempted.

The sibling checkout is now modified locally, including terraform-deploy.yml.
The prior unchanged-checkout/workflow statements describe the initial delivery
only. Deployment remains explicitly blocked for repository policy consumers.

Final follow-up: complete local validation passes (14 Terraform and 80 Python
tests), including workflow linting. Original install patch applies cleanly to
the committed baseline and yields the current deployment workflow. No live
repository authorization is claimed.

## Credential integration follow-up

Passed 11 deployment workflow tests and 50 policy tests; deployment workflow
passes actionlint. Tests include empty planning/apply credentials, production
secret isolation, and omitted rulesets before protection versus mandatory rulesets
at protected stages. These results do not verify OIDC, token permissions, record
storage isolation, or authorize a live deployment.

## Create-stage implementation and access preflight

Passed 10 live-adapter unit tests, 50 policy tests and 11 existing deployment
workflow tests. New reusable deployment and access workflows and the standalone
access caller pass actionlint. Regression coverage includes later-stage rejection,
provisioners, unrecorded adoption, service failures, environment restrictions and
changed saved-plan rejection before record advancement.

Live OIDC and S3 probe testing is pending the access preflight PR's merge and
production approval. No Terraform apply or accepted-record write was performed.
