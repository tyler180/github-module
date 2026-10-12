# ADR 001: One repository per module

Status: approved for local implementation; live rollout pending.

Decision: keep repository resources in the reusable module. Organization policy,
inventory, onboarding stages, provider/backend, and deployment records belong to
the root. Alternative: organization-wide module. Consequence: stable small ownership
boundaries, independently importable repositories, no organizational abstraction
engine. Reuse github-workflows rather than a new automation repository.
