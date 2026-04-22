"""Lightweight schema validation helpers for strict JSON contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from spectralbio.errors import SchemaValidationError
from spectralbio.utils.io import read_json


def load_schema(path: Path) -> dict[str, Any]:
    return read_json(path)


def _type_ok(expected_type: str | list[str], value: Any) -> bool:
    if isinstance(expected_type, list):
        return any(_type_ok(item, value) for item in expected_type)
    type_map = {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
    }
    return type_map.get(expected_type, True)


def _validate(schema: dict[str, Any], value: Any, path: str, errors: list[str]) -> None:
    expected_type = schema.get("type")
    if expected_type and not _type_ok(expected_type, value):
        errors.append(f"{path}: expected {expected_type}, got {type(value).__name__}")
        return

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: expected const value {schema['const']!r}, got {value!r}")

    if isinstance(value, dict):
        required = schema.get("required", [])
        for field in required:
            if field not in value:
                errors.append(f"{path}: missing required field '{field}'")
        properties = schema.get("properties", {})
        for key, subschema in properties.items():
            if key in value:
                _validate(subschema, value[key], f"{path}.{key}", errors)

    if isinstance(value, list) and "items" in schema:
        item_schema = schema["items"]
        for index, item in enumerate(value):
            _validate(item_schema, item, f"{path}[{index}]", errors)


def validate_payload(payload: Any, schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    _validate(schema, payload, "$", errors)
    return errors


def validate_payload_file(payload_path: Path, schema_path: Path) -> list[str]:
    return validate_payload(read_json(payload_path), load_schema(schema_path))


def assert_valid_payload(payload: Any, schema: dict[str, Any], schema_path: Path | None = None) -> None:
    errors = validate_payload(payload, schema)
    if errors:
        label = str(schema_path) if schema_path is not None else "inline schema"
        raise SchemaValidationError(f"{label} validation failed: {'; '.join(errors)}")
