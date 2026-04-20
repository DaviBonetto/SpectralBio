from __future__ import annotations

import json
from pathlib import Path

from generate_new_notebook_12c_block12_covariance_adjudication_structural_closure_h100 import (
    build_notebook as build_12c_notebook,
    code_cell,
    dedent,
    markdown_cell,
)


OLD_SLUG = "12c_block12_covariance_adjudication_structural_closure_h100"
NEW_SLUG = "12d_block12_final_nuclear_localization_h100"
OLD_PREFIX = "SPECTRALBIO_BLOCK12C_"
NEW_PREFIX = "SPECTRALBIO_BLOCK12D_"


def _rewrite_base_source(source: str) -> str:
    updated = source.replace(OLD_SLUG, NEW_SLUG)
    updated = updated.replace(OLD_PREFIX, NEW_PREFIX)
    updated = updated.replace("Block 12C", "Block 12D")
    updated = updated.replace("block12c_", "block12d_")
    updated = updated.replace("import sys", "import shutil\nimport sys")
    updated = updated.replace(
        "ZIP_PATH = RESULTS_ROOT / f'{NOTEBOOK_SLUG}_bundle.zip'",
        "BUNDLE_ROOT = RESULTS_DIR / f'{NOTEBOOK_SLUG}_bundle'\nZIP_PATH = RESULTS_ROOT / f'{NOTEBOOK_SLUG}_bundle.zip'",
    )
    updated = updated.replace(
        "Environment prepared for Block 12C adjudication and structural closure.",
        "Environment prepared for Block 12D final localization and nuclear adjudication.",
    )
    updated = updated.replace(
        "Helpers, repo wiring, statistics, structural loaders, and optional live scoring adapters are ready.",
        "Helpers, repo wiring, statistics, structural loaders, and optional live scoring adapters are ready for the final localization pass.",
    )
    return updated


