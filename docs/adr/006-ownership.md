# ADR 006: Explicit ownership

Status: approved locally; remote lifecycle tests pending.

Decision: defaulted repository inputs are managed; optional resources can be
initially omitted. Removal is distinct from preservation/inheritance. Explicit
state handoff is required to preserve remote policy. No dynamic per-attribute
ownership switches. Alternative: null as universal inherit/preserve. Consequence:
match/import/no-change before management; literal ignore lists and tested migrations.
