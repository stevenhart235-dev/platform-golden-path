I'm working on an architecture/discovery POC for a standardized platform golden path.

The goal is NOT to replace existing enterprise governance, Terraform, GitHub, or cloud-policy systems. The goal is to determine how existing governance requirements can be consumed by standardized delivery tooling.

Repository structure currently includes:

docs/
  00-vision-and-scope.md
  01-governance-discovery.md
  01a-tagging-contract-assessment.md
  02-application-onboarding.md
  03-reusable-ci.md
  04-infrastructure-delivery.md
  05-artifact-and-deployment.md
  06-operational-readiness.md
  07-lifecycle.md

contracts/
  tagging/
    tagging-contract.yaml   # currently empty

references/
  Clayco_Tag_Library 7.xlsx
  Clayco_Tagging_Framework 5.docx
  Clayco_Tagging_Worksheet 6.xlsx

Current milestone: M1.3 — design a machine-readable tagging contract.

Completed discovery:

M1.1 — Governance Discovery
- Existing tagging governance remains authoritative.
- Enterprise Architecture owns the tagging framework/global tags.
- Cloud Engineering owns cloud-policy enforcement.
- Platform Engineering owns CI/CD tagging enablement/tooling.
- Golden-path tooling should consume governance rather than redefine it.
- Cloud-native enforcement remains a separate control boundary.

M1.2 — Tagging Contract Assessment
The tagging model cannot be represented as only a flat list of required keys.

The contract needs to support:
- unconditional required tags
- conditionally required tags
- enumerated values
- registry-backed values
- patterned values
- contextual discriminators
- workload/resource applicability
- scope/inheritance semantics

Known examples from the written framework include:
- provider influences valid platform
- provider influences valid location
- workload-type influences backup-tier
- criticality-tier has environment-dependent applicability
- backup-tier has workload/resource-dependent applicability

Important unresolved items:
- authoritative machine-readable source
- exact registry values/status semantics
- conditional applicability rules
- scoped-uniformity representation
- logical vs provider-native tag inheritance
- warning vs blocking rules
- exception representation
- contract versioning
- availability-tier relationship to criticality-tier/backup-tier
- gaps between documented backup-tier applicability and registry coverage

Architecture direction:

Existing governance source
        ↓
Machine-readable tagging contract
        ↓
Independent validator
        ↓
Terraform plan
        ↓
Reusable GitHub workflow
        ↓
deployment decision

GitHub should orchestrate validation; it should not contain the governance logic itself.

Terraform implements infrastructure.

Azure Policy/AWS controls remain the cloud enforcement boundary so CI/CD is not the only control.

Eventually we want to demonstrate:

1. compliant Terraform plan passes
2. missing required tag fails
3. invalid registry value fails
4. conditional/discriminator rule fails appropriately
5. corrected plan passes
6. reusable GitHub workflow performs validation
7. cloud-native policy provides defense in depth

For now, DO NOT implement the validator.

Next task:

Inspect the three original tagging reference files, especially the Tag Library.

Derive the smallest representative M1.3 contract slice using REAL source values and relationships.

Start with:

provider
  -> platform
  -> location

Determine:
- actual allowed values
- registry/status fields
- discriminator relationships
- any applicability rules
- whether the workbook can reasonably serve as the source for generating a machine-readable contract

Then propose schema v0.1 for contracts/tagging/tagging-contract.yaml.

Do not invent missing policy.
Do not silently resolve ambiguities.
Record ambiguities as architecture/governance questions.
Do not modify the original reference files.

Keep the first contract intentionally small. We are proving the contract model before translating the entire enterprise tagging framework.
