# Measurement audit: baseline writing × NFE departure

Audit date: 2026-09-22. This is a read-only measurement audit. I did not run a
hypothesis regression, search alternative windows, or modify the shipped data
or existing research outputs. Counts below come from the raw Stata files under
`data/Incentives_FINAL/Raw-Data/RandomCheck/Roster/`, following
`Programs/Table7_Table10.do`.

## What the original endpoint means

The original program loads `roster_rema2012` and drops December 2005 before
the append (lines 15-17), but it does not drop December 2005 from the using
file `rosterfin`. It retains random-check records and enrolled children at
lines 70-115. For the Table 10 outcome it then keeps `open==1`, orders each
child's records from newest to oldest, and keeps `last<5` (lines 151-159).
It collapses attendance and the government-school marker by child (lines
160-164), defines `drop = 1` when the five-check attendance sum is zero (lines
168-169), and defines `gov` only within `drop` (lines 171-172). Thus `drop` is
the operational **NFE departure** measure: it includes both observed movement
to government school and the residual `drop2` outcome. It is not, by itself, a
measure of educational dropout.

The paper's Table 10 reports only aggregate outcomes: “Child left NFE,”
“Child enrolled in government school,” and “Child dropped out of school.” The
main-paper extraction places the discussion at `tmp/pdfs/original_paper.txt`
lines 2137-2149 and the table at lines 2163-2185 (PDF page 35; journal pages
1273-1274). The paper says that NFE children may enter government schools and
then separately describes children who left the NFE without doing so. It does
not cross these outcomes with baseline writing. Baseline writing is discussed
for attendance and learning at lines 1818-1820 and 2128-2136, but no
`pre_writ × drop` or `pre_writ × NFE departure` result appears there.

