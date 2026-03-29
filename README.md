<p align="center">
  <img src="assets/branding/spectralbio_banner.jpeg" alt="SpectralBio banner" />
</p>

<p align="center"><strong>Claw4S Conference 2026 Submission Artifact</strong></p>
<p align="center"><sub>Banner visual direction inspired by OpenAI's Parameter Golf presentation language.</sub></p>

Research reproducibility artifact for the **Claw4S Conference 2026**, centered on a **TP53 canonical executable benchmark** with a **bounded secondary BRCA1 transfer evaluation**.

## Claw4S Submission Context

SpectralBio is the public competition artifact for Claw4S Conference 2026. The repository is designed to be readable by judges, reproducible by third parties on a clean machine, and operationally clear for agents that need an exact execution surface.

The project framing is intentionally narrow and evidence-bound:

- Primary benchmark: `TP53 canonical executable benchmark`
- Secondary evidence: `bounded transfer on a fixed BRCA1 subset (N=100) without retraining`
- Transfer framing: `secondary transfer evaluation without retraining`
- Extension policy: `adaptation recipe only`

TP53 is the only canonical scored benchmark and the default executable path. BRCA1 is preserved as bounded secondary evidence only.

## Project Positioning

SpectralBio evaluates zero-shot missense variant scoring through a frozen reproducibility contract rather than a broad generalization claim.

- The repository is the **public artifact and execution surface**.
- The paper is the **scientific narrative report**.
- `SKILL.md` is the **agent-facing reproduction contract**.
- `docs/truth_contract.md` and `docs/reproducibility.md` define the repository truth boundary.

This separation is deliberate: the paper explains the work, while the repository and its verification artifacts define what is mechanically reproducible.

## Authors

- **Davi Bonetto** — lead human author, repository steward, and primary artifact owner
- **Claw 🦞** — AI co-author under Claw4S Conference 2026 competition rules

## Paper

The accompanying paper is:

**SpectralBio: Spectral Covariance Analysis of Protein Language Model Hidden States for Zero-Shot Variant Pathogenicity Prediction**

The paper reports the scientific framing, methodology, and results associated with this submission. The repository is the reproducibility artifact that grounds those claims in a runnable public surface.

- Paper PDF: [`paper/spectralbio.pdf`](paper/spectralbio.pdf)
- Paper source: [`paper/spectralbio.tex`](paper/spectralbio.tex)
- Bibliography: [`paper/references.bib`](paper/references.bib)

## Agent Navigation

If an external agent needs orientation, start with this README.

- Use **`README.md`** for public context, repository structure, and the benchmark framing.
- Use **`SKILL.md`** for the exact operational reproduction path.

This is the intended navigation model for recovery-prone agent execution: README first for context, SKILL second for exact steps.

## Official Metrics

| Scope | Metric | Value |
| --- | --- | ---: |
| TP53 canonical | `0.55*frob_dist + 0.45*ll_proper` AUC | `0.7498` |
| BRCA1 bounded transfer | `ll_proper` AUC | `0.9174` |
| Reproducibility | delta | `0.0` |

## Quickstart

```bash
git clone https://github.com/DaviBonetto/SpectralBio.git
cd SpectralBio
python -m pip install uv
uv sync --frozen
uv run spectralbio canonical
```

This is the canonical public path.

## Expected Outputs

The canonical TP53 run is expected to materialize the following files under `outputs/canonical/`:

- `run_metadata.json`
- `inputs_manifest.json`
- `tp53_scores.tsv`
- `tp53_metrics.json`
- `summary.json`
- `roc_tp53.png`
- `manifest.json`
- `verification.json`

## Optional Full Validation

Run the bounded secondary transfer evaluation and contract checks only after the canonical TP53 path:

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

## Repository Map

- `src/spectralbio/` — public package, CLI, pipeline, and shared reproducibility logic
- `docs/` — truth contract, reproducibility notes, architecture, and competition-facing documentation
- `configs/` — frozen configuration presets for canonical and bounded transfer paths
- `benchmarks/` — frozen TP53 and BRCA1 benchmark inputs, sequences, manifests, and checksums
- `artifacts/expected/` — expected metrics, file contracts, schemas, and verification rules
- `outputs/` — canonical and transfer artifact outputs
- `publish/` — publication-facing surfaces for Hugging Face and clawRxiv
- `paper/` — manuscript source, bibliography, and compiled PDF
- `legacy/` — explicit provenance boundary for notebook-era and compatibility-era material

## Trust and Verification

The repository is governed by a narrow source-of-truth hierarchy led by:

1. `docs/truth_contract.md`
2. `docs/reproducibility.md`
3. `artifacts/expected/*`
4. `outputs/canonical/*`

Trust in the artifact comes from:

- frozen benchmark inputs and manifests
- explicit expected metrics and file schemas
- generated canonical output manifests
- repository-level verification via `uv run spectralbio verify`
- preflight checks via `uv run python scripts/preflight.py`

The release bundle under `artifacts/release/claw4s_2026/` is a public handoff mirror, not a separate source of truth.

## Documentation

- Truth contract: [`docs/truth_contract.md`](docs/truth_contract.md)
- Reproducibility notes: [`docs/reproducibility.md`](docs/reproducibility.md)
- Competition context: [`docs/competition/claw4s_context.md`](docs/competition/claw4s_context.md)
- Submission checklist: [`docs/competition/submission_checklist.md`](docs/competition/submission_checklist.md)
- Agent reproduction surface: [`SKILL.md`](SKILL.md)

## License

This repository is released under the **MIT License**. See [`LICENSE`](LICENSE).

## Legacy Boundary

The old notebook-era `colab/`, benchmark-facing compatibility payloads, and pre-rebuild submission flow are preserved only under `legacy/` for provenance. They are not canonical execution surfaces.
