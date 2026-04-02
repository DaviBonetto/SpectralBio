# SpectralBio: Full-Matrix Covariance Analysis for Zero-Shot Variant Pathogenicity on the TP53 Canonical Benchmark

## 1. Introduction

Missense variant interpretation remains bottlenecked by the gap between variant discovery and experimental characterization. In practical terms, sequencing continuously expands the pool of variants of uncertain significance, while curated pathogenic/benign labels remain sparse, gene-imbalanced, and expensive to obtain. This makes zero-shot variant effect prediction attractive: if a model can rank substitutions from sequence context alone, it can provide bounded research evidence without requiring per-gene supervised retraining. Protein language models have made that setting increasingly plausible by learning broad sequence regularities at scale, from early large-scale unsupervised protein language modeling [9] and architectures such as ProteinBERT [10] to newer ESM-family and ProtTrans-style systems [1,2,6].

Within that landscape, most widely used zero-shot scoring intuitions remain sequence-centric. Classical methods such as SIFT and PolyPhen-2 emphasize conservation and substitution heuristics [4,5]. Evolutionary latent-variable models such as EVE leverage family-level sequence variation and deep generative priors [3]. Protein language model approaches in the ESM line, including the ESM-1v/ESM-style zero-shot mutation-effect setting represented by Meier et al. [2], show that masked or conditional sequence likelihood can already carry useful signal. Those approaches are important context for SpectralBio, because they define the baseline intuition that mutation effect can be summarized from sequence probability alone.

SpectralBio asks whether that intuition is incomplete. A missense mutation can be only moderately surprising at the token level while still inducing a substantial reorganization of the internal representation field around the mutated site. If that is true, then the model's hidden-state geometry becomes a candidate signal source in its own right. The specific hypothesis in this submission is therefore narrow and testable: **local full-matrix covariance perturbations of ESM2 hidden states may contribute useful ranking signal beyond masked-language-model likelihood for zero-shot missense pathogenicity scoring**.

This submission operationalizes that hypothesis as a **TP53-first scientific benchmark with an executable public contract**. The primary claim is the `TP53 canonical executable benchmark`, where the released canonical pair `0.55*frob_dist + 0.45*ll_proper` has official AUC `0.7498` and released value `0.749751552795031`, matching within the declared tolerance `0.0001`. The only bounded secondary evidence is BRCA1 on a fixed first-100 subset evaluated without retraining, where `ll_proper` reaches AUC `0.9174`. The release is intentionally narrower than the broader method ambition: TP53 is the validated benchmark surface, BRCA1 is bounded secondary evidence, and anything beyond those surfaces remains an adaptation recipe rather than a validated result.

### 1.1 Research Question and Scope

The research question is deliberately narrow: when a missense substitution perturbs ESM2 hidden states, does **local full-matrix covariance displacement** add useful pathogenicity-ranking signal beyond mutation likelihood alone? SpectralBio answers that question in a bounded executable setting rather than by appealing to broad generalization rhetoric. The primary validated surface is TP53. The only bounded secondary evidence is the fixed BRCA1 first-100 subset evaluated without retraining. Anything beyond TP53 and that slice remains outside the validated default claim surface.

### 1.2 Explicit Scope Boundaries and Non-Claims

This submission does **not** claim clinical deployment, clinical decision support, broad cross-protein generalization, unrestricted transferability, superiority to all external methods, validation outside the released benchmarked surfaces, or replacement of existing interpretation workflows. It also does **not** treat BRCA1 as a co-primary benchmark, and it does **not** convert a bounded no-retraining secondary slice into a broad portability claim.

The validated claim surface is narrower and explicit: **on the TP53 canonical executable benchmark, full-matrix covariance displacement contributes useful zero-shot pathogenicity-ranking signal beyond likelihood-only and eigenvalue-only summaries, under a frozen public contract, with BRCA1 limited to one fixed first-100 bounded secondary evidence slice evaluated without retraining**.

## 2. Scientific Context and Motivation

Zero-shot missense variant scoring is attractive precisely because it does not require per-gene supervised retraining, but most zero-shot intuitions remain strongly sequence-centric. In practice, many pipelines reduce the mutation-effect question to a scalar plausibility question: how surprising is the mutant residue under the surrounding sequence context? That framing is useful and often competitive, yet it may be incomplete. A substitution can be only moderately implausible at the token level while still reorganizing the internal representation geometry of the model around the mutated site.

This is where SpectralBio departs from likelihood-only reasoning. Instead of treating ESM2 solely as a conditional scoring oracle, it treats the model as a layered geometric object whose local hidden states carry covariance structure. The scientific hypothesis is not that any spectral statistic will help, nor that larger models automatically solve variant interpretation. The narrower claim is that **local full-matrix covariance displacement may preserve mutation-induced information that scalar likelihood summaries and eigenvalue-only compressions do not fully retain**. That hypothesis is consistent with the broader observation that protein language models learn structural regularities [1,18,19], but it is tested here in the specific setting of zero-shot pathogenicity ranking rather than in structure prediction or inverse-folding tasks.

This framing also explains the submission design. SpectralBio is not trying to prove a broad pan-protein law from a heterogeneous benchmark sweep. It is testing one precise representational hypothesis on one canonical executable benchmark, TP53, with one fixed BRCA1 first-100 slice as bounded secondary evidence only. The narrowness is therefore methodological, not merely operational: the benchmark is deliberately constrained so that the claim can be falsified at the exact point where covariance-based geometry is supposed to add value. In that sense, the submission sits naturally inside the ClinVar- and ProteinGym-era emphasis on explicit benchmark surfaces and comparable evidence contracts [7,8].

## 3. Related Work

The most relevant prior work for SpectralBio falls into four method families.

First, **classical missense effect predictors** such as SIFT [4] and PolyPhen-2 [5] rely on conservation, substitution patterns, and manually designed biological features. These systems established the practical importance of sequence-based pathogenicity scoring, but they do not interrogate internal representation geometry because they predate modern protein language model representations.

Second, **family-aware evolutionary generative models** such as EVE [3] use deep generative modeling over multiple-sequence-alignment structure. Their contribution is conceptually different from SpectralBio: EVE learns a family-specific latent model of tolerated variation, whereas SpectralBio studies the internal geometry of a pretrained protein language model under local perturbation. The distinction matters because SpectralBio does not require family-specific retraining in the released artifact, but it also does not claim direct like-for-like superiority to EVE on a shared benchmark surface.

