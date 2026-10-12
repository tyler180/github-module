resource "github_team_repository" "this" {
  for_each   = var.team_permissions
  repository = github_repository.this.name
  team_id    = each.key
  permission = each.value
}
