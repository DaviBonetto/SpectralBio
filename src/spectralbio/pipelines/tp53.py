"""TP53 replay wrapper built on the canonical frozen execution path."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from spectralbio.constants import CANONICAL_OUTPUT_DIR
from spectralbio.pipeline.run_canonical import run as run_canonical
from spectralbio.utils.io import ensure_dir, read_json, write_json


def materialize_tp53_replay(output_dir: Path) -> dict[str, Any]:
    ensure_dir(output_dir)
    run_canonical(CANONICAL_OUTPUT_DIR)
    summary = read_json(CANONICAL_OUTPUT_DIR / "summary.json")
    manifest = read_json(CANONICAL_OUTPUT_DIR / "manifest.json")
    metrics = read_json(CANONICAL_OUTPUT_DIR / "tp53_metrics.json")
    run_metadata = read_json(CANONICAL_OUTPUT_DIR / "run_metadata.json")

    write_json(output_dir / "summary.json", summary)
    write_json(output_dir / "manifest.json", manifest)
    write_json(output_dir / "metrics.json", metrics)
    write_json(output_dir / "run_metadata.json", run_metadata)
    shutil.copy2(CANONICAL_OUTPUT_DIR / "roc_tp53.png", output_dir / "roc_tp53.png")

    return {
        "target": "tp53",
        "role": "validation_anchor",
        "summary": summary,
        "manifest": manifest,
        "metrics": metrics,
        "model_identifiers": [run_metadata["model_name"]],
        "artifacts_used": [
            "benchmarks/tp53/tp53_canonical_v1.json",
            "benchmarks/tp53/tp53_scores_v1.json",
            "benchmarks/sequences/tp53.fasta",
        ],
        "artifacts_emitted": [
            "summary.json",
            "manifest.json",
            "metrics.json",
            "run_metadata.json",
            "roc_tp53.png",
        ],
    }
