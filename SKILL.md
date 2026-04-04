---
name: spectralbio-tp53-canonical-benchmark
description: Cold-start bootstrap the public SpectralBio repository, reproduce the frozen TP53 canonical replay surface, inspect the public BRCA2 scientific audit surfaces, optionally run the bounded BRCA1 transfer artifact, and verify the frozen repository contract from a Bash-compatible terminal.
allowed-tools: Bash(git *), Bash(python *), Bash(uv *), Bash(ls *), Bash(test *)
package_manager: uv
repo_url: https://github.com/DaviBonetto/SpectralBio
repo_root: .
canonical_output_dir: outputs/canonical
secondary_output_dir: outputs/transfer
python_version: ">=3.10"
---

# SpectralBio Public Replay And Audit Surface

## Mission

Use this skill to reproduce the public SpectralBio repository through its frozen executable replay surface and its associated public scientific audit surfaces.

- Flagship scientific result: covariance-aware augmentation against a stronger external baseline on `BRCA2`
- Validation anchor: `TP53` is the only frozen public canonical replay surface
- Breadth surface: support-ranked top-25 feasible panel
- Auxiliary executable transfer surface: `bounded transfer on a fixed BRCA1 subset (N=100) without retraining`
- Transfer framing: `secondary transfer evaluation without retraining`
- Repository framing: `research reproducibility artifact`
- Anything beyond the released replay surfaces and documented public audits: `adaptation recipe only`

## Execution Envelope

- Shell: `Bash-compatible shell`
- Python: `>= 3.10` required (tested on 3.11)
- Internet: required for repository clone and `uv sync --frozen`; the canonical public path itself uses bundled frozen references
- GPU: **not** required for the canonical public contract
- Canonical execution model: deliberate frozen-artifact materialization for reproducibility, verification, and judge-safe execution
- Model metadata: `facebook/esm2_t30_150M_UR50D` is recorded in `run_metadata.json` as provenance metadata for the frozen contract
- Run from the repository root
- If the repository is already cloned and you are already at its root, skip Step 0

## Runtime Expectations

- Canonical public path: `uv sync --frozen` then `uv run spectralbio canonical`; this is a frozen-artifact reproducibility path for TP53, not a live model-recomputation workflow
- Typical canonical runtime after `uv sync --frozen`: fast CPU-safe frozen-artifact materialization in the current repo state; supplementary research-path rerun timings (14-15s) are documented separately in the paper and are not part of the canonical verification contract runtime surface
- It validates the frozen TP53 config, loads bundled TP53 variants and score references, computes contract metrics from those frozen references, and writes the canonical artifact bundle plus the canonical-side `verification.json` report
- It does **not** perform live HuggingFace download, live ESM2 embedding recomputation, or training
- The BRCA2 flagship result is exposed through paper-aligned public audit surfaces and is **not** recomputed by `spectralbio canonical`

## Scientific And Executable Contract

### Manuscript Scientific Center

- `BRCA2` is the flagship scientific result: ESM-1v baseline `0.6324` becomes covariance-augmented `0.6890`, for paired gain `0.0566`, paired 95% CI `[0.0131, 0.1063]`, and empirical `p = 0.0010`
- `TP53` is the validation anchor that shows the covariance signal is real, auditable, and executable on a frozen public surface
- The support-ranked top-25 feasible panel is the performance-blind breadth surface
- `BRCA1` is a boundary and failure-analysis surface, not a co-primary scientific center

### Frozen Executable Replay Center

- `TP53` is the only canonical scored benchmark and the default executable path
- `BRCA1_transfer100` remains a bounded auxiliary transfer surface only
- The cold-start public path is still `uv sync --frozen` then `uv run spectralbio canonical`
- `BRCA2` currently enters the public release as a scientific audit surface, not as the default frozen CLI replay target

## Scope And Non-Claims

### Scope

- `BRCA2` is the manuscript's flagship scientific result
- `TP53` is the only canonical scored benchmark and default executable path
- `BRCA1_transfer100` is bounded auxiliary transfer evidence only
- The public execution surface is `uv`
- The true CLI namespace is `spectralbio`

### Non-Claims

- No `any protein` claim
- No `works on any protein` claim
- No strong, exceptional, or broad cross-protein generalization claim
- No BRCA1 co-primary benchmark framing
- No claim that BRCA2 is already a frozen default CLI replay benchmark
- No benchmark claim beyond TP53 replay plus the fixed BRCA1 subset without separate validation
- No clinical deployment or clinical use framing

## Truth Boundary

If you need repository truth rather than guess, anchor to these files:

- `docs/truth_contract.md`
- `docs/reproducibility.md`
- `artifacts/expected/expected_metrics.json`
- `artifacts/expected/expected_files.json`
- `artifacts/expected/output_schema.json`
- `artifacts/expected/verification_rules.json`
- `outputs/canonical/summary.json` - field: `metrics.computed_auc_best_pair`
- `outputs/canonical/verification.json`

If you need manuscript-aligned scientific framing and public audit surfaces, inspect these next:

- `abstract.md`
- `content.md`
- `notebooks/final_accept_part3_esm1v_augmentation_A100.ipynb`
- `notebooks/final_accept_part4_brca2_canonicalization_A100.ipynb`
- `notebooks/final_accept_part1_support_panel.ipynb`
- `notebooks/final_accept_part5_protocol_sweep_A100.ipynb`
- `notebooks/final_accept_part6_panel25_brca1_failure_L4.ipynb`

Do **not** promote legacy wording, wrapper convenience, or stale surfaces above these truth anchors.

## When to Use This Skill

- Case 1 - Canonical replay
  - Goal: reproduce the frozen TP53 public replay surface
  - Path: use the canonical path from the repository root
  - Result: frozen-artifact reproducibility path under `outputs/canonical/`
  - Priority: fastest and default route
- Case 2 - Public scientific audit
  - Goal: inspect the manuscript-aligned scientific center without changing the executable contract
  - Path: inspect `abstract.md`, `content.md`, and the BRCA2 / panel notebooks listed in `## Truth Boundary`
  - Result: BRCA2 flagship framing, TP53 validation role, breadth, and boundary surfaces become explicit
  - Constraint: these audit surfaces complement the TP53 replay path; they do not replace it
- Case 3 - Optional bounded auxiliary validation
  - Goal: check `BRCA1_transfer100` as bounded auxiliary executable evidence
  - Order: use this only after canonical TP53 understanding or execution
  - Path: run the optional transfer / verify / preflight path only when that bounded secondary check is required
  - Constraint: secondary evidence only, without retraining
- Case 4 - Out of scope
  - Stop if the task is adapting to a new target
  - Stop if the task requires live heavy recomputation from scratch
  - Stop if the task asks for broad generalization claims beyond the current reproducibility contract
  - Next step: use `## Adaptation Architecture`; this repository keeps that work under `adaptation recipe only`

## Step 0 - Clone The Public Repository

Run this only if the repository is not already present locally.

```bash
git clone https://github.com/DaviBonetto/SpectralBio.git
cd SpectralBio
ls pyproject.toml docs/truth_contract.md
```

The `ls` command confirms you are at the correct repository root. If either file is missing, you are in the wrong directory.

## Step 1 - Ensure `uv` Is Available

Check whether `uv` is already available:

```bash
uv --version
```

If that command fails, install `uv` with Python and check again:

```bash
python --version
python -m pip install --upgrade uv
uv --version
```

If `uv` is still not found after installation, reopen the shell or ensure your normal Python scripts directory is on `PATH`. Do not change the public command surface because of a local shell-path quirk.

## Step 2 - Sync The Locked Environment

```bash
uv sync --frozen
```

This installs the locked dependency set from `uv.lock` at the repository root. The `--frozen` flag prevents any dependency resolution or version drift. Both `pyproject.toml` and `uv.lock` must be present.

## Step 3 - Run The Canonical TP53 Replay Surface

```bash
uv run spectralbio canonical
```

This is the canonical public execution path. It validates the frozen TP53 config, loads `benchmarks/tp53/tp53_canonical_v1.json` plus the bundled score reference `benchmarks/tp53/tp53_scores_v1.json`, computes the contract metrics from those frozen score rows, copies the frozen TP53 ROC figure, and writes the canonical artifact bundle plus the canonical-side `verification.json` report to `outputs/canonical/`. Optional full validation remains separate below.

This is a deliberate frozen-artifact materialization path for reproducibility, verification, and judge-safe execution. The canonical public path does **not** depend on a live HuggingFace/ESM2 download. It validates the manuscript's TP53 anchor but does **not** rerun the BRCA2 flagship analysis.

## Step 4 - Confirm The Canonical Artifact Bundle

Required files under `outputs/canonical/`:

- `run_metadata.json`
- `inputs_manifest.json`
- `tp53_scores.tsv`
- `tp53_metrics.json`
- `summary.json`
- `roc_tp53.png`
- `manifest.json`
- `verification.json`

Confirm all files exist and are non-empty. This loop reports per-file status:

```bash
for f in run_metadata.json inputs_manifest.json tp53_scores.tsv tp53_metrics.json summary.json roc_tp53.png manifest.json verification.json; do
  test -s "outputs/canonical/$f" && echo "OK: $f" || echo "MISSING or EMPTY: $f"
done
ls outputs/canonical
```

All eight lines must read `OK:` for the artifact bundle to be complete.

