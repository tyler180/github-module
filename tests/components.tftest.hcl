mock_provider "github" {}
variables { name = "offline-fixture" }

run "managed_components" {
  command = plan
  variables {
    team_permissions = { fixture-team = "maintain" }
    workflow_permissions = {
      default_workflow_permissions     = "read"
      can_approve_pull_request_reviews = false
    }
    actions_policy = {
      enabled = true, allowed_actions = "selected", sha_pinning_required = true
      selected = {
        github_owned_allowed = false, verified_allowed = false
        patterns_allowed     = ["fixture-owner/github-workflows@*"]
      }
    }
    repository_ruleset = {
      enforcement     = "active"
      required_checks = { "platform-ci" = {} }
    }
  }
  assert {
    condition     = github_team_repository.this["fixture-team"].permission == "maintain"
    error_message = "Explicit team grant must be preserved."
  }
  assert {
    condition     = github_workflow_repository_permissions.this["managed"].default_workflow_permissions == "read" && !github_workflow_repository_permissions.this["managed"].can_approve_pull_request_reviews
    error_message = "Token policy must match explicit configuration."
  }
  assert {
    condition     = github_repository_ruleset.this["managed"].conditions[0].ref_name[0].include == tolist(["~DEFAULT_BRANCH"])
    error_message = "Ruleset must target only the default branch."
  }
  assert {
    condition     = github_repository_ruleset.this["managed"].rules[0].deletion && github_repository_ruleset.this["managed"].rules[0].non_fast_forward && github_repository_ruleset.this["managed"].rules[0].pull_request[0].require_code_owner_review
    error_message = "Baseline protections must be explicit."
  }
}
run "selected_without_config" {
  command = plan
  variables {
    actions_policy = { enabled = true, allowed_actions = "selected", sha_pinning_required = true }
  }
  expect_failures = [github_actions_repository_permissions.this]
}
run "active_without_checks" {
  command = plan
  variables { repository_ruleset = { enforcement = "active", required_checks = {} } }
  expect_failures = [github_repository_ruleset.this]
}
run "invalid_permission" {
  command = plan
  variables { team_permissions = { fixture-team = "owner" } }
  expect_failures = [var.team_permissions]
}
