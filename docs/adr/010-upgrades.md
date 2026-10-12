# ADR 010: Protected updates and overlap

Status: policy fixtures implemented; live migration pending.

Decision: keep grant stage/access/protection during tooling upgrades; reviewed PRs
and renewed commit/pin/config evidence. Check contexts migrate with overlap.
Alternative: rewind onboarding or relax protection. Consequence: stale evidence
fails; compatibility gates reflect real validation, never unconditional success.
Module/workflow/hook releases remain independently pinned.
