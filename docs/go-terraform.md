# Opt-in Go + Terraform starter

Use the existing Go starter with these additional arguments:

```sh
python3 scripts/render-template.py \
  --destination /tmp/new-go-terraform-starter \
  --code-owner tyler180 \
  --workflow-ref v2.2.0-rc.1 --hook-ref v2.2.0-rc.1 \
  --go-version 1.26.5 --go-module github.com/tyler180/new-repo \
  --terraform-version 1.15.0 \
  --terraform-workflow-ref af06ebbdfe069ce16beee12d86c9ee03591592d7
```

The Terraform revision above contains the existing shared plan/deploy caller
contracts. Independently review the revision you choose. The renderer accepts an
explicit patch Terraform version, a full workflow SHA, and an optional relative
`--terraform-directory` (default `terraform`). It adds two disabled AWS workflow
callers and a setup guide alongside the existing Go starter, plus Terraform runtime
and state ignore patterns. It does not guess cloud resources or backend configuration.
Generic and ordinary Go starter output remain unchanged when not opted in.

For an existing repo, stage only the additive files:

```sh
python3 scripts/render-template.py \
  --destination /tmp/existing-go-terraform-overlay --workflows-only \
  --terraform-version 1.15.0 \
  --terraform-workflow-ref af06ebbdfe069ce16beee12d86c9ee03591592d7
```

This needs no Go version, module, owners or hook selection because it never renders
Go source, CI, CODEOWNERS or hooks. Both modes refuse an existing destination. Review
the overlay and add it through a PR; manually reconcile existing filenames. Add
Terraform state, runtime and private variable-file ignore patterns where needed.

PR plans require repository variable `TERRAFORM_ENABLED=true`. Manual deployments
also require `TERRAFORM_DEPLOY_ENABLED=true`. The generated guide lists role,
state, environment and region variables and the OIDC/backend setup. Go/Dockerfile
changes are included in PR triggers because Terraform may build application images.
Plans skip forks; deployment accepts only manual runs on the default branch.
The environment must be protected before enabling deployment.

`github-infra` can store the opt-in in each entry's `terraform_starter` object and
render it with `scripts/render-terraform-starter.py`. The published automatic Go
bootstrap remains separate; it does not consume this new metadata until a reviewed
shared-bootstrap release implements it. Existing repo adoption requires import and
a no-change plan using observed settings; adding source callers does not import it.
