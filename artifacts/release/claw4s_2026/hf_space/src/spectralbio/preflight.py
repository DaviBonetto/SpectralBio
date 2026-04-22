"""First-class preflight and doctor entrypoints."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from spectralbio.environment import collect_environment_report


def run_preflight(cache_dir: Path, output_dir: Path, offline: bool, cpu_only: bool) -> dict[str, Any]:
    report = collect_environment_report(cache_dir, output_dir, offline=offline, cpu_only=cpu_only)
    report["command"] = "spectralbio preflight"
    report["mode"] = "preflight"
    return report


def run_doctor(cache_dir: Path, output_dir: Path, offline: bool, cpu_only: bool) -> dict[str, Any]:
    report = collect_environment_report(cache_dir, output_dir, offline=offline, cpu_only=cpu_only)
    diagnosis = {
        "status": report["status"],
        "category": "healthy" if report["status"] == "PASS" else "environment_failure",
        "summary": "Replay environment is healthy." if report["status"] == "PASS" else "Replay environment is not ready.",
        "recommended_fix": "none" if report["status"] == "PASS" else "Restore missing replay assets and schema files, then rerun `uv run spectralbio preflight`.",
        "details": report,
    }
    return diagnosis
