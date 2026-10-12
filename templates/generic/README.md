# Repository starter

This is the single generic template source, not a published GitHub template.
Before creation, materialize `.in` files using reviewed values and establish
CODEOWNERS. Record the observed source SHA, generated initial commit, bootstrap
PR/commit, workflow pins, and hook pins in the consuming configuration repository.

For exact reproducibility, bootstrap these tracked files from a specific source
commit through a PR. Do not make Terraform own them.

Local hooks: install pre-commit, then run `pre-commit install` and
`pre-commit run --all-files`. CI remains the enforcement boundary.
