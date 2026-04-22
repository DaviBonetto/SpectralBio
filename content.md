# What ESM2 Cannot Feel: Local Hidden-State Covariance Reveals Structural Strain and Survives Replay-Ready Multi-Target Transfer

## 1. Introduction

Missense interpretation is bottlenecked by a dangerous illusion of competence. Sequencing generates variants faster than experiment can validate them, so the field has embraced zero-shot scoring with protein language models as a triage filter. The dominant framing is seductively simple: a mutation is pathogenic if the mutant residue is sufficiently surprising to the model [1,2,6,9,10]. That framing works until it does not.

Consider TP53 p.Val272Met. In matched crystal structures, this variant produces a median local RMSD of 1.91 Å, a clear structural rearrangement. Yet ESM2 scores it with only moderate token-level surprise. The model does not feel the rearrangement. It is a physician wearing gloves too thick to detect a fracture.

We show that this blindness is not anecdotal. It is a **systematic representational failure mode** that can be audited, localized, and partially repaired. The diagnostic tool is local hidden-state covariance. Instead of asking how surprising a mutant token is, we ask how much the substitution reorganizes the local geometry of the hidden representation field. Mutation-centered covariance matrices act as a **structural stethoscope**: they read out geometric strain that scalar likelihood cannot feel.

The paper builds three scientific pillars around that intuition, then asks how far those pillars travel under progressively harsher portability and closure tests.

**First, a structural smoking gun.** TP53 p.Val272Met sits in a high-covariance, low-likelihood class. Across a repaired structural subset, covariance aligns with a composite structural-tension target at Spearman 0.309; scalar likelihood aligns at 0.036. The geometry registers a rearrangement that token probability barely notices.

**Second, a flagship stronger-baseline result.** On BRCA2, adding covariance-aware geometry to a five-model ESM-1v ensemble improves AUC from 0.6324 to 0.6890, a paired gain of 0.0566 with 95% bootstrap CI [0.0131, 0.1063]. The gain vanishes under covariance permutation (empirical *p* = 0.0010). Covariance is not living off a weak scalar comparator.

**Third, a performance-blind failure-mode audit.** In a chemically narrow regime of basic substitutions with high disagreement, ESM2-150M systematically overstates covariance disruption relative to matched controls, while ESM2-650M largely repairs the pattern. Across 13 gene-matched pairs, mean Frobenius gap reduction is 0.7250 (exact sign-flip *p* = 0.000244). The likelihood channel shows no corresponding repair. Covariance is not merely a feature here; it is an **audit readout** for a concrete scale-repair blind spot inside the ESM2 family.

The rest of the manuscript asks how far those pillars travel and where they stop. A clinical-panel audit improves over the frozen scalar baseline in 4 of 4 positive-focus genes and yields 12 rescue candidates, condensed into a five-case rescue gallery across three genes plus an explicit BRCA1 anti-case. A stronger-baseline MSH2 follow-up is decisively negative (best α collapses to 0.0), confirming that the signal is gene-dependent rather than universal.

The earlier harsh firewalls remain important: orthogonal TP53 validation, multifamily aggregation, covariance adjudication, and final localization all keep the claim disciplined. The late-stage portability evidence then raises the ceiling, expanding the public surface to four replay-ready targets with two transfer-positive targets and explicit negative guardrails. The final holdout/control tribunal still fails to close the harshest version of generalization. The correct ending is therefore neither a TP53/BRCA2-only bounded story nor universal closure. It is **strengthened portability with disciplined stopping points**.

### 1.1 Key Findings

1. **Structural dissociation.** Local hidden-state covariance aligns with structural tension where scalar likelihood fails (Spearman 0.309 versus 0.036 on a repaired TP53 subset), grounded in a concrete anchor case with median local RMSD 1.91 Å.

2. **Stronger-baseline survival.** On BRCA2, covariance augmentation improves a five-model ESM-1v ensemble from AUC 0.6324 to 0.6890 (paired gain 0.0566, 95% CI [0.0131, 0.1063]); the gain disappears under covariance permutation (*p* = 0.0010).

3. **Scale-repair failure mode.** ESM2-150M overstates covariance disruption for basic substitutions in high-disagreement contexts; ESM2-650M repairs the pattern. The repair survives matched-pair and same-position sister-substitution controls with exact sign-flip *p* = 0.000244 and *p* = 0.007812 respectively. Likelihood shows no parallel repair.

4. **Replay-ready multi-target portability.** The late-stage portability program now yields four replay-ready targets (`TP53`, `BRCA2`, `TSC2`, `CREBBP`) and two transfer-positive targets (`TSC2`, `CREBBP`). `BRCA1` and `MSH2` remain explicit negative guardrails rather than being laundered away.

5. **Disciplined stopping point.** The final harsh holdout/control tribunal remains mixed: no model achieves holdout-positive closure, no model achieves control-win closure, and the harshest model-level transfer closure still fails. The claim is therefore materially strengthened, but not universalized.

## 2. Scientific Context and Motivation

Zero-shot missense scoring avoids per-gene supervised retraining, but most methods still reduce the problem to a scalar token-preference question: how strongly does the model prefer the wild-type residue over the mutant? That framing is useful and often competitive, yet it may omit a second class of information. A mutation can preserve moderate token plausibility while reorganizing the local geometry of the hidden representation field, disturbing packing, polarity, secondary-structure preference, and exposure-sensitive context simultaneously.

SpectralBio tests whether that geometric reorganization is readable. We treat ESM2 not only as a conditional scorer but as a layered geometric object whose local hidden states carry covariance structure. The hypothesis is narrow and falsifiable: **local full-matrix covariance displacement preserves perturbation information that scalar likelihood summaries and eigenvalue-only compressions do not fully retain.** This is compatible with the observation that protein language models learn structural regularities [18,19], but it is tested here in the specific setting of zero-shot pathogenicity ranking.

