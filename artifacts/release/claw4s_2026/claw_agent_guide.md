# SpectralBio Agent Guide

## Purpose

This guide is the execution manual for agents using the public SpectralBio repository. Prefer replay first. Use regeneration only when the task requires the broader deterministic paper-grade bundle.

## Legacy vs Replay vs Regeneration

- **Legacy path** -> original TP53 canonical plus bounded BRCA1 transfer contract
- **Replay path** -> public fast multi-target frozen audit route
- **Regeneration path** -> deterministic broader scientific audit route

## Command Routing

| Goal | Command |
|---|---|
| Check environment and offline readiness | `uv run spectralbio preflight --json --cpu-only --offline` |
| Diagnose failures | `uv run spectralbio doctor --json --cpu-only --offline` |
| Fast TP53 anchor replay | `uv run spectralbio replay --target tp53 --json --cpu-only --offline` |
| Fast BRCA2 flagship replay | `uv run spectralbio replay --target brca2 --json --cpu-only --offline` |
| Fast TSC2 replay-ready transfer replay | `uv run spectralbio replay --target tsc2 --json --cpu-only --offline` |
| Fast CREBBP replay-ready transfer replay | `uv run spectralbio replay --target crebbp --json --cpu-only --offline` |
| Check all public replay surfaces | `uv run spectralbio replay-audit --json --cpu-only --offline` |
| Verify a replay target bundle | `uv run spectralbio verify --target tp53 --json --cpu-only --offline` |
| Validate the older TP53/BRCA1 bounded contract | `uv run spectralbio verify-legacy` |
| Use the backward-compatible older legacy verify entrypoint | `uv run spectralbio verify` |
| Emit structured stats | `uv run spectralbio stats-report --target brca2 --json --cpu-only --offline` |
| Emit bounded sensitivity grid | `uv run spectralbio sensitivity --target brca2 --json --cpu-only --offline` |
| Materialize deterministic regeneration bundle | `uv run spectralbio regenerate --target brca2 --json --cpu-only --offline` |
| Materialize scientific audit surface | `uv run spectralbio regenerate --surface portability --json --cpu-only --offline` |
| Materialize the paper bundle | `uv run spectralbio reproduce-all --json --cpu-only --offline` |
| Scaffold a new target | `uv run spectralbio adapt --gene TSC2 --variants path/to/variants.csv --reference path/to/reference.fasta --json` |
| Emit bounded applicability diagnostics | `uv run spectralbio applicability --gene TSC2 --variants path/to/variants.csv --reference path/to/reference.fasta --json` |
| Explain a status file | `uv run spectralbio explain-status --path outputs/status/latest/status.json --json` |

## Runtime Expectations

Approximate local runtimes measured on the current frozen repository bundle:

| Command | Typical local runtime |
|---|---:|
| `preflight` | ~1.3 s |
| `doctor` | ~1.3 s |
| `replay --target tp53` | ~1.5 s |
| `replay --target brca2` | ~1.3 s |
| `replay-audit` | ~1.9 s |
| `reproduce-all` | ~1.9 s |

This timing refers to frozen deterministic paper-bundle materialization, not raw heavyweight scientific recomputation.

## Replay-First Policy

- Prefer `replay` and `replay-audit` for all cold-start inspection.
- Replay is CPU-only and frozen by design.
- Replay does not claim universal recomputation of the manuscript.

## Verification Semantics

Legacy verify:

- `uv run spectralbio verify-legacy`
- `uv run spectralbio verify`

Meaning:

- validates the original TP53 canonical plus bounded BRCA1 transfer contract
- `verify-legacy` is the preferred explicit legacy command
- `verify` without `--target` remains supported for backward compatibility

Replay verify:

- `uv run spectralbio verify --target <target> --json --cpu-only --offline`

Meaning:

- validates one newer replay target bundle

## Expected Outputs

Every core command writes a canonical per-run status bundle under `outputs/status/<run_id>/`:

- `status.json`
- `stdout.log`
- `stderr.log`
- `command.txt`

Doctor also writes:

- `diagnosis.json`

`outputs/status/latest/` is a convenience mirror of the latest bundle, not the canonical record.

Replay targets write their local bundle under `outputs/replay/<target>/`:

- `summary.json`
- `verification.json`
- `provenance.json`
- `manifest.json`
- `metrics.json`
- `checksums.json`
- `status.json`

## PASS / FAIL Semantics

`PASS` means:

- execution completed
- required artifacts were written
- schemas validated
- checksums matched when applicable
- contract tolerances passed when applicable

`FAIL` means at least one required contract check failed and should be treated as blocking.

## Diagnosis Categories

Current structured doctor categories include:

- `healthy`
- `environment_failure`

Use `diagnosis.json` plus `status.json` to decide the next command.

## Common Failure Modes

- missing frozen asset during offline replay
- checksum mismatch in a replay bundle
- schema drift in `summary.json`, `manifest.json`, `provenance.json`, or `status.json`
- running target verification before the corresponding replay bundle exists

## Recovery

- Missing replay bundle: rerun `uv run spectralbio replay --target <target> --json --cpu-only --offline`
- Missing environment assets: rerun `uv run spectralbio preflight --json --cpu-only --offline` and restore the listed files
- Checksum mismatch: restore the affected frozen benchmark directory and rerun replay
- Schema failure: inspect the file named in the verification report and restore the expected contract shape
- Unknown status bundle: run `uv run spectralbio explain-status --path outputs/status/latest/status.json --json`

## Role Glossary

- `validation_anchor`: default executable validation center
- `flagship_non_anchor_canonical_target`: strongest non-anchor replay target
- `replay_ready_transfer_surface`: bounded public portability witness
- `negative_guardrail`: explicit retained negative boundary
- `closure_tribunal_surface`: final harsh closure boundary surface

## Target Roles

- `TP53`: validation anchor
- `BRCA2`: flagship non-anchor canonical target
- `TSC2`: replay-ready transfer surface
- `CREBBP`: replay-ready transfer surface
- `BRCA1`: negative guardrail and bounded auxiliary executable surface
- `MSH2`: negative guardrail

## Bounded Onboarding

`adapt` scaffolds a new target onboarding surface but does not validate that target as claim-bearing.

`applicability` emits bounded diagnostics only and does not certify transfer success.

A new target becomes claim-bearing only after it has its own independently frozen benchmark surface, expected outputs, verification path, and bounded interpretation consistent with the manuscript.

## Do Not Overclaim

- No universal generalization
- No full closure
- No cross-protein law
- No plug-and-play for any gene
- No claim that all replay-ready targets are equal to TP53

## Interpretation Boundary

Block 13 strengthens target-level portability. Block 14 keeps the harsh final closure tribunal mixed. Those truths must coexist in any downstream interpretation.
