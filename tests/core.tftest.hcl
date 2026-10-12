mock_provider "github" {}

variables { name = "offline-fixture" }

run "private_squash_defaults" {
  command = plan
  assert {
    condition     = github_repository.this.visibility == "private" && github_repository.this.auto_init
    error_message = "New basic repositories must be explicitly private and initialized."
  }
  assert {
    condition     = github_repository.this.allow_squash_merge && !github_repository.this.allow_merge_commit && !github_repository.this.allow_rebase_merge
    error_message = "Default merge policy must be squash only."
  }
  assert {
    condition     = length(github_repository_ruleset.this) == 0 && length(github_team_repository.this) == 0 && length(github_actions_repository_permissions.this) == 0 && length(github_workflow_repository_permissions.this) == 0
    error_message = "Omitted components must not be created."
  }
}

run "adoption_intent" {
  command = plan
  variables {
    initialization = "none"
    visibility     = "public"
    description    = "Existing configuration fixture"
    merge_methods  = ["merge", "squash", "rebase"]
  }
  assert {
    condition     = !github_repository.this.auto_init && length(github_branch_default.this) == 0
    error_message = "Adoption must not initialize or implicitly rename a branch."
  }
  assert {
    condition     = github_repository.this.allow_merge_commit && github_repository.this.allow_rebase_merge
    error_message = "Explicit existing merge settings must override new-repository defaults."
  }
}

run "template_creation" {
  command = plan
  variables {
    initialization = "template"
    template       = { owner = "fixture-owner", repository = "fixture-template" }
  }
  assert {
    condition     = !github_repository.this.auto_init && !github_repository.this.template[0].include_all_branches
    error_message = "Template mode must not initialize independently or copy unrelated branches."
  }
}

run "invalid_name" {
  command = plan
  variables { name = "invalid/name" }
  expect_failures = [var.name]
}
run "empty_merge_methods" {
  command = plan
  variables { merge_methods = [] }
  expect_failures = [var.merge_methods]
}
run "missing_template" {
  command = plan
  variables { initialization = "template" }
  expect_failures = [github_repository.this]
}
run "rename_without_branch" {
  command = plan
  variables { rename_default_branch = true }
  expect_failures = [github_repository.this]
}
