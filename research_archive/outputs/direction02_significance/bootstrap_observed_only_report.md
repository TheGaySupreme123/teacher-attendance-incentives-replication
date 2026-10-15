# Direction 0.2 observed-outcome-only wild-bootstrap check

This is a bounded sensitivity check using the existing raw-data construction in `scripts/run_direction02_attrition.py`. It retains only `R == 1`: eligible rows whose reconstructed source post verbal total is observed. No synthetic post-test outcome is assigned. The source-aligned sample's repeated records remain source observation units.

The regression is the same controlled Direction 0.2 interaction model, using the attrition script's `score_z` moderator, `treat_score_z`, treatment, and the original baseline controls. The null-imposed restricted model drops only `treat_score_z`, so the treatment main effect remains free. Inference uses school-level Rademacher multipliers and the same finite-sample clustered sandwich correction as the original bootstrap run.

## Results

- Interaction estimate: **0.132133 SD per teacher-score SD**.
- Clustered SE: **0.071251**; observed t = **1.8545**; 100 cluster degrees of freedom.
- Classical clustered two-sided p-value: **0.0666**.
- Null-imposed wild-bootstrap two-sided p-value: **0.0698** (697 of 9999 bootstrap |t| values at least as large as the observed |t|; Monte Carlo SE **0.0025**).
- 90% t interval: **[0.013839, 0.250427]**.
- 95% t interval: **[-0.009228, 0.273494]**.
- Sample: **1625 analysis observation rows in 101 schools**, corresponding to **1610 unique school-child keys**.

For comparison, the source-aligned result retains 1,646 analysis records in 103 schools and has interaction coefficient 0.128862, clustered SE 0.071129, and classical p=0.0730. The observed-outcome-only sensitivity uses 1,625 records in 101 schools; its coefficient is 0.132133 and its classical p-value is 0.0666. The numerical results are therefore very similar, with the same substantive uncertainty.

The fixed seed is `20260922` and the run uses `9999` bootstrap repetitions. The first five vectorized draws were independently refit; validation pass: **True**.

## Reproduction

Run `python3 scripts/run_direction02_bootstrap_observed_only.py` from the repository root. Exact bootstrap t statistics are in `bootstrap_observed_only_t_statistics.csv`; summary values, hashes, and validation are in the other `bootstrap_observed_only_*` artifacts.
