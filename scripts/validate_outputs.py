from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from spectralbio.pipeline.verify import verify_run_outputs


if __name__ == "__main__":
    report = verify_run_outputs(ROOT / "outputs" / "canonical", ROOT / "outputs" / "transfer")
    raise SystemExit(0 if report["status"] == "PASS" else 1)
