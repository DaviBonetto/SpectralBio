---
name: spectralbio-canonical-replay-and-portability-audit
description: Execute the frozen TP53 canonical replay, verify machine-checkable outputs, and inspect replay-ready portability surfaces across TP53, BRCA2, TSC2, and CREBBP, with BRCA1 and MSH2 preserved as negative guardrails. Reproduces the package's executable validation anchor and its final claim boundary: strengthened target-level portability with mixed model-level holdout/control closure.
allowed-tools: Bash(git *), Bash(python *), Bash(uv *), Bash(ls *), Bash(test *)
package_manager: uv
repo_url: https://github.com/DaviBonetto/SpectralBio
repo_root: .
canonical_output_dir: outputs/canonical
secondary_output_dir: outputs/transfer
python_version: ">=3.10"
---

# SpectralBio: Structural Stethoscope for Protein Language Models

## Mission

Reproduce the SpectralBio repository through its frozen executable replay surface and inspect the public scientific audit surfaces that define the manuscript's final state. This is not a generic protein-model benchmark. It is a **targeted representational diagnosis** showing that ESM2 can miss structural strain that covariance detects.

- **Canonical executable anchor**: `TP53` remains the only frozen default replay surface, challengeable and machine-verifiable in seconds.
- **Flagship scientific result**: on `BRCA2`, covariance-aware geometry improves a five-model ESM-1v ensemble from `0.6324` to `0.6890` (paired gain `0.0566`, 95% CI `[0.0131, 0.1063]`, empirical permutation `p = 0.0010`).
- **Qualitative centerpiece**: a performance-blind scale-repair failure mode inside ESM2, where 150M overstates covariance disruption for a narrow chemistry-defined regime and 650M repairs it (`p = 0.000244`).
- **Replay-ready portability layer**: the manuscript now supports replay-ready multi-target portability across `TP53`, `BRCA2`, `TSC2`, and `CREBBP`, with `TSC2` and `CREBBP` as transfer-positive targets.
- **Negative guardrails**: `BRCA1` and `MSH2` remain explicit boundary surfaces and must not be erased.
- **Final closure boundary**: the final holdout/control tribunal remains mixed. The package supports strengthened portability, not universal or fully closed generalization.

## Judge Quickstart

### Must run

```bash
uv sync --frozen
uv run spectralbio canonical
```

### Expected success

- `outputs/canonical/` is materialized with the full frozen TP53 artifact bundle
- `outputs/canonical/summary.json` reports `metrics.computed_auc_best_pair` within tolerance of `0.7498`
- `outputs/canonical/verification.json` reports `PASS`

### What success proves

- the **canonical executable replay surface** is intact
- `TP53` remains the public validation anchor
- the repository's frozen output contract is reproducible and machine-verifiable

### What success does not prove

- it does **not** rerun the BRCA2 flagship analysis
- it does **not** establish universal transfer
- it does **not** close the final harsh holdout/control tribunal
- it does **not** make `BRCA2`, `TSC2`, or `CREBBP` default CLI replay targets

## Execution Envelope

- Shell: Bash-compatible
- Python: `>= 3.10` (tested on 3.11)
- Internet: Required for repository clone and `uv sync --frozen`
- GPU: **Not required** for the canonical executable replay path
- Execution model: frozen-artifact reproducibility, verification, and scientific audit inspection
- Run from repository root
- If already cloned and at root, skip Step 0

## What This Package Proves

| Surface | Status | Role | Supports | Does Not Support |
|---|---|---|---|---|
| `TP53` | canonical executable replay surface | Default public validation anchor | Frozen replay, structural smoking gun, machine-verifiable contract | Universal portability, full closure |
| `BRCA2` | replay-ready portability surface + flagship scientific audit surface | Stronger-baseline centerpiece and next canonicalization target | Flagship quantitative gain, benchmark-qualified scientific center | Default CLI replay path unless repo changes |
| `TSC2` | replay-ready portability surface | Transfer-positive target-level portability witness | Public portability beyond TP53/BRCA2 | Full model-level closure |
| `CREBBP` | replay-ready portability surface | Transfer-positive target-level portability witness | Public portability beyond TP53/BRCA2 | Full model-level closure |
| `BRCA1` | auxiliary bounded executable surface + negative guardrail surface | Fixed-subset executable continuity check and explicit anti-case | Bounded BRCA1 transfer without retraining; preserved failure surface | Co-primary benchmark or broad generalization proof |
| `MSH2` | negative guardrail surface | Decisive negative replication | Boundary condition against overclaim | Positive transfer headline |

