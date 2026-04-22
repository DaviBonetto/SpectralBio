# Reproducibility

## Environment

- Python package root: `src/`
- CLI entrypoint: `spectralbio`
- Seed: `42`
- Canonical model metadata: `facebook/esm2_t30_150M_UR50D` is recorded in `outputs/canonical/run_metadata.json` as provenance for the frozen contract

## Reproducibility Definition

SpectralBio has more than one reproducibility layer. The package is only interpreted correctly when these layers are kept distinct.

### 1. Canonical executable replay reproducibility

- Surface: `TP53`
- Meaning: the public cold-start CLI path reproduces the frozen TP53 replay contract
- Verification mode: machine-verified
- Default public commands:
  - `uv sync --frozen`
  - `uv run spectralbio canonical`

### 2. Auxiliary bounded executable reproducibility

- Surface: `BRCA1_transfer100`
- Meaning: the bounded BRCA1 auxiliary transfer surface materializes correctly without retraining
- Verification mode: machine-verified
- Optional commands:
  - `uv run spectralbio transfer`
  - `uv run spectralbio verify`

### 3. Replay-ready portability reproducibility

- Surfaces:
  - `TP53`
  - `BRCA2`
  - `TSC2`
  - `CREBBP`
- Meaning: these targets exist as public replay-ready scientific portability surfaces
- Verification mode: scientific audit consistency, not default CLI replay parity

### 4. Scientific audit reproducibility

- Meaning: the manuscript-facing notebook chain, metrics, and boundary logic remain internally consistent with the frozen package
- Verification mode: document and notebook inspection

### 5. Final closure boundary reproducibility

- Meaning: the package truth must preserve that the final harsh holdout/control tribunal remains mixed
- Verification mode: claim-boundary consistency

## Reproducibility Contract

### Canonical executable replay center

- `TP53` is the only canonical executable replay surface
- It is the default public executable validation anchor
- Canonical success proves the frozen replay contract, not universal portability

### Auxiliary bounded executable center

- `BRCA1_transfer100` is the only auxiliary bounded executable surface
- It remains fixed-subset, bounded, and without retraining
- It is secondary to TP53 and must stay secondary

### Scientific center

- `BRCA2` is the flagship stronger-baseline scientific result
- Scale-repair is the qualitative centerpiece
- `TP53` is also the structural anchor

### Replay-ready portability center

- Replay-ready targets:
  - `TP53`
  - `BRCA2`
  - `TSC2`
  - `CREBBP`
- Transfer-positive targets:
  - `TSC2`
  - `CREBBP`
- Negative guardrails:
  - `BRCA1`
  - `MSH2`

### Final closure boundary

- The final harsh holdout/control tribunal remains mixed
- No model-level holdout-positive closure
- No model-level control-win closure
- No harsh model-level transfer-positive closure

## Official Metrics

### Manuscript Scientific Audit Metrics

- BRCA2 ESM-1v baseline AUC: `0.6324`
- BRCA2 covariance + ESM-1v AUC: `0.6890`
- BRCA2 paired gain vs ESM-1v: `0.0566`
- BRCA2 paired 95% bootstrap CI: `[0.0131, 0.1063]`
- BRCA2 empirical permutation `p`: `0.0010`
- TP53 structural dissociation: covariance `0.309` vs likelihood `0.036`
- Scale-repair matched-pair mean Frobenius gap reduction: `0.7250`
- Scale-repair matched-pair exact sign-flip `p`: `0.000244`

### Machine-Verified Executable Metrics

- TP53 canonical executable benchmark: `0.55*frob_dist + 0.45*ll_proper` AUC = `0.7498`
- Bounded transfer on a fixed BRCA1 subset (`N=100`): `ll_proper` AUC = `0.9174`
- Reproducibility delta: `0.0`

Metric verification uses the `0.0001` tolerance declared in `artifacts/expected/verification_rules.json`.

## Setup

If `uv` is not available yet:

```bash
python -m pip install uv
```

If `uv` is not available immediately after installation, restart the shell once and re-check it.

## Canonical Public Path

```bash
uv sync --frozen
uv run spectralbio canonical
```

The canonical path deliberately materializes frozen TP53 artifacts from bundled benchmark inputs and bundled score references. It writes the canonical contract files under `outputs/canonical/` for reproducibility, verification, and judge-safe execution. It does **not** depend on a live HuggingFace/ESM2 download in the canonical public path, and it does **not** recompute BRCA2, TSC2, or CREBBP portability analyses.

## What Canonical Success Means

Canonical TP53 success means:

- the default executable replay surface is intact
- the frozen TP53 contract still validates
- the package's primary cold-start benchmark remains challengeable and machine-verifiable

Canonical TP53 success does **not** mean:

- BRCA2 has become a default CLI replay surface
- `TSC2` and `CREBBP` are executable through the same default path
- full portability closure has been established
- the final harsh holdout/control tribunal has closed positively

## Portability-Layer Audit Path

Use this path when the goal is not only to rerun the canonical TP53 anchor, but to confirm that the package still exposes the strengthened portability layer without overclaim.

Audit targets:

- replay-ready portability surfaces:
  - `TP53`
  - `BRCA2`
  - `TSC2`
  - `CREBBP`
- transfer-positive targets:
  - `TSC2`
  - `CREBBP`
- negative guardrails:
  - `BRCA1`
  - `MSH2`

Audit surfaces:

- `SKILL.md`
- `docs/truth_contract.md`
- `content.md`
- `New Notebooks/13_block13_multitarget_generalization_closure_h100.ipynb`
- `New Notebooks/14_block14_holdout_control_closure_h100.ipynb`

Successful portability-layer audit means:

- the four replay-ready targets remain explicit
- `TSC2` and `CREBBP` remain explicit transfer-positive targets
- `BRCA1` and `MSH2` remain explicit guardrails
- the final harsh holdout/control tribunal still remains mixed

Successful portability-layer audit does **not** mean:

- these targets have default CLI replay parity with `TP53`
- the final tribunal has closed positively
- the package now supports universal or model-family-wide generalization

## Public Scientific Audit Surfaces

Use these surfaces when the task is manuscript review, scientific interpretation, portability inspection, or claim-boundary checking rather than cold-start CLI replay.

### Current manuscript chain

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

### What these surfaces establish

- BRCA2 flagship stronger-baseline result
- TP53 structural anchor
- scale-repair failure mode
- breadth and gallery logic
- earlier harsh-firewall chain
- replay-ready multi-target portability
- final mixed holdout/control closure boundary

These surfaces complement the TP53 replay path. They do not replace it as the default executable contract.

## Optional Full Validation

```bash
uv run spectralbio transfer
uv run spectralbio verify
uv run python scripts/preflight.py
```

`uv run spectralbio verify` writes the repository contract report to `outputs/canonical/verification.json` with top-level `PASS` / `FAIL` status and nested canonical / transfer checks.

The optional transfer path keeps BRCA1 bounded and auxiliary. It is not the manuscript flagship result and is not required for canonical TP53 replay success.

For local test execution:

```bash
uv sync --frozen --extra dev
uv run pytest
```

## Expected Outputs

### Canonical TP53 run

- `outputs/canonical/run_metadata.json`
- `outputs/canonical/inputs_manifest.json`
- `outputs/canonical/tp53_scores.tsv`
- `outputs/canonical/tp53_metrics.json`
- `outputs/canonical/summary.json`
- `outputs/canonical/roc_tp53.png`
- `outputs/canonical/manifest.json`
- `outputs/canonical/verification.json`

### Secondary bounded BRCA1 transfer run

- `outputs/transfer/summary.json`
- `outputs/transfer/variants.json`
- `outputs/transfer/manifest.json`

No other replay-ready portability target is currently promised as a machine-verified default CLI output surface unless the executable contract changes.

## Success Criteria

### TP53 canonical success

- canonical command exits 0
- all expected canonical files are present
- TP53 metric verification passes within tolerance
- verification status is `PASS`

### BRCA1 bounded auxiliary success

- transfer command exits 0
- all expected transfer files are present
- bounded transfer verification remains `PASS`

### Scientific audit consistency success

- BRCA2 remains the flagship stronger-baseline result
- TP53 remains the structural and executable anchor
- scale-repair remains present
- BRCA1 and MSH2 remain explicit guardrails

### Replay-ready portability consistency success

- `TP53`, `BRCA2`, `TSC2`, and `CREBBP` remain explicitly represented as replay-ready portability surfaces
- `TSC2` and `CREBBP` remain explicitly represented as transfer-positive targets

### Final closure boundary success

- the package still states that the final harsh holdout/control tribunal remains mixed
- no document upgrades that final state into universal or fully closed generalization

## Clean-Room Validation Matrix

| Validation step | Purpose | Commands or inspection | Expected outcome |
| --- | --- | --- | --- |
| Local canonical materialization | Prove the canonical path resolves on a clean uv-first machine | `uv run spectralbio canonical` | `outputs/canonical/*` present and valid |
| Local bounded auxiliary transfer | Confirm bounded BRCA1 transfer still materializes | `uv run spectralbio transfer` | `outputs/transfer/*` present and valid |
| Machine verification | Confirm canonical and transfer outputs obey the contract | `uv run spectralbio verify` | `PASS` |
| Public scientific consistency audit | Confirm BRCA2 / TP53 / portability / guardrail roles stay aligned | inspect `abstract.md`, `content.md`, `SKILL.md`, truth and reproducibility docs | roles remain coherent |
| Portability-surface consistency audit | Confirm replay-ready and transfer-positive target surfaces remain explicit | inspect current manuscript chain and Block 13 outputs | four replay-ready targets and two transfer-positive targets remain explicit |
| Final closure boundary audit | Confirm final tribunal remains bounded | inspect Block 14 outputs and package docs | final closure remains mixed |

## Troubleshooting / Failure Triage

### Canonical command fails

- first inspect `uv sync --frozen`
- then inspect `src/spectralbio/cli.py`
- then inspect `outputs/canonical/verification.json`

### Canonical outputs exist but metrics fail

- inspect `outputs/canonical/summary.json`
- inspect `artifacts/expected/expected_metrics.json`
- inspect `artifacts/expected/verification_rules.json`
- do not hand-edit outputs

### Transfer path fails

- treat it as auxiliary bounded-surface failure, not canonical TP53 failure
- inspect `benchmarks/manifests/brca1_transfer_manifest.json`
- inspect `outputs/transfer/`

### Scientific package seems contradictory

- resolve by checking `docs/truth_contract.md` first
- then `content.md`
- then current `New Notebooks` Block 13 and Block 14 surfaces

### A doc implies more generalization than the tribunal supports

- prefer the final bounded claim:
  - replay-ready multi-target portability strengthened
  - final harsh holdout/control closure still mixed

## Optional Revalidation Policy

Fresh GPU reruns are outside the current canonical public path.

They become justified only when one of the following changes:

- executable metrics are revalidated from fresh execution
- output schemas or expected file contracts change
- figures are regenerated from new scientific outputs
- portability surfaces are promoted into executable contracts
- closure status changes scientifically

Until then:

- the TP53 frozen replay baseline remains the canonical executable contract
- BRCA1 remains bounded auxiliary executable evidence
- BRCA2 / TSC2 / CREBBP remain replay-ready scientific portability surfaces
- the final harsh holdout/control tribunal remains mixed
