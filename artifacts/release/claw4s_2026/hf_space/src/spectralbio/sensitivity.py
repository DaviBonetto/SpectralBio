"""Bounded sensitivity reports from frozen alpha sweeps."""

from __future__ import annotations

from pathlib import Path
import csv
from typing import Any

from spectralbio.constants import BLOCK1_RESULTS_DIR, STATS_OUTPUT_DIR
from spectralbio.utils.io import ensure_dir, write_json


def build_sensitivity_report(target: str, output_dir: Path | None = None) -> dict[str, Any]:
    target_upper = target.upper()
    table_path = BLOCK1_RESULTS_DIR / "tables" / "baseline_alpha_audit_auc_table.csv"
    rows: list[dict[str, Any]] = []
    with table_path.open(encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row.get("gene", "").upper() == target_upper:
                rows.append(row)
    report = {
        "target": target_upper,
        "role": "sensitivity_audit",
        "metrics": {
            "alpha_grid_points": len(rows),
            "rows": rows,
        },
    }
    destination = ensure_dir((output_dir or STATS_OUTPUT_DIR) / target.lower())
    write_json(destination / "sensitivity.json", report)
    return report
