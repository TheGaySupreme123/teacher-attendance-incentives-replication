# Bounded novelty map for the final scope choice

Date: 2026-09-22

This is a decision aid for choosing a seminar study. It is not a paper draft and it is not a preregistration. The candidate families were selected after earlier exploratory inspection, so even the fixed analyses below must be described as exploratory evidence. The search is bounded to the Duflo, Hanna, and Ryan (2012) article, its official eight-page appendix and erratum, and the local replication programs, logs, and raw measurements. It does not establish originality against the wider literature.

## Recommended scope: realized NFE departure by baseline writing status

### Working title

**Attendance Incentives and Realized NFE Departure: Heterogeneity by Baseline Writing Status**

### Precise question

Does assignment to the bundled camera-monitoring and attendance-pay program change the probability of a child being classified as having left the nonformal education center differently for children who could versus could not take the baseline written test?

The primary endpoint is the original `drop` indicator: no attendance in the last five observed open-school checks under the supplied Table 10 construction. The single moderator is the pre-treatment baseline-writing indicator, `pre_writ`. The main contrast is the treatment-by-`pre_writ` interaction. This asks whether the program's realized NFE-departure response differs across an observed baseline-preparation margin; it does not ask why children leave and does not identify an educational dropout mechanism.

### Why it is new under the bounded audit

The original paper reports aggregate NFE departure/dropout, government-school movement, and non-government dropout in Table 10 (p. 1274). It separately reports baseline-writing heterogeneity for child attendance (Table 7, p. 1269) and test-score outcomes (Table 9, pp. 1272–73). It does not cross baseline writing with the Table 10 departure outcomes. The source code preserves that separation: `Table7_Table10.do:227–265` uses `pre_writ` for attendance among non-dropouts, while `Table7_Table10.do:272–296` estimates `drop`, `gov`, and `drop2` only in aggregate. No corresponding interaction was found in the article, appendix, erratum, programs, logs, or shipped outputs.

### Current fixed-family evidence

The raw reconstruction retains 2,195 children in 111 schools after excluding two eligible children whose baseline-writing records conflict. The primary `drop` interaction is +0.211 (clustered SE 0.072), 95% CI [0.069, 0.353], classical p=.004 and Holm-adjusted p=.012 across the fixed `drop`/`gov`/`drop2` family. A null-imposed school-level wild-cluster bootstrap gives p=.0072. With the supplied block fixed effects, the interaction is +0.221, 95% CI [0.082, 0.360], p=.002. Reconstructing the same last-five-open-check rule only through 2005-12-31 gives +0.197, 95% CI [0.048, 0.346], p=.010.

The implied treatment differences are +0.050 for baseline non-writers (95% CI [-0.024, 0.124]) and +0.261 for baseline writers (95% CI [0.100, 0.423]). These are conditional descriptive contrasts in realized NFE departure. They should not be narrated as evidence that the program causes educational dropout, changes schooling preferences, or operates through literacy.

The secondary `drop2` interaction is +0.163, 95% CI [0.046, 0.279], classical p=.0068, Holm p=.0136, and wild-bootstrap p=.0099. It depends on the recorded `reason == "2"` marker and should remain secondary because reason fields are frequently blank and the operational outcome is less clean. The primary `drop` outcome is the better anchor because it does not require a reason code.

### Non-negotiable limitation

The original construction keeps the last five **open** checks. Treatment increases the number of open checks, so this is a post-treatment observation rule. In the consensus sample, 145 of 2,195 children have fewer than five observed open checks. Treating those observations as unknown gives an algebraic, no-standard-error bound of [0.119, 0.364] for the writer-minus-non-writer interaction; this is not a confidence interval or a p-value. The study should call the endpoint an operational measure of realized NFE departure under the original roster rule and present coverage as a central limitation.

## Genuine but weaker alternative: post-test learning distribution

### Precise question

