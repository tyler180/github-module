variable "name" {
  description = "Repository name; owner is configured on the root provider."
  type        = string
  validation {
    condition     = can(regex("^[A-Za-z0-9_.-]{1,100}$", var.name))
    error_message = "Use 1-100 ASCII letters, digits, dots, underscores, or hyphens."
  }
}

variable "description" {
  description = "Managed description; omission clears it."
  type        = string
  default     = ""
  nullable    = false
}

variable "homepage_url" {
  description = "Managed homepage URL; omission clears it."
  type        = string
  default     = ""
  nullable    = false
}

variable "topics" {
  description = "Complete managed topic set; omission clears it."
  type        = set(string)
  default     = []
  nullable    = false
}

variable "visibility" {
  description = "Explicit visibility. Internal requires an eligible enterprise account."
  type        = string
  default     = "private"
  nullable    = false
  validation {
    condition     = contains(["private", "public", "internal"], var.visibility)
    error_message = "Visibility must be private, public, or internal."
  }
}

variable "initialization" {
  description = "Creation intent: basic, template, or none (adoption/exact-source bootstrap)."
  type        = string
  default     = "basic"
  nullable    = false
  validation {
    condition     = contains(["basic", "template", "none"], var.initialization)
    error_message = "Initialization must be basic, template, or none."
  }
}

variable "template" {
  description = "Creation-time template selection. No source SHA/ref is supported."
  type = object({
    owner      = string
    repository = string
  })
  default = null
  validation {
    condition     = var.template == null ? true : (length(var.template.owner) > 0 && length(var.template.repository) > 0)
    error_message = "Template owner and repository must be nonempty."
  }
}

variable "merge_methods" {
  description = "Managed permitted merge methods."
  type        = set(string)
  default     = ["squash"]
  nullable    = false
  validation {
    condition     = length(var.merge_methods) > 0 && length(setsubtract(var.merge_methods, ["merge", "squash", "rebase"])) == 0
    error_message = "Select at least one of merge, squash, or rebase."
  }
}

variable "delete_branch_on_merge" {
  description = "Managed automatic deletion of merged head branches."
  type        = bool
  default     = true
  nullable    = false
}

variable "allow_auto_merge" {
  description = "Managed auto-merge enablement; adoption must match the current value."
  type        = bool
  default     = false
  nullable    = false
}

variable "allow_update_branch" {
  description = "Managed update-branch suggestion; adoption must match the current value."
  type        = bool
  default     = true
  nullable    = false
}

variable "features" {
  description = "Managed repository features, including explicit defaults for omitted members."
  type = object({
    issues      = optional(bool, true)
    discussions = optional(bool, false)
    wiki        = optional(bool, false)
    projects    = optional(bool, false)
  })
  default  = {}
  nullable = false
}

variable "archived" {
  description = "Managed archive state; retirement requires a separately reviewed lifecycle change."
  type        = bool
  default     = false
  nullable    = false
}

variable "default_branch" {
  description = "Null initially leaves default-branch selection unmanaged; removal later requires handoff."
  type        = string
  default     = null
  validation {
    condition     = var.default_branch == null ? true : length(var.default_branch) > 0
    error_message = "Default branch must be nonempty when supplied."
  }
}

variable "rename_default_branch" {
  description = "Explicit default-branch rename. Normally false; adoption must not rename implicitly."
  type        = bool
  default     = false
  nullable    = false
}

variable "team_permissions" {
  description = "Non-authoritative grants keyed by existing team ID or slug. Removing a key revokes its grant."
  type        = map(string)
  default     = {}
  nullable    = false
  validation {
    condition     = alltrue([for permission in values(var.team_permissions) : contains(["pull", "triage", "push", "maintain", "admin"], permission)])
    error_message = "Use built-in team permissions: pull, triage, push, maintain, or admin."
  }
}

variable "actions_policy" {
  description = "Null initially omits ownership. Removing managed policy resets remote settings unless explicitly handed off."
  type = object({
    enabled              = bool
    allowed_actions      = string
    sha_pinning_required = bool
    selected = optional(object({
      github_owned_allowed = bool
      verified_allowed     = bool
      patterns_allowed     = set(string)
    }))
  })
  default = null
  validation {
    condition     = var.actions_policy == null ? true : contains(["all", "local_only", "selected"], var.actions_policy.allowed_actions)
    error_message = "Allowed actions must be all, local_only, or selected."
  }
}

variable "workflow_permissions" {
  description = "Null initially omits token-default ownership; enabled objects specify both fields explicitly."
  type = object({
    default_workflow_permissions     = string
    can_approve_pull_request_reviews = bool
  })
  default = null
  validation {
    condition     = var.workflow_permissions == null ? true : contains(["read", "write"], var.workflow_permissions.default_workflow_permissions)
    error_message = "Default workflow permissions must be read or write."
  }
}

variable "repository_ruleset" {
  description = "Optional default-branch ruleset. Null initially omits ownership; removal deletes it."
  type = object({
    name                              = optional(string, "platform-default-branch")
    enforcement                       = string
    required_approving_review_count   = optional(number, 1)
    require_code_owner_review         = optional(bool, true)
    dismiss_stale_reviews_on_push     = optional(bool, true)
    require_last_push_approval        = optional(bool, true)
    required_review_thread_resolution = optional(bool, true)
    strict_required_status_checks     = optional(bool, true)
    required_checks = map(object({
      integration_id = optional(number)
    }))
    bypass_actors = optional(map(object({
      actor_type  = string
      actor_id    = optional(number)
      bypass_mode = string
    })), {})
  })
  default = null
  validation {
    condition     = var.repository_ruleset == null ? true : contains(["disabled", "active"], var.repository_ruleset.enforcement)
    error_message = "V1 supports disabled or active rulesets."
  }
  validation {
    condition = var.repository_ruleset == null ? true : alltrue([
      for context, check in var.repository_ruleset.required_checks :
      length(trimspace(context)) > 0 && (check.integration_id == null ? true : check.integration_id > 0 && floor(check.integration_id) == check.integration_id)
    ])
    error_message = "Check contexts must be nonempty; explicitly selected integration IDs must be positive integers."
  }
  validation {
    condition     = var.repository_ruleset == null ? true : (var.repository_ruleset.required_approving_review_count >= 0 && var.repository_ruleset.required_approving_review_count <= 6 && floor(var.repository_ruleset.required_approving_review_count) == var.repository_ruleset.required_approving_review_count)
    error_message = "Review count must be an integer from 0 through 6."
  }
  validation {
    condition = var.repository_ruleset == null ? true : alltrue([
      for actor in values(var.repository_ruleset.bypass_actors) :
      contains(["Team", "Integration", "OrganizationAdmin", "RepositoryRole"], actor.actor_type) &&
      contains(["always", "pull_request"], actor.bypass_mode) &&
      (actor.actor_type == "OrganizationAdmin" ? actor.actor_id == null : try(actor.actor_id > 0, false))
    ])
    error_message = "Use a supported bypass actor with a positive ID (except OrganizationAdmin) and explicit mode."
  }
}
