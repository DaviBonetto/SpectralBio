# Migration Report

## Summary

This report tracks how the pre-rebuild repository is being transformed into a single-source-of-truth Claw4S submission. The governing policy is:

- preserve scientific provenance
- narrow the canonical path
- keep TP53 as the only primary executable benchmark
- keep BRCA1 as bounded secondary evidence only
- demote or rewrite any lower-precedence surface that drifts from that contract

## Scientific Safety Legend

- `Safe`: consistent with the truth contract and acceptable as an active repository surface
- `Conditional`: safe only if kept as provenance or after an explicitly stated follow-up
- `Not yet safe`: not acceptable as a canonical scientific surface until the follow-up rewrite lands

## Deletion Policy

- Nothing is permanently deleted before a verified replacement exists.
- After a verified replacement exists, obsolete canonical-path conflicts should be deleted from the active tree.
- `legacy/` is transitional, not a dumping ground.
- This report must record all deletions, moves, replacements, and scientific-safety status.

| Current Path | Decision | New Path | Rationale | Scientific Safety | Safe To Delete After Rebuild? | Verified? |
| --- | --- | --- | --- | --- | --- | --- |
| `README.md` | Rewrite in place | `README.md` | The current README is structurally aligned to TP53-primary / BRCA1-bounded framing and official metrics, but it still repeats blacklist wording in negated form. | Conditional | No | Yes |
| `SKILL.md` | Preserve current alignment; future copy changes owned by Scribe | `SKILL.md` | The historical broad-scope issue is no longer present, but the current text still repeats blacklist wording in negated form. NOETHER did not edit the file. | Conditional | No | Yes |
| `Claw4S_conference.md` | Preserve as context | `docs/competition/claw4s_context.md` references it | Still useful as local competition context and security note source. | Safe | No | Yes |
| `paper/spectralbio.tex` | Preserve but edit | `paper/spectralbio.tex` | The scientific core is valuable, but the file still contains broader transfer inference and rounded headline metrics in figure text. | Not yet safe | No | No |
| `paper/spectralbio.pdf` | Preserve as legacy snapshot only | `paper/spectralbio.pdf` | Useful as provenance during transition, but it should not be treated as the canonical paper until the source rewrite is rebuilt. | Conditional | No | Conditional |
| `paper/spectralbio_clawrxiv.md` | Move to publish surface and keep as submission mirror | `publish/clawrxiv/spectralbio_clawrxiv.md` | The clawRxiv markdown is a publication surface, not a manuscript source, and should live under `publish/` rather than `paper/`. | Safe | Yes | Yes |
| `huggingface/app.py` | Keep as compatibility wrapper | `publish/hf_space/app.py` | Shared logic moved into `src/`; old path now forwards to the canonical Space app. | Safe | Eventually | Yes |
| `huggingface/README.md` | Keep as pointer | `publish/hf_space/README.md` | Canonical Space publish path is `publish/hf_space/`, but the pointer still repeats blacklist wording in negated form. | Conditional | Eventually | Yes |
| `huggingface/dataset_card.md` | Keep as pointer | `publish/hf_dataset/README.md` | Canonical dataset card now lives in `publish/hf_dataset/`, but the pointer still repeats blacklist wording in negated form. | Conditional | Eventually | Yes |
| `huggingface/data/*` | Preserve but demote to legacy semantics | `legacy/huggingface_data/*` | Data snapshots are provenance, not canonical benchmarks. | Safe | No | Yes |
| `colab/results/*` | Preserve but demote to legacy semantics | `legacy/colab_results/*` | Reported results remain valuable provenance, but not canonical execution paths. | Safe | No | Yes |
| `submit/submit.py` | Replace and demote | `scripts/submit_clawrxiv.py` | New flow reads `CLAWRXIV_API_KEY` from environment only. | Safe | Eventually | Yes |
| `submit/api_key.txt` | Remove from canonical path | none | Secrets must never be part of the canonical workflow. | Safe | No, keep ignored locally if needed | Yes |
| `huggingface/assets/hero_bg.png.png` | Preserve but rename | `assets/generated/hero_bg.png` | Duplicate extension normalized. | Safe | Yes | Yes |
| `huggingface/assets/method_diagram.png.png` | Preserve but rename | `assets/diagrams/method_diagram.png` | Duplicate extension normalized. | Safe | Yes | Yes |
| `huggingface/assets/Princenton_logo.png` | Preserve but rename | `assets/branding/princeton_logo.png` | Misspelling fixed. | Safe | Yes | Yes |
| `huggingface/assets/Stanford_logo.png` | Preserve but move | `assets/branding/stanford_logo.png` | Branding normalized. | Safe | Yes | Yes |
| `huggingface/assets/clawRxiv_logo.png` | Preserve but move | `assets/branding/clawrxiv_logo.png` | Branding normalized. | Safe | Yes | Yes |
| `huggingface/assets/esm2_layers.png.jpeg` | Preserve but rename | `assets/diagrams/esm2_layers.jpeg` | Asset naming normalized. | Safe | Yes | Yes |
| `colab/results/figures.png` | Preserve but move | `assets/generated/tp53_results_overview.png` | Generated scientific asset moved into canonical asset layout. | Safe | Yes | Yes |
| `colab/results/tp53_variants.json` | Preserve but move semantic role | `benchmarks/tp53/tp53_canonical_v1.json` | Frozen benchmark source created from a trusted snapshot. | Safe | No | Yes |
| `colab/results/scores.json` | Preserve but move semantic role | `benchmarks/tp53/tp53_scores_v1.json` | Canonical TP53 reference score table. | Safe | No | Yes |
| `huggingface/data/brca1_variants.json` | Preserve but split | `benchmarks/brca1/brca1_full_filtered_v1.json` and `benchmarks/brca1/brca1_transfer100_v1.json` | Full filtered provenance is now separated from the reported transfer subset. | Safe | No | Yes |

