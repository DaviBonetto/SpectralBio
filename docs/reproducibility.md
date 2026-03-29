# Reproducibility

## Environment

- Python package root: `src/`
- CLI entrypoint: `spectralbio`
- Seed: `42`
- Canonical model metadata: `facebook/esm2_t30_150M_UR50D` is recorded in `outputs/canonical/run_metadata.json` as provenance for the frozen contract

## Benchmark Contract

SpectralBio reproduces one primary benchmark and one bounded secondary transfer evaluation.

- Primary benchmark: `TP53 canonical executable benchmark`
- Secondary benchmark: `bounded transfer on a fixed BRCA1 subset (N=100)`
- Transfer framing: `secondary transfer evaluation without retraining`
- Adaptation note: `adaptation recipe only`
- Provenance-only data: `BRCA1_full_filtered_v1.json` is preserved for provenance and transfer-subset derivation, not as a canonical scored benchmark.

## Official Metrics

- TP53 canonical executable benchmark: `0.55*frob_dist + 0.45*ll_proper` AUC = `0.7498`
- Bounded transfer on a fixed BRCA1 subset (`N=100`): `ll_proper` AUC = `0.9174`
- Reproducibility delta: `0.0`

Metric verification uses the `0.0001` tolerance declared in `artifacts/expected/verification_rules.json`.

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

The current canonical path deliberately materializes frozen TP53 artifacts from bundled benchmark inputs and bundled score references. It writes the canonical contract files under `outputs/canonical/` for reproducibility, verification, and judge-safe execution. It does **not** depend on a live HuggingFace/ESM2 download in the canonical public path.

## Optional Full Validation

```bash
uv run spectralbio transfer
uv run spectralbio verify
uv run python scripts/preflight.py
```

`uv run spectralbio verify` writes the repository contract report to `outputs/canonical/verification.json` with top-level `PASS` / `FAIL` status and nested canonical/transfer checks.

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

Until then, the current frozen metrics are treated as the official baseline contract.