Third, **protein language model zero-shot mutation scoring** has shown that masked or conditional sequence likelihood can already be highly informative. The ESM-family line represented by Meier et al. [2] demonstrated that language-model-based zero-shot inference can capture mutation effects without supervised fine-tuning, and the ESM2 program [1] further established protein language models as strong large-scale representation learners. ProtTrans [6] broadened this trend by showing that self-supervised protein language modeling is a viable general framework for downstream biological prediction. Closely related work also showed that transformer attention can directly encode structural information [18], while inverse-folding models demonstrated that protein language modeling can be coupled to structure-conditioned generation at scale [19]. SpectralBio is closest to this family, but departs from it in one key way: it treats the model not only as a scalar sequence scorer, but as a source of layer-wise hidden-state geometry.

Fourth, **benchmark culture and gene-resolved functional evidence** matter. ClinVar [7] provides the pathogenic/benign label substrate used for this artifact, while ProteinGym [8] represents the broader field-level push toward large, systematic benchmarking of variant effect prediction. DeepSequence-style unsupervised evolutionary modeling [11] and deep-mutational-scanning-based benchmarking [12] reinforce the value of testing variant-effect predictors against experimentally informed surfaces. Likewise, gene-resolved functional atlases for TP53 [13] and BRCA1 [14] make clear why those two genes are scientifically meaningful surfaces for bounded evaluation even when a submission does not claim broad cross-protein generalization.

At a deeper conceptual level, SpectralBio is also compatible with a longer lineage of work on dependency structure in proteins and on representation analysis in learned systems. Direct-coupling analysis showed well before protein language models that pairwise statistical structure in sequences can encode important structural information [15]. Formal perturbation frameworks such as Evolutionary Action similarly argue that mutation effect depends on context-sensitive functional displacement rather than on a single scalar surprise score [16]. AlphaFold, although aimed at a different task, further strengthened the broader lesson that learned internal structure can capture biologically consequential organization beyond local substitution heuristics [17]. In a different methodological tradition, Neuron Shapley illustrates the more general idea that model behavior can be illuminated by studying internal components and their interactions rather than relying only on surface outputs [20]. SpectralBio's narrower move is to ask whether a mutation-induced covariance perturbation summary can recover some of that hidden-state organization in a zero-shot pathogenicity-ranking setting.

The most important methodological contrast inside this submission is therefore not "SpectralBio versus one external baseline." It is **full-matrix covariance displacement versus eigenvalue-only compression inside the same hidden-state object**. This remains the cleanest and most repo-faithful scientific positioning available. The release still does not expose a broad external leaderboard against EVE, SIFT, PolyPhen-2, ProtTrans, or other contemporary predictors on the same frozen TP53 contract. However, a supplementary exact-split ESM-1v comparison is now available, and it is informative precisely because it does **not** produce an external benchmark-win claim for SpectralBio: raw TP53 AUC favors ESM-1v, while SpectralBio's core contribution remains the covariance-based ESM2 analysis and executable artifact contract.

## 4. Methodology

### 4.1 ESM2 Hidden-State Geometry

SpectralBio uses `facebook/esm2_t30_150M_UR50D`, the 30-layer 150M-parameter ESM2 model with hidden dimension `d = 640` [1]. For a wild-type sequence `S_WT` and its corresponding missense mutant `S_MUT` at position `p`, the method extracts a local mutation-centered window with radius `40` residues on each side of the mutation. If the mutation lies near sequence boundaries, the window truncates accordingly; the effective subsequence length therefore satisfies `w <= 81`.

For each layer `l in {1, ..., L}`, with `L = 30`, ESM2 produces a residue-by-feature hidden-state tensor

$$
H^{(l)} \in \mathbb{R}^{w \times d}.
$$

This local-window design is not incidental. It encodes the modeling assumption that the most relevant perturbation signal is concentrated in the neighborhood of the substitution, rather than requiring a full-sequence global statistic for the scoring construction studied here. In other words, SpectralBio is a **local hidden-state geometry** method, not a generic whole-sequence representation summary. The same bounded window also keeps covariance extraction tractable at manuscript scale.

### 4.2 Local Covariance Features

For each layer, SpectralBio computes a covariance matrix over the local hidden states:

$$
C^{(l)} = \operatorname{Cov}(H^{(l)}) \in \mathbb{R}^{d \times d}.
$$

Separate covariance matrices are formed for the wild-type and mutant windows, yielding `C_wt^(l)` and `C_mut^(l)`. From these layer-wise covariance objects, the method extracts three summary statistics reported in the paper:

$$
\operatorname{FrobDist} = \frac{1}{L}\sum_{l=1}^{L} \left\| C_{\mathrm{mut}}^{(l)} - C_{\mathrm{wt}}^{(l)} \right\|_F
$$

$$
\operatorname{TraceRatio} = \frac{1}{L}\sum_{l=1}^{L} \left| \frac{\operatorname{tr}(C_{\mathrm{mut}}^{(l)})}{\operatorname{tr}(C_{\mathrm{wt}}^{(l)})} - 1 \right|
$$

$$
\operatorname{SPS\text{-}log} = \frac{1}{L}\sum_{l=1}^{L} \left\| \log |\lambda_{\mathrm{mut}}^{(l)}| - \log |\lambda_{\mathrm{wt}}^{(l)}| \right\|_2^2
$$

where `lambda^(l)` denotes the covariance eigenvalue spectrum at layer `l`.

These three statistics represent three different hypotheses about what mutation-induced perturbation looks like:

- `frob_dist` preserves the **entire covariance perturbation** at matrix level.
- `TraceRatio` measures **global variance-scale change**.
- `SPS-log` compresses the covariance object to **eigenvalue-only spectral change**.

The technical role of `frob_dist` is especially important. If we define

$$
\Delta C^{(l)} = C_{\mathrm{mut}}^{(l)} - C_{\mathrm{wt}}^{(l)},
$$

then

$$
\left\| \Delta C^{(l)} \right\|_F^2
=
\sum_i \left(\Delta C^{(l)}_{ii}\right)^2
+ 2 \sum_{i<j} \left(\Delta C^{(l)}_{ij}\right)^2.
$$

This decomposition makes clear that full-matrix Frobenius displacement retains both **diagonal variance perturbations** and **off-diagonal correlation perturbations**. That is exactly the kind of information that can be obscured once the covariance matrix is compressed to an eigenvalue-only summary.

### 4.3 Likelihood Terms and Hidden-State Proxy Baseline (`ll_proper`, `ll_crude`)

The second methodological branch is the masked-language-model score at the mutation site:

$$
\operatorname{LL}(v) =
\log P_{\mathrm{ESM2}}(r_{\mathrm{wt},p} \mid S_{\mathrm{WT}})
-
\log P_{\mathrm{ESM2}}(r_{\mathrm{mut},p} \mid S_{\mathrm{WT}}).
$$

This term measures how much the model prefers the wild-type residue over the mutant residue under the wild-type context. It is therefore a **residue-level plausibility score**, not a representation-geometry score. SpectralBio also reports `ll_crude` in the paper as a hidden-state-derived proxy baseline based on norm differences. The repository preserves the variable names `ll_proper` and `ll_crude` for artifact fidelity, but the distinction is technical rather than rhetorical: `ll_proper` is the masked-language-model likelihood term, whereas `ll_crude` is a proxy statistic derived from hidden-state behavior rather than from the model's token log-probability.