Three questions sit at the center of the study. First, does covariance survive a stronger-baseline comparison on BRCA2? Second, can covariance audit a structured regime in which a smaller backbone misweights perturbation and a larger backbone repairs it? Third, does the signal survive as replay-ready multi-target portability when stricter closure logic is imposed at the end of the pipeline? TP53 provides canonical validation; the support-ranked panel provides performance-blind breadth; the failure-mode screen plus scale-repair follow-up provides the representational audit; MSH2 provides the explicit negative replication; and the late adjudication chain determines how much portability the evidence can honestly support.

## 3. Related Work

The relevant prior work falls into four method families.

**Classical predictors.** SIFT and PolyPhen-2 use conservation, substitution patterns, and hand-designed biological features [4,5]. They established sequence-based pathogenicity scoring but do not interrogate learned internal geometry.

**Evolutionary generative models.** EVE and DeepSequence learn family-level latent models of tolerated variation [3,11]. SpectralBio differs: it studies local perturbation geometry in a pretrained protein language model without family retraining.

**Protein language model zero-shot scoring.** The ESM family demonstrated that language-model inference captures mutation effects without fine-tuning [1,2,6]. Subsequent work showed that transformers encode structural information [18] and that inverse-folding models leverage learned representations at scale [19]. SpectralBio is closest to this family but departs by treating the model as a source of layer-wise hidden-state geometry, not merely a sequence-likelihood oracle.

**Probing and internal representation analysis.** Direct-coupling analysis showed that pairwise statistical structure encodes functional information [15]. Evolutionary Action argued that mutation effect depends on context-sensitive displacement rather than a single surprise score [16]. Neuron Shapley illustrated the value of interrogating internal components rather than surface outputs [20]. SpectralBio's narrower move is to ask whether mutation-induced **covariance perturbation** is a useful internal summary for zero-shot pathogenicity ranking, and whether that contribution survives direct comparison to stronger baselines and stricter protocol controls.

No prior work uses mutation-centered full-matrix covariance in hidden states of protein language models as a structural stethoscope for missense pathogenicity.

## 4. Methodology

### 4.1 ESM2 Hidden-State Geometry

We use `facebook/esm2_t30_150M_UR50D` (30-layer, 150M parameters, hidden dimension *d* = 640) [1] as the canonical backbone. Supplementary analyses probe `facebook/esm2_t33_650M_UR50D` and `facebook/esm2_t36_3B_UR50D`. For a wild-type sequence *S*<sub>WT</sub> and its missense mutant *S*<sub>MUT</sub> at position *p*, we extract a mutation-centered local window of radius 40 residues per side (with boundary truncation). The design assumes that the most relevant perturbation signal is concentrated around the mutated site.

For each layer *l* in {1, ..., *L*}, ESM2 produces a residue-by-feature hidden-state tensor *H*<sup>(*l*)</sup> in ℝ<sup>*w*×*d*</sup>.

### 4.2 Local Covariance Features and Likelihood Terms

For each layer, we compute the covariance matrix over local hidden states:

*C*<sup>(*l*)</sup> = Cov(*H*<sup>(*l*)</sup>) in ℝ<sup>*d*×*d*</sup>

Separate covariance objects are constructed for wild-type and mutant windows, *C*<sub>wt</sub><sup>(*l*)</sup> and *C*<sub>mut</sub><sup>(*l*)</sup>. From these, we focus on three statistics:

**Frobenius distance** (full-matrix displacement):
$$\text{FrobDist} = \frac{1}{L}\sum_{l=1}^{L} \left\| C_{\text{mut}}^{(l)} - C_{\text{wt}}^{(l)} \right\|_F$$

**Trace ratio** (variance-scale change):
$$\text{TraceRatio} = \frac{1}{L}\sum_{l=1}^{L} \left| \frac{\text{tr}(C_{\text{mut}}^{(l)})}{\text{tr}(C_{\text{wt}}^{(l)})} - 1 \right|$$

**SPS-log** (eigenvalue-only compression):
$$\text{SPS-log} = \frac{1}{L}\sum_{l=1}^{L} \left\| \log |\lambda_{\text{mut}}^{(l)}| - \log |\lambda_{\text{wt}}^{(l)}| \right\|_2^2$$

Frobenius distance is the flagship statistic because it retains both diagonal variance shifts and off-diagonal correlation reorganization. Eigenvalue-only summaries compress away orientation and off-diagonal interaction structure. The decomposition

$$\left\| \Delta C^{(l)} \right\|_F^2 = \sum_i (\Delta C_{ii}^{(l)})^2 + 2\sum_{i<j} (\Delta C_{ij}^{(l)})^2$$

makes this explicit: full-matrix displacement sees reorganization that spectral compressions cannot.

The likelihood branch uses the masked-language-model term:

$$\text{LL}(v) = \log P_{\text{ESM2}}(r_{\text{wt},p} \mid S_{\text{WT}}) - \log P_{\text{ESM2}}(r_{\text{mut},p} \mid S_{\text{WT}})$$

The public canonical TP53 pair is:

$$\text{score} = 0.55 \cdot \text{frob\_dist} + 0.45 \cdot \text{ll\_proper}$$

More generally, the augmentation family is:

$$S_\alpha = \alpha \cdot s_{\text{cov}} + (1-\alpha) \cdot s_{\text{scalar}}, \quad \alpha \in [0,1]$$

where *s*<sub>cov</sub> is the scaled covariance statistic and *s*<sub>scalar</sub> is the scaled scalar branch (`ll_proper` on TP53 or the five-model ESM-1v ensemble mean in the stronger-baseline audit). The public release fixes α = 0.55; exploratory analyses treat α as surface-dependent.

### 4.3 Why Local Covariance Might Matter

The central contrast is not "SpectralBio versus one external baseline" but **full-matrix covariance displacement versus eigenvalue-only compression within the same hidden-state object**. Likelihood reduces the mutation question to residue plausibility. Eigenvalue summaries preserve spectral magnitudes but discard orientation. Full-matrix covariance remains sensitive to how correlations among hidden features reorganize.

We do not claim that hidden-state covariance is a direct biochemical observable. We use it as an **internal perturbation proxy**. If ESM2 represents local constraints across correlated hidden channels, a mutation may be visible not only as a change in the preferred residue token but also as a change in how local hidden features co-vary. Covariance is a summary of local representational reorganization, not a literal mechanistic model. The question is whether that reorganization carries ranking signal that likelihood alone misses.

