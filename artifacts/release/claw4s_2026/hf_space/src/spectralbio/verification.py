"""Targeted verification for replay bundles and regeneration artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from spectralbio.checksums import verify_checksums
from spectralbio.constants import OUTPUTS_DIR, REPLAY_OUTPUT_DIR, SCHEMAS_DIR
from spectralbio.errors import MissingArtifactError
from spectralbio.io_contracts import load_schema, validate_payload_file
from spectralbio.utils.io import read_json, write_json


def _schema_errors_for_bundle(bundle_dir: Path) -> list[str]:
    schema_map = {
        "summary.json": SCHEMAS_DIR / "summary.schema.json",
        "manifest.json": SCHEMAS_DIR / "manifest.schema.json",
        "provenance.json": SCHEMAS_DIR / "provenance.schema.json",
        "status.json": SCHEMAS_DIR / "status.schema.json",
    }
    errors: list[str] = []
    for filename, schema_path in schema_map.items():
        file_path = bundle_dir / filename
        if file_path.exists():
            for error in validate_payload_file(file_path, schema_path):
                errors.append(f"{filename}: {error}")
    return errors


def verify_target_bundle(target: str, bundle_dir: Path | None = None) -> dict[str, Any]:
    target_lower = target.lower()
    directory = bundle_dir or (REPLAY_OUTPUT_DIR / target_lower)
    if not directory.exists():
        raise MissingArtifactError(f"Replay bundle missing: {directory}")

    summary = read_json(directory / "summary.json")
    manifest = read_json(directory / "manifest.json")
    metrics = read_json(directory / "metrics.json")
    checksums_payload = read_json(directory / "checksums.json")
    provenance = read_json(directory / "provenance.json")
    schema_errors = _schema_errors_for_bundle(directory)
    checksum_report = verify_checksums(checksums_payload["sha256"], directory)

    checks = {
        "summary_present": True,
        "manifest_present": True,
        "metrics_present": True,
        "provenance_present": True,
        "schema_validation": not schema_errors,
        "checksum_validation": checksum_report["status"] == "PASS",
        "benchmark_matches_manifest": summary["benchmark"].upper() == manifest["benchmark"].upper(),
        "metrics_nonempty": bool(metrics),
    }
    errors = list(schema_errors)
    errors.extend([f"checksum mismatch: {item['path']}" for item in checksum_report["mismatches"]])
    if not checks["benchmark_matches_manifest"]:
        errors.append("summary benchmark and manifest benchmark diverged.")
    report = {
        "status": "PASS" if not errors else "FAIL",
        "checks": checks,
        "errors": errors,
        "target": target_lower,
        "role": provenance["benchmark_role"],
    }
    write_json(directory / "verification.json", report)
    return report


def verify_replay_audit(targets: list[str]) -> dict[str, Any]:
    per_target = {target: verify_target_bundle(target) for target in targets}
    return {
        "status": "PASS" if all(report["status"] == "PASS" for report in per_target.values()) else "FAIL",
        "targets": per_target,
    }
