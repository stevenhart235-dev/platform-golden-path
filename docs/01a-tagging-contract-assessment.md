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