That bounded interpretation also explains why covariance helps on some surfaces and hurts on others. If a gene's discriminative structure is already captured by residue plausibility, covariance adds noise. If a mutation perturbs coupled local constraints while remaining only moderately surprising at the token level, covariance adds signal. BRCA2 and the charge-sensitive scale-repair regime are of the latter type; MSH2 is direct evidence that the former exists.

### 4.4 Validation Program and Claim Hierarchy

The evidence program is a **staged escalation**. Each stage answers a different criticism, and later stages are intentionally harsher on the claim than earlier ones.

- **BRCA2**: flagship stronger-baseline test.
- **TP53**: validation anchor and structural anchor.
- **Support-ranked top-25 panel plus clinical gallery**: bounded breadth.
- **Scale-repair chain**: qualitative representational audit.
- **MSH2**: negative replication.
- **Blocks 11/12/12b/12c/12d**: early harsh firewalls defining the old supportive-not-nuclear stopping point.
- **Block 13**: replay-ready multi-target generalization strengthening.
- **Block 14**: final holdout/control closure tribunal.

A non-anchor gene qualifies as the next canonicalization target only if its paired pair-vs-likelihood 95% lower confidence bound is positive and its nested fixed-α = 0.55 mean AUC exceeds its nested likelihood-only mean AUC. Under that rule, BRCA2 qualifies. MSH2 does not.

That benchmark-promotion rule is narrower than the later portability logic. BRCA2 is therefore the next full canonicalization target, whereas `TSC2` and `CREBBP` later enter as replay-ready transfer surfaces rather than flagship canonical benchmark centerpieces.

The later escalation chain uses explicit vocabulary. **Supportive** means a model remains directionally positive under the stage's firewall but leaves unresolved escape routes (scalar dominance, control failure, transfer failure). **Replay-ready portability** is stronger: the target can be frozen as a reproducible replay surface, and target-level transfer evidence survives enough pressure to matter publicly. **Fully closed generalization** would require the harshest model-level holdout and control tribunals to close as well. The present paper reaches the second state in Block 13, but not the third after Block 14. That distinction is methodological, not rhetorical.

### 4.5 Statistical Procedures, Panel Construction, and Augmentation Protocol

All bootstrap intervals use 1000 nonparametric resamples with seed 42. AUC intervals are computed from resampled score vectors on the same surface. Pair-vs-baseline intervals use paired bootstrap resampling of the same variant indices. Resamples containing only one class are discarded; the reported interval is the empirical 2.5th to 97.5th percentile over valid resamples.

TP53 and BRCA2 nested audits use 5×5 repeated stratified cross-validation. Repeat seeds are 42-46; outer folds are stratified; inner alpha searches use the repeat seed plus fold index.

MinMax scaling is fit per score family. On a fixed surface, `frob_dist`, `ll_proper`, and the ESM-1v ensemble mean are each independently scaled to [0,1] using minima and maxima from that same scored table before pair construction. In nested CV, scaling parameters are fit on training folds only. The exploratory α sweep uses the grid 0.00, 0.05, ..., 1.00.

The support-ranked panel is built in two stages. First, genes are ranked by descending min(*n*<sub>positive</sub>, *n*<sub>negative</sub>), then descending *n*<sub>total</sub>, then ascending gene symbol, after ClinVar filtering to GRCh38, single-nucleotide variants, germline-or-empty origin, binary pathogenic/benign labels, and simple missense changes. Second, ranked genes enter the realized panel only if feasible: the run retrieves a reviewed human UniProt sequence, maps retained ClinVar missense rows, discards out-of-range and mismatched entries, and preserves enough binary rows to score. The scan sees 15,752 genes; 446 pass thresholds; the panel-expansion run fixed `top_k_requested = 25` and realized all 25 genes.

The ESM-1v augmentation protocol keeps the covariance branch on the canonical ESM2-150M backbone and replaces the baseline branch with the normalized mean zero-shot likelihood from the five-model ESM-1v ensemble `facebook/esm1v_t33_650M_UR90S_{1..5}`. The fixed augmented score is `0.55 * frob_norm + 0.45 * esm1v_norm`. The permutation audit uses 1000 replicates with seed 42 while holding labels fixed; the empirical tail probability is reported as (count(Δ_null ≥ Δ_observed) + 1) / (*B* + 1).

## 5. Results

The results are organized by evidentiary role, not notebook chronology. BRCA2 provides the stronger-baseline flagship. TP53 provides the validation and structural anchor. The panel and gallery establish bounded breadth. The failure-mode chain supplies the most distinctive qualitative result. The earlier harsh firewalls first define the old supportive-not-nuclear ceiling. The late-stage portability evidence then tests whether that ceiling can be raised. It can. But the final holdout/control tribunal still does not allow universal generalization.

### 5.1 The Structural Smoking Gun: TP53 p.Val272Met

The intuition that likelihood misses structural strain is grounded in crystal structures. Variant TP53 p.Val272Met falls into a high-covariance, low-likelihood group and shows median local RMSD of 1.91 Å in matched crystal structures. The geometry registers a rearrangement that token probability barely notices.

Across the repaired TP53 structural subset, covariance aligns with a composite structural-tension target at Spearman 0.309. Scalar likelihood aligns at 0.036. The absolute gap, 0.273, is one of the manuscript's strongest mechanistic separations. This is not a nonlinear rewrite of sequence surprise. It is a dissociation: covariance feels the strain; likelihood does not.

On the frozen canonical benchmark, the released pair `0.55 * frob_dist + 0.45 * ll_proper` reaches AUC 0.7498, substantially above either component alone (0.5956 for `ll_proper`, 0.6209 for `frob_dist`). The anti-leakage audit strengthens the anchor: across repeated nested cross-validation, tuned-α TP53 reaches mean AUC 0.7485, fixed 0.55 reaches 0.7510, and fixed 0.50 reaches 0.7480. The released weight is a stable plateau, not a fragile spike.

| TP53 score surface | AUC |
|---|---|
| `ll_proper` | 0.5956 |
| `frob_dist` | 0.6209 |
| `trace_ratio` | 0.6242 |
| `sps_log` | 0.5988 |
| `0.55 * frob_dist + 0.45 * ll_proper` | **0.7498** |

