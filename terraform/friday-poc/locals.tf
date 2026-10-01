locals {
  effective_metadata = jsondecode(file(var.effective_metadata_path))

  resources_by_type = {
    for resource in local.effective_metadata.resources :
    resource.type => resource
  }

  resource_group_metadata  = local.resources_by_type["Microsoft.Resources/resourceGroups"]
  storage_account_metadata = local.resources_by_type["Microsoft.Storage/storageAccounts"]

  deployment_location = local.effective_metadata.context.deployment.location

  resource_group_tags  = tomap(local.resource_group_metadata.effective_tags)
  storage_account_tags = tomap(local.storage_account_metadata.effective_tags)

  service_name_token = replace(local.resource_group_tags["service"], "/[^a-z0-9]/", "")
  environment_token  = replace(local.resource_group_tags["env"], "/[^a-z0-9]/", "")

  naming_hash = substr(sha256(join(":", [
    var.subscription_id,
    local.effective_metadata.context.capability.id,
    local.effective_metadata.context.capability.version,
    local.resource_group_tags["service"],
    local.resource_group_tags["env"],
    local.deployment_location
  ])), 0, 10)

  resource_group_name = join("-", [
    "rg",
    local.resource_group_tags["service"],
    local.resource_group_tags["env"],
    local.deployment_location
  ])

  storage_account_name = join("", [
    "st",
    substr(local.service_name_token, 0, min(8, length(local.service_name_token))),
    substr(local.environment_token, 0, min(3, length(local.environment_token))),
    local.naming_hash
  ])
}
