# Go language pilot

Use the generic template, then replace its CI caller with `ci.yml.in` in a
reviewed bootstrap PR. Supply the actual Go toolchain version and a reviewed
github-workflows commit containing `go-validate.yml`. No Go module path, account,
backend, or successful execution is assumed. Run the pilot against an actual Go
repository; positive and deliberately failing Go CI runs remain live acceptance.

Retain the generic CODEOWNERS and hook configuration. Observe the emitted check
context from a representative PR before configuring required checks. Workflow
caller names can affect reusable-job context names; do not assume `platform-ci`
alone is the emitted full context.
