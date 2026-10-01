output "resource_group_id" {
  description = "Azure resource ID of the Resource Group."
  value       = module.foundation.resource_group_id
}

output "resource_group_name" {
  description = "Name of the Resource Group."
  value       = module.foundation.resource_group_name
}

output "storage_account_id" {
  description = "Azure resource ID of the Storage Account."
  value       = module.foundation.storage_account_id
}

output "storage_account_name" {
  description = "Name of the Storage Account."
  value       = module.foundation.storage_account_name
}

output "location" {
  description = "Azure deployment location from platform deployment context."
  value       = module.foundation.location
}

output "resource_ids" {
  description = "Resource IDs for later observed-state and tag queries."
  value = {
    resource_group  = module.foundation.resource_group_id
    storage_account = module.foundation.storage_account_id
  }
}

output "effective_tags" {
  description = "Expected effective tags by resource for later observed-state comparison."
  value = {
    resource_group  = module.foundation.resource_group_tags
    storage_account = module.foundation.storage_account_tags
  }
}
