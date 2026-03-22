# 🧬 SpectralBio
### Spectral Covariance Analysis of Protein Language Model Hidden States for Zero-Shot Variant Pathogenicity Prediction

[![Claw4S 2026](https://img.shields.io/badge/Claw4S-2026%20Stanford%20%26%20Princeton-B1040E?style=for-the-badge)](https://claw4s.github.io)
[![clawRxiv](https://img.shields.io/badge/clawRxiv-Paper%20Archive-f97316?style=for-the-badge)](http://18.118.210.52)
[![HuggingFace Demo](https://img.shields.io/badge/HuggingFace-Demo-ffd21f?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/spaces/DaviBonetto/spectralbio-demo)
[![HuggingFace Dataset](https://img.shields.io/badge/HuggingFace-Dataset-ffcc4d?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/datasets/DaviBonetto/spectralbio-clinvar)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](./LICENSE)
![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)

[![clawRxiv Logo](huggingface/assets/clawRxiv_logo.png)](http://18.118.210.52)

**Claw 🦞 (AI Co-author) · Davi Bonetto**

---

## Abstract

SpectralBio is a reproducible, zero-shot variant-effect pipeline that evaluates whether missense mutations are pathogenic by measuring mutation-induced perturbations in the hidden-state geometry of `facebook/esm2_t30_150M_UR50D`. Instead of relying only on token likelihood, the method extracts spectral covariance descriptors in a local `±40` residue window and combines them with proper masked-LM evidence. On TP53 ClinVar (`N=255`, `115` pathogenic, `140` benign), the best pair (`0.55 * FrobDist + 0.45 * LL Proper`) reaches **AUC=0.7498 (~0.750)**. On BRCA1 transfer (`N=100` subset), **LL Proper reaches AUC=0.9174 (~0.917)**, with exact reproducibility (**Δrep=0.0**).

---

## Key Results

| Benchmark | Best Method | AUC-ROC | Notes |
|---|---|---:|---|
| TP53 (ClinVar, N=255) | `0.55*frob_dist + 0.45*ll_proper` | **0.7498** | Best pair in ablation search |
| BRCA1 (transfer, N=100) | `ll_proper` | **0.9174** | Zero-retraining cross-protein signal |

### Key findings
- Matrix-level covariance features (`FrobDist`, `TraceRatio`) consistently outperform eigenvalue-only SPS variants on TP53.
- The strongest TP53 performance is a hybrid geometric + probabilistic score, not a single feature.
- `LL Proper`, although moderate on TP53, generalizes strongly on BRCA1.
- Reproducibility check reports **Δrep=0.0** with fixed seeds (`42`) across `torch`, `numpy`, and `random`.

![Results](colab/results/figures.png)

---

## Quick Start

### Option A: Run `SKILL.md` (agent-first executable workflow)
- Open the root `SKILL.md`.
- Execute each step sequentially (dependency install, ClinVar filtering, ESM2 scoring, evaluation, transfer test, validation).
- Expected runtime: ~24 minutes on T4 (longer on CPU).

### Option B: Run `colab/spectralbio.ipynb` (human notebook workflow)
- Open [colab/spectralbio.ipynb](colab/spectralbio.ipynb).
- Run all cells in order.
- Exported artifacts are written to `colab/results/`.

---

## 🤖 For AI Agents

### Using SKILL.md
The `SKILL.md` at the root of this repository is the primary executable workflow.  
It is a self-contained, step-by-step pipeline that any AI agent can execute  
without external scripts or dependencies beyond pip packages.

### Key Information for Agents
- **Model:** facebook/esm2_t30_150M_UR50D (150M params, 30 layers)
- **Seeds:** 42 (torch, numpy, random) — exact reproducibility
- **Runtime:** ~24 min on T4 GPU
- **Expected AUC:** 0.750 (TP53), 0.917 BRCA1 LL
- **Zero dependencies** beyond: torch, transformers, scipy, sklearn, numpy

### Results Location
After running SKILL.md, results will be in:
- `colab/results/summary.json` — key metrics
- `colab/results/scores.json` — per-variant feature scores (11 features × N variants)
- `colab/results/figures.png` — ROC curves and ablation plots

### Competition Submission
Use `submit/submit.py` to submit to clawRxiv.  
Requires `submit/api_key.txt` (not tracked in git).

---

## Method (Brief)

For each variant, SpectralBio compares WT vs MUT ESM2 hidden-state covariance across layers:

\[
\mathrm{FrobDist} = \frac{1}{L}\sum_{l=1}^{L}\left\|C^{(l)}_{MUT} - C^{(l)}_{WT}\right\|_F
\]

\[
\mathrm{TraceRatio} = \frac{1}{L}\sum_{l=1}^{L}\left|\frac{\mathrm{tr}(C^{(l)}_{MUT})}{\mathrm{tr}(C^{(l)}_{WT})} - 1\right|
\]

\[
\mathrm{SPS\text{-}log} = \frac{1}{L}\sum_{l=1}^{L}\left\|\log\left|\lambda^{(l)}_{MUT}\right| - \log\left|\lambda^{(l)}_{WT}\right|\right\|_2^2
\]

Where `C^(l)` is the residue-level covariance matrix of hidden states at layer `l`, and `λ^(l)` is its eigenvalue spectrum.

The best TP53 scoring rule in this project snapshot is:

\[
\mathrm{Score}_{best} = 0.55 \cdot \mathrm{FrobDist} + 0.45 \cdot \mathrm{LL\ Proper}
\]

---

## Project Structure

```text
SpectralBio/
├── README.md
├── LICENSE
├── .gitignore
├── SKILL.md
├── Claw4S_conference.md
├── colab/
│   ├── spectralbio.ipynb
│   └── results/
│       ├── tp53_variants.json
│       ├── tp53_sequence.txt
│       ├── summary.json
│       ├── scores.json
│       └── figures.png
├── paper/
│   ├── spectralbio.tex
│   ├── spectralbio.pdf
│   ├── spectralbio_clawrxiv.md
│   ├── references.bib
│   └── assets/
├── submit/
│   └── submit.py
└── huggingface/
    ├── app.py
    ├── dataset_card.md
    ├── requirements.txt
    ├── README.md
    ├── assets/
    └── data/
```

---

## Reproducibility Snapshot

- Model: `facebook/esm2_t30_150M_UR50D`
- Window: `±40` residues around mutation site
- Deterministic seeds: `42`
- TP53: `N=255`, `AUC_best_pair=0.7498`
- BRCA1 subset: `N=100`, `AUC_ll_proper=0.9174`
- Reproducibility delta: `0.0`
- Timing: `~1447s` scoring stage (~24 min)

---

## Links

- GitHub: [DaviBonetto/SpectralBio](https://github.com/DaviBonetto/SpectralBio)
- Hugging Face Demo: [spectralbio-demo](https://huggingface.co/spaces/DaviBonetto/spectralbio-demo)
- Hugging Face Dataset: [spectralbio-clinvar](https://huggingface.co/datasets/DaviBonetto/spectralbio-clinvar)
- Claw4S 2026: [claw4s.github.io](https://claw4s.github.io)
- clawRxiv: [18.118.210.52](http://18.118.210.52)

---

## Repository Hygiene

- Sensitive file `submit/api_key.txt` is excluded from version control.
- Build/runtime noise is ignored (`__pycache__/`, notebook checkpoints, env folders).
- Compressed raw archives (`*.txt.gz`) are ignored by default.
- Orchestration artifacts (`plano/`, `ultra_plan.md`) are excluded.

---

## Citation

```bibtex
@inproceedings{claw2026spectralbio,
  title={SpectralBio: Spectral Covariance Analysis of Protein Language Model Hidden States for Zero-Shot Variant Pathogenicity Prediction},
  author={Claw and Bonetto, Davi},
  booktitle={Claw4S Conference 2026, Stanford--Princeton},
  year={2026}
}
```

---

## License

MIT License.

---

## Acknowledgments

- Claw4S 2026 organizers
- Stanford University
- Princeton University
- Meta AI (ESM2)
- ClinVar (NCBI/FDA)
