mock_provider "azurerm" {}

run "resources_and_defaults" {
  command = plan

  variables {
    resource_group_name  = "rg-headshot-api-dev-centralus"
    storage_account_name = "stheadshotdev1234567890"
    location             = "centralus"
    resource_group_tags = {
      service     = "headshot-api"
      team        = "platform-engineering"
      env         = "dev"
      cost-center = "11300"
      provider    = "azure"
      location    = "centralus"
    }
    storage_account_tags = {
      service     = "headshot-api"
      team        = "platform-engineering"
      env         = "dev"
      cost-center = "11300"
      provider    = "azure"
      location    = "centralus"
    }
  }

  assert {
    condition = (
      length([azurerm_resource_group.this]) == 1 &&
      length([azurerm_storage_account.this]) == 1
    )
    error_message = "The capability must contain exactly one Resource Group and one Storage Account."
  }

  assert {
    condition = (
      azurerm_resource_group.this.location == "centralus" &&
      azurerm_storage_account.this.location == "centralus"
    )
    error_message = "Both resources must use the supplied deployment location."
  }

  assert {
    condition = (
      azurerm_resource_group.this.tags == var.resource_group_tags &&
      azurerm_storage_account.this.tags == var.storage_account_tags
    )
    error_message = "Each resource must receive its exact supplied tag map."
  }

  assert {
    condition = (
      azurerm_storage_account.this.account_kind == "StorageV2" &&
      azurerm_storage_account.this.account_tier == "Standard" &&
      azurerm_storage_account.this.account_replication_type == "LRS"
    )
    error_message = "Storage Account must use the approved POC service defaults."
  }

  assert {
    condition = (
      azurerm_storage_account.this.https_traffic_only_enabled &&
      azurerm_storage_account.this.min_tls_version == "TLS1_2" &&
      !azurerm_storage_account.this.allow_nested_items_to_be_public &&
      !azurerm_storage_account.this.cross_tenant_replication_enabled &&
      azurerm_storage_account.this.public_network_access == "Disabled"
    )
    error_message = "Storage Account security defaults do not match the V4 design."
  }
}