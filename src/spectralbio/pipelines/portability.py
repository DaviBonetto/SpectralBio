"""Portability regeneration wrapper using frozen Block 13 outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from spectralbio.constants import BLOCK13_RESULTS_DIR
from spectralbio.utils.io import ensure_dir, read_json, write_json, write_text, read_text


def materialize_portability_surface(output_dir: Path) -> dict[str, Any]:
    ensure_dir(output_dir)
    summary = read_json(BLOCK13_RESULTS_DIR / "manifests" / "claim_summary.json")
    write_json(output_dir / "summary.json", summary)
    write_json(
        output_dir / "replay_target_contracts.json",
        {
            "table_source": "New Notebooks/results/13_block13_multitarget_generalization_closure_h100/tables/replay_target_contracts.csv",
        },
    )
    write_text(output_dir / "notes.md", read_text(BLOCK13_RESULTS_DIR / "text" / "block13_summary.md"))
    return summary
