"""Shared single-variant scoring contract used by thin clients."""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any

from spectralbio.constants import (
    ADAPTATION_CLAIM,
    ALPHA,
    PRIMARY_CLAIM,
    SECONDARY_CLAIM,
    SEED,
    TP53_SEQUENCE,
)
from spectralbio.data.load_benchmarks import (
    load_brca1_transfer100,
    load_expected_metrics,
    load_tp53_scores,
    lookup_variant,
)
from spectralbio.data.sequences import load_brca1_sequence
from spectralbio.pipeline.combine_scores import combined_score

CONTRACT_VERSION = "spectralbio.demo.v1"
ARTIFACT_NOTE = "research reproducibility artifact"
SECONDARY_TRANSFER_NOTE = "secondary transfer evaluation without retraining"
PRIMARY_BENCHMARK_ROLE = "primary_canonical"
SECONDARY_BENCHMARK_ROLE = "secondary_bounded_transfer"

AA_LIST = list("ACDEFGHIKLMNPQRSTVWY")
AA_SET = set(AA_LIST)
AA_TO_THREE = {
    "A": "Ala",
    "C": "Cys",
    "D": "Asp",
    "E": "Glu",
    "F": "Phe",
    "G": "Gly",
    "H": "His",
    "I": "Ile",
    "K": "Lys",
    "L": "Leu",
    "M": "Met",
    "N": "Asn",
    "P": "Pro",
    "Q": "Gln",
    "R": "Arg",
    "S": "Ser",
    "T": "Thr",
    "V": "Val",
    "W": "Trp",
    "Y": "Tyr",
}

GENE_CHOICES = (
    ("TP53 | primary canonical benchmark", "TP53"),
    ("BRCA1 | secondary bounded transfer example", "BRCA1"),
)

PRESETS = {
    "TP53 | R175H | canonical benchmark example": {
        "gene": "TP53",
        "position_0_indexed": 174,
        "mutant_aa": "H",
        "benchmark_role": PRIMARY_BENCHMARK_ROLE,
        "ui_story": "tp53_default_preset",
    },
    "TP53 | R273H | canonical benchmark example": {
        "gene": "TP53",
        "position_0_indexed": 272,
        "mutant_aa": "H",
        "benchmark_role": PRIMARY_BENCHMARK_ROLE,
        "ui_story": "tp53_primary_example",
    },
    "BRCA1 | A1708E | secondary bounded transfer example": {
        "gene": "BRCA1",
        "position_0_indexed": 1707,
        "mutant_aa": "E",
        "benchmark_role": SECONDARY_BENCHMARK_ROLE,
        "ui_story": "brca1_secondary_example",
    },
    "BRCA1 | M1775R | secondary bounded transfer example": {
        "gene": "BRCA1",
        "position_0_indexed": 1774,
        "mutant_aa": "R",
        "benchmark_role": SECONDARY_BENCHMARK_ROLE,
        "ui_story": "brca1_secondary_example",
    },
}
PRESET_NAMES = tuple(PRESETS.keys())
DEFAULT_PRESET_NAME = PRESET_NAMES[0]


@lru_cache(maxsize=1)
def _official_metrics_cached() -> dict[str, Any]:
    return load_expected_metrics()


def official_metrics() -> dict[str, Any]:
    return deepcopy(_official_metrics_cached())


@lru_cache(maxsize=1)
def reference_distribution() -> tuple[list[float], float, float]:
    rows = load_tp53_scores()
    combined_scores = [combined_score(float(row["frob_dist"]), float(row["ll_proper"]), alpha=ALPHA) for row in rows]
    return combined_scores, min(combined_scores), max(combined_scores)


@lru_cache(maxsize=2)
def _wildtype_bundle(gene: str) -> tuple[str, Any, Any, Any, dict[str, int]]:
    from spectralbio.pipeline.compute_hidden_states import model_bundle

    gene_upper = gene.upper()
    if gene_upper == "TP53":
        sequence = TP53_SEQUENCE
    elif gene_upper == "BRCA1":
        sequence = load_brca1_sequence()
    else:
        raise ValueError(f"Unsupported gene: {gene}")

    tokenizer, model, device, aa_token_ids = model_bundle()
    return sequence, tokenizer, model, device, aa_token_ids


