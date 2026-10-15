# Transition audit source and reproducibility evidence

## Raw files used

The reconstruction reads these files directly:

- `data/Incentives_FINAL/Raw-Data/RandomCheck/Roster/roster_rema2012.dta`
- `data/Incentives_FINAL/Raw-Data/RandomCheck/Roster/rosterfin.dta`
- `data/Incentives_FINAL/Raw-Data/RandomCheck/Roster/rc_for_roster.dta`
- `data/Incentives_FINAL/Raw-Data/RandomCheck/Roster/enroll1.dta`
- `data/Incentives_FINAL/Raw-Data/RandomCheck/Roster/pre_writ_attend.dta`

The shipped files `Temp/Roster_CODED.dta` and `Temp/drop.dta` are read only for validation. The estimates are computed from the files above.

## Original program correspondence

`data/Incentives_FINAL/Programs/Table7_Table10.do` is the reference program:

- Lines 15–21: load and append the two roster sources; remove the specified dates.
- Lines 23–59: assign the month index and recode attendance sentinels.
- Lines 70–77: merge the random-check dates and retain random-check observations.
- Lines 84–115: merge enrollment and baseline-writing records and keep enrolled children.
- Lines 154–176: retain open-school checks, select the last five per child, and construct `drop` and `gov`.
- Lines 269–296: estimate aggregate Table 10 `drop`, `gov`, and `drop2` outcomes with school-clustered standard errors.

The script follows these operations. The source program warns that merge keys are not unique. `audit_transition_extension.py` therefore retains one using record for a matched key and using-only records, which reproduces the Stata intermediate row count (127,506) and final coded-roster count (56,185).

One source-file type issue is material: `reason` is a string in `roster_rema2012.dta` but numeric in `rosterfin.dta`. In the distributed Stata output, the numeric values from `rosterfin` appear as blank in `Temp/Roster_CODED.dta`; the script preserves that behavior rather than converting them into literal `"2"` transition codes. This is why the raw reconstruction matches all 2,197 shipped child-level `drop` and `gov` indicators.

## Original-paper overlap check

The local extracted article is `tmp/pdfs/original_paper.txt`, from `/Users/shayb/Downloads/Duflo-IncentivesWorkGetting-2012.pdf`. The article reports aggregate transition and dropout outcomes in Table 10 and reports writing-status heterogeneity separately for child attendance and learning. The exact `pre_writ × gov` or `pre_writ × drop` interaction is absent from the article text/tables. The bounded source audit in `original_overlap_audit.md` also checked the official supplemental appendix, erratum, local programs, logs, and published-style outputs.

## Re-run

From the project root:

```bash
python3 scripts/audit_transition_extension.py
```

The script writes the transition CSVs and `transition_audit.md` under this directory and asserts exact child-level agreement with the shipped Table 10 collapse for `drop` and `gov`.
