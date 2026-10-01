resource "azurerm_resource_group" "this" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.resource_group_tags
}

resource "azurerm_storage_account" "this" {
  name                = var.storage_account_name
  resource_group_name = azurerm_resource_group.this.name
  location            = var.location

  account_kind             = "StorageV2"
  account_tier             = "Standard"
  account_replication_type = "LRS"

  https_traffic_only_enabled       = true
  min_tls_version                  = "TLS1_2"
  allow_nested_items_to_be_public  = false
  cross_tenant_replication_enabled = false
  public_network_access            = "Disabled"

  tags = var.storage_account_tags
}
