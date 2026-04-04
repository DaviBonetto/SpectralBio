# SpectralBio: Covariance-Aware Hidden-State Geometry Adds Recoverable Zero-Shot Pathogenicity Signal Beyond Likelihood

## 1. Introduction

Missense variant interpretation remains bottlenecked by the gap between variant discovery and experimental characterization. Sequencing keeps producing variants of uncertain significance much faster than carefully curated pathogenic and benign labels can accumulate, and that imbalance is especially severe outside a small number of intensively studied genes. Zero-shot variant effect prediction is attractive in that regime because it can rank substitutions from sequence context alone, without per-gene supervised retraining. Protein language models have made that setting increasingly plausible, from early large-scale unsupervised protein sequence modeling to ESM-family systems that expose informative mutation-effect signal through masked-language-model likelihoods and related sequence-centered summaries [1,2,6,9,10].

Most zero-shot missense scoring arguments, however, remain output-centric. Classical predictors such as SIFT and PolyPhen-2 emphasize conservation and substitution heuristics [4,5]. Evolutionary latent-variable models such as EVE and DeepSequence use family-level sequence variation and deep generative priors [3,11]. Modern protein language model approaches, including ESM-1v zero-shot scoring in the style of Meier et al. [2], show that residue likelihood alone can already be highly informative. Those methods are the correct starting point for SpectralBio, because they define the dominant intuition that mutation effect is primarily a scalar plausibility problem.

SpectralBio asks whether that intuition is incomplete. A missense substitution may be only moderately surprising at the token level while still inducing a substantial local reorganization of the model's hidden-state geometry. The central scientific question of this paper is therefore whether local full-matrix covariance perturbations of ESM2 hidden states contain benchmark-relevant signal that is not exhausted by likelihood-only and eigenvalue-only summaries. The paper's central empirical test is the strongest-baseline version of that question: on BRCA2, does covariance still add signal after the baseline is upgraded from ESM2 likelihood to a five-model ESM-1v ensemble? In this study it does. Adding covariance-aware hidden-state geometry improves BRCA2 AUC from `0.6324` to `0.6890`, and that gain disappears under covariance permutation with empirical `p = 0.0010`.

TP53 then tests whether the underlying covariance signal is real or merely a same-surface tuning spike. The support-ranked top-25 feasible panel tests whether the BRCA2 result sits inside a broader performance-blind pattern rather than a hand-picked companion set. The 192-configuration protocol sweep and the BRCA1 failure analysis define where the method breaks, how checkpoint and protocol choices matter, and which negative cases remain scientifically informative.

SpectralBio is therefore presented as a bounded representational result rather than as a universally superior pathogenicity predictor, a clinical deployment recipe, or a state-of-the-art replacement for stronger external baselines. BRCA2 shows that covariance can add signal on top of a stronger external baseline, TP53 shows that the effect is real and auditable on an owned canonical benchmark, the support-ranked top-25 panel shows that the paper is not built from favorable hand-selection, and the protocol sweep together with BRCA1 shows that the phenomenon is structured rather than universal.

### 1.1 Key Findings

The first key finding is the flagship result of the paper. On BRCA2, adding covariance to ESM-1v improves AUC from `0.6324` to `0.6890`, with paired bootstrap confidence interval `[0.0131, 0.1063]`, and the gain disappears when covariance alignment is permuted. That is the clearest direct evidence in the manuscript that covariance is contributing real pathogenicity-ranking signal rather than merely re-expressing baseline behavior.

The second key finding is that TP53 validates the phenomenon rather than carrying the entire paper alone. On the canonical TP53 benchmark, the released pair remains substantially better than either branch alone, and repeated nested cross-validation places the released alpha on a stable out-of-fold plateau rather than revealing a fragile same-surface optimum. TP53 therefore answers the simplest overfitting criticism without forcing the manuscript back into a TP53-only story.

The third key finding is that the breadth surface is no longer hand-built. On the support-ranked top-25 feasible panel, 10 genes show positive pair-vs-likelihood lower confidence bounds, 2 genes are clearly negative, and the remainder are ambiguous. That is a stronger result than an all-positive companion panel because it shows structured heterogeneity on a performance-blind surface derived from a 15,752-gene scan.

The fourth key finding is that the negative and boundary cases are now interpretable. The 192-configuration sweep shows that covariance utility is checkpoint-, window-, and layer-sensitive rather than a simple small-model artifact, while BRCA1 remains a structured failure case rather than a hidden contradiction. Together those analyses turn the method's hard cases into boundary conditions.

### 1.2 Claim Boundary

The claim boundary remains deliberately bounded. SpectralBio is not presented as a state-of-the-art pathogenicity predictor, a broad cross-protein deployment recipe, or a clinically actionable tool. ESM-1v remains stronger than the released SpectralBio TP53 surface on raw TP53 discrimination, and TP53 remains the only frozen public canonical benchmark at the time of writing. What the present evidence supports is a narrower representational result: covariance-aware hidden-state geometry contributes real, falsifiable, benchmark-relevant signal; on BRCA2 it can improve a stronger external zero-shot baseline; on TP53 it survives nested validation and executable-audit scrutiny; on a support-ranked top-25 panel it appears on a performance-blind breadth surface with mixed outcomes; and under checkpoint and protocol perturbation it behaves as a structured, bounded phenomenon rather than as a universal law.

## 2. Scientific Context and Motivation

Zero-shot missense scoring is attractive precisely because it avoids per-gene supervised retraining, but most current methods still reduce the problem to a scalar token-preference question. In that framing, the key quantity is how strongly the model prefers the wild-type residue over the mutant residue in the surrounding sequence context. That framing is useful and often competitive, yet it may omit a second class of information: a mutation can preserve moderate token plausibility while still reorganizing the local geometry of the hidden representation field.

This is where SpectralBio departs from likelihood-only reasoning. Instead of treating ESM2 only as a conditional scorer, it treats the model as a layered geometric object whose local hidden states carry covariance structure. The manuscript does not argue that every covariance statistic is automatically useful, nor that larger checkpoints necessarily make covariance irrelevant. The narrower hypothesis is that local full-matrix covariance displacement can preserve perturbation information that scalar likelihood summaries and eigenvalue-only compressions do not fully retain. That hypothesis is compatible with the broader observation that protein language models learn structural regularities [1,18,19], but it is tested here in the specific setting of zero-shot pathogenicity ranking rather than in structure prediction or inverse folding.

These comparisons place the stronger-baseline BRCA2 question at the center of the study, with TP53 providing canonical validation, the support-ranked panel providing performance-blind breadth, benchmark qualification defining the release path, and the protocol plus BRCA1 analyses defining boundary conditions. The replay contract remains important because it makes the validation anchor challengeable.

The exact-split ESM-1v comparison still shows that SpectralBio does not win on raw TP53 discrimination, even after additional supplementary checkpoints are considered. The paper therefore is not a state-of-the-art pathogenicity paper. Its contribution is representational and methodological: it shows that covariance-aware hidden-state geometry can survive a stronger-baseline comparison on BRCA2, that the underlying effect is real and auditable on TP53, that it extends beyond the anchor gene on a support-ranked surface with mixed outcomes, and that its behavior under scale is heterogeneous rather than trivially monotone.

## 3. Related Work

