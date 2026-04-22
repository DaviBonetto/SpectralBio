<p align="center">
  <img src="assets/branding/spectralbio_banner.jpeg" alt="SpectralBio banner" />
</p>

<p align="center"><strong>Claw4S Conference 2026 Submission Artifact</strong></p>
<p align="center"><sub>BRCA2 flagship scientific audit, TP53 frozen canonical replay, replay-ready multi-target portability, and bounded auxiliary transfer.</sub></p>

SpectralBio is a `research reproducibility artifact` for the Claw4S Conference 2026 submission. Its manuscript-facing scientific center remains a stronger-baseline covariance augmentation result on `BRCA2`, while its frozen executable replay center remains the `TP53 canonical executable benchmark`. The public package now also carries `replay-ready multi-target portability` across `TP53`, `BRCA2`, `TSC2`, and `CREBBP`, preserves `BRCA1` and `MSH2` as negative guardrails, and keeps the `final holdout/control tribunal` explicitly mixed rather than fully closed.

## Public Hierarchy

- Flagship scientific result: `BRCA2` covariance-aware augmentation against a five-model ESM-1v ensemble
- Validation anchor: `TP53` is the only frozen public canonical replay surface
- Replay-ready portability surfaces: `TP53`, `BRCA2`, `TSC2`, `CREBBP`
- Transfer-positive targets: `TSC2`, `CREBBP`
- Negative guardrails: `BRCA1`, `MSH2`
- Auxiliary executable surface: `bounded transfer on a fixed BRCA1 subset (N=100) without retraining`
- Final closure boundary: the `final holdout/control tribunal` remains mixed

This hierarchy is deliberate. `BRCA2` owns the manuscript-facing flagship result, `TP53` owns the cold-start public replay contract, `TSC2` and `CREBBP` strengthen the target-level portability story, `BRCA1` and `MSH2` remain explicit guardrails, and the harshest model-level closure remains intentionally bounded.

## Multi-Layer Contract

### Manuscript Scientific Contract

- `BRCA2` is the flagship scientific result
- `TP53` is the validation anchor and the only frozen public canonical replay surface
- The support-ranked top-25 feasible panel and clinical gallery are the bounded breadth surfaces
- The earlier harsh-firewall chain remains part of the claim boundary
- `TP53`, `BRCA2`, `TSC2`, and `CREBBP` now form the replay-ready portability layer
- `TSC2` and `CREBBP` are transfer-positive targets at the target-level portability layer
- `BRCA1` and `MSH2` are retained negative guardrails
- The final holdout/control tribunal remains mixed and does not establish universal or model-level closure

### Frozen Executable Replay Contract

- Primary executable claim: `TP53 canonical executable benchmark`
- Auxiliary executable claim: `bounded transfer on a fixed BRCA1 subset (N=100) without retraining`
- Transfer framing: `secondary transfer evaluation without retraining`
- Repository framing: `research reproducibility artifact`
- Extension policy: `replay-ready portability is stronger than before, but default public executability is still TP53-first and bounded`

The repository is aligned only when these layers are stated together. The package should not collapse into a TP53-only story, and it should not over-promote replay-ready portability surfaces into default executable CLI benchmarks unless the code path truly exists.

## Authors

- **Davi Bonetto** - lead human author, repository steward, and primary artifact owner
- **Claw4S AI Co-author** - competition-rule co-author and reproducibility verifier

## Paper

**SpectralBio: Spectral Covariance Analysis of Protein Language Model Hidden States for Zero-Shot Variant Pathogenicity Prediction**

The paper reports the scientific framing, methodology, and results. The repository is the public execution and audit surface that makes those claims challengeable.

- Paper PDF: [`paper/spectralbio.pdf`](paper/spectralbio.pdf)
- Paper source: [`paper/spectralbio.tex`](paper/spectralbio.tex)
- Bibliography: [`paper/references.bib`](paper/references.bib)
- Long-form abstract: [`abstract.md`](abstract.md)
- Manuscript narrative mirror: [`content.md`](content.md)

