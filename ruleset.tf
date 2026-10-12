resource "github_repository_ruleset" "this" {
  for_each    = var.repository_ruleset == null ? {} : { managed = var.repository_ruleset }
  repository  = github_repository.this.name
  name        = each.value.name
  target      = "branch"
  enforcement = each.value.enforcement

  conditions {
    ref_name {
      include = ["~DEFAULT_BRANCH"]
      exclude = []
    }
  }
  dynamic "bypass_actors" {
    for_each = each.value.bypass_actors
    content {
      actor_type  = bypass_actors.value.actor_type
      actor_id    = bypass_actors.value.actor_id
      bypass_mode = bypass_actors.value.bypass_mode
    }
  }
  rules {
    deletion         = true
    non_fast_forward = true
    pull_request {
      allowed_merge_methods             = var.merge_methods
      required_approving_review_count   = each.value.required_approving_review_count
      require_code_owner_review         = each.value.require_code_owner_review
      dismiss_stale_reviews_on_push     = each.value.dismiss_stale_reviews_on_push
      require_last_push_approval        = each.value.require_last_push_approval
      required_review_thread_resolution = each.value.required_review_thread_resolution
    }
    dynamic "required_status_checks" {
      for_each = length(each.value.required_checks) == 0 ? [] : [each.value]
      content {
        strict_required_status_checks_policy = required_status_checks.value.strict_required_status_checks
        dynamic "required_check" {
          for_each = required_status_checks.value.required_checks
          content {
            context        = required_check.key
            integration_id = required_check.value.integration_id
          }
        }
      }
    }
  }
  lifecycle {
    precondition {
      condition     = each.value.enforcement != "active" || length(each.value.required_checks) > 0
      error_message = "Active v1 protection requires at least one observed deterministic check."
    }
  }
  depends_on = [github_branch_default.this]
}
