# Reproducibility Notes

## Reproducibility Split

SpectralBio now exposes two explicit execution tiers.

### Tier A: Replay / Verification

- fast
- CPU-only
- frozen
- offline-capable
- artifact-first
- machine-checkable

Main commands:

```bash
uv run spectralbio preflight --json --cpu-only --offline
uv run spectralbio replay-audit --json --cpu-only --offline
```

### Tier B: Regeneration / Audit

- deterministic
- broader
- provenance-rich
- slower than replay
- still bounded and frozen where necessary

Main commands:

```bash
uv run spectralbio regenerate --target tp53 --json --cpu-only --offline
uv run spectralbio regenerate --target brca2 --json --cpu-only --offline
uv run spectralbio regenerate --surface scale-repair --json --cpu-only --offline
uv run spectralbio regenerate --surface portability --json --cpu-only --offline
uv run spectralbio regenerate --surface holdout-control --json --cpu-only --offline
uv run spectralbio reproduce-all --json --cpu-only --offline
```

## Canonical Replay Surfaces

| Target | Role | Command |
|---|---|---|
| `TP53` | validation anchor | `uv run spectralbio replay --target tp53 --json --cpu-only --offline` |
| `BRCA2` | flagship non-anchor canonical target | `uv run spectralbio replay --target brca2 --json --cpu-only --offline` |
| `TSC2` | replay-ready transfer surface | `uv run spectralbio replay --target tsc2 --json --cpu-only --offline` |
| `CREBBP` | replay-ready transfer surface | `uv run spectralbio replay --target crebbp --json --cpu-only --offline` |

## Compatibility Replay Surfaces

These older commands remain supported:

```bash
uv run spectralbio canonical
uv run spectralbio transfer
uv run spectralbio verify
uv run spectralbio verify-legacy
```

They preserve:

- `outputs/canonical/`
- `outputs/transfer/`

Semantics:

- `verify` without `--target` preserves the original TP53 plus bounded BRCA1 contract check.
- `verify --target <target>` validates one newer replay target bundle.

## Output Contract

### Universal command bundle

Every core command writes:

- `outputs/status/<run_id>/status.json`
- `outputs/status/<run_id>/stdout.log`
- `outputs/status/<run_id>/stderr.log`
- `outputs/status/<run_id>/command.txt`

`doctor` also writes:

- `outputs/status/<run_id>/diagnosis.json`

### Replay bundle

Every replay target writes:

- `summary.json`
- `verification.json`
- `provenance.json`
- `manifest.json`
- `metrics.json`
- `checksums.json`
- `status.json`

### Regeneration bundle

Every regeneration target or surface writes:

- `raw_inputs_manifest.json`
- `intermediate_manifest.json`
- `summary.json`
- `verification.json`
- `provenance.json`
- `stats_report.json`
- `diagnosis.json`
- `checksums.json`

## Determinism

Deterministic behavior is enforced by:

- frozen replay artifacts
- fixed seeds where relevant
- stable benchmark contracts under `benchmarks/`
- strict schema files under `schemas/`
- checksum validation of emitted replay and regeneration bundles

## Runtime Expectations

Approximate local runtimes measured on the current frozen repository bundle:

| Command | Typical local runtime | Notes |
|---|---:|---|
| `preflight` | ~1.3 s | environment and asset checks |
| `doctor` | ~1.3 s | structured diagnosis over the same health surface |
| `replay --target tp53` | ~1.5 s | validation anchor replay |
| `replay --target brca2` | ~1.3 s | flagship non-anchor replay |
| `replay-audit` | ~1.9 s | all replay targets plus aggregate check |
| `reproduce-all` | ~1.9 s | deterministic frozen paper-grade bundle |

Replay is intentionally the public default because it makes the claim inspectable without demanding a heavyweight recomputation every time.

## Success Conditions

### Replay tier

- `spectralbio preflight` returns `PASS`
- each `spectralbio replay --target ...` returns `PASS`
- `spectralbio replay-audit` returns `PASS`
- all replay bundles are schema-valid and checksum-valid

### Compatibility tier

- `spectralbio canonical` returns `PASS`
- `spectralbio transfer` returns `PASS`
- `spectralbio verify` returns `PASS`

### Regeneration tier

- regeneration bundles materialize deterministically
- `spectralbio reproduce-all` writes `outputs/paper/*`
- paper bundle includes checksums and provenance

## Troubleshooting Order

1. `uv run spectralbio doctor --json --cpu-only --offline`
2. inspect `outputs/status/latest/status.json`
3. rerun the specific replay target
4. only then escalate to regeneration if the question is scientific rather than mechanical

## Interpretation Boundary

Reproducibility in this repository does **not** mean that every scientific surface is re-derived live from scratch on every run.

It means:

- the public executable anchor is replayable and machine-checkable
- the flagship and replay-ready transfer surfaces are replayable with frozen contracts
- the broader audit surfaces are materialized deterministically with provenance
- the final harsh closure tribunal remains mixed

That last line is part of reproducibility, not an exception to it.
