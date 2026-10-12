# ADR 011: Trusted transition policy

Status: local validator/fixtures implemented; live adapter not enabled.

Decision: trusted base inventory plus last successful accepted record, proposed
inventory, independent evidence, and full saved-plan inspection. Same stage or one
forward step only. Nonzero policy failures block corresponding deployment; manual
and rerun paths cannot bypass. Alternative: desired variable/evidence file as proof.
Consequence: partial failure does not advance record; fresh plan resumes safely.
Receipts bind bytes/revisions but offline mode cannot authorize deployment.