def combined_percentile(raw_score: float) -> float:
    distribution, _, _ = reference_distribution()
    percentile = float(sum(score <= raw_score for score in distribution) / len(distribution) * 100.0)
    return round(percentile, 2)


def classification_from_percent(percentile: float) -> tuple[str, str]:
    if percentile >= 90.0:
        return "high pathogenicity signal", "high_signal"
    if percentile >= 70.0:
        return "moderate pathogenicity signal", "moderate_signal"
    if percentile >= 40.0:
        return "uncertain / intermediate signal", "intermediate_signal"
    return "lower pathogenicity signal", "lower_signal"


def _protein_variant(position_0_indexed: int, wt_aa: str, mut_aa: str) -> str:
    position_1_indexed = position_0_indexed + 1
    wt_three = AA_TO_THREE.get(wt_aa.upper(), wt_aa.upper())
    mut_three = AA_TO_THREE.get(mut_aa.upper(), mut_aa.upper())
    return f"p.{wt_three}{position_1_indexed}{mut_three}"


def _scope_note(gene: str) -> str:
    if gene.upper() == "TP53":
        return PRIMARY_CLAIM
    return f"{SECONDARY_CLAIM} {ADAPTATION_CLAIM}"


def benchmark_role_for_gene(gene: str) -> str:
    if gene.upper() == "TP53":
        return PRIMARY_BENCHMARK_ROLE
    return SECONDARY_BENCHMARK_ROLE


def _benchmark_annotation(gene: str, position_1_indexed: int, mut_aa: str) -> str:
    matched = lookup_variant(gene, position_1_indexed, mut_aa)
    if matched is None:
        return "Variant not found in the frozen public benchmark files."
    if gene.upper() == "TP53":
        return "Variant found in the TP53 canonical benchmark."
    transfer_rows = load_brca1_transfer100()
    in_transfer = any(
        int(row.get("position", -1)) == position_1_indexed and str(row.get("mut_aa", "")).upper() == mut_aa.upper()
        for row in transfer_rows
    )
    if in_transfer:
        return "Variant found in the bounded BRCA1 transfer subset (N=100)."
    return "Variant found in BRCA1 full filtered provenance data, outside the canonical transfer subset."


def preset_metadata(preset_name: str) -> dict[str, Any]:
    return PRESETS[preset_name].copy()


def _preset_matches_variant(metadata: dict[str, Any], gene: str, position_0_indexed: int, mutant_aa: str) -> bool:
    return (
        metadata["gene"] == gene.upper().strip()
        and metadata["position_0_indexed"] == position_0_indexed
        and metadata["mutant_aa"] == mutant_aa.upper().strip()
    )


def infer_preset_name(gene: str, position_0_indexed: int, mutant_aa: str) -> str | None:
    gene_upper = gene.upper().strip()
    mut_upper = mutant_aa.upper().strip()
    for preset_name, metadata in PRESETS.items():
        if (
            metadata["gene"] == gene_upper
            and metadata["position_0_indexed"] == position_0_indexed
            and metadata["mutant_aa"] == mut_upper
        ):
            return preset_name
    return None


def load_preset_inputs(preset_name: str) -> tuple[str, int, str]:
    metadata = preset_metadata(preset_name)
    return metadata["gene"], metadata["position_0_indexed"] + 1, metadata["mutant_aa"]


def resolve_preset_name(gene: str, position_0_indexed: int, mutant_aa: str, preset_name: str | None) -> str | None:
    if preset_name is not None:
        metadata = PRESETS.get(preset_name)
        if metadata and _preset_matches_variant(metadata, gene, position_0_indexed, mutant_aa):
            return preset_name
    return infer_preset_name(gene, position_0_indexed, mutant_aa)


