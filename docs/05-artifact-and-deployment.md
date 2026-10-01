# V5 — Artifact and Deployment Boundary

V5 is plan only. It does not run `terraform apply`, create backend
infrastructure, or persist Terraform state or a binary plan.

Normalization writes one `effective-metadata.json` file. The workflow hashes
that file, validates it against the contract, verifies the hash again, makes
the file read-only, and passes its exact path to Terraform. Workflow YAML never
reconstructs effective tags.

Short-lived internal diagnostic artifacts contain:

- effective metadata
- machine-readable validation result
- SHA-256 checksum
- source and version manifest

They contain no Azure credentials or tokens. The binary Terraform plan and
local Terraform state are never uploaded.

Azure authentication uses GitHub OIDC and a federated Azure identity. Client,
tenant, and subscription identifiers are non-secret configuration; no client
secret is accepted. Federation and least-privilege Azure RBAC are external
prerequisites.

Because V4 has no remote backend, every hosted-runner plan starts without
durable state and normally proposes creation. Remote state, locking,
environment approval, concurrency control, and a protected apply boundary are
required before apply can be introduced.
