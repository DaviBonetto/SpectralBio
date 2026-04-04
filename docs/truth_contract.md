# SpectralBio Truth Contract

## Two-Layer Contract

SpectralBio has a manuscript scientific contract and a frozen executable replay contract. The repository is aligned only when both are stated together rather than collapsed into a TP53-only story or a BRCA2-only story.

### Manuscript Scientific Contract

- Flagship scientific result: on BRCA2, covariance-aware hidden-state geometry improves the five-model ESM-1v baseline from `0.6324` to `0.6890`, for paired gain `0.0566`, paired 95% CI `[0.0131, 0.1063]`, and empirical `p = 0.0010`
- Validation anchor: `TP53` is the only frozen public canonical replay surface
- Breadth surface: the support-ranked top-25 feasible panel derived from the 15,752-gene ClinVar scan
- Boundary surfaces: the protocol sweep and the BRCA1 failure analysis

### Frozen Executable Replay Contract

- Primary executable claim: `TP53 canonical executable benchmark`
- Primary statement: TP53 is the default executable path and the only frozen canonical scored benchmark
- Auxiliary executable claim: `bounded transfer on a fixed BRCA1 subset (N=100)`
- Auxiliary statement: BRCA1 transfer evidence is limited to the fixed `BRCA1_transfer100` subset and is reported without retraining
- Transfer framing: `secondary transfer evaluation without retraining`
- Repository framing: `research reproducibility artifact`
- Adaptation note: `adaptation recipe only`
- Adaptation statement: any extension beyond TP53 replay, the fixed BRCA1 transfer subset, and the documented scientific audit surfaces requires separate implementation and separate validation

## Non-Claims

- No default `any protein` workflow
- No `works on any protein` claim
- No `strong cross-protein generalization` claim
- No `exceptional cross-protein generalization` claim
- No `broad cross-protein generalization` claim
- No `exceptional cross-protein transfer` claim
- No `strong generalization` claim
- No `clinical deployment`, `clinical use`, or clinical decision support claim
- No claim that BRCA2 is already the frozen default CLI replay target

## Benchmark Ownership

| Surface | Contract Role | Authoritative Sources | Allowed Framing | Forbidden Framing |
| --- | --- | --- | --- | --- |
| `BRCA2` augmentation and benchmark-qualification surfaces | Flagship scientific result | `abstract.md`, `content.md`, `notebooks/final_accept_part3_esm1v_augmentation_A100.ipynb`, `notebooks/final_accept_part4_brca2_canonicalization_A100.ipynb` | flagship stronger-baseline result; public scientific audit surface; benchmark-qualified next canonicalization target | default executable path; TP53 replacement; universal generalization proof |
| `TP53` | Frozen public canonical replay surface | `benchmarks/manifests/tp53_canonical_manifest.json`, `artifacts/expected/expected_metrics.json`, `configs/tp53_canonical.yaml`, `outputs/canonical/summary.json` | deterministic TP53 reproducibility benchmark; validation anchor; canonical executable benchmark | mere auxiliary evidence; stale legacy surface; broad any-protein proof |
| Support-ranked top-25 feasible panel | Performance-blind breadth surface | `content.md`, `notebooks/final_accept_part1_support_panel.ipynb` | breadth evidence; support-ranked panel; anti-cherry-picking surface | universal transfer proof; hand-picked favorable-only proof |
| `BRCA1_transfer100` | Bounded auxiliary executable transfer evidence and continuity surface | `benchmarks/manifests/brca1_transfer_manifest.json`, `artifacts/expected/expected_metrics.json`, `configs/brca1_transfer.yaml` | bounded transfer on a fixed BRCA1 subset (`N=100`) without retraining; secondary transfer evaluation without retraining | co-equal benchmark with TP53; manuscript flagship result; default product path; broad cross-protein generalization proof |
| BRCA1 failure and protocol notebooks | Boundary evidence | `notebooks/final_accept_part5_protocol_sweep_A100.ipynb`, `notebooks/final_accept_part6_panel25_brca1_failure_L4.ipynb` | boundary analysis; structured failure surface; protocol sensitivity evidence | hidden contradiction; co-primary positive benchmark |
| `BRCA1_full_filtered_v1.json` and legacy snapshots | Provenance only | `benchmarks/brca1/brca1_full_filtered_v1.json`, `benchmarks/manifests/source_snapshot.json`, `legacy/*` | provenance-only data; migration safety snapshot | canonical benchmark; official scored execution path |

