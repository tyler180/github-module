# Go pilot

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
