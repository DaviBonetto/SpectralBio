"""Run the canonical SpectralBio preflight checks."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from spectralbio.cli import export_hf_dataset, export_hf_space
from spectralbio.constants import CANONICAL_OUTPUT_DIR, TRANSFER_OUTPUT_DIR
from spectralbio.pipeline.run_canonical import run as run_canonical
from spectralbio.pipeline.run_transfer import run as run_transfer
from spectralbio.pipeline.verify import verify_run_outputs, verify_text_contract

REPORT_PATH = ROOT / "temporario" / "fase_06_validation_submission" / "evidence" / "preflight_results.md"


def main() -> int:
    canonical_dir = CANONICAL_OUTPUT_DIR
    transfer_dir = TRANSFER_OUTPUT_DIR

    run_canonical(canonical_dir)
    run_transfer(transfer_dir)
    export_hf_space()
    export_hf_dataset()

    output_checks = verify_run_outputs(canonical_dir, transfer_dir)
    text_checks = verify_text_contract(
        [
            ROOT / "README.md",
            ROOT / "SKILL.md",
            ROOT / "publish" / "hf_dataset" / "README.md",
            ROOT / "publish" / "hf_space" / "README.md",
            ROOT / "paper" / "spectralbio.tex",
        ]
    )

    success = (
        output_checks["status"] == "PASS"
        and not text_checks["forbidden_hits"]
        and text_checks["required_phrase_present"]
    )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        "\n".join(
            [
                "# Preflight Results",
                "",
                f"- Status: {'PASS' if success else 'FAIL'}",
                f"- Output checks: `{json.dumps(output_checks, sort_keys=True)}`",
                f"- Text checks: `{json.dumps(text_checks, sort_keys=True)}`",
            ]
        ),
        encoding="utf-8",
    )
    print(REPORT_PATH)
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