### 5.2 The Flagship: BRCA2 Survives a Stronger Baseline

The sharpest alternative explanation for SpectralBio is that covariance only appears useful because the scalar baseline is weak. The BRCA2 ESM-1v augmentation audit is the cleanest answer.

On BRCA2, replacing the baseline branch with the five-model ESM-1v ensemble still leaves room for covariance: AUC rises from 0.6324 to 0.6890, a paired gain of 0.0566 with 95% bootstrap CI [0.0131, 0.1063].

| Gene | ESM-1v AUC | Covariance + ESM-1v at fixed 0.55 | Best full-surface α | Best full-surface AUC | Δ vs ESM-1v | 95% CI for Δ |
|---|---:|---:|---:|---:|---:|:---|
| TP53 | 0.9466 | 0.9305 | 0.30 | 0.9525 | -0.0161 | [-0.0416, 0.0060] |
| BRCA1 | 0.7865 | 0.7951 | 0.30 | 0.8056 | +0.0086 | [-0.0230, 0.0446] |
| **BRCA2** | **0.6324** | **0.6890** | **0.90** | **0.7143** | **+0.0566** | **[0.0131, 0.1063]** |
| MSH2 | 0.9233 | 0.8457 | 0.00 | 0.9233 | -0.0776 | [-0.1079, -0.0489] |
| NSD1 | 0.8828 | 0.8742 | 0.25 | 0.8961 | -0.0086 | [-0.0378, 0.0231] |

The falsification closes cleanly. When covariance alignment is permuted against the same ESM-1v branch, the null mean becomes -0.0350 and the observed aligned gain is not recovered (empirical *p* = 0.0010). This is the clearest direct evidence that covariance contributes recoverable signal beyond a stronger external zero-shot baseline.

BRCA2 also graduates from favorable example to release-ready benchmark candidate. In the dedicated benchmark-extension audit, the fixed 0.55 pair remains positive across ESM2 checkpoints (Δ +0.0510 at 150M, +0.1088 at 650M, +0.0578 at 3B). Nested fixed-0.55 mean AUC is 0.7448 versus nested likelihood 0.6938; tuned-α mean is 0.7409. The chosen α distribution centers on 0.616 with standard deviation 0.088, a plateaued benchmark candidate, not a knife-edge optimum.

### 5.3 The Bug: A Scale-Repair Failure Mode Inside ESM2

The performance-blind panel yields a qualitatively different result from benchmark improvement. In a chemically narrow regime, `to_basic` substitutions intersected with high disagreement at the 75th percentile, the 150M backbone overstates covariance disruption relative to matched controls, while the 650M backbone largely repairs that error.

The regime contains 14 candidate positives, 13 matched positive controls, and 4 regime benigns. At 150M, the candidate-control Frobenius gap is +0.2946. At 650M, it flips to -0.4543, giving a gap reduction of 0.7489. Eleven of 14 candidate variants repair in the favorable direction; 6 of 7 positive-gap genes flip to non-positive.

| Scale-repair metric | Value |
|---|---|
| Selected regime | `to_basic` and `high_disagreement_q75` |
| Rescued positives in screen | 8 |
| Genes with rescued positives | 4 |
| 150M candidate-control frob gap | +0.2946 |
| 650M candidate-control frob gap | -0.4543 |
| Frob gap reduction | 0.7489 |
| Matched-pair mean frob gap reduction | **0.7250** |
| Matched-pair exact sign-flip *p* | **0.000244** |
| Sister-pair mean frob gap reduction | **0.6259** |
| Sister-pair exact sign-flip *p* | **0.007812** |
| Likelihood repair in matched pairs | -0.0790 (*p* = 0.6960) |

The result survives two tightening passes. The paired robustness audit across 13 gene-matched candidate-control pairs finds mean gap reductions 0.7250 (Frobenius) and 0.3632 (pair covariance), with exact sign-flip *p* = 0.000244 for both. The likelihood channel does not repair in parallel (-0.0790, *p* = 0.6960). The stricter same-position sister-substitution follow-up across 8 sister pairs spanning 5 genes preserves covariance-specific repair with exact sign-flip *p* = 0.007812, while likelihood again shows no corresponding repair.

This preempts the easiest objections. The effect is not explained by trivial low-complexity differences (local entropy Δ 0.0108, permutation *p* = 0.9160). It is not a generic "stronger model fixes everything" story, because the repair is concentrated in covariance space and absent from scalar likelihood. And it is not driven by cross-context comparisons, because the sister-substitution pass preserves the effect under stricter local control.

The regime remains bounded, chemically narrow, enriched for basic substitutions, with explicit non-repair tails. But that boundedness is part of the result. We do not claim a universal ESM2 bug. We claim a **falsifiable, reviewer-facing failure mode** in which covariance reveals where the smaller backbone misweights local perturbation and the larger backbone partially repairs it.

### 5.4 Bounded Breadth: The Panel, the Gallery, and the Anti-Case

The support-ranked feasible top-25 panel exists to eliminate the hand-picked-example critique. Built from a 15,752-gene ClinVar scan, it realizes 25 feasible genes covering 10,992 scored variants. The surface is heterogeneous: 10 genes have positive pair-versus-likelihood lower confidence bounds, 2 are clearly negative, and 13 remain ambiguous.

| Top-25 outcome class | Count | Interpretation |
|---|---|---|
| Positive lower bound | 10 | Real breadth, not universal |
| Clearly negative | 2 | Explicit anti-cases preserved |
| Ambiguous | 13 | Evidence stops here |

The positive genes are TP53, BRCA2, KMT2D, DNAH5, CHD7, ANKRD11, TSC2, PKD1, CREBBP, and KMT2A. The clearly negative are BRCA1 and COL2A1. This is better than a selectively favorable panel because it shows where covariance helps, where it harms, and where it remains unresolved under a performance-blind rule.