The most relevant prior work for SpectralBio falls into four method families. The first family comprises classical missense effect predictors such as SIFT and PolyPhen-2, which use conservation, substitution patterns, and hand-designed biological features [4,5]. These systems established the practical importance of sequence-based pathogenicity scoring, but they do not interrogate learned internal geometry because they predate modern protein language models.

The second family comprises family-aware evolutionary generative models such as EVE and DeepSequence [3,11]. These methods learn family-level latent models of tolerated variation and have been highly influential in disease variant prediction. SpectralBio is conceptually different: it studies local perturbation geometry in a pretrained protein language model rather than a family-specific generative model, and it does so in a zero-shot setting without family retraining in the released benchmark artifact.

The third family comprises protein language model zero-shot mutation scoring. The ESM-family line represented by Meier et al. [2] demonstrated that language-model-based zero-shot inference can capture mutation effects without supervised fine-tuning. ESM2 established stronger protein representation learning at scale [1], while ProtTrans broadened the view that self-supervised protein language modeling is a viable framework for downstream biological prediction [6]. Closely related work also showed that transformer protein language models encode structural information [18] and that inverse-folding models can leverage learned protein representations at scale [19]. SpectralBio is closest to this family, but departs from it by treating the model not only as a sequence-likelihood oracle but also as a source of layer-wise hidden-state geometry.

The fourth family concerns benchmark culture and gene-resolved functional evidence. ClinVar provides the pathogenic and benign label substrate used here [7]. ProteinGym represents the broader field-level emphasis on explicit, comparable benchmark surfaces [8]. Functional studies of TP53 and BRCA1 reinforce why those genes remain scientifically meaningful evaluation surfaces even when a study does not claim broad cross-protein generalization [13,14]. SpectralBio's methodological stance is aligned with that benchmarking culture: it prefers a bounded, falsifiable claim on clearly owned surfaces over a vague generalization claim spanning many incomparable sources.

At a deeper conceptual level, SpectralBio also sits in a longer line of work on dependency structure and internal representations. Direct-coupling analysis showed that pairwise statistical structure in protein sequences can encode functionally relevant information [15]. Evolutionary Action argued that mutation effect depends on context-sensitive functional displacement rather than a single surprise score [16]. More generally, work such as Neuron Shapley illustrates the value of interrogating internal model components rather than only surface outputs [20]. SpectralBio's narrower move is to ask whether mutation-induced covariance perturbation is a useful internal summary for zero-shot missense pathogenicity ranking, and whether that contribution survives direct comparison to stronger baselines and stronger protocol controls.

## 4. Methodology

### 4.1 ESM2 Hidden-State Geometry

SpectralBio uses `facebook/esm2_t30_150M_UR50D`, the 30-layer 150M-parameter ESM2 checkpoint with hidden dimension `d = 640` [1], as the public canonical backbone. Supplementary analyses additionally probe `facebook/esm2_t33_650M_UR50D` and `facebook/esm2_t36_3B_UR50D`. For a wild-type sequence `S_WT` and its corresponding missense mutant `S_MUT` at position `p`, the method extracts a mutation-centered local window. The public canonical benchmark uses radius 40 residues on each side. The protocol sweep later tests radii `20`, `40`, `80`, and `120`. Near sequence boundaries, the window truncates accordingly.

For each layer `l in {1, ..., L}`, ESM2 produces a residue-by-feature hidden-state tensor

$$
H^{(l)} \in \mathbb{R}^{w \times d}.
$$

This local-window design is substantive rather than incidental. The method assumes that the most relevant perturbation signal is concentrated around the mutated site, so SpectralBio is a local hidden-state geometry method rather than a whole-sequence summary.

### 4.2 Local Covariance Features and Likelihood Terms

For each layer, SpectralBio computes a covariance matrix over the local hidden states,

$$
C^{(l)} = \operatorname{Cov}(H^{(l)}) \in \mathbb{R}^{d \times d},
$$

and then constructs separate covariance objects for the wild-type and mutant windows, `C_wt^(l)` and `C_mut^(l)`. From these layer-wise covariance matrices, the manuscript focuses on three statistics:

$$
\operatorname{FrobDist} = \frac{1}{L}\sum_{l=1}^{L} \left\| C_{\mathrm{mut}}^{(l)} - C_{\mathrm{wt}}^{(l)} \right\|_F
$$

$$
\operatorname{TraceRatio} = \frac{1}{L}\sum_{l=1}^{L} \left| \frac{\operatorname{tr}(C_{\mathrm{mut}}^{(l)})}{\operatorname{tr}(C_{\mathrm{wt}}^{(l)})} - 1 \right|
$$

$$
\operatorname{SPS\text{-}log} = \frac{1}{L}\sum_{l=1}^{L} \left\| \log |\lambda_{\mathrm{mut}}^{(l)}| - \log |\lambda_{\mathrm{wt}}^{(l)}| \right\|_2^2,
$$

where `lambda^(l)` denotes the covariance eigenvalue spectrum at layer `l`. These statistics correspond to different perturbation hypotheses. `frob_dist` acts on the full covariance difference and is sensitive to both diagonal variance shifts and off-diagonal correlation reorganization. `TraceRatio` measures variance-scale change. `SPS-log` is an eigenvalue-only compression.

The likelihood branch uses the masked-language-model term

$$
\operatorname{LL}(v) =
\log P_{\mathrm{ESM2}}(r_{\mathrm{wt},p} \mid S_{\mathrm{WT}})
-
\log P_{\mathrm{ESM2}}(r_{\mathrm{mut},p} \mid S_{\mathrm{WT}}).
$$

This is the repository's `ll_proper` score. The public canonical TP53 pair is

$$
\operatorname{score} = 0.55 \cdot \operatorname{frob\_dist} + 0.45 \cdot \operatorname{ll\_proper}.
$$

Supplementary analyses preserve the same ingredients while varying checkpoint, window radius, layer protocol, and baseline branch. In particular, the ESM-1v augmentation study replaces the ESM2 likelihood branch with a five-model ESM-1v ensemble score and asks whether covariance still contributes useful information.

### 4.3 Why Full-Matrix Covariance Can Matter

The key methodological contrast is not "SpectralBio versus one external baseline" but full-matrix covariance displacement versus eigenvalue-only compression within the same hidden-state object. These summaries preserve different classes of information. Likelihood terms reduce the mutation question to residue plausibility under sequence context. Eigenvalue-only summaries preserve spectral magnitudes but compress away orientation and detailed off-diagonal interaction structure. Full-matrix covariance statistics remain sensitive to how correlations among hidden features are reorganized by a substitution.

If we define

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

This decomposition makes clear that full-matrix Frobenius displacement retains both diagonal variance perturbations and off-diagonal correlation perturbations.

**Proposition 1 (Covariance Information Lower Bound).** Let `C_wt, C_mut in R^{d x d}` be covariance matrices, and let `lambda(C)` denote the vector of eigenvalues under a consistent ordering. Then

$$
\|C_{mut} - C_{wt}\|_F^2 \geq \|\lambda(C_{mut}) - \lambda(C_{wt})\|_2^2.
$$

For symmetric matrices this is a direct consequence of the Hoffman-Wielandt inequality. Equality holds when the two matrices are simultaneously diagonalizable in the same orthonormal basis; when a mutation changes eigenspace orientation as well as eigenvalue magnitudes, the inequality is strict. In that sense, full-matrix Frobenius displacement can retain perturbation information that eigenvalue-only summaries discard.