Does the program shift the marginal distribution of observed post-test total achievement, especially at the lower tail, rather than only changing the mean?

The locked primary endpoint is the treatment-minus-control 25th percentile of the existing normalized post-test total score. Fixed secondary endpoints are the median, 75th percentile, and treatment-minus-control interquartile-range difference. The analysis uses school-pair bootstrap inference and makes no individual rank-preservation claim.

### Novelty boundary

The original learning analysis reports means of math, language, and total scores and the written-test indicator (Table 8, p. 1271; Table 9, pp. 1272–73). It reports subgroup means by baseline writing and gender, but no student-score quantiles, lower-tail mass, variance, or interquartile spread. The paper's distributional language and density figure concern teacher attendance, not student learning (Figure 2, p. 1250). The appendix's distribution and serial-correlation material is also about teacher work histories (Appendix pp. 5–8; article pp. 1258–63). This makes the learning-distribution question genuinely distinct.

### Current evidence and decision value

The primary P25 contrast is +0.081, bootstrap SE 0.078, 95% percentile CI [-0.081, 0.219], approximate two-sided p=.310 and Holm p=.730 across the four fixed contrasts. The median, P75, and IQR contrasts also have intervals containing zero. It is therefore a legitimate new question but not a strong selected study from these results. It is best retained as an alternative or supporting analysis unless the seminar values distributional description over a statistically resolved main finding.

## Genuine but not recommended as the main study: learning composition by teacher score

### Precise question

Does baseline teacher score moderate the program's post-test learning response differently in mathematics and language?

The locked family uses the same strict observed-test sample, continuous standardized baseline teacher score, the original child baseline controls, and three fixed outcomes: post-test mathematics, language, and total. The domain-composition contrast is the treatment-by-score interaction difference between mathematics and language, with a joint math/language Wald test. No subject is selected after seeing its p-value.

### Novelty boundary

The paper reports separate average treatment effects for math, language, and total in Table 9 (pp. 1272–73), and teacher score appears as a control in the controlled specification. It does not estimate treatment-by-teacher-score interactions by subject, a joint domain test, or a math-minus-language moderation contrast. The exact extension is therefore absent from the bounded official-materials audit. This is a new question, not proof that teacher score causes a subject-specific mechanism.

### Current evidence and decision value

The math interaction is +0.209 (SE 0.099), nominal p=.0367 but Holm p=.110 across the three fixed learning outcomes. Language is +0.085 (p=.239), total is +0.132 (p=.067), the joint math/language test is p=.0896, and the direct math-minus-language interaction contrast is p=.0537. With geographic block controls, the math p-value is .158, language .343, and total .185. The nominal math result must not be called a new significant heterogeneity finding. The family is novel but currently inconclusive and less attractive than the NFE-departure scope.

## Scope rejected as the main contribution: reliability or outage clustering

An analysis of consecutive closures or outage persistence could be computed from `randomcheck.dta`, but it is too close to the original attendance analysis. The paper already reports time-period effects and long-run persistence (pp. 1248–49), the attendance distribution (p. 1250), and serial correlation in the structural labor-supply model (pp. 1258–63). A new run-length statistic would therefore be better treated as supporting descriptive work than as the seminar's substantive extension.

## Decision

Choose the NFE-departure question if the goal is a moderate, focused study with a genuinely new cross-outcome comparison and a two-sided statistical result under the original operational definition. Use the title and estimand above, keep `drop` primary, report `gov` and `drop2` as pre-fixed family outcomes, and state the open-check measurement limitation prominently. The result supports a claim about heterogeneous realized NFE departure under the paper's operational definition. It does not support a claim about educational dropout mechanisms.

The learning-distribution family is the cleanest novelty conceptually but does not resolve at the fixed 5% threshold. The learning-composition family is also novel but fails the fixed multiplicity/joint tests. No scope should be widened or narrowed after these results to obtain significance. All three families remain exploratory because the data and candidate directions were inspected before the final scope was fixed.
