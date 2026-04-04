"""Final acceptance-oriented supplementary validation helpers."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold

from spectralbio.constants import ALPHA, MODEL_NAME, PROJECT_ROOT, WINDOW_RADIUS
from spectralbio.data.load_benchmarks import load_brca1_full_filtered, load_tp53_scores, load_tp53_variants
from spectralbio.data.sequences import load_brca1_sequence, load_tp53_sequence
from spectralbio.pipeline.compute_ll_proper import compute_ll_proper
from spectralbio.pipeline.evaluate import _roc_auc_score
from spectralbio.supplementary.reject_recovery import (
    BackboneEvaluationConfig,
    MultiGeneConfig,
    NestedCVConfig,
    REVIEW_STATUS_RANK,
    RejectRecoveryPaths,
    _alpha_sweep_on_rows,
    _apply_minmax,
    _build_gene_rows_from_clinvar,
    covariance_features_dual,
    _download_clinvar_variant_summary,
    _ensure_gene_score_rows,
    _fetch_uniprot_sequence,
    _fit_minmax,
    _forward_local_sequence,
    _inner_tuned_alpha,
    _labels,
    _load_esm_bundle,
    _load_clinvar_subset,
    _local_window,
    _model_slug,
    _mutate_local_sequence,
    _pair_scores,
    _read_csv_rows,
    _release_esm_bundle,
    _render_nested_cv_figures,
    _safe_stratified_splits,
    _score_rows_summary,
    _subset_rows,
    _typed_score_row,
    _write_csv_rows,
    _write_json,
    bootstrap_auc_ci,
    create_reject_recovery_paths,
    paired_bootstrap_delta,
    run_multigene_panel,
    run_tp53_backbone_comparison,
    run_tp53_nested_cv_audit,
)
from spectralbio.utils.io import ensure_dir, read_json, write_text, write_tsv

BINARY_PATHOGENIC = {
    "Pathogenic",
    "Likely pathogenic",
    "Pathogenic/Likely pathogenic",
    "Likely pathogenic/Pathogenic",
}
BINARY_BENIGN = {
    "Benign",
    "Likely benign",
    "Benign/Likely benign",
    "Likely benign/Benign",
}


@dataclass(frozen=True)
class AcceptHardeningConfig:
    anchor_genes: tuple[str, ...] = ("TP53", "BRCA1")
    reference_model_name: str = MODEL_NAME
    stronger_model_names: tuple[str, ...] = (
        "facebook/esm2_t33_650M_UR50D",
        "facebook/esm2_t36_3B_UR50D",
    )
    window_radius: int = WINDOW_RADIUS
    pair_alpha: float = ALPHA
    alpha_step: float = 0.05
    random_seed: int = 42
    checkpoint_every: int = 10
    bootstrap_replicates: int = 1000
    min_total: int = 60
    min_per_class: int = 20
    max_additional_genes: int = 8
    shortlist_non_anchor_genes: int = 3
    large_model_gene_limit: int = 4
    render_figures: bool = True
    overwrite: bool = False
    reuse_frozen_tp53_reference: bool = True
    nested_cv_n_splits: int = 5
    nested_cv_n_repeats: int = 5

    def all_model_names(self) -> tuple[str, ...]:
        return (self.reference_model_name, *self.stronger_model_names)


def create_accept_hardening_paths(
    repo_root: Path | None = None,
    output_root: Path | None = None,
) -> RejectRecoveryPaths:
    repo_root = (repo_root or PROJECT_ROOT).resolve()
    output_root = output_root or repo_root / "supplementary" / "final_accept_hardening"
    return create_reject_recovery_paths(repo_root=repo_root, output_root=output_root)


def _support_scan_dir(paths: RejectRecoveryPaths) -> Path:
    directory = paths.root / "support_scan"
    ensure_dir(directory)
    return directory


def _checkpoint_sweep_dir(paths: RejectRecoveryPaths) -> Path:
    directory = paths.root / "checkpoint_sweep"
    ensure_dir(directory)
    return directory


def _nested_gene_dir(paths: RejectRecoveryPaths, gene: str) -> Path:
    directory = paths.root / "gene_nested_cv" / gene.lower()
    ensure_dir(directory)
    return directory


def _esm1v_augmentation_dir(paths: RejectRecoveryPaths) -> Path:
    directory = paths.root / "esm1v_augmentation"
    ensure_dir(directory)
    return directory


def _brca2_canonical_dir(paths: RejectRecoveryPaths) -> Path:
    directory = paths.root / "brca2_canonical"
    ensure_dir(directory)
    return directory


def _protocol_sweep_dir(paths: RejectRecoveryPaths) -> Path:
    directory = paths.root / "protocol_sweep"
    ensure_dir(directory)
    return directory


def _panel25_dir(paths: RejectRecoveryPaths) -> Path:
    directory = paths.root / "panel25"
    ensure_dir(directory)
    return directory


def _brca1_failure_dir(paths: RejectRecoveryPaths) -> Path:
    directory = paths.root / "brca1_failure"
    ensure_dir(directory)
    return directory


def _variant_key(row: dict[str, Any]) -> tuple[int, str]:
    return int(row["position"]), str(row["mut_aa"]).upper()


def _normalize_values(values: list[float]) -> list[float]:
    minimum, maximum = _fit_minmax([float(value) for value in values])
    return _apply_minmax([float(value) for value in values], minimum, maximum)


def _alpha_sweep_from_vectors(
    labels: list[int],
    covariance_scores: list[float],
    baseline_scores: list[float],
    step: float,
) -> tuple[list[dict[str, float]], dict[str, float]]:
    rows: list[dict[str, float]] = []
    best_row: dict[str, float] | None = None
    covariance = np.asarray(covariance_scores, dtype=float)
    baseline = np.asarray(baseline_scores, dtype=float)
    for alpha in np.arange(0.0, 1.0 + 1e-9, step):
        alpha_value = round(float(alpha), 2)
        beta_value = round(float(1.0 - alpha_value), 2)
        combined = (alpha_value * covariance) + (beta_value * baseline)
        auc = float(_roc_auc_score(labels, combined.tolist()))
        row = {"alpha": alpha_value, "beta": beta_value, "auc": auc}
        rows.append(row)
        if best_row is None or auc > float(best_row["auc"]):
            best_row = row
    if best_row is None:
        raise RuntimeError("alpha sweep produced no valid rows")
    return rows, best_row


def _load_gene_context(
    paths: RejectRecoveryPaths,
    gene: str,
    panel_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    gene_upper = str(gene).upper()
    if gene_upper == "TP53":
        return {
            "gene": "TP53",
            "variants": list(load_tp53_variants()),
            "sequence": load_tp53_sequence(),
            "sequence_path": paths.repo_root / "benchmarks" / "sequences" / "tp53.fasta",
        }
    if gene_upper == "BRCA1":
        return {
            "gene": "BRCA1",
            "variants": list(load_brca1_full_filtered()),
            "sequence": load_brca1_sequence(),
            "sequence_path": paths.repo_root / "benchmarks" / "sequences" / "brca1.fasta",
        }
    manifest = panel_manifest or build_support_ranked_panel_manifest(paths)
    gene_info = manifest.get("genes", {}).get(gene_upper)
    if gene_info is None:
        sequence, fasta_path = _fetch_uniprot_sequence(gene_upper, paths.cache / "uniprot")
        clinvar_path = _download_clinvar_variant_summary(paths.cache)
        clinvar_rows = _load_clinvar_subset(clinvar_path, (gene_upper,))
        gene_rows, stats = _build_gene_rows_from_clinvar(gene_upper, sequence, clinvar_rows)
        if not gene_rows:
            raise KeyError(
                f"Gene {gene_upper} is not present in the support-ranked panel and no ad hoc ClinVar context was built."
            )
        variants_path = paths.multigene / f"{gene_upper.lower()}_adhoc_variants.json"
        _write_json(variants_path, gene_rows)
        return {
            "gene": gene_upper,
            "variants": gene_rows,
            "sequence": sequence,
            "sequence_path": fasta_path,
            "n_total": int(stats.get("n_total", len(gene_rows))),
            "n_positive": int(stats.get("n_positive", sum(int(row["label"]) for row in gene_rows))),
            "n_negative": int(stats.get("n_negative", len(gene_rows) - sum(int(row["label"]) for row in gene_rows))),
        }
    sequence_path = Path(gene_info["sequence_path"])
    lines = [line.strip() for line in sequence_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    sequence = "".join(line for line in lines if not line.startswith(">"))
    return {
        "gene": gene_upper,
        "variants": read_json(Path(gene_info["variants_path"])),
        "sequence": sequence,
        "sequence_path": sequence_path,
    }


def _ensure_reference_gene_rows(
    paths: RejectRecoveryPaths,
    config: AcceptHardeningConfig,
    gene: str,
    panel_manifest: dict[str, Any] | None = None,
    output_dir: Path | None = None,
) -> list[dict[str, Any]]:
    gene_upper = str(gene).upper()
    if gene_upper == "TP53" and config.reuse_frozen_tp53_reference and config.reference_model_name == MODEL_NAME:
        return [
            _typed_score_row({**row, "gene": "TP53", "model_name": config.reference_model_name})
            for row in load_tp53_scores()
        ]

    output_dir = output_dir or (paths.multigene / gene_upper.lower())
    ensure_dir(output_dir)
    context = _load_gene_context(paths, gene_upper, panel_manifest)
    return _ensure_gene_score_rows(
        gene=gene_upper,
        sequence=str(context["sequence"]),
        variants=list(context["variants"]),
        model_name=config.reference_model_name,
        output_dir=output_dir,
        window_radius=config.window_radius,
        checkpoint_every=config.checkpoint_every,
        overwrite=config.overwrite,
    )


def _forward_full_sequence(sequence: str, bundle: Any) -> Any:
    import torch

    tokenizer, model, device, _ = bundle
    inputs = tokenizer(sequence, return_tensors="pt", add_special_tokens=True, padding=False)
    inputs = {key: value.to(device) for key, value in inputs.items()}
    with torch.inference_mode():
        outputs = model(**inputs)
    return torch.log_softmax(outputs.logits[0, 1:-1, :], dim=-1).detach().cpu().float()


def _layer_protocol_indices(layer_protocol: str, n_layers: int) -> list[int]:
    builders = {
        "all_layers": lambda size: list(range(size)),
        "top_half": lambda size: list(range(max(0, size // 2), size)),
        "last20": lambda size: list(range(max(0, size - 20), size)),
        "deep10": lambda size: list(range(max(0, size - 10), size)),
        "last8": lambda size: list(range(max(0, size - 8), size)),
        "deep5": lambda size: list(range(max(0, size - 5), size)),
        "last4": lambda size: list(range(max(0, size - 4), size)),
        "last1": lambda size: [max(0, size - 1)],
    }
    if layer_protocol not in builders:
        raise ValueError(f"Unsupported layer protocol: {layer_protocol}")
    indices = builders[layer_protocol](int(n_layers))
    if not indices:
        raise ValueError(f"Layer protocol {layer_protocol} produced an empty selection for {n_layers} layers.")
    return indices


def _typed_protocol_row(row: dict[str, Any], layer_protocols: tuple[str, ...]) -> dict[str, Any]:
    typed = {
        "gene": str(row["gene"]).upper(),
        "name": str(row["name"]),
        "position": int(row["position"]),
        "wt_aa": str(row["wt_aa"]).upper(),
        "mut_aa": str(row["mut_aa"]).upper(),
        "label": int(row["label"]),
        "window_radius": int(row["window_radius"]),
        "model_name": str(row["model_name"]),
        "ll_proper": float(row["ll_proper"]),
    }
    for protocol in layer_protocols:
        typed[f"frob_dist__{protocol}"] = float(row[f"frob_dist__{protocol}"])
        typed[f"trace_ratio__{protocol}"] = float(row[f"trace_ratio__{protocol}"])
        typed[f"sps_log__{protocol}"] = float(row[f"sps_log__{protocol}"])
    return typed


def _ensure_protocol_gene_rows(
    gene: str,
    sequence: str,
    variants: list[dict[str, Any]],
    model_name: str,
    output_dir: Path,
    window_radius: int,
    layer_protocols: tuple[str, ...],
    checkpoint_every: int,
    overwrite: bool,
) -> list[dict[str, Any]]:
    score_path = output_dir / f"{gene.lower()}_{_model_slug(model_name)}_r{int(window_radius)}_protocol_scores.csv"
    metadata_path = output_dir / f"{gene.lower()}_{_model_slug(model_name)}_r{int(window_radius)}_protocol_metadata.json"
    if score_path.exists() and not overwrite:
        existing = _read_csv_rows(score_path)
        if existing and len(existing) >= len(variants):
            return [_typed_protocol_row(row, layer_protocols) for row in existing]

    ensure_dir(output_dir)
    done_rows = {str(row["name"]): _typed_protocol_row(row, layer_protocols) for row in _read_csv_rows(score_path)}
    bundle = _load_esm_bundle(model_name)
    _, _, _, aa_token_ids = bundle
    wt_cache: dict[int, tuple[np.ndarray, Any, int, str]] = {}
    started_at = pd.Timestamp.utcnow()
    try:
        for index, variant in enumerate(variants, start=1):
            name = str(variant["name"])
            if name in done_rows and not overwrite:
                continue
            position = int(variant["position"])
            wt_aa = str(variant["wt_aa"]).upper()
            mut_aa = str(variant["mut_aa"]).upper()
            if sequence[position].upper() != wt_aa:
                raise ValueError(
                    f"WT residue mismatch for {name}: expected {wt_aa}, found {sequence[position]}"
                )
            if position not in wt_cache:
                wt_local, local_pos = _local_window(sequence, position, window_radius)
                wt_hidden, wt_logits = _forward_local_sequence(wt_local, bundle)
                wt_cache[position] = (wt_hidden, wt_logits, local_pos, wt_local)

            wt_hidden, wt_logits, local_pos, wt_local = wt_cache[position]
            mut_local = _mutate_local_sequence(wt_local, local_pos, wt_aa, mut_aa)
            mut_hidden, _ = _forward_local_sequence(mut_local, bundle)
            ll_proper = compute_ll_proper(wt_logits, local_pos, wt_aa, mut_aa, aa_token_ids)
            row: dict[str, Any] = {
                "gene": str(variant["gene"]).upper(),
                "name": name,
                "position": position,
                "wt_aa": wt_aa,
                "mut_aa": mut_aa,
                "label": int(variant["label"]),
                "window_radius": int(window_radius),
                "model_name": model_name,
                "ll_proper": float(ll_proper),
            }
            for protocol in layer_protocols:
                indices = _layer_protocol_indices(protocol, int(wt_hidden.shape[0]))
                metrics = covariance_features_dual(wt_hidden[indices], mut_hidden[indices])
                row[f"frob_dist__{protocol}"] = float(metrics["frob_dist"])
                row[f"trace_ratio__{protocol}"] = float(metrics["trace_ratio"])
                row[f"sps_log__{protocol}"] = float(metrics["sps_log"])
            done_rows[name] = row
            if checkpoint_every > 0 and index % int(checkpoint_every) == 0:
                rows_to_write = sorted(
                    done_rows.values(),
                    key=lambda item: (int(item["position"]), str(item["mut_aa"]).upper(), str(item["name"])),
                )
                _write_csv_rows(score_path, rows_to_write)
    finally:
        _release_esm_bundle(bundle)

    rows = sorted(
        done_rows.values(),
        key=lambda item: (int(item["position"]), str(item["mut_aa"]).upper(), str(item["name"])),
    )
    _write_csv_rows(score_path, rows)
    _write_json(
        metadata_path,
        {
            "gene": gene,
            "model_name": model_name,
            "window_radius": int(window_radius),
            "layer_protocols": list(layer_protocols),
            "n_total": int(len(rows)),
            "started_at_utc": str(started_at),
        },
    )
    return [_typed_protocol_row(row, layer_protocols) for row in rows]


def _load_esm1v_norm_lookup(
    paths: RejectRecoveryPaths,
    config: AcceptHardeningConfig,
    gene: str,
    sequence: str,
    variants: list[dict[str, Any]],
    model_ids: tuple[str, ...] = tuple(f"facebook/esm1v_t33_650M_UR90S_{index}" for index in range(1, 6)),
) -> dict[tuple[int, str], float]:
    table_path = _esm1v_augmentation_dir(paths) / gene.lower() / "augmentation_table.csv"
    if table_path.exists():
        table = pd.read_csv(table_path)
    else:
        table = _build_esm1v_ensemble_table(paths, config, gene, sequence, variants, model_ids)
    if "esm1v_ll_mean_norm" not in table.columns:
        table["esm1v_ll_mean_norm"] = _normalize_values(table["esm1v_ll_mean"].astype(float).tolist())
    return {
        (int(row["position"]), str(row["mut_aa"]).upper()): float(row["esm1v_ll_mean_norm"])
        for _, row in table.iterrows()
    }


def _public_model_tag(model_name: str) -> str:
    if "150M" in model_name:
        return "150m"
    if "650M" in model_name:
        return "650m"
    if "3B" in model_name:
        return "3b_shadow"
    return _model_slug(model_name)


def _brca1_domain_label(position: int) -> str:
    residue = int(position) + 1
    if 24 <= residue <= 65:
        return "RING"
    if 1392 <= residue <= 1424:
        return "coiled_coil"
    if 1646 <= residue <= 1736:
        return "BRCT1"
    if 1760 <= residue <= 1855:
        return "BRCT2"
    return "other"


def _substitution_class_label(wt_aa: str, mut_aa: str) -> str:
    groups = {
        "hydrophobic": set("AILMV"),
        "aromatic": set("FYW"),
        "polar": set("STNQ"),
        "positive": set("KRH"),
        "negative": set("DE"),
        "special": set("CGP"),
    }
    wt_group = next((name for name, aas in groups.items() if wt_aa in aas), "other")
    mut_group = next((name for name, aas in groups.items() if mut_aa in aas), "other")
    if wt_group == mut_group:
        return "conservative"
    if "special" in {wt_group, mut_group}:
        return "radical"
    if {wt_group, mut_group} == {"positive", "negative"}:
        return "radical"
    if {wt_group, mut_group} <= {"hydrophobic", "aromatic"}:
        return "moderate"
    return "radical"


def _confidence_label(review_rank: int) -> str:
    if int(review_rank) >= 3:
        return "high"
    if int(review_rank) == 2:
        return "medium"
    if int(review_rank) == 1:
        return "low"
    return "unreviewed"


def _load_clinvar_review_lookup(paths: RejectRecoveryPaths, gene: str) -> dict[tuple[int, str], dict[str, Any]]:
    import re

    gene_upper = str(gene).upper()
    clinvar_path = _download_clinvar_variant_summary(paths.cache)
    subset_rows = _load_clinvar_subset(clinvar_path, (gene_upper,))
    lookup: dict[tuple[int, str], dict[str, Any]] = {}
    pattern = re.compile(r"\(p\.([A-Z][a-z]{2})(\d+)([A-Z][a-z]{2})\)")
    aa_map = {
        "Ala": "A",
        "Arg": "R",
        "Asn": "N",
        "Asp": "D",
        "Cys": "C",
        "Gln": "Q",
        "Glu": "E",
        "Gly": "G",
        "His": "H",
        "Ile": "I",
        "Leu": "L",
        "Lys": "K",
        "Met": "M",
        "Phe": "F",
        "Pro": "P",
        "Ser": "S",
        "Thr": "T",
        "Trp": "W",
        "Tyr": "Y",
        "Val": "V",
    }
    for row in subset_rows:
        if str(row.get("Assembly", "")) != "GRCh38":
            continue
        if str(row.get("Type", "")) != "single nucleotide variant":
            continue
        origin_simple = str(row.get("OriginSimple", "")).strip()
        if origin_simple and origin_simple != "germline":
            continue
        match = pattern.search(str(row.get("Name", "")))
        if not match:
            continue
        wt_three, position_1_based, mut_three = match.groups()
        if wt_three not in aa_map or mut_three not in aa_map:
            continue
        key = (int(position_1_based) - 1, aa_map[mut_three])
        review_status = str(row.get("ReviewStatus", "")).strip()
        review_rank = int(REVIEW_STATUS_RANK.get(review_status.lower(), 0))
        existing = lookup.get(key)
        if existing is None or review_rank > int(existing["review_rank"]):
            lookup[key] = {
                "review_status": review_status,
                "review_rank": review_rank,
                "confidence": _confidence_label(review_rank),
            }
    return lookup


def scan_clinvar_gene_support(
    paths: RejectRecoveryPaths,
    config: AcceptHardeningConfig | None = None,
) -> dict[str, Any]:
    config = config or AcceptHardeningConfig()
    output_dir = _support_scan_dir(paths)
    summary_path = output_dir / "clinvar_gene_support_summary.json"
    table_path = output_dir / "clinvar_gene_support_table.csv"
    if summary_path.exists() and table_path.exists() and not config.overwrite:
        return read_json(summary_path)

    clinvar_path = _download_clinvar_variant_summary(paths.cache)
    counts: dict[str, Counter] = {}
    review_values: dict[str, list[str]] = {}
    regex = r"\(p\.([A-Z][a-z]{2})(\d+)([A-Z][a-z]{2})\)"

    for chunk in pd.read_csv(
        clinvar_path,
        sep="\t",
        compression="gzip",
        usecols=[
            "GeneSymbol",
            "Type",
            "Name",
            "ClinicalSignificance",
            "OriginSimple",
            "Assembly",
            "ReviewStatus",
        ],
        dtype=str,
        keep_default_na=False,
        chunksize=250000,
    ):
        filtered = chunk[
            (chunk["Assembly"] == "GRCh38")
            & (chunk["Type"] == "single nucleotide variant")
            & ((chunk["OriginSimple"] == "") | (chunk["OriginSimple"] == "germline"))
        ].copy()
        if filtered.empty:
            continue
        filtered["label"] = np.where(
            filtered["ClinicalSignificance"].isin(BINARY_PATHOGENIC),
            1,
            np.where(filtered["ClinicalSignificance"].isin(BINARY_BENIGN), 0, np.nan),
        )
        filtered = filtered[filtered["label"].notna()].copy()
        if filtered.empty:
            continue
        extracted = filtered["Name"].str.extract(regex)
        filtered = filtered[extracted.notna().all(axis=1)].copy()
        if filtered.empty:
            continue
        filtered["GeneSymbol"] = filtered["GeneSymbol"].str.upper()
        grouped = filtered.groupby("GeneSymbol")
        for gene, frame in grouped:
            counter = counts.setdefault(gene, Counter())
            positive = int(frame["label"].sum())
            total = int(len(frame))
            negative = int(total - positive)
            counter["n_total"] += total
            counter["n_positive"] += positive
            counter["n_negative"] += negative
            counter["n_rows"] += total
            review_values.setdefault(gene, []).extend([str(item) for item in frame["ReviewStatus"].tolist()])

    table_rows: list[dict[str, Any]] = []
    for gene, counter in counts.items():
        n_total = int(counter["n_total"])
        n_positive = int(counter["n_positive"])
        n_negative = int(counter["n_negative"])
        min_class_count = int(min(n_positive, n_negative))
        table_rows.append(
            {
                "gene": gene,
                "n_total": n_total,
                "n_positive": n_positive,
                "n_negative": n_negative,
                "min_class_count": min_class_count,
                "passes_thresholds": bool(
                    n_total >= config.min_total
                    and n_positive >= config.min_per_class
                    and n_negative >= config.min_per_class
                ),
                "review_status_examples": " | ".join(sorted(set(review_values.get(gene, [])))[:3]),
            }
        )
    table_rows.sort(key=lambda row: (-int(row["min_class_count"]), -int(row["n_total"]), str(row["gene"])))
    _write_csv_rows(table_path, table_rows)

    eligible = [row for row in table_rows if bool(row["passes_thresholds"])]
    summary = {
        "benchmark": "Global ClinVar support scan for support-ranked supplementary panel selection",
        "n_genes_seen": len(table_rows),
        "n_genes_passing_thresholds": len(eligible),
        "selection_rule": {
            "min_total": config.min_total,
            "min_per_class": config.min_per_class,
            "ranking": ["min_class_count desc", "n_total desc", "gene asc"],
        },
        "top_genes": eligible[:25],
        "artifacts": {
            "table": table_path,
            "summary": summary_path,
        },
    }
    _write_json(summary_path, summary)
    return summary


def build_support_ranked_panel_manifest(
    paths: RejectRecoveryPaths,
    config: AcceptHardeningConfig | None = None,
    support_scan: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = config or AcceptHardeningConfig()
    manifest_path = paths.root / "support_ranked_panel_manifest.json"
    if manifest_path.exists() and not config.overwrite:
        return read_json(manifest_path)

    support_scan = support_scan or scan_clinvar_gene_support(paths, config)
    support_table_path = Path(support_scan["artifacts"]["table"])
    support_rows = _read_csv_rows(support_table_path)
    ranked_genes = [
        str(row["gene"]).upper()
        for row in support_rows
        if str(row["gene"]).upper() not in {gene.upper() for gene in config.anchor_genes}
        and str(row.get("passes_thresholds", "")).lower() == "true"
    ]

    manifest: dict[str, Any] = {
        "anchor_genes": list(config.anchor_genes),
        "selected_genes": list(config.anchor_genes),
        "selection_rule": {
            "support_scan_table": str(support_table_path),
            "min_total": config.min_total,
            "min_per_class": config.min_per_class,
            "max_additional_genes": config.max_additional_genes,
            "ranking": ["min_class_count desc", "n_total desc", "gene asc"],
        },
        "genes": {},
        "candidate_stats": {},
    }

    tp53_rows = list(load_tp53_variants())
    brca1_rows = list(load_brca1_full_filtered())
    tp53_rows_path = paths.multigene / "tp53_variants.json"
    brca1_rows_path = paths.multigene / "brca1_full_filtered_variants.json"
    _write_json(tp53_rows_path, tp53_rows)
    _write_json(brca1_rows_path, brca1_rows)
    manifest["genes"]["TP53"] = {
        "variants_path": tp53_rows_path,
        "sequence_source": "local benchmark fasta",
        "sequence_path": paths.repo_root / "benchmarks" / "sequences" / "tp53.fasta",
        "n_total": len(tp53_rows),
        "n_positive": int(sum(int(row["label"]) for row in tp53_rows)),
        "n_negative": int(len(tp53_rows) - sum(int(row["label"]) for row in tp53_rows)),
        "support_rank": 0,
    }
    manifest["genes"]["BRCA1"] = {
        "variants_path": brca1_rows_path,
        "sequence_source": "local benchmark fasta",
        "sequence_path": paths.repo_root / "benchmarks" / "sequences" / "brca1.fasta",
        "n_total": len(brca1_rows),
        "n_positive": int(sum(int(row["label"]) for row in brca1_rows)),
        "n_negative": int(len(brca1_rows) - sum(int(row["label"]) for row in brca1_rows)),
        "support_rank": 0,
    }

    probe_genes = tuple(ranked_genes[: max(config.max_additional_genes * 4, config.max_additional_genes)])
    clinvar_rows: list[dict[str, str]] = []
    if probe_genes:
        clinvar_path = _download_clinvar_variant_summary(paths.cache)
        clinvar_rows = _load_clinvar_subset(clinvar_path, probe_genes)
    rows_by_gene: dict[str, list[dict[str, str]]] = {gene: [] for gene in probe_genes}
    for row in clinvar_rows:
        gene = str(row["GeneSymbol"]).upper()
        if gene in rows_by_gene:
            rows_by_gene[gene].append(row)

    selected_extra = 0
    for rank_index, gene in enumerate(ranked_genes, start=1):
        if selected_extra >= config.max_additional_genes:
            break
        sequence, fasta_path = _fetch_uniprot_sequence(gene, paths.cache / "uniprot")
        gene_rows, stats = _build_gene_rows_from_clinvar(gene, sequence, rows_by_gene.get(gene, []))
        stats["fasta_path"] = str(fasta_path)
        stats["support_rank"] = rank_index
        if (
            int(stats.get("n_total", 0)) < config.min_total
            or int(stats.get("n_positive", 0)) < config.min_per_class
            or int(stats.get("n_negative", 0)) < config.min_per_class
        ):
            stats["selected"] = False
            manifest["candidate_stats"][gene] = stats
            continue
        gene_path = paths.multigene / f"{gene.lower()}_clinvar_variants.json"
        _write_json(gene_path, gene_rows)
        manifest["genes"][gene] = {
            "variants_path": gene_path,
            "sequence_source": "UniProt reviewed human entry",
            "sequence_path": str(fasta_path),
            "n_total": int(stats["n_total"]),
            "n_positive": int(stats["n_positive"]),
            "n_negative": int(stats["n_negative"]),
            "support_rank": rank_index,
        }
        manifest["candidate_stats"][gene] = {**stats, "selected": True}
        manifest["selected_genes"].append(gene)
        selected_extra += 1

    _write_json(manifest_path, manifest)
    _write_csv_rows(
        paths.multigene / "support_ranked_gene_table.csv",
        [
            {
                "gene": gene,
                "selected": bool(stats.get("selected", False)),
                "support_rank": int(stats.get("support_rank", 0)),
                "n_total": int(stats.get("n_total", 0)),
                "n_positive": int(stats.get("n_positive", 0)),
                "n_negative": int(stats.get("n_negative", 0)),
                "skip_sequence_mismatch": int(stats.get("skip_sequence_mismatch", 0)),
                "skip_non_binary_label": int(stats.get("skip_non_binary_label", 0)),
            }
            for gene, stats in manifest["candidate_stats"].items()
        ],
    )
    return manifest


def run_support_ranked_panel(
    paths: RejectRecoveryPaths,
    config: AcceptHardeningConfig | None = None,
    panel_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = config or AcceptHardeningConfig()
    panel_manifest = panel_manifest or build_support_ranked_panel_manifest(paths, config)
    multigene_config = MultiGeneConfig(
        candidate_genes=tuple(),
        model_name=config.reference_model_name,
        window_radius=config.window_radius,
        pair_alpha=config.pair_alpha,
        random_seed=config.random_seed,
        checkpoint_every=config.checkpoint_every,
        bootstrap_replicates=config.bootstrap_replicates,
        min_total=config.min_total,
        min_per_class=config.min_per_class,
        max_additional_genes=config.max_additional_genes,
        render_figures=config.render_figures,
        overwrite=config.overwrite,
        reuse_frozen_tp53_reference=config.reuse_frozen_tp53_reference,
    )
    return run_multigene_panel(paths, multigene_config, panel_manifest=panel_manifest)


def run_gene_nested_cv_audit(
    paths: RejectRecoveryPaths,
    gene: str,
    score_rows: list[dict[str, Any]],
    config: NestedCVConfig | None = None,
) -> dict[str, Any]:
    config = config or NestedCVConfig()
    rows = [_typed_score_row(row) for row in score_rows]
    labels = _labels(rows)
    outer_splits = _safe_stratified_splits(labels, config.n_splits)
    seeds = [config.random_seed + offset for offset in range(config.n_repeats)]
    fold_rows: list[dict[str, Any]] = []
    alpha_distribution: list[dict[str, Any]] = []
    inner_sweeps: dict[str, list[dict[str, float]]] = {}
    output_dir = _nested_gene_dir(paths, gene)

    for repeat_index, seed in enumerate(seeds):
        splitter = StratifiedKFold(n_splits=outer_splits, shuffle=True, random_state=seed)
        for fold_index, (train_idx, test_idx) in enumerate(
            splitter.split(np.zeros(len(rows)), labels),
            start=1,
        ):
            train_rows = _subset_rows(rows, train_idx)
            test_rows = _subset_rows(rows, test_idx)
            chosen_alpha, inner_summary = _inner_tuned_alpha(train_rows, config, seed + fold_index)
            inner_sweeps[f"repeat_{repeat_index + 1}_fold_{fold_index}"] = inner_summary
            test_labels = _labels(test_rows)
            tuned_auc = float(_roc_auc_score(test_labels, _pair_scores(test_rows, chosen_alpha, fit_rows=train_rows)["pair"]))
            fixed_055_auc = float(_roc_auc_score(test_labels, _pair_scores(test_rows, 0.55, fit_rows=train_rows)["pair"]))
            fixed_050_auc = float(_roc_auc_score(test_labels, _pair_scores(test_rows, 0.50, fit_rows=train_rows)["pair"]))
            ll_auc = float(_roc_auc_score(test_labels, _pair_scores(test_rows, 0.0, fit_rows=train_rows)["ll_norm"]))
            frob_auc = float(_roc_auc_score(test_labels, _pair_scores(test_rows, 1.0, fit_rows=train_rows)["frob_norm"]))
            fold_rows.append(
                {
                    "gene": gene,
                    "repeat": repeat_index + 1,
                    "fold": fold_index,
                    "seed": seed,
                    "n_train": len(train_rows),
                    "n_test": len(test_rows),
                    "n_test_positive": int(sum(test_labels)),
                    "n_test_negative": int(len(test_labels) - sum(test_labels)),
                    "chosen_alpha": float(chosen_alpha),
                    "auc_tuned_alpha": tuned_auc,
                    "auc_fixed_055": fixed_055_auc,
                    "auc_fixed_050": fixed_050_auc,
                    "auc_ll_proper": ll_auc,
                    "auc_frob_dist": frob_auc,
                    "delta_tuned_vs_ll": float(tuned_auc - ll_auc),
                    "delta_fixed055_vs_ll": float(fixed_055_auc - ll_auc),
                }
            )
            alpha_distribution.append({"repeat": repeat_index + 1, "fold": fold_index, "chosen_alpha": float(chosen_alpha)})

    summary = {
        "benchmark": f"{gene} nested CV audit",
        "gene": gene,
        "n_rows": len(rows),
        "n_splits": outer_splits,
        "n_repeats": config.n_repeats,
        "alpha_step": config.alpha_step,
        "released_alpha": 0.55,
        "comparison_means": {
            "auc_tuned_alpha_mean": float(np.mean([row["auc_tuned_alpha"] for row in fold_rows])),
            "auc_tuned_alpha_std": float(np.std([row["auc_tuned_alpha"] for row in fold_rows], ddof=0)),
            "auc_fixed_055_mean": float(np.mean([row["auc_fixed_055"] for row in fold_rows])),
            "auc_fixed_055_std": float(np.std([row["auc_fixed_055"] for row in fold_rows], ddof=0)),
            "auc_fixed_050_mean": float(np.mean([row["auc_fixed_050"] for row in fold_rows])),
            "auc_fixed_050_std": float(np.std([row["auc_fixed_050"] for row in fold_rows], ddof=0)),
            "auc_ll_proper_mean": float(np.mean([row["auc_ll_proper"] for row in fold_rows])),
            "auc_ll_proper_std": float(np.std([row["auc_ll_proper"] for row in fold_rows], ddof=0)),
            "auc_frob_dist_mean": float(np.mean([row["auc_frob_dist"] for row in fold_rows])),
            "auc_frob_dist_std": float(np.std([row["auc_frob_dist"] for row in fold_rows], ddof=0)),
        },
        "chosen_alpha_mean": float(np.mean([row["chosen_alpha"] for row in fold_rows])),
        "chosen_alpha_std": float(np.std([row["chosen_alpha"] for row in fold_rows], ddof=0)),
        "artifacts": {
            "fold_results": output_dir / f"{gene.lower()}_nested_cv_fold_results.csv",
            "alpha_distribution": output_dir / f"{gene.lower()}_nested_cv_alpha_distribution.csv",
            "summary": output_dir / f"{gene.lower()}_nested_cv_summary.json",
            "inner_sweeps": output_dir / f"{gene.lower()}_nested_cv_inner_sweeps.json",
        },
    }
    _write_csv_rows(output_dir / f"{gene.lower()}_nested_cv_fold_results.csv", fold_rows)
    _write_csv_rows(output_dir / f"{gene.lower()}_nested_cv_alpha_distribution.csv", alpha_distribution)
    _write_json(output_dir / f"{gene.lower()}_nested_cv_inner_sweeps.json", inner_sweeps)
    _write_json(output_dir / f"{gene.lower()}_nested_cv_summary.json", summary)
    if config.render_figures:
        _render_nested_cv_figures(output_dir, fold_rows, alpha_distribution)
    return summary


def run_shortlist_gene_nested_cv(
    paths: RejectRecoveryPaths,
    config: AcceptHardeningConfig | None = None,
    panel_manifest: dict[str, Any] | None = None,
    multigene_metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = config or AcceptHardeningConfig()
    panel_manifest = panel_manifest or build_support_ranked_panel_manifest(paths, config)
    multigene_metrics = multigene_metrics or run_support_ranked_panel(paths, config, panel_manifest)

    non_anchor = [
        gene
        for gene in panel_manifest["selected_genes"]
        if gene.upper() not in {anchor.upper() for anchor in config.anchor_genes}
    ]
    non_anchor.sort(
        key=lambda gene: (
            -min(
                int(panel_manifest["genes"][gene]["n_positive"]),
                int(panel_manifest["genes"][gene]["n_negative"]),
            ),
            -int(panel_manifest["genes"][gene]["n_total"]),
            str(gene),
        )
    )
    shortlist = non_anchor[: config.shortlist_non_anchor_genes]

    nested_config = NestedCVConfig(
        n_splits=config.nested_cv_n_splits,
        n_repeats=config.nested_cv_n_repeats,
        alpha_step=config.alpha_step,
        random_seed=config.random_seed,
        render_figures=config.render_figures,
        overwrite=config.overwrite,
    )
    payload = {"benchmark": "Support-first shortlist nested CV", "genes": {}}
    for gene in shortlist:
        score_path = paths.multigene / gene.lower() / f"{gene.lower()}_{config.reference_model_name.replace('/', '_').replace('-', '_')}_scores.csv"
        rows = [_typed_score_row(row) for row in _read_csv_rows(score_path)]
        payload["genes"][gene] = run_gene_nested_cv_audit(paths, gene, rows, nested_config)
    _write_json(paths.root / "gene_nested_cv" / "shortlist_nested_cv_summary.json", payload)
    return payload


def recommend_second_benchmark_candidate(
    paths: RejectRecoveryPaths,
    config: AcceptHardeningConfig | None = None,
    panel_manifest: dict[str, Any] | None = None,
    multigene_metrics: dict[str, Any] | None = None,
    shortlist_nested_cv: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = config or AcceptHardeningConfig()
    panel_manifest = panel_manifest or build_support_ranked_panel_manifest(paths, config)
    multigene_metrics = multigene_metrics or run_support_ranked_panel(paths, config, panel_manifest)
    shortlist_nested_cv = shortlist_nested_cv or run_shortlist_gene_nested_cv(paths, config, panel_manifest, multigene_metrics)

    candidates: list[dict[str, Any]] = []
    for gene, nested_summary in shortlist_nested_cv.get("genes", {}).items():
        gene_metrics = multigene_metrics["genes"][gene]
        lower_delta = float(gene_metrics["pair_vs_ll_bootstrap_delta"]["ci_2p5"])
        support = min(int(gene_metrics["n_positive"]), int(gene_metrics["n_negative"]))
        fixed055 = float(nested_summary["comparison_means"]["auc_fixed_055_mean"])
        ll_mean = float(nested_summary["comparison_means"]["auc_ll_proper_mean"])
        qualifies = bool(lower_delta > 0.0 and fixed055 > ll_mean)
        candidates.append(
            {
                "gene": gene,
                "support_min_class": support,
                "n_total": int(gene_metrics["n_total"]),
                "pair_auc": float(gene_metrics["auc_pair_fixed_055"]),
                "delta_pair_vs_ll": float(gene_metrics["delta_pair_vs_ll"]),
                "paired_delta_ci_2p5": lower_delta,
                "paired_delta_ci_97p5": float(gene_metrics["pair_vs_ll_bootstrap_delta"]["ci_97p5"]),
                "nested_fixed055_mean_auc": fixed055,
                "nested_ll_mean_auc": ll_mean,
                "nested_chosen_alpha_mean": float(nested_summary["chosen_alpha_mean"]),
                "qualifies": qualifies,
            }
        )
    candidates.sort(
        key=lambda row: (
            not bool(row["qualifies"]),
            -int(row["support_min_class"]),
            -float(row["delta_pair_vs_ll"]),
            str(row["gene"]),
        )
    )
    recommendation = {
        "benchmark": "Second canonical benchmark candidate recommendation",
        "rule": {
            "shortlist_basis": "top non-anchor genes by support among the scored support-ranked panel",
            "qualify_if": [
                "paired pair-vs-ll bootstrap lower CI > 0",
                "nested fixed-0.55 mean AUC > nested ll_proper mean AUC",
            ],
            "rank_if_multiple": ["support_min_class desc", "delta_pair_vs_ll desc", "gene asc"],
        },
        "candidates": candidates,
        "recommended_gene": candidates[0]["gene"] if candidates and bool(candidates[0]["qualifies"]) else None,
    }
    _write_json(paths.root / "second_benchmark_candidate.json", recommendation)
    return recommendation


def _deep_validation_genes(
    panel_manifest: dict[str, Any],
    recommendation: dict[str, Any],
    config: AcceptHardeningConfig,
) -> list[str]:
    genes = list(config.anchor_genes)
    recommended = recommendation.get("recommended_gene")
    if recommended and recommended not in genes:
        genes.append(str(recommended))
    non_anchor = [
        gene
        for gene in panel_manifest["selected_genes"]
        if gene.upper() not in {anchor.upper() for anchor in config.anchor_genes}
        and gene != recommended
    ]
    non_anchor.sort(
        key=lambda gene: (
            -min(
                int(panel_manifest["genes"][gene]["n_positive"]),
                int(panel_manifest["genes"][gene]["n_negative"]),
            ),
            -int(panel_manifest["genes"][gene]["n_total"]),
            str(gene),
        )
    )
    for gene in non_anchor:
        if len(genes) >= config.large_model_gene_limit:
            break
        genes.append(gene)
    return genes


def run_deep_checkpoint_sweep(
    paths: RejectRecoveryPaths,
    config: AcceptHardeningConfig | None = None,
    panel_manifest: dict[str, Any] | None = None,
    multigene_metrics: dict[str, Any] | None = None,
    recommendation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = config or AcceptHardeningConfig()
    panel_manifest = panel_manifest or build_support_ranked_panel_manifest(paths, config)
    multigene_metrics = multigene_metrics or run_support_ranked_panel(paths, config, panel_manifest)
    recommendation = recommendation or recommend_second_benchmark_candidate(paths, config, panel_manifest, multigene_metrics)

    output_dir = _checkpoint_sweep_dir(paths)
    genes = _deep_validation_genes(panel_manifest, recommendation, config)
    long_rows: list[dict[str, Any]] = []
    payload: dict[str, Any] = {"benchmark": "Deep checkpoint sweep", "genes": genes, "models": {}}

    for model_index, model_name in enumerate(config.all_model_names()):
        per_gene_payload: dict[str, Any] = {}
        for gene in genes:
            if gene == "TP53":
                variants = list(load_tp53_variants())
                sequence = load_tp53_sequence()
            elif gene == "BRCA1":
                variants = list(load_brca1_full_filtered())
                sequence = load_brca1_sequence()
            else:
                gene_info = panel_manifest["genes"][gene]
                variants = read_json(Path(gene_info["variants_path"]))
                fasta_path = Path(gene_info["sequence_path"])
                lines = [line.strip() for line in fasta_path.read_text(encoding="utf-8").splitlines() if line.strip()]
                sequence = "".join(line for line in lines if not line.startswith(">"))

            if gene == "TP53" and model_name == config.reference_model_name and config.reuse_frozen_tp53_reference:
                score_rows = [_typed_score_row({**row, "gene": "TP53", "model_name": model_name}) for row in load_tp53_scores()]
            elif model_name == config.reference_model_name and gene in multigene_metrics["genes"]:
                score_path = paths.multigene / gene.lower() / f"{gene.lower()}_{model_name.replace('/', '_').replace('-', '_')}_scores.csv"
                score_rows = [_typed_score_row(row) for row in _read_csv_rows(score_path)]
            else:
                gene_dir = output_dir / gene.lower()
                ensure_dir(gene_dir)
                score_rows = _ensure_gene_score_rows(
                    gene=gene,
                    sequence=sequence,
                    variants=variants,
                    model_name=model_name,
                    output_dir=gene_dir,
                    window_radius=config.window_radius,
                    checkpoint_every=config.checkpoint_every,
                    overwrite=config.overwrite,
                )

            summary = _score_rows_summary(score_rows, config.pair_alpha)
            alpha_sweep_rows, best_alpha = _alpha_sweep_on_rows(score_rows, config.alpha_step)
            bootstrap = bootstrap_auc_ci(_labels(score_rows), summary["normalized_scores"]["pair_score"], config.bootstrap_replicates, config.random_seed)
            paired = paired_bootstrap_delta(
                _labels(score_rows),
                summary["normalized_scores"]["pair_score"],
                summary["normalized_scores"]["ll_proper_norm"],
                config.bootstrap_replicates,
                config.random_seed,
            )
            gene_payload = {
                "gene": gene,
                "model_name": model_name,
                "pair_alpha": config.pair_alpha,
                "window_radius": config.window_radius,
                **{key: value for key, value in summary.items() if key != "normalized_scores"},
                "alpha_sweep": alpha_sweep_rows,
                "best_alpha_on_full_surface": best_alpha,
                "pair_auc_bootstrap": bootstrap,
                "pair_vs_ll_bootstrap_delta": paired,
            }
            per_gene_payload[gene] = gene_payload
            long_rows.append(
                {
                    "model_name": model_name,
                    "gene": gene,
                    "model_rank": model_index,
                    "n_total": gene_payload["n_total"],
                    "n_positive": gene_payload["n_positive"],
                    "n_negative": gene_payload["n_negative"],
                    "auc_ll_proper": gene_payload["auc_ll_proper"],
                    "auc_frob_dist": gene_payload["auc_frob_dist"],
                    "auc_trace_ratio": gene_payload["auc_trace_ratio"],
                    "auc_sps_log": gene_payload["auc_sps_log"],
                    "auc_pair_fixed_055": gene_payload["auc_pair_fixed_055"],
                    "delta_pair_vs_ll": gene_payload["delta_pair_vs_ll"],
                    "best_alpha": float(best_alpha.get("alpha", config.pair_alpha)),
                    "best_alpha_auc": float(best_alpha.get("auc", gene_payload["auc_pair_fixed_055"])),
                    "paired_delta_ci_2p5": float(paired["ci_2p5"]),
                    "paired_delta_ci_97p5": float(paired["ci_97p5"]),
                }
            )
            _write_json(output_dir / gene.lower() / f"{model_name.replace('/', '_').replace('-', '_')}_summary.json", gene_payload)
        payload["models"][model_name] = per_gene_payload

    _write_csv_rows(output_dir / "checkpoint_sweep_long.csv", long_rows)
    _write_json(output_dir / "checkpoint_sweep_summary.json", payload)
    pair_pivot = []
    delta_pivot = []
    for gene in genes:
        pair_row = {"gene": gene}
        delta_row = {"gene": gene}
        for model_name in config.all_model_names():
            gene_payload = payload["models"].get(model_name, {}).get(gene)
            if gene_payload is None:
                continue
            pair_row[model_name] = float(gene_payload["auc_pair_fixed_055"])
            delta_row[model_name] = float(gene_payload["delta_pair_vs_ll"])
        pair_pivot.append(pair_row)
        delta_pivot.append(delta_row)
    _write_csv_rows(output_dir / "checkpoint_sweep_pair_auc_pivot.csv", pair_pivot)
    _write_csv_rows(output_dir / "checkpoint_sweep_delta_pivot.csv", delta_pivot)
    return payload


def run_accept_hardening_suite(
    paths: RejectRecoveryPaths,
    config: AcceptHardeningConfig | None = None,
) -> dict[str, Any]:
    config = config or AcceptHardeningConfig()
    support_scan = scan_clinvar_gene_support(paths, config)
    panel_manifest = build_support_ranked_panel_manifest(paths, config, support_scan)

    nested_tp53_summary = run_tp53_nested_cv_audit(
        paths,
        NestedCVConfig(
            n_splits=config.nested_cv_n_splits,
            n_repeats=config.nested_cv_n_repeats,
            alpha_step=config.alpha_step,
            random_seed=config.random_seed,
            render_figures=config.render_figures,
            overwrite=config.overwrite,
        ),
    )
    reference_backbone_summary = run_tp53_backbone_comparison(
        paths,
        BackboneEvaluationConfig(
            reference_model_name=config.reference_model_name,
            stronger_model_name=config.stronger_model_names[0] if config.stronger_model_names else MODEL_NAME,
            window_radius=config.window_radius,
            pair_alpha=config.pair_alpha,
            random_seed=config.random_seed,
            checkpoint_every=config.checkpoint_every,
            render_figures=config.render_figures,
            overwrite=config.overwrite,
            reuse_frozen_tp53_reference=config.reuse_frozen_tp53_reference,
            run_full_surface_alpha_sweep=True,
        ),
    )
    multigene_metrics = run_support_ranked_panel(paths, config, panel_manifest)
    shortlist_nested_cv = run_shortlist_gene_nested_cv(paths, config, panel_manifest, multigene_metrics)
    recommendation = recommend_second_benchmark_candidate(
        paths,
        config,
        panel_manifest,
        multigene_metrics,
        shortlist_nested_cv,
    )
    checkpoint_sweep = run_deep_checkpoint_sweep(paths, config, panel_manifest, multigene_metrics, recommendation)

    final_summary = {
        "benchmark": "Final accept hardening suite",
        "config": asdict(config),
        "support_scan": support_scan,
        "panel_manifest_path": paths.root / "support_ranked_panel_manifest.json",
        "tp53_nested_cv": nested_tp53_summary,
        "tp53_backbone_reference": reference_backbone_summary,
        "support_ranked_multigene": multigene_metrics,
        "shortlist_nested_cv": shortlist_nested_cv,
        "second_benchmark_candidate": recommendation,
        "checkpoint_sweep": checkpoint_sweep,
    }
    _write_json(paths.root / "final_accept_hardening_summary.json", final_summary)
    return final_summary


def _ensure_esm1v_ll_rows(
    paths: RejectRecoveryPaths,
    gene: str,
    sequence: str,
    variants: list[dict[str, Any]],
    model_name: str,
    window_radius: int,
    checkpoint_every: int,
    overwrite: bool,
) -> list[dict[str, Any]]:
    output_dir = _esm1v_augmentation_dir(paths) / "cache" / gene.lower()
    ensure_dir(output_dir)
    score_path = output_dir / f"{gene.lower()}_{_model_slug(model_name)}_ll_scores.csv"
    metadata_path = output_dir / f"{gene.lower()}_{_model_slug(model_name)}_ll_metadata.json"
    if score_path.exists() and not overwrite:
        existing = _read_csv_rows(score_path)
        if existing:
            return existing

    if len(sequence) <= 1022:
        bundle = _load_esm_bundle(model_name)
        try:
            log_probs = _forward_full_sequence(sequence, bundle)
            aa_token_ids = bundle[3]
            rows: list[dict[str, Any]] = []
            for row in variants:
                position = int(row["position"])
                wt_aa = str(row["wt_aa"]).upper()
                mut_aa = str(row["mut_aa"]).upper()
                wt_id = aa_token_ids[wt_aa]
                mut_id = aa_token_ids[mut_aa]
                ll_value = float(log_probs[position, wt_id].item() - log_probs[position, mut_id].item())
                rows.append(
                    {
                        "gene": gene,
                        "name": str(row["name"]),
                        "position": int(position),
                        "wt_aa": wt_aa,
                        "mut_aa": mut_aa,
                        "label": int(row["label"]),
                        "ll_proper": ll_value,
                        "model_name": model_name,
                        "scoring_mode": "full_sequence",
                    }
                )
        finally:
            _release_esm_bundle(bundle)
    else:
        rows = []
        score_rows = _ensure_gene_score_rows(
            gene=gene,
            sequence=sequence,
            variants=variants,
            model_name=model_name,
            output_dir=output_dir,
            window_radius=window_radius,
            checkpoint_every=checkpoint_every,
            overwrite=overwrite,
        )
        for row in score_rows:
            rows.append(
                {
                    "gene": gene,
                    "name": str(row["name"]),
                    "position": int(row["position"]),
                    "wt_aa": str(row["wt_aa"]).upper(),
                    "mut_aa": str(row["mut_aa"]).upper(),
                    "label": int(row["label"]),
                    "ll_proper": float(row["ll_proper"]),
                    "model_name": model_name,
                    "scoring_mode": "local_window",
                }
            )

    _write_csv_rows(score_path, rows)
    _write_json(
        metadata_path,
        {
            "gene": gene,
            "model_name": model_name,
            "window_radius": window_radius,
            "n_total": len(rows),
            "scoring_mode": rows[0]["scoring_mode"] if rows else "unknown",
        },
    )
    return rows


def _build_esm1v_ensemble_table(
    paths: RejectRecoveryPaths,
    config: AcceptHardeningConfig,
    gene: str,
    sequence: str,
    variants: list[dict[str, Any]],
    model_ids: tuple[str, ...],
) -> pd.DataFrame:
    model_maps: list[dict[tuple[int, str], dict[str, Any]]] = []
    scoring_modes: list[str] = []
    for model_id in model_ids:
        rows = _ensure_esm1v_ll_rows(
            paths=paths,
            gene=gene,
            sequence=sequence,
            variants=variants,
            model_name=model_id,
            window_radius=config.window_radius,
            checkpoint_every=config.checkpoint_every,
            overwrite=config.overwrite,
        )
        model_maps.append({_variant_key(row): row for row in rows})
        if rows:
            scoring_modes.append(str(rows[0].get("scoring_mode", "unknown")))

    merged_rows: list[dict[str, Any]] = []
    for row in variants:
        key = _variant_key(row)
        ll_values = [float(model_map[key]["ll_proper"]) for model_map in model_maps if key in model_map]
        if len(ll_values) != len(model_maps):
            continue
        merged_rows.append(
            {
                "gene": gene,
                "name": str(row["name"]),
                "position": int(row["position"]),
                "wt_aa": str(row["wt_aa"]).upper(),
                "mut_aa": str(row["mut_aa"]).upper(),
                "label": int(row["label"]),
                "esm1v_ll_mean": float(np.mean(ll_values)),
                "esm1v_ll_std": float(np.std(ll_values, ddof=0)),
                "esm1v_model_count": int(len(ll_values)),
                "esm1v_scoring_mode": scoring_modes[0] if scoring_modes else "unknown",
            }
        )
    return pd.DataFrame(merged_rows)


def run_esm1v_augmentation_suite(
    paths: RejectRecoveryPaths,
    config: AcceptHardeningConfig | None = None,
    genes: tuple[str, ...] = ("TP53", "BRCA2"),
    esm1v_model_ids: tuple[str, ...] = (
        "facebook/esm1v_t33_650M_UR90S_1",
        "facebook/esm1v_t33_650M_UR90S_2",
        "facebook/esm1v_t33_650M_UR90S_3",
        "facebook/esm1v_t33_650M_UR90S_4",
        "facebook/esm1v_t33_650M_UR90S_5",
    ),
    primary_genes: tuple[str, ...] = ("TP53", "BRCA2"),
    run_3b_shadow: bool = True,
    panel_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = config or AcceptHardeningConfig()
    panel_manifest = panel_manifest or build_support_ranked_panel_manifest(paths, config)
    output_dir = _esm1v_augmentation_dir(paths)
    summary_path = output_dir / "esm1v_augmentation_summary.json"
    long_path = output_dir / "esm1v_augmentation_long.csv"
    if summary_path.exists() and long_path.exists() and not config.overwrite:
        return read_json(summary_path)

    long_rows: list[dict[str, Any]] = []
    payload: dict[str, Any] = {
        "benchmark": "ESM-1v augmentation audit",
        "esm1v_model_ids": list(esm1v_model_ids),
        "genes": {},
    }
    shadow_model = config.stronger_model_names[-1] if run_3b_shadow and config.stronger_model_names else None

    for gene in genes:
        context = _load_gene_context(paths, gene, panel_manifest)
        gene_dir = output_dir / gene.lower()
        ensure_dir(gene_dir)
        reference_rows = _ensure_reference_gene_rows(paths, config, gene, panel_manifest, gene_dir / "reference")
        reference_map = {_variant_key(row): row for row in reference_rows}
        ensemble_df = _build_esm1v_ensemble_table(
            paths=paths,
            config=config,
            gene=gene,
            sequence=str(context["sequence"]),
            variants=list(context["variants"]),
            model_ids=esm1v_model_ids,
        )
        merged_rows: list[dict[str, Any]] = []
        for _, row in ensemble_df.iterrows():
            key = (int(row["position"]), str(row["mut_aa"]).upper())
            reference = reference_map.get(key)
            if reference is None:
                continue
            merged_rows.append(
                {
                    "gene": gene,
                    "name": str(row["name"]),
                    "position": int(row["position"]),
                    "wt_aa": str(row["wt_aa"]).upper(),
                    "mut_aa": str(row["mut_aa"]).upper(),
                    "label": int(row["label"]),
                    "reference_ll_proper": float(reference["ll_proper"]),
                    "reference_frob_dist": float(reference["frob_dist"]),
                    "reference_pair_score": float(_pair_scores([reference], config.pair_alpha)["pair"][0]),
                    "esm1v_ll_mean": float(row["esm1v_ll_mean"]),
                    "esm1v_ll_std": float(row["esm1v_ll_std"]),
                    "esm1v_scoring_mode": str(row["esm1v_scoring_mode"]),
                }
            )
        merged_df = pd.DataFrame(merged_rows).sort_values(["position", "mut_aa", "name"]).reset_index(drop=True)
        labels = merged_df["label"].to_numpy(dtype=int).tolist()
        frob_norm = _normalize_values(merged_df["reference_frob_dist"].to_list())
        reference_ll_norm = _normalize_values(merged_df["reference_ll_proper"].to_list())
        esm1v_norm = _normalize_values(merged_df["esm1v_ll_mean"].to_list())
        reference_pair = [
            float(config.pair_alpha * frob + (1.0 - config.pair_alpha) * ll)
            for frob, ll in zip(frob_norm, reference_ll_norm)
        ]
        augmented_pair = [
            float(config.pair_alpha * frob + (1.0 - config.pair_alpha) * ll)
            for frob, ll in zip(frob_norm, esm1v_norm)
        ]
        alpha_sweep, best_alpha = _alpha_sweep_from_vectors(labels, frob_norm, esm1v_norm, config.alpha_step)
        merged_df["reference_frob_norm"] = frob_norm
        merged_df["reference_ll_norm"] = reference_ll_norm
        merged_df["reference_pair_norm"] = reference_pair
        merged_df["esm1v_ll_mean_norm"] = esm1v_norm
        merged_df["augmented_pair_fixed_055"] = augmented_pair
        gene_payload = {
            "gene": gene,
            "n_total": int(len(merged_df)),
            "n_positive": int(merged_df["label"].sum()),
            "n_negative": int(len(merged_df) - int(merged_df["label"].sum())),
            "esm1v_scoring_mode": str(merged_df["esm1v_scoring_mode"].iloc[0]) if not merged_df.empty else "unknown",
            "auc_esm1v_mean": float(_roc_auc_score(labels, esm1v_norm)),
            "auc_reference_pair_fixed_055": float(_roc_auc_score(labels, reference_pair)),
            "auc_augmented_pair_fixed_055": float(_roc_auc_score(labels, augmented_pair)),
            "delta_augmented_vs_esm1v": float(
                _roc_auc_score(labels, augmented_pair) - _roc_auc_score(labels, esm1v_norm)
            ),
            "delta_augmented_vs_reference_pair": float(
                _roc_auc_score(labels, augmented_pair) - _roc_auc_score(labels, reference_pair)
            ),
            "pair_vs_esm1v_bootstrap_delta": paired_bootstrap_delta(
                labels,
                augmented_pair,
                esm1v_norm,
                config.bootstrap_replicates,
                config.random_seed,
            ),
            "best_alpha_on_full_surface": best_alpha,
            "alpha_sweep": alpha_sweep,
        }

        if shadow_model and gene in {item.upper() for item in primary_genes}:
            shadow_rows = _ensure_gene_score_rows(
                gene=gene,
                sequence=str(context["sequence"]),
                variants=list(context["variants"]),
                model_name=shadow_model,
                output_dir=gene_dir / "shadow",
                window_radius=config.window_radius,
                checkpoint_every=config.checkpoint_every,
                overwrite=config.overwrite,
            )
            shadow_map = {_variant_key(row): row for row in shadow_rows}
            shadow_frob_norm = _normalize_values(
                [float(shadow_map[(int(row["position"]), str(row["mut_aa"]).upper())]["frob_dist"]) for _, row in merged_df.iterrows()]
            )
            shadow_pair = [
                float(config.pair_alpha * frob + (1.0 - config.pair_alpha) * ll)
                for frob, ll in zip(shadow_frob_norm, esm1v_norm)
            ]
            merged_df[f"augmented_pair_{_model_slug(shadow_model)}"] = shadow_pair
            gene_payload["shadow_model_name"] = shadow_model
            gene_payload["auc_augmented_pair_shadow"] = float(_roc_auc_score(labels, shadow_pair))
            gene_payload["delta_shadow_vs_esm1v"] = float(
                _roc_auc_score(labels, shadow_pair) - _roc_auc_score(labels, esm1v_norm)
            )

        merged_df.to_csv(gene_dir / "augmentation_table.csv", index=False)
        _write_json(gene_dir / "augmentation_summary.json", gene_payload)
        payload["genes"][gene] = gene_payload
        long_rows.append(
            {
                "gene": gene,
                "n_total": gene_payload["n_total"],
                "n_positive": gene_payload["n_positive"],
                "n_negative": gene_payload["n_negative"],
                "esm1v_scoring_mode": gene_payload["esm1v_scoring_mode"],
                "auc_esm1v_mean": gene_payload["auc_esm1v_mean"],
                "auc_reference_pair_fixed_055": gene_payload["auc_reference_pair_fixed_055"],
                "auc_augmented_pair_fixed_055": gene_payload["auc_augmented_pair_fixed_055"],
                "delta_augmented_vs_esm1v": gene_payload["delta_augmented_vs_esm1v"],
                "delta_augmented_vs_reference_pair": gene_payload["delta_augmented_vs_reference_pair"],
                "best_alpha": float(best_alpha["alpha"]),
                "best_alpha_auc": float(best_alpha["auc"]),
                "paired_delta_ci_2p5": float(gene_payload["pair_vs_esm1v_bootstrap_delta"]["ci_2p5"]),
                "paired_delta_ci_97p5": float(gene_payload["pair_vs_esm1v_bootstrap_delta"]["ci_97p5"]),
                "shadow_model_name": str(gene_payload.get("shadow_model_name", "")),
                "auc_augmented_pair_shadow": float(gene_payload.get("auc_augmented_pair_shadow", np.nan)),
                "delta_shadow_vs_esm1v": float(gene_payload.get("delta_shadow_vs_esm1v", np.nan)),
            }
        )

    _write_csv_rows(long_path, long_rows)
    payload["gene_rows"] = long_rows
    _write_json(summary_path, payload)
    return payload


def run_esm1v_permutation_audit(
    paths: RejectRecoveryPaths,
    config: AcceptHardeningConfig | None = None,
    genes: tuple[str, ...] = ("TP53", "BRCA2"),
    permutation_replicates: int = 1000,
) -> dict[str, Any]:
    config = config or AcceptHardeningConfig()
    output_dir = _esm1v_augmentation_dir(paths)
    rows: list[dict[str, Any]] = []
    payload: dict[str, Any] = {"benchmark": "ESM-1v augmentation permutation audit", "genes": {}}

    for gene in genes:
        table_path = output_dir / gene.lower() / "augmentation_table.csv"
        if not table_path.exists():
            raise FileNotFoundError(f"Missing augmentation table for {gene}: {table_path}")
        df = pd.read_csv(table_path)
        labels = df["label"].to_numpy(dtype=int)
        esm1v_norm = df["esm1v_ll_mean_norm"].to_numpy(dtype=float)
        frob_norm = df["reference_frob_norm"].to_numpy(dtype=float)
        observed_pair = df["augmented_pair_fixed_055"].to_numpy(dtype=float)
        observed_delta = float(_roc_auc_score(labels.tolist(), observed_pair.tolist()) - _roc_auc_score(labels.tolist(), esm1v_norm.tolist()))
        rng = np.random.default_rng(config.random_seed)
        permute_frob_deltas: list[float] = []
        permute_esm1v_deltas: list[float] = []
        for _ in range(int(permutation_replicates)):
            shuffled_frob = rng.permutation(frob_norm)
            shuffled_esm1v = rng.permutation(esm1v_norm)
            pair_from_shuffled_frob = (config.pair_alpha * shuffled_frob) + ((1.0 - config.pair_alpha) * esm1v_norm)
            pair_from_shuffled_esm = (config.pair_alpha * frob_norm) + ((1.0 - config.pair_alpha) * shuffled_esm1v)
            permute_frob_deltas.append(
                float(
                    _roc_auc_score(labels.tolist(), pair_from_shuffled_frob.tolist())
                    - _roc_auc_score(labels.tolist(), esm1v_norm.tolist())
                )
            )
            permute_esm1v_deltas.append(
                float(
                    _roc_auc_score(labels.tolist(), pair_from_shuffled_esm.tolist())
                    - _roc_auc_score(labels.tolist(), shuffled_esm1v.tolist())
                )
            )

        payload["genes"][gene] = {
            "observed_delta_augmented_vs_esm1v": observed_delta,
            "permute_frob_alignment": {
                "mean": float(np.mean(permute_frob_deltas)),
                "ci_2p5": float(np.quantile(permute_frob_deltas, 0.025)),
                "ci_97p5": float(np.quantile(permute_frob_deltas, 0.975)),
                "empirical_p_ge_observed": float(
                    (np.sum(np.asarray(permute_frob_deltas) >= observed_delta) + 1)
                    / (len(permute_frob_deltas) + 1)
                ),
            },
            "permute_esm1v_alignment": {
                "mean": float(np.mean(permute_esm1v_deltas)),
                "ci_2p5": float(np.quantile(permute_esm1v_deltas, 0.025)),
                "ci_97p5": float(np.quantile(permute_esm1v_deltas, 0.975)),
                "empirical_p_ge_observed": float(
                    (np.sum(np.asarray(permute_esm1v_deltas) >= observed_delta) + 1)
                    / (len(permute_esm1v_deltas) + 1)
                ),
            },
        }
        rows.append(
            {
                "gene": gene,
                "observed_delta_augmented_vs_esm1v": observed_delta,
                "permute_frob_mean": float(np.mean(permute_frob_deltas)),
                "permute_frob_ci_2p5": float(np.quantile(permute_frob_deltas, 0.025)),
                "permute_frob_ci_97p5": float(np.quantile(permute_frob_deltas, 0.975)),
                "permute_frob_empirical_p_ge_observed": float(
                    (np.sum(np.asarray(permute_frob_deltas) >= observed_delta) + 1)
                    / (len(permute_frob_deltas) + 1)
                ),
                "permute_esm1v_mean": float(np.mean(permute_esm1v_deltas)),
                "permute_esm1v_ci_2p5": float(np.quantile(permute_esm1v_deltas, 0.025)),
                "permute_esm1v_ci_97p5": float(np.quantile(permute_esm1v_deltas, 0.975)),
                "permute_esm1v_empirical_p_ge_observed": float(
                    (np.sum(np.asarray(permute_esm1v_deltas) >= observed_delta) + 1)
                    / (len(permute_esm1v_deltas) + 1)
                ),
            }
        )

    _write_csv_rows(output_dir / "esm1v_permutation_audit.csv", rows)
    payload["rows"] = rows
    _write_json(output_dir / "esm1v_permutation_audit_summary.json", payload)
    return payload


def freeze_brca2_canonical_benchmark(
    paths: RejectRecoveryPaths,
    config: AcceptHardeningConfig | None = None,
    public_models: tuple[str, ...] = (
        "facebook/esm2_t30_150M_UR50D",
        "facebook/esm2_t33_650M_UR50D",
    ),
    run_3b_shadow: bool = True,
    panel_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = config or AcceptHardeningConfig()
    output_dir = _brca2_canonical_dir(paths)
    summary_path = output_dir / "brca2_canonical_summary.json"
    if summary_path.exists() and not config.overwrite:
        return read_json(summary_path)

    context = _load_gene_context(paths, "BRCA2", panel_manifest)
    variants = list(context["variants"])
    sequence = str(context["sequence"])
    variants_path = output_dir / "brca2_variants.json"
    sequence_path = output_dir / "brca2_sequence.fasta"
    _write_json(variants_path, variants)
    write_text(sequence_path, f">BRCA2_HUMAN\n{sequence}\n")

    model_sequence = list(dict.fromkeys([*public_models, *(config.stronger_model_names if run_3b_shadow else tuple())]))
    model_rows: list[dict[str, Any]] = []
    rows_by_model: dict[str, list[dict[str, Any]]] = {}
    for model_name in model_sequence:
        model_dir = output_dir / _public_model_tag(model_name)
        rows = _ensure_gene_score_rows(
            gene="BRCA2",
            sequence=sequence,
            variants=variants,
            model_name=model_name,
            output_dir=model_dir,
            window_radius=config.window_radius,
            checkpoint_every=config.checkpoint_every,
            overwrite=config.overwrite,
        )
        rows_by_model[model_name] = rows
        summary = _score_rows_summary(rows, config.pair_alpha)
        bootstrap = bootstrap_auc_ci(
            _labels(rows),
            summary["normalized_scores"]["pair_score"],
            config.bootstrap_replicates,
            config.random_seed,
        )
        paired = paired_bootstrap_delta(
            _labels(rows),
            summary["normalized_scores"]["pair_score"],
            summary["normalized_scores"]["ll_proper_norm"],
            config.bootstrap_replicates,
            config.random_seed,
        )
        model_rows.append(
            {
                "gene": "BRCA2",
                "model_name": model_name,
                "model_tag": _public_model_tag(model_name),
                "n_total": int(summary["n_total"]),
                "n_positive": int(summary["n_positive"]),
                "n_negative": int(summary["n_negative"]),
                "auc_ll_proper": float(summary["auc_ll_proper"]),
                "auc_frob_dist": float(summary["auc_frob_dist"]),
                "auc_trace_ratio": float(summary["auc_trace_ratio"]),
                "auc_sps_log": float(summary["auc_sps_log"]),
                "auc_pair_fixed_055": float(summary["auc_pair_fixed_055"]),
                "delta_pair_vs_ll": float(summary["delta_pair_vs_ll"]),
                "pair_ci_2p5": float(bootstrap["ci_2p5"]),
                "pair_ci_97p5": float(bootstrap["ci_97p5"]),
                "paired_delta_ci_2p5": float(paired["ci_2p5"]),
                "paired_delta_ci_97p5": float(paired["ci_97p5"]),
                "score_path": model_dir / f"brca2_{_model_slug(model_name)}_scores.csv",
                "metadata_path": model_dir / f"brca2_{_model_slug(model_name)}_metadata.json",
            }
        )

    reference_model = public_models[0]
    nested_config = NestedCVConfig(
        n_splits=config.nested_cv_n_splits,
        n_repeats=config.nested_cv_n_repeats,
        alpha_step=config.alpha_step,
        random_seed=config.random_seed,
        render_figures=config.render_figures,
        overwrite=config.overwrite,
    )
    nested_summary = run_gene_nested_cv_audit(paths, "BRCA2", rows_by_model[reference_model], nested_config)
    nested_cv_rows = _read_csv_rows(_nested_gene_dir(paths, "BRCA2") / "brca2_nested_cv_fold_results.csv")

    payload = {
        "benchmark": "BRCA2 canonical supplementary freeze",
        "gene": "BRCA2",
        "reference_model": reference_model,
        "public_models": list(public_models),
        "run_3b_shadow": bool(run_3b_shadow),
        "variants_path": variants_path,
        "sequence_path": sequence_path,
        "n_total": int(len(variants)),
        "n_positive": int(sum(int(row["label"]) for row in variants)),
        "n_negative": int(len(variants) - sum(int(row["label"]) for row in variants)),
        "model_rows": model_rows,
        "nested_cv_summary": nested_summary,
        "nested_cv_rows": nested_cv_rows,
    }
    _write_json(summary_path, payload)
    return payload


def render_brca2_canonical_release_artifacts(
    paths: RejectRecoveryPaths,
    brca2_release: dict[str, Any] | None = None,
) -> dict[str, Any]:
    output_dir = _brca2_canonical_dir(paths)
    brca2_release = brca2_release or read_json(output_dir / "brca2_canonical_summary.json")
    model_rows = list(brca2_release["model_rows"])

    public_score_files: dict[str, str] = {}
    for row in model_rows:
        model_tag = str(row["model_tag"])
        score_path = Path(row["score_path"])
        if not score_path.exists():
            continue
        target_path = output_dir / f"brca2_scores_{model_tag}.tsv"
        write_tsv(target_path, _read_csv_rows(score_path))
        public_score_files[model_tag] = str(target_path)

    manifest = {
        "benchmark": "BRCA2 canonical supplementary freeze",
        "gene": "BRCA2",
        "variants_path": str(brca2_release["variants_path"]),
        "sequence_path": str(brca2_release["sequence_path"]),
        "reference_model": str(brca2_release["reference_model"]),
        "public_models": list(brca2_release["public_models"]),
        "public_score_files": public_score_files,
        "nested_cv_summary_path": str(_nested_gene_dir(paths, "BRCA2") / "brca2_nested_cv_summary.json"),
        "n_total": int(brca2_release["n_total"]),
        "n_positive": int(brca2_release["n_positive"]),
        "n_negative": int(brca2_release["n_negative"]),
    }
    verification = {
        "benchmark": "BRCA2 verification payload",
        "reference_model": str(brca2_release["reference_model"]),
        "public_score_files": public_score_files,
        "model_rows": model_rows,
        "nested_cv_mean_auc_fixed_055": float(
            brca2_release["nested_cv_summary"]["comparison_means"]["auc_fixed_055_mean"]
        ),
        "nested_cv_mean_auc_ll_proper": float(
            brca2_release["nested_cv_summary"]["comparison_means"]["auc_ll_proper_mean"]
        ),
    }
    readme_lines = [
        "# BRCA2 Canonical Supplementary Freeze",
        "",
        "This directory freezes the BRCA2 supplementary benchmark payload used in the A100 acceptance push.",
        "",
        "## Files",
    ]
    readme_lines.extend([f"- `{name}` -> `{path}`" for name, path in sorted(public_score_files.items())] or ["- No score files found"])
    readme_lines.extend(
        [
            "",
            "## Nested CV",
            f"- Summary: `{_nested_gene_dir(paths, 'BRCA2') / 'brca2_nested_cv_summary.json'}`",
        ]
    )
    write_text(output_dir / "README.md", "\n".join(readme_lines) + "\n")
    _write_json(output_dir / "brca2_canonical_manifest.json", manifest)
    _write_json(output_dir / "brca2_verification.json", verification)
    return {
        "manifest_path": output_dir / "brca2_canonical_manifest.json",
        "verification_path": output_dir / "brca2_verification.json",
        "public_score_files": public_score_files,
    }


def run_protocol_sweep_suite(
    paths: RejectRecoveryPaths,
    config: AcceptHardeningConfig | None = None,
    genes: tuple[str, ...] = ("TP53", "BRCA1", "BRCA2"),
    window_radii: tuple[int, ...] = (20, 40, 80, 120),
    layer_protocols: tuple[str, ...] = ("last4", "last8", "top_half", "all_layers"),
    alpha_protocols: tuple[str, ...] = ("fixed_055", "nested_best", "esm1v_augmented"),
    model_names: tuple[str, ...] = (
        "facebook/esm2_t30_150M_UR50D",
        "facebook/esm2_t33_650M_UR50D",
        "facebook/esm2_t36_3B_UR50D",
    ),
    panel_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = config or AcceptHardeningConfig()
    panel_manifest = panel_manifest or build_support_ranked_panel_manifest(paths, config)
    output_dir = _protocol_sweep_dir(paths)
    summary_path = output_dir / "protocol_sweep_summary.json"
    long_path = output_dir / "protocol_sweep_long.csv"
    tp53_focus_path = output_dir / "protocol_sweep_tp53_focus.csv"
    if summary_path.exists() and long_path.exists() and not config.overwrite:
        return read_json(summary_path)

    rows: list[dict[str, Any]] = []
    supported_esm1v_genes = {"TP53", "BRCA2"}
    for gene in genes:
        context = _load_gene_context(paths, gene, panel_manifest)
        esm1v_lookup: dict[tuple[int, str], float] | None = None
        if "esm1v_augmented" in alpha_protocols and str(gene).upper() in supported_esm1v_genes:
            esm1v_lookup = _load_esm1v_norm_lookup(
                paths,
                config,
                str(gene).upper(),
                str(context["sequence"]),
                list(context["variants"]),
            )

        for model_name in model_names:
            for window_radius in window_radii:
                gene_dir = output_dir / str(gene).lower() / _model_slug(model_name)
                protocol_rows = _ensure_protocol_gene_rows(
                    gene=str(gene).upper(),
                    sequence=str(context["sequence"]),
                    variants=list(context["variants"]),
                    model_name=model_name,
                    output_dir=gene_dir,
                    window_radius=window_radius,
                    layer_protocols=layer_protocols,
                    checkpoint_every=config.checkpoint_every,
                    overwrite=config.overwrite,
                )
                labels = [int(row["label"]) for row in protocol_rows]
                ll_norm = _normalize_values([float(row["ll_proper"]) for row in protocol_rows])
                for layer_protocol in layer_protocols:
                    frob_norm = _normalize_values(
                        [float(row[f"frob_dist__{layer_protocol}"]) for row in protocol_rows]
                    )
                    fixed_scores = [
                        float(config.pair_alpha * frob + (1.0 - config.pair_alpha) * ll)
                        for frob, ll in zip(frob_norm, ll_norm)
                    ]
                    alpha_sweep, best_alpha = _alpha_sweep_from_vectors(labels, frob_norm, ll_norm, config.alpha_step)
                    row = {
                        "gene": str(gene).upper(),
                        "model_name": model_name,
                        "window_radius": int(window_radius),
                        "layer_protocol": layer_protocol,
                        "n_total": int(len(protocol_rows)),
                        "n_positive": int(sum(labels)),
                        "n_negative": int(len(labels) - sum(labels)),
                        "auc_ll_proper": float(_roc_auc_score(labels, ll_norm)),
                        "auc_frob_dist": float(_roc_auc_score(labels, frob_norm)),
                        "auc_pair_fixed_055": float(_roc_auc_score(labels, fixed_scores)),
                        "delta_pair_fixed_055_vs_ll": float(
                            _roc_auc_score(labels, fixed_scores) - _roc_auc_score(labels, ll_norm)
                        ),
                        "best_alpha": float(best_alpha["alpha"]),
                        "auc_pair_best_alpha": float(best_alpha["auc"]),
                        "delta_pair_best_alpha_vs_ll": float(best_alpha["auc"] - _roc_auc_score(labels, ll_norm)),
                    }
                    if "esm1v_augmented" in alpha_protocols and esm1v_lookup:
                        esm1v_values = [
                            esm1v_lookup.get((int(item["position"]), str(item["mut_aa"]).upper()), np.nan)
                            for item in protocol_rows
                        ]
                        if not any(np.isnan(value) for value in esm1v_values):
                            augmented_scores = [
                                float(config.pair_alpha * frob + (1.0 - config.pair_alpha) * esm)
                                for frob, esm in zip(frob_norm, esm1v_values)
                            ]
                            row["auc_pair_esm1v_augmented"] = float(_roc_auc_score(labels, augmented_scores))
                            row["delta_pair_esm1v_augmented_vs_ll"] = float(
                                _roc_auc_score(labels, augmented_scores) - _roc_auc_score(labels, ll_norm)
                            )
                        else:
                            row["auc_pair_esm1v_augmented"] = np.nan
                            row["delta_pair_esm1v_augmented_vs_ll"] = np.nan
                    else:
                        row["auc_pair_esm1v_augmented"] = np.nan
                        row["delta_pair_esm1v_augmented_vs_ll"] = np.nan
                    rows.append(row)
                _write_json(
                    gene_dir / f"protocol_radius_{int(window_radius)}.json",
                    {
                        "gene": str(gene).upper(),
                        "model_name": model_name,
                        "window_radius": int(window_radius),
                        "layer_protocols": list(layer_protocols),
                        "alpha_protocols": list(alpha_protocols),
                        "alpha_sweep_reference": alpha_sweep,
                    },
                )

    rows.sort(
        key=lambda item: (
            str(item["gene"]),
            str(item["model_name"]),
            int(item["window_radius"]),
            str(item["layer_protocol"]),
        )
    )
    _write_csv_rows(long_path, rows)
    _write_csv_rows(
        tp53_focus_path,
        sorted(
            [row for row in rows if str(row["gene"]).upper() == "TP53"],
            key=lambda item: float(item["auc_pair_best_alpha"]),
            reverse=True,
        ),
    )
    payload = {
        "benchmark": "Protocol robustness sweep",
        "genes": [str(gene).upper() for gene in genes],
        "window_radii": list(window_radii),
        "layer_protocols": list(layer_protocols),
        "alpha_protocols": list(alpha_protocols),
        "model_names": list(model_names),
        "rows": rows,
    }
    _write_json(summary_path, payload)
    return payload


def run_support_ranked_panel_expansion(
    paths: RejectRecoveryPaths,
    config: AcceptHardeningConfig | None = None,
    top_k: int = 25,
    run_650m_shadow: bool = True,
) -> dict[str, Any]:
    config = config or AcceptHardeningConfig()
    output_dir = _panel25_dir(paths)
    summary_path = output_dir / "support_ranked_top25_summary.json"
    csv_path = output_dir / "support_ranked_top25_summary.csv"
    if summary_path.exists() and csv_path.exists() and not config.overwrite:
        return read_json(summary_path)

    expanded_config = replace(
        config,
        max_additional_genes=max(0, int(top_k) - len(config.anchor_genes)),
        render_figures=False,
    )
    panel_paths = create_accept_hardening_paths(repo_root=paths.repo_root, output_root=output_dir)
    support_scan = scan_clinvar_gene_support(panel_paths, expanded_config)
    panel_manifest = build_support_ranked_panel_manifest(panel_paths, expanded_config, support_scan)
    multigene_metrics = run_support_ranked_panel(panel_paths, expanded_config, panel_manifest)

    shadow_model = "facebook/esm2_t33_650M_UR50D"
    shadow_scope = {"TP53", "BRCA1", "BRCA2"}
    rows: list[dict[str, Any]] = []
    for gene in panel_manifest["selected_genes"][: int(top_k)]:
        gene_summary = multigene_metrics["genes"][gene]
        row = {
            "gene": gene,
            "support_rank": int(panel_manifest["genes"][gene].get("support_rank", 0)),
            "n_total": int(gene_summary["n_total"]),
            "n_positive": int(gene_summary["n_positive"]),
            "n_negative": int(gene_summary["n_negative"]),
            "auc_ll_proper": float(gene_summary["auc_ll_proper"]),
            "auc_pair_fixed_055": float(gene_summary["auc_pair_fixed_055"]),
            "delta_pair_vs_ll": float(gene_summary["delta_pair_vs_ll"]),
            "pair_ci_2p5": float(gene_summary["pair_auc_bootstrap"]["ci_2p5"]),
            "pair_ci_97p5": float(gene_summary["pair_auc_bootstrap"]["ci_97p5"]),
            "paired_delta_ci_2p5": float(gene_summary["pair_vs_ll_bootstrap_delta"]["ci_2p5"]),
            "paired_delta_ci_97p5": float(gene_summary["pair_vs_ll_bootstrap_delta"]["ci_97p5"]),
            "shadow_model_name": "",
            "shadow_auc_pair_fixed_055": np.nan,
            "shadow_delta_pair_vs_ll": np.nan,
        }
        if run_650m_shadow and gene.upper() in shadow_scope:
            context = _load_gene_context(panel_paths, gene, panel_manifest)
            shadow_rows = _ensure_gene_score_rows(
                gene=gene,
                sequence=str(context["sequence"]),
                variants=list(context["variants"]),
                model_name=shadow_model,
                output_dir=output_dir / "shadow" / gene.lower(),
                window_radius=config.window_radius,
                checkpoint_every=config.checkpoint_every,
                overwrite=config.overwrite,
            )
            shadow_summary = _score_rows_summary(shadow_rows, config.pair_alpha)
            row["shadow_model_name"] = shadow_model
            row["shadow_auc_pair_fixed_055"] = float(shadow_summary["auc_pair_fixed_055"])
            row["shadow_delta_pair_vs_ll"] = float(shadow_summary["delta_pair_vs_ll"])
        rows.append(row)

    rows.sort(key=lambda item: (int(item["support_rank"]), str(item["gene"])))
    payload = {
        "benchmark": "Support-ranked top-k panel expansion",
        "top_k_requested": int(top_k),
        "top_k_realized": int(len(rows)),
        "shadow_scope": sorted(shadow_scope if run_650m_shadow else set()),
        "rows": rows,
        "panel_manifest_path": output_dir / "support_ranked_panel_manifest.json",
    }
    _write_csv_rows(csv_path, rows)
    _write_json(summary_path, payload)
    return payload


def run_brca1_failure_analysis(
    paths: RejectRecoveryPaths,
    config: AcceptHardeningConfig | None = None,
    strata: tuple[str, ...] = ("domain", "review_status", "substitution_class", "confidence"),
) -> dict[str, Any]:
    config = config or AcceptHardeningConfig()
    output_dir = _brca1_failure_dir(paths)
    summary_path = output_dir / "brca1_failure_analysis.json"
    csv_path = output_dir / "brca1_failure_analysis.csv"
    if summary_path.exists() and csv_path.exists() and not config.overwrite:
        return read_json(summary_path)

    rows = _ensure_reference_gene_rows(paths, config, "BRCA1", output_dir=output_dir / "reference")
    labels = _labels(rows)
    normalized = _pair_scores(rows, config.pair_alpha)
    review_lookup = _load_clinvar_review_lookup(paths, "BRCA1")
    positive_scores = [score for score, row in zip(normalized["pair"], rows) if int(row["label"]) == 1]
    negative_scores = [score for score, row in zip(normalized["pair"], rows) if int(row["label"]) == 0]
    positive_threshold = float(np.quantile(np.asarray(positive_scores, dtype=float), 0.25)) if positive_scores else 0.0
    negative_threshold = float(np.quantile(np.asarray(negative_scores, dtype=float), 0.75)) if negative_scores else 1.0

    variant_rows: list[dict[str, Any]] = []
    for row, ll_norm, frob_norm, pair_score in zip(
        rows,
        normalized["ll_norm"],
        normalized["frob_norm"],
        normalized["pair"],
    ):
        key = (int(row["position"]), str(row["mut_aa"]).upper())
        review = review_lookup.get(
            key,
            {"review_status": "not_found_in_clinvar_subset", "review_rank": 0, "confidence": "unreviewed"},
        )
        variant_rows.append(
            {
                "gene": "BRCA1",
                "name": str(row["name"]),
                "position": int(row["position"]),
                "wt_aa": str(row["wt_aa"]).upper(),
                "mut_aa": str(row["mut_aa"]).upper(),
                "label": int(row["label"]),
                "domain": _brca1_domain_label(int(row["position"])),
                "review_status": str(review["review_status"]),
                "review_rank": int(review["review_rank"]),
                "confidence": str(review["confidence"]),
                "substitution_class": _substitution_class_label(
                    str(row["wt_aa"]).upper(),
                    str(row["mut_aa"]).upper(),
                ),
                "ll_proper_norm": float(ll_norm),
                "frob_dist_norm": float(frob_norm),
                "pair_score": float(pair_score),
                "hard_positive": bool(int(row["label"]) == 1 and float(pair_score) <= positive_threshold),
                "hard_negative": bool(int(row["label"]) == 0 and float(pair_score) >= negative_threshold),
            }
        )

    variant_df = pd.DataFrame(variant_rows)
    summary_rows: list[dict[str, Any]] = []
    summary_rows.append(
        {
            "stratum": "all",
            "value": "all",
            "n_total": int(len(variant_df)),
            "n_positive": int(variant_df["label"].sum()),
            "n_negative": int(len(variant_df) - int(variant_df["label"].sum())),
            "auc_pair": float(_roc_auc_score(labels, variant_df["pair_score"].astype(float).tolist())),
            "auc_ll": float(_roc_auc_score(labels, variant_df["ll_proper_norm"].astype(float).tolist())),
            "delta_pair_vs_ll": float(
                _roc_auc_score(labels, variant_df["pair_score"].astype(float).tolist())
                - _roc_auc_score(labels, variant_df["ll_proper_norm"].astype(float).tolist())
            ),
            "hard_positive_rate": float(
                variant_df.loc[variant_df["label"] == 1, "hard_positive"].astype(float).mean()
            ),
            "hard_negative_rate": float(
                variant_df.loc[variant_df["label"] == 0, "hard_negative"].astype(float).mean()
            ),
        }
    )
    for stratum in strata:
        for value, frame in variant_df.groupby(stratum):
            labels_frame = frame["label"].astype(int).tolist()
            has_both_classes = len(set(labels_frame)) > 1
            summary_rows.append(
                {
                    "stratum": stratum,
                    "value": str(value),
                    "n_total": int(len(frame)),
                    "n_positive": int(frame["label"].sum()),
                    "n_negative": int(len(frame) - int(frame["label"].sum())),
                    "auc_pair": float(_roc_auc_score(labels_frame, frame["pair_score"].astype(float).tolist()))
                    if has_both_classes
                    else np.nan,
                    "auc_ll": float(_roc_auc_score(labels_frame, frame["ll_proper_norm"].astype(float).tolist()))
                    if has_both_classes
                    else np.nan,
                    "delta_pair_vs_ll": float(
                        _roc_auc_score(labels_frame, frame["pair_score"].astype(float).tolist())
                        - _roc_auc_score(labels_frame, frame["ll_proper_norm"].astype(float).tolist())
                    )
                    if has_both_classes
                    else np.nan,
                    "hard_positive_rate": float(
                        frame.loc[frame["label"] == 1, "hard_positive"].astype(float).mean()
                    )
                    if int(frame["label"].sum()) > 0
                    else np.nan,
                    "hard_negative_rate": float(
                        frame.loc[frame["label"] == 0, "hard_negative"].astype(float).mean()
                    )
                    if int(len(frame) - int(frame["label"].sum())) > 0
                    else np.nan,
                }
            )

    summary_rows.sort(key=lambda item: (str(item["stratum"]), -int(item["n_total"]), str(item["value"])))
    _write_csv_rows(csv_path, summary_rows)
    _write_csv_rows(output_dir / "brca1_failure_variants.csv", variant_rows)
    payload = {
        "benchmark": "BRCA1 failure analysis",
        "rows": summary_rows,
        "variant_rows_path": output_dir / "brca1_failure_variants.csv",
        "summary_path": csv_path,
    }
    _write_json(summary_path, payload)
    return payload


__all__ = [
    "AcceptHardeningConfig",
    "build_support_ranked_panel_manifest",
    "create_accept_hardening_paths",
    "freeze_brca2_canonical_benchmark",
    "recommend_second_benchmark_candidate",
    "run_accept_hardening_suite",
    "run_brca1_failure_analysis",
    "run_deep_checkpoint_sweep",
    "run_esm1v_augmentation_suite",
    "run_esm1v_permutation_audit",
    "run_gene_nested_cv_audit",
    "run_protocol_sweep_suite",
    "run_shortlist_gene_nested_cv",
    "run_support_ranked_panel_expansion",
    "run_support_ranked_panel",
    "scan_clinvar_gene_support",
    "render_brca2_canonical_release_artifacts",
]
