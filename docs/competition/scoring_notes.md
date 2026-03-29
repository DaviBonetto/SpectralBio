# Scoring Notes

The rebuild is optimized for three high-value competition properties:

1. Executability
2. Reproducibility
3. Clarity for agents and reviewers

Implications:

- One canonical scored path beats multiple competing entry points.
- A narrow validated core has higher expected value than ambitious but weakly supported generalization language.
- BRCA1 remains valuable as secondary evidence, but not as the artifact headline.
- Verification must be machine-readable wherever possible.

## Source-of-Truth Precedence

The repository uses this precedence ladder:

1. `docs/truth_contract.md`
2. `benchmarks/manifests/*`
3. `artifacts/expected/*`
4. `paper/*` derived from canonical outputs
5. README, demo, dataset card, and publish mirrors

Any lower-precedence artifact that conflicts with a higher-precedence source must be rewritten or removed.

## Repository Wording Policy

Forbidden repository-facing wording:

- `any protein`
- `strong cross-protein generalization`
- `exceptional cross-protein generalization`
- `broad cross-protein generalization`
- `clinical deployment`
- `clinical use`

Allowed repository-facing wording:

- `TP53 canonical executable benchmark`
- `bounded transfer on a fixed BRCA1 subset (N=100)`
- `secondary transfer evaluation without retraining`
- `adaptation recipe only`
- `research reproducibility artifact`
