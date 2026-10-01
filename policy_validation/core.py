"""Small contract interpreter for the Friday effective-metadata boundary."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml


BOUNDARY_SCHEMA_VERSION = "1.0"


class InputError(Exception):
    """Malformed or incompatible input, contract, or invocation."""


def load_yaml(path: str | Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise InputError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise InputError(f"{path} must contain a YAML object")
    return value


def _require_schema(document: dict[str, Any], label: str) -> None:
    version = str(document.get("schema_version", ""))
    if version != BOUNDARY_SCHEMA_VERSION:
        raise InputError(
            f"{label} schema_version must be {BOUNDARY_SCHEMA_VERSION!r}; "
            f"received {version or 'missing'!r}"
        )


def normalize(
    consumer: dict[str, Any],
    platform: dict[str, Any],
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Resolve consumer/platform fields into resource-level effective tags."""
    _require_schema(consumer, "consumer intent")
    _require_schema(platform, "platform context")

    metadata = contract.get("metadata")
    scope = contract.get("scope")
    consumer_fields = contract.get("consumer_fields")
    platform_fields = contract.get("platform_fields")
    sections = (metadata, scope, consumer_fields, platform_fields)
    if not all(isinstance(item, dict) for item in sections):
        raise InputError("contract is missing normalization sections")

    tags: dict[str, Any] = {}
    provenance: dict[str, str] = {}
    for field_name, definition in consumer_fields.items():
        if not isinstance(definition, dict) or "governed_tag_key" not in definition:
            raise InputError(f"invalid consumer field definition: {field_name}")
        if field_name in consumer and consumer[field_name] is not None:
            tag_key = definition["governed_tag_key"]
            tags[tag_key] = consumer[field_name]
            provenance[tag_key] = "consumer"

    deferred: dict[str, Any] = {}
    for field_name, definition in platform_fields.items():
        if not isinstance(definition, dict) or "governed_tag_key" not in definition:
            raise InputError(f"invalid platform field definition: {field_name}")
        tag_key = definition["governed_tag_key"]
        if definition.get("enforceable_in_v2") is False:
            deferred[tag_key] = {
                "resolution": definition.get("resolution", "deferred"),
                "enforceable": False,
            }
            continue
        if field_name in platform:
            value = platform[field_name]
        elif "value" in definition:
            value = definition["value"]
        else:
            value = definition.get("default")
        if value is not None:
            tags[tag_key] = value
            provenance[tag_key] = str(definition.get("source", "platform"))

    capability = platform.get("capability", scope.get("capability"))
    deployment = {
        "provider": platform.get("provider"),
        "location": platform.get("location"),
    }
    resources = scope.get("resources")
    if not isinstance(capability, dict) or not isinstance(resources, list):
        raise InputError("contract/platform capability or contract resources are invalid")
    if not all(isinstance(value, str) and value for value in deployment.values()):
        raise InputError(
            "platform context must provide non-empty deployment provider and location"
        )

    normalized_resources = []
    for resource in resources:
        if not isinstance(resource, dict) or not isinstance(resource.get("type"), str):
            raise InputError("contract contains an invalid resource definition")
        resource_type = resource["type"]
        normalized_resources.append(
            {
                "logical_id": resource_type.rsplit("/", 1)[-1],
                "type": resource_type,
                "effective_tags": dict(tags),
            }
        )

    return {
        "schema_version": BOUNDARY_SCHEMA_VERSION,
        "contract": {
            "name": metadata.get("name"),
            "version": contract.get("contract_version"),
        },
        "context": {
            "capability": capability,
            "deployment": deployment,
        },
        "provenance": provenance,
        "resources": normalized_resources,
        "deferred": deferred,
    }


def _registry_values(contract: dict[str, Any], name: str) -> set[Any]:
    registries = contract.get("registries")
    if not isinstance(registries, dict) or name not in registries:
        raise InputError(f"rule references missing registry: {name}")
    registry = registries[name]
    if not isinstance(registry, dict) or not isinstance(registry.get("values"), list):
        raise InputError(f"registry has invalid values: {name}")
    return {
        item.get("value") if isinstance(item, dict) else item
        for item in registry["values"]
    }


def _violation(
    rule_id: str,
    resource: dict[str, Any],
    tag_key: str,
    actual: Any,
    expected: str,
    message: str,
    remediation: str,
) -> dict[str, Any]:
    return {
        "rule_id": rule_id,
        "resource": resource["logical_id"],
        "resource_type": resource["type"],
        "tag_key": tag_key,
        "actual": actual,
        "expected": expected,
        "message": message,
        "remediation": remediation,
    }


