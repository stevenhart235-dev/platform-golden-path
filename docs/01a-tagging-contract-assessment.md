# 02 — Tagging Contract Assessment

**Status:** Draft v0.1
**Milestone:** M1.2
**Purpose:** Determine the validation semantics required to represent the proposed enterprise tagging framework as a machine-readable contract.

## 1. Initial Finding

The proposed tagging framework cannot be represented as a flat list of required tag keys.

The framework defines multiple validation behaviors:

- unconditional required tags
- conditionally required tags
- curated registry values
- fixed enumerations
- patterned values
- contextual discriminator relationships
- workload-specific applicability
- scope/inheritance semantics

The machine-readable contract must therefore represent both tag definitions and validation rules.

## 2. Source Roles

### Tagging Framework

Defines governance intent, semantics, applicability, ownership, and enforcement expectations.

### Tag Library

Contains the detailed tag registry, allowed values, contextual discriminator relationships, and supporting metadata.

### Tagging Worksheet

Provides a human-oriented mechanism for recording resource tags and selecting common allowed values.

### Initial Architectural Interpretation

The Tag Library is currently the strongest candidate for the source from which a machine-readable validation contract could be generated.

The Tagging Worksheet should not independently become an authoritative policy source.



## 3. Contract Gaps Identified

### GAP-001 — Backup Tier Coverage

The framework requires `backup-tier` for stateful resources and VMs.

The current registry contains mappings for:

- database
- storage
- cache

Mappings for other applicable workload/resource categories require clarification before strict enforcement.

### GAP-002 — Conditional Required Tags

Several globally required tags have contextual applicability rules.

Examples include:

- `business-owner`
- `criticality-tier`
- `backup-tier`

The validation contract must represent applicability explicitly rather than treating all global tags as universally required.

### GAP-003 — Contextual Discriminators

Some values cannot be validated independently.

Examples:

- `provider` determines valid `platform`
- `provider` determines valid `location`
- `workload-type` determines valid `backup-tier`

Validation must therefore support relationships between tag values.

### GAP-004 — Inheritance Semantics

The framework permits tags to be applied at higher logical scopes under a Scoped Uniformity Contract.

Cloud-provider inheritance behavior does not necessarily produce equivalent resource-level tags.

The implementation must distinguish:

- governance inheritance
- provider-native inheritance
- effective resource tags

## 4. V2 Friday Contract Decision

V2 is implemented as a bounded POC contract in
`contracts/tagging/tagging-contract.yaml`. It separates consumer fields,
platform-derived or configured fields, governed tag keys, and governance
validation.

The enforceable V2 rules cover only the effective tags needed on the Friday
Resource Group and Storage Account: `service`, `team`, `env`, `cost-center`,
`provider`, and `location`. Azure-native tag inheritance is not assumed.

The POC uses the registered `headshot-api` demo service and configures
`centralus` as its platform default. The service status and location default
are POC metadata and configuration; they do not establish new enterprise
approval or location policy.

The source-required `platform` tag is represented as a deferred requirement.
The capability identifier `azure-application-foundation` is not a governed
`platform` value, and none of the registered Azure platform values accurately
describes the Resource Group plus Storage Account capability. V2 therefore
does not invent or enforce a platform mapping.

Registry statuses are preserved where supplied but are not enforced because
their semantics are not consistently defined. Cost-center validation uses
registry membership because the source does not provide an enforceable
pattern. All unresolved questions are isolated under `unresolved_governance`
and are explicitly excluded from policy input.

`conditional_rules` is retained as an empty extension point. V2 does not
implement the remaining enterprise tagging model or any validator, policy,
workflow, Terraform, or Azure resources.
