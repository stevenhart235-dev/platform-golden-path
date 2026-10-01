# Friday Developer-Experience Demo

This demo asks two questions today and reserves a third for the later Azure
Policy slice:

- Governance: **Is the developer allowed to ask for this?**
- Terraform: **Can the platform implementation actually build this?**
- Later Azure Policy: **Even if someone bypasses the platform, will Azure accept it?**

Run commands from the `platform-golden-path` repository root unless a scenario
explicitly uses GitHub Actions. The demo remains plan-only.

## G1 — Governance PASS

Developer input:

```yaml
service: headshot-api
team: platform-engineering
environment: dev
cost_center: "11300"
```

- Enforcement layer: governance validator
- Expected result: PASS
- Azure authentication: no for the local command
- Azure resources modified: no

Command:

```text
python -m unittest tests.v3_policy_validation.test_policy_validation.PolicyValidationTests.test_valid_friday_input_passes_without_platform_tag -v
```

Expected output includes:

```text
test_valid_friday_input_passes_without_platform_tag ... ok
```

## G2 — Governance FAIL

Developer input is unchanged except for the invalid environment:

```yaml
service: headshot-api
team: platform-engineering
environment: banana
cost_center: "11300"
```

- Enforcement layer: governance validator
- Expected result: FAIL with governance-violation exit status `1`
- Azure authentication: no; the reusable workflow stops before Azure login
- Azure resources modified: no

Focused automated command:

```text
python -m unittest tests.v3_policy_validation.test_policy_validation.PolicyValidationTests.test_invalid_environment_cli_reports_governance_violation -v
```

The validator output exercised by the test includes:

```text
FAIL: 2 resources, 36 evaluations, 2 violations
- [allowed-environment] resourceGroups tag env='banana' is not registered.
- [allowed-environment] storageAccounts tag env='banana' is not registered.
```

Missing and unknown cost-center demonstrations remain optional follow-ups, not
primary steps in this four-scenario demo.

## T1 — Terraform PASS

Developer input is the valid G1 request.

- Enforcement layer: Terraform plan after governance validation
- Expected result: PASS
- Azure authentication: yes, through GitHub OIDC in the `trusted-plan` environment
- Azure resources modified: no; this is plan-only

Workflow:

```text
platform-delivery-lab@4b23e5e008fb7814750a106b15bbf18ee7eec5f1
  -> platform-workflows@v2.1.2
  -> platform-golden-path@v0.6.0
```

The real V6.1 GitHub run has proven normalization, governance validation,
effective-metadata integrity verification, Azure OIDC authentication, AzureRM
remote-state initialization, Terraform validation, and a successful locked
`terraform plan`. Expected output ends with a successful plan summary; it does
not include `terraform apply`.

## T2 — Terraform FAIL

The developer intent and effective tags remain governance-valid. The simulated
defect is platform-owned naming logic supplying:

```text
storage_account_name = "st-headshot-dev"
```

- Enforcement layer: Terraform module input validation
- Expected result: the invalid value is rejected as an expected failure
- Azure authentication: no; the test uses the mocked AzureRM provider
- Azure resources modified: no
- Ownership: **PLATFORM IMPLEMENTATION defect**, not invalid developer intent

Command:

```text
terraform -chdir=terraform/modules/azure-application-foundation-v0 test -filter=tests/foundation.tftest.hcl
```

Expected output includes:

```text
run "invalid_platform_storage_name_is_rejected" ... pass
```

The test is green because it expects Terraform to reject the invalid name using
the existing `storage_account_name` validation. Removing that validation or
accepting the invalid name would make the test fail.
