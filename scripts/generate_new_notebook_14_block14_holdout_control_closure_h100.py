from __future__ import annotations

import json
from pathlib import Path

from generate_new_notebook_12b_block12_multifamily_coverage_aware_generalization_h100 import (
    code_cell,
    dedent,
    markdown_cell,
)


def build_notebook() -> dict:
    cells: list[dict] = [
        markdown_cell(
            "# Experiment: SpectralBio Block 14 - Holdout and Control Closure (H100)\n\n"
            "Objective:\n"
            "- Treat Block 14 as a **surgical closure court** for the two remaining Block 13 firewalls: `holdout-positive` and `control win`.\n"
            "- Repair the two known pathologies from Block 13:\n"
            "  1. the degenerate witness-only holdout with no benign rows,\n"
            "  2. the self-blocking control logic that compared `pair_only` against itself.\n"
            "- Reuse Block 13 replay-ready surfaces first, then score only the minimum additional model-target pairs needed to produce a defensible closure verdict.\n"
            "- Produce a reviewer-facing package under `New Notebooks/results/14_block14_holdout_control_closure_h100/` with tables, figures, manifests, markdown claim files, and a zip bundle.\n"
        ),
        markdown_cell(
            "## Final Contract\n\n"
            "- Block 13 already strengthened portability, but it did **not** close the final two firewalls.\n"
            "- Block 14 fixes those firewalls instead of pretending they were fine:\n"
            "  - holdout is rebuilt from **full labeled replay-ready target panels** rather than from a witness-only subset,\n"
            "  - control wins are tested against **meaningful alternative controls** without self-comparisons.\n"
            "- Calibration anchor: `TP53`\n"
            "- Positive holdout targets: `TSC2`, `CREBBP`\n"
            "- Negative guardrails: `BRCA1`, `MSH2`\n"
            "- Optional consistency-only target: `BRCA2`\n"
            "- Focused model roster:\n"
            "  - `ProtT5`\n"
            "  - `ProGen2-small`\n"
            "  - `ESM2-650M`\n"
            "  - `ESM2-150M`\n"
            "  - `ESM-1v`\n"
            "- Exact closure rule:\n"
            "  - `>=1 holdout_positive_model`\n"
            "  - `>=1 control_win_model`\n"
            "  - `>=1 non-ESM transfer_positive_model`\n"
            "  - `BRCA1` and `MSH2` remain negative guardrails\n"
            "- The notebook is allowed to conclude that closure is still mixed. It is **not** allowed to hide where it failed.\n"
        ),
        code_cell(
            dedent(
                """
                # Setup: imports, runtime requirements, notebook identifiers, hotfixes, and focused knobs
                from __future__ import annotations

                import importlib
                import importlib.util
                import json
                import math
                import os
                import platform
                import random
                import shutil
                import subprocess
                import sys
                import zipfile
                from datetime import datetime, timezone
                from pathlib import Path

                os.environ.setdefault('DISABLE_TRANSFORMERS_AV', '1')
                os.environ.setdefault('TRANSFORMERS_NO_TORCHVISION', '1')

                NOTEBOOK_SLUG = '14_block14_holdout_control_closure_h100'
                ACCOUNT_LABEL = os.environ.get('SPECTRALBIO_ACCOUNT_LABEL', 'local_run')
                RUN_AT = datetime.now(timezone.utc).isoformat()
                OVERWRITE = os.environ.get('SPECTRALBIO_OVERWRITE', '').strip().lower() in {'1', 'true', 'yes'}
                SKIP_LIVE = os.environ.get('SPECTRALBIO_BLOCK14_SKIP_LIVE', '').strip().lower() in {'1', 'true', 'yes'}
                MODEL_FILTER = {
                    item.strip().lower()
                    for item in os.environ.get('SPECTRALBIO_BLOCK14_MODEL_FILTER', '').split(',')
                    if item.strip()
                }
                TARGET_FILTER = {
                    item.strip().upper()
                    for item in os.environ.get('SPECTRALBIO_BLOCK14_TARGET_FILTER', '').split(',')
                    if item.strip()
                }
                FIXED_ALPHA = float(os.environ.get('SPECTRALBIO_BLOCK14_FIXED_ALPHA', '0.55'))
                ALPHA_GRID = [
                    float(item.strip())
                    for item in os.environ.get('SPECTRALBIO_BLOCK14_ALPHA_GRID', '0.05,0.10,0.15,0.20,0.25,0.30,0.35,0.40,0.45,0.50,0.55,0.60,0.65,0.70,0.75,0.80,0.85,0.90,0.95').split(',')
                    if item.strip()
                ]
                RULE_THRESHOLDS = [0.05, 0.10, 0.15, 0.20, 0.25]
                CONFIDENCE_THRESHOLDS = [0.55, 0.60, 0.65]
                BOOTSTRAP_REPLICATES = int(os.environ.get('SPECTRALBIO_BLOCK14_BOOTSTRAP_REPLICATES', '2000'))
                RANDOM_REPLICATES = int(os.environ.get('SPECTRALBIO_BLOCK14_RANDOM_REPLICATES', '400'))
                RANDOM_SEED = int(os.environ.get('SPECTRALBIO_BLOCK14_RANDOM_SEED', '42'))
                WINDOW_RADIUS = int(os.environ.get('SPECTRALBIO_BLOCK14_WINDOW_RADIUS', '40'))
                CHECKPOINT_EVERY = int(os.environ.get('SPECTRALBIO_BLOCK14_CHECKPOINT_EVERY', '10'))
                MIN_RULE_ON_ABS = 10
                MIN_RULE_ON_FRAC = 0.05
                HOLDOUT_MAX_RULE_ON_FRAC = 0.60

                MODEL_SPECS = [
                    {
                        'model_name': 'Rostlab/prot_t5_xl_half_uniref50-enc',
                        'model_label': 'ProtT5',
                        'family_label': 'prottrans',
                        'architecture_kind': 'encoder_decoder',
                        'adapter_kind': 't5',
                        'sequence_mode': 'spaced',
                        'scale_bucket': 'xl',
                        'priority_rank': 1,
                    },
                    {
                        'model_name': 'hugohrban/progen2-small',
                        'model_label': 'ProGen2-small',
                        'family_label': 'progen',
                        'architecture_kind': 'causal_decoder',
                        'adapter_kind': 'causal',
                        'sequence_mode': 'raw',
                        'scale_bucket': 'small',
                        'priority_rank': 2,
                    },
                    {
                        'model_name': 'facebook/esm2_t33_650M_UR50D',
                        'model_label': 'ESM2-650M',
                        'family_label': 'esm',
                        'architecture_kind': 'masked_encoder',
                        'adapter_kind': 'esm',
                        'sequence_mode': 'raw',
                        'scale_bucket': '650M',
                        'priority_rank': 3,
                    },
                    {
                        'model_name': 'facebook/esm2_t30_150M_UR50D',
                        'model_label': 'ESM2-150M',
                        'family_label': 'esm',
                        'architecture_kind': 'masked_encoder',
                        'adapter_kind': 'esm',
                        'sequence_mode': 'raw',
                        'scale_bucket': '150M',
                        'priority_rank': 4,
                    },
                    {
                        'model_name': 'facebook/esm1v_t33_650M_UR90S_1',
                        'model_label': 'ESM-1v',
                        'family_label': 'esm_variant_specialist',
                        'architecture_kind': 'masked_encoder',
                        'adapter_kind': 'esm',
                        'sequence_mode': 'raw',
                        'scale_bucket': '650M',
                        'priority_rank': 5,
                    },
                ]

                TARGET_SPECS = [
                    {'gene': 'TP53', 'role': 'calibration_anchor', 'is_negative_control': False},
                    {'gene': 'TSC2', 'role': 'positive_holdout', 'is_negative_control': False},
                    {'gene': 'CREBBP', 'role': 'positive_holdout', 'is_negative_control': False},
                    {'gene': 'BRCA1', 'role': 'negative_holdout', 'is_negative_control': True},
                    {'gene': 'MSH2', 'role': 'negative_holdout', 'is_negative_control': True},
                    {'gene': 'BRCA2', 'role': 'consistency_only', 'is_negative_control': False},
                ]

                if MODEL_FILTER:
                    MODEL_SPECS = [
                        spec for spec in MODEL_SPECS
                        if spec['model_label'].strip().lower() in MODEL_FILTER
                        or spec['family_label'].strip().lower() in MODEL_FILTER
                    ]

                if TARGET_FILTER:
                    TARGET_SPECS = [spec for spec in TARGET_SPECS if spec['gene'] in TARGET_FILTER]

                REQUIRED_PACKAGES = {
                    'packaging': 'packaging>=24',
                    'numpy': 'numpy==2.1.3',
                    'scipy': 'scipy==1.14.1',
                    'sklearn': 'scikit-learn==1.5.2',
                    'transformers': 'transformers==4.49.0',
                    'torch': 'torch>=2.5,<3',
                    'pandas': 'pandas>=2.2',
                    'matplotlib': 'matplotlib>=3.9',
                    'requests': 'requests>=2.32',
                    'accelerate': 'accelerate>=1.0',
                    'sentencepiece': 'sentencepiece>=0.2',
                    'safetensors': 'safetensors>=0.4',
                    'google.protobuf': 'protobuf>=5',
                    'einops': 'einops>=0.8',
                }

                missing_specs = []
                for module_name, requirement in REQUIRED_PACKAGES.items():
                    if importlib.util.find_spec(module_name) is None:
                        missing_specs.append(requirement)

                if missing_specs:
                    subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', *missing_specs], check=True)

                import numpy as np
                import pandas as pd
                import matplotlib.pyplot as plt
                from IPython.display import display

                def done(message: str) -> None:
                    print(f'[DONE] {message}')

                runtime_rows = []
                for module_name in ['packaging', 'numpy', 'pandas', 'matplotlib', 'scipy', 'sklearn', 'requests', 'transformers', 'torch']:
                    module = importlib.import_module(module_name)
                    runtime_rows.append({'package': module_name, 'version': getattr(module, '__version__', 'unknown')})
                runtime_rows.append({'package': 'python', 'version': sys.version.split()[0]})
                runtime_rows.append({'package': 'platform', 'version': platform.platform()})

                random.seed(RANDOM_SEED)
                np.random.seed(RANDOM_SEED)

                display(pd.DataFrame(runtime_rows))
                done('Environment, focused roster, runtime knobs, and dependency checks are ready.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Helpers: repo wiring, score reuse, statistics, rule logic, and focused model scoring
                import gc
                import re

                def ensure_dir(path: Path) -> Path:
                    path.mkdir(parents=True, exist_ok=True)
                    return path

                def looks_like_repo(path: Path) -> bool:
                    return (path / 'src' / 'spectralbio').exists() and (path / 'New Notebooks').exists()

                def find_repo_root() -> Path:
                    env_repo = os.environ.get('SPECTRALBIO_REPO_ROOT', '').strip()
                    candidates = []
                    if env_repo:
                        candidates.append(Path(env_repo).expanduser())
                    cwd = Path.cwd().resolve()
                    candidates.extend([cwd, cwd.parent, Path('/teamspace/studios/this_studio/Stanford-Claw4s'), Path('/content/Stanford-Claw4s')])
                    for candidate in candidates:
                        if looks_like_repo(candidate):
                            return candidate.resolve()
                    raise FileNotFoundError('Could not locate repo root. Set SPECTRALBIO_REPO_ROOT if needed.')

                def resolve_existing_path(*candidates: str | Path) -> Path:
                    repo_root = find_repo_root()
                    for raw in candidates:
                        raw_path = Path(raw)
                        if raw_path.exists():
                            return raw_path.resolve()
                        raw_text = str(raw).replace('\\\\', '/')
                        for prefix in ('/content/Stanford-Claw4s/', '/teamspace/studios/this_studio/Stanford-Claw4s/'):
                            if raw_text.startswith(prefix):
                                candidate = repo_root / raw_text[len(prefix):]
                                if candidate.exists():
                                    return candidate.resolve()
                        if 'Stanford-Claw4s/' in raw_text:
                            candidate = repo_root / raw_text.split('Stanford-Claw4s/', 1)[1]
                            if candidate.exists():
                                return candidate.resolve()
                        if not raw_path.is_absolute():
                            candidate = (repo_root / raw_path).resolve()
                            if candidate.exists():
                                return candidate
                    raise FileNotFoundError('None of the candidate paths exist: ' + ' | '.join(str(candidate) for candidate in candidates))

                def safe_float(value, default: float = float('nan')) -> float:
                    try:
                        if value is None:
                            return float(default)
                        if isinstance(value, str) and not value.strip():
                            return float(default)
                        return float(value)
                    except Exception:
                        return float(default)

                def coverage_floor(n_rows: int) -> int:
                    return int(max(MIN_RULE_ON_ABS, math.ceil(float(n_rows) * MIN_RULE_ON_FRAC)))

                def bootstrap_gap(labels: np.ndarray, mask: np.ndarray, replicates: int, seed: int) -> dict[str, float]:
                    labels = np.asarray(labels, dtype=int)
                    mask = np.asarray(mask, dtype=bool)
                    on_values = labels[mask]
                    off_values = labels[~mask]
                    if len(on_values) == 0 or len(off_values) == 0:
                        return {
                            'pathogenic_fraction_rule_on': float('nan'),
                            'pathogenic_fraction_rule_off': float('nan'),
                            'enrichment_gap': float('nan'),
                            'gap_ci_low': float('nan'),
                            'gap_ci_high': float('nan'),
                        }
                    rng = np.random.default_rng(seed)
                    draws = []
                    for _ in range(int(replicates)):
                        draw_on = rng.choice(on_values, size=len(on_values), replace=True)
                        draw_off = rng.choice(off_values, size=len(off_values), replace=True)
                        draws.append(float(np.mean(draw_on) - np.mean(draw_off)))
                    draws = np.asarray(draws, dtype=float)
                    return {
                        'pathogenic_fraction_rule_on': float(np.mean(on_values)),
                        'pathogenic_fraction_rule_off': float(np.mean(off_values)),
                        'enrichment_gap': float(np.mean(on_values) - np.mean(off_values)),
                        'gap_ci_low': float(np.quantile(draws, 0.025)),
                        'gap_ci_high': float(np.quantile(draws, 0.975)),
                    }

                def odds_ratio_from_mask(labels: np.ndarray, mask: np.ndarray) -> dict[str, float]:
                    labels = np.asarray(labels, dtype=int)
                    mask = np.asarray(mask, dtype=bool)
                    a = int(np.sum((labels == 1) & mask))
                    b = int(np.sum((labels == 0) & mask))
                    c = int(np.sum((labels == 1) & (~mask)))
                    d = int(np.sum((labels == 0) & (~mask)))
                    numerator = (a + 0.5) * (d + 0.5)
                    denominator = (b + 0.5) * (c + 0.5)
                    return {
                        'positive_with_rule': a,
                        'negative_with_rule': b,
                        'positive_without_rule': c,
                        'negative_without_rule': d,
                        'odds_ratio': float(numerator / denominator),
                    }

                def random_coverage_matched_gap(labels: np.ndarray, n_rule_on: int, replicates: int, seed: int) -> dict[str, float]:
                    labels = np.asarray(labels, dtype=int)
                    if n_rule_on <= 0 or n_rule_on >= len(labels):
                        return {
                            'random_gap_mean': float('nan'),
                            'random_gap_p95': float('nan'),
                            'random_gap_p05': float('nan'),
                        }
                    rng = np.random.default_rng(seed)
                    draws = []
                    for _ in range(int(replicates)):
                        chosen = np.zeros(len(labels), dtype=bool)
                        chosen[rng.choice(len(labels), size=n_rule_on, replace=False)] = True
                        draws.append(float(np.mean(labels[chosen]) - np.mean(labels[~chosen])))
                    draws = np.asarray(draws, dtype=float)
                    return {
                        'random_gap_mean': float(np.mean(draws)),
                        'random_gap_p95': float(np.quantile(draws, 0.95)),
                        'random_gap_p05': float(np.quantile(draws, 0.05)),
                    }

                AA_BUCKETS = {
                    'A': 'small_hydrophobic', 'V': 'small_hydrophobic',
                    'I': 'large_hydrophobic', 'L': 'large_hydrophobic', 'M': 'large_hydrophobic',
                    'F': 'aromatic', 'Y': 'aromatic', 'W': 'aromatic',
                    'S': 'polar', 'T': 'polar', 'N': 'polar', 'Q': 'polar',
                    'C': 'sulfur', 'G': 'glycine', 'P': 'proline',
                    'H': 'basic', 'K': 'basic', 'R': 'basic',
                    'D': 'acidic', 'E': 'acidic',
                }

                def aa_bucket(value: str) -> str:
                    return AA_BUCKETS.get(str(value).strip().upper(), 'other')

                def chemistry_trigger_from_columns(frame: pd.DataFrame) -> pd.Series:
                    wt = frame['wt_aa'].astype(str).str.upper().map(aa_bucket)
                    mut = frame['mut_aa'].astype(str).str.upper().map(aa_bucket)
                    pair_minus_ll = pd.to_numeric(frame.get('pair_minus_ll', pd.Series(index=frame.index, dtype=float)), errors='coerce').fillna(-999.0)
                    return wt.ne(mut) & (pair_minus_ll > 0.0)

                def normalize_protein_sequence(sequence: str, sequence_mode: str) -> str:
                    normalized = re.sub(r'[^A-Za-z]', '', str(sequence).upper())
                    if sequence_mode == 'spaced':
                        return ' '.join(list(normalized))
                    return normalized

                def maybe_import_reject_recovery():
                    global _alpha_sweep_on_rows, _ensure_gene_score_rows, _pair_scores, covariance_features_dual
                    from spectralbio.supplementary.reject_recovery import (
                        _alpha_sweep_on_rows,
                        _ensure_gene_score_rows,
                        _pair_scores,
                        covariance_features_dual,
                    )
                    return True

                REPO_ROOT = find_repo_root()
                sys.path.insert(0, str(REPO_ROOT / 'src'))
                maybe_import_reject_recovery()

                RESULTS_ROOT = ensure_dir(REPO_ROOT / 'New Notebooks' / 'results' / NOTEBOOK_SLUG)
                TABLES_DIR = ensure_dir(RESULTS_ROOT / 'tables')
                FIGURES_DIR = ensure_dir(RESULTS_ROOT / 'figures')
                TEXT_DIR = ensure_dir(RESULTS_ROOT / 'text')
                MANIFESTS_DIR = ensure_dir(RESULTS_ROOT / 'manifests')
                RUNTIME_DIR = ensure_dir(RESULTS_ROOT / 'runtime')
                LIVE_SCORES_DIR = ensure_dir(RESULTS_ROOT / 'live_scores')
                BUNDLE_DIR = ensure_dir(REPO_ROOT / 'New Notebooks' / 'results' / f'{NOTEBOOK_SLUG}_bundle')
                ZIP_PATH = RESULTS_ROOT / f'{NOTEBOOK_SLUG}_bundle.zip'

                BLOCK13_ROOT = resolve_existing_path(REPO_ROOT / 'New Notebooks' / 'results' / '13_block13_multitarget_generalization_closure_h100')
                BLOCK12B_ROOT = resolve_existing_path(REPO_ROOT / 'New Notebooks' / 'results' / '12b_block12_multifamily_coverage_aware_generalization_h100')
                BLOCK10B_ROOT = resolve_existing_path(REPO_ROOT / 'New Notebooks' / 'results' / '10b_block7c_alpha_crossfamily_finalists_h100')
                BLOCK08_ROOT = resolve_existing_path(REPO_ROOT / 'New Notebooks' / 'results' / '08_block7_turbo_gallery_rescues_h100')

                def safe_model_dir(model_name: str) -> str:
                    return model_name.replace('/', '_').replace('-', '_')

                def score_output_path(model_name: str, gene: str) -> Path:
                    return ensure_dir(LIVE_SCORES_DIR / safe_model_dir(model_name)) / f"{gene.lower()}_{safe_model_dir(model_name)}_scores.csv"

                def metadata_output_path(model_name: str, gene: str) -> Path:
                    return ensure_dir(LIVE_SCORES_DIR / safe_model_dir(model_name)) / f"{gene.lower()}_{safe_model_dir(model_name)}_metadata.json"

                def reuse_candidates(model_name: str, gene: str) -> list[Path]:
                    file_name = f"{gene.lower()}_{safe_model_dir(model_name)}_scores.csv"
                    return [
                        BLOCK12B_ROOT / 'live_scores' / safe_model_dir(model_name) / file_name,
                        BLOCK13_ROOT / 'live_scores' / safe_model_dir(model_name) / file_name,
                    ]

                def has_expected_coverage(frame: pd.DataFrame, expected_variant_ids: set[str]) -> bool:
                    observed = set(frame.get('variant_id', pd.Series(dtype=str)).astype(str))
                    return bool(expected_variant_ids) and expected_variant_ids.issubset(observed)

                def reuse_exact_scores(model_name: str, gene: str, expected_variant_ids: set[str]) -> tuple[pd.DataFrame, dict] | tuple[None, None]:
                    for candidate in reuse_candidates(model_name, gene):
                        if candidate.exists():
                            frame = pd.read_csv(candidate)
                            if not has_expected_coverage(frame, expected_variant_ids):
                                continue
                            return frame, {'reuse_source': str(candidate), 'reuse_kind': 'exact_live_score'}
                    return None, None

                def clear_modules(prefixes: tuple[str, ...]) -> None:
                    stale = [name for name in list(sys.modules) if any(name == prefix or name.startswith(prefix + '.') for prefix in prefixes)]
                    for name in stale:
                        sys.modules.pop(name, None)

                def apply_transformers_torchvision_hotfix() -> None:
                    clear_modules(('transformers', 'torchvision'))
                    os.environ['DISABLE_TRANSFORMERS_AV'] = '1'
                    os.environ['TRANSFORMERS_NO_TORCHVISION'] = '1'
                    import importlib.machinery
                    import types

                    stub = types.ModuleType('torchvision')
                    stub.__spec__ = importlib.machinery.ModuleSpec('torchvision', loader=None)
                    transforms = types.ModuleType('torchvision.transforms')
                    transforms.__spec__ = importlib.machinery.ModuleSpec('torchvision.transforms', loader=None)
                    io = types.ModuleType('torchvision.io')
                    io.__spec__ = importlib.machinery.ModuleSpec('torchvision.io', loader=None)
                    datasets = types.ModuleType('torchvision.datasets')
                    datasets.__spec__ = importlib.machinery.ModuleSpec('torchvision.datasets', loader=None)
                    models = types.ModuleType('torchvision.models')
                    models.__spec__ = importlib.machinery.ModuleSpec('torchvision.models', loader=None)
                    ops = types.ModuleType('torchvision.ops')
                    ops.__spec__ = importlib.machinery.ModuleSpec('torchvision.ops', loader=None)
                    utils = types.ModuleType('torchvision.utils')
                    utils.__spec__ = importlib.machinery.ModuleSpec('torchvision.utils', loader=None)
                    interpolation = type(
                        'InterpolationMode',
                        (),
                        {
                            'NEAREST': 'nearest',
                            'NEAREST_EXACT': 'nearest_exact',
                            'BILINEAR': 'bilinear',
                            'BICUBIC': 'bicubic',
                            'BOX': 'box',
                            'HAMMING': 'hamming',
                            'LANCZOS': 'lanczos',
                        },
                    )
                    transforms.InterpolationMode = interpolation
                    stub.transforms = transforms
                    stub.io = io
                    stub.datasets = datasets
                    stub.models = models
                    stub.ops = ops
                    stub.utils = utils
                    sys.modules['torchvision'] = stub
                    sys.modules['torchvision.transforms'] = transforms
                    sys.modules['torchvision.io'] = io
                    sys.modules['torchvision.datasets'] = datasets
                    sys.modules['torchvision.models'] = models
                    sys.modules['torchvision.ops'] = ops
                    sys.modules['torchvision.utils'] = utils

                apply_transformers_torchvision_hotfix()
                import torch
                from transformers import AutoModel, AutoModelForCausalLM, AutoTokenizer, T5EncoderModel, T5Tokenizer

                def load_model_bundle(spec: dict) -> tuple[dict | None, dict]:
                    manifest = {
                        'model_label': spec['model_label'],
                        'model_name': spec['model_name'],
                        'family_label': spec['family_label'],
                        'architecture_kind': spec['architecture_kind'],
                        'adapter_kind': spec['adapter_kind'],
                        'status': 'not_loaded',
                    }
                    device = 'cuda' if torch.cuda.is_available() else 'cpu'
                    torch_dtype = torch.float16 if device == 'cuda' else torch.float32
                    try:
                        if spec['adapter_kind'] == 't5':
                            tokenizer = T5Tokenizer.from_pretrained(spec['model_name'], do_lower_case=False, legacy=True)
                            model = T5EncoderModel.from_pretrained(
                                spec['model_name'],
                                torch_dtype=torch_dtype,
                                low_cpu_mem_usage=True,
                            ).to(device).eval()
                        elif spec['adapter_kind'] == 'causal':
                            tokenizer = AutoTokenizer.from_pretrained(spec['model_name'], trust_remote_code=True)
                            if tokenizer.pad_token is None:
                                tokenizer.pad_token = tokenizer.eos_token
                            model = AutoModelForCausalLM.from_pretrained(
                                spec['model_name'],
                                torch_dtype=torch_dtype,
                                low_cpu_mem_usage=True,
                                trust_remote_code=True,
                            ).to(device).eval()
                        else:
                            tokenizer = AutoTokenizer.from_pretrained(spec['model_name'], trust_remote_code=True)
                            model = AutoModel.from_pretrained(
                                spec['model_name'],
                                torch_dtype=torch_dtype,
                                low_cpu_mem_usage=True,
                                trust_remote_code=True,
                            ).to(device).eval()
                        manifest.update({'status': 'loaded', 'device': device, 'torch_dtype': str(torch_dtype)})
                        return {'tokenizer': tokenizer, 'model': model, 'device': device}, manifest
                    except Exception as exc:
                        manifest.update({'status': 'load_failed', 'error_type': type(exc).__name__, 'error_message': str(exc)[:500]})
                        return None, manifest

                def encode_sequence(bundle: dict, sequence: str, sequence_mode: str) -> dict:
                    tokenizer = bundle['tokenizer']
                    device = bundle['device']
                    encoded = tokenizer(
                        normalize_protein_sequence(sequence, sequence_mode),
                        return_tensors='pt',
                        add_special_tokens=False,
                    )
                    return {key: value.to(device) for key, value in encoded.items()}

                def stack_hidden_states(outputs, residue_count: int) -> np.ndarray:
                    hidden_states = getattr(outputs, 'hidden_states', None)
                    if hidden_states is None:
                        hidden_states = getattr(outputs, 'encoder_hidden_states', None)
                    if hidden_states is None:
                        raise RuntimeError('Model output does not expose hidden states.')
                    layers = [layer[0, :residue_count, :].detach().cpu().float().numpy() for layer in hidden_states[1:]]
                    return np.stack(layers, axis=0)

                def generic_hidden_forward(bundle: dict, spec: dict, encoded: dict):
                    model = bundle['model']
                    if spec['adapter_kind'] == 'causal':
                        return model(**encoded, output_hidden_states=True, use_cache=False)
                    return model(**encoded, output_hidden_states=True)

                def score_panel_with_generic_model(panel_df: pd.DataFrame, sequence_map: dict[str, str], spec: dict, output_path: Path) -> tuple[pd.DataFrame, dict]:
                    expected_variant_ids = set(panel_df['variant_id'].astype(str))
                    if output_path.exists() and not OVERWRITE:
                        reused = pd.read_csv(output_path)
                        if has_expected_coverage(reused, expected_variant_ids):
                            return reused, {'status': 'reused_existing_scores', 'n_rows': int(len(reused)), 'model_label': spec['model_label']}
                        output_path.unlink(missing_ok=True)

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
                                    raise RuntimeError(f'Tokenization mismatch for {spec["model_label"]}: expected {len(local_sequence)}, got {token_count}')
                                with torch.inference_mode():
                                    wt_outputs = generic_hidden_forward(bundle, spec, wt_encoded)
                                wt_cache[wt_key] = stack_hidden_states(wt_outputs, len(local_sequence))

                            wt_hidden = wt_cache[wt_key]
                            mutated_local = local_sequence[:local_pos] + mut_aa + local_sequence[local_pos + 1:]
                            mut_encoded = encode_sequence(bundle, mutated_local, spec['sequence_mode'])
                            mut_token_count = int(mut_encoded['input_ids'].shape[1])
                            if mut_token_count != len(mutated_local):
                                raise RuntimeError(f'Mut tokenization mismatch for {spec["model_label"]}: expected {len(mutated_local)}, got {mut_token_count}')
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
                                'model_label': spec['model_label'],
                                'family_label': spec['family_label'],
                                'architecture_kind': spec['architecture_kind'],
                                'adapter_kind': spec['adapter_kind'],
                                'sequence_mode': spec['sequence_mode'],
                                'scale_bucket': spec['scale_bucket'],
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
                        manifest.update({'status': 'partial_failure' if not partial.empty else 'scoring_failed', 'n_rows': int(len(partial)), 'error_type': type(exc).__name__, 'error_message': str(exc)[:500]})
                        return partial, manifest
                    finally:
                        try:
                            del bundle['model']
                        except Exception:
                            pass
                        gc.collect()
                        if torch.cuda.is_available():
                            torch.cuda.empty_cache()

                def score_panel_with_model(panel_df: pd.DataFrame, sequence_map: dict[str, str], spec: dict, output_path: Path) -> tuple[pd.DataFrame, dict]:
                    expected_variant_ids = set(panel_df['variant_id'].astype(str))
                    if spec['adapter_kind'] == 'esm':
                        if output_path.exists() and not OVERWRITE:
                            reused = pd.read_csv(output_path)
                            if has_expected_coverage(reused, expected_variant_ids):
                                return reused, {'status': 'reused_existing_scores', 'n_rows': int(len(reused)), 'model_label': spec['model_label'], 'adapter_kind': 'esm'}
                            output_path.unlink(missing_ok=True)
                        grouped_rows = []
                        for gene, gene_df in panel_df.groupby('gene', sort=False):
                            gene_key = str(gene).upper()
                            if gene_key not in sequence_map:
                                raise KeyError(f'Missing sequence for gene {gene_key}.')
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
                        if not output.empty:
                            output['model_name'] = spec['model_name']
                            output['model_label'] = spec['model_label']
                            output['family_label'] = spec['family_label']
                            output['architecture_kind'] = spec['architecture_kind']
                            output['adapter_kind'] = spec['adapter_kind']
                            output['sequence_mode'] = spec['sequence_mode']
                            output['scale_bucket'] = spec['scale_bucket']
                        output.to_csv(output_path, index=False)
                        return output, {'status': 'completed', 'n_rows': int(len(output)), 'model_label': spec['model_label'], 'adapter_kind': 'esm'}
                    return score_panel_with_generic_model(panel_df, sequence_map, spec, output_path)

                def ensure_rank_features(frame: pd.DataFrame, alpha: float) -> pd.DataFrame:
                    working = frame.copy()
                    required = {'ll_rank_norm', 'frob_rank_norm', 'pair_rank_fixed_055', 'pair_minus_ll'}
                    need_recompute = not required.issubset(set(working.columns))
                    if not need_recompute:
                        finite_counts = []
                        for column in ['ll_rank_norm', 'frob_rank_norm', 'pair_rank_fixed_055', 'pair_minus_ll']:
                            finite_counts.append(int(np.isfinite(pd.to_numeric(working[column], errors='coerce')).sum()))
                        need_recompute = min(finite_counts) == 0
                    if need_recompute:
                        rows = working[['gene', 'name', 'position', 'wt_aa', 'mut_aa', 'label', 'frob_dist', 'trace_ratio', 'sps_log', 'll_proper', 'model_name', 'variant_id']].to_dict(orient='records')
                        payload = _pair_scores(rows, alpha)
                        working['ll_rank_norm'] = payload['ll_norm']
                        working['frob_rank_norm'] = payload['frob_norm']
                        working['pair_rank_fixed_055'] = payload['pair']
                    working['pair_minus_ll'] = pd.to_numeric(working['pair_rank_fixed_055'], errors='coerce') - pd.to_numeric(working['ll_rank_norm'], errors='coerce')
                    if 'chemistry_trigger' not in working.columns:
                        working['chemistry_trigger'] = chemistry_trigger_from_columns(working)
                    return working

                def compute_rule_mask(frame: pd.DataFrame, rule_type: str, threshold: float, confidence_threshold: float | None = None) -> pd.Series:
                    if rule_type == 'chemistry_only':
                        return frame['chemistry_trigger'].fillna(False).astype(bool)
                    if rule_type == 'pair_only':
                        return pd.to_numeric(frame['pair_minus_ll'], errors='coerce').fillna(-999.0) >= float(threshold)
                    if rule_type == 'scalar_only':
                        return pd.to_numeric(frame['ll_rank_norm'], errors='coerce').fillna(-999.0) >= float(threshold)
                    if rule_type == 'combined':
                        return frame['chemistry_trigger'].fillna(False).astype(bool) & (pd.to_numeric(frame['pair_minus_ll'], errors='coerce').fillna(-999.0) >= float(threshold))
                    if rule_type == 'combined_confident':
                        conf = 0.60 if confidence_threshold is None else float(confidence_threshold)
                        return (
                            frame['chemistry_trigger'].fillna(False).astype(bool)
                            & (pd.to_numeric(frame['pair_minus_ll'], errors='coerce').fillna(-999.0) >= float(threshold))
                            & (pd.to_numeric(frame['pair_rank_fixed_055'], errors='coerce').fillna(-999.0) >= conf)
                        )
                    raise ValueError(f'Unknown rule type: {rule_type}')

                def summarize_rule(frame: pd.DataFrame, rule_type: str, threshold: float, confidence_threshold: float | None, coverage_target: int, seed: int) -> dict[str, float]:
                    mask = compute_rule_mask(frame, rule_type, threshold, confidence_threshold)
                    labels = frame['label'].astype(int).to_numpy()
                    gap_stats = bootstrap_gap(labels, mask.to_numpy(), BOOTSTRAP_REPLICATES, seed)
                    or_stats = odds_ratio_from_mask(labels, mask.to_numpy())
                    random_stats = random_coverage_matched_gap(labels, int(mask.sum()), RANDOM_REPLICATES, seed + 17)
                    return {
                        'rule_type': rule_type,
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

                def select_best_rule(candidate_df: pd.DataFrame) -> pd.Series | None:
                    if candidate_df.empty:
                        return None
                    preferred_order = {'combined_confident': 0, 'combined': 1, 'pair_only': 2}
                    ranked = candidate_df.copy()
                    ranked = ranked.loc[pd.to_numeric(ranked['n_rule_on'], errors='coerce').fillna(0).astype(int) > 0].copy()
                    if ranked.empty:
                        return None
                    ranked['rule_priority'] = ranked['rule_type'].map(preferred_order).fillna(99).astype(int)
                    ranked['coverage_pass_int'] = ranked['coverage_floor_pass'].fillna(False).astype(int)
                    ranked = ranked.sort_values(
                        ['coverage_pass_int', 'enrichment_gap', 'odds_ratio', 'n_rule_on', 'rule_priority'],
                        ascending=[False, False, False, False, True],
                    ).reset_index(drop=True)
                    return ranked.iloc[0]

                runtime_manifest = {
                    'repo_root': str(REPO_ROOT),
                    'skip_live': SKIP_LIVE,
                    'fixed_alpha': FIXED_ALPHA,
                    'cuda_available': bool(torch.cuda.is_available()),
                    'cuda_device_count': int(torch.cuda.device_count()) if torch.cuda.is_available() else 0,
                    'cuda_device_name': torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu',
                }
                (RUNTIME_DIR / 'runtime_manifest.initial.json').write_text(json.dumps(runtime_manifest, indent=2), encoding='utf-8')
                display(pd.DataFrame([runtime_manifest]))
                done('Repo wiring, repaired rule logic, and reuse-first model adapters are ready.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Load upstream artifacts and emit the closure candidate roster
                replay_target_panels = pd.read_csv(BLOCK13_ROOT / 'tables' / 'replay_target_panels.csv')
                replay_target_contracts = pd.read_csv(BLOCK13_ROOT / 'tables' / 'replay_target_contracts.csv')
                block13_scoreboard = pd.read_csv(BLOCK13_ROOT / 'tables' / 'multitarget_generalization_scoreboard.csv')
                block13_transfer = pd.read_csv(BLOCK13_ROOT / 'tables' / 'transfer_closure_summary.csv')
                block13_claim = json.loads((BLOCK13_ROOT / 'manifests' / 'claim_summary.json').read_text(encoding='utf-8'))

                tp53_model_variant_scores = pd.read_csv(BLOCK12B_ROOT / 'tables' / 'tp53_model_variant_scores.csv')
                tp53_selected_rules_prior = pd.read_csv(BLOCK12B_ROOT / 'tables' / 'tp53_selected_rules.csv')
                tp53_rule_candidate_calibration = pd.read_csv(BLOCK12B_ROOT / 'tables' / 'tp53_rule_candidate_calibration.csv')
                block12b_control_wins = pd.read_csv(BLOCK12B_ROOT / 'tables' / 'control_win_summary.csv')

                case_support_collapsed = pd.read_csv(BLOCK10B_ROOT / 'tables' / 'case_support_collapsed.csv')
                gallery_final_cases = pd.read_csv(BLOCK08_ROOT / 'tables' / 'gallery_final_cases.csv')
                gallery_anti_case = pd.read_csv(BLOCK08_ROOT / 'tables' / 'gallery_anti_case.csv')

                closure_candidate_roster = (
                    block13_transfer.sort_values(['transfer_positive', 'near_transfer_positive', 'best_margin', 'fixed055_margin'], ascending=[False, False, False, False])
                    .reset_index(drop=True)
                )
                closure_candidate_roster.to_csv(TABLES_DIR / 'closure_candidate_roster.csv', index=False)
                display(closure_candidate_roster.head(12))
                display(replay_target_contracts.loc[replay_target_contracts['gene'].isin(['TP53', 'TSC2', 'CREBBP', 'BRCA1', 'MSH2', 'BRCA2'])].reset_index(drop=True))
                done('Upstream Block 13, 12B, 10B, and 08 artifacts are loaded and the closure candidate roster is frozen.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Build Block 14 panels from full labeled replay-ready surfaces
                selected_genes = [spec['gene'] for spec in TARGET_SPECS]
                filtered_panels = replay_target_panels.loc[replay_target_panels['gene'].isin(selected_genes)].copy()
                filtered_panels = filtered_panels.rename(columns={'wt_aa': 'wt_aa', 'mut_aa': 'mut_aa'})
                filtered_panels = filtered_panels.drop_duplicates(subset=['gene', 'variant_id', 'source_surface']).reset_index(drop=True)

                panel_manifest_rows = []
                target_frames = {}
                sequence_map = {}
                role_lookup = {spec['gene']: spec['role'] for spec in TARGET_SPECS}
                negative_lookup = {spec['gene']: bool(spec['is_negative_control']) for spec in TARGET_SPECS}

                for spec in TARGET_SPECS:
                    gene = spec['gene']
                    gene_frame = filtered_panels.loc[filtered_panels['gene'].eq(gene)].copy()
                    if gene_frame.empty:
                        continue
                    gene_frame['target_role'] = spec['role']
                    gene_frame['is_negative_control'] = bool(spec['is_negative_control'])
                    gene_frame = gene_frame.sort_values(['position', 'mut_aa', 'source_surface', 'variant_id']).reset_index(drop=True)
                    target_frames[gene] = gene_frame
                    sequence_map[gene] = str(gene_frame['sequence'].dropna().iloc[0]).strip().upper()
                    out_path = TABLES_DIR / f"{gene.lower()}_{spec['role']}_panel.csv"
                    gene_frame.to_csv(out_path, index=False)
                    panel_manifest_rows.append({
                        'gene': gene,
                        'target_role': spec['role'],
                        'is_negative_control': bool(spec['is_negative_control']),
                        'n_rows': int(len(gene_frame)),
                        'n_positive': int(pd.to_numeric(gene_frame['label'], errors='coerce').fillna(0).astype(int).sum()),
                        'n_negative': int((1 - pd.to_numeric(gene_frame['label'], errors='coerce').fillna(0).astype(int)).sum()),
                        'source_surfaces': '|'.join(sorted(gene_frame['source_surface'].astype(str).unique())),
                        'panel_path': str(out_path.relative_to(REPO_ROOT)),
                    })

                block14_panel_manifest = pd.DataFrame(panel_manifest_rows)
                block14_panel_manifest.to_csv(TABLES_DIR / 'block14_panel_manifest.csv', index=False)

                block14_target_contracts = replay_target_contracts.loc[replay_target_contracts['gene'].isin(selected_genes)].copy()
                block14_target_contracts['selected_for_block14'] = True
                block14_target_contracts['target_role'] = block14_target_contracts['gene'].map(role_lookup)
                block14_target_contracts['is_negative_control'] = block14_target_contracts['gene'].map(negative_lookup)
                block14_target_contracts.to_csv(TABLES_DIR / 'block14_target_contracts.csv', index=False)

                display(block14_panel_manifest)
                done('Block 14 full labeled calibration, holdout, negative, and consistency panels are written.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Live scoring, focused and reusable
                aggregate_reuse = pd.read_csv(BLOCK13_ROOT / 'tables' / 'multitarget_model_variant_scores.csv')
                aggregate_reuse = aggregate_reuse.loc[aggregate_reuse['gene'].isin([spec['gene'] for spec in TARGET_SPECS])].copy()
                aggregate_reuse['model_label'] = aggregate_reuse['model_label'].astype(str)
                aggregate_reuse['gene'] = aggregate_reuse['gene'].astype(str).str.upper()

                runtime_rows = []
                reuse_rows = []
                scored_frames = []

                def subset_full_panel_scores(frame: pd.DataFrame, panel_frame: pd.DataFrame, gene: str, model_label: str) -> pd.DataFrame:
                    gene_scores = frame.loc[frame['gene'].eq(gene) & frame['model_label'].eq(model_label)].copy()
                    if gene_scores.empty:
                        return gene_scores
                    expected_variants = set(panel_frame['variant_id'].astype(str))
                    gene_scores = gene_scores.loc[gene_scores['variant_id'].astype(str).isin(expected_variants)].copy()
                    if gene_scores.empty:
                        return gene_scores
                    return gene_scores.drop_duplicates(subset=['variant_id']).reset_index(drop=True)

                for spec in MODEL_SPECS:
                    model_label = spec['model_label']
                    model_name = spec['model_name']
                    for target_spec in TARGET_SPECS:
                        gene = target_spec['gene']
                        if gene not in target_frames:
                            continue
                        if target_spec['role'] == 'consistency_only' and model_label not in {'ESM2-150M', 'ESM2-650M', 'ESM-1v'}:
                            continue

                        panel_df = target_frames[gene].copy()
                        output_path = score_output_path(model_name, gene)
                        metadata_path = metadata_output_path(model_name, gene)

                        expected_variant_ids = set(panel_df['variant_id'].astype(str))
                        reused_exact, reuse_meta = reuse_exact_scores(model_name, gene, expected_variant_ids)
                        if reused_exact is not None:
                            frame = reused_exact.copy()
                            frame['gene'] = gene
                            frame['model_label'] = model_label
                            frame['model_name'] = model_name
                            frame['family_label'] = spec['family_label']
                            frame['architecture_kind'] = spec['architecture_kind']
                            frame['adapter_kind'] = spec['adapter_kind']
                            frame['sequence_mode'] = spec['sequence_mode']
                            frame['scale_bucket'] = spec['scale_bucket']
                            frame['panel_name'] = gene.lower()
                            frame.to_csv(output_path, index=False)
                            metadata_path.write_text(json.dumps(reuse_meta, indent=2), encoding='utf-8')
                            reuse_rows.append({'gene': gene, 'model_label': model_label, 'reuse_kind': reuse_meta['reuse_kind'], 'reuse_source': reuse_meta['reuse_source'], 'status': 'reused'})
                            scored_frames.append(frame)
                            runtime_rows.append({'gene': gene, 'model_label': model_label, 'status': 'reused_exact_live_score', 'n_rows': int(len(frame))})
                            continue

                        aggregate_frame = subset_full_panel_scores(aggregate_reuse, panel_df, gene, model_label)
                        if not aggregate_frame.empty and set(panel_df['variant_id'].astype(str)).issubset(set(aggregate_frame['variant_id'].astype(str))):
                            aggregate_frame = aggregate_frame.copy()
                            aggregate_frame['panel_name'] = gene.lower()
                            aggregate_frame.to_csv(output_path, index=False)
                            metadata_path.write_text(json.dumps({'reuse_kind': 'aggregate_table', 'reuse_source': 'block13_multitarget_model_variant_scores.csv'}, indent=2), encoding='utf-8')
                            reuse_rows.append({'gene': gene, 'model_label': model_label, 'reuse_kind': 'aggregate_table', 'reuse_source': 'block13_multitarget_model_variant_scores.csv', 'status': 'reused'})
                            scored_frames.append(aggregate_frame)
                            runtime_rows.append({'gene': gene, 'model_label': model_label, 'status': 'reused_aggregate_table', 'n_rows': int(len(aggregate_frame))})
                            continue

                        if SKIP_LIVE:
                            runtime_rows.append({'gene': gene, 'model_label': model_label, 'status': 'missing_live_scores_skip_requested', 'n_rows': 0})
                            reuse_rows.append({'gene': gene, 'model_label': model_label, 'reuse_kind': 'none', 'reuse_source': '', 'status': 'missing_under_skip_live'})
                            continue

                        scored, manifest = score_panel_with_model(panel_df, sequence_map, spec, output_path)
                        if not scored.empty:
                            scored['panel_name'] = gene.lower()
                            scored_frames.append(scored)
                        metadata_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
                        runtime_rows.append({'gene': gene, 'model_label': model_label, 'status': manifest.get('status', 'unknown'), 'n_rows': int(len(scored))})
                        reuse_rows.append({'gene': gene, 'model_label': model_label, 'reuse_kind': manifest.get('status', 'live'), 'reuse_source': '', 'status': manifest.get('status', 'unknown')})

                block14_model_variant_scores = pd.concat(scored_frames, ignore_index=True) if scored_frames else pd.DataFrame()
                if not block14_model_variant_scores.empty:
                    block14_model_variant_scores = block14_model_variant_scores.drop_duplicates(subset=['gene', 'model_label', 'variant_id'], keep='last').reset_index(drop=True)
                    block14_model_variant_scores = ensure_rank_features(block14_model_variant_scores, FIXED_ALPHA)
                block14_model_variant_scores.to_csv(TABLES_DIR / 'block14_model_variant_scores.csv', index=False)
                pd.DataFrame(reuse_rows).to_csv(TABLES_DIR / 'block14_score_reuse_inventory.csv', index=False)
                pd.DataFrame(runtime_rows).to_csv(TABLES_DIR / 'block14_runtime_manifest.csv', index=False)

                display(pd.DataFrame(runtime_rows))
                done('Focused reuse-first scoring finished and Block 14 model/target score tables are written.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Covariance-native calibration on TP53
                candidate_rows = []
                selected_rows = []

                tp53_panel = target_frames.get('TP53', pd.DataFrame()).copy()
                tp53_live = block14_model_variant_scores.loc[block14_model_variant_scores['gene'].eq('TP53')].copy() if not block14_model_variant_scores.empty else pd.DataFrame()

                for spec in MODEL_SPECS:
                    model_label = spec['model_label']
                    model_tp53 = tp53_live.loc[tp53_live['model_label'].eq(model_label)].copy()
                    if model_tp53.empty:
                        selected_rows.append({
                            'model_label': model_label,
                            'family_label': spec['family_label'],
                            'architecture_kind': spec['architecture_kind'],
                            'rule_type': 'none',
                            'threshold': float('nan'),
                            'confidence_threshold': float('nan'),
                            'coverage_floor_pass': False,
                            'selection_status': 'failed_anchor_calibration',
                            'reason': 'No TP53 rows available for this model in Block 14.',
                        })
                        continue

                    model_tp53 = ensure_rank_features(model_tp53, FIXED_ALPHA)
                    coverage_target = coverage_floor(len(model_tp53))
                    for rule_type in ['pair_only', 'combined', 'combined_confident']:
                        for threshold in RULE_THRESHOLDS:
                            if rule_type == 'combined_confident':
                                for confidence_threshold in CONFIDENCE_THRESHOLDS:
                                    summary = summarize_rule(model_tp53, rule_type, threshold, confidence_threshold, coverage_target, RANDOM_SEED + len(candidate_rows))
                                    summary.update({'model_label': model_label, 'family_label': spec['family_label'], 'architecture_kind': spec['architecture_kind']})
                                    candidate_rows.append(summary)
                            else:
                                summary = summarize_rule(model_tp53, rule_type, threshold, None, coverage_target, RANDOM_SEED + len(candidate_rows))
                                summary.update({'model_label': model_label, 'family_label': spec['family_label'], 'architecture_kind': spec['architecture_kind']})
                                candidate_rows.append(summary)

                    candidate_df = pd.DataFrame(candidate_rows)
                    candidate_df = candidate_df.loc[candidate_df['model_label'].eq(model_label)].copy()
                    selected = select_best_rule(candidate_df)
                    if selected is None:
                        selected_rows.append({
                            'model_label': model_label,
                            'family_label': spec['family_label'],
                            'architecture_kind': spec['architecture_kind'],
                            'rule_type': 'none',
                            'threshold': float('nan'),
                            'confidence_threshold': float('nan'),
                            'coverage_floor_pass': False,
                            'selection_status': 'failed_anchor_calibration',
                            'reason': 'No covariance-native candidate could be selected.',
                        })
                    else:
                        selected_payload = selected.to_dict()
                        selected_payload.update({'selection_status': 'selected', 'reason': 'Best covariance-native TP53 rule under the repaired selection policy.'})
                        selected_rows.append(selected_payload)

                tp53_covariance_native_rule_candidates = pd.DataFrame(candidate_rows)
                tp53_covariance_native_selected_rules = pd.DataFrame(selected_rows)
                tp53_covariance_native_rule_candidates.to_csv(TABLES_DIR / 'tp53_covariance_native_rule_candidates.csv', index=False)
                tp53_covariance_native_selected_rules.to_csv(TABLES_DIR / 'tp53_covariance_native_selected_rules.csv', index=False)

                display(tp53_covariance_native_selected_rules)
                done('TP53 covariance-native calibration is complete and repaired rule selection is frozen.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Holdout closure on full labeled targets
                holdout_pair_rows = []
                holdout_model_rows = []

                positive_holdout_genes = ['TSC2', 'CREBBP']
                negative_guardrail_genes = ['BRCA1', 'MSH2']
                optional_consistency_genes = ['BRCA2']
                holdout_genes = [gene for gene in positive_holdout_genes + negative_guardrail_genes + optional_consistency_genes if gene in target_frames]

                for _, selected in tp53_covariance_native_selected_rules.iterrows():
                    model_label = str(selected['model_label'])
                    if str(selected.get('selection_status', '')) != 'selected':
                        holdout_model_rows.append({
                            'model_label': model_label,
                            'holdout_positive_model': False,
                            'positive_holdout_targets': '',
                            'negative_holdout_targets_triggered': '',
                            'negative_guardrail_clean': False,
                            'reason': str(selected.get('reason', 'anchor calibration failed')),
                        })
                        continue

                    target_hits = []
                    negative_hits = []
                    for gene in holdout_genes:
                        panel_scores = block14_model_variant_scores.loc[
                            block14_model_variant_scores['gene'].eq(gene) & block14_model_variant_scores['model_label'].eq(model_label)
                        ].copy()
                        if panel_scores.empty:
                            holdout_pair_rows.append({
                                'gene': gene,
                                'model_label': model_label,
                                'rule_type': selected['rule_type'],
                                'threshold': selected['threshold'],
                                'confidence_threshold': selected.get('confidence_threshold', float('nan')),
                                'n_rows': 0,
                                'n_rule_on': 0,
                                'rule_on_fraction': float('nan'),
                                'pathogenic_fraction_rule_on': float('nan'),
                                'pathogenic_fraction_rule_off': float('nan'),
                                'enrichment_gap': float('nan'),
                                'gap_ci_low': float('nan'),
                                'gap_ci_high': float('nan'),
                                'holdout_positive_pair': False,
                                'target_role': role_lookup.get(gene, 'unknown'),
                            })
                            continue

                        panel_scores = ensure_rank_features(panel_scores, FIXED_ALPHA)
                        mask = compute_rule_mask(
                            panel_scores,
                            str(selected['rule_type']),
                            float(selected['threshold']),
                            safe_float(selected.get('confidence_threshold', float('nan'))),
                        )
                        labels = panel_scores['label'].astype(int).to_numpy()
                        stats = bootstrap_gap(labels, mask.to_numpy(), BOOTSTRAP_REPLICATES, RANDOM_SEED + len(holdout_pair_rows))
                        n_rows = int(len(panel_scores))
                        n_rule_on = int(mask.sum())
                        rule_on_fraction = float(mask.mean()) if n_rows else float('nan')
                        pf_on = safe_float(stats['pathogenic_fraction_rule_on'])
                        pf_off = safe_float(stats['pathogenic_fraction_rule_off'])
                        enrichment_gap = safe_float(stats['enrichment_gap'])
                        holdout_positive_pair = bool(
                            n_rule_on >= coverage_floor(n_rows)
                            and rule_on_fraction <= HOLDOUT_MAX_RULE_ON_FRAC
                            and enrichment_gap > 0.0
                            and pf_on > pf_off
                        )
                        if gene in positive_holdout_genes and holdout_positive_pair:
                            target_hits.append(gene)
                        if gene in negative_guardrail_genes and holdout_positive_pair:
                            negative_hits.append(gene)
                        holdout_pair_rows.append({
                            'gene': gene,
                            'model_label': model_label,
                            'rule_type': selected['rule_type'],
                            'threshold': selected['threshold'],
                            'confidence_threshold': selected.get('confidence_threshold', float('nan')),
                            'n_rows': n_rows,
                            'n_rule_on': n_rule_on,
                            'rule_on_fraction': rule_on_fraction,
                            **stats,
                            'holdout_positive_pair': holdout_positive_pair,
                            'target_role': role_lookup.get(gene, 'unknown'),
                        })

                    holdout_model_rows.append({
                        'model_label': model_label,
                        'family_label': selected.get('family_label', ''),
                        'architecture_kind': selected.get('architecture_kind', ''),
                        'positive_holdout_targets': '|'.join(sorted(set(target_hits))),
                        'negative_holdout_targets_triggered': '|'.join(sorted(set(negative_hits))),
                        'holdout_positive_model': bool(target_hits and not negative_hits),
                        'negative_guardrail_clean': not bool(negative_hits),
                        'reason': 'Positive full-panel holdout enrichment without triggering BRCA1 or MSH2.' if target_hits and not negative_hits else 'No positive holdout passed or a negative guardrail triggered.',
                    })

                block14_holdout_pair_summary = pd.DataFrame(holdout_pair_rows)
                block14_holdout_model_summary = pd.DataFrame(holdout_model_rows)
                block14_holdout_pair_summary.to_csv(TABLES_DIR / 'block14_holdout_pair_summary.csv', index=False)
                block14_holdout_model_summary.to_csv(TABLES_DIR / 'block14_holdout_model_summary.csv', index=False)

                display(block14_holdout_model_summary)
                done('Full labeled holdout evaluation is complete and model-level holdout status is written.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Control-win closure on the same holdouts
                control_pair_rows = []
                control_model_rows = []

                for _, selected in tp53_covariance_native_selected_rules.iterrows():
                    model_label = str(selected['model_label'])
                    if str(selected.get('selection_status', '')) != 'selected':
                        control_model_rows.append({
                            'model_label': model_label,
                            'control_win_model': False,
                            'positive_targets_with_control_win': '',
                            'negative_targets_with_control_win': '',
                            'reason': 'No selected covariance-native anchor rule was available.',
                        })
                        continue

                    positive_wins = []
                    negative_wins = []
                    for gene in [gene for gene in ['TSC2', 'CREBBP', 'BRCA1', 'MSH2', 'BRCA2'] if gene in target_frames]:
                        panel_scores = block14_model_variant_scores.loc[
                            block14_model_variant_scores['gene'].eq(gene) & block14_model_variant_scores['model_label'].eq(model_label)
                        ].copy()
                        if panel_scores.empty:
                            control_pair_rows.append({
                                'gene': gene,
                                'model_label': model_label,
                                'selected_rule_type': selected['rule_type'],
                                'selected_rule_gap': float('nan'),
                                'chemistry_only': float('nan'),
                                'scalar_top_n_matched': float('nan'),
                                'random_coverage_matched_mean': float('nan'),
                                'pair_only': float('nan'),
                                'control_win_pair': False,
                            })
                            continue

                        panel_scores = ensure_rank_features(panel_scores, FIXED_ALPHA)
                        selected_mask = compute_rule_mask(
                            panel_scores,
                            str(selected['rule_type']),
                            float(selected['threshold']),
                            safe_float(selected.get('confidence_threshold', float('nan'))),
                        )
                        labels = panel_scores['label'].astype(int).to_numpy()
                        selected_stats = bootstrap_gap(labels, selected_mask.to_numpy(), BOOTSTRAP_REPLICATES, RANDOM_SEED + len(control_pair_rows))
                        n_rule_on = int(selected_mask.sum())

                        chemistry_mask = compute_rule_mask(panel_scores, 'chemistry_only', 0.0)
                        chemistry_gap = safe_float(bootstrap_gap(labels, chemistry_mask.to_numpy(), BOOTSTRAP_REPLICATES, RANDOM_SEED + 1000 + len(control_pair_rows))['enrichment_gap'])

                        scalar_sorted = panel_scores.sort_values('ll_rank_norm', ascending=False).reset_index(drop=True)
                        scalar_mask = np.zeros(len(panel_scores), dtype=bool)
                        scalar_mask[scalar_sorted.index[:n_rule_on]] = True
                        scalar_gap = safe_float(bootstrap_gap(labels, scalar_mask, BOOTSTRAP_REPLICATES, RANDOM_SEED + 2000 + len(control_pair_rows))['enrichment_gap'])

                        random_gap_stats = random_coverage_matched_gap(labels, n_rule_on, RANDOM_REPLICATES, RANDOM_SEED + 3000 + len(control_pair_rows))
                        random_gap = safe_float(random_gap_stats['random_gap_mean'])

                        pair_gap = float('nan')
                        beats_pair = True
                        if str(selected['rule_type']) != 'pair_only':
                            pair_mask = compute_rule_mask(panel_scores, 'pair_only', float(selected['threshold']))
                            pair_gap = safe_float(bootstrap_gap(labels, pair_mask.to_numpy(), BOOTSTRAP_REPLICATES, RANDOM_SEED + 4000 + len(control_pair_rows))['enrichment_gap'])
                            beats_pair = safe_float(selected_stats['enrichment_gap']) > pair_gap

                        selected_gap = safe_float(selected_stats['enrichment_gap'])
                        control_win_pair = bool(
                            selected_gap > chemistry_gap
                            and selected_gap > scalar_gap
                            and selected_gap > random_gap
                            and beats_pair
                        )

                        if gene in ['TSC2', 'CREBBP'] and control_win_pair:
                            positive_wins.append(gene)
                        if gene in ['BRCA1', 'MSH2'] and control_win_pair:
                            negative_wins.append(gene)

                        control_pair_rows.append({
                            'gene': gene,
                            'model_label': model_label,
                            'selected_rule_type': selected['rule_type'],
                            'selected_rule_gap': selected_gap,
                            'chemistry_only': chemistry_gap,
                            'scalar_top_n_matched': scalar_gap,
                            'random_coverage_matched_mean': random_gap,
                            'pair_only': pair_gap,
                            'control_win_pair': control_win_pair,
                        })

                    control_model_rows.append({
                        'model_label': model_label,
                        'positive_targets_with_control_win': '|'.join(sorted(set(positive_wins))),
                        'negative_targets_with_control_win': '|'.join(sorted(set(negative_wins))),
                        'control_win_model': bool(positive_wins and not negative_wins),
                        'reason': 'Selected covariance-native rule beats all repaired controls on at least one positive holdout target.' if positive_wins and not negative_wins else 'No positive target beat all repaired controls or a negative guardrail also won.',
                    })

                block14_control_pair_summary = pd.DataFrame(control_pair_rows)
                block14_control_model_summary = pd.DataFrame(control_model_rows)
                block14_control_pair_summary.to_csv(TABLES_DIR / 'block14_control_pair_summary.csv', index=False)
                block14_control_model_summary.to_csv(TABLES_DIR / 'block14_control_model_summary.csv', index=False)

                display(block14_control_model_summary)
                done('Repaired control-win evaluation is complete and model-level control status is written.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Final adjudication
                final_scoreboard = (
                    tp53_covariance_native_selected_rules[['model_label', 'family_label', 'architecture_kind', 'rule_type', 'coverage_floor_pass']]
                    .rename(columns={'rule_type': 'covariance_native_rule_type'})
                    .merge(block14_holdout_model_summary[['model_label', 'holdout_positive_model', 'positive_holdout_targets', 'negative_holdout_targets_triggered', 'negative_guardrail_clean']], on='model_label', how='left')
                    .merge(block14_control_model_summary[['model_label', 'control_win_model', 'positive_targets_with_control_win', 'negative_targets_with_control_win']], on='model_label', how='left')
                )

                final_scoreboard['holdout_positive_model'] = final_scoreboard['holdout_positive_model'].fillna(False).astype(bool)
                final_scoreboard['control_win_model'] = final_scoreboard['control_win_model'].fillna(False).astype(bool)
                final_scoreboard['negative_guardrail_clean'] = final_scoreboard['negative_guardrail_clean'].fillna(False).astype(bool)
                final_scoreboard['portable_protocol_ok'] = final_scoreboard['coverage_floor_pass'].fillna(False).astype(bool)
                final_scoreboard['transfer_positive_model'] = (
                    final_scoreboard['holdout_positive_model']
                    & final_scoreboard['control_win_model']
                    & final_scoreboard['family_label'].isin(['prottrans', 'progen'])
                    & final_scoreboard['negative_guardrail_clean']
                )

                def closure_taxonomy(row: pd.Series) -> str:
                    if str(row.get('selection_status', 'selected')) != 'selected' and str(row.get('covariance_native_rule_type', 'none')) == 'none':
                        return 'failed_anchor_calibration'
                    if not bool(row.get('negative_guardrail_clean', False)):
                        return 'failed_negative_guardrail'
                    if bool(row.get('transfer_positive_model', False)):
                        return 'full_closure'
                    if bool(row.get('holdout_positive_model', False)) and bool(row.get('control_win_model', False)):
                        return 'supportive_residual'
                    if bool(row.get('holdout_positive_model', False)):
                        return 'holdout_only'
                    if bool(row.get('control_win_model', False)):
                        return 'control_only'
                    return 'supportive_residual'

                final_scoreboard['closure_taxonomy'] = final_scoreboard.apply(closure_taxonomy, axis=1)
                final_scoreboard.to_csv(TABLES_DIR / 'block14_final_scoreboard.csv', index=False)

                family_summary = (
                    final_scoreboard.groupby('family_label', dropna=False)
                    .agg(
                        n_models=('model_label', 'size'),
                        holdout_positive_models=('holdout_positive_model', 'sum'),
                        control_win_models=('control_win_model', 'sum'),
                        transfer_positive_models=('transfer_positive_model', 'sum'),
                    )
                    .reset_index()
                )
                family_summary.to_csv(TABLES_DIR / 'block14_family_summary.csv', index=False)

                holdout_positive_models = final_scoreboard.loc[final_scoreboard['holdout_positive_model'], 'model_label'].astype(str).tolist()
                control_win_models = final_scoreboard.loc[final_scoreboard['control_win_model'], 'model_label'].astype(str).tolist()
                transfer_positive_models = final_scoreboard.loc[final_scoreboard['transfer_positive_model'], 'model_label'].astype(str).tolist()
                non_esm_transfer_positive_models = final_scoreboard.loc[
                    final_scoreboard['transfer_positive_model'] & final_scoreboard['family_label'].isin(['prottrans', 'progen']),
                    'model_label'
                ].astype(str).tolist()
                negative_guardrails_clean = bool(
                    final_scoreboard.loc[final_scoreboard['model_label'].isin(final_scoreboard['model_label']), 'negative_guardrail_clean'].fillna(False).all()
                )

                if holdout_positive_models and control_win_models and non_esm_transfer_positive_models and negative_guardrails_clean:
                    claim_status = 'full_holdout_control_closure'
                    claim_reason = 'At least one covariance-native rule now transfers from TP53 to a full labeled non-anchor holdout target, beats repaired alternative controls, and preserves BRCA1/MSH2 as negative guardrails.'
                elif holdout_positive_models or control_win_models or transfer_positive_models:
                    claim_status = 'closure_strengthened_but_not_complete'
                    claim_reason = 'Block 14 repairs the invalid firewalls and strengthens closure, but at least one required closure condition remains open.'
                else:
                    claim_status = 'closure_still_mixed'
                    claim_reason = 'Even after repairing the firewalls, no model satisfied the combined holdout and control-win closure criteria without breaking negative guardrails.'

                claim_summary = {
                    'notebook_slug': NOTEBOOK_SLUG,
                    'run_at_utc': RUN_AT,
                    'account_label': ACCOUNT_LABEL,
                    'claim_status': claim_status,
                    'claim_reason': claim_reason,
                    'holdout_positive_models': holdout_positive_models,
                    'control_win_models': control_win_models,
                    'transfer_positive_models': transfer_positive_models,
                    'non_esm_transfer_positive_models': non_esm_transfer_positive_models,
                    'negative_guardrails_clean': negative_guardrails_clean,
                    'repair_notes': {
                        'holdout_panel': 'full_labeled_replay_surfaces',
                        'control_logic': 'no_self_comparison_for_pair_only_and_no_scalar_only_final_rule',
                    },
                }
                (MANIFESTS_DIR / 'block14_claim_summary.json').write_text(json.dumps(claim_summary, indent=2), encoding='utf-8')

                display(final_scoreboard)
                done('Final adjudication is complete and the Block 14 claim summary is frozen.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Reviewer-facing figures
                if not block14_holdout_pair_summary.empty:
                    holdout_plot = block14_holdout_pair_summary.loc[block14_holdout_pair_summary['gene'].isin(['TSC2', 'CREBBP', 'BRCA1', 'MSH2'])].copy()
                    pivot = holdout_plot.pivot_table(index='model_label', columns='gene', values='enrichment_gap', aggfunc='first')
                    if not pivot.empty:
                        fig, ax = plt.subplots(figsize=(8, max(4, 0.6 * len(pivot))))
                        im = ax.imshow(pivot.fillna(0.0).to_numpy(), cmap='coolwarm', aspect='auto')
                        ax.set_xticks(range(len(pivot.columns)))
                        ax.set_xticklabels(pivot.columns)
                        ax.set_yticks(range(len(pivot.index)))
                        ax.set_yticklabels(pivot.index)
                        ax.set_title('Block 14 holdout enrichment scoreboard')
                        fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
                        fig.tight_layout()
                        fig.savefig(FIGURES_DIR / 'block14_holdout_scoreboard.png', dpi=220, bbox_inches='tight')
                        plt.close(fig)

                if not block14_control_pair_summary.empty:
                    control_plot = block14_control_pair_summary.loc[block14_control_pair_summary['gene'].isin(['TSC2', 'CREBBP', 'BRCA1', 'MSH2'])].copy()
                    pivot = control_plot.pivot_table(index='model_label', columns='gene', values='selected_rule_gap', aggfunc='first')
                    if not pivot.empty:
                        fig, ax = plt.subplots(figsize=(8, max(4, 0.6 * len(pivot))))
                        im = ax.imshow(pivot.fillna(0.0).to_numpy(), cmap='viridis', aspect='auto')
                        ax.set_xticks(range(len(pivot.columns)))
                        ax.set_xticklabels(pivot.columns)
                        ax.set_yticks(range(len(pivot.index)))
                        ax.set_yticklabels(pivot.index)
                        ax.set_title('Block 14 selected-rule control scoreboard')
                        fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
                        fig.tight_layout()
                        fig.savefig(FIGURES_DIR / 'block14_control_scoreboard.png', dpi=220, bbox_inches='tight')
                        plt.close(fig)

                if not tp53_covariance_native_selected_rules.empty:
                    plot_df = tp53_covariance_native_selected_rules.loc[tp53_covariance_native_selected_rules['selection_status'].eq('selected')].copy()
                    if not plot_df.empty:
                        fig, ax = plt.subplots(figsize=(8, 4.5))
                        ax.scatter(plot_df['n_rule_on'], plot_df['enrichment_gap'], s=90, color='#0f766e')
                        for _, row in plot_df.iterrows():
                            ax.text(row['n_rule_on'] + 0.15, row['enrichment_gap'], row['model_label'], fontsize=8)
                        ax.axhline(0.0, color='black', linestyle='--', linewidth=1)
                        ax.set_xlabel('TP53 rule-on coverage')
                        ax.set_ylabel('TP53 enrichment gap')
                        ax.set_title('Block 14 TP53 covariance-native rules')
                        fig.tight_layout()
                        fig.savefig(FIGURES_DIR / 'block14_tp53_covariance_native_rules.png', dpi=220, bbox_inches='tight')
                        plt.close(fig)

                if not final_scoreboard.empty:
                    positive_guardrail = final_scoreboard[['model_label', 'holdout_positive_model', 'control_win_model', 'negative_guardrail_clean']].copy()
                    positive_guardrail = positive_guardrail.set_index('model_label')
                    fig, ax = plt.subplots(figsize=(8, max(4, 0.55 * len(positive_guardrail))))
                    im = ax.imshow(positive_guardrail.astype(float).to_numpy(), cmap='Blues', aspect='auto', vmin=0.0, vmax=1.0)
                    ax.set_xticks(range(len(positive_guardrail.columns)))
                    ax.set_xticklabels(positive_guardrail.columns, rotation=25, ha='right')
                    ax.set_yticks(range(len(positive_guardrail.index)))
                    ax.set_yticklabels(positive_guardrail.index)
                    ax.set_title('Positive targets versus negative guardrails')
                    fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
                    fig.tight_layout()
                    fig.savefig(FIGURES_DIR / 'block14_positive_targets_vs_negative_guardrails.png', dpi=220, bbox_inches='tight')
                    plt.close(fig)

                if not family_summary.empty:
                    fig, ax = plt.subplots(figsize=(7, 4.5))
                    family_summary.plot(
                        x='family_label',
                        y=['holdout_positive_models', 'control_win_models', 'transfer_positive_models'],
                        kind='bar',
                        ax=ax,
                    )
                    ax.set_ylabel('Model count')
                    ax.set_title('Block 14 family closure panel')
                    fig.tight_layout()
                    fig.savefig(FIGURES_DIR / 'block14_family_closure_panel.png', dpi=220, bbox_inches='tight')
                    plt.close(fig)

                if claim_summary['claim_status'] == 'full_holdout_control_closure':
                    winners = final_scoreboard.loc[final_scoreboard['transfer_positive_model']].copy()
                    if not winners.empty:
                        fig, ax = plt.subplots(figsize=(7, 4.5))
                        ax.barh(winners['model_label'], [1.0] * len(winners), color='#15803d')
                        ax.set_xlim(0.0, 1.2)
                        ax.set_title('Full closure witnesses')
                        fig.tight_layout()
                        fig.savefig(FIGURES_DIR / 'block14_full_closure_witnesses.png', dpi=220, bbox_inches='tight')
                        plt.close(fig)

                done('Reviewer-facing Block 14 figures are written.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Markdown outputs, manifests, and final bundle
                summary_md = '\\n'.join([
                    '# Block 14 Holdout and Control Closure Summary',
                    '',
                    f"- Claim status: `{claim_summary['claim_status']}`",
                    f"- Holdout-positive models: `{', '.join(claim_summary['holdout_positive_models']) if claim_summary['holdout_positive_models'] else 'none'}`",
                    f"- Control-win models: `{', '.join(claim_summary['control_win_models']) if claim_summary['control_win_models'] else 'none'}`",
                    f"- Non-ESM transfer-positive models: `{', '.join(claim_summary['non_esm_transfer_positive_models']) if claim_summary['non_esm_transfer_positive_models'] else 'none'}`",
                    f"- Negative guardrails clean: `{claim_summary['negative_guardrails_clean']}`",
                    '',
                    '## Interpretation',
                    '',
                    claim_summary['claim_reason'],
                ])

                claim_paragraph = (
                    'Block 14 repairs the two invalid closure firewalls from Block 13 by rebuilding holdout on full labeled replay surfaces and by evaluating covariance-native rules against repaired alternative controls without self-comparison. '
                    + claim_summary['claim_reason']
                )

                replay_contract_md = '\\n'.join([
                    '# Block 14 Replay Contract',
                    '',
                    '- Calibration anchor: `TP53`',
                    '- Positive holdout targets: `TSC2`, `CREBBP`',
                    '- Negative guardrails: `BRCA1`, `MSH2`',
                    '- Optional consistency-only target: `BRCA2`',
                    '- Final rule families allowed: `pair_only`, `combined`, `combined_confident`',
                    '- Disallowed as final rule: `scalar_only`, `chemistry_only`',
                ])

                artifact_summary = {
                    'notebook_slug': NOTEBOOK_SLUG,
                    'results_root': str(RESULTS_ROOT),
                    'tables_dir': str(TABLES_DIR),
                    'figures_dir': str(FIGURES_DIR),
                    'text_dir': str(TEXT_DIR),
                    'manifests_dir': str(MANIFESTS_DIR),
                    'runtime_dir': str(RUNTIME_DIR),
                    'live_scores_dir': str(LIVE_SCORES_DIR),
                    'bundle_dir': str(BUNDLE_DIR),
                    'zip_path': str(ZIP_PATH),
                }

                (TEXT_DIR / 'block14_summary.md').write_text(summary_md + '\\n', encoding='utf-8')
                (TEXT_DIR / 'block14_claim_paragraph.md').write_text(claim_paragraph + '\\n', encoding='utf-8')
                (TEXT_DIR / 'block14_replay_contract.md').write_text(replay_contract_md + '\\n', encoding='utf-8')
                (MANIFESTS_DIR / 'artifact_summary.json').write_text(json.dumps(artifact_summary, indent=2), encoding='utf-8')
                (RUNTIME_DIR / 'runtime_manifest.json').write_text(json.dumps(runtime_manifest, indent=2), encoding='utf-8')

                if BUNDLE_DIR.exists():
                    shutil.rmtree(BUNDLE_DIR)
                BUNDLE_DIR.mkdir(parents=True, exist_ok=True)
                for folder in [TABLES_DIR, FIGURES_DIR, TEXT_DIR, MANIFESTS_DIR, RUNTIME_DIR, LIVE_SCORES_DIR]:
                    if folder.exists():
                        destination = BUNDLE_DIR / folder.name
                        destination.mkdir(parents=True, exist_ok=True)
                        for file_path in folder.rglob('*'):
                            if file_path.is_file():
                                target = BUNDLE_DIR / file_path.relative_to(RESULTS_ROOT)
                                target.parent.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(file_path, target)

                if ZIP_PATH.exists():
                    ZIP_PATH.unlink()
                with zipfile.ZipFile(ZIP_PATH, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
                    for file_path in BUNDLE_DIR.rglob('*'):
                        if file_path.is_file():
                            archive.write(file_path, arcname=str(file_path.relative_to(BUNDLE_DIR.parent)))

                print(json.dumps(claim_summary, indent=2))
                display(final_scoreboard)
                done('Block 14 markdown, manifests, bundle directory, and zip package are complete.')
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
    notebook_path = repo_root / 'New Notebooks' / '14_block14_holdout_control_closure_h100.ipynb'
    notebook_path.write_text(json.dumps(build_notebook(), indent=2), encoding='utf-8')
    print(f'Wrote {notebook_path}')


if __name__ == '__main__':
    main()
