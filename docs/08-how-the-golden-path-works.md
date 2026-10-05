# How the Golden Path Works

## Purpose

The goal of the golden path is to make infrastructure delivery less dependent on every application team understanding and independently implementing all platform, governance, Terraform, GitHub, and cloud requirements.

The core principle is:

> **The consumer tells the platform what only the consumer can know. The platform derives and owns everything else it legitimately can.**

An application team should not need to become experts in the platform implementation just to deploy an application.

---

## The Problem

Without a standardized platform path, an application team that needs infrastructure may have to answer questions such as:

- Which Terraform module should I use?
- Which cloud region should I deploy to?
- How should resources be named?
- Which tags are required?
- Which tag values are valid?
- Which Terraform and provider versions should I use?
- How should GitHub authenticate to Azure?
- Which GitHub Actions should my pipeline use?
- Which governance checks must run?
- Which organizational standards apply?

When every application team answers those questions independently, the organization gets multiple implementations of the same delivery problem.

The golden path moves that knowledge into the platform.

---

## The Consumer Contract

For the current proof of concept, the consumer provides only:

```yaml
service: headshot-api
team: platform-engineering
environment: dev
cost_center: "11300"
```

Conceptually, the consumer is saying:

> This is the Headshot API. Platform Engineering owns it. This is the development environment. Charge its resources to this cost center.

Those are application-specific facts that the platform cannot safely invent.

The consumer does **not** decide things such as:

- Cloud provider
- Azure region
- Terraform version
- AzureRM provider version
- Terraform module
- Resource naming
- Required platform tags
- Governance implementation
- GitHub Actions implementation
- Azure authentication mechanism

Those are platform responsibilities.

---

## Consumer Intent vs. Platform Responsibility

The basic responsibility boundary is:

```text
Application says WHAT it needs
            |
            v
Platform determines HOW it is delivered
```

For the current capability, the platform knows that the deployment uses:

```text
Provider       = Azure
Location       = Central US
Capability     = azure-application-foundation v0
Naming         = platform-defined
Terraform      = platform-defined version
AzureRM        = platform-defined version
Workflow       = centrally maintained
Authentication = GitHub OIDC
Governance     = centrally validated
```

This allows platform decisions to change without requiring every application team to redesign its deployment pipeline.

---

## Effective Metadata

The platform combines consumer-owned information with platform-owned information.

Conceptually:

```text
Consumer intent
      +
Platform configuration
      |
      v
Effective metadata
```

For example:

```yaml
service: headshot-api
team: platform-engineering
env: dev
cost-center: "11300"
provider: azure
location: centralus
```

The resulting artifact represents what the platform actually intends to implement.

This is an important boundary.

Terraform does not independently reinterpret the original consumer request or reconstruct governance metadata. It consumes the validated effective configuration produced earlier in the process.

---

## Governance Happens Before Terraform

Before Terraform is allowed to interact with Azure, the effective metadata is validated against the platform's governance contract.

For example, if a consumer submitted:

```yaml
environment: banana
```

the process should stop before Terraform:

```text
Consumer request
      |
      v
Normalization
      |
      v
Governance validation
      |
      X
    STOP
```

Terraform is deliberately **not** the primary policy engine.

Terraform's responsibility is infrastructure implementation.

Governance determines whether the proposed configuration is acceptable.

This produces a separation of concerns:

```text
Governance defines compliance.

The machine-readable contract expresses governance.

The validator evaluates proposed configuration.

GitHub orchestrates the process.

Terraform implements the validated configuration.

Azure Policy provides cloud-side enforcement and defense in depth.
```

---

## Terraform's Role

Once governance succeeds, Terraform receives the validated effective metadata.

The flow becomes:

```text
Consumer intent
      |
      v
Platform configuration
      |
      v
Effective metadata
      |
      v
Governance validation
      |
      v
Terraform
      |
      v
Azure
```

Terraform therefore does not need to know how the consumer arrived at the configuration.

Its job is essentially:

> Here is the configuration that has already passed the platform boundary. Implement it.

For the current `azure-application-foundation v0` capability, that implementation is intentionally small:

```text
Resource Group
+
Storage Account
```

The small scope is deliberate. The purpose of the POC is to prove the delivery architecture, not to demonstrate complicated Azure infrastructure.

---

## GitHub Actions Is the Orchestrator

GitHub Actions is not the architecture itself.

It orchestrates the architecture.

The reusable workflow currently performs the process in approximately this order:

```text
Get consumer repository
        |
        v
Get compatible golden-path implementation
        |
        v
Resolve consumer intent
        |
        v
Normalize effective metadata
        |
        v
Validate governance
        |
        v
Verify artifact integrity
        |
        v
Initialize and validate Terraform
        |
        v
Authenticate to Azure
        |
        v
Terraform plan
```

The application repository does not contain the complete implementation of this process.

Instead, it calls a centrally maintained reusable workflow.

