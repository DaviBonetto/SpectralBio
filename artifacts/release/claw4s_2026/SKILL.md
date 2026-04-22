---
name: spectralbio-canonical-replay-and-portability-audit
description: Execute the frozen TP53 canonical replay, verify machine-checkable outputs, and inspect replay-ready portability surfaces across TP53, BRCA2, TSC2, and CREBBP, with BRCA1 and MSH2 preserved as negative guardrails. Reproduces the package's executable validation anchor and its final claim boundary: strengthened target-level portability with mixed model-level holdout/control closure.
allowed-tools: Bash(git *), Bash(python *), Bash(uv *), Bash(ls *), Bash(test *)
package_manager: uv
repo_url: https://github.com/DaviBonetto/SpectralBio
repo_root: .
python_version: ">=3.10"
---

# SpectralBio Skill

## What This Skill Proves

- `TP53` remains the default executable validation anchor.
- `BRCA2` is the flagship non-anchor canonical replay surface.
- `TSC2` and `CREBBP` are replay-ready transfer surfaces.
- `BRCA1` and `MSH2` remain explicit negative guardrails.
- replay is CPU-only, frozen, fast, and machine-checkable.
- the final holdout/control closure boundary remains mixed.

## What This Skill Does Not Prove

- not a universal upgrade
- not full closure
- not plug-and-play for any gene
- not a cross-protein law
- not a claim that covariance always helps
- not a claim that all replay-ready surfaces are equal

## Prerequisites

- run from the repository root
- Python `>=3.10`
- `uv` is the public package manager and entrypoint surface
- replay is designed for CPU-only and offline use once assets are present

## Which Command Should I Run?

| Goal | Command |
|---|---|
| Check environment before anything else | `uv run spectralbio preflight --json --cpu-only --offline` |
| Run the validation anchor only | `uv run spectralbio replay --target tp53 --json --cpu-only --offline` |
| Run the strongest non-anchor replay surface | `uv run spectralbio replay --target brca2 --json --cpu-only --offline` |
| Run all replay surfaces quickly | `uv run spectralbio replay-audit --json --cpu-only --offline` |
| Verify one replay target | `uv run spectralbio verify --target <target> --json --cpu-only --offline` |
| Validate the older legacy bounded contract | `uv run spectralbio verify-legacy` |
| Use the backward-compatible older legacy verify entrypoint | `uv run spectralbio verify` |
| Rebuild deterministic paper-grade outputs | `uv run spectralbio reproduce-all --json --cpu-only --offline` |
| Diagnose problems | `uv run spectralbio doctor --json --cpu-only --offline` |

## Runtime Expectations

Approximate local runtimes measured on the current frozen repository bundle:

| Command | Expected mode | Typical local runtime | Notes |
|---|---|---:|---|
| `preflight` | CPU/offline | ~1.3 s | environment, asset, and schema checks |
| `doctor` | CPU/offline | ~1.3 s | structured diagnosis over the same health surface |
| `replay --target tp53` | CPU/offline | ~1.5 s | validation anchor replay |
| `replay --target brca2` | CPU/offline | ~1.3 s | flagship non-anchor replay |
| `replay-audit` | CPU/offline | ~1.9 s | all replay targets plus aggregate check |
| `reproduce-all` | CPU/offline | ~1.9 s | frozen deterministic paper-bundle materialization, not raw heavyweight recomputation |

These are bounded replay/regeneration timings over frozen artifacts, not live heavyweight retraining or model download timings.

## Fastest Path

```bash
uv sync --frozen
uv run spectralbio preflight --json --cpu-only --offline
uv run spectralbio replay-audit --json --cpu-only --offline
```

This path validates the frozen public claim surface and is not the heavy raw scientific recomputation path.

If you only need the validation anchor:

```bash
uv run spectralbio replay --target tp53 --json --cpu-only --offline
```

## Replay Targets

| Target | Role | Command | Output |
|---|---|---|---|
| `TP53` | `validation_anchor` | `uv run spectralbio replay --target tp53 --json --cpu-only --offline` | `outputs/replay/tp53/` |
| `BRCA2` | `flagship_non_anchor_canonical_target` | `uv run spectralbio replay --target brca2 --json --cpu-only --offline` | `outputs/replay/brca2/` |
| `TSC2` | `replay_ready_transfer_surface` | `uv run spectralbio replay --target tsc2 --json --cpu-only --offline` | `outputs/replay/tsc2/` |
| `CREBBP` | `replay_ready_transfer_surface` | `uv run spectralbio replay --target crebbp --json --cpu-only --offline` | `outputs/replay/crebbp/` |

