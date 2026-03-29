# SpectralBio Truth Contract

## Claim Contract

SpectralBio is a research reproducibility artifact with one canonical executable benchmark and one bounded secondary transfer evaluation.

- Primary claim: `TP53 canonical executable benchmark`
- Primary statement: TP53 is the product, the default executable path, and the only canonical scored benchmark.
- Secondary claim: `bounded transfer on a fixed BRCA1 subset (N=100)`
- Secondary statement: BRCA1 transfer evidence is limited to the fixed `BRCA1_transfer100` subset and is reported without retraining.
- Adaptation note: `adaptation recipe only`
- Adaptation statement: any extension beyond TP53 and the fixed BRCA1 transfer subset is an adaptation recipe, not a validated default workflow.

## Non-Claims

- No default `any protein` workflow.
- No `works on any protein` claim.
- No `strong cross-protein generalization` claim.
- No `exceptional cross-protein generalization` claim.
- No `broad cross-protein generalization` claim.
- No `exceptional cross-protein transfer` claim.
- No `strong generalization` claim.
- No `clinical deployment`, `clinical use`, or clinical decision support claim.

## Benchmark Ownership

| Benchmark / Surface | Contract Role | Authoritative Sources | Allowed Framing | Forbidden Framing |
| --- | --- | --- | --- | --- |
| `TP53` | Primary canonical benchmark | `benchmarks/manifests/tp53_canonical_manifest.json`, `artifacts/expected/expected_metrics.json`, `configs/tp53_canonical.yaml` | deterministic TP53 reproducibility benchmark; canonical executable benchmark | secondary evidence; transfer-only evidence; broad any-protein proof |
| `BRCA1_transfer100` | Secondary bounded transfer evidence only | `benchmarks/manifests/brca1_transfer_manifest.json`, `artifacts/expected/expected_metrics.json`, `configs/brca1_transfer.yaml` | bounded transfer on a fixed BRCA1 subset (`N=100`) without retraining; secondary transfer evaluation without retraining | co-equal benchmark with TP53; default product path; broad cross-protein generalization proof |
| `BRCA1_full_filtered_v1.json` and legacy snapshots | Provenance only | `benchmarks/brca1/brca1_full_filtered_v1.json`, `benchmarks/manifests/source_snapshot.json`, `legacy/*` | provenance-only data; migration safety snapshot | canonical benchmark; official scored execution path |

## Official Metrics

These values are official only when they agree across the benchmark manifests and `artifacts/expected/expected_metrics.json`.

| Scope | Metric | Value | Source Anchors |
| --- | --- | ---: | --- |
| TP53 canonical | `0.55*frob_dist + 0.45*ll_proper` AUC | `0.7498` | `benchmarks/manifests/tp53_canonical_manifest.json`; `artifacts/expected/expected_metrics.json` |
| TP53 canonical | Reproducibility delta | `0.0` | `benchmarks/manifests/tp53_canonical_manifest.json`; `artifacts/expected/expected_metrics.json` |
| BRCA1 bounded transfer | `ll_proper` AUC on fixed subset | `0.9174` | `benchmarks/manifests/brca1_transfer_manifest.json`; `artifacts/expected/expected_metrics.json` |

Metric tolerance for verification is `0.0001`, as defined in `artifacts/expected/verification_rules.json`.

## Source-of-Truth Precedence Ladder

When two files disagree, the higher-precedence source wins and the lower-precedence source must be rewritten, demoted to provenance, or removed from canonical use.

1. `docs/truth_contract.md`
2. `benchmarks/manifests/*`
3. `artifacts/expected/*`
4. paper files derived from canonical outputs
5. README, demo, dataset card, and publish mirrors

## Canonical Evidence Anchors

### Canonical benchmark anchors

- `benchmarks/manifests/tp53_canonical_manifest.json`
- `benchmarks/manifests/brca1_transfer_manifest.json`
- `benchmarks/manifests/checksums.json`
- `benchmarks/manifests/source_snapshot.json`
- `artifacts/expected/expected_metrics.json`
- `artifacts/expected/expected_files.json`
- `artifacts/expected/output_schema.json`
- `artifacts/expected/verification_rules.json`

### Canonical execution path

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

### Secondary bounded transfer path

- `benchmarks/brca1/brca1_transfer100_v1.json`
- `benchmarks/sequences/brca1.fasta`
- `configs/brca1_transfer.yaml`
- `src/spectralbio/pipeline/run_transfer.py`
- `outputs/transfer/summary.json`
- `outputs/transfer/variants.json`
- `outputs/transfer/manifest.json`

### Provenance-only paths

- `benchmarks/brca1/brca1_full_filtered_v1.json`
- `legacy/colab/spectralbio.ipynb`
- `legacy/colab_results/*`
- `legacy/huggingface_assets/*`
- `legacy/huggingface_data/*`
- `legacy/submit/*`

These paths may preserve history, but they do not own canonical claims, canonical metrics, or canonical execution semantics.

## Wording Contract

### Allowlist

- `TP53 canonical executable benchmark`
- `bounded transfer on a fixed BRCA1 subset (N=100)`
- `secondary transfer evaluation without retraining`
- `adaptation recipe only`
- `research reproducibility artifact`

### Repository-Facing Framing Rules

- TP53 must be described as primary, canonical, and executable.
- BRCA1 must be described as secondary, bounded, fixed-subset evidence only.
- BRCA1 wording should stay close to `bounded transfer on a fixed BRCA1 subset (N=100) without retraining`.
- Do not headline BRCA1 as proof of default cross-protein behavior.
- Do not present rounded values such as `0.750` or `0.917` as official headline metrics. If rounding is necessary inside figures, label it as rounded and keep the official exact values elsewhere in the same artifact.

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

1. No canonical or mirror surface states or implies default broad any-protein behavior.
2. TP53 is unambiguously the primary benchmark and default executable path.
3. BRCA1 is unambiguously secondary, bounded, fixed-subset evidence without retraining.
4. Official metrics match the benchmark manifests and `artifacts/expected/expected_metrics.json` within the declared tolerance.
5. Legacy and provenance paths are never presented as canonical execution paths.
6. If a lower-precedence surface conflicts with this contract, that surface must be rewritten, demoted, or removed from canonical use.

## Phase Numbering Note

The original rebuild brief mixed `fase_06` intent with one reference to `fase_05_validation_submission`. The canonical repository numbering is:

- `fase_00_truth_contract`
- `fase_01_repo_rebuild`
- `fase_02_benchmarks_dataset`
- `fase_03_pipeline`
- `fase_04_demo`
- `fase_05_docs_skill`
- `fase_06_validation_submission`
