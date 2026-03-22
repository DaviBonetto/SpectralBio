<h1 align="center">SpectralBio</h1>

<p align="center"><strong>Spectral Covariance Analysis of Protein Language Model Hidden States for Zero-Shot Variant Pathogenicity Prediction</strong></p>

<p align="center">
  <a href="paper/spectralbio.pdf">Paper</a> |
  <a href="#quick-start">Quickstart</a> |
  <a href="#key-results">Experiments</a> |
  <a href="https://huggingface.co/spaces/DaviBonetto/spectralbio-demo">Public API</a>
</p>

<p align="center">
  <a href="https://claw4s.github.io"><img src="https://img.shields.io/badge/CLAW4S-111827?style=flat-square" alt="CLAW4S" /></a>
  <a href="https://claw4s.github.io"><img src="https://img.shields.io/badge/2026%20STANFORD%20%26%20PRINCETON-b91c1c?style=flat-square" alt="2026 Stanford and Princeton" /></a>
  <a href="http://18.118.210.52"><img src="https://img.shields.io/badge/CLAWRXIV-111827?style=flat-square" alt="clawRxiv" /></a>
  <a href="http://18.118.210.52"><img src="https://img.shields.io/badge/PAPER%20ARCHIVE-f59e0b?style=flat-square" alt="Paper Archive" /></a>
  <a href="https://huggingface.co/spaces/DaviBonetto/spectralbio-demo"><img src="https://img.shields.io/badge/HUGGINGFACE-111827?style=flat-square" alt="HuggingFace" /></a>
  <a href="https://huggingface.co/spaces/DaviBonetto/spectralbio-demo"><img src="https://img.shields.io/badge/DEMO-facc15?style=flat-square&logo=huggingface&logoColor=111827" alt="Demo" /></a>
</p>

<p align="center">
  <a href="paper/spectralbio.pdf"><img src="https://img.shields.io/badge/READ%20FULL%20PAPER-111827?style=flat-square" alt="Read Full Paper" /></a>
  <a href="paper/spectralbio.pdf"><img src="https://img.shields.io/badge/PDF-f3f4f6?style=flat-square&logo=adobeacrobatreader&logoColor=b91c1c" alt="PDF" /></a>
  <a href="https://huggingface.co/spaces/DaviBonetto/spectralbio-demo"><img src="https://img.shields.io/badge/LAUNCH%20DEMO-111827?style=flat-square" alt="Launch Demo" /></a>
  <a href="https://huggingface.co/spaces/DaviBonetto/spectralbio-demo"><img src="https://img.shields.io/badge/HUGGINGFACE-facc15?style=flat-square" alt="HuggingFace" /></a>
  <a href="https://huggingface.co/datasets/DaviBonetto/spectralbio-clinvar"><img src="https://img.shields.io/badge/OPEN%20DATASET-111827?style=flat-square" alt="Open Dataset" /></a>
  <a href="https://huggingface.co/datasets/DaviBonetto/spectralbio-clinvar"><img src="https://img.shields.io/badge/HF%20DATASETS-facc15?style=flat-square" alt="HF Datasets" /></a>
</p>

<p align="center">
  <a href="https://huggingface.co/datasets/DaviBonetto/spectralbio-clinvar"><img src="paper/assets/hf_logo.png" alt="Hugging Face Official Logo" height="34" /></a>
</p>

<p align="center">
  <a href="http://18.118.210.52"><img src="huggingface/assets/clawRxiv_logo.png" alt="clawRxiv Logo" height="42" /></a>
</p>

<p align="center"><strong>Claw (AI Co-author) | Davi Bonetto</strong></p>

---

## Abstract

SpectralBio is a reproducible, zero-shot variant-effect pipeline for missense pathogenicity prediction from sequence alone. The method leverages `facebook/esm2_t30_150M_UR50D` and measures mutation-induced geometric perturbations in hidden-state covariance inside a local `±40` residue window. It combines spectral features with proper masked-LM evidence to improve ranking quality without supervised training.

On TP53 ClinVar (`N=255`, `115` pathogenic, `140` benign), the best pair (`0.55 * FrobDist + 0.45 * LL Proper`) reaches **AUC=0.7498 (~0.750)**. On BRCA1 transfer (`N=100` subset), **LL Proper reaches AUC=0.9174 (~0.917)**. Reproducibility is exact with fixed seeds (**Δrep=0.0**).

---

## Key Results

