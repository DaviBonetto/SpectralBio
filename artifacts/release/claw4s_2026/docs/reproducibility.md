# Reproducibility

## Environment

- Python package root: `src/`
- CLI entrypoint: `spectralbio`
- Seed: `42`
- Canonical model metadata: `facebook/esm2_t30_150M_UR50D` is recorded in `outputs/canonical/run_metadata.json` as provenance for the frozen contract

## Reproducibility Contract

SpectralBio has one manuscript-facing scientific center and one frozen executable replay center. Reproducibility depends on keeping those roles distinct.

### Manuscript Scientific Center

- `BRCA2` is the flagship scientific result
- `TP53` is the validation anchor and the only frozen public canonical replay surface
- The support-ranked top-25 feasible panel is the breadth surface
- The protocol sweep and BRCA1 failure analysis are boundary surfaces

### Frozen Executable Replay Center

- Primary executable benchmark: `TP53 canonical executable benchmark`
- Auxiliary executable surface: `bounded transfer on a fixed BRCA1 subset (N=100)`
- Transfer framing: `secondary transfer evaluation without retraining`
- Adaptation note: `adaptation recipe only`
- Provenance-only data: `BRCA1_full_filtered_v1.json` is preserved for provenance and transfer-subset derivation, not as a canonical scored benchmark

## Official Metrics

### Manuscript Scientific Audit Metrics

- BRCA2 ESM-1v baseline AUC: `0.6324`
- BRCA2 covariance + ESM-1v AUC: `0.6890`
- BRCA2 paired gain vs ESM-1v: `0.0566`
- BRCA2 paired 95% bootstrap CI: `[0.0131, 0.1063]`
- BRCA2 empirical permutation `p`: `0.0010`

### Machine-Verified Executable Metrics

- TP53 canonical executable benchmark: `0.55*frob_dist + 0.45*ll_proper` AUC = `0.7498`
- Bounded transfer on a fixed BRCA1 subset (`N=100`): `ll_proper` AUC = `0.9174`
- Reproducibility delta: `0.0`

Metric verification uses the `0.0001` tolerance declared in `artifacts/expected/verification_rules.json` for machine-verified executable outputs.

## Setup

If `uv` is not available yet:

```bash
python -m pip install uv
```

If `uv` is not available immediately after installation, restart the shell once and re-check it.

## Canonical Public Path

```bash
uv sync --frozen
uv run spectralbio canonical
```

The current canonical path deliberately materializes frozen TP53 artifacts from bundled benchmark inputs and bundled score references. It writes the canonical contract files under `outputs/canonical/` for reproducibility, verification, and judge-safe execution. It does **not** depend on a live HuggingFace/ESM2 download in the canonical public path, and it does **not** recompute the BRCA2 flagship notebooks.

## Public Scientific Audit Surfaces

Use these surfaces when the task is scientific review, manuscript alignment, or judge-facing interpretation rather than cold-start CLI replay:

- `abstract.md`
- `content.md`
- `notebooks/final_accept_part3_esm1v_augmentation_A100.ipynb`
- `notebooks/final_accept_part4_brca2_canonicalization_A100.ipynb`
- `notebooks/final_accept_part1_support_panel.ipynb`
- `notebooks/final_accept_part5_protocol_sweep_A100.ipynb`
- `notebooks/final_accept_part6_panel25_brca1_failure_L4.ipynb`

These surfaces document the BRCA2 flagship result, BRCA2 benchmark qualification, breadth, protocol sensitivity, and BRCA1 boundary behavior. They complement the TP53 replay path; they do not replace it as the cold-start executable contract.

## Optional Full Validation

```bash
uv run spectralbio transfer
uv run spectralbio verify
uv run python scripts/preflight.py
```

`uv run spectralbio verify` writes the repository contract report to `outputs/canonical/verification.json` with top-level `PASS` / `FAIL` status and nested canonical / transfer checks.

The optional transfer path keeps BRCA1 bounded and auxiliary. It is not the manuscript flagship result and is not required for canonical TP53 replay success.

For test execution, sync the dev extra first:

```bash
uv sync --frozen --extra dev
uv run pytest
```

## Expected Outputs

The canonical path deliberately materializes the frozen TP53 artifact bundle rather than recomputing a live benchmark from a downloaded model at first run.

Canonical TP53 run:

- `outputs/canonical/run_metadata.json`
- `outputs/canonical/inputs_manifest.json`
- `outputs/canonical/tp53_scores.tsv`
- `outputs/canonical/tp53_metrics.json`
- `outputs/canonical/summary.json`
- `outputs/canonical/roc_tp53.png`
- `outputs/canonical/manifest.json`
- `outputs/canonical/verification.json`

Secondary bounded BRCA1 transfer run:

- `outputs/transfer/summary.json`
- `outputs/transfer/variants.json`
- `outputs/transfer/manifest.json`

## Clean-Room Validation Matrix

| Validation Step | Purpose | Commands | Inputs | Expected Outputs | PASS Criteria | FAIL Criteria |
| --- | --- | --- | --- | --- | --- | --- |
| Local canonical materialization | Prove the canonical path resolves on a clean uv-first local machine | `uv run spectralbio canonical` | frozen TP53 benchmark files plus bundled score references | `outputs/canonical/*` | all canonical files exist and match the frozen contract | command fails, files missing, or contract files drift |
| Public scientific consistency audit | Confirm BRCA2 / TP53 / BRCA1 roles stay aligned across paper-facing text | inspect `abstract.md`, `content.md`, `docs/truth_contract.md`, `docs/reproducibility.md`, `SKILL.md` | paper-facing contract files | consistent wording across those files | BRCA2 = flagship result, TP53 = only frozen public canonical replay surface, BRCA1 = bounded auxiliary transfer evidence | dual-center ambiguity or role drift |
| Local full preflight | Rerun canonical and transfer generation, stage export surfaces, and validate output plus wording integrity | `uv run python scripts/preflight.py` | canonical docs plus frozen outputs | `temporario/fase_06_validation_submission/evidence/preflight_results.md` | report status is `PASS` | report status is `FAIL` |
| HF Space contract test | Confirm the demo is a thin client over shared logic | `uv run pytest tests/test_demo_contract.py` | `publish/hf_space/` and `src/spectralbio/demo/` | passing demo contract tests | imports shared core and keeps BRCA1 secondary | duplicated scientific logic or broken contract |
| Dataset manifest verification | Confirm hashes, counts, and roles remain explicit | `uv run pytest tests/test_manifests.py` | `benchmarks/**` and manifests | passing manifest tests | counts and roles align with frozen files | transfer/full filtered ambiguity or stale manifest |
| Paper build verification | Confirm the paper still builds and points at canonical outputs | `uv run python scripts/build_paper.py` | `paper/spectralbio.tex` and figures | updated `paper/spectralbio.pdf` or no-op with explicit reason | build succeeds or tool absence is reported explicitly | build breaks silently or figure paths drift |

## Optional Revalidation Policy

Fresh Colab or GPU reruns are outside the current canonical public path.

They become justified only when one of the following changes:

- metrics are revalidated from fresh execution
- runtime is re-measured
- figures are regenerated from new outputs
- hashes need to be refreshed after scientific-core edits

Until then, the current frozen metrics are treated as the official replay baseline contract, while BRCA2 remains the flagship scientific audit surface.
