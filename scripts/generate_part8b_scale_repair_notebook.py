import json
from pathlib import Path


def md_cell(text: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line if line.endswith("\n") else f"{line}\n" for line in text.splitlines()],
    }


def code_cell(text: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line if line.endswith("\n") else f"{line}\n" for line in text.splitlines()],
    }


repo_root = Path(__file__).resolve().parents[1]
notebook_path = repo_root / "notebooks" / "final_accept_part8b_scale_repair_validation_H100.ipynb"

cells = [
    md_cell(
        """# Experiment: SpectralBio Scale-Repair Validation (H100)

This notebook is the one-shot follow-up to notebook 8.

## Why this notebook exists
- Notebook 7 already gave us a valid shortlist win: an interpretable disagreement regime that passed the T4 gate.
- Notebook 8 showed that the old persistence-style claim does **not** survive as a clean stronger-backbone failure mode.
- The stronger scientific win now is **scale repair**: the structured covariance-heavy disagreement seen in the 150M screen is reduced or reversed by a stronger backbone.

## What counts as victory here
- Do **not** focus on AUC as the primary gate.
- Show that the candidate regime is extreme in the 150M screen.
- Show that a stronger backbone shrinks or flips that candidate-vs-control gap.
- Show that this repair happens across a majority of candidate variants and across most genes with matched controls.

## Output contract
- Save everything only inside `notebooks/Results 7,8,9`.
- Write a zip bundle directly into that folder so it can be downloaded from the notebooks pane.
"""
    ),
    code_cell(
        """from pathlib import Path

print("This notebook writes outputs only under /notebooks.")
print("ACABEI PODE IR PARA O PRÓXIMO")
"""
    ),
    code_cell(
        """import os
import subprocess
import sys
from pathlib import Path

REPO_URL = os.environ.get("SPECTRALBIO_REPO_URL", "https://github.com/DaviBonetto/SpectralBio.git")
REPO_BRANCH = os.environ.get("SPECTRALBIO_REPO_BRANCH", "codex/claw4s-rebuild")
DEFAULT_REPO_ROOT = Path("/teamspace/studios/this_studio/Stanford-Claw4s")
FALLBACK_REPO_ROOT = Path("/content/Stanford-Claw4s")
ENV_REPO_ROOT = os.environ.get("SPECTRALBIO_REPO_ROOT", "").strip()


def _looks_like_repo(path: Path) -> bool:
    return (path / "src" / "spectralbio").exists() and (path / "notebooks").exists()


candidate_roots = []
if ENV_REPO_ROOT:
    candidate_roots.append(Path(ENV_REPO_ROOT).expanduser())
candidate_roots.extend([Path.cwd(), Path.cwd().parent, DEFAULT_REPO_ROOT, FALLBACK_REPO_ROOT])
REPO_ROOT = next((path.resolve() for path in candidate_roots if _looks_like_repo(path)), DEFAULT_REPO_ROOT)
BOOTSTRAP_MARKER = REPO_ROOT / ".colab_bootstrap_failure_mode_scale_repair_h100_complete"

if not _looks_like_repo(REPO_ROOT):
    REPO_ROOT.parent.mkdir(parents=True, exist_ok=True)
    subprocess.check_call(["git", "clone", "--branch", REPO_BRANCH, "--single-branch", REPO_URL, str(REPO_ROOT)])

os.chdir(REPO_ROOT)
subprocess.run(["git", "fetch", "origin", REPO_BRANCH], check=False)
subprocess.run(["git", "checkout", REPO_BRANCH], check=False)

src_path = REPO_ROOT / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

if not BOOTSTRAP_MARKER.exists():
    subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "torchvision"], check=False)
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", ".", "--no-deps"])
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "numpy==2.1.3",
            "pandas==2.2.3",
            "matplotlib==3.9.2",
            "scipy==1.14.1",
            "scikit-learn==1.5.2",
            "transformers==4.49.0",
            "accelerate>=1.0.0",
        ]
    )
    BOOTSTRAP_MARKER.write_text("ok\\n", encoding="utf-8")
    print("Dependencies installed without restarting the runtime.")
else:
    print("Bootstrap marker found; skipping reinstall.")

print("REPO_ROOT =", REPO_ROOT)
print("Python =", sys.version.split()[0])
print("ACABEI PODE IR PARA O PRÓXIMO")
"""
    ),
    md_cell(
        """## Plan

1. Load the canonical notebook 7 screen summary and the candidate validation pool.
2. Prefer existing notebook 8 validation rows if they already exist in `notebooks/Results 7,8,9`.
3. If needed, re-score the same pool on a configurable stronger backbone.
4. Validate **scale repair** using gap direction, per-variant repair rates, and gene-level flips.
5. Save tables, figures, narrative text, and a zip bundle only under `notebooks/Results 7,8,9`.
"""
    ),
    code_cell(
        """from __future__ import annotations

import json
import math
import os
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from spectralbio.constants import WINDOW_RADIUS
from spectralbio.utils.io import ensure_dir

OUTPUT_ROOT = REPO_ROOT / "notebooks" / "Results 7,8,9" / "failure_mode_scale_repair_bundle"
TABLES_DIR = OUTPUT_ROOT / "tables"
FIGURES_DIR = OUTPUT_ROOT / "figures"
SCORES_DIR = OUTPUT_ROOT / "scores"
TEXT_DIR = OUTPUT_ROOT / "text"

for directory in (OUTPUT_ROOT, TABLES_DIR, FIGURES_DIR, SCORES_DIR, TEXT_DIR):
    ensure_dir(directory)

DEFAULT_VALIDATION_MODEL = "facebook/esm2_t33_650M_UR50D"
VALIDATION_MODEL_NAME = os.environ.get("SPECTRALBIO_SCALE_REPAIR_MODEL", DEFAULT_VALIDATION_MODEL).strip() or DEFAULT_VALIDATION_MODEL
PREFER_EXISTING_PART8_ROWS = os.environ.get("SPECTRALBIO_REUSE_PART8_VALIDATION", "1").strip().lower() in {"1", "true", "yes", "y", "on"}
SCREEN_SUMMARY_PATH_OVERRIDE = os.environ.get("SPECTRALBIO_FAILURE_SCREEN_SUMMARY", "").strip()
OVERWRITE = os.environ.get("SPECTRALBIO_SCALE_REPAIR_OVERWRITE", "0").strip().lower() in {"1", "true", "yes", "y", "on"}
CHECKPOINT_EVERY = 1


def resolve_existing_path(raw: str | Path) -> Path:
    raw_path = Path(raw)
    if raw_path.exists():
        return raw_path
    raw_text = str(raw).replace("\\\\", "/")
    for prefix in (
        "/content/Stanford-Claw4s/",
        "/teamspace/studios/this_studio/Stanford-Claw4s/",
    ):
        if raw_text.startswith(prefix):
            candidate = REPO_ROOT / raw_text[len(prefix):]
            if candidate.exists():
                return candidate
    repo_marker = "Stanford-Claw4s/"
    if repo_marker in raw_text:
        candidate = REPO_ROOT / raw_text.split(repo_marker, 1)[1]
        if candidate.exists():
            return candidate
    if not raw_path.is_absolute():
        candidate = (REPO_ROOT / raw_path).resolve()
        if candidate.exists():
            return candidate
    return raw_path


def minmax_normalize(series: pd.Series) -> pd.Series:
    values = series.astype(float)
    minimum = float(values.min())
    maximum = float(values.max())
    if maximum <= minimum:
        return pd.Series(np.zeros(len(values), dtype=float), index=series.index)
    return (values - minimum) / (maximum - minimum)


def _ensure_gene_score_rows_lazy(**kwargs):
    try:
        from spectralbio.supplementary.reject_recovery import _ensure_gene_score_rows as _inner
    except Exception as exc:
        raise RuntimeError(
            "Could not import the stronger-backbone rescoring helper. "
            "Notebook 8b can still run from existing notebook 8 outputs on T4. "
            "If you expected a reuse-only run, confirm that "
            "failure_mode_validation_rows.csv from notebook 8 is available under notebooks/Results 7,8,9. "
            f"Original import error: {exc}"
        ) from exc
    return _inner(**kwargs)


print("validation model =", VALIDATION_MODEL_NAME)
print("PREFER_EXISTING_PART8_ROWS =", PREFER_EXISTING_PART8_ROWS)
print("output root =", OUTPUT_ROOT)
print("ACABEI PODE IR PARA O PRÓXIMO")
"""
    ),
    code_cell(
        """summary_candidates = []
if SCREEN_SUMMARY_PATH_OVERRIDE:
    summary_candidates.append(Path(SCREEN_SUMMARY_PATH_OVERRIDE))
summary_candidates.append(
    REPO_ROOT / "supplementary" / "failure_mode_screen_t4" / "failure_mode_screen" / "tables" / "candidate_failure_mode_summary.json"
)
summary_candidates.append(
    REPO_ROOT / "notebooks" / "Results 7,8,9" / "failure_mode_screen_bundle" / "tables" / "candidate_failure_mode_summary.json"
)
summary_candidates += sorted(REPO_ROOT.glob("supplementary/**/candidate_failure_mode_summary.json"))
summary_candidates += sorted(REPO_ROOT.glob("notebooks/**/candidate_failure_mode_summary.json"))

screen_summary_path = None
for candidate in summary_candidates:
    resolved = resolve_existing_path(candidate)
    if resolved.exists():
        screen_summary_path = resolved
        break
if screen_summary_path is None or not screen_summary_path.exists():
    raise FileNotFoundError("Could not find candidate_failure_mode_summary.json. Run notebook 7 first and keep its outputs available.")

screen_summary = json.loads(screen_summary_path.read_text(encoding="utf-8"))
validation_pool_path = screen_summary_path.parent / "candidate_validation_pool.csv"
validation_pool = pd.read_csv(validation_pool_path)
selected_regime = str(screen_summary["selected_regime"])
ready_for_h100 = bool(screen_summary.get("ready_for_h100", False))

existing_validation_rows_candidates = [
    REPO_ROOT / "notebooks" / "Results 7,8,9" / "failure_mode_validation_bundle" / "tables" / "failure_mode_validation_rows.csv",
    REPO_ROOT / "notebooks" / "failure_mode_validation_bundle" / "tables" / "failure_mode_validation_rows.csv",
    REPO_ROOT / "supplementary" / "failure_mode_validation_h100" / "failure_mode_validation" / "tables" / "failure_mode_validation_rows.csv",
]
existing_validation_rows_path = None
for candidate in existing_validation_rows_candidates:
    resolved = resolve_existing_path(candidate)
    if resolved.exists():
        existing_validation_rows_path = resolved
        break

reuse_existing_rows = bool(
    PREFER_EXISTING_PART8_ROWS
    and VALIDATION_MODEL_NAME == DEFAULT_VALIDATION_MODEL
    and existing_validation_rows_path is not None
)

print("screen summary =", screen_summary_path)
print("selected_regime =", selected_regime)
print("ready_for_h100 =", ready_for_h100)
print("validation_pool roles =", validation_pool["validation_role"].value_counts().to_dict())
print("existing_validation_rows_path =", existing_validation_rows_path)
print("reuse_existing_rows =", reuse_existing_rows)
print("ACABEI PODE IR PARA O PRÓXIMO")
"""
    ),
    code_cell(
        """validation_df = None
used_existing_validation_rows = False
rescored_now = False
score_source_note = None

required_existing_columns = {"ll_norm_650m", "frob_norm_650m", "pair_norm_650m"}

if reuse_existing_rows:
    existing_validation_df = pd.read_csv(existing_validation_rows_path)
    if required_existing_columns.issubset(existing_validation_df.columns):
        validation_df = existing_validation_df.copy()
        validation_df["ll_norm_strong"] = validation_df["ll_norm_650m"].astype(float)
        validation_df["frob_norm_strong"] = validation_df["frob_norm_650m"].astype(float)
        validation_df["pair_norm_strong"] = validation_df["pair_norm_650m"].astype(float)
        validation_df["strong_model_name"] = VALIDATION_MODEL_NAME
        used_existing_validation_rows = True
        score_source_note = f"Reused existing notebook 8 validation rows from {existing_validation_rows_path}"

        existing_scores_root = existing_validation_rows_path.parent.parent / "scores"
        if existing_scores_root.exists():
            shutil.copytree(existing_scores_root, SCORES_DIR, dirs_exist_ok=True)
    else:
        print("Existing validation rows found, but the stronger-backbone columns are missing. Falling back to re-score.")

if validation_df is None:
    from spectralbio.data.sequences import load_gene_sequence

    rescored_frames = []
    for gene, gene_pool in validation_pool.groupby("gene", sort=True):
        sequence = load_gene_sequence(str(gene).upper())
        variant_rows = gene_pool[["gene", "name", "position", "wt_aa", "mut_aa", "label"]].to_dict("records")
        score_rows = _ensure_gene_score_rows_lazy(
            gene=str(gene).upper(),
            sequence=sequence,
            variants=variant_rows,
            model_name=VALIDATION_MODEL_NAME,
            output_dir=SCORES_DIR / str(gene).lower(),
            window_radius=WINDOW_RADIUS,
            checkpoint_every=CHECKPOINT_EVERY,
            overwrite=OVERWRITE,
        )
        frame = pd.DataFrame(score_rows)
        frame["gene"] = frame["gene"].str.upper()
        frame = frame.merge(
            gene_pool,
            on=["gene", "name", "position", "wt_aa", "mut_aa", "label"],
            how="left",
        )
        rescored_frames.append(frame)

    validation_df = pd.concat(rescored_frames, ignore_index=True)
    validation_df["ll_norm_strong"] = validation_df.groupby("gene")["ll_proper"].transform(minmax_normalize)
    validation_df["frob_norm_strong"] = validation_df.groupby("gene")["frob_dist"].transform(minmax_normalize)
    validation_df["pair_norm_strong"] = (0.55 * validation_df["frob_norm_strong"]) + (0.45 * validation_df["ll_norm_strong"])
    validation_df["strong_model_name"] = VALIDATION_MODEL_NAME
    rescored_now = True
    score_source_note = f"Re-scored validation pool on {VALIDATION_MODEL_NAME}"

print("used_existing_validation_rows =", used_existing_validation_rows)
print("rescored_now =", rescored_now)
print("score_source_note =", score_source_note)
print("validation_df shape =", validation_df.shape)
print("ACABEI PODE IR PARA O PRÓXIMO")
"""
    ),
    code_cell(
        """candidate_mask = validation_df["validation_role"].isin(["candidate_positive_existing_aug", "candidate_positive_reference_extension"])
control_mask = validation_df["validation_role"].eq("matched_positive_control")
benign_mask = validation_df["validation_role"].eq("regime_benign")

candidate_group = validation_df[candidate_mask].copy()
control_group = validation_df[control_mask].copy()
benign_group = validation_df[benign_mask].copy()


def mean_or_zero(series: pd.Series) -> float:
    return float(series.astype(float).mean()) if not series.empty else 0.0


screen_gap_frob = mean_or_zero(candidate_group["frob_norm"]) - mean_or_zero(control_group["frob_norm"])
screen_gap_pair = mean_or_zero(candidate_group["pair_norm"]) - mean_or_zero(control_group["pair_norm"])
strong_gap_frob = mean_or_zero(candidate_group["frob_norm_strong"]) - mean_or_zero(control_group["frob_norm_strong"])
strong_gap_pair = mean_or_zero(candidate_group["pair_norm_strong"]) - mean_or_zero(control_group["pair_norm_strong"])
gap_reduction_frob = float(screen_gap_frob - strong_gap_frob)
gap_reduction_pair = float(screen_gap_pair - strong_gap_pair)

candidate_variant_repair_rate_frob = float((candidate_group["frob_norm_strong"].astype(float) < candidate_group["frob_norm"].astype(float)).mean()) if not candidate_group.empty else 0.0
candidate_variant_repair_rate_pair = float((candidate_group["pair_norm_strong"].astype(float) < candidate_group["pair_norm"].astype(float)).mean()) if not candidate_group.empty else 0.0
candidate_variant_repair_rate_ll = float((candidate_group["ll_norm_strong"].astype(float) < candidate_group["ll_norm"].astype(float)).mean()) if not candidate_group.empty else 0.0

gene_rows = []
common_genes = sorted(set(candidate_group["gene"].astype(str).unique()) & set(control_group["gene"].astype(str).unique()))
for gene in common_genes:
    gene_candidates = candidate_group[candidate_group["gene"].astype(str) == gene].copy()
    gene_controls = control_group[control_group["gene"].astype(str) == gene].copy()
    gap_150m_frob = mean_or_zero(gene_candidates["frob_norm"]) - mean_or_zero(gene_controls["frob_norm"])
    gap_strong_frob = mean_or_zero(gene_candidates["frob_norm_strong"]) - mean_or_zero(gene_controls["frob_norm_strong"])
    gap_150m_pair = mean_or_zero(gene_candidates["pair_norm"]) - mean_or_zero(gene_controls["pair_norm"])
    gap_strong_pair = mean_or_zero(gene_candidates["pair_norm_strong"]) - mean_or_zero(gene_controls["pair_norm_strong"])

    if gap_150m_frob > 0 and gap_strong_frob <= 0:
        frob_status = "flip_to_nonpositive"
    elif gap_150m_frob > 0 and gap_strong_frob < gap_150m_frob:
        frob_status = "positive_reduced"
    elif gap_150m_frob <= 0 and gap_strong_frob <= 0:
        frob_status = "already_nonpositive"
    elif gap_strong_frob > gap_150m_frob:
        frob_status = "worsened"
    else:
        frob_status = "mixed"

    gene_rows.append(
        {
            "gene": gene,
            "n_candidate": int(gene_candidates.shape[0]),
            "n_control": int(gene_controls.shape[0]),
            "gap_150m_frob": float(gap_150m_frob),
            "gap_strong_frob": float(gap_strong_frob),
            "gap_150m_pair": float(gap_150m_pair),
            "gap_strong_pair": float(gap_strong_pair),
            "frob_status": frob_status,
        }
    )

gene_summary_df = pd.DataFrame(gene_rows)
positive_gap_genes = gene_summary_df[gene_summary_df["gap_150m_frob"] > 0].copy()
positive_gap_gene_count = int(positive_gap_genes.shape[0])
flip_to_nonpositive_gene_count = int((positive_gap_genes["gap_strong_frob"] <= 0).sum()) if not positive_gap_genes.empty else 0
positive_gap_flip_rate = float(flip_to_nonpositive_gene_count / positive_gap_gene_count) if positive_gap_gene_count else 0.0
positive_gap_reduced_rate = float((positive_gap_genes["gap_strong_frob"] < positive_gap_genes["gap_150m_frob"]).mean()) if not positive_gap_genes.empty else 0.0

reference_advantage_candidate_mean = mean_or_zero(candidate_group["reference_advantage"])
reference_advantage_control_mean = mean_or_zero(control_group["reference_advantage"])

screen_signal_present = bool(ready_for_h100 and screen_gap_frob >= 0.10 and screen_gap_pair >= 0.08 and positive_gap_gene_count >= 5)
repair_direction_confirmed = bool(strong_gap_frob <= 0.0 and strong_gap_pair <= 0.0 and gap_reduction_frob >= 0.25 and gap_reduction_pair >= 0.20)
variant_repair_confirmed = bool(candidate_variant_repair_rate_frob >= 0.65 and candidate_variant_repair_rate_pair >= 0.65)
gene_repair_confirmed = bool(positive_gap_flip_rate >= 0.70 and flip_to_nonpositive_gene_count >= 4)

scale_repair_validated = bool(
    screen_signal_present
    and repair_direction_confirmed
    and variant_repair_confirmed
    and gene_repair_confirmed
)

if scale_repair_validated:
    decision_reason = "Scale repair validated: the candidate-vs-control covariance gap seen in the 150M screen shrinks or flips under the stronger backbone across most genes and most candidate variants."
else:
    decision_reason = "Scale repair not strong enough on the current thresholds."

summary_payload = {
    "selected_regime": selected_regime,
    "scale_repair_validated": bool(scale_repair_validated),
    "ready_for_h100": bool(ready_for_h100),
    "used_existing_validation_rows": bool(used_existing_validation_rows),
    "executed_heavy_stage": bool(rescored_now),
    "validation_model_name": VALIDATION_MODEL_NAME,
    "score_source_note": score_source_note,
    "reason": decision_reason,
    "role_counts": {
        role: int(count)
        for role, count in validation_df["validation_role"].value_counts().to_dict().items()
    },
    "screen_signal": {
        "candidate_control_gap_frob_150m": float(screen_gap_frob),
        "candidate_control_gap_pair_150m": float(screen_gap_pair),
        "positive_gap_gene_count": int(positive_gap_gene_count),
        "reference_advantage_candidate_mean": float(reference_advantage_candidate_mean),
        "reference_advantage_control_mean": float(reference_advantage_control_mean),
    },
    "repair_signal": {
        "candidate_control_gap_frob_strong": float(strong_gap_frob),
        "candidate_control_gap_pair_strong": float(strong_gap_pair),
        "gap_reduction_frob": float(gap_reduction_frob),
        "gap_reduction_pair": float(gap_reduction_pair),
        "candidate_variant_repair_rate_frob": float(candidate_variant_repair_rate_frob),
        "candidate_variant_repair_rate_pair": float(candidate_variant_repair_rate_pair),
        "candidate_variant_repair_rate_ll": float(candidate_variant_repair_rate_ll),
        "flip_to_nonpositive_gene_count": int(flip_to_nonpositive_gene_count),
        "positive_gap_flip_rate": float(positive_gap_flip_rate),
        "positive_gap_reduced_rate": float(positive_gap_reduced_rate),
    },
}

validation_df["frob_repair_delta"] = validation_df["frob_norm_strong"].astype(float) - validation_df["frob_norm"].astype(float)
validation_df["pair_repair_delta"] = validation_df["pair_norm_strong"].astype(float) - validation_df["pair_norm"].astype(float)
validation_df["ll_repair_delta"] = validation_df["ll_norm_strong"].astype(float) - validation_df["ll_norm"].astype(float)

scale_repair_examples = (
    validation_df[candidate_mask]
    .sort_values(["frob_repair_delta", "pair_repair_delta", "gene", "name"], ascending=[True, True, True, True])
    [
        [
            "gene",
            "name",
            "validation_role",
            "label",
            "frob_norm",
            "frob_norm_strong",
            "frob_repair_delta",
            "pair_norm",
            "pair_norm_strong",
            "pair_repair_delta",
            "ll_norm",
            "ll_norm_strong",
            "ll_repair_delta",
            "reference_advantage",
            "rescue_margin",
        ]
    ]
    .reset_index(drop=True)
)

(TABLES_DIR / "failure_mode_scale_repair_summary.json").write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")
gene_summary_df.to_csv(TABLES_DIR / "failure_mode_scale_repair_gene_summary.csv", index=False)
scale_repair_examples.to_csv(TABLES_DIR / "failure_mode_scale_repair_examples.csv", index=False)
validation_df.to_csv(TABLES_DIR / "failure_mode_scale_repair_rows.csv", index=False)

print(json.dumps(summary_payload, indent=2))
print("ACABEI PODE IR PARA O PRÓXIMO")
"""
    ),
    code_cell(
        """if gene_summary_df.empty:
    raise RuntimeError("No genes with both candidate and matched control rows were found, so no scale-repair figure can be drawn.")

plot_df = gene_summary_df.sort_values("gap_150m_frob", ascending=False).reset_index(drop=True)
x = np.arange(len(plot_df))
width = 0.35

fig, ax = plt.subplots(figsize=(12, 5))
ax.bar(x - (width / 2), plot_df["gap_150m_frob"], width=width, label="150M gap", color="#c97b24")
ax.bar(x + (width / 2), plot_df["gap_strong_frob"], width=width, label="Stronger-backbone gap", color="#2455a4")
ax.axhline(0.0, color="black", linewidth=1.0, alpha=0.7)
ax.set_xticks(x)
ax.set_xticklabels(plot_df["gene"], rotation=45, ha="right")
ax.set_ylabel("Candidate minus control mean frob gap")
ax.set_title("Scale Repair by Gene")
ax.legend()
fig.tight_layout()
fig.savefig(FIGURES_DIR / "failure_mode_scale_repair_by_gene.png", dpi=180, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(6, 6))
ax.scatter(candidate_group["frob_norm"], candidate_group["frob_norm_strong"], color="#b33b2e", alpha=0.85, label="Candidates")
ax.scatter(control_group["frob_norm"], control_group["frob_norm_strong"], color="#2455a4", alpha=0.80, label="Matched controls")
ax.plot([0, 1], [0, 1], linestyle="--", color="black", linewidth=1.0, alpha=0.6)
ax.set_xlabel("150M frob_norm")
ax.set_ylabel("Stronger-backbone frob_norm")
ax.set_title("Variant-Level Scale Repair")
ax.legend()
fig.tight_layout()
fig.savefig(FIGURES_DIR / "failure_mode_scale_repair_scatter.png", dpi=180, bbox_inches="tight")
plt.close(fig)

readout_md = f\"\"\"# Scale Repair Readout

Selected regime: `{selected_regime}`

Scale-repair validated: `{scale_repair_validated}`

Reason:
{decision_reason}

Key numbers:
- 150M candidate-control frob gap: `{screen_gap_frob:.4f}`
- Stronger-backbone candidate-control frob gap: `{strong_gap_frob:.4f}`
- 150M candidate-control pair gap: `{screen_gap_pair:.4f}`
- Stronger-backbone candidate-control pair gap: `{strong_gap_pair:.4f}`
- Frob gap reduction: `{gap_reduction_frob:.4f}`
- Pair gap reduction: `{gap_reduction_pair:.4f}`
- Candidate variant frob repair rate: `{candidate_variant_repair_rate_frob:.4f}`
- Candidate variant pair repair rate: `{candidate_variant_repair_rate_pair:.4f}`
- Positive-gap gene flip rate: `{positive_gap_flip_rate:.4f}`
\"\"\"
(TEXT_DIR / "failure_mode_scale_repair_readout.md").write_text(readout_md, encoding="utf-8")

print("Figures and narrative saved under", OUTPUT_ROOT)
print("ACABEI PODE IR PARA O PRÓXIMO")
"""
    ),
    code_cell(
        """ZIP_PATH = Path(
    shutil.make_archive(
        str(OUTPUT_ROOT),
        "zip",
        root_dir=OUTPUT_ROOT.parent,
        base_dir=OUTPUT_ROOT.name,
    )
)

print("Bundle written to", ZIP_PATH)
print("Results folder =", OUTPUT_ROOT)
print("ZIP ready in notebooks pane =", ZIP_PATH)
try:
    from google.colab import files as colab_files

    colab_files.download(str(ZIP_PATH))
    print("Auto-download triggered.")
except Exception as exc:
    print(f"Auto-download was not triggered: {exc}")
print("ACABEI PODE IR PARA O PRÓXIMO")
"""
    ),
]


notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "version": "3.12",
        },
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

notebook_path.write_text(json.dumps(notebook, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(notebook_path)
