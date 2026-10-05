Continue working in my PERSONAL GitHub and Azure POC environment only.

## Objective

Diagnose and close the validation-gate gap in the Golden Path POC.

I changed a consumer-supplied value to `banana`, but the deployment still succeeded and created or updated the Resource Group and Storage Account.

The required behavior is:

```text
Invalid consumer intent
→ normalization runs against the current input
→ governance validation fails
→ useful feedback is returned
→ Azure authentication does not occur
→ Terraform plan/apply does not occur
→ no Azure resource changes occur
```

Do not migrate anything to the work environment yet.

## Repositories required

Review the complete execution chain:

- `platform-golden-path`
- `platform-workflows`
- The consumer/caller repository used for the personal test, such as `platform-delivery-lab`

If any repository or workflow in the execution chain is unavailable, stop and request it. Do not guess how the missing workflow behaves.

Preserve unrelated changes and inspect Git status before modifying anything.

## Authorization boundary

Authorized:

- Read and modify the personal POC repositories
- Inspect relevant personal GitHub Actions workflows and run results
- Run local validation and automated tests
- Run GitHub Actions in the personal POC
- Authenticate to the existing personal Azure POC environment through its existing approved mechanism
- Run Terraform validation and plan
- Apply only when necessary to verify the corrected happy path against the existing POC Resource Group and Storage Account
- Add or update automated tests
- Update POC documentation

Not authorized:

- Accessing or modifying the work GitHub organization
- Accessing or modifying the work Azure tenant/subscription
- Creating work identities, credentials, repositories, policies, or resources
- Broadening the POC beyond the existing Resource Group and Storage Account
- Creating additional cloud infrastructure unrelated to this test
- Adding a portal, Backstage, AKS, networking, Terraform Cloud, OPA, Snyk, or other new platforms
- Deleting resources without explicit approval
- Changing enterprise governance policy
- Treating POC registry values as approved enterprise policy

Use no long-lived Azure client secret. Preserve the existing OIDC approach.

## Known implementation behavior

The current Python validator is expected to reject `environment: banana`.

The tagging contract currently allows these environment values:

- `dev`
- `stage`
- `test`
- `prod`
- `sandbox`

Terraform does not directly read the consumer `values.yml`. It consumes a generated `effective-metadata.json` artifact.

Likely failure modes include:

- Terraform reused stale effective metadata.
- Normalization did not run after the consumer value changed.
- The validation exit code was swallowed.
- A command was piped through `tee` without preserving the failing exit code.
- `continue-on-error` or `|| true` allowed execution to continue.
- A downstream job used `if: always()`.
- Terraform did not have a strict dependency on successful validation.
- The apply path accepted an arbitrary or previously generated metadata artifact.
- A direct Terraform invocation bypassed the Golden Path workflow.
- A cached or committed effective-metadata file was reused.
- The consumer called a different workflow or platform version than expected.

Do not assume one of these is the cause. Establish the actual cause with evidence.

## Required investigation

1. Record the exact consumer field changed and the exact command or workflow used.
2. Record the versions or commit SHAs of:
   - Consumer repository
   - Reusable workflow
   - Golden Path implementation
   - Tagging contract
3. Trace the value through:
   - Consumer `values.yml`
   - Normalization
   - Generated effective metadata
   - Governance validation
   - Workflow job dependencies
   - Azure login
   - Terraform initialization, plan, and apply
4. Confirm whether the deployed resources contained:
   - The old valid value
   - The invalid `banana` value
   - Some platform-derived replacement value
5. Determine whether the deployment was:
   - A full workflow invocation
   - A manually executed Terraform command
   - An apply using previously generated metadata or state
6. Document the root cause before implementing the fix.

## Required fix properties

Implement the smallest change that closes the proven gap.

The corrected path must ensure:

1. Effective metadata is regenerated from the current consumer input on every run.
2. A consumer cannot provide or select a previously generated effective-metadata artifact.
3. The validator’s nonzero exit code is preserved.
4. No validation command uses `continue-on-error`, `|| true`, or equivalent behavior.
5. If output is piped, shell pipeline failure behavior preserves the validator exit code.
6. Terraform plan and apply explicitly depend on successful validation.
7. Plan/apply jobs do not use `if: always()` or another condition that bypasses validation.
8. Azure OIDC permissions and login are unavailable to the validation-only job.
9. Azure authentication occurs only after governance validation succeeds.
10. Terraform consumes the exact validated effective-metadata artifact.
11. The artifact is integrity-checked when crossing a job boundary.
12. An apply cannot silently use a stale artifact from another commit or workflow run.
13. Workflow and Golden Path dependencies remain pinned to reviewed versions.
14. The fix does not move governance rules into workflow YAML or Terraform.

If the architecture permits developers to run Terraform locally, make clear that local execution is not an authorized deployment path. Azure authorization must ensure that only the trusted workflow identity can perform the governed deployment.

## Required tests

Add tests at the appropriate layer.

### Local tests

Run the complete existing Python suite.

Verify:

```text
valid consumer intent       → validator exit 0
environment: banana         → validator exit 1
malformed input             → execution-error exit 2
```

Confirm the invalid result names the field, rejected value, allowed values, and remediation.

### Workflow integration test

Run the actual consumer-to-reusable-workflow path with:

```yaml
environment: banana
```

Prove from the workflow log that:

- Fresh effective metadata contains `env: banana`.
- Governance validation fails.
- Azure login is not executed.
- Terraform initialization is not executed.
- Terraform plan is not executed.
- Terraform apply is not executed.
- No Azure resource changes occur.

Do not treat a green unit test alone as proof that the workflow gate works.

### Happy-path regression

Restore a valid environment value and run the same workflow.

Verify:

- Normalization uses the current input.
- Governance passes.
- The effective-metadata digest remains consistent.
- Terraform validation and plan succeed.
- If an apply is necessary for verification, it affects only the existing personal POC Resource Group and Storage Account.
- The deployed tags match the validated effective metadata.

Do not delete the POC resources unless separately authorized.

## Documentation updates

Update the relevant POC documentation to explain:

- The discovered root cause
- The corrected validation boundary
- Why Terraform cannot be invoked with stale effective metadata
- Where Azure authentication becomes available
- How the negative-path test proves enforcement
- The difference between validator unit tests and workflow integration tests
- Any remaining bypass paths or limitations

Keep the language explicitly POC-oriented. Do not claim production or enterprise enforcement.

## Completion report

Report:

- Root cause
- Exact reproduction steps
- Repositories, workflow versions, and commit SHAs tested
- Files changed
- Tests added or updated
- Local test results
- Invalid GitHub workflow result
- Evidence that Azure login and Terraform did not run for `banana`
- Happy-path regression result
- Azure resources created, modified, or unchanged
- Remaining known bypass paths
- Recommended work-environment migration prerequisites
- Explicit confirmation that no work GitHub or Azure environment was accessed or modified

Stop and report rather than guessing if the full caller/reusable-workflow chain or personal Azure execution evidence is unavailable.