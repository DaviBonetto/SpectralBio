"""Supplementary reject-recovery helpers for Colab reruns.

This module is intentionally separate from the canonical CLI and frozen outputs.
It exists to support leakage audits, stronger-backbone reruns, and broader
supplementary gene panels without mutating the public verification contract.
"""

from __future__ import annotations

import csv
import gzip
import json
import math
import shutil
import time
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.model_selection import StratifiedKFold

from spectralbio.constants import ALPHA, MODEL_NAME, PROJECT_ROOT, WINDOW_RADIUS
from spectralbio.data.load_benchmarks import load_brca1_full_filtered, load_tp53_scores, load_tp53_variants
from spectralbio.data.sequences import load_brca1_sequence, load_tp53_sequence
from spectralbio.pipeline.compute_ll_proper import compute_ll_proper
from spectralbio.pipeline.evaluate import _roc_auc_score
from spectralbio.utils.io import ensure_dir, read_json, write_json, write_text

CLINVAR_VARIANT_SUMMARY_URL = "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz"
DEFAULT_STRONGER_BACKBONE = "facebook/esm2_t33_650M_UR50D"
DEFAULT_MULTIGENE_CANDIDATES = ("PTEN", "MSH2", "MLH1", "CHEK2", "PALB2", "BRCA2", "ATM")
DEFAULT_NOTEBOOK_REPO_URL = "https://github.com/DaviBonetto/SpectralBio.git"

THREE_TO_ONE_AA = {
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

REVIEW_STATUS_RANK = {
    "practice guideline": 4,
    "reviewed by expert panel": 3,
    "criteria provided, multiple submitters, no conflicts": 2,
    "criteria provided, conflicting classifications": 1,
    "criteria provided, single submitter": 1,
    "no assertion criteria provided": 0,
    "no assertion for the individual variant": 0,
}

CLINVAR_COLUMNS = [
    "GeneSymbol",
    "Type",
    "Name",
    "ClinicalSignificance",
    "OriginSimple",
    "Assembly",
    "ReviewStatus",
    "VariationID",
]


@dataclass(frozen=True)
class RejectRecoveryPaths:
    repo_root: Path
    root: Path
    leakage_audit: Path
    backbone_strength: Path
    multigene: Path
    figures: Path
    tables: Path
    logs: Path
    configs: Path
    cache: Path
    final_bundle: Path


@dataclass(frozen=True)
class NestedCVConfig:
    n_splits: int = 5
    n_repeats: int = 5
    alpha_step: float = 0.05
    random_seed: int = 42
    render_figures: bool = True
    overwrite: bool = False

    def alpha_values(self) -> list[float]:
        return alpha_grid(self.alpha_step)


@dataclass(frozen=True)
class BackboneEvaluationConfig:
    reference_model_name: str = MODEL_NAME
    stronger_model_name: str = DEFAULT_STRONGER_BACKBONE
    window_radius: int = WINDOW_RADIUS
    pair_alpha: float = ALPHA
    random_seed: int = 42
    checkpoint_every: int = 10
    render_figures: bool = True
    overwrite: bool = False
    reuse_frozen_tp53_reference: bool = True
    run_full_surface_alpha_sweep: bool = True


@dataclass(frozen=True)
class MultiGeneConfig:
    candidate_genes: tuple[str, ...] = DEFAULT_MULTIGENE_CANDIDATES
    model_name: str = MODEL_NAME
    window_radius: int = WINDOW_RADIUS
    pair_alpha: float = ALPHA
    random_seed: int = 42
    checkpoint_every: int = 10
    bootstrap_replicates: int = 1000
    min_total: int = 40
    min_per_class: int = 10
    max_additional_genes: int = 4
    render_figures: bool = True
    overwrite: bool = False
    reuse_frozen_tp53_reference: bool = True


def alpha_grid(step: float) -> list[float]:
    if step <= 0.0 or step > 1.0:
        raise ValueError("alpha step must be in (0, 1].")
    return [round(float(value), 2) for value in np.arange(0.0, 1.0 + 1e-9, step)]


def create_reject_recovery_paths(
    repo_root: Path | None = None,
    output_root: Path | None = None,
) -> RejectRecoveryPaths:
    repo_root = (repo_root or PROJECT_ROOT).resolve()
    root = (output_root or repo_root / "supplementary" / "reject_recovery").resolve()
    paths = RejectRecoveryPaths(
        repo_root=repo_root,
        root=root,
        leakage_audit=root / "leakage_audit",
        backbone_strength=root / "backbone_strength",
        multigene=root / "multigene",
        figures=root / "figures",
        tables=root / "tables",
        logs=root / "logs",
        configs=root / "configs",
        cache=root / "cache",
        final_bundle=root / "final_bundle",
    )
    for path in asdict(paths).values():
        if isinstance(path, Path):
            ensure_dir(path)
    return paths


def _json_ready(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(key): _json_ready(inner) for key, inner in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    return value


def _write_json(path: Path, data: Any) -> Path:
    return write_json(path, _json_ready(data))


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return [dict(row) for row in reader]


def _write_csv_rows(path: Path, rows: list[dict[str, Any]]) -> Path:
    ensure_dir(path.parent)
    if not rows:
        path.write_text("", encoding="utf-8")
        return path
    headers = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _json_ready(row.get(key, "")) for key in headers})
    return path


def _fit_minmax(values: list[float]) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0
    return float(min(values)), float(max(values))


def _apply_minmax(values: list[float], minimum: float, maximum: float) -> list[float]:
    if maximum <= minimum:
        return [0.0 for _ in values]
    scale = maximum - minimum
    return [(float(value) - minimum) / scale for value in values]


def _pair_scores(
    rows: list[dict[str, Any]],
    alpha: float,
    fit_rows: list[dict[str, Any]] | None = None,
) -> dict[str, list[float]]:
    fit_rows = fit_rows or rows
    fit_frob_min, fit_frob_max = _fit_minmax([float(row["frob_dist"]) for row in fit_rows])
    fit_ll_min, fit_ll_max = _fit_minmax([float(row["ll_proper"]) for row in fit_rows])
    frob_norm = _apply_minmax([float(row["frob_dist"]) for row in rows], fit_frob_min, fit_frob_max)
    ll_norm = _apply_minmax([float(row["ll_proper"]) for row in rows], fit_ll_min, fit_ll_max)
    pair = [float(alpha * frob + (1.0 - alpha) * ll) for frob, ll in zip(frob_norm, ll_norm)]
    return {"frob_norm": frob_norm, "ll_norm": ll_norm, "pair": pair}


