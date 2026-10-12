# ADR 004: Pinned workflows and protected callers

Status: approved for local implementation; integration pending.

Decision: pinned github-workflows calls, deterministic aggregate gate, CODEOWNER
review for callers/CODEOWNERS/validation inputs. Existing deployment behavior is
unchanged. Alternative: copied CI or mutable refs. Consequence: pin updates use PRs;
check names do not prove implementation identity. Dummy-substitution live test is
mandatory. Stronger trust needs centrally required validation.
