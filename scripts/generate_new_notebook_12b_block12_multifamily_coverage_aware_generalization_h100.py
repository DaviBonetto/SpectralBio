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
            "# Experiment: SpectralBio Block 12B - Multifamily Coverage-Aware Generalization (H100)\n\n"
            "Objective:\n"
            "- Test whether the bounded covariance rule generalizes across **families, architectures, and scales**, instead of surviving only inside a narrow ESM pocket.\n"
            "- Keep the analysis **coverage-aware** so sparse rule hits cannot masquerade as portability.\n"
            "- Reincorporate a **structural orthogonal layer**, pairwise falsification controls, and a compact non-TP53 transfer panel inside the same notebook.\n"
            "- Produce a reviewer-facing validation package under `New Notebooks/results/12b_block12_multifamily_coverage_aware_generalization_h100/`.\n"
        ),
        markdown_cell(
            "## Courtroom Contract\n\n"
            "- This notebook is the final stress test for the rulebook from Block 11.\n"
            "- It does **not** try to prove universality by force. It asks whether a bounded covariance rule survives once we demand:\n"
            "  1. multi-scale ESM replication,\n"
            "  2. cross-family replication,\n"
            "  3. cross-architecture replication,\n"
            "  4. structural agreement,\n"
            "  5. stronger controls than chemistry-only or scalar-only heuristics.\n"
            "- The notebook degrades honestly: models may fail, families may fail, and those failures are part of the result rather than hidden exceptions.\n"
        ),
        code_cell(
            dedent(
                """
                # Setup: imports, runtime requirements, notebook identifiers, and the multifamily roster
                from __future__ import annotations

                import importlib
                import json
                import math
                import os
                import platform
                import random
                import shutil
                import subprocess
                import sys
                import time
                import urllib.request
                import zipfile
                from importlib import metadata as importlib_metadata
                from datetime import datetime, timezone
                from pathlib import Path

                from IPython.display import display

                NOTEBOOK_SLUG = '12b_block12_multifamily_coverage_aware_generalization_h100'
                ACCOUNT_LABEL = os.environ.get('SPECTRALBIO_ACCOUNT_LABEL', 'local_run')
                RUN_AT = datetime.now(timezone.utc).isoformat()
                OVERWRITE = os.environ.get('SPECTRALBIO_OVERWRITE', '').strip().lower() in {'1', 'true', 'yes'}
                SKIP_LIVE = os.environ.get('SPECTRALBIO_BLOCK12B_SKIP_LIVE', '').strip().lower() in {'1', 'true', 'yes'}
                WINDOW_RADIUS = int(os.environ.get('SPECTRALBIO_BLOCK12B_WINDOW_RADIUS', '40'))
                CHECKPOINT_EVERY = int(os.environ.get('SPECTRALBIO_BLOCK12B_CHECKPOINT_EVERY', '10'))
                MAX_VARIANTS = int(os.environ.get('SPECTRALBIO_BLOCK12B_MAX_VARIANTS', '255'))
                FIXED_ALPHA = float(os.environ.get('SPECTRALBIO_BLOCK12B_FIXED_ALPHA', '0.55'))
                ALPHA_STEP = float(os.environ.get('SPECTRALBIO_BLOCK12B_ALPHA_STEP', '0.05'))
                BOOTSTRAP_REPLICATES = int(os.environ.get('SPECTRALBIO_BLOCK12B_BOOTSTRAP_REPLICATES', '2000'))
                RANDOM_REPLICATES = int(os.environ.get('SPECTRALBIO_BLOCK12B_RANDOM_REPLICATES', '400'))
                RANDOM_SEED = int(os.environ.get('SPECTRALBIO_BLOCK12B_RANDOM_SEED', '42'))
                MIN_RULE_ON_ABS = int(os.environ.get('SPECTRALBIO_BLOCK12B_MIN_RULE_ON_ABS', '10'))
                MIN_RULE_ON_FRAC = float(os.environ.get('SPECTRALBIO_BLOCK12B_MIN_RULE_ON_FRAC', '0.05'))
                MINI_HOLDOUT_MAX_ROWS = int(os.environ.get('SPECTRALBIO_BLOCK12B_MINI_HOLDOUT_MAX_ROWS', '12'))
                MODEL_FILTER = {
                    item.strip().lower()
                    for item in os.environ.get('SPECTRALBIO_BLOCK12B_MODEL_FILTER', '').split(',')
                    if item.strip()
                }
                RULE_THRESHOLDS = [
                    float(value.strip())
                    for value in os.environ.get('SPECTRALBIO_BLOCK12B_RULE_THRESHOLDS', '0.05,0.10,0.15,0.20,0.25').split(',')
                    if value.strip()
                ]
                CONFIDENCE_THRESHOLDS = [
                    float(value.strip())
                    for value in os.environ.get('SPECTRALBIO_BLOCK12B_CONF_THRESHOLDS', '0.55,0.60,0.65').split(',')
                    if value.strip()
                ]

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
                    return _Requirement(spec)

                def requirement_is_satisfied(spec: str, installed_version: str | None) -> bool:
                    if not installed_version:
                        return False
                    requirement = parse_requirement(spec)
                    if not requirement.specifier:
                        return True
                    return requirement.specifier.contains(installed_version, prereleases=True)

                def clear_imported_modules(import_name: str) -> None:
                    prefixes = {import_name, import_name.split('.')[0]}
                    for loaded_name in list(sys.modules):
                        if any(loaded_name == prefix or loaded_name.startswith(prefix + '.') for prefix in prefixes):
                            sys.modules.pop(loaded_name, None)

                install_specs: list[str] = []
                runtime_rows = []
                for module_name, package_spec, import_name in runtime_requirements:
                    requirement = parse_requirement(package_spec)
                    try:
                        module = importlib.import_module(import_name)
                        version = str(
                            getattr(module, '__version__', None)
                            or importlib_metadata.version(requirement.name)
                        )
                        if requirement_is_satisfied(package_spec, version):
                            runtime_rows.append({'module': module_name, 'status': 'present', 'version': version})
                        else:
                            install_specs.append(package_spec)
                            runtime_rows.append({'module': module_name, 'status': 'upgrade_needed', 'version': version})
                    except Exception:
                        install_specs.append(package_spec)
                        runtime_rows.append({'module': module_name, 'status': 'missing', 'version': 'n/a'})

                if install_specs:
                    deduped_specs = list(dict.fromkeys(install_specs))
                    subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', *deduped_specs], check=True, text=True)
                    importlib.invalidate_caches()
                    for _, _, import_name in runtime_requirements:
                        clear_imported_modules(import_name)
                    runtime_rows = []
                    for module_name, _, import_name in runtime_requirements:
                        module = importlib.import_module(import_name)
                        version = getattr(module, '__version__', 'present')
                        runtime_rows.append({'module': module_name, 'status': 'installed_now', 'version': str(version)})

                import matplotlib.pyplot as plt
                import numpy as np
                import pandas as pd

                random.seed(RANDOM_SEED)
                np.random.seed(RANDOM_SEED)

                print({
                    'notebook_slug': NOTEBOOK_SLUG,
                    'account_label': ACCOUNT_LABEL,
                    'skip_live': SKIP_LIVE,
                    'fixed_alpha': FIXED_ALPHA,
                    'alpha_step': ALPHA_STEP,
                    'rule_thresholds': RULE_THRESHOLDS,
                    'confidence_thresholds': CONFIDENCE_THRESHOLDS,
                    'min_rule_on_abs': MIN_RULE_ON_ABS,
                    'min_rule_on_frac': MIN_RULE_ON_FRAC,
                    'bootstrap_replicates': BOOTSTRAP_REPLICATES,
                    'random_replicates': RANDOM_REPLICATES,
                    'mini_holdout_max_rows': MINI_HOLDOUT_MAX_ROWS,
                    'models': [spec['model_label'] for spec in MODEL_SPECS],
                    'python': sys.version.split()[0],
                    'platform': platform.platform(),
                    'runtime': runtime_rows,
                })
                done('Environment prepared for the multifamily coverage-aware generalization notebook.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Helpers: repo discovery, path resolution, statistics, chemistry logic, and model adapters
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

                def resolve_existing_path(*candidates: str | Path) -> Path:
                    repo_root = find_repo_root()
                    for raw in candidates:
                        raw_path = Path(raw)
                        if raw_path.exists():
                            return raw_path.resolve()
                        raw_text = str(raw).replace('\\\\', '/')
                        for prefix in ('/content/Stanford-Claw4s/', '/teamspace/studios/this_studio/Stanford-Claw4s/', '/teamspace/studios/this_studio/SpectralBio/'):
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

                def run(command: list[str], cwd: Path | None = None, check: bool = True) -> str:
                    completed = subprocess.run(
                        command,
                        cwd=str(cwd) if cwd is not None else None,
                        check=check,
                        text=True,
                        encoding='utf-8',
                        errors='replace',
                        capture_output=True,
                    )
                    if completed.stdout.strip():
                        print(completed.stdout.strip())
                    if completed.stderr.strip():
                        print(completed.stderr.strip())
                    return completed.stdout

                def safe_float(value, default: float = float('nan')) -> float:
                    try:
                        if value is None:
                            return float(default)
                        if isinstance(value, str) and not value.strip():
                            return float(default)
                        return float(value)
                    except Exception:
                        return float(default)

                def clip01(value: float) -> float:
                    return max(0.0, min(1.0, float(value)))

                def coverage_floor(n_rows: int) -> int:
                    return int(max(MIN_RULE_ON_ABS, math.ceil(float(n_rows) * MIN_RULE_ON_FRAC)))

                def weighted_mean(values: np.ndarray, weights: np.ndarray) -> float:
                    values = np.asarray(values, dtype=float)
                    weights = np.asarray(weights, dtype=float)
                    mask = np.isfinite(values) & np.isfinite(weights) & (weights > 0)
                    if not mask.any():
                        return float('nan')
                    return float(np.average(values[mask], weights=weights[mask]))

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

                def same_position_top_hit_rate(frame: pd.DataFrame, score_col: str) -> dict[str, float]:
                    if score_col not in frame.columns or frame.empty:
                        return {'n_mixed_positions': 0, 'top_hit_pathogenic_rate': float('nan')}
                    evaluable = []
                    for _, group in frame.groupby('position'):
                        labels = group['label'].astype(int)
                        if labels.nunique() < 2 or len(group) < 2:
                            continue
                        top_row = group.sort_values(score_col, ascending=False).iloc[0]
                        evaluable.append(int(top_row['label']))
                    if not evaluable:
                        return {'n_mixed_positions': 0, 'top_hit_pathogenic_rate': float('nan')}
                    return {
                        'n_mixed_positions': int(len(evaluable)),
                        'top_hit_pathogenic_rate': float(np.mean(evaluable)),
                    }

                AA_BUCKETS = {
                    'A': 'small_hydrophobic',
                    'V': 'small_hydrophobic',
                    'I': 'large_hydrophobic',
                    'L': 'large_hydrophobic',
                    'M': 'large_hydrophobic',
                    'F': 'aromatic',
                    'Y': 'aromatic',
                    'W': 'aromatic',
                    'S': 'polar',
                    'T': 'polar',
                    'N': 'polar',
                    'Q': 'polar',
                    'C': 'sulfur',
                    'G': 'glycine',
                    'P': 'proline',
                    'D': 'acidic',
                    'E': 'acidic',
                    'K': 'basic',
                    'R': 'basic',
                    'H': 'basic',
                }

                TP53_HOTSPOTS = {175, 179, 220, 245, 248, 249, 273, 282}

                TP53_DOMAIN_MAP = {
                    'transactivation': (1, 61),
                    'proline_rich': (62, 93),
                    'dna_binding': (94, 292),
                    'tetramerization': (325, 356),
                    'regulatory': (357, 393),
                }

                def aa_bucket(residue: str) -> str:
                    return AA_BUCKETS.get(str(residue).upper(), 'other')

                def chemistry_trigger_from_columns(frame: pd.DataFrame) -> pd.Series:
                    wt_bucket = frame['wt_aa'].astype(str).str.upper().map(aa_bucket)
                    mut_bucket = frame['mut_aa'].astype(str).str.upper().map(aa_bucket)
                    return (
                        (mut_bucket.eq('basic') & ~wt_bucket.eq('basic'))
                        | frame['mut_aa'].astype(str).str.upper().eq('P')
                        | (mut_bucket.eq('aromatic') & ~wt_bucket.eq('aromatic'))
                    )

                def tp53_domain_label(position: int) -> str:
                    for label, (start, end) in TP53_DOMAIN_MAP.items():
                        if int(start) <= int(position) <= int(end):
                            return label
                    return 'outside_defined_domain'

                def normalize_protein_sequence(sequence: str, mode: str) -> str:
                    import re
                    clean = re.sub(r'[UZOB]', 'X', str(sequence).upper())
                    if mode == 'spaced':
                        return ' '.join(list(clean))
                    return clean

                def fetch_uniprot_fasta(accession: str, cache_dir: Path) -> str:
                    accession = str(accession).strip()
                    cache_path = cache_dir / f'{accession}.fasta'
                    if not cache_path.exists():
                        url = f'https://rest.uniprot.org/uniprotkb/{accession}.fasta'
                        with urllib.request.urlopen(url, timeout=60) as response:
                            text = response.read().decode('utf-8')
                        cache_path.write_text(text, encoding='utf-8')
                    lines = [line.strip() for line in cache_path.read_text(encoding='utf-8').splitlines() if line.strip()]
                    return ''.join(line for line in lines if not line.startswith('>'))

                def validate_panel_against_sequences(panel_df: pd.DataFrame, sequence_map: dict[str, str], panel_name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
                    audit_cols = ['panel_name', 'gene', 'variant_id', 'name', 'position', 'wt_aa', 'mut_aa', 'reason', 'observed_residue']
                    if panel_df.empty:
                        return panel_df.copy(), pd.DataFrame(columns=audit_cols)
                    valid_rows = []
                    mismatch_rows = []
                    for row in panel_df.to_dict(orient='records'):
                        gene = str(row.get('gene', '')).upper()
                        sequence = str(sequence_map.get(gene, '')).upper()
                        position = int(row.get('position', -1))
                        wt_aa = str(row.get('wt_aa', '')).upper()
                        observed = None
                        reason = None
                        if not sequence:
                            reason = 'missing_sequence'
                        elif position < 0 or position >= len(sequence):
                            reason = 'position_out_of_range'
                        else:
                            observed = sequence[position].upper()
                            if observed != wt_aa:
                                reason = 'wt_mismatch'
                        if reason is None:
                            valid_rows.append(row)
                        else:
                            mismatch_rows.append({
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
                    valid_df = pd.DataFrame(valid_rows)
                    if valid_df.empty:
                        valid_df = panel_df.iloc[0:0].copy()
                    mismatch_df = pd.DataFrame(mismatch_rows, columns=audit_cols)
                    return valid_df, mismatch_df

                REPO_ROOT = find_repo_root()
                RESULTS_DIR = REPO_ROOT / 'New Notebooks' / 'results'
                SHARED_INPUTS_DIR = REPO_ROOT / 'New Notebooks' / 'shared_inputs' / 'reviewer_chain_upstream'
                RESULTS_ROOT = ensure_dir(RESULTS_DIR / NOTEBOOK_SLUG)
                TABLES_DIR = ensure_dir(RESULTS_ROOT / 'tables')
                FIGURES_DIR = ensure_dir(RESULTS_ROOT / 'figures')
                TEXT_DIR = ensure_dir(RESULTS_ROOT / 'text')
                MANIFESTS_DIR = ensure_dir(RESULTS_ROOT / 'manifests')
                RUNTIME_DIR = ensure_dir(RESULTS_ROOT / 'runtime')
                LIVE_SCORES_DIR = ensure_dir(RESULTS_ROOT / 'live_scores')
                CACHE_DIR = ensure_dir(RUNTIME_DIR / 'sequence_cache')
                ZIP_PATH = RESULTS_DIR / f'{NOTEBOOK_SLUG}.zip'

                src_path = REPO_ROOT / 'src'
                if str(src_path) not in sys.path:
                    sys.path.insert(0, str(src_path))
                subprocess.run([sys.executable, '-m', 'pip', 'install', '-e', '.', '--no-deps'], cwd=str(REPO_ROOT), check=False)

                def clear_modules(prefixes: list[str]) -> None:
                    for module_name in list(sys.modules):
                        if any(module_name == prefix or module_name.startswith(prefix + '.') for prefix in prefixes):
                            sys.modules.pop(module_name, None)

                def apply_transformers_torchvision_hotfix() -> None:
                    os.environ['DISABLE_TRANSFORMERS_AV'] = '1'
                    os.environ['TRANSFORMERS_NO_TORCHVISION'] = '1'
                    try:
                        import transformers.utils as tutils
                        import transformers.utils.import_utils as tiu

                        tiu._torchvision_available = False
                        try:
                            tiu._torchvision_version = '0.0'
                        except Exception:
                            pass
                        tiu.is_torchvision_available = lambda: False
                        tutils.is_torchvision_available = lambda: False
                    except Exception:
                        pass

                apply_transformers_torchvision_hotfix()
                clear_modules(['torchvision', 'transformers.image_utils', 'transformers.image_transforms', 'transformers.loss'])

                from spectralbio.supplementary.reject_recovery import (
                    _alpha_sweep_on_rows,
                    _ensure_gene_score_rows,
                    _pair_scores,
                    _score_rows_summary,
                    covariance_features_dual,
                )

                import torch
                from transformers import AutoModel, AutoModelForCausalLM, AutoTokenizer, T5EncoderModel, T5Tokenizer

                def select_hidden_layers(hidden_states) -> list:
                    core = list(hidden_states[1:]) if len(hidden_states) > 1 else list(hidden_states)
                    return list(core[-4:]) if len(core) >= 4 else list(core)

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

                        probe = 'ACDEFGHIKLMNPQRSTVWY'
                        encoded = tokenizer(
                            normalize_protein_sequence(probe, spec['sequence_mode']),
                            return_tensors='pt',
                            add_special_tokens=False,
                        )
                        residue_token_count = int(encoded['input_ids'].shape[1])
                        manifest.update({
                            'status': 'loaded',
                            'device': device,
                            'torch_dtype': str(torch_dtype),
                            'token_probe_length': residue_token_count,
                            'token_probe_matches_residue_count': bool(residue_token_count == len(probe)),
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
                            mut_token_count = int(mut_encoded['input_ids'].shape[1])
                            if mut_token_count != len(mutated_local):
                                raise RuntimeError(
                                    f'Mut tokenization mismatch for {spec["model_label"]}: expected {len(mutated_local)} residues, got {mut_token_count} tokens'
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
                        rows = _ensure_gene_score_rows(
                            gene=str(panel_df['gene'].iloc[0]).upper(),
                            sequence=sequence_map[str(panel_df['gene'].iloc[0]).upper()],
                            variants=panel_df[['gene', 'name', 'position', 'wt_aa', 'mut_aa', 'label', 'variant_id']].to_dict(orient='records'),
                            model_name=spec['model_name'],
                            output_dir=output_path.parent,
                            window_radius=WINDOW_RADIUS,
                            checkpoint_every=CHECKPOINT_EVERY,
                            overwrite=OVERWRITE,
                        )
                        output = pd.DataFrame(rows)
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
                    'head_commit': run(['git', 'rev-parse', 'HEAD'], cwd=REPO_ROOT).strip(),
                    'branch': run(['git', 'branch', '--show-current'], cwd=REPO_ROOT).strip(),
                    'skip_live': SKIP_LIVE,
                    'fixed_alpha': FIXED_ALPHA,
                    'cuda_available': bool(torch.cuda.is_available()),
                    'cuda_device_count': int(torch.cuda.device_count()) if torch.cuda.is_available() else 0,
                    'cuda_device_name': torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu',
                }
                (RUNTIME_DIR / 'runtime_manifest.json').write_text(json.dumps(runtime_manifest, indent=2), encoding='utf-8')
                display(pd.DataFrame([runtime_manifest]))
                done('Helpers, repo wiring, statistics, and model adapters are ready.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Load the TP53 benchmark, structural references, and a compact non-TP53 transfer holdout
                canonical_variants = json.loads(resolve_existing_path(REPO_ROOT / 'benchmarks' / 'tp53' / 'tp53_canonical_v1.json').read_text(encoding='utf-8'))
                canonical_panel = pd.DataFrame(canonical_variants)
                canonical_panel['gene'] = canonical_panel['gene'].astype(str).str.upper()
                canonical_panel['variant_id'] = (
                    canonical_panel['gene'].astype(str)
                    + ':'
                    + canonical_panel['wt_aa'].astype(str).str.upper()
                    + canonical_panel['position'].astype(int).astype(str)
                    + canonical_panel['mut_aa'].astype(str).str.upper()
                )
                canonical_panel = canonical_panel.loc[canonical_panel['gene'].eq('TP53')].copy()
                canonical_panel = canonical_panel.sort_values(['position', 'mut_aa']).head(MAX_VARIANTS).reset_index(drop=True)
                canonical_panel['panel_name'] = 'tp53'

                frozen_scores = pd.DataFrame(json.loads(resolve_existing_path(REPO_ROOT / 'benchmarks' / 'tp53' / 'tp53_scores_v1.json').read_text(encoding='utf-8')))
                frozen_scores['variant_id'] = (
                    'TP53:'
                    + frozen_scores['wt_aa'].astype(str).str.upper()
                    + frozen_scores['position'].astype(int).astype(str)
                    + frozen_scores['mut_aa'].astype(str).str.upper()
                )

                structural_candidates = [
                    RESULTS_DIR / '07b_block10_structural_dissociation_tp53_h100' / '07b_block10_structural_dissociation_tp53_h100' / 'tables' / 'tp53_structural_pairs_variant_level_strict.csv',
                    RESULTS_DIR / '07b_block10_structural_dissociation_tp53_h100' / 'tables' / 'tp53_structural_pairs_variant_level_strict.csv',
                    RESULTS_DIR / '07c_block10_structural_dissociation_tp53_h100' / '07c_block10_structural_dissociation_tp53_h100' / 'tables' / 'tp53_structural_pairs_variant_level_strict.csv',
                    RESULTS_DIR / '07c_block10_structural_dissociation_tp53_h100' / 'tables' / 'tp53_structural_pairs_variant_level_strict.csv',
                    SHARED_INPUTS_DIR / 'block10' / 'tp53_structural_pairs_variant_level_strict.csv',
                ]
                structural_broad_candidates = [
                    RESULTS_DIR / '07b_block10_structural_dissociation_tp53_h100' / '07b_block10_structural_dissociation_tp53_h100' / 'tables' / 'tp53_structural_pairs_variant_level_broad.csv',
                    RESULTS_DIR / '07b_block10_structural_dissociation_tp53_h100' / 'tables' / 'tp53_structural_pairs_variant_level_broad.csv',
                    SHARED_INPUTS_DIR / 'block10' / 'tp53_structural_pairs_variant_level_broad.csv',
                ]

                structural_path = next((candidate for candidate in structural_candidates if candidate.exists()), None)
                structural_broad_path = next((candidate for candidate in structural_broad_candidates if candidate.exists()), None)
                if structural_path is not None:
                    tp53_structural_strict = pd.read_csv(structural_path)
                    structural_status = 'strict_loaded'
                elif structural_broad_path is not None:
                    tp53_structural_strict = pd.read_csv(structural_broad_path)
                    structural_status = 'broad_fallback_loaded'
                else:
                    tp53_structural_strict = pd.DataFrame(columns=[
                        'variant_id',
                        'excess_local_rmsd_median',
                        'contact_change_fraction_median',
                        'pair_rank_norm',
                        'll_rank_norm',
                    ])
                    structural_status = 'missing_structural_reference'

                decision_panel_candidates = [
                    RESULTS_DIR / '11_block11_covariance_rulebook_h100' / 'tables' / 'rulebook_decision_panel.csv',
                    SHARED_INPUTS_DIR / 'block11' / 'rulebook_decision_panel.csv',
                ]
                gallery_candidates = [
                    RESULTS_DIR / '08_block7_turbo_gallery_rescues_h100' / 'tables' / 'gallery_final_cases.csv',
                    SHARED_INPUTS_DIR / 'block7' / 'gallery_final_cases.csv',
                ]
                counterexample_candidates = [
                    RESULTS_DIR / '06_block5_clinical_panel_audit_h100' / 'tables' / 'clinical_counterexample_cases.csv',
                    SHARED_INPUTS_DIR / 'block6' / 'clinical_counterexample_cases.csv',
                ]

                decision_panel_path = next((candidate for candidate in decision_panel_candidates if candidate.exists()), None)
                gallery_path = next((candidate for candidate in gallery_candidates if candidate.exists()), None)
                counterexample_path = next((candidate for candidate in counterexample_candidates if candidate.exists()), None)

                holdout_panel = pd.DataFrame()
                holdout_status = 'missing_optional_holdout'
                if decision_panel_path is not None:
                    decision_panel = pd.read_csv(decision_panel_path)
                    decision_panel = decision_panel.loc[
                        decision_panel['gene'].astype(str).str.upper().ne('TP53')
                        & decision_panel['uniprot_accession'].astype(str).str.len().gt(2)
                    ].copy()
                    positives = decision_panel.loc[decision_panel['rule_panel_label'].fillna(0).astype(int).eq(1)].copy()
                    negatives = decision_panel.loc[decision_panel['rule_panel_label'].fillna(0).astype(int).eq(0)].copy()
                    pos_rank_col = 'rulebook_score' if 'rulebook_score' in positives.columns else 'gallery_priority_score'
                    neg_rank_col = 'anti_case_score' if 'anti_case_score' in negatives.columns else 'clinical_rescue_margin'
                    pos_take = max(2, MINI_HOLDOUT_MAX_ROWS // 2)
                    neg_take = max(2, MINI_HOLDOUT_MAX_ROWS - pos_take)
                    positive_holdout = positives.sort_values(pos_rank_col, ascending=False).head(pos_take)
                    negative_holdout = negatives.sort_values(neg_rank_col, ascending=True).head(neg_take)
                    holdout_panel = pd.concat([positive_holdout, negative_holdout], ignore_index=True, sort=False)
                    holdout_panel = holdout_panel[['gene', 'name', 'position', 'wt_aa', 'mut_aa', 'label', 'variant_id', 'uniprot_accession']].copy()
                    holdout_panel['panel_name'] = 'mini_holdout_non_tp53'
                    holdout_status = 'rulebook_holdout_loaded'
                elif gallery_path is not None and counterexample_path is not None:
                    gallery_final = pd.read_csv(gallery_path)
                    clinical_counterexamples = pd.read_csv(counterexample_path)
                    gallery_final = gallery_final.loc[
                        gallery_final['gene'].astype(str).str.upper().ne('TP53')
                        & gallery_final['uniprot_accession'].astype(str).str.len().gt(2)
                    ].copy()
                    clinical_counterexamples = clinical_counterexamples.loc[
                        clinical_counterexamples['gene'].astype(str).str.upper().ne('TP53')
                    ].copy()
                    accession_map = gallery_final[['gene', 'uniprot_accession']].dropna().drop_duplicates()
                    clinical_counterexamples = clinical_counterexamples.merge(accession_map, on='gene', how='left')
                    positive_holdout = gallery_final.sort_values('clinical_rescue_margin', ascending=False).head(max(2, MINI_HOLDOUT_MAX_ROWS // 2))
                    negative_holdout = clinical_counterexamples.loc[
                        clinical_counterexamples['uniprot_accession'].astype(str).str.len().gt(2)
                    ].sort_values('clinical_rescue_margin', ascending=True).head(max(2, MINI_HOLDOUT_MAX_ROWS // 2))
                    holdout_panel = pd.concat([positive_holdout, negative_holdout], ignore_index=True, sort=False)
                    holdout_panel = holdout_panel[['gene', 'name', 'position', 'wt_aa', 'mut_aa', 'label', 'variant_id', 'uniprot_accession']].copy()
                    holdout_panel['panel_name'] = 'mini_holdout_non_tp53'
                    holdout_status = 'gallery_counterexample_fallback_loaded'

                sequence_map = {'TP53': fetch_uniprot_fasta('P04637', CACHE_DIR)}
                for record in holdout_panel[['gene', 'uniprot_accession']].drop_duplicates().to_dict(orient='records'):
                    accession = str(record.get('uniprot_accession', '')).strip()
                    if accession:
                        sequence_map[str(record['gene']).upper()] = fetch_uniprot_fasta(accession, CACHE_DIR)

                canonical_panel_valid, canonical_panel_mismatches = validate_panel_against_sequences(canonical_panel, sequence_map, 'tp53')
                if not canonical_panel_mismatches.empty:
                    canonical_panel_mismatches.to_csv(TABLES_DIR / 'tp53_sequence_validation_mismatches.csv', index=False)
                    raise ValueError(
                        'TP53 canonical panel contains WT/sequence mismatches. '
                        'See tables/tp53_sequence_validation_mismatches.csv before continuing.'
                    )
                holdout_panel_valid, holdout_panel_mismatches = validate_panel_against_sequences(holdout_panel, sequence_map, 'mini_holdout_non_tp53')
                canonical_panel = canonical_panel_valid.copy()
                holdout_panel = holdout_panel_valid.copy()

                canonical_panel.to_csv(TABLES_DIR / 'tp53_canonical_panel.csv', index=False)
                frozen_scores.to_csv(TABLES_DIR / 'tp53_frozen_scores_reference.csv', index=False)
                tp53_structural_strict.to_csv(TABLES_DIR / 'tp53_structural_reference.csv', index=False)
                holdout_panel.to_csv(TABLES_DIR / 'mini_holdout_non_tp53_panel.csv', index=False)
                holdout_panel_mismatches.to_csv(TABLES_DIR / 'mini_holdout_non_tp53_sequence_validation_mismatches.csv', index=False)

                panel_manifest = {
                    'tp53_rows': int(len(canonical_panel)),
                    'holdout_rows': int(len(holdout_panel)),
                    'holdout_filtered_mismatches': int(len(holdout_panel_mismatches)),
                    'holdout_status': holdout_status,
                    'structural_status': structural_status,
                    'structural_rows': int(len(tp53_structural_strict)),
                    'sequence_genes': sorted(sequence_map),
                }
                (RUNTIME_DIR / 'panel_manifest.json').write_text(json.dumps(panel_manifest, indent=2), encoding='utf-8')
                display(pd.DataFrame([panel_manifest]))
                display(canonical_panel.head(5))
                display(holdout_panel.head(5))
                display(holdout_panel_mismatches.head(10))
                done('TP53 benchmark, structural references, and the compact non-TP53 holdout are loaded.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Run the live TP53 panel and the mini transfer holdout across the multifamily roster
                live_frames = []
                runtime_rows = []

                if SKIP_LIVE:
                    runtime_note = pd.DataFrame([{
                        'status': 'skip_live_enabled',
                        'message': 'Set SPECTRALBIO_BLOCK12B_SKIP_LIVE=0 on H100 to execute the full multifamily run.',
                    }])
                    runtime_note.to_csv(TABLES_DIR / 'live_runtime_note.csv', index=False)
                    display(runtime_note)
                else:
                    panels = [('tp53', canonical_panel)]
                    if not holdout_panel.empty:
                        panels.append(('mini_holdout_non_tp53', holdout_panel))

                    for spec in MODEL_SPECS:
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
                            runtime_rows.append(manifest)
                            if not scored_df.empty:
                                scored_df = scored_df.copy()
                                scored_df['model_label'] = spec['model_label']
                                scored_df['family_label'] = spec['family_label']
                                scored_df['architecture_kind'] = spec['architecture_kind']
                                scored_df['adapter_kind'] = spec['adapter_kind']
                                scored_df['sequence_mode'] = spec['sequence_mode']
                                scored_df['panel_name'] = panel_name
                                scored_df['scale_bucket'] = spec['scale_bucket']
                                live_frames.append(scored_df)

                live_scores = pd.concat(live_frames, ignore_index=True, sort=False) if live_frames else pd.DataFrame()
                runtime_manifest_df = pd.DataFrame(runtime_rows)

                if not live_scores.empty:
                    live_scores.to_csv(TABLES_DIR / 'multifamily_live_model_rows.csv', index=False)
                    display(live_scores[['panel_name', 'variant_id', 'model_label', 'frob_dist', 'll_proper']].head(20))
                runtime_manifest_df.to_csv(TABLES_DIR / 'per_model_runtime_manifest.csv', index=False)
                display(runtime_manifest_df)
                done('Live multifamily scoring is finished and all runtime manifests are written.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Feature engineering, rule calibration, pairwise controls, and per-model summaries
                def compute_rule_mask(frame: pd.DataFrame, rule_type: str, threshold: float, confidence_threshold: float | None = None) -> pd.Series:
                    if rule_type == 'chemistry_only':
                        return frame['chemistry_trigger'].fillna(False).astype(bool)
                    if rule_type == 'pair_only':
                        return frame['pair_minus_ll'].fillna(-999.0) >= float(threshold)
                    if rule_type == 'scalar_only':
                        return frame['ll_rank_norm'].fillna(-999.0) >= float(threshold)
                    if rule_type == 'combined':
                        return frame['chemistry_trigger'].fillna(False).astype(bool) & (frame['pair_minus_ll'].fillna(-999.0) >= float(threshold))
                    if rule_type == 'combined_confident':
                        conf = 0.60 if confidence_threshold is None else float(confidence_threshold)
                        return (
                            frame['chemistry_trigger'].fillna(False).astype(bool)
                            & (frame['pair_minus_ll'].fillna(-999.0) >= float(threshold))
                            & (frame['pair_rank_fixed_055'].fillna(-999.0) >= conf)
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
                    preferred_order = {
                        'combined_confident': 0,
                        'combined': 1,
                        'pair_only': 2,
                        'chemistry_only': 3,
                        'scalar_only': 4,
                    }
                    ranked = candidate_df.copy()
                    ranked['rule_priority'] = ranked['rule_type'].map(preferred_order).fillna(99).astype(int)
                    ranked['coverage_pass_int'] = ranked['coverage_floor_pass'].fillna(False).astype(int)
                    ranked = ranked.sort_values(
                        ['coverage_pass_int', 'enrichment_gap', 'odds_ratio', 'n_rule_on', 'rule_priority'],
                        ascending=[False, False, False, False, True],
                    ).reset_index(drop=True)
                    return ranked.iloc[0]

                if SKIP_LIVE or live_scores.empty:
                    summary_payload = {
                        'notebook_slug': NOTEBOOK_SLUG,
                        'run_at_utc': RUN_AT,
                        'account_label': ACCOUNT_LABEL,
                        'status': 'skip_live_or_no_scores',
                        'claim_status': 'not_run',
                        'claim_reason': 'Notebook executed without live multifamily scoring.',
                    }
                    (MANIFESTS_DIR / 'block12b_multifamily_summary.json').write_text(json.dumps(summary_payload, indent=2), encoding='utf-8')
                    (MANIFESTS_DIR / 'artifact_summary.json').write_text(json.dumps(summary_payload, indent=2), encoding='utf-8')
                    print(json.dumps(summary_payload, indent=2))
                    done('Skip-live validation path completed.')
                else:
                    tp53_live = live_scores.loc[live_scores['panel_name'].eq('tp53')].copy()
                    holdout_live = live_scores.loc[live_scores['panel_name'].eq('mini_holdout_non_tp53')].copy()

                    model_variant_frames = []
                    model_summary_rows = []
                    alpha_sweep_rows = []
                    calibration_rows = []
                    selected_rule_rows = []
                    structural_rows = []
                    same_position_rows = []
                    robustness_rows = []
                    holdout_rows = []
                    control_rows = []
                    failure_rows = []

                    for spec in MODEL_SPECS:
                        model_label = spec['model_label']
                        model_tp53 = tp53_live.loc[tp53_live['model_label'].eq(model_label)].copy()
                        if model_tp53.empty:
                            failure_rows.append({
                                'model_label': model_label,
                                'family_label': spec['family_label'],
                                'architecture_kind': spec['architecture_kind'],
                                'failure_taxonomy': 'runtime_or_loading_failure',
                                'reason': 'No TP53 live rows were produced for this model.',
                            })
                            continue

                        rows = model_tp53[['gene', 'name', 'position', 'wt_aa', 'mut_aa', 'label', 'frob_dist', 'trace_ratio', 'sps_log', 'll_proper', 'model_name', 'variant_id']].to_dict(orient='records')
                        score_payload = _pair_scores(rows, FIXED_ALPHA)
                        summary = _score_rows_summary(rows, FIXED_ALPHA)
                        sweep_rows, best_alpha = _alpha_sweep_on_rows(rows, ALPHA_STEP)
                        for sweep_row in sweep_rows:
                            alpha_sweep_rows.append({
                                'model_label': model_label,
                                'family_label': spec['family_label'],
                                'architecture_kind': spec['architecture_kind'],
                                **sweep_row,
                            })

                        model_tp53['ll_rank_norm'] = score_payload['ll_norm']
                        model_tp53['frob_rank_norm'] = score_payload['frob_norm']
                        model_tp53['pair_rank_fixed_055'] = score_payload['pair']
                        model_tp53['pair_minus_ll'] = model_tp53['pair_rank_fixed_055'] - model_tp53['ll_rank_norm']
                        model_tp53['wt_bucket'] = model_tp53['wt_aa'].astype(str).str.upper().map(aa_bucket)
                        model_tp53['mut_bucket'] = model_tp53['mut_aa'].astype(str).str.upper().map(aa_bucket)
                        model_tp53['chemistry_trigger'] = chemistry_trigger_from_columns(model_tp53)
                        model_tp53['tp53_hotspot'] = model_tp53['position'].astype(int).isin(TP53_HOTSPOTS)
                        model_tp53['tp53_domain'] = model_tp53['position'].astype(int).map(tp53_domain_label)
                        model_tp53['structure_available'] = False
                        model_tp53['geometry_targeted'] = False

                        merged_structural = model_tp53.merge(tp53_structural_strict, on='variant_id', how='left', suffixes=('', '_strict'))
                        if 'excess_local_rmsd_median' in merged_structural.columns:
                            merged_structural['structure_available'] = pd.to_numeric(merged_structural['excess_local_rmsd_median'], errors='coerce').notna()
                            merged_structural['geometry_targeted'] = pd.to_numeric(merged_structural['excess_local_rmsd_median'], errors='coerce').fillna(-999.0) > 0.0
                        model_tp53 = merged_structural.copy()

                        model_variant_frames.append(model_tp53)
                        model_summary_rows.append({
                            'model_label': model_label,
                            'family_label': spec['family_label'],
                            'architecture_kind': spec['architecture_kind'],
                            'scale_bucket': spec['scale_bucket'],
                            'n_variants': int(len(model_tp53)),
                            'auc_ll_proper': float(summary['auc_ll_proper']),
                            'auc_frob_dist': float(summary['auc_frob_dist']),
                            'auc_pair_fixed_055': float(summary['auc_pair_fixed_055']),
                            'delta_pair_vs_ll': float(summary['delta_pair_vs_ll']),
                            'best_alpha': float(best_alpha['alpha']),
                            'best_auc': float(best_alpha['auc']),
                            'structural_overlap_rows': int(model_tp53['structure_available'].fillna(False).sum()),
                        })

                        coverage_target = coverage_floor(len(model_tp53))
                        for threshold in RULE_THRESHOLDS:
                            calibration_rows.append({
                                'model_label': model_label,
                                'family_label': spec['family_label'],
                                'architecture_kind': spec['architecture_kind'],
                                **summarize_rule(model_tp53, 'chemistry_only', threshold, None, coverage_target, RANDOM_SEED + len(calibration_rows)),
                            })
                            calibration_rows.append({
                                'model_label': model_label,
                                'family_label': spec['family_label'],
                                'architecture_kind': spec['architecture_kind'],
                                **summarize_rule(model_tp53, 'pair_only', threshold, None, coverage_target, RANDOM_SEED + len(calibration_rows)),
                            })
                            calibration_rows.append({
                                'model_label': model_label,
                                'family_label': spec['family_label'],
                                'architecture_kind': spec['architecture_kind'],
                                **summarize_rule(model_tp53, 'scalar_only', threshold, None, coverage_target, RANDOM_SEED + len(calibration_rows)),
                            })
                            calibration_rows.append({
                                'model_label': model_label,
                                'family_label': spec['family_label'],
                                'architecture_kind': spec['architecture_kind'],
                                **summarize_rule(model_tp53, 'combined', threshold, None, coverage_target, RANDOM_SEED + len(calibration_rows)),
                            })
                            for confidence_threshold in CONFIDENCE_THRESHOLDS:
                                calibration_rows.append({
                                    'model_label': model_label,
                                    'family_label': spec['family_label'],
                                    'architecture_kind': spec['architecture_kind'],
                                    **summarize_rule(model_tp53, 'combined_confident', threshold, confidence_threshold, coverage_target, RANDOM_SEED + len(calibration_rows)),
                                })

                        same_position_rows.append({
                            'model_label': model_label,
                            'family_label': spec['family_label'],
                            'architecture_kind': spec['architecture_kind'],
                            'score_type': 'pair_rank_fixed_055',
                            **same_position_top_hit_rate(model_tp53, 'pair_rank_fixed_055'),
                        })
                        same_position_rows.append({
                            'model_label': model_label,
                            'family_label': spec['family_label'],
                            'architecture_kind': spec['architecture_kind'],
                            'score_type': 'll_rank_norm',
                            **same_position_top_hit_rate(model_tp53, 'll_rank_norm'),
                        })
                        same_position_rows.append({
                            'model_label': model_label,
                            'family_label': spec['family_label'],
                            'architecture_kind': spec['architecture_kind'],
                            'score_type': 'pair_minus_ll',
                            **same_position_top_hit_rate(model_tp53, 'pair_minus_ll'),
                        })

                        candidate_df = pd.DataFrame([row for row in calibration_rows if row['model_label'] == model_label])
                        best_rule = select_best_rule(candidate_df)
                        if best_rule is None:
                            failure_rows.append({
                                'model_label': model_label,
                                'family_label': spec['family_label'],
                                'architecture_kind': spec['architecture_kind'],
                                'failure_taxonomy': 'calibration_failed',
                                'reason': 'No rule candidates were generated.',
                            })
                            continue

                        best_rule = best_rule.copy()
                        best_rule['selected'] = True
                        selected_rule_rows.append(best_rule.to_dict())
                        selected_mask = compute_rule_mask(
                            model_tp53,
                            str(best_rule['rule_type']),
                            float(best_rule['threshold']),
                            None if not math.isfinite(float(best_rule['confidence_threshold'])) else float(best_rule['confidence_threshold']),
                        )
                        model_tp53['selected_rule_hit'] = selected_mask.astype(bool)
                        model_tp53['selected_rule_type'] = str(best_rule['rule_type'])
                        model_tp53['selected_rule_threshold'] = float(best_rule['threshold'])

                        if model_tp53['structure_available'].fillna(False).any():
                            structural_subset = model_tp53.loc[model_tp53['structure_available'].fillna(False)].copy()
                            pair_corr = float(pd.Series(structural_subset['pair_minus_ll']).corr(pd.Series(structural_subset['excess_local_rmsd_median']), method='spearman'))
                            ll_corr = float(pd.Series(structural_subset['ll_rank_norm']).corr(pd.Series(structural_subset['excess_local_rmsd_median']), method='spearman'))
                            contact_corr = float(pd.Series(structural_subset['pair_minus_ll']).corr(pd.Series(structural_subset['contact_change_fraction_median']), method='spearman'))
                            on_mask_struct = structural_subset['selected_rule_hit'].fillna(False).astype(bool)
                            gap_struct = bootstrap_gap(
                                (pd.to_numeric(structural_subset['excess_local_rmsd_median'], errors='coerce').fillna(0.0) > 0.0).astype(int).to_numpy(),
                                on_mask_struct.to_numpy(),
                                BOOTSTRAP_REPLICATES,
                                RANDOM_SEED + 1000 + len(structural_rows),
                            )
                            structural_rows.append({
                                'model_label': model_label,
                                'family_label': spec['family_label'],
                                'architecture_kind': spec['architecture_kind'],
                                'n_structural_rows': int(len(structural_subset)),
                                'spearman_pair_minus_ll_vs_excess_local_rmsd': pair_corr,
                                'spearman_ll_rank_vs_excess_local_rmsd': ll_corr,
                                'spearman_pair_minus_ll_vs_contact_change_fraction': contact_corr,
                                'mean_excess_local_rmsd_rule_on': float(pd.to_numeric(structural_subset.loc[on_mask_struct, 'excess_local_rmsd_median'], errors='coerce').mean()) if on_mask_struct.any() else float('nan'),
                                'mean_excess_local_rmsd_rule_off': float(pd.to_numeric(structural_subset.loc[~on_mask_struct, 'excess_local_rmsd_median'], errors='coerce').mean()) if (~on_mask_struct).any() else float('nan'),
                                'structural_rule_on_fraction_positive_geometry': gap_struct['pathogenic_fraction_rule_on'],
                                'structural_rule_off_fraction_positive_geometry': gap_struct['pathogenic_fraction_rule_off'],
                                'structural_geometry_gap': gap_struct['enrichment_gap'],
                            })

                        for slice_name, slice_mask in [
                            ('full_tp53', np.ones(len(model_tp53), dtype=bool)),
                            ('leave_hotspot_out', ~model_tp53['tp53_hotspot'].fillna(False).astype(bool).to_numpy()),
                            ('dna_binding_only', model_tp53['tp53_domain'].astype(str).eq('dna_binding').to_numpy()),
                            ('leave_dna_binding_out', ~model_tp53['tp53_domain'].astype(str).eq('dna_binding').to_numpy()),
                        ]:
                            slice_df = model_tp53.loc[np.asarray(slice_mask, dtype=bool)].copy()
                            if slice_df.empty or slice_df['label'].astype(int).nunique() < 2:
                                continue
                            rows_slice = slice_df[['gene', 'name', 'position', 'wt_aa', 'mut_aa', 'label', 'frob_dist', 'trace_ratio', 'sps_log', 'll_proper', 'model_name', 'variant_id']].to_dict(orient='records')
                            slice_summary = _score_rows_summary(rows_slice, FIXED_ALPHA)
                            slice_mask_rule = compute_rule_mask(
                                slice_df,
                                str(best_rule['rule_type']),
                                float(best_rule['threshold']),
                                None if not math.isfinite(float(best_rule['confidence_threshold'])) else float(best_rule['confidence_threshold']),
                            )
                            slice_gap = bootstrap_gap(
                                slice_df['label'].astype(int).to_numpy(),
                                slice_mask_rule.to_numpy(),
                                BOOTSTRAP_REPLICATES,
                                RANDOM_SEED + 2000 + len(robustness_rows),
                            )
                            robustness_rows.append({
                                'model_label': model_label,
                                'family_label': spec['family_label'],
                                'architecture_kind': spec['architecture_kind'],
                                'slice_name': slice_name,
                                'n_rows': int(len(slice_df)),
                                'auc_pair_fixed_055': float(slice_summary['auc_pair_fixed_055']),
                                'delta_pair_vs_ll': float(slice_summary['delta_pair_vs_ll']),
                                'selected_rule_enrichment_gap': slice_gap['enrichment_gap'],
                                'selected_rule_on_fraction': float(slice_mask_rule.mean()),
                            })

                        if not holdout_live.empty:
                            model_holdout = holdout_live.loc[holdout_live['model_label'].eq(model_label)].copy()
                            if not model_holdout.empty:
                                holdout_rows_payload = model_holdout[['gene', 'name', 'position', 'wt_aa', 'mut_aa', 'label', 'frob_dist', 'trace_ratio', 'sps_log', 'll_proper', 'model_name', 'variant_id']].to_dict(orient='records')
                                holdout_score_payload = _pair_scores(holdout_rows_payload, FIXED_ALPHA)
                                model_holdout['ll_rank_norm'] = holdout_score_payload['ll_norm']
                                model_holdout['pair_rank_fixed_055'] = holdout_score_payload['pair']
                                model_holdout['pair_minus_ll'] = model_holdout['pair_rank_fixed_055'] - model_holdout['ll_rank_norm']
                                model_holdout['chemistry_trigger'] = chemistry_trigger_from_columns(model_holdout)
                                holdout_mask = compute_rule_mask(
                                    model_holdout,
                                    str(best_rule['rule_type']),
                                    float(best_rule['threshold']),
                                    None if not math.isfinite(float(best_rule['confidence_threshold'])) else float(best_rule['confidence_threshold']),
                                )
                                holdout_gap = bootstrap_gap(
                                    model_holdout['label'].astype(int).to_numpy(),
                                    holdout_mask.to_numpy(),
                                    BOOTSTRAP_REPLICATES,
                                    RANDOM_SEED + 3000 + len(holdout_rows),
                                )
                                holdout_rows.append({
                                    'model_label': model_label,
                                    'family_label': spec['family_label'],
                                    'architecture_kind': spec['architecture_kind'],
                                    'n_holdout_rows': int(len(model_holdout)),
                                    'n_holdout_rule_on': int(holdout_mask.sum()),
                                    'holdout_rule_on_fraction': float(holdout_mask.mean()),
                                    'holdout_enrichment_gap': holdout_gap['enrichment_gap'],
                                    'holdout_pathogenic_fraction_rule_on': holdout_gap['pathogenic_fraction_rule_on'],
                                    'holdout_pathogenic_fraction_rule_off': holdout_gap['pathogenic_fraction_rule_off'],
                                })

                        selected_n = int(best_rule['n_rule_on'])
                        labels = model_tp53['label'].astype(int).to_numpy()
                        chemistry_mask = compute_rule_mask(model_tp53, 'chemistry_only', float(best_rule['threshold']), None)
                        pair_mask = compute_rule_mask(model_tp53, 'pair_only', float(best_rule['threshold']), None)
                        scalar_rank = model_tp53['ll_rank_norm'].rank(method='first', ascending=False) <= selected_n
                        selected_gap = bootstrap_gap(labels, selected_mask.to_numpy(), BOOTSTRAP_REPLICATES, RANDOM_SEED + 4000 + len(control_rows))
                        chemistry_gap = bootstrap_gap(labels, chemistry_mask.to_numpy(), BOOTSTRAP_REPLICATES, RANDOM_SEED + 4100 + len(control_rows))
                        pair_gap = bootstrap_gap(labels, pair_mask.to_numpy(), BOOTSTRAP_REPLICATES, RANDOM_SEED + 4200 + len(control_rows))
                        scalar_gap = bootstrap_gap(labels, scalar_rank.to_numpy(), BOOTSTRAP_REPLICATES, RANDOM_SEED + 4300 + len(control_rows))
                        random_gap = random_coverage_matched_gap(labels, selected_n, RANDOM_REPLICATES, RANDOM_SEED + 4400 + len(control_rows))
                        control_rows.extend([
                            {
                                'model_label': model_label,
                                'family_label': spec['family_label'],
                                'architecture_kind': spec['architecture_kind'],
                                'control_name': 'selected_rule',
                                'n_rule_on': selected_n,
                                'enrichment_gap': selected_gap['enrichment_gap'],
                            },
                            {
                                'model_label': model_label,
                                'family_label': spec['family_label'],
                                'architecture_kind': spec['architecture_kind'],
                                'control_name': 'chemistry_only',
                                'n_rule_on': int(chemistry_mask.sum()),
                                'enrichment_gap': chemistry_gap['enrichment_gap'],
                            },
                            {
                                'model_label': model_label,
                                'family_label': spec['family_label'],
                                'architecture_kind': spec['architecture_kind'],
                                'control_name': 'pair_only',
                                'n_rule_on': int(pair_mask.sum()),
                                'enrichment_gap': pair_gap['enrichment_gap'],
                            },
                            {
                                'model_label': model_label,
                                'family_label': spec['family_label'],
                                'architecture_kind': spec['architecture_kind'],
                                'control_name': 'scalar_top_n_matched',
                                'n_rule_on': int(selected_n),
                                'enrichment_gap': scalar_gap['enrichment_gap'],
                            },
                            {
                                'model_label': model_label,
                                'family_label': spec['family_label'],
                                'architecture_kind': spec['architecture_kind'],
                                'control_name': 'random_coverage_matched_mean',
                                'n_rule_on': int(selected_n),
                                'enrichment_gap': random_gap['random_gap_mean'],
                            },
                        ])

                        if not bool(best_rule['coverage_floor_pass']):
                            failure_taxonomy = 'low_coverage_failure'
                            failure_reason = 'Best rule still misses the coverage floor.'
                        elif float(best_rule['enrichment_gap']) <= 0:
                            failure_taxonomy = 'family_specific_contradiction'
                            failure_reason = 'Selected rule is coverage-valid but does not enrich pathogenic TP53 variants.'
                        elif float(summary['delta_pair_vs_ll']) <= 0:
                            failure_taxonomy = 'baseline_mismatch_failure'
                            failure_reason = 'Pair score does not outrun the scalar baseline on TP53 AUC.'
                        elif structural_rows and any(row['model_label'] == model_label for row in structural_rows):
                            latest_struct = [row for row in structural_rows if row['model_label'] == model_label][-1]
                            if safe_float(latest_struct['spearman_pair_minus_ll_vs_excess_local_rmsd'], 0.0) <= safe_float(latest_struct['spearman_ll_rank_vs_excess_local_rmsd'], 0.0):
                                failure_taxonomy = 'structurally_unsupported_positive'
                                failure_reason = 'Selected rule enriches labels, but structure does not improve beyond the scalar baseline.'
                            else:
                                failure_taxonomy = 'passes_primary_checks'
                                failure_reason = 'Model passes coverage, enrichment, baseline, and structural checks.'
                        else:
                            failure_taxonomy = 'missing_structural_support_layer'
                            failure_reason = 'Model passed label checks, but structural overlap was unavailable.'

                        failure_rows.append({
                            'model_label': model_label,
                            'family_label': spec['family_label'],
                            'architecture_kind': spec['architecture_kind'],
                            'failure_taxonomy': failure_taxonomy,
                            'reason': failure_reason,
                        })

                    model_variants = pd.concat(model_variant_frames, ignore_index=True, sort=False) if model_variant_frames else pd.DataFrame()
                    model_summary = pd.DataFrame(model_summary_rows).sort_values('auc_pair_fixed_055', ascending=False).reset_index(drop=True)
                    alpha_sweep_long = pd.DataFrame(alpha_sweep_rows)
                    calibration_table = pd.DataFrame(calibration_rows)
                    selected_rules = pd.DataFrame(selected_rule_rows)
                    structural_table = pd.DataFrame(structural_rows)
                    same_position_table = pd.DataFrame(same_position_rows)
                    robustness_table = pd.DataFrame(robustness_rows)
                    holdout_transfer_table = pd.DataFrame(holdout_rows)
                    control_table = pd.DataFrame(control_rows)
                    failure_table = pd.DataFrame(failure_rows)

                    model_variants.to_csv(TABLES_DIR / 'tp53_model_variant_scores.csv', index=False)
                    model_summary.to_csv(TABLES_DIR / 'tp53_model_summary.csv', index=False)
                    alpha_sweep_long.to_csv(TABLES_DIR / 'tp53_alpha_sweep_by_model.csv', index=False)
                    calibration_table.to_csv(TABLES_DIR / 'tp53_rule_candidate_calibration.csv', index=False)
                    selected_rules.to_csv(TABLES_DIR / 'tp53_selected_rules.csv', index=False)
                    structural_table.to_csv(TABLES_DIR / 'tp53_structural_alignment_summary.csv', index=False)
                    same_position_table.to_csv(TABLES_DIR / 'tp53_same_position_ranking_summary.csv', index=False)
                    robustness_table.to_csv(TABLES_DIR / 'tp53_robustness_slice_summary.csv', index=False)
                    holdout_transfer_table.to_csv(TABLES_DIR / 'mini_holdout_transfer_summary.csv', index=False)
                    control_table.to_csv(TABLES_DIR / 'tp53_rule_vs_controls.csv', index=False)
                    failure_table.to_csv(TABLES_DIR / 'tp53_failure_taxonomy.csv', index=False)

                    display(model_summary)
                    display(selected_rules)
                    display(holdout_transfer_table)
                    done('Per-model summaries, calibration tables, controls, robustness slices, and holdout transfer tables are written.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Family-aware aggregation, figures, failure synthesis, and the final claim package
                if SKIP_LIVE or live_scores.empty:
                    print('Artifacts already written in skip-live mode.')
                else:
                    family_summary = pd.DataFrame()
                    architecture_summary = pd.DataFrame()
                    control_wins = pd.DataFrame()

                    if not selected_rules.empty:
                        merged = selected_rules.merge(
                            model_summary[['model_label', 'family_label', 'architecture_kind', 'delta_pair_vs_ll']],
                            on=['model_label', 'family_label', 'architecture_kind'],
                            how='left',
                        )
                        if not structural_table.empty:
                            merged = merged.merge(
                                structural_table[['model_label', 'spearman_pair_minus_ll_vs_excess_local_rmsd']],
                                on='model_label',
                                how='left',
                            )

                        family_rows = []
                        for family_label, group in merged.groupby('family_label'):
                            coverage_weights = group['n_rule_on'].fillna(0).astype(float).to_numpy()
                            family_rows.append({
                                'family_label': family_label,
                                'n_models': int(len(group)),
                                'n_models_passing_coverage': int(group['coverage_floor_pass'].fillna(False).sum()),
                                'weighted_enrichment_gap': weighted_mean(group['enrichment_gap'].to_numpy(), np.maximum(coverage_weights, 1.0)),
                                'weighted_delta_pair_vs_ll': weighted_mean(group['delta_pair_vs_ll'].to_numpy(), np.maximum(coverage_weights, 1.0)),
                                'weighted_structural_alignment': weighted_mean(
                                    group.get('spearman_pair_minus_ll_vs_excess_local_rmsd', pd.Series(dtype=float)).to_numpy()
                                    if 'spearman_pair_minus_ll_vs_excess_local_rmsd' in group.columns else np.array([]),
                                    np.maximum(coverage_weights, 1.0)[:len(group.get('spearman_pair_minus_ll_vs_excess_local_rmsd', pd.Series(dtype=float)).to_numpy()
                                    if 'spearman_pair_minus_ll_vs_excess_local_rmsd' in group.columns else np.array([]))],
                                ) if 'spearman_pair_minus_ll_vs_excess_local_rmsd' in group.columns else float('nan'),
                            })
                        family_summary = pd.DataFrame(family_rows).sort_values('weighted_enrichment_gap', ascending=False)

                        architecture_rows = []
                        for architecture_kind, group in merged.groupby('architecture_kind'):
                            coverage_weights = group['n_rule_on'].fillna(0).astype(float).to_numpy()
                            architecture_rows.append({
                                'architecture_kind': architecture_kind,
                                'n_models': int(len(group)),
                                'n_models_passing_coverage': int(group['coverage_floor_pass'].fillna(False).sum()),
                                'weighted_enrichment_gap': weighted_mean(group['enrichment_gap'].to_numpy(), np.maximum(coverage_weights, 1.0)),
                                'weighted_delta_pair_vs_ll': weighted_mean(group['delta_pair_vs_ll'].to_numpy(), np.maximum(coverage_weights, 1.0)),
                            })
                        architecture_summary = pd.DataFrame(architecture_rows).sort_values('weighted_enrichment_gap', ascending=False)

                    if not control_table.empty:
                        control_wins = control_table.pivot_table(
                            index=['model_label', 'family_label', 'architecture_kind'],
                            columns='control_name',
                            values='enrichment_gap',
                            aggfunc='first',
                        ).reset_index()
                        for column in ['chemistry_only', 'pair_only', 'scalar_top_n_matched', 'random_coverage_matched_mean']:
                            if column not in control_wins.columns:
                                control_wins[column] = np.nan
                        control_wins['beats_all_controls'] = (
                            control_wins['selected_rule'].fillna(-999.0) > control_wins['chemistry_only'].fillna(-999.0)
                        ) & (
                            control_wins['selected_rule'].fillna(-999.0) > control_wins['pair_only'].fillna(-999.0)
                        ) & (
                            control_wins['selected_rule'].fillna(-999.0) > control_wins['scalar_top_n_matched'].fillna(-999.0)
                        ) & (
                            control_wins['selected_rule'].fillna(-999.0) > control_wins['random_coverage_matched_mean'].fillna(-999.0)
                        )

                    family_summary.to_csv(TABLES_DIR / 'family_aggregate_summary.csv', index=False)
                    architecture_summary.to_csv(TABLES_DIR / 'architecture_aggregate_summary.csv', index=False)
                    control_wins.to_csv(TABLES_DIR / 'control_win_summary.csv', index=False)

                    scoreboard_df = selected_rules.merge(
                        model_summary[['model_label', 'family_label', 'architecture_kind', 'delta_pair_vs_ll', 'auc_pair_fixed_055']],
                        on=['model_label', 'family_label', 'architecture_kind'],
                        how='left',
                    )
                    if not structural_table.empty:
                        scoreboard_df = scoreboard_df.merge(
                            structural_table[['model_label', 'spearman_pair_minus_ll_vs_excess_local_rmsd', 'structural_geometry_gap']],
                            on='model_label',
                            how='left',
                        )
                    if not holdout_transfer_table.empty:
                        scoreboard_df = scoreboard_df.merge(
                            holdout_transfer_table[['model_label', 'holdout_enrichment_gap']],
                            on='model_label',
                            how='left',
                        )

                    scoreboard_cols = [
                        'auc_pair_fixed_055',
                        'delta_pair_vs_ll',
                        'n_rule_on',
                        'enrichment_gap',
                        'odds_ratio',
                        'spearman_pair_minus_ll_vs_excess_local_rmsd',
                        'holdout_enrichment_gap',
                    ]
                    normalized_scoreboard = scoreboard_df.copy()
                    for column in scoreboard_cols:
                        if column in normalized_scoreboard.columns:
                            values = pd.to_numeric(normalized_scoreboard[column], errors='coerce')
                            minimum = values.min(skipna=True)
                            maximum = values.max(skipna=True)
                            if pd.notna(minimum) and pd.notna(maximum) and maximum > minimum:
                                normalized_scoreboard[column] = (values - minimum) / (maximum - minimum)
                            else:
                                normalized_scoreboard[column] = values.fillna(0.0)

                    heatmap_data = normalized_scoreboard[scoreboard_cols].fillna(0.0).to_numpy() if not normalized_scoreboard.empty else np.zeros((0, len(scoreboard_cols)))
                    if len(heatmap_data):
                        fig, ax = plt.subplots(figsize=(11, max(4, 0.45 * len(normalized_scoreboard))))
                        im = ax.imshow(heatmap_data, cmap='viridis', aspect='auto')
                        ax.set_xticks(range(len(scoreboard_cols)))
                        ax.set_xticklabels(scoreboard_cols, rotation=30, ha='right')
                        ax.set_yticks(range(len(normalized_scoreboard)))
                        ax.set_yticklabels(normalized_scoreboard['model_label'])
                        ax.set_title('Multifamily model scoreboard')
                        fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
                        fig.tight_layout()
                        fig.savefig(FIGURES_DIR / 'multifamily_model_scoreboard.png', dpi=220, bbox_inches='tight')
                        plt.close(fig)

                    if not selected_rules.empty:
                        frontier_df = selected_rules.merge(
                            model_summary[['model_label', 'family_label', 'architecture_kind']],
                            on=['model_label', 'family_label', 'architecture_kind'],
                            how='left',
                        )
                        fig, ax = plt.subplots(figsize=(8, 6))
                        for family_label, group in frontier_df.groupby('family_label'):
                            ax.scatter(group['n_rule_on'], group['enrichment_gap'], s=90, alpha=0.9, label=family_label)
                            for _, row in group.iterrows():
                                ax.text(row['n_rule_on'] + 0.2, row['enrichment_gap'], row['model_label'], fontsize=8)
                        ax.axhline(0.0, color='black', linewidth=1, linestyle='--')
                        ax.set_xlabel('Coverage count (rule on)')
                        ax.set_ylabel('Pathogenic enrichment gap')
                        ax.set_title('Coverage vs enrichment frontier')
                        ax.legend(loc='best', fontsize=8)
                        fig.tight_layout()
                        fig.savefig(FIGURES_DIR / 'coverage_enrichment_frontier.png', dpi=220, bbox_inches='tight')
                        plt.close(fig)

                        esm_scale_order = ['ESM2-35M', 'ESM2-150M', 'ESM2-650M', 'ESM2-3B', 'ESM-1v']
                        esm_curve = frontier_df.loc[frontier_df['model_label'].isin(esm_scale_order)].copy()
                        esm_curve['scale_order'] = esm_curve['model_label'].map({label: idx for idx, label in enumerate(esm_scale_order)})
                        esm_curve = esm_curve.sort_values('scale_order')
                        if not esm_curve.empty:
                            fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
                            axes[0].plot(esm_curve['model_label'], esm_curve['enrichment_gap'], marker='o', color='#0f766e')
                            axes[0].set_title('ESM scale curve: enrichment')
                            axes[0].set_ylabel('Enrichment gap')
                            axes[0].tick_params(axis='x', rotation=30)
                            delta_lookup = model_summary.set_index('model_label')['delta_pair_vs_ll']
                            axes[1].plot(esm_curve['model_label'], esm_curve['model_label'].map(delta_lookup), marker='o', color='#1d4ed8')
                            axes[1].set_title('ESM scale curve: pair vs ll')
                            axes[1].set_ylabel('delta AUC(pair - ll)')
                            axes[1].tick_params(axis='x', rotation=30)
                            fig.tight_layout()
                            fig.savefig(FIGURES_DIR / 'esm_scale_curve.png', dpi=220, bbox_inches='tight')
                            plt.close(fig)

                    if not family_summary.empty:
                        fig, ax = plt.subplots(figsize=(8, 4.5))
                        ax.barh(family_summary['family_label'], family_summary['weighted_enrichment_gap'], color='#9333ea')
                        ax.set_xlabel('Weighted enrichment gap')
                        ax.set_title('Family aggregate summary')
                        fig.tight_layout()
                        fig.savefig(FIGURES_DIR / 'family_aggregate_summary.png', dpi=220, bbox_inches='tight')
                        plt.close(fig)

                    if not structural_table.empty:
                        structural_rank = structural_table.sort_values('spearman_pair_minus_ll_vs_excess_local_rmsd', ascending=True)
                        fig, ax = plt.subplots(figsize=(8, 4.5))
                        ax.barh(structural_rank['model_label'], structural_rank['spearman_pair_minus_ll_vs_excess_local_rmsd'], color='#ea580c')
                        ax.set_xlabel('Spearman(pair-minus-ll, excess local RMSD)')
                        ax.set_title('Structural alignment panel')
                        fig.tight_layout()
                        fig.savefig(FIGURES_DIR / 'structural_alignment_panel.png', dpi=220, bbox_inches='tight')
                        plt.close(fig)

                    if not control_table.empty:
                        controls_plot = control_table.loc[control_table['control_name'].isin(['selected_rule', 'chemistry_only', 'pair_only', 'scalar_top_n_matched'])].copy()
                        fig, ax = plt.subplots(figsize=(10, 5))
                        pivot = controls_plot.pivot_table(index='model_label', columns='control_name', values='enrichment_gap', aggfunc='first')
                        pivot = pivot[['selected_rule', 'chemistry_only', 'pair_only', 'scalar_top_n_matched']] if all(col in pivot.columns for col in ['selected_rule', 'chemistry_only', 'pair_only', 'scalar_top_n_matched']) else pivot
                        pivot.plot(kind='bar', ax=ax)
                        ax.set_ylabel('Enrichment gap')
                        ax.set_title('Selected rule vs controls')
                        ax.axhline(0.0, color='black', linewidth=1, linestyle='--')
                        fig.tight_layout()
                        fig.savefig(FIGURES_DIR / 'rule_vs_controls.png', dpi=220, bbox_inches='tight')
                        plt.close(fig)

                    if not failure_table.empty:
                        failure_counts = failure_table.groupby('failure_taxonomy').size().sort_values()
                        fig, ax = plt.subplots(figsize=(8, 4.5))
                        ax.barh(failure_counts.index.astype(str), failure_counts.values, color='#64748b')
                        ax.set_xlabel('Model count')
                        ax.set_title('Failure taxonomy panel')
                        fig.tight_layout()
                        fig.savefig(FIGURES_DIR / 'failure_taxonomy_panel.png', dpi=220, bbox_inches='tight')
                        plt.close(fig)

                    primary_esm_pass = int(
                        selected_rules.loc[
                            selected_rules['model_label'].isin(['ESM2-35M', 'ESM2-150M', 'ESM2-650M', 'ESM2-3B', 'ESM-1v'])
                            & selected_rules['coverage_floor_pass'].fillna(False)
                            & (pd.to_numeric(selected_rules['enrichment_gap'], errors='coerce').fillna(-999.0) > 0.0)
                        ].shape[0]
                    ) if not selected_rules.empty else 0
                    outside_esm_pass = int(
                        selected_rules.loc[
                            ~selected_rules['family_label'].astype(str).str.startswith('esm')
                            & selected_rules['coverage_floor_pass'].fillna(False)
                            & (pd.to_numeric(selected_rules['enrichment_gap'], errors='coerce').fillna(-999.0) > 0.0)
                        ].shape[0]
                    ) if not selected_rules.empty else 0
                    family_positive_count = int((pd.to_numeric(family_summary.get('weighted_enrichment_gap', pd.Series(dtype=float)), errors='coerce').fillna(-999.0) > 0.0).sum()) if not family_summary.empty else 0
                    structural_positive_count = int(
                        structural_table.loc[
                            pd.to_numeric(structural_table['spearman_pair_minus_ll_vs_excess_local_rmsd'], errors='coerce').fillna(-999.0)
                            > pd.to_numeric(structural_table['spearman_ll_rank_vs_excess_local_rmsd'], errors='coerce').fillna(-999.0)
                        ].shape[0]
                    ) if not structural_table.empty else 0
                    control_win_count = int(control_wins['beats_all_controls'].fillna(False).sum()) if not control_wins.empty else 0
                    holdout_positive_count = int(
                        holdout_transfer_table.loc[pd.to_numeric(holdout_transfer_table['holdout_enrichment_gap'], errors='coerce').fillna(-999.0) > 0.0].shape[0]
                    ) if not holdout_transfer_table.empty else 0

                    claim_status = (
                        'multifamily_generalization_supported'
                        if (
                            primary_esm_pass >= 4
                            and outside_esm_pass >= 2
                            and family_positive_count >= 3
                            and structural_positive_count >= 1
                            and control_win_count >= max(2, int(len(selected_rules) * 0.5)) if not selected_rules.empty else False
                        )
                        else 'multifamily_generalization_mixed'
                    )

                    claim_reason = (
                        'The bounded covariance rule now survives across scales, families, and architectures under an explicit coverage floor, while still aligning with structural perturbation and beating chemistry-only or scalar-only controls.'
                        if claim_status == 'multifamily_generalization_supported'
                        else 'The multifamily panel still shows real covariance signal, but portability remains uneven across families or weak once coverage floors and controls are enforced.'
                    )

                    best_model = model_summary.sort_values('auc_pair_fixed_055', ascending=False).iloc[0] if not model_summary.empty else None
                    best_structural = structural_table.sort_values('spearman_pair_minus_ll_vs_excess_local_rmsd', ascending=False).iloc[0] if not structural_table.empty else None

                    summary_payload = {
                        'notebook_slug': NOTEBOOK_SLUG,
                        'run_at_utc': RUN_AT,
                        'account_label': ACCOUNT_LABEL,
                        'claim_status': claim_status,
                        'claim_reason': claim_reason,
                        'n_models_attempted': int(len(MODEL_SPECS)),
                        'n_models_scored_on_tp53': int(model_summary.shape[0]),
                        'primary_esm_models_passing': primary_esm_pass,
                        'non_esm_models_passing': outside_esm_pass,
                        'positive_family_count': family_positive_count,
                        'structural_positive_models': structural_positive_count,
                        'control_win_count': control_win_count,
                        'holdout_positive_models': holdout_positive_count,
                        'best_model_label': str(best_model['model_label']) if best_model is not None else 'none',
                        'best_model_auc_pair_fixed_055': float(best_model['auc_pair_fixed_055']) if best_model is not None else float('nan'),
                        'best_model_delta_pair_vs_ll': float(best_model['delta_pair_vs_ll']) if best_model is not None else float('nan'),
                        'best_structural_model_label': str(best_structural['model_label']) if best_structural is not None else 'none',
                        'best_structural_alignment': float(best_structural['spearman_pair_minus_ll_vs_excess_local_rmsd']) if best_structural is not None else float('nan'),
                        'rule_selection_policy': 'coverage-aware best rule among chemistry-only, pair-only, scalar-only, combined, and combined+confidence candidates',
                        'coverage_floor_definition': f'max({MIN_RULE_ON_ABS}, ceil(n_variants * {MIN_RULE_ON_FRAC:.3f}))',
                    }

                    response_md = '\\n'.join([
                        '# Block 12B Multifamily Coverage-Aware Generalization Summary',
                        '',
                        f"- Claim status: `{summary_payload['claim_status']}`",
                        f"- Primary ESM models passing: `{summary_payload['primary_esm_models_passing']}`",
                        f"- Non-ESM models passing: `{summary_payload['non_esm_models_passing']}`",
                        f"- Positive family count: `{summary_payload['positive_family_count']}`",
                        f"- Structural-positive models: `{summary_payload['structural_positive_models']}`",
                        f"- Control wins: `{summary_payload['control_win_count']}`",
                        f"- Best model: `{summary_payload['best_model_label']}` with AUC `{summary_payload['best_model_auc_pair_fixed_055']:.3f}`",
                        f"- Best structural model: `{summary_payload['best_structural_model_label']}` with Spearman `{summary_payload['best_structural_alignment']:.3f}`",
                        '',
                        '## Interpretation',
                        '',
                        'This notebook asks a harder question than Block 12: not whether covariance looks good somewhere, but whether a bounded rule survives once coverage floors, pairwise controls, family aggregation, and structural validation are all enforced at once.',
                    ])

                    claim_paragraph = (
                        'Covariance rescue is no longer framed as a one-checkpoint curiosity. Under a coverage-aware rule, it recurs across multiple scales and extends beyond the original ESM pocket into additional model families, while the successful cases remain more aligned with orthogonal structural perturbation than chemistry-only or scalar-only explanations would predict.'
                        if claim_status == 'multifamily_generalization_supported'
                        else 'The multifamily stress test confirms that covariance still carries real signal, but the signal remains bounded: it is strongest in a subset of models and should be sold as a coverage-aware, model-sensitive rule rather than a universal cross-family law.'
                    )

                    (MANIFESTS_DIR / 'block12b_multifamily_summary.json').write_text(json.dumps(summary_payload, indent=2), encoding='utf-8')
                    (MANIFESTS_DIR / 'artifact_summary.json').write_text(json.dumps(summary_payload, indent=2), encoding='utf-8')
                    (TEXT_DIR / 'block12b_multifamily_summary.md').write_text(response_md + '\\n', encoding='utf-8')
                    (TEXT_DIR / 'block12b_claim_paragraph.md').write_text(claim_paragraph + '\\n', encoding='utf-8')

                    if ZIP_PATH.exists():
                        ZIP_PATH.unlink()
                    with zipfile.ZipFile(ZIP_PATH, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
                        for folder in [TABLES_DIR, FIGURES_DIR, TEXT_DIR, MANIFESTS_DIR, RUNTIME_DIR, LIVE_SCORES_DIR]:
                            for file_path in folder.rglob('*'):
                                if file_path.is_file():
                                    archive.write(file_path, arcname=str(file_path.relative_to(RESULTS_ROOT)))

                    print(json.dumps(summary_payload, indent=2))
                    display(family_summary)
                    display(architecture_summary)
                    display(control_wins)
                    done('Family aggregates, figures, controls, markdown, and the final zip bundle are written.')
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
    output_path = repo_root / "New Notebooks" / "12b_block12_multifamily_coverage_aware_generalization_h100.ipynb"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(notebook, indent=2), encoding="utf-8")
    print(f"Wrote notebook to {output_path}")


if __name__ == "__main__":
    main()
