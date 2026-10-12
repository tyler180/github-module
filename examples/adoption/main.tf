terraform {
  required_version = ">= 1.7, < 2.0"
  required_providers {
    github = { source = "integrations/github", version = "~> 6.13.0" }
  }
}
variable "owner" { type = string }
variable "name" { type = string }
# Supply EVERY managed setting to match the existing repository before import.
variable "existing" {
  type = object({
    description            = string
    homepage_url           = string
    topics                 = set(string)
    visibility             = string
    merge_methods          = set(string)
    delete_branch_on_merge = bool
    archived               = bool
    allow_auto_merge       = bool
    allow_update_branch    = bool
    features = object({
      issues = bool, discussions = bool, wiki = bool, projects = bool
    })
  })
}
provider "github" { owner = var.owner }
variable "components" {
  description = "Only include subordinate resources intentionally adopted; match their current values, then import each."
  type        = any
  default     = {}
}
module "repository" {
  source                 = "../.."
  name                   = var.name
  initialization         = "none"
  description            = var.existing.description
  homepage_url           = var.existing.homepage_url
  topics                 = var.existing.topics
  visibility             = var.existing.visibility
  merge_methods          = var.existing.merge_methods
  delete_branch_on_merge = var.existing.delete_branch_on_merge
  archived               = var.existing.archived
  allow_auto_merge       = var.existing.allow_auto_merge
  allow_update_branch    = var.existing.allow_update_branch
  features               = var.existing.features
  default_branch         = try(var.components.default_branch, null)
  team_permissions       = try(var.components.team_permissions, {})
  actions_policy         = try(var.components.actions_policy, null)
  workflow_permissions   = try(var.components.workflow_permissions, null)
  repository_ruleset     = try(var.components.repository_ruleset, null)
}
import {
  to = module.repository.github_repository.this
  id = var.name
}
