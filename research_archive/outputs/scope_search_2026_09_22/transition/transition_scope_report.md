# Transition scope and significance audit

## Scope and prior exploration

The fixed primary family for this audit is the treatment x baseline-writing interaction for the three existing Table 10 child outcomes: `drop` (realized departure from the NFE at the last open checks), `gov` (an observed government-school transition marker), and `drop2` (departure without that observed transfer marker). The family was chosen for this audit after prior exploratory work and is not preregistered or independent confirmation. Holm adjustment is applied across these three primary interaction p-values. Broader prior exploration means even the adjusted values remain exploratory evidence.

The primary data rule is the existing raw reconstruction in `scripts/audit_transition_extension.py`, with the two conflicting eligible baseline-writing IDs excluded. It leaves 2195 children in 111 schools. No reason field, transition indicator, or dropout indicator is imputed.

## Primary family

| Outcome | Interaction | Clustered SE | t | Raw p | Holm p | 95% CI |
|---|---:|---:|---:|---:|---:|---:|
| drop | 0.211 | 0.072 | 2.94 | 0.0040 | 0.0120 | [0.069, 0.353] |
| gov | 0.048 | 0.078 | 0.62 | 0.5344 | 0.5344 | [-0.105, 0.202] |
| drop2 | 0.163 | 0.059 | 2.76 | 0.0068 | 0.0136 | [0.046, 0.279] |

The drop2 lead remains below .05 after Holm adjustment across the fixed three-outcome family (0.0136), but this is an exploratory family result, not a clean confirmatory claim. It should be read as higher realized NFE departure without an observed government-school reason marker, not as a definitive educational-dropout or school-exit mechanism.

The cleaner primary `drop` outcome has a fixed-group treatment effect of 0.050 (SE 0.037, 95% CI [-0.024, 0.124]) for baseline nonwriters and 0.261 (SE 0.081, 95% CI [0.100, 0.423]) for baseline writers. The group counts are 858 control/940 treated nonwriters and 201 control/196 treated writers. These effects describe realized departure from the NFE under the Table 10 operational definition.

## Wild-bootstrap inference for the two positive primary leads

The primary `drop` interaction is 0.211 (clustered SE 0.072, classical p 0.0040); its null-imposed school-level Rademacher wild bootstrap-t gives p=0.0072 (Monte Carlo SE 0.0008). The primary `drop2` interaction is 0.163 (clustered SE 0.059, classical p 0.0068); its wild-bootstrap p is 0.0099 (Monte Carlo SE 0.0010). Both use 9999 draws with seed 20260922; treatment and baseline-writing main effects remain unrestricted under the null. The first five vectorized draws match independent refits for both outcomes: True and True.

## Fixed-effect and endpoint checks

Adding the existing school block field as geography/block fixed effects on the same consensus sample gives a `drop` interaction of 0.221 (SE 0.070, p=0.0020; 95% CI [0.082, 0.360]) and a `drop2` interaction of 0.178 (SE 0.058, p=0.0028; 95% CI [0.063, 0.294]). This check does not add a new outcome or change the child sample.

The raw source has a structural measurement issue: `reason` is string in `roster_rema2012.dta` but numeric in `rosterfin.dta`; the distributed Stata append leaves the latter values blank in the coded roster. Across the primary selected rows, 66.4% of reason fields are blank (7112 of 10707); blanks are 69.9% in control and 63.3% in treatment. No blanks are filled.

As a fixed calendar-endpoint measurement sensitivity motivated by blank reason fields in the final Jan–Feb 2006 rosterfin rows, the same last-five-open-check rule is recomputed using observed roster dates through 2005-12-31. The `drop` interaction is 0.197 (SE 0.075, p=0.0100; 95% CI [0.048, 0.346]) and the `drop2` interaction is 0.151 (SE 0.059, p=0.0123; 95% CI [0.033, 0.268]). This is not a p-selected window: the calendar date is fixed before looking at the estimates. It still uses blank reason fields as blank and does not impute outcomes. Both leads are smaller but remain positive; the endpoint check therefore does not show that the result is solely created by the final Jan–Feb 2006 records.

## Coverage and interpretation

Treatment changes observation opportunities: children in treatment schools have more open-school checks, so the last-five-open-check rule is post-treatment. The coverage CSVs report child counts, all-open-check counts, selected row counts, blank reason shares, and reason-2 counts by treatment and baseline-writing status and by period. The outcome remains an operational Table 10 classification rather than a directly observed transition process independent of treatment-generated open checks. In particular, `drop2` is not independently observed educational dropout: it is no attendance in the selected open checks without a recorded `reason == "2"` marker.

Coverage differs across both treatment and baseline-writing groups: mean all-open-check counts are 15.40 for control nonwriters versus 20.42 for treated nonwriters, and 15.21 for control writers versus 21.93 for treated writers. In the selected last-five rows, blank-reason shares are 72.2%, 68.4%, 59.9%, and 39.2%, respectively. The period-by-group CSV makes the temporal pattern inspectable without changing the window after seeing estimates.

The primary `drop` classification also has incomplete five-check coverage. In the consensus sample, 145 of 2195 children have fewer than five observed open checks. Treating every such child's binary `drop` outcome as unknown, without imputing or selecting a sample, gives algebraic cell bounds and a writer-minus-nonwriter treatment-effect-difference bound of [0.119, 0.364]. The lower bound remains positive, but this is a partial-identification interval with no standard error or p-value; it does not remove the post-treatment coverage concern.

## Decision

The drop2 x baseline-writing lead survives the fixed three-outcome Holm adjustment, same-sample block fixed effects, and a source-motivated calendar-endpoint check, and the primary wild-bootstrap result should be reported alongside the classical inference. The cleaner `drop` interaction is the stronger substantive anchor because it does not require a `reason` code, and its incomplete-check worst-case bound remains positive. This is a plausible, genuinely new substantive direction under the existing-number constraint. The evidence remains exploratory and measurement-limited: reason coverage is incomplete, open-check coverage is treatment-affected, and the family was selected after prior exploration. The paper should state the lead as evidence consistent with a difference in realized NFE departure without an observed government-school marker among baseline writers, not as definitive educational-dropout avoidance, a causal mechanism, or a confirmatory discovery.

Re-run with:

```bash
python3 scripts/audit_transition_scope.py
```
