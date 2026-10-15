# Direction 0.2 wild-bootstrap significance check

This bounded inference run uses the raw-data reconstruction and primary controlled model from `scripts/audit_learning_extension.py`. The replication gate for the original Table 9 specifications must be passed before interpreting this extension.

## Model and null

The outcome is post-test total score standardized as in the source analysis. The full model includes treatment, continuous baseline teacher score, their interaction, and the original baseline controls (`pre_total_v`, `pre_total_w`, and `pre_writ`). The null-imposed restricted model drops only the interaction; treatment's main effect remains in the model, so the test allows a nonzero average treatment effect.

Inference uses school-level Rademacher wild multipliers, one multiplier shared by all analysis records in a school, and the same finite-sample clustered sandwich correction as the primary estimate. It is a Studentized bootstrap-t test, with two-sided p-value `(1 + exceedances) / (B + 1)`.

## Results

- Interaction estimate: **0.128862 SD per teacher-score SD**.
- Clustered SE: **0.071129**; observed t = **1.8117**; 102 cluster degrees of freedom.
- Classical clustered two-sided p-value: **0.0730**.
- Null-imposed wild-bootstrap two-sided p-value: **0.0864** (863 of 9999 bootstrap |t| values at least as large as the observed |t|; Monte Carlo SE **0.0028**).
- 90% t interval: **[0.010793, 0.246931]**.
- 95% t interval: **[-0.012222, 0.269946]**.
- Complete-case sample: **1646 analysis observation rows in 103 schools**, corresponding to **1631 unique school-child keys**. The source-aligned sample is retained as constructed; this audit does not adjudicate whether reused keys represent duplicated measurements or distinct children.

The fixed seed is `20260922` and the run uses `9999` bootstrap repetitions. The first five vectorized draws were independently refit observation-by-observation; validation pass: **True**.

The estimate is positive, but the bootstrap result should be reported with its p-value and interval rather than converted into a threshold claim. In particular, if the p-value is near 0.10, that is evidence compatible with a modestly positive moderation pattern while remaining uncertain under a conventional 5% standard.

## Reproduction

Run `python3 scripts/run_direction02_wildbootstrap.py` from the repository root. The exact bootstrap t statistics are in `bootstrap_t_statistics.csv`; summary values, seed, model, and validation are in `bootstrap_summary.json`, `bootstrap_metadata.json`, and `bootstrap_validation.csv`.
