"""Canonical TP53 execution path."""

from __future__ import annotations

from pathlib import Path
import shutil
from typing import Any

from spectralbio.configs import load_tp53_config
from spectralbio.constants import (
    CANONICAL_COMMAND,
    CHECKSUMS_PATH,
    MODEL_NAME,
    PRIMARY_CLAIM,
    SEED,
    TP53_BENCHMARK_MANIFEST_PATH,
    TP53_CANONICAL_PATH,
    TP53_CONFIG_PATH,
    TP53_SCORE_REFERENCE_PATH,
    TP53_SEQUENCE_PATH,
)
from spectralbio.data.load_benchmarks import (
    load_expected_files,
    load_expected_metrics,
    load_tp53_scores,
    load_tp53_variants,
)
from spectralbio.pipeline.evaluate import canonical_metrics
from spectralbio.pipeline.plot_results import copy_reference_figure
from spectralbio.pipeline.verify import build_partial_verification_report
from spectralbio.utils.hashing import sha256_file
from spectralbio.utils.io import ensure_dir, project_relpath, write_json, write_tsv


def _validate_config() -> None:
    config = load_tp53_config()
    expected = {
        "benchmark": "TP53",
        "role": "canonical_benchmark",
        "variants_path": project_relpath(TP53_CANONICAL_PATH),
        "scores_path": project_relpath(TP53_SCORE_REFERENCE_PATH),
        "output_dir": "outputs/canonical",
    }
    for key, expected_value in expected.items():
        actual_value = config.get(key)
        if actual_value != expected_value:
            raise ValueError(
                f"configs/tp53_canonical.yaml drifted for '{key}': expected {expected_value!r}, got {actual_value!r}."
            )


def run(output_dir: Path) -> dict[str, Any]:
    _validate_config()
    ensure_dir(output_dir)
    for child in output_dir.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()

    variants = load_tp53_variants()
    scores = load_tp53_scores()
    metrics = canonical_metrics(scores)
    expected_metrics = load_expected_metrics()["canonical"]
    artifact_files = load_expected_files()["canonical_run"]

    if len(variants) != expected_metrics["n_total"] or len(scores) != expected_metrics["n_total"]:
        raise ValueError("TP53 canonical inputs drifted from the frozen expected count.")

    manifest = {
        "benchmark": "TP53",
        "role": "canonical_benchmark",
        "source_variants": project_relpath(TP53_CANONICAL_PATH),
        "score_reference_source": project_relpath(TP53_SCORE_REFERENCE_PATH),
        "sequence_source": project_relpath(TP53_SEQUENCE_PATH),
        "benchmark_manifest": project_relpath(TP53_BENCHMARK_MANIFEST_PATH),
        "config_path": project_relpath(TP53_CONFIG_PATH),
        "primary_claim": PRIMARY_CLAIM,
        "artifacts": artifact_files,
    }
    run_metadata = {
        "benchmark": "TP53",
        "mode": "canonical",
        "seed": SEED,
        "model_name": MODEL_NAME,
        "score_formula": expected_metrics["best_pair_desc"],
        "command": CANONICAL_COMMAND,
        "config_path": project_relpath(TP53_CONFIG_PATH),
    }
    inputs_manifest = {
        "variants_source": project_relpath(TP53_CANONICAL_PATH),
        "variants_sha256": sha256_file(TP53_CANONICAL_PATH),
        "score_reference_source": project_relpath(TP53_SCORE_REFERENCE_PATH),
        "score_reference_sha256": sha256_file(TP53_SCORE_REFERENCE_PATH),
        "sequence_source": project_relpath(TP53_SEQUENCE_PATH),
        "benchmark_manifest": project_relpath(TP53_BENCHMARK_MANIFEST_PATH),
        "checksums_ref": project_relpath(CHECKSUMS_PATH),
        "n_variants": len(variants),
    }
    tp53_metrics = {
        "official_auc_best_pair": expected_metrics["auc_best_pair"],
        "computed_auc_best_pair": metrics["auc_best_pair"],
        "computed_auc_frob_dist": metrics["auc_frob_dist"],
        "computed_auc_ll_proper": metrics["auc_ll_proper"],
        "best_pair_desc": expected_metrics["best_pair_desc"],
        "reproducibility_delta": expected_metrics["reproducibility_delta"],
    }
    summary = {
        "benchmark": "TP53",
        "role": "canonical_benchmark",
        "primary_claim": PRIMARY_CLAIM,
        "command": CANONICAL_COMMAND,
        "config_path": project_relpath(TP53_CONFIG_PATH),
        "source_variants": project_relpath(TP53_CANONICAL_PATH),
        "n_total": expected_metrics["n_total"],
        "metrics": tp53_metrics,
        "artifacts": artifact_files,
        "non_claims": [
            "No broad default any-protein workflow claim.",
            "No clinical use claim.",
        ],
    }

    write_json(output_dir / "run_metadata.json", run_metadata)
    write_json(output_dir / "inputs_manifest.json", inputs_manifest)
    write_tsv(output_dir / "tp53_scores.tsv", scores)
    write_json(output_dir / "tp53_metrics.json", tp53_metrics)
    write_json(output_dir / "manifest.json", manifest)
    write_json(output_dir / "summary.json", summary)
    copy_reference_figure(output_dir / "roc_tp53.png")
    write_json(output_dir / "verification.json", {"status": "PENDING"})

    verification = build_partial_verification_report(output_dir)
    write_json(output_dir / "verification.json", verification)
    return {
        "status": "PASS" if verification["canonical"]["status"] == "PASS" else "FAIL",
        "command": CANONICAL_COMMAND,
        "output_dir": str(output_dir),
        "summary": summary,
        "verification": verification,
    }
