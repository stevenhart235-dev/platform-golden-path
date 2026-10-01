import copy
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from policy_validation.core import InputError, load_yaml, main, normalize, validate


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "contracts/tagging/tagging-contract.yaml"
FIXTURES = Path(__file__).parent / "fixtures"


class PolicyValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = load_yaml(CONTRACT_PATH)
        cls.consumer = load_yaml(FIXTURES / "consumer-valid.yaml")
        cls.platform = load_yaml(FIXTURES / "platform-friday.yaml")

    def document(self):
        return normalize(
            copy.deepcopy(self.consumer),
            copy.deepcopy(self.platform),
            self.contract,
        )

    def test_valid_friday_input_passes_without_platform_tag(self):
        document = self.document()
        self.assertEqual(
            document["context"]["deployment"],
            {"provider": "azure", "location": "centralus"},
        )
        self.assertNotIn("platform", document["resources"][0]["effective_tags"])
        self.assertEqual(
            document["deferred"]["platform"]["resolution"],
            "unresolved-governance-mapping",
        )
        self.assertEqual(validate(document, self.contract)["result"], "PASS")

    def test_invalid_environment_cli_reports_governance_violation(self):
        with tempfile.TemporaryDirectory() as directory:
            normalized_path = Path(directory) / "effective-metadata.json"
            with redirect_stdout(io.StringIO()):
                normalize_code = main(
                    [
                        "normalize",
                        "--consumer",
                        str(FIXTURES / "consumer-invalid-environment.yaml"),
                        "--platform",
                        str(FIXTURES / "platform-friday.yaml"),
                        "--contract",
                        str(CONTRACT_PATH),
                        "--output",
                        str(normalized_path),
                    ]
                )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                validate_code = main(
                    [
                        "validate",
                        "--input",
                        str(normalized_path),
                        "--contract",
                        str(CONTRACT_PATH),
                    ]
                )

        self.assertEqual(normalize_code, 0)
        self.assertEqual(validate_code, 1)
        self.assertIn("[allowed-environment]", stdout.getvalue())
        self.assertIn("env='banana'", stdout.getvalue())

    def test_deployment_provider_tag_mismatch_is_input_error(self):
        document = self.document()
        document["resources"][0]["effective_tags"]["provider"] = "aws"
        with self.assertRaisesRegex(InputError, "does not match deployment context"):
            validate(document, self.contract)

    def test_deployment_location_tag_mismatch_is_input_error(self):
        document = self.document()
        document["resources"][1]["effective_tags"]["location"] = "northcentralus"
        with self.assertRaisesRegex(InputError, "does not match deployment context"):
            validate(document, self.contract)

    def test_missing_effective_tag_fails_on_one_resource(self):
        document = self.document()
        document["resources"][1]["effective_tags"].pop("cost-center")
        result = validate(document, self.contract)
        self.assertEqual(result["result"], "FAIL")
        self.assertTrue(
            any(
                item["rule_id"] == "required-effective-tags"
                and item["resource"] == "storageAccounts"
                and item["tag_key"] == "cost-center"
                for item in result["violations"]
            )
        )

    def test_invalid_consumer_registries_report_each_field(self):
        consumer = copy.deepcopy(self.consumer)
        consumer.update(
            service="unknown-service",
            team="unknown-team",
            environment="unknown-env",
            cost_center="99999",
        )
        result = validate(normalize(consumer, self.platform, self.contract), self.contract)
        failed_keys = {
            item["tag_key"]
            for item in result["violations"]
            if item["rule_id"].startswith(("registered-", "allowed-"))
        }
        self.assertEqual(failed_keys, {"service", "team", "env", "cost-center"})

    def test_invalid_provider_fails(self):
        platform = copy.deepcopy(self.platform)
        platform["provider"] = "aws"
        result = validate(normalize(self.consumer, platform, self.contract), self.contract)
        self.assertTrue(
            any(item["rule_id"] == "azure-provider" for item in result["violations"])
        )

    def test_invalid_azure_location_fails(self):
        platform = copy.deepcopy(self.platform)
        platform["location"] = "not-an-azure-location"
        result = validate(normalize(self.consumer, platform, self.contract), self.contract)
        self.assertTrue(
            any(item["rule_id"] == "azure-location" for item in result["violations"])
        )

    def test_consistent_governance_invalid_deployment_reaches_policy_rules(self):
        platform = copy.deepcopy(self.platform)
        platform.update(provider="aws", location="not-an-azure-location")
        document = normalize(self.consumer, platform, self.contract)
        self.assertEqual(document["context"]["deployment"]["provider"], "aws")
        self.assertEqual(
            document["resources"][0]["effective_tags"]["provider"],
            "aws",
        )
        result = validate(document, self.contract)
        self.assertEqual(result["result"], "FAIL")
        self.assertTrue(
            any(item["rule_id"] == "azure-provider" for item in result["violations"])
        )
        self.assertTrue(
            any(item["rule_id"] == "azure-location" for item in result["violations"])
        )

    def test_formatting_violation_fails(self):
        consumer = copy.deepcopy(self.consumer)
        consumer["team"] = "Platform/Engineering"
        result = validate(normalize(consumer, self.platform, self.contract), self.contract)
        self.assertTrue(
            any(item["rule_id"] == "formatting" for item in result["violations"])
        )

    def test_incompatible_contract_reference_is_execution_error(self):
        document = self.document()
        document["contract"]["version"] = "different"
        with self.assertRaises(InputError):
            validate(document, self.contract)
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "input.json"
            input_path.write_text(json.dumps(document), encoding="utf-8")
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = main(
                    [
                        "validate",
                        "--input",
                        str(input_path),
                        "--contract",
                        str(CONTRACT_PATH),
                    ]
                )
        self.assertEqual(exit_code, 2)
        self.assertIn("contract reference", stderr.getvalue())

    def test_cli_exit_codes_and_json_output(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            normalized_path = directory / "effective-metadata.json"
            result_path = directory / "result.json"
            with redirect_stdout(io.StringIO()):
                normalize_code = main(
                    [
                        "normalize",
                        "--consumer",
                        str(FIXTURES / "consumer-valid.yaml"),
                        "--platform",
                        str(FIXTURES / "platform-friday.yaml"),
                        "--contract",
                        str(CONTRACT_PATH),
                        "--output",
                        str(normalized_path),
                    ]
                )
                pass_code = main(
                    [
                        "validate",
                        "--input",
                        str(normalized_path),
                        "--contract",
                        str(CONTRACT_PATH),
                        "--output",
                        str(result_path),
                    ]
                )
            self.assertEqual(normalize_code, 0)
            self.assertEqual(pass_code, 0)
            self.assertEqual(json.loads(result_path.read_text())["result"], "PASS")
            document = json.loads(normalized_path.read_text())
            document["context"]["deployment"]["provider"] = "aws"
            document["resources"][0]["effective_tags"]["provider"] = "aws"
            document["resources"][1]["effective_tags"]["provider"] = "aws"
            normalized_path.write_text(json.dumps(document), encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                fail_code = main(
                    [
                        "validate",
                        "--input",
                        str(normalized_path),
                        "--contract",
                        str(CONTRACT_PATH),
                    ]
                )
            self.assertEqual(fail_code, 1)


if __name__ == "__main__":
    unittest.main()