The source program uses `pre_writ` for attendance among children already
classified as non-dropouts (`Table7_Table10.do`, lines 185-255); the final
Table 10 regressions at lines 268-296 are aggregate `drop`, `gov`, and `drop2`
regressions only. The eight-page official appendix was read in full from
`tmp/novelty_audit/duflo_appendix.pdf` / `duflo_appendix.txt`; it contains the
AR(1) teacher-work model and its tables, with no transition or baseline-writing
interaction. Official sources: [article](https://www.aeaweb.org/articles?id=10.1257/aer.102.4.1241)
and [supplemental appendix](https://www.aeaweb.org/articles/materials/1573)
(redirecting to the AEA asset PDF).

This supports a bounded novelty claim for a `treat × pre_writ` interaction on
the original total-departure variable: the endpoint itself is in the original
paper, but this baseline-writing moderation is absent from the paper,
appendix, and source Table 10 program. It must be described as heterogeneity
in an operational NFE-exit outcome, not as a new aggregate departure measure.

## `reason` type mismatch: exact raw audit

The mismatch is real and affects the government/dropout decomposition. In the
raw files, `roster_rema2012.dta` has a string `reason` and `rosterfin.dta` has
a numeric `reason`. The original Stata log records the append warning at
`data/Incentives_FINAL/Log-Files/Table7_Table10.log` lines 47-48: “reason is
int in using data but will be str80 now.” The resulting shipped
`Temp/Roster_CODED.dta` has 56,185 rows and 3,571 observations with
`reason == "2"`; none of those are in December 2005, January 2006, or
February 2006. This agrees with the source program's 1,738 `tempgov` matches
at log lines 519-522 and with `Temp/drop.dta`.

The following counts were obtained by retaining a source-file marker and a
separate raw numeric reason field while applying the source program's date,
random-check, enrollment, open-school, and last-five rules. “Original” means
the published Stata append behavior (numeric using-file reason becomes missing
in the string master column). “Semantic” means only the mechanically
defensible mapping of raw numeric `2` to string `"2"`; it does not assign
meanings to any other codes.

| Stage | `roster_rema2012` | `rosterfin` | Original reason-2 records | Semantic extra reason-2 records from `rosterfin` |
|---|---:|---:|---:|---:|
| Raw files | 130,318 rows; 6,721 string `2` | 5,873 rows; 670 numeric `2` | — | 670 (`286` Dec 2005, `214` Jan 2006, `170` Feb 2006) |
| After source date filters, before random-check/enrollment restrictions | 126,680 rows; 6,690 string `2` | 5,873 rows; 670 numeric `2` | 6,690 | +670 |
| `randomcheck` retained, August 2003 removed | 121,565 roster rows | 5,831 roster rows (plus 110 using-only random-check rows later removed for missing `childno`) | 6,570 | +670 |
| Enrolled coded roster (`Temp/Roster_CODED`-equivalent) | 53,774 rows; 3,571 string `2` | 2,411 rows; 362 numeric `2` | 3,571 | +362 (`157` Dec 2005, `108` Jan 2006, `97` Feb 2006) |
| Open rows, then each child's latest five open rows | 10,713 selected rows; 1,738 string `2` | all 362 numeric-2 rows are selected | 1,738 | +362, for 2,100 semantic reason-2 selected rows |

The final source-program child sample has 2,197 children (1,061 control,
1,136 treatment), matching `Temp/drop.dta` and the existing raw audit. The
published/replication-preserving classification is `drop=884`, `gov=461`,
and `drop2=423`. Mechanically mapping only `rosterfin.reason == 2` to
`"2"`, while changing no attendance or sample rule, leaves `drop` at 884 but
changes the decomposition to `gov=474` and `drop2=410`: 13 child records move
from `drop2` to `gov` (5 control and 8 treatment). These are measurement
comparison counts, not a new regression result.

The current reconstruction in
`scripts/audit_transition_extension.py` lines 101-110 deliberately sets the
using-file `reason` to blank to reproduce the distributed Stata artifact. That
choice is correct for exact reproduction of the published `Temp/Roster_CODED`
and Table 10. It would be incorrect to describe the numeric reason values as
absent from the raw file: they are present in `rosterfin` and 362 reach the
selected enrolled/open/last-five child roster. Conversely, it would be
incorrect to silently call the semantic mapping the published measure: it is
a corrected raw-data convention and changes 13 child classifications.

The mapping `2 → "2"` is defensible without inventing a label because the
original source program itself defines government transition by
`replace tempgov=1 if reason=="2"` (lines 160-162). No such mapping should be
made for codes `1`, `3`, `4`, `996`, negative sentinels, or malformed strings
unless a data dictionary establishes their meanings. For the proposed total
NFE-departure outcome, this issue is immaterial: `drop` uses only attendance
at lines 164 and 168-169 and is identical under both reason conventions.

The date detail matters: the master-file instruction at line 16 removes 138
December 2005 rows from `roster_rema2012` (including 31 string-`2` rows), but
the later append leaves all 5,873 `rosterfin` rows in place. The 286 numeric
`2` values in `rosterfin` December 2005 and the 384 in January-February 2006
are therefore the affected source waves; after enrollment restrictions, 157,
108, and 97 respectively enter the coded roster and all 362 enter the
selected last-five rows.

## Measurement risk from “last five open checks”

The rule is post-treatment in its observation opportunity. The program drops
closed-school rows before selecting the last five (`Table7_Table10.do`, lines
154-159; the log reports 16,409 closed rows dropped at lines 506-517), while
the paper reports that treatment increased the number of days schools were
open (`original_paper.txt`, lines 1806-1814). Therefore treatment can change
which child observations exist and which five records are selected. This is a
measurement limitation for `drop`, `gov`, and `drop2`, although `drop` avoids
the additional reason-code problem.

The independent raw open-check audit found 147 of 2,197 children (6.7%) with
fewer than five open checks: 104 control and 43 treatment. Their available
open-check counts range from 2 to 4. By baseline writing, the short histories
are 81 control non-writers, 21 control writers, 43 treatment non-writers, and
0 treatment writers. Existing audit counts also show the treatment difference
in observation opportunity:

* `pre_writ=0`: control mean 15.40 open checks and 90.6% with at least five;
  treatment mean 20.42 and 95.4% with at least five.
* `pre_writ=1`: control mean 15.21 and 89.6% with at least five; treatment
  mean 21.93 and 100.0% with at least five.

These figures are consistent with the existing
`outputs/research_direction_audit/transition_open_check_audit.csv`; no
arbitrary window search was used. The original code still includes children
with fewer than five records by keeping every available record under
`last<5`, so the literal “last five” definition is incomplete for these 147
children.

## Amendment: raw attendance sentinel audit

This check follows the exact loader recode in `Table7_Table10.do`, lines
56-59, and the matching log at
`data/Incentives_FINAL/Log-Files/Table7_Table10.log` lines 150-159. In the
10,713 selected open-check rows, the raw attendance values are:

| Raw value/category | Selected rows |
|---|---:|
| `1` | 3,657 |
| `2` | 6,730 |
| `-999` | 133 |
| `-888` | 162 |
| `-777` | 6 |
| `-333` | 23 |
| `22` | 2 |
| `-666`, `-444`, or Stata missing | 0 |

There are no raw `0` values in these selected rows. The source code therefore
uses `1` as the only observed presence value in this window and recodes all
other selected values to zero, with the negative codes and `22` first passing
through the `2` code. The row-level sentinel counts by the treatment and
baseline-writing cells are:

| Cell | Children | Source `drop` children | Negative-sentinel rows | Code-22 rows | `drop` children with any sentinel/22 |
|---|---:|---:|---:|---:|---:|
| Control, `pre_writ=0` | 858 | 290 | 96 | 0 | 28 |
| Control, `pre_writ=1` | 201 | 89 | 32 | 0 | 11 |
| Treatment, `pre_writ=0` | 940 | 365 | 189 | 2 | 71 |
| Treatment, `pre_writ=1` | 196 | 138 | 7 | 0 | 3 |
| Unresolved baseline-writing status | 2 | 2 | 0 | 0 | 0 |

Thus 324 selected rows are negative sentinels and 2 are code `22`; none are
generic Stata missing values. They occur in 269 children, of whom 113 are
classified as `drop=1` by the source recode and 156 have at least one raw `1`
and are not classified as dropouts. Among the 113 affected drop children, 92
also have at least one raw `2` attendance code and 21 have no raw `2` or raw
`1` at all. The latter 21 are all in control school 2491, each has only three
selected open checks, and each of those three records is a negative sentinel
(`-999` twice and `-333` once). They are the clearest “all observations are
ambiguous” cases. The 92 mixed cases have source-coded absence `2` records as
well as at least one undocumented sentinel, so their all-five absence status
also cannot be established without treating the sentinel as absence.

The treatment code's comment says “ATTENDANCE=0 MEANS STUDENT IS NOT PRESENT
THAT DAY,” and it explicitly maps the negative codes and `22` to zero. That is
the published operational convention, but the package provides no variable
value labels or attendance codebook: the raw `.dta` files have an
`attendance` variable label but no value labels, `data/Read-Me.txt` is only a
file-structure guide, and `Incentives_FINAL/Read-Me.pdf` gives no variable
definitions. The article likewise describes child attendance as collected by
roll call during random checks and warns that it is observed only when a school
is open (`tmp/pdfs/original_paper.txt`, lines 1689-1707 and 1802-1803), but it
does not define these negative codes. We therefore must not independently
call the sentinel records absences or unobserved records; exact replication
requires the source recode, while a missing-code interpretation is a
sensitivity assumption.

For a transparent bound on the total-departure measure, retain the 771 drop
children with no sentinel/22 as source-coded departures and treat the 113
sentinel/22 drop children as unresolved. The resulting departure count is
between 771 and 884 before making any assumption about those codes. This is a
measurement bound, not a replacement estimate. It is especially relevant for
the proposed `treat × pre_writ` moderation because the 113 unresolved cases
are distributed across the cells above, and the 21 all-sentinel cases are
concentrated in one control school. The total departure outcome remains
usable as the exact original operational measure, but the paper/report should
state the sentinel recode and this bound rather than describe every `drop=1`
as a directly observed child exit.

For orientation only, the unclustered arm-mean difference is 0.0837 under the
source recode (381/1,061 control versus 503/1,136 treatment). Setting all 113
ambiguous cases to non-departure gives 0.0553; allowing the unresolved cases to
be assigned adversarially gives a descriptive range of 0.0185 to 0.1204. These
are arithmetic sensitivity bounds, not alternative regression estimates.

## Recommended bounded definition

Use the original full-sample `drop` as the comparability outcome, label it
“NFE departure under the original last-five-open-check rule,” and treat the
`treat × pre_writ` result as an effect-modification question. As the one
pre-specified robustness definition, construct a **strict five-check NFE
departure** indicator: retain only children with at least five observed open
checks by the original February 2006 endpoint, take the five latest open
checks, and set the indicator to one only when all five attendance values are
zero. Do not use `reason` in this definition. Report the 147 incomplete
histories and the treatment/baseline-writing imbalance as a limitation or
bound, because the completeness restriction is itself treatment-related.

A fixed-calendar no-assumption alternative is not available from these files:
on a closed-school date there is no child-level attendance/exit observation,
so coding an unobserved child as “did not leave” would impose a
treatment-sensitive missingness assumption. The strict five-check version is
therefore a transparent measurement sensitivity, not a cure for post-treatment
observation selection.

### Action for the transition audit

Prioritize total `drop`/NFE departure for the baseline-writing interaction.
Keep `gov` and `drop2` as decomposition outcomes only, with both the exact
replication-preserving convention and the explicitly labeled semantic
`rosterfin`-reason sensitivity if they are shown. Do not present the
`drop2 × pre_writ` result as the main contribution until the reason convention
and open-check measurement issue are resolved; the total-departure result is
the more defensible candidate under the existing raw data.