## Official Metrics

### Manuscript Scientific Audit Metrics

| Surface | Metric | Value | Source Anchors |
| --- | --- | ---: | --- |
| BRCA2 augmentation | ESM-1v baseline AUC | `0.6324` | `abstract.md`; `content.md`; `notebooks/final_accept_part3_esm1v_augmentation_A100.ipynb` |
| BRCA2 augmentation | Covariance + ESM-1v fixed-`0.55` AUC | `0.6890` | `abstract.md`; `content.md`; `notebooks/final_accept_part3_esm1v_augmentation_A100.ipynb` |
| BRCA2 augmentation | Delta vs ESM-1v | `0.0566` | `abstract.md`; `content.md`; `notebooks/final_accept_part3_esm1v_augmentation_A100.ipynb` |
| BRCA2 augmentation | 95% paired bootstrap CI | `[0.0131, 0.1063]` | `abstract.md`; `content.md`; `notebooks/final_accept_part3_esm1v_augmentation_A100.ipynb` |
| BRCA2 augmentation | Empirical permutation `p` | `0.0010` | `abstract.md`; `content.md`; `notebooks/final_accept_part3_esm1v_augmentation_A100.ipynb` |

### Machine-Verified Executable Metrics

These values are official only when they agree across the benchmark manifests and `artifacts/expected/expected_metrics.json`.

| Scope | Metric | Value | Source Anchors |
| --- | --- | ---: | --- |
| TP53 canonical | `0.55*frob_dist + 0.45*ll_proper` AUC | `0.7498` | `benchmarks/manifests/tp53_canonical_manifest.json`; `artifacts/expected/expected_metrics.json` |
| TP53 canonical | Reproducibility delta | `0.0` | `benchmarks/manifests/tp53_canonical_manifest.json`; `artifacts/expected/expected_metrics.json` |
| BRCA1 bounded transfer | `ll_proper` AUC on fixed subset | `0.9174` | `benchmarks/manifests/brca1_transfer_manifest.json`; `artifacts/expected/expected_metrics.json` |

Metric tolerance for machine-verified executable checks is `0.0001`, as defined in `artifacts/expected/verification_rules.json`.

## Source-of-Truth Precedence Ladder

### Executable Replay Precedence

When executable replay files disagree, the higher-precedence source wins and the lower-precedence source must be rewritten, demoted to provenance, or removed from canonical use.

1. `docs/truth_contract.md`
2. `benchmarks/manifests/*`
3. `artifacts/expected/*`
4. `outputs/canonical/*`
5. README, demo, dataset card, and publish mirrors

### Manuscript Scientific Framing Precedence

When paper-facing framing disagrees, the higher-precedence source wins and the lower-precedence source must be rewritten, demoted, or removed from judge-facing use.

1. `docs/truth_contract.md`
2. `abstract.md`
3. `content.md`
4. `notebooks/final_accept_part3_esm1v_augmentation_A100.ipynb`
5. `notebooks/final_accept_part4_brca2_canonicalization_A100.ipynb`
6. `notebooks/final_accept_part1_support_panel.ipynb`
7. `notebooks/final_accept_part5_protocol_sweep_A100.ipynb`
8. `notebooks/final_accept_part6_panel25_brca1_failure_L4.ipynb`
9. README, demo, dataset card, and publish mirrors

## Canonical Evidence Anchors

### Frozen Executable Replay Anchors

- `benchmarks/manifests/tp53_canonical_manifest.json`
- `benchmarks/manifests/brca1_transfer_manifest.json`
- `benchmarks/manifests/checksums.json`
- `benchmarks/manifests/source_snapshot.json`
- `artifacts/expected/expected_metrics.json`
- `artifacts/expected/expected_files.json`
- `artifacts/expected/output_schema.json`
- `artifacts/expected/verification_rules.json`
- `benchmarks/tp53/tp53_canonical_v1.json`
- `benchmarks/tp53/tp53_scores_v1.json`
- `benchmarks/sequences/tp53.fasta`
- `configs/tp53_canonical.yaml`
- `src/spectralbio/pipeline/run_canonical.py`
- `outputs/canonical/run_metadata.json`
- `outputs/canonical/inputs_manifest.json`
- `outputs/canonical/tp53_scores.tsv`
- `outputs/canonical/tp53_metrics.json`
- `outputs/canonical/summary.json`
- `outputs/canonical/roc_tp53.png`
- `outputs/canonical/manifest.json`
- `outputs/canonical/verification.json`
- `benchmarks/brca1/brca1_transfer100_v1.json`
- `benchmarks/sequences/brca1.fasta`
- `configs/brca1_transfer.yaml`
- `src/spectralbio/pipeline/run_transfer.py`
- `outputs/transfer/summary.json`
- `outputs/transfer/variants.json`
- `outputs/transfer/manifest.json`

