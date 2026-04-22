from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from spectralbio.sensitivity import build_sensitivity_report


if __name__ == "__main__":
    raise SystemExit(0 if build_sensitivity_report("brca2") else 1)
