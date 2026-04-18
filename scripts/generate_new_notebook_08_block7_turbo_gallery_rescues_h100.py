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
            "# Experiment: SpectralBio Block 7 Turbo - Reviewer-Grip Rescue Gallery (H100)\n\n"
            "Objective:\n"
            "- Turn the bounded evidence from Blocks 2, 3, 5, and 10 into a memorable gallery of rescue cases.\n"
            "- Prefer cases that simultaneously show covariance-heavy rescue, local structural support, alpha-stable ranking, and cross-model support where available.\n"
            "- Include one explicit anti-case to show where the story breaks.\n"
            "- Produce reviewer-facing tables and figures under `New Notebooks/results/08_block7_turbo_gallery_rescues_h100/`.\n"
        ),
        markdown_cell(
            "## Deliverables\n\n"
            "- Unified candidate pool across Block 2 exemplars, Block 5 clinical shortlist, and Block 10 TP53 mechanistic cases.\n"
            "- WT structure support metrics with AlphaFold fallback for finalists missing Block 3 annotations.\n"
            "- Case-level alpha-stability diagnostics that answer the `0.55/0.45` criticism at exemplar level.\n"
            "- Cross-model support summary using existing `ProtT5`, `ESM2-35M`, `ESM2-150M`, `ESM2-650M`, and `ESM-1v` evidence whenever available.\n"
            "- A final gallery of `3–5` rescue cases plus `1` anti-case, with a reviewer-grip score and a concise claim paragraph.\n"
        ),
        code_cell(
            dedent(
                """
                # Setup: imports, identifiers, and notebook knobs
                from __future__ import annotations

                import importlib
                import json
                import math
                import os
                import platform
                import shutil
                import subprocess
                import sys
                import zipfile
                from datetime import datetime, timezone
                from pathlib import Path

                import matplotlib.pyplot as plt
                import numpy as np
                import pandas as pd
                import requests
                from IPython.display import display

                NOTEBOOK_SLUG = '08_block7_turbo_gallery_rescues_h100'
                ACCOUNT_LABEL = os.environ.get('SPECTRALBIO_ACCOUNT_LABEL', 'local_run')
                RUN_AT = datetime.now(timezone.utc).isoformat()
                OVERWRITE = os.environ.get('SPECTRALBIO_OVERWRITE', '').strip().lower() in {'1', 'true', 'yes'}
                TOP_POSITIVE_CASES = int(os.environ.get('SPECTRALBIO_BLOCK7_TOP_POSITIVE_CASES', '5'))
                TOP_NEGATIVE_CASES = int(os.environ.get('SPECTRALBIO_BLOCK7_TOP_NEGATIVE_CASES', '1'))
                WINDOW_RADIUS = int(os.environ.get('SPECTRALBIO_BLOCK7_WINDOW_RADIUS', '20'))
                CONTACT_RADIUS_ANGSTROM = float(os.environ.get('SPECTRALBIO_BLOCK7_CONTACT_RADIUS', '8.0'))
                LONG_RANGE_GAP = int(os.environ.get('SPECTRALBIO_BLOCK7_LONG_RANGE_GAP', '24'))
                ALPHA_GRID = [round(value, 2) for value in np.linspace(0.10, 0.90, 17)]
                REQUEST_TIMEOUT_SEC = int(os.environ.get('SPECTRALBIO_BLOCK7_REQUEST_TIMEOUT_SEC', '40'))

                MANUAL_ACCESSIONS = {
                    'ANKRD11': 'Q6UB99',
                    'BRCA1': 'P38398',
                    'BRCA2': 'P51587',
                    'COL2A1': 'P02458',
                    'CREBBP': 'Q92793',
                    'GRIN2A': 'Q12879',
                    'KMT2A': 'Q03164',
                    'MSH2': 'P43246',
                    'NSD1': 'Q96L73',
                    'TP53': 'P04637',
                    'TSC2': 'P49815',
                }

                def done(message: str) -> None:
                    print(f'TERMINEI PODE SEGUIR - {message}')

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
                    ('requests', 'requests>=2.32.0'),
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
                    subprocess.run(
                        [sys.executable, '-m', 'pip', 'install', *missing_specs],
                        check=True,
                        text=True,
                    )
                    importlib.invalidate_caches()
                    runtime_rows = []
                    for module_name, _ in runtime_requirements:
                        module = importlib.import_module(module_name)
                        version = getattr(module, '__version__', 'present')
                        runtime_rows.append({'module': module_name, 'status': 'installed_now', 'version': str(version)})

                print({
                    'notebook_slug': NOTEBOOK_SLUG,
                    'account_label': ACCOUNT_LABEL,
                    'top_positive_cases': TOP_POSITIVE_CASES,
                    'top_negative_cases': TOP_NEGATIVE_CASES,
                    'window_radius': WINDOW_RADIUS,
                    'contact_radius_angstrom': CONTACT_RADIUS_ANGSTROM,
                    'alpha_grid': ALPHA_GRID,
                    'overwrite': OVERWRITE,
                    'python': sys.version.split()[0],
                    'platform': platform.platform(),
                    'runtime': runtime_rows,
                })
                done('Initial configuration loaded.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Helpers: repo discovery, paths, numeric utilities, structure parsing, and AlphaFold cache
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

                def looks_like_repo(path: Path) -> bool:
                    return (path / 'src' / 'spectralbio').exists() and (path / 'notebooks').exists()

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
                    raise FileNotFoundError('Could not locate the SpectralBio repository root. Set SPECTRALBIO_REPO_ROOT or run inside the repo.')

                def resolve_existing_path(raw: str | Path, repo_root: Path) -> Path:
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
                    return raw_path

                def safe_float(value, default: float = float('nan')) -> float:
                    try:
                        return float(value)
                    except Exception:
                        return default

                def normalize_series(series: pd.Series) -> pd.Series:
                    numeric = pd.to_numeric(series, errors='coerce')
                    valid = numeric.dropna()
                    if valid.empty:
                        return pd.Series(np.nan, index=series.index, dtype=float)
                    low = float(valid.min())
                    high = float(valid.max())
                    if high <= low:
                        result = pd.Series(0.0, index=series.index, dtype=float)
                        result[numeric.isna()] = np.nan
                        return result
                    return (numeric - low) / (high - low)

                def zscore_series(series: pd.Series) -> pd.Series:
                    numeric = pd.to_numeric(series, errors='coerce')
                    valid = numeric.dropna()
                    if valid.empty:
                        return pd.Series(np.nan, index=series.index, dtype=float)
                    std = float(valid.std(ddof=0))
                    if std <= 1e-12:
                        result = pd.Series(0.0, index=series.index, dtype=float)
                        result[numeric.isna()] = np.nan
                        return result
                    return (numeric - float(valid.mean())) / std

                def alpha_stability_payload(row: pd.Series) -> dict:
                    ll_rank = safe_float(row.get('ll_rank_norm'))
                    frob_rank = safe_float(row.get('frob_rank_norm'))
                    scalar_baseline = safe_float(row.get('scalar_baseline_for_audit', ll_rank))
                    if math.isnan(ll_rank) or math.isnan(frob_rank):
                        return {
                            'alpha_positive_fraction': float('nan'),
                            'alpha_margin_median': float('nan'),
                            'alpha_margin_max': float('nan'),
                            'alpha_margin_min': float('nan'),
                            'alpha_stability_interval': '',
                        }
                    margins = []
                    positive_grid = []
                    for alpha in ALPHA_GRID:
                        pair_rank = alpha * frob_rank + (1.0 - alpha) * ll_rank
                        margin = pair_rank - scalar_baseline
                        margins.append(margin)
                        if margin >= 0.05:
                            positive_grid.append(alpha)
                    interval = ''
                    if positive_grid:
                        interval = f'{min(positive_grid):.2f}-{max(positive_grid):.2f}'
                    return {
                        'alpha_positive_fraction': float(len(positive_grid) / len(ALPHA_GRID)),
                        'alpha_margin_median': float(np.median(margins)),
                        'alpha_margin_max': float(np.max(margins)),
                        'alpha_margin_min': float(np.min(margins)),
                        'alpha_stability_interval': interval,
                    }

                def fetch_json(url: str) -> dict | list | None:
                    try:
                        response = requests.get(url, timeout=REQUEST_TIMEOUT_SEC, headers={'User-Agent': 'SpectralBio-Block7/1.0'})
                        response.raise_for_status()
                        return response.json()
                    except Exception as exc:
                        print(f'JSON warning for {url}: {type(exc).__name__}: {exc}')
                        return None

                def fetch_text(url: str) -> str | None:
                    try:
                        response = requests.get(url, timeout=REQUEST_TIMEOUT_SEC, headers={'User-Agent': 'SpectralBio-Block7/1.0'})
                        response.raise_for_status()
                        return response.text
                    except Exception as exc:
                        print(f'Text warning for {url}: {type(exc).__name__}: {exc}')
                        return None

                THREE_TO_ONE = {
                    'ALA': 'A', 'ARG': 'R', 'ASN': 'N', 'ASP': 'D', 'CYS': 'C', 'GLN': 'Q', 'GLU': 'E', 'GLY': 'G',
                    'HIS': 'H', 'ILE': 'I', 'LEU': 'L', 'LYS': 'K', 'MET': 'M', 'PHE': 'F', 'PRO': 'P', 'SER': 'S',
                    'THR': 'T', 'TRP': 'W', 'TYR': 'Y', 'VAL': 'V',
                }

                def fetch_alphafold_artifacts(accession: str, cache_dir: Path) -> tuple[Path | None, dict]:
                    accession = accession.strip()
                    pdb_path = cache_dir / f'{accession}.pdb'
                    metadata_path = cache_dir / f'{accession}.json'
                    metadata_payload = None
                    if metadata_path.exists():
                        try:
                            metadata_payload = json.loads(metadata_path.read_text(encoding='utf-8'))
                        except Exception:
                            metadata_payload = None
                    if metadata_payload is None:
                        metadata_payload = fetch_json(f'https://alphafold.ebi.ac.uk/api/prediction/{accession}')
                        if metadata_payload is not None:
                            metadata_path.write_text(json.dumps(metadata_payload, indent=2), encoding='utf-8')
                    if not pdb_path.exists():
                        pdb_url = None
                        if isinstance(metadata_payload, list) and metadata_payload:
                            pdb_url = metadata_payload[0].get('pdbUrl')
                        elif isinstance(metadata_payload, dict):
                            pdb_url = metadata_payload.get('pdbUrl')
                        if pdb_url:
                            pdb_text = fetch_text(pdb_url)
                            if pdb_text:
                                pdb_path.write_text(pdb_text, encoding='utf-8')
                    if pdb_path.exists():
                        return pdb_path, metadata_payload if metadata_payload is not None else {}
                    return None, metadata_payload if metadata_payload is not None else {}

                def parse_ca_records(pdb_path: Path) -> pd.DataFrame:
                    rows = []
                    for raw_line in pdb_path.read_text(encoding='utf-8', errors='replace').splitlines():
                        if not raw_line.startswith('ATOM'):
                            continue
                        atom_name = raw_line[12:16].strip()
                        residue_name = raw_line[17:20].strip()
                        if atom_name != 'CA' or residue_name not in THREE_TO_ONE:
                            continue
                        rows.append({
                            'residue_number': int(raw_line[22:26]),
                            'residue_name': residue_name,
                            'residue_aa': THREE_TO_ONE[residue_name],
                            'x': float(raw_line[30:38]),
                            'y': float(raw_line[38:46]),
                            'z': float(raw_line[46:54]),
                            'plddt': float(raw_line[60:66]),
                        })
                    return pd.DataFrame(rows)

                def structure_metrics_for_site(ca_frame: pd.DataFrame, residue_number: int, wt_aa: str, window_radius: int = WINDOW_RADIUS) -> dict:
                    if ca_frame.empty:
                        return {}
                    exact = ca_frame.loc[ca_frame['residue_number'].eq(residue_number)].copy()
                    if exact.empty:
                        exact = ca_frame.iloc[(ca_frame['residue_number'] - residue_number).abs().argsort()[:1]].copy()
                    site = exact.iloc[0]
                    local = ca_frame.loc[
                        ca_frame['residue_number'].between(int(site['residue_number']) - window_radius, int(site['residue_number']) + window_radius)
                    ].copy()
                    coords = ca_frame[['x', 'y', 'z']].to_numpy(dtype=float)
                    site_coords = np.array([site['x'], site['y'], site['z']], dtype=float)
                    distances = np.sqrt(((coords - site_coords) ** 2).sum(axis=1))
                    site_contact_count = int(((distances <= CONTACT_RADIUS_ANGSTROM) & (distances > 0)).sum())
                    residue_offsets = np.abs(ca_frame['residue_number'].to_numpy(dtype=int) - int(site['residue_number']))
                    site_long_range_contact_count = int(((distances <= CONTACT_RADIUS_ANGSTROM) & (distances > 0) & (residue_offsets >= LONG_RANGE_GAP)).sum())
                    local_coords = local[['x', 'y', 'z']].to_numpy(dtype=float)
                    pairwise = np.sqrt(((local_coords[:, None, :] - local_coords[None, :, :]) ** 2).sum(axis=2))
                    local_contact_counts = ((pairwise <= CONTACT_RADIUS_ANGSTROM) & (pairwise > 0)).sum(axis=1)
                    return {
                        'resolved_residue_number': int(site['residue_number']),
                        'resolved_wt_aa': str(site['residue_aa']),
                        'exact_residue_found': int(int(site['residue_number']) == residue_number and str(site['residue_aa']) == str(wt_aa)),
                        'site_plddt': float(site['plddt']),
                        'window_plddt_mean': float(local['plddt'].mean()),
                        'window_size_resolved': int(len(local)),
                        'site_contact_count': site_contact_count,
                        'site_long_range_contact_count': site_long_range_contact_count,
                        'window_contact_mean': float(np.mean(local_contact_counts)) if len(local_contact_counts) else float('nan'),
                        'window_contact_max': float(np.max(local_contact_counts)) if len(local_contact_counts) else float('nan'),
                        'window_confident_fraction': float((local['plddt'] >= 70.0).mean()) if not local.empty else float('nan'),
                    }

                done('Helpers ready.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Resolve repository root, outputs, and upstream artifacts
                REPO_ROOT = find_repo_root()
                RESULTS_DIR = REPO_ROOT / 'New Notebooks' / 'results'
                RESULTS_ROOT = ensure_dir(RESULTS_DIR / NOTEBOOK_SLUG)
                TABLES_DIR = ensure_dir(RESULTS_ROOT / 'tables')
                FIGURES_DIR = ensure_dir(RESULTS_ROOT / 'figures')
                TEXT_DIR = ensure_dir(RESULTS_ROOT / 'text')
                MANIFESTS_DIR = ensure_dir(RESULTS_ROOT / 'manifests')
                RUNTIME_DIR = ensure_dir(RESULTS_ROOT / 'runtime')
                STRUCTURE_CACHE_DIR = ensure_dir(RUNTIME_DIR / 'structure_cache')
                ZIP_PATH = REPO_ROOT / 'New Notebooks' / 'results' / f'{NOTEBOOK_SLUG}.zip'
                ROOT_ZIP_COPY = REPO_ROOT / 'New Notebooks' / f'{NOTEBOOK_SLUG}.zip'

                repo_status = {
                    'repo_root': str(REPO_ROOT),
                    'head_commit': run(['git', 'rev-parse', 'HEAD'], cwd=REPO_ROOT).strip(),
                    'head_subject': run(['git', 'log', '-1', '--pretty=%s'], cwd=REPO_ROOT).strip(),
                    'branch': run(['git', 'branch', '--show-current'], cwd=REPO_ROOT).strip(),
                }
                display(pd.DataFrame([repo_status]))

                artifact_paths = {
                    'block2_candidates': resolve_existing_path('New Notebooks/results/02_block2_failure_mode_hunt_h100/tables/candidate_exemplars_ranked.csv', REPO_ROOT),
                    'block3_structure_metrics': resolve_existing_path('New Notebooks/results/05_block3_structure_bridge_h100/tables/structure_bridge_metrics.csv', REPO_ROOT),
                    'block5_shortlist': resolve_existing_path('New Notebooks/results/06_block5_clinical_panel_audit_h100/tables/clinical_case_shortlist_for_block7.csv', REPO_ROOT),
                    'block5_counterexamples': resolve_existing_path('New Notebooks/results/06_block5_clinical_panel_audit_h100/tables/clinical_counterexample_cases.csv', REPO_ROOT),
                    'block5_gene_audit': resolve_existing_path('New Notebooks/results/06_block5_clinical_panel_audit_h100/tables/clinical_gene_audit_table.csv', REPO_ROOT),
                    'block4_anchor_long': resolve_existing_path('New Notebooks/results/03_block4_model_agnostic_plms_h100_v2/tables/model_agnostic_anchor_long.csv', REPO_ROOT),
                    'block4_prott5_rows': resolve_existing_path('New Notebooks/results/03_block4_model_agnostic_plms_h100_v2/tables/prott5_subset_rows.csv', REPO_ROOT),
                    'block10_07b': resolve_existing_path('New Notebooks/results/07b_block10_structural_dissociation_tp53_h100/07b_block10_structural_dissociation_tp53_h100/tables/tp53_structural_pairs_variant_level_strict.csv', REPO_ROOT),
                }
                missing_artifacts = [key for key, path in artifact_paths.items() if not path.exists()]
                if missing_artifacts:
                    raise FileNotFoundError(f'Missing required upstream artifacts for Block 7 Turbo: {missing_artifacts}')

                candidates_block2 = pd.read_csv(artifact_paths['block2_candidates'])
                structure_metrics = pd.read_csv(artifact_paths['block3_structure_metrics'])
                shortlist_block5 = pd.read_csv(artifact_paths['block5_shortlist'])
                counterexamples_block5 = pd.read_csv(artifact_paths['block5_counterexamples'])
                gene_audit_block5 = pd.read_csv(artifact_paths['block5_gene_audit'])
                anchor_long_block4 = pd.read_csv(artifact_paths['block4_anchor_long'])
                prott5_rows = pd.read_csv(artifact_paths['block4_prott5_rows'])
                tp53_07b = pd.read_csv(artifact_paths['block10_07b'])

                artifact_inventory = pd.DataFrame(
                    [{'artifact_key': key, 'path': str(path), 'exists': path.exists()} for key, path in artifact_paths.items()]
                )
                artifact_inventory.to_csv(TABLES_DIR / 'artifact_inventory.csv', index=False)
                display(artifact_inventory)
                done('Upstream artifacts loaded.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Build the unified gallery candidate pool and enrich it with structure, alpha, and cross-model evidence
                def collapse_duplicate_columns(frame: pd.DataFrame) -> pd.DataFrame:
                    if frame.empty:
                        return frame
                    renamed = {}
                    for column in frame.columns:
                        if column.endswith('_x'):
                            renamed[column] = column[:-2]
                        elif column.endswith('_y'):
                            renamed[column] = column[:-2] + '_dup'
                    frame = frame.rename(columns=renamed)
                    for column in list(frame.columns):
                        if column.endswith('_dup'):
                            base = column[:-4]
                            if base in frame.columns:
                                frame[base] = frame[base].where(frame[base].notna(), frame[column])
                                frame = frame.drop(columns=[column])
                    return frame

                candidate_columns = [
                    'gene', 'name', 'position', 'wt_aa', 'mut_aa', 'label', 'variant_id',
                    'frob_dist', 'trace_ratio', 'sps_log', 'll_proper',
                    'll_rank_norm', 'frob_rank_norm', 'pair_rank_fixed_055',
                    'esm1v_ll_mean_norm', 'augmented_pair_fixed_055', 'reference_pair_norm',
                    'clinical_rescue_margin', 'covariance_only_gain',
                    'pair_repair', 'frob_repair', 'll_repair',
                    'context_signature', 'validation_role', 'structure_support',
                    'site_plddt', 'window_plddt_mean', 'site_contact_count', 'site_long_range_contact_count',
                ]

                block2_positive = candidates_block2.loc[candidates_block2['is_repair_exemplar'].fillna(False)].copy()
                block2_positive['gallery_source'] = 'block2_repair_exemplar'
                block2_positive['clinical_rescue_margin'] = pd.to_numeric(block2_positive.get('rescue_margin'), errors='coerce')
                block2_positive['pair_rank_fixed_055'] = pd.to_numeric(block2_positive.get('pair_norm'), errors='coerce')

                shortlist_positive = shortlist_block5.copy()
                shortlist_positive['gallery_source'] = 'block5_clinical_shortlist'

                tp53_anchor = tp53_07b.copy()
                tp53_anchor = tp53_anchor.loc[
                    tp53_anchor['variant_id'].isin(['TP53:V271M', 'TP53:R248S', 'TP53:G244S'])
                ].copy()
                tp53_anchor = tp53_anchor.rename(columns={'position_0': 'position'})
                tp53_anchor['position'] = pd.to_numeric(tp53_anchor['position'], errors='coerce')
                tp53_anchor['gallery_source'] = 'block10_tp53_mechanistic_anchor'
                tp53_anchor['label'] = 1
                tp53_anchor['clinical_rescue_margin'] = np.nan
                tp53_anchor['context_signature'] = tp53_anchor.get('blinded_group')
                tp53_anchor['structure_support'] = 'experimental_state_matched'

                candidate_pool = pd.concat(
                    [
                        block2_positive.reindex(columns=candidate_columns + ['gallery_source']),
                        shortlist_positive.reindex(columns=candidate_columns + ['gallery_source']),
                        tp53_anchor.reindex(columns=candidate_columns + ['gallery_source']),
                    ],
                    ignore_index=True,
                    sort=False,
                )
                candidate_pool = candidate_pool.dropna(subset=['variant_id']).drop_duplicates(subset=['variant_id'], keep='first').reset_index(drop=True)

                gene_audit_small = gene_audit_block5.loc[
                    :, ['gene', 'focus_role', 'delta_pair_vs_ll', 'delta_augmented_vs_esm1v', 'best_available_cross_model_delta']
                ].copy()
                candidate_pool = candidate_pool.merge(gene_audit_small, on='gene', how='left')

                structure_keep = [
                    'variant_id', 'uniprot_accession', 'resolved_residue_number', 'resolved_wt_aa', 'exact_residue_found',
                    'site_plddt', 'window_plddt_mean', 'window_size_resolved', 'site_contact_count',
                    'site_long_range_contact_count', 'window_contact_mean', 'window_contact_max', 'window_confident_fraction',
                    'cohort',
                ]
                structure_small = structure_metrics.loc[:, [column for column in structure_keep if column in structure_metrics.columns]].drop_duplicates(subset=['variant_id'])
                candidate_pool = candidate_pool.merge(structure_small, on='variant_id', how='left')
                candidate_pool = collapse_duplicate_columns(candidate_pool)

                candidate_pool['uniprot_accession'] = candidate_pool.get('uniprot_accession', pd.Series(index=candidate_pool.index, dtype=object))
                candidate_pool['uniprot_accession'] = candidate_pool['uniprot_accession'].where(candidate_pool['uniprot_accession'].notna(), candidate_pool['gene'].map(MANUAL_ACCESSIONS))

                structure_refresh_rows = []
                for row in candidate_pool.to_dict(orient='records'):
                    if not math.isnan(safe_float(row.get('site_plddt'))):
                        continue
                    accession = str(row.get('uniprot_accession') or '').strip()
                    if not accession:
                        continue
                    position = int(safe_float(row.get('position'), -1))
                    if position < 0:
                        continue
                    pdb_path, _ = fetch_alphafold_artifacts(accession, STRUCTURE_CACHE_DIR)
                    if pdb_path is None:
                        continue
                    ca_frame = parse_ca_records(pdb_path)
                    metrics = structure_metrics_for_site(ca_frame, position + 1, str(row.get('wt_aa', '')))
                    if metrics:
                        metrics['variant_id'] = row['variant_id']
                        metrics['uniprot_accession'] = accession
                        structure_refresh_rows.append(metrics)

                structure_refresh = pd.DataFrame(structure_refresh_rows).drop_duplicates(subset=['variant_id']) if structure_refresh_rows else pd.DataFrame(columns=['variant_id'])
                if not structure_refresh.empty:
                    candidate_pool = candidate_pool.merge(structure_refresh, on='variant_id', how='left', suffixes=('', '_refresh'))
                    for column in ['resolved_residue_number', 'resolved_wt_aa', 'exact_residue_found', 'site_plddt', 'window_plddt_mean', 'window_size_resolved', 'site_contact_count', 'site_long_range_contact_count', 'window_contact_mean', 'window_contact_max', 'window_confident_fraction', 'uniprot_accession']:
                        refresh_column = f'{column}_refresh'
                        if refresh_column in candidate_pool.columns:
                            if column in candidate_pool.columns:
                                candidate_pool[column] = candidate_pool[column].where(candidate_pool[column].notna(), candidate_pool[refresh_column])
                            else:
                                candidate_pool[column] = candidate_pool[refresh_column]
                            candidate_pool = candidate_pool.drop(columns=[refresh_column])

                prott5_rows['variant_id'] = prott5_rows['gene'].astype(str) + ':' + prott5_rows['wt_aa'].astype(str) + prott5_rows['position'].astype(int).astype(str) + prott5_rows['mut_aa'].astype(str)
                prott5_candidates = prott5_rows.loc[prott5_rows['audit_label'].eq(1)].copy()
                prott5_controls = prott5_rows.loc[prott5_rows['audit_label'].eq(0)].copy()
                support_rows = []
                for row in prott5_candidates.to_dict(orient='records'):
                    same_position_controls = prott5_controls.loc[
                        (prott5_controls['gene'].eq(row['gene']))
                        & (prott5_controls['position'].eq(row['position']))
                    ].copy()
                    if same_position_controls.empty:
                        same_position_controls = prott5_controls.loc[prott5_controls['gene'].eq(row['gene'])].copy()
                    control_pair = float(same_position_controls['pair_fixed_055'].mean()) if not same_position_controls.empty else float('nan')
                    control_frob = float(same_position_controls['frob_dist'].mean()) if not same_position_controls.empty else float('nan')
                    support_rows.append({
                        'variant_id': row['variant_id'],
                        'prott5_pair_fixed_055': float(row['pair_fixed_055']),
                        'prott5_frob_dist': float(row['frob_dist']),
                        'prott5_mut_token_shift': float(row['mut_token_shift']),
                        'prott5_control_pair_fixed_055': control_pair,
                        'prott5_control_frob_dist': control_frob,
                        'prott5_pair_advantage': float(row['pair_fixed_055'] - control_pair) if not math.isnan(control_pair) else float('nan'),
                        'prott5_frob_advantage': float(row['frob_dist'] - control_frob) if not math.isnan(control_frob) else float('nan'),
                    })
                prott5_support = pd.DataFrame(support_rows)
                candidate_pool = candidate_pool.merge(prott5_support, on='variant_id', how='left')

                alpha_payloads = []
                for row in candidate_pool.to_dict(orient='records'):
                    payload = alpha_stability_payload(pd.Series(row))
                    payload['variant_id'] = row['variant_id']
                    alpha_payloads.append(payload)
                alpha_stability = pd.DataFrame(alpha_payloads)
                candidate_pool = candidate_pool.merge(alpha_stability, on='variant_id', how='left')

                candidate_pool['clinical_margin_signal'] = normalize_series(candidate_pool['clinical_rescue_margin'])
                candidate_pool['pair_repair_signal'] = normalize_series(candidate_pool['pair_repair'])
                candidate_pool['structure_signal'] = normalize_series(
                    pd.to_numeric(candidate_pool['site_contact_count'], errors='coerce').fillna(0)
                    + pd.to_numeric(candidate_pool['window_confident_fraction'], errors='coerce').fillna(0) * 10.0
                )
                candidate_pool['prott5_signal'] = normalize_series(candidate_pool['prott5_pair_advantage'])
                candidate_pool['gene_generality_signal'] = normalize_series(candidate_pool['best_available_cross_model_delta'])
                candidate_pool['alpha_signal'] = pd.to_numeric(candidate_pool['alpha_positive_fraction'], errors='coerce')

                candidate_pool['reviewer_grip_score'] = (
                    zscore_series(candidate_pool['clinical_margin_signal']).fillna(0) * 1.25
                    + zscore_series(candidate_pool['pair_repair_signal']).fillna(0) * 1.10
                    + zscore_series(candidate_pool['structure_signal']).fillna(0) * 1.15
                    + zscore_series(candidate_pool['prott5_signal']).fillna(0) * 0.95
                    + zscore_series(candidate_pool['gene_generality_signal']).fillna(0) * 0.70
                    + zscore_series(candidate_pool['alpha_signal']).fillna(0) * 0.85
                )

                candidate_pool['has_strong_structure'] = (
                    pd.to_numeric(candidate_pool['site_plddt'], errors='coerce').fillna(0) >= 70
                ) & (
                    pd.to_numeric(candidate_pool['site_contact_count'], errors='coerce').fillna(0) >= 5
                )
                candidate_pool['has_prott5_support'] = pd.to_numeric(candidate_pool['prott5_pair_advantage'], errors='coerce').fillna(-999) >= 0.01
                candidate_pool['has_alpha_stability'] = pd.to_numeric(candidate_pool['alpha_positive_fraction'], errors='coerce').fillna(0) >= 0.50
                candidate_pool['has_repair_signal'] = pd.to_numeric(candidate_pool['pair_repair'], errors='coerce').fillna(-999) >= 0.10
                candidate_pool['positive_focus_gene'] = candidate_pool['focus_role'].fillna('').eq('positive_focus')
                candidate_pool['counterexample_gene'] = candidate_pool['focus_role'].fillna('').eq('counterexample')

                candidate_pool.to_csv(TABLES_DIR / 'gallery_candidate_pool.csv', index=False)
                alpha_stability.to_csv(TABLES_DIR / 'gallery_alpha_stability.csv', index=False)
                display(candidate_pool.sort_values('reviewer_grip_score', ascending=False).head(15)[[
                    'variant_id', 'gallery_source', 'reviewer_grip_score', 'clinical_rescue_margin', 'pair_repair',
                    'site_plddt', 'site_contact_count', 'prott5_pair_advantage', 'alpha_positive_fraction', 'focus_role'
                ]])
                done('Unified gallery pool enriched with structure, alpha, and cross-model evidence.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Select the final gallery, build reviewer-facing figures, and write artifacts
                counterexample_path = resolve_existing_path(
                    RESULTS_DIR / '06_block5_clinical_panel_audit_h100' / 'tables' / 'clinical_counterexample_cases.csv',
                    RESULTS_DIR / '06_block5_clinical_panel_audit_h100' / '06_block5_clinical_panel_audit_h100' / 'tables' / 'clinical_counterexample_cases.csv',
                )
                counterexamples = pd.read_csv(counterexample_path).copy()
                if 'variant_id' not in counterexamples.columns:
                    counterexamples['variant_id'] = (
                        counterexamples['gene'].astype(str)
                        + ':'
                        + counterexamples['wt_aa'].astype(str)
                        + counterexamples['position'].astype(int).astype(str)
                        + counterexamples['mut_aa'].astype(str)
                    )

                final_pool = candidate_pool.copy()
                final_pool['clinical_rescue_margin'] = pd.to_numeric(final_pool.get('clinical_rescue_margin'), errors='coerce')
                final_pool['pair_repair'] = pd.to_numeric(final_pool.get('pair_repair'), errors='coerce')
                final_pool['site_plddt'] = pd.to_numeric(final_pool.get('site_plddt'), errors='coerce')
                final_pool['site_contact_count'] = pd.to_numeric(final_pool.get('site_contact_count'), errors='coerce')
                final_pool['window_confident_fraction'] = pd.to_numeric(final_pool.get('window_confident_fraction'), errors='coerce')
                final_pool['best_available_cross_model_delta'] = pd.to_numeric(final_pool.get('best_available_cross_model_delta'), errors='coerce')
                final_pool['alpha_positive_fraction'] = pd.to_numeric(final_pool.get('alpha_positive_fraction'), errors='coerce')

                final_pool['story_bucket'] = np.select(
                    [
                        final_pool['gallery_source'].eq('clinical_shortlist'),
                        final_pool['gallery_source'].eq('block2_exemplar'),
                        final_pool['gallery_source'].eq('block10_07b_strict'),
                        final_pool['gallery_source'].eq('block10_07c_strict'),
                    ],
                    [
                        'clinical_rescue',
                        'failure_mode_repair',
                        'mechanistic_anchor',
                        'dissociation_hunter',
                    ],
                    default='mixed_evidence',
                )
                final_pool['selection_bonus'] = (
                    final_pool['positive_focus_gene'].astype(int) * 1.00
                    + final_pool['has_strong_structure'].astype(int) * 0.95
                    + final_pool['has_prott5_support'].astype(int) * 0.75
                    + final_pool['has_alpha_stability'].astype(int) * 0.65
                    + final_pool['has_repair_signal'].astype(int) * 0.90
                    + final_pool['story_bucket'].eq('clinical_rescue').astype(int) * 0.45
                    + final_pool['story_bucket'].eq('mechanistic_anchor').astype(int) * 0.25
                )
                final_pool['gallery_priority_score'] = pd.to_numeric(final_pool['reviewer_grip_score'], errors='coerce').fillna(-999) + final_pool['selection_bonus']

                positive_mask = (
                    ~final_pool['counterexample_gene'].fillna(False)
                    & (
                        final_pool['positive_focus_gene'].fillna(False)
                        | final_pool['has_repair_signal'].fillna(False)
                        | final_pool['story_bucket'].isin(['mechanistic_anchor', 'clinical_rescue'])
                    )
                    & (
                        final_pool['has_strong_structure'].fillna(False)
                        | final_pool['story_bucket'].eq('mechanistic_anchor')
                    )
                )

                positive_candidates = final_pool.loc[positive_mask].copy()
                positive_candidates = positive_candidates.sort_values(
                    ['gallery_priority_score', 'clinical_rescue_margin', 'pair_repair'],
                    ascending=[False, False, False],
                )

                positive_rows = []
                gene_counts = {}
                selected_variant_ids = set()
                for row in positive_candidates.to_dict(orient='records'):
                    variant_id = row['variant_id']
                    gene = str(row.get('gene') or '')
                    if variant_id in selected_variant_ids:
                        continue
                    if gene_counts.get(gene, 0) >= 2:
                        continue
                    positive_rows.append(row)
                    selected_variant_ids.add(variant_id)
                    gene_counts[gene] = gene_counts.get(gene, 0) + 1
                    if len(positive_rows) >= TOP_POSITIVE_CASES:
                        break

                if len(positive_rows) < min(3, TOP_POSITIVE_CASES):
                    fallback_candidates = final_pool.sort_values('gallery_priority_score', ascending=False)
                    for row in fallback_candidates.to_dict(orient='records'):
                        variant_id = row['variant_id']
                        gene = str(row.get('gene') or '')
                        if variant_id in selected_variant_ids:
                            continue
                        if gene_counts.get(gene, 0) >= 2:
                            continue
                        positive_rows.append(row)
                        selected_variant_ids.add(variant_id)
                        gene_counts[gene] = gene_counts.get(gene, 0) + 1
                        if len(positive_rows) >= TOP_POSITIVE_CASES:
                            break

                # Force at least one explicit cross-family anchor when available so the gallery helps close the generality objection.
                if not any(bool(row.get('has_prott5_support')) for row in positive_rows):
                    prott5_anchor = positive_candidates.loc[
                        positive_candidates['has_prott5_support'].fillna(False)
                        & ~positive_candidates['counterexample_gene'].fillna(False)
                    ].sort_values('gallery_priority_score', ascending=False).head(1)
                    if prott5_anchor.empty:
                        prott5_anchor = final_pool.loc[
                            final_pool['has_prott5_support'].fillna(False)
                            & ~final_pool['counterexample_gene'].fillna(False)
                        ].sort_values('gallery_priority_score', ascending=False).head(1)
                    if not prott5_anchor.empty:
                        replacement = prott5_anchor.iloc[0].to_dict()
                        replace_index = None
                        replace_score = float('inf')
                        for index, row in enumerate(positive_rows):
                            if bool(row.get('has_prott5_support')):
                                continue
                            score = safe_float(row.get('gallery_priority_score'), default=-999)
                            if score < replace_score:
                                replace_index = index
                                replace_score = score
                        if replace_index is not None:
                            positive_rows[replace_index] = replacement
                        elif len(positive_rows) < TOP_POSITIVE_CASES:
                            positive_rows.append(replacement)

                gallery_final = pd.DataFrame(positive_rows)
                if gallery_final.empty:
                    raise RuntimeError('No final gallery cases were selected; investigate candidate_pool filtering.')

                gallery_final['reviewer_sticky_summary'] = (
                    gallery_final['variant_id'].astype(str)
                    + ' | margin=' + gallery_final['clinical_rescue_margin'].fillna(float('nan')).map(lambda x: f'{x:.3f}' if not math.isnan(float(x)) else 'nan')
                    + ' | repair=' + gallery_final['pair_repair'].fillna(float('nan')).map(lambda x: f'{x:.3f}' if not math.isnan(float(x)) else 'nan')
                    + ' | pLDDT=' + gallery_final['site_plddt'].fillna(float('nan')).map(lambda x: f'{x:.1f}' if not math.isnan(float(x)) else 'nan')
                    + ' | contacts=' + gallery_final['site_contact_count'].fillna(float('nan')).map(lambda x: f'{x:.0f}' if not math.isnan(float(x)) else 'nan')
                )

                anti_merge = counterexamples.merge(
                    final_pool[[
                        column for column in [
                            'variant_id', 'reviewer_grip_score', 'gallery_priority_score', 'best_available_cross_model_delta',
                            'alpha_positive_fraction', 'has_strong_structure', 'has_prott5_support', 'has_alpha_stability',
                            'story_bucket', 'focus_role'
                        ] if column in final_pool.columns
                    ]],
                    on='variant_id',
                    how='left',
                )
                anti_merge['clinical_rescue_margin'] = pd.to_numeric(anti_merge.get('clinical_rescue_margin'), errors='coerce')
                anti_merge['pair_repair'] = pd.to_numeric(anti_merge.get('pair_repair'), errors='coerce')
                anti_merge['site_plddt'] = pd.to_numeric(anti_merge.get('site_plddt'), errors='coerce')
                anti_merge['site_contact_count'] = pd.to_numeric(anti_merge.get('site_contact_count'), errors='coerce')
                anti_merge['anti_case_score'] = (
                    anti_merge['clinical_rescue_margin'].fillna(0) * -1.40
                    + anti_merge['pair_repair'].fillna(0) * -0.90
                    + (anti_merge['site_plddt'].fillna(0) / 100.0) * 0.50
                    + normalize_series(anti_merge['site_contact_count']).fillna(0) * 0.40
                )
                anti_case = anti_merge.sort_values('anti_case_score', ascending=False).head(TOP_NEGATIVE_CASES).copy()
                anti_case['reviewer_sticky_summary'] = (
                    anti_case['variant_id'].astype(str)
                    + ' | margin=' + anti_case['clinical_rescue_margin'].fillna(float('nan')).map(lambda x: f'{x:.3f}' if not math.isnan(float(x)) else 'nan')
                    + ' | repair=' + anti_case['pair_repair'].fillna(float('nan')).map(lambda x: f'{x:.3f}' if not math.isnan(float(x)) else 'nan')
                    + ' | pLDDT=' + anti_case['site_plddt'].fillna(float('nan')).map(lambda x: f'{x:.1f}' if not math.isnan(float(x)) else 'nan')
                    + ' | contacts=' + anti_case['site_contact_count'].fillna(float('nan')).map(lambda x: f'{x:.0f}' if not math.isnan(float(x)) else 'nan')
                )

                gallery_final.to_csv(TABLES_DIR / 'gallery_final_cases.csv', index=False)
                anti_case.to_csv(TABLES_DIR / 'gallery_anti_case.csv', index=False)

                fig, ax = plt.subplots(figsize=(11, 7))
                background = final_pool.copy()
                ax.scatter(
                    background['clinical_rescue_margin'].fillna(0),
                    background['pair_repair'].fillna(0),
                    s=np.clip(background['site_contact_count'].fillna(3) * 18, 40, 260),
                    c=background['reviewer_grip_score'].fillna(0),
                    cmap='viridis',
                    alpha=0.28,
                    edgecolor='none',
                )
                ax.scatter(
                    gallery_final['clinical_rescue_margin'].fillna(0),
                    gallery_final['pair_repair'].fillna(0),
                    s=np.clip(gallery_final['site_contact_count'].fillna(4) * 28, 90, 420),
                    c='#d04a02',
                    edgecolor='black',
                    linewidth=0.8,
                    label='Final rescue gallery',
                )
                if not anti_case.empty:
                    ax.scatter(
                        anti_case['clinical_rescue_margin'].fillna(0),
                        anti_case['pair_repair'].fillna(0),
                        s=np.clip(anti_case['site_contact_count'].fillna(4) * 30, 110, 420),
                        c='#1f3d7a',
                        edgecolor='black',
                        linewidth=0.9,
                        marker='X',
                        label='Anti-case',
                    )
                for _, row in gallery_final.iterrows():
                    ax.annotate(
                        row['variant_id'],
                        (row['clinical_rescue_margin'], row['pair_repair']),
                        xytext=(6, 6),
                        textcoords='offset points',
                        fontsize=8,
                    )
                for _, row in anti_case.iterrows():
                    ax.annotate(
                        row['variant_id'],
                        (row['clinical_rescue_margin'], row['pair_repair']),
                        xytext=(6, -10),
                        textcoords='offset points',
                        fontsize=8,
                    )
                ax.axvline(0, color='gray', linewidth=1.0, linestyle='--', alpha=0.6)
                ax.axhline(0, color='gray', linewidth=1.0, linestyle='--', alpha=0.6)
                ax.set_xlabel('Clinical rescue margin')
                ax.set_ylabel('Pair repair vs baseline')
                ax.set_title('Reviewer-grip gallery: rescue margin vs structural repair')
                ax.legend(loc='best')
                fig.tight_layout()
                fig.savefig(FIGURES_DIR / 'gallery_margin_vs_structure.png', dpi=220, bbox_inches='tight')
                plt.close(fig)

                heatmap_rows = pd.concat([
                    gallery_final.assign(case_role='rescue'),
                    anti_case.assign(case_role='anti_case'),
                ], ignore_index=True, sort=False)
                heatmap_metrics = [
                    ('clinical_rescue_margin', 'Clinical margin'),
                    ('pair_repair', 'Pair repair'),
                    ('site_plddt', 'Site pLDDT'),
                    ('site_contact_count', 'Local contacts'),
                    ('prott5_pair_advantage', 'ProtT5 support'),
                    ('alpha_positive_fraction', 'Alpha stability'),
                    ('best_available_cross_model_delta', 'Cross-model delta'),
                    ('reviewer_grip_score', 'Grip score'),
                ]
                present_metrics = [item for item in heatmap_metrics if item[0] in heatmap_rows.columns]
                heatmap_matrix = np.vstack([
                    zscore_series(pd.to_numeric(heatmap_rows[column], errors='coerce')).fillna(0).to_numpy()
                    for column, _ in present_metrics
                ]) if present_metrics else np.zeros((1, len(heatmap_rows)))
                fig, ax = plt.subplots(figsize=(max(8, len(heatmap_rows) * 1.5), max(4.6, len(present_metrics) * 0.7)))
                im = ax.imshow(heatmap_matrix, cmap='coolwarm', aspect='auto', vmin=-2.5, vmax=2.5)
                ax.set_xticks(range(len(heatmap_rows)))
                ax.set_xticklabels(heatmap_rows['variant_id'].tolist(), rotation=40, ha='right')
                ax.set_yticks(range(len(present_metrics)))
                ax.set_yticklabels([label for _, label in present_metrics])
                ax.set_title('Final gallery evidence heatmap (z-scored across selected cases)')
                cbar = fig.colorbar(im, ax=ax, shrink=0.82)
                cbar.set_label('Z-score within selected cases')
                fig.tight_layout()
                fig.savefig(FIGURES_DIR / 'gallery_reviewer_heatmap.png', dpi=220, bbox_inches='tight')
                plt.close(fig)

                unique_positive_genes = sorted(gallery_final['gene'].dropna().astype(str).unique().tolist())
                gallery_has_cross_model_support = int((gallery_final.get('has_prott5_support', pd.Series(dtype=bool)).fillna(False)).sum())
                gallery_has_alpha_support = int((gallery_final.get('has_alpha_stability', pd.Series(dtype=bool)).fillna(False)).sum())
                gallery_has_structure_support = int((gallery_final.get('has_strong_structure', pd.Series(dtype=bool)).fillna(False)).sum())
                gallery_has_positive_margin = int((gallery_final['clinical_rescue_margin'].fillna(-999) > 0).sum())

                claim_status = 'reviewer_grip_gallery_supported'
                claim_reason = 'The gallery isolates concrete cases where covariance rescue, local structure, and at least partial cross-model/alpha support align.'
                if len(unique_positive_genes) < 3:
                    claim_status = 'bounded_reviewer_grip_gallery'
                    claim_reason = 'The gallery is still compelling, but it spans fewer than three genes.'
                if gallery_has_structure_support < max(2, min(3, len(gallery_final))):
                    claim_status = 'bounded_reviewer_grip_gallery'
                    claim_reason = 'The gallery remains useful, but fewer than the target number of finalists have strong local structure support.'

                anti_case_variant = anti_case['variant_id'].iloc[0] if not anti_case.empty else 'not_available'
                claim_paragraph = (
                    f"We distilled the previous bounded evidence into a reviewer-grip gallery with `{len(gallery_final)}` rescue cases across "
                    f"`{len(unique_positive_genes)}` genes plus anti-case `{anti_case_variant}`. The finalists are not just high-scoring by covariance: "
                    f"`{gallery_has_structure_support}` carry strong local structure support, `{gallery_has_cross_model_support}` show explicit ProtT5 agreement, "
                    f"and `{gallery_has_alpha_support}` stay positive across the alpha sweep. This makes the story concrete: SpectralBio is strongest when "
                    f"likelihood under-reacts, local geometry is contact-dense and high-confidence, and covariance rescue survives beyond a single checkpoint."
                )

                summary_payload = {
                    'notebook_slug': NOTEBOOK_SLUG,
                    'run_at_utc': RUN_AT,
                    'account_label': ACCOUNT_LABEL,
                    'claim_status': claim_status,
                    'claim_reason': claim_reason,
                    'positive_case_count': int(len(gallery_final)),
                    'positive_gene_count': int(len(unique_positive_genes)),
                    'anti_case_count': int(len(anti_case)),
                    'anti_case_variant_id': anti_case_variant,
                    'positive_cases_with_structure_support': int(gallery_has_structure_support),
                    'positive_cases_with_prott5_support': int(gallery_has_cross_model_support),
                    'positive_cases_with_alpha_support': int(gallery_has_alpha_support),
                    'positive_cases_with_positive_margin': int(gallery_has_positive_margin),
                    'selected_positive_variants': gallery_final['variant_id'].astype(str).tolist(),
                    'selected_positive_genes': unique_positive_genes,
                    'selected_anti_variants': anti_case['variant_id'].astype(str).tolist(),
                    'claim_paragraph': claim_paragraph,
                }

                (MANIFESTS_DIR / 'block7_turbo_summary.json').write_text(json.dumps(summary_payload, indent=2), encoding='utf-8')
                (MANIFESTS_DIR / 'artifact_summary.json').write_text(json.dumps(summary_payload, indent=2), encoding='utf-8')

                summary_md = '\\n'.join([
                    '# Block 7 Turbo Gallery Summary',
                    '',
                    f"- Claim status: `{claim_status}`",
                    f"- Claim reason: {claim_reason}",
                    f"- Positive rescue cases selected: `{len(gallery_final)}` across `{len(unique_positive_genes)}` genes",
                    f"- Positive cases with strong local structure: `{gallery_has_structure_support}`",
                    f"- Positive cases with explicit ProtT5 support: `{gallery_has_cross_model_support}`",
                    f"- Positive cases with alpha stability >= 0.50: `{gallery_has_alpha_support}`",
                    f"- Anti-case: `{anti_case_variant}`",
                    '',
                    '## Selected Rescue Cases',
                    '',
                    *[f"- {text}" for text in gallery_final['reviewer_sticky_summary'].astype(str).tolist()],
                    '',
                    '## Anti-Case',
                    '',
                    *([f"- {text}" for text in anti_case['reviewer_sticky_summary'].astype(str).tolist()] if not anti_case.empty else ['- No anti-case available.']),
                    '',
                    '## Claim Paragraph',
                    '',
                    claim_paragraph,
                ])
                (TEXT_DIR / 'block7_turbo_summary.md').write_text(summary_md + '\\n', encoding='utf-8')
                (TEXT_DIR / 'block7_turbo_claim_paragraph.md').write_text(claim_paragraph + '\\n', encoding='utf-8')

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
                print(summary_md)
                done('Block 7 turbo gallery bundle is ready for download.')
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
    output_path = repo_root / "New Notebooks" / "08_block7_turbo_gallery_rescues_h100.ipynb"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(notebook, indent=2), encoding="utf-8")
    print(f"Wrote notebook to {output_path}")


if __name__ == "__main__":
    main()