Each replay bundle writes:

- `summary.json`
- `verification.json`
- `provenance.json`
- `manifest.json`
- `metrics.json`
- `checksums.json`
- `status.json`

## Verify Semantics

`verify` has two distinct meanings and they should not be collapsed.

Legacy verify:

```bash
uv run spectralbio verify-legacy
uv run spectralbio verify
```

Meaning:

- validates the original TP53 canonical plus bounded BRCA1 transfer contract
- associated with `outputs/canonical/` and `outputs/transfer/`
- preserves the older bounded executable validation surface
- `verify-legacy` is the preferred explicit legacy command
- `verify` without `--target` remains supported for backward compatibility

Target replay verify:

```bash
uv run spectralbio verify --target tp53 --json --cpu-only --offline
uv run spectralbio verify --target brca2 --json --cpu-only --offline
uv run spectralbio verify --target tsc2 --json --cpu-only --offline
uv run spectralbio verify --target crebbp --json --cpu-only --offline
```

Meaning:

- validates the newer replay target bundle for that specific target
- uses the replay bundle schema, checksum, provenance, and verification layer

## Replay Audit

Use this when you want the fastest public multi-target route:

```bash
uv run spectralbio replay-audit --json --cpu-only --offline
```

This runs:

- TP53 replay
- BRCA2 replay
- TSC2 replay
- CREBBP replay
- aggregate replay verification

The merged summary is written to:

- `outputs/replay/replay_audit_summary.json`

## Legacy Commands

The older public commands still work and remain supported:

```bash
uv run spectralbio canonical
uv run spectralbio transfer
uv run spectralbio verify
```

Those commands preserve the original bounded executable contract:

- `TP53` canonical output directory: `outputs/canonical/`
- `BRCA1_transfer100` bounded auxiliary output directory: `outputs/transfer/`

Use them when you need the legacy TP53+BRCA1 contract specifically. Use replay for the stronger modern public route.

## Doctor / Diagnostics

```bash
uv run spectralbio doctor --json --cpu-only --offline
```

This command:

- inspects environment health
- checks replay asset availability
- checks schema and contract presence
- emits a structured diagnosis bundle
- recommends the next recovery action

Doctor writes:

- `outputs/status/<run_id>/status.json`
- `outputs/status/<run_id>/diagnosis.json`
- `outputs/status/<run_id>/stdout.log`
- `outputs/status/<run_id>/stderr.log`
- `outputs/status/<run_id>/command.txt`

Mirrored latest bundle:

- `outputs/status/latest/`

## Negative Guardrails

- `BRCA1` remains an explicit bounded auxiliary and anti-case surface in the legacy transfer path.
- `MSH2` remains an explicit negative portability guardrail in the final claim boundary.
- These negatives are part of the result and must not be erased or flattened into universal generalization.

## Full Regeneration

When you need deterministic paper-grade audit bundles rather than the fastest replay route:

```bash
uv run spectralbio regenerate --target tp53 --json --cpu-only --offline
uv run spectralbio regenerate --target brca2 --json --cpu-only --offline
uv run spectralbio regenerate --surface scale-repair --json --cpu-only --offline
uv run spectralbio regenerate --surface portability --json --cpu-only --offline
uv run spectralbio regenerate --surface holdout-control --json --cpu-only --offline
uv run spectralbio reproduce-all --json --cpu-only --offline
```

Regeneration writes under:

- `outputs/regeneration/`
- `outputs/paper/`

`reproduce-all` materializes:

- `outputs/paper/tables/`
- `outputs/paper/figures/`
- `outputs/paper/contracts/`
- `outputs/paper/checksums.json`
- `outputs/paper/provenance.json`
- `outputs/paper/reproduction_report.json`

## Stats, Sensitivity, And Onboarding

Structured stats:

```bash
uv run spectralbio stats-report --target tp53 --json --cpu-only --offline
uv run spectralbio stats-report --target brca2 --json --cpu-only --offline
```

