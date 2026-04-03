"""Final acceptance-oriented supplementary validation helpers."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold

from spectralbio.constants import ALPHA, MODEL_NAME, PROJECT_ROOT, WINDOW_RADIUS
from spectralbio.data.load_benchmarks import load_brca1_full_filtered, load_tp53_scores, load_tp53_variants
from spectralbio.data.sequences import load_brca1_sequence, load_tp53_sequence
from spectralbio.pipeline.evaluate import _roc_auc_score
from spectralbio.supplementary.reject_recovery import (
    BackboneEvaluationConfig,
    MultiGeneConfig,
    NestedCVConfig,
    RejectRecoveryPaths,
    _alpha_sweep_on_rows,
    _build_gene_rows_from_clinvar,
    _download_clinvar_variant_summary,
    _ensure_gene_score_rows,
    _fetch_uniprot_sequence,
    _inner_tuned_alpha,
    _labels,
    _load_clinvar_subset,
    _pair_scores,
    _read_csv_rows,
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
from spectralbio.utils.io import ensure_dir, read_json

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


__all__ = [
    "AcceptHardeningConfig",
    "build_support_ranked_panel_manifest",
    "create_accept_hardening_paths",
    "recommend_second_benchmark_candidate",
    "run_accept_hardening_suite",
    "run_deep_checkpoint_sweep",
    "run_gene_nested_cv_audit",
    "run_shortlist_gene_nested_cv",
    "run_support_ranked_panel",
    "scan_clinvar_gene_support",
]
