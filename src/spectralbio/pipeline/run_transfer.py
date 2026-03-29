"""Bounded BRCA1 transfer execution path."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from spectralbio.configs import load_brca1_transfer_config
from spectralbio.constants import (
    BRCA1_FULL_FILTERED_PATH,
    BRCA1_TRANSFER_CONFIG_PATH,
    BRCA1_TRANSFER100_PATH,
    BRCA1_SEQUENCE_PATH,
    SECONDARY_CLAIM,
    TRANSFER_COMMAND,
)
from spectralbio.data.load_benchmarks import (
    load_brca1_full_filtered,
    load_brca1_transfer100,
    load_expected_files,
    load_expected_metrics,
)
from spectralbio.utils.io import ensure_dir, project_relpath, write_json


def _validate_config() -> None:
    config = load_brca1_transfer_config()
    expected = {
        "benchmark": "BRCA1_transfer100",
        "role": "secondary_bounded_transfer",
        "variants_path": project_relpath(BRCA1_TRANSFER100_PATH),
        "output_dir": "outputs/transfer",
        "scope_note": SECONDARY_CLAIM,
    }
    for key, expected_value in expected.items():
        actual_value = config.get(key)
        if actual_value != expected_value:
            raise ValueError(
                f"configs/brca1_transfer.yaml drifted for '{key}': expected {expected_value!r}, got {actual_value!r}."
            )


def run(output_dir: Path) -> dict[str, Any]:
    _validate_config()
    ensure_dir(output_dir)

    variants = load_brca1_transfer100()
    full_filtered = load_brca1_full_filtered()
    expected_metrics = load_expected_metrics()["transfer"]
    artifact_files = load_expected_files()["transfer_run"]
    if len(variants) != expected_metrics["n_total"] or variants != full_filtered[: expected_metrics["n_total"]]:
        raise ValueError("BRCA1 transfer path must remain the frozen fixed first-100 subset.")

    manifest = {
        "benchmark": "BRCA1_transfer100",
        "role": "secondary_bounded_transfer",
        "source_variants": project_relpath(BRCA1_TRANSFER100_PATH),
        "source_provenance": project_relpath(BRCA1_FULL_FILTERED_PATH),
        "sequence_source": project_relpath(BRCA1_SEQUENCE_PATH),
        "config_path": project_relpath(BRCA1_TRANSFER_CONFIG_PATH),
        "selection_rule": "fixed first 100 records from brca1_full_filtered_v1.json in source order",
        "expected_variant_count": expected_metrics["n_total"],
        "secondary_claim": SECONDARY_CLAIM,
        "artifacts": artifact_files,
    }
    summary = {
        "benchmark": "BRCA1_transfer100",
        "role": "secondary_bounded_transfer",
        "secondary_claim": SECONDARY_CLAIM,
        "config_path": project_relpath(BRCA1_TRANSFER_CONFIG_PATH),
        "source_variants": project_relpath(BRCA1_TRANSFER100_PATH),
        "n_total": expected_metrics["n_total"],
        "metrics": {
            "official_ll_proper_auc": expected_metrics["ll_proper_auc"],
        },
        "artifacts": artifact_files,
        "scope_note": SECONDARY_CLAIM,
        "command": TRANSFER_COMMAND,
    }

    write_json(output_dir / "variants.json", variants)
    write_json(output_dir / "manifest.json", manifest)
    write_json(output_dir / "summary.json", summary)
    return {
        "status": "PASS",
        "command": TRANSFER_COMMAND,
        "output_dir": str(output_dir),
        "summary": summary,
    }