## Official Metrics

### Manuscript Scientific Audit Metrics

| Surface | Metric | Value |
| --- | --- | ---: |
| BRCA2 flagship result | ESM-1v baseline AUC | `0.6324` |
| BRCA2 flagship result | Covariance + ESM-1v AUC | `0.6890` |
| BRCA2 flagship result | Delta vs ESM-1v | `0.0566` |
| BRCA2 flagship result | Paired 95% CI | `[0.0131, 0.1063]` |
| BRCA2 flagship result | Empirical permutation `p` | `0.0010` |
| Portability strengthening | Replay-ready targets | `TP53, BRCA2, TSC2, CREBBP` |
| Portability strengthening | Transfer-positive targets | `TSC2, CREBBP` |
| Final tribunal | Closure status | `mixed` |

### Machine-Verified Executable Metrics

| Surface | Metric | Value |
| --- | --- | ---: |
| TP53 canonical replay | `0.55*frob_dist + 0.45*ll_proper` AUC | `0.7498` |
| BRCA1 bounded auxiliary transfer | `ll_proper` AUC | `0.9174` |
| Reproducibility | delta | `0.0` |

## Start Here

If you need context first, read this README and then [`SKILL.md`](SKILL.md). If you need the exact cold-start agent path immediately, jump straight to [`SKILL.md`](SKILL.md).

### Canonical Public Path

```bash
git clone https://github.com/DaviBonetto/SpectralBio.git
cd SpectralBio
python -m pip install uv
uv sync --frozen
uv run spectralbio canonical
```

This is the canonical public path. It materializes the frozen TP53 replay contract from bundled references and writes the canonical artifact bundle to `outputs/canonical/`.

Canonical success establishes:

- the repository can reproduce the frozen TP53 executable benchmark
- the expected machine-verifiable files and metrics materialize
- the repo-level verification contract is intact

Canonical success does **not** establish:

- universal or model-family-wide generalization
- full holdout/control closure
- that every replay-ready portability surface is already exposed through the same default CLI path

### Optional Full Validation

Run the bounded auxiliary transfer and repository-wide checks only after the canonical TP53 path:

```bash
uv run spectralbio transfer
uv run spectralbio verify
uv run python scripts/preflight.py
```

For local test execution:

```bash
uv sync --frozen --extra dev
uv run pytest
```

## Public Scientific Audit Surfaces

Use these surfaces when the task is paper alignment, scientific review, or judge-facing interpretation rather than cold-start CLI replay.

### Core manuscript and contract surfaces

- [`abstract.md`](abstract.md)
- [`content.md`](content.md)
- [`SKILL.md`](SKILL.md)
- [`docs/truth_contract.md`](docs/truth_contract.md)
- [`docs/reproducibility.md`](docs/reproducibility.md)

### Current manuscript audit chain

- [`New Notebooks/results/13_block13_multitarget_generalization_closure_h100/`](New%20Notebooks/results/13_block13_multitarget_generalization_closure_h100/)
- [`New Notebooks/results/14_block14_holdout_control_closure_h100/`](New%20Notebooks/results/14_block14_holdout_control_closure_h100/)

### Earlier harsh-firewall chain

- [`New Notebooks/results/11_block11_covariance_rulebook_h100/`](New%20Notebooks/results/11_block11_covariance_rulebook_h100/)
- [`New Notebooks/results/12_block12_orthogonal_validation_tp53_h100/`](New%20Notebooks/results/12_block12_orthogonal_validation_tp53_h100/)
- [`New Notebooks/results/12b_block12_multifamily_coverage_aware_generalization_h100/`](New%20Notebooks/results/12b_block12_multifamily_coverage_aware_generalization_h100/)
- [`New Notebooks/results/12c_block12_covariance_adjudication_structural_closure_h100/`](New%20Notebooks/results/12c_block12_covariance_adjudication_structural_closure_h100/)
- [`New Notebooks/results/12d_block12_final_nuclear_localization_h100/`](New%20Notebooks/results/12d_block12_final_nuclear_localization_h100/)