def _labels(rows: list[dict[str, Any]]) -> list[int]:
    return [int(row["label"]) for row in rows]


def _subset_rows(rows: list[dict[str, Any]], indices: list[int] | np.ndarray) -> list[dict[str, Any]]:
    return [rows[int(index)] for index in indices]


def _safe_stratified_splits(labels: list[int], requested_splits: int) -> int:
    counts = Counter(labels)
    if not counts:
        raise ValueError("Cannot build a stratified split for an empty label vector.")
    return max(2, min(requested_splits, min(counts.values())))


def _alpha_sweep_on_rows(rows: list[dict[str, Any]], step: float) -> tuple[list[dict[str, float]], dict[str, float]]:
    labels = _labels(rows)
    sweep_rows: list[dict[str, float]] = []
    best_row: dict[str, float] | None = None
    for alpha in alpha_grid(step):
        pair = _pair_scores(rows, alpha)["pair"]
        auc = float(_roc_auc_score(labels, pair))
        row = {"alpha": float(alpha), "beta": float(1.0 - alpha), "auc": auc}
        sweep_rows.append(row)
        if best_row is None or auc > best_row["auc"]:
            best_row = row
    if best_row is None:
        raise RuntimeError("alpha sweep produced no result")
    return sweep_rows, best_row


def _inner_tuned_alpha(
    train_rows: list[dict[str, Any]],
    config: NestedCVConfig,
    seed: int,
) -> tuple[float, list[dict[str, float]]]:
    labels = _labels(train_rows)
    n_splits = _safe_stratified_splits(labels, max(3, config.n_splits - 1))
    splitter = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    summary: list[dict[str, float]] = []
    alpha_to_scores = {alpha: [] for alpha in config.alpha_values()}

    for inner_train_idx, inner_val_idx in splitter.split(np.zeros(len(train_rows)), labels):
        inner_train = _subset_rows(train_rows, inner_train_idx)
        inner_val = _subset_rows(train_rows, inner_val_idx)
        inner_labels = _labels(inner_val)
        for alpha in config.alpha_values():
            val_scores = _pair_scores(inner_val, alpha, fit_rows=inner_train)["pair"]
            alpha_to_scores[alpha].append(float(_roc_auc_score(inner_labels, val_scores)))

    best_alpha = 0.0
    best_mean = -math.inf
    best_std = math.inf
    for alpha, aucs in alpha_to_scores.items():
        mean_auc = float(np.mean(aucs))
        std_auc = float(np.std(aucs, ddof=0))
        summary.append({"alpha": float(alpha), "mean_auc": mean_auc, "std_auc": std_auc})
        if mean_auc > best_mean or (math.isclose(mean_auc, best_mean) and std_auc < best_std):
            best_alpha = float(alpha)
            best_mean = mean_auc
            best_std = std_auc

    summary.sort(key=lambda row: row["alpha"])
    return best_alpha, summary


