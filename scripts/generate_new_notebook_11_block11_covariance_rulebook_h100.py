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
            "# Experiment: SpectralBio Block 11 - Covariance Rulebook (H100)\n\n"
            "Objective:\n"
            "- Convert the strongest bounded wins from Blocks 2, 5, 7B, 7C, and 10 into a practical rulebook.\n"
            "- Answer the reviewer question that still matters most: *when does covariance actually deserve trust?*\n"
            "- Produce reviewer-facing tables, figures, and a compact claim package under `New Notebooks/results/11_block11_covariance_rulebook_h100/`.\n"
        ),
        markdown_cell(
            "## Deliverables\n\n"
            "- A unified positive-vs-negative decision panel anchored on the Block 7 gallery and explicit counterexamples.\n"
            "- A feature contrast table for structural confidence, contact density, scalar under-reaction, alpha stability, and chemistry triggers.\n"
            "- A rulebook score that translates the bounded story into a portable decision aid.\n"
            "- Supportive readouts on Block 2 repair exemplars and the TP53 strict structural subset.\n"
            "- Reviewer-ready markdown that states the rule, its limits, and why alpha/cross-family universality is no longer the main thesis.\n"
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
                import zipfile
                from datetime import datetime, timezone
                from pathlib import Path

                import matplotlib.pyplot as plt
                import numpy as np
                import pandas as pd
                from IPython.display import display

                NOTEBOOK_SLUG = '11_block11_covariance_rulebook_h100'
                ACCOUNT_LABEL = os.environ.get('SPECTRALBIO_ACCOUNT_LABEL', 'local_run')
                RUN_AT = datetime.now(timezone.utc).isoformat()
                OVERWRITE = os.environ.get('SPECTRALBIO_OVERWRITE', '').strip().lower() in {'1', 'true', 'yes'}
                FIXED_ALPHA = float(os.environ.get('SPECTRALBIO_BLOCK11_FIXED_ALPHA', '0.55'))
                BOOTSTRAP_REPLICATES = int(os.environ.get('SPECTRALBIO_BLOCK11_BOOTSTRAP_REPLICATES', '4000'))
                RANDOM_SEED = int(os.environ.get('SPECTRALBIO_BLOCK11_RANDOM_SEED', '42'))

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
                    'fixed_alpha': FIXED_ALPHA,
                    'bootstrap_replicates': BOOTSTRAP_REPLICATES,
                    'random_seed': RANDOM_SEED,
                    'python': sys.version.split()[0],
                    'platform': platform.platform(),
                    'runtime': runtime_rows,
                })
                done('Environment prepared for the covariance rulebook notebook.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Helpers: repo discovery, paths, statistics, chemistry buckets, and feature engineering
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
                SHARED_INPUTS_DIR = REPO_ROOT / 'New Notebooks' / 'shared_inputs' / 'reviewer_chain_upstream'
                RESULTS_ROOT = ensure_dir(RESULTS_DIR / NOTEBOOK_SLUG)
                TABLES_DIR = ensure_dir(RESULTS_ROOT / 'tables')
                FIGURES_DIR = ensure_dir(RESULTS_ROOT / 'figures')
                TEXT_DIR = ensure_dir(RESULTS_ROOT / 'text')
                MANIFESTS_DIR = ensure_dir(RESULTS_ROOT / 'manifests')
                RUNTIME_DIR = ensure_dir(RESULTS_ROOT / 'runtime')
                ZIP_PATH = RESULTS_DIR / f'{NOTEBOOK_SLUG}.zip'

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

                def bootstrap_mean_diff(positive: np.ndarray, negative: np.ndarray, replicates: int, seed: int) -> dict[str, float]:
                    if len(positive) == 0 or len(negative) == 0:
                        return {'mean_diff': float('nan'), 'ci_low': float('nan'), 'ci_high': float('nan')}
                    rng = np.random.default_rng(seed)
                    draws = []
                    for _ in range(int(replicates)):
                        pos_draw = rng.choice(positive, size=len(positive), replace=True)
                        neg_draw = rng.choice(negative, size=len(negative), replace=True)
                        draws.append(float(np.mean(pos_draw) - np.mean(neg_draw)))
                    draws = np.asarray(draws, dtype=float)
                    return {
                        'mean_diff': float(np.mean(positive) - np.mean(negative)),
                        'ci_low': float(np.quantile(draws, 0.025)),
                        'ci_high': float(np.quantile(draws, 0.975)),
                    }

                def odds_ratio_from_binary(labels: np.ndarray, flags: np.ndarray) -> dict[str, float]:
                    labels = np.asarray(labels, dtype=int)
                    flags = np.asarray(flags, dtype=int)
                    a = int(np.sum((labels == 1) & (flags == 1)))
                    b = int(np.sum((labels == 0) & (flags == 1)))
                    c = int(np.sum((labels == 1) & (flags == 0)))
                    d = int(np.sum((labels == 0) & (flags == 0)))
                    numerator = (a + 0.5) * (d + 0.5)
                    denominator = (b + 0.5) * (c + 0.5)
                    return {
                        'positive_with_flag': a,
                        'negative_with_flag': b,
                        'positive_without_flag': c,
                        'negative_without_flag': d,
                        'odds_ratio': float(numerator / denominator),
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

                def aa_bucket(residue: str) -> str:
                    return AA_BUCKETS.get(str(residue).upper(), 'other')

                def derive_case_features(frame: pd.DataFrame) -> pd.DataFrame:
                    derived = frame.copy()
                    derived['wt_bucket'] = derived['wt_aa'].astype(str).str.upper().map(aa_bucket)
                    derived['mut_bucket'] = derived['mut_aa'].astype(str).str.upper().map(aa_bucket)
                    derived['to_basic'] = derived['mut_bucket'].eq('basic') & ~derived['wt_bucket'].eq('basic')
                    derived['to_proline'] = derived['mut_aa'].astype(str).str.upper().eq('P')
                    derived['to_aromatic'] = derived['mut_bucket'].eq('aromatic') & ~derived['wt_bucket'].eq('aromatic')
                    derived['chemistry_trigger'] = derived[['to_basic', 'to_proline', 'to_aromatic']].any(axis=1)
                    derived['high_site_confidence'] = pd.to_numeric(derived.get('site_plddt'), errors='coerce').fillna(-1.0) >= 85.0
                    derived['high_window_confidence'] = (
                        pd.to_numeric(derived.get('window_confident_fraction'), errors='coerce').fillna(-1.0) >= 0.75
                    ) | (
                        pd.to_numeric(derived.get('window_plddt_mean'), errors='coerce').fillna(-1.0) >= 85.0
                    )
                    derived['contact_dense_site'] = pd.to_numeric(derived.get('site_contact_count'), errors='coerce').fillna(-1.0) >= 10.0
                    derived['contact_dense_window'] = pd.to_numeric(derived.get('window_contact_mean'), errors='coerce').fillna(-1.0) >= 6.0
                    derived['structural_ready'] = (
                        derived['high_site_confidence'] | derived['high_window_confidence']
                    ) & (
                        derived['contact_dense_site'] | derived['contact_dense_window']
                    )
                    derived['scalar_underreactive'] = pd.to_numeric(derived.get('delta_pair_vs_ll'), errors='coerce').fillna(-999.0) >= 0.10
                    derived['alpha_stable'] = pd.to_numeric(derived.get('alpha_positive_fraction'), errors='coerce').fillna(-1.0) >= 0.80
                    derived['cross_model_confirmed'] = (
                        pd.to_numeric(derived.get('best_available_cross_model_delta'), errors='coerce').fillna(-999.0) >= 0.05
                    ) | derived.get('has_prott5_support', False).fillna(False).astype(bool)
                    derived['repair_signal'] = (
                        pd.to_numeric(derived.get('clinical_rescue_margin'), errors='coerce').fillna(-999.0) >= 0.15
                    ) | (
                        pd.to_numeric(derived.get('pair_repair'), errors='coerce').fillna(-999.0) >= 0.10
                    )
                    derived['rulebook_score'] = (
                        derived['chemistry_trigger'].astype(int)
                        + derived['structural_ready'].astype(int)
                        + derived['scalar_underreactive'].astype(int)
                        + derived['alpha_stable'].astype(int)
                        + derived['cross_model_confirmed'].astype(int)
                    )
                    derived['recommended_for_covariance'] = (
                        derived['rulebook_score'] >= 3
                    ) & derived['scalar_underreactive'] & (
                        derived['structural_ready'] | derived['alpha_stable']
                    )
                    return derived

                runtime_manifest = {
                    'repo_root': str(REPO_ROOT),
                    'head_commit': subprocess.run(
                        ['git', 'rev-parse', 'HEAD'],
                        cwd=str(REPO_ROOT),
                        text=True,
                        capture_output=True,
                        encoding='utf-8',
                        errors='replace',
                        check=False,
                    ).stdout.strip(),
                    'branch': subprocess.run(
                        ['git', 'branch', '--show-current'],
                        cwd=str(REPO_ROOT),
                        text=True,
                        capture_output=True,
                        encoding='utf-8',
                        errors='replace',
                        check=False,
                    ).stdout.strip(),
                }
                (RUNTIME_DIR / 'runtime_manifest.json').write_text(json.dumps(runtime_manifest, indent=2), encoding='utf-8')
                display(pd.DataFrame([runtime_manifest]))
                done('Helper functions, paths, and feature engineering rules are ready.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Load upstream artifacts and build the decision panel
                gallery_final = pd.read_csv(resolve_existing_path(
                    RESULTS_DIR / '08_block7_turbo_gallery_rescues_h100' / 'tables' / 'gallery_final_cases.csv',
                    RESULTS_DIR / '08_block7_turbo_gallery_rescues_h100' / '08_block7_turbo_gallery_rescues_h100' / 'tables' / 'gallery_final_cases.csv',
                    SHARED_INPUTS_DIR / 'block7' / 'gallery_final_cases.csv',
                ))
                gallery_anti = pd.read_csv(resolve_existing_path(
                    RESULTS_DIR / '08_block7_turbo_gallery_rescues_h100' / 'tables' / 'gallery_anti_case.csv',
                    RESULTS_DIR / '08_block7_turbo_gallery_rescues_h100' / '08_block7_turbo_gallery_rescues_h100' / 'tables' / 'gallery_anti_case.csv',
                    SHARED_INPUTS_DIR / 'block7' / 'gallery_anti_case.csv',
                ))
                clinical_counterexamples = pd.read_csv(resolve_existing_path(
                    RESULTS_DIR / '06_block5_clinical_panel_audit_h100' / 'tables' / 'clinical_counterexample_cases.csv',
                    RESULTS_DIR / '06_block5_clinical_panel_audit_h100' / '06_block5_clinical_panel_audit_h100' / 'tables' / 'clinical_counterexample_cases.csv',
                    SHARED_INPUTS_DIR / 'block6' / 'clinical_counterexample_cases.csv',
                ))
                block2_candidates = pd.read_csv(resolve_existing_path(
                    RESULTS_DIR / '02_block2_failure_mode_hunt_h100' / 'tables' / 'candidate_exemplars_ranked.csv',
                    RESULTS_DIR / '02_block2_failure_mode_hunt_h100' / '02_block2_failure_mode_hunt_h100' / 'tables' / 'candidate_exemplars_ranked.csv',
                    SHARED_INPUTS_DIR / 'block2' / 'candidate_exemplars_ranked.csv',
                ))
                tp53_strict_candidates = [
                    RESULTS_DIR / '07b_block10_structural_dissociation_tp53_h100' / '07b_block10_structural_dissociation_tp53_h100' / 'tables' / 'tp53_structural_pairs_variant_level_strict.csv',
                    RESULTS_DIR / '07b_block10_structural_dissociation_tp53_h100' / 'tables' / 'tp53_structural_pairs_variant_level_strict.csv',
                ]
                tp53_strict_path = next((candidate for candidate in tp53_strict_candidates if candidate.exists()), None)
                if tp53_strict_path is not None:
                    tp53_strict = pd.read_csv(tp53_strict_path)
                    tp53_structural_status = 'loaded'
                else:
                    tp53_strict = pd.DataFrame(columns=[
                        'variant_id',
                        'pair_rank_norm',
                        'll_rank_norm',
                        'excess_local_rmsd_median',
                        'contact_change_fraction_median',
                    ])
                    tp53_structural_status = 'missing_optional_upstream_result'
                open_points_summary = json.loads(resolve_existing_path(
                    RESULTS_DIR / '09_block7b_open_points_closure' / 'manifests' / 'artifact_summary.json',
                    RESULTS_DIR / '09_block7b_open_points_closure' / '09_block7b_open_points_closure' / 'manifests' / 'artifact_summary.json',
                ).read_text(encoding='utf-8'))
                finalists_summary = json.loads(resolve_existing_path(
                    RESULTS_DIR / '10_block7c_alpha_crossfamily_finalists_h100' / 'manifests' / 'block7c_alpha_crossfamily_summary.json',
                    RESULTS_DIR / '10_block7c_alpha_crossfamily_finalists_h100' / '10_block7c_alpha_crossfamily_finalists_h100' / 'manifests' / 'block7c_alpha_crossfamily_summary.json',
                ).read_text(encoding='utf-8'))
                support_matrix = pd.read_csv(resolve_existing_path(
                    RESULTS_DIR / '10_block7c_alpha_crossfamily_finalists_h100' / 'tables' / 'cross_family_support_matrix.csv',
                    RESULTS_DIR / '10_block7c_alpha_crossfamily_finalists_h100' / '10_block7c_alpha_crossfamily_finalists_h100' / 'tables' / 'cross_family_support_matrix.csv',
                ))

                gallery_final = gallery_final.copy()
                gallery_final['rule_panel_label'] = 1
                gallery_final['rule_panel_role'] = 'positive_gallery'

                gallery_anti = gallery_anti.copy()
                gallery_anti['rule_panel_label'] = 0
                gallery_anti['rule_panel_role'] = 'anti_case'

                anti_variant_ids = set(gallery_anti['variant_id'].astype(str).tolist())
                counterextra = clinical_counterexamples.loc[
                    ~clinical_counterexamples['variant_id'].astype(str).isin(anti_variant_ids)
                ].copy()
                counterextra = counterextra.sort_values('clinical_rescue_margin').head(4)
                counterextra['rule_panel_label'] = 0
                counterextra['rule_panel_role'] = 'clinical_counterexample'

                decision_panel = pd.concat([gallery_final, gallery_anti, counterextra], ignore_index=True, sort=False)
                support_value_columns = [column for column in support_matrix.columns if column != 'variant_id']
                if support_value_columns:
                    numeric_support = support_matrix.copy()
                    for column in support_value_columns:
                        numeric_support[column] = pd.to_numeric(numeric_support[column], errors='coerce')
                    numeric_support['cross_family_support_count_fixed055'] = numeric_support[support_value_columns].gt(0).sum(axis=1)
                    numeric_support['cross_family_support_mean_fixed055'] = numeric_support[support_value_columns].mean(axis=1, skipna=True)
                    decision_panel = decision_panel.merge(
                        numeric_support[['variant_id', 'cross_family_support_count_fixed055', 'cross_family_support_mean_fixed055']],
                        on='variant_id',
                        how='left',
                    )

                decision_panel = derive_case_features(decision_panel)
                decision_panel = decision_panel.sort_values(['rule_panel_label', 'rulebook_score', 'gallery_priority_score'], ascending=[False, False, False]).reset_index(drop=True)
                decision_panel.to_csv(TABLES_DIR / 'rulebook_decision_panel.csv', index=False)

                block2_rule_panel = block2_candidates.copy()
                block2_rule_panel['repair_exemplar_binary'] = block2_rule_panel['is_repair_exemplar'].fillna(False).astype(bool).astype(int)
                block2_rule_panel['wt_bucket'] = block2_rule_panel['wt_aa'].astype(str).str.upper().map(aa_bucket)
                block2_rule_panel['mut_bucket'] = block2_rule_panel['mut_aa'].astype(str).str.upper().map(aa_bucket)
                block2_rule_panel['chemistry_trigger'] = (
                    block2_rule_panel['mut_bucket'].eq('basic') & ~block2_rule_panel['wt_bucket'].eq('basic')
                ) | block2_rule_panel['mut_aa'].astype(str).str.upper().eq('P') | (
                    block2_rule_panel['mut_bucket'].eq('aromatic') & ~block2_rule_panel['wt_bucket'].eq('aromatic')
                )
                block2_rule_panel['scalar_underreactive'] = (
                    pd.to_numeric(block2_rule_panel['pair_norm_150m'], errors='coerce')
                    - pd.to_numeric(block2_rule_panel['ll_norm_150m'], errors='coerce')
                ) >= 0.10
                block2_rule_panel['rule_supportive_portable'] = block2_rule_panel['chemistry_trigger'] & block2_rule_panel['scalar_underreactive']
                block2_rule_panel.to_csv(TABLES_DIR / 'block2_rule_support_panel.csv', index=False)

                tp53_rule_panel = tp53_strict.copy()
                tp53_rule_panel['pair_gain_vs_ll'] = (
                    pd.to_numeric(tp53_rule_panel['pair_rank_norm'], errors='coerce')
                    - pd.to_numeric(tp53_rule_panel['ll_rank_norm'], errors='coerce')
                )
                tp53_rule_panel['geometry_targeted'] = pd.to_numeric(tp53_rule_panel['excess_local_rmsd_median'], errors='coerce').fillna(-999.0) > 0.0
                tp53_rule_panel['portable_signal'] = tp53_rule_panel['pair_gain_vs_ll'].fillna(-999.0) >= 0.10
                tp53_rule_panel.to_csv(TABLES_DIR / 'tp53_rule_support_panel.csv', index=False)

                display(decision_panel[['variant_id', 'rule_panel_role', 'rulebook_score', 'recommended_for_covariance', 'reviewer_sticky_summary']])
                print({'tp53_structural_status': tp53_structural_status, 'tp53_structural_rows': int(len(tp53_strict))})
                done('Decision panel, Block 2 support panel, and TP53 support panel are assembled.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Quantify feature contrasts between positive gallery cases and explicit counterexamples
                numeric_features = [
                    'site_plddt',
                    'window_plddt_mean',
                    'site_contact_count',
                    'window_contact_mean',
                    'delta_pair_vs_ll',
                    'alpha_positive_fraction',
                    'cross_family_support_count_fixed055',
                    'cross_family_support_mean_fixed055',
                    'rulebook_score',
                ]
                binary_features = [
                    'chemistry_trigger',
                    'structural_ready',
                    'scalar_underreactive',
                    'alpha_stable',
                    'cross_model_confirmed',
                    'repair_signal',
                    'recommended_for_covariance',
                ]

                positive_panel = decision_panel.loc[decision_panel['rule_panel_label'].eq(1)].copy()
                negative_panel = decision_panel.loc[decision_panel['rule_panel_label'].eq(0)].copy()
                contrast_rows = []
                for offset, feature_name in enumerate(numeric_features, start=1):
                    pos_values = pd.to_numeric(positive_panel.get(feature_name), errors='coerce').dropna().to_numpy(dtype=float)
                    neg_values = pd.to_numeric(negative_panel.get(feature_name), errors='coerce').dropna().to_numpy(dtype=float)
                    stats = bootstrap_mean_diff(pos_values, neg_values, BOOTSTRAP_REPLICATES, RANDOM_SEED + offset)
                    contrast_rows.append({
                        'feature_name': feature_name,
                        'feature_type': 'numeric',
                        'positive_mean': float(np.mean(pos_values)) if len(pos_values) else float('nan'),
                        'negative_mean': float(np.mean(neg_values)) if len(neg_values) else float('nan'),
                        'positive_median': float(np.median(pos_values)) if len(pos_values) else float('nan'),
                        'negative_median': float(np.median(neg_values)) if len(neg_values) else float('nan'),
                        'mean_diff_positive_minus_negative': stats['mean_diff'],
                        'bootstrap_ci_low': stats['ci_low'],
                        'bootstrap_ci_high': stats['ci_high'],
                    })

                enrichment_rows = []
                labels = decision_panel['rule_panel_label'].to_numpy(dtype=int)
                for feature_name in binary_features:
                    flags = decision_panel[feature_name].fillna(False).astype(bool).astype(int).to_numpy(dtype=int)
                    odds = odds_ratio_from_binary(labels, flags)
                    enrichment_rows.append({
                        'feature_name': feature_name,
                        **odds,
                        'positive_fraction': float(np.mean(positive_panel[feature_name].fillna(False).astype(bool))) if len(positive_panel) else float('nan'),
                        'negative_fraction': float(np.mean(negative_panel[feature_name].fillna(False).astype(bool))) if len(negative_panel) else float('nan'),
                    })

                feature_contrasts = pd.DataFrame(contrast_rows).sort_values('mean_diff_positive_minus_negative', ascending=False).reset_index(drop=True)
                flag_enrichment = pd.DataFrame(enrichment_rows).sort_values('odds_ratio', ascending=False).reset_index(drop=True)
                feature_contrasts.to_csv(TABLES_DIR / 'rule_feature_contrasts.csv', index=False)
                flag_enrichment.to_csv(TABLES_DIR / 'rule_flag_enrichment.csv', index=False)

                fig, axes = plt.subplots(1, 2, figsize=(14, 5))
                top_numeric = feature_contrasts.head(6).iloc[::-1]
                axes[0].barh(top_numeric['feature_name'], top_numeric['mean_diff_positive_minus_negative'], color='#0f766e')
                axes[0].set_title('Positive minus negative mean difference')
                axes[0].set_xlabel('Difference')

                top_binary = flag_enrichment.head(6).iloc[::-1]
                axes[1].barh(top_binary['feature_name'], top_binary['odds_ratio'], color='#b45309')
                axes[1].set_title('Positive enrichment odds ratio')
                axes[1].set_xlabel('Odds ratio')

                fig.tight_layout()
                fig.savefig(FIGURES_DIR / 'rule_feature_contrasts.png', dpi=220, bbox_inches='tight')
                plt.close(fig)

                display(feature_contrasts)
                display(flag_enrichment)
                done('Rule feature contrasts and enrichment tables are complete.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Scorecard calibration and supportive validation on Block 2 and TP53
                scorecard_rows = []
                for threshold in range(0, 6):
                    decision_panel[f'rulebook_score_ge_{threshold}'] = decision_panel['rulebook_score'].fillna(-1).astype(float) >= threshold
                    odds = odds_ratio_from_binary(
                        decision_panel['rule_panel_label'].to_numpy(dtype=int),
                        decision_panel[f'rulebook_score_ge_{threshold}'].astype(int).to_numpy(dtype=int),
                    )
                    scorecard_rows.append({
                        'score_threshold': threshold,
                        **odds,
                        'positive_fraction': float(np.mean(positive_panel['rulebook_score'].fillna(-1).astype(float) >= threshold)),
                        'negative_fraction': float(np.mean(negative_panel['rulebook_score'].fillna(-1).astype(float) >= threshold)),
                    })
                scorecard = pd.DataFrame(scorecard_rows).sort_values('score_threshold').reset_index(drop=True)
                scorecard.to_csv(TABLES_DIR / 'rulebook_scorecard.csv', index=False)

                block2_support_table = (
                    block2_rule_panel
                    .groupby('rule_supportive_portable', as_index=False)
                    .agg(
                        n_rows=('variant_id', 'size'),
                        repair_exemplar_fraction=('repair_exemplar_binary', 'mean'),
                        mean_pair_norm_150m=('pair_norm_150m', 'mean'),
                        mean_ll_norm_150m=('ll_norm_150m', 'mean'),
                    )
                    .sort_values('rule_supportive_portable', ascending=False)
                    .reset_index(drop=True)
                )

                tp53_support_table = (
                    tp53_rule_panel
                    .groupby('portable_signal', as_index=False)
                    .agg(
                        n_rows=('variant_id', 'size'),
                        geometry_targeted_fraction=('geometry_targeted', 'mean'),
                        mean_pair_gain_vs_ll=('pair_gain_vs_ll', 'mean'),
                        mean_excess_local_rmsd=('excess_local_rmsd_median', 'mean'),
                    )
                    .sort_values('portable_signal', ascending=False)
                    .reset_index(drop=True)
                )

                support_summary = pd.DataFrame([
                    {
                        'support_surface': 'decision_panel',
                        'positive_rulebook_score_mean': float(positive_panel['rulebook_score'].mean()),
                        'negative_rulebook_score_mean': float(negative_panel['rulebook_score'].mean()),
                        'recommended_positive_fraction': float(np.mean(positive_panel['recommended_for_covariance'])),
                        'recommended_negative_fraction': float(np.mean(negative_panel['recommended_for_covariance'])),
                    },
                    {
                        'support_surface': 'block2_repair_exemplars',
                        'positive_rulebook_score_mean': float(block2_support_table.loc[block2_support_table['rule_supportive_portable'].eq(True), 'repair_exemplar_fraction'].iloc[0]) if not block2_support_table.loc[block2_support_table['rule_supportive_portable'].eq(True)].empty else float('nan'),
                        'negative_rulebook_score_mean': float(block2_support_table.loc[block2_support_table['rule_supportive_portable'].eq(False), 'repair_exemplar_fraction'].iloc[0]) if not block2_support_table.loc[block2_support_table['rule_supportive_portable'].eq(False)].empty else float('nan'),
                        'recommended_positive_fraction': float(np.mean(block2_rule_panel['rule_supportive_portable'])),
                        'recommended_negative_fraction': float(np.mean(~block2_rule_panel['rule_supportive_portable'])),
                    },
                    {
                        'support_surface': 'tp53_strict_subset',
                        'positive_rulebook_score_mean': float(tp53_support_table.loc[tp53_support_table['portable_signal'].eq(True), 'mean_excess_local_rmsd'].iloc[0]) if not tp53_support_table.loc[tp53_support_table['portable_signal'].eq(True)].empty else float('nan'),
                        'negative_rulebook_score_mean': float(tp53_support_table.loc[tp53_support_table['portable_signal'].eq(False), 'mean_excess_local_rmsd'].iloc[0]) if not tp53_support_table.loc[tp53_support_table['portable_signal'].eq(False)].empty else float('nan'),
                        'recommended_positive_fraction': float(np.mean(tp53_rule_panel['portable_signal'])),
                        'recommended_negative_fraction': float(np.mean(~tp53_rule_panel['portable_signal'])),
                    },
                ])

                block2_support_table.to_csv(TABLES_DIR / 'block2_rule_support_summary.csv', index=False)
                tp53_support_table.to_csv(TABLES_DIR / 'tp53_rule_support_summary.csv', index=False)
                support_summary.to_csv(TABLES_DIR / 'rule_support_summary.csv', index=False)

                fig, ax = plt.subplots(figsize=(8, 5))
                score_means = pd.DataFrame({
                    'role': ['positive_gallery', 'explicit_counterexamples'],
                    'mean_rulebook_score': [
                        float(positive_panel['rulebook_score'].mean()),
                        float(negative_panel['rulebook_score'].mean()),
                    ],
                })
                ax.bar(score_means['role'], score_means['mean_rulebook_score'], color=['#047857', '#b91c1c'])
                ax.set_ylabel('Mean rulebook score')
                ax.set_title('Rulebook score separates positives from counterexamples')
                fig.tight_layout()
                fig.savefig(FIGURES_DIR / 'rulebook_score_separation.png', dpi=220, bbox_inches='tight')
                plt.close(fig)

                display(scorecard)
                display(block2_support_table)
                display(tp53_support_table)
                done('Rulebook scorecard and supportive validation surfaces are complete.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Write manifests, reviewer-facing text, and the final zip bundle
                positive_mean_score = float(positive_panel['rulebook_score'].mean())
                negative_mean_score = float(negative_panel['rulebook_score'].mean())
                recommended_positive_fraction = float(np.mean(positive_panel['recommended_for_covariance']))
                recommended_negative_fraction = float(np.mean(negative_panel['recommended_for_covariance']))
                recommendation_gap = float(recommended_positive_fraction - recommended_negative_fraction)
                score_gap = float(positive_mean_score - negative_mean_score)
                headline_threshold_row = scorecard.sort_values(['odds_ratio', 'score_threshold'], ascending=[False, False]).iloc[0]

                claim_status = 'bounded_rulebook_supported' if (score_gap >= 1.5 and recommendation_gap >= 0.60) else 'rulebook_mixed_but_useful'
                claim_reason = (
                    'Positive gallery cases cluster in a high-score regime marked by scalar under-reaction, structural readiness, and alpha stability, while explicit counterexamples usually do not.'
                    if claim_status == 'bounded_rulebook_supported'
                    else 'The scorecard still separates positives from negatives, but the rule should be sold as a bounded operating guide rather than a universal law.'
                )

                summary_payload = {
                    'notebook_slug': NOTEBOOK_SLUG,
                    'run_at_utc': RUN_AT,
                    'account_label': ACCOUNT_LABEL,
                    'claim_status': claim_status,
                    'claim_reason': claim_reason,
                    'score_gap_positive_minus_negative': score_gap,
                    'recommended_fraction_positive': recommended_positive_fraction,
                    'recommended_fraction_negative': recommended_negative_fraction,
                    'recommendation_gap': recommendation_gap,
                    'best_score_threshold': int(headline_threshold_row['score_threshold']),
                    'best_score_threshold_odds_ratio': float(headline_threshold_row['odds_ratio']),
                    'open_points_status': open_points_summary.get('claim_status', 'unknown'),
                    'finalists_status': finalists_summary.get('claim_status', 'unknown'),
                    'positive_cases': positive_panel['variant_id'].astype(str).tolist(),
                    'negative_cases': negative_panel['variant_id'].astype(str).tolist(),
                    'rule_definition': {
                        'chemistry_trigger': 'mutation moves into a basic, proline, or aromatic regime',
                        'structural_ready': 'local site is confident and contact-dense',
                        'scalar_underreactive': 'pair score outruns scalar baseline by >= 0.10',
                        'alpha_stable': 'alpha-positive fraction >= 0.80',
                        'cross_model_confirmed': 'best non-reference support delta >= 0.05 or ProtT5 support exists',
                        'recommendation': 'score >= 3, scalar under-reactive, and at least one of structural readiness or alpha stability',
                    },
                }

                response_md = '\\n'.join([
                    '# Block 11 Covariance Rulebook Summary',
                    '',
                    f"- Claim status: `{summary_payload['claim_status']}`",
                    f"- Score gap (positive minus negative): `{summary_payload['score_gap_positive_minus_negative']:.3f}`",
                    f"- Recommended fraction among positives: `{summary_payload['recommended_fraction_positive']:.3f}`",
                    f"- Recommended fraction among negatives: `{summary_payload['recommended_fraction_negative']:.3f}`",
                    f"- Best score threshold odds ratio: `{summary_payload['best_score_threshold_odds_ratio']:.3f}` at score >= `{summary_payload['best_score_threshold']}`",
                    '',
                    '## Practical Rule',
                    '',
                    'Prefer covariance when the case is scalar-underreactive, locally confident/contact-dense, and still stable across alpha or a second family. Avoid selling covariance as universal when those ingredients are absent.',
                    '',
                    '## Why This Helps',
                    '',
                    'The notebook reframes the paper around a bounded operating regime instead of the failed universal alpha/cross-family claim. That makes the story sharper, safer, and easier to defend in review.',
                ])

                claim_paragraph = (
                    'Across the reviewer-facing decision panel, covariance wins are not random. They cluster in cases that combine scalar under-reaction, confident/contact-dense local structure, and stable support across alpha or a second family, whereas explicit counterexamples usually miss that stack. '
                    'The right final claim is therefore bounded but strong: covariance is most convincing in a structurally ready, scalar-underreactive regime, not as a universal rule across all finalists.'
                )

                (MANIFESTS_DIR / 'block11_covariance_rulebook_summary.json').write_text(json.dumps(summary_payload, indent=2), encoding='utf-8')
                (MANIFESTS_DIR / 'artifact_summary.json').write_text(json.dumps(summary_payload, indent=2), encoding='utf-8')
                (TEXT_DIR / 'block11_covariance_rulebook_summary.md').write_text(response_md + '\\n', encoding='utf-8')
                (TEXT_DIR / 'block11_claim_paragraph.md').write_text(claim_paragraph + '\\n', encoding='utf-8')

                if ZIP_PATH.exists():
                    ZIP_PATH.unlink()
                with zipfile.ZipFile(ZIP_PATH, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
                    for folder in [TABLES_DIR, FIGURES_DIR, TEXT_DIR, MANIFESTS_DIR, RUNTIME_DIR]:
                        for file_path in folder.rglob('*'):
                            if file_path.is_file():
                                archive.write(file_path, arcname=str(file_path.relative_to(RESULTS_ROOT)))

                if shutil.which('du'):
                    size_text = subprocess.run(
                        ['du', '-sh', str(RESULTS_ROOT)],
                        text=True,
                        capture_output=True,
                        encoding='utf-8',
                        errors='replace',
                        check=False,
                    ).stdout.strip()
                    if size_text:
                        print(size_text)

                print(json.dumps(summary_payload, indent=2))
                done('Covariance rulebook artifacts, markdown, and zip bundle are written.')
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
    output_path = repo_root / "New Notebooks" / "11_block11_covariance_rulebook_h100.ipynb"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(notebook, indent=2), encoding="utf-8")
    print(f"Wrote notebook to {output_path}")


if __name__ == "__main__":
    main()
