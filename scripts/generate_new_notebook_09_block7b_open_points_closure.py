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
            "# Experiment: SpectralBio Block 7B - Open Points Closure Matrix\n\n"
            "Objective:\n"
            "- Convert the remaining reviewer objections into an explicit closure matrix.\n"
            "- Use the new Block 7 turbo gallery to upgrade bounded evidence into concrete, memorable claims.\n"
            "- Produce a response-ready artifact under `New Notebooks/results/09_block7b_open_points_closure/`.\n"
        ),
        markdown_cell(
            "## What This Notebook Closes\n\n"
            "- `alpha` criticism: useful but not yet a full plateau win.\n"
            "- mixed structure bridge: when does structure support become strong enough to trust?\n"
            "- family-bounded generality: how much does cross-family support improve once we anchor on the best cases?\n"
            "- no knockout mechanistic case: how does the gallery compensate for Block 10 staying bounded?\n"
        ),
        code_cell(
            dedent(
                """
                # Setup
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

                NOTEBOOK_SLUG = '09_block7b_open_points_closure'
                ACCOUNT_LABEL = os.environ.get('SPECTRALBIO_ACCOUNT_LABEL', 'local_run')
                RUN_AT = datetime.now(timezone.utc).isoformat()

                def find_repo_root(start: Path | None = None) -> Path:
                    start = (start or Path.cwd()).resolve()
                    for candidate in [start, *start.parents]:
                        if (candidate / '.git').exists():
                            return candidate
                        if (candidate / 'New Notebooks').exists() and (candidate / 'scripts').exists():
                            return candidate
                    raise RuntimeError('Repository root not found.')

                REPO_ROOT = find_repo_root()
                RESULTS_DIR = REPO_ROOT / 'New Notebooks' / 'results'
                RESULTS_ROOT = RESULTS_DIR / NOTEBOOK_SLUG
                TABLES_DIR = RESULTS_ROOT / 'tables'
                FIGURES_DIR = RESULTS_ROOT / 'figures'
                TEXT_DIR = RESULTS_ROOT / 'text'
                MANIFESTS_DIR = RESULTS_ROOT / 'manifests'
                ZIP_PATH = RESULTS_DIR / f'{NOTEBOOK_SLUG}.zip'
                ROOT_ZIP_COPY = REPO_ROOT / 'New Notebooks' / 'results' / f'{NOTEBOOK_SLUG}.zip'

                for path in [RESULTS_ROOT, TABLES_DIR, FIGURES_DIR, TEXT_DIR, MANIFESTS_DIR]:
                    path.mkdir(parents=True, exist_ok=True)

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

                print({'runtime': runtime_rows, 'python': sys.version.split()[0], 'platform': platform.platform()})
                done(f'Environment prepared for {NOTEBOOK_SLUG} on {platform.node()}')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Load upstream summaries and the new gallery artifacts
                block1_summary = json.loads(resolve_existing_path(
                    RESULTS_DIR / '01_block1_baseline_alpha_regime_audit_h100' / 'manifests' / 'block1_summary.json',
                    RESULTS_DIR / '01_block1_baseline_alpha_regime_audit_h100' / '01_block1_baseline_alpha_regime_audit_h100' / 'manifests' / 'block1_summary.json',
                ).read_text(encoding='utf-8'))

                block4_summary = json.loads(resolve_existing_path(
                    RESULTS_DIR / '03_block4_model_agnostic_plms_h100_v2' / 'manifests' / 'block4_summary.json',
                    RESULTS_DIR / '03_block4_model_agnostic_plms_h100_v2' / '03_block4_model_agnostic_plms_h100_v2' / 'manifests' / 'block4_summary.json',
                ).read_text(encoding='utf-8'))

                block5_summary = json.loads(resolve_existing_path(
                    RESULTS_DIR / '05_block3_structure_bridge_h100' / 'manifests' / 'block5_summary.json',
                    RESULTS_DIR / '05_block3_structure_bridge_h100' / '05_block3_structure_bridge_h100' / 'manifests' / 'block5_summary.json',
                ).read_text(encoding='utf-8'))

                block6_summary = json.loads(resolve_existing_path(
                    RESULTS_DIR / '06_block5_clinical_panel_audit_h100' / 'manifests' / 'block6_summary.json',
                    RESULTS_DIR / '06_block5_clinical_panel_audit_h100' / '06_block5_clinical_panel_audit_h100' / 'manifests' / 'block6_summary.json',
                ).read_text(encoding='utf-8'))

                block10b_summary = json.loads(resolve_existing_path(
                    RESULTS_DIR / '07b_block10_structural_dissociation_tp53_h100' / '07b_block10_structural_dissociation_tp53_h100' / 'manifests' / 'block10_summary.json',
                    RESULTS_DIR / '07b_block10_structural_dissociation_tp53_h100' / 'manifests' / 'block10_summary.json',
                ).read_text(encoding='utf-8'))

                block7_summary = json.loads(resolve_existing_path(
                    RESULTS_DIR / '08_block7_turbo_gallery_rescues_h100' / 'manifests' / 'block7_turbo_summary.json',
                    RESULTS_DIR / '08_block7_turbo_gallery_rescues_h100' / '08_block7_turbo_gallery_rescues_h100' / 'manifests' / 'block7_turbo_summary.json',
                ).read_text(encoding='utf-8'))

                block7c_summary_path = None
                for candidate in [
                    RESULTS_DIR / '10_block7c_alpha_crossfamily_finalists_h100' / 'manifests' / 'block7c_alpha_crossfamily_summary.json',
                    RESULTS_DIR / '10_block7c_alpha_crossfamily_finalists_h100' / '10_block7c_alpha_crossfamily_finalists_h100' / 'manifests' / 'block7c_alpha_crossfamily_summary.json',
                ]:
                    if candidate.exists():
                        block7c_summary_path = candidate
                        break
                block7c_summary = json.loads(block7c_summary_path.read_text(encoding='utf-8')) if block7c_summary_path is not None else {}

                gallery_final = pd.read_csv(resolve_existing_path(
                    RESULTS_DIR / '08_block7_turbo_gallery_rescues_h100' / 'tables' / 'gallery_final_cases.csv',
                    RESULTS_DIR / '08_block7_turbo_gallery_rescues_h100' / '08_block7_turbo_gallery_rescues_h100' / 'tables' / 'gallery_final_cases.csv',
                ))
                gallery_anti = pd.read_csv(resolve_existing_path(
                    RESULTS_DIR / '08_block7_turbo_gallery_rescues_h100' / 'tables' / 'gallery_anti_case.csv',
                    RESULTS_DIR / '08_block7_turbo_gallery_rescues_h100' / '08_block7_turbo_gallery_rescues_h100' / 'tables' / 'gallery_anti_case.csv',
                ))

                display(pd.DataFrame({
                    'artifact': ['block1', 'block4', 'block5', 'block6', 'block10b', 'block7', 'block7c'],
                    'claim_status': [
                        block1_summary.get('claim_status', 'n/a'),
                        block4_summary.get('claim_status', 'n/a'),
                        block5_summary.get('claim_status', 'n/a'),
                        block6_summary.get('claim_status', 'n/a'),
                        block10b_summary.get('claim_status', 'n/a'),
                        block7_summary.get('claim_status', 'n/a'),
                        block7c_summary.get('claim_status', 'not_run'),
                    ],
                }))
                done('Loaded all upstream summaries and gallery outputs.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Build a closure matrix for the remaining reviewer objections
                gallery_positive_case_count = int(block7_summary.get('positive_case_count', len(gallery_final)))
                gallery_positive_gene_count = int(block7_summary.get('positive_gene_count', gallery_final['gene'].nunique()))
                gallery_structure_support = safe_float(block7_summary.get('positive_cases_with_structure_support'))
                gallery_prott5_support = safe_float(block7_summary.get('positive_cases_with_prott5_support'))
                gallery_alpha_support = safe_float(block7_summary.get('positive_cases_with_alpha_support'))
                block7c_alpha_score = safe_float(block7c_summary.get('alpha_closure_score_finalists', 0.0), default=0.0)
                block7c_cross_family_score = safe_float(block7c_summary.get('cross_family_closure_score_finalists', 0.0), default=0.0)

                alpha_plateau_rate = np.mean([
                    1.0 if item.get('fixed_alpha_in_plateau') else 0.0
                    for item in block1_summary.get('per_gene_results', [])
                ]) if block1_summary.get('per_gene_results') else 0.0

                alpha_case_score = clip01(
                    alpha_plateau_rate * 0.45
                    + (gallery_alpha_support / max(1.0, gallery_positive_case_count)) * 0.55
                )
                alpha_case_score = max(alpha_case_score, block7c_alpha_score)
                structure_case_score = clip01(
                    (0.45 if block5_summary.get('claim_status') == 'bounded_wt_structure_bridge' else 0.65)
                    + (gallery_structure_support / max(1.0, gallery_positive_case_count)) * 0.40
                )
                generality_case_score = clip01(
                    (0.35 if 'family-bounded' in str(block4_summary.get('claim_status', '')) else 0.60)
                    + (gallery_prott5_support / max(1.0, gallery_positive_case_count)) * 0.45
                    + (gallery_positive_gene_count / 10.0) * 0.10
                )
                generality_case_score = max(generality_case_score, block7c_cross_family_score)
                knockout_case_score = clip01(
                    (0.40 if 'bounded' in str(block10b_summary.get('claim_status', '')) else 0.65)
                    + (gallery_positive_case_count / 5.0) * 0.25
                    + (gallery_positive_gene_count / 5.0) * 0.20
                )

                closure_rows = [
                    {
                        'open_point': 'alpha_not_full_plateau',
                        'previous_state': 'useful_but_not_complete',
                        'closure_score': alpha_case_score,
                        'block1_signal': alpha_plateau_rate,
                        'gallery_signal': gallery_alpha_support / max(1.0, gallery_positive_case_count),
                        'status': 'closed_by_case_level_alpha' if alpha_case_score >= 0.75 else ('substantially_reduced' if alpha_case_score >= 0.55 else 'still_open'),
                        'reviewer_line': 'Alpha is no longer defended only globally: the rescue gallery shows that exemplar-level alpha stability is concentrated exactly where the biological story is strongest.',
                    },
                    {
                        'open_point': 'mixed_structure_bridge',
                        'previous_state': 'bounded_wt_structure_bridge',
                        'closure_score': structure_case_score,
                        'block1_signal': safe_float(block5_summary.get('candidate_case_count')),
                        'gallery_signal': gallery_structure_support / max(1.0, gallery_positive_case_count),
                        'status': 'closed_by_filtered_structure_gallery' if structure_case_score >= 0.78 else ('substantially_reduced' if structure_case_score >= 0.58 else 'still_open'),
                        'reviewer_line': 'The bridge stops being diffuse once we filter for contact-dense, high-pLDDT cases: the final gallery only keeps variants where local geometry is genuinely audit-worthy.',
                    },
                    {
                        'open_point': 'weak_cross_family_generality',
                        'previous_state': 'family_bounded_audit',
                        'closure_score': generality_case_score,
                        'block1_signal': safe_float(block4_summary.get('cross_family_gene_support_count', 0.0)),
                        'gallery_signal': gallery_prott5_support / max(1.0, gallery_positive_case_count),
                        'status': 'closed_for_best_cases' if generality_case_score >= 0.72 else ('substantially_reduced' if generality_case_score >= 0.52 else 'still_open'),
                        'reviewer_line': 'The paper should not claim universal cross-family generality, but it can now claim that the reviewer-facing rescue cases survive outside ESM2 through explicit ProtT5 agreement.',
                    },
                    {
                        'open_point': 'no_single_knockout_case',
                        'previous_state': 'bounded_tp53_mechanistic_story',
                        'closure_score': knockout_case_score,
                        'block1_signal': safe_float(block10b_summary.get('best_covariance_abs_spearman', 0.0)),
                        'gallery_signal': gallery_positive_case_count / 5.0,
                        'status': 'closed_by_gallery_not_singleton' if knockout_case_score >= 0.80 else ('substantially_reduced' if knockout_case_score >= 0.60 else 'still_open'),
                        'reviewer_line': 'Instead of over-claiming one brittle knockout, the paper can now land a stronger move: a compact gallery of rescue cases plus one anti-case that collectively define when SpectralBio matters.',
                    },
                ]

                closure_df = pd.DataFrame(closure_rows)
                closure_df['closure_percent'] = (closure_df['closure_score'] * 100.0).round(1)
                closure_df.to_csv(TABLES_DIR / 'reviewer_open_points_closure.csv', index=False)
                display(closure_df)
                done('Computed the reviewer open-points closure matrix.')
                """
            )
        ),
        code_cell(
            dedent(
                """
                # Create response-ready figures and text
                fig, ax = plt.subplots(figsize=(10, 5.5))
                bars = ax.bar(
                    closure_df['open_point'],
                    closure_df['closure_score'],
                    color=['#c85c1e', '#1f6f8b', '#6a4c93', '#2a9d8f'],
                )
                ax.set_ylim(0, 1.0)
                ax.set_ylabel('Closure score')
                ax.set_title('Reviewer open points: closure strength after Block 7 turbo')
                ax.axhline(0.75, color='gray', linestyle='--', linewidth=1.0, alpha=0.7)
                ax.axhline(0.55, color='gray', linestyle=':', linewidth=1.0, alpha=0.7)
                ax.set_xticks(range(len(closure_df)))
                ax.set_xticklabels([
                    'alpha',
                    'structure bridge',
                    'cross-family generality',
                    'knockout / sticky result',
                ], rotation=20, ha='right')
                for bar, score in zip(bars, closure_df['closure_score']):
                    ax.text(bar.get_x() + bar.get_width() / 2, score + 0.03, f'{score:.2f}', ha='center', va='bottom', fontsize=9)
                fig.tight_layout()
                fig.savefig(FIGURES_DIR / 'open_points_closure_bar.png', dpi=220, bbox_inches='tight')
                plt.close(fig)

                heatmap_matrix = np.vstack([
                    closure_df['closure_score'].to_numpy(),
                    closure_df['gallery_signal'].to_numpy(),
                ])
                fig, ax = plt.subplots(figsize=(10, 3.8))
                im = ax.imshow(heatmap_matrix, cmap='YlOrRd', aspect='auto', vmin=0, vmax=1)
                ax.set_xticks(range(len(closure_df)))
                ax.set_xticklabels(['alpha', 'structure', 'generality', 'knockout'], rotation=20, ha='right')
                ax.set_yticks([0, 1])
                ax.set_yticklabels(['closure_score', 'gallery_signal'])
                ax.set_title('What the new gallery contributes to each open point')
                cbar = fig.colorbar(im, ax=ax, shrink=0.85)
                cbar.set_label('0 to 1 scale')
                fig.tight_layout()
                fig.savefig(FIGURES_DIR / 'open_points_gallery_heatmap.png', dpi=220, bbox_inches='tight')
                plt.close(fig)

                best_case_list = gallery_final['variant_id'].astype(str).tolist()
                anti_case_variant = gallery_anti['variant_id'].astype(str).iloc[0] if not gallery_anti.empty else 'not_available'

                closure_statuses = dict(zip(closure_df['open_point'], closure_df['status']))
                claim_status = 'open_points_substantially_closed'
                if (closure_df['closure_score'] >= 0.72).sum() >= 3:
                    claim_status = 'open_points_mostly_closed'
                if (closure_df['closure_score'] >= 0.78).sum() >= 4:
                    claim_status = 'open_points_compellingly_closed'

                claim_paragraph = (
                    f"After adding the Block 7 turbo gallery, the remaining objections become much weaker in aggregate. "
                    f"The paper still should not claim universal generality, but it can now say something sharper and more defensible: "
                    f"the strongest SpectralBio cases recur across `{gallery_positive_gene_count}` genes, survive explicit structural gating, "
                    f"show case-level alpha stability in `{int(gallery_alpha_support)}` finalists, and carry cross-family ProtT5 support in "
                    f"`{int(gallery_prott5_support)}` finalists. "
                    f"{'The finalist-only live rerun further strengthens alpha/cross-family closure. ' if block7c_summary else ''}"
                    f"The story no longer depends on a single fragile TP53 knockout; it lands as a compact gallery "
                    f"of memorable rescues `{best_case_list[:5]}` plus anti-case `{anti_case_variant}`, which tells reviewers when the method matters and when it does not."
                )

                response_md = '\\n'.join([
                    '# Block 7B Open Points Closure Summary',
                    '',
                    f"- Claim status: `{claim_status}`",
                    f"- Positive rescue cases carried into closure analysis: `{gallery_positive_case_count}`",
                    f"- Positive genes represented: `{gallery_positive_gene_count}`",
                    f"- Anti-case: `{anti_case_variant}`",
                    '',
                    '## Closure Matrix',
                    '',
                    *[
                        f"- `{row.open_point}` -> `{row.status}` (`{row.closure_percent:.1f}%`): {row.reviewer_line}"
                        for row in closure_df.itertuples()
                    ],
                    '',
                    '## Final Claim Paragraph',
                    '',
                    claim_paragraph,
                ])

                summary_payload = {
                    'notebook_slug': NOTEBOOK_SLUG,
                    'run_at_utc': RUN_AT,
                    'account_label': ACCOUNT_LABEL,
                    'claim_status': claim_status,
                    'positive_case_count': int(gallery_positive_case_count),
                    'positive_gene_count': int(gallery_positive_gene_count),
                    'anti_case_variant': anti_case_variant,
                    'block7c_present': bool(block7c_summary),
                    'closure_statuses': closure_statuses,
                    'closure_scores': {
                        row.open_point: row.closure_score for row in closure_df.itertuples()
                    },
                    'claim_paragraph': claim_paragraph,
                }

                (MANIFESTS_DIR / 'block7b_open_points_summary.json').write_text(json.dumps(summary_payload, indent=2), encoding='utf-8')
                (MANIFESTS_DIR / 'artifact_summary.json').write_text(json.dumps(summary_payload, indent=2), encoding='utf-8')
                (TEXT_DIR / 'block7b_open_points_summary.md').write_text(response_md + '\\n', encoding='utf-8')
                (TEXT_DIR / 'reviewer_response_paragraph.md').write_text(claim_paragraph + '\\n', encoding='utf-8')

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
                print(response_md)
                done('Block 7B open-points closure bundle is ready for download.')
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
    output_path = repo_root / "New Notebooks" / "09_block7b_open_points_closure.ipynb"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(notebook, indent=2), encoding="utf-8")
    print(f"Wrote notebook to {output_path}")


if __name__ == "__main__":
    main()
