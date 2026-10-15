# Alternative route 02: Learning heterogeneity by baseline teacher score

**Status.** This is an alternative research memo for a possible seminar paper. It is not the selected NFE-departure paper and it is not a completed new full paper. It records a feasible paper route using the existing replication data and the already-run fixed analysis family. It should be treated as exploratory evidence.

## Question and motivation

The paper could ask: **Does the bundled camera-monitoring and attendance-pay program change student learning differently in schools with different baseline teacher-test scores, and is the pattern different for mathematics and language?** The treatment is the randomized package offered in the original experiment: camera monitoring combined with attendance-linked pay. The score is a pre-treatment school-level teacher-test measure. The question is therefore about heterogeneous reduced-form treatment effects by an observed baseline characteristic. It is not a causal estimate of teacher ability, and it cannot separate the camera component from the incentive component.

The motivation comes from a gap between the original paper's outcomes. Duflo, Hanna, and Ryan report treatment effects for mathematics, language, and total learning, and they discuss heterogeneity in attendance and other baseline characteristics. The original paper does not, under the bounded audit of the article, official appendix, erratum, source programs, logs, and shipped outputs, estimate a treatment-by-teacher-score interaction separately for each learning domain. It also does not report a joint math/language interaction test or a formal difference between the two domain-specific moderation coefficients. The bounded novelty claim is therefore specific: these interaction and composition estimates are absent from the audited original materials. It is not a claim of originality against the wider literature.

This route would make a narrower contribution than the selected NFE-departure route. It asks whether the same attendance intervention has a different learning association in different subjects, while keeping the intervention, data source, and outcome construction close to the original study. The advantage is conceptual continuity with the paper's learning results. The cost is that the evidence is currently inconclusive once the fixed outcome family and the data-quality limits are reported honestly.

## Data and estimand

The fixed observed-test sample has 1,625 source observation rows, 1,610 unique school-child keys, and 101 schools. It excludes the 21 rows that would receive a post-test total only through the source program's later zero fill. There are 835 control observations in 52 schools and 790 treatment observations in 49 schools. The teacher-score reference contains 107 score-observed schools; its mean is 34.2617 points and its standard deviation is 10.4632 points. The standardized moderator is therefore

\[
 Z_s=(\text{teacher score}_s-34.2617)/10.4632.
\]

For each learning domain, the proposed equation is

\[
 Y_{isd}^{post}=\alpha_d+\beta_d T_s+\gamma_d Z_s+\delta_d(T_s\times Z_s)+\theta_d'X_{is}+\varepsilon_{isd},
\]

In this model, treatment is assignment to the bundled program. The baseline control vector contains the original baseline verbal total, baseline written total, and baseline writing-status indicator, and standard errors are clustered by school. The domain interaction is the difference in the program's learning effect associated with a one-standard-deviation increase in baseline teacher score. Because teacher score is not randomized, it is an effect-heterogeneity description conditional on the measured score, not a causal teacher-quality effect. The outcome variables are the existing normalized post-test mathematics, language, and total scores; no new test outcomes are constructed.

The family was fixed before estimating the three domain interactions. It contains exactly the three outcomes, with total learning retained as the aggregate benchmark. The planned reporting rule is to show all three coefficients, their school-clustered uncertainty, and Holm-adjusted p-values within this three-outcome family. A corresponding geographic-block specification is a pre-defined sensitivity, not a new search. Blocks are included as indicators for blocks 2 through 5, with block 1 as the base; they are not relabeled as randomized strata.

## Current results

The main observed-only estimates are:

| Outcome | Teacher-score interaction | Clustered SE | 95% CI | Raw p | Holm p (3 outcomes) |
|---|---:|---:|---:|---:|---:|
| Mathematics | 0.209 | 0.099 | [0.013, 0.405] | 0.0367 | 0.1102 |
| Language | 0.085 | 0.072 | [-0.057, 0.227] | 0.2388 | 0.2388 |
| Total | 0.132 | 0.071 | [-0.009, 0.273] | 0.0666 | 0.1332 |

The estimates are in standard deviations of student learning per one standard deviation of teacher score. The mathematics point estimate is the largest and its unadjusted interval excludes zero, but the Holm-adjusted p-value is 0.1102. The total interaction is the previously examined Direction 0.2 result in the observed-only sample: 0.1321, with p=0.0666 and a 95% interval from -0.0092 to 0.2735. It should not be counted as a second independent discovery. The language estimate is smaller and imprecise.

The direct composition calculations give a math-minus-language interaction difference of 0.124, with clustered SE 0.064, 95% CI [-0.002, 0.251], and p=0.0537. The joint Wald test of the two interaction coefficients is F(2,100)=2.472, p=0.0896; the corresponding chi-square(2) p-value is 0.0844. These tests do not support a fixed-5-percent claim that the intervention's moderation is different across math and language. They do provide a transparent way to discuss the pattern without selecting mathematics merely because its raw p-value is the smallest.

The geographic-block sensitivity weakens every interaction:

| Outcome | Interaction | Clustered SE | 95% CI | Raw p | Holm p (3 outcomes) |
|---|---:|---:|---:|---:|---:|
| Mathematics | 0.136 | 0.095 | [-0.053, 0.325] | 0.1577 | 0.4732 |
| Language | 0.059 | 0.061 | [-0.063, 0.181] | 0.3426 | 0.4732 |
| Total | 0.087 | 0.065 | [-0.042, 0.217] | 0.1852 | 0.4732 |

