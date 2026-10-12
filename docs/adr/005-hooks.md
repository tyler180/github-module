# ADR 005: Shared pre-commit hooks

Status: approved locally; actual installation pending.

Decision: pinned shared hygiene hook and equivalent CI validation. Alternative:
native Git hooks/core.hooksPath installers. Consequence: predictable revisions and
one shared definition; developer installation is optional feedback, never the
mandatory server-side boundary. No Terraform workstation management.
