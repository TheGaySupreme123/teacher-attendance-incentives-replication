# Frozen Direction 0.2 scope family

Date: 2026-09-22

This family was fixed for the follow-up before running the domain estimates,
after the observed-only data-quality amendment was identified. It is a
theory-led broadening of the learning response: teacher capacity may moderate
the treatment response differently in the pre-defined math and language
components, with total learning as the corresponding aggregate outcome.

## Common sample and covariates

Use the strict observed-only post-test sample `R == 1` from
`scripts/run_direction02_attrition.py`, with the row identity carried by
`row_id` so repeated `(schid, childno)` keys cannot multiply observations.
The sample is fixed at N=1,625 observation rows in 101 schools. The baseline
teacher test score is standardized using the same school-level reference as
the earlier Direction 0.2 audit. Every outcome uses the same covariates:

`treat + teacher_score_z + treat_score_z + pre_total_v + pre_total_w + pre_writ`

The three outcomes are fixed in advance from the existing raw reconstruction:

1. `z_add_post_math`
2. `z_add_post_lang`
3. `z_add_post_total`

## Tests

For each outcome, estimate the treatment-by-teacher-score interaction with
school-clustered inference. Report the individual two-sided p-value and the
Holm-adjusted p-value across exactly these three outcomes.

For math and language, report one joint two-parameter Wald test of the two
interaction coefficients, using the same-school residual cross-covariance in
the clustered sandwich. Report the formal math-minus-language interaction
contrast using that same covariance matrix and t(100) inference.

Repeat only the corresponding three outcome interaction models with geographic
block fixed effects (blocks 2--5, block 1 as the base), and report their
individual and Holm-adjusted p-values plus the corresponding joint
math/language test and math-minus-language contrast.

No score cutoffs, subject-specific searches beyond this fixed three-outcome
family, school exclusions, outcome re-selection, or additional models are
permitted. A significant result in one domain is reported together with all
family results and multiplicity adjustment; the family is not selected by
observed significance.

This is an analysis-scope record, not a novelty claim. Original-paper overlap
and substantive contribution are assessed separately.
