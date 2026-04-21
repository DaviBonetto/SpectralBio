# Block 5 Clinical Panel Audit Summary

- Claim status: `clinical_panel_failure_regime_supported`
- Claim reason: Multiple clinical genes improve with covariance, the shortlist spans several genes, and BRCA1/MSH2-style counterexamples keep the claim bounded instead of over-generalized.
- Positive-focus genes with delta >= 0.05: `4` of `4`
- Same-surface wins against ESM-1v where available: `1`
- Counterexample losses or flat settings: `2`
- Shortlisted rescue candidates: `12` across `4` genes

## Claim Paragraph

In a bounded clinical-panel audit, covariance-aware scoring improves over the frozen ESM2 scalar baseline in 4 of 4 positive-focus genes, while explicitly failing or flattening in 2 counterexample settings. The audit yields 12 rescue candidates across 4 genes for downstream Block 7 curation. These shortlist entries are not asserted to be final VUS exemplars yet; they are prioritized ClinVar-style missense cases where covariance raises signal that scalar baselines under-call.
