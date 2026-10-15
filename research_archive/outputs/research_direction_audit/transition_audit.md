# Transition extension audit

## Question and novelty boundary

The extension chosen in advance for this audit, after prior exploratory candidate review, is whether the randomized bundled camera-plus-attendance-pay treatment changes the probability of moving from the nonformal education center to a government school differently for children who did versus did not take the baseline written test (`treat × pre_writ`). This is not a preregistered or independent confirmatory test. The original article reports aggregate Table 10 transition/dropout outcomes and separately reports baseline-writing heterogeneity for attendance and learning; the article, eight-page supplemental appendix, erratum, local programs, logs, and shipped outputs contain no cross-tabulation or interaction between `pre_writ` and `gov`/`drop`.

## Raw construction and reproduction

The script starts from `roster_rema2012.dta`, `rosterfin.dta`, `rc_for_roster.dta`, and `enroll1.dta`. It follows `Programs/Table7_Table10.do`: cleans attendance sentinels, retains random-check rows, keeps enrolled children, keeps the last five open-school checks per child, sums attendance and `reason == "2"`, and defines `drop`, `gov`, and `drop2 = drop & !gov`. The raw collapse has 2,197 children in 111 schools (1,061 control and 1,136 treatment). The raw `drop` and `gov` indicators match every child in the shipped `Temp/drop.dta`; the shipped file is a validation reference only.

The reconstructed Table 10 estimates are:

* `drop`: treatment difference 0.0837 (clustered SE 0.0411), matching the published rounded 0.08 [0.04].
* `gov`: treatment difference 0.1014 (clustered SE 0.0349), matching 0.10 [0.03].
* `drop2`: treatment difference -0.0177 (clustered SE 0.0306), matching -0.02 [0.03].

The `reason` field is string in `roster_rema2012.dta` but numeric in `rosterfin.dta`; in the distributed Stata append, the latter's values are blank in the coded roster. The raw reconstruction preserves that source behavior, which is necessary for exact agreement with the shipped Table 10 outcomes.

## Baseline-writing data quality

`pre_writ_attend.dta` has 2,336 rows and 2,333 child IDs. Three IDs in school 5731 are duplicated with conflicting values (children 24, 30, and 33); children 30 and 33 are in the Table 10 sample, while child 24 is not. The primary interaction excludes the two eligible conflicting IDs and uses only consensus child-level statuses, leaving 2,195 children. This handling rule was fixed before calculating the reported interaction after inspecting the raw file, and avoids assigning an arbitrary status to a duplicated ID; it does not make the analysis preregistered.

## Results

The government-school transition interaction is the coefficient on `treat × pre_writ` in a child-level OLS regression with school-clustered standard errors. For consensus-status children it is approximately +0.048 (SE 0.078, 95% CI [-0.106, 0.202], p=0.534); the implied treatment effects are +0.095 (SE 0.033) for `pre_writ=0` and +0.144 (SE 0.080) for `pre_writ=1`. Group means are in `transition_group_means.csv`. This is compatible with a somewhat larger transition effect among baseline writers, but the data do not distinguish that interaction from zero.

The non-government dropout outcome is a clearly exploratory secondary result: the `treat × pre_writ` coefficient for `drop2` is approximately +0.163 (SE 0.059, 95% CI [0.046, 0.279], p=0.007). It must not be selected or promoted because of this p-value; it is reported because it is the final Table 10 outcome and was named in advance as a secondary check. Its interpretation is also limited by the outcome construction below.

## Interpretation limit: open-school conditioning

The original definition conditions the roster observations on `open == 1` and then selects each child's last five open checks. This is a post-treatment measurement rule because treatment changes how often schools are open. All 2,197 child IDs still enter the collapse, but the number of available open checks differs: treatment children have more open checks on average and a larger share with at least five. Therefore `gov` and `drop2` are intent-to-treat-style outcomes under the paper's operational definition, not cleanly observed transitions independent of treatment-generated observation opportunities. The interaction should be treated as moderate/descriptive evidence, not a strong causal claim about readiness or formal-school progression.

## Decision

The transition-by-baseline-writing idea is genuinely distinct from the reported aggregate Table 10 and from the article's writing-status attendance/learning tables, and it is feasible with existing numbers. However, the primary interaction is imprecise and the post-treatment open-school measurement rule is a material identification limitation. It is defensible as a moderate seminar extension only if framed as a bounded heterogeneity audit of the original transition result. It is not strong enough to be the sole headline contribution without a stronger pre-specified design or additional independent evidence.
