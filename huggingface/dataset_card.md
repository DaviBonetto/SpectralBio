---
license: cc-by-4.0
pretty_name: SpectralBio ClinVar Variants
size_categories:
  - n<1K
task_categories:
  - text-classification
task_ids:
  - multi-class-classification
annotations_creators:
  - expert-generated
language_creators:
  - expert-generated
language:
  - en
multilinguality:
  - monolingual
source_datasets:
  - original
tags:
  - biology
  - bioinformatics
  - proteins
  - clinvar
  - pathogenicity
  - variant-effect-prediction
  - executable-science
  - claw4s
configs:
  - config_name: tp53
    data_files:
      - split: train
        path: tp53_variants.json
  - config_name: brca1
    data_files:
      - split: train
        path: brca1_variants.json
  - config_name: combined
    data_files:
      - split: train
        path:
          - tp53_variants.json
          - brca1_variants.json
---

# SpectralBio ClinVar Variants

## Overview

SpectralBio ClinVar Variants is a compact, agent-friendly benchmark of filtered ClinVar missense variants for two clinically important genes:

- `TP53`: the primary evaluation split used in the current SpectralBio proof-of-concept
- `BRCA1`: a secondary split prepared with the same filtering logic for transfer and generalization tests

This repository was assembled for the SpectralBio executable research workflow in the Claw4S 2026 setting. In that setting, a paper is paired with a runnable `SKILL.md` so another agent can reproduce the pipeline end to end instead of only reading a static description.

## Why This Dataset Exists

SpectralBio studies whether hidden-state geometry from a protein language model can help distinguish pathogenic from benign missense variants in a zero-shot setting. The dataset is intentionally simple:

- plain JSON files
- one record per deduplicated amino-acid substitution
- labels collapsed to a binary decision
- enough metadata to reconstruct a human-readable mutation string
- small enough to inspect directly, but structured enough for automated workflows

That design makes it useful for:

- agent execution in `SKILL.md` pipelines
- quick notebook experiments
- lightweight Hugging Face Spaces demos
- reproducibility packages submitted to executable-science settings
- conversion into Arrow, Parquet, or `datasets.Dataset`

## What Is In This Repository

| File | Role | Rows | Pathogenic | Benign | Notes |
|------|------|-----:|-----------:|-------:|-------|
| `tp53_variants.json` | TP53 primary split | 255 | 115 | 140 | Main benchmark split used in the current proof-of-concept run |
| `brca1_variants.json` | BRCA1 secondary split | 512 | 165 | 347 | Same construction logic, intended for transfer or generalization experiments |
| `analysis/summary.json` | Evaluation metadata | 1 | - | - | Snapshot of the current TP53 run and BRCA1 evaluation subset |
| `analysis/results.png` | Evaluation figure | 1 | - | - | ROC and distribution plot from the current TP53 run |
| `analysis/tp53_spectral_scores.json` | Per-variant outputs | 255 | - | - | TP53 proof-of-concept spectral scores aligned with the current analysis snapshot |

Combined label count across the two JSON files: **767 missense variants**.

## Data Configurations On The Hub

The README metadata defines three Hub-friendly configurations:

- `tp53`: loads `tp53_variants.json`
- `brca1`: loads `brca1_variants.json`
- `combined`: loads both JSON files into one train split

If the Hub auto-loader is active for this repository, you can use:

```python
from datasets import load_dataset

tp53 = load_dataset("DaviBonetto/spectralbio-clinvar", "tp53")
brca1 = load_dataset("DaviBonetto/spectralbio-clinvar", "brca1")
combined = load_dataset("DaviBonetto/spectralbio-clinvar", "combined")
```

If you prefer explicit local parsing, the JSON files are also easy to load directly with standard Python.

## Construction Pipeline

### Source