**Corollary 1 (Necessity of Matrix-Aware Terms for Isospectral Reorientation).** Let `C_wt in R^{d x d}` be symmetric, let `Q` be orthogonal, and define

$$
C_{mut} = Q C_{wt} Q^\top.
$$

Then `lambda(C_mut) = lambda(C_wt)`, so any score that depends only on the eigenvalue multiset assigns the same value to both states. If `Q C_wt != C_wt Q`, then `C_mut != C_wt` and therefore

$$
\|C_{mut} - C_{wt}\|_F > 0.
$$

Thus, for this perturbation class, eigenvalue-only summaries are blind while a full-matrix displacement term remains discriminative. The manuscript does not claim that every pathogenic variant is literally an isospectral reorientation. The result is instead a bounded rationale for why full-matrix covariance can capture a perturbation class that spectral-only summaries necessarily miss.

### 4.4 Validation Program and Claim Hierarchy

The evidence program is defined by question class rather than by post hoc selection of favorable analyses. BRCA2 ESM-1v augmentation plus permutation audit is the strongest-baseline test of whether covariance contributes anything nontrivial. TP53 is the validation anchor, examined on the frozen canonical benchmark and then re-audited under repeated nested cross-validation. The anti-cherry-picking breadth surface begins from a global ClinVar support scan over 15,752 genes and applies thresholds `min_total = 60` and `min_per_class = 20`, yielding 446 genes that pass the scan stage before support-ranked feasible selection into the realized top-25 panel.

The benchmark-extension rule is also explicit. A non-anchor gene qualifies as the next canonicalization target only if its paired pair-vs-likelihood bootstrap lower confidence bound is positive and its nested fixed-`0.55` mean AUC exceeds its nested likelihood-only mean AUC. Under that rule, BRCA2 qualifies. The protocol criticism is addressed through a bounded but direct sweep over 4 genes, 3 checkpoints, 4 window radii, 4 layer protocols, and 3 alpha-handling modes, for 192 scored configurations. The negative-case criticism is addressed through a dedicated BRCA1 failure analysis that asks whether the most visible hard case is uniformly negative or structurally mixed.

These surfaces answer different evidentiary questions. BRCA2 carries the strongest claim that covariance can add signal to a stronger external baseline. TP53 shows that the underlying covariance signal is real and not a same-surface tuning accident. The support-ranked top-25 panel shows that the paper is not built from favorable hand-selection. The protocol sweep and BRCA1 analysis define the boundaries of the current method.

### 4.5 Statistical Procedures, Panel Construction, and Augmentation Protocol

Unless otherwise noted, all bootstrap intervals in the manuscript use `1000` nonparametric resamples with seed `42`. AUC intervals are computed from resampled score vectors on the same benchmark surface. Pair-vs-baseline intervals use paired bootstrap resampling of the same variant indices for both scores, so the reported delta intervals are paired rather than independent. Resamples containing only one class are discarded, and the reported interval is the empirical `2.5`th to `97.5`th percentile over valid resamples. The TP53 and BRCA2 nested audits use `5 x 5` repeated stratified cross-validation. Repeat seeds are `42` through `46`, outer folds are stratified with those repeat seeds, and each inner alpha search uses the repeat seed plus the fold index.

MinMax scaling is fit separately for each score family. On a fixed evaluation surface, `frob_dist`, `ll_proper`, and, where used, the ESM-1v ensemble mean are each independently scaled to `[0, 1]` using minima and maxima from that same scored table before pair construction. In nested cross-validation, the minima and maxima are fit on the training folds only and then applied to the held-out fold, so held-out values do not influence scaling. The fixed public pair remains `0.55*frob_dist + 0.45*ll_proper`, and all exploratory alpha sweeps use the grid `0.00, 0.05, ..., 1.00`.

The support-ranked panel is built in two stages. First, genes are ranked by descending `min(n_positive, n_negative)`, then descending `n_total`, then ascending gene symbol after ClinVar filtering to `GRCh38`, single-nucleotide variants, germline-or-empty origin, binary pathogenic/benign labels, and simple missense protein changes. Second, ranked genes enter the realized panel only if they are feasible, meaning that the run can retrieve a reviewed human UniProt sequence, map retained ClinVar missense rows against that sequence, discard out-of-range and sequence-mismatched entries, and still preserve enough binary rows to score the gene. The panel-expansion run fixed `top_k_requested = 25` and realized all `25` genes, so the panel size reflects the target supplementary surface rather than post hoc stopping on favorable results.

The ESM-1v augmentation protocol keeps the covariance branch on the canonical ESM2-150M reference backbone and replaces the baseline branch with the normalized mean zero-shot likelihood from the five-model ESM-1v ensemble `facebook/esm1v_t33_650M_UR90S_{1..5}`. The fixed augmented score is therefore `0.55*frob_norm + 0.45*esm1v_norm`, and the exploratory full-surface alpha sweep again uses the `0.05` grid. The permutation audit uses `1000` replicates with seed `42` while holding labels fixed: one null permutes covariance alignment against ESM-1v, and the other permutes ESM-1v alignment against covariance. The empirical tail probability is reported as `(count(delta_null >= delta_observed) + 1) / (B + 1)`.

## 5. Benchmark Design and Evidence Surfaces

### 5.1 Evidence Hierarchy and Role Assignment

The evidence surfaces in this study are not inferentially interchangeable. The strongest single result is the BRCA2 augmentation audit against ESM-1v, and the remaining surfaces test whether that result is real, bounded, and non-accidental. Table 1 summarizes the evidence program from the strongest-baseline test through validation, breadth, and boundary analyses.

| Surface | Role | Scale | Main result | Interpretation | Claim status |
| --- | --- | ---: | --- | --- | --- |
| ESM-1v augmentation audit | flagship stronger-baseline test | 4 genes | BRCA2 improves from `0.6324` to `0.6890` with CI `[0.0131, 0.1063]` | Covariance can add signal on top of a stronger external baseline | Flagship claim |
| ESM-1v augmentation permutation audit | flagship falsification test | TP53 and BRCA2 | BRCA2 gain disappears when covariance alignment is permuted | Observed BRCA2 gain is not a generic metric artifact | Flagship falsification |
| TP53 canonical benchmark | canonical validation anchor | 255 variants | `0.55*frob_dist + 0.45*ll_proper = 0.7498` | Covariance-likelihood complementarity on the owned benchmark surface | Validation anchor |
| TP53 nested CV leakage audit | anti-leakage validation | 25 outer folds | fixed `0.55` mean AUC `0.7510`; tuned mean AUC `0.7485` | Released alpha behaves as a stable plateau rather than a fragile spike | Strengthens validation anchor |
| BRCA2 benchmark-candidate audit | benchmark-extension evidence | `N = 658` plus nested CV | fixed `0.55` mean AUC `0.7448` versus likelihood `0.6938`; candidate qualifies | Positions BRCA2 as the next canonicalization target under the stated rule | Benchmark-extension evidence |
| Global ClinVar support scan | supplementary provenance scan | 15,752 genes seen; 446 pass thresholds | Performance-blind support ranking under predeclared rules | Replaces hand-picked breadth with auditable panel provenance | Evidence provenance |
| Support-ranked top-25 panel | anti-cherry-picking breadth surface | 10,992 variants across 25 genes | 10 genes with positive lower bounds; 2 clearly negative; 13 ambiguous | Shows the paper is not built from favorable hand-selection and that breadth is heterogeneous | Breadth evidence |
| `150M/650M/3B` protocol sweep | checkpoint and protocol boundary analysis | 192 configurations | Small-window and shallow-layer protocols matter; effects are checkpoint-sensitive but persistent | Rejects the simplistic "just a 150M artifact" critique while defining sensitivity | Boundary evidence |
| BRCA1 failure analysis | hard-negative boundary case | 512 variants across domain and confidence strata | Negativity is not uniform; some domains are near-neutral or slightly positive | Replaces a blanket failure story with structured heterogeneity | Boundary evidence |
| TP53 label permutation and context shuffle | generic falsification controls | TP53 | Null behavior near chance and strong context dependence | Signal depends on label alignment and local geometry | Falsification support |

