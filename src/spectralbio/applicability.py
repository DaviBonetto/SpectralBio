"""Bounded applicability diagnostics for new targets."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from spectralbio.utils.io import write_json


def _read_variants(variants_path: Path) -> list[dict[str, str]]:
    delimiter = "\t" if variants_path.suffix.lower() == ".tsv" else ","
    with variants_path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter=delimiter))


def evaluate_applicability(gene: str, variants: Path, reference: Path, output_path: Path | None = None) -> dict[str, Any]:
    rows = _read_variants(variants)
    reference_text = reference.read_text(encoding="utf-8")
    label_values = [row.get("label", "") for row in rows]
    positives = sum(1 for value in label_values if str(value) == "1")
    negatives = sum(1 for value in label_values if str(value) == "0")
    if len(rows) >= 100 and positives >= 20 and negatives >= 20 and reference_text.startswith(">"):
        category = "likely_helpful"
    elif len(rows) >= 25 and reference_text.startswith(">"):
        category = "likely_bounded"
    else:
        category = "likely_not_recommended"

    report = {
        "status": "PASS",
        "gene": gene.upper(),
        "category": category,
        "details": {
            "n_variants": len(rows),
            "n_positive": positives,
            "n_negative": negatives,
            "reference_loaded": reference_text.startswith(">"),
            "recommendation": "Bounded diagnostic only. No universal transfer claim.",
        },
    }
    if output_path is not None:
        write_json(output_path, report)
    return report