- **ClinVar** (NCBI and FDA): [https://ftp.ncbi.nlm.nih.gov/pub/clinvar/](https://ftp.ncbi.nlm.nih.gov/pub/clinvar/)
- Download snapshot used for this release: **March 2026**

### Filtering Logic

Each retained record satisfies all of the following:

1. Gene symbol is `TP53` or `BRCA1`
2. Variant type is a single nucleotide missense event
3. Clinical significance is one of:
   - `Pathogenic`
   - `Likely pathogenic`
   - `Benign`
   - `Likely benign`
4. Variants with uncertain, conflicting, or VUS-style labels are excluded
5. Variants are deduplicated within each gene split by `(position, mut_aa)`

### Label Convention

- `label = 1` means `Pathogenic` or `Likely pathogenic`
- `label = 0` means `Benign` or `Likely benign`

This deliberately collapses ClinVar nuance into a benchmark-friendly binary target.

## Schema

| Field | Type | Description |
|-------|------|-------------|
| `gene` | string | Gene symbol, currently `TP53` or `BRCA1` |
| `wt_aa` | string | Wild-type amino acid in one-letter code |
| `position` | int | **0-indexed** amino-acid position in the canonical protein sequence |
| `mut_aa` | string | Mutant amino acid in one-letter code |
| `label` | int | Binary label: `1` pathogenic, `0` benign |
| `name` | string | ClinVar-derived variant string retained for provenance and human-readable mutation recovery |

## Dataset Contract For Agents

If you are another agent consuming this repository, the main operational rules are:

```yaml
repo_id: DaviBonetto/spectralbio-clinvar
configs:
  - tp53
  - brca1
  - combined
record_format: flat JSON objects
position_indexing: 0-based
rendered_variant_rule: "{wt_aa}{position + 1}{mut_aa}"
label_meaning:
  1: pathogenic_or_likely_pathogenic
  0: benign_or_likely_benign
deduplication_key:
  - gene
  - position
  - mut_aa
provenance_field: name
gold_labels_location:
  - tp53_variants.json
  - brca1_variants.json
analysis_files_are_labels: false
```

### Practical Notes For Agents

- The dataset ships as JSON lists, not as a custom loading script.
- `position` is 0-based in the files, but most biological notation is 1-based.
- To display a familiar mutation label, use `f"{wt_aa}{position + 1}{mut_aa}"`.
- `name` is a provenance field and should not be treated as the primary key.
- The `analysis/*` files are convenience artifacts from the current proof-of-concept run, not the source of truth for labels.

## Example Records

```json
[
  {
    "gene": "TP53",
    "wt_aa": "R",
    "position": 174,
    "mut_aa": "H",
    "label": 1,
    "name": "NM_000546.6(TP53):c.524G>A (p.Arg175His)"
  },
  {
    "gene": "BRCA1",
    "wt_aa": "C",
    "position": 60,
    "mut_aa": "G",
    "label": 1,
    "name": "NM_007294.4(BRCA1):c.181T>G (p.Cys61Gly)"
  }
]
```

## Quick Usage

### Plain Python

```python
import json

with open("tp53_variants.json", "r", encoding="utf-8") as f:
    tp53 = json.load(f)

print(len(tp53))
print(tp53[0])
print(f"Rendered mutation: {tp53[0]['wt_aa']}{tp53[0]['position'] + 1}{tp53[0]['mut_aa']}")
```

### Hugging Face Datasets From Raw JSON

```python
import json
from datasets import Dataset

with open("tp53_variants.json", "r", encoding="utf-8") as f:
    tp53 = Dataset.from_list(json.load(f))

with open("brca1_variants.json", "r", encoding="utf-8") as f:
    brca1 = Dataset.from_list(json.load(f))

print(tp53.features)
print(brca1.num_rows)
```

## Included Analysis Snapshot

This repository also includes the current proof-of-concept evaluation artifacts from the SpectralBio project. The exact values are stored in `analysis/summary.json`. In the current release:

- TP53 evaluation size: `255`
- TP53 SPS AUC: `0.5611`
- TP53 combined SPS plus likelihood AUC: `0.7074`
- BRCA1 evaluation subset size in the summary snapshot: `100`
- Reported reproducibility delta: `0.0`

These files are included for provenance and reproducibility. They should not be confused with a production-ready clinical benchmark.

## Recommended Uses

- Zero-shot variant-effect prediction experiments
- Reproducible Claw4S or `SKILL.md` workflows
- Agent-oriented benchmark construction and prompt grounding
- Lightweight educational demos for protein language models
- Data conversion into tabular, Arrow, or Parquet formats

## Limitations

- Only two genes are included in this release.
- Labels are intentionally binary and collapse ClinVar nuance.
- No VUS, uncertain, or conflicting variants are included.
- This is a research dataset, **not** a clinical decision-support product.
- The dataset is small and interpretable by design, not a comprehensive genome-wide benchmark.
- The included scores and figures reflect the current proof-of-concept snapshot, not a final clinical claim.

## Relationship To The SpectralBio Project

This dataset is the data layer for the SpectralBio executable research workflow:

- GitHub repo: method, narrative, and reproducibility assets
- Hugging Face dataset: benchmark inputs and analysis artifacts
- Hugging Face Space: interactive demo for humans and agents
- `SKILL.md`: end-to-end executable workflow for regenerating the experiment

The goal is to make the research easy to inspect, rerun, and reference from downstream agents.

## Linked Resources

- Project repository: [https://github.com/DaviBonetto/SpectralBio](https://github.com/DaviBonetto/SpectralBio)
- Interactive demo: [https://huggingface.co/spaces/DaviBonetto/spectralbio-demo](https://huggingface.co/spaces/DaviBonetto/spectralbio-demo)
- Dataset page: [https://huggingface.co/datasets/DaviBonetto/spectralbio-clinvar](https://huggingface.co/datasets/DaviBonetto/spectralbio-clinvar)
- Executable workflow path in the repo: `SKILL.md`

## Citation

If you use this dataset, cite the dataset page and the SpectralBio project:

```bibtex
@dataset{bonetto2026spectralbio_clinvar,
  author = {Bonetto, Davi and Claw},
  title = {SpectralBio ClinVar Variants},
  year = {2026},
  url = {https://huggingface.co/datasets/DaviBonetto/spectralbio-clinvar},
  note = {Filtered ClinVar missense variants for TP53 and BRCA1 used in the SpectralBio executable research workflow}
}

@misc{bonetto2026spectralbio,
  author = {Bonetto, Davi and Claw},
  title = {SpectralBio: Eigenvalue Analysis of Protein Language Model Hidden States for Zero-Shot Variant Pathogenicity Prediction},
  year = {2026},
  howpublished = {Project repository},
  url = {https://github.com/DaviBonetto/SpectralBio}
}
```
