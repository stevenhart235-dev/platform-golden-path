# V4 — Terraform Infrastructure Delivery

**Status:** V4 implemented
**Capability:** azure-application-foundation v0

The Friday root directly reads the V3.1 effective-metadata artifact. It uses
context.deployment.location for Azure placement and passes each resource's
effective_tags map unchanged to the reusable child module.

Terraform does not read the governance contract and does not validate
registries or approved values. Its checks cover artifact compatibility,
resource shape, deployment-context consistency, and Azure naming constraints.

The child module creates exactly one Resource Group and one Storage Account.
It does not configure a provider or backend, assume tag inheritance, or add a
platform tag.

The root targets an existing subscription through a non-sensitive
subscription_id input. Azure credentials remain outside Terraform inputs and
use the AzureRM provider's normal authentication chain.

No remote backend is configured or provisioned in V4. Local state is the
default until a later deployment design supplies approved pre-existing state
storage.
