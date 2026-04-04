<p align="center">
  <img src="assets/branding/spectralbio_banner.jpeg" alt="SpectralBio banner" />
</p>

<p align="center"><strong>Claw4S Conference 2026 Submission Artifact</strong></p>
<p align="center"><sub>BRCA2 flagship scientific audit, TP53 frozen canonical replay, BRCA1 bounded auxiliary transfer.</sub></p>

SpectralBio is a `research reproducibility artifact` for the Claw4S Conference 2026 submission. Its manuscript-facing scientific center is a stronger-baseline covariance augmentation result on `BRCA2`, while its frozen executable replay center remains the `TP53 canonical executable benchmark`.

## Public Hierarchy

- Flagship scientific result: `BRCA2` covariance-aware augmentation against a five-model ESM-1v ensemble
- Validation anchor: `TP53` is the only frozen public canonical replay surface
- Breadth surface: support-ranked top-25 feasible panel from the 15,752-gene ClinVar scan
- Boundary surfaces: protocol sweep and BRCA1 failure analysis
- Auxiliary executable surface: `bounded transfer on a fixed BRCA1 subset (N=100) without retraining`

This hierarchy is deliberate. `BRCA2` owns the manuscript-facing scientific claim, `TP53` owns the cold-start public replay contract, `BRCA1` remains `secondary transfer evaluation without retraining`, and anything beyond the released replay or audit surfaces is `adaptation recipe only`.

## Two-Layer Contract

### Manuscript Scientific Contract

- `BRCA2` is the flagship scientific result
- `TP53` is the validation anchor and the only frozen public canonical replay surface
- The support-ranked top-25 feasible panel is the breadth surface
- The protocol sweep and BRCA1 failure analysis are the main public boundary surfaces

### Frozen Executable Replay Contract

- Primary executable claim: `TP53 canonical executable benchmark`
- Auxiliary executable claim: `bounded transfer on a fixed BRCA1 subset (N=100) without retraining`
- Transfer framing: `secondary transfer evaluation without retraining`
- Repository framing: `research reproducibility artifact`
- Extension policy: `adaptation recipe only`

The repository is aligned only when these two layers are stated together rather than collapsed into a TP53-only story or a BRCA2-only story.

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

Use these surfaces when the task is paper alignment, scientific review, or judge-facing interpretation rather than cold-start CLI replay:

- [`abstract.md`](abstract.md)
- [`content.md`](content.md)
- [`notebooks/final_accept_part3_esm1v_augmentation_A100.ipynb`](notebooks/final_accept_part3_esm1v_augmentation_A100.ipynb)
- [`notebooks/final_accept_part4_brca2_canonicalization_A100.ipynb`](notebooks/final_accept_part4_brca2_canonicalization_A100.ipynb)
- [`notebooks/final_accept_part1_support_panel.ipynb`](notebooks/final_accept_part1_support_panel.ipynb)
- [`notebooks/final_accept_part5_protocol_sweep_A100.ipynb`](notebooks/final_accept_part5_protocol_sweep_A100.ipynb)
- [`notebooks/final_accept_part6_panel25_brca1_failure_L4.ipynb`](notebooks/final_accept_part6_panel25_brca1_failure_L4.ipynb)

These surfaces expose the BRCA2 flagship result, benchmark qualification, support-ranked breadth, protocol sensitivity, and BRCA1 boundary behavior. They complement the TP53 replay path; they do not replace it as the canonical executable contract.

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