The block-adjusted joint math/language test is F(2,100)=1.023, p=0.3631. The adjusted math-minus-language difference is 0.077, SE 0.065, 95% CI [-0.052, 0.206], p=0.2383. The movement in the point estimates is a reason to describe the composition result as specification-sensitive exploratory evidence.

## Significance, attrition, and measurement limits

The three-outcome family was fixed after earlier inspection, not preregistered. The raw mathematics p-value is therefore descriptive even before accounting for the Holm correction. The correction is applied to the stated three-outcome family; it does not erase the broader history of considering alternative extensions. No additional score cutoffs, subject-specific outcomes, school exclusions, or one-sided tests should be added to make the result look more decisive.

The observed-test restriction matters. The score-complete baseline cohort has 2,104 rows in 107 schools, of which 1,625 have an observed reconstructed post-test outcome and 479 do not. The observed rate is 77.2 percent. A fixed baseline observation model estimates the treatment-by-score coefficient for outcome observation as -0.031, clustered SE 0.046, 95% CI [-0.122, 0.060], p=0.495. This does not prove that attrition is harmless. A stabilized inverse-probability-weighting sensitivity gives an interaction of 0.135; its conditional clustered p-value is 0.0527, while the whole-school bootstrap 95% percentile interval is [-0.0033, 0.2791]. The interval includes zero and depends on missing-at-random conditional on measured baseline variables and positivity. It does not recover missing outcomes.

There are 15 repeated school-child keys in the retained source records, represented by 30 rows in the fixed post-test audit. The source rows are kept for replication alignment; they should not be described as 1,625 independently observed children. Six schools have no observed follow-up outcome in the score-complete audit, and 141 baseline rows across six schools lack a teacher score and are outside this estimand. Original item scoring, missing-modality coding, and normalization are retained. These choices support reproducibility but do not make every test record complete or make teacher score an exogenous measure of ability.

## Feasible execution plan

The analysis is already complete enough to support a draft, so the remaining work is paper construction and transparent presentation rather than a new significance search. First, rerun the audited original learning tables and state exactly which published Table 9 A/B checks match the shipped reference. The replication record reports that all 16 Table 9 A/B checks match at reported precision, with the known small R-squared differences. Second, present the domain interaction equation and a coefficient plot with the three primary estimates and 95% intervals. Third, report the math/language joint test and direct contrast in a compact table, with the block specification in the appendix. Fourth, write the attrition and multiplicity limits next to the result instead of treating them as afterthoughts. The existing scripts and hashes provide a reproducibility path; no raw data modification is required.

An optional subapproach is to make domain composition the organizing question: **does the program's teacher-score moderation differ between mathematics and language?** In that version, the math-minus-language contrast (0.124, p=0.0537) and the joint test (p=0.0896) would be the central extension, while total learning would be the aggregate benchmark. This gives the paper a clean estimand, but the current confidence interval crosses zero and the geographic sensitivity is weaker. It should remain optional or secondary rather than replace the full three-outcome table.

## Suggested complete paper outline

1. **Abstract, under 150 words.** State the original attendance-and-learning experiment, the replication, the teacher-score/domain question, and the fact that the point estimates are positive but not robust to the fixed family correction.
2. **Introduction, 1–2 pages.** Explain why an average learning effect may conceal differences by baseline teacher capacity and subject. State the observed-only estimates and the bounded novelty claim. End with the paper roadmap; do not create a separate literature-review section.
3. **Original study, data, and replication, 2–3 pages.** Describe the randomized bundled intervention, student tests, teacher score, source reconstruction, and the audited match to the original learning tables. Define the analysis sample and the observed-outcome restriction.
4. **Extension design, about 1–2 pages.** Give the interaction equation, standardization rule, school-clustered inference, fixed three-outcome family, Holm adjustment, and optional math-minus-language estimand.
5. **Results, 3–4 pages.** Lead with the three interaction estimates, then the direct composition and joint tests. Use the geographic-block table and attrition/IPW interval as robustness material. Keep all three outcomes visible.
6. **Discussion and conclusion, about 1 page.** State what the estimates can and cannot establish, with teacher score treated as an observed moderator rather than a causal mechanism. Put detailed coefficients, input hashes, and code instructions in an appendix.

## Defensible conclusion and ranking

The defensible conclusion is: **the data are consistent with a larger teacher-score moderation pattern for mathematics than for language, but the evidence is exploratory and not statistically resolved after the fixed three-outcome correction or the geographic-block sensitivity.** The total-learning interaction remains positive but crosses zero at 95 percent. The paper should not claim that high-score teachers cause stronger learning gains, that the program works through a subject-specific mechanism, or that mathematics alone is a confirmed finding.

Execution effort is **medium-high**: the estimates and code are available, but the paper needs careful replication, multiplicity, attrition, and measurement exposition. As a paper choice, this route ranks **third overall** behind the selected NFE-departure route and the learning-distribution route. It is a useful reference draft and a credible fallback if the seminar values continuity with the original learning outcomes, but it is less attractive as the main paper because its strongest nominal result does not survive the fixed family correction.
