"""Holdout/control regeneration wrapper using frozen Block 14 outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from spectralbio.constants import BLOCK14_RESULTS_DIR
from spectralbio.utils.io import ensure_dir, read_json, write_json


def materialize_holdout_control_surface(output_dir: Path) -> dict[str, Any]:
    ensure_dir(output_dir)
    summary = read_json(BLOCK14_RESULTS_DIR / "manifests" / "block14_claim_summary.json")
    write_json(output_dir / "summary.json", summary)
    return summary
