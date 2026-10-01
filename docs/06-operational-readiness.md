# V6.1 — Remote-State-Backed Plan Proof

**Status:** implemented, not yet published or executed in GitHub Actions
**Scope:** trusted plan only

## Decision 1: state is platform infrastructure

Terraform state is platform infrastructure. The
`azure-application-foundation-v0` capability consumes a pre-provisioned Azure
Blob backend but does not create, modify, or own its lifecycle. Consumer intent
does not contain backend configuration.

The reusable platform workflow supplies the backend coordinates to the thin
Terraform root during `terraform init`. The reusable child module remains
backend-agnostic.

The V6.1 backend is:

- subscription: `96b5adf1-55d9-4411-ae2a-adfaccecf80e`
- resource group: `rg-platform-tfstate-centralus`
- storage account: `stplatformtf65b543de`
- container: `tfstate`
- key: `friday-poc/azure-application-foundation-v0.tfstate`

Authentication uses Microsoft Entra ID and GitHub OIDC through the AzureRM
backend's `use_azuread_auth` and `use_oidc` settings. Storage account keys, SAS
tokens, client secrets, and access keys are prohibited.

## Privilege model

- `trusted-plan` has two independently scoped authorization boundaries:
  - Azure managed-workload control plane: read-only (`Reader` at the target subscription)
  - Terraform backend: the minimum permissions required for normal state access
    and state locking, scoped only to the dedicated `tfstate` container
- `trusted-apply`: a future separate identity with workload write plus state
  read/write

V6.1 implements and tests only the trusted-plan path. It does not implement
apply or provision backend infrastructure.

Backend write capability required to acquire or release a state-lock lease does
not imply authority to mutate managed Azure workloads. The plan identity remains
`Reader` against the target subscription and workload control plane.

## V6.1 authorization finding and validation sequence

The initial design assigned `Storage Blob Data Reader` to `trusted-plan`.
Analysis of the AzureRM backend showed that normal Terraform state locking uses
Azure Blob leases. Lease acquisition requires blob write capability, so
`Storage Blob Data Reader` is expected to be insufficient even though
`terraform plan` does not mutate managed Azure infrastructure.

V6.1 deliberately validates that finding in this order:

1. Publish V6.1 without changing the existing `Storage Blob Data Reader`
   assignment.
2. Run the real `trusted-plan` workflow against the remote backend.
3. Confirm whether execution fails specifically at state locking or lease
   acquisition.
4. If confirmed, make a separate documented authorization decision.
5. Prefer the least-privilege practical permission scoped to the dedicated
   `tfstate` container.
6. Do not disable Terraform state locking as a workaround.

## Decision 2: plan and apply identities are separate

Plan and apply must use separate Microsoft Entra service principals. Separate
GitHub environments federating to the same service principal would not create
Azure RBAC separation.

Any future trusted-apply design requires a separate identity, remote-state
write and lease permissions, workload write permissions, approval controls,
and its own explicitly reviewed workflow. Those concerns remain out of scope
for V6.1.

## Execution boundary

The plan sequence remains:

1. normalize consumer intent
2. hash effective metadata
3. validate governance
4. verify the effective-metadata digest
5. authenticate to Azure with OIDC
6. initialize the platform-owned remote backend
7. validate Terraform
8. run a normal, locked Terraform plan

No Terraform state or binary plan is uploaded as a diagnostic artifact.
