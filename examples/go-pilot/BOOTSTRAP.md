# Bootstrap a Go repository

First create the repository using the [Terraform example](README.md#create-the-repository),
or the github-infra deployment workflow. Then, from the github-module checkout,
generate into a new destination:

```sh
python3 scripts/render-template.py \
  --destination /tmp/github-go-pilot \
  --code-owner tyler180 \
  --workflow-ref v2.2.0-rc.1 \
  --hook-ref v2.2.0-rc.1 \
  --go-version 1.26.5 \
  --go-module github.com/tyler180/github-go-pilot
cd /tmp/github-go-pilot
bash scripts/validate.sh
```

The renderer creates the complete module, program, tests, validation script,
Makefile, CI caller, CODEOWNERS, hook configuration and ignore file. It refuses
an existing destination. The legacy --workflow-sha and --hook-sha options still
work; references must be full commits or exact immutable release tags, not main
or a floating major alias. Use a release that contains Go validation and hooks.

The source example is itself runnable with module path example.com/github-go-pilot.
Replace that path via --go-module when creating a real repository. Match Go's
major/minor version to the generated module's minimum version.

For the provisioning pilot, add repository intent at create stage in github-infra,
review the full-root plan, and create it through the approved deployment workflow.
Then add these files in a reviewed bootstrap PR. Retain the source release/commit,
initial commit and merged PR as provenance. Do not move the inventory to bootstrap
or protect until live authorization for those stages has been implemented.

After publishing the bootstrap PR, verify a successful run and a deliberately
failing test/formatting change. Observe the actual aggregate check name before
using it for branch protection. Local tests and the example's CI do not prove
live enforcement on the newly provisioned repository.

Clone the newly created repository, create a bootstrap branch, and copy the
generated starter into it (including hidden files, excluding Terraform state):

```sh
git clone https://github.com/YOUR_GITHUB_OWNER/github-go-pilot.git /tmp/go-pilot-checkout
cd /tmp/go-pilot-checkout
git switch -c bootstrap-go
cp -R /tmp/github-go-pilot/. .
bash scripts/validate.sh
git add .
git commit -m "Bootstrap Go pilot"
git push -u origin bootstrap-go
gh pr create --title "Bootstrap Go pilot" --body "Add the Go starter and shared CI."
```

Use your actual owner and repository name in both the renderer's `--go-module`
and clone URL. The renderer deliberately excludes the Terraform provisioning
folder from the generated application starter. Review and merge the bootstrap
PR after CI succeeds.