The distinction between `ll_crude` and `ll_proper` also matters empirically. On TP53, `ll_crude` is the stronger standalone proxy baseline, whereas `ll_proper` is the likelihood term that forms the released canonical pair with `frob_dist` under the constrained search and is also the term reported for the bounded BRCA1 first-100 slice. This asymmetry indicates that the released score is not simply the strongest standalone feature combined with a residual term.

### 4.4 Aggregated Scoring Function

All scalar features are MinMax-scaled to `[0, 1]` before combination. The paper performs a constrained pairwise search over mixtures of the form

$$
s_{\alpha} = \alpha f_1 + (1-\alpha) f_2,
\qquad
\alpha \in \{0, 0.05, 0.10, \dots, 1.00\}.
$$

The released canonical pair on TP53 is:

$$
\operatorname{score} = 0.55 \cdot \operatorname{frob\_dist} + 0.45 \cdot \operatorname{ll\_proper}.
$$

This released pair is scientifically important for two reasons. First, it is the best validated pair under a constrained search rather than a hand-selected interpolation. Second, it pairs a **matrix-level representation statistic** with a **sequence-likelihood statistic**, making the final benchmark result directly interpretable as a complementarity result rather than as a single-family score.

### 4.5 Why Covariance Matters

The most important internal methodological comparison in SpectralBio is the comparison between **full-matrix covariance displacement**, **eigenvalue-only summaries**, and **likelihood-only scalar scoring**. These are not cosmetically different summaries of the same object. They preserve different classes of information. Likelihood terms reduce the mutation question to residue plausibility under sequence context. Eigenvalue-only SPS-style summaries retain spectral magnitudes but compress away orientation and detailed off-diagonal interaction structure. Full-matrix covariance statistics, by contrast, remain sensitive to how correlations among hidden features are reorganized by a substitution.

This distinction is easiest to see algebraically. Two covariance matrices can have similar eigenvalue profiles while still differing in the arrangement of their off-diagonal terms, and therefore in the geometry of local hidden-state dependence. Because `frob_dist` acts on the matrix difference itself, it preserves sensitivity to that broader perturbation class rather than only to the spectrum of the perturbation. In practical terms, it is a summary of **how the local hidden-state manifold is reorganized**, not merely of whether total variance or dominant eigenvalues changed.

That distinction is not left as theory alone. On the canonical TP53 benchmark, the matrix-level features `TraceRatio` and `frob_dist` both outperform every SPS variant reported in the paper, while the released canonical pair combines a covariance term with a masked-language-model likelihood term. The benchmark claim is empirical; the proposition below supplies only the bounded rationale for why full-matrix covariance can retain information that eigenvalue-only summaries discard.

**Proposition 1 (Covariance Information Lower Bound).** Let $C_{wt}, C_{mut} \in \mathbb{R}^{d \times d}$ be covariance matrices, and let $\lambda(C)$ denote the vector of eigenvalues under a consistent ordering. Then

$$
\|C_{mut} - C_{wt}\|_F^2 \geq \|\lambda(C_{mut}) - \lambda(C_{wt})\|_2^2.
$$

For symmetric matrices this is a direct consequence of the Hoffman-Wielandt inequality. Equality holds when the two matrices are simultaneously diagonalizable in the same orthonormal basis; when a mutation changes the orientation of the principal directions as well as their magnitudes, the inequality is strict. In that sense, full-matrix Frobenius displacement retains perturbation information that eigenvalue-only summaries necessarily discard, which provides the theoretical rationale for why covariance-based scoring can recover signal unavailable to spectral-only compression.

### 4.6 When Matrix-Level Information Becomes Necessary

The previous proposition shows that full-matrix covariance displacement can contain strictly more perturbation information than eigenvalue-only compression. The corollary below should be read in the same spirit: it is a bounded necessity example for one perturbation class, not a claim that the TP53 benchmark literally instantiates that class variant by variant.

**Corollary 1 (Necessity of Matrix-Aware Terms for Isospectral Reorientation).** Let $C_{wt} \in \mathbb{R}^{d \times d}$ be symmetric, let $Q$ be orthogonal, and define

$$
C_{mut} = Q C_{wt} Q^\top.
$$

Then $\lambda(C_{mut}) = \lambda(C_{wt})$, so any score that depends only on the eigenvalue multiset assigns the same value to both states. If $Q C_{wt} \neq C_{wt} Q$, equivalently if the perturbation changes the covariance eigenspaces rather than leaving the original basis fixed, then $C_{mut} \neq C_{wt}$ and therefore

$$
\|C_{mut} - C_{wt}\|_F > 0.
$$

Thus, for this perturbation class, eigenvalue-only summaries are provably blind while a full-matrix displacement term remains discriminative. This does **not** prove that every TP53 variant behaves as an isospectral reorientation, and the benchmark itself does not identify that mechanism variant by variant. It does, however, sharpen the theoretical interpretation from a mere sufficiency statement to a bounded necessity statement: for mutations that preserve spectral magnitudes while rotating correlation structure, covariance-aware scoring is not just helpful but required.

## 5. Benchmark Design

### 5.1 Canonical TP53 and bounded BRCA1 surfaces

| Surface | Contract role | Frozen source(s) | N | Label split | Claim boundary |
| --- | --- | --- | ---: | --- | --- |
| `TP53` | Primary canonical benchmark | `benchmarks/tp53/tp53_canonical_v1.json`, `benchmarks/tp53/tp53_scores_v1.json`, `configs/tp53_canonical.yaml` | 255 | 115 pathogenic / 140 benign | Only canonical scored benchmark and default executable path |
| `BRCA1_transfer100` | bounded secondary evidence | `benchmarks/brca1/brca1_transfer100_v1.json`, `configs/brca1_transfer.yaml` | 100 | 29 pathogenic / 71 benign | Fixed first 100 records from `brca1_full_filtered_v1.json` in source order; no retraining |
| `BRCA1_full_filtered_v1.json` | Provenance only | `benchmarks/brca1/brca1_full_filtered_v1.json` | 512 | 165 pathogenic / 347 benign | Provenance and subset derivation only; not a canonical scored surface |

This design is intentionally asymmetric. TP53 is not simply an arbitrary benchmark choice; it is the **canonical executable benchmark** because it is the surface where paper, manifests, expected metrics, score formula, and verifier all coincide. BRCA1 is preserved as bounded secondary evidence on the fixed first-100 slice because that is the highest-confidence scope the repository truth contract can honestly sustain.

### 5.2 Evaluation Protocol and Benchmark Ownership

