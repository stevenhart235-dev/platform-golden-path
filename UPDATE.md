I'm working on a Golden Path architecture/POC and want you to act as my technical implementation partner this week.

CONTEXT

I'm a Cloud Architect and still early in current-state discovery.

My manager, Jerrod, has explicitly asked me to work on Golden Paths. I recently whiteboarded the following general model with him:

Consumer / application intent
→ platform enrichment/defaults
→ effective configuration
→ governance/validation
→ Terraform / approved infrastructure implementation
→ Azure
→ Azure Policy / platform-side guardrails

Jerrod agreed with the general direction.

We also discussed bootstrapping application repositories with very thin consumer-facing configuration, potentially something like:

- ci.yml pointing to centrally maintained reusable workflows
- values.yml containing only information the consumer genuinely needs to provide

A major design principle is:

CONSUMERS SHOULD KNOW AS LITTLE AS PRACTICAL ABOUT THE BACKEND INFRASTRUCTURE.

Self-service is NOT currently a requirement.

The goal is abstraction and a supported/paved delivery path, not necessarily a developer portal or push-button infrastructure provisioning.

Jerrod has also provided an existing tagging strategy that he started, but he has explicitly said it is open to refinement/change.

There is a new Platform Engineering Lead starting soon. Jerrod wants me to collaborate with that person on the longer-term strategy, so this POC must NOT be presented as a predetermined production architecture.

POC PURPOSE

The question I want this POC to answer is:

"Can we demonstrate one Golden Path where the consumer provides minimal workload-specific intent while the platform owns the infrastructure knowledge necessary to produce a governed Azure deployment?"

This is an executable architecture model, not a production platform.

The current implementation can use whatever tools are useful. Jerrod has explicitly given flexibility to use a new Git repo, Terraform Cloud, Azure, etc.

However, tool choice should remain secondary to the architecture. GitHub Actions, Terraform, Terraform Cloud, Azure Policy, etc. are implementations of capabilities and should not unnecessarily become architectural requirements.

CURRENT TECHNICAL DIRECTION

Keep the first path intentionally small:

Consumer repo
    |
    |-- application/source
    |-- ci.yml
    |-- values.yml
            |
            v
================ PLATFORM BOUNDARY ================
            |
            |-- resolve platform defaults
            |-- enrich consumer intent
            |-- apply authoritative metadata where available
            |-- validate governance
            |-- select/use approved implementation
            |
            v
Reusable workflow
            |
            v
Reusable Terraform module
            |
            v
Azure deployment
            |
            v
Azure Policy / platform guardrail

Use a trivial Azure workload for the POC. Resource Group + Storage Account is sufficient.

We are NOT trying to prove that I know how to build complicated Azure infrastructure.

We are proving the contract and abstraction boundary.

CONSUMER VS PLATFORM

The consumer should supply only knowledge genuinely unique to the workload.

Current exploratory fields have included:

- service
- team
- environment
- cost center

Platform-derived/configured values have included:

- provider
- Azure region/location
- naming
- implementation/module selection
- module versions
- workflow implementation
- infrastructure details
- governance rules

Do NOT assume those consumer fields are final.

An important discovery question is whether Portfolio or another authoritative organizational system already owns application identity, ownership, cost center, criticality, lifecycle state, etc.

If authoritative information already exists, the Golden Path should preferably consume/reference it rather than asking application teams to duplicate it in values.yml or Azure tags.

Do NOT turn Azure tags into a homegrown CMDB.

POC SUCCESS CRITERIA

I'd like the first vertical slice to demonstrate three scenarios:

1. HAPPY PATH

Valid minimal consumer intent
→ platform enrichment
→ governance passes
→ Terraform runs
→ Azure resource is created with expected effective metadata

2. INVALID PATH

Change a consumer value to something obviously invalid (e.g. "banana")
→ validation fails before Terraform
→ consumer receives a useful explanation

3. BYPASS/GUARDRAIL PATH

Demonstrate that Azure Policy or another appropriate platform-side control protects an important invariant if someone bypasses the preferred delivery workflow.

IMPORTANT BOUNDARIES

Do NOT expand this into:

- Backstage
- developer portal
- enterprise CMDB
- full application portfolio system
- AKS platform
- enterprise networking redesign
- FinOps platform
- Terraform Cloud replacement
- OpenTofu migration
- AI application platform
- full production-ready IDP
- every possible hosting pattern

Golden Path does NOT equal AKS.

Eventually there may be multiple approved hosting patterns underneath the Golden Path experience, but we are building ONE vertical slice first.

Think:

ONE consumer
→ ONE contract
→ ONE reusable workflow
→ ONE validation layer
→ ONE Terraform implementation
→ ONE simple Azure deployment
→ ONE platform guardrail

ARCHITECTURAL PRINCIPLES

- Consumer supplies only knowledge unique to the workload.
- Platform derives/defaults everything practical.
- Validate as early as practical.
- Enforce important invariants at appropriate platform boundaries.
- Do not duplicate authoritative sources of truth.
- Do not force every workload into the same hosting pattern.
- Exceptions should be possible but explicit.
- Infrastructure should remain traceable to the workload/application it supports.
- Deployment is not the end of the lifecycle.
- Do not automate organizational processes we don't yet understand.
- Do not add technology merely because we can.

DISCOVERY IS HAPPENING IN PARALLEL

While building the POC, I'm also learning:

- What Portfolio owns
- What the authoritative application inventory is
- How application/business/technical ownership is tracked
- Whether criticality/RTO/RPO/lifecycle are recorded
- How new applications/projects enter the organization
- Where architecture becomes involved
- How hosting targets are selected
- How Infrastructure, Development, Security, Networking, Data, and Portfolio interact
- What happens operationally after deployment
- How applications and infrastructure are retired

Do not invent answers to those questions in the POC.

Use placeholders/interfaces where necessary and explicitly identify unresolved organizational dependencies.

THIS WEEK

I have three lanes:

1. PRIMARY: Continue/refine the first Golden Path POC.
2. DISCOVERY: Learn as much as practical about the existing organization/processes/systems.
3. OPERATIONAL SUPPORT: Help with normal incoming work such as HAProxy, public IP reviews/migrations, Azure issues, tickets, etc.

Only #1 is currently the strategic capability I'm actively driving.

Operational work can reveal Golden Path requirements, but do not automatically turn every problem I encounter into another architecture initiative.

WORKING STYLE

Help me keep this small.

Before adding a component, ask:

"What architectural question does this answer?"

If there isn't a good answer, don't add it.

Distinguish throughout our work:

OBSERVED - something actually seen or communicated
DIRECTED - something leadership explicitly asked for
HYPOTHESIS - possible explanation/design direction
UNKNOWN - something requiring discovery
DECISION - something deliberately decided with sufficient evidence

Do not silently turn hypotheses into requirements or POC implementation choices into enterprise architecture decisions.

The informal mental model for the project is:

"Follow the Yellow Brick Road."

The consumer follows the supported path and shouldn't need to understand all of the infrastructure machinery behind it.

Let's start by reviewing the current Golden Path POC/repositories and determine the smallest set of changes necessary to produce a clean end-to-end V0 demonstration by the end of this week.