| Benchmark | Best Method | AUC-ROC | Interpretation |
|---|---|---:|---|
| TP53 (ClinVar, N=255) | `0.55*frob_dist + 0.45*ll_proper` | **0.7498** | Best pair in ablation search |
| BRCA1 transfer (N=100) | `ll_proper` | **0.9174** | Strong cross-protein generalization |

### Main empirical takeaways
- Matrix-level covariance features (`FrobDist`, `TraceRatio`) are consistently stronger than eigenvalue-only SPS variants on TP53.
- The best TP53 score is a hybrid geometric + probabilistic signal, not a single raw feature.
- `LL Proper` is moderate on TP53 but exceptionally strong on BRCA1 transfer.
- Reported reproducibility check remains exact (`Δrep=0.0`) with deterministic seeds.

![Results](colab/results/figures.png)

---

## Method (Brief)

For each variant, SpectralBio compares WT and MUT hidden-state covariance across ESM2 layers.

$$
\mathrm{FrobDist} = \frac{1}{L}\sum_{l=1}^{L}\left\|C_{\text{MUT}}^{(l)} - C_{\text{WT}}^{(l)}\right\|_F
$$

$$
\mathrm{TraceRatio} = \frac{1}{L}\sum_{l=1}^{L}\left|\frac{\mathrm{tr}\left(C_{\text{MUT}}^{(l)}\right)}{\mathrm{tr}\left(C_{\text{WT}}^{(l)}\right)} - 1\right|
$$

$$
\mathrm{SPS\text{-}log} = \frac{1}{L}\sum_{l=1}^{L}\left\|\log\left|\lambda_{\text{MUT}}^{(l)}\right| - \log\left|\lambda_{\text{WT}}^{(l)}\right|\right\|_2^2
$$

Where `C^(l)` is the residue-level covariance matrix at layer `l`, and `λ^(l)` is its eigenvalue spectrum.

Best TP53 combination in this release:

$$
\mathrm{Score}_{\text{best}} = 0.55\cdot\mathrm{FrobDist} + 0.45\cdot\mathrm{LL\ Proper}
$$

---

## Method Diagram (Pipeline Discussion)

![Method Diagram](huggingface/assets/method_diagram.png.png)

The diagram summarizes the end-to-end computational flow used in the paper:

1. **Variant ingestion:** TP53/BRCA1 ClinVar missense variants are filtered and normalized.
2. **Sequence-local encoding:** WT and MUT windows (`±40`) are encoded by ESM2-150M.
3. **Layerwise covariance:** per-layer residue covariance matrices are computed.
4. **Spectral descriptors:** `FrobDist`, `TraceRatio`, `SPS-log` quantify geometric perturbation.
5. **Likelihood integration:** proper masked-LM likelihood (`LL Proper`) is blended with spectral signals.
6. **Evaluation:** AUC ablations on TP53 and transfer analysis on BRCA1.

This is intentionally designed as an executable science pipeline: each block has a direct file-level artifact in this repository.

---

## Paper Discussion (Deep Dive)

### Why covariance geometry matters
Likelihood scores answer “how probable is this mutation under token prediction,” while covariance perturbation answers “how strongly did internal representation geometry shift.” In practice, those are complementary biological signals.

### Why the TP53 best score is a mixture
On TP53, no single feature dominates all decision boundaries. The top-performing rule is the weighted pair (`FrobDist + LL Proper`), indicating that geometric and probabilistic cues contribute non-redundant information.

### Why BRCA1 transfer is important
The BRCA1 result (`AUC=0.9174` for `LL Proper`) suggests cross-protein portability in the likelihood component. This is important for zero-shot settings where no supervised retraining is available.

### Current limitations
- Two-gene scope for this release (TP53 primary + BRCA1 transfer subset).
- Window size and feature mixing are fixed in this benchmark snapshot.
- Intended for research reproducibility, not clinical deployment.

### Feature-level interpretation from the TP53 ablation

| Feature | AUC-ROC (TP53) | Interpretation |
|---|---:|---|
| `ll_crude` | 0.7026 | Strong baseline proxy from hidden-state norm differences |
| `trace_ratio` | 0.6242 | Useful matrix-scale perturbation signal |
| `frob_dist` | 0.6209 | Stable global covariance displacement measure |
| `sps_log` | 0.5988 | Eigenvalue-only signal, weaker than matrix-level features |
| `ll_proper` | 0.5956 | Modest on TP53 but strongest transfer behavior on BRCA1 |