### Public Scientific Audit Anchors

- `abstract.md`
- `content.md`
- `notebooks/final_accept_part3_esm1v_augmentation_A100.ipynb`
- `notebooks/final_accept_part4_brca2_canonicalization_A100.ipynb`
- `notebooks/final_accept_part1_support_panel.ipynb`
- `notebooks/final_accept_part5_protocol_sweep_A100.ipynb`
- `notebooks/final_accept_part6_panel25_brca1_failure_L4.ipynb`

### Provenance-Only Paths

- `benchmarks/brca1/brca1_full_filtered_v1.json`
- `legacy/colab/spectralbio.ipynb`
- `legacy/colab_results/*`
- `legacy/huggingface_assets/*`
- `legacy/huggingface_data/*`
- `legacy/submit/*`

These paths may preserve history, but they do not own canonical executable claims, canonical metrics, or canonical execution semantics.

## Wording Contract

### Core Executable Allowlist

- `TP53 canonical executable benchmark`
- `bounded transfer on a fixed BRCA1 subset (N=100)`
- `secondary transfer evaluation without retraining`
- `adaptation recipe only`
- `research reproducibility artifact`

### Manuscript-Aligned Additions

- `BRCA2 flagship scientific result`
- `TP53 validation anchor`
- `TP53 frozen public canonical replay surface`
- `support-ranked top-25 feasible panel`
- `public scientific audit surface`
- `benchmark-qualified BRCA2 result`

### Repository-Facing Framing Rules

- When discussing paper-level claims, BRCA2 must be described as the flagship scientific result.
- When discussing cold-start execution, TP53 must be described as the default path and the only frozen public canonical replay surface.
- BRCA1 must be described as bounded, fixed-subset auxiliary evidence only.
- BRCA1 wording should stay close to `bounded transfer on a fixed BRCA1 subset (N=100) without retraining`.
- Do not headline BRCA1 as proof of default cross-protein behavior.
- Do not present BRCA2 as already replacing TP53 in the frozen CLI replay contract.
- Do not present rounded values such as `0.750` or `0.917` as official headline executable metrics. If rounding is necessary inside figures, label it as rounded and keep the official exact values elsewhere in the same artifact.

### Forbidden Claim Phrases

- `any protein`
- `works on any protein`
- `strong cross-protein generalization`
- `exceptional cross-protein generalization`
- `broad cross-protein generalization`
- `exceptional cross-protein transfer`
- `strong generalization`
- `clinical deployment`
- `clinical use`

## Verification Contract

The repository is aligned only if all of the following are true:

1. BRCA2 is unambiguously framed as the flagship scientific result in paper-facing surfaces.
2. TP53 is unambiguously framed as the only frozen public canonical replay surface and the default executable path.
3. The support-ranked top-25 panel is unambiguously framed as the performance-blind breadth surface.
4. BRCA1 is unambiguously bounded auxiliary executable evidence without retraining and is never promoted to co-primary manuscript center.
5. Official executable metrics match the benchmark manifests and `artifacts/expected/expected_metrics.json` within the declared tolerance.
6. Legacy and provenance paths are never presented as canonical execution paths.
7. If a lower-precedence surface conflicts with this contract, that surface must be rewritten, demoted, or removed from canonical use.

## Phase Numbering Note

The original rebuild brief mixed `fase_06` intent with one reference to `fase_05_validation_submission`. The canonical repository numbering is:

- `fase_00_truth_contract`
- `fase_01_repo_rebuild`
- `fase_02_benchmarks_dataset`
- `fase_03_pipeline`
- `fase_04_demo`
- `fase_05_docs_skill`
- `fase_06_validation_submission`