def run_tp53_nested_cv_audit(
    paths: RejectRecoveryPaths,
    config: NestedCVConfig | None = None,
    score_rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    config = config or NestedCVConfig()
    rows = score_rows or list(load_tp53_scores())
    labels = _labels(rows)
    outer_splits = _safe_stratified_splits(labels, config.n_splits)
    seeds = [config.random_seed + offset for offset in range(config.n_repeats)]

    fold_rows: list[dict[str, Any]] = []
    alpha_distribution: list[dict[str, Any]] = []
    inner_sweeps: dict[str, list[dict[str, float]]] = {}

    for repeat_index, seed in enumerate(seeds):
        splitter = StratifiedKFold(n_splits=outer_splits, shuffle=True, random_state=seed)
        for fold_index, (train_idx, test_idx) in enumerate(splitter.split(np.zeros(len(rows)), labels), start=1):
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

            row = {
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
            fold_rows.append(row)
            alpha_distribution.append({"repeat": repeat_index + 1, "fold": fold_index, "chosen_alpha": float(chosen_alpha)})

    summary = {
        "benchmark": "TP53 nested CV leakage audit",
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
            "fold_results": paths.leakage_audit / "tp53_nested_cv_fold_results.csv",
            "alpha_distribution": paths.leakage_audit / "tp53_nested_cv_alpha_distribution.csv",
            "summary": paths.leakage_audit / "tp53_nested_cv_summary.json",
            "inner_sweeps": paths.leakage_audit / "tp53_nested_cv_inner_sweeps.json",
        },
    }

    _write_csv_rows(paths.leakage_audit / "tp53_nested_cv_fold_results.csv", fold_rows)
    _write_csv_rows(paths.leakage_audit / "tp53_nested_cv_alpha_distribution.csv", alpha_distribution)
    _write_json(paths.leakage_audit / "tp53_nested_cv_inner_sweeps.json", inner_sweeps)
    _write_json(paths.leakage_audit / "tp53_nested_cv_summary.json", summary)
    _write_json(paths.configs / "nested_cv_config.json", asdict(config))

    if config.render_figures:
        _render_nested_cv_figures(paths.leakage_audit, fold_rows, alpha_distribution)

    return summary


def covariance_features_dual(hidden_wt: np.ndarray, hidden_mut: np.ndarray) -> dict[str, float]:
    if hidden_wt.shape != hidden_mut.shape:
        raise ValueError(f"hidden-state tensors must match, got {hidden_wt.shape} vs {hidden_mut.shape}")

    frob_dists: list[float] = []
    trace_ratios: list[float] = []
    shifts_log: list[float] = []

    for layer_index in range(hidden_wt.shape[0]):
        wt = np.asarray(hidden_wt[layer_index], dtype=np.float64)
        mut = np.asarray(hidden_mut[layer_index], dtype=np.float64)
        wt_centered = wt - np.mean(wt, axis=0, keepdims=True)
        mut_centered = mut - np.mean(mut, axis=0, keepdims=True)
        observations = wt_centered.shape[0]
        if observations <= 1:
            frob_dists.append(0.0)
            trace_ratios.append(0.0)
            shifts_log.append(0.0)
            continue

        scale = math.sqrt(observations - 1.0)
        wt_scaled = wt_centered / scale
        mut_scaled = mut_centered / scale
        gram_wt = wt_scaled @ wt_scaled.T
        gram_mut = mut_scaled @ mut_scaled.T
        cross = wt_scaled @ mut_scaled.T

        frob_sq = float(
            np.trace(gram_wt @ gram_wt)
            + np.trace(gram_mut @ gram_mut)
            - 2.0 * np.sum(cross * cross)
        )
        frob_dists.append(math.sqrt(max(frob_sq, 0.0)))

        trace_wt = float(np.trace(gram_wt))
        trace_mut = float(np.trace(gram_mut))
        if abs(trace_wt) > 1e-12:
            trace_ratios.append(abs((trace_mut / trace_wt) - 1.0))
        else:
            trace_ratios.append(0.0)

        eig_wt = np.sort(np.abs(np.linalg.eigvalsh(gram_wt))) + 1e-12
        eig_mut = np.sort(np.abs(np.linalg.eigvalsh(gram_mut))) + 1e-12
        shifts_log.append(float(np.linalg.norm(np.log(eig_mut) - np.log(eig_wt)) ** 2))

    return {
        "frob_dist": float(np.mean(frob_dists)),
        "trace_ratio": float(np.mean(trace_ratios)),
        "sps_log": float(np.mean(shifts_log)),
    }


def _local_window(sequence: str, center_pos: int, window_radius: int) -> tuple[str, int]:
    start = max(0, int(center_pos) - int(window_radius))
    end = min(len(sequence), int(center_pos) + int(window_radius) + 1)
    local_sequence = sequence[start:end]
    return local_sequence, int(center_pos - start)


def _mutate_local_sequence(local_sequence: str, local_pos: int, wt_aa: str, mut_aa: str) -> str:
    if local_sequence[local_pos].upper() != wt_aa.upper():
        raise ValueError(
            f"WT residue mismatch inside local window: expected {wt_aa}, found {local_sequence[local_pos]}"
        )
    return local_sequence[:local_pos] + mut_aa.upper() + local_sequence[local_pos + 1 :]


def _load_esm_bundle(model_name: str):
    import torch
    from transformers import EsmForMaskedLM, EsmTokenizer

    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if device == "cuda" else torch.float32
    tokenizer = EsmTokenizer.from_pretrained(model_name)
    model = EsmForMaskedLM.from_pretrained(
        model_name,
        torch_dtype=torch_dtype,
        low_cpu_mem_usage=True,
    ).to(device).eval()
    aa_token_ids = {aa: tokenizer.convert_tokens_to_ids(aa) for aa in "ACDEFGHIKLMNPQRSTVWY"}
    return tokenizer, model, device, aa_token_ids


def _release_esm_bundle(bundle: Any) -> None:
    import torch

    _, model, _, _ = bundle
    del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def _forward_local_sequence(local_sequence: str, bundle: Any) -> tuple[np.ndarray, Any]:
    import torch

    tokenizer, model, device, _ = bundle
    inputs = tokenizer(local_sequence, return_tensors="pt", add_special_tokens=True, padding=False)
    inputs = {key: value.to(device) for key, value in inputs.items()}
    with torch.inference_mode():
        outputs = model(**inputs, output_hidden_states=True)
    hidden = torch.stack(outputs.hidden_states[1:], dim=0)[:, 0, 1:-1, :].detach().cpu().float().numpy()
    logits = outputs.logits[0].detach().cpu().float()
    return hidden, logits


def _score_variant_from_sequence(
    sequence: str,
    row: dict[str, Any],
    bundle: Any,
    window_radius: int,
    wt_cache: dict[int, tuple[np.ndarray, Any, int]],
) -> dict[str, Any]:
    position = int(row["position"])
    wt_aa = str(row["wt_aa"]).upper()
    mut_aa = str(row["mut_aa"]).upper()
    if sequence[position].upper() != wt_aa:
        raise ValueError(
            f"WT residue mismatch for {row['name']}: expected {wt_aa}, found {sequence[position]}"
        )

    if position not in wt_cache:
        wt_local, local_pos = _local_window(sequence, position, window_radius)
        wt_hidden, wt_logits = _forward_local_sequence(wt_local, bundle)
        wt_cache[position] = (wt_hidden, wt_logits, local_pos)

    wt_hidden, wt_logits, local_pos = wt_cache[position]
    wt_local, _ = _local_window(sequence, position, window_radius)
    mut_local = _mutate_local_sequence(wt_local, local_pos, wt_aa, mut_aa)
    mut_hidden, _ = _forward_local_sequence(mut_local, bundle)

    covariance_metrics = covariance_features_dual(wt_hidden, mut_hidden)
    _, _, _, aa_token_ids = bundle
    ll_proper = compute_ll_proper(wt_logits, local_pos, wt_aa, mut_aa, aa_token_ids)

    return {
        "gene": str(row["gene"]).upper(),
        "name": str(row["name"]),
        "position": position,
        "wt_aa": wt_aa,
        "mut_aa": mut_aa,
        "label": int(row["label"]),
        "frob_dist": float(covariance_metrics["frob_dist"]),
        "trace_ratio": float(covariance_metrics["trace_ratio"]),
        "sps_log": float(covariance_metrics["sps_log"]),
        "ll_proper": float(ll_proper),
    }


def _score_rows_summary(rows: list[dict[str, Any]], pair_alpha: float) -> dict[str, Any]:
    labels = _labels(rows)
    trace_values = [float(row["trace_ratio"]) for row in rows]
    sps_values = [float(row["sps_log"]) for row in rows]
    metrics = {
        "ll_proper_norm": _pair_scores(rows, 0.0)["ll_norm"],
        "frob_dist_norm": _pair_scores(rows, 1.0)["frob_norm"],
        "pair_score": _pair_scores(rows, pair_alpha)["pair"],
        "trace_ratio_norm": _apply_minmax(trace_values, *_fit_minmax(trace_values)),
        "sps_log_norm": _apply_minmax(sps_values, *_fit_minmax(sps_values)),
    }
    return {
        "n_total": len(rows),
        "n_positive": int(sum(labels)),
        "n_negative": int(len(labels) - sum(labels)),
        "auc_ll_proper": float(_roc_auc_score(labels, metrics["ll_proper_norm"])),
        "auc_frob_dist": float(_roc_auc_score(labels, metrics["frob_dist_norm"])),
        "auc_trace_ratio": float(_roc_auc_score(labels, metrics["trace_ratio_norm"])),
        "auc_sps_log": float(_roc_auc_score(labels, metrics["sps_log_norm"])),
        "auc_pair_fixed_055": float(_roc_auc_score(labels, metrics["pair_score"])),
        "delta_pair_vs_ll": float(
            _roc_auc_score(labels, metrics["pair_score"]) - _roc_auc_score(labels, metrics["ll_proper_norm"])
        ),
        "normalized_scores": metrics,
    }


def _typed_score_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "gene": str(row["gene"]),
        "name": str(row["name"]),
        "position": int(row["position"]),
        "wt_aa": str(row["wt_aa"]),
        "mut_aa": str(row["mut_aa"]),
        "label": int(row["label"]),
        "frob_dist": float(row["frob_dist"]),
        "trace_ratio": float(row["trace_ratio"]),
        "sps_log": float(row["sps_log"]),
        "ll_proper": float(row["ll_proper"]),
        "model_name": str(row.get("model_name", MODEL_NAME)),
    }


