# SpectralBio Truth Contract

## Repository Precedence

When repository-facing execution truth and manuscript-facing scientific truth differ, resolve by precedence rather than convenience.

### Primary precedence

1. `docs/truth_contract.md`
2. `docs/reproducibility.md`
3. `artifacts/expected/expected_metrics.json`
4. `artifacts/expected/expected_files.json`
5. `artifacts/expected/output_schema.json`
6. `artifacts/expected/verification_rules.json`
7. `outputs/canonical/summary.json`
8. `outputs/canonical/verification.json`

### Supporting executable corroborators

- `benchmarks/manifests/tp53_canonical_manifest.json`
- `benchmarks/manifests/brca1_transfer_manifest.json`
- `benchmarks/manifests/source_snapshot.json`
- `benchmarks/manifests/checksums.json`
- `src/spectralbio/cli.py`

### Supporting scientific corroborators

- `abstract.md`
- `content.md`
- current manuscript notebook chain under `New Notebooks/`

### Conflict rule

- If a legacy notebook, stale README section, or convenience command suggests a stronger claim than the current truth contract or the final holdout/control boundary, the bounded final claim wins.
- If a legacy surface suggests a weaker public story than the current manuscript plus Block 13 portability evidence, the updated manuscript-aligned truth wins.
- If executable docs and CLI behavior conflict, the executable truth must be rewritten to match the code.

## Claim Taxonomy

Use this taxonomy consistently across all package-facing documents.

1. **Canonical executable replay surface**  
   Default public cold-start execution contract.

2. **Auxiliary bounded executable surface**  
   Executable, but explicitly secondary and bounded.

3. **Scientific audit surface**  
   Manuscript-facing, notebook-backed evidence.

4. **Replay-ready portability surface**  
   Target-level public replay-ready portability evidence that does not imply default CLI replay parity.

5. **Transfer-positive target surface**  
   Replay-ready portability surface that is explicitly positive at the target level.

6. **Negative guardrail surface**  
   Explicit retained negative or boundary surface.

7. **Earlier harsh-firewall chain**  
   The pre-Block-13 late adjudication chain that stops at supportive rather than nuclear.

8. **Final holdout/control closure boundary**  
   The harshest model-level closure tribunal, currently mixed and non-closing.

## Current Truthful Claim Set

### Canonical executable replay

- `TP53` is the only canonical executable replay surface
- Default public path:
  - `uv sync --frozen`
  - `uv run spectralbio canonical`
- Canonical executable benchmark metric:
  - `0.55*frob_dist + 0.45*ll_proper` AUC = `0.7498`

### Auxiliary bounded executable surface

- `BRCA1_transfer100` is the only auxiliary bounded executable surface
- It remains:
  - fixed subset (`N=100`)
  - without retraining
  - secondary to TP53
- Official bounded executable metric:
  - `ll_proper` AUC = `0.9174`

### Flagship scientific result

- `BRCA2` is the flagship stronger-baseline scientific result
- Official scientific audit metrics:
  - ESM-1v baseline AUC = `0.6324`
  - covariance + ESM-1v AUC = `0.6890`
  - paired gain = `0.0566`
  - paired 95% CI = `[0.0131, 0.1063]`
  - empirical permutation `p = 0.0010`

### Qualitative centerpiece

- Scale-repair failure mode remains part of the central claim set
- Core qualitative truth:
  - ESM2-150M overstates covariance disruption in a narrow chemistry-defined regime
  - ESM2-650M repairs it
  - likelihood does not repair in parallel

### Replay-ready portability layer

- Replay-ready targets:
  - `TP53`
  - `BRCA2`
  - `TSC2`
  - `CREBBP`
- Transfer-positive targets:
  - `TSC2`
  - `CREBBP`
- Interpretation:
  - the public story is no longer only TP53 plus bounded support
  - this is target-level portability strengthening
  - this is not yet model-level universal closure

### Negative guardrails

- `BRCA1`
- `MSH2`

These surfaces must remain explicit. They are part of the scientific rigor of the package, not removable exceptions.

### Earlier harsh-firewall chain

- The earlier late adjudication chain remains part of package truth
- It still supports:
  - supportive rather than nuclear
- It still does **not** support:
  - universal closure
  - model-family-wide closure

### Final holdout/control closure boundary

- Block 14 final claim status:
  - `closure_still_mixed`
- Holdout-positive models:
  - `[]`
- Control-win models:
  - `[]`
