terraform {
  required_providers {
    github = { source = "integrations/github", version = "~> 6.13.0" }
  }
}
variable "owner" { type = string }
variable "name" { type = string }
variable "template_owner" { type = string }
variable "template_repository" { type = string }
provider "github" { owner = var.owner }
module "repository" {
  source         = "../.."
  name           = var.name
  initialization = "template"
  template = {
    owner      = var.template_owner
    repository = var.template_repository
  }
}