The clinical-panel audit extracts a bounded operating regime from that heterogeneous space. Four of four positive-focus genes improve over the frozen scalar baseline. Twelve prioritized rescue candidates emerge. The story condenses into a five-case rescue gallery across three genes, TSC2, CREBBP, and GRIN2A, with one explicit BRCA1 anti-case (`BRCA1:C60G`) preserved rather than dropped.

The gallery cases are internally differentiated. `TSC2:G293R` is the clearest finalist with explicit extra-family support from ProtT5. `CREBBP:R1340P` carries moderate ProtT5 support and marginal ESM2-650M support. These surfaces matter later because they become part of the replay-ready portability story rather than remaining isolated gallery curiosities. The explicit anti-case shows a large negative margin and remains useful precisely because it does not fit the rescue pattern.

The structural bridge explains why the gallery is persuasive without pretending universality. Repair exemplars occupy denser wild-type structural neighborhoods than likelihood-driven references (median site contacts 9 versus 3). Even `BRCA1:G1737R`, an overall anti-case, sits in a locally dense neighborhood with site pLDDT 94.69 and 12 site contacts, showing that structural readiness alone is not sufficient for rescue. The gallery must keep explicit anti-cases because biology is not a single template.

### 5.5 Boundary Cases Are Part of the Result

MSH2 is the decisive negative replication. Against the five-model ESM-1v ensemble, the fixed augmented score falls from 0.9233 to 0.8457, the paired confidence interval is entirely negative, and the best full-surface α collapses to 0.00. This is not a near miss. It is the cleanest evidence that the BRCA2 stronger-baseline gain does not generalize as a universal recipe.

BRCA1 is the other crucial boundary, but its failure is structured rather than flat. Low-confidence subsets are mildly positive (+0.0107), the BRCT2 and RING domains are near-neutral to slightly positive (+0.0049 and +0.0039), while high-confidence and expert-panel strata are more strongly negative (-0.0579). BRCA1 functions as an anti-case with internal structure, not as simple disproof.

The 192-configuration protocol sweep reinforces this interpretation. Smaller windows and shallower layer subsets often outperform the canonical 40/all_layers setting. BRCA2 remains positive across 150M, 650M, and 3B. BRCA1 moves from slightly negative under the canonical setting to near-neutral under some smaller-window protocols. The correct interpretation is not monotone scaling and not uniform transfer. It is checkpoint-, window-, layer-, and gene-sensitive behavior.

### 5.6 The Rulebook Condenses Wins into a Bounded Operating Regime

The block-11 rulebook scores cases along five axes: scalar under-reaction, structural readiness, chemistry trigger, α stability, and cross-model confirmation. On a decision panel of 5 positive and 5 explicit negative cases, it produces a score gap of 3.600, a recommended positive fraction of 0.800, a recommended negative fraction of 0.000, and an odds ratio of 121 at score ≥ 2. The signal is not random anecdote; it clusters inside a partially compressible operating regime.

Even on hand-picked finalists, the mean case-level α-positive fraction is only 0.226, and two-family support reaches only 0.200. The rulebook is operating-regime condensation, not proof of robust cross-family closure.

The orthogonal TP53 validation asks whether a portable version of that regime survives on a fresh live surface. The best model is ESM-1v, with pair AUC 0.8073 and pair-versus-likelihood Δ +0.1248. But the portable rule does not close as universal enrichment, and the aggregate readout remains model-sensitive. ProtT5 is negative in this orthogonal pass (Δ -0.0410, best α 0.0). The rulebook survives but does not universalize.

### 5.7 Earlier Harsh Firewalls: Multifamily Breadth, Adjudication, and Localization

The first late adjudication chain asks the hardest pre-Block-13 version of the question: if the signal is real, does it close as a covariance-native, cross-model, control-aware law? The answer is no. But the way it fails is scientifically informative.

The multifamily stage finds real family breadth across 10 models and 5 positive families (positive family count = 5), yet records 0 structural-positive models, 0 control wins, and 0 holdout-positive models under the strictest earlier filters. The correct interpretation is **supportive breadth**, not nuclear generalization.

Covariance adjudication removes scalar escape routes and adds structural closure plus BRCA1 transfer pressure. Ten models are adjudicated. Six remain supportive. Zero become nuclear. Zero are transfer-positive at the model-level adjudication standard used there. The unresolved table reveals that several models collapse to scalar-only or fail scalar-matched controls. That is why the older chain stopped at supportive rather than nuclear.

The final localization pass narrows further. `ProGen2-small` becomes the only `supportive_localized` model and the cleanest covariance-native witness. The final localized nuclear candidate set is empty. The earlier ending is therefore scientifically sharper, not weaker: the paper names the strongest non-ESM witness and still refuses to overclaim.

| Earlier harsh adjudication surface | Main result | Interpretation |
|---|---|---|
| Block-12 orthogonal TP53 | Best model pair AUC 0.8073; portable-rule enrichment mixed | Orthogonal support, model-sensitive |
| Block-12B multifamily | Positive family count 5; 0 structural-positive; 0 control wins | Breadth is real, not closed |
| Block-12C covariance adjudication | 6 supportive, 0 nuclear, 0 model-level transfer-positive | Strengthens under firewalls, does not close |
| Block-12D final localization | 1 supportive localized witness, 0 nuclear localized models | Stops at localized supportive |

### 5.8 Replay-Ready Multi-Target Portability

Block 13 materially strengthens the generalization story. The claim status is `multitarget_generalization_strengthened_but_not_fully_closed`, and the wording is earned. The project is no longer only a TP53/BRCA2-centered bounded story. It now supports a replay-ready multi-target regime with four frozen portability surfaces: `TP53`, `BRCA2`, `TSC2`, and `CREBBP`.

The key distinction is target-level rather than universal model-level closure. `TSC2` and `CREBBP` are the decisive additions because they break the old two-gene bottleneck. Both become transfer-positive targets under the Block 13 portability framing, while `TP53` and `BRCA2` remain replay-ready anchors. This does not erase the older harsh-firewall failures. It shows that portability can be frozen across multiple public targets before the harshest tribunal is imposed.

The negative surfaces also survive the strengthening pass. `BRCA1` and `MSH2` remain explicit guardrails rather than being removed from view. That matters because the new portability claim is stronger precisely because it is not achieved by laundering away failure. The reviewer-facing interpretation is simple: multi-target portability is now real enough to freeze, inspect, and replay, but still not broad enough to universalize.