- Transfer-positive models at that harsh model-level closure standard:
  - `[]`
- Negative guardrails clean:
  - `false`

Interpretation:
- the final harsh tribunal remains mixed
- strengthened portability and failed full closure must coexist

## Benchmark Ownership

| Surface | Contract role | Allowed framing | Forbidden framing |
|---|---|---|---|
| `TP53` | canonical executable replay surface | default executable replay benchmark; validation anchor | mere auxiliary evidence; universal portability proof |
| `BRCA1_transfer100` | auxiliary bounded executable surface | bounded transfer on a fixed BRCA1 subset without retraining | co-primary benchmark; universal transfer proof |
| `BRCA2` | flagship scientific audit surface; replay-ready portability surface | flagship stronger-baseline result; next full canonicalization target under the benchmark-promotion rule | already the default CLI replay path |
| `TSC2` | replay-ready portability surface; transfer-positive target surface | replay-ready transfer surface; portability witness | default CLI replay path; model-level full closure |
| `CREBBP` | replay-ready portability surface; transfer-positive target surface | replay-ready transfer surface; portability witness | default CLI replay path; model-level full closure |
| `BRCA1` | negative guardrail surface | anti-case; structured boundary surface | disposable exception or hidden contradiction |
| `MSH2` | negative guardrail surface | decisive negative replication; boundary surface | minor footnote or omitted guardrail |

## Claims Explicitly Forbidden

- universal generalization
- full closure
- broad cross-protein law
- model-family-wide closure
- holdout-positive closure
- control-win closure
- generic works-on-any-protein portability
- universal alpha transfer
- claim that every replay-ready target is already a default CLI benchmark
- claim that `BRCA2`, `TSC2`, or `CREBBP` run through the same default public CLI path as `TP53` unless the code changes
- collapse of target-level portability into model-level closure
- erasure of `BRCA1` or `MSH2`
- erasure of the earlier harsh-firewall chain

## Current Manuscript-Aligned Scientific Audit Anchors

### Current manuscript chain

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

### Legacy manuscript surfaces

- `notebooks/final_accept_part1_support_panel.ipynb`
- `notebooks/final_accept_part3_esm1v_augmentation_A100.ipynb`
- `notebooks/final_accept_part4_brca2_canonicalization_A100.ipynb`
- `notebooks/final_accept_part5_protocol_sweep_A100.ipynb`
- `notebooks/final_accept_part6_panel25_brca1_failure_L4.ipynb`

Legacy surfaces may still be read for corroboration. They do not outrank the current manuscript chain.

## Machine-Verified Executable Metrics

These values are official only when they agree across the benchmark manifests, expected artifacts, and generated outputs.

| Scope | Metric | Value |
|---|---|---:|
| TP53 canonical | `0.55*frob_dist + 0.45*ll_proper` AUC | `0.7498` |
| TP53 canonical | reproducibility delta | `0.0` |
| BRCA1 bounded transfer | `ll_proper` AUC on fixed subset | `0.9174` |

Metric tolerance for machine-verified executable checks is `0.0001`.

## Wording Contract

### Executable allowlist

- `TP53 canonical executable benchmark`
- `bounded transfer on a fixed BRCA1 subset (N=100) without retraining`
- `secondary transfer evaluation without retraining`
- `research reproducibility artifact`

### Scientific addenda allowlist

- `BRCA2 flagship stronger-baseline result`
- `TP53 validation anchor`
- `replay-ready multi-target portability`
- `transfer-positive targets`
- `negative guardrails`
- `final holdout/control closure remains mixed`

### Forbidden wording directions

- any phrase that implies default executable parity across all replay-ready targets
- any phrase that turns replay-ready portability into model-level closure
- any phrase that erases `BRCA1` and `MSH2`
- any phrase that rewinds the package to a TP53-only public story

## Verification Contract

The repository package is aligned only if all of the following are true:

1. `TP53` remains the only canonical executable replay surface.
2. `BRCA1_transfer100` remains bounded auxiliary executable evidence.
3. `BRCA2` remains the flagship stronger-baseline scientific result.
4. `TSC2` and `CREBBP` are explicitly present as replay-ready transfer-positive targets.
5. `BRCA1` and `MSH2` remain explicit negative guardrails.
6. The earlier harsh-firewall chain remains present.
7. Block 13 portability strengthening is present.
8. Block 14 mixed final closure is present.
9. No document collapses target-level portability into model-level closure.
10. No document claims universal or fully closed generalization.
