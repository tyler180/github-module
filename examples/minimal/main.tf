terraform {
  required_version = ">= 1.7, < 2.0"
  required_providers {
    github = { source = "integrations/github", version = "~> 6.13.0" }
  }
}
variable "owner" {
  type        = string
  description = "Actual GitHub owner, supplied by the consumer."
}
variable "name" { type = string }
provider "github" { owner = var.owner }

module "repository" {
  source = "../.."
  name   = var.name
}
