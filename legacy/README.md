# Legacy Provenance Boundary

`legacy/` stores transitional snapshots that were removed from the active
canonical path after verified replacements existed.

Rules:

- Do not add new primary workflows here.
- Do not point new code at these files as the default path.
- Keep provenance snapshots only when they explain how a canonical file was
  derived or preserve historical competition evidence.

Current ownership:

- `legacy/colab/`: notebook-era Colab workflow snapshots
- `legacy/colab_results/`: notebook-era TP53 result snapshots
- `legacy/huggingface_assets/`: old demo-era asset files kept verbatim for provenance
- `legacy/huggingface_data/`: old benchmark-facing data snapshots
- `legacy/submit/`: pre-rebuild submission flow retained for provenance only

Notes:

- `legacy/submit/api_key.txt` is intentionally ignored and must remain local-only.
- Nothing under `legacy/` is a canonical execution surface.
