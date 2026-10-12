# Mandatory policy gates and trust boundary

Implementation is staged in integrations/github-workflows/additions/automation/
repository-policy. The isolated reusable repository-policy.yml job reads uploaded
candidate data, checks out trusted base/record/policy separately, and runs Python
in isolated mode. It does not install Terraform or execute candidate configuration.
All current receipts and observations are explicitly offline-only.

## Enforcement allocation

Variable validation: names, enums, merge methods, team roles, ruleset review count,
bypass actor schema, nonempty selections. Resource preconditions: initialization
mode/template agreement, rename/branch relationship, selected-action configuration,
active ruleset/check relationship. Root terraform_data.contract preconditions:
stage/schema validity, checks at protect/grant, disjoint team classifications.

Trusted failing CI policy: accepted-base comparison, monotonic one-step stages,
independent evidence, complete-plan semantic inspection, destructive/security
actions, and premature grants. Literal prevent_destroy is defense in depth only.
There are no mandatory Terraform check blocks.

Policy uses plan resource_changes AND all planned_values, checks their consistency,
and validates the expected inventory-derived resources. It rejects unsupported
resource/data types, unknown critical values, deferred/incomplete/error plans,
drift, imports, deletion/replacement, weakening protections, and forbidden updates.
Computed IDs can be unknown during new creation, but known repository identity
must match the accepted record for existing repositories.

## Live integration prerequisites (not enabled)

1. Collect immutable approved base and last successful record from protected
   sources. PR base comparison is necessary; deployment additionally compares the
   accepted configuration, avoiding merged-but-unapplied transition assumptions.
2. Execute candidate Terraform only in the separate explicitly credentialed
   environment from existing TERRAFORM.md. Never execute PR code with privileges
   in pull_request_target. Contributors with plan credentials must be trusted.
3. Independently bind candidate snapshot to its Git commit; produce JSON from the
   exact saved binary plan and preserve both in a scoped immutable artifact.
   Candidate-written JSON/receipts are not authoritative.
4. Load validator and policy ref from approved base/central immutable revision.
   Evaluate full plan before packaging/approval. A failing gate has nonzero exit;
   no continue-on-error, optional bypass, or approval override.
5. Before apply, after environment approval, recheck current accepted record,
   source revision, artifact bindings, observation freshness and effective rules.
   Apply only the inspected saved plan. Do not replan inside the apply job.
6. Verify post-operation facts; only then write the next accepted record.

Existing terraform-plan.yml and terraform-deploy.yml remain unchanged. New gate
integration must be implemented and separately accepted before enabling this root.
All mandatory gates apply equally to manual dispatch and reruns. Reruns after
partial apply, stale inputs, missing/expired artifacts, or changed default branch
require a new plan and approval. A green PR test is not deployment authorization.

## Limitations

Receipts are unprivileged integrity manifests, not signed authorizations. The live
collector/storage and deployment-record writer are intentionally pending. Fixture
truth flags prove validator behavior only, never GitHub behavior. Reviewers and
admins remain trusted; pinned refs chosen by untrusted candidates are not trusted
policy. Administrative credentials outside the gated workflow can bypass policy.
Backend locking and cross-repository state ownership still need live verification.
