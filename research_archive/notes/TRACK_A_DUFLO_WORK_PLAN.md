# Track A Work Plan: Duflo, Hanna, and Ryan (2012)

## Project Choice

Use Duflo, Hanna, and Ryan (2012), "Incentives Work: Getting Teachers to Come to School," for Track A: Replication + Extension.

Why this is a good Track A paper:

- It is explicitly listed in the seminar instructions as a recommended Track A paper.
- The replication package is already downloaded locally in this folder.
- The headline result is clear: camera monitoring plus attendance-based pay incentives increased teacher attendance by about 21 percentage points.
- The paper also has student-learning outcomes, which gives us a natural extension after reproducing the attendance result.

Current local files:

- Paper PDF: `/Users/shayb/Downloads/Duflo-IncentivesWorkGetting-2012.pdf`
- Seminar instructions PDF: `/Users/shayb/Downloads/Experiments Seminar Paper Instructions 2026.pdf`
- Replication package: `/Users/shayb/Downloads/112523-V1`
- Experimental replication folder: `/Users/shayb/Downloads/112523-V1/data/Incentives_FINAL`
- Structural model folder: `/Users/shayb/Downloads/112523-V1/data/Structural-Programs`

Current external source:

- openICPSR project: https://doi.org/10.3886/E112523V1

## Assignment Requirements From The Seminar Instructions

Track A requires:

1. Get the replication package.
2. Run the replication code and reproduce the main tables/figures.
3. Say whether the replication matched the published paper.
4. Make one sensible extension.
5. Write an 8-12 page paper with:
   - Abstract under 150 words.
   - Introduction, 1-2 pages.
   - Data and method, 1-2 pages.
   - Results, 3-4 pages.
   - Discussion and conclusion, about 1 page.

The proposal defense requires a one-page executive memo and a 5-10 minute explanation of the paper choice, progress, and risks.

## What The Original Paper Does

The experiment studies nonformal education centers in rural Rajasthan, India. Seva Mandir randomly assigned schools to a camera-monitoring and financial-incentive program. In treatment schools, teachers had to document attendance with date-stamped photos at the beginning and end of each school day. Their pay depended on valid attendance days. Control-school teachers continued under flat pay and normal monitoring.

Main findings to use in our paper:

- Teacher attendance increased strongly. Table 2 reports that treatment schools were open 0.79 of the time versus 0.58 in control schools, a treatment-control difference of 0.21.
- The effect persisted across periods: before the mid-test, between mid-test and post-test, and after the formal evaluation period.
- The effect was larger among teachers with below-median baseline test scores, though both high-score and low-score teachers improved.
- Student instruction time increased because schools were open more often.
- Student test scores increased by about 0.17 standard deviations.
- There is no evidence that teachers compensated by teaching less when present.

## Replication Feasibility Check

The local package contains the original Stata code and outputs:

- Main do-file: `data/Incentives_FINAL/MasterDoFile.do`
- Programs: `data/Incentives_FINAL/Programs`
- Published-style outputs: `data/Incentives_FINAL/Output`
- Logs: `data/Incentives_FINAL/Log-Files`
- Raw data: `data/Incentives_FINAL/Raw-Data`

Important practical issue: the original Stata code uses old Windows absolute paths such as `C:\Incentives_Matter_Data\...`, while the local package is on macOS and some filenames are hyphenated. Also, Stata is not available in this shell. Therefore, our practical replication path should be:

1. Treat the original Stata code and logs as the reference implementation.
2. Reproduce the key tables in Python from the `.dta` raw files.
3. Compare our Python outputs against the original CSV/log outputs and the published paper.

I already verified the Table 2 attendance replication in Python in memory. The Python calculation exactly matches the original Stata log for the main attendance result:

| Sample | Treatment effect | Clustered SE | N | Published/Stata output |
|---|---:|---:|---:|---|
| All post-baseline random checks | 0.207121 | 0.029586 | 3,071 | 0.21 [0.03] |
| Until mid-test | 0.196051 | 0.036231 | 882 | 0.20 [0.04] |
| Mid-test to post-test | 0.171577 | 0.039290 | 660 | 0.17 [0.04] |
| After post-test | 0.231001 | 0.040966 | 1,529 | 0.23 [0.04] |

This is strong evidence that we can complete the replication without Stata.

## Recommended Main Replication Target

Replicate Table 2, Panel A, and preferably the teacher-score subgroup rows in Panels B and C.

Reason:

- It is the cleanest headline result.
- It uses one main dataset: `Raw-Data/RandomCheck/Teacher-Attendance/randomcheck.dta`.
- It has a simple regression: `open` on `treat`, with standard errors clustered by school.
- It directly answers the paper's central question: did incentives and monitoring increase attendance?

Secondary replication if time allows:

- Table 9, Panel A: treatment effects on mid-test and post-test scores.
- This is useful because the extension will probably focus on learning outcomes or visualization.

## Recommended Extension

Use extension option 4 from the seminar instructions: make a clearer figure.

Proposed extension:

> Turn the headline attendance table into an honest coefficient plot showing the treatment effect and 95 percent confidence interval for each period: all months, until mid-test, mid-test to post-test, and after post-test. Add teacher-score subgroup effects as a second panel or separate figure.

Why this is the safest and strongest extension:

- It adds original work without requiring a fragile new causal claim.
- It directly follows the seminar menu of accepted extensions.
- It is easy to explain in a proposal defense.
- It makes the paper more readable than the original Table 2.
- It can be done with the replicated estimates we already know how to compute.

