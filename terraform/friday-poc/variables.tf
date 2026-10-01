variable "effective_metadata_path" {
  description = "Path to the V3-validated effective-metadata JSON artifact."
  type        = string

  validation {
    condition = try(
      fileexists(var.effective_metadata_path) &&
      jsondecode(file(var.effective_metadata_path)).schema_version == "1.0" &&
      jsondecode(file(var.effective_metadata_path)).contract.name == "friday-vertical-slice" &&
      jsondecode(file(var.effective_metadata_path)).contract.version == "0.1.0" &&
      jsondecode(file(var.effective_metadata_path)).context.capability.id == "azure-application-foundation" &&
      jsondecode(file(var.effective_metadata_path)).context.capability.version == "v0" &&
      length(trimspace(jsondecode(file(var.effective_metadata_path)).context.deployment.provider)) > 0 &&
      length(trimspace(jsondecode(file(var.effective_metadata_path)).context.deployment.location)) > 0,
      false
    )
    error_message = "effective_metadata_path must reference a compatible V3.1 Friday effective-metadata artifact."
  }

  validation {
    condition = try(
      length([
        for resource in jsondecode(file(var.effective_metadata_path)).resources :
        resource if resource.type == "Microsoft.Resources/resourceGroups"
      ]) == 1 &&
      length([
        for resource in jsondecode(file(var.effective_metadata_path)).resources :
        resource if resource.type == "Microsoft.Storage/storageAccounts"
      ]) == 1,
      false
    )
    error_message = "effective metadata must contain exactly one Resource Group and one Storage Account record."
  }

  validation {
    condition = try(
      alltrue([
        for resource in jsondecode(file(var.effective_metadata_path)).resources :
        can(tomap(resource.effective_tags))
      ]) &&
      alltrue(flatten([
        for resource in jsondecode(file(var.effective_metadata_path)).resources : [
          resource.effective_tags.provider == jsondecode(file(var.effective_metadata_path)).context.deployment.provider,
          resource.effective_tags.location == jsondecode(file(var.effective_metadata_path)).context.deployment.location
          ] if contains([
            "Microsoft.Resources/resourceGroups",
            "Microsoft.Storage/storageAccounts"
        ], resource.type)
      ])),
      false
    )
    error_message = "applicable resource tag maps must be strings and must match deployment provider/location context."
  }
}

variable "subscription_id" {
  description = "Existing Azure subscription targeted by this deployment."
  type        = string

  validation {
    condition = can(regex(
      "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
      var.subscription_id
    ))
    error_message = "subscription_id must be a UUID."
  }
}
