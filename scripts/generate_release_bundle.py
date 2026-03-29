"""Build the SpectralBio release bundle."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from spectralbio.cli import release_bundle


if __name__ == "__main__":
    destination = release_bundle()
    print(destination)
