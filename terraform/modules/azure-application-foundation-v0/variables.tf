variable "resource_group_name" {
  description = "Platform-generated Resource Group name."
  type        = string

  validation {
    condition = (
      length(var.resource_group_name) >= 1 &&
      length(var.resource_group_name) <= 90 &&
      !endswith(var.resource_group_name, ".")
    )
    error_message = "resource_group_name must be 1-90 characters and must not end with a period."
  }
}

variable "storage_account_name" {
  description = "Platform-generated globally unique Storage Account name."
  type        = string

  validation {
    condition = (
      length(var.storage_account_name) >= 3 &&
      length(var.storage_account_name) <= 24 &&
      can(regex("^[a-z0-9]+$", var.storage_account_name))
    )
    error_message = "storage_account_name must be 3-24 lowercase alphanumeric characters."
  }
}

variable "location" {
  description = "Azure deployment location selected by platform configuration."
  type        = string

  validation {
    condition     = length(trimspace(var.location)) > 0
    error_message = "location must be a non-empty Azure location."
  }
}

variable "resource_group_tags" {
  description = "Validated effective tags for the Resource Group."
  type        = map(string)
}

variable "storage_account_tags" {
  description = "Validated effective tags for the Storage Account."
  type        = map(string)
}
