terraform {
  required_version = ">= 1.7, < 2.0"
  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 6.13.0"
    }
  }
}

variable "owner" {
  description = "GitHub user or organization that will own the pilot."
  type        = string
}

variable "name" {
  description = "Name of the new Go pilot repository."
  type        = string
  default     = "github-go-pilot"
}

provider "github" {
  owner = var.owner
  # Authenticate using GITHUB_TOKEN in the environment.
}

module "repository" {
  source = "git::https://github.com/tyler180/github-module.git?ref=v0.1.0-rc.2"

  name                   = var.name
  description            = "Go pilot created with the GitHub repository Terraform module."
  visibility             = "private"
  initialization         = "basic"
  default_branch         = "main"
  rename_default_branch  = true
  topics                 = ["go", "pilot"]
  merge_methods          = ["squash"]
  delete_branch_on_merge = true
}

output "repository_url" {
  value = module.repository.html_url
}

output "repository_id" {
  value = module.repository.repository_id
}
