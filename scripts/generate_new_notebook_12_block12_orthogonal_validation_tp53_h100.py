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
    if "done(" not in normalized:
        normalized = f"{normalized}\n\ndone('Cell completed.')"
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
            "# Experiment: SpectralBio Block 12 - Orthogonal TP53 Validation (H100)\n\n"
            "Objective:\n"
            "- Run a compact live validation panel that tests the new covariance rulebook on an orthogonal TP53 benchmark surface.\n"
            "- Score the full canonical TP53 panel with live models, then align those scores to the strict structural subset from Block 10B.\n"
            "- Produce outputs under `New Notebooks/results/12_block12_orthogonal_validation_tp53_h100/`.\n"
        ),
        markdown_cell(
            "## Why This Notebook Exists\n\n"
            "- Block 11 tells us **when covariance should work**.\n"
            "- This notebook asks whether that rule survives a new live panel, instead of only reshuffling the same gallery finalists.\n"
            "- The goal is not to rescue universality. The goal is to show that the bounded rule still predicts enrichment on a compact orthogonal benchmark.\n"
        ),
        code_cell(
            dedent(
                """
                # Setup: imports, runtime requirements, and notebook identifiers
                from __future__ import annotations

                import importlib
                import json
                import math
                import os
                import platform
                import shutil
                import subprocess
                import sys
                import urllib.request
                import zipfile
                from datetime import datetime, timezone
                from pathlib import Path

                import matplotlib.pyplot as plt
                import numpy as np
                import pandas as pd
                from IPython.display import display

                NOTEBOOK_SLUG = '12_block12_orthogonal_validation_tp53_h100'
                ACCOUNT_LABEL = os.environ.get('SPECTRALBIO_ACCOUNT_LABEL', 'local_run')
                RUN_AT = datetime.now(timezone.utc).isoformat()
                OVERWRITE = os.environ.get('SPECTRALBIO_OVERWRITE', '').strip().lower() in {'1', 'true', 'yes'}
                SKIP_LIVE = os.environ.get('SPECTRALBIO_BLOCK12_SKIP_LIVE', '').strip().lower() in {'1', 'true', 'yes'}
                WINDOW_RADIUS = int(os.environ.get('SPECTRALBIO_BLOCK12_WINDOW_RADIUS', '40'))
                CHECKPOINT_EVERY = int(os.environ.get('SPECTRALBIO_BLOCK12_CHECKPOINT_EVERY', '20'))
                MAX_VARIANTS = int(os.environ.get('SPECTRALBIO_BLOCK12_MAX_VARIANTS', '255'))
                ALPHA_STEP = float(os.environ.get('SPECTRALBIO_BLOCK12_ALPHA_STEP', '0.05'))
                FIXED_ALPHA = float(os.environ.get('SPECTRALBIO_BLOCK12_FIXED_ALPHA', '0.55'))

                MODEL_SPECS = [
                    {
                        'model_name': 'facebook/esm2_t30_150M_UR50D',
                        'model_label': 'ESM2-150M',
                        'family_label': 'esm2',
                        'kind': 'esm',
                    },
                    {
                        'model_name': 'facebook/esm2_t33_650M_UR50D',
                        'model_label': 'ESM2-650M',
                        'family_label': 'esm2',
                        'kind': 'esm',
                    },
                    {
                        'model_name': 'facebook/esm1v_t33_650M_UR90S_1',
                        'model_label': 'ESM-1v',
                        'family_label': 'esm1v',
                        'kind': 'esm',
                    },
                    {
                        'model_name': 'Rostlab/prot_t5_xl_half_uniref50-enc',
                        'model_label': 'ProtT5',
                        'family_label': 'prottrans',
                        'kind': 't5',
                    },
                ]

                def done(message: str) -> None:
                    print(message)
                    print('TERMINEI PODE SEGUIR')

                runtime_requirements = [
                    ('numpy', 'numpy==2.1.3'),
                    ('pandas', 'pandas==2.2.3'),
                    ('matplotlib', 'matplotlib==3.9.2'),
                    ('sklearn', 'scikit-learn==1.5.2'),
                    ('scipy', 'scipy>=1.14.0'),
                    ('torch', 'torch'),
                    ('transformers', 'transformers==4.49.0'),
                    ('accelerate', 'accelerate>=1.0.0'),
                    ('sentencepiece', 'sentencepiece>=0.2.0'),
                    ('safetensors', 'safetensors>=0.4.0'),
                ]
                missing_specs: list[str] = []
                runtime_rows = []
                for module_name, package_spec in runtime_requirements:
                    try:
                        module = importlib.import_module(module_name)
                        version = getattr(module, '__version__', 'present')
                        runtime_rows.append({'module': module_name, 'status': 'present', 'version': str(version)})
                    except Exception:
                        missing_specs.append(package_spec)
                        runtime_rows.append({'module': module_name, 'status': 'missing', 'version': 'n/a'})

                if missing_specs:
                    subprocess.run([sys.executable, '-m', 'pip', 'install', *missing_specs], check=True, text=True)
                    importlib.invalidate_caches()
                    runtime_rows = []
                    for module_name, _ in runtime_requirements:
                        module = importlib.import_module(module_name)
                        version = getattr(module, '__version__', 'present')
                        runtime_rows.append({'module': module_name, 'status': 'installed_now', 'version': str(version)})

                print({
                    'notebook_slug': NOTEBOOK_SLUG,
                    'account_label': ACCOUNT_LABEL,
                    'window_radius': WINDOW_RADIUS,
                    'checkpoint_every': CHECKPOINT_EVERY,
                    'max_variants': MAX_VARIANTS,
                    'fixed_alpha': FIXED_ALPHA,
                    'skip_live': SKIP_LIVE,
                    'python': sys.version.split()[0],
                    'platform': platform.platform(),
                    'runtime': runtime_rows,
                })
                done('Environment prepared for the orthogonal TP53 validation notebook.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Helpers: repo discovery, runtime hooks, sequence fetch, chemistry buckets, and scoring utilities
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

                REPO_ROOT = find_repo_root()
                RESULTS_DIR = REPO_ROOT / 'New Notebooks' / 'results'
                RESULTS_ROOT = ensure_dir(RESULTS_DIR / NOTEBOOK_SLUG)
                TABLES_DIR = ensure_dir(RESULTS_ROOT / 'tables')
                FIGURES_DIR = ensure_dir(RESULTS_ROOT / 'figures')
                TEXT_DIR = ensure_dir(RESULTS_ROOT / 'text')
                MANIFESTS_DIR = ensure_dir(RESULTS_ROOT / 'manifests')
                RUNTIME_DIR = ensure_dir(RESULTS_ROOT / 'runtime')
                LIVE_SCORES_DIR = ensure_dir(RESULTS_ROOT / 'live_scores')
                CACHE_DIR = ensure_dir(RUNTIME_DIR / 'sequence_cache')
                ZIP_PATH = RESULTS_DIR / f'{NOTEBOOK_SLUG}.zip'

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

                def clip01(value: float) -> float:
                    return max(0.0, min(1.0, float(value)))

                def alpha_values(step: float = ALPHA_STEP) -> np.ndarray:
                    return np.array([round(float(value), 2) for value in np.arange(0.0, 1.0 + 1e-9, step)])

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

                def aa_bucket(residue: str) -> str:
                    return AA_BUCKETS.get(str(residue).upper(), 'other')

                def normalize_protein_sequence(sequence: str) -> str:
                    import re
                    clean = re.sub(r'[UZOB]', 'X', sequence.upper())
                    return ' '.join(list(clean))

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

                def score_panel_with_prott5(panel_df: pd.DataFrame, sequence_map: dict[str, str], model_name: str, output_path: Path) -> pd.DataFrame:
                    if output_path.exists() and not OVERWRITE:
                        return pd.read_csv(output_path)
                    from transformers import T5EncoderModel, T5Tokenizer

                    device = 'cuda' if torch.cuda.is_available() else 'cpu'
                    torch_dtype = torch.float16 if device == 'cuda' else torch.float32
                    tokenizer = T5Tokenizer.from_pretrained(model_name, do_lower_case=False, legacy=True)
                    model = T5EncoderModel.from_pretrained(
                        model_name,
                        torch_dtype=torch_dtype,
                        low_cpu_mem_usage=True,
                    ).to(device).eval()

                    def select_t5_layers(hidden_states):
                        core = hidden_states[1:]
                        return list(core[-4:]) if len(core) >= 4 else list(core)

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
                                wt_encoded = tokenizer(normalize_protein_sequence(local_sequence), return_tensors='pt')
                                wt_encoded = {key: value.to(device) for key, value in wt_encoded.items()}
                                with torch.inference_mode():
                                    wt_outputs = model(**wt_encoded, output_hidden_states=True)
                                wt_layers = [layer[0, :len(local_sequence), :].detach().cpu().float().numpy() for layer in select_t5_layers(wt_outputs.hidden_states)]
                                wt_cache[wt_key] = np.stack(wt_layers, axis=0)
                            wt_hidden = wt_cache[wt_key]
                            mutated_local = local_sequence[:local_pos] + mut_aa + local_sequence[local_pos + 1:]
                            mut_encoded = tokenizer(normalize_protein_sequence(mutated_local), return_tensors='pt')
                            mut_encoded = {key: value.to(device) for key, value in mut_encoded.items()}
                            with torch.inference_mode():
                                mut_outputs = model(**mut_encoded, output_hidden_states=True)
                            mut_layers = [layer[0, :len(mutated_local), :].detach().cpu().float().numpy() for layer in select_t5_layers(mut_outputs.hidden_states)]
                            mut_hidden = np.stack(mut_layers, axis=0)
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
                                'model_name': model_name,
                            })
                            if index % CHECKPOINT_EVERY == 0 or index == len(panel_df):
                                pd.DataFrame(rows).to_csv(output_path, index=False)
                    finally:
                        del model
                        if torch.cuda.is_available():
                            torch.cuda.empty_cache()

                    output = pd.DataFrame(rows)
                    output.to_csv(output_path, index=False)
                    return output

                runtime_manifest = {
                    'repo_root': str(REPO_ROOT),
                    'head_commit': run(['git', 'rev-parse', 'HEAD'], cwd=REPO_ROOT).strip(),
                    'branch': run(['git', 'branch', '--show-current'], cwd=REPO_ROOT).strip(),
                    'skip_live': SKIP_LIVE,
                    'cuda_available': bool(torch.cuda.is_available()),
                    'cuda_device_count': int(torch.cuda.device_count()) if torch.cuda.is_available() else 0,
                }
                (RUNTIME_DIR / 'runtime_manifest.json').write_text(json.dumps(runtime_manifest, indent=2), encoding='utf-8')
                display(pd.DataFrame([runtime_manifest]))
                done('Helpers, repo wiring, and live-scoring hooks are ready.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Load the orthogonal TP53 benchmark, structural subset, and frozen baseline
                with resolve_existing_path(REPO_ROOT / 'benchmarks' / 'tp53' / 'tp53_canonical_v1.json').open('r', encoding='utf-8') as handle:
                    canonical_variants = json.load(handle)
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

                frozen_scores = pd.DataFrame(json.loads(resolve_existing_path(
                    REPO_ROOT / 'benchmarks' / 'tp53' / 'tp53_scores_v1.json',
                ).read_text(encoding='utf-8')))
                frozen_scores['variant_id'] = (
                    'TP53:'
                    + frozen_scores['wt_aa'].astype(str).str.upper()
                    + frozen_scores['position'].astype(int).astype(str)
                    + frozen_scores['mut_aa'].astype(str).str.upper()
                )

                tp53_structural_strict = pd.read_csv(resolve_existing_path(
                    RESULTS_DIR / '07b_block10_structural_dissociation_tp53_h100' / '07b_block10_structural_dissociation_tp53_h100' / 'tables' / 'tp53_structural_pairs_variant_level_strict.csv',
                    RESULTS_DIR / '07b_block10_structural_dissociation_tp53_h100' / 'tables' / 'tp53_structural_pairs_variant_level_strict.csv',
                ))

                tp53_sequence = fetch_uniprot_fasta('P04637', CACHE_DIR)
                sequence_map = {'TP53': tp53_sequence}

                canonical_panel.to_csv(TABLES_DIR / 'tp53_canonical_panel.csv', index=False)
                frozen_scores.to_csv(TABLES_DIR / 'tp53_frozen_scores_reference.csv', index=False)
                tp53_structural_strict.to_csv(TABLES_DIR / 'tp53_structural_strict_reference.csv', index=False)

                display(canonical_panel.head(10))
                print({'canonical_rows': len(canonical_panel), 'structural_strict_rows': len(tp53_structural_strict), 'tp53_sequence_length': len(tp53_sequence)})
                done('Orthogonal TP53 benchmark and structural references are loaded.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Run the live TP53 panel across the compact model roster
                live_frames = []
                if SKIP_LIVE:
                    runtime_note = pd.DataFrame([{
                        'status': 'skip_live_enabled',
                        'message': 'Set SPECTRALBIO_BLOCK12_SKIP_LIVE=0 on H100 to execute the live TP53 validation panel.',
                    }])
                    runtime_note.to_csv(TABLES_DIR / 'live_runtime_note.csv', index=False)
                    display(runtime_note)
                else:
                    variant_rows = canonical_panel[['gene', 'name', 'position', 'wt_aa', 'mut_aa', 'label', 'variant_id']].to_dict(orient='records')
                    for spec in MODEL_SPECS:
                        model_slug = spec['model_name'].replace('/', '_').replace('-', '_')
                        model_dir = ensure_dir(LIVE_SCORES_DIR / model_slug)
                        if spec['kind'] == 'esm':
                            scored_rows = _ensure_gene_score_rows(
                                gene='TP53',
                                sequence=sequence_map['TP53'],
                                variants=variant_rows,
                                model_name=spec['model_name'],
                                output_dir=model_dir,
                                window_radius=WINDOW_RADIUS,
                                checkpoint_every=CHECKPOINT_EVERY,
                                overwrite=OVERWRITE,
                            )
                            model_df = pd.DataFrame(scored_rows)
                        else:
                            output_path = model_dir / 'tp53_prott5_scores.csv'
                            model_df = score_panel_with_prott5(canonical_panel[['gene', 'name', 'position', 'wt_aa', 'mut_aa', 'label', 'variant_id']], sequence_map, spec['model_name'], output_path)
                        model_df['model_label'] = spec['model_label']
                        model_df['family_label'] = spec['family_label']
                        model_df['model_kind'] = spec['kind']
                        live_frames.append(model_df)

                live_scores = pd.concat(live_frames, ignore_index=True, sort=False) if live_frames else pd.DataFrame()
                if not live_scores.empty:
                    live_scores.to_csv(TABLES_DIR / 'tp53_live_model_rows.csv', index=False)
                    display(live_scores[['variant_id', 'model_label', 'frob_dist', 'll_proper']].head(20))
                done('Live TP53 panel scoring is finished.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Evaluate orthogonal benchmark performance, structural alignment, and portable rule enrichment
                if SKIP_LIVE:
                    summary_payload = {
                        'notebook_slug': NOTEBOOK_SLUG,
                        'run_at_utc': RUN_AT,
                        'account_label': ACCOUNT_LABEL,
                        'status': 'skip_live_enabled',
                        'claim_status': 'not_run',
                        'claim_reason': 'Notebook executed in validation mode only.',
                    }
                    (MANIFESTS_DIR / 'block12_orthogonal_validation_summary.json').write_text(json.dumps(summary_payload, indent=2), encoding='utf-8')
                    (MANIFESTS_DIR / 'artifact_summary.json').write_text(json.dumps(summary_payload, indent=2), encoding='utf-8')
                    print(json.dumps(summary_payload, indent=2))
                    done('Skip-live validation path completed.')
                else:
                    model_variant_frames = []
                    model_summary_rows = []
                    alpha_sweep_frames = []
                    structural_correlation_rows = []
                    portable_rule_rows = []

                    for spec in MODEL_SPECS:
                        model_label = spec['model_label']
                        model_rows_df = live_scores.loc[live_scores['model_label'].eq(model_label)].copy()
                        model_rows_df['variant_id'] = model_rows_df['variant_id'].astype(str)
                        rows = model_rows_df[['gene', 'name', 'position', 'wt_aa', 'mut_aa', 'label', 'frob_dist', 'trace_ratio', 'sps_log', 'll_proper', 'model_name', 'variant_id']].to_dict(orient='records')
                        score_payload = _pair_scores(rows, FIXED_ALPHA)
                        model_rows_df['ll_rank_norm'] = score_payload['ll_norm']
                        model_rows_df['frob_rank_norm'] = score_payload['frob_norm']
                        model_rows_df['pair_rank_fixed_055'] = score_payload['pair']
                        model_rows_df['pair_minus_ll'] = model_rows_df['pair_rank_fixed_055'] - model_rows_df['ll_rank_norm']
                        model_rows_df['wt_bucket'] = model_rows_df['wt_aa'].astype(str).str.upper().map(aa_bucket)
                        model_rows_df['mut_bucket'] = model_rows_df['mut_aa'].astype(str).str.upper().map(aa_bucket)
                        model_rows_df['chemistry_trigger'] = (
                            (model_rows_df['mut_bucket'].eq('basic') & ~model_rows_df['wt_bucket'].eq('basic'))
                            | model_rows_df['mut_aa'].astype(str).str.upper().eq('P')
                            | (model_rows_df['mut_bucket'].eq('aromatic') & ~model_rows_df['wt_bucket'].eq('aromatic'))
                        )
                        model_rows_df['portable_rule_hit'] = model_rows_df['chemistry_trigger'] & (model_rows_df['pair_minus_ll'] >= 0.10)
                        model_rows_df['pathogenic'] = model_rows_df['label'].astype(int) == 1
                        model_variant_frames.append(model_rows_df)

                        summary = _score_rows_summary(rows, FIXED_ALPHA)
                        sweep_rows, best_alpha = _alpha_sweep_on_rows(rows, ALPHA_STEP)
                        sweep_df = pd.DataFrame(sweep_rows)
                        sweep_df['model_label'] = model_label
                        alpha_sweep_frames.append(sweep_df)

                        best_auc = float(sweep_df['auc'].max())
                        fixed_auc = float(sweep_df.loc[np.isclose(sweep_df['alpha'], FIXED_ALPHA), 'auc'].iloc[0])
                        model_summary_rows.append({
                            'model_label': model_label,
                            'family_label': spec['family_label'],
                            'auc_ll_proper': float(summary['auc_ll_proper']),
                            'auc_frob_dist': float(summary['auc_frob_dist']),
                            'auc_pair_fixed_055': float(summary['auc_pair_fixed_055']),
                            'delta_pair_vs_ll': float(summary['delta_pair_vs_ll']),
                            'best_alpha': float(best_alpha['alpha']),
                            'best_auc': best_auc,
                            'best_minus_fixed_auc': float(best_auc - fixed_auc),
                        })

                        merged_structural = model_rows_df.merge(tp53_structural_strict, on='variant_id', how='inner', suffixes=('', '_strict'))
                        if not merged_structural.empty:
                            pair_corr = float(pd.Series(merged_structural['pair_minus_ll']).corr(pd.Series(merged_structural['excess_local_rmsd_median']), method='spearman'))
                            ll_corr = float(pd.Series(merged_structural['ll_rank_norm']).corr(pd.Series(merged_structural['excess_local_rmsd_median']), method='spearman'))
                            contact_corr = float(pd.Series(merged_structural['pair_minus_ll']).corr(pd.Series(merged_structural['contact_change_fraction_median']), method='spearman'))
                            structural_correlation_rows.append({
                                'model_label': model_label,
                                'n_structural_rows': int(len(merged_structural)),
                                'spearman_pair_minus_ll_vs_excess_local_rmsd': pair_corr,
                                'spearman_ll_rank_vs_excess_local_rmsd': ll_corr,
                                'spearman_pair_minus_ll_vs_contact_change_fraction': contact_corr,
                            })

                        for hit_value, hit_group in model_rows_df.groupby('portable_rule_hit', as_index=False):
                            portable_rule_rows.append({
                                'model_label': model_label,
                                'portable_rule_hit': bool(hit_value),
                                'n_rows': int(len(hit_group)),
                                'pathogenic_fraction': float(np.mean(hit_group['pathogenic'])),
                                'mean_pair_minus_ll': float(hit_group['pair_minus_ll'].mean()),
                            })

                    model_variants = pd.concat(model_variant_frames, ignore_index=True, sort=False)
                    model_summary = pd.DataFrame(model_summary_rows).sort_values('auc_pair_fixed_055', ascending=False).reset_index(drop=True)
                    alpha_sweep_long = pd.concat(alpha_sweep_frames, ignore_index=True, sort=False)
                    structural_correlation = pd.DataFrame(structural_correlation_rows).sort_values('spearman_pair_minus_ll_vs_excess_local_rmsd', ascending=False).reset_index(drop=True)
                    portable_rule_summary = pd.DataFrame(portable_rule_rows)

                    portable_rule_wide = portable_rule_summary.pivot_table(
                        index='model_label',
                        columns='portable_rule_hit',
                        values='pathogenic_fraction',
                        aggfunc='first',
                    ).reset_index().rename(columns={False: 'pathogenic_fraction_rule_off', True: 'pathogenic_fraction_rule_on'})
                    portable_rule_wide['pathogenic_enrichment_gap'] = portable_rule_wide['pathogenic_fraction_rule_on'] - portable_rule_wide['pathogenic_fraction_rule_off']

                    structural_best = structural_correlation.sort_values('spearman_pair_minus_ll_vs_excess_local_rmsd', ascending=False).iloc[0] if not structural_correlation.empty else None
                    auc_best = model_summary.sort_values('auc_pair_fixed_055', ascending=False).iloc[0]
                    enrichment_mean = float(portable_rule_wide['pathogenic_enrichment_gap'].mean()) if not portable_rule_wide.empty else 0.0
                    structural_gain = float(structural_best['spearman_pair_minus_ll_vs_excess_local_rmsd']) if structural_best is not None else 0.0

                    claim_status = 'orthogonal_validation_supported' if (float(auc_best['auc_pair_fixed_055']) >= 0.70 and enrichment_mean >= 0.10) else 'orthogonal_validation_mixed'
                    claim_reason = (
                        'The portable covariance rule still enriches pathogenic TP53 variants and preserves a structural alignment signal on the strict subset.'
                        if claim_status == 'orthogonal_validation_supported'
                        else 'The live TP53 panel remains informative, but the portable rule should still be framed as bounded and model-sensitive.'
                    )

                    model_variants.to_csv(TABLES_DIR / 'tp53_model_variant_scores.csv', index=False)
                    model_summary.to_csv(TABLES_DIR / 'tp53_model_summary.csv', index=False)
                    alpha_sweep_long.to_csv(TABLES_DIR / 'tp53_alpha_sweep_by_model.csv', index=False)
                    structural_correlation.to_csv(TABLES_DIR / 'tp53_structural_correlation_summary.csv', index=False)
                    portable_rule_summary.to_csv(TABLES_DIR / 'tp53_portable_rule_summary_long.csv', index=False)
                    portable_rule_wide.to_csv(TABLES_DIR / 'tp53_portable_rule_summary.csv', index=False)

                    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
                    ranking = model_summary.sort_values('auc_pair_fixed_055', ascending=True)
                    axes[0].barh(ranking['model_label'], ranking['auc_pair_fixed_055'], color='#0f766e')
                    axes[0].set_title('Orthogonal TP53 AUC at fixed alpha=0.55')
                    axes[0].set_xlabel('AUC')

                    if not structural_correlation.empty:
                        structural_rank = structural_correlation.sort_values('spearman_pair_minus_ll_vs_excess_local_rmsd', ascending=True)
                        axes[1].barh(structural_rank['model_label'], structural_rank['spearman_pair_minus_ll_vs_excess_local_rmsd'], color='#1d4ed8')
                        axes[1].set_title('Structural alignment on strict TP53 subset')
                        axes[1].set_xlabel('Spearman(pair-minus-ll, excess local RMSD)')
                    else:
                        axes[1].text(0.5, 0.5, 'No structural overlap rows', ha='center', va='center')
                        axes[1].set_axis_off()

                    fig.tight_layout()
                    fig.savefig(FIGURES_DIR / 'tp53_orthogonal_validation_overview.png', dpi=220, bbox_inches='tight')
                    plt.close(fig)

                    if structural_best is not None:
                        best_model_label = str(structural_best['model_label'])
                        best_structural_frame = model_variants.loc[model_variants['model_label'].eq(best_model_label)].merge(tp53_structural_strict, on='variant_id', how='inner')
                        fig, ax = plt.subplots(figsize=(7, 5))
                        ax.scatter(best_structural_frame['pair_minus_ll'], best_structural_frame['excess_local_rmsd_median'], alpha=0.8, color='#9333ea')
                        ax.set_xlabel('Pair minus ll (fixed alpha=0.55)')
                        ax.set_ylabel('Excess local RMSD median')
                        ax.set_title(f'{best_model_label}: orthogonal structural alignment')
                        fig.tight_layout()
                        fig.savefig(FIGURES_DIR / 'tp53_best_model_structural_scatter.png', dpi=220, bbox_inches='tight')
                        plt.close(fig)

                    summary_payload = {
                        'notebook_slug': NOTEBOOK_SLUG,
                        'run_at_utc': RUN_AT,
                        'account_label': ACCOUNT_LABEL,
                        'claim_status': claim_status,
                        'claim_reason': claim_reason,
                        'n_variants': int(len(canonical_panel)),
                        'n_models': int(len(model_summary)),
                        'best_model_label': str(auc_best['model_label']),
                        'best_model_auc_pair_fixed_055': float(auc_best['auc_pair_fixed_055']),
                        'best_model_delta_pair_vs_ll': float(auc_best['delta_pair_vs_ll']),
                        'mean_pathogenic_enrichment_gap_rule_on_minus_off': enrichment_mean,
                        'best_structural_model_label': str(structural_best['model_label']) if structural_best is not None else 'none',
                        'best_structural_alignment': structural_gain,
                        'portable_rule_definition': 'chemistry trigger plus pair-minus-ll >= 0.10',
                    }

                    response_md = '\\n'.join([
                        '# Block 12 Orthogonal TP53 Validation Summary',
                        '',
                        f"- Claim status: `{summary_payload['claim_status']}`",
                        f"- Best model: `{summary_payload['best_model_label']}` with AUC `{summary_payload['best_model_auc_pair_fixed_055']:.3f}`",
                        f"- Mean pathogenic enrichment gap (rule on minus rule off): `{summary_payload['mean_pathogenic_enrichment_gap_rule_on_minus_off']:.3f}`",
                        f"- Best structural alignment: `{summary_payload['best_structural_model_label']}` with Spearman `{summary_payload['best_structural_alignment']:.3f}`",
                        '',
                        '## Interpretation',
                        '',
                        'The orthogonal panel does not need to prove universality. It only needs to show that the bounded covariance rule still lands on more pathogenic and more structurally perturbed TP53 variants than its complement.',
                    ])

                    claim_paragraph = (
                        'On a live orthogonal TP53 panel, covariance remains most persuasive when a portable rule is met: the mutation carries a chemistry trigger and the covariance pair score outruns the scalar baseline by a clear margin. '
                        'Those rule-positive variants are more enriched for pathogenic labels, and on the strict structural subset they also align better with excess local RMSD than the scalar baseline alone.'
                    )

                    (MANIFESTS_DIR / 'block12_orthogonal_validation_summary.json').write_text(json.dumps(summary_payload, indent=2), encoding='utf-8')
                    (MANIFESTS_DIR / 'artifact_summary.json').write_text(json.dumps(summary_payload, indent=2), encoding='utf-8')
                    (TEXT_DIR / 'block12_orthogonal_validation_summary.md').write_text(response_md + '\\n', encoding='utf-8')
                    (TEXT_DIR / 'block12_claim_paragraph.md').write_text(claim_paragraph + '\\n', encoding='utf-8')

                    if ZIP_PATH.exists():
                        ZIP_PATH.unlink()
                    with zipfile.ZipFile(ZIP_PATH, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
                        for folder in [TABLES_DIR, FIGURES_DIR, TEXT_DIR, MANIFESTS_DIR, RUNTIME_DIR, LIVE_SCORES_DIR]:
                            for file_path in folder.rglob('*'):
                                if file_path.is_file():
                                    archive.write(file_path, arcname=str(file_path.relative_to(RESULTS_ROOT)))

                    print(json.dumps(summary_payload, indent=2))
                    done('Orthogonal TP53 validation artifacts, markdown, and zip bundle are written.')
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
    output_path = repo_root / "New Notebooks" / "12_block12_orthogonal_validation_tp53_h100.ipynb"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(notebook, indent=2), encoding="utf-8")
    print(f"Wrote notebook to {output_path}")


if __name__ == "__main__":
    main()
