# ADR 002: Source bootstrap ownership

Status: approved for local implementation; live rollout pending.

Decision: one generic template plus reviewed bootstrap PRs; no repository-file
resources. Mutable template SHA observations are provenance, not pinning. Exact
reproducibility uses a PR from an exact source commit. Alternative: continuous
Terraform file management. Consequence: source belongs to developers and update
PRs; Terraform removal cannot delete bootstrap files.
