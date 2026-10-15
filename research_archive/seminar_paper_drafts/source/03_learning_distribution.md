# Alternative route 03: Distributional effects on post-test learning

**Status.** This is an alternative research memo for a possible seminar paper. It is not the selected NFE-departure paper and it is not a completed new full paper. It describes a bounded distributional extension using only the existing reconstructed post-test outcome and the already-run school bootstrap.

## Question and motivation

The paper could ask: **Did the camera-monitoring and attendance-pay program shift the distribution of observed student learning, especially at the lower tail, rather than only changing the mean?** The original study emphasizes average effects on mathematics, language, and total learning. A mean can conceal whether an intervention helps students near the bottom, raises outcomes throughout the distribution, or increases dispersion by benefiting some children more than others. A quantile-based extension makes that question explicit while using the same experiment and the same normalized post-test total.

The primary estimand is the treatment-control difference in the 25th percentile of observed post-test total learning. The median, 75th percentile, and the treatment-control difference in interquartile range are fixed secondary contrasts. The P25 choice gives the paper a lower-tail focus without searching over many quantiles after seeing the data. The extension is descriptive about the observed outcome distribution; it is not a structural quantile treatment effect and does not assume that the same child would occupy the same rank under treatment and control.

This route has a clean bounded novelty argument. The original paper reports means and treatment effects for mathematics, language, and total scores, and it reports subgroup means by baseline writing and gender. The audited article, official appendix, erratum, source programs, logs, and shipped outputs do not report student-learning quantiles, lower-tail mass, learning variance, or an interquartile-range contrast. The distributional figures and discussion in the original work concern teacher attendance, not the distribution of student learning. That supports the claim that this is a different question within the same experiment. It remains a bounded audit, not proof that no later paper has studied an analogous distributional question.

## Data and estimands

The locked analysis sample contains 1,737 observation rows, 1,720 unique school-child keys, and 107 schools. It includes 868 control rows from 54 schools and 869 treatment rows from 53 schools. Teacher-score availability is not required and is not used for sample selection or adjustment. The outcome is the existing normalized reconstructed post-test total, `outcome_z`. Rows are retained as source observation units, including repeated keys and ties.

For each assignment arm, I calculate empirical quantiles of the observed post-test total using NumPy's linear interpolation. In the equations below, Q denotes a quantile and the subscript identifies the treatment or control arm. The primary and secondary estimands are

\[
\Delta_{\tau}=Q_1(\tau)-Q_0(\tau), \qquad \tau\in\{0.25,0.50,0.75\},
\]

and

\[
\Delta_{IQR}=[Q_1(0.75)-Q_1(0.25)]-[Q_0(0.75)-Q_0(0.25)].
\]

The uncertainty calculation resamples schools separately within treatment and control arms. Each selected school contributes every source row in that school to the bootstrap replicate. The run uses 9,999 school-pair bootstrap repetitions, seed 20260922, 95-percentile intervals, and an approximate centered two-sided p-value with the stated +1 finite-sample adjustment. Holm adjustment is applied across the four visible contrasts. This is a school-level resampling procedure, so the results should not be presented as individual-level standard errors or as evidence of rank preservation.

## Current results

The arm-specific empirical quantiles provide useful scale for the contrasts:

| Assignment arm | Rows | Unique keys | Schools | P25 | P50 | P75 | IQR |
|---|---:|---:|---:|---:|---:|---:|---:|
| Control | 868 | 858 | 54 | -0.522 | 0.109 | 0.975 | 1.497 |
| Treatment | 869 | 862 | 53 | -0.441 | 0.252 | 1.233 | 1.674 |

The corresponding treatment-minus-control contrasts are:

| Contrast | Role | Estimate | Bootstrap SE | 95% percentile CI | Centered p | Holm p (4 contrasts) |
|---|---|---:|---:|---:|---:|---:|
| P25 | Primary | 0.081 | 0.078 | [-0.081, 0.219] | 0.3099 | 0.7300 |
| P50 | Secondary | 0.144 | 0.159 | [-0.137, 0.481] | 0.3692 | 0.7300 |
| P75 | Secondary | 0.258 | 0.196 | [-0.166, 0.603] | 0.1825 | 0.7300 |
| IQR | Secondary | 0.177 | 0.152 | [-0.150, 0.444] | 0.2415 | 0.7300 |

The point estimates are positive at all three quantiles, and the treatment IQR is wider by 0.177 standard deviations. Every interval includes zero. The primary lower-tail contrast is 0.081 SD, with centered bootstrap p = .310. The evidence does not establish any fixed distributional effect at the 5-percent level. The observed pattern can motivate hypotheses about uneven learning gains.

## Relation to the original paper and replication

The extension should begin with a compact replication of the original study's design and its mean learning outcomes. The original intervention is a bundled reduced-form treatment: cameras and attendance-linked pay arrive together. The distributional analysis preserves the original outcome construction and uses no external data, additional testing, or newly collected observations. The replication record should state the exact raw files, source cleaning rules, post-test observation rule, and software used, then place the quantile results after the replication section.

