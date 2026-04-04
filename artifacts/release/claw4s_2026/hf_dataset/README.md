# SpectralBio Dataset Card

## Public Hierarchy

SpectralBio separates manuscript-facing scientific centrality from frozen executable replay centrality.

- Flagship scientific result: `BRCA2` covariance-aware augmentation against a stronger five-model ESM-1v baseline
- Validation anchor: `TP53` is the only frozen public canonical replay surface
- Breadth surface: support-ranked top-25 feasible panel derived from the 15,752-gene ClinVar scan
- Boundary surfaces: protocol sweep and BRCA1 failure analysis
- Auxiliary executable surface: `bounded transfer on a fixed BRCA1 subset (N=100) without retraining`

This dataset card therefore describes both the released executable payloads and the broader scientific audit context in which they sit.

## Frozen Executable Replay Contract

- Primary executable benchmark: `TP53 canonical executable benchmark`
- Auxiliary executable surface: `bounded transfer on a fixed BRCA1 subset (N=100) without retraining`
- Transfer framing: `secondary transfer evaluation without retraining`
- Repository framing: `research reproducibility artifact`
- Extension policy: `adaptation recipe only`
- Provenance-only data: `BRCA1_full_filtered_v1.json` is preserved for transparency and transfer-subset derivation only

TP53 remains the only canonical scored benchmark. `BRCA1_transfer100` remains bounded auxiliary executable evidence without retraining.

## Frozen Files

| Surface | Role | File | Count | Label split | SHA256 |
| --- | --- | --- | ---: | --- | --- |
| TP53 canonical variants | Canonical executable benchmark | `benchmarks/tp53/tp53_canonical_v1.json` | 255 | pathogenic=115, benign=140 (`1`=`pathogenic`, `0`=`benign`) | `ba37cef10ef3a334932be0b0b7a7d4756d15ea7c6aaf29a777ef79c14e1d4fa6` |
| TP53 score reference | Canonical companion file | `benchmarks/tp53/tp53_scores_v1.json` | 255 | aligned to TP53 canonical variants by name and order | `a07066ca3d55cce98d81a04a30f71ab99e3c5cbb95d28a4a135d03229e809b28` |
| BRCA1 transfer subset | Secondary transfer evaluation without retraining | `benchmarks/brca1/brca1_transfer100_v1.json` | 100 | pathogenic=29, benign=71 (`1`=`pathogenic`, `0`=`benign`) | `62c3bcc50d0258adb0af2fef77be00f763ff3c03f3adb27e52393d0ea49f2341` |
| BRCA1 full filtered | Provenance-only source snapshot | `benchmarks/brca1/brca1_full_filtered_v1.json` | 512 | pathogenic=165, benign=347 (`1`=`pathogenic`, `0`=`benign`) | `4a4e911a226b4f5c5aa7069e39d5ccfc22be122678bf2d11275f70240d0d7a46` |

## Public Scientific Audit Surfaces

The BRCA2 flagship result and the support-ranked breadth evidence are carried by the public scientific audit surfaces rather than by the frozen executable dataset payload itself.

- `abstract.md`
- `content.md`
- `notebooks/final_accept_part3_esm1v_augmentation_A100.ipynb`
- `notebooks/final_accept_part4_brca2_canonicalization_A100.ipynb`
- `notebooks/final_accept_part1_support_panel.ipynb`
- `notebooks/final_accept_part5_protocol_sweep_A100.ipynb`
- `notebooks/final_accept_part6_panel25_brca1_failure_L4.ipynb`

## Official Metrics

### Manuscript Scientific Audit Metrics

- BRCA2 ESM-1v baseline AUC: `0.6324`
- BRCA2 covariance + ESM-1v AUC: `0.6890`
- BRCA2 paired gain vs ESM-1v: `0.0566`
- BRCA2 paired 95% bootstrap CI: `[0.0131, 0.1063]`
- BRCA2 empirical permutation `p`: `0.0010`

### Machine-Verified Executable Metrics

- TP53 canonical executable benchmark: `0.55 * frob_dist + 0.45 * ll_proper` AUC = `0.7498`
- Bounded transfer on a fixed BRCA1 subset (`N=100`) without retraining: `ll_proper` AUC = `0.9174`
- Reproducibility delta: `0.0`

## Provenance Link

- `brca1_transfer100_v1.json` is the fixed first 100 records from `brca1_full_filtered_v1.json`.
- `BRCA1_full_filtered_v1.json` is preserved for provenance and migration safety only.
- Canonical truth lives in `docs/truth_contract.md`, `benchmarks/manifests/*.json`, and `artifacts/expected/*`.
- Scientific framing truth lives in `abstract.md`, `content.md`, and the BRCA2 / panel notebooks listed above.

## References

- Truth contract: `docs/truth_contract.md`
- Reproducibility notes: `docs/reproducibility.md`
- Canonical benchmark manifest: `benchmarks/manifests/tp53_canonical_manifest.json`
- Transfer benchmark manifest: `benchmarks/manifests/brca1_transfer_manifest.json`
- Provenance manifest: `benchmarks/manifests/source_snapshot.json`
- Checksums: `benchmarks/manifests/checksums.json`
