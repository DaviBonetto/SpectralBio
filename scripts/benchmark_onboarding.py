from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from spectralbio.adapt import create_adaptation_scaffold


if __name__ == "__main__":
    output = create_adaptation_scaffold(
        "EXAMPLE",
        ROOT / "benchmarks" / "tp53" / "tp53_canonical_v1.json",
        ROOT / "benchmarks" / "sequences" / "tp53.fasta",
        ROOT / "artifacts" / "onboarding",
    )
    raise SystemExit(0 if output["status"] == "PASS" else 1)
