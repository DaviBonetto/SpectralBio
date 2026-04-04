# Introduction

Zero-shot missense scoring with protein language models is often framed as a sequence-likelihood problem. SpectralBio advances a narrower claim: mutation-induced perturbations in the local full-matrix covariance geometry of ESM2 hidden states carry real pathogenicity signal, but that signal has to be separated into manuscript-facing scientific evidence and frozen executable replay evidence.

The manuscript's flagship scientific result is on `BRCA2`, where covariance-aware hidden-state geometry is tested against a stronger five-model ESM-1v external baseline rather than against an internal likelihood branch alone. The strongest public executable replay surface, however, remains the `TP53 canonical executable benchmark`, which is the only frozen public canonical replay surface released for cold-start verification. The support-ranked top-25 feasible panel provides the breadth surface, and the protocol sweep plus BRCA1 failure analysis provide the main public boundary surfaces.

## Scientific Center

On BRCA2, adding covariance-aware geometry to the ESM-1v ensemble improves AUC from `0.6324` to `0.6890`, for a paired gain of `0.0566`, paired 95% confidence interval `[0.0131, 0.1063]`, and empirical permutation `p = 0.0010`. This is the manuscript's flagship result because it tests covariance against a stronger external baseline and makes the covariance contribution falsifiable rather than purely internal to one benchmark.

The broader study does not stop at one favorable gene. A performance-blind support-ranked top-25 feasible panel derived from a 15,752-gene ClinVar scan is used as the breadth surface, while the protocol sweep and BRCA1 failure notebook expose where the effect is sensitive, structured, or absent. The scientific claim is therefore not universal transfer or clinical deployment. It is a narrower statement that full-matrix covariance geometry contains real zero-shot pathogenicity signal, can improve a stronger baseline in a benchmark-qualified gene, and behaves as a structured phenomenon rather than a universal law.

## Frozen Executable Replay Center

The released executable contract is intentionally stricter than the paper's scientific center.

- Primary executable benchmark: `TP53 canonical executable benchmark`
- Auxiliary executable surface: `bounded transfer on a fixed BRCA1 subset (N=100) without retraining`
- Transfer framing: `secondary transfer evaluation without retraining`
- Repository framing: `research reproducibility artifact`
- Extension policy: `adaptation recipe only`

Under that frozen contract, the canonical TP53 replay reaches AUC `0.7498` for `0.55*frob_dist + 0.45*ll_proper`, and the fixed BRCA1 auxiliary transfer subset reports `ll_proper` AUC `0.9174`. The executable replay surface exists to make the repository mechanically challengeable. It does not replace BRCA2 as the manuscript's scientific center.

## Public Audit Surfaces

The public scientific audit surfaces that establish the BRCA2-first hierarchy are:

- `abstract.md`
- `content.md`
- `notebooks/final_accept_part3_esm1v_augmentation_A100.ipynb`
- `notebooks/final_accept_part4_brca2_canonicalization_A100.ipynb`
- `notebooks/final_accept_part1_support_panel.ipynb`
- `notebooks/final_accept_part5_protocol_sweep_A100.ipynb`
- `notebooks/final_accept_part6_panel25_brca1_failure_L4.ipynb`

The cold-start executable replay surface is exposed separately through `SKILL.md`, `docs/truth_contract.md`, `docs/reproducibility.md`, and the frozen TP53 / BRCA1 manifests and outputs.

## Reproducibility

The experiment uses fixed seeds (`torch`, `numpy`, and `random` all set to 42), public ClinVar-derived benchmark payloads, and the public ESM2-150M checkpoint as model provenance. Under the repository's canonical execution path, the TP53 canonical executable benchmark reproduces with **reproducibility delta = 0.0**.
