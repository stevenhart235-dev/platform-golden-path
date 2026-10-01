output "resource_group_id" {
  description = "Azure resource ID of the Resource Group."
  value       = azurerm_resource_group.this.id
}

output "resource_group_name" {
  description = "Name of the Resource Group."
  value       = azurerm_resource_group.this.name
}

output "resource_group_tags" {
  description = "Effective tags applied to the Resource Group."
  value       = azurerm_resource_group.this.tags
}

output "storage_account_id" {
  description = "Azure resource ID of the Storage Account."
  value       = azurerm_storage_account.this.id
}

output "storage_account_name" {
  description = "Name of the Storage Account."
  value       = azurerm_storage_account.this.name
}

output "storage_account_tags" {
  description = "Effective tags applied to the Storage Account."
  value       = azurerm_storage_account.this.tags
}

output "location" {
  description = "Azure deployment location."
  value       = azurerm_resource_group.this.location
}
