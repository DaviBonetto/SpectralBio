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

SpectralBio is a research reproducibility artifact delivered as a thin Hugging Face Space over the shared repository core.

## Benchmark Contract

- Primary benchmark: `TP53 canonical executable benchmark`
- Secondary benchmark: `bounded transfer on a fixed BRCA1 subset (N=100)`
- Transfer framing: `secondary transfer evaluation without retraining`
- Adaptation note: `adaptation recipe only`
- Provenance-only data: `BRCA1_full_filtered_v1.json` stays outside the default Space path.

The live Space is published from a repository-root mirror whose root README points to `publish/hf_space/app.py`, while all scoring, validation, benchmark membership, and reference calibration stay under `src/spectralbio/`.

## Official Metrics

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

TP53 presets are the default path. BRCA1 remains a bounded secondary transfer example without retraining.