### 5.2 Challenge-to-Evidence Map

Table 2 maps the main scientific challenges to the corresponding evidence layers used here.

| Scientific challenge | New evidence | Main result | Claim impact |
| --- | --- | --- | --- |
| Covariance may only beat a weak ESM2 likelihood branch | ESM-1v augmentation plus permutation audit | BRCA2 gain `+0.0566` over ESM-1v with positive CI; gain disappears under covariance permutation | Provides the clearest stronger-baseline test and direct falsification |
| `0.55/0.45` may be same-surface overfit | Repeated nested cross-validation on TP53 | fixed `0.55` mean AUC `0.7510`; tuned mean AUC `0.7485` | Directly addresses leakage criticism on the public anchor surface |
| Supplementary panel may be cherry-picked | Global support scan plus support-ranked top-25 panel | 15,752 genes screened, 446 passing thresholds, 10,992 scored variants | Broadens the evidence beyond TP53 on a performance-blind surface |
| BRCA2 is only a favorable example, not a real next benchmark | Dedicated BRCA2 canonicalization audit | fixed `0.55` mean AUC `0.7448` versus likelihood `0.6938`; candidate qualifies | Converts a favorable example into a concrete release path |
| 650M is not enough to answer scaling objections | 192-configuration checkpoint/window/layer sweep | TP53 and BRCA2 remain positive under multiple checkpoints; BRCA1 is protocol-sensitive rather than uniformly null | Turns the scaling objection into a measured robustness result |
| BRCA1 negative transfer undermines the method | BRCA1 domain/confidence/review-status failure analysis | Negativity concentrates in specific strata; BRCT2 and RING are near-neutral to slightly positive | Replaces an undifferentiated failure story with interpretable structure |
| Paper overstates itself relative to external baselines | Exact-split ESM-1v calibration retained | TP53 ESM-1v still stronger than the released TP53 pair | Forces honest positioning while preserving stronger BRCA2 claims |

### 5.3 Support-Ranked Selection and Benchmark Extension

The supplementary panel begins from a global ClinVar scan, applies explicit support thresholds, and then uses a support-ranked feasibility filter to decide which non-anchor genes are actually scored. Support-ranked means descending `min(n_positive, n_negative)`, then descending `n_total`, then ascending gene symbol. Feasible means that a ranked gene can be paired with a reviewed human UniProt sequence, retain binary missense rows after ClinVar parsing and sequence checks, and still yield a scoreable reference surface. The scan sees 15,752 genes, of which 446 pass the threshold stage. The panel-expansion run fixed the target size at 25 and realized all 25 genes, so the realized panel is `BRCA1`, `TP53`, `BRCA2`, `KMT2D`, `DMD`, `DNAH5`, `CHD7`, `MSH2`, `NSD1`, `SACS`, `DNAH11`, `COL7A1`, `ADGRV1`, `ANKRD11`, `TSC2`, `PKD1`, `CREBBP`, `DYNC1H1`, `GRIN2A`, `GRIN2B`, `USH2A`, `COL2A1`, `SYNGAP1`, `KMT2A`, and `ZEB2`. That provenance matters because the panel is bounded, but not hand-picked by observed performance.

The benchmark-extension rule is likewise operational. A non-anchor gene qualifies as the next benchmark candidate only if its paired pair-vs-likelihood lower confidence bound is positive and its nested fixed-`0.55` mean AUC exceeds its nested likelihood-only mean AUC. Under that rule, BRCA2 qualifies. NSD1 and MSH2 remain scientifically interesting, but both fail the release criterion because their lower bounds remain non-positive. The paper therefore has a concrete next benchmark surface instead of an undefined post-TP53 horizon.

### 5.4 Frozen Executable Contract

The executable contract remains one of the study's strengths. The public canonical setup is `uv sync --frozen` followed by `uv run spectralbio canonical`, which materializes the frozen TP53 artifact from bundled inputs and bundled score references. GPU is not required for that canonical replay path. The contract remains machine-checkable through `outputs/canonical/summary.json` and `outputs/canonical/verification.json`, with the latter exposing structured pass/fail fields for file-set validation, metric agreement, schema alignment, and artifact completeness. BRCA2 is the manuscript's flagship scientific result, but TP53 remains the only frozen public canonical replay surface. The contract therefore makes the covariance claim numerically challengeable on a frozen public surface.

### 5.5 Public Analysis Surfaces

The BRCA2 ESM-1v augmentation analysis contains the strongest direct test of whether covariance adds signal beyond a stronger baseline, because it joins the baseline-versus-augmentation comparison to the covariance-permutation null on the same surface. The BRCA2 canonicalization analysis shows that BRCA2 is not merely a favorable auxiliary example, but the only non-anchor gene that currently satisfies the benchmark-promotion rule. TP53 remains the executable anchor because it is the only frozen public canonical replay surface, whereas BRCA2 carries the manuscript's flagship scientific result.

## 6. Results

We begin with the BRCA2 augmentation audit because the strongest-baseline test provides the sharpest test of the central hypothesis. TP53 then serves as the validation anchor that shows the underlying covariance signal is real and auditable. The support-ranked top-25 panel addresses breadth and anti-cherry-picking, while the protocol sweep and BRCA1 analysis define boundary conditions.

### 6.1 Flagship Result: Covariance on Top of ESM-1v on BRCA2

The main alternative explanation faced by SpectralBio is straightforward: perhaps covariance only appears useful because the baseline branch is weak. The BRCA2 ESM-1v augmentation audit is designed to answer exactly that objection. The core comparison is a three-way contrast on BRCA2 between the ESM-1v baseline, the aligned covariance-plus-ESM-1v score, and the covariance-permuted null. In that setting, covariance still adds signal.

| Gene | ESM-1v AUC | SpectralBio reference pair | Covariance + ESM-1v at fixed `0.55` | Best full-surface alpha | Best full-surface AUC | Delta vs ESM-1v | 95% CI for delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| TP53 | `0.9466` | `0.7498` | `0.9305` | `0.30` | `0.9525` | `-0.0161` | `[-0.0416, 0.0060]` |
| BRCA1 | `0.7865` | `0.8285` | `0.7951` | `0.30` | `0.8056` | `+0.0086` | `[-0.0230, 0.0446]` |
| BRCA2 | `0.6324` | `0.7446` | `0.6890` | `0.90` | `0.7143` | `+0.0566` | `[0.0131, 0.1063]` |
| NSD1 | `0.8828` | `0.8608` | `0.8742` | `0.25` | `0.8961` | `-0.0086` | `[-0.0378, 0.0231]` |

