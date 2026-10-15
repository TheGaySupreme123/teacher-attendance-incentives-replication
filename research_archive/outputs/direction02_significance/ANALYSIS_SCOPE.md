# Direction 02: focused significance assessment

Chosen before this round of robustness calculations, 2026-09-22. This is NOT a preregistration: the primary interaction and other exploratory screens were seen in earlier work.

## Fixed main question

Does assignment to the bundled camera-monitoring and attendance-pay program have a different effect on POST-TEST TOTAL achievement as baseline teacher score rises?

Primary coefficient: treatment × continuous baseline teacher score. Teacher score is standardized using the existing audited 107-school reference. Outcome scale and source cleaning remain those of the replicated Table9. The reference model includes treatment, teacher score, their interaction, and the original pupil baseline verbal score, written score, and writing-status controls. Use complete cases for these fields. Inference clusters by school; two-sided 5% threshold and 95% intervals.

## Checks fixed for this round

1. Exact main rerun and independent wild-cluster bootstrap-t, null imposed only on the interaction, retaining a nonzero average treatment effect. Fixed seed and repetition count; no repeated seeds to seek significance.
2. Same-sample reasonable specifications: original child controls; treatment interacted with child baseline controls; geographic block fixed effects; both sets; equal-school weighting (different target average); no child controls on the SAME sample as a diagnostic.
3. Single secondary outcome/time point: midline TOTAL learning. No subject-specific mathematics/language searches; no alternative cutpoint searches.
4. Predicted treatment effects at fixed school-score 25th and 75th percentiles and their direct contrast. A significant treatment effect at one score and a nonsignificant effect at another do not establish heterogeneity.
5. Leave-one-school-out main-model influence summary. Report the entire range; do not remove a school to obtain significance.
6. Missing-outcome audit and one inverse-probability weighting sensitivity based solely on observed baseline information. No imputed learning outcomes. Refit the observation model in each whole-school bootstrap if used for uncertainty. Label missing-at-random and positivity assumptions.

## Interpretation boundaries

Existing measurements only. Bootstrap/resampling is an inference calculation, not new people or new observations. Prior exploration means p-values are descriptive/exploratory evidence. Report all agreed checks, including nonsignificant results. Retain the distinction between original average treatment effects, conditional effects at specific teacher scores, and the genuinely new interaction. No causal claim about teacher ability itself and no mediation claim that attendance alone caused learning.

An estimate crossing a threshold under one reasonable model while failing under others is specification-sensitive evidence, not robust proof. Do not change to one-sided testing or a 10% threshold after seeing the result.

## Data-quality amendment discovered during the missingness audit

The original source stayer rule retains 21 rows with neither baseline achievement totals nor post-test verbal/written totals; its later zero fill creates test totals for those rows. This was discovered during the fixed missingness check, not by searching for a preferred p-value. The source-compatible 1,646-row calculations are retained for replication transparency. For the user's existing-measurements constraint, the substantive extension now emphasizes the 1,625 rows with observed baseline and post-test totals (101 schools). The same fixed specifications and inference procedures are repeated on that observed-test sample; no new outcomes, cutpoints, test tails, or significance thresholds are selected. Original item scoring and test-modality rules are retained. Fifteen repeated ID keys still require a separate, all-affected-records exclusion sensitivity.
