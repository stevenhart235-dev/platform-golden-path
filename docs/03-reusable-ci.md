# V5 — Reusable CI Orchestration

**Status:** V5 implemented
**Mode:** plan only

The consumer calls a versioned reusable workflow in `platform-workflows` and
provides only its consumer-intent path and Azure deployment identifiers. The
consumer pins that public platform interface; it does not select internal
platform component versions.

The reusable workflow owns the compatible `platform-golden-path` dependency.
For the Friday POC workflow release `v2.0.0`, that dependency is
`platform-golden-path@v0.5.0`. Both releases must be immutable once published.

The workflow orchestrates checkout, normalization, governance validation,
artifact-integrity verification, Terraform validation, Azure OIDC login, and
Terraform plan. Governance values, effective-tag construction, and Terraform
resource definitions remain in `platform-golden-path`.

The existing cross-repository `workflow_call` proof is reused unchanged as the
mechanical pattern. V5 adds a separate Friday workflow rather than modifying
the proven Python CI workflow.

## Consumer interface

The reusable workflow accepts:

- `consumer-intent-path`
- `subscription-id`
- `azure-client-id`
- `azure-tenant-id`

The Azure identifiers are deployment/authentication configuration, not
secrets. The caller grants only `contents: read` and `id-token: write`.

Provider, location, capability version, implementation repository/ref,
Terraform root, governance contract, and tag maps are not consumer inputs.

## Release prerequisite

The current implementation must be published as the immutable
`platform-golden-path@v0.5.0` release before the Friday reusable workflow can
execute. After the workflow is verified, `platform-workflows@v2.0.0` can be
published for consumer pinning. Consumers must not be given an override for
the internal golden-path ref.
