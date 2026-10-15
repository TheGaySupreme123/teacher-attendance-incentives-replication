# Evidence review: baseline writing × recorded NFE departure

Audit date: 2026-10-07. This is a read-only evidence sheet for the reference
paper. It does not change raw data or analysis outputs.

## Estimand and source construction

The treatment is assignment to the bundled camera-monitoring and attendance-pay
program. The main estimand is the coefficient on `treat × pre_writ` in a child-
level OLS regression of the original Table 10 `drop` indicator, with school-
clustered standard errors. `pre_writ` is the binary baseline written-test
status; it is an observed pre-treatment characteristic, not a randomized
moderator or a continuous literacy measure.

The `drop` indicator is one when the child has zero recorded attendance over
the last **up to five observed random checks for which the school was open**.
It includes both children with a recorded government-school marker and the
residual `drop2` category. It is therefore best named “recorded/operational
NFE departure under the original last-open-check rule,” not verified school
departure or educational dropout.

The reconstruction follows `Programs/Table7_Table10.do:15-176` and matches all
2,197 child-level `drop` and `gov` values in `Raw-Data/RandomCheck/Roster/Temp/drop.dta`.
The analysis excludes two Table 10 children with conflicting duplicated
`pre_writ` rows, leaving 2,195 children in 111 outcome schools (57 treatment,
54 control), with cluster degrees of freedom 110.

## Numeric evidence sheet

### Aggregate replication anchor

| Table 10 outcome | Control mean | Treatment mean | Difference | Clustered SE | N | Published rounded result |
|---|---:|---:|---:|---:|---:|---:|
| `drop` / child left NFE | 0.3591 | 0.4428 | +0.0837 | 0.0411 | 2,197 | +0.08 [0.04] |
| `gov` / recorded government-school marker | 0.1574 | 0.2588 | +0.1014 | 0.0349 | 2,197 | +0.10 [0.03] |
| `drop2` / `drop` without recorded marker | 0.2017 | 0.1840 | −0.0177 | 0.0306 | 2,197 | −0.02 [0.03] |

The source-coded full sample has 884 `drop`, 461 `gov`, and 423 `drop2`
children. The raw reconstruction matches the shipped child outcomes and the
published rounded Table 10 estimates.

### Primary interaction family

| Outcome | Writer-minus-nonwriter interaction | Clustered SE | 95% CI | Raw p | Holm p |
|---|---:|---:|---:|---:|---:|
| `drop` (primary) | +0.210993 | 0.071787 | [+0.0687, +0.3533] | 0.004011 | 0.012033 |
| `gov` | +0.048398 | 0.077651 | [−0.1055, +0.2023] | 0.534396 | 0.534396 |
| `drop2` | +0.162596 | 0.058949 | [+0.0458, +0.2794] | 0.006807 | 0.013615 |

The Holm correction is only across these three Table 10 outcome interactions.
It does not convert a post-inspection scope choice into a confirmatory test.

For the primary `drop` outcome, control/treatment rates are 33.8%/38.8% for
nonwriters (858/940 children) and 44.3%/70.4% for writers (201/196). The
conditional treatment effects are +0.0503 (95% CI [−0.0236,+0.1242]) and
+0.2613 (95% CI [+0.0999,+0.4227]); their directly tested difference is the
+0.211 interaction. Do not compare the two subgroup p-values instead.

Checks:

- Same-sample school-block fixed effects: +0.2210, SE 0.0699, 95% CI [+0.0824,+0.3596], p=.00203.
- Fixed endpoint through 2005-12-31: +0.1969, SE 0.0751, 95% CI [+0.0480,+0.3458], p=.01002. This is a measurement-driven endpoint check, not a preregistered window search; December coding remains affected.
- Null-imposed school-level Rademacher wild-bootstrap-t for `drop`: p=.0072 (71/9,999 extreme draws; Monte Carlo SE .00085; seed 20260922). The first five vectorized draws match direct refits.
- The analogous `drop2` bootstrap p=.0099. It remains secondary because `drop2` depends on the imperfect `reason` marker.

## Coverage and coding limits

The treatment changes school opening, and the source code drops closed-school
rows before selecting the last five. In the consensus sample, 145/2,195
children have fewer than five open checks: 81 control nonwriters, 21 control
writers, 43 treated nonwriters, and 0 treated writers. Mean all-open-check
counts are 15.40 versus 20.42 for nonwriters (control versus treatment) and
15.21 versus 21.93 for writers; the shares with at least five are 90.6%/95.4%
and 89.6%/100.0%, respectively. This is treatment-dependent observation
coverage, so the interaction can reflect the measurement rule as well as
actual NFE exit.

