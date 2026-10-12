# Local verification — 2026-10-12

No Terraform apply, GitHub mutation, deployment enablement, publish, or push occurred.

| Check | Result |
|---|---|
| Terraform fmt -check -recursive | PASS (module, examples, tests, lockfile) |
| Provider installation | PASS for module and all four consuming examples using local mirror of official 6.13.0 darwin_arm64 archive; SHA256 verified against published sums |
| Module Terraform validate | BLOCKED: provider RPC cannot bind its local Unix socket in this sandbox |
| Module mocked Terraform tests | BLOCKED at schema loading; 0 tests executed, not a test pass |
| Consuming-root validate/mocked tests | BLOCKED by the same RPC restriction; 0 stage tests executed |
| Other examples' provider validation | NOT EXECUTED after confirming the shared provider RPC restriction; initialization succeeded |
| Policy fixtures | PASS: 43 standard-library tests |
| Receipt/isolation fixtures | PASS: 10 tests |
| Shared hook fixtures | PASS: 4 tests |
| Template materialization fixtures | PASS: 6 tests |
| Actionlint 1.7.12 | PASS: 5 new shared workflows, 2 existing plan/deploy workflows, 2 rendered starter/pilot callers |
| Native Terraform JSON smoke | PASS: built-in-only credential-free terraform_data fixture validated/planned; exact binary/JSON/snapshot receipt evaluated and rechecked; no apply |
| Sibling patch | PASS: git apply --check and apply to isolated temporary copy; original plan/deploy workflow bytes preserved |
| Real github-workflows checkout | UNCHANGED: writes rejected because it is outside writable workspace roots |
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