Figure 1 summarizes the BRCA2 result across its three evidentiary components: stronger baseline, observed gain, and direct falsification.

| Panel | Quantity | Main result | Interpretation |
| --- | --- | --- | --- |
| A | BRCA2 ESM-1v baseline versus aligned covariance + ESM-1v | `0.6324` versus `0.6890` | Covariance improves discrimination even after the baseline is upgraded |
| B | Paired BRCA2 delta over ESM-1v | `+0.0566` with 95% paired bootstrap CI `[0.0131, 0.1063]` | The observed gain remains positive under paired uncertainty estimation |
| C | Covariance-permutation null | Null mean `-0.0350`; observed aligned gain at empirical `p = 0.0010` | The gain depends on correct covariance alignment rather than generic score combination |

**Figure 1. BRCA2 augmentation and falsification summary.** Panel A compares BRCA2 discrimination under the five-model ESM-1v ensemble alone (`AUC 0.6324`) and the aligned covariance-plus-ESM-1v score (`AUC 0.6890`). Panel B reports the paired gain over ESM-1v (`+0.0566`, 95% paired bootstrap CI `[0.0131, 0.1063]`). Panel C shows the covariance-alignment permutation null, whose mean is `-0.0350`; no null replicate reaches the observed aligned gain, giving empirical `p = 0.0010`. Together these panels summarize why BRCA2 provides the strongest direct test of the central hypothesis.

The BRCA2 row is the manuscript's most memorable empirical result. The aligned covariance augmentation improves over ESM-1v by `+0.0566` AUC and survives paired bootstrap uncertainty in the favorable direction. The accompanying permutation audit closes the loop: when covariance alignment is destroyed, the observed BRCA2 gain is no longer reachable. Under covariance permutation, the null mean becomes `-0.0350`, with empirical probability `p = 0.0010` of producing a value at least as large as the observed aligned result. This is the clearest direct evidence in the paper that covariance is contributing real signal rather than just repackaging baseline behavior.

The other rows calibrate scope rather than compete with BRCA2 for narrative centrality. TP53 prevents overclaiming because the fixed `0.55` augmented score does not beat ESM-1v, even though the exploratory full-surface best-alpha result slightly exceeds it. BRCA1 is inconclusive under this augmentation view, and NSD1 remains negative to ambiguous. The result is therefore narrow and strong: the paper does not claim that covariance improves every strong baseline everywhere; it claims that BRCA2 is a clean, falsifiable case where it does.

### 6.2 TP53 as Validation Anchor

TP53 serves a different job. It is the owned canonical benchmark on which the manuscript can show that covariance signal is real, reproducible, and not dependent on post hoc retelling. On the frozen TP53 benchmark, the released pair `0.55*frob_dist + 0.45*ll_proper` achieves official AUC `0.7498` and released value `0.749751552795031`, matching within the declared tolerance. The benchmark therefore remains both numerically reproducible and contract-verifiable.

| TP53 score surface | AUC |
| --- | ---: |
| `ll_proper` | `0.5956` |
| `frob_dist` | `0.6209` |
| `trace_ratio` | `0.6242` |
| `sps_log` | `0.5988` |
| `0.55*frob_dist + 0.45*ll_proper` | `0.7498` |

The key TP53 pattern is complementarity rather than single-feature dominance. `ll_proper` and `frob_dist` are both modest alone, while their released combination is substantially higher. The pair improves over `ll_proper` by `+0.1542` AUC and over `frob_dist` by `+0.1288`. Within the original released artifact, `ll_crude` reaches `0.7026` and the released triple `ll_crude + TraceRatio + frob_dist` reaches `0.7264`, but neither exceeds the canonical pair. TP53 therefore still supports the same mechanistic reading: a matrix-level perturbation statistic and a likelihood term contribute complementary information.

The repeated nested cross-validation audit then addresses the main criticism of the TP53 anchor, namely that the released `0.55/0.45` pair may be only a same-surface tuning spike. Across 5 repeats and 5 outer folds per repeat, the tuned-alpha mean AUC is `0.7485`, the fixed `0.55` mean AUC is `0.7510`, and the fixed `0.50` mean AUC is `0.7480`. The likelihood-only and covariance-only terms remain much lower, with mean AUC `0.5983` for `ll_proper` and `0.6206` for `frob_dist`.

| TP53 nested CV metric | Mean AUC | SD |
| --- | ---: | ---: |
| Tuned alpha | `0.7485` | `0.0594` |
| Fixed `alpha = 0.55` | `0.7510` | `0.0590` |
| Fixed `alpha = 0.50` | `0.7480` | `0.0591` |
| `ll_proper` | `0.5983` | `0.0611` |
| `frob_dist` | `0.6206` | `0.0570` |

The chosen-alpha distribution is stable rather than erratic. Across the 25 outer folds, the chosen alpha has mean `0.58` and standard deviation `0.0548`, with counts concentrated around the released value. Nested tuning does not reveal a hidden collapse in performance, and the released `0.55` setting performs essentially as well as or slightly better than the out-of-fold tuned average. TP53 therefore does not carry the manuscript as a universal benchmark, but it does validate that the underlying covariance effect is real and challengeable.

### 6.3 BRCA2 Benchmark Extension and Canonicalization Evidence

BRCA2 is also the only non-anchor gene that satisfies the manuscript's promotion rule for benchmark extension. That matters because the flagship BRCA2 augmentation result would be narratively weaker if BRCA2 remained only a favorable auxiliary example. The dedicated BRCA2 audit shows positive point-estimate gains across all three checkpoints, with strongest confidence at 650M and a wider 3B interval that still includes zero.

| BRCA2 checkpoint | `ll_proper` | Pair at `0.55` | Pair minus `ll_proper` | 95% CI for paired delta |
| --- | ---: | ---: | ---: | --- |
| ESM2-150M | `0.6935` | `0.7446` | `+0.0510` | `[0.0010, 0.1006]` |
| ESM2-650M | `0.6906` | `0.7994` | `+0.1088` | `[0.0516, 0.1650]` |
| ESM2-3B | `0.7685` | `0.8264` | `+0.0578` | `[-0.0033, 0.1211]` |

The nested BRCA2 audit is equally important because it elevates BRCA2 from a favorable point estimate to a release-ready benchmark candidate. Across 25 outer folds, the fixed `0.55` mean AUC is `0.7448`, the fixed `0.50` mean AUC is `0.7439`, and the tuned-alpha mean AUC is `0.7409`, while the nested likelihood-only mean AUC is `0.6938`. The chosen alpha has mean `0.616` and standard deviation `0.088`, again consistent with a plateau rather than a knife-edge optimum.

| BRCA2 nested CV metric | Mean AUC | SD |
| --- | ---: | ---: |
| Tuned alpha | `0.7409` | `0.0708` |
| Fixed `alpha = 0.55` | `0.7448` | `0.0746` |
| Fixed `alpha = 0.50` | `0.7439` | `0.0763` |
| `ll_proper` | `0.6938` | `0.0848` |
| `frob_dist` | `0.7110` | `0.0572` |

This is the relevant evidentiary threshold for calling BRCA2 the next canonicalization target. The argument is no longer just that BRCA2 looks good in one auxiliary comparison. It is that BRCA2 is the only non-anchor gene that satisfies a predeclared benchmark-promotion rule under both paired-confidence and nested-performance criteria.

### 6.4 Support-Ranked Top-25 Panel

