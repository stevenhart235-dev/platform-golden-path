# V3 — Policy Validation Design

**Status:** V3 implemented
**Scope:** Friday vertical slice only

## Decision

V3 uses a small Python contract interpreter rather than OPA/Rego and Conftest.
The current tagging contract contains a small assertion vocabulary, so adding
another policy language and runtime would increase POC complexity without
reducing governance duplication.

The reusable workflow will eventually orchestrate this validator. It must not
contain governance values or rules.

## Boundary

Normalization converts consumer intent and platform-derived or configured
values into a versioned effective-metadata JSON document. The document lists
the effective tags expected on each applicable resource and records value
provenance. Its context records both the selected capability and the platform
deployment configuration:

~~~json
{
  "context": {
    "capability": {
      "id": "azure-application-foundation",
      "version": "v0"
    },
    "deployment": {
      "provider": "azure",
      "location": "centralus"
    }
  }
}
~~~

The deployment provider and location originate from platform configuration.
Normalization also emits them as effective tags for every applicable resource,
with provider recorded as platform-derived and location as
platform-configured.

Policy evaluation consumes only:

- the normalized effective-metadata document
- contracts/tagging/tagging-contract.yaml

The normalized document is deliberately independent of Terraform. A future
Terraform-plan adapter may produce the same boundary shape without changing
the governance result format.

## Commands

Normalize:

~~~text
python -m policy_validation normalize \
  --consumer <consumer.yaml> \
  --platform <platform.yaml> \
  --contract contracts/tagging/tagging-contract.yaml \
  --output <effective-metadata.json>
~~~

Validate:

~~~text
python -m policy_validation validate \
  --input <effective-metadata.json> \
  --contract contracts/tagging/tagging-contract.yaml \
  [--output <validation-result.json>]
~~~

The validator prints a human-readable result. The optional output is JSON for
automation and later workflow publication.

## Exit Codes

- 0: validation passed
- 1: one or more governance violations
- 2: malformed or incompatible input, contract error, or execution failure

## Contract Interpretation

Python implements only generic assertion behavior:

- required
- registry-membership
- equals
- common tag formatting
- resource applicability

Required tags, field mappings, registry values, fixed values, and applicable
resource types remain in the V2 contract.

Only governance_validation.enforceable_rules and formatting requirements are
evaluated. Deferred source requirements, unresolved governance questions,
registry status semantics, and the empty conditional-rule extension point do
not become policy.

Before governance evaluation, the validator performs artifact-integrity
checks. Each applicable resource's effective provider and location tags must
exactly match context.deployment. A mismatch is malformed boundary input and
uses exit code 2; it is not a governance violation. Internally consistent but
governance-invalid values continue to the V2 contract rules and use exit code
1 when those rules fail.

The unresolved platform mapping is recorded in normalized metadata as
deferred and is not emitted as an effective tag.

## Future Tooling Threshold

OPA/Rego and Conftest should be reconsidered when conditional/discriminator
rules become material, policies span multiple infrastructure domains, or
direct Terraform-plan evaluation provides enough value to justify the
additional runtime and policy language.

V3 does not add GitHub Actions, Terraform, Azure resources, or Azure Policy.