def _model_slug(model_name: str) -> str:
    return model_name.replace("/", "_").replace("-", "_")


def _ensure_gene_score_rows(
    gene: str,
    sequence: str,
    variants: list[dict[str, Any]],
    model_name: str,
    output_dir: Path,
    window_radius: int,
    checkpoint_every: int,
    overwrite: bool,
) -> list[dict[str, Any]]:
    score_path = output_dir / f"{gene.lower()}_{_model_slug(model_name)}_scores.csv"
    metadata_path = output_dir / f"{gene.lower()}_{_model_slug(model_name)}_metadata.json"
    if score_path.exists() and not overwrite:
        existing = _read_csv_rows(score_path)
        if existing and len(existing) >= len(variants):
            return [_typed_score_row(row) for row in existing]

    done_rows = {_typed_score_row(row)["name"]: _typed_score_row(row) for row in _read_csv_rows(score_path)}
    bundle = _load_esm_bundle(model_name)
    wt_cache: dict[int, tuple[np.ndarray, Any, int]] = {}
    started_at = time.time()

    try:
        for index, row in enumerate(variants, start=1):
            if str(row["name"]) in done_rows:
                continue
            scored = _score_variant_from_sequence(sequence, row, bundle, window_radius, wt_cache)
            scored["model_name"] = model_name
            done_rows[str(row["name"])] = scored
            if index % checkpoint_every == 0 or index == len(variants):
                ordered = [_row for _row in (done_rows.get(str(item["name"])) for item in variants) if _row is not None]
                _write_csv_rows(score_path, ordered)
                _write_json(
                    metadata_path,
                    {
                        "gene": gene,
                        "model_name": model_name,
                        "window_radius": window_radius,
                        "n_variants_total": len(variants),
                        "n_variants_written": len(ordered),
                        "elapsed_seconds": float(time.time() - started_at),
                    },
                )
    finally:
        _release_esm_bundle(bundle)

    return [_row for _row in (done_rows.get(str(item["name"])) for item in variants) if _row is not None]


def run_tp53_backbone_comparison(
    paths: RejectRecoveryPaths,
    config: BackboneEvaluationConfig | None = None,
) -> dict[str, Any]:
    config = config or BackboneEvaluationConfig()
    tp53_rows = list(load_tp53_variants())
    tp53_sequence = load_tp53_sequence()

    per_model_rows: dict[str, list[dict[str, Any]]] = {}
    if config.reuse_frozen_tp53_reference and config.reference_model_name == MODEL_NAME:
        reference_rows = [_typed_score_row({**row, "gene": "TP53", "model_name": config.reference_model_name}) for row in load_tp53_scores()]
    else:
        reference_rows = _ensure_gene_score_rows(
            gene="TP53",
            sequence=tp53_sequence,
            variants=tp53_rows,
            model_name=config.reference_model_name,
            output_dir=paths.backbone_strength,
            window_radius=config.window_radius,
            checkpoint_every=config.checkpoint_every,
            overwrite=config.overwrite,
        )

    stronger_rows = _ensure_gene_score_rows(
        gene="TP53",
        sequence=tp53_sequence,
        variants=tp53_rows,
        model_name=config.stronger_model_name,
        output_dir=paths.backbone_strength,
        window_radius=config.window_radius,
        checkpoint_every=config.checkpoint_every,
        overwrite=config.overwrite,
    )

    per_model_rows[config.reference_model_name] = reference_rows
    per_model_rows[config.stronger_model_name] = stronger_rows

    summary_rows: list[dict[str, Any]] = []
    metrics_payload: dict[str, Any] = {"benchmark": "TP53 backbone comparison", "models": {}}

    for model_name, model_rows in per_model_rows.items():
        summary = _score_rows_summary(model_rows, config.pair_alpha)
        alpha_sweep_rows, best_alpha = _alpha_sweep_on_rows(model_rows, 0.05) if config.run_full_surface_alpha_sweep else ([], {})
        model_summary = {
            "model_name": model_name,
            "window_radius": config.window_radius,
            "pair_alpha": config.pair_alpha,
            "alpha_sweep": alpha_sweep_rows,
            "best_alpha_on_full_surface": best_alpha,
            **{key: value for key, value in summary.items() if key != "normalized_scores"},
        }
        metrics_payload["models"][model_name] = model_summary
        summary_rows.append(
            {
                "model_name": model_name,
                "n_total": model_summary["n_total"],
                "auc_ll_proper": model_summary["auc_ll_proper"],
                "auc_frob_dist": model_summary["auc_frob_dist"],
                "auc_trace_ratio": model_summary["auc_trace_ratio"],
                "auc_sps_log": model_summary["auc_sps_log"],
                "auc_pair_fixed_055": model_summary["auc_pair_fixed_055"],
                "delta_pair_vs_ll": model_summary["delta_pair_vs_ll"],
                "best_alpha_on_full_surface": float(best_alpha.get("alpha", config.pair_alpha)),
                "best_alpha_auc": float(best_alpha.get("auc", model_summary["auc_pair_fixed_055"])),
            }
        )

    _write_csv_rows(paths.backbone_strength / "tp53_backbone_comparison.csv", summary_rows)
    _write_json(paths.backbone_strength / "tp53_backbone_metrics.json", metrics_payload)
    _write_json(paths.configs / "backbone_config.json", asdict(config))

    if config.render_figures:
        _render_backbone_figures(paths.backbone_strength, summary_rows)

    return metrics_payload


