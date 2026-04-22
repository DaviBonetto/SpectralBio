"""Scale-repair regeneration wrapper using frozen manuscript artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from spectralbio.constants import BLOCK2_RESULTS_DIR
from spectralbio.utils.io import ensure_dir, read_text, write_json, write_text


def materialize_scale_repair_surface(output_dir: Path) -> dict[str, Any]:
    ensure_dir(output_dir)
    summary = {
        "surface": "scale-repair",
        "role": "scientific_audit_surface",
        "source_bundle": "New Notebooks/results/02_block2_failure_mode_hunt_h100",
        "claim": "Scale-repair remains a qualitative centerpiece with deterministic frozen evidence.",
    }
    write_json(output_dir / "summary.json", summary)
    if (BLOCK2_RESULTS_DIR / "text" / "block2_summary.md").exists():
        write_text(
            output_dir / "notes.md",
            read_text(BLOCK2_RESULTS_DIR / "text" / "block2_summary.md"),
        )
    return summary
