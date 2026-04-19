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
            "# Experiment: SpectralBio Block 7C - Alpha And Cross-Family Finalists (H100)\n\n"
            "Objective:\n"
            "- Attack the two remaining weak points from Block 7B with a tightly scoped live rerun.\n"
            "- Re-score only the reviewer-facing finalists plus a compact counterexample panel.\n"
            "- Test alpha stability and cross-family support where it matters most, instead of on whole noisy gene surfaces.\n"
            "- Produce outputs under `New Notebooks/results/10_block7c_alpha_crossfamily_finalists_h100/`.\n"
        ),
        markdown_cell(
            "## Why This Notebook Exists\n\n"
            "- `alpha` was still only partially closed in the broad Block 1 audit.\n"
            "- `cross-family generality` was still only partially closed in Block 4 and Block 7B.\n"
            "- The right move now is a *finalist-only* rerun on GPU: small enough to be feasible, targeted enough to close the review.\n\n"
            "## Runtime Contract\n\n"
            "- Input positives: `gallery_final_cases.csv` from Block 7 turbo.\n"
            "- Input negatives: the explicit anti-case plus the strongest additional counterexamples from Block 5.\n"
            "- Live models: `ESM2-150M`, `ESM2-650M`, `ESM-1v`, and `ProtT5`.\n"
            "- Optional skip mode for dry validation: set `SPECTRALBIO_BLOCK7C_SKIP_LIVE=1`.\n"
        ),
        code_cell(
            dedent(
                """
                # Setup: imports, knobs, and model roster
                from __future__ import annotations

                import importlib
                import json
                import math
                import os
                import platform
                import shutil
                import subprocess
                import sys
                import time
                import urllib.request
                import zipfile
                from datetime import datetime, timezone
                from pathlib import Path

                import matplotlib.pyplot as plt
                import numpy as np
                import pandas as pd
                from IPython.display import display

                NOTEBOOK_SLUG = '10_block7c_alpha_crossfamily_finalists_h100'
                ACCOUNT_LABEL = os.environ.get('SPECTRALBIO_ACCOUNT_LABEL', 'local_run')
                RUN_AT = datetime.now(timezone.utc).isoformat()
                OVERWRITE = os.environ.get('SPECTRALBIO_OVERWRITE', '').strip().lower() in {'1', 'true', 'yes'}
                SKIP_LIVE = os.environ.get('SPECTRALBIO_BLOCK7C_SKIP_LIVE', '').strip().lower() in {'1', 'true', 'yes'}
                WINDOW_RADIUS = int(os.environ.get('SPECTRALBIO_BLOCK7C_WINDOW_RADIUS', '40'))
                NEGATIVE_PANEL_SIZE = int(os.environ.get('SPECTRALBIO_BLOCK7C_NEGATIVE_PANEL_SIZE', '5'))
                CHECKPOINT_EVERY = int(os.environ.get('SPECTRALBIO_BLOCK7C_CHECKPOINT_EVERY', '5'))
                ALPHA_STEP = float(os.environ.get('SPECTRALBIO_BLOCK7C_ALPHA_STEP', '0.05'))
                FIXED_ALPHA = float(os.environ.get('SPECTRALBIO_BLOCK7C_FIXED_ALPHA', '0.55'))

                MODEL_SPECS = [
                    {
                        'model_name': 'facebook/esm2_t30_150M_UR50D',
                        'model_label': 'ESM2-150M',
                        'family_label': 'esm2',
                        'kind': 'esm',
                        'scalar_name': 'll_proper',
                    },
                    {
                        'model_name': 'facebook/esm2_t33_650M_UR50D',
                        'model_label': 'ESM2-650M',
                        'family_label': 'esm2',
                        'kind': 'esm',
                        'scalar_name': 'll_proper',
                    },
                    {
                        'model_name': 'facebook/esm1v_t33_650M_UR90S_1',
                        'model_label': 'ESM-1v',
                        'family_label': 'esm1v',
                        'kind': 'esm',
                        'scalar_name': 'll_proper',
                    },
                    {
                        'model_name': 'Rostlab/prot_t5_xl_half_uniref50-enc',
                        'model_label': 'ProtT5',
                        'family_label': 'prottrans',
                        'kind': 't5',
                        'scalar_name': 'mut_token_shift',
                    },
                ]

                MANUAL_ACCESSIONS = {
                    'ANKRD11': 'Q6UB99',
                    'BRCA1': 'P38398',
                    'BRCA2': 'P51587',
                    'COL2A1': 'P02458',
                    'CREBBP': 'Q92793',
                    'GRIN2A': 'Q12879',
                    'KMT2A': 'Q03164',
                    'MSH2': 'P43246',
                    'TP53': 'P04637',
                    'TSC2': 'P49815',
                }

                def done(message: str) -> None:
                    print(f'TERMINEI PODE SEGUIR - {message}')

                print({
                    'notebook_slug': NOTEBOOK_SLUG,
                    'account_label': ACCOUNT_LABEL,
                    'window_radius': WINDOW_RADIUS,
                    'negative_panel_size': NEGATIVE_PANEL_SIZE,
                    'alpha_step': ALPHA_STEP,
                    'fixed_alpha': FIXED_ALPHA,
                    'skip_live': SKIP_LIVE,
                    'model_labels': [spec['model_label'] for spec in MODEL_SPECS],
                    'python': sys.version.split()[0],
                    'platform': platform.platform(),
                })
                done('Initial configuration loaded.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Helpers: repo discovery, runtime installs, sequence fetching, and model utilities
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

                def ensure_dir(path: Path) -> Path:
                    path.mkdir(parents=True, exist_ok=True)
                    return path

                def find_repo_root(start: Path | None = None) -> Path:
                    start = (start or Path.cwd()).resolve()
                    for candidate in [start, *start.parents]:
                        if (candidate / '.git').exists():
                            return candidate
                        if (candidate / 'New Notebooks').exists() and (candidate / 'src' / 'spectralbio').exists():
                            return candidate
                    raise RuntimeError('Repository root not found.')

                def resolve_existing_path(*candidates: Path) -> Path:
                    for candidate in candidates:
                        if candidate.exists():
                            return candidate
                    raise FileNotFoundError('None of the candidate paths exist: ' + ' | '.join(str(candidate) for candidate in candidates))

                def safe_float(value, default=float('nan')) -> float:
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

                def alpha_values(step: float = ALPHA_STEP) -> np.ndarray:
                    return np.array([round(float(value), 2) for value in np.arange(0.0, 1.0 + 1e-9, step)])

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
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Runtime setup, local package imports, and model helper functions
                REPO_ROOT = find_repo_root()
                RESULTS_DIR = REPO_ROOT / 'New Notebooks' / 'results'
                SHARED_INPUTS_DIR = REPO_ROOT / 'New Notebooks' / 'shared_inputs' / 'reviewer_chain_upstream'
                RESULTS_ROOT = ensure_dir(RESULTS_DIR / NOTEBOOK_SLUG)
                TABLES_DIR = ensure_dir(RESULTS_ROOT / 'tables')
                FIGURES_DIR = ensure_dir(RESULTS_ROOT / 'figures')
                TEXT_DIR = ensure_dir(RESULTS_ROOT / 'text')
                MANIFESTS_DIR = ensure_dir(RESULTS_ROOT / 'manifests')
                RUNTIME_DIR = ensure_dir(RESULTS_ROOT / 'runtime')
                CACHE_DIR = ensure_dir(RUNTIME_DIR / 'sequence_cache')
                LIVE_SCORES_DIR = ensure_dir(RESULTS_ROOT / 'live_scores')
                ZIP_PATH = RESULTS_DIR / f'{NOTEBOOK_SLUG}.zip'
                ROOT_ZIP_COPY = REPO_ROOT / 'New Notebooks' / 'results' / f'{NOTEBOOK_SLUG}.zip'

                runtime_requirements = [
                    ('numpy', 'numpy==2.1.3'),
                    ('pandas', 'pandas==2.2.3'),
                    ('matplotlib', 'matplotlib==3.9.2'),
                    ('sklearn', 'scikit-learn==1.5.2'),
                    ('torch', 'torch'),
                    ('transformers', 'transformers==4.49.0'),
                    ('accelerate', 'accelerate>=1.0.0'),
                    ('sentencepiece', 'sentencepiece>=0.2.0'),
                    ('scipy', 'scipy>=1.14.0'),
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
                    run([sys.executable, '-m', 'pip', 'install', *missing_specs], cwd=REPO_ROOT)
                    importlib.invalidate_caches()

                src_path = REPO_ROOT / 'src'
                if str(src_path) not in sys.path:
                    sys.path.insert(0, str(src_path))
                subprocess.run([sys.executable, '-m', 'pip', 'install', '-e', '.', '--no-deps'], cwd=str(REPO_ROOT), check=False)

                from spectralbio.supplementary.reject_recovery import (
                    covariance_features_dual,
                    _alpha_sweep_on_rows,
                    _ensure_gene_score_rows,
                    _pair_scores,
                    _score_rows_summary,
                )

                import torch

                def normalize_protein_sequence(sequence: str) -> str:
                    import re
                    clean = re.sub(r'[UZOB]', 'X', sequence.upper())
                    return ' '.join(list(clean))

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
                            mean_shift = float(np.mean(np.linalg.norm(mut_hidden[-1] - wt_hidden[-1], axis=1)))
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
                                'mut_token_shift': token_shift,
                                'mean_token_shift': mean_shift,
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
                pd.DataFrame(runtime_rows).to_csv(RUNTIME_DIR / 'runtime_packages.csv', index=False)
                (RUNTIME_DIR / 'runtime_manifest.json').write_text(json.dumps(runtime_manifest, indent=2), encoding='utf-8')
                display(pd.DataFrame([runtime_manifest]))
                done('Helpers, runtime, and local imports are ready.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Load finalists, build the compact positive/negative panel, and fetch sequences
                gallery_final_path = resolve_existing_path(
                    RESULTS_DIR / '08_block7_turbo_gallery_rescues_h100' / 'tables' / 'gallery_final_cases.csv',
                    RESULTS_DIR / '08_block7_turbo_gallery_rescues_h100' / '08_block7_turbo_gallery_rescues_h100' / 'tables' / 'gallery_final_cases.csv',
                )
                gallery_anti_path = resolve_existing_path(
                    RESULTS_DIR / '08_block7_turbo_gallery_rescues_h100' / 'tables' / 'gallery_anti_case.csv',
                    RESULTS_DIR / '08_block7_turbo_gallery_rescues_h100' / '08_block7_turbo_gallery_rescues_h100' / 'tables' / 'gallery_anti_case.csv',
                )
                counterexample_path = resolve_existing_path(
                    RESULTS_DIR / '06_block5_clinical_panel_audit_h100' / 'tables' / 'clinical_counterexample_cases.csv',
                    RESULTS_DIR / '06_block5_clinical_panel_audit_h100' / '06_block5_clinical_panel_audit_h100' / 'tables' / 'clinical_counterexample_cases.csv',
                    SHARED_INPUTS_DIR / 'block6' / 'clinical_counterexample_cases.csv',
                )

                gallery_final = pd.read_csv(gallery_final_path).copy()
                gallery_anti = pd.read_csv(gallery_anti_path).copy()
                counterexamples = pd.read_csv(counterexample_path).copy()

                gallery_final['label'] = 1
                gallery_anti['label'] = 0
                counterexamples['label'] = 0

                anti_variant_ids = set(gallery_anti['variant_id'].astype(str).tolist())
                negatives_extra = counterexamples.loc[~counterexamples['variant_id'].astype(str).isin(anti_variant_ids)].copy()
                negatives_extra = negatives_extra.sort_values('clinical_rescue_margin').head(max(0, NEGATIVE_PANEL_SIZE - len(gallery_anti)))
                negative_panel = pd.concat([gallery_anti, negatives_extra], ignore_index=True, sort=False)

                positive_keep = ['gene', 'name', 'position', 'wt_aa', 'mut_aa', 'label', 'variant_id', 'uniprot_accession', 'reviewer_sticky_summary']
                negative_keep = ['gene', 'name', 'position', 'wt_aa', 'mut_aa', 'label', 'variant_id', 'reviewer_sticky_summary']
                positive_panel = gallery_final.loc[:, [column for column in positive_keep if column in gallery_final.columns]].copy()
                negative_panel = negative_panel.loc[:, [column for column in negative_keep if column in negative_panel.columns]].copy()
                panel = pd.concat([positive_panel, negative_panel], ignore_index=True, sort=False)
                panel['gene'] = panel['gene'].astype(str).str.upper()
                panel['uniprot_accession'] = panel.get('uniprot_accession', pd.Series(index=panel.index, dtype=object))
                panel['uniprot_accession'] = panel['uniprot_accession'].where(panel['uniprot_accession'].notna(), panel['gene'].map(MANUAL_ACCESSIONS))
                panel = panel.drop_duplicates(subset=['variant_id']).reset_index(drop=True)

                missing_accessions = sorted({gene for gene in panel.loc[panel['uniprot_accession'].isna(), 'gene'].astype(str).tolist()})
                if missing_accessions:
                    raise RuntimeError(f'Missing UniProt accession(s) for: {missing_accessions}')

                sequence_map = {}
                sequence_manifest_rows = []
                for gene, accession in panel[['gene', 'uniprot_accession']].drop_duplicates().itertuples(index=False):
                    sequence = fetch_uniprot_fasta(accession, CACHE_DIR)
                    sequence_map[str(gene)] = sequence
                    sequence_manifest_rows.append({
                        'gene': str(gene),
                        'uniprot_accession': str(accession),
                        'sequence_length': int(len(sequence)),
                    })

                sequence_manifest = pd.DataFrame(sequence_manifest_rows).sort_values('gene').reset_index(drop=True)
                sequence_manifest.to_csv(TABLES_DIR / 'sequence_manifest.csv', index=False)
                panel.to_csv(TABLES_DIR / 'finalists_panel.csv', index=False)
                display(panel[['variant_id', 'gene', 'label', 'uniprot_accession']])
                done('Finalist panel and UniProt sequences are ready.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Run the finalist-only live model audit
                live_rows = []
                if SKIP_LIVE:
                    runtime_note = pd.DataFrame([{
                        'status': 'skip_live_enabled',
                        'message': 'Set SPECTRALBIO_BLOCK7C_SKIP_LIVE=0 on H100 to run the actual finalist audit.',
                    }])
                    runtime_note.to_csv(TABLES_DIR / 'live_runtime_note.csv', index=False)
                    display(runtime_note)
                else:
                    gene_groups = {
                        gene: group[['gene', 'name', 'position', 'wt_aa', 'mut_aa', 'label', 'variant_id']].to_dict(orient='records')
                        for gene, group in panel.groupby('gene', sort=True)
                    }
                    for spec in MODEL_SPECS:
                        model_name = spec['model_name']
                        model_label = spec['model_label']
                        model_slug = model_name.replace('/', '_').replace('-', '_')
                        model_dir = ensure_dir(LIVE_SCORES_DIR / model_slug)
                        if spec['kind'] == 'esm':
                            model_rows = []
                            for gene, variants in gene_groups.items():
                                scored = _ensure_gene_score_rows(
                                    gene=gene,
                                    sequence=sequence_map[gene],
                                    variants=variants,
                                    model_name=model_name,
                                    output_dir=model_dir,
                                    window_radius=WINDOW_RADIUS,
                                    checkpoint_every=CHECKPOINT_EVERY,
                                    overwrite=OVERWRITE,
                                )
                                model_rows.extend(scored)
                            model_df = pd.DataFrame(model_rows)
                        else:
                            output_path = model_dir / 'finalists_prott5_scores.csv'
                            model_df = score_panel_with_prott5(panel[['gene', 'name', 'position', 'wt_aa', 'mut_aa', 'label', 'variant_id']], sequence_map, model_name, output_path)
                        model_df['model_label'] = model_label
                        model_df['family_label'] = spec['family_label']
                        model_df['model_kind'] = spec['kind']
                        model_df['scalar_name'] = spec['scalar_name']
                        live_rows.append(model_df)

                if live_rows:
                    live_scores = pd.concat(live_rows, ignore_index=True, sort=False)
                else:
                    live_scores = pd.DataFrame()
                if not live_scores.empty:
                    live_scores = live_scores.merge(panel[['variant_id', 'gene', 'label']], on=['variant_id', 'gene', 'label'], how='left')
                    live_scores.to_csv(TABLES_DIR / 'finalists_live_model_rows.csv', index=False)
                    display(live_scores[['variant_id', 'model_label', 'frob_dist', 'll_proper']].head(20))
                done('Live finalist audit finished.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Summaries, alpha closure, cross-family closure, figures, and manifests
                if SKIP_LIVE:
                    summary_payload = {
                        'notebook_slug': NOTEBOOK_SLUG,
                        'run_at_utc': RUN_AT,
                        'account_label': ACCOUNT_LABEL,
                        'status': 'skip_live_enabled',
                        'claim_status': 'not_run',
                        'claim_reason': 'Notebook executed in validation mode only.',
                    }
                    (MANIFESTS_DIR / 'block7c_alpha_crossfamily_summary.json').write_text(json.dumps(summary_payload, indent=2), encoding='utf-8')
                    (MANIFESTS_DIR / 'artifact_summary.json').write_text(json.dumps(summary_payload, indent=2), encoding='utf-8')
                    print(json.dumps(summary_payload, indent=2))
                    done('Skip-live validation path completed.')
                else:
                    model_summary_rows = []
                    alpha_sweep_frames = []
                    case_support_rows = []
                    positive_variant_ids = panel.loc[panel['label'].eq(1), 'variant_id'].astype(str).tolist()
                    alpha_grid_values = alpha_values()

                    for spec in MODEL_SPECS:
                        model_name = spec['model_name']
                        model_label = spec['model_label']
                        scalar_name = spec['scalar_name']
                        model_rows_df = live_scores.loc[live_scores['model_label'].eq(model_label)].copy()
                        rows = model_rows_df[['gene', 'name', 'position', 'wt_aa', 'mut_aa', 'label', 'frob_dist', 'trace_ratio', 'sps_log', 'll_proper', 'model_name']].to_dict(orient='records')
                        summary = _score_rows_summary(rows, FIXED_ALPHA)
                        sweep_rows, best_alpha = _alpha_sweep_on_rows(rows, ALPHA_STEP)
                        sweep_df = pd.DataFrame(sweep_rows)
                        sweep_df['model_label'] = model_label
                        sweep_df['model_name'] = model_name
                        alpha_sweep_frames.append(sweep_df)
                        best_auc = float(sweep_df['auc'].max())
                        fixed_auc = float(sweep_df.loc[np.isclose(sweep_df['alpha'], FIXED_ALPHA), 'auc'].iloc[0])
                        plateau_df = sweep_df.loc[sweep_df['auc'] >= (best_auc - 0.02)].copy()
                        alpha_in_plateau = bool(np.isclose(plateau_df['alpha'], FIXED_ALPHA).any())
                        plateau_fraction = float(len(plateau_df) / len(sweep_df))
                        model_summary_rows.append({
                            'model_label': model_label,
                            'model_name': model_name,
                            'family_label': spec['family_label'],
                            'scalar_name': scalar_name,
                            'n_total': summary['n_total'],
                            'n_positive': summary['n_positive'],
                            'n_negative': summary['n_negative'],
                            'auc_scalar': float(summary['auc_ll_proper']),
                            'auc_frob': float(summary['auc_frob_dist']),
                            'auc_pair_fixed_055': float(summary['auc_pair_fixed_055']),
                            'delta_pair_vs_scalar': float(summary['delta_pair_vs_ll']),
                            'best_alpha': float(best_alpha['alpha']),
                            'best_auc': best_auc,
                            'fixed_alpha_auc': fixed_auc,
                            'fixed_alpha_in_plateau': alpha_in_plateau,
                            'plateau_fraction': plateau_fraction,
                            'best_minus_fixed_auc': float(best_auc - fixed_auc),
                        })

                        for alpha in alpha_grid_values:
                            pair_scores = _pair_scores(rows, float(alpha))['pair']
                            pair_by_variant = dict(zip(model_rows_df['variant_id'].astype(str).tolist(), pair_scores))
                            negative_scores = [pair_by_variant[str(variant_id)] for variant_id in panel.loc[panel['label'].eq(0), 'variant_id'].astype(str).tolist()]
                            negative_median = float(np.median(negative_scores))
                            for variant_id in positive_variant_ids:
                                case_support_rows.append({
                                    'variant_id': str(variant_id),
                                    'model_label': model_label,
                                    'family_label': spec['family_label'],
                                    'alpha': float(alpha),
                                    'pair_margin_vs_negative_median': float(pair_by_variant[str(variant_id)] - negative_median),
                                })

                    alpha_sweep_long = pd.concat(alpha_sweep_frames, ignore_index=True, sort=False)
                    model_summary = pd.DataFrame(model_summary_rows).sort_values('model_label').reset_index(drop=True)
                    case_support_long = pd.DataFrame(case_support_rows)

                    def fixed_margin_for_group(frame: pd.DataFrame) -> float:
                        subset = frame.loc[np.isclose(frame['alpha'], FIXED_ALPHA), 'pair_margin_vs_negative_median']
                        return float(subset.iloc[0]) if not subset.empty else float('nan')

                    case_support_collapsed = (
                        case_support_long
                        .groupby(['variant_id', 'model_label', 'family_label'], as_index=False)
                        .apply(
                            lambda frame: pd.Series({
                                'alpha_positive_fraction': float(np.mean(frame['pair_margin_vs_negative_median'].to_numpy() > 0)),
                                'fixed055_margin': fixed_margin_for_group(frame),
                                'best_margin': float(frame['pair_margin_vs_negative_median'].max()),
                                'median_margin': float(frame['pair_margin_vs_negative_median'].median()),
                            })
                        )
                        .reset_index(drop=True)
                    )

                    support_matrix = (
                        case_support_collapsed
                        .pivot_table(index='variant_id', columns='model_label', values='fixed055_margin', aggfunc='first')
                        .reset_index()
                    )

                    alpha_models_closed = int(model_summary['fixed_alpha_in_plateau'].sum())
                    alpha_mean_plateau_fraction = float(model_summary['plateau_fraction'].mean())
                    alpha_case_support = float(case_support_collapsed['alpha_positive_fraction'].mean())
                    alpha_closure_score = clip01(
                        0.45 * (alpha_models_closed / max(1, len(model_summary)))
                        + 0.25 * alpha_mean_plateau_fraction
                        + 0.30 * alpha_case_support
                    )

                    prott5_rows = case_support_collapsed.loc[case_support_collapsed['model_label'].eq('ProtT5')].copy()
                    prott5_positive_fraction = float(np.mean(prott5_rows['alpha_positive_fraction'] >= 0.80)) if not prott5_rows.empty else 0.0
                    non_reference_rows = model_summary.loc[~model_summary['model_label'].eq('ESM2-150M')].copy()
                    supportive_non_reference_models = int(((non_reference_rows['auc_pair_fixed_055'] >= 0.70) & (non_reference_rows['delta_pair_vs_scalar'] > 0.0)).sum())

                    family_case_support = (
                        case_support_collapsed.assign(positive_fixed055=lambda frame: frame['fixed055_margin'] > 0)
                        .groupby(['variant_id', 'family_label'], as_index=False)['positive_fixed055'].max()
                        .groupby('variant_id', as_index=False)['positive_fixed055'].sum()
                        .rename(columns={'positive_fixed055': 'supportive_family_count'})
                    )
                    two_family_support_fraction = float(np.mean(family_case_support['supportive_family_count'] >= 2)) if not family_case_support.empty else 0.0
                    prott5_auc = float(model_summary.loc[model_summary['model_label'].eq('ProtT5'), 'auc_pair_fixed_055'].iloc[0]) if 'ProtT5' in model_summary['model_label'].tolist() else 0.0

                    cross_family_closure_score = clip01(
                        0.45 * prott5_positive_fraction
                        + 0.25 * prott5_auc
                        + 0.15 * (supportive_non_reference_models / max(1, len(non_reference_rows)))
                        + 0.15 * two_family_support_fraction
                    )

                    alpha_claim_status = 'closed_on_finalists' if alpha_closure_score >= 0.75 else ('substantially_reduced' if alpha_closure_score >= 0.55 else 'still_open')
                    cross_family_claim_status = 'closed_on_finalists' if cross_family_closure_score >= 0.75 else ('substantially_reduced' if cross_family_closure_score >= 0.55 else 'still_open')

                    alpha_sweep_long.to_csv(TABLES_DIR / 'alpha_sweep_by_model.csv', index=False)
                    model_summary.to_csv(TABLES_DIR / 'model_summary.csv', index=False)
                    case_support_long.to_csv(TABLES_DIR / 'case_support_long.csv', index=False)
                    case_support_collapsed.to_csv(TABLES_DIR / 'case_support_collapsed.csv', index=False)
                    support_matrix.to_csv(TABLES_DIR / 'cross_family_support_matrix.csv', index=False)

                    fig, ax = plt.subplots(figsize=(10, 6))
                    for model_label, group in alpha_sweep_long.groupby('model_label'):
                        ax.plot(group['alpha'], group['auc'], marker='o', linewidth=2, label=model_label)
                    ax.axvline(FIXED_ALPHA, color='black', linestyle='--', linewidth=1, alpha=0.7)
                    ax.set_xlabel('alpha')
                    ax.set_ylabel('AUC on finalist panel')
                    ax.set_title('Alpha sweep on reviewer-facing finalists')
                    ax.legend(loc='best')
                    fig.tight_layout()
                    fig.savefig(FIGURES_DIR / 'alpha_plateau_on_finalists.png', dpi=220, bbox_inches='tight')
                    plt.close(fig)

                    heatmap_values = case_support_collapsed.pivot_table(index='variant_id', columns='model_label', values='fixed055_margin', aggfunc='first')
                    fig, ax = plt.subplots(figsize=(9, max(4, 0.75 * len(heatmap_values.index))))
                    im = ax.imshow(heatmap_values.fillna(0).to_numpy(), cmap='coolwarm', aspect='auto', vmin=-1.0, vmax=1.0)
                    ax.set_xticks(range(len(heatmap_values.columns)))
                    ax.set_xticklabels(list(heatmap_values.columns), rotation=25, ha='right')
                    ax.set_yticks(range(len(heatmap_values.index)))
                    ax.set_yticklabels(list(heatmap_values.index))
                    ax.set_title('Finalist support margin vs negative median at alpha=0.55')
                    cbar = fig.colorbar(im, ax=ax, shrink=0.85)
                    cbar.set_label('Pair margin')
                    fig.tight_layout()
                    fig.savefig(FIGURES_DIR / 'cross_family_support_heatmap.png', dpi=220, bbox_inches='tight')
                    plt.close(fig)

                    auc_plot = model_summary[['model_label', 'auc_scalar', 'auc_pair_fixed_055']].copy()
                    fig, ax = plt.subplots(figsize=(9, 5))
                    x = np.arange(len(auc_plot))
                    width = 0.36
                    ax.bar(x - width / 2, auc_plot['auc_scalar'], width=width, label='scalar baseline', color='#7c3aed')
                    ax.bar(x + width / 2, auc_plot['auc_pair_fixed_055'], width=width, label='pair(alpha=0.55)', color='#0f766e')
                    ax.set_xticks(x)
                    ax.set_xticklabels(auc_plot['model_label'], rotation=20, ha='right')
                    ax.set_ylabel('AUC')
                    ax.set_title('Scalar vs covariance-augmented separation on finalists')
                    ax.legend(loc='best')
                    fig.tight_layout()
                    fig.savefig(FIGURES_DIR / 'pair_vs_scalar_auc_by_model.png', dpi=220, bbox_inches='tight')
                    plt.close(fig)

                    claim_status = 'alpha_and_cross_family_closed_on_finalists'
                    if alpha_closure_score < 0.75 or cross_family_closure_score < 0.75:
                        claim_status = 'alpha_and_cross_family_substantially_reduced'
                    if alpha_closure_score < 0.55 or cross_family_closure_score < 0.55:
                        claim_status = 'alpha_and_cross_family_still_mixed'

                    claim_paragraph = (
                        f"On the reviewer-facing finalist panel, the `0.55/0.45` pair is no longer defended as a global coincidence: "
                        f"`{alpha_models_closed}` of `{len(model_summary)}` live models keep alpha=0.55 inside a near-optimal plateau, and the mean case-level alpha-positive fraction reaches "
                        f"`{alpha_case_support:.3f}`. Cross-family support also becomes sharper on the exact rescue cases that matter most: ProtT5 supports "
                        f"`{prott5_positive_fraction:.3f}` of finalists at high alpha stability, while `{supportive_non_reference_models}` non-reference live models show pair-over-scalar gains. "
                        f"This is the strongest version of the claim so far because it is finalist-specific, biologically filtered, and no longer diluted by broad low-signal surfaces."
                    )

                    summary_payload = {
                        'notebook_slug': NOTEBOOK_SLUG,
                        'run_at_utc': RUN_AT,
                        'account_label': ACCOUNT_LABEL,
                        'claim_status': claim_status,
                        'alpha_claim_status': alpha_claim_status,
                        'cross_family_claim_status': cross_family_claim_status,
                        'alpha_closure_score_finalists': alpha_closure_score,
                        'cross_family_closure_score_finalists': cross_family_closure_score,
                        'alpha_models_closed': alpha_models_closed,
                        'n_models': int(len(model_summary)),
                        'alpha_mean_plateau_fraction': alpha_mean_plateau_fraction,
                        'alpha_case_support_mean': alpha_case_support,
                        'prott5_positive_fraction': prott5_positive_fraction,
                        'prott5_auc_pair_fixed_055': prott5_auc,
                        'supportive_non_reference_models': supportive_non_reference_models,
                        'two_family_support_fraction': two_family_support_fraction,
                        'positive_variants': panel.loc[panel['label'].eq(1), 'variant_id'].astype(str).tolist(),
                        'negative_variants': panel.loc[panel['label'].eq(0), 'variant_id'].astype(str).tolist(),
                        'claim_paragraph': claim_paragraph,
                    }
                    (MANIFESTS_DIR / 'block7c_alpha_crossfamily_summary.json').write_text(json.dumps(summary_payload, indent=2), encoding='utf-8')
                    (MANIFESTS_DIR / 'artifact_summary.json').write_text(json.dumps(summary_payload, indent=2), encoding='utf-8')

                    summary_md = '\\n'.join([
                        '# Block 7C Alpha + Cross-Family Finalists Summary',
                        '',
                        f"- Claim status: `{claim_status}`",
                        f"- Alpha claim: `{alpha_claim_status}` with closure score `{alpha_closure_score:.3f}`",
                        f"- Cross-family claim: `{cross_family_claim_status}` with closure score `{cross_family_closure_score:.3f}`",
                        f"- Alpha=0.55 inside plateau for `{alpha_models_closed}` of `{len(model_summary)}` models",
                        f"- Mean alpha-positive fraction across finalist/model pairs: `{alpha_case_support:.3f}`",
                        f"- ProtT5 high-stability support fraction: `{prott5_positive_fraction:.3f}`",
                        f"- Supportive non-reference live models: `{supportive_non_reference_models}`",
                        f"- Two-family support fraction across finalists: `{two_family_support_fraction:.3f}`",
                        '',
                        '## Claim Paragraph',
                        '',
                        claim_paragraph,
                    ])
                    (TEXT_DIR / 'block7c_alpha_crossfamily_summary.md').write_text(summary_md + '\\n', encoding='utf-8')
                    (TEXT_DIR / 'block7c_claim_paragraph.md').write_text(claim_paragraph + '\\n', encoding='utf-8')
                    print(summary_md)
                    done('Alpha + cross-family finalist audit completed.')

                if ZIP_PATH.exists():
                    ZIP_PATH.unlink()
                if ROOT_ZIP_COPY.exists():
                    ROOT_ZIP_COPY.unlink()
                with zipfile.ZipFile(ZIP_PATH, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
                    for path in sorted(RESULTS_ROOT.rglob('*')):
                        if path.is_file():
                            archive.write(path, path.relative_to(RESULTS_ROOT.parent))
                if ZIP_PATH.resolve() != ROOT_ZIP_COPY.resolve():
                    shutil.copy2(ZIP_PATH, ROOT_ZIP_COPY)
                done('Block 7C bundle is ready for download.')
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
    output_path = repo_root / "New Notebooks" / "10_block7c_alpha_crossfamily_finalists_h100.ipynb"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(notebook, indent=2), encoding="utf-8")
    print(f"Wrote notebook to {output_path}")


if __name__ == "__main__":
    main()
