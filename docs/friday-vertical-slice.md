# Friday Golden Path Vertical Slice

## Objective

Demonstrate a small end-to-end golden path proving:

consumer intent
→ reusable GitHub workflow
→ governance/policy validation
→ reusable Terraform
→ Azure deployment
→ tag-based discovery/cost attribution
→ Azure Policy enforcement

## Design Principle

The consumer tells the platform what only the consumer can know.
The platform derives everything else it legitimately can.

## V0 — Scope

Azure only.

The POC deploys into an existing Azure subscription.

Capability:

azure-application-foundation v0

Resources created:

- Resource Group
- Storage Account

Explicitly out of scope:

- management-group provisioning
- subscription vending
- Function Apps
- VNets
- private endpoints
- private DNS
- AKS
- production networking
- full enterprise tagging implementation

These may be future extensions of the capability without changing
the fundamental consumer interaction model.

## V1 — Consumer Contract

The consumer supplies only:

service
team
environment
cost_center

Example:

service: orders-api
team: commerce
environment: dev
cost_center: "123"

Consumer responsibilities:

- identify the service
- identify organizational ownership
- express deployment environment intent
- provide financial attribution

Platform responsibilities:

- Azure provider selection
- capability selection/context
- Azure region/default placement
- naming
- Terraform implementation
- Terraform/provider/module versions
- resource defaults
- construction of standardized tags
- governance integration
- deployment mechanics
- authentication mechanism
- policy evaluation

Governance responsibilities:

- determine whether supplied and derived values are permitted
- define applicable tagging requirements
- provide the authoritative validation rules

## Derived Metadata

For this vertical slice the platform derives:

provider = azure
location = approved platform default
platform/capability = determined by selected golden path

The platform must not fabricate governance metadata it cannot
authoritatively determine.

The following enterprise tagging concepts are intentionally deferred
where sufficient authoritative context does not yet exist:

- business-owner
- workload-type
- criticality-tier
- backup-tier

## Future Direction

The consumer contract should be capable of becoming smaller as
authoritative organizational relationships become available.

For example, a future service catalog may allow:

service → team → cost-center → business-owner

At that point the consumer may only need to provide service and
environment.

The platform interface should express consumer intent rather than
expose underlying Terraform or cloud implementation details.

## Success Criteria

The vertical slice is successful when it can demonstrate:

1. Minimal consumer intent is accepted.
2. Invalid intent fails governance validation.
3. Valid intent produces compliant Terraform.
4. A reusable workflow orchestrates validation and deployment.
5. Azure resources are created with standardized metadata.
6. Resources can be discovered/grouped using standardized tags.
7. Azure Policy prevents a representative noncompliant deployment
   that bypasses the golden path.