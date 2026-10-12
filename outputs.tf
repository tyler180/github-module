output "name" { value = github_repository.this.name }
output "full_name" { value = github_repository.this.full_name }
output "repository_id" { value = github_repository.this.repo_id }
output "node_id" { value = github_repository.this.node_id }
output "html_url" { value = github_repository.this.html_url }
output "ssh_clone_url" { value = github_repository.this.ssh_clone_url }
output "http_clone_url" { value = github_repository.this.http_clone_url }

output "managed_ruleset_id" {
  value = try(github_repository_ruleset.this["managed"].ruleset_id, null)
}

output "managed_components" {
  description = "Configured ownership, not evidence of operational readiness."
  value = {
    repository           = true
    default_branch       = var.default_branch != null
    team_grants          = keys(var.team_permissions)
    actions_policy       = var.actions_policy != null
    workflow_permissions = var.workflow_permissions != null
    repository_ruleset   = var.repository_ruleset != null
  }
}
