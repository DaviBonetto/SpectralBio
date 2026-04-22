from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from spectralbio.regeneration import regenerate_surface


if __name__ == "__main__":
    raise SystemExit(0 if regenerate_surface("holdout-control")["status"] == "PASS" else 1)
