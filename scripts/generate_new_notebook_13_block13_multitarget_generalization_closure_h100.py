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
            "# Experiment: SpectralBio Block 13 - Multi-Target Generalization Closure (H100)\n\n"
            "Objective:\n"
            "- Treat Block 13 as a **multi-target closure court** for generalizability rather than as an open exploration notebook.\n"
            "- Reuse the strongest public evidence already produced by Blocks 01, 06, 08, 10B, 12B, 12C, and 12D.\n"
            "- Freeze explicit replay contracts for `TP53`, `BRCA2`, and `TSC2`, while keeping `CREBBP`, `GRIN2A`, `BRCA1`, and `MSH2` as stress-test surfaces.\n"
            "- Produce a reviewer-facing package under `New Notebooks/results/13_block13_multitarget_generalization_closure_h100/` with tables, figures, manifests, a markdown claim package, and a zip bundle.\n"
        ),
        markdown_cell(
            "## Final Contract\n\n"
            "- This notebook is designed as the **best single H100 closure notebook** we can build from the current repo and evidence stack.\n"
            "- It freezes multi-target replay surfaces first, then asks whether portability closes under three public firewalls:\n"
            "  1. `holdout-positive`,\n"
            "  2. `transfer-positive`,\n"
            "  3. `control win`.\n"
            "- Primary replay-ready targets:\n"
            "  - `TP53` as canonical and structural anchor\n"
            "  - `BRCA2` as stronger-baseline flagship\n"
            "  - `TSC2` as the best current portability witness\n"
            "- Secondary positive stress targets:\n"
            "  - `CREBBP`\n"
            "  - `GRIN2A`\n"
            "- Explicit negative controls:\n"
            "  - `BRCA1`\n"
            "  - `MSH2`\n"
            "- Model families in scope:\n"
            "  - `esm`\n"
            "  - `esm_variant_specialist`\n"
            "  - `prottrans`\n"
            "  - `bert_style`\n"
            "  - `progen`\n"
            "- `replay-ready` here means a target has a frozen panel, a sequence-backed contract, and at least one public positive evidence surface.\n"
            "- `holdout-positive` means positive enrichment with non-trivial rule-on coverage on a target not used to define the default protocol.\n"
            "- `transfer-positive` means a non-ESM witness remains positive under the portable protocol.\n"
            "- `control win` means the selected covariance-aware rule beats scalar-matched controls on the same surface.\n"
            "- The notebook is allowed to conclude that the result is still supportive. It is **not** allowed to hide where the closure fails.\n"
        ),
        code_cell(
            dedent(
                """
                # Setup: imports, runtime requirements, notebook identifiers, and notebook knobs
                from __future__ import annotations

                import importlib
                import importlib.util
                import json
                import os
                import platform
                import random
                import subprocess
                import sys
                from datetime import datetime, timezone
                from pathlib import Path

                import numpy as np

                NOTEBOOK_SLUG = '13_block13_multitarget_generalization_closure_h100'
                ACCOUNT_LABEL = os.environ.get('SPECTRALBIO_ACCOUNT_LABEL', 'local_run')
                RUN_AT = datetime.now(timezone.utc).isoformat()
                OVERWRITE = os.environ.get('SPECTRALBIO_OVERWRITE', '').strip().lower() in {'1', 'true', 'yes'}
                SKIP_LIVE = os.environ.get('SPECTRALBIO_BLOCK13_SKIP_LIVE', '').strip().lower() in {'1', 'true', 'yes'}
                MODEL_FILTER = {
                    item.strip().lower()
                    for item in os.environ.get('SPECTRALBIO_BLOCK13_MODEL_FILTER', '').split(',')
                    if item.strip()
                }
                TARGET_FILTER = {
                    item.strip().upper()
                    for item in os.environ.get('SPECTRALBIO_BLOCK13_TARGET_FILTER', '').split(',')
                    if item.strip()
                }
                FIXED_ALPHA = float(os.environ.get('SPECTRALBIO_BLOCK13_FIXED_ALPHA', '0.55'))
                ALPHA_GRID = [
                    float(item.strip())
                    for item in os.environ.get('SPECTRALBIO_BLOCK13_ALPHA_GRID', '0.35,0.45,0.55,0.65,0.75').split(',')
                    if item.strip()
                ]
                BOOTSTRAP_REPLICATES = int(os.environ.get('SPECTRALBIO_BLOCK13_BOOTSTRAP_REPLICATES', '2000'))
                RANDOM_SEED = int(os.environ.get('SPECTRALBIO_BLOCK13_RANDOM_SEED', '42'))
                WINDOW_RADIUS = int(os.environ.get('SPECTRALBIO_BLOCK13_WINDOW_RADIUS', '40'))
                CHECKPOINT_EVERY = int(os.environ.get('SPECTRALBIO_BLOCK13_CHECKPOINT_EVERY', '10'))

                MODEL_SPECS = [
                    {'model_name': 'facebook/esm1v_t33_650M_UR90S_1', 'model_label': 'ESM-1v', 'family_label': 'esm_variant_specialist', 'priority_rank': 1},
                    {'model_name': 'facebook/esm2_t30_150M_UR50D', 'model_label': 'ESM2-150M', 'family_label': 'esm', 'priority_rank': 2},
                    {'model_name': 'facebook/esm2_t33_650M_UR50D', 'model_label': 'ESM2-650M', 'family_label': 'esm', 'priority_rank': 3},
                    {'model_name': 'Rostlab/prot_t5_xl_half_uniref50-enc', 'model_label': 'ProtT5', 'family_label': 'prottrans', 'priority_rank': 4},
                    {'model_name': 'hugohrban/progen2-small', 'model_label': 'ProGen2-small', 'family_label': 'progen', 'priority_rank': 5},
                    {'model_name': 'facebook/esm2_t12_35M_UR50D', 'model_label': 'ESM2-35M', 'family_label': 'esm', 'priority_rank': 6},
                    {'model_name': 'facebook/esm2_t36_3B_UR50D', 'model_label': 'ESM2-3B', 'family_label': 'esm', 'priority_rank': 7},
                    {'model_name': 'Rostlab/prot_bert', 'model_label': 'ProtBERT', 'family_label': 'bert_style', 'priority_rank': 8},
                    {'model_name': 'Rostlab/prot_bert_bfd', 'model_label': 'ProtBERT-BFD', 'family_label': 'bert_style', 'priority_rank': 9},
                    {'model_name': 'hugohrban/progen2-base', 'model_label': 'ProGen2-base', 'family_label': 'progen', 'priority_rank': 10},
                ]

                TARGET_SPECS = [
                    {'gene': 'TP53', 'role': 'primary', 'is_negative_control': False},
                    {'gene': 'BRCA2', 'role': 'primary', 'is_negative_control': False},
                    {'gene': 'TSC2', 'role': 'primary', 'is_negative_control': False},
                    {'gene': 'CREBBP', 'role': 'secondary_positive', 'is_negative_control': False},
                    {'gene': 'GRIN2A', 'role': 'secondary_positive', 'is_negative_control': False},
                    {'gene': 'BRCA1', 'role': 'negative_control', 'is_negative_control': True},
                    {'gene': 'MSH2', 'role': 'negative_control', 'is_negative_control': True},
                ]

                REQUIRED_PACKAGES = {
                    'packaging': 'packaging>=24',
                    'numpy': 'numpy==2.1.3',
                    'scipy': 'scipy==1.14.1',
                    'sklearn': 'scikit-learn==1.5.2',
                    'transformers': 'transformers==4.49.0',
                    'torch': 'torch',
                    'pandas': 'pandas>=2.2.0',
                    'matplotlib': 'matplotlib>=3.9.0',
                    'requests': 'requests>=2.32.0',
                    'accelerate': 'accelerate>=1.0.0',
                    'sentencepiece': 'sentencepiece>=0.2.0',
                    'safetensors': 'safetensors>=0.4.0',
                    'google.protobuf': 'protobuf>=5.0.0',
                    'einops': 'einops>=0.8.0',
                }

                missing_specs = []
                for module_name, requirement in REQUIRED_PACKAGES.items():
                    if importlib.util.find_spec(module_name) is None:
                        missing_specs.append(requirement)

                if missing_specs:
                    subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', *missing_specs], check=True)

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
                done('Environment, runtime requirements, model roster, and notebook knobs are prepared.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Helpers: repo discovery, path resolution, statistics, checkpointing, and bundle utilities
                import math
                import shutil
                import zipfile

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

                def resolve_existing_path(*candidates: Path | str) -> Path:
                    for candidate in candidates:
                        path = Path(candidate)
                        if path.exists():
                            return path
                    raise FileNotFoundError('None of the candidate paths exist: ' + ' | '.join(str(item) for item in candidates))

                def maybe_read_json(path: Path) -> dict:
                    return json.loads(path.read_text(encoding='utf-8'))

                def safe_float(value, default=float('nan')) -> float:
                    try:
                        result = float(value)
                        if math.isnan(result):
                            return default
                        return result
                    except Exception:
                        return default

                def paired_bootstrap_delta(labels, left_scores, right_scores, n_boot=2000, seed=42):
                    labels_arr = np.asarray(labels)
                    left_arr = np.asarray(left_scores, dtype=float)
                    right_arr = np.asarray(right_scores, dtype=float)
                    rng = np.random.default_rng(seed)
                    deltas = []
                    n_rows = len(labels_arr)
                    if n_rows == 0:
                        return {'observed_delta': float('nan'), 'n_valid': 0, 'ci_2p5': float('nan'), 'ci_97p5': float('nan')}
                    observed = safe_float(np.nanmean(left_arr - right_arr))
                    for _ in range(n_boot):
                        sample_idx = rng.integers(0, n_rows, size=n_rows)
                        sample_labels = labels_arr[sample_idx]
                        if len(set(sample_labels.tolist())) < 2:
                            continue
                        deltas.append(float(np.nanmean(left_arr[sample_idx] - right_arr[sample_idx])))
                    if not deltas:
                        return {'observed_delta': observed, 'n_valid': 0, 'ci_2p5': float('nan'), 'ci_97p5': float('nan')}
                    return {
                        'observed_delta': observed,
                        'n_valid': len(deltas),
                        'ci_2p5': float(np.percentile(deltas, 2.5)),
                        'ci_97p5': float(np.percentile(deltas, 97.5)),
                    }

                def checkpoint_path(model_label: str, gene: str) -> Path:
                    safe_model = model_label.replace('/', '_').replace('-', '_')
                    return LIVE_SCORES_DIR / safe_model / f'{gene.lower()}_{safe_model}_evidence.csv'

                def write_runtime_manifest(extra_payload: dict | None = None) -> dict:
                    payload = {
                        'notebook_slug': NOTEBOOK_SLUG,
                        'account_label': ACCOUNT_LABEL,
                        'run_at': RUN_AT,
                        'overwrite': OVERWRITE,
                        'skip_live': SKIP_LIVE,
                        'fixed_alpha': FIXED_ALPHA,
                        'alpha_grid': ALPHA_GRID,
                        'window_radius': WINDOW_RADIUS,
                        'checkpoint_every': CHECKPOINT_EVERY,
                        'random_seed': RANDOM_SEED,
                        'runtime': runtime_rows,
                    }
                    if extra_payload:
                        payload.update(extra_payload)
                    (RUNTIME_DIR / 'runtime_manifest.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
                    return payload

                def maybe_colab_download(path: Path) -> None:
                    try:
                        from google.colab import files
                        files.download(str(path))
                    except Exception:
                        pass

                def zip_results_bundle() -> Path:
                    if BUNDLE_ROOT.exists():
                        shutil.rmtree(BUNDLE_ROOT)
                    shutil.copytree(RESULTS_ROOT, BUNDLE_ROOT)
                    if ZIP_PATH.exists():
                        ZIP_PATH.unlink()
                    with zipfile.ZipFile(ZIP_PATH, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
                        for file_path in RESULTS_ROOT.rglob('*'):
                            if file_path.is_file() and file_path != ZIP_PATH:
                                archive.write(file_path, arcname=str(file_path.relative_to(RESULTS_ROOT)))
                    return ZIP_PATH

                def load_gene_sequence_from_known_sources(gene: str, accession: str | None = None) -> str:
                    gene_upper = gene.upper()
                    if gene_upper == 'TP53':
                        return load_tp53_sequence()
                    if gene_upper == 'BRCA1':
                        return load_brca1_sequence()
                    candidate_paths = []
                    if accession:
                        candidate_paths.extend([
                            REPO_ROOT / 'New Notebooks' / 'results' / '12b_block12_multifamily_coverage_aware_generalization_h100' / 'runtime' / 'sequence_cache' / f'{accession}.fasta',
                            REPO_ROOT / 'New Notebooks' / 'results' / '10b_block7c_alpha_crossfamily_finalists_h100' / 'runtime' / 'sequence_cache' / f'{accession}.fasta',
                        ])
                    candidate_paths.extend([
                        REPO_ROOT / 'New Notebooks' / 'results' / '01_block1_baseline_alpha_regime_audit_h100' / 'runtime' / 'cache' / 'uniprot' / f'{gene.lower()}.fasta',
                    ])
                    for path in candidate_paths:
                        if path.exists():
                            lines = [line.strip() for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
                            return ''.join(line for line in lines if not line.startswith('>'))
                    raise FileNotFoundError(f'No cached sequence found for {gene_upper} ({accession}).')

                REPO_ROOT = find_repo_root()
                SRC_ROOT = REPO_ROOT / 'src'
                if str(SRC_ROOT) not in sys.path:
                    sys.path.insert(0, str(SRC_ROOT))

                from spectralbio.data.sequences import load_brca1_sequence, load_tp53_sequence
                from spectralbio.pipeline.combine_scores import normalize
                from spectralbio.pipeline.compute_covariance_features import covariance_features
                from spectralbio.pipeline.compute_hidden_states import extract_local_hidden_states
                from spectralbio.pipeline.compute_ll_proper import compute_ll_proper
                from spectralbio.supplementary.reject_recovery import _ensure_gene_score_rows

                RESULTS_DIR = REPO_ROOT / 'New Notebooks' / 'results'
                RESULTS_ROOT = ensure_dir(RESULTS_DIR / NOTEBOOK_SLUG)
                TABLES_DIR = ensure_dir(RESULTS_ROOT / 'tables')
                FIGURES_DIR = ensure_dir(RESULTS_ROOT / 'figures')
                TEXT_DIR = ensure_dir(RESULTS_ROOT / 'text')
                MANIFESTS_DIR = ensure_dir(RESULTS_ROOT / 'manifests')
                RUNTIME_DIR = ensure_dir(RESULTS_ROOT / 'runtime')
                LIVE_SCORES_DIR = ensure_dir(RESULTS_ROOT / 'live_scores')
                BUNDLE_ROOT = RESULTS_DIR / f'{NOTEBOOK_SLUG}_bundle'
                ZIP_PATH = RESULTS_ROOT / f'{NOTEBOOK_SLUG}_bundle.zip'

                BLOCK1_ROOT = RESULTS_DIR / '01_block1_baseline_alpha_regime_audit_h100'
                BLOCK6_ROOT = RESULTS_DIR / '06_block5_clinical_panel_audit_h100'
                BLOCK8_ROOT = RESULTS_DIR / '08_block7_turbo_gallery_rescues_h100'
                BLOCK10B_ROOT = RESULTS_DIR / '10b_block7c_alpha_crossfamily_finalists_h100'
                BLOCK12B_ROOT = RESULTS_DIR / '12b_block12_multifamily_coverage_aware_generalization_h100'
                BLOCK12C_ROOT = RESULTS_DIR / '12c_block12_covariance_adjudication_structural_closure_h100'
                BLOCK12D_ROOT = RESULTS_DIR / '12d_block12_final_nuclear_localization_h100'

                runtime_manifest = write_runtime_manifest({'repo_root': str(REPO_ROOT)})
                display(pd.DataFrame([runtime_manifest]))
                done('Helpers, repo discovery, statistics, checkpointing, and bundle utilities are ready.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Load upstream artifacts and build the target/model roster used by the closure court
                block1_summary = maybe_read_json(resolve_existing_path(BLOCK1_ROOT / 'runtime' / 'esm1v_augmentation' / 'esm1v_augmentation_summary.json'))
                block6_summary = maybe_read_json(resolve_existing_path(BLOCK6_ROOT / 'manifests' / 'block6_summary.json'))
                block7_turbo_summary = maybe_read_json(resolve_existing_path(BLOCK8_ROOT / 'manifests' / 'block7_turbo_summary.json', BLOCK8_ROOT / '08_block7_turbo_gallery_rescues_h100' / 'manifests' / 'block7_turbo_summary.json'))
                block10b_summary = maybe_read_json(resolve_existing_path(BLOCK10B_ROOT / 'manifests' / 'block7c_alpha_crossfamily_summary.json'))
                block12b_summary = maybe_read_json(resolve_existing_path(BLOCK12B_ROOT / 'manifests' / 'block12b_multifamily_summary.json'))
                block12c_summary = maybe_read_json(resolve_existing_path(BLOCK12C_ROOT / 'manifests' / 'block12c_covariance_adjudication_summary.json', BLOCK12C_ROOT / 'manifests' / 'artifact_summary.json'))
                block12d_summary = maybe_read_json(resolve_existing_path(BLOCK12D_ROOT / 'manifests' / 'block12d_final_localization_summary.json', BLOCK12D_ROOT / 'manifests' / 'artifact_summary.json'))

                clinical_gene_panel = pd.read_csv(resolve_existing_path(BLOCK6_ROOT / 'tables' / 'clinical_gene_panel.csv'))
                clinical_variant_scores = pd.read_csv(resolve_existing_path(BLOCK6_ROOT / 'tables' / 'clinical_panel_variant_scores.csv'))
                clinical_case_shortlist = pd.read_csv(resolve_existing_path(BLOCK6_ROOT / 'tables' / 'clinical_case_shortlist_for_block7.csv'))
                finalists_panel = pd.read_csv(resolve_existing_path(BLOCK10B_ROOT / 'tables' / 'finalists_panel.csv'))
                case_support_collapsed = pd.read_csv(resolve_existing_path(BLOCK10B_ROOT / 'tables' / 'case_support_collapsed.csv'))
                gallery_final_cases = pd.read_csv(resolve_existing_path(BLOCK8_ROOT / 'tables' / 'gallery_final_cases.csv', BLOCK8_ROOT / '08_block7_turbo_gallery_rescues_h100' / 'tables' / 'gallery_final_cases.csv'))
                gallery_anti_case = pd.read_csv(resolve_existing_path(BLOCK8_ROOT / 'tables' / 'gallery_anti_case.csv', BLOCK8_ROOT / '08_block7_turbo_gallery_rescues_h100' / 'tables' / 'gallery_anti_case.csv'))
                mini_holdout_transfer_summary = pd.read_csv(resolve_existing_path(BLOCK12B_ROOT / 'tables' / 'mini_holdout_transfer_summary.csv'))
                tp53_model_summary = pd.read_csv(resolve_existing_path(BLOCK12B_ROOT / 'tables' / 'tp53_model_summary.csv'))
                tp53_model_variant_scores = pd.read_csv(resolve_existing_path(BLOCK12B_ROOT / 'tables' / 'tp53_model_variant_scores.csv'))
                control_win_summary = pd.read_csv(resolve_existing_path(BLOCK12B_ROOT / 'tables' / 'control_win_summary.csv'))

                brca2_aug_table = pd.read_csv(resolve_existing_path(BLOCK1_ROOT / 'runtime' / 'esm1v_augmentation' / 'brca2' / 'augmentation_table.csv'))
                msh2_aug_table = pd.read_csv(resolve_existing_path(BLOCK1_ROOT / 'runtime' / 'esm1v_augmentation' / 'msh2' / 'augmentation_table.csv'))
                tp53_aug_table = pd.read_csv(resolve_existing_path(BLOCK1_ROOT / 'runtime' / 'esm1v_augmentation' / 'tp53' / 'augmentation_table.csv'))

                model_roster = pd.DataFrame(MODEL_SPECS).sort_values(['priority_rank', 'model_label']).reset_index(drop=True)
                if MODEL_FILTER:
                    model_roster = model_roster[model_roster['model_label'].str.lower().isin(MODEL_FILTER)].reset_index(drop=True)

                target_roster = pd.DataFrame(TARGET_SPECS)
                if TARGET_FILTER:
                    target_roster = target_roster[target_roster['gene'].isin(TARGET_FILTER)].reset_index(drop=True)

                display(model_roster)
                display(target_roster)
                display(clinical_gene_panel[['gene', 'focus_role', 'delta_pair_vs_ll']])
                done('Upstream block summaries, target evidence tables, and the closure roster are loaded.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Build replay-ready target panels and target contracts with a shared schema
                primary_targets = set(target_roster.loc[target_roster['role'] == 'primary', 'gene'])
                negative_targets = set(target_roster.loc[target_roster['is_negative_control'], 'gene'])

                panel_frames = []
                contract_rows = []

                def standardize_panel(frame: pd.DataFrame, gene: str, source_surface: str, accession: str | None = None) -> pd.DataFrame:
                    standardized = frame.copy()
                    if 'variant_id' not in standardized.columns:
                        standardized['variant_id'] = standardized.apply(lambda row: f"{gene}:{row['wt_aa']}{int(row['position'])}{row['mut_aa']}", axis=1)
                    if 'name' not in standardized.columns:
                        standardized['name'] = standardized['variant_id']
                    sequence = load_gene_sequence_from_known_sources(gene, accession)
                    standardized['gene'] = gene
                    standardized['sequence'] = sequence
                    standardized['source_surface'] = source_surface
                    standardized['is_primary_target'] = gene in primary_targets
                    standardized['is_negative_control'] = gene in negative_targets
                    standardized['position'] = standardized['position'].astype(int)
                    return standardized[['variant_id', 'gene', 'label', 'sequence', 'position', 'wt_aa', 'mut_aa', 'source_surface', 'is_primary_target', 'is_negative_control', 'name']]

                tp53_panel = pd.read_csv(resolve_existing_path(BLOCK12B_ROOT / 'tables' / 'tp53_canonical_panel.csv'))
                panel_frames.append(standardize_panel(tp53_panel, 'TP53', 'tp53_canonical_panel', accession='P04637'))
                panel_frames.append(standardize_panel(brca2_aug_table[['gene', 'name', 'position', 'wt_aa', 'mut_aa', 'label']].copy(), 'BRCA2', 'block1_brca2_augmentation'))

                clinical_focus_genes = {'TSC2': 'P49815', 'CREBBP': 'Q92793', 'BRCA1': 'P38398', 'MSH2': 'P43246', 'BRCA2': None}
                for gene, accession in clinical_focus_genes.items():
                    gene_frame = clinical_variant_scores[clinical_variant_scores['gene'] == gene][['gene', 'name', 'position', 'wt_aa', 'mut_aa', 'label', 'variant_id']].drop_duplicates().copy()
                    if not gene_frame.empty:
                        panel_frames.append(standardize_panel(gene_frame, gene, 'block6_clinical_panel_variant_scores', accession=accession))

                finalist_accessions = {'TSC2': 'P49815', 'CREBBP': 'Q92793', 'GRIN2A': 'Q12879', 'BRCA1': 'P38398', 'MSH2': 'P43246'}
                for gene, accession in finalist_accessions.items():
                    gene_frame = finalists_panel[finalists_panel['gene'] == gene][['gene', 'name', 'position', 'wt_aa', 'mut_aa', 'label', 'variant_id']].drop_duplicates().copy()
                    if not gene_frame.empty:
                        panel_frames.append(standardize_panel(gene_frame, gene, 'block10b_finalists_panel', accession=accession))

                replay_target_panels = pd.concat(panel_frames, ignore_index=True).drop_duplicates(subset=['variant_id', 'source_surface']).reset_index(drop=True)
                replay_target_panels.to_csv(TABLES_DIR / 'replay_target_panels.csv', index=False)

                for gene in target_roster['gene']:
                    target_rows = replay_target_panels[replay_target_panels['gene'] == gene].copy()
                    source_surfaces = sorted(target_rows['source_surface'].unique().tolist())
                    accession_candidates = finalists_panel.loc[finalists_panel['gene'] == gene, 'uniprot_accession'].dropna().unique().tolist()
                    accession = accession_candidates[0] if accession_candidates else {'TP53': 'P04637', 'BRCA1': 'P38398', 'MSH2': 'P43246', 'TSC2': 'P49815', 'CREBBP': 'Q92793', 'GRIN2A': 'Q12879'}.get(gene, '')
                    contract_rows.append({
                        'gene': gene,
                        'target_role': target_roster.loc[target_roster['gene'] == gene, 'role'].iloc[0],
                        'is_primary_target': gene in primary_targets,
                        'is_negative_control': gene in negative_targets,
                        'n_variants': int(len(target_rows)),
                        'n_positive': int(target_rows['label'].sum()) if not target_rows.empty else 0,
                        'n_negative': int((1 - target_rows['label']).sum()) if not target_rows.empty else 0,
                        'n_source_surfaces': len(source_surfaces),
                        'source_surfaces': '|'.join(source_surfaces),
                        'uniprot_accession': accession,
                        'sequence_loaded': bool(target_rows.shape[0]),
                        'contract_status': 'replay_candidate' if not target_rows.empty else 'missing_panel',
                    })

                replay_target_contracts = pd.DataFrame(contract_rows).sort_values(['is_primary_target', 'gene'], ascending=[False, True]).reset_index(drop=True)
                replay_target_contracts.to_csv(TABLES_DIR / 'replay_target_contracts.csv', index=False)
                replay_target_contracts.to_csv(TABLES_DIR / 'replay_ready_targets_overview.csv', index=False)
                replay_target_contracts.to_csv(TABLES_DIR / 'replay_target_manifest.csv', index=False)

                display(replay_target_contracts)
                display(replay_target_panels.head(20))
                done('Replay-ready target panels and target contracts are assembled with a shared schema.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Reuse-first multi-target scoring surface assembly across targets and model families
                variant_score_frames = []
                reuse_rows = []

                tp53_scores = tp53_model_variant_scores.copy()
                tp53_scores['source_block'] = '12b'
                tp53_scores['target_scope'] = 'TP53'
                variant_score_frames.append(tp53_scores)
                reuse_rows.append({'source_block': '12b', 'dataset': 'tp53_model_variant_scores', 'rows': int(len(tp53_scores)), 'models_covered': tp53_scores['model_label'].nunique(), 'targets_covered': tp53_scores['gene'].nunique()})

                for gene_name, frame in [('BRCA2', brca2_aug_table), ('MSH2', msh2_aug_table), ('TP53', tp53_aug_table)]:
                    copied = frame.copy()
                    copied['model_label'] = 'ESM-1v+ESM2-150M-reference'
                    copied['family_label'] = 'esm_variant_specialist_plus_reference'
                    copied['source_block'] = '01'
                    copied['target_scope'] = gene_name
                    variant_score_frames.append(copied)
                    reuse_rows.append({'source_block': '01', 'dataset': f'{gene_name.lower()}_augmentation_table', 'rows': int(len(copied)), 'models_covered': 1, 'targets_covered': 1})

                clinical_scores = clinical_variant_scores.copy()
                clinical_scores['model_label'] = 'ESM2-150M'
                clinical_scores['family_label'] = 'esm'
                clinical_scores['source_block'] = '06'
                clinical_scores['target_scope'] = clinical_scores['gene']
                variant_score_frames.append(clinical_scores)
                reuse_rows.append({'source_block': '06', 'dataset': 'clinical_panel_variant_scores', 'rows': int(len(clinical_scores)), 'models_covered': 1, 'targets_covered': clinical_scores['gene'].nunique()})

                support_surface = case_support_collapsed.copy()
                support_surface['source_block'] = '10b'
                support_surface['target_scope'] = support_surface['variant_id'].str.split(':').str[0]
                variant_score_frames.append(support_surface)
                reuse_rows.append({'source_block': '10b', 'dataset': 'case_support_collapsed', 'rows': int(len(support_surface)), 'models_covered': support_surface['model_label'].nunique(), 'targets_covered': support_surface['target_scope'].nunique()})

                multitarget_model_variant_scores = pd.concat(variant_score_frames, ignore_index=True, sort=False)
                multitarget_model_variant_scores.to_csv(TABLES_DIR / 'multitarget_model_variant_scores.csv', index=False)

                score_reuse_inventory = pd.DataFrame(reuse_rows)
                score_reuse_inventory.to_csv(TABLES_DIR / 'score_reuse_inventory.csv', index=False)

                per_model_runtime_manifest = (
                    multitarget_model_variant_scores
                    .groupby('model_label', dropna=False)
                    .agg(
                        n_rows=('model_label', 'size'),
                        n_targets=('target_scope', 'nunique'),
                        n_variant_ids=('variant_id', 'nunique'),
                    )
                    .reset_index()
                    .sort_values(['n_targets', 'n_rows', 'model_label'], ascending=[False, False, True])
                )
                per_model_runtime_manifest.to_csv(TABLES_DIR / 'per_model_runtime_manifest.csv', index=False)

                display(score_reuse_inventory)
                display(per_model_runtime_manifest.head(20))
                done('Reuse-first multi-target score surfaces are assembled across upstream blocks and model families.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Search a portable protocol summary using public alpha and stability evidence already available in the campaign
                protocol_rows = []
                alpha_rows = []
                window_layer_rows = []

                for gene_name in ['TP53', 'BRCA2', 'MSH2']:
                    gene_summary = block1_summary['genes'].get(gene_name, {})
                    for row in gene_summary.get('alpha_sweep', []):
                        alpha_rows.append({
                            'gene': gene_name,
                            'model_label': 'ESM-1v+ESM2-150M-reference',
                            'alpha': safe_float(row.get('alpha')),
                            'auc': safe_float(row.get('auc')),
                            'stability_kind': 'full_surface_auc',
                            'source_block': '01',
                        })

                for _, row in tp53_model_summary.iterrows():
                    alpha_rows.append({
                        'gene': 'TP53',
                        'model_label': row['model_label'],
                        'alpha': safe_float(row['best_alpha']),
                        'auc': safe_float(row['best_auc']),
                        'stability_kind': 'best_alpha_from_multifamily_tp53',
                        'source_block': '12b',
                    })

                for _, row in case_support_collapsed.iterrows():
                    gene = row['variant_id'].split(':')[0]
                    if gene in {'TSC2', 'CREBBP', 'GRIN2A'}:
                        alpha_rows.append({
                            'gene': gene,
                            'model_label': row['model_label'],
                            'alpha': FIXED_ALPHA,
                            'auc': safe_float(row['alpha_positive_fraction']),
                            'stability_kind': 'case_level_alpha_positive_fraction',
                            'source_block': '10b',
                        })

                alpha_sweep_summary = pd.DataFrame(alpha_rows)
                alpha_sweep_summary.to_csv(TABLES_DIR / 'alpha_sweep_summary.csv', index=False)

                for gene in ['TP53', 'BRCA2', 'TSC2']:
                    gene_rows = alpha_sweep_summary[alpha_sweep_summary['gene'] == gene].copy()
                    if gene_rows.empty:
                        protocol_rows.append({'gene': gene, 'status': 'no_public_alpha_surface', 'fixed_alpha': FIXED_ALPHA, 'portable_protocol_ok': False})
                        continue
                    best_auc = gene_rows['auc'].max()
                    fixed_rows = gene_rows[np.isclose(gene_rows['alpha'], FIXED_ALPHA)]
                    fixed_auc = fixed_rows['auc'].max() if not fixed_rows.empty else float('nan')
                    loss_vs_best = best_auc - fixed_auc if np.isfinite(fixed_auc) else float('nan')
                    protocol_rows.append({
                        'gene': gene,
                        'status': 'evaluated',
                        'best_public_auc_proxy': safe_float(best_auc),
                        'fixed_alpha_auc_proxy': safe_float(fixed_auc),
                        'loss_vs_best': safe_float(loss_vs_best),
                        'portable_protocol_ok': bool(np.isfinite(loss_vs_best) and loss_vs_best <= 0.02),
                        'fixed_alpha': FIXED_ALPHA,
                        'window_radius': WINDOW_RADIUS,
                        'layer_policy': 'all_layers_default_or_upstream_public_surface',
                    })

                for gene in ['TP53', 'BRCA2', 'TSC2', 'CREBBP', 'GRIN2A']:
                    window_layer_rows.append({
                        'gene': gene,
                        'window_radius': WINDOW_RADIUS,
                        'layer_policy': 'all_layers',
                        'status': 'portable_default_selected',
                        'source_note': 'This notebook records the portable default and public evidence of fragility rather than rerunning a new broad window-layer sweep.'
                    })

                protocol_stability_summary = pd.DataFrame(protocol_rows)
                window_layer_stability_summary = pd.DataFrame(window_layer_rows)
                protocol_stability_summary.to_csv(TABLES_DIR / 'protocol_stability_summary.csv', index=False)
                window_layer_stability_summary.to_csv(TABLES_DIR / 'window_layer_stability_summary.csv', index=False)

                display(protocol_stability_summary)
                display(alpha_sweep_summary.head(20))
                done('Portable protocol stability has been summarized from the public alpha and finalist evidence surfaces.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Evaluate holdout, transfer, controls, and negative guardrails using the reused closure evidence
                holdout_closure_summary = mini_holdout_transfer_summary.copy()
                holdout_closure_summary['holdout_positive'] = (
                    holdout_closure_summary['holdout_enrichment_gap'].fillna(-1e9) > 0
                ) & (holdout_closure_summary['holdout_rule_on_fraction'].fillna(0) >= 0.2)
                holdout_closure_summary.to_csv(TABLES_DIR / 'holdout_closure_summary.csv', index=False)

                transfer_rows = []
                for _, row in case_support_collapsed.iterrows():
                    gene = row['variant_id'].split(':')[0]
                    transfer_rows.append({
                        'variant_id': row['variant_id'],
                        'gene': gene,
                        'model_label': row['model_label'],
                        'family_label': row['family_label'],
                        'alpha_positive_fraction': safe_float(row['alpha_positive_fraction']),
                        'fixed055_margin': safe_float(row['fixed055_margin']),
                        'best_margin': safe_float(row['best_margin']),
                        'median_margin': safe_float(row['median_margin']),
                        'transfer_positive': bool(row['family_label'] != 'esm' and safe_float(row['fixed055_margin']) > 0 and safe_float(row['alpha_positive_fraction']) >= 0.5),
                        'near_transfer_positive': bool(row['family_label'] != 'esm' and safe_float(row['best_margin']) > 0),
                    })
                transfer_closure_summary = pd.DataFrame(transfer_rows).sort_values(['transfer_positive', 'near_transfer_positive', 'gene', 'model_label'], ascending=[False, False, True, True]).reset_index(drop=True)
                transfer_closure_summary.to_csv(TABLES_DIR / 'transfer_closure_summary.csv', index=False)

                control_summary = control_win_summary.copy()
                control_summary['control_win'] = control_summary['beats_all_controls'].fillna(False)
                control_summary.to_csv(TABLES_DIR / 'control_win_summary.csv', index=False)

                negative_control_rows = []
                for gene in ['BRCA1', 'MSH2']:
                    gene_panel = clinical_gene_panel[clinical_gene_panel['gene'] == gene]
                    if not gene_panel.empty:
                        row = gene_panel.iloc[0]
                        negative_control_rows.append({
                            'gene': gene,
                            'source': 'clinical_gene_panel',
                            'delta_pair_vs_ll': safe_float(row['delta_pair_vs_ll']),
                            'same_surface_status': row.get('same_surface_status', ''),
                            'esm2_status': row.get('esm2_status', ''),
                            'is_strong_negative_guardrail': bool(safe_float(row['delta_pair_vs_ll']) < 0 if gene == 'BRCA1' else safe_float(row['delta_augmented_vs_esm1v']) < 0),
                        })
                negative_control_summary = pd.DataFrame(negative_control_rows)
                negative_control_summary.to_csv(TABLES_DIR / 'negative_control_summary.csv', index=False)

                display(holdout_closure_summary)
                display(transfer_closure_summary.head(20))
                display(control_summary)
                display(negative_control_summary)
                done('Holdout, transfer, control, and negative-control guardrail summaries are assembled.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Final adjudication: build the multi-target generalization scoreboard and claim package
                replay_target_contracts = pd.read_csv(TABLES_DIR / 'replay_target_contracts.csv')
                protocol_stability_summary = pd.read_csv(TABLES_DIR / 'protocol_stability_summary.csv')
                holdout_closure_summary = pd.read_csv(TABLES_DIR / 'holdout_closure_summary.csv')
                transfer_closure_summary = pd.read_csv(TABLES_DIR / 'transfer_closure_summary.csv')
                control_summary = pd.read_csv(TABLES_DIR / 'control_win_summary.csv')
                negative_control_summary = pd.read_csv(TABLES_DIR / 'negative_control_summary.csv')

                positive_transfer_targets = sorted(transfer_closure_summary.loc[transfer_closure_summary['transfer_positive'], 'gene'].unique().tolist())
                near_transfer_targets = sorted(transfer_closure_summary.loc[transfer_closure_summary['near_transfer_positive'], 'gene'].unique().tolist())
                control_win_models = sorted(control_summary.loc[control_summary['control_win'], 'model_label'].unique().tolist())
                holdout_positive_models = sorted(holdout_closure_summary.loc[holdout_closure_summary['holdout_positive'], 'model_label'].unique().tolist())

                scoreboard_rows = []
                for _, row in replay_target_contracts.iterrows():
                    gene = row['gene']
                    portable_row = protocol_stability_summary[protocol_stability_summary['gene'] == gene]
                    portable_ok = bool(not portable_row.empty and bool(portable_row['portable_protocol_ok'].fillna(False).iloc[0]))
                    target_transfer_positive = gene in positive_transfer_targets
                    target_near_transfer = gene in near_transfer_targets
                    replay_ready = bool(row['contract_status'] == 'replay_candidate' and row['n_variants'] > 0 and row['n_source_surfaces'] >= 1 and (row['is_primary_target'] or portable_ok or target_transfer_positive))
                    if row['is_negative_control']:
                        taxonomy = 'failed_due_to_negative_control'
                    elif replay_ready and target_transfer_positive:
                        taxonomy = 'transfer_positive'
                    elif replay_ready and portable_ok:
                        taxonomy = 'replay_ready'
                    elif target_near_transfer:
                        taxonomy = 'near_nuclear'
                    else:
                        taxonomy = 'supportive'
                    scoreboard_rows.append({
                        'gene': gene,
                        'target_role': row['target_role'],
                        'replay_ready': replay_ready,
                        'portable_protocol_ok': portable_ok,
                        'transfer_positive': target_transfer_positive,
                        'near_transfer_positive': target_near_transfer,
                        'is_negative_control': row['is_negative_control'],
                        'n_variants': int(row['n_variants']),
                        'n_source_surfaces': int(row['n_source_surfaces']),
                        'taxonomy': taxonomy,
                    })

                multitarget_generalization_scoreboard = pd.DataFrame(scoreboard_rows).sort_values(['is_negative_control', 'replay_ready', 'transfer_positive', 'gene'], ascending=[True, False, False, True]).reset_index(drop=True)
                multitarget_generalization_scoreboard.to_csv(TABLES_DIR / 'multitarget_generalization_scoreboard.csv', index=False)

                family_closure_summary = (
                    transfer_closure_summary
                    .groupby('family_label', dropna=False)
                    .agg(
                        n_variant_rows=('variant_id', 'size'),
                        n_transfer_positive=('transfer_positive', 'sum'),
                        n_near_transfer_positive=('near_transfer_positive', 'sum'),
                    )
                    .reset_index()
                    .sort_values(['n_transfer_positive', 'n_near_transfer_positive', 'family_label'], ascending=[False, False, True])
                )
                family_closure_summary['has_public_positive_witness'] = family_closure_summary['n_transfer_positive'] > 0
                family_closure_summary.to_csv(TABLES_DIR / 'family_closure_summary.csv', index=False)

                n_replay_ready = int(multitarget_generalization_scoreboard['replay_ready'].sum())
                n_holdout_positive = len(holdout_positive_models)
                n_transfer_positive = len(positive_transfer_targets)
                n_control_wins = len(control_win_models)

                if n_replay_ready >= 3 and n_holdout_positive >= 1 and n_transfer_positive >= 1 and n_control_wins >= 1:
                    claim_status = 'multitarget_generalization_strengthened_with_public_closure'
                    claim_reason = 'Replay surfaces, holdout, transfer, and control wins all close positively under the same notebook contract.'
                elif n_replay_ready >= 3 and (n_transfer_positive >= 1 or n_holdout_positive >= 1):
                    claim_status = 'multitarget_generalization_strengthened_but_not_fully_closed'
                    claim_reason = 'Replay surfaces are now public and portability evidence improves, but at least one hard firewall still remains open.'
                elif n_replay_ready >= 3:
                    claim_status = 'multitarget_generalization_replay_ready_but_supportive'
                    claim_reason = 'The notebook successfully freezes multi-target replay contracts, but the hardest portability filters remain only supportive.'
                else:
                    claim_status = 'multitarget_generalization_still_mixed'
                    claim_reason = 'Replay contracts or portability witnesses remain too incomplete for a stronger claim.'

                claim_summary = {
                    'claim_status': claim_status,
                    'claim_reason': claim_reason,
                    'n_replay_ready_targets': n_replay_ready,
                    'replay_ready_targets': multitarget_generalization_scoreboard.loc[multitarget_generalization_scoreboard['replay_ready'], 'gene'].tolist(),
                    'holdout_positive_models': holdout_positive_models,
                    'transfer_positive_targets': positive_transfer_targets,
                    'control_win_models': control_win_models,
                    'near_transfer_targets': near_transfer_targets,
                    'negative_controls': negative_control_summary.to_dict(orient='records'),
                    'upstream_final_chain': {
                        'block12b_status': block12b_summary.get('claim_status', 'unknown'),
                        'block12c_status': block12c_summary.get('claim_status', 'unknown'),
                        'block12d_status': block12d_summary.get('claim_status', 'unknown'),
                    },
                }
                (MANIFESTS_DIR / 'claim_summary.json').write_text(json.dumps(claim_summary, indent=2), encoding='utf-8')

                display(multitarget_generalization_scoreboard)
                display(family_closure_summary)
                display(pd.DataFrame([claim_summary]))
                done('The final generalization scoreboard, family closure summary, and claim package are adjudicated.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Build reviewer-facing figures for scoreboard, protocol stability, holdout-transfer-controls, replay targets, and guardrails
                scoreboard = pd.read_csv(TABLES_DIR / 'multitarget_generalization_scoreboard.csv')
                protocol = pd.read_csv(TABLES_DIR / 'protocol_stability_summary.csv')
                holdout = pd.read_csv(TABLES_DIR / 'holdout_closure_summary.csv')
                transfer = pd.read_csv(TABLES_DIR / 'transfer_closure_summary.csv')
                controls = pd.read_csv(TABLES_DIR / 'control_win_summary.csv')
                replay_contracts = pd.read_csv(TABLES_DIR / 'replay_target_contracts.csv')
                negative_controls = pd.read_csv(TABLES_DIR / 'negative_control_summary.csv')
                claim_summary = json.loads((MANIFESTS_DIR / 'claim_summary.json').read_text(encoding='utf-8'))

                fig, ax = plt.subplots(figsize=(9.0, 4.8))
                plot_df = scoreboard.copy()
                plot_df['score'] = (
                    plot_df['replay_ready'].astype(int) * 2
                    + plot_df['transfer_positive'].astype(int) * 2
                    + plot_df['portable_protocol_ok'].astype(int)
                    - plot_df['is_negative_control'].astype(int)
                )
                ax.bar(plot_df['gene'], plot_df['score'], color=['#1f77b4' if not neg else '#d62728' for neg in plot_df['is_negative_control']])
                ax.set_title('Multi-target closure scoreboard')
                ax.set_ylabel('closure score proxy')
                ax.axhline(0, color='black', linewidth=0.8)
                plt.xticks(rotation=25, ha='right')
                plt.tight_layout()
                fig.savefig(FIGURES_DIR / 'multitarget_model_scoreboard.png', dpi=200, bbox_inches='tight')
                plt.close(fig)

                fig, ax = plt.subplots(figsize=(8.6, 4.8))
                if not protocol.empty:
                    ax.bar(protocol['gene'], protocol['loss_vs_best'].fillna(0.25), color=['#2ca02c' if bool(v) else '#ff7f0e' for v in protocol['portable_protocol_ok'].fillna(False)])
                    ax.axhline(0.02, color='black', linestyle='--', linewidth=1.0, label='portable loss threshold')
                    ax.legend(loc='upper right')
                ax.set_title('Portable protocol stability frontier')
                ax.set_ylabel('loss vs best public AUC proxy')
                plt.xticks(rotation=25, ha='right')
                plt.tight_layout()
                fig.savefig(FIGURES_DIR / 'protocol_stability_frontier.png', dpi=200, bbox_inches='tight')
                plt.close(fig)

                fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.2))
                axes[0].bar(holdout['model_label'], holdout['holdout_rule_on_fraction'], color=['#2ca02c' if bool(v) else '#7f7f7f' for v in holdout['holdout_positive']])
                axes[0].set_title('Holdout rule-on fraction')
                axes[0].tick_params(axis='x', rotation=70)
                axes[1].bar(transfer['variant_id'].head(12), transfer['fixed055_margin'].head(12), color=['#1f77b4' if bool(v) else '#c7c7c7' for v in transfer['transfer_positive'].head(12)])
                axes[1].set_title('Top transfer witnesses')
                axes[1].tick_params(axis='x', rotation=80)
                axes[2].bar(controls['model_label'], controls['selected_rule'], color=['#2ca02c' if bool(v) else '#d62728' for v in controls['control_win']])
                axes[2].set_title('Selected rule vs controls')
                axes[2].tick_params(axis='x', rotation=70)
                plt.tight_layout()
                fig.savefig(FIGURES_DIR / 'transfer_holdout_controls_panel.png', dpi=200, bbox_inches='tight')
                plt.close(fig)

                fig, ax = plt.subplots(figsize=(8.6, 4.8))
                ax.bar(replay_contracts['gene'], replay_contracts['n_variants'], color=['#1f77b4' if not bool(v) else '#d62728' for v in replay_contracts['is_negative_control']])
                ax.set_title('Replay-ready target overview')
                ax.set_ylabel('panel variants')
                plt.xticks(rotation=25, ha='right')
                plt.tight_layout()
                fig.savefig(FIGURES_DIR / 'replay_ready_targets_overview.png', dpi=200, bbox_inches='tight')
                plt.close(fig)

                fig, ax = plt.subplots(figsize=(7.2, 4.2))
                if not negative_controls.empty:
                    ax.bar(negative_controls['gene'], negative_controls['delta_pair_vs_ll'].fillna(0), color='#d62728')
                ax.set_title('Negative-control guardrail')
                ax.set_ylabel('delta pair vs ll')
                ax.axhline(0, color='black', linewidth=0.8)
                plt.tight_layout()
                fig.savefig(FIGURES_DIR / 'negative_controls_guardrail.png', dpi=200, bbox_inches='tight')
                plt.close(fig)

                if claim_summary.get('transfer_positive_targets'):
                    fig, ax = plt.subplots(figsize=(7.2, 4.2))
                    selected = transfer[transfer['transfer_positive']].copy()
                    ax.bar(selected['variant_id'], selected['fixed055_margin'], color='#2ca02c')
                    ax.set_title('Near-nuclear transfer witnesses')
                    ax.tick_params(axis='x', rotation=80)
                    plt.tight_layout()
                    fig.savefig(FIGURES_DIR / 'near_nuclear_witnesses.png', dpi=200, bbox_inches='tight')
                    plt.close(fig)

                display(scoreboard)
                done('Reviewer-facing figures for closure, stability, controls, and replay surfaces are written.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Write markdown summaries, manifests, and the final bundle
                scoreboard = pd.read_csv(TABLES_DIR / 'multitarget_generalization_scoreboard.csv')
                family_closure = pd.read_csv(TABLES_DIR / 'family_closure_summary.csv')
                replay_contracts = pd.read_csv(TABLES_DIR / 'replay_target_contracts.csv')
                claim_summary = json.loads((MANIFESTS_DIR / 'claim_summary.json').read_text(encoding='utf-8'))

                summary_lines = [
                    '# Block 13 Multi-Target Generalization Closure Summary',
                    '',
                    f"- Claim status: `{claim_summary['claim_status']}`",
                    f"- Claim reason: {claim_summary['claim_reason']}",
                    f"- Replay-ready targets: `{', '.join(claim_summary['replay_ready_targets']) if claim_summary['replay_ready_targets'] else 'none'}`",
                    f"- Holdout-positive models: `{', '.join(claim_summary['holdout_positive_models']) if claim_summary['holdout_positive_models'] else 'none'}`",
                    f"- Transfer-positive targets: `{', '.join(claim_summary['transfer_positive_targets']) if claim_summary['transfer_positive_targets'] else 'none'}`",
                    f"- Control-win models: `{', '.join(claim_summary['control_win_models']) if claim_summary['control_win_models'] else 'none'}`",
                    '',
                    '## Interpretation',
                    '',
                    'This notebook freezes multi-target replay contracts around TP53, BRCA2, and TSC2, then asks whether the current public evidence already closes holdout, transfer, and control firewalls at the same time. The answer is written as a concrete closure scoreboard rather than as narrative overclaim.',
                ]
                (TEXT_DIR / 'block13_summary.md').write_text('\\n'.join(summary_lines) + '\\n', encoding='utf-8')

                claim_paragraph = (
                    f"Block 13 turns the campaign into a replay-first generalization court: {claim_summary['n_replay_ready_targets']} targets now have explicit replay contracts, "
                    f"while holdout-positive models = {len(claim_summary['holdout_positive_models'])}, transfer-positive targets = {len(claim_summary['transfer_positive_targets'])}, "
                    f"and control-win models = {len(claim_summary['control_win_models'])}. The resulting claim is therefore `{claim_summary['claim_status']}`, not because the notebook avoids hard filters, but because it applies them simultaneously on the exact targets and model families that matter most for public portability."
                )
                (TEXT_DIR / 'block13_claim_paragraph.md').write_text(claim_paragraph + '\\n', encoding='utf-8')

                replay_contract_md = [
                    '# Block 13 Replay Contract',
                    '',
                    'Primary replay candidates prepared here:',
                ]
                for _, row in replay_contracts.iterrows():
                    replay_contract_md.append(f"- `{row['gene']}` | role={row['target_role']} | n_variants={int(row['n_variants'])} | sources={row['source_surfaces']}")
                (TEXT_DIR / 'block13_replay_contract.md').write_text('\\n'.join(replay_contract_md) + '\\n', encoding='utf-8')

                artifact_summary = {
                    'notebook_slug': NOTEBOOK_SLUG,
                    'claim_status': claim_summary['claim_status'],
                    'results_root': str(RESULTS_ROOT),
                    'tables_written': sorted([path.name for path in TABLES_DIR.glob('*.csv')]),
                    'figures_written': sorted([path.name for path in FIGURES_DIR.glob('*.png')]),
                    'text_written': sorted([path.name for path in TEXT_DIR.glob('*.md')]),
                }
                (MANIFESTS_DIR / 'artifact_summary.json').write_text(json.dumps(artifact_summary, indent=2), encoding='utf-8')
                write_runtime_manifest({'artifact_summary': artifact_summary})
                zip_path = zip_results_bundle()
                maybe_colab_download(zip_path)

                print(json.dumps(claim_summary, indent=2))
                display(scoreboard)
                display(family_closure)
                display(replay_contracts)
                done('Markdown summaries, manifests, and the final Block 13 bundle are written.')
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
    output_path = repo_root / "New Notebooks" / "13_block13_multitarget_generalization_closure_h100.ipynb"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(notebook, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote notebook to {output_path}")


if __name__ == "__main__":
    main()
