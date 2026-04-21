# Block 7 Turbo Gallery Summary

- Claim status: `reviewer_grip_gallery_supported`
- Claim reason: The gallery isolates concrete cases where covariance rescue, local structure, and at least partial cross-model/alpha support align.
- Positive rescue cases selected: `5` across `3` genes
- Positive cases with strong local structure: `4`
- Positive cases with explicit ProtT5 support: `1`
- Positive cases with alpha stability >= 0.50: `4`
- Anti-case: `BRCA1:C60G`

## Selected Rescue Cases

- TSC2:N1563K | margin=0.395 | repair=nan | pLDDT=89.4 | contacts=10
- TSC2:G293R | margin=0.348 | repair=nan | pLDDT=90.9 | contacts=13
- CREBBP:R1340P | margin=0.247 | repair=nan | pLDDT=98.5 | contacts=11
- CREBBP:S1686F | margin=0.232 | repair=nan | pLDDT=98.2 | contacts=12
- GRIN2A:P78R | margin=nan | repair=0.228 | pLDDT=88.6 | contacts=3

## Anti-Case

- BRCA1:C60G | margin=-0.482 | repair=nan | pLDDT=nan | contacts=nan

## Claim Paragraph

We distilled the previous bounded evidence into a reviewer-grip gallery with `5` rescue cases across `3` genes plus anti-case `BRCA1:C60G`. The finalists are not just high-scoring by covariance: `4` carry strong local structure support, `1` show explicit ProtT5 agreement, and `4` stay positive across the alpha sweep. This makes the story concrete: SpectralBio is strongest when likelihood under-reacts, local geometry is contact-dense and high-confidence, and covariance rescue survives beyond a single checkpoint.