## Scientific And Executable Contract

### Surface Taxonomy

- **Canonical executable replay surface**: default public cold-start execution contract
- **Auxiliary bounded executable surface**: executable but explicitly secondary and bounded
- **Scientific audit surface**: manuscript-facing, notebook-backed evidence
- **Replay-ready portability surface**: target-level portability surface with public replay-ready evidence
- **Negative guardrail surface**: explicit retained negative or boundary surface
- **Earlier harsh-firewall chain**: the pre-Block-13 late-stage adjudication chain
- **Final holdout/control closure boundary**: the harshest model-level closure tribunal

### Current repository truth

| Layer | Current truth |
|---|---|
| Canonical executable replay surface | `TP53` only |
| Auxiliary bounded executable surface | `BRCA1_transfer100` only |
| Flagship scientific audit surface | `BRCA2` stronger-baseline result |
| Replay-ready portability surfaces | `TP53`, `BRCA2`, `TSC2`, `CREBBP` |
| Transfer-positive targets | `TSC2`, `CREBBP` |
| Negative guardrails | `BRCA1`, `MSH2` |
| Earlier harsh-firewall chain | supportive rather than nuclear |
| Final holdout/control closure boundary | mixed; no model-level holdout/control closure |

### Important distinction

The package now contains a stronger public story than the older `TP53 canonical + BRCA1 bounded support` world. But the strengthening occurs at the **target-level replay-ready portability layer**, not at the **model-level harsh closure layer**. Block 13 raises the portability ceiling. Block 14 prevents universalization.

## Why This Skill Is Different

Most reproducibility artifacts ask you to recompute from scratch, download models, rerun inference, and wait hours. This repository inverts that: the canonical path is a **frozen verification contract**. You are not reproducing a long computation first; you are verifying that the published claim matches the published frozen evidence.

The canonical TP53 path completes in **seconds**, not hours, because it validates frozen score references rather than recomputing live embeddings. That design is deliberate. The evidence should be inspectable faster than it was produced.

## Runtime Expectations

- Canonical path: `uv sync --frozen` then `uv run spectralbio canonical`
- Typical runtime after sync: **< 5 seconds** CPU-only frozen artifact materialization
- Canonical path validates frozen TP53 config, loads bundled variants and score references, computes contract metrics, writes artifact bundle, and writes verification output
- Canonical path does **not** perform live HuggingFace/ESM2 downloads or notebook recomputation
- `BRCA2`, `TSC2`, and `CREBBP` matter in the scientific audit and replay-ready portability layers, not yet as the default CLI replay path

## Scope And Non-Claims

### Scope

- `TP53` is the default executable replay center
- `BRCA2` is the flagship stronger-baseline scientific result
- `BRCA1_transfer100` is bounded auxiliary executable evidence only
- `TSC2` and `CREBBP` are replay-ready transfer-positive targets in the scientific package
- `BRCA1` and `MSH2` are explicit negative guardrails
- Public execution surface: `uv`
- CLI namespace: `spectralbio`

### Must not claim

- no universal generalization
- no full closure
- no broad cross-protein law
- no model-family-wide closure
- no holdout-positive closure
- no control-win closure
- no generic works-on-any-protein portability
- no universal alpha transfer
- no clinical deployment or clinical use
- no claim that every replay-ready target is already a default CLI benchmark
- no claim that `BRCA2`, `TSC2`, or `CREBBP` already run through the same default public CLI path as `TP53`
- no collapse of target-level portability into model-level closure

These non-claims are part of the result, not qualifications pasted on afterward.

## Truth Boundary

If you need repository truth rather than guesswork, anchor to these files first:

- `docs/truth_contract.md`
- `docs/reproducibility.md`
- `artifacts/expected/expected_metrics.json`
- `artifacts/expected/expected_files.json`
- `artifacts/expected/output_schema.json`
- `artifacts/expected/verification_rules.json`
- `outputs/canonical/summary.json`
- `outputs/canonical/verification.json`

If you need executable corroborators, inspect these next:

- `benchmarks/manifests/tp53_canonical_manifest.json`
- `benchmarks/manifests/brca1_transfer_manifest.json`
- `benchmarks/manifests/source_snapshot.json`
- `benchmarks/manifests/checksums.json`

If you need manuscript-aligned scientific audit surfaces, inspect these next:

- `abstract.md`
- `content.md`
- `New Notebooks/01_block1_baseline_alpha_regime_audit_h100.ipynb`
- `New Notebooks/02_block2_failure_mode_hunt_h100.ipynb`
- `New Notebooks/05_block3_structure_bridge_h100.ipynb`
- `New Notebooks/06_block5_clinical_panel_audit_h100.ipynb`
- `New Notebooks/07c_block10_structural_dissociation_tp53_h100.ipynb`
- `New Notebooks/08_block7_turbo_gallery_rescues_h100.ipynb`
- `New Notebooks/11_block11_covariance_rulebook_h100.ipynb`
- `New Notebooks/12_block12_orthogonal_validation_tp53_h100.ipynb`
- `New Notebooks/12b_block12_multifamily_coverage_aware_generalization_h100.ipynb`
- `New Notebooks/12c_block12_covariance_adjudication_structural_closure_h100.ipynb`
- `New Notebooks/12d_block12_final_nuclear_localization_h100.ipynb`
- `New Notebooks/13_block13_multitarget_generalization_closure_h100.ipynb`
- `New Notebooks/14_block14_holdout_control_closure_h100.ipynb`

Treat legacy notebook-era surfaces and old `final_accept_*` material as support only when needed for provenance. Do not promote them above the current manuscript chain.

## Must Run / May Inspect / Must Not Claim / Out Of Scope

### Must run

- `uv sync --frozen`
- `uv run spectralbio canonical`

### May inspect

- `uv run spectralbio transfer`
- `uv run spectralbio verify`
- `uv run python scripts/preflight.py`
- current manuscript notebook surfaces under `New Notebooks/`
- `abstract.md`, `content.md`, and the truth / reproducibility contract files

### Must not claim

- anything beyond the claim boundary listed above
- that replay-ready targets are already machine-verified default CLI benchmarks unless the repo changes
- that the final harsh closure tribunal closed positively

### Out of scope

- adapting to a genuinely new target without a separate contract
- live heavy recomputation as the default public path
- broad portability claims beyond the documented replay-ready and guardrail surfaces

## When To Use This Skill

### Case 1 - Canonical replay (default)

- Goal: reproduce the frozen TP53 public replay surface
- Path: canonical path from repository root
- Result: frozen-artifact reproducibility under `outputs/canonical/`
- Priority: fastest route, completes in seconds

### Case 2 - Public scientific audit

- Goal: inspect the manuscript-aligned scientific center without changing the executable contract
- Path: inspect `abstract.md`, `content.md`, and the current `New Notebooks` audit chain
- Result: BRCA2 flagship, TP53 structural anchor, breadth, scale-repair, replay-ready portability, and final mixed closure become explicit
- Constraint: scientific audit surfaces complement TP53 replay; they do not replace it

### Case 3 - Optional bounded auxiliary validation

- Goal: check `BRCA1_transfer100` as bounded auxiliary executable evidence
- Order: use only after canonical TP53 understanding or execution
- Path: run optional transfer / verify / preflight path when bounded secondary validation is required
- Constraint: bounded secondary evidence only, without retraining

### Case 4 - Out of scope

- stop if the task is adapting to a genuinely new target
- stop if the task requires live heavy recomputation as the default product path
- stop if the task asks for universal or fully closed generalization
- next step: use the `Adaptation Architecture` section and require separate evidence

## Step 0 - Clone The Public Repository

Run only if the repository is not already present locally.

```bash
git clone https://github.com/DaviBonetto/SpectralBio.git
cd SpectralBio
ls pyproject.toml docs/truth_contract.md
```

The `ls` confirms that you are at the correct repository root.

## Step 1 - Ensure `uv` Is Available

```bash
uv --version
```

If that fails:

```bash
python -m pip install --upgrade uv
uv --version
```

If `uv` is still not found, restart the shell once. Do not rewrite the public command surface because of a local shell-path issue.

## Step 2 - Sync The Locked Environment

```bash
uv sync --frozen
```

This installs the locked dependency set from `uv.lock` without allowing version drift.

## Step 3 - Run The Canonical TP53 Replay Surface

```bash
uv run spectralbio canonical
```

This is the canonical public execution path. It validates the frozen TP53 config, loads `benchmarks/tp53/tp53_canonical_v1.json` plus the bundled score reference `benchmarks/tp53/tp53_scores_v1.json`, computes contract metrics from those frozen score rows, copies the frozen TP53 ROC figure, and writes the canonical artifact bundle plus `verification.json` to `outputs/canonical/`.

This path is a frozen-artifact materialization path for reproducibility and judge-safe execution. It does **not** rerun the BRCA2 flagship analysis or any portability notebook.

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

Confirm all files exist and are non-empty:

```bash
for f in run_metadata.json inputs_manifest.json tp53_scores.tsv tp53_metrics.json summary.json roc_tp53.png manifest.json verification.json; do
  test -s "outputs/canonical/$f" && echo "OK: $f" || echo "MISSING or EMPTY: $f"
done
ls outputs/canonical
```

All eight lines must read `OK:`.

## Step 5 - Validate Canonical Metrics

```bash
python -c "
import json, sys
with open('outputs/canonical/summary.json') as f:
    s = json.load(f)
try:
    auc = s['metrics']['computed_auc_best_pair']
except KeyError:
    sys.exit('FAIL: metrics.computed_auc_best_pair not found in outputs/canonical/summary.json')
official = s['metrics'].get('official_auc_best_pair', 0.7498)
delta = abs(auc - official)
if delta > 0.0001:
    sys.exit(f'FAIL: computed AUC {auc:.6f} deviates from official {official:.4f} by {delta:.6f} (tolerance 0.0001)')
print(f'OK: computed_auc_best_pair={auc:.6f} | official={official:.4f} | delta={delta:.6f} | tolerance=0.0001')
"
```

This is the machine-checkable form of the canonical replay contract.

## What Creates And Checks The Files

| Command | What it does |
|---|---|
| `uv run spectralbio canonical` | Validates config, loads frozen TP53 inputs, computes contract metrics, copies frozen figure, writes `outputs/canonical/` |
| `uv run spectralbio transfer` | Writes bounded BRCA1 auxiliary artifact bundle to `outputs/transfer/` from frozen fixed first-100 subset |
| `uv run spectralbio verify` | Verifies canonical and transfer outputs against the frozen repository contract |
| `uv run python scripts/preflight.py` | Reruns public surfaces, stages export surfaces, and checks output plus wording-sensitive repository assertions |

Do **not** hand-edit outputs to force success.

## Canonical Success Criteria

Canonical success requires all of the following:

- `uv sync --frozen` exits 0
- `uv run spectralbio canonical` exits 0
- all eight canonical files are present and non-empty
- `metrics.computed_auc_best_pair` is within `0.0001` of `0.7498`
- `outputs/canonical/verification.json` reports `PASS`
- TP53 remains the default executable replay path

Canonical success establishes the frozen TP53 executable contract. It does **not** by itself establish:

- BRCA2 notebook recomputation
- TSC2/CREBBP executable replay parity with TP53
- universal transfer
- full holdout/control closure

## Optional Full Validation

Run this only when you need the bounded auxiliary BRCA1 evidence and the full repository validation pass after the canonical TP53 run.

```bash
uv run spectralbio transfer
uv run spectralbio verify
uv run python scripts/preflight.py
```

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

This remains a bounded auxiliary executable path. It is not the flagship scientific result and not the default public benchmark path.

## Verification Contract

### Machine-Verified Replay Contract

- TP53 canonical score formula: `0.55*frob_dist + 0.45*ll_proper`
- TP53 official AUC: `0.7498`
- TP53 reproducibility delta: `0.0`
- BRCA1 bounded transfer AUC: `0.9174`
- verification tolerance: `0.0001`

### Scientific Audit Contract

- BRCA2 flagship augmentation: ESM-1v `0.6324` -> covariance + ESM-1v `0.6890`
- BRCA2 paired gain: `0.0566`, 95% CI `[0.0131, 0.1063]`, permutation `p = 0.0010`
- TP53 structural dissociation: covariance `0.309` vs likelihood `0.036`
- Scale-repair matched-pair mean Frobenius gap reduction: `0.7250`, exact sign-flip `p = 0.000244`
- Scale-repair sister-substitution sign-flip `p = 0.007812`
- Clinical-panel breadth: `4 of 4` positive-focus genes improve, `12` rescue candidates
- Earlier harsh-firewall chain: supportive rather than nuclear
- Replay-ready portability layer: `TP53`, `BRCA2`, `TSC2`, `CREBBP`
- Transfer-positive targets: `TSC2`, `CREBBP`
- Negative guardrails: `BRCA1`, `MSH2`
- Final holdout/control tribunal: mixed; no harsh model-level closure

### Final claim boundary

This package now supports:

- a canonical executable TP53 replay contract
- bounded BRCA1 auxiliary executable continuity
- replay-ready multi-target portability at the scientific audit layer

It does **not** support:

- universal generalization
- full closure
- holdout-positive closure
- control-win closure
- model-family-wide closure

## Public Scientific Audit Surfaces

### Current manuscript chain (preferred)

