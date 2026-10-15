# Direction 02: results for the research decision

Run date: 22 September 2026. This is an analysis record, not a seminar-paper draft.

**Conclusion:** the existing data show a positive teacher-score moderation pattern, but do not establish a statistically significant difference at the fixed two-sided 5% threshold. This is substantive and feasible research, with inconclusive evidence rather than a proven new effect.

## Question and interpretation

Does the randomized camera-monitoring and attendance-pay program have a larger post-test total-learning effect where baseline teacher scores are higher? The interaction is measured in SD of student total learning per one-SD higher teacher score. The teacher-score reference mean is 34.2617 and SD 10.4632 across 107 schools. Teacher score is not randomized: this does not identify the causal effect of teacher ability or an attendance-to-learning mechanism.

## Data-quality amendment and main result

The original source-compatible sample has 1,646 rows, 1,631 unique school-child keys and 103 schools. The source stayer rule retains 21 rows with neither baseline verbal/written totals nor post-test verbal/written totals; later zero fill creates their totals. The reconstruction preserves this behavior only for replication transparency.

For the user’s existing-measurements constraint, the substantive result excludes all 21 rows. It uses 1,625 observed-test rows, 1,610 unique keys and 101 schools. Original item scoring, missing-modality coding and supplied normalization are retained; this is not a claim that every item in every test is complete. The baseline reference cohort has 2,104 rows across 107 schools; 479 do not have observed follow-up outcomes.

Observed-test interaction: **+0.132133 SD**, school-clustered SE **0.071251**, **95% CI −0.009228 to +0.273494**, **p=.066621**. A null-imposed wild-cluster bootstrap-t using 9,999 school-level Rademacher draws (seed 20260922) gives **p=.0698**, simulation SE .0025. The ordinary 95% interval is a clustered-t interval, not a bootstrap-inverted interval.

The source-compatible replication reference is +0.128862, CI −0.012222 to +0.269946, p=.072981; its separate wild-bootstrap p=.0864. The observed-only restriction is a documented data-quality amendment made after the initial follow-up plan; neither analysis is preregistered.

## All fixed specifications, observed-test sample

Each includes treatment, baseline teacher score and their interaction. The main model also includes original child baseline verbal score, written score and writing status. All uncertainties cluster by school and use CR1 correction with t(G−1) inference.

| Model | Interaction (SD) | 95% CI | p-value | Rows |
|---|---:|---|---:|---:|
| Main observed-test model | +0.132 | -0.009 to +0.273 | 0.067 | 1625 |
| Allow effects to vary with child preparation | +0.129 | -0.013 to +0.272 | 0.075 | 1625 |
| Add geographic controls | +0.087 | -0.042 to +0.217 | 0.185 | 1625 |
| Child preparation + geography | +0.087 | -0.046 to +0.219 | 0.200 | 1625 |
| Give each school equal total weight | +0.124 | -0.015 to +0.263 | 0.079 | 1625 |
| Remove child controls (diagnostic) | +0.153 | -0.049 to +0.355 | 0.135 | 1625 |
| Exclude all repeated child-ID keys | +0.130 | -0.009 to +0.269 | 0.067 | 1595 |

Equal-school weighting changes the target average. Geographic indicators are geographic blocks, not established randomization strata. The repeated-key sensitivity drops all 30 records belonging to 15 repeated keys, not a selected subset. IDs do not resolve repeated measurement versus identifier collisions.

## Fixed score contrasts from the same observed-test fit

| Teacher score | Program effect (SD) | 95% CI | p-value |
|---|---:|---|---:|
| 25th percentile: 27 points | +0.017 | −0.194 to +0.228 | .870 |
| 75th percentile: 41.75 points | +0.204 | +0.007 to +0.401 | .043 |
| 75th minus 25th percentile | +0.186 | −0.013 to +0.386 | .067 |

The last row is the direct heterogeneity test. A significant treatment effect at one score and an insignificant effect at another do not establish that the effects differ. These exploratory contrasts have no multiplicity adjustment. No alternative cutoff or subject-specific outcome was searched in this follow-up.

## Missing-outcome sensitivity

The observed-test rate is 1,625/2,104 = 77.2%. A fixed baseline model for outcome observation includes treatment, teacher score, their interaction, original baseline achievement/writing measures and geographic indicators. The treatment-by-score observation coefficient is −.031, 95% CI −.122 to +.060, p=.495; a nonsignificant result does not establish absence of selective attrition.

One inverse-probability weighting sensitivity gives **+0.135150 SD**. A whole-school pairs bootstrap reestimates the observation-probability model and weighted regression in each of 999 draws (all valid; seed 20260922), yielding **95% percentile CI −0.003332 to +0.279057**. It includes zero. The conditional clustered p=.0527 omits uncertainty from estimating weights, so the bootstrap interval is emphasized. The bootstrap sign fraction is not presented as a null-imposed test p-value.

Fitted observation probabilities range .466–.938 and weights .823–1.649; no trimming was selected. This depends on missing-at-random conditional on the measured baseline predictors and positivity, and cannot prove selection bias is removed. Six baseline schools have no observed follow-up outcomes in the score-complete cohort. Another 141 baseline records in six schools lack teacher scores and are outside this target. No missing student outcome is filled for IPW.

## Additional source-compatible diagnostics

These retain the original coding and are separate from the observed-test headline. Midline total interaction: +.051, CI −.068 to +.171, p=.395. Omitting each of the 103 source-compatible schools in turn gives interaction estimates .107–.164 and p-values .015–.126; 6 of 103 omissions reach .05. None was selected for exclusion. These diagnostics do not establish robust 5% significance.

## Replication and bounded novelty

All 16 Table 9 A/B checks match the released package reference outputs for coefficients, clustered SEs and observation counts at reported precision. Small R-squared differences remain, maximum .005. The printed article lists N=1,760 for controlled post-test Panel B, while the released output and reconstructed controlled code sample use N=1,624. The Panel A count of 1,760 and source-compatible extension count of 1,646 are unaffected.

The exact treatment-by-baseline-teacher-score learning interaction was not found in the full article, official eight-page appendix, erratum or targeted code/log audit. This is a bounded originality check, not proof of absence from wider literature. The original average learning effect, teacher-score attendance split, child-writing/gender learning splits and attendance-learning IV analysis are already in the paper.

## Reproduce and inspect

Run from `/Users/shayb/Downloads/112523-V1` using Python with numpy, pandas and scipy:

```sh
python3 scripts/audit_learning_extension.py
python3 scripts/run_direction02_specs.py
python3 scripts/run_direction02_wildbootstrap.py
python3 scripts/run_direction02_attrition.py
python3 scripts/run_direction02_observed_specs.py
python3 scripts/run_direction02_bootstrap_observed_only.py
```

Outputs and input/script hashes are in `outputs/direction02_significance/` and `outputs/research_direction_audit/`. All model coefficients and contrasts are retained, including nonsignificant results. Bootstrap vectors were checked against direct refits; the observed-test point estimate was independently recalculated. Raw source inputs were not modified.

Original study: https://www.aeaweb.org/articles?id=10.1257/aer.102.4.1241
Replication data: https://doi.org/10.3886/E112523V1
Wild-bootstrap algorithm reference: https://www.stata.com/manuals/rwildbootstrap.pdf