def _classify_clinsig(raw_value: str) -> int | None:
    value = str(raw_value).strip()
    if value in {"Pathogenic", "Likely pathogenic", "Pathogenic/Likely pathogenic", "Likely pathogenic/Pathogenic"}:
        return 1
    if value in {"Benign", "Likely benign", "Benign/Likely benign", "Likely benign/Benign"}:
        return 0
    return None


def _parse_protein_change(name: str) -> tuple[str, int, str] | None:
    import re

    match = re.search(r"\(p\.([A-Z][a-z]{2})(\d+)([A-Z][a-z]{2})\)", name)
    if not match:
        return None
    wt_three, position, mut_three = match.groups()
    if wt_three not in THREE_TO_ONE_AA or mut_three not in THREE_TO_ONE_AA:
        return None
    return THREE_TO_ONE_AA[wt_three], int(position), THREE_TO_ONE_AA[mut_three]


def _download_clinvar_variant_summary(cache_dir: Path) -> Path:
    target = cache_dir / "clinvar_variant_summary.txt.gz"
    if target.exists():
        return target
    ensure_dir(target.parent)
    urllib.request.urlretrieve(CLINVAR_VARIANT_SUMMARY_URL, target)
    return target


def _load_clinvar_subset(summary_path: Path, gene_symbols: tuple[str, ...]) -> list[dict[str, str]]:
    gene_set = {gene.upper() for gene in gene_symbols}
    try:
        import pandas as pd

        frames = []
        for chunk in pd.read_csv(
            summary_path,
            sep="\t",
            compression="gzip",
            usecols=CLINVAR_COLUMNS,
            dtype=str,
            keep_default_na=False,
            chunksize=250000,
        ):
            filtered = chunk[chunk["GeneSymbol"].str.upper().isin(gene_set)]
            if not filtered.empty:
                frames.append(filtered)
        if not frames:
            return []
        return pd.concat(frames, ignore_index=True).to_dict("records")
    except ImportError:
        rows: list[dict[str, str]] = []
        with gzip.open(summary_path, "rt", encoding="utf-8", errors="replace") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            for row in reader:
                if str(row["GeneSymbol"]).upper() in gene_set:
                    rows.append({key: str(row.get(key, "")) for key in CLINVAR_COLUMNS})
        return rows


def _fetch_uniprot_sequence(gene: str, cache_dir: Path) -> tuple[str, Path]:
    target = cache_dir / f"{gene.lower()}.fasta"
    if not target.exists():
        query = urllib.parse.quote(f"gene_exact:{gene} AND organism_id:9606 AND reviewed:true")
        url = f"https://rest.uniprot.org/uniprotkb/search?query={query}&format=fasta&size=1"
        with urllib.request.urlopen(url, timeout=120) as response:
            text = response.read().decode("utf-8")
        if not text.startswith(">"):
            raise RuntimeError(f"UniProt returned no reviewed FASTA for {gene}.")
        write_text(target, text)
    lines = [line.strip() for line in target.read_text(encoding="utf-8").splitlines() if line.strip()]
    sequence = "".join(line for line in lines if not line.startswith(">"))
    if not sequence:
        raise RuntimeError(f"Cached FASTA for {gene} is empty: {target}")
    return sequence, target


