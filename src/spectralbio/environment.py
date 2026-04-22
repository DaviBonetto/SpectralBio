"""Environment, filesystem, and repository health checks."""

from __future__ import annotations

import platform
import shutil
import site
import subprocess
import sys
from pathlib import Path
from typing import Any

from spectralbio.constants import (
    BENCHMARK_REGISTRY_PATH,
    BRCA1_TRANSFER100_PATH,
    BRCA2_BENCHMARK_DIR,
    CHECKSUMS_PATH,
    CREBBP_BENCHMARK_DIR,
    OUTPUT_SCHEMA_PATH,
    PROJECT_ROOT,
    SCHEMAS_DIR,
    TP53_CANONICAL_PATH,
    TP53_SCORE_REFERENCE_PATH,
    TSC2_BENCHMARK_DIR,
    VERIFICATION_RULES_PATH,
)
from spectralbio.utils.hashing import sha256_file
from spectralbio.utils.io import ensure_dir, project_relpath


def _git_output(*args: str) -> str | None:
    try:
        return (
            subprocess.check_output(["git", *args], cwd=PROJECT_ROOT, text=True, stderr=subprocess.DEVNULL)
            .strip()
        )
    except Exception:
        return None


def get_git_commit_hash() -> str | None:
    return _git_output("rev-parse", "HEAD")


def get_uv_lock_hash() -> str | None:
    uv_lock = PROJECT_ROOT / "uv.lock"
    if not uv_lock.exists():
        return None
    return sha256_file(uv_lock)


def get_python_details() -> dict[str, str]:
    return {
        "version": platform.python_version(),
        "implementation": platform.python_implementation(),
        "executable": sys.executable,
    }


def get_uv_available() -> bool:
    if shutil.which("uv") is not None:
        return True
    user_site = Path(site.USER_SITE)
    candidate_paths = [
        user_site.parent / "Scripts" / "uv.exe",
        user_site.parent / "Scripts" / "uv",
        Path(site.USER_BASE) / "Python313" / "Scripts" / "uv.exe",
    ]
    return any(path.exists() for path in candidate_paths)


def ensure_writable(path: Path) -> bool:
    try:
        ensure_dir(path)
        probe = path / ".spectralbio_write_probe"
        probe.write_text("ok\n", encoding="utf-8")
        probe.unlink()
        return True
    except Exception:
        return False


def required_schema_paths() -> list[Path]:
    return [
        SCHEMAS_DIR / "status.schema.json",
        SCHEMAS_DIR / "summary.schema.json",
        SCHEMAS_DIR / "verification.schema.json",
        SCHEMAS_DIR / "provenance.schema.json",
        SCHEMAS_DIR / "stats_report.schema.json",
        SCHEMAS_DIR / "diagnosis.schema.json",
        SCHEMAS_DIR / "manifest.schema.json",
        SCHEMAS_DIR / "benchmark_contract.schema.json",
    ]


def required_replay_assets() -> list[Path]:
    return [
        TP53_CANONICAL_PATH,
        TP53_SCORE_REFERENCE_PATH,
        BRCA1_TRANSFER100_PATH,
        CHECKSUMS_PATH,
        OUTPUT_SCHEMA_PATH,
        VERIFICATION_RULES_PATH,
        BENCHMARK_REGISTRY_PATH,
        BRCA2_BENCHMARK_DIR / "benchmark_contract.json",
        TSC2_BENCHMARK_DIR / "benchmark_contract.json",
        CREBBP_BENCHMARK_DIR / "benchmark_contract.json",
    ]


def collect_environment_report(cache_dir: Path, output_dir: Path, offline: bool, cpu_only: bool) -> dict[str, Any]:
    schema_paths = required_schema_paths()
    replay_assets = required_replay_assets()
    checks = {
        "python_available": True,
        "uv_available": get_uv_available(),
        "cache_dir_writable": ensure_writable(cache_dir),
        "output_dir_writable": ensure_writable(output_dir),
        "schema_files_present": all(path.exists() for path in schema_paths),
        "replay_assets_present": all(path.exists() for path in replay_assets),
        "offline_ready": (not offline) or all(path.exists() for path in replay_assets),
        "cpu_only_supported": cpu_only,
    }
    blocking_checks = {key: value for key, value in checks.items() if key != "uv_available"}
    warnings: list[str] = []
    if not checks["uv_available"]:
        warnings.append("uv is not available on the current shell PATH. The public contract still prefers uv.")
    return {
        "status": "PASS" if all(blocking_checks.values()) else "FAIL",
        "checks": checks,
        "warnings": warnings,
        "python": get_python_details(),
        "git_commit": get_git_commit_hash(),
        "uv_lock_sha256": get_uv_lock_hash(),
        "cache_dir": project_relpath(cache_dir) if cache_dir.exists() else str(cache_dir),
        "output_dir": project_relpath(output_dir) if output_dir.exists() else str(output_dir),
        "missing_schema_files": [project_relpath(path) for path in schema_paths if not path.exists()],
        "missing_replay_assets": [project_relpath(path) for path in replay_assets if not path.exists()],
    }
