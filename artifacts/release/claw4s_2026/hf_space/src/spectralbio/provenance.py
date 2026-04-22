"""Provenance builders for replay and regeneration artifacts."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from spectralbio.constants import PROJECT_ROOT, SEED
from spectralbio.environment import get_git_commit_hash, get_uv_lock_hash
from spectralbio.utils.hashing import sha256_file
from spectralbio.utils.io import project_relpath, write_json


def build_provenance(
    *,
    target: str,
    role: str,
    command: str,
    input_paths: list[Path],
    model_identifiers: list[str],
    source_label: str,
    output_dir: Path,
    seeds: dict[str, int] | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "target": target.upper(),
        "benchmark_role": role,
        "source_label": source_label,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by_command": command,
        "git_commit_hash": get_git_commit_hash(),
        "uv_lock_hash": get_uv_lock_hash(),
        "output_dir": project_relpath(output_dir) if output_dir.exists() else str(output_dir),
        "model_identifiers": model_identifiers,
        "seed_values": seeds or {"global_seed": SEED},
        "inputs": [
            {
                "path": project_relpath(path),
                "sha256": sha256_file(path),
            }
            for path in input_paths
            if path.exists()
        ],
        "assumptions": {
            "offline_replay_supported": True,
            "cpu_only_supported": True,
        },
    }
    if extra:
        payload.update(extra)
    return payload


def write_provenance(path: Path, payload: dict[str, Any]) -> Path:
    return write_json(path, payload)
