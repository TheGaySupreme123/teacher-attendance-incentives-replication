# Locked scope audit: post-test total-learning distribution

This scope was fixed before computing distributional contrasts.

## Estimand family

- Outcome: the existing reconstructed post-test total score (`outcome_z`).
- Sample: rows from `run_direction02_attrition.prepare_data()` satisfying all four conditions: `baseline_observed`, `writing_observed`, `outcome_observed`, and nonmissing `outcome_z`.
- Teacher-score variables: not required and not used for sample selection or adjustment.
- Contrasts: treatment minus control at P25, P50, and P75, plus treatment IQR minus control IQR.
- Primary contrast: P25. P50, P75, and IQR are secondary and remain visible in the same table.
- No other quantiles, outcomes, cut points, or moderator specifications are in scope.

## Inference rule

The uncertainty calculation is a stratified school-pair bootstrap: schools are resampled with replacement separately within the treatment and control arms, and every source observation row from a selected school is carried into that replicate. Results are percentile 95% intervals, bootstrap standard deviations, and approximate centered-bootstrap two-sided p-values with a +1 finite-sample adjustment. Holm adjustment is reported across these four prespecified contrasts.

Quantiles use NumPy's default linear interpolation. Repeated source rows and ties are retained. The resulting contrasts are descriptive distributional comparisons; the analysis does not claim individual-level standard errors, rank preservation, or a structural quantile treatment effect.

This is a newly screened exploratory family and is not confirmatory. The exact script, seed, sample counts, and input hashes are recorded in the companion metadata.
