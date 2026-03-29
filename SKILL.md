---
name: spectralbio-tp53-canonical-benchmark
description: Cold-start bootstrap the public SpectralBio repository, reproduce the TP53 canonical executable benchmark, optionally run the bounded transfer on a fixed BRCA1 subset (N=100) without retraining, and verify the frozen repository artifact contract from a Bash-compatible terminal.
allowed-tools: Bash(git *), Bash(python *), Bash(uv *), Bash(ls *), Bash(test *)
package_manager: uv
repo_url: https://github.com/DaviBonetto/SpectralBio
repo_root: .
canonical_output_dir: outputs/canonical
secondary_output_dir: outputs/transfer
python_version: ">=3.10"
estimated_runtime_cpu_min: 25
estimated_runtime_gpu_min: 4
---

# SpectralBio TP53 Canonical Benchmark

## Mission

Use this skill to reproduce the public SpectralBio repository through its single canonical benchmark path and its clearly secondary optional validation path.

- Primary benchmark: `TP53 canonical executable benchmark`
- Secondary evidence: `bounded transfer on a fixed BRCA1 subset (N=100) without retraining`
- Transfer framing: `secondary transfer evaluation without retraining`
- Repository framing: `research reproducibility artifact`
- Anything beyond TP53 plus the fixed BRCA1 subset: `adaptation recipe only`

## Runtime Envelope

- Shell: `Bash-compatible shell`
- Python: `≥ 3.10` required (tested on 3.11)
- RAM: `≥ 4 GB` (ESM2-150M uses ~1.5 GB peak during CPU inference)
- Disk: `~800 MB` total (model cache ~600 MB + repository + outputs ~10 MB)
- Internet: required for repository clone, `uv sync --frozen`, and first-run ESM2-150M model download (~600 MB from HuggingFace)
- Estimated runtime: `~25 min on CPU` | `~4 min on GPU` (canonical TP53 path, N=255 variants)
- GPU: **not** required for the canonical public contract
- Model cache: HuggingFace stores downloaded models in `~/.cache/huggingface/` by default
- Run from the repository root
- If the repository is already cloned and you are already at its root, skip Step 0

## Scope And Non-Claims

### Scope

- TP53 is the only canonical scored benchmark and the default executable path
- BRCA1 is fixed-subset secondary evidence only
- The public execution surface is `uv`
- The true CLI namespace is `spectralbio`

### Non-Claims

- No `any protein` claim
- No `works on any protein` claim
- No strong, exceptional, or broad cross-protein generalization claim
- No BRCA1 co-primary benchmark framing
- No benchmark claim beyond TP53 plus the fixed BRCA1 subset
- No clinical deployment or clinical use framing

## Truth Boundary

If you need to inspect repository truth rather than guess, anchor to these files:

- `docs/truth_contract.md`
- `docs/reproducibility.md`
- `artifacts/expected/expected_metrics.json`
- `artifacts/expected/expected_files.json`
- `artifacts/expected/output_schema.json`
- `artifacts/expected/verification_rules.json`
- `outputs/canonical/summary.json` — field: `metrics.computed_auc_best_pair`
- `outputs/canonical/verification.json`

Do **not** promote legacy wording, wrapper convenience, or stale surfaces above these truth anchors.

## Step 0 — Clone The Public Repository

Run this only if the repository is not already present locally.

```bash
git clone https://github.com/DaviBonetto/SpectralBio.git
cd SpectralBio
ls pyproject.toml docs/truth_contract.md
```

The `ls` command confirms you are at the correct repository root. If either file is missing, you are in the wrong directory.

## Step 1 — Ensure `uv` Is Available

Check whether `uv` is already available:

```bash
uv --version
```

If that command fails, install `uv` with Python and check again:

```bash
python -m pip install --upgrade uv
export PATH="$HOME/.local/bin:$PATH"
uv --version
```

`uv` is typically installed to `~/.local/bin/`. The `export PATH` line ensures it is reachable in the current shell session without opening a new terminal.

## Step 2 — Sync The Locked Environment

```bash
uv sync --frozen
```

This installs the locked dependency set from `uv.lock` at the repository root. The `--frozen` flag prevents any dependency resolution or version drift. Both `pyproject.toml` and `uv.lock` must be present.

## Step 3 — Run The Canonical TP53 Benchmark

> **⚠ First-run model download:** On first execution `uv run spectralbio canonical` automatically downloads ESM2-150M (~600 MB) from HuggingFace. This requires internet access and takes ~2 min on a 50 Mbps connection. The model is cached at `~/.cache/huggingface/` for all subsequent runs. If the download fails with a HuggingFace error, verify internet access and retry once before investigating further.

```bash
uv run spectralbio canonical
```

This is the canonical public execution path. It loads the variant benchmark from `benchmarks/tp53/tp53_canonical_v1.json`, runs ESM2-150M inference, computes spectral and likelihood features, and writes the full artifact bundle to `outputs/canonical/`. Expected wall-clock time: ~25 min on CPU, ~4 min on GPU.

## Step 4 — Confirm The Canonical Artifact Bundle

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

## Step 5 — Validate Canonical Metrics

Confirm that `outputs/canonical/summary.json` reports the expected AUC within the declared tolerance. The computed AUC lives at `metrics.computed_auc_best_pair` inside the JSON object:

```bash
python -c "
import json, sys
with open('outputs/canonical/summary.json') as f:
    s = json.load(f)
try:
    auc = s['metrics']['computed_auc_best_pair']
except KeyError:
    sys.exit('FAIL: metrics.computed_auc_best_pair not found in outputs/canonical/summary.json — check field names')
official = s['metrics'].get('official_auc_best_pair', 0.7498)
delta = abs(auc - official)
if delta > 0.0001:
    sys.exit(f'FAIL: computed AUC {auc:.6f} deviates from official {official:.4f} by {delta:.6f} (tolerance 0.0001)')
print(f'OK: computed_auc_best_pair={auc:.6f} | official={official:.4f} | delta={delta:.6f} | tolerance=0.0001')
"
```

A passing run prints `OK: computed_auc_best_pair=0.749751...` and exits 0. This is the machine-checkable form of the Verification Contract. If this check fails, do not hand-edit outputs — rerun Step 3 or inspect `outputs/canonical/verification.json`.

## What Creates And Checks The Files

- `uv run spectralbio canonical`
  - loads variants from `benchmarks/tp53/tp53_canonical_v1.json`
  - runs ESM2-150M inference under `configs/tp53_canonical.yaml`
  - writes the full TP53 artifact bundle to `outputs/canonical/`
- `uv run spectralbio transfer`
  - creates the bounded BRCA1 secondary artifact bundle in `outputs/transfer/`
- `uv run spectralbio verify`
  - validates canonical and transfer outputs against the frozen repository contract
  - on success: exits 0 and writes `"status": "passed"` to `outputs/canonical/verification.json`
  - on failure: exits non-zero and writes `"status": "failed"` with a list of failed checks
- `uv run python scripts/preflight.py`
  - rechecks output status plus wording and contract-sensitive repository assertions

Do **not** hand-edit outputs to force success. Use repository commands only.

## Canonical Success Criteria

The canonical path is successful only if **all** of the following are true:

- `uv sync --frozen` exits with code 0
- `uv run spectralbio canonical` exits with code 0
- Step 4 loop reports `OK:` for all eight required files
- Step 5 metric check prints `OK:` and exits 0 (`computed_auc_best_pair` within 0.0001 of `official_auc_best_pair`)
- TP53 remains the primary and default executable benchmark path
- no step above required BRCA1 transfer, `verify`, `preflight`, GPU, or paper build to count canonical TP53 success

## Optional Full Validation

Run this only when you need the bounded secondary BRCA1 evidence and the full repository validation pass **after** the canonical TP53 run.

```bash
uv run spectralbio transfer
uv run spectralbio verify
uv run python scripts/preflight.py
```

This optional validation path keeps BRCA1 secondary and bounded. It is **not** the default path and **not** required for canonical TP53 success.

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

Repository-aligned verification keeps these exact values and tolerance:

- TP53 canonical score formula: `0.55*frob_dist + 0.45*ll_proper`
- TP53 official AUC: `0.7498`
- TP53 computed AUC (`metrics.computed_auc_best_pair`): `0.749751...` (delta = 0.0 when rounded to 4 decimal places)
- BRCA1 bounded transfer AUC: `0.9174`
- reproducibility delta: `0.0`
- verification tolerance: `0.0001`

Report drift if filenames change, metrics move outside tolerance, TP53 stops being primary, or BRCA1 stops being bounded secondary evidence.

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

## Adaptation Recipe (Generalizability)

Adapting beyond the canonical TP53 and fixed BRCA1 subset is possible but is **not** covered by the reproducibility contract of this skill.

The repository uses config-driven execution. The canonical TP53 run loads `configs/tp53_canonical.yaml`. To target a different gene, provide a config file following the same schema:

```bash
# Adapt to a new gene using a config file (bounded adaptation):
uv run spectralbio canonical --config configs/your_target.yaml
```

Constraints on generalization:

- ESM2-150M supports sequences up to 1024 amino acids (hard context window limit)
- No retraining is performed — this is zero-shot inference only
- AUC outside the TP53 canonical benchmark and BRCA1 fixed-subset is not guaranteed and not claimed
- Any adapted run should produce its own `verification.json` — do not compare to canonical metrics

Treat any result outside the canonical TP53 path as an adaptation recipe result only.

## Failure Modes

Stop and report failure if any of the following occur:

- Step 4 loop reports `MISSING or EMPTY:` for any required file
- Step 5 metric check prints `FAIL:` or exits non-zero
- `metrics.computed_auc_best_pair` is absent from `outputs/canonical/summary.json`
- TP53 is no longer the primary benchmark or default executable path
- BRCA1 is presented as a co-primary benchmark or default path
- the transfer path is treated as unrestricted generalization rather than a fixed bounded subset
- `uv run spectralbio verify` fails after optional full validation
- `uv run python scripts/preflight.py` fails after optional full validation
- repository wording drifts into forbidden claims
- a legacy or compatibility surface is presented as the canonical public contract
- ESM2-150M model download fails — verify internet access and retry once

## Optional GPU Note

GPU or Colab reruns are optional revalidation only. They are not required for the public canonical contract defined in this skill. If GPU is available, the canonical run completes in ~4 min instead of ~25 min; all outputs and metrics are identical.

## Auxiliary Repository Capabilities

The repository may also expose auxiliary export or release surfaces such as:

- `uv run spectralbio export-hf-space`
- `uv run spectralbio export-hf-dataset`
- `uv run spectralbio release`

These are auxiliary repository capabilities, not part of the canonical TP53 benchmark contract and not required for reproducing the public benchmark path above.

## Minimal Copy-Paste Path

Use this when you want the shortest correct public path on a fresh machine after cloning the repository and ensuring `uv` is available. Expected runtime: ~25 min on CPU.

```bash
uv sync --frozen
uv run spectralbio canonical
```
