# SpectralBio Truth Contract

## Source Of Truth Order

1. `docs/truth_contract.md`
2. `docs/reproducibility.md`
3. `artifacts/expected/expected_metrics.json`
4. `artifacts/expected/expected_files.json`
5. `artifacts/expected/output_schema.json`
6. `artifacts/expected/verification_rules.json`
7. `outputs/canonical/summary.json`
8. `outputs/canonical/verification.json`

Supporting corroborators:

- `benchmarks/manifests/tp53_canonical_manifest.json`
- `benchmarks/manifests/brca1_transfer_manifest.json`
- `benchmarks/manifests/source_snapshot.json`
- `benchmarks/manifests/checksums.json`
- `benchmarks/benchmark_registry.json`

## Claim Taxonomy

1. `validation_anchor`
2. `flagship_non_anchor_canonical_target`
3. `replay_ready_transfer_surface`
4. `auxiliary_bounded_executable_surface`
5. `negative_guardrail`
6. `closure_tribunal_surface`

## Current Truthful Claim Set

### Executable anchor

- `TP53` remains the default executable validation anchor.
- canonical compatibility command:
  - `uv run spectralbio canonical`
- replay-first command:
  - `uv run spectralbio replay --target tp53 --json --cpu-only --offline`

### Bounded auxiliary executable surface

- `BRCA1_transfer100` remains bounded and secondary.
- compatibility command:
  - `uv run spectralbio transfer`
- it must not be promoted to co-primary benchmark status.

### Flagship non-anchor canonical target

- `BRCA2` is the strongest non-anchor replay surface.
- replay command:
  - `uv run spectralbio replay --target brca2 --json --cpu-only --offline`
- this does not replace TP53 as the validation anchor.

### Replay-ready transfer surfaces

- `TSC2`
- `CREBBP`

These surfaces are public, frozen, replayable, and bounded. They are not flagship canonical centerpieces and they are not a license for universal portability claims.

### Negative guardrails

- `BRCA1`
- `MSH2`

These guardrails must remain explicit in code, docs, and interpretation.

### Closure boundary

- Block 13 strengthens target-level portability across `TP53`, `BRCA2`, `TSC2`, and `CREBBP`.
- Block 14 keeps the harsh final holdout/control tribunal mixed.

Interpretation:

- target-level portability strengthened
- model-level closure not achieved

## Forbidden Claims

- universal generalization
- full closure
- broad cross-protein law
- universal alpha transfer
- plug-and-play for any gene
- claim that all replay-ready surfaces are equal to TP53
- claim that BRCA2/TSC2/CREBBP are the default executable anchor

## Command Contract

### Preferred public route

```bash
uv sync --frozen
uv run spectralbio preflight --json --cpu-only --offline
uv run spectralbio replay-audit --json --cpu-only --offline
```

### Single-target replay

```bash
uv run spectralbio replay --target tp53 --json --cpu-only --offline
uv run spectralbio replay --target brca2 --json --cpu-only --offline
uv run spectralbio replay --target tsc2 --json --cpu-only --offline
uv run spectralbio replay --target crebbp --json --cpu-only --offline
```

### Compatibility commands

```bash
uv run spectralbio canonical
uv run spectralbio transfer
uv run spectralbio verify
uv run spectralbio verify-legacy
```

Interpretation:

- `verify` without `--target` preserves the older TP53 plus bounded BRCA1 executable contract.
- `verify --target <target>` validates a newer replay benchmark bundle for that specific target.

## Mechanical Contract

Every core command must emit:

- `outputs/status/<run_id>/status.json`
- `outputs/status/<run_id>/stdout.log`
- `outputs/status/<run_id>/stderr.log`
- `outputs/status/<run_id>/command.txt`

`doctor` must also emit:

- `outputs/status/<run_id>/diagnosis.json`

Every replay target bundle must emit:

- `summary.json`
- `verification.json`
- `provenance.json`
- `manifest.json`
- `metrics.json`
- `checksums.json`
- `status.json`

## Benchmark Registry Truth

`benchmarks/benchmark_registry.json` is the machine-readable role map used by `spectralbio list-targets`.

Required role mapping:

- `TP53` -> `validation_anchor`
- `BRCA2` -> `flagship_non_anchor_canonical_target`
- `TSC2` -> `replay_ready_transfer_surface`
- `CREBBP` -> `replay_ready_transfer_surface`
- `BRCA1` -> `negative_guardrail`
- `MSH2` -> `negative_guardrail`
- `HOLDOUT_CONTROL` -> `closure_tribunal_surface`

## Bounded Extension Policy

`spectralbio adapt` creates a scaffold only.

`spectralbio applicability` emits bounded diagnostics only:

- `likely_helpful`
- `likely_bounded`
- `likely_not_recommended`

Neither command may be described as proof of universal transfer.
