## Block 1 Shared Inputs

This folder vendors the minimal CSV and JSON artifacts required by
`01_baseline_alpha_and_naming_audit.ipynb`.

Why this exists:
- The original result folders are not reliably present in the GitHub clone used by Colab.
- The notebook only needs a small reviewer-facing audit surface, not the full historical result tree.
- Keeping these inputs here makes the notebook reproducible, lightweight, and Colab-safe.

Contents:
- `tp53_augmentation_table.csv`
- `brca2_augmentation_table.csv`
- `msh2_augmentation_table.csv`
- `esm1v_augmentation_summary.json`
- `brca2_nested_cv_summary.json`
- `msh2_h100_decision_summary.json`
- `protocol_sweep_summary.json`
- `tp53_scores.tsv`