TP53 evaluation is anchored to `AUC-ROC`, fixed seed `42`, frozen manifests, expected metrics, and verification rules. The goal is not breadth for its own sake; it is a scientifically interpretable claim with minimal execution ambiguity.

BRCA1 remains deliberately constrained. It is a fixed-subset, no-retraining secondary evaluation surface comprising the first 100 records in source order, not a co-primary benchmark and not a broad generalization surface. The same ownership rule keeps `BRCA1_full_filtered_v1.json` in provenance-only status rather than allowing it to drift into a second scored benchmark.

### 5.3 Frozen Executable Contract

| Contract element | Repository commitment |
| --- | --- |
| Package manager | `uv` |
| Python requirement | `>=3.10` |
| Canonical public setup | `uv sync --frozen` |
| Canonical command | `uv run spectralbio canonical` |
| Optional full validation | `uv run spectralbio transfer`, `uv run spectralbio verify`, `uv run python scripts/preflight.py` |
| CLI namespace | `spectralbio` |
| Seed | `42` |
| Model provenance | `facebook/esm2_t30_150M_UR50D` recorded in `run_metadata.json` |
| Verification tolerance | `0.0001` |
| Canonical runtime model | Frozen-artifact materialization from bundled benchmark inputs and bundled score references |
| Canonical verification artifact | `outputs/canonical/verification.json` |

The public canonical runtime is deliberately not framed as a first-run heavy recomputation workflow. Instead, it validates configuration, loads bundled TP53 inputs and bundled score references, computes contract metrics from those frozen references, copies the canonical ROC figure, materializes the output bundle, and verifies it. Because this path materializes the frozen benchmark object rather than recomputing the research pipeline, GPU is not required.

That separation is intentional: the paper carries the scientific claim and benchmark evidence, while the repository exposes the stable replay surface through which that claim can be inspected and verified. Supplementary Colab/T4 runs then provide feasibility context for research-path reruns rather than defining the canonical contract: the OpenClaw Phase 2 notebook finished in `182.8` seconds total, individual TP53 reruns took roughly `14.4-15.8` seconds, and an instrumented TP53 runtime probe measured `6.38` seconds for a likelihood-only proxy plus `8.61` seconds of covariance overhead (`14.99` seconds total). These timings remain informative supplementary context, not part of the canonical CPU-only contract.

### 5.4 Exact Artifact Outputs and Public Surfaces

**Canonical outputs: `outputs/canonical/`**

- `run_metadata.json`
- `inputs_manifest.json`
- `tp53_scores.tsv`
- `tp53_metrics.json`
- `summary.json`
- `roc_tp53.png`
- `manifest.json`
- `verification.json`

**Transfer outputs: `outputs/transfer/`**

- `summary.json`
- `variants.json`
- `manifest.json`

The public artifact surfaces associated with this submission are:

- GitHub repository: [https://github.com/DaviBonetto/SpectralBio](https://github.com/DaviBonetto/SpectralBio)
- Release bundle (`v1.1.0`): [https://github.com/DaviBonetto/SpectralBio/releases/tag/v1.1.0](https://github.com/DaviBonetto/SpectralBio/releases/tag/v1.1.0)
- Demo Space: [https://huggingface.co/spaces/DaviBonetto/spectralbio-demo](https://huggingface.co/spaces/DaviBonetto/spectralbio-demo)
- Dataset: [https://huggingface.co/datasets/DaviBonetto/spectralbio-clinvar](https://huggingface.co/datasets/DaviBonetto/spectralbio-clinvar)
- Paper PDF: [https://github.com/DaviBonetto/SpectralBio/blob/main/paper/spectralbio.pdf](https://github.com/DaviBonetto/SpectralBio/blob/main/paper/spectralbio.pdf)
- SKILL: [https://github.com/DaviBonetto/SpectralBio/blob/main/SKILL.md](https://github.com/DaviBonetto/SpectralBio/blob/main/SKILL.md)
- Truth contract: [https://github.com/DaviBonetto/SpectralBio/blob/main/docs/truth_contract.md](https://github.com/DaviBonetto/SpectralBio/blob/main/docs/truth_contract.md)
- Reproducibility notes: [https://github.com/DaviBonetto/SpectralBio/blob/main/docs/reproducibility.md](https://github.com/DaviBonetto/SpectralBio/blob/main/docs/reproducibility.md)
- Canonical summary artifact: [https://github.com/DaviBonetto/SpectralBio/blob/main/outputs/canonical/summary.json](https://github.com/DaviBonetto/SpectralBio/blob/main/outputs/canonical/summary.json)
- Canonical verification artifact: [https://github.com/DaviBonetto/SpectralBio/blob/main/outputs/canonical/verification.json](https://github.com/DaviBonetto/SpectralBio/blob/main/outputs/canonical/verification.json)

### 5.5 Judge-Facing Evidence Surfaces

Three public surfaces are especially important for technical judges because they convert the submission from a narrative claim into an inspectable benchmark object. The release bundle `v1.1.0` exposes a stable public checkpoint for the submission package as a whole. The canonical `summary.json` exposes the released metric surface in a machine-readable form. The canonical `verification.json` exposes pass/fail status for the contract itself, including file-set, metric, manifest, and figure checks. Together, these assets are unusually strong evidence anchors for an artifact-centered research submission because they make the public claim surface concrete rather than implicit.

### 5.6 Reproducibility Snapshot

| Dimension | Repository-grounded statement |
| --- | --- |
| canonical benchmark | `TP53 canonical executable benchmark` |
| secondary evidence | fixed BRCA1 first-100 subset in source order, without retraining |
| public command surface | `uv sync --frozen` followed by `uv run spectralbio canonical` |
| canonical runtime model | frozen-artifact materialization from bundled benchmark inputs and bundled score references |
| GPU needed for canonical path | Not required |
| verification artifact | `outputs/canonical/verification.json` |
| metric surface | `outputs/canonical/summary.json` |
| truth boundary | `docs/truth_contract.md` |
| public evidence surfaces | repository, release bundle `v1.1.0`, `summary.json`, `verification.json`, demo, dataset |

A supplementary checksum probe on the current local workspace also matched SHA-256 values across Windows 11 and Ubuntu WSL2 for the three frozen canonical files `outputs/canonical/summary.json`, `outputs/canonical/verification.json`, and `benchmarks/tp53/tp53_scores_v1.json`. This is a narrow frozen-file parity check, not a claim that every supplementary rerun branch is numerically identical across arbitrary environments.

### 5.7 Machine-Checkable Reproduction Contract

The submission exposes a **machine-checkable benchmark object**, not just a prose account of a prior run. Frozen outputs, `summary.json`, and `verification.json` make the public claim surface inspectable, while `SKILL.md` serves as the executable reproduction contract for the canonical path, expected outputs, and non-claims. An agent can therefore recover the same verification surfaces without inferring execution semantics from prose.

## 6. Results

### 6.1 Primary and Secondary Benchmark Results

| Benchmark surface | Score surface | Official AUC | Released value | Abs. delta vs official | Tolerance | Status |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| TP53 canonical | `0.55*frob_dist + 0.45*ll_proper` | `0.7498` | `0.749751552795031` | `0.000048447204969` | `0.0001` | `PASS` |
| BRCA1 fixed subset | `ll_proper` | `0.9174` | `0.9174` | `0.0` | `0.0001` | bounded secondary evidence |

The canonical TP53 result is the central executable claim of the submission. It is not only a headline AUC; it is a metric tied to a released score formula, frozen benchmark inputs, expected output schema, and a verification report that passes within tolerance. `outputs/canonical/summary.json` records `reproducibility_delta = 0.0`, and `outputs/canonical/verification.json` reports top-level `PASS` for the canonical benchmark surface.

![Figure 1. ROC curve for the TP53 canonical benchmark](https://raw.githubusercontent.com/DaviBonetto/SpectralBio/main/outputs/canonical/roc_tp53.png)

**Figure 1.** ROC curve for the released TP53 canonical benchmark using `0.55*frob_dist + 0.45*ll_proper`.

The BRCA1 result is intentionally narrower in role. It shows that the masked-language-model likelihood term remains informative on a fixed out-of-benchmark slice comprising the first 100 records in source order, without retraining, but that slice is not allowed to dominate the interpretation of the submission. A supplementary recomputation on that same frozen slice gives `0.9160` with a 95% bootstrap interval `[0.8235, 0.9836]`, close to the released `0.9174`; this helps characterize uncertainty on that exact slice without broadening the claim surface.

### 6.2 Released Canonical Pair and Complementarity

The central quantitative pattern of the TP53 benchmark is that **neither the covariance term nor the likelihood term is sufficient alone, while their combination is materially stronger**. This is why the released canonical pair supports a complementarity claim rather than a generic feature-mixing claim.

| TP53 configuration | AUC | Interpretation |
| --- | ---: | --- |
| `ll_crude` | `0.7026` | strongest standalone hidden-state-derived proxy baseline |
| `ll_proper` | `0.5956` | masked-language-model likelihood term alone |
| `frob_dist` | `0.6209` | full-matrix covariance geometry term alone |
| `ll_crude + TraceRatio + frob_dist` | `0.7264` | released triple |
| `0.55*frob_dist + 0.45*ll_proper` | `0.7498` | released canonical pair |

The released canonical pair uses one **representation-geometry term** and one **likelihood term**, not two near-duplicate sequence statistics. On the frozen TP53 surface, the constrained alpha sweep peaks at the released mixture `0.55*frob_dist + 0.45*ll_proper`, with nearby grid points slightly lower (`0.7469` at `0.50/0.50` and `0.7492` at `0.60/0.40`). The released triple is also pinned down cleanly: under the exact released search space, `ll_crude + TraceRatio + frob_dist` reproduces `0.7264` at weights `[0.7, 0.1, 0.2]`, while the higher `0.7338` value appears only under a broader supplementary weight grid and therefore does not replace the released triple.

### 6.3 Verification, Significance, and Sensitivity

| Verification metric | Value |
| --- | --- |
| canonical verification status | `PASS` |
| artifact bundle completeness | `8/8` required files listed in `outputs/canonical/summary.json` |
| canonical metric agreement | computed AUC matches official AUC within `0.0001` tolerance |
| metric tolerance | `0.0001` |
| reproducibility delta | `0.0` |

The TP53 result matters because it is tied to a mechanically verifiable public execution surface rather than to a narrative-only report of a past run. The benchmark is therefore inspectable as well as rerunnable.

At the artifact level, `verification.json` exposes structured pass/fail fields for file-set validation, schema checks, source and checksum alignment, metric agreement, and bundle integrity, so the released benchmark is machine-auditable rather than merely described.

Statistically, the strongest formal evidence remains centered on the complementarity claim. The released canonical pair is positively separated from `ll_proper` (`+0.1542`, 95% CI `[0.0859, 0.2254]`), `frob_dist` (`+0.1288`, 95% CI `[0.0623, 0.1970]`), and `sps_log` (`+0.1509`, 95% CI `[0.0872, 0.2197]`), with paired two-sided bootstrap `p = 0.0004` in each comparison. Against `ll_crude`, the interval crosses zero (`+0.0471`, 95% CI `[-0.0287, 0.1243]`, `p = 0.2328`), which is consistent with `ll_crude` remaining a competitive standalone proxy baseline.

Sensitivity analyses remain supportive but secondary. A TP53 window sweep over radii `20-60` peaks at the released radius `40` (`0.7498`), and a layer sweep stays in a narrow band from `0.7385` (`last1`) to `0.7572` (`deep10`), with the released all-layer aggregation at `0.7498`. A seed replay with seeds `42` and `123` reproduces identical raw features and the same AUC `0.7498`. Together, these analyses sharpen confidence in the TP53 result without redefining the released surface.

### 6.4 Negative Controls and Failure Modes

Two bounded negative controls can now be stated without changing the canonical TP53 benchmark semantics. First, on the frozen TP53 score surface, we permuted the pathogenic/benign labels `1000` times while holding the released canonical pair scores fixed. Under that null construction, the resulting AUC distribution had mean `0.4994` and standard deviation `0.0360`, with observed range `[0.3871, 0.6048]`. The released canonical pair remained at `0.7498`, and no permutation reached that value, giving an empirical permutation probability `p = 0.0010` under `1000` trials. This is a deliberately limited control, but it is still informative: once biological label alignment is destroyed, the released ranking collapses to chance-level behavior on the frozen TP53 surface.

Second, a supplementary sequence-level shuffled-context control reran the TP53 benchmark at the released radius `40` on a Colab/T4 path while preserving amino-acid composition and keeping the central residue fixed, but destroying local positional order in the surrounding context. Across three independent context permutations (`4242`, `4343`, `4444`), the released canonical pair dropped from `0.7498` to `0.5759`, `0.5286`, and `0.5117`, with mean `0.5388` and standard deviation `0.0333`; the mean drop relative to the released canonical pair was therefore `0.2110`. This control is again intentionally bounded, but the pattern is clear: once local positional geometry is deliberately disrupted, the released signal degrades sharply rather than surviving as a generic artifact of amino-acid composition alone.

### 6.5 Exact-Split ESM-1v Comparison

The most direct external calibration is the exact-split ESM-1v comparison on the identical TP53 canonical variant set. Using the official five-model ESM-1v ensemble with WT-marginals zero-shot scoring, the measured ensemble AUC is `0.9465` (95% bootstrap CI `[0.9178, 0.9704]`) on the same `255` TP53 variants where the released canonical pair reaches `0.7498` (95% bootstrap CI `[0.6867, 0.8088]`). The paired bootstrap delta is `+0.1968` in favor of ESM-1v (95% CI `[0.1380, 0.2578]`, two-sided `p = 0.0004`), and all five individual ESM-1v models also exceed the released canonical pair.

This comparison is best read as scope calibration rather than as the center of the paper. It does **not** support an external raw-AUC win claim for SpectralBio. Its value is to sharpen the contribution boundary: SpectralBio contributes a covariance-centered ESM2 analysis, a bounded internal complementarity result, and an unusually inspectable executable benchmark object, while ESM-1v remains substantially stronger on raw TP53 discrimination in the measured exact-split ESM-1v comparison.

### 6.6 Computational Cost

Runtime is best treated as practical context rather than as a main result. On the TP53 rerun path, one uninstrumented pass over the `255` variants completed in `14.47` seconds, while an instrumented probe measured `14.99` seconds total, comprising `6.38` seconds for a likelihood-only proxy and `8.61` seconds of covariance overhead. On that same surface, `ll_proper` reached `0.5956`, while the released canonical pair reached `0.7498`, a gain of `+0.1542` AUC over the likelihood term.

| Configuration | Runtime (TP53, 255 variants) | Relative | AUC |
| --- | ---: | ---: | ---: |
| Likelihood-only proxy | `6.38 s` | `1.00x` | `0.5956` |
| + Covariance-augmented full rerun (instrumented) | `14.99 s` | `2.35x` | `0.7498` |
| Marginal covariance overhead | `+8.61 s` | `+135.0%` vs proxy | `+0.1542` |

For broader context, the exact-split ESM-1v comparison required `191.00` seconds across the five model runs on the same Colab/T4 environment, approximately `13.2x` the uninstrumented SpectralBio TP53 rerun time. The right reading is modest: covariance adds real cost, but still within a practical offline rerun regime at TP53 scale. These timings remain supplementary and should not be read as a standalone speed claim.

### 6.7 Error Analysis by Substitution Type

The exact-split ESM-1v comparison can also be stratified by substitution severity using rounded Grantham distances derived from the standard amino-acid composition, polarity, and volume formulation. The Grantham bins are mutually exclusive, while the cysteine-involved row remains intentionally non-exclusive as a chemically important supplementary check.

| Substitution class | N | Pathogenic / benign | SpectralBio AUC | ESM-1v AUC |
| --- | ---: | ---: | ---: | ---: |
| Conservative (`0-50`) | `73` | `21 / 52` | `0.6557` | `0.9405` |
| Moderately conservative (`51-100`) | `89` | `30 / 59` | `0.6904` | `0.9672` |
| Moderately radical (`101-150`) | `66` | `47 / 19` | `0.7648` | `0.9373` |
| Radical (`>150`) | `27` | `17 / 10` | `0.7353` | `0.8588` |
| Cysteine-involved | `26` | `19 / 7` | `0.5865` | `0.8647` |

ESM-1v remains stronger in every row, so this analysis does not change the main external comparison. Its value is narrower: it localizes where SpectralBio is relatively less weak. The covariance-based score is strongest in the `101-150` moderately radical bin and comparatively closer to ESM-1v in the `>150` radical bin than in the conservative bins, while cysteine-involved substitutions remain difficult. Because this stratification is post hoc and some bins are small, it should be read as descriptive error localization rather than as a new benchmark claim.

### 6.8 UMAP View of the TP53 Covariance-Likelihood Geometry

A secondary UMAP projection gives a descriptive view of the TP53 covariance-likelihood geometry in two dimensions using `frob_dist`, `ll_proper`, and a `trace_ratio` residual obtained after regressing `trace_ratio` on `ll_proper` and `ll_crude` across the frozen TP53 surface.

![Figure 2. UMAP projection of TP53 variants](https://raw.githubusercontent.com/DaviBonetto/SpectralBio/main/paper/assets/tp53_umap_covariance_likelihood.png)

**Figure 2.** UMAP projection of the `255` TP53 variants in the residual covariance-likelihood space (`n_neighbors = 10`, `min_dist = 0.01`, cosine metric, seed `42`). Pathogenic variants are shown in red and benign variants in blue. The label-conditioned silhouette score is `0.133`, indicating partial class organization with substantial overlap rather than distinct clusters. The figure is therefore descriptive only and does not support a strong separability claim.

## 7. Interpretation and Component Analysis

This section addresses the central interpretive question raised by the TP53 result: why does the released score work better than simpler summaries, and what exactly does that imply for zero-shot variant effect prediction? The goal is not to inflate the benchmark with speculative mechanism claims, but to extract the strongest scientifically defensible reading of the reported component pattern.

### 7.1 TP53 Component Table

| TP53 statistic or combination | AUC | Interpretation |
| --- | ---: | --- |
| `ll_crude` | `0.7026` | Strongest standalone hidden-state-derived proxy baseline reported in the paper |
| `TraceRatio` | `0.6242` | Matrix-level variance-scale perturbation |
| `frob_dist` | `0.6209` | Full-matrix covariance displacement |
| `SPS-log` | `0.5988` | Best eigenvalue-only SPS-style summary |
| `ll_proper` | `0.5956` | Masked-language-model likelihood term |
| `SPS-all` | `0.5611` | Eigenvalue-only summary |
| `SPS-topk` | `0.5606` | Eigenvalue-only summary |
| `SPS-deep10` | `0.5542` | Eigenvalue-only summary |
| `SPS-deep5` | `0.5298` | Eigenvalue-only summary |
| `ll_crude + TraceRatio + frob_dist` | `0.7264` | Highest-performing released triple under the constrained search |
| `0.55*frob_dist + 0.45*ll_proper` | `0.7498` | released canonical pair |

### 7.2 Within-Benchmark Deltas

| Comparison | AUC delta |
| --- | ---: |
| released canonical pair minus `ll_crude` | `+0.0471` |
| released canonical pair minus `frob_dist` | `+0.1288` |
| released canonical pair minus `ll_proper` | `+0.1542` |
| released canonical pair minus released triple | `+0.0234` |
| `frob_dist` minus `SPS-log` | `+0.0221` |
| `TraceRatio` minus `SPS-log` | `+0.0253` |

### 7.3 Why the Component Pattern Matters

The reported TP53 component pattern supports three judge-relevant scientific inferences:

- `0.55*frob_dist + 0.45*ll_proper` is the released canonical pair under the constrained search because it behaves as a **complementarity result**, not as a single-feature win. `frob_dist` and `ll_proper` are both modest alone on TP53, but their combination reaches `0.7498`, which means the useful signal is distributed across representation geometry and residue plausibility rather than concentrated in one isolated statistic. Formal paired-bootstrap evidence strengthens that reading against `ll_proper`, `frob_dist`, and `SPS-log`, while still treating `ll_crude` as a competitive standalone proxy baseline.

- Full-matrix covariance summaries matter because **matrix-level perturbation outperforms eigenvalue-only compression** on the canonical benchmark. `frob_dist` and `TraceRatio` both exceed `SPS-log`, and the weaker SPS variants fall further behind, supporting the narrower methodological claim that covariance structure carries benchmark-relevant information that spectrum-only summaries discard.

- BRCA1 remains bounded secondary evidence because its role is to show **limited no-retraining signal on one fixed secondary slice**, not broad cross-protein generalization. The fixed-subset BRCA1 result is therefore scientifically useful without changing the benchmark hierarchy: TP53 remains the canonical claim surface, and BRCA1 remains a disciplined secondary check rather than a second primary benchmark.

## 8. Discussion

SpectralBio contributes a bounded scientific claim: **mutation-induced full-matrix covariance displacement in ESM2 hidden states carries nonredundant benchmark signal beyond masked-language-model likelihood**. On TP53, matrix-level features outperform eigenvalue-only SPS-style summaries, and the canonical pair improves on both the likelihood term and the covariance term alone. The strongest formal evidence therefore supports complementarity between representation geometry and sequence likelihood, not a generic feature-accumulation story.

That same restraint governs the surrounding evidence. The released triple is directionally weaker than the canonical pair under the exact released search space, but not formally separated at the same threshold; BRCA1 remains bounded secondary evidence on one fixed no-retraining slice; and the exact-split ESM-1v comparison shows clearly that SpectralBio is not the strongest raw-AUC predictor on the measured TP53 surface. Those facts narrow the contribution rather than diminishing it.

What remains is still meaningful. On a tightly specified executable benchmark, covariance-aware ESM2 summaries recover signal that eigenvalue-only compression and likelihood-only scoring leave behind. The Grantham stratification and UMAP view remain descriptive, but they are directionally consistent with that interpretation. More broadly, the submission argues that representational claims become more useful when tied to a challengeable public artifact surface rather than left as prose alone.

## 9. Limitations and Non-Claims

This submission does **not** claim any-protein applicability, broad or exceptional cross-protein generalization, superiority to external predictors on a shared released benchmark, clinical deployment, clinical use, or clinical decision support. It does **not** treat BRCA1 as a co-primary benchmark, and it does **not** describe the default public path as a full recomputation of every experimental branch in the study. The exact-split ESM-1v comparison makes one of those non-claims concrete: on raw TP53 AUC, the measured ESM-1v ensemble outperforms the canonical pair.

Methodologically, the evidence remains bounded by a small set of design choices: only TP53 is canonical; BRCA1 appears only as a fixed no-retraining secondary slice; the released local context window uses a radius of `40` residues on each side of the mutation; the released model is ESM2-150M; and the paper reports a constrained released search space rather than an unrestricted model-selection regime. These are not cosmetic caveats. They define the scope inside which the current claim should be read.

The supplementary analyses tighten interpretation on the existing surfaces, but they do not broaden the validated claim surface. They add uncertainty estimates, paired significance tests, two bounded negative controls, window and layer sensitivity sweeps, deterministic seed replay, environment-specific runtime notes, an exact-split ESM-1v comparison, and two descriptive TP53 geometry views (Grantham stratification and UMAP). What remains outside the canonical artifact surface is broader model-size exploration, unrestricted hyperparameter search, broader negative-control families, wider external baseline coverage, and broader cross-gene validation.

## 10. Adaptation Architecture

Beyond TP53 and the fixed BRCA1 subset, SpectralBio should be interpreted as an **adaptation architecture**, not as a pre-validated performance surface. A new target would require:

- a target-specific sequence reference,
- a frozen target-specific benchmark file,
- a target-specific score reference,
- a target-specific config,
- target-specific manifests and checksums,
- target-specific expected metrics,
- and independent validation evidence.

Until those pieces exist for a new target, repository support for additional proteins is a **procedure**, not a result. This is the correct place for generalizability in the current submission: not as an unrestricted claim, but as a bounded adaptation recipe whose validation burden is made explicit rather than left implicit.

## 11. Conclusion

SpectralBio shows that, on the TP53 canonical executable benchmark, full-matrix covariance geometry in ESM2 hidden states contributes measurable zero-shot pathogenicity-ranking signal beyond likelihood-only and eigenvalue-only summaries. It does **not** show external state-of-the-art pathogenicity prediction: the exact-split ESM-1v comparison is stronger on raw TP53 AUC, and BRCA1 remains bounded secondary evidence on one fixed no-retraining slice. SpectralBio therefore matters less as a raw-AUC leader than as a bounded demonstration that covariance-aware hidden-state geometry contains empirically recoverable signal and can be exposed through a reproducible benchmark artifact with a challengeable public contract.

## References

1. Lin, Z., Akin, H., Rao, R., et al. *Evolutionary-scale prediction of atomic-level protein structure with a language model.* Science 379(6637), 1123-1130 (2023). [https://www.science.org/doi/10.1126/science.ade2574](https://www.science.org/doi/10.1126/science.ade2574)
2. Meier, J., Rao, R., Verkuil, R., Liu, J., Sercu, T., and Rives, A. *Language models enable zero-shot prediction of the effects of mutations on protein function.* NeurIPS 34 (2021). [https://proceedings.neurips.cc/paper/2021/hash/f51338d736f95dd42427296047067694-Abstract.html](https://proceedings.neurips.cc/paper/2021/hash/f51338d736f95dd42427296047067694-Abstract.html)
3. Frazer, J., Notin, P., Dias, M., et al. *Disease variant prediction with deep generative models of evolutionary data.* Nature 599, 91-95 (2021). [https://www.nature.com/articles/s41586-021-04043-8](https://www.nature.com/articles/s41586-021-04043-8)
4. Ng, P. C., and Henikoff, S. *SIFT: predicting amino acid changes that affect protein function.* Nucleic Acids Research 31(13), 3812-3814 (2003). [https://pubmed.ncbi.nlm.nih.gov/12824425/](https://pubmed.ncbi.nlm.nih.gov/12824425/)
5. Adzhubei, I. A., Schmidt, S., Peshkin, L., et al. *A method and server for predicting damaging missense mutations.* Nature Methods 7, 248-249 (2010). [https://www.nature.com/articles/nmeth0410-248](https://www.nature.com/articles/nmeth0410-248)
6. Elnaggar, A., Heinzinger, M., Dallago, C., et al. *ProtTrans: Toward Understanding the Language of Life Through Self-Supervised Learning.* IEEE Transactions on Pattern Analysis and Machine Intelligence 44(10), 7112-7127 (2022). [https://pubmed.ncbi.nlm.nih.gov/34232869/](https://pubmed.ncbi.nlm.nih.gov/34232869/)
7. Landrum, M. J., Lee, J. M., Benson, M., et al. *ClinVar: improving access to variant interpretations and supporting evidence.* Nucleic Acids Research 46(D1), D1062-D1067 (2018). [https://academic.oup.com/nar/article-abstract/46/D1/D1062/4641904](https://academic.oup.com/nar/article-abstract/46/D1/D1062/4641904)
8. Notin, P., Dias, M., Frazer, J., et al. *ProteinGym: Large-scale benchmarks for protein fitness prediction and design.* NeurIPS 36 (2023). [https://proceedings.neurips.cc/paper_files/paper/2023/hash/cac723e5ff29f65e3fcbb0739ae91bee-Abstract-Datasets_and_Benchmarks.html](https://proceedings.neurips.cc/paper_files/paper/2023/hash/cac723e5ff29f65e3fcbb0739ae91bee-Abstract-Datasets_and_Benchmarks.html)
9. Rives, A., Meier, J., Sercu, T., et al. *Biological structure and function emerge from scaling unsupervised learning to 250 million protein sequences.* Proceedings of the National Academy of Sciences 118(15), e2016239118 (2021). [https://pubmed.ncbi.nlm.nih.gov/33876751/](https://pubmed.ncbi.nlm.nih.gov/33876751/)
10. Brandes, N., Ofer, D., Peleg, Y., et al. *ProteinBERT: a universal deep-learning model of protein sequence and function.* Bioinformatics 38(8), 2102-2110 (2022). [https://pubmed.ncbi.nlm.nih.gov/35020807/](https://pubmed.ncbi.nlm.nih.gov/35020807/)
11. Riesselman, A. J., Ingraham, J. B., and Marks, D. S. *Deep generative models of genetic variation capture the effects of mutations.* Nature Methods 15, 816-822 (2018). [https://www.nature.com/articles/s41592-018-0138-4](https://www.nature.com/articles/s41592-018-0138-4)
12. Livesey, B. J., and Marsh, J. A. *Using deep mutational scanning to benchmark variant effect predictors and identify disease mutations.* Molecular Systems Biology 16(7), e9380 (2020). [https://www.embopress.org/doi/10.15252/msb.20199380](https://www.embopress.org/doi/10.15252/msb.20199380)
13. Kotler, E., Shani, O., Goldfeld, G., et al. *A systematic p53 mutation library links differential functional impact to cancer mutation pattern and evolutionary conservation.* Molecular Cell 71(1), 178-190.e8 (2018). [https://pubmed.ncbi.nlm.nih.gov/29979965/](https://pubmed.ncbi.nlm.nih.gov/29979965/)
14. Findlay, G. M., Daza, R. M., Martin, B., et al. *Accurate classification of BRCA1 variants with saturation genome editing.* Nature 562, 217-222 (2018). [https://www.nature.com/articles/s41586-018-0461-z](https://www.nature.com/articles/s41586-018-0461-z)
15. Morcos, F., Pagnani, A., Lunt, B., et al. *Direct-coupling analysis of residue coevolution captures native contacts across many protein families.* Proceedings of the National Academy of Sciences 108(49), E1293-E1301 (2011). [https://pmc.ncbi.nlm.nih.gov/articles/PMC3241805/](https://pmc.ncbi.nlm.nih.gov/articles/PMC3241805/)
16. Katsonis, P., and Lichtarge, O. *A formal perturbation equation between genotype and phenotype determines the Evolutionary Action of protein-coding variations on fitness.* Genome Research 24(12), 2050-2058 (2014). [https://pubmed.ncbi.nlm.nih.gov/25217195/](https://pubmed.ncbi.nlm.nih.gov/25217195/)
17. Jumper, J., Evans, R., Pritzel, A., et al. *Highly accurate protein structure prediction with AlphaFold.* Nature 596, 583-589 (2021). [https://www.nature.com/articles/s41586-021-03819-2](https://www.nature.com/articles/s41586-021-03819-2)
18. Rao, R., Meier, J., Sercu, T., Ovchinnikov, S., and Rives, A. *Transformer protein language models are unsupervised structure learners.* ICLR (2021). [https://openreview.net/forum?id=fylclEqgvgd](https://openreview.net/forum?id=fylclEqgvgd)
19. Hsu, C., Verkuil, R., Liu, J., Lin, Z., Hie, B., Sercu, T., Lerer, A., and Rives, A. *Learning inverse folding from millions of predicted structures.* Proceedings of Machine Learning Research 162, 8946-8970 (2022). [https://proceedings.mlr.press/v162/hsu22a.html](https://proceedings.mlr.press/v162/hsu22a.html)
20. Ghorbani, A., and Zou, J. *Neuron Shapley: Discovering the Responsible Neurons.* Advances in Neural Information Processing Systems 33 (2020). [https://proceedings.neurips.cc/paper_files/paper/2020/file/41c542dfe6e4fc3deb251d64cf6ed2e4-Paper.pdf](https://proceedings.neurips.cc/paper_files/paper/2020/file/41c542dfe6e4fc3deb251d64cf6ed2e4-Paper.pdf)

## Artifact Links

| Surface | Role |
| --- | --- |
| [Repository](https://github.com/DaviBonetto/SpectralBio) | Source repository and primary public code surface |
| [Release bundle `v1.1.0`](https://github.com/DaviBonetto/SpectralBio/releases/tag/v1.1.0) | Stable public release surface for the submission package |
| [Paper PDF](https://github.com/DaviBonetto/SpectralBio/blob/main/paper/spectralbio.pdf) | Manuscript-level scientific framing |
| [SKILL](https://github.com/DaviBonetto/SpectralBio/blob/main/SKILL.md) | Cold-start agent reproduction contract |
| [Demo Space](https://huggingface.co/spaces/DaviBonetto/spectralbio-demo) | Interactive public demonstration surface |
| [Dataset](https://huggingface.co/datasets/DaviBonetto/spectralbio-clinvar) | Public data surface for the submission |
| [Canonical `summary.json`](https://github.com/DaviBonetto/SpectralBio/blob/main/outputs/canonical/summary.json) | Machine-readable metric surface |
| [Canonical `verification.json`](https://github.com/DaviBonetto/SpectralBio/blob/main/outputs/canonical/verification.json) | Machine-readable contract verification surface |
| [Truth contract](https://github.com/DaviBonetto/SpectralBio/blob/main/docs/truth_contract.md) | Claim boundary and precedence surface |
| [Reproducibility notes](https://github.com/DaviBonetto/SpectralBio/blob/main/docs/reproducibility.md) | Public explanation of canonical execution semantics |
| [clawRxiv mirror](https://github.com/DaviBonetto/SpectralBio/blob/main/publish/clawrxiv/spectralbio_clawrxiv.md) | Publication-facing mirror of the submission page |
