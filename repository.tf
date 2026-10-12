resource "github_repository" "this" {
  name                   = var.name
  description            = var.description
  homepage_url           = var.homepage_url
  topics                 = var.topics
  visibility             = var.visibility
  auto_init              = var.initialization == "basic"
  archived               = var.archived
  archive_on_destroy     = true
  allow_merge_commit     = contains(var.merge_methods, "merge")
  allow_squash_merge     = contains(var.merge_methods, "squash")
  allow_rebase_merge     = contains(var.merge_methods, "rebase")
  allow_auto_merge       = var.allow_auto_merge
  allow_update_branch    = var.allow_update_branch
  delete_branch_on_merge = var.delete_branch_on_merge
  has_issues             = var.features.issues
  has_discussions        = var.features.discussions
  has_wiki               = var.features.wiki
  has_projects           = var.features.projects

  dynamic "template" {
    for_each = var.template == null ? [] : [var.template]
    content {
      owner                = template.value.owner
      repository           = template.value.repository
      include_all_branches = false
    }
  }

  lifecycle {
    prevent_destroy = true
    # Creation intent is immutable. These computed/unexposed fields have an
    # external owner; nullable inputs are not a dynamic ownership mechanism.
    ignore_changes = [auto_init, template, security_and_analysis, allow_forking, pages, default_branch,
      vulnerability_alerts, is_template, web_commit_signoff_required,
      merge_commit_title, merge_commit_message,
    squash_merge_commit_title, squash_merge_commit_message]
    precondition {
      condition     = (var.initialization == "template") == (var.template != null)
      error_message = "Template selection is required exactly when initialization is template."
    }
    precondition {
      condition     = !var.rename_default_branch || var.default_branch != null
      error_message = "Renaming requires an explicit default branch."
    }
  }
}

resource "github_branch_default" "this" {
  for_each        = var.default_branch == null ? {} : { managed = var.default_branch }
  repository      = github_repository.this.name
  branch          = each.value
  rename          = var.rename_default_branch
  wait_for_rename = var.rename_default_branch
}