The support-ranked top-25 feasible panel exists to answer a different challenge: whether the paper's positive story depends on favorable hand-selection. It covers 10,992 variants in total, with 3,019 pathogenic and 7,973 benign variants. Because the panel is derived from a 15,752-gene scan with transparent thresholds and ranking rules, it carries far more scientific weight than the earlier hand-built companion panel.

The central panel result is not uniform success. Instead, it is structured heterogeneity on a performance-blind surface. Ten genes have positive pair-vs-likelihood lower confidence bounds: `TP53`, `BRCA2`, `KMT2D`, `DNAH5`, `CHD7`, `ANKRD11`, `TSC2`, `PKD1`, `CREBBP`, and `KMT2A`. Two genes are clearly negative with upper confidence bounds below zero: `BRCA1` and `COL2A1`. The remaining thirteen genes are ambiguous. That is more informative than a selectively favorable smaller panel because it shows where covariance helps, where it fails, and where the current evidence remains inconclusive.

| Gene | N | Pos / neg | `ll_proper` | Pair AUC | Pair - `ll` | 95% CI for paired delta |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| BRCA1 | `512` | `165 / 347` | `0.8527` | `0.8283` | `-0.0245` | `[-0.0470, -0.0029]` |
| TP53 | `255` | `115 / 140` | `0.5956` | `0.7498` | `+0.1542` | `[0.0889, 0.2251]` |
| BRCA2 | `658` | `100 / 558` | `0.6938` | `0.7446` | `+0.0507` | `[0.0004, 0.1000]` |
| KMT2D | `1181` | `93 / 1088` | `0.6920` | `0.7358` | `+0.0438` | `[0.0012, 0.0903]` |
| DMD | `367` | `25 / 342` | `0.7123` | `0.7087` | `-0.0036` | `[-0.0774, 0.0888]` |
| DNAH5 | `449` | `41 / 408` | `0.6187` | `0.7079` | `+0.0892` | `[0.0081, 0.1845]` |
| CHD7 | `390` | `74 / 316` | `0.6563` | `0.7221` | `+0.0658` | `[0.0205, 0.1176]` |
| MSH2 | `395` | `124 / 271` | `0.7463` | `0.7491` | `+0.0028` | `[-0.0389, 0.0480]` |
| NSD1 | `407` | `160 / 247` | `0.8473` | `0.8613` | `+0.0140` | `[-0.0168, 0.0509]` |
| SACS | `516` | `48 / 468` | `0.6680` | `0.6979` | `+0.0299` | `[-0.0533, 0.1193]` |
| DNAH11 | `1078` | `23 / 1055` | `0.7978` | `0.7949` | `-0.0029` | `[-0.0532, 0.0554]` |
| COL7A1 | `497` | `283 / 214` | `0.9429` | `0.9499` | `+0.0070` | `[-0.0049, 0.0189]` |
| ADGRV1 | `624` | `20 / 604` | `0.5260` | `0.5915` | `+0.0655` | `[-0.0562, 0.2157]` |
| ANKRD11 | `264` | `33 / 231` | `0.6112` | `0.8047` | `+0.1935` | `[0.1241, 0.2709]` |
| TSC2 | `362` | `164 / 198` | `0.5672` | `0.7000` | `+0.1327` | `[0.0860, 0.1799]` |
| PKD1 | `348` | `163 / 185` | `0.7491` | `0.8194` | `+0.0703` | `[0.0356, 0.1060]` |
| CREBBP | `296` | `114 / 182` | `0.6473` | `0.7524` | `+0.1051` | `[0.0624, 0.1502]` |
| DYNC1H1 | `383` | `141 / 242` | `0.6516` | `0.6384` | `-0.0132` | `[-0.0591, 0.0342]` |
| GRIN2A | `278` | `101 / 177` | `0.8155` | `0.8067` | `-0.0087` | `[-0.0523, 0.0324]` |
| GRIN2B | `276` | `138 / 138` | `0.7382` | `0.6961` | `-0.0421` | `[-0.0896, 0.0097]` |
| USH2A | `438` | `305 / 133` | `0.8773` | `0.8933` | `+0.0160` | `[-0.0045, 0.0330]` |
| COL2A1 | `578` | `450 / 128` | `0.9792` | `0.9474` | `-0.0318` | `[-0.0634, -0.0074]` |
| SYNGAP1 | `189` | `61 / 128` | `0.6930` | `0.7317` | `+0.0387` | `[-0.0050, 0.0870]` |
| KMT2A | `85` | `43 / 42` | `0.5493` | `0.7248` | `+0.1755` | `[0.0736, 0.2850]` |
| ZEB2 | `166` | `35 / 131` | `0.8417` | `0.8646` | `+0.0229` | `[-0.0187, 0.0809]` |

This panel changes the interpretation in two ways simultaneously. It makes the positive case broader, because covariance utility is visible beyond TP53 on multiple independent genes and includes BRCA2 on a performance-blind breadth surface. It also makes the paper more credible, because the panel contains real negatives and ambiguities instead of a curated all-green transfer story.

### 6.5 Protocol Sweep and Boundary Conditions

The protocol sweep closes the remaining version of the scaling criticism. It is no longer enough to say that the manuscript reran a larger checkpoint. The current study tests 192 configurations spanning four genes, three checkpoints, four window radii, four layer protocols, and three alpha-handling modes. The resulting pattern is more informative than monotone improvement. Covariance utility is real, but protocol-sensitive. Small windows and shallower layer subsets often outperform the canonical `40/all_layers` setting, especially for TP53 and BRCA2.

| Gene | Checkpoint | Best fixed-`0.55` protocol | Pair minus `ll_proper` | Best nested protocol | Pair minus `ll_proper` |
| --- | --- | --- | ---: | --- | ---: |
| TP53 | ESM2-t30_150M | `w=20, last8` | `+0.1987` | `w=20, top_half, a=0.90` | `+0.2323` |
| TP53 | ESM2-t33_650M | `w=40, last4` | `+0.1040` | `w=40, last4, a=0.60` | `+0.1072` |
| TP53 | ESM2-t36_3B | `w=20, all_layers` | `+0.1572` | `w=20, last4, a=0.35` | `+0.1767` |
| BRCA1 | ESM2-t30_150M | `w=20, all_layers` | `+0.0449` | `w=20, all_layers, a=0.40` | `+0.0477` |
| BRCA1 | ESM2-t33_650M | `w=120, all_layers` | `-0.0035` | `w=20, all_layers, a=0.20` | `+0.0068` |
| BRCA1 | ESM2-t36_3B | `w=80, all_layers` | `-0.0040` | `w=20, all_layers, a=0.25` | `+0.0201` |
| BRCA2 | ESM2-t30_150M | `w=20, last4` | `+0.1428` | `w=20, last4, a=0.55` | `+0.1428` |
| BRCA2 | ESM2-t33_650M | `w=40, all_layers` | `+0.1088` | `w=40, last4, a=0.50` | `+0.1108` |
| BRCA2 | ESM2-t36_3B | `w=20, last4` | `+0.0901` | `w=20, last4, a=0.40` | `+0.1043` |
| NSD1 | ESM2-t30_150M | `w=20, all_layers` | `+0.0789` | `w=20, all_layers, a=0.50` | `+0.0791` |
| NSD1 | ESM2-t33_650M | `w=20, all_layers` | `+0.0318` | `w=20, all_layers, a=0.40` | `+0.0388` |
| NSD1 | ESM2-t36_3B | `w=20, all_layers` | `-0.0044` | `w=20, all_layers, a=0.30` | `+0.0278` |

