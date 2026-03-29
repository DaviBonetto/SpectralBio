"""Placeholder plotting helpers for frozen artifact runs."""

from __future__ import annotations

from pathlib import Path

from spectralbio.constants import PROJECT_ROOT


def copy_reference_figure(destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    source = PROJECT_ROOT / "assets" / "generated" / "tp53_results_overview.png"
    destination.write_bytes(source.read_bytes())
    return destination
