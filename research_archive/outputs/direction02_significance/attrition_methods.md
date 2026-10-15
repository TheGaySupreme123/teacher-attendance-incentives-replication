# Direction 0.2 post-test attrition sensitivity

This is a raw-data sensitivity audit for post-test total learning moderated by the continuous pre-treatment teacher score. It uses the reconstruction in `scripts/audit_learning_extension.py`; no synthetic post-test outcome is assigned to a row whose source post verbal total is missing.

## Exact cohort and outcome rule

The pre-treatment eligible cohort is the intersection of: an original baseline achievement total in either verbal or written baseline test, an observed baseline writing-status flag, and an observed teacher score. Teacher-score-missing records are excluded before fitting the observation model because the treatment-by-score estimand is undefined for them. This yields the score-complete baseline cohort shown in `attrition_counts.csv`.

The outcome-observation indicator is one only when the reconstructed source `post_total_v` is observed and the normalized post total exists. This preserves the original source outcome construction for observed rows while excluding rows that would obtain a zero only through the source's later missing-value fill. The complete-case contrast uses exactly the same treatment, teacher-score, interaction, and baseline-control regression on the eligible cohort with this indicator equal to one.

Repeated `(schid, childno)` keys are retained as source reconstruction units so the audit does not silently deduplicate or multiply them. Counts therefore report both source rows and unique student keys. The repeated keys are listed in `attrition_duplicate_keys.csv`; they are a measurement and interpretation limitation, not evidence of additional children.

## Observation model

A fixed linear-probability model predicts outcome observation from treatment, standardized teacher score, treatment-by-score, the original child baseline achievement components (`pre_total_v`, source-scaled `pre_total_w`), baseline writing status, and geographic-block indicators (smallest block omitted). Its treatment-by-score coefficient is reported with school-clustered small-sample uncertainty. A logistic version of the same fixed design supplies probabilities for the weighting sensitivity.

Treatment-by-score prediction of outcome observation: **-0.031** (clustered SE 0.046, 95% CI -0.122 to 0.060, p=0.495, N=2104, schools=107).

## Main and IPW contrast

The source-compatible audited complete-case reference is 0.129 (SE 0.071, CI -0.012 to 0.270, p=0.073, N=1646, schools=103). It contains the source rows retained by the audited stayer rule, including rows whose post verbal total is missing and was later filled to zero by the source construction.

The no-synthetic-outcome complete-case estimate on the eligible cohort is 0.132 (SE 0.071, CI -0.009 to 0.273, p=0.067, N=1625, schools=101).

The single IPW sensitivity uses stabilized weights `mean(R)/p_hat` for observed outcomes, where `p_hat` comes from the fixed baseline logistic design above. The weighted interaction is 0.135; its conditional school-clustered SE is 0.069 (conditional p=0.053). The whole-school bootstrap used 999 valid draws out of 999 with seed 20260922; its two-sided 95% percentile CI is -0.003 to 0.279.

The bootstrap refits the observation model and the weighted outcome regression in every whole-school draw, so the percentile interval includes probability-estimation uncertainty. The IPW result is not treated as statistically significant when this interval includes zero. The sensitivity relies on missing at random conditional on the fixed baseline design and on positivity; these assumptions are not testable from these data.

## Diagnostics and limits

Among baseline records with an observed achievement and writing flag, 141 rows across 6 schools lack a teacher score and are outside the estimand. The fitted probabilities and stabilized weights are reported in `attrition_ipw_diagnostics.csv`; the smallest fitted probability and largest observed-outcome weight are shown there. No trimming or post hoc cutpoint selection was used.

The score-complete analytic sample contains 15 repeated student keys in the retained source rows. The duplicate-key report identifies conflicting or repeated source records. The package's school-level clustering remains the inference unit, but duplicated keys limit interpretation as a unique-child panel.

Teacher score is an observed pre-treatment moderator, not a randomized treatment. The interaction describes heterogeneity by measured score and does not identify a causal effect of teacher quality. IPW can address measured outcome-selection differences only under the stated MAR and positivity assumptions; it does not recover outcomes for missing-score schools or prove that missingness has been resolved.

Raw-input, source-program, shipped-reference, and script SHA-256 hashes are in `attrition_raw_hashes.csv`; run metadata and the exact command are in `attrition_run_metadata.json`.
