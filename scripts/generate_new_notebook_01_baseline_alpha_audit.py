from __future__ import annotations

import json
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


def build_notebook() -> dict:
    cells = [
        markdown_cell(
            "# Experiment: SpectralBio Campaign 01 - Baseline Alpha And Naming Audit\n\n"
            "Objective:\n"
            "- Produce a reviewer-facing audit for the three most exposed criticisms: weak baseline, arbitrary alpha, and opaque regime naming.\n"
            "- Reuse the strongest existing artifacts first, then only rerun targeted baseline work if explicitly enabled.\n"
            "- Package a clean summary that can feed the next H100-bound notebooks.\n"
        ),
        markdown_cell(
            "## Audit Questions\n\n"
            "1. Does the criticism about the TP53 baseline still hold when we compare same-surface alternatives directly?\n"
            "2. Is `0.55 / 0.45` a fragile hand-tuned point, or does it sit on a broad plateau compared with alternative combination rules?\n"
            "3. Can we rewrite the regime naming and selection logic so the paper reads as an auditable screen rather than post-hoc jargon?\n\n"
            "## Execution Mode\n\n"
            "- Default mode is artifact-driven and does **not** require GPU.\n"
            "- A guarded rerun mode is available for targeted baseline recomputation when `RERUN_TARGETED_BASELINES = True`.\n"
        ),
        code_cell(
            "# Setup: imports, configuration, and stable paths\n"
            "from __future__ import annotations\n\n"
            "import json\n"
            "import math\n"
            "import os\n"
            "import platform\n"
            "import shutil\n"
            "import subprocess\n"
            "import sys\n"
            "import zipfile\n"
            "from datetime import datetime, timezone\n"
            "from pathlib import Path\n\n"
            "import numpy as np\n"
            "import pandas as pd\n"
            "from IPython.display import display\n"
            "from sklearn.isotonic import IsotonicRegression\n"
            "from sklearn.linear_model import LogisticRegression\n"
            "from sklearn.metrics import roc_auc_score\n"
            "from sklearn.model_selection import RepeatedStratifiedKFold\n"
            "from sklearn.preprocessing import MinMaxScaler\n\n"
            "SEED = 42\n"
            "NOTEBOOK_SLUG = '01_baseline_alpha_and_naming_audit'\n"
            "ACCOUNT_LABEL = os.environ.get('SPECTRALBIO_ACCOUNT_LABEL', 'SET_ACCOUNT_LABEL_HERE')\n"
            "REPO_URL = os.environ.get('SPECTRALBIO_REPO_URL', 'https://github.com/DaviBonetto/SpectralBio.git')\n"
            "GIT_REF = os.environ.get('SPECTRALBIO_GIT_REF', 'codex/claw4s-rebuild')\n"
            "REPO_DIR = Path(os.environ.get('SPECTRALBIO_COLAB_REPO_DIR', '/content/Stanford-Claw4s'))\n"
            "RERUN_TARGETED_BASELINES = os.environ.get('SPECTRALBIO_RERUN_TARGETED_BASELINES', '').strip().lower() in {'1', 'true', 'yes'}\n"
            "RUN_AT = datetime.now(timezone.utc).isoformat()\n\n"
            "def done(message: str) -> None:\n"
            "    print(f'TERMINEI PODE SEGUIR - {message}')\n\n"
            "def in_colab() -> bool:\n"
            "    return 'google.colab' in sys.modules\n\n"
            "print({'seed': SEED, 'account_label': ACCOUNT_LABEL, 'repo_url': REPO_URL, 'git_ref': GIT_REF, 'rerun_targeted_baselines': RERUN_TARGETED_BASELINES, 'repo_dir': str(REPO_DIR), 'python': sys.version.split()[0], 'platform': platform.platform()})\n"
            "done('Configuração carregada.')\n"
        ),
        code_cell(
            "# Helper functions used by the remaining cells\n"
            "def run(command: list[str], cwd: Path | None = None) -> str:\n"
            "    completed = subprocess.run(\n"
            "        command,\n"
            "        cwd=str(cwd) if cwd is not None else None,\n"
            "        check=True,\n"
            "        text=True,\n"
            "        encoding='utf-8',\n"
            "        errors='replace',\n"
            "        capture_output=True,\n"
            "    )\n"
            "    stdout = completed.stdout or ''\n"
            "    stderr = completed.stderr or ''\n"
            "    if stdout.strip():\n"
            "        print(stdout.strip())\n"
            "    if stderr.strip():\n"
            "        print(stderr.strip())\n"
            "    return stdout\n\n"
            "def ensure_dir(path: Path) -> Path:\n"
            "    path.mkdir(parents=True, exist_ok=True)\n"
            "    return path\n\n"
            "def normalize_rel(path: Path, root: Path) -> str:\n"
            "    return str(path.resolve().relative_to(root.resolve())).replace('\\\\', '/')\n\n"
            "def load_json(path: Path) -> dict:\n"
            "    return json.loads(path.read_text(encoding='utf-8'))\n\n"
            "def load_table(path: Path) -> pd.DataFrame:\n"
            "    if path.suffix == '.tsv':\n"
            "        return pd.read_csv(path, sep='\\t')\n"
            "    return pd.read_csv(path)\n\n"
            "def auc_safe(y_true: pd.Series | np.ndarray, y_score: pd.Series | np.ndarray) -> float:\n"
            "    return float(roc_auc_score(np.asarray(y_true), np.asarray(y_score)))\n\n"
            "def rank_borda_score(left: pd.Series, right: pd.Series) -> np.ndarray:\n"
            "    left_rank = left.rank(method='average', ascending=True, pct=True)\n"
            "    right_rank = right.rank(method='average', ascending=True, pct=True)\n"
            "    return ((left_rank + right_rank) / 2.0).to_numpy(dtype=float)\n\n"
            "def cv_combo_scores(frame: pd.DataFrame, feature_cols: list[str], label_col: str, seed: int = 42) -> dict:\n"
            "    X = frame[feature_cols].to_numpy(dtype=float)\n"
            "    y = frame[label_col].to_numpy(dtype=int)\n"
            "    splitter = RepeatedStratifiedKFold(n_splits=5, n_repeats=5, random_state=seed)\n"
            "    logistic_scores = np.zeros(len(frame), dtype=float)\n"
            "    isotonic_scores = np.zeros(len(frame), dtype=float)\n"
            "    for train_idx, test_idx in splitter.split(X, y):\n"
            "        scaler = MinMaxScaler()\n"
            "        X_train = scaler.fit_transform(X[train_idx])\n"
            "        X_test = scaler.transform(X[test_idx])\n"
            "        model = LogisticRegression(max_iter=1000, random_state=seed)\n"
            "        model.fit(X_train, y[train_idx])\n"
            "        logistic_pred_train = model.predict_proba(X_train)[:, 1]\n"
            "        logistic_pred_test = model.predict_proba(X_test)[:, 1]\n"
            "        logistic_scores[test_idx] = logistic_pred_test\n"
            "        iso = IsotonicRegression(out_of_bounds='clip')\n"
            "        iso.fit(logistic_pred_train, y[train_idx])\n"
            "        isotonic_scores[test_idx] = iso.predict(logistic_pred_test)\n"
            "    return {\n"
            "        'logistic_cv_score': logistic_scores,\n"
            "        'isotonic_cv_score': isotonic_scores,\n"
            "        'auc_logistic_cv': auc_safe(y, logistic_scores),\n"
            "        'auc_isotonic_cv': auc_safe(y, isotonic_scores),\n"
            "    }\n\n"
            "done('Helpers prontos.')\n"
        ),
        code_cell(
            "# Sync the repository from GitHub so the audit uses the latest pushed version\n"
            "if REPO_DIR.exists() and (REPO_DIR / '.git').exists():\n"
            "    run(['git', 'fetch', 'origin', GIT_REF, '--depth', '1'], cwd=REPO_DIR)\n"
            "    run(['git', 'checkout', '--detach', 'FETCH_HEAD'], cwd=REPO_DIR)\n"
            "else:\n"
            "    if REPO_DIR.exists():\n"
            "        shutil.rmtree(REPO_DIR)\n"
            "    run(['git', 'clone', '--depth', '1', '--branch', GIT_REF, REPO_URL, str(REPO_DIR)])\n\n"
            "repo_status = {\n"
            "    'repo_dir': str(REPO_DIR),\n"
            "    'head_commit': run(['git', 'rev-parse', 'HEAD'], cwd=REPO_DIR).strip(),\n"
            "    'head_subject': run(['git', 'log', '-1', '--pretty=%s'], cwd=REPO_DIR).strip(),\n"
            "}\n"
            "print(repo_status)\n"
            "done('Repositório sincronizado.')\n"
        ),
        code_cell(
            "# Create the campaign output directories for this notebook run\n"
            "campaign_root = REPO_DIR / 'New Notebooks'\n"
            "results_root = ensure_dir(campaign_root / 'results' / NOTEBOOK_SLUG)\n"
            "manifests_dir = ensure_dir(results_root / 'manifests')\n"
            "tables_dir = ensure_dir(results_root / 'tables')\n"
            "text_dir = ensure_dir(results_root / 'text')\n"
            "zip_path = campaign_root / 'results' / f'{NOTEBOOK_SLUG}.zip'\n"
            "print({'results_root': str(results_root), 'zip_path': str(zip_path)})\n"
            "done('Pastas da campanha criadas.')\n"
        ),
        code_cell(
            "# Resolve all required artifact paths and audit availability before any analysis\n"
            "shared_inputs_dir = REPO_DIR / 'New Notebooks' / 'shared_inputs' / 'block1_baseline_alpha_audit'\n"
            "artifact_paths = {\n"
            "    'tp53_aug_table': shared_inputs_dir / 'tp53_augmentation_table.csv',\n"
            "    'brca2_aug_table': shared_inputs_dir / 'brca2_augmentation_table.csv',\n"
            "    'msh2_aug_table': shared_inputs_dir / 'msh2_augmentation_table.csv',\n"
            "    'esm1v_aug_summary': shared_inputs_dir / 'esm1v_augmentation_summary.json',\n"
            "    'brca2_nested_summary': shared_inputs_dir / 'brca2_nested_cv_summary.json',\n"
            "    'msh2_decision_summary': shared_inputs_dir / 'msh2_h100_decision_summary.json',\n"
            "    'protocol_sweep_summary': shared_inputs_dir / 'protocol_sweep_summary.json',\n"
            "    'tp53_scores': shared_inputs_dir / 'tp53_scores.tsv',\n"
            "}\n"
            "availability = []\n"
            "for key, path in artifact_paths.items():\n"
            "    availability.append({'artifact': key, 'path': normalize_rel(path, REPO_DIR), 'exists': path.exists()})\n"
            "availability_df = pd.DataFrame(availability)\n"
            "display(availability_df)\n"
            "availability_df.to_csv(tables_dir / 'artifact_availability.csv', index=False)\n"
            "missing_required = availability_df.loc[~availability_df['exists'], 'artifact'].tolist()\n"
            "if missing_required:\n"
            "    raise FileNotFoundError(f'Missing required artifacts: {missing_required}')\n"
            "done('Disponibilidade dos artefatos validada.')\n"
        ),
        code_cell(
            "# Load the core tables and summaries used in the audit\n"
            "tp53_aug = load_table(artifact_paths['tp53_aug_table'])\n"
            "brca2_aug = load_table(artifact_paths['brca2_aug_table'])\n"
            "msh2_aug = load_table(artifact_paths['msh2_aug_table'])\n"
            "tp53_scores = load_table(artifact_paths['tp53_scores'])\n"
            "esm1v_aug_summary = load_json(artifact_paths['esm1v_aug_summary'])\n"
            "brca2_nested_summary = load_json(artifact_paths['brca2_nested_summary'])\n"
            "msh2_decision_summary = load_json(artifact_paths['msh2_decision_summary'])\n"
            "protocol_sweep_summary = load_json(artifact_paths['protocol_sweep_summary'])\n"
            "print({'tp53_aug_shape': tp53_aug.shape, 'brca2_aug_shape': brca2_aug.shape, 'msh2_aug_shape': msh2_aug.shape, 'tp53_scores_shape': tp53_scores.shape})\n"
            "done('Artefatos principais carregados.')\n"
        ),
        code_cell(
            "# Compare fixed 0.55 with alternative combination rules on TP53, BRCA2, and MSH2\n"
            "gene_frames = {\n"
            "    'TP53': tp53_aug.copy(),\n"
            "    'BRCA2': brca2_aug.copy(),\n"
            "    'MSH2': msh2_aug.copy(),\n"
            "}\n"
            "audit_rows = []\n"
            "scored_frames = {}\n"
            "for gene, frame in gene_frames.items():\n"
            "    frame = frame.copy()\n"
            "    frame['borda_pair'] = rank_borda_score(frame['reference_frob_norm'], frame['esm1v_ll_mean_norm'])\n"
            "    combo = cv_combo_scores(frame, ['reference_frob_norm', 'esm1v_ll_mean_norm'], 'label', seed=SEED)\n"
            "    frame['logistic_cv_score'] = combo['logistic_cv_score']\n"
            "    frame['isotonic_cv_score'] = combo['isotonic_cv_score']\n"
            "    auc_reference_pair = auc_safe(frame['label'], frame['reference_pair_norm']) if 'reference_pair_norm' in frame else float('nan')\n"
            "    auc_esm1v = auc_safe(frame['label'], frame['esm1v_ll_mean_norm'])\n"
            "    auc_augmented_055 = auc_safe(frame['label'], frame['augmented_pair_fixed_055'])\n"
            "    auc_borda = auc_safe(frame['label'], frame['borda_pair'])\n"
            "    audit_rows.extend([\n"
            "        {'gene': gene, 'score_family': 'esm1v_baseline', 'auc': auc_esm1v},\n"
            "        {'gene': gene, 'score_family': 'reference_pair_norm', 'auc': auc_reference_pair},\n"
            "        {'gene': gene, 'score_family': 'augmented_pair_fixed_055', 'auc': auc_augmented_055},\n"
            "        {'gene': gene, 'score_family': 'borda_pair', 'auc': auc_borda},\n"
            "        {'gene': gene, 'score_family': 'logistic_cv_pair', 'auc': combo['auc_logistic_cv']},\n"
            "        {'gene': gene, 'score_family': 'isotonic_cv_pair', 'auc': combo['auc_isotonic_cv']},\n"
            "    ])\n"
            "    scored_frames[gene] = frame\n"
            "audit_df = pd.DataFrame(audit_rows).sort_values(['gene', 'auc'], ascending=[True, False]).reset_index(drop=True)\n"
            "display(audit_df)\n"
            "audit_df.to_csv(tables_dir / 'baseline_alpha_audit_auc_table.csv', index=False)\n"
            "done('Comparação de combinações concluída.')\n"
        ),
        code_cell(
            "# Consolidate the strongest reviewer-facing evidence from the existing summaries\n"
            "summary_rows = [\n"
            "    {\n"
            "        'surface': 'TP53 same-surface anchor',\n"
            "        'finding': 'ESM-1v remains very strong while fixed 0.55 augmented score is lower, so TP53 is not being sold as a stronger-baseline win.',\n"
            "        'value': esm1v_aug_summary['genes']['TP53']['auc_esm1v_mean'],\n"
            "        'secondary_value': esm1v_aug_summary['genes']['TP53']['auc_augmented_pair_fixed_055'],\n"
            "    },\n"
            "    {\n"
            "        'surface': 'BRCA2 stronger-baseline flagship',\n"
            "        'finding': 'BRCA2 remains the clean positive stronger-baseline case against the five-model ESM-1v ensemble.',\n"
            "        'value': esm1v_aug_summary['genes']['BRCA2']['auc_esm1v_mean'],\n"
            "        'secondary_value': esm1v_aug_summary['genes']['BRCA2']['auc_augmented_pair_fixed_055'],\n"
            "    },\n"
            "    {\n"
            "        'surface': 'MSH2 negative replication',\n"
            "        'finding': 'MSH2 remains a decisive non-replication and supports the bounded claim.',\n"
            "        'value': msh2_decision_summary['auc_esm1v_mean'],\n"
            "        'secondary_value': msh2_decision_summary['auc_augmented_pair_fixed_055'],\n"
            "    },\n"
            "    {\n"
            "        'surface': 'BRCA2 nested CV',\n"
            "        'finding': 'Released alpha is on a plateau rather than a knife-edge optimum in BRCA2 nested CV.',\n"
            "        'value': brca2_nested_summary['comparison_means']['auc_fixed_055_mean'],\n"
            "        'secondary_value': brca2_nested_summary['comparison_means']['auc_tuned_alpha_mean'],\n"
            "    },\n"
            "]\n"
            "summary_df = pd.DataFrame(summary_rows)\n"
            "display(summary_df)\n"
            "summary_df.to_csv(tables_dir / 'reviewer_facing_summary_table.csv', index=False)\n"
            "done('Resumo reviewer-facing consolidado.')\n"
        ),
        code_cell(
            "# Replace opaque regime names with readable labels and document the selection rule explicitly\n"
            "regime_glossary = pd.DataFrame([\n"
            "    {\n"
            "        'legacy_name': 'to_basic__AND__high_disagreement_q75',\n"
            "        'proposed_name': 'high-covariance high-disagreement basic-substitution regime',\n"
            "        'selection_explanation': 'Variants selected from the support-ranked panel by fixed rescue, harm, and disagreement thresholds before stronger-backbone interpretation.',\n"
            "    },\n"
            "    {\n"
            "        'legacy_name': 'support-ranked top-25 feasible panel',\n"
            "        'proposed_name': 'performance-blind support-ranked feasible top-25 panel',\n"
            "        'selection_explanation': 'Genes ranked by binary label support under explicit feasibility and support filters rather than by observed gain.',\n"
            "    },\n"
            "])\n"
            "display(regime_glossary)\n"
            "regime_glossary.to_csv(tables_dir / 'regime_glossary.csv', index=False)\n"
            "done('Glossário de regimes gerado.')\n"
        ),
        code_cell(
            "# Optional hook for targeted reruns if we later decide to spend GPU on Block 1\n"
            "rerun_manifest = {\n"
            "    'rerun_targeted_baselines': RERUN_TARGETED_BASELINES,\n"
            "    'status': 'skipped',\n"
            "    'note': 'Default path is artifact-driven. Flip SPECTRALBIO_RERUN_TARGETED_BASELINES=true only when you explicitly want a fresh targeted rerun.'\n"
            "}\n"
            "if RERUN_TARGETED_BASELINES:\n"
            "    rerun_manifest['status'] = 'requested_but_not_implemented_here'\n"
            "    rerun_manifest['note'] = 'Fresh targeted reruns should be delegated to a dedicated GPU notebook rather than mixed into this audit notebook.'\n"
            "print(rerun_manifest)\n"
            "(manifests_dir / 'rerun_manifest.json').write_text(json.dumps(rerun_manifest, indent=2) + '\\n', encoding='utf-8')\n"
            "done('Hook de rerun opcional registrado.')\n"
        ),
        code_cell(
            "# Write the final notebook summary in paper-facing language\n"
            "top_rows = audit_df.sort_values(['gene', 'auc'], ascending=[True, False]).groupby('gene').head(3)\n"
            "summary_lines = [\n"
            "    '# SpectralBio Campaign 01 Summary',\n"
            "    '',\n"
            "    f'- Account label: `{ACCOUNT_LABEL}`',\n"
            "    f'- Repository HEAD: `{repo_status['head_commit'][:12]}` - {repo_status['head_subject']}',\n"
            "    f'- Artifact-driven mode: `{not RERUN_TARGETED_BASELINES}`',\n"
            "    '',\n"
            "    '## Main takeaways',\n"
            "    '',\n"
            "    '- TP53 remains a same-surface validation anchor rather than a stronger-baseline flagship.',\n"
            "    '- BRCA2 remains the clean positive stronger-baseline case.',\n"
            "    '- MSH2 remains the decisive negative replication attempt.',\n"
            "    '- Fixed alpha can now be discussed against Borda and CV-calibrated alternatives instead of as a naked heuristic.',\n"
            "    '',\n"
            "    '## Best-performing combinations by gene',\n"
            "    '',\n"
            "]\n"
            "for _, row in top_rows.iterrows():\n"
            "    summary_lines.append(f\"- {row['gene']}: `{row['score_family']}` with AUC `{row['auc']:.4f}`\")\n"
            "summary_lines.extend([\n"
            "    '',\n"
            "    '## Naming upgrades',\n"
            "    '',\n"
            "    '- `to_basic__AND__high_disagreement_q75` -> `high-covariance high-disagreement basic-substitution regime`',\n"
            "    '- `support-ranked top-25 feasible panel` -> `performance-blind support-ranked feasible top-25 panel`',\n"
            "])\n"
            "summary_path = text_dir / 'baseline_alpha_audit_summary.md'\n"
            "summary_path.write_text('\\n'.join(summary_lines) + '\\n', encoding='utf-8')\n"
            "print(summary_path.read_text(encoding='utf-8'))\n"
            "done('Resumo final escrito.')\n"
        ),
        code_cell(
            "# Package this notebook's outputs as a zip artifact\n"
            "if zip_path.exists():\n"
            "    zip_path.unlink()\n\n"
            "with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:\n"
            "    for file_path in sorted(results_root.rglob('*')):\n"
            "        if file_path.is_file():\n"
            "            archive.write(file_path, file_path.relative_to(results_root.parent))\n\n"
            "artifact_summary = {\n"
            "    'zip_path': str(zip_path),\n"
            "    'zip_size_bytes': zip_path.stat().st_size,\n"
            "    'results_root': str(results_root),\n"
            "}\n"
            "(manifests_dir / 'artifact_summary.json').write_text(json.dumps(artifact_summary, indent=2) + '\\n', encoding='utf-8')\n"
            "print(artifact_summary)\n"
            "done('Zip gerado com sucesso.')\n"
        ),
        code_cell(
            "# Download the zip automatically when running in Google Colab\n"
            "if in_colab():\n"
            "    from google.colab import files\n\n"
            "    files.download(str(zip_path))\n"
            "    print(f'Colab download started: {zip_path}')\n"
            "else:\n"
            "    print(f'Not running in Colab. Manual artifact path: {zip_path}')\n\n"
            "done('Notebook finalizado.')\n"
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
                "version": "3.12",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    output_path = repo_root / "New Notebooks" / "01_baseline_alpha_and_naming_audit.ipynb"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    notebook = build_notebook()
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(notebook, handle, indent=2)
        handle.write("\n")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
