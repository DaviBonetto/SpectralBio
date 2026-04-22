"""Replay orchestration built on top of the frozen repository surfaces."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any, Callable

from spectralbio.benchmark_registry import get_target, list_targets
from spectralbio.checksums import write_checksums
from spectralbio.constants import BENCHMARKS_DIR, REPLAY_OUTPUT_DIR, REPLAY_TARGETS, STATUS_OUTPUT_DIR
from spectralbio.pipelines import (
    materialize_brca2_replay,
    materialize_crebbp_replay,
    materialize_tp53_replay,
    materialize_tsc2_replay,
)
from spectralbio.provenance import build_provenance, write_provenance
from spectralbio.status import build_status_payload
from spectralbio.utils.io import ensure_dir, project_relpath, write_json
from spectralbio.verification import verify_replay_audit, verify_target_bundle


REPLAY_HANDLERS: dict[str, Callable[[Path], dict[str, Any]]] = {
    "tp53": materialize_tp53_replay,
    "brca2": materialize_brca2_replay,
    "tsc2": materialize_tsc2_replay,
    "crebbp": materialize_crebbp_replay,
}


def run_replay_target(
    target: str,
    *,
    output_dir: Path | None = None,
    offline: bool = True,
    cpu_only: bool = True,
) -> dict[str, Any]:
    target_lower = target.lower()
    target_meta = get_target(target_lower)
    started = datetime.now(timezone.utc).isoformat()
    timer = perf_counter()
    target_dir = ensure_dir(output_dir or (REPLAY_OUTPUT_DIR / target_lower))
    handler = REPLAY_HANDLERS[target_lower]
    payload = handler(target_dir)
    benchmark_dir = BENCHMARKS_DIR / target_lower
    input_paths = [path for path in benchmark_dir.iterdir() if path.is_file()] if benchmark_dir.exists() else []

    provenance = build_provenance(
        target=target_lower,
        role=target_meta["role_label"],
        command=f"spectralbio replay --target {target_lower}",
        input_paths=input_paths,
        model_identifiers=payload["model_identifiers"],
        source_label=target_meta["source_label"],
        output_dir=target_dir,
        extra={"target_metadata": target_meta},
    )
    write_provenance(target_dir / "provenance.json", provenance)

    checksummed_paths = [
        target_dir / "summary.json",
        target_dir / "manifest.json",
        target_dir / "metrics.json",
        target_dir / "provenance.json",
    ]
    if (target_dir / "run_metadata.json").exists():
        checksummed_paths.append(target_dir / "run_metadata.json")
    if (target_dir / "roc_tp53.png").exists():
        checksummed_paths.append(target_dir / "roc_tp53.png")
    write_checksums(target_dir / "checksums.json", checksummed_paths, target_dir)

    verification = verify_target_bundle(target_lower, target_dir)
    finished = datetime.now(timezone.utc).isoformat()
    status = build_status_payload(
        command=f"spectralbio replay --target {target_lower}",
        status=verification["status"],
        exit_code=0 if verification["status"] == "PASS" else 1,
        mode="replay",
        target=target_lower,
        surface_role=target_meta["role_label"],
        started_at=started,
        finished_at=finished,
        duration_seconds=perf_counter() - timer,
        offline=offline,
        cpu_only=cpu_only,
        artifacts_used=payload["artifacts_used"],
        artifacts_emitted=[project_relpath(path) for path in target_dir.iterdir() if path.is_file()],
        checks_performed=["schema_validation", "checksum_validation", "target_verification"],
        metrics=payload["metrics"],
        warnings=[],
        next_action="none" if verification["status"] == "PASS" else f"spectralbio verify --target {target_lower}",
    )
    write_json(target_dir / "status.json", status)
    verification = verify_target_bundle(target_lower, target_dir)
    return {
        "status": verification["status"],
        "target": target_lower,
        "output_dir": str(target_dir),
        "summary": payload["summary"],
        "verification": verification,
        "status_payload": status,
    }


def run_replay_audit(*, offline: bool = True, cpu_only: bool = True) -> dict[str, Any]:
    per_target = {
        target: run_replay_target(target, offline=offline, cpu_only=cpu_only)
        for target in REPLAY_TARGETS
    }
    merged = verify_replay_audit(list(REPLAY_TARGETS))
    summary = {
        "status": merged["status"],
        "replay_targets": [entry["target"] for entry in list_targets() if entry["replay_ready"]],
        "transfer_positive_targets": [entry["target"].upper() for entry in list_targets() if entry.get("transfer_positive")],
        "negative_guardrails": [entry["target"].upper() for entry in list_targets() if entry["role_label"] == "negative_guardrail"],
        "targets": {target: result["status"] for target, result in per_target.items()},
    }
    ensure_dir(REPLAY_OUTPUT_DIR)
    write_json(REPLAY_OUTPUT_DIR / "replay_audit_summary.json", summary)
    return summary