def validate(document: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    """Evaluate generic V2 assertions against normalized effective metadata."""
    _require_schema(document, "effective metadata")
    metadata = contract.get("metadata")
    governance = contract.get("governance_validation")
    if not isinstance(metadata, dict) or not isinstance(governance, dict):
        raise InputError("contract is missing validation sections")

    expected_contract = {
        "name": metadata.get("name"),
        "version": contract.get("contract_version"),
    }
    if document.get("contract") != expected_contract:
        raise InputError(
            f"effective metadata contract reference must be {expected_contract!r}"
        )

    applicability = governance.get("applicability")
    rules = governance.get("enforceable_rules")
    if not isinstance(applicability, dict) or not isinstance(rules, list):
        raise InputError("contract validation applicability or rules are invalid")
    resource_types = applicability.get("resource_types")
    resources = document.get("resources")
    if not isinstance(resource_types, list) or not isinstance(resources, list):
        raise InputError("effective metadata resources or resource types are invalid")

    by_type = {
        resource.get("type"): resource
        for resource in resources
        if isinstance(resource, dict)
    }
    missing_types = [item for item in resource_types if item not in by_type]
    if missing_types:
        raise InputError(
            "effective metadata is missing applicable resource types: "
            + ", ".join(missing_types)
        )
    applicable_resources = [by_type[item] for item in resource_types]
    for resource in applicable_resources:
        if not isinstance(resource.get("logical_id"), str) or not isinstance(
            resource.get("effective_tags"), dict
        ):
            raise InputError("effective metadata contains an invalid resource")

    context = document.get("context")
    deployment = context.get("deployment") if isinstance(context, dict) else None
    if not isinstance(deployment, dict):
        raise InputError("effective metadata is missing deployment context")
    for field in ("provider", "location"):
        value = deployment.get(field)
        if not isinstance(value, str) or not value:
            raise InputError(
                f"effective metadata deployment {field} must be a non-empty string"
            )
        for resource in applicable_resources:
            tag_value = resource["effective_tags"].get(field)
            if tag_value != value:
                raise InputError(
                    f"{resource['logical_id']} effective tag {field}={tag_value!r} "
                    f"does not match deployment context {field}={value!r}"
                )

    violations: list[dict[str, Any]] = []
    evaluations = 0
    formatting = governance.get("formatting", {}).get("keys_and_values", {})
    if not isinstance(formatting, dict):
        raise InputError("contract formatting rules are invalid")
    for resource in applicable_resources:
        for tag_key, value in resource["effective_tags"].items():
            evaluations += 1
            if not isinstance(tag_key, str) or not isinstance(value, str):
                violations.append(
                    _violation(
                        "formatting",
                        resource,
                        str(tag_key),
                        value,
                        "string tag key and value",
                        f"{resource['logical_id']} tag {tag_key!r} must be a string.",
                        "Provide the governed tag as a string value.",
                    )
                )
                continue
            problems = []
            if formatting.get("lowercase_required") and (
                tag_key != tag_key.lower() or value != value.lower()
            ):
                problems.append("lowercase")
            prohibited = set(formatting.get("prohibited", []))
            if "spaces" in prohibited and (" " in tag_key or " " in value):
                problems.append("no spaces")
            if "underscores" in prohibited and ("_" in tag_key or "_" in value):
                problems.append("no underscores")
            if formatting.get("permitted_separator") == "hyphen":
                for candidate in (tag_key, value):
                    if any(not (character.isalnum() or character == "-") for character in candidate):
                        if "hyphens as separators" not in problems:
                            problems.append("hyphens as separators")
            if problems:
                violations.append(
                    _violation(
                        "formatting",
                        resource,
                        tag_key,
                        value,
                        ", ".join(problems),
                        f"{resource['logical_id']} tag {tag_key}={value!r} violates "
                        f"formatting: {', '.join(problems)}.",
                        "Use lowercase stable identifiers with hyphens as separators.",
                    )
                )

    for rule in rules:
        if not isinstance(rule, dict):
            raise InputError("contract contains a non-object enforceable rule")
        rule_id = rule.get("id")
        assertion = rule.get("assertion")
        if not isinstance(rule_id, str) or not isinstance(assertion, str):
            raise InputError("contract contains an invalid enforceable rule")
        if assertion == "required":
            tag_keys = rule.get("tag_keys")
            if not isinstance(tag_keys, list):
                raise InputError(f"required rule {rule_id} has invalid tag_keys")
            for resource in applicable_resources:
                for tag_key in tag_keys:
                    evaluations += 1
                    value = resource["effective_tags"].get(tag_key)
                    if value is None or value == "":
                        violations.append(
                            _violation(
                                rule_id,
                                resource,
                                tag_key,
                                value,
                                "a non-empty effective tag",
                                f"{resource['logical_id']} is missing required tag "
                                f"{tag_key}.",
                                f"Supply or derive {tag_key} before policy evaluation.",
                            )
                        )
        elif assertion == "registry-membership":
            tag_key = rule.get("tag_key")
            registry_name = rule.get("registry")
            if not isinstance(tag_key, str) or not isinstance(registry_name, str):
                raise InputError(f"registry rule {rule_id} is invalid")
            allowed = _registry_values(contract, registry_name)
            for resource in applicable_resources:
                evaluations += 1
                value = resource["effective_tags"].get(tag_key)
                if value is not None and value not in allowed:
                    violations.append(
                        _violation(
                            rule_id,
                            resource,
                            tag_key,
                            value,
                            f"a value from registry {registry_name}",
                            f"{resource['logical_id']} tag {tag_key}={value!r} "
                            "is not registered.",
                            f"Use a {tag_key} value listed by contract "
                            f"{contract.get('contract_version')}.",
                        )
                    )
        elif assertion == "equals":
            tag_key = rule.get("tag_key")
            expected = rule.get("value")
            if not isinstance(tag_key, str):
                raise InputError(f"equals rule {rule_id} is invalid")
            for resource in applicable_resources:
                evaluations += 1
                value = resource["effective_tags"].get(tag_key)
                if value is not None and value != expected:
                    violations.append(
                        _violation(
                            rule_id,
                            resource,
                            tag_key,
                            value,
                            repr(expected),
                            f"{resource['logical_id']} tag {tag_key} must equal "
                            f"{expected!r}; received {value!r}.",
                            f"Derive {tag_key} from the approved platform context.",
                        )
                    )
        else:
            raise InputError(f"unsupported assertion {assertion!r} in rule {rule_id}")

    return {
        "schema_version": BOUNDARY_SCHEMA_VERSION,
        "result": "FAIL" if violations else "PASS",
        "contract": expected_contract,
        "summary": {
            "resources_evaluated": len(applicable_resources),
            "rules_evaluated": evaluations,
            "violations": len(violations),
        },
        "violations": violations,
    }


def _write_json(path: str | Path, value: dict[str, Any]) -> None:
    try:
        Path(path).write_text(
            json.dumps(value, indent=2, sort_keys=False) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        raise InputError(f"cannot write {path}: {exc}") from exc


def _print_result(result: dict[str, Any]) -> None:
    summary = result["summary"]
    print(
        f"{result['result']}: {summary['resources_evaluated']} resources, "
        f"{summary['rules_evaluated']} evaluations, "
        f"{summary['violations']} violations"
    )
    for violation in result["violations"]:
        print(
            f"- [{violation['rule_id']}] {violation['message']} "
            f"Remediation: {violation['remediation']}"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m policy_validation")
    subparsers = parser.add_subparsers(dest="command", required=True)
    normalize_parser = subparsers.add_parser(
        "normalize", help="construct normalized effective metadata"
    )
    normalize_parser.add_argument("--consumer", required=True)
    normalize_parser.add_argument("--platform", required=True)
    normalize_parser.add_argument("--contract", required=True)
    normalize_parser.add_argument("--output", required=True)
    validate_parser = subparsers.add_parser(
        "validate", help="validate normalized effective metadata"
    )
    validate_parser.add_argument("--input", required=True)
    validate_parser.add_argument("--contract", required=True)
    validate_parser.add_argument(
        "--output", help="optional machine-readable JSON result"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
        contract = load_yaml(args.contract)
        if args.command == "normalize":
            document = normalize(
                load_yaml(args.consumer),
                load_yaml(args.platform),
                contract,
            )
            _write_json(args.output, document)
            print(
                f"Normalized {len(document['resources'])} resources to {args.output} "
                f"using contract {document['contract']['version']}."
            )
            return 0
        result = validate(load_yaml(args.input), contract)
        if args.output:
            _write_json(args.output, result)
        _print_result(result)
        return 0 if result["result"] == "PASS" else 1
    except InputError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # pragma: no cover - final execution boundary
        print(f"ERROR: unexpected validation failure: {exc}", file=sys.stderr)
        return 2
