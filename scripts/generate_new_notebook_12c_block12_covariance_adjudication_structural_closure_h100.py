from __future__ import annotations

import json
import textwrap
from pathlib import Path


def markdown_cell(source: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source.splitlines(keepends=True),
    }


def code_cell(source: str) -> dict:
    normalized = source.rstrip()
    lines = normalized.splitlines()
    last_non_empty = next((line.strip() for line in reversed(lines) if line.strip()), "")
    if last_non_empty != 'print("TERMINEI PODE SEGUIR")':
        normalized = f'{normalized}\n\nprint("TERMINEI PODE SEGUIR")'
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": (normalized + "\n").splitlines(keepends=True),
    }


def dedent(source: str) -> str:
    return textwrap.dedent(source).lstrip("\n")


def build_notebook() -> dict:
    cells: list[dict] = [
        markdown_cell(
            "# Experiment: SpectralBio Block 12C - Covariance Adjudication And Structural Closure (H100)\n\n"
            "Objective:\n"
            "- Reuse the broad multifamily signal from **Block 12B**, but now adjudicate the claim under a stricter courtroom contract.\n"
            "- Close the **structural layer** using the real strict/broad Block 07B/07C references instead of allowing an empty fallback.\n"
            "- Replace the weak non-TP53 mini panel with a **balanced BRCA1 transfer arm** that can actually separate positive and negative variants.\n"
            "- Promote only a **covariance-native nuclear set** into the primary claim; models that win only through scalar rescue become supportive evidence, not the headline.\n"
            "- Produce a reviewer-facing closure package under `New Notebooks/results/12c_block12_covariance_adjudication_structural_closure_h100/`.\n"
        ),
        markdown_cell(
            "## Adjudication Contract\n\n"
            "- Block 12B already showed that the signal is broader than one checkpoint. Block 12C asks the harder question: **does a covariance-native rule still stand once structural closure, matched scalar controls, and a balanced transfer arm are all enforced together?**\n"
            "- This notebook is deliberately asymmetric:\n"
            "  1. it **reuses** TP53 live scoring from Block 12B,\n"
            "  2. it **reruns only what stayed weak**,\n"
            "  3. it distinguishes a **nuclear set** from a merely supportive set.\n"
            "- Promotion to a stronger claim requires a covariance-native win that survives: coverage floors, scalar-matched controls, same-position adjudication, structural alignment, and non-TP53 transfer.\n"
        ),
        code_cell(
            dedent(
                """
                # Setup: imports, runtime requirements, notebook identifiers, and the adjudication roster
                from __future__ import annotations

                import importlib
                import json
                import math
                import os
                import platform
                import random
                import subprocess
                import sys
                import time
                import zipfile
                from importlib import metadata as importlib_metadata
                from datetime import datetime, timezone
                from pathlib import Path

                from IPython.display import display

                NOTEBOOK_SLUG = '12c_block12_covariance_adjudication_structural_closure_h100'
                BLOCK12B_SLUG = '12b_block12_multifamily_coverage_aware_generalization_h100'
                ACCOUNT_LABEL = os.environ.get('SPECTRALBIO_ACCOUNT_LABEL', 'local_run')
                RUN_AT = datetime.now(timezone.utc).isoformat()
                OVERWRITE = os.environ.get('SPECTRALBIO_OVERWRITE', '').strip().lower() in {'1', 'true', 'yes'}
                RERUN_BRCA1 = os.environ.get('SPECTRALBIO_BLOCK12C_RERUN_BRCA1', '1').strip().lower() in {'1', 'true', 'yes'}
                INCLUDE_ANKH = os.environ.get('SPECTRALBIO_BLOCK12C_INCLUDE_ANKH', '').strip().lower() in {'1', 'true', 'yes'}
                WINDOW_RADIUS = int(os.environ.get('SPECTRALBIO_BLOCK12C_WINDOW_RADIUS', '40'))
                CHECKPOINT_EVERY = int(os.environ.get('SPECTRALBIO_BLOCK12C_CHECKPOINT_EVERY', '10'))
                FIXED_ALPHA = float(os.environ.get('SPECTRALBIO_BLOCK12C_FIXED_ALPHA', '0.55'))
                BOOTSTRAP_REPLICATES = int(os.environ.get('SPECTRALBIO_BLOCK12C_BOOTSTRAP_REPLICATES', '2000'))
                RANDOM_REPLICATES = int(os.environ.get('SPECTRALBIO_BLOCK12C_RANDOM_REPLICATES', '500'))
                RANDOM_SEED = int(os.environ.get('SPECTRALBIO_BLOCK12C_RANDOM_SEED', '42'))
                MIN_RULE_ON_ABS = int(os.environ.get('SPECTRALBIO_BLOCK12C_MIN_RULE_ON_ABS', '10'))
                MIN_RULE_ON_FRAC = float(os.environ.get('SPECTRALBIO_BLOCK12C_MIN_RULE_ON_FRAC', '0.05'))
                MODEL_FILTER = {
                    item.strip().lower()
                    for item in os.environ.get('SPECTRALBIO_BLOCK12C_MODEL_FILTER', '').split(',')
                    if item.strip()
                }

                MODEL_SPECS = [
                    {
                        'model_name': 'facebook/esm2_t12_35M_UR50D',
                        'model_label': 'ESM2-35M',
                        'family_label': 'esm',
                        'architecture_kind': 'masked_encoder',
                        'adapter_kind': 'esm',
                        'sequence_mode': 'raw',
                        'scale_bucket': '35M',
                    },
                    {
                        'model_name': 'facebook/esm2_t30_150M_UR50D',
                        'model_label': 'ESM2-150M',
                        'family_label': 'esm',
                        'architecture_kind': 'masked_encoder',
                        'adapter_kind': 'esm',
                        'sequence_mode': 'raw',
                        'scale_bucket': '150M',
                    },
                    {
                        'model_name': 'facebook/esm2_t33_650M_UR50D',
                        'model_label': 'ESM2-650M',
                        'family_label': 'esm',
                        'architecture_kind': 'masked_encoder',
                        'adapter_kind': 'esm',
                        'sequence_mode': 'raw',
                        'scale_bucket': '650M',
                    },
                    {
                        'model_name': 'facebook/esm2_t36_3B_UR50D',
                        'model_label': 'ESM2-3B',
                        'family_label': 'esm',
                        'architecture_kind': 'masked_encoder',
                        'adapter_kind': 'esm',
                        'sequence_mode': 'raw',
                        'scale_bucket': '3B',
                    },
                    {
                        'model_name': 'facebook/esm1v_t33_650M_UR90S_1',
                        'model_label': 'ESM-1v',
                        'family_label': 'esm_variant_specialist',
                        'architecture_kind': 'masked_encoder',
                        'adapter_kind': 'esm',
                        'sequence_mode': 'raw',
                        'scale_bucket': '650M',
                    },
                    {
                        'model_name': 'Rostlab/prot_t5_xl_half_uniref50-enc',
                        'model_label': 'ProtT5',
                        'family_label': 'prottrans',
                        'architecture_kind': 'encoder_decoder',
                        'adapter_kind': 't5',
                        'sequence_mode': 'spaced',
                        'scale_bucket': 'xl',
                    },
                    {
                        'model_name': 'Rostlab/prot_bert',
                        'model_label': 'ProtBERT',
                        'family_label': 'bert_style',
                        'architecture_kind': 'bidirectional_encoder',
                        'adapter_kind': 'auto',
                        'sequence_mode': 'spaced',
                        'scale_bucket': 'base',
                    },
                    {
                        'model_name': 'Rostlab/prot_bert_bfd',
                        'model_label': 'ProtBERT-BFD',
                        'family_label': 'bert_style',
                        'architecture_kind': 'bidirectional_encoder',
                        'adapter_kind': 'auto',
                        'sequence_mode': 'spaced',
                        'scale_bucket': 'bfd',
                    },
                    {
                        'model_name': 'hugohrban/progen2-small',
                        'model_label': 'ProGen2-small',
                        'family_label': 'progen',
                        'architecture_kind': 'causal_decoder',
                        'adapter_kind': 'causal',
                        'sequence_mode': 'raw',
                        'scale_bucket': 'small',
                    },
                    {
                        'model_name': 'hugohrban/progen2-base',
                        'model_label': 'ProGen2-base',
                        'family_label': 'progen',
                        'architecture_kind': 'causal_decoder',
                        'adapter_kind': 'causal',
                        'sequence_mode': 'raw',
                        'scale_bucket': 'base',
                    },
                ]

                if INCLUDE_ANKH:
                    MODEL_SPECS.extend([
                        {
                            'model_name': 'ElnaggarLab/ankh-base',
                            'model_label': 'Ankh-base',
                            'family_label': 'ankh',
                            'architecture_kind': 'encoder_decoder',
                            'adapter_kind': 'auto',
                            'sequence_mode': 'spaced',
                            'scale_bucket': 'base',
                        },
                        {
                            'model_name': 'ElnaggarLab/ankh-large',
                            'model_label': 'Ankh-large',
                            'family_label': 'ankh',
                            'architecture_kind': 'encoder_decoder',
                            'adapter_kind': 'auto',
                            'sequence_mode': 'spaced',
                            'scale_bucket': 'large',
                        },
                    ])

                if MODEL_FILTER:
                    MODEL_SPECS = [
                        spec
                        for spec in MODEL_SPECS
                        if spec['model_label'].strip().lower() in MODEL_FILTER
                        or spec['family_label'].strip().lower() in MODEL_FILTER
                    ]

                def done(message: str) -> None:
                    print(message)
                    print('TERMINEI PODE SEGUIR')

                try:
                    from packaging.requirements import Requirement as _Requirement
                except Exception:
                    subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'packaging>=24.0'], check=True, text=True)
                    from packaging.requirements import Requirement as _Requirement

                TORCH_SPEC = 'torch>=2.5,<3'
                runtime_requirements = [
                    ('packaging', 'packaging>=24.0', 'packaging'),
                    ('numpy', 'numpy==2.1.3', 'numpy'),
                    ('pandas', 'pandas>=2.2.0', 'pandas'),
                    ('matplotlib', 'matplotlib>=3.9.0', 'matplotlib'),
                    ('sklearn', 'scikit-learn==1.5.2', 'sklearn'),
                    ('scipy', 'scipy==1.14.1', 'scipy'),
                    ('requests', 'requests>=2.32.0', 'requests'),
                    ('torch', TORCH_SPEC, 'torch'),
                    ('transformers', 'transformers==4.49.0', 'transformers'),
                    ('accelerate', 'accelerate>=1.0.0', 'accelerate'),
                    ('sentencepiece', 'sentencepiece>=0.2.0', 'sentencepiece'),
                    ('safetensors', 'safetensors>=0.4.0', 'safetensors'),
                    ('protobuf', 'protobuf>=5.0.0', 'google.protobuf'),
                    ('einops', 'einops>=0.8.0', 'einops'),
                ]

                def parse_requirement(spec: str):
                    requirement = _Requirement(spec)
                    return requirement.name, requirement.specifier

                def installed_version_for(requirement_spec: str) -> str | None:
                    package_name, _ = parse_requirement(requirement_spec)
                    try:
                        return importlib_metadata.version(package_name)
                    except importlib_metadata.PackageNotFoundError:
                        return None

                def requirement_satisfied(requirement_spec: str) -> bool:
                    version = installed_version_for(requirement_spec)
                    if version is None:
                        return False
                    _, specifier = parse_requirement(requirement_spec)
                    return True if not specifier else version in specifier

                install_specs: list[str] = []
                runtime_rows = []
                for module_name, package_spec, import_target in runtime_requirements:
                    satisfied = requirement_satisfied(package_spec)
                    runtime_rows.append({
                        'module': module_name,
                        'package_spec': package_spec,
                        'status': 'present' if satisfied else 'install_required',
                        'version': installed_version_for(package_spec) or 'missing',
                    })
                    if not satisfied:
                        install_specs.append(package_spec)

                if install_specs:
                    subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', *install_specs], check=True, text=True)
                    importlib.invalidate_caches()
                    runtime_rows = []
                    for module_name, package_spec, import_target in runtime_requirements:
                        module = importlib.import_module(import_target)
                        runtime_rows.append({
                            'module': module_name,
                            'package_spec': package_spec,
                            'status': 'installed_now',
                            'version': str(getattr(module, '__version__', 'present')),
                        })

                print({
                    'notebook_slug': NOTEBOOK_SLUG,
                    'block12b_slug': BLOCK12B_SLUG,
                    'account_label': ACCOUNT_LABEL,
                    'rerun_brca1': RERUN_BRCA1,
                    'include_ankh': INCLUDE_ANKH,
                    'window_radius': WINDOW_RADIUS,
                    'checkpoint_every': CHECKPOINT_EVERY,
                    'fixed_alpha': FIXED_ALPHA,
                    'python': sys.version.split()[0],
                    'platform': platform.platform(),
                    'runtime': runtime_rows,
                    'models': [spec['model_label'] for spec in MODEL_SPECS],
                })
                done('Environment prepared for Block 12C adjudication and structural closure.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Helpers: repo discovery, statistics, structural closure, sequence validation, and optional live scoring
                import json
                import math
                import random
                import sys
                from pathlib import Path

                import matplotlib.pyplot as plt
                import numpy as np
                import pandas as pd
                import torch
                from scipy import stats
                from sklearn.metrics import roc_auc_score
                from transformers import AutoModel, AutoModelForMaskedLM, AutoModelForSeq2SeqLM, AutoTokenizer

                def ensure_dir(path: Path) -> Path:
                    path.mkdir(parents=True, exist_ok=True)
                    return path

                def looks_like_repo(path: Path) -> bool:
                    return (path / 'src' / 'spectralbio').exists() and (path / 'New Notebooks').exists()

                def find_repo_root() -> Path:
                    env_repo = os.environ.get('SPECTRALBIO_REPO_ROOT', '').strip()
                    candidates: list[Path] = []
                    if env_repo:
                        candidates.append(Path(env_repo).expanduser())
                    cwd = Path.cwd().resolve()
                    candidates.extend([
                        cwd,
                        cwd.parent,
                        Path('/teamspace/studios/this_studio/Stanford-Claw4s'),
                        Path('/teamspace/studios/this_studio/SpectralBio'),
                        Path('/content/Stanford-Claw4s'),
                    ])
                    for candidate in candidates:
                        if looks_like_repo(candidate):
                            return candidate.resolve()
                    raise FileNotFoundError('Could not locate repo root. Set SPECTRALBIO_REPO_ROOT.')

                REPO_ROOT = find_repo_root()
                SRC_ROOT = REPO_ROOT / 'src'
                if str(SRC_ROOT) not in sys.path:
                    sys.path.insert(0, str(SRC_ROOT))

                from spectralbio.supplementary.reject_recovery import _ensure_gene_score_rows

                RESULTS_DIR = REPO_ROOT / 'New Notebooks' / 'results'
                RESULTS_ROOT = ensure_dir(RESULTS_DIR / NOTEBOOK_SLUG)
                TABLES_DIR = ensure_dir(RESULTS_ROOT / 'tables')
                FIGURES_DIR = ensure_dir(RESULTS_ROOT / 'figures')
                TEXT_DIR = ensure_dir(RESULTS_ROOT / 'text')
                MANIFESTS_DIR = ensure_dir(RESULTS_ROOT / 'manifests')
                RUNTIME_DIR = ensure_dir(RESULTS_ROOT / 'runtime')
                LIVE_SCORES_DIR = ensure_dir(RESULTS_ROOT / 'live_scores')
                ZIP_PATH = RESULTS_ROOT / f'{NOTEBOOK_SLUG}_bundle.zip'

                BLOCK12B_ROOT = RESULTS_DIR / BLOCK12B_SLUG
                BLOCK12B_TABLES_DIR = BLOCK12B_ROOT / 'tables'
                BLOCK12B_MANIFESTS_DIR = BLOCK12B_ROOT / 'manifests'

                def run(cmd: list[str], cwd: Path | None = None) -> str:
                    completed = subprocess.run(cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True, check=True)
                    return completed.stdout.strip()

                def safe_float(value, default=float('nan')) -> float:
                    try:
                        numeric = float(value)
                        if math.isnan(numeric):
                            return default
                        return numeric
                    except Exception:
                        return default

                def weighted_mean(values, weights) -> float:
                    values_arr = np.asarray(values, dtype=float)
                    weights_arr = np.asarray(weights, dtype=float)
                    valid = np.isfinite(values_arr) & np.isfinite(weights_arr) & (weights_arr > 0)
                    if not valid.any():
                        return float('nan')
                    return float(np.average(values_arr[valid], weights=weights_arr[valid]))

                def coverage_floor(n_variants: int) -> int:
                    return max(MIN_RULE_ON_ABS, int(math.ceil(float(n_variants) * MIN_RULE_ON_FRAC)))

                def bootstrap_gap(labels, mask, replicates: int, seed: int) -> dict:
                    labels_arr = np.asarray(labels, dtype=float)
                    mask_arr = np.asarray(mask, dtype=bool)
                    if labels_arr.size == 0:
                        return {
                            'pathogenic_fraction_rule_on': float('nan'),
                            'pathogenic_fraction_rule_off': float('nan'),
                            'enrichment_gap': float('nan'),
                            'gap_ci_low': float('nan'),
                            'gap_ci_high': float('nan'),
                        }
                    on = labels_arr[mask_arr]
                    off = labels_arr[~mask_arr]
                    on_mean = float(np.mean(on)) if on.size else float('nan')
                    off_mean = float(np.mean(off)) if off.size else float('nan')
                    gap = on_mean - off_mean if on.size and off.size else float('nan')
                    if not on.size or not off.size:
                        return {
                            'pathogenic_fraction_rule_on': on_mean,
                            'pathogenic_fraction_rule_off': off_mean,
                            'enrichment_gap': gap,
                            'gap_ci_low': float('nan'),
                            'gap_ci_high': float('nan'),
                        }
                    rng = np.random.default_rng(seed)
                    samples = []
                    for _ in range(replicates):
                        sample_on = rng.choice(on, size=on.size, replace=True)
                        sample_off = rng.choice(off, size=off.size, replace=True)
                        samples.append(float(sample_on.mean() - sample_off.mean()))
                    return {
                        'pathogenic_fraction_rule_on': on_mean,
                        'pathogenic_fraction_rule_off': off_mean,
                        'enrichment_gap': gap,
                        'gap_ci_low': float(np.quantile(samples, 0.025)),
                        'gap_ci_high': float(np.quantile(samples, 0.975)),
                    }

                def odds_ratio_from_mask(labels, mask) -> dict:
                    labels_arr = np.asarray(labels, dtype=int)
                    mask_arr = np.asarray(mask, dtype=bool)
                    positive_with = int(((labels_arr == 1) & mask_arr).sum())
                    negative_with = int(((labels_arr == 0) & mask_arr).sum())
                    positive_without = int(((labels_arr == 1) & ~mask_arr).sum())
                    negative_without = int(((labels_arr == 0) & ~mask_arr).sum())
                    odds_ratio = ((positive_with + 0.5) * (negative_without + 0.5)) / ((negative_with + 0.5) * (positive_without + 0.5))
                    return {
                        'positive_with_rule': positive_with,
                        'negative_with_rule': negative_with,
                        'positive_without_rule': positive_without,
                        'negative_without_rule': negative_without,
                        'odds_ratio': float(odds_ratio),
                    }

                def random_coverage_matched_gap(labels, n_on: int, replicates: int, seed: int) -> dict:
                    labels_arr = np.asarray(labels, dtype=float)
                    n_total = labels_arr.size
                    if n_total == 0 or n_on <= 0 or n_on >= n_total:
                        return {
                            'random_gap_mean': float('nan'),
                            'random_gap_p95': float('nan'),
                            'random_gap_p05': float('nan'),
                        }
                    rng = np.random.default_rng(seed)
                    gaps = []
                    all_indices = np.arange(n_total)
                    for _ in range(replicates):
                        chosen = rng.choice(all_indices, size=n_on, replace=False)
                        mask = np.zeros(n_total, dtype=bool)
                        mask[chosen] = True
                        on = labels_arr[mask]
                        off = labels_arr[~mask]
                        gaps.append(float(on.mean() - off.mean()))
                    return {
                        'random_gap_mean': float(np.mean(gaps)),
                        'random_gap_p95': float(np.quantile(gaps, 0.95)),
                        'random_gap_p05': float(np.quantile(gaps, 0.05)),
                    }

                def normalize_protein_sequence(sequence: str, sequence_mode: str) -> str:
                    sequence = ''.join(str(sequence).strip().split()).upper()
                    return ' '.join(sequence) if sequence_mode == 'spaced' else sequence

                AA_BUCKETS = {
                    'A': 'hydrophobic', 'V': 'hydrophobic', 'I': 'hydrophobic', 'L': 'hydrophobic', 'M': 'hydrophobic',
                    'F': 'aromatic', 'Y': 'aromatic', 'W': 'aromatic',
                    'S': 'polar', 'T': 'polar', 'N': 'polar', 'Q': 'polar', 'C': 'polar',
                    'K': 'positive', 'R': 'positive', 'H': 'positive',
                    'D': 'negative', 'E': 'negative',
                    'G': 'special', 'P': 'special',
                }

                def aa_bucket(aa: str) -> str:
                    return AA_BUCKETS.get(str(aa).upper(), 'other')

                def chemistry_trigger_from_columns(frame: pd.DataFrame) -> pd.Series:
                    wt_bucket = frame['wt_aa'].astype(str).str.upper().map(aa_bucket)
                    mut_bucket = frame['mut_aa'].astype(str).str.upper().map(aa_bucket)
                    return wt_bucket.ne(mut_bucket) | frame['mut_aa'].astype(str).str.upper().isin({'P', 'G', 'C'})

                def select_hidden_layers(hidden_states) -> list:
                    n_layers = len(hidden_states)
                    if n_layers <= 4:
                        return list(hidden_states)
                    return [hidden_states[0], hidden_states[n_layers // 2], hidden_states[-1]]

                def covariance_features_dual(wt_hidden: np.ndarray, mut_hidden: np.ndarray) -> dict:
                    wt_last = np.asarray(wt_hidden[-1], dtype=np.float32)
                    mut_last = np.asarray(mut_hidden[-1], dtype=np.float32)
                    wt_centered = wt_last - wt_last.mean(axis=0, keepdims=True)
                    mut_centered = mut_last - mut_last.mean(axis=0, keepdims=True)
                    denom_wt = max(1, wt_centered.shape[0] - 1)
                    denom_mut = max(1, mut_centered.shape[0] - 1)
                    cov_wt = (wt_centered.T @ wt_centered) / denom_wt
                    cov_mut = (mut_centered.T @ mut_centered) / denom_mut
                    diff = cov_mut - cov_wt
                    frob_dist = float(np.linalg.norm(diff, ord='fro'))
                    trace_wt = float(np.trace(cov_wt))
                    trace_mut = float(np.trace(cov_mut))
                    trace_ratio = trace_mut / trace_wt if abs(trace_wt) > 1e-8 else float('nan')
                    sign, logdet_wt = np.linalg.slogdet(cov_wt + np.eye(cov_wt.shape[0], dtype=np.float32) * 1e-4)
                    sign_mut, logdet_mut = np.linalg.slogdet(cov_mut + np.eye(cov_mut.shape[0], dtype=np.float32) * 1e-4)
                    sps_log = float(logdet_mut - logdet_wt) if sign > 0 and sign_mut > 0 else float('nan')
                    return {
                        'frob_dist': frob_dist,
                        'trace_ratio': trace_ratio,
                        'sps_log': sps_log,
                    }

                def score_vector_from_frame(frame: pd.DataFrame, alpha: float) -> pd.DataFrame:
                    scored = frame.copy()
                    ll_norm = scored['ll_proper'].rank(method='average', ascending=False, pct=True).astype(float)
                    frob_norm = scored['frob_dist'].rank(method='average', ascending=False, pct=True).astype(float)
                    scored['ll_rank_norm'] = ll_norm
                    scored['frob_rank_norm'] = frob_norm
                    scored['pair_rank_fixed_055'] = alpha * frob_norm + (1.0 - alpha) * ll_norm
                    scored['pair_minus_ll'] = scored['pair_rank_fixed_055'] - scored['ll_rank_norm']
                    scored['chemistry_trigger'] = chemistry_trigger_from_columns(scored)
                    return scored

                def compute_rule_mask(frame: pd.DataFrame, rule_type: str, threshold: float, confidence_threshold: float | None) -> pd.Series:
                    pair_signal = pd.to_numeric(frame['pair_minus_ll'], errors='coerce').fillna(-999.0) >= float(threshold)
                    scalar_signal = pd.to_numeric(frame['ll_rank_norm'], errors='coerce').fillna(-999.0) >= (1.0 - float(threshold))
                    chemistry_signal = frame['chemistry_trigger'].fillna(False).astype(bool)
                    confidence_signal = pd.to_numeric(frame['pair_rank_fixed_055'], errors='coerce').fillna(-999.0) >= float(confidence_threshold if confidence_threshold is not None else 0.0)

                    if rule_type == 'chemistry_only':
                        return chemistry_signal
                    if rule_type == 'pair_only':
                        return pair_signal
                    if rule_type == 'scalar_only':
                        return scalar_signal
                    if rule_type == 'combined':
                        return chemistry_signal & pair_signal
                    if rule_type == 'combined_confident':
                        return chemistry_signal & pair_signal & confidence_signal
                    return pd.Series(np.zeros(len(frame), dtype=bool), index=frame.index)

                def summarize_rule(frame: pd.DataFrame, rule_type: str, threshold: float, confidence_threshold: float | None, seed: int) -> dict:
                    mask = compute_rule_mask(frame, rule_type, threshold, confidence_threshold)
                    labels = frame['label'].astype(int).to_numpy()
                    coverage_target = coverage_floor(len(frame))
                    gap_stats = bootstrap_gap(labels, mask.to_numpy(), BOOTSTRAP_REPLICATES, seed)
                    or_stats = odds_ratio_from_mask(labels, mask.to_numpy())
                    random_stats = random_coverage_matched_gap(labels, int(mask.sum()), RANDOM_REPLICATES, seed + 17)
                    return {
                        'rule_type': str(rule_type),
                        'threshold': float(threshold),
                        'confidence_threshold': float(confidence_threshold) if confidence_threshold is not None else float('nan'),
                        'n_rule_on': int(mask.sum()),
                        'fraction_rule_on': float(mask.mean()),
                        'coverage_target': int(coverage_target),
                        'coverage_floor_pass': bool(int(mask.sum()) >= int(coverage_target)),
                        **gap_stats,
                        **or_stats,
                        **random_stats,
                    }

                def select_covariance_candidate(candidate_df: pd.DataFrame) -> pd.Series | None:
                    if candidate_df.empty:
                        return None
                    covariance_only = candidate_df.loc[candidate_df['rule_type'].isin(['pair_only', 'combined', 'combined_confident'])].copy()
                    if covariance_only.empty:
                        return None
                    covariance_only['coverage_pass_int'] = covariance_only['coverage_floor_pass'].fillna(False).astype(int)
                    covariance_only['rule_priority'] = covariance_only['rule_type'].map({
                        'combined_confident': 0,
                        'combined': 1,
                        'pair_only': 2,
                    }).fillna(99).astype(int)
                    covariance_only = covariance_only.sort_values(
                        ['coverage_pass_int', 'enrichment_gap', 'odds_ratio', 'n_rule_on', 'rule_priority'],
                        ascending=[False, False, False, False, True],
                    ).reset_index(drop=True)
                    return covariance_only.iloc[0]

                def same_position_top_hit_rate(frame: pd.DataFrame, score_column: str) -> dict:
                    working = frame.copy()
                    working[score_column] = pd.to_numeric(working[score_column], errors='coerce')
                    grouped = []
                    for position, group in working.groupby('position', sort=True):
                        labels = group['label'].astype(int)
                        if labels.nunique() < 2:
                            continue
                        top_row = group.sort_values(score_column, ascending=False, kind='stable').iloc[0]
                        grouped.append(int(top_row['label']))
                    if not grouped:
                        return {'n_mixed_positions': 0, 'top_hit_pathogenic_rate': float('nan')}
                    return {
                        'n_mixed_positions': int(len(grouped)),
                        'top_hit_pathogenic_rate': float(np.mean(grouped)),
                    }

                def safe_auc(labels, scores) -> float:
                    labels_arr = pd.Series(labels).astype(int)
                    scores_arr = pd.Series(scores).astype(float)
                    if labels_arr.nunique() < 2:
                        return float('nan')
                    return float(roc_auc_score(labels_arr.to_numpy(), scores_arr.to_numpy()))

                def tp53_domain_label(position: int) -> str:
                    if 94 <= position <= 292:
                        return 'dna_binding'
                    if 323 <= position <= 355:
                        return 'tetramerization'
                    if 63 <= position <= 92:
                        return 'proline_rich'
                    return 'other'

                TP53_HOTSPOTS = {175, 179, 220, 245, 248, 249, 273, 282}

                def structural_reference_candidates() -> list[Path]:
                    return [
                        RESULTS_DIR / '07b_block10_structural_dissociation_tp53_h100' / '07b_block10_structural_dissociation_tp53_h100' / 'tables' / 'tp53_structural_pairs_variant_level_strict.csv',
                        RESULTS_DIR / '07b_block10_structural_dissociation_tp53_h100' / 'tables' / 'tp53_structural_pairs_variant_level_strict.csv',
                        RESULTS_DIR / '07c_block10_structural_dissociation_tp53_h100' / '07c_block10_structural_dissociation_tp53_h100' / 'tables' / 'tp53_structural_pairs_variant_level_strict.csv',
                        RESULTS_DIR / '07c_block10_structural_dissociation_tp53_h100' / 'tables' / 'tp53_structural_pairs_variant_level_strict.csv',
                        RESULTS_DIR / '07b_block10_structural_dissociation_tp53_h100' / '07b_block10_structural_dissociation_tp53_h100' / 'tables' / 'tp53_structural_pairs_variant_level_broad.csv',
                        RESULTS_DIR / '07b_block10_structural_dissociation_tp53_h100' / 'tables' / 'tp53_structural_pairs_variant_level_broad.csv',
                    ]

                def load_structural_reference() -> tuple[pd.DataFrame, str, str]:
                    for candidate in structural_reference_candidates():
                        if candidate.exists():
                            frame = pd.read_csv(candidate)
                            if 'contact_change_fraction_median' not in frame.columns and 'contact_change_fraction' in frame.columns:
                                frame['contact_change_fraction_median'] = frame['contact_change_fraction']
                            if {'wt_aa', 'mut_aa'}.issubset(frame.columns) and 'position_1' in frame.columns:
                                frame['variant_id_one_based'] = (
                                    'TP53:'
                                    + frame['wt_aa'].astype(str).str.upper()
                                    + frame['position_1'].astype(int).astype(str)
                                    + frame['mut_aa'].astype(str).str.upper()
                                )
                            return frame, str(candidate), ('strict' if 'strict' in candidate.name else 'broad')
                    return pd.DataFrame(columns=[
                        'variant_id',
                        'excess_local_rmsd_median',
                        'contact_change_fraction_median',
                        'pair_rank_norm',
                        'll_rank_norm',
                    ]), 'none', 'missing'

                def parse_fasta_sequence(path: Path) -> str:
                    lines = [line.strip() for line in path.read_text(encoding='utf-8').splitlines() if line.strip() and not line.startswith('>')]
                    return ''.join(lines).upper()

                def validate_panel_against_sequence(panel_df: pd.DataFrame, sequence: str, gene: str, panel_name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
                    keep_rows = []
                    audit_rows = []
                    for row in panel_df.to_dict(orient='records'):
                        position = int(row.get('position', -1))
                        wt_aa = str(row.get('wt_aa', '')).upper()
                        observed = None
                        reason = None
                        if position < 0 or position >= len(sequence):
                            reason = 'position_out_of_range'
                        else:
                            observed = sequence[position].upper()
                            if observed != wt_aa:
                                reason = 'wt_mismatch'
                        if reason is None:
                            keep_rows.append(row)
                        else:
                            audit_rows.append({
                                'panel_name': panel_name,
                                'gene': gene,
                                'variant_id': str(row.get('variant_id', row.get('name', ''))),
                                'name': str(row.get('name', '')),
                                'position': position,
                                'wt_aa': wt_aa,
                                'mut_aa': str(row.get('mut_aa', '')).upper(),
                                'reason': reason,
                                'observed_residue': observed,
                            })
                    keep_df = pd.DataFrame(keep_rows)
                    if keep_df.empty:
                        keep_df = panel_df.iloc[0:0].copy()
                    audit_df = pd.DataFrame(audit_rows)
                    return keep_df, audit_df

                def load_model_bundle(spec: dict) -> tuple[dict | None, dict]:
                    manifest = {
                        'model_label': spec['model_label'],
                        'model_name': spec['model_name'],
                        'family_label': spec['family_label'],
                        'architecture_kind': spec['architecture_kind'],
                        'adapter_kind': spec['adapter_kind'],
                    }
                    try:
                        tokenizer = AutoTokenizer.from_pretrained(spec['model_name'], trust_remote_code=True)
                        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
                        device = 'cuda' if torch.cuda.is_available() else 'cpu'
                        if spec['adapter_kind'] == 't5':
                            model = AutoModelForSeq2SeqLM.from_pretrained(spec['model_name'], torch_dtype=torch_dtype, trust_remote_code=True)
                        elif spec['adapter_kind'] == 'causal':
                            model = AutoModel.from_pretrained(spec['model_name'], torch_dtype=torch_dtype, trust_remote_code=True)
                        elif spec['adapter_kind'] == 'auto':
                            try:
                                model = AutoModel.from_pretrained(spec['model_name'], torch_dtype=torch_dtype, trust_remote_code=True)
                            except Exception:
                                model = AutoModelForMaskedLM.from_pretrained(spec['model_name'], torch_dtype=torch_dtype, trust_remote_code=True)
                        else:
                            model = AutoModelForMaskedLM.from_pretrained(spec['model_name'], torch_dtype=torch_dtype, trust_remote_code=True)
                        model = model.to(device)
                        model.eval()
                        manifest.update({
                            'status': 'loaded',
                            'device': device,
                            'torch_dtype': str(torch_dtype),
                        })
                        return {'tokenizer': tokenizer, 'model': model, 'device': device}, manifest
                    except Exception as exc:
                        manifest.update({
                            'status': 'load_failed',
                            'error_type': type(exc).__name__,
                            'error_message': str(exc)[:500],
                        })
                        return None, manifest

                def encode_sequence(bundle: dict, sequence: str, sequence_mode: str) -> dict[str, torch.Tensor]:
                    encoded = bundle['tokenizer'](
                        normalize_protein_sequence(sequence, sequence_mode),
                        return_tensors='pt',
                        add_special_tokens=False,
                    )
                    return {key: value.to(bundle['device']) for key, value in encoded.items()}

                def stack_hidden_states(outputs, residue_count: int) -> np.ndarray:
                    hidden_states = getattr(outputs, 'hidden_states', None)
                    if hidden_states is None:
                        hidden_states = getattr(outputs, 'encoder_hidden_states', None)
                    if hidden_states is None:
                        raise RuntimeError('Model output does not expose hidden states.')
                    selected = select_hidden_layers(hidden_states)
                    layers = []
                    for layer in selected:
                        layers.append(layer[0, :residue_count, :].detach().cpu().float().numpy())
                    return np.stack(layers, axis=0)

                def generic_hidden_forward(bundle: dict, spec: dict, encoded: dict[str, torch.Tensor]):
                    model = bundle['model']
                    if spec['adapter_kind'] == 'causal':
                        return model(**encoded, output_hidden_states=True, use_cache=False)
                    return model(**encoded, output_hidden_states=True)

                def score_panel_with_generic_model(panel_df: pd.DataFrame, sequence_map: dict[str, str], spec: dict, output_path: Path) -> tuple[pd.DataFrame, dict]:
                    if output_path.exists() and not OVERWRITE:
                        reused = pd.read_csv(output_path)
                        return reused, {
                            'model_label': spec['model_label'],
                            'model_name': spec['model_name'],
                            'status': 'reused_existing_scores',
                            'n_rows': int(len(reused)),
                        }

                    bundle, manifest = load_model_bundle(spec)
                    if bundle is None:
                        return pd.DataFrame(), manifest

                    rows = []
                    wt_cache: dict[tuple[str, int], np.ndarray] = {}
                    try:
                        for index, row in enumerate(panel_df.to_dict(orient='records'), start=1):
                            gene = str(row['gene']).upper()
                            sequence = sequence_map[gene]
                            position = int(row['position'])
                            wt_aa = str(row['wt_aa']).upper()
                            mut_aa = str(row['mut_aa']).upper()
                            if sequence[position].upper() != wt_aa:
                                raise ValueError(f'WT mismatch for {row["variant_id"]}: expected {wt_aa}, found {sequence[position]}')

                            start = max(0, position - WINDOW_RADIUS)
                            end = min(len(sequence), position + WINDOW_RADIUS + 1)
                            local_sequence = sequence[start:end]
                            local_pos = position - start
                            wt_key = (gene, position)

                            if wt_key not in wt_cache:
                                wt_encoded = encode_sequence(bundle, local_sequence, spec['sequence_mode'])
                                token_count = int(wt_encoded['input_ids'].shape[1])
                                if token_count != len(local_sequence):
                                    raise RuntimeError(
                                        f'Tokenization mismatch for {spec["model_label"]}: expected {len(local_sequence)} residues, got {token_count} tokens'
                                    )
                                with torch.inference_mode():
                                    wt_outputs = generic_hidden_forward(bundle, spec, wt_encoded)
                                wt_cache[wt_key] = stack_hidden_states(wt_outputs, len(local_sequence))

                            wt_hidden = wt_cache[wt_key]
                            mutated_local = local_sequence[:local_pos] + mut_aa + local_sequence[local_pos + 1:]
                            mut_encoded = encode_sequence(bundle, mutated_local, spec['sequence_mode'])
                            token_count = int(mut_encoded['input_ids'].shape[1])
                            if token_count != len(mutated_local):
                                raise RuntimeError(
                                    f'Mut tokenization mismatch for {spec["model_label"]}: expected {len(mutated_local)} residues, got {token_count} tokens'
                                )
                            with torch.inference_mode():
                                mut_outputs = generic_hidden_forward(bundle, spec, mut_encoded)
                            mut_hidden = stack_hidden_states(mut_outputs, len(mutated_local))
                            cov = covariance_features_dual(wt_hidden, mut_hidden)
                            token_shift = float(np.linalg.norm(mut_hidden[-1][local_pos] - wt_hidden[-1][local_pos]))
                            rows.append({
                                'gene': gene,
                                'name': row['name'],
                                'position': position,
                                'wt_aa': wt_aa,
                                'mut_aa': mut_aa,
                                'label': int(row['label']),
                                'variant_id': row['variant_id'],
                                'frob_dist': float(cov['frob_dist']),
                                'trace_ratio': float(cov['trace_ratio']),
                                'sps_log': float(cov['sps_log']),
                                'll_proper': token_shift,
                                'model_name': spec['model_name'],
                            })
                            if index % CHECKPOINT_EVERY == 0 or index == len(panel_df):
                                pd.DataFrame(rows).to_csv(output_path, index=False)
                        output = pd.DataFrame(rows)
                        output.to_csv(output_path, index=False)
                        manifest.update({'status': 'completed', 'n_rows': int(len(output))})
                        return output, manifest
                    except Exception as exc:
                        partial = pd.DataFrame(rows)
                        if not partial.empty:
                            partial.to_csv(output_path, index=False)
                        manifest.update({
                            'status': 'partial_failure' if not partial.empty else 'scoring_failed',
                            'n_rows': int(len(partial)),
                            'error_type': type(exc).__name__,
                            'error_message': str(exc)[:500],
                        })
                        return partial, manifest
                    finally:
                        try:
                            del bundle['model']
                        except Exception:
                            pass
                        if torch.cuda.is_available():
                            torch.cuda.empty_cache()

                def score_panel_with_model(panel_df: pd.DataFrame, sequence_map: dict[str, str], spec: dict, output_path: Path) -> tuple[pd.DataFrame, dict]:
                    if spec['adapter_kind'] == 'esm':
                        if output_path.exists() and not OVERWRITE:
                            reused = pd.read_csv(output_path)
                            return reused, {
                                'model_label': spec['model_label'],
                                'model_name': spec['model_name'],
                                'status': 'reused_existing_scores',
                                'n_rows': int(len(reused)),
                                'adapter_kind': 'esm',
                            }
                        grouped_rows = []
                        for gene, gene_df in panel_df.groupby('gene', sort=False):
                            gene_key = str(gene).upper()
                            if gene_key not in sequence_map:
                                raise KeyError(f'Missing sequence for gene {gene_key} in panel scoring.')
                            gene_rows = _ensure_gene_score_rows(
                                gene=gene_key,
                                sequence=sequence_map[gene_key],
                                variants=gene_df[['gene', 'name', 'position', 'wt_aa', 'mut_aa', 'label', 'variant_id']].to_dict(orient='records'),
                                model_name=spec['model_name'],
                                output_dir=output_path.parent,
                                window_radius=WINDOW_RADIUS,
                                checkpoint_every=CHECKPOINT_EVERY,
                                overwrite=OVERWRITE,
                            )
                            grouped_rows.extend(gene_rows)
                        output = pd.DataFrame(grouped_rows)
                        if not output.empty and 'variant_id' in output.columns and 'variant_id' in panel_df.columns:
                            ordering = panel_df[['variant_id']].copy()
                            ordering['_order'] = np.arange(len(ordering))
                            output = output.merge(ordering, on='variant_id', how='left')
                            output = output.sort_values(['_order', 'variant_id'], kind='stable').drop(columns=['_order'])
                        output.to_csv(output_path, index=False)
                        return output, {
                            'model_label': spec['model_label'],
                            'model_name': spec['model_name'],
                            'status': 'completed',
                            'n_rows': int(len(output)),
                            'adapter_kind': 'esm',
                        }
                    return score_panel_with_generic_model(panel_df, sequence_map, spec, output_path)

                runtime_manifest = {
                    'repo_root': str(REPO_ROOT),
                    'head_commit': run(['git', 'rev-parse', 'HEAD'], cwd=REPO_ROOT),
                    'branch': run(['git', 'branch', '--show-current'], cwd=REPO_ROOT),
                    'cuda_available': bool(torch.cuda.is_available()),
                    'cuda_device_count': int(torch.cuda.device_count()) if torch.cuda.is_available() else 0,
                    'cuda_device_name': torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu',
                    'rerun_brca1': RERUN_BRCA1,
                    'include_ankh': INCLUDE_ANKH,
                }
                (RUNTIME_DIR / 'runtime_manifest.json').write_text(json.dumps(runtime_manifest, indent=2), encoding='utf-8')
                display(pd.DataFrame([runtime_manifest]))
                done('Helpers, repo wiring, statistics, structural loaders, and live scoring adapters are ready.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Load Block 12B artifacts, diagnose unresolved weaknesses, and close the TP53 structural layer
                required_12b_tables = {
                    'variant_scores': BLOCK12B_TABLES_DIR / 'tp53_model_variant_scores.csv',
                    'model_summary': BLOCK12B_TABLES_DIR / 'tp53_model_summary.csv',
                    'calibration': BLOCK12B_TABLES_DIR / 'tp53_rule_candidate_calibration.csv',
                    'selected_rules': BLOCK12B_TABLES_DIR / 'tp53_selected_rules.csv',
                    'controls': BLOCK12B_TABLES_DIR / 'tp53_rule_vs_controls.csv',
                    'same_position': BLOCK12B_TABLES_DIR / 'tp53_same_position_ranking_summary.csv',
                    'robustness': BLOCK12B_TABLES_DIR / 'tp53_robustness_slice_summary.csv',
                    'failure': BLOCK12B_TABLES_DIR / 'tp53_failure_taxonomy.csv',
                }
                missing_12b = [name for name, path in required_12b_tables.items() if not path.exists()]
                if missing_12b:
                    raise FileNotFoundError(f'Missing required Block 12B tables: {missing_12b}')

                variant_scores_12b = pd.read_csv(required_12b_tables['variant_scores'])
                model_summary_12b = pd.read_csv(required_12b_tables['model_summary'])
                calibration_12b = pd.read_csv(required_12b_tables['calibration'])
                selected_rules_12b = pd.read_csv(required_12b_tables['selected_rules'])
                control_table_12b = pd.read_csv(required_12b_tables['controls'])
                same_position_12b = pd.read_csv(required_12b_tables['same_position'])
                robustness_12b = pd.read_csv(required_12b_tables['robustness'])
                failure_12b = pd.read_csv(required_12b_tables['failure'])

                if 'selected_rule_hit' not in variant_scores_12b.columns:
                    variant_scores_12b['selected_rule_hit'] = False

                structural_reference, structural_source_path, structural_source_kind = load_structural_reference()
                tp53_structural_closure = variant_scores_12b.merge(
                    structural_reference,
                    on='variant_id',
                    how='left',
                    suffixes=('', '_structure'),
                )
                for base_name in ['excess_local_rmsd_median', 'contact_change_fraction_median', 'pair_rank_norm', 'll_rank_norm']:
                    structure_name = f'{base_name}_structure'
                    if structure_name in tp53_structural_closure.columns:
                        tp53_structural_closure[base_name] = pd.to_numeric(
                            tp53_structural_closure.get(base_name, pd.Series(dtype=float)),
                            errors='coerce',
                        ).combine_first(
                            pd.to_numeric(tp53_structural_closure[structure_name], errors='coerce')
                        )
                tp53_structural_closure['structure_available'] = pd.to_numeric(
                    tp53_structural_closure.get('excess_local_rmsd_median', pd.Series(dtype=float)),
                    errors='coerce',
                ).notna()
                tp53_structural_closure['geometry_positive'] = pd.to_numeric(
                    tp53_structural_closure.get('excess_local_rmsd_median', pd.Series(dtype=float)),
                    errors='coerce',
                ).fillna(-999.0) > 0.0
                tp53_structural_closure['tp53_hotspot'] = tp53_structural_closure['position'].astype(int).isin(TP53_HOTSPOTS)
                tp53_structural_closure['tp53_domain'] = tp53_structural_closure['position'].astype(int).map(tp53_domain_label)

                unresolved_rows = []
                control_pivot = control_table_12b.pivot_table(
                    index='model_label',
                    columns='control_name',
                    values='enrichment_gap',
                    aggfunc='first',
                ).reset_index()
                if 'selected_rule' not in control_pivot.columns:
                    control_pivot['selected_rule'] = np.nan
                if 'scalar_top_n_matched' not in control_pivot.columns:
                    control_pivot['scalar_top_n_matched'] = np.nan

                for _, row in selected_rules_12b.iterrows():
                    model_label = str(row['model_label'])
                    structure_rows = tp53_structural_closure.loc[
                        tp53_structural_closure['model_label'].eq(model_label) & tp53_structural_closure['structure_available'].fillna(False)
                    ]
                    control_row = control_pivot.loc[control_pivot['model_label'].eq(model_label)]
                    selected_gap = safe_float(control_row['selected_rule'].iloc[0], float('nan')) if not control_row.empty else float('nan')
                    scalar_gap = safe_float(control_row['scalar_top_n_matched'].iloc[0], float('nan')) if not control_row.empty else float('nan')
                    unresolved_flags = []
                    if str(row['rule_type']) == 'scalar_only':
                        unresolved_flags.append('scalar_only_primary')
                    if not bool(row['coverage_floor_pass']):
                        unresolved_flags.append('coverage_floor_failed')
                    if structure_rows.empty:
                        unresolved_flags.append('missing_structural_overlap')
                    if math.isfinite(selected_gap) and math.isfinite(scalar_gap) and not (selected_gap > scalar_gap):
                        unresolved_flags.append('selected_rule_not_above_scalar_matched')
                    unresolved_rows.append({
                        'model_label': model_label,
                        'family_label': row['family_label'],
                        'architecture_kind': row['architecture_kind'],
                        'selected_rule_type': row['rule_type'],
                        'selected_rule_enrichment_gap': safe_float(row['enrichment_gap'], float('nan')),
                        'selected_rule_n_on': int(row['n_rule_on']),
                        'structural_overlap_rows': int(len(structure_rows)),
                        'selected_rule_vs_scalar_gap_delta': selected_gap - scalar_gap if math.isfinite(selected_gap) and math.isfinite(scalar_gap) else float('nan'),
                        'unresolved_flags': '|'.join(unresolved_flags) if unresolved_flags else 'none',
                    })

                unresolved_table = pd.DataFrame(unresolved_rows).sort_values(['unresolved_flags', 'model_label']).reset_index(drop=True)

                structural_rows = []
                for model_label, group in tp53_structural_closure.groupby('model_label'):
                    structural_subset = group.loc[group['structure_available'].fillna(False)].copy()
                    if structural_subset.empty:
                        structural_rows.append({
                            'model_label': model_label,
                            'family_label': group['family_label'].iloc[0],
                            'architecture_kind': group['architecture_kind'].iloc[0],
                            'n_structural_rows': 0,
                            'spearman_pair_minus_ll_vs_excess_local_rmsd': float('nan'),
                            'spearman_ll_rank_vs_excess_local_rmsd': float('nan'),
                            'spearman_pair_minus_ll_vs_contact_change_fraction': float('nan'),
                            'mean_excess_local_rmsd_rule_on': float('nan'),
                            'mean_excess_local_rmsd_rule_off': float('nan'),
                            'structural_geometry_gap': float('nan'),
                            'structural_status': 'no_overlap',
                        })
                        continue

                    on_mask = structural_subset['selected_rule_hit'].fillna(False).astype(bool).to_numpy()
                    geometry_gap = bootstrap_gap(
                        structural_subset['geometry_positive'].astype(int).to_numpy(),
                        on_mask,
                        BOOTSTRAP_REPLICATES,
                        RANDOM_SEED + 1000 + len(structural_rows),
                    )
                    structural_rows.append({
                        'model_label': model_label,
                        'family_label': structural_subset['family_label'].iloc[0],
                        'architecture_kind': structural_subset['architecture_kind'].iloc[0],
                        'n_structural_rows': int(len(structural_subset)),
                        'spearman_pair_minus_ll_vs_excess_local_rmsd': float(pd.Series(structural_subset['pair_minus_ll']).corr(pd.Series(structural_subset['excess_local_rmsd_median']), method='spearman')),
                        'spearman_ll_rank_vs_excess_local_rmsd': float(pd.Series(structural_subset['ll_rank_norm']).corr(pd.Series(structural_subset['excess_local_rmsd_median']), method='spearman')),
                        'spearman_pair_minus_ll_vs_contact_change_fraction': float(pd.Series(structural_subset['pair_minus_ll']).corr(pd.Series(structural_subset['contact_change_fraction_median']), method='spearman')),
                        'mean_excess_local_rmsd_rule_on': float(pd.to_numeric(structural_subset.loc[on_mask, 'excess_local_rmsd_median'], errors='coerce').mean()) if on_mask.any() else float('nan'),
                        'mean_excess_local_rmsd_rule_off': float(pd.to_numeric(structural_subset.loc[~on_mask, 'excess_local_rmsd_median'], errors='coerce').mean()) if (~on_mask).any() else float('nan'),
                        'structural_geometry_gap': geometry_gap['enrichment_gap'],
                        'structural_status': 'closed',
                    })

                tp53_structural_closure_summary = pd.DataFrame(structural_rows).sort_values('n_structural_rows', ascending=False).reset_index(drop=True)

                structural_manifest = {
                    'structural_source_path': structural_source_path,
                    'structural_source_kind': structural_source_kind,
                    'n_variant_score_rows': int(len(variant_scores_12b)),
                    'n_structural_reference_rows': int(len(structural_reference)),
                    'models_with_structural_overlap': int((tp53_structural_closure_summary['n_structural_rows'] > 0).sum()),
                }

                unresolved_table.to_csv(TABLES_DIR / 'tp53_unresolved_from_12b.csv', index=False)
                tp53_structural_closure.to_csv(TABLES_DIR / 'tp53_structural_closure_reference.csv', index=False)
                tp53_structural_closure_summary.to_csv(TABLES_DIR / 'tp53_structural_closure_summary.csv', index=False)
                (MANIFESTS_DIR / 'structural_closure_manifest.json').write_text(json.dumps(structural_manifest, indent=2), encoding='utf-8')

                display(unresolved_table)
                display(tp53_structural_closure_summary)
                done('Block 12B intake is loaded, unresolved weaknesses are enumerated, and the structural layer is now closed onto TP53 model scores.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Re-adjudicate TP53 with covariance-native candidates, scalar-matched controls, and nuclear vs supportive sets
                covariance_rows = []
                hard_control_rows = []
                eligibility_rows = []

                for model_label, group in variant_scores_12b.groupby('model_label'):
                    family_label = str(group['family_label'].iloc[0])
                    architecture_kind = str(group['architecture_kind'].iloc[0])
                    candidate_df = calibration_12b.loc[calibration_12b['model_label'].eq(model_label)].copy()
                    covariance_candidate = select_covariance_candidate(candidate_df)
                    same_position_pair = same_position_top_hit_rate(group, 'pair_minus_ll')
                    same_position_ll = same_position_top_hit_rate(group, 'll_rank_norm')
                    structural_row = tp53_structural_closure_summary.loc[tp53_structural_closure_summary['model_label'].eq(model_label)]
                    structural_pair = safe_float(structural_row['spearman_pair_minus_ll_vs_excess_local_rmsd'].iloc[0], float('nan')) if not structural_row.empty else float('nan')
                    structural_ll = safe_float(structural_row['spearman_ll_rank_vs_excess_local_rmsd'].iloc[0], float('nan')) if not structural_row.empty else float('nan')
                    structural_rows_n = int(structural_row['n_structural_rows'].iloc[0]) if not structural_row.empty else 0

                    if covariance_candidate is None:
                        eligibility_rows.append({
                            'model_label': model_label,
                            'family_label': family_label,
                            'architecture_kind': architecture_kind,
                            'eligibility_status': 'not_eligible',
                            'reason': 'no_covariance_native_candidate',
                        })
                        continue

                    threshold = float(covariance_candidate['threshold'])
                    confidence_threshold = None if not math.isfinite(float(covariance_candidate['confidence_threshold'])) else float(covariance_candidate['confidence_threshold'])
                    covariance_mask = compute_rule_mask(group, str(covariance_candidate['rule_type']), threshold, confidence_threshold)
                    labels = group['label'].astype(int).to_numpy()
                    covariance_gap = bootstrap_gap(labels, covariance_mask.to_numpy(), BOOTSTRAP_REPLICATES, RANDOM_SEED + 5000 + len(covariance_rows))
                    scalar_top_n = group['ll_rank_norm'].rank(method='first', ascending=False) <= int(covariance_mask.sum())
                    scalar_gap = bootstrap_gap(labels, scalar_top_n.to_numpy(), BOOTSTRAP_REPLICATES, RANDOM_SEED + 5100 + len(covariance_rows))
                    chemistry_mask = compute_rule_mask(group, 'chemistry_only', threshold, None)
                    chemistry_gap = bootstrap_gap(labels, chemistry_mask.to_numpy(), BOOTSTRAP_REPLICATES, RANDOM_SEED + 5200 + len(covariance_rows))
                    random_gap = random_coverage_matched_gap(labels, int(covariance_mask.sum()), RANDOM_REPLICATES, RANDOM_SEED + 5300 + len(covariance_rows))

                    hard_control_rows.extend([
                        {
                            'model_label': model_label,
                            'family_label': family_label,
                            'architecture_kind': architecture_kind,
                            'control_name': 'covariance_candidate',
                            'n_rule_on': int(covariance_mask.sum()),
                            'enrichment_gap': covariance_gap['enrichment_gap'],
                        },
                        {
                            'model_label': model_label,
                            'family_label': family_label,
                            'architecture_kind': architecture_kind,
                            'control_name': 'scalar_top_n_matched',
                            'n_rule_on': int(covariance_mask.sum()),
                            'enrichment_gap': scalar_gap['enrichment_gap'],
                        },
                        {
                            'model_label': model_label,
                            'family_label': family_label,
                            'architecture_kind': architecture_kind,
                            'control_name': 'chemistry_only',
                            'n_rule_on': int(chemistry_mask.sum()),
                            'enrichment_gap': chemistry_gap['enrichment_gap'],
                        },
                        {
                            'model_label': model_label,
                            'family_label': family_label,
                            'architecture_kind': architecture_kind,
                            'control_name': 'random_coverage_matched_mean',
                            'n_rule_on': int(covariance_mask.sum()),
                            'enrichment_gap': random_gap['random_gap_mean'],
                        },
                    ])

                    same_position_pair_rate = safe_float(same_position_pair['top_hit_pathogenic_rate'], float('nan'))
                    same_position_ll_rate = safe_float(same_position_ll['top_hit_pathogenic_rate'], float('nan'))
                    beats_scalar = math.isfinite(covariance_gap['enrichment_gap']) and math.isfinite(scalar_gap['enrichment_gap']) and covariance_gap['enrichment_gap'] > scalar_gap['enrichment_gap']
                    beats_chemistry = math.isfinite(covariance_gap['enrichment_gap']) and math.isfinite(chemistry_gap['enrichment_gap']) and covariance_gap['enrichment_gap'] > chemistry_gap['enrichment_gap']
                    same_position_advantage = math.isfinite(same_position_pair_rate) and math.isfinite(same_position_ll_rate) and same_position_pair_rate > same_position_ll_rate
                    structural_advantage = structural_rows_n > 0 and math.isfinite(structural_pair) and math.isfinite(structural_ll) and structural_pair > structural_ll
                    coverage_pass = bool(covariance_candidate['coverage_floor_pass'])
                    enrichment_positive = math.isfinite(covariance_gap['enrichment_gap']) and covariance_gap['enrichment_gap'] > 0

                    if coverage_pass and enrichment_positive and beats_scalar and beats_chemistry and same_position_advantage and structural_advantage:
                        adjudication_status = 'nuclear'
                        reason = 'covariance_candidate_beats_scalar_and_structure'
                    elif coverage_pass and enrichment_positive:
                        adjudication_status = 'supportive'
                        reason = 'positive_but_not_fully_adjudicated'
                    else:
                        adjudication_status = 'not_eligible'
                        reason = 'coverage_or_enrichment_failure'

                    covariance_rows.append({
                        'model_label': model_label,
                        'family_label': family_label,
                        'architecture_kind': architecture_kind,
                        'covariance_rule_type': str(covariance_candidate['rule_type']),
                        'covariance_threshold': threshold,
                        'covariance_confidence_threshold': confidence_threshold if confidence_threshold is not None else float('nan'),
                        'covariance_n_rule_on': int(covariance_mask.sum()),
                        'covariance_enrichment_gap': covariance_gap['enrichment_gap'],
                        'covariance_odds_ratio': float(odds_ratio_from_mask(labels, covariance_mask.to_numpy())['odds_ratio']),
                        'scalar_top_n_matched_gap': scalar_gap['enrichment_gap'],
                        'chemistry_only_gap': chemistry_gap['enrichment_gap'],
                        'random_gap_mean': random_gap['random_gap_mean'],
                        'same_position_pair_minus_ll_rate': same_position_pair_rate,
                        'same_position_ll_rate': same_position_ll_rate,
                        'same_position_advantage': bool(same_position_advantage),
                        'structural_overlap_rows': structural_rows_n,
                        'structural_pair_spearman': structural_pair,
                        'structural_ll_spearman': structural_ll,
                        'structural_advantage': bool(structural_advantage),
                        'beats_scalar_top_n_matched': bool(beats_scalar),
                        'beats_chemistry_only': bool(beats_chemistry),
                        'coverage_floor_pass': coverage_pass,
                        'adjudication_status': adjudication_status,
                        'adjudication_reason': reason,
                    })

                tp53_covariance_adjudication = pd.DataFrame(covariance_rows).sort_values(
                    ['adjudication_status', 'covariance_enrichment_gap'],
                    ascending=[True, False],
                ).reset_index(drop=True)
                tp53_hard_controls = pd.DataFrame(hard_control_rows)

                models_not_eligible = tp53_covariance_adjudication.loc[
                    ~tp53_covariance_adjudication['adjudication_status'].isin(['nuclear', 'supportive'])
                ][['model_label', 'family_label', 'architecture_kind', 'adjudication_reason']].rename(columns={'adjudication_reason': 'reason'})

                nuclear_supportive_sets = tp53_covariance_adjudication[['model_label', 'family_label', 'architecture_kind', 'adjudication_status', 'adjudication_reason']].copy()
                nuclear_supportive_sets['claim_firewall'] = np.where(
                    nuclear_supportive_sets['adjudication_status'].eq('nuclear'),
                    'eligible_for_primary_covariance_claim',
                    np.where(
                        nuclear_supportive_sets['adjudication_status'].eq('supportive'),
                        'supportive_only_not_primary_claim',
                        'excluded_from_primary_claim',
                    ),
                )

                tp53_covariance_adjudication.to_csv(TABLES_DIR / 'tp53_covariance_adjudication_summary.csv', index=False)
                tp53_hard_controls.to_csv(TABLES_DIR / 'tp53_covariance_vs_controls_hard.csv', index=False)
                nuclear_supportive_sets.to_csv(TABLES_DIR / 'tp53_nuclear_supportive_sets.csv', index=False)
                models_not_eligible.to_csv(TABLES_DIR / 'models_not_eligible_for_primary_claim.csv', index=False)

                display(tp53_covariance_adjudication)
                display(nuclear_supportive_sets)
                done('TP53 has been re-adjudicated under covariance-first rules, hard controls, and the nuclear vs supportive firewall.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Build a balanced BRCA1 transfer arm, validate sequence integrity, and optionally score it live across the adjudication roster
                brca1_transfer_path = REPO_ROOT / 'benchmarks' / 'brca1' / 'brca1_transfer100_v1.json'
                brca1_full_path = REPO_ROOT / 'benchmarks' / 'brca1' / 'brca1_full_filtered_v1.json'
                brca1_sequence_path = REPO_ROOT / 'benchmarks' / 'sequences' / 'brca1.fasta'

                brca1_transfer_panel = pd.DataFrame(json.loads(brca1_transfer_path.read_text(encoding='utf-8')))
                brca1_transfer_panel['gene'] = brca1_transfer_panel['gene'].astype(str).str.upper()
                brca1_transfer_panel['variant_id'] = (
                    brca1_transfer_panel['gene'].astype(str)
                    + ':'
                    + brca1_transfer_panel['wt_aa'].astype(str).str.upper()
                    + brca1_transfer_panel['position'].astype(int).astype(str)
                    + brca1_transfer_panel['mut_aa'].astype(str).str.upper()
                )
                brca1_transfer_panel['panel_name'] = 'brca1_transfer100'

                brca1_full = pd.DataFrame(json.loads(brca1_full_path.read_text(encoding='utf-8')))
                brca1_full['gene'] = brca1_full['gene'].astype(str).str.upper()
                brca1_full['variant_id'] = (
                    brca1_full['gene'].astype(str)
                    + ':'
                    + brca1_full['wt_aa'].astype(str).str.upper()
                    + brca1_full['position'].astype(int).astype(str)
                    + brca1_full['mut_aa'].astype(str).str.upper()
                )

                mixed_position_rows = []
                for position, group in brca1_full.groupby('position', sort=True):
                    labels = group['label'].astype(int)
                    if labels.nunique() < 2:
                        continue
                    pathogenic = group.loc[group['label'].astype(int).eq(1)].head(1)
                    benign = group.loc[group['label'].astype(int).eq(0)].head(1)
                    mixed_position_rows.extend(pathogenic.to_dict(orient='records'))
                    mixed_position_rows.extend(benign.to_dict(orient='records'))
                brca1_same_position_panel = pd.DataFrame(mixed_position_rows).drop_duplicates(subset=['variant_id']).reset_index(drop=True)
                brca1_same_position_panel['panel_name'] = 'brca1_same_position_adjudication'

                brca1_sequence = parse_fasta_sequence(brca1_sequence_path)
                brca1_transfer_panel_valid, brca1_transfer_mismatches = validate_panel_against_sequence(
                    brca1_transfer_panel,
                    brca1_sequence,
                    'BRCA1',
                    'brca1_transfer100',
                )
                brca1_same_position_panel_valid, brca1_same_position_mismatches = validate_panel_against_sequence(
                    brca1_same_position_panel,
                    brca1_sequence,
                    'BRCA1',
                    'brca1_same_position_adjudication',
                )

                brca1_transfer_panel_valid.to_csv(TABLES_DIR / 'brca1_transfer100_panel.csv', index=False)
                brca1_same_position_panel_valid.to_csv(TABLES_DIR / 'brca1_same_position_adjudication_panel.csv', index=False)
                brca1_transfer_mismatches.to_csv(TABLES_DIR / 'brca1_transfer100_sequence_audit.csv', index=False)
                brca1_same_position_mismatches.to_csv(TABLES_DIR / 'brca1_same_position_sequence_audit.csv', index=False)

                sequence_map = {'BRCA1': brca1_sequence}
                brca1_live_frames = []
                brca1_runtime_rows = []

                adjudication_models = tp53_covariance_adjudication['model_label'].tolist()
                active_model_specs = [spec for spec in MODEL_SPECS if spec['model_label'] in adjudication_models]

                if RERUN_BRCA1:
                    panels = [('brca1_transfer100', brca1_transfer_panel_valid), ('brca1_same_position_adjudication', brca1_same_position_panel_valid)]
                    for spec in active_model_specs:
                        model_slug = spec['model_name'].replace('/', '_').replace('-', '_')
                        model_dir = ensure_dir(LIVE_SCORES_DIR / model_slug)
                        for panel_name, panel_df in panels:
                            output_path = model_dir / f'{panel_name}_{model_slug}_scores.csv'
                            scored_df, manifest = score_panel_with_model(
                                panel_df[['gene', 'name', 'position', 'wt_aa', 'mut_aa', 'label', 'variant_id']].copy(),
                                sequence_map,
                                spec,
                                output_path,
                            )
                            manifest['panel_name'] = panel_name
                            manifest['output_path'] = str(output_path)
                            brca1_runtime_rows.append(manifest)
                            if not scored_df.empty:
                                scored_df = score_vector_from_frame(scored_df, FIXED_ALPHA)
                                scored_df['model_label'] = spec['model_label']
                                scored_df['family_label'] = spec['family_label']
                                scored_df['architecture_kind'] = spec['architecture_kind']
                                scored_df['panel_name'] = panel_name
                                brca1_live_frames.append(scored_df)
                else:
                    brca1_runtime_rows.append({
                        'status': 'skip_brca1_disabled',
                        'message': 'Set SPECTRALBIO_BLOCK12C_RERUN_BRCA1=1 to execute BRCA1 transfer scoring.',
                    })

                brca1_live_scores = pd.concat(brca1_live_frames, ignore_index=True, sort=False) if brca1_live_frames else pd.DataFrame()
                brca1_runtime_manifest = pd.DataFrame(brca1_runtime_rows)
                brca1_runtime_manifest.to_csv(TABLES_DIR / 'brca1_runtime_manifest.csv', index=False)

                brca1_transfer_rows = []
                brca1_same_position_rows = []
                if not brca1_live_scores.empty:
                    brca1_live_scores.to_csv(TABLES_DIR / 'brca1_live_model_rows.csv', index=False)
                    for _, adjudication_row in tp53_covariance_adjudication.iterrows():
                        model_label = adjudication_row['model_label']
                        transfer_model = brca1_live_scores.loc[
                            brca1_live_scores['model_label'].eq(model_label) & brca1_live_scores['panel_name'].eq('brca1_transfer100')
                        ].copy()
                        same_position_model = brca1_live_scores.loc[
                            brca1_live_scores['model_label'].eq(model_label) & brca1_live_scores['panel_name'].eq('brca1_same_position_adjudication')
                        ].copy()
                        threshold = float(adjudication_row['covariance_threshold'])
                        confidence_threshold = None if not math.isfinite(float(adjudication_row['covariance_confidence_threshold'])) else float(adjudication_row['covariance_confidence_threshold'])

                        if not transfer_model.empty:
                            transfer_model['chemistry_trigger'] = chemistry_trigger_from_columns(transfer_model)
                            transfer_mask = compute_rule_mask(
                                transfer_model,
                                str(adjudication_row['covariance_rule_type']),
                                threshold,
                                confidence_threshold,
                            )
                            transfer_gap = bootstrap_gap(
                                transfer_model['label'].astype(int).to_numpy(),
                                transfer_mask.to_numpy(),
                                BOOTSTRAP_REPLICATES,
                                RANDOM_SEED + 6000 + len(brca1_transfer_rows),
                            )
                            brca1_transfer_rows.append({
                                'model_label': model_label,
                                'family_label': adjudication_row['family_label'],
                                'architecture_kind': adjudication_row['architecture_kind'],
                                'n_transfer_rows': int(len(transfer_model)),
                                'n_transfer_rule_on': int(transfer_mask.sum()),
                                'transfer_rule_fraction': float(transfer_mask.mean()),
                                'transfer_enrichment_gap': transfer_gap['enrichment_gap'],
                                'transfer_auc_pair_fixed_055': safe_auc(transfer_model['label'], transfer_model['pair_rank_fixed_055']),
                                'transfer_auc_ll_rank_norm': safe_auc(transfer_model['label'], transfer_model['ll_rank_norm']),
                            })

                        if not same_position_model.empty:
                            same_position_model['chemistry_trigger'] = chemistry_trigger_from_columns(same_position_model)
                            same_position_rows_pair = same_position_top_hit_rate(same_position_model, 'pair_minus_ll')
                            same_position_rows_ll = same_position_top_hit_rate(same_position_model, 'll_rank_norm')
                            brca1_same_position_rows.append({
                                'model_label': model_label,
                                'family_label': adjudication_row['family_label'],
                                'architecture_kind': adjudication_row['architecture_kind'],
                                'n_mixed_positions': int(same_position_rows_pair['n_mixed_positions']),
                                'pair_minus_ll_top_hit_rate': same_position_rows_pair['top_hit_pathogenic_rate'],
                                'll_rank_top_hit_rate': same_position_rows_ll['top_hit_pathogenic_rate'],
                            })

                brca1_transfer_summary = pd.DataFrame(brca1_transfer_rows)
                brca1_same_position_summary = pd.DataFrame(brca1_same_position_rows)
                brca1_transfer_summary.to_csv(TABLES_DIR / 'brca1_transfer_summary.csv', index=False)
                brca1_same_position_summary.to_csv(TABLES_DIR / 'brca1_same_position_summary.csv', index=False)

                display(brca1_transfer_summary)
                display(brca1_same_position_summary)
                done('The balanced BRCA1 transfer arm, same-position adjudication panel, sequence audits, and optional live scores are written.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Final synthesis: evidence ladder, figures, nuclear claim, and the adjudication bundle
                structural_safe = tp53_structural_closure_summary.copy()
                brca1_transfer_safe = brca1_transfer_summary.copy()
                brca1_same_position_safe = brca1_same_position_summary.copy()

                final_scoreboard = tp53_covariance_adjudication.merge(
                    model_summary_12b[['model_label', 'auc_pair_fixed_055', 'delta_pair_vs_ll']],
                    on='model_label',
                    how='left',
                )
                if not structural_safe.empty:
                    final_scoreboard = final_scoreboard.merge(
                        structural_safe[['model_label', 'n_structural_rows', 'spearman_pair_minus_ll_vs_excess_local_rmsd', 'structural_geometry_gap']],
                        on='model_label',
                        how='left',
                    )
                if not brca1_transfer_safe.empty:
                    final_scoreboard = final_scoreboard.merge(
                        brca1_transfer_safe[['model_label', 'transfer_enrichment_gap']],
                        on='model_label',
                        how='left',
                    )
                if not brca1_same_position_safe.empty:
                    final_scoreboard = final_scoreboard.merge(
                        brca1_same_position_safe[['model_label', 'pair_minus_ll_top_hit_rate', 'll_rank_top_hit_rate']],
                        on='model_label',
                        how='left',
                    )

                evidence_rows = []
                for _, row in final_scoreboard.iterrows():
                    level = 0
                    if safe_float(row['covariance_enrichment_gap'], -999.0) > 0:
                        level = 1
                    if bool(row.get('same_position_advantage', False)):
                        level = max(level, 2)
                    if bool(row.get('beats_scalar_top_n_matched', False)):
                        level = max(level, 3)
                    if safe_float(row.get('transfer_enrichment_gap', float('nan')), -999.0) > 0:
                        level = max(level, 4)
                    if bool(row.get('structural_advantage', False)):
                        level = max(level, 5)
                    evidence_rows.append({
                        'model_label': row['model_label'],
                        'family_label': row['family_label'],
                        'architecture_kind': row['architecture_kind'],
                        'adjudication_status': row['adjudication_status'],
                        'highest_evidence_level': int(level),
                    })
                evidence_ladder = pd.DataFrame(evidence_rows).sort_values(['highest_evidence_level', 'model_label'], ascending=[False, True])
                evidence_ladder.to_csv(TABLES_DIR / 'tp53_evidence_ladder.csv', index=False)

                primary_nuclear = final_scoreboard.loc[final_scoreboard['adjudication_status'].eq('nuclear')].copy()
                nuclear_non_esm = primary_nuclear.loc[~primary_nuclear['family_label'].astype(str).str.startswith('esm')]
                structural_positive_count = int(
                    structural_safe.loc[
                        pd.to_numeric(structural_safe['spearman_pair_minus_ll_vs_excess_local_rmsd'], errors='coerce').fillna(-999.0)
                        > pd.to_numeric(structural_safe['spearman_ll_rank_vs_excess_local_rmsd'], errors='coerce').fillna(-999.0)
                    ].shape[0]
                ) if not structural_safe.empty else 0
                transfer_positive_count = int(
                    brca1_transfer_safe.loc[pd.to_numeric(brca1_transfer_safe['transfer_enrichment_gap'], errors='coerce').fillna(-999.0) > 0.0].shape[0]
                ) if not brca1_transfer_safe.empty else 0

                claim_status = (
                    'covariance_adjudication_supported'
                    if len(primary_nuclear) >= 2 and len(nuclear_non_esm) >= 1 and structural_positive_count >= 1 and transfer_positive_count >= 1
                    else 'covariance_adjudication_mixed'
                )
                claim_reason = (
                    'A covariance-native nuclear set now survives scalar-matched controls, same-position adjudication, structural closure, and a balanced BRCA1 transfer arm.'
                    if claim_status == 'covariance_adjudication_supported'
                    else 'The notebook strengthens the case substantially, but the covariance-native nuclear set is still too narrow or too uneven to close the claim beyond dispute.'
                )

                fig, ax = plt.subplots(figsize=(9, max(4.2, 0.45 * len(structural_safe))))
                if not structural_safe.empty:
                    structural_rank = structural_safe.sort_values('spearman_pair_minus_ll_vs_excess_local_rmsd', ascending=True)
                    ax.barh(structural_rank['model_label'], structural_rank['spearman_pair_minus_ll_vs_excess_local_rmsd'], color='#ea580c')
                    ax.set_xlabel('Spearman(pair-minus-ll, excess local RMSD)')
                    ax.set_title('Structural closure panel')
                else:
                    ax.text(0.5, 0.5, 'No structural overlap available', ha='center', va='center')
                    ax.set_axis_off()
                fig.tight_layout()
                fig.savefig(FIGURES_DIR / 'structural_closure_panel.png', dpi=220, bbox_inches='tight')
                plt.close(fig)

                if not final_scoreboard.empty:
                    scoreboard_cols = [
                        'auc_pair_fixed_055',
                        'delta_pair_vs_ll',
                        'covariance_enrichment_gap',
                        'scalar_top_n_matched_gap',
                        'spearman_pair_minus_ll_vs_excess_local_rmsd',
                        'transfer_enrichment_gap',
                    ]
                    normalized = final_scoreboard[['model_label'] + [col for col in scoreboard_cols if col in final_scoreboard.columns]].copy()
                    for column in scoreboard_cols:
                        if column not in normalized.columns:
                            normalized[column] = 0.0
                        values = pd.to_numeric(normalized[column], errors='coerce')
                        minimum = values.min(skipna=True)
                        maximum = values.max(skipna=True)
                        if pd.notna(minimum) and pd.notna(maximum) and maximum > minimum:
                            normalized[column] = (values - minimum) / (maximum - minimum)
                        else:
                            normalized[column] = values.fillna(0.0)
                    heatmap_data = normalized[scoreboard_cols].fillna(0.0).to_numpy()
                    fig, ax = plt.subplots(figsize=(10.5, max(4.2, 0.45 * len(normalized))))
                    im = ax.imshow(heatmap_data, cmap='viridis', aspect='auto')
                    ax.set_xticks(range(len(scoreboard_cols)))
                    ax.set_xticklabels(scoreboard_cols, rotation=30, ha='right')
                    ax.set_yticks(range(len(normalized)))
                    ax.set_yticklabels(normalized['model_label'])
                    ax.set_title('Covariance adjudication scoreboard')
                    fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
                    fig.tight_layout()
                    fig.savefig(FIGURES_DIR / 'covariance_adjudication_scoreboard.png', dpi=220, bbox_inches='tight')
                    plt.close(fig)

                fig, ax = plt.subplots(figsize=(9, max(4.2, 0.45 * max(1, len(brca1_transfer_safe)))))
                if not brca1_transfer_safe.empty:
                    transfer_rank = brca1_transfer_safe.sort_values('transfer_enrichment_gap', ascending=True)
                    ax.barh(transfer_rank['model_label'], transfer_rank['transfer_enrichment_gap'], color='#0f766e')
                    ax.set_xlabel('Transfer enrichment gap')
                    ax.set_title('BRCA1 transfer panel')
                    ax.axvline(0.0, color='black', linewidth=1, linestyle='--')
                else:
                    ax.text(0.5, 0.5, 'BRCA1 transfer not executed', ha='center', va='center')
                    ax.set_axis_off()
                fig.tight_layout()
                fig.savefig(FIGURES_DIR / 'brca1_transfer_panel.png', dpi=220, bbox_inches='tight')
                plt.close(fig)

                if not evidence_ladder.empty:
                    fig, ax = plt.subplots(figsize=(8.5, max(4.0, 0.42 * len(evidence_ladder))))
                    ax.barh(evidence_ladder['model_label'], evidence_ladder['highest_evidence_level'], color='#1d4ed8')
                    ax.set_xlabel('Highest evidence level reached')
                    ax.set_title('Evidence ladder')
                    fig.tight_layout()
                    fig.savefig(FIGURES_DIR / 'evidence_ladder_panel.png', dpi=220, bbox_inches='tight')
                    plt.close(fig)

                summary_payload = {
                    'notebook_slug': NOTEBOOK_SLUG,
                    'run_at_utc': RUN_AT,
                    'account_label': ACCOUNT_LABEL,
                    'claim_status': claim_status,
                    'claim_reason': claim_reason,
                    'n_models_adjudicated': int(final_scoreboard.shape[0]),
                    'n_nuclear_models': int(primary_nuclear.shape[0]),
                    'n_supportive_models': int(final_scoreboard['adjudication_status'].eq('supportive').sum()) if not final_scoreboard.empty else 0,
                    'n_non_esm_nuclear_models': int(nuclear_non_esm.shape[0]),
                    'structural_positive_models': structural_positive_count,
                    'transfer_positive_models': transfer_positive_count,
                    'structural_source_kind': structural_source_kind,
                    'structural_source_path': structural_source_path,
                    'best_nuclear_model': str(primary_nuclear.sort_values('covariance_enrichment_gap', ascending=False).iloc[0]['model_label']) if not primary_nuclear.empty else 'none',
                }

                response_md = '\\n'.join([
                    '# Block 12C Covariance Adjudication Summary',
                    '',
                    f"- Claim status: `{summary_payload['claim_status']}`",
                    f"- Nuclear models: `{summary_payload['n_nuclear_models']}`",
                    f"- Supportive models: `{summary_payload['n_supportive_models']}`",
                    f"- Non-ESM nuclear models: `{summary_payload['n_non_esm_nuclear_models']}`",
                    f"- Structural-positive models: `{summary_payload['structural_positive_models']}`",
                    f"- Transfer-positive models: `{summary_payload['transfer_positive_models']}`",
                    f"- Best nuclear model: `{summary_payload['best_nuclear_model']}`",
                    '',
                    '## Interpretation',
                    '',
                    'This notebook does not ask whether multifamily signal exists at all. It asks whether a covariance-native claim survives once the scalar escape hatch is fenced off, the structural layer is forced shut, and a balanced BRCA1 transfer arm is brought into the same courtroom.',
                ])

                claim_paragraph = (
                    'The claim is now anchored to a nuclear set rather than to the broadest possible roster. In that nuclear set, covariance-native rules survive scalar-matched controls, maintain same-position advantage, align more cleanly with orthogonal structural perturbation, and transfer beyond TP53 into a balanced BRCA1 panel.'
                    if claim_status == 'covariance_adjudication_supported'
                    else 'The adjudication notebook meaningfully strengthens the case, especially by closing the structural layer and replacing the weak transfer panel. But the covariance-native nuclear set remains limited enough that the final paper claim should stay bounded and explicit about where the rescue truly holds.'
                )

                (MANIFESTS_DIR / 'block12c_covariance_adjudication_summary.json').write_text(json.dumps(summary_payload, indent=2), encoding='utf-8')
                (MANIFESTS_DIR / 'artifact_summary.json').write_text(json.dumps(summary_payload, indent=2), encoding='utf-8')
                (TEXT_DIR / 'block12c_covariance_adjudication_summary.md').write_text(response_md + '\\n', encoding='utf-8')
                (TEXT_DIR / 'block12c_claim_paragraph.md').write_text(claim_paragraph + '\\n', encoding='utf-8')

                if ZIP_PATH.exists():
                    ZIP_PATH.unlink()
                with zipfile.ZipFile(ZIP_PATH, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
                    for folder in [TABLES_DIR, FIGURES_DIR, TEXT_DIR, MANIFESTS_DIR, RUNTIME_DIR, LIVE_SCORES_DIR]:
                        for file_path in folder.rglob('*'):
                            if file_path.is_file():
                                archive.write(file_path, arcname=str(file_path.relative_to(RESULTS_ROOT)))

                print(json.dumps(summary_payload, indent=2))
                display(final_scoreboard)
                display(evidence_ladder)
                done('Figures, evidence ladder, markdown summaries, manifests, and the final adjudication bundle are written.')
                """
            )
        ),
    ]
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3.11",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    notebook = build_notebook()
    output_path = repo_root / "New Notebooks" / "12c_block12_covariance_adjudication_structural_closure_h100.ipynb"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(notebook, indent=2), encoding="utf-8")
    print(f"Wrote notebook to {output_path}")


if __name__ == "__main__":
    main()