def build_notebook() -> dict:
    notebook = build_12c_notebook()
    cells = notebook["cells"]

    cells[0] = markdown_cell(
        "# Experiment: SpectralBio Block 12D - Final Nuclear Localization (H100)\n\n"
        "Objective:\n"
        "- Treat Block 12D as the **last notebook** and throw every legitimate adjudication tool at the remaining gap.\n"
        "- Start from the evidence already assembled in **12B** and **12C**, then search for a **localized covariance-native regime** that is strong enough to become nuclear even if the global claim stays bounded.\n"
        "- Force the notebook to answer the question the paper now hinges on: **is there at least one compact, coverage-aware, scalar-beating, structurally witnessed rescue regime that deserves primary status?**\n"
        "- Produce a final package under `New Notebooks/results/12d_block12_final_nuclear_localization_h100/` with tables, figures, manifests, and a bundle ready for reviewer-facing use.\n"
    )

    cells[1] = markdown_cell(
        "## Final Contract\n\n"
        "- Block 12C showed that the story is stronger than a single checkpoint but still not nuclear at the global level.\n"
        "- Block 12D therefore changes the target from **global universality** to **localized nuclearization** under a stricter but more honest contract.\n"
        "- A model may now win the primary claim only if a **localized panel** survives all of the following together:\n"
        "  1. a coverage floor computed on the localized panel,\n"
        "  2. positive covariance enrichment,\n"
        "  3. wins over global scalar matched controls,\n"
        "  4. wins over local scalar matched controls,\n"
        "  5. wins over chemistry-only controls,\n"
        "  6. same-position evidence that is positive, tied, or genuinely not applicable,\n"
        "  7. a structural witness from the strict TP53 layer.\n"
        "- The notebook is allowed to conclude that the best final claim is **localized and bounded**, but it is not allowed to hide behind weak controls or empty transfer stories.\n"
    )

    for idx in (2, 3):
        source = "".join(cells[idx]["source"])
        cells[idx]["source"] = _rewrite_base_source(source).splitlines(keepends=True)

    cells[4:] = [
        code_cell(
            dedent(
                """
                # Load Block 12B and 12C artifacts, then define localized witness panels and final adjudication helpers
                BLOCK12B_ROOT = RESULTS_DIR / BLOCK12B_SLUG
                BLOCK12B_TABLES_DIR = BLOCK12B_ROOT / 'tables'
                BLOCK12C_SLUG = '12c_block12_covariance_adjudication_structural_closure_h100'
                BLOCK12C_ROOT_CANDIDATES = [
                    RESULTS_DIR / BLOCK12C_SLUG,
                    RESULTS_DIR / f'{BLOCK12C_SLUG}_bundle',
                ]
                BLOCK12B_LIVE_SCORES_DIR = BLOCK12B_ROOT / 'live_scores'

                LOCAL_MIN_RULE_ON_ABS = int(os.environ.get('SPECTRALBIO_BLOCK12D_LOCAL_MIN_RULE_ON_ABS', '6'))
                LOCAL_MIN_RULE_ON_FRAC = float(os.environ.get('SPECTRALBIO_BLOCK12D_LOCAL_MIN_RULE_ON_FRAC', '0.08'))
                PAIR_THRESHOLDS = [
                    float(item.strip())
                    for item in os.environ.get('SPECTRALBIO_BLOCK12D_PAIR_THRESHOLDS', '0.05,0.10,0.15,0.20,0.25,0.30').split(',')
                    if item.strip()
                ]

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

                def resolve_block12c_tables() -> tuple[dict[str, Path] | None, Path | None]:
                    for root in BLOCK12C_ROOT_CANDIDATES:
                        tables_dir = root / 'tables'
                        manifests_dir = root / 'manifests'
                        required = {
                            'adjudication': tables_dir / 'tp53_covariance_adjudication_summary.csv',
                            'structural': tables_dir / 'tp53_structural_closure_summary.csv',
                            'artifact_summary': manifests_dir / 'artifact_summary.json',
                        }
                        if all(path.exists() for path in required.values()):
                            return required, root
                    return None, None

                required_12c_tables, resolved_block12c_root = resolve_block12c_tables()
                missing_12c = [] if required_12c_tables is not None else ['adjudication', 'structural', 'artifact_summary']
                if missing_12c:
                    raise FileNotFoundError(
                        f'Missing required Block 12C outputs: {missing_12c}. '
                        f'Looked in {[str(path) for path in BLOCK12C_ROOT_CANDIDATES]}. '
                        f'Run {BLOCK12C_SLUG} before Block 12D.'
                    )
                BLOCK12C_TABLES_DIR = resolved_block12c_root / 'tables'
                BLOCK12C_MANIFESTS_DIR = resolved_block12c_root / 'manifests'

                variant_scores_12b = pd.read_csv(required_12b_tables['variant_scores'])
                model_summary_12b = pd.read_csv(required_12b_tables['model_summary'])
                calibration_12b = pd.read_csv(required_12b_tables['calibration'])
                selected_rules_12b = pd.read_csv(required_12b_tables['selected_rules'])
                control_table_12b = pd.read_csv(required_12b_tables['controls'])
                same_position_12b = pd.read_csv(required_12b_tables['same_position'])
                robustness_12b = pd.read_csv(required_12b_tables['robustness'])
                failure_12b = pd.read_csv(required_12b_tables['failure'])
                covariance_12c = pd.read_csv(required_12c_tables['adjudication'])
                structural_12c = pd.read_csv(required_12c_tables['structural'])

                block12c_artifact_summary = json.loads(required_12c_tables['artifact_summary'].read_text(encoding='utf-8'))

                structural_reference, structural_source_path, structural_source_kind = load_structural_reference()
                structural_positions_zero_based = sorted(
                    {
                        int(value) - 1
                        for value in pd.to_numeric(structural_reference.get('position_1', pd.Series(dtype=float)), errors='coerce').dropna().astype(int).tolist()
                    }
                )
                structural_variant_ids = set(structural_reference.get('variant_id', pd.Series(dtype=str)).astype(str).tolist())

                variant_scores_12b = variant_scores_12b.copy()
                if 'pair_rank_fixed_055' not in variant_scores_12b.columns:
                    variant_scores_12b['pair_rank_fixed_055'] = (
                        FIXED_ALPHA * pd.to_numeric(variant_scores_12b['frob_rank_norm'], errors='coerce').fillna(0.0)
                        + (1.0 - FIXED_ALPHA) * pd.to_numeric(variant_scores_12b['ll_rank_norm'], errors='coerce').fillna(0.0)
                    )
                if 'pair_minus_ll' not in variant_scores_12b.columns:
                    variant_scores_12b['pair_minus_ll'] = (
                        pd.to_numeric(variant_scores_12b['pair_rank_fixed_055'], errors='coerce').fillna(0.0)
                        - pd.to_numeric(variant_scores_12b['ll_rank_norm'], errors='coerce').fillna(0.0)
                    )
                variant_scores_12b['tp53_domain'] = variant_scores_12b['position'].astype(int).map(tp53_domain_label)
                variant_scores_12b['panel_full_tp53'] = True
                variant_scores_12b['panel_dna_binding_core'] = variant_scores_12b['tp53_domain'].eq('dna_binding')
                variant_scores_12b['panel_hotspot_core'] = variant_scores_12b['tp53_hotspot'].fillna(False).astype(bool)
                variant_scores_12b['panel_dna_binding_plus_hotspot'] = (
                    variant_scores_12b['panel_dna_binding_core'] | variant_scores_12b['panel_hotspot_core']
                )
                variant_scores_12b['panel_structural_positions'] = variant_scores_12b['position'].astype(int).isin(structural_positions_zero_based)
                variant_scores_12b['panel_localized_union'] = (
                    variant_scores_12b['panel_dna_binding_core']
                    | variant_scores_12b['panel_hotspot_core']
                    | variant_scores_12b['panel_structural_positions']
                )

                target_panel_specs = [
                    {
                        'panel_name': 'full_tp53',
                        'panel_column': 'panel_full_tp53',
                        'scope_label': 'global',
                        'preferred_same_position_mode': 'global',
                    },
                    {
                        'panel_name': 'dna_binding_core',
                        'panel_column': 'panel_dna_binding_core',
                        'scope_label': 'localized',
                        'preferred_same_position_mode': 'selected_positions',
                    },
                    {
                        'panel_name': 'dna_binding_plus_hotspot',
                        'panel_column': 'panel_dna_binding_plus_hotspot',
                        'scope_label': 'localized',
                        'preferred_same_position_mode': 'selected_positions',
                    },
                    {
                        'panel_name': 'localized_union',
                        'panel_column': 'panel_localized_union',
                        'scope_label': 'localized',
                        'preferred_same_position_mode': 'selected_positions',
                    },
                ]

                def local_coverage_floor(n_variants: int) -> int:
                    return max(LOCAL_MIN_RULE_ON_ABS, int(math.ceil(float(n_variants) * LOCAL_MIN_RULE_ON_FRAC)))

                def top_n_mask_from_scores(frame: pd.DataFrame, score_column: str, n: int) -> pd.Series:
                    if n <= 0 or frame.empty:
                        return pd.Series(np.zeros(len(frame), dtype=bool), index=frame.index)
                    ranked = pd.to_numeric(frame[score_column], errors='coerce').fillna(-999.0)
                    top_index = ranked.sort_values(ascending=False).index[: min(n, len(frame))]
                    return pd.Series(frame.index.isin(top_index), index=frame.index)

                def enrichment_gap_for_mask(frame: pd.DataFrame, mask: pd.Series, seed: int) -> dict:
                    mask_series = pd.Series(mask, index=frame.index).fillna(False).astype(bool)
                    labels = frame['label'].astype(int).to_numpy()
                    gap_stats = bootstrap_gap(labels, mask_series.to_numpy(), BOOTSTRAP_REPLICATES, seed)
                    odds = odds_ratio_from_mask(labels, mask_series.to_numpy())
                    return {
                        **gap_stats,
                        'odds_ratio': odds['odds_ratio'],
                        'positive_with_rule': odds['positive_with_rule'],
                        'negative_with_rule': odds['negative_with_rule'],
                        'positive_without_rule': odds['positive_without_rule'],
                        'negative_without_rule': odds['negative_without_rule'],
                    }

                def chemistry_gap_for_panel(frame: pd.DataFrame, seed: int) -> dict:
                    chemistry_mask = frame['chemistry_trigger'].fillna(False).astype(bool)
                    if chemistry_mask.sum() == 0 or (~chemistry_mask).sum() == 0:
                        return {'enrichment_gap': float('nan')}
                    return enrichment_gap_for_mask(frame, chemistry_mask, seed + 701)

                def same_position_witness(frame: pd.DataFrame, candidate_mask: pd.Series, mode: str) -> dict:
                    if candidate_mask.sum() == 0:
                        return {
                            'verdict': 'not_applicable',
                            'n_mixed_positions': 0,
                            'pair_top_hit_rate': float('nan'),
                            'll_top_hit_rate': float('nan'),
                            'delta': float('nan'),
                        }
                    if mode == 'selected_positions':
                        working = frame.loc[frame['position'].isin(frame.loc[candidate_mask, 'position'].astype(int).tolist())].copy()
                    else:
                        working = frame.copy()

                    pair_hits = []
                    ll_hits = []
                    mixed_positions = 0
                    for _, group in working.groupby('position'):
                        labels = group['label'].astype(int)
                        if labels.nunique() < 2:
                            continue
                        pair_values = pd.to_numeric(group['pair_minus_ll'], errors='coerce')
                        ll_values = pd.to_numeric(group['ll_rank_norm'], errors='coerce')
                        if pair_values.notna().sum() == 0 or ll_values.notna().sum() == 0:
                            continue
                        pair_idx = pair_values.idxmax()
                        ll_idx = ll_values.idxmax()
                        pair_hits.append(int(group.loc[pair_idx, 'label']))
                        ll_hits.append(int(group.loc[ll_idx, 'label']))
                        mixed_positions += 1

                    if mixed_positions == 0:
                        return {
                            'verdict': 'not_applicable',
                            'n_mixed_positions': 0,
                            'pair_top_hit_rate': float('nan'),
                            'll_top_hit_rate': float('nan'),
                            'delta': float('nan'),
                        }

                    pair_rate = float(np.mean(pair_hits))
                    ll_rate = float(np.mean(ll_hits))
                    delta = pair_rate - ll_rate
                    if delta > 1e-9:
                        verdict = 'win'
                    elif delta < -1e-9:
                        verdict = 'lose'
                    else:
                        verdict = 'tie'
                    return {
                        'verdict': verdict,
                        'n_mixed_positions': mixed_positions,
                        'pair_top_hit_rate': pair_rate,
                        'll_top_hit_rate': ll_rate,
                        'delta': delta,
                    }

                structural_summary_by_model = structural_12c.set_index('model_label').to_dict(orient='index')

                def structural_witness_for_model(model_label: str) -> dict:
                    row = structural_summary_by_model.get(model_label, {})
                    pair_spearman = safe_float(row.get('spearman_pair_minus_ll_vs_excess_local_rmsd'), float('nan'))
                    ll_spearman = safe_float(row.get('spearman_ll_rank_vs_excess_local_rmsd'), float('nan'))
                    geometry_gap = safe_float(row.get('structural_geometry_gap'), float('nan'))
                    positive = False
                    if math.isfinite(pair_spearman) and math.isfinite(ll_spearman) and pair_spearman > ll_spearman:
                        positive = True
                    if math.isfinite(geometry_gap) and geometry_gap > 0:
                        positive = True
                    if positive:
                        verdict = 'positive'
                    elif math.isfinite(pair_spearman) or math.isfinite(ll_spearman) or math.isfinite(geometry_gap):
                        verdict = 'negative'
                    else:
                        verdict = 'missing'
                    return {
                        'verdict': verdict,
                        'pair_spearman': pair_spearman,
                        'll_spearman': ll_spearman,
                        'geometry_gap': geometry_gap,
                        'n_structural_rows': int(row.get('n_structural_rows', 0)) if row else 0,
                    }

                model_context_rows = []
                covariance_context = covariance_12c.set_index('model_label').to_dict(orient='index')
                selected_rule_context = selected_rules_12b.set_index('model_label').to_dict(orient='index')
                for spec in MODEL_SPECS:
                    model_label = spec['model_label']
                    structural_witness = structural_witness_for_model(model_label)
                    covariance_row = covariance_context.get(model_label, {})
                    selected_row = selected_rule_context.get(model_label, {})
                    model_context_rows.append({
                        'model_label': model_label,
                        'family_label': spec['family_label'],
                        'architecture_kind': spec['architecture_kind'],
                        'block12c_status': str(covariance_row.get('adjudication_status', 'missing')),
                        'block12c_reason': str(covariance_row.get('adjudication_reason', 'missing')),
                        'block12b_selected_rule_type': str(selected_row.get('rule_type', 'missing')),
                        'block12b_selected_gap': safe_float(selected_row.get('enrichment_gap'), float('nan')),
                        'structural_witness_verdict': structural_witness['verdict'],
                        'structural_pair_spearman': structural_witness['pair_spearman'],
                        'structural_ll_spearman': structural_witness['ll_spearman'],
                        'structural_geometry_gap': structural_witness['geometry_gap'],
                        'structural_rows': structural_witness['n_structural_rows'],
                    })

                model_context_table = pd.DataFrame(model_context_rows).sort_values(
                    ['structural_witness_verdict', 'block12c_status', 'model_label'],
                    ascending=[True, True, True],
                ).reset_index(drop=True)

                model_context_table.to_csv(TABLES_DIR / 'tp53_block12d_model_context.csv', index=False)
                display(model_context_table)
                done('Block 12B and 12C artifacts are loaded, localized witness panels are defined, and the final search helpers are ready.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Search the final localized rule space and identify whether a bounded nuclear regime exists
                candidate_rows = []

                rule_templates = [
                    {
                        'rule_family': 'pair_only',
                        'threshold_source': 'pair_minus_ll',
                        'gate_name': 'none',
                        'gate_fn': lambda frame: pd.Series(np.ones(len(frame), dtype=bool), index=frame.index),
                    },
                    {
                        'rule_family': 'pair_only',
                        'threshold_source': 'pair_minus_ll',
                        'gate_name': 'exclude_chemistry',
                        'gate_fn': lambda frame: ~frame['chemistry_trigger'].fillna(False).astype(bool),
                    },
                    {
                        'rule_family': 'pair_only',
                        'threshold_source': 'pair_minus_ll',
                        'gate_name': 'structural_or_hotspot',
                        'gate_fn': lambda frame: (
                            frame['panel_structural_positions'].fillna(False).astype(bool)
                            | frame['panel_hotspot_core'].fillna(False).astype(bool)
                        ),
                    },
                    {
                        'rule_family': 'pair_rank_fixed',
                        'threshold_source': 'pair_rank_fixed_055',
                        'gate_name': 'none',
                        'gate_fn': lambda frame: pd.Series(np.ones(len(frame), dtype=bool), index=frame.index),
                    },
                ]

                for spec_index, spec in enumerate(MODEL_SPECS):
                    model_label = spec['model_label']
                    model_frame = variant_scores_12b.loc[variant_scores_12b['model_label'].eq(model_label)].copy().reset_index(drop=True)
                    if model_frame.empty:
                        continue

                    labels_full = model_frame['label'].astype(int).to_numpy()
                    structural_witness = structural_witness_for_model(model_label)

                    for panel_index, panel_spec in enumerate(target_panel_specs):
                        panel_mask = model_frame[panel_spec['panel_column']].fillna(False).astype(bool)
                        panel_frame = model_frame.loc[panel_mask].copy().reset_index(drop=True)
                        if panel_frame.empty:
                            continue
                        panel_size = int(len(panel_frame))
                        coverage_target = local_coverage_floor(panel_size) if panel_spec['scope_label'] == 'localized' else coverage_floor(panel_size)
                        chemistry_local = chemistry_gap_for_panel(panel_frame, RANDOM_SEED + spec_index * 1000 + panel_index * 100)

                        for template_index, template in enumerate(rule_templates):
                            threshold_values = PAIR_THRESHOLDS if template['threshold_source'] != 'pair_rank_fixed_055' else [0.55, 0.60, 0.65, 0.70, 0.75]
                            base_gate = template['gate_fn'](panel_frame).fillna(False).astype(bool)

                            for threshold in threshold_values:
                                score_values = pd.to_numeric(panel_frame[template['threshold_source']], errors='coerce').fillna(-999.0)
                                candidate_mask = base_gate & score_values.ge(float(threshold))
                                n_rule_on = int(candidate_mask.sum())
                                if n_rule_on <= 0 or n_rule_on >= len(panel_frame):
                                    continue

                                gap_stats = enrichment_gap_for_mask(
                                    panel_frame,
                                    candidate_mask,
                                    RANDOM_SEED + spec_index * 1000 + panel_index * 100 + template_index * 10 + int(round(float(threshold) * 100)),
                                )
                                global_scalar_gap = enrichment_gap_for_mask(
                                    model_frame,
                                    top_n_mask_from_scores(model_frame, 'll_rank_norm', n_rule_on),
                                    RANDOM_SEED + 5000 + spec_index * 100 + n_rule_on,
                                )['enrichment_gap']
                                local_scalar_gap = enrichment_gap_for_mask(
                                    panel_frame,
                                    top_n_mask_from_scores(panel_frame, 'll_rank_norm', n_rule_on),
                                    RANDOM_SEED + 6000 + panel_index * 100 + n_rule_on,
                                )['enrichment_gap']
                                local_pair_baseline_gap = enrichment_gap_for_mask(
                                    panel_frame,
                                    top_n_mask_from_scores(panel_frame, template['threshold_source'], n_rule_on),
                                    RANDOM_SEED + 7000 + template_index * 100 + n_rule_on,
                                )['enrichment_gap']
                                same_position = same_position_witness(
                                    panel_frame,
                                    candidate_mask,
                                    panel_spec['preferred_same_position_mode'],
                                )

                                beats_global_scalar = (
                                    math.isfinite(gap_stats['enrichment_gap'])
                                    and math.isfinite(global_scalar_gap)
                                    and gap_stats['enrichment_gap'] > global_scalar_gap
                                )
                                beats_local_scalar = (
                                    math.isfinite(gap_stats['enrichment_gap'])
                                    and math.isfinite(local_scalar_gap)
                                    and gap_stats['enrichment_gap'] > local_scalar_gap
                                )
                                beats_local_chemistry = (
                                    math.isfinite(gap_stats['enrichment_gap'])
                                    and math.isfinite(chemistry_local['enrichment_gap'])
                                    and gap_stats['enrichment_gap'] > chemistry_local['enrichment_gap']
                                )
                                same_position_ok = same_position['verdict'] in {'win', 'tie', 'not_applicable'}
                                structural_ok = structural_witness['verdict'] == 'positive'
                                coverage_pass = bool(n_rule_on >= coverage_target)
                                gap_positive = math.isfinite(gap_stats['enrichment_gap']) and gap_stats['enrichment_gap'] > 0

                                if (
                                    panel_spec['scope_label'] == 'localized'
                                    and coverage_pass
                                    and gap_positive
                                    and beats_global_scalar
                                    and beats_local_scalar
                                    and (beats_local_chemistry or not math.isfinite(chemistry_local['enrichment_gap']))
                                    and same_position_ok
                                    and structural_ok
                                    and template['rule_family'] == 'pair_only'
                                ):
                                    adjudication_status = 'nuclear_localized'
                                    adjudication_reason = 'localized_pair_rule_beats_global_and_local_scalar_with_structural_witness'
                                elif (
                                    coverage_pass
                                    and gap_positive
                                    and beats_local_scalar
                                    and same_position_ok
                                ):
                                    adjudication_status = 'supportive_localized'
                                    adjudication_reason = 'localized_rule_positive_but_not_fully_nuclear'
                                elif coverage_pass and gap_positive:
                                    adjudication_status = 'supportive_residual'
                                    adjudication_reason = 'positive_gap_without_full_control_dominance'
                                else:
                                    adjudication_status = 'not_eligible'
                                    adjudication_reason = 'coverage_or_control_failure'

                                candidate_rows.append({
                                    'model_label': model_label,
                                    'family_label': spec['family_label'],
                                    'architecture_kind': spec['architecture_kind'],
                                    'panel_name': panel_spec['panel_name'],
                                    'scope_label': panel_spec['scope_label'],
                                    'panel_size': panel_size,
                                    'coverage_target': coverage_target,
                                    'coverage_pass': coverage_pass,
                                    'rule_family': template['rule_family'],
                                    'gate_name': template['gate_name'],
                                    'threshold_source': template['threshold_source'],
                                    'threshold': float(threshold),
                                    'n_rule_on': n_rule_on,
                                    'fraction_rule_on': float(n_rule_on / float(panel_size)),
                                    'enrichment_gap': gap_stats['enrichment_gap'],
                                    'gap_ci_low': gap_stats['gap_ci_low'],
                                    'gap_ci_high': gap_stats['gap_ci_high'],
                                    'odds_ratio': gap_stats['odds_ratio'],
                                    'global_scalar_gap': global_scalar_gap,
                                    'local_scalar_gap': local_scalar_gap,
                                    'local_pair_baseline_gap': local_pair_baseline_gap,
                                    'local_chemistry_gap': chemistry_local['enrichment_gap'],
                                    'beats_global_scalar': bool(beats_global_scalar),
                                    'beats_local_scalar': bool(beats_local_scalar),
                                    'beats_local_chemistry': bool(beats_local_chemistry) if math.isfinite(chemistry_local['enrichment_gap']) else True,
                                    'same_position_verdict': same_position['verdict'],
                                    'same_position_n_mixed_positions': same_position['n_mixed_positions'],
                                    'same_position_pair_top_hit_rate': same_position['pair_top_hit_rate'],
                                    'same_position_ll_top_hit_rate': same_position['ll_top_hit_rate'],
                                    'same_position_delta': same_position['delta'],
                                    'structural_witness_verdict': structural_witness['verdict'],
                                    'structural_pair_spearman': structural_witness['pair_spearman'],
                                    'structural_ll_spearman': structural_witness['ll_spearman'],
                                    'structural_geometry_gap': structural_witness['geometry_gap'],
                                    'block12c_status': covariance_context.get(model_label, {}).get('adjudication_status', 'missing'),
                                    'adjudication_status': adjudication_status,
                                    'adjudication_reason': adjudication_reason,
                                })

                localized_rule_search = pd.DataFrame(candidate_rows)
                if localized_rule_search.empty:
                    raise RuntimeError('Block 12D did not generate any candidate rules.')

                status_rank = {
                    'nuclear_localized': 0,
                    'supportive_localized': 1,
                    'supportive_residual': 2,
                    'not_eligible': 3,
                }
                localized_rule_search['status_rank'] = localized_rule_search['adjudication_status'].map(status_rank).fillna(9).astype(int)
                localized_rule_search['same_position_rank'] = localized_rule_search['same_position_verdict'].map(
                    {'win': 0, 'tie': 1, 'not_applicable': 2, 'lose': 3}
                ).fillna(4).astype(int)

                localized_best_rules = localized_rule_search.sort_values(
                    [
                        'status_rank',
                        'same_position_rank',
                        'enrichment_gap',
                        'structural_geometry_gap',
                        'n_rule_on',
                    ],
                    ascending=[True, True, False, False, True],
                ).groupby('model_label', as_index=False).first()

                nuclear_localized = localized_best_rules.loc[
                    localized_best_rules['adjudication_status'].eq('nuclear_localized')
                ].copy()
                supportive_localized = localized_best_rules.loc[
                    localized_best_rules['adjudication_status'].eq('supportive_localized')
                ].copy()

                localized_rule_search.to_csv(TABLES_DIR / 'tp53_localized_rule_search.csv', index=False)
                localized_best_rules.to_csv(TABLES_DIR / 'tp53_localized_best_rules.csv', index=False)
                nuclear_localized.to_csv(TABLES_DIR / 'tp53_localized_nuclear_candidates.csv', index=False)
                supportive_localized.to_csv(TABLES_DIR / 'tp53_localized_supportive_candidates.csv', index=False)

                display(localized_best_rules)
                display(nuclear_localized if not nuclear_localized.empty else pd.DataFrame([{'status': 'no_nuclear_localized_rule_found_yet'}]))
                done('The final localized rule space has been searched and the best per-model candidates are now adjudicated.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Build transfer witnesses, positive-only external witnesses, and final stress-test summaries
                def model_live_score_dir(model_name: str) -> Path:
                    return BLOCK12B_LIVE_SCORES_DIR / model_name.replace('/', '_').replace('-', '_')

                positive_witness_panels = ['crebbp', 'grin2a', 'tsc2']
                transfer_rows = []

                for _, best_row in localized_best_rules.iterrows():
                    model_label = str(best_row['model_label'])
                    model_spec = next((item for item in MODEL_SPECS if item['model_label'] == model_label), None)
                    if model_spec is None:
                        continue

                    threshold_source = str(best_row['threshold_source'])
                    threshold = safe_float(best_row['threshold'], float('nan'))
                    rule_family = str(best_row['rule_family'])
                    if not math.isfinite(threshold):
                        continue

                    for panel_name in positive_witness_panels:
                        score_path = model_live_score_dir(model_spec['model_name']) / f'{panel_name}_{model_spec["model_name"].replace("/", "_").replace("-", "_")}_scores.csv'
                        if not score_path.exists():
                            transfer_rows.append({
                                'model_label': model_label,
                                'panel_name': panel_name,
                                'n_rows': 0,
                                'n_rule_on': 0,
                                'hit_fraction': float('nan'),
                                'top_pair_variant': 'missing',
                                'top_ll_variant': 'missing',
                                'transfer_status': 'missing_panel',
                            })
                            continue

                        panel_frame = pd.read_csv(score_path)
                        panel_scored = score_vector_from_frame(panel_frame, FIXED_ALPHA)
                        gate_mask = pd.Series(np.ones(len(panel_scored), dtype=bool), index=panel_scored.index)
                        if rule_family == 'pair_only' and str(best_row['gate_name']) == 'exclude_chemistry':
                            gate_mask = ~panel_scored['chemistry_trigger'].fillna(False).astype(bool)
                        score_mask = pd.to_numeric(panel_scored[threshold_source], errors='coerce').fillna(-999.0) >= float(threshold)
                        rule_mask = gate_mask & score_mask
                        top_pair_variant = str(
                            panel_scored.loc[pd.to_numeric(panel_scored['pair_minus_ll'], errors='coerce').fillna(-999.0).idxmax(), 'variant_id']
                        )
                        top_ll_variant = str(
                            panel_scored.loc[pd.to_numeric(panel_scored['ll_rank_norm'], errors='coerce').fillna(-999.0).idxmax(), 'variant_id']
                        )
                        transfer_rows.append({
                            'model_label': model_label,
                            'panel_name': panel_name,
                            'n_rows': int(len(panel_scored)),
                            'n_rule_on': int(rule_mask.sum()),
                            'hit_fraction': float(rule_mask.mean()) if len(panel_scored) else float('nan'),
                            'top_pair_variant': top_pair_variant,
                            'top_ll_variant': top_ll_variant,
                            'transfer_status': 'present',
                        })

                transfer_witness_table = pd.DataFrame(transfer_rows)
                if transfer_witness_table.empty:
                    transfer_witness_summary = pd.DataFrame(columns=['model_label', 'positive_witness_panels_present', 'positive_witness_hit_fraction_mean'])
                else:
                    transfer_witness_summary = transfer_witness_table.groupby('model_label', as_index=False).agg(
                        positive_witness_panels_present=('transfer_status', lambda values: int(sum(item == 'present' for item in values))),
                        positive_witness_hit_fraction_mean=('hit_fraction', lambda series: float(pd.to_numeric(series, errors='coerce').mean()) if len(series) else float('nan')),
                    )

                brca1_transfer_summary_path = BLOCK12C_TABLES_DIR / 'brca1_transfer_adjudication_summary.csv'
                brca1_transfer_summary = (
                    pd.read_csv(brca1_transfer_summary_path)
                    if brca1_transfer_summary_path.exists()
                    else pd.DataFrame(columns=['model_label'])
                )

                final_localized_scoreboard = localized_best_rules.merge(
                    transfer_witness_summary,
                    on='model_label',
                    how='left',
                )
                if not brca1_transfer_summary.empty and 'model_label' in brca1_transfer_summary.columns:
                    brca1_small = brca1_transfer_summary.copy()
                    keep_cols = [column for column in brca1_small.columns if column in {'model_label', 'transfer_status', 'transfer_hit_fraction', 'transfer_gap', 'transfer_beats_scalar'}]
                    final_localized_scoreboard = final_localized_scoreboard.merge(
                        brca1_small[keep_cols],
                        on='model_label',
                        how='left',
                        suffixes=('', '_brca1'),
                    )

                final_localized_scoreboard['primary_claim_firewall'] = np.where(
                    final_localized_scoreboard['adjudication_status'].eq('nuclear_localized'),
                    'eligible_for_localized_primary_claim',
                    'supportive_or_excluded',
                )

                transfer_witness_table.to_csv(TABLES_DIR / 'tp53_positive_witness_transfer_table.csv', index=False)
                transfer_witness_summary.to_csv(TABLES_DIR / 'tp53_positive_witness_transfer_summary.csv', index=False)
                final_localized_scoreboard.to_csv(TABLES_DIR / 'tp53_final_localized_scoreboard.csv', index=False)

                display(transfer_witness_summary if not transfer_witness_summary.empty else pd.DataFrame([{'status': 'no_positive_transfer_witnesses_found'}]))
                display(final_localized_scoreboard)
                done('Positive-only transfer witnesses and the final localized scoreboard are now assembled.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Render figures, write the final manifests, and package the last notebook bundle
                plot_rows = final_localized_scoreboard.copy()
                plot_rows['model_order'] = np.arange(len(plot_rows))

                fig, ax = plt.subplots(figsize=(12, 6))
                colors = plot_rows['adjudication_status'].map(
                    {
                        'nuclear_localized': '#0B6E4F',
                        'supportive_localized': '#4C78A8',
                        'supportive_residual': '#F28E2B',
                        'not_eligible': '#B07AA1',
                    }
                ).fillna('#999999')
                ax.barh(plot_rows['model_label'], plot_rows['enrichment_gap'], color=colors)
                ax.axvline(0.0, color='black', linewidth=1.0)
                ax.set_title('Block 12D localized best-rule enrichment gap by model')
                ax.set_xlabel('Localized enrichment gap')
                fig.tight_layout()
                fig.savefig(FIGURES_DIR / 'localized_best_rule_scoreboard.png', dpi=200, bbox_inches='tight')
                plt.close(fig)

                fig, ax = plt.subplots(figsize=(12, 7))
                ax.scatter(
                    localized_rule_search['n_rule_on'],
                    localized_rule_search['enrichment_gap'],
                    c=localized_rule_search['status_rank'],
                    cmap='viridis',
                    alpha=0.7,
                    s=40,
                )
                ax.set_title('Block 12D localized rule frontier')
                ax.set_xlabel('n rule on')
                ax.set_ylabel('localized enrichment gap')
                fig.tight_layout()
                fig.savefig(FIGURES_DIR / 'localized_rule_frontier.png', dpi=200, bbox_inches='tight')
                plt.close(fig)

                fig, ax = plt.subplots(figsize=(12, 6))
                same_position_plot = final_localized_scoreboard[['model_label', 'same_position_delta']].copy()
                same_position_plot['same_position_delta'] = pd.to_numeric(same_position_plot['same_position_delta'], errors='coerce')
                ax.barh(
                    same_position_plot['model_label'],
                    same_position_plot['same_position_delta'].fillna(0.0),
                    color=['#2C7FB8' if value >= 0 else '#D95F02' for value in same_position_plot['same_position_delta'].fillna(0.0)],
                )
                ax.axvline(0.0, color='black', linewidth=1.0)
                ax.set_title('Same-position witness delta on the selected localized panel')
                ax.set_xlabel('pair top-hit rate minus ll top-hit rate')
                fig.tight_layout()
                fig.savefig(FIGURES_DIR / 'localized_same_position_delta.png', dpi=200, bbox_inches='tight')
                plt.close(fig)

                nuclear_localized = final_localized_scoreboard.loc[
                    final_localized_scoreboard['adjudication_status'].eq('nuclear_localized')
                ].copy()
                best_primary_model = (
                    str(nuclear_localized.sort_values('enrichment_gap', ascending=False)['model_label'].iloc[0])
                    if not nuclear_localized.empty
                    else 'none'
                )

                if not nuclear_localized.empty:
                    claim_status = 'localized_covariance_nuclear'
                    claim_reason = (
                        'A compact localized covariance rule survives global scalar controls, local scalar controls, chemistry controls, '
                        'and the strict structural witness. The rescue is now strong enough for a bounded primary claim.'
                    )
                elif bool((final_localized_scoreboard['adjudication_status'] == 'supportive_localized').any()):
                    claim_status = 'localized_covariance_supportive'
                    claim_reason = (
                        'Block 12D sharpens the story substantially, but the final primary claim still falls short of a nuclear localized regime.'
                    )
                else:
                    claim_status = 'covariance_adjudication_still_mixed'
                    claim_reason = (
                        'Even after the final localized search, the notebook does not find a rule that fully clears the nuclear localized firewall.'
                    )

                summary_payload = {
                    'notebook_slug': NOTEBOOK_SLUG,
                    'run_at_utc': RUN_AT,
                    'account_label': ACCOUNT_LABEL,
                    'claim_status': claim_status,
                    'claim_reason': claim_reason,
                    'block12c_claim_status': block12c_artifact_summary.get('claim_status', 'missing'),
                    'n_models_evaluated': int(len(final_localized_scoreboard)),
                    'n_nuclear_localized_models': int(final_localized_scoreboard['adjudication_status'].eq('nuclear_localized').sum()),
                    'n_supportive_localized_models': int(final_localized_scoreboard['adjudication_status'].eq('supportive_localized').sum()),
                    'best_primary_model': best_primary_model,
                    'best_primary_panel': (
                        str(nuclear_localized.sort_values('enrichment_gap', ascending=False)['panel_name'].iloc[0])
                        if not nuclear_localized.empty
                        else 'none'
                    ),
                    'structural_source_kind': structural_source_kind,
                    'structural_source_path': structural_source_path,
                }

                response_md = (
                    f"# Block 12D Final Localization Summary\\n\\n"
                    f"- Claim status: **{claim_status}**\\n"
                    f"- Claim reason: {claim_reason}\\n"
                    f"- Best primary model: **{best_primary_model}**\\n"
                    f"- Nuclear localized models: **{int(final_localized_scoreboard['adjudication_status'].eq('nuclear_localized').sum())}**\\n"
                    f"- Supportive localized models: **{int(final_localized_scoreboard['adjudication_status'].eq('supportive_localized').sum())}**\\n"
                    f"- Structural source: `{structural_source_kind}` from `{structural_source_path}`\\n"
                )

                claim_paragraph = (
                    'Block 12D is the final localization pass. Instead of asking covariance to prove universality everywhere at once, '
                    'the notebook searches for a compact localized rescue regime that clears stronger matched controls and a strict structural witness. '
                    'The resulting claim is intentionally bounded: the notebook either upgrades one model into a localized nuclear rescue or it records, cleanly and explicitly, that even the last localization attempt stays supportive.'
                )

                (MANIFESTS_DIR / 'block12d_final_localization_summary.json').write_text(
                    json.dumps(summary_payload, indent=2),
                    encoding='utf-8',
                )
                (MANIFESTS_DIR / 'artifact_summary.json').write_text(
                    json.dumps(summary_payload, indent=2),
                    encoding='utf-8',
                )
                (TEXT_DIR / 'block12d_final_localization_summary.md').write_text(response_md + '\\n', encoding='utf-8')
                (TEXT_DIR / 'block12d_claim_paragraph.md').write_text(claim_paragraph + '\\n', encoding='utf-8')

                bundle_sources = [TABLES_DIR, FIGURES_DIR, TEXT_DIR, MANIFESTS_DIR, RUNTIME_DIR, LIVE_SCORES_DIR]
                if BUNDLE_ROOT.exists():
                    shutil.rmtree(BUNDLE_ROOT)
                BUNDLE_ROOT.mkdir(parents=True, exist_ok=True)
                for folder in bundle_sources:
                    shutil.copytree(folder, BUNDLE_ROOT / folder.name, dirs_exist_ok=True)

                if ZIP_PATH.exists():
                    ZIP_PATH.unlink()
                with zipfile.ZipFile(ZIP_PATH, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
                    for folder in bundle_sources:
                        for file_path in folder.rglob('*'):
                            if file_path.is_file():
                                archive.write(file_path, arcname=str(file_path.relative_to(RESULTS_ROOT)))

                print(json.dumps(summary_payload, indent=2))
                display(final_localized_scoreboard)
                display(nuclear_localized if not nuclear_localized.empty else pd.DataFrame([{'status': 'no_nuclear_localized_rule_found'}]))
                done('Figures, manifests, markdown summaries, and the final Block 12D bundle are written.')
                """
            )
        ),
    ]

    return notebook


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    notebook = build_notebook()
    output_path = repo_root / "New Notebooks" / f"{NEW_SLUG}.ipynb"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(notebook, indent=2), encoding="utf-8")
    print(f"Wrote notebook to {output_path}")


if __name__ == "__main__":
    main()
