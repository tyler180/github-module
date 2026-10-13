# Secret scanning and scope

Shared hygiene CI now includes mandatory Gitleaks 8.30.1. The Linux release archive
is verified against its fixed SHA256 before execution. CI scans full fetched Git
history with central built-in rules, redacts output, and rejects scanner errors.
Candidate `.gitleaks.toml`, `.gitleaksignore`, and `gitleaks:allow` comments cannot
suppress the central scan. A scan failure, cancellation, or skip fails platform-ci.

The generic pre-commit configuration includes the shared `secret-scan` hook. It
scans staged changes and requires Gitleaks 8.30.1 installed locally. Install that
exact release from https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1 and
verify its published checksum. No automatic local downloads or global install are
performed. `pre-commit install` remains developer onboarding; CI enforces checks.

Tests use synthetic tokens in temporary repositories. They verify clean history,
staged detections, historical detections after deletion, redaction, and rejection
of candidate suppressions. Do not commit real credentials to test the scanner.

Secret scanning is pattern detection, not proof that code is safe. Dependency
vulnerability scanning (for example govulncheck), Terraform/IaC vulnerability
scanning, and licensed GitHub security features remain follow-on decisions. This
release does not claim those capabilities. Exceptions require a reviewed change
to central tooling; there is no caller-controlled baseline/allowlist parameter.
