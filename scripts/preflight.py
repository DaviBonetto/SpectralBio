"""Run the first-class SpectralBio preflight and stage a markdown report."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from spectralbio.constants import REPLAY_OUTPUT_DIR
from spectralbio.preflight import run_preflight

REPORT_PATH = ROOT / "temporario" / "fase_06_validation_submission" / "evidence" / "preflight_results.md"


def main() -> int:
    report = run_preflight(
        cache_dir=ROOT / ".cache" / "spectralbio",
        output_dir=REPLAY_OUTPUT_DIR,
        offline=True,
        cpu_only=True,
    )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        "\n".join(
            [
                "# Preflight Results",
                "",
                f"- Status: {report['status']}",
                f"- Checks: `{json.dumps(report['checks'], sort_keys=True)}`",
                f"- Missing replay assets: `{json.dumps(report['missing_replay_assets'], sort_keys=True)}`",
                f"- Missing schema files: `{json.dumps(report['missing_schema_files'], sort_keys=True)}`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(REPORT_PATH)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
