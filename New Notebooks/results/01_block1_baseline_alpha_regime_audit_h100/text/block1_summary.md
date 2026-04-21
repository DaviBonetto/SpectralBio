# SpectralBio Block 1 Summary

- Account label: `SET_ACCOUNT_LABEL_HERE`
- Repository HEAD: `cb52f10a52b9` - feat(notebooks): Add Block 1 H100 audit notebook
- Genes audited: `TP53, BRCA2, MSH2`
- 3B shadow enabled: `False`

## Main takeaways

- BRCA2: ESM-1v AUC `0.6324`, augmented pair AUC `0.6890`, best alpha `0.90`, fixed 0.55 in plateau `False`
- MSH2: ESM-1v AUC `0.9233`, augmented pair AUC `0.8457`, best alpha `0.00`, fixed 0.55 in plateau `False`
- TP53: ESM-1v AUC `0.9466`, augmented pair AUC `0.9305`, best alpha `0.30`, fixed 0.55 in plateau `False`

## Naming upgrades

- `to_basic__AND__high_disagreement_q75` -> `high-covariance high-disagreement basic-substitution regime`
- `support-ranked feasible panel` -> `performance-blind support-ranked feasible panel`
