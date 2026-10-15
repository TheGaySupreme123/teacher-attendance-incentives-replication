# Post-test total-learning distribution contrasts

This is the newly screened exploratory distribution family fixed in `scope_audit.md`; it is not confirmatory.

## Locked sample and estimands

The sample contains **1737 analysis observation rows**, **1720 unique school-child keys**, and **107 schools**. It includes rows with observed baseline achievement, observed baseline writing status, and an observed reconstructed post-test total. Teacher-score availability was not required or used. There are 868 control rows in 54 schools and 869 treatment rows in 53 schools.

The prespecified contrasts are treatment minus control at P25, P50, and P75, and treatment IQR minus control IQR. P25 was fixed as primary before computation; the other three are secondary. Quantiles use NumPy's linear interpolation, and source rows and ties are retained.

## Results

The bootstrap uses separate school resampling within each treatment arm, carries every source row from each selected school, reports 95% percentile intervals and bootstrap standard deviations, and uses an approximate centered two-sided p-value with `(1 + exceedances)/(B + 1)`. Holm adjustment covers all four visible contrasts.

- **p25 (primary)**: contrast **0.081059**, bootstrap SE 0.077647, 95% percentile CI [-0.081058, 0.218858], approximate centered p=0.3099, Holm-adjusted p=0.7300.
- **p50 (secondary)**: contrast **0.143572**, bootstrap SE 0.158791, 95% percentile CI [-0.136627, 0.480947], approximate centered p=0.3692, Holm-adjusted p=0.7300.
- **p75 (secondary)**: contrast **0.258405**, bootstrap SE 0.195881, 95% percentile CI [-0.166311, 0.602661], approximate centered p=0.1825, Holm-adjusted p=0.7300.
- **iqr (secondary)**: contrast **0.177346**, bootstrap SE 0.151898, 95% percentile CI [-0.150210, 0.443617], approximate centered p=0.2415, Holm-adjusted p=0.7300.

The run used **9999** school-pair bootstrap repetitions with fixed seed `20260922`. These p-values are descriptive bootstrap approximations for the prespecified contrasts. They do not provide individual-level standard errors, assert rank preservation, or identify a structural quantile treatment effect. Missing post-test observations and source-aligned repeated rows remain interpretation limits.

## Reproduction

Run `python3 scripts/run_distribution_quantile_bootstrap.py`. The locked scope is in `scope_audit.md`; exact replicate contrasts are in `distribution_bootstrap.csv`, and summaries, input hashes, and metadata are in the other `distribution_*` artifacts.
