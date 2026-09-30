# 01 — Governance Discovery & Integration

**Status:** Draft v0.1  
**Milestone:** M1.1  
**Initial focus:** Enterprise resource tagging  
**Implementation status:** Discovery only

## 1. Objective

Assess the existing Clayco Tagging Strategy Framework and determine how its approved requirements can be consumed by the proposed platform golden path.

The golden path will not independently redefine enterprise tagging standards or assume ownership of organizational governance.

## 2. Source Material

The following original documents are retained unchanged in `references/`:

- `Clayco_Tagging_Framework 5.docx`
- `Clayco_Tag_Library 7.xlsx`
- `Clayco_Tagging_Worksheet 6.xlsx`

The framework is the primary source for the initial architectural assessment. Workbook contents and validation semantics must be reconciled before implementation.

## 3. Documented Governance Model

The proposed framework establishes a moderate enforcement model in which required global tags are mandatory on applicable, taggable resources.

### Responsibilities

| Function | Documented responsibility |
|---|---|
| Enterprise Architecture | Owns the framework, defines global tags and approves registry changes |
| Cloud Engineering | Implements cloud-native policy enforcement |
| Platform Engineering | Implements CI/CD tagging enablement and supporting tooling |
| Application Teams | Ensure resources they own comply |
| FinOps / Finance | Define cost-center structures and validate cost-tag coverage |

### Documented conventions

- Tag keys and values use lowercase.
- Hyphens are the permitted separator.
- Required tags use stable identifiers rather than arbitrary descriptive text.
- Approved values and patterns are maintained centrally.
- Provider-specific differences must not create incompatible business taxonomies.
- Required tags should avoid unnecessary high-cardinality values.

## 4. Global Tag Contract

The framework identifies eleven required global tag keys, subject to documented applicability and contextual rules.

| Category | Tags |
|---|---|
| Identity and ownership | `service`, `team`, `business-owner` |
| Placement and environment | `provider`, `platform`, `location`, `env` |
| Operations and lifecycle | `workload-type`, `cost-center` |
| Resilience | `criticality-tier`, `backup-tier` |

Not every tag has identical applicability. For example, criticality requirements differ between production and lower environments, while backup requirements depend on workload characteristics.

The Tag Library also contains a `sublocation` category. Its relationship to the eleven global tags requires confirmation.

## 5. Scoped Uniformity and Effective Tagging

The framework introduces Scoped Uniformity Contracts to reduce unnecessary repetition when a subscription, account or other logical boundary has consistent ownership and workload metadata.

Uniformity requires a shared:

- Service.
- Owning team.
- Environment.
- Cost center.

The implementation must distinguish logical inheritance from provider-native tag behavior.

In particular, Azure resource tags do not automatically inherit from resource groups or subscriptions. Any requirement for effective resource-level tags must be satisfied through supported policy, provisioning or synchronization mechanisms.

A logical inheritance contract alone must not be interpreted as proof of effective tagging.

## 6. Proposed Golden Path Integration

The initial integration model is:

1. Consume an approved, versioned tagging contract.
2. Validate proposed infrastructure changes.
3. Report violations with actionable feedback.
4. Prevent deployment for requirements explicitly classified as blocking.
5. Support authorized, auditable exceptions.
6. Preserve cloud-native enforcement for provisioning outside the delivery pipeline.

### Responsibility boundaries

| Component | Proposed responsibility |
|---|---|
| Governance source | Defines approved standards and registry values |
| Reusable GitHub workflows | Orchestrate validation and release gates |
| Terraform modules | Implement compliant infrastructure defaults |
| Policy-as-code | Evaluate proposed infrastructure changes |
| Azure Policy / AWS controls | Enforce applicable cloud-native requirements |
| Compliance reporting | Detect existing drift and support remediation |

The governance source may eventually be maintained in a dedicated repository. Repository ownership and implementation boundaries remain discovery decisions.

## 7. Open Architecture Decisions

The following require clarification before implementation:

| ID | Question |
|---|---|
| GOV-001 | Which registry statuses represent approved deployable values? |
| GOV-002 | What is the authoritative, machine-readable tagging contract? |
| GOV-003 | How will conditional values be validated across provider, platform, location and workload type? |
| GOV-004 | How will scoped uniformity be represented and verified? |
| GOV-005 | Which violations are warnings versus deployment blockers? |
| GOV-006 | Who approves exceptions, and how are expiration and auditability handled? |
| GOV-007 | How are existing resources evaluated and remediated? |
| GOV-008 | How will provider-specific tagging limitations be handled? |
| GOV-009 | How are `availability-tier`, `criticality-tier` and `backup-tier` intended to relate? |
| GOV-010 | How will standards be versioned without unexpectedly breaking existing application delivery? |

## 8. Initial Vertical Slice

The proposed first proof of concept will:

- Use a small, representative Terraform configuration.
- Consume a versioned sample of the approved tagging contract.
- Generate a Terraform execution plan.
- Evaluate the plan against a limited set of agreed tagging requirements.
- Return actionable pass/fail results through a reusable GitHub workflow.
- Demonstrate a failed deployment gate.
- Document how cloud-native enforcement complements pipeline validation.

No production infrastructure deployment is required for this initial proof of concept.

## 9. Exit Criteria

M1.1 is complete when:

- The existing framework and supporting workbooks have been reconciled.
- Governance ownership is confirmed.
- Tag applicability and conditional validation are understood.
- Open decisions are documented with proposed owners.
- The initial validation scope is agreed upon.
- Implementation responsibilities are sufficiently defined to begin a bounded proof of concept.

**Current status:** Discovery in progress. No new organizational policy has been approved by this document.