def analyze_variant(gene: str, position_0_indexed: int, mutant_aa: str) -> dict[str, Any]:
    from spectralbio.pipeline.compute_covariance_features import covariance_features
    from spectralbio.pipeline.compute_hidden_states import extract_local_hidden_states
    from spectralbio.pipeline.compute_ll_proper import compute_ll_proper

    gene_upper = gene.upper().strip()
    mut_upper = mutant_aa.upper().strip()
    if gene_upper not in {"TP53", "BRCA1"}:
        raise ValueError("Gene must be TP53 or BRCA1.")
    if mut_upper not in AA_SET:
        raise ValueError("Mutant amino acid must be one of the 20 canonical residues.")

    sequence, _, _, _, aa_token_ids = _wildtype_bundle(gene_upper)
    if position_0_indexed < 0 or position_0_indexed >= len(sequence):
        raise ValueError(f"Position must be between 1 and {len(sequence)} for {gene_upper}.")

    wt_aa = sequence[position_0_indexed]
    if wt_aa == mut_upper:
        raise ValueError("Mutant amino acid must differ from the wild-type residue.")

    mutated_sequence = f"{sequence[:position_0_indexed]}{mut_upper}{sequence[position_0_indexed + 1:]}"
    hidden_wt, logits_wt, local_pos = extract_local_hidden_states(sequence, position_0_indexed)
    hidden_mut, _, _ = extract_local_hidden_states(mutated_sequence, position_0_indexed)
    features = covariance_features(hidden_wt, hidden_mut)
    ll_value = compute_ll_proper(logits_wt, local_pos, wt_aa, mut_upper, aa_token_ids)
    raw_combined = combined_score(features["frob_dist"], ll_value, alpha=ALPHA)
    percentile = combined_percentile(raw_combined)
    label, label_key = classification_from_percent(percentile)

    return {
        "gene": gene_upper,
        "position_1_indexed": position_0_indexed + 1,
        "position_0_indexed": position_0_indexed,
        "wt_aa": wt_aa,
        "mut_aa": mut_upper,
        "protein_variant": _protein_variant(position_0_indexed, wt_aa, mut_upper),
        "frob_dist": round(features["frob_dist"], 6),
        "trace_ratio": round(features["trace_ratio"], 6),
        "sps_log": round(features["sps_log"], 6),
        "ll_proper": round(ll_value, 6),
        "combined_raw": round(raw_combined, 6),
        "combined_percentile": percentile,
        "label": label,
        "label_key": label_key,
        "seed": SEED,
    }


def score_variant_contract(
    gene: str,
    position_0_indexed: int,
    mutant_aa: str,
    *,
    preset_name: str | None = None,
) -> dict[str, Any]:
    result = analyze_variant(gene, position_0_indexed, mutant_aa)
    resolved_preset_name = resolve_preset_name(gene, position_0_indexed, mutant_aa, preset_name)
    resolved_preset = PRESETS.get(resolved_preset_name, {})
    benchmark_role = benchmark_role_for_gene(result["gene"])
    request = {
        "gene": result["gene"],
        "position_0_indexed": result["position_0_indexed"],
        "position_1_indexed": result["position_1_indexed"],
        "mutant_aa": result["mut_aa"],
        "preset_name": resolved_preset_name,
    }
    contract_result = {
        "protein_variant": result["protein_variant"],
        "wild_type_residue": result["wt_aa"],
        "mutant_residue": result["mut_aa"],
        "frob_dist": result["frob_dist"],
        "trace_ratio": result["trace_ratio"],
        "sps_log": result["sps_log"],
        "ll_proper": result["ll_proper"],
        "combined_raw": result["combined_raw"],
        "reference_calibration": {
            "reference_benchmark": "TP53",
            "reference_metric": "0.55*frob_dist + 0.45*ll_proper",
            "combined_percentile": result["combined_percentile"],
        },
        "classification": {
            "label": result["label"],
            "label_key": result["label_key"],
        },
        "seed": result["seed"],
    }
    benchmark_context = {
        "benchmark_role": benchmark_role,
        "benchmark_role_label": PRIMARY_CLAIM if benchmark_role == PRIMARY_BENCHMARK_ROLE else SECONDARY_CLAIM,
        "benchmark_annotation": _benchmark_annotation(result["gene"], result["position_1_indexed"], result["mut_aa"]),
        "scope_note": _scope_note(result["gene"]),
        "artifact_note": ARTIFACT_NOTE,
        "secondary_transfer_note": SECONDARY_TRANSFER_NOTE,
        "adaptation_note": ADAPTATION_CLAIM,
        "primary_claim": PRIMARY_CLAIM,
        "secondary_claim": SECONDARY_CLAIM,
        "preset": {
            "name": resolved_preset_name,
            "is_default_tp53_preset": resolved_preset_name == DEFAULT_PRESET_NAME,
            "ui_story": resolved_preset.get("ui_story"),
        },
    }
    return {
        "contract_version": CONTRACT_VERSION,
        "request": request,
        "result": contract_result,
        "benchmark_context": benchmark_context,
        "official_metrics": official_metrics(),
    }
