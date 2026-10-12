# Go repository pilot

This example creates a private GitHub repository with Terraform, then adds a
runnable Go starter through a bootstrap PR. Start with the repository creation
steps below.

## Create the repository

Run from this directory in a checkout of github-module. Install Terraform 1.7+
and set `GITHUB_TOKEN` securely in your shell to a token that can create and
administer repositories for your owner. Do not put the token in Terraform files.

```sh
terraform -chdir=terraform init
terraform -chdir=terraform plan -var="owner=YOUR_GITHUB_OWNER" -out=pilot.tfplan
# Review the plan, then create the repository:
terraform -chdir=terraform apply pilot.tfplan
terraform -chdir=terraform output repository_url
```

The default name is `github-go-pilot`; add `-var="name=YOUR_REPOSITORY_NAME"` to
the plan command to change it. The module initializes a README, sets `main` as
the default branch, and configures private visibility and squash merging. It
does not upload the Go source.

This standalone example uses local Terraform state in `terraform/`. Keep that
state securely: it owns the repository. Commit its `.terraform.lock.hcl` after
initialization, but keep state, plans, and credentials out of Git. Do not also
manage the same repository from github-infra. If you want the existing protected
deployment workflow, add this intent to github-infra instead and deploy there;
the commands above demonstrate a separate local deployment.

Next follow [BOOTSTRAP.md](BOOTSTRAP.md) to add the Go files to the new repository.

## Run the Go starter

A small runnable Go command with no external dependencies. Go 1.26 or newer is
required; CI uses the explicit toolchain version in `.github/workflows/ci.yml`.

From this directory:

```sh
go run .
go run . -name Tyler
bash scripts/validate.sh
```

The first command prints `Hello, Go pilot!`; the second prints `Hello, Tyler!`.
An empty or whitespace-only name produces `Hello, world!`.

`make run`, `make test`, and `make check` provide the same local entry points.
Validation checks formatting, runs `go vet`, runs race-enabled tests, and checks
CLI output. The program has no shared concurrent state; the race run is a smoke
check, not proof of concurrent behavior. No `go.sum` is needed without external
module dependencies.

CI calls the published immutable github-workflows `v2.2.0-rc.1` release. It checks
Go formatting, vet and tests plus repository hygiene and redacted secret scanning.
The aggregate check succeeds only when all validation jobs succeed. Observe the
actual check name from a PR before configuring required checks.

Optional local hooks require pre-commit and Gitleaks 8.30.1 on PATH:

```sh
pre-commit install
pre-commit run --all-files
```

To materialize this pilot with your own module path and code owner, follow
[BOOTSTRAP.md](BOOTSTRAP.md). Repository provisioning and later protection are
separate from these source files; Terraform does not manage the Go code.
