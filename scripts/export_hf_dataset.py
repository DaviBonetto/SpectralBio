"""Export the canonical Hugging Face dataset bundle."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from spectralbio.cli import export_hf_dataset


if __name__ == "__main__":
    destination = export_hf_dataset()
    print(destination)
