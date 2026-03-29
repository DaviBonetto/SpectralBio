# Submission Checklist

- Canonical TP53 path runs from frozen benchmark files only.
- BRCA1 transfer path runs from `brca1_transfer100_v1.json` only.
- `spectralbio verify` passes.
- `scripts/preflight.py` passes.
- README, SKILL, paper, dataset card, demo, and truth contract agree on scope.
- No forbidden generalization wording remains in canonical docs.
- `publish/hf_space/` and `publish/hf_dataset/` are exportable.
- `scripts/submit_clawrxiv.py` reads `CLAWRXIV_API_KEY` from environment only.
- No secrets are committed.
- Release bundle exists under `artifacts/release/claw4s_2026/`.
- Credentials are never committed.
- Credentials are read from environment variables or ignored local files only.
- Credentials are never sent to any domain or IP other than `http://18.118.210.52`.