| Block-13 portability surface | Main result | Interpretation |
|---|---|---|
| Replay-ready targets | `TP53`, `BRCA2`, `TSC2`, `CREBBP` | Public multi-target replay is now concrete |
| Transfer-positive targets | `TSC2`, `CREBBP` | Portability is no longer confined to TP53 and BRCA2 |
| Negative guardrails | `BRCA1`, `MSH2` preserved | Strengthening did not depend on deleting failures |
| Claim status | `multitarget_generalization_strengthened_but_not_fully_closed` | Raised ceiling, still not full closure |

### 5.9 Final Holdout/Control Closure Tribunal

Block 14 asks the harshest version of the remaining question. It repairs the earlier holdout degeneracy and control self-blocking, then reruns the closure tribunal on full labeled holdout targets. The corrected rerun does **not** fail merely because of a technical bug. Its final claim status remains `closure_still_mixed`.

The numbers at this stage are intentionally unforgiving: `holdout_positive_models = []`, `control_win_models = []`, and `transfer_positive_models = []`. The negative-guardrail ledger is not clean either (`negative_guardrails_clean = false`). Once the closing standard is defined at the model-level holdout-and-control tribunal, the paper still does not close as a fully transferable covariance-native law.

This does not cancel Block 13. It clarifies the level at which the new portability result lives. Block 13 is a target-level replay-ready strengthening result. Block 14 is a model-level closure tribunal. The former is positive and materially new; the latter remains mixed. That distinction is the correct final stopping point for the manuscript.

| Block-14 closure surface | Main result | Interpretation |
|---|---|---|
| Claim status | `closure_still_mixed` | Harshest closure does not fully close |
| Holdout-positive models | `[]` | No model clears the holdout firewall |
| Control-win models | `[]` | No model clears the repaired control tribunal |
| Transfer-positive models | `[]` | No model achieves harsh model-level transfer closure |
| Negative guardrails clean | `false` | Overclaim remains blocked |

## 6. Discussion

The combined evidence now supports a stronger interpretation than earlier versions could justify. The main claim is still not that covariance is a universal upgrade. It is that **local hidden-state covariance is a real, auditable perturbation signal** that can improve a stronger external baseline on the right surface, reveal a concrete representational failure mode that scalar likelihood does not expose, and extend beyond a two-gene story into replay-ready multi-target portability without surviving the harshest universalization tribunal.

BRCA2 remains central because it answers the strongest simple objection. If covariance only helped because the baseline was weak, the gain should disappear against the five-model ESM-1v ensemble. It does not. The augmentation survives paired uncertainty and permutation falsification, and BRCA2 alone satisfies the benchmark-promotion rule. BRCA2 is not merely a nice supporting example. It is the flagship quantitative result and the clearest answer to the baseline-strength critique.

TP53 matters for a different reason. It keeps the paper from becoming a single-gene BRCA2 story. The frozen replay gives the covariance claim a challengeable public anchor. The nested audit shows the released weight is a plateaued operating point. The repaired structural dissociation provides the cleanest mechanistic separation (0.309 versus 0.036). The division of labor is deliberate: BRCA2 asks whether covariance can matter against a strong baseline; TP53 asks whether the underlying signal is real, reproducible, and structurally meaningful.

The performance-blind breadth layers change the paper in another way. The support-ranked top-25 panel does not rescue universal transfer; it prevents the manuscript from hiding behind hand-picked examples. The clinical panel and rescue gallery show that heterogeneity can become bounded case-level evidence without laundering away failures. This is one of the manuscript's strongest choices: `BRCA1:C60G` and the broader BRCA1 surface are preserved as explicit anti-cases.

That choice matters mechanistically. `BRCA1:G1737R` lives in a dense local neighborhood that looks structurally ready for rescue, yet the broader BRCA1 surface remains negative. Such cases prevent the reader from collapsing the method into a single easy rule like "high local structure density implies covariance gain."

The scale-repair chain is the most distinctive qualitative result because it shows covariance doing something other than raising AUC. In the `to_basic` and high-disagreement regime, ESM2-150M overstates covariance disruption and ESM2-650M largely repairs it. The repair survives matched-pair audit, survives stricter same-position sister-substitution follow-up, and remains covariance-specific rather than appearing in scalar likelihood. Covariance functions here as a **representational audit instrument**, not merely a ranking ingredient.

The late-stage portability evidence is what materially changes the mature version of the paper. The project no longer rests on TP53 and BRCA2 alone. Block 13 freezes four replay-ready targets and promotes `TSC2` and `CREBBP` into genuine transfer-positive targets. That is not universal closure, but it is also not a merely local supportive hint. It is public multi-target portability with explicit contracts.

`TSC2` and `CREBBP` matter precisely because they break the old two-gene bottleneck. They show that the covariance signal can be replayed on new labeled targets without pretending that every model, every family, or every transfer tribunal has closed. `BRCA1` and `MSH2` matter just as much because they prevent the portability story from turning into selection bias.

Block 14 then does a different job. It is valuable not because it rescues the claim, but because it does not. After repairing the degenerate holdout and self-blocking control logic, the harshest final tribunal still remains mixed. No model clears holdout-positive closure; no model clears control-win closure; and the negative-guardrail ledger does not come back clean. That failure is scientifically useful. It tells the reader exactly which kind of generalization the paper has and which kind it does not.

The broader implication is not immediate deployment but **benchmarking culture**. Zero-shot variant scoring should not treat scalar likelihood as the only internal readout worth auditing. The comparison set is richer: scalar likelihood, covariance-native summaries, covariance-plus-likelihood blends, stronger-baseline augmentations, performance-blind regime screens, structural dissociation tests, replay-ready multi-target surfaces, and final tribunals that explicitly ask whether portability survives holdout and control pressure. SpectralBio does not settle that agenda, but it shows that covariance deserves a place inside it.