## Step 5 - Validate Canonical Metrics

Confirm that `outputs/canonical/summary.json` reports the expected AUC within the declared tolerance. The computed AUC lives at `metrics.computed_auc_best_pair` inside the JSON object:

```bash
python -c "
import json, sys
with open('outputs/canonical/summary.json') as f:
    s = json.load(f)
try:
    auc = s['metrics']['computed_auc_best_pair']
except KeyError:
    sys.exit('FAIL: metrics.computed_auc_best_pair not found in outputs/canonical/summary.json - check field names')
official = s['metrics'].get('official_auc_best_pair', 0.7498)
delta = abs(auc - official)
if delta > 0.0001:
    sys.exit(f'FAIL: computed AUC {auc:.6f} deviates from official {official:.4f} by {delta:.6f} (tolerance 0.0001)')
print(f'OK: computed_auc_best_pair={auc:.6f} | official={official:.4f} | delta={delta:.6f} | tolerance=0.0001')
"
```

A passing run prints `OK: computed_auc_best_pair=0.749751...` and exits 0. This is the machine-checkable form of the replay contract. If this check fails, do not hand-edit outputs - rerun Step 3 or inspect `outputs/canonical/verification.json`.

## What Creates And Checks The Files

- `uv run spectralbio canonical`: validates `configs/tp53_canonical.yaml`, loads the frozen TP53 variants and bundled score reference, computes contract metrics from those frozen rows, copies the frozen TP53 figure, and writes the full TP53 artifact bundle to `outputs/canonical/`
- `uv run spectralbio transfer`: writes the bounded BRCA1 auxiliary artifact bundle to `outputs/transfer/` from the frozen fixed first-100 subset
- `uv run spectralbio verify`: validates canonical and transfer outputs against the frozen repository contract and writes a `PASS` / `FAIL` report to `outputs/canonical/verification.json`
- `uv run python scripts/preflight.py`: reruns canonical and transfer generation, stages the export surfaces, and then checks output contract plus wording-sensitive repository assertions

Do **not** hand-edit outputs to force success. Use repository commands only.

## Canonical Success Criteria

The canonical path is successful only if **all** of the following are true:

- `uv sync --frozen` exits with code 0
- `uv run spectralbio canonical` exits with code 0
- Step 4 loop reports `OK:` for all eight required files
- Step 5 metric check prints `OK:` and exits 0 (`computed_auc_best_pair` within 0.0001 of `official_auc_best_pair`)
- TP53 remains the primary and default executable benchmark path
- Canonical success establishes the frozen TP53 replay surface and validation anchor; it does **not** by itself rerun BRCA2 notebooks or panel analyses
- No step above required BRCA1 transfer, `verify`, `preflight`, GPU, or paper build to count canonical TP53 success

## Optional Full Validation

Run this only when you need the bounded auxiliary BRCA1 evidence and the full repository validation pass **after** the canonical TP53 run.

```bash
uv run spectralbio transfer
uv run spectralbio verify
uv run python scripts/preflight.py
```

This optional validation path keeps BRCA1 bounded and auxiliary. It is **not** the default path, **not** the flagship scientific result, and **not** required for canonical TP53 success.

Expected transfer outputs under `outputs/transfer/`:

- `summary.json`
- `variants.json`
- `manifest.json`

Confirm them if you ran the optional path:

```bash
for f in summary.json variants.json manifest.json; do
  test -s "outputs/transfer/$f" && echo "OK: $f" || echo "MISSING or EMPTY: $f"
done
ls outputs/transfer
```

## Verification Contract

### Machine-Verified Replay Contract

- TP53 canonical score formula: `0.55*frob_dist + 0.45*ll_proper`
- TP53 official AUC: `0.7498`
- TP53 computed AUC (`metrics.computed_auc_best_pair`): `0.749751...` (delta = 0.0 when rounded to 4 decimal places)
- BRCA1 bounded transfer AUC: `0.9174`
- Reproducibility delta: `0.0`
- Verification tolerance: `0.0001`

### Scientific Audit Contract

- BRCA2 flagship augmentation result: ESM-1v `0.6324` to covariance-plus-ESM-1v `0.6890`
- BRCA2 paired delta over ESM-1v: `0.0566` with paired 95% CI `[0.0131, 0.1063]`
- BRCA2 covariance-permutation audit: empirical `p = 0.0010`
- TP53 remains the only frozen public canonical replay surface
- The support-ranked top-25 feasible panel remains the breadth surface
- BRCA1 remains bounded auxiliary executable evidence and a boundary surface, not a co-primary flagship result

Report drift if filenames change, replay metrics move outside tolerance, TP53 stops being the default executable path, or manuscript-facing text stops distinguishing BRCA2 scientific centrality from TP53 replay centrality.