A mean effect and a quantile contrast answer different questions. Uncertain quantile contrasts do not invalidate the original mean result. The fixed P25/P50/P75/IQR family and school-resampling rule make this additional question auditable.

## Attrition, repeated records, and inference limits

The distribution sample uses observed baseline achievement, observed baseline writing status, and an observed reconstructed post-test total. It does not impute a missing learning outcome. The metadata records 3,399 post-test rows before the locked filter and 1,737 analysis rows after it. Because the filter does not require a teacher score, this sample is not interchangeable with the Direction 0.2 score-complete sample. In particular, the 1,625-row observed-only interaction sample used in the teacher-score route is a different estimand and should not be substituted here.

The analysis contains 1,737 rows but 1,720 unique school-child keys. The source package includes repeated keys and tied scores; the locked analysis retains them for source alignment. The resulting contrast is an empirical distribution of source observation rows, not a claim about 1,737 distinct children. School assignment is the randomization level, and the bootstrap respects that level by resampling schools within treatment arm. The relatively small number of schools in each arm also contributes to the wide intervals.

The outcome-observation rule can still create selection. The current distribution run does not estimate or impute a missing-outcome model, and it cannot prove that the observed-test distribution represents the distribution that would have been measured for all eligible children. The separate teacher-score attrition audit shows why this concern should be stated plainly: in a related score-complete cohort, 1,625 of 2,104 rows had observed follow-up, and a fixed observation model could not establish that selection was absent. Those numbers describe the score-complete audit, not a new distributional attrition estimate; they should be used only as context for the general measurement limitation.

The family was newly screened and fixed before the bootstrap calculation, but the overall project has a history of considering candidate extensions. The four-contrast Holm correction is therefore necessary but not sufficient to turn the analysis into confirmatory evidence. No additional quantiles, outcomes, cut points, subgroup screens, or alternate bootstrap choices should be added to seek a smaller p-value. Bootstrap p-values are approximate descriptive quantities here; the percentile intervals are the principal uncertainty display.

## Feasible execution plan

The quantitative extension is already complete. The feasible remaining work is to make it readable and reproducible. The paper should include one main table with the four locked contrasts and one figure showing the arm-specific quantiles or the four treatment-control differences with percentile intervals. The figure should label the outcome as normalized post-test total learning and identify school-pair bootstrap inference. An appendix can show the exact sample map, quantile interpolation rule, seed, number of repetitions, and the source-row versus unique-key counts. The existing distribution script and metadata contain the necessary hashes and command for a replication package.

The replication section should carry 20–30 percent of the paper, with the distributional extension taking 60–70 percent. The main text needs only the original experiment, the mean replication anchor, the estimand, the principal P25 result, and the four-contrast table. Detailed bootstrap diagnostics and the related attrition audit belong in the appendix. There is no need for a new structural model, teacher-score restriction, or alternative outcome.

## Suggested complete paper outline

1. **Abstract, under 150 words.** State the original mean-learning question, the distributional extension, the 1,737-row observed-test sample, and the result that all fixed contrasts have intervals containing zero.
2. **Introduction, 1–2 pages.** Explain why lower-tail and dispersion effects matter for interpreting an average learning gain. State the P25 estimand, the bounded novelty claim, the main estimate, and the paper roadmap. Weave related work into this motivation rather than adding a standalone literature review.
3. **Original study and replication, 2–3 pages.** Describe the rural Rajasthan experiment, bundled treatment, student tests, source reconstruction, and the match to the original mean learning analysis. Define the analysis unit and observed-test restriction.
4. **Distributional design, 1–2 pages.** Define empirical quantiles, P25 as primary, P50/P75/IQR as secondary, school-pair bootstrap inference, and the absence of a rank-preservation claim.
5. **Results, 3–4 pages.** Present the arm-specific quantile table, the four contrasts, and one coefficient or quantile figure. Explain why positive point estimates do not establish a distributional effect when the intervals are wide and Holm-adjusted p-values are 0.7300.
6. **Measurement and interpretation, 1 page.** Discuss observed-outcome selection, repeated keys, source rows, school-level inference, and the limited bounded novelty claim.
7. **Discussion and conclusion, about 1 page.** State that the data do not resolve whether the program affects any fixed part of the observed learning distribution, while identifying the point pattern as a useful descriptive lead for future work. Put reproducibility details and extra diagnostics in an appendix.

## Defensible conclusion and ranking

The defensible main conclusion is: **the treatment-group distribution has higher observed P25, median, and P75 point estimates and a wider observed IQR than the control distribution, but the fixed school-bootstrap intervals include zero for every contrast, so the data do not establish a distributional learning effect.** The paper can argue that a distributional lens is substantively useful and genuinely distinct from the original mean analysis. It cannot claim that the program benefited the lower tail, increased inequality, or produced a structural quantile treatment effect.

Execution effort is **medium** because the sample, bootstrap, and scope audit already exist. This route ranks **second overall**: it offers a clear new question, while departure has more resolved evidence. Keep it as a separate possible paper route and report its inconclusive result.