Bounded sensitivity:

```bash
uv run spectralbio sensitivity --target tp53 --json --cpu-only --offline
uv run spectralbio sensitivity --target brca2 --json --cpu-only --offline
```

Bounded onboarding scaffold:

```bash
uv run spectralbio adapt --gene TSC2 --variants path/to/variants.csv --reference path/to/reference.fasta --json
```

Bounded applicability diagnostics:

```bash
uv run spectralbio applicability --gene TSC2 --variants path/to/variants.csv --reference path/to/reference.fasta --json
```

`adapt` scaffolds a new target onboarding surface but does not validate that target as claim-bearing.

`applicability` emits bounded diagnostics only and does not certify transfer success.

A new target becomes claim-bearing only after it has its own independently frozen benchmark surface, expected outputs, verification path, and bounded interpretation consistent with the manuscript.

## Role Glossary

- `validation_anchor`: default executable validation center
- `flagship_non_anchor_canonical_target`: strongest non-anchor replay target
- `replay_ready_transfer_surface`: bounded public portability witness
- `negative_guardrail`: explicit retained negative boundary
- `closure_tribunal_surface`: final harsh closure boundary surface

## Output Directory Map

- `outputs/replay/<target>/` - replay target bundles
- `outputs/regeneration/` - regeneration target and scientific surface bundles
- `outputs/paper/` - paper-grade deterministic outputs
- `outputs/status/<run_id>/` - canonical per-run status bundles
- `outputs/status/latest/` - convenience mirror of the latest bundle, not the canonical record

## Schemas And Contracts

Strict schemas live under `schemas/`:

- `status.schema.json`
- `summary.schema.json`
- `verification.schema.json`
- `provenance.schema.json`
- `stats_report.schema.json`
- `diagnosis.schema.json`
- `manifest.schema.json`
- `benchmark_contract.schema.json`

Replay benchmark contracts live under:

- `benchmarks/tp53/`
- `benchmarks/brca2/`
- `benchmarks/tsc2/`
- `benchmarks/crebbp/`
- `benchmarks/benchmark_registry.json`

Compatibility contract files remain under:

- `artifacts/expected/expected_metrics.json`
- `artifacts/expected/expected_files.json`
- `artifacts/expected/output_schema.json`
- `artifacts/expected/verification_rules.json`

## PASS / FAIL Semantics

A command reports `PASS` only if:

- execution completed
- required artifacts were written
- schemas validated
- checksums matched when applicable
- contract tolerances passed when applicable

A command reports `FAIL` if any required contract check fails.

## Troubleshooting

If replay fails:

1. Run `uv run spectralbio doctor --json --cpu-only --offline`
2. Inspect `outputs/status/latest/status.json`
3. Inspect `outputs/status/latest/diagnosis.json` when present
4. If the problem is a target bundle, rerun `uv run spectralbio replay --target <target> --json --cpu-only --offline`

Common failure classes:

- missing offline replay asset
- checksum mismatch
- schema drift
- missing replay bundle before target verification

## Success Criteria

Minimum public success:

- `uv run spectralbio preflight --json --cpu-only --offline` => `PASS`
- `uv run spectralbio replay --target tp53 --json --cpu-only --offline` => `PASS`
- `uv run spectralbio replay --target brca2 --json --cpu-only --offline` => `PASS`
- `uv run spectralbio replay --target tsc2 --json --cpu-only --offline` => `PASS`
- `uv run spectralbio replay --target crebbp --json --cpu-only --offline` => `PASS`
- `uv run spectralbio replay-audit --json --cpu-only --offline` => `PASS`

Compatibility success:

- `uv run spectralbio canonical` => `PASS`
- `uv run spectralbio transfer` => `PASS`
- `uv run spectralbio verify` => `PASS`

## Interpretation Boundaries

- `TP53` remains the executable validation anchor.
- `BRCA2` is the next full canonicalization target and flagship non-anchor replay surface.
- `TSC2` and `CREBBP` strengthen bounded portability as replay-ready transfer surfaces.
- `BRCA1` and `MSH2` remain negative guardrails.
- Block 13 strengthens target-level portability.
- Block 14 keeps the final holdout/control tribunal mixed.

That boundary is part of the result. Do not flatten it into universal generalization.