## Public Scientific Audit Surfaces

Use these surfaces when the task is paper alignment, scientific review, or judge-facing explanation rather than cold-start CLI replay:

- `notebooks/final_accept_part3_esm1v_augmentation_A100.ipynb` - BRCA2 flagship stronger-baseline augmentation audit
- `notebooks/final_accept_part4_brca2_canonicalization_A100.ipynb` - BRCA2 benchmark qualification and next-surface evidence
- `notebooks/final_accept_part1_support_panel.ipynb` - support-ranked top-25 breadth surface
- `notebooks/final_accept_part5_protocol_sweep_A100.ipynb` - checkpoint, window, and layer sensitivity boundary analysis
- `notebooks/final_accept_part6_panel25_brca1_failure_L4.ipynb` - BRCA1 failure and boundary structure

These are public scientific audit surfaces. They are not the cold-start default CLI contract.

## Command Truth

### Preferred Public Surface

```bash
uv sync --frozen
uv run spectralbio canonical
```

### Optional Full-Validation Surface

```bash
uv run spectralbio transfer
uv run spectralbio verify
uv run python scripts/preflight.py
```

### Underlying CLI Truth

- `spectralbio canonical`
- `spectralbio transfer`
- `spectralbio verify`

### Demoted Surfaces

- `make` is convenience only
- `python -m spectralbio.cli ...` is compatibility or historical only
- wrapper scripts under `scripts/` are auxiliary only

Do **not** promote demoted surfaces above the `uv` path in public execution.

## Adaptation Architecture

### Frozen Invariants

The validated default path remains the `TP53 canonical executable benchmark`. Its strict artifact-contract style, strict output-schema discipline, strict verification tolerance (`0.0001`), and primary score formula (`0.55*frob_dist + 0.45*ll_proper`) are part of the frozen TP53 reproducibility contract. The BRCA2 flagship scientific result is currently audited through notebooks and paper-aligned public surfaces rather than through the default CLI replay path.

### Adaptation Interface

A new target such as `{GENE}` would require its own bounded benchmark inputs and provenance: a target-specific variant dataset, a target-specific sequence reference, a target-specific score reference, a target-specific config and manifest trail, and target-specific expected metrics backed by independent validation evidence. None of these are created automatically by the current TP53-plus-BRCA1 repository contract.

### Adaptation Recipe

For a new target, first curate a target-specific benchmark with explicit labels and provenance. Then generate target-specific score references with a separate validated workflow, define the target-specific config and expected metrics, and add independent validation evidence for that target. Only after that target has its own separately implemented and independently validated contract should this repository be extended to materialize outputs for it, and any resulting evidence must be reported separately from the TP53 canonical claim set.

### Limitation Statement

`TP53` canonically validates the public replay surface. `BRCA2` is the manuscript's flagship stronger-baseline result but is not yet a frozen default CLI replay surface. `BRCA1_transfer100` remains bounded auxiliary transfer evidence only. Any new target requires separate implementation and separate validation, and no broad generalization claim is made.

## Failure Modes

Stop and report failure if any of the following occur:

- Step 4 loop reports `MISSING or EMPTY:` for any required file
- Step 5 metric check prints `FAIL:` or exits non-zero
- `metrics.computed_auc_best_pair` is absent from `outputs/canonical/summary.json`
- TP53 is no longer the primary benchmark or default executable path
- BRCA1 is presented as a co-primary benchmark or default path
- BRCA2 is described as already being the default frozen CLI benchmark without separate implementation
- the transfer path is treated as unrestricted generalization rather than a fixed bounded subset
- manuscript-facing text erases BRCA2 as the flagship scientific result or collapses TP53 and BRCA2 into an ambiguous dual-center story
- `uv run spectralbio verify` fails after optional full validation
- `uv run python scripts/preflight.py` fails after optional full validation
- repository wording drifts into forbidden claims
- a legacy or compatibility surface is presented as the canonical public contract

## Optional Revalidation Note

Fresh GPU or Colab reruns are outside the current canonical public path. If you pursue them, treat them as separate revalidation work rather than part of the frozen judge-facing execution surface.

## Auxiliary Repository Capabilities

The repository may also expose auxiliary export or release surfaces such as:

- `uv run spectralbio export-hf-space`
- `uv run spectralbio export-hf-dataset`
- `uv run spectralbio release`

These are auxiliary repository capabilities, not part of the canonical TP53 replay contract and not required for reproducing the public benchmark path above.

## Minimal Copy-Paste Path

Use this when you want the shortest correct public path on a fresh machine after cloning the repository and ensuring `uv` is available.

```bash
uv sync --frozen
uv run spectralbio canonical
```
