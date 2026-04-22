"""Checksum helpers for replay, regeneration, and release surfaces."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from spectralbio.utils.hashing import sha256_file
from spectralbio.utils.io import project_relpath, write_json


def compute_checksums(paths: list[Path], base_dir: Path | None = None) -> dict[str, str]:
    checksums: dict[str, str] = {}
    for path in paths:
        key = path.name if base_dir is None else path.resolve().relative_to(base_dir.resolve()).as_posix()
        checksums[key] = sha256_file(path)
    return checksums


def verify_checksums(expected: dict[str, str], base_dir: Path) -> dict[str, Any]:
    mismatches: list[dict[str, str]] = []
    for relative_path, expected_sha in expected.items():
        file_path = base_dir / relative_path
        if not file_path.exists():
            mismatches.append(
                {
                    "path": relative_path,
                    "expected_sha256": expected_sha,
                    "actual_sha256": "MISSING",
                }
            )
            continue
        actual_sha = sha256_file(file_path)
        if actual_sha != expected_sha:
            mismatches.append(
                {
                    "path": relative_path,
                    "expected_sha256": expected_sha,
                    "actual_sha256": actual_sha,
                }
            )
    return {
        "status": "PASS" if not mismatches else "FAIL",
        "mismatches": mismatches,
    }


def write_checksums(path: Path, files: list[Path], base_dir: Path) -> Path:
    payload = {
        "base_dir": project_relpath(base_dir) if base_dir.exists() else str(base_dir),
        "sha256": compute_checksums(files, base_dir=base_dir),
    }
    return write_json(path, payload)