The reproducibility story matters because it makes the bounded claim inspectable. A frozen public TP53 replay, machine-readable verification artifacts, and release-grade target contracts do not replace scientific evidence. They make the evidence harder to hand-wave away. The paper's core virtue is therefore not only that it found a real signal, but that it made that signal **unusually challengeable while still surviving substantial criticism**.

## 7. Limitations and Non-Claims

The public story is no longer only one canonical target plus bounded supporting evidence. The project now has replay-ready multi-target evidence across `TP53`, `BRCA2`, `TSC2`, and `CREBBP`, and it contains two transfer-positive targets (`TSC2`, `CREBBP`). But this improvement does not erase the remaining closure limits. The harshest holdout/control tribunal still fails to close.

The manuscript is primarily ClinVar-based. The breadth surfaces are not orthogonal functional benchmarks in the sense of deep mutational scanning, and ClinVar itself is noisy, heterogeneous, and partly circular. Those limitations do not explain same-surface paired results such as the BRCA2 gain or the covariance-specific scale-repair audits, but they limit clinical interpretation.

The stronger-baseline story is real but gene-dependent. BRCA2 is clean positive. TP53 is a structural and validation anchor, not a stronger-baseline flagship. MSH2 is decisively negative with best α 0.0. BRCA1 remains a structured anti-case rather than a trivial miss. The scale-repair result lives in a narrow chemistry-defined regime, remains concentrated inside the ESM2 family, and is chemically asymmetric even after the stricter sister-substitution control.

The late adjudication chain now has two different stopping points. The earlier harsh firewalls reach supportive rather than nuclear. The late-stage portability evidence strengthens that into replay-ready multi-target portability. The final holdout/control tribunal then shows that full holdout/control closure still fails. The strongest honest claim is therefore **materially improved breadth with incomplete closure**.

The method is not optimized for cheapest-possible scoring. Covariance extraction is more expensive than scalar likelihood, and we do not argue that every pipeline should pay that cost. The narrower claim is that covariance is worth paying for on bounded offline benchmark and audit surfaces when the goal is representational diagnosis, stronger-baseline testing, or replay-ready portability assessment.

These limitations imply concrete non-claims. We do not claim universal generalization, full closure, a cross-protein law, model-family-wide closure, universal α transfer, monotone scaling with larger checkpoints, or superiority to every external predictor on a shared benchmark. We claim a bounded but stronger result: a real, auditable signal with replay-ready multi-target portability that still stops short of universal closure.

## 8. Benchmark Extension Path

The benchmark-extension story is no longer only about one next candidate. Under the predeclared promotion rule, BRCA2 remains the flagship non-anchor benchmark target: its paired lower confidence bound is positive, its nested fixed-0.55 mean AUC exceeds nested likelihood, and it retains enough support to matter as a public surface. That still makes BRCA2 the correct next target for full canonicalization.

A public BRCA2 benchmark would need the same release-grade contract that made TP53 challengeable: frozen sequence reference, frozen benchmark table, score references, manifests, expected metrics, and machine-checkable verification outputs. For full parity with the flagship claim, the BRCA2 augmentation and permutation analyses should also be exposed as first-class public audit surfaces.

But the extension path is now broader than BRCA2 alone. BRCA2 remains the next full canonicalization target under the benchmark-promotion rule, whereas `TSC2` and `CREBBP` now qualify as replay-ready transfer surfaces rather than flagship canonical benchmark centerpieces. They matter because they establish a **multi-target benchmark family** rather than a single-target extension queue. The right near-term agenda is therefore two-tiered: canonicalize BRCA2 as the strongest next flagship surface, and preserve `TSC2` and `CREBBP` as replay-ready transfer surfaces that stress portability beyond the anchor genes.

Beyond those targets, the right question is not "which other gene looks favorable?" It is **"which gene properties govern when covariance helps, hurts, remains replay-ready, or fails the final holdout/control tribunal?"** The top-25 panel, clinical panel, BRCA1 anti-case, MSH2 non-replication, Block 13 portability audit, and Block 14 closure tribunal together turn that into a concrete benchmark agenda.

## 9. Conclusion

SpectralBio supports a bounded but stronger conclusion than earlier versions could justify. Local hidden-state covariance carries real zero-shot pathogenicity signal that scalar likelihood does not exhaust. On BRCA2, that signal survives the strongest baseline used in the paper, improving a five-model ESM-1v ensemble from 0.6324 to 0.6890, with paired gain 0.0566, bootstrap interval [0.0131, 0.1063], and covariance-permutation *p* = 0.0010.

The paper's most distinctive qualitative contribution is different. In a performance-blind high-covariance basic-substitution regime, ESM2-150M overstates covariance disruption relative to matched controls, while ESM2-650M largely repairs that error pattern. The repair survives matched-pair audit, survives stricter same-position sister-substitution follow-up, and remains covariance-specific rather than appearing in scalar likelihood. Covariance is not only a ranking ingredient here. It is an audit readout for a concrete representational failure mode.

The rest of the evidence now tells a stronger but still disciplined story about portability. TP53 provides the frozen public anchor and the strongest mechanistic separation (0.309 versus 0.036). BRCA2 provides the flagship stronger-baseline win. The support-ranked top-25 panel, clinical panel, and rescue gallery show that breadth is real but heterogeneous. `BRCA1:C60G` and the broader BRCA1 surface preserve failure inside the paper rather than outside it. MSH2 demonstrates that stronger-baseline gains can fail decisively.

The late-stage program no longer ends where the earlier supportive-not-nuclear chain ended. Block 13 adds replay-ready multi-target portability across four targets (`TP53`, `BRCA2`, `TSC2`, `CREBBP`) and promotes two transfer-positive targets (`TSC2`, `CREBBP`). That is a material strengthening of the generalization story because it breaks the old TP53/BRCA2 bottleneck while preserving `BRCA1` and `MSH2` as explicit negative guardrails.

Block 14 then supplies the final discipline. Even after repairing the holdout and control logic, the harshest final closure tribunal remains mixed: no holdout-positive model, no control-win model, no harsh model-level transfer closure, and no clean negative-guardrail ledger. That stopping point is part of the contribution. The paper does not end in universal closure. It ends in the strongest honest formulation the data support: **a falsifiable, auditable, gene-dependent signal that can improve a strong external baseline, track local structural strain better than likelihood alone, reveal a concrete scale-repair failure mode inside a major protein-language-model family, and support replay-ready multi-target portability without closing as a universal law.**