## NOETHER Review Notes

- The migration architecture is scientifically sound.
- Remaining follow-up is concentrated in lower-precedence wording and paper wording.
- README, SKILL, legacy pointers, and publish mirrors are structurally correct but still need allowlist-only copy.
- The paper source remains the highest-risk unresolved surface because it still over-infers beyond bounded BRCA1 transfer and still cites legacy reproducibility paths.

## Tree Numbering Resolution

The original planning brief mentioned `fase_05_validation_submission`, but the repository now standardizes the final phase as `temporario/fase_06_validation_submission`. The old wording is treated as a brief typo, not a structural requirement.

## Repository Surgery Updates (2026-03-25)

The following active-tree conflicts were removed after their replacements were verified:

| Obsolete Active Path | Replacement / Owner | Action | Reason |
| --- | --- | --- | --- |
| `spectralbio/__init__.py` | `src/spectralbio/` only | Deleted from active tree | Removed the root-vs-src namespace split so the package has one canonical authority under `src/`. |
| `sitecustomize.py` | none | Deleted from active tree | Retired an ineffective repo-root path injector after standardizing on uv-first installs and script-local `src/` bootstrapping. |
| `huggingface/assets/*` | `assets/*` | Deleted from active tree | Compatibility folder no longer carries primary assets. |
| `huggingface/data/*` | `legacy/huggingface_data/*` and `benchmarks/*` | Deleted from active tree | Compatibility folder no longer carries benchmark-facing data. |
| `submit/*` | `scripts/submit_clawrxiv.py` and `legacy/submit/*` | Deleted from active tree | Removed a second submit surface and the old secret-bearing path. |
| `colab/spectralbio.ipynb` | `legacy/colab/spectralbio.ipynb` | Deleted from active tree | Notebook-era workflow is preserved for provenance only and no longer occupies the public root surface. |
| `colab/results/*` | `legacy/colab_results/*` and `assets/generated/tp53_results_overview.png` | Deleted from active tree | Removed benchmark-facing duplicates after paper asset references were redirected. |
| `artifacts/release/claw4s_2026/canonical/*` and `artifacts/release/claw4s_2026/transfer/*` | `artifacts/release/claw4s_2026/outputs/*` | Deleted | Release bundle now exposes one obvious output layout. |

Additional normalization completed:

- `configs/tp53_canonical.yaml` now targets `outputs/canonical`
- `configs/brca1_transfer.yaml` now targets `outputs/transfer`
- `benchmarks/manifests/source_snapshot.json` now points to `legacy/` provenance paths instead of deleted active-tree copies
