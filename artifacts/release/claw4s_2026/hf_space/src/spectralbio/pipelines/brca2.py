"""Frozen BRCA2 replay wrapper."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from spectralbio.constants import BRCA2_BENCHMARK_DIR
from spectralbio.utils.io import ensure_dir, read_json, write_json


def materialize_brca2_replay(output_dir: Path) -> dict[str, Any]:
    ensure_dir(output_dir)
    summary = read_json(BRCA2_BENCHMARK_DIR / "summary.expected.json")
    manifest = read_json(BRCA2_BENCHMARK_DIR / "manifest.json")
    metrics = read_json(BRCA2_BENCHMARK_DIR / "metrics.expected.json")
    write_json(output_dir / "summary.json", summary)
    write_json(output_dir / "manifest.json", manifest)
    write_json(output_dir / "metrics.json", metrics)
    return {
        "target": "brca2",
        "role": "flagship_non_anchor_canonical_target",
        "summary": summary,
        "manifest": manifest,
        "metrics": metrics,
        "model_identifiers": [
            "facebook/esm2_t30_150M_UR50D",
            "facebook/esm1v_t33_650M_UR90S_ensemble_mean",
        ],
        "artifacts_used": [
            "benchmarks/brca2/benchmark_table.tsv",
            "benchmarks/brca2/score_reference.tsv",
            "benchmarks/brca2/sequence_reference.fasta",
        ],
        "artifacts_emitted": ["summary.json", "manifest.json", "metrics.json"],
    }
