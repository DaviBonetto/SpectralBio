"""Status bundle helpers for every public command."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from spectralbio.constants import SCHEMAS_DIR, STATUS_OUTPUT_DIR
from spectralbio.io_contracts import assert_valid_payload, load_schema
from spectralbio.utils.io import ensure_dir, write_json, write_text


STATUS_SCHEMA_PATH = SCHEMAS_DIR / "status.schema.json"


def new_run_id(prefix: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}-{timestamp}-{uuid4().hex[:8]}"


def build_status_payload(
    *,
    command: str,
    status: str,
    exit_code: int,
    mode: str,
    target: str | None,
    surface_role: str,
    started_at: str,
    finished_at: str,
    duration_seconds: float,
    offline: bool,
    cpu_only: bool,
    artifacts_used: list[str],
    artifacts_emitted: list[str],
    checks_performed: list[str],
    metrics: dict[str, Any] | None = None,
    warnings: list[str] | None = None,
    next_action: str = "none",
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "command": command,
        "status": status,
        "exit_code": exit_code,
        "mode": mode,
        "target": target.upper() if target else None,
        "surface_role": surface_role,
        "started_at": started_at,
        "finished_at": finished_at,
        "duration_seconds": round(duration_seconds, 6),
        "offline": offline,
        "cpu_only": cpu_only,
        "artifacts_used": artifacts_used,
        "artifacts_emitted": artifacts_emitted,
        "checks_performed": checks_performed,
        "metrics": metrics or {},
        "warnings": warnings or [],
        "next_action": next_action,
        "details": details or {},
    }
    assert_valid_payload(payload, load_schema(STATUS_SCHEMA_PATH), STATUS_SCHEMA_PATH)
    return payload


def write_status_bundle(
    *,
    run_id: str,
    payload: dict[str, Any],
    stdout_text: str,
    stderr_text: str,
    command_text: str,
    root_dir: Path = STATUS_OUTPUT_DIR,
    extra_json_files: dict[str, Any] | None = None,
) -> Path:
    run_dir = ensure_dir(root_dir / run_id)
    write_json(run_dir / "status.json", payload)
    write_text(run_dir / "stdout.log", stdout_text)
    write_text(run_dir / "stderr.log", stderr_text)
    write_text(run_dir / "command.txt", command_text + "\n")
    for filename, extra_payload in (extra_json_files or {}).items():
        write_json(run_dir / filename, extra_payload)
    latest_dir = ensure_dir(root_dir / "latest")
    write_json(latest_dir / "status.json", payload)
    write_text(latest_dir / "stdout.log", stdout_text)
    write_text(latest_dir / "stderr.log", stderr_text)
    write_text(latest_dir / "command.txt", command_text + "\n")
    latest_diagnosis = latest_dir / "diagnosis.json"
    if "diagnosis.json" not in (extra_json_files or {}) and latest_diagnosis.exists():
        latest_diagnosis.unlink()
    for filename, extra_payload in (extra_json_files or {}).items():
        write_json(latest_dir / filename, extra_payload)
    return run_dir


def status_stdout(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2) + "\n"