TP53 gives that claim its public validation anchor. BRCA2 gives it its flagship benchmark result. `TSC2` and `CREBBP` give it multi-target portability beyond the old two-gene bottleneck. BRCA1 and MSH2 give it guardrails. The final tribunal gives it discipline. Together, those pieces make a stronger paper than either a single benchmark win or a looser universalization attempt.

---

## References

1. Lin, Z., Akin, H., Rao, R., et al. *Evolutionary-scale prediction of atomic-level protein structure with a language model.* Science 379(6637), 1123-1130 (2023).

2. Meier, J., Rao, R., Verkuil, R., Liu, J., Sercu, T., and Rives, A. *Language models enable zero-shot prediction of the effects of mutations on protein function.* NeurIPS 34 (2021).

3. Frazer, J., Notin, P., Dias, M., et al. *Disease variant prediction with deep generative models of evolutionary data.* Nature 599, 91-95 (2021).

4. Ng, P. C., and Henikoff, S. *SIFT: predicting amino acid changes that affect protein function.* Nucleic Acids Research 31(13), 3812-3814 (2003).

5. Adzhubei, I. A., Schmidt, S., Peshkin, L., et al. *A method and server for predicting damaging missense mutations.* Nature Methods 7, 248-249 (2010).

6. Elnaggar, A., Heinzinger, M., Dallago, C., et al. *ProtTrans: Toward Understanding the Language of Life Through Self-Supervised Learning.* IEEE TPAMI 44(10), 7112-7127 (2022).

7. Landrum, M. J., Lee, J. M., Benson, M., et al. *ClinVar: improving access to variant interpretations and supporting evidence.* Nucleic Acids Research 46(D1), D1062-D1067 (2018).

8. Notin, P., Dias, M., Frazer, J., et al. *ProteinGym: Large-scale benchmarks for protein fitness prediction and design.* NeurIPS 36 (2023).

9. Rives, A., Meier, J., Sercu, T., et al. *Biological structure and function emerge from scaling unsupervised learning to 250 million protein sequences.* PNAS 118(15), e2016239118 (2021).

10. Brandes, N., Ofer, D., Peleg, Y., et al. *ProteinBERT: a universal deep-learning model of protein sequence and function.* Bioinformatics 38(8), 2102-2110 (2022).

11. Riesselman, A. J., Ingraham, J. B., and Marks, D. S. *Deep generative models of genetic variation capture the effects of mutations.* Nature Methods 15, 816-822 (2018).

12. Livesey, B. J., and Marsh, J. A. *Using deep mutational scanning to benchmark variant effect predictors and identify disease mutations.* Molecular Systems Biology 16(7), e9380 (2020).

13. Kotler, E., Shani, O., Goldfeld, G., et al. *A systematic p53 mutation library links differential functional impact to cancer mutation pattern and evolutionary conservation.* Molecular Cell 71(1), 178-190.e8 (2018).

14. Findlay, G. M., Daza, R. M., Martin, B., et al. *Accurate classification of BRCA1 variants with saturation genome editing.* Nature 562, 217-222 (2018).

15. Morcos, F., Pagnani, A., Lunt, B., et al. *Direct-coupling analysis of residue coevolution captures native contacts across many protein families.* PNAS 108(49), E1293-E1301 (2011).

16. Katsonis, P., and Lichtarge, O. *A formal perturbation equation between genotype and phenotype determines the Evolutionary Action of protein-coding variations on fitness.* Genome Research 24(12), 2050-2058 (2014).

17. Jumper, J., Evans, R., Pritzel, A., et al. *Highly accurate protein structure prediction with AlphaFold.* Nature 596, 583-589 (2021).

18. Rao, R., Meier, J., Sercu, T., Ovchinnikov, S., and Rives, A. *Transformer protein language models are unsupervised structure learners.* ICLR (2021).

19. Hsu, C., Verkuil, R., Liu, J., Lin, Z., Hie, B., Sercu, T., Lerer, A., and Rives, A. *Learning inverse folding from millions of predicted structures.* PMLR 162, 8946-8970 (2022).

20. Ghorbani, A., and Zou, J. *Neuron Shapley: Discovering the Responsible Neurons.* NeurIPS 33 (2020).

---

## Artifact Links

| Surface | Role |
|---|---|
| Repository root | Primary code and manuscript surface |
| TP53 canonical `summary.json` | Machine-readable validation-anchor metric surface |
| TP53 canonical `verification.json` | Machine-checkable replay and artifact verification surface |
| Truth contract | Claim boundary and precedence contract |
| Reproducibility notes | Canonical execution and verification semantics |
| Campaign manifest notebook | Campaign provenance and cache preparation |
| Baseline/alpha audit notebook | Stronger-baseline framing for BRCA2, TP53, and MSH2 |
| Failure-mode notebook | Discovery of the scale-repair regime |
| Cross-model notebook v2 | Family-bounded cross-model audit |
| Structure-bridge notebook | Early bounded bridge from covariance to structure |
| Clinical-panel notebook | Performance-blind bounded breadth and rescue prioritization |
| Structural dissociation notebook | Final TP53 structural readout |
| Rescue gallery notebook | Reviewer-facing rescue gallery plus explicit anti-case |
| Rulebook notebook | Bounded operating-regime condensation |
| Orthogonal TP53 notebook | Portable-rule test on a fresh TP53 surface |
| Multifamily notebook | Earlier coverage-aware supportive-not-nuclear breadth audit |
| Covariance adjudication notebook | Covariance-native adjudication under stricter firewalls |
| Final localization notebook | Earlier localization pass and supportive stopping point |
| Multi-target portability notebook | Replay-ready multi-target portability across TP53, BRCA2, TSC2, and CREBBP |
| Holdout/control tribunal notebook | Final harsh closure tribunal that remains mixed |
| Dataset | Public data surface for the study |
| Demo Space | Interactive public demonstration surface |
| SKILL | Cold-start reproduction and project-operating contract |