This table sharpens the interpretation of multiple genes. TP53 is not just positive; it is strongly protocol-sensitive, with best nested gains that exceed the canonical public setting. BRCA2 shows positive point-estimate gains across all three checkpoints, with strongest support at 650M and a wider 3B interval that still includes zero. BRCA1, perhaps the most important hard case, is no longer a simple negative-transfer result: the canonical `40/all_layers` setting is negative, yet smaller-window protocols recover modest positive deltas.

That BRCA1 pattern becomes more interpretable in the dedicated failure analysis. The global BRCA1 result is negative, with pair AUC `0.8283` versus likelihood `0.8527`, but that negativity is not uniform across confidence, review-status, and domain strata.

| BRCA1 stratum | N | Pair AUC | `ll_proper` AUC | Pair - `ll` |
| --- | ---: | ---: | ---: | ---: |
| All variants | `512` | `0.8283` | `0.8527` | `-0.0245` |
| Low confidence | `218` | `0.8383` | `0.8276` | `+0.0107` |
| High confidence | `197` | `0.8484` | `0.9063` | `-0.0579` |
| BRCT1 domain | `81` | `0.8390` | `0.8699` | `-0.0309` |
| BRCT2 domain | `66` | `0.8566` | `0.8517` | `+0.0049` |
| RING domain | `44` | `0.9884` | `0.9846` | `+0.0039` |
| Expert panel reviewed | `197` | `0.8484` | `0.9063` | `-0.0579` |
| Criteria provided, single submitter | `205` | `0.8316` | `0.8226` | `+0.0089` |

The correct interpretation is therefore not that BRCA1 disproves covariance. It is that the canonical BRCA1 full-set configuration is likelihood-dominant, but the failure is structured. High-confidence and expert-panel subsets are more negative than the whole set. BRCT1 is negative, while BRCT2 and RING are near-neutral to slightly positive. Combined with the protocol sweep, this makes BRCA1 a region- and protocol-sensitive boundary case rather than evidence that covariance is globally useless outside TP53.

### 6.6 Negative Controls and Falsification

The negative controls remain claim-bearing evidence rather than cosmetic appendix material. On the frozen TP53 score surface, 1000 label permutations produce an AUC distribution with mean `0.4994`, standard deviation `0.0360`, and observed range `[0.3871, 0.6048]`, while the released canonical pair remains at `0.7498`; no permutation reaches that value, giving an empirical probability `p = 0.0010`. Once biological label alignment is destroyed, the score collapses to chance-level behavior.

A second supplementary control destroys local positional context while preserving amino-acid composition and the central residue identity. Across three independent shuffled-context reruns, the released canonical pair drops from `0.7498` to `0.5759`, `0.5286`, and `0.5117`, with mean `0.5388` and standard deviation `0.0333`. The mean drop relative to the released pair is therefore `0.2110`. This shows that the TP53 anchor is not merely an artifact of residue composition; it depends on intact local context geometry.

The BRCA2 permutation audit completes the manuscript's strongest falsification loop. On BRCA2, the observed covariance-on-ESM-1v gain is `+0.0566`. Under covariance-alignment permutation, the null mean is `-0.0350`, and the observed gain becomes unattainable at empirical probability `p = 0.0010`. Under ESM-1v-alignment permutation, the null mean is strongly positive in the opposite direction, again making the observed aligned gain non-generic. Taken together, TP53 and BRCA2 show two different kinds of falsification support: TP53 shows that the base covariance signal collapses when labels or context are broken, and BRCA2 shows that the strongest-baseline gain collapses when covariance alignment is broken.

## 7. Discussion

The combined evidence supports a narrow but coherent interpretation of SpectralBio, and that interpretation now has a clear center of mass. The paper's strongest result is not merely that covariance helps on an internal TP53 comparison. It is that on BRCA2, covariance-aware hidden-state geometry improves a stronger ESM-1v ensemble baseline, and that the gain disappears under covariance permutation. That is the manuscript's clearest answer to the most damaging alternative explanation, namely that covariance only appears useful because the comparison baseline is weak.

TP53 then takes on a cleaner role. It is the validation anchor that shows the underlying covariance signal is real, executable, and not a same-surface tuning accident. The frozen TP53 benchmark establishes complementarity between covariance and likelihood, while the nested audit shows that the released alpha sits on a stable out-of-fold plateau. TP53 therefore does not have to carry the whole paper alone. It has to show that the mechanism being invoked by the BRCA2 result is not illusory.

The support-ranked top-25 panel serves a similarly specific purpose. Its value is not that it turns the manuscript into a universal generalization claim. Its value is that it breaks the hand-picked-companion critique. Because the panel is derived from a 15,752-gene scan with explicit thresholds and a support-ranked feasibility rule, the reader is no longer being asked to trust a favorable set of examples selected after seeing deltas. The resulting pattern is heterogeneous, not uniformly positive, and that is exactly why it is scientifically useful.

The protocol sweep and BRCA1 analysis complete the story by showing that covariance utility is structured rather than monotone. BRCA2 remains supportive across checkpoints at the point-estimate level. TP53 becomes even stronger under some smaller-window and shallower-layer protocols than under the public canonical setting. BRCA1 remains negative overall, but not uniformly so; the failure is concentrated in identifiable strata and domains. Those are not embarrassing exceptions to hide. They are the current boundary conditions of the method.

The broader implication is not clinical deployment. It is benchmark culture. Zero-shot missense work should not treat scalar likelihood as the only internal readout worth auditing. The relevant comparison set is broader: likelihood-only, eigenvalue-only, full-matrix covariance, covariance plus likelihood, covariance plus stronger external baselines, and bounded protocol sweeps that test whether the effect survives reasonable perturbations. SpectralBio does not settle that agenda, but it does make it difficult to dismiss.

The reproducibility strength remains important in that context. The canonical benchmark is unusually challengeable because it is backed by a frozen executable contract, machine-readable expected outputs, and machine-checkable verification artifacts. That contract does not substitute for empirical evidence; it makes the empirical claim directly testable and gives the manuscript a harder floor under criticism.

## 8. Limitations and Non-Claims

TP53 remains the only frozen public canonical benchmark. BRCA2 is now a release-ready second benchmark candidate under a predeclared rule, and it is also the manuscript's strongest augmentation result, but it is not yet exposed as a published CPU-only canonical bundle with the same first-class replay surface as TP53. The paper therefore has one released public benchmark, one explicit next-canonicalization path, and one flagship supplementary result rather than two released canonical benchmarks.

The support-ranked top-25 panel is still selected rather than exhaustive. The global scan removes the charge of hand-picking because panel construction begins from 15,752 observed genes and 446 threshold-passing genes under a transparent ranking rule. Even so, the final panel is a bounded feasible subset after sequence retrieval, ClinVar parsing, and sequence-consistency filtering, not a full survey of all qualifying genes. The breadth surface is therefore stronger than a hand-built companion panel, but it does not erase the distinction between support-ranked validation and exhaustive external generalization.

The breadth surface is also still ClinVar-based. It is not an orthogonal functional benchmark in the style of a full external deep-mutational-scanning or saturation-assay surface. The top-25 result should therefore be interpreted as a structured ClinVar generalization surface rather than as assay-complete external validation.