def _build_gene_rows_from_clinvar(
    gene: str,
    sequence: str,
    clinvar_rows: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    selected: dict[tuple[int, str], dict[str, Any]] = {}
    stats = Counter()
    for row in clinvar_rows:
        stats["rows_seen"] += 1
        if str(row.get("Assembly", "")) != "GRCh38":
            stats["skip_non_grch38"] += 1
            continue
        if str(row.get("Type", "")) != "single nucleotide variant":
            stats["skip_non_snv"] += 1
            continue
        origin_simple = str(row.get("OriginSimple", "")).strip()
        if origin_simple and origin_simple != "germline":
            stats["skip_non_germline"] += 1
            continue
        label = _classify_clinsig(str(row.get("ClinicalSignificance", "")))
        if label is None:
            stats["skip_non_binary_label"] += 1
            continue
        parsed = _parse_protein_change(str(row.get("Name", "")))
        if parsed is None:
            stats["skip_non_simple_missense"] += 1
            continue
        wt_aa, position_1_based, mut_aa = parsed
        position = position_1_based - 1
        if position < 0 or position >= len(sequence):
            stats["skip_out_of_range"] += 1
            continue
        if sequence[position].upper() != wt_aa:
            stats["skip_sequence_mismatch"] += 1
            continue
        key = (position, mut_aa)
        review_rank = REVIEW_STATUS_RANK.get(str(row.get("ReviewStatus", "")).strip().lower(), 0)
        candidate = {
            "gene": gene,
            "wt_aa": wt_aa,
            "position": position,
            "mut_aa": mut_aa,
            "label": int(label),
            "name": str(row["Name"]),
            "_review_rank": review_rank,
        }
        existing = selected.get(key)
        if existing is None or review_rank > int(existing["_review_rank"]):
            selected[key] = candidate

    rows = [
        {
            "gene": value["gene"],
            "wt_aa": value["wt_aa"],
            "position": int(value["position"]),
            "mut_aa": value["mut_aa"],
            "label": int(value["label"]),
            "name": value["name"],
        }
        for value in sorted(selected.values(), key=lambda item: (int(item["position"]), str(item["mut_aa"])))
    ]

    stats["n_total"] = len(rows)
    stats["n_positive"] = int(sum(int(row["label"]) for row in rows))
    stats["n_negative"] = int(len(rows) - stats["n_positive"])
    return rows, dict(stats)


def build_multigene_panel_manifest(
    paths: RejectRecoveryPaths,
    config: MultiGeneConfig | None = None,
) -> dict[str, Any]:
    config = config or MultiGeneConfig()
    manifest_path = paths.multigene / "panel_manifest.json"
    if manifest_path.exists() and not config.overwrite:
        return read_json(manifest_path)

    panel: dict[str, Any] = {
        "selected_genes": ["TP53", "BRCA1"],
        "genes": {},
        "candidate_stats": {},
        "selection_rule": {
            "candidate_genes": list(config.candidate_genes),
            "min_total": config.min_total,
            "min_per_class": config.min_per_class,
            "max_additional_genes": config.max_additional_genes,
        },
    }

    tp53_rows = list(load_tp53_variants())
    brca1_rows = list(load_brca1_full_filtered())
    tp53_rows_path = paths.multigene / "tp53_variants.json"
    brca1_rows_path = paths.multigene / "brca1_full_filtered_variants.json"
    _write_json(tp53_rows_path, tp53_rows)
    _write_json(brca1_rows_path, brca1_rows)
    panel["genes"]["TP53"] = {
        "variants_path": tp53_rows_path,
        "sequence_source": "local benchmark fasta",
        "sequence_path": paths.repo_root / "benchmarks" / "sequences" / "tp53.fasta",
        "n_total": len(tp53_rows),
        "n_positive": int(sum(int(row["label"]) for row in tp53_rows)),
        "n_negative": int(len(tp53_rows) - sum(int(row["label"]) for row in tp53_rows)),
    }
    panel["genes"]["BRCA1"] = {
        "variants_path": brca1_rows_path,
        "sequence_source": "local benchmark fasta",
        "sequence_path": paths.repo_root / "benchmarks" / "sequences" / "brca1.fasta",
        "n_total": len(brca1_rows),
        "n_positive": int(sum(int(row["label"]) for row in brca1_rows)),
        "n_negative": int(len(brca1_rows) - sum(int(row["label"]) for row in brca1_rows)),
    }

    summary_path = _download_clinvar_variant_summary(paths.cache)
    subset_rows = _load_clinvar_subset(summary_path, config.candidate_genes)
    rows_by_gene: dict[str, list[dict[str, str]]] = {gene: [] for gene in config.candidate_genes}
    for row in subset_rows:
        gene = str(row["GeneSymbol"]).upper()
        if gene in rows_by_gene:
            rows_by_gene[gene].append(row)

    selected_extra = 0
    for gene in config.candidate_genes:
        if selected_extra >= config.max_additional_genes:
            break
        sequence, fasta_path = _fetch_uniprot_sequence(gene, paths.cache / "uniprot")
        gene_rows, stats = _build_gene_rows_from_clinvar(gene, sequence, rows_by_gene.get(gene, []))
        stats["fasta_path"] = fasta_path
        if stats["n_total"] < config.min_total or stats["n_positive"] < config.min_per_class or stats["n_negative"] < config.min_per_class:
            stats["selected"] = False
            panel["candidate_stats"][gene] = stats
            continue
        gene_path = paths.multigene / f"{gene.lower()}_clinvar_variants.json"
        _write_json(gene_path, gene_rows)
        panel["genes"][gene] = {
            "variants_path": gene_path,
            "sequence_source": "UniProt reviewed human entry",
            "sequence_path": fasta_path,
            "n_total": stats["n_total"],
            "n_positive": stats["n_positive"],
            "n_negative": stats["n_negative"],
        }
        panel["candidate_stats"][gene] = {**stats, "selected": True}
        panel["selected_genes"].append(gene)
        selected_extra += 1

    _write_json(manifest_path, panel)
    _write_json(paths.configs / "multigene_panel_selection_config.json", asdict(config))
    _write_csv_rows(
        paths.multigene / "multigene_gene_table.csv",
        [
            {
                "gene": gene,
                "selected": bool(stats.get("selected", False)),
                "n_total": int(stats.get("n_total", 0)),
                "n_positive": int(stats.get("n_positive", 0)),
                "n_negative": int(stats.get("n_negative", 0)),
                "skip_sequence_mismatch": int(stats.get("skip_sequence_mismatch", 0)),
                "skip_non_binary_label": int(stats.get("skip_non_binary_label", 0)),
            }
            for gene, stats in panel["candidate_stats"].items()
        ],
    )
    return panel


def bootstrap_auc_ci(labels: list[int], scores: list[float], n_boot: int, seed: int) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    y_true = np.asarray(labels, dtype=int)
    values = np.asarray(scores, dtype=float)
    aucs: list[float] = []
    for _ in range(int(n_boot)):
        index = rng.integers(0, len(y_true), size=len(y_true))
        y_boot = y_true[index]
        if len(np.unique(y_boot)) < 2:
            continue
        aucs.append(float(_roc_auc_score(y_boot.tolist(), values[index].tolist())))
    if not aucs:
        raise RuntimeError("bootstrap produced no valid resamples")
    auc_array = np.asarray(aucs, dtype=float)
    return {
        "n_boot_requested": int(n_boot),
        "n_boot_valid": int(len(aucs)),
        "ci_2p5": float(np.quantile(auc_array, 0.025)),
        "ci_50": float(np.quantile(auc_array, 0.5)),
        "ci_97p5": float(np.quantile(auc_array, 0.975)),
    }


def paired_bootstrap_delta(labels: list[int], score_a: list[float], score_b: list[float], n_boot: int, seed: int) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    y_true = np.asarray(labels, dtype=int)
    a_values = np.asarray(score_a, dtype=float)
    b_values = np.asarray(score_b, dtype=float)
    deltas: list[float] = []
    for _ in range(int(n_boot)):
        index = rng.integers(0, len(y_true), size=len(y_true))
        y_boot = y_true[index]
        if len(np.unique(y_boot)) < 2:
            continue
        auc_a = _roc_auc_score(y_boot.tolist(), a_values[index].tolist())
        auc_b = _roc_auc_score(y_boot.tolist(), b_values[index].tolist())
        deltas.append(float(auc_a - auc_b))
    if not deltas:
        raise RuntimeError("paired bootstrap produced no valid resamples")
    delta_array = np.asarray(deltas, dtype=float)
    observed = float(_roc_auc_score(labels, score_a) - _roc_auc_score(labels, score_b))
    return {
        "observed_delta": observed,
        "n_boot_requested": int(n_boot),
        "n_boot_valid": int(len(deltas)),
        "ci_2p5": float(np.quantile(delta_array, 0.025)),
        "ci_50": float(np.quantile(delta_array, 0.5)),
        "ci_97p5": float(np.quantile(delta_array, 0.975)),
        "p_one_sided_pair_gt_baseline": float((np.sum(delta_array <= 0.0) + 1) / (len(delta_array) + 1)),
    }


def run_multigene_panel(
    paths: RejectRecoveryPaths,
    config: MultiGeneConfig | None = None,
    panel_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = config or MultiGeneConfig()
    panel_manifest = panel_manifest or build_multigene_panel_manifest(paths, config)
    summary_rows: list[dict[str, Any]] = []
    metrics_payload: dict[str, Any] = {"benchmark": "Supplementary multigene panel", "genes": {}}

    for gene in panel_manifest["selected_genes"]:
        gene_info = panel_manifest["genes"][gene]
        variants = read_json(Path(gene_info["variants_path"]))
        if gene == "TP53" and config.reuse_frozen_tp53_reference and config.model_name == MODEL_NAME:
            score_rows = [_typed_score_row({**row, "gene": "TP53", "model_name": config.model_name}) for row in load_tp53_scores()]
        else:
            if gene == "TP53":
                sequence = load_tp53_sequence()
            elif gene == "BRCA1":
                sequence = load_brca1_sequence()
            else:
                fasta_path = Path(gene_info["sequence_path"])
                lines = [line.strip() for line in fasta_path.read_text(encoding="utf-8").splitlines() if line.strip()]
                sequence = "".join(line for line in lines if not line.startswith(">"))
            gene_dir = paths.multigene / gene.lower()
            ensure_dir(gene_dir)
            score_rows = _ensure_gene_score_rows(
                gene=gene,
                sequence=sequence,
                variants=variants,
                model_name=config.model_name,
                output_dir=gene_dir,
                window_radius=config.window_radius,
                checkpoint_every=config.checkpoint_every,
                overwrite=config.overwrite,
            )

        summary = _score_rows_summary(score_rows, config.pair_alpha)
        bootstrap = bootstrap_auc_ci(_labels(score_rows), summary["normalized_scores"]["pair_score"], config.bootstrap_replicates, config.random_seed)
        paired = paired_bootstrap_delta(
            _labels(score_rows),
            summary["normalized_scores"]["pair_score"],
            summary["normalized_scores"]["ll_proper_norm"],
            config.bootstrap_replicates,
            config.random_seed,
        )
        gene_summary = {
            "gene": gene,
            "model_name": config.model_name,
            "window_radius": config.window_radius,
            "pair_alpha": config.pair_alpha,
            **{key: value for key, value in summary.items() if key != "normalized_scores"},
            "pair_auc_bootstrap": bootstrap,
            "pair_vs_ll_bootstrap_delta": paired,
        }
        metrics_payload["genes"][gene] = gene_summary
        summary_rows.append(
            {
                "gene": gene,
                "n_total": gene_summary["n_total"],
                "n_positive": gene_summary["n_positive"],
                "n_negative": gene_summary["n_negative"],
                "auc_ll_proper": gene_summary["auc_ll_proper"],
                "auc_frob_dist": gene_summary["auc_frob_dist"],
                "auc_trace_ratio": gene_summary["auc_trace_ratio"],
                "auc_sps_log": gene_summary["auc_sps_log"],
                "auc_pair_fixed_055": gene_summary["auc_pair_fixed_055"],
                "delta_pair_vs_ll": gene_summary["delta_pair_vs_ll"],
                "pair_ci_2p5": bootstrap["ci_2p5"],
                "pair_ci_97p5": bootstrap["ci_97p5"],
                "paired_delta_ci_2p5": paired["ci_2p5"],
                "paired_delta_ci_97p5": paired["ci_97p5"],
            }
        )
        _write_json(paths.multigene / gene.lower() / "summary.json", gene_summary)

    _write_csv_rows(paths.multigene / "multigene_summary.csv", summary_rows)
    _write_json(paths.multigene / "multigene_metrics.json", metrics_payload)
    _write_json(paths.configs / "multigene_config.json", asdict(config))

    if config.render_figures:
        _render_multigene_figures(paths.multigene, summary_rows)

    return metrics_payload


def write_experiment_log(
    paths: RejectRecoveryPaths,
    completed_experiments: list[str],
    skipped_experiments: list[str],
    notes: list[str],
    zip_path: Path | None = None,
) -> Path:
    lines = [
        "# SpectralBio Reject-Recovery Experiment Log",
        "",
        "## Completed experiments",
    ]
    lines.extend([f"- {item}" for item in completed_experiments] or ["- None"])
    lines.extend(["", "## Skipped experiments"])
    lines.extend([f"- {item}" for item in skipped_experiments] or ["- None"])
    lines.extend(["", "## Notes"])
    lines.extend([f"- {item}" for item in notes] or ["- None"])
    lines.extend(
        [
            "",
            "## Output paths",
            f"- Root: {paths.root}",
            f"- Leakage audit: {paths.leakage_audit}",
            f"- Backbone strength: {paths.backbone_strength}",
            f"- Multigene: {paths.multigene}",
            f"- Figures: {paths.figures}",
            f"- Tables: {paths.tables}",
            f"- Configs: {paths.configs}",
            f"- Logs: {paths.logs}",
            f"- Final bundle: {zip_path if zip_path else 'not created yet'}",
        ]
    )
    return write_text(paths.logs / "experiment_log.md", "\n".join(lines) + "\n")


def create_reject_recovery_zip(
    paths: RejectRecoveryPaths,
    bundle_name: str = "spectralbio_reject_recovery_bundle",
) -> Path:
    temp_base = paths.root.parent / bundle_name
    temp_zip = temp_base.with_suffix(".zip")
    final_zip = paths.final_bundle / f"{bundle_name}.zip"
    if temp_zip.exists():
        temp_zip.unlink()
    if final_zip.exists():
        final_zip.unlink()
    shutil.make_archive(str(temp_base), "zip", root_dir=paths.root)
    ensure_dir(final_zip.parent)
    shutil.move(str(temp_zip), str(final_zip))
    return final_zip


def _render_nested_cv_figures(output_dir: Path, fold_rows: list[dict[str, Any]], alpha_rows: list[dict[str, Any]]) -> None:
    import matplotlib.pyplot as plt

    alphas = [float(row["chosen_alpha"]) for row in alpha_rows]
    unique_alphas = sorted(set(alphas))
    counts = [alphas.count(alpha) for alpha in unique_alphas]
    plt.figure(figsize=(8, 4.5))
    plt.bar(unique_alphas, counts, width=0.04, color="#2f6f91")
    plt.xlabel("Chosen alpha")
    plt.ylabel("Outer-fold count")
    plt.title("TP53 nested CV chosen-alpha distribution")
    plt.tight_layout()
    plt.savefig(output_dir / "tp53_nested_cv_fig_alpha_hist.png", dpi=180, bbox_inches="tight")
    plt.close()

    labels = ["tuned alpha", "fixed 0.55", "fixed 0.50", "ll_proper", "frob_dist"]
    means = [
        float(np.mean([row["auc_tuned_alpha"] for row in fold_rows])),
        float(np.mean([row["auc_fixed_055"] for row in fold_rows])),
        float(np.mean([row["auc_fixed_050"] for row in fold_rows])),
        float(np.mean([row["auc_ll_proper"] for row in fold_rows])),
        float(np.mean([row["auc_frob_dist"] for row in fold_rows])),
    ]
    stds = [
        float(np.std([row["auc_tuned_alpha"] for row in fold_rows], ddof=0)),
        float(np.std([row["auc_fixed_055"] for row in fold_rows], ddof=0)),
        float(np.std([row["auc_fixed_050"] for row in fold_rows], ddof=0)),
        float(np.std([row["auc_ll_proper"] for row in fold_rows], ddof=0)),
        float(np.std([row["auc_frob_dist"] for row in fold_rows], ddof=0)),
    ]
    plt.figure(figsize=(9, 4.8))
    plt.bar(labels, means, yerr=stds, color=["#2f6f91", "#7dbd6d", "#9ecae1", "#dd8452", "#c44e52"])
    plt.ylabel("Out-of-fold ROC AUC")
    plt.title("TP53 nested CV AUC comparison")
    plt.ylim(0.45, 0.95)
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(output_dir / "tp53_nested_cv_fig_auc_comparison.png", dpi=180, bbox_inches="tight")
    plt.close()


def _render_backbone_figures(output_dir: Path, summary_rows: list[dict[str, Any]]) -> None:
    import matplotlib.pyplot as plt

    model_labels = [str(Path(row["model_name"]).name) for row in summary_rows]
    ll_values = [float(row["auc_ll_proper"]) for row in summary_rows]
    pair_values = [float(row["auc_pair_fixed_055"]) for row in summary_rows]
    delta_values = [float(row["delta_pair_vs_ll"]) for row in summary_rows]

    x = np.arange(len(model_labels))
    width = 0.35
    plt.figure(figsize=(8, 4.8))
    plt.bar(x - width / 2, ll_values, width=width, label="ll_proper", color="#dd8452")
    plt.bar(x + width / 2, pair_values, width=width, label="pair(0.55)", color="#2f6f91")
    plt.xticks(x, model_labels, rotation=15)
    plt.ylabel("ROC AUC")
    plt.title("TP53 backbone comparison")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "tp53_backbone_fig_auc.png", dpi=180, bbox_inches="tight")
    plt.close()

    plt.figure(figsize=(7, 4.5))
    plt.bar(model_labels, delta_values, color="#7dbd6d")
    plt.axhline(0.0, color="black", linewidth=1.0)
    plt.ylabel("Pair AUC - ll_proper AUC")
    plt.title("TP53 pair delta versus ll_proper")
    plt.tight_layout()
    plt.savefig(output_dir / "tp53_backbone_fig_delta_vs_ll.png", dpi=180, bbox_inches="tight")
    plt.close()


def _render_multigene_figures(output_dir: Path, summary_rows: list[dict[str, Any]]) -> None:
    import matplotlib.pyplot as plt

    genes = [str(row["gene"]) for row in summary_rows]
    ll_values = [float(row["auc_ll_proper"]) for row in summary_rows]
    pair_values = [float(row["auc_pair_fixed_055"]) for row in summary_rows]
    delta_values = [float(row["delta_pair_vs_ll"]) for row in summary_rows]

    x = np.arange(len(genes))
    width = 0.35
    plt.figure(figsize=(10, 4.8))
    plt.bar(x - width / 2, ll_values, width=width, label="ll_proper", color="#dd8452")
    plt.bar(x + width / 2, pair_values, width=width, label="pair(0.55)", color="#2f6f91")
    plt.xticks(x, genes, rotation=20)
    plt.ylabel("ROC AUC")
    plt.title("Supplementary multigene panel AUC by gene")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "multigene_fig_auc_by_gene.png", dpi=180, bbox_inches="tight")
    plt.close()

    plt.figure(figsize=(10, 4.5))
    plt.bar(genes, delta_values, color="#7dbd6d")
    plt.axhline(0.0, color="black", linewidth=1.0)
    plt.ylabel("Pair AUC - ll_proper AUC")
    plt.title("Supplementary multigene pair delta versus ll_proper")
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig(output_dir / "multigene_fig_delta_pair_vs_ll.png", dpi=180, bbox_inches="tight")
    plt.close()