Treating the 145 incomplete histories as unknown gives an observed-sample
algebraic interaction range of [+0.1191,+0.3638]. These are partial-
identification bounds with no standard errors or p-values. They are not
confidence intervals and do not solve calendar-dependent follow-up or
selection.

The raw attendance audit finds 324 negative-sentinel rows and 2 code-22 rows
among the 10,713 selected rows in the full 2,197-child sample. The source code
maps them to absence, but the package has no value-label codebook. Among the
2,195 consensus children, 113 source-coded departures depend on at least one
such undocumented code (28 control nonwriters, 11 control writers, 71 treated
nonwriters, 3 treated writers). Twenty-one all-sentinel cases are concentrated
in short-history control school 2491. Treating the 113 classifications as
unknown gives [+0.1631,+0.3413]; treating them plus all incomplete histories
as unknown gives [+0.0885,+0.4563]. These are arithmetic observed-sample
bounds, not inferential robustness intervals.

Excluding the 113 ambiguous departure classifications while retaining known
presence cases yields +0.2663, SE 0.0737, 95% CI [+0.1203,+0.4123], p=.000456,
N=2,082 and 111 schools; its wild-bootstrap p=.0011. This is a selection
sensitivity, not a replacement estimand or evidence that the sentinel codes
are missing at random.

The `reason` field is string in `roster_rema2012.dta` but numeric in
`rosterfin.dta`; the distributed Stata append leaves the latter values blank in
`Temp/Roster_CODED.dta`. Mapping only numeric raw `2` to string `"2"` changes
13 destination classifications (full sample `gov` 461→474 and `drop2`
423→410) while leaving every `drop` classification unchanged. In the primary
consensus selected rows, 7,112/10,707 reason fields are blank (66.4%). A blank
marker cannot be described as proof that a child did not transfer. Do not call
`drop2` definitive educational dropout.

## Bounded novelty

The original article already reports aggregate Table 10 NFE departure,
government-school movement and residual dropout, and already reports
baseline-writing heterogeneity for child attendance (Table 7) and learning
(Table 9). The exact `treat × pre_writ` interaction on `drop`, `gov` or
`drop2` was not found in the article, the complete eight-page official
appendix, erratum, local programs, logs or shipped outputs. The contribution is
therefore the narrow cross-outcome heterogeneity test, not a new aggregate
departure outcome, a new baseline-writing measure, or a causal effect of
writing ability. This is a bounded local originality finding, not a claim about
all later literature or unpublished work.

## Drafting cautions

Use language such as: “Assignment to the bundled program increased the
probability of being classified as having left the NFE under the original
last-open-check rule more for baseline writers than nonwriters.” Immediately
state that the classification is operational, open-check coverage is
treatment-affected, and the interaction is exploratory after prior inspection.

Avoid “the program caused literacy-based dropout,” “writers progressed to
formal school,” “nonwriters did not respond,” or “drop2 is educational
dropout.” The primary result is not a mediation result and cannot distinguish
successful progression from an unfavorable exit. Keep `gov` and `drop2` as
secondary decomposition outcomes with the reason-code caveat.

## Audit issue to correct in prose/output

`outputs/scope_search_2026_09_22/transition/transition_scope_measurement_summary.csv`
reports `pre_writ_conflicting_ids_in_analysis=0` because the code compares the
conflict list to the already-filtered `primary` frame. The independent audit
shows three conflicting IDs in `pre_writ_attend.dta`, two of them in the
2,197-child Table 10 sample; those two are precisely the exclusions that
produce N=2,195. The field is tautologically zero after exclusion and should
not be used to imply that no conflicts affected the starting sample.

Relevant artifacts: `outputs/scope_search_2026_09_22/SCOPE_DECISION.md`,
`outputs/scope_search_2026_09_22/measurement_audit.md`,
`outputs/scope_search_2026_09_22/transition/transition_scope_model_results.csv`,
`outputs/scope_search_2026_09_22/transition/transition_scope_group_effects.csv`,
`outputs/scope_search_2026_09_22/transition/transition_incomplete_last5_bounds.csv`,
`outputs/scope_search_2026_09_22/measurement/sentinel_interaction_bounds.json`,
`outputs/research_direction_audit/original_overlap_audit.md`, and
`data/Incentives_FINAL/Programs/Table7_Table10.do`.
