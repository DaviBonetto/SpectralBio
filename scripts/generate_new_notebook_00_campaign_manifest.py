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
            "# Experiment: SpectralBio Campaign 00 - Manifest And Cache Prep (T4)\n\n"
            "Objective:\n"
            "- Bootstrap a Colab/T4-ready SpectralBio campaign workspace from GitHub.\n"
            "- Inventory the reusable notebooks, scripts, and result bundles already present in the repository.\n"
            "- Write a clean campaign manifest, package it as a zip, and download it automatically in Colab.\n"
        ),
        markdown_cell(
            "## What This Notebook Does\n\n"
            "- Syncs the latest repository state from GitHub.\n"
            "- Creates a campaign-specific results folder under `New Notebooks/results/`.\n"
            "- Scans the repository for reusable notebooks, scripts, and known result directories.\n"
            "- Produces a machine-readable manifest and a short human-readable summary.\n"
            "- Builds a zip artifact and downloads it automatically when running in Google Colab.\n\n"
            "## What This Notebook Does Not Do\n\n"
            "- It does **not** run heavy PLM inference.\n"
            "- It does **not** spend H100 time.\n"
            "- It does **not** modify paper text.\n"
        ),
        code_cell(
            "# Setup: imports, configuration, and stable paths\n"
            "from __future__ import annotations\n\n"
            "import json\n"
            "import os\n"
            "import platform\n"
            "import shutil\n"
            "import subprocess\n"
            "import sys\n"
            "import textwrap\n"
            "import zipfile\n"
            "from datetime import datetime, timezone\n"
            "from pathlib import Path\n\n"
            "SEED = 42\n"
            "NOTEBOOK_SLUG = '00_campaign_manifest_and_cache_prep_t4'\n"
            "ACCOUNT_LABEL = os.environ.get('SPECTRALBIO_ACCOUNT_LABEL', 'SET_ACCOUNT_LABEL_HERE')\n"
            "REPO_URL = os.environ.get('SPECTRALBIO_REPO_URL', 'https://github.com/DaviBonetto/SpectralBio.git')\n"
            "GIT_REF = os.environ.get('SPECTRALBIO_GIT_REF', 'codex/claw4s-rebuild')\n"
            "REPO_DIR = Path(os.environ.get('SPECTRALBIO_COLAB_REPO_DIR', '/content/Stanford-Claw4s'))\n"
            "RUN_AT = datetime.now(timezone.utc).isoformat()\n\n"
            "def done(message: str) -> None:\n"
            "    print(f'TERMINEI PODE SEGUIR - {message}')\n\n"
            "def in_colab() -> bool:\n"
            "    return 'google.colab' in sys.modules\n\n"
            "print({'seed': SEED, 'account_label': ACCOUNT_LABEL, 'repo_url': REPO_URL, 'git_ref': GIT_REF, 'repo_dir': str(REPO_DIR), 'python': sys.version.split()[0], 'platform': platform.platform()})\n"
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
            "def list_names(path: Path) -> list[str]:\n"
            "    if not path.exists():\n"
            "        return []\n"
            "    return sorted(item.name for item in path.iterdir())\n\n"
            "done('Helpers prontos.')\n"
        ),
        code_cell(
            "# Sync the repository from GitHub so Colab runs the latest pushed version\n"
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
            "zip_path = campaign_root / 'results' / f'{NOTEBOOK_SLUG}.zip'\n\n"
            "layout = {\n"
            "    'campaign_root': str(campaign_root),\n"
            "    'results_root': str(results_root),\n"
            "    'manifests_dir': str(manifests_dir),\n"
            "    'tables_dir': str(tables_dir),\n"
            "    'text_dir': str(text_dir),\n"
            "    'zip_path': str(zip_path),\n"
            "}\n"
            "print(layout)\n"
            "done('Pastas da campanha criadas.')\n"
        ),
        code_cell(
            "# Inventory the reusable notebooks, scripts, and known result bundles already present in the repo\n"
            "inventory = {\n"
            "    'run_at_utc': RUN_AT,\n"
            "    'account_label': ACCOUNT_LABEL,\n"
            "    'git_ref_requested': GIT_REF,\n"
            "    'repo_status': repo_status,\n"
            "    'key_paths': {\n"
            "        'notebooks_dir': 'notebooks',\n"
            "        'scripts_dir': 'scripts',\n"
            "        'paper_dir': 'paper',\n"
            "        'supplementary_dir': 'supplementary',\n"
            "    },\n"
            "    'existing_notebooks': list_names(REPO_DIR / 'notebooks'),\n"
            "    'existing_scripts': list_names(REPO_DIR / 'scripts'),\n"
            "    'known_result_dirs': [\n"
            "        normalize_rel(path, REPO_DIR)\n"
            "        for path in sorted((REPO_DIR / 'notebooks').iterdir())\n"
            "        if path.is_dir()\n"
            "    ],\n"
            "    'reusable_targets': {\n"
            "        'baseline_and_alpha': [\n"
            "            'notebooks/final_accept_part3_esm1v_augmentation_A100.ipynb',\n"
            "            'notebooks/final_accept_part4_brca2_canonicalization_A100.ipynb',\n"
            "            'notebooks/final_accept_part5_protocol_sweep_A100.ipynb',\n"
            "            'notebooks/review_recovery_msh2_esm1v_h100.ipynb',\n"
            "        ],\n"
            "        'failure_mode_chain': [\n"
            "            'notebooks/final_accept_part7_failure_mode_screen_T4.ipynb',\n"
            "            'notebooks/final_accept_part8_failure_mode_validation_H100.ipynb',\n"
            "            'notebooks/final_accept_part8b_scale_repair_validation_H100.ipynb',\n"
            "            'notebooks/final_accept_part10_failure_mode_robustness_audit_T4.ipynb',\n"
            "            'notebooks/final_accept_part11_sister_substitution_audit_T4.ipynb',\n"
            "        ],\n"
            "        'clinical_followups': [\n"
            "            'notebooks/final_accept_part1_support_panel.ipynb',\n"
            "            'notebooks/final_accept_part6_panel25_brca1_failure_L4.ipynb',\n"
            "            'notebooks/final_accept_part12_tsc2_crebbp_esm1v_followup_T4.ipynb',\n"
            "        ],\n"
            "        'automation_scripts': [\n"
            "            'scripts/run_part10_failure_mode_robustness_audit.py',\n"
            "            'scripts/run_part11_sister_substitution_audit.py',\n"
            "            'scripts/run_part12_tsc2_crebbp_esm1v_followup.py',\n"
            "            'scripts/preflight.py',\n"
            "            'scripts/build_paper.py',\n"
            "            'scripts/generate_release_bundle.py',\n"
            "        ],\n"
            "    },\n"
            "}\n\n"
            "manifest_path = manifests_dir / 'campaign_manifest.json'\n"
            "with manifest_path.open('w', encoding='utf-8') as handle:\n"
            "    json.dump(inventory, handle, indent=2)\n"
            "    handle.write('\\n')\n\n"
            "print({'manifest_path': str(manifest_path), 'notebooks_found': len(inventory['existing_notebooks']), 'scripts_found': len(inventory['existing_scripts'])})\n"
            "done('Manifesto principal escrito.')\n"
        ),
        code_cell(
            "# Build a compact human-readable summary for the next execution round\n"
            "summary_lines = [\n"
            "    '# SpectralBio Campaign 00 Summary',\n"
            "    '',\n"
            "    f'- Account label: `{ACCOUNT_LABEL}`',\n"
            "    f'- Requested Git ref: `{GIT_REF}`',\n"
            "    f\"- Repository HEAD: `{repo_status['head_commit'][:12]}` - {repo_status['head_subject']}\",\n"
            "    f\"- Notebooks discovered: `{len(inventory['existing_notebooks'])}`\",\n"
            "    f\"- Scripts discovered: `{len(inventory['existing_scripts'])}`\",\n"
            "    '',\n"
            "    '## Reusable groups',\n"
            "    '',\n"
            "]\n\n"
            "for group_name, members in inventory['reusable_targets'].items():\n"
            "    summary_lines.append(f'### {group_name}')\n"
            "    summary_lines.append('')\n"
            "    for member in members:\n"
            "        exists = (REPO_DIR / member).exists()\n"
            "        marker = 'OK' if exists else 'MISSING'\n"
            "        summary_lines.append(f'- [{marker}] `{member}`')\n"
            "    summary_lines.append('')\n\n"
            "summary_path = text_dir / 'campaign_summary.md'\n"
            "summary_path.write_text('\\n'.join(summary_lines).strip() + '\\n', encoding='utf-8')\n"
            "print(summary_path.read_text(encoding='utf-8'))\n"
            "done('Resumo legível gerado.')\n"
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
            "artifact_summary_path = manifests_dir / 'artifact_summary.json'\n"
            "artifact_summary_path.write_text(json.dumps(artifact_summary, indent=2) + '\\n', encoding='utf-8')\n"
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
        markdown_cell(
            "## Expected Next Step\n\n"
            "After this notebook finishes, send the generated zip back into the working thread so the H100-bound notebooks can be narrowed and prioritized with the exact cached inventory from the synced repository.\n"
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
    output_path = repo_root / "New Notebooks" / "00_campaign_manifest_and_cache_prep_T4.ipynb"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    notebook = build_notebook()
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(notebook, handle, indent=2)
        handle.write("\n")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