The BRCA2 ESM-1v augmentation result is strong but still bounded. On BRCA2, the covariance augmentation over ESM-1v is positive with a positive confidence interval and survives a permutation audit. On TP53, the fixed `0.55` augmented score does not beat ESM-1v, even though the full-surface best-alpha exploratory result does. The correct interpretation is therefore that BRCA2 is the clean positive stronger-baseline case, while TP53 remains suggestive but not release-ready under that specific comparison.

The protocol sweep closes the simplest scaling criticism without exhausting the space. The current study tests 192 configurations across checkpoints, windows, layer subsets, and alpha handling, which is enough to reject the claim that covariance utility is merely a 150M artifact. It is not enough to settle every scaling question or define a universal optimal protocol. The sweep covers four genes, not all genes in the panel; it covers four window radii and four layer protocols, not an exhaustive protocol universe; and it still leaves open richer combination rules and broader backbone families.

These boundaries imply specific non-claims. The paper does not claim broad cross-protein portability, clinical deployment, clinical decision support, or superiority to external predictors on a shared public benchmark. It does not claim that larger ESM2 checkpoints monotonically strengthen covariance-aware scoring. It does not claim that the support-ranked top-25 panel defines a universal law of covariance utility. It does not claim that the exploratory TP53 best-alpha augmentation over ESM-1v is already a release-grade result. These caveats are part of the result, not decorative qualifications.

## 9. Benchmark Extension Path

The paper has a concrete answer to the question of what comes after TP53. Under the predeclared benchmark-extension rule, BRCA2 is the only non-anchor gene that qualifies. Its paired lower confidence bound is positive, its nested fixed-`0.55` mean AUC exceeds its nested likelihood-only mean AUC, and it retains substantial support after filtering. That makes BRCA2 the correct next target for canonicalization.

Canonicalization still requires real work, but it is no longer hypothetical. A BRCA2 public benchmark release would need the same elements that made TP53 challengeable: a frozen sequence reference, a frozen benchmark variant file, score references, configuration and manifest files, expected metrics, and machine-checkable verification artifacts. For full manuscript-artifact parity, the BRCA2 augmentation and permutation surfaces should also be exposed as first-class public audit outputs rather than only as notebook-generated analyses. The current evidence justifies that work scientifically.

Beyond BRCA2, the relevant next step is not to search for another favorable companion gene. It is to ask which support-ranked genes join BRCA2 in qualifying under the same bounded promotion rule as canonicalization infrastructure expands. The top-25 panel turns that into a concrete agenda.

## 10. Conclusion

SpectralBio supports a bounded but memorable conclusion. On BRCA2, adding covariance-aware hidden-state geometry to a five-model ESM-1v ensemble improves AUC from `0.6324` to `0.6890`, and that gain disappears under covariance permutation with empirical `p = 0.0010`. This is the manuscript's clearest evidence that covariance contributes recoverable pathogenicity-ranking signal beyond a stronger external zero-shot baseline.

The rest of the evidence gives that claim its proper weight. TP53 shows that the underlying covariance effect is real and not a same-surface tuning accident. The support-ranked top-25 panel shows that the paper is not built from favorable hand-selection and that breadth is heterogeneous rather than universally positive. The protocol sweep and BRCA1 analysis show that the phenomenon is checkpoint-, window-, layer-, and gene-sensitive rather than a trivial monotone scaling law.

The appropriate final interpretation is therefore a bounded representational one: covariance-aware hidden-state geometry contains real zero-shot pathogenicity signal; BRCA2 shows that the signal can improve a stronger baseline; TP53 shows that the signal is executable and auditable; and the support-ranked panel together with the boundary analyses shows where the current method generalizes and where it does not. The benchmark artifact makes that claim directly challengeable and gives BRCA2 a clear path to becoming the next canonical surface.

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

The BRCA2 augmentation and canonicalization analyses document the manuscript's flagship scientific result and its benchmark-extension path, while the TP53 summary and verification files remain the only frozen public canonical replay surface for the underlying covariance claim.

| Surface | Role |
| --- | --- |
| [Repository](https://github.com/DaviBonetto/SpectralBio) | Source repository and primary public code surface |
| [Release bundle `v1.2.0`](https://github.com/DaviBonetto/SpectralBio/tree/v1.2.0/artifacts/release/claw4s_2026) | Frozen packaged release surface for the artifact bundle |
| [Paper PDF](https://github.com/DaviBonetto/SpectralBio/blob/v1.2.0/paper/spectralbio.pdf) | Release-pinned public manuscript mirror |
| [BRCA2 ESM-1v augmentation notebook](https://github.com/DaviBonetto/SpectralBio/blob/v1.2.0/notebooks/final_accept_part3_esm1v_augmentation_A100.ipynb) | Flagship BRCA2 baseline-versus-augmentation-versus-permutation analysis |
| [BRCA2 canonicalization notebook](https://github.com/DaviBonetto/SpectralBio/blob/v1.2.0/notebooks/final_accept_part4_brca2_canonicalization_A100.ipynb) | BRCA2 benchmark-candidate qualification and next-canonicalization evidence |
| [Canonical `summary.json`](https://github.com/DaviBonetto/SpectralBio/blob/v1.2.0/outputs/canonical/summary.json) | Machine-readable TP53 validation-anchor metric surface |
| [Canonical `verification.json`](https://github.com/DaviBonetto/SpectralBio/blob/v1.2.0/outputs/canonical/verification.json) | Machine-readable TP53 validation-anchor contract verification surface |
| [Support-scan notebook](https://github.com/DaviBonetto/SpectralBio/blob/v1.2.0/notebooks/final_accept_part1_support_panel.ipynb) | Public analysis surface for global ClinVar support ranking, feasibility filtering, and panel provenance |
| [Protocol-sweep notebook](https://github.com/DaviBonetto/SpectralBio/blob/v1.2.0/notebooks/final_accept_part5_protocol_sweep_A100.ipynb) | Public analysis surface for the 192-configuration checkpoint/window/layer boundary analysis |
| [Top-25 panel and BRCA1 failure notebook](https://github.com/DaviBonetto/SpectralBio/blob/v1.2.0/notebooks/final_accept_part6_panel25_brca1_failure_L4.ipynb) | Public analysis surface for anti-cherry-picking breadth, BRCA1 strata, and supplementary boundary summaries |
| [Dataset](https://huggingface.co/datasets/DaviBonetto/spectralbio-clinvar) | Public data surface for the study |
| [Demo Space](https://huggingface.co/spaces/DaviBonetto/spectralbio-demo) | Interactive public demonstration surface |
| [SKILL](https://github.com/DaviBonetto/SpectralBio/blob/v1.2.0/SKILL.md) | Release-pinned public cold-start reproduction contract |
| [Truth contract](https://github.com/DaviBonetto/SpectralBio/blob/v1.2.0/docs/truth_contract.md) | Claim boundary and precedence surface |
| [Reproducibility notes](https://github.com/DaviBonetto/SpectralBio/blob/v1.2.0/docs/reproducibility.md) | Public explanation of canonical execution semantics |
| [clawRxiv mirror](https://github.com/DaviBonetto/SpectralBio/blob/v1.2.0/publish/clawrxiv/spectralbio_clawrxiv.md) | Publication-facing mirror of the study page |