- `New Notebooks/01_block1_baseline_alpha_regime_audit_h100.ipynb` - BRCA2 flagship, TP53 validation, MSH2 negative replication
- `New Notebooks/02_block2_failure_mode_hunt_h100.ipynb` - scale-repair failure mode discovery
- `New Notebooks/05_block3_structure_bridge_h100.ipynb` - bounded structural bridge
- `New Notebooks/06_block5_clinical_panel_audit_h100.ipynb` - performance-blind breadth and rescue prioritization
- `New Notebooks/07c_block10_structural_dissociation_tp53_h100.ipynb` - final TP53 structural readout
- `New Notebooks/08_block7_turbo_gallery_rescues_h100.ipynb` - rescue gallery plus explicit anti-case

### Earlier harsh-firewall chain

- `New Notebooks/11_block11_covariance_rulebook_h100.ipynb`
- `New Notebooks/12_block12_orthogonal_validation_tp53_h100.ipynb`
- `New Notebooks/12b_block12_multifamily_coverage_aware_generalization_h100.ipynb`
- `New Notebooks/12c_block12_covariance_adjudication_structural_closure_h100.ipynb`
- `New Notebooks/12d_block12_final_nuclear_localization_h100.ipynb`

### Late-stage portability evidence

- `New Notebooks/13_block13_multitarget_generalization_closure_h100.ipynb`

### Final holdout/control tribunal

- `New Notebooks/14_block14_holdout_control_closure_h100.ipynb`

### Legacy manuscript surfaces (support only)

- `notebooks/final_accept_part1_support_panel.ipynb`
- `notebooks/final_accept_part3_esm1v_augmentation_A100.ipynb`
- `notebooks/final_accept_part4_brca2_canonicalization_A100.ipynb`
- `notebooks/final_accept_part5_protocol_sweep_A100.ipynb`
- `notebooks/final_accept_part6_panel25_brca1_failure_L4.ipynb`

When current manuscript surfaces and legacy surfaces diverge, prefer the current manuscript chain.

## Command Truth

### Preferred public surface

```bash
uv sync --frozen
uv run spectralbio canonical
```

### Optional full-validation surface

```bash
uv run spectralbio transfer
uv run spectralbio verify
uv run python scripts/preflight.py
```

### Underlying CLI truth

- `spectralbio canonical`
- `spectralbio transfer`
- `spectralbio verify`

### Demoted surfaces

- `make` is convenience only
- `python -m spectralbio.cli ...` is compatibility or historical only
- wrapper scripts under `scripts/` are auxiliary only

## Adaptation Architecture

### Frozen invariants

The validated default path remains the TP53 canonical executable benchmark. Its strict output schema, verification tolerance (`0.0001`), and score formula (`0.55*frob_dist + 0.45*ll_proper`) are part of the frozen replay contract.

### Current portability state

The repository now contains a stronger scientific package than TP53 alone. `BRCA2`, `TSC2`, and `CREBBP` matter as replay-ready portability surfaces, and `TSC2` plus `CREBBP` matter as transfer-positive targets. But that is still different from saying that these targets are already default CLI replay benchmarks.

### Adaptation rule

Any truly new target still requires:

- target-specific benchmark inputs
- target-specific provenance
- target-specific score references
- target-specific expected metrics
- target-specific validation evidence

Only after that separate contract exists should a new target be promoted into the executable replay layer.

### Limitation statement

TP53 remains the only default executable replay benchmark. BRCA2 remains the flagship stronger-baseline scientific result. `TSC2` and `CREBBP` now matter as replay-ready transfer surfaces. `BRCA1_transfer100` remains bounded auxiliary executable evidence. Any truly new target still requires separate implementation and separate validation.

## Failure Modes

Stop and report failure if any of the following occur:

- any canonical required file is missing or empty
- canonical metric verification fails
- TP53 stops being the default executable replay path without corresponding repo truth
- BRCA1 bounded transfer is promoted into co-primary benchmark language
- BRCA2/TSC2/CREBBP are described as default executable CLI replay paths without actual support
- `TSC2` and `CREBBP` disappear from the portability layer
- `BRCA1` or `MSH2` disappear as explicit guardrails
- the earlier harsh-firewall chain disappears from the package
- Block 13 portability strengthening is omitted
- Block 14 mixed closure is omitted
- the package reverts to an outdated `TP53 only + bounded support` framing
- the package claims universal or fully closed generalization
- a demoted surface is presented as canonical public command truth

## Minimal Copy-Paste Path

```bash
uv sync --frozen
uv run spectralbio canonical
```

That is the shortest correct public path to the canonical executable replay surface.
