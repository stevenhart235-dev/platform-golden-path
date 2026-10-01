module "foundation" {
  source = "../modules/azure-application-foundation-v0"

  resource_group_name  = local.resource_group_name
  storage_account_name = local.storage_account_name
  location             = local.deployment_location

  resource_group_tags  = local.resource_group_tags
  storage_account_tags = local.storage_account_tags
}
