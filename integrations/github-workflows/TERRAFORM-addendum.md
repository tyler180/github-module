
## Repository module validation and offline policy

The existing terraform-plan.yml and terraform-deploy.yml contracts remain unchanged.
The additions below do not enable deployment and do not supply credentials/backend.

terraform-module-validate.yml provides credential-free fmt, backend-disabled init,
validate, provider-mocked plan-only tests, shared hygiene, and a failing aggregate
platform-ci job. Inputs: terraform-version, tooling-ref (same reviewed full SHA as
the reusable workflow reference), optional working-directory. Do not pass cloud
roles, provider administrative tokens, or secrets. Candidate validation remains
separate from explicitly credentialed infrastructure plan/deploy.

repository-hygiene.yml and the repository-hygiene pre-commit hook share a read-only
Python implementation. go-validate.yml is the single language pilot; it requires
go-version and tooling-ref, runs formatting/vet/race tests plus hygiene, and retains
a failing aggregate gate. Observe actual reusable check contexts before enforcement.

repository-policy-fixtures.yml runs trusted fixtures from a separately promoted
full trusted-policy-ref. repository-policy.yml evaluates same-run artifact data in
a separate job without Terraform execution. It checks out approved base and accepted
record independently from candidate input. Its refs must be selected by the trusted
caller/base; SHA syntax does not prove authorization. All current observations and
receipts are OFFLINE ONLY and deployment_authorized is always false.

Before any live repository deployment, integrate a trusted live observation and
artifact collector and mandatory policy gates into the existing deployment path.
Bind the exact saved binary plan, JSON generated from it, configuration snapshot/
commit, accepted base/record, and policy revision. Recheck after environment approval
and on manual/rerun paths. A partial apply requires a fresh plan and approval,
not reuse of the old saved plan. Record advancement follows verified successful
operations only. Existing artifact rerun behavior is preserved for other callers.

Account capabilities, independent reviewers, credentials, backend and protected
environments gate live rollout, not local validation. See automation/repository-policy/
README.md for the offline input/receipt schema and the remaining live trust boundary.
Codex review remains optional advisory follow-on, not the initial required gate.
