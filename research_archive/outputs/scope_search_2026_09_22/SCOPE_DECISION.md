# Recommended revised study scope

22 September 2026. This is a research-choice memo, not a paper draft.

**Recommendation:** use baseline writing status × departure from the original nonformal education center (NFE) as the main extension. Keep government-school transfer and departure without a recorded transfer marker as secondary outcomes. This scope has a substantive question absent from the audited original materials and passes the reported two-sided 5% checks using only the original dataset.

## Precise research question

Does assignment to the camera-monitoring and attendance-pay program increase recorded departure from the original NFE more among children who could take the written baseline test than among those who could not?

Working title: *Attendance Incentives and NFE Departure: Differences by Initial Writing Ability*.

This changes the endpoint from test-score gains to school departure, and the moderator from the teacher's score to the child's initial writing status. The extension remains moderate: one primary binary outcome, one pre-treatment moderator, a school-clustered interaction regression, and a short set of measurement/inference checks. It is not a claim that writing ability itself causes a response.

## Main result

2,195 children in 111 schools, after excluding two IDs with conflicting baseline-writing values. School-clustered standard errors, two-sided t(110) tests.

| Initial preparation | Control departure rate | Treatment departure rate | Program effect | 95% CI for effect |
|---|---:|---:|---:|---|
| Baseline nonwriter | 33.8% | 38.8% | +5.0 percentage points | −2.4 to +12.4 |
| Baseline writer | 44.3% | 70.4% | +26.1 percentage points | +10.0 to +42.3 |
| **Writer-minus-nonwriter difference in effects** | — | — | **+21.1 percentage points** | **+6.9 to +35.3** |

The direct interaction is 0.210993, clustered SE 0.071787, **p=.004011**. The raw group-cell difference independently reproduces that coefficient. Do not substitute a comparison of subgroup significance labels for this directly tested difference.

- **Holm p=.012033**, across the fixed three schooling-outcome interactions.
- **Wild-cluster bootstrap p=.0072**, null imposed only on the interaction, 9,999 school-level Rademacher draws, seed 20260922. Simulation standard error .0008. The first five vectorized draws match direct refits.
- **Geographic controls:** +22.1 points, 95% CI +8.2 to +36.0, p=.002033, same sample. The supplied school block is not asserted to be a randomization stratum.
- **Fixed December 2005 endpoint:** +19.7 points, 95% CI +4.8 to +34.6, p=.010016, same sample. This drops the final January–February 2006 observations; it was motivated by their reason-code problem, not a date search. December reason coding is also affected, so this is not a complete coding repair.

## What this would add to the paper

The original paper's Table 10 reports average NFE departure, government-school movement, and residual dropout (pp. 1273–74). It reports baseline-writing differences separately for attendance and learning in Tables 7 and 9. The exact treatment × baseline-writing interaction on NFE departure was not found in the complete article, official appendix, erratum, or audited source programs/logs. This is a bounded novelty finding, not proof of originality across all later literature.

The substantive contribution is that the average departure effect hides a much larger response among initially prepared children. A departure could be successful progression or a less favorable exit. The result establishes a difference in the original study's recorded departure measure; it does not establish its mechanism or welfare implications.

## Full schooling family

| Outcome interaction, writer minus nonwriter | Difference | 95% CI | Raw p | Holm p |
|---|---:|---|---:|---:|
| NFE departure, primary | +21.1 points | +6.9 to +35.3 | .0040 | .0120 |
| Recorded government-school transfer | +4.8 points | −10.5 to +20.2 | .5344 | .5344 |
| Departure without a recorded transfer marker | +16.3 points | +4.6 to +27.9 | .0068 | .0136 |

These use the original replication-compatible definitions. The secondary residual-departure bootstrap p=.0099. The government-transfer interaction does not establish different rates of progression by baseline preparation. The residual-departure result must not be called definitive educational dropout.

## Measurement limits that belong in the study

The original `drop` rule identifies no attendance at every one of the last **up to five observed checks at which the school was open**. It is an operational NFE-departure/sustained-absence classification, not an independently verified end-of-schooling event. The treatment changes school opening and therefore the observation opportunities and calendar dates used in this rule.

145 of the 2,195 children have fewer than five open checks. Treating all 145 classifications as unknown, without imputing outcomes or selecting a reduced sample, yields algebraic bounds of **+11.9 to +36.4 points** on the interaction. These stay positive in this sample but are **not confidence bounds**, have no p-value, and do not resolve sampling uncertainty or different calendar coverage.

A separate raw-data audit confirmed that numeric government-transfer reason codes in `rosterfin.dta` are lost during the original append to a string field. There are raw transfer-code observations in December 2005–February 2006. Harmonizing numeric `2` to string `"2"` changes 13 destination classifications in the full 2,197-child replication sample, while **every total-departure classification remains unchanged**. This is why total NFE departure is the cleaner main endpoint. Blank destination codes do not prove no transfer. See `measurement_audit.md` for exact counts and source lines.