### Legacy flagship notebook mirrors

- [`notebooks/final_accept_part3_esm1v_augmentation_A100.ipynb`](notebooks/final_accept_part3_esm1v_augmentation_A100.ipynb)
- [`notebooks/final_accept_part4_brca2_canonicalization_A100.ipynb`](notebooks/final_accept_part4_brca2_canonicalization_A100.ipynb)
- [`notebooks/final_accept_part1_support_panel.ipynb`](notebooks/final_accept_part1_support_panel.ipynb)
- [`notebooks/final_accept_part5_protocol_sweep_A100.ipynb`](notebooks/final_accept_part5_protocol_sweep_A100.ipynb)
- [`notebooks/final_accept_part6_panel25_brca1_failure_L4.ipynb`](notebooks/final_accept_part6_panel25_brca1_failure_L4.ipynb)

These surfaces expose the BRCA2 flagship result, TP53 structural anchor, scale-repair, bounded breadth, earlier harsh firewalls, late-stage portability strengthening, and the final mixed tribunal. They complement the TP53 replay path; they do not replace it as the canonical executable contract.

## Expected Outputs

The canonical TP53 run is expected to materialize these files under `outputs/canonical/`:

- `run_metadata.json`
- `inputs_manifest.json`
- `tp53_scores.tsv`
- `tp53_metrics.json`
- `summary.json`
- `roc_tp53.png`
- `manifest.json`
- `verification.json`

The optional bounded BRCA1 transfer path is expected to materialize these files under `outputs/transfer/`:

- `summary.json`
- `variants.json`
- `manifest.json`

Replay-ready portability surfaces and the final tribunal are currently represented as bundled scientific audit results under `New Notebooks/results/`. They are part of the public truth boundary, but they are not default machine-verified CLI bundles through the same path as TP53 canonical replay.

## Repository Map

- `src/spectralbio/` - public package, CLI, pipeline, demo contract, and shared reproducibility logic
- `docs/` - truth contract, reproducibility notes, architecture, and competition-facing documentation
- `configs/` - frozen configuration presets for canonical and bounded transfer paths
- `benchmarks/` - frozen TP53 and BRCA1 executable inputs, sequences, manifests, and checksums
- `artifacts/expected/` - expected metrics, file contracts, schemas, and verification rules
- `outputs/` - canonical and transfer artifact outputs
- `publish/` - publication-facing surfaces for Hugging Face and clawRxiv
- `paper/` - manuscript source, bibliography, and compiled PDF
- `legacy/` - provenance-only notebook-era, compatibility-era, and migration-era material

## Trust and Verification

The repository is governed by a narrow source-of-truth hierarchy led by:

1. `docs/truth_contract.md`
2. `docs/reproducibility.md`
3. `artifacts/expected/*`
4. `outputs/canonical/*`

Trust in the artifact comes from:

- frozen benchmark inputs and manifests
- explicit expected metrics and output schemas
- generated canonical output manifests
- repository-level verification via `uv run spectralbio verify`
- preflight checks via `uv run python scripts/preflight.py`
- replay-ready portability evidence and final tribunal bundles under `New Notebooks/results/`

The handoff mirror under `artifacts/release/claw4s_2026/` is a packaged public surface, not a higher-precedence source of truth.

## Documentation

- Truth contract: [`docs/truth_contract.md`](docs/truth_contract.md)
- Reproducibility notes: [`docs/reproducibility.md`](docs/reproducibility.md)
- Competition context: [`docs/competition/claw4s_context.md`](docs/competition/claw4s_context.md)
- Submission checklist: [`docs/competition/submission_checklist.md`](docs/competition/submission_checklist.md)
- Agent reproduction contract: [`SKILL.md`](SKILL.md)

## License

This repository is released under the **MIT License**. See [`LICENSE`](LICENSE).

## Legacy Boundary

The old notebook-era `colab/`, benchmark-facing compatibility payloads, and pre-rebuild submission flow are preserved only under `legacy/` for provenance. They are not canonical execution surfaces.
