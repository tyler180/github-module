variable "owner" {
  description = "Actual owner; no account details are assumed."
  type        = string
}
variable "inventory_file" {
  description = "JSON inventory, not proof of verification. No backend or deployment caller is supplied."
  type        = string
  default     = "repositories.json"
}
provider "github" { owner = var.owner }

locals {
  inventory = jsondecode(file("${path.module}/${var.inventory_file}"))
  stages    = ["create", "bootstrap", "verify", "protect", "grant"]
}

# No provider operations: this is a structural guard, not historical proof.
resource "terraform_data" "contract" {
  input = local.inventory
  lifecycle {
    precondition {
      condition     = local.inventory.schema_version == 1 && alltrue([for repo in values(local.inventory.repositories) : contains(local.stages, repo.stage)])
      error_message = "Use inventory schema 1 and a recognized onboarding stage."
    }
    precondition {
      condition = alltrue([for repo in values(local.inventory.repositories) :
        !contains(["protect", "grant"], repo.stage) || try(length(repo.required_checks) > 0, false)
      ])
      error_message = "Protect/grant requires a configured deterministic check contract."
    }
    precondition {
      condition = alltrue([for repo in values(local.inventory.repositories) :
        length(setintersection(toset(keys(try(repo.provisioning_teams, {}))), toset(keys(try(repo.developer_teams, {}))))) == 0
      ])
      error_message = "Provisioning and developer team identities must be disjoint."
    }
  }
}

module "repositories" {
  for_each = local.inventory.repositories
  source   = "../.."

  name                   = each.value.name
  initialization         = try(each.value.initialization, "basic")
  template               = try(each.value.template, null)
  description            = try(each.value.description, "")
  homepage_url           = try(each.value.homepage_url, "")
  topics                 = try(each.value.topics, [])
  visibility             = try(each.value.visibility, "private")
  merge_methods          = try(each.value.merge_methods, ["squash"])
  delete_branch_on_merge = try(each.value.delete_branch_on_merge, true)
  allow_auto_merge       = try(each.value.allow_auto_merge, false)
  allow_update_branch    = try(each.value.allow_update_branch, true)
  features               = try(each.value.features, {})
  archived               = try(each.value.archived, false)
  default_branch         = try(each.value.default_branch, null)
  rename_default_branch  = try(each.value.rename_default_branch, false)
  actions_policy         = try(each.value.actions_policy, null)
  workflow_permissions   = try(each.value.workflow_permissions, null)
  team_permissions = merge(
    try(each.value.provisioning_teams, {}),
    each.value.stage == "grant" ? try(each.value.developer_teams, {}) : {}
  )
  repository_ruleset = {
    enforcement     = contains(["protect", "grant"], each.value.stage) ? "active" : "disabled"
    required_checks = try(each.value.required_checks, {})
  }
  depends_on = [terraform_data.contract]
}

output "repositories" {
  value = { for key, repo in module.repositories : key => {
    repository_id = repo.repository_id
    full_name     = repo.full_name
    html_url      = repo.html_url
  } }
}
