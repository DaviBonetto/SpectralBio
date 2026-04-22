"""Structured stats reports for TP53 and BRCA2."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from spectralbio.constants import BLOCK1_RESULTS_DIR, STATS_OUTPUT_DIR
from spectralbio.utils.io import ensure_dir, read_json, write_json


def build_stats_report(target: str, output_dir: Path | None = None) -> dict[str, Any]:
    target_lower = target.lower()
    destination = ensure_dir((output_dir or STATS_OUTPUT_DIR) / target_lower)
    if target_lower == "tp53":
        summary = read_json(Path("outputs/canonical/summary.json"))
        report = {
            "target": "TP53",
            "role": "validation_anchor",
            "metrics": summary["metrics"],
        }
    elif target_lower == "brca2":
        augmentation = read_json(BLOCK1_RESULTS_DIR / "runtime" / "esm1v_augmentation" / "brca2" / "augmentation_summary.json")
        permutation = read_json(BLOCK1_RESULTS_DIR / "runtime" / "esm1v_augmentation" / "esm1v_permutation_audit_summary.json")
        report = {
            "target": "BRCA2",
            "role": "flagship_non_anchor_canonical_target",
            "metrics": {
                "auc_esm1v_mean": augmentation["auc_esm1v_mean"],
                "auc_augmented_pair_fixed_055": augmentation["auc_augmented_pair_fixed_055"],
                "delta_augmented_vs_esm1v": augmentation["delta_augmented_vs_esm1v"],
                "bootstrap_ci_2p5": augmentation["pair_vs_esm1v_bootstrap_delta"]["ci_2p5"],
                "bootstrap_ci_97p5": augmentation["pair_vs_esm1v_bootstrap_delta"]["ci_97p5"],
                "empirical_permutation_p": permutation["genes"]["BRCA2"]["permute_frob_alignment"]["empirical_p_ge_observed"],
            },
        }
    else:
        raise ValueError("stats-report currently supports tp53 and brca2 only.")

    write_json(destination / "stats_report.json", report)
    return report