Possible upgraded extension, if we want more substance:

> Add a stability check showing whether the 21 percentage-point result changes when we include period fixed effects or block fixed effects.

This would answer: is the attendance effect stable after controlling for time/seasonality or randomization block?

Do not make the main extension "gender heterogeneity" or "baseline skill heterogeneity" unless we add something genuinely new, because the original paper already reports baseline-writing and gender panels for learning outcomes.

## Work Phases

### Phase 1: Clean Reproducible Setup

Goal: make the project runnable from this folder.

Tasks:

- Create a `scripts/` folder.
- Create a Python environment or install required packages.
- Required Python packages:
  - `pandas`
  - `numpy`
  - `matplotlib`
  - `statsmodels` or our own small cluster-robust OLS helper
- Write a script such as `scripts/replicate_table2.py`.
- Script should read the raw Stata data directly from `data/Incentives_FINAL/Raw-Data`.
- Output clean results to `outputs/table2_replication.csv`.
- Output a coefficient plot to `outputs/table2_attendance_effects.png`.

### Phase 2: Replicate The Headline Result

Goal: reproduce Table 2 attendance estimates.

Exact procedure:

- Load `randomcheck.dta`.
- Recreate the `time` variable exactly as in `Programs/Table-2.do`.
- Allocate August 25+ observations to September, as the Stata code does.
- Drop schools `1111`, `1211`, `2493`, `5221`, `5231`, `5332`, and `5711`.
- Drop baseline month `time == 1`.
- Estimate `open = alpha + beta * treat + error`.
- Cluster standard errors by `schid`.
- Repeat for:
  - all post-baseline months
  - `time < 9`
  - `time > 8 & time < 16`
  - `time > 15`
- Merge teacher test scores and repeat for above- and below-median teacher scores.

Deliverable:

- A short replication note saying the main estimate matches: beta = 0.207, SE = 0.030, which rounds to Table 2's 0.21 [0.03].

### Phase 3: Build The Extension Figure

Goal: make one clear, self-contained figure.

Figure design:

- X-axis: period or subgroup.
- Y-axis: treatment effect on school open/teacher attendance.
- Points: estimated treatment effect.
- Error bars: 95 percent confidence intervals using clustered standard errors.
- Horizontal zero line.
- Footnote: "Dependent variable is an indicator for whether the school was open during an unannounced random check. Standard errors clustered by school. Baseline month excluded. Data from Duflo, Hanna, and Ryan (2012) replication package."

Interpretation:

- The treatment effect is positive in every period.
- The result does not disappear after the formal evaluation period.
- The effect is especially large among teachers with below-median baseline test scores, mainly because control attendance was lower for this group.

### Phase 4: Optional Stability Check

Goal: add a small robustness table or figure if time allows.

Candidate checks:

- Add month-period fixed effects.
- Add randomization block fixed effects.
- Drop each block one at a time and see whether the estimate remains positive.
- Use the original Table 2 result as the baseline and report how much the estimate moves.

Keep this small. The extension should stay readable and defensible.

### Phase 5: Draft The One-Page Proposal Memo

Suggested memo structure:

- Paper: Duflo, Hanna, and Ryan (2012), AER.
- Research question: Can monitoring plus financial incentives reduce teacher absenteeism and improve education outcomes?
- Main result to replicate: treatment schools were open about 21 percentage points more often than control schools.
- Data/code: openICPSR replication package, local folder already downloaded.
- Progress: replication package inspected; Table 2 main result reproduced in Python and matches the Stata log.
- Extension: create a coefficient plot of attendance effects over periods and by teacher baseline score; optionally add period/block fixed-effect stability checks.
- Risks:
  - Original code is Stata with old Windows paths; solution is Python reimplementation from raw `.dta` files.
  - Learning-outcome replication is more complex than attendance replication; keep it secondary unless time allows.
  - Extension must not overclaim new causal mechanisms.

### Phase 6: Final Paper Outline

1. Abstract
   - One short paragraph: I replicate the attendance effect and show it visually across periods/subgroups.

2. Introduction
   - State the question immediately.
   - Explain why teacher absenteeism matters.
   - State the replicated result and extension result in the first page.

3. Original Study And Research Design
   - Explain the setting: Seva Mandir NFEs in Rajasthan.
   - Explain random assignment to camera monitoring and attendance incentives.
   - Explain the outcome: whether a school was open during unannounced checks.

4. Replication Method
   - Data source and exact files.
   - Cleaning rules copied from original Stata code.
   - Regression equation.
   - Clustered standard errors by school.

5. Replication Results
   - Table comparing original Table 2 to our replicated numbers.
   - One paragraph saying the replication matches.

6. Extension Results
   - Coefficient plot.
   - Interpretation across periods and teacher-score subgroups.
   - Optional stability-check table.

7. Discussion And Conclusion
   - Restate the main finding.
   - Explain what the extension adds: the effect is visually stable and not driven by one period.
   - Honest weakness: the intervention combines monitoring and pay incentives, so the simple reduced-form result does not separately identify each component.

## Immediate Next Steps

1. Ask the professor to approve Duflo, Hanna, and Ryan (2012) as the Track A paper, noting that it is on the recommended list and the replication package opens locally.
2. Create the Python replication script for Table 2.
3. Save the replicated Table 2 estimates and compare them against `data/Incentives_FINAL/Output/table2.csv`.
4. Generate the extension coefficient plot.
5. Draft the one-page proposal memo for the proposal defense.

