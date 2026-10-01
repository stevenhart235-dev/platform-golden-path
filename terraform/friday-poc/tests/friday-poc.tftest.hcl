mock_provider "azurerm" {}

run "valid_friday_foundation" {
  command = apply

  variables {
    effective_metadata_path = "tests/effective-metadata.json"
    subscription_id         = "11111111-2222-3333-4444-555555555555"
  }

  assert {
    condition     = module.foundation.resource_group_name == "rg-headshot-api-dev-centralus"
    error_message = "Resource Group naming is not deterministic."
  }

  assert {
    condition     = can(regex("^st[a-z0-9]{1,22}$", module.foundation.storage_account_name))
    error_message = "Storage Account name must be deterministic and Azure-valid."
  }

  assert {
    condition     = length(module.foundation.storage_account_name) <= 24
    error_message = "Storage Account name exceeds Azure's 24-character limit."
  }

  assert {
    condition     = module.foundation.location == "centralus"
    error_message = "Both resources must deploy to context.deployment.location."
  }

  assert {
    condition = module.foundation.resource_group_tags == tomap({
      service     = "headshot-api"
      team        = "platform-engineering"
      env         = "dev"
      cost-center = "11300"
      provider    = "azure"
      location    = "centralus"
    })
    error_message = "Resource Group tags must exactly match its effective metadata."
  }

  assert {
    condition = module.foundation.storage_account_tags == tomap({
      service     = "headshot-api"
      team        = "platform-engineering"
      env         = "dev"
      cost-center = "11300"
      provider    = "azure"
      location    = "centralus"
    })
    error_message = "Storage Account tags must exactly match its effective metadata."
  }

  assert {
    condition = (
      !contains(keys(module.foundation.resource_group_tags), "platform") &&
      !contains(keys(module.foundation.storage_account_tags), "platform")
    )
    error_message = "The unresolved governed platform tag must not be fabricated."
  }

  assert {
    condition = (
      nonsensitive(output.resource_ids.resource_group) != "" &&
      nonsensitive(output.resource_ids.storage_account) != "" &&
      output.effective_tags.resource_group == module.foundation.resource_group_tags &&
      output.effective_tags.storage_account == module.foundation.storage_account_tags
    )
    error_message = "Outputs must expose IDs and expected tags without credentials."
  }
}

run "incompatible_artifact_fails" {
  command = plan

  variables {
    effective_metadata_path = "tests/incompatible-effective-metadata.json"
    subscription_id         = "11111111-2222-3333-4444-555555555555"
  }

  expect_failures = [
    var.effective_metadata_path,
  ]
}
