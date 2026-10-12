# ADR 008: Adoption in repository core

Status: example implemented; live no-change import pending.

Decision: match owned repository and selected subordinate settings, import every
managed object, then require no-change plan before defaults. Advanced migration and
retirement are later. Alternative: overwrite/create during adoption. Consequence:
history/access remain intentional; ordinary policy rejects unreviewed imports,
replacement, drift, and destruction.
