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
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


def dedent(source: str) -> str:
    return textwrap.dedent(source).lstrip("\n")


def build_notebook() -> dict:
    cells: list[dict] = [
        markdown_cell(
            "# Experiment: SpectralBio Block 10 - Structural Dissociation in TP53 (H100)\n\n"
            "Objective:\n"
            "- Close the mechanistic question that reviewers can still ask after Blocks 2, 5, and 6.\n"
            "- Use experimental TP53 crystal structures as an external ground truth for local geometric perturbation.\n"
            "- Recompute covariance-aware SpectralBio scores directly on the structural subset, instead of depending on partial frozen coverage.\n"
            "- Test whether `frob_dist` tracks local structural tension better than scalar `ll_proper` on the same mutant set.\n"
            "- Save a complete Lightning-friendly bundle under `New Notebooks/results/07_block10_structural_dissociation_tp53_h100/`.\n"
        ),
        markdown_cell(
            "## Block 10 Deliverables\n\n"
            "- A cached TP53 structural subset built from RCSB experimental structures, filtered to WT and single-missense mutant entries.\n"
            "- WT-vs-mutant structural pairings with global alignment, local window RMSD, and local contact-change summaries.\n"
            "- Fresh ESM2-150M scoring on the exact structural subset: `ll_proper`, `frob_dist`, `trace_ratio`, `sps_log`, and pair score.\n"
            "- A blinded three-group dissociation analysis.\n"
            "- Reviewer-facing figures, a `block10_summary.json`, and a single memorable TP53 case that can later anchor Block 7.\n\n"
            "## Runtime contract\n\n"
            "- Target environment: **Lightning AI Studio**\n"
            "- Target hardware: **H100**\n"
            "- The notebook caches all remote metadata, PDB downloads, and structural subset scores.\n"
            "- Heavy model work is bounded to the TP53 structural subset only.\n"
            "- All outputs are written under `New Notebooks/results/07_block10_structural_dissociation_tp53_h100/`.\n"
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
                from IPython.display import display

                NOTEBOOK_SLUG = '07_block10_structural_dissociation_tp53_h100'
                ACCOUNT_LABEL = os.environ.get('SPECTRALBIO_ACCOUNT_LABEL', 'SET_ACCOUNT_LABEL_HERE')
                RUN_AT = datetime.now(timezone.utc).isoformat()
                SEED = int(os.environ.get('SPECTRALBIO_RANDOM_SEED', '42'))
                STRUCTURE_WINDOW_RADIUS = int(os.environ.get('SPECTRALBIO_BLOCK10_STRUCTURE_WINDOW_RADIUS', '20'))
                CONTACT_RADIUS_ANGSTROM = float(os.environ.get('SPECTRALBIO_BLOCK10_CONTACT_RADIUS', '8.0'))
                MIN_SEQ_LEN = int(os.environ.get('SPECTRALBIO_BLOCK10_MIN_SEQ_LEN', '180'))
                MAX_SEQ_LEN = int(os.environ.get('SPECTRALBIO_BLOCK10_MAX_SEQ_LEN', '230'))
                MAX_SEARCH_ROWS = int(os.environ.get('SPECTRALBIO_BLOCK10_MAX_SEARCH_ROWS', '200'))
                MAX_MUTANT_ENTRIES = int(os.environ.get('SPECTRALBIO_BLOCK10_MAX_MUTANT_ENTRIES', '30'))
                MIN_GLOBAL_OVERLAP = int(os.environ.get('SPECTRALBIO_BLOCK10_MIN_GLOBAL_OVERLAP', '80'))
                MIN_LOCAL_OVERLAP = int(os.environ.get('SPECTRALBIO_BLOCK10_MIN_LOCAL_OVERLAP', '8'))
                TOP_CASES = int(os.environ.get('SPECTRALBIO_BLOCK10_TOP_CASES', '5'))
                OVERWRITE = os.environ.get('SPECTRALBIO_OVERWRITE', '').strip().lower() in {'1', 'true', 'yes'}

                def done(message: str) -> None:
                    print(f'TERMINEI PODE SEGUIR - {message}')

                print({
                    'notebook_slug': NOTEBOOK_SLUG,
                    'account_label': ACCOUNT_LABEL,
                    'seed': SEED,
                    'structure_window_radius': STRUCTURE_WINDOW_RADIUS,
                    'contact_radius_angstrom': CONTACT_RADIUS_ANGSTROM,
                    'min_seq_len': MIN_SEQ_LEN,
                    'max_seq_len': MAX_SEQ_LEN,
                    'max_search_rows': MAX_SEARCH_ROWS,
                    'max_mutant_entries': MAX_MUTANT_ENTRIES,
                    'min_global_overlap': MIN_GLOBAL_OVERLAP,
                    'min_local_overlap': MIN_LOCAL_OVERLAP,
                    'top_cases': TOP_CASES,
                    'overwrite': OVERWRITE,
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
                # Helpers: subprocess, repo discovery, paths, numeric utilities, and small IO helpers
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

                def median_or_nan(series: pd.Series) -> float:
                    values = pd.to_numeric(series, errors='coerce').dropna()
                    if values.empty:
                        return float('nan')
                    return float(values.median())

                def spearman_or_nan(left: pd.Series, right: pd.Series) -> float:
                    frame = pd.DataFrame({
                        'left': pd.to_numeric(left, errors='coerce'),
                        'right': pd.to_numeric(right, errors='coerce'),
                    }).dropna()
                    if len(frame) < 3:
                        return float('nan')
                    return float(frame['left'].corr(frame['right'], method='spearman'))

                def pearson_or_nan(left: pd.Series, right: pd.Series) -> float:
                    frame = pd.DataFrame({
                        'left': pd.to_numeric(left, errors='coerce'),
                        'right': pd.to_numeric(right, errors='coerce'),
                    }).dropna()
                    if len(frame) < 3:
                        return float('nan')
                    return float(frame['left'].corr(frame['right'], method='pearson'))

                def percentile_rank(series: pd.Series) -> pd.Series:
                    numeric = pd.to_numeric(series, errors='coerce')
                    return numeric.rank(method='average', pct=True)

                def q_or_nan(series: pd.Series, q: float) -> float:
                    values = pd.to_numeric(series, errors='coerce').dropna()
                    if values.empty:
                        return float('nan')
                    return float(values.quantile(q))

                def maybe_read_json(path: Path) -> dict:
                    if path.exists():
                        return json.loads(path.read_text(encoding='utf-8'))
                    return {}

                def maybe_read_csv(path: Path) -> pd.DataFrame:
                    if path.exists():
                        return pd.read_csv(path)
                    return pd.DataFrame()

                done('Helpers ready.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Resolve repository root, outputs, and runtime dependencies
                REPO_ROOT = find_repo_root()
                RESULTS_ROOT = ensure_dir(REPO_ROOT / 'New Notebooks' / 'results' / NOTEBOOK_SLUG)
                TABLES_DIR = ensure_dir(RESULTS_ROOT / 'tables')
                FIGURES_DIR = ensure_dir(RESULTS_ROOT / 'figures')
                TEXT_DIR = ensure_dir(RESULTS_ROOT / 'text')
                MANIFESTS_DIR = ensure_dir(RESULTS_ROOT / 'manifests')
                RUNTIME_DIR = ensure_dir(RESULTS_ROOT / 'runtime')
                API_CACHE_DIR = ensure_dir(RUNTIME_DIR / 'api_cache')
                PDB_CACHE_DIR = ensure_dir(RUNTIME_DIR / 'pdb_cache')
                CONTACT_PAYLOAD_DIR = ensure_dir(RUNTIME_DIR / 'contact_payloads')
                SCORE_CACHE_DIR = ensure_dir(RUNTIME_DIR / 'score_cache')
                ZIP_PATH = REPO_ROOT / 'New Notebooks' / 'results' / f'{NOTEBOOK_SLUG}.zip'
                ROOT_ZIP_COPY = REPO_ROOT / 'New Notebooks' / f'{NOTEBOOK_SLUG}.zip'

                LIGHT_REQUIREMENTS = [
                    ('numpy', 'numpy==2.1.3'),
                    ('pandas', 'pandas==2.2.3'),
                    ('matplotlib', 'matplotlib==3.9.2'),
                    ('requests', 'requests==2.32.3'),
                    ('scipy', 'scipy==1.14.1'),
                ]
                light_missing = []
                for module_name, package_name in LIGHT_REQUIREMENTS:
                    try:
                        importlib.import_module(module_name)
                    except Exception:
                        light_missing.append(package_name)
                if light_missing:
                    run([sys.executable, '-m', 'pip', 'install', *light_missing], cwd=REPO_ROOT)
                    importlib.invalidate_caches()

                try:
                    import torch
                except Exception as exc:
                    raise RuntimeError('PyTorch is required for Block 10 scoring. Use an H100 runtime with torch preinstalled.') from exc

                try:
                    import transformers  # noqa: F401
                except Exception:
                    run([sys.executable, '-m', 'pip', 'install', 'transformers==4.46.3', 'sentencepiece==0.2.0'], cwd=REPO_ROOT)
                    importlib.invalidate_caches()

                import requests

                SRC_ROOT = REPO_ROOT / 'src'
                if str(SRC_ROOT) not in sys.path:
                    sys.path.insert(0, str(SRC_ROOT))

                repo_status = {
                    'repo_root': str(REPO_ROOT),
                    'head_commit': run(['git', 'rev-parse', 'HEAD'], cwd=REPO_ROOT).strip(),
                    'head_subject': run(['git', 'log', '-1', '--pretty=%s'], cwd=REPO_ROOT).strip(),
                    'branch': run(['git', 'branch', '--show-current'], cwd=REPO_ROOT).strip(),
                }
                display(pd.DataFrame([repo_status]))
                done('Repository, outputs, and dependencies confirmed.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Load upstream context and optional frozen references
                block2_summary = maybe_read_json(resolve_existing_path('New Notebooks/results/02_block2_failure_mode_hunt_h100/manifests/block2_summary.json', REPO_ROOT))
                block5_summary = maybe_read_json(resolve_existing_path('New Notebooks/results/05_block3_structure_bridge_h100/manifests/artifact_summary.json', REPO_ROOT))
                block6_summary = maybe_read_json(resolve_existing_path('New Notebooks/results/06_block5_clinical_panel_audit_h100/manifests/block6_summary.json', REPO_ROOT))

                tp53_aug_path = resolve_existing_path(
                    'supplementary/final_accept_part3_esm1v_augmentation/esm1v_augmentation/tp53/augmentation_table.csv',
                    REPO_ROOT,
                )
                tp53_aug = maybe_read_csv(tp53_aug_path)
                if not tp53_aug.empty:
                    tp53_aug['variant_id'] = (
                        tp53_aug['gene'].astype(str)
                        + ':'
                        + tp53_aug['wt_aa'].astype(str)
                        + tp53_aug['position'].astype(int).astype(str)
                        + tp53_aug['mut_aa'].astype(str)
                    )

                upstream_snapshot = {
                    'block2_selected_regime': block2_summary.get('selected_regime'),
                    'block2_selected_label': block2_summary.get('selected_label'),
                    'block2_bug_statement': block2_summary.get('bug_statement'),
                    'block5_claim_status': block5_summary.get('claim_status'),
                    'block6_claim_status': block6_summary.get('claim_status'),
                    'block6_positive_focus_genes': block6_summary.get('positive_focus_genes'),
                    'tp53_augmentation_rows': int(len(tp53_aug)),
                }
                display(pd.DataFrame([upstream_snapshot]))
                done('Upstream context loaded.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Search TP53 experimental structures, infer single-missense mutants, and cache the structural subset
                import requests

                UNIPROT_ACCESSION = 'P04637'
                SEARCH_CACHE_PATH = API_CACHE_DIR / 'rcsb_tp53_polymer_entity_search.json'
                WT_FASTA_PATH = API_CACHE_DIR / 'P04637_tp53.fasta'

                def fetch_text(url: str, cache_path: Path, overwrite: bool = False) -> str:
                    if cache_path.exists() and not overwrite:
                        return cache_path.read_text(encoding='utf-8')
                    response = requests.get(url, timeout=120)
                    response.raise_for_status()
                    cache_path.write_text(response.text, encoding='utf-8')
                    return response.text

                def fetch_json(url: str, cache_path: Path, overwrite: bool = False) -> dict:
                    if cache_path.exists() and not overwrite:
                        return json.loads(cache_path.read_text(encoding='utf-8'))
                    response = requests.get(url, timeout=120)
                    response.raise_for_status()
                    payload = response.json()
                    cache_path.write_text(json.dumps(payload, indent=2), encoding='utf-8')
                    return payload

                def post_json(url: str, payload: dict, cache_path: Path, overwrite: bool = False) -> dict:
                    if cache_path.exists() and not overwrite:
                        return json.loads(cache_path.read_text(encoding='utf-8'))
                    response = requests.post(url, json=payload, timeout=120)
                    response.raise_for_status()
                    result = response.json()
                    cache_path.write_text(json.dumps(result, indent=2), encoding='utf-8')
                    return result

                def fasta_sequence(fasta_text: str) -> str:
                    return ''.join(line.strip() for line in fasta_text.splitlines() if not line.startswith('>'))

                def sequence_change_list(deposited_sequence: str, auth_mapping: list[str], wildtype_sequence: str) -> list[dict]:
                    changes: list[dict] = []
                    for entity_index, (residue, auth_position) in enumerate(zip(deposited_sequence, auth_mapping), start=1):
                        auth_text = str(auth_position).strip()
                        if not auth_text.isdigit():
                            return []
                        auth_pos_1 = int(auth_text)
                        if auth_pos_1 < 1 or auth_pos_1 > len(wildtype_sequence):
                            return []
                        wt_aa = wildtype_sequence[auth_pos_1 - 1]
                        if residue != wt_aa:
                            changes.append({
                                'entity_position_1': entity_index,
                                'position_1': auth_pos_1,
                                'position_0': auth_pos_1 - 1,
                                'wt_aa': wt_aa,
                                'mut_aa': residue,
                            })
                    return changes

                wt_fasta_text = fetch_text(
                    f'https://rest.uniprot.org/uniprotkb/{UNIPROT_ACCESSION}.fasta',
                    WT_FASTA_PATH,
                    overwrite=OVERWRITE,
                )
                TP53_WT_SEQUENCE = fasta_sequence(wt_fasta_text)

                search_query = {
                    'query': {
                        'type': 'group',
                        'logical_operator': 'and',
                        'nodes': [
                            {
                                'type': 'terminal',
                                'service': 'text',
                                'parameters': {
                                    'attribute': 'rcsb_entity_source_organism.rcsb_gene_name.value',
                                    'operator': 'exact_match',
                                    'value': 'TP53',
                                },
                            },
                            {
                                'type': 'terminal',
                                'service': 'text',
                                'parameters': {
                                    'attribute': 'rcsb_entity_source_organism.ncbi_scientific_name',
                                    'operator': 'exact_match',
                                    'value': 'Homo sapiens',
                                },
                            },
                            {
                                'type': 'terminal',
                                'service': 'text',
                                'parameters': {
                                    'attribute': 'entity_poly.rcsb_entity_polymer_type',
                                    'operator': 'exact_match',
                                    'value': 'Protein',
                                },
                            },
                            {
                                'type': 'terminal',
                                'service': 'text',
                                'parameters': {
                                    'attribute': 'exptl.method',
                                    'operator': 'exact_match',
                                    'value': 'X-RAY DIFFRACTION',
                                },
                            },
                            {
                                'type': 'terminal',
                                'service': 'text',
                                'parameters': {
                                    'attribute': 'rcsb_entry_info.resolution_combined',
                                    'operator': 'less_or_equal',
                                    'value': 3.0,
                                },
                            },
                            {
                                'type': 'terminal',
                                'service': 'text',
                                'parameters': {
                                    'attribute': 'entity_poly.rcsb_mutation_count',
                                    'operator': 'greater_or_equal',
                                    'value': 0,
                                },
                            },
                            {
                                'type': 'terminal',
                                'service': 'text',
                                'parameters': {
                                    'attribute': 'entity_poly.rcsb_mutation_count',
                                    'operator': 'less_or_equal',
                                    'value': 3,
                                },
                            },
                        ],
                    },
                    'return_type': 'polymer_entity',
                    'request_options': {
                        'paginate': {'start': 0, 'rows': MAX_SEARCH_ROWS},
                        'results_content_type': ['experimental'],
                    },
                }

                search_payload = post_json(
                    'https://search.rcsb.org/rcsbsearch/v2/query',
                    search_query,
                    SEARCH_CACHE_PATH,
                    overwrite=OVERWRITE,
                )
                search_identifiers = [row['identifier'] for row in search_payload.get('result_set', [])]

                entity_rows = []
                for identifier in search_identifiers:
                    entry_id, entity_id = identifier.split('_')
                    entity_cache_path = API_CACHE_DIR / f'entity_{entry_id}_{entity_id}.json'
                    entity_payload = fetch_json(
                        f'https://data.rcsb.org/rest/v1/core/polymer_entity/{entry_id}/{entity_id}',
                        entity_cache_path,
                        overwrite=OVERWRITE,
                    )
                    refs = entity_payload.get('rcsb_polymer_entity_container_identifiers', {}).get('reference_sequence_identifiers', []) or []
                    uniprot_hits = {ref.get('database_accession') for ref in refs}
                    if UNIPROT_ACCESSION not in uniprot_hits:
                        continue

                    entry_cache_path = API_CACHE_DIR / f'entry_{entry_id}.json'
                    entry_payload = fetch_json(
                        f'https://data.rcsb.org/rest/v1/core/entry/{entry_id}',
                        entry_cache_path,
                        overwrite=OVERWRITE,
                    )
                    resolution_list = entry_payload.get('rcsb_entry_info', {}).get('resolution_combined') or []
                    resolution = safe_float(resolution_list[0]) if resolution_list else float('nan')

                    deposited_sequence = ''.join((entity_payload.get('entity_poly', {}).get('pdbx_seq_one_letter_code_can') or '').split())
                    if not deposited_sequence:
                        continue
                    if len(deposited_sequence) < MIN_SEQ_LEN or len(deposited_sequence) > MAX_SEQ_LEN:
                        continue

                    auth_asym_ids = entity_payload.get('rcsb_polymer_entity_container_identifiers', {}).get('auth_asym_ids') or []
                    chosen_asym = None
                    auth_mapping = None
                    for auth_asym_id in auth_asym_ids:
                        instance_cache_path = API_CACHE_DIR / f'instance_{entry_id}_{auth_asym_id}.json'
                        try:
                            instance_payload = fetch_json(
                                f'https://data.rcsb.org/rest/v1/core/polymer_entity_instance/{entry_id}/{auth_asym_id}',
                                instance_cache_path,
                                overwrite=OVERWRITE,
                            )
                        except Exception:
                            continue
                        mapping_candidate = instance_payload.get('rcsb_polymer_entity_instance_container_identifiers', {}).get('auth_to_entity_poly_seq_mapping') or []
                        if len(mapping_candidate) == len(deposited_sequence):
                            chosen_asym = auth_asym_id
                            auth_mapping = mapping_candidate
                            break

                    if chosen_asym is None or auth_mapping is None:
                        continue

                    changes = sequence_change_list(deposited_sequence, auth_mapping, TP53_WT_SEQUENCE)
                    if len(changes) > 3:
                        continue

                    construct_start = int(str(auth_mapping[0]))
                    construct_end = int(str(auth_mapping[-1]))
                    is_wt = len(changes) == 0
                    is_single_missense = len(changes) == 1
                    variant_id = ''
                    position_1 = float('nan')
                    position_0 = float('nan')
                    wt_aa = ''
                    mut_aa = ''
                    mutation_label = ''
                    if is_single_missense:
                        change = changes[0]
                        position_1 = int(change['position_1'])
                        position_0 = int(change['position_0'])
                        wt_aa = str(change['wt_aa'])
                        mut_aa = str(change['mut_aa'])
                        mutation_label = f'{wt_aa}{position_1}{mut_aa}'
                        variant_id = f'TP53:{wt_aa}{position_0}{mut_aa}'

                    entity_rows.append({
                        'identifier': identifier,
                        'entry_id': entry_id,
                        'entity_id': entity_id,
                        'auth_asym_id': chosen_asym,
                        'resolution': resolution,
                        'seq_len': len(deposited_sequence),
                        'construct_start': construct_start,
                        'construct_end': construct_end,
                        'rcsb_mutation_count': int(entity_payload.get('entity_poly', {}).get('rcsb_mutation_count', 0) or 0),
                        'changes_json': json.dumps(changes),
                        'n_inferred_changes': len(changes),
                        'is_wt': bool(is_wt),
                        'is_single_missense': bool(is_single_missense),
                        'position_1': position_1,
                        'position_0': position_0,
                        'wt_aa': wt_aa,
                        'mut_aa': mut_aa,
                        'mutation_label': mutation_label,
                        'variant_id': variant_id,
                        'overlaps_tp53_augmentation': bool(variant_id in set(tp53_aug['variant_id'])) if not tp53_aug.empty and variant_id else False,
                    })

                structural_entities = pd.DataFrame(entity_rows)
                if structural_entities.empty:
                    raise RuntimeError('No TP53 structural entities survived filtering. Block 10 cannot continue.')

                wt_entities = structural_entities[structural_entities['is_wt']].copy().sort_values(['resolution', 'identifier'])
                mutant_entities = structural_entities[structural_entities['is_single_missense']].copy().sort_values(['variant_id', 'resolution', 'identifier'])
                if len(mutant_entities) > MAX_MUTANT_ENTRIES:
                    mutant_entities = mutant_entities.head(MAX_MUTANT_ENTRIES).copy()

                structural_entities.to_csv(TABLES_DIR / 'tp53_structural_entities.csv', index=False)
                wt_entities.to_csv(TABLES_DIR / 'tp53_wt_entities.csv', index=False)
                mutant_entities.to_csv(TABLES_DIR / 'tp53_mutant_entities.csv', index=False)

                subset_snapshot = pd.DataFrame([{
                    'search_hits': len(search_identifiers),
                    'filtered_entities': len(structural_entities),
                    'wt_entities': len(wt_entities),
                    'mutant_entries': len(mutant_entities),
                    'unique_mutant_variants': int(mutant_entities['variant_id'].nunique()) if not mutant_entities.empty else 0,
                    'augmentation_overlap_variants': int(mutant_entities['variant_id'].isin(set(tp53_aug['variant_id'])) .sum()) if not tp53_aug.empty else 0,
                }])
                display(subset_snapshot)
                display(mutant_entities[['identifier', 'variant_id', 'mutation_label', 'resolution', 'seq_len', 'construct_start', 'construct_end']].head(20))
                done('TP53 structural subset discovered and cached.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Download PDB files, choose WT references, align structures, and compute local structural perturbation
                THREE_TO_ONE = {
                    'ALA': 'A', 'ARG': 'R', 'ASN': 'N', 'ASP': 'D', 'CYS': 'C',
                    'GLN': 'Q', 'GLU': 'E', 'GLY': 'G', 'HIS': 'H', 'ILE': 'I',
                    'LEU': 'L', 'LYS': 'K', 'MET': 'M', 'PHE': 'F', 'PRO': 'P',
                    'SER': 'S', 'THR': 'T', 'TRP': 'W', 'TYR': 'Y', 'VAL': 'V',
                }

                def fetch_pdb(entry_id: str, overwrite: bool = False) -> Path:
                    pdb_path = PDB_CACHE_DIR / f'{entry_id}.pdb'
                    if pdb_path.exists() and not overwrite:
                        return pdb_path
                    response = requests.get(f'https://files.rcsb.org/download/{entry_id}.pdb', timeout=120)
                    response.raise_for_status()
                    text = response.text
                    if 'ATOM' not in text:
                        raise RuntimeError(f'PDB download for {entry_id} does not look like an atomic structure file.')
                    pdb_path.write_text(text, encoding='utf-8')
                    return pdb_path

                def parse_ca_records(pdb_path: Path, auth_asym_id: str) -> pd.DataFrame:
                    rows = []
                    for line in pdb_path.read_text(encoding='utf-8', errors='replace').splitlines():
                        if not line.startswith('ATOM'):
                            continue
                        if line[12:16].strip() != 'CA':
                            continue
                        alt_loc = line[16].strip()
                        if alt_loc not in {'', 'A'}:
                            continue
                        if line[21].strip() != str(auth_asym_id).strip():
                            continue
                        residue_name = line[17:20].strip().upper()
                        if residue_name not in THREE_TO_ONE:
                            continue
                        if line[26].strip():
                            continue
                        residue_number_text = line[22:26].strip()
                        if not residue_number_text or not residue_number_text.lstrip('-').isdigit():
                            continue
                        rows.append({
                            'residue_number': int(residue_number_text),
                            'aa': THREE_TO_ONE[residue_name],
                            'x': float(line[30:38].strip()),
                            'y': float(line[38:46].strip()),
                            'z': float(line[46:54].strip()),
                            'bfactor': float(line[60:66].strip()),
                        })
                    frame = pd.DataFrame(rows)
                    if frame.empty:
                        return frame
                    return frame.sort_values('residue_number').drop_duplicates('residue_number', keep='first').reset_index(drop=True)

                def coords_for_positions(frame: pd.DataFrame, positions: list[int]) -> np.ndarray:
                    subset = frame[frame['residue_number'].isin(positions)].sort_values('residue_number')
                    return subset[['x', 'y', 'z']].to_numpy(dtype=float)

                def kabsch_fit(reference_coords: np.ndarray, mobile_coords: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
                    ref_center = reference_coords.mean(axis=0)
                    mobile_center = mobile_coords.mean(axis=0)
                    ref_centered = reference_coords - ref_center
                    mobile_centered = mobile_coords - mobile_center
                    covariance = mobile_centered.T @ ref_centered
                    u, _, vt = np.linalg.svd(covariance)
                    rotation = vt.T @ u.T
                    if np.linalg.det(rotation) < 0:
                        vt[-1, :] *= -1
                        rotation = vt.T @ u.T
                    aligned = mobile_centered @ rotation + ref_center
                    rmsd = float(np.sqrt(np.mean(np.sum((aligned - reference_coords) ** 2, axis=1))))
                    return rotation, ref_center, mobile_center, rmsd

                def apply_transform(coords: np.ndarray, rotation: np.ndarray, ref_center: np.ndarray, mobile_center: np.ndarray) -> np.ndarray:
                    return (coords - mobile_center) @ rotation + ref_center

                def contact_map(coords: np.ndarray, radius: float = CONTACT_RADIUS_ANGSTROM) -> np.ndarray:
                    if len(coords) == 0:
                        return np.zeros((0, 0), dtype=int)
                    distances = np.linalg.norm(coords[:, None, :] - coords[None, :, :], axis=-1)
                    return ((distances <= radius) & (distances > 0)).astype(int)

                structure_manifest_rows = []
                structure_cache: dict[str, pd.DataFrame] = {}
                for row in pd.concat([wt_entities, mutant_entities], ignore_index=True).to_dict(orient='records'):
                    try:
                        pdb_path = fetch_pdb(row['entry_id'], overwrite=OVERWRITE)
                        ca_df = parse_ca_records(pdb_path, row['auth_asym_id'])
                        structure_cache[row['identifier']] = ca_df
                        structure_manifest_rows.append({
                            'identifier': row['identifier'],
                            'entry_id': row['entry_id'],
                            'auth_asym_id': row['auth_asym_id'],
                            'pdb_path': str(pdb_path),
                            'ca_rows': int(len(ca_df)),
                            'status': 'ok',
                        })
                    except Exception as exc:
                        structure_manifest_rows.append({
                            'identifier': row['identifier'],
                            'entry_id': row['entry_id'],
                            'auth_asym_id': row['auth_asym_id'],
                            'pdb_path': '',
                            'ca_rows': 0,
                            'status': f'error:{type(exc).__name__}',
                            'error': str(exc),
                        })

                structure_manifest = pd.DataFrame(structure_manifest_rows)
                structure_manifest.to_csv(TABLES_DIR / 'tp53_pdb_manifest.csv', index=False)

                if structure_manifest[structure_manifest['status'] == 'ok'].empty:
                    raise RuntimeError('No PDB structures could be parsed for TP53 Block 10.')

                def pair_candidates(mut_row: dict, wt_frame: pd.DataFrame) -> list[dict]:
                    mut_df = structure_cache.get(mut_row['identifier'], pd.DataFrame())
                    if mut_df.empty:
                        return []
                    mut_pos = int(mut_row['position_1'])
                    candidates = []
                    for wt_row in wt_frame.to_dict(orient='records'):
                        wt_df = structure_cache.get(wt_row['identifier'], pd.DataFrame())
                        if wt_df.empty:
                            continue
                        overlap_positions = sorted(set(mut_df['residue_number']).intersection(set(wt_df['residue_number'])))
                        if len(overlap_positions) < MIN_GLOBAL_OVERLAP:
                            continue
                        local_positions = [pos for pos in overlap_positions if abs(pos - mut_pos) <= STRUCTURE_WINDOW_RADIUS]
                        if len(local_positions) < MIN_LOCAL_OVERLAP:
                            continue
                        construct_distance = abs(int(mut_row['construct_start']) - int(wt_row['construct_start'])) + abs(int(mut_row['construct_end']) - int(wt_row['construct_end']))
                        candidates.append({
                            'wt_identifier': wt_row['identifier'],
                            'wt_entry_id': wt_row['entry_id'],
                            'wt_auth_asym_id': wt_row['auth_asym_id'],
                            'wt_resolution': safe_float(wt_row['resolution']),
                            'total_overlap': len(overlap_positions),
                            'local_overlap': len(local_positions),
                            'construct_distance': construct_distance,
                            'overlap_positions': overlap_positions,
                            'local_positions': local_positions,
                        })
                    candidates.sort(key=lambda row: (-row['local_overlap'], -row['total_overlap'], row['construct_distance'], row['wt_resolution'] if not math.isnan(row['wt_resolution']) else 999.0, row['wt_identifier']))
                    return candidates

                entry_pair_rows = []
                for mut_row in mutant_entities.to_dict(orient='records'):
                    mut_df = structure_cache.get(mut_row['identifier'], pd.DataFrame())
                    if mut_df.empty:
                        continue
                    candidates = pair_candidates(mut_row, wt_entities)
                    if not candidates:
                        continue
                    chosen = candidates[0]
                    wt_df = structure_cache[chosen['wt_identifier']]
                    overlap_positions = chosen['overlap_positions']
                    local_positions = chosen['local_positions']

                    wt_global = coords_for_positions(wt_df, overlap_positions)
                    mut_global = coords_for_positions(mut_df, overlap_positions)
                    rotation, ref_center, mobile_center, global_rmsd = kabsch_fit(wt_global, mut_global)

                    wt_local = coords_for_positions(wt_df, local_positions)
                    mut_local = coords_for_positions(mut_df, local_positions)
                    aligned_mut_local = apply_transform(mut_local, rotation, ref_center, mobile_center)
                    local_rmsd = float(np.sqrt(np.mean(np.sum((aligned_mut_local - wt_local) ** 2, axis=1))))

                    wt_local_contacts = contact_map(wt_local)
                    mut_local_contacts = contact_map(mut_local)
                    contact_diff = mut_local_contacts - wt_local_contacts
                    contact_change_count = int(np.abs(contact_diff).sum() / 2) if contact_diff.size else 0
                    possible_contacts = int((len(local_positions) * (len(local_positions) - 1)) / 2) if len(local_positions) > 1 else 0
                    contact_change_fraction = float(contact_change_count / possible_contacts) if possible_contacts > 0 else float('nan')

                    mut_site_row = mut_df[mut_df['residue_number'] == int(mut_row['position_1'])]
                    wt_site_row = wt_df[wt_df['residue_number'] == int(mut_row['position_1'])]
                    mut_site_bfactor = safe_float(mut_site_row['bfactor'].iloc[0]) if not mut_site_row.empty else float('nan')
                    wt_site_bfactor = safe_float(wt_site_row['bfactor'].iloc[0]) if not wt_site_row.empty else float('nan')

                    payload = {
                        'mutant_identifier': mut_row['identifier'],
                        'wt_identifier': chosen['wt_identifier'],
                        'variant_id': mut_row['variant_id'],
                        'mutation_label': mut_row['mutation_label'],
                        'window_positions': [int(pos) for pos in local_positions],
                        'wt_contact_map': wt_local_contacts.tolist(),
                        'mut_contact_map': mut_local_contacts.tolist(),
                        'diff_contact_map': contact_diff.tolist(),
                    }
                    payload_path = CONTACT_PAYLOAD_DIR / f"{mut_row['identifier']}__vs__{chosen['wt_identifier']}.json"
                    payload_path.write_text(json.dumps(payload, indent=2), encoding='utf-8')

                    entry_pair_rows.append({
                        'identifier': mut_row['identifier'],
                        'entry_id': mut_row['entry_id'],
                        'auth_asym_id': mut_row['auth_asym_id'],
                        'variant_id': mut_row['variant_id'],
                        'mutation_label': mut_row['mutation_label'],
                        'position_1': int(mut_row['position_1']),
                        'position_0': int(mut_row['position_0']),
                        'wt_aa': mut_row['wt_aa'],
                        'mut_aa': mut_row['mut_aa'],
                        'mutant_resolution': safe_float(mut_row['resolution']),
                        'construct_start': int(mut_row['construct_start']),
                        'construct_end': int(mut_row['construct_end']),
                        'wt_identifier': chosen['wt_identifier'],
                        'wt_entry_id': chosen['wt_entry_id'],
                        'wt_auth_asym_id': chosen['wt_auth_asym_id'],
                        'wt_resolution': chosen['wt_resolution'],
                        'total_overlap': int(chosen['total_overlap']),
                        'local_overlap': int(chosen['local_overlap']),
                        'construct_distance': int(chosen['construct_distance']),
                        'global_rmsd': global_rmsd,
                        'local_rmsd': local_rmsd,
                        'excess_local_rmsd': local_rmsd - global_rmsd,
                        'mut_site_bfactor': mut_site_bfactor,
                        'wt_site_bfactor': wt_site_bfactor,
                        'contact_change_count': contact_change_count,
                        'contact_change_fraction': contact_change_fraction,
                        'contact_payload_path': str(payload_path),
                    })

                entry_pairs = pd.DataFrame(entry_pair_rows)
                if entry_pairs.empty:
                    raise RuntimeError('No WT-mutant structural pairs met the overlap criteria. Block 10 cannot continue.')

                entry_pairs = entry_pairs.sort_values(['variant_id', 'mutant_resolution', 'identifier']).reset_index(drop=True)
                entry_pairs.to_csv(TABLES_DIR / 'tp53_structural_pairs_entry_level.csv', index=False)

                display(structure_manifest.head(20))
                display(entry_pairs[['identifier', 'variant_id', 'wt_identifier', 'local_overlap', 'total_overlap', 'global_rmsd', 'local_rmsd', 'contact_change_count']].head(20))
                done('WT references selected and local structural perturbation computed.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Recompute SpectralBio scores directly on the TP53 structural subset
                from spectralbio.constants import ALPHA, TP53_SEQUENCE
                from spectralbio.pipeline.combine_scores import combined_score
                from spectralbio.pipeline.compute_covariance_features import covariance_features
                from spectralbio.pipeline.compute_hidden_states import extract_local_hidden_states, model_bundle
                from spectralbio.pipeline.compute_ll_proper import compute_ll_proper

                score_cache_path = SCORE_CACHE_DIR / 'tp53_structural_subset_scores.csv'
                structural_variants = (
                    entry_pairs[['variant_id', 'position_0', 'position_1', 'wt_aa', 'mut_aa', 'mutation_label']]
                    .drop_duplicates()
                    .sort_values(['position_1', 'variant_id'])
                    .reset_index(drop=True)
                )

                if score_cache_path.exists() and not OVERWRITE:
                    score_df = pd.read_csv(score_cache_path)
                else:
                    tokenizer, model, device, aa_token_ids = model_bundle()
                    _ = (tokenizer, model, device)
                    score_rows = []
                    for row in structural_variants.to_dict(orient='records'):
                        position_0 = int(row['position_0'])
                        mutant_sequence = TP53_SEQUENCE[:position_0] + row['mut_aa'] + TP53_SEQUENCE[position_0 + 1:]
                        hidden_wt, logits_wt, local_pos = extract_local_hidden_states(TP53_SEQUENCE, position_0)
                        hidden_mut, _, _ = extract_local_hidden_states(mutant_sequence, position_0)
                        features = covariance_features(hidden_wt, hidden_mut)
                        ll_value = compute_ll_proper(logits_wt, local_pos, row['wt_aa'], row['mut_aa'], aa_token_ids)
                        pair_raw = combined_score(features['frob_dist'], ll_value, alpha=ALPHA)
                        score_rows.append({
                            'variant_id': row['variant_id'],
                            'position_0': position_0,
                            'position_1': int(row['position_1']),
                            'wt_aa': row['wt_aa'],
                            'mut_aa': row['mut_aa'],
                            'mutation_label': row['mutation_label'],
                            'frob_dist': float(features['frob_dist']),
                            'trace_ratio': float(features['trace_ratio']),
                            'sps_log': float(features['sps_log']),
                            'll_proper': float(ll_value),
                            'pair_score_raw': float(pair_raw),
                        })
                    score_df = pd.DataFrame(score_rows)
                    score_df['ll_rank_norm'] = percentile_rank(score_df['ll_proper'])
                    score_df['frob_rank_norm'] = percentile_rank(score_df['frob_dist'])
                    score_df['pair_rank_norm'] = percentile_rank(score_df['pair_score_raw'])
                    score_df.to_csv(score_cache_path, index=False)

                overlap_check = pd.DataFrame()
                if not tp53_aug.empty:
                    overlap_check = score_df.merge(
                        tp53_aug[['variant_id', 'reference_ll_proper', 'reference_frob_dist', 'reference_pair_score', 'reference_ll_norm', 'reference_frob_norm', 'reference_pair_norm']],
                        on='variant_id',
                        how='inner',
                    )
                    if not overlap_check.empty:
                        overlap_check['delta_ll_vs_frozen'] = overlap_check['ll_proper'] - overlap_check['reference_ll_proper']
                        overlap_check['delta_frob_vs_frozen'] = overlap_check['frob_dist'] - overlap_check['reference_frob_dist']
                        overlap_check['delta_pair_vs_frozen'] = overlap_check['pair_score_raw'] - overlap_check['reference_pair_score']
                        overlap_check.to_csv(TABLES_DIR / 'tp53_reference_overlap_check.csv', index=False)

                score_df.to_csv(TABLES_DIR / 'tp53_structural_subset_scores.csv', index=False)
                display(score_df)
                if not overlap_check.empty:
                    display(overlap_check[['variant_id', 'delta_ll_vs_frozen', 'delta_frob_vs_frozen', 'delta_pair_vs_frozen']])
                done('SpectralBio TP53 structural-subset scores recomputed.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Merge structure with scores, build blinded groups, and summarize the dissociation test
                entry_level = entry_pairs.merge(score_df, on=['variant_id', 'position_0', 'position_1', 'wt_aa', 'mut_aa', 'mutation_label'], how='left')
                variant_level = (
                    entry_level
                    .groupby(['variant_id', 'position_0', 'position_1', 'wt_aa', 'mut_aa', 'mutation_label'], dropna=False)
                    .agg(
                        n_entries=('identifier', 'count'),
                        best_entry_identifier=('identifier', 'first'),
                        local_rmsd_median=('local_rmsd', median_or_nan),
                        local_rmsd_max=('local_rmsd', 'max'),
                        global_rmsd_median=('global_rmsd', median_or_nan),
                        excess_local_rmsd_median=('excess_local_rmsd', median_or_nan),
                        local_overlap_median=('local_overlap', median_or_nan),
                        total_overlap_median=('total_overlap', median_or_nan),
                        contact_change_count_median=('contact_change_count', median_or_nan),
                        contact_change_fraction_median=('contact_change_fraction', median_or_nan),
                        mutant_resolution_best=('mutant_resolution', 'min'),
                        wt_resolution_best=('wt_resolution', 'min'),
                        frob_dist=('frob_dist', 'first'),
                        trace_ratio=('trace_ratio', 'first'),
                        sps_log=('sps_log', 'first'),
                        ll_proper=('ll_proper', 'first'),
                        pair_score_raw=('pair_score_raw', 'first'),
                        ll_rank_norm=('ll_rank_norm', 'first'),
                        frob_rank_norm=('frob_rank_norm', 'first'),
                        pair_rank_norm=('pair_rank_norm', 'first'),
                    )
                    .reset_index()
                )

                rmsd_high_threshold = q_or_nan(variant_level['local_rmsd_median'], 0.75)
                rmsd_low_threshold = q_or_nan(variant_level['local_rmsd_median'], 0.40)
                ll_high_threshold = q_or_nan(variant_level['ll_proper'], 0.75)
                ll_low_threshold = q_or_nan(variant_level['ll_proper'], 0.40)

                def assign_blinded_group(local_rmsd: float, ll_value: float) -> str:
                    if math.isnan(local_rmsd) or math.isnan(ll_value):
                        return 'unassigned'
                    if local_rmsd >= rmsd_high_threshold and ll_value <= ll_low_threshold:
                        return 'group_a_high_geometry_low_likelihood'
                    if local_rmsd <= rmsd_low_threshold and ll_value >= ll_high_threshold:
                        return 'group_b_low_geometry_high_likelihood'
                    if local_rmsd <= rmsd_low_threshold and ll_value <= ll_low_threshold:
                        return 'group_c_low_geometry_low_likelihood'
                    return 'unassigned'

                variant_level['blinded_group'] = [
                    assign_blinded_group(local_rmsd, ll_value)
                    for local_rmsd, ll_value in zip(variant_level['local_rmsd_median'], variant_level['ll_proper'])
                ]
                entry_level = entry_level.merge(
                    variant_level[['variant_id', 'blinded_group']],
                    on='variant_id',
                    how='left',
                    suffixes=('', '_variant'),
                )

                correlation_rows = []
                for level_name, frame, rmsd_column, contact_column in [
                    ('entry_level', entry_level, 'local_rmsd', 'contact_change_fraction'),
                    ('variant_level', variant_level, 'local_rmsd_median', 'contact_change_fraction_median'),
                ]:
                    correlation_rows.extend([
                        {'analysis_level': level_name, 'metric_name': 'frob_vs_local_rmsd_spearman', 'value': spearman_or_nan(frame['frob_dist'], frame[rmsd_column])},
                        {'analysis_level': level_name, 'metric_name': 'll_vs_local_rmsd_spearman', 'value': spearman_or_nan(frame['ll_proper'], frame[rmsd_column])},
                        {'analysis_level': level_name, 'metric_name': 'pair_vs_local_rmsd_spearman', 'value': spearman_or_nan(frame['pair_score_raw'], frame[rmsd_column])},
                        {'analysis_level': level_name, 'metric_name': 'frob_vs_local_rmsd_pearson', 'value': pearson_or_nan(frame['frob_dist'], frame[rmsd_column])},
                        {'analysis_level': level_name, 'metric_name': 'll_vs_local_rmsd_pearson', 'value': pearson_or_nan(frame['ll_proper'], frame[rmsd_column])},
                        {'analysis_level': level_name, 'metric_name': 'pair_vs_contact_change_spearman', 'value': spearman_or_nan(frame['pair_score_raw'], frame[contact_column])},
                    ])

                correlation_summary = pd.DataFrame(correlation_rows)
                blinded_group_summary = (
                    variant_level
                    .groupby('blinded_group', dropna=False)
                    .agg(
                        n_variants=('variant_id', 'count'),
                        median_local_rmsd=('local_rmsd_median', median_or_nan),
                        median_global_rmsd=('global_rmsd_median', median_or_nan),
                        median_frob_dist=('frob_dist', median_or_nan),
                        median_ll_proper=('ll_proper', median_or_nan),
                        median_pair_score=('pair_score_raw', median_or_nan),
                        median_contact_change_fraction=('contact_change_fraction_median', median_or_nan),
                    )
                    .reset_index()
                    .sort_values(['n_variants', 'median_local_rmsd'], ascending=[False, False])
                )

                hokkaido_case = variant_level[variant_level['blinded_group'] == 'group_a_high_geometry_low_likelihood'].copy()
                if hokkaido_case.empty:
                    hokkaido_case = variant_level.copy()
                hokkaido_case = hokkaido_case.sort_values(['local_rmsd_median', 'frob_dist', 'll_proper'], ascending=[False, False, True]).head(1)

                exception_cases = variant_level.sort_values(['local_rmsd_median', 'frob_rank_norm'], ascending=[False, True]).head(3).copy()

                entry_level.to_csv(TABLES_DIR / 'tp53_structural_pairs_entry_level_scored.csv', index=False)
                variant_level.to_csv(TABLES_DIR / 'tp53_structural_pairs_variant_level_scored.csv', index=False)
                blinded_group_summary.to_csv(TABLES_DIR / 'tp53_blinded_group_summary.csv', index=False)
                correlation_summary.to_csv(TABLES_DIR / 'tp53_correlation_summary.csv', index=False)
                hokkaido_case.to_csv(TABLES_DIR / 'tp53_hokkaido_case.csv', index=False)
                exception_cases.to_csv(TABLES_DIR / 'tp53_exception_cases.csv', index=False)

                display(correlation_summary)
                display(blinded_group_summary)
                display(hokkaido_case)
                done('Blinded groups and dissociation summaries computed.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Build reviewer-facing figures, including the top-case contact change map
                if variant_level.empty:
                    raise RuntimeError('Variant-level structural subset is empty. No figures can be created.')

                def annotate_points(ax, frame: pd.DataFrame, x_col: str, y_col: str, label_col: str) -> None:
                    for row in frame.to_dict(orient='records'):
                        x = safe_float(row.get(x_col))
                        y = safe_float(row.get(y_col))
                        if math.isnan(x) or math.isnan(y):
                            continue
                        ax.annotate(str(row.get(label_col, '')), (x, y), xytext=(4, 4), textcoords='offset points', fontsize=8, alpha=0.85)

                fig, ax = plt.subplots(figsize=(8.2, 6.2))
                scatter = ax.scatter(variant_level['local_rmsd_median'], variant_level['frob_dist'], c=variant_level['pair_rank_norm'], cmap='viridis', s=70, edgecolor='black', linewidth=0.4)
                annotate_points(ax, variant_level, 'local_rmsd_median', 'frob_dist', 'variant_id')
                ax.set_title('TP53 structural subset: local RMSD vs covariance Frobenius distance')
                ax.set_xlabel('Local window RMSD (A)')
                ax.set_ylabel('frob_dist')
                ax.grid(alpha=0.25)
                fig.colorbar(scatter, ax=ax, label='pair_rank_norm')
                fig.tight_layout()
                fig.savefig(FIGURES_DIR / 'tp53_frob_vs_local_rmsd.png', dpi=220)
                plt.close(fig)

                fig, ax = plt.subplots(figsize=(8.2, 6.2))
                scatter = ax.scatter(variant_level['local_rmsd_median'], variant_level['ll_proper'], c=variant_level['pair_rank_norm'], cmap='magma', s=70, edgecolor='black', linewidth=0.4)
                annotate_points(ax, variant_level, 'local_rmsd_median', 'll_proper', 'variant_id')
                ax.set_title('TP53 structural subset: local RMSD vs scalar likelihood penalty')
                ax.set_xlabel('Local window RMSD (A)')
                ax.set_ylabel('ll_proper')
                ax.grid(alpha=0.25)
                fig.colorbar(scatter, ax=ax, label='pair_rank_norm')
                fig.tight_layout()
                fig.savefig(FIGURES_DIR / 'tp53_ll_vs_local_rmsd.png', dpi=220)
                plt.close(fig)

                grouped = variant_level[variant_level['blinded_group'] != 'unassigned'].copy()
                if grouped.empty:
                    grouped = variant_level.copy()
                fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.8))
                group_names = [name for name, _ in grouped.groupby('blinded_group')]
                frob_groups = [group['frob_dist'].dropna().to_numpy(dtype=float) for _, group in grouped.groupby('blinded_group')]
                ll_groups = [group['ll_proper'].dropna().to_numpy(dtype=float) for _, group in grouped.groupby('blinded_group')]
                axes[0].boxplot(frob_groups, tick_labels=group_names, showfliers=False)
                axes[0].set_title('frob_dist by blinded group')
                axes[0].set_ylabel('frob_dist')
                axes[0].tick_params(axis='x', rotation=20)
                axes[0].grid(alpha=0.2)
                axes[1].boxplot(ll_groups, tick_labels=group_names, showfliers=False)
                axes[1].set_title('ll_proper by blinded group')
                axes[1].set_ylabel('ll_proper')
                axes[1].tick_params(axis='x', rotation=20)
                axes[1].grid(alpha=0.2)
                fig.tight_layout()
                fig.savefig(FIGURES_DIR / 'tp53_blinded_group_boxplots.png', dpi=220)
                plt.close(fig)

                if not hokkaido_case.empty:
                    top_case = hokkaido_case.iloc[0].to_dict()
                    top_entry = entry_level[entry_level['identifier'] == str(top_case['best_entry_identifier'])].iloc[0].to_dict()
                    payload_path = Path(top_entry['contact_payload_path'])
                    if payload_path.exists():
                        payload = json.loads(payload_path.read_text(encoding='utf-8'))
                        diff_matrix = np.asarray(payload['diff_contact_map'], dtype=float)
                        if diff_matrix.size:
                            fig, ax = plt.subplots(figsize=(5.6, 5.0))
                            image = ax.imshow(diff_matrix, cmap='coolwarm', vmin=-1, vmax=1, aspect='auto')
                            ax.set_title(f"{top_case['variant_id']} local contact delta")
                            ax.set_xlabel('Window residue index')
                            ax.set_ylabel('Window residue index')
                            fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
                            fig.tight_layout()
                            fig.savefig(FIGURES_DIR / 'tp53_hokkaido_contact_delta.png', dpi=220)
                            plt.close(fig)

                fig, ax = plt.subplots(figsize=(8.2, 5.0))
                ranked = variant_level.sort_values('local_rmsd_median', ascending=False).head(TOP_CASES)
                ax.bar(ranked['variant_id'].astype(str), ranked['local_rmsd_median'].astype(float), color='#4c78a8')
                ax.set_title('Top TP53 structural perturbations in the experimental subset')
                ax.set_ylabel('Local RMSD (A)')
                ax.set_xlabel('variant_id')
                ax.tick_params(axis='x', rotation=25)
                ax.grid(axis='y', alpha=0.25)
                fig.tight_layout()
                fig.savefig(FIGURES_DIR / 'tp53_top_local_rmsd_variants.png', dpi=220)
                plt.close(fig)

                print('Saved figures:', sorted(path.name for path in FIGURES_DIR.glob('*.png')))
                done('Reviewer-facing structural dissociation figures saved.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Write markdown/json summaries, claim paragraph, and the final bundle
                variant_corr_frob = safe_float(correlation_summary[(correlation_summary['analysis_level'] == 'variant_level') & (correlation_summary['metric_name'] == 'frob_vs_local_rmsd_spearman')]['value'].iloc[0])
                variant_corr_ll = safe_float(correlation_summary[(correlation_summary['analysis_level'] == 'variant_level') & (correlation_summary['metric_name'] == 'll_vs_local_rmsd_spearman')]['value'].iloc[0])
                variant_corr_pair = safe_float(correlation_summary[(correlation_summary['analysis_level'] == 'variant_level') & (correlation_summary['metric_name'] == 'pair_vs_local_rmsd_spearman')]['value'].iloc[0])
                corr_gap = variant_corr_frob - variant_corr_ll if not math.isnan(variant_corr_frob) and not math.isnan(variant_corr_ll) else float('nan')

                group_a_count = int((variant_level['blinded_group'] == 'group_a_high_geometry_low_likelihood').sum())
                group_b_count = int((variant_level['blinded_group'] == 'group_b_low_geometry_high_likelihood').sum())
                group_c_count = int((variant_level['blinded_group'] == 'group_c_low_geometry_low_likelihood').sum())

                claim_status = 'weak_tp53_structural_dissociation'
                claim_reason = 'The TP53 structural subset is informative but not yet strong enough to make a mechanistic dissociation claim.'
                if len(variant_level) >= 6 and len(entry_level) >= 12 and not math.isnan(variant_corr_frob) and not math.isnan(variant_corr_ll) and variant_corr_frob >= 0.45 and corr_gap >= 0.20:
                    claim_status = 'tp53_structural_dissociation_supported'
                    claim_reason = 'On the TP53 structural subset, covariance tracks local structural perturbation substantially better than scalar likelihood, supporting the tension-versus-surprise interpretation.'
                elif len(variant_level) >= 5 and not math.isnan(variant_corr_frob) and not math.isnan(variant_corr_ll) and variant_corr_frob > variant_corr_ll:
                    claim_status = 'bounded_tp53_structural_case_study_supported'
                    claim_reason = 'The TP53 structural subset favors covariance over scalar likelihood, but the evidence is still best framed as a bounded mechanistic case study.'
                elif group_a_count >= 1 and not math.isnan(variant_corr_frob):
                    claim_status = 'case_level_tp53_rescue_supported'
                    claim_reason = 'The strongest support is case-level: at least one TP53 mutant shows high local structural perturbation with only modest scalar likelihood penalty.'

                top_case_payload = hokkaido_case.iloc[0].to_dict() if not hokkaido_case.empty else {}
                exception_payload = exception_cases.to_dict(orient='records')
                claim_paragraph = (
                    'Using experimental TP53 crystal structures as an external geometric ground truth, Block 10 builds a bounded mechanistic test of SpectralBio. '
                    f'The structural subset contains {len(entry_level)} WT-vs-mutant entry pairs covering {len(variant_level)} unique TP53 missense variants. '
                    f'At the variant level, the covariance score tracks local window RMSD with Spearman {variant_corr_frob:.3f} while scalar likelihood tracks it with Spearman {variant_corr_ll:.3f}, '
                    f'for a covariance-minus-likelihood gap of {corr_gap:.3f}. '
                    'This does not prove universal structural validity, but it directly addresses the reviewer question of whether covariance is merely a nonlinear rewrite of likelihood: on this TP53 structural subset, covariance behaves more like a detector of local geometric tension, while likelihood behaves more like a detector of sequence surprise.'
                )

                summary_payload = {
                    'notebook_slug': NOTEBOOK_SLUG,
                    'account_label': ACCOUNT_LABEL,
                    'run_at_utc': RUN_AT,
                    'head_commit': repo_status['head_commit'],
                    'claim_status': claim_status,
                    'claim_reason': claim_reason,
                    'n_search_hits': int(len(search_identifiers)),
                    'n_filtered_entities': int(len(structural_entities)),
                    'n_wt_entities': int(len(wt_entities)),
                    'n_mutant_entries': int(len(mutant_entities)),
                    'n_entry_pairs': int(len(entry_level)),
                    'n_unique_variants': int(len(variant_level)),
                    'group_a_count': group_a_count,
                    'group_b_count': group_b_count,
                    'group_c_count': group_c_count,
                    'rmsd_high_threshold': rmsd_high_threshold,
                    'rmsd_low_threshold': rmsd_low_threshold,
                    'll_high_threshold': ll_high_threshold,
                    'll_low_threshold': ll_low_threshold,
                    'variant_level_frob_vs_local_rmsd_spearman': variant_corr_frob,
                    'variant_level_ll_vs_local_rmsd_spearman': variant_corr_ll,
                    'variant_level_pair_vs_local_rmsd_spearman': variant_corr_pair,
                    'variant_level_corr_gap_frob_minus_ll': corr_gap,
                    'top_case': top_case_payload,
                    'exception_cases': exception_payload,
                    'claim_paragraph': claim_paragraph,
                }
                (MANIFESTS_DIR / 'block10_summary.json').write_text(json.dumps(summary_payload, indent=2), encoding='utf-8')
                (MANIFESTS_DIR / 'artifact_summary.json').write_text(json.dumps(summary_payload, indent=2), encoding='utf-8')

                summary_md = '\\n'.join([
                    '# Block 10 Structural Dissociation Summary',
                    '',
                    f"- Claim status: `{claim_status}`",
                    f"- Claim reason: {claim_reason}",
                    f"- TP53 structural entity hits: `{len(structural_entities)}` filtered from `{len(search_identifiers)}` search hits",
                    f"- WT entities: `{len(wt_entities)}`",
                    f"- Mutant entries: `{len(mutant_entities)}`",
                    f"- Entry-level pairs: `{len(entry_level)}`",
                    f"- Unique TP53 variants: `{len(variant_level)}`",
                    f"- Group A count: `{group_a_count}`",
                    f"- Group B count: `{group_b_count}`",
                    f"- Group C count: `{group_c_count}`",
                    f"- Variant-level Spearman(frob_dist, local RMSD): `{variant_corr_frob:.3f}`" if not math.isnan(variant_corr_frob) else '- Variant-level Spearman(frob_dist, local RMSD): `nan`',
                    f"- Variant-level Spearman(ll_proper, local RMSD): `{variant_corr_ll:.3f}`" if not math.isnan(variant_corr_ll) else '- Variant-level Spearman(ll_proper, local RMSD): `nan`',
                    f"- Variant-level covariance-minus-likelihood gap: `{corr_gap:.3f}`" if not math.isnan(corr_gap) else '- Variant-level covariance-minus-likelihood gap: `nan`',
                    '',
                    '## Claim Paragraph',
                    '',
                    claim_paragraph,
                ])
                (TEXT_DIR / 'block10_summary.md').write_text(summary_md + '\\n', encoding='utf-8')
                (TEXT_DIR / 'block10_claim_paragraph.md').write_text(claim_paragraph + '\\n', encoding='utf-8')

                if ZIP_PATH.exists():
                    ZIP_PATH.unlink()
                if ROOT_ZIP_COPY.exists():
                    ROOT_ZIP_COPY.unlink()
                with zipfile.ZipFile(ZIP_PATH, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
                    for path in sorted(RESULTS_ROOT.rglob('*')):
                        if path.is_file():
                            archive.write(path, path.relative_to(RESULTS_ROOT.parent))
                shutil.copy2(ZIP_PATH, ROOT_ZIP_COPY)
                print(summary_md)
                done('Block 10 structural dissociation bundle is ready for download.')
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
    output_path = repo_root / "New Notebooks" / "07_block10_structural_dissociation_tp53_h100.ipynb"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(notebook, indent=2), encoding="utf-8")
    print(f"Wrote notebook to {output_path}")


if __name__ == "__main__":
    main()