This ranking is exactly why SpectralBio keeps both geometric and probabilistic channels.
The top TP53 score comes from feature complementarity, while the top BRCA1 score comes
from transfer stability in `ll_proper`.

---

## Quick Start

### Option A (agents): `SKILL.md`
- Open `SKILL.md` at repository root.
- Execute each step sequentially.
- Runtime target: ~24 min on T4 GPU.

### Option B (humans): notebook
- Open [colab/spectralbio.ipynb](colab/spectralbio.ipynb).
- Run cells in order.
- Outputs are written to `colab/results/`.

---

## 🤖 For AI Agents (Reproduction-First)

### 1) Where to start
- Primary entrypoint: `SKILL.md`
- Notebook mirror: `colab/spectralbio.ipynb`
- Paper text: `paper/spectralbio.tex` and `paper/spectralbio_clawrxiv.md`

### 2) Minimal execution contract
- **Model:** `facebook/esm2_t30_150M_UR50D`
- **Seeds:** `42` (`torch`, `numpy`, `random`)
- **Core deps:** `torch`, `transformers`, `scipy`, `scikit-learn`, `numpy`
- **Expected key metrics:** TP53 ~`0.750`, BRCA1 LL ~`0.917`, `Δrep=0.0`

### 3) Agent navigation map

| If you need... | Open this path | What you get |
|---|---|---|
| Reproducible workflow | `SKILL.md` | Ordered execution steps and validation criteria |
| Raw TP53 variants | `colab/results/tp53_variants.json` | Curated benchmark variant list |
| Raw per-variant scores | `colab/results/scores.json` | 11-feature table for each TP53 variant |
| Final metric snapshot | `colab/results/summary.json` | AUCs, counts, timing, reproducibility delta |
| Visual diagnostics | `colab/results/figures.png` | ROC + ablation + distributions |
| Interactive demo code | `huggingface/app.py` | Space logic and scoring API |
| Dataset metadata | `huggingface/dataset_card.md` | Schema, splits, usage notes |
| Submission flow | `submit/submit.py` | clawRxiv publish script |

### 4) Output checklist after running
- `colab/results/summary.json` exists and contains TP53 + BRCA1 metrics.
- `colab/results/scores.json` exists and has TP53 rows with spectral/LL features.
- `colab/results/figures.png` exists and renders correctly.
- `reproducibility_delta` in summary remains `0.0`.

### 5) Submission notes for agents
- `submit/submit.py` expects local `submit/api_key.txt`.
- Never commit API keys.
- Publish target is clawRxiv (`http://18.118.210.52`).

### 6) 60-second bootstrap commands (agents)

```bash
git clone https://github.com/DaviBonetto/SpectralBio
cd SpectralBio
# Primary reproducibility path
# Follow SKILL.md step-by-step and validate outputs in colab/results/
```

### 7) Fast troubleshooting map

| Symptom | Likely cause | Fix |
|---|---|---|
| Equations or metrics not matching expected values | Seed drift or partial pipeline execution | Re-run with seeds fixed to `42` and execute full `SKILL.md` sequence |
| Missing `figures.png` or `scores.json` | Early stop before evaluation steps | Continue notebook/SKILL flow through final validation block |
| Submission script fails | Missing API key file | Create local `submit/api_key.txt` (never commit) |
| Slow runtime | CPU execution | Prefer T4/A100 runtime for expected wall-clock behavior |

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
- Window radius: `±40`
- Deterministic seeds: `42`
- TP53: `N=255`, `AUC_best_pair=0.7498`
- BRCA1 transfer subset: `N=100`, `AUC_ll_proper=0.9174`
- Reproducibility delta: `0.0`
- Scoring time: `~1447s` (~24 minutes)

---

## Links

- GitHub: [DaviBonetto/SpectralBio](https://github.com/DaviBonetto/SpectralBio)
- Demo: [Hugging Face Space](https://huggingface.co/spaces/DaviBonetto/spectralbio-demo)
- Dataset: [Hugging Face Dataset](https://huggingface.co/datasets/DaviBonetto/spectralbio-clinvar)
- Full paper PDF: [paper/spectralbio.pdf](paper/spectralbio.pdf)
- Claw4S 2026: [claw4s.github.io](https://claw4s.github.io)
- clawRxiv: [18.118.210.52](http://18.118.210.52)

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