The attendance-code audit also found 324 selected records with undocumented negative codes, plus two code-22 records; the original program treats these as absence. Of the 884 source-coded departures in the 2,197-child replication sample, 113 depend on at least one such record. Twenty-one cases consist entirely of sentinels and already have fewer than five open checks. The raw package supplies no codebook establishing the negative codes as absence rather than unobserved attendance. These cannot silently be called directly observed absences.

A reproducible child-level audit keeps original outcome labels separate from raw-code flags. Treating all 113 ambiguous departures as unknown gives an algebraic interaction range of **+16.3 to +34.1 points**. Conservatively also treating every incomplete five-check history as unknown gives **+8.8 to +45.6 points** across 230 resolved-ID children. These are observed-sample identification ranges, **not confidence intervals or evidence of 5% significance under every possible coding**. They do not repair calendar-dependent observation or missing-data selection. The fixed exclusion sensitivity below is separately labeled and does not replace the replication-compatible main analysis.

**Fixed attendance-code sensitivity:** exclude all 113 ambiguous departure classifications while retaining known raw-presence nondepartures. The interaction is **+26.6 points**, 95% CI **+12.0 to +41.2**, **p=.000456**, in **2,082 children/111 schools**. The same null-imposed school wild-bootstrap procedure gives **p=.0011** (9,999 draws). Independent raw-code audit implementations agree on all 2,197 child ambiguity flags. This is a selection sensitivity, not proof that missingness is random or a replacement for the original full-sample endpoint.

## Other scopes examined, all retained

The scope comparison was explicitly exploratory. Families were fixed before their new calculations, after prior inspection of the dataset. No new scope was preregistered or independently confirmed.

1. **Teacher-score moderation of learning by subject.** Math: +0.209 SD per teacher-score SD, raw p=.0367; Holm across math/language/total p=.1102; with geographic controls p=.1577. Language p=.2388; total p=.0666. Joint math/language p=.0896; direct math-minus-language p=.0537. Do not select mathematics alone as a robust finding.
2. **Broader post-test learning distribution.** Full observed-test sample: 1,737 records, 1,720 unique school-child keys, 107 schools; no teacher-score restriction. The fixed primary P25 contrast is +.081 SD, 95% school-bootstrap interval −.081 to +.219, approximate centered two-sided p=.3099. Median p=.3692, P75 p=.1825, IQR p=.2415; all intervals include zero and all Holm-four p-values=.7300. No further quantile was searched.
3. **Original total-learning Direction 02.** Observed-test interaction p=.0666, wild-bootstrap p=.0698, geographic-control p=.1852. It remains a worthwhile but inconclusive question.

The three-outcome Holm correction addresses the schooling family only. It does not erase earlier exploratory selection, the other families, or the broader model history. The appropriate claim is a statistically supported **exploratory extension under a stated outcome definition**, not guaranteed replication or definitive causal mechanisms.

## Practical scope

- Replication anchor: original Table 10.
- Main outcome: NFE departure under the original operational rule.
- Main moderator: baseline written-test status.
- Main test: treatment × baseline writing, clustered by school.
- Secondary outcomes: recorded government-school transfer and residual departure, with reason-coding limitations visible.
- Checks: geographic controls, school wild bootstrap, fixed endpoint sensitivity and incomplete-window bounds.
- Main exhibit: the two group treatment effects and their directly tested difference, with confidence intervals.

This can fit a moderate seminar project: it requires no new survey, new external dataset, large structural model, or paper-wide rewrite. The core analysis has been completed; the remaining research task is interpreting the narrow claim and its measurement limitations clearly.

## Reproduce

From `/Users/shayb/Downloads/112523-V1`, using Python with NumPy, pandas and SciPy:

```sh
python3 scripts/audit_transition_scope.py
python3 scripts/audit_sentinel_measurement.py
python3 scripts/audit_transition_sentinels.py
python3 scripts/run_scope_learning_family.py
python3 scripts/run_distribution_quantile_bootstrap.py
```

The transition script uses the raw reconstruction functions in `audit_transition_extension.py`; the learning scripts use the raw reconstruction and observed-test audit from the earlier Direction 02 analysis. Original raw files are unchanged. Full estimates and bootstrap vectors remain under `outputs/scope_search_2026_09_22/`.

Sources: [original article](https://www.aeaweb.org/articles?id=10.1257/aer.102.4.1241), [official appendix](https://www.aeaweb.org/articles/materials/1573), [replication package](https://doi.org/10.3886/E112523V1). Exact overlap checks: `novelty.md` and `measurement_audit.md` in this folder.
