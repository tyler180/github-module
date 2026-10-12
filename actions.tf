resource "github_actions_repository_permissions" "this" {
  for_each             = var.actions_policy == null ? {} : { managed = var.actions_policy }
  repository           = github_repository.this.name
  enabled              = each.value.enabled
  allowed_actions      = each.value.allowed_actions
  sha_pinning_required = each.value.sha_pinning_required

  dynamic "allowed_actions_config" {
    for_each = each.value.selected == null ? [] : [each.value.selected]
    content {
      github_owned_allowed = allowed_actions_config.value.github_owned_allowed
      verified_allowed     = allowed_actions_config.value.verified_allowed
      patterns_allowed     = allowed_actions_config.value.patterns_allowed
    }
  }
  lifecycle {
    precondition {
      condition     = (each.value.allowed_actions == "selected") == (each.value.selected != null)
      error_message = "Selected actions policy requires exactly one explicit selected configuration."
    }
  }
}

resource "github_workflow_repository_permissions" "this" {
  for_each                         = var.workflow_permissions == null ? {} : { managed = var.workflow_permissions }
  repository                       = github_repository.this.name
  default_workflow_permissions     = each.value.default_workflow_permissions
  can_approve_pull_request_reviews = each.value.can_approve_pull_request_reviews
}
