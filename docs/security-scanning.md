# Secret scanning and scope

Shared hygiene CI now includes mandatory Gitleaks 8.30.1. The Linux release archive
is verified against its fixed SHA256 before execution. CI scans full fetched Git
history with central built-in rules, redacts output, and rejects scanner errors.
Candidate `.gitleaks.toml`, `.gitleaksignore`, and `gitleaks:allow` comments cannot
suppress the central scan. A scan failure, cancellation, or skip fails platform-ci.

The generic pre-commit configuration includes shared staged scanning and a manual
scanner preparation hook. New Go starters provide `make setup`, which installs
pre-commit 4.3.0 in an ignored project-local .venv, registers hooks, and prepares
Gitleaks automatically. The shared scanner downloads a pinned release for
macOS/Linux Intel/ARM, verifies archive and binary SHA256 values, and verifies the
cached binary before every use. It never executes a Gitleaks binary from PATH.
Downloads, checksum failures and unsupported systems fail closed. The first use
needs network access; verified cached use works offline. CI remains mandatory.

Existing repositories need a reviewed source upgrade to receive the new hook pin
and setup files. Do not rerun initial bootstrap to overwrite an application.
