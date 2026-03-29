# Architecture

## Repository Layers

SpectralBio is now organized into four explicit layers:

1. Frozen benchmark and provenance data under `benchmarks/` and `legacy/`
2. Shared scientific core under `src/spectralbio/`
3. Publish surfaces under `publish/` and compatibility wrappers under `huggingface/`
4. Public presentation and frozen handoff material under `assets/`, `paper/`, `docs/`, and `artifacts/release/`

## Benchmark Contract

SpectralBio exposes one canonical executable benchmark and one bounded secondary transfer evaluation.

- Primary benchmark: `TP53 canonical executable benchmark`
- Secondary benchmark: `bounded transfer on a fixed BRCA1 subset (N=100)`
- Transfer framing: `secondary transfer evaluation without retraining`
- Adaptation note: `adaptation recipe only`
- Provenance-only data: `BRCA1_full_filtered_v1.json` is preserved for provenance and transfer-subset derivation, not as a canonical scored benchmark.

## Official Metrics

| Scope | Metric | Value |
| --- | --- | ---: |
| TP53 canonical | `0.55*frob_dist + 0.45*ll_proper` AUC | `0.7498` |
| BRCA1 bounded transfer | `ll_proper` AUC | `0.9174` |
| Reproducibility | delta | `0.0` |

Metric verification follows the `0.0001` tolerance declared in `artifacts/expected/verification_rules.json`.

## Core Modules

- `src/spectralbio/data/`: frozen benchmark loading, manifests, schema helpers
- `src/spectralbio/pipeline/`: canonical run, transfer run, feature computation, verification
- `src/spectralbio/demo/`: single-variant scoring reused by the demo
- `src/spectralbio/utils/`: IO, hashing, determinism
- `src/spectralbio/cli.py`: one canonical command surface

## Command Surface

The repository exposes one canonical CLI:

- `spectralbio canonical`
- `spectralbio transfer`
- `spectralbio verify`
- `spectralbio export-hf-space`
- `spectralbio export-hf-dataset`
- `spectralbio release`

`spectralbio canonical` is the default executable path for TP53. `spectralbio transfer` preserves the secondary BRCA1 evidence path without redefining the canonical benchmark.

## Publish Surfaces

- `publish/hf_space/` is a thin client that imports shared logic from `src/spectralbio/`
- `publish/hf_dataset/` contains the aligned dataset-facing card and manifest
- `publish/clawrxiv/` is reserved for submission-facing bundle content

Legacy `huggingface/` now acts as a compatibility wrapper only.

## Demo Hard Rule

The Hugging Face Space must not own independent scientific logic.

- all scoring must come from `src/spectralbio/`
- all feature computation must come from `src/spectralbio/`
- all validation and reference calibration must come from `src/spectralbio/`
- the demo may render, cache, and format results
- the demo may not become a second scientific implementation
