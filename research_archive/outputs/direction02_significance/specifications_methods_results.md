# Direction 0.2 specification results

## Question and fixed analysis sample

The analysis asks whether the treatment effect on the post-test total learning score varies with the continuous baseline teacher-test score. The score is a pre-treatment school-level measure, standardized using the mean and sample standard deviation across the 107 score-observed schools used by the audited reconstruction. The primary post-test complete-case sample was fixed before fitting any specification: 1,646 observation rows in 103 schools, representing 1,631 unique `(schid, childno)` keys. Fifteen keys are repeated (30 rows). Every ordinary primary and post-test sensitivity model uses exactly those observations and schools; the separate duplicate-key data-quality sensitivity is explicitly reported on a reduced sample.

The primary regression is post-test total score on treatment, standardized teacher score, their interaction, and the original child baseline controls (`pre_total_v`, `pre_total_w`, and `pre_writ`). The outcome and construction follow the raw-data audit; no subject-specific outcomes, score cutoffs, or outcome re-selection are used. The specification set was fixed for this follow-up after prior exploratory review; it was not preregistered.

## Inference

All fits use school-clustered CR1 standard errors with the audit's finite-sample factor G/(G-1) x (N-1)/(N-K). P-values and 95% intervals use a two-sided t distribution with G-1 school degrees of freedom. The coefficient table reports every estimated coefficient, including controls and geographic block indicators. Rank and condition checks are recorded for every fit.

The primary interaction is **0.128862** SD of learning per teacher-score SD (SE 0.071129, p=0.073, 95% CI -0.012222 to 0.269946; N=1646, G=103). It reproduces the prior audited estimate 0.128862 (SE 0.071129) to rounding precision.

## Fixed score-level treatment contrasts

The marginal effects are formal linear contrasts from the same primary fit: treatment coefficient plus the interaction coefficient multiplied by the standardized teacher score. The school-score 25th percentile is a raw score of 27 (z = -0.6940); the 75th percentile is 41.75 (z = 0.7157).

At the school-score **p25_school_score** (raw 27.00, z -0.6940), the treatment effect is **0.024190** SD (SE 0.105573, p=0.819, 95% CI -0.185214 to 0.233594).
At the school-score **p75_school_score** (raw 41.75, z 0.7157), the treatment effect is **0.205847** SD (SE 0.097378, p=0.037, 95% CI 0.012698 to 0.398997).

The formal high-minus-low contrast (p75 minus p25) is **0.181657** SD (SE 0.100271, p=0.073, 95% CI -0.017230 to 0.380544). Its p-value is exactly the interaction p-value because the treatment main effect cancels; no new fit is estimated. The interaction p-value is 0.073. A significant marginal treatment effect at one fixed score percentile would therefore not by itself establish statistically significant heterogeneity; the heterogeneity claim is tested by the interaction coefficient and its confidence interval.

## Sensitivities

The child-composition sensitivity adds treatment interactions with all three original child baseline controls. The geographic-block specifications add indicators for blocks 2–5, with block 1 as the base; these are geographic block fixed effects and are not relabeled as randomized strata. The equal-school-weight fit gives each school total weight one, changing the estimand from the observation-weighted average treatment effect to an equal-school average. The no-baseline-controls model is a diagnostic on the same primary complete-case sample.

- `child_baseline_interactions`: interaction 0.126240, SE 0.071790, p=0.082, 95% CI -0.016156 to 0.268635; N=1646, G=103.
- `geographic_block_fixed_effects`: interaction 0.086494, SE 0.064779, p=0.185, 95% CI -0.041995 to 0.214982; N=1646, G=103.
- `child_baseline_interactions_plus_geographic_block_fixed_effects`: interaction 0.086114, SE 0.066222, p=0.196, 95% CI -0.045236 to 0.217465; N=1646, G=103.
- `equal_school_weight_primary`: interaction 0.125151, SE 0.069692, p=0.075, 95% CI -0.013083 to 0.263385; N=1646, G=103.
- `no_baseline_controls_same_sample`: interaction 0.145595, SE 0.102271, p=0.158, 95% CI -0.057260 to 0.348449; N=1646, G=103.
- `data_quality_duplicate_key_exclusion`: interaction 0.126885, SE 0.070157, p=0.073, 95% CI -0.012271 to 0.266042; N=1616, G=103.

The data-quality sensitivity drops every row belonging to a repeated `(schid, childno)` key in the fixed post sample (15 keys, 30 rows), producing N=1,616 observations. This is a rule based on the full duplicate-key audit rather than a hand-picked exclusion. The IDs alone cannot establish whether these records are repeated measurements or identifier collisions, so the primary result retains the original audit-aligned rows and this result is reported as a sensitivity.

The midline total-score model is secondary and uses its own audited midline complete-case sample (N=1,767 observations, G=107), with the same original baseline controls and score interaction. It is not pooled with the post-test specification.

Secondary midline interaction: 0.051463, SE 0.060314, p=0.395, 95% CI -0.068116 to 0.171041; N=1767, G=107.

## Leave-one-school-out check

The primary specification was refit after omitting each of the 103 schools in turn. No school was selected for exclusion. Across all omissions, the interaction estimate ranges from 0.106871 to 0.164052; the two-sided p-values range from 0.015347 to 0.126386, with 6 of 103 omissions yielding p<.05. The full per-school estimates, omitted-school identifiers, standard errors, p-values, intervals, sample sizes and rank checks are in `specifications_leave_one_school_out.csv`; no omission was used to select the reported result.

## Limits

Teacher score is observed before treatment but is not randomized, so the interaction is descriptive treatment-effect heterogeneity by an observed baseline measure. Teacher-score missingness and test attrition reduce the complete-case sample. The post-test high-score marginal effect is evidence that the treatment effect is positive at that fixed score level; it does not prove that the high-score effect differs from the low-score effect at the 5% level unless the interaction itself is significant.

## Reproduction and provenance

Run `python3 scripts/run_direction02_specs.py` from `/Users/shayb/Downloads/112523-V1`. The raw input and source hashes, software versions, source audit hash, commit, sample definition, and specification list are recorded in `specifications_metadata.json` and `specifications_input_hashes.csv`. The article's Table 9B post panel reports N=1,760, while the released package/code Table9B_post reference reports N=1,624; this package/article discrepancy does not affect the primary Table 9A post reconstruction used here. Generated at 2026-09-22T10:42:46.670633+00:00.
