from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from spectralbio.provenance import build_provenance
from spectralbio.utils.io import write_json


if __name__ == "__main__":
    payload = build_provenance(
        target="manual",
        role="support_script",
        command="python scripts/build_provenance.py",
        input_paths=[],
        model_identifiers=[],
        source_label="manual_script",
        output_dir=ROOT / "outputs",
    )
    write_json(ROOT / "outputs" / "provenance_manual.json", payload)
    raise SystemExit(0)
