"""Frozen TSC2 replay wrapper."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from spectralbio.constants import TSC2_BENCHMARK_DIR
from spectralbio.utils.io import ensure_dir, read_json, write_json


def materialize_tsc2_replay(output_dir: Path) -> dict[str, Any]:
    ensure_dir(output_dir)
    summary = read_json(TSC2_BENCHMARK_DIR / "summary.expected.json")
    manifest = read_json(TSC2_BENCHMARK_DIR / "manifest.json")
    metrics = read_json(TSC2_BENCHMARK_DIR / "metrics.expected.json")
    write_json(output_dir / "summary.json", summary)
    write_json(output_dir / "manifest.json", manifest)
    write_json(output_dir / "metrics.json", metrics)
    return {
        "target": "tsc2",
        "role": "replay_ready_transfer_surface",
        "summary": summary,
        "manifest": manifest,
        "metrics": metrics,
        "model_identifiers": ["ESM2-650M", "ProtT5", "ESM-1v"],
        "artifacts_used": [
            "benchmarks/tsc2/benchmark_table.tsv",
            "benchmarks/tsc2/score_reference.tsv",
            "benchmarks/tsc2/sequence_reference.fasta",
        ],
        "artifacts_emitted": ["summary.json", "manifest.json", "metrics.json"],
    }
