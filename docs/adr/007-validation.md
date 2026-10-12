# ADR 007: Validation versus deployment

Status: approved locally; credentialed integration pending.

Decision: credential-free fmt/backend-disabled validate/mocked plan tests. Separate
credentialed plan/deploy uses existing TERRAFORM.md contract. Alternative: force
every module consumer through cloud-role/backend planning. Consequence: account,
credentials, reviewers, and backend gate live rollout, not local work. No mandatory
Terraform check blocks or CI warning-only safeguards.