This allows many application repositories to consume the same delivery machinery while the platform team maintains the implementation centrally.

---

## Versioned Platform Contracts

The platform pieces are independently versioned.

The proven V5 dependency chain was:

```text
platform-delivery-lab
        |
        | consumes
        v
platform-workflows@v2.0.1
        |
        | consumes
        v
platform-golden-path@v0.5.0
```

This gives us explicit compatibility boundaries instead of silently consuming whatever happens to exist on another repository's main branch.

Platform changes can therefore be released intentionally and adopted deliberately.

---

## Azure Authentication

The workflow does not store an Azure client secret.

Instead, GitHub authenticates to Microsoft Entra ID using OpenID Connect (OIDC).

Conceptually:

```text
GitHub Actions
      |
      | OIDC identity token
      v
Microsoft Entra ID
      |
      | validates repository/environment identity
      v
Temporary Azure authentication
```

The trust relationship is constrained to the expected GitHub repository and environment.

For the current POC, the workflow runs under:

```text
platform-delivery-lab
        |
        v
trusted-plan
```

The federated credential trusts the immutable GitHub repository identity associated with that environment.

This means Azure does not simply trust "something running in GitHub."

It trusts the specifically configured workload identity.

---

## Authentication and Authorization Are Separate

Successfully authenticating does not mean the workflow can do anything it wants in Azure.

The current service principal has:

```text
Reader
```

at the target subscription.

That was intentional.

The V5 workflow performs a Terraform **plan**, not an apply.

Therefore, we started with read-only Azure authorization rather than immediately granting Contributor.

This gives us:

```text
GitHub identity
      |
      v
OIDC authentication
      |
      v
Microsoft Entra ID
      |
      v
Azure Reader authorization
```

The successful V5 execution demonstrated that Reader was sufficient for the current Terraform planning operation.

The workflow currently does not have permission to deploy the planned resources.

---

## What V5 Proved

The successful V5 run demonstrated the complete path:

```text
Application-owned information
        |
        v
Standard consumer interface
        |
        v
Versioned reusable workflow
        |
        v
Versioned platform implementation
        |
        v
Effective metadata generation
        |
        v
Governance validation
        |
        v
Artifact integrity verification
        |
        v
Terraform initialization and validation
        |
        v
GitHub trusted environment
        |
        v
OIDC authentication
        |
        v
Least-privilege Azure authorization
        |
        v
Real Terraform plan against Azure
```

The end-to-end GitHub Actions run completed successfully.

V5 runtime proof:

```text
GitHub Actions run: 36880999539
Result: SUCCESS
```

No Terraform apply was performed and no Azure resources were created by this workflow.

This proves significantly more than the ability to create a Resource Group or Storage Account with Terraform.

It demonstrates that infrastructure delivery can be treated as a **platform capability** rather than requiring every application repository to independently implement the entire delivery process.

---

## What the Application Team Does Not Need to Know

A consumer using this capability did not need to know:

```text
How the governance validator works
How effective metadata is constructed
Which Terraform root module is used
Which child module is used
Which AzureRM version is selected
How resources are named
How GitHub obtains an Azure identity
How federated credentials are configured
Which GitHub actions implement the pipeline
How governance is evaluated before Terraform
```

Those concerns remain platform responsibilities.

The application team interacts with a much smaller contract.

---

## What We Have Not Solved Yet

The current implementation is deliberately a vertical slice.

It does **not** yet represent a production-complete internal developer platform.

Among other things, it does not yet provide:

- Terraform apply
- Production remote state and locking
- Apply approval boundaries
- Complete enterprise tagging coverage
- Final resolution of the governed `platform` tag
- Full exception handling
- Azure Policy bypass enforcement
- Complex networking
- AKS deployment
- Application runtime deployment
- Automatic platform/capability selection
- Production-grade lifecycle management

Those are later architectural decisions.

They were intentionally excluded so the fundamental delivery model could be proven first.

---

## Future Direction

Today the platform exposes one intentionally small capability:

```text
azure-application-foundation v0
```

In the future, the same model could support additional capabilities.

For example, an application could provide its application-specific intent:

```yaml
service: payments-api
team: payments
environment: prod
cost_center: "12345"
```

A more mature platform could determine that the workload should:

```text
Deploy to an existing AKS platform
Use workload identity
Use approved networking
Use standard observability
Use required governance controls
Use platform naming
Use governed tags
```

Another workload might be better suited for Azure Container Apps.

Another might require a new cluster or dedicated infrastructure.

The long-term goal is not to force every workload onto the same infrastructure.

The goal is to provide a standardized mechanism for turning application intent into an appropriate, governed platform implementation.

---

## The Core Idea

The entire architecture can be summarized with one principle:

> **The consumer tells the platform what only the consumer can know. The platform derives everything else it legitimately can.**

Or even more simply:

```text
Application teams describe their intent.

The platform owns the complexity required to deliver it safely.
```