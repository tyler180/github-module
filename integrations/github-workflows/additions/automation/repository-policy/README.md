# Trusted repository policy (local-only)

policy.py is a standard-library validator. It reads JSON; it never runs Terraform,
shell commands, candidate Python, or dynamically selected candidate policy. Use
`python3 -I` from an immutable reviewed github-workflows checkout. Inputs belong
in separate candidate, approved-base, accepted-record, and observation directories.

The trusted policy-ref must be selected from the previously approved caller/base
revision, not candidate inputs. Changes to policy code or its trusted ref require
separate promotion. CODEOWNERS/reviewers and administrative credential control
remain trusted. A caller able to change the policy-ref can bypass that boundary;
the string's SHA format alone does not prove approval.

Delivered adapters accept source=offline-fixture only. Every receipt includes
deployment_authorized=false. Fake IDs, commits, and successes exist only in test
fixtures. No live record, API collector, credentialed plan, apply gate, or approved
record writer is enabled. repository-policy.yml reads same-run artifacts by ID in
a separate unprivileged job. The deployment workflow now requires that job for
repository inventory roots, followed by an authorization job that rejects all
fixture-only authorization. Live collector, record writer, and pre-apply live
rechecks remain prerequisites before that block can be replaced.

CLI required inputs:

- --base: previous accepted repositories.json; --base-sha: immutable revision.
- --record: separately trusted accepted record (schema 1, configuration_sha,
  inventory_digest, repositories with immutable IDs/name/stage/tooling_digest).
- --candidate: bound snapshot's repositories.json.
- --evidence: schema 1 observations, each marked offline-fixture, with fresh UTC
  timestamp, matching identity/tooling digest, bootstrap commits, checks, negative
  validation, and effective protection facts when granting access.
- --plan-json: full format-1.2 Terraform plan JSON; --saved-plan: corresponding
  bytes. Fixture tests use clearly labeled fake saved-plan bytes.
- --configuration and --configuration-sha: exact snapshot and producer revision.
- --policy-sha: trusted policy revision; --receipt: output outside snapshot.

The receipt hashes snapshot file paths/bytes (excluding .git/.terraform caches),
saved-plan bytes, plan JSON, policy implementation, and all inputs. It binds base,
candidate, and policy revisions. verify_receipt.py repeats evaluation with fresh
inputs/time and refuses changed bytes, records, evidence, policy, or revisions.

These hashes provide substitution detection, not signature/attestation. The CLI
cannot prove claimed commits supplied a snapshot, that JSON was generated from
the binary plan, or that offline observation facts happened. Before live rollout,
trusted artifact collection must verify those relationships independently and
query GitHub for actual runs/commits/effective access and protections. No signed
receipt system is invented here. A future live adapter must not accept these
offline receipts as deployment authorization.

The policy rejects skipped/backward stages, unmatched accepted bases, destruction,
replacement, unmanaged-field changes, visibility changes, archival, imports,
drift, unknown critical values, unexpected resources, and premature grants. Root
baseline review policy is fixed; no bypass actors. Developer teams use pull,
triage, or push. Changing provisioners or existing Actions policy requires a
separate reviewed lifecycle/security procedure. Full planned values are checked
against inventory and against resource_changes, not only changed resources.

Check-name removals require overlap and renewed observations. Actual strong
enforcement is account-specific: dummy jobs can satisfy a check context; code-owner
review is the initial defense. Stronger workflow identity requires central policy.

Run test_policy.py, test_receipt.py, and test_hygiene.py with python3 -I. No third
party packages, live credentials, backend, or successful live evidence are needed.
