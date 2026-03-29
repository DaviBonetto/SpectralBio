# Legacy Hugging Face Compatibility Folder

The canonical live Space is a repository-root mirror whose root README points
to `publish/hf_space/app.py`. The canonical dataset card remains under
`publish/hf_dataset/`.

This folder is compatibility-only. It is intentionally limited to thin wrapper
files so existing Hugging Face entrypoints do not break while the repository
converges on one canonical publish path.

Files intentionally kept here:

- `app.py`
- `README.md`
- `dataset_card.md`
- `requirements.txt`

Removed from this folder after verified replacement:

- benchmark-facing snapshots now live outside this compatibility pointer
- decorative assets now live outside this compatibility pointer

- Artifact role: `research reproducibility artifact`
- Primary benchmark: `TP53 canonical executable benchmark`
- Secondary benchmark: `bounded transfer on a fixed BRCA1 subset (N=100)`
- Transfer framing: `secondary transfer evaluation without retraining`
- Adaptation note: `adaptation recipe only`
