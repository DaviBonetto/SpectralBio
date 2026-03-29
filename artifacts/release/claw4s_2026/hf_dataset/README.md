# SpectralBio Dataset Card

## Benchmark Contract

SpectralBio is a research reproducibility artifact with one canonical executable benchmark and one bounded secondary transfer evaluation.

- TP53 canonical executable benchmark: primary scored benchmark and default executable path.
- Bounded transfer on a fixed BRCA1 subset (`N=100`): secondary benchmark only.
- Transfer framing: `secondary transfer evaluation without retraining`
- Adaptation recipe only: any broader reuse requires separate validation.
- Provenance-only data: `BRCA1_full_filtered_v1.json` is preserved for transparency and transfer-subset derivation.

TP53 is the only canonical scored benchmark. `BRCA1_transfer100` is secondary bounded transfer evidence without retraining.

## Frozen Files

| Surface | Role | File | Count | Label split | SHA256 |
| --- | --- | --- | ---: | --- | --- |
| TP53 canonical variants | Canonical executable benchmark | `benchmarks/tp53/tp53_canonical_v1.json` | 255 | pathogenic=115, benign=140 (`1`=`pathogenic`, `0`=`benign`) | `ba37cef10ef3a334932be0b0b7a7d4756d15ea7c6aaf29a777ef79c14e1d4fa6` |
| TP53 score reference | Canonical companion file | `benchmarks/tp53/tp53_scores_v1.json` | 255 | aligned to TP53 canonical variants by name and order | `a07066ca3d55cce98d81a04a30f71ab99e3c5cbb95d28a4a135d03229e809b28` |
| BRCA1 transfer subset | Secondary transfer evaluation without retraining | `benchmarks/brca1/brca1_transfer100_v1.json` | 100 | pathogenic=29, benign=71 (`1`=`pathogenic`, `0`=`benign`) | `62c3bcc50d0258adb0af2fef77be00f763ff3c03f3adb27e52393d0ea49f2341` |
| BRCA1 full filtered | Provenance-only source snapshot | `benchmarks/brca1/brca1_full_filtered_v1.json` | 512 | pathogenic=165, benign=347 (`1`=`pathogenic`, `0`=`benign`) | `4a4e911a226b4f5c5aa7069e39d5ccfc22be122678bf2d11275f70240d0d7a46` |

## Official Metrics

- TP53 canonical executable benchmark: `0.55 * frob_dist + 0.45 * ll_proper` AUC = `0.7498`
- Bounded transfer on a fixed BRCA1 subset (`N=100`) without retraining: `ll_proper` AUC = `0.9174`
- Reproducibility delta: `0.0`

## Provenance Link

- `brca1_transfer100_v1.json` is the fixed first 100 records from `brca1_full_filtered_v1.json`.
- `BRCA1_full_filtered_v1.json` is preserved for provenance and migration safety only.
- Canonical truth lives in `docs/truth_contract.md`, `benchmarks/manifests/*.json`, and `artifacts/expected/*`.

## References

- Truth contract: `docs/truth_contract.md`
- Canonical benchmark manifest: `benchmarks/manifests/tp53_canonical_manifest.json`
- Transfer benchmark manifest: `benchmarks/manifests/brca1_transfer_manifest.json`
- Provenance manifest: `benchmarks/manifests/source_snapshot.json`
- Checksums: `benchmarks/manifests/checksums.json`
