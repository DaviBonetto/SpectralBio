---
title: SpectralBio
emoji: 🧬
colorFrom: indigo
colorTo: gray
sdk: gradio
app_file: app.py
pinned: false
license: cc-by-4.0
python_version: "3.10"
models:
  - facebook/esm2_t30_150M_UR50D
datasets:
  - DaviBonetto/SpectralBio-ClinVar
tags:
  - biology
  - bioinformatics
  - proteins
  - clinvar
  - esm2
  - pathogenicity
  - executable-science
---

# SpectralBio

SpectralBio is a scientific demo for zero-shot missense variant pathogenicity prediction using spectral covariance analysis of ESM2 hidden states.

## What is inside this Space

- `Overview` tab with the paper framing, method diagram, results table, and figure panel
- `Try it` tab with live TP53 and BRCA1 variant analysis on top of `facebook/esm2_t30_150M_UR50D`
- `For AI Agents` tab with reproducibility notes, `SKILL.md`, and API usage examples
- Exact paper-facing v2 metrics:
  - TP53 best pair AUC: `0.7498`
  - BRCA1 zero-retraining AUC: `0.9174`
  - Reproducibility delta: `0.0`

## Scientific context

SpectralBio computes local hidden-state covariance matrices in a ±40 residue window around a mutation, derives spectral signals such as `FrobDist`, `TraceRatio`, and `SPS-log`, and combines them with `LL Proper` for zero-shot scoring.

The live UI presents the combined score as a TP53-reference percentile using the paper-confirmed formula:

```text
0.55 * frob_dist + 0.45 * ll_proper
```

## Links

- GitHub: [DaviBonetto/SpectralBio](https://github.com/DaviBonetto/SpectralBio)
- Dataset: [DaviBonetto/SpectralBio-ClinVar](https://huggingface.co/datasets/DaviBonetto/SpectralBio-ClinVar)
- clawRxiv: [clawrxiv.io](http://www.clawrxiv.io)
- SKILL.md: [SKILL.md](https://github.com/DaviBonetto/SpectralBio/blob/main/SKILL.md)
- Live Space: [DaviBonetto/spectralbio-demo](https://huggingface.co/spaces/DaviBonetto/spectralbio-demo)

## Reproducibility

```text
Seeds: 42 (PyTorch, NumPy, random)
Model: facebook/esm2_t30_150M_UR50D
Dataset: ClinVar FTP (public)
Runtime: ~1447s on NVIDIA T4
Delta_rep: 0.0 (exact)
```

## Programmatic use

The Space exposes a JSON API endpoint via Gradio:

```python
from gradio_client import Client

client = Client("DaviBonetto/spectralbio-demo")
result = client.predict("TP53", 174, "H", api_name="/score_variant")
print(result["combined_percentile"], result["label"])
```

## Notes

- Input positions in the live demo are `0`-indexed for agent reproducibility.
- Protein notation in the rendered output is mirrored back to standard `1`-indexed form.
- This Space is for research inspection and executable-science reproducibility, not clinical use.
