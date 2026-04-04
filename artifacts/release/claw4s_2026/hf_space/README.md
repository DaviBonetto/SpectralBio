---
title: SpectralBio Demo
emoji: "🧬"
colorFrom: red
colorTo: yellow
sdk: gradio
sdk_version: 6.9.0
app_file: publish/hf_space/app.py
pinned: false
preload_from_hub:
  - facebook/esm2_t30_150M_UR50D
---

# SpectralBio Demo

SpectralBio is a `research reproducibility artifact` delivered as a thin Hugging Face Space over the shared repository core. The manuscript's flagship scientific result lives on `BRCA2`, while this live Space intentionally exposes only the frozen executable replay center.

## Public Hierarchy

- Flagship scientific result: `BRCA2` covariance-aware augmentation against a stronger five-model ESM-1v baseline
- Validation anchor: `TP53` is the only frozen public canonical replay surface
- Breadth surface: support-ranked top-25 feasible panel
- Boundary surfaces: protocol sweep and BRCA1 failure analysis
- Auxiliary executable surface: `bounded transfer on a fixed BRCA1 subset (N=100) without retraining`

## Space Contract

- Primary benchmark: `TP53 canonical executable benchmark`
- Secondary benchmark: `bounded transfer on a fixed BRCA1 subset (N=100)`
- Transfer framing: `secondary transfer evaluation without retraining`
- Adaptation note: `adaptation recipe only`
- Provenance-only data: `BRCA1_full_filtered_v1.json` stays outside the default Space path

The live Space is published from a repository-root mirror whose root README points to `publish/hf_space/app.py`, while all scoring, validation, benchmark membership, and reference calibration stay under `src/spectralbio/`. BRCA2 remains the paper-facing flagship result and is not recomputed by the default Space path.

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

## Stable Payload

The `/score_variant` Gradio endpoint returns a versioned machine-readable payload with these top-level sections:

- `contract_version`
- `request`
- `result`
- `benchmark_context`
- `official_metrics`

TP53 presets are the default path. BRCA1 remains a bounded secondary transfer example without retraining. BRCA2 scientific centrality is represented in the paper-aligned audit surfaces, not in the live scoring workflow.
